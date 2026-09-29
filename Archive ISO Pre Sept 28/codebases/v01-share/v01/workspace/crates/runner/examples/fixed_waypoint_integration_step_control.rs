//! Actual-grid integration-step control for conditional fixed-waypoint fits.
//!
//! This focused control uses the canonical one-turn dynamics, actual ERA5 and
//! IGRF fixtures, both declared waypoint routes, every fitted SATCOM epoch,
//! and a deterministic envelope of posterior-relevant state parameters. It
//! compares 600/300/60 second propagation with a 30 second reference and
//! selects the largest step meeting predeclared numerical thresholds.

use std::{
    collections::BTreeMap,
    env, fs,
    path::{Path, PathBuf},
};

use anyhow::{bail, Context, Result};
use clap::Parser;
use mh370_domain::{great_circle_distance_nm, Hertz, LatLon, NauticalMiles, Vec3};
use mh370_dynamics::{
    one_turn_trajectories_at, Era5Grid, FixedWaypointLeg, IgrfGrid, LateralGuidance,
    NavigationEnvironment, OneTurnConfig, OneTurnParameters, OneTurnTrajectory, RadarPrior,
};
use mh370_estimator::{parse_satcom_observations, FixedWaypointMetadata, FlightObservation};
use mh370_satcom::{evaluate_observation, SatcomModelConfig};
use serde::{Deserialize, Serialize};
use sha2::{Digest, Sha256};

const RESULT_NAME: &str = "fixed_waypoint_integration_step_control.json";
const CSV_NAME: &str = "fixed_waypoint_integration_step_control.csv";
const MANIFEST_NAME: &str = "fixed_waypoint_integration_step_control_manifest.json";
const RESULT_SCHEMA_VERSION: u32 = 1;
const MANIFEST_SCHEMA_VERSION: u32 = 1;
const REFERENCE_STEP_S: f64 = 30.0;
const STEPS_S: [f64; 4] = [600.0, 300.0, 60.0, 30.0];
const POSTERIOR_RELEVANCE_LOG_LIKELIHOOD_DROP: f64 = 25.0;

#[derive(Debug, Parser)]
#[command(about = "Select a production integration step for fixed-waypoint conditionals")]
struct Arguments {
    #[arg(
        long,
        default_value = "configs/mh370-through-0011-fixed-waypoint-conditionals-medium.toml"
    )]
    suite_config: PathBuf,
    #[arg(
        long,
        default_value = "runs/mh370/fixed-waypoint-integration-step-control"
    )]
    output: PathBuf,
}

#[derive(Debug, Deserialize)]
struct SuiteConfiguration {
    schema_version: u32,
    name: String,
    inputs: InputConfiguration,
    families: Vec<FamilyConfiguration>,
    model: ModelConfiguration,
    environment: EnvironmentConfiguration,
}

#[derive(Debug, Deserialize)]
struct InputConfiguration {
    observations: PathBuf,
    satellite_ephemeris: PathBuf,
    ground_station_position_km: Vec3,
    fit_through_epoch_id: Option<String>,
}

#[derive(Debug, Deserialize)]
struct ModelConfiguration {
    radar: RadarPrior,
    dynamics: OneTurnConfig,
    satcom: SatcomModelConfig,
}

#[derive(Debug, Deserialize)]
struct EnvironmentConfiguration {
    era5: PathBuf,
    igrf: PathBuf,
    time_origin_unix_s: f64,
    integration_step_s: f64,
}

#[derive(Debug, Deserialize)]
struct FamilyConfiguration {
    name: String,
    use_bfo: bool,
    bfo_sd_override_hz: Option<f64>,
    lateral_mode: mh370_dynamics::LateralMode,
    fixed_waypoint: Option<FixedWaypointConfiguration>,
}

#[derive(Debug, Clone, Deserialize)]
#[serde(deny_unknown_fields)]
struct FixedWaypointConfiguration {
    target_name: String,
    latitude_deg: f64,
    longitude_deg: f64,
    arrival_radius_nm: f64,
    coordinate_source_title: String,
    coordinate_source_uri: String,
    coordinate_frame_assumption: String,
    coordinate_source_date: Option<String>,
    coordinate_note: String,
}

