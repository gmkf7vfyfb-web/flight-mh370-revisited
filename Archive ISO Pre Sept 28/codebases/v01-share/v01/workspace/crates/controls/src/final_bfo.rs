use mh370_domain::{AircraftState, Degrees, Feet, FeetPerMinute, Seconds, Vec3};
use mh370_dynamics::{propagate_constant_track, DynamicsError};
use mh370_satcom::{bfo_components, BfoConstants};
use serde::{Deserialize, Serialize};
use thiserror::Error;

const FPM_TO_M_S: f64 = 0.005_08;
const STANDARD_GRAVITY_M_S2: f64 = 9.806_65;
const SENSITIVITY_STEP_FPM: f64 = 1_000.0;

#[derive(Debug, Clone, Copy, PartialEq, Serialize, Deserialize)]
pub struct BfoPairObservation {
    pub raw_bfo_hz: f64,
    /// Explicit channel/electronics term added to the physical prediction.
    /// Zero represents the raw-BFO, no-additional-transient hypothesis.
    pub channel_bias_hz: f64,
    pub ordinary_measurement_sd_hz: f64,
    pub satellite_afc_hz: f64,
    pub satellite_position_km: Vec3,
    pub satellite_velocity_km_s: Vec3,
    pub ground_station_position_km: Vec3,
}

#[derive(Debug, Clone, Copy, PartialEq, Serialize, Deserialize)]
pub struct BfoPairSearchBounds {
    pub track_step_deg: f64,
    pub maximum_absolute_turn_rate_deg_s: f64,
    pub turn_rate_step_deg_s: f64,
    pub minimum_vertical_speed_fpm: f64,
    pub maximum_vertical_speed_fpm: f64,
    pub maximum_absolute_vertical_acceleration_g: f64,
}

#[derive(Debug, Clone, Copy, PartialEq, Serialize, Deserialize)]
pub struct BfoPairCandidate {
    pub request_track_true_deg: f64,
    pub acknowledgement_track_true_deg: f64,
    pub turn_rate_deg_s: f64,
    pub request_vertical_speed_fpm: f64,
    pub acknowledgement_vertical_speed_fpm: f64,
    pub vertical_speed_change_fpm: f64,
    /// Earth-vertical kinematic acceleration, positive upward. This is not
    /// aircraft normal load factor.
    pub mean_vertical_acceleration_g_upward: f64,
    pub acknowledgement_altitude_ft: f64,
    pub request_bfo_sensitivity_hz_per_fpm: f64,
    pub acknowledgement_bfo_sensitivity_hz_per_fpm: f64,
    pub request_vertical_speed_sd_fpm: f64,
    pub acknowledgement_vertical_speed_sd_fpm: f64,
    pub vertical_acceleration_sd_g: f64,
}

