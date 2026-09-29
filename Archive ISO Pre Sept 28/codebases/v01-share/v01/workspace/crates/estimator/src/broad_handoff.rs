use std::collections::{BTreeMap, BTreeSet};

use mh370_domain::{Degrees, LatLon, Seconds};
use mh370_dynamics::{PendingRenewal, PoweredFlightState, PoweredLateralMode};
use mh370_end_of_flight::PoweredFuelState;
use mh370_particle_filter::{normalize_log_weights, FilterResult, FilterSnapshot, StratumId};
use mh370_satcom::{BfoBiasState, ObservationFit};
use serde::{Deserialize, Serialize};
use thiserror::Error;

use crate::{
    BroadFlightDiagnostics, BroadFlightParticleStatus, BroadFlightScores, BroadFlightState,
    BroadFuelDiagnosticStatus, BroadPendingRenewalRefreshConfig,
    BroadSatcomEventMarkGuideDiagnostics,
};

/// Current canonical broad handoff schema. The existing type names retain
/// their historical `V1` suffix; schema changes are made in place rather than
/// by creating parallel handoff implementations.
pub const BROAD_POSTERIOR_HANDOFF_SCHEMA_VERSION: u32 = 2;
const NORMALIZATION_TOLERANCE: f64 = 1e-10;
const PENDING_RENEWAL_DUE_TOLERANCE_S: f64 = 1e-9;

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct BroadStratumMetadataV1 {
    pub id: StratumId,
    pub name: String,
    pub process_family: String,
    pub scientific_log_prior_probability: f64,
    pub allocated_particles: usize,
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct BroadRunMetadataV1 {
    pub model_family: String,
    pub seed: u64,
    pub run_identity_sha256: String,
    pub config_sha256: String,
    pub input_sha256: BTreeMap<String, String>,
    /// Absolute UTC origin for every relative `Seconds` value in this handoff.
    pub time_origin_utc: String,
    /// Upstream state/prior epoch; distinct from the posterior checkpoint.
    pub source_epoch_id: String,
    pub source_time: Seconds,
    pub source_time_utc: String,
    pub dynamics_model_family: String,
    pub fuel_model_family: String,
    /// When present, every independent terminal continuation draw must first
    /// refresh these pending auxiliary clocks from their exact conditional
    /// laws. The filtering PF schedule itself remains runner-owned.
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub pending_renewal_refresh: Option<BroadPendingRenewalRefreshConfig>,
    /// Explicit powered-flight support model. The config hash remains the
    /// authoritative parameter identity; these fields make the dominant
    /// conditional assumptions visible without reopening the TOML.
    pub powered_performance_model_family: String,
    pub powered_aerodynamic_family: String,
    pub powered_thrust_family: String,
    pub powered_thrust_multiplier: f64,
    pub powered_static_thrust_cap_per_engine_n: f64,
    pub powered_maximum_additional_drag_coefficient: f64,
    pub configured_particles: usize,
    pub strata: Vec<BroadStratumMetadataV1>,
}

impl BroadRunMetadataV1 {
    pub fn validate(&self) -> Result<(), BroadPosteriorHandoffErrorV1> {
        validate_run_metadata(self)
    }
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum BroadConditioningSemanticsV1 {
    /// Uses no observations later than `through_epoch_id`.
    Filtering { through_epoch_id: String },
    /// State is retained at the earlier filtering checkpoint but descendant
    /// weights include explicitly declared later evidence.
    Smoothed {
        filtering_checkpoint_id: String,
        conditioned_through_epoch_id: String,
    },
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct BroadCheckpointMetadataV1 {
    /// Stable artifact-local identity. A smoothed and filtering posterior at
    /// the same physical time have different checkpoint identifiers.
    pub checkpoint_id: String,
    pub state_epoch_id: String,
    pub state_time: Seconds,
    pub state_time_utc: String,
    pub conditioning: BroadConditioningSemanticsV1,
}

impl BroadCheckpointMetadataV1 {
    pub fn validate(&self) -> Result<(), BroadPosteriorHandoffErrorV1> {
        validate_checkpoint(self)
    }
}

#[derive(Debug, Clone, PartialEq, Eq, PartialOrd, Ord, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum BroadEvidenceComponentV1 {
    Bto,
    Bfo,
    FuelExhaustionWindow,
    LogonRequestTime,
    LogonOccurrence,
    ReceivedPower,
}

#[derive(Debug, Clone, PartialEq, Eq, PartialOrd, Ord, Serialize, Deserialize)]
pub struct BroadEvidenceIdentityV1 {
    pub epoch_id: String,
    pub channel: Option<String>,
    pub component: BroadEvidenceComponentV1,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum BroadEvidenceDispositionV1 {
    Consumed,
    HeldOut,
    Diagnostic,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum BroadEvidenceStateEffectV1 {
    /// An additive density ratio may reuse the propagated population, subject
    /// to adequate importance overlap.
    None,
    /// The evidence analytically changed a latent state such as BFO bias.
    AnalyticLatentUpdate,
    /// The evidence conditioned a transition/event history.
    TransitionConditioning,
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct BroadEvidenceEntryV1 {
    pub identity: BroadEvidenceIdentityV1,
    pub disposition: BroadEvidenceDispositionV1,
    pub state_effect: BroadEvidenceStateEffectV1,
}

#[derive(Debug, Clone, Default, PartialEq, Eq, Serialize, Deserialize)]
pub struct BroadEvidenceLedgerV1 {
    entries: Vec<BroadEvidenceEntryV1>,
}

#[derive(Debug, Error, Clone, PartialEq, Eq)]
pub enum BroadEvidenceLedgerErrorV1 {
    #[error("broad evidence epoch and channel identifiers must not be empty")]
    EmptyIdentity,
    #[error("broad evidence identity is recorded more than once: {0:?}")]
    DuplicateIdentity(BroadEvidenceIdentityV1),
    #[error("broad evidence has already been consumed: {0:?}")]
    DuplicateConsumption(BroadEvidenceIdentityV1),
}

impl BroadEvidenceLedgerV1 {
    pub fn new() -> Self {
        Self::default()
    }

    pub fn from_entries(
        entries: Vec<BroadEvidenceEntryV1>,
    ) -> Result<Self, BroadEvidenceLedgerErrorV1> {
        let ledger = Self { entries };
        ledger.validate()?;
        Ok(ledger)
    }

    pub fn entries(&self) -> &[BroadEvidenceEntryV1] {
        &self.entries
    }

    pub fn record(
        &mut self,
        identity: BroadEvidenceIdentityV1,
        disposition: BroadEvidenceDispositionV1,
        state_effect: BroadEvidenceStateEffectV1,
    ) -> Result<(), BroadEvidenceLedgerErrorV1> {
        validate_evidence_identity(&identity)?;
        if self.entries.iter().any(|entry| entry.identity == identity) {
            return Err(BroadEvidenceLedgerErrorV1::DuplicateIdentity(identity));
        }
        self.entries.push(BroadEvidenceEntryV1 {
            identity,
            disposition,
            state_effect,
        });
        Ok(())
    }

    pub fn consume(
        &mut self,
        identity: BroadEvidenceIdentityV1,
        state_effect: BroadEvidenceStateEffectV1,
    ) -> Result<(), BroadEvidenceLedgerErrorV1> {
        validate_evidence_identity(&identity)?;
        if let Some(entry) = self
            .entries
            .iter_mut()
            .find(|entry| entry.identity == identity)
        {
            if entry.disposition == BroadEvidenceDispositionV1::Consumed {
                return Err(BroadEvidenceLedgerErrorV1::DuplicateConsumption(identity));
            }
            entry.disposition = BroadEvidenceDispositionV1::Consumed;
            entry.state_effect = state_effect;
            return Ok(());
        }
        self.entries.push(BroadEvidenceEntryV1 {
            identity,
            disposition: BroadEvidenceDispositionV1::Consumed,
            state_effect,
        });
        Ok(())
    }

    pub fn validate(&self) -> Result<(), BroadEvidenceLedgerErrorV1> {
        let mut identities = BTreeSet::new();
        for entry in &self.entries {
            validate_evidence_identity(&entry.identity)?;
            if !identities.insert(&entry.identity) {
                return Err(BroadEvidenceLedgerErrorV1::DuplicateIdentity(
                    entry.identity.clone(),
                ));
            }
        }
        Ok(())
    }

    pub fn validate_particle_scores(
        &self,
        scores: &[BroadParticleEvidenceScoreV1],
    ) -> Result<(), BroadPosteriorHandoffErrorV1> {
        validate_particle_evidence_scores(scores, self)
    }
}

fn validate_evidence_identity(
    identity: &BroadEvidenceIdentityV1,
) -> Result<(), BroadEvidenceLedgerErrorV1> {
    if identity.epoch_id.trim().is_empty()
        || identity
            .channel
            .as_ref()
            .is_some_and(|channel| channel.trim().is_empty())
    {
        return Err(BroadEvidenceLedgerErrorV1::EmptyIdentity);
    }
    Ok(())
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct BroadParticleEvidenceScoreV1 {
    pub identity: BroadEvidenceIdentityV1,
    pub log_likelihood: f64,
}

/// Aggregate SATCOM identities used by the canonical broad schema. The counts make it
/// impossible to label a partial component history as "through checkpoint".
#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct BroadAggregateEvidenceV1 {
    pub bto_through_checkpoint: BroadEvidenceIdentityV1,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub bfo_through_checkpoint: Option<BroadEvidenceIdentityV1>,
    pub bto_observation_count: u32,
    pub bfo_observation_count: u32,
}

#[derive(Debug, Clone, PartialEq, Eq, PartialOrd, Ord, Serialize, Deserialize)]
pub struct BroadPosteriorParticleIdentityV1 {
    pub model_family: String,
    pub seed: u64,
    pub checkpoint_id: String,
    pub particle: usize,
}

#[derive(Debug, Clone, PartialEq, Eq, PartialOrd, Ord, Serialize, Deserialize)]
pub struct BroadPriorRootIdentityV1 {
    pub model_family: String,
    pub seed: u64,
    pub source_epoch_id: String,
    pub stratum: StratumId,
    pub initial_particle: usize,
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct BroadPosteriorHandoffParticleV1 {
    pub identity: BroadPosteriorParticleIdentityV1,
    pub prior_root: BroadPriorRootIdentityV1,
    /// For a smoothed export, identifies the filtering particle whose state is
    /// retained while later descendant weights are aggregated onto it.
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub parent_particle: Option<BroadPosteriorParticleIdentityV1>,
    /// One for a filtering export. For a smoothed export, the number of final
    /// particle slots whose weights were aggregated onto this retained state.
    #[serde(default = "one_descendant")]
    pub descendant_count: usize,
    pub stratum: StratumId,
    pub normalized_log_weight: f64,
    pub source_log_likelihood: f64,
    pub cumulative_log_prior_over_proposal: f64,
    /// Physical flight state plus pending manoeuvre clocks. Pending clocks are
    /// disposable auxiliary future randomness, not inferred manoeuvre intent.
    /// If `run.pending_renewal_refresh` is present, a terminal sampler must
    /// independently refresh its configured clocks for every continuation
    /// draw before propagation.
    pub powered_flight: PoweredFlightState,
    /// Correlated mass/feed state remains explicitly outside AircraftState.
    pub fuel: PoweredFuelState,
    /// Particle-correlated latent; never reconstruct this as a fixed default.
    pub fuel_flow_scale: f64,
    pub fuel_quantity_offset_kg: f64,
    pub bfo_bias: BfoBiasState,
    pub status: BroadFlightParticleStatus,
    pub fuel_status: BroadFuelDiagnosticStatus,
    pub scores: BroadFlightScores,
    pub last_fit: Option<ObservationFit>,
    pub diagnostics: BroadFlightDiagnostics,
    pub evidence_scores: Vec<BroadParticleEvidenceScoreV1>,
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct BroadPosteriorHandoffV1 {
    pub schema_version: u32,
    pub run: BroadRunMetadataV1,
    pub checkpoint: BroadCheckpointMetadataV1,
    pub evidence: BroadEvidenceLedgerV1,
    pub particles: Vec<BroadPosteriorHandoffParticleV1>,
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct BroadPosteriorReportRowV1 {
    pub checkpoint_id: String,
    pub model_family: String,
    pub seed: u64,
    pub particle: usize,
    pub prior_root: usize,
    pub stratum: StratumId,
    pub normalized_weight: f64,
    pub latitude_deg: f64,
    pub longitude_deg: f64,
    pub pressure_altitude_ft: f64,
    pub track_true_deg: f64,
    pub heading_true_deg: f64,
    pub ground_speed_kt: f64,
    pub vertical_speed_ft_min: f64,
    pub mach: f64,
    pub bank_deg: f64,
    pub lateral_mode: PoweredLateralMode,
    pub target_mach: f64,
    pub target_pressure_altitude_ft: f64,
    pub lateral_events: u32,
    pub speed_events: u32,
    pub altitude_events: u32,
    pub gross_mass_kg: f64,
    pub left_usable_fuel_kg: f64,
    pub right_usable_fuel_kg: f64,
    pub dual_engine_exhaustion_time_s: Option<f64>,
    pub fuel_flow_scale: f64,
    pub fuel_quantity_offset_kg: f64,
    pub bfo_bias_mean_hz: f64,
    pub bfo_bias_variance_hz2: f64,
}

impl BroadPosteriorParticleIdentityV1 {
    pub fn validate_for(
        &self,
        run: &BroadRunMetadataV1,
        checkpoint: &BroadCheckpointMetadataV1,
    ) -> Result<(), BroadPosteriorHandoffErrorV1> {
        validate_particle_identity(self, run, checkpoint)
    }
}

impl BroadPriorRootIdentityV1 {
    pub fn validate_for(
        &self,
        run: &BroadRunMetadataV1,
    ) -> Result<(), BroadPosteriorHandoffErrorV1> {
        validate_prior_root_identity(self, run)
    }
}

impl BroadPosteriorHandoffParticleV1 {
    /// Reconstruct the exact marked-jump filtering state without replacing
    /// particle-correlated fuel latents or diagnostic/status history.
    pub fn to_broad_flight_state(&self) -> BroadFlightState {
        BroadFlightState {
            stratum: self.stratum,
            powered_flight: self.powered_flight,
            fuel: self.fuel,
            fuel_flow_scale: self.fuel_flow_scale,
            fuel_quantity_offset_kg: self.fuel_quantity_offset_kg,
            bfo_bias: self.bfo_bias,
            status: self.status,
            fuel_status: self.fuel_status,
            scores: self.scores,
            last_fit: self.last_fit,
            diagnostics: self.diagnostics,
        }
    }
}

#[derive(Debug, Error, Clone, PartialEq)]
pub enum BroadPosteriorHandoffErrorV1 {
    #[error("unsupported broad posterior handoff schema version {0}")]
    UnsupportedSchema(u32),
    #[error("broad posterior handoff metadata is incomplete")]
    IncompleteMetadata,
    #[error("broad posterior handoff SHA-256 identity is invalid: {0}")]
    InvalidSha256(String),
    #[error("broad posterior stratum metadata is invalid")]
    InvalidStrata,
    #[error("broad posterior handoff contains no particles")]
    NoParticles,
    #[error("broad posterior checkpoint precedes its declared source epoch")]
    InvalidCheckpointTime,
    #[error("broad posterior particle identity is duplicated: {0:?}")]
    DuplicateParticle(BroadPosteriorParticleIdentityV1),
    #[error("broad posterior particle identity does not match its run/checkpoint")]
    ParticleIdentityMismatch,
    #[error("broad posterior particle references an unknown stratum")]
    UnknownStratum,
    #[error("broad posterior particle state or weight is invalid")]
    InvalidParticle,
    #[error("broad posterior pending-renewal refresh metadata or state is invalid")]
    InvalidPendingRenewalRefresh,
    #[error("broad posterior log weights are not normalized; logsumexp={0}")]
    UnnormalizedLogWeights(f64),
    #[error("broad posterior per-particle evidence scores are incomplete, duplicated, or invalid")]
    InvalidEvidenceScores,
    #[error("broad posterior source log likelihood disagrees with its evidence scores")]
    EvidenceScoreSumMismatch,
    #[error("aircraft BFO bias and full BFO-bias state disagree")]
    BfoBiasMeanMismatch,
    #[error(transparent)]
    Evidence(#[from] BroadEvidenceLedgerErrorV1),
}

#[derive(Debug, Error)]
pub enum BroadHandoffBuildErrorV1 {
    #[error("filter snapshot shape or ancestry is invalid")]
    InvalidSnapshot,
    #[error("snapshot time does not match the handoff checkpoint")]
    CheckpointMismatch,
    #[error("filtering/smoothed checkpoint semantics do not match the requested export")]
    ConditioningMismatch,
    #[error("aggregate BTO/BFO identities, counts, or ledger dispositions are inconsistent")]
    AggregateEvidenceMismatch,
    #[error("no finite-weight particle remains for handoff")]
    NoFiniteWeight,
    #[error(transparent)]
    Handoff(#[from] BroadPosteriorHandoffErrorV1),
}

const fn one_descendant() -> usize {
    1
}

/// Build a filtering handoff from a retained or final broad-flight snapshot.
/// Zero-mass (`-inf`) slots are omitted; finite normalized weights and original
/// root/stratum identities are otherwise preserved.
pub fn build_broad_filtering_handoff_v1(
    snapshot: &FilterSnapshot<BroadFlightState>,
    run: BroadRunMetadataV1,
    checkpoint: BroadCheckpointMetadataV1,
    evidence: BroadEvidenceLedgerV1,
    aggregate: BroadAggregateEvidenceV1,
) -> Result<BroadPosteriorHandoffV1, BroadHandoffBuildErrorV1> {
    if !matches!(
        checkpoint.conditioning,
        BroadConditioningSemanticsV1::Filtering { .. }
    ) {
        return Err(BroadHandoffBuildErrorV1::ConditioningMismatch);
    }
    let descendant_counts = vec![1; snapshot.particles.len()];
    build_broad_handoff_from_snapshot(
        snapshot,
        &snapshot.log_weights,
        &descendant_counts,
        None,
        run,
        checkpoint,
        evidence,
        aggregate,
    )
}

/// Aggregate later descendant weights onto an earlier retained state and emit
/// a smoothed handoff. `parent_particle` points to the corresponding filtering
/// checkpoint slot; `descendant_count` records the exact many-to-one collapse.
#[allow(clippy::too_many_arguments)]
pub fn build_broad_smoothed_handoff_v1(
    filter: &FilterResult<BroadFlightState>,
    snapshot_position: usize,
    descendant_log_weights: &[f64],
    run: BroadRunMetadataV1,
    checkpoint: BroadCheckpointMetadataV1,
    evidence: BroadEvidenceLedgerV1,
    aggregate: BroadAggregateEvidenceV1,
) -> Result<BroadPosteriorHandoffV1, BroadHandoffBuildErrorV1> {
    let filtering_checkpoint_id = match &checkpoint.conditioning {
        BroadConditioningSemanticsV1::Smoothed {
            filtering_checkpoint_id,
            ..
        } => filtering_checkpoint_id.clone(),
        BroadConditioningSemanticsV1::Filtering { .. } => {
            return Err(BroadHandoffBuildErrorV1::ConditioningMismatch);
        }
    };
    if snapshot_position + 1 >= filter.snapshots.len() {
        return Err(BroadHandoffBuildErrorV1::InvalidSnapshot);
    }
    let smoothed = filter
        .aggregate_descendant_weights_at_snapshot(snapshot_position, descendant_log_weights)
        .map_err(|_| BroadHandoffBuildErrorV1::InvalidSnapshot)?;
    let snapshot = filter
        .snapshots
        .get(snapshot_position)
        .ok_or(BroadHandoffBuildErrorV1::InvalidSnapshot)?;
    build_broad_handoff_from_snapshot(
        snapshot,
        &smoothed.normalized_log_weights,
        &smoothed.descendant_counts,
        Some(filtering_checkpoint_id),
        run,
        checkpoint,
        evidence,
        aggregate,
    )
}

#[allow(clippy::too_many_arguments)]
fn build_broad_handoff_from_snapshot(
    snapshot: &FilterSnapshot<BroadFlightState>,
    log_weights: &[f64],
    descendant_counts: &[usize],
    filtering_checkpoint_id: Option<String>,
    run: BroadRunMetadataV1,
    checkpoint: BroadCheckpointMetadataV1,
    evidence: BroadEvidenceLedgerV1,
    aggregate: BroadAggregateEvidenceV1,
) -> Result<BroadPosteriorHandoffV1, BroadHandoffBuildErrorV1> {
    run.validate()?;
    checkpoint.validate()?;
    evidence
        .validate()
        .map_err(BroadPosteriorHandoffErrorV1::from)?;
    validate_aggregate_evidence(&evidence, &aggregate)?;
    if (snapshot.observation_time_s - checkpoint.state_time.0).abs() > 1.0e-8 {
        return Err(BroadHandoffBuildErrorV1::CheckpointMismatch);
    }
    let count = snapshot.particles.len();
    if count == 0
        || snapshot.log_weights.len() != count
        || log_weights.len() != count
        || snapshot.root_ids.len() != count
        || snapshot.stratum_ids.len() != count
        || descendant_counts.len() != count
        || log_weights
            .iter()
            .any(|weight| !weight.is_finite() && *weight != f64::NEG_INFINITY)
    {
        return Err(BroadHandoffBuildErrorV1::InvalidSnapshot);
    }
    let retained = log_weights
        .iter()
        .enumerate()
        .filter_map(|(index, &weight)| weight.is_finite().then_some((index, weight)))
        .collect::<Vec<_>>();
    if retained.is_empty() {
        return Err(BroadHandoffBuildErrorV1::NoFiniteWeight);
    }
    let retained_weights = retained
        .iter()
        .map(|(_, weight)| *weight)
        .collect::<Vec<_>>();
    let (normalized, _) = normalize_log_weights(&retained_weights)
        .map_err(|_| BroadHandoffBuildErrorV1::NoFiniteWeight)?;
    let mut particles = Vec::with_capacity(retained.len());
    for ((slot, _), normalized_log_weight) in retained.into_iter().zip(normalized) {
        let state = snapshot.particles[slot];
        if state.stratum != snapshot.stratum_ids[slot]
            || state.scores.bto_observations != aggregate.bto_observation_count
            || state.scores.bfo_observations != aggregate.bfo_observation_count
            || (aggregate.bfo_through_checkpoint.is_none()
                && state.scores.cumulative_bfo_log_likelihood != 0.0)
            || descendant_counts[slot] == 0
        {
            return Err(BroadHandoffBuildErrorV1::AggregateEvidenceMismatch);
        }
        let identity = BroadPosteriorParticleIdentityV1 {
            model_family: run.model_family.clone(),
            seed: run.seed,
            checkpoint_id: checkpoint.checkpoint_id.clone(),
            particle: slot,
        };
        let parent_particle = filtering_checkpoint_id.as_ref().map(|checkpoint_id| {
            BroadPosteriorParticleIdentityV1 {
                model_family: run.model_family.clone(),
                seed: run.seed,
                checkpoint_id: checkpoint_id.clone(),
                particle: slot,
            }
        });
        let bto = state.scores.cumulative_bto_log_likelihood;
        let bfo = state.scores.cumulative_bfo_log_likelihood;
        let mut evidence_scores = vec![BroadParticleEvidenceScoreV1 {
            identity: aggregate.bto_through_checkpoint.clone(),
            log_likelihood: bto,
        }];
        if let Some(identity) = &aggregate.bfo_through_checkpoint {
            evidence_scores.push(BroadParticleEvidenceScoreV1 {
                identity: identity.clone(),
                log_likelihood: bfo,
            });
        }
        particles.push(BroadPosteriorHandoffParticleV1 {
            identity,
            prior_root: BroadPriorRootIdentityV1 {
                model_family: run.model_family.clone(),
                seed: run.seed,
                source_epoch_id: run.source_epoch_id.clone(),
                stratum: state.stratum,
                initial_particle: snapshot.root_ids[slot],
            },
            parent_particle,
            descendant_count: descendant_counts[slot],
            stratum: state.stratum,
            normalized_log_weight,
            source_log_likelihood: bto + bfo,
            cumulative_log_prior_over_proposal: state
                .diagnostics
                .satcom_event_mark_guide
                .cumulative_log_prior_over_proposal,
            powered_flight: state.powered_flight,
            fuel: state.fuel,
            fuel_flow_scale: state.fuel_flow_scale,
            fuel_quantity_offset_kg: state.fuel_quantity_offset_kg,
            bfo_bias: state.bfo_bias,
            status: state.status,
            fuel_status: state.fuel_status,
            scores: state.scores,
            last_fit: state.last_fit,
            diagnostics: state.diagnostics,
            evidence_scores,
        });
    }
    let handoff = BroadPosteriorHandoffV1 {
        schema_version: BROAD_POSTERIOR_HANDOFF_SCHEMA_VERSION,
        run,
        checkpoint,
        evidence,
        particles,
    };
    handoff.validate()?;
    Ok(handoff)
}

fn validate_aggregate_evidence(
    ledger: &BroadEvidenceLedgerV1,
    aggregate: &BroadAggregateEvidenceV1,
) -> Result<(), BroadHandoffBuildErrorV1> {
    let bfo_shape_valid = match &aggregate.bfo_through_checkpoint {
        Some(bfo) => {
            bfo.component == BroadEvidenceComponentV1::Bfo
                && *bfo != aggregate.bto_through_checkpoint
                && aggregate.bfo_observation_count > 0
        }
        None => aggregate.bfo_observation_count == 0,
    };
    if aggregate.bto_through_checkpoint.component != BroadEvidenceComponentV1::Bto
        || aggregate.bto_observation_count == 0
        || !bfo_shape_valid
    {
        return Err(BroadHandoffBuildErrorV1::AggregateEvidenceMismatch);
    }
    let consumed = ledger
        .entries()
        .iter()
        .filter(|entry| entry.disposition == BroadEvidenceDispositionV1::Consumed)
        .collect::<Vec<_>>();
    let bto = consumed
        .iter()
        .find(|entry| entry.identity == aggregate.bto_through_checkpoint);
    let bfo = aggregate
        .bfo_through_checkpoint
        .as_ref()
        .and_then(|identity| {
            consumed
                .iter()
                .find(|entry| entry.identity == *identity)
                .copied()
        });
    let expected_consumed = 1 + usize::from(aggregate.bfo_through_checkpoint.is_some());
    if consumed.len() != expected_consumed
        || bto.map_or(true, |entry| {
            entry.state_effect != BroadEvidenceStateEffectV1::None
        })
        || aggregate.bfo_through_checkpoint.as_ref().is_some_and(|_| {
            bfo.map_or(true, |entry| {
                entry.state_effect != BroadEvidenceStateEffectV1::AnalyticLatentUpdate
            })
        })
    {
        return Err(BroadHandoffBuildErrorV1::AggregateEvidenceMismatch);
    }
    Ok(())
}

impl BroadPosteriorHandoffV1 {
    pub fn validate(&self) -> Result<(), BroadPosteriorHandoffErrorV1> {
        if self.schema_version != BROAD_POSTERIOR_HANDOFF_SCHEMA_VERSION {
            return Err(BroadPosteriorHandoffErrorV1::UnsupportedSchema(
                self.schema_version,
            ));
        }
        self.run.validate()?;
        self.checkpoint.validate()?;
        self.evidence.validate()?;
        if self.checkpoint.state_time.0 < self.run.source_time.0 {
            return Err(BroadPosteriorHandoffErrorV1::InvalidCheckpointTime);
        }
        if self.particles.is_empty() {
            return Err(BroadPosteriorHandoffErrorV1::NoParticles);
        }
        let known_strata = self
            .run
            .strata
            .iter()
            .map(|stratum| stratum.id)
            .collect::<BTreeSet<_>>();
        let mut identities = BTreeSet::new();
        for particle in &self.particles {
            particle
                .identity
                .validate_for(&self.run, &self.checkpoint)?;
            particle.prior_root.validate_for(&self.run)?;
            if !identities.insert(&particle.identity) {
                return Err(BroadPosteriorHandoffErrorV1::DuplicateParticle(
                    particle.identity.clone(),
                ));
            }
            if particle.identity.particle >= self.run.configured_particles
                || particle.prior_root.initial_particle >= self.run.configured_particles
                || particle.stratum != particle.prior_root.stratum
                || !known_strata.contains(&particle.stratum)
            {
                return Err(BroadPosteriorHandoffErrorV1::UnknownStratum);
            }
            if let Some(parent) = &particle.parent_particle {
                if parent.model_family != self.run.model_family
                    || parent.seed != self.run.seed
                    || parent.checkpoint_id.trim().is_empty()
                {
                    return Err(BroadPosteriorHandoffErrorV1::ParticleIdentityMismatch);
                }
            }
            if !particle.normalized_log_weight.is_finite()
                || !particle.source_log_likelihood.is_finite()
                || !particle.cumulative_log_prior_over_proposal.is_finite()
                || particle.descendant_count == 0
                || !valid_powered_state(particle.powered_flight)
                || !valid_fuel_state(particle.fuel)
                || !particle.fuel_flow_scale.is_finite()
                || particle.fuel_flow_scale <= 0.0
                || !particle.fuel_quantity_offset_kg.is_finite()
                || !valid_particle_status(particle.status, particle.powered_flight.aircraft.time)
                || !valid_fuel_status(particle.fuel_status, particle.fuel.time)
                || !valid_flight_scores(particle.scores)
                || !particle.last_fit.map_or(true, valid_observation_fit)
                || !valid_flight_diagnostics(particle.diagnostics)
                || particle.cumulative_log_prior_over_proposal
                    != particle
                        .diagnostics
                        .satcom_event_mark_guide
                        .cumulative_log_prior_over_proposal
                || (particle.powered_flight.aircraft.time.0 - self.checkpoint.state_time.0).abs()
                    > 1e-8
                || (particle.fuel.time.0 - self.checkpoint.state_time.0).abs() > 1e-8
                || !particle.bfo_bias.mean_hz.is_finite()
                || !particle.bfo_bias.variance_hz2.is_finite()
                || particle.bfo_bias.variance_hz2 < 0.0
            {
                return Err(BroadPosteriorHandoffErrorV1::InvalidParticle);
            }
            if !valid_pending_renewal_refresh_pairing(
                particle.powered_flight,
                particle.diagnostics,
                self.run.pending_renewal_refresh,
            ) {
                return Err(BroadPosteriorHandoffErrorV1::InvalidPendingRenewalRefresh);
            }
            if particle.powered_flight.aircraft.bfo_bias.0 != particle.bfo_bias.mean_hz {
                return Err(BroadPosteriorHandoffErrorV1::BfoBiasMeanMismatch);
            }
            self.evidence
                .validate_particle_scores(&particle.evidence_scores)?;
            let evidence_sum = particle
                .evidence_scores
                .iter()
                .map(|score| score.log_likelihood)
                .sum::<f64>();
            let tolerance = 1e-9 * (1.0 + particle.source_log_likelihood.abs());
            let state_score = particle.scores.cumulative_bto_log_likelihood
                + particle.scores.cumulative_bfo_log_likelihood;
            if (evidence_sum - particle.source_log_likelihood).abs() > tolerance
                || (state_score - particle.source_log_likelihood).abs() > tolerance
            {
                return Err(BroadPosteriorHandoffErrorV1::EvidenceScoreSumMismatch);
            }
        }
        let maximum = self
            .particles
            .iter()
            .map(|particle| particle.normalized_log_weight)
            .fold(f64::NEG_INFINITY, f64::max);
        let log_sum = maximum
            + self
                .particles
                .iter()
                .map(|particle| (particle.normalized_log_weight - maximum).exp())
                .sum::<f64>()
                .ln();
        if !log_sum.is_finite() || log_sum.abs() > NORMALIZATION_TOLERANCE {
            return Err(BroadPosteriorHandoffErrorV1::UnnormalizedLogWeights(
                log_sum,
            ));
        }
        Ok(())
    }

    pub fn report_rows(&self) -> Vec<BroadPosteriorReportRowV1> {
        self.particles
            .iter()
            .map(|particle| {
                let flight = particle.powered_flight;
                BroadPosteriorReportRowV1 {
                    checkpoint_id: self.checkpoint.checkpoint_id.clone(),
                    model_family: self.run.model_family.clone(),
                    seed: self.run.seed,
                    particle: particle.identity.particle,
                    prior_root: particle.prior_root.initial_particle,
                    stratum: particle.stratum,
                    normalized_weight: particle.normalized_log_weight.exp(),
                    latitude_deg: flight.aircraft.position.latitude.0,
                    longitude_deg: flight.aircraft.position.longitude.0,
                    pressure_altitude_ft: flight.aircraft.altitude.0,
                    track_true_deg: flight.aircraft.track_true.0,
                    heading_true_deg: flight.heading_true.0,
                    ground_speed_kt: flight.aircraft.ground_speed.0,
                    vertical_speed_ft_min: flight.aircraft.vertical_speed.0,
                    mach: flight.mach,
                    bank_deg: flight.bank_angle.0,
                    lateral_mode: flight.command.lateral_mode,
                    target_mach: flight.command.target_mach,
                    target_pressure_altitude_ft: flight.command.target_pressure_altitude.0,
                    lateral_events: flight.event_counters.lateral,
                    speed_events: flight.event_counters.speed,
                    altitude_events: flight.event_counters.altitude,
                    gross_mass_kg: particle.fuel.gross_mass().0,
                    left_usable_fuel_kg: particle.fuel.left_usable_feed.0,
                    right_usable_fuel_kg: particle.fuel.right_usable_feed.0,
                    dual_engine_exhaustion_time_s: particle
                        .fuel
                        .dual_engine_exhaustion_time
                        .map(|time| time.0),
                    fuel_flow_scale: particle.fuel_flow_scale,
                    fuel_quantity_offset_kg: particle.fuel_quantity_offset_kg,
                    bfo_bias_mean_hz: particle.bfo_bias.mean_hz,
                    bfo_bias_variance_hz2: particle.bfo_bias.variance_hz2,
                }
            })
            .collect()
    }
}

fn validate_particle_identity(
    identity: &BroadPosteriorParticleIdentityV1,
    run: &BroadRunMetadataV1,
    checkpoint: &BroadCheckpointMetadataV1,
) -> Result<(), BroadPosteriorHandoffErrorV1> {
    if identity.model_family != run.model_family
        || identity.seed != run.seed
        || identity.checkpoint_id != checkpoint.checkpoint_id
    {
        return Err(BroadPosteriorHandoffErrorV1::ParticleIdentityMismatch);
    }
    Ok(())
}

fn validate_prior_root_identity(
    identity: &BroadPriorRootIdentityV1,
    run: &BroadRunMetadataV1,
) -> Result<(), BroadPosteriorHandoffErrorV1> {
    if identity.model_family != run.model_family
        || identity.seed != run.seed
        || identity.source_epoch_id != run.source_epoch_id
        || !run
            .strata
            .iter()
            .any(|stratum| stratum.id == identity.stratum)
    {
        return Err(BroadPosteriorHandoffErrorV1::ParticleIdentityMismatch);
    }
    Ok(())
}

fn validate_particle_evidence_scores(
    scores: &[BroadParticleEvidenceScoreV1],
    ledger: &BroadEvidenceLedgerV1,
) -> Result<(), BroadPosteriorHandoffErrorV1> {
    let consumed = ledger
        .entries()
        .iter()
        .filter(|entry| entry.disposition == BroadEvidenceDispositionV1::Consumed)
        .map(|entry| &entry.identity)
        .collect::<BTreeSet<_>>();
    let score_identities = scores
        .iter()
        .map(|score| &score.identity)
        .collect::<BTreeSet<_>>();
    if scores.iter().any(|score| !score.log_likelihood.is_finite())
        || score_identities.len() != scores.len()
        || score_identities != consumed
    {
        return Err(BroadPosteriorHandoffErrorV1::InvalidEvidenceScores);
    }
    Ok(())
}

fn valid_coordinate(position: LatLon) -> bool {
    position.latitude.0.is_finite()
        && (-90.0..=90.0).contains(&position.latitude.0)
        && position.longitude.0.is_finite()
        && (-180.0..180.0).contains(&position.longitude.0)
}

fn valid_bearing(bearing: Degrees) -> bool {
    bearing.0.is_finite() && (0.0..360.0).contains(&bearing.0)
}

fn valid_particle_status(status: BroadFlightParticleStatus, state_time: Seconds) -> bool {
    match status {
        BroadFlightParticleStatus::Active => true,
        BroadFlightParticleStatus::Rejected { at_time, .. } => {
            at_time.is_finite() && at_time.0 <= state_time.0 + 1.0e-8
        }
    }
}

fn valid_fuel_status(status: BroadFuelDiagnosticStatus, state_time: Seconds) -> bool {
    match status {
        BroadFuelDiagnosticStatus::Valid => true,
        BroadFuelDiagnosticStatus::OutsideModelDomain { at_time } => {
            at_time.is_finite() && at_time.0 <= state_time.0 + 1.0e-8
        }
    }
}

fn valid_flight_scores(scores: BroadFlightScores) -> bool {
    scores.cumulative_bto_log_likelihood.is_finite()
        && scores.cumulative_bfo_log_likelihood.is_finite()
}

fn valid_observation_fit(fit: ObservationFit) -> bool {
    fit.log_likelihood.is_finite()
        && [
            fit.predicted_bto_us,
            fit.bto_residual_us,
            fit.predicted_bfo_without_bias_hz,
            fit.bfo_innovation_hz,
        ]
        .into_iter()
        .flatten()
        .all(f64::is_finite)
}

fn valid_flight_diagnostics(diagnostics: BroadFlightDiagnostics) -> bool {
    let boundary = diagnostics.powered_boundary_seconds;
    let boundary_values = [
        boundary.stall_or_minimum_mach_floor,
        boundary.vmo_or_mmo_ceiling,
        boundary.bank,
        boundary.roll_rate,
        boundary.climb_rate,
        boundary.descent_rate,
        boundary.vertical_acceleration,
        boundary.lower_altitude,
        boundary.upper_altitude,
        boundary.magnetic_altitude_clamp,
    ];
    boundary_values
        .iter()
        .all(|value| value.is_finite() && *value >= 0.0)
        && diagnostics.magnetic_altitude_clamp_seconds.is_finite()
        && diagnostics.magnetic_altitude_clamp_seconds >= 0.0
        && diagnostics.fuel_outside_martin_domain_seconds.is_finite()
        && diagnostics.fuel_outside_martin_domain_seconds >= 0.0
        && diagnostics
            .last_fuel_anchor_mass_adjustment_kg
            .map_or(true, f64::is_finite)
        && valid_satcom_event_mark_guide_diagnostics(diagnostics.satcom_event_mark_guide)
}

fn valid_pending_renewal_refresh_pairing(
    state: PoweredFlightState,
    diagnostics: BroadFlightDiagnostics,
    config: Option<BroadPendingRenewalRefreshConfig>,
) -> bool {
    if !diagnostics.pending_renewal_refresh.validate() {
        return false;
    }
    let Some(config) = config else {
        return diagnostics.pending_renewal_refresh.is_empty();
    };
    if config.validate().is_err() {
        return false;
    }
    let refresh = diagnostics.pending_renewal_refresh;
    if (!config.lateral && refresh.lateral_refreshes != 0)
        || (!config.speed && refresh.speed_refreshes != 0)
        || (!config.altitude && refresh.altitude_refreshes != 0)
    {
        return false;
    }
    let mut selected_counts = [
        config.lateral.then_some(refresh.lateral_refreshes),
        config.speed.then_some(refresh.speed_refreshes),
        config.altitude.then_some(refresh.altitude_refreshes),
    ]
    .into_iter()
    .flatten();
    let Some(selected_count) = selected_counts.next() else {
        return false;
    };
    if selected_counts.any(|count| count != selected_count) {
        return false;
    }
    let pending_is_refreshable = |pending: Option<PendingRenewal>| {
        pending.is_some_and(|pending| {
            pending.not_before.0.is_finite()
                && pending.next_event.0.is_finite()
                && pending.next_event.0 >= pending.not_before.0
                && pending.next_event.0 > state.aircraft.time.0 + PENDING_RENEWAL_DUE_TOLERANCE_S
        })
    };
    (!config.lateral || pending_is_refreshable(state.event_clocks.lateral))
        && (!config.speed || pending_is_refreshable(state.event_clocks.speed))
        && (!config.altitude || pending_is_refreshable(state.event_clocks.altitude))
}

fn valid_satcom_event_mark_guide_diagnostics(
    diagnostics: BroadSatcomEventMarkGuideDiagnostics,
) -> bool {
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
    let Some(minimum_probability) = diagnostics.minimum_selected_probability else {
        return false;
    };
    let Some(maximum_probability) = diagnostics.maximum_selected_probability else {
        return false;
    };
    let Some(minimum_event_correction) = diagnostics.minimum_event_log_prior_over_proposal else {
        return false;
    };
    let Some(maximum_event_correction) = diagnostics.maximum_event_log_prior_over_proposal else {
        return false;
    };
    let Some(minimum_lead) = diagnostics.minimum_lead_seconds else {
        return false;
    };
    let Some(maximum_lead) = diagnostics.maximum_lead_seconds else {
        return false;
    };
    let tolerance = 1.0e-10
        * (1.0
            + diagnostics
                .cumulative_log_prior_over_proposal
                .abs()
                .max(diagnostics.sum_log_candidate_count.abs())
                .max(diagnostics.sum_selected_log_probability.abs()));
    let recomposed =
        -diagnostics.sum_log_candidate_count - diagnostics.sum_selected_log_probability;
    let Some(minimum_candidate_marks) = diagnostics.guided_lateral_events.checked_mul(2) else {
        return false;
    };
    let Some(maximum_candidate_marks) = diagnostics.guided_lateral_events.checked_mul(64) else {
        return false;
    };
    diagnostics.candidate_marks >= minimum_candidate_marks
        && diagnostics.candidate_marks <= maximum_candidate_marks
        && diagnostics.sum_selection_effective_sample_size
            >= diagnostics.guided_lateral_events as f64 - tolerance
        && diagnostics.sum_selection_effective_sample_size
            <= diagnostics.candidate_marks as f64 + tolerance
        && diagnostics.sum_selection_entropy_nats >= -tolerance
        && diagnostics.sum_selection_entropy_nats <= diagnostics.sum_log_candidate_count + tolerance
        && minimum_probability > 0.0
        && maximum_probability <= 1.0
        && minimum_probability <= maximum_probability
        && minimum_event_correction <= maximum_event_correction
        && minimum_lead >= 0.0
        && minimum_lead <= maximum_lead
        && (diagnostics.cumulative_log_prior_over_proposal - recomposed).abs() <= tolerance
        && diagnostics.cumulative_log_prior_over_proposal
            >= diagnostics.sum_minimum_log_prior_over_proposal - tolerance
        && diagnostics.cumulative_log_prior_over_proposal
            <= diagnostics.sum_maximum_log_prior_over_proposal + tolerance
}

fn valid_powered_state(state: PoweredFlightState) -> bool {
    let aircraft = state.aircraft;
    let clocks = state.event_clocks;
    let clock_valid = |pending: Option<PendingRenewal>| {
        pending.map_or(true, |pending| {
            pending.not_before.0.is_finite()
                && pending.next_event.0.is_finite()
                && pending.next_event.0 >= pending.not_before.0
                && pending.next_event.0 > aircraft.time.0 + PENDING_RENEWAL_DUE_TOLERANCE_S
        })
    };
    let destination_valid = state
        .command
        .great_circle_destination
        .map_or(true, valid_coordinate);
    let destination_matches_mode = matches!(
        state.command.lateral_mode,
        PoweredLateralMode::GreatCircleTrackContinuation
    ) == state.command.great_circle_destination.is_some();
    aircraft.all_finite()
        && valid_coordinate(aircraft.position)
        && aircraft.altitude.0 >= 0.0
        && valid_bearing(aircraft.track_true)
        && aircraft.ground_speed.0 > 0.0
        && valid_bearing(state.heading_true)
        && state.mach.is_finite()
        && state.mach > 0.0
        && state.bank_angle.0.is_finite()
        && valid_bearing(state.command.selected_control)
        && destination_valid
        && destination_matches_mode
        && state.command.target_mach.is_finite()
        && state.command.target_mach > 0.0
        && state.command.target_pressure_altitude.0.is_finite()
        && state.command.target_pressure_altitude.0 >= 0.0
        && clock_valid(clocks.lateral)
        && clock_valid(clocks.speed)
        && clock_valid(clocks.altitude)
}

fn valid_fuel_state(state: PoweredFuelState) -> bool {
    let masses = [
        state.zero_fuel_weight.0,
        state.left_usable_feed.0,
        state.right_usable_feed.0,
        state.reserved_fuel.0,
        state.unusable_fuel.0,
    ];
    let exhaustion_time_valid = |time: Option<Seconds>| {
        time.map_or(true, |time| {
            time.0.is_finite() && time.0 <= state.time.0 + 1.0e-8
        })
    };
    let dual_consistent = match (
        state.left_exhaustion_time,
        state.right_exhaustion_time,
        state.dual_engine_exhaustion_time,
    ) {
        (Some(left), Some(right), Some(dual)) => (dual.0 - left.0.max(right.0)).abs() <= 1.0e-8,
        (Some(_), Some(_), None) | (_, None, Some(_)) | (None, _, Some(_)) => false,
        _ => true,
    };
    state.time.is_finite()
        && masses.iter().all(|mass| mass.is_finite())
        && state.zero_fuel_weight.0 > 0.0
        && masses[1..].iter().all(|mass| *mass >= 0.0)
        && state.gross_mass().0.is_finite()
        && exhaustion_time_valid(state.left_exhaustion_time)
        && exhaustion_time_valid(state.right_exhaustion_time)
        && exhaustion_time_valid(state.dual_engine_exhaustion_time)
        && dual_consistent
}

fn validate_run_metadata(run: &BroadRunMetadataV1) -> Result<(), BroadPosteriorHandoffErrorV1> {
    if run
        .pending_renewal_refresh
        .is_some_and(|config| config.validate().is_err())
    {
        return Err(BroadPosteriorHandoffErrorV1::InvalidPendingRenewalRefresh);
    }
    if run.model_family.trim().is_empty()
        || run.input_sha256.is_empty()
        || run
            .input_sha256
            .keys()
            .any(|identity| identity.trim().is_empty())
        || run.time_origin_utc.trim().is_empty()
        || run.source_epoch_id.trim().is_empty()
        || !run.source_time.is_finite()
        || run.source_time_utc.trim().is_empty()
        || run.dynamics_model_family.trim().is_empty()
        || run.fuel_model_family.trim().is_empty()
        || run.powered_performance_model_family.trim().is_empty()
        || run.powered_aerodynamic_family.trim().is_empty()
        || run.powered_thrust_family.trim().is_empty()
        || !run.powered_thrust_multiplier.is_finite()
        || run.powered_thrust_multiplier <= 0.0
        || !run.powered_static_thrust_cap_per_engine_n.is_finite()
        || run.powered_static_thrust_cap_per_engine_n <= 0.0
        || !run.powered_maximum_additional_drag_coefficient.is_finite()
        || run.powered_maximum_additional_drag_coefficient < 0.0
        || run.configured_particles < 2
    {
        return Err(BroadPosteriorHandoffErrorV1::IncompleteMetadata);
    }
    validate_sha256(&run.run_identity_sha256)?;
    validate_sha256(&run.config_sha256)?;
    for digest in run.input_sha256.values() {
        validate_sha256(digest)?;
    }
    let allocated_particles = run.strata.iter().try_fold(0usize, |total, stratum| {
        total.checked_add(stratum.allocated_particles)
    });
    if run.strata.is_empty()
        || run.strata.iter().any(|stratum| {
            stratum.name.trim().is_empty()
                || stratum.process_family.trim().is_empty()
                || !stratum.scientific_log_prior_probability.is_finite()
                || stratum.allocated_particles == 0
        })
        || allocated_particles != Some(run.configured_particles)
    {
        return Err(BroadPosteriorHandoffErrorV1::InvalidStrata);
    }
    let ids = run
        .strata
        .iter()
        .map(|stratum| stratum.id)
        .collect::<BTreeSet<_>>();
    let names = run
        .strata
        .iter()
        .map(|stratum| stratum.name.as_str())
        .collect::<BTreeSet<_>>();
    let maximum_log_prior = run
        .strata
        .iter()
        .map(|stratum| stratum.scientific_log_prior_probability)
        .fold(f64::NEG_INFINITY, f64::max);
    let log_prior_sum = maximum_log_prior
        + run
            .strata
            .iter()
            .map(|stratum| (stratum.scientific_log_prior_probability - maximum_log_prior).exp())
            .sum::<f64>()
            .ln();
    if ids.len() != run.strata.len()
        || names.len() != run.strata.len()
        || log_prior_sum.abs() > NORMALIZATION_TOLERANCE
    {
        return Err(BroadPosteriorHandoffErrorV1::InvalidStrata);
    }
    Ok(())
}

fn validate_checkpoint(
    checkpoint: &BroadCheckpointMetadataV1,
) -> Result<(), BroadPosteriorHandoffErrorV1> {
    let conditioning_valid = match &checkpoint.conditioning {
        BroadConditioningSemanticsV1::Filtering { through_epoch_id } => {
            !through_epoch_id.trim().is_empty()
        }
        BroadConditioningSemanticsV1::Smoothed {
            filtering_checkpoint_id,
            conditioned_through_epoch_id,
        } => {
            !filtering_checkpoint_id.trim().is_empty()
                && !conditioned_through_epoch_id.trim().is_empty()
        }
    };
    if checkpoint.checkpoint_id.trim().is_empty()
        || checkpoint.state_epoch_id.trim().is_empty()
        || !checkpoint.state_time.is_finite()
        || checkpoint.state_time_utc.trim().is_empty()
        || !conditioning_valid
    {
        return Err(BroadPosteriorHandoffErrorV1::IncompleteMetadata);
    }
    Ok(())
}

fn validate_sha256(value: &str) -> Result<(), BroadPosteriorHandoffErrorV1> {
    if value.len() != 64
        || !value
            .bytes()
            .all(|byte| byte.is_ascii_digit() || (b'a'..=b'f').contains(&byte))
    {
        return Err(BroadPosteriorHandoffErrorV1::InvalidSha256(
            value.to_string(),
        ));
    }
    Ok(())
}

#[cfg(test)]
mod tests {
    use mh370_domain::{AircraftState, Feet, FeetPerMinute, Hertz, Knots, LatLon};
    use mh370_dynamics::{PoweredEventClocks, PoweredEventCounters, PoweredFlightCommand};
    use mh370_end_of_flight::Kilograms;
    use mh370_particle_filter::{FilterAncestryStep, FilterResult, FilterSnapshot};

    use crate::{
        BroadFlightDiagnostics, BroadFlightParticleStatus, BroadFlightScores, BroadFlightState,
        BroadFuelDiagnosticStatus,
    };

    use super::*;

    fn identity(component: BroadEvidenceComponentV1) -> BroadEvidenceIdentityV1 {
        BroadEvidenceIdentityV1 {
            epoch_id: "m0011".to_string(),
            channel: Some("R1200".to_string()),
            component,
        }
    }

    fn run_metadata() -> BroadRunMetadataV1 {
        BroadRunMetadataV1 {
            model_family: "broad-marked-jump".to_string(),
            seed: 370_011,
            run_identity_sha256: "a".repeat(64),
            config_sha256: "b".repeat(64),
            input_sha256: BTreeMap::from([("satcom".to_string(), "c".repeat(64))]),
            time_origin_utc: "2014-03-08T18:02:00Z".to_string(),
            source_epoch_id: "radar-prior".to_string(),
            source_time: Seconds(0.0),
            source_time_utc: "2014-03-08T18:02:00Z".to_string(),
            dynamics_model_family: "powered-marked-jump-v1".to_string(),
            fuel_model_family: "conditional-martin-extended-v1".to_string(),
            pending_renewal_refresh: None,
            powered_performance_model_family: "attached-flow-segment-force-balance-v1".to_string(),
            powered_aerodynamic_family: "openap-v2.6.0-b772-attached-flow".to_string(),
            powered_thrust_family: "openap-v2.6.0-b772-trent895-cruise-ceiling".to_string(),
            powered_thrust_multiplier: 1.25,
            powered_static_thrust_cap_per_engine_n: 411_480.0,
            powered_maximum_additional_drag_coefficient: 0.1,
            configured_particles: 100,
            strata: vec![
                BroadStratumMetadataV1 {
                    id: StratumId(1),
                    name: "persistent".to_string(),
                    process_family: "gamma-renewal-low-rate".to_string(),
                    scientific_log_prior_probability: 0.6_f64.ln(),
                    allocated_particles: 60,
                },
                BroadStratumMetadataV1 {
                    id: StratumId(2),
                    name: "flexible".to_string(),
                    process_family: "gamma-renewal-high-rate".to_string(),
                    scientific_log_prior_probability: 0.4_f64.ln(),
                    allocated_particles: 40,
                },
            ],
        }
    }

    fn small_run_metadata() -> BroadRunMetadataV1 {
        let mut run = run_metadata();
        run.configured_particles = 4;
        run.strata[0].allocated_particles = 2;
        run.strata[0].scientific_log_prior_probability = 0.5_f64.ln();
        run.strata[1].allocated_particles = 2;
        run.strata[1].scientific_log_prior_probability = 0.5_f64.ln();
        run
    }

    fn broad_state(slot: usize, stratum: StratumId, time_s: f64) -> BroadFlightState {
        let bias = BfoBiasState {
            mean_hz: 145.0 + slot as f64,
            variance_hz2: 16.0,
        };
        let aircraft = AircraftState {
            time: Seconds(time_s),
            position: LatLon::new(-20.0 - slot as f64, 90.0 + slot as f64).unwrap(),
            altitude: Feet(35_000.0),
            track_true: Degrees(180.0),
            ground_speed: Knots(470.0),
            vertical_speed: FeetPerMinute(0.0),
            bfo_bias: Hertz(bias.mean_hz),
        };
        BroadFlightState {
            stratum,
            powered_flight: PoweredFlightState {
                aircraft,
                heading_true: Degrees(178.0),
                mach: 0.82,
                bank_angle: Degrees(0.0),
                command: PoweredFlightCommand {
                    lateral_mode: PoweredLateralMode::ConstantTrueTrack,
                    selected_control: Degrees(180.0),
                    great_circle_destination: None,
                    target_mach: 0.82,
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
                time: Seconds(time_s),
                zero_fuel_weight: Kilograms(174_369.0),
                left_usable_feed: Kilograms(5_000.0),
                right_usable_feed: Kilograms(5_000.0),
                reserved_fuel: Kilograms(15.0),
                unusable_fuel: Kilograms(0.0),
                left_exhaustion_time: None,
                right_exhaustion_time: None,
                dual_engine_exhaustion_time: None,
            },
            fuel_flow_scale: 0.875 + 0.031_25 * slot as f64,
            fuel_quantity_offset_kg: -75.0 + 50.0 * slot as f64,
            bfo_bias: bias,
            status: BroadFlightParticleStatus::Active,
            fuel_status: BroadFuelDiagnosticStatus::Valid,
            scores: BroadFlightScores {
                cumulative_bto_log_likelihood: -1.0 - slot as f64,
                cumulative_bfo_log_likelihood: -2.0 - slot as f64,
                bto_observations: 1,
                bfo_observations: 1,
            },
            last_fit: None,
            diagnostics: BroadFlightDiagnostics::default(),
        }
    }

    fn aggregate_evidence() -> (BroadEvidenceLedgerV1, BroadAggregateEvidenceV1) {
        let bto = BroadEvidenceIdentityV1 {
            epoch_id: "bto-through-m0011".to_string(),
            channel: Some("aggregate".to_string()),
            component: BroadEvidenceComponentV1::Bto,
        };
        let bfo = BroadEvidenceIdentityV1 {
            epoch_id: "bfo-through-m0011".to_string(),
            channel: Some("aggregate".to_string()),
            component: BroadEvidenceComponentV1::Bfo,
        };
        let mut ledger = BroadEvidenceLedgerV1::new();
        ledger
            .consume(bto.clone(), BroadEvidenceStateEffectV1::None)
            .unwrap();
        ledger
            .consume(
                bfo.clone(),
                BroadEvidenceStateEffectV1::AnalyticLatentUpdate,
            )
            .unwrap();
        (
            ledger,
            BroadAggregateEvidenceV1 {
                bto_through_checkpoint: bto,
                bfo_through_checkpoint: Some(bfo),
                bto_observation_count: 1,
                bfo_observation_count: 1,
            },
        )
    }

    fn filtering_checkpoint(time_s: f64) -> BroadCheckpointMetadataV1 {
        BroadCheckpointMetadataV1 {
            checkpoint_id: "m0011-filtered".to_string(),
            state_epoch_id: "m0011".to_string(),
            state_time: Seconds(time_s),
            state_time_utc: "2014-03-09T00:11:00Z".to_string(),
            conditioning: BroadConditioningSemanticsV1::Filtering {
                through_epoch_id: "m0011".to_string(),
            },
        }
    }

    #[test]
    fn metadata_distinguishes_filtered_and_smoothed_checkpoints() {
        run_metadata().validate().unwrap();
        BroadCheckpointMetadataV1 {
            checkpoint_id: "m0011-filtered".to_string(),
            state_epoch_id: "m0011".to_string(),
            state_time: Seconds(22_150.0),
            state_time_utc: "2014-03-09T00:11:00Z".to_string(),
            conditioning: BroadConditioningSemanticsV1::Filtering {
                through_epoch_id: "m0011".to_string(),
            },
        }
        .validate()
        .unwrap();
        BroadCheckpointMetadataV1 {
            checkpoint_id: "m0011-smoothed-r600".to_string(),
            state_epoch_id: "m0011".to_string(),
            state_time: Seconds(22_150.0),
            state_time_utc: "2014-03-09T00:11:00Z".to_string(),
            conditioning: BroadConditioningSemanticsV1::Smoothed {
                filtering_checkpoint_id: "m0011-filtered".to_string(),
                conditioned_through_epoch_id: "m0019-r600".to_string(),
            },
        }
        .validate()
        .unwrap();
    }

    #[test]
    fn broad_evidence_consumption_is_atomic() {
        let evidence = identity(BroadEvidenceComponentV1::Bto);
        let mut ledger = BroadEvidenceLedgerV1::new();
        ledger
            .consume(evidence.clone(), BroadEvidenceStateEffectV1::None)
            .unwrap();
        assert_eq!(
            ledger.consume(evidence.clone(), BroadEvidenceStateEffectV1::None),
            Err(BroadEvidenceLedgerErrorV1::DuplicateConsumption(evidence))
        );

        let evidence = ledger.entries()[0].identity.clone();
        ledger
            .validate_particle_scores(&[BroadParticleEvidenceScoreV1 {
                identity: evidence.clone(),
                log_likelihood: -3.0,
            }])
            .unwrap();
        assert_eq!(
            ledger.validate_particle_scores(&[]),
            Err(BroadPosteriorHandoffErrorV1::InvalidEvidenceScores)
        );
    }

    #[test]
    fn filtering_builder_preserves_slots_roots_strata_and_round_trips() {
        let states = vec![
            broad_state(0, StratumId(1), 10.0),
            broad_state(1, StratumId(1), 10.0),
            broad_state(2, StratumId(2), 10.0),
            broad_state(3, StratumId(2), 10.0),
        ];
        let expected_states = states.clone();
        let snapshot = FilterSnapshot {
            observation_index: Some(0),
            observation_time_s: 10.0,
            particles: states,
            log_weights: [0.1_f64, 0.2, 0.3, 0.4].into_iter().map(f64::ln).collect(),
            root_ids: vec![3, 1, 2, 0],
            stratum_ids: vec![StratumId(1), StratumId(1), StratumId(2), StratumId(2)],
        };
        let (ledger, aggregate) = aggregate_evidence();
        let handoff = build_broad_filtering_handoff_v1(
            &snapshot,
            small_run_metadata(),
            filtering_checkpoint(10.0),
            ledger,
            aggregate,
        )
        .unwrap();
        assert_eq!(handoff.particles.len(), 4);
        assert_eq!(handoff.particles[0].identity.particle, 0);
        assert_eq!(handoff.particles[0].prior_root.initial_particle, 3);
        assert_eq!(handoff.particles[2].stratum, StratumId(2));
        assert!(handoff
            .particles
            .iter()
            .all(|particle| particle.parent_particle.is_none() && particle.descendant_count == 1));
        for particle in &handoff.particles {
            assert_eq!(
                particle.to_broad_flight_state(),
                expected_states[particle.identity.particle]
            );
        }
        let encoded = serde_json::to_string(&handoff).unwrap();
        let decoded: BroadPosteriorHandoffV1 = serde_json::from_str(&encoded).unwrap();
        assert_eq!(decoded.particles.len(), handoff.particles.len());
        assert_eq!(decoded.run, handoff.run);
        assert_eq!(decoded.checkpoint, handoff.checkpoint);
        for (decoded, original) in decoded.particles.iter().zip(&handoff.particles) {
            assert_eq!(decoded.identity, original.identity);
            assert_eq!(decoded.prior_root, original.prior_root);
            assert!(
                (decoded.normalized_log_weight - original.normalized_log_weight).abs()
                    < f64::EPSILON
            );
            assert_eq!(
                decoded.to_broad_flight_state(),
                original.to_broad_flight_state()
            );
        }
        decoded.validate().unwrap();
    }

    #[test]
    fn schema_two_validates_refresh_metadata_counters_and_pending_pairs() {
        let refresh_config = BroadPendingRenewalRefreshConfig {
            lateral: true,
            speed: true,
            altitude: true,
        };
        let pending = Some(PendingRenewal {
            not_before: Seconds(110.0),
            next_event: Seconds(210.0),
        });
        let mut states = vec![
            broad_state(0, StratumId(1), 10.0),
            broad_state(1, StratumId(1), 10.0),
            broad_state(2, StratumId(2), 10.0),
            broad_state(3, StratumId(2), 10.0),
        ];
        for state in &mut states {
            state.powered_flight.event_clocks = PoweredEventClocks {
                lateral: pending,
                speed: pending,
                altitude: pending,
            };
            state.diagnostics.pending_renewal_refresh.total_refreshes = 3;
            state.diagnostics.pending_renewal_refresh.lateral_refreshes = 1;
            state.diagnostics.pending_renewal_refresh.speed_refreshes = 1;
            state.diagnostics.pending_renewal_refresh.altitude_refreshes = 1;
        }
        let snapshot = FilterSnapshot {
            observation_index: Some(0),
            observation_time_s: 10.0,
            particles: states,
            log_weights: vec![0.25_f64.ln(); 4],
            root_ids: vec![0, 1, 2, 3],
            stratum_ids: vec![StratumId(1), StratumId(1), StratumId(2), StratumId(2)],
        };
        let mut run = small_run_metadata();
        run.pending_renewal_refresh = Some(refresh_config);
        let (ledger, aggregate) = aggregate_evidence();
        let handoff = build_broad_filtering_handoff_v1(
            &snapshot,
            run,
            filtering_checkpoint(10.0),
            ledger,
            aggregate,
        )
        .unwrap();
        assert_eq!(handoff.schema_version, 2);
        handoff.validate().unwrap();

        let encoded = serde_json::to_value(&handoff).unwrap();
        assert_eq!(
            encoded["run"]["pending_renewal_refresh"],
            serde_json::json!({"lateral": true, "speed": true, "altitude": true})
        );
        assert_eq!(
            encoded["particles"][0]["diagnostics"]["pending_renewal_refresh"]["total_refreshes"],
            3
        );
        serde_json::from_value::<BroadPosteriorHandoffV1>(encoded.clone())
            .unwrap()
            .validate()
            .unwrap();

        let mut legacy_schema = handoff.clone();
        legacy_schema.schema_version = 1;
        assert_eq!(
            legacy_schema.validate(),
            Err(BroadPosteriorHandoffErrorV1::UnsupportedSchema(1))
        );

        let mut absent_metadata = handoff.clone();
        absent_metadata.run.pending_renewal_refresh = None;
        assert_eq!(
            absent_metadata.validate(),
            Err(BroadPosteriorHandoffErrorV1::InvalidPendingRenewalRefresh)
        );

        let mut disabled_kind_with_history = handoff.clone();
        disabled_kind_with_history
            .run
            .pending_renewal_refresh
            .as_mut()
            .unwrap()
            .speed = false;
        assert_eq!(
            disabled_kind_with_history.validate(),
            Err(BroadPosteriorHandoffErrorV1::InvalidPendingRenewalRefresh)
        );

        let mut inconsistent_total = handoff.clone();
        inconsistent_total.particles[0]
            .diagnostics
            .pending_renewal_refresh
            .total_refreshes = 2;
        assert_eq!(
            inconsistent_total.validate(),
            Err(BroadPosteriorHandoffErrorV1::InvalidPendingRenewalRefresh)
        );

        let mut unequal_selected_counts = handoff.clone();
        let refresh = &mut unequal_selected_counts.particles[0]
            .diagnostics
            .pending_renewal_refresh;
        refresh.lateral_refreshes = 2;
        refresh.speed_refreshes = 1;
        refresh.altitude_refreshes = 0;
        assert_eq!(
            unequal_selected_counts.validate(),
            Err(BroadPosteriorHandoffErrorV1::InvalidPendingRenewalRefresh)
        );

        let mut missing_pair = handoff.clone();
        missing_pair.particles[0].powered_flight.event_clocks.speed = None;
        assert_eq!(
            missing_pair.validate(),
            Err(BroadPosteriorHandoffErrorV1::InvalidPendingRenewalRefresh)
        );

        let mut configured_without_realized_resample = handoff.clone();
        for particle in &mut configured_without_realized_resample.particles {
            particle.diagnostics.pending_renewal_refresh = Default::default();
        }
        configured_without_realized_resample.validate().unwrap();

        let mut legacy_numeric_clock = encoded;
        legacy_numeric_clock["particles"][0]["powered_flight"]["event_clocks"]["lateral"] =
            serde_json::json!(210.0);
        assert!(serde_json::from_value::<BroadPosteriorHandoffV1>(legacy_numeric_clock).is_err());
    }

    #[test]
    fn filtering_builder_preserves_and_validates_event_mark_proposal_correction() {
        let candidate_count = 4.0_f64;
        let defensive_prior_probability = 0.2_f64;
        let selected_probability = 0.1_f64;
        let log_candidate_count = candidate_count.ln();
        let event_correction = -log_candidate_count - selected_probability.ln();
        let maximum_selection_probability =
            defensive_prior_probability / candidate_count + 1.0 - defensive_prior_probability;
        let minimum_correction = -log_candidate_count - maximum_selection_probability.ln();
        let maximum_correction = -defensive_prior_probability.ln();
        let guide_diagnostics = BroadSatcomEventMarkGuideDiagnostics {
            eligible_lateral_events: 1,
            guided_lateral_events: 1,
            candidate_marks: candidate_count as u64,
            finite_candidate_scores: candidate_count as u64,
            materialization_failures: 0,
            proxy_projection_successes: candidate_count as u64,
            proxy_projection_failures: 0,
            proxy_projection_skipped_candidates: 0,
            all_scores_negative_infinity_events: 0,
            sum_selection_effective_sample_size: 2.0,
            sum_selection_entropy_nats: 1.0,
            minimum_selected_probability: Some(selected_probability),
            maximum_selected_probability: Some(selected_probability),
            minimum_event_log_prior_over_proposal: Some(event_correction),
            maximum_event_log_prior_over_proposal: Some(event_correction),
            minimum_lead_seconds: Some(900.0),
            maximum_lead_seconds: Some(900.0),
            sum_log_candidate_count: log_candidate_count,
            sum_selected_log_probability: selected_probability.ln(),
            cumulative_log_prior_over_proposal: event_correction,
            sum_minimum_log_prior_over_proposal: minimum_correction,
            sum_maximum_log_prior_over_proposal: maximum_correction,
        };
        let mut states = vec![
            broad_state(0, StratumId(1), 10.0),
            broad_state(1, StratumId(1), 10.0),
            broad_state(2, StratumId(2), 10.0),
            broad_state(3, StratumId(2), 10.0),
        ];
        for state in &mut states {
            state.diagnostics.satcom_event_mark_guide = guide_diagnostics;
        }
        let snapshot = FilterSnapshot {
            observation_index: Some(0),
            observation_time_s: 10.0,
            particles: states,
            log_weights: vec![0.25_f64.ln(); 4],
            root_ids: vec![0, 1, 2, 3],
            stratum_ids: vec![StratumId(1), StratumId(1), StratumId(2), StratumId(2)],
        };
        let (ledger, aggregate) = aggregate_evidence();
        let handoff = build_broad_filtering_handoff_v1(
            &snapshot,
            small_run_metadata(),
            filtering_checkpoint(10.0),
            ledger,
            aggregate,
        )
        .unwrap();
        assert!(handoff.particles.iter().all(|particle| {
            particle.cumulative_log_prior_over_proposal == event_correction
                && particle
                    .diagnostics
                    .satcom_event_mark_guide
                    .cumulative_log_prior_over_proposal
                    == event_correction
        }));
        handoff.validate().unwrap();

        let mut mismatched_particle = handoff.clone();
        mismatched_particle.particles[0].cumulative_log_prior_over_proposal = 0.0;
        assert_eq!(
            mismatched_particle.validate(),
            Err(BroadPosteriorHandoffErrorV1::InvalidParticle)
        );
        let mut invalid_aggregate = handoff;
        invalid_aggregate.particles[0]
            .diagnostics
            .satcom_event_mark_guide
            .sum_selected_log_probability = 0.0;
        assert_eq!(
            invalid_aggregate.validate(),
            Err(BroadPosteriorHandoffErrorV1::InvalidParticle)
        );
    }

    #[test]
    fn filtering_builder_records_no_bfo_evidence_for_bto_only_ablation() {
        let mut states = vec![
            broad_state(0, StratumId(1), 10.0),
            broad_state(1, StratumId(1), 10.0),
            broad_state(2, StratumId(2), 10.0),
            broad_state(3, StratumId(2), 10.0),
        ];
        for state in &mut states {
            state.scores.cumulative_bfo_log_likelihood = 0.0;
            state.scores.bfo_observations = 0;
        }
        let snapshot = FilterSnapshot {
            observation_index: Some(0),
            observation_time_s: 10.0,
            particles: states,
            log_weights: vec![0.25_f64.ln(); 4],
            root_ids: vec![0, 1, 2, 3],
            stratum_ids: vec![StratumId(1), StratumId(1), StratumId(2), StratumId(2)],
        };
        let bto = BroadEvidenceIdentityV1 {
            epoch_id: "bto-through-m0011".to_string(),
            channel: Some("aggregate".to_string()),
            component: BroadEvidenceComponentV1::Bto,
        };
        let mut ledger = BroadEvidenceLedgerV1::new();
        ledger
            .consume(bto.clone(), BroadEvidenceStateEffectV1::None)
            .unwrap();
        let handoff = build_broad_filtering_handoff_v1(
            &snapshot,
            small_run_metadata(),
            filtering_checkpoint(10.0),
            ledger,
            BroadAggregateEvidenceV1 {
                bto_through_checkpoint: bto,
                bfo_through_checkpoint: None,
                bto_observation_count: 1,
                bfo_observation_count: 0,
            },
        )
        .unwrap();
        assert!(handoff
            .evidence
            .entries()
            .iter()
            .all(|entry| { entry.identity.component != BroadEvidenceComponentV1::Bfo }));
        assert!(handoff.particles.iter().all(|particle| {
            particle.evidence_scores.len() == 1
                && particle.evidence_scores[0].identity.component == BroadEvidenceComponentV1::Bto
                && particle.source_log_likelihood == particle.evidence_scores[0].log_likelihood
        }));
        handoff.validate().unwrap();
    }

    #[test]
    fn smoothed_builder_aggregates_exact_descendant_weights() {
        let earlier_states = vec![
            broad_state(0, StratumId(1), 10.0),
            broad_state(1, StratumId(1), 10.0),
            broad_state(2, StratumId(2), 10.0),
            broad_state(3, StratumId(2), 10.0),
        ];
        let final_states = vec![
            broad_state(0, StratumId(1), 20.0),
            broad_state(1, StratumId(1), 20.0),
            broad_state(2, StratumId(2), 20.0),
            broad_state(3, StratumId(2), 20.0),
        ];
        let earlier = FilterSnapshot {
            observation_index: Some(0),
            observation_time_s: 10.0,
            particles: earlier_states,
            log_weights: vec![0.25_f64.ln(); 4],
            root_ids: vec![0, 1, 2, 3],
            stratum_ids: vec![StratumId(1), StratumId(1), StratumId(2), StratumId(2)],
        };
        let final_snapshot = FilterSnapshot {
            observation_index: Some(1),
            observation_time_s: 20.0,
            particles: final_states.clone(),
            log_weights: [0.1_f64, 0.2, 0.3, 0.4].into_iter().map(f64::ln).collect(),
            root_ids: vec![0, 0, 2, 2],
            stratum_ids: vec![StratumId(1), StratumId(1), StratumId(2), StratumId(2)],
        };
        let filter = FilterResult {
            particles: final_states,
            log_weights: final_snapshot.log_weights.clone(),
            root_ids: final_snapshot.root_ids.clone(),
            snapshots: vec![earlier, final_snapshot],
            ancestry: vec![FilterAncestryStep {
                child_observation_index: 1,
                parent_observation_index: Some(0),
                parent_indices: vec![0, 0, 2, 2],
            }],
            checkpoints: Vec::new(),
            log_evidence: 0.0,
            initial_log_evidence: 0.0,
            initial_strata: Vec::new(),
        };
        let checkpoint = BroadCheckpointMetadataV1 {
            checkpoint_id: "m0011-smoothed-m0019".to_string(),
            state_epoch_id: "m0011".to_string(),
            state_time: Seconds(10.0),
            state_time_utc: "2014-03-09T00:11:00Z".to_string(),
            conditioning: BroadConditioningSemanticsV1::Smoothed {
                filtering_checkpoint_id: "m0011-filtered".to_string(),
                conditioned_through_epoch_id: "m0019".to_string(),
            },
        };
        let (ledger, aggregate) = aggregate_evidence();
        let descendant_weights = [0.1_f64, 0.2, 0.3, 0.4]
            .into_iter()
            .map(f64::ln)
            .collect::<Vec<_>>();
        let handoff = build_broad_smoothed_handoff_v1(
            &filter,
            0,
            &descendant_weights,
            small_run_metadata(),
            checkpoint,
            ledger,
            aggregate,
        )
        .unwrap();
        assert_eq!(handoff.particles.len(), 2);
        assert_eq!(handoff.particles[0].identity.particle, 0);
        assert_eq!(handoff.particles[1].identity.particle, 2);
        assert!((handoff.particles[0].normalized_log_weight.exp() - 0.3).abs() < 1e-12);
        assert!((handoff.particles[1].normalized_log_weight.exp() - 0.7).abs() < 1e-12);
        assert_eq!(handoff.particles[0].descendant_count, 2);
        assert_eq!(handoff.particles[1].descendant_count, 2);
        assert_eq!(
            handoff.particles[1]
                .parent_particle
                .as_ref()
                .unwrap()
                .checkpoint_id,
            "m0011-filtered"
        );
        assert_eq!(handoff.particles[1].prior_root.initial_particle, 2);
        handoff.validate().unwrap();
    }
}