impl FixedWaypointConfiguration {
    fn metadata(&self) -> Result<FixedWaypointMetadata> {
        Ok(FixedWaypointMetadata {
            target_name: self.target_name.clone(),
            position: LatLon::new(self.latitude_deg, self.longitude_deg)?,
            arrival_radius: NauticalMiles(self.arrival_radius_nm),
            coordinate_source_title: self.coordinate_source_title.clone(),
            coordinate_source_uri: self.coordinate_source_uri.clone(),
            coordinate_frame_assumption: self.coordinate_frame_assumption.clone(),
            coordinate_source_date: self.coordinate_source_date.clone(),
            coordinate_note: self.coordinate_note.clone(),
        })
    }
}

#[derive(Debug, Clone, Serialize)]
struct ParameterEnvelope {
    initial_position: LatLon,
    initial_track_true_deg: Vec<f64>,
    turn_time_s: Vec<f64>,
    mach: Vec<f64>,
    altitude_ft: Vec<f64>,
    combinations_per_route: usize,
    posterior_relevance_rule: String,
}

impl ParameterEnvelope {
    fn from_radar(radar: &RadarPrior) -> Result<Self> {
        let initial_position = LatLon::new(radar.latitude_deg, radar.longitude_deg)?;
        let initial_track_true_deg = vec![
            radar.control_mean_deg_true - 1.66,
            radar.control_mean_deg_true,
            radar.control_mean_deg_true + 1.64,
        ];
        let turn_time_s = vec![1_800.0, 2_250.0, 2_700.0];
        let mach = vec![0.75, 0.795, 0.84];
        let altitude_ft = vec![26_000.0, 34_500.0, 43_000.0];
        let combinations_per_route =
            initial_track_true_deg.len() * turn_time_s.len() * mach.len() * altitude_ft.len();
        Ok(Self {
            initial_position,
            initial_track_true_deg,
            turn_time_s,
            mach,
            altitude_ft,
            combinations_per_route,
            posterior_relevance_rule: format!(
                "30 s total BTO+BFO log likelihood no more than {POSTERIOR_RELEVANCE_LOG_LIKELIHOOD_DROP} natural-log units below the best envelope point for that route"
            ),
        })
    }

    fn parameters(&self) -> Vec<OneTurnParameters> {
        let mut output = Vec::with_capacity(self.combinations_per_route);
        for initial_track_true_deg in &self.initial_track_true_deg {
            for turn_time_s in &self.turn_time_s {
                for mach in &self.mach {
                    for altitude_ft in &self.altitude_ft {
                        output.push(OneTurnParameters {
                            initial_latitude_deg: self.initial_position.latitude.0,
                            initial_longitude_deg: self.initial_position.longitude.0,
                            initial_track_true_deg: *initial_track_true_deg,
                            turn_time_s: *turn_time_s,
                            post_turn_track_true_deg: 0.0,
                            mach: *mach,
                            altitude_ft: *altitude_ft,
                        });
                    }
                }
            }
        }
        output
    }
}

#[derive(Debug, Clone, Serialize)]
struct Thresholds {
    maximum_bto_difference_us: f64,
    maximum_bfo_difference_hz: f64,
    maximum_endpoint_separation_nm: f64,
    maximum_posterior_relevant_log_likelihood_difference: f64,
    maximum_partition_endpoint_separation_nm: f64,
    maximum_partition_track_difference_deg: f64,
}

impl Default for Thresholds {
    fn default() -> Self {
        Self {
            maximum_bto_difference_us: 1.0,
            maximum_bfo_difference_hz: 0.1,
            maximum_endpoint_separation_nm: 0.5,
            maximum_posterior_relevant_log_likelihood_difference: 0.05,
            maximum_partition_endpoint_separation_nm: 1e-6,
            maximum_partition_track_difference_deg: 1e-9,
        }
    }
}

