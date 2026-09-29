//! Transparent point-mass feasibility calculations for a short flight segment.
//!
//! This is a generic kinematic screen, not a Boeing 777 flight-dynamics or
//! loads model. It assumes constant horizontal-speed magnitude, constant
//! earth-vertical acceleration, constant turn rate, a local flat-earth frame,
//! and standard gravity. The declared horizontal-speed basis is used
//! consistently for path angles, turn acceleration, and the energy-equivalent
//! force calculation.
//!
//! With [`HorizontalSpeedBasis::TrueAirspeed`], those results are air-relative
//! proxies and require stationary or separately accounted-for wind to be read
//! as inertial mechanics. With [`HorizontalSpeedBasis::GroundSpeed`], the
//! kinematics and energy are earth-relative, but the equivalent
//! drag-minus-thrust remains an energy-equivalent quantity rather than an
//! aerodynamic force estimate.

use mh370_domain::{Degrees, Feet, FeetPerMinute, Knots, Seconds};
use serde::{Deserialize, Serialize};
use thiserror::Error;

const STANDARD_GRAVITY_METERS_PER_SECOND_SQUARED: f64 = 9.806_65;
const METERS_PER_SECOND_PER_KNOT: f64 = 1_852.0 / 3_600.0;
const METERS_PER_SECOND_PER_FOOT_PER_MINUTE: f64 = 0.304_8 / 60.0;
const FEET_PER_METER: f64 = 1.0 / 0.304_8;

macro_rules! scalar_unit {
    ($name:ident) => {
        #[derive(Debug, Clone, Copy, Default, PartialEq, PartialOrd, Serialize, Deserialize)]
        #[serde(transparent)]
        pub struct $name(pub f64);

        impl $name {
            pub const fn new(value: f64) -> Self {
                Self(value)
            }

            pub const fn value(self) -> f64 {
                self.0
            }

            pub fn is_finite(self) -> bool {
                self.0.is_finite()
            }
        }
    };
}

scalar_unit!(DegreesPerSecond);
scalar_unit!(MetersPerSecondSquared);
scalar_unit!(SpecificLoadG);
scalar_unit!(JoulesPerKilogram);
scalar_unit!(WattsPerKilogram);

/// Reference used for the supplied horizontal-speed magnitude.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum HorizontalSpeedBasis {
    /// Horizontal component of true airspeed.
    TrueAirspeed,
    /// Horizontal ground-speed magnitude in the local earth frame.
    GroundSpeed,
}

/// Classification against the caller's generic total-specific-load threshold.
///
/// This classification makes no aircraft-type-specific structural, handling,
/// or certification claim.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum GenericLoadClassification {
    WithinInclusiveThreshold,
    ExceedsThreshold,
}

/// Inputs for one constant-acceleration, constant-turn-rate segment.
///
/// Vertical speeds and accelerations are positive upward. Positive turn rate
/// produces positive lateral acceleration. The total-load threshold is in
/// multiples of standard gravity and is inclusive.
#[derive(Debug, Clone, Copy, PartialEq, Serialize, Deserialize)]
pub struct ThreeDofFeasibilityInput {
    pub horizontal_speed: Knots,
    pub horizontal_speed_basis: HorizontalSpeedBasis,
    pub initial_vertical_speed: FeetPerMinute,
    pub final_vertical_speed: FeetPerMinute,
    pub elapsed_time: Seconds,
    pub turn_rate: DegreesPerSecond,
    pub generic_total_specific_load_threshold: SpecificLoadG,
}

/// Inertial acceleration components evaluated at the segment midpoint.
///
/// `flight_path_tangential` is positive along the midpoint velocity.
/// `vertical_plane_normal_upward` is positive toward the upward normal to that
/// velocity. `horizontal_turn_lateral` is positive with positive turn rate.
#[derive(Debug, Clone, Copy, PartialEq, Serialize, Deserialize)]
pub struct ThreeDofAccelerationComponents {
    pub earth_vertical_upward: MetersPerSecondSquared,
    pub flight_path_tangential: MetersPerSecondSquared,
    pub vertical_plane_normal_upward: MetersPerSecondSquared,
    pub horizontal_turn_lateral: MetersPerSecondSquared,
}

