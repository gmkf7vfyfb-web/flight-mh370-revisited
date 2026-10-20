//! Thin file/config boundary for broad powered-flight terminal inference.
//!
//! Scientific propagation and likelihood equations remain in their spokes.
//! This module resolves hash-locked inputs, reconstructs the exact powered
//! model that produced a broad 00:11 handoff, and publishes deterministic
//! terminal artifacts.

use std::{
    cell::Cell,
    collections::{BTreeMap, BTreeSet},
    fs,
    path::{Path, PathBuf},
};

use anyhow::{bail, Context, Result};
use mh370_domain::{Feet, Microseconds, Seconds, Vec3};
use mh370_dynamics::{
    EnvironmentError, Era5Grid, IgrfGrid, MagneticAltitudePolicy, ManeuverProcess,
    PoweredFlightEnvironment, PoweredFlightLimits, PoweredIntegration, PoweredLateralMode,
    RadarPrior,
};
use mh370_end_of_flight::{
    AerodynamicModel, ApuStartPolicy, AtmosphereProfile, ControlledToUncontrolledPolicy,
    EngineFuelFlowShares, IntegrationSettings, Kilograms, KilogramsPerCubicMetre, MetresPerSecond,
    PoweredFuelModel, PoweredFuelState, RestartTransientFamily, TransitionAtmosphere,
    TransitionAtmosphereError, TransitionAtmosphereSample,
};
use mh370_estimator::{
    parse_satcom_observations, BroadEvidenceComponentV1, BroadEvidenceDispositionV1,
    BroadFlightConfig, BroadFlightModel, BroadFlightModelOptions, BroadFlightStratum,
    BroadFuelFlowInitializationDesign, BroadFuelUncertainty, BroadPosteriorHandoffV1,
    BroadPoweredFeasibilityConfig, BroadProposalCandidateSchedule,
    BroadStratumFuelUncertaintyOverride, BroadUniformRange,
};
use mh370_particle_filter::StratumId;
use mh370_satcom::{ExactTimeSatcomContact, SatelliteEcefPropagationLimit, SatelliteEcefState};
use serde::{Deserialize, Serialize};

use crate::{
    atomic_write,
    broad_impact_handoff::{
        BroadImpactHandoffV1, BroadImpactModelHashesV1, BroadImpactParentV1,
        BroadImpactRunProvenanceV1, BroadOutcomeMassV1, BroadR600EvidenceV1,
        BroadR600ParticleEvidenceV1, BroadR600ZeroSupportReasonV1, BroadTerminalEvidenceModelV1,
        BroadTerminalFamilyV1, BroadTerminalModelHashesV1, BROAD_IMPACT_HANDOFF_SCHEMA_ID,
        BROAD_IMPACT_HANDOFF_SCHEMA_VERSION,
    },
    broad_terminal_commands::{
        build_broad_terminal_with_model, reject_pending_renewal_refresh_parent,
        BroadTerminalEnvironment, BroadTerminalPropagationConfigV1, BroadUpstreamEvidenceMappingV1,
    },
    executable_sha256,
    impact_handoff::{
        AbsoluteTimeBasisV1, EvidenceApplicationRoleV1, EvidenceApplicationV1,
        EvidenceDispositionV2, EvidenceEntryV2, EvidenceIdentityV2, EvidenceLedgerV2,
    },
    prepare_output, sha256_bytes,
};

const CONFIG_SCHEMA_VERSION: u32 = 1;
const SOURCE_TIME_ORIGIN_UNIX_S: f64 = 1_394_215_309.0;
const SOURCE_TIME_ORIGIN_UTC: &str = "2014-03-07T18:01:49Z";
const M0011_RELATIVE_S: f64 = 22_150.0;
const R600_SOURCE_RELATIVE_S: f64 = 22_660.0;
const R600_SOURCE_TIME_UNIX_S: f64 = 1_394_237_969.0;
const R600_CONTACT_OFFSET_S: f64 = 0.416;
const R600_CONTACT_TIME_UNIX_S: f64 = 1_394_237_969.416;
const R600_ELAPSED_FROM_M0011_S: f64 = 510.416;
const R600_OBSERVED_BTO_US: f64 = 18_400.0;
const R600_BTO_SD_US: f64 = 63.0;
const MPS_PER_KNOT: f64 = 1_852.0 / 3_600.0;
const TIME_TOLERANCE_S: f64 = 1.0e-6;