#[derive(Debug)]
struct Evaluation {
    trajectories: Vec<OneTurnTrajectory>,
    predicted_bto_us: Vec<Option<f64>>,
    predicted_bfo_without_bias_hz: Vec<Option<f64>>,
    total_log_likelihood: f64,
    partition_last_only_separation_nm: f64,
    partition_extra_epoch_separation_nm: f64,
    partition_last_only_track_difference_deg: f64,
    partition_extra_epoch_track_difference_deg: f64,
}

#[derive(Debug, Clone, Serialize)]
struct StepComparison {
    route_family: String,
    route: FixedWaypointMetadata,
    step_s: f64,
    reference_step_s: f64,
    parameter_combinations: usize,
    posterior_relevant_combinations: usize,
    maximum_position_separation_across_epochs_nm: f64,
    maximum_endpoint_separation_nm: f64,
    maximum_true_track_difference_deg: f64,
    maximum_true_heading_difference_deg: f64,
    maximum_predicted_bto_difference_us: f64,
    maximum_predicted_bfo_without_bias_difference_hz: f64,
    maximum_total_log_likelihood_difference_all_envelope: f64,
    maximum_total_log_likelihood_difference_posterior_relevant: f64,
    maximum_partition_last_only_endpoint_separation_nm: f64,
    maximum_partition_extra_epoch_endpoint_separation_nm: f64,
    maximum_partition_last_only_track_difference_deg: f64,
    maximum_partition_extra_epoch_track_difference_deg: f64,
    passes: bool,
}

#[derive(Debug, Serialize)]
struct ControlResult {
    schema_version: u32,
    name: &'static str,
    status: &'static str,
    suite_name: String,
    suite_config_schema_version: u32,
    input_set_sha256: String,
    input_sha256: BTreeMap<String, String>,
    fitted_epoch_ids: Vec<String>,
    fitted_epoch_times_s: Vec<f64>,
    tested_steps_s: Vec<f64>,
    reference_step_s: f64,
    envelope: ParameterEnvelope,
    thresholds: Thresholds,
    comparisons: Vec<StepComparison>,
    chosen_production_step_s: Option<f64>,
    configured_production_step_s: f64,
    configured_step_matches_chosen: bool,
    decision_rule: &'static str,
    scientific_scope: Vec<String>,
}

#[derive(Debug, Serialize)]
struct OutputManifest {
    schema_version: u32,
    result_schema_version: u32,
    generator: String,
    generator_source_sha256: String,
    executable_sha256: String,
    input_set_sha256: String,
    input_sha256: BTreeMap<String, String>,
    output_sha256: BTreeMap<String, String>,
    reproduction_command: String,
}

fn resolve(configuration: &Path, value: &Path) -> PathBuf {
    if value.is_absolute() {
        value.to_path_buf()
    } else {
        configuration
            .parent()
            .unwrap_or_else(|| Path::new("."))
            .join(value)
    }
}

fn sha256_bytes(bytes: &[u8]) -> String {
    hex::encode(Sha256::digest(bytes))
}

fn read_hashed(path: &Path, label: &str, hashes: &mut BTreeMap<String, String>) -> Result<Vec<u8>> {
    let bytes =
        fs::read(path).with_context(|| format!("cannot read {label} {}", path.display()))?;
    hashes.insert(label.to_string(), sha256_bytes(&bytes));
    Ok(bytes)
}

fn atomic_write(path: &Path, bytes: &[u8]) -> Result<()> {
    let temporary = path.with_extension("tmp");
    fs::write(&temporary, bytes)
        .with_context(|| format!("cannot write {}", temporary.display()))?;
    fs::rename(&temporary, path).with_context(|| format!("cannot replace {}", path.display()))?;
    Ok(())
}

fn angular_difference_deg(first: f64, second: f64) -> f64 {
    (first - second + 180.0).rem_euclid(360.0) - 180.0
}

fn diagnostic_time(times: &[f64]) -> Result<f64> {
    for pair in times.windows(2).rev() {
        let value = 0.5 * (pair[0] + pair[1]);
        if value > pair[0] && value < pair[1] {
            return Ok(value);
        }
    }
    bail!("cannot construct an interior diagnostic epoch")
}

