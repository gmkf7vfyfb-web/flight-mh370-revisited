//! Deterministic structural-family predictive control at the corrected R600 contact.
//!
//! This is deliberately an example/control rather than a second estimator. It
//! reads typed 00:11 posterior handoffs, replays their unchanged guidance from
//! the radar epoch on the canonical absolute integration lattice, and applies
//! exactly one new likelihood: corrected R600 BTO at 00:19:29.

use std::{
    collections::BTreeMap,
    env, fs,
    path::{Path, PathBuf},
};

use anyhow::{bail, Context, Result};
use clap::Parser;
use mh370_domain::{
    great_circle_distance_nm, AircraftState, Degrees, LatLon, NauticalMiles, Seconds, Vec3,
};
use mh370_dynamics::{
    ground_velocity_from_control, one_turn_trajectories_at, propagate_constant_track, Era5Grid,
    FixedWaypointLeg, IgrfGrid, LateralGuidance, LateralMode, NavigationEnvironment, OneTurnConfig,
    OneTurnParameters, RadarPrior,
};
use mh370_estimator::{
    parse_satcom_observations, EvidenceComponent, EvidenceDisposition, FixedWaypointMetadata,
    FlightObservation, PosteriorHandoff,
};
use mh370_satcom::{evaluate_observation, SatcomModelConfig};
use rayon::{prelude::*, ThreadPoolBuilder};
use serde::{Deserialize, Serialize};
use sha2::{Digest, Sha256};

const RESULT_NAME: &str = "r600_predictive_compatibility.json";
const CSV_NAME: &str = "r600_predictive_compatibility.csv";
const MANIFEST_NAME: &str = "r600_predictive_compatibility_manifest.json";
const DEFAULT_MAXIMUM_STEP_S: f64 = 30.0;
const MAXIMUM_SUPPORTED_STEP_S: f64 = 600.0;
const RESULT_SCHEMA_VERSION: u32 = 2;
const OUTPUT_MANIFEST_SCHEMA_VERSION: u32 = 2;
const M1941_EPOCH_ID: &str = "m1941";
const M1941_EXPECTED_TIME_S: f64 = 5_953.0;
const M1941_EXPECTED_UTC: &str = "2014-03-07T19:41:02.000Z";
const M0011_EPOCH_ID: &str = "m0011";
const M0011_EXPECTED_TIME_S: f64 = 22_150.0;
const M0011_EXPECTED_UTC: &str = "2014-03-08T00:10:59.000Z";
const R600_EPOCH_ID: &str = "m0019a";
const R600_EXPECTED_TIME_S: f64 = 22_660.0;
const R600_EXPECTED_UTC: &str = "2014-03-08T00:19:29.000Z";
const R600_OBSERVED_BTO_US: f64 = 18_400.0;
const R600_BTO_SD_US: f64 = 63.0;

#[derive(Debug, Parser)]
#[command(about = "Evaluate unchanged-mode 00:11 posteriors against corrected 00:19 R600 BTO")]
struct Arguments {
    #[arg(
        long,
        default_value = "configs/mh370-through-0011-autopilot-modes-medium.toml"
    )]
    suite_config: PathBuf,
    #[arg(long, default_value = "configs/mh370-r600-bto-predictive-control.toml")]
    continuation_config: PathBuf,
    #[arg(long, default_value = "runs/mh370/through-0011-autopilot-modes-medium")]
    source_run: PathBuf,
    #[arg(
        long,
        default_value = "runs/mh370/through-0011-autopilot-modes-medium/r600-predictive-control"
    )]
    output: PathBuf,
    /// Guard on the numerical step. Current-v2 suites replay at the exact fit
    /// step; legacy-v1 scalar artifacts continue from the handoff at the
    /// smaller of their source step and this value.
    #[arg(long, default_value_t = DEFAULT_MAXIMUM_STEP_S)]
    maximum_step_s: f64,
    /// Deterministic particle-replay workers. Ordered collection and every
    /// scientific reduction remain in canonical handoff order.
    #[arg(long, default_value_t = 8)]
    threads: usize,
}

#[derive(Debug, Deserialize)]
struct SuiteConfiguration {
    schema_version: u32,
    name: String,
    seeds: Vec<u64>,
    families: Vec<FamilyConfiguration>,
    inputs: SourceInputsConfiguration,
    environment: EnvironmentConfiguration,
    convergence: SourceConvergenceConfiguration,
    model: SourceModelConfiguration,
}

#[derive(Debug, Deserialize)]
struct SourceConvergenceConfiguration {
    maximum_seed_mean_separation_nm: f64,
    maximum_log_evidence_range: f64,
    minimum_mutation_acceptance: f64,
}

#[derive(Debug, Deserialize)]
struct SourceInputsConfiguration {
    observations: PathBuf,
    satellite_ephemeris: PathBuf,
    ground_station_position_km: Vec3,
    #[serde(default)]
    fit_through_epoch_id: Option<String>,
}

#[derive(Debug, Deserialize)]
struct SourceSuiteSummaryArtifact {
    schema_version: u32,
    #[serde(default)]
    config_schema_version: Option<u32>,
    #[serde(default)]
    handoff_schema_version: Option<u32>,
    status: String,
    #[serde(default)]
    families: Vec<SourceSummaryFamily>,
}

#[derive(Debug, Deserialize)]
struct SourceSummaryFamily {
    name: String,
    lateral_mode: LateralMode,
    #[serde(default)]
    fixed_waypoint: Option<FixedWaypointMetadata>,
}

#[derive(Debug, Deserialize)]
struct SourceRunManifestArtifact {
    schema_version: u32,
    #[serde(default)]
    config_schema_version: Option<u32>,
    #[serde(default)]
    handoff_schema_version: Option<u32>,
    config_sha256: String,
    outputs: BTreeMap<String, String>,
    #[serde(default)]
    structural_families: Vec<SourceStructuralFamily>,
}

#[derive(Debug, Deserialize)]
struct SourceStructuralFamily {
    name: String,
    lateral_mode: LateralMode,
    #[serde(default)]
    fixed_waypoint: Option<FixedWaypointMetadata>,
    #[serde(default)]
    fixed_waypoint_identity_sha256: Option<String>,
    era5_temperature_wind_active: bool,
    igrf_declination_active: bool,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
enum SourceArtifactContract {
    LegacyV1Scalar,
    CurrentV2,
}

impl SourceArtifactContract {
    fn handoff_schema_version(self) -> u32 {
        match self {
            Self::LegacyV1Scalar => 1,
            Self::CurrentV2 => 2,
        }
    }

    fn suite_artifact_schema_version(self) -> u32 {
        match self {
            Self::LegacyV1Scalar => 1,
            Self::CurrentV2 => 2,
        }
    }
}

#[derive(Debug, Deserialize)]
struct SourceModelConfiguration {
    radar: RadarPrior,
    dynamics: OneTurnConfig,
    satcom: SatcomModelConfig,
}

#[derive(Debug, Deserialize)]
struct FamilyConfiguration {
    name: String,
    lateral_mode: LateralMode,
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
            position: LatLon::new(self.latitude_deg, self.longitude_deg)
                .context("fixed-waypoint coordinate is invalid")?,
            arrival_radius: NauticalMiles(self.arrival_radius_nm),
            coordinate_source_title: self.coordinate_source_title.clone(),
            coordinate_source_uri: self.coordinate_source_uri.clone(),
            coordinate_frame_assumption: self.coordinate_frame_assumption.clone(),
            coordinate_source_date: self.coordinate_source_date.clone(),
            coordinate_note: self.coordinate_note.clone(),
        })
    }
}

#[derive(Debug, Deserialize)]
struct EnvironmentConfiguration {
    era5: PathBuf,
    igrf: PathBuf,
    time_origin_unix_s: f64,
    integration_step_s: f64,
}

#[derive(Debug, Deserialize)]
#[serde(deny_unknown_fields)]
struct ContinuationConfiguration {
    schema_version: u32,
    name: String,
    inputs: ContinuationInputs,
    satcom: SatcomModelConfig,
    selection: SelectionConfiguration,
}

#[derive(Debug, Deserialize)]
#[serde(deny_unknown_fields)]
struct ContinuationInputs {
    observations: PathBuf,
    satellite_ephemeris: PathBuf,
    ground_station_position_km: Vec3,
    source_epoch_id: String,
    target_epoch_id: String,
    target_channel: String,
}

#[derive(Debug, Deserialize)]
#[serde(deny_unknown_fields)]
struct SelectionConfiguration {
    kind: String,
}

#[derive(Debug, Clone)]
struct ParticleRecord {
    initial_post_turn_track_true_deg: f64,
    checkpoint_latitude_deg: Option<f64>,
    checkpoint_longitude_deg: Option<f64>,
    checkpoint_track_true_deg: Option<f64>,
    start_latitude_deg: f64,
    start_longitude_deg: f64,
    start_track_true_deg: f64,
    end_latitude_deg: f64,
    end_longitude_deg: f64,
    end_track_true_deg: f64,
    end_heading_true_deg: f64,
    residual_us: f64,
    normalized_log_prior: f64,
    log_likelihood: f64,
    prior_weight: f64,
    seed_posterior_weight: f64,
    posterior_weight: f64,
}

#[derive(Debug, Clone, Serialize)]
struct PositionSummary {
    latitude_deg: f64,
    longitude_deg: f64,
}

#[derive(Debug, Clone, Serialize)]
struct DistributionSummary {
    mean: PositionSummary,
    latitude_90_deg: [f64; 2],
    longitude_90_deg: [f64; 2],
    bto_residual_mean_us: f64,
    bto_residual_mae_us: f64,
    bto_residual_rmse_us: f64,
    mass_within_one_bto_sd: f64,
    mass_within_two_bto_sd: f64,
    effective_sample_size: f64,
    track_true: AngularSummary,
}

#[derive(Debug, Clone, Serialize)]
struct AngularSummary {
    circular_mean_deg: f64,
    /// Central weighted interval after unwrapping every angle about the
    /// circular mean. Endpoints may therefore lie outside [0, 360).
    central_90_deg: [f64; 2],
}

#[derive(Debug, Clone, Serialize)]
struct CheckpointSummary {
    epoch_id: String,
    time_s: f64,
    mean: PositionSummary,
    latitude_90_deg: [f64; 2],
    longitude_90_deg: [f64; 2],
    track_true: AngularSummary,
}

#[derive(Debug, Clone, Serialize)]
struct PredictiveStabilitySummary {
    minimum_seed_conditioned_effective_sample_size: f64,
    seed_log_predictive_density_range_nats: f64,
    maximum_seed_conditioned_mean_separation_nm: f64,
    maximum_allowed_log_predictive_density_range_nats: f64,
    maximum_allowed_conditioned_mean_separation_nm: f64,
    descriptive_limit_origin: &'static str,
    all_conditioned_effective_sample_sizes_finite_positive: bool,
    passes_source_config_derived_descriptive_limits: bool,
    status: &'static str,
}

