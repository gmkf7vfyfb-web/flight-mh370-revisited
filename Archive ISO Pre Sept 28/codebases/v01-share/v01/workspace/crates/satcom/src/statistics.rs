use std::f64::consts::PI;

use serde::{Deserialize, Serialize};
use thiserror::Error;

#[derive(Debug, Error, Clone, PartialEq)]
pub enum StatisticsError {
    #[error("standard deviation must be finite and positive")]
    InvalidStandardDeviation,
    #[error("variance, reversion rate, noise strength, and time must be finite and non-negative")]
    InvalidNonNegativeParameter,
    #[error("observation, prediction, and SD sequences have different lengths")]
    SequenceLengthMismatch,
}

pub fn normal_log_density(residual: f64, standard_deviation: f64) -> Result<f64, StatisticsError> {
    if !residual.is_finite() || !standard_deviation.is_finite() || standard_deviation <= 0.0 {
        return Err(StatisticsError::InvalidStandardDeviation);
    }
    Ok(-0.5 * (residual / standard_deviation).powi(2)
        - (standard_deviation * (2.0 * PI).sqrt()).ln())
}

#[derive(Debug, Clone, Copy, PartialEq, Serialize, Deserialize)]
pub struct BfoBiasState {
    pub mean_hz: f64,
    pub variance_hz2: f64,
}

pub fn bfo_bias_predictive_update(
    state: BfoBiasState,
    observed_bfo_hz: f64,
    base_without_bias_hz: f64,
    measurement_sd_hz: f64,
) -> Result<(f64, f64, BfoBiasState), StatisticsError> {
    if !state.variance_hz2.is_finite()
        || state.variance_hz2 < 0.0
        || !measurement_sd_hz.is_finite()
        || measurement_sd_hz <= 0.0
    {
        return Err(StatisticsError::InvalidNonNegativeParameter);
    }
    let innovation = observed_bfo_hz - base_without_bias_hz - state.mean_hz;
    let predictive_variance = state.variance_hz2 + measurement_sd_hz.powi(2);
    let log_likelihood =
        -0.5 * (innovation.powi(2) / predictive_variance + (2.0 * PI * predictive_variance).ln());
    let gain = state.variance_hz2 / predictive_variance;
    let updated = BfoBiasState {
        mean_hz: state.mean_hz + gain * innovation,
        variance_hz2: state.variance_hz2 * (1.0 - gain),
    };
    Ok((log_likelihood, innovation, updated))
}

pub fn bfo_bias_sequence_log_likelihood(
    observed_bfo_hz: &[f64],
    base_without_bias_hz: &[f64],
    measurement_sd_hz: &[f64],
    prior_mean_hz: f64,
    prior_sd_hz: f64,
) -> Result<(f64, Vec<f64>, BfoBiasState), StatisticsError> {
    if observed_bfo_hz.len() != base_without_bias_hz.len()
        || observed_bfo_hz.len() != measurement_sd_hz.len()
    {
        return Err(StatisticsError::SequenceLengthMismatch);
    }
    if !prior_sd_hz.is_finite() || prior_sd_hz <= 0.0 {
        return Err(StatisticsError::InvalidStandardDeviation);
    }
    let mut state = BfoBiasState {
        mean_hz: prior_mean_hz,
        variance_hz2: prior_sd_hz.powi(2),
    };
    let mut total = 0.0;
    let mut innovations = Vec::with_capacity(observed_bfo_hz.len());
    for ((observed, base), sd) in observed_bfo_hz
        .iter()
        .zip(base_without_bias_hz)
        .zip(measurement_sd_hz)
    {
        let (increment, innovation, updated) =
            bfo_bias_predictive_update(state, *observed, *base, *sd)?;
        total += increment;
        innovations.push(innovation);
        state = updated;
    }
    Ok((total, innovations, state))
}

#[derive(Debug, Clone, Copy, PartialEq, Serialize, Deserialize)]
pub struct OuTransitionMoments {
    pub mean: f64,
    pub variance: f64,
    pub phi: f64,
}

#[derive(Debug, Clone, Copy, PartialEq, Serialize, Deserialize)]
pub struct OuIntegralMoments {
    pub state_mean: f64,
    pub integral_mean: f64,
    pub state_variance: f64,
    pub integral_variance: f64,
    pub covariance: f64,
    pub phi: f64,
}

