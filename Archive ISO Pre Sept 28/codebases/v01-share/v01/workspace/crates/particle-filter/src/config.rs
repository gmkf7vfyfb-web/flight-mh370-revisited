use serde::{Deserialize, Serialize};

use crate::StratumId;

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum Algorithm {
    Bootstrap,
    Auxiliary,
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct FilterConfig {
    pub particles: usize,
    pub seed: u64,
    pub algorithm: Algorithm,
    pub initial_time_s: f64,
    pub ess_resample_fraction: f64,
}

impl FilterConfig {
    pub fn validate(&self) -> Result<(), &'static str> {
        if self.particles < 2 {
            return Err("particle count must be at least two");
        }
        if !self.initial_time_s.is_finite() {
            return Err("initial time must be finite");
        }
        if !self.ess_resample_fraction.is_finite()
            || self.ess_resample_fraction <= 0.0
            || self.ess_resample_fraction > 1.0
        {
            return Err("ESS resampling fraction must lie in (0, 1]");
        }
        Ok(())
    }
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct StratumAllocation {
    pub id: StratumId,
    /// Fixed computational allocation. It need not equal the scientific prior
    /// mass; the filter applies the exact allocation correction.
    pub particles: usize,
    /// Normalized scientific prior probability of this stratum in log space.
    pub log_prior_probability: f64,
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct StratifiedFilterPlan {
    pub strata: Vec<StratumAllocation>,
}

/// Ancestor-selection policy for fixed-allocation stratified filters.
///
/// For each stratum, let `P_r` be the normalized target mass carried by an
/// original root ancestor and let `R` be the number of roots with positive
/// target mass. The defensive proposal is
/// `Q_r = (1-epsilon) P_r + epsilon / R`; a particle is then selected within
/// its root in proportion to its target mass. Exact `p_i / q_i` corrections
/// remain on the children. `epsilon = 0` is the historical behavior.
#[derive(Debug, Clone, Copy, PartialEq, serde::Serialize, serde::Deserialize)]
pub struct WithinStratumResamplingPolicy {
    pub uniform_root_mixture_epsilon: f64,
}

impl Default for WithinStratumResamplingPolicy {
    fn default() -> Self {
        Self {
            uniform_root_mixture_epsilon: 0.0,
        }
    }
}

impl WithinStratumResamplingPolicy {
    pub fn validate(self) -> Result<(), &'static str> {
        if !self.uniform_root_mixture_epsilon.is_finite()
            || !(0.0..=1.0).contains(&self.uniform_root_mixture_epsilon)
        {
            return Err("defensive root-mixture epsilon must lie in [0, 1]");
        }
        Ok(())
    }
}

impl StratifiedFilterPlan {
    pub fn validate(&self, particles: usize) -> Result<(), &'static str> {
        if self.strata.is_empty() {
            return Err("at least one stratum is required");
        }
        if self
            .strata
            .iter()
            .any(|entry| entry.particles == 0 || !entry.log_prior_probability.is_finite())
        {
            return Err("stratum allocations and prior probabilities must be positive and finite");
        }
        let allocated = self
            .strata
            .iter()
            .try_fold(0usize, |total, entry| total.checked_add(entry.particles))
            .ok_or("stratum particle allocation overflowed")?;
        if allocated != particles {
            return Err("stratum allocations must sum to the configured particle count");
        }
        let mut ids = self.strata.iter().map(|entry| entry.id).collect::<Vec<_>>();
        ids.sort_unstable();
        if ids.windows(2).any(|pair| pair[0] == pair[1]) {
            return Err("stratum identifiers must be unique");
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
        if !log_sum.is_finite() || log_sum.abs() > 1e-10 {
            return Err("stratum log prior probabilities must be normalized");
        }
        Ok(())
    }

    pub(crate) fn canonical_allocations(&self) -> Vec<StratumAllocation> {
        let mut allocations = self.strata.clone();
        allocations.sort_unstable_by_key(|entry| entry.id);
        allocations
    }
}
