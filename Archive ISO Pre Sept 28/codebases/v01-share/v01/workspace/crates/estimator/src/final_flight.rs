use std::collections::BTreeMap;

use mh370_domain::{Hertz, ImpactPoint, LatLon};
use mh370_dynamics::{
    canonicalize_one_turn_parameters, mutate_one_turn, one_turn_direct_to_track_at_turn,
    one_turn_log_prior, one_turn_trajectories_at, sample_one_turn, EnvironmentError,
    LateralGuidance, LateralMode, NavigationEnvironment, OneTurnConfig, OneTurnError,
    OneTurnParameters, OneTurnTrajectory, RadarPrior,
};
use mh370_end_of_flight::{project_impact, EndOfFlightConfig, EndOfFlightError};
use mh370_particle_filter::{
    rng_for, run_tempered_smc, Mutation, StaticModel, TemperedCheckpoint, TemperedConfig,
    TemperedError, TemperedResult,
};
use mh370_satcom::{
    evaluate_observation, BfoBiasState, ObservationFit, SatcomModelConfig, SatcomModelError,
};
use rand_chacha::ChaCha8Rng;
use serde::{Deserialize, Serialize};
use thiserror::Error;

use crate::FlightObservation;

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct FinalFlightConfig {
    pub tempering: TemperedConfig,
    pub radar: RadarPrior,
    pub dynamics: OneTurnConfig,
    pub satcom: SatcomModelConfig,
    pub end_of_flight: EndOfFlightConfig,
    pub use_bfo: bool,
}

