//! Deterministic fuel-exhaustion projection at one frozen operating point.
//!
//! This is a computational support projection, not an observation model. It does not
//! choose fuel, tune an exhaustion time, or attach a likelihood. The caller supplies
//! the sampled fuel state and flow scale. The selected operating point is held fixed
//! to an exact upper time bound and the same analytic mass law as powered propagation
//! is evaluated once, with at most one depletion event per feed.

use mh370_domain::{Degrees, Feet, FeetPerMinute, Seconds};
use serde::{Deserialize, Serialize};
use thiserror::Error;

use crate::powered_fuel::{
    advance_powered_fuel_with_flow_scale, validate_segment, validate_shares, validate_state,
    EVENT_TIME_TOLERANCE_S,
};
use crate::{
    EngineFuelFlowShares, PoweredFuelError, PoweredFuelModel, PoweredFuelSegmentInput,
    PoweredFuelState, PoweredFuelStepDiagnostics, PoweredFuelWeather,
};

/// Aircraft/fuel-model inputs held fixed throughout a support projection.
///
/// `state_time` identifies the state from which these values were sampled and must
/// match [`PoweredFuelState::time`]. It prevents accidentally applying a stale
/// operating point to a later particle state.
#[derive(Debug, Clone, Copy, PartialEq, Serialize, Deserialize)]
pub struct FrozenPoweredFuelOperatingPoint {
    pub state_time: Seconds,
    pub pressure_altitude: Feet,
    pub mach: f64,
    pub bank_angle: Degrees,
    pub vertical_speed: FeetPerMinute,
    pub weather: PoweredFuelWeather,
}

/// Diagnostics from the single analytic projection.
#[derive(Debug, Clone, Copy, PartialEq, Serialize, Deserialize)]
pub struct FrozenPoweredFuelProjectionDiagnostics {
    pub powered_fuel_step: PoweredFuelStepDiagnostics,
    pub particle_flow_scale: f64,
    /// Count of left/right feed-depletion events newly encountered by the projection.
    /// Its domain is 0..=2.
    pub feed_depletion_event_count: u8,
}

/// Why the selected fuel law cannot be evaluated at the frozen operating point.
///
/// This is an ordinary projection outcome so a proposal-support calculation can mark
/// the candidate unsupported without treating a model-domain boundary as a software
/// failure.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum FrozenPoweredFuelModelUnavailableReason {
    OutsideSelectedModelDomain,
    InvalidModelConfiguration,
    InvalidFlowEvaluation,
}

/// Result of projecting the sampled feeds to an exact upper bound.
#[derive(Debug, Clone, Copy, PartialEq, Serialize, Deserialize)]
#[serde(tag = "outcome", rename_all = "snake_case")]
pub enum FrozenPoweredFuelProjection {
    ExhaustsAtOrBeforeBound {
        time: Seconds,
        bound: Seconds,
        state: PoweredFuelState,
        diagnostics: FrozenPoweredFuelProjectionDiagnostics,
    },
    NoExhaustionByBound {
        bound: Seconds,
        state: PoweredFuelState,
        diagnostics: FrozenPoweredFuelProjectionDiagnostics,
    },
    /// The input state already records dual-engine exhaustion at or before its time.
    AlreadyExhaustedBeforeStart {
        time: Seconds,
        state: PoweredFuelState,
    },
    FuelModelUnavailable {
        reason: FrozenPoweredFuelModelUnavailableReason,
        state: PoweredFuelState,
    },
}

