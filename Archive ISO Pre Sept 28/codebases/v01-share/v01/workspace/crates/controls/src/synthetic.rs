use std::fmt;

use mh370_domain::{AircraftState, Degrees, Hertz, Knots, LatLon, SatcomObservation, Vec3};
use mh370_dynamics::{propagate_constant_track, DynamicsError};
use mh370_particle_filter::{rng_for, run_filter, FilterResult, ParticleModel, Proposal, SmcError};
use mh370_satcom::{bfo_components, bto, normal_log_density, StatisticsError};
use rand_chacha::ChaCha8Rng;
use rand_distr::{Distribution, StandardNormal};
use serde::{Deserialize, Serialize};
use thiserror::Error;

use crate::{summarize_synthetic, ExperimentConfig, SyntheticScenario, SyntheticSummary};

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct SyntheticDataset {
    pub schema_version: u32,
    pub experiment_name: String,
    pub truth_seed: u64,
    /// Includes the initial state followed by one state per observation.
    pub truth_states: Vec<AircraftState>,
    pub observations: Vec<SatcomObservation>,
}

#[derive(Debug, Clone, Serialize)]
pub struct SyntheticRun {
    pub dataset: SyntheticDataset,
    pub filter: FilterResult<AircraftState>,
    pub summary: SyntheticSummary,
}