const HANDOFF_FILE: &str = "broad-terminal-impact-handoff.json";
const SIDECAR_FILE: &str = "broad-terminal-transition-sidecar.json";
const SUMMARY_FILE: &str = "summary.json";
const MANIFEST_FILE: &str = "run-manifest.json";

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
struct BroadTerminalCliConfig {
    schema_version: u32,
    name: String,
    hypothesis_id: String,
    code_revision: String,
    terminal_seed: u64,
    inputs: BroadTerminalInputs,
    r600: R600InputConfig,
    evidence: TerminalEvidenceConfig,
    terminal_family: TerminalFamilyConfig,
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
struct BroadTerminalInputs {
    parent_handoff: PathBuf,
    powered_flight_config: PathBuf,
    final_satcom_observations: PathBuf,
    final_satellite_ephemeris: PathBuf,
    era5_manifest: PathBuf,
    igrf_manifest: PathBuf,
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
struct R600InputConfig {
    epoch_id: String,
    channel: String,
    satellite_maximum_propagation_s: f64,
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(tag = "branch", rename_all = "snake_case")]
enum TerminalEvidenceConfig {
    R600BtoOnly,
    JointR600BtoAndLogonTiming {
        erlang_shape: u32,
        erlang_scale_s: f64,
    },
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
struct TerminalFamilyConfig {
    id: String,
    model_family: String,
    continuation_draws_per_parent: u32,
    final_powered_bound: Seconds,
    apu_accessible_reserved_fuel: Kilograms,
    ocxo_restart_count: u32,
    restart_transient: RestartTransientFamily,
    mirrored_policies: [ControlledToUncontrolledPolicy; 2],
    aerodynamics: AerodynamicModel,
    fallback_atmosphere: AtmosphereProfile,
    apu_start_policy: ApuStartPolicy,
    integration: IntegrationSettings,
    environment: TerminalEra5Config,
}

#[derive(Debug, Clone, Copy, PartialEq, Serialize, Deserialize)]
struct TerminalEra5Config {
    minimum_pressure_altitude_ft: f64,
    maximum_pressure_altitude_ft: f64,
    below_minimum_policy: PressureAltitudeBoundaryPolicy,
    above_maximum_policy: PressureAltitudeBoundaryPolicy,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
enum PressureAltitudeBoundaryPolicy {
    ClampToGrid,
    Reject,
}

/// The subset of the broad-flight runner configuration required to replay a
/// continuation. The entire source file is hash-matched to the parent before
/// these fields are used.
#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
struct SourceBroadSuite {
    inputs: SourceBroadInputs,
    environment: SourceBroadEnvironment,
    filter: SourceBroadFilter,
    model: SourceBroadModel,
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
struct SourceBroadInputs {
    observations: PathBuf,
    satellite_ephemeris: PathBuf,
    era5: PathBuf,
    igrf: PathBuf,
    ground_station_position_km: Vec3,
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
struct SourceBroadEnvironment {
    time_origin_utc: String,
    time_origin_unix_s: f64,
    magnetic_altitude_policy: MagneticAltitudePolicy,
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
struct SourceBroadFilter {
    particles: usize,
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
struct SourceBroadModel {
    radar_prior: RadarPrior,
    initial_vertical_speed_ft_min: BroadUniformRange,
    source_fuel: PoweredFuelState,
    fuel_uncertainty: BroadFuelUncertainty,
    fuel_model: PoweredFuelModel,
    fuel_flow_shares: EngineFuelFlowShares,
    powered_feasibility: BroadPoweredFeasibilityConfig,
    limits: PoweredFlightLimits,
    integration: PoweredIntegration,
    proposal_candidates: usize,
    #[serde(default)]
    proposal_candidate_schedule: BroadProposalCandidateSchedule,
    satcom: mh370_satcom::SatcomModelConfig,
    initial_modes: Vec<SourceInitialMode>,
    maneuver_families: Vec<SourceManeuverFamily>,
    #[serde(default)]
    fuel_flow_initialization_design: BroadFuelFlowInitializationDesign,
    #[serde(default)]
    fuel_flow_support_strata: Vec<SourceFuelSupport>,
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
struct SourceInitialMode {
    name: String,
    mode: PoweredLateralMode,
    scientific_probability: f64,
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
struct SourceManeuverFamily {
    name: String,
    scientific_probability: f64,
    process: ManeuverProcess,
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
struct SourceFuelSupport {
    name: String,
    flow_scale_log_uniform: BroadUniformRange,
}

#[derive(Debug, Deserialize)]
struct Era5ManifestIdentity {
    output_sha256: String,
    pressure_altitudes_ft: Vec<f64>,
    density_derivation_contract: serde_json::Value,
}

#[derive(Debug, Deserialize)]
struct IgrfManifestIdentity {
    output_sha256: String,
}

#[derive(Debug)]
struct DynamicTerminalEnvironment<'a> {
    weather: &'a Era5Grid,
    relative_time_origin_unix_s: f64,
    minimum_pressure_altitude_ft: f64,
    maximum_pressure_altitude_ft: f64,
    below_minimum_policy: PressureAltitudeBoundaryPolicy,
    above_maximum_policy: PressureAltitudeBoundaryPolicy,
    sample_count: Cell<u64>,
    below_minimum_clamp_count: Cell<u64>,
    above_maximum_clamp_count: Cell<u64>,
}

impl DynamicTerminalEnvironment<'_> {
    fn weather(
        &self,
        time: Seconds,
        position: mh370_domain::LatLon,
        pressure_altitude: Feet,
    ) -> std::result::Result<(mh370_dynamics::WeatherSample, f64), TransitionAtmosphereError> {
        let mut altitude_ft = pressure_altitude.0;
        if altitude_ft < self.minimum_pressure_altitude_ft {
            match self.below_minimum_policy {
                PressureAltitudeBoundaryPolicy::ClampToGrid => {
                    altitude_ft = self.minimum_pressure_altitude_ft;
                    self.below_minimum_clamp_count
                        .set(self.below_minimum_clamp_count.get().saturating_add(1));
                }
                PressureAltitudeBoundaryPolicy::Reject => {
                    return Err(TransitionAtmosphereError::OutsideDomain);
                }
            }
        }
        if altitude_ft > self.maximum_pressure_altitude_ft {
            match self.above_maximum_policy {
                PressureAltitudeBoundaryPolicy::ClampToGrid => {
                    altitude_ft = self.maximum_pressure_altitude_ft;
                    self.above_maximum_clamp_count
                        .set(self.above_maximum_clamp_count.get().saturating_add(1));
                }
                PressureAltitudeBoundaryPolicy::Reject => {
                    return Err(TransitionAtmosphereError::OutsideDomain);
                }
            }
        }
        let absolute_time = self.relative_time_origin_unix_s + time.0;
        let sample = self
            .weather
            .sample(absolute_time, altitude_ft, position)
            .map_err(map_environment_error)?;
        self.sample_count
            .set(self.sample_count.get().saturating_add(1));
        Ok((sample, altitude_ft))
    }
}

impl TransitionAtmosphere for DynamicTerminalEnvironment<'_> {
    fn sample(
        &self,
        time: Seconds,
        position: mh370_domain::LatLon,
        pressure_altitude: Feet,
    ) -> std::result::Result<TransitionAtmosphereSample, TransitionAtmosphereError> {
        let (weather, sampled_altitude_ft) = self.weather(time, position, pressure_altitude)?;
        let density = weather.dry_air_density_kg_m3(sampled_altitude_ft);
        if !density.is_finite() || density <= 0.0 {
            return Err(TransitionAtmosphereError::InvalidSample);
        }
        Ok(TransitionAtmosphereSample {
            density: KilogramsPerCubicMetre(density),
            wind_north: MetresPerSecond(weather.wind_north.0 * MPS_PER_KNOT),
            wind_east: MetresPerSecond(weather.wind_east.0 * MPS_PER_KNOT),
        })
    }
}

impl BroadTerminalEnvironment for DynamicTerminalEnvironment<'_> {
    fn speed_of_sound_m_s(
        &self,
        time: Seconds,
        position: mh370_domain::LatLon,
        pressure_altitude: Feet,
    ) -> std::result::Result<f64, TransitionAtmosphereError> {
        Ok(self
            .weather(time, position, pressure_altitude)?
            .0
            .speed_of_sound_knots()
            * MPS_PER_KNOT)
    }
}

fn map_environment_error(error: EnvironmentError) -> TransitionAtmosphereError {
    match error {
        EnvironmentError::OutsideDomain => TransitionAtmosphereError::OutsideDomain,
        EnvironmentError::InvalidFormat | EnvironmentError::InvalidAxis => {
            TransitionAtmosphereError::InvalidSample
        }
    }
}

#[derive(Debug, Clone, Serialize)]
struct BroadTerminalSummaryV1 {
    schema_version: u32,
    status: &'static str,
    name: String,
    hypothesis_id: String,
    parent_run_identity_sha256: String,
    terminal_run_identity_sha256: String,
    terminal_family_id: String,
    evidence_branch: &'static str,
    exact_r600_time_utc_unix_s: f64,
    retained_parent_particles: usize,
    terminal_draws: usize,
    positive_posterior_draws: usize,
    posterior_effective_sample_size: f64,
    r600_scored_draws: usize,
    r600_zero_support: BTreeMap<String, usize>,
    outcome_mass: BroadOutcomeMassV1,
    era5_sample_count: u64,
    era5_below_minimum_clamp_count: u64,
    era5_above_maximum_clamp_count: u64,
    limitations: Vec<String>,
}

#[derive(Debug, Clone, Serialize)]
struct BroadTerminalManifestV1 {
    schema_version: u32,
    engine_version: &'static str,
    command: &'static str,
    status: &'static str,
    hypothesis_id: String,
    config_path: String,
    configured_input_paths: BTreeMap<String, String>,
    config_sha256: String,
    input_sha256: BTreeMap<String, String>,
    model_sha256: BroadImpactModelHashesV1,
    run_identity_sha256: String,
    terminal_seed: u64,
    outputs: BTreeMap<String, String>,
    scientific_scope: Vec<String>,
}

#[derive(Serialize)]
struct DynamicsHashPreimage<'a> {
    domain: &'static str,
    radar_prior: &'a RadarPrior,
    initial_vertical_speed_ft_min: &'a BroadUniformRange,
    limits: &'a PoweredFlightLimits,
    integration: &'a PoweredIntegration,
    strata: &'a [BroadFlightStratum],
    proposal_candidates: usize,
    proposal_candidate_schedule: &'a BroadProposalCandidateSchedule,
}

#[derive(Serialize)]
struct FuelHashPreimage<'a> {
    domain: &'static str,
    source_fuel: &'a PoweredFuelState,
    uncertainty: &'a BroadFuelUncertainty,
    model: &'a PoweredFuelModel,
    shares: &'a EngineFuelFlowShares,
    initialization_design: BroadFuelFlowInitializationDesign,
    stratum_overrides: &'a [BroadStratumFuelUncertaintyOverride],
}

pub(crate) fn infer(config_path: &Path, output: &Path) -> Result<()> {
    let config_bytes = read(config_path, "broad-terminal configuration")?;
    let config_text = std::str::from_utf8(&config_bytes).context("configuration is not UTF-8")?;
    let config: BroadTerminalCliConfig =
        toml::from_str(config_text).context("cannot parse broad-terminal TOML")?;
    validate_config(&config)?;

    let parent_path = resolve(config_path, &config.inputs.parent_handoff);
    let source_config_path = resolve(config_path, &config.inputs.powered_flight_config);
    let final_observation_path = resolve(config_path, &config.inputs.final_satcom_observations);
    let final_ephemeris_path = resolve(config_path, &config.inputs.final_satellite_ephemeris);
    let era5_manifest_path = resolve(config_path, &config.inputs.era5_manifest);
    let igrf_manifest_path = resolve(config_path, &config.inputs.igrf_manifest);

    let parent_bytes = read(&parent_path, "broad 00:11 handoff")?;
    let parent: BroadPosteriorHandoffV1 =
        serde_json::from_slice(&parent_bytes).context("cannot parse broad 00:11 handoff")?;
    parent.validate().context("invalid broad 00:11 handoff")?;
    reject_pending_renewal_refresh_parent(&parent)?;

    let source_config_bytes = read(&source_config_path, "source broad-flight configuration")?;
    if sha256_bytes(&source_config_bytes) != parent.run.config_sha256 {
        bail!("source broad-flight configuration hash differs from the parent handoff");
    }
    let source_config_text = std::str::from_utf8(&source_config_bytes)
        .context("source broad-flight configuration is not UTF-8")?;
    let source: SourceBroadSuite = toml::from_str(source_config_text)
        .context("cannot parse source broad-flight configuration")?;
    validate_source_clock(&source, &parent)?;

    let source_observation_path = resolve(&source_config_path, &source.inputs.observations);
    let source_ephemeris_path = resolve(&source_config_path, &source.inputs.satellite_ephemeris);
    let era5_path = resolve(&source_config_path, &source.inputs.era5);
    let igrf_path = resolve(&source_config_path, &source.inputs.igrf);
    let source_observation_bytes = read(&source_observation_path, "source SATCOM observations")?;
    let source_ephemeris_bytes = read(&source_ephemeris_path, "source satellite ephemeris")?;
    let era5_bytes = read(&era5_path, "ERA5 grid")?;
    let igrf_bytes = read(&igrf_path, "IGRF grid")?;
    verify_parent_input_hash(&parent, "satcom_observations", &source_observation_bytes)?;
    verify_parent_input_hash(&parent, "satellite_ephemeris", &source_ephemeris_bytes)?;
    verify_parent_input_hash(&parent, "era5", &era5_bytes)?;
    verify_parent_input_hash(&parent, "igrf", &igrf_bytes)?;

    let era5_manifest_bytes = read(&era5_manifest_path, "ERA5 manifest")?;
    let igrf_manifest_bytes = read(&igrf_manifest_path, "IGRF manifest")?;
    let era5_manifest: Era5ManifestIdentity = serde_json::from_slice(&era5_manifest_bytes)
        .context("ERA5 manifest is not the expected JSON schema")?;
    let igrf_manifest: IgrfManifestIdentity = serde_json::from_slice(&igrf_manifest_bytes)
        .context("IGRF manifest is not the expected JSON schema")?;
    verify_environment_manifests(
        &config.terminal_family.environment,
        &era5_bytes,
        &igrf_bytes,
        &era5_manifest,
        &igrf_manifest,
    )?;

    let weather = Era5Grid::parse(&era5_bytes).context("ERA5 runtime grid is invalid")?;
    let magnetic = IgrfGrid::parse(&igrf_bytes).context("IGRF runtime grid is invalid")?;
    let (era5_minimum, era5_maximum) = weather.pressure_altitude_bounds_ft();
    if era5_minimum.to_bits()
        != config
            .terminal_family
            .environment
            .minimum_pressure_altitude_ft
            .to_bits()
        || era5_maximum.to_bits()
            != config
                .terminal_family
                .environment
                .maximum_pressure_altitude_ft
                .to_bits()
    {
        bail!("encoded ERA5 pressure-altitude bounds differ from the terminal configuration");
    }
    let (powered_config, fuel_overrides) = expand_source_model(&source, &parent)?;
    let powered_environment = PoweredFlightEnvironment {
        weather: &weather,
        magnetic: Some(&magnetic),
        magnetic_altitude_policy: source.environment.magnetic_altitude_policy,
        time_origin_unix_s: source.environment.time_origin_unix_s,
    };
    let powered_model = BroadFlightModel::new_with_options(
        powered_config.clone(),
        powered_environment,
        BroadFlightModelOptions {
            stratum_fuel_uncertainty_overrides: fuel_overrides.clone(),
            fuel_flow_initialization_design: source.model.fuel_flow_initialization_design,
            proposal_candidate_schedule: source.model.proposal_candidate_schedule.clone(),
            satcom_event_mark_guide: None,
        },
    )
    .context("source broad-flight model cannot be reconstructed")?;

    let final_observation_bytes = read(&final_observation_path, "final SATCOM observations")?;
    let final_ephemeris_bytes = read(&final_ephemeris_path, "final satellite ephemeris")?;
    let contact = exact_r600_contact(
        &config.r600,
        &source,
        &final_observation_bytes,
        &final_ephemeris_bytes,
    )?;

    let config_sha256 = sha256_bytes(&config_bytes);
    let parent_sha256 = sha256_bytes(&parent_bytes);
    let terminal_family_config_sha256 = hash_json(&config.terminal_family)?;
    let model_sha256 = BroadImpactModelHashesV1 {
        dynamics_sha256: hash_json(&DynamicsHashPreimage {
            domain: "mh370-broad-powered-dynamics-config-v1",
            radar_prior: &powered_config.radar_prior,
            initial_vertical_speed_ft_min: &powered_config.initial_vertical_speed_ft_min,
            limits: &powered_config.limits,
            integration: &powered_config.integration,
            strata: &powered_config.strata,
            proposal_candidates: powered_config.proposal_candidates,
            proposal_candidate_schedule: &source.model.proposal_candidate_schedule,
        })?,
        fuel_sha256: hash_json(&FuelHashPreimage {
            domain: "mh370-broad-powered-fuel-config-v1",
            source_fuel: &powered_config.source_fuel,
            uncertainty: &powered_config.fuel_uncertainty,
            model: &powered_config.fuel_model,
            shares: &powered_config.fuel_flow_shares,
            initialization_design: source.model.fuel_flow_initialization_design,
            stratum_overrides: &fuel_overrides,
        })?,
        satcom_sha256: hash_json(&powered_config.satcom)?,
        end_of_flight_sha256: terminal_family_config_sha256.clone(),
    };
    let input_sha256 = BTreeMap::from([
        ("parent_handoff".to_string(), parent_sha256.clone()),
        (
            "powered_flight_config".to_string(),
            sha256_bytes(&source_config_bytes),
        ),
        (
            "source_satcom_observations".to_string(),
            sha256_bytes(&source_observation_bytes),
        ),
        (
            "source_satellite_ephemeris".to_string(),
            sha256_bytes(&source_ephemeris_bytes),
        ),
        (
            "final_satcom_observations".to_string(),
            sha256_bytes(&final_observation_bytes),
        ),
        (
            "final_satellite_ephemeris".to_string(),
            sha256_bytes(&final_ephemeris_bytes),
        ),
        ("era5_grid".to_string(), sha256_bytes(&era5_bytes)),
        (
            "era5_manifest".to_string(),
            sha256_bytes(&era5_manifest_bytes),
        ),
        ("igrf_grid".to_string(), sha256_bytes(&igrf_bytes)),
        (
            "igrf_manifest".to_string(),
            sha256_bytes(&igrf_manifest_bytes),
        ),
    ]);
    let executable_sha256 = executable_sha256()?;
    let (template, mappings) = build_template(
        &config,
        &parent,
        parent_sha256,
        config_sha256.clone(),
        executable_sha256.clone(),
        input_sha256.clone(),
        model_sha256.clone(),
        terminal_family_config_sha256,
    )?;
    let dynamic_environment = DynamicTerminalEnvironment {
        weather: &weather,
        relative_time_origin_unix_s: SOURCE_TIME_ORIGIN_UNIX_S,
        minimum_pressure_altitude_ft: config
            .terminal_family
            .environment
            .minimum_pressure_altitude_ft,
        maximum_pressure_altitude_ft: config
            .terminal_family
            .environment
            .maximum_pressure_altitude_ft,
        below_minimum_policy: config.terminal_family.environment.below_minimum_policy,
        above_maximum_policy: config.terminal_family.environment.above_maximum_policy,
        sample_count: Cell::new(0),
        below_minimum_clamp_count: Cell::new(0),
        above_maximum_clamp_count: Cell::new(0),
    };
    let propagation = BroadTerminalPropagationConfigV1 {
        time_origin_unix_s_utc: SOURCE_TIME_ORIGIN_UNIX_S,
        final_powered_bound: config.terminal_family.final_powered_bound,
        continuation_draws_per_parent: config.terminal_family.continuation_draws_per_parent,
        apu_accessible_reserved_fuel: config.terminal_family.apu_accessible_reserved_fuel,
        ocxo_restart_count: config.terminal_family.ocxo_restart_count,
        restart_transient: config.terminal_family.restart_transient,
        mirrored_policies: config.terminal_family.mirrored_policies.clone(),
        aerodynamics: config.terminal_family.aerodynamics,
        fallback_atmosphere: config.terminal_family.fallback_atmosphere.clone(),
        apu_start_policy: config.terminal_family.apu_start_policy,
        integration: config.terminal_family.integration,
        environment_family_id: "era5-pressure-altitude-4d".to_string(),
        environment_input_sha256: BTreeMap::from([
            ("era5_grid".to_string(), sha256_bytes(&era5_bytes)),
            (
                "era5_manifest".to_string(),
                sha256_bytes(&era5_manifest_bytes),
            ),
            ("igrf_grid".to_string(), sha256_bytes(&igrf_bytes)),
            (
                "igrf_manifest".to_string(),
                sha256_bytes(&igrf_manifest_bytes),
            ),
        ]),
        r600_contact: contact,
        satcom: powered_config.satcom,
        upstream_evidence_mappings: mappings,
    };
    let artifacts = build_broad_terminal_with_model(
        &parent,
        template,
        propagation,
        &powered_model,
        &dynamic_environment,
    )?;

    prepare_output(output)?;
    let handoff_bytes = pretty_json_bytes(&artifacts.handoff)?;
    let reconstructed_sidecar_bytes = pretty_json_bytes(&artifacts.sidecar)?;
    if reconstructed_sidecar_bytes != artifacts.sidecar_bytes {
        bail!("terminal sidecar serialization is not byte-stable");
    }
    atomic_write(&output.join(SIDECAR_FILE), &artifacts.sidecar_bytes)?;
    atomic_write(&output.join(HANDOFF_FILE), &handoff_bytes)?;

    let summary = summarize(&config, &parent, &artifacts.handoff, &dynamic_environment);
    let summary_bytes = pretty_json_bytes(&summary)?;
    atomic_write(&output.join(SUMMARY_FILE), &summary_bytes)?;

    let outputs = BTreeMap::from([
        (HANDOFF_FILE.to_string(), sha256_bytes(&handoff_bytes)),
        (
            SIDECAR_FILE.to_string(),
            sha256_bytes(&artifacts.sidecar_bytes),
        ),
        (SUMMARY_FILE.to_string(), sha256_bytes(&summary_bytes)),
    ]);
    let manifest = BroadTerminalManifestV1 {
        schema_version: 1,
        engine_version: env!("CARGO_PKG_VERSION"),
        command: "infer-broad-terminal",
        status: "conditional_broad_terminal_complete",
        hypothesis_id: config.hypothesis_id.clone(),
        config_path: portable_invocation_path(config_path),
        configured_input_paths: configured_input_paths(&config, &source),
        config_sha256,
        input_sha256,
        model_sha256,
        run_identity_sha256: artifacts.handoff.run.run_identity_sha256.clone(),
        terminal_seed: config.terminal_seed,
        outputs,
        scientific_scope: vec![
            "One explicitly named terminal family with an exact port/starboard bank-sign mirror; no terminal-family probabilities or averaging.".to_string(),
            "The central branch consumes corrected R600 BTO only; the optional branch consumes R600 BTO and conditional successful-restart Erlang timing atomically.".to_string(),
            "Every terminal draw is retained, including zero-support, rejected, no-exhaustion, non-impact, and impact outcomes.".to_string(),
            "ERA5 supplies time-varying temperature and horizontal wind; vertical wind is unresolved and zero in the point-mass equations.".to_string(),
        ],
    };
    atomic_write(&output.join(MANIFEST_FILE), &pretty_json_bytes(&manifest)?)?;
    println!(
        "status={} family={} branch={} draws={} positive={} handoff={}",
        summary.status,
        summary.terminal_family_id,
        summary.evidence_branch,
        summary.terminal_draws,
        summary.positive_posterior_draws,
        output.join(HANDOFF_FILE).display()
    );
    Ok(())
}

fn validate_config(config: &BroadTerminalCliConfig) -> Result<()> {
    if config.schema_version != CONFIG_SCHEMA_VERSION
        || config.name.trim().is_empty()
        || config.hypothesis_id.trim().is_empty()
        || config.code_revision.trim().is_empty()
        || config.r600.epoch_id != "m0019a"
        || config.r600.channel != "R600"
        || !config.r600.satellite_maximum_propagation_s.is_finite()
        || config.r600.satellite_maximum_propagation_s < R600_CONTACT_OFFSET_S
        || config.terminal_family.id.trim().is_empty()
        || config.terminal_family.model_family.trim().is_empty()
        || config.terminal_family.continuation_draws_per_parent == 0
        || !config.terminal_family.final_powered_bound.is_finite()
        || config.terminal_family.final_powered_bound.0
            <= R600_SOURCE_RELATIVE_S + R600_CONTACT_OFFSET_S
    {
        bail!("invalid or incomplete broad-terminal configuration");
    }
    let environment = config.terminal_family.environment;
    if !environment.minimum_pressure_altitude_ft.is_finite()
        || !environment.maximum_pressure_altitude_ft.is_finite()
        || environment.minimum_pressure_altitude_ft < 0.0
        || environment.maximum_pressure_altitude_ft <= environment.minimum_pressure_altitude_ft
    {
        bail!("invalid broad-terminal ERA5 pressure-altitude bounds");
    }
    if let TerminalEvidenceConfig::JointR600BtoAndLogonTiming {
        erlang_shape,
        erlang_scale_s,
    } = config.evidence
    {
        mh370_end_of_flight::SuccessfulApuSduErlangLagConfig {
            shape: erlang_shape,
            scale: Seconds(erlang_scale_s),
        }
        .validate()
        .context("invalid conditional R600 timing sensitivity")?;
    }
    Ok(())
}

fn validate_source_clock(
    source: &SourceBroadSuite,
    parent: &BroadPosteriorHandoffV1,
) -> Result<()> {
    if source.environment.time_origin_utc != SOURCE_TIME_ORIGIN_UTC
        || source.environment.time_origin_unix_s.to_bits() != SOURCE_TIME_ORIGIN_UNIX_S.to_bits()
        || parent.run.time_origin_utc != SOURCE_TIME_ORIGIN_UTC
        || (parent.checkpoint.state_time.0 - M0011_RELATIVE_S).abs() > TIME_TOLERANCE_S
        || parent.checkpoint.state_epoch_id != "m0011"
        || source.filter.particles != parent.run.configured_particles
    {
        bail!("source broad-flight clocks or configured population differ from the parent handoff");
    }
    Ok(())
}

fn verify_parent_input_hash(
    parent: &BroadPosteriorHandoffV1,
    key: &str,
    bytes: &[u8],
) -> Result<()> {
    let expected = parent
        .run
        .input_sha256
        .get(key)
        .with_context(|| format!("parent handoff lacks required {key} input identity"))?;
    if expected != &sha256_bytes(bytes) {
        bail!("{key} hash differs from the parent handoff");
    }
    Ok(())
}

fn verify_environment_manifests(
    configured: &TerminalEra5Config,
    era5_bytes: &[u8],
    igrf_bytes: &[u8],
    era5: &Era5ManifestIdentity,
    igrf: &IgrfManifestIdentity,
) -> Result<()> {
    if era5.output_sha256 != sha256_bytes(era5_bytes)
        || igrf.output_sha256 != sha256_bytes(igrf_bytes)
        || era5.density_derivation_contract.is_null()
        || era5.pressure_altitudes_ft.first().copied()
            != Some(configured.minimum_pressure_altitude_ft)
        || era5.pressure_altitudes_ft.last().copied()
            != Some(configured.maximum_pressure_altitude_ft)
    {
        bail!("environment grid identity or pressure-altitude contract differs from its manifest");
    }
    Ok(())
}

#[derive(Clone)]
struct ValidatedFuelSupport {
    name: String,
    range: BroadUniformRange,
    probability: f64,
}

fn expand_source_model(
    source: &SourceBroadSuite,
    parent: &BroadPosteriorHandoffV1,
) -> Result<(BroadFlightConfig, Vec<BroadStratumFuelUncertaintyOverride>)> {
    validate_named_probabilities(
        source
            .model
            .initial_modes
            .iter()
            .map(|entry| (entry.name.as_str(), entry.scientific_probability)),
    )?;
    validate_named_probabilities(
        source
            .model
            .maneuver_families
            .iter()
            .map(|entry| (entry.name.as_str(), entry.scientific_probability)),
    )?;
    let latin_hypercube = source.model.fuel_flow_initialization_design
        == BroadFuelFlowInitializationDesign::LogSpaceLatinHypercube;
    if latin_hypercube && !source.model.fuel_flow_support_strata.is_empty() {
        bail!("Latin-hypercube fuel initialization cannot have support strata");
    }
    let fuel_support = validated_fuel_support(&source.model, latin_hypercube)?;
    let count = source
        .model
        .maneuver_families
        .len()
        .checked_mul(fuel_support.len())
        .and_then(|value| value.checked_mul(source.model.initial_modes.len()))
        .context("source broad stratum count overflowed")?;
    if count == 0 || count > u32::MAX as usize || source.filter.particles < count {
        bail!("source broad-flight stratum allocation is invalid");
    }
    let quotient = source.filter.particles / count;
    let remainder = source.filter.particles % count;
    let mut strata = Vec::with_capacity(count);
    let mut overrides = Vec::new();
    let mut index = 0usize;
    for maneuver in &source.model.maneuver_families {
        for fuel in &fuel_support {
            for mode in &source.model.initial_modes {
                let id = StratumId(u32::try_from(index).context("source stratum id overflowed")?);
                let name = if latin_hypercube {
                    format!("{}--{}", maneuver.name, mode.name)
                } else {
                    format!("{}--{}--{}", maneuver.name, fuel.name, mode.name)
                };
                let probability = maneuver.scientific_probability
                    * mode.scientific_probability
                    * if latin_hypercube {
                        1.0
                    } else {
                        fuel.probability
                    };
                let metadata = parent
                    .run
                    .strata
                    .get(index)
                    .context("parent handoff has fewer strata than its source model")?;
                if metadata.id != id
                    || metadata.name != name
                    || metadata.process_family != name
                    || metadata.allocated_particles != quotient + usize::from(index < remainder)
                    || (metadata.scientific_log_prior_probability - probability.ln()).abs()
                        > 1.0e-12
                {
                    bail!("source model expansion differs from parent stratum {index}");
                }
                strata.push(BroadFlightStratum {
                    id,
                    name,
                    initial_lateral_mode: mode.mode,
                    maneuver_process: maneuver.process,
                });
                if !latin_hypercube {
                    overrides.push(BroadStratumFuelUncertaintyOverride {
                        stratum: id,
                        fuel_uncertainty: BroadFuelUncertainty {
                            total_quantity_offset_kg: source
                                .model
                                .fuel_uncertainty
                                .total_quantity_offset_kg,
                            flow_scale_log_uniform: fuel.range,
                        },
                    });
                }
                index += 1;
            }
        }
    }
    if index != parent.run.strata.len() {
        bail!("parent handoff has more strata than its source model");
    }
    let config = BroadFlightConfig {
        radar_prior: source.model.radar_prior,
        initial_vertical_speed_ft_min: source.model.initial_vertical_speed_ft_min,
        source_fuel: source.model.source_fuel,
        fuel_uncertainty: source.model.fuel_uncertainty,
        fuel_model: source.model.fuel_model,
        fuel_flow_shares: source.model.fuel_flow_shares,
        powered_feasibility: source.model.powered_feasibility,
        limits: source.model.limits,
        integration: source.model.integration,
        proposal_candidates: source.model.proposal_candidates,
        satcom: source.model.satcom,
        strata,
    };
    config
        .validate()
        .context("invalid source broad-flight model")?;
    Ok((config, overrides))
}

fn validate_named_probabilities<'a>(values: impl Iterator<Item = (&'a str, f64)>) -> Result<()> {
    let values = values.collect::<Vec<_>>();
    let mut names = BTreeSet::new();
    let sum = values.iter().map(|(_, value)| value).sum::<f64>();
    if values.is_empty()
        || (sum - 1.0).abs() > 1.0e-10
        || values.iter().any(|(name, value)| {
            name.trim().is_empty() || !names.insert(*name) || !value.is_finite() || *value <= 0.0
        })
    {
        bail!("source broad model probabilities must be unique, positive, and normalized");
    }
    Ok(())
}

fn validated_fuel_support(
    model: &SourceBroadModel,
    latin_hypercube: bool,
) -> Result<Vec<ValidatedFuelSupport>> {
    let global = model.fuel_uncertainty.flow_scale_log_uniform;
    if !global.validate() || global.minimum <= 0.0 {
        bail!("source fuel-flow support is invalid");
    }
    if latin_hypercube {
        return Ok(vec![ValidatedFuelSupport {
            name: String::new(),
            range: global,
            probability: 1.0,
        }]);
    }
    if model.fuel_flow_support_strata.is_empty() {
        return Ok(vec![ValidatedFuelSupport {
            name: "full-fuel-flow-support".to_string(),
            range: global,
            probability: 1.0,
        }]);
    }
    if global.minimum == global.maximum {
        bail!("fixed source fuel-flow support cannot be partitioned");
    }
    let mut configured = model.fuel_flow_support_strata.clone();
    configured.sort_by(|left, right| {
        left.flow_scale_log_uniform
            .minimum
            .total_cmp(&right.flow_scale_log_uniform.minimum)
    });
    let mut names = BTreeSet::new();
    let tolerance = 1.0e-12;
    if configured.iter().any(|entry| {
        entry.name.trim().is_empty()
            || !names.insert(entry.name.as_str())
            || !entry.flow_scale_log_uniform.validate()
            || entry.flow_scale_log_uniform.minimum <= 0.0
            || entry.flow_scale_log_uniform.maximum <= entry.flow_scale_log_uniform.minimum
    }) || (configured[0].flow_scale_log_uniform.minimum - global.minimum).abs() > tolerance
        || (configured
            .last()
            .expect("non-empty")
            .flow_scale_log_uniform
            .maximum
            - global.maximum)
            .abs()
            > tolerance
        || configured.windows(2).any(|pair| {
            (pair[0].flow_scale_log_uniform.maximum - pair[1].flow_scale_log_uniform.minimum).abs()
                > tolerance
        })
    {
        bail!("source fuel-flow strata do not exactly partition the declared support");
    }
    let total_log_width = (global.maximum / global.minimum).ln();
    Ok(configured
        .into_iter()
        .map(|entry| ValidatedFuelSupport {
            name: entry.name,
            range: entry.flow_scale_log_uniform,
            probability: (entry.flow_scale_log_uniform.maximum
                / entry.flow_scale_log_uniform.minimum)
                .ln()
                / total_log_width,
        })
        .collect())
}

fn exact_r600_contact(
    config: &R600InputConfig,
    source: &SourceBroadSuite,
    observation_bytes: &[u8],
    ephemeris_bytes: &[u8],
) -> Result<ExactTimeSatcomContact> {
    let observations = std::str::from_utf8(observation_bytes)
        .context("final SATCOM observations are not UTF-8")?;
    let ephemeris = std::str::from_utf8(ephemeris_bytes).context("final ephemeris is not UTF-8")?;
    require_csv_value(
        observations,
        &config.epoch_id,
        "time_utc",
        "2014-03-08T00:19:29.000Z",
    )?;
    require_csv_value_containing(observations, &config.epoch_id, "note", &config.channel)?;
    let parsed = parse_satcom_observations(
        observations,
        ephemeris,
        source.inputs.ground_station_position_km,
        None,
    )?;
    let row = parsed
        .into_iter()
        .find(|row| row.id == config.epoch_id)
        .context("final SATCOM inputs do not contain corrected R600")?;
    let observed_bto = row
        .measurement
        .bto
        .context("corrected R600 row has no BTO")?;
    let bto_sd = row
        .measurement
        .bto_sd
        .context("corrected R600 row has no BTO standard deviation")?;
    if (row.measurement.time.0 - R600_SOURCE_RELATIVE_S).abs() > TIME_TOLERANCE_S
        || observed_bto.0.to_bits() != R600_OBSERVED_BTO_US.to_bits()
        || bto_sd.0.to_bits() != R600_BTO_SD_US.to_bits()
        || row.measurement.bfo.is_some()
        || (SOURCE_TIME_ORIGIN_UNIX_S + row.measurement.time.0 - R600_SOURCE_TIME_UNIX_S).abs()
            > TIME_TOLERANCE_S
    {
        bail!("corrected R600 datum differs from the pinned release observation");
    }
    Ok(ExactTimeSatcomContact {
        satellite_source_epoch: Seconds(R600_SOURCE_TIME_UNIX_S),
        satellite_source_state: SatelliteEcefState {
            position_km: row.measurement.satellite_position_km,
            velocity_km_s: row.measurement.satellite_velocity_km_s,
        },
        satellite_delta: Seconds(R600_CONTACT_OFFSET_S),
        satellite_propagation_limit: SatelliteEcefPropagationLimit {
            maximum_absolute_delta: Seconds(config.satellite_maximum_propagation_s),
        },
        ground_station_position_km: row.measurement.ground_station_position_km,
        observed_bto: Microseconds(R600_OBSERVED_BTO_US),
        bto_standard_deviation: Microseconds(R600_BTO_SD_US),
        bfo: None,
    })
}

fn require_csv_value(csv: &str, epoch: &str, column: &str, expected: &str) -> Result<()> {
    let observed = csv_value(csv, epoch, column)?;
    if observed != expected {
        bail!("CSV {column} for {epoch} differs from {expected}");
    }
    Ok(())
}

fn require_csv_value_containing(
    csv: &str,
    epoch: &str,
    column: &str,
    expected_fragment: &str,
) -> Result<()> {
    let observed = csv_value(csv, epoch, column)?;
    if !observed.contains(expected_fragment) {
        bail!("CSV {column} for {epoch} does not identify {expected_fragment}");
    }
    Ok(())
}

fn csv_value<'a>(csv: &'a str, epoch: &str, column: &str) -> Result<&'a str> {
    let mut lines = csv.lines();
    let header = lines.next().context("CSV is empty")?;
    let columns = header.split(',').collect::<Vec<_>>();
    let epoch_column = columns
        .iter()
        .position(|value| *value == "epoch_id")
        .context("CSV lacks epoch_id")?;
    let value_column = columns
        .iter()
        .position(|value| *value == column)
        .with_context(|| format!("CSV lacks {column}"))?;
    let row = lines
        .map(|line| line.split(',').collect::<Vec<_>>())
        .find(|fields| fields.get(epoch_column).copied() == Some(epoch))
        .with_context(|| format!("CSV lacks epoch {epoch}"))?;
    if row.len() != columns.len() {
        bail!("CSV row for {epoch} has the wrong number of columns");
    }
    row.get(value_column)
        .copied()
        .with_context(|| format!("CSV row for {epoch} lacks {column}"))
}

#[allow(clippy::too_many_arguments)]
fn build_template(
    config: &BroadTerminalCliConfig,
    parent: &BroadPosteriorHandoffV1,
    parent_sha256: String,
    config_sha256: String,
    executable_sha256: String,
    input_sha256: BTreeMap<String, String>,
    model_sha256: BroadImpactModelHashesV1,
    terminal_family_config_sha256: String,
) -> Result<(BroadImpactHandoffV1, Vec<BroadUpstreamEvidenceMappingV1>)> {
    let mappings = parent
        .evidence
        .entries()
        .iter()
        .filter(|entry| entry.disposition == BroadEvidenceDispositionV1::Consumed)
        .map(|entry| BroadUpstreamEvidenceMappingV1 {
            source: entry.identity.clone(),
            downstream: downstream_parent_identity(&entry.identity),
        })
        .collect::<Vec<_>>();
    if mappings.is_empty() {
        bail!("parent handoff contains no consumed evidence");
    }
    let r600_identity = EvidenceIdentityV2 {
        dataset_id: "inmarsat-log".to_string(),
        observation_id: "m0019-r600".to_string(),
        component_id: "bto".to_string(),
        channel_id: Some("r600".to_string()),
    };
    let timing_identity = EvidenceIdentityV2 {
        dataset_id: "inmarsat-log".to_string(),
        observation_id: "m0019-r600".to_string(),
        component_id: "logon_request_time".to_string(),
        channel_id: Some("r600".to_string()),
    };
    let fuel_window_identity = EvidenceIdentityV2 {
        dataset_id: "derived-event".to_string(),
        observation_id: "m0019".to_string(),
        component_id: "fuel_exhaustion_window".to_string(),
        channel_id: None,
    };
    let occurrence_identity = EvidenceIdentityV2 {
        dataset_id: "inmarsat-log".to_string(),
        observation_id: "m0019-r600".to_string(),
        component_id: "logon_occurrence".to_string(),
        channel_id: Some("r600".to_string()),
    };
    let terminal_evidence_model = match config.evidence {
        TerminalEvidenceConfig::R600BtoOnly => BroadTerminalEvidenceModelV1::R600BtoOnly,
        TerminalEvidenceConfig::JointR600BtoAndLogonTiming {
            erlang_shape,
            erlang_scale_s,
        } => BroadTerminalEvidenceModelV1::JointR600BtoAndLogonTiming {
            logon_request_identity: timing_identity.clone(),
            fuel_exhaustion_window_identity: fuel_window_identity.clone(),
            logon_occurrence_identity: occurrence_identity.clone(),
            erlang_shape,
            erlang_rate_per_s: 1.0 / erlang_scale_s,
        },
    };
    let mut entries = mappings
        .iter()
        .map(|mapping| EvidenceEntryV2 {
            identity: mapping.downstream.clone(),
            dependence_group_id: "upstream-parent".to_string(),
            disposition: EvidenceDispositionV2::Consumed,
            application_id: Some("embedded-upstream".to_string()),
        })
        .collect::<Vec<_>>();
    entries.push(EvidenceEntryV2 {
        identity: r600_identity.clone(),
        dependence_group_id: "final-logon".to_string(),
        disposition: EvidenceDispositionV2::Consumed,
        application_id: Some("terminal-update".to_string()),
    });
    if matches!(
        config.evidence,
        TerminalEvidenceConfig::JointR600BtoAndLogonTiming { .. }
    ) {
        entries.extend([
            EvidenceEntryV2 {
                identity: timing_identity,
                dependence_group_id: "final-logon".to_string(),
                disposition: EvidenceDispositionV2::Consumed,
                application_id: Some("terminal-update".to_string()),
            },
            EvidenceEntryV2 {
                identity: fuel_window_identity,
                dependence_group_id: "final-logon".to_string(),
                disposition: EvidenceDispositionV2::HeldOut,
                application_id: None,
            },
            EvidenceEntryV2 {
                identity: occurrence_identity,
                dependence_group_id: "final-logon".to_string(),
                disposition: EvidenceDispositionV2::HeldOut,
                application_id: None,
            },
        ]);
    }
    let branch_config_sha256 = hash_json(&config.evidence)?;
    let template = BroadImpactHandoffV1 {
        schema_id: BROAD_IMPACT_HANDOFF_SCHEMA_ID.to_string(),
        schema_version: BROAD_IMPACT_HANDOFF_SCHEMA_VERSION,
        time_basis: AbsoluteTimeBasisV1 {
            scale: "utc".to_string(),
            epoch: "1970-01-01T00:00:00Z".to_string(),
            unit: "second".to_string(),
            convention: "posix_seconds_no_leap_representation".to_string(),
        },
        run: BroadImpactRunProvenanceV1 {
            hypothesis_id: config.hypothesis_id.clone(),
            run_identity_sha256: zero_digest(),
            producer_executable_sha256: executable_sha256,
            config_sha256: config_sha256.clone(),
            input_sha256: input_sha256.clone(),
            model_sha256: model_sha256.clone(),
            code_revision: config.code_revision.clone(),
            terminal_seed: config.terminal_seed,
            transition_sidecar_sha256: zero_digest(),
        },
        parent: BroadImpactParentV1 {
            schema_version: parent.schema_version,
            handoff_sha256: parent_sha256,
            run_identity_sha256: parent.run.run_identity_sha256.clone(),
            config_sha256: parent.run.config_sha256.clone(),
            input_sha256: parent.run.input_sha256.clone(),
            evidence_ledger_sha256: zero_digest(),
            consumed_evidence: mappings
                .iter()
                .map(|mapping| mapping.downstream.clone())
                .collect(),
            model_family: parent.run.model_family.clone(),
            seed: parent.run.seed,
            checkpoint_id: parent.checkpoint.checkpoint_id.clone(),
            source_epoch_id: parent.run.source_epoch_id.clone(),
            checkpoint_time_unix_s_utc: SOURCE_TIME_ORIGIN_UNIX_S + M0011_RELATIVE_S,
            conditioning: parent.checkpoint.conditioning.clone(),
            configured_particle_count: parent.run.configured_particles,
            retained_particle_count: parent.particles.len(),
        },
        terminal_family: BroadTerminalFamilyV1 {
            id: config.terminal_family.id.clone(),
            model_family: config.terminal_family.model_family.clone(),
            config_sha256: terminal_family_config_sha256.clone(),
            model_sha256: BroadTerminalModelHashesV1 {
                end_of_flight_sha256: terminal_family_config_sha256,
            },
        },
        r600_evidence: BroadR600EvidenceV1 {
            identity: r600_identity,
            dependence_group_id: "final-logon".to_string(),
            application_id: "terminal-update".to_string(),
            time_utc_unix_s: R600_CONTACT_TIME_UNIX_S,
            elapsed_from_parent_checkpoint_s: R600_ELAPSED_FROM_M0011_S,
            observed_bto_us: R600_OBSERVED_BTO_US,
            standard_deviation_us: R600_BTO_SD_US,
        },
        terminal_evidence_model,
        evidence: EvidenceLedgerV2 {
            entries,
            applications: vec![
                EvidenceApplicationV1 {
                    id: "embedded-upstream".to_string(),
                    role: EvidenceApplicationRoleV1::EmbeddedUpstream,
                    model_family: parent.run.model_family.clone(),
                    config_sha256: parent.run.config_sha256.clone(),
                    input_sha256: parent.run.input_sha256.clone(),
                    log_evidence_increment: None,
                },
                EvidenceApplicationV1 {
                    id: "terminal-update".to_string(),
                    role: EvidenceApplicationRoleV1::WeightUpdate,
                    model_family: match config.evidence {
                        TerminalEvidenceConfig::R600BtoOnly => "normal-r600-bto",
                        TerminalEvidenceConfig::JointR600BtoAndLogonTiming { .. } => {
                            "normal-r600-bto-plus-conditional-successful-restart-erlang"
                        }
                    }
                    .to_string(),
                    config_sha256: branch_config_sha256,
                    input_sha256: BTreeMap::from([
                        (
                            "final_satcom_observations".to_string(),
                            input_sha256["final_satcom_observations"].clone(),
                        ),
                        (
                            "final_satellite_ephemeris".to_string(),
                            input_sha256["final_satellite_ephemeris"].clone(),
                        ),
                    ]),
                    log_evidence_increment: Some(0.0),
                },
            ],
        },
        outcome_mass: BroadOutcomeMassV1::default(),
        particles: Vec::new(),
    };
    Ok((template, mappings))
}

fn downstream_parent_identity(
    identity: &mh370_estimator::BroadEvidenceIdentityV1,
) -> EvidenceIdentityV2 {
    EvidenceIdentityV2 {
        dataset_id: "broad-parent-handoff".to_string(),
        observation_id: identity.epoch_id.clone(),
        component_id: match identity.component {
            BroadEvidenceComponentV1::Bto => "bto",
            BroadEvidenceComponentV1::Bfo => "bfo",
            BroadEvidenceComponentV1::FuelExhaustionWindow => "fuel_exhaustion_window",
            BroadEvidenceComponentV1::LogonRequestTime => "logon_request_time",
            BroadEvidenceComponentV1::LogonOccurrence => "logon_occurrence",
            BroadEvidenceComponentV1::ReceivedPower => "received_power",
        }
        .to_string(),
        channel_id: identity.channel.clone(),
    }
}

fn summarize(
    config: &BroadTerminalCliConfig,
    parent: &BroadPosteriorHandoffV1,
    handoff: &BroadImpactHandoffV1,
    environment: &DynamicTerminalEnvironment<'_>,
) -> BroadTerminalSummaryV1 {
    let positive = handoff
        .particles
        .iter()
        .filter_map(|particle| particle.posterior_normalized_log_weight)
        .collect::<Vec<_>>();
    let posterior_effective_sample_size = if positive.is_empty() {
        0.0
    } else {
        1.0 / positive
            .iter()
            .map(|value| (2.0 * value).exp())
            .sum::<f64>()
    };
    let mut zero_support = BTreeMap::new();
    let mut r600_scored_draws = 0usize;
    for particle in &handoff.particles {
        match particle.r600 {
            BroadR600ParticleEvidenceV1::Scored { .. } => r600_scored_draws += 1,
            BroadR600ParticleEvidenceV1::ZeroSupport { reason } => {
                let key = match reason {
                    BroadR600ZeroSupportReasonV1::DidNotReachEpoch => "did_not_reach_epoch",
                    BroadR600ZeroSupportReasonV1::SatcomUnpowered => "satcom_unpowered",
                    BroadR600ZeroSupportReasonV1::RejectedBeforeEpoch => "rejected_before_epoch",
                };
                *zero_support.entry(key.to_string()).or_default() += 1;
            }
        }
    }
    BroadTerminalSummaryV1 {
        schema_version: 1,
        status: "conditional_broad_terminal_complete",
        name: config.name.clone(),
        hypothesis_id: config.hypothesis_id.clone(),
        parent_run_identity_sha256: parent.run.run_identity_sha256.clone(),
        terminal_run_identity_sha256: handoff.run.run_identity_sha256.clone(),
        terminal_family_id: config.terminal_family.id.clone(),
        evidence_branch: match config.evidence {
            TerminalEvidenceConfig::R600BtoOnly => "r600_bto_only",
            TerminalEvidenceConfig::JointR600BtoAndLogonTiming { .. } => {
                "joint_r600_bto_and_conditional_logon_timing"
            }
        },
        exact_r600_time_utc_unix_s: R600_CONTACT_TIME_UNIX_S,
        retained_parent_particles: parent.particles.len(),
        terminal_draws: handoff.particles.len(),
        positive_posterior_draws: positive.len(),
        posterior_effective_sample_size,
        r600_scored_draws,
        r600_zero_support: zero_support,
        outcome_mass: handoff.outcome_mass,
        era5_sample_count: environment.sample_count.get(),
        era5_below_minimum_clamp_count: environment.below_minimum_clamp_count.get(),
        era5_above_maximum_clamp_count: environment.above_maximum_clamp_count.get(),
        limitations: vec![
            "Conditional public-data B777 proxy; no calibrated terminal family probability is inferred.".to_string(),
            "Port/starboard terminal paths are an exact bank-sign mirror and share each powered continuation draw.".to_string(),
            "Impact attitude and water-contact duration remain unresolved.".to_string(),
            "No final BFO, R1200 BTO, ocean drift, hydroacoustics, antenna gain, or search-coverage likelihood is applied.".to_string(),
        ],
    }
}

fn configured_input_paths(
    config: &BroadTerminalCliConfig,
    source: &SourceBroadSuite,
) -> BTreeMap<String, String> {
    BTreeMap::from([
        (
            "parent_handoff".to_string(),
            portable_configured_path(&config.inputs.parent_handoff),
        ),
        (
            "powered_flight_config".to_string(),
            portable_configured_path(&config.inputs.powered_flight_config),
        ),
        (
            "final_satcom_observations".to_string(),
            portable_configured_path(&config.inputs.final_satcom_observations),
        ),
        (
            "final_satellite_ephemeris".to_string(),
            portable_configured_path(&config.inputs.final_satellite_ephemeris),
        ),
        (
            "era5_manifest".to_string(),
            portable_configured_path(&config.inputs.era5_manifest),
        ),
        (
            "igrf_manifest".to_string(),
            portable_configured_path(&config.inputs.igrf_manifest),
        ),
        (
            "source_satcom_observations".to_string(),
            portable_configured_path(&source.inputs.observations),
        ),
        (
            "source_satellite_ephemeris".to_string(),
            portable_configured_path(&source.inputs.satellite_ephemeris),
        ),
        (
            "era5_grid".to_string(),
            portable_configured_path(&source.inputs.era5),
        ),
        (
            "igrf_grid".to_string(),
            portable_configured_path(&source.inputs.igrf),
        ),
    ])
}

fn portable_invocation_path(path: &Path) -> String {
    if path.is_relative() {
        return portable_path(path);
    }
    std::env::current_dir()
        .ok()
        .and_then(|current| path.strip_prefix(current).ok().map(portable_path))
        .unwrap_or_else(|| {
            path.file_name()
                .map(|name| name.to_string_lossy().into_owned())
                .unwrap_or_else(|| "broad-terminal-config.toml".to_string())
        })
}

fn portable_configured_path(path: &Path) -> String {
    if path.is_relative() {
        portable_path(path)
    } else {
        path.file_name()
            .map(|name| name.to_string_lossy().into_owned())
            .unwrap_or_else(|| "external-input".to_string())
    }
}

fn portable_path(path: &Path) -> String {
    path.to_string_lossy().replace('\\', "/")
}

fn resolve(config_path: &Path, path: &Path) -> PathBuf {
    if path.is_absolute() {
        path.to_path_buf()
    } else {
        config_path
            .parent()
            .unwrap_or_else(|| Path::new("."))
            .join(path)
    }
}

fn read(path: &Path, label: &str) -> Result<Vec<u8>> {
    fs::read(path).with_context(|| format!("cannot read {label}: {}", path.display()))
}

fn hash_json(value: &impl Serialize) -> Result<String> {
    Ok(sha256_bytes(&serde_json::to_vec(value)?))
}

fn pretty_json_bytes(value: &impl Serialize) -> Result<Vec<u8>> {
    let mut bytes = serde_json::to_vec_pretty(value)?;
    bytes.push(b'\n');
    Ok(bytes)
}

fn zero_digest() -> String {
    "0".repeat(64)
}

#[cfg(test)]
mod tests {
    use std::sync::atomic::{AtomicU64, Ordering};