impl FinalFlightConfig {
    pub fn validate(&self) -> Result<(), FinalFlightError> {
        self.tempering.validate()?;
        self.dynamics.validate(&self.radar)?;
        self.satcom.validate()?;
        self.end_of_flight.validate()?;
        Ok(())
    }
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct FinalFlightParticle {
    pub parameters: OneTurnParameters,
    pub trajectory: OneTurnTrajectory,
    /// Scalar selected control for legacy families; actual initial WGS84
    /// direct-to course at the sampled turn for a fixed-waypoint family.
    pub post_turn_track_true: mh370_domain::Degrees,
    pub bfo_bias: BfoBiasState,
    pub last_fit: Option<ObservationFit>,
}

#[derive(Debug, Clone)]
pub struct FinalFlightRun {
    pub seed: u64,
    pub observations: Vec<FlightObservation>,
    pub filter: TemperedResult<OneTurnParameters>,
    pub posterior: Vec<FinalFlightParticle>,
    pub impacts: Vec<ImpactPoint>,
    pub summary: FinalFlightSummary,
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct FinalFlightSummary {
    pub model_scope: String,
    pub particles: usize,
    pub observations: usize,
    pub use_bfo: bool,
    pub lateral_mode: LateralMode,
    pub environment_applied: bool,
    pub weather_applied: bool,
    pub magnetic_declination_applied: bool,
    pub seed: u64,
    pub log_evidence: f64,
    pub posterior_ess: f64,
    pub temperature_steps: usize,
    pub minimum_tempered_ess: f64,
    pub minimum_mutation_acceptance: Option<f64>,
    pub last_contact_mean: LatLon,
    pub impact_mean: LatLon,
    pub impact_latitude_50_deg: [f64; 2],
    pub impact_latitude_90_deg: [f64; 2],
    pub impact_longitude_50_deg: [f64; 2],
    pub impact_longitude_90_deg: [f64; 2],
    pub impact_displacement_90_nm: [f64; 2],
    pub turn_time_90_s: [f64; 2],
    pub post_turn_track_90_deg_true: [f64; 2],
    pub mach_90: [f64; 2],
    pub altitude_90_ft: [f64; 2],
    pub checkpoints: Vec<TemperedCheckpoint>,
    pub limitations: Vec<String>,
}

#[derive(Debug, Error)]
pub enum FinalFlightError {
    #[error("at least one accident observation is required")]
    NoObservations,
    #[error("accident observations are not ordered or precede the radar state")]
    ObservationOrder,
    #[error(transparent)]
    Dynamics(#[from] OneTurnError),
    #[error(transparent)]
    Satcom(#[from] SatcomModelError),
    #[error(transparent)]
    Filter(#[from] TemperedError),
    #[error(transparent)]
    EndOfFlight(#[from] EndOfFlightError),
    #[error("additional flight likelihood failed: {0}")]
    AdditionalLikelihood(String),
}

/// Narrow composition point for optional evidence owned by the runner.
///
/// Implementations receive the propagated trajectory at an existing SATCOM
/// epoch. This keeps optional scientific spokes out of the estimator crate and
/// prevents them from reaching into one another.
pub trait FinalFlightLikelihood: Sync {
    fn log_likelihood(
        &self,
        trajectory: &OneTurnTrajectory,
        observation: &FlightObservation,
    ) -> Result<f64, String>;
}

#[derive(Clone)]
struct FinalFlightModel<'a> {
    config: FinalFlightConfig,
    observations: Vec<FlightObservation>,
    observation_times_s: Vec<f64>,
    additional_likelihood: Option<&'a dyn FinalFlightLikelihood>,
    environment: Option<NavigationEnvironment<'a>>,
}

impl FinalFlightModel<'_> {
    fn lateral_guidance(&self) -> LateralGuidance {
        self.environment
            .map(|environment| environment.lateral_guidance)
            .unwrap_or_default()
    }

    fn evaluate(
        &self,
        parameters: OneTurnParameters,
        materialize_guidance_metadata: bool,
    ) -> Result<(f64, FinalFlightParticle), FinalFlightError> {
        let mut bias = self.config.satcom.initial_bias();
        let mut total = 0.0;
        let mut trajectory = None;
        let mut last_fit = None;
        let trajectories = one_turn_trajectories_at(
            parameters,
            &self.config.radar,
            &self.config.dynamics,
            &self.observation_times_s,
            bias.mean_hz,
            self.environment,
        )?;
        for (observation, mut state) in self.observations.iter().zip(trajectories) {
            let fit = evaluate_observation(
                state.aircraft,
                &mut bias,
                &observation.measurement,
                observation.satellite_afc_hz,
                self.config.use_bfo,
                &self.config.satcom,
            )?;
            state.aircraft.bfo_bias = Hertz(bias.mean_hz);
            total += fit.log_likelihood;
            if let Some(additional) = self.additional_likelihood {
                total += additional
                    .log_likelihood(&state, observation)
                    .map_err(FinalFlightError::AdditionalLikelihood)?;
            }
            trajectory = Some(state);
            last_fit = Some(fit);
        }
        let post_turn_track_true = match (self.lateral_guidance(), materialize_guidance_metadata) {
            (LateralGuidance::DirectTo(_), true) => one_turn_direct_to_track_at_turn(
                parameters,
                &self.config.radar,
                &self.config.dynamics,
                self.environment
                    .expect("direct-to guidance requires an environment"),
            )?,
            // The zero value is the explicitly documented inactive internal
            // sentinel and this particle is discarded by likelihood-only calls.
            (LateralGuidance::DirectTo(_), false) => mh370_domain::Degrees(0.0),
            (LateralGuidance::SelectedControl(_), _) => {
                mh370_domain::Degrees(parameters.post_turn_track_true_deg).wrapped_360()
            }
        };
        Ok((
            total,
            FinalFlightParticle {
                parameters,
                trajectory: trajectory.ok_or(FinalFlightError::NoObservations)?,
                post_turn_track_true,
                bfo_bias: bias,
                last_fit,
            },
        ))
    }
}

impl StaticModel for FinalFlightModel<'_> {
    type State = OneTurnParameters;
    type Error = FinalFlightError;

    fn initialize(
        &self,
        _particle_index: usize,
        rng: &mut ChaCha8Rng,
    ) -> Result<Self::State, Self::Error> {
        Ok(canonicalize_one_turn_parameters(
            sample_one_turn(&self.config.radar, &self.config.dynamics, rng)?,
            self.lateral_guidance(),
        ))
    }

    fn log_prior(&self, state: &Self::State) -> Result<f64, Self::Error> {
        Ok(one_turn_log_prior(
            state,
            &self.config.radar,
            &self.config.dynamics,
        )?)
    }

    fn log_likelihood(&self, state: &Self::State) -> Result<f64, Self::Error> {
        match self.evaluate(*state, false) {
            Ok(result) => Ok(result.0),
            Err(FinalFlightError::Dynamics(OneTurnError::Environment(
                EnvironmentError::OutsideDomain,
            ))) => Ok(f64::NEG_INFINITY),
            Err(error) => Err(error),
        }
    }

    fn mutate(
        &self,
        state: &Self::State,
        scale: f64,
        rng: &mut ChaCha8Rng,
    ) -> Result<Mutation<Self::State>, Self::Error> {
        Ok(Mutation::symmetric(canonicalize_one_turn_parameters(
            mutate_one_turn(
                *state,
                &self.config.radar,
                &self.config.dynamics,
                scale,
                rng,
            )?,
            self.lateral_guidance(),
        )))
    }
}

fn weighted_quantiles(values: &[f64], weights: &[f64], probabilities: &[f64]) -> Vec<f64> {
    let mut pairs = values
        .iter()
        .copied()
        .zip(weights.iter().copied())
        .collect::<Vec<_>>();
    pairs.sort_by(|first, second| first.0.total_cmp(&second.0));
    let mut cumulative = 0.0;
    let mut target = 0usize;
    let mut output = Vec::with_capacity(probabilities.len());
    for (value, weight) in pairs {
        cumulative += weight;
        while target < probabilities.len() && cumulative >= probabilities[target] {
            output.push(value);
            target += 1;
        }
    }
    while output.len() < probabilities.len() {
        output.push(*values.last().unwrap_or(&f64::NAN));
    }
    output
}

fn weighted_position(positions: &[LatLon], weights: &[f64]) -> LatLon {
    let latitude = positions
        .iter()
        .zip(weights)
        .map(|(position, weight)| position.latitude.0 * weight)
        .sum::<f64>();
    let sine = positions
        .iter()
        .zip(weights)
        .map(|(position, weight)| position.longitude.to_radians().sin() * weight)
        .sum::<f64>();
    let cosine = positions
        .iter()
        .zip(weights)
        .map(|(position, weight)| position.longitude.to_radians().cos() * weight)
        .sum::<f64>();
    LatLon::new(latitude, sine.atan2(cosine).to_degrees())
        .expect("weighted posterior position is valid")
}

fn interval(values: &[f64], weights: &[f64], low: f64, high: f64) -> [f64; 2] {
    let values = weighted_quantiles(values, weights, &[low, high]);
    [values[0], values[1]]
}

fn summarize(
    run: &TemperedResult<OneTurnParameters>,
    posterior: &[FinalFlightParticle],
    impacts: &[ImpactPoint],
    observations: usize,
    use_bfo: bool,
    seed: u64,
    lateral_mode: LateralMode,
    environment_applied: bool,
) -> Result<FinalFlightSummary, FinalFlightError> {
    let weights = run.normalized_weights();
    let last_positions = posterior
        .iter()
        .map(|particle| particle.trajectory.aircraft.position)
        .collect::<Vec<_>>();
    let impact_positions = impacts
        .iter()
        .map(|impact| impact.position)
        .collect::<Vec<_>>();
    let latitudes = impact_positions
        .iter()
        .map(|position| position.latitude.0)
        .collect::<Vec<_>>();
    let longitudes = impact_positions
        .iter()
        .map(|position| position.longitude.0)
        .collect::<Vec<_>>();
    let displacements = impacts
        .iter()
        .map(|impact| impact.displacement_from_last_contact.0)
        .collect::<Vec<_>>();
    let turn_times = posterior
        .iter()
        .map(|particle| particle.parameters.turn_time_s)
        .collect::<Vec<_>>();
    let tracks = posterior
        .iter()
        .map(|particle| particle.post_turn_track_true.0)
        .collect::<Vec<_>>();
    let mach = posterior
        .iter()
        .map(|particle| particle.parameters.mach)
        .collect::<Vec<_>>();
    let altitudes = posterior
        .iter()
        .map(|particle| particle.parameters.altitude_ft)
        .collect::<Vec<_>>();
    let minimum_ess = run
        .checkpoints
        .iter()
        .map(|checkpoint| checkpoint.particle_ess)
        .fold(f64::INFINITY, f64::min);
    let minimum_acceptance = run
        .checkpoints
        .iter()
        .filter_map(|checkpoint| checkpoint.mutation_acceptance)
        .min_by(f64::total_cmp);
    let magnetic_declination_applied = environment_applied
        && matches!(
            lateral_mode,
            LateralMode::ConstantMagneticHeading | LateralMode::ConstantMagneticTrack
        );
    let environment_statement = if environment_applied && magnetic_declination_applied {
        "ERA5 temperature/wind and east-positive IGRF-14 declination are active and interpolated along each trajectory."
    } else if environment_applied {
        "ERA5 temperature/wind is active; IGRF-14 declination is inactive for this true-reference lateral guidance."
    } else {
        "Historical wind and magnetic variation are not applied in this model family."
    };

    Ok(FinalFlightSummary {
        model_scope: format!("one-turn {} model-conditional estimate", lateral_mode.name()),
        particles: posterior.len(),
        observations,
        use_bfo,
        lateral_mode,
        environment_applied,
        weather_applied: environment_applied,
        magnetic_declination_applied,
        seed,
        log_evidence: run.log_evidence,
        posterior_ess: run.effective_sample_size()?,
        temperature_steps: run.checkpoints.len(),
        minimum_tempered_ess: minimum_ess,
        minimum_mutation_acceptance: minimum_acceptance,
        last_contact_mean: weighted_position(&last_positions, &weights),
        impact_mean: weighted_position(&impact_positions, &weights),
        impact_latitude_50_deg: interval(&latitudes, &weights, 0.25, 0.75),
        impact_latitude_90_deg: interval(&latitudes, &weights, 0.05, 0.95),
        impact_longitude_50_deg: interval(&longitudes, &weights, 0.25, 0.75),
        impact_longitude_90_deg: interval(&longitudes, &weights, 0.05, 0.95),
        impact_displacement_90_nm: interval(&displacements, &weights, 0.05, 0.95),
        turn_time_90_s: interval(&turn_times, &weights, 0.05, 0.95),
        post_turn_track_90_deg_true: interval(&tracks, &weights, 0.05, 0.95),
        mach_90: interval(&mach, &weights, 0.05, 0.95),
        altitude_90_ft: interval(&altitudes, &weights, 0.05, 0.95),
        checkpoints: run.checkpoints.clone(),
        limitations: vec![
            "The numerical radar mean is reconstructed; its original covariance is unavailable."
                .to_string(),
            format!(
                "The trajectory assumes one instantaneous turn followed by {}, constant Mach, and constant altitude.",
                lateral_mode.name()
            ),
            environment_statement.to_string(),
            "Fuel state and the proprietary satellite correction series remain unavailable."
                .to_string(),
            "The final two BFO values are excluded; end-of-flight displacement is a separately named conditional model."
                .to_string(),
        ],
    })
}

pub fn run_final_flight_estimate(
    config: &FinalFlightConfig,
    observations: &[FlightObservation],
) -> Result<FinalFlightRun, FinalFlightError> {
    run_final_flight_estimate_with_environment_and_likelihood(config, observations, None, None)
}

pub fn run_final_flight_estimate_with_likelihood(
    config: &FinalFlightConfig,
    observations: &[FlightObservation],
    additional_likelihood: Option<&dyn FinalFlightLikelihood>,
) -> Result<FinalFlightRun, FinalFlightError> {
    run_final_flight_estimate_with_environment_and_likelihood(
        config,
        observations,
        None,
        additional_likelihood,
    )
}

pub fn run_final_flight_estimate_with_environment_and_likelihood<'a>(
    config: &FinalFlightConfig,
    observations: &[FlightObservation],
    environment: Option<NavigationEnvironment<'a>>,
    additional_likelihood: Option<&'a dyn FinalFlightLikelihood>,
) -> Result<FinalFlightRun, FinalFlightError> {
    config.validate()?;
    if observations.is_empty() {
        return Err(FinalFlightError::NoObservations);
    }
    if observations
        .iter()
        .scan(config.radar.time_s, |previous, observation| {
            let valid = observation.measurement.time.0 >= *previous;
            *previous = observation.measurement.time.0;
            Some(valid)
        })
        .any(|valid| !valid)
    {
        return Err(FinalFlightError::ObservationOrder);
    }
    let model = FinalFlightModel {
        config: config.clone(),
        observations: observations.to_vec(),
        observation_times_s: observations
            .iter()
            .map(|observation| observation.measurement.time.0)
            .collect(),
        additional_likelihood,
        environment,
    };
    let filter = run_tempered_smc(&model, &config.tempering)?;
    let posterior = filter
        .particles
        .iter()
        .map(|parameters| model.evaluate(*parameters, true).map(|result| result.1))
        .collect::<Result<Vec<_>, _>>()?;
    let mut impacts = Vec::with_capacity(posterior.len());
    for (particle, value) in posterior.iter().enumerate() {
        let mut rng = rng_for(
            config.tempering.seed,
            "end-of-flight",
            observations.len(),
            particle,
            0,
        );
        impacts.push(project_impact(
            value.trajectory.aircraft,
            &config.end_of_flight,
            &mut rng,
        )?);
    }
    let summary = summarize(
        &filter,
        &posterior,
        &impacts,
        observations.len(),
        config.use_bfo,
        config.tempering.seed,
        environment
            .map(|value| value.lateral_guidance.lateral_mode())
            .unwrap_or_default(),
        environment.is_some(),
    )?;
    Ok(FinalFlightRun {
        seed: config.tempering.seed,
        observations: observations.to_vec(),
        filter,
        posterior,
        impacts,
        summary,
    })
}

pub fn final_posterior_rows(
    run: &FinalFlightRun,
) -> impl Iterator<Item = (&FinalFlightParticle, &ImpactPoint, f64)> {
    run.posterior
        .iter()
        .zip(&run.impacts)
        .zip(&run.filter.log_weights)
        .map(|((particle, impact), weight)| (particle, impact, weight.exp()))
}

pub fn parameter_names() -> BTreeMap<&'static str, &'static str> {
    BTreeMap::from([
        ("turn_time_s", "seconds from the radar epoch"),
        ("post_turn_track_true_deg", "degrees true"),
        ("mach", "dimensionless"),
        ("altitude_ft", "feet"),
    ])
}

#[cfg(test)]
mod tests {
    use mh370_domain::{Microseconds, SatcomObservation, Seconds, Vec3};
    use mh370_end_of_flight::EndOfFlightMode;
    use mh370_satcom::{BfoConstants, BtoConstants};