#[derive(Debug, Clone, Serialize)]
struct FamilyResult {
    family: String,
    lateral_mode: LateralMode,
    fixed_waypoint: Option<FixedWaypointMetadata>,
    particles: usize,
    initial_post_turn_track_true: AngularSummary,
    m1941_through_m0011_smoothing_posterior: Option<CheckpointSummary>,
    m0011_source_posterior: CheckpointSummary,
    source_mean_at_0011: PositionSummary,
    propagated_prior_at_0019: DistributionSummary,
    r600_conditioned_at_0019: DistributionSummary,
    mean_track_true_deg_after_conditioning: f64,
    mean_heading_true_deg_after_conditioning: f64,
    seed_log_predictive_density: BTreeMap<u64, f64>,
    seed_posterior_effective_sample_size: BTreeMap<u64, f64>,
    equal_seed_log_predictive_density: f64,
    log_predictive_likelihood_ratio_to_constant_true_track: f64,
    predictive_likelihood_ratio_to_constant_true_track: Option<f64>,
    seed_log_predictive_density_range: f64,
    maximum_seed_conditioned_mean_separation_nm: f64,
    predictive_stability: PredictiveStabilitySummary,
    maximum_source_replay_separation_nm: Option<f64>,
    maximum_source_replay_track_difference_deg: Option<f64>,
    maximum_source_replay_heading_difference_deg: Option<f64>,
    maximum_source_replay_ground_speed_difference_kt: Option<f64>,
}

#[derive(Debug, Serialize)]
struct PropagationDescription {
    source_time_s: f64,
    target_time_s: f64,
    duration_s: f64,
    time_origin_unix_s: f64,
    source_fit_integration_step_s: f64,
    r600_propagation_integration_step_s: f64,
    integration_policy: String,
    weather: String,
    magnetic: String,
    speed_altitude: String,
    lateral_control: String,
}

#[derive(Debug, Serialize)]
struct SelectionDescription {
    epoch_id: String,
    time_utc: String,
    channel: String,
    observed_bto_us: f64,
    standard_deviation_us: f64,
    likelihood: &'static str,
}

#[derive(Debug, Serialize)]
struct ControlSettings {
    algorithm: String,
    maximum_step_s: f64,
    applied_step_s: f64,
    source_artifact_contract: String,
}

#[derive(Debug, Serialize)]
struct ControlResult {
    schema_version: u32,
    source_suite_artifact_schema_version: u32,
    source_config_schema_version: u32,
    source_handoff_schema_version: u32,
    name: &'static str,
    status: &'static str,
    source_suite_name: String,
    continuation_name: String,
    source_run_status: String,
    source_epoch_id: String,
    propagation: PropagationDescription,
    selection: SelectionDescription,
    structural_pooling: &'static str,
    seed_pooling: &'static str,
    input_set_sha256: String,
    input_sha256: BTreeMap<String, String>,
    families: Vec<FamilyResult>,
    limitations: Vec<String>,
}

#[derive(Debug, Serialize)]
struct OutputManifest {
    schema_version: u32,
    result_schema_version: u32,
    source_suite_artifact_schema_version: u32,
    source_config_schema_version: u32,
    source_handoff_schema_version: u32,
    threads: usize,
    generator: String,
    generator_source_sha256: String,
    executable_sha256: String,
    input_set_sha256: String,
    input_sha256: BTreeMap<String, String>,
    output_sha256: BTreeMap<String, String>,
    reproduction_command: String,
    scientific_scope: Vec<String>,
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

fn fixed_waypoint_identity(route: &FixedWaypointMetadata) -> Result<String> {
    Ok(sha256_bytes(&serde_json::to_vec(route)?))
}

fn lateral_mode_token(mode: LateralMode) -> &'static str {
    match mode {
        LateralMode::ConstantTrueHeading => "constant_true_heading",
        LateralMode::ConstantMagneticHeading => "constant_magnetic_heading",
        LateralMode::ConstantTrueTrack => "constant_true_track",
        LateralMode::ConstantMagneticTrack => "constant_magnetic_track",
        LateralMode::LateralNavigation => "lateral_navigation",
    }
}

fn magnetic_declination_active(mode: LateralMode) -> bool {
    matches!(
        mode,
        LateralMode::ConstantMagneticHeading | LateralMode::ConstantMagneticTrack
    )
}

fn declination_for_mode(
    mode: LateralMode,
    sample: impl FnOnce() -> Result<Degrees>,
) -> Result<Degrees> {
    if magnetic_declination_active(mode) {
        sample()
    } else {
        Ok(Degrees(0.0))
    }
}

fn angular_difference_deg(first: f64, second: f64) -> f64 {
    (first - second + 180.0).rem_euclid(360.0) - 180.0
}

fn validate_source_artifact_contract(
    suite: &SuiteConfiguration,
    summary: &SourceSuiteSummaryArtifact,
    manifest: &SourceRunManifestArtifact,
) -> Result<SourceArtifactContract> {
    if summary.schema_version != manifest.schema_version {
        bail!(
            "source suite-summary schema {} and run-manifest schema {} do not match",
            summary.schema_version,
            manifest.schema_version
        );
    }
    match summary.schema_version {
        1 => {
            if suite.schema_version != 1
                || summary.config_schema_version.is_some()
                || summary.handoff_schema_version.is_some()
                || manifest.config_schema_version.is_some()
                || manifest.handoff_schema_version.is_some()
                || !manifest.structural_families.is_empty()
                || suite.families.iter().any(|family| {
                    family.lateral_mode == LateralMode::LateralNavigation
                        || family.fixed_waypoint.is_some()
                })
            {
                bail!("schema-v1 source artifacts are valid only for legacy scalar suites");
            }
            Ok(SourceArtifactContract::LegacyV1Scalar)
        }
        2 => {
            if summary.config_schema_version != Some(suite.schema_version)
                || manifest.config_schema_version != Some(suite.schema_version)
                || summary.handoff_schema_version != Some(2)
                || manifest.handoff_schema_version != Some(2)
            {
                bail!("schema-v2 source artifacts have inconsistent config/handoff schemas");
            }
            if summary.families.len() != suite.families.len()
                || manifest.structural_families.len() != suite.families.len()
            {
                bail!("schema-v2 source artifacts do not enumerate every structural family");
            }
            for configured in &suite.families {
                let expected_route = configured
                    .fixed_waypoint
                    .as_ref()
                    .map(FixedWaypointConfiguration::metadata)
                    .transpose()?;
                let summary_family = summary
                    .families
                    .iter()
                    .find(|family| family.name == configured.name)
                    .with_context(|| format!("suite summary lacks family {}", configured.name))?;
                if summary_family.lateral_mode != configured.lateral_mode
                    || summary_family.fixed_waypoint != expected_route
                {
                    bail!(
                        "suite-summary guidance identity disagrees for family {}",
                        configured.name
                    );
                }
                let manifest_family = manifest
                    .structural_families
                    .iter()
                    .find(|family| family.name == configured.name)
                    .with_context(|| format!("run manifest lacks family {}", configured.name))?;
                let expected_route_identity = expected_route
                    .as_ref()
                    .map(fixed_waypoint_identity)
                    .transpose()?;
                if manifest_family.lateral_mode != configured.lateral_mode
                    || manifest_family.fixed_waypoint != expected_route
                    || manifest_family.fixed_waypoint_identity_sha256 != expected_route_identity
                    || !manifest_family.era5_temperature_wind_active
                    || manifest_family.igrf_declination_active
                        != magnetic_declination_active(configured.lateral_mode)
                {
                    bail!(
                        "run-manifest structural identity disagrees for family {}",
                        configured.name
                    );
                }
            }
            Ok(SourceArtifactContract::CurrentV2)
        }
        version => bail!("unsupported source artifact schema version {version}"),
    }
}

fn logsumexp(values: impl Iterator<Item = f64>) -> f64 {
    let values = values.collect::<Vec<_>>();
    let maximum = values.iter().copied().fold(f64::NEG_INFINITY, f64::max);
    maximum
        + values
            .iter()
            .map(|value| (value - maximum).exp())
            .sum::<f64>()
            .ln()
}

fn finite_linear_ratio(log_ratio: f64) -> Option<f64> {
    let ratio = log_ratio.exp();
    (ratio.is_finite() && ratio > 0.0).then_some(ratio)
}

fn mean_position(
    records: &[ParticleRecord],
    weight: impl Fn(&ParticleRecord) -> f64,
    use_start: bool,
) -> Result<PositionSummary> {
    let total = records.iter().map(&weight).sum::<f64>();
    if !total.is_finite() || total <= 0.0 {
        bail!("position summary has invalid total weight");
    }
    let latitude = records
        .iter()
        .map(|record| {
            weight(record)
                * if use_start {
                    record.start_latitude_deg
                } else {
                    record.end_latitude_deg
                }
        })
        .sum::<f64>()
        / total;
    let sine = records
        .iter()
        .map(|record| {
            let longitude = if use_start {
                record.start_longitude_deg
            } else {
                record.end_longitude_deg
            };
            weight(record) * longitude.to_radians().sin()
        })
        .sum::<f64>()
        / total;
    let cosine = records
        .iter()
        .map(|record| {
            let longitude = if use_start {
                record.start_longitude_deg
            } else {
                record.end_longitude_deg
            };
            weight(record) * longitude.to_radians().cos()
        })
        .sum::<f64>()
        / total;
    Ok(PositionSummary {
        latitude_deg: latitude,
        longitude_deg: sine.atan2(cosine).to_degrees(),
    })
}

fn weighted_quantile(
    records: &[ParticleRecord],
    probability: f64,
    latitude: bool,
    posterior: bool,
) -> f64 {
    let mut values = records
        .iter()
        .map(|record| {
            (
                if latitude {
                    record.end_latitude_deg
                } else {
                    record.end_longitude_deg
                },
                if posterior {
                    record.posterior_weight
                } else {
                    record.prior_weight
                },
            )
        })
        .collect::<Vec<_>>();
    values.sort_by(|first, second| first.0.total_cmp(&second.0));
    let mut cumulative = 0.0;
    for (value, weight) in values {
        cumulative += weight;
        if cumulative >= probability {
            return value;
        }
    }
    f64::NAN
}

