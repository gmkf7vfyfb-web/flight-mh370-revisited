mod environment;
mod one_turn;
mod powered_flight;
mod three_dof;
mod waypoint;

pub use environment::{isa_pressure_pa, EnvironmentError, Era5Grid, IgrfGrid, WeatherSample};

pub use one_turn::{
    canonicalize_one_turn_parameters, mutate_one_turn, one_turn_direct_to_track_at_turn,
    one_turn_log_prior, one_turn_state_at, one_turn_trajectories_at, sample_one_turn,
    speed_of_sound_knots, NavigationEnvironment, OneTurnConfig, OneTurnError, OneTurnParameters,
    OneTurnTrajectory, RadarPrior,
};

pub use powered_flight::{
    advance_powered_flight_step, advance_powered_flight_step_with_budget,
    advance_powered_flight_step_with_budget_and_event_proposal, initialize_powered_flight,
    instantaneous_powered_limits, propagate_powered_flight, propagate_powered_flight_with_observer,
    refresh_powered_event_renewal, InstantaneousPoweredLimits, MagneticAltitudePolicy,
    ManeuverProcess, ObservedPoweredFlightError, PendingRenewal, PoweredBoundarySeconds,
    PoweredEventBudget, PoweredEventCandidateScorer, PoweredEventClocks, PoweredEventCounters,
    PoweredEventKind, PoweredEventMark, PoweredEventProposalCandidate, PoweredEventProposalConfig,
    PoweredEventProposalConfigError, PoweredEventProposalDiagnostic, PoweredEventProposalError,
    PoweredEventProposalEvent, PoweredEventProposalRng, PoweredFlightCommand,
    PoweredFlightDiagnostics, PoweredFlightEnvironment, PoweredFlightError, PoweredFlightLimits,
    PoweredFlightSegment, PoweredFlightState, PoweredFlightTransition, PoweredIntegration,
    PoweredLateralMode, PoweredLateralModeWeights, PoweredLimitActivity,
    PoweredRenewalRefreshError, PoweredStepRegime, ProposedPoweredFlightSegment, RenewalClock,
    MAX_POWERED_EVENT_PROPOSAL_CANDIDATES,
};

pub use three_dof::{
    evaluate_three_dof_feasibility, DegreesPerSecond, GenericLoadClassification,
    HorizontalSpeedBasis, JoulesPerKilogram, MetersPerSecondSquared, SpecificLoadG,
    ThreeDofAccelerationComponents, ThreeDofFeasibility, ThreeDofFeasibilityError,
    ThreeDofFeasibilityInput, WattsPerKilogram,
};

pub use waypoint::{
    fixed_waypoint_guidance, FixedWaypointGuidance, FixedWaypointLeg, LateralGuidance,
    WaypointError,
};

use mh370_domain::{
    AircraftState, Degrees, Feet, FeetPerMinute, Knots, NauticalMiles, Seconds, VelocityEnu,
};
use serde::{Deserialize, Serialize};
use thiserror::Error;

use mh370_domain::{destination_wgs84, GeodesyError};

#[derive(Debug, Clone, Copy, Default, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum LateralMode {
    ConstantTrueHeading,
    ConstantMagneticHeading,
    #[default]
    ConstantTrueTrack,
    ConstantMagneticTrack,
    LateralNavigation,
}

impl LateralMode {
    pub const fn name(self) -> &'static str {
        match self {
            Self::ConstantTrueHeading => "constant true heading",
            Self::ConstantMagneticHeading => "constant magnetic heading",
            Self::ConstantTrueTrack => "constant true track",
            Self::ConstantMagneticTrack => "constant magnetic track",
            Self::LateralNavigation => "lateral navigation",
        }
    }

    fn heading_controlled(self) -> bool {
        matches!(
            self,
            Self::ConstantTrueHeading | Self::ConstantMagneticHeading
        )
    }

    fn magnetic(self) -> bool {
        matches!(
            self,
            Self::ConstantMagneticHeading | Self::ConstantMagneticTrack
        )
    }
}

#[derive(Debug, Clone, Copy, PartialEq, Serialize, Deserialize)]
pub struct GroundVelocity {
    pub velocity: VelocityEnu,
    pub speed: Knots,
    pub track_true: Degrees,
    pub control_true: Degrees,
    pub heading_true: Degrees,
}