    use super::*;

    fn config() -> FinalFlightConfig {
        FinalFlightConfig {
            tempering: TemperedConfig {
                particles: 512,
                seed: 370,
                target_ess_fraction: 0.75,
                mutation_steps: 3,
                mutation_scale: 0.08,
                maximum_mutation_scale: 0.08,
                minimum_temperature_increment: 0.01,
                maximum_temperature_steps: 80,
            },
            radar: RadarPrior {
                time_s: 0.0,
                latitude_deg: 5.6,
                longitude_deg: 99.0,
                position_sd_nm: 0.5,
                control_mean_deg_true: 295.0,
                control_sd_deg: 1.0,
                mach_min: 0.73,
                mach_max: 0.84,
                altitude_min_ft: 25_000.0,
                altitude_max_ft: 43_000.0,
            },
            dynamics: OneTurnConfig {
                turn_time_min_s: 10.0,
                turn_time_max_s: 50.0,
            },
            satcom: SatcomModelConfig {
                bto: BtoConstants {
                    speed_of_light_km_s: 299_792.458,
                    nominal_delay_us: 499_962.0,
                    channel_term_us: 4_283.0,
                },
                bfo: BfoConstants {
                    satellite_afc_hz: 0.0,
                    uplink_hz: 1_646_652_500.0,
                    downlink_hz: 3_615_152_500.0,
                    speed_of_light_km_s: 299_792.458,
                    nominal_satellite_longitude_deg: 64.5,
                    nominal_satellite_altitude_km: 36_210.12,
                },
                bfo_bias_prior_mean_hz: 150.0,
                bfo_bias_prior_sd_hz: 25.0,
            },
            end_of_flight: EndOfFlightConfig {
                mode: EndOfFlightMode::LastContact,
                minimum_along_track_nm: 0.0,
                maximum_along_track_nm: 0.0,
                cross_track_sd_nm: 0.0,
                minimum_delay_seconds: 0.0,
                maximum_delay_seconds: 0.0,
            },
            use_bfo: false,
        }
    }

    fn observations() -> Vec<FlightObservation> {
        vec![FlightObservation {
            id: "wide-fixture".to_string(),
            time_utc: "t".to_string(),
            satellite_afc_hz: 0.0,
            measurement: SatcomObservation {
                time: Seconds(60.0),
                satellite_position_km: Vec3::new(18_161.0, 38_060.0, 1_029.0),
                satellite_velocity_km_s: Vec3::new(0.002, -0.001, -0.046),
                ground_station_position_km: Vec3::new(-2_368.8, 4_881.1, -3_342.0),
                bto: Some(Microseconds(12_000.0)),
                bto_sd: Some(Microseconds(100_000.0)),
                bfo: None,
                bfo_sd: None,
            },
        }]
    }

    #[test]
    fn final_flight_sampler_is_deterministic_and_finite() {
        let first = run_final_flight_estimate(&config(), &observations()).unwrap();
        let second = run_final_flight_estimate(&config(), &observations()).unwrap();
        assert_eq!(first.summary, second.summary);
        assert!(first.summary.log_evidence.is_finite());
        assert!(first.summary.posterior_ess > 350.0);
        assert_eq!(first.posterior.len(), 512);
    }
}
