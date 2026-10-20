//! Conditional timing model for the successful APU/SDU restart chain.
//!
//! This module deliberately models only the lag density conditional on a
//! dual-engine-generator-loss event and a successful APU pickup, SDU restart,
//! and recorded R600 logon.  It has no API for an event-occurrence factor.

use mh370_domain::Seconds;
use serde::{Deserialize, Serialize};
use thiserror::Error;

/// Stable identifier for this explicitly conditional sensitivity family.
pub const SUCCESSFUL_APU_SDU_ERLANG_LAG_FAMILY: &str =
    "conditional_successful_apu_sdu_restart_erlang_lag";

/// Scientific boundaries that downstream manifests should retain.
pub const SUCCESSFUL_APU_SDU_ERLANG_LAG_LIMITATIONS: &[&str] = &[
    "conditional on dual-engine generator loss causing the power interruption and on a successful APU pickup, SDU restart, and recorded R600 logon",
    "published approximate APU and SDU chain times do not provide an empirical lag distribution or scatter; Erlang parameters are an analyst-declared sensitivity",
    "the R600 timing evidence must be consumed once and must not be accompanied by an independent exhaustion-window or logon-occurrence likelihood",
    "this timing density does not model the R600 BTO or either final BFO observation",
];

const ABSOLUTE_RELATIVE_TOLERANCE_SECONDS: f64 = 1.0e-6;
const MAX_NUMERICALLY_SUPPORTED_ERLANG_SHAPE: u32 = 128;
const QUANTILE_BISECTION_ITERATIONS: usize = 128;

/// An absolute UTC instant represented as POSIX seconds without leap seconds.
///
/// Keeping this distinct from [`Seconds`] prevents an absolute time from being
/// silently substituted for a duration or a flight-relative time.
#[derive(Debug, Clone, Copy, PartialEq, PartialOrd, Serialize, Deserialize)]
#[serde(transparent)]
pub struct UtcPosixSeconds(pub f64);

/// The observed R600 logon time expressed on both required clocks.
///
/// `relative_seconds` is measured from `relative_epoch_utc_posix_seconds`.
/// Validation requires that this representation agrees with the absolute UTC
/// representation to one microsecond, while retaining fractional seconds.
#[derive(Debug, Clone, Copy, PartialEq, Serialize, Deserialize)]
pub struct R600ObservedLogonTime {
    pub absolute_utc_posix_seconds: UtcPosixSeconds,
    pub relative_seconds: Seconds,
    pub relative_epoch_utc_posix_seconds: UtcPosixSeconds,
}

/// Erlang lag parameters under a successful APU-plus-SDU event chain.
///
/// The release sensitivity uses `shape = 8` and `scale = 14.875 s`.  Those
/// values are not a fitted manufacturer distribution and callers must keep the
/// family conditional rather than averaging it into an unconditional model.
#[derive(Debug, Clone, Copy, PartialEq, Serialize, Deserialize)]
pub struct SuccessfulApuSduErlangLagConfig {
    pub shape: u32,
    pub scale: Seconds,
}

impl SuccessfulApuSduErlangLagConfig {
    /// Declared release sensitivity: mean lag 119 seconds and shape eight.
    pub const fn release_sensitivity() -> Self {
        Self {
            shape: 8,
            scale: Seconds(14.875),
        }
    }

    pub fn validate(self) -> Result<(), SystemsTimingError> {
        if self.shape == 0 || self.shape > MAX_NUMERICALLY_SUPPORTED_ERLANG_SHAPE {
            return Err(SystemsTimingError::InvalidErlangShape { shape: self.shape });
        }
        if !self.scale.0.is_finite() || self.scale.0 <= 0.0 {
            return Err(SystemsTimingError::InvalidErlangScale { scale: self.scale });
        }
        Ok(())
    }
}

/// Timing inputs for the conditional lag density.
///
/// The generator-loss time uses the same relative epoch declared by
/// `observed_r600_logon_time`.  There is intentionally no success probability,
/// occurrence indicator, exhaustion window, BTO, or BFO field.
#[derive(Debug, Clone, Copy, PartialEq, Serialize, Deserialize)]
pub struct ConditionalSuccessfulApuSduTimingInput {
    pub observed_r600_logon_time: R600ObservedLogonTime,
    pub dual_generator_loss_relative_seconds: Seconds,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum ConditionalLagSupport {
    PositiveLag,
    NonpositiveLag,
}

/// Result of evaluating the normalized Erlang density with respect to seconds.
#[derive(Debug, Clone, Copy, PartialEq)]
pub struct ConditionalSuccessfulApuSduTimingLikelihood {
    pub lag: Seconds,
    pub support: ConditionalLagSupport,
    /// Natural logarithm of the normalized probability density per second.
    /// This is negative infinity for a nonpositive lag.
    pub normalized_log_density_per_second: f64,
}

/// Equal-tail central interval of the declared conditional lag distribution.
#[derive(Debug, Clone, Copy, PartialEq, Serialize, Deserialize)]
pub struct ErlangCentralLagInterval {
    pub probability: f64,
    pub lower: Seconds,
    pub upper: Seconds,
}

#[derive(Debug, Error, Clone, Copy, PartialEq)]
pub enum SystemsTimingError {
    #[error("Erlang shape {shape} is outside the supported integer range 1..=128")]
    InvalidErlangShape { shape: u32 },
    #[error("Erlang scale must be finite and strictly positive, got {scale:?}")]
    InvalidErlangScale { scale: Seconds },
    #[error("R600 absolute UTC, relative time, and relative epoch must all be finite")]
    NonfiniteR600Time,
    #[error(
        "R600 absolute and relative representations disagree: declared {declared:?}, implied {implied:?}"
    )]
    InconsistentR600TimeRepresentations { declared: Seconds, implied: Seconds },
    #[error("dual-generator-loss relative time must be finite")]
    NonfiniteDualGeneratorLossTime,
    #[error("central interval probability must be finite and strictly between zero and one")]
    InvalidCentralProbability,
}

