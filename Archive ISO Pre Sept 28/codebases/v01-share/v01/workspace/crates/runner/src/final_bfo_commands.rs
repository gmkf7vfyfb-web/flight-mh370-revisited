use std::{
    collections::BTreeMap,
    fs,
    path::{Path, PathBuf},
    time::Instant,
};

use anyhow::{bail, Context, Result};
use mh370_antenna::{
    evaluate_conditional_power, target_eirp_prediction, AircraftAttitude,
    ConditionalPowerObservation, DirectionalGainGrid, DirectionalPatternBasis, TargetEirpLinkModel,
};
use mh370_controls::{
    analyze_bfo_pair, search_bfo_pair, solve_bfo_vertical_speed, BfoPairCandidate,
    BfoPairObservation, BfoPairSearchBounds,
};
use mh370_domain::{
    AircraftState, Degrees, Feet, FeetPerMinute, Hertz, Knots, LatLon, Seconds, Vec3,
};
use mh370_dynamics::{
    evaluate_three_dof_feasibility, propagate_constant_track, DegreesPerSecond,
    GenericLoadClassification, HorizontalSpeedBasis, SpecificLoadG, ThreeDofFeasibilityInput,
};
use mh370_estimator::parse_satcom_observations;
use mh370_reporting::{build_bfo_match_tables_svg, BfoMatchTablePanel, BfoMatchTables};
use mh370_satcom::{bto, normal_log_density, SatcomModelConfig};
use serde::{Deserialize, Serialize};

use crate::{
    atomic_write, executable_sha256, prepare_output, sha256_bytes, sha256_file, write_json,
};
const RAW_BFO_MATCH_TOLERANCE_SD: f64 = 2.0;

#[derive(Debug, Clone, Deserialize)]
struct FinalBfoInputs {
    observations: PathBuf,
    satellite_ephemeris: PathBuf,
    ground_station_position_km: Vec3,
    request_epoch_id: String,
    acknowledgement_epoch_id: String,
}

#[derive(Debug, Clone, Copy, Deserialize, Serialize)]
struct RawPairConfig {
    request_bfo_hz: f64,
    acknowledgement_bfo_hz: f64,
    request_channel_bias_hz: f64,
    acknowledgement_channel_bias_hz: f64,
    ordinary_measurement_sd_hz: f64,
    elapsed_seconds: f64,
}

#[derive(Debug, Clone, Deserialize)]
struct SearchConfig {
    broad_posterior_samples: usize,
    broad_altitude_levels_ft: Vec<f64>,
    track_step_deg: f64,
    maximum_absolute_turn_rate_deg_s: f64,
    turn_rate_step_deg_s: f64,
    minimum_vertical_speed_fpm: f64,
    maximum_vertical_speed_fpm: f64,
    maximum_absolute_vertical_acceleration_g: f64,
    maximum_generic_total_specific_load_g: f64,
}

impl SearchConfig {
    fn bounds(&self) -> BfoPairSearchBounds {
        BfoPairSearchBounds {
            track_step_deg: self.track_step_deg,
            maximum_absolute_turn_rate_deg_s: self.maximum_absolute_turn_rate_deg_s,
            turn_rate_step_deg_s: self.turn_rate_step_deg_s,
            minimum_vertical_speed_fpm: self.minimum_vertical_speed_fpm,
            maximum_vertical_speed_fpm: self.maximum_vertical_speed_fpm,
            maximum_absolute_vertical_acceleration_g: self.maximum_absolute_vertical_acceleration_g,
        }
    }
}

#[derive(Debug, Clone, Deserialize)]
struct ConditionalPowerConfig {
    surface: PathBuf,
    observed_dbm: f64,
    observation_adjustment_db: f64,
    observation_sd_db: f64,
    reference_gain_dbic: f64,
    directional_departure_scale: f64,
    permit_unverified_reconstruction: bool,
    link: TargetEirpLinkModel,
}

#[derive(Debug, Clone, Deserialize)]
struct FinalBfoConfig {
    schema_version: u32,
    name: String,
    source_posterior: PathBuf,
    inputs: FinalBfoInputs,
    satcom: SatcomModelConfig,
    raw_pair: RawPairConfig,
    search: SearchConfig,
    conditional_power: Option<ConditionalPowerConfig>,
}

#[derive(Debug, Clone)]
struct SourceParticle {
    source: usize,
    particle: usize,
    weight: f64,
    state: AircraftState,
}

#[derive(Debug, Clone, Copy)]
struct PowerEvaluation {
    log_likelihood: f64,
    predicted_dbm: f64,
    residual_db: f64,
}

#[derive(Debug, Clone)]
struct FixedRecord {
    source: usize,
    particle: usize,
    prior_weight: f64,
    both_bto_weight: f64,
    both_bto_power_weight: Option<f64>,
    state: AircraftState,
    candidate: BfoPairCandidate,
    predicted_bto_change_us: f64,
    horizontal_and_satellite_bto_change_us: f64,
    descent_bto_change_us: f64,
    observed_minus_predicted_bto_change_us: f64,
    minimum_constant_altitude_bto_change_over_heading_grid_us: f64,
    maximum_constant_altitude_bto_change_over_heading_grid_us: f64,
    acknowledgement_bto_prediction_us: f64,
    acknowledgement_bto_residual_us: f64,
    acknowledgement_bto_log_likelihood: f64,
    within_declared_bounds: bool,
    power: Option<PowerEvaluation>,
}

#[derive(Debug, Clone)]
struct BroadRecord {
    source: usize,
    particle: usize,
    evaluated_candidates: usize,
    feasible_candidates: usize,
    minimum_request_altitude_ft: Option<f64>,
    minimum_candidate: Option<BfoPairCandidate>,
    minimum_no_turn_request_altitude_ft: Option<f64>,
    minimum_no_turn_candidate: Option<BfoPairCandidate>,
}

#[derive(Debug, Clone, Serialize)]
struct Distribution {
    mean: f64,
    minimum: f64,
    quantile_05: f64,
    median: f64,
    quantile_95: f64,
    maximum: f64,
}

#[derive(Debug, Clone, Serialize)]
struct WeightedScenarioSummary {
    label: String,
    effective_sample_size: f64,
    probability_within_declared_kinematic_bounds: f64,
    request_vertical_speed_fpm: Distribution,
    acknowledgement_vertical_speed_fpm: Distribution,
    vertical_speed_change_fpm: Distribution,
    mean_vertical_acceleration_g_upward: Distribution,
    request_vertical_speed_measurement_sd_fpm: Distribution,
    vertical_acceleration_measurement_sd_g: Distribution,
}

#[derive(Debug, Clone, Serialize)]
struct BtoChangeSummary {
    observed_bto_change_us: f64,
    predicted_total_change_us: Distribution,
    horizontal_and_satellite_change_at_constant_altitude_us: Distribution,
    descent_altitude_change_us: Distribution,
    observed_minus_predicted_change_us: Distribution,
    minimum_constant_altitude_change_over_heading_grid_us: Distribution,
    maximum_constant_altitude_change_over_heading_grid_us: Distribution,
}

#[derive(Debug, Clone, Serialize)]
struct BroadSummary {
    systematic_posterior_samples: usize,
    altitude_levels_ft: Vec<f64>,
    evaluated_candidates_per_sample: usize,
    posterior_sample_fraction_with_any_feasible_candidate: f64,
    feasible_grid_fraction: Distribution,
    minimum_absolute_acceleration_g: Option<Distribution>,
    minimum_absolute_acceleration_without_turn_g: Option<Distribution>,
    request_vertical_speed_at_minimum_fpm: Option<Distribution>,
    acknowledgement_vertical_speed_at_minimum_fpm: Option<Distribution>,
}

#[derive(Debug, Clone, Serialize)]
struct ConditionalPowerSummary {
    status: &'static str,
    raw_observed_dbm: f64,
    observation_adjustment_db: f64,
    adjusted_observed_dbm: f64,
    observation_sd_db: f64,
    heading_proxy: &'static str,
    directional_pattern_basis: &'static str,
    combined_with_both_bto: WeightedScenarioSummary,
}

