use std::{
    cell::Cell,
    collections::BTreeMap,
    fs,
    path::{Path, PathBuf},
};

use anyhow::{bail, Context, Result};
use mh370_domain::{AircraftState, Degrees, Feet, FeetPerMinute, Knots, Seconds, Vec3};
use mh370_dynamics::{EnvironmentError, Era5Grid};
use mh370_end_of_flight::{
    allocate_powered_fuel, attempt_controlled_to_uncontrolled_with_atmosphere_and_checkpoints,
    kong_arc1_assumed_total_flow_kg_s, project_martin_trent892_lrc_fuel, AerodynamicModel,
    ApuStartPolicy, ApuState, AtmosphereNode, AtmosphereProfile, ConditionalB772AerodynamicFamily,
    ConditionalModelFamily, ControlFamily, ControlTransitionOutcome,
    ControlledToUncontrolledPolicy, ElectricalSystemState, ExactTimeCheckpoint,
    ExactTimeCheckpointSchedule, IntegrationSettings, Kilograms, KilogramsPerCubicMetre,
    MartinFuelProjection, MetresPerSecond, ModelWeight, Newtons, OcxoState, PointMassState,
    PoweredFuelAllocation, PoweredFuelAllocationInput, RequestedCheckpointStatus,
    RestartTransientFamily, TransitionAtmosphere, TransitionAtmosphereError,
    TransitionAtmosphereSample, TransitionInitialCondition, TransitionKernelInput,
    TransitionTermination, WeightedTransition, KONG_FUEL_TABLE_WORKBOOK_SHA256,
    MARTIN_BSM_V7_9_4_WORKBOOK_SHA256,
};
use mh370_estimator::{
    parse_satcom_observations, EvidenceComponent, EvidenceDisposition, EvidenceIdentity,
    EvidenceLedger, FlightObservation, PosteriorHandoff, PosteriorHandoffParticle,
    PosteriorParticleIdentity,
};
use mh370_satcom::{evaluate_observation, SatcomModelConfig};
use serde::{Deserialize, Serialize};

use crate::impact_handoff::{
    AbsoluteTimeBasisV1, ConditionalModelFamilyV1, ControlTransitionTriggerV1, EnuVelocityV1,
    EofControlPolicyFamilyV1, EofScenarioV1, EvidenceApplicationRoleV1, EvidenceApplicationV1,
    EvidenceDispositionV2, EvidenceEntryV2, EvidenceIdentityV2, EvidenceLedgerV2,
    ImpactConditioningV1, ImpactEnergyV1, ImpactKinematicsV1, ImpactParticleIdentityV1,
    ImpactPosteriorHandoffV1, ImpactPosteriorParticleV1, ImpactRunProvenanceV1,
    OutcomeWeightMassV1, ParticleLikelihoodTermV1, RestartTransientFamilyV1, ScenarioCombinationV1,
    SourceRunRefV1, TransitionTerminationV1, IMPACT_POSTERIOR_HANDOFF_SCHEMA_ID,
    IMPACT_POSTERIOR_HANDOFF_SCHEMA_VERSION,
};
use crate::{executable_sha256, prepare_output, sha256_bytes, sha256_file, write_json};

