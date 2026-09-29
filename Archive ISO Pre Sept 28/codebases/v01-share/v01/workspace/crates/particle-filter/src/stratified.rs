use std::collections::{BTreeMap, BTreeSet};

use rand::Rng;
use rand_chacha::ChaCha8Rng;
use rayon::prelude::*;
use serde::{Deserialize, Serialize};

use crate::{
    effective_sample_size, logsumexp, normalize_log_weights, rng_for, systematic_resample_n,
    Algorithm, FilterAncestryStep, FilterCheckpoint, FilterConfig, FilterResult, FilterRunOptions,
    FilterSnapshot, ParticleModel, Proposal, SmcError, SnapshotRetention, StratifiedFilterPlan,
    StratumAllocation, StratumDiagnostics, StratumId, WithinStratumResamplingPolicy,
};

use crate::filter::weight_diagnostics;
use crate::rng::rng_for_coordinates;

struct StratifiedEpoch<S> {
    states: Vec<S>,
    log_weights: Vec<f64>,
    ancestor_indices: Vec<usize>,
    stratum_ids: Vec<StratumId>,
    guide_ess: Option<f64>,
    posterior_ess: f64,
    ancestor_resampled: bool,
    log_evidence_increment: f64,
    transition_pool_checkpoint: Option<GlobalTransitionPoolCheckpoint>,
    root_stratified_candidate_pool_checkpoints: Vec<RootStratifiedCandidatePoolCheckpoint>,
    intermediate_potential_checkpoint: Option<IntermediatePotentialCheckpoint>,
    persistent_twist_log_potentials: Option<Vec<f64>>,
}

/// Stable random domain for an ordinary stratified-bootstrap move applied
/// after posterior resampling. The stream coordinates are the run seed,
/// observation index, output slot, and scientific stratum; prior-root identity
/// is deliberately absent so sibling children can receive distinct moves.
pub const STRATIFIED_POST_RESAMPLE_MOVE_RNG_DOMAIN: &str =
    "stratified-bootstrap-post-resample-move-v1";

/// Explicit per-observation lifecycle for a post-resampling move.
///
/// `Apply` invokes the configured move only when the ordinary bootstrap epoch
/// actually performs posterior resampling. It is valid and auditable for an
/// `Apply` step to record zero invocations when no resampling was required.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum StratifiedPostResampleMoveStep {
    Inactive,
    Apply,
}

/// Immutable identity of one ordinary post-resampling move invocation.
#[derive(Debug, Clone, Copy, PartialEq)]
pub struct StratifiedPostResampleMoveContext {
    pub observation_index: usize,
    pub observation_time_s: f64,
    pub stratum: StratumId,
    pub output_slot: usize,
    pub parent_slot: usize,
}

/// Model-owned invariant move applied to each child of an actual ordinary
/// stratified-bootstrap posterior resample.
///
/// The move must preserve the filtering target conditional on the immutable
/// state it retains. It receives no weight correction: a caller must not use
/// this seam for an approximate proposal or for additional scientific
/// evidence. The particle engine verifies that the move does not change the
/// state's scientific stratum.
pub trait StratifiedPostResampleMove<M: ParticleModel>: Sync {
    fn apply(
        &self,
        model: &M,
        state: &mut M::State,
        context: StratifiedPostResampleMoveContext,
        rng: &mut ChaCha8Rng,
    ) -> Result<(), M::Error>;
}

/// Explicit no-op implementation used to prove that enabling the bounded
/// execution seam does not perturb the legacy filter population.
#[derive(Debug, Clone, Copy, Default, PartialEq, Eq)]
pub struct NoopStratifiedPostResampleMove;

impl<M: ParticleModel> StratifiedPostResampleMove<M> for NoopStratifiedPostResampleMove {
    fn apply(
        &self,
        _model: &M,
        _state: &mut M::State,
        _context: StratifiedPostResampleMoveContext,
        _rng: &mut ChaCha8Rng,
    ) -> Result<(), M::Error> {
        Ok(())
    }
}

/// Exact output range and ancestry diversity on which a move was invoked.
/// Ordinary fixed-allocation resampling keeps each scientific stratum in one
/// canonical contiguous output range.
#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct StratifiedPostResampleMoveStratumCheckpoint {
    pub stratum: StratumId,
    pub output_slot_start: usize,
    pub output_slot_end_exclusive: usize,
    pub output_move_invocations: usize,
    pub distinct_parent_slots: usize,
    pub distinct_prior_roots: usize,
}

/// Audit record for one physical observation epoch.
#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct StratifiedPostResampleMoveCheckpoint {
    pub observation_index: usize,
    pub observation_time_s: f64,
    pub step: StratifiedPostResampleMoveStep,
    pub posterior_resampling_occurred: bool,
    pub output_move_invocations: usize,
    pub strata: Vec<StratifiedPostResampleMoveStratumCheckpoint>,
}

/// Ordinary filtering output plus the complete scheduled move ledger.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct StratifiedPostResampleMoveFilterResult<S> {
    pub pooled: FilterResult<S>,
    pub post_resample_move_checkpoints: Vec<StratifiedPostResampleMoveCheckpoint>,
}

/// Per-observation selection of the ordinary filter epoch or an exact global
/// ancestor/transition candidate pool.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(tag = "kind", rename_all = "snake_case")]
pub enum GlobalTransitionPoolStep {
    Standard,
    Pool { candidates_per_particle: usize },
}

/// Per-observation activation of a transition pool that draws a fixed number
/// of candidates from every finite-mass root in each scientific stratum.
///
/// This schedule is intentionally separate from [`GlobalTransitionPoolStep`]
/// so existing exhaustive matches and serialized legacy schedules remain
/// unchanged.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(tag = "kind", rename_all = "snake_case")]
pub enum RootStratifiedTransitionPoolStep {
    Standard,
    Pool { candidates_per_positive_root: usize },
}

/// Candidate-pool support and weight diagnostics inside one scientific
/// stratum. Candidate masses precede the final fixed-allocation downselection;
/// output masses describe the proper-weighted population after it.
#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct GlobalTransitionPoolStratumDiagnostics {
    pub id: StratumId,
    pub input_particles: usize,
    pub configured_candidates: usize,
    pub generated_candidates: usize,
    pub input_positive_roots: usize,
    pub sampled_ancestor_roots: usize,
    pub positive_candidates: usize,
    pub estimated_log_predictive_mass: Option<f64>,
    pub candidate_posterior_mass: f64,
    pub candidate_log_posterior_mass: Option<f64>,
    pub conditional_candidate_effective_sample_size: f64,
    pub conditional_maximum_candidate_weight: f64,
    pub distinct_positive_candidate_roots: usize,
    pub conditional_candidate_root_effective_sample_size: f64,
    pub conditional_maximum_candidate_root_weight: f64,
    pub output_posterior_mass: f64,
    pub output_log_posterior_mass: Option<f64>,
    /// Ancestor-proposal diagnostics when a strictly positive computational
    /// selection guide was enabled. The guide changes allocation only; the
    /// exact target/proposal correction remains in every candidate weight.
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub ancestor_selection_guide: Option<SelectionGuideDistributionDiagnostics>,
    /// Output-proposal diagnostics when a strictly positive computational
    /// selection guide was enabled. The selected population retains the exact
    /// candidate-target/proposal correction.
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub output_selection_guide: Option<SelectionGuideDistributionDiagnostics>,
}

/// Diagnostics for one proper proposal distribution tilted by a strictly
/// positive computational selection guide.
#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct SelectionGuideDistributionDiagnostics {
    pub positive_target_states: usize,
    pub minimum_log_guide: f64,
    pub maximum_log_guide: f64,
    /// `log E_target[h]` inside the scientific stratum before the defensive
    /// root mixture is applied.
    pub log_target_mean_guide: f64,
    pub proposal_effective_sample_size: f64,
    pub maximum_proposal_probability: f64,
    pub distinct_proposal_roots: usize,
    pub proposal_root_effective_sample_size: f64,
    pub maximum_proposal_root_probability: f64,
    pub maximum_absolute_log_target_over_proposal: f64,
}

/// Diagnostics for one exact global transition-pool epoch.
#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct GlobalTransitionPoolCheckpoint {
    pub observation_index: usize,
    pub observation_time_s: f64,
    /// Legacy per-particle candidate multiplier. This is zero for a
    /// root-stratified pool; its paired
    /// [`RootStratifiedCandidatePoolCheckpoint`] records the fixed per-root
    /// allocation.
    pub candidates_per_particle: usize,
    pub configured_candidates: usize,
    pub generated_candidates: usize,
    pub positive_candidates: usize,
    /// Normalizer of the proper-weighted candidate pool before output
    /// downselection.
    pub candidate_log_evidence_increment: f64,
    /// Stochastic normalization introduced only when the defensive output
    /// proposal differs from the candidate target.
    pub output_resampling_log_correction: f64,
    /// Increment actually accumulated by the filter. This is the sum of the
    /// preceding two log terms.
    pub realized_log_evidence_increment: f64,
    pub candidate_effective_sample_size: f64,
    pub maximum_candidate_weight: f64,
    pub distinct_positive_candidate_roots: usize,
    pub candidate_root_effective_sample_size: f64,
    pub maximum_candidate_root_weight: f64,
    pub strata: Vec<GlobalTransitionPoolStratumDiagnostics>,
}

/// Location of a fixed-root candidate pool within a physical observation
/// interval.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(tag = "kind", rename_all = "snake_case")]
pub enum RootStratifiedCandidatePoolLocation {
    ObservationEndpoint,
    IntermediatePoint { point_index: usize },
    IntermediateEndpoint { point_count: usize },
}

/// Concentration and independent split diagnostics for one scientific
/// stratum in a fixed-root candidate pool.
#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct RootStratifiedCandidatePoolStratumDiagnostics {
    pub id: StratumId,
    pub input_positive_roots: usize,
    pub candidates_per_positive_root: usize,
    pub generated_candidates: usize,
    pub roots_with_positive_candidates: usize,
    pub minimum_positive_candidates_per_root: usize,
    pub maximum_positive_candidates_per_root: usize,
    pub minimum_within_root_candidate_effective_sample_size: f64,
    pub median_within_root_candidate_effective_sample_size: f64,
    pub maximum_within_root_candidate_weight: f64,
    pub roots_with_maximum_candidate_weight_at_least_half: usize,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub first_split_log_predictive_mass: Option<f64>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub second_split_log_predictive_mass: Option<f64>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub absolute_split_log_predictive_mass_difference: Option<f64>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub split_root_total_variation: Option<f64>,
}

/// Diagnostics specific to a candidate pool with exactly `L` transition
/// replicates per finite-mass root. The ordinary proper-weight diagnostics are
/// reported separately in [`GlobalTransitionPoolCheckpoint`].
#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct RootStratifiedCandidatePoolCheckpoint {
    pub observation_index: usize,
    pub observation_time_s: f64,
    pub location: RootStratifiedCandidatePoolLocation,
    pub candidates_per_positive_root: usize,
    pub configured_candidates: usize,
    pub generated_candidates: usize,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub first_split_candidate_log_evidence_increment: Option<f64>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub second_split_candidate_log_evidence_increment: Option<f64>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub absolute_split_log_evidence_difference: Option<f64>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub split_candidate_root_total_variation: Option<f64>,
    pub strata: Vec<RootStratifiedCandidatePoolStratumDiagnostics>,
}

/// Ordinary fixed-allocation filtering output plus diagnostics for the epochs
/// on which a global transition pool was requested.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct GlobalTransitionPoolFilterResult<S> {
    pub pooled: FilterResult<S>,
    pub transition_pool_checkpoints: Vec<GlobalTransitionPoolCheckpoint>,
}

/// Exact filtering output and diagnostics from fixed-root transition pools.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct RootStratifiedTransitionPoolFilterResult<S> {
    pub pooled: FilterResult<S>,
    pub transition_pool_checkpoints: Vec<GlobalTransitionPoolCheckpoint>,
    pub root_stratified_candidate_pool_checkpoints: Vec<RootStratifiedCandidatePoolCheckpoint>,
}

/// Model-owned, strictly positive computational guide used only to allocate
/// ancestor and output proposals. It is never a likelihood or target factor.
/// The particle engine retains exact target/proposal corrections in all
/// weights, so filtering snapshots and evidence keep their ordinary meaning.
pub trait SelectionGuide<M: ParticleModel>: Sync {
    type Point: Sync;

    fn log_selection_guide(
        &self,
        model: &M,
        state: &M::State,
        endpoint_observation: &M::Observation,
        point: &Self::Point,
    ) -> Result<f64, M::Error>;
}

/// Per-observation activation of a model-owned computational selection guide.
#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(tag = "kind", rename_all = "snake_case")]
pub enum SelectionGuideStep<P> {
    Unguided,
    Guide { point: P },
}

/// Exact filtering output from a selection-guided run. Guided standard epochs
/// use a one-candidate global pool; guided bridge-stage diagnostics remain in
/// `intermediate_potential_checkpoints`.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SelectionGuideFilterResult<S> {
    pub pooled: FilterResult<S>,
    pub guided_standard_checkpoints: Vec<GlobalTransitionPoolCheckpoint>,
    pub intermediate_potential_checkpoints: Vec<IntermediatePotentialCheckpoint>,
}

/// A model-owned, strictly positive computational potential that may be
/// carried across physical observation epochs. While active, the particle
/// target is the physical filtering measure multiplied by this potential.
/// The potential is exactly removed at the declared final epoch and is never
/// itself evidence.
pub trait PersistentTwist<M: ParticleModel>: Sync {
    type Point: Sync;

    fn log_twist_potential(
        &self,
        model: &M,
        state: &M::State,
        endpoint_observation: &M::Observation,
        point: &Self::Point,
    ) -> Result<f64, M::Error>;
}

/// Typed lifecycle for one contiguous persistent-twist interval.
#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(tag = "kind", rename_all = "snake_case")]
pub enum PersistentTwistStep<P> {
    Inactive,
    Activate { point: P },
    Continue { point: P },
    Finalize { point: P },
}

/// Lifecycle phase recorded for an active persistent-twist epoch.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum PersistentTwistPhase {
    Activate,
    Continue,
    Finalize,
}

/// Pre-untwist support diagnostics for one persistent-twist epoch, together
/// with the ordinary physical population implied by exact division by the
/// current potential. The latter is diagnostic until `Finalize`.
#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct PersistentTwistPopulationDiagnostics {
    pub positive_particles: usize,
    pub minimum_log_potential: f64,
    pub maximum_log_potential: f64,
    pub twisted_effective_sample_size: f64,
    pub twisted_maximum_particle_weight: f64,
    pub twisted_distinct_positive_roots: usize,
    pub twisted_root_effective_sample_size: f64,
    pub twisted_maximum_root_weight: f64,
    pub twisted_strata: Vec<StratumDiagnostics>,
    /// `log E_twisted[1 / H]`. At `Finalize` this is the exact global
    /// normalizer applied to recover ordinary physical filtering weights.
    pub log_implied_untwist_correction: f64,
    pub implied_untwisted_effective_sample_size: f64,
    pub implied_untwisted_maximum_particle_weight: f64,
    pub implied_untwisted_distinct_positive_roots: usize,
    pub implied_untwisted_root_effective_sample_size: f64,
    pub implied_untwisted_maximum_root_weight: f64,
    pub implied_untwisted_strata: Vec<StratumDiagnostics>,
}

/// Exact evidence and support accounting for one active persistent-twist
/// epoch. Activate/Continue outputs are computational twisted targets, not
/// physical filtering posteriors. Finalize includes the single global
/// untwist and returns physical filtering semantics.
#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct PersistentTwistCheckpoint {
    pub observation_index: usize,
    pub observation_time_s: f64,
    pub phase: PersistentTwistPhase,
    pub output_is_twisted: bool,
    pub twisted_target_log_evidence_increment: f64,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub final_untwist_log_evidence_correction: Option<f64>,
    pub filter_checkpoint_log_evidence_increment: f64,
    pub population: PersistentTwistPopulationDiagnostics,
}

/// Output of a persistent-twist run. The final pooled population is always an
/// ordinary physical filtering result because a nonempty twist schedule must
/// contain exactly one `Finalize` step. Any retained intermediate snapshot
/// whose stored weights still target `mu * H` is listed explicitly.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PersistentTwistFilterResult<S> {
    pub pooled: FilterResult<S>,
    pub persistent_twist_checkpoints: Vec<PersistentTwistCheckpoint>,
    pub twisted_standard_checkpoints: Vec<GlobalTransitionPoolCheckpoint>,
    pub intermediate_potential_checkpoints: Vec<IntermediatePotentialCheckpoint>,
    pub twisted_filtering_observation_indices: Vec<usize>,
}

/// A model-owned intermediate state description and the number of globally
/// pooled transition candidates drawn per current particle. The particle
/// engine treats `point` as opaque scientific configuration.
#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct IntermediatePotentialBridgePoint<P> {
    pub point: P,
    pub candidates_per_particle: usize,
}

/// A model-owned intermediate state description and the number of transition
/// candidates drawn from every finite-mass root at that point.
#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct RootStratifiedIntermediatePotentialBridgePoint<P> {
    pub point: P,
    pub candidates_per_positive_root: usize,
}

/// Per-observation selection of the ordinary filter epoch or one or more
/// strictly positive intermediate guide potentials.
#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(tag = "kind", rename_all = "snake_case")]
pub enum IntermediatePotentialStep<P> {
    Standard,
    Bridge {
        points: Vec<IntermediatePotentialBridgePoint<P>>,
    },
    /// The same exact intermediate-potential bridge followed by a globally
    /// pooled endpoint transition. `endpoint_candidates_per_particle = 1` is
    /// deliberately canonicalized to the legacy [`Self::Bridge`] endpoint
    /// path, including its keyed random stream and serialized result.
    BridgeWithEndpointPool {
        points: Vec<IntermediatePotentialBridgePoint<P>>,
        endpoint_candidates_per_particle: usize,
    },
}

impl<P> IntermediatePotentialStep<P> {
    fn bridge_parts(&self) -> Option<(&[IntermediatePotentialBridgePoint<P>], usize)> {
        match self {
            Self::Standard => None,
            Self::Bridge { points } => Some((points, 1)),
            Self::BridgeWithEndpointPool {
                points,
                endpoint_candidates_per_particle,
            } => Some((points, *endpoint_candidates_per_particle)),
        }
    }
}

/// Per-observation intermediate-potential schedule using a fixed number of
/// candidates per finite-mass root at every declared point and endpoint.
#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(tag = "kind", rename_all = "snake_case")]
pub enum RootStratifiedIntermediatePotentialStep<P> {
    Standard,
    Bridge {
        points: Vec<RootStratifiedIntermediatePotentialBridgePoint<P>>,
        endpoint_candidates_per_positive_root: usize,
    },
}

impl<P> RootStratifiedIntermediatePotentialStep<P> {
    fn bridge_parts(
        &self,
    ) -> Option<(&[RootStratifiedIntermediatePotentialBridgePoint<P>], usize)> {
        match self {
            Self::Standard => None,
            Self::Bridge {
                points,
                endpoint_candidates_per_positive_root,
            } => Some((points, *endpoint_candidates_per_positive_root)),
        }
    }
}

/// One split-transition proposal and its model-owned ephemeral interval
/// context. The context is carried only by the particle engine while an
/// observation interval is being bridged; it is never stored in scientific
/// state or serialized into a snapshot.
#[derive(Debug, Clone)]
pub struct IntermediatePotentialProposal<S, C> {
    pub proposal: Proposal<S>,
    pub context: C,
}

/// Model-specific bridge operations used by the generic particle engine.
///
/// `begin_interval`, `propose_to_point`, and `propose_to_endpoint` share one
/// ephemeral per-lineage context so transition-wide budgets and invariants are
/// not reset at subdivision boundaries. Together the point and endpoint hooks
/// must describe the same physical transition law as an unsplit endpoint
/// transition; every proposal density correction belongs in the returned
/// [`Proposal`]. The context itself contributes no density factor and is never
/// serialized. `log_potential` is a read-only log of a strictly positive finite
/// guide potential; it must not assimilate or mutate the endpoint observation.
#[allow(clippy::too_many_arguments)]
pub trait IntermediatePotentialBridge<M: ParticleModel>: Sync {
    type Point: Sync;
    type Context: Clone + Send + Sync;

    fn point_time_s(&self, point: &Self::Point) -> f64;

    fn begin_interval(
        &self,
        model: &M,
        state: &M::State,
        endpoint_observation: &M::Observation,
    ) -> Result<Self::Context, M::Error>;

    fn propose_to_point(
        &self,
        model: &M,
        state: &M::State,
        endpoint_observation: &M::Observation,
        point: &Self::Point,
        context: &Self::Context,
        elapsed_seconds: f64,
        rng: &mut ChaCha8Rng,
    ) -> Result<IntermediatePotentialProposal<M::State, Self::Context>, M::Error>;

    fn propose_to_endpoint(
        &self,
        model: &M,
        state: &M::State,
        endpoint_observation: &M::Observation,
        context: &Self::Context,
        elapsed_seconds: f64,
        rng: &mut ChaCha8Rng,
    ) -> Result<Proposal<M::State>, M::Error>;

    fn log_potential(
        &self,
        model: &M,
        state: &M::State,
        endpoint_observation: &M::Observation,
        point: &Self::Point,
    ) -> Result<f64, M::Error>;
}

/// Diagnostics for one intermediate guide point. Candidate and output fields
/// retain the exact global-pool meanings; `observation_index` identifies the
/// physical endpoint and `observation_time_s` is this intermediate point time.
#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct IntermediatePotentialPointCheckpoint {
    pub point_index: usize,
    pub point_time_s: f64,
    pub elapsed_seconds: f64,
    pub candidate_pool: GlobalTransitionPoolCheckpoint,
    pub output_positive_particles: usize,
    pub output_effective_sample_size: f64,
    pub output_maximum_particle_weight: f64,
    pub output_distinct_positive_roots: usize,
    pub output_root_effective_sample_size: f64,
    pub output_maximum_root_weight: f64,
    pub output_strata: Vec<StratumDiagnostics>,
}

/// Exact endpoint `G / h_last` correction after all intermediate points.
#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct IntermediatePotentialEndpointCheckpoint {
    pub elapsed_seconds: f64,
    pub positive_particles: usize,
    pub log_evidence_increment: f64,
    pub posterior_effective_sample_size: f64,
    pub maximum_particle_weight: f64,
    pub distinct_positive_roots: usize,
    pub root_effective_sample_size: f64,
    pub maximum_root_weight: f64,
    pub strata: Vec<StratumDiagnostics>,
    /// Full proper-weight and support diagnostics when the endpoint uses more
    /// than one candidate per input particle. Absent on the legacy `K = 1`
    /// endpoint path so existing result serialization remains byte-identical.
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub candidate_pool: Option<GlobalTransitionPoolCheckpoint>,
}

/// Diagnostics for one physical observation interval bridged with strictly
/// positive intermediate potentials.
#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct IntermediatePotentialCheckpoint {
    pub observation_index: usize,
    pub observation_time_s: f64,
    pub points: Vec<IntermediatePotentialPointCheckpoint>,
    pub endpoint: IntermediatePotentialEndpointCheckpoint,
    /// Sum of every candidate-pool normalizer, every defensive-output
    /// correction, and the final exact `G / h_last` correction.
    pub realized_log_evidence_increment: f64,
}

/// Ordinary fixed-allocation filtering output plus diagnostics for intervals
/// using intermediate guide potentials.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct IntermediatePotentialFilterResult<S> {
    pub pooled: FilterResult<S>,
    pub intermediate_potential_checkpoints: Vec<IntermediatePotentialCheckpoint>,
}

/// Exact intermediate-potential output with fixed-root allocation diagnostics.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct RootStratifiedIntermediatePotentialFilterResult<S> {
    pub pooled: FilterResult<S>,
    pub intermediate_potential_checkpoints: Vec<IntermediatePotentialCheckpoint>,
    pub root_stratified_candidate_pool_checkpoints: Vec<RootStratifiedCandidatePoolCheckpoint>,
}

struct EpochInput<'a, M: ParticleModel> {
    model: &'a M,
    states: &'a [M::State],
    log_weights: &'a [f64],
    root_ids: &'a [usize],
    stratum_ids: &'a [StratumId],
    observation: &'a M::Observation,
    elapsed_seconds: f64,
    epoch: usize,
    config: &'a FilterConfig,
    resampling_policy: WithinStratumResamplingPolicy,
    retain_zero_mass_strata: bool,
}

fn model_error(error: impl std::fmt::Display) -> SmcError {
    SmcError::Model(error.to_string())
}

fn validate_observation_times<M: ParticleModel>(
    model: &M,
    observations: &[M::Observation],
    initial_time_s: f64,
) -> Result<(), SmcError> {
    let mut previous_time = initial_time_s;
    for observation in observations {
        let time = model.observation_time_s(observation);
        if !time.is_finite() || time < previous_time {
            return Err(SmcError::InvalidObservationTime);
        }
        previous_time = time;
    }
    Ok(())
}

fn indices_by_stratum(strata: &[StratumId]) -> BTreeMap<StratumId, Vec<usize>> {
    let mut indices = BTreeMap::<StratumId, Vec<usize>>::new();
    for (particle, &stratum) in strata.iter().enumerate() {
        indices.entry(stratum).or_default().push(particle);
    }
    indices
}

fn ensure_allocation(
    allocations: &[StratumAllocation],
    stratum_ids: &[StratumId],
) -> Result<BTreeMap<StratumId, Vec<usize>>, SmcError> {
    let indices = indices_by_stratum(stratum_ids);
    for allocation in allocations {
        if indices.get(&allocation.id).map(Vec::len) != Some(allocation.particles) {
            return Err(SmcError::StratumMismatch);
        }
    }
    if indices.len() != allocations.len() {
        return Err(SmcError::StratumMismatch);
    }
    Ok(indices)
}

/// Return normalized log proposal probabilities for a target distribution
/// after mixing its positive-mass root ancestors with a uniform root law.
/// Within each selected root, particles retain their exact target-conditional
/// probabilities, so clone multiplicity cannot dilute the defensive mass.
fn defensive_root_log_probabilities(
    target_log_probabilities: &[f64],
    root_ids: &[usize],
    policy: WithinStratumResamplingPolicy,
) -> Result<Vec<f64>, SmcError> {
    if target_log_probabilities.is_empty()
        || target_log_probabilities.len() != root_ids.len()
        || target_log_probabilities
            .iter()
            .any(|value| !(value.is_finite() || *value == f64::NEG_INFINITY))
    {
        return Err(SmcError::InvalidWeights);
    }
    policy.validate().map_err(SmcError::InvalidConfiguration)?;
    if policy.uniform_root_mixture_epsilon == 0.0 {
        return Ok(target_log_probabilities.to_vec());
    }

    let mut root_members = BTreeMap::<usize, Vec<usize>>::new();
    for (index, (&log_probability, &root)) in
        target_log_probabilities.iter().zip(root_ids).enumerate()
    {
        if log_probability.is_finite() {
            root_members.entry(root).or_default().push(index);
        }
    }
    if root_members.is_empty() {
        return Err(SmcError::AllParticlesRejected);
    }
    let root_count = root_members.len() as f64;
    let epsilon = policy.uniform_root_mixture_epsilon;
    let log_uniform_root = -root_count.ln();
    let mut result = vec![f64::NEG_INFINITY; target_log_probabilities.len()];
    for members in root_members.values() {
        let root_values = members
            .iter()
            .map(|&index| target_log_probabilities[index])
            .collect::<Vec<_>>();
        let log_root_mass = crate::logsumexp(&root_values)?;
        let log_proposal_root_mass = if epsilon == 1.0 {
            log_uniform_root
        } else {
            log_add_exp(
                (1.0 - epsilon).ln() + log_root_mass,
                epsilon.ln() + log_uniform_root,
            )
        };
        for &index in members {
            result[index] =
                log_proposal_root_mass + target_log_probabilities[index] - log_root_mass;
        }
    }
    let (normalized, _) = normalize_log_weights(&result)?;
    Ok(normalized)
}

type SelectionGuideScorer<'a, S> = dyn Fn(&S) -> Result<f64, SmcError> + Sync + 'a;

type PersistentTwistScorer<'a, S> = dyn Fn(&S) -> Result<f64, SmcError> + Sync + 'a;

struct PersistentTwistEpochInput<'a, S> {
    phase: PersistentTwistPhase,
    input_log_potentials: Option<&'a [f64]>,
    score: &'a PersistentTwistScorer<'a, S>,
}

fn selection_guided_root_log_probabilities<S>(
    target_log_probabilities: &[f64],
    states: &[S],
    root_ids: &[usize],
    policy: WithinStratumResamplingPolicy,
    guide: Option<&SelectionGuideScorer<'_, S>>,
) -> Result<(Vec<f64>, Option<SelectionGuideDistributionDiagnostics>), SmcError> {
    let Some(guide) = guide else {
        return defensive_root_log_probabilities(target_log_probabilities, root_ids, policy)
            .map(|probabilities| (probabilities, None));
    };
    if target_log_probabilities.len() != states.len()
        || target_log_probabilities.len() != root_ids.len()
    {
        return Err(SmcError::InvalidAncestry);
    }

    let mut guided_log_measures = Vec::with_capacity(states.len());
    let mut minimum_log_guide = f64::INFINITY;
    let mut maximum_log_guide = f64::NEG_INFINITY;
    let mut positive_target_states = 0usize;
    for (&target, state) in target_log_probabilities.iter().zip(states) {
        if target == f64::NEG_INFINITY {
            guided_log_measures.push(f64::NEG_INFINITY);
            continue;
        }
        if !target.is_finite() {
            return Err(SmcError::InvalidWeights);
        }
        let log_guide = guide(state)?;
        if !log_guide.is_finite() {
            return Err(SmcError::InvalidWeights);
        }
        positive_target_states += 1;
        minimum_log_guide = minimum_log_guide.min(log_guide);
        maximum_log_guide = maximum_log_guide.max(log_guide);
        guided_log_measures.push(target + log_guide);
    }
    if positive_target_states == 0 {
        return Err(SmcError::AllParticlesRejected);
    }

    let (guided_target, log_target_mean_guide) = normalize_log_weights(&guided_log_measures)?;
    let proposal = defensive_root_log_probabilities(&guided_target, root_ids, policy)?;
    let (
        _,
        proposal_ess,
        maximum_proposal_probability,
        distinct_proposal_roots,
        root_ess,
        maximum_root_probability,
    ) = conditional_support_diagnostics(&proposal, root_ids)?;
    let maximum_absolute_log_target_over_proposal = target_log_probabilities
        .iter()
        .zip(&proposal)
        .filter(|(target, _)| target.is_finite())
        .map(|(target, proposal)| (target - proposal).abs())
        .fold(0.0, f64::max);

    Ok((
        proposal,
        Some(SelectionGuideDistributionDiagnostics {
            positive_target_states,
            minimum_log_guide,
            maximum_log_guide,
            log_target_mean_guide,
            proposal_effective_sample_size: proposal_ess,
            maximum_proposal_probability,
            distinct_proposal_roots,
            proposal_root_effective_sample_size: root_ess,
            maximum_proposal_root_probability: maximum_root_probability,
            maximum_absolute_log_target_over_proposal,
        }),
    ))
}

fn log_add_exp(first: f64, second: f64) -> f64 {
    let maximum = first.max(second);
    maximum + ((first - maximum).exp() + (second - maximum).exp()).ln()
}

fn run_stratified_bootstrap_epoch<M: ParticleModel>(
    input: &EpochInput<'_, M>,
) -> Result<StratifiedEpoch<M::State>, SmcError> {
    let EpochInput {
        model,
        states,
        log_weights,
        stratum_ids,
        observation,
        elapsed_seconds,
        epoch,
        config,
        ..
    } = input;
    let proposals = states
        .par_iter()
        .enumerate()
        .map(|(particle, state)| {
            if input.retain_zero_mass_strata && log_weights[particle] == f64::NEG_INFINITY {
                return Ok((state.clone(), f64::NEG_INFINITY));
            }
            let mut rng = rng_for(
                config.seed,
                "stratified-bootstrap-proposal",
                *epoch,
                particle,
                0,
            );
            let mut proposal = model
                .propose(state, observation, *elapsed_seconds, &mut rng)
                .map_err(model_error)?;
            if !proposal.log_prior_over_proposal.is_finite()
                || model.stratum(&proposal.state) != stratum_ids[particle]
            {
                return Err(if !proposal.log_prior_over_proposal.is_finite() {
                    SmcError::InvalidWeights
                } else {
                    SmcError::StratumMismatch
                });
            }
            let likelihood = model
                .observe(&mut proposal.state, observation)
                .map_err(model_error)?;
            if !(likelihood.is_finite() || likelihood == f64::NEG_INFINITY) {
                return Err(SmcError::InvalidWeights);
            }
            if model.stratum(&proposal.state) != stratum_ids[particle] {
                return Err(SmcError::StratumMismatch);
            }
            Ok((
                proposal.state,
                log_weights[particle] + likelihood + proposal.log_prior_over_proposal,
            ))
        })
        .collect::<Vec<Result<_, SmcError>>>();

    let mut new_states = Vec::with_capacity(states.len());
    let mut raw_weights = Vec::with_capacity(states.len());
    for proposal in proposals {
        let (state, weight) = proposal?;
        new_states.push(state);
        raw_weights.push(weight);
    }
    let (normalized, log_evidence_increment) = normalize_log_weights(&raw_weights)?;
    let posterior_ess = effective_sample_size(&normalized)?;
    Ok(StratifiedEpoch {
        states: new_states,
        log_weights: normalized,
        ancestor_indices: (0..states.len()).collect(),
        stratum_ids: stratum_ids.to_vec(),
        guide_ess: None,
        posterior_ess,
        ancestor_resampled: false,
        log_evidence_increment,
        transition_pool_checkpoint: None,
        root_stratified_candidate_pool_checkpoints: Vec::new(),
        intermediate_potential_checkpoint: None,
        persistent_twist_log_potentials: None,
    })
}

fn run_stratified_auxiliary_epoch<M: ParticleModel>(
    input: &EpochInput<'_, M>,
    allocations: &[StratumAllocation],
) -> Result<StratifiedEpoch<M::State>, SmcError> {
    let EpochInput {
        model,
        states,
        log_weights,
        root_ids,
        stratum_ids,
        observation,
        elapsed_seconds,
        epoch,
        config,
        resampling_policy,
        retain_zero_mass_strata,
    } = input;
    let sources = ensure_allocation(allocations, stratum_ids)?;
    let guides = states
        .par_iter()
        .zip(log_weights.par_iter())
        .map(|(state, &log_weight)| {
            if *retain_zero_mass_strata && log_weight == f64::NEG_INFINITY {
                return Ok(f64::NEG_INFINITY);
            }
            let value = model
                .guide_log_likelihood(state, observation)
                .map_err(model_error)?;
            if value.is_finite() || value == f64::NEG_INFINITY {
                Ok(value)
            } else {
                Err(SmcError::InvalidWeights)
            }
        })
        .collect::<Vec<Result<f64, SmcError>>>()
        .into_iter()
        .collect::<Result<Vec<_>, _>>()?;

    // Each tuple is (output slot, source ancestor, expected stratum,
    // cross-stratum allocation correction excluding the likelihood).
    let mut assignments = Vec::with_capacity(states.len());
    let mut guide_log_probabilities = vec![f64::NEG_INFINITY; states.len()];
    let mut output_slot = 0usize;
    for allocation in allocations {
        let source_indices = &sources[&allocation.id];
        let ancestor_raw = source_indices
            .iter()
            .map(|&index| log_weights[index] + guides[index])
            .collect::<Vec<_>>();
        let island_was_already_extinct = source_indices
            .iter()
            .all(|&index| log_weights[index] == f64::NEG_INFINITY);
        if island_was_already_extinct && *retain_zero_mass_strata {
            for &ancestor in source_indices {
                assignments.push((output_slot, ancestor, allocation.id, f64::NEG_INFINITY));
                output_slot += 1;
            }
            continue;
        }
        let (conditional_log_weights, log_guide_mass) = normalize_log_weights(&ancestor_raw)
            .map_err(|error| match error {
                SmcError::AllParticlesRejected => SmcError::StratumRejected(allocation.id),
                other => other,
            })?;
        let source_roots = source_indices
            .iter()
            .map(|&index| root_ids[index])
            .collect::<Vec<_>>();
        let ancestor_proposal_log_probabilities = defensive_root_log_probabilities(
            &conditional_log_weights,
            &source_roots,
            *resampling_policy,
        )
        .map_err(|error| match error {
            SmcError::AllParticlesRejected => SmcError::StratumRejected(allocation.id),
            other => other,
        })?;
        let allocation_probability = allocation.particles as f64 / states.len() as f64;
        for (&source, &proposal) in source_indices
            .iter()
            .zip(&ancestor_proposal_log_probabilities)
        {
            guide_log_probabilities[source] = allocation_probability.ln() + proposal;
        }
        let ancestor_proposal_weights = ancestor_proposal_log_probabilities
            .iter()
            .map(|value| value.exp())
            .collect::<Vec<_>>();
        let mut rng = rng_for(
            config.seed,
            "stratified-auxiliary-ancestor",
            *epoch,
            output_slot,
            allocation.id.0 as u64,
        );
        let first_offset = rng.gen::<f64>() / allocation.particles as f64;
        let local_ancestors = systematic_resample_n(
            &ancestor_proposal_weights,
            allocation.particles,
            first_offset,
        )?;
        for local_ancestor in local_ancestors {
            let ancestor = source_indices[local_ancestor];
            let base_correction = if resampling_policy.uniform_root_mixture_epsilon == 0.0 {
                log_guide_mass - allocation_probability.ln() - guides[ancestor]
            } else {
                log_weights[ancestor]
                    - allocation_probability.ln()
                    - ancestor_proposal_log_probabilities[local_ancestor]
            };
            assignments.push((output_slot, ancestor, allocation.id, base_correction));
            output_slot += 1;
        }
    }
    let guide_ess = effective_sample_size(&guide_log_probabilities)?;

    let proposals = assignments
        .par_iter()
        .map(|&(particle, ancestor, expected_stratum, base_correction)| {
            if *retain_zero_mass_strata && base_correction == f64::NEG_INFINITY {
                return Ok((states[ancestor].clone(), f64::NEG_INFINITY));
            }
            let mut rng = rng_for(
                config.seed,
                "stratified-auxiliary-proposal",
                *epoch,
                particle,
                0,
            );
            let mut proposal = model
                .propose(&states[ancestor], observation, *elapsed_seconds, &mut rng)
                .map_err(model_error)?;
            if !proposal.log_prior_over_proposal.is_finite() {
                return Err(SmcError::InvalidWeights);
            }
            if model.stratum(&proposal.state) != expected_stratum {
                return Err(SmcError::StratumMismatch);
            }
            let likelihood = model
                .observe(&mut proposal.state, observation)
                .map_err(model_error)?;
            if !(likelihood.is_finite() || likelihood == f64::NEG_INFINITY) {
                return Err(SmcError::InvalidWeights);
            }
            if model.stratum(&proposal.state) != expected_stratum {
                return Err(SmcError::StratumMismatch);
            }
            Ok((
                proposal.state,
                likelihood + proposal.log_prior_over_proposal + base_correction,
            ))
        })
        .collect::<Vec<Result<_, SmcError>>>();

    let mut new_states = Vec::with_capacity(states.len());
    let mut raw_weights = Vec::with_capacity(states.len());
    for proposal in proposals {
        let (state, weight) = proposal?;
        new_states.push(state);
        raw_weights.push(weight);
    }
    let (normalized, raw_normalizer) = normalize_log_weights(&raw_weights)?;
    let posterior_ess = effective_sample_size(&normalized)?;
    Ok(StratifiedEpoch {
        states: new_states,
        log_weights: normalized,
        ancestor_indices: assignments
            .iter()
            .map(|(_, ancestor, _, _)| *ancestor)
            .collect(),
        stratum_ids: assignments
            .iter()
            .map(|(_, _, stratum, _)| *stratum)
            .collect(),
        guide_ess: Some(guide_ess),
        posterior_ess,
        ancestor_resampled: true,
        log_evidence_increment: raw_normalizer - (states.len() as f64).ln(),
        transition_pool_checkpoint: None,
        root_stratified_candidate_pool_checkpoints: Vec::new(),
        intermediate_potential_checkpoint: None,
        persistent_twist_log_potentials: None,
    })
}

