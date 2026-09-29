use std::error::Error;

use rand_chacha::ChaCha8Rng;

use serde::{Deserialize, Serialize};

/// Stable identifier for a deliberately over-sampled structural or process
/// stratum. The scientific meaning of each identifier belongs to the model
/// and must be recorded by its run metadata.
#[derive(
    Debug, Clone, Copy, Default, PartialEq, Eq, PartialOrd, Ord, Hash, Serialize, Deserialize,
)]
#[serde(transparent)]
pub struct StratumId(pub u32);

#[derive(Debug, Clone)]
pub struct Initialization<S> {
    pub state: S,
    /// Within-stratum `log p(state | stratum) - log q(state | stratum)`.
    ///
    /// The filter separately corrects the declared scientific stratum mass
    /// for its computational particle allocation.
    pub log_prior_over_proposal: f64,
}

impl<S> Initialization<S> {
    pub fn from_prior(state: S) -> Self {
        Self {
            state,
            log_prior_over_proposal: 0.0,
        }
    }
}

#[derive(Debug, Clone)]
pub struct Proposal<S> {
    pub state: S,
    /// log p(transition) - log q(proposal).
    pub log_prior_over_proposal: f64,
}

impl<S> Proposal<S> {
    pub fn from_prior(state: S) -> Self {
        Self {
            state,
            log_prior_over_proposal: 0.0,
        }
    }
}

pub trait ParticleModel: Sync {
    type State: Clone + Send + Sync;
    type Observation: Sync;
    type Error: Error + Send + Sync + 'static;

    fn observation_time_s(&self, observation: &Self::Observation) -> f64;

    fn initialize(
        &self,
        particle_index: usize,
        rng: &mut ChaCha8Rng,
    ) -> Result<Self::State, Self::Error>;

    /// Initialize a particle inside a caller-declared computational stratum.
    ///
    /// Models that use stratification override this method and [`Self::stratum`].
    /// The default preserves the original unstratified API and is valid only
    /// for [`StratumId::default()`]. Randomness remains keyed by the canonical
    /// global particle index supplied by the engine.
    fn initialize_in_stratum(
        &self,
        stratum: StratumId,
        particle_index: usize,
        _particle_index_within_stratum: usize,
        _particles_in_stratum: usize,
        rng: &mut ChaCha8Rng,
    ) -> Result<Initialization<Self::State>, Self::Error> {
        debug_assert_eq!(stratum, StratumId::default());
        self.initialize(particle_index, rng)
            .map(Initialization::from_prior)
    }

    /// Return the immutable sampling stratum carried by a state.
    ///
    /// Current flight mode may change; this identifier should instead denote
    /// the structural family or latent manoeuvre-rate band whose representation
    /// the run intends to preserve.
    fn stratum(&self, _state: &Self::State) -> StratumId {
        StratumId::default()
    }

    /// A predictive approximation used only to select auxiliary ancestors.
    ///
    /// Returning zero gives a valid bootstrap-style guide.
    fn guide_log_likelihood(
        &self,
        _state: &Self::State,
        _observation: &Self::Observation,
    ) -> Result<f64, Self::Error> {
        Ok(0.0)
    }

    fn propose(
        &self,
        state: &Self::State,
        observation: &Self::Observation,
        elapsed_seconds: f64,
        rng: &mut ChaCha8Rng,
    ) -> Result<Proposal<Self::State>, Self::Error>;

    /// Score an observation without changing the proposed state.
    fn log_likelihood(
        &self,
        state: &Self::State,
        observation: &Self::Observation,
    ) -> Result<f64, Self::Error>;

    /// Score and assimilate an observation. Models with analytically marginalized
    /// state may update it after computing the predictive density.
    fn observe(
        &self,
        state: &mut Self::State,
        observation: &Self::Observation,
    ) -> Result<f64, Self::Error> {
        self.log_likelihood(state, observation)
    }
}
