use mh370_domain::{Seconds, Vec3};
use serde::{Deserialize, Serialize};
use thiserror::Error;

/// Satellite position and velocity in the Earth-centred Earth-fixed frame.
#[derive(Debug, Clone, Copy, PartialEq, Serialize, Deserialize)]
pub struct SatelliteEcefState {
    /// ECEF position in kilometres.
    pub position_km: Vec3,
    /// ECEF velocity in kilometres per second.
    pub velocity_km_s: Vec3,
}

/// Machine-readable identity of the approximation used between ephemeris rows.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum SatelliteEphemerisApproximation {
    /// Linear ECEF propagation; satellite acceleration and orbit curvature are neglected.
    ConstantVelocityEcef,
}

/// Caller-declared validity bound for constant-velocity ephemeris propagation.
#[derive(Debug, Clone, Copy, PartialEq, Serialize, Deserialize)]
pub struct SatelliteEcefPropagationLimit {
    /// Maximum permitted magnitude of the propagation interval.
    pub maximum_absolute_delta: Seconds,
}

/// A bounded, constant-velocity satellite-state propagation result.
#[derive(Debug, Clone, Copy, PartialEq, Serialize, Deserialize)]
pub struct PropagatedSatelliteEcefState {
    pub state: SatelliteEcefState,
    pub delta: Seconds,
    pub approximation: SatelliteEphemerisApproximation,
}

#[derive(Debug, Error, Clone, PartialEq)]
pub enum SatelliteEcefPropagationError {
    #[error("satellite ECEF position and velocity must be finite")]
    NonFiniteSourceState,
    #[error("propagation delta must be finite")]
    NonFiniteDelta,
    #[error("maximum absolute propagation delta must be finite and positive")]
    InvalidMaximumAbsoluteDelta,
    #[error(
        "absolute propagation delta {requested_seconds} s exceeds caller-declared maximum {maximum_seconds} s"
    )]
    MaximumAbsoluteDeltaExceeded {
        requested_seconds: f64,
        maximum_seconds: f64,
    },
    #[error("constant-velocity propagation produced a non-finite ECEF position")]
    NonFinitePropagatedPosition,
}

/// Propagate a satellite ECEF state linearly over a short, caller-bounded interval.
///
/// This deliberately does not estimate orbital acceleration or interpolation
/// truncation error. The returned approximation tag makes that limitation
/// available to downstream manifests, while `limit` prevents accidental use
/// beyond the interval the caller has accepted for the source ephemeris.
pub fn propagate_satellite_ecef_constant_velocity(
    source: SatelliteEcefState,
    delta: Seconds,
    limit: SatelliteEcefPropagationLimit,
) -> Result<PropagatedSatelliteEcefState, SatelliteEcefPropagationError> {
    if !source.position_km.is_finite() || !source.velocity_km_s.is_finite() {
        return Err(SatelliteEcefPropagationError::NonFiniteSourceState);
    }
    if !delta.is_finite() {
        return Err(SatelliteEcefPropagationError::NonFiniteDelta);
    }
    if !limit.maximum_absolute_delta.is_finite() || limit.maximum_absolute_delta.0 <= 0.0 {
        return Err(SatelliteEcefPropagationError::InvalidMaximumAbsoluteDelta);
    }
    if delta.0.abs() > limit.maximum_absolute_delta.0 {
        return Err(
            SatelliteEcefPropagationError::MaximumAbsoluteDeltaExceeded {
                requested_seconds: delta.0,
                maximum_seconds: limit.maximum_absolute_delta.0,
            },
        );
    }

    let position_km = source.position_km + source.velocity_km_s * delta.0;
    if !position_km.is_finite() {
        return Err(SatelliteEcefPropagationError::NonFinitePropagatedPosition);
    }

    Ok(PropagatedSatelliteEcefState {
        state: SatelliteEcefState {
            position_km,
            velocity_km_s: source.velocity_km_s,
        },
        delta,
        approximation: SatelliteEphemerisApproximation::ConstantVelocityEcef,
    })
}

#[cfg(test)]
mod tests {
    use approx::assert_abs_diff_eq;

    use super::*;

    fn limit(seconds: f64) -> SatelliteEcefPropagationLimit {
        SatelliteEcefPropagationLimit {
            maximum_absolute_delta: Seconds(seconds),
        }
    }