    use mh370_domain::{AircraftState, Degrees, FeetPerMinute, Hertz, Knots, LatLon};
    use mh370_dynamics::{
        PendingRenewal, PoweredEventClocks, PoweredEventCounters, PoweredFlightCommand,
        PoweredFlightState, PoweredLateralModeWeights,
    };
    use mh370_end_of_flight::{
        AtmosphereNode, ConditionalB772AerodynamicFamily, ControlCommand, ControlSchedule,
        ControlSegment, ControlTransitionTrigger, ControlledToUncontrolledScenario,
        KilogramsPerSecond,
    };
    use mh370_estimator::{
        BroadCheckpointMetadataV1, BroadConditioningSemanticsV1, BroadEvidenceEntryV1,
        BroadEvidenceIdentityV1, BroadEvidenceLedgerV1, BroadEvidenceStateEffectV1,
        BroadFlightDiagnostics, BroadFlightParticleStatus, BroadFlightScores,
        BroadFuelDiagnosticStatus, BroadParticleEvidenceScoreV1, BroadPendingRenewalRefreshConfig,
        BroadPosteriorHandoffParticleV1, BroadPosteriorParticleIdentityV1,
        BroadPriorRootIdentityV1, BroadRunMetadataV1, BroadStratumMetadataV1,
        BROAD_FLIGHT_MODEL_FAMILY, BROAD_POSTERIOR_HANDOFF_SCHEMA_VERSION,
    };
    use mh370_satcom::{BfoBiasState, BfoConstants, BtoConstants, SatcomModelConfig};

