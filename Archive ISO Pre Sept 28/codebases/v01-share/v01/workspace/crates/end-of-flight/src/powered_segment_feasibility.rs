//! Attached-flow point-mass feasibility for one powered-flight segment.
//!
//! This calculation inverts the longitudinal and vertical-plane point-mass
//! equations at the segment midpoint.  It uses one explicitly selected public
//! OpenAP B772 parabolic polar and a caller-declared total-thrust range.  It is
//! not a calibrated B777-200ER/Trent 892 performance or terminal-flight model.
//! The two published polar families remain separate conditional alternatives.

use mh370_domain::{Degrees, Seconds};
use serde::{Deserialize, Serialize};
use thiserror::Error;

use crate::{
    ConditionalB772AerodynamicFamily, Kilograms, KilogramsPerCubicMetre, MetresPerSecond, Newtons,
};

const STANDARD_GRAVITY_M_S2: f64 = 9.806_65;

/// Limits that must accompany any interpretation of this feasibility screen.
pub const POWERED_SEGMENT_FEASIBILITY_LIMITATIONS: &[&str] = &[
    "OpenAP B772 attached-flow polar; not calibrated B777-200ER or Trent 892 data",
    "caller-declared thrust range is a conditional proxy, not an inferred engine envelope",
    "midpoint constant-rate inversion requires subdivision across material state changes",
    "numerical lift-coefficient bounds are not a validated stall or high-angle-of-attack model",
    "heading dynamics, control-law authority, buffet, windmilling, and structural limits are absent",
];

/// Caller-declared total thrust available from all operating engines.
///
/// The lower value is the minimum commandable thrust represented by the
/// caller's model; the upper value is its maximum available thrust.  Both are
/// forces along the true-airspeed vector.
#[derive(Debug, Clone, Copy, PartialEq, Serialize, Deserialize)]
pub struct DeclaredTotalThrustRange {
    pub minimum_commandable: Newtons,
    pub maximum_available: Newtons,
}

/// Endpoints and midpoint conditions for one constant-rate segment.
#[derive(Debug, Clone, Copy, PartialEq, Serialize, Deserialize)]
pub struct PoweredSegmentFeasibilityInput {
    pub aerodynamic_family: ConditionalB772AerodynamicFamily,
    pub duration: Seconds,
    pub start_true_airspeed: MetresPerSecond,
    pub end_true_airspeed: MetresPerSecond,
    pub start_flight_path_angle: Degrees,
    pub end_flight_path_angle: Degrees,
    pub midpoint_density: KilogramsPerCubicMetre,
    pub mass: Kilograms,
    pub bank_angle: Degrees,
    pub declared_total_thrust: DeclaredTotalThrustRange,
}

/// Signed margins; a nonnegative value is inside the corresponding bound.
#[derive(Debug, Clone, Copy, PartialEq, Serialize, Deserialize)]
pub struct PoweredSegmentFeasibilityMargins {
    pub start_airspeed_above_minimum: MetresPerSecond,
    pub start_airspeed_below_maximum: MetresPerSecond,
    pub end_airspeed_above_minimum: MetresPerSecond,
    pub end_airspeed_below_maximum: MetresPerSecond,
    pub bank_below_maximum: Degrees,
    pub lift_coefficient_above_minimum: f64,
    pub lift_coefficient_below_maximum: f64,
    pub thrust_above_minimum: Newtons,
    pub thrust_below_maximum: Newtons,
}

/// Individual checks and their conjunction.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
pub struct PoweredSegmentFeasibilityFlags {
    pub airspeeds_within_numerical_envelope: bool,
    pub bank_within_numerical_envelope: bool,
    pub lift_coefficient_within_numerical_envelope: bool,
    pub required_thrust_within_declared_range: bool,
    pub attached_flow_proxy_feasible: bool,
}

/// Midpoint inversion result for one segment.
#[derive(Debug, Clone, Copy, PartialEq, Serialize, Deserialize)]
pub struct PoweredSegmentFeasibility {
    pub aerodynamic_family: ConditionalB772AerodynamicFamily,
    pub midpoint_true_airspeed: MetresPerSecond,
    pub midpoint_flight_path_angle: Degrees,
    pub true_airspeed_rate_metres_per_second_squared: f64,
    pub flight_path_angle_rate_radians_per_second: f64,
    pub dynamic_pressure_pascals: f64,
    pub required_lift: Newtons,
    pub required_lift_load_factor: f64,
    pub lift_coefficient: f64,
    pub drag_coefficient: f64,
    pub drag: Newtons,
    pub required_thrust: Newtons,
    pub margins: PoweredSegmentFeasibilityMargins,
    pub flags: PoweredSegmentFeasibilityFlags,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, Error)]
