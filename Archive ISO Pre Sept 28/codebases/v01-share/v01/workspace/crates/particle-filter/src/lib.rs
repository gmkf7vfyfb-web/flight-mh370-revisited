//! One centralized Bayesian particle engine.
//!
//! Sequential filtering and adaptive tempered static inference share deterministic
//! resampling, keyed random streams, and numerical weight handling.

mod config;
mod filter;
mod islands;
mod model;
mod resampling;
mod rng;
mod stratified;
mod tempered;

pub use config::{
    Algorithm, FilterConfig, StratifiedFilterPlan, StratumAllocation, WithinStratumResamplingPolicy,
};
pub use filter::{
    run_filter, run_filter_with_options, run_filter_with_snapshot_retention, FilterAncestryStep,
    FilterCheckpoint, FilterParticleIdentity, FilterResult, FilterRunOptions, FilterSnapshot,
    SmcError, SmoothedSnapshotWeights, SnapshotRetention, StratumDiagnostics,
};
pub use islands::{
    run_stratified_island_filter,
    run_stratified_island_filter_with_snapshot_retention_and_resampling_policy, IslandAllocation,
    IslandDiagnostics, IslandFilterCheckpoint, IslandIdentity, IslandRootIdentity,
    IslandRunDiagnostics, IslandTermination, StratifiedIslandFilterResult, StratifiedIslandPlan,
    StratumIslandAllocation,
};
pub use model::{Initialization, ParticleModel, Proposal, StratumId};
pub use resampling::{
    aggregate_log_weights_by_ancestor, effective_sample_size, logsumexp, normalize_log_weights,
    reweight_population, systematic_resample, systematic_resample_n, ReweightedPopulation,
};
pub use rng::{derive_seed, rng_for};
pub use stratified::{
    run_stratified_bootstrap_filter_with_post_resample_move, run_stratified_filter,
    run_stratified_filter_with_global_transition_pool,
    run_stratified_filter_with_intermediate_potentials,
    run_stratified_filter_with_intermediate_potentials_and_persistent_twist,
    run_stratified_filter_with_intermediate_potentials_and_selection_guide,
    run_stratified_filter_with_options, run_stratified_filter_with_resampling_policy,
    run_stratified_filter_with_root_stratified_intermediate_potentials,
    run_stratified_filter_with_root_stratified_transition_pool,
    run_stratified_filter_with_snapshot_retention,
    run_stratified_filter_with_snapshot_retention_and_resampling_policy,
    GlobalTransitionPoolCheckpoint, GlobalTransitionPoolFilterResult, GlobalTransitionPoolStep,
    GlobalTransitionPoolStratumDiagnostics, IntermediatePotentialBridge,
    IntermediatePotentialBridgePoint, IntermediatePotentialCheckpoint,
    IntermediatePotentialEndpointCheckpoint, IntermediatePotentialFilterResult,
    IntermediatePotentialPointCheckpoint, IntermediatePotentialProposal, IntermediatePotentialStep,
    NoopStratifiedPostResampleMove, PersistentTwist, PersistentTwistCheckpoint,
    PersistentTwistFilterResult, PersistentTwistPhase, PersistentTwistPopulationDiagnostics,
    PersistentTwistStep, RootStratifiedCandidatePoolCheckpoint,
    RootStratifiedCandidatePoolLocation, RootStratifiedCandidatePoolStratumDiagnostics,
    RootStratifiedIntermediatePotentialBridgePoint,
    RootStratifiedIntermediatePotentialFilterResult, RootStratifiedIntermediatePotentialStep,
    RootStratifiedTransitionPoolFilterResult, RootStratifiedTransitionPoolStep, SelectionGuide,
    SelectionGuideDistributionDiagnostics, SelectionGuideFilterResult, SelectionGuideStep,
    StratifiedPostResampleMove, StratifiedPostResampleMoveCheckpoint,
    StratifiedPostResampleMoveContext, StratifiedPostResampleMoveFilterResult,
    StratifiedPostResampleMoveStep, StratifiedPostResampleMoveStratumCheckpoint,
    STRATIFIED_POST_RESAMPLE_MOVE_RNG_DOMAIN,
};
pub use tempered::{
    run_tempered_smc, Mutation, StaticModel, TemperedCheckpoint, TemperedConfig, TemperedError,
    TemperedResult,
};
