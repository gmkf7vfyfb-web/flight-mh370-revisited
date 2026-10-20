use std::{collections::BTreeMap, error::Error, fmt};

use rand_chacha::ChaCha8Rng;
use serde::{Deserialize, Serialize};

use crate::{
    effective_sample_size, logsumexp, normalize_log_weights, FilterCheckpoint, FilterConfig,
    FilterResult, FilterSnapshot, Initialization, ParticleModel, Proposal, SmcError,
    SnapshotRetention, StratifiedFilterPlan, StratumAllocation, StratumDiagnostics, StratumId,
    WithinStratumResamplingPolicy,
};

use crate::stratified::run_stratified_filter_internal;

/// One scientific stratum split into independent resampling islands.
///
/// Every island estimates the same conditional target for `id`. The outer
/// filter assigns each island exactly `exp(log_prior_probability) / islands`
/// prior mass; particle allocation therefore remains a computational choice.
#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct StratumIslandAllocation {
    pub id: StratumId,
    pub islands: usize,
    pub particles_per_island: usize,
    pub log_prior_probability: f64,
}

/// Fixed island layout for one complete stratified filter run.
#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct StratifiedIslandPlan {
    pub strata: Vec<StratumIslandAllocation>,
}

impl StratifiedIslandPlan {
    pub fn validate(&self, particles: usize) -> Result<(), &'static str> {
        if self.strata.is_empty() {
            return Err("at least one island stratum is required");
        }
        let mut canonical_ids = self.strata.iter().map(|entry| entry.id).collect::<Vec<_>>();
        canonical_ids.sort_unstable();
        if canonical_ids.windows(2).any(|pair| pair[0] == pair[1]) {
            return Err("island stratum identifiers must be unique");
        }
        if self.strata.iter().any(|entry| {
            entry.islands == 0
                || entry.particles_per_island < 2
                || !entry.log_prior_probability.is_finite()
        }) {
            return Err(
                "island counts, particles per island, and prior probabilities must be valid",
            );
        }
        let allocated = self.strata.iter().try_fold(0usize, |total, entry| {
            entry
                .islands
                .checked_mul(entry.particles_per_island)
                .and_then(|count| total.checked_add(count))
        });
        if allocated != Some(particles) {
            return Err("island particle allocations must sum to the configured particle count");
        }
        let island_count = self
            .strata
            .iter()
            .try_fold(0usize, |total, entry| total.checked_add(entry.islands))
            .ok_or("island count overflowed")?;
        if island_count > u32::MAX as usize {
            return Err("island count exceeds the computational stratum identity range");
        }
        let maximum = self
            .strata
            .iter()
            .map(|entry| entry.log_prior_probability)
            .fold(f64::NEG_INFINITY, f64::max);
        let log_sum = maximum
            + self
                .strata
                .iter()
                .map(|entry| (entry.log_prior_probability - maximum).exp())
                .sum::<f64>()
                .ln();
        if !log_sum.is_finite() || log_sum.abs() > 1.0e-10 {
            return Err("island stratum log prior probabilities must be normalized");
        }
        Ok(())
    }

    fn canonical_strata(&self) -> Vec<StratumIslandAllocation> {
        let mut strata = self.strata.clone();
        strata.sort_unstable_by_key(|entry| entry.id);
        strata
    }
}

/// Stable identity of an independent resampling island.
#[derive(Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord, Hash, Serialize, Deserialize)]
pub struct IslandIdentity {
    pub scientific_stratum: StratumId,
    pub island_index: usize,
}

/// Deterministic computational allocation and root range for one island.
#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct IslandAllocation {
    pub identity: IslandIdentity,
    pub computational_stratum: StratumId,
    pub particles: usize,
    pub scientific_log_prior_probability: f64,
    pub island_log_prior_probability: f64,
    pub initial_root_start: usize,
    pub initial_root_end_exclusive: usize,
}

/// Lossless composite interpretation of the filter's compact numeric root ID.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
pub struct IslandRootIdentity {
    pub global_root: usize,
    pub island: IslandIdentity,
    pub local_root: usize,
}

#[derive(Debug, Clone, Copy, PartialEq, Serialize, Deserialize)]
#[serde(tag = "status", rename_all = "snake_case")]
pub enum IslandTermination {
    Complete,
    ExtinctAtObservation {
        observation_index: usize,
        observation_time_s: f64,
    },
}

/// One island's contribution at a particular observation checkpoint.
#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct IslandDiagnostics {
    pub identity: IslandIdentity,
    pub computational_stratum: StratumId,
    pub configured_particles: usize,
    pub globally_normalized_mass: f64,
    pub globally_normalized_log_mass: Option<f64>,
    /// Evidence for the scientific-stratum-conditional target. The scientific
    /// prior and equal island prior have both been removed.
    pub conditional_log_evidence: Option<f64>,
    pub conditional_particle_effective_sample_size: f64,
    pub conditional_maximum_particle_weight: f64,
    pub distinct_positive_root_ancestors: usize,
    pub conditional_root_effective_sample_size: f64,
}

/// Island-level diagnostics accompanying one ordinary pooled checkpoint.
#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct IslandFilterCheckpoint {
    pub observation_index: usize,
    pub observation_time_s: f64,
    pub positive_mass_islands: usize,
    pub island_effective_sample_size: f64,
    pub maximum_island_mass: f64,
    pub pooled_particle_effective_sample_size: f64,
    pub pooled_root_effective_sample_size: f64,
    pub maximum_pooled_root_mass: f64,
    pub islands: Vec<IslandDiagnostics>,
}