#[derive(Debug, Clone, Copy, PartialEq, Serialize, Deserialize)]
pub struct BfoVerticalSolution {
    pub required_vertical_speed_fpm: f64,
    pub sensitivity_hz_per_fpm: f64,
    pub ordinary_measurement_sd_fpm: f64,
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct BfoPairSearchResult {
    pub evaluated_candidates: usize,
    pub feasible_candidates: usize,
    pub minimum_absolute_acceleration: Option<BfoPairCandidate>,
    pub minimum_absolute_acceleration_without_turn: Option<BfoPairCandidate>,
}

#[derive(Debug, Error)]
pub enum FinalBfoError {
    #[error("invalid final-BFO control input")]
    InvalidInput,
    #[error("BFO has negligible vertical-speed sensitivity")]
    DegenerateVerticalSensitivity,
    #[error(transparent)]
    Dynamics(#[from] DynamicsError),
}

fn validate_observation(observation: BfoPairObservation) -> Result<(), FinalBfoError> {
    if ![
        observation.raw_bfo_hz,
        observation.channel_bias_hz,
        observation.ordinary_measurement_sd_hz,
        observation.satellite_afc_hz,
        observation.satellite_position_km.x,
        observation.satellite_position_km.y,
        observation.satellite_position_km.z,
        observation.satellite_velocity_km_s.x,
        observation.satellite_velocity_km_s.y,
        observation.satellite_velocity_km_s.z,
        observation.ground_station_position_km.x,
        observation.ground_station_position_km.y,
        observation.ground_station_position_km.z,
    ]
    .iter()
    .all(|value| value.is_finite())
        || observation.ordinary_measurement_sd_hz <= 0.0
    {
        return Err(FinalBfoError::InvalidInput);
    }
    Ok(())
}

fn predicted_bfo_hz(
    state: AircraftState,
    observation: BfoPairObservation,
    mut constants: BfoConstants,
) -> f64 {
    constants.satellite_afc_hz = observation.satellite_afc_hz;
    bfo_components(
        state,
        observation.satellite_position_km,
        observation.satellite_velocity_km_s,
        observation.ground_station_position_km,
        constants,
    )
    .base_without_bias
    .0 + state.bfo_bias.0
        + observation.channel_bias_hz
}

fn required_vertical_speed(
    mut state: AircraftState,
    observation: BfoPairObservation,
    constants: BfoConstants,
) -> Result<(f64, f64), FinalBfoError> {
    state.vertical_speed = FeetPerMinute(0.0);
    let zero = predicted_bfo_hz(state, observation, constants);
    state.vertical_speed = FeetPerMinute(SENSITIVITY_STEP_FPM);
    let sensitivity =
        (predicted_bfo_hz(state, observation, constants) - zero) / SENSITIVITY_STEP_FPM;
    if !sensitivity.is_finite() || sensitivity.abs() < 1e-12 {
        return Err(FinalBfoError::DegenerateVerticalSensitivity);
    }
    Ok(((observation.raw_bfo_hz - zero) / sensitivity, sensitivity))
}

/// Invert one BFO observation for vertical speed at a declared instantaneous
/// horizontal state. Unknown startup or channel transients must be represented
/// explicitly by `observation.channel_bias_hz`; they are not hidden here.
pub fn solve_bfo_vertical_speed(
    state: AircraftState,
    observation: BfoPairObservation,
    constants: BfoConstants,
) -> Result<BfoVerticalSolution, FinalBfoError> {
    validate_observation(observation)?;
    if !state.all_finite()
        || ![
            constants.uplink_hz,
            constants.downlink_hz,
            constants.speed_of_light_km_s,
            constants.nominal_satellite_longitude_deg,
            constants.nominal_satellite_altitude_km,
        ]
        .iter()
        .all(|value| value.is_finite())
        || state.altitude.0 < 0.0
        || state.ground_speed.0 <= 0.0
        || constants.uplink_hz <= 0.0
        || constants.downlink_hz <= 0.0
        || constants.speed_of_light_km_s <= 0.0
        || constants.nominal_satellite_altitude_km <= 0.0
    {
        return Err(FinalBfoError::InvalidInput);
    }
    let (required_vertical_speed_fpm, sensitivity_hz_per_fpm) =
        required_vertical_speed(state, observation, constants)?;
    Ok(BfoVerticalSolution {
        required_vertical_speed_fpm,
        sensitivity_hz_per_fpm,
        ordinary_measurement_sd_fpm: observation.ordinary_measurement_sd_hz
            / sensitivity_hz_per_fpm.abs(),
    })
}

pub fn analyze_bfo_pair(
    initial: AircraftState,
    request: BfoPairObservation,
    acknowledgement: BfoPairObservation,
    constants: BfoConstants,
    elapsed_seconds: f64,
    request_track_true_deg: f64,
    turn_rate_deg_s: f64,
) -> Result<BfoPairCandidate, FinalBfoError> {
    validate_observation(request)?;
    validate_observation(acknowledgement)?;
    if !initial.all_finite()
        || ![
            elapsed_seconds,
            request_track_true_deg,
            turn_rate_deg_s,
            constants.uplink_hz,
            constants.downlink_hz,
            constants.speed_of_light_km_s,
            constants.nominal_satellite_longitude_deg,
            constants.nominal_satellite_altitude_km,
        ]
        .iter()
        .all(|value| value.is_finite())
        || elapsed_seconds <= 0.0
        || initial.altitude.0 < 0.0
        || initial.ground_speed.0 <= 0.0
        || constants.uplink_hz <= 0.0
        || constants.downlink_hz <= 0.0
        || constants.speed_of_light_km_s <= 0.0
        || constants.nominal_satellite_altitude_km <= 0.0
    {
        return Err(FinalBfoError::InvalidInput);
    }

    let mut request_state = initial;
    request_state.track_true = Degrees(request_track_true_deg).wrapped_360();
    request_state.vertical_speed = FeetPerMinute(0.0);
    let (request_vertical_speed_fpm, request_sensitivity) =
        required_vertical_speed(request_state, request, constants)?;

    let acknowledgement_track_true_deg = request_track_true_deg + turn_rate_deg_s * elapsed_seconds;
    let midpoint_track_true_deg = request_track_true_deg + 0.5 * turn_rate_deg_s * elapsed_seconds;
    let mut horizontal_state = request_state;
    horizontal_state.track_true = Degrees(midpoint_track_true_deg).wrapped_360();
    horizontal_state.vertical_speed = FeetPerMinute(0.0);
    let mut acknowledgement_state =
        propagate_constant_track(horizontal_state, Seconds(elapsed_seconds))?;
    acknowledgement_state.track_true = Degrees(acknowledgement_track_true_deg).wrapped_360();

    let mut acknowledgement_vertical_speed_fpm = 0.0;
    for _ in 0..4 {
        let altitude_ft = initial.altitude.0
            + 0.5
                * (request_vertical_speed_fpm + acknowledgement_vertical_speed_fpm)
                * elapsed_seconds
                / 60.0;
        acknowledgement_state.altitude = Feet(altitude_ft);
        let solved = required_vertical_speed(acknowledgement_state, acknowledgement, constants)?;
        acknowledgement_vertical_speed_fpm = solved.0;
    }
    let acknowledgement_altitude_ft = initial.altitude.0
        + 0.5 * (request_vertical_speed_fpm + acknowledgement_vertical_speed_fpm) * elapsed_seconds
            / 60.0;
    acknowledgement_state.altitude = Feet(acknowledgement_altitude_ft);
    let solved = required_vertical_speed(acknowledgement_state, acknowledgement, constants)?;
    let acknowledgement_vertical_speed_fpm = solved.0;
    let acknowledgement_sensitivity = solved.1;

    let vertical_speed_change_fpm = acknowledgement_vertical_speed_fpm - request_vertical_speed_fpm;
    let acceleration_g =
        vertical_speed_change_fpm * FPM_TO_M_S / elapsed_seconds / STANDARD_GRAVITY_M_S2;
    let request_vertical_speed_sd_fpm =
        request.ordinary_measurement_sd_hz / request_sensitivity.abs();
    let acknowledgement_vertical_speed_sd_fpm =
        acknowledgement.ordinary_measurement_sd_hz / acknowledgement_sensitivity.abs();
    let vertical_acceleration_sd_g =
        request_vertical_speed_sd_fpm.hypot(acknowledgement_vertical_speed_sd_fpm) * FPM_TO_M_S
            / elapsed_seconds
            / STANDARD_GRAVITY_M_S2;

    Ok(BfoPairCandidate {
        request_track_true_deg: Degrees(request_track_true_deg).wrapped_360().0,
        acknowledgement_track_true_deg: Degrees(acknowledgement_track_true_deg).wrapped_360().0,
        turn_rate_deg_s,
        request_vertical_speed_fpm,
        acknowledgement_vertical_speed_fpm,
        vertical_speed_change_fpm,
        mean_vertical_acceleration_g_upward: acceleration_g,
        acknowledgement_altitude_ft,
        request_bfo_sensitivity_hz_per_fpm: request_sensitivity,
        acknowledgement_bfo_sensitivity_hz_per_fpm: acknowledgement_sensitivity,
        request_vertical_speed_sd_fpm,
        acknowledgement_vertical_speed_sd_fpm,
        vertical_acceleration_sd_g,
    })
}

fn candidate_within_bounds(candidate: BfoPairCandidate, bounds: BfoPairSearchBounds) -> bool {
    candidate.acknowledgement_altitude_ft >= 0.0
        && candidate.request_vertical_speed_fpm >= bounds.minimum_vertical_speed_fpm
        && candidate.request_vertical_speed_fpm <= bounds.maximum_vertical_speed_fpm
        && candidate.acknowledgement_vertical_speed_fpm >= bounds.minimum_vertical_speed_fpm
        && candidate.acknowledgement_vertical_speed_fpm <= bounds.maximum_vertical_speed_fpm
        && candidate.mean_vertical_acceleration_g_upward.abs()
            <= bounds.maximum_absolute_vertical_acceleration_g
}

pub fn search_bfo_pair(
    initial: AircraftState,
    request: BfoPairObservation,
    acknowledgement: BfoPairObservation,
    constants: BfoConstants,
    elapsed_seconds: f64,
    bounds: BfoPairSearchBounds,
) -> Result<BfoPairSearchResult, FinalBfoError> {
    if ![
        bounds.track_step_deg,
        bounds.maximum_absolute_turn_rate_deg_s,
        bounds.turn_rate_step_deg_s,
        bounds.minimum_vertical_speed_fpm,
        bounds.maximum_vertical_speed_fpm,
        bounds.maximum_absolute_vertical_acceleration_g,
    ]
    .iter()
    .all(|value| value.is_finite())
        || bounds.track_step_deg <= 0.0
        || bounds.track_step_deg > 360.0
        || bounds.maximum_absolute_turn_rate_deg_s < 0.0
        || bounds.turn_rate_step_deg_s <= 0.0
        || bounds.minimum_vertical_speed_fpm >= bounds.maximum_vertical_speed_fpm
        || bounds.maximum_absolute_vertical_acceleration_g <= 0.0
    {
        return Err(FinalBfoError::InvalidInput);
    }

    let mut evaluated_candidates = 0;
    let mut feasible_candidates = 0;
    let mut minimum_absolute_acceleration: Option<BfoPairCandidate> = None;
    let mut minimum_without_turn: Option<BfoPairCandidate> = None;
    let track_count = (360.0 / bounds.track_step_deg).ceil() as usize;
    let turn_steps =
        (bounds.maximum_absolute_turn_rate_deg_s / bounds.turn_rate_step_deg_s).ceil() as i64;
    for track_index in 0..track_count {
        let track = track_index as f64 * bounds.track_step_deg;
        for turn_index in -turn_steps..=turn_steps {
            let turn_rate = turn_index as f64 * bounds.turn_rate_step_deg_s;
            if turn_rate.abs() > bounds.maximum_absolute_turn_rate_deg_s + 1e-12 {
                continue;
            }
            let candidate = analyze_bfo_pair(
                initial,
                request,
                acknowledgement,
                constants,
                elapsed_seconds,
                track,
                turn_rate,
            )?;
            evaluated_candidates += 1;
            if !candidate_within_bounds(candidate, bounds) {
                continue;
            }
            feasible_candidates += 1;
            if minimum_absolute_acceleration.map_or(true, |current| {
                candidate.mean_vertical_acceleration_g_upward.abs()
                    < current.mean_vertical_acceleration_g_upward.abs()
            }) {
                minimum_absolute_acceleration = Some(candidate);
            }
            if turn_rate.abs() < 1e-12
                && minimum_without_turn.map_or(true, |current| {
                    candidate.mean_vertical_acceleration_g_upward.abs()
                        < current.mean_vertical_acceleration_g_upward.abs()
                })
            {
                minimum_without_turn = Some(candidate);
            }
        }
    }

    Ok(BfoPairSearchResult {
        evaluated_candidates,
        feasible_candidates,
        minimum_absolute_acceleration,
        minimum_absolute_acceleration_without_turn: minimum_without_turn,
    })
}

#[cfg(test)]
mod tests {
    use mh370_domain::{Feet, Hertz, Knots, LatLon};