fn weighted_quantile_by(
    records: &[ParticleRecord],
    probability: f64,
    value: impl Fn(&ParticleRecord) -> f64,
    weight: impl Fn(&ParticleRecord) -> f64,
) -> f64 {
    let mut values = records
        .iter()
        .map(|record| (value(record), weight(record)))
        .collect::<Vec<_>>();
    values.sort_by(|first, second| first.0.total_cmp(&second.0));
    let total = values.iter().map(|(_, weight)| weight).sum::<f64>();
    let target = probability * total;
    let mut cumulative = 0.0;
    for (value, weight) in values {
        cumulative += weight;
        if cumulative >= target {
            return value;
        }
    }
    f64::NAN
}

fn angular_summary(
    records: &[ParticleRecord],
    value: impl Fn(&ParticleRecord) -> f64 + Copy,
    weight: impl Fn(&ParticleRecord) -> f64 + Copy,
) -> Result<AngularSummary> {
    let total = records.iter().map(weight).sum::<f64>();
    if !total.is_finite() || total <= 0.0 {
        bail!("angular summary has invalid total weight");
    }
    let sine = records
        .iter()
        .map(|record| weight(record) * value(record).to_radians().sin())
        .sum::<f64>();
    let cosine = records
        .iter()
        .map(|record| weight(record) * value(record).to_radians().cos())
        .sum::<f64>();
    let mean = sine.atan2(cosine).to_degrees().rem_euclid(360.0);
    let unwrapped = |record: &ParticleRecord| mean + angular_difference_deg(value(record), mean);
    Ok(AngularSummary {
        circular_mean_deg: mean,
        central_90_deg: [
            weighted_quantile_by(records, 0.05, unwrapped, weight),
            weighted_quantile_by(records, 0.95, unwrapped, weight),
        ],
    })
}

fn checkpoint_summary(
    records: &[ParticleRecord],
    epoch_id: &str,
    time_s: f64,
    latitude: impl Fn(&ParticleRecord) -> f64 + Copy,
    longitude: impl Fn(&ParticleRecord) -> f64 + Copy,
    track: impl Fn(&ParticleRecord) -> f64 + Copy,
    weight: impl Fn(&ParticleRecord) -> f64 + Copy,
) -> Result<CheckpointSummary> {
    let total = records.iter().map(weight).sum::<f64>();
    if !total.is_finite() || total <= 0.0 {
        bail!("checkpoint summary has invalid total weight");
    }
    let mean_latitude = records
        .iter()
        .map(|record| weight(record) * latitude(record))
        .sum::<f64>()
        / total;
    let sine = records
        .iter()
        .map(|record| weight(record) * longitude(record).to_radians().sin())
        .sum::<f64>();
    let cosine = records
        .iter()
        .map(|record| weight(record) * longitude(record).to_radians().cos())
        .sum::<f64>();
    Ok(CheckpointSummary {
        epoch_id: epoch_id.to_string(),
        time_s,
        mean: PositionSummary {
            latitude_deg: mean_latitude,
            longitude_deg: sine.atan2(cosine).to_degrees(),
        },
        latitude_90_deg: [
            weighted_quantile_by(records, 0.05, latitude, weight),
            weighted_quantile_by(records, 0.95, latitude, weight),
        ],
        longitude_90_deg: [
            weighted_quantile_by(records, 0.05, longitude, weight),
            weighted_quantile_by(records, 0.95, longitude, weight),
        ],
        track_true: angular_summary(records, track, weight)?,
    })
}

fn distribution_summary(
    records: &[ParticleRecord],
    bto_sd_us: f64,
    posterior: bool,
) -> Result<DistributionSummary> {
    let weight = |record: &ParticleRecord| {
        if posterior {
            record.posterior_weight
        } else {
            record.prior_weight
        }
    };
    let total = records.iter().map(weight).sum::<f64>();
    if (total - 1.0).abs() > 1e-9 {
        bail!("family mixture weights do not sum to one: {total}");
    }
    let residual_mean = records
        .iter()
        .map(|record| weight(record) * record.residual_us)
        .sum();
    let residual_mae = records
        .iter()
        .map(|record| weight(record) * record.residual_us.abs())
        .sum();
    let residual_rmse = records
        .iter()
        .map(|record| weight(record) * record.residual_us.powi(2))
        .sum::<f64>()
        .sqrt();
    let mass_within = |multiple: f64| {
        let mass = records
            .iter()
            .filter(|record| record.residual_us.abs() <= multiple * bto_sd_us)
            .map(weight)
            .sum::<f64>();
        if mass == 0.0 {
            0.0
        } else {
            mass
        }
    };
    Ok(DistributionSummary {
        mean: mean_position(records, weight, false)?,
        latitude_90_deg: [
            weighted_quantile(records, 0.05, true, posterior),
            weighted_quantile(records, 0.95, true, posterior),
        ],
        longitude_90_deg: [
            weighted_quantile(records, 0.05, false, posterior),
            weighted_quantile(records, 0.95, false, posterior),
        ],
        bto_residual_mean_us: residual_mean,
        bto_residual_mae_us: residual_mae,
        bto_residual_rmse_us: residual_rmse,
        mass_within_one_bto_sd: mass_within(1.0),
        mass_within_two_bto_sd: mass_within(2.0),
        effective_sample_size: 1.0
            / records
                .iter()
                .map(|record| weight(record).powi(2))
                .sum::<f64>(),
        track_true: angular_summary(records, |record| record.end_track_true_deg, weight)?,
    })
}

fn propagate_legacy_scalar_from_handoff(
    mut state: AircraftState,
    mut heading_true: Degrees,
    target_time_s: f64,
    mach: f64,
    modal_control: Degrees,
    lateral_mode: LateralMode,
    weather: &Era5Grid,
    magnetic: &IgrfGrid,
    environment: &EnvironmentConfiguration,
    control_step_s: f64,
) -> Result<(AircraftState, Degrees)> {
    if lateral_mode == LateralMode::LateralNavigation {
        bail!("legacy schema-v1 handoffs cannot encode typed LNAV continuation");
    }
    while state.time.0 < target_time_s - 1e-9 {
        let duration_s = control_step_s.min(target_time_s - state.time.0);
        let sample = weather.sample(
            environment.time_origin_unix_s + state.time.0,
            state.altitude.0,
            state.position,
        )?;
        let declination = declination_for_mode(lateral_mode, || {
            Ok(magnetic.declination(state.altitude.0, state.position)?)
        })?;
        let velocity = ground_velocity_from_control(
            mh370_domain::Knots(mach * sample.speed_of_sound_knots()),
            modal_control,
            lateral_mode,
            sample.wind_north,
            sample.wind_east,
            declination,
        )?;
        state.track_true = velocity.track_true;
        state.ground_speed = velocity.speed;
        heading_true = velocity.heading_true;
        state = propagate_constant_track(state, Seconds(duration_s))?;
    }
    Ok((state, heading_true))
}

fn guidance_for_family(
    mode: LateralMode,
    fixed_waypoint: Option<&FixedWaypointMetadata>,
) -> Result<LateralGuidance> {
    match (mode, fixed_waypoint) {
        (LateralMode::LateralNavigation, Some(route)) => Ok(LateralGuidance::DirectTo(
            FixedWaypointLeg::new(route.position, route.arrival_radius)?,
        )),
        (LateralMode::LateralNavigation, None) => {
            bail!("LNAV family lacks typed fixed-waypoint metadata")
        }
        (_, Some(_)) => bail!("scalar family unexpectedly carries fixed-waypoint metadata"),
        (_, None) => Ok(LateralGuidance::SelectedControl(mode)),
    }
}

fn source_parameters(
    particle: &mh370_estimator::PosteriorHandoffParticle,
    fixed_waypoint: Option<&FixedWaypointMetadata>,
) -> OneTurnParameters {
    OneTurnParameters {
        initial_latitude_deg: particle.turn.initial_position.latitude.0,
        initial_longitude_deg: particle.turn.initial_position.longitude.0,
        initial_track_true_deg: particle.turn.initial_track_true.0,
        turn_time_s: particle.turn.turn_time.0,
        // LNAV's scalar is scientifically inactive and canonicalized to a
        // zero serialization sentinel. The handoff turn field contains the
        // derived initial direct-to course, not this parameter.
        post_turn_track_true_deg: if fixed_waypoint.is_some() {
            0.0
        } else {
            particle.turn.post_turn_track_true.0
        },
        mach: particle.mach,
        altitude_ft: particle.aircraft.altitude.0,
    }
}

#[derive(Debug, Clone, Copy)]
struct SourceReplayDifferences {
    position_nm: f64,
    track_deg: f64,
    heading_deg: f64,
    ground_speed_kt: f64,
}

fn validate_replayed_source_state(
    replayed: &mh370_dynamics::OneTurnTrajectory,
    handoff_state: &AircraftState,
    handoff_heading: Degrees,
) -> Result<SourceReplayDifferences> {
    let differences = SourceReplayDifferences {
        position_nm: great_circle_distance_nm(replayed.aircraft.position, handoff_state.position).0,
        track_deg: angular_difference_deg(
            replayed.aircraft.track_true.0,
            handoff_state.track_true.0,
        )
        .abs(),
        heading_deg: angular_difference_deg(replayed.heading_true.0, handoff_heading.0).abs(),
        ground_speed_kt: (replayed.aircraft.ground_speed.0 - handoff_state.ground_speed.0).abs(),
    };
    if differences.position_nm > 1e-6
        || differences.track_deg > 1e-8
        || differences.heading_deg > 1e-8
        || differences.ground_speed_kt > 1e-8
        || (replayed.aircraft.altitude.0 - handoff_state.altitude.0).abs() > 1e-8
        || (replayed.aircraft.time.0 - handoff_state.time.0).abs() > 1e-9
    {
        bail!("source state is not reproduced by the declared full-path replay");
    }
    Ok(differences)
}

