use std::collections::{BTreeMap, HashSet};

use mh370_domain::LatLon;
use rayon::prelude::*;
use serde::{Deserialize, Serialize};
use thiserror::Error;

use crate::{
    sampling::{simulate_ensemble, EnsembleRequest},
    ArrivalSamplingConfig, BarnacleIsotopeModel, DebrisEvidence, DriftEnvironment, DriftPath,
    GriddedField, IsotopeError, IsotopeEvaluation, MotionConfig, NonRecoveryEvaluation,
    PathTerminationReason, RecoveryEvaluation, RecoveryEvent, SamplingDiagnostics,
};

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct SourceAreaCell {
    pub id: String,
    pub position: LatLon,
    pub prior_weight: f64,
}

/// An object-motion family is distinct from the environmental current family.
/// Recovery events in one family share a transport law but receive separate
/// adaptive ensembles. A family with no recovery event represents an explicit
/// unobserved-debris population for non-recovery evidence and is propagated
/// independently. Incompatible current products remain separate invocations.
#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct DebrisMotionFamily {
    pub id: String,
    pub motion: MotionConfig,
    pub debris: DebrisEvidence,
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct SourceAreaConfig {
    pub family: String,
    pub seed: u64,
    /// Number of paths per source cell and independent recovery episode.
    pub particles_per_cell: usize,
    pub release_unix_seconds: f64,
    pub sampling: ArrivalSamplingConfig,
    pub motion_families: Vec<DebrisMotionFamily>,
    pub isotope: Option<BarnacleIsotopeModel>,
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct RecoveryEnsembleEvaluation {
    pub event_id: String,
    pub terminated_fraction: f64,
    pub proposal_terminated_fraction: f64,
    pub termination_reasons: BTreeMap<PathTerminationReason, usize>,
    pub termination_reason_fractions: BTreeMap<PathTerminationReason, f64>,
    pub sampling: SamplingDiagnostics,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum SourceCellStatus {
    Supported,
    /// No represented flaperon arrival was available to screen. The isotope
    /// term is neutral rather than turning Monte Carlo absence into rejection.
    NoFlaperonArrival,
    IsotopeUnavailable,
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct MotionFamilyEvaluation {
    pub id: String,
    pub debris_log_compatibility: f64,
    pub terminated_fraction: f64,
    pub proposal_terminated_fraction: f64,
    pub termination_reasons: BTreeMap<PathTerminationReason, usize>,
    pub termination_reason_fractions: BTreeMap<PathTerminationReason, f64>,
    /// First configured episode for schema compatibility. Complete
    /// event-targeted proposal diagnostics are in `recovery_ensembles`.
    pub sampling: SamplingDiagnostics,
    #[serde(default)]
    pub recovery_ensembles: Vec<RecoveryEnsembleEvaluation>,
    pub recoveries: Vec<RecoveryEvaluation>,
    pub non_recoveries: Vec<NonRecoveryEvaluation>,
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct SourceCellResult {
    pub id: String,
    pub position: LatLon,
    pub prior_weight: f64,
    pub debris_log_compatibility: f64,
    /// P(isotope | represented flaperon arrival), absent when isotope is off
    /// or the adaptive sample contains no represented arrival.
    #[serde(alias = "conditional_isotope_log_likelihood")]
    pub conditional_isotope_log_compatibility: Option<f64>,
    pub combined_log_weight: Option<f64>,
    pub normalized_weight: f64,
    /// Aggregate across object-motion families. Family-specific values are
    /// retained below and should be used for scientific interpretation.
    pub terminated_fraction: f64,
    #[serde(default)]
    pub proposal_terminated_fraction: f64,
    pub termination_reasons: BTreeMap<PathTerminationReason, usize>,
    #[serde(default)]
    pub termination_reason_fractions: BTreeMap<PathTerminationReason, f64>,
    /// Flaperon-family sampler diagnostics when present, otherwise the first
    /// configured family. Complete diagnostics are in `motion_families`.
    #[serde(default)]
    pub sampling: SamplingDiagnostics,
    pub status: SourceCellStatus,
    pub recoveries: Vec<RecoveryEvaluation>,
    #[serde(default)]
    pub non_recoveries: Vec<NonRecoveryEvaluation>,
    #[serde(default)]
    pub motion_families: Vec<MotionFamilyEvaluation>,
    pub isotope: Option<IsotopeEvaluation>,
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct SourceAreaResult {
    pub family: String,
    pub seed: u64,
    pub particles_per_cell: usize,
    pub motion_family_ids: Vec<String>,
    pub isotope_enabled: bool,
    pub cells: Vec<SourceCellResult>,
    pub peak_cell_id: String,
    pub peak_position: LatLon,
    pub mean_terminated_fraction: f64,
    #[serde(default)]
    pub mean_proposal_terminated_fraction: f64,
}

#[derive(Debug, Error)]
pub enum SourceAreaError {
    #[error("source-area configuration is invalid")]
    InvalidConfiguration,
    #[error("source cell {0} failed: {1}")]
    Cell(String, String),
    #[error("all source cells have zero or invalid weight")]
    NoFiniteWeight,
}

pub fn evaluate_source_area(
    config: &SourceAreaConfig,
    cells: &[SourceAreaCell],
    environment: DriftEnvironment<'_>,
    sst: Option<&GriddedField>,
) -> Result<SourceAreaResult, SourceAreaError> {
    validate(config, cells, sst)?;

    let preliminary = cells
        .par_iter()
        .map(|cell| evaluate_cell(config, cell, environment, sst))
        .collect::<Vec<_>>();
    let mut results = preliminary.into_iter().collect::<Result<Vec<_>, _>>()?;

    let maximum = results
        .iter()
        .filter_map(|cell| cell.combined_log_weight)
        .filter(|value| value.is_finite())
        .fold(f64::NEG_INFINITY, f64::max);
    if !maximum.is_finite() {
        return Err(SourceAreaError::NoFiniteWeight);
    }
    let total = results
        .iter()
        .filter_map(|cell| cell.combined_log_weight)
        .map(|value| (value - maximum).exp())
        .sum::<f64>();
    if !total.is_finite() || total <= 0.0 {
        return Err(SourceAreaError::NoFiniteWeight);
    }
    for cell in &mut results {
        cell.normalized_weight = cell
            .combined_log_weight
            .map_or(0.0, |value| (value - maximum).exp() / total);
    }
    let peak = results
        .iter()
        .max_by(|first, second| first.normalized_weight.total_cmp(&second.normalized_weight))
        .ok_or(SourceAreaError::NoFiniteWeight)?;
    Ok(SourceAreaResult {
        family: config.family.clone(),
        seed: config.seed,
        particles_per_cell: config.particles_per_cell,
        motion_family_ids: config
            .motion_families
            .iter()
            .map(|family| family.id.clone())
            .collect(),
        isotope_enabled: config.isotope.is_some(),
        peak_cell_id: peak.id.clone(),
        peak_position: peak.position,
        mean_terminated_fraction: results
            .iter()
            .map(|cell| cell.terminated_fraction)
            .sum::<f64>()
            / results.len() as f64,
        mean_proposal_terminated_fraction: results
            .iter()
            .map(|cell| cell.proposal_terminated_fraction)
            .sum::<f64>()
            / results.len() as f64,
        cells: results,
    })
}

fn validate(
    config: &SourceAreaConfig,
    cells: &[SourceAreaCell],
    sst: Option<&GriddedField>,
) -> Result<(), SourceAreaError> {
    let unique_cell_ids = cells
        .iter()
        .map(|cell| cell.id.as_str())
        .collect::<HashSet<_>>();
    let unique_family_ids = config
        .motion_families
        .iter()
        .map(|family| family.id.as_str())
        .collect::<HashSet<_>>();
    let events = config
        .motion_families
        .iter()
        .flat_map(|family| &family.debris.events)
        .collect::<Vec<_>>();
    let object_ids = events
        .iter()
        .flat_map(|event| event.object_ids.iter().map(String::as_str))
        .collect::<Vec<_>>();
    let flaperon_count = config
        .motion_families
        .iter()
        .flat_map(|family| &family.debris.events)
        .filter(|event| event.is_flaperon)
        .count();
    let invalid_family = config.motion_families.iter().any(|family| {
        let event_ids = family
            .debris
            .events
            .iter()
            .map(|event| event.id.as_str())
            .collect::<HashSet<_>>();
        family.id.trim().is_empty()
            || family.motion.validate().is_err()
            || family.debris.validate().is_err()
            || event_ids.len() != family.debris.events.len()
            || family
                .debris
                .events
                .iter()
                .any(|event| event.discovery_end_unix_seconds <= config.release_unix_seconds)
            || family.debris.non_recoveries.iter().any(|observation| {
                observation.observation_end_unix_seconds <= config.release_unix_seconds
            })
    });
    let inconsistent_shared_episode = events.iter().enumerate().any(|(index, first)| {
        events.iter().skip(index + 1).any(|second| {
            first.id == second.id
                && (first.location != second.location
                    || first.position != second.position
                    || first.discovery_start_unix_seconds != second.discovery_start_unix_seconds
                    || first.discovery_end_unix_seconds != second.discovery_end_unix_seconds
                    || first.discovery_delay != second.discovery_delay
                    || first.evidence_weight != second.evidence_weight
                    || first.is_flaperon != second.is_flaperon)
        })
    });
    if config.family.trim().is_empty()
        || config.particles_per_cell == 0
        || !config.release_unix_seconds.is_finite()
        || cells.is_empty()
        || unique_cell_ids.len() != cells.len()
        || cells.iter().any(|cell| {
            cell.id.trim().is_empty() || !cell.prior_weight.is_finite() || cell.prior_weight <= 0.0
        })
        || config.motion_families.is_empty()
        || unique_family_ids.len() != config.motion_families.len()
        || object_ids.iter().copied().collect::<HashSet<_>>().len() != object_ids.len()
        || inconsistent_shared_episode
        || invalid_family
        || config.sampling.validate().is_err()
        || config
            .isotope
            .as_ref()
            .is_some_and(|model| model.validate().is_err() || sst.is_none() || flaperon_count != 1)
    {
        return Err(SourceAreaError::InvalidConfiguration);
    }
    Ok(())
}

fn evaluate_cell(
    config: &SourceAreaConfig,
    cell: &SourceAreaCell,
    environment: DriftEnvironment<'_>,
    sst: Option<&GriddedField>,
) -> Result<SourceCellResult, SourceAreaError> {
    let cell_seed = stable_key(&cell.id);
    let mut family_results = Vec::with_capacity(config.motion_families.len());
    let mut recovery_groups = BTreeMap::<String, Vec<RecoveryEvaluation>>::new();
    let mut all_non_recoveries = Vec::new();
    let mut aggregate_termination_counts = BTreeMap::new();
    let mut aggregate_termination_weights = BTreeMap::new();
    let mut aggregate_importance_weight = 0.0;
    let mut aggregate_proposal_terminated = 0usize;
    let mut aggregate_path_count = 0usize;
    let mut debris_log_compatibility = 0.0;
    let mut isotope = None;
    let mut isotope_log_compatibility = None;
    let mut status = SourceCellStatus::Supported;
    let mut headline_sampling = None;

    for family in &config.motion_families {
        let object_count = family
            .debris
            .events
            .iter()
            .map(|event| event.object_ids.len().max(1))
            .sum::<usize>();
        let mut family_recoveries = Vec::with_capacity(family.debris.events.len());
        let mut recovery_ensembles = Vec::with_capacity(family.debris.events.len());
        let mut family_non_recovery = BTreeMap::<String, NonRecoveryAccumulator>::new();
        let mut family_termination_reasons = BTreeMap::new();
        let mut family_termination_weights = BTreeMap::new();
        let mut family_importance_weight = 0.0;
        let mut family_proposal_terminated = 0usize;
        let mut family_path_count = 0usize;
        let mut family_debris_log_compatibility = 0.0;
        let mut family_sampling = None;

        if family.debris.events.is_empty() {
            let end_time = family
                .debris
                .non_recoveries
                .iter()
                .map(|observation| observation.observation_end_unix_seconds)
                .fold(config.release_unix_seconds, f64::max);
            let (paths, sampling) = simulate_ensemble(EnsembleRequest {
                environment,
                start: cell.position,
                start_unix_seconds: config.release_unix_seconds,
                end_unix_seconds: end_time,
                motion: family.motion,
                recoveries: &[],
                recovery_pre_discovery_window_days: family.debris.pre_discovery_window_days,
                sampling: ArrivalSamplingConfig::default(),
                particles: config.particles_per_cell,
                base_seed: config.seed,
                stream_key: cell_seed
                    ^ stable_key(&family.id)
                    ^ stable_key("non-recovery-population"),
            })
            .map_err(|error| SourceAreaError::Cell(cell.id.clone(), error.to_string()))?;
            let termination = summarize_terminations(&paths);
            for (reason, count) in &termination.reasons {
                *family_termination_reasons.entry(*reason).or_insert(0) += *count;
                *aggregate_termination_counts.entry(*reason).or_insert(0) += *count;
            }
            for (reason, weight) in &termination.weights {
                *family_termination_weights.entry(*reason).or_insert(0.0) += *weight;
                *aggregate_termination_weights.entry(*reason).or_insert(0.0) += *weight;
            }
            family_importance_weight += termination.total_importance_weight;
            aggregate_importance_weight += termination.total_importance_weight;
            family_proposal_terminated += termination.proposal_terminated;
            aggregate_proposal_terminated += termination.proposal_terminated;
            family_path_count += paths.len();
            aggregate_path_count += paths.len();

            let evaluation = family
                .debris
                .evaluate(&paths)
                .map_err(|error| SourceAreaError::Cell(cell.id.clone(), error.to_string()))?;
            family_debris_log_compatibility += evaluation.log_compatibility;
            for observation in evaluation.non_recoveries {
                family_non_recovery
                    .entry(observation.observation_id.clone())
                    .or_default()
                    .add(1.0, observation);
            }
            family_sampling = Some(sampling.clone());
            if headline_sampling.is_none() {
                headline_sampling = Some(sampling);
            }
        }

        for event in &family.debris.events {
            let event_object_fraction = event.object_ids.len().max(1) as f64 / object_count as f64;
            let mut event_evidence = family.debris.clone();
            event_evidence.events = vec![event.clone()];
            event_evidence.non_recoveries = family
                .debris
                .non_recoveries
                .iter()
                .cloned()
                .map(|mut observation| {
                    observation.expected_reportable_items *= event_object_fraction;
                    observation
                })
                .collect();
            let end_time = event_end_time(config, family, event);
            let (paths, sampling) = simulate_ensemble(EnsembleRequest {
                environment,
                start: cell.position,
                start_unix_seconds: config.release_unix_seconds,
                end_unix_seconds: end_time,
                motion: family.motion,
                recoveries: std::slice::from_ref(event),
                recovery_pre_discovery_window_days: family.debris.pre_discovery_window_days,
                sampling: config.sampling,
                particles: config.particles_per_cell,
                base_seed: config.seed,
                stream_key: cell_seed ^ stable_key(&family.id) ^ stable_key(&event.id),
            })
            .map_err(|error| SourceAreaError::Cell(cell.id.clone(), error.to_string()))?;

            let termination = summarize_terminations(&paths);
            for (reason, count) in &termination.reasons {
                *family_termination_reasons.entry(*reason).or_insert(0) += *count;
                *aggregate_termination_counts.entry(*reason).or_insert(0) += *count;
            }
            for (reason, weight) in &termination.weights {
                *family_termination_weights.entry(*reason).or_insert(0.0) += *weight;
                *aggregate_termination_weights.entry(*reason).or_insert(0.0) += *weight;
            }
            recovery_ensembles.push(RecoveryEnsembleEvaluation {
                event_id: event.id.clone(),
                terminated_fraction: termination.fractions.values().sum(),
                proposal_terminated_fraction: termination.proposal_terminated as f64
                    / paths.len() as f64,
                termination_reasons: termination.reasons,
                termination_reason_fractions: termination.fractions,
                sampling: sampling.clone(),
            });
            family_importance_weight += termination.total_importance_weight;
            aggregate_importance_weight += termination.total_importance_weight;
            family_proposal_terminated += termination.proposal_terminated;
            aggregate_proposal_terminated += termination.proposal_terminated;
            family_path_count += paths.len();
            aggregate_path_count += paths.len();

            let evaluation = event_evidence
                .evaluate(&paths)
                .map_err(|error| SourceAreaError::Cell(cell.id.clone(), error.to_string()))?;
            family_debris_log_compatibility += evaluation.log_compatibility;
            let recovery = evaluation
                .recoveries
                .into_iter()
                .next()
                .expect("one configured recovery produces one evaluation");
            recovery_groups
                .entry(recovery.event_id.clone())
                .or_default()
                .push(recovery.clone());
            family_recoveries.push(recovery);
            for observation in evaluation.non_recoveries {
                family_non_recovery
                    .entry(observation.observation_id.clone())
                    .or_default()
                    .add(event_object_fraction, observation);
            }

            if event.is_flaperon {
                headline_sampling = Some(sampling.clone());
                if let Some(model) = &config.isotope {
                    let arrival =
                        event_evidence
                            .flaperon_arrival_weights(&paths)
                            .map_err(|error| {
                                SourceAreaError::Cell(cell.id.clone(), error.to_string())
                            })?;
                    match model.evaluate_conditional(&paths, &arrival, sst.expect("validated SST"))
                    {
                        Ok(evaluation) => {
                            isotope_log_compatibility =
                                Some(evaluation.conditional_log_compatibility);
                            isotope = Some(evaluation);
                        }
                        Err(IsotopeError::NoArrivalSupport) => {
                            status = SourceCellStatus::NoFlaperonArrival;
                        }
                        Err(error) => {
                            return Err(SourceAreaError::Cell(cell.id.clone(), error.to_string()));
                        }
                    }
                }
            }
            if family_sampling.is_none() {
                family_sampling = Some(sampling.clone());
            }
            if headline_sampling.is_none() {
                headline_sampling = Some(sampling);
            }
        }

        let family_non_recoveries = family_non_recovery
            .into_values()
            .map(NonRecoveryAccumulator::finish)
            .collect::<Vec<_>>();
        debris_log_compatibility += family_non_recoveries
            .iter()
            .map(|observation| observation.log_compatibility)
            .sum::<f64>();
        all_non_recoveries.extend(family_non_recoveries.iter().cloned());
        let family_termination_reason_fractions = family_termination_weights
            .into_iter()
            .map(|(reason, weight)| (reason, weight / family_importance_weight))
            .collect::<BTreeMap<_, _>>();
        family_results.push(MotionFamilyEvaluation {
            id: family.id.clone(),
            debris_log_compatibility: family_debris_log_compatibility,
            terminated_fraction: family_termination_reason_fractions.values().sum(),
            proposal_terminated_fraction: family_proposal_terminated as f64
                / family_path_count as f64,
            termination_reasons: family_termination_reasons,
            termination_reason_fractions: family_termination_reason_fractions,
            sampling: family_sampling.unwrap_or_default(),
            recovery_ensembles,
            recoveries: family_recoveries,
            non_recoveries: family_non_recoveries,
        });
    }

    // A co-recovery episode is one likelihood factor even when its objects
    // require different motion laws. Using the least-suppressive compatible
    // motion family is a conservative profile over those defensible laws; it
    // is not a subjective weighted mixture and cannot create a positive boost.
    let all_recoveries = profile_recovery_episodes(recovery_groups);
    debris_log_compatibility += all_recoveries
        .iter()
        .map(|recovery| recovery.log_compatibility)
        .sum::<f64>();

    let termination_reason_fractions = aggregate_termination_weights
        .into_iter()
        .map(|(reason, weight)| (reason, weight / aggregate_importance_weight))
        .collect::<BTreeMap<_, _>>();
    let terminated_fraction = termination_reason_fractions.values().sum::<f64>();
    let proposal_terminated_fraction =
        aggregate_proposal_terminated as f64 / aggregate_path_count as f64;
    let combined_log_weight = Some(
        cell.prior_weight.ln()
            + debris_log_compatibility
            + isotope_log_compatibility.unwrap_or(0.0),
    );
    Ok(SourceCellResult {
        id: cell.id.clone(),
        position: cell.position,
        prior_weight: cell.prior_weight,
        debris_log_compatibility,
        conditional_isotope_log_compatibility: isotope_log_compatibility,
        combined_log_weight,
        normalized_weight: 0.0,
        terminated_fraction,
        proposal_terminated_fraction,
        termination_reasons: aggregate_termination_counts,
        termination_reason_fractions,
        sampling: headline_sampling.unwrap_or_default(),
        status,
        recoveries: all_recoveries,
        non_recoveries: all_non_recoveries,
        motion_families: family_results,
        isotope,
    })
}

struct EnsembleTerminationSummary {
    total_importance_weight: f64,
    proposal_terminated: usize,
    reasons: BTreeMap<PathTerminationReason, usize>,
    weights: BTreeMap<PathTerminationReason, f64>,
    fractions: BTreeMap<PathTerminationReason, f64>,
}

fn summarize_terminations(paths: &[DriftPath]) -> EnsembleTerminationSummary {
    let total_importance_weight = paths.iter().map(DriftPath::importance_weight).sum::<f64>();
    let mut reasons = BTreeMap::new();
    let mut weights = BTreeMap::new();
    for path in paths {
        if let Some(termination) = path.termination.as_ref() {
            *reasons.entry(termination.reason).or_insert(0) += 1;
            *weights.entry(termination.reason).or_insert(0.0) += path.importance_weight();
        }
    }
    let proposal_terminated = reasons.values().sum();
    let fractions = weights
        .iter()
        .map(|(reason, weight)| (*reason, *weight / total_importance_weight))
        .collect();
    EnsembleTerminationSummary {
        total_importance_weight,
        proposal_terminated,
        reasons,
        weights,
        fractions,
    }
}

#[derive(Default)]
struct NonRecoveryAccumulator {
    observation_id: String,
    estimated_landfall_probability: f64,
    unresolved_path_probability: f64,
    conservative_scoring_probability: f64,
    log_compatibility: f64,
    effective_sample_size_denominator: f64,
}

impl NonRecoveryAccumulator {
    fn add(&mut self, fraction: f64, evaluation: NonRecoveryEvaluation) {
        if self.observation_id.is_empty() {
            self.observation_id.clone_from(&evaluation.observation_id);
        }
        self.estimated_landfall_probability += fraction * evaluation.estimated_landfall_probability;
        self.unresolved_path_probability += fraction * evaluation.unresolved_path_probability;
        self.conservative_scoring_probability +=
            fraction * evaluation.conservative_scoring_probability;
        self.log_compatibility += evaluation.log_compatibility;
        if evaluation.effective_sample_size > 0.0 {
            self.effective_sample_size_denominator += fraction.powi(2)
                * evaluation.conservative_scoring_probability.powi(2)
                / evaluation.effective_sample_size;
        }
    }

    fn finish(self) -> NonRecoveryEvaluation {
        let effective_sample_size = if self.effective_sample_size_denominator > 0.0 {
            self.conservative_scoring_probability.powi(2) / self.effective_sample_size_denominator
        } else {
            0.0
        };
        NonRecoveryEvaluation {
            observation_id: self.observation_id,
            estimated_landfall_probability: self.estimated_landfall_probability,
            unresolved_path_probability: self.unresolved_path_probability,
            conservative_scoring_probability: self.conservative_scoring_probability,
            effective_sample_size,
            log_compatibility: self.log_compatibility,
        }
    }
}

fn profile_recovery_episodes(
    groups: BTreeMap<String, Vec<RecoveryEvaluation>>,
) -> Vec<RecoveryEvaluation> {
    groups
        .into_values()
        .map(|evaluations| {
            let mut chosen = evaluations
                .iter()
                .max_by(|first, second| {
                    first.log_compatibility.total_cmp(&second.log_compatibility)
                })
                .expect("recovery group is non-empty")
                .clone();
            chosen.object_count = evaluations
                .iter()
                .map(|evaluation| evaluation.object_count)
                .sum();
            chosen.is_flaperon = evaluations.iter().any(|evaluation| evaluation.is_flaperon);
            chosen
        })
        .collect()
}

fn event_end_time(
    config: &SourceAreaConfig,
    family: &DebrisMotionFamily,
    event: &RecoveryEvent,
) -> f64 {
    let recovery_end = std::iter::once(event.discovery_end_unix_seconds).chain(
        family
            .debris
            .non_recoveries
            .iter()
            .map(|observation| observation.observation_end_unix_seconds),
    );
    let isotope_end = config
        .isotope
        .iter()
        .filter(|_| event.is_flaperon)
        .flat_map(|model| model.chronologies.iter().map(|item| item.end_unix_seconds));
    recovery_end
        .chain(isotope_end)
        .fold(config.release_unix_seconds, f64::max)
}

fn stable_key(identifier: &str) -> u64 {
    identifier
        .bytes()
        .fold(0xcbf2_9ce4_8422_2325, |hash, byte| {
            (hash ^ u64::from(byte)).wrapping_mul(0x0000_0100_0000_01b3)
        })
}

#[cfg(test)]
mod tests {
    use super::{profile_recovery_episodes, stable_key};
    use crate::RecoveryEvaluation;
    use std::collections::BTreeMap;

    #[test]
    fn deterministic_stream_keys_are_distinct_and_order_independent() {
        let cell = stable_key("arc-south-35");
        assert_eq!(cell, stable_key("arc-south-35"));
        assert_ne!(cell, stable_key("arc-south-36"));
    }

    #[test]
    fn shared_episode_profiles_motion_laws_without_multiplying_them() {
        let evaluation = |log_compatibility: f64, object_count: usize| RecoveryEvaluation {
            event_id: "shared-recovery".to_string(),
            object_count,
            is_flaperon: false,
            mean_encounter_weight: log_compatibility.exp(),
            effective_sample_size: 100.0,
            evidence_weight: 1.0,
            log_compatibility,
        };
        let profiled = profile_recovery_episodes(BTreeMap::from([(
            "shared-recovery".to_string(),
            vec![evaluation(-4.0, 1), evaluation(-1.0, 2)],
        )]));
        assert_eq!(profiled.len(), 1);
        assert_eq!(profiled[0].object_count, 3);
        assert_eq!(profiled[0].log_compatibility, -1.0);
    }
}
