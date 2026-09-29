use std::{
    collections::{BTreeMap, BTreeSet},
    fs,
    path::{Path, PathBuf},
    time::Instant,
};

use anyhow::{bail, Context, Result};
use mh370_antenna::{geometry as antenna_geometry, AntennaPattern};
use mh370_domain::{
    great_circle_distance_nm, Degrees, ImpactPoint, LatLon, NauticalMiles, Seconds, Vec3,
};
use mh370_dynamics::{
    Era5Grid, FixedWaypointLeg, IgrfGrid, LateralGuidance, LateralMode, NavigationEnvironment,
};
use mh370_estimator::{
    final_posterior_rows, parse_satcom_observations,
    run_final_flight_estimate_with_environment_and_likelihood, EvidenceComponent,
    EvidenceDisposition, EvidenceIdentity, EvidenceLedger, FinalFlightConfig,
    FinalFlightLikelihood, FinalFlightRun, FinalFlightSummary, FixedWaypointMetadata,
    PosteriorHandoff, PosteriorHandoffParticle, PosteriorParticleIdentity, PosteriorRunMetadata,
    TurnMetadata, POSTERIOR_HANDOFF_SCHEMA_VERSION,
};
use mh370_hydroacoustics::HydroEvent;
use mh370_reporting::{
    build_accident_panel_png, build_pdf, build_posterior_svg, compare_spatial_posteriors,
    DiagnosticPoint, PosteriorSpatialComparison, ReportDocument, ReportMapContext, ReportPoint,
};
use rayon::ThreadPoolBuilder;
use serde::{Deserialize, Serialize};
use serde_json::json;

use crate::{
    accident_antenna::{AccidentAntennaConfig, AccidentAntennaLikelihood},
    atomic_write, executable_sha256,
    ocean_drift_application::{apply_source_area, DriftApplicationSummary},
    prepare_output, sha256_bytes, sha256_file, write_json,
};

const SUITE_SUMMARY_SCHEMA_VERSION: u32 = 2;
const RUN_MANIFEST_SCHEMA_VERSION: u32 = 2;
const SEED_SUMMARY_SCHEMA_VERSION: u32 = 2;
const POSTERIOR_CSV_SCHEMA_VERSION: u32 = 2;

#[derive(Debug, Clone, Deserialize)]
#[serde(deny_unknown_fields)]
struct InputConfig {
    observations: PathBuf,
    satellite_ephemeris: PathBuf,
    ground_station_position_km: Vec3,
    /// Optional explicit guard against accidentally fitting later contacts.
    fit_through_epoch_id: Option<String>,
}

#[derive(Debug, Clone, PartialEq, Deserialize)]
#[serde(deny_unknown_fields)]
struct FixedWaypointConfig {
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

impl FixedWaypointConfig {
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

#[derive(Debug, Clone, Deserialize)]
#[serde(deny_unknown_fields)]
struct FamilyConfig {
    name: String,
    use_bfo: bool,
    bfo_sd_override_hz: Option<f64>,
    #[serde(default)]
    use_antenna_gain: bool,
    #[serde(default)]
    lateral_mode: LateralMode,
    fixed_waypoint: Option<FixedWaypointConfig>,
}

impl FamilyConfig {
    fn lateral_guidance(&self) -> Result<LateralGuidance> {
        match &self.fixed_waypoint {
            Some(route) => Ok(LateralGuidance::DirectTo(FixedWaypointLeg::new(
                LatLon::new(route.latitude_deg, route.longitude_deg)
                    .context("fixed-waypoint coordinate is invalid")?,
                NauticalMiles(route.arrival_radius_nm),
            )?)),
            None => Ok(LateralGuidance::SelectedControl(self.lateral_mode)),
        }
    }
}

fn same_non_gain_settings(first: &FamilyConfig, second: &FamilyConfig) -> bool {
    first.use_bfo == second.use_bfo
        && first.bfo_sd_override_hz == second.bfo_sd_override_hz
        && first.lateral_mode == second.lateral_mode
        && first.fixed_waypoint == second.fixed_waypoint
}

fn single_factor_change(first: &FamilyConfig, second: &FamilyConfig) -> Option<String> {
    if same_non_gain_settings(first, second) && first.use_antenna_gain != second.use_antenna_gain {
        return Some("conditional_antenna_gain".to_string());
    }
    if !first.use_antenna_gain
        && !second.use_antenna_gain
        && first.lateral_mode == second.lateral_mode
        && first.fixed_waypoint == second.fixed_waypoint
        && first.use_bfo != second.use_bfo
    {
        return Some("bfo".to_string());
    }
    None
}

#[derive(Debug, Clone, Deserialize)]
#[serde(deny_unknown_fields)]
struct EnvironmentConfig {
    era5: PathBuf,
    igrf: PathBuf,
    time_origin_unix_s: f64,
    integration_step_s: f64,
}

#[derive(Debug, Clone, Deserialize)]
#[serde(deny_unknown_fields)]
struct ConvergenceConfig {
    maximum_seed_mean_separation_nm: f64,
    maximum_log_evidence_range: f64,
    minimum_mutation_acceptance: f64,
}

#[derive(Debug, Clone, Deserialize)]
struct DriftContextConfig {
    maximum_cell_distance_nm: f64,
    application: Option<DriftApplicationConfig>,
}

#[derive(Debug, Clone, Deserialize)]
struct DriftApplicationConfig {
    source_area: PathBuf,
    family: String,
    isotope_enabled: bool,
}

#[derive(Debug, Clone, Default, Deserialize)]
struct EvidenceConfig {
    drift: Option<DriftContextConfig>,
    #[serde(default)]
    hydro_events: Vec<HydroEvent>,
    antenna_pattern: Option<AntennaPattern>,
    antenna_gain: Option<AccidentAntennaConfig>,
}

#[derive(Debug, Clone, Deserialize)]
#[serde(deny_unknown_fields)]
struct SuiteConfig {
    schema_version: u32,
    name: String,
    inputs: InputConfig,
    seeds: Vec<u64>,
    families: Vec<FamilyConfig>,
    #[serde(default)]
    paired_comparisons: Vec<PairedComparisonConfig>,
    convergence: ConvergenceConfig,
    model: FinalFlightConfig,
    environment: Option<EnvironmentConfig>,
    #[serde(default)]
    evidence: EvidenceConfig,
    map_context: Option<ReportMapContext>,
}

#[derive(Debug, Clone, Deserialize)]
#[serde(deny_unknown_fields)]
struct PairedComparisonConfig {
    reference_family: String,
    comparison_family: String,
    single_factor_change: String,
}

#[derive(Debug, Clone, Serialize)]
struct SeedResult {
    seed: u64,
    summary: FinalFlightSummary,
    output: String,
    posterior_handoff: String,
}

#[derive(Debug, Clone, Serialize)]
struct SeedArtifactSummary {
    schema_version: u32,
    config_schema_version: u32,
    handoff_schema_version: u32,
    run: PosteriorRunMetadata,
    fixed_waypoint_identity_sha256: Option<String>,
    summary: FinalFlightSummary,
}

#[derive(Debug, Clone, Serialize)]
struct FamilyResult {
    name: String,
    use_bfo: bool,
    bfo_sd_override_hz: Option<f64>,
    antenna_gain_applied: bool,
    lateral_mode: LateralMode,
    fixed_waypoint: Option<FixedWaypointMetadata>,
    environment_applied: bool,
    weather_applied: bool,
    magnetic_declination_applied: bool,
    seeds: Vec<SeedResult>,
    pooled_particles: usize,
    pooled_mean: LatLon,
    pooled_latitude_90_deg: [f64; 2],
    pooled_longitude_90_deg: [f64; 2],
    minimum_posterior_ess: f64,
    minimum_tempered_ess: f64,
    minimum_mutation_acceptance: Option<f64>,
    maximum_seed_mean_separation_nm: Option<f64>,
    log_evidence_range: f64,
    converged: Option<bool>,
    elapsed_seconds: f64,
    report_pdf: String,
    posterior_svg: String,
    posterior_png: String,
    conditional_evidence: serde_json::Value,
}

#[derive(Debug, Serialize)]
struct SuiteResult {
    schema_version: u32,
    config_schema_version: u32,
    handoff_schema_version: u32,
    name: String,
    status: String,
    threads: usize,
    elapsed_seconds: f64,
    families: Vec<FamilyResult>,
    family_comparisons: Vec<FamilyComparisonResult>,
}

#[derive(Debug, Clone, Serialize)]
struct FamilyComparisonResult {
    reference_family: String,
    comparison_family: String,
    centroid_separation_nm: f64,
    single_factor_change: Option<String>,
    spatial: PosteriorSpatialComparison,
}

#[derive(Debug, Serialize)]
struct FamilyComparisonArtifact<'a> {
    schema_version: u32,
    suite_name: &'a str,
    interpretation: &'static str,
    comparisons: &'a [FamilyComparisonResult],
}

#[derive(Debug, Serialize)]
struct SuiteManifest {
    schema_version: u32,
    config_schema_version: u32,
    handoff_schema_version: u32,
    engine_version: &'static str,
    executable_sha256: String,
    command: &'static str,
    config_path: String,
    config_sha256: String,
    input_sha256: BTreeMap<String, String>,
    outputs: BTreeMap<String, String>,
    structural_families: Vec<StructuralFamilyIdentity>,
    scientific_scope: Vec<String>,
}

#[derive(Debug, Clone, Serialize)]
struct StructuralFamilyIdentity {
    name: String,
    lateral_mode: LateralMode,
    fixed_waypoint: Option<FixedWaypointMetadata>,
    fixed_waypoint_identity_sha256: Option<String>,
    era5_temperature_wind_active: bool,
    igrf_declination_active: bool,
}

#[derive(Debug, Serialize)]
struct RunIdentityPreimage<'a> {
    domain: &'static str,
    engine_version: &'static str,
    executable_sha256: &'a str,
    config_sha256: &'a str,
    input_sha256: &'a BTreeMap<String, String>,
    model_family: &'a str,
    seed: u64,
}