fn evaluate_family(
    configuration: &FamilyConfiguration,
    seeds: &[u64],
    source_run: &Path,
    checkpoint: &FlightObservation,
    source: &FlightObservation,
    target: &FlightObservation,
    satcom: &SatcomModelConfig,
    weather: &Era5Grid,
    magnetic: &IgrfGrid,
    environment: &EnvironmentConfiguration,
    convergence: &SourceConvergenceConfiguration,
    model: &SourceModelConfiguration,
    propagation_step_s: f64,
    source_artifact_contract: SourceArtifactContract,
    source_output_sha256: &BTreeMap<String, String>,
    hashes: &mut BTreeMap<String, String>,
) -> Result<FamilyResult> {
    let expected_fixed_waypoint = configuration
        .fixed_waypoint
        .as_ref()
        .map(FixedWaypointConfiguration::metadata)
        .transpose()?;
    let source_count = seeds.len() as f64;
    let bto_sd_us = target
        .measurement
        .bto_sd
        .context("target epoch lacks BTO standard deviation")?
        .0;
    let mut all_records = Vec::new();
    let mut seed_log_predictive_density = BTreeMap::new();
    let mut seed_posterior_effective_sample_size = BTreeMap::new();
    let mut seed_means = Vec::new();
    let guidance =
        guidance_for_family(configuration.lateral_mode, expected_fixed_waypoint.as_ref())?;
    let mut maximum_source_replay_separation_nm: Option<f64> = None;
    let mut maximum_source_replay_track_difference_deg: Option<f64> = None;
    let mut maximum_source_replay_heading_difference_deg: Option<f64> = None;
    let mut maximum_source_replay_ground_speed_difference_kt: Option<f64> = None;

    for seed in seeds {
        let relative = PathBuf::from(format!(
            "{}/seed-{seed}/posterior-handoff.json",
            configuration.name
        ));
        let path = source_run.join(&relative);
        let label = format!("handoff/{}/seed-{seed}", configuration.name);
        let bytes = read_hashed(&path, &label, hashes)?;
        if source_output_sha256.get(&relative.display().to_string()) != hashes.get(&label) {
            bail!("{label} hash does not match the source suite manifest");
        }
        let handoff: PosteriorHandoff = serde_json::from_slice(&bytes)
            .with_context(|| format!("cannot parse {}", path.display()))?;
        handoff.validate()?;
        if handoff.schema_version != source_artifact_contract.handoff_schema_version() {
            bail!(
                "{label} schema {} is incompatible with source artifact schema {}",
                handoff.schema_version,
                source_artifact_contract.suite_artifact_schema_version()
            );
        }
        if handoff.run.model_family != configuration.name || handoff.run.seed != *seed {
            bail!("handoff run identity does not match {label}");
        }
        if handoff
            .run
            .lateral_mode
            .is_some_and(|mode| mode != configuration.lateral_mode)
        {
            bail!("handoff run-level lateral mode does not match {label}");
        }
        if handoff.run.fixed_waypoint != expected_fixed_waypoint {
            bail!("handoff fixed-waypoint metadata does not match {label}");
        }
        for expected in [
            ("era5", &hashes["era5"]),
            ("igrf", &hashes["igrf"]),
            ("satcom_observations", &hashes["source_observations"]),
            ("satellite_ephemeris", &hashes["source_satellite_ephemeris"]),
        ] {
            if handoff.run.input_sha256.get(expected.0) != Some(expected.1) {
                bail!("{label} does not identify the selected {} grid", expected.0);
            }
        }
        if handoff.evidence.entries().iter().any(|entry| {
            entry.identity.epoch_id == target.id
                && entry.identity.component == EvidenceComponent::Bto
                && entry.disposition == EvidenceDisposition::Consumed
        }) {
            bail!("{label} already consumed target R600 BTO");
        }
        if !handoff.evidence.entries().iter().any(|entry| {
            entry.identity.epoch_id == source.id
                && entry.identity.component == EvidenceComponent::Bto
                && entry.disposition == EvidenceDisposition::Consumed
        }) {
            bail!("{label} did not consume declared source-epoch BTO");
        }

        // `par_iter` is indexed, so collecting into `Vec` preserves canonical
        // handoff order. Every floating-point reduction remains serial below.
        let evaluated = handoff
            .particles
            .par_iter()
            .map(
                |particle| -> Result<(ParticleRecord, Option<SourceReplayDifferences>)> {
                    if particle.lateral_mode != configuration.lateral_mode {
                        bail!("particle lateral mode does not match {label}");
                    }
                    if (particle.aircraft.time.0 - source.measurement.time.0).abs() > 1e-9 {
                        bail!("particle time does not match declared source epoch in {label}");
                    }
                    let start = particle.aircraft;
                    let (
                        end,
                        heading_true,
                        replayed_checkpoint,
                        initial_post_turn_track_true,
                        replay_differences,
                    ) = match source_artifact_contract {
                        SourceArtifactContract::LegacyV1Scalar => {
                            let (end, heading_true) = propagate_legacy_scalar_from_handoff(
                                start,
                                particle.heading_true,
                                target.measurement.time.0,
                                particle.mach,
                                particle.turn.post_turn_track_true,
                                particle.lateral_mode,
                                weather,
                                magnetic,
                                environment,
                                propagation_step_s,
                            )?;
                            (
                                end,
                                heading_true,
                                None,
                                particle.turn.post_turn_track_true,
                                None,
                            )
                        }
                        SourceArtifactContract::CurrentV2 => {
                            let trajectories = one_turn_trajectories_at(
                                source_parameters(particle, handoff.run.fixed_waypoint.as_ref()),
                                &model.radar,
                                &model.dynamics,
                                &[
                                    particle.turn.turn_time.0,
                                    checkpoint.measurement.time.0,
                                    source.measurement.time.0,
                                    target.measurement.time.0,
                                ],
                                particle.bfo_bias.mean_hz,
                                Some(NavigationEnvironment {
                                    weather,
                                    magnetic,
                                    time_origin_unix_s: environment.time_origin_unix_s,
                                    integration_step_s: propagation_step_s,
                                    lateral_guidance: guidance,
                                }),
                            )?;
                            let replayed_turn = trajectories[0];
                            if angular_difference_deg(
                                replayed_turn.aircraft.track_true.0,
                                particle.turn.post_turn_track_true.0,
                            )
                            .abs()
                                > 1e-8
                            {
                                bail!("{label} turn-course metadata is not reproduced by full-path replay");
                            }
                            let replayed_checkpoint = trajectories[1];
                            let replayed_source = trajectories[2];
                            let differences = validate_replayed_source_state(
                                &replayed_source,
                                &start,
                                particle.heading_true,
                            )
                            .with_context(|| {
                                format!("{label} failed source replay verification")
                            })?;
                            (
                                trajectories[3].aircraft,
                                trajectories[3].heading_true,
                                Some(replayed_checkpoint),
                                replayed_turn.aircraft.track_true,
                                Some(differences),
                            )
                        }
                    };
                    let mut bias = particle.bfo_bias;
                    let fit = evaluate_observation(
                        end,
                        &mut bias,
                        &target.measurement,
                        target.satellite_afc_hz,
                        false,
                        satcom,
                    )?;
                    Ok((
                        ParticleRecord {
                            initial_post_turn_track_true_deg: initial_post_turn_track_true.0,
                            checkpoint_latitude_deg: replayed_checkpoint
                                .map(|trajectory| trajectory.aircraft.position.latitude.0),
                            checkpoint_longitude_deg: replayed_checkpoint
                                .map(|trajectory| trajectory.aircraft.position.longitude.0),
                            checkpoint_track_true_deg: replayed_checkpoint
                                .map(|trajectory| trajectory.aircraft.track_true.0),
                            start_latitude_deg: start.position.latitude.0,
                            start_longitude_deg: start.position.longitude.0,
                            start_track_true_deg: start.track_true.0,
                            end_latitude_deg: end.position.latitude.0,
                            end_longitude_deg: end.position.longitude.0,
                            end_track_true_deg: end.track_true.0,
                            end_heading_true_deg: heading_true.0,
                            residual_us: fit
                                .bto_residual_us
                                .context("target BTO was not evaluated")?,
                            normalized_log_prior: particle.normalized_log_weight,
                            log_likelihood: fit.log_likelihood,
                            prior_weight: particle.normalized_log_weight.exp() / source_count,
                            seed_posterior_weight: 0.0,
                            posterior_weight: 0.0,
                        },
                        replay_differences,
                    ))
                },
            )
            .collect::<Result<Vec<_>>>()?;
        let mut seed_records = Vec::with_capacity(evaluated.len());
        for (record, differences) in evaluated {
            if let Some(differences) = differences {
                maximum_source_replay_separation_nm = Some(
                    maximum_source_replay_separation_nm
                        .unwrap_or(0.0)
                        .max(differences.position_nm),
                );
                maximum_source_replay_track_difference_deg = Some(
                    maximum_source_replay_track_difference_deg
                        .unwrap_or(0.0)
                        .max(differences.track_deg),
                );
                maximum_source_replay_heading_difference_deg = Some(
                    maximum_source_replay_heading_difference_deg
                        .unwrap_or(0.0)
                        .max(differences.heading_deg),
                );
                maximum_source_replay_ground_speed_difference_kt = Some(
                    maximum_source_replay_ground_speed_difference_kt
                        .unwrap_or(0.0)
                        .max(differences.ground_speed_kt),
                );
            }
            seed_records.push(record);
        }
        let log_predictive = logsumexp(
            seed_records
                .iter()
                .map(|record| record.normalized_log_prior + record.log_likelihood),
        );
        let mut inverse_ess = 0.0;
        for record in &mut seed_records {
            record.seed_posterior_weight =
                (record.normalized_log_prior + record.log_likelihood - log_predictive).exp();
            record.posterior_weight = record.seed_posterior_weight / source_count;
            inverse_ess += record.seed_posterior_weight.powi(2);
        }
        seed_means.push(mean_position(
            &seed_records,
            |record| record.seed_posterior_weight,
            false,
        )?);
        seed_log_predictive_density.insert(*seed, log_predictive);
        seed_posterior_effective_sample_size.insert(*seed, 1.0 / inverse_ess);
        all_records.extend(seed_records);
    }

    let equal_seed_log_predictive_density =
        logsumexp(seed_log_predictive_density.values().copied()) - source_count.ln();
    let log_values = seed_log_predictive_density
        .values()
        .copied()
        .collect::<Vec<_>>();
    let mut maximum_separation: f64 = 0.0;
    for first in 0..seed_means.len() {
        for second in (first + 1)..seed_means.len() {
            let first = LatLon::new(
                seed_means[first].latitude_deg,
                seed_means[first].longitude_deg,
            )?;
            let second = LatLon::new(
                seed_means[second].latitude_deg,
                seed_means[second].longitude_deg,
            )?;
            maximum_separation = maximum_separation.max(great_circle_distance_nm(first, second).0);
        }
    }
    let prior_at_0019 = distribution_summary(&all_records, bto_sd_us, false)?;
    let conditioned_at_0019 = distribution_summary(&all_records, bto_sd_us, true)?;
    let initial_post_turn_track_true = angular_summary(
        &all_records,
        |record| record.initial_post_turn_track_true_deg,
        |record| record.prior_weight,
    )?;
    let checkpoint_source_posterior = if all_records
        .iter()
        .all(|record| record.checkpoint_latitude_deg.is_some())
    {
        Some(checkpoint_summary(
            &all_records,
            &checkpoint.id,
            checkpoint.measurement.time.0,
            |record| record.checkpoint_latitude_deg.expect("checked above"),
            |record| record.checkpoint_longitude_deg.expect("checked above"),
            |record| record.checkpoint_track_true_deg.expect("checked above"),
            |record| record.prior_weight,
        )?)
    } else if all_records
        .iter()
        .all(|record| record.checkpoint_latitude_deg.is_none())
    {
        None
    } else {
        bail!("family contains a mixture of checkpoint-capable and legacy records");
    };
    let source_posterior = checkpoint_summary(
        &all_records,
        &source.id,
        source.measurement.time.0,
        |record| record.start_latitude_deg,
        |record| record.start_longitude_deg,
        |record| record.start_track_true_deg,
        |record| record.prior_weight,
    )?;
    let conditioned_heading = angular_summary(
        &all_records,
        |record| record.end_heading_true_deg,
        |record| record.posterior_weight,
    )?;
    let seed_log_predictive_density_range =
        log_values.iter().copied().fold(f64::NEG_INFINITY, f64::max)
            - log_values.iter().copied().fold(f64::INFINITY, f64::min);
    let minimum_seed_conditioned_effective_sample_size = seed_posterior_effective_sample_size
        .values()
        .copied()
        .fold(f64::INFINITY, f64::min);
    let all_conditioned_effective_sample_sizes_finite_positive =
        seed_posterior_effective_sample_size
            .values()
            .all(|value| value.is_finite() && *value > 0.0);
    if !all_conditioned_effective_sample_sizes_finite_positive {
        bail!("R600-conditioned effective sample size is not finite and positive");
    }
    let passes_source_config_derived_descriptive_limits = seed_log_predictive_density_range
        <= convergence.maximum_log_evidence_range
        && maximum_separation <= convergence.maximum_seed_mean_separation_nm;
    let predictive_stability = PredictiveStabilitySummary {
        minimum_seed_conditioned_effective_sample_size,
        seed_log_predictive_density_range_nats: seed_log_predictive_density_range,
        maximum_seed_conditioned_mean_separation_nm: maximum_separation,
        maximum_allowed_log_predictive_density_range_nats: convergence
            .maximum_log_evidence_range,
        maximum_allowed_conditioned_mean_separation_nm: convergence
            .maximum_seed_mean_separation_nm,
        descriptive_limit_origin: "source convergence limits reused and frozen before R600 evaluation; not prospectively calibrated R600 thresholds",
        all_conditioned_effective_sample_sizes_finite_positive,
        passes_source_config_derived_descriptive_limits,
        status: if passes_source_config_derived_descriptive_limits {
            "within_source_config_derived_descriptive_limits"
        } else {
            "provisional_outside_source_config_derived_descriptive_limits"
        },
    };
    Ok(FamilyResult {
        family: configuration.name.clone(),
        lateral_mode: configuration.lateral_mode,
        fixed_waypoint: expected_fixed_waypoint,
        particles: all_records.len(),
        initial_post_turn_track_true,
        m1941_through_m0011_smoothing_posterior: checkpoint_source_posterior,
        m0011_source_posterior: source_posterior.clone(),
        source_mean_at_0011: source_posterior.mean,
        mean_track_true_deg_after_conditioning: conditioned_at_0019.track_true.circular_mean_deg,
        mean_heading_true_deg_after_conditioning: conditioned_heading.circular_mean_deg,
        propagated_prior_at_0019: prior_at_0019,
        r600_conditioned_at_0019: conditioned_at_0019,
        seed_log_predictive_density,
        seed_posterior_effective_sample_size,
        equal_seed_log_predictive_density,
        log_predictive_likelihood_ratio_to_constant_true_track: 0.0,
        predictive_likelihood_ratio_to_constant_true_track: Some(1.0),
        seed_log_predictive_density_range,
        maximum_seed_conditioned_mean_separation_nm: maximum_separation,
        predictive_stability,
        maximum_source_replay_separation_nm,
        maximum_source_replay_track_difference_deg,
        maximum_source_replay_heading_difference_deg,
        maximum_source_replay_ground_speed_difference_kt,
    })
}

