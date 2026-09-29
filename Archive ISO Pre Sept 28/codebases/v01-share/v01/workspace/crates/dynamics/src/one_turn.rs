use mh370_domain::{AircraftState, Degrees, Feet, FeetPerMinute, Hertz, Knots, LatLon, Seconds};
use rand::Rng;
use rand_chacha::ChaCha8Rng;
use rand_distr::{Distribution, StandardNormal};
use serde::{Deserialize, Serialize};
use thiserror::Error;

use crate::{
    fixed_waypoint_guidance, ground_velocity_from_control, propagate_constant_track,
    EnvironmentError, Era5Grid, GroundVelocity, IgrfGrid, LateralGuidance, LateralMode,
    WaypointError,
};

const KNOT_M_S: f64 = 0.514_444_444_444_444_5;

#[derive(Debug, Clone, Copy, PartialEq, Serialize, Deserialize)]
pub struct RadarPrior {
    pub time_s: f64,
    pub latitude_deg: f64,
    pub longitude_deg: f64,
    pub position_sd_nm: f64,
    pub control_mean_deg_true: f64,
    pub control_sd_deg: f64,
    pub mach_min: f64,
    pub mach_max: f64,
    pub altitude_min_ft: f64,
    pub altitude_max_ft: f64,
}

impl RadarPrior {
    pub fn validate(&self) -> Result<(), OneTurnError> {
        LatLon::new(self.latitude_deg, self.longitude_deg)
            .map_err(|_| OneTurnError::InvalidRadarPrior)?;
        if ![
            self.time_s,
            self.position_sd_nm,
            self.control_mean_deg_true,
            self.control_sd_deg,
            self.mach_min,
            self.mach_max,
            self.altitude_min_ft,
            self.altitude_max_ft,
        ]
        .iter()
        .all(|value| value.is_finite())
            || self.position_sd_nm < 0.0
            || self.control_sd_deg < 0.0
            || self.mach_min <= 0.0
            || self.mach_max <= self.mach_min
            || self.altitude_min_ft < 0.0
            || self.altitude_max_ft <= self.altitude_min_ft
        {
            return Err(OneTurnError::InvalidRadarPrior);
        }
        Ok(())
    }
}

#[derive(Debug, Clone, Copy, PartialEq, Serialize, Deserialize)]
pub struct OneTurnConfig {
    pub turn_time_min_s: f64,
    pub turn_time_max_s: f64,
}

impl OneTurnConfig {
    pub fn validate(&self, radar: &RadarPrior) -> Result<(), OneTurnError> {
        radar.validate()?;
        if !self.turn_time_min_s.is_finite()
            || !self.turn_time_max_s.is_finite()
            || self.turn_time_min_s < radar.time_s
            || self.turn_time_max_s <= self.turn_time_min_s
        {
            return Err(OneTurnError::InvalidConfiguration);
        }
        Ok(())
    }
}

#[derive(Debug, Clone, Copy)]
pub struct NavigationEnvironment<'a> {
    pub weather: &'a Era5Grid,
    pub magnetic: &'a IgrfGrid,
    pub time_origin_unix_s: f64,
    pub integration_step_s: f64,
    pub lateral_guidance: LateralGuidance,
}

#[derive(Debug, Clone, Copy, PartialEq, Serialize, Deserialize)]
pub struct OneTurnParameters {
    pub initial_latitude_deg: f64,
    pub initial_longitude_deg: f64,
    pub initial_track_true_deg: f64,
    pub turn_time_s: f64,
    pub post_turn_track_true_deg: f64,
    pub mach: f64,
    pub altitude_ft: f64,
}

#[derive(Debug, Clone, Copy, PartialEq, Serialize, Deserialize)]
pub struct OneTurnTrajectory {
    pub parameters: OneTurnParameters,
    pub aircraft: AircraftState,
    pub turn_count: u8,
    pub heading_true: Degrees,
}