#[derive(Debug, Error)]
pub enum DynamicsError {
    #[error("track control is infeasible for the declared airspeed and crosswind")]
    InfeasibleTrack,
    #[error("propagation duration must be finite and non-negative")]
    InvalidDuration,
    #[error(transparent)]
    Geodesy(#[from] GeodesyError),
}

pub fn ground_velocity_from_control(
    true_airspeed: Knots,
    control: Degrees,
    mode: LateralMode,
    wind_north: Knots,
    wind_east: Knots,
    east_positive_declination: Degrees,
) -> Result<GroundVelocity, DynamicsError> {
    let control_true = if mode.magnetic() {
        Degrees(control.0 + east_positive_declination.0).wrapped_360()
    } else {
        control.wrapped_360()
    };
    let angle = control_true.to_radians();
    let desired_north = angle.cos();
    let desired_east = angle.sin();

    let (north, east) = if mode.heading_controlled() {
        (
            true_airspeed.0 * desired_north + wind_north.0,
            true_airspeed.0 * desired_east + wind_east.0,
        )
    } else {
        let along = wind_north.0 * desired_north + wind_east.0 * desired_east;
        let cross = -wind_north.0 * desired_east + wind_east.0 * desired_north;
        if cross.abs() > true_airspeed.0 {
            return Err(DynamicsError::InfeasibleTrack);
        }
        let speed = along + (true_airspeed.0.powi(2) - cross.powi(2)).sqrt();
        (speed * desired_north, speed * desired_east)
    };
    let speed = north.hypot(east);
    let track_true = Degrees(east.atan2(north).to_degrees()).wrapped_360();
    let heading_true = if mode.heading_controlled() {
        control_true
    } else {
        Degrees(
            (east - wind_east.0)
                .atan2(north - wind_north.0)
                .to_degrees(),
        )
        .wrapped_360()
    };
    Ok(GroundVelocity {
        velocity: VelocityEnu {
            north: Knots(north),
            east: Knots(east),
            vertical: FeetPerMinute(0.0),
        },
        speed: Knots(speed),
        track_true,
        control_true,
        heading_true,
    })
}

pub fn propagate_constant_track(
    mut state: AircraftState,
    duration: Seconds,
) -> Result<AircraftState, DynamicsError> {
    if !duration.0.is_finite() || duration.0 < 0.0 {
        return Err(DynamicsError::InvalidDuration);
    }
    let distance = NauticalMiles(state.ground_speed.0 * duration.0 / 3_600.0);
    state.position = destination_wgs84(state.position, state.track_true, distance)?;
    state.altitude = Feet(state.altitude.0 + state.vertical_speed.0 * duration.0 / 60.0);
    state.time = Seconds(state.time.0 + duration.0);
    Ok(state)
}

#[cfg(test)]
mod tests {
    use approx::assert_abs_diff_eq;
    use mh370_domain::{Feet, FeetPerMinute, Hertz, LatLon};

    use super::*;

    #[test]
    fn magnetic_sign_and_heading_track_wind_resolution_match_convention() {
        let heading = ground_velocity_from_control(
            Knots(500.0),
            Degrees(0.0),
            LateralMode::ConstantTrueHeading,
            Knots(0.0),
            Knots(50.0),
            Degrees(0.0),
        )
        .unwrap();
        let track = ground_velocity_from_control(
            Knots(500.0),
            Degrees(0.0),
            LateralMode::ConstantTrueTrack,
            Knots(0.0),
            Knots(50.0),
            Degrees(0.0),
        )
        .unwrap();
        assert!(heading.track_true.0 > 0.0);
        assert_abs_diff_eq!(track.track_true.0, 0.0, epsilon = 1e-12);
        assert_abs_diff_eq!(track.velocity.east.0, 0.0, epsilon = 1e-12);

        let magnetic = ground_velocity_from_control(
            Knots(500.0),
            Degrees(100.0),
            LateralMode::ConstantMagneticHeading,
            Knots(0.0),
            Knots(0.0),
            Degrees(5.0),
        )
        .unwrap();
        assert_abs_diff_eq!(magnetic.control_true.0, 105.0, epsilon = 1e-12);
    }

    #[test]
    fn constant_track_propagation_closes_elapsed_distance_and_altitude() {
        let state = AircraftState {
            time: Seconds(0.0),
            position: LatLon::new(0.0, 0.0).unwrap(),
            altitude: Feet(35_000.0),
            track_true: Degrees(90.0),
            ground_speed: Knots(480.0),
            vertical_speed: FeetPerMinute(-100.0),
            bfo_bias: Hertz(150.0),
        };
        let result = propagate_constant_track(state, Seconds(450.0)).unwrap();
        assert_abs_diff_eq!(result.time.0, 450.0, epsilon = 0.0);
        assert_abs_diff_eq!(result.altitude.0, 34_250.0, epsilon = 1e-12);
        assert_abs_diff_eq!(result.position.latitude.0, 0.0, epsilon = 1e-10);
    }
}