pub enum PoweredSegmentFeasibilityError {
    #[error("duration must be finite and strictly positive")]
    InvalidDuration,
    #[error("endpoint true airspeeds must be finite and strictly positive")]
    InvalidTrueAirspeed,
    #[error("flight-path angles must be finite and strictly between -90 and 90 degrees")]
    InvalidFlightPathAngle,
    #[error("midpoint density must be finite and strictly positive")]
    InvalidDensity,
    #[error("mass must be finite and strictly positive")]
    InvalidMass,
    #[error("bank angle must be finite and strictly between -90 and 90 degrees")]
    InvalidBankAngle,
    #[error("declared thrust bounds must be finite, nonnegative, and ordered")]
    InvalidDeclaredThrustRange,
    #[error("powered-segment calculation produced a non-finite result")]
    NonFiniteResult,
}

/// Invert the attached-flow point-mass equations at the segment midpoint.
///
/// With flight-path angle `gamma` and bank `phi`, the calculation uses
/// `T - D - m g sin(gamma) = m V_dot` and
/// `L cos(phi) - m g cos(gamma) = m V gamma_dot`.
pub fn evaluate_powered_segment_feasibility(
    input: PoweredSegmentFeasibilityInput,
) -> Result<PoweredSegmentFeasibility, PoweredSegmentFeasibilityError> {
    validate_input(input)?;

    let model = input.aerodynamic_family.model();
    let duration_s = input.duration.0;
    let midpoint_speed_m_s = 0.5 * (input.start_true_airspeed.0 + input.end_true_airspeed.0);
    let midpoint_gamma_rad = 0.5
        * (input.start_flight_path_angle.to_radians() + input.end_flight_path_angle.to_radians());
    let speed_rate_m_s2 = (input.end_true_airspeed.0 - input.start_true_airspeed.0) / duration_s;
    let gamma_rate_rad_s = (input.end_flight_path_angle.to_radians()
        - input.start_flight_path_angle.to_radians())
        / duration_s;
    let bank_rad = input.bank_angle.to_radians();
    let mass_kg = input.mass.0;

    let dynamic_pressure_pa = 0.5 * input.midpoint_density.0 * midpoint_speed_m_s.powi(2);
    let dynamic_pressure_area_n = dynamic_pressure_pa * model.reference_area.0;
    let required_lift_n = mass_kg
        * (midpoint_speed_m_s * gamma_rate_rad_s
            + STANDARD_GRAVITY_M_S2 * midpoint_gamma_rad.cos())
        / bank_rad.cos();
    let lift_coefficient = required_lift_n / dynamic_pressure_area_n;
    let drag_coefficient =
        model.zero_lift_drag_coefficient + model.induced_drag_factor * lift_coefficient.powi(2);
    let drag_n = dynamic_pressure_area_n * drag_coefficient;
    let required_thrust_n =
        mass_kg * (speed_rate_m_s2 + STANDARD_GRAVITY_M_S2 * midpoint_gamma_rad.sin()) + drag_n;

    let margins = PoweredSegmentFeasibilityMargins {
        start_airspeed_above_minimum: MetresPerSecond(
            input.start_true_airspeed.0 - model.minimum_true_airspeed.0,
        ),
        start_airspeed_below_maximum: MetresPerSecond(
            model.maximum_true_airspeed.0 - input.start_true_airspeed.0,
        ),
        end_airspeed_above_minimum: MetresPerSecond(
            input.end_true_airspeed.0 - model.minimum_true_airspeed.0,
        ),
        end_airspeed_below_maximum: MetresPerSecond(
            model.maximum_true_airspeed.0 - input.end_true_airspeed.0,
        ),
        bank_below_maximum: Degrees(model.maximum_bank_angle.0 - input.bank_angle.0.abs()),
        lift_coefficient_above_minimum: lift_coefficient - model.minimum_lift_coefficient,
        lift_coefficient_below_maximum: model.maximum_lift_coefficient - lift_coefficient,
        thrust_above_minimum: Newtons(
            required_thrust_n - input.declared_total_thrust.minimum_commandable.0,
        ),
        thrust_below_maximum: Newtons(
            input.declared_total_thrust.maximum_available.0 - required_thrust_n,
        ),
    };
    let airspeeds_within_numerical_envelope = margins.start_airspeed_above_minimum.0 >= 0.0
        && margins.start_airspeed_below_maximum.0 >= 0.0
        && margins.end_airspeed_above_minimum.0 >= 0.0
        && margins.end_airspeed_below_maximum.0 >= 0.0;
    let bank_within_numerical_envelope = margins.bank_below_maximum.0 >= 0.0;
    let lift_coefficient_within_numerical_envelope = margins.lift_coefficient_above_minimum >= 0.0
        && margins.lift_coefficient_below_maximum >= 0.0;
    let required_thrust_within_declared_range =
        margins.thrust_above_minimum.0 >= 0.0 && margins.thrust_below_maximum.0 >= 0.0;
    let flags = PoweredSegmentFeasibilityFlags {
        airspeeds_within_numerical_envelope,
        bank_within_numerical_envelope,
        lift_coefficient_within_numerical_envelope,
        required_thrust_within_declared_range,
        attached_flow_proxy_feasible: airspeeds_within_numerical_envelope
            && bank_within_numerical_envelope
            && lift_coefficient_within_numerical_envelope
            && required_thrust_within_declared_range,
    };

    let finite = [
        midpoint_speed_m_s,
        midpoint_gamma_rad,
        speed_rate_m_s2,
        gamma_rate_rad_s,
        dynamic_pressure_pa,
        required_lift_n,
        lift_coefficient,
        drag_coefficient,
        drag_n,
        required_thrust_n,
        margins.start_airspeed_above_minimum.0,
        margins.start_airspeed_below_maximum.0,
        margins.end_airspeed_above_minimum.0,
        margins.end_airspeed_below_maximum.0,
        margins.bank_below_maximum.0,
        margins.lift_coefficient_above_minimum,
        margins.lift_coefficient_below_maximum,
        margins.thrust_above_minimum.0,
        margins.thrust_below_maximum.0,
    ]
    .into_iter()
    .all(f64::is_finite);
    if !finite {
        return Err(PoweredSegmentFeasibilityError::NonFiniteResult);
    }

    Ok(PoweredSegmentFeasibility {
        aerodynamic_family: input.aerodynamic_family,
        midpoint_true_airspeed: MetresPerSecond(midpoint_speed_m_s),
        midpoint_flight_path_angle: Degrees(midpoint_gamma_rad.to_degrees()),
        true_airspeed_rate_metres_per_second_squared: speed_rate_m_s2,
        flight_path_angle_rate_radians_per_second: gamma_rate_rad_s,
        dynamic_pressure_pascals: dynamic_pressure_pa,
        required_lift: Newtons(required_lift_n),
        required_lift_load_factor: required_lift_n / (mass_kg * STANDARD_GRAVITY_M_S2),
        lift_coefficient,
        drag_coefficient,
        drag: Newtons(drag_n),
        required_thrust: Newtons(required_thrust_n),
        margins,
        flags,
    })
}