    use super::*;

    static TEST_DIRECTORY_ID: AtomicU64 = AtomicU64::new(0);

    struct TestDirectory(PathBuf);

    impl TestDirectory {
        fn new() -> Self {
            let id = TEST_DIRECTORY_ID.fetch_add(1, Ordering::Relaxed);
            let path = std::env::temp_dir().join(format!(
                "mh370-broad-terminal-cli-{}-{id}",
                std::process::id()
            ));
            fs::create_dir(&path).unwrap();
            Self(path)
        }
    }

    impl Drop for TestDirectory {
        fn drop(&mut self) {
            let _ = fs::remove_dir_all(&self.0);
        }
    }

    fn write_file(directory: &Path, name: &str, bytes: &[u8]) {
        fs::write(directory.join(name), bytes).unwrap();
    }

    fn source_model() -> SourceBroadModel {
        SourceBroadModel {
            radar_prior: RadarPrior {
                time_s: 0.0,
                latitude_deg: 5.0,
                longitude_deg: 99.0,
                position_sd_nm: 0.5,
                control_mean_deg_true: 180.0,
                control_sd_deg: 1.0,
                mach_min: 0.75,
                mach_max: 0.82,
                altitude_min_ft: 34_000.0,
                altitude_max_ft: 36_000.0,
            },
            initial_vertical_speed_ft_min: BroadUniformRange::fixed(0.0),
            source_fuel: PoweredFuelState {
                time: Seconds(0.0),
                zero_fuel_weight: Kilograms(174_369.0),
                left_usable_feed: Kilograms(18_000.0),
                right_usable_feed: Kilograms(18_000.0),
                reserved_fuel: Kilograms(15.0),
                unusable_fuel: Kilograms(0.0),
                left_exhaustion_time: None,
                right_exhaustion_time: None,
                dual_engine_exhaustion_time: None,
            },
            fuel_uncertainty: BroadFuelUncertainty {
                total_quantity_offset_kg: BroadUniformRange::fixed(0.0),
                flow_scale_log_uniform: BroadUniformRange::fixed(1.0),
            },
            fuel_model: PoweredFuelModel::MartinTrent892Lrc,
            fuel_flow_shares: EngineFuelFlowShares {
                left: 0.5,
                right: 0.5,
            },
            powered_feasibility: BroadPoweredFeasibilityConfig {
                aerodynamic_family: ConditionalB772AerodynamicFamily::OpenapV2_6_0AttachedFlow,
                thrust_multiplier: 1.25,
                static_thrust_cap_per_engine_n: 411_480.0,
                maximum_additional_drag_coefficient: 0.1,
            },
            limits: PoweredFlightLimits {
                minimum_pressure_altitude_ft: 500.0,
                maximum_pressure_altitude_ft: 43_000.0,
                minimum_mach_floor: 0.3,
                mmo: 0.87,
                vmo_kcas: 330.0,
                wing_area_m2: 427.8,
                maximum_lift_coefficient: 1.5,
                stall_speed_margin: 1.2,
                maximum_bank_deg: 30.0,
                maximum_roll_rate_deg_s: 3.0,
                maximum_mach_rate_per_s: 0.0005,
                maximum_climb_rate_ft_min: 4_000.0,
                maximum_descent_rate_ft_min: 4_000.0,
                maximum_vertical_acceleration_ft_min_s: 200.0,
                heading_capture_time_s: 120.0,
                altitude_capture_time_s: 600.0,
            },
            integration: PoweredIntegration {
                steady_step_s: 60.0,
                transition_step_s: 15.0,
                heading_capture_tolerance_deg: 0.25,
                maximum_events_per_transition: 256,
            },
            proposal_candidates: 1,
            proposal_candidate_schedule: BroadProposalCandidateSchedule::Constant,
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
            initial_modes: vec![SourceInitialMode {
                name: "constant-true-track".to_string(),
                mode: PoweredLateralMode::ConstantTrueTrack,
                scientific_probability: 1.0,
            }],
            maneuver_families: vec![SourceManeuverFamily {
                name: "no-marked-jumps".to_string(),
                scientific_probability: 1.0,
                process: ManeuverProcess {
                    lateral_clock: None,
                    speed_clock: None,
                    altitude_clock: None,
                    lateral_mode_weights: PoweredLateralModeWeights {
                        constant_true_heading: 0.0,
                        constant_magnetic_heading: 0.0,
                        constant_true_track: 1.0,
                        constant_magnetic_track: 0.0,
                        great_circle_track_continuation: 0.0,
                    },
                    maximum_course_change_deg: 180.0,
                    target_mach_min: 0.3,
                    target_mach_max: 0.87,
                    target_altitude_min_ft: 500.0,
                    target_altitude_max_ft: 43_000.0,
                    great_circle_leg_length_nm: 600.0,
                },
            }],
            fuel_flow_initialization_design:
                BroadFuelFlowInitializationDesign::IndependentLogUniform,
            fuel_flow_support_strata: Vec::new(),
        }
    }