#[derive(Debug, Serialize)]
struct FinalBfoSummary {
    schema_version: u32,
    name: String,
    status: &'static str,
    source_posterior_conditioning: Vec<String>,
    source_particles: usize,
    source_effective_sample_size: f64,
    request_epoch_id: String,
    acknowledgement_epoch_id: String,
    ephemeris_epoch_separation_s: f64,
    raw_pair: RawPairConfig,
    raw_hypothesis: Vec<String>,
    bto_change_diagnostic: BtoChangeSummary,
    fixed_prior_horizontal: WeightedScenarioSummary,
    raw_bfo_match_tables: BfoMatchTables,
    raw_bfo_zoom_match_tables: BfoMatchTables,
    raw_bfo_linked_zoom_match_tables: BfoMatchTables,
    fixed_prior_horizontal_with_both_bto: WeightedScenarioSummary,
    conditional_power: Option<ConditionalPowerSummary>,
    broad_horizontal_feasibility: BroadSummary,
    elapsed_seconds: f64,
    limitations: Vec<String>,
}

#[derive(Debug, Serialize)]
struct FinalBfoManifest {
    schema_version: u32,
    engine_version: &'static str,
    executable_sha256: String,
    command: &'static str,
    config_path: String,
    config_sha256: String,
    input_sha256: BTreeMap<String, String>,
    outputs: BTreeMap<String, String>,
    scientific_scope: Vec<String>,
}

fn resolve(config_path: &Path, value: &Path) -> PathBuf {
    if value.is_absolute() {
        value.to_path_buf()
    } else {
        config_path
            .parent()
            .unwrap_or_else(|| Path::new("."))
            .join(value)
    }
}

fn number(value: &str, row: usize, field: &str) -> Result<f64> {
    value
        .parse()
        .with_context(|| format!("invalid {field} in source posterior row {row}"))
}

fn integer(value: &str, row: usize, field: &str) -> Result<usize> {
    value
        .parse()
        .with_context(|| format!("invalid {field} in source posterior row {row}"))
}

fn parse_source_posterior(text: &str) -> Result<Vec<SourceParticle>> {
    const HEADER: &str = "source,particle,prior_weight,log_selection_likelihood,weight,start_time_s,start_latitude_deg,start_longitude_deg,end_time_s,end_latitude_deg,end_longitude_deg,altitude_ft,track_true_deg,ground_speed_kt,mach,bfo_bias_hz,predicted_observable,observable_residual,turn_time_s,post_turn_track_true_deg";
    let mut lines = text.lines();
    if lines.next() != Some(HEADER) {
        bail!("source posterior has an unsupported schema");
    }
    let mut particles = Vec::new();
    for (index, line) in lines.enumerate() {
        if line.trim().is_empty() {
            continue;
        }
        let row = index + 2;
        let fields = line.split(',').collect::<Vec<_>>();
        if fields.len() != 20 {
            bail!("invalid source posterior row {row}");
        }
        let weight = number(fields[4], row, "weight")?;
        let state = AircraftState {
            time: Seconds(number(fields[8], row, "end time")?),
            position: LatLon::new(
                number(fields[9], row, "end latitude")?,
                number(fields[10], row, "end longitude")?,
            )
            .with_context(|| format!("invalid coordinate in source posterior row {row}"))?,
            altitude: Feet(number(fields[11], row, "altitude")?),
            track_true: Degrees(number(fields[12], row, "track")?).wrapped_360(),
            ground_speed: Knots(number(fields[13], row, "ground speed")?),
            vertical_speed: FeetPerMinute(0.0),
            bfo_bias: Hertz(number(fields[15], row, "BFO bias")?),
        };
        if !state.all_finite()
            || state.altitude.0 < 0.0
            || state.ground_speed.0 <= 0.0
            || !weight.is_finite()
            || weight <= 0.0
        {
            bail!("nonphysical source posterior row {row}");
        }
        particles.push(SourceParticle {
            source: integer(fields[0], row, "source")?,
            particle: integer(fields[1], row, "particle")?,
            weight,
            state,
        });
    }
    if particles.is_empty() {
        bail!("source posterior is empty");
    }
    let total = particles.iter().map(|item| item.weight).sum::<f64>();
    if !total.is_finite() || total <= 0.0 {
        bail!("source posterior has zero probability");
    }
    for item in &mut particles {
        item.weight /= total;
    }
    Ok(particles)
}

fn weighted_distribution(values: &[(f64, f64)]) -> Result<Distribution> {
    let mut retained = values
        .iter()
        .copied()
        .filter(|(value, weight)| value.is_finite() && weight.is_finite() && *weight > 0.0)
        .collect::<Vec<_>>();
    if retained.is_empty() {
        bail!("cannot summarize an empty distribution");
    }
    let total = retained.iter().map(|item| item.1).sum::<f64>();
    if !total.is_finite() || total <= 0.0 {
        bail!("distribution has zero probability");
    }
    for item in &mut retained {
        item.1 /= total;
    }
    let mean = retained.iter().map(|item| item.0 * item.1).sum();
    let minimum = retained
        .iter()
        .map(|item| item.0)
        .fold(f64::INFINITY, f64::min);
    let maximum = retained
        .iter()
        .map(|item| item.0)
        .fold(f64::NEG_INFINITY, f64::max);
    retained.sort_by(|first, second| first.0.total_cmp(&second.0));
    let quantile = |probability: f64| {
        let mut cumulative = 0.0;
        for (value, weight) in &retained {
            cumulative += weight;
            if cumulative >= probability {
                return *value;
            }
        }
        retained.last().expect("distribution is non-empty").0
    };
    Ok(Distribution {
        mean,
        minimum,
        quantile_05: quantile(0.05),
        median: quantile(0.5),
        quantile_95: quantile(0.95),
        maximum,
    })
}

fn optional_equal_distribution(values: Vec<f64>) -> Result<Option<Distribution>> {
    if values.is_empty() {
        Ok(None)
    } else {
        let weight = 1.0 / values.len() as f64;
        Ok(Some(weighted_distribution(
            &values
                .into_iter()
                .map(|value| (value, weight))
                .collect::<Vec<_>>(),
        )?))
    }
}

fn effective_sample_size(weights: &[f64]) -> f64 {
    1.0 / weights.iter().map(|value| value.powi(2)).sum::<f64>()
}

fn scenario_summary(
    records: &[FixedRecord],
    weights: &[f64],
    label: &str,
) -> Result<WeightedScenarioSummary> {
    if records.len() != weights.len() {
        bail!("scenario weights do not match records");
    }
    let values = |extract: fn(&BfoPairCandidate) -> f64| {
        records
            .iter()
            .zip(weights)
            .map(|(record, weight)| (extract(&record.candidate), *weight))
            .collect::<Vec<_>>()
    };
    Ok(WeightedScenarioSummary {
        label: label.to_string(),
        effective_sample_size: effective_sample_size(weights),
        probability_within_declared_kinematic_bounds: records
            .iter()
            .zip(weights)
            .filter(|(record, _)| record.within_declared_bounds)
            .map(|(_, weight)| *weight)
            .sum(),
        request_vertical_speed_fpm: weighted_distribution(&values(|item| {
            item.request_vertical_speed_fpm
        }))?,
        acknowledgement_vertical_speed_fpm: weighted_distribution(&values(|item| {
            item.acknowledgement_vertical_speed_fpm
        }))?,
        vertical_speed_change_fpm: weighted_distribution(&values(|item| {
            item.vertical_speed_change_fpm
        }))?,
        mean_vertical_acceleration_g_upward: weighted_distribution(&values(|item| {
            item.mean_vertical_acceleration_g_upward
        }))?,
        request_vertical_speed_measurement_sd_fpm: weighted_distribution(&values(|item| {
            item.request_vertical_speed_sd_fpm
        }))?,
        vertical_acceleration_measurement_sd_g: weighted_distribution(&values(|item| {
            item.vertical_acceleration_sd_g
        }))?,
    })
}

fn fixed_record_distribution(
    records: &[FixedRecord],
    weights: &[f64],
    extract: impl Fn(&FixedRecord) -> f64,
) -> Result<Distribution> {
    weighted_distribution(
        &records
            .iter()
            .zip(weights)
            .map(|(record, weight)| (extract(record), *weight))
            .collect::<Vec<_>>(),
    )
}