#[derive(Debug, Error)]
pub enum SyntheticError {
    #[error("invalid experiment configuration: {0}")]
    InvalidConfiguration(&'static str),
    #[error("sampled coordinate is outside the physical domain")]
    InvalidCoordinate,
    #[error("sampled ground speed is non-positive")]
    InvalidGroundSpeed,
    #[error(transparent)]
    Dynamics(#[from] DynamicsError),
    #[error(transparent)]
    Statistics(#[from] StatisticsError),
    #[error(transparent)]
    Filter(#[from] SmcError),
}

fn normal(rng: &mut ChaCha8Rng) -> f64 {
    StandardNormal.sample(rng)
}

fn satellite_position(scenario: &SyntheticScenario, time_s: f64) -> Vec3 {
    scenario.satellite_initial_position_km
        + scenario.satellite_velocity_km_s * (time_s - scenario.initial_time_s)
}

fn perturb_and_propagate(
    scenario: &SyntheticScenario,
    state: AircraftState,
    elapsed_seconds: f64,
    rng: &mut ChaCha8Rng,
) -> Result<AircraftState, SyntheticError> {
    let scale = (elapsed_seconds / 3_600.0).sqrt();
    let mut proposed = state;
    proposed.track_true = Degrees(
        proposed.track_true.0 + normal(rng) * scenario.process_track_sd_deg_per_sqrt_hour * scale,
    )
    .wrapped_360();
    proposed.ground_speed = Knots(
        proposed.ground_speed.0
            + normal(rng) * scenario.process_ground_speed_sd_kt_per_sqrt_hour * scale,
    );
    proposed.bfo_bias = Hertz(
        proposed.bfo_bias.0 + normal(rng) * scenario.process_bfo_bias_sd_hz_per_sqrt_hour * scale,
    );
    if proposed.ground_speed.0 <= 0.0 || !proposed.all_finite() {
        return Err(SyntheticError::InvalidGroundSpeed);
    }
    Ok(propagate_constant_track(
        proposed,
        mh370_domain::Seconds(elapsed_seconds),
    )?)
}

fn predictions(
    scenario: &SyntheticScenario,
    state: AircraftState,
    observation: &SatcomObservation,
) -> (f64, f64) {
    let bto_value = bto(
        state.position,
        state.altitude.0,
        observation.satellite_position_km,
        observation.ground_station_position_km,
        scenario.bto_constants,
    )
    .0;
    let bfo_value = bfo_components(
        state,
        observation.satellite_position_km,
        observation.satellite_velocity_km_s,
        observation.ground_station_position_km,
        scenario.bfo_constants,
    )
    .base_without_bias
    .0 + state.bfo_bias.0;
    (bto_value, bfo_value)
}

fn observation_log_likelihood(
    scenario: &SyntheticScenario,
    state: AircraftState,
    observation: &SatcomObservation,
    inflation: f64,
) -> Result<f64, SyntheticError> {
    let (predicted_bto, predicted_bfo) = predictions(scenario, state, observation);
    let mut result = 0.0;
    if let (Some(observed), Some(sd)) = (observation.bto, observation.bto_sd) {
        result += normal_log_density(observed.0 - predicted_bto, sd.0 * inflation)?;
    }
    if let (Some(observed), Some(sd)) = (observation.bfo, observation.bfo_sd) {
        result += normal_log_density(observed.0 - predicted_bfo, sd.0 * inflation)?;
    }
    Ok(result)
}

pub fn simulate_synthetic(
    configuration: &ExperimentConfig,
) -> Result<SyntheticDataset, SyntheticError> {
    configuration
        .validate()
        .map_err(SyntheticError::InvalidConfiguration)?;
    let scenario = &configuration.synthetic;
    let mut truth = scenario
        .initial_state()
        .map_err(SyntheticError::InvalidConfiguration)?;
    let mut truth_states = vec![truth];
    let mut observations = Vec::with_capacity(scenario.epochs);

    for epoch in 0..scenario.epochs {
        let time_s = scenario.initial_time_s + (epoch + 1) as f64 * scenario.epoch_interval_s;
        let mut process_rng = rng_for(
            configuration.truth_seed,
            "synthetic-truth-process",
            epoch,
            0,
            0,
        );
        truth =
            perturb_and_propagate(scenario, truth, scenario.epoch_interval_s, &mut process_rng)?;
        debug_assert!((truth.time.0 - time_s).abs() < 1e-9);

        let mut observation = SatcomObservation {
            time: mh370_domain::Seconds(time_s),
            satellite_position_km: satellite_position(scenario, time_s),
            satellite_velocity_km_s: scenario.satellite_velocity_km_s,
            ground_station_position_km: scenario.ground_station_position_km,
            bto: None,
            bto_sd: None,
            bfo: None,
            bfo_sd: None,
        };
        let (predicted_bto, predicted_bfo) = predictions(scenario, truth, &observation);
        let mut observation_rng = rng_for(
            configuration.truth_seed,
            "synthetic-measurement",
            epoch,
            0,
            0,
        );
        observation.bto = Some(mh370_domain::Microseconds(
            predicted_bto + normal(&mut observation_rng) * scenario.bto_sd_us,
        ));
        observation.bto_sd = Some(mh370_domain::Microseconds(scenario.bto_sd_us));
        observation.bfo = Some(Hertz(
            predicted_bfo + normal(&mut observation_rng) * scenario.bfo_sd_hz,
        ));
        observation.bfo_sd = Some(Hertz(scenario.bfo_sd_hz));
        observation
            .validate()
            .map_err(SyntheticError::InvalidConfiguration)?;

        truth_states.push(truth);
        observations.push(observation);
    }

    Ok(SyntheticDataset {
        schema_version: 1,
        experiment_name: configuration.name.clone(),
        truth_seed: configuration.truth_seed,
        truth_states,
        observations,
    })
}

#[derive(Clone)]
struct SyntheticModel {
    scenario: SyntheticScenario,
}

#[derive(Debug)]
struct ModelError(SyntheticError);

impl fmt::Display for ModelError {
    fn fmt(&self, formatter: &mut fmt::Formatter<'_>) -> fmt::Result {
        self.0.fmt(formatter)
    }
}

impl std::error::Error for ModelError {}

impl From<SyntheticError> for ModelError {
    fn from(value: SyntheticError) -> Self {
        Self(value)
    }
}

impl ParticleModel for SyntheticModel {
    type State = AircraftState;
    type Observation = SatcomObservation;
    type Error = ModelError;

    fn observation_time_s(&self, observation: &Self::Observation) -> f64 {
        observation.time.0
    }

    fn initialize(
        &self,
        _particle_index: usize,
        rng: &mut ChaCha8Rng,
    ) -> Result<Self::State, Self::Error> {
        let initial = self
            .scenario
            .initial_state()
            .map_err(|value| ModelError(SyntheticError::InvalidConfiguration(value)))?;
        let position = LatLon::new(
            initial.position.latitude.0 + normal(rng) * self.scenario.prior_latitude_sd_deg,
            initial.position.longitude.0 + normal(rng) * self.scenario.prior_longitude_sd_deg,
        )
        .map_err(|_| ModelError(SyntheticError::InvalidCoordinate))?;
        let state = AircraftState {
            position,
            track_true: Degrees(
                initial.track_true.0 + normal(rng) * self.scenario.prior_track_sd_deg,
            )
            .wrapped_360(),
            ground_speed: Knots(
                initial.ground_speed.0 + normal(rng) * self.scenario.prior_ground_speed_sd_kt,
            ),
            bfo_bias: Hertz(initial.bfo_bias.0 + normal(rng) * self.scenario.prior_bfo_bias_sd_hz),
            ..initial
        };
        if state.ground_speed.0 <= 0.0 {
            return Err(ModelError(SyntheticError::InvalidGroundSpeed));
        }
        Ok(state)
    }

    fn guide_log_likelihood(
        &self,
        state: &Self::State,
        observation: &Self::Observation,
    ) -> Result<f64, Self::Error> {
        let elapsed = observation.time.0 - state.time.0;
        let forecast = propagate_constant_track(*state, mh370_domain::Seconds(elapsed))
            .map_err(SyntheticError::from)?;
        observation_log_likelihood(
            &self.scenario,
            forecast,
            observation,
            self.scenario.guide_inflation,
        )
        .map_err(ModelError)
    }

    fn propose(
        &self,
        state: &Self::State,
        _observation: &Self::Observation,
        elapsed_seconds: f64,
        rng: &mut ChaCha8Rng,
    ) -> Result<Proposal<Self::State>, Self::Error> {
        let state = perturb_and_propagate(&self.scenario, *state, elapsed_seconds, rng)?;
        Ok(Proposal::from_prior(state))
    }

    fn log_likelihood(
        &self,
        state: &Self::State,
        observation: &Self::Observation,
    ) -> Result<f64, Self::Error> {
        observation_log_likelihood(&self.scenario, *state, observation, 1.0).map_err(ModelError)
    }
}

pub fn run_synthetic(configuration: &ExperimentConfig) -> Result<SyntheticRun, SyntheticError> {
    let dataset = simulate_synthetic(configuration)?;
    let model = SyntheticModel {
        scenario: configuration.synthetic.clone(),
    };
    let filter = run_filter(&model, &dataset.observations, &configuration.filter)?;
    let summary = summarize_synthetic(&dataset, &filter, &configuration.validation)?;
    Ok(SyntheticRun {
        dataset,
        filter,
        summary,
    })
}

#[cfg(test)]
mod tests {
    use mh370_particle_filter::{Algorithm, FilterConfig};
    use mh370_satcom::{BfoConstants, BtoConstants};

    use super::*;
    use crate::ValidationThresholds;

    fn configuration(particles: usize) -> ExperimentConfig {
        ExperimentConfig {
            schema_version: 1,
            name: "unit-synthetic".to_string(),
            truth_seed: 32_0101,
            filter: FilterConfig {
                particles,
                seed: 32_1001,
                algorithm: Algorithm::Auxiliary,
                initial_time_s: 0.0,
                ess_resample_fraction: 0.5,
            },
            synthetic: SyntheticScenario {
                epochs: 5,
                epoch_interval_s: 600.0,
                initial_time_s: 0.0,
                initial_latitude_deg: -6.0,
                initial_longitude_deg: 92.0,
                initial_altitude_ft: 35_000.0,
                initial_track_deg: 185.0,
                initial_ground_speed_kt: 480.0,
                initial_vertical_speed_fpm: 0.0,
                initial_bfo_bias_hz: 150.0,
                prior_latitude_sd_deg: 0.7,
                prior_longitude_sd_deg: 0.7,
                prior_track_sd_deg: 8.0,
                prior_ground_speed_sd_kt: 20.0,
                prior_bfo_bias_sd_hz: 25.0,
                process_track_sd_deg_per_sqrt_hour: 0.5,
                process_ground_speed_sd_kt_per_sqrt_hour: 5.0,
                process_bfo_bias_sd_hz_per_sqrt_hour: 1.0,
                bto_sd_us: 29.0,
                bfo_sd_hz: 7.0,
                guide_inflation: 4.0,
                satellite_initial_position_km: Vec3::new(
                    18_161.906_97,
                    38_060.473_36,
                    1_029.903_202,
                ),
                satellite_velocity_km_s: Vec3::new(0.002_195, -0.000_728, -0.045_877),
                ground_station_position_km: Vec3::new(-2_368.8, 4_881.1, -3_342.0),
                bto_constants: BtoConstants {
                    speed_of_light_km_s: 299_792.458,
                    nominal_delay_us: 499_962.0,
                    channel_term_us: 4_283.0,
                },
                bfo_constants: BfoConstants {
                    satellite_afc_hz: -18.075_833_333_333,
                    uplink_hz: 1_646_652_500.0,
                    downlink_hz: 3_615_152_500.0,
                    speed_of_light_km_s: 299_792.458,
                    nominal_satellite_longitude_deg: 64.5,
                    nominal_satellite_altitude_km: 36_210.12,
                },
            },
            validation: ValidationThresholds {
                maximum_final_mean_error_nm: 200.0,
                minimum_mass_within_100_nm: 0.2,
                minimum_final_ess: 10.0,
            },
        }
    }

    #[test]
    fn synthetic_dataset_is_exactly_repeatable() {
        let config = configuration(512);
        assert_eq!(
            simulate_synthetic(&config).unwrap(),
            simulate_synthetic(&config).unwrap()
        );
    }

    #[test]
    fn auxiliary_filter_closes_small_synthetic_fixture() {
        let run = run_synthetic(&configuration(2_048)).unwrap();
        assert!(run.summary.passed, "{:?}", run.summary.failures);
        assert!(run.summary.final_mean_error_nm < 200.0);
        assert_eq!(run.filter.checkpoints.len(), 5);
    }
}
