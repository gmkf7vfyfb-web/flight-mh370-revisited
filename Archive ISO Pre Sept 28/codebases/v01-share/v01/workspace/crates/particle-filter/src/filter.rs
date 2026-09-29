use std::collections::BTreeMap;

use rand::Rng;
use rayon::prelude::*;
use serde::{Deserialize, Serialize};
use thiserror::Error;

use crate::{
    aggregate_log_weights_by_ancestor, effective_sample_size, normalize_log_weights, rng_for,
    systematic_resample, Algorithm, FilterConfig, ParticleModel, StratumId,
};

#[derive(Debug, Error)]
pub enum SmcError {
    #[error("invalid filter configuration: {0}")]
    InvalidConfiguration(&'static str),
    #[error("observation times must be finite, ordered, and not precede the initial time")]
    InvalidObservationTime,
    #[error("particle model failed: {0}")]
    Model(String),
    #[error("particle weight is NaN or positive infinity")]
    InvalidWeights,
    #[error("all particles received zero probability")]
    AllParticlesRejected,
    #[error("systematic-resampling offset is outside [0, 1/N)")]
    InvalidResamplingOffset,
    #[error("particle ancestry is absent or internally inconsistent")]
    InvalidAncestry,
    #[error("requested filter snapshot does not exist")]
    InvalidSnapshot,
    #[error("particle state does not carry its declared immutable stratum")]
    StratumMismatch,
    #[error("all particles in stratum {0:?} received zero probability")]
    StratumRejected(StratumId),
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct StratumDiagnostics {
    pub id: StratumId,
    pub particle_count: usize,
    pub posterior_mass: f64,
    /// Log mass remains informative when the corresponding linear mass
    /// underflows to zero.
    pub log_posterior_mass: Option<f64>,
    /// ESS after weights are normalized within this stratum.
    pub conditional_ess: f64,
    pub maximum_normalized_weight: f64,
    pub maximum_normalized_log_weight: Option<f64>,
    pub distinct_root_ancestors: usize,
    pub root_effective_sample_size: f64,
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct FilterCheckpoint {
    pub observation_index: usize,
    pub observation_time_s: f64,
    pub guide_ess: Option<f64>,
    pub posterior_ess: f64,
    pub ancestor_resampled: bool,
    pub posterior_resampled: bool,
    pub log_evidence_increment: f64,
    pub cumulative_log_evidence: f64,
    #[serde(default)]
    pub maximum_normalized_weight: f64,
    #[serde(default)]
    pub distinct_root_ancestors: usize,
    #[serde(default)]
    pub root_effective_sample_size: f64,
    #[serde(default)]
    pub maximum_root_weight: f64,
    #[serde(default)]
    pub roots_with_mass_at_least_1e_6: usize,
    #[serde(default)]
    pub roots_with_mass_at_least_1e_3: usize,
    #[serde(default)]
    pub strata: Vec<StratumDiagnostics>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct FilterSnapshot<S> {
    pub observation_index: Option<usize>,
    pub observation_time_s: f64,
    pub particles: Vec<S>,
    pub log_weights: Vec<f64>,
    pub root_ids: Vec<usize>,
    #[serde(default)]
    pub stratum_ids: Vec<StratumId>,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord, Serialize, Deserialize)]
pub struct FilterParticleIdentity {
    /// `None` identifies the initialized population; `Some(i)` identifies the
    /// population immediately after assimilating observation `i`.
    pub observation_index: Option<usize>,
    pub particle_index: usize,
}

impl<S> FilterSnapshot<S> {
    pub fn particle_identity(
        &self,
        particle_index: usize,
    ) -> Result<FilterParticleIdentity, SmcError> {
        if particle_index >= self.particles.len() {
            return Err(SmcError::InvalidSnapshot);
        }
        Ok(FilterParticleIdentity {
            observation_index: self.observation_index,
            particle_index,
        })
    }
}

/// Exact child-slot to parent-slot map between consecutive retained snapshots.
/// Intervening unretained epochs and resampling operations are already
/// composed into each map.
#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct FilterAncestryStep {
    pub child_observation_index: usize,
    #[serde(default)]
    pub parent_observation_index: Option<usize>,
    pub parent_indices: Vec<usize>,
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct SmoothedSnapshotWeights {
    pub observation_index: Option<usize>,
    pub observation_time_s: f64,
    pub normalized_log_weights: Vec<f64>,
    pub descendant_counts: Vec<usize>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct FilterResult<S> {
    pub particles: Vec<S>,
    pub log_weights: Vec<f64>,
    pub root_ids: Vec<usize>,
    pub snapshots: Vec<FilterSnapshot<S>>,
    #[serde(default)]
    pub ancestry: Vec<FilterAncestryStep>,
    pub checkpoints: Vec<FilterCheckpoint>,
    pub log_evidence: f64,
    #[serde(default)]
    pub initial_log_evidence: f64,
    #[serde(default)]
    pub initial_strata: Vec<StratumDiagnostics>,
}

#[derive(Debug, Clone, Copy, Default)]
pub struct FilterRunOptions {
    pub retain_snapshots: bool,
}

/// Select state populations to retain while preserving exact ancestry through
/// skipped epochs. A selected policy also retains the final observation
/// population so later weights can be traced back to every selected snapshot.
#[derive(Debug, Clone, PartialEq, Eq)]
pub enum SnapshotRetention {
    None,
    All,
    SelectedObservationIndices(Vec<usize>),
}

impl SnapshotRetention {
    pub(crate) fn retains_initial(&self) -> bool {
        matches!(self, Self::All)
    }

    pub(crate) fn retains_observation(
        &self,
        observation_index: usize,
        observations: usize,
    ) -> bool {
        match self {
            Self::None => false,
            Self::All => true,
            Self::SelectedObservationIndices(indices) => {
                observation_index + 1 == observations || indices.contains(&observation_index)
            }
        }
    }

    pub(crate) fn validate(&self, observations: usize) -> Result<(), SmcError> {
        if let Self::SelectedObservationIndices(indices) = self {
            if indices.iter().any(|&index| index >= observations) {
                return Err(SmcError::InvalidSnapshot);
            }
            let mut canonical = indices.clone();
            canonical.sort_unstable();
            canonical.dedup();
            if canonical.len() != indices.len() {
                return Err(SmcError::InvalidSnapshot);
            }
        }
        Ok(())
    }
}

impl<S> FilterResult<S> {
    pub fn normalized_weights(&self) -> Vec<f64> {
        self.log_weights.iter().map(|value| value.exp()).collect()
    }

    pub fn effective_sample_size(&self) -> Result<f64, SmcError> {
        effective_sample_size(&self.log_weights)
    }

    /// Aggregate arbitrary descendant weights at the final filter population
    /// onto a retained earlier snapshot. This is the discrete particle-smoother
    /// operation needed when a later conditional branch reweights descendants.
    pub fn aggregate_descendant_weights_at_snapshot(
        &self,
        snapshot_position: usize,
        descendant_log_weights: &[f64],
    ) -> Result<SmoothedSnapshotWeights, SmcError> {
        if self.snapshots.is_empty()
            || snapshot_position >= self.snapshots.len()
            || descendant_log_weights.len() != self.particles.len()
            || self.ancestry.len() + 1 != self.snapshots.len()
            || self
                .snapshots
                .last()
                .map(|snapshot| snapshot.particles.len())
                != Some(self.particles.len())
            || self.ancestry.iter().enumerate().any(|(index, step)| {
                Some(step.child_observation_index) != self.snapshots[index + 1].observation_index
                    || step.parent_observation_index != self.snapshots[index].observation_index
                    || step.parent_indices.len() != self.snapshots[index + 1].particles.len()
            })
        {
            return Err(SmcError::InvalidSnapshot);
        }
        let mut ancestor_indices = (0..self.particles.len()).collect::<Vec<_>>();
        for step in self.ancestry[snapshot_position..].iter().rev() {
            for ancestor in &mut ancestor_indices {
                *ancestor = *step
                    .parent_indices
                    .get(*ancestor)
                    .ok_or(SmcError::InvalidAncestry)?;
            }
        }
        let snapshot = &self.snapshots[snapshot_position];
        let normalized_log_weights = aggregate_log_weights_by_ancestor(
            &ancestor_indices,
            snapshot.particles.len(),
            descendant_log_weights,
        )?;
        let mut descendant_counts = vec![0usize; snapshot.particles.len()];
        for ancestor in ancestor_indices {
            descendant_counts[ancestor] += 1;
        }
        Ok(SmoothedSnapshotWeights {
            observation_index: snapshot.observation_index,
            observation_time_s: snapshot.observation_time_s,
            normalized_log_weights,
            descendant_counts,
        })
    }
}

pub(crate) struct WeightDiagnostics {
    pub maximum_normalized_weight: f64,
    pub distinct_root_ancestors: usize,
    pub root_effective_sample_size: f64,
    pub maximum_root_weight: f64,
    pub roots_with_mass_at_least_1e_6: usize,
    pub roots_with_mass_at_least_1e_3: usize,
    pub strata: Vec<StratumDiagnostics>,
}

pub(crate) fn weight_diagnostics(
    log_weights: &[f64],
    root_ids: &[usize],
    stratum_ids: &[StratumId],
) -> Result<WeightDiagnostics, SmcError> {
    if log_weights.len() != root_ids.len() || log_weights.len() != stratum_ids.len() {
        return Err(SmcError::InvalidAncestry);
    }
    let (normalized, _) = normalize_log_weights(log_weights)?;
    let weights = normalized
        .iter()
        .map(|value| value.exp())
        .collect::<Vec<_>>();
    let maximum_normalized_weight = weights.iter().copied().fold(0.0, f64::max);
    let mut root_mass = BTreeMap::<usize, f64>::new();
    for ((&root, &weight), &log_weight) in root_ids.iter().zip(&weights).zip(&normalized) {
        // A negative-infinity log weight is exactly zero mass even when the
        // root identifier remains in a retained/extinct particle slot.
        if log_weight.is_finite() {
            *root_mass.entry(root).or_default() += weight;
        }
    }
    let distinct_root_ancestors = root_mass.len();
    let root_effective_sample_size = 1.0
        / root_mass
            .values()
            .map(|weight| weight * weight)
            .sum::<f64>();
    let maximum_root_weight = root_mass.values().copied().fold(0.0, f64::max);
    let roots_with_mass_at_least_1e_6 = root_mass
        .values()
        .filter(|&&weight| weight >= 1.0e-6)
        .count();
    let roots_with_mass_at_least_1e_3 = root_mass
        .values()
        .filter(|&&weight| weight >= 1.0e-3)
        .count();

    let mut members = BTreeMap::<StratumId, Vec<usize>>::new();
    for (particle, &stratum) in stratum_ids.iter().enumerate() {
        members.entry(stratum).or_default().push(particle);
    }
    let mut strata = Vec::with_capacity(members.len());
    for (id, particles) in members {
        let stratum_log_weights = particles
            .iter()
            .map(|&index| normalized[index])
            .collect::<Vec<_>>();
        let log_posterior_mass = match crate::logsumexp(&stratum_log_weights) {
            Ok(value) => value,
            Err(SmcError::AllParticlesRejected) => {
                strata.push(StratumDiagnostics {
                    id,
                    particle_count: particles.len(),
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
            Err(error) => return Err(error),
        };
        let posterior_mass = log_posterior_mass.exp();
        let conditional_sum_squares = particles
            .iter()
            .map(|&index| (2.0 * (normalized[index] - log_posterior_mass)).exp())
            .sum::<f64>();
        let mut stratum_root_mass = BTreeMap::<usize, f64>::new();
        for &index in &particles {
            if normalized[index].is_finite() {
                *stratum_root_mass.entry(root_ids[index]).or_default() +=
                    (normalized[index] - log_posterior_mass).exp();
            }
        }
        let maximum_normalized_log_weight = particles
            .iter()
            .map(|&index| normalized[index])
            .fold(f64::NEG_INFINITY, f64::max);
        strata.push(StratumDiagnostics {
            id,
            particle_count: particles.len(),
            posterior_mass,
            log_posterior_mass: Some(log_posterior_mass),
            conditional_ess: 1.0 / conditional_sum_squares,
            maximum_normalized_weight: maximum_normalized_log_weight.exp(),
            maximum_normalized_log_weight: Some(maximum_normalized_log_weight),
            distinct_root_ancestors: stratum_root_mass.len(),
            root_effective_sample_size: 1.0
                / stratum_root_mass
                    .values()
                    .map(|weight| weight * weight)
                    .sum::<f64>(),
        });
    }
    Ok(WeightDiagnostics {
        maximum_normalized_weight,
        distinct_root_ancestors,
        root_effective_sample_size,
        maximum_root_weight,
        roots_with_mass_at_least_1e_6,
        roots_with_mass_at_least_1e_3,
        strata,
    })
}

struct EpochResult<S> {
    states: Vec<S>,
    log_weights: Vec<f64>,
    ancestor_indices: Vec<usize>,
    guide_ess: Option<f64>,
    posterior_ess: f64,
    ancestor_resampled: bool,
    log_evidence_increment: f64,
}

fn model_error(error: impl std::fmt::Display) -> SmcError {
    SmcError::Model(error.to_string())
}

fn resample_indices(
    log_weights: &[f64],
    seed: u64,
    purpose: &str,
    epoch: usize,
) -> Result<Vec<usize>, SmcError> {
    let weights = log_weights
        .iter()
        .map(|value| value.exp())
        .collect::<Vec<_>>();
    let mut rng = rng_for(seed, purpose, epoch, 0, 0);
    let first_offset = rng.gen::<f64>() / log_weights.len() as f64;
    systematic_resample(&weights, first_offset)
}

fn run_bootstrap_epoch<M: ParticleModel>(
    model: &M,
    states: &[M::State],
    log_weights: &[f64],
    observation: &M::Observation,
    elapsed_seconds: f64,
    epoch: usize,
    config: &FilterConfig,
) -> Result<EpochResult<M::State>, SmcError> {
    let proposals = states
        .par_iter()
        .enumerate()
        .map(|(particle, state)| {
            let mut rng = rng_for(config.seed, "bootstrap-proposal", epoch, particle, 0);
            let mut proposal = model
                .propose(state, observation, elapsed_seconds, &mut rng)
                .map_err(model_error)?;
            if !proposal.log_prior_over_proposal.is_finite() {
                return Err(SmcError::InvalidWeights);
            }
            let likelihood = model
                .observe(&mut proposal.state, observation)
                .map_err(model_error)?;
            if !(likelihood.is_finite() || likelihood == f64::NEG_INFINITY) {
                return Err(SmcError::InvalidWeights);
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
    let ess = effective_sample_size(&normalized)?;
    Ok(EpochResult {
        states: new_states,
        log_weights: normalized,
        ancestor_indices: (0..states.len()).collect(),
        guide_ess: None,
        posterior_ess: ess,
        ancestor_resampled: false,
        log_evidence_increment,
    })
}

fn run_auxiliary_epoch<M: ParticleModel>(
    model: &M,
    states: &[M::State],
    log_weights: &[f64],
    observation: &M::Observation,
    elapsed_seconds: f64,
    epoch: usize,
    config: &FilterConfig,
) -> Result<EpochResult<M::State>, SmcError> {
    let guides = states
        .par_iter()
        .map(|state| {
            let value = model
                .guide_log_likelihood(state, observation)
                .map_err(model_error)?;
            if value.is_finite() || value == f64::NEG_INFINITY {
                Ok(value)
            } else {
                Err(SmcError::InvalidWeights)
            }
        })
        .collect::<Vec<Result<f64, SmcError>>>();
    let guides = guides.into_iter().collect::<Result<Vec<_>, _>>()?;

    let ancestor_raw = log_weights
        .iter()
        .zip(&guides)
        .map(|(weight, guide)| weight + guide)
        .collect::<Vec<_>>();
    let (ancestor_log_weights, guide_normalizer) = normalize_log_weights(&ancestor_raw)?;
    let guide_ess = effective_sample_size(&ancestor_log_weights)?;
    let ancestor_weights = ancestor_log_weights
        .iter()
        .map(|value| value.exp())
        .collect::<Vec<_>>();
    let mut ancestor_rng = rng_for(config.seed, "auxiliary-ancestor", epoch, 0, 0);
    let first_offset = ancestor_rng.gen::<f64>() / states.len() as f64;
    let ancestors = systematic_resample(&ancestor_weights, first_offset)?;

    let proposals = ancestors
        .par_iter()
        .enumerate()
        .map(|(particle, ancestor)| {
            let mut rng = rng_for(config.seed, "auxiliary-proposal", epoch, particle, 0);
            let mut proposal = model
                .propose(&states[*ancestor], observation, elapsed_seconds, &mut rng)
                .map_err(model_error)?;
            if !proposal.log_prior_over_proposal.is_finite() {
                return Err(SmcError::InvalidWeights);
            }
            let likelihood = model
                .observe(&mut proposal.state, observation)
                .map_err(model_error)?;
            if !(likelihood.is_finite() || likelihood == f64::NEG_INFINITY) {
                return Err(SmcError::InvalidWeights);
            }
            Ok((
                proposal.state,
                likelihood + proposal.log_prior_over_proposal - guides[*ancestor],
            ))
        })
        .collect::<Vec<Result<_, SmcError>>>();

    let mut new_states = Vec::with_capacity(states.len());
    let mut correction_weights = Vec::with_capacity(states.len());
    for proposal in proposals {
        let (state, weight) = proposal?;
        new_states.push(state);
        correction_weights.push(weight);
    }
    let (normalized, correction_normalizer) = normalize_log_weights(&correction_weights)?;
    let posterior_ess = effective_sample_size(&normalized)?;
    let log_evidence_increment =
        guide_normalizer + correction_normalizer - (states.len() as f64).ln();
    Ok(EpochResult {
        states: new_states,
        log_weights: normalized,
        ancestor_indices: ancestors,
        guide_ess: Some(guide_ess),
        posterior_ess,
        ancestor_resampled: true,
        log_evidence_increment,
    })
}

pub fn run_filter<M: ParticleModel>(
    model: &M,
    observations: &[M::Observation],
    config: &FilterConfig,
) -> Result<FilterResult<M::State>, SmcError> {
    run_filter_with_options(model, observations, config, FilterRunOptions::default())
}

pub fn run_filter_with_options<M: ParticleModel>(
    model: &M,
    observations: &[M::Observation],
    config: &FilterConfig,
    options: FilterRunOptions,
) -> Result<FilterResult<M::State>, SmcError> {
    let retention = if options.retain_snapshots {
        SnapshotRetention::All
    } else {
        SnapshotRetention::None
    };
    run_filter_with_snapshot_retention(model, observations, config, &retention)
}

pub fn run_filter_with_snapshot_retention<M: ParticleModel>(
    model: &M,
    observations: &[M::Observation],
    config: &FilterConfig,
    retention: &SnapshotRetention,
) -> Result<FilterResult<M::State>, SmcError> {
    config.validate().map_err(SmcError::InvalidConfiguration)?;
    retention.validate(observations.len())?;

    let mut previous_time = config.initial_time_s;
    for observation in observations {
        let time = model.observation_time_s(observation);
        if !time.is_finite() || time < previous_time {
            return Err(SmcError::InvalidObservationTime);
        }
        previous_time = time;
    }

    let initialized = (0..config.particles)
        .into_par_iter()
        .map(|particle| {
            let mut rng = rng_for(config.seed, "initialize", 0, particle, 0);
            model.initialize(particle, &mut rng).map_err(model_error)
        })
        .collect::<Vec<Result<M::State, SmcError>>>();
    let mut states = initialized.into_iter().collect::<Result<Vec<_>, _>>()?;
    let uniform_log_weight = -(config.particles as f64).ln();
    let mut log_weights = vec![uniform_log_weight; config.particles];
    let mut root_ids = (0..config.particles).collect::<Vec<_>>();
    let mut stratum_ids = states
        .iter()
        .map(|state| model.stratum(state))
        .collect::<Vec<_>>();
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
    let mut log_evidence = 0.0;
    previous_time = config.initial_time_s;

    for (epoch, observation) in observations.iter().enumerate() {
        let observation_time = model.observation_time_s(observation);
        let elapsed_seconds = observation_time - previous_time;
        let epoch_result = match config.algorithm {
            Algorithm::Bootstrap => run_bootstrap_epoch(
                model,
                &states,
                &log_weights,
                observation,
                elapsed_seconds,
                epoch,
                config,
            )?,
            Algorithm::Auxiliary => run_auxiliary_epoch(
                model,
                &states,
                &log_weights,
                observation,
                elapsed_seconds,
                epoch,
                config,
            )?,
        };
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
        root_ids = epoch_result
            .ancestor_indices
            .iter()
            .map(|index| root_ids[*index])
            .collect();
        stratum_ids = states
            .iter()
            .map(|state| model.stratum(state))
            .collect::<Vec<_>>();
        let guide_ess = epoch_result.guide_ess;
        let posterior_ess = epoch_result.posterior_ess;
        let ancestor_resampled = epoch_result.ancestor_resampled;
        let increment = epoch_result.log_evidence_increment;
        let mut posterior_resampled = false;
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

        if config.algorithm == Algorithm::Bootstrap
            && epoch + 1 < observations.len()
            && posterior_ess < config.ess_resample_fraction * config.particles as f64
        {
            let indices = resample_indices(&log_weights, config.seed, "posterior-resample", epoch)?;
            states = indices.iter().map(|index| states[*index].clone()).collect();
            root_ids = indices.iter().map(|index| root_ids[*index]).collect();
            log_weights.fill(uniform_log_weight);
            working_to_previous_snapshot = if retain_epoch {
                indices
            } else if has_retained_snapshot {
                indices
                    .iter()
                    .map(|index| snapshot_parent_indices[*index])
                    .collect()
            } else {
                Vec::new()
            };
            posterior_resampled = true;
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
        previous_time = observation_time;
    }

    Ok(FilterResult {
        particles: states,
        log_weights,
        root_ids,
        snapshots,
        ancestry,
        checkpoints,
        log_evidence,
        initial_log_evidence: 0.0,
        initial_strata,
    })
}

#[cfg(test)]
mod tests {
    use std::{error::Error, fmt};

    use rand_distr::{Distribution, StandardNormal};
    use rayon::ThreadPoolBuilder;
    use serde::Serialize;

    use super::*;
    use crate::Proposal;

    #[derive(Debug, Clone, Copy, PartialEq, Serialize)]
    struct State {
        time: f64,
        x: f64,
    }

    #[derive(Debug, Clone, Copy)]
    struct Observation {
        time: f64,
        y: f64,
    }

    #[derive(Debug)]
    struct TestError;

    impl fmt::Display for TestError {
        fn fmt(&self, formatter: &mut fmt::Formatter<'_>) -> fmt::Result {
            formatter.write_str("test model error")
        }
    }

    impl Error for TestError {}

    struct GaussianModel;

    impl ParticleModel for GaussianModel {
        type State = State;
        type Observation = Observation;
        type Error = TestError;

        fn observation_time_s(&self, observation: &Self::Observation) -> f64 {
            observation.time
        }

        fn initialize(
            &self,
            _particle_index: usize,
            rng: &mut rand_chacha::ChaCha8Rng,
        ) -> Result<Self::State, Self::Error> {
            let draw: f64 = StandardNormal.sample(rng);
            Ok(State {
                time: 0.0,
                x: draw * 3.0,
            })
        }

        fn guide_log_likelihood(
            &self,
            state: &Self::State,
            observation: &Self::Observation,
        ) -> Result<f64, Self::Error> {
            Ok(-0.5 * ((observation.y - state.x) / 2.0).powi(2))
        }

        fn propose(
            &self,
            state: &Self::State,
            observation: &Self::Observation,
            elapsed_seconds: f64,
            rng: &mut rand_chacha::ChaCha8Rng,
        ) -> Result<Proposal<Self::State>, Self::Error> {
            let draw: f64 = StandardNormal.sample(rng);
            Ok(Proposal::from_prior(State {
                time: observation.time,
                x: state.x + draw * 0.2 * elapsed_seconds.sqrt(),
            }))
        }

        fn log_likelihood(
            &self,
            state: &Self::State,
            observation: &Self::Observation,
        ) -> Result<f64, Self::Error> {
            Ok(-0.5 * (observation.y - state.x).powi(2) - 0.5 * (2.0 * std::f64::consts::PI).ln())
        }
    }

    fn config(algorithm: Algorithm) -> FilterConfig {
        FilterConfig {
            particles: 2_000,
            seed: 4_201,
            algorithm,
            initial_time_s: 0.0,
            ess_resample_fraction: 0.5,
        }
    }

    fn posterior_mean(result: &FilterResult<State>) -> f64 {
        result
            .particles
            .iter()
            .zip(result.normalized_weights())
            .map(|(state, weight)| state.x * weight)
            .sum()
    }

    #[test]
    fn bootstrap_and_auxiliary_filters_recover_gaussian_location() {
        let observations = [
            Observation { time: 1.0, y: 1.5 },
            Observation { time: 2.0, y: 1.6 },
            Observation { time: 3.0, y: 1.4 },
        ];
        for algorithm in [Algorithm::Bootstrap, Algorithm::Auxiliary] {
            let result = run_filter(&GaussianModel, &observations, &config(algorithm)).unwrap();
            assert!((posterior_mean(&result) - 1.5).abs() < 0.2);
            assert!(result.log_evidence.is_finite());
            assert_eq!(result.checkpoints.len(), observations.len());
        }
    }

    #[test]
    fn results_are_identical_across_thread_counts() {
        let observations = [
            Observation { time: 1.0, y: 0.4 },
            Observation { time: 2.0, y: 0.5 },
        ];
        let one = ThreadPoolBuilder::new()
            .num_threads(1)
            .build()
            .unwrap()
            .install(|| run_filter(&GaussianModel, &observations, &config(Algorithm::Auxiliary)))
            .unwrap();
        let four = ThreadPoolBuilder::new()
            .num_threads(4)
            .build()
            .unwrap()
            .install(|| run_filter(&GaussianModel, &observations, &config(Algorithm::Auxiliary)))
            .unwrap();
        assert_eq!(
            serde_json::to_vec(&one).unwrap(),
            serde_json::to_vec(&four).unwrap()
        );
    }
}