/// Results of the generic three-degree-of-freedom feasibility screen.
#[derive(Debug, Clone, Copy, PartialEq, Serialize, Deserialize)]
pub struct ThreeDofFeasibility {
    pub horizontal_speed_basis: HorizontalSpeedBasis,
    /// Positive for net descent and negative for net climb.
    pub altitude_loss: Feet,
    pub initial_flight_path_angle: Degrees,
    pub final_flight_path_angle: Degrees,
    pub acceleration: ThreeDofAccelerationComponents,
    /// Signed upward proper acceleration divided by standard gravity.
    pub earth_up_specific_load: SpecificLoadG,
    /// Magnitude of proper acceleration divided by standard gravity.
    pub total_specific_load: SpecificLoadG,
    /// Change in kinetic plus gravitational potential energy per unit mass.
    pub mechanical_energy_change: JoulesPerKilogram,
    /// Positive when mechanical energy is dissipated over the segment.
    pub dissipative_power: WattsPerKilogram,
    /// Energy-equivalent `(drag - thrust) / mass` along midpoint velocity.
    pub equivalent_drag_minus_thrust_per_mass: MetersPerSecondSquared,
    pub generic_total_specific_load_threshold: SpecificLoadG,
    pub generic_load_classification: GenericLoadClassification,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, Error)]
pub enum ThreeDofFeasibilityError {
    #[error("horizontal speed must be finite and strictly positive")]
    InvalidHorizontalSpeed,
    #[error("vertical speeds must be finite")]
    InvalidVerticalSpeed,
    #[error("elapsed time must be finite and strictly positive")]
    InvalidElapsedTime,
    #[error("turn rate must be finite")]
    InvalidTurnRate,
    #[error("generic total-specific-load threshold must be finite and non-negative")]
    InvalidGenericLoadThreshold,
    #[error("three-DoF calculation produced a non-finite result")]
    NonFiniteResult,
}