fn evaluate(
    parameters: OneTurnParameters,
    route: &FixedWaypointMetadata,
    step_s: f64,
    observations: &[FlightObservation],
    bfo_sd_override_hz: Option<f64>,
    use_bfo: bool,
    model: &ModelConfiguration,
    weather: &Era5Grid,
    magnetic: &IgrfGrid,
    environment: &EnvironmentConfiguration,
) -> Result<Evaluation> {
    let times = observations
        .iter()
        .map(|observation| observation.measurement.time.0)
        .collect::<Vec<_>>();
    let guidance =
        LateralGuidance::DirectTo(FixedWaypointLeg::new(route.position, route.arrival_radius)?);
    let navigation = NavigationEnvironment {
        weather,
        magnetic,
        time_origin_unix_s: environment.time_origin_unix_s,
        integration_step_s: step_s,
        lateral_guidance: guidance,
    };
    let trajectories = one_turn_trajectories_at(
        parameters,
        &model.radar,
        &model.dynamics,
        &times,
        model.satcom.bfo_bias_prior_mean_hz,
        Some(navigation),
    )?;

    let last_time = *times.last().context("observation times are empty")?;
    let last_only = one_turn_trajectories_at(
        parameters,
        &model.radar,
        &model.dynamics,
        &[last_time],
        model.satcom.bfo_bias_prior_mean_hz,
        Some(navigation),
    )?[0];
    let mut extra_times = times.clone();
    extra_times.push(diagnostic_time(&times)?);
    extra_times.sort_by(f64::total_cmp);
    let with_extra = one_turn_trajectories_at(
        parameters,
        &model.radar,
        &model.dynamics,
        &extra_times,
        model.satcom.bfo_bias_prior_mean_hz,
        Some(navigation),
    )?;
    let extra_last = *with_extra
        .last()
        .context("extra-epoch trajectories are empty")?;
    let full_last = *trajectories.last().context("trajectories are empty")?;

    let mut bias = model.satcom.initial_bias();
    let mut predicted_bto_us = Vec::with_capacity(observations.len());
    let mut predicted_bfo_without_bias_hz = Vec::with_capacity(observations.len());
    let mut total_log_likelihood = 0.0;
    for (trajectory, observation) in trajectories.iter().zip(observations) {
        let mut measurement = observation.measurement.clone();
        if measurement.bfo.is_some() {
            if let Some(sd) = bfo_sd_override_hz {
                measurement.bfo_sd = Some(Hertz(sd));
            }
        }
        let fit = evaluate_observation(
            trajectory.aircraft,
            &mut bias,
            &measurement,
            observation.satellite_afc_hz,
            use_bfo,
            &model.satcom,
        )?;
        total_log_likelihood += fit.log_likelihood;
        predicted_bto_us.push(fit.predicted_bto_us);
        predicted_bfo_without_bias_hz.push(fit.predicted_bfo_without_bias_hz);
    }

    Ok(Evaluation {
        trajectories,
        predicted_bto_us,
        predicted_bfo_without_bias_hz,
        total_log_likelihood,
        partition_last_only_separation_nm: great_circle_distance_nm(
            full_last.aircraft.position,
            last_only.aircraft.position,
        )
        .0,
        partition_extra_epoch_separation_nm: great_circle_distance_nm(
            full_last.aircraft.position,
            extra_last.aircraft.position,
        )
        .0,
        partition_last_only_track_difference_deg: angular_difference_deg(
            full_last.aircraft.track_true.0,
            last_only.aircraft.track_true.0,
        )
        .abs(),
        partition_extra_epoch_track_difference_deg: angular_difference_deg(
            full_last.aircraft.track_true.0,
            extra_last.aircraft.track_true.0,
        )
        .abs(),
    })
}