    use super::*;

    fn state() -> AircraftState {
        AircraftState {
            time: Seconds(22_660.0),
            position: LatLon::new(-37.63, 89.21).unwrap(),
            altitude: Feet(35_000.0),
            track_true: Degrees(186.0),
            ground_speed: Knots(480.0),
            vertical_speed: FeetPerMinute(0.0),
            bfo_bias: Hertz(150.0),
        }
    }

    fn observation(raw_bfo_hz: f64, second: bool) -> BfoPairObservation {
        BfoPairObservation {
            raw_bfo_hz,
            channel_bias_hz: 0.0,
            ordinary_measurement_sd_hz: 7.0,
            satellite_afc_hz: -37.8,
            satellite_position_km: if second {
                Vec3::new(18_182.033_52, 38_049.636_31, 391.752_122)
            } else {
                Vec3::new(18_182.020_38, 38_049.649_62, 392.417_794)
            },
            satellite_velocity_km_s: if second {
                Vec3::new(0.001_583, -0.001_635, -0.083_225)
            } else {
                Vec3::new(0.001_584, -0.001_634, -0.083_208)
            },
            ground_station_position_km: Vec3::new(-2_368.8, 4_881.1, -3_342.0),
        }
    }

    fn constants() -> BfoConstants {
        BfoConstants {
            satellite_afc_hz: 0.0,
            uplink_hz: 1_646_652_500.0,
            downlink_hz: 3_615_152_500.0,
            speed_of_light_km_s: 299_792.458,
            nominal_satellite_longitude_deg: 64.5,
            nominal_satellite_altitude_km: 36_210.12,
        }
    }