fn bto_change_summary(
    records: &[FixedRecord],
    weights: &[f64],
    observed_bto_change_us: f64,
) -> Result<BtoChangeSummary> {
    if records.len() != weights.len() {
        bail!("BTO-change weights do not match records");
    }
    Ok(BtoChangeSummary {
        observed_bto_change_us,
        predicted_total_change_us: fixed_record_distribution(records, weights, |record| {
            record.predicted_bto_change_us
        })?,
        horizontal_and_satellite_change_at_constant_altitude_us: fixed_record_distribution(
            records,
            weights,
            |record| record.horizontal_and_satellite_bto_change_us,
        )?,
        descent_altitude_change_us: fixed_record_distribution(records, weights, |record| {
            record.descent_bto_change_us
        })?,
        observed_minus_predicted_change_us: fixed_record_distribution(
            records,
            weights,
            |record| record.observed_minus_predicted_bto_change_us,
        )?,
        minimum_constant_altitude_change_over_heading_grid_us: fixed_record_distribution(
            records,
            weights,
            |record| record.minimum_constant_altitude_bto_change_over_heading_grid_us,
        )?,
        maximum_constant_altitude_change_over_heading_grid_us: fixed_record_distribution(
            records,
            weights,
            |record| record.maximum_constant_altitude_bto_change_over_heading_grid_us,
        )?,
    })
}

fn normalize_log_weights(log_weights: &[f64]) -> Result<(Vec<f64>, f64)> {
    let maximum = log_weights
        .iter()
        .copied()
        .fold(f64::NEG_INFINITY, f64::max);
    let sum = log_weights
        .iter()
        .map(|value| (value - maximum).exp())
        .sum::<f64>();
    if !maximum.is_finite() || !sum.is_finite() || sum <= 0.0 {
        bail!("scenario has zero posterior probability");
    }
    Ok((
        log_weights
            .iter()
            .map(|value| (value - maximum).exp() / sum)
            .collect(),
        maximum + sum.ln(),
    ))
}

fn systematic_sample_indices(particles: &[SourceParticle], count: usize) -> Vec<usize> {
    let mut indices = Vec::with_capacity(count);
    let mut index = 0;
    let mut cumulative = particles[0].weight;
    for sample in 0..count {
        let threshold = (sample as f64 + 0.5) / count as f64;
        while cumulative < threshold && index + 1 < particles.len() {
            index += 1;
            cumulative += particles[index].weight;
        }
        indices.push(index);
    }
    indices
}
fn interval_overlaps(value: f64, half_width: f64, bucket: [f64; 2]) -> bool {
    value + half_width >= bucket[0] && value - half_width <= bucket[1]
}

const HEADING_BUCKET_COUNT: usize = 6;

fn heading_buckets_deg() -> Vec<[f64; 2]> {
    (0..HEADING_BUCKET_COUNT)
        .map(|index| [index as f64 * 60.0, (index + 1) as f64 * 60.0])
        .collect()
}

fn uniform_vertical_speed_buckets(
    minimum_fpm: f64,
    maximum_fpm: f64,
    bucket_count: usize,
) -> Vec<[f64; 2]> {
    let width = (maximum_fpm - minimum_fpm) / bucket_count as f64;
    (0..bucket_count)
        .map(|index| {
            [
                minimum_fpm + index as f64 * width,
                minimum_fpm + (index + 1) as f64 * width,
            ]
        })
        .collect()
}

fn independent_bfo_match_tables(
    particles: &[SourceParticle],
    sample_indices: &[usize],
    request: BfoPairObservation,
    acknowledgement: BfoPairObservation,
    constants: mh370_satcom::BfoConstants,
    raw_pair: RawPairConfig,
    bounds: BfoPairSearchBounds,
    vertical_speed_buckets_fpm: Vec<[f64; 2]>,
    title: &str,
) -> Result<BfoMatchTables> {
    let headings_per_bucket = (60.0 / bounds.track_step_deg).round() as usize;
    if headings_per_bucket == 0
        || (headings_per_bucket as f64 * bounds.track_step_deg - 60.0).abs() > 1e-9
        || vertical_speed_buckets_fpm.is_empty()
    {
        bail!("raw-BFO table grid is invalid");
    }
    let row_count = vertical_speed_buckets_fpm.len();
    let mut request_counts = vec![vec![0usize; HEADING_BUCKET_COUNT]; row_count];
    let mut acknowledgement_counts = vec![vec![0usize; HEADING_BUCKET_COUNT]; row_count];

    for &particle_index in sample_indices {
        let particle = &particles[particle_index];
        for heading_bucket in 0..HEADING_BUCKET_COUNT {
            let mut request_matches = vec![false; row_count];
            let mut acknowledgement_matches = vec![false; row_count];
            for heading_index in 0..headings_per_bucket {
                let heading_deg =
                    heading_bucket as f64 * 60.0 + heading_index as f64 * bounds.track_step_deg;
                let mut request_state = particle.state;
                request_state.track_true = Degrees(heading_deg);
                request_state.vertical_speed = FeetPerMinute(0.0);
                let request_solution = solve_bfo_vertical_speed(request_state, request, constants)?;
                let mut acknowledgement_state =
                    propagate_constant_track(request_state, Seconds(raw_pair.elapsed_seconds))?;
                acknowledgement_state.track_true = Degrees(heading_deg);
                acknowledgement_state.vertical_speed = FeetPerMinute(0.0);
                let acknowledgement_solution =
                    solve_bfo_vertical_speed(acknowledgement_state, acknowledgement, constants)?;
                for (vertical_bucket, bucket) in
                    vertical_speed_buckets_fpm.iter().copied().enumerate()
                {
                    request_matches[vertical_bucket] |= interval_overlaps(
                        request_solution.required_vertical_speed_fpm,
                        RAW_BFO_MATCH_TOLERANCE_SD * request_solution.ordinary_measurement_sd_fpm,
                        bucket,
                    );
                    acknowledgement_matches[vertical_bucket] |= interval_overlaps(
                        acknowledgement_solution.required_vertical_speed_fpm,
                        RAW_BFO_MATCH_TOLERANCE_SD
                            * acknowledgement_solution.ordinary_measurement_sd_fpm,
                        bucket,
                    );
                }
            }
            for vertical_bucket in 0..row_count {
                request_counts[vertical_bucket][heading_bucket] +=
                    usize::from(request_matches[vertical_bucket]);
                acknowledgement_counts[vertical_bucket][heading_bucket] +=
                    usize::from(acknowledgement_matches[vertical_bucket]);
            }
        }
    }

    let tolerance_sd = RAW_BFO_MATCH_TOLERANCE_SD;
    Ok(BfoMatchTables {
        title: title.to_string(),
        systematic_sample_count: sample_indices.len(),
        heading_step_deg: bounds.track_step_deg,
        tolerance_sd,
        tolerance_hz: tolerance_sd * raw_pair.ordinary_measurement_sd_hz,
        acknowledgement_elapsed_seconds: raw_pair.elapsed_seconds,
        heading_buckets_deg: heading_buckets_deg(),
        vertical_speed_buckets_fpm,
        request: BfoMatchTablePanel {
            title: "First transmission".to_string(),
            epoch_utc: "00:19:29".to_string(),
            channel: "R600 log-on request".to_string(),
            observed_bfo_hz: raw_pair.request_bfo_hz,
            counts: request_counts,
        },
        acknowledgement: BfoMatchTablePanel {
            title: "Second transmission".to_string(),
            epoch_utc: "00:19:37".to_string(),
            channel: "R1200 log-on acknowledge".to_string(),
            observed_bfo_hz: raw_pair.acknowledgement_bfo_hz,
            counts: acknowledgement_counts,
        },
        counting_rule: format!(
            "One sample per cell if any {:.0} deg heading in its sector has a +/-{:.0} Hz solution interval overlapping the vertical-speed row.",
            bounds.track_step_deg,
            tolerance_sd * raw_pair.ordinary_measurement_sd_hz
        ),
        limitation: "Panels are independent instantaneous inversions. Cells are nonexclusive existence counts, not probabilities or connected trajectories.".to_string(),
    })
}