#[derive(Debug)]
struct TransitionPoolCandidate<S, A> {
    state: S,
    log_measure: f64,
    ancestor_index: usize,
    root_id: usize,
    root_replicate: Option<usize>,
    carried_auxiliary: A,
}

struct CandidatePoolEpoch<S, A> {
    epoch: StratifiedEpoch<S>,
    carried_auxiliary: Vec<A>,
    checkpoint: GlobalTransitionPoolCheckpoint,
    root_stratified_checkpoint: Option<RootStratifiedCandidatePoolCheckpoint>,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
enum CandidatePoolAllocation {
    PerParticle(usize),
    PerPositiveRoot(usize),
}

impl CandidatePoolAllocation {
    fn validate(self) -> Result<(), SmcError> {
        match self {
            Self::PerParticle(0) => Err(SmcError::InvalidConfiguration(
                "global transition-pool candidates per particle must be positive",
            )),
            Self::PerPositiveRoot(0) => Err(SmcError::InvalidConfiguration(
                "root-stratified transition-pool candidates per positive root must be positive",
            )),
            Self::PerParticle(_) | Self::PerPositiveRoot(_) => Ok(()),
        }
    }

    fn legacy_candidates_per_particle(self) -> usize {
        match self {
            Self::PerParticle(candidates) => candidates,
            Self::PerPositiveRoot(_) => 0,
        }
    }
}

#[derive(Debug, Clone, Copy)]
enum CandidatePoolRandomDomain {
    EndpointObservation,
    IntermediatePotential { point_index: usize },
    IntermediatePotentialEndpoint { point_count: usize },
}

impl CandidatePoolRandomDomain {
    fn ancestor_purpose(self) -> &'static str {
        match self {
            Self::EndpointObservation => "stratified-global-pool-ancestor",
            Self::IntermediatePotential { .. } => "stratified-intermediate-potential-pool-ancestor",
            Self::IntermediatePotentialEndpoint { .. } => {
                "stratified-intermediate-potential-endpoint-pool-ancestor"
            }
        }
    }

    fn transition_purpose(self) -> &'static str {
        match self {
            Self::EndpointObservation => "stratified-global-pool-transition",
            Self::IntermediatePotential { .. } => {
                "stratified-intermediate-potential-pool-transition"
            }
            Self::IntermediatePotentialEndpoint { .. } => {
                "stratified-intermediate-potential-endpoint-pool-transition"
            }
        }
    }

    fn output_purpose(self) -> &'static str {
        match self {
            Self::EndpointObservation => "stratified-global-pool-output",
            Self::IntermediatePotential { .. } => "stratified-intermediate-potential-pool-output",
            Self::IntermediatePotentialEndpoint { .. } => {
                "stratified-intermediate-potential-endpoint-pool-output"
            }
        }
    }

    fn root_ancestor_purpose(self) -> &'static str {
        match self {
            Self::EndpointObservation => "stratified-root-pool-ancestor-v1",
            Self::IntermediatePotential { .. } => {
                "stratified-root-intermediate-potential-pool-ancestor-v1"
            }
            Self::IntermediatePotentialEndpoint { .. } => {
                "stratified-root-intermediate-potential-endpoint-pool-ancestor-v1"
            }
        }
    }

    fn root_transition_purpose(self) -> &'static str {
        match self {
            Self::EndpointObservation => "stratified-root-pool-transition-v1",
            Self::IntermediatePotential { .. } => {
                "stratified-root-intermediate-potential-pool-transition-v1"
            }
            Self::IntermediatePotentialEndpoint { .. } => {
                "stratified-root-intermediate-potential-endpoint-pool-transition-v1"
            }
        }
    }

    fn root_output_purpose(self) -> &'static str {
        match self {
            Self::EndpointObservation => "stratified-root-pool-output-v1",
            Self::IntermediatePotential { .. } => {
                "stratified-root-intermediate-potential-pool-output-v1"
            }
            Self::IntermediatePotentialEndpoint { .. } => {
                "stratified-root-intermediate-potential-endpoint-pool-output-v1"
            }
        }
    }

    fn root_location(self) -> RootStratifiedCandidatePoolLocation {
        match self {
            Self::EndpointObservation => RootStratifiedCandidatePoolLocation::ObservationEndpoint,
            Self::IntermediatePotential { point_index } => {
                RootStratifiedCandidatePoolLocation::IntermediatePoint { point_index }
            }
            Self::IntermediatePotentialEndpoint { point_count } => {
                RootStratifiedCandidatePoolLocation::IntermediateEndpoint { point_count }
            }
        }
    }

    fn root_coordinates(self, stratum: StratumId, root: usize, replicate: usize) -> [u64; 5] {
        let (stage, stage_index) = match self {
            Self::EndpointObservation => (0, 0),
            Self::IntermediatePotential { point_index } => (1, point_index as u64),
            Self::IntermediatePotentialEndpoint { point_count } => (2, point_count as u64),
        };
        [
            stratum.0 as u64,
            root as u64,
            stage,
            stage_index,
            replicate as u64,
        ]
    }

    fn substream(self, stratum: StratumId) -> u64 {
        match self {
            Self::EndpointObservation => stratum.0 as u64,
            Self::IntermediatePotential { point_index } => point_index as u64,
            Self::IntermediatePotentialEndpoint { point_count } => point_count as u64,
        }
    }
}

fn conditional_support_diagnostics(
    log_measures: &[f64],
    root_ids: &[usize],
) -> Result<(usize, f64, f64, usize, f64, f64), SmcError> {
    if log_measures.len() != root_ids.len() {
        return Err(SmcError::InvalidAncestry);
    }
    let (normalized, _) = normalize_log_weights(log_measures)?;
    let positive_candidates = normalized.iter().filter(|value| value.is_finite()).count();
    let candidate_ess = effective_sample_size(&normalized)?;
    let maximum_candidate_weight = normalized
        .iter()
        .filter(|value| value.is_finite())
        .map(|value| value.exp())
        .fold(0.0, f64::max);
    let mut root_masses = BTreeMap::<usize, f64>::new();
    for (&root, &log_weight) in root_ids.iter().zip(&normalized) {
        if log_weight.is_finite() {
            *root_masses.entry(root).or_default() += log_weight.exp();
        }
    }
    let root_sum_squares = root_masses.values().map(|mass| mass * mass).sum::<f64>();
    let root_ess = if root_sum_squares > 0.0 {
        1.0 / root_sum_squares
    } else {
        0.0
    };
    let maximum_root_weight = root_masses.values().copied().fold(0.0, f64::max);
    Ok((
        positive_candidates,
        candidate_ess,
        maximum_candidate_weight,
        root_masses.len(),
        root_ess,
        maximum_root_weight,
    ))
}

struct RootStratifiedStratumSummary {
    diagnostics: RootStratifiedCandidatePoolStratumDiagnostics,
    first_root_log_masses: BTreeMap<usize, f64>,
    second_root_log_masses: BTreeMap<usize, f64>,
}

fn optional_logsumexp(values: impl IntoIterator<Item = f64>) -> Result<Option<f64>, SmcError> {
    let finite = values
        .into_iter()
        .filter(|value| value.is_finite())
        .collect::<Vec<_>>();
    if finite.is_empty() {
        Ok(None)
    } else {
        logsumexp(&finite).map(Some)
    }
}

fn root_distribution_total_variation(
    first: &BTreeMap<usize, f64>,
    second: &BTreeMap<usize, f64>,
) -> Result<Option<f64>, SmcError> {
    let Some(first_normalizer) = optional_logsumexp(first.values().copied())? else {
        return Ok(None);
    };
    let Some(second_normalizer) = optional_logsumexp(second.values().copied())? else {
        return Ok(None);
    };
    let roots = first
        .keys()
        .chain(second.keys())
        .copied()
        .map(|root| (root, ()))
        .collect::<BTreeMap<_, _>>();
    let total_variation = 0.5
        * roots
            .keys()
            .map(|root| {
                let first_mass = first
                    .get(root)
                    .map_or(0.0, |mass| (*mass - first_normalizer).exp());
                let second_mass = second
                    .get(root)
                    .map_or(0.0, |mass| (*mass - second_normalizer).exp());
                (first_mass - second_mass).abs()
            })
            .sum::<f64>();
    Ok(Some(total_variation))
}

fn root_stratified_stratum_summary<S, A>(
    id: StratumId,
    input_positive_roots: usize,
    candidates_per_positive_root: usize,
    candidates: &[TransitionPoolCandidate<S, A>],
) -> Result<RootStratifiedStratumSummary, SmcError> {
    let mut candidates_by_root = BTreeMap::<usize, Vec<&TransitionPoolCandidate<S, A>>>::new();
    for candidate in candidates {
        if candidate.root_replicate.is_none() {
            return Err(SmcError::InvalidConfiguration(
                "root-stratified diagnostics received a legacy candidate",
            ));
        }
        candidates_by_root
            .entry(candidate.root_id)
            .or_default()
            .push(candidate);
    }
    if candidates_by_root.len() != input_positive_roots
        || candidates_by_root
            .values()
            .any(|members| members.len() != candidates_per_positive_root)
    {
        return Err(SmcError::InvalidAncestry);
    }

    let mut positive_counts = Vec::with_capacity(input_positive_roots);
    let mut within_root_ess = Vec::with_capacity(input_positive_roots);
    let mut maximum_within_root_candidate_weight = 0.0_f64;
    let mut roots_with_maximum_candidate_weight_at_least_half = 0usize;
    let mut first_root_log_masses = BTreeMap::new();
    let mut second_root_log_masses = BTreeMap::new();
    let first_split_count = candidates_per_positive_root.div_ceil(2);
    let second_split_count = candidates_per_positive_root / 2;

    for (&root, members) in &candidates_by_root {
        let log_measures = members
            .iter()
            .map(|candidate| candidate.log_measure)
            .collect::<Vec<_>>();
        let positive = log_measures
            .iter()
            .filter(|value| value.is_finite())
            .count();
        positive_counts.push(positive);
        if positive == 0 {
            within_root_ess.push(0.0);
        } else {
            let (normalized, _) = normalize_log_weights(&log_measures)?;
            let ess = effective_sample_size(&normalized)?;
            let maximum = normalized
                .iter()
                .filter(|value| value.is_finite())
                .map(|value| value.exp())
                .fold(0.0, f64::max);
            within_root_ess.push(ess);
            maximum_within_root_candidate_weight =
                maximum_within_root_candidate_weight.max(maximum);
            if maximum >= 0.5 {
                roots_with_maximum_candidate_weight_at_least_half += 1;
            }
        }

        let first = members
            .iter()
            .filter(|candidate| candidate.root_replicate.expect("checked") % 2 == 0)
            .map(|candidate| candidate.log_measure);
        if let Some(log_mass) = optional_logsumexp(first)? {
            first_root_log_masses.insert(
                root,
                log_mass + (candidates_per_positive_root as f64 / first_split_count as f64).ln(),
            );
        }
        if second_split_count > 0 {
            let second = members
                .iter()
                .filter(|candidate| candidate.root_replicate.expect("checked") % 2 == 1)
                .map(|candidate| candidate.log_measure);
            if let Some(log_mass) = optional_logsumexp(second)? {
                second_root_log_masses.insert(
                    root,
                    log_mass
                        + (candidates_per_positive_root as f64 / second_split_count as f64).ln(),
                );
            }
        }
    }
    within_root_ess.sort_by(f64::total_cmp);
    let median_within_root_candidate_effective_sample_size = if within_root_ess.is_empty() {
        0.0
    } else {
        within_root_ess[within_root_ess.len() / 2]
    };
    let first_split_log_predictive_mass =
        optional_logsumexp(first_root_log_masses.values().copied())?;
    let second_split_log_predictive_mass =
        optional_logsumexp(second_root_log_masses.values().copied())?;
    let absolute_split_log_predictive_mass_difference = first_split_log_predictive_mass
        .zip(second_split_log_predictive_mass)
        .map(|(first, second)| (first - second).abs());
    let split_root_total_variation =
        root_distribution_total_variation(&first_root_log_masses, &second_root_log_masses)?;
    let roots_with_positive_candidates = positive_counts.iter().filter(|&&count| count > 0).count();
    let minimum_positive_candidates_per_root = positive_counts.iter().copied().min().unwrap_or(0);
    let maximum_positive_candidates_per_root = positive_counts.iter().copied().max().unwrap_or(0);
    let minimum_within_root_candidate_effective_sample_size =
        within_root_ess.first().copied().unwrap_or(0.0);

    Ok(RootStratifiedStratumSummary {
        diagnostics: RootStratifiedCandidatePoolStratumDiagnostics {
            id,
            input_positive_roots,
            candidates_per_positive_root,
            generated_candidates: candidates.len(),
            roots_with_positive_candidates,
            minimum_positive_candidates_per_root,
            maximum_positive_candidates_per_root,
            minimum_within_root_candidate_effective_sample_size,
            median_within_root_candidate_effective_sample_size,
            maximum_within_root_candidate_weight,
            roots_with_maximum_candidate_weight_at_least_half,
            first_split_log_predictive_mass,
            second_split_log_predictive_mass,
            absolute_split_log_predictive_mass_difference,
            split_root_total_variation,
        },
        first_root_log_masses,
        second_root_log_masses,
    })
}

fn persistent_twist_population_diagnostics(
    twisted_log_weights: &[f64],
    log_potentials: &[f64],
    root_ids: &[usize],
    stratum_ids: &[StratumId],
) -> Result<(PersistentTwistPopulationDiagnostics, Vec<f64>, f64), SmcError> {
    if twisted_log_weights.len() != log_potentials.len()
        || twisted_log_weights.len() != root_ids.len()
        || twisted_log_weights.len() != stratum_ids.len()
        || log_potentials.iter().any(|value| !value.is_finite())
    {
        return Err(SmcError::InvalidWeights);
    }
    let positive_particles = twisted_log_weights
        .iter()
        .filter(|weight| weight.is_finite())
        .count();
    if positive_particles == 0 {
        return Err(SmcError::AllParticlesRejected);
    }
    let minimum_log_potential = twisted_log_weights
        .iter()
        .zip(log_potentials)
        .filter(|(weight, _)| weight.is_finite())
        .map(|(_, potential)| *potential)
        .fold(f64::INFINITY, f64::min);
    let maximum_log_potential = twisted_log_weights
        .iter()
        .zip(log_potentials)
        .filter(|(weight, _)| weight.is_finite())
        .map(|(_, potential)| *potential)
        .fold(f64::NEG_INFINITY, f64::max);
    let raw_untwisted_log_weights = twisted_log_weights
        .iter()
        .zip(log_potentials)
        .map(|(&weight, &potential)| {
            if weight == f64::NEG_INFINITY {
                f64::NEG_INFINITY
            } else {
                weight - potential
            }
        })
        .collect::<Vec<_>>();
    let (untwisted_log_weights, log_implied_untwist_correction) =
        normalize_log_weights(&raw_untwisted_log_weights)?;
    let twisted = weight_diagnostics(twisted_log_weights, root_ids, stratum_ids)?;
    let untwisted = weight_diagnostics(&untwisted_log_weights, root_ids, stratum_ids)?;
    let diagnostics = PersistentTwistPopulationDiagnostics {
        positive_particles,
        minimum_log_potential,
        maximum_log_potential,
        twisted_effective_sample_size: effective_sample_size(twisted_log_weights)?,
        twisted_maximum_particle_weight: twisted.maximum_normalized_weight,
        twisted_distinct_positive_roots: twisted.distinct_root_ancestors,
        twisted_root_effective_sample_size: twisted.root_effective_sample_size,
        twisted_maximum_root_weight: twisted.maximum_root_weight,
        twisted_strata: twisted.strata,
        log_implied_untwist_correction,
        implied_untwisted_effective_sample_size: effective_sample_size(&untwisted_log_weights)?,
        implied_untwisted_maximum_particle_weight: untwisted.maximum_normalized_weight,
        implied_untwisted_distinct_positive_roots: untwisted.distinct_root_ancestors,
        implied_untwisted_root_effective_sample_size: untwisted.root_effective_sample_size,
        implied_untwisted_maximum_root_weight: untwisted.maximum_root_weight,
        implied_untwisted_strata: untwisted.strata,
    };
    Ok((
        diagnostics,
        untwisted_log_weights,
        log_implied_untwist_correction,
    ))
}