fn csv(result: &ControlResult) -> String {
    let mut output = String::from(
        "result_schema_version,source_suite_artifact_schema_version,source_config_schema_version,source_handoff_schema_version,input_set_sha256,family,lateral_mode,fixed_waypoint_identity_sha256,fixed_waypoint_target,fixed_waypoint_latitude_deg,fixed_waypoint_longitude_deg,fixed_waypoint_arrival_radius_nm,particles,initial_post_turn_track_true_mean_deg,initial_post_turn_track_true_p05_deg,initial_post_turn_track_true_p95_deg,m1941_through_m0011_smoothing_mean_latitude_deg,m1941_through_m0011_smoothing_mean_longitude_deg,m1941_through_m0011_smoothing_latitude_p05_deg,m1941_through_m0011_smoothing_latitude_p95_deg,m1941_through_m0011_smoothing_longitude_p05_deg,m1941_through_m0011_smoothing_longitude_p95_deg,m1941_through_m0011_smoothing_track_true_mean_deg,m1941_through_m0011_smoothing_track_true_p05_deg,m1941_through_m0011_smoothing_track_true_p95_deg,m0011_source_mean_latitude_deg,m0011_source_mean_longitude_deg,m0011_source_latitude_p05_deg,m0011_source_latitude_p95_deg,m0011_source_longitude_p05_deg,m0011_source_longitude_p95_deg,m0011_source_track_true_mean_deg,m0011_source_track_true_p05_deg,m0011_source_track_true_p95_deg,source_mean_latitude_deg,source_mean_longitude_deg,maximum_source_replay_separation_nm,maximum_source_replay_track_difference_deg,maximum_source_replay_heading_difference_deg,maximum_source_replay_ground_speed_difference_kt,prior_mean_latitude_deg,prior_mean_longitude_deg,prior_track_true_mean_deg,prior_track_true_p05_deg,prior_track_true_p95_deg,prior_bto_residual_mean_us,prior_bto_residual_rmse_us,prior_mass_within_one_bto_sd,prior_mass_within_two_bto_sd,conditioned_mean_latitude_deg,conditioned_mean_longitude_deg,conditioned_track_true_mean_deg,conditioned_track_true_p05_deg,conditioned_track_true_p95_deg,conditioned_bto_residual_mean_us,conditioned_bto_residual_rmse_us,equal_seed_log_predictive_density,log_predictive_likelihood_ratio_to_constant_true_track,predictive_likelihood_ratio_to_constant_true_track,seed_log_predictive_density_range,maximum_seed_conditioned_mean_separation_nm,minimum_seed_conditioned_effective_sample_size,predictive_stability_maximum_allowed_log_predictive_density_range_nats,predictive_stability_maximum_allowed_conditioned_mean_separation_nm,predictive_stability_all_conditioned_ess_finite_positive,predictive_stability_passes_source_config_derived_limits,predictive_stability_status\n",
    );
    let number = |value: f64| format!("{value:.12}");
    let optional_number = |value: Option<f64>| value.map(number).unwrap_or_default();
    let checkpoint_columns = |checkpoint: Option<&CheckpointSummary>| {
        checkpoint.map_or_else(
            || vec![String::new(); 9],
            |checkpoint| {
                vec![
                    number(checkpoint.mean.latitude_deg),
                    number(checkpoint.mean.longitude_deg),
                    number(checkpoint.latitude_90_deg[0]),
                    number(checkpoint.latitude_90_deg[1]),
                    number(checkpoint.longitude_90_deg[0]),
                    number(checkpoint.longitude_90_deg[1]),
                    number(checkpoint.track_true.circular_mean_deg),
                    number(checkpoint.track_true.central_90_deg[0]),
                    number(checkpoint.track_true.central_90_deg[1]),
                ]
            },
        )
    };
    for family in &result.families {
        let prior = &family.propagated_prior_at_0019;
        let posterior = &family.r600_conditioned_at_0019;
        let (route_identity, target, target_latitude, target_longitude, target_radius) = family
            .fixed_waypoint
            .as_ref()
            .map(|route| {
                Ok::<_, anyhow::Error>((
                    fixed_waypoint_identity(route)?,
                    route.target_name.clone(),
                    number(route.position.latitude.0),
                    number(route.position.longitude.0),
                    number(route.arrival_radius.0),
                ))
            })
            .transpose()
            .expect("validated route serializes")
            .unwrap_or((
                String::new(),
                String::new(),
                String::new(),
                String::new(),
                String::new(),
            ));
        let mut row = vec![
            result.schema_version.to_string(),
            result.source_suite_artifact_schema_version.to_string(),
            result.source_config_schema_version.to_string(),
            result.source_handoff_schema_version.to_string(),
            result.input_set_sha256.clone(),
            family.family.clone(),
            lateral_mode_token(family.lateral_mode).to_string(),
            route_identity,
            target,
            target_latitude,
            target_longitude,
            target_radius,
            family.particles.to_string(),
            number(family.initial_post_turn_track_true.circular_mean_deg),
            number(family.initial_post_turn_track_true.central_90_deg[0]),
            number(family.initial_post_turn_track_true.central_90_deg[1]),
        ];
        row.extend(checkpoint_columns(
            family.m1941_through_m0011_smoothing_posterior.as_ref(),
        ));
        row.extend(checkpoint_columns(Some(&family.m0011_source_posterior)));
        row.extend([
            number(family.source_mean_at_0011.latitude_deg),
            number(family.source_mean_at_0011.longitude_deg),
            optional_number(family.maximum_source_replay_separation_nm),
            optional_number(family.maximum_source_replay_track_difference_deg),
            optional_number(family.maximum_source_replay_heading_difference_deg),
            optional_number(family.maximum_source_replay_ground_speed_difference_kt),
            number(prior.mean.latitude_deg),
            number(prior.mean.longitude_deg),
            number(prior.track_true.circular_mean_deg),
            number(prior.track_true.central_90_deg[0]),
            number(prior.track_true.central_90_deg[1]),
            number(prior.bto_residual_mean_us),
            number(prior.bto_residual_rmse_us),
            number(prior.mass_within_one_bto_sd),
            number(prior.mass_within_two_bto_sd),
            number(posterior.mean.latitude_deg),
            number(posterior.mean.longitude_deg),
            number(posterior.track_true.circular_mean_deg),
            number(posterior.track_true.central_90_deg[0]),
            number(posterior.track_true.central_90_deg[1]),
            number(posterior.bto_residual_mean_us),
            number(posterior.bto_residual_rmse_us),
            number(family.equal_seed_log_predictive_density),
            number(family.log_predictive_likelihood_ratio_to_constant_true_track),
            optional_number(family.predictive_likelihood_ratio_to_constant_true_track),
            number(family.seed_log_predictive_density_range),
            number(family.maximum_seed_conditioned_mean_separation_nm),
            number(
                family
                    .predictive_stability
                    .minimum_seed_conditioned_effective_sample_size,
            ),
            number(
                family
                    .predictive_stability
                    .maximum_allowed_log_predictive_density_range_nats,
            ),
            number(
                family
                    .predictive_stability
                    .maximum_allowed_conditioned_mean_separation_nm,
            ),
            family
                .predictive_stability
                .all_conditioned_effective_sample_sizes_finite_positive
                .to_string(),
            family
                .predictive_stability
                .passes_source_config_derived_descriptive_limits
                .to_string(),
            family.predictive_stability.status.to_string(),
        ]);
        output.push_str(&row.join(","));
        output.push('\n');
    }
    output
}

