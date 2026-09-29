//! Satellite communication observation equations and bias models.

mod ephemeris;
mod exact_contact;
mod observation;
mod satcom;
mod statistics;

pub use ephemeris::{
    propagate_satellite_ecef_constant_velocity, PropagatedSatelliteEcefState,
    SatelliteEcefPropagationError, SatelliteEcefPropagationLimit, SatelliteEcefState,
    SatelliteEphemerisApproximation,
};
pub use exact_contact::{
    score_exact_time_satcom_contact, ExactTimeBfoDatum, ExactTimeBfoFit, ExactTimeBtoFit,
    ExactTimeSatcomContact, ExactTimeSatcomContactError, ExactTimeSatcomContactFit,
};
pub use observation::{evaluate_observation, ObservationFit, SatcomModelConfig, SatcomModelError};

pub use satcom::{bfo_components, bto, BfoComponents, BfoConstants, BtoConstants};
pub use statistics::{
    bfo_bias_predictive_update, bfo_bias_sequence_log_likelihood, normal_log_density,
    ou_state_and_integral_moments, ou_transition_moments, BfoBiasState, OuIntegralMoments,
    OuTransitionMoments, StatisticsError,
};