#[allow(clippy::too_many_arguments)]
fn run_stratified_global_candidate_pool_epoch<M, F, A>(
    input: &EpochInput<'_, M>,
    allocations: &[StratumAllocation],
    candidate_allocation: CandidatePoolAllocation,
    target_time_s: f64,
    source_auxiliary: &[A],
    random_domain: CandidatePoolRandomDomain,
    selection_guide: Option<&SelectionGuideScorer<'_, M::State>>,
    score_candidate: F,
) -> Result<CandidatePoolEpoch<M::State, A>, SmcError>
where
    M: ParticleModel,
    A: Clone + Send + Sync,
    F: Fn(usize, &M::State, &mut ChaCha8Rng) -> Result<(M::State, f64, f64, A), SmcError> + Sync,
{
    candidate_allocation.validate()?;
    let EpochInput {
        model,
        states,
        log_weights,
        root_ids,
        stratum_ids,
        epoch,
        config,
        resampling_policy,
        retain_zero_mass_strata,
        ..
    } = input;
    if source_auxiliary.len() != states.len() || !target_time_s.is_finite() {
        return Err(SmcError::InvalidConfiguration(
            "candidate-pool auxiliary state is internally inconsistent",
        ));
    }
    let sources = ensure_allocation(allocations, stratum_ids)?;
    let mut output_states = Vec::with_capacity(states.len());
    let mut output_raw_log_measures = Vec::with_capacity(states.len());
    let mut output_roots = Vec::with_capacity(states.len());
    let mut output_strata = Vec::with_capacity(states.len());
    let mut output_ancestors = Vec::with_capacity(states.len());
    let mut output_auxiliary = Vec::with_capacity(states.len());
    let mut stratum_diagnostics = Vec::with_capacity(allocations.len());
    let mut root_stratified_summaries = Vec::new();
    let mut configured_candidate_offset = 0usize;
    let mut output_slot = 0usize;

    for allocation in allocations {
        let source_indices = &sources[&allocation.id];
        let input_positive_roots = source_indices
            .iter()
            .filter(|&&index| log_weights[index].is_finite())
            .map(|&index| (root_ids[index], ()))
            .collect::<BTreeMap<_, ()>>()
            .len();
        let configured_candidates = match candidate_allocation {
            CandidatePoolAllocation::PerParticle(candidates_per_particle) => {
                allocation.particles.checked_mul(candidates_per_particle)
            }
            CandidatePoolAllocation::PerPositiveRoot(candidates_per_positive_root) => {
                input_positive_roots.checked_mul(candidates_per_positive_root)
            }
        }
        .ok_or(SmcError::InvalidConfiguration(
            "global transition-pool candidate count overflowed",
        ))?;
        let next_candidate_offset = configured_candidate_offset
            .checked_add(configured_candidates)
            .ok_or(SmcError::InvalidConfiguration(
                "global transition-pool candidate count overflowed",
            ))?;
        let source_log_measures = source_indices
            .iter()
            .map(|&index| log_weights[index])
            .collect::<Vec<_>>();
        let stratum_was_already_extinct = source_log_measures
            .iter()
            .all(|value| *value == f64::NEG_INFINITY);
        if stratum_was_already_extinct && *retain_zero_mass_strata {
            for &parent in source_indices {
                output_states.push(states[parent].clone());
                output_raw_log_measures.push(f64::NEG_INFINITY);
                output_roots.push(root_ids[parent]);
                output_strata.push(allocation.id);
                output_ancestors.push(parent);
                output_auxiliary.push(source_auxiliary[parent].clone());
                output_slot += 1;
            }
            stratum_diagnostics.push(GlobalTransitionPoolStratumDiagnostics {
                id: allocation.id,
                input_particles: allocation.particles,
                configured_candidates,
                generated_candidates: 0,
                input_positive_roots: 0,
                sampled_ancestor_roots: 0,
                positive_candidates: 0,
                estimated_log_predictive_mass: None,
                candidate_posterior_mass: 0.0,
                candidate_log_posterior_mass: None,
                conditional_candidate_effective_sample_size: 0.0,
                conditional_maximum_candidate_weight: 0.0,
                distinct_positive_candidate_roots: 0,
                conditional_candidate_root_effective_sample_size: 0.0,
                conditional_maximum_candidate_root_weight: 0.0,
                output_posterior_mass: 0.0,
                output_log_posterior_mass: None,
                ancestor_selection_guide: None,
                output_selection_guide: None,
            });
            if let CandidatePoolAllocation::PerPositiveRoot(candidates_per_positive_root) =
                candidate_allocation
            {
                root_stratified_summaries.push(root_stratified_stratum_summary::<M::State, A>(
                    allocation.id,
                    0,
                    candidates_per_positive_root,
                    &[],
                )?);
            }
            configured_candidate_offset = next_candidate_offset;
            continue;
        }

        let (conditional_source_log_weights, _) = normalize_log_weights(&source_log_measures)
            .map_err(|error| match error {
                SmcError::AllParticlesRejected => SmcError::StratumRejected(allocation.id),
                other => other,
            })?;
        let source_roots = source_indices
            .iter()
            .map(|&index| root_ids[index])
            .collect::<Vec<_>>();
        debug_assert_eq!(
            input_positive_roots,
            conditional_source_log_weights
                .iter()
                .zip(&source_roots)
                .filter(|(weight, _)| weight.is_finite())
                .map(|(_, root)| (*root, ()))
                .collect::<BTreeMap<_, ()>>()
                .len()
        );
        let (candidate_results, ancestor_selection_guide) = match candidate_allocation {
            CandidatePoolAllocation::PerParticle(_) => {
                // Keep the legacy proposal, keyed streams, arithmetic order,
                // and candidate order unchanged.
                let source_states = source_indices
                    .iter()
                    .map(|&index| &states[index])
                    .collect::<Vec<_>>();
                let source_selection_guide =
                    selection_guide.map(|guide| move |state: &&M::State| guide(*state));
                let (ancestor_proposal_log_probabilities, ancestor_selection_guide) =
                    selection_guided_root_log_probabilities(
                        &conditional_source_log_weights,
                        &source_states,
                        &source_roots,
                        *resampling_policy,
                        source_selection_guide
                            .as_ref()
                            .map(|guide| guide as &SelectionGuideScorer<'_, &M::State>),
                    )
                    .map_err(|error| match error {
                        SmcError::AllParticlesRejected => SmcError::StratumRejected(allocation.id),
                        other => other,
                    })?;
                let ancestor_proposal_probabilities = ancestor_proposal_log_probabilities
                    .iter()
                    .map(|value| value.exp())
                    .collect::<Vec<_>>();
                let mut ancestor_rng = rng_for(
                    config.seed,
                    random_domain.ancestor_purpose(),
                    *epoch,
                    configured_candidate_offset,
                    random_domain.substream(allocation.id),
                );
                let first_ancestor_offset =
                    ancestor_rng.gen::<f64>() / configured_candidates as f64;
                let local_ancestors = systematic_resample_n(
                    &ancestor_proposal_probabilities,
                    configured_candidates,
                    first_ancestor_offset,
                )?;
                let assignments = local_ancestors
                    .iter()
                    .enumerate()
                    .map(|(candidate, &local_ancestor)| {
                        (
                            configured_candidate_offset + candidate,
                            source_indices[local_ancestor],
                            ancestor_proposal_log_probabilities[local_ancestor],
                        )
                    })
                    .collect::<Vec<_>>();
                let candidates = assignments
                    .par_iter()
                    .map(|&(candidate_slot, ancestor, log_ancestor_proposal)| {
                        let mut rng = rng_for(
                            config.seed,
                            random_domain.transition_purpose(),
                            *epoch,
                            candidate_slot,
                            random_domain.substream(allocation.id),
                        );
                        let (state, log_prior_over_proposal, log_target_ratio, carried_auxiliary) =
                            score_candidate(ancestor, &states[ancestor], &mut rng)?;
                        if !log_prior_over_proposal.is_finite()
                            || !(log_target_ratio.is_finite()
                                || log_target_ratio == f64::NEG_INFINITY)
                        {
                            return Err(SmcError::InvalidWeights);
                        }
                        if model.stratum(&state) != allocation.id {
                            return Err(SmcError::StratumMismatch);
                        }
                        Ok(TransitionPoolCandidate {
                            state,
                            log_measure: log_weights[ancestor] - log_ancestor_proposal
                                + log_prior_over_proposal
                                + log_target_ratio
                                - (configured_candidates as f64).ln(),
                            ancestor_index: ancestor,
                            root_id: root_ids[ancestor],
                            root_replicate: None,
                            carried_auxiliary,
                        })
                    })
                    .collect::<Vec<Result<_, SmcError>>>()
                    .into_iter()
                    .collect::<Result<Vec<_>, _>>()?;
                (candidates, ancestor_selection_guide)
            }
            CandidatePoolAllocation::PerPositiveRoot(candidates_per_positive_root) => {
                let mut root_members = BTreeMap::<usize, Vec<usize>>::new();
                for (local, (&log_weight, &root)) in conditional_source_log_weights
                    .iter()
                    .zip(&source_roots)
                    .enumerate()
                {
                    if log_weight.is_finite() {
                        root_members.entry(root).or_default().push(local);
                    }
                }
                let mut assignments = Vec::with_capacity(configured_candidates);
                for (&root, members) in &root_members {
                    let root_log_weights = members
                        .iter()
                        .map(|&local| conditional_source_log_weights[local])
                        .collect::<Vec<_>>();
                    let (within_root_log_probabilities, _) =
                        normalize_log_weights(&root_log_weights)?;
                    let within_root_probabilities = within_root_log_probabilities
                        .iter()
                        .map(|value| value.exp())
                        .collect::<Vec<_>>();
                    for replicate in 0..candidates_per_positive_root {
                        let coordinates =
                            random_domain.root_coordinates(allocation.id, root, replicate);
                        let mut ancestor_rng = rng_for_coordinates(
                            config.seed,
                            random_domain.root_ancestor_purpose(),
                            *epoch,
                            &coordinates,
                        );
                        let selected = systematic_resample_n(
                            &within_root_probabilities,
                            1,
                            ancestor_rng.gen::<f64>(),
                        )?[0];
                        let local_ancestor = members[selected];
                        assignments.push((
                            root,
                            replicate,
                            source_indices[local_ancestor],
                            within_root_log_probabilities[selected],
                        ));
                    }
                }
                debug_assert_eq!(assignments.len(), configured_candidates);
                let candidates = assignments
                    .par_iter()
                    .map(
                        |&(root, replicate, ancestor, log_within_root_probability)| {
                            let coordinates =
                                random_domain.root_coordinates(allocation.id, root, replicate);
                            let mut rng = rng_for_coordinates(
                                config.seed,
                                random_domain.root_transition_purpose(),
                                *epoch,
                                &coordinates,
                            );
                            let (
                                state,
                                log_prior_over_proposal,
                                log_target_ratio,
                                carried_auxiliary,
                            ) = score_candidate(ancestor, &states[ancestor], &mut rng)?;
                            if !log_prior_over_proposal.is_finite()
                                || !(log_target_ratio.is_finite()
                                    || log_target_ratio == f64::NEG_INFINITY)
                            {
                                return Err(SmcError::InvalidWeights);
                            }
                            if model.stratum(&state) != allocation.id {
                                return Err(SmcError::StratumMismatch);
                            }
                            Ok(TransitionPoolCandidate {
                                state,
                                log_measure: log_weights[ancestor] - log_within_root_probability
                                    + log_prior_over_proposal
                                    + log_target_ratio
                                    - (candidates_per_positive_root as f64).ln(),
                                ancestor_index: ancestor,
                                root_id: root,
                                root_replicate: Some(replicate),
                                carried_auxiliary,
                            })
                        },
                    )
                    .collect::<Vec<Result<_, SmcError>>>()
                    .into_iter()
                    .collect::<Result<Vec<_>, _>>()?;
                (candidates, None)
            }
        };
        let candidate_log_measures = candidate_results
            .iter()
            .map(|candidate| candidate.log_measure)
            .collect::<Vec<_>>();
        let candidate_roots = candidate_results
            .iter()
            .map(|candidate| candidate.root_id)
            .collect::<Vec<_>>();
        if let CandidatePoolAllocation::PerPositiveRoot(candidates_per_positive_root) =
            candidate_allocation
        {
            root_stratified_summaries.push(root_stratified_stratum_summary(
                allocation.id,
                input_positive_roots,
                candidates_per_positive_root,
                &candidate_results,
            )?);
        }
        let sampled_ancestor_roots = candidate_roots
            .iter()
            .copied()
            .map(|root| (root, ()))
            .collect::<BTreeMap<_, _>>()
            .len();
        let estimated_log_predictive_mass = match logsumexp(&candidate_log_measures) {
            Ok(value) => Some(value),
            Err(SmcError::AllParticlesRejected) => None,
            Err(error) => return Err(error),
        };
        if let Some(log_predictive_mass) = estimated_log_predictive_mass {
            let (
                positive_candidates,
                candidate_ess,
                maximum_candidate_weight,
                distinct_candidate_roots,
                candidate_root_ess,
                maximum_candidate_root_weight,
            ) = conditional_support_diagnostics(&candidate_log_measures, &candidate_roots)?;
            let conditional_candidate_log_weights = candidate_log_measures
                .iter()
                .map(|value| value - log_predictive_mass)
                .collect::<Vec<_>>();
            let candidate_states = candidate_results
                .iter()
                .map(|candidate| &candidate.state)
                .collect::<Vec<_>>();
            let candidate_selection_guide =
                selection_guide.map(|guide| move |state: &&M::State| guide(*state));
            let (output_proposal_log_probabilities, output_selection_guide) =
                selection_guided_root_log_probabilities(
                    &conditional_candidate_log_weights,
                    &candidate_states,
                    &candidate_roots,
                    *resampling_policy,
                    candidate_selection_guide
                        .as_ref()
                        .map(|guide| guide as &SelectionGuideScorer<'_, &M::State>),
                )?;
            let output_proposal_probabilities = output_proposal_log_probabilities
                .iter()
                .map(|value| value.exp())
                .collect::<Vec<_>>();
            let output_purpose = match candidate_allocation {
                CandidatePoolAllocation::PerParticle(_) => random_domain.output_purpose(),
                CandidatePoolAllocation::PerPositiveRoot(_) => random_domain.root_output_purpose(),
            };
            let mut output_rng = rng_for(
                config.seed,
                output_purpose,
                *epoch,
                output_slot,
                random_domain.substream(allocation.id),
            );
            let first_output_offset = output_rng.gen::<f64>() / allocation.particles as f64;
            let output_candidates = systematic_resample_n(
                &output_proposal_probabilities,
                allocation.particles,
                first_output_offset,
            )?;
            for candidate_index in output_candidates {
                let candidate = &candidate_results[candidate_index];
                output_states.push(candidate.state.clone());
                output_raw_log_measures.push(
                    log_predictive_mass - (allocation.particles as f64).ln()
                        + conditional_candidate_log_weights[candidate_index]
                        - output_proposal_log_probabilities[candidate_index],
                );
                output_roots.push(candidate.root_id);
                output_strata.push(allocation.id);
                output_ancestors.push(candidate.ancestor_index);
                output_auxiliary.push(candidate.carried_auxiliary.clone());
                output_slot += 1;
            }
            stratum_diagnostics.push(GlobalTransitionPoolStratumDiagnostics {
                id: allocation.id,
                input_particles: allocation.particles,
                configured_candidates,
                generated_candidates: candidate_results.len(),
                input_positive_roots,
                sampled_ancestor_roots,
                positive_candidates,
                estimated_log_predictive_mass,
                candidate_posterior_mass: 0.0,
                candidate_log_posterior_mass: None,
                conditional_candidate_effective_sample_size: candidate_ess,
                conditional_maximum_candidate_weight: maximum_candidate_weight,
                distinct_positive_candidate_roots: distinct_candidate_roots,
                conditional_candidate_root_effective_sample_size: candidate_root_ess,
                conditional_maximum_candidate_root_weight: maximum_candidate_root_weight,
                output_posterior_mass: 0.0,
                output_log_posterior_mass: None,
                ancestor_selection_guide,
                output_selection_guide,
            });
        } else {
            for local in 0..allocation.particles {
                let candidate = &candidate_results[local % candidate_results.len()];
                output_states.push(candidate.state.clone());
                output_raw_log_measures.push(f64::NEG_INFINITY);
                output_roots.push(candidate.root_id);
                output_strata.push(allocation.id);
                output_ancestors.push(candidate.ancestor_index);
                output_auxiliary.push(candidate.carried_auxiliary.clone());
                output_slot += 1;
            }
            stratum_diagnostics.push(GlobalTransitionPoolStratumDiagnostics {
                id: allocation.id,
                input_particles: allocation.particles,
                configured_candidates,
                generated_candidates: candidate_results.len(),
                input_positive_roots,
                sampled_ancestor_roots,
                positive_candidates: 0,
                estimated_log_predictive_mass: None,
                candidate_posterior_mass: 0.0,
                candidate_log_posterior_mass: None,
                conditional_candidate_effective_sample_size: 0.0,
                conditional_maximum_candidate_weight: 0.0,
                distinct_positive_candidate_roots: 0,
                conditional_candidate_root_effective_sample_size: 0.0,
                conditional_maximum_candidate_root_weight: 0.0,
                output_posterior_mass: 0.0,
                output_log_posterior_mass: None,
                ancestor_selection_guide,
                output_selection_guide: None,
            });
        }
        configured_candidate_offset = next_candidate_offset;
    }

    let finite_predictive_masses = stratum_diagnostics
        .iter()
        .filter_map(|diagnostics| diagnostics.estimated_log_predictive_mass)
        .collect::<Vec<_>>();
    if finite_predictive_masses.is_empty() {
        return Err(SmcError::AllParticlesRejected);
    }
    let candidate_log_evidence_increment = logsumexp(&finite_predictive_masses)?;
    let mut candidate_sum_squares = 0.0;
    let mut candidate_root_sum_squares = 0.0;
    let mut maximum_candidate_weight = 0.0_f64;
    let mut maximum_candidate_root_weight = 0.0_f64;
    let mut distinct_positive_candidate_roots = 0usize;
    for diagnostics in &mut stratum_diagnostics {
        let Some(log_mass) = diagnostics.estimated_log_predictive_mass else {
            continue;
        };
        let candidate_log_posterior_mass = log_mass - candidate_log_evidence_increment;
        let candidate_posterior_mass = candidate_log_posterior_mass.exp();
        diagnostics.candidate_posterior_mass = candidate_posterior_mass;
        diagnostics.candidate_log_posterior_mass = Some(candidate_log_posterior_mass);
        candidate_sum_squares += candidate_posterior_mass.powi(2)
            / diagnostics.conditional_candidate_effective_sample_size;
        candidate_root_sum_squares += candidate_posterior_mass.powi(2)
            / diagnostics.conditional_candidate_root_effective_sample_size;
        maximum_candidate_weight = maximum_candidate_weight
            .max(candidate_posterior_mass * diagnostics.conditional_maximum_candidate_weight);
        maximum_candidate_root_weight = maximum_candidate_root_weight
            .max(candidate_posterior_mass * diagnostics.conditional_maximum_candidate_root_weight);
        distinct_positive_candidate_roots += diagnostics.distinct_positive_candidate_roots;
    }

    let (normalized_output_log_weights, realized_log_evidence_increment) =
        normalize_log_weights(&output_raw_log_measures)?;
    let posterior_ess = effective_sample_size(&normalized_output_log_weights)?;
    let output_diagnostics = weight_diagnostics(
        &normalized_output_log_weights,
        &output_roots,
        &output_strata,
    )?;
    for diagnostics in &mut stratum_diagnostics {
        let output = output_diagnostics
            .strata
            .iter()
            .find(|entry| entry.id == diagnostics.id)
            .ok_or(SmcError::StratumMismatch)?;
        diagnostics.output_posterior_mass = output.posterior_mass;
        diagnostics.output_log_posterior_mass = output.log_posterior_mass;
    }
    let configured_candidates = stratum_diagnostics
        .iter()
        .try_fold(0usize, |total, diagnostics| {
            total.checked_add(diagnostics.configured_candidates)
        })
        .ok_or(SmcError::InvalidConfiguration(
            "global transition-pool candidate count overflowed",
        ))?;
    let generated_candidates = stratum_diagnostics
        .iter()
        .map(|diagnostics| diagnostics.generated_candidates)
        .sum();
    let positive_candidates = stratum_diagnostics
        .iter()
        .map(|diagnostics| diagnostics.positive_candidates)
        .sum();
    let root_stratified_checkpoint = match candidate_allocation {
        CandidatePoolAllocation::PerParticle(_) => None,
        CandidatePoolAllocation::PerPositiveRoot(candidates_per_positive_root) => {
            let mut first_root_log_masses = BTreeMap::<usize, f64>::new();
            let mut second_root_log_masses = BTreeMap::<usize, f64>::new();
            for summary in &root_stratified_summaries {
                for (&root, &log_mass) in &summary.first_root_log_masses {
                    first_root_log_masses
                        .entry(root)
                        .and_modify(|current| *current = log_add_exp(*current, log_mass))
                        .or_insert(log_mass);
                }
                for (&root, &log_mass) in &summary.second_root_log_masses {
                    second_root_log_masses
                        .entry(root)
                        .and_modify(|current| *current = log_add_exp(*current, log_mass))
                        .or_insert(log_mass);
                }
            }
            let first_split_candidate_log_evidence_increment =
                optional_logsumexp(first_root_log_masses.values().copied())?;
            let second_split_candidate_log_evidence_increment =
                optional_logsumexp(second_root_log_masses.values().copied())?;
            let absolute_split_log_evidence_difference =
                first_split_candidate_log_evidence_increment
                    .zip(second_split_candidate_log_evidence_increment)
                    .map(|(first, second)| (first - second).abs());
            let split_candidate_root_total_variation =
                root_distribution_total_variation(&first_root_log_masses, &second_root_log_masses)?;
            Some(RootStratifiedCandidatePoolCheckpoint {
                observation_index: *epoch,
                observation_time_s: target_time_s,
                location: random_domain.root_location(),
                candidates_per_positive_root,
                configured_candidates,
                generated_candidates,
                first_split_candidate_log_evidence_increment,
                second_split_candidate_log_evidence_increment,
                absolute_split_log_evidence_difference,
                split_candidate_root_total_variation,
                strata: root_stratified_summaries
                    .into_iter()
                    .map(|summary| summary.diagnostics)
                    .collect(),
            })
        }
    };
    Ok(CandidatePoolEpoch {
        epoch: StratifiedEpoch {
            states: output_states,
            log_weights: normalized_output_log_weights,
            ancestor_indices: output_ancestors,
            stratum_ids: output_strata,
            guide_ess: None,
            posterior_ess,
            ancestor_resampled: true,
            log_evidence_increment: realized_log_evidence_increment,
            transition_pool_checkpoint: None,
            root_stratified_candidate_pool_checkpoints: Vec::new(),
            intermediate_potential_checkpoint: None,
            persistent_twist_log_potentials: None,
        },
        carried_auxiliary: output_auxiliary,
        checkpoint: GlobalTransitionPoolCheckpoint {
            observation_index: *epoch,
            observation_time_s: target_time_s,
            candidates_per_particle: candidate_allocation.legacy_candidates_per_particle(),
            configured_candidates,
            generated_candidates,
            positive_candidates,
            candidate_log_evidence_increment,
            output_resampling_log_correction: realized_log_evidence_increment
                - candidate_log_evidence_increment,
            realized_log_evidence_increment,
            candidate_effective_sample_size: 1.0 / candidate_sum_squares,
            maximum_candidate_weight,
            distinct_positive_candidate_roots,
            candidate_root_effective_sample_size: 1.0 / candidate_root_sum_squares,
            maximum_candidate_root_weight,
            strata: stratum_diagnostics,
        },
        root_stratified_checkpoint,
    })
}

fn run_stratified_global_transition_pool_epoch<M: ParticleModel>(
    input: &EpochInput<'_, M>,
    allocations: &[StratumAllocation],
    candidates_per_particle: usize,
    selection_guide: Option<&SelectionGuideScorer<'_, M::State>>,
) -> Result<StratifiedEpoch<M::State>, SmcError> {
    let source_auxiliary = vec![(); input.states.len()];
    let pooled = run_stratified_global_candidate_pool_epoch(
        input,
        allocations,
        CandidatePoolAllocation::PerParticle(candidates_per_particle),
        input.model.observation_time_s(input.observation),
        &source_auxiliary,
        CandidatePoolRandomDomain::EndpointObservation,
        selection_guide,
        |_, state, rng| {
            let mut proposal = input
                .model
                .propose(state, input.observation, input.elapsed_seconds, rng)
                .map_err(model_error)?;
            if !proposal.log_prior_over_proposal.is_finite() {
                return Err(SmcError::InvalidWeights);
            }
            let likelihood = input
                .model
                .observe(&mut proposal.state, input.observation)
                .map_err(model_error)?;
            if !(likelihood.is_finite() || likelihood == f64::NEG_INFINITY) {
                return Err(SmcError::InvalidWeights);
            }
            Ok((
                proposal.state,
                proposal.log_prior_over_proposal,
                likelihood,
                (),
            ))
        },
    )?;
    let mut epoch = pooled.epoch;
    epoch.transition_pool_checkpoint = Some(pooled.checkpoint);
    debug_assert!(pooled.root_stratified_checkpoint.is_none());
    Ok(epoch)
}

fn run_stratified_root_transition_pool_epoch<M: ParticleModel>(
    input: &EpochInput<'_, M>,
    allocations: &[StratumAllocation],
    candidates_per_positive_root: usize,
) -> Result<StratifiedEpoch<M::State>, SmcError> {
    let source_auxiliary = vec![(); input.states.len()];
    let pooled = run_stratified_global_candidate_pool_epoch(
        input,
        allocations,
        CandidatePoolAllocation::PerPositiveRoot(candidates_per_positive_root),
        input.model.observation_time_s(input.observation),
        &source_auxiliary,
        CandidatePoolRandomDomain::EndpointObservation,
        None,
        |_, state, rng| {
            let mut proposal = input
                .model
                .propose(state, input.observation, input.elapsed_seconds, rng)
                .map_err(model_error)?;
            if !proposal.log_prior_over_proposal.is_finite() {
                return Err(SmcError::InvalidWeights);
            }
            let likelihood = input
                .model
                .observe(&mut proposal.state, input.observation)
                .map_err(model_error)?;
            if !(likelihood.is_finite() || likelihood == f64::NEG_INFINITY) {
                return Err(SmcError::InvalidWeights);
            }
            Ok((
                proposal.state,
                proposal.log_prior_over_proposal,
                likelihood,
                (),
            ))
        },
    )?;
    let CandidatePoolEpoch {
        mut epoch,
        checkpoint,
        root_stratified_checkpoint,
        ..
    } = pooled;
    epoch.transition_pool_checkpoint = Some(checkpoint);
    epoch
        .root_stratified_candidate_pool_checkpoints
        .push(
            root_stratified_checkpoint.ok_or(SmcError::InvalidConfiguration(
                "root-stratified transition pool omitted its allocation diagnostics",
            ))?,
        );
    Ok(epoch)
}

fn persistent_twist_source_log_potentials<S>(
    particle_count: usize,
    twist: &PersistentTwistEpochInput<'_, S>,
) -> Result<Vec<f64>, SmcError> {
    let source = match twist.phase {
        PersistentTwistPhase::Activate => {
            if twist.input_log_potentials.is_some() {
                return Err(SmcError::InvalidConfiguration(
                    "persistent-twist activation must use the identity denominator",
                ));
            }
            vec![0.0; particle_count]
        }
        PersistentTwistPhase::Continue | PersistentTwistPhase::Finalize => twist
            .input_log_potentials
            .ok_or(SmcError::InvalidConfiguration(
                "an active persistent twist lost its per-lineage potential",
            ))?
            .to_vec(),
    };
    if source.len() != particle_count || source.iter().any(|value| !value.is_finite()) {
        return Err(SmcError::InvalidConfiguration(
            "persistent-twist lineage potentials are internally inconsistent",
        ));
    }
    Ok(source)
}

fn run_stratified_persistent_twist_epoch<M: ParticleModel>(
    input: &EpochInput<'_, M>,
    allocations: &[StratumAllocation],
    twist: &PersistentTwistEpochInput<'_, M::State>,
) -> Result<StratifiedEpoch<M::State>, SmcError> {
    let source_log_potentials = persistent_twist_source_log_potentials(input.states.len(), twist)?;
    let pooled = run_stratified_global_candidate_pool_epoch(
        input,
        allocations,
        CandidatePoolAllocation::PerParticle(1),
        input.model.observation_time_s(input.observation),
        &source_log_potentials,
        CandidatePoolRandomDomain::EndpointObservation,
        None,
        |ancestor, state, rng| {
            let mut proposal = input
                .model
                .propose(state, input.observation, input.elapsed_seconds, rng)
                .map_err(model_error)?;
            if !proposal.log_prior_over_proposal.is_finite() {
                return Err(SmcError::InvalidWeights);
            }
            let likelihood = input
                .model
                .observe(&mut proposal.state, input.observation)
                .map_err(model_error)?;
            if !(likelihood.is_finite() || likelihood == f64::NEG_INFINITY) {
                return Err(SmcError::InvalidWeights);
            }
            let log_potential = (twist.score)(&proposal.state)?;
            if !log_potential.is_finite() {
                return Err(SmcError::InvalidWeights);
            }
            let log_twist_ratio = log_potential - source_log_potentials[ancestor];
            if !log_twist_ratio.is_finite() {
                return Err(SmcError::InvalidWeights);
            }
            Ok((
                proposal.state,
                proposal.log_prior_over_proposal,
                likelihood + log_twist_ratio,
                log_potential,
            ))
        },
    )?;
    let CandidatePoolEpoch {
        mut epoch,
        carried_auxiliary,
        checkpoint,
        root_stratified_checkpoint,
    } = pooled;
    debug_assert!(root_stratified_checkpoint.is_none());
    epoch.transition_pool_checkpoint = Some(checkpoint);
    epoch.persistent_twist_log_potentials = Some(carried_auxiliary);
    Ok(epoch)
}

#[derive(Debug, Clone)]
struct IntermediatePotentialLineage<C> {
    log_potential: f64,
    log_twist_potential: f64,
    context: C,
}

struct CandidateAllocatedIntermediatePotentialBridgePoint<'a, P> {
    point: &'a P,
    candidate_allocation: CandidatePoolAllocation,
}

#[derive(Debug, Clone, Copy)]
enum IntermediateEndpointCandidateAllocation {
    LegacySingle,
    Pool(CandidatePoolAllocation),
}

impl IntermediateEndpointCandidateAllocation {
    fn pool_allocation(self) -> CandidatePoolAllocation {
        match self {
            Self::LegacySingle => CandidatePoolAllocation::PerParticle(1),
            Self::Pool(allocation) => allocation,
        }
    }
}

#[allow(clippy::too_many_arguments)]
fn run_stratified_intermediate_potential_epoch<M, B>(
    input: &EpochInput<'_, M>,
    allocations: &[StratumAllocation],
    bridge: &B,
    points: &[CandidateAllocatedIntermediatePotentialBridgePoint<'_, B::Point>],
    endpoint_candidate_allocation: IntermediateEndpointCandidateAllocation,
    selection_guide: Option<&SelectionGuideScorer<'_, M::State>>,
    persistent_twist: Option<&PersistentTwistEpochInput<'_, M::State>>,
) -> Result<StratifiedEpoch<M::State>, SmcError>
where
    M: ParticleModel,
    B: IntermediatePotentialBridge<M>,
{
    if points.is_empty() {
        return Err(SmcError::InvalidConfiguration(
            "an intermediate-potential bridge must contain at least one point",
        ));
    }
    endpoint_candidate_allocation.pool_allocation().validate()?;
    if selection_guide.is_some() && persistent_twist.is_some() {
        return Err(SmcError::InvalidConfiguration(
            "a local selection guide and persistent twist cannot be combined",
        ));
    }
    let input_log_twist_potentials = persistent_twist
        .map(|twist| persistent_twist_source_log_potentials(input.states.len(), twist))
        .transpose()?;
    let endpoint_time_s = input.model.observation_time_s(input.observation);
    let interval_start_time_s = endpoint_time_s - input.elapsed_seconds;
    let mut prior_point_time_s = interval_start_time_s;
    for point in points {
        let point_time_s = bridge.point_time_s(point.point);
        if !point_time_s.is_finite()
            || point_time_s <= prior_point_time_s
            || point_time_s >= endpoint_time_s
        {
            return Err(SmcError::InvalidConfiguration(
                "bridge points must be strictly ordered inside their observation interval and use positive candidate counts",
            ));
        }
        point.candidate_allocation.validate()?;
        prior_point_time_s = point_time_s;
    }

    let mut states = input.states.to_vec();
    let mut log_weights = input.log_weights.to_vec();
    let mut root_ids = input.root_ids.to_vec();
    let mut stratum_ids = input.stratum_ids.to_vec();
    let initialized_lineages = states
        .par_iter()
        .zip(log_weights.par_iter())
        .enumerate()
        .map(|(particle, (state, &log_weight))| {
            if log_weight == f64::NEG_INFINITY {
                Ok(None)
            } else {
                bridge
                    .begin_interval(input.model, state, input.observation)
                    .map(|context| {
                        Some(IntermediatePotentialLineage {
                            log_potential: 0.0,
                            log_twist_potential: input_log_twist_potentials
                                .as_ref()
                                .map_or(0.0, |values| values[particle]),
                            context,
                        })
                    })
                    .map_err(model_error)
            }
        })
        .collect::<Vec<Result<_, SmcError>>>();
    let mut carried_lineages = initialized_lineages
        .into_iter()
        .collect::<Result<Vec<_>, _>>()?;
    let mut ancestors_to_epoch_input = (0..states.len()).collect::<Vec<_>>();
    let mut point_checkpoints = Vec::with_capacity(points.len());
    let mut root_stratified_candidate_pool_checkpoints = Vec::new();
    let mut realized_log_evidence_increment = 0.0;
    let mut current_time_s = interval_start_time_s;

    for (point_index, point) in points.iter().enumerate() {
        let point_time_s = bridge.point_time_s(point.point);
        let elapsed_seconds = point_time_s - current_time_s;
        let stage_input = EpochInput {
            model: input.model,
            states: &states,
            log_weights: &log_weights,
            root_ids: &root_ids,
            stratum_ids: &stratum_ids,
            observation: input.observation,
            elapsed_seconds,
            epoch: input.epoch,
            config: input.config,
            resampling_policy: input.resampling_policy,
            retain_zero_mass_strata: true,
        };
        let previous_lineages = &carried_lineages;
        let pooled = run_stratified_global_candidate_pool_epoch(
            &stage_input,
            allocations,
            point.candidate_allocation,
            point_time_s,
            previous_lineages,
            CandidatePoolRandomDomain::IntermediatePotential { point_index },
            selection_guide,
            |ancestor, state, rng| {
                let lineage = previous_lineages[ancestor]
                    .as_ref()
                    .ok_or(SmcError::InvalidAncestry)?;
                let bridged = bridge
                    .propose_to_point(
                        input.model,
                        state,
                        input.observation,
                        point.point,
                        &lineage.context,
                        elapsed_seconds,
                        rng,
                    )
                    .map_err(model_error)?;
                let proposal = bridged.proposal;
                if !proposal.log_prior_over_proposal.is_finite() {
                    return Err(SmcError::InvalidWeights);
                }
                let log_potential = bridge
                    .log_potential(input.model, &proposal.state, input.observation, point.point)
                    .map_err(model_error)?;
                if !log_potential.is_finite() {
                    return Err(SmcError::InvalidWeights);
                }
                let log_potential_ratio = log_potential - lineage.log_potential;
                if !log_potential_ratio.is_finite() {
                    return Err(SmcError::InvalidWeights);
                }
                let log_twist_potential = if let Some(twist) = persistent_twist {
                    (twist.score)(&proposal.state)?
                } else {
                    lineage.log_twist_potential
                };
                if !log_twist_potential.is_finite() {
                    return Err(SmcError::InvalidWeights);
                }
                let log_twist_ratio = log_twist_potential - lineage.log_twist_potential;
                if !log_twist_ratio.is_finite() {
                    return Err(SmcError::InvalidWeights);
                }
                let combined_potential_ratio = if persistent_twist.is_some() {
                    log_potential_ratio + log_twist_ratio
                } else {
                    log_potential_ratio
                };
                Ok((
                    proposal.state,
                    proposal.log_prior_over_proposal,
                    combined_potential_ratio,
                    Some(IntermediatePotentialLineage {
                        log_potential,
                        log_twist_potential,
                        context: bridged.context,
                    }),
                ))
            },
        )?;
        let CandidatePoolEpoch {
            epoch,
            carried_auxiliary: next_lineages,
            checkpoint,
            root_stratified_checkpoint,
        } = pooled;
        if let Some(checkpoint) = root_stratified_checkpoint {
            root_stratified_candidate_pool_checkpoints.push(checkpoint);
        }
        let next_ancestors_to_epoch_input = epoch
            .ancestor_indices
            .iter()
            .map(|&ancestor| ancestors_to_epoch_input[ancestor])
            .collect::<Vec<_>>();
        let next_root_ids = epoch
            .ancestor_indices
            .iter()
            .map(|&ancestor| root_ids[ancestor])
            .collect::<Vec<_>>();
        let output_diagnostics =
            weight_diagnostics(&epoch.log_weights, &next_root_ids, &epoch.stratum_ids)?;
        realized_log_evidence_increment += checkpoint.realized_log_evidence_increment;
        point_checkpoints.push(IntermediatePotentialPointCheckpoint {
            point_index,
            point_time_s,
            elapsed_seconds,
            candidate_pool: checkpoint,
            output_positive_particles: epoch
                .log_weights
                .iter()
                .filter(|weight| weight.is_finite())
                .count(),
            output_effective_sample_size: epoch.posterior_ess,
            output_maximum_particle_weight: output_diagnostics.maximum_normalized_weight,
            output_distinct_positive_roots: output_diagnostics.distinct_root_ancestors,
            output_root_effective_sample_size: output_diagnostics.root_effective_sample_size,
            output_maximum_root_weight: output_diagnostics.maximum_root_weight,
            output_strata: output_diagnostics.strata,
        });
        states = epoch.states;
        log_weights = epoch.log_weights;
        stratum_ids = epoch.stratum_ids;
        root_ids = next_root_ids;
        carried_lineages = next_lineages;
        ancestors_to_epoch_input = next_ancestors_to_epoch_input;
        current_time_s = point_time_s;
    }

    let endpoint_elapsed_seconds = endpoint_time_s - current_time_s;
    let (
        endpoint_states,
        endpoint_log_weights,
        endpoint_stratum_ids,
        endpoint_ancestors,
        endpoint_log_evidence_increment,
        endpoint_candidate_pool,
        endpoint_log_twist_potentials,
    ) = if matches!(
        endpoint_candidate_allocation,
        IntermediateEndpointCandidateAllocation::LegacySingle
    ) && selection_guide.is_none()
        && persistent_twist.is_none()
    {
        // Preserve the legacy bridge endpoint path and RNG domain exactly.
        let proposals = states
            .par_iter()
            .enumerate()
            .map(|(particle, state)| {
                if log_weights[particle] == f64::NEG_INFINITY {
                    return Ok((state.clone(), f64::NEG_INFINITY));
                }
                let mut rng = rng_for(
                    input.config.seed,
                    "stratified-intermediate-potential-endpoint",
                    input.epoch,
                    particle,
                    points.len() as u64,
                );
                let lineage = carried_lineages[particle]
                    .as_ref()
                    .ok_or(SmcError::InvalidAncestry)?;
                let mut proposal = bridge
                    .propose_to_endpoint(
                        input.model,
                        state,
                        input.observation,
                        &lineage.context,
                        endpoint_elapsed_seconds,
                        &mut rng,
                    )
                    .map_err(model_error)?;
                if !proposal.log_prior_over_proposal.is_finite() {
                    return Err(SmcError::InvalidWeights);
                }
                if input.model.stratum(&proposal.state) != stratum_ids[particle] {
                    return Err(SmcError::StratumMismatch);
                }
                let likelihood = input
                    .model
                    .observe(&mut proposal.state, input.observation)
                    .map_err(model_error)?;
                if !(likelihood.is_finite() || likelihood == f64::NEG_INFINITY) {
                    return Err(SmcError::InvalidWeights);
                }
                if input.model.stratum(&proposal.state) != stratum_ids[particle] {
                    return Err(SmcError::StratumMismatch);
                }
                Ok((
                    proposal.state,
                    log_weights[particle] + proposal.log_prior_over_proposal + likelihood
                        - lineage.log_potential,
                ))
            })
            .collect::<Vec<Result<_, SmcError>>>();
        let mut endpoint_states = Vec::with_capacity(states.len());
        let mut endpoint_raw_log_weights = Vec::with_capacity(states.len());
        for proposal in proposals {
            let (state, log_weight) = proposal?;
            endpoint_states.push(state);
            endpoint_raw_log_weights.push(log_weight);
        }
        let (endpoint_log_weights, endpoint_log_evidence_increment) =
            normalize_log_weights(&endpoint_raw_log_weights)?;
        (
            endpoint_states,
            endpoint_log_weights,
            stratum_ids.clone(),
            (0..states.len()).collect::<Vec<_>>(),
            endpoint_log_evidence_increment,
            None,
            None,
        )
    } else {
        let endpoint_input = EpochInput {
            model: input.model,
            states: &states,
            log_weights: &log_weights,
            root_ids: &root_ids,
            stratum_ids: &stratum_ids,
            observation: input.observation,
            elapsed_seconds: endpoint_elapsed_seconds,
            epoch: input.epoch,
            config: input.config,
            resampling_policy: input.resampling_policy,
            retain_zero_mass_strata: true,
        };
        let source_lineages = &carried_lineages;
        let pooled = run_stratified_global_candidate_pool_epoch(
            &endpoint_input,
            allocations,
            endpoint_candidate_allocation.pool_allocation(),
            endpoint_time_s,
            source_lineages,
            CandidatePoolRandomDomain::IntermediatePotentialEndpoint {
                point_count: points.len(),
            },
            selection_guide,
            |ancestor, state, rng| {
                let lineage = source_lineages[ancestor]
                    .as_ref()
                    .ok_or(SmcError::InvalidAncestry)?;
                let mut proposal = bridge
                    .propose_to_endpoint(
                        input.model,
                        state,
                        input.observation,
                        &lineage.context,
                        endpoint_elapsed_seconds,
                        rng,
                    )
                    .map_err(model_error)?;
                if !proposal.log_prior_over_proposal.is_finite() {
                    return Err(SmcError::InvalidWeights);
                }
                let likelihood = input
                    .model
                    .observe(&mut proposal.state, input.observation)
                    .map_err(model_error)?;
                if !(likelihood.is_finite() || likelihood == f64::NEG_INFINITY) {
                    return Err(SmcError::InvalidWeights);
                }
                let log_twist_potential = if let Some(twist) = persistent_twist {
                    (twist.score)(&proposal.state)?
                } else {
                    lineage.log_twist_potential
                };
                if !log_twist_potential.is_finite() {
                    return Err(SmcError::InvalidWeights);
                }
                let log_twist_ratio = log_twist_potential - lineage.log_twist_potential;
                if !log_twist_ratio.is_finite() {
                    return Err(SmcError::InvalidWeights);
                }
                let combined_endpoint_ratio = if persistent_twist.is_some() {
                    likelihood - lineage.log_potential + log_twist_ratio
                } else {
                    likelihood - lineage.log_potential
                };
                Ok((
                    proposal.state,
                    proposal.log_prior_over_proposal,
                    combined_endpoint_ratio,
                    Some(IntermediatePotentialLineage {
                        log_potential: lineage.log_potential,
                        log_twist_potential,
                        context: lineage.context.clone(),
                    }),
                ))
            },
        )?;
        let CandidatePoolEpoch {
            epoch,
            checkpoint,
            carried_auxiliary,
            root_stratified_checkpoint,
        } = pooled;
        if let Some(checkpoint) = root_stratified_checkpoint {
            root_stratified_candidate_pool_checkpoints.push(checkpoint);
        }
        let endpoint_log_twist_potentials = persistent_twist.is_some().then(|| {
            carried_auxiliary
                .into_iter()
                .map(|lineage| lineage.map_or(0.0, |lineage| lineage.log_twist_potential))
                .collect::<Vec<_>>()
        });
        (
            epoch.states,
            epoch.log_weights,
            epoch.stratum_ids,
            epoch.ancestor_indices,
            checkpoint.realized_log_evidence_increment,
            Some(checkpoint),
            endpoint_log_twist_potentials,
        )
    };
    let endpoint_root_ids = endpoint_ancestors
        .iter()
        .map(|&ancestor| root_ids[ancestor])
        .collect::<Vec<_>>();
    ancestors_to_epoch_input = endpoint_ancestors
        .iter()
        .map(|&ancestor| ancestors_to_epoch_input[ancestor])
        .collect();
    let posterior_ess = effective_sample_size(&endpoint_log_weights)?;
    let endpoint_diagnostics = weight_diagnostics(
        &endpoint_log_weights,
        &endpoint_root_ids,
        &endpoint_stratum_ids,
    )?;
    realized_log_evidence_increment += endpoint_log_evidence_increment;
    let endpoint = IntermediatePotentialEndpointCheckpoint {
        elapsed_seconds: endpoint_elapsed_seconds,
        positive_particles: endpoint_log_weights
            .iter()
            .filter(|weight| weight.is_finite())
            .count(),
        log_evidence_increment: endpoint_log_evidence_increment,
        posterior_effective_sample_size: posterior_ess,
        maximum_particle_weight: endpoint_diagnostics.maximum_normalized_weight,
        distinct_positive_roots: endpoint_diagnostics.distinct_root_ancestors,
        root_effective_sample_size: endpoint_diagnostics.root_effective_sample_size,
        maximum_root_weight: endpoint_diagnostics.maximum_root_weight,
        strata: endpoint_diagnostics.strata,
        candidate_pool: endpoint_candidate_pool,
    };
    Ok(StratifiedEpoch {
        states: endpoint_states,
        log_weights: endpoint_log_weights,
        ancestor_indices: ancestors_to_epoch_input,
        stratum_ids: endpoint_stratum_ids,
        guide_ess: None,
        posterior_ess,
        ancestor_resampled: true,
        log_evidence_increment: realized_log_evidence_increment,
        transition_pool_checkpoint: None,
        root_stratified_candidate_pool_checkpoints,
        intermediate_potential_checkpoint: Some(IntermediatePotentialCheckpoint {
            observation_index: input.epoch,
            observation_time_s: endpoint_time_s,
            points: point_checkpoints,
            endpoint,
            realized_log_evidence_increment,
        }),
        persistent_twist_log_potentials: endpoint_log_twist_potentials,
    })
}

struct ResampledPopulation<S> {
    states: Vec<S>,
    log_weights: Vec<f64>,
    root_ids: Vec<usize>,
    stratum_ids: Vec<StratumId>,
    parent_indices: Vec<usize>,
    any_resampled: bool,
}

struct ResampleWithinStrataInput<'a, S> {
    states: &'a [S],
    log_weights: &'a [f64],
    root_ids: &'a [usize],
    stratum_ids: &'a [StratumId],
    allocations: &'a [StratumAllocation],
    seed: u64,
    epoch: usize,
    policy: WithinStratumResamplingPolicy,
    retain_zero_mass_strata: bool,
    conditional_ess_resample_fraction: Option<f64>,
}

fn resample_within_strata<S: Clone>(
    input: ResampleWithinStrataInput<'_, S>,
) -> Result<ResampledPopulation<S>, SmcError> {
    let ResampleWithinStrataInput {
        states,
        log_weights,
        root_ids,
        stratum_ids,
        allocations,
        seed,
        epoch,
        policy,
        retain_zero_mass_strata,
        conditional_ess_resample_fraction,
    } = input;
    let sources = ensure_allocation(allocations, stratum_ids)?;
    let mut new_states = Vec::with_capacity(states.len());
    let mut new_weights = Vec::with_capacity(states.len());
    let mut new_roots = Vec::with_capacity(states.len());
    let mut new_strata = Vec::with_capacity(states.len());
    let mut parent_indices = Vec::with_capacity(states.len());
    let mut output_slot = 0usize;
    let mut any_resampled = false;
    for allocation in allocations {
        let source_indices = &sources[&allocation.id];
        let raw = source_indices
            .iter()
            .map(|&index| log_weights[index])
            .collect::<Vec<_>>();
        let normalized = normalize_log_weights(&raw);
        if matches!(normalized, Err(SmcError::AllParticlesRejected)) && retain_zero_mass_strata {
            for &parent in source_indices {
                new_states.push(states[parent].clone());
                new_weights.push(f64::NEG_INFINITY);
                new_roots.push(root_ids[parent]);
                new_strata.push(allocation.id);
                parent_indices.push(parent);
                output_slot += 1;
            }
            continue;
        }
        let (conditional, log_stratum_mass) = normalized.map_err(|error| match error {
            SmcError::AllParticlesRejected => SmcError::StratumRejected(allocation.id),
            other => other,
        })?;
        let should_resample = match conditional_ess_resample_fraction {
            Some(fraction) => {
                effective_sample_size(&conditional)? < fraction * allocation.particles as f64
            }
            None => true,
        };
        if !should_resample {
            for &parent in source_indices {
                new_states.push(states[parent].clone());
                new_weights.push(log_weights[parent]);
                new_roots.push(root_ids[parent]);
                new_strata.push(allocation.id);
                parent_indices.push(parent);
                output_slot += 1;
            }
            continue;
        }
        any_resampled = true;
        let source_roots = source_indices
            .iter()
            .map(|&index| root_ids[index])
            .collect::<Vec<_>>();
        let proposal_log_probabilities =
            defensive_root_log_probabilities(&conditional, &source_roots, policy).map_err(
                |error| match error {
                    SmcError::AllParticlesRejected => SmcError::StratumRejected(allocation.id),
                    other => other,
                },
            )?;
        let proposal_weights = proposal_log_probabilities
            .iter()
            .map(|value| value.exp())
            .collect::<Vec<_>>();
        let mut rng = rng_for(
            seed,
            "stratified-posterior-resample",
            epoch,
            output_slot,
            allocation.id.0 as u64,
        );
        let first_offset = rng.gen::<f64>() / allocation.particles as f64;
        for local in systematic_resample_n(&proposal_weights, allocation.particles, first_offset)? {
            let parent = source_indices[local];
            new_states.push(states[parent].clone());
            let correction = if policy.uniform_root_mixture_epsilon == 0.0 {
                0.0
            } else {
                conditional[local] - proposal_log_probabilities[local]
            };
            new_weights.push(log_stratum_mass - (allocation.particles as f64).ln() + correction);
            new_roots.push(root_ids[parent]);
            new_strata.push(allocation.id);
            parent_indices.push(parent);
            output_slot += 1;
        }
    }
    Ok(ResampledPopulation {
        states: new_states,
        log_weights: new_weights,
        root_ids: new_roots,
        stratum_ids: new_strata,
        parent_indices,
        any_resampled,
    })
}

struct ApplyStratifiedPostResampleMoveInput<'a, 'kernel, M: ParticleModel> {
    model: &'a M,
    schedule: &'a StratifiedPostResampleMoveSchedule<'kernel, M>,
    population: &'a mut ResampledPopulation<M::State>,
    observation_index: usize,
    observation_time_s: f64,
    seed: u64,
}

fn apply_stratified_post_resample_move<M: ParticleModel>(
    input: ApplyStratifiedPostResampleMoveInput<'_, '_, M>,
) -> Result<Vec<StratifiedPostResampleMoveStratumCheckpoint>, SmcError> {
    let ApplyStratifiedPostResampleMoveInput {
        model,
        schedule,
        population,
        observation_index,
        observation_time_s,
        seed,
    } = input;
    let ResampledPopulation {
        states,
        root_ids,
        stratum_ids,
        parent_indices,
        ..
    } = population;
    if states.len() != stratum_ids.len()
        || states.len() != parent_indices.len()
        || states.len() != root_ids.len()
    {
        return Err(SmcError::InvalidAncestry);
    }

    let applications = states
        .par_iter_mut()
        .enumerate()
        .map(|(output_slot, state)| {
            let stratum = stratum_ids[output_slot];
            let context = StratifiedPostResampleMoveContext {
                observation_index,
                observation_time_s,
                stratum,
                output_slot,
                parent_slot: parent_indices[output_slot],
            };
            let mut rng = rng_for(
                seed,
                STRATIFIED_POST_RESAMPLE_MOVE_RNG_DOMAIN,
                observation_index,
                output_slot,
                stratum.0 as u64,
            );
            schedule
                .move_kernel
                .apply(model, state, context, &mut rng)
                .map_err(model_error)?;
            if model.stratum(state) != stratum {
                return Err(SmcError::StratumMismatch);
            }
            Ok(())
        })
        .collect::<Vec<Result<(), SmcError>>>();
    for application in applications {
        application?;
    }

    indices_by_stratum(stratum_ids)
        .into_iter()
        .map(|(stratum, output_slots)| {
            let output_slot_start = *output_slots.first().ok_or(SmcError::StratumMismatch)?;
            let output_slot_end_exclusive = output_slots
                .last()
                .copied()
                .ok_or(SmcError::StratumMismatch)?
                + 1;
            if output_slot_end_exclusive - output_slot_start != output_slots.len() {
                return Err(SmcError::StratumMismatch);
            }
            let distinct_parent_slots = output_slots
                .iter()
                .map(|&slot| parent_indices[slot])
                .collect::<BTreeSet<_>>()
                .len();
            let distinct_prior_roots = output_slots
                .iter()
                .map(|&slot| root_ids[slot])
                .collect::<BTreeSet<_>>()
                .len();
            Ok(StratifiedPostResampleMoveStratumCheckpoint {
                stratum,
                output_slot_start,
                output_slot_end_exclusive,
                output_move_invocations: output_slots.len(),
                distinct_parent_slots,
                distinct_prior_roots,
            })
        })
        .collect()
}

pub fn run_stratified_filter<M: ParticleModel>(
    model: &M,
    observations: &[M::Observation],
    config: &FilterConfig,
    plan: &StratifiedFilterPlan,
) -> Result<FilterResult<M::State>, SmcError> {
    run_stratified_filter_with_options(
        model,
        observations,
        config,
        plan,
        FilterRunOptions::default(),
    )
}

/// Run a stratified filter with an explicit defensive root-resampling policy.
/// Existing APIs call this with epsilon zero.
pub fn run_stratified_filter_with_resampling_policy<M: ParticleModel>(
    model: &M,
    observations: &[M::Observation],
    config: &FilterConfig,
    plan: &StratifiedFilterPlan,
    resampling_policy: WithinStratumResamplingPolicy,
) -> Result<FilterResult<M::State>, SmcError> {
    run_stratified_filter_with_snapshot_retention_and_resampling_policy(
        model,
        observations,
        config,
        plan,
        &SnapshotRetention::None,
        resampling_policy,
    )
}

pub fn run_stratified_filter_with_options<M: ParticleModel>(
    model: &M,
    observations: &[M::Observation],
    config: &FilterConfig,
    plan: &StratifiedFilterPlan,
    options: FilterRunOptions,
) -> Result<FilterResult<M::State>, SmcError> {
    let retention = if options.retain_snapshots {
        SnapshotRetention::All
    } else {
        SnapshotRetention::None
    };
    run_stratified_filter_with_snapshot_retention(model, observations, config, plan, &retention)
}

pub fn run_stratified_filter_with_snapshot_retention<M: ParticleModel>(
    model: &M,
    observations: &[M::Observation],
    config: &FilterConfig,
    plan: &StratifiedFilterPlan,
    retention: &SnapshotRetention,
) -> Result<FilterResult<M::State>, SmcError> {
    run_stratified_filter_with_snapshot_retention_and_resampling_policy(
        model,
        observations,
        config,
        plan,
        retention,
        WithinStratumResamplingPolicy::default(),
    )
}

/// Snapshot-selective stratified filtering with defensive root resampling.
/// The policy is applied both to auxiliary ancestor selection and to
/// ESS-triggered bootstrap posterior resampling.
pub fn run_stratified_filter_with_snapshot_retention_and_resampling_policy<M: ParticleModel>(
    model: &M,
    observations: &[M::Observation],
    config: &FilterConfig,
    plan: &StratifiedFilterPlan,
    retention: &SnapshotRetention,
    resampling_policy: WithinStratumResamplingPolicy,
) -> Result<FilterResult<M::State>, SmcError> {
    run_stratified_filter_internal(
        model,
        observations,
        config,
        plan,
        retention,
        resampling_policy,
        false,
        false,
    )
}

struct StratifiedPostResampleMoveSchedule<'a, M: ParticleModel> {
    move_kernel: &'a dyn StratifiedPostResampleMove<M>,
    steps: &'a [StratifiedPostResampleMoveStep],
}

