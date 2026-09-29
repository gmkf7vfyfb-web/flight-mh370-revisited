//! Conditional additional-drag authority for a powered-segment screen.
//!
//! The clean attached-flow polar can imply negative required thrust during a
//! sufficiently steep descent.  That does not by itself make the segment
//! operationally impossible: a real aircraft may be able to add drag.  This
//! module evaluates that narrow question using a caller-declared maximum
//! increment in drag coefficient.  It does not assert that speedbrakes,
//! spoilers, landing gear, windmilling engines, or any other particular source
//! of drag was available or selected.

use serde::{Deserialize, Serialize};
use thiserror::Error;

use crate::{Newtons, PoweredSegmentFeasibility};

/// Limits that must accompany any interpretation of this drag-authority screen.
pub const POWERED_SEGMENT_ADDITIONAL_DRAG_LIMITATIONS: &[&str] = &[
    "maximum additional drag coefficient is caller-declared, not inferred",
    "the calculation represents additive drag only and does not identify a device or configuration",
    "availability, deployment dynamics, lift changes, moments, buffet, and control laws are absent",
];

/// Caller-declared upper bound on drag beyond the selected clean polar.
#[derive(Debug, Clone, Copy, PartialEq, Serialize, Deserialize)]
pub struct DeclaredAdditionalDragAllowance {
    /// Maximum additive drag coefficient, `Delta C_D >= 0`.
    pub maximum_delta_drag_coefficient: f64,
}

/// Independent checks used to form the operational-feasibility result.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
pub struct PoweredSegmentOperationalFeasibilityFlags {
    /// The clean-polar airspeed, bank, and lift-coefficient checks all pass.
    pub clean_polar_numerical_envelope_feasible: bool,
    /// Clean thrust is above its lower bound, or declared extra drag can make it so.
    pub lower_thrust_or_additional_drag_feasible: bool,
    /// Clean required thrust does not exceed maximum available thrust.
    pub upper_thrust_feasible: bool,
    /// Conjunction of the numerical-envelope and both thrust-side checks.
    pub operationally_feasible: bool,
}

/// Result of applying declared additional-drag authority to an existing screen.
#[derive(Debug, Clone, Copy, PartialEq, Serialize, Deserialize)]
pub struct PoweredSegmentOperationalFeasibility {
    /// Midpoint `qS`, the force corresponding to one unit of drag coefficient.
    pub dynamic_pressure_area: Newtons,
    /// Extra drag needed to reach minimum commandable thrust; zero if unnecessary.
    pub required_additional_drag: Newtons,
    /// `required_additional_drag / qS`.
    pub required_delta_drag_coefficient: f64,
    /// Caller-declared maximum additive drag coefficient.
    pub maximum_delta_drag_coefficient: f64,
    /// Maximum extra drag available from the declaration, `qS Delta C_D_max`.
    pub maximum_additional_drag: Newtons,
    pub flags: PoweredSegmentOperationalFeasibilityFlags,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, Error)]
pub enum PoweredSegmentOperationalFeasibilityError {
    #[error("maximum additional drag coefficient must be finite and nonnegative")]
    InvalidMaximumDeltaDragCoefficient,
    #[error("powered-segment result contains invalid values needed by the drag screen")]
    InvalidPoweredSegmentResult,
    #[error("additional-drag calculation produced a non-finite result")]
    NonFiniteResult,
}

