use rand::Rng;
use rand_chacha::ChaCha8Rng;
use rayon::prelude::*;
use serde::{Deserialize, Serialize};
use thiserror::Error;

use crate::{effective_sample_size, normalize_log_weights, rng_for, systematic_resample, SmcError};

#[derive(Debug, Clone)]
pub struct Mutation<S> {
    pub state: S,
    /// log q(current | proposed) - log q(proposed | current).
    pub log_reverse_over_forward: f64,
}

impl<S> Mutation<S> {
    pub fn symmetric(state: S) -> Self {
        Self {
            state,
            log_reverse_over_forward: 0.0,
        }
    }
}

pub trait StaticModel: Sync {
    type State: Clone + Send + Sync;
    type Error: std::error::Error + Send + Sync + 'static;

    /// Draw exactly from the normalized prior.
    fn initialize(
        &self,
        particle_index: usize,
        rng: &mut ChaCha8Rng,
    ) -> Result<Self::State, Self::Error>;

    fn log_prior(&self, state: &Self::State) -> Result<f64, Self::Error>;

    fn log_likelihood(&self, state: &Self::State) -> Result<f64, Self::Error>;

    /// Propose an MCMC move. The returned proposal ratio makes asymmetric
    /// kernels valid; bounded reflected random walks can return zero.
    fn mutate(
        &self,
        state: &Self::State,
        scale: f64,
        rng: &mut ChaCha8Rng,
    ) -> Result<Mutation<Self::State>, Self::Error>;
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct TemperedConfig {
    pub particles: usize,
    pub seed: u64,
    pub target_ess_fraction: f64,
    pub mutation_steps: usize,
    pub mutation_scale: f64,
    pub maximum_mutation_scale: f64,
    pub minimum_temperature_increment: f64,
    pub maximum_temperature_steps: usize,
}

impl TemperedConfig {
    pub fn validate(&self) -> Result<(), TemperedError> {
        if self.particles < 2
            || !self.target_ess_fraction.is_finite()
            || !(0.05..1.0).contains(&self.target_ess_fraction)
            || self.mutation_steps == 0
            || !self.mutation_scale.is_finite()
            || self.mutation_scale <= 0.0
            || !self.maximum_mutation_scale.is_finite()
            || self.maximum_mutation_scale < self.mutation_scale
            || !self.minimum_temperature_increment.is_finite()
            || self.minimum_temperature_increment <= 0.0
            || self.minimum_temperature_increment > 1.0
            || self.maximum_temperature_steps == 0
        {
            return Err(TemperedError::InvalidConfiguration);
        }
        Ok(())
    }
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct TemperedCheckpoint {
    pub step: usize,
    pub temperature: f64,
    pub temperature_increment: f64,
    pub particle_ess: f64,
    pub resampled: bool,
    pub mutation_acceptance: Option<f64>,
    pub log_evidence_increment: f64,
    pub cumulative_log_evidence: f64,
}

#[derive(Debug, Clone)]
pub struct TemperedResult<S> {
    pub particles: Vec<S>,
    pub log_weights: Vec<f64>,
    pub log_likelihoods: Vec<f64>,
    pub checkpoints: Vec<TemperedCheckpoint>,
    pub log_evidence: f64,
}

impl<S> TemperedResult<S> {
    pub fn normalized_weights(&self) -> Vec<f64> {
        self.log_weights.iter().map(|value| value.exp()).collect()
    }