/// Evaluate a short segment with constant horizontal-speed magnitude, constant
/// earth-vertical acceleration, and constant turn rate.
pub fn evaluate_three_dof_feasibility(
    input: ThreeDofFeasibilityInput,
) -> Result<ThreeDofFeasibility, ThreeDofFeasibilityError> {
    if !input.horizontal_speed.is_finite() || input.horizontal_speed.0 <= 0.0 {
        return Err(ThreeDofFeasibilityError::InvalidHorizontalSpeed);
    }
    if !input.initial_vertical_speed.is_finite() || !input.final_vertical_speed.is_finite() {
        return Err(ThreeDofFeasibilityError::InvalidVerticalSpeed);
    }
    if !input.elapsed_time.is_finite() || input.elapsed_time.0 <= 0.0 {
        return Err(ThreeDofFeasibilityError::InvalidElapsedTime);
    }
    if !input.turn_rate.is_finite() {
        return Err(ThreeDofFeasibilityError::InvalidTurnRate);
    }
    if !input.generic_total_specific_load_threshold.is_finite()
        || input.generic_total_specific_load_threshold.0 < 0.0
    {
        return Err(ThreeDofFeasibilityError::InvalidGenericLoadThreshold);
    }

    let horizontal_speed = input.horizontal_speed.0 * METERS_PER_SECOND_PER_KNOT;
    let initial_vertical_speed =
        input.initial_vertical_speed.0 * METERS_PER_SECOND_PER_FOOT_PER_MINUTE;
    let final_vertical_speed = input.final_vertical_speed.0 * METERS_PER_SECOND_PER_FOOT_PER_MINUTE;
    let elapsed_time = input.elapsed_time.0;
    let mean_vertical_speed = 0.5 * (initial_vertical_speed + final_vertical_speed);
    let altitude_change = mean_vertical_speed * elapsed_time;
    let altitude_loss_feet = -altitude_change * FEET_PER_METER;
    let earth_vertical_acceleration =
        (final_vertical_speed - initial_vertical_speed) / elapsed_time;

    let initial_flight_path_angle = initial_vertical_speed.atan2(horizontal_speed);
    let final_flight_path_angle = final_vertical_speed.atan2(horizontal_speed);
    let midpoint_flight_path_angle = mean_vertical_speed.atan2(horizontal_speed);

    let turn_rate = input.turn_rate.0.to_radians();
    let lateral_acceleration = horizontal_speed * turn_rate;
    let tangential_acceleration = earth_vertical_acceleration * midpoint_flight_path_angle.sin();
    let vertical_plane_normal_acceleration =
        earth_vertical_acceleration * midpoint_flight_path_angle.cos();

    let earth_up_proper_acceleration =
        earth_vertical_acceleration + STANDARD_GRAVITY_METERS_PER_SECOND_SQUARED;
    let earth_up_specific_load =
        earth_up_proper_acceleration / STANDARD_GRAVITY_METERS_PER_SECOND_SQUARED;
    let total_specific_load = earth_up_proper_acceleration.hypot(lateral_acceleration)
        / STANDARD_GRAVITY_METERS_PER_SECOND_SQUARED;

    let vertical_kinetic_energy_change = 0.5
        * (final_vertical_speed - initial_vertical_speed)
        * (final_vertical_speed + initial_vertical_speed);
    let mechanical_energy_change = vertical_kinetic_energy_change
        + STANDARD_GRAVITY_METERS_PER_SECOND_SQUARED * altitude_change;
    let dissipative_power = -mechanical_energy_change / elapsed_time;
    let midpoint_speed = horizontal_speed.hypot(mean_vertical_speed);
    let equivalent_drag_minus_thrust_per_mass = dissipative_power / midpoint_speed;

    let finite_results = [
        altitude_loss_feet,
        earth_vertical_acceleration,
        initial_flight_path_angle,
        final_flight_path_angle,
        tangential_acceleration,
        vertical_plane_normal_acceleration,
        lateral_acceleration,
        earth_up_specific_load,
        total_specific_load,
        mechanical_energy_change,
        dissipative_power,
        equivalent_drag_minus_thrust_per_mass,
    ]
    .into_iter()
    .all(f64::is_finite);
    if !finite_results {
        return Err(ThreeDofFeasibilityError::NonFiniteResult);
    }

    let generic_load_classification =
        if total_specific_load <= input.generic_total_specific_load_threshold.0 {
            GenericLoadClassification::WithinInclusiveThreshold
        } else {
            GenericLoadClassification::ExceedsThreshold
        };

    Ok(ThreeDofFeasibility {
        horizontal_speed_basis: input.horizontal_speed_basis,
        altitude_loss: Feet(altitude_loss_feet),
        initial_flight_path_angle: Degrees(initial_flight_path_angle.to_degrees()),
        final_flight_path_angle: Degrees(final_flight_path_angle.to_degrees()),
        acceleration: ThreeDofAccelerationComponents {
            earth_vertical_upward: MetersPerSecondSquared(earth_vertical_acceleration),
            flight_path_tangential: MetersPerSecondSquared(tangential_acceleration),
            vertical_plane_normal_upward: MetersPerSecondSquared(
                vertical_plane_normal_acceleration,
            ),
            horizontal_turn_lateral: MetersPerSecondSquared(lateral_acceleration),
        },
        earth_up_specific_load: SpecificLoadG(earth_up_specific_load),
        total_specific_load: SpecificLoadG(total_specific_load),
        mechanical_energy_change: JoulesPerKilogram(mechanical_energy_change),
        dissipative_power: WattsPerKilogram(dissipative_power),
        equivalent_drag_minus_thrust_per_mass: MetersPerSecondSquared(
            equivalent_drag_minus_thrust_per_mass,
        ),
        generic_total_specific_load_threshold: input.generic_total_specific_load_threshold,
        generic_load_classification,
    })
}

#[cfg(test)]
mod tests {
    use approx::assert_abs_diff_eq;

    use super::*;

    const TEST_GRAVITY: f64 = 9.806_65;

    fn knots_from_meters_per_second(value: f64) -> Knots {
        Knots(value / (1_852.0 / 3_600.0))
    }

    fn feet_per_minute_from_meters_per_second(value: f64) -> FeetPerMinute {
        FeetPerMinute(value / (0.304_8 / 60.0))
    }

    fn input(
        horizontal_speed_meters_per_second: f64,
        initial_vertical_speed_meters_per_second: f64,
        final_vertical_speed_meters_per_second: f64,
        elapsed_seconds: f64,
        turn_rate_degrees_per_second: f64,
        threshold_g: f64,
    ) -> ThreeDofFeasibilityInput {
        ThreeDofFeasibilityInput {
            horizontal_speed: knots_from_meters_per_second(horizontal_speed_meters_per_second),
            horizontal_speed_basis: HorizontalSpeedBasis::TrueAirspeed,
            initial_vertical_speed: feet_per_minute_from_meters_per_second(
                initial_vertical_speed_meters_per_second,
            ),
            final_vertical_speed: feet_per_minute_from_meters_per_second(
                final_vertical_speed_meters_per_second,
            ),
            elapsed_time: Seconds(elapsed_seconds),
            turn_rate: DegreesPerSecond(turn_rate_degrees_per_second),
            generic_total_specific_load_threshold: SpecificLoadG(threshold_g),
        }
    }