fn zoom_vertical_speed_buckets(
    coarse: &BfoMatchTables,
    bucket_count: usize,
) -> Result<Vec<[f64; 2]>> {
    if bucket_count == 0 {
        bail!("zoom bucket count must be positive");
    }
    let matched_rows: Vec<_> = (0..coarse.vertical_speed_buckets_fpm.len())
        .filter(|row| {
            coarse.request.counts[*row].iter().any(|count| *count > 0)
                || coarse.acknowledgement.counts[*row]
                    .iter()
                    .any(|count| *count > 0)
        })
        .collect();
    let first = *matched_rows
        .first()
        .context("raw-BFO coarse table contains no matches")?;
    let last = *matched_rows
        .last()
        .context("raw-BFO coarse table contains no matches")?;
    Ok(uniform_vertical_speed_buckets(
        coarse.vertical_speed_buckets_fpm[first][0],
        coarse.vertical_speed_buckets_fpm[last][1],
        bucket_count,
    ))
}

fn heading_bucket_index(track_true_deg: f64) -> usize {
    let wrapped = Degrees(track_true_deg).wrapped_360().0;
    ((wrapped / 60.0).floor() as usize).min(HEADING_BUCKET_COUNT - 1)
}

fn linked_bfo_match_tables(
    particles: &[SourceParticle],
    sample_indices: &[usize],
    request: BfoPairObservation,
    acknowledgement: BfoPairObservation,
    constants: mh370_satcom::BfoConstants,
    raw_pair: RawPairConfig,
    bounds: BfoPairSearchBounds,
    maximum_generic_total_specific_load_g: f64,
    vertical_speed_buckets_fpm: Vec<[f64; 2]>,
) -> Result<BfoMatchTables> {
    let headings_per_bucket = (60.0 / bounds.track_step_deg).round() as usize;
    if headings_per_bucket == 0
        || (headings_per_bucket as f64 * bounds.track_step_deg - 60.0).abs() > 1e-9
        || bounds.turn_rate_step_deg_s <= 0.0
        || vertical_speed_buckets_fpm.is_empty()
    {
        bail!("linked raw-BFO table grid is invalid");
    }
    let row_count = vertical_speed_buckets_fpm.len();
    let turn_steps =
        (bounds.maximum_absolute_turn_rate_deg_s / bounds.turn_rate_step_deg_s).ceil() as i64;
    let mut request_counts = vec![vec![0usize; HEADING_BUCKET_COUNT]; row_count];
    let mut acknowledgement_counts = vec![vec![0usize; HEADING_BUCKET_COUNT]; row_count];

    for &particle_index in sample_indices {
        let particle = &particles[particle_index];
        let mut request_matches = vec![vec![false; HEADING_BUCKET_COUNT]; row_count];
        let mut acknowledgement_matches = vec![vec![false; HEADING_BUCKET_COUNT]; row_count];
        for heading_bucket in 0..HEADING_BUCKET_COUNT {
            for heading_index in 0..headings_per_bucket {
                let request_heading_deg =
                    heading_bucket as f64 * 60.0 + heading_index as f64 * bounds.track_step_deg;
                for turn_index in -turn_steps..=turn_steps {
                    let turn_rate_deg_s = turn_index as f64 * bounds.turn_rate_step_deg_s;
                    if turn_rate_deg_s.abs()
                        > bounds.maximum_absolute_turn_rate_deg_s + f64::EPSILON
                    {
                        continue;
                    }
                    let candidate = analyze_bfo_pair(
                        particle.state,
                        request,
                        acknowledgement,
                        constants,
                        raw_pair.elapsed_seconds,
                        request_heading_deg,
                        turn_rate_deg_s,
                    )?;
                    if !within_bounds(candidate, bounds)
                        || !within_generic_total_specific_load(
                            candidate,
                            particle.state.ground_speed,
                            raw_pair.elapsed_seconds,
                            maximum_generic_total_specific_load_g,
                        )?
                    {
                        continue;
                    }
                    let request_column = heading_bucket_index(candidate.request_track_true_deg);
                    let acknowledgement_column =
                        heading_bucket_index(candidate.acknowledgement_track_true_deg);
                    for (row, bucket) in vertical_speed_buckets_fpm.iter().copied().enumerate() {
                        request_matches[row][request_column] |= interval_overlaps(
                            candidate.request_vertical_speed_fpm,
                            RAW_BFO_MATCH_TOLERANCE_SD * candidate.request_vertical_speed_sd_fpm,
                            bucket,
                        );
                        acknowledgement_matches[row][acknowledgement_column] |= interval_overlaps(
                            candidate.acknowledgement_vertical_speed_fpm,
                            RAW_BFO_MATCH_TOLERANCE_SD
                                * candidate.acknowledgement_vertical_speed_sd_fpm,
                            bucket,
                        );
                    }
                }
            }
        }
        for row in 0..row_count {
            for column in 0..HEADING_BUCKET_COUNT {
                request_counts[row][column] += usize::from(request_matches[row][column]);
                acknowledgement_counts[row][column] +=
                    usize::from(acknowledgement_matches[row][column]);
            }
        }
    }

    let tolerance_sd = RAW_BFO_MATCH_TOLERANCE_SD;
    Ok(BfoMatchTables {
        title: "Raw BFO pair: dynamically linked candidates (zoom)".to_string(),
        systematic_sample_count: sample_indices.len(),
        heading_step_deg: bounds.track_step_deg,
        tolerance_sd,
        tolerance_hz: tolerance_sd * raw_pair.ordinary_measurement_sd_hz,
        acknowledgement_elapsed_seconds: raw_pair.elapsed_seconds,
        heading_buckets_deg: heading_buckets_deg(),
        vertical_speed_buckets_fpm,
        request: BfoMatchTablePanel {
            title: "Linked first state".to_string(),
            epoch_utc: "00:19:29".to_string(),
            channel: "R600 log-on request".to_string(),
            observed_bfo_hz: raw_pair.request_bfo_hz,
            counts: request_counts,
        },
        acknowledgement: BfoMatchTablePanel {
            title: "Linked second state".to_string(),
            epoch_utc: "00:19:37".to_string(),
            channel: "R1200 log-on acknowledge".to_string(),
            observed_bfo_hz: raw_pair.acknowledgement_bfo_hz,
            counts: acknowledgement_counts,
        },
        counting_rule: format!(
            "Central raw-BFO pair must form one 8.027 s path on the {:.0} deg and {:.1} deg/s grid and pass the declared bounds; rows include +/-{:.0} Hz.",
            bounds.track_step_deg,
            bounds.turn_rate_step_deg_s,
            tolerance_sd * raw_pair.ordinary_measurement_sd_hz
        ),
        limitation: format!(
            "Screen: earth-vertical acceleration at most {:.1} g and generic total specific load at most {:.1} g (ground-speed proxy); not a validated 777 envelope or probabilities.",
            bounds.maximum_absolute_vertical_acceleration_g,
            maximum_generic_total_specific_load_g
        ),
    })
}

fn within_generic_total_specific_load(
    candidate: BfoPairCandidate,
    ground_speed: Knots,
    elapsed_seconds: f64,
    threshold_g: f64,
) -> Result<bool> {
    let feasibility = evaluate_three_dof_feasibility(ThreeDofFeasibilityInput {
        horizontal_speed: ground_speed,
        horizontal_speed_basis: HorizontalSpeedBasis::GroundSpeed,
        initial_vertical_speed: FeetPerMinute(candidate.request_vertical_speed_fpm),
        final_vertical_speed: FeetPerMinute(candidate.acknowledgement_vertical_speed_fpm),
        elapsed_time: Seconds(elapsed_seconds),
        turn_rate: DegreesPerSecond(candidate.turn_rate_deg_s),
        generic_total_specific_load_threshold: SpecificLoadG(threshold_g),
    })?;
    Ok(matches!(
        feasibility.generic_load_classification,
        GenericLoadClassification::WithinInclusiveThreshold
    ))
}

fn within_bounds(candidate: BfoPairCandidate, bounds: BfoPairSearchBounds) -> bool {
    candidate.acknowledgement_altitude_ft >= 0.0
        && candidate.request_vertical_speed_fpm >= bounds.minimum_vertical_speed_fpm
        && candidate.request_vertical_speed_fpm <= bounds.maximum_vertical_speed_fpm
        && candidate.acknowledgement_vertical_speed_fpm >= bounds.minimum_vertical_speed_fpm
        && candidate.acknowledgement_vertical_speed_fpm <= bounds.maximum_vertical_speed_fpm
        && candidate.mean_vertical_acceleration_g_upward.abs()
            <= bounds.maximum_absolute_vertical_acceleration_g
}