/// Final status and contribution of a configured island. Extinct islands stay
/// in this table and retain their configured prior denominator.
#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct IslandRunDiagnostics {
    pub allocation: IslandAllocation,
    pub termination: IslandTermination,
    pub final_globally_normalized_mass: f64,
    pub final_conditional_log_evidence: Option<f64>,
}

/// A normal filter result pooled with exact evidence weights, plus the island
/// facts needed to diagnose whether that pooling is itself well supported.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct StratifiedIslandFilterResult<S> {
    pub pooled: FilterResult<S>,
    pub islands: Vec<IslandRunDiagnostics>,
    pub island_checkpoints: Vec<IslandFilterCheckpoint>,
}

impl<S> StratifiedIslandFilterResult<S> {
    pub fn root_identity(&self, global_root: usize) -> Option<IslandRootIdentity> {
        self.islands.iter().find_map(|entry| {
            let allocation = &entry.allocation;
            (global_root >= allocation.initial_root_start
                && global_root < allocation.initial_root_end_exclusive)
                .then_some(IslandRootIdentity {
                    global_root,
                    island: allocation.identity,
                    local_root: global_root - allocation.initial_root_start,
                })
        })
    }
}

#[derive(Debug, Clone)]
struct IslandState<S> {
    inner: S,
    computational_stratum: StratumId,
}

#[derive(Debug)]
enum IslandModelError<E> {
    Inner(E),
    UnknownComputationalStratum,
    ScientificStratumChanged,
}

impl<E: fmt::Display> fmt::Display for IslandModelError<E> {
    fn fmt(&self, formatter: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            Self::Inner(error) => write!(formatter, "{error}"),
            Self::UnknownComputationalStratum => {
                formatter.write_str("unknown computational island stratum")
            }
            Self::ScientificStratumChanged => {
                formatter.write_str("particle changed its immutable scientific stratum")
            }
        }
    }
}

impl<E: Error + 'static> Error for IslandModelError<E> {
    fn source(&self) -> Option<&(dyn Error + 'static)> {
        match self {
            Self::Inner(error) => Some(error),
            Self::UnknownComputationalStratum | Self::ScientificStratumChanged => None,
        }
    }
}

struct IslandModel<'a, M> {
    inner: &'a M,
    allocations: &'a [IslandAllocation],
}

impl<M: ParticleModel> IslandModel<'_, M> {
    fn allocation(
        &self,
        computational_stratum: StratumId,
    ) -> Result<&IslandAllocation, IslandModelError<M::Error>> {
        self.allocations
            .get(computational_stratum.0 as usize)
            .filter(|entry| entry.computational_stratum == computational_stratum)
            .ok_or(IslandModelError::UnknownComputationalStratum)
    }

    fn ensure_scientific_stratum(
        &self,
        state: &M::State,
        allocation: &IslandAllocation,
    ) -> Result<(), IslandModelError<M::Error>> {
        if self.inner.stratum(state) == allocation.identity.scientific_stratum {
            Ok(())
        } else {
            Err(IslandModelError::ScientificStratumChanged)
        }
    }
}