/// Malformed or inconsistent inputs to a frozen fuel projection.
#[derive(Debug, Error, Clone, Copy, PartialEq)]
pub enum FrozenPoweredFuelProjectionError {
    #[error("invalid initial powered-fuel state: {0}")]
    InvalidInitialState(#[source] PoweredFuelError),
    #[error("invalid engine fuel-flow shares: {0}")]
    InvalidEngineFlowShares(#[source] PoweredFuelError),
    #[error("particle fuel-flow scale must be finite and strictly positive")]
    InvalidParticleFlowScale,
    #[error("projection upper bound must be finite")]
    NonFiniteUpperBound,
    #[error("projection upper bound must be later than the fuel-state time")]
    UpperBoundNotAfterStart,
    #[error("frozen operating-point time does not equal the fuel-state time")]
    OperatingPointTimeMismatch,
    #[error("invalid frozen powered-fuel operating point: {0}")]
    InvalidOperatingPoint(#[source] PoweredFuelError),
    #[error("analytic powered-fuel projection failed: {0}")]
    FuelPropagation(#[source] PoweredFuelError),
    #[error("analytic powered-fuel projection returned an inconsistent exhaustion time")]
    InconsistentExhaustionTime,
}

/// Project dual-engine fuel exhaustion under one frozen operating point.
///
/// The function is deterministic and side-effect free: `initial_state` is copied, and
/// no random draw, likelihood, SATCOM quantity, or target-window adjustment is used.
/// `particle_flow_scale` multiplies the selected fuel law before any declared broad
/// model flow bounds are applied. The projection uses one analytic segment, so its
/// work is constant in the duration to `upper_bound` and it can encounter no more
/// than the two feed-depletion events represented by [`PoweredFuelState`].
pub fn project_frozen_powered_fuel_exhaustion(
    initial_state: PoweredFuelState,
    model: PoweredFuelModel,
    shares: EngineFuelFlowShares,
    operating_point: FrozenPoweredFuelOperatingPoint,
    particle_flow_scale: f64,
    upper_bound: Seconds,
) -> Result<FrozenPoweredFuelProjection, FrozenPoweredFuelProjectionError> {
    validate_state(initial_state).map_err(FrozenPoweredFuelProjectionError::InvalidInitialState)?;
    validate_shares(shares).map_err(FrozenPoweredFuelProjectionError::InvalidEngineFlowShares)?;
    if !particle_flow_scale.is_finite() || particle_flow_scale <= 0.0 {
        return Err(FrozenPoweredFuelProjectionError::InvalidParticleFlowScale);
    }
    if !upper_bound.is_finite() {
        return Err(FrozenPoweredFuelProjectionError::NonFiniteUpperBound);
    }
    if (operating_point.state_time.0 - initial_state.time.0).abs() > EVENT_TIME_TOLERANCE_S {
        return Err(FrozenPoweredFuelProjectionError::OperatingPointTimeMismatch);
    }
    if upper_bound.0 <= initial_state.time.0 + EVENT_TIME_TOLERANCE_S {
        return Err(FrozenPoweredFuelProjectionError::UpperBoundNotAfterStart);
    }

    let segment = PoweredFuelSegmentInput {
        start_time: initial_state.time,
        end_time: upper_bound,
        midpoint_pressure_altitude: operating_point.pressure_altitude,
        midpoint_mach: operating_point.mach,
        midpoint_bank_angle: operating_point.bank_angle,
        midpoint_vertical_speed: operating_point.vertical_speed,
        midpoint_weather: operating_point.weather,
    };
    validate_segment(segment).map_err(FrozenPoweredFuelProjectionError::InvalidOperatingPoint)?;

    if let Some(time) = initial_state.dual_engine_exhaustion_time {
        return Ok(FrozenPoweredFuelProjection::AlreadyExhaustedBeforeStart {
            time,
            state: initial_state,
        });
    }

    let mut projected_state = initial_state;
    let step = match advance_powered_fuel_with_flow_scale(
        &mut projected_state,
        model,
        shares,
        segment,
        particle_flow_scale,
    ) {
        Ok(step) => step,
        Err(PoweredFuelError::OutsideModelDomain) => {
            return Ok(FrozenPoweredFuelProjection::FuelModelUnavailable {
                reason: FrozenPoweredFuelModelUnavailableReason::OutsideSelectedModelDomain,
                state: initial_state,
            });
        }
        Err(PoweredFuelError::InvalidModelConfiguration) => {
            return Ok(FrozenPoweredFuelProjection::FuelModelUnavailable {
                reason: FrozenPoweredFuelModelUnavailableReason::InvalidModelConfiguration,
                state: initial_state,
            });
        }
        Err(PoweredFuelError::InvalidFuelFlow) => {
            return Ok(FrozenPoweredFuelProjection::FuelModelUnavailable {
                reason: FrozenPoweredFuelModelUnavailableReason::InvalidFlowEvaluation,
                state: initial_state,
            });
        }
        Err(error) => {
            return Err(FrozenPoweredFuelProjectionError::FuelPropagation(error));
        }
    };
    let feed_depletion_event_count = u8::from(step.diagnostics.left_exhausted_in_segment)
        + u8::from(step.diagnostics.right_exhausted_in_segment);
    let diagnostics = FrozenPoweredFuelProjectionDiagnostics {
        powered_fuel_step: step.diagnostics,
        particle_flow_scale,
        feed_depletion_event_count,
    };

    match projected_state.dual_engine_exhaustion_time {
        Some(time) if time.0 <= upper_bound.0 + EVENT_TIME_TOLERANCE_S => {
            Ok(FrozenPoweredFuelProjection::ExhaustsAtOrBeforeBound {
                time,
                bound: upper_bound,
                state: projected_state,
                diagnostics,
            })
        }
        Some(_) => Err(FrozenPoweredFuelProjectionError::InconsistentExhaustionTime),
        None => Ok(FrozenPoweredFuelProjection::NoExhaustionByBound {
            bound: upper_bound,
            state: projected_state,
            diagnostics,
        }),
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::{advance_powered_fuel, DeclaredBroadFuelExtension, Kilograms};

    fn state(time: f64, left: f64, right: f64) -> PoweredFuelState {
        PoweredFuelState {
            time: Seconds(time),
            zero_fuel_weight: Kilograms(174_369.0),
            left_usable_feed: Kilograms(left),
            right_usable_feed: Kilograms(right),
            reserved_fuel: Kilograms(0.0),
            unusable_fuel: Kilograms(0.0),
            left_exhaustion_time: None,
            right_exhaustion_time: None,
            dual_engine_exhaustion_time: None,
        }
    }

    fn shares() -> EngineFuelFlowShares {
        EngineFuelFlowShares {
            left: 0.45,
            right: 0.55,
        }
    }

    fn operating_point(time: f64, altitude: f64) -> FrozenPoweredFuelOperatingPoint {
        FrozenPoweredFuelOperatingPoint {
            state_time: Seconds(time),
            pressure_altitude: Feet(altitude),
            mach: 0.81,
            bank_angle: Degrees(7.0),
            vertical_speed: FeetPerMinute(-250.0),
            weather: PoweredFuelWeather {
                static_air_temperature_celsius: -45.0,
                air_density_kg_m3: 0.38,
            },
        }
    }

    fn broad() -> PoweredFuelModel {
        PoweredFuelModel::DeclaredBroadExtension(DeclaredBroadFuelExtension {
            minimum_pressure_altitude: Feet(25_000.0),
            maximum_pressure_altitude: Feet(43_000.0),
            minimum_mach: 0.70,
            maximum_mach: 0.88,
            maximum_absolute_bank: Degrees(45.0),
            reference_mach: 0.82,
            nominal_flow_scale: 1.0,
            mach_log_sensitivity_per_mach: 1.5,
            below_fl350_log_sensitivity_per_1000_ft: 0.04,
            above_fl410_log_sensitivity_per_1000_ft: 0.02,
            bank_induced_drag_fraction: 0.45,
            climb_log_sensitivity_per_1000_ft_min: 0.04,
            descent_log_relief_per_1000_ft_min: 0.015,
            minimum_flow_multiplier: 0.5,
            maximum_flow_multiplier: 2.5,
        })
    }

    fn segment(
        point: FrozenPoweredFuelOperatingPoint,
        end_time: Seconds,
    ) -> PoweredFuelSegmentInput {
        PoweredFuelSegmentInput {
            start_time: point.state_time,
            end_time,
            midpoint_pressure_altitude: point.pressure_altitude,
            midpoint_mach: point.mach,
            midpoint_bank_angle: point.bank_angle,
            midpoint_vertical_speed: point.vertical_speed,
            midpoint_weather: point.weather,
        }
    }

    #[test]
    fn projection_matches_the_existing_exact_law_with_particle_scale() {
        let initial = state(1_000.0, 30.0, 95.0);
        let point = operating_point(initial.time.0, 35_000.0);
        let bound = Seconds(1_300.0);
        let scale = 1.25;

        let projection =
            project_frozen_powered_fuel_exhaustion(initial, broad(), shares(), point, scale, bound)
                .unwrap();

        let PoweredFuelModel::DeclaredBroadExtension(mut scaled_config) = broad() else {
            unreachable!("fixture is the broad model")
        };
        scaled_config.nominal_flow_scale *= scale;
        let mut independently_advanced = initial;
        let direct = advance_powered_fuel(
            &mut independently_advanced,
            PoweredFuelModel::DeclaredBroadExtension(scaled_config),
            shares(),
            segment(point, bound),
        )
        .unwrap();

        let FrozenPoweredFuelProjection::ExhaustsAtOrBeforeBound {
            time,
            state,
            diagnostics,
            ..
        } = projection
        else {
            panic!("small asymmetric feeds must exhaust before the bound")
        };
        assert_eq!(state, independently_advanced);
        assert_eq!(diagnostics.powered_fuel_step, direct.diagnostics);
        assert_eq!(
            time,
            independently_advanced.dual_engine_exhaustion_time.unwrap()
        );
        assert_eq!(diagnostics.particle_flow_scale, scale);
        assert_eq!(diagnostics.feed_depletion_event_count, 2);
    }

    #[test]
    fn projection_is_duration_constant_and_outer_cadence_independent() {
        let initial = state(0.0, 40.0, 80.0);
        let point = operating_point(0.0, 35_000.0);
        let bound = Seconds(400.0);
        let projected = project_frozen_powered_fuel_exhaustion(
            initial,
            PoweredFuelModel::MartinTrent892Lrc,
            shares(),
            point,
            1.0,
            bound,
        )
        .unwrap();
        let FrozenPoweredFuelProjection::ExhaustsAtOrBeforeBound {
            time: projected_time,
            ..
        } = projected
        else {
            panic!("small feeds must exhaust")
        };

        let mut stepped = initial;
        while stepped.time.0 < bound.0 && stepped.dual_engine_exhaustion_time.is_none() {
            let end = Seconds((stepped.time.0 + 7.0).min(bound.0));
            let step_point = FrozenPoweredFuelOperatingPoint {
                state_time: stepped.time,
                ..point
            };
            advance_powered_fuel(
                &mut stepped,
                PoweredFuelModel::MartinTrent892Lrc,
                shares(),
                segment(step_point, end),
            )
            .unwrap();
        }
        assert!((projected_time.0 - stepped.dual_engine_exhaustion_time.unwrap().0).abs() < 1.0e-8);
    }

    #[test]
    fn no_exhaustion_and_preexisting_exhaustion_are_distinct_outcomes() {
        let initial = state(50.0, 10_000.0, 10_000.0);
        let no_exhaustion = project_frozen_powered_fuel_exhaustion(
            initial,
            broad(),
            shares(),
            operating_point(50.0, 35_000.0),
            1.0,
            Seconds(60.0),
        )
        .unwrap();
        let FrozenPoweredFuelProjection::NoExhaustionByBound {
            bound,
            state: projected_state,
            diagnostics,
        } = no_exhaustion
        else {
            panic!("large feeds must remain at a ten-second bound")
        };
        assert_eq!(bound, Seconds(60.0));
        assert_eq!(projected_state.time, bound);
        assert_eq!(diagnostics.feed_depletion_event_count, 0);

        let exhausted = PoweredFuelState {
            time: Seconds(100.0),
            left_usable_feed: Kilograms(0.0),
            right_usable_feed: Kilograms(0.0),
            left_exhaustion_time: Some(Seconds(80.0)),
            right_exhaustion_time: Some(Seconds(90.0)),
            dual_engine_exhaustion_time: Some(Seconds(90.0)),
            ..state(100.0, 0.0, 0.0)
        };
        let already = project_frozen_powered_fuel_exhaustion(
            exhausted,
            PoweredFuelModel::MartinTrent892Lrc,
            shares(),
            operating_point(100.0, 30_000.0),
            1.0,
            Seconds(200.0),
        )
        .unwrap();
        assert_eq!(
            already,
            FrozenPoweredFuelProjection::AlreadyExhaustedBeforeStart {
                time: Seconds(90.0),
                state: exhausted,
            }
        );
    }

    #[test]
    fn selected_model_domain_failure_is_an_ordinary_outcome() {
        let initial = state(0.0, 1_000.0, 1_000.0);
        let result = project_frozen_powered_fuel_exhaustion(
            initial,
            PoweredFuelModel::MartinTrent892Lrc,
            shares(),
            operating_point(0.0, 30_000.0),
            1.0,
            Seconds(60.0),
        )
        .unwrap();
        assert_eq!(
            result,
            FrozenPoweredFuelProjection::FuelModelUnavailable {
                reason: FrozenPoweredFuelModelUnavailableReason::OutsideSelectedModelDomain,
                state: initial,
            }
        );
    }

    #[test]
    fn malformed_scale_bound_operating_point_and_time_desync_are_typed_errors() {
        let initial = state(100.0, 1_000.0, 1_000.0);
        let point = operating_point(100.0, 35_000.0);
        assert_eq!(
            project_frozen_powered_fuel_exhaustion(
                initial,
                broad(),
                shares(),
                point,
                0.0,
                Seconds(200.0),
            ),
            Err(FrozenPoweredFuelProjectionError::InvalidParticleFlowScale)
        );
        assert_eq!(
            project_frozen_powered_fuel_exhaustion(
                initial,
                broad(),
                shares(),
                point,
                1.0,
                Seconds(100.0),
            ),
            Err(FrozenPoweredFuelProjectionError::UpperBoundNotAfterStart)
        );
        assert_eq!(
            project_frozen_powered_fuel_exhaustion(
                initial,
                broad(),
                shares(),
                FrozenPoweredFuelOperatingPoint {
                    state_time: Seconds(101.0),
                    ..point
                },
                1.0,
                Seconds(200.0),
            ),
            Err(FrozenPoweredFuelProjectionError::OperatingPointTimeMismatch)
        );
        assert_eq!(
            project_frozen_powered_fuel_exhaustion(
                initial,
                broad(),
                shares(),
                FrozenPoweredFuelOperatingPoint {
                    mach: f64::NAN,
                    ..point
                },
                1.0,
                Seconds(200.0),
            ),
            Err(FrozenPoweredFuelProjectionError::InvalidOperatingPoint(
                PoweredFuelError::NonFinite {
                    field: "midpoint Mach"
                }
            ))
        );
    }

    #[test]
    fn projection_does_not_mutate_the_callers_state() {
        let initial = state(0.0, 30.0, 95.0);
        let retained = initial;
        let first = project_frozen_powered_fuel_exhaustion(
            initial,
            broad(),
            shares(),
            operating_point(0.0, 35_000.0),
            0.9,
            Seconds(300.0),
        )
        .unwrap();
        let second = project_frozen_powered_fuel_exhaustion(
            initial,
            broad(),
            shares(),
            operating_point(0.0, 35_000.0),
            0.9,
            Seconds(300.0),
        )
        .unwrap();
        assert_eq!(initial, retained);
        assert_eq!(first, second);
    }
}