fn acknowledgement_state(
    initial: AircraftState,
    candidate: BfoPairCandidate,
    elapsed_seconds: f64,
) -> Result<AircraftState> {
    let mut midpoint = initial;
    midpoint.track_true = Degrees(
        candidate.request_track_true_deg + 0.5 * candidate.turn_rate_deg_s * elapsed_seconds,
    )
    .wrapped_360();
    midpoint.vertical_speed = FeetPerMinute(
        0.5 * (candidate.request_vertical_speed_fpm + candidate.acknowledgement_vertical_speed_fpm),
    );
    let mut end = propagate_constant_track(midpoint, Seconds(elapsed_seconds))?;
    end.track_true = Degrees(candidate.acknowledgement_track_true_deg);
    end.vertical_speed = FeetPerMinute(candidate.acknowledgement_vertical_speed_fpm);
    Ok(end)
}

fn fixed_csv(records: &[FixedRecord]) -> Vec<u8> {
    let mut output = String::from(
        "source,particle,source_weight,both_bto_weight,both_bto_power_weight,latitude_deg,longitude_deg,altitude_ft,track_true_deg,ground_speed_kt,bfo_bias_hz,request_vertical_speed_fpm,acknowledgement_vertical_speed_fpm,vertical_speed_change_fpm,mean_vertical_acceleration_g_upward,vertical_acceleration_measurement_sd_g,acknowledgement_altitude_ft,acknowledgement_bto_prediction_us,acknowledgement_bto_residual_us,acknowledgement_bto_log_likelihood,within_declared_bounds,power_prediction_dbm,power_residual_db,power_log_likelihood\n",
    );
    for item in records {
        let power_weight = item
            .both_bto_power_weight
            .map(|value| value.to_string())
            .unwrap_or_default();
        let (power_prediction, power_residual, power_log_likelihood) = item
            .power
            .map(|value| {
                (
                    value.predicted_dbm.to_string(),
                    value.residual_db.to_string(),
                    value.log_likelihood.to_string(),
                )
            })
            .unwrap_or_default();
        let _ = std::fmt::Write::write_fmt(
            &mut output,
            format_args!(
                "{},{},{:.17e},{:.17e},{},{:.12},{:.12},{:.3},{:.9},{:.9},{:.9},{:.6},{:.6},{:.6},{:.9},{:.9},{:.3},{:.9},{:.9},{:.12},{},{},{},{}\n",
                item.source,
                item.particle,
                item.prior_weight,
                item.both_bto_weight,
                power_weight,
                item.state.position.latitude.0,
                item.state.position.longitude.0,
                item.state.altitude.0,
                item.state.track_true.0,
                item.state.ground_speed.0,
                item.state.bfo_bias.0,
                item.candidate.request_vertical_speed_fpm,
                item.candidate.acknowledgement_vertical_speed_fpm,
                item.candidate.vertical_speed_change_fpm,
                item.candidate.mean_vertical_acceleration_g_upward,
                item.candidate.vertical_acceleration_sd_g,
                item.candidate.acknowledgement_altitude_ft,
                item.acknowledgement_bto_prediction_us,
                item.acknowledgement_bto_residual_us,
                item.acknowledgement_bto_log_likelihood,
                item.within_declared_bounds,
                power_prediction,
                power_residual,
                power_log_likelihood,
            ),
        );
    }
    output.into_bytes()
}

fn broad_csv(records: &[BroadRecord]) -> Vec<u8> {
    let mut output = String::from(
        "sample,source,particle,evaluated_candidates,feasible_candidates,minimum_request_altitude_ft,minimum_request_track_true_deg,minimum_acknowledgement_track_true_deg,minimum_turn_rate_deg_s,minimum_request_vertical_speed_fpm,minimum_acknowledgement_vertical_speed_fpm,minimum_vertical_acceleration_g_upward,minimum_no_turn_request_altitude_ft,minimum_no_turn_request_track_true_deg,minimum_no_turn_request_vertical_speed_fpm,minimum_no_turn_acknowledgement_vertical_speed_fpm,minimum_no_turn_vertical_acceleration_g_upward\n",
    );
    for (sample, item) in records.iter().enumerate() {
        let candidate = item.minimum_candidate.unwrap_or(BfoPairCandidate {
            request_track_true_deg: f64::NAN,
            acknowledgement_track_true_deg: f64::NAN,
            turn_rate_deg_s: f64::NAN,
            request_vertical_speed_fpm: f64::NAN,
            acknowledgement_vertical_speed_fpm: f64::NAN,
            vertical_speed_change_fpm: f64::NAN,
            mean_vertical_acceleration_g_upward: f64::NAN,
            acknowledgement_altitude_ft: f64::NAN,
            request_bfo_sensitivity_hz_per_fpm: f64::NAN,
            acknowledgement_bfo_sensitivity_hz_per_fpm: f64::NAN,
            request_vertical_speed_sd_fpm: f64::NAN,
            acknowledgement_vertical_speed_sd_fpm: f64::NAN,
            vertical_acceleration_sd_g: f64::NAN,
        });
        let no_turn = item.minimum_no_turn_candidate.unwrap_or(candidate);
        let _ = std::fmt::Write::write_fmt(
            &mut output,
            format_args!(
                "{sample},{},{},{},{},{},{:.9},{:.9},{:.9},{:.6},{:.6},{:.9},{},{:.9},{:.6},{:.6},{:.9}\n",
                item.source,
                item.particle,
                item.evaluated_candidates,
                item.feasible_candidates,
                item.minimum_request_altitude_ft.map(|value| value.to_string()).unwrap_or_default(),
                candidate.request_track_true_deg,
                candidate.acknowledgement_track_true_deg,
                candidate.turn_rate_deg_s,
                candidate.request_vertical_speed_fpm,
                candidate.acknowledgement_vertical_speed_fpm,
                candidate.mean_vertical_acceleration_g_upward,
                item.minimum_no_turn_request_altitude_ft.map(|value| value.to_string()).unwrap_or_default(),
                no_turn.request_track_true_deg,
                no_turn.request_vertical_speed_fpm,
                no_turn.acknowledgement_vertical_speed_fpm,
                no_turn.mean_vertical_acceleration_g_upward,
            ),
        );
    }
    output.into_bytes()
}