fn atomic_write(path: &Path, bytes: &[u8]) -> Result<()> {
    let temporary = path.with_extension("tmp");
    fs::write(&temporary, bytes)
        .with_context(|| format!("cannot write {}", temporary.display()))?;
    fs::rename(&temporary, path).with_context(|| format!("cannot replace {}", path.display()))?;
    Ok(())
}

fn main() -> Result<()> {
    let arguments = Arguments::parse();
    let mut input_sha256 = BTreeMap::new();
    let suite_bytes = read_hashed(&arguments.suite_config, "suite_config", &mut input_sha256)?;
    let suite: SuiteConfiguration =
        toml::from_str(std::str::from_utf8(&suite_bytes).context("suite config is not UTF-8")?)?;
    if !matches!(suite.schema_version, 1 | 2) || suite.seeds.is_empty() || suite.families.is_empty()
    {
        bail!("source suite is incomplete");
    }
    let unique_family_names = suite
        .families
        .iter()
        .map(|family| &family.name)
        .collect::<std::collections::BTreeSet<_>>();
    if unique_family_names.len() != suite.families.len() {
        bail!("source suite family names are not unique");
    }
    if suite
        .families
        .iter()
        .filter(|family| family.lateral_mode == LateralMode::ConstantTrueTrack)
        .count()
        != 1
    {
        bail!(
            "predictive comparison requires exactly one fresh constant-true-track reference family"
        );
    }
    for family in &suite.families {
        if suite.schema_version == 1
            && (family.lateral_mode == LateralMode::LateralNavigation
                || family.fixed_waypoint.is_some())
        {
            bail!("schema-v1 suite configs cannot encode typed fixed-waypoint guidance");
        }
        match (family.lateral_mode, &family.fixed_waypoint) {
            (LateralMode::LateralNavigation, Some(route)) => {
                let metadata = route.metadata()?;
                if metadata.target_name.trim().is_empty()
                    || metadata.arrival_radius.0 <= 0.0
                    || !metadata.arrival_radius.is_finite()
                    || metadata.coordinate_source_title.trim().is_empty()
                    || metadata.coordinate_source_uri.trim().is_empty()
                    || metadata.coordinate_frame_assumption.trim().is_empty()
                    || metadata.coordinate_note.trim().is_empty()
                    || metadata
                        .coordinate_source_date
                        .as_ref()
                        .is_some_and(|date| date.trim().is_empty())
                {
                    bail!("fixed-waypoint family metadata is incomplete");
                }
            }
            (LateralMode::LateralNavigation, None) => {
                bail!("LNAV family lacks an explicit fixed waypoint");
            }
            (_, Some(_)) => bail!("fixed waypoint is only valid for an LNAV family"),
            (_, None) => {}
        }
    }
    if !suite.environment.time_origin_unix_s.is_finite()
        || !suite.environment.integration_step_s.is_finite()
        || suite.environment.integration_step_s <= 0.0
    {
        bail!("suite environment configuration is invalid");
    }
    if !suite
        .convergence
        .maximum_seed_mean_separation_nm
        .is_finite()
        || suite.convergence.maximum_seed_mean_separation_nm <= 0.0
        || !suite.convergence.maximum_log_evidence_range.is_finite()
        || suite.convergence.maximum_log_evidence_range <= 0.0
        || !suite.convergence.minimum_mutation_acceptance.is_finite()
        || suite.convergence.minimum_mutation_acceptance < 0.0
    {
        bail!("source convergence/stability limits are invalid");
    }
    if !arguments.maximum_step_s.is_finite()
        || arguments.maximum_step_s <= 0.0
        || arguments.maximum_step_s > MAXIMUM_SUPPORTED_STEP_S
    {
        bail!("maximum step must be finite, positive, and no greater than 600 seconds");
    }
    if arguments.threads == 0 {
        bail!("thread count must be positive");
    }

    let continuation_bytes = read_hashed(
        &arguments.continuation_config,
        "continuation_config",
        &mut input_sha256,
    )?;
    let continuation: ContinuationConfiguration = toml::from_str(
        std::str::from_utf8(&continuation_bytes).context("continuation config is not UTF-8")?,
    )?;
    if continuation.schema_version != 2 || continuation.selection.kind != "bto" {
        bail!("control requires the schema-v2 BTO continuation configuration");
    }
    continuation.satcom.validate()?;
    suite.model.satcom.validate()?;
    if continuation.satcom != suite.model.satcom {
        bail!("continuation SATCOM constants differ from the source estimator model");
    }
    if continuation.inputs.ground_station_position_km != suite.inputs.ground_station_position_km {
        bail!("continuation ground-station position differs from the source estimator model");
    }

    let suite_summary_path = arguments.source_run.join("suite-summary.json");
    let suite_manifest_path = arguments.source_run.join("run-manifest.json");
    let suite_summary_bytes = read_hashed(
        &suite_summary_path,
        "source_suite_summary",
        &mut input_sha256,
    )?;
    let suite_manifest_bytes = read_hashed(
        &suite_manifest_path,
        "source_suite_manifest",
        &mut input_sha256,
    )?;
    let suite_summary: SourceSuiteSummaryArtifact = serde_json::from_slice(&suite_summary_bytes)
        .context("cannot parse source suite summary")?;
    let suite_manifest: SourceRunManifestArtifact = serde_json::from_slice(&suite_manifest_bytes)
        .context("cannot parse source run manifest")?;
    if suite_manifest.config_sha256 != input_sha256["suite_config"] {
        bail!("source suite manifest does not identify the selected suite config");
    }
    if suite_manifest.outputs.get("suite-summary.json") != input_sha256.get("source_suite_summary")
    {
        bail!("source run manifest does not bind the selected suite summary");
    }
    let source_artifact_contract =
        validate_source_artifact_contract(&suite, &suite_summary, &suite_manifest)?;
    let propagation_step_s = match source_artifact_contract {
        SourceArtifactContract::LegacyV1Scalar => suite
            .environment
            .integration_step_s
            .min(arguments.maximum_step_s),
        SourceArtifactContract::CurrentV2 => {
            if suite.environment.integration_step_s > arguments.maximum_step_s + 1e-12 {
                bail!(
                    "current-v2 replay requires the exact source step {} s, which exceeds the declared guard {} s",
                    suite.environment.integration_step_s,
                    arguments.maximum_step_s
                );
            }
            suite.environment.integration_step_s
        }
    };
    let algorithm = match source_artifact_contract {
        SourceArtifactContract::LegacyV1Scalar => {
            "legacy schema-v1 scalar handoff continuation from the exact 00:11 state"
        }
        SourceArtifactContract::CurrentV2 => {
            "partition-invariant full radar-to-[modeled turn,m1941,00:11,R600] replay at the exact source fit step"
        }
    };
    input_sha256.insert(
        "control_settings".to_string(),
        sha256_bytes(&serde_json::to_vec(&ControlSettings {
            algorithm: algorithm.to_string(),
            maximum_step_s: arguments.maximum_step_s,
            applied_step_s: propagation_step_s,
            source_artifact_contract: match source_artifact_contract {
                SourceArtifactContract::LegacyV1Scalar => "legacy_v1_scalar".to_string(),
                SourceArtifactContract::CurrentV2 => "current_v2_full_replay".to_string(),
            },
        })?),
    );
    let source_run_status = suite_summary.status.clone();
    let source_output_sha256 = suite_manifest.outputs.clone();

    let era5_path = resolve(&arguments.suite_config, &suite.environment.era5);
    let igrf_path = resolve(&arguments.suite_config, &suite.environment.igrf);
    let era5_bytes = read_hashed(&era5_path, "era5", &mut input_sha256)?;
    let igrf_bytes = read_hashed(&igrf_path, "igrf", &mut input_sha256)?;
    let weather = Era5Grid::parse(&era5_bytes)?;
    let magnetic = IgrfGrid::parse(&igrf_bytes)?;

    let source_observations_path = resolve(&arguments.suite_config, &suite.inputs.observations);
    let source_ephemeris_path = resolve(&arguments.suite_config, &suite.inputs.satellite_ephemeris);
    let source_observations_bytes = read_hashed(
        &source_observations_path,
        "source_observations",
        &mut input_sha256,
    )?;
    let source_ephemeris_bytes = read_hashed(
        &source_ephemeris_path,
        "source_satellite_ephemeris",
        &mut input_sha256,
    )?;
    let source_observations = parse_satcom_observations(
        std::str::from_utf8(&source_observations_bytes)?,
        std::str::from_utf8(&source_ephemeris_bytes)?,
        suite.inputs.ground_station_position_km,
        None,
    )?;
    let fit_through_epoch_id = suite
        .inputs
        .fit_through_epoch_id
        .as_deref()
        .unwrap_or(&continuation.inputs.source_epoch_id);
    if fit_through_epoch_id != M0011_EPOCH_ID
        || continuation.inputs.source_epoch_id != M0011_EPOCH_ID
    {
        bail!("source fit boundary and continuation source must both be literal m0011");
    }
    if continuation.inputs.target_epoch_id != R600_EPOCH_ID
        || continuation.inputs.target_channel != "R600"
    {
        bail!("control target must be literal corrected m0019a/R600");
    }
    let checkpoint = source_observations
        .iter()
        .find(|observation| observation.id == M1941_EPOCH_ID)
        .context("hashed source observations lack m1941 checkpoint")?;
    if (checkpoint.measurement.time.0 - M1941_EXPECTED_TIME_S).abs() > 1e-9
        || checkpoint.time_utc != M1941_EXPECTED_UTC
    {
        bail!("hashed source m1941 checkpoint has an unexpected time identity");
    }
    let source = source_observations
        .iter()
        .find(|observation| observation.id == fit_through_epoch_id)
        .context("hashed source observations lack the declared fit boundary")?;
    if (source.measurement.time.0 - M0011_EXPECTED_TIME_S).abs() > 1e-9
        || source.time_utc != M0011_EXPECTED_UTC
    {
        bail!("hashed source fit boundary has an unexpected m0011 time identity");
    }

    let control_observations_path = resolve(
        &arguments.continuation_config,
        &continuation.inputs.observations,
    );
    let control_ephemeris_path = resolve(
        &arguments.continuation_config,
        &continuation.inputs.satellite_ephemeris,
    );
    let control_observations_bytes = read_hashed(
        &control_observations_path,
        "control_observations",
        &mut input_sha256,
    )?;
    let control_ephemeris_bytes = read_hashed(
        &control_ephemeris_path,
        "control_satellite_ephemeris",
        &mut input_sha256,
    )?;
    let control_observations = parse_satcom_observations(
        std::str::from_utf8(&control_observations_bytes)?,
        std::str::from_utf8(&control_ephemeris_bytes)?,
        continuation.inputs.ground_station_position_km,
        None,
    )?;
    let control_source = control_observations
        .iter()
        .find(|observation| observation.id == continuation.inputs.source_epoch_id)
        .context("control observations lack the source epoch")?;
    if (control_source.measurement.time.0 - source.measurement.time.0).abs() > 1e-9
        || control_source.time_utc != M0011_EXPECTED_UTC
    {
        bail!("source and control observation files disagree on source-epoch identity");
    }
    let target = control_observations
        .iter()
        .find(|observation| observation.id == continuation.inputs.target_epoch_id)
        .context("target epoch is absent")?;
    if (target.measurement.time.0 - R600_EXPECTED_TIME_S).abs() > 1e-9
        || target.time_utc != R600_EXPECTED_UTC
    {
        bail!("control target has an unexpected corrected-R600 time identity");
    }
    let (observed_bto, bto_sd) = target
        .measurement
        .bto
        .zip(target.measurement.bto_sd)
        .context("target epoch lacks complete BTO")?;
    if (observed_bto.0 - R600_OBSERVED_BTO_US).abs() > 1e-9
        || (bto_sd.0 - R600_BTO_SD_US).abs() > 1e-9
    {
        bail!("control target is not the canonical corrected R600 18400 +/- 63 us observation");
    }
    if target.measurement.bfo.is_some() || target.measurement.bfo_sd.is_some() {
        bail!("target R600 control observation must not contain BFO");
    }
    let duration_s = target.measurement.time.0 - source.measurement.time.0;
    if !duration_s.is_finite()
        || duration_s <= 0.0
        || checkpoint.measurement.time.0 >= source.measurement.time.0
    {
        bail!("target epoch does not follow source epoch");
    }

    let replay_pool = ThreadPoolBuilder::new()
        .num_threads(arguments.threads)
        .build()
        .context("cannot build deterministic R600 replay pool")?;
    let mut families = replay_pool.install(|| -> Result<Vec<FamilyResult>> {
        let mut families = Vec::new();
        for family in &suite.families {
            families.push(evaluate_family(
                family,
                &suite.seeds,
                &arguments.source_run,
                checkpoint,
                source,
                target,
                &continuation.satcom,
                &weather,
                &magnetic,
                &suite.environment,
                &suite.convergence,
                &suite.model,
                propagation_step_s,
                source_artifact_contract,
                &source_output_sha256,
                &mut input_sha256,
            )?);
        }
        Ok(families)
    })?;
    let ctt_log_predictive = families
        .iter()
        .find(|family| family.lateral_mode == LateralMode::ConstantTrueTrack)
        .context("constant-true-track result is absent")?
        .equal_seed_log_predictive_density;
    for family in &mut families {
        let log_ratio = family.equal_seed_log_predictive_density - ctt_log_predictive;
        family.log_predictive_likelihood_ratio_to_constant_true_track = log_ratio;
        family.predictive_likelihood_ratio_to_constant_true_track = finite_linear_ratio(log_ratio);
    }
    let predictive_comparison_provisional = families.iter().any(|family| {
        !family
            .predictive_stability
            .passes_source_config_derived_descriptive_limits
    });

    let input_set_sha256 = sha256_bytes(&serde_json::to_vec(&input_sha256)?);
    let has_fixed_waypoint = suite
        .families
        .iter()
        .any(|family| family.fixed_waypoint.is_some());
    let any_magnetic = suite
        .families
        .iter()
        .any(|family| magnetic_declination_active(family.lateral_mode));
    let integration_policy = match source_artifact_contract {
        SourceArtifactContract::LegacyV1Scalar => format!(
            "legacy scalar source state is preserved exactly at 00:11; only the subsequent continuation uses {:.0} s steps (source fit used {:.0} s)",
            propagation_step_s, suite.environment.integration_step_s
        ),
        SourceArtifactContract::CurrentV2 => format!(
            "full radar-to-[modeled turn,m1941,00:11,R600] replay uses the same selected {:.0} s step as the source fit; the replayed turn course and 00:11 state are checked against every handoff particle",
            propagation_step_s
        ),
    };
    let mut limitations = vec![
        "This is estimator-held-out forward R600 compatibility from 00:11 posteriors, not a new estimator fit, selection-blind model test, or impact PDF.".to_string(),
        "Each family preserves its own declared guidance; structural families and fixed-waypoint candidates are never pooled or assigned model probabilities.".to_string(),
        "For a schema-v2 fixed-waypoint family, the handoff carries one run-level typed destination and the turn field records the actual initial direct-to course, never the inactive internal scalar sentinel.".to_string(),
        "Mach and pressure altitude are held constant while ERA5 temperature and winds are sampled along propagation; IGRF declination is active only for magnetic-reference scalar families.".to_string(),
        "R600 BTO was excluded from estimator fitting and is the only new likelihood here. BFO, received power, fuel, endurance, flameout, descent, and impact displacement are not evaluated.".to_string(),
        "Every result is conditional on powered flight continuing to the recorded R600 reception at 00:19:29 UTC.".to_string(),
        "Equal weighting is used only across deterministic seeds within a family; the source suite may remain numerically nonconverged.".to_string(),
        "The m1941 checkpoint is a through-00:11 smoothing posterior at m1941: its particle weights include all fitted evidence through 00:11, including observations later than m1941. It is not a filtering posterior available at 19:41.".to_string(),
        "The initial post-turn true-track summary is the selected CTT setpoint for the CTT family and the derived WGS84-geodesic tangent at the modeled turn for each direct-to family.".to_string(),
        "Angular central 90 percent intervals are weighted 5th and 95th percentiles after unwrapping about the circular mean; serialized endpoints can lie outside 0 to 360 degrees.".to_string(),
        "R600-conditioned summaries normalize the R600 likelihood posterior separately within each seed and then average the three seed posteriors equally; predictive density does not reweight seed posterior mass.".to_string(),
    ];
    if source_artifact_contract == SourceArtifactContract::LegacyV1Scalar {
        limitations.push("The legacy schema-v1 source artifacts predate partition-invariant full-path replay, so their m1941 smoothing checkpoint is unavailable and serialized as null; their exact 00:11 handoff remains the continuation boundary.".to_string());
    }
    limitations.push("The 0.8 nat seed log-predictive-range and 30 NM conditioned-centroid-separation boundaries are source-config-derived descriptive limits reused and frozen before R600 evaluation; they were not prospectively calibrated as R600 thresholds.".to_string());
    if predictive_comparison_provisional {
        limitations.push("At least one structural family exceeds the source-config-derived descriptive seed-stability boundary, so cross-family R600 compatibility comparisons are marked provisional.".to_string());
    }
    limitations.push("Beyond basic finite-positive validity, per-seed R600-conditioned effective-sample-size magnitude is reported as a diagnostic only; no prospectively calibrated ESS floor was declared, so ESS magnitude does not contribute to the descriptive pass/provisional status.".to_string());
    if has_fixed_waypoint {
        limitations.push("The waypoint candidates were selected post hoc after inspecting 186.2-degree/seventh-arc geometry, then frozen before these production fits. This compatibility calculation has no waypoint-universe prior or look-elsewhere correction and is not out-of-sample candidate selection.".to_string());
    }
    let result = ControlResult {
        schema_version: RESULT_SCHEMA_VERSION,
        source_suite_artifact_schema_version: source_artifact_contract
            .suite_artifact_schema_version(),
        source_config_schema_version: suite.schema_version,
        source_handoff_schema_version: source_artifact_contract.handoff_schema_version(),
        name: "MH370 00:11 posterior forward R600 compatibility",
        status: if predictive_comparison_provisional {
            "complete_control_provisional_numerical_stability"
        } else {
            "complete_control"
        },
        source_suite_name: suite.name,
        continuation_name: continuation.name,
        source_run_status,
        source_epoch_id: source.id.clone(),
        propagation: PropagationDescription {
            source_time_s: source.measurement.time.0,
            target_time_s: target.measurement.time.0,
            duration_s,
            time_origin_unix_s: suite.environment.time_origin_unix_s,
            source_fit_integration_step_s: suite.environment.integration_step_s,
            r600_propagation_integration_step_s: propagation_step_s,
            integration_policy,
            weather: "ERA5 pressure-level temperature and horizontal winds active".to_string(),
            magnetic: if any_magnetic {
                "IGRF-14 east-positive declination active only for magnetic-reference scalar families; inactive for true-reference and direct-to families".to_string()
            } else {
                "IGRF-14 grid loaded and hash-recorded but inactive/not applicable for these true-reference and direct-to families".to_string()
            },
            speed_altitude: "constant Mach and constant pressure altitude per source particle"
                .to_string(),
            lateral_control:
                "unchanged selected-control mode or typed fixed-waypoint direct-to leg".to_string(),
        },
        selection: SelectionDescription {
            epoch_id: target.id.clone(),
            time_utc: target.time_utc.clone(),
            channel: continuation.inputs.target_channel,
            observed_bto_us: observed_bto.0,
            standard_deviation_us: bto_sd.0,
            likelihood: "Gaussian observed-minus-predicted BTO residual",
        },
        structural_pooling: "none",
        seed_pooling: "equal weight within each family only; R600-conditioned particle weights are normalized separately within each seed before equal-seed averaging",
        input_set_sha256: input_set_sha256.clone(),
        input_sha256: input_sha256.clone(),
        families,
        limitations: limitations.clone(),
    };

    fs::create_dir_all(&arguments.output)
        .with_context(|| format!("cannot create {}", arguments.output.display()))?;
    let result_path = arguments.output.join(RESULT_NAME);
    let csv_path = arguments.output.join(CSV_NAME);
    atomic_write(
        &result_path,
        &(serde_json::to_string_pretty(&result)? + "\n").into_bytes(),
    )?;
    atomic_write(&csv_path, csv(&result).as_bytes())?;

    let generator =
        PathBuf::from(env!("CARGO_MANIFEST_DIR")).join("examples/r600_predictive_compatibility.rs");
    let executable = env::current_exe()?;
    let output_sha256 = BTreeMap::from([
        (
            RESULT_NAME.to_string(),
            sha256_bytes(&fs::read(&result_path)?),
        ),
        (CSV_NAME.to_string(), sha256_bytes(&fs::read(&csv_path)?)),
    ]);
    let reproduction_command = format!(
        "cargo run --release -p mh370-runner --example r600_predictive_compatibility -- --suite-config {} --continuation-config {} --source-run {} --output {} --maximum-step-s {} --threads {}",
        arguments.suite_config.display(),
        arguments.continuation_config.display(),
        arguments.source_run.display(),
        arguments.output.display(),
        arguments.maximum_step_s,
        arguments.threads,
    );
    let manifest = OutputManifest {
        schema_version: OUTPUT_MANIFEST_SCHEMA_VERSION,
        result_schema_version: RESULT_SCHEMA_VERSION,
        source_suite_artifact_schema_version: source_artifact_contract
            .suite_artifact_schema_version(),
        source_config_schema_version: suite.schema_version,
        source_handoff_schema_version: source_artifact_contract.handoff_schema_version(),
        threads: arguments.threads,
        generator: generator.display().to_string(),
        generator_source_sha256: sha256_bytes(&fs::read(&generator)?),
        executable_sha256: sha256_bytes(&fs::read(&executable)?),
        input_set_sha256,
        input_sha256,
        output_sha256,
        reproduction_command,
        scientific_scope: limitations,
    };
    let manifest_path = arguments.output.join(MANIFEST_NAME);
    atomic_write(
        &manifest_path,
        &(serde_json::to_string_pretty(&manifest)? + "\n").into_bytes(),
    )?;
    println!(
        "generated {}, {}, and {}",
        result_path.display(),
        csv_path.display(),
        manifest_path.display()
    );
    Ok(())
}