/// Run the ordinary fixed-allocation stratified bootstrap filter with an
/// explicit target-invariant move after actual posterior resampling.
///
/// This bounded API deliberately does not expose island filtering, auxiliary
/// ancestor selection, transition pools, intermediate potentials, selection
/// guides, or persistent twists. Retention is limited to no snapshots or the
/// final physical observation because the existing discrete smoother does not
/// record mutation-kernel ancestry. Existing stratified-filter APIs use no
/// move and retain their historical random streams and serialized results.
#[allow(clippy::too_many_arguments)]
pub fn run_stratified_bootstrap_filter_with_post_resample_move<M, R>(
    model: &M,
    move_kernel: &R,
    observations: &[M::Observation],
    config: &FilterConfig,
    plan: &StratifiedFilterPlan,
    retention: &SnapshotRetention,
    resampling_policy: WithinStratumResamplingPolicy,
    steps: &[StratifiedPostResampleMoveStep],
) -> Result<StratifiedPostResampleMoveFilterResult<M::State>, SmcError>
where
    M: ParticleModel,
    R: StratifiedPostResampleMove<M>,
{
    let schedule = StratifiedPostResampleMoveSchedule { move_kernel, steps };
    let result = run_stratified_filter_core(
        model,
        observations,
        config,
        plan,
        retention,
        resampling_policy,
        false,
        false,
        None,
        None,
        None,
        None,
        Some(&schedule),
    )?;
    Ok(StratifiedPostResampleMoveFilterResult {
        pooled: result.pooled,
        post_resample_move_checkpoints: result.post_resample_move_checkpoints,
    })
}

trait DynTransitionPoolSchedule: Sync {
    fn steps_len(&self) -> usize;
    fn allocation(&self, epoch: usize) -> Option<CandidatePoolAllocation>;
}

struct LegacyTransitionPoolSchedule<'a> {
    steps: &'a [GlobalTransitionPoolStep],
}

impl DynTransitionPoolSchedule for LegacyTransitionPoolSchedule<'_> {
    fn steps_len(&self) -> usize {
        self.steps.len()
    }

    fn allocation(&self, epoch: usize) -> Option<CandidatePoolAllocation> {
        match self.steps[epoch] {
            GlobalTransitionPoolStep::Standard => None,
            GlobalTransitionPoolStep::Pool {
                candidates_per_particle,
            } => Some(CandidatePoolAllocation::PerParticle(
                candidates_per_particle,
            )),
        }
    }
}

struct RootStratifiedTransitionPoolSchedule<'a> {
    steps: &'a [RootStratifiedTransitionPoolStep],
}

impl DynTransitionPoolSchedule for RootStratifiedTransitionPoolSchedule<'_> {
    fn steps_len(&self) -> usize {
        self.steps.len()
    }

    fn allocation(&self, epoch: usize) -> Option<CandidatePoolAllocation> {
        match self.steps[epoch] {
            RootStratifiedTransitionPoolStep::Standard => None,
            RootStratifiedTransitionPoolStep::Pool {
                candidates_per_positive_root,
            } => Some(CandidatePoolAllocation::PerPositiveRoot(
                candidates_per_positive_root,
            )),
        }
    }
}

trait DynIntermediatePotentialSchedule<M: ParticleModel>: Sync {
    fn steps_len(&self) -> usize;
    fn has_bridge(&self) -> bool;
    fn validate_times(
        &self,
        model: &M,
        observations: &[M::Observation],
        initial_time_s: f64,
    ) -> Result<(), SmcError>;
    fn run_epoch(
        &self,
        input: &EpochInput<'_, M>,
        allocations: &[StratumAllocation],
        selection_guide: Option<&SelectionGuideScorer<'_, M::State>>,
        persistent_twist: Option<&PersistentTwistEpochInput<'_, M::State>>,
    ) -> Result<Option<StratifiedEpoch<M::State>>, SmcError>;
}

trait DynSelectionGuideSchedule<M: ParticleModel>: Sync {
    fn steps_len(&self) -> usize;
    fn has_guide(&self) -> bool;
    fn is_guided(&self, epoch: usize) -> bool;
    fn log_selection_guide(
        &self,
        epoch: usize,
        model: &M,
        state: &M::State,
        observation: &M::Observation,
    ) -> Result<f64, SmcError>;
}

struct SelectionGuideScheduleAdapter<'a, G, P> {
    guide: &'a G,
    steps: &'a [SelectionGuideStep<P>],
}

impl<M, G> DynSelectionGuideSchedule<M> for SelectionGuideScheduleAdapter<'_, G, G::Point>
where
    M: ParticleModel,
    G: SelectionGuide<M>,
{
    fn steps_len(&self) -> usize {
        self.steps.len()
    }

    fn has_guide(&self) -> bool {
        self.steps
            .iter()
            .any(|step| matches!(step, SelectionGuideStep::Guide { .. }))
    }

    fn is_guided(&self, epoch: usize) -> bool {
        matches!(self.steps[epoch], SelectionGuideStep::Guide { .. })
    }

    fn log_selection_guide(
        &self,
        epoch: usize,
        model: &M,
        state: &M::State,
        observation: &M::Observation,
    ) -> Result<f64, SmcError> {
        let SelectionGuideStep::Guide { point } = &self.steps[epoch] else {
            return Err(SmcError::InvalidConfiguration(
                "selection guide requested at an unguided epoch",
            ));
        };
        self.guide
            .log_selection_guide(model, state, observation, point)
            .map_err(model_error)
    }
}

trait DynPersistentTwistSchedule<M: ParticleModel>: Sync {
    fn steps_len(&self) -> usize;
    fn has_twist(&self) -> bool;
    fn validate_structure(&self) -> Result<(), SmcError>;
    fn phase(&self, epoch: usize) -> Option<PersistentTwistPhase>;
    fn log_twist_potential(
        &self,
        epoch: usize,
        model: &M,
        state: &M::State,
        observation: &M::Observation,
    ) -> Result<f64, SmcError>;
}

struct PersistentTwistScheduleAdapter<'a, T, P> {
    twist: &'a T,
    steps: &'a [PersistentTwistStep<P>],
}

impl<M, T> DynPersistentTwistSchedule<M> for PersistentTwistScheduleAdapter<'_, T, T::Point>
where
    M: ParticleModel,
    T: PersistentTwist<M>,
{
    fn steps_len(&self) -> usize {
        self.steps.len()
    }

    fn has_twist(&self) -> bool {
        self.steps
            .iter()
            .any(|step| !matches!(step, PersistentTwistStep::Inactive))
    }

    fn validate_structure(&self) -> Result<(), SmcError> {
        let mut active = false;
        let mut completed = false;
        for step in self.steps {
            match step {
                PersistentTwistStep::Inactive if active => {
                    return Err(SmcError::InvalidConfiguration(
                        "a persistent twist cannot become inactive before finalization",
                    ));
                }
                PersistentTwistStep::Inactive => {}
                PersistentTwistStep::Activate { .. } if active || completed => {
                    return Err(SmcError::InvalidConfiguration(
                        "a persistent twist must have exactly one activation",
                    ));
                }
                PersistentTwistStep::Activate { .. } => active = true,
                PersistentTwistStep::Continue { .. } if !active => {
                    return Err(SmcError::InvalidConfiguration(
                        "persistent-twist continuation requires an active twist",
                    ));
                }
                PersistentTwistStep::Continue { .. } => {}
                PersistentTwistStep::Finalize { .. } if !active => {
                    return Err(SmcError::InvalidConfiguration(
                        "persistent-twist finalization requires an active twist",
                    ));
                }
                PersistentTwistStep::Finalize { .. } => {
                    active = false;
                    completed = true;
                }
            }
        }
        if active {
            return Err(SmcError::InvalidConfiguration(
                "a persistent-twist schedule must finalize before returning",
            ));
        }
        Ok(())
    }

    fn phase(&self, epoch: usize) -> Option<PersistentTwistPhase> {
        match &self.steps[epoch] {
            PersistentTwistStep::Inactive => None,
            PersistentTwistStep::Activate { .. } => Some(PersistentTwistPhase::Activate),
            PersistentTwistStep::Continue { .. } => Some(PersistentTwistPhase::Continue),
            PersistentTwistStep::Finalize { .. } => Some(PersistentTwistPhase::Finalize),
        }
    }

    fn log_twist_potential(
        &self,
        epoch: usize,
        model: &M,
        state: &M::State,
        observation: &M::Observation,
    ) -> Result<f64, SmcError> {
        let point = match &self.steps[epoch] {
            PersistentTwistStep::Activate { point }
            | PersistentTwistStep::Continue { point }
            | PersistentTwistStep::Finalize { point } => point,
            PersistentTwistStep::Inactive => {
                return Err(SmcError::InvalidConfiguration(
                    "persistent twist requested at an inactive epoch",
                ));
            }
        };
        self.twist
            .log_twist_potential(model, state, observation, point)
            .map_err(model_error)
    }
}

struct IntermediatePotentialScheduleAdapter<'a, B, P> {
    bridge: &'a B,
    steps: &'a [IntermediatePotentialStep<P>],
}

impl<M, B> DynIntermediatePotentialSchedule<M>
    for IntermediatePotentialScheduleAdapter<'_, B, B::Point>
where
    M: ParticleModel,
    B: IntermediatePotentialBridge<M>,
{
    fn steps_len(&self) -> usize {
        self.steps.len()
    }

    fn has_bridge(&self) -> bool {
        self.steps.iter().any(|step| step.bridge_parts().is_some())
    }

    fn validate_times(
        &self,
        model: &M,
        observations: &[M::Observation],
        initial_time_s: f64,
    ) -> Result<(), SmcError> {
        let mut interval_start_time_s = initial_time_s;
        for (observation, step) in observations.iter().zip(self.steps) {
            let endpoint_time_s = model.observation_time_s(observation);
            if let Some((points, endpoint_candidates_per_particle)) = step.bridge_parts() {
                if points.is_empty() {
                    return Err(SmcError::InvalidConfiguration(
                        "an intermediate-potential bridge must contain at least one point",
                    ));
                }
                if endpoint_candidates_per_particle == 0 {
                    return Err(SmcError::InvalidConfiguration(
                        "intermediate-potential endpoint candidates per particle must be positive",
                    ));
                }
                let mut prior_point_time_s = interval_start_time_s;
                for point in points {
                    let point_time_s = self.bridge.point_time_s(&point.point);
                    if !point_time_s.is_finite()
                        || point_time_s <= prior_point_time_s
                        || point_time_s >= endpoint_time_s
                        || point.candidates_per_particle == 0
                    {
                        return Err(SmcError::InvalidConfiguration(
                            "bridge points must be strictly ordered inside their observation interval and use positive candidate counts",
                        ));
                    }
                    prior_point_time_s = point_time_s;
                }
            }
            interval_start_time_s = endpoint_time_s;
        }
        Ok(())
    }

    fn run_epoch(
        &self,
        input: &EpochInput<'_, M>,
        allocations: &[StratumAllocation],
        selection_guide: Option<&SelectionGuideScorer<'_, M::State>>,
        persistent_twist: Option<&PersistentTwistEpochInput<'_, M::State>>,
    ) -> Result<Option<StratifiedEpoch<M::State>>, SmcError> {
        match self.steps[input.epoch].bridge_parts() {
            None => Ok(None),
            Some((points, endpoint_candidates_per_particle)) => {
                let allocated_points = points
                    .iter()
                    .map(|point| CandidateAllocatedIntermediatePotentialBridgePoint {
                        point: &point.point,
                        candidate_allocation: CandidatePoolAllocation::PerParticle(
                            point.candidates_per_particle,
                        ),
                    })
                    .collect::<Vec<_>>();
                let endpoint_candidate_allocation = if endpoint_candidates_per_particle == 1 {
                    IntermediateEndpointCandidateAllocation::LegacySingle
                } else {
                    IntermediateEndpointCandidateAllocation::Pool(
                        CandidatePoolAllocation::PerParticle(endpoint_candidates_per_particle),
                    )
                };
                run_stratified_intermediate_potential_epoch(
                    input,
                    allocations,
                    self.bridge,
                    &allocated_points,
                    endpoint_candidate_allocation,
                    selection_guide,
                    persistent_twist,
                )
                .map(Some)
            }
        }
    }
}

struct RootStratifiedIntermediatePotentialScheduleAdapter<'a, B, P> {
    bridge: &'a B,
    steps: &'a [RootStratifiedIntermediatePotentialStep<P>],
}

impl<M, B> DynIntermediatePotentialSchedule<M>
    for RootStratifiedIntermediatePotentialScheduleAdapter<'_, B, B::Point>
where
    M: ParticleModel,
    B: IntermediatePotentialBridge<M>,
{
    fn steps_len(&self) -> usize {
        self.steps.len()
    }

    fn has_bridge(&self) -> bool {
        self.steps.iter().any(|step| step.bridge_parts().is_some())
    }

    fn validate_times(
        &self,
        model: &M,
        observations: &[M::Observation],
        initial_time_s: f64,
    ) -> Result<(), SmcError> {
        let mut interval_start_time_s = initial_time_s;
        for (observation, step) in observations.iter().zip(self.steps) {
            let endpoint_time_s = model.observation_time_s(observation);
            if let Some((points, endpoint_candidates_per_positive_root)) = step.bridge_parts() {
                if points.is_empty() {
                    return Err(SmcError::InvalidConfiguration(
                        "an intermediate-potential bridge must contain at least one point",
                    ));
                }
                CandidatePoolAllocation::PerPositiveRoot(endpoint_candidates_per_positive_root)
                    .validate()?;
                let mut prior_point_time_s = interval_start_time_s;
                for point in points {
                    let point_time_s = self.bridge.point_time_s(&point.point);
                    CandidatePoolAllocation::PerPositiveRoot(point.candidates_per_positive_root)
                        .validate()?;
                    if !point_time_s.is_finite()
                        || point_time_s <= prior_point_time_s
                        || point_time_s >= endpoint_time_s
                    {
                        return Err(SmcError::InvalidConfiguration(
                            "bridge points must be strictly ordered inside their observation interval and use positive candidate counts",
                        ));
                    }
                    prior_point_time_s = point_time_s;
                }
            }
            interval_start_time_s = endpoint_time_s;
        }
        Ok(())
    }

    fn run_epoch(
        &self,
        input: &EpochInput<'_, M>,
        allocations: &[StratumAllocation],
        selection_guide: Option<&SelectionGuideScorer<'_, M::State>>,
        persistent_twist: Option<&PersistentTwistEpochInput<'_, M::State>>,
    ) -> Result<Option<StratifiedEpoch<M::State>>, SmcError> {
        match self.steps[input.epoch].bridge_parts() {
            None => Ok(None),
            Some((points, endpoint_candidates_per_positive_root)) => {
                let allocated_points = points
                    .iter()
                    .map(|point| CandidateAllocatedIntermediatePotentialBridgePoint {
                        point: &point.point,
                        candidate_allocation: CandidatePoolAllocation::PerPositiveRoot(
                            point.candidates_per_positive_root,
                        ),
                    })
                    .collect::<Vec<_>>();
                run_stratified_intermediate_potential_epoch(
                    input,
                    allocations,
                    self.bridge,
                    &allocated_points,
                    IntermediateEndpointCandidateAllocation::Pool(
                        CandidatePoolAllocation::PerPositiveRoot(
                            endpoint_candidates_per_positive_root,
                        ),
                    ),
                    selection_guide,
                    persistent_twist,
                )
                .map(Some)
            }
        }
    }
}

/// Run a fixed-allocation stratified filter with strictly positive
/// intermediate guide potentials on selected observation intervals.
///
/// At point `j`, the exact candidate-pool increment is
/// `p/q * h_j(x_j) / h_{j-1}(x_{j-1})`. Every point uses the same proper
/// root-defensive global candidate and output laws as
/// [`run_stratified_filter_with_global_transition_pool`]. The physical endpoint
/// is then assimilated with increment `p/q * G(y | x) / h_last`. A legacy
/// [`IntermediatePotentialStep::Bridge`] proposes it once per output particle.
/// [`IntermediatePotentialStep::BridgeWithEndpointPool`] instead applies the
/// same proper global candidate/output law at the endpoint, with the declared
/// number of candidates per particle. `K = 1` is canonicalized to the legacy
/// endpoint path. All guide factors therefore telescope out of both the
/// endpoint target and its evidence estimator.
///
/// Bridge steps currently require the bootstrap algorithm and cannot be
/// combined with a separate endpoint global-transition-pool schedule.
#[allow(clippy::too_many_arguments)]
pub fn run_stratified_filter_with_intermediate_potentials<M, B>(
    model: &M,
    bridge: &B,
    observations: &[M::Observation],
    config: &FilterConfig,
    plan: &StratifiedFilterPlan,
    retention: &SnapshotRetention,
    resampling_policy: WithinStratumResamplingPolicy,
    steps: &[IntermediatePotentialStep<B::Point>],
) -> Result<IntermediatePotentialFilterResult<M::State>, SmcError>
where
    M: ParticleModel,
    B: IntermediatePotentialBridge<M>,
{
    let schedule = IntermediatePotentialScheduleAdapter { bridge, steps };
    let result = run_stratified_filter_core(
        model,
        observations,
        config,
        plan,
        retention,
        resampling_policy,
        true,
        false,
        None,
        Some(&schedule),
        None,
        None,
        None,
    )?;
    Ok(IntermediatePotentialFilterResult {
        pooled: result.pooled,
        intermediate_potential_checkpoints: result.intermediate_potential_checkpoints,
    })
}

/// Run an exact intermediate-potential filter with a fixed number of
/// transition candidates per finite-mass root at every bridge point and at
/// the physical endpoint. Guide ratios still telescope pathwise; fixed-root
/// allocation changes only the Monte Carlo proposal.
/// Composition with a separate selection guide or persistent twist is not
/// exposed by this bounded API.
#[allow(clippy::too_many_arguments)]
pub fn run_stratified_filter_with_root_stratified_intermediate_potentials<M, B>(
    model: &M,
    bridge: &B,
    observations: &[M::Observation],
    config: &FilterConfig,
    plan: &StratifiedFilterPlan,
    retention: &SnapshotRetention,
    resampling_policy: WithinStratumResamplingPolicy,
    steps: &[RootStratifiedIntermediatePotentialStep<B::Point>],
) -> Result<RootStratifiedIntermediatePotentialFilterResult<M::State>, SmcError>
where
    M: ParticleModel,
    B: IntermediatePotentialBridge<M>,
{
    let schedule = RootStratifiedIntermediatePotentialScheduleAdapter { bridge, steps };
    let result = run_stratified_filter_core(
        model,
        observations,
        config,
        plan,
        retention,
        resampling_policy,
        true,
        false,
        None,
        Some(&schedule),
        None,
        None,
        None,
    )?;
    Ok(RootStratifiedIntermediatePotentialFilterResult {
        pooled: result.pooled,
        intermediate_potential_checkpoints: result.intermediate_potential_checkpoints,
        root_stratified_candidate_pool_checkpoints: result
            .root_stratified_candidate_pool_checkpoints,
    })
}

/// Run the exact intermediate-potential filter while using a strictly
/// positive future-facing guide only to allocate ancestor and output
/// proposals on selected epochs.
///
/// If `h` is the model-owned selection guide, a guided ancestor is drawn from
/// a root-defensive version of `Q_i ∝ W_i h_i` and retains `W_i / Q_i` in
/// its candidate measure. Output candidates are analogously drawn from a
/// root-defensive `H_j ∝ v_j h_j` and retain `v_j / H_j`. The guide is
/// therefore absent from the filtering target and evidence at every epoch.
/// Guided standard epochs use a one-candidate global pool so the selected
/// allocation and its correction survive to the next epoch. No ordinary
/// target-only resampling follows a guided selection.
#[allow(clippy::too_many_arguments)]
pub fn run_stratified_filter_with_intermediate_potentials_and_selection_guide<M, B, G>(
    model: &M,
    bridge: &B,
    selection_guide: &G,
    observations: &[M::Observation],
    config: &FilterConfig,
    plan: &StratifiedFilterPlan,
    retention: &SnapshotRetention,
    resampling_policy: WithinStratumResamplingPolicy,
    intermediate_steps: &[IntermediatePotentialStep<B::Point>],
    selection_steps: &[SelectionGuideStep<G::Point>],
) -> Result<SelectionGuideFilterResult<M::State>, SmcError>
where
    M: ParticleModel,
    B: IntermediatePotentialBridge<M>,
    G: SelectionGuide<M>,
{
    let intermediate_schedule = IntermediatePotentialScheduleAdapter {
        bridge,
        steps: intermediate_steps,
    };
    let selection_schedule = SelectionGuideScheduleAdapter {
        guide: selection_guide,
        steps: selection_steps,
    };
    let result = run_stratified_filter_core(
        model,
        observations,
        config,
        plan,
        retention,
        resampling_policy,
        true,
        false,
        None,
        Some(&intermediate_schedule),
        Some(&selection_schedule),
        None,
        None,
    )?;
    Ok(SelectionGuideFilterResult {
        pooled: result.pooled,
        guided_standard_checkpoints: result.transition_pool_checkpoints,
        intermediate_potential_checkpoints: result.intermediate_potential_checkpoints,
    })
}

/// Run an exact persistent computational twist across a contiguous group of
/// physical observation epochs and remove it once at the declared final
/// epoch.
///
/// While active, a candidate descended from `i` has measure
/// `W_i / Q_i * p/q * G * H_new/H_old / B`. At an intermediate SATCOM guide
/// point, `G` is replaced by the existing bridge-potential ratio, so the two
/// independent telescoping ratios compose pathwise. Candidate output is drawn
/// from the ordinary root-defensive candidate target and retains its exact
/// target/proposal correction; a local [`SelectionGuide`] is not applied.
///
/// `Activate` uses exactly `H_old = 1`. `Finalize` first performs the twisted
/// endpoint candidate/output selection and then globally reweights retained
/// slots by `1/H_final`, without resampling. The returned final population,
/// final retained snapshot, final filter checkpoint, and cumulative evidence
/// therefore have ordinary physical filtering semantics and can be consumed
/// by downstream likelihood code without another twist correction.
#[allow(clippy::too_many_arguments)]
pub fn run_stratified_filter_with_intermediate_potentials_and_persistent_twist<M, B, T>(
    model: &M,
    bridge: &B,
    persistent_twist: &T,
    observations: &[M::Observation],
    config: &FilterConfig,
    plan: &StratifiedFilterPlan,
    retention: &SnapshotRetention,
    resampling_policy: WithinStratumResamplingPolicy,
    intermediate_steps: &[IntermediatePotentialStep<B::Point>],
    persistent_twist_steps: &[PersistentTwistStep<T::Point>],
) -> Result<PersistentTwistFilterResult<M::State>, SmcError>
where
    M: ParticleModel,
    B: IntermediatePotentialBridge<M>,
    T: PersistentTwist<M>,
{
    let intermediate_schedule = IntermediatePotentialScheduleAdapter {
        bridge,
        steps: intermediate_steps,
    };
    let persistent_twist_schedule = PersistentTwistScheduleAdapter {
        twist: persistent_twist,
        steps: persistent_twist_steps,
    };
    let result = run_stratified_filter_core(
        model,
        observations,
        config,
        plan,
        retention,
        resampling_policy,
        true,
        false,
        None,
        Some(&intermediate_schedule),
        None,
        Some(&persistent_twist_schedule),
        None,
    )?;
    Ok(PersistentTwistFilterResult {
        pooled: result.pooled,
        persistent_twist_checkpoints: result.persistent_twist_checkpoints,
        twisted_standard_checkpoints: result.transition_pool_checkpoints,
        intermediate_potential_checkpoints: result.intermediate_potential_checkpoints,
        twisted_filtering_observation_indices: result.twisted_filtering_observation_indices,
    })
}

/// Run a fixed-allocation stratified filter with an explicit per-observation
/// global ancestor/transition-pool schedule.
///
/// At a pooled epoch, stratum `s` draws `B_s = k * n_s` ancestors from the
/// root-defensive proposal `Q_s`, then proposes and scores one transition from
/// each. Candidate `j`, descended from particle `i`, represents the proper
/// unnormalized measure
///
/// `W_i / Q_s(i) * p(x_j | x_i) / q(x_j | x_i) * L(y | x_j) / B_s`.
///
/// Candidates compete across their complete scientific stratum before the
/// fixed `n_s` output population is selected. A defensive output proposal is
/// corrected by the exact candidate-target/proposal ratio. Thus the realized
/// output normalizer, which is reported separately from the pre-selection
/// candidate normalizer, remains an unbiased evidence increment.
///
/// `Standard` steps use `config.algorithm`. `Pool` steps replace that epoch's
/// configured algorithm and deliberately form their ancestor proposal from
/// the current positive-mass roots without consulting the model's approximate
/// guide, so a finite target root cannot be removed by guide under-support.
pub fn run_stratified_filter_with_global_transition_pool<M: ParticleModel>(
    model: &M,
    observations: &[M::Observation],
    config: &FilterConfig,
    plan: &StratifiedFilterPlan,
    retention: &SnapshotRetention,
    resampling_policy: WithinStratumResamplingPolicy,
    steps: &[GlobalTransitionPoolStep],
) -> Result<GlobalTransitionPoolFilterResult<M::State>, SmcError> {
    let schedule = LegacyTransitionPoolSchedule { steps };
    let result = run_stratified_filter_core(
        model,
        observations,
        config,
        plan,
        retention,
        resampling_policy,
        true,
        false,
        Some(&schedule),
        None,
        None,
        None,
        None,
    )?;
    Ok(GlobalTransitionPoolFilterResult {
        pooled: result.pooled,
        transition_pool_checkpoints: result.transition_pool_checkpoints,
    })
}

/// Run an exact fixed-allocation filter whose selected epochs draw exactly
/// `L` prior/proposal transitions from every finite-mass root inside each
/// scientific stratum.
///
/// If root `r` has incoming mass `M_r`, an ancestor is drawn from
/// `a(i | r) = W_i / M_r`. Each resulting candidate carries proper measure
/// `M_r / L * p/q * G`. The existing defensive output proposal is then
/// applied with its exact target/proposal correction.
///
/// This bounded API targets the ordinary physical filter. Composition with a
/// selection guide or persistent twist is intentionally not exposed.
pub fn run_stratified_filter_with_root_stratified_transition_pool<M: ParticleModel>(
    model: &M,
    observations: &[M::Observation],
    config: &FilterConfig,
    plan: &StratifiedFilterPlan,
    retention: &SnapshotRetention,
    resampling_policy: WithinStratumResamplingPolicy,
    steps: &[RootStratifiedTransitionPoolStep],
) -> Result<RootStratifiedTransitionPoolFilterResult<M::State>, SmcError> {
    let schedule = RootStratifiedTransitionPoolSchedule { steps };
    let result = run_stratified_filter_core(
        model,
        observations,
        config,
        plan,
        retention,
        resampling_policy,
        true,
        false,
        Some(&schedule),
        None,
        None,
        None,
        None,
    )?;
    Ok(RootStratifiedTransitionPoolFilterResult {
        pooled: result.pooled,
        transition_pool_checkpoints: result.transition_pool_checkpoints,
        root_stratified_candidate_pool_checkpoints: result
            .root_stratified_candidate_pool_checkpoints,
    })
}

/// Internal form used by the island wrapper. Zero-mass computational strata
/// remain as zero-weight slots so one extinct island cannot terminate the
/// other independent estimators. Bootstrap resampling can also be triggered
/// from each computational stratum's conditional ESS rather than globally.
#[allow(clippy::too_many_arguments)]
pub(crate) fn run_stratified_filter_internal<M: ParticleModel>(
    model: &M,
    observations: &[M::Observation],
    config: &FilterConfig,
    plan: &StratifiedFilterPlan,
    retention: &SnapshotRetention,
    resampling_policy: WithinStratumResamplingPolicy,
    retain_zero_mass_strata: bool,
    resample_by_stratum_ess: bool,
) -> Result<FilterResult<M::State>, SmcError> {
    run_stratified_filter_core(
        model,
        observations,
        config,
        plan,
        retention,
        resampling_policy,
        retain_zero_mass_strata,
        resample_by_stratum_ess,
        None,
        None,
        None,
        None,
        None,
    )
    .map(|result| result.pooled)
}

struct StratifiedCoreResult<S> {
    pooled: FilterResult<S>,
    transition_pool_checkpoints: Vec<GlobalTransitionPoolCheckpoint>,
    root_stratified_candidate_pool_checkpoints: Vec<RootStratifiedCandidatePoolCheckpoint>,
    intermediate_potential_checkpoints: Vec<IntermediatePotentialCheckpoint>,
    persistent_twist_checkpoints: Vec<PersistentTwistCheckpoint>,
    twisted_filtering_observation_indices: Vec<usize>,
    post_resample_move_checkpoints: Vec<StratifiedPostResampleMoveCheckpoint>,
}