fn compare(
    family: &FamilyConfiguration,
    route: FixedWaypointMetadata,
    step_s: f64,
    parameters: &[OneTurnParameters],
    reference: &[Evaluation],
    reference_best_log_likelihood: f64,
    observations: &[FlightObservation],
    model: &ModelConfiguration,
    weather: &Era5Grid,
    magnetic: &IgrfGrid,
    environment: &EnvironmentConfiguration,
    thresholds: &Thresholds,
) -> Result<StepComparison> {
    let mut maximum_position: f64 = 0.0;
    let mut maximum_endpoint: f64 = 0.0;
    let mut maximum_track: f64 = 0.0;
    let mut maximum_heading: f64 = 0.0;
    let mut maximum_bto: f64 = 0.0;
    let mut maximum_bfo: f64 = 0.0;
    let mut maximum_log_likelihood_all: f64 = 0.0;
    let mut maximum_log_likelihood_relevant: f64 = 0.0;
    let mut maximum_partition_last: f64 = 0.0;
    let mut maximum_partition_extra: f64 = 0.0;
    let mut maximum_partition_last_track: f64 = 0.0;
    let mut maximum_partition_extra_track: f64 = 0.0;
    let mut posterior_relevant_combinations = 0;

    for (parameters, reference) in parameters.iter().copied().zip(reference) {
        let candidate = evaluate(
            parameters,
            &route,
            step_s,
            observations,
            family.bfo_sd_override_hz,
            family.use_bfo,
            model,
            weather,
            magnetic,
            environment,
        )?;
        for (candidate_state, reference_state) in
            candidate.trajectories.iter().zip(&reference.trajectories)
        {
            maximum_position = maximum_position.max(
                great_circle_distance_nm(
                    candidate_state.aircraft.position,
                    reference_state.aircraft.position,
                )
                .0,
            );
            maximum_track = maximum_track.max(
                angular_difference_deg(
                    candidate_state.aircraft.track_true.0,
                    reference_state.aircraft.track_true.0,
                )
                .abs(),
            );
            maximum_heading = maximum_heading.max(
                angular_difference_deg(
                    candidate_state.heading_true.0,
                    reference_state.heading_true.0,
                )
                .abs(),
            );
        }
        maximum_endpoint = maximum_endpoint.max(
            great_circle_distance_nm(
                candidate.trajectories.last().unwrap().aircraft.position,
                reference.trajectories.last().unwrap().aircraft.position,
            )
            .0,
        );
        for (candidate_value, reference_value) in candidate
            .predicted_bto_us
            .iter()
            .zip(&reference.predicted_bto_us)
        {
            if let (Some(candidate_value), Some(reference_value)) =
                (candidate_value, reference_value)
            {
                maximum_bto = maximum_bto.max((candidate_value - reference_value).abs());
            }
        }
        for (candidate_value, reference_value) in candidate
            .predicted_bfo_without_bias_hz
            .iter()
            .zip(&reference.predicted_bfo_without_bias_hz)
        {
            if let (Some(candidate_value), Some(reference_value)) =
                (candidate_value, reference_value)
            {
                maximum_bfo = maximum_bfo.max((candidate_value - reference_value).abs());
            }
        }
        let log_likelihood_difference =
            (candidate.total_log_likelihood - reference.total_log_likelihood).abs();
        maximum_log_likelihood_all = maximum_log_likelihood_all.max(log_likelihood_difference);
        if reference.total_log_likelihood
            >= reference_best_log_likelihood - POSTERIOR_RELEVANCE_LOG_LIKELIHOOD_DROP
        {
            posterior_relevant_combinations += 1;
            maximum_log_likelihood_relevant =
                maximum_log_likelihood_relevant.max(log_likelihood_difference);
        }
        maximum_partition_last =
            maximum_partition_last.max(candidate.partition_last_only_separation_nm);
        maximum_partition_extra =
            maximum_partition_extra.max(candidate.partition_extra_epoch_separation_nm);
        maximum_partition_last_track =
            maximum_partition_last_track.max(candidate.partition_last_only_track_difference_deg);
        maximum_partition_extra_track =
            maximum_partition_extra_track.max(candidate.partition_extra_epoch_track_difference_deg);
    }
    if posterior_relevant_combinations == 0 {
        bail!("posterior-relevance envelope is empty for {}", family.name);
    }
    let passes = maximum_bto <= thresholds.maximum_bto_difference_us
        && maximum_bfo <= thresholds.maximum_bfo_difference_hz
        && maximum_endpoint <= thresholds.maximum_endpoint_separation_nm
        && maximum_log_likelihood_relevant
            <= thresholds.maximum_posterior_relevant_log_likelihood_difference
        && maximum_partition_last <= thresholds.maximum_partition_endpoint_separation_nm
        && maximum_partition_extra <= thresholds.maximum_partition_endpoint_separation_nm
        && maximum_partition_last_track <= thresholds.maximum_partition_track_difference_deg
        && maximum_partition_extra_track <= thresholds.maximum_partition_track_difference_deg;
    Ok(StepComparison {
        route_family: family.name.clone(),
        route,
        step_s,
        reference_step_s: REFERENCE_STEP_S,
        parameter_combinations: parameters.len(),
        posterior_relevant_combinations,
        maximum_position_separation_across_epochs_nm: maximum_position,
        maximum_endpoint_separation_nm: maximum_endpoint,
        maximum_true_track_difference_deg: maximum_track,
        maximum_true_heading_difference_deg: maximum_heading,
        maximum_predicted_bto_difference_us: maximum_bto,
        maximum_predicted_bfo_without_bias_difference_hz: maximum_bfo,
        maximum_total_log_likelihood_difference_all_envelope: maximum_log_likelihood_all,
        maximum_total_log_likelihood_difference_posterior_relevant: maximum_log_likelihood_relevant,
        maximum_partition_last_only_endpoint_separation_nm: maximum_partition_last,
        maximum_partition_extra_epoch_endpoint_separation_nm: maximum_partition_extra,
        maximum_partition_last_only_track_difference_deg: maximum_partition_last_track,
        maximum_partition_extra_epoch_track_difference_deg: maximum_partition_extra_track,
        passes,
    })
}

