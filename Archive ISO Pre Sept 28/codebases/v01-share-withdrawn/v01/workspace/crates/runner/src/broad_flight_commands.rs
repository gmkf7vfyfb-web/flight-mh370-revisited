//! Runner orchestration for the broad, repeated-manoeuvre powered-flight model.

use std::{
    collections::BTreeMap,
    fs,
    path::{Path, PathBuf},
    time::Instant,
};

use anyhow::{bail, Context, Result};
use mh370_domain::{Hertz, Microseconds, Seconds, Vec3};
use mh370_dynamics::{
    Era5Grid, IgrfGrid, MagneticAltitudePolicy, ManeuverProcess, PoweredFlightEnvironment,
    PoweredFlightLimits, PoweredIntegration, PoweredLateralMode, RadarPrior,
};
use mh370_end_of_flight::{EngineFuelFlowShares, PoweredFuelModel, PoweredFuelState};
use mh370_estimator::{
    build_broad_filtering_handoff_v1, parse_satcom_observations, BroadAggregateEvidenceV1,
    BroadCheckpointMetadataV1, BroadConditioningSemanticsV1, BroadEvidenceComponentV1,
    BroadEvidenceDispositionV1, BroadEvidenceEntryV1, BroadEvidenceIdentityV1,
    BroadEvidenceLedgerV1, BroadEvidenceStateEffectV1, BroadFlightConfig, BroadFlightDiagnostics,
    BroadFlightModel, BroadFlightModelOptions, BroadFlightObservation, BroadFlightState,
    BroadFlightStratum, BroadFuelAnchorObservation, BroadFuelExhaustionSelectionGuide,
    BroadFuelExhaustionSelectionGuideConfig, BroadFuelExhaustionSelectionGuideOutcome,
    BroadFuelExhaustionSelectionGuidePoint, BroadFuelFlowInitializationDesign,
    BroadFuelUncertainty, BroadPendingRenewalRefreshConfig, BroadPendingRenewalRefreshKernel,
    BroadPoweredFeasibilityConfig, BroadProposalCandidateSchedule, BroadRejectionCounts,
    BroadRunMetadataV1, BroadSatcomEventMarkGuideConfig, BroadSatcomEventMarkGuideDiagnostics,
    BroadSatcomEventMarkGuideEpoch, BroadSatcomIntermediatePotentialBridge,
    BroadSatcomIntermediatePotentialConfig, BroadSatcomIntermediatePotentialPoint,
    BroadSatcomObservation, BroadStratumFuelUncertaintyOverride, BroadStratumMetadataV1,
    BroadUniformRange, BROAD_FUEL_EXHAUSTION_PERSISTENT_TWIST_FAMILY,
    BROAD_FUEL_EXHAUSTION_SELECTION_GUIDE_FAMILY, BROAD_PENDING_RENEWAL_REFRESH_FAMILY,
    BROAD_SATCOM_EVENT_MARK_GUIDE_FAMILY, BROAD_SATCOM_INTERMEDIATE_POTENTIAL_FAMILY,
};
use mh370_particle_filter::{
    logsumexp, normalize_log_weights, run_stratified_bootstrap_filter_with_post_resample_move,
    run_stratified_filter_with_global_transition_pool,
    run_stratified_filter_with_intermediate_potentials,
    run_stratified_filter_with_intermediate_potentials_and_persistent_twist,
    run_stratified_filter_with_intermediate_potentials_and_selection_guide,
    run_stratified_filter_with_root_stratified_transition_pool,
    run_stratified_filter_with_snapshot_retention_and_resampling_policy,
    run_stratified_island_filter_with_snapshot_retention_and_resampling_policy, Algorithm,
    FilterConfig, FilterResult, GlobalTransitionPoolCheckpoint, GlobalTransitionPoolFilterResult,
    GlobalTransitionPoolStep, IntermediatePotentialCheckpoint, IntermediatePotentialStep,
    IslandFilterCheckpoint, IslandRunDiagnostics, IslandTermination, PersistentTwistCheckpoint,
    PersistentTwistPhase, PersistentTwistStep, RootStratifiedCandidatePoolCheckpoint,
    RootStratifiedCandidatePoolLocation, RootStratifiedTransitionPoolFilterResult,
    RootStratifiedTransitionPoolStep, SelectionGuideDistributionDiagnostics, SelectionGuideStep,
    SnapshotRetention, StratifiedFilterPlan, StratifiedIslandFilterResult, StratifiedIslandPlan,
    StratifiedPostResampleMoveCheckpoint, StratifiedPostResampleMoveStep, StratumAllocation,
    StratumId, StratumIslandAllocation, WithinStratumResamplingPolicy,
    STRATIFIED_POST_RESAMPLE_MOVE_RNG_DOMAIN,
};
use mh370_reporting::{
    build_accident_panel_png, build_pdf, build_posterior_svg, DiagnosticPoint, ReportDocument,
    ReportPoint,
};
use mh370_satcom::SatcomModelConfig;
use rayon::ThreadPoolBuilder;
use serde::{Deserialize, Serialize};

use crate::{
    atomic_write, executable_sha256, prepare_output, sha256_bytes, sha256_file, write_json,
};

const CONFIG_SCHEMA_VERSION: u32 = 1;

#[derive(Debug, Clone, PartialEq, Deserialize)]
struct BroadInputs {
    observations: PathBuf,
    satellite_ephemeris: PathBuf,
    era5: PathBuf,
    igrf: PathBuf,
    ground_station_position_km: Vec3,
    source_epoch_id: String,
    source_time_utc: String,
    fit_through_epoch_id: String,
}

#[derive(Debug, Clone, PartialEq, Deserialize)]
struct BroadEnvironmentConfig {
    time_origin_utc: String,
    time_origin_unix_s: f64,
    magnetic_altitude_policy: MagneticAltitudePolicy,
}

#[derive(Debug, Clone, PartialEq, Deserialize)]
struct BroadFamilyConfig {
    id: String,
    use_bfo: bool,
    bfo_sd_override_hz: Option<f64>,
}

#[derive(Debug, Clone, PartialEq, Deserialize)]
struct BroadInitialModeConfig {
    name: String,
    mode: PoweredLateralMode,
    scientific_probability: f64,
}

#[derive(Debug, Clone, PartialEq, Deserialize)]
struct BroadManeuverFamilyConfig {
    name: String,
    scientific_probability: f64,
    process: ManeuverProcess,
}

/// A computational partition of the model's global log-uniform fuel-flow
/// latent. The scientific mass is derived from log interval width, so adding
/// support strata cannot silently change the declared fuel prior.
#[derive(Debug, Clone, PartialEq, Deserialize)]
struct BroadFuelFlowSupportStratumConfig {
    name: String,
    flow_scale_log_uniform: BroadUniformRange,
}

/// Compact runner-facing model declaration. The runner expands the Cartesian
/// product of initial modes and manoeuvre-rate families into immutable strata.
#[derive(Debug, Clone, PartialEq, Deserialize)]
struct BroadModelConfig {
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
    satcom: SatcomModelConfig,
    initial_modes: Vec<BroadInitialModeConfig>,
    maneuver_families: Vec<BroadManeuverFamilyConfig>,
    #[serde(default)]
    fuel_flow_initialization_design: BroadFuelFlowInitializationDesign,
    #[serde(default)]
    fuel_flow_support_strata: Vec<BroadFuelFlowSupportStratumConfig>,
}

#[derive(Debug, Clone, PartialEq, Deserialize)]
struct BroadSuiteConfig {
    schema_version: u32,
    name: String,
    seeds: Vec<u64>,
    inputs: BroadInputs,
    environment: BroadEnvironmentConfig,
    filter: FilterConfig,
    #[serde(default)]
    resampling_policy: WithinStratumResamplingPolicy,
    /// Optional exact independent-island SMC design. Every scientific stratum
    /// receives the same number and size of islands; the particle filter still
    /// pools them with scientific-prior and island-evidence weights.
    #[serde(default)]
    islands: Option<BroadIslandConfig>,
    /// Optional exact global ancestor/transition-pool schedule. This remains a
    /// distinct inference design from independent islands.
    #[serde(default)]
    global_transition_pool: Option<BroadGlobalTransitionPoolSchedule>,
    /// Optional exact transition pool with a fixed candidate count for every
    /// finite-mass root inside each scientific stratum. Observation IDs are
    /// resolved only after the SATCOM rows and fuel anchor have been composed.
    #[serde(default)]
    root_stratified_transition_pool: Option<BroadRootStratifiedTransitionPoolConfig>,
    /// Optional proposal-only guide for eligible lateral-event marks before
    /// exact SATCOM endpoints. Event clocks and the scientific prior remain
    /// unchanged; every selected mark carries its exact target/proposal ratio.
    #[serde(default)]
    satcom_event_mark_guide: Option<BroadSatcomEventMarkGuideRunConfig>,
    /// Optional exact Gibbs refresh of the selected pending renewal clocks
    /// after named physical observations that actually trigger ordinary
    /// posterior resampling.
    #[serde(default)]
    pending_renewal_refresh: Option<BroadPendingRenewalRefreshRunConfig>,
    /// Optional exact two-point SATCOM guide for long observation intervals.
    /// Presence enables the resolved defaults; this is an inference mechanism,
    /// not an additional item of scientific evidence.
    #[serde(default)]
    intermediate_satcom_bridge: Option<BroadIntermediateSatcomBridgeConfig>,
    /// Optional proposal-only guide toward the declared future fuel-exhaustion
    /// window. Its canonical SATCOM time source is independent of the fitted
    /// prefix so shortened pilot configurations retain the same future window.
    #[serde(default)]
    fuel_exhaustion_selection_guide: Option<BroadFuelExhaustionSelectionGuideRunConfig>,
    /// Optional proposal-only potential carried across physical filtering
    /// epochs, then removed exactly at the configured fit-through endpoint.
    #[serde(default)]
    fuel_exhaustion_persistent_twist: Option<BroadFuelExhaustionPersistentTwistRunConfig>,
    model: BroadModelConfig,
    fuel_anchor: BroadFuelAnchorObservation,
    families: Vec<BroadFamilyConfig>,
    #[serde(default)]
    outputs: BroadOutputConfig,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
struct BroadIslandConfig {
    islands_per_stratum: usize,
    particles_per_island: usize,
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(tag = "kind", rename_all = "snake_case")]
enum BroadGlobalTransitionPoolSchedule {
    ObservationIntervalTiers {
        tiers: Vec<BroadGlobalTransitionPoolTier>,
    },
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
struct BroadGlobalTransitionPoolTier {
    minimum_elapsed_seconds: f64,
    candidates_per_particle: usize,
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
struct BroadRootStratifiedTransitionPoolConfig {
    epochs: Vec<BroadRootStratifiedTransitionPoolEpochConfig>,
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
struct BroadRootStratifiedTransitionPoolEpochConfig {
    observation_id: String,
    candidates_per_positive_root: usize,
}

/// Human-facing SATCOM event-mark proposal schedule. Unit suffixes remain
/// explicit at the TOML boundary and are resolved into estimator domain types.
#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
struct BroadSatcomEventMarkGuideRunConfig {
    epochs: Vec<BroadSatcomEventMarkGuideEpochRunConfig>,
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
struct BroadSatcomEventMarkGuideEpochRunConfig {
    observation_id: String,
    minimum_lead_s: f64,
    maximum_lookback_s: f64,
    candidates_per_event: usize,
    defensive_prior_probability: f64,
    score_temperature: f64,
}

/// Runner-owned exact-ID schedule plus the estimator-owned stream selection.
#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
struct BroadPendingRenewalRefreshRunConfig {
    after_observation_ids: Vec<String>,
    lateral: bool,
    speed: bool,
    altitude: bool,
}

impl BroadPendingRenewalRefreshRunConfig {
    const fn resolved(&self) -> BroadPendingRenewalRefreshConfig {
        BroadPendingRenewalRefreshConfig {
            lateral: self.lateral,
            speed: self.speed,
            altitude: self.altitude,
        }
    }

    fn validate(&self) -> Result<()> {
        self.resolved()
            .validate()
            .map_err(anyhow::Error::new)
            .context("invalid pending-renewal refresh")?;
        if self.after_observation_ids.is_empty()
            || self
                .after_observation_ids
                .iter()
                .any(|id| id.trim().is_empty())
        {
            bail!("pending-renewal refresh observation IDs must be non-empty");
        }
        let mut ids = self
            .after_observation_ids
            .iter()
            .map(String::as_str)
            .collect::<Vec<_>>();
        ids.sort_unstable();
        ids.dedup();
        if ids.len() != self.after_observation_ids.len() {
            bail!("pending-renewal refresh observation IDs must be unique");
        }
        if !self.lateral || !self.speed || !self.altitude {
            bail!(
                "the first pending-renewal refresh release requires lateral, speed, and altitude"
            );
        }
        Ok(())
    }

    fn stable_descriptor(&self) -> String {
        format!(
            "{};after-observation-ids=[{}]",
            self.resolved().stable_descriptor(),
            self.after_observation_ids.join(",")
        )
    }
}

/// Human-facing bridge configuration. Unit suffixes are explicit at the TOML
/// boundary; every omitted field is resolved before it is written to any run
/// artifact.
#[derive(Debug, Clone, Copy, PartialEq, Serialize, Deserialize)]
#[serde(default)]
struct BroadIntermediateSatcomBridgeConfig {
    early_offset_s: f64,
    late_offset_s: f64,
    minimum_interval_s: f64,
    early_candidates_per_particle: usize,
    late_candidates_per_particle: usize,
    endpoint_candidates_per_particle: usize,
    potential_floor: f64,
    bto_projection_sd_us_per_remaining_hour: f64,
    bfo_projection_sd_hz_per_remaining_hour: f64,
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
struct BroadFuelExhaustionSelectionGuideRunConfig {
    #[serde(default = "default_selection_guide_potential_floor")]
    potential_floor: f64,
    canonical_full_satcom_observations: PathBuf,
    window_start_epoch_id: String,
    window_end_epoch_id: String,
    window_end_contact_offset_s: f64,
}

/// The persistent mechanism deliberately resolves the same guarded scientific
/// potential as the local selection guide. The separate TOML table selects a
/// different exact SMC law, not a different fuel or SATCOM assumption.
type BroadFuelExhaustionPersistentTwistRunConfig = BroadFuelExhaustionSelectionGuideRunConfig;

const fn default_selection_guide_potential_floor() -> f64 {
    0.02
}

impl BroadFuelExhaustionSelectionGuideRunConfig {
    const fn resolved(&self) -> BroadFuelExhaustionSelectionGuideConfig {
        BroadFuelExhaustionSelectionGuideConfig {
            potential_floor: self.potential_floor,
        }
    }
}

#[derive(Debug, Clone, Copy, PartialEq, Serialize)]
struct BroadResolvedFuelExhaustionGuideWindow {
    window_start_s: f64,
    canonical_window_end_s: f64,
    window_end_contact_offset_s: f64,
    window_end_s: f64,
}

impl Default for BroadIntermediateSatcomBridgeConfig {
    fn default() -> Self {
        let config = BroadSatcomIntermediatePotentialConfig::default();
        Self {
            early_offset_s: config.early_offset.0,
            late_offset_s: config.late_offset.0,
            minimum_interval_s: config.minimum_interval.0,
            early_candidates_per_particle: config.early_candidates_per_particle,
            late_candidates_per_particle: config.late_candidates_per_particle,
            endpoint_candidates_per_particle: 1,
            potential_floor: config.potential_floor,
            bto_projection_sd_us_per_remaining_hour: config.bto_projection_sd_per_remaining_hour.0,
            bfo_projection_sd_hz_per_remaining_hour: config.bfo_projection_sd_per_remaining_hour.0,
        }
    }
}

impl BroadIntermediateSatcomBridgeConfig {
    fn resolved(self) -> BroadSatcomIntermediatePotentialConfig {
        BroadSatcomIntermediatePotentialConfig {
            early_offset: Seconds(self.early_offset_s),
            late_offset: Seconds(self.late_offset_s),
            minimum_interval: Seconds(self.minimum_interval_s),
            early_candidates_per_particle: self.early_candidates_per_particle,
            late_candidates_per_particle: self.late_candidates_per_particle,
            potential_floor: self.potential_floor,
            bto_projection_sd_per_remaining_hour: Microseconds(
                self.bto_projection_sd_us_per_remaining_hour,
            ),
            bfo_projection_sd_per_remaining_hour: Hertz(
                self.bfo_projection_sd_hz_per_remaining_hour,
            ),
        }
    }
}

impl BroadGlobalTransitionPoolSchedule {
    fn tiers(&self) -> &[BroadGlobalTransitionPoolTier] {
        match self {
            Self::ObservationIntervalTiers { tiers } => tiers,
        }
    }

    fn validate(&self) -> Result<()> {
        let tiers = self.tiers();
        if tiers.is_empty()
            || tiers.iter().any(|tier| {
                !tier.minimum_elapsed_seconds.is_finite()
                    || tier.minimum_elapsed_seconds < 0.0
                    || tier.candidates_per_particle == 0
            })
            || tiers
                .windows(2)
                .any(|pair| pair[0].minimum_elapsed_seconds >= pair[1].minimum_elapsed_seconds)
        {
            bail!(
                "global transition-pool tiers must be non-empty, strictly ordered, finite, non-negative, and use positive candidate counts"
            );
        }
        Ok(())
    }

    fn step_for_elapsed_seconds(&self, elapsed_seconds: f64) -> GlobalTransitionPoolStep {
        self.tiers()
            .iter()
            .rev()
            .find(|tier| elapsed_seconds >= tier.minimum_elapsed_seconds)
            .map_or(GlobalTransitionPoolStep::Standard, |tier| {
                GlobalTransitionPoolStep::Pool {
                    candidates_per_particle: tier.candidates_per_particle,
                }
            })
    }

    fn stable_descriptor(&self) -> String {
        let tiers = self
            .tiers()
            .iter()
            .map(|tier| {
                format!(
                    "elapsed>={:.9}s:k{}",
                    tier.minimum_elapsed_seconds, tier.candidates_per_particle
                )
            })
            .collect::<Vec<_>>()
            .join(",");
        format!("observation-interval-tiers[{tiers}]")
    }
}

impl BroadRootStratifiedTransitionPoolConfig {
    fn validate(&self) -> Result<()> {
        if self.epochs.is_empty()
            || self.epochs.iter().any(|epoch| {
                epoch.observation_id.trim().is_empty() || epoch.candidates_per_positive_root == 0
            })
        {
            bail!(
                "root-stratified transition-pool epochs must be non-empty, name an observation, and use positive candidate counts"
            );
        }
        let mut observation_ids = self
            .epochs
            .iter()
            .map(|epoch| epoch.observation_id.as_str())
            .collect::<Vec<_>>();
        observation_ids.sort_unstable();
        observation_ids.dedup();
        if observation_ids.len() != self.epochs.len() {
            bail!("root-stratified transition-pool observation IDs must be unique");
        }
        Ok(())
    }

    fn stable_descriptor(&self) -> String {
        let epochs = self
            .epochs
            .iter()
            .map(|epoch| {
                format!(
                    "{}:l{}-per-positive-root",
                    epoch.observation_id, epoch.candidates_per_positive_root
                )
            })
            .collect::<Vec<_>>()
            .join(",");
        format!("observation-ids[{epochs}]")
    }
}

impl BroadSatcomEventMarkGuideRunConfig {
    fn resolved(&self) -> BroadSatcomEventMarkGuideConfig {
        BroadSatcomEventMarkGuideConfig {
            epochs: self
                .epochs
                .iter()
                .map(|epoch| BroadSatcomEventMarkGuideEpoch {
                    observation_id: epoch.observation_id.clone(),
                    minimum_lead: Seconds(epoch.minimum_lead_s),
                    maximum_lookback: Seconds(epoch.maximum_lookback_s),
                    candidates_per_event: epoch.candidates_per_event,
                    defensive_prior_probability: epoch.defensive_prior_probability,
                    score_temperature: epoch.score_temperature,
                })
                .collect(),
        }
    }

    fn validate(&self) -> Result<()> {
        self.resolved()
            .validate()
            .map_err(anyhow::Error::new)
            .context("invalid SATCOM event-mark guide")
    }

    fn stable_descriptor(&self) -> String {
        self.resolved().stable_descriptor()
    }
}

/// Large broad-flight pilots can exceed hundreds of megabytes per seed.  The
/// scientific run is unchanged when a diagnostic pilot omits a continuation
/// handoff or flat particle table; the manifest records only artifacts that
/// were actually emitted.  Release/continuation configurations retain both by
/// default.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Deserialize)]
struct BroadOutputConfig {
    #[serde(default = "default_true")]
    write_posterior_csv: bool,
    #[serde(default = "default_true")]
    write_posterior_handoff: bool,
}

impl Default for BroadOutputConfig {
    fn default() -> Self {
        Self {
            write_posterior_csv: true,
            write_posterior_handoff: true,
        }
    }
}

const fn default_true() -> bool {
    true
}

#[derive(Debug, Clone, Serialize)]
struct BroadSeedSummary {
    family: String,
    seed: u64,
    configured_particles: usize,
    positive_weight_particles: usize,
    effective_sample_size: f64,
    maximum_weight: f64,
    distinct_prior_roots: usize,
    prior_root_effective_sample_size: f64,
    maximum_prior_root_weight: f64,
    prior_roots_with_mass_at_least_1e_6: usize,
    prior_roots_with_mass_at_least_1e_3: usize,
    posterior_state_diversity: BroadPosteriorStateDiversity,
    nonzero_posterior_strata: usize,
    dominant_stratum: u32,
    dominant_stratum_mass: f64,
    log_evidence: f64,
    mean_latitude_deg: f64,
    mean_longitude_deg: f64,
    rejection_counts: BroadRejectionCounts,
    mean_lateral_events: f64,
    mean_speed_events: f64,
    mean_altitude_events: f64,
    mean_fuel_anchor_mass_adjustment_kg: f64,
    mean_fuel_flow_scale: f64,
    fuel_flow_scale_sd: f64,
    fuel_exhausted_by_checkpoint_mass: f64,
    mean_powered_additional_drag_required_segments: f64,
    #[serde(skip_serializing_if = "Option::is_none")]
    island_smc: Option<BroadIslandSeedSummary>,
    #[serde(skip_serializing_if = "Option::is_none")]
    global_transition_pool_smc: Option<BroadGlobalTransitionPoolSeedSummary>,
    #[serde(skip_serializing_if = "Option::is_none")]
    root_stratified_transition_pool_smc: Option<BroadRootStratifiedTransitionPoolSeedSummary>,
    #[serde(skip_serializing_if = "Option::is_none")]
    satcom_event_mark_guide: Option<BroadSatcomEventMarkGuideSeedSummary>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pending_renewal_refresh: Option<BroadPendingRenewalRefreshSeedSummary>,
    #[serde(skip_serializing_if = "Option::is_none")]
    intermediate_satcom_bridge_smc: Option<BroadIntermediatePotentialSeedSummary>,
    #[serde(skip_serializing_if = "Option::is_none")]
    fuel_exhaustion_selection_guide_smc: Option<BroadFuelExhaustionSelectionGuideSeedSummary>,
    #[serde(skip_serializing_if = "Option::is_none")]
    fuel_exhaustion_persistent_twist_smc: Option<BroadFuelExhaustionPersistentTwistSeedSummary>,
}

#[derive(Debug, Clone, Default, PartialEq, Eq, Serialize)]
struct BroadExactStateCloneMultiplicity {
    finite_log_weight_particles: usize,
    strictly_positive_normalized_weight_particles: usize,
    unique_exact_states: usize,
    maximum_exact_state_multiplicity: usize,
    finite_log_weight_particles_in_duplicate_exact_state_groups: usize,
}

#[derive(Debug, Clone, Serialize)]
struct BroadFilteringOutcomeSignatureDiversity {
    finite_log_weight_particles: usize,
    strictly_positive_normalized_weight_particles: usize,
    unique_filtering_outcome_signatures: usize,
    finite_log_weight_particles_in_duplicate_signature_groups: usize,
    posterior_mass_in_duplicate_signature_groups: f64,
    maximum_signature_multiplicity: usize,
    maximum_signature_group_posterior_mass: f64,
    signature_aggregated_effective_sample_size: f64,
}

#[derive(Debug, Clone, Serialize)]
struct BroadDominantPriorRootStateDiversity {
    prior_root_id: usize,
    posterior_mass: f64,
    filtering_outcome_signatures: BroadFilteringOutcomeSignatureDiversity,
}

#[derive(Debug, Clone, Serialize)]
struct BroadPosteriorStateDiversity {
    filtering_outcome_signature_semantics: &'static str,
    all_particles: BroadFilteringOutcomeSignatureDiversity,
    dominant_prior_root: BroadDominantPriorRootStateDiversity,
}

#[derive(Debug, Clone, Default, Serialize)]
struct BroadPendingRenewalRefreshSeedSummary {
    finite_log_weight_particles: usize,
    strictly_positive_normalized_weight_particles: usize,
    posterior_mass_with_refreshes: f64,
    posterior_weighted_mean_total_refreshes: f64,
    posterior_weighted_mean_lateral_refreshes: f64,
    posterior_weighted_mean_speed_refreshes: f64,
    posterior_weighted_mean_altitude_refreshes: f64,
    minimum_selected_stream_refreshes_across_finite_log_weight_lineages: u64,
    maximum_selected_stream_refreshes_across_finite_log_weight_lineages: u64,
    exact_state_clone_multiplicity: BroadExactStateCloneMultiplicity,
}

#[derive(Debug, Serialize)]
struct BroadPendingRenewalRefreshDiagnosticsArtifact<'a> {
    schema: &'static str,
    schema_version: u32,
    model_family: &'static str,
    refresh_family: &'static str,
    move_rng_domain: &'static str,
    family: &'a str,
    seed: u64,
    run_identity_sha256: &'a str,
    config_sha256: &'a str,
    input_sha256: &'a BTreeMap<String, String>,
    filter: &'a FilterConfig,
    resampling_policy: WithinStratumResamplingPolicy,
    plan: &'a StratifiedFilterPlan,
    config: &'a BroadPendingRenewalRefreshRunConfig,
    resolved_estimator_config: BroadPendingRenewalRefreshConfig,
    refresh_descriptor: String,
    inference_descriptor: String,
    realized_epochs: &'a [BroadRealizedPendingRenewalRefreshEpoch],
    schedule_semantics: &'static str,
    move_semantics: &'static str,
    weighting_and_evidence_semantics: &'static str,
    move_log_weight_logz_and_evidence_adjustment: f64,
    diagnostic_population_semantics: &'static str,
    exact_state_clone_semantics: &'static str,
    posterior_state_diversity: &'a BroadPosteriorStateDiversity,
    physical_filter_checkpoints: &'a [mh370_particle_filter::FilterCheckpoint],
    post_resample_move_checkpoints: &'a [StratifiedPostResampleMoveCheckpoint],
    posterior_survivor_summary: &'a BroadPendingRenewalRefreshSeedSummary,
}

#[derive(Debug, Clone, Default, Serialize)]
struct BroadSatcomEventMarkGuideStratumSummary {
    stratum: u32,
    posterior_mass: f64,
    posterior_mass_with_guided_lateral_events: f64,
    conditional_mean_guided_lateral_events: f64,
    conditional_mean_candidate_marks: f64,
    conditional_mean_cumulative_log_prior_over_proposal: f64,
}

#[derive(Debug, Clone, Default, Serialize)]
struct BroadSatcomEventMarkGuideSeedSummary {
    positive_weight_particles: usize,
    posterior_mass_with_eligible_lateral_events: f64,
    posterior_mass_with_guided_lateral_events: f64,
    posterior_weighted_mean_eligible_lateral_events: f64,
    posterior_weighted_mean_guided_lateral_events: f64,
    posterior_weighted_mean_candidate_marks: f64,
    posterior_weighted_mean_finite_candidate_scores: f64,
    posterior_weighted_mean_materialization_failures: f64,
    posterior_weighted_mean_proxy_projection_successes: f64,
    posterior_weighted_mean_proxy_projection_failures: f64,
    posterior_weighted_mean_proxy_projection_skipped_candidates: f64,
    posterior_weighted_mean_all_scores_negative_infinity_events: f64,
    #[serde(skip_serializing_if = "Option::is_none")]
    posterior_survivor_candidate_materialization_failure_fraction: Option<f64>,
    #[serde(skip_serializing_if = "Option::is_none")]
    posterior_survivor_proxy_projection_failure_fraction: Option<f64>,
    #[serde(skip_serializing_if = "Option::is_none")]
    posterior_survivor_proxy_projection_skipped_fraction: Option<f64>,
    #[serde(skip_serializing_if = "Option::is_none")]
    posterior_survivor_all_scores_negative_infinity_event_fraction: Option<f64>,
    #[serde(skip_serializing_if = "Option::is_none")]
    posterior_survivor_mean_selection_effective_sample_size_per_guided_event: Option<f64>,
    #[serde(skip_serializing_if = "Option::is_none")]
    posterior_survivor_mean_selection_entropy_nats_per_guided_event: Option<f64>,
    #[serde(skip_serializing_if = "Option::is_none")]
    minimum_observed_lead_seconds: Option<f64>,
    #[serde(skip_serializing_if = "Option::is_none")]
    maximum_observed_lead_seconds: Option<f64>,
    #[serde(skip_serializing_if = "Option::is_none")]
    minimum_selected_probability_across_positive_weight_lineages: Option<f64>,
    #[serde(skip_serializing_if = "Option::is_none")]
    maximum_selected_probability_across_positive_weight_lineages: Option<f64>,
    #[serde(skip_serializing_if = "Option::is_none")]
    minimum_event_log_prior_over_proposal_across_positive_weight_lineages: Option<f64>,
    #[serde(skip_serializing_if = "Option::is_none")]
    maximum_event_log_prior_over_proposal_across_positive_weight_lineages: Option<f64>,
    posterior_weighted_mean_sum_log_candidate_count: f64,
    posterior_weighted_mean_sum_selected_log_probability: f64,
    posterior_weighted_mean_cumulative_log_prior_over_proposal: f64,
    posterior_weighted_sd_cumulative_log_prior_over_proposal: f64,
    maximum_absolute_lineage_correction_recomposition_error: f64,
    strata: Vec<BroadSatcomEventMarkGuideStratumSummary>,
}

#[derive(Debug, Serialize)]
struct BroadSatcomEventMarkGuideDiagnosticsArtifact<'a> {
    schema: &'static str,
    schema_version: u32,
    model_family: &'static str,
    guide_family: &'static str,
    family: &'a str,
    seed: u64,
    run_identity_sha256: &'a str,
    config_sha256: &'a str,
    input_sha256: &'a BTreeMap<String, String>,
    filter: &'a FilterConfig,
    resampling_policy: WithinStratumResamplingPolicy,
    config: &'a BroadSatcomEventMarkGuideRunConfig,
    resolved_estimator_config: BroadSatcomEventMarkGuideConfig,
    guide_descriptor: String,
    realized_epochs: &'a [BroadRealizedSatcomEventMarkGuideEpoch],
    eligibility_semantics: &'static str,
    proposal_semantics: &'static str,
    proxy_semantics: &'static str,
    correction_semantics: &'static str,
    evidence_semantics: &'static str,
    root_pool_composition_semantics: &'static str,
    diagnostic_population_semantics: &'static str,
    physical_filter_checkpoints: &'a [mh370_particle_filter::FilterCheckpoint],
    posterior_survivor_summary: &'a BroadSatcomEventMarkGuideSeedSummary,
}

#[derive(Debug, Clone, Serialize)]
struct BroadIslandSeedSummary {
    configured_islands: usize,
    positive_mass_islands: usize,
    extinct_islands: usize,
    island_effective_sample_size: f64,
    maximum_island_mass: f64,
    minimum_positive_island_particle_effective_sample_size: f64,
    minimum_positive_island_root_effective_sample_size: f64,
    maximum_positive_island_conditional_particle_weight: f64,
}

#[derive(Debug, Serialize)]
struct BroadIslandDiagnosticsArtifact<'a> {
    schema: &'static str,
    schema_version: u32,
    model_family: &'static str,
    family: &'a str,
    seed: u64,
    run_identity_sha256: &'a str,
    config_sha256: &'a str,
    input_sha256: &'a BTreeMap<String, String>,
    filter: &'a FilterConfig,
    resampling_policy: WithinStratumResamplingPolicy,
    pooling_semantics: &'static str,
    plan: &'a StratifiedIslandPlan,
    islands: &'a [IslandRunDiagnostics],
    checkpoints: &'a [IslandFilterCheckpoint],
}

#[derive(Debug, Clone, Serialize)]
struct BroadGlobalTransitionPoolSeedSummary {
    pooled_epochs: usize,
    total_configured_candidates: usize,
    total_generated_candidates: usize,
    total_positive_candidates: usize,
    minimum_candidate_effective_sample_size: f64,
    maximum_candidate_weight: f64,
    minimum_candidate_root_effective_sample_size: f64,
    maximum_candidate_root_weight: f64,
    maximum_absolute_output_resampling_log_correction: f64,
}

#[derive(Debug, Serialize)]
struct BroadGlobalTransitionPoolDiagnosticsArtifact<'a> {
    schema: &'static str,
    schema_version: u32,
    model_family: &'static str,
    family: &'a str,
    seed: u64,
    run_identity_sha256: &'a str,
    config_sha256: &'a str,
    input_sha256: &'a BTreeMap<String, String>,
    filter: &'a FilterConfig,
    resampling_policy: WithinStratumResamplingPolicy,
    schedule: &'a BroadGlobalTransitionPoolSchedule,
    realized_epochs: &'a [BroadRealizedGlobalTransitionPoolEpoch],
    weighting_semantics: &'static str,
    checkpoints: &'a [GlobalTransitionPoolCheckpoint],
}

#[derive(Debug, Clone, Serialize)]
struct BroadRootStratifiedTransitionPoolSeedSummary {
    pooled_epochs: usize,
    total_input_positive_root_epoch_instances: usize,
    total_configured_candidates: usize,
    total_generated_candidates: usize,
    total_positive_candidates: usize,
    total_roots_with_positive_candidates: usize,
    minimum_positive_candidates_per_root: usize,
    maximum_positive_candidates_per_root: usize,
    minimum_within_root_candidate_effective_sample_size: f64,
    minimum_stratum_median_within_root_candidate_effective_sample_size: f64,
    maximum_within_root_candidate_weight: f64,
    roots_with_maximum_candidate_weight_at_least_half: usize,
    minimum_candidate_effective_sample_size: f64,
    maximum_candidate_weight: f64,
    minimum_candidate_root_effective_sample_size: f64,
    maximum_candidate_root_weight: f64,
    maximum_absolute_output_resampling_log_correction: f64,
    #[serde(skip_serializing_if = "Option::is_none")]
    maximum_absolute_split_log_evidence_difference: Option<f64>,
    #[serde(skip_serializing_if = "Option::is_none")]
    maximum_split_candidate_root_total_variation: Option<f64>,
}

#[derive(Debug, Serialize)]
struct BroadRootStratifiedTransitionPoolDiagnosticsArtifact<'a> {
    schema: &'static str,
    schema_version: u32,
    model_family: &'static str,
    family: &'a str,
    seed: u64,
    run_identity_sha256: &'a str,
    config_sha256: &'a str,
    input_sha256: &'a BTreeMap<String, String>,
    filter: &'a FilterConfig,
    resampling_policy: WithinStratumResamplingPolicy,
    config: &'a BroadRootStratifiedTransitionPoolConfig,
    realized_epochs: &'a [BroadRealizedRootStratifiedTransitionPoolEpoch],
    target_semantics: &'static str,
    candidate_allocation_semantics: &'static str,
    generic_checkpoint_candidates_per_particle_semantics: &'static str,
    weighting_semantics: &'static str,
    transition_pool_checkpoints: &'a [GlobalTransitionPoolCheckpoint],
    root_stratified_candidate_pool_checkpoints: &'a [RootStratifiedCandidatePoolCheckpoint],
}

#[derive(Debug, Clone, Serialize)]
struct BroadIntermediatePotentialSeedSummary {
    bridged_epochs: usize,
    guide_points: usize,
    total_configured_candidates: usize,
    total_generated_candidates: usize,
    total_positive_candidates: usize,
    minimum_candidate_effective_sample_size: f64,
    maximum_candidate_weight: f64,
    minimum_candidate_root_effective_sample_size: f64,
    maximum_candidate_root_weight: f64,
    minimum_guide_output_effective_sample_size: f64,
    minimum_guide_output_root_effective_sample_size: f64,
    minimum_endpoint_effective_sample_size: f64,
    minimum_endpoint_root_effective_sample_size: f64,
    maximum_absolute_output_resampling_log_correction: f64,
    #[serde(skip_serializing_if = "Option::is_none")]
    endpoint_pool: Option<BroadIntermediatePotentialEndpointPoolSummary>,
}

#[derive(Debug, Clone, Serialize)]
struct BroadIntermediatePotentialEndpointPoolSummary {
    pooled_epochs: usize,
    total_configured_candidates: usize,
    total_generated_candidates: usize,
    total_positive_candidates: usize,
    minimum_candidate_effective_sample_size: f64,
    maximum_candidate_weight: f64,
    minimum_candidate_root_effective_sample_size: f64,
    maximum_candidate_root_weight: f64,
    maximum_absolute_output_resampling_log_correction: f64,
}

#[derive(Debug, Serialize)]
struct BroadIntermediatePotentialDiagnosticsArtifact<'a> {
    schema: &'static str,
    schema_version: u32,
    model_family: &'static str,
    guide_family: &'static str,
    family: &'a str,
    seed: u64,
    run_identity_sha256: &'a str,
    config_sha256: &'a str,
    input_sha256: &'a BTreeMap<String, String>,
    filter: &'a FilterConfig,
    resampling_policy: WithinStratumResamplingPolicy,
    config: BroadIntermediateSatcomBridgeConfig,
    realized_epochs: &'a [BroadRealizedIntermediatePotentialEpoch],
    potential_semantics: &'static str,
    weighting_semantics: &'static str,
    checkpoints: &'a [IntermediatePotentialCheckpoint],
}

#[derive(Debug, Clone, Serialize)]
struct BroadFuelExhaustionSelectionGuideSeedSummary {
    guided_epochs: usize,
    guided_standard_epochs: usize,
    guided_bridge_epochs: usize,
    selection_distribution_evaluations: usize,
    minimum_log_guide: f64,
    maximum_log_guide: f64,
    minimum_proposal_effective_sample_size: f64,
    maximum_proposal_probability: f64,
    minimum_proposal_root_effective_sample_size: f64,
    maximum_proposal_root_probability: f64,
    maximum_absolute_log_target_over_proposal: f64,
    final_posterior: BroadFuelExhaustionPosteriorSummary,
}

#[derive(Debug, Clone, Serialize)]
struct BroadFuelExhaustionOutcomeSummary {
    outcome: BroadFuelExhaustionSelectionGuideOutcome,
    retained_slots: usize,
    posterior_mass: f64,
}

#[derive(Debug, Clone, Serialize)]
struct BroadFuelExhaustionCompatibleStratumSummary {
    stratum: u32,
    compatible_positive_weight_slots: usize,
    distinct_compatible_seed_local_roots: usize,
    compatible_physical_posterior_mass: f64,
    #[serde(skip_serializing_if = "Option::is_none")]
    compatible_physical_root_effective_sample_size: Option<f64>,
    #[serde(skip_serializing_if = "Option::is_none")]
    maximum_compatible_physical_root_weight: Option<f64>,
}

#[derive(Debug, Clone, Serialize)]
struct BroadFuelExhaustionPosteriorSummary {
    retained_slots: usize,
    positive_weight_slots: usize,
    zero_weight_placeholder_slots: usize,
    outcomes: Vec<BroadFuelExhaustionOutcomeSummary>,
    compatible_retained_slot_fraction: f64,
    compatible_positive_weight_slots: usize,
    compatible_positive_weight_slot_fraction: f64,
    distinct_compatible_seed_local_roots: usize,
    compatible_posterior_mass: f64,
    #[serde(skip_serializing_if = "Option::is_none")]
    compatible_root_effective_sample_size: Option<f64>,
    #[serde(skip_serializing_if = "Option::is_none")]
    maximum_compatible_root_weight: Option<f64>,
    #[serde(skip_serializing_if = "Option::is_none")]
    compatible_projected_exhaustion_time_min_s: Option<f64>,
    #[serde(skip_serializing_if = "Option::is_none")]
    compatible_projected_exhaustion_time_mean_s: Option<f64>,
    #[serde(skip_serializing_if = "Option::is_none")]
    compatible_projected_exhaustion_time_max_s: Option<f64>,
    compatible_strata: Vec<BroadFuelExhaustionCompatibleStratumSummary>,
}

#[derive(Debug)]
struct BroadFuelExhaustionPosteriorPopulation {
    seed: u64,
    summary: BroadFuelExhaustionPosteriorSummary,
    compatible_root_masses: Vec<f64>,
    compatible_root_masses_by_stratum: BTreeMap<u32, Vec<f64>>,
}

#[derive(Debug, Clone, Serialize)]
struct BroadFuelExhaustionPersistentTwistSeedSummary {
    active_epochs: usize,
    continue_epochs: usize,
    twisted_standard_epochs: usize,
    twisted_bridge_epochs: usize,
    minimum_twisted_effective_sample_size: f64,
    minimum_implied_physical_effective_sample_size: f64,
    minimum_twisted_root_effective_sample_size: f64,
    minimum_implied_physical_root_effective_sample_size: f64,
    maximum_twisted_root_weight: f64,
    maximum_implied_physical_root_weight: f64,
    #[serde(skip_serializing_if = "Option::is_none")]
    final_global_untwist_log_evidence_correction: Option<f64>,
    final_output_is_ordinary_physical_filter: bool,
    final_posterior: BroadFuelExhaustionPosteriorSummary,
}

#[derive(Debug, Clone, Serialize)]
struct BroadPersistentTwistEvidenceRecomposition {
    initial_log_evidence: f64,
    inactive_physical_log_evidence_increment_sum: f64,
    active_twisted_target_log_evidence_increment_sum: f64,
    final_global_untwist_log_evidence_correction: f64,
    recomposed_final_physical_log_evidence: f64,
    reported_final_physical_log_evidence: f64,
    maximum_absolute_wrapper_vs_filter_checkpoint_increment_difference: f64,
}

#[derive(Debug, Clone)]
struct BroadPersistentTwistExecutionDiagnostics {
    checkpoints: Vec<PersistentTwistCheckpoint>,
    twisted_standard_checkpoints: Vec<GlobalTransitionPoolCheckpoint>,
    intermediate_potential_checkpoints: Vec<IntermediatePotentialCheckpoint>,
    twisted_filtering_observation_indices: Vec<usize>,
}

#[derive(Debug, Serialize)]
struct BroadFuelExhaustionPersistentTwistDiagnosticsArtifact<'a> {
    schema: &'static str,
    schema_version: u32,
    model_family: &'static str,
    twist_family: &'static str,
    family: &'a str,
    seed: u64,
    run_identity_sha256: &'a str,
    config_sha256: &'a str,
    input_sha256: &'a BTreeMap<String, String>,
    filter: &'a FilterConfig,
    resampling_policy: WithinStratumResamplingPolicy,
    config: &'a BroadFuelExhaustionPersistentTwistRunConfig,
    resolved_estimator_config: BroadFuelExhaustionSelectionGuideConfig,
    twist_descriptor: String,
    resolved_window: BroadResolvedFuelExhaustionGuideWindow,
    realized_epochs: &'a [BroadRealizedFuelExhaustionPersistentTwistEpoch],
    proposal_semantics: &'static str,
    evidence_semantics: &'static str,
    finalization_semantics: &'static str,
    terminal_semantics: &'static str,
    canonical_source_semantics: &'static str,
    wrapper_checkpoints: &'a [PersistentTwistCheckpoint],
    twisted_standard_checkpoints: &'a [GlobalTransitionPoolCheckpoint],
    intermediate_potential_checkpoints: &'a [IntermediatePotentialCheckpoint],
    nested_checkpoint_semantics: &'static str,
    twisted_filtering_observation_indices: &'a [usize],
    evidence_recomposition: &'a BroadPersistentTwistEvidenceRecomposition,
    final_posterior: &'a BroadFuelExhaustionPosteriorSummary,
}

#[derive(Debug)]
struct BroadFuelExhaustionSelectionCheckpoints {
    guided_standard: Vec<GlobalTransitionPoolCheckpoint>,
    intermediate_potential: Vec<IntermediatePotentialCheckpoint>,
}

#[derive(Debug, Serialize)]
struct BroadFuelExhaustionSelectionGuideDiagnosticsArtifact<'a> {
    schema: &'static str,
    schema_version: u32,
    model_family: &'static str,
    guide_family: &'static str,
    family: &'a str,
    seed: u64,
    run_identity_sha256: &'a str,
    config_sha256: &'a str,
    input_sha256: &'a BTreeMap<String, String>,
    filter: &'a FilterConfig,
    resampling_policy: WithinStratumResamplingPolicy,
    config: &'a BroadFuelExhaustionSelectionGuideRunConfig,
    resolved_estimator_config: BroadFuelExhaustionSelectionGuideConfig,
    guide_descriptor: String,
    resolved_window: BroadResolvedFuelExhaustionGuideWindow,
    realized_epochs: &'a [BroadRealizedFuelExhaustionSelectionGuideEpoch],
    proposal_semantics: &'static str,
    evidence_semantics: &'static str,
    canonical_source_semantics: &'static str,
    guided_standard_checkpoints: &'a [GlobalTransitionPoolCheckpoint],
    intermediate_potential_checkpoints: &'a [IntermediatePotentialCheckpoint],
    final_posterior: &'a BroadFuelExhaustionPosteriorSummary,
}

#[derive(Debug, Clone, Copy)]
struct BroadFuelExhaustionSelectionGuideReportContext<'a> {
    posterior: Option<&'a BroadFuelExhaustionPosteriorSummary>,
    window: Option<BroadResolvedFuelExhaustionGuideWindow>,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize)]
#[serde(rename_all = "snake_case")]
enum BroadIndependentSeedPoolingSemantics {
    EvidenceWeightedIndependentPosteriorMixture,
}

#[derive(Debug, Clone, PartialEq, Serialize)]
struct BroadSeedEvidenceWeight {
    seed: u64,
    log_evidence: f64,
    normalized_evidence_weight: f64,
}

#[derive(Debug, Clone, PartialEq, Serialize)]
struct BroadIndependentSeedPoolSummary {
    pooling_semantics: BroadIndependentSeedPoolingSemantics,
    seed_evidence_weights: Vec<BroadSeedEvidenceWeight>,
    evidence_weight_effective_sample_size: f64,
    maximum_seed_evidence_weight: f64,
    pooled_particle_effective_sample_size: f64,
    seed_namespaced_root_effective_sample_size: f64,
    maximum_seed_namespaced_root_weight: f64,
}

#[derive(Debug)]
struct BroadSeedPosteriorPopulation {
    seed: u64,
    log_evidence: f64,
    points: Vec<ReportPoint>,
    root_masses: Vec<f64>,
}

#[derive(Debug, Clone, Serialize)]
struct BroadFamilySummary {
    id: String,
    use_bfo: bool,
    bfo_sd_override_hz: Option<f64>,
    realized_proposal_epochs: Vec<BroadRealizedProposalEpoch>,
    #[serde(skip_serializing_if = "Option::is_none")]
    realized_global_transition_pool_epochs: Option<Vec<BroadRealizedGlobalTransitionPoolEpoch>>,
    #[serde(skip_serializing_if = "Option::is_none")]
    realized_root_stratified_transition_pool_epochs:
        Option<Vec<BroadRealizedRootStratifiedTransitionPoolEpoch>>,
    #[serde(skip_serializing_if = "Option::is_none")]
    realized_satcom_event_mark_guide_epochs: Option<Vec<BroadRealizedSatcomEventMarkGuideEpoch>>,
    #[serde(skip_serializing_if = "Option::is_none")]
    realized_pending_renewal_refresh_epochs: Option<Vec<BroadRealizedPendingRenewalRefreshEpoch>>,
    #[serde(skip_serializing_if = "Option::is_none")]
    realized_intermediate_satcom_bridge_epochs:
        Option<Vec<BroadRealizedIntermediatePotentialEpoch>>,
    #[serde(skip_serializing_if = "Option::is_none")]
    realized_fuel_exhaustion_selection_guide_epochs:
        Option<Vec<BroadRealizedFuelExhaustionSelectionGuideEpoch>>,
    #[serde(skip_serializing_if = "Option::is_none")]
    fuel_exhaustion_selection_guide_posterior: Option<BroadFuelExhaustionPosteriorSummary>,
    #[serde(skip_serializing_if = "Option::is_none")]
    realized_fuel_exhaustion_persistent_twist_epochs:
        Option<Vec<BroadRealizedFuelExhaustionPersistentTwistEpoch>>,
    #[serde(skip_serializing_if = "Option::is_none")]
    fuel_exhaustion_persistent_twist_posterior: Option<BroadFuelExhaustionPosteriorSummary>,
    #[serde(skip_serializing_if = "Option::is_none")]
    independent_seed_pooling: Option<BroadIndependentSeedPoolSummary>,
    seeds: Vec<BroadSeedSummary>,
}

#[derive(Debug, Clone, PartialEq, Serialize)]
struct BroadRealizedProposalEpoch {
    observation_id: String,
    observation_kind: &'static str,
    elapsed_seconds: f64,
    proposal_candidates: usize,
}

#[derive(Debug, Clone, PartialEq, Serialize)]
struct BroadRealizedGlobalTransitionPoolEpoch {
    observation_index: usize,
    observation_id: String,
    observation_kind: &'static str,
    observation_time_s: f64,
    elapsed_seconds: f64,
    step: GlobalTransitionPoolStep,
}

#[derive(Debug, Clone, PartialEq, Serialize)]
struct BroadRealizedRootStratifiedTransitionPoolEpoch {
    observation_index: usize,
    observation_id: String,
    observation_kind: &'static str,
    observation_time_s: f64,
    step: RootStratifiedTransitionPoolStep,
}

#[derive(Debug, Clone, PartialEq, Serialize)]
struct BroadRealizedSatcomEventMarkGuideEpoch {
    observation_index: usize,
    observation_id: String,
    observation_kind: &'static str,
    transition_start_s: f64,
    observation_time_s: f64,
    eligible_event_time_minimum_s: f64,
    eligible_event_time_maximum_s: f64,
    minimum_lead_s: f64,
    maximum_lookback_s: f64,
    candidates_per_event: usize,
    defensive_prior_probability: f64,
    score_temperature: f64,
    use_bto: bool,
    use_bfo: bool,
}

#[derive(Debug, Clone, PartialEq, Serialize)]
struct BroadRealizedPendingRenewalRefreshEpoch {
    observation_index: usize,
    observation_id: String,
    observation_kind: &'static str,
    observation_time_s: f64,
    step: StratifiedPostResampleMoveStep,
}

#[derive(Debug, Clone, PartialEq, Serialize)]
struct BroadRealizedIntermediatePotentialEpoch {
    observation_index: usize,
    observation_id: String,
    observation_kind: &'static str,
    observation_time_s: f64,
    elapsed_seconds: f64,
    step: IntermediatePotentialStep<BroadSatcomIntermediatePotentialPoint>,
}

#[derive(Debug, Clone, PartialEq, Serialize)]
struct BroadRealizedFuelExhaustionSelectionGuideEpoch {
    observation_index: usize,
    observation_id: String,
    observation_kind: &'static str,
    observation_time_s: f64,
    after_fuel_anchor: bool,
    step: SelectionGuideStep<BroadFuelExhaustionSelectionGuidePoint>,
}

#[derive(Debug, Clone, PartialEq, Serialize)]
struct BroadRealizedFuelExhaustionPersistentTwistEpoch {
    observation_index: usize,
    observation_id: String,
    observation_kind: &'static str,
    observation_time_s: f64,
    after_fuel_anchor: bool,
    step: PersistentTwistStep<BroadFuelExhaustionSelectionGuidePoint>,
}

#[derive(Debug, Clone, Serialize)]
struct BroadSuiteSummary {
    schema_version: u32,
    name: String,
    status: String,
    model_family: String,
    fuel_flow_initialization_design: BroadFuelFlowInitializationDesign,
    baseline_proposal_candidates: usize,
    proposal_candidate_schedule: BroadProposalCandidateSchedule,
    resampling_policy: WithinStratumResamplingPolicy,
    #[serde(skip_serializing_if = "Option::is_none")]
    island_plan: Option<StratifiedIslandPlan>,
    #[serde(skip_serializing_if = "Option::is_none")]
    global_transition_pool_schedule: Option<BroadGlobalTransitionPoolSchedule>,
    #[serde(skip_serializing_if = "Option::is_none")]
    root_stratified_transition_pool: Option<BroadRootStratifiedTransitionPoolConfig>,
    #[serde(skip_serializing_if = "Option::is_none")]
    satcom_event_mark_guide: Option<BroadSatcomEventMarkGuideRunConfig>,
    #[serde(skip_serializing_if = "Option::is_none")]
    satcom_event_mark_guide_descriptor: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pending_renewal_refresh: Option<BroadPendingRenewalRefreshRunConfig>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pending_renewal_refresh_descriptor: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    intermediate_satcom_bridge: Option<BroadIntermediateSatcomBridgeConfig>,
    #[serde(skip_serializing_if = "Option::is_none")]
    fuel_exhaustion_selection_guide: Option<BroadFuelExhaustionSelectionGuideRunConfig>,
    #[serde(skip_serializing_if = "Option::is_none")]
    fuel_exhaustion_persistent_twist: Option<BroadFuelExhaustionPersistentTwistRunConfig>,
    #[serde(skip_serializing_if = "Option::is_none")]
    fuel_exhaustion_persistent_twist_descriptor: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    resolved_fuel_exhaustion_guide_window: Option<BroadResolvedFuelExhaustionGuideWindow>,
    families: Vec<BroadFamilySummary>,
    limitations: Vec<String>,
}

#[derive(Debug, Clone, Serialize)]
struct BroadRunManifest {
    schema_version: u32,
    command: &'static str,
    status: String,
    fuel_flow_initialization_design: BroadFuelFlowInitializationDesign,
    baseline_proposal_candidates: usize,
    proposal_candidate_schedule: BroadProposalCandidateSchedule,
    #[serde(skip_serializing_if = "Option::is_none")]
    island_plan: Option<StratifiedIslandPlan>,
    #[serde(skip_serializing_if = "Option::is_none")]
    global_transition_pool_schedule: Option<BroadGlobalTransitionPoolSchedule>,
    #[serde(skip_serializing_if = "Option::is_none")]
    realized_global_transition_pool_epochs_by_family:
        Option<BTreeMap<String, Vec<BroadRealizedGlobalTransitionPoolEpoch>>>,
    #[serde(skip_serializing_if = "Option::is_none")]
    root_stratified_transition_pool: Option<BroadRootStratifiedTransitionPoolConfig>,
    #[serde(skip_serializing_if = "Option::is_none")]
    realized_root_stratified_transition_pool_epochs_by_family:
        Option<BTreeMap<String, Vec<BroadRealizedRootStratifiedTransitionPoolEpoch>>>,
    #[serde(skip_serializing_if = "Option::is_none")]
    satcom_event_mark_guide: Option<BroadSatcomEventMarkGuideRunConfig>,
    #[serde(skip_serializing_if = "Option::is_none")]
    satcom_event_mark_guide_descriptor: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    realized_satcom_event_mark_guide_epochs_by_family:
        Option<BTreeMap<String, Vec<BroadRealizedSatcomEventMarkGuideEpoch>>>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pending_renewal_refresh: Option<BroadPendingRenewalRefreshRunConfig>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pending_renewal_refresh_descriptor: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    realized_pending_renewal_refresh_epochs_by_family:
        Option<BTreeMap<String, Vec<BroadRealizedPendingRenewalRefreshEpoch>>>,
    #[serde(skip_serializing_if = "Option::is_none")]
    intermediate_satcom_bridge: Option<BroadIntermediateSatcomBridgeConfig>,
    #[serde(skip_serializing_if = "Option::is_none")]
    fuel_exhaustion_selection_guide: Option<BroadFuelExhaustionSelectionGuideRunConfig>,
    #[serde(skip_serializing_if = "Option::is_none")]
    fuel_exhaustion_persistent_twist: Option<BroadFuelExhaustionPersistentTwistRunConfig>,
    #[serde(skip_serializing_if = "Option::is_none")]
    fuel_exhaustion_persistent_twist_descriptor: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    resolved_fuel_exhaustion_guide_window: Option<BroadResolvedFuelExhaustionGuideWindow>,
    #[serde(skip_serializing_if = "Option::is_none")]
    realized_intermediate_satcom_bridge_epochs_by_family:
        Option<BTreeMap<String, Vec<BroadRealizedIntermediatePotentialEpoch>>>,
    #[serde(skip_serializing_if = "Option::is_none")]
    realized_fuel_exhaustion_selection_guide_epochs_by_family:
        Option<BTreeMap<String, Vec<BroadRealizedFuelExhaustionSelectionGuideEpoch>>>,
    #[serde(skip_serializing_if = "Option::is_none")]
    realized_fuel_exhaustion_persistent_twist_epochs_by_family:
        Option<BTreeMap<String, Vec<BroadRealizedFuelExhaustionPersistentTwistEpoch>>>,
    #[serde(skip_serializing_if = "Option::is_none")]
    independent_seed_pooling_by_family: Option<BTreeMap<String, BroadIndependentSeedPoolSummary>>,
    realized_proposal_epochs_by_family: BTreeMap<String, Vec<BroadRealizedProposalEpoch>>,
    executable_sha256: String,
    config_path: String,
    config_sha256: String,
    input_sha256: BTreeMap<String, String>,
    elapsed_seconds: f64,
    threads: usize,
    outputs: BTreeMap<String, String>,
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

fn validate_suite(config: &BroadSuiteConfig) -> Result<()> {
    if config.schema_version != CONFIG_SCHEMA_VERSION {
        bail!("unsupported broad-flight configuration schema");
    }
    if config.name.trim().is_empty()
        || config.seeds.is_empty()
        || config.inputs.fit_through_epoch_id.trim().is_empty()
        || config.inputs.source_epoch_id.trim().is_empty()
        || config.inputs.source_time_utc.trim().is_empty()
        || config.environment.time_origin_utc.trim().is_empty()
        || config.families.is_empty()
        || !config.environment.time_origin_unix_s.is_finite()
    {
        bail!("broad-flight configuration metadata is incomplete");
    }
    let mut seeds = config.seeds.clone();
    seeds.sort_unstable();
    seeds.dedup();
    if seeds.len() != config.seeds.len() {
        bail!("broad-flight seeds must be unique");
    }
    let mut family_ids = config
        .families
        .iter()
        .map(|family| family.id.as_str())
        .collect::<Vec<_>>();
    family_ids.sort_unstable();
    family_ids.dedup();
    if family_ids.len() != config.families.len() || family_ids.iter().any(|id| id.trim().is_empty())
    {
        bail!("broad-flight family identifiers must be unique and non-empty");
    }
    config
        .filter
        .validate()
        .map_err(anyhow::Error::msg)
        .context("invalid broad filter")?;
    config
        .resampling_policy
        .validate()
        .map_err(anyhow::Error::msg)
        .context("invalid broad resampling policy")?;
    let alternative_inference_designs = usize::from(config.islands.is_some())
        + usize::from(config.global_transition_pool.is_some())
        + usize::from(config.root_stratified_transition_pool.is_some())
        + usize::from(config.intermediate_satcom_bridge.is_some());
    if alternative_inference_designs > 1 {
        bail!(
            "island SMC, global transition-pool SMC, root-stratified transition-pool SMC, and intermediate SATCOM bridging are mutually exclusive"
        );
    }
    if let Some(schedule) = &config.global_transition_pool {
        schedule.validate()?;
        if config.model.proposal_candidates != 1
            || config.model.proposal_candidate_schedule != BroadProposalCandidateSchedule::Constant
        {
            bail!("global transition-pool SMC requires constant local proposal_candidates = 1");
        }
    }
    if let Some(schedule) = &config.root_stratified_transition_pool {
        schedule.validate()?;
        if config.filter.algorithm != Algorithm::Bootstrap {
            bail!("root-stratified transition-pool SMC requires the bootstrap filter algorithm");
        }
        if config.model.proposal_candidates != 1
            || config.model.proposal_candidate_schedule != BroadProposalCandidateSchedule::Constant
        {
            bail!(
                "root-stratified transition-pool SMC requires constant local proposal_candidates = 1"
            );
        }
        if config.fuel_exhaustion_selection_guide.is_some()
            || config.fuel_exhaustion_persistent_twist.is_some()
        {
            bail!(
                "root-stratified transition-pool SMC cannot be combined with a fuel guide or persistent twist"
            );
        }
    }
    if let Some(guide) = &config.satcom_event_mark_guide {
        guide.validate()?;
        if config.filter.algorithm != Algorithm::Bootstrap {
            bail!("SATCOM event-mark guidance requires the bootstrap filter algorithm");
        }
        if config.model.proposal_candidates != 1
            || config.model.proposal_candidate_schedule != BroadProposalCandidateSchedule::Constant
        {
            bail!("SATCOM event-mark guidance requires constant local proposal_candidates = 1");
        }
        if config.islands.is_some()
            || config.global_transition_pool.is_some()
            || config.intermediate_satcom_bridge.is_some()
            || config.fuel_exhaustion_selection_guide.is_some()
            || config.fuel_exhaustion_persistent_twist.is_some()
        {
            bail!(
                "SATCOM event-mark guidance may be combined only with ordinary filtering or the root-stratified transition pool"
            );
        }
    }
    if let Some(refresh) = &config.pending_renewal_refresh {
        refresh.validate()?;
        for family in &config.model.maneuver_families {
            for (stream, selected, clock) in [
                ("lateral", refresh.lateral, family.process.lateral_clock),
                ("speed", refresh.speed, family.process.speed_clock),
                ("altitude", refresh.altitude, family.process.altitude_clock),
            ] {
                if !selected {
                    continue;
                }
                let clock = clock.with_context(|| {
                    format!(
                        "pending-renewal refresh selects the disabled {stream} stream in maneuver family {}",
                        family.name
                    )
                })?;
                if clock.gamma_shape != 1.0 {
                    bail!(
                        "pending-renewal refresh requires gamma_shape = 1 for the selected {stream} stream in maneuver family {}",
                        family.name
                    );
                }
            }
        }
        if config.filter.algorithm != Algorithm::Bootstrap {
            bail!("pending-renewal refresh requires the bootstrap filter algorithm");
        }
        if config.model.proposal_candidates != 1
            || config.model.proposal_candidate_schedule != BroadProposalCandidateSchedule::Constant
        {
            bail!("pending-renewal refresh requires constant local proposal_candidates = 1");
        }
        if config.islands.is_some()
            || config.global_transition_pool.is_some()
            || config.root_stratified_transition_pool.is_some()
            || config.intermediate_satcom_bridge.is_some()
            || config.fuel_exhaustion_selection_guide.is_some()
            || config.fuel_exhaustion_persistent_twist.is_some()
            || config.satcom_event_mark_guide.is_some()
        {
            bail!(
                "pending-renewal refresh is a refresh-only pilot and requires the ordinary stratified path without islands, transition pools, bridges, fuel guides, persistent twists, or SATCOM event-mark guidance"
            );
        }
    }
    if let Some(bridge) = config.intermediate_satcom_bridge {
        bridge
            .resolved()
            .validate()
            .map_err(anyhow::Error::new)
            .context("invalid intermediate SATCOM bridge")?;
        if bridge.endpoint_candidates_per_particle == 0 {
            bail!("intermediate SATCOM endpoint candidates per particle must be positive");
        }
        if config.filter.algorithm != Algorithm::Bootstrap {
            bail!("intermediate SATCOM bridging requires the bootstrap filter algorithm");
        }
        if config.model.proposal_candidates != 1
            || config.model.proposal_candidate_schedule != BroadProposalCandidateSchedule::Constant
        {
            bail!("intermediate SATCOM bridging requires constant local proposal_candidates = 1");
        }
    }
    if config.fuel_exhaustion_selection_guide.is_some()
        && config.fuel_exhaustion_persistent_twist.is_some()
    {
        bail!(
            "local fuel-exhaustion selection guidance and the persistent fuel twist are mutually exclusive"
        );
    }
    if let Some(guide) = &config.fuel_exhaustion_selection_guide {
        validate_fuel_exhaustion_guide_source_config(guide, "selection-guide")?;
        if config.islands.is_some()
            || config.global_transition_pool.is_some()
            || config.root_stratified_transition_pool.is_some()
        {
            bail!(
                "fuel-exhaustion selection guidance cannot be combined with islands or a separate global transition pool"
            );
        }
        if config.filter.algorithm != Algorithm::Bootstrap {
            bail!("fuel-exhaustion selection guidance requires the bootstrap filter algorithm");
        }
        if config.model.proposal_candidates != 1
            || config.model.proposal_candidate_schedule != BroadProposalCandidateSchedule::Constant
        {
            bail!(
                "fuel-exhaustion selection guidance requires constant local proposal_candidates = 1"
            );
        }
    }
    if let Some(twist) = &config.fuel_exhaustion_persistent_twist {
        validate_fuel_exhaustion_guide_source_config(twist, "persistent-twist")?;
        if config.islands.is_some()
            || config.global_transition_pool.is_some()
            || config.root_stratified_transition_pool.is_some()
        {
            bail!(
                "fuel-exhaustion persistent twisting cannot be combined with islands or a separate global transition pool"
            );
        }
        let active = twist.potential_floor.to_bits() != 1.0_f64.to_bits();
        if active && config.filter.algorithm != Algorithm::Bootstrap {
            bail!("active fuel-exhaustion persistent twisting requires the bootstrap filter algorithm");
        }
        if active
            && (config.model.proposal_candidates != 1
                || config.model.proposal_candidate_schedule
                    != BroadProposalCandidateSchedule::Constant)
        {
            bail!(
                "active fuel-exhaustion persistent twisting requires constant local proposal_candidates = 1"
            );
        }
    }
    let _ = expand_model_and_plan(config)?;
    Ok(())
}

fn validate_fuel_exhaustion_guide_source_config(
    guide: &BroadFuelExhaustionSelectionGuideRunConfig,
    mechanism: &str,
) -> Result<()> {
    if !guide.potential_floor.is_finite()
        || !(0.0..=1.0).contains(&guide.potential_floor)
        || guide.potential_floor == 0.0
        || guide
            .canonical_full_satcom_observations
            .as_os_str()
            .is_empty()
        || guide.window_start_epoch_id != "m0011"
        || guide.window_end_epoch_id != "m0019a"
        || !guide.window_end_contact_offset_s.is_finite()
        || (guide.window_end_contact_offset_s - 0.416).abs() > 1.0e-12
    {
        bail!("invalid v1 fuel-exhaustion {mechanism} configuration");
    }
    Ok(())
}

fn normalized_probability_sum<'a>(values: impl Iterator<Item = &'a f64>) -> bool {
    let sum = values.copied().sum::<f64>();
    sum.is_finite() && (sum - 1.0).abs() <= 1.0e-10
}

fn expand_model_and_plan(
    suite: &BroadSuiteConfig,
) -> Result<(
    BroadFlightConfig,
    StratifiedFilterPlan,
    Vec<BroadStratumFuelUncertaintyOverride>,
)> {
    if suite.model.initial_modes.is_empty()
        || suite.model.maneuver_families.is_empty()
        || !normalized_probability_sum(
            suite
                .model
                .initial_modes
                .iter()
                .map(|entry| &entry.scientific_probability),
        )
        || !normalized_probability_sum(
            suite
                .model
                .maneuver_families
                .iter()
                .map(|entry| &entry.scientific_probability),
        )
        || suite.model.initial_modes.iter().any(|entry| {
            entry.name.trim().is_empty()
                || !entry.scientific_probability.is_finite()
                || entry.scientific_probability <= 0.0
        })
        || suite.model.maneuver_families.iter().any(|entry| {
            entry.name.trim().is_empty()
                || !entry.scientific_probability.is_finite()
                || entry.scientific_probability <= 0.0
        })
    {
        bail!("broad mode and manoeuvre-family probabilities must be positive and normalized");
    }
    if suite.model.fuel_flow_initialization_design
        == BroadFuelFlowInitializationDesign::LogSpaceLatinHypercube
        && !suite.model.fuel_flow_support_strata.is_empty()
    {
        bail!(
            "log-space Latin-hypercube fuel initialization cannot be combined with fuel-flow support strata"
        );
    }
    let fuel_support = validated_fuel_support_strata(&suite.model)?;
    let stratum_count = suite
        .model
        .initial_modes
        .len()
        .checked_mul(suite.model.maneuver_families.len())
        .and_then(|count| count.checked_mul(fuel_support.len()))
        .context("broad stratum count overflowed")?;
    if stratum_count > u32::MAX as usize || suite.filter.particles < stratum_count {
        bail!("broad run must allocate at least one particle per representational stratum");
    }
    let quotient = suite.filter.particles / stratum_count;
    let remainder = suite.filter.particles % stratum_count;
    let mut strata = Vec::with_capacity(stratum_count);
    let mut allocations = Vec::with_capacity(stratum_count);
    let mut fuel_overrides = Vec::with_capacity(stratum_count);
    let mut index = 0usize;
    for maneuver in &suite.model.maneuver_families {
        for fuel in &fuel_support {
            for mode in &suite.model.initial_modes {
                let id = StratumId(u32::try_from(index).context("broad stratum id overflowed")?);
                let particles = quotient + usize::from(index < remainder);
                let latin_hypercube = suite.model.fuel_flow_initialization_design
                    == BroadFuelFlowInitializationDesign::LogSpaceLatinHypercube;
                let probability = maneuver.scientific_probability
                    * mode.scientific_probability
                    * if latin_hypercube {
                        1.0
                    } else {
                        fuel.scientific_probability
                    };
                strata.push(BroadFlightStratum {
                    id,
                    name: if latin_hypercube {
                        format!("{}--{}", maneuver.name, mode.name)
                    } else {
                        format!("{}--{}--{}", maneuver.name, fuel.name, mode.name)
                    },
                    initial_lateral_mode: mode.mode,
                    maneuver_process: maneuver.process,
                });
                allocations.push(StratumAllocation {
                    id,
                    particles,
                    log_prior_probability: probability.ln(),
                });
                if !latin_hypercube {
                    fuel_overrides.push(BroadStratumFuelUncertaintyOverride {
                        stratum: id,
                        fuel_uncertainty: BroadFuelUncertainty {
                            total_quantity_offset_kg: suite
                                .model
                                .fuel_uncertainty
                                .total_quantity_offset_kg,
                            flow_scale_log_uniform: fuel.flow_scale_log_uniform,
                        },
                    });
                }
                index += 1;
            }
        }
    }
    let model = BroadFlightConfig {
        radar_prior: suite.model.radar_prior,
        initial_vertical_speed_ft_min: suite.model.initial_vertical_speed_ft_min,
        source_fuel: suite.model.source_fuel,
        fuel_uncertainty: suite.model.fuel_uncertainty,
        fuel_model: suite.model.fuel_model,
        fuel_flow_shares: suite.model.fuel_flow_shares,
        powered_feasibility: suite.model.powered_feasibility,
        limits: suite.model.limits,
        integration: suite.model.integration,
        proposal_candidates: suite.model.proposal_candidates,
        satcom: suite.model.satcom,
        strata,
    };
    model.validate().context("invalid expanded broad model")?;
    suite
        .model
        .proposal_candidate_schedule
        .validate_with_baseline_candidates(model.proposal_candidates)
        .context("invalid broad proposal-candidate schedule")?;
    let plan = StratifiedFilterPlan {
        strata: allocations,
    };
    plan.validate(suite.filter.particles)
        .map_err(anyhow::Error::msg)
        .context("invalid expanded broad stratification plan")?;
    let _ = build_island_plan(suite, &plan)?;
    Ok((model, plan, fuel_overrides))
}

fn build_island_plan(
    suite: &BroadSuiteConfig,
    scientific_plan: &StratifiedFilterPlan,
) -> Result<Option<StratifiedIslandPlan>> {
    let Some(config) = suite.islands else {
        return Ok(None);
    };
    if suite.model.fuel_flow_initialization_design
        != BroadFuelFlowInitializationDesign::IndependentLogUniform
    {
        bail!(
            "island SMC requires independent_log_uniform fuel initialization; Latin-hypercube cells repeat within every island"
        );
    }
    let particles_per_scientific_stratum = config
        .islands_per_stratum
        .checked_mul(config.particles_per_island)
        .context("island particle allocation overflowed")?;
    let configured_particles = scientific_plan
        .strata
        .len()
        .checked_mul(particles_per_scientific_stratum)
        .context("island particle allocation overflowed")?;
    if configured_particles != suite.filter.particles {
        bail!(
            "island allocation requires {configured_particles} particles, but filter.particles is {}",
            suite.filter.particles
        );
    }
    let plan = StratifiedIslandPlan {
        strata: scientific_plan
            .strata
            .iter()
            .map(|stratum| StratumIslandAllocation {
                id: stratum.id,
                islands: config.islands_per_stratum,
                particles_per_island: config.particles_per_island,
                log_prior_probability: stratum.log_prior_probability,
            })
            .collect(),
    };
    plan.validate(suite.filter.particles)
        .map_err(anyhow::Error::msg)
        .context("invalid broad island plan")?;
    Ok(Some(plan))
}

#[derive(Debug, Clone)]
struct ValidatedFuelSupportStratum {
    name: String,
    flow_scale_log_uniform: BroadUniformRange,
    scientific_probability: f64,
}

fn validated_fuel_support_strata(
    model: &BroadModelConfig,
) -> Result<Vec<ValidatedFuelSupportStratum>> {
    let global = model.fuel_uncertainty.flow_scale_log_uniform;
    if !global.validate() || global.minimum <= 0.0 {
        bail!("global fuel-flow scale range must be positive and ordered");
    }
    if model.fuel_flow_support_strata.is_empty() {
        return Ok(vec![ValidatedFuelSupportStratum {
            name: "full-fuel-flow-support".to_string(),
            flow_scale_log_uniform: global,
            scientific_probability: 1.0,
        }]);
    }
    if global.minimum == global.maximum {
        bail!("fixed fuel-flow scale cannot be divided into support strata");
    }
    let mut configured = model.fuel_flow_support_strata.clone();
    configured.sort_by(|first, second| {
        first
            .flow_scale_log_uniform
            .minimum
            .total_cmp(&second.flow_scale_log_uniform.minimum)
    });
    let mut names = std::collections::BTreeSet::new();
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
            .expect("configured fuel support is non-empty")
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
        bail!("fuel-flow support strata must uniquely and contiguously partition the global range");
    }
    let total_log_width = (global.maximum / global.minimum).ln();
    Ok(configured
        .into_iter()
        .map(|entry| ValidatedFuelSupportStratum {
            scientific_probability: (entry.flow_scale_log_uniform.maximum
                / entry.flow_scale_log_uniform.minimum)
                .ln()
                / total_log_width,
            name: entry.name,
            flow_scale_log_uniform: entry.flow_scale_log_uniform,
        })
        .collect())
}

fn read_input(path: &Path, label: &str) -> Result<Vec<u8>> {
    fs::read(path).with_context(|| format!("cannot read {label}: {}", path.display()))
}

fn resolve_fuel_exhaustion_guide_window(
    config: &BroadFuelExhaustionSelectionGuideRunConfig,
    canonical_satcom_bytes: &[u8],
) -> Result<BroadResolvedFuelExhaustionGuideWindow> {
    let text = std::str::from_utf8(canonical_satcom_bytes)
        .context("canonical full SATCOM observations are not UTF-8")?;
    let mut lines = text.lines();
    let expected_header = "epoch_id,time_utc,seconds_from_t0,bto_us,bto_sd_us,bfo_hz,bfo_sd_hz,satellite_afc_hz,raw_source_rows,note";
    if lines.next().map(str::trim_end) != Some(expected_header) {
        bail!("canonical full SATCOM observations have an unexpected schema");
    }
    let mut start_time_s = None;
    let mut canonical_end_time_s = None;
    for line in lines.filter(|line| !line.trim().is_empty()) {
        let fields = line.trim_end_matches('\r').split(',').collect::<Vec<_>>();
        if fields.len() != 10 {
            bail!("canonical full SATCOM observations contain a malformed row");
        }
        if fields[0] == config.window_start_epoch_id {
            if start_time_s.is_some() {
                bail!("canonical full SATCOM observations repeat the guide-window start row");
            }
            start_time_s = Some(
                fields[2]
                    .parse::<f64>()
                    .context("guide-window start time is not numeric")?,
            );
        }
        if fields[0] == config.window_end_epoch_id {
            if canonical_end_time_s.is_some() {
                bail!("canonical full SATCOM observations repeat the guide-window end row");
            }
            let end_time_s = fields[2]
                .parse::<f64>()
                .context("guide-window end time is not numeric")?;
            let bto_us = fields[3]
                .parse::<f64>()
                .context("guide-window end BTO is not numeric")?;
            let bto_sd_us = fields[4]
                .parse::<f64>()
                .context("guide-window end BTO deviation is not numeric")?;
            if bto_us.to_bits() != 18_400.0_f64.to_bits()
                || bto_sd_us.to_bits() != 63.0_f64.to_bits()
                || !fields[5].is_empty()
                || !fields[6].is_empty()
                || !fields[9].contains("R600 corrected")
            {
                bail!("canonical m0019a row is not the guarded R600 BTO-only source");
            }
            canonical_end_time_s = Some(end_time_s);
        }
    }
    let start_time_s = start_time_s.context("canonical SATCOM source has no m0011 row")?;
    let canonical_end_time_s =
        canonical_end_time_s.context("canonical SATCOM source has no m0019a row")?;
    if start_time_s.to_bits() != 22_150.0_f64.to_bits()
        || canonical_end_time_s.to_bits() != 22_660.0_f64.to_bits()
    {
        bail!("canonical fuel-guide SATCOM times do not match the v1 time basis");
    }
    let window_end_s = canonical_end_time_s + config.window_end_contact_offset_s;
    if window_end_s.to_bits() != 22_660.416_f64.to_bits() || window_end_s <= start_time_s {
        bail!("resolved fuel-exhaustion guide window is not the exact v1 interval");
    }
    Ok(BroadResolvedFuelExhaustionGuideWindow {
        window_start_s: start_time_s,
        canonical_window_end_s: canonical_end_time_s,
        window_end_contact_offset_s: config.window_end_contact_offset_s,
        window_end_s,
    })
}

fn observations_for_family(
    config: &BroadSuiteConfig,
    family: &BroadFamilyConfig,
    observation_text: &str,
    ephemeris_text: &str,
) -> Result<Vec<BroadFlightObservation>> {
    let parsed = parse_satcom_observations(
        observation_text,
        ephemeris_text,
        config.inputs.ground_station_position_km,
        family.bfo_sd_override_hz,
    )?;
    let actual = parsed.last().context("SATCOM input is empty")?;
    if actual.id != config.inputs.fit_through_epoch_id {
        bail!(
            "fit-through guard expected {}, found {}",
            config.inputs.fit_through_epoch_id,
            actual.id
        );
    }
    let mut observations = parsed
        .into_iter()
        .map(|flight| {
            let use_bto = flight.measurement.bto.is_some();
            let use_bfo = family.use_bfo && flight.measurement.bfo.is_some();
            if use_bto || use_bfo {
                BroadFlightObservation::Satcom(BroadSatcomObservation {
                    flight,
                    use_bto,
                    use_bfo,
                })
            } else {
                BroadFlightObservation::Checkpoint {
                    id: format!("held-out-{}", flight.id),
                    time: flight.measurement.time,
                }
            }
        })
        .collect::<Vec<_>>();
    observations.push(BroadFlightObservation::FuelAnchor(
        config.fuel_anchor.clone(),
    ));
    observations.sort_by(|first, second| first.time().0.total_cmp(&second.time().0));
    for pair in observations.windows(2) {
        if pair[0].time().0 == pair[1].time().0 {
            bail!("broad observations must have distinct exact times");
        }
    }
    Ok(observations)
}

fn realized_proposal_epochs(
    model: &BroadFlightModel<'_>,
    observations: &[BroadFlightObservation],
    initial_time_s: f64,
) -> Vec<BroadRealizedProposalEpoch> {
    let mut previous_time_s = initial_time_s;
    observations
        .iter()
        .map(|observation| {
            let elapsed_seconds = observation.time().0 - previous_time_s;
            previous_time_s = observation.time().0;
            BroadRealizedProposalEpoch {
                observation_id: observation.id().to_string(),
                observation_kind: match observation {
                    BroadFlightObservation::FuelAnchor(_) => "fuel_anchor",
                    BroadFlightObservation::Satcom(_) => "satcom",
                    BroadFlightObservation::Checkpoint { .. } => "checkpoint",
                },
                elapsed_seconds,
                proposal_candidates: model
                    .proposal_candidates_for_observation(observation, elapsed_seconds),
            }
        })
        .collect()
}

fn realized_global_transition_pool_epochs(
    schedule: &BroadGlobalTransitionPoolSchedule,
    observations: &[BroadFlightObservation],
    initial_time_s: f64,
) -> (
    Vec<GlobalTransitionPoolStep>,
    Vec<BroadRealizedGlobalTransitionPoolEpoch>,
) {
    let mut previous_time_s = initial_time_s;
    let realized = observations
        .iter()
        .enumerate()
        .map(|(observation_index, observation)| {
            let observation_time_s = observation.time().0;
            let elapsed_seconds = observation_time_s - previous_time_s;
            previous_time_s = observation_time_s;
            let step = schedule.step_for_elapsed_seconds(elapsed_seconds);
            (
                step,
                BroadRealizedGlobalTransitionPoolEpoch {
                    observation_index,
                    observation_id: observation.id().to_string(),
                    observation_kind: match observation {
                        BroadFlightObservation::FuelAnchor(_) => "fuel_anchor",
                        BroadFlightObservation::Satcom(_) => "satcom",
                        BroadFlightObservation::Checkpoint { .. } => "checkpoint",
                    },
                    observation_time_s,
                    elapsed_seconds,
                    step,
                },
            )
        })
        .collect::<Vec<_>>();
    realized.into_iter().unzip()
}

fn realized_root_stratified_transition_pool_epochs(
    config: &BroadRootStratifiedTransitionPoolConfig,
    observations: &[BroadFlightObservation],
) -> Result<(
    Vec<RootStratifiedTransitionPoolStep>,
    Vec<BroadRealizedRootStratifiedTransitionPoolEpoch>,
)> {
    let configured = config
        .epochs
        .iter()
        .map(|epoch| {
            (
                epoch.observation_id.as_str(),
                epoch.candidates_per_positive_root,
            )
        })
        .collect::<BTreeMap<_, _>>();
    let mut realized_id_counts = BTreeMap::<&str, usize>::new();
    let realized = observations
        .iter()
        .enumerate()
        .map(|(observation_index, observation)| {
            let step = configured.get(observation.id()).map_or(
                RootStratifiedTransitionPoolStep::Standard,
                |&candidates_per_positive_root| {
                    *realized_id_counts.entry(observation.id()).or_default() += 1;
                    RootStratifiedTransitionPoolStep::Pool {
                        candidates_per_positive_root,
                    }
                },
            );
            (
                step,
                BroadRealizedRootStratifiedTransitionPoolEpoch {
                    observation_index,
                    observation_id: observation.id().to_string(),
                    observation_kind: match observation {
                        BroadFlightObservation::FuelAnchor(_) => "fuel_anchor",
                        BroadFlightObservation::Satcom(_) => "satcom",
                        BroadFlightObservation::Checkpoint { .. } => "checkpoint",
                    },
                    observation_time_s: observation.time().0,
                    step,
                },
            )
        })
        .collect::<Vec<_>>();
    if realized_id_counts.values().any(|&count| count != 1) {
        bail!(
            "root-stratified transition-pool observation IDs must each occur exactly once in the realized observation sequence"
        );
    }
    if realized_id_counts.len() != configured.len() {
        let missing = configured
            .keys()
            .filter(|id| !realized_id_counts.contains_key(*id))
            .copied()
            .collect::<Vec<_>>()
            .join(", ");
        bail!("root-stratified transition-pool observation IDs were not realized: {missing}");
    }
    Ok(realized.into_iter().unzip())
}

fn realized_satcom_event_mark_guide_epochs(
    config: &BroadSatcomEventMarkGuideRunConfig,
    observations: &[BroadFlightObservation],
    initial_time_s: f64,
) -> Result<Vec<BroadRealizedSatcomEventMarkGuideEpoch>> {
    let resolved = config.resolved();
    let configured = resolved
        .epochs
        .iter()
        .map(|epoch| (epoch.observation_id.as_str(), epoch))
        .collect::<BTreeMap<_, _>>();
    let mut realized_id_counts = BTreeMap::<&str, usize>::new();
    for observation in observations {
        if configured.contains_key(observation.id()) {
            *realized_id_counts.entry(observation.id()).or_default() += 1;
        }
    }
    if realized_id_counts.values().any(|&count| count != 1) {
        bail!(
            "SATCOM event-mark guide observation IDs must each occur exactly once in the realized observation sequence"
        );
    }
    if realized_id_counts.len() != configured.len() {
        let missing = configured
            .keys()
            .filter(|id| !realized_id_counts.contains_key(*id))
            .copied()
            .collect::<Vec<_>>()
            .join(", ");
        bail!("SATCOM event-mark guide observation IDs were not realized: {missing}");
    }
    let mut realized = Vec::with_capacity(configured.len());
    let mut transition_start_s = initial_time_s;
    for (observation_index, observation) in observations.iter().enumerate() {
        let observation_time_s = observation.time().0;
        if let Some(epoch) = configured.get(observation.id()) {
            let BroadFlightObservation::Satcom(satcom) = observation else {
                bail!(
                    "SATCOM event-mark guide observation {} resolved to a non-SATCOM epoch",
                    observation.id()
                );
            };
            if !satcom.use_bto && !satcom.use_bfo {
                bail!(
                    "SATCOM event-mark guide observation {} has no enabled endpoint channel",
                    observation.id()
                );
            }
            let eligible_event_time_minimum_s =
                transition_start_s.max(observation_time_s - epoch.maximum_lookback.0);
            let eligible_event_time_maximum_s = observation_time_s - epoch.minimum_lead.0;
            if eligible_event_time_minimum_s > eligible_event_time_maximum_s {
                bail!(
                    "SATCOM event-mark guide observation {} has no eligible event time in its physical transition",
                    observation.id()
                );
            }
            realized.push(BroadRealizedSatcomEventMarkGuideEpoch {
                observation_index,
                observation_id: observation.id().to_string(),
                observation_kind: "satcom",
                transition_start_s,
                observation_time_s,
                eligible_event_time_minimum_s,
                eligible_event_time_maximum_s,
                minimum_lead_s: epoch.minimum_lead.0,
                maximum_lookback_s: epoch.maximum_lookback.0,
                candidates_per_event: epoch.candidates_per_event,
                defensive_prior_probability: epoch.defensive_prior_probability,
                score_temperature: epoch.score_temperature,
                use_bto: satcom.use_bto,
                use_bfo: satcom.use_bfo,
            });
        }
        transition_start_s = observation_time_s;
    }
    Ok(realized)
}

fn realized_pending_renewal_refresh_epochs(
    config: &BroadPendingRenewalRefreshRunConfig,
    observations: &[BroadFlightObservation],
) -> Result<(
    Vec<StratifiedPostResampleMoveStep>,
    Vec<BroadRealizedPendingRenewalRefreshEpoch>,
)> {
    config.validate()?;
    if observations.is_empty() {
        bail!("pending-renewal refresh requires a non-empty observation sequence");
    }
    let configured = config
        .after_observation_ids
        .iter()
        .map(|id| (id.as_str(), ()))
        .collect::<BTreeMap<_, _>>();
    let mut realized_id_counts = BTreeMap::<&str, usize>::new();
    let realized = observations
        .iter()
        .enumerate()
        .map(|(observation_index, observation)| {
            let step = if configured.contains_key(observation.id()) {
                *realized_id_counts.entry(observation.id()).or_default() += 1;
                StratifiedPostResampleMoveStep::Apply
            } else {
                StratifiedPostResampleMoveStep::Inactive
            };
            (
                step,
                BroadRealizedPendingRenewalRefreshEpoch {
                    observation_index,
                    observation_id: observation.id().to_string(),
                    observation_kind: match observation {
                        BroadFlightObservation::FuelAnchor(_) => "fuel_anchor",
                        BroadFlightObservation::Satcom(_) => "satcom",
                        BroadFlightObservation::Checkpoint { .. } => "checkpoint",
                    },
                    observation_time_s: observation.time().0,
                    step,
                },
            )
        })
        .collect::<Vec<_>>();
    if realized_id_counts.values().any(|&count| count != 1) {
        bail!(
            "pending-renewal refresh observation IDs must each occur exactly once in the realized observation sequence"
        );
    }
    if realized_id_counts.len() != configured.len() {
        let missing = configured
            .keys()
            .filter(|id| !realized_id_counts.contains_key(*id))
            .copied()
            .collect::<Vec<_>>()
            .join(", ");
        bail!("pending-renewal refresh observation IDs were not realized: {missing}");
    }
    if let Some(final_epoch) = realized.last().map(|(_, epoch)| epoch) {
        if final_epoch.step == StratifiedPostResampleMoveStep::Apply {
            bail!(
                "pending-renewal refresh cannot target final observation {} because no powered propagation follows it",
                final_epoch.observation_id
            );
        }
    }
    Ok(realized.into_iter().unzip())
}

fn realized_intermediate_satcom_bridge_epochs(
    config: BroadIntermediateSatcomBridgeConfig,
    observations: &[BroadFlightObservation],
    initial_time_s: f64,
) -> Result<(
    Vec<IntermediatePotentialStep<BroadSatcomIntermediatePotentialPoint>>,
    Vec<BroadRealizedIntermediatePotentialEpoch>,
)> {
    let resolved = config.resolved();
    let mut previous_time = Seconds(initial_time_s);
    let realized = observations
        .iter()
        .enumerate()
        .map(|(observation_index, observation)| {
            let observation_time_s = observation.time().0;
            let elapsed_seconds = observation_time_s - previous_time.0;
            let step = resolved
                .step_for_endpoint(previous_time, observation)
                .map_err(anyhow::Error::new)?;
            let step = match step {
                IntermediatePotentialStep::Bridge { points }
                    if config.endpoint_candidates_per_particle > 1 =>
                {
                    IntermediatePotentialStep::BridgeWithEndpointPool {
                        points,
                        endpoint_candidates_per_particle: config.endpoint_candidates_per_particle,
                    }
                }
                step => step,
            };
            previous_time = observation.time();
            Ok((
                step.clone(),
                BroadRealizedIntermediatePotentialEpoch {
                    observation_index,
                    observation_id: observation.id().to_string(),
                    observation_kind: match observation {
                        BroadFlightObservation::FuelAnchor(_) => "fuel_anchor",
                        BroadFlightObservation::Satcom(_) => "satcom",
                        BroadFlightObservation::Checkpoint { .. } => "checkpoint",
                    },
                    observation_time_s,
                    elapsed_seconds,
                    step,
                },
            ))
        })
        .collect::<Result<Vec<_>>>()?;
    Ok(realized.into_iter().unzip())
}

fn realized_fuel_exhaustion_selection_guide_epochs(
    config: &BroadFuelExhaustionSelectionGuideRunConfig,
    window: BroadResolvedFuelExhaustionGuideWindow,
    observations: &[BroadFlightObservation],
) -> Result<(
    Vec<SelectionGuideStep<BroadFuelExhaustionSelectionGuidePoint>>,
    Vec<BroadRealizedFuelExhaustionSelectionGuideEpoch>,
)> {
    let point = BroadFuelExhaustionSelectionGuidePoint {
        window_start: Seconds(window.window_start_s),
        window_end: Seconds(window.window_end_s),
    };
    point.validate().map_err(anyhow::Error::new)?;
    let neutral = config.potential_floor.to_bits() == 1.0_f64.to_bits();
    let mut fuel_anchor_seen = false;
    let mut guided_epochs = 0usize;
    let mut realized = Vec::with_capacity(observations.len());
    for (observation_index, observation) in observations.iter().enumerate() {
        let is_fuel_anchor = matches!(observation, BroadFlightObservation::FuelAnchor(_));
        if is_fuel_anchor && fuel_anchor_seen {
            bail!("fuel-exhaustion selection guidance requires exactly one fuel anchor");
        }
        let after_fuel_anchor = fuel_anchor_seen;
        let step = if !neutral && after_fuel_anchor {
            if observation.time().0 > window.window_start_s + 1.0e-9 {
                bail!(
                    "fuel-exhaustion selection guidance cannot target an endpoint after its window start"
                );
            }
            guided_epochs += 1;
            SelectionGuideStep::Guide { point }
        } else {
            SelectionGuideStep::Unguided
        };
        realized.push(BroadRealizedFuelExhaustionSelectionGuideEpoch {
            observation_index,
            observation_id: observation.id().to_string(),
            observation_kind: match observation {
                BroadFlightObservation::FuelAnchor(_) => "fuel_anchor",
                BroadFlightObservation::Satcom(_) => "satcom",
                BroadFlightObservation::Checkpoint { .. } => "checkpoint",
            },
            observation_time_s: observation.time().0,
            after_fuel_anchor,
            step,
        });
        if is_fuel_anchor {
            fuel_anchor_seen = true;
        }
    }
    if !fuel_anchor_seen {
        bail!("fuel-exhaustion selection guidance requires exactly one fuel anchor");
    }
    if !neutral && guided_epochs == 0 {
        bail!("fuel-exhaustion selection guidance has no observation after the fuel anchor");
    }
    let steps = realized.iter().map(|epoch| epoch.step.clone()).collect();
    Ok((steps, realized))
}

fn realized_fuel_exhaustion_persistent_twist_epochs(
    config: &BroadFuelExhaustionPersistentTwistRunConfig,
    window: BroadResolvedFuelExhaustionGuideWindow,
    observations: &[BroadFlightObservation],
    fit_through_epoch_id: &str,
) -> Result<(
    Vec<PersistentTwistStep<BroadFuelExhaustionSelectionGuidePoint>>,
    Vec<BroadRealizedFuelExhaustionPersistentTwistEpoch>,
)> {
    let point = BroadFuelExhaustionSelectionGuidePoint {
        window_start: Seconds(window.window_start_s),
        window_end: Seconds(window.window_end_s),
    };
    point.validate().map_err(anyhow::Error::new)?;
    let neutral = config.potential_floor.to_bits() == 1.0_f64.to_bits();
    let mut fuel_anchor_seen = false;
    let mut active = false;
    let mut finalized = false;
    let mut fuel_anchor_count = 0usize;
    let mut realized = Vec::with_capacity(observations.len());
    for (observation_index, observation) in observations.iter().enumerate() {
        if finalized {
            bail!("persistent fuel twist has an observation after finalization");
        }
        let is_fuel_anchor = matches!(observation, BroadFlightObservation::FuelAnchor(_));
        if is_fuel_anchor {
            fuel_anchor_count += 1;
        }
        let after_fuel_anchor = fuel_anchor_seen;
        let is_fit_through = observation.id() == fit_through_epoch_id;
        let step = if neutral || !after_fuel_anchor {
            PersistentTwistStep::Inactive
        } else if is_fit_through {
            if !active {
                bail!(
                    "persistent fuel twist requires an activation observation before fit-through"
                );
            }
            finalized = true;
            PersistentTwistStep::Finalize { point }
        } else if !active {
            active = true;
            PersistentTwistStep::Activate { point }
        } else {
            PersistentTwistStep::Continue { point }
        };
        if active && !neutral && observation.time().0 > window.window_start_s + 1.0e-9 {
            bail!("persistent fuel twist cannot target an endpoint after its window start");
        }
        realized.push(BroadRealizedFuelExhaustionPersistentTwistEpoch {
            observation_index,
            observation_id: observation.id().to_string(),
            observation_kind: match observation {
                BroadFlightObservation::FuelAnchor(_) => "fuel_anchor",
                BroadFlightObservation::Satcom(_) => "satcom",
                BroadFlightObservation::Checkpoint { .. } => "checkpoint",
            },
            observation_time_s: observation.time().0,
            after_fuel_anchor,
            step,
        });
        if is_fuel_anchor {
            fuel_anchor_seen = true;
        }
    }
    if fuel_anchor_count != 1 {
        bail!("persistent fuel twist requires exactly one fuel anchor");
    }
    if observations.last().map(|observation| observation.id()) != Some(fit_through_epoch_id) {
        bail!("persistent fuel twist must finalize at the final fit-through observation");
    }
    if !neutral && (!active || !finalized) {
        bail!("active persistent fuel twist has an incomplete lifecycle");
    }
    let steps = realized.iter().map(|epoch| epoch.step.clone()).collect();
    Ok((steps, realized))
}

fn persistent_twist_schedule_is_active(
    steps: &[PersistentTwistStep<BroadFuelExhaustionSelectionGuidePoint>],
) -> bool {
    steps
        .iter()
        .any(|step| !matches!(step, PersistentTwistStep::Inactive))
}

fn effective_sample_size(log_weights: &[f64]) -> f64 {
    1.0 / log_weights
        .iter()
        .map(|value| (2.0 * value).exp())
        .sum::<f64>()
}

fn seed_posterior_population(
    seed: u64,
    result: &FilterResult<BroadFlightState>,
) -> BroadSeedPosteriorPopulation {
    let mut points = Vec::new();
    let mut root_masses = BTreeMap::<usize, f64>::new();
    for ((state, &log_weight), &root) in result
        .particles
        .iter()
        .zip(&result.log_weights)
        .zip(&result.root_ids)
    {
        if log_weight.is_finite() {
            let weight = log_weight.exp();
            points.push(ReportPoint {
                latitude_deg: state.powered_flight.aircraft.position.latitude.0,
                longitude_deg: state.powered_flight.aircraft.position.longitude.0,
                weight,
            });
            *root_masses.entry(root).or_default() += weight;
        }
    }
    BroadSeedPosteriorPopulation {
        seed,
        log_evidence: result.log_evidence,
        points,
        root_masses: root_masses.into_values().collect(),
    }
}

fn pool_independent_seed_posteriors(
    mut populations: Vec<BroadSeedPosteriorPopulation>,
) -> Result<(Vec<ReportPoint>, Option<BroadIndependentSeedPoolSummary>)> {
    if populations.is_empty() {
        bail!("cannot pool an empty set of independent broad-flight seed populations");
    }
    if populations.len() == 1 {
        return Ok((populations.pop().expect("one seed population").points, None));
    }
    let log_evidences = populations
        .iter()
        .map(|population| population.log_evidence)
        .collect::<Vec<_>>();
    let (log_evidence_weights, _) = normalize_log_weights(&log_evidences)
        .map_err(anyhow::Error::new)
        .context("cannot normalize independent seed evidence estimates")?;
    let mut seed_evidence_weights = Vec::with_capacity(populations.len());
    let mut pooled_points = Vec::new();
    let mut evidence_weight_sum_squares = 0.0;
    let mut maximum_seed_evidence_weight = 0.0_f64;
    let mut pooled_particle_sum_squares = 0.0;
    let mut namespaced_root_sum_squares = 0.0;
    let mut maximum_namespaced_root_weight = 0.0_f64;
    for (mut population, &log_evidence_weight) in populations.into_iter().zip(&log_evidence_weights)
    {
        let evidence_weight = log_evidence_weight.exp();
        let conditional_particle_mass = population
            .points
            .iter()
            .map(|point| point.weight)
            .sum::<f64>();
        let conditional_root_mass = population.root_masses.iter().sum::<f64>();
        if !conditional_particle_mass.is_finite()
            || !conditional_root_mass.is_finite()
            || (conditional_particle_mass - 1.0).abs() > 1.0e-8
            || (conditional_root_mass - 1.0).abs() > 1.0e-8
        {
            bail!("independent seed posterior is not conditionally normalized");
        }
        evidence_weight_sum_squares += evidence_weight.powi(2);
        maximum_seed_evidence_weight = maximum_seed_evidence_weight.max(evidence_weight);
        for point in &mut population.points {
            point.weight *= evidence_weight;
            pooled_particle_sum_squares += point.weight.powi(2);
        }
        for root_mass in population.root_masses {
            let namespaced_mass = evidence_weight * root_mass;
            namespaced_root_sum_squares += namespaced_mass.powi(2);
            maximum_namespaced_root_weight = maximum_namespaced_root_weight.max(namespaced_mass);
        }
        seed_evidence_weights.push(BroadSeedEvidenceWeight {
            seed: population.seed,
            log_evidence: population.log_evidence,
            normalized_evidence_weight: evidence_weight,
        });
        pooled_points.extend(population.points);
    }
    if evidence_weight_sum_squares <= 0.0
        || pooled_particle_sum_squares <= 0.0
        || namespaced_root_sum_squares <= 0.0
    {
        bail!("independent seed pooling produced an empty posterior measure");
    }
    Ok((
        pooled_points,
        Some(BroadIndependentSeedPoolSummary {
            pooling_semantics:
                BroadIndependentSeedPoolingSemantics::EvidenceWeightedIndependentPosteriorMixture,
            seed_evidence_weights,
            evidence_weight_effective_sample_size: 1.0 / evidence_weight_sum_squares,
            maximum_seed_evidence_weight,
            pooled_particle_effective_sample_size: 1.0 / pooled_particle_sum_squares,
            seed_namespaced_root_effective_sample_size: 1.0 / namespaced_root_sum_squares,
            maximum_seed_namespaced_root_weight: maximum_namespaced_root_weight,
        }),
    ))
}

fn pool_fuel_exhaustion_selection_posteriors(
    populations: &[BroadFuelExhaustionPosteriorPopulation],
    independent_seed_pooling: Option<&BroadIndependentSeedPoolSummary>,
) -> Result<BroadFuelExhaustionPosteriorSummary> {
    if populations.is_empty() {
        bail!("cannot pool an empty set of fuel-selection posterior diagnostics");
    }
    if populations.len() == 1 && independent_seed_pooling.is_some()
        || populations.len() > 1 && independent_seed_pooling.is_none()
    {
        bail!("fuel-selection diagnostics lack the matching independent-seed pooling ledger");
    }
    let evidence_weight = |seed| -> Result<f64> {
        match independent_seed_pooling {
            None => Ok(1.0),
            Some(pooling) => pooling
                .seed_evidence_weights
                .iter()
                .find(|entry| entry.seed == seed)
                .map(|entry| entry.normalized_evidence_weight)
                .with_context(|| format!("seed {seed} has no evidence weight")),
        }
    };
    let outcomes = fuel_selection_outcomes();
    let mut outcome_slots = [0usize; 6];
    let mut outcome_mass = [0.0_f64; 6];
    let mut retained_slots = 0usize;
    let mut positive_weight_slots = 0usize;
    let mut compatible_positive_weight_slots = 0usize;
    let mut compatible_root_sum_squares = 0.0;
    let mut maximum_compatible_root_mass = 0.0_f64;
    let mut compatible_distinct_namespaced_roots = 0usize;
    let mut compatible_stratum_slots = BTreeMap::<u32, usize>::new();
    let mut compatible_stratum_roots = BTreeMap::<u32, Vec<f64>>::new();
    let mut compatible_projected_min = f64::INFINITY;
    let mut compatible_projected_max = f64::NEG_INFINITY;
    let mut compatible_projected_weighted_sum = 0.0;
    for population in populations {
        let alpha = evidence_weight(population.seed)?;
        retained_slots += population.summary.retained_slots;
        positive_weight_slots += population.summary.positive_weight_slots;
        compatible_positive_weight_slots += population.summary.compatible_positive_weight_slots;
        for outcome in &population.summary.outcomes {
            let index = fuel_selection_outcome_index(outcome.outcome);
            outcome_slots[index] += outcome.retained_slots;
            outcome_mass[index] += alpha * outcome.posterior_mass;
        }
        for &root_mass in &population.compatible_root_masses {
            let namespaced_mass = alpha * root_mass;
            compatible_root_sum_squares += namespaced_mass.powi(2);
            maximum_compatible_root_mass = maximum_compatible_root_mass.max(namespaced_mass);
        }
        compatible_distinct_namespaced_roots += population.compatible_root_masses.len();
        for stratum in &population.summary.compatible_strata {
            *compatible_stratum_slots.entry(stratum.stratum).or_default() +=
                stratum.compatible_positive_weight_slots;
        }
        for (&stratum, roots) in &population.compatible_root_masses_by_stratum {
            compatible_stratum_roots
                .entry(stratum)
                .or_default()
                .extend(roots.iter().map(|mass| alpha * mass));
        }
        if population.summary.compatible_posterior_mass > 0.0 {
            if let Some(value) = population
                .summary
                .compatible_projected_exhaustion_time_min_s
            {
                compatible_projected_min = compatible_projected_min.min(value);
            }
            if let Some(value) = population
                .summary
                .compatible_projected_exhaustion_time_max_s
            {
                compatible_projected_max = compatible_projected_max.max(value);
            }
            if let Some(value) = population
                .summary
                .compatible_projected_exhaustion_time_mean_s
            {
                compatible_projected_weighted_sum +=
                    alpha * population.summary.compatible_posterior_mass * value;
            }
        }
    }
    let compatible_mass = outcome_mass[0];
    let positive_compatible = compatible_mass > 0.0 && compatible_root_sum_squares > 0.0;
    let total_mass = outcome_mass.iter().sum::<f64>();
    if !total_mass.is_finite() || (total_mass - 1.0).abs() > 1.0e-8 {
        bail!("pooled fuel-selection outcome masses are not normalized");
    }
    Ok(BroadFuelExhaustionPosteriorSummary {
        retained_slots,
        positive_weight_slots,
        zero_weight_placeholder_slots: retained_slots - positive_weight_slots,
        outcomes: outcomes
            .into_iter()
            .enumerate()
            .map(|(index, outcome)| BroadFuelExhaustionOutcomeSummary {
                outcome,
                retained_slots: outcome_slots[index],
                posterior_mass: outcome_mass[index],
            })
            .collect(),
        compatible_retained_slot_fraction: outcome_slots[0] as f64 / retained_slots as f64,
        compatible_positive_weight_slots,
        compatible_positive_weight_slot_fraction: compatible_positive_weight_slots as f64
            / positive_weight_slots as f64,
        distinct_compatible_seed_local_roots: compatible_distinct_namespaced_roots,
        compatible_posterior_mass: compatible_mass,
        compatible_root_effective_sample_size: positive_compatible
            .then_some(compatible_mass.powi(2) / compatible_root_sum_squares),
        maximum_compatible_root_weight: positive_compatible
            .then_some(maximum_compatible_root_mass / compatible_mass),
        compatible_projected_exhaustion_time_min_s: positive_compatible
            .then_some(compatible_projected_min),
        compatible_projected_exhaustion_time_mean_s: positive_compatible
            .then_some(compatible_projected_weighted_sum / compatible_mass),
        compatible_projected_exhaustion_time_max_s: positive_compatible
            .then_some(compatible_projected_max),
        compatible_strata: compatible_stratum_slots
            .into_iter()
            .map(|(stratum, compatible_positive_weight_slots)| {
                let roots = compatible_stratum_roots
                    .remove(&stratum)
                    .unwrap_or_default();
                let mass = roots.iter().sum::<f64>();
                let sum_squares = roots.iter().map(|value| value.powi(2)).sum::<f64>();
                BroadFuelExhaustionCompatibleStratumSummary {
                    stratum,
                    compatible_positive_weight_slots,
                    distinct_compatible_seed_local_roots: roots.len(),
                    compatible_physical_posterior_mass: mass,
                    compatible_physical_root_effective_sample_size: (sum_squares > 0.0)
                        .then_some(mass.powi(2) / sum_squares),
                    maximum_compatible_physical_root_weight: (mass > 0.0)
                        .then(|| roots.iter().copied().fold(0.0_f64, f64::max) / mass),
                }
            })
            .collect(),
    })
}

fn summarize_islands(
    result: &StratifiedIslandFilterResult<BroadFlightState>,
) -> BroadIslandSeedSummary {
    let final_checkpoint = result
        .island_checkpoints
        .last()
        .expect("a broad island run always contains at least one observation");
    let positive = final_checkpoint
        .islands
        .iter()
        .filter(|island| island.globally_normalized_log_mass.is_some())
        .collect::<Vec<_>>();
    BroadIslandSeedSummary {
        configured_islands: result.islands.len(),
        positive_mass_islands: final_checkpoint.positive_mass_islands,
        extinct_islands: result
            .islands
            .iter()
            .filter(|island| {
                matches!(
                    island.termination,
                    IslandTermination::ExtinctAtObservation { .. }
                )
            })
            .count(),
        island_effective_sample_size: final_checkpoint.island_effective_sample_size,
        maximum_island_mass: final_checkpoint.maximum_island_mass,
        minimum_positive_island_particle_effective_sample_size: positive
            .iter()
            .map(|island| island.conditional_particle_effective_sample_size)
            .reduce(f64::min)
            .unwrap_or(0.0),
        minimum_positive_island_root_effective_sample_size: positive
            .iter()
            .map(|island| island.conditional_root_effective_sample_size)
            .reduce(f64::min)
            .unwrap_or(0.0),
        maximum_positive_island_conditional_particle_weight: positive
            .iter()
            .map(|island| island.conditional_maximum_particle_weight)
            .fold(0.0, f64::max),
    }
}

fn summarize_global_transition_pool(
    result: &GlobalTransitionPoolFilterResult<BroadFlightState>,
) -> BroadGlobalTransitionPoolSeedSummary {
    BroadGlobalTransitionPoolSeedSummary {
        pooled_epochs: result.transition_pool_checkpoints.len(),
        total_configured_candidates: result
            .transition_pool_checkpoints
            .iter()
            .map(|checkpoint| checkpoint.configured_candidates)
            .sum(),
        total_generated_candidates: result
            .transition_pool_checkpoints
            .iter()
            .map(|checkpoint| checkpoint.generated_candidates)
            .sum(),
        total_positive_candidates: result
            .transition_pool_checkpoints
            .iter()
            .map(|checkpoint| checkpoint.positive_candidates)
            .sum(),
        minimum_candidate_effective_sample_size: result
            .transition_pool_checkpoints
            .iter()
            .map(|checkpoint| checkpoint.candidate_effective_sample_size)
            .reduce(f64::min)
            .unwrap_or(0.0),
        maximum_candidate_weight: result
            .transition_pool_checkpoints
            .iter()
            .map(|checkpoint| checkpoint.maximum_candidate_weight)
            .fold(0.0, f64::max),
        minimum_candidate_root_effective_sample_size: result
            .transition_pool_checkpoints
            .iter()
            .map(|checkpoint| checkpoint.candidate_root_effective_sample_size)
            .reduce(f64::min)
            .unwrap_or(0.0),
        maximum_candidate_root_weight: result
            .transition_pool_checkpoints
            .iter()
            .map(|checkpoint| checkpoint.maximum_candidate_root_weight)
            .fold(0.0, f64::max),
        maximum_absolute_output_resampling_log_correction: result
            .transition_pool_checkpoints
            .iter()
            .map(|checkpoint| checkpoint.output_resampling_log_correction.abs())
            .fold(0.0, f64::max),
    }
}

fn summarize_root_stratified_transition_pool<S>(
    result: &RootStratifiedTransitionPoolFilterResult<S>,
) -> BroadRootStratifiedTransitionPoolSeedSummary {
    let root_strata = result
        .root_stratified_candidate_pool_checkpoints
        .iter()
        .flat_map(|checkpoint| &checkpoint.strata)
        .filter(|stratum| stratum.input_positive_roots > 0)
        .collect::<Vec<_>>();
    BroadRootStratifiedTransitionPoolSeedSummary {
        pooled_epochs: result.root_stratified_candidate_pool_checkpoints.len(),
        total_input_positive_root_epoch_instances: root_strata
            .iter()
            .map(|stratum| stratum.input_positive_roots)
            .sum(),
        total_configured_candidates: result
            .root_stratified_candidate_pool_checkpoints
            .iter()
            .map(|checkpoint| checkpoint.configured_candidates)
            .sum(),
        total_generated_candidates: result
            .root_stratified_candidate_pool_checkpoints
            .iter()
            .map(|checkpoint| checkpoint.generated_candidates)
            .sum(),
        total_positive_candidates: result
            .transition_pool_checkpoints
            .iter()
            .map(|checkpoint| checkpoint.positive_candidates)
            .sum(),
        total_roots_with_positive_candidates: root_strata
            .iter()
            .map(|stratum| stratum.roots_with_positive_candidates)
            .sum(),
        minimum_positive_candidates_per_root: root_strata
            .iter()
            .map(|stratum| stratum.minimum_positive_candidates_per_root)
            .min()
            .unwrap_or(0),
        maximum_positive_candidates_per_root: root_strata
            .iter()
            .map(|stratum| stratum.maximum_positive_candidates_per_root)
            .max()
            .unwrap_or(0),
        minimum_within_root_candidate_effective_sample_size: root_strata
            .iter()
            .map(|stratum| stratum.minimum_within_root_candidate_effective_sample_size)
            .reduce(f64::min)
            .unwrap_or(0.0),
        minimum_stratum_median_within_root_candidate_effective_sample_size: root_strata
            .iter()
            .map(|stratum| stratum.median_within_root_candidate_effective_sample_size)
            .reduce(f64::min)
            .unwrap_or(0.0),
        maximum_within_root_candidate_weight: root_strata
            .iter()
            .map(|stratum| stratum.maximum_within_root_candidate_weight)
            .fold(0.0, f64::max),
        roots_with_maximum_candidate_weight_at_least_half: root_strata
            .iter()
            .map(|stratum| stratum.roots_with_maximum_candidate_weight_at_least_half)
            .sum(),
        minimum_candidate_effective_sample_size: result
            .transition_pool_checkpoints
            .iter()
            .map(|checkpoint| checkpoint.candidate_effective_sample_size)
            .reduce(f64::min)
            .unwrap_or(0.0),
        maximum_candidate_weight: result
            .transition_pool_checkpoints
            .iter()
            .map(|checkpoint| checkpoint.maximum_candidate_weight)
            .fold(0.0, f64::max),
        minimum_candidate_root_effective_sample_size: result
            .transition_pool_checkpoints
            .iter()
            .map(|checkpoint| checkpoint.candidate_root_effective_sample_size)
            .reduce(f64::min)
            .unwrap_or(0.0),
        maximum_candidate_root_weight: result
            .transition_pool_checkpoints
            .iter()
            .map(|checkpoint| checkpoint.maximum_candidate_root_weight)
            .fold(0.0, f64::max),
        maximum_absolute_output_resampling_log_correction: result
            .transition_pool_checkpoints
            .iter()
            .map(|checkpoint| checkpoint.output_resampling_log_correction.abs())
            .fold(0.0, f64::max),
        maximum_absolute_split_log_evidence_difference: result
            .root_stratified_candidate_pool_checkpoints
            .iter()
            .filter_map(|checkpoint| checkpoint.absolute_split_log_evidence_difference)
            .reduce(f64::max),
        maximum_split_candidate_root_total_variation: result
            .root_stratified_candidate_pool_checkpoints
            .iter()
            .filter_map(|checkpoint| checkpoint.split_candidate_root_total_variation)
            .reduce(f64::max),
    }
}

fn close_refresh_float(left: f64, right: f64) -> bool {
    let scale = 1.0 + left.abs().max(right.abs());
    (left - right).abs() <= 1.0e-10 * scale
}

fn validate_pending_renewal_refresh_diagnostics(
    config: &BroadPendingRenewalRefreshRunConfig,
    realized: &[BroadRealizedPendingRenewalRefreshEpoch],
    plan: &StratifiedFilterPlan,
    result: &FilterResult<BroadFlightState>,
    checkpoints: &[StratifiedPostResampleMoveCheckpoint],
) -> Result<()> {
    if realized.len() != result.checkpoints.len() || realized.len() != checkpoints.len() {
        bail!(
            "pending-renewal refresh schedule, physical checkpoints, and move checkpoints must have identical observation counts"
        );
    }
    let mut expected_ranges = BTreeMap::new();
    let mut next_slot = 0usize;
    for allocation in &plan.strata {
        let end = next_slot
            .checked_add(allocation.particles)
            .context("pending-renewal refresh stratum range overflowed")?;
        expected_ranges.insert(allocation.id, (next_slot, end));
        next_slot = end;
    }
    if next_slot != result.particles.len() {
        bail!("pending-renewal refresh plan does not cover the pooled population");
    }
    let mut successful_refresh_epochs = 0u64;
    let mut recomposed_log_evidence = result.initial_log_evidence;
    for ((epoch, physical), checkpoint) in realized.iter().zip(&result.checkpoints).zip(checkpoints)
    {
        if epoch.observation_index != physical.observation_index
            || epoch.observation_index != checkpoint.observation_index
            || !close_refresh_float(epoch.observation_time_s, physical.observation_time_s)
            || !close_refresh_float(epoch.observation_time_s, checkpoint.observation_time_s)
            || epoch.step != checkpoint.step
            || physical.posterior_resampled != checkpoint.posterior_resampling_occurred
            || physical.guide_ess.is_some()
            || physical.ancestor_resampled
        {
            bail!("pending-renewal refresh checkpoint does not match its ordinary physical epoch");
        }
        recomposed_log_evidence += physical.log_evidence_increment;
        if !close_refresh_float(recomposed_log_evidence, physical.cumulative_log_evidence) {
            bail!("pending-renewal refresh physical log-evidence checkpoints do not recompose");
        }
        let should_invoke =
            epoch.step == StratifiedPostResampleMoveStep::Apply && physical.posterior_resampled;
        if !should_invoke {
            if checkpoint.output_move_invocations != 0 || !checkpoint.strata.is_empty() {
                bail!(
                    "pending-renewal refresh invoked outside a configured actual posterior resample"
                );
            }
            continue;
        }
        successful_refresh_epochs = successful_refresh_epochs
            .checked_add(1)
            .context("pending-renewal refresh epoch count overflowed")?;
        if checkpoint.output_move_invocations != result.particles.len()
            || checkpoint.strata.len() != plan.strata.len()
        {
            bail!(
                "pending-renewal refresh must invoke exactly once per output slot across every configured stratum"
            );
        }
        let mut seen = BTreeMap::new();
        let mut invocation_sum = 0usize;
        for stratum in &checkpoint.strata {
            let Some(&(expected_start, expected_end)) = expected_ranges.get(&stratum.stratum)
            else {
                bail!("pending-renewal refresh checkpoint names an unknown stratum");
            };
            if seen.insert(stratum.stratum, ()).is_some()
                || stratum.output_slot_start != expected_start
                || stratum.output_slot_end_exclusive != expected_end
                || stratum.output_move_invocations != expected_end - expected_start
                || stratum.distinct_parent_slots == 0
                || stratum.distinct_parent_slots > stratum.output_move_invocations
                || stratum.distinct_prior_roots == 0
                || stratum.distinct_prior_roots > stratum.distinct_parent_slots
            {
                bail!("pending-renewal refresh stratum invocation accounting is invalid");
            }
            invocation_sum = invocation_sum
                .checked_add(stratum.output_move_invocations)
                .context("pending-renewal refresh invocation count overflowed")?;
        }
        if seen.len() != expected_ranges.len()
            || invocation_sum != checkpoint.output_move_invocations
        {
            bail!("pending-renewal refresh stratum invocations do not close to the epoch total");
        }
    }
    if !close_refresh_float(recomposed_log_evidence, result.log_evidence) {
        bail!("pending-renewal refresh physical log evidence does not close to the filter result");
    }
    let selected_epoch_bound = successful_refresh_epochs;
    for (slot, (state, &log_weight)) in result.particles.iter().zip(&result.log_weights).enumerate()
    {
        let diagnostics = state.diagnostics.pending_renewal_refresh;
        if !diagnostics.validate()
            || (!config.lateral && diagnostics.lateral_refreshes != 0)
            || (!config.speed && diagnostics.speed_refreshes != 0)
            || (!config.altitude && diagnostics.altitude_refreshes != 0)
        {
            bail!("pending-renewal refresh counters are invalid for retained particle slot {slot}");
        }
        let selected = [
            config.lateral.then_some(diagnostics.lateral_refreshes),
            config.speed.then_some(diagnostics.speed_refreshes),
            config.altitude.then_some(diagnostics.altitude_refreshes),
        ]
        .into_iter()
        .flatten()
        .collect::<Vec<_>>();
        if selected.is_empty()
            || selected.iter().any(|&count| count != selected[0])
            || selected[0] > selected_epoch_bound
            || (log_weight.is_finite() && selected[0] != selected_epoch_bound)
        {
            bail!(
                "pending-renewal refresh per-lineage counters disagree with the realized move schedule for retained particle slot {slot}"
            );
        }
    }
    Ok(())
}

struct BroadFilteringOutcomeSignatureRecord {
    root_id: usize,
    log_weight: f64,
    signature: Vec<u8>,
}

fn broad_filtering_outcome_signature(state: BroadFlightState) -> Result<Vec<u8>> {
    let mut signature = state;
    for pending in [
        &mut signature.powered_flight.event_clocks.lateral,
        &mut signature.powered_flight.event_clocks.speed,
        &mut signature.powered_flight.event_clocks.altitude,
    ]
    .into_iter()
    .flatten()
    {
        // `not_before` is realized renewal history and remains part of the
        // filtering outcome. Only the disposable future draw is erased.
        pending.next_event = Seconds(0.0);
    }
    signature.diagnostics.pending_renewal_refresh = Default::default();
    serde_json::to_vec(&signature).context("cannot serialize a broad filtering-outcome signature")
}

fn summarize_filtering_outcome_signatures(
    records: &[&BroadFilteringOutcomeSignatureRecord],
    global_log_normalizer: f64,
) -> Result<BroadFilteringOutcomeSignatureDiversity> {
    if records.is_empty() {
        bail!("cannot summarize an empty finite-log-weight state population");
    }
    let population_log_mass = logsumexp(
        &records
            .iter()
            .map(|record| record.log_weight)
            .collect::<Vec<_>>(),
    )
    .map_err(anyhow::Error::new)
    .context("cannot aggregate posterior state-population mass")?;
    let mut groups = BTreeMap::<&[u8], Vec<f64>>::new();
    for record in records {
        groups
            .entry(record.signature.as_slice())
            .or_default()
            .push(record.log_weight);
    }
    let mut group_log_masses = Vec::with_capacity(groups.len());
    let mut duplicate_group_log_masses = Vec::new();
    let mut duplicate_particles = 0usize;
    let mut maximum_multiplicity = 0usize;
    for log_weights in groups.values() {
        let log_mass = logsumexp(log_weights)
            .map_err(anyhow::Error::new)
            .context("cannot aggregate a filtering-outcome signature mass")?;
        group_log_masses.push(log_mass);
        maximum_multiplicity = maximum_multiplicity.max(log_weights.len());
        if log_weights.len() > 1 {
            duplicate_particles = duplicate_particles
                .checked_add(log_weights.len())
                .context("filtering-outcome duplicate count overflowed")?;
            duplicate_group_log_masses.push(log_mass);
        }
    }
    let log_sum_squared_conditional_signature_masses = logsumexp(
        &group_log_masses
            .iter()
            .map(|log_mass| 2.0 * (log_mass - population_log_mass))
            .collect::<Vec<_>>(),
    )
    .map_err(anyhow::Error::new)
    .context("cannot calculate filtering-outcome signature ESS")?;
    let posterior_mass_in_duplicate_signature_groups = if duplicate_group_log_masses.is_empty() {
        0.0
    } else {
        (logsumexp(&duplicate_group_log_masses)
            .map_err(anyhow::Error::new)
            .context("cannot aggregate duplicate filtering-outcome signature mass")?
            - global_log_normalizer)
            .exp()
    };
    let maximum_signature_group_posterior_mass = group_log_masses
        .iter()
        .copied()
        .max_by(f64::total_cmp)
        .map(|log_mass| (log_mass - global_log_normalizer).exp())
        .unwrap_or(0.0);
    Ok(BroadFilteringOutcomeSignatureDiversity {
        finite_log_weight_particles: records.len(),
        strictly_positive_normalized_weight_particles: records
            .iter()
            .filter(|record| record.log_weight.exp() > 0.0)
            .count(),
        unique_filtering_outcome_signatures: groups.len(),
        finite_log_weight_particles_in_duplicate_signature_groups: duplicate_particles,
        posterior_mass_in_duplicate_signature_groups,
        maximum_signature_multiplicity: maximum_multiplicity,
        maximum_signature_group_posterior_mass,
        signature_aggregated_effective_sample_size: (-log_sum_squared_conditional_signature_masses)
            .exp(),
    })
}

fn summarize_posterior_state_diversity(
    result: &FilterResult<BroadFlightState>,
) -> Result<BroadPosteriorStateDiversity> {
    if result.particles.len() != result.log_weights.len()
        || result.particles.len() != result.root_ids.len()
    {
        bail!("posterior state-diversity inputs have inconsistent lengths");
    }
    let global_log_normalizer = logsumexp(&result.log_weights)
        .map_err(anyhow::Error::new)
        .context("cannot normalize posterior state-diversity weights")?;
    if !close_refresh_float(global_log_normalizer, 0.0) {
        bail!("posterior state-diversity weights are not normalized");
    }
    let records = result
        .particles
        .iter()
        .zip(&result.log_weights)
        .zip(&result.root_ids)
        .filter_map(|((state, &log_weight), &root_id)| {
            log_weight
                .is_finite()
                .then_some((state, log_weight, root_id))
        })
        .map(|(state, log_weight, root_id)| {
            Ok(BroadFilteringOutcomeSignatureRecord {
                root_id,
                log_weight,
                signature: broad_filtering_outcome_signature(*state)?,
            })
        })
        .collect::<Result<Vec<_>>>()?;
    let all_record_refs = records.iter().collect::<Vec<_>>();
    let all_particles =
        summarize_filtering_outcome_signatures(&all_record_refs, global_log_normalizer)?;
    let mut roots = BTreeMap::<usize, Vec<&BroadFilteringOutcomeSignatureRecord>>::new();
    for record in &records {
        roots.entry(record.root_id).or_default().push(record);
    }
    let mut dominant_root_id = None;
    let mut dominant_root_log_mass = f64::NEG_INFINITY;
    for (&root_id, root_records) in &roots {
        let log_mass = logsumexp(
            &root_records
                .iter()
                .map(|record| record.log_weight)
                .collect::<Vec<_>>(),
        )
        .map_err(anyhow::Error::new)
        .context("cannot aggregate prior-root posterior mass")?;
        let wins_tied_mass = match dominant_root_id {
            Some(current) => root_id < current,
            None => true,
        };
        if log_mass > dominant_root_log_mass
            || (log_mass == dominant_root_log_mass && wins_tied_mass)
        {
            dominant_root_id = Some(root_id);
            dominant_root_log_mass = log_mass;
        }
    }
    let dominant_root_id = dominant_root_id.context("posterior has no finite-log-weight root")?;
    let dominant_root_records = roots
        .get(&dominant_root_id)
        .expect("the selected dominant root came from this map");
    Ok(BroadPosteriorStateDiversity {
        filtering_outcome_signature_semantics:
            "complete_broad_flight_state_with_only_each_present_pending_renewal_next_event_canonicalized_and_pending_renewal_refresh_diagnostics_cleared;clock_presence_and_not_before_plus_stratum_physical_command_event_counter_fuel_latent_bfo_status_score_last_fit_and_all_other_diagnostics_fields_are_retained;posterior_masses_use_global_normalized_weights;ess_is_conditional_within_the_named_population",
        all_particles,
        dominant_prior_root: BroadDominantPriorRootStateDiversity {
            prior_root_id: dominant_root_id,
            posterior_mass: (dominant_root_log_mass - global_log_normalizer).exp(),
            filtering_outcome_signatures: summarize_filtering_outcome_signatures(
                dominant_root_records,
                global_log_normalizer,
            )?,
        },
    })
}

fn summarize_pending_renewal_refresh(
    result: &FilterResult<BroadFlightState>,
) -> Result<BroadPendingRenewalRefreshSeedSummary> {
    let final_snapshot = result
        .snapshots
        .last()
        .context("pending-renewal refresh run did not retain its final physical snapshot")?;
    if final_snapshot.particles != result.particles
        || final_snapshot.log_weights != result.log_weights
        || final_snapshot.root_ids != result.root_ids
        || final_snapshot.stratum_ids
            != result
                .particles
                .iter()
                .map(|state| state.stratum)
                .collect::<Vec<_>>()
    {
        bail!("pending-renewal refresh final retained snapshot differs from the pooled output");
    }
    let mut summary = BroadPendingRenewalRefreshSeedSummary::default();
    let mut minimum_selected = u64::MAX;
    let mut exact_states = BTreeMap::<Vec<u8>, usize>::new();
    let mut posterior_mass = 0.0;
    for (state, &log_weight) in final_snapshot
        .particles
        .iter()
        .zip(&final_snapshot.log_weights)
    {
        if !log_weight.is_finite() {
            continue;
        }
        let weight = log_weight.exp();
        posterior_mass += weight;
        let diagnostics = state.diagnostics.pending_renewal_refresh;
        summary.finite_log_weight_particles += 1;
        summary.strictly_positive_normalized_weight_particles += usize::from(weight > 0.0);
        summary.posterior_mass_with_refreshes +=
            weight * f64::from(diagnostics.total_refreshes > 0);
        summary.posterior_weighted_mean_total_refreshes +=
            weight * diagnostics.total_refreshes as f64;
        summary.posterior_weighted_mean_lateral_refreshes +=
            weight * diagnostics.lateral_refreshes as f64;
        summary.posterior_weighted_mean_speed_refreshes +=
            weight * diagnostics.speed_refreshes as f64;
        summary.posterior_weighted_mean_altitude_refreshes +=
            weight * diagnostics.altitude_refreshes as f64;
        minimum_selected = minimum_selected.min(diagnostics.lateral_refreshes);
        summary.maximum_selected_stream_refreshes_across_finite_log_weight_lineages = summary
            .maximum_selected_stream_refreshes_across_finite_log_weight_lineages
            .max(diagnostics.lateral_refreshes);
        let bytes = serde_json::to_vec(state)
            .context("cannot serialize a retained broad state for exact clone diagnostics")?;
        *exact_states.entry(bytes).or_default() += 1;
    }
    if summary.finite_log_weight_particles == 0 {
        bail!("pending-renewal refresh result has no finite-log-weight retained particles");
    }
    if !close_refresh_float(posterior_mass, 1.0) {
        bail!("pending-renewal refresh retained posterior weights are not normalized");
    }
    summary.minimum_selected_stream_refreshes_across_finite_log_weight_lineages = minimum_selected;
    summary.exact_state_clone_multiplicity = BroadExactStateCloneMultiplicity {
        finite_log_weight_particles: summary.finite_log_weight_particles,
        strictly_positive_normalized_weight_particles: summary
            .strictly_positive_normalized_weight_particles,
        unique_exact_states: exact_states.len(),
        maximum_exact_state_multiplicity: exact_states.values().copied().max().unwrap_or(0),
        finite_log_weight_particles_in_duplicate_exact_state_groups: exact_states
            .values()
            .copied()
            .filter(|&multiplicity| multiplicity > 1)
            .sum(),
    };
    Ok(summary)
}

fn valid_satcom_event_mark_guide_diagnostics(
    config: Option<&BroadSatcomEventMarkGuideRunConfig>,
    diagnostics: BroadSatcomEventMarkGuideDiagnostics,
) -> bool {
    let Some(config) = config else {
        return diagnostics == BroadSatcomEventMarkGuideDiagnostics::default();
    };
    let finite_sums = [
        diagnostics.sum_selection_effective_sample_size,
        diagnostics.sum_selection_entropy_nats,
        diagnostics.sum_log_candidate_count,
        diagnostics.sum_selected_log_probability,
        diagnostics.cumulative_log_prior_over_proposal,
        diagnostics.sum_minimum_log_prior_over_proposal,
        diagnostics.sum_maximum_log_prior_over_proposal,
    ]
    .into_iter()
    .all(f64::is_finite);
    let finite_options = [
        diagnostics.minimum_selected_probability,
        diagnostics.maximum_selected_probability,
        diagnostics.minimum_event_log_prior_over_proposal,
        diagnostics.maximum_event_log_prior_over_proposal,
        diagnostics.minimum_lead_seconds,
        diagnostics.maximum_lead_seconds,
    ]
    .into_iter()
    .flatten()
    .all(f64::is_finite);
    let successfully_scored_candidates = diagnostics
        .proxy_projection_successes
        .checked_add(diagnostics.proxy_projection_skipped_candidates);
    if !finite_sums
        || !finite_options
        || diagnostics.eligible_lateral_events != diagnostics.guided_lateral_events
        || match successfully_scored_candidates {
            Some(count) => diagnostics.finite_candidate_scores > count,
            None => true,
        }
        || diagnostics.all_scores_negative_infinity_events > diagnostics.guided_lateral_events
        || diagnostics
            .proxy_projection_successes
            .checked_add(diagnostics.proxy_projection_failures)
            .and_then(|count| count.checked_add(diagnostics.proxy_projection_skipped_candidates))
            .and_then(|count| count.checked_add(diagnostics.materialization_failures))
            != Some(diagnostics.candidate_marks)
    {
        return false;
    }
    if diagnostics.guided_lateral_events == 0 {
        return diagnostics == BroadSatcomEventMarkGuideDiagnostics::default();
    }
    let (
        Some(minimum_probability),
        Some(maximum_probability),
        Some(minimum_event_correction),
        Some(maximum_event_correction),
        Some(minimum_lead),
        Some(maximum_lead),
    ) = (
        diagnostics.minimum_selected_probability,
        diagnostics.maximum_selected_probability,
        diagnostics.minimum_event_log_prior_over_proposal,
        diagnostics.maximum_event_log_prior_over_proposal,
        diagnostics.minimum_lead_seconds,
        diagnostics.maximum_lead_seconds,
    )
    else {
        return false;
    };
    let scale = diagnostics
        .cumulative_log_prior_over_proposal
        .abs()
        .max(diagnostics.sum_log_candidate_count.abs())
        .max(diagnostics.sum_selected_log_probability.abs());
    let tolerance = 1.0e-10 * (1.0 + scale);
    let recomposed =
        -diagnostics.sum_log_candidate_count - diagnostics.sum_selected_log_probability;
    let minimum_candidates_per_event = config
        .epochs
        .iter()
        .map(|epoch| epoch.candidates_per_event)
        .min()
        .expect("validated guide has at least one epoch")
        as u64;
    let maximum_candidates_per_event = config
        .epochs
        .iter()
        .map(|epoch| epoch.candidates_per_event)
        .max()
        .expect("validated guide has at least one epoch")
        as u64;
    let Some(minimum_candidate_marks) = diagnostics
        .guided_lateral_events
        .checked_mul(minimum_candidates_per_event)
    else {
        return false;
    };
    let Some(maximum_candidate_marks) = diagnostics
        .guided_lateral_events
        .checked_mul(maximum_candidates_per_event)
    else {
        return false;
    };
    let configured_minimum_probability = config
        .epochs
        .iter()
        .map(|epoch| epoch.defensive_prior_probability / epoch.candidates_per_event as f64)
        .reduce(f64::min)
        .expect("validated guide has at least one epoch");
    let configured_maximum_probability = config
        .epochs
        .iter()
        .map(|epoch| {
            epoch.defensive_prior_probability / epoch.candidates_per_event as f64 + 1.0
                - epoch.defensive_prior_probability
        })
        .reduce(f64::max)
        .expect("validated guide has at least one epoch");
    let configured_minimum_lead = config
        .epochs
        .iter()
        .map(|epoch| epoch.minimum_lead_s)
        .reduce(f64::min)
        .expect("validated guide has at least one epoch");
    let configured_maximum_lookback = config
        .epochs
        .iter()
        .map(|epoch| epoch.maximum_lookback_s)
        .reduce(f64::max)
        .expect("validated guide has at least one epoch");
    let minimum_log_candidate_count = config
        .epochs
        .iter()
        .map(|epoch| (epoch.candidates_per_event as f64).ln())
        .reduce(f64::min)
        .expect("validated guide has at least one epoch");
    let maximum_log_candidate_count = config
        .epochs
        .iter()
        .map(|epoch| (epoch.candidates_per_event as f64).ln())
        .reduce(f64::max)
        .expect("validated guide has at least one epoch");
    let minimum_per_event_lower_correction = config
        .epochs
        .iter()
        .map(|epoch| {
            let log_candidate_count = (epoch.candidates_per_event as f64).ln();
            let maximum_probability =
                epoch.defensive_prior_probability / epoch.candidates_per_event as f64 + 1.0
                    - epoch.defensive_prior_probability;
            -log_candidate_count - maximum_probability.ln()
        })
        .reduce(f64::min)
        .expect("validated guide has at least one epoch");
    let maximum_per_event_lower_correction = config
        .epochs
        .iter()
        .map(|epoch| {
            let log_candidate_count = (epoch.candidates_per_event as f64).ln();
            let maximum_probability =
                epoch.defensive_prior_probability / epoch.candidates_per_event as f64 + 1.0
                    - epoch.defensive_prior_probability;
            -log_candidate_count - maximum_probability.ln()
        })
        .reduce(f64::max)
        .expect("validated guide has at least one epoch");
    let minimum_per_event_upper_correction = config
        .epochs
        .iter()
        .map(|epoch| -epoch.defensive_prior_probability.ln())
        .reduce(f64::min)
        .expect("validated guide has at least one epoch");
    let maximum_per_event_upper_correction = config
        .epochs
        .iter()
        .map(|epoch| -epoch.defensive_prior_probability.ln())
        .reduce(f64::max)
        .expect("validated guide has at least one epoch");
    let guided_events = diagnostics.guided_lateral_events as f64;
    let event_extrema_match_config = minimum_event_correction
        >= minimum_per_event_lower_correction - tolerance
        && maximum_event_correction <= maximum_per_event_upper_correction + tolerance;
    let one_epoch_extrema_recompose = if config.epochs.len() == 1 {
        let log_candidate_count = (config.epochs[0].candidates_per_event as f64).ln();
        let expected_minimum_event_correction = -log_candidate_count - maximum_probability.ln();
        let expected_maximum_event_correction = -log_candidate_count - minimum_probability.ln();
        (minimum_event_correction - expected_minimum_event_correction).abs() <= tolerance
            && (maximum_event_correction - expected_maximum_event_correction).abs() <= tolerance
    } else {
        true
    };
    let every_epoch_is_projection_neutral = config
        .epochs
        .iter()
        .all(|epoch| epoch.score_temperature == 0.0 || epoch.defensive_prior_probability == 1.0);
    let neutral_proxy_counts_close = !every_epoch_is_projection_neutral
        || (diagnostics.proxy_projection_successes == 0
            && diagnostics.proxy_projection_failures == 0
            && diagnostics.finite_candidate_scores
                == diagnostics.proxy_projection_skipped_candidates
            && diagnostics
                .proxy_projection_skipped_candidates
                .checked_add(diagnostics.materialization_failures)
                == Some(diagnostics.candidate_marks)
            && match diagnostics
                .all_scores_negative_infinity_events
                .checked_mul(minimum_candidates_per_event)
            {
                Some(minimum_all_invalid_marks) => {
                    minimum_all_invalid_marks <= diagnostics.materialization_failures
                }
                None => false,
            });
    diagnostics.candidate_marks >= minimum_candidate_marks
        && diagnostics.candidate_marks <= maximum_candidate_marks
        && event_extrema_match_config
        && one_epoch_extrema_recompose
        && neutral_proxy_counts_close
        && diagnostics.sum_log_candidate_count
            >= guided_events * minimum_log_candidate_count - tolerance
        && diagnostics.sum_log_candidate_count
            <= guided_events * maximum_log_candidate_count + tolerance
        && diagnostics.sum_minimum_log_prior_over_proposal
            >= guided_events * minimum_per_event_lower_correction - tolerance
        && diagnostics.sum_minimum_log_prior_over_proposal
            <= guided_events * maximum_per_event_lower_correction + tolerance
        && diagnostics.sum_maximum_log_prior_over_proposal
            >= guided_events * minimum_per_event_upper_correction - tolerance
        && diagnostics.sum_maximum_log_prior_over_proposal
            <= guided_events * maximum_per_event_upper_correction + tolerance
        && diagnostics.cumulative_log_prior_over_proposal
            >= guided_events * minimum_per_event_lower_correction - tolerance
        && diagnostics.cumulative_log_prior_over_proposal
            <= guided_events * maximum_per_event_upper_correction + tolerance
        && diagnostics.sum_selection_effective_sample_size
            >= diagnostics.guided_lateral_events as f64 - tolerance
        && diagnostics.sum_selection_effective_sample_size
            <= diagnostics.candidate_marks as f64 + tolerance
        && diagnostics.sum_selection_entropy_nats >= -tolerance
        && diagnostics.sum_selection_entropy_nats <= diagnostics.sum_log_candidate_count + tolerance
        && minimum_probability >= configured_minimum_probability - tolerance
        && maximum_probability <= configured_maximum_probability + tolerance
        && minimum_probability <= maximum_probability
        && minimum_event_correction <= maximum_event_correction
        && minimum_lead >= configured_minimum_lead - tolerance
        && maximum_lead <= configured_maximum_lookback + tolerance
        && minimum_lead <= maximum_lead
        && diagnostics.sum_selected_log_probability <= tolerance
        && (diagnostics.cumulative_log_prior_over_proposal - recomposed).abs() <= tolerance
        && diagnostics.cumulative_log_prior_over_proposal
            >= diagnostics.sum_minimum_log_prior_over_proposal - tolerance
        && diagnostics.cumulative_log_prior_over_proposal
            <= diagnostics.sum_maximum_log_prior_over_proposal + tolerance
}

fn validate_satcom_event_mark_guide_diagnostics(
    config: Option<&BroadSatcomEventMarkGuideRunConfig>,
    result: &FilterResult<BroadFlightState>,
) -> Result<()> {
    if let Some((particle, _)) = result.particles.iter().enumerate().find(|(_, state)| {
        !valid_satcom_event_mark_guide_diagnostics(
            config,
            state.diagnostics.satcom_event_mark_guide,
        )
    }) {
        bail!(
            "SATCOM event-mark guide diagnostics are invalid for retained particle slot {particle}"
        );
    }
    Ok(())
}

#[derive(Debug, Default)]
struct BroadSatcomEventMarkGuideStratumAccumulator {
    posterior_mass: f64,
    posterior_mass_with_guided_lateral_events: f64,
    weighted_guided_lateral_events: f64,
    weighted_candidate_marks: f64,
    weighted_cumulative_log_prior_over_proposal: f64,
}

fn positive_ratio(numerator: f64, denominator: f64) -> Option<f64> {
    (denominator > 0.0).then(|| numerator / denominator)
}

fn summarize_satcom_event_mark_guide(
    result: &FilterResult<BroadFlightState>,
) -> Result<BroadSatcomEventMarkGuideSeedSummary> {
    let mut posterior_mass = 0.0;
    let mut positive_weight_particles = 0;
    let mut mass_with_eligible = 0.0;
    let mut mass_with_guided = 0.0;
    let mut eligible = 0.0;
    let mut guided = 0.0;
    let mut candidates = 0.0;
    let mut finite_scores = 0.0;
    let mut materialization_failures = 0.0;
    let mut proxy_successes = 0.0;
    let mut proxy_failures = 0.0;
    let mut proxy_skipped = 0.0;
    let mut all_negative_infinity = 0.0;
    let mut selection_effective_sample_size = 0.0;
    let mut selection_entropy = 0.0;
    let mut correction = 0.0;
    let mut correction_squared = 0.0;
    let mut sum_log_candidate_count = 0.0;
    let mut sum_selected_log_probability = 0.0;
    let mut minimum_lead: Option<f64> = None;
    let mut maximum_lead: Option<f64> = None;
    let mut minimum_selected_probability: Option<f64> = None;
    let mut maximum_selected_probability: Option<f64> = None;
    let mut minimum_event_correction: Option<f64> = None;
    let mut maximum_event_correction: Option<f64> = None;
    let mut maximum_recomposition_error = 0.0_f64;
    let mut strata = BTreeMap::<u32, BroadSatcomEventMarkGuideStratumAccumulator>::new();
    for (state, &log_weight) in result.particles.iter().zip(&result.log_weights) {
        let diagnostics = state.diagnostics.satcom_event_mark_guide;
        let recomposed =
            -diagnostics.sum_log_candidate_count - diagnostics.sum_selected_log_probability;
        maximum_recomposition_error = maximum_recomposition_error
            .max((diagnostics.cumulative_log_prior_over_proposal - recomposed).abs());
        let weight = log_weight.exp();
        if weight == 0.0 {
            continue;
        }
        positive_weight_particles += 1;
        posterior_mass += weight;
        mass_with_eligible += weight
            * if diagnostics.eligible_lateral_events > 0 {
                1.0
            } else {
                0.0
            };
        mass_with_guided += weight
            * if diagnostics.guided_lateral_events > 0 {
                1.0
            } else {
                0.0
            };
        eligible += weight * diagnostics.eligible_lateral_events as f64;
        guided += weight * diagnostics.guided_lateral_events as f64;
        candidates += weight * diagnostics.candidate_marks as f64;
        finite_scores += weight * diagnostics.finite_candidate_scores as f64;
        materialization_failures += weight * diagnostics.materialization_failures as f64;
        proxy_successes += weight * diagnostics.proxy_projection_successes as f64;
        proxy_failures += weight * diagnostics.proxy_projection_failures as f64;
        proxy_skipped += weight * diagnostics.proxy_projection_skipped_candidates as f64;
        all_negative_infinity += weight * diagnostics.all_scores_negative_infinity_events as f64;
        selection_effective_sample_size += weight * diagnostics.sum_selection_effective_sample_size;
        selection_entropy += weight * diagnostics.sum_selection_entropy_nats;
        correction += weight * diagnostics.cumulative_log_prior_over_proposal;
        correction_squared += weight * diagnostics.cumulative_log_prior_over_proposal.powi(2);
        sum_log_candidate_count += weight * diagnostics.sum_log_candidate_count;
        sum_selected_log_probability += weight * diagnostics.sum_selected_log_probability;
        if let Some(value) = diagnostics.minimum_lead_seconds {
            minimum_lead = Some(minimum_lead.map_or(value, |current| current.min(value)));
        }
        if let Some(value) = diagnostics.maximum_lead_seconds {
            maximum_lead = Some(maximum_lead.map_or(value, |current| current.max(value)));
        }
        if let Some(value) = diagnostics.minimum_selected_probability {
            minimum_selected_probability =
                Some(minimum_selected_probability.map_or(value, |current| current.min(value)));
        }
        if let Some(value) = diagnostics.maximum_selected_probability {
            maximum_selected_probability =
                Some(maximum_selected_probability.map_or(value, |current| current.max(value)));
        }
        if let Some(value) = diagnostics.minimum_event_log_prior_over_proposal {
            minimum_event_correction =
                Some(minimum_event_correction.map_or(value, |current| current.min(value)));
        }
        if let Some(value) = diagnostics.maximum_event_log_prior_over_proposal {
            maximum_event_correction =
                Some(maximum_event_correction.map_or(value, |current| current.max(value)));
        }
        let stratum = strata.entry(state.stratum.0).or_default();
        stratum.posterior_mass += weight;
        stratum.posterior_mass_with_guided_lateral_events += weight
            * if diagnostics.guided_lateral_events > 0 {
                1.0
            } else {
                0.0
            };
        stratum.weighted_guided_lateral_events += weight * diagnostics.guided_lateral_events as f64;
        stratum.weighted_candidate_marks += weight * diagnostics.candidate_marks as f64;
        stratum.weighted_cumulative_log_prior_over_proposal +=
            weight * diagnostics.cumulative_log_prior_over_proposal;
    }
    if !posterior_mass.is_finite() || posterior_mass <= 0.0 {
        bail!("SATCOM event-mark guide summary has no positive posterior mass");
    }
    let normalized = |value: f64| value / posterior_mass;
    let mean_correction = normalized(correction);
    let strata = strata
        .into_iter()
        .map(
            |(stratum, values)| BroadSatcomEventMarkGuideStratumSummary {
                stratum,
                posterior_mass: normalized(values.posterior_mass),
                posterior_mass_with_guided_lateral_events: normalized(
                    values.posterior_mass_with_guided_lateral_events,
                ),
                conditional_mean_guided_lateral_events: values.weighted_guided_lateral_events
                    / values.posterior_mass,
                conditional_mean_candidate_marks: values.weighted_candidate_marks
                    / values.posterior_mass,
                conditional_mean_cumulative_log_prior_over_proposal: values
                    .weighted_cumulative_log_prior_over_proposal
                    / values.posterior_mass,
            },
        )
        .collect();
    Ok(BroadSatcomEventMarkGuideSeedSummary {
        positive_weight_particles,
        posterior_mass_with_eligible_lateral_events: normalized(mass_with_eligible),
        posterior_mass_with_guided_lateral_events: normalized(mass_with_guided),
        posterior_weighted_mean_eligible_lateral_events: normalized(eligible),
        posterior_weighted_mean_guided_lateral_events: normalized(guided),
        posterior_weighted_mean_candidate_marks: normalized(candidates),
        posterior_weighted_mean_finite_candidate_scores: normalized(finite_scores),
        posterior_weighted_mean_materialization_failures: normalized(materialization_failures),
        posterior_weighted_mean_proxy_projection_successes: normalized(proxy_successes),
        posterior_weighted_mean_proxy_projection_failures: normalized(proxy_failures),
        posterior_weighted_mean_proxy_projection_skipped_candidates: normalized(proxy_skipped),
        posterior_weighted_mean_all_scores_negative_infinity_events: normalized(
            all_negative_infinity,
        ),
        posterior_survivor_candidate_materialization_failure_fraction: positive_ratio(
            materialization_failures,
            candidates,
        ),
        posterior_survivor_proxy_projection_failure_fraction: positive_ratio(
            proxy_failures,
            proxy_successes + proxy_failures,
        ),
        posterior_survivor_proxy_projection_skipped_fraction: positive_ratio(
            proxy_skipped,
            candidates,
        ),
        posterior_survivor_all_scores_negative_infinity_event_fraction: positive_ratio(
            all_negative_infinity,
            guided,
        ),
        posterior_survivor_mean_selection_effective_sample_size_per_guided_event: positive_ratio(
            selection_effective_sample_size,
            guided,
        ),
        posterior_survivor_mean_selection_entropy_nats_per_guided_event: positive_ratio(
            selection_entropy,
            guided,
        ),
        minimum_observed_lead_seconds: minimum_lead,
        maximum_observed_lead_seconds: maximum_lead,
        minimum_selected_probability_across_positive_weight_lineages: minimum_selected_probability,
        maximum_selected_probability_across_positive_weight_lineages: maximum_selected_probability,
        minimum_event_log_prior_over_proposal_across_positive_weight_lineages:
            minimum_event_correction,
        maximum_event_log_prior_over_proposal_across_positive_weight_lineages:
            maximum_event_correction,
        posterior_weighted_mean_sum_log_candidate_count: normalized(sum_log_candidate_count),
        posterior_weighted_mean_sum_selected_log_probability: normalized(
            sum_selected_log_probability,
        ),
        posterior_weighted_mean_cumulative_log_prior_over_proposal: mean_correction,
        posterior_weighted_sd_cumulative_log_prior_over_proposal: (normalized(correction_squared)
            - mean_correction.powi(2))
        .max(0.0)
        .sqrt(),
        maximum_absolute_lineage_correction_recomposition_error: maximum_recomposition_error,
        strata,
    })
}

fn summarize_intermediate_potentials(
    checkpoints: &[IntermediatePotentialCheckpoint],
) -> BroadIntermediatePotentialSeedSummary {
    let points = checkpoints
        .iter()
        .flat_map(|checkpoint| &checkpoint.points)
        .collect::<Vec<_>>();
    let endpoint_pools = checkpoints
        .iter()
        .filter_map(|checkpoint| checkpoint.endpoint.candidate_pool.as_ref())
        .collect::<Vec<_>>();
    BroadIntermediatePotentialSeedSummary {
        bridged_epochs: checkpoints.len(),
        guide_points: points.len(),
        total_configured_candidates: points
            .iter()
            .map(|point| point.candidate_pool.configured_candidates)
            .sum(),
        total_generated_candidates: points
            .iter()
            .map(|point| point.candidate_pool.generated_candidates)
            .sum(),
        total_positive_candidates: points
            .iter()
            .map(|point| point.candidate_pool.positive_candidates)
            .sum(),
        minimum_candidate_effective_sample_size: points
            .iter()
            .map(|point| point.candidate_pool.candidate_effective_sample_size)
            .reduce(f64::min)
            .unwrap_or(0.0),
        maximum_candidate_weight: points
            .iter()
            .map(|point| point.candidate_pool.maximum_candidate_weight)
            .fold(0.0, f64::max),
        minimum_candidate_root_effective_sample_size: points
            .iter()
            .map(|point| point.candidate_pool.candidate_root_effective_sample_size)
            .reduce(f64::min)
            .unwrap_or(0.0),
        maximum_candidate_root_weight: points
            .iter()
            .map(|point| point.candidate_pool.maximum_candidate_root_weight)
            .fold(0.0, f64::max),
        minimum_guide_output_effective_sample_size: points
            .iter()
            .map(|point| point.output_effective_sample_size)
            .reduce(f64::min)
            .unwrap_or(0.0),
        minimum_guide_output_root_effective_sample_size: points
            .iter()
            .map(|point| point.output_root_effective_sample_size)
            .reduce(f64::min)
            .unwrap_or(0.0),
        minimum_endpoint_effective_sample_size: checkpoints
            .iter()
            .map(|checkpoint| checkpoint.endpoint.posterior_effective_sample_size)
            .reduce(f64::min)
            .unwrap_or(0.0),
        minimum_endpoint_root_effective_sample_size: checkpoints
            .iter()
            .map(|checkpoint| checkpoint.endpoint.root_effective_sample_size)
            .reduce(f64::min)
            .unwrap_or(0.0),
        maximum_absolute_output_resampling_log_correction: points
            .iter()
            .map(|point| point.candidate_pool.output_resampling_log_correction.abs())
            .fold(0.0, f64::max),
        endpoint_pool: (!endpoint_pools.is_empty()).then(|| {
            BroadIntermediatePotentialEndpointPoolSummary {
                pooled_epochs: endpoint_pools.len(),
                total_configured_candidates: endpoint_pools
                    .iter()
                    .map(|checkpoint| checkpoint.configured_candidates)
                    .sum(),
                total_generated_candidates: endpoint_pools
                    .iter()
                    .map(|checkpoint| checkpoint.generated_candidates)
                    .sum(),
                total_positive_candidates: endpoint_pools
                    .iter()
                    .map(|checkpoint| checkpoint.positive_candidates)
                    .sum(),
                minimum_candidate_effective_sample_size: endpoint_pools
                    .iter()
                    .map(|checkpoint| checkpoint.candidate_effective_sample_size)
                    .reduce(f64::min)
                    .unwrap_or(0.0),
                maximum_candidate_weight: endpoint_pools
                    .iter()
                    .map(|checkpoint| checkpoint.maximum_candidate_weight)
                    .fold(0.0, f64::max),
                minimum_candidate_root_effective_sample_size: endpoint_pools
                    .iter()
                    .map(|checkpoint| checkpoint.candidate_root_effective_sample_size)
                    .reduce(f64::min)
                    .unwrap_or(0.0),
                maximum_candidate_root_weight: endpoint_pools
                    .iter()
                    .map(|checkpoint| checkpoint.maximum_candidate_root_weight)
                    .fold(0.0, f64::max),
                maximum_absolute_output_resampling_log_correction: endpoint_pools
                    .iter()
                    .map(|checkpoint| checkpoint.output_resampling_log_correction.abs())
                    .fold(0.0, f64::max),
            }
        }),
    }
}

fn validate_global_transition_pool_diagnostics(
    realized: &[BroadRealizedGlobalTransitionPoolEpoch],
    result: &GlobalTransitionPoolFilterResult<BroadFlightState>,
) -> Result<()> {
    let expected = realized
        .iter()
        .filter_map(|epoch| match epoch.step {
            GlobalTransitionPoolStep::Standard => None,
            GlobalTransitionPoolStep::Pool {
                candidates_per_particle,
            } => Some((epoch, candidates_per_particle)),
        })
        .collect::<Vec<_>>();
    if expected.len() != result.transition_pool_checkpoints.len()
        || expected
            .iter()
            .zip(&result.transition_pool_checkpoints)
            .any(|((epoch, candidates_per_particle), checkpoint)| {
                epoch.observation_index != checkpoint.observation_index
                    || epoch.observation_time_s.to_bits() != checkpoint.observation_time_s.to_bits()
                    || *candidates_per_particle != checkpoint.candidates_per_particle
                    || (checkpoint.candidate_log_evidence_increment
                        + checkpoint.output_resampling_log_correction
                        - checkpoint.realized_log_evidence_increment)
                        .abs()
                        > 1.0e-10
            })
    {
        bail!("global transition-pool diagnostics do not match the realized observation schedule");
    }
    Ok(())
}

fn valid_split_diagnostics(
    first: Option<f64>,
    second: Option<f64>,
    absolute_difference: Option<f64>,
    root_total_variation: Option<f64>,
) -> bool {
    let expected_difference = first
        .zip(second)
        .map(|(first, second)| (first - second).abs());
    let difference_matches = match (expected_difference, absolute_difference) {
        (Some(expected), Some(actual)) => {
            actual.is_finite() && (expected - actual).abs() <= 1.0e-10
        }
        (None, None) => true,
        _ => false,
    };
    difference_matches
        && root_total_variation.is_some() == expected_difference.is_some()
        && match first {
            None => true,
            Some(value) => value.is_finite(),
        }
        && match second {
            None => true,
            Some(value) => value.is_finite(),
        }
        && match root_total_variation {
            None => true,
            Some(value) => value.is_finite() && (-1.0e-12..=1.0 + 1.0e-12).contains(&value),
        }
}

fn validate_root_stratified_transition_pool_diagnostics<S>(
    realized: &[BroadRealizedRootStratifiedTransitionPoolEpoch],
    result: &RootStratifiedTransitionPoolFilterResult<S>,
) -> Result<()> {
    let expected = realized
        .iter()
        .filter_map(|epoch| match epoch.step {
            RootStratifiedTransitionPoolStep::Standard => None,
            RootStratifiedTransitionPoolStep::Pool {
                candidates_per_positive_root,
            } => Some((epoch, candidates_per_positive_root)),
        })
        .collect::<Vec<_>>();
    if expected.len() != result.transition_pool_checkpoints.len()
        || expected.len() != result.root_stratified_candidate_pool_checkpoints.len()
    {
        bail!("root-stratified transition-pool diagnostics have an incomplete checkpoint ledger");
    }
    for (((epoch, candidates_per_positive_root), checkpoint), root_checkpoint) in expected
        .iter()
        .zip(&result.transition_pool_checkpoints)
        .zip(&result.root_stratified_candidate_pool_checkpoints)
    {
        let filter_checkpoint = result
            .pooled
            .checkpoints
            .get(epoch.observation_index)
            .context("root-stratified transition-pool checkpoint has no physical filter epoch")?;
        let common_header_matches = epoch.observation_index == checkpoint.observation_index
            && epoch.observation_index == root_checkpoint.observation_index
            && epoch.observation_time_s.to_bits() == checkpoint.observation_time_s.to_bits()
            && epoch.observation_time_s.to_bits() == root_checkpoint.observation_time_s.to_bits()
            && root_checkpoint.location == RootStratifiedCandidatePoolLocation::ObservationEndpoint
            && *candidates_per_positive_root == root_checkpoint.candidates_per_positive_root
            && checkpoint.candidates_per_particle == 0
            && checkpoint.configured_candidates == root_checkpoint.configured_candidates
            && checkpoint.generated_candidates == root_checkpoint.generated_candidates
            && checkpoint.positive_candidates <= checkpoint.generated_candidates
            && (checkpoint.candidate_log_evidence_increment
                + checkpoint.output_resampling_log_correction
                - checkpoint.realized_log_evidence_increment)
                .abs()
                <= 1.0e-10
            && filter_checkpoint.observation_time_s.to_bits() == epoch.observation_time_s.to_bits()
            && filter_checkpoint.observation_index == epoch.observation_index
            && (filter_checkpoint.log_evidence_increment
                - checkpoint.realized_log_evidence_increment)
                .abs()
                <= 1.0e-10
            && valid_split_diagnostics(
                root_checkpoint.first_split_candidate_log_evidence_increment,
                root_checkpoint.second_split_candidate_log_evidence_increment,
                root_checkpoint.absolute_split_log_evidence_difference,
                root_checkpoint.split_candidate_root_total_variation,
            );
        if !common_header_matches {
            bail!(
                "root-stratified transition-pool diagnostics do not match the realized physical observation"
            );
        }

        let mut configured_candidates = 0usize;
        let mut generated_candidates = 0usize;
        for root_stratum in &root_checkpoint.strata {
            let expected_candidates = root_stratum
                .input_positive_roots
                .checked_mul(*candidates_per_positive_root)
                .context("root-stratified transition-pool candidate count overflowed")?;
            configured_candidates = configured_candidates
                .checked_add(expected_candidates)
                .context("root-stratified transition-pool candidate count overflowed")?;
            generated_candidates = generated_candidates
                .checked_add(root_stratum.generated_candidates)
                .context("root-stratified transition-pool generated count overflowed")?;
            let ordinary_stratum = checkpoint
                .strata
                .iter()
                .find(|stratum| stratum.id == root_stratum.id)
                .context("root-stratified transition-pool stratum has no proper-weight ledger")?;
            let empty = root_stratum.input_positive_roots == 0;
            let stratum_matches = root_stratum.candidates_per_positive_root
                == *candidates_per_positive_root
                && root_stratum.generated_candidates == expected_candidates
                && root_stratum.roots_with_positive_candidates <= root_stratum.input_positive_roots
                && root_stratum.minimum_positive_candidates_per_root
                    <= root_stratum.maximum_positive_candidates_per_root
                && root_stratum.maximum_positive_candidates_per_root
                    <= *candidates_per_positive_root
                && (!empty
                    || (root_stratum.roots_with_positive_candidates == 0
                        && root_stratum.minimum_positive_candidates_per_root == 0
                        && root_stratum.maximum_positive_candidates_per_root == 0))
                && root_stratum
                    .minimum_within_root_candidate_effective_sample_size
                    .is_finite()
                && root_stratum.minimum_within_root_candidate_effective_sample_size >= 0.0
                && root_stratum
                    .median_within_root_candidate_effective_sample_size
                    .is_finite()
                && root_stratum.median_within_root_candidate_effective_sample_size >= 0.0
                && root_stratum
                    .maximum_within_root_candidate_weight
                    .is_finite()
                && (0.0..=1.0 + 1.0e-12)
                    .contains(&root_stratum.maximum_within_root_candidate_weight)
                && root_stratum.roots_with_maximum_candidate_weight_at_least_half
                    <= root_stratum.roots_with_positive_candidates
                && ordinary_stratum.input_positive_roots == root_stratum.input_positive_roots
                && ordinary_stratum.sampled_ancestor_roots == root_stratum.input_positive_roots
                && ordinary_stratum.configured_candidates == expected_candidates
                && ordinary_stratum.generated_candidates == root_stratum.generated_candidates
                && ordinary_stratum.ancestor_selection_guide.is_none()
                && ordinary_stratum.output_selection_guide.is_none()
                && valid_split_diagnostics(
                    root_stratum.first_split_log_predictive_mass,
                    root_stratum.second_split_log_predictive_mass,
                    root_stratum.absolute_split_log_predictive_mass_difference,
                    root_stratum.split_root_total_variation,
                );
            if !stratum_matches {
                bail!(
                    "root-stratified transition-pool diagnostics violate fixed per-root allocation"
                );
            }
        }
        if root_checkpoint.strata.len() != checkpoint.strata.len()
            || configured_candidates != root_checkpoint.configured_candidates
            || generated_candidates != root_checkpoint.generated_candidates
        {
            bail!(
                "root-stratified transition-pool aggregate counts do not match its stratum ledger"
            );
        }
    }
    Ok(())
}

fn validate_intermediate_potential_diagnostics<S>(
    realized: &[BroadRealizedIntermediatePotentialEpoch],
    pooled: &FilterResult<S>,
    checkpoints: &[IntermediatePotentialCheckpoint],
    forced_endpoint_pool_observation_indices: &[usize],
    outer_endpoint_log_corrections: &BTreeMap<usize, f64>,
) -> Result<()> {
    let expected = realized
        .iter()
        .filter_map(|epoch| match &epoch.step {
            IntermediatePotentialStep::Standard => None,
            IntermediatePotentialStep::Bridge { points } => Some((epoch, points, 1)),
            IntermediatePotentialStep::BridgeWithEndpointPool {
                points,
                endpoint_candidates_per_particle,
            } => Some((epoch, points, *endpoint_candidates_per_particle)),
        })
        .collect::<Vec<_>>();
    if expected.len() != checkpoints.len() {
        bail!("intermediate-potential diagnostics do not match the realized observation schedule");
    }
    for ((epoch, expected_points, endpoint_candidates_per_particle), checkpoint) in
        expected.iter().zip(checkpoints)
    {
        let endpoint_candidates_per_particle = *endpoint_candidates_per_particle;
        if epoch.observation_index != checkpoint.observation_index
            || epoch.observation_time_s.to_bits() != checkpoint.observation_time_s.to_bits()
            || expected_points.len() != checkpoint.points.len()
        {
            bail!(
                "intermediate-potential diagnostics do not match the realized observation schedule"
            );
        }
        let mut prior_time_s = epoch.observation_time_s - epoch.elapsed_seconds;
        for (point_index, (expected_point, point)) in
            expected_points.iter().zip(&checkpoint.points).enumerate()
        {
            let expected_time_s = expected_point.point.time.0;
            let candidate_pool = &point.candidate_pool;
            if point.point_index != point_index
                || point.point_time_s.to_bits() != expected_time_s.to_bits()
                || point.elapsed_seconds.to_bits() != (expected_time_s - prior_time_s).to_bits()
                || candidate_pool.observation_index != epoch.observation_index
                || candidate_pool.observation_time_s.to_bits() != expected_time_s.to_bits()
                || candidate_pool.candidates_per_particle != expected_point.candidates_per_particle
                || (candidate_pool.candidate_log_evidence_increment
                    + candidate_pool.output_resampling_log_correction
                    - candidate_pool.realized_log_evidence_increment)
                    .abs()
                    > 1.0e-10
            {
                bail!(
                    "intermediate-potential diagnostics do not match the realized observation schedule"
                );
            }
            prior_time_s = expected_time_s;
        }
        let expected_endpoint_elapsed_seconds = epoch.observation_time_s - prior_time_s;
        let recomposed_log_evidence = checkpoint
            .points
            .iter()
            .map(|point| point.candidate_pool.realized_log_evidence_increment)
            .sum::<f64>()
            + checkpoint.endpoint.log_evidence_increment;
        let forced_endpoint_pool =
            forced_endpoint_pool_observation_indices.contains(&epoch.observation_index);
        let outer_endpoint_log_correction = outer_endpoint_log_corrections
            .get(&epoch.observation_index)
            .copied()
            .unwrap_or(0.0);
        let endpoint_pool_matches = match &checkpoint.endpoint.candidate_pool {
            None => endpoint_candidates_per_particle == 1 && !forced_endpoint_pool,
            Some(candidate_pool)
                if endpoint_candidates_per_particle > 1 || forced_endpoint_pool =>
            {
                candidate_pool.observation_index == epoch.observation_index
                    && candidate_pool.observation_time_s.to_bits()
                        == epoch.observation_time_s.to_bits()
                    && candidate_pool.candidates_per_particle == endpoint_candidates_per_particle
                    && (candidate_pool.candidate_log_evidence_increment
                        + candidate_pool.output_resampling_log_correction
                        - candidate_pool.realized_log_evidence_increment)
                        .abs()
                        <= 1.0e-10
                    && (candidate_pool.realized_log_evidence_increment
                        + outer_endpoint_log_correction
                        - checkpoint.endpoint.log_evidence_increment)
                        .abs()
                        <= 1.0e-10
            }
            _ => false,
        };
        let filter_checkpoint_matches = pooled
            .checkpoints
            .iter()
            .find(|physical| physical.observation_index == epoch.observation_index)
            .is_some_and(|physical| {
                physical.observation_time_s.to_bits() == epoch.observation_time_s.to_bits()
                    && (physical.log_evidence_increment
                        - checkpoint.realized_log_evidence_increment)
                        .abs()
                        <= 1.0e-10
            });
        if checkpoint.endpoint.elapsed_seconds.to_bits()
            != expected_endpoint_elapsed_seconds.to_bits()
            || (recomposed_log_evidence - checkpoint.realized_log_evidence_increment).abs()
                > 1.0e-10
            || !endpoint_pool_matches
            || !filter_checkpoint_matches
        {
            bail!(
                "intermediate-potential diagnostics do not match the realized observation schedule"
            );
        }
    }
    Ok(())
}

fn validate_candidate_pool_selection_guide(
    checkpoint: &GlobalTransitionPoolCheckpoint,
    expected_guided: bool,
    potential_floor: f64,
) -> Result<()> {
    if (checkpoint.candidate_log_evidence_increment + checkpoint.output_resampling_log_correction
        - checkpoint.realized_log_evidence_increment)
        .abs()
        > 1.0e-10
    {
        bail!("fuel-selection candidate-pool evidence does not recompose exactly");
    }
    for stratum in &checkpoint.strata {
        let expects_ancestor = expected_guided && stratum.generated_candidates > 0;
        let expects_output = expected_guided && stratum.positive_candidates > 0;
        if stratum.ancestor_selection_guide.is_some() != expects_ancestor
            || stratum.output_selection_guide.is_some() != expects_output
        {
            bail!("fuel-selection diagnostics do not match the realized guide schedule");
        }
        for diagnostic in stratum
            .ancestor_selection_guide
            .iter()
            .chain(stratum.output_selection_guide.iter())
        {
            let minimum_allowed = potential_floor.ln() - 1.0e-12;
            if diagnostic.positive_target_states == 0
                || diagnostic.minimum_log_guide < minimum_allowed
                || diagnostic.maximum_log_guide > 1.0e-12
                || diagnostic.minimum_log_guide > diagnostic.maximum_log_guide
                || diagnostic.log_target_mean_guide < minimum_allowed
                || diagnostic.log_target_mean_guide > 1.0e-12
                || !diagnostic.proposal_effective_sample_size.is_finite()
                || !diagnostic.proposal_root_effective_sample_size.is_finite()
                || !diagnostic
                    .maximum_absolute_log_target_over_proposal
                    .is_finite()
            {
                bail!("fuel-selection proposal diagnostics violate the declared guide support");
            }
        }
    }
    Ok(())
}

fn validate_fuel_exhaustion_selection_guide_diagnostics(
    realized: &[BroadRealizedFuelExhaustionSelectionGuideEpoch],
    intermediate_realized: Option<&[BroadRealizedIntermediatePotentialEpoch]>,
    pooled: &FilterResult<BroadFlightState>,
    checkpoints: &BroadFuelExhaustionSelectionCheckpoints,
    potential_floor: f64,
) -> Result<()> {
    let is_bridge = |observation_index| {
        intermediate_realized
            .and_then(|epochs| {
                epochs
                    .iter()
                    .find(|epoch| epoch.observation_index == observation_index)
            })
            .is_some_and(|epoch| {
                matches!(
                    epoch.step,
                    IntermediatePotentialStep::Bridge { .. }
                        | IntermediatePotentialStep::BridgeWithEndpointPool { .. }
                )
            })
    };
    let expected_standard = realized
        .iter()
        .filter(|epoch| {
            matches!(epoch.step, SelectionGuideStep::Guide { .. })
                && !is_bridge(epoch.observation_index)
        })
        .collect::<Vec<_>>();
    if expected_standard.len() != checkpoints.guided_standard.len() {
        bail!("guided standard checkpoints do not match the realized guide schedule");
    }
    for (epoch, checkpoint) in expected_standard.iter().zip(&checkpoints.guided_standard) {
        let physical_matches = pooled
            .checkpoints
            .iter()
            .find(|physical| physical.observation_index == epoch.observation_index)
            .is_some_and(|physical| {
                physical.observation_time_s.to_bits() == epoch.observation_time_s.to_bits()
                    && (physical.log_evidence_increment
                        - checkpoint.realized_log_evidence_increment)
                        .abs()
                        <= 1.0e-10
            });
        if checkpoint.observation_index != epoch.observation_index
            || checkpoint.observation_time_s.to_bits() != epoch.observation_time_s.to_bits()
            || checkpoint.candidates_per_particle != 1
            || !physical_matches
        {
            bail!("guided standard checkpoints do not match the realized guide schedule");
        }
        validate_candidate_pool_selection_guide(checkpoint, true, potential_floor)?;
    }

    for checkpoint in &checkpoints.intermediate_potential {
        let epoch = realized
            .iter()
            .find(|epoch| epoch.observation_index == checkpoint.observation_index)
            .context("intermediate checkpoint has no fuel-selection schedule entry")?;
        let guided = matches!(epoch.step, SelectionGuideStep::Guide { .. });
        for point in &checkpoint.points {
            validate_candidate_pool_selection_guide(
                &point.candidate_pool,
                guided,
                potential_floor,
            )?;
        }
        match &checkpoint.endpoint.candidate_pool {
            Some(pool) => validate_candidate_pool_selection_guide(pool, guided, potential_floor)?,
            None if guided => {
                bail!("guided intermediate endpoint omitted its exact proposal correction")
            }
            None => {}
        }
    }
    let expected_guided_bridges = realized
        .iter()
        .filter(|epoch| {
            matches!(epoch.step, SelectionGuideStep::Guide { .. })
                && is_bridge(epoch.observation_index)
        })
        .count();
    let actual_guided_bridges = checkpoints
        .intermediate_potential
        .iter()
        .filter(|checkpoint| {
            realized.iter().any(|epoch| {
                epoch.observation_index == checkpoint.observation_index
                    && matches!(epoch.step, SelectionGuideStep::Guide { .. })
            })
        })
        .count();
    if expected_guided_bridges != actual_guided_bridges {
        bail!("guided bridge checkpoints do not match the realized guide schedule");
    }
    Ok(())
}

fn selection_guide_distribution_diagnostics<'a>(
    checkpoints: &'a BroadFuelExhaustionSelectionCheckpoints,
) -> Vec<&'a SelectionGuideDistributionDiagnostics> {
    let mut diagnostics = Vec::new();
    let mut collect_pool = |pool: &'a GlobalTransitionPoolCheckpoint| {
        for stratum in &pool.strata {
            diagnostics.extend(stratum.ancestor_selection_guide.iter());
            diagnostics.extend(stratum.output_selection_guide.iter());
        }
    };
    for checkpoint in &checkpoints.guided_standard {
        collect_pool(checkpoint);
    }
    for checkpoint in &checkpoints.intermediate_potential {
        for point in &checkpoint.points {
            collect_pool(&point.candidate_pool);
        }
        if let Some(endpoint) = &checkpoint.endpoint.candidate_pool {
            collect_pool(endpoint);
        }
    }
    diagnostics
}

fn fuel_selection_outcomes() -> [BroadFuelExhaustionSelectionGuideOutcome; 6] {
    use BroadFuelExhaustionSelectionGuideOutcome as Outcome;
    [
        Outcome::Compatible,
        Outcome::OutsideWindow,
        Outcome::NoExhaustionByBound,
        Outcome::AlreadyExhausted,
        Outcome::InactiveParticle,
        Outcome::FuelModelUnavailable,
    ]
}

const fn fuel_selection_outcome_index(outcome: BroadFuelExhaustionSelectionGuideOutcome) -> usize {
    use BroadFuelExhaustionSelectionGuideOutcome as Outcome;
    match outcome {
        Outcome::Compatible => 0,
        Outcome::OutsideWindow => 1,
        Outcome::NoExhaustionByBound => 2,
        Outcome::AlreadyExhausted => 3,
        Outcome::InactiveParticle => 4,
        Outcome::FuelModelUnavailable => 5,
    }
}

fn visit_positive_weight_slots<S>(
    states: &[S],
    log_weights: &[f64],
    root_ids: &[usize],
    mut visit: impl FnMut(usize, &S, f64, usize) -> Result<()>,
) -> Result<usize> {
    if states.len() != log_weights.len() || states.len() != root_ids.len() {
        bail!("fuel-selection posterior vectors have inconsistent lengths");
    }
    let mut positive_weight_slots = 0usize;
    for (slot, ((state, &log_weight), &root)) in
        states.iter().zip(log_weights).zip(root_ids).enumerate()
    {
        if !log_weight.is_finite() {
            continue;
        }
        positive_weight_slots += 1;
        visit(slot, state, log_weight.exp(), root)?;
    }
    Ok(positive_weight_slots)
}

fn evaluate_fuel_exhaustion_selection_posterior(
    seed: u64,
    guide: &BroadFuelExhaustionSelectionGuide,
    model: &BroadFlightModel<'_>,
    endpoint: &BroadFlightObservation,
    point: BroadFuelExhaustionSelectionGuidePoint,
    result: &FilterResult<BroadFlightState>,
) -> Result<BroadFuelExhaustionPosteriorPopulation> {
    let mut outcome_slots = [0usize; 6];
    let mut outcome_mass = [0.0_f64; 6];
    let mut compatible_root_masses = BTreeMap::<usize, f64>::new();
    let mut compatible_root_masses_by_stratum = BTreeMap::<u32, BTreeMap<usize, f64>>::new();
    let mut compatible_slots_by_stratum = BTreeMap::<u32, usize>::new();
    let mut compatible_projected_min = f64::INFINITY;
    let mut compatible_projected_max = f64::NEG_INFINITY;
    let mut compatible_projected_weighted_sum = 0.0;
    let mut compatible_positive_weight_slots = 0usize;
    let positive_weight_slots = visit_positive_weight_slots(
        &result.particles,
        &result.log_weights,
        &result.root_ids,
        |slot, state, weight, root| {
            let evaluation = guide
                .evaluate(model, state, endpoint, &point)
                .map_err(anyhow::Error::new)
                .with_context(|| format!("cannot evaluate fuel guide at retained slot {slot}"))?;
            let index = fuel_selection_outcome_index(evaluation.outcome);
            outcome_slots[index] += 1;
            outcome_mass[index] += weight;
            if matches!(
                evaluation.outcome,
                BroadFuelExhaustionSelectionGuideOutcome::Compatible
            ) {
                compatible_positive_weight_slots += 1;
                *compatible_root_masses.entry(root).or_default() += weight;
                *compatible_root_masses_by_stratum
                    .entry(state.stratum.0)
                    .or_default()
                    .entry(root)
                    .or_default() += weight;
                *compatible_slots_by_stratum
                    .entry(state.stratum.0)
                    .or_default() += 1;
                if weight > 0.0 {
                    let projected = evaluation
                        .projected_dual_engine_exhaustion_time
                        .context("compatible fuel-guide outcome has no projected exhaustion time")?
                        .0;
                    compatible_projected_min = compatible_projected_min.min(projected);
                    compatible_projected_max = compatible_projected_max.max(projected);
                    compatible_projected_weighted_sum += weight * projected;
                }
            }
            Ok(())
        },
    )?;
    let total_mass = outcome_mass.iter().sum::<f64>();
    if !total_mass.is_finite() || (total_mass - 1.0).abs() > 1.0e-8 {
        bail!("fuel-selection posterior outcome masses are not normalized");
    }
    let compatible_mass = outcome_mass[0];
    let compatible_root_sum_squares = compatible_root_masses
        .values()
        .map(|mass| mass.powi(2))
        .sum::<f64>();
    let maximum_compatible_root_mass = compatible_root_masses
        .values()
        .copied()
        .fold(0.0_f64, f64::max);
    let positive_compatible = compatible_mass > 0.0 && compatible_root_sum_squares > 0.0;
    let compatible_strata = result
        .checkpoints
        .last()
        .context("fuel-selection posterior has no filter checkpoint")?
        .strata
        .iter()
        .filter(|diagnostic| diagnostic.posterior_mass > 0.0)
        .map(|diagnostic| {
            let stratum = diagnostic.id.0;
            let empty = BTreeMap::new();
            let roots = compatible_root_masses_by_stratum
                .get(&stratum)
                .unwrap_or(&empty);
            let mass = roots.values().sum::<f64>();
            let sum_squares = roots.values().map(|value| value.powi(2)).sum::<f64>();
            BroadFuelExhaustionCompatibleStratumSummary {
                stratum,
                compatible_positive_weight_slots: compatible_slots_by_stratum
                    .get(&stratum)
                    .copied()
                    .unwrap_or(0),
                distinct_compatible_seed_local_roots: roots.len(),
                compatible_physical_posterior_mass: mass,
                compatible_physical_root_effective_sample_size: (sum_squares > 0.0)
                    .then_some(mass.powi(2) / sum_squares),
                maximum_compatible_physical_root_weight: (mass > 0.0)
                    .then(|| roots.values().copied().fold(0.0_f64, f64::max) / mass),
            }
        })
        .collect::<Vec<_>>();
    let outcomes = fuel_selection_outcomes()
        .into_iter()
        .enumerate()
        .map(|(index, outcome)| BroadFuelExhaustionOutcomeSummary {
            outcome,
            retained_slots: outcome_slots[index],
            posterior_mass: outcome_mass[index],
        })
        .collect();
    Ok(BroadFuelExhaustionPosteriorPopulation {
        seed,
        summary: BroadFuelExhaustionPosteriorSummary {
            retained_slots: result.particles.len(),
            positive_weight_slots,
            zero_weight_placeholder_slots: result.particles.len() - positive_weight_slots,
            outcomes,
            compatible_retained_slot_fraction: outcome_slots[0] as f64
                / result.particles.len() as f64,
            compatible_positive_weight_slots,
            compatible_positive_weight_slot_fraction: compatible_positive_weight_slots as f64
                / positive_weight_slots as f64,
            distinct_compatible_seed_local_roots: compatible_root_masses.len(),
            compatible_posterior_mass: compatible_mass,
            compatible_root_effective_sample_size: positive_compatible
                .then_some(compatible_mass.powi(2) / compatible_root_sum_squares),
            maximum_compatible_root_weight: positive_compatible
                .then_some(maximum_compatible_root_mass / compatible_mass),
            compatible_projected_exhaustion_time_min_s: positive_compatible
                .then_some(compatible_projected_min),
            compatible_projected_exhaustion_time_mean_s: positive_compatible
                .then_some(compatible_projected_weighted_sum / compatible_mass),
            compatible_projected_exhaustion_time_max_s: positive_compatible
                .then_some(compatible_projected_max),
            compatible_strata,
        },
        compatible_root_masses: compatible_root_masses.into_values().collect(),
        compatible_root_masses_by_stratum: compatible_root_masses_by_stratum
            .into_iter()
            .map(|(stratum, roots)| (stratum, roots.into_values().collect()))
            .collect(),
    })
}

fn summarize_fuel_exhaustion_selection_guide(
    realized: &[BroadRealizedFuelExhaustionSelectionGuideEpoch],
    intermediate_realized: Option<&[BroadRealizedIntermediatePotentialEpoch]>,
    checkpoints: &BroadFuelExhaustionSelectionCheckpoints,
    final_posterior: BroadFuelExhaustionPosteriorSummary,
) -> BroadFuelExhaustionSelectionGuideSeedSummary {
    let diagnostics = selection_guide_distribution_diagnostics(checkpoints);
    let is_bridge = |index| {
        intermediate_realized.is_some_and(|epochs| {
            epochs.iter().any(|epoch| {
                epoch.observation_index == index
                    && matches!(
                        epoch.step,
                        IntermediatePotentialStep::Bridge { .. }
                            | IntermediatePotentialStep::BridgeWithEndpointPool { .. }
                    )
            })
        })
    };
    let guided_epochs = realized
        .iter()
        .filter(|epoch| matches!(epoch.step, SelectionGuideStep::Guide { .. }))
        .collect::<Vec<_>>();
    BroadFuelExhaustionSelectionGuideSeedSummary {
        guided_epochs: guided_epochs.len(),
        guided_standard_epochs: guided_epochs
            .iter()
            .filter(|epoch| !is_bridge(epoch.observation_index))
            .count(),
        guided_bridge_epochs: guided_epochs
            .iter()
            .filter(|epoch| is_bridge(epoch.observation_index))
            .count(),
        selection_distribution_evaluations: diagnostics.len(),
        minimum_log_guide: diagnostics
            .iter()
            .map(|diagnostic| diagnostic.minimum_log_guide)
            .reduce(f64::min)
            .unwrap_or(0.0),
        maximum_log_guide: diagnostics
            .iter()
            .map(|diagnostic| diagnostic.maximum_log_guide)
            .reduce(f64::max)
            .unwrap_or(0.0),
        minimum_proposal_effective_sample_size: diagnostics
            .iter()
            .map(|diagnostic| diagnostic.proposal_effective_sample_size)
            .reduce(f64::min)
            .unwrap_or(0.0),
        maximum_proposal_probability: diagnostics
            .iter()
            .map(|diagnostic| diagnostic.maximum_proposal_probability)
            .fold(0.0, f64::max),
        minimum_proposal_root_effective_sample_size: diagnostics
            .iter()
            .map(|diagnostic| diagnostic.proposal_root_effective_sample_size)
            .reduce(f64::min)
            .unwrap_or(0.0),
        maximum_proposal_root_probability: diagnostics
            .iter()
            .map(|diagnostic| diagnostic.maximum_proposal_root_probability)
            .fold(0.0, f64::max),
        maximum_absolute_log_target_over_proposal: diagnostics
            .iter()
            .map(|diagnostic| diagnostic.maximum_absolute_log_target_over_proposal)
            .fold(0.0, f64::max),
        final_posterior,
    }
}

fn validate_persistent_twist_diagnostics<S>(
    realized: &[BroadRealizedFuelExhaustionPersistentTwistEpoch],
    intermediate_realized: Option<&[BroadRealizedIntermediatePotentialEpoch]>,
    result: &FilterResult<S>,
    diagnostics: &BroadPersistentTwistExecutionDiagnostics,
) -> Result<BroadPersistentTwistEvidenceRecomposition> {
    if realized.len() != result.checkpoints.len() {
        bail!("persistent-twist lifecycle does not align with filter checkpoints");
    }
    let active = realized
        .iter()
        .filter_map(|epoch| match epoch.step {
            PersistentTwistStep::Inactive => None,
            PersistentTwistStep::Activate { .. } => Some((epoch, PersistentTwistPhase::Activate)),
            PersistentTwistStep::Continue { .. } => Some((epoch, PersistentTwistPhase::Continue)),
            PersistentTwistStep::Finalize { .. } => Some((epoch, PersistentTwistPhase::Finalize)),
        })
        .collect::<Vec<_>>();
    if active.len() != diagnostics.checkpoints.len() {
        bail!("persistent-twist wrapper checkpoints do not match the realized lifecycle");
    }
    let mut maximum_wrapper_difference = 0.0_f64;
    for ((epoch, phase), checkpoint) in active.iter().zip(&diagnostics.checkpoints) {
        let filter_checkpoint = &result.checkpoints[epoch.observation_index];
        maximum_wrapper_difference = maximum_wrapper_difference.max(
            (checkpoint.filter_checkpoint_log_evidence_increment
                - filter_checkpoint.log_evidence_increment)
                .abs(),
        );
        if checkpoint.observation_index != epoch.observation_index
            || checkpoint.observation_time_s.to_bits() != epoch.observation_time_s.to_bits()
            || checkpoint.phase != *phase
            || checkpoint.output_is_twisted != (*phase != PersistentTwistPhase::Finalize)
            || (checkpoint.filter_checkpoint_log_evidence_increment
                - filter_checkpoint.log_evidence_increment)
                .abs()
                > 1.0e-10
        {
            bail!("persistent-twist wrapper checkpoint does not match the physical ledger");
        }
    }
    let expected_twisted_indices = active
        .iter()
        .filter(|(_, phase)| *phase != PersistentTwistPhase::Finalize)
        .map(|(epoch, _)| epoch.observation_index)
        .collect::<Vec<_>>();
    if diagnostics.twisted_filtering_observation_indices != expected_twisted_indices {
        bail!("persistent-twist retained-target index ledger is inconsistent");
    }
    let is_bridge = |index| {
        intermediate_realized.is_some_and(|epochs| {
            epochs.iter().any(|epoch| {
                epoch.observation_index == index
                    && matches!(
                        epoch.step,
                        IntermediatePotentialStep::Bridge { .. }
                            | IntermediatePotentialStep::BridgeWithEndpointPool { .. }
                    )
            })
        })
    };
    let expected_twisted_standard = active
        .iter()
        .filter(|(epoch, _)| !is_bridge(epoch.observation_index))
        .collect::<Vec<_>>();
    if expected_twisted_standard.len() != diagnostics.twisted_standard_checkpoints.len() {
        bail!("persistent-twist standard-pool checkpoints do not match the lifecycle");
    }
    for ((epoch, _), checkpoint) in expected_twisted_standard
        .iter()
        .zip(&diagnostics.twisted_standard_checkpoints)
    {
        let wrapper = diagnostics
            .checkpoints
            .iter()
            .find(|entry| entry.observation_index == epoch.observation_index)
            .expect("active epoch has a validated wrapper checkpoint");
        if checkpoint.observation_index != epoch.observation_index
            || checkpoint.observation_time_s.to_bits() != epoch.observation_time_s.to_bits()
            || checkpoint.candidates_per_particle != 1
            || (checkpoint.realized_log_evidence_increment
                - wrapper.twisted_target_log_evidence_increment)
                .abs()
                > 1.0e-10
        {
            bail!("persistent-twist standard-pool diagnostics are inconsistent");
        }
    }
    let finalizations = diagnostics
        .checkpoints
        .iter()
        .filter(|checkpoint| checkpoint.phase == PersistentTwistPhase::Finalize)
        .collect::<Vec<_>>();
    if !active.is_empty() && finalizations.len() != 1 {
        bail!("active persistent twist requires one exact final untwist");
    }
    if let Some(finalization) = finalizations.first() {
        let final_checkpoint = result
            .checkpoints
            .last()
            .context("persistent-twist run has no final filter checkpoint")?;
        if finalization.observation_index != final_checkpoint.observation_index
            || finalization.output_is_twisted
            || finalization.final_untwist_log_evidence_correction.is_none()
            || (final_checkpoint.posterior_ess
                - finalization
                    .population
                    .implied_untwisted_effective_sample_size)
                .abs()
                > 1.0e-8
            || (final_checkpoint.root_effective_sample_size
                - finalization
                    .population
                    .implied_untwisted_root_effective_sample_size)
                .abs()
                > 1.0e-8
        {
            bail!("persistent-twist final output is not the ordinary physical filter");
        }
    }
    let inactive_increment_sum = realized
        .iter()
        .filter(|epoch| matches!(epoch.step, PersistentTwistStep::Inactive))
        .map(|epoch| result.checkpoints[epoch.observation_index].log_evidence_increment)
        .sum::<f64>();
    let active_twisted_increment_sum = diagnostics
        .checkpoints
        .iter()
        .map(|checkpoint| checkpoint.twisted_target_log_evidence_increment)
        .sum::<f64>();
    let final_correction = finalizations
        .first()
        .and_then(|checkpoint| checkpoint.final_untwist_log_evidence_correction)
        .unwrap_or(0.0);
    let recomposed = result.initial_log_evidence
        + inactive_increment_sum
        + active_twisted_increment_sum
        + final_correction;
    let generic_recomposed = result.initial_log_evidence
        + result
            .checkpoints
            .iter()
            .map(|checkpoint| checkpoint.log_evidence_increment)
            .sum::<f64>();
    if (recomposed - result.log_evidence).abs() > 1.0e-9
        || (generic_recomposed - result.log_evidence).abs() > 1.0e-9
        || maximum_wrapper_difference > 1.0e-10
    {
        bail!("persistent-twist physical evidence does not recompose exactly");
    }
    let snapshot = result
        .snapshots
        .last()
        .context("persistent-twist run did not retain its final snapshot")?;
    if snapshot.observation_index
        != result
            .checkpoints
            .last()
            .map(|value| value.observation_index)
        || snapshot.log_weights != result.log_weights
    {
        bail!("persistent-twist final snapshot is not the untwisted physical population");
    }
    Ok(BroadPersistentTwistEvidenceRecomposition {
        initial_log_evidence: result.initial_log_evidence,
        inactive_physical_log_evidence_increment_sum: inactive_increment_sum,
        active_twisted_target_log_evidence_increment_sum: active_twisted_increment_sum,
        final_global_untwist_log_evidence_correction: final_correction,
        recomposed_final_physical_log_evidence: recomposed,
        reported_final_physical_log_evidence: result.log_evidence,
        maximum_absolute_wrapper_vs_filter_checkpoint_increment_difference:
            maximum_wrapper_difference,
    })
}

fn summarize_fuel_exhaustion_persistent_twist(
    realized: &[BroadRealizedFuelExhaustionPersistentTwistEpoch],
    intermediate_realized: Option<&[BroadRealizedIntermediatePotentialEpoch]>,
    diagnostics: &BroadPersistentTwistExecutionDiagnostics,
    final_posterior: BroadFuelExhaustionPosteriorSummary,
) -> BroadFuelExhaustionPersistentTwistSeedSummary {
    let is_bridge = |index| {
        intermediate_realized.is_some_and(|epochs| {
            epochs.iter().any(|epoch| {
                epoch.observation_index == index
                    && matches!(
                        epoch.step,
                        IntermediatePotentialStep::Bridge { .. }
                            | IntermediatePotentialStep::BridgeWithEndpointPool { .. }
                    )
            })
        })
    };
    let active = realized
        .iter()
        .filter(|epoch| !matches!(epoch.step, PersistentTwistStep::Inactive))
        .collect::<Vec<_>>();
    BroadFuelExhaustionPersistentTwistSeedSummary {
        active_epochs: active.len(),
        continue_epochs: active
            .iter()
            .filter(|epoch| matches!(epoch.step, PersistentTwistStep::Continue { .. }))
            .count(),
        twisted_standard_epochs: active
            .iter()
            .filter(|epoch| !is_bridge(epoch.observation_index))
            .count(),
        twisted_bridge_epochs: active
            .iter()
            .filter(|epoch| is_bridge(epoch.observation_index))
            .count(),
        minimum_twisted_effective_sample_size: diagnostics
            .checkpoints
            .iter()
            .map(|checkpoint| checkpoint.population.twisted_effective_sample_size)
            .reduce(f64::min)
            .unwrap_or(0.0),
        minimum_implied_physical_effective_sample_size: diagnostics
            .checkpoints
            .iter()
            .map(|checkpoint| {
                checkpoint
                    .population
                    .implied_untwisted_effective_sample_size
            })
            .reduce(f64::min)
            .unwrap_or(0.0),
        minimum_twisted_root_effective_sample_size: diagnostics
            .checkpoints
            .iter()
            .map(|checkpoint| checkpoint.population.twisted_root_effective_sample_size)
            .reduce(f64::min)
            .unwrap_or(0.0),
        minimum_implied_physical_root_effective_sample_size: diagnostics
            .checkpoints
            .iter()
            .map(|checkpoint| {
                checkpoint
                    .population
                    .implied_untwisted_root_effective_sample_size
            })
            .reduce(f64::min)
            .unwrap_or(0.0),
        maximum_twisted_root_weight: diagnostics
            .checkpoints
            .iter()
            .map(|checkpoint| checkpoint.population.twisted_maximum_root_weight)
            .fold(0.0, f64::max),
        maximum_implied_physical_root_weight: diagnostics
            .checkpoints
            .iter()
            .map(|checkpoint| checkpoint.population.implied_untwisted_maximum_root_weight)
            .fold(0.0, f64::max),
        final_global_untwist_log_evidence_correction: diagnostics
            .checkpoints
            .iter()
            .find(|checkpoint| checkpoint.phase == PersistentTwistPhase::Finalize)
            .and_then(|checkpoint| checkpoint.final_untwist_log_evidence_correction),
        final_output_is_ordinary_physical_filter: match diagnostics.checkpoints.last() {
            None => true,
            Some(checkpoint) => !checkpoint.output_is_twisted,
        },
        final_posterior,
    }
}

struct BroadSeedInferenceSummaries {
    island_smc: Option<BroadIslandSeedSummary>,
    global_transition_pool_smc: Option<BroadGlobalTransitionPoolSeedSummary>,
    root_stratified_transition_pool_smc: Option<BroadRootStratifiedTransitionPoolSeedSummary>,
    satcom_event_mark_guide: Option<BroadSatcomEventMarkGuideSeedSummary>,
    pending_renewal_refresh: Option<BroadPendingRenewalRefreshSeedSummary>,
    intermediate_satcom_bridge_smc: Option<BroadIntermediatePotentialSeedSummary>,
    fuel_exhaustion_selection_guide_smc: Option<BroadFuelExhaustionSelectionGuideSeedSummary>,
    fuel_exhaustion_persistent_twist_smc: Option<BroadFuelExhaustionPersistentTwistSeedSummary>,
}

fn summarize(
    family: &str,
    seed: u64,
    result: &FilterResult<BroadFlightState>,
    posterior_state_diversity: BroadPosteriorStateDiversity,
    inference: BroadSeedInferenceSummaries,
) -> BroadSeedSummary {
    let mut mean_latitude_deg = 0.0;
    let mut mean_longitude_deg = 0.0;
    let mut mean_lateral_events = 0.0;
    let mut mean_speed_events = 0.0;
    let mut mean_altitude_events = 0.0;
    let mut mean_fuel_anchor_mass_adjustment_kg = 0.0;
    let mut mean_fuel_flow_scale = 0.0;
    let mut mean_fuel_flow_scale_squared = 0.0;
    let mut fuel_exhausted_by_checkpoint_mass = 0.0;
    let mut mean_powered_additional_drag_required_segments = 0.0;
    let mut maximum_weight = 0.0_f64;
    let mut positive_weight_particles = 0;
    for (state, &log_weight) in result.particles.iter().zip(&result.log_weights) {
        let weight = log_weight.exp();
        if weight > 0.0 {
            positive_weight_particles += 1;
        }
        maximum_weight = maximum_weight.max(weight);
        mean_latitude_deg += weight * state.powered_flight.aircraft.position.latitude.0;
        mean_longitude_deg += weight * state.powered_flight.aircraft.position.longitude.0;
        mean_lateral_events += weight * state.powered_flight.event_counters.lateral as f64;
        mean_speed_events += weight * state.powered_flight.event_counters.speed as f64;
        mean_altitude_events += weight * state.powered_flight.event_counters.altitude as f64;
        mean_fuel_anchor_mass_adjustment_kg += weight
            * state
                .diagnostics
                .last_fuel_anchor_mass_adjustment_kg
                .unwrap_or(0.0);
        mean_fuel_flow_scale += weight * state.fuel_flow_scale;
        mean_fuel_flow_scale_squared += weight * state.fuel_flow_scale.powi(2);
        if state.fuel.dual_engine_exhaustion_time.is_some() {
            fuel_exhausted_by_checkpoint_mass += weight;
        }
        mean_powered_additional_drag_required_segments +=
            weight * state.diagnostics.powered_additional_drag_required_segments as f64;
    }
    let final_checkpoint = result
        .checkpoints
        .last()
        .expect("a broad run always contains at least one observation");
    let dominant = final_checkpoint
        .strata
        .iter()
        .max_by(|first, second| first.posterior_mass.total_cmp(&second.posterior_mass))
        .expect("a stratified broad run always reports strata");
    BroadSeedSummary {
        family: family.to_string(),
        seed,
        configured_particles: result.particles.len(),
        positive_weight_particles,
        effective_sample_size: effective_sample_size(&result.log_weights),
        maximum_weight,
        distinct_prior_roots: final_checkpoint.distinct_root_ancestors,
        prior_root_effective_sample_size: final_checkpoint.root_effective_sample_size,
        maximum_prior_root_weight: final_checkpoint.maximum_root_weight,
        prior_roots_with_mass_at_least_1e_6: final_checkpoint.roots_with_mass_at_least_1e_6,
        prior_roots_with_mass_at_least_1e_3: final_checkpoint.roots_with_mass_at_least_1e_3,
        posterior_state_diversity,
        nonzero_posterior_strata: final_checkpoint
            .strata
            .iter()
            .filter(|stratum| stratum.posterior_mass > 0.0)
            .count(),
        dominant_stratum: dominant.id.0,
        dominant_stratum_mass: dominant.posterior_mass,
        log_evidence: result.log_evidence,
        mean_latitude_deg,
        mean_longitude_deg,
        rejection_counts: BroadRejectionCounts::from_states(&result.particles),
        mean_lateral_events,
        mean_speed_events,
        mean_altitude_events,
        mean_fuel_anchor_mass_adjustment_kg,
        mean_fuel_flow_scale,
        fuel_flow_scale_sd: (mean_fuel_flow_scale_squared - mean_fuel_flow_scale.powi(2))
            .max(0.0)
            .sqrt(),
        fuel_exhausted_by_checkpoint_mass,
        mean_powered_additional_drag_required_segments,
        island_smc: inference.island_smc,
        global_transition_pool_smc: inference.global_transition_pool_smc,
        root_stratified_transition_pool_smc: inference.root_stratified_transition_pool_smc,
        satcom_event_mark_guide: inference.satcom_event_mark_guide,
        pending_renewal_refresh: inference.pending_renewal_refresh,
        intermediate_satcom_bridge_smc: inference.intermediate_satcom_bridge_smc,
        fuel_exhaustion_selection_guide_smc: inference.fuel_exhaustion_selection_guide_smc,
        fuel_exhaustion_persistent_twist_smc: inference.fuel_exhaustion_persistent_twist_smc,
    }
}

const POSTERIOR_DIAGNOSTIC_CSV_HEADER: &str = "target_mach,target_pressure_altitude_ft,integration_segments,powered_target_clamp_count,powered_boundary_stall_or_minimum_mach_floor_s,powered_boundary_vmo_or_mmo_ceiling_s,powered_boundary_bank_s,powered_boundary_roll_rate_s,powered_boundary_climb_rate_s,powered_boundary_descent_rate_s,powered_boundary_vertical_acceleration_s,powered_boundary_lower_altitude_s,powered_boundary_upper_altitude_s,powered_boundary_magnetic_altitude_clamp_s,fuel_outside_martin_domain_seconds,fuel_flow_multiplier_bound_hits,powered_thrust_proxy_extrapolation_segments,powered_thrust_proxy_cap_segments,powered_additional_drag_required_segments,satcom_event_mark_guide_eligible_lateral_events,satcom_event_mark_guide_guided_lateral_events,satcom_event_mark_guide_candidate_marks,satcom_event_mark_guide_finite_candidate_scores,satcom_event_mark_guide_materialization_failures,satcom_event_mark_guide_proxy_projection_successes,satcom_event_mark_guide_proxy_projection_failures,satcom_event_mark_guide_proxy_projection_skipped_candidates,satcom_event_mark_guide_all_scores_negative_infinity_events,satcom_event_mark_guide_sum_selection_effective_sample_size,satcom_event_mark_guide_sum_selection_entropy_nats,satcom_event_mark_guide_minimum_selected_probability,satcom_event_mark_guide_maximum_selected_probability,satcom_event_mark_guide_minimum_event_log_prior_over_proposal,satcom_event_mark_guide_maximum_event_log_prior_over_proposal,satcom_event_mark_guide_minimum_lead_seconds,satcom_event_mark_guide_maximum_lead_seconds,satcom_event_mark_guide_sum_log_candidate_count,satcom_event_mark_guide_sum_selected_log_probability,satcom_event_mark_guide_cumulative_log_prior_over_proposal,satcom_event_mark_guide_sum_minimum_log_prior_over_proposal,satcom_event_mark_guide_sum_maximum_log_prior_over_proposal";

fn optional_csv_f64(value: Option<f64>) -> String {
    value
        .map(|value| format!("{value:.17e}"))
        .unwrap_or_default()
}

fn posterior_diagnostic_csv_suffix(
    target_mach: f64,
    target_pressure_altitude_ft: f64,
    diagnostics: BroadFlightDiagnostics,
) -> String {
    let boundary = diagnostics.powered_boundary_seconds;
    let guide = diagnostics.satcom_event_mark_guide;
    let fields = vec![
        format!("{target_mach:.12}"),
        format!("{target_pressure_altitude_ft:.6}"),
        diagnostics.integration_segments.to_string(),
        diagnostics.powered_target_clamp_count.to_string(),
        format!("{:.9}", boundary.stall_or_minimum_mach_floor),
        format!("{:.9}", boundary.vmo_or_mmo_ceiling),
        format!("{:.9}", boundary.bank),
        format!("{:.9}", boundary.roll_rate),
        format!("{:.9}", boundary.climb_rate),
        format!("{:.9}", boundary.descent_rate),
        format!("{:.9}", boundary.vertical_acceleration),
        format!("{:.9}", boundary.lower_altitude),
        format!("{:.9}", boundary.upper_altitude),
        format!("{:.9}", boundary.magnetic_altitude_clamp),
        format!("{:.9}", diagnostics.fuel_outside_martin_domain_seconds),
        diagnostics.fuel_flow_multiplier_bound_hits.to_string(),
        diagnostics
            .powered_thrust_proxy_extrapolation_segments
            .to_string(),
        diagnostics.powered_thrust_proxy_cap_segments.to_string(),
        diagnostics
            .powered_additional_drag_required_segments
            .to_string(),
        guide.eligible_lateral_events.to_string(),
        guide.guided_lateral_events.to_string(),
        guide.candidate_marks.to_string(),
        guide.finite_candidate_scores.to_string(),
        guide.materialization_failures.to_string(),
        guide.proxy_projection_successes.to_string(),
        guide.proxy_projection_failures.to_string(),
        guide.proxy_projection_skipped_candidates.to_string(),
        guide.all_scores_negative_infinity_events.to_string(),
        format!("{:.17e}", guide.sum_selection_effective_sample_size),
        format!("{:.17e}", guide.sum_selection_entropy_nats),
        optional_csv_f64(guide.minimum_selected_probability),
        optional_csv_f64(guide.maximum_selected_probability),
        optional_csv_f64(guide.minimum_event_log_prior_over_proposal),
        optional_csv_f64(guide.maximum_event_log_prior_over_proposal),
        optional_csv_f64(guide.minimum_lead_seconds),
        optional_csv_f64(guide.maximum_lead_seconds),
        format!("{:.17e}", guide.sum_log_candidate_count),
        format!("{:.17e}", guide.sum_selected_log_probability),
        format!("{:.17e}", guide.cumulative_log_prior_over_proposal),
        format!("{:.17e}", guide.sum_minimum_log_prior_over_proposal),
        format!("{:.17e}", guide.sum_maximum_log_prior_over_proposal),
    ];
    format!(",{}", fields.join(","))
}

fn posterior_csv(result: &FilterResult<BroadFlightState>) -> Vec<u8> {
    let mut csv = String::from(
        "particle,root,stratum,weight,time_s,latitude_deg,longitude_deg,pressure_altitude_ft,track_true_deg,heading_true_deg,ground_speed_kt,vertical_speed_ft_min,mach,bank_deg,lateral_mode,lateral_events,speed_events,altitude_events,gross_mass_kg,left_usable_fuel_kg,right_usable_fuel_kg,dual_engine_exhaustion_time_s,bto_log_likelihood,bfo_log_likelihood,fuel_flow_scale,fuel_quantity_offset_kg,",
    );
    csv.push_str(POSTERIOR_DIAGNOSTIC_CSV_HEADER);
    csv.push('\n');
    for (particle, ((state, &log_weight), &root)) in result
        .particles
        .iter()
        .zip(&result.log_weights)
        .zip(&result.root_ids)
        .enumerate()
    {
        if !log_weight.is_finite() {
            continue;
        }
        let flight = state.powered_flight;
        let dual = state
            .fuel
            .dual_engine_exhaustion_time
            .map(|time| format!("{:.9}", time.0))
            .unwrap_or_default();
        csv.push_str(&format!(
            "{particle},{root},{},{:.17e},{:.9},{:.12},{:.12},{:.6},{:.9},{:.9},{:.9},{:.9},{:.12},{:.9},{:?},{},{},{},{:.9},{:.9},{:.9},{dual},{:.17e},{:.17e},{:.12},{:.9}",
            state.stratum.0,
            log_weight.exp(),
            flight.aircraft.time.0,
            flight.aircraft.position.latitude.0,
            flight.aircraft.position.longitude.0,
            flight.aircraft.altitude.0,
            flight.aircraft.track_true.0,
            flight.heading_true.0,
            flight.aircraft.ground_speed.0,
            flight.aircraft.vertical_speed.0,
            flight.mach,
            flight.bank_angle.0,
            flight.command.lateral_mode,
            flight.event_counters.lateral,
            flight.event_counters.speed,
            flight.event_counters.altitude,
            state.fuel.gross_mass().0,
            state.fuel.left_usable_feed.0,
            state.fuel.right_usable_feed.0,
            state.scores.cumulative_bto_log_likelihood,
            state.scores.cumulative_bfo_log_likelihood,
            state.fuel_flow_scale,
            state.fuel_quantity_offset_kg,
        ));
        csv.push_str(&posterior_diagnostic_csv_suffix(
            flight.command.target_mach,
            flight.command.target_pressure_altitude.0,
            state.diagnostics,
        ));
        csv.push('\n');
    }
    csv.into_bytes()
}

struct BroadHandoffContext<'a> {
    suite: &'a BroadSuiteConfig,
    family: &'a BroadFamilyConfig,
    model: &'a BroadFlightConfig,
    plan: &'a StratifiedFilterPlan,
    observations: &'a [BroadFlightObservation],
    input_sha256: &'a BTreeMap<String, String>,
    config_sha256: &'a str,
    fuel_exhaustion_selection_guide_window: Option<BroadResolvedFuelExhaustionGuideWindow>,
}

fn island_inference_descriptor(config: BroadIslandConfig) -> String {
    format!(
        "inference=scientific-stratum-island-smc-v1;islands-per-scientific-stratum={};particles-per-island={};pooling=scientific-prior-times-equal-island-prior-times-conditional-evidence",
        config.islands_per_stratum, config.particles_per_island
    )
}

fn global_transition_pool_inference_descriptor(
    schedule: &BroadGlobalTransitionPoolSchedule,
) -> String {
    format!(
        "inference=global-transition-pool-smc-v1;local-proposal-candidates=1;schedule={};weighting=proper-candidate-measure-plus-output-proposal-correction",
        schedule.stable_descriptor()
    )
}

fn root_stratified_transition_pool_inference_descriptor(
    config: &BroadRootStratifiedTransitionPoolConfig,
) -> String {
    format!(
        "inference=root-stratified-transition-pool-smc-v1;local-proposal-candidates=1;schedule={};allocation=fixed-l-per-finite-mass-root-within-scientific-stratum;weighting=proper-physical-candidate-measure-plus-exact-root-defensive-output-proposal-correction;additional-scientific-evidence=none",
        config.stable_descriptor()
    )
}

fn satcom_event_mark_guide_inference_descriptor(
    config: &BroadSatcomEventMarkGuideRunConfig,
) -> String {
    format!(
        "inference=satcom-event-mark-guide-v1;local-proposal-candidates=1;{};eligibility=lateral-event-with-inclusive-physical-endpoint-lead-window;weighting=incremental-exact-log-prior-over-proposal-applied-once-by-physical-transition;additional-scientific-evidence=none",
        config.stable_descriptor()
    )
}

fn pending_renewal_refresh_inference_descriptor(
    config: &BroadPendingRenewalRefreshRunConfig,
) -> String {
    format!(
        "inference=pending-renewal-post-resample-refresh-v1;local-proposal-candidates=1;{};kernel=target-invariant-auxiliary-clock-gibbs;trigger=configured-ordinary-posterior-resample-only;weight-logz-evidence-term=none;terminal=per-continuation-refresh-required",
        config.stable_descriptor()
    )
}

fn intermediate_satcom_bridge_inference_descriptor(
    config: BroadIntermediateSatcomBridgeConfig,
) -> String {
    format!(
        "inference=intermediate-satcom-potential-smc-v1;local-proposal-candidates=1;endpoint-candidates-per-particle={};{};weighting=exact-telescoping-intermediate-potentials-with-proper-candidate-and-output-proposal-corrections",
        config.endpoint_candidates_per_particle,
        config.resolved().stable_descriptor()
    )
}

fn fuel_exhaustion_selection_guide_inference_descriptor(
    config: &BroadFuelExhaustionSelectionGuideRunConfig,
    window: BroadResolvedFuelExhaustionGuideWindow,
) -> String {
    format!(
        "inference=fuel-exhaustion-selection-guide-v1;local-proposal-candidates=1;{};window-start-epoch={};window-start-s={};window-end-source-epoch={};window-end-source-s={};window-end-contact-offset-s={};window-end-s={};activation=strictly-after-arc1-fuel-anchor;canonical-window-source=hash-locked-input;canonical-row-role=time-only-not-consumed-or-scored",
        config.resolved().stable_descriptor(),
        config.window_start_epoch_id,
        window.window_start_s,
        config.window_end_epoch_id,
        window.canonical_window_end_s,
        window.window_end_contact_offset_s,
        window.window_end_s,
    )
}

fn fuel_exhaustion_persistent_twist_inference_descriptor(
    config: &BroadFuelExhaustionPersistentTwistRunConfig,
    window: BroadResolvedFuelExhaustionGuideWindow,
) -> Result<String> {
    let twist =
        BroadFuelExhaustionSelectionGuide::new(config.resolved()).map_err(anyhow::Error::new)?;
    let neutral = config.potential_floor.to_bits() == 1.0_f64.to_bits();
    Ok(format!(
        "inference=fuel-exhaustion-persistent-twist-v1;execution={};{};window-start-epoch={};window-start-s={};window-end-source-epoch={};window-end-source-s={};window-end-contact-offset-s={};window-end-s={};activation={};finalization={};semantics=computational-proposal-only-no-fuel-or-satcom-likelihood-final-weights-ordinary-physical-filter;terminal=must-not-correct-persistent-potential-again;canonical-window-source=hash-locked-input;canonical-row-role=time-only-not-consumed-or-scored",
        if neutral {
            "neutral-all-inactive-legacy-filter-path"
        } else {
            "bootstrap-constant-local-proposal-candidates-1"
        },
        twist.persistent_twist_stable_descriptor(),
        config.window_start_epoch_id,
        window.window_start_s,
        config.window_end_epoch_id,
        window.canonical_window_end_s,
        window.window_end_contact_offset_s,
        window.window_end_s,
        if neutral {
            "none"
        } else {
            "first-physical-observation-strictly-after-unique-fuel-anchor"
        },
        if neutral {
            "none"
        } else {
            "fit-through-single-global-inverse-potential-without-resampling"
        },
    ))
}

fn broad_run_identity_sha256(
    config_sha256: &str,
    family: &str,
    seed: u64,
    input_sha256: &BTreeMap<String, String>,
) -> String {
    sha256_bytes(
        format!(
            "mh370-broad-filter-v1\n{config_sha256}\n{family}\n{seed}\n{}",
            input_sha256
                .iter()
                .map(|(name, digest)| format!("{name}={digest}"))
                .collect::<Vec<_>>()
                .join("\n")
        )
        .as_bytes(),
    )
}

fn filtering_handoff(
    context: BroadHandoffContext<'_>,
    seed: u64,
    result: &FilterResult<BroadFlightState>,
) -> Result<mh370_estimator::BroadPosteriorHandoffV1> {
    let snapshot = result
        .snapshots
        .last()
        .context("broad filter did not retain its final snapshot")?;
    let final_observation = context
        .observations
        .last()
        .context("broad observation sequence is empty")?;
    if snapshot.observation_time_s != final_observation.time().0 {
        bail!("retained broad checkpoint does not match the final observation");
    }
    let bto_observation_count = context
        .observations
        .iter()
        .filter(|observation| {
            matches!(
                observation,
                BroadFlightObservation::Satcom(value) if value.use_bto
            )
        })
        .count() as u32;
    let bfo_observation_count = context
        .observations
        .iter()
        .filter(|observation| {
            matches!(
                observation,
                BroadFlightObservation::Satcom(value) if value.use_bfo
            )
        })
        .count() as u32;
    let bto_identity = BroadEvidenceIdentityV1 {
        epoch_id: format!(
            "satcom-through-{}",
            context.suite.inputs.fit_through_epoch_id
        ),
        channel: None,
        component: BroadEvidenceComponentV1::Bto,
    };
    let bfo_identity = context.family.use_bfo.then(|| BroadEvidenceIdentityV1 {
        epoch_id: format!(
            "satcom-through-{}",
            context.suite.inputs.fit_through_epoch_id
        ),
        channel: None,
        component: BroadEvidenceComponentV1::Bfo,
    });
    let mut evidence_entries = vec![BroadEvidenceEntryV1 {
        identity: bto_identity.clone(),
        disposition: BroadEvidenceDispositionV1::Consumed,
        state_effect: BroadEvidenceStateEffectV1::None,
    }];
    if let Some(identity) = &bfo_identity {
        evidence_entries.push(BroadEvidenceEntryV1 {
            identity: identity.clone(),
            disposition: BroadEvidenceDispositionV1::Consumed,
            state_effect: BroadEvidenceStateEffectV1::AnalyticLatentUpdate,
        });
    } else {
        evidence_entries.push(BroadEvidenceEntryV1 {
            identity: BroadEvidenceIdentityV1 {
                epoch_id: format!(
                    "satcom-through-{}",
                    context.suite.inputs.fit_through_epoch_id
                ),
                channel: None,
                component: BroadEvidenceComponentV1::Bfo,
            },
            disposition: BroadEvidenceDispositionV1::HeldOut,
            state_effect: BroadEvidenceStateEffectV1::None,
        });
    }
    let evidence = BroadEvidenceLedgerV1::from_entries(evidence_entries)?;
    let run_identity_sha256 = broad_run_identity_sha256(
        context.config_sha256,
        &context.family.id,
        seed,
        context.input_sha256,
    );
    let run = BroadRunMetadataV1 {
        model_family: mh370_estimator::BROAD_FLIGHT_MODEL_FAMILY.to_string(),
        seed,
        run_identity_sha256,
        config_sha256: context.config_sha256.to_string(),
        input_sha256: context.input_sha256.clone(),
        time_origin_utc: context.suite.environment.time_origin_utc.clone(),
        source_epoch_id: context.suite.inputs.source_epoch_id.clone(),
        source_time: Seconds(context.model.radar_prior.time_s),
        source_time_utc: context.suite.inputs.source_time_utc.clone(),
        dynamics_model_family: {
            let mut descriptor = format!(
                "powered-marked-jump-era5-v1;{}",
                context
                    .suite
                    .model
                    .proposal_candidate_schedule
                    .stable_descriptor(context.model.proposal_candidates)
            );
            if let Some(config) = context.suite.islands {
                descriptor.push(';');
                descriptor.push_str(&island_inference_descriptor(config));
            }
            if let Some(schedule) = &context.suite.global_transition_pool {
                descriptor.push(';');
                descriptor.push_str(&global_transition_pool_inference_descriptor(schedule));
            }
            if let Some(config) = &context.suite.root_stratified_transition_pool {
                descriptor.push(';');
                descriptor
                    .push_str(&root_stratified_transition_pool_inference_descriptor(config));
            }
            if let Some(config) = &context.suite.satcom_event_mark_guide {
                descriptor.push(';');
                descriptor.push_str(&satcom_event_mark_guide_inference_descriptor(config));
            }
            if let Some(config) = &context.suite.pending_renewal_refresh {
                descriptor.push(';');
                descriptor.push_str(&pending_renewal_refresh_inference_descriptor(config));
            }
            if let Some(config) = context.suite.intermediate_satcom_bridge {
                descriptor.push(';');
                descriptor.push_str(&intermediate_satcom_bridge_inference_descriptor(config));
            }
            if let (Some(config), Some(window)) = (
                context.suite.fuel_exhaustion_selection_guide.as_ref(),
                context.fuel_exhaustion_selection_guide_window,
            ) {
                descriptor.push(';');
                descriptor.push_str(&fuel_exhaustion_selection_guide_inference_descriptor(
                    config, window,
                ));
            }
            if let (Some(config), Some(window)) = (
                context.suite.fuel_exhaustion_persistent_twist.as_ref(),
                context.fuel_exhaustion_selection_guide_window,
            ) {
                descriptor.push(';');
                descriptor.push_str(&fuel_exhaustion_persistent_twist_inference_descriptor(
                    config, window,
                )?);
            }
            descriptor
        },
        fuel_model_family: format!(
            "{};fuel-flow-initialization={}",
            match context.model.fuel_model {
            PoweredFuelModel::MartinTrent892Lrc => "martin-trent892-lrc-strict",
            PoweredFuelModel::DeclaredBroadExtension(_) => {
                "martin-trent892-declared-broad-extension"
            }
            },
            context
                .suite
                .model
                .fuel_flow_initialization_design
                .as_str()
        ),
        pending_renewal_refresh: context
            .suite
            .pending_renewal_refresh
            .as_ref()
            .map(BroadPendingRenewalRefreshRunConfig::resolved),
        powered_performance_model_family: "attached-flow-segment-force-balance-v1".to_string(),
        powered_aerodynamic_family: match context.model.powered_feasibility.aerodynamic_family {
            mh370_end_of_flight::ConditionalB772AerodynamicFamily::OpenapV2_6_0AttachedFlow => {
                "openap-v2.6.0-b772-attached-flow"
            }
            mh370_end_of_flight::ConditionalB772AerodynamicFamily::OpenapPublished2020AttachedFlow => {
                "openap-published-2020-b772-attached-flow"
            }
        }
        .to_string(),
        powered_thrust_family: "openap-v2.6.0-b772-trent895-cruise-ceiling".to_string(),
        powered_thrust_multiplier: context.model.powered_feasibility.thrust_multiplier,
        powered_static_thrust_cap_per_engine_n: context
            .model
            .powered_feasibility
            .static_thrust_cap_per_engine_n,
        powered_maximum_additional_drag_coefficient: context
            .model
            .powered_feasibility
            .maximum_additional_drag_coefficient,
        configured_particles: context.suite.filter.particles,
        strata: context
            .model
            .strata
            .iter()
            .map(|stratum| {
                let allocation = context
                    .plan
                    .strata
                    .iter()
                    .find(|entry| entry.id == stratum.id)
                    .expect("expanded model and plan share strata");
                BroadStratumMetadataV1 {
                    id: stratum.id,
                    name: stratum.name.clone(),
                    process_family: stratum.name.clone(),
                    scientific_log_prior_probability: allocation.log_prior_probability,
                    allocated_particles: allocation.particles,
                }
            })
            .collect(),
    };
    let checkpoint = BroadCheckpointMetadataV1 {
        checkpoint_id: format!(
            "filtering-through-{}",
            context.suite.inputs.fit_through_epoch_id
        ),
        state_epoch_id: context.suite.inputs.fit_through_epoch_id.clone(),
        state_time: final_observation.time(),
        state_time_utc: match final_observation {
            BroadFlightObservation::Satcom(observation) => observation.flight.time_utc.clone(),
            _ => bail!("broad final checkpoint must be a SATCOM observation"),
        },
        conditioning: BroadConditioningSemanticsV1::Filtering {
            through_epoch_id: context.suite.inputs.fit_through_epoch_id.clone(),
        },
    };
    build_broad_filtering_handoff_v1(
        snapshot,
        run,
        checkpoint,
        evidence,
        BroadAggregateEvidenceV1 {
            bto_through_checkpoint: bto_identity,
            bfo_through_checkpoint: bfo_identity,
            bto_observation_count,
            bfo_observation_count,
        },
    )
    .map_err(anyhow::Error::new)
}

fn report_document(
    suite: &BroadSuiteConfig,
    model: &BroadFlightConfig,
    family: &BroadFamilyConfig,
    summaries: &[BroadSeedSummary],
    independent_seed_pooling: Option<&BroadIndependentSeedPoolSummary>,
    fuel_selection_guide: BroadFuelExhaustionSelectionGuideReportContext<'_>,
    points: Vec<ReportPoint>,
) -> ReportDocument {
    let mut summary = vec![
        ("Seeds".to_string(), summaries.len().to_string()),
        (
            "Particles per seed".to_string(),
            suite.filter.particles.to_string(),
        ),
        (
            "Evidence".to_string(),
            if family.use_bfo {
                "BTO + BFO"
            } else {
                "BTO only"
            }
            .to_string(),
        ),
        (
            "Adaptive cadence".to_string(),
            format!(
                "{:.0} s steady / {:.0} s transition",
                model.integration.steady_step_s, model.integration.transition_step_s
            ),
        ),
        (
            "Transition proposal".to_string(),
            suite
                .model
                .proposal_candidate_schedule
                .stable_descriptor(model.proposal_candidates),
        ),
        (
            "Root-defense epsilon".to_string(),
            format!(
                "{:.3}",
                suite.resampling_policy.uniform_root_mixture_epsilon
            ),
        ),
        (
            "Fuel support".to_string(),
            format!(
                "{} across {} structural strata",
                suite.model.fuel_flow_initialization_design.as_str(),
                model.strata.len()
            ),
        ),
    ];
    if let Some(config) = suite.islands {
        summary.push((
            "Inference".to_string(),
            format!(
                "{} evidence-weighted islands/stratum x {} particles/island",
                config.islands_per_stratum, config.particles_per_island
            ),
        ));
    } else if let Some(schedule) = &suite.global_transition_pool {
        summary.push((
            "Inference".to_string(),
            format!(
                "evidence-weighted global transition pool; {}",
                schedule.stable_descriptor()
            ),
        ));
    } else if let Some(config) = &suite.root_stratified_transition_pool {
        summary.push((
            "Inference".to_string(),
            format!(
                "physical fixed-candidate-per-root transition pool; {}",
                config.stable_descriptor()
            ),
        ));
    } else if let Some(config) = &suite.pending_renewal_refresh {
        summary.push((
            "Inference".to_string(),
            format!(
                "target-invariant pending-renewal Gibbs refresh after configured actual posterior resampling; {}",
                config.stable_descriptor()
            ),
        ));
    } else if let Some(config) = suite.intermediate_satcom_bridge {
        summary.push((
            "Inference".to_string(),
            format!(
                "exact two-point SATCOM bridge; {}",
                config.resolved().stable_descriptor()
            ),
        ));
    }
    if let Some(config) = &suite.satcom_event_mark_guide {
        summary.push((
            "SATCOM event-mark proposal".to_string(),
            format!(
                "lateral-only, inclusive endpoint lead windows; {}; proposal-only",
                config.stable_descriptor()
            ),
        ));
    }
    if let (Some(config), Some(window)) = (
        suite.fuel_exhaustion_selection_guide.as_ref(),
        fuel_selection_guide.window,
    ) {
        summary.push((
            "Fuel proposal guide".to_string(),
            format!(
                "delta {:.3}; exact window {:.3}–{:.3} s; proposal-only",
                config.potential_floor, window.window_start_s, window.window_end_s
            ),
        ));
    }
    if let (Some(config), Some(window)) = (
        suite.fuel_exhaustion_persistent_twist.as_ref(),
        fuel_selection_guide.window,
    ) {
        summary.push((
            "Persistent fuel proposal twist".to_string(),
            format!(
                "delta {:.3}; exact window {:.3}–{:.3} s; globally untwisted at fit-through",
                config.potential_floor, window.window_start_s, window.window_end_s
            ),
        ));
    }
    if let Some(posterior) = fuel_selection_guide.posterior {
        summary.extend([
            (
                "Fuel-window compatibility".to_string(),
                format!(
                    "target mass {:.4}; positive-slot fraction {:.4}",
                    posterior.compatible_posterior_mass,
                    posterior.compatible_positive_weight_slot_fraction
                ),
            ),
            (
                "Compatible root ESS / maximum".to_string(),
                match (
                    posterior.compatible_root_effective_sample_size,
                    posterior.maximum_compatible_root_weight,
                ) {
                    (Some(ess), Some(maximum)) => format!("{ess:.1} / {maximum:.4}"),
                    _ => "none".to_string(),
                },
            ),
            (
                "Compatible slots / seed-local roots".to_string(),
                format!(
                    "{} / {}; {} zero-weight placeholders retained separately",
                    posterior.compatible_positive_weight_slots,
                    posterior.distinct_compatible_seed_local_roots,
                    posterior.zero_weight_placeholder_slots
                ),
            ),
        ]);
    }
    if let Some(pooling) = independent_seed_pooling {
        summary.extend([
            (
                "Seed pooling".to_string(),
                "independent posterior populations weighted by estimated evidence".to_string(),
            ),
            (
                "Seed-weight ESS / maximum".to_string(),
                format!(
                    "{:.2} / {:.4}",
                    pooling.evidence_weight_effective_sample_size,
                    pooling.maximum_seed_evidence_weight
                ),
            ),
            (
                "Pooled particle / namespaced-root ESS".to_string(),
                format!(
                    "{:.1} / {:.1}",
                    pooling.pooled_particle_effective_sample_size,
                    pooling.seed_namespaced_root_effective_sample_size
                ),
            ),
        ]);
    }
    ReportDocument {
        title: format!("{} — {}", suite.name, family.id),
        subtitle: "Broad marked-jump powered-flight filtering posterior".to_string(),
        summary,
        points,
        diagnostics: summaries
            .iter()
            .map(|summary| DiagnosticPoint {
                label: format!("seed {}", summary.seed),
                effective_sample_size: summary.effective_sample_size,
                log_evidence_increment: summary.log_evidence,
            })
            .collect(),
        evidence_conditions: {
            let mut conditions = vec![
            format!(
                "SATCOM through {}; fuel is propagated but does not weight this filtering posterior",
                suite.inputs.fit_through_epoch_id
            ),
            "Repeated manoeuvres are a declared marked-jump prior, not observed pilot intent"
                .to_string(),
            ];
            if suite.intermediate_satcom_bridge.is_some() {
                conditions.push(
                    "Intermediate SATCOM potentials are strictly positive computational guides that telescope out; each physical endpoint likelihood is consumed exactly once"
                        .to_string(),
                );
            }
            if suite.satcom_event_mark_guide.is_some() {
                conditions.push(
                    "The SATCOM event-mark guide selects among prior lateral marks only inside configured inclusive endpoint lead windows; its exact incremental target/proposal correction is consumed once by the physical transition and adds no SATCOM observation or likelihood; frozen-command endpoint projection is computational guidance, not pilot-intent or trajectory evidence"
                        .to_string(),
                );
            }
            if suite.pending_renewal_refresh.is_some() {
                conditions.push(
                    "The configured post-resampling move refreshes only disposable pending lateral, speed, and altitude renewal clocks from their exact conditional laws; it is target invariant and contributes no log-weight, logZ, likelihood, or scientific evidence term"
                        .to_string(),
                );
            }
            if suite.fuel_exhaustion_selection_guide.is_some() {
                conditions.push(
                    "The frozen fuel-exhaustion compatibility guide changes proposal allocation only and is exactly corrected; its hash-locked future SATCOM row supplies time bounds but is neither consumed nor scored"
                        .to_string(),
                );
            }
            if suite.fuel_exhaustion_persistent_twist.is_some() {
                conditions.push(
                    "The persistent frozen fuel-exhaustion potential changes computational allocation only; it adds no fuel or SATCOM likelihood and is removed globally at fit-through, so terminal inference must not correct it again"
                        .to_string(),
                );
            }
            conditions
        },
        limitations: vec![
            "This is a conditional broad-prior posterior; there is no assumption-free PDF"
                .to_string(),
            "The powered-flight envelope is a public-data kinematic/lift proxy, not a calibrated Boeing 777 control-law model"
                .to_string(),
            format!(
                "Additional drag up to declared delta-Cd {:.3} is a conditional support allowance, not a measured B777 limit",
                model
                    .powered_feasibility
                    .maximum_additional_drag_coefficient
            ),
            "The Martin fuel extension is diagnostic through this checkpoint and is not an independent likelihood"
                .to_string(),
            "HPD contours use a fixed display kernel; estimator weights and numerical summaries are unchanged"
                .to_string(),
        ],
        map_context: None,
    }
}

pub(crate) fn estimate(
    config_path: &Path,
    output: &Path,
    requested_threads: Option<usize>,
) -> Result<()> {
    let config_bytes = read_input(config_path, "configuration")?;
    let config_text = std::str::from_utf8(&config_bytes).context("configuration is not UTF-8")?;
    let suite: BroadSuiteConfig = toml::from_str(config_text).context("cannot parse broad TOML")?;
    validate_suite(&suite)?;
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
    let era5_path = resolve(config_path, &suite.inputs.era5);
    let igrf_path = resolve(config_path, &suite.inputs.igrf);
    let observation_bytes = read_input(&observation_path, "SATCOM observations")?;
    let ephemeris_bytes = read_input(&ephemeris_path, "satellite ephemeris")?;
    let era5_bytes = read_input(&era5_path, "ERA5 grid")?;
    let igrf_bytes = read_input(&igrf_path, "IGRF grid")?;
    let configured_fuel_guide = suite
        .fuel_exhaustion_selection_guide
        .as_ref()
        .or(suite.fuel_exhaustion_persistent_twist.as_ref());
    let fuel_exhaustion_guide_source = configured_fuel_guide
        .map(|guide| {
            let path = resolve(config_path, &guide.canonical_full_satcom_observations);
            let bytes = read_input(&path, "fuel-guide canonical full SATCOM observations")?;
            let window = resolve_fuel_exhaustion_guide_window(guide, &bytes)?;
            Ok::<_, anyhow::Error>((bytes, window))
        })
        .transpose()?;
    let fuel_exhaustion_persistent_twist_descriptor = suite
        .fuel_exhaustion_persistent_twist
        .as_ref()
        .map(|config| {
            fuel_exhaustion_persistent_twist_inference_descriptor(
                config,
                fuel_exhaustion_guide_source
                    .as_ref()
                    .map(|(_, window)| *window)
                    .expect("configured persistent twist has a resolved canonical window"),
            )
        })
        .transpose()?;
    let satcom_event_mark_guide_descriptor = suite
        .satcom_event_mark_guide
        .as_ref()
        .map(satcom_event_mark_guide_inference_descriptor);
    let pending_renewal_refresh_descriptor = suite
        .pending_renewal_refresh
        .as_ref()
        .map(pending_renewal_refresh_inference_descriptor);
    let observation_text =
        std::str::from_utf8(&observation_bytes).context("SATCOM CSV is not UTF-8")?;
    let ephemeris_text =
        std::str::from_utf8(&ephemeris_bytes).context("ephemeris CSV is not UTF-8")?;
    let weather = Era5Grid::parse(&era5_bytes)?;
    let magnetic = IgrfGrid::parse(&igrf_bytes)?;
    let environment = PoweredFlightEnvironment {
        weather: &weather,
        magnetic: Some(&magnetic),
        magnetic_altitude_policy: suite.environment.magnetic_altitude_policy,
        time_origin_unix_s: suite.environment.time_origin_unix_s,
    };
    let (model_config, plan, fuel_overrides) = expand_model_and_plan(&suite)?;
    let island_plan = build_island_plan(&suite, &plan)?;
    let model = BroadFlightModel::new_with_options(
        model_config.clone(),
        environment,
        BroadFlightModelOptions {
            stratum_fuel_uncertainty_overrides: fuel_overrides,
            fuel_flow_initialization_design: suite.model.fuel_flow_initialization_design,
            proposal_candidate_schedule: suite.model.proposal_candidate_schedule.clone(),
            satcom_event_mark_guide: suite
                .satcom_event_mark_guide
                .as_ref()
                .map(BroadSatcomEventMarkGuideRunConfig::resolved),
        },
    )?;
    let intermediate_satcom_bridge = suite
        .intermediate_satcom_bridge
        .map(|config| BroadSatcomIntermediatePotentialBridge::new(config.resolved()))
        .transpose()
        .map_err(anyhow::Error::new)
        .context("cannot construct intermediate SATCOM bridge")?;
    let pending_renewal_refresh = suite
        .pending_renewal_refresh
        .as_ref()
        .map(|config| BroadPendingRenewalRefreshKernel::new(config.resolved()))
        .transpose()
        .map_err(anyhow::Error::new)
        .context("cannot construct pending-renewal refresh kernel")?;
    let fuel_exhaustion_selection_guide = configured_fuel_guide
        .map(|config| BroadFuelExhaustionSelectionGuide::new(config.resolved()))
        .transpose()
        .map_err(anyhow::Error::new)
        .context("cannot construct fuel-exhaustion selection guide")?;
    let pool = ThreadPoolBuilder::new()
        .num_threads(threads)
        .build()
        .context("cannot build broad-flight worker pool")?;
    let started = Instant::now();
    let mut family_summaries = Vec::new();
    let mut realized_proposal_epochs_by_family = BTreeMap::new();
    let mut realized_global_transition_pool_epochs_by_family = suite
        .global_transition_pool
        .as_ref()
        .map(|_| BTreeMap::new());
    let mut realized_root_stratified_transition_pool_epochs_by_family = suite
        .root_stratified_transition_pool
        .as_ref()
        .map(|_| BTreeMap::new());
    let mut realized_satcom_event_mark_guide_epochs_by_family = suite
        .satcom_event_mark_guide
        .as_ref()
        .map(|_| BTreeMap::new());
    let mut realized_pending_renewal_refresh_epochs_by_family = suite
        .pending_renewal_refresh
        .as_ref()
        .map(|_| BTreeMap::new());
    let mut realized_intermediate_satcom_bridge_epochs_by_family = suite
        .intermediate_satcom_bridge
        .as_ref()
        .map(|_| BTreeMap::new());
    let mut realized_fuel_exhaustion_selection_guide_epochs_by_family = suite
        .fuel_exhaustion_selection_guide
        .as_ref()
        .map(|_| BTreeMap::new());
    let mut realized_fuel_exhaustion_persistent_twist_epochs_by_family = suite
        .fuel_exhaustion_persistent_twist
        .as_ref()
        .map(|_| BTreeMap::new());
    let mut independent_seed_pooling_by_family = (suite.seeds.len() > 1).then(BTreeMap::new);
    let mut outputs = BTreeMap::new();
    let config_sha256 = sha256_bytes(&config_bytes);
    let mut input_sha256 = BTreeMap::from([
        (
            "satcom_observations".to_string(),
            sha256_bytes(&observation_bytes),
        ),
        (
            "satellite_ephemeris".to_string(),
            sha256_bytes(&ephemeris_bytes),
        ),
        ("era5".to_string(), sha256_bytes(&era5_bytes)),
        ("igrf".to_string(), sha256_bytes(&igrf_bytes)),
    ]);
    if let Some((bytes, _)) = &fuel_exhaustion_guide_source {
        input_sha256.insert(
            "fuel_guide_canonical_satcom_observations".to_string(),
            sha256_bytes(bytes),
        );
    }

    for family in &suite.families {
        let observations =
            observations_for_family(&suite, family, observation_text, ephemeris_text)?;
        let proposal_epochs =
            realized_proposal_epochs(&model, &observations, suite.filter.initial_time_s);
        realized_proposal_epochs_by_family.insert(family.id.clone(), proposal_epochs.clone());
        let (global_transition_pool_steps, realized_global_transition_pool_epochs) = suite
            .global_transition_pool
            .as_ref()
            .map(|schedule| {
                realized_global_transition_pool_epochs(
                    schedule,
                    &observations,
                    suite.filter.initial_time_s,
                )
            })
            .map_or((None, None), |(steps, realized)| {
                (Some(steps), Some(realized))
            });
        if let Some(realized) = &realized_global_transition_pool_epochs {
            if !realized
                .iter()
                .any(|epoch| matches!(epoch.step, GlobalTransitionPoolStep::Pool { .. }))
            {
                bail!(
                    "global transition-pool schedule does not select an observation for family {}",
                    family.id
                );
            }
            realized_global_transition_pool_epochs_by_family
                .as_mut()
                .expect("configured transition pool has a realized-epoch ledger")
                .insert(family.id.clone(), realized.clone());
        }
        let (
            root_stratified_transition_pool_steps,
            realized_root_stratified_transition_pool_epochs,
        ) = suite
            .root_stratified_transition_pool
            .as_ref()
            .map(|config| realized_root_stratified_transition_pool_epochs(config, &observations))
            .transpose()?
            .map_or((None, None), |(steps, realized)| {
                (Some(steps), Some(realized))
            });
        if let Some(realized) = &realized_root_stratified_transition_pool_epochs {
            if !realized
                .iter()
                .any(|epoch| matches!(epoch.step, RootStratifiedTransitionPoolStep::Pool { .. }))
            {
                bail!(
                    "root-stratified transition-pool schedule does not select an observation for family {}",
                    family.id
                );
            }
            realized_root_stratified_transition_pool_epochs_by_family
                .as_mut()
                .expect("configured root-stratified transition pool has a realized-epoch ledger")
                .insert(family.id.clone(), realized.clone());
        }
        let realized_satcom_event_mark_guide_epochs = suite
            .satcom_event_mark_guide
            .as_ref()
            .map(|config| {
                realized_satcom_event_mark_guide_epochs(
                    config,
                    &observations,
                    suite.filter.initial_time_s,
                )
            })
            .transpose()?;
        if let Some(realized) = &realized_satcom_event_mark_guide_epochs {
            realized_satcom_event_mark_guide_epochs_by_family
                .as_mut()
                .expect("configured SATCOM event-mark guide has a realized-epoch ledger")
                .insert(family.id.clone(), realized.clone());
        }
        let (pending_renewal_refresh_steps, realized_pending_renewal_refresh_epochs) = suite
            .pending_renewal_refresh
            .as_ref()
            .map(|config| realized_pending_renewal_refresh_epochs(config, &observations))
            .transpose()?
            .map_or((None, None), |(steps, realized)| {
                (Some(steps), Some(realized))
            });
        if let Some(realized) = &realized_pending_renewal_refresh_epochs {
            realized_pending_renewal_refresh_epochs_by_family
                .as_mut()
                .expect("configured pending-renewal refresh has a realized-epoch ledger")
                .insert(family.id.clone(), realized.clone());
        }
        let (intermediate_potential_steps, realized_intermediate_satcom_bridge_epochs) = suite
            .intermediate_satcom_bridge
            .map(|config| {
                realized_intermediate_satcom_bridge_epochs(
                    config,
                    &observations,
                    suite.filter.initial_time_s,
                )
            })
            .transpose()?
            .map_or((None, None), |(steps, realized)| {
                (Some(steps), Some(realized))
            });
        if let Some(realized) = &realized_intermediate_satcom_bridge_epochs {
            if !realized.iter().any(|epoch| {
                matches!(
                    epoch.step,
                    IntermediatePotentialStep::Bridge { .. }
                        | IntermediatePotentialStep::BridgeWithEndpointPool { .. }
                )
            }) {
                bail!(
                    "intermediate SATCOM bridge does not select an observation interval for family {}",
                    family.id
                );
            }
            realized_intermediate_satcom_bridge_epochs_by_family
                .as_mut()
                .expect("configured intermediate bridge has a realized-epoch ledger")
                .insert(family.id.clone(), realized.clone());
        }
        let (fuel_exhaustion_selection_steps, realized_fuel_exhaustion_selection_guide_epochs) =
            suite
                .fuel_exhaustion_selection_guide
                .as_ref()
                .map(|config| {
                    realized_fuel_exhaustion_selection_guide_epochs(
                        config,
                        fuel_exhaustion_guide_source
                            .as_ref()
                            .map(|(_, window)| *window)
                            .expect("configured fuel guide has a resolved canonical window"),
                        &observations,
                    )
                })
                .transpose()?
                .map_or((None, None), |(steps, realized)| {
                    (Some(steps), Some(realized))
                });
        if let Some(realized) = &realized_fuel_exhaustion_selection_guide_epochs {
            realized_fuel_exhaustion_selection_guide_epochs_by_family
                .as_mut()
                .expect("configured fuel guide has a realized-epoch ledger")
                .insert(family.id.clone(), realized.clone());
        }
        let (
            fuel_exhaustion_persistent_twist_steps,
            realized_fuel_exhaustion_persistent_twist_epochs,
        ) = suite
            .fuel_exhaustion_persistent_twist
            .as_ref()
            .map(|config| {
                realized_fuel_exhaustion_persistent_twist_epochs(
                    config,
                    fuel_exhaustion_guide_source
                        .as_ref()
                        .map(|(_, window)| *window)
                        .expect("configured persistent twist has a resolved canonical window"),
                    &observations,
                    &suite.inputs.fit_through_epoch_id,
                )
            })
            .transpose()?
            .map_or((None, None), |(steps, realized)| {
                (Some(steps), Some(realized))
            });
        if let Some(realized) = &realized_fuel_exhaustion_persistent_twist_epochs {
            realized_fuel_exhaustion_persistent_twist_epochs_by_family
                .as_mut()
                .expect("configured persistent twist has a realized-epoch ledger")
                .insert(family.id.clone(), realized.clone());
        }
        let family_output = output.join(&family.id);
        fs::create_dir_all(&family_output)?;
        let mut seed_summaries = Vec::new();
        let mut seed_posterior_populations = Vec::new();
        let mut fuel_exhaustion_posterior_populations = Vec::new();
        for &seed in &suite.seeds {
            let mut filter = suite.filter.clone();
            filter.seed = seed;
            let seed_output = family_output.join(format!("seed-{seed}"));
            fs::create_dir_all(&seed_output)?;
            let retention =
                SnapshotRetention::SelectedObservationIndices(vec![observations.len() - 1]);
            let mut pending_renewal_refresh_checkpoints = None;
            let (
                result,
                island_smc,
                global_transition_pool_smc,
                root_stratified_transition_pool_smc,
                intermediate_satcom_bridge_smc,
                fuel_selection_checkpoints,
                persistent_twist_execution,
            ) = if let Some(steps) = &pending_renewal_refresh_steps {
                let moved = pool.install(|| {
                    run_stratified_bootstrap_filter_with_post_resample_move(
                        &model,
                        pending_renewal_refresh
                            .as_ref()
                            .expect("refresh steps require their estimator kernel"),
                        &observations,
                        &filter,
                        &plan,
                        &retention,
                        suite.resampling_policy,
                        steps,
                    )
                })?;
                pending_renewal_refresh_checkpoints = Some(moved.post_resample_move_checkpoints);
                (moved.pooled, None, None, None, None, None, None)
            } else if let Some(island_plan) = &island_plan {
                let island_result = pool.install(|| {
                    run_stratified_island_filter_with_snapshot_retention_and_resampling_policy(
                        &model,
                        &observations,
                        &filter,
                        island_plan,
                        &retention,
                        suite.resampling_policy,
                    )
                })?;
                let diagnostics_path = seed_output.join("island-diagnostics.json");
                let run_identity_sha256 =
                    broad_run_identity_sha256(&config_sha256, &family.id, seed, &input_sha256);
                write_json(
                    &diagnostics_path,
                    &BroadIslandDiagnosticsArtifact {
                        schema: "mh370-broad-island-smc-diagnostics-v1",
                        schema_version: 1,
                        model_family: mh370_estimator::BROAD_FLIGHT_MODEL_FAMILY,
                        family: &family.id,
                        seed,
                        run_identity_sha256: &run_identity_sha256,
                        config_sha256: &config_sha256,
                        input_sha256: &input_sha256,
                        filter: &filter,
                        resampling_policy: suite.resampling_policy,
                        pooling_semantics:
                            "scientific_prior_times_equal_island_prior_times_conditional_evidence",
                        plan: island_plan,
                        islands: &island_result.islands,
                        checkpoints: &island_result.island_checkpoints,
                    },
                )?;
                outputs.insert(
                    format!("{}/seed-{seed}/island-diagnostics.json", family.id),
                    sha256_file(&diagnostics_path)?,
                );
                let island_summary = summarize_islands(&island_result);
                (
                    island_result.pooled,
                    Some(island_summary),
                    None,
                    None,
                    None,
                    None,
                    None,
                )
            } else if let Some(steps) = &global_transition_pool_steps {
                let transition_pool_result = pool.install(|| {
                    run_stratified_filter_with_global_transition_pool(
                        &model,
                        &observations,
                        &filter,
                        &plan,
                        &retention,
                        suite.resampling_policy,
                        steps,
                    )
                })?;
                validate_global_transition_pool_diagnostics(
                    realized_global_transition_pool_epochs
                        .as_deref()
                        .expect("transition-pool steps have a realized-epoch ledger"),
                    &transition_pool_result,
                )?;
                let diagnostics_path = seed_output.join("transition-pool-diagnostics.json");
                let run_identity_sha256 =
                    broad_run_identity_sha256(&config_sha256, &family.id, seed, &input_sha256);
                write_json(
                    &diagnostics_path,
                    &BroadGlobalTransitionPoolDiagnosticsArtifact {
                        schema: "mh370-broad-global-transition-pool-diagnostics-v1",
                        schema_version: 1,
                        model_family: mh370_estimator::BROAD_FLIGHT_MODEL_FAMILY,
                        family: &family.id,
                        seed,
                        run_identity_sha256: &run_identity_sha256,
                        config_sha256: &config_sha256,
                        input_sha256: &input_sha256,
                        filter: &filter,
                        resampling_policy: suite.resampling_policy,
                        schedule: suite
                            .global_transition_pool
                            .as_ref()
                            .expect("transition-pool steps require their configured schedule"),
                        realized_epochs: realized_global_transition_pool_epochs
                            .as_deref()
                            .expect("transition-pool steps have a realized-epoch ledger"),
                        weighting_semantics:
                            "proper_candidate_measure_with_exact_output_proposal_correction",
                        checkpoints: &transition_pool_result.transition_pool_checkpoints,
                    },
                )?;
                outputs.insert(
                    format!("{}/seed-{seed}/transition-pool-diagnostics.json", family.id),
                    sha256_file(&diagnostics_path)?,
                );
                let transition_pool_summary =
                    summarize_global_transition_pool(&transition_pool_result);
                (
                    transition_pool_result.pooled,
                    None,
                    Some(transition_pool_summary),
                    None,
                    None,
                    None,
                    None,
                )
            } else if let Some(steps) = &root_stratified_transition_pool_steps {
                let transition_pool_result = pool.install(|| {
                    run_stratified_filter_with_root_stratified_transition_pool(
                        &model,
                        &observations,
                        &filter,
                        &plan,
                        &retention,
                        suite.resampling_policy,
                        steps,
                    )
                })?;
                validate_root_stratified_transition_pool_diagnostics(
                    realized_root_stratified_transition_pool_epochs
                        .as_deref()
                        .expect(
                            "root-stratified transition-pool steps have a realized-epoch ledger",
                        ),
                    &transition_pool_result,
                )?;
                let diagnostics_path =
                    seed_output.join("root-stratified-transition-pool-diagnostics.json");
                let run_identity_sha256 =
                    broad_run_identity_sha256(&config_sha256, &family.id, seed, &input_sha256);
                write_json(
                    &diagnostics_path,
                    &BroadRootStratifiedTransitionPoolDiagnosticsArtifact {
                        schema: "mh370-broad-root-stratified-transition-pool-diagnostics-v1",
                        schema_version: 1,
                        model_family: mh370_estimator::BROAD_FLIGHT_MODEL_FAMILY,
                        family: &family.id,
                        seed,
                        run_identity_sha256: &run_identity_sha256,
                        config_sha256: &config_sha256,
                        input_sha256: &input_sha256,
                        filter: &filter,
                        resampling_policy: suite.resampling_policy,
                        config: suite.root_stratified_transition_pool.as_ref().expect(
                            "root-stratified transition-pool steps require their configured schedule",
                        ),
                        realized_epochs: realized_root_stratified_transition_pool_epochs
                            .as_deref()
                            .expect(
                                "root-stratified transition-pool steps have a realized-epoch ledger",
                            ),
                        target_semantics:
                            "ordinary_physical_filter_for_configured_family_no_additional_scientific_evidence",
                        candidate_allocation_semantics:
                            "exactly_l_transition_candidates_per_finite_mass_root_within_each_scientific_stratum",
                        generic_checkpoint_candidates_per_particle_semantics:
                            "zero_is_a_typed_sentinel_for_root_stratified_allocation;operative_l_is_candidates_per_positive_root_in_the_paired_root_checkpoint",
                        weighting_semantics:
                            "proper_physical_candidate_measure_with_exact_root_defensive_output_proposal_correction",
                        transition_pool_checkpoints: &transition_pool_result
                            .transition_pool_checkpoints,
                        root_stratified_candidate_pool_checkpoints: &transition_pool_result
                            .root_stratified_candidate_pool_checkpoints,
                    },
                )?;
                outputs.insert(
                    format!(
                        "{}/seed-{seed}/root-stratified-transition-pool-diagnostics.json",
                        family.id
                    ),
                    sha256_file(&diagnostics_path)?,
                );
                let transition_pool_summary =
                    summarize_root_stratified_transition_pool(&transition_pool_result);
                (
                    transition_pool_result.pooled,
                    None,
                    None,
                    Some(transition_pool_summary),
                    None,
                    None,
                    None,
                )
            } else if fuel_exhaustion_persistent_twist_steps
                .as_ref()
                .is_some_and(|steps| persistent_twist_schedule_is_active(steps))
            {
                let default_bridge = BroadSatcomIntermediatePotentialBridge::default();
                let bridge = intermediate_satcom_bridge
                    .as_ref()
                    .unwrap_or(&default_bridge);
                let standard_intermediate_steps =
                    vec![IntermediatePotentialStep::Standard; observations.len()];
                let execution_intermediate_steps = intermediate_potential_steps
                    .as_deref()
                    .unwrap_or(&standard_intermediate_steps);
                let persistent_result = pool.install(|| {
                    run_stratified_filter_with_intermediate_potentials_and_persistent_twist(
                        &model,
                        bridge,
                        fuel_exhaustion_selection_guide.as_ref().expect(
                            "active persistent-twist steps require their estimator adapter",
                        ),
                        &observations,
                        &filter,
                        &plan,
                        &retention,
                        suite.resampling_policy,
                        execution_intermediate_steps,
                        fuel_exhaustion_persistent_twist_steps
                            .as_deref()
                            .expect("active persistent twist has a realized step schedule"),
                    )
                })?;
                let bridge_summary = if let Some(bridge_config) = suite.intermediate_satcom_bridge {
                    let twisted_indices = persistent_result
                        .persistent_twist_checkpoints
                        .iter()
                        .map(|checkpoint| checkpoint.observation_index)
                        .collect::<Vec<_>>();
                    let final_untwist_corrections = persistent_result
                        .persistent_twist_checkpoints
                        .iter()
                        .filter_map(|checkpoint| {
                            checkpoint
                                .final_untwist_log_evidence_correction
                                .map(|correction| (checkpoint.observation_index, correction))
                        })
                        .collect::<BTreeMap<_, _>>();
                    validate_intermediate_potential_diagnostics(
                        realized_intermediate_satcom_bridge_epochs
                            .as_deref()
                            .expect("bridge steps have a realized-epoch ledger"),
                        &persistent_result.pooled,
                        &persistent_result.intermediate_potential_checkpoints,
                        &twisted_indices,
                        &final_untwist_corrections,
                    )?;
                    let diagnostics_path =
                        seed_output.join("intermediate-potential-diagnostics.json");
                    let run_identity_sha256 =
                        broad_run_identity_sha256(&config_sha256, &family.id, seed, &input_sha256);
                    write_json(
                        &diagnostics_path,
                        &BroadIntermediatePotentialDiagnosticsArtifact {
                            schema: "mh370-broad-intermediate-potential-diagnostics-v1",
                            schema_version: 1,
                            model_family: mh370_estimator::BROAD_FLIGHT_MODEL_FAMILY,
                            guide_family: BROAD_SATCOM_INTERMEDIATE_POTENTIAL_FAMILY,
                            family: &family.id,
                            seed,
                            run_identity_sha256: &run_identity_sha256,
                            config_sha256: &config_sha256,
                            input_sha256: &input_sha256,
                            filter: &filter,
                            resampling_policy: suite.resampling_policy,
                            config: bridge_config,
                            realized_epochs: realized_intermediate_satcom_bridge_epochs
                                .as_deref()
                                .expect("bridge checkpoints have a realized-epoch ledger"),
                            potential_semantics:
                                "strictly_positive_terminal_tangent_satcom_compatibility_guide_not_scientific_evidence",
                            weighting_semantics:
                                "exact_telescoping_bridge_potential_composed_with_persistent_fuel_twist;final_endpoint_aggregate_includes_global_untwist",
                            checkpoints: &persistent_result.intermediate_potential_checkpoints,
                        },
                    )?;
                    outputs.insert(
                        format!(
                            "{}/seed-{seed}/intermediate-potential-diagnostics.json",
                            family.id
                        ),
                        sha256_file(&diagnostics_path)?,
                    );
                    Some(summarize_intermediate_potentials(
                        &persistent_result.intermediate_potential_checkpoints,
                    ))
                } else {
                    None
                };
                let execution = BroadPersistentTwistExecutionDiagnostics {
                    checkpoints: persistent_result.persistent_twist_checkpoints,
                    twisted_standard_checkpoints: persistent_result.twisted_standard_checkpoints,
                    intermediate_potential_checkpoints: persistent_result
                        .intermediate_potential_checkpoints,
                    twisted_filtering_observation_indices: persistent_result
                        .twisted_filtering_observation_indices,
                };
                (
                    persistent_result.pooled,
                    None,
                    None,
                    None,
                    bridge_summary,
                    None,
                    Some(execution),
                )
            } else if fuel_exhaustion_selection_steps
                .as_ref()
                .is_some_and(|steps| {
                    steps
                        .iter()
                        .any(|step| matches!(step, SelectionGuideStep::Guide { .. }))
                })
            {
                let default_bridge = BroadSatcomIntermediatePotentialBridge::default();
                let bridge = intermediate_satcom_bridge
                    .as_ref()
                    .unwrap_or(&default_bridge);
                let standard_intermediate_steps =
                    vec![IntermediatePotentialStep::Standard; observations.len()];
                let execution_intermediate_steps = intermediate_potential_steps
                    .as_deref()
                    .unwrap_or(&standard_intermediate_steps);
                let selection_result = pool.install(|| {
                    run_stratified_filter_with_intermediate_potentials_and_selection_guide(
                        &model,
                        bridge,
                        fuel_exhaustion_selection_guide
                            .as_ref()
                            .expect("active fuel-guide steps require their estimator adapter"),
                        &observations,
                        &filter,
                        &plan,
                        &retention,
                        suite.resampling_policy,
                        execution_intermediate_steps,
                        fuel_exhaustion_selection_steps
                            .as_deref()
                            .expect("active fuel guidance has a realized step schedule"),
                    )
                })?;
                let fuel_checkpoints = BroadFuelExhaustionSelectionCheckpoints {
                    guided_standard: selection_result.guided_standard_checkpoints,
                    intermediate_potential: selection_result.intermediate_potential_checkpoints,
                };
                let guided_indices = realized_fuel_exhaustion_selection_guide_epochs
                    .as_deref()
                    .expect("active fuel guidance has a realized-epoch ledger")
                    .iter()
                    .filter(|epoch| matches!(epoch.step, SelectionGuideStep::Guide { .. }))
                    .map(|epoch| epoch.observation_index)
                    .collect::<Vec<_>>();
                let bridge_summary = if let Some(bridge_config) = suite.intermediate_satcom_bridge {
                    validate_intermediate_potential_diagnostics(
                        realized_intermediate_satcom_bridge_epochs
                            .as_deref()
                            .expect("bridge steps have a realized-epoch ledger"),
                        &selection_result.pooled,
                        &fuel_checkpoints.intermediate_potential,
                        &guided_indices,
                        &BTreeMap::new(),
                    )?;
                    let diagnostics_path =
                        seed_output.join("intermediate-potential-diagnostics.json");
                    let run_identity_sha256 =
                        broad_run_identity_sha256(&config_sha256, &family.id, seed, &input_sha256);
                    write_json(
                            &diagnostics_path,
                            &BroadIntermediatePotentialDiagnosticsArtifact {
                                schema: "mh370-broad-intermediate-potential-diagnostics-v1",
                                schema_version: 1,
                                model_family: mh370_estimator::BROAD_FLIGHT_MODEL_FAMILY,
                                guide_family: BROAD_SATCOM_INTERMEDIATE_POTENTIAL_FAMILY,
                                family: &family.id,
                                seed,
                                run_identity_sha256: &run_identity_sha256,
                                config_sha256: &config_sha256,
                                input_sha256: &input_sha256,
                                filter: &filter,
                                resampling_policy: suite.resampling_policy,
                                config: bridge_config,
                                realized_epochs: realized_intermediate_satcom_bridge_epochs
                                    .as_deref()
                                    .expect("bridge checkpoints have a realized-epoch ledger"),
                                potential_semantics:
                                    "strictly_positive_terminal_tangent_satcom_compatibility_guide_not_scientific_evidence",
                                weighting_semantics:
                                    "exact_telescoping_h_ratio_then_endpoint_g_over_h_with_proper_candidate_output_and_fuel_selection_proposal_corrections",
                                checkpoints: &fuel_checkpoints.intermediate_potential,
                            },
                        )?;
                    outputs.insert(
                        format!(
                            "{}/seed-{seed}/intermediate-potential-diagnostics.json",
                            family.id
                        ),
                        sha256_file(&diagnostics_path)?,
                    );
                    Some(summarize_intermediate_potentials(
                        &fuel_checkpoints.intermediate_potential,
                    ))
                } else {
                    None
                };
                (
                    selection_result.pooled,
                    None,
                    None,
                    None,
                    bridge_summary,
                    Some(fuel_checkpoints),
                    None,
                )
            } else if let Some(steps) = &intermediate_potential_steps {
                let intermediate_result = pool.install(|| {
                    run_stratified_filter_with_intermediate_potentials(
                        &model,
                        intermediate_satcom_bridge
                            .as_ref()
                            .expect("bridge steps require their estimator adapter"),
                        &observations,
                        &filter,
                        &plan,
                        &retention,
                        suite.resampling_policy,
                        steps,
                    )
                })?;
                validate_intermediate_potential_diagnostics(
                    realized_intermediate_satcom_bridge_epochs
                        .as_deref()
                        .expect("bridge steps have a realized-epoch ledger"),
                    &intermediate_result.pooled,
                    &intermediate_result.intermediate_potential_checkpoints,
                    &[],
                    &BTreeMap::new(),
                )?;
                let diagnostics_path = seed_output.join("intermediate-potential-diagnostics.json");
                let run_identity_sha256 =
                    broad_run_identity_sha256(&config_sha256, &family.id, seed, &input_sha256);
                write_json(
                        &diagnostics_path,
                        &BroadIntermediatePotentialDiagnosticsArtifact {
                            schema: "mh370-broad-intermediate-potential-diagnostics-v1",
                            schema_version: 1,
                            model_family: mh370_estimator::BROAD_FLIGHT_MODEL_FAMILY,
                            guide_family: BROAD_SATCOM_INTERMEDIATE_POTENTIAL_FAMILY,
                            family: &family.id,
                            seed,
                            run_identity_sha256: &run_identity_sha256,
                            config_sha256: &config_sha256,
                            input_sha256: &input_sha256,
                            filter: &filter,
                            resampling_policy: suite.resampling_policy,
                            config: suite
                                .intermediate_satcom_bridge
                                .expect("bridge steps require their configured schedule"),
                            realized_epochs: realized_intermediate_satcom_bridge_epochs
                                .as_deref()
                                .expect("bridge steps have a realized-epoch ledger"),
                            potential_semantics:
                                "strictly_positive_terminal_tangent_satcom_compatibility_guide_not_scientific_evidence",
                            weighting_semantics:
                                "exact_telescoping_h_ratio_then_endpoint_g_over_h_with_proper_candidate_and_output_proposal_corrections",
                            checkpoints: &intermediate_result.intermediate_potential_checkpoints,
                        },
                    )?;
                outputs.insert(
                    format!(
                        "{}/seed-{seed}/intermediate-potential-diagnostics.json",
                        family.id
                    ),
                    sha256_file(&diagnostics_path)?,
                );
                let bridge_summary = summarize_intermediate_potentials(
                    &intermediate_result.intermediate_potential_checkpoints,
                );
                let fuel_checkpoints = suite.fuel_exhaustion_selection_guide.as_ref().map(|_| {
                    BroadFuelExhaustionSelectionCheckpoints {
                        guided_standard: Vec::new(),
                        intermediate_potential: intermediate_result
                            .intermediate_potential_checkpoints
                            .clone(),
                    }
                });
                let persistent_execution =
                    suite.fuel_exhaustion_persistent_twist.as_ref().map(|_| {
                        BroadPersistentTwistExecutionDiagnostics {
                            checkpoints: Vec::new(),
                            twisted_standard_checkpoints: Vec::new(),
                            intermediate_potential_checkpoints: intermediate_result
                                .intermediate_potential_checkpoints
                                .clone(),
                            twisted_filtering_observation_indices: Vec::new(),
                        }
                    });
                (
                    intermediate_result.pooled,
                    None,
                    None,
                    None,
                    Some(bridge_summary),
                    fuel_checkpoints,
                    persistent_execution,
                )
            } else {
                (
                    pool.install(|| {
                        run_stratified_filter_with_snapshot_retention_and_resampling_policy(
                            &model,
                            &observations,
                            &filter,
                            &plan,
                            &retention,
                            suite.resampling_policy,
                        )
                    })?,
                    None,
                    None,
                    None,
                    None,
                    suite.fuel_exhaustion_selection_guide.as_ref().map(|_| {
                        BroadFuelExhaustionSelectionCheckpoints {
                            guided_standard: Vec::new(),
                            intermediate_potential: Vec::new(),
                        }
                    }),
                    suite.fuel_exhaustion_persistent_twist.as_ref().map(|_| {
                        BroadPersistentTwistExecutionDiagnostics {
                            checkpoints: Vec::new(),
                            twisted_standard_checkpoints: Vec::new(),
                            intermediate_potential_checkpoints: Vec::new(),
                            twisted_filtering_observation_indices: Vec::new(),
                        }
                    }),
                )
            };
            let posterior_state_diversity = summarize_posterior_state_diversity(&result)?;
            let pending_renewal_refresh_summary = if let Some(config) =
                suite.pending_renewal_refresh.as_ref()
            {
                let realized = realized_pending_renewal_refresh_epochs
                    .as_deref()
                    .expect("configured pending-renewal refresh has a realized ledger");
                let move_checkpoints = pending_renewal_refresh_checkpoints
                    .as_deref()
                    .expect("configured pending-renewal refresh has an execution ledger");
                validate_pending_renewal_refresh_diagnostics(
                    config,
                    realized,
                    &plan,
                    &result,
                    move_checkpoints,
                )?;
                let posterior_survivor_summary = summarize_pending_renewal_refresh(&result)?;
                let diagnostics_path = seed_output.join("pending-renewal-refresh-diagnostics.json");
                let run_identity_sha256 =
                    broad_run_identity_sha256(&config_sha256, &family.id, seed, &input_sha256);
                write_json(
                    &diagnostics_path,
                    &BroadPendingRenewalRefreshDiagnosticsArtifact {
                        schema: "mh370-broad-pending-renewal-refresh-diagnostics-v2",
                        schema_version: 2,
                        model_family: mh370_estimator::BROAD_FLIGHT_MODEL_FAMILY,
                        refresh_family: BROAD_PENDING_RENEWAL_REFRESH_FAMILY,
                        move_rng_domain: STRATIFIED_POST_RESAMPLE_MOVE_RNG_DOMAIN,
                        family: &family.id,
                        seed,
                        run_identity_sha256: &run_identity_sha256,
                        config_sha256: &config_sha256,
                        input_sha256: &input_sha256,
                        filter: &filter,
                        resampling_policy: suite.resampling_policy,
                        plan: &plan,
                        config,
                        resolved_estimator_config: config.resolved(),
                        refresh_descriptor: config.resolved().stable_descriptor(),
                        inference_descriptor: pending_renewal_refresh_inference_descriptor(config),
                        realized_epochs: realized,
                        schedule_semantics:
                            "exact_post_composition_observation_id_to_apply_or_inactive;apply_is_after_the_named_physical_observation_and_only_before_a_following_powered_transition",
                        move_semantics:
                            "exact_target_invariant_auxiliary_clock_gibbs_refresh_of_lateral_speed_and_altitude_pending_shape_one_renewals_after_actual_ordinary_posterior_resampling",
                        weighting_and_evidence_semantics:
                            "no_log_weight_logz_or_scientific_evidence_term;physical_bto_bfo_likelihoods_and_filter_evidence_are_unchanged_by_the_move",
                        move_log_weight_logz_and_evidence_adjustment: 0.0,
                        diagnostic_population_semantics:
                            "pf_epoch_checkpoints_are_exact_hook_workload;finite_log_weight_particles_include_normalized_weights_that_underflow_to_zero;strictly_positive_normalized_weight_particles_require_exp_log_weight_greater_than_zero;posterior_weighted_refresh_counters_describe_retained_survivor_lineages_and_must_not_be_summed_to_reconstruct_prior_epoch_invocations",
                        exact_state_clone_semantics:
                            "finite_log_weight_final_particles_grouped_by_exact_canonical_json_bytes_of_the_complete_broad_flight_state_including_disposable_pending_next_event_clocks_and_refresh_diagnostics;collision_diagnostic_not_an_independence_proof",
                        posterior_state_diversity: &posterior_state_diversity,
                        physical_filter_checkpoints: &result.checkpoints,
                        post_resample_move_checkpoints: move_checkpoints,
                        posterior_survivor_summary: &posterior_survivor_summary,
                    },
                )?;
                outputs.insert(
                    format!(
                        "{}/seed-{seed}/pending-renewal-refresh-diagnostics.json",
                        family.id
                    ),
                    sha256_file(&diagnostics_path)?,
                );
                Some(posterior_survivor_summary)
            } else {
                None
            };
            validate_satcom_event_mark_guide_diagnostics(
                suite.satcom_event_mark_guide.as_ref(),
                &result,
            )?;
            let satcom_event_mark_guide = if let Some(config) =
                suite.satcom_event_mark_guide.as_ref()
            {
                let posterior_survivor_summary = summarize_satcom_event_mark_guide(&result)?;
                let diagnostics_path = seed_output.join("satcom-event-mark-guide-diagnostics.json");
                let run_identity_sha256 =
                    broad_run_identity_sha256(&config_sha256, &family.id, seed, &input_sha256);
                write_json(
                    &diagnostics_path,
                    &BroadSatcomEventMarkGuideDiagnosticsArtifact {
                        schema: "mh370-broad-satcom-event-mark-guide-diagnostics-v1",
                        schema_version: 1,
                        model_family: mh370_estimator::BROAD_FLIGHT_MODEL_FAMILY,
                        guide_family: BROAD_SATCOM_EVENT_MARK_GUIDE_FAMILY,
                        family: &family.id,
                        seed,
                        run_identity_sha256: &run_identity_sha256,
                        config_sha256: &config_sha256,
                        input_sha256: &input_sha256,
                        filter: &filter,
                        resampling_policy: suite.resampling_policy,
                        config,
                        resolved_estimator_config: config.resolved(),
                        guide_descriptor: satcom_event_mark_guide_inference_descriptor(config),
                        realized_epochs: realized_satcom_event_mark_guide_epochs
                            .as_deref()
                            .expect("configured SATCOM event-mark guide has a realized ledger"),
                        eligibility_semantics:
                            "lateral_events_only_with_minimum_lead_less_than_or_equal_to_endpoint_minus_event_time_less_than_or_equal_to_maximum_lookback;configured_exact_satcom_endpoint_id_must_realize_once",
                        proposal_semantics:
                            "k_independent_prior_marks_then_q_j_equals_epsilon_over_k_plus_one_minus_epsilon_times_softmax_beta_times_enabled_endpoint_proxy_log_likelihood",
                        proxy_semantics:
                            "frozen_selected_command_to_physical_endpoint_with_future_event_clocks_disabled;enabled_bto_and_predictive_bfo_only;beta_zero_or_epsilon_one_skips_projection_and_scores_valid_candidates_uniformly;computational_guidance_not_pilot_intent_or_trajectory_evidence",
                        correction_semantics:
                            "incremental_log_prior_over_proposal_is_applied_exactly_once_by_each_physical_transition;state_cumulative_correction_is_diagnostic_only_and_must_not_be_reapplied",
                        evidence_semantics:
                            "proposal_only_no_additional_satcom_row_or_scientific_likelihood;physical_endpoint_bto_and_bfo_are_each_observed_once",
                        root_pool_composition_semantics:
                            "root_pool_l_counts_physical_transition_candidates_only;event_mark_k_is_internal_to_each_transition_and_does_not_multiply_or_redefine_root_pool_candidate_counts",
                        diagnostic_population_semantics:
                            "posterior_weighted_statistics_describe_retained_selected_lineages_and_not_all_discarded_proposal_workload;ess_and_entropy_are_reported_as_event_means_from_lineage_sums",
                        physical_filter_checkpoints: &result.checkpoints,
                        posterior_survivor_summary: &posterior_survivor_summary,
                    },
                )?;
                outputs.insert(
                    format!(
                        "{}/seed-{seed}/satcom-event-mark-guide-diagnostics.json",
                        family.id
                    ),
                    sha256_file(&diagnostics_path)?,
                );
                Some(posterior_survivor_summary)
            } else {
                None
            };
            let fuel_exhaustion_selection_guide_smc = if let Some(config) =
                suite.fuel_exhaustion_selection_guide.as_ref()
            {
                let realized = realized_fuel_exhaustion_selection_guide_epochs
                    .as_deref()
                    .expect("configured fuel guide has a realized-epoch ledger");
                let selection_checkpoints = fuel_selection_checkpoints
                    .as_ref()
                    .expect("configured fuel guide has an execution-diagnostics ledger");
                validate_fuel_exhaustion_selection_guide_diagnostics(
                    realized,
                    realized_intermediate_satcom_bridge_epochs.as_deref(),
                    &result,
                    selection_checkpoints,
                    config.potential_floor,
                )?;
                let window = fuel_exhaustion_guide_source
                    .as_ref()
                    .map(|(_, window)| *window)
                    .expect("configured fuel guide has a resolved canonical window");
                let point = BroadFuelExhaustionSelectionGuidePoint {
                    window_start: Seconds(window.window_start_s),
                    window_end: Seconds(window.window_end_s),
                };
                let posterior_population = evaluate_fuel_exhaustion_selection_posterior(
                    seed,
                    fuel_exhaustion_selection_guide
                        .as_ref()
                        .expect("configured fuel guide has an estimator adapter"),
                    &model,
                    observations
                        .last()
                        .expect("broad observation sequence is non-empty"),
                    point,
                    &result,
                )?;
                let diagnostics_path =
                    seed_output.join("fuel-exhaustion-selection-guide-diagnostics.json");
                let run_identity_sha256 =
                    broad_run_identity_sha256(&config_sha256, &family.id, seed, &input_sha256);
                write_json(
                    &diagnostics_path,
                    &BroadFuelExhaustionSelectionGuideDiagnosticsArtifact {
                        schema: "mh370-broad-fuel-exhaustion-selection-guide-diagnostics-v1",
                        schema_version: 1,
                        model_family: mh370_estimator::BROAD_FLIGHT_MODEL_FAMILY,
                        guide_family: BROAD_FUEL_EXHAUSTION_SELECTION_GUIDE_FAMILY,
                        family: &family.id,
                        seed,
                        run_identity_sha256: &run_identity_sha256,
                        config_sha256: &config_sha256,
                        input_sha256: &input_sha256,
                        filter: &filter,
                        resampling_policy: suite.resampling_policy,
                        config,
                        resolved_estimator_config: config.resolved(),
                        guide_descriptor: config.resolved().stable_descriptor(),
                        resolved_window: window,
                        realized_epochs: realized,
                        proposal_semantics:
                            "strictly_positive_frozen_operating_point_compatibility_selection_with_exact_target_over_proposal_correction",
                        evidence_semantics:
                            "computational_proposal_only_no_fuel_logon_or_satcom_likelihood_and_no_change_to_the_evidence_ledger",
                        canonical_source_semantics:
                            "hash_locked_full_satcom_source_supplies_window_times_only;the_window_rows_are_not_inserted_consumed_or_scored_by_the_guide",
                        guided_standard_checkpoints: &selection_checkpoints.guided_standard,
                        intermediate_potential_checkpoints: &selection_checkpoints
                            .intermediate_potential,
                        final_posterior: &posterior_population.summary,
                    },
                )?;
                outputs.insert(
                    format!(
                        "{}/seed-{seed}/fuel-exhaustion-selection-guide-diagnostics.json",
                        family.id
                    ),
                    sha256_file(&diagnostics_path)?,
                );
                let seed_summary = summarize_fuel_exhaustion_selection_guide(
                    realized,
                    realized_intermediate_satcom_bridge_epochs.as_deref(),
                    selection_checkpoints,
                    posterior_population.summary.clone(),
                );
                fuel_exhaustion_posterior_populations.push(posterior_population);
                Some(seed_summary)
            } else {
                None
            };
            let fuel_exhaustion_persistent_twist_smc = if let Some(config) =
                suite.fuel_exhaustion_persistent_twist.as_ref()
            {
                let realized = realized_fuel_exhaustion_persistent_twist_epochs
                    .as_deref()
                    .expect("configured persistent twist has a realized-epoch ledger");
                let execution = persistent_twist_execution
                    .as_ref()
                    .expect("configured persistent twist has an execution-diagnostics ledger");
                let recomposition = validate_persistent_twist_diagnostics(
                    realized,
                    realized_intermediate_satcom_bridge_epochs.as_deref(),
                    &result,
                    execution,
                )?;
                let window = fuel_exhaustion_guide_source
                    .as_ref()
                    .map(|(_, window)| *window)
                    .expect("configured persistent twist has a resolved canonical window");
                let point = BroadFuelExhaustionSelectionGuidePoint {
                    window_start: Seconds(window.window_start_s),
                    window_end: Seconds(window.window_end_s),
                };
                let guide = fuel_exhaustion_selection_guide
                    .as_ref()
                    .expect("configured persistent twist has an estimator adapter");
                let posterior_population = evaluate_fuel_exhaustion_selection_posterior(
                    seed,
                    guide,
                    &model,
                    observations
                        .last()
                        .expect("broad observation sequence is non-empty"),
                    point,
                    &result,
                )?;
                let diagnostics_path = seed_output.join("persistent-twist-diagnostics.json");
                let run_identity_sha256 =
                    broad_run_identity_sha256(&config_sha256, &family.id, seed, &input_sha256);
                write_json(
                    &diagnostics_path,
                    &BroadFuelExhaustionPersistentTwistDiagnosticsArtifact {
                        schema: "mh370-broad-fuel-exhaustion-persistent-twist-diagnostics-v1",
                        schema_version: 1,
                        model_family: mh370_estimator::BROAD_FLIGHT_MODEL_FAMILY,
                        twist_family: BROAD_FUEL_EXHAUSTION_PERSISTENT_TWIST_FAMILY,
                        family: &family.id,
                        seed,
                        run_identity_sha256: &run_identity_sha256,
                        config_sha256: &config_sha256,
                        input_sha256: &input_sha256,
                        filter: &filter,
                        resampling_policy: suite.resampling_policy,
                        config,
                        resolved_estimator_config: config.resolved(),
                        twist_descriptor: guide.persistent_twist_stable_descriptor(),
                        resolved_window: window,
                        realized_epochs: realized,
                        proposal_semantics: if persistent_twist_schedule_is_active(
                            fuel_exhaustion_persistent_twist_steps
                                .as_deref()
                                .expect("configured persistent twist has a step schedule"),
                        ) {
                            "strictly_positive_frozen_operating_point_future_fuel_compatibility_potential_carried_across_physical_epochs"
                        } else {
                            "potential_floor_one_realizes_an_all-inactive_schedule_and_executes_the_legacy_filter_path"
                        },
                        evidence_semantics:
                            "computational_proposal_only_no_fuel_logon_or_satcom_likelihood_and_no_change_to_the_bto_bfo_evidence_ledger",
                        finalization_semantics: if execution.checkpoints.is_empty() {
                            "neutral_all-inactive_schedule_requires_no_untwist;legacy_filter_outputs_are_preserved"
                        } else {
                            "single_global_inverse_potential_reweight_without_resampling_at_fit_through_returns_ordinary_physical_filter_weights_snapshots_evidence_and_strata"
                        },
                        terminal_semantics:
                            "terminal_inference_must_consume_final_physical_weights_and_must_not_apply_another_persistent_potential_correction",
                        canonical_source_semantics:
                            "hash_locked_full_satcom_source_supplies_strict_window_times_only;the_window_rows_are_not_inserted_consumed_or_scored_by_the_twist",
                        wrapper_checkpoints: &execution.checkpoints,
                        twisted_standard_checkpoints: &execution.twisted_standard_checkpoints,
                        intermediate_potential_checkpoints: &execution
                            .intermediate_potential_checkpoints,
                        nested_checkpoint_semantics:
                            "candidate_pool_diagnostics_are_pre_global-untwist_twisted-target_semantics;the_final_wrapper_filter_checkpoint_and_final_bridge_endpoint_aggregate_include_the_global_physical_untwist",
                        twisted_filtering_observation_indices: &execution
                            .twisted_filtering_observation_indices,
                        evidence_recomposition: &recomposition,
                        final_posterior: &posterior_population.summary,
                    },
                )?;
                outputs.insert(
                    format!(
                        "{}/seed-{seed}/persistent-twist-diagnostics.json",
                        family.id
                    ),
                    sha256_file(&diagnostics_path)?,
                );
                let seed_summary = summarize_fuel_exhaustion_persistent_twist(
                    realized,
                    realized_intermediate_satcom_bridge_epochs.as_deref(),
                    execution,
                    posterior_population.summary.clone(),
                );
                fuel_exhaustion_posterior_populations.push(posterior_population);
                Some(seed_summary)
            } else {
                None
            };
            let checkpoints_path = seed_output.join("checkpoints.json");
            if suite.outputs.write_posterior_csv {
                let posterior_path = seed_output.join("posterior.csv");
                atomic_write(&posterior_path, &posterior_csv(&result))?;
                outputs.insert(
                    format!("{}/seed-{seed}/posterior.csv", family.id),
                    sha256_file(&posterior_path)?,
                );
            }
            write_json(&checkpoints_path, &result.checkpoints)?;
            if suite.outputs.write_posterior_handoff {
                let handoff_path = seed_output.join("posterior-handoff.json");
                let handoff = filtering_handoff(
                    BroadHandoffContext {
                        suite: &suite,
                        family,
                        model: &model_config,
                        plan: &plan,
                        observations: &observations,
                        input_sha256: &input_sha256,
                        config_sha256: &config_sha256,
                        fuel_exhaustion_selection_guide_window: fuel_exhaustion_guide_source
                            .as_ref()
                            .map(|(_, window)| *window),
                    },
                    seed,
                    &result,
                )?;
                write_json(&handoff_path, &handoff)?;
                outputs.insert(
                    format!("{}/seed-{seed}/posterior-handoff.json", family.id),
                    sha256_file(&handoff_path)?,
                );
            }
            let seed_summary = summarize(
                &family.id,
                seed,
                &result,
                posterior_state_diversity,
                BroadSeedInferenceSummaries {
                    island_smc,
                    global_transition_pool_smc,
                    root_stratified_transition_pool_smc,
                    satcom_event_mark_guide,
                    pending_renewal_refresh: pending_renewal_refresh_summary,
                    intermediate_satcom_bridge_smc,
                    fuel_exhaustion_selection_guide_smc,
                    fuel_exhaustion_persistent_twist_smc,
                },
            );
            write_json(&seed_output.join("summary.json"), &seed_summary)?;
            seed_posterior_populations.push(seed_posterior_population(seed, &result));
            for name in ["checkpoints.json", "summary.json"] {
                let relative = format!("{}/seed-{seed}/{name}", family.id);
                outputs.insert(relative, sha256_file(&seed_output.join(name))?);
            }
            seed_summaries.push(seed_summary);
        }
        let (pooled_points, independent_seed_pooling) =
            pool_independent_seed_posteriors(seed_posterior_populations)?;
        if let Some(pooling) = &independent_seed_pooling {
            independent_seed_pooling_by_family
                .as_mut()
                .expect("a multi-seed run has a pooling ledger")
                .insert(family.id.clone(), pooling.clone());
        }
        let fuel_exhaustion_guide_posterior = suite
            .fuel_exhaustion_selection_guide
            .as_ref()
            .or(suite.fuel_exhaustion_persistent_twist.as_ref())
            .map(|_| {
                pool_fuel_exhaustion_selection_posteriors(
                    &fuel_exhaustion_posterior_populations,
                    independent_seed_pooling.as_ref(),
                )
            })
            .transpose()?;
        let document = report_document(
            &suite,
            &model_config,
            family,
            &seed_summaries,
            independent_seed_pooling.as_ref(),
            BroadFuelExhaustionSelectionGuideReportContext {
                posterior: fuel_exhaustion_guide_posterior.as_ref(),
                window: fuel_exhaustion_guide_source
                    .as_ref()
                    .map(|(_, window)| *window),
            },
            pooled_points,
        );
        let pdf_path = family_output.join("report.pdf");
        let svg_path = family_output.join("posterior.svg");
        let png_path = family_output.join("posterior.png");
        atomic_write(&pdf_path, &build_pdf(&document)?)?;
        atomic_write(&svg_path, &build_posterior_svg(&document)?)?;
        atomic_write(&png_path, &build_accident_panel_png(&document)?)?;
        for name in ["report.pdf", "posterior.svg", "posterior.png"] {
            outputs.insert(
                format!("{}/{name}", family.id),
                sha256_file(&family_output.join(name))?,
            );
        }
        family_summaries.push(BroadFamilySummary {
            id: family.id.clone(),
            use_bfo: family.use_bfo,
            bfo_sd_override_hz: family.bfo_sd_override_hz,
            realized_proposal_epochs: proposal_epochs,
            realized_global_transition_pool_epochs,
            realized_root_stratified_transition_pool_epochs,
            realized_satcom_event_mark_guide_epochs,
            realized_pending_renewal_refresh_epochs,
            realized_intermediate_satcom_bridge_epochs,
            realized_fuel_exhaustion_selection_guide_epochs,
            fuel_exhaustion_selection_guide_posterior: suite
                .fuel_exhaustion_selection_guide
                .as_ref()
                .and(fuel_exhaustion_guide_posterior.clone()),
            realized_fuel_exhaustion_persistent_twist_epochs,
            fuel_exhaustion_persistent_twist_posterior: suite
                .fuel_exhaustion_persistent_twist
                .as_ref()
                .and(fuel_exhaustion_guide_posterior),
            independent_seed_pooling,
            seeds: seed_summaries,
        });
    }

    let mut limitations = vec![
        "Fuel exhaustion, terminal dynamics, R600 and later evidence do not weight this filtering artifact; an enabled local guide or persistent twist is proposal-only, is exactly corrected, and has a diagnostic compatibility summary"
            .to_string(),
        "The filtering PDF for the configured fit-through epoch deliberately retains paths whose diagnostic fuel state exhausts early; only the later fuel-conditioned/smoothed branch may remove them"
            .to_string(),
        "Model-family prior probabilities are declared choices and have not been empirically calibrated"
            .to_string(),
    ];
    if suite.satcom_event_mark_guide.is_some() {
        limitations.extend([
            "SATCOM event-mark proposal diagnostics are posterior-survivor summaries; they do not measure every candidate evaluated and discarded during filtering"
                .to_string(),
            "Frozen-command SATCOM endpoint projection is proposal-only computational guidance, not pilot-intent or trajectory evidence"
                .to_string(),
        ]);
    }
    if suite.pending_renewal_refresh.is_some() {
        limitations.extend([
            "Pending-renewal refresh diagnostics are posterior-survivor lineage summaries; exact per-epoch hook calls are recorded separately and later resampling may clone or discard earlier refreshed lineages"
                .to_string(),
            "Pending manoeuvre clocks are disposable auxiliary future randomness, not inferred pilot intent or trajectory evidence; each independent terminal continuation must refresh configured clocks before propagation"
                .to_string(),
        ]);
    }
    let summary = BroadSuiteSummary {
        schema_version: 1,
        name: suite.name.clone(),
        status: "conditional_broad_filter_complete".to_string(),
        model_family: mh370_estimator::BROAD_FLIGHT_MODEL_FAMILY.to_string(),
        fuel_flow_initialization_design: suite.model.fuel_flow_initialization_design,
        baseline_proposal_candidates: suite.model.proposal_candidates,
        proposal_candidate_schedule: suite.model.proposal_candidate_schedule.clone(),
        resampling_policy: suite.resampling_policy,
        island_plan: island_plan.clone(),
        global_transition_pool_schedule: suite.global_transition_pool.clone(),
        root_stratified_transition_pool: suite.root_stratified_transition_pool.clone(),
        satcom_event_mark_guide: suite.satcom_event_mark_guide.clone(),
        satcom_event_mark_guide_descriptor: satcom_event_mark_guide_descriptor.clone(),
        pending_renewal_refresh: suite.pending_renewal_refresh.clone(),
        pending_renewal_refresh_descriptor: pending_renewal_refresh_descriptor.clone(),
        intermediate_satcom_bridge: suite.intermediate_satcom_bridge,
        fuel_exhaustion_selection_guide: suite.fuel_exhaustion_selection_guide.clone(),
        fuel_exhaustion_persistent_twist: suite.fuel_exhaustion_persistent_twist.clone(),
        fuel_exhaustion_persistent_twist_descriptor: fuel_exhaustion_persistent_twist_descriptor
            .clone(),
        resolved_fuel_exhaustion_guide_window: fuel_exhaustion_guide_source
            .as_ref()
            .map(|(_, window)| *window),
        families: family_summaries,
        limitations,
    };
    let summary_path = output.join("summary.json");
    write_json(&summary_path, &summary)?;
    outputs.insert("summary.json".to_string(), sha256_file(&summary_path)?);
    let manifest = BroadRunManifest {
        schema_version: 1,
        command: "estimate-broad-flight",
        status: summary.status.clone(),
        fuel_flow_initialization_design: suite.model.fuel_flow_initialization_design,
        baseline_proposal_candidates: suite.model.proposal_candidates,
        proposal_candidate_schedule: suite.model.proposal_candidate_schedule.clone(),
        island_plan,
        global_transition_pool_schedule: suite.global_transition_pool,
        realized_global_transition_pool_epochs_by_family,
        root_stratified_transition_pool: suite.root_stratified_transition_pool,
        realized_root_stratified_transition_pool_epochs_by_family,
        satcom_event_mark_guide: suite.satcom_event_mark_guide,
        satcom_event_mark_guide_descriptor,
        realized_satcom_event_mark_guide_epochs_by_family,
        pending_renewal_refresh: suite.pending_renewal_refresh,
        pending_renewal_refresh_descriptor,
        realized_pending_renewal_refresh_epochs_by_family,
        intermediate_satcom_bridge: suite.intermediate_satcom_bridge,
        fuel_exhaustion_selection_guide: suite.fuel_exhaustion_selection_guide,
        fuel_exhaustion_persistent_twist: suite.fuel_exhaustion_persistent_twist,
        fuel_exhaustion_persistent_twist_descriptor,
        resolved_fuel_exhaustion_guide_window: fuel_exhaustion_guide_source
            .as_ref()
            .map(|(_, window)| *window),
        realized_intermediate_satcom_bridge_epochs_by_family,
        realized_fuel_exhaustion_selection_guide_epochs_by_family,
        realized_fuel_exhaustion_persistent_twist_epochs_by_family,
        independent_seed_pooling_by_family,
        realized_proposal_epochs_by_family,
        executable_sha256: executable_sha256()?,
        config_path: config_path.display().to_string(),
        config_sha256,
        input_sha256,
        elapsed_seconds: started.elapsed().as_secs_f64(),
        threads,
        outputs,
    };
    write_json(&output.join("run-manifest.json"), &manifest)?;
    println!(
        "status={} families={} seeds={} particles_per_seed={} elapsed_s={:.3} summary={}",
        summary.status,
        suite.families.len(),
        suite.seeds.len(),
        suite.filter.particles,
        manifest.elapsed_seconds,
        summary_path.display()
    );
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;
    use mh370_domain::{AircraftState, Degrees, Feet, FeetPerMinute, Knots, LatLon};
    use mh370_dynamics::{
        PendingRenewal, PoweredEventClocks, PoweredEventCounters, PoweredFlightCommand,
        PoweredFlightState,
    };
    use mh370_end_of_flight::Kilograms;
    use mh370_estimator::{
        BroadFlightParticleStatus, BroadFlightScores, BroadFuelDiagnosticStatus,
        BroadPendingRenewalRefreshDiagnostics, BROAD_POSTERIOR_HANDOFF_SCHEMA_VERSION,
    };
    use mh370_particle_filter::{
        FilterCheckpoint, FilterSnapshot, GlobalTransitionPoolStratumDiagnostics,
        IntermediatePotentialBridgePoint, IntermediatePotentialEndpointCheckpoint,
        IntermediatePotentialPointCheckpoint, PersistentTwistPopulationDiagnostics,
        RootStratifiedCandidatePoolStratumDiagnostics, StratifiedPostResampleMoveStratumCheckpoint,
        StratumDiagnostics,
    };
    use mh370_satcom::BfoBiasState;

    #[test]
    fn posterior_diagnostic_csv_fields_are_stable_and_aligned() {
        let mut diagnostics = BroadFlightDiagnostics {
            integration_segments: 3,
            powered_target_clamp_count: 4,
            fuel_outside_martin_domain_seconds: 15.0,
            fuel_flow_multiplier_bound_hits: 16,
            powered_thrust_proxy_extrapolation_segments: 17,
            powered_thrust_proxy_cap_segments: 18,
            powered_additional_drag_required_segments: 19,
            ..BroadFlightDiagnostics::default()
        };
        diagnostics
            .powered_boundary_seconds
            .stall_or_minimum_mach_floor = 5.0;
        diagnostics.powered_boundary_seconds.vmo_or_mmo_ceiling = 6.0;
        diagnostics.powered_boundary_seconds.bank = 7.0;
        diagnostics.powered_boundary_seconds.roll_rate = 8.0;
        diagnostics.powered_boundary_seconds.climb_rate = 9.0;
        diagnostics.powered_boundary_seconds.descent_rate = 10.0;
        diagnostics.powered_boundary_seconds.vertical_acceleration = 11.0;
        diagnostics.powered_boundary_seconds.lower_altitude = 12.0;
        diagnostics.powered_boundary_seconds.upper_altitude = 13.0;
        diagnostics.powered_boundary_seconds.magnetic_altitude_clamp = 14.0;
        diagnostics.satcom_event_mark_guide = BroadSatcomEventMarkGuideDiagnostics {
            eligible_lateral_events: 20,
            guided_lateral_events: 21,
            candidate_marks: 22,
            finite_candidate_scores: 23,
            materialization_failures: 24,
            proxy_projection_successes: 25,
            proxy_projection_failures: 26,
            proxy_projection_skipped_candidates: 27,
            all_scores_negative_infinity_events: 28,
            sum_selection_effective_sample_size: 29.0,
            sum_selection_entropy_nats: 30.0,
            minimum_selected_probability: Some(31.0),
            maximum_selected_probability: Some(32.0),
            minimum_event_log_prior_over_proposal: Some(33.0),
            maximum_event_log_prior_over_proposal: Some(34.0),
            minimum_lead_seconds: Some(35.0),
            maximum_lead_seconds: Some(36.0),
            sum_log_candidate_count: 37.0,
            sum_selected_log_probability: 38.0,
            cumulative_log_prior_over_proposal: 39.0,
            sum_minimum_log_prior_over_proposal: 40.0,
            sum_maximum_log_prior_over_proposal: 41.0,
        };

        let suffix = posterior_diagnostic_csv_suffix(1.0, 2.0, diagnostics);
        let fields = suffix
            .strip_prefix(',')
            .unwrap()
            .split(',')
            .collect::<Vec<_>>();
        let names = POSTERIOR_DIAGNOSTIC_CSV_HEADER
            .split(',')
            .collect::<Vec<_>>();
        let expected = [
            ("target_mach", 1.0),
            ("target_pressure_altitude_ft", 2.0),
            ("integration_segments", 3.0),
            ("powered_target_clamp_count", 4.0),
            ("powered_boundary_stall_or_minimum_mach_floor_s", 5.0),
            ("powered_boundary_vmo_or_mmo_ceiling_s", 6.0),
            ("powered_boundary_bank_s", 7.0),
            ("powered_boundary_roll_rate_s", 8.0),
            ("powered_boundary_climb_rate_s", 9.0),
            ("powered_boundary_descent_rate_s", 10.0),
            ("powered_boundary_vertical_acceleration_s", 11.0),
            ("powered_boundary_lower_altitude_s", 12.0),
            ("powered_boundary_upper_altitude_s", 13.0),
            ("powered_boundary_magnetic_altitude_clamp_s", 14.0),
            ("fuel_outside_martin_domain_seconds", 15.0),
            ("fuel_flow_multiplier_bound_hits", 16.0),
            ("powered_thrust_proxy_extrapolation_segments", 17.0),
            ("powered_thrust_proxy_cap_segments", 18.0),
            ("powered_additional_drag_required_segments", 19.0),
            ("satcom_event_mark_guide_eligible_lateral_events", 20.0),
            ("satcom_event_mark_guide_guided_lateral_events", 21.0),
            ("satcom_event_mark_guide_candidate_marks", 22.0),
            ("satcom_event_mark_guide_finite_candidate_scores", 23.0),
            ("satcom_event_mark_guide_materialization_failures", 24.0),
            ("satcom_event_mark_guide_proxy_projection_successes", 25.0),
            ("satcom_event_mark_guide_proxy_projection_failures", 26.0),
            (
                "satcom_event_mark_guide_proxy_projection_skipped_candidates",
                27.0,
            ),
            (
                "satcom_event_mark_guide_all_scores_negative_infinity_events",
                28.0,
            ),
            (
                "satcom_event_mark_guide_sum_selection_effective_sample_size",
                29.0,
            ),
            ("satcom_event_mark_guide_sum_selection_entropy_nats", 30.0),
            ("satcom_event_mark_guide_minimum_selected_probability", 31.0),
            ("satcom_event_mark_guide_maximum_selected_probability", 32.0),
            (
                "satcom_event_mark_guide_minimum_event_log_prior_over_proposal",
                33.0,
            ),
            (
                "satcom_event_mark_guide_maximum_event_log_prior_over_proposal",
                34.0,
            ),
            ("satcom_event_mark_guide_minimum_lead_seconds", 35.0),
            ("satcom_event_mark_guide_maximum_lead_seconds", 36.0),
            ("satcom_event_mark_guide_sum_log_candidate_count", 37.0),
            ("satcom_event_mark_guide_sum_selected_log_probability", 38.0),
            (
                "satcom_event_mark_guide_cumulative_log_prior_over_proposal",
                39.0,
            ),
            (
                "satcom_event_mark_guide_sum_minimum_log_prior_over_proposal",
                40.0,
            ),
            (
                "satcom_event_mark_guide_sum_maximum_log_prior_over_proposal",
                41.0,
            ),
        ];
        assert_eq!(names.len(), expected.len());
        assert_eq!(fields.len(), expected.len());
        for (((name, field), (expected_name, expected_value)), index) in
            names.iter().zip(fields).zip(expected).zip(0..)
        {
            assert_eq!(*name, expected_name, "header mismatch at column {index}");
            assert_eq!(
                field.parse::<f64>().unwrap(),
                expected_value,
                "value mismatch for {name}"
            );
        }
    }

    #[test]
    fn checked_in_broad_pilot_preserves_fuel_support_in_one_hundred_strata() {
        let text = include_str!("../../../configs/mh370-broad-powered-flight-pilot.toml");
        let suite: BroadSuiteConfig = toml::from_str(text).unwrap();
        validate_suite(&suite).unwrap();
        assert!(suite.outputs.write_posterior_csv);
        assert!(suite.outputs.write_posterior_handoff);
        assert_eq!(suite.islands, None);
        assert_eq!(suite.global_transition_pool, None);
        assert_eq!(suite.root_stratified_transition_pool, None);
        assert_eq!(suite.satcom_event_mark_guide, None);
        assert_eq!(suite.intermediate_satcom_bridge, None);
        assert_eq!(suite.resampling_policy.uniform_root_mixture_epsilon, 0.0);
        assert_eq!(
            suite.model.proposal_candidate_schedule,
            BroadProposalCandidateSchedule::Constant
        );
        assert_eq!(
            suite.model.fuel_flow_initialization_design,
            BroadFuelFlowInitializationDesign::IndependentLogUniform
        );
        let (model, plan, fuel_overrides) = expand_model_and_plan(&suite).unwrap();
        assert_eq!(model.strata.len(), 100);
        assert_eq!(plan.strata.len(), 100);
        assert_eq!(fuel_overrides.len(), 100);
        assert_eq!(
            plan.strata
                .iter()
                .map(|entry| entry.particles)
                .sum::<usize>(),
            20_000
        );
        assert!(
            (plan
                .strata
                .iter()
                .map(|entry| entry.log_prior_probability.exp())
                .sum::<f64>()
                - 1.0)
                .abs()
                < 1.0e-12
        );
        let mut represented = fuel_overrides
            .iter()
            .map(|entry| {
                let allocation = plan
                    .strata
                    .iter()
                    .find(|allocation| allocation.id == entry.stratum)
                    .unwrap();
                (
                    entry.fuel_uncertainty.flow_scale_log_uniform,
                    allocation.log_prior_probability.exp(),
                )
            })
            .collect::<Vec<_>>();
        represented.sort_by(|first, second| first.0.minimum.total_cmp(&second.0.minimum));
        assert_eq!(represented.first().unwrap().0.minimum, 0.9);
        assert_eq!(represented.last().unwrap().0.maximum, 1.1);
    }

    #[test]
    fn log_space_latin_hypercube_uses_only_twenty_structural_strata() {
        let text = include_str!("../../../configs/mh370-broad-powered-flight-pilot.toml");
        let mut suite: BroadSuiteConfig = toml::from_str(text).unwrap();
        suite.model.fuel_flow_initialization_design =
            BroadFuelFlowInitializationDesign::LogSpaceLatinHypercube;
        suite.model.fuel_flow_support_strata.clear();
        validate_suite(&suite).unwrap();
        let (model, plan, fuel_overrides) = expand_model_and_plan(&suite).unwrap();
        assert_eq!(model.strata.len(), 20);
        assert_eq!(plan.strata.len(), 20);
        assert!(fuel_overrides.is_empty());
        assert_eq!(
            plan.strata
                .iter()
                .map(|allocation| allocation.particles)
                .sum::<usize>(),
            suite.filter.particles
        );
        assert!(model
            .strata
            .iter()
            .all(|stratum| !stratum.name.contains("fuel-flow-support")));
        assert!(
            (plan
                .strata
                .iter()
                .map(|entry| entry.log_prior_probability.exp())
                .sum::<f64>()
                - 1.0)
                .abs()
                < 1.0e-12
        );
    }

    #[test]
    fn log_space_latin_hypercube_rejects_legacy_fuel_support_partitions() {
        let text = include_str!("../../../configs/mh370-broad-powered-flight-pilot.toml");
        let mut suite: BroadSuiteConfig = toml::from_str(text).unwrap();
        suite.model.fuel_flow_initialization_design =
            BroadFuelFlowInitializationDesign::LogSpaceLatinHypercube;
        let error = validate_suite(&suite).unwrap_err().to_string();
        assert!(error.contains("cannot be combined with fuel-flow support strata"));
    }

    #[test]
    fn latin_hypercube_config_spelling_is_stable() {
        let text = include_str!("../../../configs/mh370-broad-powered-flight-pilot.toml");
        let text = text.replace(
            "proposal_candidates = 8",
            "proposal_candidates = 8\nfuel_flow_initialization_design = \"log_space_latin_hypercube\"",
        );
        let suite: BroadSuiteConfig = toml::from_str(&text).unwrap();
        assert_eq!(
            suite.model.fuel_flow_initialization_design,
            BroadFuelFlowInitializationDesign::LogSpaceLatinHypercube
        );
    }

    #[test]
    fn interval_tier_proposal_schedule_parses_and_preserves_exact_boundaries() {
        let text = include_str!("../../../configs/mh370-broad-powered-flight-pilot.toml");
        let text = text.replacen(
            "proposal_candidates = 8",
            "proposal_candidates = 1\n\
             [model.proposal_candidate_schedule]\n\
             kind = \"observation_interval_tiers\"\n\
             [[model.proposal_candidate_schedule.tiers]]\n\
             minimum_elapsed_seconds = 600.0\n\
             proposal_candidates = 2\n\
             [[model.proposal_candidate_schedule.tiers]]\n\
             minimum_elapsed_seconds = 1800.0\n\
             proposal_candidates = 4",
            1,
        );
        let suite: BroadSuiteConfig = toml::from_str(&text).unwrap();
        validate_suite(&suite).unwrap();
        let schedule = &suite.model.proposal_candidate_schedule;
        assert_eq!(schedule.candidates_for_elapsed_seconds(1, 151.0), 1);
        assert_eq!(schedule.candidates_for_elapsed_seconds(1, 600.0), 2);
        assert_eq!(schedule.candidates_for_elapsed_seconds(1, 1_800.0), 4);
        assert_eq!(
            serde_json::to_value(schedule).unwrap(),
            serde_json::json!({
                "kind": "observation_interval_tiers",
                "tiers": [
                    {
                        "minimum_elapsed_seconds": 600.0,
                        "proposal_candidates": 2
                    },
                    {
                        "minimum_elapsed_seconds": 1800.0,
                        "proposal_candidates": 4
                    }
                ]
            })
        );
    }

    #[test]
    fn island_config_expands_every_scientific_stratum_without_changing_its_prior() {
        let text = include_str!("../../../configs/mh370-broad-powered-flight-pilot.toml").replacen(
            "seeds = [370023]",
            "seeds = [370023]\n\n[islands]\nislands_per_stratum = 2\nparticles_per_island = 100",
            1,
        );
        let suite: BroadSuiteConfig = toml::from_str(&text).unwrap();
        validate_suite(&suite).unwrap();
        let (_, scientific, _) = expand_model_and_plan(&suite).unwrap();
        let islands = build_island_plan(&suite, &scientific).unwrap().unwrap();
        assert_eq!(islands.strata.len(), 100);
        assert!(islands.strata.iter().all(|entry| {
            entry.islands == 2
                && entry.particles_per_island == 100
                && entry.log_prior_probability
                    == scientific
                        .strata
                        .iter()
                        .find(|stratum| stratum.id == entry.id)
                        .unwrap()
                        .log_prior_probability
        }));
        assert_eq!(
            islands
                .strata
                .iter()
                .map(|entry| entry.islands * entry.particles_per_island)
                .sum::<usize>(),
            suite.filter.particles
        );
        assert_eq!(
            island_inference_descriptor(suite.islands.unwrap()),
            "inference=scientific-stratum-island-smc-v1;islands-per-scientific-stratum=2;particles-per-island=100;pooling=scientific-prior-times-equal-island-prior-times-conditional-evidence"
        );
    }

    #[test]
    fn island_config_rejects_a_population_mismatch() {
        let text = include_str!("../../../configs/mh370-broad-powered-flight-pilot.toml").replacen(
            "seeds = [370023]",
            "seeds = [370023]\n\n[islands]\nislands_per_stratum = 2\nparticles_per_island = 99",
            1,
        );
        let suite: BroadSuiteConfig = toml::from_str(&text).unwrap();
        let error = validate_suite(&suite).unwrap_err().to_string();
        assert!(error.contains("requires 19800 particles"));
    }

    #[test]
    fn island_config_rejects_repeated_latin_hypercube_cells() {
        let text = include_str!("../../../configs/mh370-broad-powered-flight-pilot.toml").replacen(
            "seeds = [370023]",
            "seeds = [370023]\n\n[islands]\nislands_per_stratum = 5\nparticles_per_island = 200",
            1,
        );
        let mut suite: BroadSuiteConfig = toml::from_str(&text).unwrap();
        suite.model.fuel_flow_initialization_design =
            BroadFuelFlowInitializationDesign::LogSpaceLatinHypercube;
        suite.model.fuel_flow_support_strata.clear();
        let error = validate_suite(&suite).unwrap_err().to_string();
        assert!(error.contains("requires independent_log_uniform"));
    }

    fn pending_renewal_refresh_config_text() -> String {
        include_str!("../../../configs/mh370-broad-powered-flight-pilot.toml")
            .replacen("proposal_candidates = 8", "proposal_candidates = 1", 1)
            .replacen(
                "seeds = [370023]",
                "seeds = [370023]\n\n[pending_renewal_refresh]\nafter_observation_ids = [\"m1839\"]\nlateral = true\nspeed = true\naltitude = true",
                1,
            )
    }

    fn synthetic_pending_renewal_refresh_state(
        stratum: StratumId,
        time_s: f64,
        refreshes_per_stream: u64,
        bto_observations: u32,
        bfo_observations: u32,
    ) -> BroadFlightState {
        let pending = Some(PendingRenewal {
            not_before: Seconds(time_s),
            next_event: Seconds(time_s + 900.0 + stratum.0 as f64),
        });
        BroadFlightState {
            stratum,
            powered_flight: PoweredFlightState {
                aircraft: AircraftState {
                    time: Seconds(time_s),
                    position: LatLon::new(-35.0, 93.0).unwrap(),
                    altitude: Feet(35_000.0),
                    track_true: Degrees(180.0),
                    ground_speed: Knots(470.0),
                    vertical_speed: FeetPerMinute(0.0),
                    bfo_bias: Hertz(0.0),
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
                    lateral: pending,
                    speed: pending,
                    altitude: pending,
                },
                event_counters: PoweredEventCounters::default(),
            },
            fuel: PoweredFuelState {
                time: Seconds(time_s),
                zero_fuel_weight: Kilograms(174_369.0),
                left_usable_feed: Kilograms(1_000.0),
                right_usable_feed: Kilograms(1_000.0),
                reserved_fuel: Kilograms(15.0),
                unusable_fuel: Kilograms(0.0),
                left_exhaustion_time: None,
                right_exhaustion_time: None,
                dual_engine_exhaustion_time: None,
            },
            fuel_flow_scale: 1.0,
            fuel_quantity_offset_kg: 0.0,
            bfo_bias: BfoBiasState {
                mean_hz: 0.0,
                variance_hz2: 16.0,
            },
            status: BroadFlightParticleStatus::Active,
            fuel_status: BroadFuelDiagnosticStatus::Valid,
            scores: BroadFlightScores {
                cumulative_bto_log_likelihood: 0.0,
                cumulative_bfo_log_likelihood: 0.0,
                bto_observations,
                bfo_observations,
            },
            last_fit: None,
            diagnostics: BroadFlightDiagnostics {
                pending_renewal_refresh: BroadPendingRenewalRefreshDiagnostics {
                    total_refreshes: 3 * refreshes_per_stream,
                    lateral_refreshes: refreshes_per_stream,
                    speed_refreshes: refreshes_per_stream,
                    altitude_refreshes: refreshes_per_stream,
                },
                ..BroadFlightDiagnostics::default()
            },
        }
    }

    struct SyntheticPendingRenewalRefreshFixture {
        suite: BroadSuiteConfig,
        observations: Vec<BroadFlightObservation>,
        model: BroadFlightConfig,
        plan: StratifiedFilterPlan,
        realized: Vec<BroadRealizedPendingRenewalRefreshEpoch>,
        result: FilterResult<BroadFlightState>,
        move_checkpoints: Vec<StratifiedPostResampleMoveCheckpoint>,
    }

    fn synthetic_pending_renewal_refresh_fixture() -> SyntheticPendingRenewalRefreshFixture {
        let mut suite: BroadSuiteConfig =
            toml::from_str(&pending_renewal_refresh_config_text()).unwrap();
        suite.filter.particles = 20;
        suite.model.fuel_flow_initialization_design =
            BroadFuelFlowInitializationDesign::LogSpaceLatinHypercube;
        suite.model.fuel_flow_support_strata.clear();
        validate_suite(&suite).unwrap();
        let observations = observations_for_family(
            &suite,
            &suite.families[1],
            include_str!("../../../inputs/accident/satcom-through-0011.csv"),
            include_str!("../../../inputs/accident/satellite-through-0011.csv"),
        )
        .unwrap();
        let (model, plan, _) = expand_model_and_plan(&suite).unwrap();
        let (steps, realized) = realized_pending_renewal_refresh_epochs(
            suite.pending_renewal_refresh.as_ref().unwrap(),
            &observations,
        )
        .unwrap();
        let refresh_index = realized
            .iter()
            .position(|epoch| epoch.step == StratifiedPostResampleMoveStep::Apply)
            .unwrap();
        let final_strata = plan
            .strata
            .iter()
            .map(|allocation| StratumDiagnostics {
                id: allocation.id,
                particle_count: allocation.particles,
                posterior_mass: 0.05,
                log_posterior_mass: Some(0.05_f64.ln()),
                conditional_ess: 1.0,
                maximum_normalized_weight: 1.0,
                maximum_normalized_log_weight: Some(0.0),
                distinct_root_ancestors: 1,
                root_effective_sample_size: 1.0,
            })
            .collect::<Vec<_>>();
        let mut cumulative = 0.0;
        let physical_checkpoints = observations
            .iter()
            .enumerate()
            .map(|(index, observation)| {
                let increment = (index + 1) as f64 * 0.01;
                cumulative += increment;
                FilterCheckpoint {
                    observation_index: index,
                    observation_time_s: observation.time().0,
                    guide_ess: None,
                    posterior_ess: 20.0,
                    ancestor_resampled: false,
                    posterior_resampled: index == refresh_index,
                    log_evidence_increment: increment,
                    cumulative_log_evidence: cumulative,
                    maximum_normalized_weight: 0.05,
                    distinct_root_ancestors: 20,
                    root_effective_sample_size: 20.0,
                    maximum_root_weight: 0.05,
                    roots_with_mass_at_least_1e_6: 20,
                    roots_with_mass_at_least_1e_3: 20,
                    strata: if index + 1 == observations.len() {
                        final_strata.clone()
                    } else {
                        Vec::new()
                    },
                }
            })
            .collect::<Vec<_>>();
        let mut expected_start = 0usize;
        let refreshed_strata = plan
            .strata
            .iter()
            .map(|allocation| {
                let start = expected_start;
                expected_start += allocation.particles;
                StratifiedPostResampleMoveStratumCheckpoint {
                    stratum: allocation.id,
                    output_slot_start: start,
                    output_slot_end_exclusive: expected_start,
                    output_move_invocations: allocation.particles,
                    distinct_parent_slots: allocation.particles,
                    distinct_prior_roots: allocation.particles,
                }
            })
            .collect::<Vec<_>>();
        let move_checkpoints = realized
            .iter()
            .map(|epoch| {
                let invoked = epoch.observation_index == refresh_index;
                StratifiedPostResampleMoveCheckpoint {
                    observation_index: epoch.observation_index,
                    observation_time_s: epoch.observation_time_s,
                    step: epoch.step,
                    posterior_resampling_occurred: invoked,
                    output_move_invocations: if invoked { 20 } else { 0 },
                    strata: if invoked {
                        refreshed_strata.clone()
                    } else {
                        Vec::new()
                    },
                }
            })
            .collect::<Vec<_>>();
        let bto_observations = observations
            .iter()
            .filter(|observation| {
                matches!(observation, BroadFlightObservation::Satcom(value) if value.use_bto)
            })
            .count() as u32;
        let bfo_observations = observations
            .iter()
            .filter(|observation| {
                matches!(observation, BroadFlightObservation::Satcom(value) if value.use_bfo)
            })
            .count() as u32;
        let final_time_s = observations.last().unwrap().time().0;
        let particles = plan
            .strata
            .iter()
            .flat_map(|allocation| {
                (0..allocation.particles).map(move |_| {
                    synthetic_pending_renewal_refresh_state(
                        allocation.id,
                        final_time_s,
                        1,
                        bto_observations,
                        bfo_observations,
                    )
                })
            })
            .collect::<Vec<_>>();
        let stratum_ids = particles
            .iter()
            .map(|state| state.stratum)
            .collect::<Vec<_>>();
        let root_ids = (0..particles.len()).collect::<Vec<_>>();
        let log_weights = vec![-(particles.len() as f64).ln(); particles.len()];
        let snapshot = FilterSnapshot {
            observation_index: Some(observations.len() - 1),
            observation_time_s: final_time_s,
            particles: particles.clone(),
            log_weights: log_weights.clone(),
            root_ids: root_ids.clone(),
            stratum_ids: stratum_ids.clone(),
        };
        let result = FilterResult {
            particles,
            log_weights,
            root_ids,
            snapshots: vec![snapshot],
            ancestry: Vec::new(),
            checkpoints: physical_checkpoints,
            log_evidence: cumulative,
            initial_log_evidence: 0.0,
            initial_strata: Vec::new(),
        };
        assert_eq!(steps.len(), observations.len());
        SyntheticPendingRenewalRefreshFixture {
            suite,
            observations,
            model,
            plan,
            realized,
            result,
            move_checkpoints,
        }
    }

    #[test]
    fn pending_renewal_refresh_maps_exact_m1839_after_full_composition_with_twenty_strata() {
        let fixture = synthetic_pending_renewal_refresh_fixture();
        assert_eq!(fixture.plan.strata.len(), 20);
        assert!(fixture
            .plan
            .strata
            .iter()
            .all(|allocation| allocation.particles == 1));
        let m1839 = &fixture.realized[4];
        assert_eq!(m1839.observation_id, "m1839");
        assert_eq!(m1839.observation_kind, "satcom");
        assert_eq!(m1839.step, StratifiedPostResampleMoveStep::Apply);
        assert!(fixture
            .realized
            .iter()
            .enumerate()
            .all(|(index, epoch)| index == 4
                || epoch.step == StratifiedPostResampleMoveStep::Inactive));
        let config = fixture.suite.pending_renewal_refresh.as_ref().unwrap();
        assert_eq!(
            serde_json::to_value(config).unwrap(),
            serde_json::json!({
                "after_observation_ids": ["m1839"],
                "lateral": true,
                "speed": true,
                "altitude": true
            })
        );
        assert!(pending_renewal_refresh_inference_descriptor(config)
            .contains("weight-logz-evidence-term=none"));
    }

    #[test]
    fn pending_renewal_refresh_rejects_bad_ids_final_endpoint_and_held_out_aliasing() {
        let fixture = synthetic_pending_renewal_refresh_fixture();
        let config = fixture.suite.pending_renewal_refresh.as_ref().unwrap();
        let mut duplicate_config = fixture.suite.clone();
        duplicate_config
            .pending_renewal_refresh
            .as_mut()
            .unwrap()
            .after_observation_ids
            .push("m1839".to_string());
        assert!(validate_suite(&duplicate_config)
            .unwrap_err()
            .to_string()
            .contains("must be unique"));

        let mut missing = config.clone();
        missing.after_observation_ids = vec!["not-present".to_string()];
        assert!(
            realized_pending_renewal_refresh_epochs(&missing, &fixture.observations)
                .unwrap_err()
                .to_string()
                .contains("were not realized")
        );

        let mut duplicate_observations = fixture.observations.clone();
        duplicate_observations.push(fixture.observations[4].clone());
        assert!(
            realized_pending_renewal_refresh_epochs(config, &duplicate_observations)
                .unwrap_err()
                .to_string()
                .contains("each occur exactly once")
        );

        let mut final_endpoint = config.clone();
        final_endpoint.after_observation_ids =
            vec![fixture.observations.last().unwrap().id().to_string()];
        assert!(
            realized_pending_renewal_refresh_epochs(&final_endpoint, &fixture.observations)
                .unwrap_err()
                .to_string()
                .contains("cannot target final observation")
        );

        let bto_only_observations = observations_for_family(
            &fixture.suite,
            &fixture.suite.families[0],
            include_str!("../../../inputs/accident/satcom-through-0011.csv"),
            include_str!("../../../inputs/accident/satellite-through-0011.csv"),
        )
        .unwrap();
        assert!(bto_only_observations
            .iter()
            .any(|observation| observation.id() == "held-out-m1839"));
        assert!(
            realized_pending_renewal_refresh_epochs(config, &bto_only_observations)
                .unwrap_err()
                .to_string()
                .contains("observation IDs were not realized: m1839")
        );
    }

    #[test]
    fn pending_renewal_refresh_rejects_partial_streams_and_other_inference_paths() {
        let make_suite =
            || toml::from_str::<BroadSuiteConfig>(&pending_renewal_refresh_config_text()).unwrap();
        for disable in 0..3 {
            let mut suite = make_suite();
            let config = suite.pending_renewal_refresh.as_mut().unwrap();
            match disable {
                0 => config.lateral = false,
                1 => config.speed = false,
                _ => config.altitude = false,
            }
            assert!(validate_suite(&suite)
                .unwrap_err()
                .to_string()
                .contains("requires lateral, speed, and altitude"));
        }
        let mut auxiliary = make_suite();
        auxiliary.filter.algorithm = Algorithm::Auxiliary;
        assert!(validate_suite(&auxiliary)
            .unwrap_err()
            .to_string()
            .contains("requires the bootstrap"));
        let mut local_pool = make_suite();
        local_pool.model.proposal_candidates = 2;
        assert!(validate_suite(&local_pool)
            .unwrap_err()
            .to_string()
            .contains("constant local proposal_candidates = 1"));

        let mut disabled_clock = make_suite();
        disabled_clock.model.maneuver_families[0]
            .process
            .lateral_clock = None;
        assert!(validate_suite(&disabled_clock)
            .unwrap_err()
            .to_string()
            .contains("selects the disabled lateral stream"));

        let mut nonunit_clock = make_suite();
        nonunit_clock.model.maneuver_families[0]
            .process
            .speed_clock
            .as_mut()
            .unwrap()
            .gamma_shape = 1.5;
        assert!(validate_suite(&nonunit_clock)
            .unwrap_err()
            .to_string()
            .contains("requires gamma_shape = 1 for the selected speed stream"));

        let mut incompatible = Vec::new();
        let mut islands = make_suite();
        islands.islands = Some(BroadIslandConfig {
            islands_per_stratum: 1,
            particles_per_island: 200,
        });
        incompatible.push(islands);
        let mut global = make_suite();
        global.global_transition_pool = Some(
            BroadGlobalTransitionPoolSchedule::ObservationIntervalTiers {
                tiers: vec![BroadGlobalTransitionPoolTier {
                    minimum_elapsed_seconds: 3_000.0,
                    candidates_per_particle: 4,
                }],
            },
        );
        incompatible.push(global);
        let mut root = make_suite();
        root.root_stratified_transition_pool = Some(BroadRootStratifiedTransitionPoolConfig {
            epochs: vec![BroadRootStratifiedTransitionPoolEpochConfig {
                observation_id: "m1941".to_string(),
                candidates_per_positive_root: 4,
            }],
        });
        incompatible.push(root);
        let mut bridge = make_suite();
        bridge.intermediate_satcom_bridge = Some(BroadIntermediateSatcomBridgeConfig::default());
        incompatible.push(bridge);
        let guide_suite: BroadSuiteConfig =
            toml::from_str(&fuel_selection_guide_config_text(0.02)).unwrap();
        let mut guide = make_suite();
        guide.fuel_exhaustion_selection_guide = guide_suite.fuel_exhaustion_selection_guide;
        incompatible.push(guide);
        let twist_suite: BroadSuiteConfig =
            toml::from_str(&persistent_twist_config_text(Some(0.02))).unwrap();
        let mut twist = make_suite();
        twist.fuel_exhaustion_persistent_twist = twist_suite.fuel_exhaustion_persistent_twist;
        incompatible.push(twist);
        let mark_suite: BroadSuiteConfig =
            toml::from_str(&satcom_event_mark_guide_config_text()).unwrap();
        let mut mark = make_suite();
        mark.satcom_event_mark_guide = mark_suite.satcom_event_mark_guide;
        incompatible.push(mark);
        for suite in incompatible {
            assert!(validate_suite(&suite)
                .unwrap_err()
                .to_string()
                .contains("refresh-only pilot"));
        }
    }

    #[test]
    fn pending_renewal_refresh_checkpoint_and_lineage_diagnostics_fail_closed() {
        let fixture = synthetic_pending_renewal_refresh_fixture();
        let config = fixture.suite.pending_renewal_refresh.as_ref().unwrap();
        validate_pending_renewal_refresh_diagnostics(
            config,
            &fixture.realized,
            &fixture.plan,
            &fixture.result,
            &fixture.move_checkpoints,
        )
        .unwrap();

        let mut outside_schedule = fixture.move_checkpoints.clone();
        outside_schedule[0].output_move_invocations = 1;
        assert!(validate_pending_renewal_refresh_diagnostics(
            config,
            &fixture.realized,
            &fixture.plan,
            &fixture.result,
            &outside_schedule,
        )
        .is_err());

        let mut wrong_stratum_count = fixture.move_checkpoints.clone();
        wrong_stratum_count[4].strata.pop();
        assert!(validate_pending_renewal_refresh_diagnostics(
            config,
            &fixture.realized,
            &fixture.plan,
            &fixture.result,
            &wrong_stratum_count,
        )
        .is_err());

        let mut wrong_output_range = fixture.move_checkpoints.clone();
        wrong_output_range[4].strata[0].output_slot_end_exclusive += 1;
        assert!(validate_pending_renewal_refresh_diagnostics(
            config,
            &fixture.realized,
            &fixture.plan,
            &fixture.result,
            &wrong_output_range,
        )
        .is_err());

        let mut leaked_evidence = fixture.result.clone();
        leaked_evidence.checkpoints[4].cumulative_log_evidence += 1.0;
        assert!(validate_pending_renewal_refresh_diagnostics(
            config,
            &fixture.realized,
            &fixture.plan,
            &leaked_evidence,
            &fixture.move_checkpoints,
        )
        .is_err());

        let mut broken_lineage = fixture.result.clone();
        broken_lineage.particles[0]
            .diagnostics
            .pending_renewal_refresh
            .speed_refreshes = 0;
        assert!(validate_pending_renewal_refresh_diagnostics(
            config,
            &fixture.realized,
            &fixture.plan,
            &broken_lineage,
            &fixture.move_checkpoints,
        )
        .is_err());
    }

    #[test]
    fn pending_renewal_refresh_sidecar_is_hashed_self_contained_and_has_no_evidence_term() {
        let fixture = synthetic_pending_renewal_refresh_fixture();
        let config = fixture.suite.pending_renewal_refresh.as_ref().unwrap();
        let base_state = fixture.result.particles[0];
        let base_signature = broad_filtering_outcome_signature(base_state).unwrap();
        let mut disposable_only = base_state;
        disposable_only
            .powered_flight
            .event_clocks
            .lateral
            .as_mut()
            .unwrap()
            .next_event
            .0 += 1.0;
        disposable_only.diagnostics.pending_renewal_refresh =
            BroadPendingRenewalRefreshDiagnostics {
                total_refreshes: 6,
                lateral_refreshes: 2,
                speed_refreshes: 2,
                altitude_refreshes: 2,
            };
        assert_eq!(
            broad_filtering_outcome_signature(disposable_only).unwrap(),
            base_signature
        );
        let mut different_clock_presence = base_state;
        different_clock_presence.powered_flight.event_clocks.lateral = None;
        assert_ne!(
            broad_filtering_outcome_signature(different_clock_presence).unwrap(),
            base_signature
        );
        let mut different_renewal_history = base_state;
        different_renewal_history
            .powered_flight
            .event_clocks
            .lateral
            .as_mut()
            .unwrap()
            .not_before
            .0 += 1.0;
        assert_ne!(
            broad_filtering_outcome_signature(different_renewal_history).unwrap(),
            base_signature
        );

        let mut collision_result = fixture.result.clone();
        collision_result.particles[1] = disposable_only;
        collision_result.root_ids[1] = collision_result.root_ids[0];
        let final_snapshot = collision_result.snapshots.last_mut().unwrap();
        final_snapshot.particles = collision_result.particles.clone();
        final_snapshot.root_ids = collision_result.root_ids.clone();
        final_snapshot.stratum_ids = collision_result
            .particles
            .iter()
            .map(|state| state.stratum)
            .collect();

        let summary = summarize_pending_renewal_refresh(&collision_result).unwrap();
        let state_diversity = summarize_posterior_state_diversity(&collision_result).unwrap();
        assert_eq!(summary.finite_log_weight_particles, 20);
        assert_eq!(summary.strictly_positive_normalized_weight_particles, 20);
        assert!((summary.posterior_weighted_mean_total_refreshes - 3.15).abs() < 1.0e-12);
        assert!((summary.posterior_weighted_mean_lateral_refreshes - 1.05).abs() < 1.0e-12);
        assert_eq!(
            summary.exact_state_clone_multiplicity.unique_exact_states,
            20
        );
        assert_eq!(
            summary
                .exact_state_clone_multiplicity
                .maximum_exact_state_multiplicity,
            1
        );
        assert_eq!(
            state_diversity
                .all_particles
                .unique_filtering_outcome_signatures,
            19
        );
        assert_eq!(
            state_diversity
                .all_particles
                .finite_log_weight_particles_in_duplicate_signature_groups,
            2
        );
        assert!(
            (state_diversity
                .all_particles
                .posterior_mass_in_duplicate_signature_groups
                - 0.1)
                .abs()
                < 1.0e-12
        );
        assert_eq!(
            state_diversity.all_particles.maximum_signature_multiplicity,
            2
        );
        assert!(
            (state_diversity
                .all_particles
                .maximum_signature_group_posterior_mass
                - 0.1)
                .abs()
                < 1.0e-12
        );
        assert!(
            (state_diversity
                .all_particles
                .signature_aggregated_effective_sample_size
                - 1.0 / 0.055)
                .abs()
                < 1.0e-10
        );
        assert_eq!(state_diversity.dominant_prior_root.prior_root_id, 0);
        assert!((state_diversity.dominant_prior_root.posterior_mass - 0.1).abs() < 1.0e-12);
        assert_eq!(
            state_diversity
                .dominant_prior_root
                .filtering_outcome_signatures
                .unique_filtering_outcome_signatures,
            1
        );
        assert!(
            (state_diversity
                .dominant_prior_root
                .filtering_outcome_signatures
                .signature_aggregated_effective_sample_size
                - 1.0)
                .abs()
                < 1.0e-12
        );
        let input_sha256 = BTreeMap::from([("fixture".to_string(), "a".repeat(64))]);
        let run_identity = "b".repeat(64);
        let config_sha256 = "c".repeat(64);
        let artifact = BroadPendingRenewalRefreshDiagnosticsArtifact {
            schema: "mh370-broad-pending-renewal-refresh-diagnostics-v2",
            schema_version: 2,
            model_family: mh370_estimator::BROAD_FLIGHT_MODEL_FAMILY,
            refresh_family: BROAD_PENDING_RENEWAL_REFRESH_FAMILY,
            move_rng_domain: STRATIFIED_POST_RESAMPLE_MOVE_RNG_DOMAIN,
            family: "bto-bfo-published-error",
            seed: 370023,
            run_identity_sha256: &run_identity,
            config_sha256: &config_sha256,
            input_sha256: &input_sha256,
            filter: &fixture.suite.filter,
            resampling_policy: fixture.suite.resampling_policy,
            plan: &fixture.plan,
            config,
            resolved_estimator_config: config.resolved(),
            refresh_descriptor: config.resolved().stable_descriptor(),
            inference_descriptor: pending_renewal_refresh_inference_descriptor(config),
            realized_epochs: &fixture.realized,
            schedule_semantics: "exact-ID schedule",
            move_semantics: "target-invariant auxiliary-clock Gibbs",
            weighting_and_evidence_semantics: "no weight logZ or evidence term",
            move_log_weight_logz_and_evidence_adjustment: 0.0,
            diagnostic_population_semantics: "survivor lineages",
            exact_state_clone_semantics: "complete serialized state bytes",
            posterior_state_diversity: &state_diversity,
            physical_filter_checkpoints: &collision_result.checkpoints,
            post_resample_move_checkpoints: &fixture.move_checkpoints,
            posterior_survivor_summary: &summary,
        };
        let bytes = serde_json::to_vec(&artifact).unwrap();
        assert_eq!(
            sha256_bytes(&bytes),
            sha256_bytes(&serde_json::to_vec(&artifact).unwrap())
        );
        let value: serde_json::Value = serde_json::from_slice(&bytes).unwrap();
        assert_eq!(value["schema_version"], 2);
        assert_eq!(value["move_log_weight_logz_and_evidence_adjustment"], 0.0);
        assert_eq!(
            value["physical_filter_checkpoints"]
                .as_array()
                .unwrap()
                .len(),
            fixture.observations.len()
        );
        assert_eq!(
            value["post_resample_move_checkpoints"][4]["output_move_invocations"],
            20
        );
        assert_eq!(
            value["post_resample_move_checkpoints"][4]["strata"]
                .as_array()
                .unwrap()
                .len(),
            20
        );

        let mut underflow_result = fixture.result.clone();
        let mut raw_log_weights = vec![0.0; underflow_result.particles.len()];
        *raw_log_weights.last_mut().unwrap() = -1_000.0;
        underflow_result.log_weights = normalize_log_weights(&raw_log_weights).unwrap().0;
        underflow_result.snapshots.last_mut().unwrap().log_weights =
            underflow_result.log_weights.clone();
        let underflow_summary = summarize_pending_renewal_refresh(&underflow_result).unwrap();
        let underflow_diversity = summarize_posterior_state_diversity(&underflow_result).unwrap();
        assert_eq!(underflow_summary.finite_log_weight_particles, 20);
        assert_eq!(
            underflow_summary.strictly_positive_normalized_weight_particles,
            19
        );
        assert_eq!(
            underflow_diversity
                .all_particles
                .finite_log_weight_particles,
            20
        );
        assert_eq!(
            underflow_diversity
                .all_particles
                .strictly_positive_normalized_weight_particles,
            19
        );

        let mut disabled_result = fixture.result.clone();
        for state in &mut disabled_result.particles {
            state.diagnostics.pending_renewal_refresh = Default::default();
        }
        for state in &mut disabled_result.snapshots.last_mut().unwrap().particles {
            state.diagnostics.pending_renewal_refresh = Default::default();
        }
        let disabled_diversity = summarize_posterior_state_diversity(&disabled_result).unwrap();
        let disabled_seed_summary = summarize(
            "matched-disabled-control",
            370023,
            &disabled_result,
            disabled_diversity,
            BroadSeedInferenceSummaries {
                island_smc: None,
                global_transition_pool_smc: None,
                root_stratified_transition_pool_smc: None,
                satcom_event_mark_guide: None,
                pending_renewal_refresh: None,
                intermediate_satcom_bridge_smc: None,
                fuel_exhaustion_selection_guide_smc: None,
                fuel_exhaustion_persistent_twist_smc: None,
            },
        );
        let disabled_value = serde_json::to_value(disabled_seed_summary).unwrap();
        assert_eq!(disabled_value["positive_weight_particles"], 20);
        assert_eq!(
            disabled_value["posterior_state_diversity"]["all_particles"]
                ["finite_log_weight_particles"],
            20
        );
        assert!(disabled_value.get("pending_renewal_refresh").is_none());
    }

    #[test]
    fn pending_renewal_refresh_handoff_is_schema_two_and_legacy_config_stays_absent() {
        let fixture = synthetic_pending_renewal_refresh_fixture();
        let input_sha256 = BTreeMap::from([("fixture".to_string(), "a".repeat(64))]);
        let handoff = filtering_handoff(
            BroadHandoffContext {
                suite: &fixture.suite,
                family: &fixture.suite.families[1],
                model: &fixture.model,
                plan: &fixture.plan,
                observations: &fixture.observations,
                input_sha256: &input_sha256,
                config_sha256: &"b".repeat(64),
                fuel_exhaustion_selection_guide_window: None,
            },
            370023,
            &fixture.result,
        )
        .unwrap();
        assert_eq!(
            handoff.schema_version,
            BROAD_POSTERIOR_HANDOFF_SCHEMA_VERSION
        );
        assert_eq!(handoff.schema_version, 2);
        assert_eq!(
            handoff.run.pending_renewal_refresh,
            Some(
                fixture
                    .suite
                    .pending_renewal_refresh
                    .as_ref()
                    .unwrap()
                    .resolved()
            )
        );
        assert!(handoff
            .run
            .dynamics_model_family
            .contains("target-invariant-auxiliary-clock-gibbs"));

        let legacy: BroadSuiteConfig = toml::from_str(include_str!(
            "../../../configs/mh370-broad-powered-flight-pilot.toml"
        ))
        .unwrap();
        validate_suite(&legacy).unwrap();
        assert!(legacy.pending_renewal_refresh.is_none());
    }

    fn transition_pool_config_text(minimum_elapsed_seconds: f64, candidates: usize) -> String {
        include_str!("../../../configs/mh370-broad-powered-flight-pilot.toml")
            .replacen("proposal_candidates = 8", "proposal_candidates = 1", 1)
            .replacen(
                "seeds = [370023]",
                &format!(
                    "seeds = [370023]\n\n[global_transition_pool]\nkind = \"observation_interval_tiers\"\n[[global_transition_pool.tiers]]\nminimum_elapsed_seconds = {minimum_elapsed_seconds}\ncandidates_per_particle = {candidates}"
                ),
                1,
            )
    }

    #[test]
    fn transition_pool_schedule_maps_final_typed_observations_and_exact_boundary() {
        let text = transition_pool_config_text(3_000.0, 4);
        let suite: BroadSuiteConfig = toml::from_str(&text).unwrap();
        validate_suite(&suite).unwrap();
        let schedule = suite.global_transition_pool.as_ref().unwrap();
        assert_eq!(
            schedule.step_for_elapsed_seconds(2_999.999),
            GlobalTransitionPoolStep::Standard
        );
        assert_eq!(
            schedule.step_for_elapsed_seconds(3_000.0),
            GlobalTransitionPoolStep::Pool {
                candidates_per_particle: 4
            }
        );
        let observations = observations_for_family(
            &suite,
            &suite.families[1],
            include_str!("../../../inputs/accident/satcom-through-0011.csv"),
            include_str!("../../../inputs/accident/satellite-through-0011.csv"),
        )
        .unwrap();
        let (steps, realized) = realized_global_transition_pool_epochs(
            schedule,
            &observations,
            suite.filter.initial_time_s,
        );
        assert_eq!(steps.len(), observations.len());
        assert_eq!(realized.len(), observations.len());
        let pooled = realized
            .iter()
            .filter(|epoch| matches!(epoch.step, GlobalTransitionPoolStep::Pool { .. }))
            .map(|epoch| epoch.observation_id.as_str())
            .collect::<Vec<_>>();
        assert_eq!(pooled, ["m1941", "m2041", "m2141", "m2241", "m0011"]);
        let m2315 = realized
            .iter()
            .find(|epoch| epoch.observation_id == "m2315")
            .unwrap();
        assert_eq!(m2315.elapsed_seconds, 2_021.0);
        assert_eq!(m2315.step, GlobalTransitionPoolStep::Standard);
        let m0011 = realized.last().unwrap();
        assert_eq!(m0011.observation_index, observations.len() - 1);
        assert_eq!(m0011.observation_time_s, 22_150.0);
        assert_eq!(m0011.elapsed_seconds, 3_357.0);
    }

    #[test]
    fn transition_pool_schedule_is_typed_and_stably_described() {
        let suite: BroadSuiteConfig =
            toml::from_str(&transition_pool_config_text(3_000.0, 4)).unwrap();
        let schedule = suite.global_transition_pool.as_ref().unwrap();
        assert_eq!(
            serde_json::to_value(schedule).unwrap(),
            serde_json::json!({
                "kind": "observation_interval_tiers",
                "tiers": [{
                    "minimum_elapsed_seconds": 3000.0,
                    "candidates_per_particle": 4
                }]
            })
        );
        assert_eq!(
            global_transition_pool_inference_descriptor(schedule),
            "inference=global-transition-pool-smc-v1;local-proposal-candidates=1;schedule=observation-interval-tiers[elapsed>=3000.000000000s:k4];weighting=proper-candidate-measure-plus-output-proposal-correction"
        );
    }

    #[test]
    fn transition_pool_rejects_islands_and_stacked_local_candidates() {
        let mut suite: BroadSuiteConfig =
            toml::from_str(&transition_pool_config_text(3_000.0, 4)).unwrap();
        suite.islands = Some(BroadIslandConfig {
            islands_per_stratum: 2,
            particles_per_island: 100,
        });
        assert!(validate_suite(&suite)
            .unwrap_err()
            .to_string()
            .contains("mutually exclusive"));

        suite.islands = None;
        suite.model.proposal_candidates = 2;
        assert!(validate_suite(&suite)
            .unwrap_err()
            .to_string()
            .contains("constant local proposal_candidates = 1"));
    }

    #[test]
    fn transition_pool_diagnostics_contract_is_provenance_bound() {
        let suite: BroadSuiteConfig =
            toml::from_str(&transition_pool_config_text(3_000.0, 4)).unwrap();
        let schedule = suite.global_transition_pool.as_ref().unwrap();
        let observations = observations_for_family(
            &suite,
            &suite.families[0],
            include_str!("../../../inputs/accident/satcom-through-0011.csv"),
            include_str!("../../../inputs/accident/satellite-through-0011.csv"),
        )
        .unwrap();
        let (_, realized) = realized_global_transition_pool_epochs(
            schedule,
            &observations,
            suite.filter.initial_time_s,
        );
        let input_sha256 = BTreeMap::from([("fixture".to_string(), "a".repeat(64))]);
        let value = serde_json::to_value(BroadGlobalTransitionPoolDiagnosticsArtifact {
            schema: "mh370-broad-global-transition-pool-diagnostics-v1",
            schema_version: 1,
            model_family: mh370_estimator::BROAD_FLIGHT_MODEL_FAMILY,
            family: "bto-only",
            seed: 370023,
            run_identity_sha256: &"b".repeat(64),
            config_sha256: &"c".repeat(64),
            input_sha256: &input_sha256,
            filter: &suite.filter,
            resampling_policy: suite.resampling_policy,
            schedule,
            realized_epochs: &realized,
            weighting_semantics: "proper_candidate_measure_with_exact_output_proposal_correction",
            checkpoints: &[],
        })
        .unwrap();
        assert_eq!(
            value["schema"],
            "mh370-broad-global-transition-pool-diagnostics-v1"
        );
        assert_eq!(value["run_identity_sha256"], "b".repeat(64));
        assert_eq!(value["input_sha256"]["fixture"], "a".repeat(64));
        assert_eq!(value["filter"]["seed"], 0);
        assert_eq!(value["realized_epochs"].as_array().unwrap().len(), 11);
        assert_eq!(value["checkpoints"], serde_json::json!([]));
    }

    fn satcom_event_mark_guide_config_text() -> String {
        include_str!("../../../configs/mh370-broad-powered-flight-pilot.toml")
            .replacen("proposal_candidates = 8", "proposal_candidates = 1", 1)
            .replacen(
                "seeds = [370023]",
                "seeds = [370023]\n\n[satcom_event_mark_guide]\n[[satcom_event_mark_guide.epochs]]\nobservation_id = \"m1941\"\nminimum_lead_s = 60.0\nmaximum_lookback_s = 900.0\ncandidates_per_event = 8\ndefensive_prior_probability = 0.2\nscore_temperature = 0.25",
                1,
            )
    }

    #[test]
    fn satcom_event_mark_guide_config_is_typed_and_root_pool_compatible() {
        let mut suite: BroadSuiteConfig =
            toml::from_str(&satcom_event_mark_guide_config_text()).unwrap();
        validate_suite(&suite).unwrap();
        let guide = suite.satcom_event_mark_guide.as_ref().unwrap();
        assert_eq!(
            serde_json::to_value(guide).unwrap(),
            serde_json::json!({
                "epochs": [{
                    "observation_id": "m1941",
                    "minimum_lead_s": 60.0,
                    "maximum_lookback_s": 900.0,
                    "candidates_per_event": 8,
                    "defensive_prior_probability": 0.2,
                    "score_temperature": 0.25
                }]
            })
        );
        let resolved = guide.resolved();
        assert_eq!(resolved.epochs[0].minimum_lead, Seconds(60.0));
        assert_eq!(resolved.epochs[0].maximum_lookback, Seconds(900.0));
        let descriptor = satcom_event_mark_guide_inference_descriptor(guide);
        assert!(descriptor.contains(BROAD_SATCOM_EVENT_MARK_GUIDE_FAMILY));
        assert!(descriptor.contains("inclusive-physical-endpoint-lead-window"));
        assert!(descriptor.contains("additional-scientific-evidence=none"));

        suite.root_stratified_transition_pool = Some(BroadRootStratifiedTransitionPoolConfig {
            epochs: vec![BroadRootStratifiedTransitionPoolEpochConfig {
                observation_id: "m1941".to_string(),
                candidates_per_positive_root: 4,
            }],
        });
        validate_suite(&suite).unwrap();
        assert_eq!(
            suite
                .root_stratified_transition_pool
                .as_ref()
                .unwrap()
                .epochs[0]
                .candidates_per_positive_root,
            4
        );
        assert_eq!(
            suite.satcom_event_mark_guide.as_ref().unwrap().epochs[0].candidates_per_event,
            8
        );
    }

    #[test]
    fn satcom_event_mark_guide_realizes_exact_inclusive_family_endpoint() {
        let suite: BroadSuiteConfig =
            toml::from_str(&satcom_event_mark_guide_config_text()).unwrap();
        let guide = suite.satcom_event_mark_guide.as_ref().unwrap();
        let bto_observations = observations_for_family(
            &suite,
            &suite.families[0],
            include_str!("../../../inputs/accident/satcom-through-0011.csv"),
            include_str!("../../../inputs/accident/satellite-through-0011.csv"),
        )
        .unwrap();
        let bto = realized_satcom_event_mark_guide_epochs(
            guide,
            &bto_observations,
            suite.filter.initial_time_s,
        )
        .unwrap();
        assert_eq!(bto.len(), 1);
        assert_eq!(bto[0].observation_id, "m1941");
        assert_eq!(bto[0].observation_index, 5);
        assert_eq!(bto[0].observation_kind, "satcom");
        assert_eq!(bto[0].transition_start_s, 2_286.0);
        assert_eq!(bto[0].observation_time_s, 5_953.0);
        assert_eq!(bto[0].eligible_event_time_minimum_s, 5_053.0);
        assert_eq!(bto[0].eligible_event_time_maximum_s, 5_893.0);
        assert!(bto[0].use_bto);
        assert!(!bto[0].use_bfo);

        let bto_bfo_observations = observations_for_family(
            &suite,
            &suite.families[1],
            include_str!("../../../inputs/accident/satcom-through-0011.csv"),
            include_str!("../../../inputs/accident/satellite-through-0011.csv"),
        )
        .unwrap();
        let bto_bfo = realized_satcom_event_mark_guide_epochs(
            guide,
            &bto_bfo_observations,
            suite.filter.initial_time_s,
        )
        .unwrap();
        assert!(bto_bfo[0].use_bto);
        assert!(bto_bfo[0].use_bfo);
    }

    #[test]
    fn satcom_event_mark_guide_rejects_unrealized_ambiguous_or_unusable_endpoints() {
        let suite: BroadSuiteConfig =
            toml::from_str(&satcom_event_mark_guide_config_text()).unwrap();
        let observations = observations_for_family(
            &suite,
            &suite.families[1],
            include_str!("../../../inputs/accident/satcom-through-0011.csv"),
            include_str!("../../../inputs/accident/satellite-through-0011.csv"),
        )
        .unwrap();
        let guide = suite.satcom_event_mark_guide.as_ref().unwrap();

        let mut missing = guide.clone();
        missing.epochs[0].observation_id = "not-present".to_string();
        assert!(realized_satcom_event_mark_guide_epochs(
            &missing,
            &observations,
            suite.filter.initial_time_s
        )
        .unwrap_err()
        .to_string()
        .contains("were not realized"));

        let mut duplicated_observations = observations.clone();
        duplicated_observations.push(
            observations
                .iter()
                .find(|observation| observation.id() == "m1941")
                .unwrap()
                .clone(),
        );
        assert!(realized_satcom_event_mark_guide_epochs(
            guide,
            &duplicated_observations,
            suite.filter.initial_time_s
        )
        .unwrap_err()
        .to_string()
        .contains("each occur exactly once"));

        let mut non_satcom = guide.clone();
        non_satcom.epochs[0].observation_id = suite.fuel_anchor.id.clone();
        assert!(realized_satcom_event_mark_guide_epochs(
            &non_satcom,
            &observations,
            suite.filter.initial_time_s
        )
        .unwrap_err()
        .to_string()
        .contains("non-SATCOM"));

        let mut empty_window = guide.clone();
        empty_window.epochs[0].minimum_lead_s = 4_000.0;
        empty_window.epochs[0].maximum_lookback_s = 5_000.0;
        assert!(realized_satcom_event_mark_guide_epochs(
            &empty_window,
            &observations,
            suite.filter.initial_time_s
        )
        .unwrap_err()
        .to_string()
        .contains("no eligible event time"));

        let bto_only_observations = observations_for_family(
            &suite,
            &suite.families[0],
            include_str!("../../../inputs/accident/satcom-through-0011.csv"),
            include_str!("../../../inputs/accident/satellite-through-0011.csv"),
        )
        .unwrap();
        assert!(bto_only_observations.iter().any(|observation| {
            observation.id() == "held-out-m1839"
                && matches!(observation, BroadFlightObservation::Checkpoint { .. })
        }));
        let mut held_out_bfo_only = guide.clone();
        held_out_bfo_only.epochs[0].observation_id = "m1839".to_string();
        let error = realized_satcom_event_mark_guide_epochs(
            &held_out_bfo_only,
            &bto_only_observations,
            suite.filter.initial_time_s,
        )
        .unwrap_err()
        .to_string();
        assert!(error.contains("observation IDs were not realized: m1839"));
    }

    #[test]
    fn satcom_event_mark_guide_rejects_stacked_or_nonbootstrap_designs() {
        let make_suite =
            || toml::from_str::<BroadSuiteConfig>(&satcom_event_mark_guide_config_text()).unwrap();
        let mut auxiliary = make_suite();
        auxiliary.filter.algorithm = Algorithm::Auxiliary;
        assert!(validate_suite(&auxiliary)
            .unwrap_err()
            .to_string()
            .contains("requires the bootstrap"));

        let mut local_k = make_suite();
        local_k.model.proposal_candidates = 2;
        assert!(validate_suite(&local_k)
            .unwrap_err()
            .to_string()
            .contains("constant local proposal_candidates = 1"));

        let mut islands = make_suite();
        islands.islands = Some(BroadIslandConfig {
            islands_per_stratum: 2,
            particles_per_island: 100,
        });
        assert!(validate_suite(&islands)
            .unwrap_err()
            .to_string()
            .contains("only with ordinary filtering or the root-stratified transition pool"));

        let mut invalid = make_suite();
        invalid.satcom_event_mark_guide.as_mut().unwrap().epochs[0].score_temperature = -0.1;
        assert!(validate_suite(&invalid)
            .unwrap_err()
            .to_string()
            .contains("invalid SATCOM event-mark guide"));
    }

    fn valid_satcom_event_mark_diagnostics(
        config: &BroadSatcomEventMarkGuideRunConfig,
    ) -> BroadSatcomEventMarkGuideDiagnostics {
        let epoch = &config.epochs[0];
        let log_candidate_count = (epoch.candidates_per_event as f64).ln();
        let selected_log_probability = 0.25_f64.ln();
        let maximum_probability =
            epoch.defensive_prior_probability / epoch.candidates_per_event as f64 + 1.0
                - epoch.defensive_prior_probability;
        BroadSatcomEventMarkGuideDiagnostics {
            eligible_lateral_events: 1,
            guided_lateral_events: 1,
            candidate_marks: 8,
            finite_candidate_scores: 8,
            materialization_failures: 0,
            proxy_projection_successes: 8,
            proxy_projection_failures: 0,
            proxy_projection_skipped_candidates: 0,
            all_scores_negative_infinity_events: 0,
            sum_selection_effective_sample_size: 4.0,
            sum_selection_entropy_nats: 1.0,
            minimum_selected_probability: Some(0.25),
            maximum_selected_probability: Some(0.25),
            minimum_event_log_prior_over_proposal: Some(
                -log_candidate_count - selected_log_probability,
            ),
            maximum_event_log_prior_over_proposal: Some(
                -log_candidate_count - selected_log_probability,
            ),
            minimum_lead_seconds: Some(60.0),
            maximum_lead_seconds: Some(60.0),
            sum_log_candidate_count: log_candidate_count,
            sum_selected_log_probability: selected_log_probability,
            cumulative_log_prior_over_proposal: -log_candidate_count - selected_log_probability,
            sum_minimum_log_prior_over_proposal: -log_candidate_count - maximum_probability.ln(),
            sum_maximum_log_prior_over_proposal: -epoch.defensive_prior_probability.ln(),
        }
    }

    #[test]
    fn satcom_event_mark_guide_diagnostics_recompose_against_config() {
        let suite: BroadSuiteConfig =
            toml::from_str(&satcom_event_mark_guide_config_text()).unwrap();
        let config = suite.satcom_event_mark_guide.as_ref().unwrap();
        let diagnostics = valid_satcom_event_mark_diagnostics(config);
        assert!(valid_satcom_event_mark_guide_diagnostics(
            Some(config),
            diagnostics
        ));

        let mut wrong_log_k = diagnostics;
        wrong_log_k.sum_log_candidate_count += 0.1;
        wrong_log_k.cumulative_log_prior_over_proposal -= 0.1;
        assert!(!valid_satcom_event_mark_guide_diagnostics(
            Some(config),
            wrong_log_k
        ));

        let mut wrong_lower_bound = diagnostics;
        wrong_lower_bound.sum_minimum_log_prior_over_proposal += 0.1;
        assert!(!valid_satcom_event_mark_guide_diagnostics(
            Some(config),
            wrong_lower_bound
        ));

        let mut wrong_upper_bound = diagnostics;
        wrong_upper_bound.sum_maximum_log_prior_over_proposal -= 0.1;
        assert!(!valid_satcom_event_mark_guide_diagnostics(
            Some(config),
            wrong_upper_bound
        ));

        let mut wrong_event_extrema = diagnostics;
        wrong_event_extrema.minimum_event_log_prior_over_proposal = Some(-1.0);
        wrong_event_extrema.maximum_event_log_prior_over_proposal = Some(1.0);
        assert!(!valid_satcom_event_mark_guide_diagnostics(
            Some(config),
            wrong_event_extrema
        ));

        let mut event_extrema_outside_config = diagnostics;
        event_extrema_outside_config.maximum_event_log_prior_over_proposal = Some(2.0);
        assert!(!valid_satcom_event_mark_guide_diagnostics(
            Some(config),
            event_extrema_outside_config
        ));

        assert!(!valid_satcom_event_mark_guide_diagnostics(
            None,
            diagnostics
        ));
        assert!(valid_satcom_event_mark_guide_diagnostics(
            None,
            BroadSatcomEventMarkGuideDiagnostics::default()
        ));
    }

    #[test]
    fn neutral_satcom_event_mark_guide_diagnostics_close_skipped_proxy_counts() {
        let suite: BroadSuiteConfig =
            toml::from_str(&satcom_event_mark_guide_config_text()).unwrap();
        let mut config = suite.satcom_event_mark_guide.unwrap();
        config.epochs[0].score_temperature = 0.0;
        let epoch = &config.epochs[0];
        let log_candidate_count = (epoch.candidates_per_event as f64).ln();
        let maximum_probability =
            epoch.defensive_prior_probability / epoch.candidates_per_event as f64 + 1.0
                - epoch.defensive_prior_probability;
        let diagnostics = BroadSatcomEventMarkGuideDiagnostics {
            eligible_lateral_events: 1,
            guided_lateral_events: 1,
            candidate_marks: 8,
            finite_candidate_scores: 8,
            materialization_failures: 0,
            proxy_projection_successes: 0,
            proxy_projection_failures: 0,
            proxy_projection_skipped_candidates: 8,
            all_scores_negative_infinity_events: 0,
            sum_selection_effective_sample_size: 8.0,
            sum_selection_entropy_nats: log_candidate_count,
            minimum_selected_probability: Some(0.125),
            maximum_selected_probability: Some(0.125),
            minimum_event_log_prior_over_proposal: Some(0.0),
            maximum_event_log_prior_over_proposal: Some(0.0),
            minimum_lead_seconds: Some(900.0),
            maximum_lead_seconds: Some(900.0),
            sum_log_candidate_count: log_candidate_count,
            sum_selected_log_probability: -log_candidate_count,
            cumulative_log_prior_over_proposal: 0.0,
            sum_minimum_log_prior_over_proposal: -log_candidate_count - maximum_probability.ln(),
            sum_maximum_log_prior_over_proposal: -epoch.defensive_prior_probability.ln(),
        };
        assert!(valid_satcom_event_mark_guide_diagnostics(
            Some(&config),
            diagnostics
        ));
        let mut falsely_projected = diagnostics;
        falsely_projected.proxy_projection_skipped_candidates = 0;
        falsely_projected.proxy_projection_successes = 8;
        assert!(!valid_satcom_event_mark_guide_diagnostics(
            Some(&config),
            falsely_projected
        ));

        let mut all_marks_invalid = diagnostics;
        all_marks_invalid.finite_candidate_scores = 0;
        all_marks_invalid.materialization_failures = 8;
        all_marks_invalid.proxy_projection_skipped_candidates = 0;
        all_marks_invalid.all_scores_negative_infinity_events = 1;
        assert!(valid_satcom_event_mark_guide_diagnostics(
            Some(&config),
            all_marks_invalid
        ));

        let mut impossible_fallback = diagnostics;
        impossible_fallback.all_scores_negative_infinity_events = 1;
        assert!(!valid_satcom_event_mark_guide_diagnostics(
            Some(&config),
            impossible_fallback
        ));
    }

    #[test]
    fn epsilon_one_satcom_event_mark_guide_serializes_exact_uniform_neutrality() {
        let suite: BroadSuiteConfig =
            toml::from_str(&satcom_event_mark_guide_config_text()).unwrap();
        let mut config = suite.satcom_event_mark_guide.unwrap();
        config.epochs[0].defensive_prior_probability = 1.0;
        assert!(config.epochs[0].score_temperature > 0.0);
        let epoch = &config.epochs[0];
        let log_candidate_count = (epoch.candidates_per_event as f64).ln();
        let uniform_probability = 1.0 / epoch.candidates_per_event as f64;
        let configured_lower_bound = -log_candidate_count - uniform_probability.ln();
        let configured_upper_bound = -epoch.defensive_prior_probability.ln();
        assert_eq!(configured_lower_bound, 0.0);
        assert_eq!(configured_upper_bound, 0.0);
        let diagnostics = BroadSatcomEventMarkGuideDiagnostics {
            eligible_lateral_events: 1,
            guided_lateral_events: 1,
            candidate_marks: 8,
            finite_candidate_scores: 8,
            materialization_failures: 0,
            proxy_projection_successes: 0,
            proxy_projection_failures: 0,
            proxy_projection_skipped_candidates: 8,
            all_scores_negative_infinity_events: 0,
            sum_selection_effective_sample_size: 8.0,
            sum_selection_entropy_nats: log_candidate_count,
            minimum_selected_probability: Some(uniform_probability),
            maximum_selected_probability: Some(uniform_probability),
            minimum_event_log_prior_over_proposal: Some(0.0),
            maximum_event_log_prior_over_proposal: Some(0.0),
            minimum_lead_seconds: Some(60.0),
            maximum_lead_seconds: Some(60.0),
            sum_log_candidate_count: log_candidate_count,
            sum_selected_log_probability: -log_candidate_count,
            cumulative_log_prior_over_proposal: 0.0,
            sum_minimum_log_prior_over_proposal: configured_lower_bound,
            sum_maximum_log_prior_over_proposal: configured_upper_bound,
        };
        assert!(valid_satcom_event_mark_guide_diagnostics(
            Some(&config),
            diagnostics
        ));
        let serialized = serde_json::to_value(diagnostics).unwrap();
        assert_eq!(serialized["proxy_projection_skipped_candidates"], 8);
        assert_eq!(
            serialized["minimum_selected_probability"],
            uniform_probability
        );
        assert_eq!(serialized["minimum_event_log_prior_over_proposal"], 0.0);
        assert_eq!(serialized["cumulative_log_prior_over_proposal"], 0.0);
        assert_eq!(serialized["sum_minimum_log_prior_over_proposal"], 0.0);
        assert_eq!(serialized["sum_maximum_log_prior_over_proposal"], 0.0);
        let mut falsely_projected = diagnostics;
        falsely_projected.proxy_projection_skipped_candidates = 0;
        falsely_projected.proxy_projection_successes = 8;
        assert!(!valid_satcom_event_mark_guide_diagnostics(
            Some(&config),
            falsely_projected
        ));
    }

    #[test]
    fn satcom_event_mark_guide_sidecar_binds_physical_checkpoints() {
        let suite: BroadSuiteConfig =
            toml::from_str(&satcom_event_mark_guide_config_text()).unwrap();
        let config = suite.satcom_event_mark_guide.as_ref().unwrap();
        let observations = observations_for_family(
            &suite,
            &suite.families[0],
            include_str!("../../../inputs/accident/satcom-through-0011.csv"),
            include_str!("../../../inputs/accident/satellite-through-0011.csv"),
        )
        .unwrap();
        let realized = realized_satcom_event_mark_guide_epochs(
            config,
            &observations,
            suite.filter.initial_time_s,
        )
        .unwrap();
        let input_sha256 = BTreeMap::from([("fixture".to_string(), "a".repeat(64))]);
        let summary = BroadSatcomEventMarkGuideSeedSummary::default();
        let value = serde_json::to_value(BroadSatcomEventMarkGuideDiagnosticsArtifact {
            schema: "mh370-broad-satcom-event-mark-guide-diagnostics-v1",
            schema_version: 1,
            model_family: mh370_estimator::BROAD_FLIGHT_MODEL_FAMILY,
            guide_family: BROAD_SATCOM_EVENT_MARK_GUIDE_FAMILY,
            family: "bto-only",
            seed: 370023,
            run_identity_sha256: &"b".repeat(64),
            config_sha256: &"c".repeat(64),
            input_sha256: &input_sha256,
            filter: &suite.filter,
            resampling_policy: suite.resampling_policy,
            config,
            resolved_estimator_config: config.resolved(),
            guide_descriptor: satcom_event_mark_guide_inference_descriptor(config),
            realized_epochs: &realized,
            eligibility_semantics: "inclusive",
            proposal_semantics: "proposal",
            proxy_semantics: "proxy",
            correction_semantics: "applied_once",
            evidence_semantics: "no_additional_evidence",
            root_pool_composition_semantics: "root_l_is_physical_only",
            diagnostic_population_semantics: "posterior_survivors",
            physical_filter_checkpoints: &[],
            posterior_survivor_summary: &summary,
        })
        .unwrap();
        assert_eq!(
            value["schema"],
            "mh370-broad-satcom-event-mark-guide-diagnostics-v1"
        );
        assert_eq!(value["guide_family"], BROAD_SATCOM_EVENT_MARK_GUIDE_FAMILY);
        assert_eq!(value["realized_epochs"][0]["use_bfo"], false);
        assert_eq!(value["physical_filter_checkpoints"], serde_json::json!([]));
        assert_eq!(
            value["root_pool_composition_semantics"],
            "root_l_is_physical_only"
        );
    }

    fn root_stratified_transition_pool_config_text(
        observation_id: &str,
        candidates_per_positive_root: usize,
    ) -> String {
        include_str!("../../../configs/mh370-broad-powered-flight-pilot.toml")
            .replacen("proposal_candidates = 8", "proposal_candidates = 1", 1)
            .replacen(
                "seeds = [370023]",
                &format!(
                    "seeds = [370023]\n\n[root_stratified_transition_pool]\n[[root_stratified_transition_pool.epochs]]\nobservation_id = \"{observation_id}\"\ncandidates_per_positive_root = {candidates_per_positive_root}"
                ),
                1,
            )
    }

    #[test]
    fn root_stratified_transition_pool_maps_exact_post_composition_observations() {
        let suite: BroadSuiteConfig =
            toml::from_str(&root_stratified_transition_pool_config_text("m1941", 4)).unwrap();
        validate_suite(&suite).unwrap();
        let config = suite.root_stratified_transition_pool.as_ref().unwrap();
        assert_eq!(
            serde_json::to_value(config).unwrap(),
            serde_json::json!({
                "epochs": [{
                    "observation_id": "m1941",
                    "candidates_per_positive_root": 4
                }]
            })
        );
        assert_eq!(
            root_stratified_transition_pool_inference_descriptor(config),
            "inference=root-stratified-transition-pool-smc-v1;local-proposal-candidates=1;schedule=observation-ids[m1941:l4-per-positive-root];allocation=fixed-l-per-finite-mass-root-within-scientific-stratum;weighting=proper-physical-candidate-measure-plus-exact-root-defensive-output-proposal-correction;additional-scientific-evidence=none"
        );

        let observations = observations_for_family(
            &suite,
            &suite.families[1],
            include_str!("../../../inputs/accident/satcom-through-0011.csv"),
            include_str!("../../../inputs/accident/satellite-through-0011.csv"),
        )
        .unwrap();
        let mut two_epoch_config = config.clone();
        two_epoch_config
            .epochs
            .push(BroadRootStratifiedTransitionPoolEpochConfig {
                observation_id: "m0011".to_string(),
                candidates_per_positive_root: 8,
            });
        two_epoch_config.validate().unwrap();
        assert_eq!(
            two_epoch_config.stable_descriptor(),
            "observation-ids[m1941:l4-per-positive-root,m0011:l8-per-positive-root]"
        );
        let (steps, realized) =
            realized_root_stratified_transition_pool_epochs(&two_epoch_config, &observations)
                .unwrap();
        assert_eq!(steps.len(), observations.len());
        assert_eq!(realized.len(), observations.len());
        let pooled = realized
            .iter()
            .filter(|epoch| matches!(epoch.step, RootStratifiedTransitionPoolStep::Pool { .. }))
            .collect::<Vec<_>>();
        assert_eq!(pooled.len(), 2);
        assert_eq!(pooled[0].observation_id, "m1941");
        assert_eq!(pooled[0].observation_index, 5);
        assert_eq!(pooled[0].observation_kind, "satcom");
        assert_eq!(pooled[0].observation_time_s, 5_953.0);
        assert_eq!(
            pooled[0].step,
            RootStratifiedTransitionPoolStep::Pool {
                candidates_per_positive_root: 4
            }
        );
        assert_eq!(pooled[1].observation_id, "m0011");
        assert_eq!(pooled[1].observation_index, 10);
        assert_eq!(pooled[1].observation_time_s, 22_150.0);
        assert_eq!(
            pooled[1].step,
            RootStratifiedTransitionPoolStep::Pool {
                candidates_per_positive_root: 8
            }
        );
        let fuel_anchor = realized
            .iter()
            .find(|epoch| epoch.observation_kind == "fuel_anchor")
            .unwrap();
        assert_eq!(fuel_anchor.observation_index, 2);
        assert_eq!(fuel_anchor.step, RootStratifiedTransitionPoolStep::Standard);
    }

    #[test]
    fn root_stratified_transition_pool_rejects_ambiguous_or_missing_ids() {
        let mut empty = BroadRootStratifiedTransitionPoolConfig { epochs: Vec::new() };
        assert!(empty
            .validate()
            .unwrap_err()
            .to_string()
            .contains("epochs must be non-empty"));
        empty
            .epochs
            .push(BroadRootStratifiedTransitionPoolEpochConfig {
                observation_id: "m1941".to_string(),
                candidates_per_positive_root: 0,
            });
        assert!(empty
            .validate()
            .unwrap_err()
            .to_string()
            .contains("positive candidate counts"));

        let mut duplicate_config: BroadSuiteConfig = toml::from_str(
            &root_stratified_transition_pool_config_text("m1941", 4).replacen(
                "[[root_stratified_transition_pool.epochs]]",
                "[[root_stratified_transition_pool.epochs]]\nobservation_id = \"m1941\"\ncandidates_per_positive_root = 8\n\n[[root_stratified_transition_pool.epochs]]",
                1,
            ),
        )
        .unwrap();
        assert!(validate_suite(&duplicate_config)
            .unwrap_err()
            .to_string()
            .contains("observation IDs must be unique"));

        duplicate_config
            .root_stratified_transition_pool
            .as_mut()
            .unwrap()
            .epochs[0]
            .observation_id = " ".to_string();
        assert!(duplicate_config
            .root_stratified_transition_pool
            .as_ref()
            .unwrap()
            .validate()
            .unwrap_err()
            .to_string()
            .contains("non-empty"));

        let suite: BroadSuiteConfig =
            toml::from_str(&root_stratified_transition_pool_config_text("m1941", 4)).unwrap();
        let config = suite.root_stratified_transition_pool.as_ref().unwrap();
        let mut observations = observations_for_family(
            &suite,
            &suite.families[1],
            include_str!("../../../inputs/accident/satcom-through-0011.csv"),
            include_str!("../../../inputs/accident/satellite-through-0011.csv"),
        )
        .unwrap();
        let duplicate = observations
            .iter()
            .find(|observation| observation.id() == "m1941")
            .unwrap()
            .clone();
        observations.push(duplicate);
        assert!(
            realized_root_stratified_transition_pool_epochs(config, &observations)
                .unwrap_err()
                .to_string()
                .contains("each occur exactly once")
        );

        let missing_config = BroadRootStratifiedTransitionPoolConfig {
            epochs: vec![BroadRootStratifiedTransitionPoolEpochConfig {
                observation_id: "not-present".to_string(),
                candidates_per_positive_root: 4,
            }],
        };
        assert!(
            realized_root_stratified_transition_pool_epochs(&missing_config, &observations)
                .unwrap_err()
                .to_string()
                .contains("were not realized: not-present")
        );
    }

    #[test]
    fn root_stratified_transition_pool_rejects_incompatible_inference_designs() {
        let make_suite = || {
            toml::from_str::<BroadSuiteConfig>(&root_stratified_transition_pool_config_text(
                "m1941", 4,
            ))
            .unwrap()
        };

        let mut auxiliary = make_suite();
        auxiliary.filter.algorithm = Algorithm::Auxiliary;
        assert!(validate_suite(&auxiliary)
            .unwrap_err()
            .to_string()
            .contains("requires the bootstrap"));

        let mut stacked_local = make_suite();
        stacked_local.model.proposal_candidates = 2;
        assert!(validate_suite(&stacked_local)
            .unwrap_err()
            .to_string()
            .contains("constant local proposal_candidates = 1"));

        let mut nonconstant_local = make_suite();
        nonconstant_local.model.proposal_candidate_schedule =
            BroadProposalCandidateSchedule::ObservationIntervalTiers {
                tiers: vec![mh370_estimator::BroadProposalCandidateTier {
                    minimum_elapsed_seconds: 3_000.0,
                    proposal_candidates: 2,
                }],
            };
        assert!(validate_suite(&nonconstant_local)
            .unwrap_err()
            .to_string()
            .contains("constant local proposal_candidates = 1"));

        let mut islands = make_suite();
        islands.islands = Some(BroadIslandConfig {
            islands_per_stratum: 2,
            particles_per_island: 100,
        });
        assert!(validate_suite(&islands)
            .unwrap_err()
            .to_string()
            .contains("mutually exclusive"));

        let mut legacy_pool = make_suite();
        legacy_pool.global_transition_pool = Some(
            BroadGlobalTransitionPoolSchedule::ObservationIntervalTiers {
                tiers: vec![BroadGlobalTransitionPoolTier {
                    minimum_elapsed_seconds: 3_000.0,
                    candidates_per_particle: 4,
                }],
            },
        );
        assert!(validate_suite(&legacy_pool)
            .unwrap_err()
            .to_string()
            .contains("mutually exclusive"));

        let mut bridge = make_suite();
        bridge.intermediate_satcom_bridge = Some(BroadIntermediateSatcomBridgeConfig::default());
        assert!(validate_suite(&bridge)
            .unwrap_err()
            .to_string()
            .contains("mutually exclusive"));

        let guide_suite: BroadSuiteConfig =
            toml::from_str(&fuel_selection_guide_config_text(0.02)).unwrap();
        let mut guide = make_suite();
        guide.fuel_exhaustion_selection_guide = guide_suite.fuel_exhaustion_selection_guide;
        assert!(validate_suite(&guide)
            .unwrap_err()
            .to_string()
            .contains("cannot be combined with a fuel guide"));

        let twist_suite: BroadSuiteConfig =
            toml::from_str(&persistent_twist_config_text(Some(0.02))).unwrap();
        let mut twist = make_suite();
        twist.fuel_exhaustion_persistent_twist = twist_suite.fuel_exhaustion_persistent_twist;
        assert!(validate_suite(&twist)
            .unwrap_err()
            .to_string()
            .contains("cannot be combined with a fuel guide or persistent twist"));
    }

    fn synthetic_root_stratified_transition_pool_result() -> (
        Vec<BroadRealizedRootStratifiedTransitionPoolEpoch>,
        RootStratifiedTransitionPoolFilterResult<()>,
    ) {
        let realized_increment = -1.9;
        let id = StratumId(7);
        let transition_pool_checkpoint = GlobalTransitionPoolCheckpoint {
            observation_index: 0,
            observation_time_s: 5_953.0,
            candidates_per_particle: 0,
            configured_candidates: 8,
            generated_candidates: 8,
            positive_candidates: 6,
            candidate_log_evidence_increment: -2.0,
            output_resampling_log_correction: 0.1,
            realized_log_evidence_increment: realized_increment,
            candidate_effective_sample_size: 4.5,
            maximum_candidate_weight: 0.3,
            distinct_positive_candidate_roots: 2,
            candidate_root_effective_sample_size: 1.8,
            maximum_candidate_root_weight: 0.7,
            strata: vec![GlobalTransitionPoolStratumDiagnostics {
                id,
                input_particles: 4,
                configured_candidates: 8,
                generated_candidates: 8,
                input_positive_roots: 2,
                sampled_ancestor_roots: 2,
                positive_candidates: 6,
                estimated_log_predictive_mass: Some(-2.0),
                candidate_posterior_mass: 1.0,
                candidate_log_posterior_mass: Some(0.0),
                conditional_candidate_effective_sample_size: 4.5,
                conditional_maximum_candidate_weight: 0.3,
                distinct_positive_candidate_roots: 2,
                conditional_candidate_root_effective_sample_size: 1.8,
                conditional_maximum_candidate_root_weight: 0.7,
                output_posterior_mass: 1.0,
                output_log_posterior_mass: Some(0.0),
                ancestor_selection_guide: None,
                output_selection_guide: None,
            }],
        };
        let root_checkpoint = RootStratifiedCandidatePoolCheckpoint {
            observation_index: 0,
            observation_time_s: 5_953.0,
            location: RootStratifiedCandidatePoolLocation::ObservationEndpoint,
            candidates_per_positive_root: 4,
            configured_candidates: 8,
            generated_candidates: 8,
            first_split_candidate_log_evidence_increment: Some(-2.1),
            second_split_candidate_log_evidence_increment: Some(-1.9),
            absolute_split_log_evidence_difference: Some(0.2),
            split_candidate_root_total_variation: Some(0.1),
            strata: vec![RootStratifiedCandidatePoolStratumDiagnostics {
                id,
                input_positive_roots: 2,
                candidates_per_positive_root: 4,
                generated_candidates: 8,
                roots_with_positive_candidates: 2,
                minimum_positive_candidates_per_root: 2,
                maximum_positive_candidates_per_root: 4,
                minimum_within_root_candidate_effective_sample_size: 1.5,
                median_within_root_candidate_effective_sample_size: 3.0,
                maximum_within_root_candidate_weight: 0.7,
                roots_with_maximum_candidate_weight_at_least_half: 1,
                first_split_log_predictive_mass: Some(-2.2),
                second_split_log_predictive_mass: Some(-2.0),
                absolute_split_log_predictive_mass_difference: Some(0.2),
                split_root_total_variation: Some(0.15),
            }],
        };
        let result = RootStratifiedTransitionPoolFilterResult {
            pooled: FilterResult {
                particles: vec![()],
                log_weights: vec![0.0],
                root_ids: vec![11],
                snapshots: Vec::new(),
                ancestry: Vec::new(),
                checkpoints: vec![synthetic_filter_checkpoint(
                    0,
                    5_953.0,
                    realized_increment,
                    realized_increment,
                )],
                log_evidence: realized_increment,
                initial_log_evidence: 0.0,
                initial_strata: Vec::new(),
            },
            transition_pool_checkpoints: vec![transition_pool_checkpoint],
            root_stratified_candidate_pool_checkpoints: vec![root_checkpoint],
        };
        (
            vec![BroadRealizedRootStratifiedTransitionPoolEpoch {
                observation_index: 0,
                observation_id: "m1941".to_string(),
                observation_kind: "satcom",
                observation_time_s: 5_953.0,
                step: RootStratifiedTransitionPoolStep::Pool {
                    candidates_per_positive_root: 4,
                },
            }],
            result,
        )
    }

    #[test]
    fn root_stratified_transition_pool_diagnostics_enforce_allocation_and_evidence() {
        let (realized, result) = synthetic_root_stratified_transition_pool_result();
        validate_root_stratified_transition_pool_diagnostics(&realized, &result).unwrap();
        let summary = summarize_root_stratified_transition_pool(&result);
        assert_eq!(summary.pooled_epochs, 1);
        assert_eq!(summary.total_input_positive_root_epoch_instances, 2);
        assert_eq!(summary.total_configured_candidates, 8);
        assert_eq!(summary.total_generated_candidates, 8);
        assert_eq!(summary.total_positive_candidates, 6);
        assert_eq!(summary.minimum_positive_candidates_per_root, 2);
        assert_eq!(summary.maximum_positive_candidates_per_root, 4);

        let mut wrong_allocation = result.clone();
        wrong_allocation.root_stratified_candidate_pool_checkpoints[0].strata[0]
            .generated_candidates = 7;
        assert!(
            validate_root_stratified_transition_pool_diagnostics(&realized, &wrong_allocation)
                .unwrap_err()
                .to_string()
                .contains("fixed per-root allocation")
        );

        let mut leaked_evidence = result.clone();
        leaked_evidence.transition_pool_checkpoints[0].output_resampling_log_correction = 0.2;
        assert!(
            validate_root_stratified_transition_pool_diagnostics(&realized, &leaked_evidence)
                .unwrap_err()
                .to_string()
                .contains("realized physical observation")
        );

        let mut invalid_split = result.clone();
        invalid_split.root_stratified_candidate_pool_checkpoints[0]
            .absolute_split_log_evidence_difference = Some(0.3);
        assert!(
            validate_root_stratified_transition_pool_diagnostics(&realized, &invalid_split)
                .unwrap_err()
                .to_string()
                .contains("realized physical observation")
        );
    }

    #[test]
    fn root_stratified_transition_pool_sidecar_disambiguates_the_generic_sentinel() {
        let suite: BroadSuiteConfig =
            toml::from_str(&root_stratified_transition_pool_config_text("m1941", 4)).unwrap();
        let config = suite.root_stratified_transition_pool.as_ref().unwrap();
        let (realized, result) = synthetic_root_stratified_transition_pool_result();
        let input_sha256 = BTreeMap::from([("fixture".to_string(), "a".repeat(64))]);
        let value = serde_json::to_value(BroadRootStratifiedTransitionPoolDiagnosticsArtifact {
            schema: "mh370-broad-root-stratified-transition-pool-diagnostics-v1",
            schema_version: 1,
            model_family: mh370_estimator::BROAD_FLIGHT_MODEL_FAMILY,
            family: "bto-bfo-published-error",
            seed: 370023,
            run_identity_sha256: &"b".repeat(64),
            config_sha256: &"c".repeat(64),
            input_sha256: &input_sha256,
            filter: &suite.filter,
            resampling_policy: suite.resampling_policy,
            config,
            realized_epochs: &realized,
            target_semantics:
                "ordinary_physical_filter_for_configured_family_no_additional_scientific_evidence",
            candidate_allocation_semantics:
                "exactly_l_transition_candidates_per_finite_mass_root_within_each_scientific_stratum",
            generic_checkpoint_candidates_per_particle_semantics:
                "zero_is_a_typed_sentinel_for_root_stratified_allocation;operative_l_is_candidates_per_positive_root_in_the_paired_root_checkpoint",
            weighting_semantics:
                "proper_physical_candidate_measure_with_exact_root_defensive_output_proposal_correction",
            transition_pool_checkpoints: &result.transition_pool_checkpoints,
            root_stratified_candidate_pool_checkpoints: &result
                .root_stratified_candidate_pool_checkpoints,
        })
        .unwrap();
        assert_eq!(
            value["schema"],
            "mh370-broad-root-stratified-transition-pool-diagnostics-v1"
        );
        assert_eq!(
            value["transition_pool_checkpoints"][0]["candidates_per_particle"],
            0
        );
        assert_eq!(
            value["root_stratified_candidate_pool_checkpoints"][0]["candidates_per_positive_root"],
            4
        );
        assert!(
            value["generic_checkpoint_candidates_per_particle_semantics"]
                .as_str()
                .unwrap()
                .contains("zero_is_a_typed_sentinel")
        );
        assert_eq!(
            value["target_semantics"],
            "ordinary_physical_filter_for_configured_family_no_additional_scientific_evidence"
        );
        assert_eq!(value["run_identity_sha256"], "b".repeat(64));
        assert_eq!(value["input_sha256"]["fixture"], "a".repeat(64));
    }

    fn intermediate_bridge_config_text(explicit: bool) -> String {
        let table = if explicit {
            "[intermediate_satcom_bridge]\n\
             early_offset_s = 1800.0\n\
             late_offset_s = 2940.0\n\
             minimum_interval_s = 3000.0\n\
             early_candidates_per_particle = 2\n\
             late_candidates_per_particle = 4\n\
             endpoint_candidates_per_particle = 1\n\
             potential_floor = 0.02\n\
             bto_projection_sd_us_per_remaining_hour = 900.0\n\
             bfo_projection_sd_hz_per_remaining_hour = 60.0"
        } else {
            "[intermediate_satcom_bridge]"
        };
        include_str!("../../../configs/mh370-broad-powered-flight-pilot.toml")
            .replacen("proposal_candidates = 8", "proposal_candidates = 1", 1)
            .replacen(
                "seeds = [370023]",
                &format!("seeds = [370023]\n\n{table}"),
                1,
            )
    }

    #[test]
    fn intermediate_bridge_defaults_and_explicit_toml_resolve_identically() {
        let defaulted: BroadSuiteConfig =
            toml::from_str(&intermediate_bridge_config_text(false)).unwrap();
        let explicit: BroadSuiteConfig =
            toml::from_str(&intermediate_bridge_config_text(true)).unwrap();
        validate_suite(&defaulted).unwrap();
        validate_suite(&explicit).unwrap();
        let config = defaulted.intermediate_satcom_bridge.unwrap();
        assert_eq!(Some(config), explicit.intermediate_satcom_bridge);
        assert_eq!(config, BroadIntermediateSatcomBridgeConfig::default());
        assert_eq!(
            serde_json::to_value(config).unwrap(),
            serde_json::json!({
                "early_offset_s": 1800.0,
                "late_offset_s": 2940.0,
                "minimum_interval_s": 3000.0,
                "early_candidates_per_particle": 2,
                "late_candidates_per_particle": 4,
                "endpoint_candidates_per_particle": 1,
                "potential_floor": 0.02,
                "bto_projection_sd_us_per_remaining_hour": 900.0,
                "bfo_projection_sd_hz_per_remaining_hour": 60.0
            })
        );
        assert_eq!(config.resolved().potential_floor, 0.02);

        let mut neutral = config;
        neutral.potential_floor = 1.0;
        neutral.resolved().validate().unwrap();
        assert!(intermediate_satcom_bridge_inference_descriptor(neutral).contains("delta=1;"));
    }

    #[test]
    fn intermediate_bridge_realizes_only_long_bto_endpoint_intervals() {
        let suite: BroadSuiteConfig =
            toml::from_str(&intermediate_bridge_config_text(false)).unwrap();
        let config = suite.intermediate_satcom_bridge.unwrap();
        let observations = observations_for_family(
            &suite,
            &suite.families[1],
            include_str!("../../../inputs/accident/satcom-through-0011.csv"),
            include_str!("../../../inputs/accident/satellite-through-0011.csv"),
        )
        .unwrap();
        let (steps, realized) = realized_intermediate_satcom_bridge_epochs(
            config,
            &observations,
            suite.filter.initial_time_s,
        )
        .unwrap();
        assert_eq!(steps.len(), observations.len());
        assert_eq!(realized.len(), observations.len());
        let bridged = realized
            .iter()
            .filter(|epoch| matches!(epoch.step, IntermediatePotentialStep::Bridge { .. }))
            .map(|epoch| epoch.observation_id.as_str())
            .collect::<Vec<_>>();
        assert_eq!(bridged, ["m1941", "m2041", "m2141", "m2241", "m0011"]);
        assert!(realized.iter().any(|epoch| {
            epoch.observation_kind == "fuel_anchor"
                && matches!(epoch.step, IntermediatePotentialStep::Standard)
        }));
        let m1941 = realized
            .iter()
            .find(|epoch| epoch.observation_id == "m1941")
            .unwrap();
        let IntermediatePotentialStep::Bridge { points } = &m1941.step else {
            panic!("m1941 should be bridged")
        };
        let interval_start_s = m1941.observation_time_s - m1941.elapsed_seconds;
        assert_eq!(points.len(), 2);
        assert_eq!(points[0].point.interval_start.0, interval_start_s);
        assert_eq!(points[0].point.time.0, interval_start_s + 1_800.0);
        assert_eq!(points[0].candidates_per_particle, 2);
        assert_eq!(points[1].point.time.0, interval_start_s + 2_940.0);
        assert_eq!(points[1].candidates_per_particle, 4);

        let mut pooled_config = config;
        pooled_config.endpoint_candidates_per_particle = 4;
        let (_, pooled_realized) = realized_intermediate_satcom_bridge_epochs(
            pooled_config,
            &observations,
            suite.filter.initial_time_s,
        )
        .unwrap();
        assert!(matches!(
            &pooled_realized
                .iter()
                .find(|epoch| epoch.observation_id == "m1941")
                .unwrap()
                .step,
            IntermediatePotentialStep::BridgeWithEndpointPool {
                endpoint_candidates_per_particle: 4,
                ..
            }
        ));
        assert!(
            intermediate_satcom_bridge_inference_descriptor(pooled_config)
                .contains("endpoint-candidates-per-particle=4;")
        );
    }

    #[test]
    fn intermediate_bridge_rejects_other_inference_designs_and_nonlocal_k1() {
        let mut suite: BroadSuiteConfig =
            toml::from_str(&intermediate_bridge_config_text(false)).unwrap();
        suite.islands = Some(BroadIslandConfig {
            islands_per_stratum: 2,
            particles_per_island: 100,
        });
        assert!(validate_suite(&suite)
            .unwrap_err()
            .to_string()
            .contains("mutually exclusive"));

        suite.islands = None;
        suite.model.proposal_candidates = 2;
        assert!(validate_suite(&suite)
            .unwrap_err()
            .to_string()
            .contains("constant local proposal_candidates = 1"));

        suite.model.proposal_candidates = 1;
        suite.filter.algorithm = Algorithm::Auxiliary;
        assert!(validate_suite(&suite)
            .unwrap_err()
            .to_string()
            .contains("bootstrap filter algorithm"));

        suite.filter.algorithm = Algorithm::Bootstrap;
        suite
            .intermediate_satcom_bridge
            .as_mut()
            .unwrap()
            .endpoint_candidates_per_particle = 0;
        assert!(validate_suite(&suite)
            .unwrap_err()
            .to_string()
            .contains("endpoint candidates per particle must be positive"));
    }

    #[test]
    fn intermediate_bridge_diagnostics_contract_is_provenance_bound() {
        let suite: BroadSuiteConfig =
            toml::from_str(&intermediate_bridge_config_text(false)).unwrap();
        let config = suite.intermediate_satcom_bridge.unwrap();
        let observations = observations_for_family(
            &suite,
            &suite.families[0],
            include_str!("../../../inputs/accident/satcom-through-0011.csv"),
            include_str!("../../../inputs/accident/satellite-through-0011.csv"),
        )
        .unwrap();
        let (_, realized) = realized_intermediate_satcom_bridge_epochs(
            config,
            &observations,
            suite.filter.initial_time_s,
        )
        .unwrap();
        let input_sha256 = BTreeMap::from([("fixture".to_string(), "a".repeat(64))]);
        let value = serde_json::to_value(BroadIntermediatePotentialDiagnosticsArtifact {
            schema: "mh370-broad-intermediate-potential-diagnostics-v1",
            schema_version: 1,
            model_family: mh370_estimator::BROAD_FLIGHT_MODEL_FAMILY,
            guide_family: BROAD_SATCOM_INTERMEDIATE_POTENTIAL_FAMILY,
            family: "bto-only",
            seed: 370023,
            run_identity_sha256: &"b".repeat(64),
            config_sha256: &"c".repeat(64),
            input_sha256: &input_sha256,
            filter: &suite.filter,
            resampling_policy: suite.resampling_policy,
            config,
            realized_epochs: &realized,
            potential_semantics:
                "strictly_positive_terminal_tangent_satcom_compatibility_guide_not_scientific_evidence",
            weighting_semantics:
                "exact_telescoping_h_ratio_then_endpoint_g_over_h_with_proper_candidate_and_output_proposal_corrections",
            checkpoints: &[],
        })
        .unwrap();
        assert_eq!(
            value["schema"],
            "mh370-broad-intermediate-potential-diagnostics-v1"
        );
        assert_eq!(
            value["guide_family"],
            BROAD_SATCOM_INTERMEDIATE_POTENTIAL_FAMILY
        );
        assert_eq!(value["config"]["early_offset_s"], 1800.0);
        assert_eq!(value["run_identity_sha256"], "b".repeat(64));
        assert_eq!(value["input_sha256"]["fixture"], "a".repeat(64));
        assert_eq!(value["realized_epochs"].as_array().unwrap().len(), 11);
        assert_eq!(value["checkpoints"], serde_json::json!([]));
    }

    fn synthetic_seed_population(
        seed: u64,
        log_evidence: f64,
        particle_weights: &[f64],
        root_masses: &[f64],
    ) -> BroadSeedPosteriorPopulation {
        BroadSeedPosteriorPopulation {
            seed,
            log_evidence,
            points: particle_weights
                .iter()
                .enumerate()
                .map(|(index, &weight)| ReportPoint {
                    latitude_deg: index as f64,
                    longitude_deg: -(index as f64),
                    weight,
                })
                .collect(),
            root_masses: root_masses.to_vec(),
        }
    }

    #[test]
    fn unequal_seed_evidence_controls_the_combined_posterior_and_metrics() {
        let (points, pooling) = pool_independent_seed_posteriors(vec![
            synthetic_seed_population(11, 9.0_f64.ln(), &[0.5, 0.5], &[1.0]),
            synthetic_seed_population(22, 0.0, &[1.0], &[1.0]),
        ])
        .unwrap();
        let pooling = pooling.expect("two seeds require an explicit pooling ledger");
        let close = |actual: f64, expected: f64| (actual - expected).abs() < 1.0e-12;
        assert!(close(
            pooling.seed_evidence_weights[0].normalized_evidence_weight,
            0.9
        ));
        assert!(close(
            pooling.seed_evidence_weights[1].normalized_evidence_weight,
            0.1
        ));
        assert_ne!(
            pooling.seed_evidence_weights[0].normalized_evidence_weight,
            0.5
        );
        assert!(close(points[0].weight, 0.45));
        assert!(close(points[1].weight, 0.45));
        assert!(close(points[2].weight, 0.1));
        assert!(close(
            pooling.evidence_weight_effective_sample_size,
            1.0 / (0.9_f64.powi(2) + 0.1_f64.powi(2))
        ));
        assert!(close(pooling.maximum_seed_evidence_weight, 0.9));
        assert!(close(
            pooling.pooled_particle_effective_sample_size,
            1.0 / (0.45_f64.powi(2) + 0.45_f64.powi(2) + 0.1_f64.powi(2))
        ));
        // Both synthetic seeds deliberately reuse root 0. Treating seed as
        // part of root identity keeps the two masses distinct.
        assert!(close(
            pooling.seed_namespaced_root_effective_sample_size,
            1.0 / (0.9_f64.powi(2) + 0.1_f64.powi(2))
        ));
        assert!(close(pooling.maximum_seed_namespaced_root_weight, 0.9));
        assert_eq!(
            serde_json::to_value(&pooling).unwrap()["pooling_semantics"],
            "evidence_weighted_independent_posterior_mixture"
        );
    }

    #[test]
    fn single_seed_combined_points_preserve_the_conditional_weights_exactly() {
        let original = [0.25_f64, 0.75_f64];
        let (points, pooling) = pool_independent_seed_posteriors(vec![synthetic_seed_population(
            11,
            -123.0,
            &original,
            &[1.0],
        )])
        .unwrap();
        assert!(pooling.is_none());
        assert_eq!(points.len(), original.len());
        for (point, expected) in points.iter().zip(original) {
            assert_eq!(point.weight.to_bits(), expected.to_bits());
        }
    }

    fn fuel_selection_guide_config_text(potential_floor: f64) -> String {
        include_str!("../../../configs/mh370-broad-powered-flight-pilot.toml")
            .replacen("proposal_candidates = 8", "proposal_candidates = 1", 1)
            .replacen(
                "seeds = [370023]",
                &format!(
                    "seeds = [370023]\n\n\
                     [fuel_exhaustion_selection_guide]\n\
                     potential_floor = {potential_floor}\n\
                     canonical_full_satcom_observations = \"../inputs/accident/satcom-observations.csv\"\n\
                     window_start_epoch_id = \"m0011\"\n\
                     window_end_epoch_id = \"m0019a\"\n\
                     window_end_contact_offset_s = 0.416"
                ),
                1,
            )
    }

    #[test]
    fn fuel_selection_guide_time_window_is_locked_to_the_canonical_full_source() {
        let suite: BroadSuiteConfig =
            toml::from_str(&fuel_selection_guide_config_text(0.02)).unwrap();
        validate_suite(&suite).unwrap();
        let guide = suite.fuel_exhaustion_selection_guide.as_ref().unwrap();
        let window = resolve_fuel_exhaustion_guide_window(
            guide,
            include_bytes!("../../../inputs/accident/satcom-observations.csv"),
        )
        .unwrap();
        assert_eq!(window.window_start_s, 22_150.0);
        assert_eq!(window.canonical_window_end_s, 22_660.0);
        assert_eq!(window.window_end_contact_offset_s, 0.416);
        assert_eq!(window.window_end_s, 22_660.416);

        let neutral: BroadSuiteConfig =
            toml::from_str(&fuel_selection_guide_config_text(1.0)).unwrap();
        validate_suite(&neutral).unwrap();

        let defaulted: BroadSuiteConfig = toml::from_str(
            &fuel_selection_guide_config_text(0.02).replace("potential_floor = 0.02\n", ""),
        )
        .unwrap();
        assert_eq!(
            defaulted
                .fuel_exhaustion_selection_guide
                .unwrap()
                .potential_floor,
            0.02
        );
    }

    #[test]
    fn fuel_selection_guide_starts_strictly_after_the_anchor_and_neutral_is_unguided() {
        let suite: BroadSuiteConfig =
            toml::from_str(&fuel_selection_guide_config_text(0.02)).unwrap();
        let guide = suite.fuel_exhaustion_selection_guide.as_ref().unwrap();
        let window = resolve_fuel_exhaustion_guide_window(
            guide,
            include_bytes!("../../../inputs/accident/satcom-observations.csv"),
        )
        .unwrap();
        let mut observations = observations_for_family(
            &suite,
            &suite.families[0],
            include_str!("../../../inputs/accident/satcom-through-0011.csv"),
            include_str!("../../../inputs/accident/satellite-through-0011.csv"),
        )
        .unwrap();
        let short_index = observations
            .iter()
            .position(|observation| observation.id() == "m1828b")
            .unwrap();
        let short_time = observations[short_index].time();
        observations[short_index] = BroadFlightObservation::Checkpoint {
            id: "short-post-anchor-checkpoint".to_string(),
            time: short_time,
        };
        let (steps, realized) =
            realized_fuel_exhaustion_selection_guide_epochs(guide, window, &observations).unwrap();
        assert_eq!(steps.len(), observations.len());
        let anchor = realized
            .iter()
            .position(|epoch| epoch.observation_kind == "fuel_anchor")
            .unwrap();
        assert!(realized[..=anchor].iter().all(|epoch| {
            !epoch.after_fuel_anchor && matches!(epoch.step, SelectionGuideStep::Unguided)
        }));
        assert!(realized[anchor + 1..].iter().all(|epoch| {
            epoch.after_fuel_anchor && matches!(epoch.step, SelectionGuideStep::Guide { .. })
        }));
        assert_eq!(
            realized[anchor + 1].observation_id,
            "short-post-anchor-checkpoint"
        );
        assert!(matches!(
            realized.last().unwrap().step,
            SelectionGuideStep::Guide {
                point: BroadFuelExhaustionSelectionGuidePoint {
                    window_start: Seconds(22_150.0),
                    window_end: Seconds(22_660.416),
                }
            }
        ));

        let neutral: BroadSuiteConfig =
            toml::from_str(&fuel_selection_guide_config_text(1.0)).unwrap();
        let (_, neutral_realized) = realized_fuel_exhaustion_selection_guide_epochs(
            neutral.fuel_exhaustion_selection_guide.as_ref().unwrap(),
            window,
            &observations,
        )
        .unwrap();
        assert!(neutral_realized
            .iter()
            .all(|epoch| matches!(epoch.step, SelectionGuideStep::Unguided)));
    }

    #[test]
    fn fuel_selection_guide_coexists_with_endpoint_k4_bridge() {
        let mut suite: BroadSuiteConfig =
            toml::from_str(&fuel_selection_guide_config_text(0.02)).unwrap();
        suite.intermediate_satcom_bridge = Some(BroadIntermediateSatcomBridgeConfig {
            endpoint_candidates_per_particle: 4,
            ..BroadIntermediateSatcomBridgeConfig::default()
        });
        validate_suite(&suite).unwrap();
        assert_eq!(
            suite
                .intermediate_satcom_bridge
                .unwrap()
                .endpoint_candidates_per_particle,
            4
        );
    }

    #[test]
    fn fuel_selection_diagnostics_skip_zero_weight_pre_anchor_placeholders() {
        let fuel_anchor_counts = [0_u32, 1_u32];
        let log_weights = [f64::NEG_INFINITY, 0.0];
        let roots = [17_usize, 23_usize];
        let mut visited = Vec::new();
        let positive = visit_positive_weight_slots(
            &fuel_anchor_counts,
            &log_weights,
            &roots,
            |slot, &fuel_anchor_count, weight, root| {
                if fuel_anchor_count != 1 {
                    bail!("zero-mass pre-anchor placeholder was evaluated");
                }
                visited.push((slot, weight, root));
                Ok(())
            },
        )
        .unwrap();
        assert_eq!(positive, 1);
        assert_eq!(visited, [(1, 1.0, 23)]);
    }

    #[test]
    fn fuel_selection_guide_rejects_unlocked_source_semantics_and_incompatible_inference() {
        let text = fuel_selection_guide_config_text(0.02);
        let mut suite: BroadSuiteConfig = toml::from_str(&text).unwrap();
        suite
            .fuel_exhaustion_selection_guide
            .as_mut()
            .unwrap()
            .window_end_contact_offset_s = 0.0;
        assert!(validate_suite(&suite)
            .unwrap_err()
            .to_string()
            .contains("invalid v1 fuel-exhaustion"));

        let mut suite: BroadSuiteConfig = toml::from_str(&text).unwrap();
        suite.model.proposal_candidates = 2;
        assert!(validate_suite(&suite)
            .unwrap_err()
            .to_string()
            .contains("constant local proposal_candidates = 1"));

        let mut suite: BroadSuiteConfig = toml::from_str(&text).unwrap();
        suite.islands = Some(BroadIslandConfig {
            islands_per_stratum: 2,
            particles_per_island: 100,
        });
        assert!(validate_suite(&suite)
            .unwrap_err()
            .to_string()
            .contains("cannot be combined with islands"));

        let suite: BroadSuiteConfig = toml::from_str(&text).unwrap();
        let guide = suite.fuel_exhaustion_selection_guide.as_ref().unwrap();
        let corrupted = include_str!("../../../inputs/accident/satcom-observations.csv")
            .replace("22660.0,18400,63,,,", "22660.0,18400,63,1.0,7.0,");
        assert!(
            resolve_fuel_exhaustion_guide_window(guide, corrupted.as_bytes())
                .unwrap_err()
                .to_string()
                .contains("not the guarded R600 BTO-only source")
        );
    }

    fn synthetic_fuel_selection_population(
        seed: u64,
        compatible_mass: f64,
        compatible_slots: usize,
    ) -> BroadFuelExhaustionPosteriorPopulation {
        let retained_slots = 10;
        BroadFuelExhaustionPosteriorPopulation {
            seed,
            summary: BroadFuelExhaustionPosteriorSummary {
                retained_slots,
                positive_weight_slots: retained_slots,
                zero_weight_placeholder_slots: 0,
                outcomes: fuel_selection_outcomes()
                    .into_iter()
                    .map(|outcome| BroadFuelExhaustionOutcomeSummary {
                        retained_slots: match outcome {
                            BroadFuelExhaustionSelectionGuideOutcome::Compatible => {
                                compatible_slots
                            }
                            BroadFuelExhaustionSelectionGuideOutcome::OutsideWindow => {
                                retained_slots - compatible_slots
                            }
                            _ => 0,
                        },
                        posterior_mass: match outcome {
                            BroadFuelExhaustionSelectionGuideOutcome::Compatible => compatible_mass,
                            BroadFuelExhaustionSelectionGuideOutcome::OutsideWindow => {
                                1.0 - compatible_mass
                            }
                            _ => 0.0,
                        },
                        outcome,
                    })
                    .collect(),
                compatible_retained_slot_fraction: compatible_slots as f64 / retained_slots as f64,
                compatible_positive_weight_slots: compatible_slots,
                compatible_positive_weight_slot_fraction: compatible_slots as f64
                    / retained_slots as f64,
                distinct_compatible_seed_local_roots: usize::from(compatible_mass > 0.0) * 2,
                compatible_posterior_mass: compatible_mass,
                compatible_root_effective_sample_size: (compatible_mass > 0.0).then_some(2.0),
                maximum_compatible_root_weight: (compatible_mass > 0.0).then_some(0.5),
                compatible_projected_exhaustion_time_min_s: (compatible_mass > 0.0)
                    .then_some(22_200.0),
                compatible_projected_exhaustion_time_mean_s: (compatible_mass > 0.0)
                    .then_some(22_300.0),
                compatible_projected_exhaustion_time_max_s: (compatible_mass > 0.0)
                    .then_some(22_400.0),
                compatible_strata: vec![BroadFuelExhaustionCompatibleStratumSummary {
                    stratum: 7,
                    compatible_positive_weight_slots: compatible_slots,
                    distinct_compatible_seed_local_roots: usize::from(compatible_mass > 0.0) * 2,
                    compatible_physical_posterior_mass: compatible_mass,
                    compatible_physical_root_effective_sample_size: (compatible_mass > 0.0)
                        .then_some(2.0),
                    maximum_compatible_physical_root_weight: (compatible_mass > 0.0).then_some(0.5),
                }],
            },
            compatible_root_masses: if compatible_mass > 0.0 {
                vec![compatible_mass / 2.0; 2]
            } else {
                Vec::new()
            },
            compatible_root_masses_by_stratum: if compatible_mass > 0.0 {
                BTreeMap::from([(7, vec![compatible_mass / 2.0; 2])])
            } else {
                BTreeMap::new()
            },
        }
    }

    #[test]
    fn fuel_selection_compatibility_uses_evidence_weighted_seed_mixture() {
        let (_, seed_pooling) = pool_independent_seed_posteriors(vec![
            synthetic_seed_population(11, 9.0_f64.ln(), &[1.0], &[1.0]),
            synthetic_seed_population(22, 0.0, &[1.0], &[1.0]),
        ])
        .unwrap();
        let pooled = pool_fuel_exhaustion_selection_posteriors(
            &[
                synthetic_fuel_selection_population(11, 1.0, 8),
                synthetic_fuel_selection_population(22, 0.0, 0),
            ],
            seed_pooling.as_ref(),
        )
        .unwrap();
        assert!((pooled.compatible_posterior_mass - 0.9).abs() < 1.0e-12);
        assert!((pooled.compatible_retained_slot_fraction - 0.4).abs() < 1.0e-12);
        assert!((pooled.compatible_positive_weight_slot_fraction - 0.4).abs() < 1.0e-12);
        assert_eq!(pooled.compatible_positive_weight_slots, 8);
        assert!((pooled.compatible_root_effective_sample_size.unwrap() - 2.0).abs() < 1.0e-12);
        assert!((pooled.maximum_compatible_root_weight.unwrap() - 0.5).abs() < 1.0e-12);
        assert_eq!(pooled.distinct_compatible_seed_local_roots, 2);
        assert_eq!(pooled.compatible_strata.len(), 1);
        assert_eq!(pooled.compatible_strata[0].stratum, 7);
        assert_eq!(
            pooled.compatible_strata[0].compatible_positive_weight_slots,
            8
        );
        assert!(
            (pooled.compatible_strata[0].compatible_physical_posterior_mass - 0.9).abs() < 1.0e-12
        );
        assert!(
            (pooled.compatible_strata[0]
                .compatible_physical_root_effective_sample_size
                .unwrap()
                - 2.0)
                .abs()
                < 1.0e-12
        );
        assert_ne!(pooled.compatible_posterior_mass, 0.5);
    }

    #[test]
    fn fuel_selection_diagnostics_contract_records_proposal_only_provenance() {
        let suite: BroadSuiteConfig =
            toml::from_str(&fuel_selection_guide_config_text(0.02)).unwrap();
        let config = suite.fuel_exhaustion_selection_guide.as_ref().unwrap();
        let window = resolve_fuel_exhaustion_guide_window(
            config,
            include_bytes!("../../../inputs/accident/satcom-observations.csv"),
        )
        .unwrap();
        let observations = observations_for_family(
            &suite,
            &suite.families[0],
            include_str!("../../../inputs/accident/satcom-through-0011.csv"),
            include_str!("../../../inputs/accident/satellite-through-0011.csv"),
        )
        .unwrap();
        let (_, realized) =
            realized_fuel_exhaustion_selection_guide_epochs(config, window, &observations).unwrap();
        let posterior = synthetic_fuel_selection_population(370023, 0.25, 3).summary;
        let input_sha256 = BTreeMap::from([(
            "fuel_guide_canonical_satcom_observations".to_string(),
            "a".repeat(64),
        )]);
        let value = serde_json::to_value(BroadFuelExhaustionSelectionGuideDiagnosticsArtifact {
            schema: "mh370-broad-fuel-exhaustion-selection-guide-diagnostics-v1",
            schema_version: 1,
            model_family: mh370_estimator::BROAD_FLIGHT_MODEL_FAMILY,
            guide_family: BROAD_FUEL_EXHAUSTION_SELECTION_GUIDE_FAMILY,
            family: "bto-only",
            seed: 370023,
            run_identity_sha256: &"b".repeat(64),
            config_sha256: &"c".repeat(64),
            input_sha256: &input_sha256,
            filter: &suite.filter,
            resampling_policy: suite.resampling_policy,
            config,
            resolved_estimator_config: config.resolved(),
            guide_descriptor: config.resolved().stable_descriptor(),
            resolved_window: window,
            realized_epochs: &realized,
            proposal_semantics:
                "strictly_positive_frozen_operating_point_compatibility_selection_with_exact_target_over_proposal_correction",
            evidence_semantics:
                "computational_proposal_only_no_fuel_logon_or_satcom_likelihood_and_no_change_to_the_evidence_ledger",
            canonical_source_semantics:
                "hash_locked_full_satcom_source_supplies_window_times_only;the_window_rows_are_not_inserted_consumed_or_scored_by_the_guide",
            guided_standard_checkpoints: &[],
            intermediate_potential_checkpoints: &[],
            final_posterior: &posterior,
        })
        .unwrap();
        assert_eq!(
            value["guide_family"],
            BROAD_FUEL_EXHAUSTION_SELECTION_GUIDE_FAMILY
        );
        assert_eq!(value["config"]["potential_floor"], 0.02);
        assert_eq!(
            value["config"]["canonical_full_satcom_observations"],
            "../inputs/accident/satcom-observations.csv"
        );
        assert_eq!(value["resolved_window"]["window_end_s"], 22_660.416);
        assert!(value["guide_descriptor"]
            .as_str()
            .unwrap()
            .contains("tau>window-start+0.000001s-and-tau<window-end-0.000001s"));
        assert_eq!(
            value["input_sha256"]["fuel_guide_canonical_satcom_observations"],
            "a".repeat(64)
        );
        assert!(value["evidence_semantics"]
            .as_str()
            .unwrap()
            .contains("no_change_to_the_evidence_ledger"));
        assert!(value["realized_epochs"]
            .as_array()
            .unwrap()
            .iter()
            .any(|epoch| {
                epoch["observation_id"] == "m0011" && epoch["step"]["kind"] == "guide"
            }));
    }

    fn persistent_twist_config_text(potential_floor: Option<f64>) -> String {
        let floor = potential_floor
            .map(|value| format!("potential_floor = {value}\n"))
            .unwrap_or_default();
        include_str!("../../../configs/mh370-broad-powered-flight-pilot.toml")
            .replacen("proposal_candidates = 8", "proposal_candidates = 1", 1)
            .replacen(
                "seeds = [370023]",
                &format!(
                    "seeds = [370023]\n\n\
                     [fuel_exhaustion_persistent_twist]\n\
                     {floor}\
                     canonical_full_satcom_observations = \"../inputs/accident/satcom-observations.csv\"\n\
                     window_start_epoch_id = \"m0011\"\n\
                     window_end_epoch_id = \"m0019a\"\n\
                     window_end_contact_offset_s = 0.416"
                ),
                1,
            )
    }

    #[test]
    fn persistent_twist_toml_absence_default_floor_and_explicit_fields_are_stable() {
        let absent: BroadSuiteConfig = toml::from_str(include_str!(
            "../../../configs/mh370-broad-powered-flight-pilot.toml"
        ))
        .unwrap();
        assert!(absent.fuel_exhaustion_persistent_twist.is_none());

        let defaulted: BroadSuiteConfig =
            toml::from_str(&persistent_twist_config_text(None)).unwrap();
        let explicit: BroadSuiteConfig =
            toml::from_str(&persistent_twist_config_text(Some(0.02))).unwrap();
        validate_suite(&defaulted).unwrap();
        validate_suite(&explicit).unwrap();
        assert_eq!(
            defaulted.fuel_exhaustion_persistent_twist,
            explicit.fuel_exhaustion_persistent_twist
        );
        let config = explicit.fuel_exhaustion_persistent_twist.unwrap();
        assert_eq!(config.potential_floor, 0.02);
        assert_eq!(config.window_start_epoch_id, "m0011");
        assert_eq!(config.window_end_epoch_id, "m0019a");
        assert_eq!(config.window_end_contact_offset_s, 0.416);
    }

    #[test]
    fn persistent_twist_lifecycle_is_anchor_causal_and_finalizes_exactly_at_fit_through() {
        let suite: BroadSuiteConfig =
            toml::from_str(&persistent_twist_config_text(Some(0.02))).unwrap();
        let config = suite.fuel_exhaustion_persistent_twist.as_ref().unwrap();
        let window = resolve_fuel_exhaustion_guide_window(
            config,
            include_bytes!("../../../inputs/accident/satcom-observations.csv"),
        )
        .unwrap();
        let observations = observations_for_family(
            &suite,
            &suite.families[0],
            include_str!("../../../inputs/accident/satcom-through-0011.csv"),
            include_str!("../../../inputs/accident/satellite-through-0011.csv"),
        )
        .unwrap();
        let (steps, realized) = realized_fuel_exhaustion_persistent_twist_epochs(
            config,
            window,
            &observations,
            "m0011",
        )
        .unwrap();
        assert!(persistent_twist_schedule_is_active(&steps));
        let anchor = realized
            .iter()
            .position(|epoch| epoch.observation_kind == "fuel_anchor")
            .unwrap();
        assert!(realized[..=anchor]
            .iter()
            .all(|epoch| matches!(epoch.step, PersistentTwistStep::Inactive)));
        assert!(matches!(
            realized[anchor + 1].step,
            PersistentTwistStep::Activate { .. }
        ));
        assert!(realized[anchor + 2..realized.len() - 1]
            .iter()
            .all(|epoch| matches!(epoch.step, PersistentTwistStep::Continue { .. })));
        let final_epoch = realized.last().unwrap();
        assert_eq!(final_epoch.observation_id, "m0011");
        assert_eq!(final_epoch.observation_time_s, 22_150.0);
        assert!(matches!(
            final_epoch.step,
            PersistentTwistStep::Finalize {
                point: BroadFuelExhaustionSelectionGuidePoint {
                    window_start: Seconds(22_150.0),
                    window_end: Seconds(22_660.416),
                }
            }
        ));
    }

    #[test]
    fn neutral_persistent_twist_realizes_all_inactive_and_selects_the_legacy_path() {
        let suite: BroadSuiteConfig =
            toml::from_str(&persistent_twist_config_text(Some(1.0))).unwrap();
        validate_suite(&suite).unwrap();
        let config = suite.fuel_exhaustion_persistent_twist.as_ref().unwrap();
        let window = resolve_fuel_exhaustion_guide_window(
            config,
            include_bytes!("../../../inputs/accident/satcom-observations.csv"),
        )
        .unwrap();
        let observations = observations_for_family(
            &suite,
            &suite.families[0],
            include_str!("../../../inputs/accident/satcom-through-0011.csv"),
            include_str!("../../../inputs/accident/satellite-through-0011.csv"),
        )
        .unwrap();
        let (steps, realized) = realized_fuel_exhaustion_persistent_twist_epochs(
            config,
            window,
            &observations,
            "m0011",
        )
        .unwrap();
        assert!(steps
            .iter()
            .all(|step| matches!(step, PersistentTwistStep::Inactive)));
        assert!(!persistent_twist_schedule_is_active(&steps));
        assert_eq!(steps.len(), realized.len());
        let descriptor =
            fuel_exhaustion_persistent_twist_inference_descriptor(config, window).unwrap();
        assert!(descriptor.contains("execution=neutral-all-inactive-legacy-filter-path"));
        assert!(descriptor.contains("tau>window-start+0.000001s"));
    }

    #[test]
    fn active_persistent_twist_accepts_bridge_and_rejects_other_inference_designs() {
        let text = persistent_twist_config_text(Some(0.02));
        let mut suite: BroadSuiteConfig = toml::from_str(&text).unwrap();
        suite.intermediate_satcom_bridge = Some(BroadIntermediateSatcomBridgeConfig::default());
        validate_suite(&suite).unwrap();

        let twist = suite.fuel_exhaustion_persistent_twist.clone();
        suite.fuel_exhaustion_selection_guide = twist;
        assert!(validate_suite(&suite)
            .unwrap_err()
            .to_string()
            .contains("mutually exclusive"));

        let mut suite: BroadSuiteConfig = toml::from_str(&text).unwrap();
        suite.islands = Some(BroadIslandConfig {
            islands_per_stratum: 2,
            particles_per_island: 100,
        });
        assert!(validate_suite(&suite)
            .unwrap_err()
            .to_string()
            .contains("cannot be combined with islands"));

        let mut suite: BroadSuiteConfig = toml::from_str(&text).unwrap();
        suite.global_transition_pool = Some(
            BroadGlobalTransitionPoolSchedule::ObservationIntervalTiers {
                tiers: vec![BroadGlobalTransitionPoolTier {
                    minimum_elapsed_seconds: 3_000.0,
                    candidates_per_particle: 4,
                }],
            },
        );
        assert!(validate_suite(&suite)
            .unwrap_err()
            .to_string()
            .contains("separate global transition pool"));

        let mut suite: BroadSuiteConfig = toml::from_str(&text).unwrap();
        suite.model.proposal_candidates = 2;
        assert!(validate_suite(&suite)
            .unwrap_err()
            .to_string()
            .contains("constant local proposal_candidates = 1"));
    }

    fn synthetic_filter_checkpoint(
        index: usize,
        time_s: f64,
        increment: f64,
        cumulative: f64,
    ) -> FilterCheckpoint {
        let ess = 1.0 / (0.4_f64.powi(2) + 0.6_f64.powi(2));
        FilterCheckpoint {
            observation_index: index,
            observation_time_s: time_s,
            guide_ess: None,
            posterior_ess: ess,
            ancestor_resampled: false,
            posterior_resampled: true,
            log_evidence_increment: increment,
            cumulative_log_evidence: cumulative,
            maximum_normalized_weight: 0.6,
            distinct_root_ancestors: 2,
            root_effective_sample_size: ess,
            maximum_root_weight: 0.6,
            roots_with_mass_at_least_1e_6: 2,
            roots_with_mass_at_least_1e_3: 2,
            strata: Vec::new(),
        }
    }

    fn synthetic_twist_population(
        positive_particles: usize,
    ) -> PersistentTwistPopulationDiagnostics {
        let ess = 1.0 / (0.4_f64.powi(2) + 0.6_f64.powi(2));
        PersistentTwistPopulationDiagnostics {
            positive_particles,
            minimum_log_potential: 0.02_f64.ln(),
            maximum_log_potential: 0.0,
            twisted_effective_sample_size: 1.8,
            twisted_maximum_particle_weight: 0.7,
            twisted_distinct_positive_roots: positive_particles,
            twisted_root_effective_sample_size: 1.8,
            twisted_maximum_root_weight: 0.7,
            twisted_strata: Vec::new(),
            log_implied_untwist_correction: -0.2,
            implied_untwisted_effective_sample_size: ess,
            implied_untwisted_maximum_particle_weight: 0.6,
            implied_untwisted_distinct_positive_roots: positive_particles,
            implied_untwisted_root_effective_sample_size: ess,
            implied_untwisted_maximum_root_weight: 0.6,
            implied_untwisted_strata: Vec::new(),
        }
    }

    fn synthetic_pool_checkpoint(
        index: usize,
        time_s: f64,
        increment: f64,
    ) -> GlobalTransitionPoolCheckpoint {
        GlobalTransitionPoolCheckpoint {
            observation_index: index,
            observation_time_s: time_s,
            candidates_per_particle: 1,
            configured_candidates: 2,
            generated_candidates: 2,
            positive_candidates: 2,
            candidate_log_evidence_increment: increment,
            output_resampling_log_correction: 0.0,
            realized_log_evidence_increment: increment,
            candidate_effective_sample_size: 2.0,
            maximum_candidate_weight: 0.5,
            distinct_positive_candidate_roots: 2,
            candidate_root_effective_sample_size: 2.0,
            maximum_candidate_root_weight: 0.5,
            strata: Vec::new(),
        }
    }

    fn synthetic_persistent_diagnostics() -> (
        Vec<BroadRealizedFuelExhaustionPersistentTwistEpoch>,
        FilterResult<()>,
        BroadPersistentTwistExecutionDiagnostics,
    ) {
        let point = BroadFuelExhaustionSelectionGuidePoint {
            window_start: Seconds(22_150.0),
            window_end: Seconds(22_660.416),
        };
        let realized = vec![
            BroadRealizedFuelExhaustionPersistentTwistEpoch {
                observation_index: 0,
                observation_id: "activation".to_string(),
                observation_kind: "satcom",
                observation_time_s: 1.0,
                after_fuel_anchor: true,
                step: PersistentTwistStep::Activate { point },
            },
            BroadRealizedFuelExhaustionPersistentTwistEpoch {
                observation_index: 1,
                observation_id: "m0011".to_string(),
                observation_kind: "satcom",
                observation_time_s: 2.0,
                after_fuel_anchor: true,
                step: PersistentTwistStep::Finalize { point },
            },
        ];
        let log_weights = vec![0.4_f64.ln(), 0.6_f64.ln()];
        let result = FilterResult {
            particles: vec![(), ()],
            log_weights: log_weights.clone(),
            root_ids: vec![0, 1],
            snapshots: vec![FilterSnapshot {
                observation_index: Some(1),
                observation_time_s: 2.0,
                particles: vec![(), ()],
                log_weights: log_weights.clone(),
                root_ids: vec![0, 1],
                stratum_ids: vec![StratumId(0), StratumId(0)],
            }],
            ancestry: Vec::new(),
            checkpoints: vec![
                synthetic_filter_checkpoint(0, 1.0, 0.4, 0.4),
                synthetic_filter_checkpoint(1, 2.0, -0.3, 0.1),
            ],
            log_evidence: 0.1,
            initial_log_evidence: 0.0,
            initial_strata: Vec::new(),
        };
        let diagnostics = BroadPersistentTwistExecutionDiagnostics {
            checkpoints: vec![
                PersistentTwistCheckpoint {
                    observation_index: 0,
                    observation_time_s: 1.0,
                    phase: PersistentTwistPhase::Activate,
                    output_is_twisted: true,
                    twisted_target_log_evidence_increment: 0.4,
                    final_untwist_log_evidence_correction: None,
                    filter_checkpoint_log_evidence_increment: 0.4,
                    population: synthetic_twist_population(2),
                },
                PersistentTwistCheckpoint {
                    observation_index: 1,
                    observation_time_s: 2.0,
                    phase: PersistentTwistPhase::Finalize,
                    output_is_twisted: false,
                    twisted_target_log_evidence_increment: -0.1,
                    final_untwist_log_evidence_correction: Some(-0.2),
                    filter_checkpoint_log_evidence_increment: -0.3,
                    population: synthetic_twist_population(2),
                },
            ],
            twisted_standard_checkpoints: vec![
                synthetic_pool_checkpoint(0, 1.0, 0.4),
                synthetic_pool_checkpoint(1, 2.0, -0.1),
            ],
            intermediate_potential_checkpoints: Vec::new(),
            twisted_filtering_observation_indices: vec![0],
        };
        (realized, result, diagnostics)
    }

    #[test]
    fn persistent_twist_outer_and_nested_pool_evidence_recompose_to_final_physical_output() {
        let (realized, result, diagnostics) = synthetic_persistent_diagnostics();
        let recomposition =
            validate_persistent_twist_diagnostics(&realized, None, &result, &diagnostics).unwrap();
        assert!(
            (recomposition.active_twisted_target_log_evidence_increment_sum - 0.3).abs() < 1.0e-12
        );
        assert!((recomposition.final_global_untwist_log_evidence_correction + 0.2).abs() < 1.0e-12);
        assert!((recomposition.recomposed_final_physical_log_evidence - 0.1).abs() < 1.0e-12);
        assert_eq!(
            result.snapshots.last().unwrap().log_weights,
            result.log_weights
        );
        assert_eq!(
            diagnostics.twisted_standard_checkpoints[1].realized_log_evidence_increment,
            diagnostics.checkpoints[1].twisted_target_log_evidence_increment
        );
        assert_eq!(
            diagnostics.checkpoints[1].filter_checkpoint_log_evidence_increment,
            result.checkpoints[1].log_evidence_increment
        );

        let mut inconsistent = diagnostics.clone();
        inconsistent.checkpoints[1].filter_checkpoint_log_evidence_increment += 0.01;
        assert!(
            validate_persistent_twist_diagnostics(&realized, None, &result, &inconsistent)
                .unwrap_err()
                .to_string()
                .contains("physical ledger")
        );
    }

    #[test]
    fn final_bridge_aggregate_applies_outer_untwist_but_nested_candidate_pool_stays_twisted() {
        let (_, result, _) = synthetic_persistent_diagnostics();
        let point = BroadSatcomIntermediatePotentialPoint {
            interval_start: Seconds(1.0),
            time: Seconds(1.5),
            kind: mh370_estimator::BroadSatcomIntermediatePotentialPointKind::EarlyBtoOnly,
        };
        let realized = vec![BroadRealizedIntermediatePotentialEpoch {
            observation_index: 1,
            observation_id: "m0011".to_string(),
            observation_kind: "satcom",
            observation_time_s: 2.0,
            elapsed_seconds: 1.0,
            step: IntermediatePotentialStep::Bridge {
                points: vec![IntermediatePotentialBridgePoint {
                    point,
                    candidates_per_particle: 2,
                }],
            },
        }];
        let mut point_pool = synthetic_pool_checkpoint(1, 1.5, 0.2);
        point_pool.candidates_per_particle = 2;
        point_pool.configured_candidates = 4;
        point_pool.generated_candidates = 4;
        point_pool.positive_candidates = 4;
        let endpoint_pool = synthetic_pool_checkpoint(1, 2.0, -0.3);
        let ess = result.checkpoints[1].posterior_ess;
        let checkpoint = IntermediatePotentialCheckpoint {
            observation_index: 1,
            observation_time_s: 2.0,
            points: vec![IntermediatePotentialPointCheckpoint {
                point_index: 0,
                point_time_s: 1.5,
                elapsed_seconds: 0.5,
                candidate_pool: point_pool,
                output_positive_particles: 2,
                output_effective_sample_size: 2.0,
                output_maximum_particle_weight: 0.5,
                output_distinct_positive_roots: 2,
                output_root_effective_sample_size: 2.0,
                output_maximum_root_weight: 0.5,
                output_strata: Vec::new(),
            }],
            endpoint: IntermediatePotentialEndpointCheckpoint {
                elapsed_seconds: 0.5,
                positive_particles: 2,
                log_evidence_increment: -0.5,
                posterior_effective_sample_size: ess,
                maximum_particle_weight: 0.6,
                distinct_positive_roots: 2,
                root_effective_sample_size: ess,
                maximum_root_weight: 0.6,
                strata: Vec::new(),
                candidate_pool: Some(endpoint_pool),
            },
            realized_log_evidence_increment: -0.3,
        };
        validate_intermediate_potential_diagnostics(
            &realized,
            &result,
            &[checkpoint],
            &[1],
            &BTreeMap::from([(1, -0.2)]),
        )
        .unwrap();
    }

    #[test]
    fn persistent_twist_diagnostics_contract_records_no_evidence_leak_and_placeholders() {
        let suite: BroadSuiteConfig =
            toml::from_str(&persistent_twist_config_text(Some(0.02))).unwrap();
        let config = suite.fuel_exhaustion_persistent_twist.as_ref().unwrap();
        let window = resolve_fuel_exhaustion_guide_window(
            config,
            include_bytes!("../../../inputs/accident/satcom-observations.csv"),
        )
        .unwrap();
        let (realized, result, diagnostics) = synthetic_persistent_diagnostics();
        let recomposition =
            validate_persistent_twist_diagnostics(&realized, None, &result, &diagnostics).unwrap();
        let mut posterior = synthetic_fuel_selection_population(370023, 0.25, 3).summary;
        posterior.retained_slots = 12;
        posterior.positive_weight_slots = 10;
        posterior.zero_weight_placeholder_slots = 2;
        let input_sha256 = BTreeMap::from([(
            "fuel_guide_canonical_satcom_observations".to_string(),
            "a".repeat(64),
        )]);
        let guide = BroadFuelExhaustionSelectionGuide::new(config.resolved()).unwrap();
        let value = serde_json::to_value(BroadFuelExhaustionPersistentTwistDiagnosticsArtifact {
            schema: "mh370-broad-fuel-exhaustion-persistent-twist-diagnostics-v1",
            schema_version: 1,
            model_family: mh370_estimator::BROAD_FLIGHT_MODEL_FAMILY,
            twist_family: BROAD_FUEL_EXHAUSTION_PERSISTENT_TWIST_FAMILY,
            family: "bto-bfo",
            seed: 370023,
            run_identity_sha256: &"b".repeat(64),
            config_sha256: &"c".repeat(64),
            input_sha256: &input_sha256,
            filter: &suite.filter,
            resampling_policy: suite.resampling_policy,
            config,
            resolved_estimator_config: config.resolved(),
            twist_descriptor: guide.persistent_twist_stable_descriptor(),
            resolved_window: window,
            realized_epochs: &realized,
            proposal_semantics: "proposal_only",
            evidence_semantics:
                "computational_proposal_only_no_fuel_logon_or_satcom_likelihood_and_no_change_to_the_bto_bfo_evidence_ledger",
            finalization_semantics: "final_weights_are_untwisted_physical_filter_weights",
            terminal_semantics: "terminal_must_not_correct_H_again",
            canonical_source_semantics: "time_only_not_consumed_or_scored",
            wrapper_checkpoints: &diagnostics.checkpoints,
            twisted_standard_checkpoints: &diagnostics.twisted_standard_checkpoints,
            intermediate_potential_checkpoints: &[],
            nested_checkpoint_semantics: "pre_untwist",
            twisted_filtering_observation_indices: &diagnostics
                .twisted_filtering_observation_indices,
            evidence_recomposition: &recomposition,
            final_posterior: &posterior,
        })
        .unwrap();
        assert_eq!(
            value["schema"],
            "mh370-broad-fuel-exhaustion-persistent-twist-diagnostics-v1"
        );
        assert_eq!(
            value["twist_family"],
            BROAD_FUEL_EXHAUSTION_PERSISTENT_TWIST_FAMILY
        );
        assert!(value["twist_descriptor"]
            .as_str()
            .unwrap()
            .contains("scientific-evidence=none"));
        assert!(value["evidence_semantics"]
            .as_str()
            .unwrap()
            .contains("no_fuel_logon_or_satcom_likelihood"));
        assert_eq!(value["final_posterior"]["zero_weight_placeholder_slots"], 2);
        assert_eq!(
            value["evidence_recomposition"]["reported_final_physical_log_evidence"],
            0.1
        );
    }
}