    fn source_suite() -> SourceBroadSuite {
        SourceBroadSuite {
            inputs: SourceBroadInputs {
                observations: PathBuf::from("source-observations.csv"),
                satellite_ephemeris: PathBuf::from("source-ephemeris.csv"),
                era5: PathBuf::from("era5.bin"),
                igrf: PathBuf::from("igrf.bin"),
                ground_station_position_km: Vec3::new(-2_368.8, 4_881.1, -3_342.0),
            },
            environment: SourceBroadEnvironment {
                time_origin_utc: SOURCE_TIME_ORIGIN_UTC.to_string(),
                time_origin_unix_s: SOURCE_TIME_ORIGIN_UNIX_S,
                magnetic_altitude_policy: MagneticAltitudePolicy::ClampToGridAltitude,
            },
            filter: SourceBroadFilter { particles: 2 },
            model: source_model(),
        }
    }

    fn parent_handoff(
        source_config_sha256: String,
        input_sha256: BTreeMap<String, String>,
    ) -> BroadPosteriorHandoffV1 {
        let model_family = BROAD_FLIGHT_MODEL_FAMILY.to_string();
        let checkpoint_id = "filtering-through-m0011".to_string();
        let evidence_identity = BroadEvidenceIdentityV1 {
            epoch_id: "satcom-through-m0011".to_string(),
            channel: None,
            component: BroadEvidenceComponentV1::Bto,
        };
        let evidence = BroadEvidenceLedgerV1::from_entries(vec![BroadEvidenceEntryV1 {
            identity: evidence_identity.clone(),
            disposition: BroadEvidenceDispositionV1::Consumed,
            state_effect: BroadEvidenceStateEffectV1::None,
        }])
        .unwrap();
        let particles = (0..2)
            .map(|particle| {
                let bias = 150.0 + particle as f64;
                BroadPosteriorHandoffParticleV1 {
                    identity: BroadPosteriorParticleIdentityV1 {
                        model_family: model_family.clone(),
                        seed: 370_019,
                        checkpoint_id: checkpoint_id.clone(),
                        particle,
                    },
                    prior_root: BroadPriorRootIdentityV1 {
                        model_family: model_family.clone(),
                        seed: 370_019,
                        source_epoch_id: "radar-180149".to_string(),
                        stratum: StratumId(0),
                        initial_particle: particle,
                    },
                    parent_particle: None,
                    descendant_count: 1,
                    stratum: StratumId(0),
                    normalized_log_weight: (0.5_f64).ln(),
                    source_log_likelihood: -1.0,
                    cumulative_log_prior_over_proposal: 0.0,
                    powered_flight: PoweredFlightState {
                        aircraft: AircraftState {
                            time: Seconds(M0011_RELATIVE_S),
                            position: LatLon::new(-35.0 - particle as f64 * 0.01, 90.0).unwrap(),
                            altitude: Feet(35_000.0),
                            track_true: Degrees(180.0),
                            ground_speed: Knots(470.0),
                            vertical_speed: FeetPerMinute(0.0),
                            bfo_bias: Hertz(bias),
                        },
                        heading_true: Degrees(180.0),
                        mach: 0.78,
                        bank_angle: Degrees(0.0),
                        command: PoweredFlightCommand {
                            lateral_mode: PoweredLateralMode::ConstantTrueTrack,
                            selected_control: Degrees(180.0),
                            great_circle_destination: None,
                            target_mach: 0.78,
                            target_pressure_altitude: Feet(35_000.0),
                        },
                        event_clocks: PoweredEventClocks {
                            lateral: None,
                            speed: None,
                            altitude: None,
                        },
                        event_counters: PoweredEventCounters::default(),
                    },
                    fuel: PoweredFuelState {
                        time: Seconds(M0011_RELATIVE_S),
                        zero_fuel_weight: Kilograms(174_369.0),
                        left_usable_feed: Kilograms(2.0),
                        right_usable_feed: Kilograms(2.0),
                        reserved_fuel: Kilograms(15.0),
                        unusable_fuel: Kilograms(0.0),
                        left_exhaustion_time: None,
                        right_exhaustion_time: None,
                        dual_engine_exhaustion_time: None,
                    },
                    fuel_flow_scale: 1.0,
                    fuel_quantity_offset_kg: 0.0,
                    bfo_bias: BfoBiasState {
                        mean_hz: bias,
                        variance_hz2: 16.0,
                    },
                    status: BroadFlightParticleStatus::Active,
                    fuel_status: BroadFuelDiagnosticStatus::Valid,
                    scores: BroadFlightScores {
                        cumulative_bto_log_likelihood: -1.0,
                        cumulative_bfo_log_likelihood: 0.0,
                        bto_observations: 1,
                        bfo_observations: 0,
                    },
                    last_fit: None,
                    diagnostics: BroadFlightDiagnostics::default(),
                    evidence_scores: vec![BroadParticleEvidenceScoreV1 {
                        identity: evidence_identity.clone(),
                        log_likelihood: -1.0,
                    }],
                }
            })
            .collect();
        BroadPosteriorHandoffV1 {
            schema_version: BROAD_POSTERIOR_HANDOFF_SCHEMA_VERSION,
            run: BroadRunMetadataV1 {
                model_family,
                seed: 370_019,
                run_identity_sha256: "1".repeat(64),
                config_sha256: source_config_sha256,
                input_sha256,
                time_origin_utc: SOURCE_TIME_ORIGIN_UTC.to_string(),
                source_epoch_id: "radar-180149".to_string(),
                source_time: Seconds(0.0),
                source_time_utc: SOURCE_TIME_ORIGIN_UTC.to_string(),
                dynamics_model_family: "powered-marked-jump-era5-v1".to_string(),
                fuel_model_family: "martin-trent892-lrc-strict".to_string(),
                pending_renewal_refresh: None,
                powered_performance_model_family: "attached-flow-segment-force-balance-v1"
                    .to_string(),
                powered_aerodynamic_family: "openap-v2.6.0-b772-attached-flow".to_string(),
                powered_thrust_family: "openap-v2.6.0-b772-trent895-cruise-ceiling".to_string(),
                powered_thrust_multiplier: 1.25,
                powered_static_thrust_cap_per_engine_n: 411_480.0,
                powered_maximum_additional_drag_coefficient: 0.1,
                configured_particles: 2,
                strata: vec![BroadStratumMetadataV1 {
                    id: StratumId(0),
                    name: "no-marked-jumps--full-fuel-flow-support--constant-true-track"
                        .to_string(),
                    process_family: "no-marked-jumps--full-fuel-flow-support--constant-true-track"
                        .to_string(),
                    scientific_log_prior_probability: 0.0,
                    allocated_particles: 2,
                }],
            },
            checkpoint: BroadCheckpointMetadataV1 {
                checkpoint_id,
                state_epoch_id: "m0011".to_string(),
                state_time: Seconds(M0011_RELATIVE_S),
                state_time_utc: "2014-03-08T00:10:59Z".to_string(),
                conditioning: BroadConditioningSemanticsV1::Filtering {
                    through_epoch_id: "m0011".to_string(),
                },
            },
            evidence,
            particles,
        }
    }