#[allow(clippy::too_many_arguments)]
fn run_stratified_filter_core<M: ParticleModel>(
    model: &M,
    observations: &[M::Observation],
    config: &FilterConfig,
    plan: &StratifiedFilterPlan,
    retention: &SnapshotRetention,
    resampling_policy: WithinStratumResamplingPolicy,
    retain_zero_mass_strata: bool,
    resample_by_stratum_ess: bool,
    transition_pool_schedule: Option<&dyn DynTransitionPoolSchedule>,
    intermediate_potential_schedule: Option<&dyn DynIntermediatePotentialSchedule<M>>,
    selection_guide_schedule: Option<&dyn DynSelectionGuideSchedule<M>>,
    persistent_twist_schedule: Option<&dyn DynPersistentTwistSchedule<M>>,
    post_resample_move_schedule: Option<&StratifiedPostResampleMoveSchedule<'_, M>>,
) -> Result<StratifiedCoreResult<M::State>, SmcError> {
    config.validate().map_err(SmcError::InvalidConfiguration)?;
    plan.validate(config.particles)
        .map_err(SmcError::InvalidConfiguration)?;
    resampling_policy
        .validate()
        .map_err(SmcError::InvalidConfiguration)?;
    retention.validate(observations.len())?;
    if let Some(schedule) = post_resample_move_schedule {
        if config.algorithm != Algorithm::Bootstrap {
            return Err(SmcError::InvalidConfiguration(
                "post-resampling moves require the bootstrap algorithm",
            ));
        }
        if schedule.steps.len() != observations.len() {
            return Err(SmcError::InvalidConfiguration(
                "post-resampling move steps must match the observation count",
            ));
        }
        if retain_zero_mass_strata
            || resample_by_stratum_ess
            || transition_pool_schedule.is_some()
            || intermediate_potential_schedule.is_some()
            || selection_guide_schedule.is_some()
            || persistent_twist_schedule.is_some()
        {
            return Err(SmcError::InvalidConfiguration(
                "post-resampling moves support only the ordinary stratified bootstrap filter",
            ));
        }
        let retains_only_final = match retention {
            SnapshotRetention::None => true,
            SnapshotRetention::SelectedObservationIndices(indices) => {
                indices.iter().all(|&index| index + 1 == observations.len())
            }
            SnapshotRetention::All => false,
        };
        if !retains_only_final {
            return Err(SmcError::InvalidConfiguration(
                "post-resampling moves do not support intermediate snapshots or smoothing",
            ));
        }
    }
    if transition_pool_schedule.is_some() && intermediate_potential_schedule.is_some() {
        return Err(SmcError::InvalidConfiguration(
            "endpoint global pools and intermediate-potential bridges are mutually exclusive",
        ));
    }
    if transition_pool_schedule.is_some() && selection_guide_schedule.is_some() {
        return Err(SmcError::InvalidConfiguration(
            "selection-guided filtering cannot be combined with a separate global transition-pool schedule",
        ));
    }
    if persistent_twist_schedule.is_some()
        && (transition_pool_schedule.is_some() || selection_guide_schedule.is_some())
    {
        return Err(SmcError::InvalidConfiguration(
            "persistent twisting cannot be combined with a local selection guide or separate global transition-pool schedule",
        ));
    }
    if let Some(schedule) = transition_pool_schedule {
        if schedule.steps_len() != observations.len() {
            return Err(SmcError::InvalidConfiguration(
                "global transition-pool steps must match the observation count",
            ));
        }
        for epoch in 0..schedule.steps_len() {
            if let Some(allocation) = schedule.allocation(epoch) {
                allocation.validate()?;
            }
        }
    }
    validate_observation_times(model, observations, config.initial_time_s)?;
    if let Some(schedule) = intermediate_potential_schedule {
        if schedule.steps_len() != observations.len() {
            return Err(SmcError::InvalidConfiguration(
                "intermediate-potential steps must match the observation count",
            ));
        }
        if schedule.has_bridge() && config.algorithm != Algorithm::Bootstrap {
            return Err(SmcError::InvalidConfiguration(
                "intermediate-potential bridges currently require the bootstrap algorithm",
            ));
        }
        schedule.validate_times(model, observations, config.initial_time_s)?;
    }
    if let Some(schedule) = selection_guide_schedule {
        if schedule.steps_len() != observations.len() {
            return Err(SmcError::InvalidConfiguration(
                "selection-guide steps must match the observation count",
            ));
        }
        if schedule.has_guide() && config.algorithm != Algorithm::Bootstrap {
            return Err(SmcError::InvalidConfiguration(
                "selection-guided filtering currently requires the bootstrap algorithm",
            ));
        }
    }
    if let Some(schedule) = persistent_twist_schedule {
        if schedule.steps_len() != observations.len() {
            return Err(SmcError::InvalidConfiguration(
                "persistent-twist steps must match the observation count",
            ));
        }
        schedule.validate_structure()?;
        if schedule.has_twist() && config.algorithm != Algorithm::Bootstrap {
            return Err(SmcError::InvalidConfiguration(
                "persistent twisting currently requires the bootstrap algorithm",
            ));
        }
    }
    let allocations = plan.canonical_allocations();

    let mut tasks = Vec::with_capacity(config.particles);
    let mut global_particle = 0usize;
    for allocation in &allocations {
        for within in 0..allocation.particles {
            tasks.push((global_particle, within, allocation.clone()));
            global_particle += 1;
        }
    }
    let initialized = tasks
        .par_iter()
        .map(|(particle, within, allocation)| {
            let mut rng = rng_for(
                config.seed,
                "stratified-initialize",
                0,
                *particle,
                allocation.id.0 as u64,
            );
            let initialized = model
                .initialize_in_stratum(
                    allocation.id,
                    *particle,
                    *within,
                    allocation.particles,
                    &mut rng,
                )
                .map_err(model_error)?;
            if !initialized.log_prior_over_proposal.is_finite() {
                return Err(SmcError::InvalidWeights);
            }
            if model.stratum(&initialized.state) != allocation.id {
                return Err(SmcError::StratumMismatch);
            }
            let allocation_probability = allocation.particles as f64 / config.particles as f64;
            Ok((
                initialized.state,
                allocation.log_prior_probability - allocation_probability.ln()
                    + initialized.log_prior_over_proposal,
                allocation.id,
            ))
        })
        .collect::<Vec<Result<_, SmcError>>>();

    let mut states = Vec::with_capacity(config.particles);
    let mut raw_initial_weights = Vec::with_capacity(config.particles);
    let mut stratum_ids = Vec::with_capacity(config.particles);
    for initialized in initialized {
        let (state, weight, stratum) = initialized?;
        states.push(state);
        raw_initial_weights.push(weight);
        stratum_ids.push(stratum);
    }
    let (mut log_weights, initial_normalizer) = normalize_log_weights(&raw_initial_weights)?;
    let initial_log_evidence = initial_normalizer - (config.particles as f64).ln();
    let mut root_ids = (0..config.particles).collect::<Vec<_>>();
    let initial_strata = weight_diagnostics(&log_weights, &root_ids, &stratum_ids)?.strata;
    let mut working_to_previous_snapshot = (0..config.particles).collect::<Vec<_>>();
    let mut snapshots = Vec::new();
    let mut has_retained_snapshot = false;
    if retention.retains_initial() {
        snapshots.push(FilterSnapshot {
            observation_index: None,
            observation_time_s: config.initial_time_s,
            particles: states.clone(),
            log_weights: log_weights.clone(),
            root_ids: root_ids.clone(),
            stratum_ids: stratum_ids.clone(),
        });
        has_retained_snapshot = true;
    }
    let mut ancestry = Vec::new();
    let mut checkpoints = Vec::with_capacity(observations.len());
    let mut transition_pool_checkpoints = Vec::new();
    let mut root_stratified_candidate_pool_checkpoints = Vec::new();
    let mut intermediate_potential_checkpoints = Vec::new();
    let mut persistent_twist_checkpoints = Vec::new();
    let mut twisted_filtering_observation_indices = Vec::new();
    let mut post_resample_move_checkpoints = Vec::new();
    let mut persistent_twist_log_potentials: Option<Vec<f64>> = None;
    let mut log_evidence = initial_log_evidence;
    let mut previous_time = config.initial_time_s;

    for (epoch, observation) in observations.iter().enumerate() {
        let observation_time = model.observation_time_s(observation);
        let mut post_resample_move_checkpoint =
            post_resample_move_schedule.map(|schedule| StratifiedPostResampleMoveCheckpoint {
                observation_index: epoch,
                observation_time_s: observation_time,
                step: schedule.steps[epoch],
                posterior_resampling_occurred: false,
                output_move_invocations: 0,
                strata: Vec::new(),
            });
        let elapsed_seconds = observation_time - previous_time;
        let input = EpochInput {
            model,
            states: &states,
            log_weights: &log_weights,
            root_ids: &root_ids,
            stratum_ids: &stratum_ids,
            observation,
            elapsed_seconds,
            epoch,
            config,
            resampling_policy,
            retain_zero_mass_strata,
        };
        let pool_allocation =
            transition_pool_schedule.and_then(|schedule| schedule.allocation(epoch));
        let score_selection_guide = |state: &M::State| {
            selection_guide_schedule
                .ok_or(SmcError::InvalidConfiguration(
                    "selection-guide schedule is unavailable",
                ))?
                .log_selection_guide(epoch, model, state, observation)
        };
        let selection_guide: Option<&SelectionGuideScorer<'_, M::State>> =
            if selection_guide_schedule.is_some_and(|schedule| schedule.is_guided(epoch)) {
                Some(&score_selection_guide)
            } else {
                None
            };
        let persistent_twist_phase =
            persistent_twist_schedule.and_then(|schedule| schedule.phase(epoch));
        let mut epoch_result = {
            let score_persistent_twist = |state: &M::State| {
                persistent_twist_schedule
                    .ok_or(SmcError::InvalidConfiguration(
                        "persistent-twist schedule is unavailable",
                    ))?
                    .log_twist_potential(epoch, model, state, observation)
            };
            let persistent_twist = persistent_twist_phase.map(|phase| PersistentTwistEpochInput {
                phase,
                input_log_potentials: persistent_twist_log_potentials.as_deref(),
                score: &score_persistent_twist,
            });
            match intermediate_potential_schedule
                .map(|schedule| {
                    schedule.run_epoch(
                        &input,
                        &allocations,
                        selection_guide,
                        persistent_twist.as_ref(),
                    )
                })
                .transpose()?
                .flatten()
            {
                Some(bridged) => bridged,
                None if selection_guide.is_some() => run_stratified_global_transition_pool_epoch(
                    &input,
                    &allocations,
                    1,
                    selection_guide,
                )?,
                None if persistent_twist.is_some() => run_stratified_persistent_twist_epoch(
                    &input,
                    &allocations,
                    persistent_twist.as_ref().expect("matched as present"),
                )?,
                None => match pool_allocation {
                    None => match config.algorithm {
                        Algorithm::Bootstrap => run_stratified_bootstrap_epoch(&input)?,
                        Algorithm::Auxiliary => {
                            run_stratified_auxiliary_epoch(&input, &allocations)?
                        }
                    },
                    Some(CandidatePoolAllocation::PerParticle(candidates_per_particle)) => {
                        run_stratified_global_transition_pool_epoch(
                            &input,
                            &allocations,
                            candidates_per_particle,
                            None,
                        )?
                    }
                    Some(CandidatePoolAllocation::PerPositiveRoot(
                        candidates_per_positive_root,
                    )) => run_stratified_root_transition_pool_epoch(
                        &input,
                        &allocations,
                        candidates_per_positive_root,
                    )?,
                },
            }
        };
        let next_root_ids = epoch_result
            .ancestor_indices
            .iter()
            .map(|index| root_ids[*index])
            .collect::<Vec<_>>();
        if let Some(phase) = persistent_twist_phase {
            let output_log_potentials = epoch_result.persistent_twist_log_potentials.take().ok_or(
                SmcError::InvalidConfiguration(
                    "an active persistent-twist epoch did not return lineage potentials",
                ),
            )?;
            let twisted_target_log_evidence_increment = epoch_result.log_evidence_increment;
            let (population, untwisted_log_weights, untwist_correction) =
                persistent_twist_population_diagnostics(
                    &epoch_result.log_weights,
                    &output_log_potentials,
                    &next_root_ids,
                    &epoch_result.stratum_ids,
                )?;
            let final_untwist_log_evidence_correction =
                (phase == PersistentTwistPhase::Finalize).then_some(untwist_correction);
            if phase == PersistentTwistPhase::Finalize {
                epoch_result.log_weights = untwisted_log_weights;
                epoch_result.posterior_ess = effective_sample_size(&epoch_result.log_weights)?;
                epoch_result.log_evidence_increment += untwist_correction;
                persistent_twist_log_potentials = None;

                if let Some(checkpoint) = epoch_result.intermediate_potential_checkpoint.as_mut() {
                    let physical = weight_diagnostics(
                        &epoch_result.log_weights,
                        &next_root_ids,
                        &epoch_result.stratum_ids,
                    )?;
                    checkpoint.realized_log_evidence_increment += untwist_correction;
                    checkpoint.endpoint.log_evidence_increment += untwist_correction;
                    checkpoint.endpoint.positive_particles = epoch_result
                        .log_weights
                        .iter()
                        .filter(|weight| weight.is_finite())
                        .count();
                    checkpoint.endpoint.posterior_effective_sample_size =
                        epoch_result.posterior_ess;
                    checkpoint.endpoint.maximum_particle_weight =
                        physical.maximum_normalized_weight;
                    checkpoint.endpoint.distinct_positive_roots = physical.distinct_root_ancestors;
                    checkpoint.endpoint.root_effective_sample_size =
                        physical.root_effective_sample_size;
                    checkpoint.endpoint.maximum_root_weight = physical.maximum_root_weight;
                    checkpoint.endpoint.strata = physical.strata;
                }
            } else {
                persistent_twist_log_potentials = Some(output_log_potentials);
                twisted_filtering_observation_indices.push(epoch);
            }
            persistent_twist_checkpoints.push(PersistentTwistCheckpoint {
                observation_index: epoch,
                observation_time_s: observation_time,
                phase,
                output_is_twisted: phase != PersistentTwistPhase::Finalize,
                twisted_target_log_evidence_increment,
                final_untwist_log_evidence_correction,
                filter_checkpoint_log_evidence_increment: epoch_result.log_evidence_increment,
                population,
            });
        } else if epoch_result.persistent_twist_log_potentials.is_some()
            || persistent_twist_log_potentials.is_some()
        {
            return Err(SmcError::InvalidConfiguration(
                "persistent-twist lineage state escaped its active schedule",
            ));
        }
        // A guided bridge has already made and corrected its future-facing
        // output selection even though its detailed pool diagnostics live in
        // the intermediate-potential checkpoint. Do not immediately erase
        // that allocation with an ordinary target-only ESS resample.
        let transition_pool_resampled = epoch_result.transition_pool_checkpoint.is_some()
            || !epoch_result
                .root_stratified_candidate_pool_checkpoints
                .is_empty()
            || selection_guide.is_some()
            || persistent_twist_phase.is_some();
        let snapshot_parent_indices = if has_retained_snapshot {
            epoch_result
                .ancestor_indices
                .iter()
                .map(|index| working_to_previous_snapshot[*index])
                .collect::<Vec<_>>()
        } else {
            Vec::new()
        };
        states = epoch_result.states;
        log_weights = epoch_result.log_weights;
        stratum_ids = epoch_result.stratum_ids;
        root_ids = next_root_ids;
        let guide_ess = epoch_result.guide_ess;
        let posterior_ess = epoch_result.posterior_ess;
        let ancestor_resampled = epoch_result.ancestor_resampled;
        let increment = epoch_result.log_evidence_increment;
        let mut posterior_resampled = transition_pool_resampled;
        let diagnostics = weight_diagnostics(&log_weights, &root_ids, &stratum_ids)?;

        let retain_epoch = retention.retains_observation(epoch, observations.len());
        if retain_epoch {
            let parent_observation_index = snapshots
                .last()
                .and_then(|snapshot| snapshot.observation_index);
            snapshots.push(FilterSnapshot {
                observation_index: Some(epoch),
                observation_time_s: observation_time,
                particles: states.clone(),
                log_weights: log_weights.clone(),
                root_ids: root_ids.clone(),
                stratum_ids: stratum_ids.clone(),
            });
            if has_retained_snapshot {
                ancestry.push(FilterAncestryStep {
                    child_observation_index: epoch,
                    parent_observation_index,
                    parent_indices: snapshot_parent_indices.clone(),
                });
            }
            has_retained_snapshot = true;
        }

        let global_resampling_triggered =
            posterior_ess < config.ess_resample_fraction * config.particles as f64;
        if config.algorithm == Algorithm::Bootstrap
            && !transition_pool_resampled
            && epoch + 1 < observations.len()
            && (global_resampling_triggered || resample_by_stratum_ess)
        {
            let mut resampled = resample_within_strata(ResampleWithinStrataInput {
                states: &states,
                log_weights: &log_weights,
                root_ids: &root_ids,
                stratum_ids: &stratum_ids,
                allocations: &allocations,
                seed: config.seed,
                epoch,
                policy: resampling_policy,
                retain_zero_mass_strata,
                conditional_ess_resample_fraction: resample_by_stratum_ess
                    .then_some(config.ess_resample_fraction),
            })?;
            if let (Some(schedule), Some(checkpoint)) = (
                post_resample_move_schedule,
                post_resample_move_checkpoint.as_mut(),
            ) {
                checkpoint.posterior_resampling_occurred = resampled.any_resampled;
                if resampled.any_resampled
                    && checkpoint.step == StratifiedPostResampleMoveStep::Apply
                {
                    checkpoint.strata = apply_stratified_post_resample_move(
                        ApplyStratifiedPostResampleMoveInput {
                            model,
                            schedule,
                            population: &mut resampled,
                            observation_index: epoch,
                            observation_time_s: observation_time,
                            seed: config.seed,
                        },
                    )?;
                    checkpoint.output_move_invocations = checkpoint
                        .strata
                        .iter()
                        .map(|entry| entry.output_move_invocations)
                        .sum();
                }
            }
            states = resampled.states;
            log_weights = resampled.log_weights;
            root_ids = resampled.root_ids;
            stratum_ids = resampled.stratum_ids;
            working_to_previous_snapshot = if retain_epoch {
                resampled.parent_indices
            } else if has_retained_snapshot {
                resampled
                    .parent_indices
                    .iter()
                    .map(|index| snapshot_parent_indices[*index])
                    .collect()
            } else {
                Vec::new()
            };
            posterior_resampled = resampled.any_resampled;
        } else if retain_epoch {
            working_to_previous_snapshot = (0..config.particles).collect();
        } else if has_retained_snapshot {
            working_to_previous_snapshot = snapshot_parent_indices;
        } else {
            working_to_previous_snapshot.clear();
        }

        log_evidence += increment;
        checkpoints.push(FilterCheckpoint {
            observation_index: epoch,
            observation_time_s: observation_time,
            guide_ess,
            posterior_ess,
            ancestor_resampled,
            posterior_resampled,
            log_evidence_increment: increment,
            cumulative_log_evidence: log_evidence,
            maximum_normalized_weight: diagnostics.maximum_normalized_weight,
            distinct_root_ancestors: diagnostics.distinct_root_ancestors,
            root_effective_sample_size: diagnostics.root_effective_sample_size,
            maximum_root_weight: diagnostics.maximum_root_weight,
            roots_with_mass_at_least_1e_6: diagnostics.roots_with_mass_at_least_1e_6,
            roots_with_mass_at_least_1e_3: diagnostics.roots_with_mass_at_least_1e_3,
            strata: diagnostics.strata,
        });
        root_stratified_candidate_pool_checkpoints
            .append(&mut epoch_result.root_stratified_candidate_pool_checkpoints);
        if let Some(checkpoint) = epoch_result.transition_pool_checkpoint {
            transition_pool_checkpoints.push(checkpoint);
        }
        if let Some(checkpoint) = epoch_result.intermediate_potential_checkpoint {
            intermediate_potential_checkpoints.push(checkpoint);
        }
        if let Some(checkpoint) = post_resample_move_checkpoint {
            post_resample_move_checkpoints.push(checkpoint);
        }
        previous_time = observation_time;
    }

    Ok(StratifiedCoreResult {
        pooled: FilterResult {
            particles: states,
            log_weights,
            root_ids,
            snapshots,
            ancestry,
            checkpoints,
            log_evidence,
            initial_log_evidence,
            initial_strata,
        },
        transition_pool_checkpoints,
        root_stratified_candidate_pool_checkpoints,
        intermediate_potential_checkpoints,
        persistent_twist_checkpoints,
        twisted_filtering_observation_indices,
        post_resample_move_checkpoints,
    })
}

#[cfg(test)]
mod tests {
    use std::{
        collections::{BTreeMap, BTreeSet},
        error::Error,
        fmt,
        sync::{Arc, Mutex},
    };

    use rand_distr::{Distribution, Exp};
    use rayon::ThreadPoolBuilder;
    use serde::{Deserialize, Serialize};

    use super::*;
    use crate::{Initialization, Proposal};

    #[derive(Debug, Clone, Copy, PartialEq, Serialize, Deserialize)]
    struct JumpState {
        time: f64,
        position: f64,
        event_count: u32,
        stratum: StratumId,
    }

    #[derive(Debug, Clone, Copy)]
    struct Observation {
        time: f64,
        position: f64,
    }

    #[derive(Debug)]
    struct ToyError;

    impl fmt::Display for ToyError {
        fn fmt(&self, formatter: &mut fmt::Formatter<'_>) -> fmt::Result {
            formatter.write_str("toy model error")
        }
    }

    impl Error for ToyError {}

    struct MarkedJumpModel;

    impl MarkedJumpModel {
        fn rate(stratum: StratumId) -> f64 {
            match stratum.0 {
                10 => 0.25,
                20 => 1.0,
                _ => unreachable!(),
            }
        }
    }

    impl ParticleModel for MarkedJumpModel {
        type State = JumpState;
        type Observation = Observation;
        type Error = ToyError;

        fn observation_time_s(&self, observation: &Self::Observation) -> f64 {
            observation.time
        }

        fn initialize(
            &self,
            _particle_index: usize,
            _rng: &mut rand_chacha::ChaCha8Rng,
        ) -> Result<Self::State, Self::Error> {
            Ok(JumpState {
                time: 0.0,
                position: 0.0,
                event_count: 0,
                stratum: StratumId::default(),
            })
        }

        fn initialize_in_stratum(
            &self,
            stratum: StratumId,
            _particle_index: usize,
            _particle_index_within_stratum: usize,
            _particles_in_stratum: usize,
            _rng: &mut rand_chacha::ChaCha8Rng,
        ) -> Result<Initialization<Self::State>, Self::Error> {
            Ok(Initialization::from_prior(JumpState {
                time: 0.0,
                position: 0.0,
                event_count: 0,
                stratum,
            }))
        }

        fn stratum(&self, state: &Self::State) -> StratumId {
            state.stratum
        }

        fn guide_log_likelihood(
            &self,
            state: &Self::State,
            observation: &Self::Observation,
        ) -> Result<f64, Self::Error> {
            let elapsed = observation.time - state.time;
            let expected = state.position + Self::rate(state.stratum) * elapsed;
            let variance = 0.49 + Self::rate(state.stratum) * elapsed;
            Ok(-0.5 * (observation.position - expected).powi(2) / variance)
        }

        fn propose(
            &self,
            state: &Self::State,
            observation: &Self::Observation,
            _elapsed_seconds: f64,
            rng: &mut rand_chacha::ChaCha8Rng,
        ) -> Result<Proposal<Self::State>, Self::Error> {
            let exponential = Exp::new(Self::rate(state.stratum)).unwrap();
            let mut next = *state;
            let mut event_time = state.time;
            loop {
                event_time += exponential.sample(rng);
                if event_time > observation.time {
                    break;
                }
                next.position += 1.0;
                next.event_count += 1;
            }
            next.time = observation.time;
            Ok(Proposal::from_prior(next))
        }

        fn log_likelihood(
            &self,
            state: &Self::State,
            observation: &Self::Observation,
        ) -> Result<f64, Self::Error> {
            Ok(-0.5 * ((observation.position - state.position) / 0.7).powi(2))
        }
    }

    fn plan(reverse: bool) -> StratifiedFilterPlan {
        let mut strata = vec![
            StratumAllocation {
                id: StratumId(10),
                particles: 600,
                log_prior_probability: 0.7_f64.ln(),
            },
            StratumAllocation {
                id: StratumId(20),
                particles: 1_400,
                log_prior_probability: 0.3_f64.ln(),
            },
        ];
        if reverse {
            strata.reverse();
        }
        StratifiedFilterPlan { strata }
    }

    fn config() -> FilterConfig {
        FilterConfig {
            particles: 2_000,
            seed: 37_011,
            algorithm: Algorithm::Auxiliary,
            initial_time_s: 0.0,
            ess_resample_fraction: 0.5,
        }
    }

    #[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
    struct PostResampleMoveState {
        initial_particle: usize,
        particle_within_stratum: usize,
        stratum: StratumId,
        move_draw: Option<u64>,
    }

    #[derive(Debug, Clone, Copy)]
    struct PostResampleMoveObservation {
        time_s: f64,
        favored_particle_within_stratum: Option<usize>,
    }

    struct PostResampleMoveModel;

    impl ParticleModel for PostResampleMoveModel {
        type State = PostResampleMoveState;
        type Observation = PostResampleMoveObservation;
        type Error = ToyError;

        fn observation_time_s(&self, observation: &Self::Observation) -> f64 {
            observation.time_s
        }

        fn initialize(
            &self,
            particle_index: usize,
            _rng: &mut ChaCha8Rng,
        ) -> Result<Self::State, Self::Error> {
            Ok(PostResampleMoveState {
                initial_particle: particle_index,
                particle_within_stratum: particle_index,
                stratum: StratumId::default(),
                move_draw: None,
            })
        }

        fn initialize_in_stratum(
            &self,
            stratum: StratumId,
            particle_index: usize,
            particle_index_within_stratum: usize,
            _particles_in_stratum: usize,
            _rng: &mut ChaCha8Rng,
        ) -> Result<Initialization<Self::State>, Self::Error> {
            Ok(Initialization::from_prior(PostResampleMoveState {
                initial_particle: particle_index,
                particle_within_stratum: particle_index_within_stratum,
                stratum,
                move_draw: None,
            }))
        }

        fn stratum(&self, state: &Self::State) -> StratumId {
            state.stratum
        }

        fn propose(
            &self,
            state: &Self::State,
            _observation: &Self::Observation,
            _elapsed_seconds: f64,
            _rng: &mut ChaCha8Rng,
        ) -> Result<Proposal<Self::State>, Self::Error> {
            Ok(Proposal::from_prior(state.clone()))
        }

        fn log_likelihood(
            &self,
            state: &Self::State,
            observation: &Self::Observation,
        ) -> Result<f64, Self::Error> {
            Ok(match observation.favored_particle_within_stratum {
                Some(favored) if state.particle_within_stratum != favored => f64::NEG_INFINITY,
                _ => 0.0,
            })
        }
    }

    fn post_resample_move_config(algorithm: Algorithm) -> FilterConfig {
        FilterConfig {
            particles: 8,
            seed: 91_337,
            algorithm,
            initial_time_s: 0.0,
            ess_resample_fraction: 0.9,
        }
    }

    fn post_resample_move_plan() -> StratifiedFilterPlan {
        StratifiedFilterPlan {
            strata: vec![
                StratumAllocation {
                    id: StratumId(30),
                    particles: 4,
                    log_prior_probability: 0.5_f64.ln(),
                },
                StratumAllocation {
                    id: StratumId(40),
                    particles: 4,
                    log_prior_probability: 0.5_f64.ln(),
                },
            ],
        }
    }

    fn forced_post_resample_move_observations() -> [PostResampleMoveObservation; 2] {
        [
            PostResampleMoveObservation {
                time_s: 1.0,
                favored_particle_within_stratum: Some(0),
            },
            PostResampleMoveObservation {
                time_s: 2.0,
                favored_particle_within_stratum: None,
            },
        ]
    }

    #[derive(Clone, Default)]
    struct RecordingPostResampleMove {
        invocations: Arc<Mutex<Vec<(StratifiedPostResampleMoveContext, u64)>>>,
    }

    impl RecordingPostResampleMove {
        fn canonical_invocations(
            &self,
        ) -> BTreeMap<usize, (StratifiedPostResampleMoveContext, u64)> {
            let invocations = self.invocations.lock().unwrap();
            assert_eq!(
                invocations.len(),
                invocations
                    .iter()
                    .map(|(context, _)| context.output_slot)
                    .collect::<BTreeSet<_>>()
                    .len(),
                "an output child was moved more than once"
            );
            invocations
                .iter()
                .map(|&(context, draw)| (context.output_slot, (context, draw)))
                .collect()
        }
    }

    impl StratifiedPostResampleMove<PostResampleMoveModel> for RecordingPostResampleMove {
        fn apply(
            &self,
            _model: &PostResampleMoveModel,
            state: &mut PostResampleMoveState,
            context: StratifiedPostResampleMoveContext,
            rng: &mut ChaCha8Rng,
        ) -> Result<(), ToyError> {
            let draw = rng.gen::<u64>();
            state.move_draw = Some(draw);
            self.invocations.lock().unwrap().push((context, draw));
            Ok(())
        }
    }

    struct FailingPostResampleMove;

    impl StratifiedPostResampleMove<PostResampleMoveModel> for FailingPostResampleMove {
        fn apply(
            &self,
            _model: &PostResampleMoveModel,
            _state: &mut PostResampleMoveState,
            _context: StratifiedPostResampleMoveContext,
            _rng: &mut ChaCha8Rng,
        ) -> Result<(), ToyError> {
            Err(ToyError)
        }
    }

    struct StratumChangingPostResampleMove;

    impl StratifiedPostResampleMove<PostResampleMoveModel> for StratumChangingPostResampleMove {
        fn apply(
            &self,
            _model: &PostResampleMoveModel,
            state: &mut PostResampleMoveState,
            _context: StratifiedPostResampleMoveContext,
            _rng: &mut ChaCha8Rng,
        ) -> Result<(), ToyError> {
            state.stratum = StratumId(99);
            Ok(())
        }
    }

    #[test]
    fn noop_post_resample_move_preserves_legacy_filter_bytes() {
        let observations = forced_post_resample_move_observations();
        let config = post_resample_move_config(Algorithm::Bootstrap);
        let plan = post_resample_move_plan();
        let retention = SnapshotRetention::SelectedObservationIndices(vec![1]);
        let legacy = run_stratified_filter_with_snapshot_retention_and_resampling_policy(
            &PostResampleMoveModel,
            &observations,
            &config,
            &plan,
            &retention,
            WithinStratumResamplingPolicy::default(),
        )
        .unwrap();
        let moved = run_stratified_bootstrap_filter_with_post_resample_move(
            &PostResampleMoveModel,
            &NoopStratifiedPostResampleMove,
            &observations,
            &config,
            &plan,
            &retention,
            WithinStratumResamplingPolicy::default(),
            &[
                StratifiedPostResampleMoveStep::Apply,
                StratifiedPostResampleMoveStep::Apply,
            ],
        )
        .unwrap();

        assert_eq!(
            serde_json::to_vec(&legacy).unwrap(),
            serde_json::to_vec(&moved.pooled).unwrap()
        );
        assert_eq!(moved.post_resample_move_checkpoints.len(), 2);
        assert!(moved.post_resample_move_checkpoints[0].posterior_resampling_occurred);
        assert_eq!(
            moved.post_resample_move_checkpoints[0].output_move_invocations,
            config.particles
        );
        assert!(!moved.post_resample_move_checkpoints[1].posterior_resampling_occurred);
        assert_eq!(
            moved.post_resample_move_checkpoints[1].output_move_invocations,
            0
        );
    }

    #[test]
    fn post_resample_move_is_once_per_child_and_thread_order_deterministic() {
        let observations = forced_post_resample_move_observations();
        let config = post_resample_move_config(Algorithm::Bootstrap);
        let plan = post_resample_move_plan();
        let retention = SnapshotRetention::None;
        let steps = [
            StratifiedPostResampleMoveStep::Apply,
            StratifiedPostResampleMoveStep::Apply,
        ];
        let legacy = run_stratified_filter_with_snapshot_retention_and_resampling_policy(
            &PostResampleMoveModel,
            &observations,
            &config,
            &plan,
            &retention,
            WithinStratumResamplingPolicy::default(),
        )
        .unwrap();

        let one_move = RecordingPostResampleMove::default();
        let one = ThreadPoolBuilder::new()
            .num_threads(1)
            .build()
            .unwrap()
            .install(|| {
                run_stratified_bootstrap_filter_with_post_resample_move(
                    &PostResampleMoveModel,
                    &one_move,
                    &observations,
                    &config,
                    &plan,
                    &retention,
                    WithinStratumResamplingPolicy::default(),
                    &steps,
                )
            })
            .unwrap();
        let four_move = RecordingPostResampleMove::default();
        let four = ThreadPoolBuilder::new()
            .num_threads(4)
            .build()
            .unwrap()
            .install(|| {
                run_stratified_bootstrap_filter_with_post_resample_move(
                    &PostResampleMoveModel,
                    &four_move,
                    &observations,
                    &config,
                    &plan,
                    &retention,
                    WithinStratumResamplingPolicy::default(),
                    &steps,
                )
            })
            .unwrap();

        let one_invocations = one_move.canonical_invocations();
        let four_invocations = four_move.canonical_invocations();
        assert_eq!(one_invocations, four_invocations);
        assert_eq!(one_invocations.len(), config.particles);
        assert_eq!(
            one_invocations
                .values()
                .map(|(_, draw)| draw)
                .collect::<BTreeSet<_>>()
                .len(),
            config.particles
        );
        for output_slot in 0..config.particles {
            let expected_stratum = if output_slot < 4 {
                StratumId(30)
            } else {
                StratumId(40)
            };
            let expected_parent = if output_slot < 4 { 0 } else { 4 };
            let (context, draw) = one_invocations[&output_slot];
            assert_eq!(
                context,
                StratifiedPostResampleMoveContext {
                    observation_index: 0,
                    observation_time_s: 1.0,
                    stratum: expected_stratum,
                    output_slot,
                    parent_slot: expected_parent,
                }
            );
            let expected_draw = rng_for(
                config.seed,
                STRATIFIED_POST_RESAMPLE_MOVE_RNG_DOMAIN,
                0,
                output_slot,
                expected_stratum.0 as u64,
            )
            .gen::<u64>();
            assert_eq!(draw, expected_draw);
            assert_eq!(one.pooled.particles[output_slot].move_draw, Some(draw));
        }

        assert_eq!(one.pooled.log_weights, legacy.log_weights);
        assert_eq!(one.pooled.root_ids, legacy.root_ids);
        assert_eq!(one.pooled.ancestry, legacy.ancestry);
        assert_eq!(one.pooled.checkpoints, legacy.checkpoints);
        assert_eq!(one.pooled.log_evidence, legacy.log_evidence);
        assert_eq!(
            serde_json::to_vec(&one).unwrap(),
            serde_json::to_vec(&four).unwrap()
        );

        let first = &one.post_resample_move_checkpoints[0];
        assert_eq!(first.step, StratifiedPostResampleMoveStep::Apply);
        assert!(first.posterior_resampling_occurred);
        assert_eq!(first.output_move_invocations, 8);
        assert_eq!(
            first.strata,
            vec![
                StratifiedPostResampleMoveStratumCheckpoint {
                    stratum: StratumId(30),
                    output_slot_start: 0,
                    output_slot_end_exclusive: 4,
                    output_move_invocations: 4,
                    distinct_parent_slots: 1,
                    distinct_prior_roots: 1,
                },
                StratifiedPostResampleMoveStratumCheckpoint {
                    stratum: StratumId(40),
                    output_slot_start: 4,
                    output_slot_end_exclusive: 8,
                    output_move_invocations: 4,
                    distinct_parent_slots: 1,
                    distinct_prior_roots: 1,
                },
            ]
        );
        let second = &one.post_resample_move_checkpoints[1];
        assert_eq!(second.step, StratifiedPostResampleMoveStep::Apply);
        assert!(!second.posterior_resampling_occurred);
        assert_eq!(second.output_move_invocations, 0);
        assert!(second.strata.is_empty());
    }

    #[test]
    fn post_resample_move_records_zero_when_resampling_does_not_occur() {
        let observations = [
            PostResampleMoveObservation {
                time_s: 1.0,
                favored_particle_within_stratum: None,
            },
            PostResampleMoveObservation {
                time_s: 2.0,
                favored_particle_within_stratum: None,
            },
        ];
        let move_kernel = RecordingPostResampleMove::default();
        let result = run_stratified_bootstrap_filter_with_post_resample_move(
            &PostResampleMoveModel,
            &move_kernel,
            &observations,
            &post_resample_move_config(Algorithm::Bootstrap),
            &post_resample_move_plan(),
            &SnapshotRetention::None,
            WithinStratumResamplingPolicy::default(),
            &[
                StratifiedPostResampleMoveStep::Apply,
                StratifiedPostResampleMoveStep::Apply,
            ],
        )
        .unwrap();

        assert!(move_kernel.canonical_invocations().is_empty());
        assert_eq!(result.post_resample_move_checkpoints.len(), 2);
        assert!(result
            .post_resample_move_checkpoints
            .iter()
            .all(|checkpoint| !checkpoint.posterior_resampling_occurred
                && checkpoint.output_move_invocations == 0
                && checkpoint.strata.is_empty()));
    }

    #[test]
    fn inactive_post_resample_move_step_records_resampling_without_calls() {
        let observations = forced_post_resample_move_observations();
        let move_kernel = RecordingPostResampleMove::default();
        let result = run_stratified_bootstrap_filter_with_post_resample_move(
            &PostResampleMoveModel,
            &move_kernel,
            &observations,
            &post_resample_move_config(Algorithm::Bootstrap),
            &post_resample_move_plan(),
            &SnapshotRetention::None,
            WithinStratumResamplingPolicy::default(),
            &[
                StratifiedPostResampleMoveStep::Inactive,
                StratifiedPostResampleMoveStep::Apply,
            ],
        )
        .unwrap();

        assert!(move_kernel.canonical_invocations().is_empty());
        let first = &result.post_resample_move_checkpoints[0];
        assert_eq!(first.step, StratifiedPostResampleMoveStep::Inactive);
        assert!(first.posterior_resampling_occurred);
        assert_eq!(first.output_move_invocations, 0);
        assert!(first.strata.is_empty());
    }

    #[test]
    fn post_resample_move_rejects_unsupported_modes_and_invalid_schedule() {
        let observations = forced_post_resample_move_observations();
        let auxiliary_error = run_stratified_bootstrap_filter_with_post_resample_move(
            &PostResampleMoveModel,
            &NoopStratifiedPostResampleMove,
            &observations,
            &post_resample_move_config(Algorithm::Auxiliary),
            &post_resample_move_plan(),
            &SnapshotRetention::None,
            WithinStratumResamplingPolicy::default(),
            &[
                StratifiedPostResampleMoveStep::Apply,
                StratifiedPostResampleMoveStep::Apply,
            ],
        )
        .unwrap_err();
        assert!(matches!(
            auxiliary_error,
            SmcError::InvalidConfiguration("post-resampling moves require the bootstrap algorithm")
        ));

        let schedule_error = run_stratified_bootstrap_filter_with_post_resample_move(
            &PostResampleMoveModel,
            &NoopStratifiedPostResampleMove,
            &observations,
            &post_resample_move_config(Algorithm::Bootstrap),
            &post_resample_move_plan(),
            &SnapshotRetention::None,
            WithinStratumResamplingPolicy::default(),
            &[StratifiedPostResampleMoveStep::Apply],
        )
        .unwrap_err();
        assert!(matches!(
            schedule_error,
            SmcError::InvalidConfiguration(
                "post-resampling move steps must match the observation count"
            )
        ));

        let smoothing_error = run_stratified_bootstrap_filter_with_post_resample_move(
            &PostResampleMoveModel,
            &NoopStratifiedPostResampleMove,
            &observations,
            &post_resample_move_config(Algorithm::Bootstrap),
            &post_resample_move_plan(),
            &SnapshotRetention::All,
            WithinStratumResamplingPolicy::default(),
            &[
                StratifiedPostResampleMoveStep::Apply,
                StratifiedPostResampleMoveStep::Apply,
            ],
        )
        .unwrap_err();
        assert!(matches!(
            smoothing_error,
            SmcError::InvalidConfiguration(
                "post-resampling moves do not support intermediate snapshots or smoothing"
            )
        ));
    }

    #[test]
    fn post_resample_move_maps_model_errors_and_enforces_stratum_identity() {
        let observations = forced_post_resample_move_observations();
        let config = post_resample_move_config(Algorithm::Bootstrap);
        let plan = post_resample_move_plan();
        let steps = [
            StratifiedPostResampleMoveStep::Apply,
            StratifiedPostResampleMoveStep::Inactive,
        ];
        let model_error = run_stratified_bootstrap_filter_with_post_resample_move(
            &PostResampleMoveModel,
            &FailingPostResampleMove,
            &observations,
            &config,
            &plan,
            &SnapshotRetention::None,
            WithinStratumResamplingPolicy::default(),
            &steps,
        )
        .unwrap_err();
        assert!(matches!(
            model_error,
            SmcError::Model(message) if message == "toy model error"
        ));

        let stratum_error = run_stratified_bootstrap_filter_with_post_resample_move(
            &PostResampleMoveModel,
            &StratumChangingPostResampleMove,
            &observations,
            &config,
            &plan,
            &SnapshotRetention::None,
            WithinStratumResamplingPolicy::default(),
            &steps,
        )
        .unwrap_err();
        assert!(matches!(stratum_error, SmcError::StratumMismatch));
    }

    #[test]
    fn allocation_correction_recovers_declared_initial_stratum_mass() {
        let result = run_stratified_filter(&MarkedJumpModel, &[], &config(), &plan(false)).unwrap();
        assert!(result.initial_log_evidence.abs() < 1e-12);
        assert_eq!(result.initial_strata.len(), 2);
        assert!((result.initial_strata[0].posterior_mass - 0.7).abs() < 1e-12);
        assert!((result.initial_strata[1].posterior_mass - 0.3).abs() < 1e-12);
    }

    #[test]
    fn marked_jump_filter_recovers_observed_high_rate_history_and_ancestry() {
        let observations = [
            Observation {
                time: 2.0,
                position: 2.0,
            },
            Observation {
                time: 4.0,
                position: 4.0,
            },
            Observation {
                time: 6.0,
                position: 6.0,
            },
        ];
        let result = run_stratified_filter_with_options(
            &MarkedJumpModel,
            &observations,
            &config(),
            &plan(false),
            FilterRunOptions {
                retain_snapshots: true,
            },
        )
        .unwrap();
        let mean = result
            .particles
            .iter()
            .zip(result.normalized_weights())
            .map(|(state, weight)| state.position * weight)
            .sum::<f64>();
        let high_rate_mass = result
            .checkpoints
            .last()
            .unwrap()
            .strata
            .iter()
            .find(|entry| entry.id == StratumId(20))
            .unwrap()
            .posterior_mass;
        assert!((mean - 6.0).abs() < 0.35, "posterior mean was {mean}");
        assert!(high_rate_mass > 0.8, "high-rate mass was {high_rate_mass}");
        assert_eq!(result.ancestry.len(), observations.len());

        let mut conditional = vec![f64::NEG_INFINITY; result.particles.len()];
        conditional[17] = 0.0;
        let smoothed = result
            .aggregate_descendant_weights_at_snapshot(1, &conditional)
            .unwrap();
        assert_eq!(smoothed.observation_index, Some(0));
        assert_eq!(
            smoothed
                .normalized_log_weights
                .iter()
                .filter(|value| value.is_finite())
                .count(),
            1
        );
        let mut expected_ancestor = 17usize;
        for step in result.ancestry[1..].iter().rev() {
            expected_ancestor = step.parent_indices[expected_ancestor];
        }
        assert!(smoothed.normalized_log_weights[expected_ancestor].abs() < 1e-14);
        assert_eq!(smoothed.descendant_counts.iter().sum::<usize>(), 2_000);
    }

    #[test]
    fn canonical_strata_and_keyed_streams_are_order_and_thread_invariant() {
        let observations = [Observation {
            time: 2.0,
            position: 2.0,
        }];
        let one = ThreadPoolBuilder::new()
            .num_threads(1)
            .build()
            .unwrap()
            .install(|| {
                run_stratified_filter(&MarkedJumpModel, &observations, &config(), &plan(false))
            })
            .unwrap();
        let four_reversed = ThreadPoolBuilder::new()
            .num_threads(4)
            .build()
            .unwrap()
            .install(|| {
                run_stratified_filter(&MarkedJumpModel, &observations, &config(), &plan(true))
            })
            .unwrap();
        assert_eq!(
            serde_json::to_vec(&one).unwrap(),
            serde_json::to_vec(&four_reversed).unwrap()
        );

        let policy = WithinStratumResamplingPolicy {
            uniform_root_mixture_epsilon: 0.2,
        };
        let one_defensive = ThreadPoolBuilder::new()
            .num_threads(1)
            .build()
            .unwrap()
            .install(|| {
                run_stratified_filter_with_resampling_policy(
                    &MarkedJumpModel,
                    &observations,
                    &config(),
                    &plan(false),
                    policy,
                )
            })
            .unwrap();
        let four_defensive_reversed = ThreadPoolBuilder::new()
            .num_threads(4)
            .build()
            .unwrap()
            .install(|| {
                run_stratified_filter_with_resampling_policy(
                    &MarkedJumpModel,
                    &observations,
                    &config(),
                    &plan(true),
                    policy,
                )
            })
            .unwrap();
        assert_eq!(
            serde_json::to_vec(&one_defensive).unwrap(),
            serde_json::to_vec(&four_defensive_reversed).unwrap()
        );
    }

    #[test]
    fn defensive_proposal_is_uniform_over_positive_roots_not_clones() {
        let target = [
            0.45_f64.ln(),
            0.45_f64.ln(),
            0.1_f64.ln(),
            f64::NEG_INFINITY,
        ];
        let roots = [10, 10, 20, 30];
        let proposal = defensive_root_log_probabilities(
            &target,
            &roots,
            WithinStratumResamplingPolicy {
                uniform_root_mixture_epsilon: 0.2,
            },
        )
        .unwrap();
        let linear = proposal.iter().map(|value| value.exp()).collect::<Vec<_>>();
        assert!((linear[0] - 0.41).abs() < 1e-14);
        assert!((linear[1] - 0.41).abs() < 1e-14);
        assert!((linear[2] - 0.18).abs() < 1e-14);
        assert_eq!(proposal[3], f64::NEG_INFINITY);
        assert!(((target[0] - proposal[0]).exp() - 0.45 / 0.41).abs() < 1e-14);
        assert!(((target[2] - proposal[2]).exp() - 0.1 / 0.18).abs() < 1e-14);

        let unchanged = defensive_root_log_probabilities(
            &target,
            &roots,
            WithinStratumResamplingPolicy::default(),
        )
        .unwrap();
        assert_eq!(unchanged, target);
    }

    #[test]
    fn checkpoint_root_mass_diagnostics_ignore_clone_counts() {
        let log_weights = [0.7_f64, 0.2, 0.099_998, 0.000_002]
            .into_iter()
            .map(f64::ln)
            .collect::<Vec<_>>();
        let diagnostics = weight_diagnostics(
            &log_weights,
            &[0, 0, 1, 2],
            &[StratumId(1), StratumId(1), StratumId(1), StratumId(1)],
        )
        .unwrap();
        assert_eq!(diagnostics.distinct_root_ancestors, 3);
        assert!((diagnostics.maximum_root_weight - 0.9).abs() < 1e-14);
        assert_eq!(diagnostics.roots_with_mass_at_least_1e_6, 3);
        assert_eq!(diagnostics.roots_with_mass_at_least_1e_3, 2);
        let expected_root_ess =
            1.0 / (0.9_f64.powi(2) + 0.099_998_f64.powi(2) + 0.000_002_f64.powi(2));
        assert!((diagnostics.root_effective_sample_size - expected_root_ess).abs() < 1e-12);
    }

