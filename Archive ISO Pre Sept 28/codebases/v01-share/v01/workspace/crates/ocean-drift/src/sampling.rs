use std::collections::HashSet;

use mh370_domain::{great_circle_distance_nm, LatLon};
use rand::Rng;
use rand_chacha::{rand_core::SeedableRng, ChaCha8Rng};
use serde::{Deserialize, Serialize};

use crate::{
    transport::{advance_state, finish_state, initialize_state, DriftState},
    DriftEnvironment, DriftPath, MotionConfig, RecoveryEvent, TransportError,
};

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum ArrivalSamplingMethod {
    Independent,
    AdaptiveSmc,
}

#[derive(Debug, Clone, Copy, PartialEq, Serialize, Deserialize)]
pub struct ArrivalSamplingConfig {
    pub method: ArrivalSamplingMethod,
    /// Interval between adaptive resampling events.
    pub resampling_interval_days: f64,
    /// Maximum log proposal preference from the farthest to nearest live path.
    /// Correction weights remove this proposal preference from estimates.
    pub selection_strength: f64,
    /// Resampling begins this many days before the flaperon discovery anchor.
    pub start_days_before_recovery: f64,
}

impl Default for ArrivalSamplingConfig {
    fn default() -> Self {
        Self {
            method: ArrivalSamplingMethod::Independent,
            resampling_interval_days: 30.0,
            selection_strength: 0.0,
            start_days_before_recovery: 0.0,
        }
    }
}