    #[test]
    fn subsecond_linear_fixture_moves_approximately_0034621_km_and_preserves_velocity() {
        // A one-axis fixture keeps the expected displacement independent of
        // the implementation's vector arithmetic.
        let expected_displacement_km = 0.034_621;
        let delta_seconds = 0.416;
        let velocity_km_s = expected_displacement_km / delta_seconds;
        let source = SatelliteEcefState {
            position_km: Vec3::new(18_000.0, 38_000.0, 400.0),
            velocity_km_s: Vec3::new(velocity_km_s, 0.0, 0.0),
        };

        let propagated =
            propagate_satellite_ecef_constant_velocity(source, Seconds(delta_seconds), limit(0.5))
                .unwrap();

        assert_abs_diff_eq!(
            (propagated.state.position_km - source.position_km).norm(),
            expected_displacement_km,
            epsilon = 2e-12
        );
        assert_eq!(propagated.state.velocity_km_s, source.velocity_km_s);
        assert_eq!(propagated.delta, Seconds(0.416));
        assert_eq!(
            propagated.approximation,
            SatelliteEphemerisApproximation::ConstantVelocityEcef
        );
    }

    #[test]
    fn negative_delta_and_exact_declared_limit_are_supported() {
        let source = SatelliteEcefState {
            position_km: Vec3::new(10.0, 20.0, 30.0),
            velocity_km_s: Vec3::new(1.0, -2.0, 0.5),
        };
        let propagated =
            propagate_satellite_ecef_constant_velocity(source, Seconds(-0.25), limit(0.25))
                .unwrap();

        assert_eq!(propagated.state.position_km, Vec3::new(9.75, 20.5, 29.875));
        assert_eq!(propagated.state.velocity_km_s, source.velocity_km_s);
    }

    #[test]
    fn interval_beyond_caller_declared_span_is_rejected() {
        let source = SatelliteEcefState {
            position_km: Vec3::new(1.0, 2.0, 3.0),
            velocity_km_s: Vec3::new(0.01, 0.02, 0.03),
        };
        assert_eq!(
            propagate_satellite_ecef_constant_velocity(source, Seconds(0.416), limit(0.4)),
            Err(
                SatelliteEcefPropagationError::MaximumAbsoluteDeltaExceeded {
                    requested_seconds: 0.416,
                    maximum_seconds: 0.4,
                }
            )
        );
    }

    #[test]
    fn non_finite_inputs_and_invalid_limit_fail_closed() {
        let valid = SatelliteEcefState {
            position_km: Vec3::new(1.0, 2.0, 3.0),
            velocity_km_s: Vec3::new(0.01, 0.02, 0.03),
        };
        let non_finite_state = SatelliteEcefState {
            position_km: Vec3::new(f64::NAN, 2.0, 3.0),
            ..valid
        };

        assert_eq!(
            propagate_satellite_ecef_constant_velocity(non_finite_state, Seconds(0.1), limit(0.5)),
            Err(SatelliteEcefPropagationError::NonFiniteSourceState)
        );
        assert_eq!(
            propagate_satellite_ecef_constant_velocity(valid, Seconds(f64::NAN), limit(0.5)),
            Err(SatelliteEcefPropagationError::NonFiniteDelta)
        );
        assert_eq!(
            propagate_satellite_ecef_constant_velocity(valid, Seconds(0.1), limit(0.0)),
            Err(SatelliteEcefPropagationError::InvalidMaximumAbsoluteDelta)
        );
        assert_eq!(
            propagate_satellite_ecef_constant_velocity(valid, Seconds(0.1), limit(f64::INFINITY)),
            Err(SatelliteEcefPropagationError::InvalidMaximumAbsoluteDelta)
        );
    }

    #[test]
    fn finite_inputs_that_overflow_propagated_position_are_rejected() {
        let source = SatelliteEcefState {
            position_km: Vec3::new(f64::MAX, 0.0, 0.0),
            velocity_km_s: Vec3::new(f64::MAX, 0.0, 0.0),
        };
        assert_eq!(
            propagate_satellite_ecef_constant_velocity(source, Seconds(1.0), limit(1.0)),
            Err(SatelliteEcefPropagationError::NonFinitePropagatedPosition)
        );
    }
}