    #[test]
    fn checkpoint_root_counts_exclude_exactly_zero_mass_slots() {
        let diagnostics = weight_diagnostics(
            &[0.75_f64.ln(), 0.25_f64.ln(), f64::NEG_INFINITY],
            &[7, 8, 9],
            &[StratumId(1), StratumId(1), StratumId(1)],
        )
        .unwrap();
        assert_eq!(diagnostics.distinct_root_ancestors, 2);
        assert_eq!(diagnostics.strata[0].distinct_root_ancestors, 2);
        assert_eq!(diagnostics.roots_with_mass_at_least_1e_6, 2);
    }

    #[derive(Debug, Clone, Copy)]
    struct DelayedRareState {
        rare: bool,
        stratum: StratumId,
    }

    #[derive(Debug, Clone, Copy)]
    struct DelayedRareObservation {
        time: f64,
        rare_log_likelihood: f64,
    }

    struct DelayedRareModel;

    impl ParticleModel for DelayedRareModel {
        type State = DelayedRareState;
        type Observation = DelayedRareObservation;
        type Error = ToyError;

        fn observation_time_s(&self, observation: &Self::Observation) -> f64 {
            observation.time
        }

        fn initialize(
            &self,
            particle_index: usize,
            _rng: &mut rand_chacha::ChaCha8Rng,
        ) -> Result<Self::State, Self::Error> {
            Ok(DelayedRareState {
                rare: particle_index == 0,
                stratum: StratumId(30),
            })
        }

        fn initialize_in_stratum(
            &self,
            stratum: StratumId,
            particle_index: usize,
            _particle_index_within_stratum: usize,
            _particles_in_stratum: usize,
            _rng: &mut rand_chacha::ChaCha8Rng,
        ) -> Result<Initialization<Self::State>, Self::Error> {
            Ok(Initialization::from_prior(DelayedRareState {
                rare: particle_index == 0,
                stratum,
            }))
        }

        fn stratum(&self, state: &Self::State) -> StratumId {
            state.stratum
        }

        fn propose(
            &self,
            state: &Self::State,
            _observation: &Self::Observation,
            _elapsed_seconds: f64,
            _rng: &mut rand_chacha::ChaCha8Rng,
        ) -> Result<Proposal<Self::State>, Self::Error> {
            Ok(Proposal::from_prior(*state))
        }

        fn log_likelihood(
            &self,
            state: &Self::State,
            observation: &Self::Observation,
        ) -> Result<f64, Self::Error> {
            Ok(if state.rare {
                observation.rare_log_likelihood
            } else {
                0.0
            })
        }
    }

    #[test]
    fn delayed_rare_root_survives_with_exact_correction_and_evidence() {
        let rare_suppression = 1.0e-6_f64.ln();
        let observations = [
            DelayedRareObservation {
                time: 1.0,
                rare_log_likelihood: rare_suppression,
            },
            DelayedRareObservation {
                time: 2.0,
                rare_log_likelihood: rare_suppression,
            },
            DelayedRareObservation {
                time: 3.0,
                rare_log_likelihood: -2.0 * rare_suppression,
            },
        ];
        let config = FilterConfig {
            particles: 100,
            seed: 73,
            algorithm: Algorithm::Bootstrap,
            initial_time_s: 0.0,
            ess_resample_fraction: 1.0,
        };
        let plan = StratifiedFilterPlan {
            strata: vec![StratumAllocation {
                id: StratumId(30),
                particles: 100,
                log_prior_probability: 0.0,
            }],
        };
        let ordinary =
            run_stratified_filter(&DelayedRareModel, &observations, &config, &plan).unwrap();
        assert!(!ordinary.root_ids.contains(&0));

        let defensive = run_stratified_filter_with_resampling_policy(
            &DelayedRareModel,
            &observations,
            &config,
            &plan,
            WithinStratumResamplingPolicy {
                uniform_root_mixture_epsilon: 1.0,
            },
        )
        .unwrap();
        assert!(defensive.root_ids.contains(&0));
        assert!(defensive.log_evidence.abs() < 1e-10);
        assert!(ordinary.log_evidence < -0.009);
    }

    #[test]
    fn selected_snapshots_compose_ancestry_across_skipped_epochs() {
        let observations = [
            Observation {
                time: 2.0,
                position: 2.0,
            },
            Observation {
                time: 4.0,
                position: 4.0,
            },
            Observation {
                time: 6.0,
                position: 6.0,
            },
        ];
        let result = run_stratified_filter_with_snapshot_retention(
            &MarkedJumpModel,
            &observations,
            &config(),
            &plan(false),
            &SnapshotRetention::SelectedObservationIndices(vec![0]),
        )
        .unwrap();
        assert_eq!(result.snapshots.len(), 2);
        assert_eq!(result.snapshots[0].observation_index, Some(0));
        assert_eq!(result.snapshots[1].observation_index, Some(2));
        assert_eq!(result.ancestry.len(), 1);
        assert_eq!(result.ancestry[0].parent_observation_index, Some(0));
        assert_eq!(result.ancestry[0].child_observation_index, 2);

        let smoothed = result
            .aggregate_descendant_weights_at_snapshot(0, &result.log_weights)
            .unwrap();
        assert_eq!(smoothed.observation_index, Some(0));
        let sum = smoothed
            .normalized_log_weights
            .iter()
            .map(|value| value.exp())
            .sum::<f64>();
        assert!((sum - 1.0).abs() < 1e-12);
    }

    #[derive(Debug, Clone, Copy, PartialEq, Serialize, Deserialize)]
    struct PoolState {
        stratum: StratumId,
        initial_root: usize,
        random_coordinate: f64,
        assimilated_observations: usize,
    }

    #[derive(Debug, Clone, Copy)]
    enum PoolLikelihood {
        All,
        ByInitialRoot([f64; 4]),
        ByStratum {
            selected: StratumId,
            selected_log_likelihood: f64,
            other_log_likelihood: f64,
        },
        RejectStratum(StratumId),
        Distance(f64),
    }

    #[derive(Debug, Clone, Copy)]
    struct PoolObservation {
        time_s: f64,
        likelihood: PoolLikelihood,
    }

    struct PoolModel {
        transition_log_prior_over_proposal: f64,
        random_transition: bool,
    }

    impl PoolModel {
        const fn from_prior() -> Self {
            Self {
                transition_log_prior_over_proposal: 0.0,
                random_transition: false,
            }
        }
    }

    impl ParticleModel for PoolModel {
        type State = PoolState;
        type Observation = PoolObservation;
        type Error = ToyError;

        fn observation_time_s(&self, observation: &Self::Observation) -> f64 {
            observation.time_s
        }

        fn initialize(
            &self,
            particle_index: usize,
            _rng: &mut rand_chacha::ChaCha8Rng,
        ) -> Result<Self::State, Self::Error> {
            Ok(PoolState {
                stratum: StratumId::default(),
                initial_root: particle_index,
                random_coordinate: 0.0,
                assimilated_observations: 0,
            })
        }

        fn initialize_in_stratum(
            &self,
            stratum: StratumId,
            particle_index: usize,
            _particle_index_within_stratum: usize,
            _particles_in_stratum: usize,
            _rng: &mut rand_chacha::ChaCha8Rng,
        ) -> Result<Initialization<Self::State>, Self::Error> {
            Ok(Initialization::from_prior(PoolState {
                stratum,
                initial_root: particle_index,
                random_coordinate: 0.0,
                assimilated_observations: 0,
            }))
        }

        fn stratum(&self, state: &Self::State) -> StratumId {
            state.stratum
        }

        fn propose(
            &self,
            state: &Self::State,
            _observation: &Self::Observation,
            _elapsed_seconds: f64,
            rng: &mut rand_chacha::ChaCha8Rng,
        ) -> Result<Proposal<Self::State>, Self::Error> {
            let mut state = *state;
            if self.random_transition {
                state.random_coordinate += rng.gen::<f64>();
            }
            Ok(Proposal {
                state,
                log_prior_over_proposal: self.transition_log_prior_over_proposal,
            })
        }

        fn log_likelihood(
            &self,
            state: &Self::State,
            observation: &Self::Observation,
        ) -> Result<f64, Self::Error> {
            Ok(match observation.likelihood {
                PoolLikelihood::All => 0.0,
                PoolLikelihood::ByInitialRoot(log_likelihoods) => {
                    log_likelihoods[state.initial_root]
                }
                PoolLikelihood::ByStratum {
                    selected,
                    selected_log_likelihood,
                    other_log_likelihood,
                } => {
                    if state.stratum == selected {
                        selected_log_likelihood
                    } else {
                        other_log_likelihood
                    }
                }
                PoolLikelihood::RejectStratum(rejected) => {
                    if state.stratum == rejected {
                        f64::NEG_INFINITY
                    } else {
                        0.0
                    }
                }
                PoolLikelihood::Distance(target) => {
                    -0.5 * (state.random_coordinate - target).powi(2)
                }
            })
        }

        fn observe(
            &self,
            state: &mut Self::State,
            observation: &Self::Observation,
        ) -> Result<f64, Self::Error> {
            let likelihood = self.log_likelihood(state, observation)?;
            state.assimilated_observations += 1;
            Ok(likelihood)
        }
    }

    #[derive(Debug, Clone, Copy, PartialEq, Serialize, Deserialize)]
    struct PoolSelectionGuidePoint {
        favored_roots_below: usize,
        favored_log_guide: f64,
        other_log_guide: f64,
    }

    struct PoolSelectionGuide;

    impl SelectionGuide<PoolModel> for PoolSelectionGuide {
        type Point = PoolSelectionGuidePoint;

        fn log_selection_guide(
            &self,
            _model: &PoolModel,
            state: &PoolState,
            _endpoint_observation: &PoolObservation,
            point: &Self::Point,
        ) -> Result<f64, ToyError> {
            Ok(if state.initial_root < point.favored_roots_below {
                point.favored_log_guide
            } else {
                point.other_log_guide
            })
        }
    }

    #[derive(Debug, Clone, Copy, PartialEq, Serialize, Deserialize)]
    struct PoolPersistentTwistPoint {
        favored_roots_below: usize,
        favored_log_potential: f64,
        other_log_potential: f64,
    }

    struct PoolPersistentTwist;

    impl PersistentTwist<PoolModel> for PoolPersistentTwist {
        type Point = PoolPersistentTwistPoint;

        fn log_twist_potential(
            &self,
            _model: &PoolModel,
            state: &PoolState,
            _endpoint_observation: &PoolObservation,
            point: &Self::Point,
        ) -> Result<f64, ToyError> {
            Ok(if state.initial_root < point.favored_roots_below {
                point.favored_log_potential
            } else {
                point.other_log_potential
            })
        }
    }

    #[derive(Debug, Clone, Copy, PartialEq, Serialize, Deserialize)]
    struct PoolBridgePoint {
        time_s: f64,
        log_potentials: [f64; 4],
        transition_log_prior_over_proposal: f64,
        context_bit: u8,
    }

    #[derive(Debug, Clone, Copy)]
    struct PoolBridgeContext {
        seen_points: u8,
    }

    struct PoolIntermediateBridge {
        endpoint_log_prior_over_proposal: f64,
        record_context_in_coordinate: bool,
    }

    impl IntermediatePotentialBridge<PoolModel> for PoolIntermediateBridge {
        type Point = PoolBridgePoint;
        type Context = PoolBridgeContext;

        fn point_time_s(&self, point: &Self::Point) -> f64 {
            point.time_s
        }

        fn begin_interval(
            &self,
            _model: &PoolModel,
            _state: &PoolState,
            _endpoint_observation: &PoolObservation,
        ) -> Result<Self::Context, ToyError> {
            Ok(PoolBridgeContext { seen_points: 0 })
        }

        fn propose_to_point(
            &self,
            model: &PoolModel,
            state: &PoolState,
            endpoint_observation: &PoolObservation,
            point: &Self::Point,
            context: &Self::Context,
            elapsed_seconds: f64,
            rng: &mut ChaCha8Rng,
        ) -> Result<IntermediatePotentialProposal<PoolState, Self::Context>, ToyError> {
            let mut proposal = model.propose(state, endpoint_observation, elapsed_seconds, rng)?;
            proposal.log_prior_over_proposal += point.transition_log_prior_over_proposal;
            Ok(IntermediatePotentialProposal {
                proposal,
                context: PoolBridgeContext {
                    seen_points: context.seen_points | point.context_bit,
                },
            })
        }

        fn propose_to_endpoint(
            &self,
            model: &PoolModel,
            state: &PoolState,
            endpoint_observation: &PoolObservation,
            context: &Self::Context,
            elapsed_seconds: f64,
            rng: &mut ChaCha8Rng,
        ) -> Result<Proposal<PoolState>, ToyError> {
            let mut proposal = model.propose(state, endpoint_observation, elapsed_seconds, rng)?;
            proposal.log_prior_over_proposal += self.endpoint_log_prior_over_proposal;
            if self.record_context_in_coordinate {
                proposal.state.random_coordinate += f64::from(context.seen_points);
            }
            Ok(proposal)
        }

        fn log_potential(
            &self,
            _model: &PoolModel,
            state: &PoolState,
            _endpoint_observation: &PoolObservation,
            point: &Self::Point,
        ) -> Result<f64, ToyError> {
            Ok(point.log_potentials[state.initial_root % point.log_potentials.len()])
        }
    }

    struct CountingPoolModel {
        endpoint_observations: std::sync::Arc<std::sync::atomic::AtomicUsize>,
    }

    impl ParticleModel for CountingPoolModel {
        type State = PoolState;
        type Observation = PoolObservation;
        type Error = ToyError;

        fn observation_time_s(&self, observation: &Self::Observation) -> f64 {
            observation.time_s
        }

        fn initialize(
            &self,
            particle_index: usize,
            _rng: &mut ChaCha8Rng,
        ) -> Result<Self::State, Self::Error> {
            Ok(PoolState {
                stratum: StratumId::default(),
                initial_root: particle_index,
                random_coordinate: 0.0,
                assimilated_observations: 0,
            })
        }

        fn initialize_in_stratum(
            &self,
            stratum: StratumId,
            particle_index: usize,
            _particle_index_within_stratum: usize,
            _particles_in_stratum: usize,
            _rng: &mut ChaCha8Rng,
        ) -> Result<Initialization<Self::State>, Self::Error> {
            Ok(Initialization::from_prior(PoolState {
                stratum,
                initial_root: particle_index,
                random_coordinate: 0.0,
                assimilated_observations: 0,
            }))
        }

        fn stratum(&self, state: &Self::State) -> StratumId {
            state.stratum
        }

        fn propose(
            &self,
            state: &Self::State,
            _observation: &Self::Observation,
            _elapsed_seconds: f64,
            _rng: &mut ChaCha8Rng,
        ) -> Result<Proposal<Self::State>, Self::Error> {
            Ok(Proposal::from_prior(*state))
        }

        fn log_likelihood(
            &self,
            _state: &Self::State,
            _observation: &Self::Observation,
        ) -> Result<f64, Self::Error> {
            Ok(0.0)
        }

        fn observe(
            &self,
            state: &mut Self::State,
            _observation: &Self::Observation,
        ) -> Result<f64, Self::Error> {
            self.endpoint_observations
                .fetch_add(1, std::sync::atomic::Ordering::SeqCst);
            state.assimilated_observations += 1;
            Ok(0.0)
        }
    }

    struct CountingPersistentTwist {
        evaluations: std::sync::Arc<std::sync::atomic::AtomicUsize>,
    }

    impl PersistentTwist<CountingPoolModel> for CountingPersistentTwist {
        type Point = ();

        fn log_twist_potential(
            &self,
            _model: &CountingPoolModel,
            _state: &PoolState,
            _endpoint_observation: &PoolObservation,
            _point: &Self::Point,
        ) -> Result<f64, ToyError> {
            self.evaluations
                .fetch_add(1, std::sync::atomic::Ordering::SeqCst);
            Ok(0.0)
        }
    }

    struct CountingIntermediateBridge {
        endpoint_proposals: std::sync::Arc<std::sync::atomic::AtomicUsize>,
    }

    impl IntermediatePotentialBridge<CountingPoolModel> for CountingIntermediateBridge {
        type Point = PoolBridgePoint;
        type Context = u8;

        fn point_time_s(&self, point: &Self::Point) -> f64 {
            point.time_s
        }

        fn begin_interval(
            &self,
            _model: &CountingPoolModel,
            _state: &PoolState,
            _endpoint_observation: &PoolObservation,
        ) -> Result<Self::Context, ToyError> {
            Ok(0)
        }

        fn propose_to_point(
            &self,
            _model: &CountingPoolModel,
            state: &PoolState,
            _endpoint_observation: &PoolObservation,
            point: &Self::Point,
            context: &Self::Context,
            _elapsed_seconds: f64,
            _rng: &mut ChaCha8Rng,
        ) -> Result<IntermediatePotentialProposal<PoolState, Self::Context>, ToyError> {
            Ok(IntermediatePotentialProposal {
                proposal: Proposal::from_prior(*state),
                context: *context | point.context_bit,
            })
        }

        fn propose_to_endpoint(
            &self,
            _model: &CountingPoolModel,
            state: &PoolState,
            _endpoint_observation: &PoolObservation,
            context: &Self::Context,
            _elapsed_seconds: f64,
            _rng: &mut ChaCha8Rng,
        ) -> Result<Proposal<PoolState>, ToyError> {
            if *context != 1 {
                return Err(ToyError);
            }
            self.endpoint_proposals
                .fetch_add(1, std::sync::atomic::Ordering::SeqCst);
            Ok(Proposal::from_prior(*state))
        }

        fn log_potential(
            &self,
            _model: &CountingPoolModel,
            _state: &PoolState,
            _endpoint_observation: &PoolObservation,
            _point: &Self::Point,
        ) -> Result<f64, ToyError> {
            Ok(0.0)
        }
    }

    fn pool_config(particles: usize, algorithm: Algorithm) -> FilterConfig {
        FilterConfig {
            particles,
            seed: 91_733,
            algorithm,
            initial_time_s: 0.0,
            ess_resample_fraction: 0.5,
        }
    }

    fn one_pool_stratum() -> StratifiedFilterPlan {
        one_pool_stratum_with_particles(4)
    }

    fn one_pool_stratum_with_particles(particles: usize) -> StratifiedFilterPlan {
        StratifiedFilterPlan {
            strata: vec![StratumAllocation {
                id: StratumId(30),
                particles,
                log_prior_probability: 0.0,
            }],
        }
    }

    fn assert_close(actual: f64, expected: f64) {
        assert!(
            (actual - expected).abs() < 1.0e-12,
            "expected {expected:.16e}, got {actual:.16e}"
        );
    }

    #[test]
    fn root_stratified_pool_uses_exact_root_mass_over_replicate_weight() {
        let stratum = StratumId(30);
        let states = vec![
            PoolState {
                stratum,
                initial_root: 0,
                random_coordinate: 0.0,
                assimilated_observations: 0,
            };
            5
        ];
        let linear_weights = [0.05_f64, 0.15, 0.30, 0.10, 0.40];
        let log_weights = linear_weights.map(f64::ln);
        let root_ids = [10, 10, 10, 20, 20];
        let stratum_ids = [stratum; 5];
        let config = pool_config(5, Algorithm::Bootstrap);
        let input = EpochInput {
            model: &PoolModel::from_prior(),
            states: &states,
            log_weights: &log_weights,
            root_ids: &root_ids,
            stratum_ids: &stratum_ids,
            observation: &PoolObservation {
                time_s: 1.0,
                likelihood: PoolLikelihood::All,
            },
            elapsed_seconds: 1.0,
            epoch: 0,
            config: &config,
            resampling_policy: WithinStratumResamplingPolicy::default(),
            retain_zero_mass_strata: true,
        };
        let allocations = [StratumAllocation {
            id: stratum,
            particles: 5,
            log_prior_probability: 0.0,
        }];
        let result = run_stratified_global_candidate_pool_epoch(
            &input,
            &allocations,
            CandidatePoolAllocation::PerPositiveRoot(3),
            1.0,
            &[(); 5],
            CandidatePoolRandomDomain::EndpointObservation,
            None,
            |ancestor, state, _| {
                let root_target: f64 = if root_ids[ancestor] == 10 { 2.0 } else { 0.5 };
                Ok((*state, 3.0_f64.ln(), root_target.ln(), ()))
            },
        )
        .unwrap();

        // Both roots have mass 0.5. The exact candidate normalizer is
        // 3 * (0.5 * 2 + 0.5 * 0.5) = 3.75, independent of clone counts.
        assert_close(
            result.checkpoint.candidate_log_evidence_increment,
            3.75_f64.ln(),
        );
        assert_eq!(result.checkpoint.configured_candidates, 6);
        assert_eq!(result.checkpoint.generated_candidates, 6);
        assert_eq!(result.checkpoint.strata[0].input_positive_roots, 2);
        assert_eq!(result.checkpoint.strata[0].sampled_ancestor_roots, 2);
        let root = result.root_stratified_checkpoint.unwrap();
        assert_eq!(root.candidates_per_positive_root, 3);
        assert_eq!(root.configured_candidates, 6);
        assert_close(
            root.first_split_candidate_log_evidence_increment.unwrap(),
            3.75_f64.ln(),
        );
        assert_close(
            root.second_split_candidate_log_evidence_increment.unwrap(),
            3.75_f64.ln(),
        );
        assert_close(root.split_candidate_root_total_variation.unwrap(), 0.0);
        let concentration = &root.strata[0];
        assert_eq!(concentration.minimum_positive_candidates_per_root, 3);
        assert_eq!(concentration.maximum_positive_candidates_per_root, 3);
        assert_close(
            concentration.minimum_within_root_candidate_effective_sample_size,
            3.0,
        );
        assert_close(
            concentration.maximum_within_root_candidate_weight,
            1.0 / 3.0,
        );
    }

    #[test]
    fn root_candidate_transition_streams_ignore_clone_order_and_other_roots() {
        let collect_draws = |root_ids: Vec<usize>, coordinates: Vec<f64>| {
            let stratum = StratumId(30);
            let states = coordinates
                .into_iter()
                .map(|random_coordinate| PoolState {
                    stratum,
                    initial_root: 0,
                    random_coordinate,
                    assimilated_observations: 0,
                })
                .collect::<Vec<_>>();
            let particle_count = states.len();
            let log_weights = vec![-(particle_count as f64).ln(); particle_count];
            let stratum_ids = vec![stratum; particle_count];
            let config = pool_config(particle_count, Algorithm::Bootstrap);
            let observation = PoolObservation {
                time_s: 1.0,
                likelihood: PoolLikelihood::All,
            };
            let input = EpochInput {
                model: &PoolModel::from_prior(),
                states: &states,
                log_weights: &log_weights,
                root_ids: &root_ids,
                stratum_ids: &stratum_ids,
                observation: &observation,
                elapsed_seconds: 1.0,
                epoch: 7,
                config: &config,
                resampling_policy: WithinStratumResamplingPolicy::default(),
                retain_zero_mass_strata: true,
            };
            let draws =
                std::sync::Arc::new(std::sync::Mutex::new(BTreeMap::<usize, Vec<f64>>::new()));
            let recorded = std::sync::Arc::clone(&draws);
            run_stratified_global_candidate_pool_epoch(
                &input,
                &[StratumAllocation {
                    id: stratum,
                    particles: particle_count,
                    log_prior_probability: 0.0,
                }],
                CandidatePoolAllocation::PerPositiveRoot(4),
                1.0,
                &vec![(); particle_count],
                CandidatePoolRandomDomain::EndpointObservation,
                None,
                |ancestor, state, rng| {
                    recorded
                        .lock()
                        .unwrap()
                        .entry(root_ids[ancestor])
                        .or_default()
                        .push(rng.gen::<f64>());
                    Ok((*state, 0.0, 0.0, ()))
                },
            )
            .unwrap();
            drop(recorded);
            let mut draws = std::sync::Arc::try_unwrap(draws)
                .unwrap()
                .into_inner()
                .unwrap();
            for values in draws.values_mut() {
                values.sort_by(f64::total_cmp);
            }
            draws
        };

        let baseline = collect_draws(vec![10, 10, 20], vec![1.0, 2.0, 3.0]);
        let perturbed = collect_draws(vec![10, 10, 30, 20], vec![2.0, 1.0, 9.0, 3.0]);
        assert_eq!(baseline[&10], perturbed[&10]);
        assert_eq!(baseline[&20], perturbed[&20]);
    }

    #[test]
    fn root_stratified_standard_pool_is_thread_invariant() {
        let observations = [PoolObservation {
            time_s: 1.0,
            likelihood: PoolLikelihood::Distance(0.4),
        }];
        let steps = [RootStratifiedTransitionPoolStep::Pool {
            candidates_per_positive_root: 4,
        }];
        let first = StratumAllocation {
            id: StratumId(10),
            particles: 4,
            log_prior_probability: 0.3_f64.ln(),
        };
        let second = StratumAllocation {
            id: StratumId(20),
            particles: 4,
            log_prior_probability: 0.7_f64.ln(),
        };
        let forward = StratifiedFilterPlan {
            strata: vec![first.clone(), second.clone()],
        };
        let reversed = StratifiedFilterPlan {
            strata: vec![second, first],
        };
        let run = |plan: &StratifiedFilterPlan| {
            run_stratified_filter_with_root_stratified_transition_pool(
                &PoolModel {
                    transition_log_prior_over_proposal: 0.0,
                    random_transition: true,
                },
                &observations,
                &pool_config(8, Algorithm::Bootstrap),
                plan,
                &SnapshotRetention::All,
                WithinStratumResamplingPolicy {
                    uniform_root_mixture_epsilon: 0.2,
                },
                &steps,
            )
            .unwrap()
        };
        let one = ThreadPoolBuilder::new()
            .num_threads(1)
            .build()
            .unwrap()
            .install(|| run(&forward));
        let four = ThreadPoolBuilder::new()
            .num_threads(4)
            .build()
            .unwrap()
            .install(|| run(&reversed));
        assert_eq!(
            serde_json::to_vec(&one).unwrap(),
            serde_json::to_vec(&four).unwrap()
        );
        let ordinary = &one.transition_pool_checkpoints[0];
        let root = &one.root_stratified_candidate_pool_checkpoints[0];
        assert_eq!(ordinary.candidates_per_particle, 0);
        assert_eq!(ordinary.observation_index, root.observation_index);
        assert_close(ordinary.observation_time_s, root.observation_time_s);
        assert_eq!(ordinary.configured_candidates, root.configured_candidates);
        assert_eq!(ordinary.generated_candidates, root.generated_candidates);
    }

    #[test]
    fn root_stratified_bridge_uses_root_pools_at_points_and_endpoint_without_followup_resampling() {
        let observations = [
            PoolObservation {
                time_s: 2.0,
                likelihood: PoolLikelihood::ByInitialRoot([
                    0.97_f64.ln(),
                    0.01_f64.ln(),
                    0.01_f64.ln(),
                    0.01_f64.ln(),
                ]),
            },
            PoolObservation {
                time_s: 3.0,
                likelihood: PoolLikelihood::All,
            },
        ];
        let steps = [
            RootStratifiedIntermediatePotentialStep::Bridge {
                points: vec![RootStratifiedIntermediatePotentialBridgePoint {
                    point: PoolBridgePoint {
                        time_s: 1.0,
                        log_potentials: [0.25_f64.ln(); 4],
                        transition_log_prior_over_proposal: 0.0,
                        context_bit: 1,
                    },
                    candidates_per_positive_root: 2,
                }],
                endpoint_candidates_per_positive_root: 3,
            },
            RootStratifiedIntermediatePotentialStep::Standard,
        ];
        let mut config = pool_config(4, Algorithm::Bootstrap);
        config.ess_resample_fraction = 1.0;
        let policy = WithinStratumResamplingPolicy {
            uniform_root_mixture_epsilon: 0.5,
        };
        let plan = one_pool_stratum();
        let result = run_stratified_filter_with_root_stratified_intermediate_potentials(
            &PoolModel::from_prior(),
            &PoolIntermediateBridge {
                endpoint_log_prior_over_proposal: 0.0,
                record_context_in_coordinate: false,
            },
            &observations,
            &config,
            &plan,
            &SnapshotRetention::All,
            policy,
            &steps,
        )
        .unwrap();

        assert_eq!(result.root_stratified_candidate_pool_checkpoints.len(), 2);
        let point = &result.root_stratified_candidate_pool_checkpoints[0];
        assert_eq!(
            point.location,
            RootStratifiedCandidatePoolLocation::IntermediatePoint { point_index: 0 }
        );
        assert_eq!(point.configured_candidates, 8);
        let ordinary_point = &result.intermediate_potential_checkpoints[0].points[0].candidate_pool;
        assert_eq!(ordinary_point.candidates_per_particle, 0);
        assert_eq!(ordinary_point.observation_index, point.observation_index);
        assert_close(ordinary_point.observation_time_s, point.observation_time_s);
        assert_eq!(
            ordinary_point.configured_candidates,
            point.configured_candidates
        );
        let endpoint = &result.root_stratified_candidate_pool_checkpoints[1];
        assert_eq!(
            endpoint.location,
            RootStratifiedCandidatePoolLocation::IntermediateEndpoint { point_count: 1 }
        );
        assert_eq!(endpoint.configured_candidates, 12);
        let ordinary_endpoint = result.intermediate_potential_checkpoints[0]
            .endpoint
            .candidate_pool
            .as_ref()
            .unwrap();
        assert_eq!(ordinary_endpoint.candidates_per_particle, 0);
        assert_eq!(
            ordinary_endpoint.observation_index,
            endpoint.observation_index
        );
        assert_close(
            ordinary_endpoint.observation_time_s,
            endpoint.observation_time_s,
        );
        assert_eq!(
            ordinary_endpoint.configured_candidates,
            endpoint.configured_candidates
        );
        assert!(result.pooled.log_evidence.is_finite());

        // The first root-pooled bridge is deliberately nonfinal and has low
        // enough ESS that an ordinary follow-up resampling would run without
        // the root-pool guard. Prove that such a resampling would be nontrivial,
        // then verify the identity ancestry carried into the neutral epoch.
        let bridge_snapshot = result
            .pooled
            .snapshots
            .iter()
            .find(|snapshot| snapshot.observation_index == Some(0))
            .unwrap();
        let would_resample = resample_within_strata(ResampleWithinStrataInput {
            states: &bridge_snapshot.particles,
            log_weights: &bridge_snapshot.log_weights,
            root_ids: &bridge_snapshot.root_ids,
            stratum_ids: &bridge_snapshot.stratum_ids,
            allocations: &plan.canonical_allocations(),
            seed: config.seed,
            epoch: 0,
            policy,
            retain_zero_mass_strata: true,
            conditional_ess_resample_fraction: None,
        })
        .unwrap();
        assert_ne!(would_resample.parent_indices, (0..4).collect::<Vec<_>>());
        let neutral_ancestry = result
            .pooled
            .ancestry
            .iter()
            .find(|step| step.child_observation_index == 1)
            .unwrap();
        assert_eq!(neutral_ancestry.parent_observation_index, Some(0));
        assert_eq!(neutral_ancestry.parent_indices, (0..4).collect::<Vec<_>>());
    }

    #[test]
    fn global_pool_defensive_output_uses_exact_candidate_target_correction() {
        let linear_likelihoods = [0.7_f64, 0.2, 0.09, 0.01];
        let observations = [PoolObservation {
            time_s: 1.0,
            likelihood: PoolLikelihood::ByInitialRoot(linear_likelihoods.map(f64::ln)),
        }];
        let policy = WithinStratumResamplingPolicy {
            uniform_root_mixture_epsilon: 0.5,
        };
        let result = run_stratified_filter_with_global_transition_pool(
            &PoolModel::from_prior(),
            &observations,
            &pool_config(4, Algorithm::Auxiliary),
            &one_pool_stratum(),
            &SnapshotRetention::All,
            policy,
            &[GlobalTransitionPoolStep::Pool {
                candidates_per_particle: 1,
            }],
        )
        .unwrap();
        let checkpoint = &result.transition_pool_checkpoints[0];
        assert_eq!(checkpoint.configured_candidates, 4);
        assert_eq!(checkpoint.generated_candidates, 4);
        assert_eq!(checkpoint.positive_candidates, 4);
        assert_eq!(checkpoint.strata[0].input_positive_roots, 4);
        assert_eq!(checkpoint.strata[0].sampled_ancestor_roots, 4);
        assert_close(checkpoint.candidate_log_evidence_increment, 0.25_f64.ln());
        assert_close(
            checkpoint.candidate_effective_sample_size,
            1.0 / linear_likelihoods
                .iter()
                .map(|likelihood| likelihood.powi(2))
                .sum::<f64>(),
        );
        assert_close(
            checkpoint.candidate_root_effective_sample_size,
            checkpoint.candidate_effective_sample_size,
        );

        let output_root_counts = (0..4)
            .map(|root| {
                result
                    .pooled
                    .root_ids
                    .iter()
                    .filter(|&&selected| selected == root)
                    .count()
            })
            .collect::<Vec<_>>();
        let output_root_proposal =
            linear_likelihoods.map(|probability| 0.5 * probability + 0.5 / 4.0);
        let realized_correction = output_root_counts
            .iter()
            .zip(linear_likelihoods)
            .zip(output_root_proposal)
            .map(|((&count, target), proposal)| count as f64 * target / proposal / 4.0)
            .sum::<f64>();
        assert_close(
            checkpoint.output_resampling_log_correction,
            realized_correction.ln(),
        );
        assert_close(
            checkpoint.realized_log_evidence_increment,
            0.25_f64.ln() + realized_correction.ln(),
        );
        assert_close(
            result.pooled.log_evidence,
            checkpoint.realized_log_evidence_increment,
        );

        let normalized_root_masses = (0..4)
            .map(|root| {
                result
                    .pooled
                    .root_ids
                    .iter()
                    .zip(&result.pooled.log_weights)
                    .filter(|(selected, _)| **selected == root)
                    .map(|(_, log_weight)| log_weight.exp())
                    .sum::<f64>()
            })
            .collect::<Vec<_>>();
        for root in 0..4 {
            assert_close(
                normalized_root_masses[root],
                output_root_counts[root] as f64 * linear_likelihoods[root]
                    / output_root_proposal[root]
                    / 4.0
                    / realized_correction,
            );
        }
        assert!(result
            .pooled
            .particles
            .iter()
            .all(|state| state.assimilated_observations == 1));
    }

    #[test]
    fn global_pool_includes_transition_importance_correction_in_evidence() {
        let observations = [PoolObservation {
            time_s: 1.0,
            likelihood: PoolLikelihood::ByInitialRoot([0.25_f64.ln(); 4]),
        }];
        let model = PoolModel {
            transition_log_prior_over_proposal: 2.0_f64.ln(),
            random_transition: false,
        };
        let result = run_stratified_filter_with_global_transition_pool(
            &model,
            &observations,
            &pool_config(4, Algorithm::Bootstrap),
            &one_pool_stratum(),
            &SnapshotRetention::None,
            WithinStratumResamplingPolicy::default(),
            &[GlobalTransitionPoolStep::Pool {
                candidates_per_particle: 3,
            }],
        )
        .unwrap();
        let checkpoint = &result.transition_pool_checkpoints[0];
        assert_close(checkpoint.candidate_log_evidence_increment, 0.5_f64.ln());
        assert_close(checkpoint.output_resampling_log_correction, 0.0);
        assert_close(result.pooled.log_evidence, 0.5_f64.ln());
    }

    #[test]
    fn global_pool_preserves_unequal_scientific_priors_and_allocations() {
        let plan = StratifiedFilterPlan {
            strata: vec![
                StratumAllocation {
                    id: StratumId(10),
                    particles: 2,
                    log_prior_probability: 0.25_f64.ln(),
                },
                StratumAllocation {
                    id: StratumId(20),
                    particles: 4,
                    log_prior_probability: 0.75_f64.ln(),
                },
            ],
        };
        let observations = [PoolObservation {
            time_s: 1.0,
            likelihood: PoolLikelihood::ByStratum {
                selected: StratumId(20),
                selected_log_likelihood: 3.0_f64.ln(),
                other_log_likelihood: 0.0,
            },
        }];
        let result = run_stratified_filter_with_global_transition_pool(
            &PoolModel::from_prior(),
            &observations,
            &pool_config(6, Algorithm::Auxiliary),
            &plan,
            &SnapshotRetention::None,
            WithinStratumResamplingPolicy::default(),
            &[GlobalTransitionPoolStep::Pool {
                candidates_per_particle: 3,
            }],
        )
        .unwrap();
        let checkpoint = &result.transition_pool_checkpoints[0];
        assert_close(checkpoint.candidate_log_evidence_increment, 2.5_f64.ln());
        assert_close(checkpoint.output_resampling_log_correction, 0.0);
        assert_close(checkpoint.strata[0].candidate_posterior_mass, 0.1);
        assert_close(checkpoint.strata[1].candidate_posterior_mass, 0.9);
        assert_close(checkpoint.strata[0].output_posterior_mass, 0.1);
        assert_close(checkpoint.strata[1].output_posterior_mass, 0.9);
        assert_close(result.pooled.log_evidence, 2.5_f64.ln());
    }

