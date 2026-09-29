use std::collections::{BTreeMap, HashMap};

use mh370_domain::{
    great_circle_distance_nm, AircraftState, Degrees, Feet, FeetPerMinute, Hertz, Knots, LatLon,
    Seconds, Vec3,
};
use mh370_particle_filter::FilterSnapshot;
use mh370_satcom::{bfo_components, bto, SatcomModelConfig};
use serde::{Deserialize, Serialize};
use thiserror::Error;

use crate::{KnownFlightInferenceRun, KnownFlightParticle};

const RUN_SCHEMA: &str = "mh370-known-flight-inference-v2";

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct KnownFlightScoringConfig {
    pub schema_version: u32,
    pub name: String,
    pub expected_inference_sha256: String,
    pub expected_truth_sha256: String,
    pub expected_seeds: Vec<u64>,
    pub grid: KnownFlightGrid,
    pub ground_station_position_km: Vec3,
    pub satcom: SatcomModelConfig,
}

impl KnownFlightScoringConfig {
    pub fn validate(&self) -> Result<(), &'static str> {
        if self.schema_version != 2 {
            return Err("unsupported known-flight scoring schema");
        }
        if self.name.trim().is_empty() {
            return Err("known-flight scoring name must not be empty");
        }
        if !is_sha256(&self.expected_inference_sha256) || !is_sha256(&self.expected_truth_sha256) {
            return Err("known-flight expected SHA-256 is invalid");
        }
        if self.expected_seeds.is_empty() {
            return Err("known-flight scoring seed set must not be empty");
        }
        if self
            .expected_seeds
            .iter()
            .enumerate()
            .any(|(index, value)| self.expected_seeds[..index].contains(value))
        {
            return Err("known-flight scoring seeds must be unique");
        }
        self.grid.validate()?;
        if !self.ground_station_position_km.is_finite() {
            return Err("known-flight scorer ground station is invalid");
        }
        self.satcom
            .validate()
            .map_err(|_| "known-flight scorer SATCOM model is invalid")
    }
}

fn is_sha256(value: &str) -> bool {
    value.len() == 64 && value.bytes().all(|byte| byte.is_ascii_hexdigit())
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct KnownFlightGrid {
    pub latitude_min_deg: f64,
    pub latitude_max_deg: f64,
    pub longitude_min_deg: f64,
    pub longitude_max_deg: f64,
    pub cell_size_deg: f64,
}

impl KnownFlightGrid {
    fn validate(&self) -> Result<(), &'static str> {
        if ![
            self.latitude_min_deg,
            self.latitude_max_deg,
            self.longitude_min_deg,
            self.longitude_max_deg,
            self.cell_size_deg,
        ]
        .iter()
        .all(|value| value.is_finite())
            || self.latitude_min_deg >= self.latitude_max_deg
            || self.longitude_min_deg >= self.longitude_max_deg
            || self.cell_size_deg <= 0.0
        {
            return Err("known-flight histogram grid is invalid");
        }
        let latitude = (self.latitude_max_deg - self.latitude_min_deg) / self.cell_size_deg;
        let longitude = (self.longitude_max_deg - self.longitude_min_deg) / self.cell_size_deg;
        if (latitude - latitude.round()).abs() > 1e-9
            || (longitude - longitude.round()).abs() > 1e-9
            || latitude * longitude > 2_000_000.0
        {
            return Err("known-flight histogram grid dimensions are invalid");
        }
        Ok(())
    }

    fn dimensions(&self) -> (usize, usize) {
        (
            ((self.latitude_max_deg - self.latitude_min_deg) / self.cell_size_deg).round() as usize,
            ((self.longitude_max_deg - self.longitude_min_deg) / self.cell_size_deg).round()
                as usize,
        )
    }

    fn index(&self, position: LatLon) -> Option<usize> {
        if position.latitude.0 < self.latitude_min_deg
            || position.latitude.0 >= self.latitude_max_deg
            || position.longitude.0 < self.longitude_min_deg
            || position.longitude.0 >= self.longitude_max_deg
        {
            return None;
        }
        let (_, columns) = self.dimensions();
        let row =
            ((position.latitude.0 - self.latitude_min_deg) / self.cell_size_deg).floor() as usize;
        let column =
            ((position.longitude.0 - self.longitude_min_deg) / self.cell_size_deg).floor() as usize;
        Some(row * columns + column)
    }

    fn latitude_center(&self, index: usize) -> f64 {
        let (_, columns) = self.dimensions();
        self.latitude_min_deg
            + (index / columns) as f64 * self.cell_size_deg
            + 0.5 * self.cell_size_deg
    }
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct KnownFlightTruthRow {
    pub checkpoint_index: usize,
    pub epoch_id: String,
    pub time_utc: String,
    pub seconds_from_t0: f64,
    pub observed_bto_us: Option<f64>,
    pub truth_predicted_bto_us: Option<f64>,
    pub truth_state_bto_residual_us: Option<f64>,
    pub observed_bfo_hz: Option<f64>,
    pub altitude_ft: f64,
    pub mach: f64,
    pub latitude_deg: f64,
    pub longitude_deg: f64,
    pub heading_true_deg: f64,
    pub ground_speed_kt: f64,
    pub ground_track_deg: f64,
}

fn csv_value<'a>(
    values: &'a [&str],
    fields: &HashMap<String, usize>,
    name: &str,
) -> Result<&'a str, KnownFlightScoreError> {
    fields
        .get(name)
        .and_then(|index| values.get(*index))
        .copied()
        .ok_or_else(|| KnownFlightScoreError::InvalidTruth(format!("truth CSV lacks field {name}")))
}