impl ArrivalSamplingConfig {
    pub fn validate(&self) -> Result<(), TransportError> {
        let valid_common = self.resampling_interval_days.is_finite()
            && self.resampling_interval_days > 0.0
            && self.selection_strength.is_finite()
            && self.selection_strength >= 0.0
            && self.start_days_before_recovery.is_finite()
            && self.start_days_before_recovery >= 0.0;
        let valid_method = match self.method {
            ArrivalSamplingMethod::Independent => self.selection_strength == 0.0,
            ArrivalSamplingMethod::AdaptiveSmc => {
                self.selection_strength > 0.0 && self.start_days_before_recovery > 0.0
            }
        };
        if valid_common && valid_method {
            Ok(())
        } else {
            Err(TransportError::InvalidConfiguration)
        }
    }
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct SamplingDiagnostics {
    pub method: ArrivalSamplingMethod,
    pub resampling_events: usize,
    pub propagated_segments: usize,
    pub represented_initial_ancestors: usize,
    pub mean_correction_weight: f64,
    pub correction_weight_effective_sample_size: f64,
    pub minimum_log_correction_weight: f64,
    pub maximum_log_correction_weight: f64,
    pub minimum_proposal_probability: f64,
    pub maximum_proposal_probability: f64,
    /// Per-resampling proposal and correction summaries. Keyed streams plus
    /// these summaries make the adaptive proposal auditable without storing
    /// every long trajectory in the source-area artifact.
    #[serde(default)]
    pub events: Vec<SamplingEventDiagnostics>,
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct SamplingEventDiagnostics {
    pub checkpoint_unix_seconds: f64,
    pub live_particles_before_resampling: usize,
    pub distinct_selected_ancestors: usize,
    /// Minimum, 25th, 50th, 75th, and maximum proposal probabilities.
    pub proposal_probability_quantiles: [f64; 5],
    /// Minimum, 25th, 50th, 75th, and maximum drawn log correction weights.
    pub log_correction_weight_quantiles: [f64; 5],
    pub mean_correction_weight: f64,
    pub correction_weight_effective_sample_size: f64,
}

impl Default for SamplingDiagnostics {
    fn default() -> Self {
        Self {
            method: ArrivalSamplingMethod::Independent,
            resampling_events: 0,
            propagated_segments: 0,
            represented_initial_ancestors: 0,
            mean_correction_weight: 1.0,
            correction_weight_effective_sample_size: 0.0,
            minimum_log_correction_weight: 0.0,
            maximum_log_correction_weight: 0.0,
            minimum_proposal_probability: 0.0,
            maximum_proposal_probability: 0.0,
            events: Vec::new(),
        }
    }
}

#[derive(Clone)]
struct Particle {
    state: DriftState,
    initial_ancestor: usize,
}

pub(crate) struct EnsembleRequest<'a> {
    pub environment: DriftEnvironment<'a>,
    pub start: LatLon,
    pub start_unix_seconds: f64,
    pub end_unix_seconds: f64,
    pub motion: MotionConfig,
    /// Recovery targets represented by this object-motion family. Adaptive
    /// selection ranks proximity to the union; correction weights retain the
    /// physical-law estimate for each event separately.
    pub recoveries: &'a [RecoveryEvent],
    /// Legacy arrival-to-discovery support used only when an event has no
    /// explicit delay bins. The likelihood itself remains owned by the
    /// observation model.
    pub recovery_pre_discovery_window_days: f64,
    pub sampling: ArrivalSamplingConfig,
    pub particles: usize,
    pub base_seed: u64,
    pub stream_key: u64,
}

pub(crate) fn simulate_ensemble(
    request: EnsembleRequest<'_>,
) -> Result<(Vec<DriftPath>, SamplingDiagnostics), TransportError> {
    request.sampling.validate()?;
    request.motion.validate()?;
    if request.particles == 0
        || request.end_unix_seconds <= request.start_unix_seconds
        || (request.sampling.method == ArrivalSamplingMethod::AdaptiveSmc
            && request.recoveries.is_empty())
        || !request.recovery_pre_discovery_window_days.is_finite()
        || request.recovery_pre_discovery_window_days <= 0.0
        || request
            .recoveries
            .iter()
            .any(|event| event.discovery_end_unix_seconds <= request.start_unix_seconds)
    {
        return Err(TransportError::InvalidConfiguration);
    }

    let mut particles = (0..request.particles)
        .map(|index| {
            let mut rng = ChaCha8Rng::seed_from_u64(keyed_seed(
                request.base_seed,
                request.stream_key,
                0,
                index as u64,
            ));
            Particle {
                state: initialize_state(
                    request.start,
                    request.start_unix_seconds,
                    request.motion,
                    &mut rng,
                ),
                initial_ancestor: index,
            }
        })
        .collect::<Vec<_>>();

    let first_recovery = request
        .recoveries
        .iter()
        .map(|event| event.discovery_end_unix_seconds)
        .fold(request.end_unix_seconds, f64::min);
    let last_recovery = request
        .recoveries
        .iter()
        .map(|event| event.discovery_end_unix_seconds)
        .fold(request.start_unix_seconds, f64::max);
    let checkpoints = checkpoints(
        request.start_unix_seconds,
        request.end_unix_seconds,
        first_recovery,
        last_recovery,
        request.sampling,
    );
    let mut segment_start = request.start_unix_seconds;
    let mut minimum_proposal_probability = 1.0 / request.particles as f64;
    let mut maximum_proposal_probability = minimum_proposal_probability;
    let mut event_diagnostics = Vec::with_capacity(checkpoints.len());

    for (generation, checkpoint) in checkpoints.iter().copied().enumerate() {
        if checkpoint <= segment_start {
            continue;
        }
        propagate(
            &mut particles,
            request.environment,
            checkpoint,
            request.motion,
            request.base_seed,
            request.stream_key,
            generation as u64 + 1,
        )?;
        let log_selection = selection_log_potentials(
            &particles,
            request.recoveries,
            checkpoint,
            request.recovery_pre_discovery_window_days,
            request.sampling.selection_strength,
        );
        let log_weights = particles
            .iter()
            .map(|particle| particle.state.log_importance_weight)
            .collect::<Vec<_>>();
        let mut rng = ChaCha8Rng::seed_from_u64(keyed_seed(
            request.base_seed,
            request.stream_key,
            u64::MAX - generation as u64,
            0,
        ));
        let draw = resample_indices(&log_weights, &log_selection, &mut rng);
        minimum_proposal_probability = minimum_proposal_probability.min(draw.minimum_probability);
        maximum_proposal_probability = maximum_proposal_probability.max(draw.maximum_probability);
        let correction_weights = draw
            .log_correction_weights
            .iter()
            .map(|value| value.exp())
            .collect::<Vec<_>>();
        event_diagnostics.push(SamplingEventDiagnostics {
            checkpoint_unix_seconds: checkpoint,
            live_particles_before_resampling: particles
                .iter()
                .filter(|particle| !particle.state.is_terminated())
                .count(),
            distinct_selected_ancestors: draw.indices.iter().copied().collect::<HashSet<_>>().len(),
            proposal_probability_quantiles: draw.probability_quantiles,
            log_correction_weight_quantiles: quantiles(&draw.log_correction_weights),
            mean_correction_weight: correction_weights.iter().sum::<f64>()
                / correction_weights.len() as f64,
            correction_weight_effective_sample_size: effective_sample_size(&correction_weights),
        });
        particles = draw
            .indices
            .into_iter()
            .zip(draw.log_correction_weights)
            .map(|(ancestor, log_weight)| {
                let mut clone = particles[ancestor].clone();
                clone.state.log_importance_weight = log_weight;
                clone
            })
            .collect();
        segment_start = checkpoint;
    }

    if request.end_unix_seconds > segment_start {
        propagate(
            &mut particles,
            request.environment,
            request.end_unix_seconds,
            request.motion,
            request.base_seed,
            request.stream_key,
            checkpoints.len() as u64 + 1,
        )?;
    }

    let represented_initial_ancestors = particles
        .iter()
        .map(|particle| particle.initial_ancestor)
        .collect::<HashSet<_>>()
        .len();
    let log_weights = particles
        .iter()
        .map(|particle| particle.state.log_importance_weight)
        .collect::<Vec<_>>();
    let weights = log_weights
        .iter()
        .map(|value| value.exp())
        .collect::<Vec<_>>();
    let diagnostics = SamplingDiagnostics {
        method: request.sampling.method,
        resampling_events: checkpoints.len(),
        propagated_segments: request.particles * (checkpoints.len() + 1),
        represented_initial_ancestors,
        mean_correction_weight: weights.iter().sum::<f64>() / weights.len() as f64,
        correction_weight_effective_sample_size: effective_sample_size(&weights),
        minimum_log_correction_weight: log_weights.iter().copied().fold(f64::INFINITY, f64::min),
        maximum_log_correction_weight: log_weights
            .iter()
            .copied()
            .fold(f64::NEG_INFINITY, f64::max),
        minimum_proposal_probability,
        maximum_proposal_probability,
        events: event_diagnostics,
    };
    Ok((
        particles
            .into_iter()
            .map(|particle| finish_state(particle.state))
            .collect(),
        diagnostics,
    ))
}

fn checkpoints(
    start: f64,
    end: f64,
    first_recovery_end: f64,
    last_recovery_end: f64,
    config: ArrivalSamplingConfig,
) -> Vec<f64> {
    if config.method == ArrivalSamplingMethod::Independent {
        return Vec::new();
    }
    let interval = config.resampling_interval_days * 86_400.0;
    let mut next = (first_recovery_end - config.start_days_before_recovery * 86_400.0).max(start);
    let adaptive_end = end.min(last_recovery_end);
    let mut result = Vec::new();
    while next < adaptive_end - 1e-6 {
        if next > start + 1e-6 {
            result.push(next);
        }
        next += interval;
    }
    result
}

#[allow(clippy::too_many_arguments)]
fn propagate(
    particles: &mut [Particle],
    environment: DriftEnvironment<'_>,
    end: f64,
    motion: MotionConfig,
    base_seed: u64,
    stream_key: u64,
    generation: u64,
) -> Result<(), TransportError> {
    for (index, particle) in particles.iter_mut().enumerate() {
        let mut rng =
            ChaCha8Rng::seed_from_u64(keyed_seed(base_seed, stream_key, generation, index as u64));
        advance_state(environment, &mut particle.state, end, motion, &mut rng)?;
    }
    Ok(())
}

fn selection_log_potentials(
    particles: &[Particle],
    targets: &[RecoveryEvent],
    checkpoint: f64,
    legacy_delay_days: f64,
    strength: f64,
) -> Vec<f64> {
    let mut ranked = particles
        .iter()
        .enumerate()
        .map(|(index, particle)| {
            let distance = targets
                .iter()
                .map(|target| {
                    let (minimum_delay_days, maximum_delay_days) =
                        if target.discovery_delay.is_empty() {
                            (0.0, legacy_delay_days)
                        } else {
                            (
                                target
                                    .discovery_delay
                                    .iter()
                                    .map(|bin| bin.start_days)
                                    .fold(f64::INFINITY, f64::min),
                                target
                                    .discovery_delay
                                    .iter()
                                    .map(|bin| bin.end_days)
                                    .fold(f64::NEG_INFINITY, f64::max),
                            )
                        };
                    let earliest_arrival =
                        target.discovery_start_unix_seconds - maximum_delay_days * 86_400.0;
                    let latest_arrival =
                        target.discovery_end_unix_seconds - minimum_delay_days * 86_400.0;
                    let historical = particle
                        .state
                        .points()
                        .iter()
                        .filter(|point| {
                            point.unix_seconds >= earliest_arrival
                                && point.unix_seconds <= latest_arrival
                        })
                        .map(|point| great_circle_distance_nm(point.position, target.position).0)
                        .fold(f64::INFINITY, f64::min);
                    let continuable =
                        if !particle.state.is_terminated() && checkpoint <= latest_arrival {
                            particle
                                .state
                                .points()
                                .last()
                                .map(|point| {
                                    great_circle_distance_nm(point.position, target.position).0
                                })
                                .unwrap_or(f64::INFINITY)
                        } else {
                            f64::INFINITY
                        };
                    historical.min(continuable)
                })
                .fold(f64::INFINITY, f64::min);
            (index, distance)
        })
        .collect::<Vec<_>>();
    ranked.sort_by(|first, second| {
        first
            .1
            .total_cmp(&second.1)
            .then_with(|| first.0.cmp(&second.0))
    });
    let denominator = particles.len().saturating_sub(1).max(1) as f64;
    let mut result = vec![0.0; particles.len()];
    for (rank, (index, _)) in ranked.into_iter().enumerate() {
        result[index] = -strength * rank as f64 / denominator;
    }
    result
}

struct ResamplingDraw {
    indices: Vec<usize>,
    log_correction_weights: Vec<f64>,
    minimum_probability: f64,
    maximum_probability: f64,
    probability_quantiles: [f64; 5],
}

fn resample_indices<R: Rng + ?Sized>(
    log_weights: &[f64],
    log_selection: &[f64],
    rng: &mut R,
) -> ResamplingDraw {
    let count = log_weights.len();
    let proposal_logs = log_weights
        .iter()
        .zip(log_selection)
        .map(|(weight, selection)| weight + selection)
        .collect::<Vec<_>>();
    let normalizer = logsumexp(&proposal_logs);
    let probabilities = proposal_logs
        .iter()
        .map(|value| (value - normalizer).exp())
        .collect::<Vec<_>>();
    let cumulative = probabilities
        .iter()
        .scan(0.0, |total, value| {
            *total += value;
            Some(*total)
        })
        .collect::<Vec<_>>();
    let mut indices = Vec::with_capacity(count);
    let mut correction = Vec::with_capacity(count);
    // Stratification preserves the exact marginal proposal and correction
    // weights while reducing multinomial duplication at every splitting
    // level. Each keyed stream still generates a deterministic draw.
    for stratum in 0..count {
        let uniform = (stratum as f64 + rng.gen::<f64>()) / count as f64;
        let ancestor = cumulative
            .partition_point(|value| *value <= uniform)
            .min(count - 1);
        indices.push(ancestor);
        correction.push(log_weights[ancestor] - (count as f64).ln() - probabilities[ancestor].ln());
    }
    ResamplingDraw {
        indices,
        log_correction_weights: correction,
        minimum_probability: probabilities.iter().copied().fold(f64::INFINITY, f64::min),
        maximum_probability: probabilities
            .iter()
            .copied()
            .fold(f64::NEG_INFINITY, f64::max),
        probability_quantiles: quantiles(&probabilities),
    }
}

fn quantiles(values: &[f64]) -> [f64; 5] {
    let mut ordered = values.to_vec();
    ordered.sort_by(f64::total_cmp);
    let at = |probability: f64| {
        let index = (probability * ordered.len().saturating_sub(1) as f64).round() as usize;
        ordered[index]
    };
    [at(0.0), at(0.25), at(0.5), at(0.75), at(1.0)]
}

fn logsumexp(values: &[f64]) -> f64 {
    let maximum = values.iter().copied().fold(f64::NEG_INFINITY, f64::max);
    maximum
        + values
            .iter()
            .map(|value| (value - maximum).exp())
            .sum::<f64>()
            .ln()
}

fn effective_sample_size(weights: &[f64]) -> f64 {
    let sum = weights.iter().sum::<f64>();
    let squares = weights.iter().map(|weight| weight * weight).sum::<f64>();
    if squares > 0.0 {
        sum * sum / squares
    } else {
        0.0
    }
}

fn keyed_seed(base: u64, stream: u64, generation: u64, particle: u64) -> u64 {
    let mut value = base ^ stream.wrapping_mul(0x9E37_79B9_7F4A_7C15);
    value ^= generation.wrapping_mul(0xA076_1D64_78BD_642F);
    value ^= particle.wrapping_mul(0xD1B5_4A32_D192_ED03);
    value ^= value >> 30;
    value = value.wrapping_mul(0xBF58_476D_1CE4_E5B9);
    value ^= value >> 27;
    value.wrapping_mul(0x94D0_49BB_1331_11EB) ^ (value >> 31)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn correction_weights_make_rank_biased_resampling_unbiased() {
        let values = [0.0, 0.0, 1.0, 1.0];
        let log_weights = [0.0; 4];
        let log_selection = [-3.0, -3.0, 0.0, 0.0];
        let mut total = 0.0;
        let replications = 20_000;
        for seed in 0..replications {
            let mut rng = ChaCha8Rng::seed_from_u64(seed as u64);
            let draw = resample_indices(&log_weights, &log_selection, &mut rng);
            let estimate = draw
                .indices
                .iter()
                .zip(&draw.log_correction_weights)
                .map(|(index, weight)| values[*index] * weight.exp())
                .sum::<f64>()
                / values.len() as f64;
            total += estimate;
        }
        let average = total / replications as f64;
        assert!((average - 0.5).abs() < 0.01, "average={average}");
    }

    #[test]
    fn correction_weights_remain_unbiased_through_multiple_synthetic_levels() {
        let initial_values = [0.0, 0.25, 0.75, 1.0];
        let replications = 20_000;
        let mut total = 0.0;
        for seed in 0..replications {
            let mut values = initial_values.to_vec();
            let mut log_weights = vec![0.0; values.len()];
            let mut rng = ChaCha8Rng::seed_from_u64(seed as u64);
            for strength in [1.0, 2.0, 3.0] {
                let log_selection = values
                    .iter()
                    .map(|value| strength * value)
                    .collect::<Vec<_>>();
                let draw = resample_indices(&log_weights, &log_selection, &mut rng);
                values = draw.indices.iter().map(|index| values[*index]).collect();
                log_weights = draw.log_correction_weights;
            }
            total += values
                .iter()
                .zip(&log_weights)
                .map(|(value, weight)| value * weight.exp())
                .sum::<f64>()
                / values.len() as f64;
        }
        let estimate = total / replications as f64;
        assert!((estimate - 0.5).abs() < 0.015, "estimate={estimate}");
    }

    #[test]
    fn independent_configuration_has_no_checkpoints() {
        assert!(checkpoints(0.0, 100.0, 50.0, 100.0, ArrivalSamplingConfig::default()).is_empty());
    }

    #[test]
    fn adaptive_checkpoints_stop_at_last_recovery_not_later_non_recovery() {
        let day = 86_400.0;
        let checkpoints = checkpoints(
            0.0,
            100.0 * day,
            50.0 * day,
            70.0 * day,
            ArrivalSamplingConfig {
                method: ArrivalSamplingMethod::AdaptiveSmc,
                resampling_interval_days: 10.0,
                selection_strength: 2.0,
                start_days_before_recovery: 40.0,
            },
        );
        assert_eq!(checkpoints.first(), Some(&(10.0 * day)));
        assert_eq!(checkpoints.last(), Some(&(60.0 * day)));
    }
}