impl<M: ParticleModel> ParticleModel for IslandModel<'_, M> {
    type State = IslandState<M::State>;
    type Observation = M::Observation;
    type Error = IslandModelError<M::Error>;

    fn observation_time_s(&self, observation: &Self::Observation) -> f64 {
        self.inner.observation_time_s(observation)
    }

    fn initialize(
        &self,
        particle_index: usize,
        rng: &mut ChaCha8Rng,
    ) -> Result<Self::State, Self::Error> {
        let allocation = self
            .allocations
            .first()
            .ok_or(IslandModelError::UnknownComputationalStratum)?;
        let initialized = self
            .inner
            .initialize_in_stratum(
                allocation.identity.scientific_stratum,
                particle_index,
                particle_index % allocation.particles,
                allocation.particles,
                rng,
            )
            .map_err(IslandModelError::Inner)?;
        self.ensure_scientific_stratum(&initialized.state, allocation)?;
        Ok(IslandState {
            inner: initialized.state,
            computational_stratum: allocation.computational_stratum,
        })
    }

    fn initialize_in_stratum(
        &self,
        stratum: StratumId,
        particle_index: usize,
        particle_index_within_stratum: usize,
        particles_in_stratum: usize,
        rng: &mut ChaCha8Rng,
    ) -> Result<Initialization<Self::State>, Self::Error> {
        let allocation = self.allocation(stratum)?;
        if particles_in_stratum != allocation.particles {
            return Err(IslandModelError::UnknownComputationalStratum);
        }
        let initialized = self
            .inner
            .initialize_in_stratum(
                allocation.identity.scientific_stratum,
                particle_index,
                particle_index_within_stratum,
                particles_in_stratum,
                rng,
            )
            .map_err(IslandModelError::Inner)?;
        self.ensure_scientific_stratum(&initialized.state, allocation)?;
        Ok(Initialization {
            state: IslandState {
                inner: initialized.state,
                computational_stratum: stratum,
            },
            log_prior_over_proposal: initialized.log_prior_over_proposal,
        })
    }

    fn stratum(&self, state: &Self::State) -> StratumId {
        state.computational_stratum
    }

    fn guide_log_likelihood(
        &self,
        state: &Self::State,
        observation: &Self::Observation,
    ) -> Result<f64, Self::Error> {
        let allocation = self.allocation(state.computational_stratum)?;
        self.ensure_scientific_stratum(&state.inner, allocation)?;
        self.inner
            .guide_log_likelihood(&state.inner, observation)
            .map_err(IslandModelError::Inner)
    }

    fn propose(
        &self,
        state: &Self::State,
        observation: &Self::Observation,
        elapsed_seconds: f64,
        rng: &mut ChaCha8Rng,
    ) -> Result<Proposal<Self::State>, Self::Error> {
        let allocation = self.allocation(state.computational_stratum)?;
        self.ensure_scientific_stratum(&state.inner, allocation)?;
        let proposal = self
            .inner
            .propose(&state.inner, observation, elapsed_seconds, rng)
            .map_err(IslandModelError::Inner)?;
        self.ensure_scientific_stratum(&proposal.state, allocation)?;
        Ok(Proposal {
            state: IslandState {
                inner: proposal.state,
                computational_stratum: state.computational_stratum,
            },
            log_prior_over_proposal: proposal.log_prior_over_proposal,
        })
    }

    fn log_likelihood(
        &self,
        state: &Self::State,
        observation: &Self::Observation,
    ) -> Result<f64, Self::Error> {
        let allocation = self.allocation(state.computational_stratum)?;
        self.ensure_scientific_stratum(&state.inner, allocation)?;
        self.inner
            .log_likelihood(&state.inner, observation)
            .map_err(IslandModelError::Inner)
    }

    fn observe(
        &self,
        state: &mut Self::State,
        observation: &Self::Observation,
    ) -> Result<f64, Self::Error> {
        let allocation = self.allocation(state.computational_stratum)?;
        self.ensure_scientific_stratum(&state.inner, allocation)?;
        let likelihood = self
            .inner
            .observe(&mut state.inner, observation)
            .map_err(IslandModelError::Inner)?;
        self.ensure_scientific_stratum(&state.inner, allocation)?;
        Ok(likelihood)
    }
}

fn expanded_plan(
    plan: &StratifiedIslandPlan,
) -> Result<(StratifiedFilterPlan, Vec<IslandAllocation>), SmcError> {
    let mut allocations = Vec::new();
    let mut islands = Vec::new();
    let mut root_start = 0usize;
    for stratum in plan.canonical_strata() {
        let island_log_prior = stratum.log_prior_probability - (stratum.islands as f64).ln();
        for island_index in 0..stratum.islands {
            let ordinal = islands.len();
            let computational_stratum = StratumId(
                u32::try_from(ordinal)
                    .map_err(|_| SmcError::InvalidConfiguration("island count overflowed"))?,
            );
            let root_end = root_start.checked_add(stratum.particles_per_island).ok_or(
                SmcError::InvalidConfiguration("island root range overflowed"),
            )?;
            allocations.push(StratumAllocation {
                id: computational_stratum,
                particles: stratum.particles_per_island,
                log_prior_probability: island_log_prior,
            });
            islands.push(IslandAllocation {
                identity: IslandIdentity {
                    scientific_stratum: stratum.id,
                    island_index,
                },
                computational_stratum,
                particles: stratum.particles_per_island,
                scientific_log_prior_probability: stratum.log_prior_probability,
                island_log_prior_probability: island_log_prior,
                initial_root_start: root_start,
                initial_root_end_exclusive: root_end,
            });
            root_start = root_end;
        }
    }
    Ok((
        StratifiedFilterPlan {
            strata: allocations,
        },
        islands,
    ))
}

fn allocation_for(
    allocations: &[IslandAllocation],
    computational_stratum: StratumId,
) -> Result<&IslandAllocation, SmcError> {
    allocations
        .get(computational_stratum.0 as usize)
        .filter(|entry| entry.computational_stratum == computational_stratum)
        .ok_or(SmcError::StratumMismatch)
}

fn island_diagnostics(
    strata: &[StratumDiagnostics],
    cumulative_log_evidence: f64,
    allocations: &[IslandAllocation],
) -> Result<Vec<IslandDiagnostics>, SmcError> {
    strata
        .iter()
        .map(|diagnostics| {
            let allocation = allocation_for(allocations, diagnostics.id)?;
            let conditional_maximum_particle_weight = diagnostics
                .log_posterior_mass
                .and_then(|log_mass| {
                    diagnostics
                        .maximum_normalized_log_weight
                        .map(|value| value - log_mass)
                })
                .map_or(0.0, f64::exp);
            Ok(IslandDiagnostics {
                identity: allocation.identity,
                computational_stratum: allocation.computational_stratum,
                configured_particles: allocation.particles,
                globally_normalized_mass: diagnostics.posterior_mass,
                globally_normalized_log_mass: diagnostics.log_posterior_mass,
                conditional_log_evidence: diagnostics.log_posterior_mass.map(|log_mass| {
                    log_mass + cumulative_log_evidence - allocation.island_log_prior_probability
                }),
                conditional_particle_effective_sample_size: diagnostics.conditional_ess,
                conditional_maximum_particle_weight,
                distinct_positive_root_ancestors: diagnostics.distinct_root_ancestors,
                conditional_root_effective_sample_size: diagnostics.root_effective_sample_size,
            })
        })
        .collect()
}