    #[test]
    fn global_pool_preserves_extinct_stratum_slots_and_smoothed_zero_mass() {
        let plan = StratifiedFilterPlan {
            strata: vec![
                StratumAllocation {
                    id: StratumId(10),
                    particles: 2,
                    log_prior_probability: 0.5_f64.ln(),
                },
                StratumAllocation {
                    id: StratumId(20),
                    particles: 2,
                    log_prior_probability: 0.5_f64.ln(),
                },
            ],
        };
        let observations = [
            PoolObservation {
                time_s: 1.0,
                likelihood: PoolLikelihood::All,
            },
            PoolObservation {
                time_s: 2.0,
                likelihood: PoolLikelihood::RejectStratum(StratumId(10)),
            },
            PoolObservation {
                time_s: 3.0,
                likelihood: PoolLikelihood::All,
            },
        ];
        let result = run_stratified_filter_with_global_transition_pool(
            &PoolModel::from_prior(),
            &observations,
            &pool_config(4, Algorithm::Auxiliary),
            &plan,
            &SnapshotRetention::All,
            WithinStratumResamplingPolicy::default(),
            &[
                GlobalTransitionPoolStep::Pool {
                    candidates_per_particle: 2,
                },
                GlobalTransitionPoolStep::Pool {
                    candidates_per_particle: 2,
                },
                GlobalTransitionPoolStep::Standard,
            ],
        )
        .unwrap();

        assert_close(result.pooled.log_evidence, 0.5_f64.ln());
        assert_eq!(result.pooled.snapshots.len(), 4);
        assert_eq!(result.pooled.ancestry.len(), 3);
        assert!(result.pooled.log_weights[..2]
            .iter()
            .all(|weight| *weight == f64::NEG_INFINITY));
        let extinction = &result.transition_pool_checkpoints[1].strata[0];
        assert_eq!(extinction.generated_candidates, 4);
        assert_eq!(extinction.positive_candidates, 0);
        assert_eq!(extinction.estimated_log_predictive_mass, None);
        assert_eq!(extinction.output_log_posterior_mass, None);
        let smoothed = result
            .pooled
            .aggregate_descendant_weights_at_snapshot(0, &result.pooled.log_weights)
            .unwrap();
        assert!(smoothed.normalized_log_weights[..2]
            .iter()
            .all(|weight| *weight == f64::NEG_INFINITY));
    }

    #[test]
    fn global_pool_is_plan_order_and_rayon_thread_invariant() {
        let first = StratumAllocation {
            id: StratumId(10),
            particles: 4,
            log_prior_probability: 0.3_f64.ln(),
        };
        let second = StratumAllocation {
            id: StratumId(20),
            particles: 4,
            log_prior_probability: 0.7_f64.ln(),
        };
        let forward = StratifiedFilterPlan {
            strata: vec![first.clone(), second.clone()],
        };
        let reversed = StratifiedFilterPlan {
            strata: vec![second, first],
        };
        let observations = [
            PoolObservation {
                time_s: 1.0,
                likelihood: PoolLikelihood::Distance(0.4),
            },
            PoolObservation {
                time_s: 2.0,
                likelihood: PoolLikelihood::Distance(0.8),
            },
        ];
        let steps = [
            GlobalTransitionPoolStep::Pool {
                candidates_per_particle: 3,
            },
            GlobalTransitionPoolStep::Standard,
        ];
        let model = PoolModel {
            transition_log_prior_over_proposal: 0.0,
            random_transition: true,
        };
        let filter_config = pool_config(8, Algorithm::Auxiliary);
        let one = ThreadPoolBuilder::new()
            .num_threads(1)
            .build()
            .unwrap()
            .install(|| {
                run_stratified_filter_with_global_transition_pool(
                    &model,
                    &observations,
                    &filter_config,
                    &forward,
                    &SnapshotRetention::All,
                    WithinStratumResamplingPolicy {
                        uniform_root_mixture_epsilon: 0.2,
                    },
                    &steps,
                )
            })
            .unwrap();
        let four = ThreadPoolBuilder::new()
            .num_threads(4)
            .build()
            .unwrap()
            .install(|| {
                run_stratified_filter_with_global_transition_pool(
                    &model,
                    &observations,
                    &filter_config,
                    &reversed,
                    &SnapshotRetention::All,
                    WithinStratumResamplingPolicy {
                        uniform_root_mixture_epsilon: 0.2,
                    },
                    &steps,
                )
            })
            .unwrap();
        assert_eq!(
            serde_json::to_vec(&one).unwrap(),
            serde_json::to_vec(&four).unwrap()
        );
    }

    #[test]
    fn standard_only_pool_schedule_preserves_the_legacy_result() {
        let observations = [PoolObservation {
            time_s: 1.0,
            likelihood: PoolLikelihood::ByInitialRoot([0.7_f64, 0.2, 0.09, 0.01].map(f64::ln)),
        }];
        let model = PoolModel::from_prior();
        let filter_config = pool_config(4, Algorithm::Bootstrap);
        let plan = one_pool_stratum();
        let legacy = run_stratified_filter_with_snapshot_retention(
            &model,
            &observations,
            &filter_config,
            &plan,
            &SnapshotRetention::All,
        )
        .unwrap();
        let scheduled = run_stratified_filter_with_global_transition_pool(
            &model,
            &observations,
            &filter_config,
            &plan,
            &SnapshotRetention::All,
            WithinStratumResamplingPolicy::default(),
            &[GlobalTransitionPoolStep::Standard],
        )
        .unwrap();
        let root_scheduled = run_stratified_filter_with_root_stratified_transition_pool(
            &model,
            &observations,
            &filter_config,
            &plan,
            &SnapshotRetention::All,
            WithinStratumResamplingPolicy::default(),
            &[RootStratifiedTransitionPoolStep::Standard],
        )
        .unwrap();
        assert!(scheduled.transition_pool_checkpoints.is_empty());
        assert!(root_scheduled.transition_pool_checkpoints.is_empty());
        assert!(root_scheduled
            .root_stratified_candidate_pool_checkpoints
            .is_empty());
        assert_eq!(
            serde_json::to_vec(&legacy).unwrap(),
            serde_json::to_vec(&scheduled.pooled).unwrap()
        );
        assert_eq!(
            serde_json::to_vec(&legacy).unwrap(),
            serde_json::to_vec(&root_scheduled.pooled).unwrap()
        );
    }

    #[test]
    fn global_pool_schedule_validation_is_typed() {
        let observation = [PoolObservation {
            time_s: 1.0,
            likelihood: PoolLikelihood::All,
        }];
        let arguments = (
            &PoolModel::from_prior(),
            &observation,
            &pool_config(4, Algorithm::Bootstrap),
            &one_pool_stratum(),
        );
        let wrong_length = run_stratified_filter_with_global_transition_pool(
            arguments.0,
            arguments.1,
            arguments.2,
            arguments.3,
            &SnapshotRetention::None,
            WithinStratumResamplingPolicy::default(),
            &[],
        )
        .unwrap_err();
        assert!(matches!(wrong_length, SmcError::InvalidConfiguration(_)));
        let zero_candidates = run_stratified_filter_with_global_transition_pool(
            arguments.0,
            arguments.1,
            arguments.2,
            arguments.3,
            &SnapshotRetention::None,
            WithinStratumResamplingPolicy::default(),
            &[GlobalTransitionPoolStep::Pool {
                candidates_per_particle: 0,
            }],
        )
        .unwrap_err();
        assert!(matches!(zero_candidates, SmcError::InvalidConfiguration(_)));
        let zero_root_candidates = run_stratified_filter_with_root_stratified_transition_pool(
            arguments.0,
            arguments.1,
            arguments.2,
            arguments.3,
            &SnapshotRetention::None,
            WithinStratumResamplingPolicy::default(),
            &[RootStratifiedTransitionPoolStep::Pool {
                candidates_per_positive_root: 0,
            }],
        )
        .unwrap_err();
        assert!(matches!(
            zero_root_candidates,
            SmcError::InvalidConfiguration(_)
        ));
    }

    #[test]
    fn intermediate_potential_pool_telescopes_transition_and_endpoint_weights() {
        let linear_likelihoods = [0.7_f64, 0.2, 0.09, 0.01];
        let observations = [PoolObservation {
            time_s: 1.0,
            likelihood: PoolLikelihood::ByInitialRoot(linear_likelihoods.map(f64::ln)),
        }];
        let bridge = PoolIntermediateBridge {
            endpoint_log_prior_over_proposal: 0.5_f64.ln(),
            record_context_in_coordinate: true,
        };
        let steps = [IntermediatePotentialStep::Bridge {
            points: vec![IntermediatePotentialBridgePoint {
                point: PoolBridgePoint {
                    time_s: 0.5,
                    log_potentials: linear_likelihoods.map(f64::ln),
                    transition_log_prior_over_proposal: 2.0_f64.ln(),
                    context_bit: 1,
                },
                candidates_per_particle: 3,
            }],
        }];
        let result = run_stratified_filter_with_intermediate_potentials(
            &PoolModel::from_prior(),
            &bridge,
            &observations,
            &pool_config(4, Algorithm::Bootstrap),
            &one_pool_stratum(),
            &SnapshotRetention::All,
            WithinStratumResamplingPolicy::default(),
            &steps,
        )
        .unwrap();

        assert_close(result.pooled.log_evidence, 0.25_f64.ln());
        assert_eq!(result.intermediate_potential_checkpoints.len(), 1);
        let checkpoint = &result.intermediate_potential_checkpoints[0];
        assert_eq!(checkpoint.observation_index, 0);
        assert_close(checkpoint.observation_time_s, 1.0);
        assert_eq!(checkpoint.points.len(), 1);
        let point = &checkpoint.points[0];
        assert_eq!(point.point_index, 0);
        assert_close(point.point_time_s, 0.5);
        assert_close(point.elapsed_seconds, 0.5);
        assert_eq!(point.candidate_pool.configured_candidates, 12);
        assert_eq!(point.candidate_pool.positive_candidates, 12);
        assert_close(
            point.candidate_pool.candidate_log_evidence_increment,
            0.5_f64.ln(),
        );
        assert_close(point.candidate_pool.output_resampling_log_correction, 0.0);
        assert_eq!(point.output_positive_particles, 4);
        assert_eq!(point.output_distinct_positive_roots, 2);
        assert_eq!(point.output_strata.len(), 1);
        assert_close(checkpoint.endpoint.log_evidence_increment, 0.5_f64.ln());
        assert_close(
            checkpoint.realized_log_evidence_increment,
            point.candidate_pool.realized_log_evidence_increment
                + checkpoint.endpoint.log_evidence_increment,
        );
        assert_eq!(
            checkpoint.endpoint.distinct_positive_roots,
            result
                .pooled
                .root_ids
                .iter()
                .copied()
                .collect::<std::collections::BTreeSet<_>>()
                .len()
        );
        assert!(result
            .pooled
            .particles
            .iter()
            .all(|state| state.assimilated_observations == 1 && state.random_coordinate == 1.0));
        assert_eq!(result.pooled.snapshots.len(), 2);
        assert_eq!(result.pooled.ancestry.len(), 1);
        let smoothed = result
            .pooled
            .aggregate_descendant_weights_at_snapshot(0, &result.pooled.log_weights)
            .unwrap();
        assert_eq!(smoothed.observation_index, None);
        assert_eq!(smoothed.descendant_counts.iter().sum::<usize>(), 4);
    }

    #[test]
    fn endpoint_pool_k1_is_byte_identical_to_the_legacy_bridge_endpoint() {
        let observations = [PoolObservation {
            time_s: 2.0,
            likelihood: PoolLikelihood::Distance(0.8),
        }];
        let point = IntermediatePotentialBridgePoint {
            point: PoolBridgePoint {
                time_s: 1.0,
                log_potentials: [0.7_f64.ln(), 0.2_f64.ln(), 0.09_f64.ln(), 0.01_f64.ln()],
                transition_log_prior_over_proposal: 0.0,
                context_bit: 1,
            },
            candidates_per_particle: 3,
        };
        let legacy_steps = [IntermediatePotentialStep::Bridge {
            points: vec![point.clone()],
        }];
        let endpoint_pool_steps = [IntermediatePotentialStep::BridgeWithEndpointPool {
            points: vec![point],
            endpoint_candidates_per_particle: 1,
        }];
        let model = PoolModel {
            transition_log_prior_over_proposal: 0.0,
            random_transition: true,
        };
        let bridge = PoolIntermediateBridge {
            endpoint_log_prior_over_proposal: 0.0,
            record_context_in_coordinate: true,
        };
        let filter = pool_config(4, Algorithm::Bootstrap);
        let plan = one_pool_stratum();
        let policy = WithinStratumResamplingPolicy {
            uniform_root_mixture_epsilon: 0.2,
        };
        let run = |steps: &[IntermediatePotentialStep<PoolBridgePoint>]| {
            run_stratified_filter_with_intermediate_potentials(
                &model,
                &bridge,
                &observations,
                &filter,
                &plan,
                &SnapshotRetention::All,
                policy,
                steps,
            )
            .unwrap()
        };
        let legacy = run(&legacy_steps);
        let canonical_k1 = run(&endpoint_pool_steps);
        assert_eq!(
            serde_json::to_vec(&legacy).unwrap(),
            serde_json::to_vec(&canonical_k1).unwrap()
        );
        assert!(canonical_k1.intermediate_potential_checkpoints[0]
            .endpoint
            .candidate_pool
            .is_none());
        let serialized = serde_json::to_value(&canonical_k1).unwrap();
        assert!(
            serialized["intermediate_potential_checkpoints"][0]["endpoint"]
                .get("candidate_pool")
                .is_none()
        );
    }

    #[test]
    fn endpoint_pool_has_exact_candidate_and_output_corrections() {
        let linear_likelihoods = [0.7_f64, 0.2, 0.09, 0.01];
        let observations = [PoolObservation {
            time_s: 2.0,
            likelihood: PoolLikelihood::ByInitialRoot(linear_likelihoods.map(f64::ln)),
        }];
        let bridge = PoolIntermediateBridge {
            endpoint_log_prior_over_proposal: 2.0_f64.ln(),
            record_context_in_coordinate: true,
        };
        let steps = [IntermediatePotentialStep::BridgeWithEndpointPool {
            points: vec![IntermediatePotentialBridgePoint {
                point: PoolBridgePoint {
                    time_s: 1.0,
                    log_potentials: [0.5_f64.ln(); 4],
                    transition_log_prior_over_proposal: 0.0,
                    context_bit: 1,
                },
                candidates_per_particle: 1,
            }],
            endpoint_candidates_per_particle: 3,
        }];
        let policy = WithinStratumResamplingPolicy {
            uniform_root_mixture_epsilon: 0.5,
        };
        let result = run_stratified_filter_with_intermediate_potentials(
            &PoolModel::from_prior(),
            &bridge,
            &observations,
            &pool_config(4, Algorithm::Bootstrap),
            &one_pool_stratum(),
            &SnapshotRetention::All,
            policy,
            &steps,
        )
        .unwrap();

        let checkpoint = &result.intermediate_potential_checkpoints[0];
        assert_close(
            checkpoint.points[0]
                .candidate_pool
                .realized_log_evidence_increment,
            0.5_f64.ln(),
        );
        let endpoint_pool = checkpoint.endpoint.candidate_pool.as_ref().unwrap();
        assert_eq!(endpoint_pool.candidates_per_particle, 3);
        assert_eq!(endpoint_pool.configured_candidates, 12);
        assert_eq!(endpoint_pool.generated_candidates, 12);
        assert_eq!(endpoint_pool.positive_candidates, 12);
        // E[2 * G / 0.5] = 1 for the four equally weighted roots.
        assert_close(endpoint_pool.candidate_log_evidence_increment, 0.0);

        let output_root_counts = (0..4)
            .map(|root| {
                result
                    .pooled
                    .root_ids
                    .iter()
                    .filter(|&&selected| selected == root)
                    .count()
            })
            .collect::<Vec<_>>();
        let output_root_proposal =
            linear_likelihoods.map(|probability| 0.5 * probability + 0.5 / 4.0);
        let realized_correction = output_root_counts
            .iter()
            .zip(linear_likelihoods)
            .zip(output_root_proposal)
            .map(|((&count, target), proposal)| count as f64 * target / proposal / 4.0)
            .sum::<f64>();
        assert_close(
            endpoint_pool.output_resampling_log_correction,
            realized_correction.ln(),
        );
        assert_close(
            endpoint_pool.realized_log_evidence_increment,
            endpoint_pool.candidate_log_evidence_increment
                + endpoint_pool.output_resampling_log_correction,
        );
        assert_close(
            checkpoint.endpoint.log_evidence_increment,
            endpoint_pool.realized_log_evidence_increment,
        );
        assert_close(
            checkpoint.realized_log_evidence_increment,
            0.5_f64.ln() + endpoint_pool.realized_log_evidence_increment,
        );
        assert_close(
            result.pooled.log_evidence,
            checkpoint.realized_log_evidence_increment,
        );
        assert_eq!(result.pooled.ancestry.len(), 1);
        assert_eq!(
            result.pooled.ancestry[0].parent_indices,
            result.pooled.root_ids
        );
        assert!(result
            .pooled
            .particles
            .iter()
            .all(|state| state.assimilated_observations == 1 && state.random_coordinate == 1.0));
    }

    #[test]
    fn endpoint_pool_calls_context_hook_and_observe_once_per_candidate() {
        use std::sync::{
            atomic::{AtomicUsize, Ordering},
            Arc,
        };

        let endpoint_proposals = Arc::new(AtomicUsize::new(0));
        let endpoint_observations = Arc::new(AtomicUsize::new(0));
        let model = CountingPoolModel {
            endpoint_observations: Arc::clone(&endpoint_observations),
        };
        let bridge = CountingIntermediateBridge {
            endpoint_proposals: Arc::clone(&endpoint_proposals),
        };
        let observations = [PoolObservation {
            time_s: 2.0,
            likelihood: PoolLikelihood::All,
        }];
        let steps = [IntermediatePotentialStep::BridgeWithEndpointPool {
            points: vec![IntermediatePotentialBridgePoint {
                point: PoolBridgePoint {
                    time_s: 1.0,
                    log_potentials: [0.0; 4],
                    transition_log_prior_over_proposal: 0.0,
                    context_bit: 1,
                },
                candidates_per_particle: 2,
            }],
            endpoint_candidates_per_particle: 3,
        }];
        let result = run_stratified_filter_with_intermediate_potentials(
            &model,
            &bridge,
            &observations,
            &pool_config(4, Algorithm::Bootstrap),
            &one_pool_stratum(),
            &SnapshotRetention::None,
            WithinStratumResamplingPolicy::default(),
            &steps,
        )
        .unwrap();
        assert_eq!(endpoint_proposals.load(Ordering::SeqCst), 12);
        assert_eq!(endpoint_observations.load(Ordering::SeqCst), 12);
        assert!(result
            .pooled
            .particles
            .iter()
            .all(|state| state.assimilated_observations == 1));
    }

    #[test]
    fn endpoint_pool_preserves_extinct_stratum_slots_and_rejects_whole_extinction() {
        let plan = StratifiedFilterPlan {
            strata: vec![
                StratumAllocation {
                    id: StratumId(10),
                    particles: 2,
                    log_prior_probability: 0.5_f64.ln(),
                },
                StratumAllocation {
                    id: StratumId(20),
                    particles: 2,
                    log_prior_probability: 0.5_f64.ln(),
                },
            ],
        };
        let observations = [PoolObservation {
            time_s: 2.0,
            likelihood: PoolLikelihood::RejectStratum(StratumId(10)),
        }];
        let bridge = PoolIntermediateBridge {
            endpoint_log_prior_over_proposal: 0.0,
            record_context_in_coordinate: false,
        };
        let steps = [IntermediatePotentialStep::BridgeWithEndpointPool {
            points: vec![IntermediatePotentialBridgePoint {
                point: PoolBridgePoint {
                    time_s: 1.0,
                    log_potentials: [0.0; 4],
                    transition_log_prior_over_proposal: 0.0,
                    context_bit: 1,
                },
                candidates_per_particle: 2,
            }],
            endpoint_candidates_per_particle: 2,
        }];
        let result = run_stratified_filter_with_intermediate_potentials(
            &PoolModel::from_prior(),
            &bridge,
            &observations,
            &pool_config(4, Algorithm::Bootstrap),
            &plan,
            &SnapshotRetention::All,
            WithinStratumResamplingPolicy::default(),
            &steps,
        )
        .unwrap();
        assert_close(result.pooled.log_evidence, 0.5_f64.ln());
        assert!(result.pooled.log_weights[..2]
            .iter()
            .all(|weight| *weight == f64::NEG_INFINITY));
        let endpoint_pool = result.intermediate_potential_checkpoints[0]
            .endpoint
            .candidate_pool
            .as_ref()
            .unwrap();
        assert_eq!(endpoint_pool.strata[0].generated_candidates, 4);
        assert_eq!(endpoint_pool.strata[0].positive_candidates, 0);
        assert_eq!(endpoint_pool.strata[0].estimated_log_predictive_mass, None);
        assert_eq!(endpoint_pool.strata[0].output_log_posterior_mass, None);
        let smoothed = result
            .pooled
            .aggregate_descendant_weights_at_snapshot(0, &result.pooled.log_weights)
            .unwrap();
        assert!(smoothed.normalized_log_weights[..2]
            .iter()
            .all(|weight| *weight == f64::NEG_INFINITY));

        let whole_extinction = run_stratified_filter_with_intermediate_potentials(
            &PoolModel::from_prior(),
            &bridge,
            &[PoolObservation {
                time_s: 2.0,
                likelihood: PoolLikelihood::ByInitialRoot([f64::NEG_INFINITY; 4]),
            }],
            &pool_config(4, Algorithm::Bootstrap),
            &one_pool_stratum(),
            &SnapshotRetention::None,
            WithinStratumResamplingPolicy::default(),
            &steps,
        )
        .unwrap_err();
        assert!(
            matches!(whole_extinction, SmcError::AllParticlesRejected),
            "unexpected extinction error: {whole_extinction:?}"
        );
    }

    #[test]
    fn intermediate_points_have_distinct_potentials_and_carry_ephemeral_context() {
        let observations = [PoolObservation {
            time_s: 3.0,
            likelihood: PoolLikelihood::All,
        }];
        let bridge = PoolIntermediateBridge {
            endpoint_log_prior_over_proposal: 0.0,
            record_context_in_coordinate: true,
        };
        let steps = [IntermediatePotentialStep::Bridge {
            points: vec![
                IntermediatePotentialBridgePoint {
                    point: PoolBridgePoint {
                        time_s: 1.0,
                        log_potentials: [0.5_f64.ln(); 4],
                        transition_log_prior_over_proposal: 0.0,
                        context_bit: 1,
                    },
                    candidates_per_particle: 2,
                },
                IntermediatePotentialBridgePoint {
                    point: PoolBridgePoint {
                        time_s: 2.0,
                        log_potentials: [0.25_f64.ln(); 4],
                        transition_log_prior_over_proposal: 0.0,
                        context_bit: 2,
                    },
                    candidates_per_particle: 2,
                },
            ],
        }];
        let result = run_stratified_filter_with_intermediate_potentials(
            &PoolModel::from_prior(),
            &bridge,
            &observations,
            &pool_config(4, Algorithm::Bootstrap),
            &one_pool_stratum(),
            &SnapshotRetention::None,
            WithinStratumResamplingPolicy::default(),
            &steps,
        )
        .unwrap();

        assert_close(result.pooled.log_evidence, 0.0);
        let checkpoint = &result.intermediate_potential_checkpoints[0];
        assert_eq!(checkpoint.points.len(), 2);
        assert_close(
            checkpoint.points[0]
                .candidate_pool
                .realized_log_evidence_increment,
            0.5_f64.ln(),
        );
        assert_close(
            checkpoint.points[1]
                .candidate_pool
                .realized_log_evidence_increment,
            0.5_f64.ln(),
        );
        assert_close(checkpoint.endpoint.log_evidence_increment, 4.0_f64.ln());
        assert!(result
            .pooled
            .particles
            .iter()
            .all(|state| state.random_coordinate == 3.0));
    }

    #[test]
    fn intermediate_bridge_is_plan_order_and_rayon_thread_invariant() {
        let first = StratumAllocation {
            id: StratumId(10),
            particles: 4,
            log_prior_probability: 0.3_f64.ln(),
        };
        let second = StratumAllocation {
            id: StratumId(20),
            particles: 4,
            log_prior_probability: 0.7_f64.ln(),
        };
        let forward = StratifiedFilterPlan {
            strata: vec![first.clone(), second.clone()],
        };
        let reversed = StratifiedFilterPlan {
            strata: vec![second, first],
        };
        let observations = [PoolObservation {
            time_s: 2.0,
            likelihood: PoolLikelihood::Distance(0.8),
        }];
        let steps = [IntermediatePotentialStep::BridgeWithEndpointPool {
            points: vec![IntermediatePotentialBridgePoint {
                point: PoolBridgePoint {
                    time_s: 1.0,
                    log_potentials: [0.7_f64.ln(), 0.2_f64.ln(), 0.09_f64.ln(), 0.01_f64.ln()],
                    transition_log_prior_over_proposal: 0.0,
                    context_bit: 1,
                },
                candidates_per_particle: 3,
            }],
            endpoint_candidates_per_particle: 3,
        }];
        let model = PoolModel {
            transition_log_prior_over_proposal: 0.0,
            random_transition: true,
        };
        let bridge = PoolIntermediateBridge {
            endpoint_log_prior_over_proposal: 0.0,
            record_context_in_coordinate: false,
        };
        let filter = pool_config(8, Algorithm::Bootstrap);
        let policy = WithinStratumResamplingPolicy {
            uniform_root_mixture_epsilon: 0.2,
        };
        let one = ThreadPoolBuilder::new()
            .num_threads(1)
            .build()
            .unwrap()
            .install(|| {
                run_stratified_filter_with_intermediate_potentials(
                    &model,
                    &bridge,
                    &observations,
                    &filter,
                    &forward,
                    &SnapshotRetention::All,
                    policy,
                    &steps,
                )
            })
            .unwrap();
        let four = ThreadPoolBuilder::new()
            .num_threads(4)
            .build()
            .unwrap()
            .install(|| {
                run_stratified_filter_with_intermediate_potentials(
                    &model,
                    &bridge,
                    &observations,
                    &filter,
                    &reversed,
                    &SnapshotRetention::All,
                    policy,
                    &steps,
                )
            })
            .unwrap();
        assert_eq!(
            serde_json::to_vec(&one).unwrap(),
            serde_json::to_vec(&four).unwrap()
        );
    }

    #[test]
    fn standard_only_intermediate_schedule_preserves_legacy_result() {
        let observations = [PoolObservation {
            time_s: 1.0,
            likelihood: PoolLikelihood::ByInitialRoot([0.7_f64, 0.2, 0.09, 0.01].map(f64::ln)),
        }];
        let model = PoolModel::from_prior();
        let bridge = PoolIntermediateBridge {
            endpoint_log_prior_over_proposal: 0.0,
            record_context_in_coordinate: false,
        };
        let filter = pool_config(4, Algorithm::Bootstrap);
        let plan = one_pool_stratum();
        let legacy = run_stratified_filter_with_snapshot_retention(
            &model,
            &observations,
            &filter,
            &plan,
            &SnapshotRetention::All,
        )
        .unwrap();
        let scheduled = run_stratified_filter_with_intermediate_potentials(
            &model,
            &bridge,
            &observations,
            &filter,
            &plan,
            &SnapshotRetention::All,
            WithinStratumResamplingPolicy::default(),
            &[IntermediatePotentialStep::Standard],
        )
        .unwrap();
        assert!(scheduled.intermediate_potential_checkpoints.is_empty());
        assert_eq!(
            serde_json::to_vec(&legacy).unwrap(),
            serde_json::to_vec(&scheduled.pooled).unwrap()
        );
    }

    #[test]
    fn intermediate_schedule_and_strictly_positive_potentials_are_validated() {
        let observations = [PoolObservation {
            time_s: 1.0,
            likelihood: PoolLikelihood::All,
        }];
        let model = PoolModel::from_prior();
        let bridge = PoolIntermediateBridge {
            endpoint_log_prior_over_proposal: 0.0,
            record_context_in_coordinate: false,
        };
        let filter = pool_config(4, Algorithm::Bootstrap);
        let plan = one_pool_stratum();
        let run = |steps: &[IntermediatePotentialStep<PoolBridgePoint>], config: &FilterConfig| {
            run_stratified_filter_with_intermediate_potentials(
                &model,
                &bridge,
                &observations,
                config,
                &plan,
                &SnapshotRetention::None,
                WithinStratumResamplingPolicy::default(),
                steps,
            )
        };

        assert!(matches!(
            run(&[], &filter).unwrap_err(),
            SmcError::InvalidConfiguration(_)
        ));
        assert!(matches!(
            run(
                &[IntermediatePotentialStep::Bridge { points: vec![] }],
                &filter
            )
            .unwrap_err(),
            SmcError::InvalidConfiguration(_)
        ));
        assert!(matches!(
            run(
                &[IntermediatePotentialStep::BridgeWithEndpointPool {
                    points: vec![IntermediatePotentialBridgePoint {
                        point: PoolBridgePoint {
                            time_s: 0.5,
                            log_potentials: [0.0; 4],
                            transition_log_prior_over_proposal: 0.0,
                            context_bit: 1,
                        },
                        candidates_per_particle: 1,
                    }],
                    endpoint_candidates_per_particle: 0,
                }],
                &filter,
            )
            .unwrap_err(),
            SmcError::InvalidConfiguration(_)
        ));
        for (time_s, candidates_per_particle) in [(0.0, 1), (1.0, 1), (0.5, 0)] {
            let steps = [IntermediatePotentialStep::Bridge {
                points: vec![IntermediatePotentialBridgePoint {
                    point: PoolBridgePoint {
                        time_s,
                        log_potentials: [0.0; 4],
                        transition_log_prior_over_proposal: 0.0,
                        context_bit: 1,
                    },
                    candidates_per_particle,
                }],
            }];
            assert!(matches!(
                run(&steps, &filter).unwrap_err(),
                SmcError::InvalidConfiguration(_)
            ));
        }
        let non_finite = [IntermediatePotentialStep::Bridge {
            points: vec![IntermediatePotentialBridgePoint {
                point: PoolBridgePoint {
                    time_s: 0.5,
                    log_potentials: [f64::NEG_INFINITY; 4],
                    transition_log_prior_over_proposal: 0.0,
                    context_bit: 1,
                },
                candidates_per_particle: 1,
            }],
        }];
        assert!(matches!(
            run(&non_finite, &filter).unwrap_err(),
            SmcError::InvalidWeights
        ));
        let mut auxiliary = filter;
        auxiliary.algorithm = Algorithm::Auxiliary;
        let valid = [IntermediatePotentialStep::Bridge {
            points: vec![IntermediatePotentialBridgePoint {
                point: PoolBridgePoint {
                    time_s: 0.5,
                    log_potentials: [0.0; 4],
                    transition_log_prior_over_proposal: 0.0,
                    context_bit: 1,
                },
                candidates_per_particle: 1,
            }],
        }];
        assert!(matches!(
            run(&valid, &auxiliary).unwrap_err(),
            SmcError::InvalidConfiguration(_)
        ));
    }

    #[test]
    fn selection_guide_proposal_has_exact_target_over_proposal_correction() {
        let target_probabilities = [0.4_f64, 0.3, 0.2, 0.1];
        let target_log_probabilities = target_probabilities.map(f64::ln);
        let guide_values = [4.0_f64, 3.0, 2.0, 1.0];
        let states = (0..4)
            .map(|initial_root| PoolState {
                stratum: StratumId(30),
                initial_root,
                random_coordinate: 0.0,
                assimilated_observations: 0,
            })
            .collect::<Vec<_>>();
        let roots = [0, 1, 2, 3];
        let log_guide = |state: &PoolState| Ok(guide_values[state.initial_root].ln());
        let (proposal, diagnostics) = selection_guided_root_log_probabilities(
            &target_log_probabilities,
            &states,
            &roots,
            WithinStratumResamplingPolicy::default(),
            Some(&log_guide),
        )
        .unwrap();
        let target_mean_guide = target_probabilities
            .iter()
            .zip(guide_values)
            .map(|(target, guide)| target * guide)
            .sum::<f64>();
        for index in 0..4 {
            assert_close(
                proposal[index].exp(),
                target_probabilities[index] * guide_values[index] / target_mean_guide,
            );
        }
        let expected_target_mass = proposal
            .iter()
            .zip(target_probabilities)
            .map(|(log_proposal, target)| log_proposal.exp() * target / log_proposal.exp())
            .sum::<f64>();
        assert_close(expected_target_mass, 1.0);

        let diagnostics = diagnostics.unwrap();
        assert_eq!(diagnostics.positive_target_states, 4);
        assert_close(diagnostics.minimum_log_guide, 0.0);
        assert_close(diagnostics.maximum_log_guide, 4.0_f64.ln());
        assert_close(diagnostics.log_target_mean_guide, target_mean_guide.ln());
        assert_close(
            diagnostics.proposal_effective_sample_size,
            1.0 / proposal
                .iter()
                .map(|value| value.exp().powi(2))
                .sum::<f64>(),
        );
        assert_eq!(diagnostics.distinct_proposal_roots, 4);
        assert_close(
            diagnostics.maximum_absolute_log_target_over_proposal,
            target_mean_guide.ln(),
        );
    }

    #[test]
    fn guided_standard_epoch_allocates_future_support_but_preserves_target_and_evidence() {
        let particles = 1_000;
        let observations = [PoolObservation {
            time_s: 1.0,
            likelihood: PoolLikelihood::All,
        }];
        let guide_point = PoolSelectionGuidePoint {
            favored_roots_below: 10,
            favored_log_guide: 99.0_f64.ln(),
            other_log_guide: 0.0,
        };
        let result = run_stratified_filter_with_intermediate_potentials_and_selection_guide(
            &PoolModel::from_prior(),
            &PoolIntermediateBridge {
                endpoint_log_prior_over_proposal: 0.0,
                record_context_in_coordinate: false,
            },
            &PoolSelectionGuide,
            &observations,
            &pool_config(particles, Algorithm::Bootstrap),
            &one_pool_stratum_with_particles(particles),
            &SnapshotRetention::All,
            WithinStratumResamplingPolicy::default(),
            &[IntermediatePotentialStep::Standard],
            &[SelectionGuideStep::Guide { point: guide_point }],
        )
        .unwrap();

        assert_eq!(result.guided_standard_checkpoints.len(), 1);
        assert!(result.intermediate_potential_checkpoints.is_empty());
        let checkpoint = &result.guided_standard_checkpoints[0];
        assert_eq!(checkpoint.candidates_per_particle, 1);
        assert_eq!(checkpoint.generated_candidates, particles);
        assert_close(checkpoint.candidate_log_evidence_increment, 0.0);
        assert_close(checkpoint.output_resampling_log_correction, 0.0);
        assert_close(checkpoint.realized_log_evidence_increment, 0.0);
        assert_close(result.pooled.log_evidence, 0.0);
        assert!(checkpoint.strata[0].ancestor_selection_guide.is_some());
        assert!(checkpoint.strata[0].output_selection_guide.is_some());

        let favored_slots = result
            .pooled
            .particles
            .iter()
            .filter(|state| state.initial_root < 10)
            .count();
        assert_eq!(favored_slots, particles / 2);
        let favored_target_mass = result
            .pooled
            .particles
            .iter()
            .zip(&result.pooled.log_weights)
            .filter(|(state, _)| state.initial_root < 10)
            .map(|(_, log_weight)| log_weight.exp())
            .sum::<f64>();
        assert_close(favored_target_mass, 0.01);
        assert!(result
            .pooled
            .particles
            .iter()
            .all(|state| state.assimilated_observations == 1));
    }

    #[test]
    fn selection_guide_composes_with_bridge_endpoint_and_retained_ancestry() {
        let observations = [
            PoolObservation {
                time_s: 2.0,
                likelihood: PoolLikelihood::All,
            },
            PoolObservation {
                time_s: 3.0,
                likelihood: PoolLikelihood::All,
            },
        ];
        let bridge = PoolIntermediateBridge {
            endpoint_log_prior_over_proposal: 0.0,
            record_context_in_coordinate: true,
        };
        let guide_point = PoolSelectionGuidePoint {
            favored_roots_below: 1,
            favored_log_guide: 4.0_f64.ln(),
            other_log_guide: 0.0,
        };
        let result = run_stratified_filter_with_intermediate_potentials_and_selection_guide(
            &PoolModel::from_prior(),
            &bridge,
            &PoolSelectionGuide,
            &observations,
            &pool_config(4, Algorithm::Bootstrap),
            &one_pool_stratum(),
            &SnapshotRetention::All,
            WithinStratumResamplingPolicy {
                uniform_root_mixture_epsilon: 0.2,
            },
            &[
                IntermediatePotentialStep::Bridge {
                    points: vec![IntermediatePotentialBridgePoint {
                        point: PoolBridgePoint {
                            time_s: 1.0,
                            log_potentials: [0.0; 4],
                            transition_log_prior_over_proposal: 0.0,
                            context_bit: 1,
                        },
                        candidates_per_particle: 2,
                    }],
                },
                IntermediatePotentialStep::Standard,
            ],
            &[
                SelectionGuideStep::Guide { point: guide_point },
                SelectionGuideStep::Guide { point: guide_point },
            ],
        )
        .unwrap();

        assert_eq!(result.intermediate_potential_checkpoints.len(), 1);
        assert_eq!(result.guided_standard_checkpoints.len(), 1);
        let bridge_checkpoint = &result.intermediate_potential_checkpoints[0];
        assert!(bridge_checkpoint.points[0].candidate_pool.strata[0]
            .ancestor_selection_guide
            .is_some());
        assert!(bridge_checkpoint.points[0].candidate_pool.strata[0]
            .output_selection_guide
            .is_some());
        let endpoint_pool = bridge_checkpoint
            .endpoint
            .candidate_pool
            .as_ref()
            .expect("a guided K=1 endpoint must retain its exact pool correction");
        assert_eq!(endpoint_pool.candidates_per_particle, 1);
        assert!(endpoint_pool.strata[0].ancestor_selection_guide.is_some());
        assert!(endpoint_pool.strata[0].output_selection_guide.is_some());
        assert_close(
            bridge_checkpoint.realized_log_evidence_increment,
            bridge_checkpoint.points[0]
                .candidate_pool
                .realized_log_evidence_increment
                + endpoint_pool.realized_log_evidence_increment,
        );
        assert_eq!(result.pooled.snapshots.len(), 3);
        assert_eq!(result.pooled.ancestry.len(), 2);
        assert!(result.pooled.checkpoints[0].posterior_resampled);
        assert!(result
            .pooled
            .ancestry
            .iter()
            .flat_map(|step| &step.parent_indices)
            .all(|&parent| parent < 4));
        let smoothed = result
            .pooled
            .aggregate_descendant_weights_at_snapshot(0, &result.pooled.log_weights)
            .unwrap();
        assert_close(
            smoothed
                .normalized_log_weights
                .iter()
                .map(|value| value.exp())
                .sum(),
            1.0,
        );
        assert!(result
            .pooled
            .particles
            .iter()
            .all(|state| state.assimilated_observations == 2));
    }