fn csv(comparisons: &[StepComparison], input_set_sha256: &str) -> String {
    let mut output = String::from(
        "result_schema_version,input_set_sha256,route_family,route_target,route_latitude_deg,route_longitude_deg,step_s,reference_step_s,parameter_combinations,posterior_relevant_combinations,maximum_position_separation_across_epochs_nm,maximum_endpoint_separation_nm,maximum_true_track_difference_deg,maximum_true_heading_difference_deg,maximum_predicted_bto_difference_us,maximum_predicted_bfo_without_bias_difference_hz,maximum_total_log_likelihood_difference_all_envelope,maximum_total_log_likelihood_difference_posterior_relevant,maximum_partition_last_only_endpoint_separation_nm,maximum_partition_extra_epoch_endpoint_separation_nm,maximum_partition_last_only_track_difference_deg,maximum_partition_extra_epoch_track_difference_deg,passes\n",
    );
    for comparison in comparisons {
        output.push_str(&format!(
            "{RESULT_SCHEMA_VERSION},{input_set_sha256},{},{},{:.10},{:.10},{:.0},{:.0},{},{},{:.12},{:.12},{:.12},{:.12},{:.12},{:.12},{:.12},{:.12},{:.12},{:.12},{:.12},{:.12},{}\n",
            comparison.route_family,
            comparison.route.target_name,
            comparison.route.position.latitude.0,
            comparison.route.position.longitude.0,
            comparison.step_s,
            comparison.reference_step_s,
            comparison.parameter_combinations,
            comparison.posterior_relevant_combinations,
            comparison.maximum_position_separation_across_epochs_nm,
            comparison.maximum_endpoint_separation_nm,
            comparison.maximum_true_track_difference_deg,
            comparison.maximum_true_heading_difference_deg,
            comparison.maximum_predicted_bto_difference_us,
            comparison.maximum_predicted_bfo_without_bias_difference_hz,
            comparison.maximum_total_log_likelihood_difference_all_envelope,
            comparison.maximum_total_log_likelihood_difference_posterior_relevant,
            comparison.maximum_partition_last_only_endpoint_separation_nm,
            comparison.maximum_partition_extra_epoch_endpoint_separation_nm,
            comparison.maximum_partition_last_only_track_difference_deg,
            comparison.maximum_partition_extra_epoch_track_difference_deg,
            comparison.passes,
        ));
    }
    output
}