impl R600ObservedLogonTime {
    pub fn validate(self) -> Result<(), SystemsTimingError> {
        if !self.absolute_utc_posix_seconds.0.is_finite()
            || !self.relative_seconds.0.is_finite()
            || !self.relative_epoch_utc_posix_seconds.0.is_finite()
        {
            return Err(SystemsTimingError::NonfiniteR600Time);
        }
        let implied =
            Seconds(self.absolute_utc_posix_seconds.0 - self.relative_epoch_utc_posix_seconds.0);
        if (implied.0 - self.relative_seconds.0).abs() > ABSOLUTE_RELATIVE_TOLERANCE_SECONDS {
            return Err(SystemsTimingError::InconsistentR600TimeRepresentations {
                declared: self.relative_seconds,
                implied,
            });
        }
        Ok(())
    }
}

/// Evaluate the event-chain lag density conditional on successful completion.
///
/// This returns a proper Erlang density with respect to seconds.  A generator
/// loss at or after the observed R600 logon has zero density (`-inf` in log
/// space), rather than being treated as a configuration failure.
pub fn conditional_successful_apu_sdu_logon_lag_likelihood(
    config: SuccessfulApuSduErlangLagConfig,
    input: ConditionalSuccessfulApuSduTimingInput,
) -> Result<ConditionalSuccessfulApuSduTimingLikelihood, SystemsTimingError> {
    config.validate()?;
    input.observed_r600_logon_time.validate()?;
    if !input.dual_generator_loss_relative_seconds.0.is_finite() {
        return Err(SystemsTimingError::NonfiniteDualGeneratorLossTime);
    }

    let lag = Seconds(
        input.observed_r600_logon_time.relative_seconds.0
            - input.dual_generator_loss_relative_seconds.0,
    );
    if lag.0 <= 0.0 {
        return Ok(ConditionalSuccessfulApuSduTimingLikelihood {
            lag,
            support: ConditionalLagSupport::NonpositiveLag,
            normalized_log_density_per_second: f64::NEG_INFINITY,
        });
    }

    let shape = f64::from(config.shape);
    let log_gamma_shape = log_integer_gamma(config.shape);
    let log_density = (shape - 1.0) * lag.0.ln()
        - lag.0 / config.scale.0
        - log_gamma_shape
        - shape * config.scale.0.ln();

    Ok(ConditionalSuccessfulApuSduTimingLikelihood {
        lag,
        support: ConditionalLagSupport::PositiveLag,
        normalized_log_density_per_second: log_density,
    })
}

/// Return a deterministic equal-tail interval for the configured Erlang lag.
pub fn erlang_central_lag_interval(
    config: SuccessfulApuSduErlangLagConfig,
    probability: f64,
) -> Result<ErlangCentralLagInterval, SystemsTimingError> {
    config.validate()?;
    if !probability.is_finite() || probability <= 0.0 || probability >= 1.0 {
        return Err(SystemsTimingError::InvalidCentralProbability);
    }
    let tail = 0.5 * (1.0 - probability);
    Ok(ErlangCentralLagInterval {
        probability,
        lower: Seconds(erlang_quantile(config, tail)),
        upper: Seconds(erlang_quantile(config, 1.0 - tail)),
    })
}

fn log_integer_gamma(shape: u32) -> f64 {
    (1..shape).map(|factor| f64::from(factor).ln()).sum()
}

fn erlang_cdf(config: SuccessfulApuSduErlangLagConfig, value_seconds: f64) -> f64 {
    if value_seconds <= 0.0 {
        return 0.0;
    }
    let scaled = value_seconds / config.scale.0;
    if scaled > 745.0 {
        return 1.0;
    }
    let mut term = 1.0;
    let mut sum = term;
    for index in 1..config.shape {
        term *= scaled / f64::from(index);
        sum += term;
    }
    (1.0 - (-scaled).exp() * sum).clamp(0.0, 1.0)
}

fn erlang_quantile(config: SuccessfulApuSduErlangLagConfig, probability: f64) -> f64 {
    let mut lower = 0.0;
    let mut upper = f64::from(config.shape) * config.scale.0;
    while erlang_cdf(config, upper) < probability {
        upper *= 2.0;
    }
    for _ in 0..QUANTILE_BISECTION_ITERATIONS {
        let midpoint = 0.5 * (lower + upper);
        if erlang_cdf(config, midpoint) < probability {
            lower = midpoint;
        } else {
            upper = midpoint;
        }
    }
    0.5 * (lower + upper)
}