#[cfg(test)]
mod tests {
    use mh370_domain::{Feet, FeetPerMinute, Hertz, Knots};
    use mh370_satcom::{BfoConstants, BtoConstants};

    use super::*;

    fn radar() -> RadarPrior {
        RadarPrior {
            time_s: 0.0,
            latitude_deg: 5.624829,
            longitude_deg: 99.048157,
            position_sd_nm: 0.5,
            control_mean_deg_true: 295.66,
            control_sd_deg: 1.0,
            mach_min: 0.73,
            mach_max: 0.84,
            altitude_min_ft: 25_000.0,
            altitude_max_ft: 43_000.0,
        }
    }

    fn satcom() -> SatcomModelConfig {
        SatcomModelConfig {
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
        }
    }

    fn angular_record(angle_deg: f64, weight: f64) -> ParticleRecord {
        ParticleRecord {
            initial_post_turn_track_true_deg: angle_deg,
            checkpoint_latitude_deg: None,
            checkpoint_longitude_deg: None,
            checkpoint_track_true_deg: None,
            start_latitude_deg: 0.0,
            start_longitude_deg: 0.0,
            start_track_true_deg: angle_deg,
            end_latitude_deg: 0.0,
            end_longitude_deg: 0.0,
            end_track_true_deg: angle_deg,
            end_heading_true_deg: angle_deg,
            residual_us: 0.0,
            normalized_log_prior: weight.ln(),
            log_likelihood: 0.0,
            prior_weight: weight,
            seed_posterior_weight: weight,
            posterior_weight: weight,
        }
    }