fn valid_nonnegative(values: &[f64]) -> bool {
    values
        .iter()
        .all(|value| value.is_finite() && *value >= 0.0)
}

pub fn ou_transition_moments(
    value: f64,
    setpoint: f64,
    beta: f64,
    noise_strength: f64,
    dt_seconds: f64,
) -> Result<OuTransitionMoments, StatisticsError> {
    if !value.is_finite()
        || !setpoint.is_finite()
        || !valid_nonnegative(&[beta, noise_strength, dt_seconds])
    {
        return Err(StatisticsError::InvalidNonNegativeParameter);
    }
    if beta == 0.0 {
        Ok(OuTransitionMoments {
            mean: value,
            variance: noise_strength * dt_seconds,
            phi: 1.0,
        })
    } else {
        let phi = (-beta * dt_seconds).exp();
        Ok(OuTransitionMoments {
            mean: setpoint + phi * (value - setpoint),
            variance: noise_strength / (2.0 * beta) * (1.0 - phi.powi(2)),
            phi,
        })
    }
}

pub fn ou_state_and_integral_moments(
    value: f64,
    setpoint: f64,
    beta: f64,
    noise_strength: f64,
    dt_seconds: f64,
) -> Result<OuIntegralMoments, StatisticsError> {
    let transition = ou_transition_moments(value, setpoint, beta, noise_strength, dt_seconds)?;
    let (integral_mean, integral_variance, covariance) = if beta == 0.0 {
        (
            value * dt_seconds,
            noise_strength * dt_seconds.powi(3) / 3.0,
            noise_strength * dt_seconds.powi(2) / 2.0,
        )
    } else {
        let phi = transition.phi;
        (
            setpoint * dt_seconds + (value - setpoint) * (1.0 - phi) / beta,
            noise_strength / beta.powi(2)
                * (dt_seconds - 2.0 * (1.0 - phi) / beta + (1.0 - phi.powi(2)) / (2.0 * beta)),
            noise_strength * (1.0 - phi).powi(2) / (2.0 * beta.powi(2)),
        )
    };
    Ok(OuIntegralMoments {
        state_mean: transition.mean,
        integral_mean,
        state_variance: transition.variance,
        integral_variance,
        covariance,
        phi: transition.phi,
    })
}

#[cfg(test)]
mod tests {
    use approx::assert_abs_diff_eq;

    use super::*;

    #[test]
    fn ou_exact_moments_cover_brownian_and_stationary_limits() {
        let moments = ou_transition_moments(10.0, 4.0, 0.2, 3.0, 5.0).unwrap();
        let phi = (-1.0_f64).exp();
        assert_abs_diff_eq!(moments.phi, phi, epsilon = 1e-15);
        assert_abs_diff_eq!(moments.mean, 4.0 + 6.0 * phi, epsilon = 1e-15);
        assert_abs_diff_eq!(
            moments.variance,
            3.0 / 0.4 * (1.0 - phi.powi(2)),
            epsilon = 1e-15
        );

        let brownian = ou_state_and_integral_moments(10.0, 99.0, 0.0, 3.0, 5.0).unwrap();
        assert_eq!(brownian.state_mean, 10.0);
        assert_eq!(brownian.integral_mean, 50.0);
        assert_eq!(brownian.state_variance, 15.0);
        assert_eq!(brownian.integral_variance, 125.0);
        assert_eq!(brownian.covariance, 37.5);
    }

    #[test]
    fn sequential_bias_fixture_matches_frozen_dense_result() {
        let (log_likelihood, innovations, state) = bfo_bias_sequence_log_likelihood(
            &[105.0, 110.0, 95.0, 120.0],
            &[-40.0, -35.0, -55.0, -25.0],
            &[7.0, 4.0, 2.0, 7.0],
            150.0,
            25.0,
        )
        .unwrap();
        assert_abs_diff_eq!(log_likelihood, -13.263_466_318_260_075, epsilon = 1e-11);
        assert_eq!(innovations.len(), 4);
        let precision = 1.0 / 25.0_f64.powi(2)
            + 1.0 / 7.0_f64.powi(2)
            + 1.0 / 4.0_f64.powi(2)
            + 1.0 / 2.0_f64.powi(2)
            + 1.0 / 7.0_f64.powi(2);
        assert_abs_diff_eq!(state.variance_hz2, 1.0 / precision, epsilon = 1e-12);
    }
}