    fn mirror_policies() -> [ControlledToUncontrolledPolicy; 2] {
        let pre_trigger_controlled = ControlSchedule {
            segments: vec![ControlSegment {
                start_offset: Seconds(0.0),
                command: ControlCommand::Controlled {
                    lift_load_factor: 1.0,
                    bank_angle: Degrees(0.0),
                },
            }],
        };
        std::array::from_fn(|index| ControlledToUncontrolledPolicy {
            scenario: ControlledToUncontrolledScenario {
                label: if index == 0 { "port" } else { "starboard" }.to_string(),
                trigger: ControlTransitionTrigger::DualEngineGeneratorLoss,
            },
            pre_trigger_controlled: pre_trigger_controlled.clone(),
            post_trigger_uncontrolled: ControlSchedule {
                segments: vec![ControlSegment {
                    start_offset: Seconds(0.0),
                    command: ControlCommand::Uncontrolled {
                        lift_coefficient: 0.7,
                        bank_angle: Degrees(if index == 0 { -5.0 } else { 5.0 }),
                    },
                }],
            },
        })
    }

    fn terminal_config() -> BroadTerminalCliConfig {
        BroadTerminalCliConfig {
            schema_version: 1,
            name: "synthetic broad terminal bridge".to_string(),
            hypothesis_id: "synthetic-broad-terminal".to_string(),
            code_revision: "test-revision".to_string(),
            terminal_seed: 370_019,
            inputs: BroadTerminalInputs {
                parent_handoff: PathBuf::from("parent.json"),
                powered_flight_config: PathBuf::from("source.toml"),
                final_satcom_observations: PathBuf::from("final-observations.csv"),
                final_satellite_ephemeris: PathBuf::from("final-ephemeris.csv"),
                era5_manifest: PathBuf::from("era5-manifest.json"),
                igrf_manifest: PathBuf::from("igrf-manifest.json"),
            },
            r600: R600InputConfig {
                epoch_id: "m0019a".to_string(),
                channel: "R600".to_string(),
                satellite_maximum_propagation_s: 0.5,
            },
            evidence: TerminalEvidenceConfig::R600BtoOnly,
            terminal_family: TerminalFamilyConfig {
                id: "symmetric-low-bank-terminal".to_string(),
                model_family: "controlled-to-uncontrolled-point-mass".to_string(),
                continuation_draws_per_parent: 1,
                final_powered_bound: Seconds(R600_SOURCE_RELATIVE_S + 1_200.0),
                apu_accessible_reserved_fuel: Kilograms(15.0),
                ocxo_restart_count: 0,
                restart_transient: RestartTransientFamily::CommonOcxoWarmup,
                mirrored_policies: mirror_policies(),
                aerodynamics: ConditionalB772AerodynamicFamily::OpenapV2_6_0AttachedFlow.model(),
                fallback_atmosphere: AtmosphereProfile {
                    nodes: vec![AtmosphereNode {
                        altitude: Feet(0.0),
                        density: KilogramsPerCubicMetre(1.225),
                        wind_north: MetresPerSecond(0.0),
                        wind_east: MetresPerSecond(0.0),
                    }],
                },
                apu_start_policy: ApuStartPolicy::OnDualEngineGeneratorLoss {
                    start_delay: Seconds(1.0),
                    start_fuel: Kilograms(0.5),
                    generator_delay: Seconds(2.0),
                    running_fuel_flow: KilogramsPerSecond(0.01),
                },
                integration: IntegrationSettings {
                    time_step: Seconds(5.0),
                    maximum_duration: Seconds(1_500.0),
                    sea_surface_altitude: Feet(0.0),
                    maximum_steps: 1_000,
                },
                environment: TerminalEra5Config {
                    minimum_pressure_altitude_ft: 500.0,
                    maximum_pressure_altitude_ft: 43_000.0,
                    below_minimum_policy: PressureAltitudeBoundaryPolicy::ClampToGrid,
                    above_maximum_policy: PressureAltitudeBoundaryPolicy::ClampToGrid,
                },
            },
        }
    }