fn island_checkpoint(
    checkpoint: &FilterCheckpoint,
    allocations: &[IslandAllocation],
) -> Result<IslandFilterCheckpoint, SmcError> {
    let islands = island_diagnostics(
        &checkpoint.strata,
        checkpoint.cumulative_log_evidence,
        allocations,
    )?;
    let finite_log_masses = islands
        .iter()
        .filter_map(|entry| entry.globally_normalized_log_mass)
        .collect::<Vec<_>>();
    let (normalized, _) = normalize_log_weights(&finite_log_masses)?;
    Ok(IslandFilterCheckpoint {
        observation_index: checkpoint.observation_index,
        observation_time_s: checkpoint.observation_time_s,
        positive_mass_islands: finite_log_masses.len(),
        island_effective_sample_size: effective_sample_size(&normalized)?,
        maximum_island_mass: normalized
            .iter()
            .map(|value| value.exp())
            .fold(0.0, f64::max),
        pooled_particle_effective_sample_size: checkpoint.posterior_ess,
        pooled_root_effective_sample_size: checkpoint.root_effective_sample_size,
        maximum_pooled_root_mass: checkpoint.maximum_root_weight,
        islands,
    })
}

fn aggregate_scientific_strata(
    strata: &[StratumDiagnostics],
    allocations: &[IslandAllocation],
) -> Result<Vec<StratumDiagnostics>, SmcError> {
    let mut groups = BTreeMap::<StratumId, Vec<&StratumDiagnostics>>::new();
    for diagnostics in strata {
        let allocation = allocation_for(allocations, diagnostics.id)?;
        groups
            .entry(allocation.identity.scientific_stratum)
            .or_default()
            .push(diagnostics);
    }
    let mut aggregated = Vec::with_capacity(groups.len());
    for (id, members) in groups {
        let particle_count = members.iter().map(|entry| entry.particle_count).sum();
        let finite_log_masses = members
            .iter()
            .filter_map(|entry| entry.log_posterior_mass)
            .collect::<Vec<_>>();
        if finite_log_masses.is_empty() {
            aggregated.push(StratumDiagnostics {
                id,
                particle_count,
                posterior_mass: 0.0,
                log_posterior_mass: None,
                conditional_ess: 0.0,
                maximum_normalized_weight: 0.0,
                maximum_normalized_log_weight: None,
                distinct_root_ancestors: 0,
                root_effective_sample_size: 0.0,
            });
            continue;
        }
        let log_mass = logsumexp(&finite_log_masses)?;
        let conditional_particle_sum_squares = members
            .iter()
            .filter(|entry| entry.conditional_ess > 0.0)
            .map(|entry| {
                let island_mass = entry
                    .log_posterior_mass
                    .map_or(0.0, |value| (value - log_mass).exp());
                island_mass * island_mass / entry.conditional_ess
            })
            .sum::<f64>();
        let conditional_root_sum_squares = members
            .iter()
            .filter(|entry| entry.root_effective_sample_size > 0.0)
            .map(|entry| {
                let island_mass = entry
                    .log_posterior_mass
                    .map_or(0.0, |value| (value - log_mass).exp());
                island_mass * island_mass / entry.root_effective_sample_size
            })
            .sum::<f64>();
        let maximum_normalized_log_weight = members
            .iter()
            .filter_map(|entry| entry.maximum_normalized_log_weight)
            .max_by(|first, second| first.total_cmp(second));
        aggregated.push(StratumDiagnostics {
            id,
            particle_count,
            posterior_mass: log_mass.exp(),
            log_posterior_mass: Some(log_mass),
            conditional_ess: 1.0 / conditional_particle_sum_squares,
            maximum_normalized_weight: maximum_normalized_log_weight.map_or(0.0, f64::exp),
            maximum_normalized_log_weight,
            distinct_root_ancestors: members
                .iter()
                .map(|entry| entry.distinct_root_ancestors)
                .sum(),
            root_effective_sample_size: 1.0 / conditional_root_sum_squares,
        });
    }
    Ok(aggregated)
}

fn unwrap_snapshot<S>(
    snapshot: FilterSnapshot<IslandState<S>>,
    allocations: &[IslandAllocation],
) -> Result<FilterSnapshot<S>, SmcError> {
    let mut particles = Vec::with_capacity(snapshot.particles.len());
    let mut scientific_strata = Vec::with_capacity(snapshot.particles.len());
    for (state, declared_computational_stratum) in
        snapshot.particles.into_iter().zip(snapshot.stratum_ids)
    {
        if state.computational_stratum != declared_computational_stratum {
            return Err(SmcError::StratumMismatch);
        }
        let allocation = allocation_for(allocations, state.computational_stratum)?;
        particles.push(state.inner);
        scientific_strata.push(allocation.identity.scientific_stratum);
    }
    Ok(FilterSnapshot {
        observation_index: snapshot.observation_index,
        observation_time_s: snapshot.observation_time_s,
        particles,
        log_weights: snapshot.log_weights,
        root_ids: snapshot.root_ids,
        stratum_ids: scientific_strata,
    })
}