#[derive(Debug, Error)]
pub enum OneTurnError {
    #[error("invalid one-turn dynamics configuration")]
    InvalidConfiguration,
    #[error("invalid radar prior")]
    InvalidRadarPrior,
    #[error("one-turn parameters are outside their declared prior")]
    OutsidePrior,
    #[error("requested trajectory time precedes the radar epoch")]
    TimeBeforeRadar,
    #[error("environment-aware propagation requires finite positive integration settings")]
    InvalidEnvironmentConfiguration,
    #[error(transparent)]
    Environment(#[from] EnvironmentError),
    #[error(transparent)]
    Waypoint(#[from] WaypointError),
    #[error(transparent)]
    Propagation(#[from] crate::DynamicsError),
}

/// Remove the scientifically inactive scalar post-turn control from a
/// fixed-waypoint parameter state.
///
/// The value zero is a serialization sentinel, not a northbound command. The
/// actual immediate post-turn track is derived from the propagated turn
/// position and fixed waypoint.
pub fn canonicalize_one_turn_parameters(
    mut parameters: OneTurnParameters,
    guidance: LateralGuidance,
) -> OneTurnParameters {
    if matches!(guidance, LateralGuidance::DirectTo(_)) {
        parameters.post_turn_track_true_deg = 0.0;
    }
    parameters
}

fn standard_normal(rng: &mut ChaCha8Rng) -> f64 {
    StandardNormal.sample(rng)
}

fn angle_difference(target: f64, reference: f64) -> f64 {
    (target - reference + 180.0).rem_euclid(360.0) - 180.0
}

fn reflect(value: f64, minimum: f64, maximum: f64) -> f64 {
    let width = maximum - minimum;
    let folded = (value - minimum).rem_euclid(2.0 * width);
    if folded <= width {
        minimum + folded
    } else {
        maximum - (folded - width)
    }
}

pub fn speed_of_sound_knots(altitude_ft: f64) -> f64 {
    let altitude_m = altitude_ft * 0.304_8;
    let temperature_k = if altitude_m < 11_000.0 {
        288.15 - 0.0065 * altitude_m
    } else {
        216.65
    };
    (1.4 * 287.052_87 * temperature_k).sqrt() / KNOT_M_S
}

pub fn sample_one_turn(
    radar: &RadarPrior,
    config: &OneTurnConfig,
    rng: &mut ChaCha8Rng,
) -> Result<OneTurnParameters, OneTurnError> {
    config.validate(radar)?;
    let north_nm = radar.position_sd_nm * standard_normal(rng);
    let east_nm = radar.position_sd_nm * standard_normal(rng);
    let latitude = radar.latitude_deg + north_nm / 60.0;
    let longitude = radar.longitude_deg + east_nm / (60.0 * radar.latitude_deg.to_radians().cos());
    LatLon::new(latitude, longitude).map_err(|_| OneTurnError::OutsidePrior)?;
    Ok(OneTurnParameters {
        initial_latitude_deg: latitude,
        initial_longitude_deg: longitude,
        initial_track_true_deg: Degrees(
            radar.control_mean_deg_true + radar.control_sd_deg * standard_normal(rng),
        )
        .wrapped_360()
        .0,
        turn_time_s: rng.gen_range(config.turn_time_min_s..config.turn_time_max_s),
        post_turn_track_true_deg: rng.gen_range(0.0..360.0),
        mach: rng.gen_range(radar.mach_min..radar.mach_max),
        altitude_ft: rng.gen_range(radar.altitude_min_ft..radar.altitude_max_ft),
    })
}

pub fn one_turn_log_prior(
    parameters: &OneTurnParameters,
    radar: &RadarPrior,
    config: &OneTurnConfig,
) -> Result<f64, OneTurnError> {
    config.validate(radar)?;
    LatLon::new(
        parameters.initial_latitude_deg,
        parameters.initial_longitude_deg,
    )
    .map_err(|_| OneTurnError::OutsidePrior)?;
    if !parameters.initial_track_true_deg.is_finite()
        || !parameters.post_turn_track_true_deg.is_finite()
        || !(config.turn_time_min_s..=config.turn_time_max_s).contains(&parameters.turn_time_s)
        || !(0.0..360.0).contains(&parameters.post_turn_track_true_deg)
        || !(radar.mach_min..=radar.mach_max).contains(&parameters.mach)
        || !(radar.altitude_min_ft..=radar.altitude_max_ft).contains(&parameters.altitude_ft)
    {
        return Ok(f64::NEG_INFINITY);
    }

    let north_nm = (parameters.initial_latitude_deg - radar.latitude_deg) * 60.0;
    let east_nm = angle_difference(parameters.initial_longitude_deg, radar.longitude_deg)
        * 60.0
        * radar.latitude_deg.to_radians().cos();
    let position_term = if radar.position_sd_nm > 0.0 {
        -0.5 * ((north_nm / radar.position_sd_nm).powi(2)
            + (east_nm / radar.position_sd_nm).powi(2))
    } else if north_nm.abs() < 1e-12 && east_nm.abs() < 1e-12 {
        0.0
    } else {
        f64::NEG_INFINITY
    };
    let track_error = angle_difference(
        parameters.initial_track_true_deg,
        radar.control_mean_deg_true,
    );
    let track_term = if radar.control_sd_deg > 0.0 {
        -0.5 * (track_error / radar.control_sd_deg).powi(2)
    } else if track_error.abs() < 1e-12 {
        0.0
    } else {
        f64::NEG_INFINITY
    };
    Ok(position_term + track_term)
}

pub fn mutate_one_turn(
    parameters: OneTurnParameters,
    radar: &RadarPrior,
    config: &OneTurnConfig,
    scale: f64,
    rng: &mut ChaCha8Rng,
) -> Result<OneTurnParameters, OneTurnError> {
    config.validate(radar)?;
    if !scale.is_finite() || scale <= 0.0 {
        return Err(OneTurnError::InvalidConfiguration);
    }
    let latitude_step = radar.position_sd_nm / 60.0 * scale * standard_normal(rng);
    let longitude_step = radar.position_sd_nm / (60.0 * radar.latitude_deg.to_radians().cos())
        * scale
        * standard_normal(rng);
    let track_step = radar.control_sd_deg * scale * standard_normal(rng);
    let turn_range = config.turn_time_max_s - config.turn_time_min_s;
    let mach_range = radar.mach_max - radar.mach_min;
    let altitude_range = radar.altitude_max_ft - radar.altitude_min_ft;
    Ok(OneTurnParameters {
        initial_latitude_deg: parameters.initial_latitude_deg + latitude_step,
        initial_longitude_deg: Degrees(parameters.initial_longitude_deg + longitude_step)
            .wrapped_180()
            .0,
        initial_track_true_deg: Degrees(parameters.initial_track_true_deg + track_step)
            .wrapped_360()
            .0,
        turn_time_s: reflect(
            parameters.turn_time_s + turn_range * scale * standard_normal(rng),
            config.turn_time_min_s,
            config.turn_time_max_s,
        ),
        post_turn_track_true_deg: Degrees(
            parameters.post_turn_track_true_deg + 360.0 * scale * standard_normal(rng),
        )
        .wrapped_360()
        .0,
        mach: reflect(
            parameters.mach + mach_range * scale * standard_normal(rng),
            radar.mach_min,
            radar.mach_max,
        ),
        altitude_ft: reflect(
            parameters.altitude_ft + altitude_range * scale * standard_normal(rng),
            radar.altitude_min_ft,
            radar.altitude_max_ft,
        ),
    })
}

pub fn one_turn_state_at(
    parameters: OneTurnParameters,
    radar: &RadarPrior,
    config: &OneTurnConfig,
    time_s: f64,
    bfo_bias_hz: f64,
) -> Result<OneTurnTrajectory, OneTurnError> {
    if one_turn_log_prior(&parameters, radar, config)? == f64::NEG_INFINITY {
        return Err(OneTurnError::OutsidePrior);
    }
    if !time_s.is_finite() || time_s < radar.time_s {
        return Err(OneTurnError::TimeBeforeRadar);
    }
    let mut aircraft = AircraftState {
        time: Seconds(radar.time_s),
        position: LatLon::new(
            parameters.initial_latitude_deg,
            parameters.initial_longitude_deg,
        )
        .map_err(|_| OneTurnError::OutsidePrior)?,
        altitude: Feet(parameters.altitude_ft),
        track_true: Degrees(parameters.initial_track_true_deg),
        ground_speed: Knots(parameters.mach * speed_of_sound_knots(parameters.altitude_ft)),
        vertical_speed: FeetPerMinute(0.0),
        bfo_bias: Hertz(bfo_bias_hz),
    };
    let before_turn_end = time_s.min(parameters.turn_time_s);
    aircraft = propagate_constant_track(aircraft, Seconds(before_turn_end - radar.time_s))?;
    let turn_count = u8::from(time_s >= parameters.turn_time_s);
    if turn_count == 1 {
        aircraft.track_true = Degrees(parameters.post_turn_track_true_deg);
        aircraft = propagate_constant_track(aircraft, Seconds(time_s - parameters.turn_time_s))?;
    }
    let heading_true = aircraft.track_true;
    Ok(OneTurnTrajectory {
        parameters,
        aircraft,
        turn_count,
        heading_true,
    })
}

fn validate_environment(environment: NavigationEnvironment<'_>) -> Result<(), OneTurnError> {
    if !environment.time_origin_unix_s.is_finite()
        || !environment.integration_step_s.is_finite()
        || environment.integration_step_s <= 0.0
    {
        return Err(OneTurnError::InvalidEnvironmentConfiguration);
    }
    environment.lateral_guidance.validate()?;
    Ok(())
}

fn instantaneous_ground_velocity(
    aircraft: AircraftState,
    post_turn: bool,
    parameters: OneTurnParameters,
    environment: NavigationEnvironment<'_>,
) -> Result<GroundVelocity, OneTurnError> {
    validate_environment(environment)?;
    let weather = environment.weather.sample(
        environment.time_origin_unix_s + aircraft.time.0,
        aircraft.altitude.0,
        aircraft.position,
    )?;
    let (control, lateral_mode, declination) = match environment.lateral_guidance {
        LateralGuidance::DirectTo(leg) if post_turn => (
            fixed_waypoint_guidance(aircraft.position, leg)?.track_true,
            LateralMode::ConstantTrueTrack,
            Degrees(0.0),
        ),
        LateralGuidance::DirectTo(_) => (
            Degrees(parameters.initial_track_true_deg),
            LateralMode::ConstantTrueTrack,
            Degrees(0.0),
        ),
        LateralGuidance::SelectedControl(lateral_mode) => {
            let control = if post_turn {
                Degrees(parameters.post_turn_track_true_deg)
            } else {
                Degrees(parameters.initial_track_true_deg)
            };
            let declination = if matches!(
                lateral_mode,
                LateralMode::ConstantMagneticHeading | LateralMode::ConstantMagneticTrack
            ) {
                environment
                    .magnetic
                    .declination(aircraft.altitude.0, aircraft.position)?
            } else {
                Degrees(0.0)
            };
            (control, lateral_mode, declination)
        }
    };
    Ok(ground_velocity_from_control(
        Knots(parameters.mach * weather.speed_of_sound_knots()),
        control,
        lateral_mode,
        weather.wind_north,
        weather.wind_east,
        declination,
    )?)
}

fn with_instantaneous_velocity(
    mut aircraft: AircraftState,
    post_turn: bool,
    parameters: OneTurnParameters,
    environment: NavigationEnvironment<'_>,
) -> Result<(AircraftState, Degrees), OneTurnError> {
    let velocity = instantaneous_ground_velocity(aircraft, post_turn, parameters, environment)?;
    aircraft.track_true = velocity.track_true;
    aircraft.ground_speed = velocity.speed;
    Ok((aircraft, velocity.heading_true))
}

fn next_lattice_boundary(time_s: f64, origin_s: f64, step_s: f64) -> f64 {
    let cell = ((time_s - origin_s) / step_s).floor();
    let mut boundary = origin_s + (cell + 1.0) * step_s;
    while boundary <= time_s + 1e-9 {
        boundary += step_s;
    }
    boundary
}

struct EnvironmentTrajectoryIntegrator<'a> {
    parameters: OneTurnParameters,
    environment: NavigationEnvironment<'a>,
    lattice_origin_s: f64,
    cell_start: AircraftState,
    cell_heading_true: Degrees,
    cell_end_time_s: f64,
}

impl<'a> EnvironmentTrajectoryIntegrator<'a> {
    fn new(
        parameters: OneTurnParameters,
        radar: &RadarPrior,
        bfo_bias_hz: f64,
        environment: NavigationEnvironment<'a>,
    ) -> Result<Self, OneTurnError> {
        validate_environment(environment)?;
        let aircraft = AircraftState {
            time: Seconds(radar.time_s),
            position: LatLon::new(
                parameters.initial_latitude_deg,
                parameters.initial_longitude_deg,
            )
            .map_err(|_| OneTurnError::OutsidePrior)?,
            altitude: Feet(parameters.altitude_ft),
            track_true: Degrees(parameters.initial_track_true_deg),
            ground_speed: Knots(parameters.mach * speed_of_sound_knots(parameters.altitude_ft)),
            vertical_speed: FeetPerMinute(0.0),
            bfo_bias: Hertz(bfo_bias_hz),
        };
        let post_turn = aircraft.time.0 >= parameters.turn_time_s - 1e-9;
        let (cell_start, cell_heading_true) =
            with_instantaneous_velocity(aircraft, post_turn, parameters, environment)?;
        let mut result = Self {
            parameters,
            environment,
            lattice_origin_s: radar.time_s,
            cell_start,
            cell_heading_true,
            cell_end_time_s: f64::NAN,
        };
        result.cell_end_time_s = result.next_cell_end();
        Ok(result)
    }

    fn post_turn_at(&self, time_s: f64) -> bool {
        time_s >= self.parameters.turn_time_s - 1e-9
    }

    fn next_cell_end(&self) -> f64 {
        let lattice_boundary = next_lattice_boundary(
            self.cell_start.time.0,
            self.lattice_origin_s,
            self.environment.integration_step_s,
        );
        if !self.post_turn_at(self.cell_start.time.0)
            && self.parameters.turn_time_s < lattice_boundary - 1e-9
        {
            self.parameters.turn_time_s
        } else {
            lattice_boundary
        }
    }

    fn propagate_cached_to(&self, target_time_s: f64) -> Result<AircraftState, OneTurnError> {
        let duration_s = target_time_s - self.cell_start.time.0;
        if !duration_s.is_finite() || duration_s < -1e-9 {
            return Err(OneTurnError::TimeBeforeRadar);
        }
        if self.post_turn_at(self.cell_start.time.0) {
            if let LateralGuidance::DirectTo(leg) = self.environment.lateral_guidance {
                let guidance = fixed_waypoint_guidance(self.cell_start.position, leg)?;
                let step_distance_nm =
                    self.cell_start.ground_speed.0 * duration_s.max(0.0) / 3_600.0;
                if step_distance_nm + leg.arrival_radius.0 >= guidance.distance_remaining.0 {
                    return Err(WaypointError::LegCompletesDuringStep {
                        distance_remaining_nm: guidance.distance_remaining.0,
                        step_distance_nm,
                        arrival_radius_nm: leg.arrival_radius.0,
                    }
                    .into());
                }
            }
        }
        let mut result = propagate_constant_track(self.cell_start, Seconds(duration_s.max(0.0)))?;
        result.time = Seconds(target_time_s);
        Ok(result)
    }

    fn complete_cell(&mut self) -> Result<(), OneTurnError> {
        let boundary_state = self.propagate_cached_to(self.cell_end_time_s)?;
        let (cell_start, cell_heading_true) = with_instantaneous_velocity(
            boundary_state,
            self.post_turn_at(self.cell_end_time_s),
            self.parameters,
            self.environment,
        )?;
        self.cell_start = cell_start;
        self.cell_heading_true = cell_heading_true;
        self.cell_end_time_s = self.next_cell_end();
        Ok(())
    }

    fn trajectory_at(&mut self, time_s: f64) -> Result<OneTurnTrajectory, OneTurnError> {
        if !time_s.is_finite() || time_s < self.lattice_origin_s - 1e-9 {
            return Err(OneTurnError::TimeBeforeRadar);
        }
        while time_s >= self.cell_end_time_s - 1e-9 {
            self.complete_cell()?;
            if (time_s - self.cell_start.time.0).abs() <= 1e-9 {
                break;
            }
        }
        let (aircraft, heading_true) = if (time_s - self.cell_start.time.0).abs() <= 1e-9 {
            (self.cell_start, self.cell_heading_true)
        } else {
            let presentation_state = self.propagate_cached_to(time_s)?;
            with_instantaneous_velocity(
                presentation_state,
                self.post_turn_at(time_s),
                self.parameters,
                self.environment,
            )?
        };
        Ok(OneTurnTrajectory {
            parameters: self.parameters,
            aircraft,
            turn_count: u8::from(self.post_turn_at(time_s)),
            heading_true,
        })
    }
}

/// Derive the commanded direct-to track at the sampled turn position using the
/// same absolute integration lattice as likelihood trajectories.
pub fn one_turn_direct_to_track_at_turn(
    parameters: OneTurnParameters,
    radar: &RadarPrior,
    config: &OneTurnConfig,
    environment: NavigationEnvironment<'_>,
) -> Result<Degrees, OneTurnError> {
    if one_turn_log_prior(&parameters, radar, config)? == f64::NEG_INFINITY {
        return Err(OneTurnError::OutsidePrior);
    }
    if environment.lateral_guidance.direct_to_leg().is_none() {
        return Err(WaypointError::UntypedLateralNavigation.into());
    }
    let mut integrator = EnvironmentTrajectoryIntegrator::new(parameters, radar, 0.0, environment)?;
    Ok(integrator
        .trajectory_at(parameters.turn_time_s)?
        .aircraft
        .track_true)
}

pub fn one_turn_trajectories_at(
    parameters: OneTurnParameters,
    radar: &RadarPrior,
    config: &OneTurnConfig,
    times_s: &[f64],
    bfo_bias_hz: f64,
    environment: Option<NavigationEnvironment<'_>>,
) -> Result<Vec<OneTurnTrajectory>, OneTurnError> {
    if environment.is_none() {
        return times_s
            .iter()
            .map(|time| one_turn_state_at(parameters, radar, config, *time, bfo_bias_hz))
            .collect();
    }
    if one_turn_log_prior(&parameters, radar, config)? == f64::NEG_INFINITY {
        return Err(OneTurnError::OutsidePrior);
    }
    let environment = environment.expect("environment option was checked");
    let mut integrator =
        EnvironmentTrajectoryIntegrator::new(parameters, radar, bfo_bias_hz, environment)?;
    let mut previous_time_s = radar.time_s;
    let mut trajectories = Vec::with_capacity(times_s.len());
    for time_s in times_s {
        if !time_s.is_finite() || *time_s < previous_time_s {
            return Err(OneTurnError::TimeBeforeRadar);
        }
        trajectories.push(integrator.trajectory_at(*time_s)?);
        previous_time_s = *time_s;
    }
    Ok(trajectories)
}

#[cfg(test)]
mod tests {
    use std::{fs, path::Path};

    use approx::assert_abs_diff_eq;
    use mh370_domain::{destination_wgs84, NauticalMiles};
    use rand::SeedableRng;

    use super::*;
    use crate::FixedWaypointLeg;

    fn radar() -> RadarPrior {
        RadarPrior {
            time_s: 0.0,
            latitude_deg: 5.624829,
            longitude_deg: 99.048157,
            position_sd_nm: 0.5,
            control_mean_deg_true: 295.66,
            control_sd_deg: 1.0,
            mach_min: 0.73,
            mach_max: 0.84,
            altitude_min_ft: 25_000.0,
            altitude_max_ft: 43_000.0,
        }
    }

    fn config() -> OneTurnConfig {
        OneTurnConfig {
            turn_time_min_s: 900.0,
            turn_time_max_s: 3_600.0,
        }
    }

    fn constant_environment() -> (Era5Grid, IgrfGrid) {
        let mut era5 = b"MHERA5V1".to_vec();
        for count in [2_u32, 2, 2, 2] {
            era5.extend(count.to_le_bytes());
        }
        for time in [1_000_i64, 5_000] {
            era5.extend(time.to_le_bytes());
        }
        for value in [25_000_f32, 43_000.0, 0.0, 10.0, 90.0, 110.0] {
            era5.extend(value.to_le_bytes());
        }
        for value in std::iter::repeat_n(216.65_f32, 16) {
            era5.extend(value.to_le_bytes());
        }
        for _ in 0..32 {
            era5.extend(0.0_f32.to_le_bytes());
        }

        let mut igrf = b"MHIGRFV1".to_vec();
        for count in [2_u32, 2, 2] {
            igrf.extend(count.to_le_bytes());
        }
        igrf.extend(1_000_i64.to_le_bytes());
        igrf.extend(2014.18_f64.to_le_bytes());
        for value in [25_000_f32, 43_000.0, 0.0, 10.0, 90.0, 110.0] {
            igrf.extend(value.to_le_bytes());
        }
        for _ in 0..8 {
            igrf.extend(0.0_f32.to_le_bytes());
        }
        (
            Era5Grid::parse(&era5).unwrap(),
            IgrfGrid::parse(&igrf).unwrap(),
        )
    }

    fn varying_environment() -> (Era5Grid, IgrfGrid) {
        let mut era5 = b"MHERA5V1".to_vec();
        for count in [2_u32, 2, 2, 2] {
            era5.extend(count.to_le_bytes());
        }
        for time in [1_000_i64, 6_000] {
            era5.extend(time.to_le_bytes());
        }
        for value in [25_000_f32, 43_000.0, -10.0, 20.0, 85.0, 120.0] {
            era5.extend(value.to_le_bytes());
        }
        let mut temperature = Vec::new();
        let mut wind_east = Vec::new();
        let mut wind_north = Vec::new();
        for time in 0..2 {
            for altitude in 0..2 {
                for latitude in 0..2 {
                    for longitude in 0..2 {
                        temperature.push(
                            214.0
                                + 4.0 * time as f32
                                + altitude as f32
                                + 2.0 * latitude as f32
                                + longitude as f32,
                        );
                        wind_east.push(
                            -18.0
                                + 9.0 * time as f32
                                + 2.0 * altitude as f32
                                + 5.0 * latitude as f32
                                + 3.0 * longitude as f32,
                        );
                        wind_north.push(
                            14.0 - 7.0 * time as f32 + altitude as f32 - 4.0 * latitude as f32
                                + 2.0 * longitude as f32,
                        );
                    }
                }
            }
        }
        for field in [&temperature, &wind_east, &wind_north] {
            for value in field {
                era5.extend(value.to_le_bytes());
            }
        }

        let mut igrf = b"MHIGRFV1".to_vec();
        for count in [2_u32, 2, 2] {
            igrf.extend(count.to_le_bytes());
        }
        igrf.extend(1_000_i64.to_le_bytes());
        igrf.extend(2014.18_f64.to_le_bytes());
        for value in [25_000_f32, 43_000.0, -10.0, 20.0, 85.0, 120.0] {
            igrf.extend(value.to_le_bytes());
        }
        for altitude in 0..2 {
            for latitude in 0..2 {
                for longitude in 0..2 {
                    let declination = -8.0 + 2.0 * altitude as f32 - 5.0 * latitude as f32
                        + 7.0 * longitude as f32;
                    igrf.extend(declination.to_le_bytes());
                }
            }
        }
        (
            Era5Grid::parse(&era5).unwrap(),
            IgrfGrid::parse(&igrf).unwrap(),
        )
    }

    fn deliberately_out_of_domain_magnetic_grid() -> IgrfGrid {
        let mut igrf = b"MHIGRFV1".to_vec();
        for count in [1_u32, 1, 1] {
            igrf.extend(count.to_le_bytes());
        }
        igrf.extend(1_000_i64.to_le_bytes());
        igrf.extend(2014.18_f64.to_le_bytes());
        for value in [35_000_f32, 0.0, 0.0, 5.0] {
            igrf.extend(value.to_le_bytes());
        }
        IgrfGrid::parse(&igrf).unwrap()
    }

    fn assert_same_trajectory(first: &OneTurnTrajectory, second: &OneTurnTrajectory) {
        assert_eq!(first.aircraft, second.aircraft);
        assert_eq!(first.heading_true, second.heading_true);
        assert_eq!(first.turn_count, second.turn_count);
    }

    fn partitioned_endpoint(guidance: LateralGuidance, times: &[f64]) -> OneTurnTrajectory {
        let (weather, magnetic) = varying_environment();
        let mut radar = radar();
        radar.time_s = 137.5;
        let parameters = OneTurnParameters {
            initial_latitude_deg: 5.624829,
            initial_longitude_deg: 99.048157,
            initial_track_true_deg: 295.66,
            turn_time_s: 1_800.0,
            post_turn_track_true_deg: 160.0,
            mach: 0.8,
            altitude_ft: 35_000.0,
        };
        one_turn_trajectories_at(
            parameters,
            &radar,
            &config(),
            times,
            150.0,
            Some(NavigationEnvironment {
                weather: &weather,
                magnetic: &magnetic,
                time_origin_unix_s: 1_000.0,
                integration_step_s: 300.0,
                lateral_guidance: guidance,
            }),
        )
        .unwrap()
        .pop()
        .unwrap()
    }

    #[test]
    fn environment_aware_heading_propagation_is_sequential_and_explicit() {
        let (weather, magnetic) = constant_environment();
        let parameters = OneTurnParameters {
            initial_latitude_deg: 5.624829,
            initial_longitude_deg: 99.048157,
            initial_track_true_deg: 295.66,
            turn_time_s: 1_800.0,
            post_turn_track_true_deg: 180.0,
            mach: 0.8,
            altitude_ft: 35_000.0,
        };
        let trajectories = one_turn_trajectories_at(
            parameters,
            &radar(),
            &config(),
            &[1_200.0, 3_600.0],
            150.0,
            Some(NavigationEnvironment {
                weather: &weather,
                magnetic: &magnetic,
                time_origin_unix_s: 1_000.0,
                integration_step_s: 300.0,
                lateral_guidance: LateralGuidance::SelectedControl(
                    LateralMode::ConstantTrueHeading,
                ),
            }),
        )
        .unwrap();
        assert_eq!(trajectories.len(), 2);
        assert_eq!(trajectories[0].aircraft.time.0, 1_200.0);
        assert_eq!(trajectories[1].aircraft.time.0, 3_600.0);
        assert!((trajectories[0].heading_true.0 - 295.66).abs() < 1e-9);
        assert!((trajectories[1].heading_true.0 - 180.0).abs() < 1e-9);
        assert_eq!(trajectories[0].turn_count, 0);
        assert_eq!(trajectories[1].turn_count, 1);
    }

    #[test]
    fn sampled_and_mutated_parameters_remain_in_the_declared_prior() {
        let mut first = ChaCha8Rng::seed_from_u64(370);
        let mut second = ChaCha8Rng::seed_from_u64(370);
        let parameters = sample_one_turn(&radar(), &config(), &mut first).unwrap();
        assert_eq!(
            parameters,
            sample_one_turn(&radar(), &config(), &mut second).unwrap()
        );
        let mutated = mutate_one_turn(parameters, &radar(), &config(), 0.2, &mut first).unwrap();
        assert!(one_turn_log_prior(&mutated, &radar(), &config())
            .unwrap()
            .is_finite());
    }

    #[test]
    fn trajectory_turns_once_and_preserves_constant_speed_and_altitude() {
        let parameters = OneTurnParameters {
            initial_latitude_deg: 5.624829,
            initial_longitude_deg: 99.048157,
            initial_track_true_deg: 295.66,
            turn_time_s: 1_800.0,
            post_turn_track_true_deg: 180.0,
            mach: 0.8,
            altitude_ft: 35_000.0,
        };
        let before = one_turn_state_at(parameters, &radar(), &config(), 1_200.0, 150.0).unwrap();
        let after = one_turn_state_at(parameters, &radar(), &config(), 3_600.0, 150.0).unwrap();
        assert_eq!(before.turn_count, 0);
        assert_eq!(after.turn_count, 1);
        assert_eq!(before.aircraft.altitude.0, 35_000.0);
        assert_eq!(after.aircraft.altitude.0, 35_000.0);
        assert_eq!(before.aircraft.ground_speed, after.aircraft.ground_speed);
        assert_eq!(after.aircraft.track_true.0, 180.0);
    }

    #[test]
    fn direct_to_preserves_initial_ctt_then_uses_derived_waypoint_track() {
        let (weather, magnetic) = constant_environment();
        let leg =
            FixedWaypointLeg::new(LatLon::new(0.5, 109.0).unwrap(), NauticalMiles(1.0)).unwrap();
        let environment = NavigationEnvironment {
            weather: &weather,
            magnetic: &magnetic,
            time_origin_unix_s: 1_000.0,
            integration_step_s: 10.0,
            lateral_guidance: LateralGuidance::DirectTo(leg),
        };
        let parameters = OneTurnParameters {
            initial_latitude_deg: 5.624829,
            initial_longitude_deg: 99.048157,
            initial_track_true_deg: 295.66,
            turn_time_s: 1_800.0,
            post_turn_track_true_deg: 0.0,
            mach: 0.8,
            altitude_ft: 35_000.0,
        };
        let trajectories = one_turn_trajectories_at(
            parameters,
            &radar(),
            &config(),
            &[1_799.0, 1_800.0, 1_801.0, 3_600.0],
            150.0,
            Some(environment),
        )
        .unwrap();
        let track_at_turn =
            one_turn_direct_to_track_at_turn(parameters, &radar(), &config(), environment).unwrap();

        assert_abs_diff_eq!(
            trajectories[0].aircraft.track_true.0,
            parameters.initial_track_true_deg,
            epsilon = 1e-12
        );
        assert_abs_diff_eq!(
            trajectories[1].aircraft.track_true.0,
            track_at_turn.0,
            epsilon = 1e-10
        );
        assert_abs_diff_eq!(
            trajectories[2].aircraft.track_true.0,
            fixed_waypoint_guidance(trajectories[2].aircraft.position, leg)
                .unwrap()
                .track_true
                .0,
            epsilon = 1e-12
        );
        assert!(track_at_turn.0 > 90.0 && track_at_turn.0 < 180.0);
        assert!((trajectories[3].aircraft.track_true.0 - track_at_turn.0).abs() > 0.05);
    }

    #[test]
    fn direct_to_parameter_canonicalization_only_removes_inactive_scalar() {
        let parameters = OneTurnParameters {
            initial_latitude_deg: 5.624829,
            initial_longitude_deg: 99.048157,
            initial_track_true_deg: 295.66,
            turn_time_s: 1_800.0,
            post_turn_track_true_deg: 234.5,
            mach: 0.8,
            altitude_ft: 35_000.0,
        };
        let leg =
            FixedWaypointLeg::new(LatLon::new(0.5, 109.0).unwrap(), NauticalMiles(1.0)).unwrap();
        let direct = canonicalize_one_turn_parameters(parameters, LateralGuidance::DirectTo(leg));
        assert_eq!(direct.post_turn_track_true_deg, 0.0);
        assert_eq!(
            direct.initial_track_true_deg,
            parameters.initial_track_true_deg
        );
        assert_eq!(
            canonicalize_one_turn_parameters(
                parameters,
                LateralGuidance::SelectedControl(LateralMode::ConstantTrueTrack),
            ),
            parameters
        );
    }

    #[test]
    fn absolute_lattice_is_invariant_to_scalar_and_direct_to_output_partitions() {
        let direct_leg =
            FixedWaypointLeg::new(LatLon::new(0.5, 109.0).unwrap(), NauticalMiles(1.0)).unwrap();
        let guidance_families = [
            LateralGuidance::SelectedControl(LateralMode::ConstantTrueTrack),
            LateralGuidance::SelectedControl(LateralMode::ConstantMagneticHeading),
            LateralGuidance::DirectTo(direct_leg),
        ];
        let all_epochs = [437.5, 777.25, 1_800.0, 1_937.5, 2_333.333, 3_501.25];
        let with_diagnostics = [
            321.125, 437.5, 777.25, 1_111.111, 1_800.0, 1_800.125, 1_937.5, 2_001.75, 2_333.333,
            3_000.001, 3_501.25,
        ];
        for guidance in guidance_families {
            let endpoint_only = partitioned_endpoint(guidance, &[3_501.25]);
            let ordinary = partitioned_endpoint(guidance, &all_epochs);
            let diagnostic = partitioned_endpoint(guidance, &with_diagnostics);
            assert_same_trajectory(&endpoint_only, &ordinary);
            assert_same_trajectory(&endpoint_only, &diagnostic);
        }
    }

    #[test]
    fn true_reference_modes_do_not_query_inactive_igrf() {
        let (weather, _) = constant_environment();
        let magnetic = deliberately_out_of_domain_magnetic_grid();
        let parameters = OneTurnParameters {
            initial_latitude_deg: 5.624829,
            initial_longitude_deg: 99.048157,
            initial_track_true_deg: 295.66,
            turn_time_s: 1_800.0,
            post_turn_track_true_deg: 160.0,
            mach: 0.8,
            altitude_ft: 35_000.0,
        };
        for lateral_mode in [
            LateralMode::ConstantTrueTrack,
            LateralMode::ConstantTrueHeading,
        ] {
            one_turn_trajectories_at(
                parameters,
                &radar(),
                &config(),
                &[1_200.0],
                150.0,
                Some(NavigationEnvironment {
                    weather: &weather,
                    magnetic: &magnetic,
                    time_origin_unix_s: 1_000.0,
                    integration_step_s: 300.0,
                    lateral_guidance: LateralGuidance::SelectedControl(lateral_mode),
                }),
            )
            .unwrap();
        }
        for lateral_mode in [
            LateralMode::ConstantMagneticTrack,
            LateralMode::ConstantMagneticHeading,
        ] {
            let error = one_turn_trajectories_at(
                parameters,
                &radar(),
                &config(),
                &[1_200.0],
                150.0,
                Some(NavigationEnvironment {
                    weather: &weather,
                    magnetic: &magnetic,
                    time_origin_unix_s: 1_000.0,
                    integration_step_s: 300.0,
                    lateral_guidance: LateralGuidance::SelectedControl(lateral_mode),
                }),
            )
            .unwrap_err();
            assert!(matches!(
                error,
                OneTurnError::Environment(EnvironmentError::OutsideDomain)
            ));
        }
    }

    #[test]
    fn canonical_era5_igrf_endpoints_are_invariant_to_requested_epoch_partition() {
        let workspace = Path::new(env!("CARGO_MANIFEST_DIR")).join("../..");
        let weather = Era5Grid::parse(
            &fs::read(workspace.join("inputs/environment/mh370-era5-grid.bin")).unwrap(),
        )
        .unwrap();
        let magnetic = IgrfGrid::parse(
            &fs::read(workspace.join("inputs/environment/mh370-igrf14-grid.bin")).unwrap(),
        )
        .unwrap();
        let parameters = OneTurnParameters {
            initial_latitude_deg: 5.624829,
            initial_longitude_deg: 99.048157,
            initial_track_true_deg: 295.66,
            turn_time_s: 2_000.0,
            post_turn_track_true_deg: 186.2,
            mach: 0.8,
            altitude_ft: 35_000.0,
        };
        let direct_leg = FixedWaypointLeg::new(
            LatLon::new(-68.470_60, 78.840_61).unwrap(),
            NauticalMiles(1.0),
        )
        .unwrap();
        let ordinary_epochs = [
            1_425.0, 1_576.0, 1_585.0, 2_286.0, 5_953.0, 9_555.0, 13_177.0, 16_772.0, 18_793.0,
            22_150.0,
        ];
        let diagnostic_epochs = [
            777.125, 1_425.0, 1_576.0, 1_585.0, 1_999.75, 2_000.0, 2_000.25, 2_286.0, 4_321.987,
            5_953.0, 9_555.0, 12_345.678, 13_177.0, 16_772.0, 18_793.0, 20_001.001, 22_150.0,
        ];
        for lateral_guidance in [
            LateralGuidance::SelectedControl(LateralMode::ConstantTrueTrack),
            LateralGuidance::SelectedControl(LateralMode::ConstantMagneticHeading),
            LateralGuidance::DirectTo(direct_leg),
        ] {
            let environment = NavigationEnvironment {
                weather: &weather,
                magnetic: &magnetic,
                time_origin_unix_s: 1_394_215_309.0,
                integration_step_s: 600.0,
                lateral_guidance,
            };
            let run = |times: &[f64]| {
                one_turn_trajectories_at(
                    parameters,
                    &radar(),
                    &config(),
                    times,
                    150.0,
                    Some(environment),
                )
                .unwrap()
                .pop()
                .unwrap()
            };
            let endpoint_only = run(&[22_150.0]);
            let ordinary = run(&ordinary_epochs);
            let diagnostic = run(&diagnostic_epochs);
            assert_same_trajectory(&endpoint_only, &ordinary);
            assert_same_trajectory(&endpoint_only, &diagnostic);
        }
    }

    #[test]
    fn presentation_velocity_uses_exact_epoch_era5_igrf_and_waypoint_tangent() {
        let (weather, magnetic) = varying_environment();
        let mut radar = radar();
        radar.time_s = 137.5;
        let parameters = OneTurnParameters {
            initial_latitude_deg: 5.624829,
            initial_longitude_deg: 99.048157,
            initial_track_true_deg: 295.66,
            turn_time_s: 1_800.0,
            post_turn_track_true_deg: 160.0,
            mach: 0.8,
            altitude_ft: 35_000.0,
        };
        let observation_time_s = 2_333.333;
        let leg =
            FixedWaypointLeg::new(LatLon::new(0.5, 109.0).unwrap(), NauticalMiles(1.0)).unwrap();
        let direct_environment = NavigationEnvironment {
            weather: &weather,
            magnetic: &magnetic,
            time_origin_unix_s: 1_000.0,
            integration_step_s: 300.0,
            lateral_guidance: LateralGuidance::DirectTo(leg),
        };
        let direct = one_turn_trajectories_at(
            parameters,
            &radar,
            &config(),
            &[777.25, 1_800.0, observation_time_s],
            150.0,
            Some(direct_environment),
        )
        .unwrap()
        .pop()
        .unwrap();
        let local_guidance = fixed_waypoint_guidance(direct.aircraft.position, leg).unwrap();
        let local_weather = weather
            .sample(
                1_000.0 + observation_time_s,
                direct.aircraft.altitude.0,
                direct.aircraft.position,
            )
            .unwrap();
        let expected_direct = ground_velocity_from_control(
            Knots(parameters.mach * local_weather.speed_of_sound_knots()),
            local_guidance.track_true,
            LateralMode::ConstantTrueTrack,
            local_weather.wind_north,
            local_weather.wind_east,
            Degrees(0.0),
        )
        .unwrap();
        assert_abs_diff_eq!(
            direct.aircraft.track_true.0,
            local_guidance.track_true.0,
            epsilon = 1e-12
        );
        assert_eq!(direct.aircraft.ground_speed, expected_direct.speed);
        assert_eq!(direct.heading_true, expected_direct.heading_true);

        let magnetic_environment = NavigationEnvironment {
            lateral_guidance: LateralGuidance::SelectedControl(
                LateralMode::ConstantMagneticHeading,
            ),
            ..direct_environment
        };
        let magnetic_trajectory = one_turn_trajectories_at(
            parameters,
            &radar,
            &config(),
            &[observation_time_s],
            150.0,
            Some(magnetic_environment),
        )
        .unwrap()
        .pop()
        .unwrap();
        let magnetic_weather = weather
            .sample(
                1_000.0 + observation_time_s,
                magnetic_trajectory.aircraft.altitude.0,
                magnetic_trajectory.aircraft.position,
            )
            .unwrap();
        let declination = magnetic
            .declination(
                magnetic_trajectory.aircraft.altitude.0,
                magnetic_trajectory.aircraft.position,
            )
            .unwrap();
        let expected_magnetic = ground_velocity_from_control(
            Knots(parameters.mach * magnetic_weather.speed_of_sound_knots()),
            Degrees(parameters.post_turn_track_true_deg),
            LateralMode::ConstantMagneticHeading,
            magnetic_weather.wind_north,
            magnetic_weather.wind_east,
            declination,
        )
        .unwrap();
        assert_eq!(
            magnetic_trajectory.aircraft.track_true,
            expected_magnetic.track_true
        );
        assert_eq!(
            magnetic_trajectory.aircraft.ground_speed,
            expected_magnetic.speed
        );
        assert_eq!(
            magnetic_trajectory.heading_true,
            expected_magnetic.heading_true
        );
    }

    #[test]
    fn exact_turn_is_post_turn_and_derived_direct_course_matches_likelihood_path() {
        let (weather, magnetic) = varying_environment();
        let mut radar = radar();
        radar.time_s = 137.5;
        let leg =
            FixedWaypointLeg::new(LatLon::new(0.5, 109.0).unwrap(), NauticalMiles(1.0)).unwrap();
        let environment = NavigationEnvironment {
            weather: &weather,
            magnetic: &magnetic,
            time_origin_unix_s: 1_000.0,
            integration_step_s: 300.0,
            lateral_guidance: LateralGuidance::DirectTo(leg),
        };
        let parameters = OneTurnParameters {
            initial_latitude_deg: 5.624829,
            initial_longitude_deg: 99.048157,
            initial_track_true_deg: 295.66,
            turn_time_s: 1_800.0,
            post_turn_track_true_deg: 0.0,
            mach: 0.8,
            altitude_ft: 35_000.0,
        };
        let turn_from_likelihood = one_turn_trajectories_at(
            parameters,
            &radar,
            &config(),
            &[777.25, 1_111.111, parameters.turn_time_s],
            150.0,
            Some(environment),
        )
        .unwrap()
        .pop()
        .unwrap();
        let derived =
            one_turn_direct_to_track_at_turn(parameters, &radar, &config(), environment).unwrap();
        let geometric = fixed_waypoint_guidance(turn_from_likelihood.aircraft.position, leg)
            .unwrap()
            .track_true;
        assert_eq!(turn_from_likelihood.turn_count, 1);
        assert_eq!(turn_from_likelihood.aircraft.track_true, derived);
        assert_eq!(turn_from_likelihood.aircraft.track_true, geometric);

        let without_environment = one_turn_state_at(
            OneTurnParameters {
                post_turn_track_true_deg: 160.0,
                ..parameters
            },
            &radar,
            &config(),
            parameters.turn_time_s,
            150.0,
        )
        .unwrap();
        assert_eq!(without_environment.turn_count, 1);
        assert_eq!(without_environment.aircraft.track_true, Degrees(160.0));
    }

    #[test]
    fn direct_to_single_leg_rejects_arrival_during_a_lattice_cell() {
        let (weather, magnetic) = varying_environment();
        let mut radar = radar();
        radar.time_s = 137.5;
        let start = LatLon::new(radar.latitude_deg, radar.longitude_deg).unwrap();
        let nearby_waypoint =
            destination_wgs84(start, Degrees(180.0), NauticalMiles(10.0)).unwrap();
        let nearby_leg = FixedWaypointLeg::new(nearby_waypoint, NauticalMiles(1.0)).unwrap();
        let parameters = OneTurnParameters {
            initial_latitude_deg: radar.latitude_deg,
            initial_longitude_deg: radar.longitude_deg,
            initial_track_true_deg: 295.66,
            turn_time_s: radar.time_s,
            post_turn_track_true_deg: 0.0,
            mach: 0.8,
            altitude_ft: 35_000.0,
        };
        let direct_config = OneTurnConfig {
            turn_time_min_s: radar.time_s,
            turn_time_max_s: 3_600.0,
        };
        let error = one_turn_trajectories_at(
            parameters,
            &radar,
            &direct_config,
            &[437.5],
            150.0,
            Some(NavigationEnvironment {
                weather: &weather,
                magnetic: &magnetic,
                time_origin_unix_s: 1_000.0,
                integration_step_s: 300.0,
                lateral_guidance: LateralGuidance::DirectTo(nearby_leg),
            }),
        )
        .unwrap_err();
        assert!(matches!(
            error,
            OneTurnError::Waypoint(WaypointError::LegCompletesDuringStep { .. })
        ));
    }
}