    fn era5_bytes() -> Vec<u8> {
        let mut bytes = b"MHERA5V1".to_vec();
        for count in [2_u32, 2, 2, 2] {
            bytes.extend(count.to_le_bytes());
        }
        for time in [SOURCE_TIME_ORIGIN_UNIX_S as i64, 1_394_245_309_i64] {
            bytes.extend(time.to_le_bytes());
        }
        for value in [500.0_f32, 43_000.0] {
            bytes.extend(value.to_le_bytes());
        }
        for value in [-90.0_f32, 90.0] {
            bytes.extend(value.to_le_bytes());
        }
        for value in [-180.0_f32, 180.0] {
            bytes.extend(value.to_le_bytes());
        }
        for value in [250.0_f32, 0.0, 0.0] {
            for _ in 0..16 {
                bytes.extend(value.to_le_bytes());
            }
        }
        bytes
    }

    fn igrf_bytes() -> Vec<u8> {
        let mut bytes = b"MHIGRFV1".to_vec();
        for count in [2_u32, 2, 2] {
            bytes.extend(count.to_le_bytes());
        }
        bytes.extend((R600_SOURCE_TIME_UNIX_S as i64).to_le_bytes());
        bytes.extend(2014.18_f64.to_le_bytes());
        for value in [500.0_f32, 43_000.0] {
            bytes.extend(value.to_le_bytes());
        }
        for value in [-90.0_f32, 90.0] {
            bytes.extend(value.to_le_bytes());
        }
        for value in [-180.0_f32, 180.0] {
            bytes.extend(value.to_le_bytes());
        }
        for _ in 0..8 {
            bytes.extend(0.0_f32.to_le_bytes());
        }
        bytes
    }