/// Run independent resampling islands inside every declared scientific
/// stratum and pool them with their exact evidence weights.
///
/// Computational islands are represented internally as immutable strata, so
/// existing propagation, weighting, selective snapshots, and ancestry remain
/// on the canonical filter path. An island that reaches zero mass is retained
/// as negative-infinity-weight slots. This preserves earlier snapshot ancestry
/// while ensuring it contributes exactly zero thereafter.
pub fn run_stratified_island_filter_with_snapshot_retention_and_resampling_policy<
    M: ParticleModel,
>(
    model: &M,
    observations: &[M::Observation],
    config: &FilterConfig,
    plan: &StratifiedIslandPlan,
    retention: &SnapshotRetention,
    resampling_policy: WithinStratumResamplingPolicy,
) -> Result<StratifiedIslandFilterResult<M::State>, SmcError> {
    plan.validate(config.particles)
        .map_err(SmcError::InvalidConfiguration)?;
    let (expanded_plan, allocations) = expanded_plan(plan)?;
    let island_model = IslandModel {
        inner: model,
        allocations: &allocations,
    };
    let raw = run_stratified_filter_internal(
        &island_model,
        observations,
        config,
        &expanded_plan,
        retention,
        resampling_policy,
        true,
        true,
    )?;

    let initial_island_diagnostics =
        island_diagnostics(&raw.initial_strata, raw.initial_log_evidence, &allocations)?;
    let island_checkpoints = raw
        .checkpoints
        .iter()
        .map(|checkpoint| island_checkpoint(checkpoint, &allocations))
        .collect::<Result<Vec<_>, _>>()?;
    let mut checkpoints = raw.checkpoints;
    for checkpoint in &mut checkpoints {
        checkpoint.strata = aggregate_scientific_strata(&checkpoint.strata, &allocations)?;
    }
    let initial_strata = aggregate_scientific_strata(&raw.initial_strata, &allocations)?;
    let snapshots = raw
        .snapshots
        .into_iter()
        .map(|snapshot| unwrap_snapshot(snapshot, &allocations))
        .collect::<Result<Vec<_>, _>>()?;
    let particles = raw.particles.into_iter().map(|state| state.inner).collect();
    let final_island_diagnostics = island_checkpoints
        .last()
        .map_or(initial_island_diagnostics.as_slice(), |checkpoint| {
            checkpoint.islands.as_slice()
        });
    let islands = allocations
        .iter()
        .map(|allocation| {
            let final_diagnostics = final_island_diagnostics
                .iter()
                .find(|entry| entry.identity == allocation.identity)
                .expect("validated expanded plan has one diagnostic per island");
            let first_extinction = island_checkpoints.iter().find(|checkpoint| {
                checkpoint.islands.iter().any(|entry| {
                    entry.identity == allocation.identity
                        && entry.globally_normalized_log_mass.is_none()
                })
            });
            IslandRunDiagnostics {
                allocation: allocation.clone(),
                termination: first_extinction.map_or(IslandTermination::Complete, |checkpoint| {
                    IslandTermination::ExtinctAtObservation {
                        observation_index: checkpoint.observation_index,
                        observation_time_s: checkpoint.observation_time_s,
                    }
                }),
                final_globally_normalized_mass: final_diagnostics.globally_normalized_mass,
                final_conditional_log_evidence: final_diagnostics.conditional_log_evidence,
            }
        })
        .collect();
    Ok(StratifiedIslandFilterResult {
        pooled: FilterResult {
            particles,
            log_weights: raw.log_weights,
            root_ids: raw.root_ids,
            snapshots,
            ancestry: raw.ancestry,
            checkpoints,
            log_evidence: raw.log_evidence,
            initial_log_evidence: raw.initial_log_evidence,
            initial_strata,
        },
        islands,
        island_checkpoints,
    })
}

/// Final-snapshot island filter with the default root-resampling policy.
pub fn run_stratified_island_filter<M: ParticleModel>(
    model: &M,
    observations: &[M::Observation],
    config: &FilterConfig,
    plan: &StratifiedIslandPlan,
) -> Result<StratifiedIslandFilterResult<M::State>, SmcError> {
    run_stratified_island_filter_with_snapshot_retention_and_resampling_policy(
        model,
        observations,
        config,
        plan,
        &SnapshotRetention::None,
        WithinStratumResamplingPolicy::default(),
    )
}

#[cfg(test)]
mod tests {
    use std::{convert::Infallible, f64::consts::LN_2};

    use rand::Rng;
    use rayon::ThreadPoolBuilder;

    use super::*;
    use crate::{run_stratified_filter_with_snapshot_retention, Algorithm};

    #[derive(Debug, Clone, Copy, PartialEq, Serialize, Deserialize)]
    struct ToyState {
        scientific_stratum: StratumId,
        initial_particle: usize,
        random_coordinate: f64,
    }

    #[derive(Debug, Clone, Copy)]
    enum LikelihoodRule {
        All,
        ByScientificStratum {
            selected: StratumId,
            selected_log_likelihood: f64,
            other_log_likelihood: f64,
        },
        RejectBelow {
            initial_particle: usize,
        },
        RejectParticle {
            initial_particle: usize,
        },
        Distance {
            target: f64,
        },
        GuideRejectAll,
        RejectAll,
    }

    #[derive(Debug, Clone, Copy)]
    struct ToyObservation {
        time_s: f64,
        rule: LikelihoodRule,
    }