    #[test]
    fn solved_pair_reproduces_raw_request_and_requires_increasing_descent() {
        let candidate = analyze_bfo_pair(
            state(),
            observation(182.0, false),
            observation(-2.0, true),
            constants(),
            8.027,
            186.0,
            0.0,
        )
        .unwrap();
        let mut request_state = state();
        request_state.vertical_speed = FeetPerMinute(candidate.request_vertical_speed_fpm);
        let prediction = predicted_bfo_hz(request_state, observation(182.0, false), constants());
        assert!((prediction - 182.0).abs() < 1e-8);
        assert!(
            candidate.acknowledgement_vertical_speed_fpm < candidate.request_vertical_speed_fpm
        );
        assert!(candidate.mean_vertical_acceleration_g_upward < 0.0);
        assert!(candidate.vertical_acceleration_sd_g > 0.0);
        // Independent scalar audit in inputs/evidence/startup-bfo-scenarios.json
        // gives -10,523.98 ft/min and -0.67916 g when all pair change is
        // assigned to vertical dynamics. Geometry makes this fixture slightly
        // different, so use a deliberately rough cross-implementation bound.
        assert!((candidate.vertical_speed_change_fpm + 10_523.98).abs() < 100.0);
        assert!((candidate.mean_vertical_acceleration_g_upward + 0.679_16).abs() < 0.01);
    }

    #[test]
    fn broad_search_finds_a_pair_within_generous_kinematic_bounds() {
        let result = search_bfo_pair(
            state(),
            observation(182.0, false),
            observation(-2.0, true),
            constants(),
            8.027,
            BfoPairSearchBounds {
                track_step_deg: 30.0,
                maximum_absolute_turn_rate_deg_s: 3.0,
                turn_rate_step_deg_s: 1.0,
                minimum_vertical_speed_fpm: -30_000.0,
                maximum_vertical_speed_fpm: 10_000.0,
                maximum_absolute_vertical_acceleration_g: 1.0,
            },
        )
        .unwrap();
        assert!(result.evaluated_candidates > 0);
        assert!(result.feasible_candidates > 0);
        assert!(result.minimum_absolute_acceleration.is_some());
        assert!(result.minimum_absolute_acceleration_without_turn.is_some());
    }
}