    pub fn effective_sample_size(&self) -> Result<f64, TemperedError> {
        effective_sample_size(&self.log_weights).map_err(TemperedError::Filter)
    }
}

#[derive(Debug, Error)]
pub enum TemperedError {
    #[error("invalid tempered-SMC configuration")]
    InvalidConfiguration,
    #[error("static model failed: {0}")]
    Model(String),
    #[error("prior or likelihood density is not finite")]
    InvalidDensity,
    #[error("tempering exceeded its configured step limit")]
    StepLimit,
    #[error(transparent)]
    Filter(#[from] SmcError),
}

fn model_error(error: impl std::fmt::Display) -> TemperedError {
    TemperedError::Model(error.to_string())
}

fn valid_density(value: f64) -> bool {
    value.is_finite() || value == f64::NEG_INFINITY
}

fn ess_after_increment(
    log_weights: &[f64],
    log_likelihoods: &[f64],
    increment: f64,
) -> Result<f64, TemperedError> {
    let raw = log_weights
        .iter()
        .zip(log_likelihoods)
        .map(|(weight, likelihood)| weight + increment * likelihood)
        .collect::<Vec<_>>();
    let (normalized, _) = normalize_log_weights(&raw)?;
    effective_sample_size(&normalized).map_err(TemperedError::Filter)
}

fn choose_temperature_increment(
    log_weights: &[f64],
    log_likelihoods: &[f64],
    remaining: f64,
    target_ess: f64,
    minimum: f64,
) -> Result<f64, TemperedError> {
    if ess_after_increment(log_weights, log_likelihoods, remaining)? >= target_ess {
        return Ok(remaining);
    }
    let mut lower = 0.0;
    let mut upper = remaining;
    for _ in 0..52 {
        let middle = 0.5 * (lower + upper);
        if ess_after_increment(log_weights, log_likelihoods, middle)? >= target_ess {
            lower = middle;
        } else {
            upper = middle;
        }
    }
    Ok(lower.max(minimum.min(remaining)))
}

pub fn run_tempered_smc<M: StaticModel>(
    model: &M,
    config: &TemperedConfig,
) -> Result<TemperedResult<M::State>, TemperedError> {
    config.validate()?;
    let initialized = (0..config.particles)
        .into_par_iter()
        .map(|particle| {
            let mut rng = rng_for(config.seed, "tempered-initialize", 0, particle, 0);
            let state = model.initialize(particle, &mut rng).map_err(model_error)?;
            let log_prior = model.log_prior(&state).map_err(model_error)?;
            let log_likelihood = model.log_likelihood(&state).map_err(model_error)?;
            if !valid_density(log_prior) || !valid_density(log_likelihood) {
                return Err(TemperedError::InvalidDensity);
            }
            Ok((state, log_prior, log_likelihood))
        })
        .collect::<Vec<Result<_, TemperedError>>>();

    let mut states = Vec::with_capacity(config.particles);
    let mut log_priors = Vec::with_capacity(config.particles);
    let mut log_likelihoods = Vec::with_capacity(config.particles);
    for item in initialized {
        let (state, log_prior, log_likelihood) = item?;
        states.push(state);
        log_priors.push(log_prior);
        log_likelihoods.push(log_likelihood);
    }

    let uniform_log_weight = -(config.particles as f64).ln();
    let mut log_weights = vec![uniform_log_weight; config.particles];
    let target_ess = config.target_ess_fraction * config.particles as f64;
    let mut temperature = 0.0;
    let mut log_evidence = 0.0;
    let mut checkpoints = Vec::new();

    while temperature < 1.0 - 8.0 * f64::EPSILON {
        if checkpoints.len() >= config.maximum_temperature_steps {
            return Err(TemperedError::StepLimit);
        }
        let remaining = 1.0 - temperature;
        let increment = choose_temperature_increment(
            &log_weights,
            &log_likelihoods,
            remaining,
            target_ess,
            config.minimum_temperature_increment,
        )?;
        let raw_weights = log_weights
            .iter()
            .zip(&log_likelihoods)
            .map(|(weight, likelihood)| weight + increment * likelihood)
            .collect::<Vec<_>>();
        let (normalized, evidence_increment) = normalize_log_weights(&raw_weights)?;
        log_weights = normalized;
        temperature = (temperature + increment).min(1.0);
        log_evidence += evidence_increment;
        let ess = effective_sample_size(&log_weights)?;
        let should_resample = temperature < 1.0 - 8.0 * f64::EPSILON;
        let mut acceptance = None;

        if should_resample {
            let linear_weights = log_weights
                .iter()
                .map(|value| value.exp())
                .collect::<Vec<_>>();
            let mut rng = rng_for(config.seed, "tempered-resample", checkpoints.len(), 0, 0);
            let first_offset = rng.gen::<f64>() / config.particles as f64;
            let ancestors = systematic_resample(&linear_weights, first_offset)?;
            states = ancestors
                .iter()
                .map(|index| states[*index].clone())
                .collect();
            log_priors = ancestors.iter().map(|index| log_priors[*index]).collect();
            log_likelihoods = ancestors
                .iter()
                .map(|index| log_likelihoods[*index])
                .collect();
            log_weights.fill(uniform_log_weight);

            let mutation_scale = (config.mutation_scale / temperature.sqrt().max(1e-6))
                .min(config.maximum_mutation_scale);
            let mut accepted_total = 0usize;
            for mutation_step in 0..config.mutation_steps {
                let proposals = states
                    .par_iter()
                    .zip(&log_priors)
                    .zip(&log_likelihoods)
                    .enumerate()
                    .map(|(particle, ((state, current_prior), current_likelihood))| {
                        let mut rng = rng_for(
                            config.seed,
                            "tempered-mutation",
                            checkpoints.len(),
                            particle,
                            mutation_step as u64,
                        );
                        let mutation = model
                            .mutate(state, mutation_scale, &mut rng)
                            .map_err(model_error)?;
                        let proposed_prior =
                            model.log_prior(&mutation.state).map_err(model_error)?;
                        let proposed_likelihood =
                            model.log_likelihood(&mutation.state).map_err(model_error)?;
                        if !valid_density(proposed_prior) || !valid_density(proposed_likelihood) {
                            return Err(TemperedError::InvalidDensity);
                        }
                        let log_acceptance = proposed_prior + temperature * proposed_likelihood
                            - current_prior
                            - temperature * current_likelihood
                            + mutation.log_reverse_over_forward;
                        let draw = rng.gen::<f64>().max(f64::MIN_POSITIVE).ln();
                        if draw < log_acceptance.min(0.0) {
                            Ok((mutation.state, proposed_prior, proposed_likelihood, true))
                        } else {
                            Ok((state.clone(), *current_prior, *current_likelihood, false))
                        }
                    })
                    .collect::<Vec<Result<_, TemperedError>>>();

                let mut next_states = Vec::with_capacity(config.particles);
                let mut next_priors = Vec::with_capacity(config.particles);
                let mut next_likelihoods = Vec::with_capacity(config.particles);
                for proposal in proposals {
                    let (state, prior, likelihood, accepted) = proposal?;
                    next_states.push(state);
                    next_priors.push(prior);
                    next_likelihoods.push(likelihood);
                    accepted_total += usize::from(accepted);
                }
                states = next_states;
                log_priors = next_priors;
                log_likelihoods = next_likelihoods;
            }
            acceptance =
                Some(accepted_total as f64 / (config.particles * config.mutation_steps) as f64);
        }

        checkpoints.push(TemperedCheckpoint {
            step: checkpoints.len(),
            temperature,
            temperature_increment: increment,
            particle_ess: ess,
            resampled: should_resample,
            mutation_acceptance: acceptance,
            log_evidence_increment: evidence_increment,
            cumulative_log_evidence: log_evidence,
        });
    }

    Ok(TemperedResult {
        particles: states,
        log_weights,
        log_likelihoods,
        checkpoints,
        log_evidence,
    })
}

#[cfg(test)]
mod tests {
    use rand_distr::{Distribution, StandardNormal};