    #[test]
    fn level_unaccelerated_flight_is_one_g_with_no_energy_change() {
        let result =
            evaluate_three_dof_feasibility(input(200.0, 0.0, 0.0, 10.0, 0.0, 1.0)).unwrap();

        assert_abs_diff_eq!(result.altitude_loss.0, 0.0, epsilon = 1e-12);
        assert_abs_diff_eq!(result.initial_flight_path_angle.0, 0.0, epsilon = 1e-12);
        assert_abs_diff_eq!(result.final_flight_path_angle.0, 0.0, epsilon = 1e-12);
        assert_abs_diff_eq!(
            result.acceleration.earth_vertical_upward.0,
            0.0,
            epsilon = 1e-12
        );
        assert_abs_diff_eq!(
            result.acceleration.flight_path_tangential.0,
            0.0,
            epsilon = 1e-12
        );
        assert_abs_diff_eq!(
            result.acceleration.vertical_plane_normal_upward.0,
            0.0,
            epsilon = 1e-12
        );
        assert_abs_diff_eq!(
            result.acceleration.horizontal_turn_lateral.0,
            0.0,
            epsilon = 1e-12
        );
        assert_abs_diff_eq!(result.earth_up_specific_load.0, 1.0, epsilon = 1e-12);
        assert_abs_diff_eq!(result.total_specific_load.0, 1.0, epsilon = 1e-12);
        assert_abs_diff_eq!(result.mechanical_energy_change.0, 0.0, epsilon = 1e-12);
        assert_abs_diff_eq!(result.dissipative_power.0, 0.0, epsilon = 1e-12);
        assert_abs_diff_eq!(
            result.equivalent_drag_minus_thrust_per_mass.0,
            0.0,
            epsilon = 1e-12
        );
        assert_eq!(
            result.generic_load_classification,
            GenericLoadClassification::WithinInclusiveThreshold
        );
    }

    #[test]
    fn ballistic_free_fall_conserves_mechanical_energy_and_has_zero_specific_load() {
        let elapsed = 2.0;
        let final_vertical_speed = -TEST_GRAVITY * elapsed;
        let result = evaluate_three_dof_feasibility(input(
            100.0,
            0.0,
            final_vertical_speed,
            elapsed,
            0.0,
            1.0,
        ))
        .unwrap();

        let expected_altitude_loss_feet = 0.5 * TEST_GRAVITY * elapsed.powi(2) / 0.304_8;
        assert_abs_diff_eq!(
            result.altitude_loss.0,
            expected_altitude_loss_feet,
            epsilon = 1e-10
        );
        assert_abs_diff_eq!(
            result.acceleration.earth_vertical_upward.0,
            -TEST_GRAVITY,
            epsilon = 1e-12
        );
        assert_abs_diff_eq!(result.earth_up_specific_load.0, 0.0, epsilon = 1e-12);
        assert_abs_diff_eq!(result.total_specific_load.0, 0.0, epsilon = 1e-12);
        assert_abs_diff_eq!(result.mechanical_energy_change.0, 0.0, epsilon = 1e-10);
        assert_abs_diff_eq!(result.dissipative_power.0, 0.0, epsilon = 1e-10);
        assert_abs_diff_eq!(
            result.equivalent_drag_minus_thrust_per_mass.0,
            0.0,
            epsilon = 1e-12
        );
    }