#[cfg(test)]
mod tests {
    use super::*;

    const ORIGIN_UTC_POSIX_SECONDS: f64 = 1_394_215_309.0;
    const R600_UTC_POSIX_SECONDS: f64 = 1_394_237_969.416;
    const R600_RELATIVE_SECONDS: f64 = 22_660.416;

    fn observation() -> R600ObservedLogonTime {
        R600ObservedLogonTime {
            absolute_utc_posix_seconds: UtcPosixSeconds(R600_UTC_POSIX_SECONDS),
            relative_seconds: Seconds(R600_RELATIVE_SECONDS),
            relative_epoch_utc_posix_seconds: UtcPosixSeconds(ORIGIN_UTC_POSIX_SECONDS),
        }
    }

    fn likelihood_at_lag(lag_seconds: f64) -> ConditionalSuccessfulApuSduTimingLikelihood {
        conditional_successful_apu_sdu_logon_lag_likelihood(
            SuccessfulApuSduErlangLagConfig::release_sensitivity(),
            ConditionalSuccessfulApuSduTimingInput {
                observed_r600_logon_time: observation(),
                dual_generator_loss_relative_seconds: Seconds(R600_RELATIVE_SECONDS - lag_seconds),
            },
        )
        .unwrap()
    }

    #[test]
    fn precise_r600_time_is_consistent_on_both_clocks() {
        observation().validate().unwrap();
        let evaluated = likelihood_at_lag(119.0);
        assert_eq!(evaluated.lag, Seconds(119.0));
        assert_eq!(evaluated.support, ConditionalLagSupport::PositiveLag);
    }

    #[test]
    fn independently_calculated_mode_and_normalized_log_density_match() {
        let config = SuccessfulApuSduErlangLagConfig::release_sensitivity();
        let mode = f64::from(config.shape - 1) * config.scale.0;
        assert_eq!(mode, 104.125);

        let at_mode = likelihood_at_lag(mode).normalized_log_density_per_second;
        // Independently calculated from x^7 exp(-x/theta)/(7! theta^8).
        assert!((at_mode - (-4.603_472_269_109_915)).abs() < 1.0e-13);
        assert!(at_mode > likelihood_at_lag(mode - 1.0).normalized_log_density_per_second);
        assert!(at_mode > likelihood_at_lag(mode + 1.0).normalized_log_density_per_second);
    }

    #[test]
    fn central_intervals_match_independent_integer_gamma_quantiles() {
        let config = SuccessfulApuSduErlangLagConfig::release_sensitivity();
        let expected = [
            (0.90, 59.214_738_944_565_48, 195.578_192_811_177_7),
            (0.95, 51.375_753_629_133_925, 214.537_296_005_322_8),
            (0.99, 38.245_152_982_637_32, 254.862_199_875_085_76),
        ];
        for (probability, expected_lower, expected_upper) in expected {
            let interval = erlang_central_lag_interval(config, probability).unwrap();
            assert!((interval.lower.0 - expected_lower).abs() < 1.0e-9);
            assert!((interval.upper.0 - expected_upper).abs() < 1.0e-9);
        }
    }

    #[test]
    fn nonpositive_lags_have_zero_density_not_an_occurrence_factor() {
        for lag in [0.0, -1.0] {
            let evaluated = likelihood_at_lag(lag);
            assert_eq!(evaluated.support, ConditionalLagSupport::NonpositiveLag);
            assert_eq!(
                evaluated.normalized_log_density_per_second,
                f64::NEG_INFINITY
            );
        }
    }

    #[test]
    fn invalid_configuration_and_clock_mismatch_are_rejected() {
        assert!(matches!(
            SuccessfulApuSduErlangLagConfig {
                shape: 0,
                scale: Seconds(14.875),
            }
            .validate(),
            Err(SystemsTimingError::InvalidErlangShape { shape: 0 })
        ));
        assert!(matches!(
            SuccessfulApuSduErlangLagConfig {
                shape: 8,
                scale: Seconds(0.0),
            }
            .validate(),
            Err(SystemsTimingError::InvalidErlangScale { .. })
        ));
        for probability in [0.0, 1.0, f64::NAN] {
            assert_eq!(
                erlang_central_lag_interval(
                    SuccessfulApuSduErlangLagConfig::release_sensitivity(),
                    probability,
                ),
                Err(SystemsTimingError::InvalidCentralProbability)
            );
        }

        let mut mismatched = observation();
        mismatched.relative_seconds.0 += 0.001;
        assert!(matches!(
            mismatched.validate(),
            Err(SystemsTimingError::InconsistentR600TimeRepresentations { .. })
        ));
    }

    #[test]
    fn forbidden_legacy_exhaustion_clock_is_absent() {
        let forbidden = ["00:17", ":30"].concat();
        assert!(!include_str!("systems_timing.rs").contains(&forbidden));
    }
}