    use super::*;

    #[derive(Debug, Clone, Copy, PartialEq)]
    struct State(f64);

    #[derive(Debug, thiserror::Error)]
    #[error("toy model error")]
    struct ToyError;

    struct GaussianModel;

    impl StaticModel for GaussianModel {
        type State = State;
        type Error = ToyError;

        fn initialize(
            &self,
            _particle_index: usize,
            rng: &mut ChaCha8Rng,
        ) -> Result<Self::State, Self::Error> {
            let draw: f64 = StandardNormal.sample(rng);
            Ok(State(5.0 * draw))
        }

        fn log_prior(&self, state: &Self::State) -> Result<f64, Self::Error> {
            Ok(-0.5 * (state.0 / 5.0).powi(2))
        }

        fn log_likelihood(&self, state: &Self::State) -> Result<f64, Self::Error> {
            Ok(-0.5 * (2.0 - state.0).powi(2))
        }

        fn mutate(
            &self,
            state: &Self::State,
            scale: f64,
            rng: &mut ChaCha8Rng,
        ) -> Result<Mutation<Self::State>, Self::Error> {
            let draw: f64 = StandardNormal.sample(rng);
            Ok(Mutation::symmetric(State(state.0 + scale * draw)))
        }
    }

    fn config() -> TemperedConfig {
        TemperedConfig {
            particles: 4096,
            seed: 370,
            target_ess_fraction: 0.8,
            mutation_steps: 4,
            mutation_scale: 0.8,
            maximum_mutation_scale: 1.0,
            minimum_temperature_increment: 0.005,
            maximum_temperature_steps: 80,
        }
    }

    #[test]
    fn tempered_sampler_recovers_conjugate_gaussian_posterior() {
        let result = run_tempered_smc(&GaussianModel, &config()).unwrap();
        let mean = result
            .particles
            .iter()
            .zip(&result.log_weights)
            .map(|(state, weight)| state.0 * weight.exp())
            .sum::<f64>();
        let expected = 50.0 / 26.0;
        assert!((mean - expected).abs() < 0.08, "{mean} != {expected}");
        assert!(result.effective_sample_size().unwrap() > 3000.0);
        assert!(result.checkpoints.len() < 20);
        let acceptance = result
            .checkpoints
            .iter()
            .filter_map(|checkpoint| checkpoint.mutation_acceptance)
            .collect::<Vec<_>>();
        assert!(acceptance.iter().all(|rate| *rate > 0.1 && *rate <= 1.0));
        assert!(acceptance.iter().any(|rate| *rate < 0.9));
    }

    #[test]
    fn tempered_sampler_is_identical_across_thread_counts() {
        let one = rayon::ThreadPoolBuilder::new()
            .num_threads(1)
            .build()
            .unwrap()
            .install(|| run_tempered_smc(&GaussianModel, &config()).unwrap());
        let four = rayon::ThreadPoolBuilder::new()
            .num_threads(4)
            .build()
            .unwrap()
            .install(|| run_tempered_smc(&GaussianModel, &config()).unwrap());
        assert_eq!(one.particles, four.particles);
        assert_eq!(one.log_weights, four.log_weights);
        assert_eq!(one.log_likelihoods, four.log_likelihoods);
        assert_eq!(one.checkpoints, four.checkpoints);
        assert_eq!(one.log_evidence, four.log_evidence);
    }
}