    struct ToyModel {
        initial_log_ratios: Vec<f64>,
        use_random_proposal: bool,
    }

    impl ToyModel {
        fn from_prior() -> Self {
            Self {
                initial_log_ratios: Vec::new(),
                use_random_proposal: false,
            }
        }
    }

    impl ParticleModel for ToyModel {
        type State = ToyState;
        type Observation = ToyObservation;
        type Error = Infallible;

        fn observation_time_s(&self, observation: &Self::Observation) -> f64 {
            observation.time_s
        }

        fn initialize(
            &self,
            particle_index: usize,
            _rng: &mut ChaCha8Rng,
        ) -> Result<Self::State, Self::Error> {
            Ok(ToyState {
                scientific_stratum: StratumId::default(),
                initial_particle: particle_index,
                random_coordinate: 0.0,
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
            Ok(Initialization {
                state: ToyState {
                    scientific_stratum: stratum,
                    initial_particle: particle_index,
                    random_coordinate: 0.0,
                },
                log_prior_over_proposal: self
                    .initial_log_ratios
                    .get(particle_index)
                    .copied()
                    .unwrap_or(0.0),
            })
        }

        fn stratum(&self, state: &Self::State) -> StratumId {
            state.scientific_stratum
        }

        fn propose(
            &self,
            state: &Self::State,
            _observation: &Self::Observation,
            _elapsed_seconds: f64,
            rng: &mut ChaCha8Rng,
        ) -> Result<Proposal<Self::State>, Self::Error> {
            let mut next = *state;
            if self.use_random_proposal {
                next.random_coordinate += rng.gen::<f64>();
            }
            Ok(Proposal::from_prior(next))
        }

        fn guide_log_likelihood(
            &self,
            _state: &Self::State,
            observation: &Self::Observation,
        ) -> Result<f64, Self::Error> {
            Ok(
                if matches!(observation.rule, LikelihoodRule::GuideRejectAll) {
                    f64::NEG_INFINITY
                } else {
                    0.0
                },
            )
        }

        fn log_likelihood(
            &self,
            state: &Self::State,
            observation: &Self::Observation,
        ) -> Result<f64, Self::Error> {
            Ok(match observation.rule {
                LikelihoodRule::All => 0.0,
                LikelihoodRule::ByScientificStratum {
                    selected,
                    selected_log_likelihood,
                    other_log_likelihood,
                } => {
                    if state.scientific_stratum == selected {
                        selected_log_likelihood
                    } else {
                        other_log_likelihood
                    }
                }
                LikelihoodRule::RejectBelow { initial_particle } => {
                    if state.initial_particle < initial_particle {
                        f64::NEG_INFINITY
                    } else {
                        0.0
                    }
                }
                LikelihoodRule::RejectParticle { initial_particle } => {
                    if state.initial_particle == initial_particle {
                        f64::NEG_INFINITY
                    } else {
                        0.0
                    }
                }
                LikelihoodRule::Distance { target } => {
                    -0.5 * (state.random_coordinate - target).powi(2)
                }
                LikelihoodRule::GuideRejectAll => 0.0,
                LikelihoodRule::RejectAll => f64::NEG_INFINITY,
            })
        }
    }

    fn config(particles: usize, algorithm: Algorithm) -> FilterConfig {
        FilterConfig {
            particles,
            seed: 74_113,
            algorithm,
            initial_time_s: 0.0,
            ess_resample_fraction: 0.6,
        }
    }

    fn single_stratum_two_islands() -> StratifiedIslandPlan {
        StratifiedIslandPlan {
            strata: vec![StratumIslandAllocation {
                id: StratumId(10),
                islands: 2,
                particles_per_island: 2,
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
    fn unequal_strata_and_islands_are_pooled_by_evidence_not_particle_count() {
        let plan = StratifiedIslandPlan {
            strata: vec![
                StratumIslandAllocation {
                    id: StratumId(10),
                    islands: 2,
                    particles_per_island: 2,
                    log_prior_probability: 0.25_f64.ln(),
                },
                StratumIslandAllocation {
                    id: StratumId(20),
                    islands: 1,
                    particles_per_island: 4,
                    log_prior_probability: 0.75_f64.ln(),
                },
            ],
        };
        let observations = [ToyObservation {
            time_s: 1.0,
            rule: LikelihoodRule::ByScientificStratum {
                selected: StratumId(20),
                selected_log_likelihood: 3.0_f64.ln(),
                other_log_likelihood: 0.0,
            },
        }];
        let result = run_stratified_island_filter(
            &ToyModel::from_prior(),
            &observations,
            &config(8, Algorithm::Bootstrap),
            &plan,
        )
        .unwrap();

        assert_close(result.pooled.log_evidence, 2.5_f64.ln());
        let checkpoint = &result.island_checkpoints[0];
        assert_close(checkpoint.islands[0].globally_normalized_mass, 0.05);
        assert_close(checkpoint.islands[1].globally_normalized_mass, 0.05);
        assert_close(checkpoint.islands[2].globally_normalized_mass, 0.9);
        assert_close(checkpoint.islands[0].conditional_log_evidence.unwrap(), 0.0);
        assert_close(
            checkpoint.islands[2].conditional_log_evidence.unwrap(),
            3.0_f64.ln(),
        );
        assert_close(
            checkpoint.island_effective_sample_size,
            1.0 / (0.05_f64.powi(2) * 2.0 + 0.9_f64.powi(2)),
        );
        assert_close(
            checkpoint.pooled_particle_effective_sample_size,
            1.0 / (0.025_f64.powi(2) * 4.0 + 0.225_f64.powi(2) * 4.0),
        );
        let scientific = &result.pooled.checkpoints[0].strata;
        assert_close(scientific[0].posterior_mass, 0.1);
        assert_close(scientific[1].posterior_mass, 0.9);
        assert_close(scientific[0].conditional_ess, 4.0);
        assert_close(scientific[1].conditional_ess, 4.0);
    }

    #[test]
    fn no_observation_result_retains_each_islands_conditional_initial_evidence() {
        let model = ToyModel {
            initial_log_ratios: vec![0.0, 0.0, 3.0_f64.ln(), 3.0_f64.ln()],
            use_random_proposal: false,
        };
        let result = run_stratified_island_filter(
            &model,
            &[],
            &config(4, Algorithm::Bootstrap),
            &single_stratum_two_islands(),
        )
        .unwrap();

        assert_close(result.pooled.initial_log_evidence, 2.0_f64.ln());
        assert_close(result.pooled.log_evidence, 2.0_f64.ln());
        assert_close(result.islands[0].final_globally_normalized_mass, 0.25);
        assert_close(result.islands[1].final_globally_normalized_mass, 0.75);
        assert_close(
            result.islands[0].final_conditional_log_evidence.unwrap(),
            0.0,
        );
        assert_close(
            result.islands[1].final_conditional_log_evidence.unwrap(),
            3.0_f64.ln(),
        );
        assert_eq!(
            result.root_identity(0),
            Some(IslandRootIdentity {
                global_root: 0,
                island: IslandIdentity {
                    scientific_stratum: StratumId(10),
                    island_index: 0,
                },
                local_root: 0,
            })
        );
        assert_eq!(result.root_identity(3).unwrap().local_root, 1);
        assert_eq!(result.root_identity(4), None);
    }

    #[test]
    fn extinct_island_keeps_exact_prior_denominator_and_retained_ancestry() {
        let observations = [
            ToyObservation {
                time_s: 1.0,
                rule: LikelihoodRule::All,
            },
            ToyObservation {
                time_s: 2.0,
                rule: LikelihoodRule::RejectBelow {
                    initial_particle: 2,
                },
            },
            ToyObservation {
                time_s: 3.0,
                rule: LikelihoodRule::All,
            },
        ];
        for algorithm in [Algorithm::Bootstrap, Algorithm::Auxiliary] {
            let result =
                run_stratified_island_filter_with_snapshot_retention_and_resampling_policy(
                    &ToyModel::from_prior(),
                    &observations,
                    &config(4, algorithm),
                    &single_stratum_two_islands(),
                    &SnapshotRetention::All,
                    WithinStratumResamplingPolicy::default(),
                )
                .unwrap();

            assert_close(result.pooled.log_evidence, -LN_2);
            assert_eq!(result.pooled.snapshots.len(), 4);
            assert_eq!(result.pooled.ancestry.len(), 3);
            assert!(result
                .pooled
                .snapshots
                .iter()
                .all(|snapshot| snapshot.particles.len() == 4));
            assert_eq!(
                result.islands[0].termination,
                IslandTermination::ExtinctAtObservation {
                    observation_index: 1,
                    observation_time_s: 2.0,
                }
            );
            assert_eq!(result.islands[0].final_conditional_log_evidence, None);
            assert_close(
                result.islands[1].final_conditional_log_evidence.unwrap(),
                0.0,
            );
            assert_eq!(result.island_checkpoints[2].positive_mass_islands, 1);
            assert_close(result.island_checkpoints[2].maximum_island_mass, 1.0);
            assert_eq!(result.pooled.checkpoints[2].distinct_root_ancestors, 2);
            assert!(result.pooled.log_weights[..2]
                .iter()
                .all(|weight| *weight == f64::NEG_INFINITY));

            let smoothed = result
                .pooled
                .aggregate_descendant_weights_at_snapshot(0, &result.pooled.log_weights)
                .unwrap();
            assert!(smoothed.normalized_log_weights[..2]
                .iter()
                .all(|weight| *weight == f64::NEG_INFINITY));
            assert_eq!(smoothed.descendant_counts.iter().sum::<usize>(), 4);
        }
    }

    #[test]
    fn conditional_island_ess_triggers_only_the_degenerate_islands_resampling() {
        let observations = [
            ToyObservation {
                time_s: 1.0,
                rule: LikelihoodRule::RejectParticle {
                    initial_particle: 1,
                },
            },
            ToyObservation {
                time_s: 2.0,
                rule: LikelihoodRule::All,
            },
        ];
        let result = run_stratified_island_filter(
            &ToyModel::from_prior(),
            &observations,
            &config(4, Algorithm::Bootstrap),
            &single_stratum_two_islands(),
        )
        .unwrap();

        assert_close(result.pooled.log_evidence, 0.75_f64.ln());
        assert!(result.pooled.checkpoints[0].posterior_resampled);
        assert_eq!(result.pooled.root_ids, vec![0, 0, 2, 3]);
        assert_close(result.islands[0].final_globally_normalized_mass, 1.0 / 3.0);
        assert_close(result.islands[1].final_globally_normalized_mass, 2.0 / 3.0);
        assert_close(
            result.islands[0].final_conditional_log_evidence.unwrap(),
            -LN_2,
        );
        assert_close(
            result.islands[1].final_conditional_log_evidence.unwrap(),
            0.0,
        );
    }

    #[test]
    fn all_islands_rejected_remains_a_typed_filter_failure() {
        let observations = [ToyObservation {
            time_s: 1.0,
            rule: LikelihoodRule::RejectAll,
        }];
        for algorithm in [Algorithm::Bootstrap, Algorithm::Auxiliary] {
            let error = run_stratified_island_filter(
                &ToyModel::from_prior(),
                &observations,
                &config(4, algorithm),
                &single_stratum_two_islands(),
            )
            .unwrap_err();
            assert!(matches!(error, SmcError::AllParticlesRejected));
        }
    }

    #[test]
    fn an_unsupported_auxiliary_guide_is_fatal_not_island_extinction() {
        let observations = [ToyObservation {
            time_s: 1.0,
            rule: LikelihoodRule::GuideRejectAll,
        }];
        let error = run_stratified_island_filter(
            &ToyModel::from_prior(),
            &observations,
            &config(4, Algorithm::Auxiliary),
            &single_stratum_two_islands(),
        )
        .unwrap_err();
        assert!(matches!(error, SmcError::StratumRejected(StratumId(0))));
    }

    #[test]
    fn canonical_island_identity_is_plan_order_and_thread_invariant() {
        let first = StratumIslandAllocation {
            id: StratumId(10),
            islands: 2,
            particles_per_island: 2,
            log_prior_probability: 0.25_f64.ln(),
        };
        let second = StratumIslandAllocation {
            id: StratumId(20),
            islands: 1,
            particles_per_island: 4,
            log_prior_probability: 0.75_f64.ln(),
        };
        let observations = [
            ToyObservation {
                time_s: 1.0,
                rule: LikelihoodRule::Distance { target: 0.4 },
            },
            ToyObservation {
                time_s: 2.0,
                rule: LikelihoodRule::Distance { target: 0.8 },
            },
        ];
        let model = ToyModel {
            initial_log_ratios: Vec::new(),
            use_random_proposal: true,
        };
        let forward = StratifiedIslandPlan {
            strata: vec![first.clone(), second.clone()],
        };
        let reversed = StratifiedIslandPlan {
            strata: vec![second, first],
        };
        let one = ThreadPoolBuilder::new()
            .num_threads(1)
            .build()
            .unwrap()
            .install(|| {
                run_stratified_island_filter(
                    &model,
                    &observations,
                    &config(8, Algorithm::Auxiliary),
                    &forward,
                )
            })
            .unwrap();
        let four = ThreadPoolBuilder::new()
            .num_threads(4)
            .build()
            .unwrap()
            .install(|| {
                run_stratified_island_filter(
                    &model,
                    &observations,
                    &config(8, Algorithm::Auxiliary),
                    &reversed,
                )
            })
            .unwrap();
        assert_eq!(
            serde_json::to_vec(&one).unwrap(),
            serde_json::to_vec(&four).unwrap()
        );
    }

    #[test]
    fn one_island_is_compatible_with_the_existing_stratified_filter() {
        let observation = [ToyObservation {
            time_s: 1.0,
            rule: LikelihoodRule::RejectParticle {
                initial_particle: 3,
            },
        }];
        let filter_config = config(4, Algorithm::Bootstrap);
        let scientific_id = StratumId(10);
        let base_plan = StratifiedFilterPlan {
            strata: vec![StratumAllocation {
                id: scientific_id,
                particles: 4,
                log_prior_probability: 0.0,
            }],
        };
        let island_plan = StratifiedIslandPlan {
            strata: vec![StratumIslandAllocation {
                id: scientific_id,
                islands: 1,
                particles_per_island: 4,
                log_prior_probability: 0.0,
            }],
        };
        let model = ToyModel::from_prior();
        let base = run_stratified_filter_with_snapshot_retention(
            &model,
            &observation,
            &filter_config,
            &base_plan,
            &SnapshotRetention::All,
        )
        .unwrap();
        let island = run_stratified_island_filter_with_snapshot_retention_and_resampling_policy(
            &model,
            &observation,
            &filter_config,
            &island_plan,
            &SnapshotRetention::All,
            WithinStratumResamplingPolicy::default(),
        )
        .unwrap();
        assert_eq!(
            serde_json::to_vec(&base).unwrap(),
            serde_json::to_vec(&island.pooled).unwrap()
        );
    }

    #[test]
    fn island_plan_rejects_invalid_or_ambiguous_allocations() {
        let valid = single_stratum_two_islands();
        assert!(valid.validate(4).is_ok());
        assert!(valid.validate(5).is_err());

        let mut invalid = valid.clone();
        invalid.strata[0].particles_per_island = 1;
        assert!(invalid.validate(2).is_err());

        let duplicate = StratifiedIslandPlan {
            strata: vec![valid.strata[0].clone(), valid.strata[0].clone()],
        };
        assert!(duplicate.validate(8).is_err());

        let unnormalized = StratifiedIslandPlan {
            strata: vec![StratumIslandAllocation {
                log_prior_probability: 0.5_f64.ln(),
                ..valid.strata[0].clone()
            }],
        };
        assert!(unnormalized.validate(4).is_err());
    }
}