fn number(
    values: &[&str],
    fields: &HashMap<String, usize>,
    name: &str,
) -> Result<f64, KnownFlightScoreError> {
    let parsed = csv_value(values, fields, name)?
        .parse::<f64>()
        .map_err(|_| {
            KnownFlightScoreError::InvalidTruth(format!("truth field {name} is not numeric"))
        })?;
    if parsed.is_finite() {
        Ok(parsed)
    } else {
        Err(KnownFlightScoreError::InvalidTruth(format!(
            "truth field {name} is not finite"
        )))
    }
}

fn optional_number(
    values: &[&str],
    fields: &HashMap<String, usize>,
    name: &str,
) -> Result<Option<f64>, KnownFlightScoreError> {
    if csv_value(values, fields, name)?.is_empty() {
        Ok(None)
    } else {
        number(values, fields, name).map(Some)
    }
}

pub fn parse_known_flight_truth_csv(
    bytes: &[u8],
) -> Result<Vec<KnownFlightTruthRow>, KnownFlightScoreError> {
    let text = std::str::from_utf8(bytes)
        .map_err(|_| KnownFlightScoreError::InvalidTruth("truth CSV is not UTF-8".to_string()))?;
    let mut lines = text.lines();
    let header = lines
        .next()
        .ok_or_else(|| KnownFlightScoreError::InvalidTruth("truth CSV is empty".to_string()))?;
    if header.contains('"') {
        return Err(KnownFlightScoreError::InvalidTruth(
            "quoted truth CSV is not supported".to_string(),
        ));
    }
    let names = header.trim_end_matches('\r').split(',').collect::<Vec<_>>();
    let fields = names
        .iter()
        .enumerate()
        .map(|(index, name)| ((*name).to_string(), index))
        .collect::<HashMap<_, _>>();
    let mut rows = Vec::new();
    for (line_index, raw) in lines.enumerate() {
        let line = raw.trim_end_matches('\r');
        if line.is_empty() {
            continue;
        }
        let values = line.split(',').collect::<Vec<_>>();
        if values.len() != names.len() || line.contains('"') {
            return Err(KnownFlightScoreError::InvalidTruth(format!(
                "truth CSV line {} is malformed",
                line_index + 2
            )));
        }
        let checkpoint_index = csv_value(&values, &fields, "checkpoint_index")?
            .parse::<usize>()
            .map_err(|_| {
                KnownFlightScoreError::InvalidTruth("truth checkpoint index is invalid".to_string())
            })?;
        rows.push(KnownFlightTruthRow {
            checkpoint_index,
            epoch_id: csv_value(&values, &fields, "epoch_id")?.to_string(),
            time_utc: csv_value(&values, &fields, "time_utc")?.to_string(),
            seconds_from_t0: number(&values, &fields, "seconds_from_t0")?,
            observed_bto_us: optional_number(&values, &fields, "observed_bto_us")?,
            truth_predicted_bto_us: optional_number(&values, &fields, "truth_predicted_bto_us")?,
            truth_state_bto_residual_us: optional_number(
                &values,
                &fields,
                "truth_state_bto_residual_us",
            )?,
            observed_bfo_hz: optional_number(&values, &fields, "observed_bfo_hz")?,
            altitude_ft: number(&values, &fields, "altitude_ft")?,
            mach: number(&values, &fields, "mach")?,
            latitude_deg: number(&values, &fields, "lat_deg")?,
            longitude_deg: number(&values, &fields, "lon_deg")?,
            heading_true_deg: number(&values, &fields, "heading_true_deg")?,
            ground_speed_kt: number(&values, &fields, "ground_speed_kt")?,
            ground_track_deg: number(&values, &fields, "ground_track_deg")?,
        });
    }
    if rows.is_empty() {
        return Err(KnownFlightScoreError::InvalidTruth(
            "truth CSV has no rows".to_string(),
        ));
    }
    for (index, row) in rows.iter().enumerate() {
        if row.checkpoint_index != index {
            return Err(KnownFlightScoreError::InvalidTruth(
                "truth checkpoints are not contiguous".to_string(),
            ));
        }
        let observation_fields = [
            row.observed_bto_us,
            row.truth_predicted_bto_us,
            row.truth_state_bto_residual_us,
            row.observed_bfo_hz,
        ];
        if (index == 0 && observation_fields.iter().any(Option::is_some))
            || (index > 0 && observation_fields.iter().any(Option::is_none))
        {
            return Err(KnownFlightScoreError::InvalidTruth(
                "truth observation fields do not match checkpoint type".to_string(),
            ));
        }
    }
    Ok(rows)
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct KnownFlightCheckpointScore {
    pub seed: u64,
    pub checkpoint_index: usize,
    pub epoch_id: String,
    pub seconds_from_t0: f64,
    pub truth_latitude_deg: f64,
    pub truth_longitude_deg: f64,
    pub truth_heading_true_deg: f64,
    pub truth_ground_track_deg: f64,
    pub truth_ground_speed_kt: f64,
    pub truth_altitude_ft: f64,
    pub truth_mach: f64,
    pub posterior_mean_latitude_deg: f64,
    pub posterior_mean_longitude_deg: f64,
    pub posterior_mean_error_nm: f64,
    pub posterior_mean_ground_track_deg: f64,
    pub posterior_mean_ground_speed_kt: f64,
    pub posterior_mean_altitude_ft: f64,
    pub posterior_mean_mach: f64,
    pub posterior_mean_bfo_bias_hz: f64,
    pub mass_within_25_nm: f64,
    pub mass_within_50_nm: f64,
    pub mass_within_100_nm: f64,
    pub mass_within_200_nm: f64,
    pub truth_hpd_mass: f64,
    pub particle_ess: f64,
    pub root_ess: f64,
    pub contributing_root_count: usize,
    pub maximum_root_probability: f64,
    pub grid_captured_mass: f64,
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct KnownFlightPairwiseScore {
    pub checkpoint_index: usize,
    pub first_seed: u64,
    pub second_seed: u64,
    pub overlap: f64,
    pub jensen_shannon_nats: f64,
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct KnownFlightBtoClosure {
    pub checkpoint_index: usize,
    pub epoch_id: String,
    pub reported_predicted_bto_us: f64,
    pub rust_predicted_bto_us: f64,
    pub prediction_difference_us: f64,
    pub reported_residual_us: f64,
    pub rust_residual_us: f64,
    pub residual_difference_us: f64,
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct KnownFlightBfoClosure {
    pub checkpoint_index: usize,
    pub epoch_id: String,
    pub observed_bfo_hz: f64,
    pub predicted_without_aircraft_bias_hz: f64,
    pub implied_aircraft_bias_hz: f64,
    pub satellite_oscillator_hz: f64,
    pub perth_ges_afc_hz: f64,
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct KnownFlightScoreSummary {
    pub schema_version: String,
    pub status: String,
    pub numerically_valid: bool,
    pub experiment_name: String,
    pub model_family: String,
    pub inference_sha256: String,
    pub inference_config_sha256: String,
    pub truth_sha256: String,
    pub seeds: Vec<u64>,
    pub particle_count_per_seed: usize,
    pub checkpoints: Vec<KnownFlightCheckpointScore>,
    pub pairwise: Vec<KnownFlightPairwiseScore>,
    pub bto_truth_closure: Vec<KnownFlightBtoClosure>,
    pub bfo_truth_closure: Vec<KnownFlightBfoClosure>,
    pub minimum_final_mass_within_100_nm: f64,
    pub maximum_final_truth_hpd_mass: f64,
    pub minimum_pairwise_overlap: f64,
    pub maximum_pairwise_js_nats: f64,
    pub minimum_final_root_ess: f64,
    pub minimum_final_particle_ess: f64,
    pub maximum_bto_closure_abs_error_us: f64,
    pub limitations: Vec<String>,
}

#[derive(Debug, Error)]
pub enum KnownFlightScoreError {
    #[error("invalid known-flight scoring configuration: {0}")]
    InvalidConfiguration(&'static str),
    #[error("invalid scorer truth: {0}")]
    InvalidTruth(String),
    #[error("invalid known-flight inference result: {0}")]
    InvalidRun(String),
}

fn normalized_weights(
    snapshot: &FilterSnapshot<KnownFlightParticle>,
) -> Result<Vec<f64>, KnownFlightScoreError> {
    if snapshot.particles.is_empty()
        || snapshot.particles.len() != snapshot.log_weights.len()
        || snapshot.particles.len() != snapshot.root_ids.len()
    {
        return Err(KnownFlightScoreError::InvalidRun(
            "snapshot arrays differ in length or are empty".to_string(),
        ));
    }
    let mut weights = snapshot
        .log_weights
        .iter()
        .map(|value| value.exp())
        .collect::<Vec<_>>();
    let total = weights.iter().sum::<f64>();
    if !total.is_finite() || total <= 0.0 {
        return Err(KnownFlightScoreError::InvalidRun(
            "snapshot weights are invalid".to_string(),
        ));
    }
    for weight in &mut weights {
        *weight /= total;
    }
    Ok(weights)
}

fn circular_mean<'a>(values: impl Iterator<Item = (f64, &'a f64)>) -> f64 {
    let (sine, cosine) = values.fold((0.0, 0.0), |(sine, cosine), (degrees, weight)| {
        (
            sine + *weight * degrees.to_radians().sin(),
            cosine + *weight * degrees.to_radians().cos(),
        )
    });
    sine.atan2(cosine).to_degrees().rem_euclid(360.0)
}

fn histogram(
    snapshot: &FilterSnapshot<KnownFlightParticle>,
    weights: &[f64],
    grid: &KnownFlightGrid,
) -> Result<(Vec<f64>, f64), KnownFlightScoreError> {
    let (rows, columns) = grid.dimensions();
    let mut result = vec![0.0; rows * columns];
    let mut captured = 0.0;
    for (state, weight) in snapshot.particles.iter().zip(weights) {
        if let Some(index) = grid.index(state.aircraft.position) {
            result[index] += *weight;
            captured += *weight;
        }
    }
    if captured <= 0.0 || !captured.is_finite() {
        return Err(KnownFlightScoreError::InvalidRun(
            "histogram captures no posterior mass".to_string(),
        ));
    }
    for probability in &mut result {
        *probability /= captured;
    }
    Ok((result, captured))
}

fn hpd_mass_at_truth(
    histogram: &[f64],
    truth: LatLon,
    grid: &KnownFlightGrid,
) -> Result<f64, KnownFlightScoreError> {
    let truth_index = grid.index(truth).ok_or_else(|| {
        KnownFlightScoreError::InvalidTruth("truth lies outside histogram grid".to_string())
    })?;
    let density = |index: usize, probability: f64| {
        probability / grid.latitude_center(index).to_radians().cos().max(1e-12)
    };
    let truth_density = density(truth_index, histogram[truth_index]);
    Ok(histogram
        .iter()
        .enumerate()
        .filter_map(|(index, probability)| {
            (density(index, *probability) + 1e-18 >= truth_density).then_some(*probability)
        })
        .sum())
}

fn root_metrics(
    snapshot: &FilterSnapshot<KnownFlightParticle>,
    weights: &[f64],
) -> Result<(f64, usize, f64), KnownFlightScoreError> {
    let mut mass = BTreeMap::<usize, f64>::new();
    for (root, weight) in snapshot.root_ids.iter().zip(weights) {
        *mass.entry(*root).or_default() += *weight;
    }
    if mass.is_empty() {
        return Err(KnownFlightScoreError::InvalidRun(
            "snapshot has no roots".to_string(),
        ));
    }
    let ess = 1.0 / mass.values().map(|value| value * value).sum::<f64>();
    let maximum = mass.values().copied().fold(0.0, f64::max);
    Ok((ess, mass.len(), maximum))
}

fn score_checkpoint(
    run: &KnownFlightInferenceRun,
    snapshot: &FilterSnapshot<KnownFlightParticle>,
    truth: &KnownFlightTruthRow,
    grid: &KnownFlightGrid,
) -> Result<(KnownFlightCheckpointScore, Vec<f64>), KnownFlightScoreError> {
    if (snapshot.observation_time_s - truth.seconds_from_t0).abs() > 1e-6
        || snapshot.observation_index != truth.checkpoint_index.checked_sub(1)
    {
        return Err(KnownFlightScoreError::InvalidRun(format!(
            "seed {} checkpoint {} does not align with truth",
            run.seed, truth.checkpoint_index
        )));
    }
    let weights = normalized_weights(snapshot)?;
    let truth_position = LatLon::new(truth.latitude_deg, truth.longitude_deg).map_err(|_| {
        KnownFlightScoreError::InvalidTruth("truth coordinate is invalid".to_string())
    })?;
    let mean_latitude = snapshot
        .particles
        .iter()
        .zip(&weights)
        .map(|(state, weight)| state.aircraft.position.latitude.0 * weight)
        .sum::<f64>();
    let mean_longitude = circular_mean(
        snapshot
            .particles
            .iter()
            .zip(&weights)
            .map(|(state, weight)| (state.aircraft.position.longitude.0, weight)),
    );
    let mean_position = LatLon::new(mean_latitude, mean_longitude).map_err(|_| {
        KnownFlightScoreError::InvalidRun("posterior mean coordinate is invalid".to_string())
    })?;
    let mean = |field: fn(&KnownFlightParticle) -> f64| {
        snapshot
            .particles
            .iter()
            .zip(&weights)
            .map(|(state, weight)| field(state) * weight)
            .sum::<f64>()
    };
    let mass_within = |radius_nm: f64| {
        snapshot
            .particles
            .iter()
            .zip(&weights)
            .filter_map(|(state, weight)| {
                (great_circle_distance_nm(state.aircraft.position, truth_position).0 <= radius_nm)
                    .then_some(*weight)
            })
            .sum::<f64>()
    };
    let particle_ess = 1.0 / weights.iter().map(|weight| weight * weight).sum::<f64>();
    let (root_ess, contributing_root_count, maximum_root_probability) =
        root_metrics(snapshot, &weights)?;
    let (histogram, captured) = histogram(snapshot, &weights, grid)?;
    let result = KnownFlightCheckpointScore {
        seed: run.seed,
        checkpoint_index: truth.checkpoint_index,
        epoch_id: truth.epoch_id.clone(),
        seconds_from_t0: truth.seconds_from_t0,
        truth_latitude_deg: truth.latitude_deg,
        truth_longitude_deg: truth.longitude_deg,
        truth_heading_true_deg: truth.heading_true_deg,
        truth_ground_track_deg: truth.ground_track_deg,
        truth_ground_speed_kt: truth.ground_speed_kt,
        truth_altitude_ft: truth.altitude_ft,
        truth_mach: truth.mach,
        posterior_mean_latitude_deg: mean_position.latitude.0,
        posterior_mean_longitude_deg: mean_position.longitude.0,
        posterior_mean_error_nm: great_circle_distance_nm(mean_position, truth_position).0,
        posterior_mean_ground_track_deg: circular_mean(
            snapshot
                .particles
                .iter()
                .zip(&weights)
                .map(|(state, weight)| (state.aircraft.track_true.0, weight)),
        ),
        posterior_mean_ground_speed_kt: mean(|state| state.aircraft.ground_speed.0),
        posterior_mean_altitude_ft: mean(|state| state.aircraft.altitude.0),
        posterior_mean_mach: mean(|state| state.mach),
        posterior_mean_bfo_bias_hz: mean(|state| state.bfo_bias.mean_hz),
        mass_within_25_nm: mass_within(25.0),
        mass_within_50_nm: mass_within(50.0),
        mass_within_100_nm: mass_within(100.0),
        mass_within_200_nm: mass_within(200.0),
        truth_hpd_mass: hpd_mass_at_truth(&histogram, truth_position, grid)?,
        particle_ess,
        root_ess,
        contributing_root_count,
        maximum_root_probability,
        grid_captured_mass: captured,
    };
    Ok((result, histogram))
}

fn overlap(first: &[f64], second: &[f64]) -> f64 {
    first
        .iter()
        .zip(second)
        .map(|(left, right)| left.min(*right))
        .sum()
}

fn jensen_shannon(first: &[f64], second: &[f64]) -> f64 {
    first
        .iter()
        .zip(second)
        .map(|(left, right)| {
            let middle = 0.5 * (left + right);
            let term = |value: f64| {
                if value > 0.0 {
                    0.5 * value * (value / middle).ln()
                } else {
                    0.0
                }
            };
            term(*left) + term(*right)
        })
        .sum()
}

fn satcom_closure(
    run: &KnownFlightInferenceRun,
    truth: &[KnownFlightTruthRow],
    configuration: &KnownFlightScoringConfig,
) -> Result<(Vec<KnownFlightBtoClosure>, Vec<KnownFlightBfoClosure>), KnownFlightScoreError> {
    if run.observations.len() + 1 != truth.len() {
        return Err(KnownFlightScoreError::InvalidRun(
            "observation and truth checkpoint counts differ".to_string(),
        ));
    }
    let mut bto_rows = Vec::new();
    let mut bfo_rows = Vec::new();
    for (index, (observation, row)) in run.observations.iter().zip(&truth[1..]).enumerate() {
        if observation.epoch_id != row.epoch_id
            || observation.time_utc != row.time_utc
            || (observation.satcom.time.0 - row.seconds_from_t0).abs() > 1e-6
        {
            return Err(KnownFlightScoreError::InvalidRun(
                "inference observations do not align with truth".to_string(),
            ));
        }
        let position = LatLon::new(row.latitude_deg, row.longitude_deg).map_err(|_| {
            KnownFlightScoreError::InvalidTruth("truth coordinate is invalid".to_string())
        })?;
        let predicted_bto = bto(
            position,
            row.altitude_ft,
            observation.satcom.satellite_position_km,
            configuration.ground_station_position_km,
            configuration.satcom.bto,
        )
        .0;
        let reported_prediction = row.truth_predicted_bto_us.unwrap();
        let observed_bto = row.observed_bto_us.unwrap();
        let reported_residual = row.truth_state_bto_residual_us.unwrap();
        let rust_residual = observed_bto - predicted_bto;
        bto_rows.push(KnownFlightBtoClosure {
            checkpoint_index: index + 1,
            epoch_id: row.epoch_id.clone(),
            reported_predicted_bto_us: reported_prediction,
            rust_predicted_bto_us: predicted_bto,
            prediction_difference_us: predicted_bto - reported_prediction,
            reported_residual_us: reported_residual,
            rust_residual_us: rust_residual,
            residual_difference_us: rust_residual - reported_residual,
        });

        let state = AircraftState {
            time: Seconds(row.seconds_from_t0),
            position,
            altitude: Feet(row.altitude_ft),
            track_true: Degrees(row.ground_track_deg),
            ground_speed: Knots(row.ground_speed_kt),
            vertical_speed: FeetPerMinute(0.0),
            bfo_bias: Hertz(0.0),
        };
        let mut constants = configuration.satcom.bfo;
        constants.satellite_afc_hz = observation.combined_satellite_ges_hz();
        let predicted_without_bias = bfo_components(
            state,
            observation.satcom.satellite_position_km,
            observation.satcom.satellite_velocity_km_s,
            configuration.ground_station_position_km,
            constants,
        )
        .base_without_bias
        .0;
        let observed_bfo = row.observed_bfo_hz.unwrap();
        bfo_rows.push(KnownFlightBfoClosure {
            checkpoint_index: index + 1,
            epoch_id: row.epoch_id.clone(),
            observed_bfo_hz: observed_bfo,
            predicted_without_aircraft_bias_hz: predicted_without_bias,
            implied_aircraft_bias_hz: observed_bfo - predicted_without_bias,
            satellite_oscillator_hz: observation.satellite_oscillator_hz,
            perth_ges_afc_hz: observation.perth_ges_afc_hz,
        });
    }
    Ok((bto_rows, bfo_rows))
}

pub fn score_known_flight(
    configuration: &KnownFlightScoringConfig,
    runs: &[KnownFlightInferenceRun],
    truth: &[KnownFlightTruthRow],
    truth_sha256: &str,
) -> Result<KnownFlightScoreSummary, KnownFlightScoreError> {
    configuration
        .validate()
        .map_err(KnownFlightScoreError::InvalidConfiguration)?;
    if truth_sha256 != configuration.expected_truth_sha256 {
        return Err(KnownFlightScoreError::InvalidTruth(
            "truth SHA-256 does not match configuration".to_string(),
        ));
    }
    if runs.len() != configuration.expected_seeds.len() || runs.is_empty() {
        return Err(KnownFlightScoreError::InvalidRun(
            "run count differs from configured seed plan".to_string(),
        ));
    }
    let mut ordered = runs.iter().collect::<Vec<_>>();
    ordered.sort_by_key(|run| run.seed);
    let mut seeds = configuration.expected_seeds.clone();
    seeds.sort_unstable();
    if ordered.iter().map(|run| run.seed).collect::<Vec<_>>() != seeds {
        return Err(KnownFlightScoreError::InvalidRun(
            "run seeds differ from configured plan".to_string(),
        ));
    }
    let first = ordered[0];
    for run in &ordered {
        if run.schema_version != RUN_SCHEMA
            || run.inference_sha256 != configuration.expected_inference_sha256
            || run.inference_config_sha256 != first.inference_config_sha256
            || run.particle_count != first.particle_count
            || run.experiment_name != first.experiment_name
            || run.model_family != first.model_family
            || run.filter.snapshots.len() != truth.len()
        {
            return Err(KnownFlightScoreError::InvalidRun(format!(
                "seed {} provenance or checkpoint contract is invalid",
                run.seed
            )));
        }
    }

    let (bto_truth_closure, bfo_truth_closure) = satcom_closure(first, truth, configuration)?;
    let mut checkpoints = Vec::new();
    let mut histograms = Vec::new();
    for run in &ordered {
        let mut per_run = Vec::new();
        for (snapshot, truth_row) in run.filter.snapshots.iter().zip(truth) {
            let (assessment, histogram) =
                score_checkpoint(run, snapshot, truth_row, &configuration.grid)?;
            checkpoints.push(assessment);
            per_run.push(histogram);
        }
        histograms.push(per_run);
    }

    let mut pairwise = Vec::new();
    for checkpoint_index in 0..truth.len() {
        for first_index in 0..ordered.len() {
            for second_index in first_index + 1..ordered.len() {
                let left = &histograms[first_index][checkpoint_index];
                let right = &histograms[second_index][checkpoint_index];
                pairwise.push(KnownFlightPairwiseScore {
                    checkpoint_index,
                    first_seed: ordered[first_index].seed,
                    second_seed: ordered[second_index].seed,
                    overlap: overlap(left, right),
                    jensen_shannon_nats: jensen_shannon(left, right),
                });
            }
        }
    }

    let terminal_index = truth.len() - 1;
    let terminal = checkpoints
        .iter()
        .filter(|item| item.checkpoint_index == terminal_index)
        .collect::<Vec<_>>();
    let minimum_final_mass_within_100_nm = terminal
        .iter()
        .map(|item| item.mass_within_100_nm)
        .fold(1.0, f64::min);
    let maximum_final_truth_hpd_mass = terminal
        .iter()
        .map(|item| item.truth_hpd_mass)
        .fold(0.0, f64::max);
    let minimum_final_root_ess = terminal
        .iter()
        .map(|item| item.root_ess)
        .fold(f64::INFINITY, f64::min);
    let minimum_final_particle_ess = terminal
        .iter()
        .map(|item| item.particle_ess)
        .fold(f64::INFINITY, f64::min);
    let minimum_pairwise_overlap = pairwise.iter().map(|item| item.overlap).fold(1.0, f64::min);
    let maximum_pairwise_js_nats = pairwise
        .iter()
        .map(|item| item.jensen_shannon_nats)
        .fold(0.0, f64::max);
    let maximum_bto_closure_abs_error_us = bto_truth_closure
        .iter()
        .flat_map(|item| {
            [
                item.prediction_difference_us.abs(),
                item.residual_difference_us.abs(),
            ]
        })
        .fold(0.0, f64::max);

    Ok(KnownFlightScoreSummary {
        schema_version: "mh370-known-flight-assessment-v2".to_string(),
        status: "complete_known_flight_control_assessment".to_string(),
        numerically_valid: true,
        experiment_name: first.experiment_name.clone(),
        model_family: first.model_family.clone(),
        inference_sha256: first.inference_sha256.clone(),
        inference_config_sha256: first.inference_config_sha256.clone(),
        truth_sha256: truth_sha256.to_string(),
        seeds,
        particle_count_per_seed: first.particle_count,
        checkpoints,
        pairwise,
        bto_truth_closure,
        bfo_truth_closure,
        minimum_final_mass_within_100_nm,
        maximum_final_truth_hpd_mass,
        minimum_pairwise_overlap,
        maximum_pairwise_js_nats,
        minimum_final_root_ess,
        minimum_final_particle_ess,
        maximum_bto_closure_abs_error_us,
        limitations: vec![
            "held-back ACARS positions and trajectories were loaded only by this scorer"
                .to_string(),
            "posterior localization is conditional on the declared motion and BFO-noise family"
                .to_string(),
            "this known-flight control does not establish adequacy for the MH370 accident flight"
                .to_string(),
        ],
    })
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn circular_mean_handles_north_wrap() {
        let weights = [0.5, 0.5];
        let mean = circular_mean([(359.0, &weights[0]), (1.0, &weights[1])].into_iter());
        assert!(mean < 1e-9 || (mean - 360.0).abs() < 1e-9);
    }

    #[test]
    fn scoring_hash_check_is_strict() {
        assert!(is_sha256(
            "344debab104b9429ecf2db0b6b54530b60db86d642fdcfc9e04baad76add159a"
        ));
        assert!(!is_sha256("short"));
    }
}