fn validate_input(
    input: PoweredSegmentFeasibilityInput,
) -> Result<(), PoweredSegmentFeasibilityError> {
    if !input.duration.is_finite() || input.duration.0 <= 0.0 {
        return Err(PoweredSegmentFeasibilityError::InvalidDuration);
    }
    if !input.start_true_airspeed.is_finite()
        || !input.end_true_airspeed.is_finite()
        || input.start_true_airspeed.0 <= 0.0
        || input.end_true_airspeed.0 <= 0.0
    {
        return Err(PoweredSegmentFeasibilityError::InvalidTrueAirspeed);
    }
    if !input.start_flight_path_angle.is_finite()
        || !input.end_flight_path_angle.is_finite()
        || input.start_flight_path_angle.0.abs() >= 90.0
        || input.end_flight_path_angle.0.abs() >= 90.0
    {
        return Err(PoweredSegmentFeasibilityError::InvalidFlightPathAngle);
    }
    if !input.midpoint_density.is_finite() || input.midpoint_density.0 <= 0.0 {
        return Err(PoweredSegmentFeasibilityError::InvalidDensity);
    }
    if !input.mass.is_finite() || input.mass.0 <= 0.0 {
        return Err(PoweredSegmentFeasibilityError::InvalidMass);
    }
    if !input.bank_angle.is_finite() || input.bank_angle.0.abs() >= 90.0 {
        return Err(PoweredSegmentFeasibilityError::InvalidBankAngle);
    }
    let thrust = input.declared_total_thrust;
    if !thrust.minimum_commandable.is_finite()
        || !thrust.maximum_available.is_finite()
        || thrust.minimum_commandable.0 < 0.0
        || thrust.maximum_available.0 < thrust.minimum_commandable.0
    {
        return Err(PoweredSegmentFeasibilityError::InvalidDeclaredThrustRange);
    }
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;

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

    #[test]
    fn independent_straight_level_equilibrium_matches_parabolic_polar() {
        let input = input();
        let result = evaluate_powered_segment_feasibility(input).unwrap();
        let model = input.aerodynamic_family.model();
        let q_s = 0.5 * input.midpoint_density.0 * 230.0_f64.powi(2) * model.reference_area.0;
        let expected_lift = input.mass.0 * STANDARD_GRAVITY_M_S2;
        let expected_cl = expected_lift / q_s;
        let expected_cd =
            model.zero_lift_drag_coefficient + model.induced_drag_factor * expected_cl.powi(2);
        let expected_drag = q_s * expected_cd;

        assert!((result.required_lift.0 - expected_lift).abs() < 1.0e-8);
        assert!((result.lift_coefficient - expected_cl).abs() < 1.0e-12);
        assert!((result.drag.0 - expected_drag).abs() < 1.0e-8);
        assert!((result.required_thrust.0 - expected_drag).abs() < 1.0e-8);
        assert_eq!(result.required_lift_load_factor, 1.0);
        assert!(result.flags.attached_flow_proxy_feasible);
    }

    #[test]
    fn aggressive_climb_and_acceleration_exceeds_declared_thrust() {
        let mut input = input();
        input.end_true_airspeed = MetresPerSecond(290.0);
        input.start_flight_path_angle = Degrees(8.0);
        input.end_flight_path_angle = Degrees(8.0);
        input.declared_total_thrust.maximum_available = Newtons(120_000.0);

        let result = evaluate_powered_segment_feasibility(input).unwrap();
        assert!(result.required_thrust.0 > 120_000.0);
        assert!(!result.flags.required_thrust_within_declared_range);
        assert!(result.margins.thrust_below_maximum.0 < 0.0);
        assert!(!result.flags.attached_flow_proxy_feasible);
    }

    #[test]
    fn midpoint_cadence_refinement_is_finite_and_convergent() {
        fn average_required_thrust(step_s: f64) -> f64 {
            let total_s = 600.0;
            let count = (total_s / step_s) as usize;
            let mut sum = 0.0;
            for index in 0..count {
                let t0 = index as f64 * step_s;
                let t1 = t0 + step_s;
                let mut segment = input();
                segment.duration = Seconds(step_s);
                segment.start_true_airspeed = MetresPerSecond(180.0 + 80.0 * t0 / total_s);
                segment.end_true_airspeed = MetresPerSecond(180.0 + 80.0 * t1 / total_s);
                segment.start_flight_path_angle = Degrees(2.0);
                segment.end_flight_path_angle = Degrees(2.0);
                sum += evaluate_powered_segment_feasibility(segment)
                    .unwrap()
                    .required_thrust
                    .0;
            }
            sum / count as f64
        }

        let reference = average_required_thrust(1.0);
        let value_60 = average_required_thrust(60.0);
        let value_30 = average_required_thrust(30.0);
        let value_15 = average_required_thrust(15.0);
        assert!([reference, value_60, value_30, value_15]
            .into_iter()
            .all(f64::is_finite));
        assert!((value_30 - reference).abs() < (value_60 - reference).abs());
        assert!((value_15 - reference).abs() < (value_30 - reference).abs());
        assert!((value_15 - reference).abs() / reference.abs() < 1.0e-4);
    }

    #[test]
    fn malformed_physical_inputs_return_typed_errors() {
        let mut bad = input();
        bad.duration = Seconds(0.0);
        assert_eq!(
            evaluate_powered_segment_feasibility(bad).unwrap_err(),
            PoweredSegmentFeasibilityError::InvalidDuration
        );

        let mut bad = input();
        bad.declared_total_thrust.minimum_commandable = Newtons(2.0);
        bad.declared_total_thrust.maximum_available = Newtons(1.0);
        assert_eq!(
            evaluate_powered_segment_feasibility(bad).unwrap_err(),
            PoweredSegmentFeasibilityError::InvalidDeclaredThrustRange
        );
    }

    #[test]
    fn polar_families_are_not_averaged() {
        let current = evaluate_powered_segment_feasibility(input()).unwrap();
        let mut published_input = input();
        published_input.aerodynamic_family =
            ConditionalB772AerodynamicFamily::OpenapPublished2020AttachedFlow;
        let published = evaluate_powered_segment_feasibility(published_input).unwrap();

        assert_eq!(
            current.aerodynamic_family,
            ConditionalB772AerodynamicFamily::OpenapV2_6_0AttachedFlow
        );
        assert_eq!(
            published.aerodynamic_family,
            ConditionalB772AerodynamicFamily::OpenapPublished2020AttachedFlow
        );
        assert!(published.required_thrust.0 > current.required_thrust.0);
    }
}