const CONFIG_SCHEMA_VERSION: u32 = 2;
const SIDECAR_SCHEMA_ID: &str = "mh370-eof-transition-sidecar";
const SIDECAR_SCHEMA_VERSION: u32 = 2;
const MANIFEST_SCHEMA_VERSION: u32 = 1;
const REQUIRED_SOURCE_UTC: &str = "2014-03-08T00:10:59Z";
const REQUIRED_R600_UTC: &str = "2014-03-08T00:19:29Z";
const REQUIRED_R1200_UTC: &str = "2014-03-08T00:19:37Z";
const REQUIRED_R600_ELAPSED_S: f64 = 510.0;
const REQUIRED_R1200_ELAPSED_S: f64 = 518.0;
const REQUIRED_R600_BTO_US: f64 = 18_400.0;
const REQUIRED_R600_BTO_SD_US: f64 = 63.0;
const REQUIRED_R1200_BTO_US: f64 = 18_380.0;
const REQUIRED_R1200_BTO_SD_US: f64 = 43.0;
const UTC_TOLERANCE_S: f64 = 1.0e-6;
const MPS_PER_KNOT: f64 = 1_852.0 / 3_600.0;
const MPS_PER_FPM: f64 = 0.304_8 / 60.0;
const R600_APPLICATION_ID: &str = "r600-bto-at-0019";
const UPSTREAM_APPLICATION_ID: &str = "source-posterior-through-0011";
const FINAL_BFO_DIAGNOSTIC_APPLICATION_ID: &str = "raw-final-bfo-diagnostic";
const FINAL_LOGON_DEPENDENCE_GROUP: &str = "mh370-final-logon-0019";

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
struct ImpactInputs {
    observations: PathBuf,
    satellite_ephemeris: PathBuf,
    ground_station_position_km: Vec3,
    source_epoch_id: String,
    r600_epoch_id: String,
    r600_channel: String,
    r1200_epoch_id: String,
    r1200_channel: String,
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
struct ImpactScenarioConfig {
    id: String,
    /// Schema v1 has one separate scenario and therefore requires this to be one.
    model_weight: ModelWeight,
    environment: ImpactEnvironmentConfig,
    fuel_model: ImpactFuelModelConfig,
    electrical: ElectricalSystemState,
    apu: ApuState,
    ocxo: OcxoState,
    restart_transient: RestartTransientFamily,
    control_policy: ControlledToUncontrolledPolicy,
    aerodynamic_family: ConditionalB772AerodynamicFamily,
    apu_start_policy: ApuStartPolicy,
    integration: IntegrationSettings,
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(tag = "model", rename_all = "snake_case")]
enum ImpactEnvironmentConfig {
    StaticAltitudeProfile {
        speed_of_sound_m_s: f64,
        atmosphere: AtmosphereProfile,
    },
    Era5PressureAltitude {
        grid: PathBuf,
        manifest: PathBuf,
        minimum_pressure_altitude_ft: f64,
        maximum_pressure_altitude_ft: f64,
        below_minimum_policy: Era5BelowMinimumPolicy,
        above_maximum_policy: Era5AboveMaximumPolicy,
    },
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
enum Era5BelowMinimumPolicy {
    ClampPressureAltitude,
    Reject,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
enum Era5AboveMaximumPolicy {
    ClampPressureAltitude,
    Reject,
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(tag = "model", rename_all = "snake_case")]
enum ImpactFuelModelConfig {
    FixedAllocation {
        allocation: PoweredFuelAllocationInput,
    },
    MartinTrent892Lrc {
        zero_fuel_weight: Kilograms,
        anchor_total_fuel: Kilograms,
        anchor_utc: String,
        pressure_altitude: Feet,
        apu_reserved_fuel: Kilograms,
        inaccessible_reported_fuel: Kilograms,
        thrust_per_engine: Newtons,
        left_generator_online: bool,
        right_generator_online: bool,
        effective_feed_timing: mh370_end_of_flight::EffectiveFeedTiming,
        martin_workbook_sha256: String,
        kong_sanity_workbook_sha256: String,
    },
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
struct FuelModelResolutionV1 {
    family_id: String,
    allocation_input: PoweredFuelAllocationInput,
    martin_projection: Option<MartinFuelProjection>,
    kong_arc1_assumed_total_flow_kg_s: Option<f64>,
    kong_minus_martin_arc1_fraction: Option<f64>,
    limitations: Vec<String>,
}

#[derive(Debug, Deserialize)]
struct Era5ManifestIdentity {
    output_sha256: String,
    pressure_altitudes_ft: Vec<f64>,
    density_derivation_contract: serde_json::Value,
}

#[derive(Debug)]
struct Era5ImpactAtmosphere {
    grid: Era5Grid,
    relative_time_origin_unix_s_utc: f64,
    minimum_pressure_altitude_ft: f64,
    maximum_pressure_altitude_ft: f64,
    below_minimum_policy: Era5BelowMinimumPolicy,
    above_maximum_policy: Era5AboveMaximumPolicy,
    sample_count: Cell<u64>,
    below_minimum_clamp_count: Cell<u64>,
    above_maximum_clamp_count: Cell<u64>,
}

#[derive(Debug)]
enum ResolvedImpactEnvironment {
    Static {
        speed_of_sound_m_s: f64,
        atmosphere: AtmosphereProfile,
    },
    Era5(Era5ImpactAtmosphere),
}

impl Era5ImpactAtmosphere {
    fn weather(
        &self,
        time: Seconds,
        position: mh370_domain::LatLon,
        pressure_altitude: Feet,
    ) -> Result<(mh370_dynamics::WeatherSample, f64), TransitionAtmosphereError> {
        let mut altitude_ft = pressure_altitude.0;
        if altitude_ft < self.minimum_pressure_altitude_ft {
            match self.below_minimum_policy {
                Era5BelowMinimumPolicy::ClampPressureAltitude => {
                    altitude_ft = self.minimum_pressure_altitude_ft;
                    self.below_minimum_clamp_count
                        .set(self.below_minimum_clamp_count.get().saturating_add(1));
                }
                Era5BelowMinimumPolicy::Reject => {
                    return Err(TransitionAtmosphereError::OutsideDomain);
                }
            }
        }
        if altitude_ft > self.maximum_pressure_altitude_ft {
            match self.above_maximum_policy {
                Era5AboveMaximumPolicy::ClampPressureAltitude => {
                    altitude_ft = self.maximum_pressure_altitude_ft;
                    self.above_maximum_clamp_count
                        .set(self.above_maximum_clamp_count.get().saturating_add(1));
                }
                Era5AboveMaximumPolicy::Reject => {
                    return Err(TransitionAtmosphereError::OutsideDomain);
                }
            }
        }
        let absolute_time = self.relative_time_origin_unix_s_utc + time.0;
        let weather = self
            .grid
            .sample(absolute_time, altitude_ft, position)
            .map_err(|error| match error {
                EnvironmentError::OutsideDomain => TransitionAtmosphereError::OutsideDomain,
                EnvironmentError::InvalidFormat | EnvironmentError::InvalidAxis => {
                    TransitionAtmosphereError::InvalidSample
                }
            })?;
        self.sample_count
            .set(self.sample_count.get().saturating_add(1));
        Ok((weather, altitude_ft))
    }
}

impl TransitionAtmosphere for Era5ImpactAtmosphere {
    fn sample(
        &self,
        time: Seconds,
        position: mh370_domain::LatLon,
        pressure_altitude: Feet,
    ) -> Result<TransitionAtmosphereSample, TransitionAtmosphereError> {
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

impl TransitionAtmosphere for ResolvedImpactEnvironment {
    fn sample(
        &self,
        time: Seconds,
        position: mh370_domain::LatLon,
        pressure_altitude: Feet,
    ) -> Result<TransitionAtmosphereSample, TransitionAtmosphereError> {
        match self {
            Self::Static { atmosphere, .. } => atmosphere.sample(time, position, pressure_altitude),
            Self::Era5(atmosphere) => atmosphere.sample(time, position, pressure_altitude),
        }
    }
}

impl ResolvedImpactEnvironment {
    fn speed_of_sound_m_s(
        &self,
        time: Seconds,
        position: mh370_domain::LatLon,
        pressure_altitude: Feet,
    ) -> Result<f64> {
        match self {
            Self::Static {
                speed_of_sound_m_s, ..
            } => Ok(*speed_of_sound_m_s),
            Self::Era5(atmosphere) => {
                let (weather, _) = atmosphere
                    .weather(time, position, pressure_altitude)
                    .map_err(anyhow::Error::new)?;
                Ok(weather.speed_of_sound_knots() * MPS_PER_KNOT)
            }
        }
    }

    fn fallback_profile(&self) -> AtmosphereProfile {
        match self {
            Self::Static { atmosphere, .. } => atmosphere.clone(),
            Self::Era5(_) => AtmosphereProfile {
                nodes: vec![AtmosphereNode {
                    altitude: Feet(0.0),
                    density: KilogramsPerCubicMetre(1.225),
                    wind_north: MetresPerSecond(0.0),
                    wind_east: MetresPerSecond(0.0),
                }],
            },
        }
    }
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
struct ImpactConfig {
    schema_version: u32,
    hypothesis_id: String,
    source_handoff: PathBuf,
    relative_time_origin_utc: String,
    source_checkpoint_utc: String,
    code_revision: String,
    source_draw_count: Option<usize>,
    eof_seed: u64,
    inputs: ImpactInputs,
    satcom: SatcomModelConfig,
    scenario: ImpactScenarioConfig,
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
struct CheckpointScoreV1 {
    requested_elapsed_s: f64,
    status: CheckpointScoreStatusV1,
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(tag = "kind", rename_all = "snake_case")]
enum CheckpointScoreStatusV1 {
    Reached {
        checkpoint: Box<ExactTimeCheckpoint>,
        observed_bto_us: f64,
        standard_deviation_us: f64,
        predicted_bto_us: f64,
        residual_us: f64,
        log_likelihood: f64,
    },
    Unreached {
        termination: TransitionTermination,
        /// None is an exact zero observation likelihood; JSON cannot encode -infinity.
        log_likelihood: Option<f64>,
    },
    PhysicallyUnavailable {
        checkpoint: Box<ExactTimeCheckpoint>,
        reason: String,
        /// None is exact zero support; this is conditioning on reception, not a likelihood term.
        log_likelihood: Option<f64>,
    },
}

impl CheckpointScoreV1 {
    fn log_likelihood(&self) -> Option<f64> {
        match self.status {
            CheckpointScoreStatusV1::Reached { log_likelihood, .. } => Some(log_likelihood),
            CheckpointScoreStatusV1::Unreached { .. }
            | CheckpointScoreStatusV1::PhysicallyUnavailable { .. } => None,
        }
    }
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
struct TransitionSidecarRecordV1 {
    upstream_identity: PosteriorParticleIdentity,
    eof_draw_id: u32,
    upstream_normalized_log_weight: f64,
    sampling_log_correction: f64,
    // Together with sidecar.scenario and sidecar.fuel_allocation, this reconstructs the full input.
    initial_flight: PointMassState,
    transition: WeightedTransition,
    reached_checkpoints: Vec<ExactTimeCheckpoint>,
    checkpoint_status: RequestedCheckpointStatus,
    control_transition: ControlTransitionOutcome,
    r600_score: CheckpointScoreV1,
    prior_weight: f64,
    r600_conditioned_weight: f64,
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(tag = "method", rename_all = "snake_case")]
enum SourceSamplingV1 {
    AllParticles {
        evaluated_draws: usize,
    },
    SystematicResampling {
        requested_draws: usize,
        evaluated_draws: usize,
        eof_seed: u64,
        unit_interval_offset: f64,
    },
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
struct TerminationMassV1 {
    termination: TransitionTerminationV1,
    prior_normalized_mass: f64,
    r600_conditioned_normalized_mass: f64,
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
struct EnvironmentDiagnosticsV1 {
    family_id: String,
    sample_count: u64,
    below_minimum_pressure_altitude_clamp_count: u64,
    above_maximum_pressure_altitude_clamp_count: u64,
    density_rule: String,
    limitations: Vec<String>,
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
struct TransitionSidecarV1 {
    schema_id: String,
    schema_version: u32,
    hypothesis_id: String,
    producer_executable_sha256: String,
    config_sha256: String,
    source_handoff_sha256: String,
    source_run_identity_sha256: String,
    eof_seed: u64,
    relative_time_origin_unix_s_utc: f64,
    source_checkpoint_time_unix_s_utc: f64,
    r600_checkpoint_time_unix_s_utc: f64,
    r600_elapsed_s: f64,
    source_sampling: SourceSamplingV1,
    scenario: ImpactScenarioConfig,
    fuel_model_resolution: FuelModelResolutionV1,
    fuel_allocation: PoweredFuelAllocation,
    environment_diagnostics: EnvironmentDiagnosticsV1,
    log_evidence_increment: f64,
    outcome_mass: Vec<TerminationMassV1>,
    records: Vec<TransitionSidecarRecordV1>,
    limitations: Vec<String>,
}

#[derive(Debug, Serialize)]
struct ImpactManifestV1 {
    schema_version: u32,
    engine_version: &'static str,
    executable_sha256: String,
    command: &'static str,
    hypothesis_id: String,
    config_path: String,
    config_sha256: String,
    input_sha256: BTreeMap<String, String>,
    run_identity_sha256: String,
    outputs: BTreeMap<String, String>,
    scientific_scope: Vec<String>,
}

#[derive(Debug, Serialize)]
struct ImpactRunIdentityPreimage<'a> {
    domain: &'static str,
    engine_version: &'static str,
    producer_executable_sha256: &'a str,
    config_sha256: &'a str,
    input_sha256: &'a BTreeMap<String, String>,
    source_run_identity_sha256: &'a str,
    eof_scenario_id: &'a str,
    eof_seed: u64,
    transition_sidecar_sha256: &'a str,
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

fn resolve_environment(
    config_path: &Path,
    config: &ImpactEnvironmentConfig,
    relative_time_origin_unix_s_utc: f64,
) -> Result<(ResolvedImpactEnvironment, BTreeMap<String, String>)> {
    match config {
        ImpactEnvironmentConfig::StaticAltitudeProfile {
            speed_of_sound_m_s,
            atmosphere,
        } => {
            if !speed_of_sound_m_s.is_finite() || *speed_of_sound_m_s <= 0.0 {
                bail!("static atmosphere speed of sound must be positive");
            }
            Ok((
                ResolvedImpactEnvironment::Static {
                    speed_of_sound_m_s: *speed_of_sound_m_s,
                    atmosphere: atmosphere.clone(),
                },
                BTreeMap::new(),
            ))
        }
        ImpactEnvironmentConfig::Era5PressureAltitude {
            grid,
            manifest,
            minimum_pressure_altitude_ft,
            maximum_pressure_altitude_ft,
            below_minimum_policy,
            above_maximum_policy,
        } => {
            if !minimum_pressure_altitude_ft.is_finite()
                || !maximum_pressure_altitude_ft.is_finite()
                || *minimum_pressure_altitude_ft < 0.0
                || *minimum_pressure_altitude_ft >= *maximum_pressure_altitude_ft
            {
                bail!("ERA5 pressure-altitude bounds are invalid");
            }
            let grid_path = resolve(config_path, grid);
            let manifest_path = resolve(config_path, manifest);
            let grid_bytes = fs::read(&grid_path)
                .with_context(|| format!("cannot read ERA5 grid {}", grid_path.display()))?;
            let manifest_bytes = fs::read(&manifest_path).with_context(|| {
                format!("cannot read ERA5 manifest {}", manifest_path.display())
            })?;
            let identity: Era5ManifestIdentity = serde_json::from_slice(&manifest_bytes)
                .context("ERA5 manifest is not the expected JSON schema")?;
            let actual_grid_sha256 = sha256_bytes(&grid_bytes);
            if identity.output_sha256 != actual_grid_sha256 {
                bail!("ERA5 binary hash does not match its manifest");
            }
            if identity.density_derivation_contract.is_null() {
                bail!("ERA5 manifest lacks its density derivation contract");
            }
            let grid = Era5Grid::parse(&grid_bytes).context("ERA5 runtime grid is invalid")?;
            let (actual_minimum, actual_maximum) = grid.pressure_altitude_bounds_ft();
            if (actual_minimum - minimum_pressure_altitude_ft).abs() > 1.0e-9
                || (actual_maximum - maximum_pressure_altitude_ft).abs() > 1.0e-9
                || identity.pressure_altitudes_ft.first().copied() != Some(actual_minimum)
                || identity.pressure_altitudes_ft.last().copied() != Some(actual_maximum)
            {
                bail!("ERA5 configured and encoded pressure-altitude bounds disagree");
            }
            Ok((
                ResolvedImpactEnvironment::Era5(Era5ImpactAtmosphere {
                    grid,
                    relative_time_origin_unix_s_utc,
                    minimum_pressure_altitude_ft: *minimum_pressure_altitude_ft,
                    maximum_pressure_altitude_ft: *maximum_pressure_altitude_ft,
                    below_minimum_policy: *below_minimum_policy,
                    above_maximum_policy: *above_maximum_policy,
                    sample_count: Cell::new(0),
                    below_minimum_clamp_count: Cell::new(0),
                    above_maximum_clamp_count: Cell::new(0),
                }),
                BTreeMap::from([
                    ("era5_grid".to_string(), actual_grid_sha256),
                    ("era5_manifest".to_string(), sha256_bytes(&manifest_bytes)),
                ]),
            ))
        }
    }
}

fn resolve_fuel_model(
    config: &ImpactFuelModelConfig,
    source_checkpoint_time_unix_s_utc: f64,
) -> Result<FuelModelResolutionV1> {
    match config {
        ImpactFuelModelConfig::FixedAllocation { allocation } => Ok(FuelModelResolutionV1 {
            family_id: "fixed_allocation_legacy_conditional".to_string(),
            allocation_input: *allocation,
            martin_projection: None,
            kong_arc1_assumed_total_flow_kg_s: None,
            kong_minus_martin_arc1_fraction: None,
            limitations: vec![
                "Caller-supplied fuel total and constant engine flows; no historical fuel-performance propagation.".to_string(),
            ],
        }),
        ImpactFuelModelConfig::MartinTrent892Lrc {
            zero_fuel_weight,
            anchor_total_fuel,
            anchor_utc,
            pressure_altitude,
            apu_reserved_fuel,
            inaccessible_reported_fuel,
            thrust_per_engine,
            left_generator_online,
            right_generator_online,
            effective_feed_timing,
            martin_workbook_sha256,
            kong_sanity_workbook_sha256,
        } => {
            if martin_workbook_sha256 != MARTIN_BSM_V7_9_4_WORKBOOK_SHA256
                || kong_sanity_workbook_sha256 != KONG_FUEL_TABLE_WORKBOOK_SHA256
            {
                bail!("fuel workbook identity does not match the audited release coefficients");
            }
            let anchor_time = parse_utc_posix_seconds(anchor_utc)?;
            let elapsed_seconds = source_checkpoint_time_unix_s_utc - anchor_time;
            if elapsed_seconds < 0.0 {
                bail!("fuel anchor occurs after the 00:11 source checkpoint");
            }
            let projection = project_martin_trent892_lrc_fuel(
                zero_fuel_weight.0,
                anchor_total_fuel.0,
                pressure_altitude.0,
                elapsed_seconds,
            )
            .context("Martin Trent-892 LRC fuel projection failed")?;
            let available_for_engines = projection.end_total_fuel.0
                - apu_reserved_fuel.0
                - inaccessible_reported_fuel.0;
            if available_for_engines <= 0.0 {
                bail!("Martin projection leaves no engine-accessible fuel after exclusions");
            }
            let flow_per_engine = projection.end_total_flow.0 / 2.0;
            let allocation_input = PoweredFuelAllocationInput {
                zero_fuel_weight: *zero_fuel_weight,
                total_onboard_fuel: projection.end_total_fuel,
                apu_reserved_fuel: *apu_reserved_fuel,
                inaccessible_reported_fuel: *inaccessible_reported_fuel,
                left_fuel_flow: mh370_end_of_flight::KilogramsPerSecond(flow_per_engine),
                right_fuel_flow: mh370_end_of_flight::KilogramsPerSecond(flow_per_engine),
                left_thrust: *thrust_per_engine,
                right_thrust: *thrust_per_engine,
                left_generator_online: *left_generator_online,
                right_generator_online: *right_generator_online,
                effective_feed_timing: *effective_feed_timing,
            };
            let arc1_gross_mass = 174_369.0 + 33_524.104_881_96;
            let martin_arc1 = mh370_end_of_flight::martin_trent892_lrc_total_flow(
                35_000.0,
                arc1_gross_mass,
            )?
            .0;
            let kong_arc1 = kong_arc1_assumed_total_flow_kg_s(arc1_gross_mass)?;
            Ok(FuelModelResolutionV1 {
                family_id: "martin_bsm_v7_9_4_trent892_lrc_constant_fl".to_string(),
                allocation_input,
                martin_projection: Some(projection),
                kong_arc1_assumed_total_flow_kg_s: Some(kong_arc1),
                kong_minus_martin_arc1_fraction: Some((kong_arc1 - martin_arc1) / martin_arc1),
                limitations: vec![
                    "Martin BSM v7.9.4 is an independent spreadsheet model, not a Boeing or Rolls-Royce performance deck.".to_string(),
                    "Fuel history is projected at one declared constant pressure altitude; route, Mach, bank, temperature, and engine-efficiency history are not integrated.".to_string(),
                    "The Kong comparison assumes its unlabeled cells are kg/h per engine and is a one-state sanity check only; it never initializes fuel.".to_string(),
                    "Total fuel is deterministically allocated to effective engine feeds under the separately named feed-timing condition; physical tank/crossfeed state is unresolved.".to_string(),
                ],
            })
        }
    }
}

fn valid_identifier(value: &str) -> bool {
    let mut bytes = value.bytes();
    bytes
        .next()
        .is_some_and(|byte| byte.is_ascii_alphanumeric())
        && bytes
            .all(|byte| byte.is_ascii_alphanumeric() || matches!(byte, b'.' | b'_' | b':' | b'-'))
}

/// Parse the restricted UTC representation used by canonical run inputs.
/// Leap seconds are not accepted because the handoff declares POSIX no-leap time.
fn parse_utc_posix_seconds(value: &str) -> Result<f64> {
    let (date, time) = value
        .strip_suffix('Z')
        .and_then(|body| body.split_once('T'))
        .context("UTC timestamp must be YYYY-MM-DDTHH:MM:SS[.fraction]Z")?;
    let mut date_fields = date.split('-');
    let year = date_fields
        .next()
        .context("UTC year is missing")?
        .parse::<i64>()?;
    let month = date_fields
        .next()
        .context("UTC month is missing")?
        .parse::<u32>()?;
    let day = date_fields
        .next()
        .context("UTC day is missing")?
        .parse::<u32>()?;
    if date_fields.next().is_some() {
        bail!("UTC date contains extra fields");
    }
    let mut time_fields = time.split(':');
    let hour = time_fields
        .next()
        .context("UTC hour is missing")?
        .parse::<u32>()?;
    let minute = time_fields
        .next()
        .context("UTC minute is missing")?
        .parse::<u32>()?;
    let second = time_fields
        .next()
        .context("UTC second is missing")?
        .parse::<f64>()?;
    if time_fields.next().is_some()
        || !(1..=12).contains(&month)
        || day == 0
        || day > days_in_month(year, month)
        || hour > 23
        || minute > 59
        || !second.is_finite()
        || !(0.0..60.0).contains(&second)
    {
        bail!("UTC timestamp is outside the POSIX civil-time range");
    }
    Ok(days_from_civil(year, month, day) as f64 * 86_400.0
        + hour as f64 * 3_600.0
        + minute as f64 * 60.0
        + second)
}

fn days_in_month(year: i64, month: u32) -> u32 {
    match month {
        1 | 3 | 5 | 7 | 8 | 10 | 12 => 31,
        4 | 6 | 9 | 11 => 30,
        2 if year.rem_euclid(4) == 0
            && (year.rem_euclid(100) != 0 || year.rem_euclid(400) == 0) =>
        {
            29
        }
        2 => 28,
        _ => 0,
    }
}

// Howard Hinnant's public-domain civil-date transform, shifted to Unix.
fn days_from_civil(year: i64, month: u32, day: u32) -> i64 {
    let year = year - i64::from(month <= 2);
    let era = year.div_euclid(400);
    let year_of_era = year - era * 400;
    let adjusted_month = month as i64 + if month > 2 { -3 } else { 9 };
    let day_of_year = (153 * adjusted_month + 2) / 5 + day as i64 - 1;
    let day_of_era = year_of_era * 365 + year_of_era / 4 - year_of_era / 100 + day_of_year;
    era * 146_097 + day_of_era - 719_468
}

fn close_time(first: f64, second: f64) -> bool {
    (first - second).abs() <= UTC_TOLERANCE_S
}

#[derive(Debug, Clone, PartialEq)]
struct SelectedSourceDraw {
    particle: PosteriorHandoffParticle,
    eof_draw_id: u32,
    sampling_log_correction: f64,
}

fn splitmix64_unit_interval(seed: u64) -> f64 {
    let mut value = seed.wrapping_add(0x9e37_79b9_7f4a_7c15);
    value = (value ^ (value >> 30)).wrapping_mul(0xbf58_476d_1ce4_e5b9);
    value = (value ^ (value >> 27)).wrapping_mul(0x94d0_49bb_1331_11eb);
    value ^= value >> 31;
    ((value >> 11) as f64) * (1.0 / ((1_u64 << 53) as f64))
}

fn select_source_draws(
    handoff: &PosteriorHandoff,
    requested_draws: Option<usize>,
    eof_seed: u64,
) -> Result<(Vec<SelectedSourceDraw>, SourceSamplingV1)> {
    match requested_draws {
        None => {
            let draws = handoff
                .particles
                .iter()
                .cloned()
                .map(|particle| SelectedSourceDraw {
                    particle,
                    eof_draw_id: 0,
                    sampling_log_correction: 0.0,
                })
                .collect::<Vec<_>>();
            let sampling = SourceSamplingV1::AllParticles {
                evaluated_draws: draws.len(),
            };
            Ok((draws, sampling))
        }
        Some(count) => {
            if count == 0 {
                bail!("source_draw_count must be positive when provided");
            }
            if count > u32::MAX as usize {
                bail!("source_draw_count exceeds the schema-v1 draw identity range");
            }
            let weights = handoff
                .particles
                .iter()
                .map(|particle| particle.normalized_log_weight.exp())
                .collect::<Vec<_>>();
            let weight_sum = weights.iter().sum::<f64>();
            if !weight_sum.is_finite() || weight_sum <= 0.0 || (weight_sum - 1.0).abs() > 1.0e-10 {
                bail!("source posterior weights are not normalized for resampling");
            }

            let unit_interval_offset = splitmix64_unit_interval(eof_seed);
            let log_count = (count as f64).ln();
            let mut cumulative = weights[0];
            let mut source_index = 0_usize;
            let mut draws = Vec::with_capacity(count);
            for draw_index in 0..count {
                let target = (unit_interval_offset + draw_index as f64) / count as f64;
                while target > cumulative && source_index + 1 < handoff.particles.len() {
                    source_index += 1;
                    cumulative += weights[source_index];
                }
                let particle = handoff.particles[source_index].clone();
                let sampling_log_correction = -log_count - particle.normalized_log_weight;
                if !sampling_log_correction.is_finite() {
                    bail!("systematic-resampling importance correction is not finite");
                }
                draws.push(SelectedSourceDraw {
                    particle,
                    eof_draw_id: u32::try_from(draw_index)
                        .context("draw identity exceeds schema-v1 range")?,
                    sampling_log_correction,
                });
            }
            Ok((
                draws,
                SourceSamplingV1::SystematicResampling {
                    requested_draws: count,
                    evaluated_draws: count,
                    eof_seed,
                    unit_interval_offset,
                },
            ))
        }
    }
}

fn exactly_one_observation<'a>(
    observations: &'a [FlightObservation],
    epoch_id: &str,
) -> Result<&'a FlightObservation> {
    let mut matching = observations
        .iter()
        .filter(|observation| observation.id == epoch_id);
    let observation = matching
        .next()
        .with_context(|| format!("SATCOM epoch {epoch_id} is absent"))?;
    if matching.next().is_some() {
        bail!("SATCOM epoch {epoch_id} is duplicated");
    }
    Ok(observation)
}

fn require_contact(
    observation: &FlightObservation,
    expected_utc: &str,
    expected_bto_us: f64,
    expected_sd_us: f64,
    relative_time_origin_unix_s_utc: f64,
) -> Result<()> {
    let observed_utc = parse_utc_posix_seconds(&observation.time_utc)?;
    let expected_utc = parse_utc_posix_seconds(expected_utc)?;
    let (bto, sd) = observation
        .measurement
        .bto
        .zip(observation.measurement.bto_sd)
        .context("declared final contact lacks a complete BTO observation")?;
    if !close_time(observed_utc, expected_utc)
        || !close_time(
            relative_time_origin_unix_s_utc + observation.measurement.time.0,
            expected_utc,
        )
        || !close_time(bto.0, expected_bto_us)
        || !close_time(sd.0, expected_sd_us)
        || observation.measurement.bfo.is_some()
        || observation.measurement.bfo_sd.is_some()
    {
        bail!("declared final contact differs from the corrected canonical BTO-only fixture");
    }
    Ok(())
}

fn require_ephemeris_utc(ephemeris_csv: &str, epoch_id: &str, expected_utc: &str) -> Result<()> {
    let mut lines = ephemeris_csv.lines();
    let header = lines.next().context("ephemeris table is empty")?;
    let header_fields = header.split(',').collect::<Vec<_>>();
    let epoch_index = header_fields
        .iter()
        .position(|field| *field == "epoch_id")
        .context("ephemeris table lacks epoch_id")?;
    let utc_index = header_fields
        .iter()
        .position(|field| *field == "time_utc")
        .context("ephemeris table lacks time_utc")?;
    let mut matched_utc = None;
    for (line_index, line) in lines.enumerate() {
        if line.trim().is_empty() {
            continue;
        }
        let fields = line.split(',').collect::<Vec<_>>();
        if fields.len() != header_fields.len() {
            bail!("invalid ephemeris row {}", line_index + 2);
        }
        if fields[epoch_index] == epoch_id && matched_utc.replace(fields[utc_index]).is_some() {
            bail!("ephemeris epoch {epoch_id} is duplicated");
        }
    }
    let observed_utc = parse_utc_posix_seconds(
        matched_utc.with_context(|| format!("ephemeris epoch {epoch_id} is absent"))?,
    )?;
    if !close_time(observed_utc, parse_utc_posix_seconds(expected_utc)?) {
        bail!("ephemeris epoch {epoch_id} has the wrong absolute UTC time");
    }
    Ok(())
}

fn component_id(component: EvidenceComponent) -> &'static str {
    match component {
        EvidenceComponent::Bto => "bto",
        EvidenceComponent::Bfo => "bfo",
        EvidenceComponent::ReceivedPower => "received-power",
        EvidenceComponent::LogonRequestTime => "logon-request-time",
        EvidenceComponent::LogonOccurrence => "logon-occurrence",
    }
}

fn evidence_identity_v2(identity: &EvidenceIdentity) -> EvidenceIdentityV2 {
    EvidenceIdentityV2 {
        dataset_id: "mh370-satcom-log".to_string(),
        observation_id: identity.epoch_id.clone(),
        component_id: component_id(identity.component).to_string(),
        channel_id: identity.channel.clone(),
    }
}

fn dependence_group(identity: &EvidenceIdentity) -> String {
    format!("satcom-event-{}", identity.epoch_id)
}

struct EvidenceBuildContext<'a> {
    config_sha256: &'a str,
    current_input_sha256: &'a BTreeMap<String, String>,
    upstream_config_sha256: &'a str,
    upstream_input_sha256: &'a BTreeMap<String, String>,
}

fn build_evidence_ledger(
    source: &EvidenceLedger,
    r600_identity: &EvidenceIdentity,
    r1200_identity: &EvidenceIdentity,
    context: EvidenceBuildContext<'_>,
    log_evidence_increment: f64,
) -> Result<EvidenceLedgerV2> {
    let reserved = [
        r1200_identity.clone(),
        EvidenceIdentity {
            epoch_id: r600_identity.epoch_id.clone(),
            channel: r600_identity.channel.clone(),
            component: EvidenceComponent::Bfo,
        },
        EvidenceIdentity {
            epoch_id: r1200_identity.epoch_id.clone(),
            channel: r1200_identity.channel.clone(),
            component: EvidenceComponent::Bfo,
        },
        EvidenceIdentity {
            epoch_id: r600_identity.epoch_id.clone(),
            channel: r600_identity.channel.clone(),
            component: EvidenceComponent::LogonRequestTime,
        },
        EvidenceIdentity {
            epoch_id: r600_identity.epoch_id.clone(),
            channel: r600_identity.channel.clone(),
            component: EvidenceComponent::LogonOccurrence,
        },
    ];
    if source
        .entries()
        .iter()
        .any(|entry| reserved.contains(&entry.identity))
    {
        bail!("source handoff already records evidence reserved for end-of-flight inference");
    }

    let mut consumed = source.clone();
    consumed
        .consume(r600_identity.clone())
        .context("R600 BTO evidence cannot be consumed atomically")?;

    let has_embedded = consumed.entries().iter().any(|entry| {
        entry.identity != *r600_identity && entry.disposition == EvidenceDisposition::Consumed
    });
    let has_upstream_diagnostic = consumed
        .entries()
        .iter()
        .any(|entry| entry.disposition == EvidenceDisposition::Diagnostic);

    let mut applications = Vec::new();
    if has_embedded {
        applications.push(EvidenceApplicationV1 {
            id: UPSTREAM_APPLICATION_ID.to_string(),
            role: EvidenceApplicationRoleV1::EmbeddedUpstream,
            model_family: "source-posterior".to_string(),
            config_sha256: context.upstream_config_sha256.to_string(),
            input_sha256: context.upstream_input_sha256.clone(),
            log_evidence_increment: None,
        });
    }
    if has_upstream_diagnostic {
        applications.push(EvidenceApplicationV1 {
            id: "source-diagnostic-evidence".to_string(),
            role: EvidenceApplicationRoleV1::Diagnostic,
            model_family: "source-diagnostic".to_string(),
            config_sha256: context.upstream_config_sha256.to_string(),
            input_sha256: context.upstream_input_sha256.clone(),
            log_evidence_increment: None,
        });
    }
    applications.push(EvidenceApplicationV1 {
        id: R600_APPLICATION_ID.to_string(),
        role: EvidenceApplicationRoleV1::WeightUpdate,
        model_family: "corrected-r600-bto-given-reception".to_string(),
        config_sha256: context.config_sha256.to_string(),
        input_sha256: context.current_input_sha256.clone(),
        log_evidence_increment: Some(log_evidence_increment),
    });
    applications.push(EvidenceApplicationV1 {
        id: FINAL_BFO_DIAGNOSTIC_APPLICATION_ID.to_string(),
        role: EvidenceApplicationRoleV1::Diagnostic,
        model_family: "raw-final-bfo-diagnostic-only".to_string(),
        config_sha256: context.config_sha256.to_string(),
        input_sha256: context.current_input_sha256.clone(),
        log_evidence_increment: None,
    });

    let mut entries = consumed
        .entries()
        .iter()
        .map(|entry| {
            let is_r600 = entry.identity == *r600_identity;
            let (disposition, application_id) = if is_r600 {
                (
                    EvidenceDispositionV2::Consumed,
                    Some(R600_APPLICATION_ID.to_string()),
                )
            } else {
                match entry.disposition {
                    EvidenceDisposition::Consumed => (
                        EvidenceDispositionV2::Consumed,
                        Some(UPSTREAM_APPLICATION_ID.to_string()),
                    ),
                    EvidenceDisposition::HeldOut => (EvidenceDispositionV2::HeldOut, None),
                    EvidenceDisposition::Diagnostic => (
                        EvidenceDispositionV2::Diagnostic,
                        Some("source-diagnostic-evidence".to_string()),
                    ),
                }
            };
            EvidenceEntryV2 {
                identity: evidence_identity_v2(&entry.identity),
                dependence_group_id: if is_r600 {
                    FINAL_LOGON_DEPENDENCE_GROUP.to_string()
                } else {
                    dependence_group(&entry.identity)
                },
                disposition,
                application_id,
            }
        })
        .collect::<Vec<_>>();

    entries.push(EvidenceEntryV2 {
        identity: evidence_identity_v2(r1200_identity),
        dependence_group_id: FINAL_LOGON_DEPENDENCE_GROUP.to_string(),
        disposition: EvidenceDispositionV2::HeldOut,
        application_id: None,
    });
    for identity in [
        EvidenceIdentity {
            epoch_id: r600_identity.epoch_id.clone(),
            channel: r600_identity.channel.clone(),
            component: EvidenceComponent::Bfo,
        },
        EvidenceIdentity {
            epoch_id: r1200_identity.epoch_id.clone(),
            channel: r1200_identity.channel.clone(),
            component: EvidenceComponent::Bfo,
        },
    ] {
        entries.push(EvidenceEntryV2 {
            identity: evidence_identity_v2(&identity),
            dependence_group_id: FINAL_LOGON_DEPENDENCE_GROUP.to_string(),
            disposition: EvidenceDispositionV2::Diagnostic,
            application_id: Some(FINAL_BFO_DIAGNOSTIC_APPLICATION_ID.to_string()),
        });
    }
    for component in [
        EvidenceComponent::LogonRequestTime,
        EvidenceComponent::LogonOccurrence,
    ] {
        let identity = EvidenceIdentity {
            epoch_id: r600_identity.epoch_id.clone(),
            channel: r600_identity.channel.clone(),
            component,
        };
        entries.push(EvidenceEntryV2 {
            identity: evidence_identity_v2(&identity),
            dependence_group_id: FINAL_LOGON_DEPENDENCE_GROUP.to_string(),
            disposition: EvidenceDispositionV2::HeldOut,
            application_id: None,
        });
    }

    let ledger = EvidenceLedgerV2 {
        entries,
        applications,
    };
    ledger
        .validate()
        .map_err(anyhow::Error::new)
        .context("generated impact evidence ledger violates schema v1")?;
    Ok(ledger)
}

fn transition_termination_v1(value: TransitionTermination) -> TransitionTerminationV1 {
    match value {
        TransitionTermination::Impact => TransitionTerminationV1::Impact,
        TransitionTermination::MaximumDuration => TransitionTerminationV1::MaximumDuration,
        TransitionTermination::MaximumSteps => TransitionTerminationV1::MaximumSteps,
        TransitionTermination::DeclaredEnvelopeExit(exit) => match exit {
            mh370_end_of_flight::DeclaredEnvelopeExit::AirspeedBelowMinimum => {
                TransitionTerminationV1::AirspeedBelowMinimum
            }
            mh370_end_of_flight::DeclaredEnvelopeExit::AirspeedAboveMaximum => {
                TransitionTerminationV1::AirspeedAboveMaximum
            }
            mh370_end_of_flight::DeclaredEnvelopeExit::NearVerticalFlightPath => {
                TransitionTerminationV1::NearVerticalFlightPath
            }
        },
    }
}

fn restart_family_v1(value: RestartTransientFamily) -> RestartTransientFamilyV1 {
    match value {
        RestartTransientFamily::NoAdditionalTransient => {
            RestartTransientFamilyV1::NoAdditionalTransient
        }
        RestartTransientFamily::CommonOcxoWarmup => RestartTransientFamilyV1::CommonOcxoWarmup,
        RestartTransientFamily::R1200ChannelSettling => {
            RestartTransientFamilyV1::R1200ChannelSettling
        }
        RestartTransientFamily::UnspecifiedRestartTransient => {
            RestartTransientFamilyV1::UnspecifiedRestartTransient
        }
    }
}

fn control_trigger_v1(
    value: mh370_end_of_flight::ControlTransitionTrigger,
) -> ControlTransitionTriggerV1 {
    match value {
        mh370_end_of_flight::ControlTransitionTrigger::DualEngineFlameout => {
            ControlTransitionTriggerV1::DualEngineFlameout
        }
        mh370_end_of_flight::ControlTransitionTrigger::DualEngineGeneratorLoss => {
            ControlTransitionTriggerV1::DualEngineGeneratorLoss
        }
    }
}

fn make_kernel_input(
    particle: &PosteriorHandoffParticle,
    scenario: &ImpactScenarioConfig,
    fuel: PoweredFuelAllocation,
    environment: &ResolvedImpactEnvironment,
    aerodynamics: AerodynamicModel,
) -> Result<TransitionKernelInput> {
    let speed_of_sound_m_s = environment.speed_of_sound_m_s(
        particle.aircraft.time,
        particle.aircraft.position,
        particle.aircraft.altitude,
    )?;
    let true_airspeed_m_s = speed_of_sound_m_s * particle.mach;
    let vertical_speed_m_s = particle.aircraft.vertical_speed.0 * MPS_PER_FPM;
    if !true_airspeed_m_s.is_finite() || true_airspeed_m_s <= 0.0 {
        bail!("particle Mach and scenario speed of sound do not define a positive airspeed");
    }
    let sine_gamma = vertical_speed_m_s / true_airspeed_m_s;
    if !sine_gamma.is_finite() || sine_gamma.abs() >= 1.0 {
        bail!("particle vertical speed is incompatible with its conditional true airspeed");
    }
    let flight_path_angle = Degrees(sine_gamma.asin().to_degrees());
    Ok(TransitionKernelInput {
        initial: TransitionInitialCondition {
            flight: PointMassState {
                time: particle.aircraft.time,
                position: particle.aircraft.position,
                altitude: particle.aircraft.altitude,
                true_airspeed: mh370_end_of_flight::MetresPerSecond(true_airspeed_m_s),
                flight_path_angle,
                heading_true: particle.heading_true,
            },
            mass: fuel.mass,
            fuel: fuel.fuel,
            engines: fuel.engines,
            electrical: scenario.electrical,
            apu: scenario.apu,
            ocxo: scenario.ocxo,
        },
        family: ConditionalModelFamily {
            control: ControlFamily::Controlled,
            restart_transient: scenario.restart_transient,
        },
        model_weight: scenario.model_weight,
        control: scenario.control_policy.pre_trigger_controlled.clone(),
        aerodynamics,
        atmosphere: environment.fallback_profile(),
        apu_start_policy: scenario.apu_start_policy,
        integration: scenario.integration,
    })
}

fn checkpoint_aircraft(
    checkpoint: &ExactTimeCheckpoint,
    particle: &PosteriorHandoffParticle,
) -> AircraftState {
    let kinematics = checkpoint.state.kinematics;
    AircraftState {
        time: kinematics.point_mass.time,
        position: kinematics.point_mass.position,
        altitude: kinematics.point_mass.altitude,
        track_true: kinematics.ground_track_true,
        ground_speed: Knots(kinematics.ground_speed.0 / MPS_PER_KNOT),
        vertical_speed: FeetPerMinute(kinematics.vertical_speed.0 / MPS_PER_FPM),
        bfo_bias: mh370_domain::Hertz(particle.bfo_bias.mean_hz),
    }
}

fn score_r600(
    checkpoints: &[ExactTimeCheckpoint],
    transition: &WeightedTransition,
    particle: &PosteriorHandoffParticle,
    observation: &FlightObservation,
    satcom: &SatcomModelConfig,
) -> Result<CheckpointScoreV1> {
    let Some(checkpoint) = checkpoints
        .iter()
        .find(|checkpoint| close_time(checkpoint.requested_elapsed.0, REQUIRED_R600_ELAPSED_S))
    else {
        return Ok(CheckpointScoreV1 {
            requested_elapsed_s: REQUIRED_R600_ELAPSED_S,
            status: CheckpointScoreStatusV1::Unreached {
                termination: transition.termination,
                log_likelihood: None,
            },
        });
    };
    if !checkpoint.state.electrical.satcom_powered {
        return Ok(CheckpointScoreV1 {
            requested_elapsed_s: REQUIRED_R600_ELAPSED_S,
            status: CheckpointScoreStatusV1::PhysicallyUnavailable {
                checkpoint: Box::new(checkpoint.clone()),
                reason:
                    "R600 reception is conditioned on SATCOM being powered at the exact checkpoint"
                        .to_string(),
                log_likelihood: None,
            },
        });
    }
    let mut bias = particle.bfo_bias;
    let fit = evaluate_observation(
        checkpoint_aircraft(checkpoint, particle),
        &mut bias,
        &observation.measurement,
        observation.satellite_afc_hz,
        false,
        satcom,
    )?;
    let predicted_bto_us = fit
        .predicted_bto_us
        .context("R600 BTO model did not return a prediction")?;
    let residual_us = fit
        .bto_residual_us
        .context("R600 BTO model did not return a residual")?;
    if !fit.log_likelihood.is_finite() {
        bail!("R600 BTO likelihood is not finite");
    }
    Ok(CheckpointScoreV1 {
        requested_elapsed_s: REQUIRED_R600_ELAPSED_S,
        status: CheckpointScoreStatusV1::Reached {
            checkpoint: Box::new(checkpoint.clone()),
            observed_bto_us: REQUIRED_R600_BTO_US,
            standard_deviation_us: REQUIRED_R600_BTO_SD_US,
            predicted_bto_us,
            residual_us,
            log_likelihood: fit.log_likelihood,
        },
    })
}

fn log_sum_exp(values: impl Iterator<Item = f64>) -> Option<f64> {
    let values = values.collect::<Vec<_>>();
    if values.is_empty() || values.iter().any(|value| !value.is_finite()) {
        return None;
    }
    let maximum = values.iter().copied().fold(f64::NEG_INFINITY, f64::max);
    Some(
        maximum
            + values
                .iter()
                .map(|value| (value - maximum).exp())
                .sum::<f64>()
                .ln(),
    )
}

fn normalize_mass_map(masses: &mut BTreeMap<TransitionTerminationV1, f64>) {
    let total = masses.values().sum::<f64>();
    if total.is_finite() && total > 0.0 {
        for mass in masses.values_mut() {
            *mass /= total;
        }
    }
}

fn termination_masses(
    records: &[TransitionSidecarRecordV1],
) -> (Vec<TerminationMassV1>, Vec<OutcomeWeightMassV1>) {
    let mut prior = BTreeMap::<TransitionTerminationV1, f64>::new();
    let mut conditioned = BTreeMap::<TransitionTerminationV1, f64>::new();
    for record in records {
        let termination = transition_termination_v1(record.transition.termination);
        *prior.entry(termination).or_default() += record.prior_weight;
        *conditioned.entry(termination).or_default() += record.r600_conditioned_weight;
    }
    normalize_mass_map(&mut prior);
    normalize_mass_map(&mut conditioned);
    let all = prior
        .keys()
        .chain(conditioned.keys())
        .copied()
        .collect::<std::collections::BTreeSet<_>>();
    let sidecar = all
        .iter()
        .map(|termination| TerminationMassV1 {
            termination: *termination,
            prior_normalized_mass: prior.get(termination).copied().unwrap_or(0.0),
            r600_conditioned_normalized_mass: conditioned.get(termination).copied().unwrap_or(0.0),
        })
        .collect::<Vec<_>>();
    let conditioning = all
        .iter()
        .map(|termination| OutcomeWeightMassV1 {
            termination: *termination,
            normalized_mass: conditioned.get(termination).copied().unwrap_or(0.0),
        })
        .collect::<Vec<_>>();
    (sidecar, conditioning)
}

fn build_impact_particles(
    records: &[TransitionSidecarRecordV1],
    source_run_id: &str,
    scenario_id: &str,
    relative_time_origin_unix_s_utc: f64,
    target_log_mass: f64,
) -> Vec<ImpactPosteriorParticleV1> {
    records
        .iter()
        .filter_map(|record| {
            let impact = record.transition.impact.as_ref()?;
            let log_likelihood = record.r600_score.log_likelihood()?;
            let track_rad = impact.point.bearing_true.to_radians();
            let raw_log_weight = record.upstream_normalized_log_weight
                + record.sampling_log_correction
                + log_likelihood;
            Some(ImpactPosteriorParticleV1 {
                identity: ImpactParticleIdentityV1 {
                    source_run_id: source_run_id.to_string(),
                    upstream: record.upstream_identity.clone(),
                    eof_scenario_id: scenario_id.to_string(),
                    eof_draw_id: record.eof_draw_id,
                },
                upstream_normalized_log_weight: record.upstream_normalized_log_weight,
                eof_draw_log_weight: record.sampling_log_correction,
                likelihood_terms: vec![ParticleLikelihoodTermV1 {
                    application_id: R600_APPLICATION_ID.to_string(),
                    log_likelihood,
                }],
                normalized_log_weight: raw_log_weight - target_log_mass,
                termination_mass_kg: impact.mass.0,
                kinematics: ImpactKinematicsV1 {
                    time_utc_unix_s: relative_time_origin_unix_s_utc + impact.point.time.0,
                    position_wgs84: impact.point.position,
                    true_airspeed_m_s: impact.true_airspeed.0,
                    ground_velocity_enu_m_s: EnuVelocityV1 {
                        east: impact.ground_speed.0 * track_rad.sin(),
                        north: impact.ground_speed.0 * track_rad.cos(),
                        up: impact.vertical_speed.0,
                    },
                    displacement_from_last_contact_nm: impact
                        .point
                        .displacement_from_last_contact
                        .0,
                },
                energy: ImpactEnergyV1 {
                    total_j: impact.kinetic_energy.0,
                    horizontal_j: impact.horizontal_kinetic_energy.0,
                    vertical_j: impact.vertical_kinetic_energy.0,
                },
                attitude: None,
                contact_duration_s: None,
            })
        })
        .collect()
}

pub(crate) fn infer_impact(config_path: &Path, output: &Path) -> Result<()> {
    let config_bytes =
        fs::read(config_path).with_context(|| format!("cannot read {}", config_path.display()))?;
    let config: ImpactConfig =
        toml::from_str(std::str::from_utf8(&config_bytes).context("impact config is not UTF-8")?)
            .context("cannot parse impact TOML")?;
    let config_sha256 = sha256_bytes(&config_bytes);
    if config.schema_version != CONFIG_SCHEMA_VERSION
        || !valid_identifier(&config.hypothesis_id)
        || config.code_revision.trim().is_empty()
        || !valid_identifier(&config.scenario.id)
        || config.source_draw_count == Some(0)
        || config
            .source_draw_count
            .is_some_and(|count| count > u32::MAX as usize)
        || config.scenario.model_weight.0.to_bits() != 1.0_f64.to_bits()
        || config.scenario.control_policy.scenario.label != config.scenario.id
        || config.inputs.r600_channel != "R600"
        || config.inputs.r1200_channel != "R1200"
        || !valid_identifier(&config.inputs.source_epoch_id)
        || !valid_identifier(&config.inputs.r600_epoch_id)
        || !valid_identifier(&config.inputs.r1200_epoch_id)
        || config.inputs.source_epoch_id == config.inputs.r600_epoch_id
        || config.inputs.r600_epoch_id == config.inputs.r1200_epoch_id
    {
        bail!(
            "impact configuration is incomplete or violates the schema-v2 single-scenario contract"
        );
    }
    config.satcom.validate()?;

    let relative_time_origin_unix_s_utc =
        parse_utc_posix_seconds(&config.relative_time_origin_utc)?;
    let source_checkpoint_time_unix_s_utc = parse_utc_posix_seconds(&config.source_checkpoint_utc)?;
    let required_source_utc = parse_utc_posix_seconds(REQUIRED_SOURCE_UTC)?;
    let r600_checkpoint_time_unix_s_utc = parse_utc_posix_seconds(REQUIRED_R600_UTC)?;
    let r1200_checkpoint_time_unix_s_utc = parse_utc_posix_seconds(REQUIRED_R1200_UTC)?;
    if !close_time(source_checkpoint_time_unix_s_utc, required_source_utc)
        || !close_time(
            r600_checkpoint_time_unix_s_utc - source_checkpoint_time_unix_s_utc,
            REQUIRED_R600_ELAPSED_S,
        )
        || !close_time(
            r1200_checkpoint_time_unix_s_utc - source_checkpoint_time_unix_s_utc,
            REQUIRED_R1200_ELAPSED_S,
        )
    {
        bail!("schema v2 requires the exact 00:10:59, 00:19:29, and 00:19:37 UTC epochs");
    }

    let (environment, environment_input_sha256) = resolve_environment(
        config_path,
        &config.scenario.environment,
        relative_time_origin_unix_s_utc,
    )?;
    let fuel_model_resolution = resolve_fuel_model(
        &config.scenario.fuel_model,
        source_checkpoint_time_unix_s_utc,
    )?;
    let aerodynamics = config.scenario.aerodynamic_family.model();

    let source_path = resolve(config_path, &config.source_handoff);
    let observation_path = resolve(config_path, &config.inputs.observations);
    let ephemeris_path = resolve(config_path, &config.inputs.satellite_ephemeris);
    let source_bytes = fs::read(&source_path)
        .with_context(|| format!("cannot read source handoff {}", source_path.display()))?;
    let observation_bytes = fs::read(&observation_path)
        .with_context(|| format!("cannot read observations {}", observation_path.display()))?;
    let ephemeris_bytes = fs::read(&ephemeris_path)
        .with_context(|| format!("cannot read ephemeris {}", ephemeris_path.display()))?;
    let source: PosteriorHandoff =
        serde_json::from_slice(&source_bytes).context("source handoff is not valid JSON")?;
    source
        .validate()
        .map_err(anyhow::Error::new)
        .context("source posterior handoff is invalid")?;
    if !valid_identifier(&source.run.model_family) {
        bail!("source model-family identifier is not schema-v1 compatible");
    }

    let observation_csv =
        std::str::from_utf8(&observation_bytes).context("observation CSV is not UTF-8")?;
    let ephemeris_csv =
        std::str::from_utf8(&ephemeris_bytes).context("ephemeris CSV is not UTF-8")?;
    let observations = parse_satcom_observations(
        observation_csv,
        ephemeris_csv,
        config.inputs.ground_station_position_km,
        None,
    )?;
    let source_observation =
        exactly_one_observation(&observations, &config.inputs.source_epoch_id)?;
    let r600_observation = exactly_one_observation(&observations, &config.inputs.r600_epoch_id)?;
    let r1200_observation = exactly_one_observation(&observations, &config.inputs.r1200_epoch_id)?;
    require_ephemeris_utc(
        ephemeris_csv,
        &config.inputs.source_epoch_id,
        REQUIRED_SOURCE_UTC,
    )?;
    require_ephemeris_utc(
        ephemeris_csv,
        &config.inputs.r600_epoch_id,
        REQUIRED_R600_UTC,
    )?;
    require_ephemeris_utc(
        ephemeris_csv,
        &config.inputs.r1200_epoch_id,
        REQUIRED_R1200_UTC,
    )?;
    require_contact(
        r600_observation,
        REQUIRED_R600_UTC,
        REQUIRED_R600_BTO_US,
        REQUIRED_R600_BTO_SD_US,
        relative_time_origin_unix_s_utc,
    )?;
    require_contact(
        r1200_observation,
        REQUIRED_R1200_UTC,
        REQUIRED_R1200_BTO_US,
        REQUIRED_R1200_BTO_SD_US,
        relative_time_origin_unix_s_utc,
    )?;
    if !close_time(
        parse_utc_posix_seconds(&source_observation.time_utc)?,
        source_checkpoint_time_unix_s_utc,
    ) || !close_time(
        relative_time_origin_unix_s_utc + source_observation.measurement.time.0,
        source_checkpoint_time_unix_s_utc,
    ) || source.particles.iter().any(|particle| {
        !close_time(
            relative_time_origin_unix_s_utc + particle.aircraft.time.0,
            source_checkpoint_time_unix_s_utc,
        )
    }) {
        bail!("absolute UTC, observation-relative time, and source particle time disagree");
    }

    let r600_identity = EvidenceIdentity {
        epoch_id: config.inputs.r600_epoch_id.clone(),
        channel: Some(config.inputs.r600_channel.clone()),
        component: EvidenceComponent::Bto,
    };
    let r1200_identity = EvidenceIdentity {
        epoch_id: config.inputs.r1200_epoch_id.clone(),
        channel: Some(config.inputs.r1200_channel.clone()),
        component: EvidenceComponent::Bto,
    };
    if source.evidence.entries().iter().any(|entry| {
        entry.identity == r600_identity && entry.disposition == EvidenceDisposition::Consumed
    }) {
        bail!("R600 BTO was already consumed upstream; refusing duplicate evidence use");
    }

    let source_handoff_sha256 = sha256_bytes(&source_bytes);
    let mut current_input_sha256 = BTreeMap::from([
        (
            "satcom_observations".to_string(),
            sha256_bytes(&observation_bytes),
        ),
        (
            "satellite_ephemeris".to_string(),
            sha256_bytes(&ephemeris_bytes),
        ),
    ]);
    current_input_sha256.extend(environment_input_sha256.clone());
    let mut input_sha256 = BTreeMap::from([
        (
            "source_posterior_handoff".to_string(),
            source_handoff_sha256.clone(),
        ),
        (
            "satcom_observations".to_string(),
            sha256_bytes(&observation_bytes),
        ),
        (
            "satellite_ephemeris".to_string(),
            sha256_bytes(&ephemeris_bytes),
        ),
    ]);
    input_sha256.extend(environment_input_sha256);
    build_evidence_ledger(
        &source.evidence,
        &r600_identity,
        &r1200_identity,
        EvidenceBuildContext {
            config_sha256: &config_sha256,
            current_input_sha256: &current_input_sha256,
            upstream_config_sha256: &source.run.config_sha256,
            upstream_input_sha256: &source.run.input_sha256,
        },
        0.0,
    )
    .context("end-of-flight evidence cannot be applied atomically")?;
    let executable_sha256 = executable_sha256()?;
    let scenario_config_sha256 = sha256_bytes(&serde_json::to_vec(&config.scenario)?);
    let fuel_allocation = allocate_powered_fuel(fuel_model_resolution.allocation_input)
        .context("conditional fuel allocation is invalid")?;
    let (draws, source_sampling) =
        select_source_draws(&source, config.source_draw_count, config.eof_seed)?;
    let checkpoint_schedule = ExactTimeCheckpointSchedule {
        requested_elapsed_times: vec![Seconds(REQUIRED_R600_ELAPSED_S)],
    };

    prepare_output(output)?;
    let mut records = Vec::with_capacity(draws.len());
    for draw in draws {
        let kernel_input = make_kernel_input(
            &draw.particle,
            &config.scenario,
            fuel_allocation,
            &environment,
            aerodynamics,
        )?;
        let attempt = attempt_controlled_to_uncontrolled_with_atmosphere_and_checkpoints(
            &kernel_input,
            &config.scenario.control_policy,
            &checkpoint_schedule,
            &environment,
        )
        .context("conditional end-of-flight propagation failed")?;
        let r600_score = score_r600(
            &attempt.checkpoints,
            &attempt.transition,
            &draw.particle,
            r600_observation,
            &config.satcom,
        )?;
        let prior_log_weight = draw.particle.normalized_log_weight + draw.sampling_log_correction;
        records.push(TransitionSidecarRecordV1 {
            upstream_identity: draw.particle.identity,
            eof_draw_id: draw.eof_draw_id,
            upstream_normalized_log_weight: draw.particle.normalized_log_weight,
            sampling_log_correction: draw.sampling_log_correction,
            initial_flight: kernel_input.initial.flight,
            transition: attempt.transition,
            reached_checkpoints: attempt.checkpoints,
            checkpoint_status: attempt.checkpoint_status,
            control_transition: attempt.control_transition,
            r600_score,
            prior_weight: prior_log_weight.exp(),
            r600_conditioned_weight: 0.0,
        });
    }

    let log_evidence_increment = log_sum_exp(records.iter().filter_map(|record| {
        record.r600_score.log_likelihood().map(|log_likelihood| {
            record.upstream_normalized_log_weight + record.sampling_log_correction + log_likelihood
        })
    }))
    .context("the selected scenario has zero probability of reaching the R600 checkpoint")?;
    for record in &mut records {
        record.r600_conditioned_weight = record.r600_score.log_likelihood().map_or(0.0, |value| {
            (record.upstream_normalized_log_weight + record.sampling_log_correction + value
                - log_evidence_increment)
                .exp()
        });
    }
    let (outcome_mass, conditioning_mass) = termination_masses(&records);
    let impact_mass = conditioning_mass
        .iter()
        .find(|outcome| outcome.termination == TransitionTerminationV1::Impact)
        .map(|outcome| outcome.normalized_mass)
        .filter(|mass| *mass > 0.0)
        .context("the R600-conditioned scenario contains no impact outcomes")?;
    let target_log_mass = log_evidence_increment + impact_mass.ln();

    let environment_diagnostics = match &environment {
        ResolvedImpactEnvironment::Static { .. } => EnvironmentDiagnosticsV1 {
            family_id: "static_altitude_profile".to_string(),
            sample_count: 0,
            below_minimum_pressure_altitude_clamp_count: 0,
            above_maximum_pressure_altitude_clamp_count: 0,
            density_rule: "caller_supplied_altitude_profile".to_string(),
            limitations: vec![
                "Altitude-only static profile; no time-varying or horizontal weather structure."
                    .to_string(),
            ],
        },
        ResolvedImpactEnvironment::Era5(atmosphere) => EnvironmentDiagnosticsV1 {
            family_id: "era5_pressure_altitude_4d".to_string(),
            sample_count: atmosphere.sample_count.get(),
            below_minimum_pressure_altitude_clamp_count: atmosphere
                .below_minimum_clamp_count
                .get(),
            above_maximum_pressure_altitude_clamp_count: atmosphere
                .above_maximum_clamp_count
                .get(),
            density_rule:
                "ISA pressure at pressure altitude divided by dry-air gas constant and interpolated ERA5 temperature"
                    .to_string(),
            limitations: vec![
                "ERA5 provides horizontal wind and temperature only; vertical wind is zero in the point-mass equations."
                    .to_string(),
                "Below 500 ft, only pressure altitude is clamped to 500 ft; UTC and WGS84 position remain dynamic and unclamped."
                    .to_string(),
                "Above 43,000 ft, only pressure altitude is clamped to 43,000 ft; this affects proxy trajectories that briefly leave the extraction envelope."
                    .to_string(),
                "Pressure altitude is used as geometric height in point-mass position/impact integration."
                    .to_string(),
            ],
        },
    };
    let limitations = vec![
        "One caller-selected conditional end-of-flight scenario; no scenario probabilities or model-family averaging.".to_string(),
        "Corrected 00:19:29 R600 BTO is the only new likelihood. Recorded reception requires SATCOM power at that checkpoint; power is a physical support condition and receives no separate likelihood.".to_string(),
        "00:19:37 R1200 BTO is held out; both final raw BFOs remain diagnostic and do not alter weights.".to_string(),
        format!("Aerodynamic family {} is an explicit attached-flow conditional proxy, not a B777 terminal-flight calibration.", config.scenario.aerodynamic_family.evidence_status()),
        "Control history, fuel/feed state, APU, electrical, and restart behavior are explicit conditional inputs, not inferred model-family probabilities.".to_string(),
        "ERA5 temperature and horizontal wind are sampled at every force evaluation; the extraction is hourly and 0.5 degree, so interpolation does not create high-cadence observations.".to_string(),
        "Impact attitude and water-contact duration are unresolved and therefore null.".to_string(),
    ];
    let sidecar = TransitionSidecarV1 {
        schema_id: SIDECAR_SCHEMA_ID.to_string(),
        schema_version: SIDECAR_SCHEMA_VERSION,
        hypothesis_id: config.hypothesis_id.clone(),
        producer_executable_sha256: executable_sha256.clone(),
        config_sha256: config_sha256.clone(),
        source_handoff_sha256: source_handoff_sha256.clone(),
        source_run_identity_sha256: source.run.run_identity_sha256.clone(),
        eof_seed: config.eof_seed,
        relative_time_origin_unix_s_utc,
        source_checkpoint_time_unix_s_utc,
        r600_checkpoint_time_unix_s_utc,
        r600_elapsed_s: REQUIRED_R600_ELAPSED_S,
        source_sampling,
        scenario: config.scenario.clone(),
        fuel_model_resolution,
        fuel_allocation,
        environment_diagnostics,
        log_evidence_increment,
        outcome_mass,
        records,
        limitations: limitations.clone(),
    };
    let sidecar_path = output.join("transition-sidecar.json");
    write_json(&sidecar_path, &sidecar)?;
    let transition_sidecar_sha256 = sha256_file(&sidecar_path)?;
    let run_identity_sha256 = sha256_bytes(&serde_json::to_vec(&ImpactRunIdentityPreimage {
        domain: "mh370-impact-inference-run-v1",
        engine_version: env!("CARGO_PKG_VERSION"),
        producer_executable_sha256: &executable_sha256,
        config_sha256: &config_sha256,
        input_sha256: &input_sha256,
        source_run_identity_sha256: &source.run.run_identity_sha256,
        eof_scenario_id: &config.scenario.id,
        eof_seed: config.eof_seed,
        transition_sidecar_sha256: &transition_sidecar_sha256,
    })?);
    let source_run_id = format!("source:{}:{}", source.run.model_family, source.run.seed);
    let evidence = build_evidence_ledger(
        &source.evidence,
        &r600_identity,
        &r1200_identity,
        EvidenceBuildContext {
            config_sha256: &config_sha256,
            current_input_sha256: &current_input_sha256,
            upstream_config_sha256: &source.run.config_sha256,
            upstream_input_sha256: &source.run.input_sha256,
        },
        log_evidence_increment,
    )?;
    let particles = build_impact_particles(
        &sidecar.records,
        &source_run_id,
        &config.scenario.id,
        relative_time_origin_unix_s_utc,
        target_log_mass,
    );
    let handoff = ImpactPosteriorHandoffV1 {
        schema_id: IMPACT_POSTERIOR_HANDOFF_SCHEMA_ID.to_string(),
        schema_version: IMPACT_POSTERIOR_HANDOFF_SCHEMA_VERSION,
        time_basis: AbsoluteTimeBasisV1 {
            scale: "utc".to_string(),
            epoch: "1970-01-01T00:00:00Z".to_string(),
            unit: "second".to_string(),
            convention: "posix_seconds_no_leap_representation".to_string(),
        },
        run: ImpactRunProvenanceV1 {
            hypothesis_id: config.hypothesis_id.clone(),
            run_identity_sha256,
            producer_executable_sha256: executable_sha256.clone(),
            config_sha256: config_sha256.clone(),
            input_sha256: input_sha256.clone(),
            code_revision: config.code_revision.clone(),
            eof_seed: config.eof_seed,
            transition_sidecar_sha256,
        },
        source_runs: vec![SourceRunRefV1 {
            id: source_run_id,
            model_family: source.run.model_family.clone(),
            seed: source.run.seed,
            pool_log_weight: 0.0,
            posterior_handoff_sha256: source_handoff_sha256,
            upstream_run_identity_sha256: source.run.run_identity_sha256.clone(),
            upstream_config_sha256: source.run.config_sha256.clone(),
            upstream_input_sha256: source.run.input_sha256.clone(),
            relative_time_origin_unix_s_utc,
            source_checkpoint_time_unix_s_utc,
        }],
        scenario_combination: ScenarioCombinationV1::Separate,
        eof_scenarios: vec![EofScenarioV1 {
            id: config.scenario.id.clone(),
            family: ConditionalModelFamilyV1 {
                control_policy: EofControlPolicyFamilyV1::ControlledToUncontrolled {
                    trigger: control_trigger_v1(config.scenario.control_policy.scenario.trigger),
                },
                restart_transient: restart_family_v1(config.scenario.restart_transient),
            },
            log_weight: 0.0,
            config_sha256: scenario_config_sha256,
        }],
        evidence,
        impact_conditioning: ImpactConditioningV1 {
            conditioned_on: "transition_termination=impact".to_string(),
            outcome_weight_mass: conditioning_mass,
        },
        particles,
    };
    handoff
        .validate()
        .map_err(anyhow::Error::new)
        .context("generated impact posterior handoff is invalid")?;
    let handoff_path = output.join("impact-posterior-handoff.json");
    write_json(&handoff_path, &handoff)?;

    let outputs = BTreeMap::from([
        (
            "impact-posterior-handoff.json".to_string(),
            sha256_file(&handoff_path)?,
        ),
        (
            "transition-sidecar.json".to_string(),
            sha256_file(&sidecar_path)?,
        ),
    ]);
    let manifest = ImpactManifestV1 {
        schema_version: MANIFEST_SCHEMA_VERSION,
        engine_version: env!("CARGO_PKG_VERSION"),
        executable_sha256,
        command: "infer-impact",
        hypothesis_id: config.hypothesis_id,
        config_path: config_path.display().to_string(),
        config_sha256,
        input_sha256,
        run_identity_sha256: handoff.run.run_identity_sha256.clone(),
        outputs,
        scientific_scope: limitations,
    };
    let manifest_path = output.join("run-manifest.json");
    write_json(&manifest_path, &manifest)?;
    println!(
        "status=complete source_seed={} draws={} impacts={} r600_log_evidence={:.9} impact_mass={:.9} handoff={} sidecar={} manifest={}",
        source.run.seed,
        sidecar.records.len(),
        handoff.particles.len(),
        log_evidence_increment,
        impact_mass,
        handoff_path.display(),
        sidecar_path.display(),
        manifest_path.display()
    );
    Ok(())
}

#[cfg(test)]
mod tests {
    use mh370_domain::{Feet, Hertz, LatLon};
    use mh370_dynamics::LateralMode;
    use mh370_estimator::{PosteriorRunMetadata, TurnMetadata, POSTERIOR_HANDOFF_SCHEMA_VERSION};
    use mh370_satcom::BfoBiasState;

    use super::*;

    fn digest(byte: char) -> String {
        std::iter::repeat_n(byte, 64).collect()
    }

    fn source_handoff() -> PosteriorHandoff {
        let particles = [0.25_f64, 0.75]
            .into_iter()
            .enumerate()
            .map(|(index, weight)| PosteriorHandoffParticle {
                identity: PosteriorParticleIdentity {
                    model_family: "fixture-family".to_string(),
                    seed: 7,
                    particle: index,
                },
                normalized_log_weight: weight.ln(),
                source_log_likelihood: -2.0,
                aircraft: AircraftState {
                    time: Seconds(22_150.0),
                    position: LatLon::new(-36.0, 89.0).unwrap(),
                    altitude: Feet(35_000.0),
                    track_true: Degrees(185.0),
                    ground_speed: Knots(470.0),
                    vertical_speed: FeetPerMinute(0.0),
                    bfo_bias: Hertz(150.0),
                },
                heading_true: Degrees(187.0),
                lateral_mode: LateralMode::ConstantTrueTrack,
                mach: 0.8,
                turn: TurnMetadata {
                    initial_position: LatLon::new(5.0, 99.0).unwrap(),
                    initial_track_true: Degrees(290.0),
                    turn_time: Seconds(2_000.0),
                    post_turn_track_true: Degrees(185.0),
                    turn_count: 1,
                },
                bfo_bias: BfoBiasState {
                    mean_hz: 150.0,
                    variance_hz2: 4.0,
                },
            })
            .collect();
        PosteriorHandoff {
            schema_version: POSTERIOR_HANDOFF_SCHEMA_VERSION,
            run: PosteriorRunMetadata {
                model_family: "fixture-family".to_string(),
                seed: 7,
                lateral_mode: Some(LateralMode::ConstantTrueTrack),
                run_identity_sha256: digest('1'),
                config_sha256: digest('2'),
                input_sha256: BTreeMap::from([("fixture".to_string(), digest('3'))]),
                fixed_waypoint: None,
            },
            evidence: EvidenceLedger::new(),
            particles,
        }
    }

    #[test]
    fn systematic_resampling_is_deterministic_and_exactly_corrected() {
        let source = source_handoff();
        source.validate().unwrap();
        let (first, sampling) = select_source_draws(&source, Some(3), 42).unwrap();
        let (second, repeated) = select_source_draws(&source, Some(3), 42).unwrap();
        assert_eq!(first, second);
        assert_eq!(sampling, repeated);
        let expected = -(3.0_f64).ln();
        let total = first
            .iter()
            .map(|draw| {
                let combined = draw.particle.normalized_log_weight + draw.sampling_log_correction;
                assert!((combined - expected).abs() < 1.0e-14);
                combined.exp()
            })
            .sum::<f64>();
        assert!((total - 1.0).abs() < 1.0e-14);
        assert!(first.iter().any(|draw| draw.sampling_log_correction > 0.0));
        assert!(first.iter().any(|draw| draw.sampling_log_correction < 0.0));
    }

    #[test]
    fn r600_consumption_rejects_duplicate_and_has_one_weight_update() {
        let r600 = EvidenceIdentity {
            epoch_id: "m0019a".to_string(),
            channel: Some("R600".to_string()),
            component: EvidenceComponent::Bto,
        };
        let r1200 = EvidenceIdentity {
            epoch_id: "m0019b".to_string(),
            channel: Some("R1200".to_string()),
            component: EvidenceComponent::Bto,
        };
        let hashes = BTreeMap::from([("fixture".to_string(), digest('4'))]);
        let ledger = build_evidence_ledger(
            &EvidenceLedger::new(),
            &r600,
            &r1200,
            EvidenceBuildContext {
                config_sha256: &digest('5'),
                current_input_sha256: &hashes,
                upstream_config_sha256: &digest('6'),
                upstream_input_sha256: &hashes,
            },
            -3.0,
        )
        .unwrap();
        assert_eq!(
            ledger
                .applications
                .iter()
                .filter(|application| application.role == EvidenceApplicationRoleV1::WeightUpdate)
                .count(),
            1
        );
        assert_eq!(
            ledger
                .entries
                .iter()
                .filter(|entry| {
                    entry.disposition == EvidenceDispositionV2::Consumed
                        && entry.dependence_group_id == FINAL_LOGON_DEPENDENCE_GROUP
                })
                .count(),
            1
        );
        assert_eq!(
            ledger
                .entries
                .iter()
                .filter(|entry| {
                    entry.identity == evidence_identity_v2(&r1200)
                        && entry.disposition == EvidenceDispositionV2::HeldOut
                        && entry.application_id.is_none()
                })
                .count(),
            1
        );
        assert_eq!(
            ledger
                .entries
                .iter()
                .filter(|entry| {
                    entry.identity.component_id == "bfo"
                        && entry.disposition == EvidenceDispositionV2::Diagnostic
                        && entry.application_id.as_deref()
                            == Some(FINAL_BFO_DIAGNOSTIC_APPLICATION_ID)
                })
                .count(),
            2
        );
        assert_eq!(
            ledger
                .entries
                .iter()
                .filter(|entry| {
                    matches!(
                        entry.identity.component_id.as_str(),
                        "logon-request-time" | "logon-occurrence"
                    ) && entry.disposition == EvidenceDispositionV2::HeldOut
                        && entry.application_id.is_none()
                })
                .count(),
            2
        );

        let consumed = EvidenceLedger::from_entries(vec![mh370_estimator::EvidenceEntry {
            identity: r600.clone(),
            disposition: EvidenceDisposition::Consumed,
        }])
        .unwrap();
        assert!(build_evidence_ledger(
            &consumed,
            &r600,
            &r1200,
            EvidenceBuildContext {
                config_sha256: &digest('5'),
                current_input_sha256: &hashes,
                upstream_config_sha256: &digest('6'),
                upstream_input_sha256: &hashes,
            },
            -3.0,
        )
        .is_err());

        let invalid_source = EvidenceLedger::from_entries(vec![mh370_estimator::EvidenceEntry {
            identity: EvidenceIdentity {
                epoch_id: "invalid identity".to_string(),
                channel: None,
                component: EvidenceComponent::Bto,
            },
            disposition: EvidenceDisposition::HeldOut,
        }])
        .unwrap();
        assert!(build_evidence_ledger(
            &invalid_source,
            &r600,
            &r1200,
            EvidenceBuildContext {
                config_sha256: &digest('5'),
                current_input_sha256: &hashes,
                upstream_config_sha256: &digest('6'),
                upstream_input_sha256: &hashes,
            },
            -3.0,
        )
        .is_err());
    }

    #[test]
    fn termination_mass_normalization_removes_roundoff_above_one() {
        let mut masses =
            BTreeMap::from([(TransitionTerminationV1::Impact, 1.000_000_000_000_000_4)]);
        normalize_mass_map(&mut masses);
        assert_eq!(masses[&TransitionTerminationV1::Impact], 1.0);
    }

    #[test]
    fn utc_parser_pins_the_exact_handoff_interval() {
        let source = parse_utc_posix_seconds(REQUIRED_SOURCE_UTC).unwrap();
        let r600 = parse_utc_posix_seconds(REQUIRED_R600_UTC).unwrap();
        let r1200 = parse_utc_posix_seconds(REQUIRED_R1200_UTC).unwrap();
        assert_eq!(r600 - source, REQUIRED_R600_ELAPSED_S);
        assert_eq!(r1200 - source, REQUIRED_R1200_ELAPSED_S);
        assert_eq!(r1200 - r600, 8.0);
        assert_eq!(
            parse_utc_posix_seconds("2014-03-08T00:19:29.000Z").unwrap(),
            r600
        );
        assert!(parse_utc_posix_seconds("2014-03-08T00:19:60Z").is_err());
    }

    #[test]
    fn selected_ephemeris_epoch_must_have_exact_utc() {
        let ephemeris = "epoch_id,time_utc,x_km\n\
m0019a,2014-03-08T00:19:29.000Z,1\n";
        require_ephemeris_utc(ephemeris, "m0019a", REQUIRED_R600_UTC).unwrap();
        assert!(require_ephemeris_utc(ephemeris, "m0019a", REQUIRED_R1200_UTC).is_err());
    }
}