    #[test]
    fn constant_acceleration_descent_matches_closed_form_energy_and_components() {
        let result =
            evaluate_three_dof_feasibility(input(200.0, -10.0, -20.0, 5.0, 0.0, 2.5)).unwrap();

        let midpoint_path_angle = (-15.0_f64).atan2(200.0);
        let expected_energy_change =
            0.5 * (20.0_f64.powi(2) - 10.0_f64.powi(2)) - TEST_GRAVITY * 75.0;
        let expected_dissipative_power = -expected_energy_change / 5.0;

        assert_abs_diff_eq!(result.altitude_loss.0, 75.0 / 0.304_8, epsilon = 1e-10);
        assert_abs_diff_eq!(
            result.initial_flight_path_angle.0,
            (-10.0_f64).atan2(200.0).to_degrees(),
            epsilon = 1e-12
        );
        assert_abs_diff_eq!(
            result.final_flight_path_angle.0,
            (-20.0_f64).atan2(200.0).to_degrees(),
            epsilon = 1e-12
        );
        assert_abs_diff_eq!(
            result.acceleration.earth_vertical_upward.0,
            -2.0,
            epsilon = 1e-12
        );
        assert_abs_diff_eq!(
            result.acceleration.flight_path_tangential.0,
            -2.0 * midpoint_path_angle.sin(),
            epsilon = 1e-12
        );
        assert_abs_diff_eq!(
            result.acceleration.vertical_plane_normal_upward.0,
            -2.0 * midpoint_path_angle.cos(),
            epsilon = 1e-12
        );
        assert_abs_diff_eq!(
            result.earth_up_specific_load.0,
            (TEST_GRAVITY - 2.0) / TEST_GRAVITY,
            epsilon = 1e-12
        );
        assert_abs_diff_eq!(
            result.mechanical_energy_change.0,
            expected_energy_change,
            epsilon = 1e-10
        );
        assert_abs_diff_eq!(
            result.dissipative_power.0,
            expected_dissipative_power,
            epsilon = 1e-10
        );
        assert_abs_diff_eq!(
            result.equivalent_drag_minus_thrust_per_mass.0,
            expected_dissipative_power / 200.0_f64.hypot(-15.0),
            epsilon = 1e-12
        );
    }

    #[test]
    fn coordinated_level_turn_combines_vertical_and_lateral_specific_load() {
        let horizontal_speed = 100.0;
        let target_lateral_acceleration = 3.0_f64.sqrt() * TEST_GRAVITY;
        let turn_rate_degrees_per_second =
            (target_lateral_acceleration / horizontal_speed).to_degrees();
        let result = evaluate_three_dof_feasibility(input(
            horizontal_speed,
            0.0,
            0.0,
            10.0,
            turn_rate_degrees_per_second,
            1.5,
        ))
        .unwrap();

        assert_abs_diff_eq!(
            result.acceleration.horizontal_turn_lateral.0,
            target_lateral_acceleration,
            epsilon = 1e-12
        );
        assert_abs_diff_eq!(result.earth_up_specific_load.0, 1.0, epsilon = 1e-12);
        assert_abs_diff_eq!(result.total_specific_load.0, 2.0, epsilon = 1e-12);
        assert_abs_diff_eq!(result.mechanical_energy_change.0, 0.0, epsilon = 1e-12);
        assert_eq!(
            result.generic_load_classification,
            GenericLoadClassification::ExceedsThreshold
        );
    }

    #[test]
    fn raw_bfo_median_regression_matches_vertical_acceleration_and_energy_change() {
        let result = evaluate_three_dof_feasibility(ThreeDofFeasibilityInput {
            horizontal_speed: Knots(480.043_410),
            horizontal_speed_basis: HorizontalSpeedBasis::GroundSpeed,
            initial_vertical_speed: FeetPerMinute(-4_451.293_157),
            final_vertical_speed: FeetPerMinute(-14_994.696_168),
            elapsed_time: Seconds(8.027),
            turn_rate: DegreesPerSecond(0.0),
            generic_total_specific_load_threshold: SpecificLoadG(2.5),
        })
        .unwrap();

        assert_eq!(
            result.horizontal_speed_basis,
            HorizontalSpeedBasis::GroundSpeed
        );
        assert_abs_diff_eq!(
            result.acceleration.earth_vertical_upward.0 / TEST_GRAVITY,
            -0.6804,
            epsilon = 5e-5
        );
        assert_abs_diff_eq!(
            result.mechanical_energy_change.0 / 1_000.0,
            -1.243,
            epsilon = 0.002
        );
        assert_abs_diff_eq!(result.altitude_loss.0, 1_300.78, epsilon = 0.02);
        assert_eq!(
            result.generic_load_classification,
            GenericLoadClassification::WithinInclusiveThreshold
        );
    }
}