fn load_config(path: &Path) -> Result<(SuiteConfig, Vec<u8>)> {
    let bytes = fs::read(path).with_context(|| format!("cannot read {}", path.display()))?;
    let text = std::str::from_utf8(&bytes).context("suite configuration is not UTF-8")?;
    let config: SuiteConfig = toml::from_str(text).context("cannot parse accident-suite TOML")?;
    if !matches!(config.schema_version, 1 | 2)
        || config.name.trim().is_empty()
        || config.seeds.is_empty()
        || config.families.is_empty()
    {
        bail!("accident-suite configuration is incomplete");
    }
    if config.seeds.iter().copied().collect::<BTreeSet<_>>().len() != config.seeds.len() {
        bail!("accident-suite seeds must be unique numerical replicates");
    }
    config.model.validate().map_err(anyhow::Error::new)?;
    let convergence = &config.convergence;
    if !convergence.maximum_seed_mean_separation_nm.is_finite()
        || convergence.maximum_seed_mean_separation_nm <= 0.0
        || !convergence.maximum_log_evidence_range.is_finite()
        || convergence.maximum_log_evidence_range <= 0.0
        || !convergence.minimum_mutation_acceptance.is_finite()
        || !(0.0..=1.0).contains(&convergence.minimum_mutation_acceptance)
    {
        bail!("convergence thresholds are invalid");
    }
    let mut family_names = BTreeSet::new();
    for family in &config.families {
        if !family_names.insert(&family.name) {
            bail!("accident-suite family names must be unique");
        }
        if family.name.is_empty()
            || !family.name.chars().all(|character| {
                character.is_ascii_alphanumeric() || matches!(character, '-' | '_')
            })
        {
            bail!("family names must be non-empty path-safe descriptive names");
        }
        if let Some(sd) = family.bfo_sd_override_hz {
            if !sd.is_finite() || sd <= 0.0 {
                bail!("family BFO SD overrides must be finite and positive");
            }
        }
        if config.schema_version == 1
            && (family.lateral_mode == LateralMode::LateralNavigation
                || family.fixed_waypoint.is_some())
        {
            bail!("schema-v1 accident suites only support scalar lateral-control families");
        }
        match (family.lateral_mode, &family.fixed_waypoint) {
            (LateralMode::LateralNavigation, Some(route)) => {
                let metadata = route.metadata()?;
                if metadata.target_name.trim().is_empty()
                    || !metadata.arrival_radius.is_finite()
                    || metadata.arrival_radius.0 <= 0.0
                    || metadata.coordinate_source_title.trim().is_empty()
                    || metadata.coordinate_source_uri.trim().is_empty()
                    || metadata.coordinate_frame_assumption.trim().is_empty()
                    || metadata.coordinate_note.trim().is_empty()
                    || metadata
                        .coordinate_source_date
                        .as_ref()
                        .is_some_and(|date| date.trim().is_empty())
                {
                    bail!("fixed-waypoint metadata is incomplete or invalid");
                }
            }
            (LateralMode::LateralNavigation, None) => {
                bail!("LNAV requires one explicit fixed waypoint");
            }
            (_, Some(_)) => {
                bail!("fixed-waypoint metadata is only valid for an LNAV family");
            }
            (_, None) => {}
        }
        if family.lateral_mode != LateralMode::ConstantTrueTrack && config.environment.is_none() {
            bail!("non-default lateral guidance requires the declared navigation environment");
        }
    }
    let mut comparison_pairs = BTreeSet::new();
    for comparison in &config.paired_comparisons {
        let reference = config
            .families
            .iter()
            .find(|family| family.name == comparison.reference_family)
            .context("paired-comparison reference family is absent")?;
        let candidate = config
            .families
            .iter()
            .find(|family| family.name == comparison.comparison_family)
            .context("paired-comparison candidate family is absent")?;
        if reference.name == candidate.name
            || !comparison_pairs.insert((&reference.name, &candidate.name))
            || single_factor_change(reference, candidate).as_deref()
                != Some(comparison.single_factor_change.as_str())
        {
            bail!(
                "paired comparison {} to {} is duplicated or is not the declared single-factor change",
                reference.name,
                candidate.name
            );
        }
    }
    if let Some(environment) = &config.environment {
        if !environment.time_origin_unix_s.is_finite()
            || !environment.integration_step_s.is_finite()
            || environment.integration_step_s <= 0.0
        {
            bail!("environment integration settings are invalid");
        }
    }
    if config
        .inputs
        .fit_through_epoch_id
        .as_ref()
        .is_some_and(|epoch| epoch.trim().is_empty())
    {
        bail!("fit-through epoch identifier must not be empty");
    }
    Ok((config, bytes))
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

fn posterior_csv(
    run: &FinalFlightRun,
    metadata: &PosteriorRunMetadata,
    config_schema_version: u32,
) -> Result<Vec<u8>> {
    let route_identity = metadata
        .fixed_waypoint
        .as_ref()
        .map(fixed_waypoint_identity)
        .transpose()?
        .unwrap_or_default();
    let (route_latitude, route_longitude, route_radius) = metadata
        .fixed_waypoint
        .as_ref()
        .map(|route| {
            (
                route.position.latitude.0.to_string(),
                route.position.longitude.0.to_string(),
                route.arrival_radius.0.to_string(),
            )
        })
        .unwrap_or_default();
    let mut output = String::from(
        "artifact_schema_version,config_schema_version,handoff_schema_version,model_family,run_identity_sha256,lateral_mode,fixed_waypoint_identity_sha256,fixed_waypoint_latitude_deg,fixed_waypoint_longitude_deg,fixed_waypoint_arrival_radius_nm,particle,weight,last_contact_time_s,last_contact_latitude_deg,last_contact_longitude_deg,impact_time_s,impact_latitude_deg,impact_longitude_deg,impact_displacement_nm,altitude_ft,track_true_deg,ground_speed_kt,mach,bfo_bias_hz,turn_time_s,post_turn_track_true_deg\n",
    );
    for (index, (particle, impact, weight)) in final_posterior_rows(run).enumerate() {
        let state = &particle.trajectory;
        let parameters = &particle.parameters;
        let _ = std::fmt::Write::write_fmt(
            &mut output,
            format_args!(
                "{},{},{},{},{},{},{},{},{},{},{index},{weight:.17e},{:.6},{:.12},{:.12},{:.6},{:.12},{:.12},{:.9},{:.3},{:.9},{:.9},{:.9},{:.9},{:.6},{:.9}\n",
                POSTERIOR_CSV_SCHEMA_VERSION,
                config_schema_version,
                POSTERIOR_HANDOFF_SCHEMA_VERSION,
                metadata.model_family,
                metadata.run_identity_sha256,
                lateral_mode_token(
                    metadata
                        .lateral_mode
                        .expect("validated writer metadata has a lateral mode"),
                ),
                route_identity,
                route_latitude,
                route_longitude,
                route_radius,
                state.aircraft.time.0,
                state.aircraft.position.latitude.0,
                state.aircraft.position.longitude.0,
                impact.time.0,
                impact.position.latitude.0,
                impact.position.longitude.0,
                impact.displacement_from_last_contact.0,
                state.aircraft.altitude.0,
                state.aircraft.track_true.0,
                state.aircraft.ground_speed.0,
                parameters.mach,
                particle.bfo_bias.mean_hz,
                parameters.turn_time_s,
                particle.post_turn_track_true.0,
            ),
        );
    }
    Ok(output.into_bytes())
}

fn write_seed(
    output: &Path,
    run: &FinalFlightRun,
    metadata: &PosteriorRunMetadata,
    config_schema_version: u32,
) -> Result<()> {
    validate_seed_artifact_identity(run.summary.lateral_mode, metadata)?;
    fs::create_dir_all(output).with_context(|| format!("cannot create {}", output.display()))?;
    let fixed_waypoint_identity_sha256 = metadata
        .fixed_waypoint
        .as_ref()
        .map(fixed_waypoint_identity)
        .transpose()?;
    write_json(
        &output.join("summary.json"),
        &SeedArtifactSummary {
            schema_version: SEED_SUMMARY_SCHEMA_VERSION,
            config_schema_version,
            handoff_schema_version: POSTERIOR_HANDOFF_SCHEMA_VERSION,
            run: metadata.clone(),
            fixed_waypoint_identity_sha256,
            summary: run.summary.clone(),
        },
    )?;
    write_json(&output.join("checkpoints.json"), &run.filter.checkpoints)?;
    atomic_write(
        &output.join("posterior.csv"),
        &posterior_csv(run, metadata, config_schema_version)?,
    )?;
    Ok(())
}

fn run_identity(
    executable_digest: &str,
    config_digest: &str,
    input_sha256: &BTreeMap<String, String>,
    model_family: &str,
    seed: u64,
) -> Result<String> {
    let bytes = serde_json::to_vec(&RunIdentityPreimage {
        domain: "mh370-estimate-run-v1",
        engine_version: env!("CARGO_PKG_VERSION"),
        executable_sha256: executable_digest,
        config_sha256: config_digest,
        input_sha256,
        model_family,
        seed,
    })?;
    Ok(sha256_bytes(&bytes))
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

fn validate_seed_artifact_identity(
    lateral_mode: LateralMode,
    metadata: &PosteriorRunMetadata,
) -> Result<()> {
    if metadata.lateral_mode != Some(lateral_mode)
        || (lateral_mode == LateralMode::LateralNavigation) != metadata.fixed_waypoint.is_some()
    {
        bail!("standalone seed artifact guidance identity is incomplete or inconsistent");
    }
    if let Some(route) = &metadata.fixed_waypoint {
        if route.target_name.trim().is_empty()
            || !route.arrival_radius.is_finite()
            || route.arrival_radius.0 <= 0.0
            || route.coordinate_source_title.trim().is_empty()
            || route.coordinate_source_uri.trim().is_empty()
            || route.coordinate_frame_assumption.trim().is_empty()
            || route.coordinate_note.trim().is_empty()
        {
            bail!("standalone LNAV seed artifact lacks complete route provenance");
        }
    }
    Ok(())
}

fn build_evidence_ledger(
    run: &FinalFlightRun,
    family: &FamilyConfig,
    antenna: Option<&AccidentAntennaLikelihood>,
) -> Result<EvidenceLedger> {
    let mut ledger = EvidenceLedger::new();
    for observation in &run.observations {
        if observation.measurement.bto.is_some() {
            ledger.record(
                EvidenceIdentity {
                    epoch_id: observation.id.clone(),
                    channel: None,
                    component: EvidenceComponent::Bto,
                },
                EvidenceDisposition::Consumed,
            )?;
        }
        if observation.measurement.bfo.is_some() {
            ledger.record(
                EvidenceIdentity {
                    epoch_id: observation.id.clone(),
                    channel: None,
                    component: EvidenceComponent::Bfo,
                },
                if family.use_bfo {
                    EvidenceDisposition::Consumed
                } else {
                    EvidenceDisposition::HeldOut
                },
            )?;
        }
    }
    if let Some(antenna) = antenna {
        for (epoch_id, channel) in antenna.evidence_identities() {
            ledger.record(
                EvidenceIdentity {
                    epoch_id: epoch_id.to_string(),
                    channel: Some(channel.to_string()),
                    component: EvidenceComponent::ReceivedPower,
                },
                if family.use_antenna_gain {
                    EvidenceDisposition::Consumed
                } else {
                    EvidenceDisposition::HeldOut
                },
            )?;
        }
    }
    Ok(ledger)
}

fn build_posterior_handoff(
    run: &FinalFlightRun,
    family: &FamilyConfig,
    antenna: Option<&AccidentAntennaLikelihood>,
    executable_digest: &str,
    config_digest: &str,
    input_sha256: &BTreeMap<String, String>,
    handoff_schema_version: u32,
) -> Result<PosteriorHandoff> {
    if run.posterior.len() != run.filter.log_weights.len()
        || run.posterior.len() != run.filter.log_likelihoods.len()
    {
        bail!("posterior and filter populations have inconsistent lengths");
    }
    let retained = run
        .filter
        .log_weights
        .iter()
        .enumerate()
        .filter_map(|(index, weight)| weight.is_finite().then_some(index))
        .collect::<Vec<_>>();
    if retained.is_empty() {
        bail!("posterior handoff has no finite-weight particles");
    }
    let maximum = retained
        .iter()
        .map(|index| run.filter.log_weights[*index])
        .fold(f64::NEG_INFINITY, f64::max);
    let log_normalizer = maximum
        + retained
            .iter()
            .map(|index| (run.filter.log_weights[*index] - maximum).exp())
            .sum::<f64>()
            .ln();
    let particles = retained
        .into_iter()
        .map(|index| {
            let particle = &run.posterior[index];
            let parameters = particle.parameters;
            let source_log_likelihood = run.filter.log_likelihoods[index];
            if !source_log_likelihood.is_finite() {
                bail!("finite-weight particle {index} has a non-finite source likelihood");
            }
            Ok(PosteriorHandoffParticle {
                identity: PosteriorParticleIdentity {
                    model_family: family.name.clone(),
                    seed: run.seed,
                    particle: index,
                },
                normalized_log_weight: run.filter.log_weights[index] - log_normalizer,
                source_log_likelihood,
                aircraft: particle.trajectory.aircraft,
                heading_true: particle.trajectory.heading_true,
                lateral_mode: family.lateral_mode,
                mach: parameters.mach,
                turn: TurnMetadata {
                    initial_position: LatLon::new(
                        parameters.initial_latitude_deg,
                        parameters.initial_longitude_deg,
                    )
                    .context("posterior initial coordinate is invalid")?,
                    initial_track_true: Degrees(parameters.initial_track_true_deg).wrapped_360(),
                    turn_time: Seconds(parameters.turn_time_s),
                    post_turn_track_true: particle.post_turn_track_true.wrapped_360(),
                    turn_count: particle.trajectory.turn_count,
                },
                bfo_bias: particle.bfo_bias,
            })
        })
        .collect::<Result<Vec<_>>>()?;
    let handoff = PosteriorHandoff {
        schema_version: handoff_schema_version,
        run: PosteriorRunMetadata {
            model_family: family.name.clone(),
            seed: run.seed,
            lateral_mode: Some(family.lateral_mode),
            run_identity_sha256: run_identity(
                executable_digest,
                config_digest,
                input_sha256,
                &family.name,
                run.seed,
            )?,
            config_sha256: config_digest.to_string(),
            input_sha256: input_sha256.clone(),
            fixed_waypoint: family
                .fixed_waypoint
                .as_ref()
                .map(FixedWaypointConfig::metadata)
                .transpose()?,
        },
        evidence: build_evidence_ledger(run, family, antenna)?,
        particles,
    };
    handoff
        .validate()
        .map_err(anyhow::Error::new)
        .context("generated posterior handoff is invalid")?;
    Ok(handoff)
}

fn weighted_quantile(points: &[ReportPoint], latitude: bool, probability: f64) -> f64 {
    let mut values = points
        .iter()
        .map(|point| {
            (
                if latitude {
                    point.latitude_deg
                } else {
                    point.longitude_deg
                },
                point.weight,
            )
        })
        .collect::<Vec<_>>();
    values.sort_by(|first, second| first.0.total_cmp(&second.0));
    let total = values.iter().map(|value| value.1).sum::<f64>();
    let mut cumulative = 0.0;
    for (value, weight) in values {
        cumulative += weight;
        if cumulative >= probability * total {
            return value;
        }
    }
    f64::NAN
}

fn pooled_mean(points: &[ReportPoint]) -> LatLon {
    let total = points.iter().map(|point| point.weight).sum::<f64>();
    let latitude = points
        .iter()
        .map(|point| point.latitude_deg * point.weight)
        .sum::<f64>()
        / total;
    let sin_longitude = points
        .iter()
        .map(|point| point.longitude_deg.to_radians().sin() * point.weight)
        .sum::<f64>()
        / total;
    let cos_longitude = points
        .iter()
        .map(|point| point.longitude_deg.to_radians().cos() * point.weight)
        .sum::<f64>()
        / total;
    LatLon::new(latitude, sin_longitude.atan2(cos_longitude).to_degrees())
        .expect("pooled mean is a valid coordinate")
}

fn maximum_seed_separation_nm(runs: &[FinalFlightRun]) -> Option<f64> {
    if runs.len() < 2 {
        return None;
    }
    let mut maximum: f64 = 0.0;
    for first in 0..runs.len() {
        for second in (first + 1)..runs.len() {
            maximum = maximum.max(
                great_circle_distance_nm(
                    runs[first].summary.impact_mean,
                    runs[second].summary.impact_mean,
                )
                .0,
            );
        }
    }
    Some(maximum)
}

fn log_evidence_range(runs: &[FinalFlightRun]) -> f64 {
    let minimum = runs
        .iter()
        .map(|run| run.summary.log_evidence)
        .fold(f64::INFINITY, f64::min);
    let maximum = runs
        .iter()
        .map(|run| run.summary.log_evidence)
        .fold(f64::NEG_INFINITY, f64::max);
    maximum - minimum
}

fn family_comparison_csv(comparisons: &[FamilyComparisonResult]) -> Vec<u8> {
    let mut output = String::from(
        "reference_family,comparison_family,single_factor_change,centroid_separation_nm,overlap_coefficient,total_variation_distance,jensen_shannon_divergence_nats,reference_hpd50_km2,reference_hpd90_km2,reference_hpd95_km2,reference_hpd99_km2,comparison_hpd50_km2,comparison_hpd90_km2,comparison_hpd95_km2,comparison_hpd99_km2\n",
    );
    for comparison in comparisons {
        let first = comparison.spatial.first_hpd_area_km2;
        let second = comparison.spatial.second_hpd_area_km2;
        let _ = std::fmt::Write::write_fmt(
            &mut output,
            format_args!(
                "{},{},{},{:.9},{:.12},{:.12},{:.12},{:.6},{:.6},{:.6},{:.6},{:.6},{:.6},{:.6},{:.6}\n",
                comparison.reference_family,
                comparison.comparison_family,
                comparison.single_factor_change.as_deref().unwrap_or("multiple"),
                comparison.centroid_separation_nm,
                comparison.spatial.overlap_coefficient,
                comparison.spatial.total_variation_distance,
                comparison.spatial.jensen_shannon_divergence_nats,
                first.mass_50,
                first.mass_90,
                first.mass_95,
                first.mass_99,
                second.mass_50,
                second.mass_90,
                second.mass_95,
                second.mass_99,
            ),
        );
    }
    output.into_bytes()
}

fn aggregate_diagnostics(runs: &[FinalFlightRun]) -> Vec<DiagnosticPoint> {
    let count = runs
        .iter()
        .map(|run| run.filter.checkpoints.len())
        .min()
        .unwrap_or(0);
    (0..count)
        .map(|index| {
            let temperature = runs
                .iter()
                .map(|run| run.filter.checkpoints[index].temperature)
                .sum::<f64>()
                / runs.len() as f64;
            let ess = runs
                .iter()
                .map(|run| run.filter.checkpoints[index].particle_ess)
                .sum::<f64>()
                / runs.len() as f64;
            let increment = runs
                .iter()
                .map(|run| run.filter.checkpoints[index].log_evidence_increment)
                .sum::<f64>()
                / runs.len() as f64;
            DiagnosticPoint {
                label: if temperature < 0.01 {
                    format!("t {temperature:.1e}")
                } else {
                    format!("t {temperature:.2}")
                },
                effective_sample_size: ess,
                log_evidence_increment: increment,
            }
        })
        .collect()
}

fn conditional_evidence(
    config: &EvidenceConfig,
    runs: &[FinalFlightRun],
    mean: LatLon,
    antenna_gain: Option<&AccidentAntennaLikelihood>,
    antenna_gain_applied: bool,
    drift_application: Option<&DriftApplicationSummary>,
) -> Result<serde_json::Value> {
    let run = runs.first().context("accident family has no runs")?;
    let final_observation = run
        .observations
        .last()
        .context("accident run has no observations")?;
    let representative_index = run
        .filter
        .log_weights
        .iter()
        .enumerate()
        .max_by(|first, second| first.1.total_cmp(second.1))
        .map(|item| item.0)
        .context("accident run has no particles")?;
    let representative = &run.posterior[representative_index];
    let impact = ImpactPoint {
        time: Seconds(run.impacts[representative_index].time.0),
        position: mean,
        bearing_true: representative.trajectory.aircraft.track_true,
        displacement_from_last_contact: NauticalMiles(0.0),
    };

    let hydro = config
        .hydro_events
        .iter()
        .map(|event| {
            event
                .score(impact)
                .map(|score| json!(score))
                .unwrap_or_else(|error| json!({"event": event.name, "error": error.to_string()}))
        })
        .collect::<Vec<_>>();

    let antenna = if let Some(gain) = antenna_gain {
        gain.metadata(antenna_gain_applied)
    } else if let Some(pattern) = config.antenna_pattern {
        match antenna_geometry(
            representative.trajectory.aircraft,
            final_observation.measurement.satellite_position_km,
            pattern,
        ) {
            Ok(value) => json!({
                "applied_to_posterior": false,
                "pattern_basis": pattern.basis,
                "geometry": value,
                "reason": "geometry only; no commissioned measured gain surface or resolved precompensation",
            }),
            Err(error) => json!({"error": error.to_string()}),
        }
    } else {
        json!(null)
    };

    Ok(json!({
        "drift_application": drift_application,
        "hydroacoustics": hydro,
        "antenna": antenna,
    }))
}

fn format_latitude(latitude_deg: f64, precision: usize) -> String {
    format!(
        "{:.*} deg {}",
        precision,
        latitude_deg.abs(),
        if latitude_deg < 0.0 { "S" } else { "N" }
    )
}

fn format_longitude(longitude_deg: f64, precision: usize) -> String {
    format!(
        "{:.*} deg {}",
        precision,
        longitude_deg.abs(),
        if longitude_deg < 0.0 { "W" } else { "E" }
    )
}

fn report_document(
    suite_name: &str,
    family: &FamilyConfig,
    runs: &[FinalFlightRun],
    points: Vec<ReportPoint>,
    mean: LatLon,
    latitude_90: [f64; 2],
    longitude_90: [f64; 2],
    minimum_ess: f64,
    minimum_tempered_ess: f64,
    minimum_mutation_acceptance: Option<f64>,
    maximum_seed_mean_separation_nm: Option<f64>,
    log_evidence_range: f64,
    converged: Option<bool>,
    drift_applied: bool,
    hydro_count: usize,
    antenna_geometry_present: bool,
    antenna_gain_applied: bool,
    map_context: Option<ReportMapContext>,
) -> ReportDocument {
    let particles = runs
        .iter()
        .map(|run| run.filter.particles.len())
        .sum::<usize>();
    let mut conditions = vec![
        format!(
            "SATCOM family: {}.",
            if family.use_bfo {
                format!(
                    "BTO and BFO, BFO SD {} Hz",
                    family
                        .bfo_sd_override_hz
                        .map(|value| format!("{value:.3}"))
                        .unwrap_or_else(|| "from input".to_string())
                )
            } else {
                "BTO only".to_string()
            }
        ),
        if runs[0].summary.impact_displacement_90_nm[1] == 0.0 {
            "End of flight: final SATCOM state; no displacement kernel applied.".to_string()
        } else {
            format!(
                "End-of-flight displacement: {:.1} to {:.1} NM (90% interval).",
                runs[0].summary.impact_displacement_90_nm[0],
                runs[0].summary.impact_displacement_90_nm[1]
            )
        },
    ];
    conditions.insert(
        0,
        format!(
            "Lateral model: {}; {}",
            family.lateral_mode.name(),
            if runs[0].summary.weather_applied
                && runs[0].summary.magnetic_declination_applied
            {
                "ERA5 temperature/wind and IGRF-14 declination active."
            } else if runs[0].summary.weather_applied {
                "ERA5 temperature/wind active; IGRF-14 declination inactive for true-reference guidance."
            } else {
                "historical navigation environment not applied."
            }
        ),
    );
    if let Some(route) = &family.fixed_waypoint {
        conditions.insert(
            1,
            format!(
                "Conditional fixed waypoint: {} at {}, {}; arrival radius {:.2} NM. Coordinate source: {} ({}).",
                route.target_name,
                format_latitude(route.latitude_deg, 6),
                format_longitude(route.longitude_deg, 6),
                route.arrival_radius_nm,
                route.coordinate_source_title,
                route.coordinate_source_uri,
            ),
        );
        conditions.insert(
            2,
            format!("Waypoint provenance limitation: {}", route.coordinate_note),
        );
        conditions.insert(
            2,
            format!(
                "Waypoint coordinate-frame assumption: {}",
                route.coordinate_frame_assumption
            ),
        );
    }
    conditions.push(match converged {
        Some(true) => "Cross-seed numerical convergence: passed.".to_string(),
        Some(false) => {
            "Cross-seed numerical convergence: failed; treat this run as diagnostic.".to_string()
        }
        None => {
            "Cross-seed numerical convergence: unassessed in a single-seed smoke run.".to_string()
        }
    });
    if drift_applied {
        conditions.push(
            "The explicitly selected, family-specific ocean-drift source likelihood is applied to every weighted flight particle; the source-cell prior is removed before composition."
                .to_string(),
        );
    }
    if hydro_count > 0 {
        conditions.push(
            "Hydroacoustic features are displayed as conditional travel-time geometry, not independent detections."
                .to_string(),
        );
    }
    if antenna_gain_applied {
        conditions.push(
            "Directional received power is applied conditionally at five regular R1200 epochs; the gain surface and no-precompensation endpoint are uncommissioned."
                .to_string(),
        );
    } else if antenna_geometry_present {
        conditions.push(
            "Antenna output is geometry-only because the available gain pattern is synthetic."
                .to_string(),
        );
    }
    ReportDocument {
        title: format!("MH370 posterior - {}", family.name),
        subtitle: format!(
            "{} | {} independent seeds | canonical Rust estimator",
            suite_name,
            runs.len()
        ),
        summary: vec![
            ("Pooled particles".to_string(), particles.to_string()),
            ("Independent seeds".to_string(), runs.len().to_string()),
            (
                "Posterior mean".to_string(),
                format!(
                    "{}, {}",
                    format_latitude(mean.latitude.0, 3),
                    format_longitude(mean.longitude.0, 3)
                ),
            ),
            (
                "90% latitude".to_string(),
                format!(
                    "{} to {}",
                    format_latitude(latitude_90[0], 2),
                    format_latitude(latitude_90[1], 2)
                ),
            ),
            (
                "90% longitude".to_string(),
                format!(
                    "{} to {}",
                    format_longitude(longitude_90[0], 2),
                    format_longitude(longitude_90[1], 2)
                ),
            ),
            (
                "Numerical convergence".to_string(),
                match converged {
                    Some(true) => "passed".to_string(),
                    Some(false) => "failed".to_string(),
                    None => "unassessed".to_string(),
                },
            ),
            (
                "Seed mean separation".to_string(),
                maximum_seed_mean_separation_nm
                    .map(|value| format!("{value:.1} NM"))
                    .unwrap_or_else(|| "unassessed".to_string()),
            ),
            (
                "Log-evidence range".to_string(),
                if maximum_seed_mean_separation_nm.is_some() {
                    format!("{log_evidence_range:.3} nats")
                } else {
                    "unassessed".to_string()
                },
            ),
            (
                "Minimum particle ESS".to_string(),
                format!("{minimum_ess:.0}"),
            ),
            (
                "Minimum tempered ESS".to_string(),
                format!("{minimum_tempered_ess:.0}"),
            ),
            (
                "Minimum mutation acceptance".to_string(),
                minimum_mutation_acceptance
                    .map(|value| format!("{:.1}%", 100.0 * value))
                    .unwrap_or_else(|| "unavailable".to_string()),
            ),
            (
                "Observation model".to_string(),
                if family.use_antenna_gain {
                    "BTO + conditional BFO + conditional Rx power".to_string()
                } else if family.use_bfo {
                    "BTO + conditional BFO".to_string()
                } else {
                    "BTO only".to_string()
                },
            ),
        ],
        points,
        diagnostics: aggregate_diagnostics(runs),
        evidence_conditions: conditions,
        limitations: runs[0].summary.limitations.clone(),
        map_context,
    }
}

pub(crate) fn estimate(
    config_path: &Path,
    output: &Path,
    requested_threads: Option<usize>,
) -> Result<()> {
    let (suite, config_bytes) = load_config(config_path)?;
    let config_digest = sha256_bytes(&config_bytes);
    let executable_digest = executable_sha256()?;
    let threads = requested_threads.unwrap_or_else(|| {
        std::thread::available_parallelism()
            .map(usize::from)
            .unwrap_or(1)
    });
    if threads == 0 {
        bail!("thread count must be positive");
    }
    prepare_output(output)?;

    let observation_path = resolve(config_path, &suite.inputs.observations);
    let ephemeris_path = resolve(config_path, &suite.inputs.satellite_ephemeris);
    let observation_bytes = fs::read(&observation_path)
        .with_context(|| format!("cannot read {}", observation_path.display()))?;
    let ephemeris_bytes = fs::read(&ephemeris_path)
        .with_context(|| format!("cannot read {}", ephemeris_path.display()))?;
    let observation_text =
        std::str::from_utf8(&observation_bytes).context("observation CSV is not UTF-8")?;
    let ephemeris_text =
        std::str::from_utf8(&ephemeris_bytes).context("ephemeris CSV is not UTF-8")?;
    let antenna_inputs = if let Some(configuration) = &suite.evidence.antenna_gain {
        let package_path = resolve(config_path, &configuration.observations);
        let surface_path = resolve(config_path, &configuration.surface);
        let package_bytes = fs::read(&package_path)
            .with_context(|| format!("cannot read {}", package_path.display()))?;
        let surface_bytes = fs::read(&surface_path)
            .with_context(|| format!("cannot read {}", surface_path.display()))?;
        Some((package_path, package_bytes, surface_path, surface_bytes))
    } else {
        None
    };

    let environment_inputs = if let Some(configuration) = &suite.environment {
        let era5_path = resolve(config_path, &configuration.era5);
        let igrf_path = resolve(config_path, &configuration.igrf);
        let era5_bytes =
            fs::read(&era5_path).with_context(|| format!("cannot read {}", era5_path.display()))?;
        let igrf_bytes =
            fs::read(&igrf_path).with_context(|| format!("cannot read {}", igrf_path.display()))?;
        let weather = Era5Grid::parse(&era5_bytes)?;
        let magnetic = IgrfGrid::parse(&igrf_bytes)?;
        Some((
            era5_path, era5_bytes, igrf_path, igrf_bytes, weather, magnetic,
        ))
    } else {
        None
    };

    let mut handoff_input_sha256 = BTreeMap::from([
        (
            "satcom_observations".to_string(),
            sha256_bytes(&observation_bytes),
        ),
        (
            "satellite_ephemeris".to_string(),
            sha256_bytes(&ephemeris_bytes),
        ),
    ]);
    if let Some((_, package_bytes, _, surface_bytes)) = &antenna_inputs {
        handoff_input_sha256.insert(
            "antenna_observations".to_string(),
            sha256_bytes(package_bytes),
        );
        handoff_input_sha256.insert("antenna_surface".to_string(), sha256_bytes(surface_bytes));
    }
    if let Some((_, era5_bytes, _, igrf_bytes, _, _)) = &environment_inputs {
        handoff_input_sha256.insert("era5".to_string(), sha256_bytes(era5_bytes));
        handoff_input_sha256.insert("igrf".to_string(), sha256_bytes(igrf_bytes));
    }

    let pool = ThreadPoolBuilder::new()
        .num_threads(threads)
        .build()
        .context("cannot build deterministic worker pool")?;
    let suite_started = Instant::now();
    let mut family_results = Vec::new();
    let mut family_point_sets = BTreeMap::<String, Vec<ReportPoint>>::new();

    for family in &suite.families {
        let family_started = Instant::now();
        let lateral_guidance = family.lateral_guidance()?;
        let observations = parse_satcom_observations(
            observation_text,
            ephemeris_text,
            suite.inputs.ground_station_position_km,
            family.bfo_sd_override_hz,
        )?;
        if let Some(expected) = &suite.inputs.fit_through_epoch_id {
            let actual = observations
                .last()
                .context("fit-through guard cannot inspect an empty observation set")?;
            if actual.id != *expected {
                bail!(
                    "fit-through guard expected final fitted epoch {expected}, found {}",
                    actual.id
                );
            }
        }
        let navigation_environment = environment_inputs.as_ref().map(|inputs| {
            let configuration = suite
                .environment
                .as_ref()
                .expect("loaded environment has configuration");
            NavigationEnvironment {
                weather: &inputs.4,
                magnetic: &inputs.5,
                time_origin_unix_s: configuration.time_origin_unix_s,
                integration_step_s: configuration.integration_step_s,
                lateral_guidance,
            }
        });
        let antenna_evidence = if let Some(configuration) = &suite.evidence.antenna_gain {
            let (_, package_bytes, _, surface_bytes) = antenna_inputs
                .as_ref()
                .context("configured antenna evidence was not loaded")?;
            Some(
                AccidentAntennaLikelihood::parse(
                    configuration,
                    package_bytes,
                    surface_bytes,
                    &observations,
                )
                .map_err(anyhow::Error::msg)?,
            )
        } else {
            None
        };
        if family.use_antenna_gain && antenna_evidence.is_none() {
            bail!("family enables antenna gain but no antenna evidence is configured");
        }
        let family_output = output.join(&family.name);
        fs::create_dir_all(&family_output)?;
        let mut runs = Vec::new();
        let mut seed_results = Vec::new();
        let mut report_points = Vec::new();

        for seed in &suite.seeds {
            let mut model = suite.model.clone();
            model.tempering.seed = *seed;
            model.use_bfo = family.use_bfo;
            let likelihood = if family.use_antenna_gain {
                antenna_evidence
                    .as_ref()
                    .map(|antenna| antenna as &dyn FinalFlightLikelihood)
            } else {
                None
            };
            let run = pool.install(|| {
                run_final_flight_estimate_with_environment_and_likelihood(
                    &model,
                    &observations,
                    navigation_environment,
                    likelihood,
                )
            })?;
            let seed_name = format!("seed-{seed}");
            let seed_output = family_output.join(&seed_name);
            let handoff = build_posterior_handoff(
                &run,
                family,
                antenna_evidence.as_ref(),
                &executable_digest,
                &config_digest,
                &handoff_input_sha256,
                POSTERIOR_HANDOFF_SCHEMA_VERSION,
            )?;
            write_seed(&seed_output, &run, &handoff.run, suite.schema_version)?;
            write_json(&seed_output.join("posterior-handoff.json"), &handoff)?;
            let seed_weight = 1.0 / suite.seeds.len() as f64;
            report_points.extend(final_posterior_rows(&run).map(|(_, impact, weight)| {
                ReportPoint {
                    latitude_deg: impact.position.latitude.0,
                    longitude_deg: impact.position.longitude.0,
                    weight: weight * seed_weight,
                }
            }));
            seed_results.push(SeedResult {
                seed: *seed,
                summary: run.summary.clone(),
                output: seed_name.clone(),
                posterior_handoff: format!("{seed_name}/posterior-handoff.json"),
            });
            runs.push(run);
        }

        let drift_application = if let Some(application) = suite
            .evidence
            .drift
            .as_ref()
            .and_then(|drift| drift.application.as_ref())
        {
            let path = resolve(config_path, &application.source_area);
            Some(apply_source_area(
                &path,
                &application.family,
                application.isotope_enabled,
                suite
                    .evidence
                    .drift
                    .as_ref()
                    .expect("drift application has drift context")
                    .maximum_cell_distance_nm,
                &mut report_points,
            )?)
        } else {
            None
        };

        let mean = pooled_mean(&report_points);
        let latitude_90 = [
            weighted_quantile(&report_points, true, 0.05),
            weighted_quantile(&report_points, true, 0.95),
        ];
        let longitude_90 = [
            weighted_quantile(&report_points, false, 0.05),
            weighted_quantile(&report_points, false, 0.95),
        ];
        let minimum_ess = runs
            .iter()
            .map(|run| run.summary.posterior_ess)
            .fold(f64::INFINITY, f64::min);
        let minimum_tempered_ess = runs
            .iter()
            .map(|run| run.summary.minimum_tempered_ess)
            .fold(f64::INFINITY, f64::min);
        let minimum_mutation_acceptance = runs
            .iter()
            .filter_map(|run| run.summary.minimum_mutation_acceptance)
            .min_by(f64::total_cmp);
        let maximum_seed_mean_separation_nm = maximum_seed_separation_nm(&runs);
        let log_evidence_range = log_evidence_range(&runs);
        let converged = maximum_seed_mean_separation_nm.map(|separation| {
            separation <= suite.convergence.maximum_seed_mean_separation_nm
                && log_evidence_range <= suite.convergence.maximum_log_evidence_range
                && minimum_mutation_acceptance
                    .map(|rate| rate >= suite.convergence.minimum_mutation_acceptance)
                    .unwrap_or(false)
        });
        let evidence = conditional_evidence(
            &suite.evidence,
            &runs,
            mean,
            antenna_evidence.as_ref(),
            family.use_antenna_gain,
            drift_application.as_ref(),
        )?;
        write_json(&family_output.join("conditional-evidence.json"), &evidence)?;
        family_point_sets.insert(family.name.clone(), report_points.clone());

        let document = report_document(
            &suite.name,
            family,
            &runs,
            report_points,
            mean,
            latitude_90,
            longitude_90,
            minimum_ess,
            minimum_tempered_ess,
            minimum_mutation_acceptance,
            maximum_seed_mean_separation_nm,
            log_evidence_range,
            converged,
            drift_application.is_some(),
            suite.evidence.hydro_events.len(),
            suite.evidence.antenna_pattern.is_some(),
            family.use_antenna_gain,
            suite.map_context.clone(),
        );
        let pdf_path = family_output.join("report.pdf");
        let svg_path = family_output.join("posterior.svg");
        let png_path = family_output.join("posterior.png");
        atomic_write(&pdf_path, &build_pdf(&document)?)?;
        atomic_write(&svg_path, &build_posterior_svg(&document)?)?;
        atomic_write(&png_path, &build_accident_panel_png(&document)?)?;

        family_results.push(FamilyResult {
            name: family.name.clone(),
            use_bfo: family.use_bfo,
            bfo_sd_override_hz: family.bfo_sd_override_hz,
            antenna_gain_applied: family.use_antenna_gain,
            lateral_mode: family.lateral_mode,
            fixed_waypoint: family
                .fixed_waypoint
                .as_ref()
                .map(FixedWaypointConfig::metadata)
                .transpose()?,
            environment_applied: navigation_environment.is_some(),
            weather_applied: runs[0].summary.weather_applied,
            magnetic_declination_applied: runs[0].summary.magnetic_declination_applied,
            pooled_particles: runs.iter().map(|run| run.filter.particles.len()).sum(),
            pooled_mean: mean,
            pooled_latitude_90_deg: latitude_90,
            pooled_longitude_90_deg: longitude_90,
            minimum_posterior_ess: minimum_ess,
            minimum_tempered_ess,
            minimum_mutation_acceptance,
            maximum_seed_mean_separation_nm,
            log_evidence_range,
            converged,
            elapsed_seconds: family_started.elapsed().as_secs_f64(),
            report_pdf: format!("{}/report.pdf", family.name),
            posterior_svg: format!("{}/posterior.svg", family.name),
            posterior_png: format!("{}/posterior.png", family.name),
            conditional_evidence: evidence,
            seeds: seed_results,
        });
    }

    let mut family_comparisons = Vec::with_capacity(suite.paired_comparisons.len());
    for requested in &suite.paired_comparisons {
        let reference = family_results
            .iter()
            .find(|family| family.name == requested.reference_family)
            .expect("paired comparison was validated before inference");
        let comparison = family_results
            .iter()
            .find(|family| family.name == requested.comparison_family)
            .expect("paired comparison was validated before inference");
        let spatial = compare_spatial_posteriors(
            family_point_sets
                .get(&requested.reference_family)
                .expect("reference posterior points were retained"),
            family_point_sets
                .get(&requested.comparison_family)
                .expect("comparison posterior points were retained"),
        )?;
        family_comparisons.push(FamilyComparisonResult {
            reference_family: requested.reference_family.clone(),
            comparison_family: requested.comparison_family.clone(),
            centroid_separation_nm: great_circle_distance_nm(
                reference.pooled_mean,
                comparison.pooled_mean,
            )
            .0,
            single_factor_change: Some(requested.single_factor_change.clone()),
            spatial,
        });
    }

    let comparison_json_path = output.join("family-comparisons.json");
    let comparison_csv_path = output.join("family-comparisons.csv");
    write_json(
        &comparison_json_path,
        &FamilyComparisonArtifact {
            schema_version: 1,
            suite_name: &suite.name,
            interpretation: "Descriptive common-raster comparisons of separately conditioned posterior families; these are not posterior model probabilities or Bayes factors.",
            comparisons: &family_comparisons,
        },
    )?;
    atomic_write(
        &comparison_csv_path,
        &family_comparison_csv(&family_comparisons),
    )?;

    let status = if suite.seeds.len() < 2 {
        "complete_unassessed_smoke"
    } else if family_results
        .iter()
        .all(|family| family.converged == Some(true))
    {
        "complete_converged"
    } else {
        "complete_nonconverged"
    }
    .to_string();
    let suite_result = SuiteResult {
        schema_version: SUITE_SUMMARY_SCHEMA_VERSION,
        config_schema_version: suite.schema_version,
        handoff_schema_version: POSTERIOR_HANDOFF_SCHEMA_VERSION,
        name: suite.name.clone(),
        status,
        threads,
        elapsed_seconds: suite_started.elapsed().as_secs_f64(),
        families: family_results,
        family_comparisons,
    };
    let summary_path = output.join("suite-summary.json");
    write_json(&summary_path, &suite_result)?;

    let mut input_sha256 = BTreeMap::from([
        (
            observation_path.display().to_string(),
            sha256_bytes(&observation_bytes),
        ),
        (
            ephemeris_path.display().to_string(),
            sha256_bytes(&ephemeris_bytes),
        ),
    ]);
    if let Some((package_path, package_bytes, surface_path, surface_bytes)) = &antenna_inputs {
        input_sha256.insert(
            package_path.display().to_string(),
            sha256_bytes(package_bytes),
        );
        input_sha256.insert(
            surface_path.display().to_string(),
            sha256_bytes(surface_bytes),
        );
    }
    if let Some((era5_path, era5_bytes, igrf_path, igrf_bytes, _, _)) = &environment_inputs {
        input_sha256.insert(era5_path.display().to_string(), sha256_bytes(era5_bytes));
        input_sha256.insert(igrf_path.display().to_string(), sha256_bytes(igrf_bytes));
    }
    if let Some(drift) = &suite.evidence.drift {
        if let Some(application) = &drift.application {
            let source_area_path = resolve(config_path, &application.source_area);
            input_sha256.insert(
                source_area_path.display().to_string(),
                sha256_file(&source_area_path)?,
            );
        }
    }
    let mut outputs = BTreeMap::from([(
        "suite-summary.json".to_string(),
        sha256_file(&summary_path)?,
    )]);
    outputs.insert(
        "family-comparisons.json".to_string(),
        sha256_file(&comparison_json_path)?,
    );
    outputs.insert(
        "family-comparisons.csv".to_string(),
        sha256_file(&comparison_csv_path)?,
    );
    for family in &suite_result.families {
        let conditional_evidence = format!("{}/conditional-evidence.json", family.name);
        outputs.insert(
            conditional_evidence.clone(),
            sha256_file(&output.join(&conditional_evidence))?,
        );
        for seed in &family.seeds {
            for artifact in ["summary.json", "checkpoints.json", "posterior.csv"] {
                let relative = format!("{}/{}/{}", family.name, seed.output, artifact);
                outputs.insert(relative.clone(), sha256_file(&output.join(&relative))?);
            }
            let handoff_relative = format!("{}/{}", family.name, seed.posterior_handoff);
            outputs.insert(
                handoff_relative.clone(),
                sha256_file(&output.join(&handoff_relative))?,
            );
        }
        for relative in [
            &family.report_pdf,
            &family.posterior_svg,
            &family.posterior_png,
        ] {
            outputs.insert(relative.clone(), sha256_file(&output.join(relative))?);
        }
    }
    let manifest = SuiteManifest {
        schema_version: RUN_MANIFEST_SCHEMA_VERSION,
        config_schema_version: suite.schema_version,
        handoff_schema_version: POSTERIOR_HANDOFF_SCHEMA_VERSION,
        engine_version: env!("CARGO_PKG_VERSION"),
        executable_sha256: executable_digest,
        command: "estimate",
        config_path: config_path.display().to_string(),
        config_sha256: config_digest,
        input_sha256,
        outputs,
        structural_families: suite
            .families
            .iter()
            .map(|family| {
                let fixed_waypoint = family
                    .fixed_waypoint
                    .as_ref()
                    .map(FixedWaypointConfig::metadata)
                    .transpose()?;
                let fixed_waypoint_identity_sha256 = fixed_waypoint
                    .as_ref()
                    .map(fixed_waypoint_identity)
                    .transpose()?;
                Ok(StructuralFamilyIdentity {
                    name: family.name.clone(),
                    lateral_mode: family.lateral_mode,
                    fixed_waypoint,
                    fixed_waypoint_identity_sha256,
                    era5_temperature_wind_active: suite.environment.is_some(),
                    igrf_declination_active: suite.environment.is_some()
                        && matches!(
                            family.lateral_mode,
                            LateralMode::ConstantMagneticHeading
                                | LateralMode::ConstantMagneticTrack
                        ),
                })
            })
            .collect::<Result<Vec<_>>>()?,
        scientific_scope: vec![
            "Every family is a model-conditional estimate, not an observed crash location."
                .to_string(),
            "Per-seed posterior handoffs represent the estimator checkpoint before any downstream ocean-drift or report-only reweighting."
                .to_string(),
            "Autopilot modes are emitted as explicit model families and are never pooled."
                .to_string(),
            "Fixed-waypoint candidate identities and coordinates were frozen before these production estimator runs, but the candidates were selected post hoc from exploratory 186.2-degree/seventh-arc geometry; they were not drawn from a preregistered or exhaustive waypoint universe, receive no look-elsewhere correction, and are never pooled or assigned posterior model probabilities."
                .to_string(),
            "Structural BFO alternatives are emitted separately and never averaged by default."
                .to_string(),
            "A family-specific ocean-drift source likelihood is applied only when selected explicitly; incompatible drift families are never averaged."
                .to_string(),
        ],
    };
    write_json(&output.join("run-manifest.json"), &manifest)?;

    println!(
        "status={} families={} seeds={} elapsed_s={:.3} threads={} summary={}",
        suite_result.status,
        suite_result.families.len(),
        suite.seeds.len(),
        suite_result.elapsed_seconds,
        threads,
        summary_path.display()
    );
    for family in &suite_result.families {
        let separation = family
            .maximum_seed_mean_separation_nm
            .map_or("unassessed".to_string(), |value| format!("{value:.2}"));
        let converged = family
            .converged
            .map_or("unassessed".to_string(), |value| value.to_string());
        println!(
            "{} mean=({:.4},{:.4}) seed_separation_nm={} log_evidence_range={:.3} converged={}",
            family.name,
            family.pooled_mean.latitude.0,
            family.pooled_mean.longitude.0,
            separation,
            family.log_evidence_range,
            converged
        );
    }
    Ok(())
}

#[cfg(test)]
mod tests {
    use std::collections::BTreeMap;

    use mh370_domain::{LatLon, NauticalMiles};
    use mh370_dynamics::LateralMode;
    use mh370_estimator::{FixedWaypointMetadata, PosteriorRunMetadata};

    use super::{
        format_latitude, format_longitude, lateral_mode_token, validate_seed_artifact_identity,
        POSTERIOR_CSV_SCHEMA_VERSION, RUN_MANIFEST_SCHEMA_VERSION, SEED_SUMMARY_SCHEMA_VERSION,
        SUITE_SUMMARY_SCHEMA_VERSION,
    };

    #[test]
    fn geographic_report_labels_use_cardinal_hemispheres() {
        assert_eq!(format_latitude(-68.4706, 4), "68.4706 deg S");
        assert_eq!(format_latitude(5.5, 1), "5.5 deg N");
        assert_eq!(format_longitude(-68.267, 3), "68.267 deg W");
        assert_eq!(format_longitude(78.84061, 2), "78.84 deg E");
    }

    fn metadata(mode: LateralMode) -> PosteriorRunMetadata {
        PosteriorRunMetadata {
            model_family: "fixture".to_string(),
            seed: 7,
            lateral_mode: Some(mode),
            run_identity_sha256: "a".repeat(64),
            config_sha256: "b".repeat(64),
            input_sha256: BTreeMap::from([("fixture".to_string(), "c".repeat(64))]),
            fixed_waypoint: None,
        }
    }

    fn route() -> FixedWaypointMetadata {
        FixedWaypointMetadata {
            target_name: "Fixture landing area".to_string(),
            position: LatLon::new(-68.0, 78.0).unwrap(),
            arrival_radius: NauticalMiles(1.0),
            coordinate_source_title: "Official register".to_string(),
            coordinate_source_uri: "https://example.invalid/register".to_string(),
            coordinate_frame_assumption: "published coordinates treated as WGS84".to_string(),
            coordinate_source_date: Some("2014".to_string()),
            coordinate_note: "facility reference point".to_string(),
        }
    }

    #[test]
    fn standalone_seed_identity_requires_complete_typed_lnav_route() {
        let scalar = metadata(LateralMode::ConstantTrueTrack);
        validate_seed_artifact_identity(LateralMode::ConstantTrueTrack, &scalar).unwrap();

        let mut missing = metadata(LateralMode::LateralNavigation);
        assert!(validate_seed_artifact_identity(LateralMode::LateralNavigation, &missing).is_err());
        missing.fixed_waypoint = Some(route());
        validate_seed_artifact_identity(LateralMode::LateralNavigation, &missing).unwrap();

        let mut incomplete = missing.clone();
        incomplete
            .fixed_waypoint
            .as_mut()
            .unwrap()
            .coordinate_note
            .clear();
        assert!(
            validate_seed_artifact_identity(LateralMode::LateralNavigation, &incomplete).is_err()
        );

        let mut scalar_with_route = scalar;
        scalar_with_route.fixed_waypoint = Some(route());
        assert!(validate_seed_artifact_identity(
            LateralMode::ConstantTrueTrack,
            &scalar_with_route
        )
        .is_err());
    }

    #[test]
    fn artifact_schemas_and_machine_tokens_are_explicit() {
        assert_eq!(SUITE_SUMMARY_SCHEMA_VERSION, 2);
        assert_eq!(RUN_MANIFEST_SCHEMA_VERSION, 2);
        assert_eq!(SEED_SUMMARY_SCHEMA_VERSION, 2);
        assert_eq!(POSTERIOR_CSV_SCHEMA_VERSION, 2);
        assert_eq!(
            lateral_mode_token(LateralMode::LateralNavigation),
            "lateral_navigation"
        );
        assert_eq!(
            lateral_mode_token(LateralMode::ConstantMagneticTrack),
            "constant_magnetic_track"
        );
    }
}