fn main() -> Result<()> {
    let arguments = Arguments::parse();
    let mut input_sha256 = BTreeMap::new();
    let suite_bytes = read_hashed(&arguments.suite_config, "suite_config", &mut input_sha256)?;
    let suite: SuiteConfiguration =
        toml::from_str(std::str::from_utf8(&suite_bytes).context("suite config is not UTF-8")?)?;
    if suite.schema_version != 2 || suite.name.trim().is_empty() {
        bail!("control requires the schema-v2 fixed-waypoint suite");
    }
    suite.model.radar.validate()?;
    suite.model.dynamics.validate(&suite.model.radar)?;
    suite.model.satcom.validate()?;
    if !suite.environment.integration_step_s.is_finite()
        || suite.environment.integration_step_s <= 0.0
        || !suite.environment.time_origin_unix_s.is_finite()
    {
        bail!("suite environment is invalid");
    }
    let routes = suite
        .families
        .iter()
        .filter(|family| family.lateral_mode == mh370_dynamics::LateralMode::LateralNavigation)
        .map(|family| {
            let route = family
                .fixed_waypoint
                .as_ref()
                .with_context(|| format!("{} lacks fixed waypoint", family.name))?
                .metadata()?;
            Ok((family, route))
        })
        .collect::<Result<Vec<_>>>()?;
    if routes.len() != 2 {
        bail!("control requires exactly the two primary fixed-waypoint families");
    }

    let observation_path = resolve(&arguments.suite_config, &suite.inputs.observations);
    let ephemeris_path = resolve(&arguments.suite_config, &suite.inputs.satellite_ephemeris);
    let era5_path = resolve(&arguments.suite_config, &suite.environment.era5);
    let igrf_path = resolve(&arguments.suite_config, &suite.environment.igrf);
    let observation_bytes = read_hashed(&observation_path, "observations", &mut input_sha256)?;
    let ephemeris_bytes = read_hashed(&ephemeris_path, "satellite_ephemeris", &mut input_sha256)?;
    let era5_bytes = read_hashed(&era5_path, "era5", &mut input_sha256)?;
    let igrf_bytes = read_hashed(&igrf_path, "igrf", &mut input_sha256)?;
    let observations = parse_satcom_observations(
        std::str::from_utf8(&observation_bytes)?,
        std::str::from_utf8(&ephemeris_bytes)?,
        suite.inputs.ground_station_position_km,
        None,
    )?;
    if observations.is_empty()
        || suite.inputs.fit_through_epoch_id.as_deref()
            != observations
                .last()
                .map(|observation| observation.id.as_str())
    {
        bail!("fitted observation boundary does not match the declared final epoch");
    }
    let weather = Era5Grid::parse(&era5_bytes)?;
    let magnetic = IgrfGrid::parse(&igrf_bytes)?;
    let envelope = ParameterEnvelope::from_radar(&suite.model.radar)?;
    let parameters = envelope.parameters();
    let thresholds = Thresholds::default();
    let mut comparisons = Vec::new();

    for (family, route) in routes {
        let reference = parameters
            .iter()
            .copied()
            .map(|parameters| {
                evaluate(
                    parameters,
                    &route,
                    REFERENCE_STEP_S,
                    &observations,
                    family.bfo_sd_override_hz,
                    family.use_bfo,
                    &suite.model,
                    &weather,
                    &magnetic,
                    &suite.environment,
                )
            })
            .collect::<Result<Vec<_>>>()?;
        let reference_best = reference
            .iter()
            .map(|evaluation| evaluation.total_log_likelihood)
            .fold(f64::NEG_INFINITY, f64::max);
        for step_s in STEPS_S {
            comparisons.push(compare(
                family,
                route.clone(),
                step_s,
                &parameters,
                &reference,
                reference_best,
                &observations,
                &suite.model,
                &weather,
                &magnetic,
                &suite.environment,
                &thresholds,
            )?);
        }
    }

    let chosen_production_step_s = STEPS_S.into_iter().find(|step| {
        comparisons
            .iter()
            .filter(|comparison| comparison.step_s == *step)
            .count()
            == 2
            && comparisons
                .iter()
                .filter(|comparison| comparison.step_s == *step)
                .all(|comparison| comparison.passes)
    });
    let input_set_sha256 = sha256_bytes(&serde_json::to_vec(&input_sha256)?);
    let configured_step_matches_chosen = chosen_production_step_s
        .is_some_and(|step| (step - suite.environment.integration_step_s).abs() <= 1e-12);
    let scientific_scope = vec![
        "This is a deterministic numerical-integration control, not an estimator fit and not evidence for either destination.".to_string(),
        "Both fixed-waypoint candidates are evaluated separately on the same declared state envelope; they are never pooled.".to_string(),
        "ERA5 temperature and winds are active. IGRF is loaded and hash-recorded but declination is inactive for true-track direct-to guidance.".to_string(),
        "The 30 s result is a numerical reference. The largest passing tested step is selected before the production fit.".to_string(),
    ];
    let result = ControlResult {
        schema_version: RESULT_SCHEMA_VERSION,
        name: "MH370 fixed-waypoint actual-grid integration-step control",
        status: if configured_step_matches_chosen {
            "complete"
        } else if chosen_production_step_s.is_some() {
            "chosen_step_not_configured"
        } else {
            "no_step_passed"
        },
        suite_name: suite.name,
        suite_config_schema_version: suite.schema_version,
        input_set_sha256: input_set_sha256.clone(),
        input_sha256: input_sha256.clone(),
        fitted_epoch_ids: observations
            .iter()
            .map(|observation| observation.id.clone())
            .collect(),
        fitted_epoch_times_s: observations
            .iter()
            .map(|observation| observation.measurement.time.0)
            .collect(),
        tested_steps_s: STEPS_S.to_vec(),
        reference_step_s: REFERENCE_STEP_S,
        envelope,
        thresholds,
        comparisons,
        chosen_production_step_s,
        configured_production_step_s: suite.environment.integration_step_s,
        configured_step_matches_chosen,
        decision_rule:
            "largest tested step passing every threshold for both routes; 30 s is the reference",
        scientific_scope,
    };

    fs::create_dir_all(&arguments.output)
        .with_context(|| format!("cannot create {}", arguments.output.display()))?;
    let result_path = arguments.output.join(RESULT_NAME);
    let csv_path = arguments.output.join(CSV_NAME);
    atomic_write(
        &result_path,
        &(serde_json::to_string_pretty(&result)? + "\n").into_bytes(),
    )?;
    atomic_write(
        &csv_path,
        csv(&result.comparisons, &input_set_sha256).as_bytes(),
    )?;

    let generator = PathBuf::from(env!("CARGO_MANIFEST_DIR"))
        .join("examples/fixed_waypoint_integration_step_control.rs");
    let executable = env::current_exe()?;
    let output_sha256 = BTreeMap::from([
        (
            RESULT_NAME.to_string(),
            sha256_bytes(&fs::read(&result_path)?),
        ),
        (CSV_NAME.to_string(), sha256_bytes(&fs::read(&csv_path)?)),
    ]);
    let reproduction_command = format!(
        "cargo run --release -p mh370-runner --example fixed_waypoint_integration_step_control -- --suite-config {} --output {}",
        arguments.suite_config.display(),
        arguments.output.display(),
    );
    let manifest = OutputManifest {
        schema_version: MANIFEST_SCHEMA_VERSION,
        result_schema_version: RESULT_SCHEMA_VERSION,
        generator: generator.display().to_string(),
        generator_source_sha256: sha256_bytes(&fs::read(&generator)?),
        executable_sha256: sha256_bytes(&fs::read(&executable)?),
        input_set_sha256,
        input_sha256,
        output_sha256,
        reproduction_command,
    };
    let manifest_path = arguments.output.join(MANIFEST_NAME);
    atomic_write(
        &manifest_path,
        &(serde_json::to_string_pretty(&manifest)? + "\n").into_bytes(),
    )?;
    println!(
        "generated {}, {}, and {}; chosen step: {:?} s",
        result_path.display(),
        csv_path.display(),
        manifest_path.display(),
        result.chosen_production_step_s,
    );
    Ok(())
}