/// Evaluate whether declared additional drag can satisfy the lower thrust bound.
///
/// Added drag increases required thrust, so it can only repair a lower-thrust
/// failure.  It cannot repair an upper-thrust failure.  Existing airspeed,
/// bank, and lift-coefficient flags are preserved as independent necessary
/// conditions.  The supplied [`PoweredSegmentFeasibility`] is not modified.
pub fn evaluate_powered_segment_operational_feasibility(
    segment: &PoweredSegmentFeasibility,
    allowance: DeclaredAdditionalDragAllowance,
) -> Result<PoweredSegmentOperationalFeasibility, PoweredSegmentOperationalFeasibilityError> {
    let maximum_delta_cd = allowance.maximum_delta_drag_coefficient;
    if !maximum_delta_cd.is_finite() || maximum_delta_cd < 0.0 {
        return Err(PoweredSegmentOperationalFeasibilityError::InvalidMaximumDeltaDragCoefficient);
    }

    let model = segment.aerodynamic_family.model();
    let dynamic_pressure_area_n = segment.dynamic_pressure_pascals * model.reference_area.0;
    let required_thrust_n = segment.required_thrust.0;
    let lower_margin_n = segment.margins.thrust_above_minimum.0;
    let upper_margin_n = segment.margins.thrust_below_maximum.0;
    let minimum_commandable_thrust_n = required_thrust_n - lower_margin_n;
    let maximum_available_thrust_n = required_thrust_n + upper_margin_n;
    if !segment.dynamic_pressure_pascals.is_finite()
        || segment.dynamic_pressure_pascals <= 0.0
        || !dynamic_pressure_area_n.is_finite()
        || dynamic_pressure_area_n <= 0.0
        || !required_thrust_n.is_finite()
        || !lower_margin_n.is_finite()
        || !upper_margin_n.is_finite()
        || !minimum_commandable_thrust_n.is_finite()
        || !maximum_available_thrust_n.is_finite()
        || minimum_commandable_thrust_n < 0.0
        || maximum_available_thrust_n < minimum_commandable_thrust_n
    {
        return Err(PoweredSegmentOperationalFeasibilityError::InvalidPoweredSegmentResult);
    }

    let required_additional_drag_n = (-lower_margin_n).max(0.0);
    let required_delta_cd = required_additional_drag_n / dynamic_pressure_area_n;
    let maximum_additional_drag_n = dynamic_pressure_area_n * maximum_delta_cd;
    if !required_additional_drag_n.is_finite()
        || !required_delta_cd.is_finite()
        || !maximum_additional_drag_n.is_finite()
    {
        return Err(PoweredSegmentOperationalFeasibilityError::NonFiniteResult);
    }

    let clean_polar_numerical_envelope_feasible = segment.flags.airspeeds_within_numerical_envelope
        && segment.flags.bank_within_numerical_envelope
        && segment.flags.lift_coefficient_within_numerical_envelope;
    let lower_thrust_or_additional_drag_feasible =
        required_additional_drag_n <= maximum_additional_drag_n;
    let upper_thrust_feasible = upper_margin_n >= 0.0;
    let flags = PoweredSegmentOperationalFeasibilityFlags {
        clean_polar_numerical_envelope_feasible,
        lower_thrust_or_additional_drag_feasible,
        upper_thrust_feasible,
        operationally_feasible: clean_polar_numerical_envelope_feasible
            && lower_thrust_or_additional_drag_feasible
            && upper_thrust_feasible,
    };

    Ok(PoweredSegmentOperationalFeasibility {
        dynamic_pressure_area: Newtons(dynamic_pressure_area_n),
        required_additional_drag: Newtons(required_additional_drag_n),
        required_delta_drag_coefficient: required_delta_cd,
        maximum_delta_drag_coefficient: maximum_delta_cd,
        maximum_additional_drag: Newtons(maximum_additional_drag_n),
        flags,
    })
}

#[cfg(test)]
mod tests {
    use mh370_domain::{Degrees, Seconds};

    use super::*;
    use crate::{
        evaluate_powered_segment_feasibility, ConditionalB772AerodynamicFamily,
        DeclaredTotalThrustRange, Kilograms, KilogramsPerCubicMetre, MetresPerSecond,
        PoweredSegmentFeasibilityInput,
    };

    fn input() -> PoweredSegmentFeasibilityInput {
        PoweredSegmentFeasibilityInput {
            aerodynamic_family: ConditionalB772AerodynamicFamily::OpenapV2_6_0AttachedFlow,
            duration: Seconds(60.0),
            start_true_airspeed: MetresPerSecond(230.0),
            end_true_airspeed: MetresPerSecond(230.0),
            start_flight_path_angle: Degrees(0.0),
            end_flight_path_angle: Degrees(0.0),
            midpoint_density: KilogramsPerCubicMetre(0.38),
            mass: Kilograms(210_000.0),
            bank_angle: Degrees(0.0),
            declared_total_thrust: DeclaredTotalThrustRange {
                minimum_commandable: Newtons(0.0),
                maximum_available: Newtons(500_000.0),
            },
        }
    }

    fn evaluate(
        input: PoweredSegmentFeasibilityInput,
        maximum_delta_cd: f64,
    ) -> PoweredSegmentOperationalFeasibility {
        let segment = evaluate_powered_segment_feasibility(input).unwrap();
        evaluate_powered_segment_operational_feasibility(
            &segment,
            DeclaredAdditionalDragAllowance {
                maximum_delta_drag_coefficient: maximum_delta_cd,
            },
        )
        .unwrap()
    }