    fn install_fixture(directory: &Path) -> PathBuf {
        let source_observations = b"source fixture\n";
        let source_ephemeris = b"source fixture\n";
        let era5 = era5_bytes();
        let igrf = igrf_bytes();
        write_file(directory, "source-observations.csv", source_observations);
        write_file(directory, "source-ephemeris.csv", source_ephemeris);
        write_file(directory, "era5.bin", &era5);
        write_file(directory, "igrf.bin", &igrf);
        write_file(
            directory,
            "era5-manifest.json",
            &serde_json::to_vec_pretty(&serde_json::json!({
                "output_sha256": sha256_bytes(&era5),
                "pressure_altitudes_ft": [500.0, 43000.0],
                "density_derivation_contract": {"formula": "synthetic fixture"}
            }))
            .unwrap(),
        );
        write_file(
            directory,
            "igrf-manifest.json",
            &serde_json::to_vec_pretty(&serde_json::json!({
                "output_sha256": sha256_bytes(&igrf)
            }))
            .unwrap(),
        );
        write_file(
            directory,
            "final-observations.csv",
            b"epoch_id,time_utc,seconds_from_t0,bto_us,bto_sd_us,bfo_hz,bfo_sd_hz,satellite_afc_hz,raw_source_rows,note\nm0019a,2014-03-08T00:19:29.000Z,22660.0,18400,63,,,-37.8,7188,R600 corrected; BFO excluded\n",
        );
        write_file(
            directory,
            "final-ephemeris.csv",
            b"epoch_id,time_utc,x_km,y_km,z_km,vx_km_s,vy_km_s,vz_km_s\nm0019a,2014-03-08T00:19:29.000Z,18182.02038,38049.64962,392.417794,0.001584,-0.001634,-0.083208\n",
        );
        let source = source_suite();
        let source_bytes = toml::to_string_pretty(&source).unwrap().into_bytes();
        write_file(directory, "source.toml", &source_bytes);
        let parent = parent_handoff(
            sha256_bytes(&source_bytes),
            BTreeMap::from([
                (
                    "satcom_observations".to_string(),
                    sha256_bytes(source_observations),
                ),
                (
                    "satellite_ephemeris".to_string(),
                    sha256_bytes(source_ephemeris),
                ),
                ("era5".to_string(), sha256_bytes(&era5)),
                ("igrf".to_string(), sha256_bytes(&igrf)),
            ]),
        );
        parent.validate().unwrap();
        write_file(
            directory,
            "parent.json",
            &pretty_json_bytes(&parent).unwrap(),
        );
        let config_path = directory.join("terminal.toml");
        write_file(
            directory,
            "terminal.toml",
            toml::to_string_pretty(&terminal_config())
                .unwrap()
                .as_bytes(),
        );
        config_path
    }

    #[test]
    fn synthetic_cli_is_end_to_end_deterministic_and_keeps_portable_paths() {
        let fixture = TestDirectory::new();
        let config_path = install_fixture(&fixture.0);
        let first = fixture.0.join("first");
        let second = fixture.0.join("second");
        infer(&config_path, &first).unwrap();
        infer(&config_path, &second).unwrap();

        for name in [HANDOFF_FILE, SIDECAR_FILE, SUMMARY_FILE, MANIFEST_FILE] {
            assert_eq!(
                fs::read(first.join(name)).unwrap(),
                fs::read(second.join(name)).unwrap()
            );
        }
        let handoff: BroadImpactHandoffV1 =
            serde_json::from_slice(&fs::read(first.join(HANDOFF_FILE)).unwrap()).unwrap();
        handoff.validate().unwrap();
        assert_eq!(handoff.particles.len(), 4);
        assert_eq!(
            handoff.r600_evidence.time_utc_unix_s,
            R600_CONTACT_TIME_UNIX_S
        );
        assert!(handoff.particles.iter().all(|particle| {
            matches!(particle.r600, BroadR600ParticleEvidenceV1::Scored { .. })
                && particle.posterior_normalized_log_weight.is_some()
        }));
        let manifest_text = fs::read_to_string(first.join(MANIFEST_FILE)).unwrap();
        assert!(!manifest_text.contains(&fixture.0.display().to_string()));
        assert!(manifest_text.contains("terminal.toml"));
    }

    #[test]
    fn fractional_r600_and_source_config_hash_are_strict_guards() {
        let fixture = TestDirectory::new();
        let config_path = install_fixture(&fixture.0);
        let mut observations =
            fs::read_to_string(fixture.0.join("final-observations.csv")).unwrap();
        observations = observations.replace("18400,63", "18401,63");
        fs::write(fixture.0.join("final-observations.csv"), observations).unwrap();
        let error = infer(&config_path, &fixture.0.join("bad-observation")).unwrap_err();
        assert!(error.to_string().contains("pinned release observation"));

        install_fixture(&fixture.0);
        fs::write(fixture.0.join("source.toml"), b"tampered = true\n").unwrap();
        let error = infer(&config_path, &fixture.0.join("bad-source")).unwrap_err();
        assert!(error.to_string().contains("configuration hash differs"));
    }

    #[test]
    fn terminal_cli_rejects_refresh_parent_before_any_continuation_is_propagated() {
        let fixture = TestDirectory::new();
        let config_path = install_fixture(&fixture.0);
        let parent_path = fixture.0.join("parent.json");
        let mut parent: BroadPosteriorHandoffV1 =
            serde_json::from_slice(&fs::read(&parent_path).unwrap()).unwrap();
        parent.run.pending_renewal_refresh = Some(BroadPendingRenewalRefreshConfig {
            lateral: true,
            speed: true,
            altitude: true,
        });
        parent
            .run
            .dynamics_model_family
            .push_str(";target-invariant-auxiliary-clock-gibbs");
        for particle in &mut parent.particles {
            let time = particle.powered_flight.aircraft.time.0;
            let pending = Some(PendingRenewal {
                not_before: Seconds(time),
                next_event: Seconds(time + 60.0),
            });
            particle.powered_flight.event_clocks = PoweredEventClocks {
                lateral: pending,
                speed: pending,
                altitude: pending,
            };
        }
        parent.validate().unwrap();
        write_file(
            &fixture.0,
            "parent.json",
            &pretty_json_bytes(&parent).unwrap(),
        );

        let error = infer(&config_path, &fixture.0.join("must-not-run")).unwrap_err();
        assert!(error.to_string().contains(
            "cannot consume a pending-renewal-refresh parent until every independent continuation draw refreshes"
        ));
        assert!(!fixture.0.join("must-not-run").exists());
    }

    #[test]
    fn checked_accident_inputs_resolve_the_fractional_r600_contact() {
        let workspace = Path::new(env!("CARGO_MANIFEST_DIR")).join("../..");
        let source_text =
            fs::read_to_string(workspace.join("configs/mh370-broad-powered-flight-pilot.toml"))
                .unwrap();
        let source: SourceBroadSuite = toml::from_str(&source_text).unwrap();
        let observations =
            fs::read(workspace.join("inputs/accident/satcom-observations.csv")).unwrap();
        let ephemeris =
            fs::read(workspace.join("inputs/accident/satellite-ephemeris.csv")).unwrap();
        let contact = exact_r600_contact(
            &R600InputConfig {
                epoch_id: "m0019a".to_string(),
                channel: "R600".to_string(),
                satellite_maximum_propagation_s: 0.5,
            },
            &source,
            &observations,
            &ephemeris,
        )
        .unwrap();
        assert_eq!(contact.satellite_source_epoch.0, R600_SOURCE_TIME_UNIX_S);
        assert_eq!(contact.satellite_delta.0, R600_CONTACT_OFFSET_S);
        assert_eq!(
            contact.satellite_source_epoch.0 + contact.satellite_delta.0,
            R600_CONTACT_TIME_UNIX_S
        );
        assert!(contact.bfo.is_none());
    }
}