    #[test]
    fn unguided_selection_schedule_is_byte_identical_to_intermediate_filter() {
        let observations = [PoolObservation {
            time_s: 2.0,
            likelihood: PoolLikelihood::Distance(0.4),
        }];
        let bridge = PoolIntermediateBridge {
            endpoint_log_prior_over_proposal: 0.0,
            record_context_in_coordinate: true,
        };
        let steps = [IntermediatePotentialStep::Bridge {
            points: vec![IntermediatePotentialBridgePoint {
                point: PoolBridgePoint {
                    time_s: 1.0,
                    log_potentials: [0.7_f64.ln(), 0.2_f64.ln(), 0.09_f64.ln(), 0.01_f64.ln()],
                    transition_log_prior_over_proposal: 0.0,
                    context_bit: 1,
                },
                candidates_per_particle: 3,
            }],
        }];
        let model = PoolModel {
            transition_log_prior_over_proposal: 0.0,
            random_transition: true,
        };
        let filter = pool_config(4, Algorithm::Bootstrap);
        let plan = one_pool_stratum();
        let policy = WithinStratumResamplingPolicy {
            uniform_root_mixture_epsilon: 0.2,
        };
        let legacy = run_stratified_filter_with_intermediate_potentials(
            &model,
            &bridge,
            &observations,
            &filter,
            &plan,
            &SnapshotRetention::All,
            policy,
            &steps,
        )
        .unwrap();
        let selected = run_stratified_filter_with_intermediate_potentials_and_selection_guide(
            &model,
            &bridge,
            &PoolSelectionGuide,
            &observations,
            &filter,
            &plan,
            &SnapshotRetention::All,
            policy,
            &steps,
            &[SelectionGuideStep::Unguided],
        )
        .unwrap();
        assert!(selected.guided_standard_checkpoints.is_empty());
        assert_eq!(
            serde_json::to_vec(&legacy.pooled).unwrap(),
            serde_json::to_vec(&selected.pooled).unwrap()
        );
        assert_eq!(
            serde_json::to_vec(&legacy.intermediate_potential_checkpoints).unwrap(),
            serde_json::to_vec(&selected.intermediate_potential_checkpoints).unwrap()
        );

        let auxiliary_filter = pool_config(4, Algorithm::Auxiliary);
        let standard_steps = [IntermediatePotentialStep::Standard];
        let auxiliary_legacy = run_stratified_filter_with_intermediate_potentials(
            &model,
            &bridge,
            &observations,
            &auxiliary_filter,
            &plan,
            &SnapshotRetention::All,
            policy,
            &standard_steps,
        )
        .unwrap();
        let auxiliary_selected =
            run_stratified_filter_with_intermediate_potentials_and_selection_guide(
                &model,
                &bridge,
                &PoolSelectionGuide,
                &observations,
                &auxiliary_filter,
                &plan,
                &SnapshotRetention::All,
                policy,
                &standard_steps,
                &[SelectionGuideStep::Unguided],
            )
            .unwrap();
        assert_eq!(
            serde_json::to_vec(&auxiliary_legacy.pooled).unwrap(),
            serde_json::to_vec(&auxiliary_selected.pooled).unwrap()
        );
    }

    #[test]
    fn selection_guide_is_plan_order_and_rayon_thread_invariant() {
        let first = StratumAllocation {
            id: StratumId(10),
            particles: 4,
            log_prior_probability: 0.3_f64.ln(),
        };
        let second = StratumAllocation {
            id: StratumId(20),
            particles: 4,
            log_prior_probability: 0.7_f64.ln(),
        };
        let forward = StratifiedFilterPlan {
            strata: vec![first.clone(), second.clone()],
        };
        let reversed = StratifiedFilterPlan {
            strata: vec![second, first],
        };
        let observations = [
            PoolObservation {
                time_s: 1.0,
                likelihood: PoolLikelihood::Distance(0.4),
            },
            PoolObservation {
                time_s: 2.0,
                likelihood: PoolLikelihood::Distance(0.8),
            },
        ];
        let model = PoolModel {
            transition_log_prior_over_proposal: 0.0,
            random_transition: true,
        };
        let bridge = PoolIntermediateBridge {
            endpoint_log_prior_over_proposal: 0.0,
            record_context_in_coordinate: false,
        };
        let filter = pool_config(8, Algorithm::Bootstrap);
        let intermediate_steps = [
            IntermediatePotentialStep::Standard,
            IntermediatePotentialStep::Standard,
        ];
        let selection_steps = [
            SelectionGuideStep::Guide {
                point: PoolSelectionGuidePoint {
                    favored_roots_below: 4,
                    favored_log_guide: 3.0_f64.ln(),
                    other_log_guide: 0.0,
                },
            },
            SelectionGuideStep::Guide {
                point: PoolSelectionGuidePoint {
                    favored_roots_below: 4,
                    favored_log_guide: 2.0_f64.ln(),
                    other_log_guide: 0.0,
                },
            },
        ];
        let run = |plan: &StratifiedFilterPlan| {
            run_stratified_filter_with_intermediate_potentials_and_selection_guide(
                &model,
                &bridge,
                &PoolSelectionGuide,
                &observations,
                &filter,
                plan,
                &SnapshotRetention::All,
                WithinStratumResamplingPolicy {
                    uniform_root_mixture_epsilon: 0.2,
                },
                &intermediate_steps,
                &selection_steps,
            )
        };
        let one = ThreadPoolBuilder::new()
            .num_threads(1)
            .build()
            .unwrap()
            .install(|| run(&forward))
            .unwrap();
        let four = ThreadPoolBuilder::new()
            .num_threads(4)
            .build()
            .unwrap()
            .install(|| run(&reversed))
            .unwrap();
        assert_eq!(
            serde_json::to_vec(&one).unwrap(),
            serde_json::to_vec(&four).unwrap()
        );
    }

    #[test]
    fn selection_guide_preserves_extinction_semantics_and_validates_inputs() {
        let plan = StratifiedFilterPlan {
            strata: vec![
                StratumAllocation {
                    id: StratumId(10),
                    particles: 2,
                    log_prior_probability: 0.5_f64.ln(),
                },
                StratumAllocation {
                    id: StratumId(20),
                    particles: 2,
                    log_prior_probability: 0.5_f64.ln(),
                },
            ],
        };
        let bridge = PoolIntermediateBridge {
            endpoint_log_prior_over_proposal: 0.0,
            record_context_in_coordinate: false,
        };
        let guide_point = PoolSelectionGuidePoint {
            favored_roots_below: 2,
            favored_log_guide: 2.0_f64.ln(),
            other_log_guide: 0.0,
        };
        let selected_extinction =
            run_stratified_filter_with_intermediate_potentials_and_selection_guide(
                &PoolModel::from_prior(),
                &bridge,
                &PoolSelectionGuide,
                &[PoolObservation {
                    time_s: 1.0,
                    likelihood: PoolLikelihood::RejectStratum(StratumId(10)),
                }],
                &pool_config(4, Algorithm::Bootstrap),
                &plan,
                &SnapshotRetention::All,
                WithinStratumResamplingPolicy::default(),
                &[IntermediatePotentialStep::Standard],
                &[SelectionGuideStep::Guide { point: guide_point }],
            )
            .unwrap();
        assert_close(selected_extinction.pooled.log_evidence, 0.5_f64.ln());
        assert!(selected_extinction.pooled.log_weights[..2]
            .iter()
            .all(|weight| *weight == f64::NEG_INFINITY));
        let extinct = &selected_extinction.guided_standard_checkpoints[0].strata[0];
        assert_eq!(extinct.positive_candidates, 0);
        assert!(extinct.ancestor_selection_guide.is_some());
        assert!(extinct.output_selection_guide.is_none());

        let all_rejected = run_stratified_filter_with_intermediate_potentials_and_selection_guide(
            &PoolModel::from_prior(),
            &bridge,
            &PoolSelectionGuide,
            &[PoolObservation {
                time_s: 1.0,
                likelihood: PoolLikelihood::ByInitialRoot([f64::NEG_INFINITY; 4]),
            }],
            &pool_config(4, Algorithm::Bootstrap),
            &one_pool_stratum(),
            &SnapshotRetention::None,
            WithinStratumResamplingPolicy::default(),
            &[IntermediatePotentialStep::Standard],
            &[SelectionGuideStep::Guide { point: guide_point }],
        )
        .unwrap_err();
        assert!(matches!(all_rejected, SmcError::AllParticlesRejected));

        let non_finite = run_stratified_filter_with_intermediate_potentials_and_selection_guide(
            &PoolModel::from_prior(),
            &bridge,
            &PoolSelectionGuide,
            &[PoolObservation {
                time_s: 1.0,
                likelihood: PoolLikelihood::All,
            }],
            &pool_config(4, Algorithm::Bootstrap),
            &one_pool_stratum(),
            &SnapshotRetention::None,
            WithinStratumResamplingPolicy::default(),
            &[IntermediatePotentialStep::Standard],
            &[SelectionGuideStep::Guide {
                point: PoolSelectionGuidePoint {
                    favored_roots_below: 4,
                    favored_log_guide: f64::INFINITY,
                    other_log_guide: 0.0,
                },
            }],
        )
        .unwrap_err();
        assert!(matches!(non_finite, SmcError::InvalidWeights));

        let wrong_length = run_stratified_filter_with_intermediate_potentials_and_selection_guide(
            &PoolModel::from_prior(),
            &bridge,
            &PoolSelectionGuide,
            &[PoolObservation {
                time_s: 1.0,
                likelihood: PoolLikelihood::All,
            }],
            &pool_config(4, Algorithm::Bootstrap),
            &one_pool_stratum(),
            &SnapshotRetention::None,
            WithinStratumResamplingPolicy::default(),
            &[IntermediatePotentialStep::Standard],
            &[],
        )
        .unwrap_err();
        assert!(matches!(wrong_length, SmcError::InvalidConfiguration(_)));

        let auxiliary = run_stratified_filter_with_intermediate_potentials_and_selection_guide(
            &PoolModel::from_prior(),
            &bridge,
            &PoolSelectionGuide,
            &[PoolObservation {
                time_s: 1.0,
                likelihood: PoolLikelihood::All,
            }],
            &pool_config(4, Algorithm::Auxiliary),
            &one_pool_stratum(),
            &SnapshotRetention::None,
            WithinStratumResamplingPolicy::default(),
            &[IntermediatePotentialStep::Standard],
            &[SelectionGuideStep::Guide { point: guide_point }],
        )
        .unwrap_err();
        assert!(matches!(auxiliary, SmcError::InvalidConfiguration(_)));
    }

    #[test]
    fn persistent_twist_enriches_slots_then_globally_untwists_to_the_physical_filter() {
        let particles = 1_000;
        let observations = [
            PoolObservation {
                time_s: 1.0,
                likelihood: PoolLikelihood::All,
            },
            PoolObservation {
                time_s: 2.0,
                likelihood: PoolLikelihood::All,
            },
        ];
        let point = PoolPersistentTwistPoint {
            favored_roots_below: 10,
            favored_log_potential: 99.0_f64.ln(),
            other_log_potential: 0.0,
        };
        let result = run_stratified_filter_with_intermediate_potentials_and_persistent_twist(
            &PoolModel::from_prior(),
            &PoolIntermediateBridge {
                endpoint_log_prior_over_proposal: 0.0,
                record_context_in_coordinate: false,
            },
            &PoolPersistentTwist,
            &observations,
            &pool_config(particles, Algorithm::Bootstrap),
            &one_pool_stratum_with_particles(particles),
            &SnapshotRetention::All,
            WithinStratumResamplingPolicy::default(),
            &[
                IntermediatePotentialStep::Standard,
                IntermediatePotentialStep::Standard,
            ],
            &[
                PersistentTwistStep::Activate { point },
                PersistentTwistStep::Finalize { point },
            ],
        )
        .unwrap();

        assert_eq!(result.persistent_twist_checkpoints.len(), 2);
        assert_eq!(result.twisted_standard_checkpoints.len(), 2);
        assert!(result.intermediate_potential_checkpoints.is_empty());
        assert_eq!(result.twisted_filtering_observation_indices, vec![0]);
        let activation = &result.persistent_twist_checkpoints[0];
        assert_eq!(activation.phase, PersistentTwistPhase::Activate);
        assert!(activation.output_is_twisted);
        assert_close(
            activation.twisted_target_log_evidence_increment,
            1.98_f64.ln(),
        );
        assert_eq!(activation.final_untwist_log_evidence_correction, None);
        assert_close(
            activation.population.log_implied_untwist_correction,
            (50.0_f64 / 99.0).ln(),
        );

        let finalization = &result.persistent_twist_checkpoints[1];
        assert_eq!(finalization.phase, PersistentTwistPhase::Finalize);
        assert!(!finalization.output_is_twisted);
        assert_close(finalization.twisted_target_log_evidence_increment, 0.0);
        assert_close(
            finalization.final_untwist_log_evidence_correction.unwrap(),
            (50.0_f64 / 99.0).ln(),
        );
        assert_close(
            finalization.filter_checkpoint_log_evidence_increment,
            (50.0_f64 / 99.0).ln(),
        );
        assert_close(result.pooled.log_evidence, 0.0);
        assert_close(
            result.pooled.checkpoints[0].cumulative_log_evidence,
            1.98_f64.ln(),
        );
        assert_close(result.pooled.checkpoints[1].cumulative_log_evidence, 0.0);
        assert_close(
            result.pooled.checkpoints[1].log_evidence_increment,
            (50.0_f64 / 99.0).ln(),
        );

        let favored_slots = result
            .pooled
            .particles
            .iter()
            .filter(|state| state.initial_root < 10)
            .count();
        assert_eq!(favored_slots, particles / 2);
        let favored_physical_mass = result
            .pooled
            .particles
            .iter()
            .zip(&result.pooled.log_weights)
            .filter(|(state, _)| state.initial_root < 10)
            .map(|(_, log_weight)| log_weight.exp())
            .sum::<f64>();
        assert_close(favored_physical_mass, 0.01);
        assert_eq!(result.pooled.snapshots.len(), 3);
        assert_eq!(result.pooled.ancestry.len(), 2);
        assert_eq!(
            result.pooled.snapshots.last().unwrap().log_weights,
            result.pooled.log_weights
        );
        assert_close(
            result.pooled.checkpoints[1].root_effective_sample_size,
            finalization
                .population
                .implied_untwisted_root_effective_sample_size,
        );
        assert_close(
            result.pooled.checkpoints[1].maximum_root_weight,
            finalization
                .population
                .implied_untwisted_maximum_root_weight,
        );

        // Downstream terminal scoring consumes the already-untwisted parent
        // exactly once. Algebraically this equals scoring the pre-untwist
        // twisted population with G/H and globally normalizing by E[1/H].
        let physical_terminal_expectation = result
            .pooled
            .particles
            .iter()
            .zip(&result.pooled.log_weights)
            .map(|(state, log_weight)| {
                let terminal_factor = if state.initial_root < 10 { 2.0 } else { 0.5 };
                log_weight.exp() * terminal_factor
            })
            .sum::<f64>();
        let twisted_terminal_numerator = result
            .pooled
            .particles
            .iter()
            .map(|state| {
                let (potential, terminal_factor) = if state.initial_root < 10 {
                    (99.0, 2.0)
                } else {
                    (1.0, 0.5)
                };
                terminal_factor / potential / particles as f64
            })
            .sum::<f64>();
        let twisted_untwist_normalizer = result
            .pooled
            .particles
            .iter()
            .map(|state| {
                let potential = if state.initial_root < 10 { 99.0 } else { 1.0 };
                1.0 / potential / particles as f64
            })
            .sum::<f64>();
        assert_close(
            physical_terminal_expectation,
            twisted_terminal_numerator / twisted_untwist_normalizer,
        );
    }

    #[test]
    fn persistent_twist_constant_potential_cancels_and_all_inactive_is_byte_identical() {
        let observations = [
            PoolObservation {
                time_s: 1.0,
                likelihood: PoolLikelihood::All,
            },
            PoolObservation {
                time_s: 2.0,
                likelihood: PoolLikelihood::All,
            },
        ];
        let model = PoolModel::from_prior();
        let bridge = PoolIntermediateBridge {
            endpoint_log_prior_over_proposal: 0.0,
            record_context_in_coordinate: false,
        };
        let filter = pool_config(4, Algorithm::Bootstrap);
        let plan = one_pool_stratum();
        let intermediate_steps = [
            IntermediatePotentialStep::Standard,
            IntermediatePotentialStep::Standard,
        ];
        let run_constant = |log_potential: f64| {
            let point = PoolPersistentTwistPoint {
                favored_roots_below: 4,
                favored_log_potential: log_potential,
                other_log_potential: log_potential,
            };
            run_stratified_filter_with_intermediate_potentials_and_persistent_twist(
                &model,
                &bridge,
                &PoolPersistentTwist,
                &observations,
                &filter,
                &plan,
                &SnapshotRetention::All,
                WithinStratumResamplingPolicy::default(),
                &intermediate_steps,
                &[
                    PersistentTwistStep::Activate { point },
                    PersistentTwistStep::Finalize { point },
                ],
            )
            .unwrap()
        };
        let neutral = run_constant(0.0);
        let constant = run_constant(7.0_f64.ln());
        assert_close(
            constant.persistent_twist_checkpoints[0].twisted_target_log_evidence_increment,
            7.0_f64.ln(),
        );
        assert_close(
            constant.persistent_twist_checkpoints[1]
                .final_untwist_log_evidence_correction
                .unwrap(),
            -7.0_f64.ln(),
        );
        assert_close(constant.pooled.log_evidence, 0.0);
        assert_eq!(constant.pooled.particles, neutral.pooled.particles);
        assert_eq!(constant.pooled.log_weights, neutral.pooled.log_weights);
        assert_eq!(constant.pooled.root_ids, neutral.pooled.root_ids);
        assert_eq!(constant.pooled.ancestry, neutral.pooled.ancestry);

        let legacy = run_stratified_filter_with_intermediate_potentials(
            &model,
            &bridge,
            &observations,
            &filter,
            &plan,
            &SnapshotRetention::All,
            WithinStratumResamplingPolicy::default(),
            &intermediate_steps,
        )
        .unwrap();
        let inactive = run_stratified_filter_with_intermediate_potentials_and_persistent_twist(
            &model,
            &bridge,
            &PoolPersistentTwist,
            &observations,
            &filter,
            &plan,
            &SnapshotRetention::All,
            WithinStratumResamplingPolicy::default(),
            &intermediate_steps,
            &[PersistentTwistStep::Inactive, PersistentTwistStep::Inactive],
        )
        .unwrap();
        assert!(inactive.persistent_twist_checkpoints.is_empty());
        assert!(inactive.twisted_standard_checkpoints.is_empty());
        assert!(inactive.twisted_filtering_observation_indices.is_empty());
        assert_eq!(
            serde_json::to_vec(&legacy.pooled).unwrap(),
            serde_json::to_vec(&inactive.pooled).unwrap()
        );
        assert_eq!(
            serde_json::to_vec(&legacy.intermediate_potential_checkpoints).unwrap(),
            serde_json::to_vec(&inactive.intermediate_potential_checkpoints).unwrap()
        );
    }

    #[test]
    fn persistent_twist_uses_successive_new_over_old_ratios_across_physical_epochs() {
        let observations = [
            PoolObservation {
                time_s: 1.0,
                likelihood: PoolLikelihood::All,
            },
            PoolObservation {
                time_s: 2.0,
                likelihood: PoolLikelihood::All,
            },
            PoolObservation {
                time_s: 3.0,
                likelihood: PoolLikelihood::All,
            },
        ];
        let constant_point = |potential: f64| PoolPersistentTwistPoint {
            favored_roots_below: 4,
            favored_log_potential: potential.ln(),
            other_log_potential: potential.ln(),
        };
        let result = run_stratified_filter_with_intermediate_potentials_and_persistent_twist(
            &PoolModel::from_prior(),
            &PoolIntermediateBridge {
                endpoint_log_prior_over_proposal: 0.0,
                record_context_in_coordinate: false,
            },
            &PoolPersistentTwist,
            &observations,
            &pool_config(4, Algorithm::Bootstrap),
            &one_pool_stratum(),
            &SnapshotRetention::All,
            WithinStratumResamplingPolicy::default(),
            &[
                IntermediatePotentialStep::Standard,
                IntermediatePotentialStep::Standard,
                IntermediatePotentialStep::Standard,
            ],
            &[
                PersistentTwistStep::Activate {
                    point: constant_point(2.0),
                },
                PersistentTwistStep::Continue {
                    point: constant_point(5.0),
                },
                PersistentTwistStep::Finalize {
                    point: constant_point(7.0),
                },
            ],
        )
        .unwrap();
        assert_close(
            result.persistent_twist_checkpoints[0].twisted_target_log_evidence_increment,
            2.0_f64.ln(),
        );
        assert_close(
            result.persistent_twist_checkpoints[1].twisted_target_log_evidence_increment,
            (5.0_f64 / 2.0).ln(),
        );
        assert_close(
            result.persistent_twist_checkpoints[2].twisted_target_log_evidence_increment,
            (7.0_f64 / 5.0).ln(),
        );
        assert_close(
            result.persistent_twist_checkpoints[2]
                .final_untwist_log_evidence_correction
                .unwrap(),
            (1.0_f64 / 7.0).ln(),
        );
        assert_close(result.pooled.log_evidence, 0.0);
        assert_eq!(result.twisted_filtering_observation_indices, vec![0, 1]);
        assert_eq!(result.pooled.snapshots.len(), 4);
        assert_eq!(result.pooled.ancestry.len(), 3);
    }

    #[test]
    fn persistent_twist_composes_with_two_bridge_points_and_endpoint_k4() {
        let particles = 1_000;
        let observations = [
            PoolObservation {
                time_s: 0.5,
                likelihood: PoolLikelihood::All,
            },
            PoolObservation {
                time_s: 2.0,
                likelihood: PoolLikelihood::All,
            },
        ];
        let point = PoolPersistentTwistPoint {
            favored_roots_below: 10,
            favored_log_potential: 99.0_f64.ln(),
            other_log_potential: 0.0,
        };
        let result = run_stratified_filter_with_intermediate_potentials_and_persistent_twist(
            &PoolModel::from_prior(),
            &PoolIntermediateBridge {
                endpoint_log_prior_over_proposal: 0.0,
                record_context_in_coordinate: true,
            },
            &PoolPersistentTwist,
            &observations,
            &pool_config(particles, Algorithm::Bootstrap),
            &one_pool_stratum_with_particles(particles),
            &SnapshotRetention::All,
            WithinStratumResamplingPolicy::default(),
            &[
                IntermediatePotentialStep::Standard,
                IntermediatePotentialStep::BridgeWithEndpointPool {
                    points: vec![
                        IntermediatePotentialBridgePoint {
                            point: PoolBridgePoint {
                                time_s: 1.0,
                                log_potentials: [0.5_f64.ln(); 4],
                                transition_log_prior_over_proposal: 0.0,
                                context_bit: 1,
                            },
                            candidates_per_particle: 2,
                        },
                        IntermediatePotentialBridgePoint {
                            point: PoolBridgePoint {
                                time_s: 1.5,
                                log_potentials: [0.25_f64.ln(); 4],
                                transition_log_prior_over_proposal: 0.0,
                                context_bit: 2,
                            },
                            candidates_per_particle: 2,
                        },
                    ],
                    endpoint_candidates_per_particle: 4,
                },
            ],
            &[
                PersistentTwistStep::Activate { point },
                PersistentTwistStep::Finalize { point },
            ],
        )
        .unwrap();

        assert_eq!(result.intermediate_potential_checkpoints.len(), 1);
        let bridge_checkpoint = &result.intermediate_potential_checkpoints[0];
        assert_eq!(bridge_checkpoint.points.len(), 2);
        assert_eq!(
            bridge_checkpoint.points[0]
                .candidate_pool
                .candidates_per_particle,
            2
        );
        assert_eq!(
            bridge_checkpoint.points[1]
                .candidate_pool
                .candidates_per_particle,
            2
        );
        assert_eq!(
            bridge_checkpoint
                .endpoint
                .candidate_pool
                .as_ref()
                .unwrap()
                .candidates_per_particle,
            4
        );
        assert_close(
            bridge_checkpoint.points[0]
                .candidate_pool
                .realized_log_evidence_increment,
            0.5_f64.ln(),
        );
        assert_close(
            bridge_checkpoint.points[1]
                .candidate_pool
                .realized_log_evidence_increment,
            0.5_f64.ln(),
        );
        assert_close(
            bridge_checkpoint
                .endpoint
                .candidate_pool
                .as_ref()
                .unwrap()
                .realized_log_evidence_increment,
            4.0_f64.ln(),
        );
        assert_close(
            result.persistent_twist_checkpoints[0].twisted_target_log_evidence_increment,
            1.98_f64.ln(),
        );
        assert_close(
            result.persistent_twist_checkpoints[1].twisted_target_log_evidence_increment,
            0.0,
        );
        assert_close(
            bridge_checkpoint.realized_log_evidence_increment,
            (50.0_f64 / 99.0).ln(),
        );
        assert_close(
            bridge_checkpoint.endpoint.log_evidence_increment,
            4.0_f64.ln() + (50.0_f64 / 99.0).ln(),
        );
        assert_close(
            bridge_checkpoint.endpoint.posterior_effective_sample_size,
            result.pooled.checkpoints[1].posterior_ess,
        );
        assert_close(
            bridge_checkpoint.endpoint.root_effective_sample_size,
            result.pooled.checkpoints[1].root_effective_sample_size,
        );
        assert_close(result.pooled.log_evidence, 0.0);
        let favored_slots = result
            .pooled
            .particles
            .iter()
            .filter(|state| state.initial_root < 10)
            .count();
        assert_eq!(favored_slots, particles / 2);
        let favored_mass = result
            .pooled
            .particles
            .iter()
            .zip(&result.pooled.log_weights)
            .filter(|(state, _)| state.initial_root < 10)
            .map(|(_, weight)| weight.exp())
            .sum::<f64>();
        assert_close(favored_mass, 0.01);
        assert!(result
            .pooled
            .particles
            .iter()
            .all(|state| state.random_coordinate == 3.0 && state.assimilated_observations == 2));
    }

    #[test]
    fn persistent_twist_endpoint_observes_each_k4_candidate_once_and_carries_context() {
        use std::sync::{
            atomic::{AtomicUsize, Ordering},
            Arc,
        };

        let endpoint_proposals = Arc::new(AtomicUsize::new(0));
        let endpoint_observations = Arc::new(AtomicUsize::new(0));
        let twist_evaluations = Arc::new(AtomicUsize::new(0));
        let model = CountingPoolModel {
            endpoint_observations: Arc::clone(&endpoint_observations),
        };
        let result = run_stratified_filter_with_intermediate_potentials_and_persistent_twist(
            &model,
            &CountingIntermediateBridge {
                endpoint_proposals: Arc::clone(&endpoint_proposals),
            },
            &CountingPersistentTwist {
                evaluations: Arc::clone(&twist_evaluations),
            },
            &[
                PoolObservation {
                    time_s: 1.0,
                    likelihood: PoolLikelihood::All,
                },
                PoolObservation {
                    time_s: 3.0,
                    likelihood: PoolLikelihood::All,
                },
            ],
            &pool_config(4, Algorithm::Bootstrap),
            &one_pool_stratum(),
            &SnapshotRetention::All,
            WithinStratumResamplingPolicy::default(),
            &[
                IntermediatePotentialStep::Standard,
                IntermediatePotentialStep::BridgeWithEndpointPool {
                    points: vec![IntermediatePotentialBridgePoint {
                        point: PoolBridgePoint {
                            time_s: 2.0,
                            log_potentials: [0.0; 4],
                            transition_log_prior_over_proposal: 0.0,
                            context_bit: 1,
                        },
                        candidates_per_particle: 2,
                    }],
                    endpoint_candidates_per_particle: 4,
                },
            ],
            &[
                PersistentTwistStep::Activate { point: () },
                PersistentTwistStep::Finalize { point: () },
            ],
        )
        .unwrap();
        assert_eq!(endpoint_proposals.load(Ordering::SeqCst), 16);
        assert_eq!(endpoint_observations.load(Ordering::SeqCst), 20);
        assert_eq!(twist_evaluations.load(Ordering::SeqCst), 28);
        assert!(result
            .pooled
            .particles
            .iter()
            .all(|state| state.assimilated_observations == 2));
        assert_eq!(result.pooled.snapshots.len(), 3);
        assert_eq!(result.pooled.ancestry.len(), 2);
    }

    #[test]
    fn persistent_twist_preserves_stratum_extinction_and_global_untwist() {
        let plan = StratifiedFilterPlan {
            strata: vec![
                StratumAllocation {
                    id: StratumId(10),
                    particles: 2,
                    log_prior_probability: 0.5_f64.ln(),
                },
                StratumAllocation {
                    id: StratumId(20),
                    particles: 2,
                    log_prior_probability: 0.5_f64.ln(),
                },
            ],
        };
        let point = PoolPersistentTwistPoint {
            favored_roots_below: 0,
            favored_log_potential: 2.0_f64.ln(),
            other_log_potential: 2.0_f64.ln(),
        };
        let bridge = PoolIntermediateBridge {
            endpoint_log_prior_over_proposal: 0.0,
            record_context_in_coordinate: false,
        };
        let result = run_stratified_filter_with_intermediate_potentials_and_persistent_twist(
            &PoolModel::from_prior(),
            &bridge,
            &PoolPersistentTwist,
            &[
                PoolObservation {
                    time_s: 1.0,
                    likelihood: PoolLikelihood::All,
                },
                PoolObservation {
                    time_s: 2.0,
                    likelihood: PoolLikelihood::RejectStratum(StratumId(10)),
                },
            ],
            &pool_config(4, Algorithm::Bootstrap),
            &plan,
            &SnapshotRetention::All,
            WithinStratumResamplingPolicy::default(),
            &[
                IntermediatePotentialStep::Standard,
                IntermediatePotentialStep::Standard,
            ],
            &[
                PersistentTwistStep::Activate { point },
                PersistentTwistStep::Finalize { point },
            ],
        )
        .unwrap();
        assert_close(result.pooled.log_evidence, 0.5_f64.ln());
        assert!(result.pooled.log_weights[..2]
            .iter()
            .all(|weight| *weight == f64::NEG_INFINITY));
        let extinct = &result.twisted_standard_checkpoints[1].strata[0];
        assert_eq!(extinct.positive_candidates, 0);
        assert_eq!(extinct.estimated_log_predictive_mass, None);
        assert_close(
            result.persistent_twist_checkpoints[1]
                .final_untwist_log_evidence_correction
                .unwrap(),
            -2.0_f64.ln(),
        );
        let smoothed = result
            .pooled
            .aggregate_descendant_weights_at_snapshot(0, &result.pooled.log_weights)
            .unwrap();
        assert!(smoothed.normalized_log_weights[..2]
            .iter()
            .all(|weight| *weight == f64::NEG_INFINITY));

        let all_rejected = run_stratified_filter_with_intermediate_potentials_and_persistent_twist(
            &PoolModel::from_prior(),
            &bridge,
            &PoolPersistentTwist,
            &[
                PoolObservation {
                    time_s: 1.0,
                    likelihood: PoolLikelihood::All,
                },
                PoolObservation {
                    time_s: 2.0,
                    likelihood: PoolLikelihood::ByInitialRoot([f64::NEG_INFINITY; 4]),
                },
            ],
            &pool_config(4, Algorithm::Bootstrap),
            &one_pool_stratum(),
            &SnapshotRetention::None,
            WithinStratumResamplingPolicy::default(),
            &[
                IntermediatePotentialStep::Standard,
                IntermediatePotentialStep::Standard,
            ],
            &[
                PersistentTwistStep::Activate { point },
                PersistentTwistStep::Finalize { point },
            ],
        )
        .unwrap_err();
        assert!(matches!(all_rejected, SmcError::AllParticlesRejected));
    }

    #[test]
    fn persistent_twist_is_plan_order_and_rayon_thread_invariant() {
        let first = StratumAllocation {
            id: StratumId(10),
            particles: 4,
            log_prior_probability: 0.3_f64.ln(),
        };
        let second = StratumAllocation {
            id: StratumId(20),
            particles: 4,
            log_prior_probability: 0.7_f64.ln(),
        };
        let forward = StratifiedFilterPlan {
            strata: vec![first.clone(), second.clone()],
        };
        let reversed = StratifiedFilterPlan {
            strata: vec![second, first],
        };
        let observations = [
            PoolObservation {
                time_s: 1.0,
                likelihood: PoolLikelihood::Distance(0.4),
            },
            PoolObservation {
                time_s: 2.0,
                likelihood: PoolLikelihood::Distance(0.8),
            },
        ];
        let model = PoolModel {
            transition_log_prior_over_proposal: 0.0,
            random_transition: true,
        };
        let bridge = PoolIntermediateBridge {
            endpoint_log_prior_over_proposal: 0.0,
            record_context_in_coordinate: false,
        };
        let filter = pool_config(8, Algorithm::Bootstrap);
        let point = PoolPersistentTwistPoint {
            favored_roots_below: 4,
            favored_log_potential: 3.0_f64.ln(),
            other_log_potential: 0.0,
        };
        let run = |plan: &StratifiedFilterPlan| {
            run_stratified_filter_with_intermediate_potentials_and_persistent_twist(
                &model,
                &bridge,
                &PoolPersistentTwist,
                &observations,
                &filter,
                plan,
                &SnapshotRetention::All,
                WithinStratumResamplingPolicy {
                    uniform_root_mixture_epsilon: 0.2,
                },
                &[
                    IntermediatePotentialStep::Standard,
                    IntermediatePotentialStep::Standard,
                ],
                &[
                    PersistentTwistStep::Activate { point },
                    PersistentTwistStep::Finalize { point },
                ],
            )
        };
        let one = ThreadPoolBuilder::new()
            .num_threads(1)
            .build()
            .unwrap()
            .install(|| run(&forward))
            .unwrap();
        let four = ThreadPoolBuilder::new()
            .num_threads(4)
            .build()
            .unwrap()
            .install(|| run(&reversed))
            .unwrap();
        assert_eq!(
            serde_json::to_vec(&one).unwrap(),
            serde_json::to_vec(&four).unwrap()
        );
    }

    #[test]
    fn persistent_twist_validates_lifecycle_algorithm_and_finite_potential() {
        let observations = [
            PoolObservation {
                time_s: 1.0,
                likelihood: PoolLikelihood::All,
            },
            PoolObservation {
                time_s: 2.0,
                likelihood: PoolLikelihood::All,
            },
        ];
        let model = PoolModel::from_prior();
        let bridge = PoolIntermediateBridge {
            endpoint_log_prior_over_proposal: 0.0,
            record_context_in_coordinate: false,
        };
        let plan = one_pool_stratum();
        let intermediate_steps = [
            IntermediatePotentialStep::Standard,
            IntermediatePotentialStep::Standard,
        ];
        let point = PoolPersistentTwistPoint {
            favored_roots_below: 4,
            favored_log_potential: 0.0,
            other_log_potential: 0.0,
        };
        let run = |steps: &[PersistentTwistStep<PoolPersistentTwistPoint>],
                   config: &FilterConfig| {
            run_stratified_filter_with_intermediate_potentials_and_persistent_twist(
                &model,
                &bridge,
                &PoolPersistentTwist,
                &observations,
                config,
                &plan,
                &SnapshotRetention::None,
                WithinStratumResamplingPolicy::default(),
                &intermediate_steps,
                steps,
            )
        };
        for invalid in [
            vec![
                PersistentTwistStep::Continue { point },
                PersistentTwistStep::Inactive,
            ],
            vec![
                PersistentTwistStep::Activate { point },
                PersistentTwistStep::Inactive,
            ],
            vec![
                PersistentTwistStep::Activate { point },
                PersistentTwistStep::Activate { point },
            ],
            vec![
                PersistentTwistStep::Inactive,
                PersistentTwistStep::Finalize { point },
            ],
            vec![
                PersistentTwistStep::Activate { point },
                PersistentTwistStep::Continue { point },
            ],
        ] {
            assert!(matches!(
                run(&invalid, &pool_config(4, Algorithm::Bootstrap)).unwrap_err(),
                SmcError::InvalidConfiguration(_)
            ));
        }
        assert!(matches!(
            run(
                &[PersistentTwistStep::Inactive],
                &pool_config(4, Algorithm::Bootstrap)
            )
            .unwrap_err(),
            SmcError::InvalidConfiguration(_)
        ));
        assert!(matches!(
            run(
                &[
                    PersistentTwistStep::Activate { point },
                    PersistentTwistStep::Finalize { point },
                ],
                &pool_config(4, Algorithm::Auxiliary),
            )
            .unwrap_err(),
            SmcError::InvalidConfiguration(_)
        ));

        let non_finite_point = PoolPersistentTwistPoint {
            favored_roots_below: 4,
            favored_log_potential: f64::NEG_INFINITY,
            other_log_potential: 0.0,
        };
        let non_finite = run(
            &[
                PersistentTwistStep::Activate {
                    point: non_finite_point,
                },
                PersistentTwistStep::Finalize {
                    point: non_finite_point,
                },
            ],
            &pool_config(4, Algorithm::Bootstrap),
        )
        .unwrap_err();
        assert!(matches!(non_finite, SmcError::InvalidWeights));
    }
}