    #[test]
    fn zero_allowance_is_exactly_equivalent_to_existing_feasibility_flag() {
        let cases = [
            input(),
            {
                let mut value = input();
                value.start_flight_path_angle = Degrees(-5.0);
                value.end_flight_path_angle = Degrees(-5.0);
                value
            },
            {
                let mut value = input();
                value.end_true_airspeed = MetresPerSecond(290.0);
                value.start_flight_path_angle = Degrees(8.0);
                value.end_flight_path_angle = Degrees(8.0);
                value.declared_total_thrust.maximum_available = Newtons(120_000.0);
                value
            },
        ];

        for case in cases {
            let segment = evaluate_powered_segment_feasibility(case).unwrap();
            let result = evaluate_powered_segment_operational_feasibility(
                &segment,
                DeclaredAdditionalDragAllowance {
                    maximum_delta_drag_coefficient: 0.0,
                },
            )
            .unwrap();
            assert_eq!(
                result.flags.operationally_feasible,
                segment.flags.attached_flow_proxy_feasible
            );
        }
    }

    #[test]
    fn sufficient_declared_drag_rescues_lower_thrust_failure_in_steep_descent() {
        let mut steep_descent = input();
        steep_descent.start_flight_path_angle = Degrees(-5.0);
        steep_descent.end_flight_path_angle = Degrees(-5.0);
        let segment = evaluate_powered_segment_feasibility(steep_descent).unwrap();
        assert!(segment.required_thrust.0 < 0.0);
        assert!(!segment.flags.required_thrust_within_declared_range);

        let result = evaluate(steep_descent, 0.1);
        assert!(result.required_additional_drag.0 > 0.0);
        assert!(result.maximum_additional_drag.0 > result.required_additional_drag.0);
        assert!(
            (result.maximum_additional_drag.0 - result.dynamic_pressure_area.0 * 0.1).abs()
                < 1.0e-9
        );
        assert!(
            (result.required_delta_drag_coefficient
                - result.required_additional_drag.0 / result.dynamic_pressure_area.0)
                .abs()
                < 1.0e-15
        );
        assert!(result.flags.lower_thrust_or_additional_drag_feasible);
        assert!(result.flags.upper_thrust_feasible);
        assert!(result.flags.operationally_feasible);
    }

    #[test]
    fn insufficient_declared_drag_does_not_rescue_lower_thrust_failure() {
        let mut steep_descent = input();
        steep_descent.start_flight_path_angle = Degrees(-5.0);
        steep_descent.end_flight_path_angle = Degrees(-5.0);

        let result = evaluate(steep_descent, 0.001);
        assert!(result.maximum_additional_drag.0 < result.required_additional_drag.0);
        assert!(!result.flags.lower_thrust_or_additional_drag_feasible);
        assert!(result.flags.upper_thrust_feasible);
        assert!(!result.flags.operationally_feasible);
    }

    #[test]
    fn upper_thrust_failure_cannot_be_rescued_by_additional_drag() {
        let mut climb = input();
        climb.end_true_airspeed = MetresPerSecond(290.0);
        climb.start_flight_path_angle = Degrees(8.0);
        climb.end_flight_path_angle = Degrees(8.0);
        climb.declared_total_thrust.maximum_available = Newtons(120_000.0);

        let result = evaluate(climb, 1.0);
        assert!(result.flags.lower_thrust_or_additional_drag_feasible);
        assert!(!result.flags.upper_thrust_feasible);
        assert!(!result.flags.operationally_feasible);
    }

    #[test]
    fn malformed_allowance_returns_typed_error() {
        let segment = evaluate_powered_segment_feasibility(input()).unwrap();
        for maximum_delta_drag_coefficient in [f64::NAN, f64::INFINITY, -f64::EPSILON] {
            assert_eq!(
                evaluate_powered_segment_operational_feasibility(
                    &segment,
                    DeclaredAdditionalDragAllowance {
                        maximum_delta_drag_coefficient,
                    },
                )
                .unwrap_err(),
                PoweredSegmentOperationalFeasibilityError::InvalidMaximumDeltaDragCoefficient
            );
        }
    }
}