pub(crate) fn analyze(config_path: &Path, output: &Path) -> Result<()> {
    let started = Instant::now();
    let config_bytes =
        fs::read(config_path).with_context(|| format!("cannot read {}", config_path.display()))?;
    let config: FinalBfoConfig = toml::from_str(
        std::str::from_utf8(&config_bytes).context("final-BFO config is not UTF-8")?,
    )
    .context("cannot parse final-BFO TOML")?;
    config.satcom.validate()?;
    let pair_values = [
        config.raw_pair.request_bfo_hz,
        config.raw_pair.acknowledgement_bfo_hz,
        config.raw_pair.request_channel_bias_hz,
        config.raw_pair.acknowledgement_channel_bias_hz,
        config.raw_pair.ordinary_measurement_sd_hz,
        config.raw_pair.elapsed_seconds,
    ];
    if config.schema_version != 1
        || config.name.trim().is_empty()
        || config.inputs.request_epoch_id.trim().is_empty()
        || config.inputs.acknowledgement_epoch_id.trim().is_empty()
        || !pair_values.iter().all(|value| value.is_finite())
        || config.raw_pair.ordinary_measurement_sd_hz <= 0.0
        || config.raw_pair.elapsed_seconds <= 0.0
        || config.search.broad_posterior_samples == 0
        || !config
            .search
            .maximum_generic_total_specific_load_g
            .is_finite()
        || config.search.maximum_generic_total_specific_load_g <= 0.0
        || config.search.broad_altitude_levels_ft.is_empty()
        || config
            .search
            .broad_altitude_levels_ft
            .iter()
            .any(|value| !value.is_finite() || *value < 0.0)
    {
        bail!("final-BFO configuration is incomplete or invalid");
    }
    let bounds = config.search.bounds();
    prepare_output(output)?;

    let source_path = resolve(config_path, &config.source_posterior);
    let observation_path = resolve(config_path, &config.inputs.observations);
    let ephemeris_path = resolve(config_path, &config.inputs.satellite_ephemeris);
    let source_bytes =
        fs::read(&source_path).with_context(|| format!("cannot read {}", source_path.display()))?;
    let observation_bytes = fs::read(&observation_path)
        .with_context(|| format!("cannot read {}", observation_path.display()))?;
    let ephemeris_bytes = fs::read(&ephemeris_path)
        .with_context(|| format!("cannot read {}", ephemeris_path.display()))?;
    let particles = parse_source_posterior(
        std::str::from_utf8(&source_bytes).context("source posterior is not UTF-8")?,
    )?;
    let observations = parse_satcom_observations(
        std::str::from_utf8(&observation_bytes).context("observation CSV is not UTF-8")?,
        std::str::from_utf8(&ephemeris_bytes).context("ephemeris CSV is not UTF-8")?,
        config.inputs.ground_station_position_km,
        None,
    )?;
    let request_source = observations
        .iter()
        .find(|item| item.id == config.inputs.request_epoch_id)
        .context("request epoch is absent from SATCOM input")?;
    let acknowledgement_source = observations
        .iter()
        .find(|item| item.id == config.inputs.acknowledgement_epoch_id)
        .context("acknowledgement epoch is absent from SATCOM input")?;
    let request_bto = request_source
        .measurement
        .bto
        .context("request epoch lacks a BTO observation")?;
    let (acknowledgement_bto, acknowledgement_bto_sd) = acknowledgement_source
        .measurement
        .bto
        .zip(acknowledgement_source.measurement.bto_sd)
        .context("acknowledgement epoch lacks a complete BTO observation")?;
    if particles
        .iter()
        .any(|item| (item.state.time.0 - request_source.measurement.time.0).abs() > 1e-6)
    {
        bail!("source posterior is not located at the request epoch");
    }

    let request_observation = BfoPairObservation {
        raw_bfo_hz: config.raw_pair.request_bfo_hz,
        channel_bias_hz: config.raw_pair.request_channel_bias_hz,
        ordinary_measurement_sd_hz: config.raw_pair.ordinary_measurement_sd_hz,
        satellite_afc_hz: request_source.satellite_afc_hz,
        satellite_position_km: request_source.measurement.satellite_position_km,
        satellite_velocity_km_s: request_source.measurement.satellite_velocity_km_s,
        ground_station_position_km: request_source.measurement.ground_station_position_km,
    };
    let acknowledgement_observation = BfoPairObservation {
        raw_bfo_hz: config.raw_pair.acknowledgement_bfo_hz,
        channel_bias_hz: config.raw_pair.acknowledgement_channel_bias_hz,
        ordinary_measurement_sd_hz: config.raw_pair.ordinary_measurement_sd_hz,
        satellite_afc_hz: acknowledgement_source.satellite_afc_hz,
        satellite_position_km: acknowledgement_source.measurement.satellite_position_km,
        satellite_velocity_km_s: acknowledgement_source.measurement.satellite_velocity_km_s,
        ground_station_position_km: acknowledgement_source
            .measurement
            .ground_station_position_km,
    };

    let mut input_sha256 = BTreeMap::from([
        (
            source_path.display().to_string(),
            sha256_bytes(&source_bytes),
        ),
        (
            observation_path.display().to_string(),
            sha256_bytes(&observation_bytes),
        ),
        (
            ephemeris_path.display().to_string(),
            sha256_bytes(&ephemeris_bytes),
        ),
    ]);
    let power_grid = if let Some(power) = &config.conditional_power {
        if ![
            power.observed_dbm,
            power.observation_adjustment_db,
            power.observation_sd_db,
            power.reference_gain_dbic,
            power.directional_departure_scale,
        ]
        .iter()
        .all(|value| value.is_finite())
            || power.observation_sd_db <= 0.0
            || !(0.0..=1.0).contains(&power.directional_departure_scale)
        {
            bail!("conditional power configuration is invalid");
        }
        let path = resolve(config_path, &power.surface);
        let bytes = fs::read(&path)
            .with_context(|| format!("cannot read antenna surface {}", path.display()))?;
        input_sha256.insert(path.display().to_string(), sha256_bytes(&bytes));
        Some(DirectionalGainGrid::parse(
            &bytes,
            DirectionalPatternBasis::UnverifiedReconstruction,
        )?)
    } else {
        None
    };

    let mut fixed = Vec::with_capacity(particles.len());
    let mut both_bto_log_weights = Vec::with_capacity(particles.len());
    let mut both_bto_power_log_weights = Vec::with_capacity(particles.len());
    for item in &particles {
        let candidate = analyze_bfo_pair(
            item.state,
            request_observation,
            acknowledgement_observation,
            config.satcom.bfo,
            config.raw_pair.elapsed_seconds,
            item.state.track_true.0,
            0.0,
        )?;
        let request_bto_prediction = bto(
            item.state.position,
            item.state.altitude.0,
            request_source.measurement.satellite_position_km,
            request_source.measurement.ground_station_position_km,
            config.satcom.bto,
        )
        .0;
        let mut minimum_constant_altitude_bto_change_us = f64::INFINITY;
        let mut maximum_constant_altitude_bto_change_us = f64::NEG_INFINITY;
        let heading_count = (360.0 / bounds.track_step_deg).ceil() as usize;
        for heading_index in 0..heading_count {
            let mut horizontal_state = item.state;
            horizontal_state.track_true =
                Degrees(heading_index as f64 * bounds.track_step_deg).wrapped_360();
            horizontal_state.vertical_speed = FeetPerMinute(0.0);
            let horizontal_end = propagate_constant_track(
                horizontal_state,
                Seconds(config.raw_pair.elapsed_seconds),
            )?;
            let change_us = bto(
                horizontal_end.position,
                horizontal_end.altitude.0,
                acknowledgement_source.measurement.satellite_position_km,
                acknowledgement_source
                    .measurement
                    .ground_station_position_km,
                config.satcom.bto,
            )
            .0 - request_bto_prediction;
            minimum_constant_altitude_bto_change_us =
                minimum_constant_altitude_bto_change_us.min(change_us);
            maximum_constant_altitude_bto_change_us =
                maximum_constant_altitude_bto_change_us.max(change_us);
        }
        let end = acknowledgement_state(item.state, candidate, config.raw_pair.elapsed_seconds)?;
        let acknowledgement_bto_at_request_altitude = bto(
            end.position,
            item.state.altitude.0,
            acknowledgement_source.measurement.satellite_position_km,
            acknowledgement_source
                .measurement
                .ground_station_position_km,
            config.satcom.bto,
        )
        .0;
        let predicted_bto = bto(
            end.position,
            end.altitude.0,
            acknowledgement_source.measurement.satellite_position_km,
            acknowledgement_source
                .measurement
                .ground_station_position_km,
            config.satcom.bto,
        )
        .0;
        let predicted_bto_change_us = predicted_bto - request_bto_prediction;
        let horizontal_and_satellite_bto_change_us =
            acknowledgement_bto_at_request_altitude - request_bto_prediction;
        let descent_bto_change_us = predicted_bto - acknowledgement_bto_at_request_altitude;
        let observed_minus_predicted_bto_change_us =
            acknowledgement_bto.0 - request_bto.0 - predicted_bto_change_us;
        let bto_residual = acknowledgement_bto.0 - predicted_bto;
        let bto_log_likelihood = normal_log_density(bto_residual, acknowledgement_bto_sd.0)?;
        both_bto_log_weights.push(item.weight.ln() + bto_log_likelihood);

        let power_evaluation = if let (Some(power), Some(grid)) =
            (&config.conditional_power, &power_grid)
        {
            let adjusted_observed = power.observed_dbm + power.observation_adjustment_db;
            let link_prediction = target_eirp_prediction(
                item.state,
                request_source.measurement.satellite_position_km,
                request_source.measurement.ground_station_position_km,
                power.link,
            )?;
            let score = evaluate_conditional_power(
                item.state,
                AircraftAttitude::level(item.state.track_true),
                request_source.measurement.satellite_position_km,
                grid,
                ConditionalPowerObservation {
                    observed_dbm: adjusted_observed,
                    full_precompensation_prediction_dbm: link_prediction
                        .full_precompensation_prediction_dbm,
                    standard_deviation_db: power.observation_sd_db,
                    reference_gain_dbic: power.reference_gain_dbic,
                    directional_departure_scale: power.directional_departure_scale,
                    permit_unverified_reconstruction: power.permit_unverified_reconstruction,
                },
            )?;
            let log_likelihood = score
                .log_likelihood
                .context("unverified power likelihood was not explicitly permitted")?;
            both_bto_power_log_weights.push(item.weight.ln() + bto_log_likelihood + log_likelihood);
            Some(PowerEvaluation {
                log_likelihood,
                predicted_dbm: score.predicted_dbm,
                residual_db: adjusted_observed - score.predicted_dbm,
            })
        } else {
            None
        };
        fixed.push(FixedRecord {
            source: item.source,
            particle: item.particle,
            prior_weight: item.weight,
            both_bto_weight: 0.0,
            both_bto_power_weight: None,
            state: item.state,
            candidate,
            predicted_bto_change_us,
            horizontal_and_satellite_bto_change_us,
            descent_bto_change_us,
            observed_minus_predicted_bto_change_us,
            minimum_constant_altitude_bto_change_over_heading_grid_us:
                minimum_constant_altitude_bto_change_us,
            maximum_constant_altitude_bto_change_over_heading_grid_us:
                maximum_constant_altitude_bto_change_us,
            acknowledgement_bto_prediction_us: predicted_bto,
            acknowledgement_bto_residual_us: bto_residual,
            acknowledgement_bto_log_likelihood: bto_log_likelihood,
            within_declared_bounds: within_bounds(candidate, bounds),
            power: power_evaluation,
        });
    }
    let (both_bto_weights, _) = normalize_log_weights(&both_bto_log_weights)?;
    for (record, weight) in fixed.iter_mut().zip(&both_bto_weights) {
        record.both_bto_weight = *weight;
    }
    let power_weights = if both_bto_power_log_weights.is_empty() {
        None
    } else {
        let (weights, _) = normalize_log_weights(&both_bto_power_log_weights)?;
        for (record, weight) in fixed.iter_mut().zip(&weights) {
            record.both_bto_power_weight = Some(*weight);
        }
        Some(weights)
    };

    let sample_indices =
        systematic_sample_indices(&particles, config.search.broad_posterior_samples);
    let raw_bfo_match_tables = independent_bfo_match_tables(
        &particles,
        &sample_indices,
        request_observation,
        acknowledgement_observation,
        config.satcom.bfo,
        config.raw_pair,
        bounds,
        uniform_vertical_speed_buckets(
            bounds.minimum_vertical_speed_fpm,
            bounds.maximum_vertical_speed_fpm,
            6,
        ),
        "Raw BFO feasibility by heading and vertical speed",
    )?;
    let zoom_buckets = zoom_vertical_speed_buckets(&raw_bfo_match_tables, 10)?;
    let raw_bfo_zoom_match_tables = independent_bfo_match_tables(
        &particles,
        &sample_indices,
        request_observation,
        acknowledgement_observation,
        config.satcom.bfo,
        config.raw_pair,
        bounds,
        zoom_buckets.clone(),
        "Raw BFO feasibility: matched-range zoom",
    )?;
    let raw_bfo_linked_zoom_match_tables = linked_bfo_match_tables(
        &particles,
        &sample_indices,
        request_observation,
        acknowledgement_observation,
        config.satcom.bfo,
        config.raw_pair,
        bounds,
        config.search.maximum_generic_total_specific_load_g,
        zoom_buckets,
    )?;
    let mut broad = Vec::with_capacity(sample_indices.len());
    for &particle_index in &sample_indices {
        let item = &particles[particle_index];
        let mut evaluated_candidates = 0;
        let mut feasible_candidates = 0;
        let mut minimum: Option<(f64, BfoPairCandidate)> = None;
        let mut minimum_no_turn: Option<(f64, BfoPairCandidate)> = None;
        for altitude_ft in &config.search.broad_altitude_levels_ft {
            let mut state = item.state;
            state.altitude = Feet(*altitude_ft);
            let result = search_bfo_pair(
                state,
                request_observation,
                acknowledgement_observation,
                config.satcom.bfo,
                config.raw_pair.elapsed_seconds,
                bounds,
            )?;
            evaluated_candidates += result.evaluated_candidates;
            feasible_candidates += result.feasible_candidates;
            if let Some(candidate) = result.minimum_absolute_acceleration {
                if minimum.map_or(true, |(_, current)| {
                    candidate.mean_vertical_acceleration_g_upward.abs()
                        < current.mean_vertical_acceleration_g_upward.abs()
                }) {
                    minimum = Some((*altitude_ft, candidate));
                }
            }
            if let Some(candidate) = result.minimum_absolute_acceleration_without_turn {
                if minimum_no_turn.map_or(true, |(_, current)| {
                    candidate.mean_vertical_acceleration_g_upward.abs()
                        < current.mean_vertical_acceleration_g_upward.abs()
                }) {
                    minimum_no_turn = Some((*altitude_ft, candidate));
                }
            }
        }
        broad.push(BroadRecord {
            source: item.source,
            particle: item.particle,
            evaluated_candidates,
            feasible_candidates,
            minimum_request_altitude_ft: minimum.map(|value| value.0),
            minimum_candidate: minimum.map(|value| value.1),
            minimum_no_turn_request_altitude_ft: minimum_no_turn.map(|value| value.0),
            minimum_no_turn_candidate: minimum_no_turn.map(|value| value.1),
        });
    }

    let prior_weights = fixed
        .iter()
        .map(|item| item.prior_weight)
        .collect::<Vec<_>>();
    let fixed_prior_horizontal = scenario_summary(
        &fixed,
        &prior_weights,
        "first R600 BTO-conditioned; raw BFO inversion; prior track and zero turn",
    )?;
    let fixed_both_bto = scenario_summary(
        &fixed,
        &both_bto_weights,
        "both final BTOs; raw BFO inversion; prior track and zero turn",
    )?;
    let bto_change_diagnostic = bto_change_summary(
        &fixed,
        &prior_weights,
        acknowledgement_bto.0 - request_bto.0,
    )?;
    let conditional_power = match (&config.conditional_power, power_weights.as_ref()) {
        (Some(power), Some(weights)) => Some(ConditionalPowerSummary {
            status: "conditional_sensitivity_only",
            raw_observed_dbm: power.observed_dbm,
            observation_adjustment_db: power.observation_adjustment_db,
            adjusted_observed_dbm: power.observed_dbm + power.observation_adjustment_db,
            observation_sd_db: power.observation_sd_db,
            heading_proxy: "true ground track",
            directional_pattern_basis: "unverified_first_pass_reconstruction",
            combined_with_both_bto: scenario_summary(
                &fixed,
                weights,
                "both final BTOs plus conditional R600 power; raw BFO inversion",
            )?,
        }),
        _ => None,
    };

    let broad_count = broad.len() as f64;
    let broad_summary = BroadSummary {
        systematic_posterior_samples: broad.len(),
        altitude_levels_ft: config.search.broad_altitude_levels_ft.clone(),
        evaluated_candidates_per_sample: broad
            .first()
            .map(|item| item.evaluated_candidates)
            .unwrap_or(0),
        posterior_sample_fraction_with_any_feasible_candidate: broad
            .iter()
            .filter(|item| item.feasible_candidates > 0)
            .count() as f64
            / broad_count,
        feasible_grid_fraction: weighted_distribution(
            &broad
                .iter()
                .map(|item| {
                    (
                        item.feasible_candidates as f64 / item.evaluated_candidates as f64,
                        1.0 / broad_count,
                    )
                })
                .collect::<Vec<_>>(),
        )?,
        minimum_absolute_acceleration_g: optional_equal_distribution(
            broad
                .iter()
                .filter_map(|item| item.minimum_candidate)
                .map(|item| item.mean_vertical_acceleration_g_upward.abs())
                .collect(),
        )?,
        minimum_absolute_acceleration_without_turn_g: optional_equal_distribution(
            broad
                .iter()
                .filter_map(|item| item.minimum_no_turn_candidate)
                .map(|item| item.mean_vertical_acceleration_g_upward.abs())
                .collect(),
        )?,
        request_vertical_speed_at_minimum_fpm: optional_equal_distribution(
            broad
                .iter()
                .filter_map(|item| item.minimum_candidate)
                .map(|item| item.request_vertical_speed_fpm)
                .collect(),
        )?,
        acknowledgement_vertical_speed_at_minimum_fpm: optional_equal_distribution(
            broad
                .iter()
                .filter_map(|item| item.minimum_candidate)
                .map(|item| item.acknowledgement_vertical_speed_fpm)
                .collect(),
        )?,
    };

    let summary = FinalBfoSummary {
        schema_version: 2,
        name: config.name,
        status: "complete_diagnostic_not_core_posterior",
        source_posterior_conditioning: vec![
            "00:11 posterior propagated with fixed true track, ground speed, and altitude to 00:19:29".to_string(),
            "00:19:29 R600 BTO likelihood already included in source weights".to_string(),
            "00:19:37 R1200 BTO is shown as an explicit additional reweighting".to_string(),
        ],
        source_particles: particles.len(),
        source_effective_sample_size: effective_sample_size(&prior_weights),
        request_epoch_id: request_source.id.clone(),
        acknowledgement_epoch_id: acknowledgement_source.id.clone(),
        ephemeris_epoch_separation_s: acknowledgement_source.measurement.time.0
            - request_source.measurement.time.0,
        raw_pair: config.raw_pair,
        raw_hypothesis: vec![
            "Both reported BFO values are treated as physical observations with zero added startup/channel bias.".to_string(),
            "The posterior BFO equipment bias inferred through 00:11 is retained particle by particle.".to_string(),
            "The displayed 7 Hz uncertainty is the ordinary BFO error model; it does not calibrate unknown startup transients.".to_string(),
        ],
        bto_change_diagnostic,
        fixed_prior_horizontal,
        raw_bfo_match_tables,
        raw_bfo_zoom_match_tables,
        raw_bfo_linked_zoom_match_tables,
        fixed_prior_horizontal_with_both_bto: fixed_both_bto,
        conditional_power,
        broad_horizontal_feasibility: broad_summary,
        elapsed_seconds: started.elapsed().as_secs_f64(),
        limitations: vec![
            "This is an inverse kinematic feasibility control, not a posterior over descent dynamics; no probability prior is assigned to headings, turns, vertical speeds, or accelerations.".to_string(),
            "Earth-vertical acceleration is not aircraft load factor and the declared envelope is a transparent generous bound, not a validated Boeing 777 envelope.".to_string(),
            "The linked table additionally applies a configured 2.5 g generic total-specific-load screen using ground speed as an airspeed proxy; it is not a Boeing 777 operating or structural limit.".to_string(),
            "Broad heading search changes local 00:19 state without propagating a preceding turn from 00:11 and therefore cannot be used as a trajectory posterior.".to_string(),
            "Broad altitude levels test local BFO feasibility only; their BTO compatibility and probability are not evaluated.".to_string(),
            "Horizontal speed is held at each source particle value; candidate roll, pitch, wind, engine state, and flight-control state are absent.".to_string(),
            "The conditional power result uses ground track as heading, explicitly sets roll and pitch to zero, applies a -3.6 dB channel adjustment from configuration, and uses an uncommissioned antenna reconstruction.".to_string(),
            "No R600-versus-R1200 BFO calibration exists in the current estimator; zero channel terms are an explicit hypothesis, not a measurement.".to_string(),
        ],
    };

    let summary_path = output.join("summary.json");
    let fixed_path = output.join("fixed-horizontal.csv");
    let broad_path = output.join("broad-feasibility.csv");
    let table_json_path = output.join("raw-bfo-match-tables.json");
    let table_svg_path = output.join("raw-bfo-match-tables.svg");
    let zoom_table_json_path = output.join("raw-bfo-match-tables-zoom.json");
    let zoom_table_svg_path = output.join("raw-bfo-match-tables-zoom.svg");
    let linked_zoom_table_json_path = output.join("raw-bfo-linked-match-tables-zoom.json");
    let linked_zoom_table_svg_path = output.join("raw-bfo-linked-match-tables-zoom.svg");
    write_json(&summary_path, &summary)?;
    atomic_write(&fixed_path, &fixed_csv(&fixed))?;
    atomic_write(&broad_path, &broad_csv(&broad))?;
    write_json(&table_json_path, &summary.raw_bfo_match_tables)?;
    atomic_write(
        &table_svg_path,
        &build_bfo_match_tables_svg(&summary.raw_bfo_match_tables)?,
    )?;
    write_json(&zoom_table_json_path, &summary.raw_bfo_zoom_match_tables)?;
    atomic_write(
        &zoom_table_svg_path,
        &build_bfo_match_tables_svg(&summary.raw_bfo_zoom_match_tables)?,
    )?;
    write_json(
        &linked_zoom_table_json_path,
        &summary.raw_bfo_linked_zoom_match_tables,
    )?;
    atomic_write(
        &linked_zoom_table_svg_path,
        &build_bfo_match_tables_svg(&summary.raw_bfo_linked_zoom_match_tables)?,
    )?;

    let mut outputs = BTreeMap::new();
    for path in [
        &summary_path,
        &fixed_path,
        &broad_path,
        &table_json_path,
        &table_svg_path,
        &zoom_table_json_path,
        &zoom_table_svg_path,
        &linked_zoom_table_json_path,
        &linked_zoom_table_svg_path,
    ] {
        outputs.insert(
            path.file_name().unwrap().to_string_lossy().to_string(),
            sha256_file(path)?,
        );
    }
    let manifest = FinalBfoManifest {
        schema_version: 1,
        engine_version: env!("CARGO_PKG_VERSION"),
        executable_sha256: executable_sha256()?,
        command: "analyze-final-bfo",
        config_path: config_path.display().to_string(),
        config_sha256: sha256_bytes(&config_bytes),
        input_sha256,
        outputs,
        scientific_scope: vec![
            "Focused diagnostic downstream of the current 00:11-to-00:19 R600-BTO continuation.".to_string(),
            "Raw BFO feasibility and conditional power sensitivity remain separate from the core posterior.".to_string(),
        ],
    };
    write_json(&output.join("run-manifest.json"), &manifest)?;

    println!(
        "status=complete particles={} broad_samples={} request_vs_median_fpm={:.0} acknowledgement_vs_median_fpm={:.0} acceleration_median_g={:.3} summary={}",
        summary.source_particles,
        summary.broad_horizontal_feasibility.systematic_posterior_samples,
        summary.fixed_prior_horizontal.request_vertical_speed_fpm.median,
        summary.fixed_prior_horizontal.acknowledgement_vertical_speed_fpm.median,
        summary.fixed_prior_horizontal.mean_vertical_acceleration_g_upward.median,
        summary_path.display()
    );
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn source_parser_uses_bto_continuation_endpoint_and_weight() {
        let text = "source,particle,prior_weight,log_selection_likelihood,weight,start_time_s,start_latitude_deg,start_longitude_deg,end_time_s,end_latitude_deg,end_longitude_deg,altitude_ft,track_true_deg,ground_speed_kt,mach,bfo_bias_hz,predicted_observable,observable_residual,turn_time_s,post_turn_track_true_deg\n0,7,0.5,-1.0,1.0,22150,-36,89,22660,-37.6,89.2,35000,186,480,0.8,150,18400,0,2000,186\n";
        let parsed = parse_source_posterior(text).unwrap();
        assert_eq!(parsed.len(), 1);
        assert_eq!(parsed[0].particle, 7);
        assert_eq!(parsed[0].weight, 1.0);
        assert_eq!(parsed[0].state.time.0, 22_660.0);
        assert_eq!(parsed[0].state.position.latitude.0, -37.6);
    }

    #[test]
    fn systematic_sample_is_deterministic_and_respects_mass() {
        let base = AircraftState {
            time: Seconds(0.0),
            position: LatLon::new(0.0, 0.0).unwrap(),
            altitude: Feet(1.0),
            track_true: Degrees(0.0),
            ground_speed: Knots(1.0),
            vertical_speed: FeetPerMinute(0.0),
            bfo_bias: Hertz(0.0),
        };
        let particles = vec![
            SourceParticle {
                source: 0,
                particle: 0,
                weight: 0.75,
                state: base,
            },
            SourceParticle {
                source: 0,
                particle: 1,
                weight: 0.25,
                state: base,
            },
        ];
        assert_eq!(systematic_sample_indices(&particles, 4), vec![0, 0, 0, 1]);
    }
}