    fn scalar_suite(schema_version: u32) -> SuiteConfiguration {
        SuiteConfiguration {
            schema_version,
            name: "fixture".to_string(),
            seeds: vec![7],
            families: vec![FamilyConfiguration {
                name: "constant-true-track".to_string(),
                lateral_mode: LateralMode::ConstantTrueTrack,
                fixed_waypoint: None,
            }],
            inputs: SourceInputsConfiguration {
                observations: "observations.csv".into(),
                satellite_ephemeris: "ephemeris.csv".into(),
                ground_station_position_km: Vec3 {
                    x: -2_368.8,
                    y: 4_881.1,
                    z: -3_342.0,
                },
                fit_through_epoch_id: Some("m0011".to_string()),
            },
            environment: EnvironmentConfiguration {
                era5: "era5.bin".into(),
                igrf: "igrf.bin".into(),
                time_origin_unix_s: 0.0,
                integration_step_s: 30.0,
            },
            convergence: SourceConvergenceConfiguration {
                maximum_seed_mean_separation_nm: 30.0,
                maximum_log_evidence_range: 0.8,
                minimum_mutation_acceptance: 0.02,
            },
            model: SourceModelConfiguration {
                radar: radar(),
                dynamics: OneTurnConfig {
                    turn_time_min_s: 600.0,
                    turn_time_max_s: 3_600.0,
                },
                satcom: satcom(),
            },
        }
    }

    fn scalar_summary(schema_version: u32) -> SourceSuiteSummaryArtifact {
        SourceSuiteSummaryArtifact {
            schema_version,
            config_schema_version: (schema_version == 2).then_some(1),
            handoff_schema_version: (schema_version == 2).then_some(2),
            status: "complete".to_string(),
            families: vec![SourceSummaryFamily {
                name: "constant-true-track".to_string(),
                lateral_mode: LateralMode::ConstantTrueTrack,
                fixed_waypoint: None,
            }],
        }
    }

    fn scalar_manifest(schema_version: u32) -> SourceRunManifestArtifact {
        SourceRunManifestArtifact {
            schema_version,
            config_schema_version: (schema_version == 2).then_some(1),
            handoff_schema_version: (schema_version == 2).then_some(2),
            config_sha256: "a".repeat(64),
            outputs: BTreeMap::new(),
            structural_families: if schema_version == 2 {
                vec![SourceStructuralFamily {
                    name: "constant-true-track".to_string(),
                    lateral_mode: LateralMode::ConstantTrueTrack,
                    fixed_waypoint: None,
                    fixed_waypoint_identity_sha256: None,
                    era5_temperature_wind_active: true,
                    igrf_declination_active: false,
                }]
            } else {
                Vec::new()
            },
        }
    }

    #[test]
    fn source_artifact_schema_matrix_is_explicit() {
        let legacy_suite = scalar_suite(1);
        assert_eq!(
            validate_source_artifact_contract(
                &legacy_suite,
                &scalar_summary(1),
                &scalar_manifest(1),
            )
            .unwrap(),
            SourceArtifactContract::LegacyV1Scalar
        );
        assert_eq!(
            validate_source_artifact_contract(
                &legacy_suite,
                &scalar_summary(2),
                &scalar_manifest(2),
            )
            .unwrap(),
            SourceArtifactContract::CurrentV2
        );
        assert!(validate_source_artifact_contract(
            &legacy_suite,
            &scalar_summary(1),
            &scalar_manifest(2),
        )
        .is_err());

        let mut unsupported = scalar_summary(2);
        unsupported.schema_version = 9;
        assert!(validate_source_artifact_contract(
            &legacy_suite,
            &unsupported,
            &scalar_manifest(2),
        )
        .is_err());
    }

    #[test]
    fn true_reference_legacy_continuation_never_queries_igrf() {
        let mut queried = false;
        let declination = declination_for_mode(LateralMode::ConstantTrueTrack, || {
            queried = true;
            bail!("outside IGRF grid")
        })
        .unwrap();
        assert_eq!(declination, Degrees(0.0));
        assert!(!queried);
        assert!(
            declination_for_mode(LateralMode::ConstantMagneticTrack, || {
                bail!("outside IGRF grid")
            })
            .is_err()
        );
    }

    #[test]
    fn exact_log_ratio_survives_linear_overflow_and_underflow() {
        assert_eq!(finite_linear_ratio(0.0), Some(1.0));
        assert!(finite_linear_ratio(710.0).is_none());
        assert!(finite_linear_ratio(-1_000.0).is_none());
    }

    #[test]
    fn angular_summary_unwraps_across_north() {
        let records = [angular_record(359.0, 0.5), angular_record(1.0, 0.5)];
        let summary = angular_summary(
            &records,
            |record| record.end_track_true_deg,
            |record| record.prior_weight,
        )
        .unwrap();
        assert!(angular_difference_deg(summary.circular_mean_deg, 0.0).abs() < 1e-10);
        assert!((summary.central_90_deg[1] - summary.central_90_deg[0] - 2.0).abs() < 1e-10);
        assert!(
            (summary.central_90_deg[0] <= 0.0 && summary.central_90_deg[1] >= 0.0)
                || (summary.central_90_deg[0] <= 360.0 && summary.central_90_deg[1] >= 360.0)
        );
    }

    #[test]
    fn current_v2_replay_rejects_a_mismatched_source_state() {
        let parameters = OneTurnParameters {
            initial_latitude_deg: 5.0,
            initial_longitude_deg: 99.0,
            initial_track_true_deg: 295.0,
            turn_time_s: 2_000.0,
            post_turn_track_true_deg: 185.0,
            mach: 0.82,
            altitude_ft: 35_000.0,
        };
        let state = AircraftState {
            time: Seconds(22_150.0),
            position: LatLon::new(-36.0, 89.0).unwrap(),
            altitude: Feet(35_000.0),
            track_true: Degrees(186.0),
            ground_speed: Knots(480.0),
            vertical_speed: FeetPerMinute(0.0),
            bfo_bias: Hertz(150.0),
        };
        let replayed = mh370_dynamics::OneTurnTrajectory {
            parameters,
            aircraft: state,
            turn_count: 1,
            heading_true: Degrees(187.0),
        };
        validate_replayed_source_state(&replayed, &state, Degrees(187.0)).unwrap();

        let mut mismatched = state;
        mismatched.position = LatLon::new(-36.01, 89.0).unwrap();
        assert!(validate_replayed_source_state(&replayed, &mismatched, Degrees(187.0)).is_err());
    }

    #[test]
    fn canonical_legacy_v1_artifacts_remain_readable() {
        let root = PathBuf::from(env!("CARGO_MANIFEST_DIR")).join("../..");
        let config_path = root.join("configs/mh370-through-0011-autopilot-modes-medium.toml");
        let run = root.join("runs/mh370/through-0011-autopilot-modes-medium");
        let suite: SuiteConfiguration =
            toml::from_str(&fs::read_to_string(config_path).unwrap()).unwrap();
        let summary: SourceSuiteSummaryArtifact =
            serde_json::from_slice(&fs::read(run.join("suite-summary.json")).unwrap()).unwrap();
        let manifest: SourceRunManifestArtifact =
            serde_json::from_slice(&fs::read(run.join("run-manifest.json")).unwrap()).unwrap();
        assert_eq!(
            validate_source_artifact_contract(&suite, &summary, &manifest).unwrap(),
            SourceArtifactContract::LegacyV1Scalar
        );
        let handoff: PosteriorHandoff = serde_json::from_slice(
            &fs::read(run.join("constant-true-track/seed-370023/posterior-handoff.json")).unwrap(),
        )
        .unwrap();
        handoff.validate().unwrap();
        assert_eq!(handoff.schema_version, 1);
    }
}
