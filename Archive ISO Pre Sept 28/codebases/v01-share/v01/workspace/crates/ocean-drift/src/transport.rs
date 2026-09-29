use mh370_domain::{destination_wgs84, Degrees, LatLon, NauticalMiles};
use rand::Rng;
use rand_distr::StandardNormal;
use serde::{Deserialize, Serialize};
use thiserror::Error;

use crate::{FieldError, GriddedField};

#[derive(Debug, Clone, Copy, PartialEq, Serialize, Deserialize)]
pub struct MotionConfig {
    pub integration_step_seconds: f64,
    pub output_step_seconds: f64,
    pub horizontal_diffusivity_m2_per_s: f64,
    /// Multiplicative response to the separately supplied surface-Stokes field.
    /// One applies the full surface velocity; zero disables its contribution.
    #[serde(default = "unit_stokes_velocity_scale")]
    pub stokes_velocity_scale: f64,
    /// Wind-speed-proportional direct leeway, distinct from Stokes drift.
    pub windage_fraction: f64,
    /// Fixed wind-relative leeway speed. This represents empirical object
    /// response such as the CSIRO flaperon measurement without converting it
    /// into a wind fraction.
    #[serde(default)]
    pub windage_speed_m_per_s: f64,
    /// Positive angles rotate windage clockwise from downwind.
    pub windage_angle_degrees: f64,
    pub current_standard_error_scale: f64,
}

const fn unit_stokes_velocity_scale() -> f64 {
    1.0
}

impl MotionConfig {
    pub fn validate(&self) -> Result<(), TransportError> {
        let output_ratio = self.output_step_seconds / self.integration_step_seconds;
        if !self.integration_step_seconds.is_finite()
            || self.integration_step_seconds <= 0.0
            || !self.output_step_seconds.is_finite()
            || self.output_step_seconds < self.integration_step_seconds
            || !self.horizontal_diffusivity_m2_per_s.is_finite()
            || self.horizontal_diffusivity_m2_per_s < 0.0
            || !self.stokes_velocity_scale.is_finite()
            || !(0.0..=2.0).contains(&self.stokes_velocity_scale)
            || !self.windage_fraction.is_finite()
            || !(0.0..=0.1).contains(&self.windage_fraction)
            || !self.windage_speed_m_per_s.is_finite()
            || !(0.0..=1.0).contains(&self.windage_speed_m_per_s)
            || !self.windage_angle_degrees.is_finite()
            || self.windage_angle_degrees.abs() > 90.0
            || !self.current_standard_error_scale.is_finite()
            || !(0.0..=5.0).contains(&self.current_standard_error_scale)
            || (output_ratio - output_ratio.round()).abs() > 1e-10
        {
            return Err(TransportError::InvalidConfiguration);
        }
        Ok(())
    }
}

#[derive(Debug, Clone, Copy, PartialEq, Serialize, Deserialize)]
pub struct DriftPoint {
    pub unix_seconds: f64,
    pub position: LatLon,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum PathTerminationReason {
    MissingFieldCoverage,
    OutsideSpatialSupport,
    LandEncounter,
    Beaching,
    OutsideTimeSupport,
    NumericalFailure,
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct PathTermination {
    pub unix_seconds: f64,
    /// Position at termination when one exists. Field-format failures can
    /// occur before a meaningful position is available and use `None`.
    #[serde(default)]
    pub position: Option<LatLon>,
    pub reason: PathTerminationReason,
    pub detail: String,
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct DriftPath {
    pub points: Vec<DriftPoint>,
    pub termination: Option<PathTermination>,
    /// Importance correction relative to the physical transport law. Ordinary
    /// independent paths have log weight zero.
    #[serde(default)]
    pub log_importance_weight: f64,
}

impl DriftPath {
    pub fn importance_weight(&self) -> f64 {
        self.log_importance_weight.exp()
    }
}

#[derive(Debug, Clone, Copy)]
pub struct DriftEnvironment<'a> {
    pub currents: &'a GriddedField,
    /// Ten-metre winds. Direct windage is applied only when configured.
    pub wind: Option<&'a GriddedField>,
    /// A wave-model Stokes velocity field, kept distinct from windage.
    pub stokes: Option<&'a GriddedField>,
    /// Optional coastal field with `land_fraction` and, when calibrated,
    /// `beaching_rate` (per day). Without it no beaching is invented.
    pub coast: Option<&'a GriddedField>,
}

#[derive(Debug, Error, Clone, PartialEq)]
pub enum TransportError {
    #[error("invalid transport configuration")]
    InvalidConfiguration,
    #[error("invalid transport time interval")]
    InvalidTime,
    #[error("geodesic update failed")]
    Geodesy,
    #[error(transparent)]
    Field(#[from] FieldError),
}

#[derive(Debug, Clone)]
pub(crate) struct DriftState {
    position: LatLon,
    time: f64,
    next_output: f64,
    points: Vec<DriftPoint>,
    termination: Option<PathTermination>,
    current_error_east: f64,
    current_error_north: f64,
    pub(crate) log_importance_weight: f64,
}

impl DriftState {
    pub(crate) fn points(&self) -> &[DriftPoint] {
        &self.points
    }

    pub(crate) fn is_terminated(&self) -> bool {
        self.termination.is_some()
    }
}

/// Forward integrate one surface trajectory with midpoint advection.
///
/// The current-field uncertainty draw is constant along a trajectory because
/// GDP `eU/eV` describe uncertainty in the estimated climatological mean, not
/// unresolved white-noise eddies. Diffusion is a separate random walk.
pub fn simulate_path<R: Rng + ?Sized>(
    environment: DriftEnvironment<'_>,
    start: LatLon,
    start_unix_seconds: f64,
    end_unix_seconds: f64,
    config: MotionConfig,
    rng: &mut R,
) -> Result<DriftPath, TransportError> {
    config.validate()?;
    if !start_unix_seconds.is_finite()
        || !end_unix_seconds.is_finite()
        || end_unix_seconds <= start_unix_seconds
    {
        return Err(TransportError::InvalidTime);
    }
    let mut state = initialize_state(start, start_unix_seconds, config, rng);
    advance_state(environment, &mut state, end_unix_seconds, config, rng)?;
    Ok(finish_state(state))
}

pub(crate) fn initialize_state<R: Rng + ?Sized>(
    start: LatLon,
    start_unix_seconds: f64,
    config: MotionConfig,
    rng: &mut R,
) -> DriftState {
    DriftState {
        position: start,
        time: start_unix_seconds,
        next_output: start_unix_seconds + config.output_step_seconds,
        points: vec![DriftPoint {
            unix_seconds: start_unix_seconds,
            position: start,
        }],
        termination: None,
        current_error_east: rng.sample(StandardNormal),
        current_error_north: rng.sample(StandardNormal),
        log_importance_weight: 0.0,
    }
}

pub(crate) fn advance_state<R: Rng + ?Sized>(
    environment: DriftEnvironment<'_>,
    state: &mut DriftState,
    end_unix_seconds: f64,
    config: MotionConfig,
    rng: &mut R,
) -> Result<(), TransportError> {
    config.validate()?;
    if state.termination.is_some() {
        return Ok(());
    }
    if !end_unix_seconds.is_finite() || end_unix_seconds <= state.time {
        return Err(TransportError::InvalidTime);
    }

    while state.time < end_unix_seconds {
        let step = config
            .integration_step_seconds
            .min(end_unix_seconds - state.time);
        match land_encounter(environment, state.time, state.position) {
            Ok(true) => {
                state.termination = Some(PathTermination {
                    unix_seconds: state.time,
                    position: Some(state.position),
                    reason: PathTerminationReason::LandEncounter,
                    detail: "explicit coastal interaction field".to_string(),
                });
                return Ok(());
            }
            Ok(false) => {}
            Err(error) => {
                state.termination = Some(field_termination(state.time, state.position, error));
                return Ok(());
            }
        }
        let first = match velocity(
            environment,
            state.time,
            state.position,
            config,
            state.current_error_east,
            state.current_error_north,
        ) {
            Ok(value) => value,
            Err(error) => {
                state.termination = Some(field_termination(state.time, state.position, error));
                return Ok(());
            }
        };
        let midpoint = match advect(state.position, first.0, first.1, step / 2.0) {
            Ok(value) => value,
            Err(error) => {
                state.termination = Some(numerical_termination(state.time, state.position, error));
                return Ok(());
            }
        };
        match land_encounter(environment, state.time + step / 2.0, midpoint) {
            Ok(true) => {
                state.termination = Some(PathTermination {
                    unix_seconds: state.time + step / 2.0,
                    position: Some(midpoint),
                    reason: PathTerminationReason::LandEncounter,
                    detail: "explicit coastal interaction field at RK2 midpoint".to_string(),
                });
                return Ok(());
            }
            Ok(false) => {}
            Err(error) => {
                state.termination =
                    Some(field_termination(state.time + step / 2.0, midpoint, error));
                return Ok(());
            }
        }
        let second = match velocity(
            environment,
            state.time + step / 2.0,
            midpoint,
            config,
            state.current_error_east,
            state.current_error_north,
        ) {
            Ok(value) => value,
            Err(error) => {
                state.termination = Some(field_termination(state.time, midpoint, error));
                return Ok(());
            }
        };
        state.position = match advect(state.position, second.0, second.1, step) {
            Ok(value) => value,
            Err(error) => {
                state.termination = Some(numerical_termination(state.time, state.position, error));
                return Ok(());
            }
        };
        if config.horizontal_diffusivity_m2_per_s > 0.0 {
            let standard_deviation = (2.0 * config.horizontal_diffusivity_m2_per_s * step).sqrt();
            let east: f64 = rng.sample::<f64, _>(StandardNormal) * standard_deviation;
            let north: f64 = rng.sample::<f64, _>(StandardNormal) * standard_deviation;
            state.position = match advect(state.position, east / step, north / step, step) {
                Ok(value) => value,
                Err(error) => {
                    state.termination =
                        Some(numerical_termination(state.time, state.position, error));
                    return Ok(());
                }
            };
        }
        match coastal_termination(environment, state.time + step, state.position, step, rng) {
            Ok(Some(reason)) => {
                state.time += step;
                state.points.push(DriftPoint {
                    unix_seconds: state.time,
                    position: state.position,
                });
                state.termination = Some(PathTermination {
                    unix_seconds: state.time,
                    position: Some(state.position),
                    reason,
                    detail: "explicit coastal interaction field".to_string(),
                });
                return Ok(());
            }
            Ok(None) => {}
            Err(error) => {
                state.termination = Some(field_termination(state.time, state.position, error));
                return Ok(());
            }
        }
        state.time += step;
        if state.time + 1e-6 >= state.next_output || state.time + 1e-6 >= end_unix_seconds {
            state.points.push(DriftPoint {
                unix_seconds: state.time,
                position: state.position,
            });
            while state.next_output <= state.time + 1e-6 {
                state.next_output += config.output_step_seconds;
            }
        }
    }
    Ok(())
}

fn coastal_termination<R: Rng + ?Sized>(
    environment: DriftEnvironment<'_>,
    time: f64,
    position: LatLon,
    step_seconds: f64,
    rng: &mut R,
) -> Result<Option<PathTerminationReason>, FieldError> {
    if land_encounter(environment, time, position)? {
        return Ok(Some(PathTerminationReason::LandEncounter));
    }
    let Some(coast) = environment.coast else {
        return Ok(None);
    };
    let beaching_rate = match coast.interpolate("beaching_rate", time, position) {
        Ok(value) => value.max(0.0),
        Err(FieldError::MissingComponent(_)) => 0.0,
        Err(error) => return Err(error),
    };
    if beaching_rate > 0.0 {
        let probability = 1.0 - (-beaching_rate * step_seconds / 86_400.0).exp();
        if rng.gen::<f64>() < probability.clamp(0.0, 1.0) {
            return Ok(Some(PathTerminationReason::Beaching));
        }
    }
    Ok(None)
}

fn land_encounter(
    environment: DriftEnvironment<'_>,
    time: f64,
    position: LatLon,
) -> Result<bool, FieldError> {
    let Some(coast) = environment.coast else {
        return Ok(false);
    };
    Ok(coast.interpolate("land_fraction", time, position)? >= 0.5)
}

pub(crate) fn finish_state(state: DriftState) -> DriftPath {
    DriftPath {
        points: state.points,
        termination: state.termination,
        log_importance_weight: state.log_importance_weight,
    }
}

fn field_termination(time: f64, position: LatLon, error: FieldError) -> PathTermination {
    let reason = match error {
        FieldError::OutsideTime => PathTerminationReason::OutsideTimeSupport,
        FieldError::OutsideSpace => PathTerminationReason::OutsideSpatialSupport,
        FieldError::MissingValue => PathTerminationReason::MissingFieldCoverage,
        FieldError::InvalidFormat(_) | FieldError::MissingComponent(_) | FieldError::Storage(_) => {
            PathTerminationReason::NumericalFailure
        }
    };
    PathTermination {
        unix_seconds: time,
        position: Some(position),
        reason,
        detail: error.to_string(),
    }
}

fn numerical_termination(time: f64, position: LatLon, error: TransportError) -> PathTermination {
    PathTermination {
        unix_seconds: time,
        position: Some(position),
        reason: PathTerminationReason::NumericalFailure,
        detail: error.to_string(),
    }
}

fn velocity(
    environment: DriftEnvironment<'_>,
    time: f64,
    position: LatLon,
    config: MotionConfig,
    error_east: f64,
    error_north: f64,
) -> Result<(f64, f64), FieldError> {
    let current = environment.currents.velocity(time, position)?;
    let mut east = current.east_mps
        + config.current_standard_error_scale * current.east_standard_error_mps * error_east;
    let mut north = current.north_mps
        + config.current_standard_error_scale * current.north_standard_error_mps * error_north;
    if let Some(stokes) = environment.stokes {
        let wave = stokes.velocity(time, position)?;
        east += config.stokes_velocity_scale * wave.east_mps;
        north += config.stokes_velocity_scale * wave.north_mps;
    }
    if config.windage_fraction > 0.0 || config.windage_speed_m_per_s > 0.0 {
        let wind = environment
            .wind
            .ok_or_else(|| FieldError::MissingComponent("wind field".to_string()))?
            .velocity(time, position)?;
        let angle = config.windage_angle_degrees.to_radians();
        let wind_speed = wind.east_mps.hypot(wind.north_mps);
        let response = if wind_speed > 0.0 {
            config.windage_fraction + config.windage_speed_m_per_s / wind_speed
        } else {
            config.windage_fraction
        };
        east += response * (wind.east_mps * angle.cos() + wind.north_mps * angle.sin());
        north += response * (wind.north_mps * angle.cos() - wind.east_mps * angle.sin());
    }
    Ok((east, north))
}

fn advect(
    start: LatLon,
    east_mps: f64,
    north_mps: f64,
    seconds: f64,
) -> Result<LatLon, TransportError> {
    let speed = east_mps.hypot(north_mps);
    if !speed.is_finite() || !seconds.is_finite() || seconds <= 0.0 {
        return Err(TransportError::Geodesy);
    }
    if speed == 0.0 {
        return Ok(start);
    }
    let bearing = east_mps.atan2(north_mps).to_degrees().rem_euclid(360.0);
    destination_wgs84(
        start,
        Degrees(bearing),
        NauticalMiles(speed * seconds / 1_852.0),
    )
    .map_err(|_| TransportError::Geodesy)
}

#[cfg(test)]
mod tests {
    use super::*;
    use approx::assert_abs_diff_eq;
    use rand_chacha::{rand_core::SeedableRng, ChaCha8Rng};

    fn component_field(components: &[(&str, f32)]) -> GriddedField {
        let mut bytes = b"MHGRID1\0".to_vec();
        bytes.extend(1u32.to_le_bytes());
        bytes.extend(0u32.to_le_bytes());
        for value in [2u32, 2, 2, components.len() as u32] {
            bytes.extend(value.to_le_bytes());
        }
        for value in [0.0_f64, 200_000.0, -10.0, 10.0, -10.0, 10.0] {
            bytes.extend(value.to_le_bytes());
        }
        for (name, value) in components {
            let mut raw = [0u8; 16];
            raw[..name.len()].copy_from_slice(name.as_bytes());
            bytes.extend(raw);
            for _ in 0..8 {
                bytes.extend(value.to_le_bytes());
            }
        }
        GriddedField::from_bytes("constant", &bytes).unwrap()
    }

    fn constant_field(east: f32, north: f32) -> GriddedField {
        component_field(&[("u", east), ("v", north)])
    }

    fn zero_motion() -> MotionConfig {
        MotionConfig {
            integration_step_seconds: 21_600.0,
            output_step_seconds: 86_400.0,
            horizontal_diffusivity_m2_per_s: 0.0,
            stokes_velocity_scale: 1.0,
            windage_fraction: 0.0,
            windage_speed_m_per_s: 0.0,
            windage_angle_degrees: 0.0,
            current_standard_error_scale: 0.0,
        }
    }

    #[test]
    fn configured_stokes_scale_has_the_expected_analytic_displacement() {
        let currents = constant_field(0.0, 0.0);
        let stokes = constant_field(1.0, 0.0);
        let mut config = zero_motion();
        config.stokes_velocity_scale = 0.5;
        let mut rng = ChaCha8Rng::seed_from_u64(81);
        let path = simulate_path(
            DriftEnvironment {
                currents: &currents,
                wind: None,
                stokes: Some(&stokes),
                coast: None,
            },
            LatLon::new(0.0, 0.0).unwrap(),
            0.0,
            86_400.0,
            config,
            &mut rng,
        )
        .unwrap();
        let end = path.points.last().unwrap().position;
        assert_abs_diff_eq!(
            end.longitude.0,
            0.5 * 86_400.0 / 111_319.490_793_273_57,
            epsilon = 1e-8
        );
    }

    #[test]
    fn fixed_wind_relative_leeway_is_not_rescaled_by_wind_speed() {
        let currents = constant_field(0.0, 0.0);
        let wind = constant_field(0.0, 2.0);
        let mut config = zero_motion();
        config.stokes_velocity_scale = 0.0;
        config.windage_speed_m_per_s = 0.1;
        let mut rng = ChaCha8Rng::seed_from_u64(82);
        let path = simulate_path(
            DriftEnvironment {
                currents: &currents,
                wind: Some(&wind),
                stokes: None,
                coast: None,
            },
            LatLon::new(0.0, 0.0).unwrap(),
            0.0,
            86_400.0,
            config,
            &mut rng,
        )
        .unwrap();
        let end = path.points.last().unwrap().position;
        assert_abs_diff_eq!(end.latitude.0, 0.1 * 86_400.0 / 110_574.0, epsilon = 2e-4);
        assert_abs_diff_eq!(end.longitude.0, 0.0, epsilon = 1e-10);
    }

    #[test]
    fn one_day_constant_eastward_fixture_matches_analytic_distance() {
        let field = constant_field(1.0, 0.0);
        let mut rng = ChaCha8Rng::seed_from_u64(8);
        let path = simulate_path(
            DriftEnvironment {
                currents: &field,
                wind: None,
                stokes: None,
                coast: None,
            },
            LatLon::new(0.0, 0.0).unwrap(),
            0.0,
            86_400.0,
            zero_motion(),
            &mut rng,
        )
        .unwrap();
        let end = path.points.last().unwrap().position;
        assert_abs_diff_eq!(end.latitude.0, 0.0, epsilon = 1e-10);
        assert_abs_diff_eq!(
            end.longitude.0,
            86_400.0 / 111_319.490_793_273_57,
            epsilon = 1e-8
        );
    }

    #[test]
    fn fixed_seed_reproduces_diffusive_path() {
        let field = constant_field(0.0, 0.0);
        let config = MotionConfig {
            integration_step_seconds: 21_600.0,
            output_step_seconds: 86_400.0,
            horizontal_diffusivity_m2_per_s: 50.0,
            stokes_velocity_scale: 1.0,
            windage_fraction: 0.0,
            windage_speed_m_per_s: 0.0,
            windage_angle_degrees: 0.0,
            current_standard_error_scale: 0.0,
        };
        let run = |seed| {
            let mut rng = ChaCha8Rng::seed_from_u64(seed);
            simulate_path(
                DriftEnvironment {
                    currents: &field,
                    wind: None,
                    stokes: None,
                    coast: None,
                },
                LatLon::new(0.0, 0.0).unwrap(),
                0.0,
                86_400.0,
                config,
                &mut rng,
            )
            .unwrap()
        };
        assert_eq!(run(42), run(42));
        assert_ne!(run(42), run(43));
    }

    fn termination_with(
        currents: &GriddedField,
        coast: Option<&GriddedField>,
        start_time: f64,
        mut config: MotionConfig,
    ) -> PathTerminationReason {
        let mut rng = ChaCha8Rng::seed_from_u64(9);
        if config.windage_fraction > 0.0 || config.windage_speed_m_per_s > 0.0 {
            config.windage_angle_degrees = 0.0;
        }
        simulate_path(
            DriftEnvironment {
                currents,
                wind: None,
                stokes: None,
                coast,
            },
            LatLon::new(0.0, 0.0).unwrap(),
            start_time,
            start_time + 86_400.0,
            config,
            &mut rng,
        )
        .unwrap()
        .termination
        .unwrap()
        .reason
    }

    #[test]
    fn termination_taxonomy_distinguishes_land_beaching_time_and_missing_data() {
        let currents = constant_field(0.0, 0.0);
        let land = component_field(&[("land_fraction", 1.0)]);
        assert_eq!(
            termination_with(&currents, Some(&land), 0.0, zero_motion()),
            PathTerminationReason::LandEncounter
        );

        let beach = component_field(&[("land_fraction", 0.0), ("beaching_rate", 1.0e9)]);
        assert_eq!(
            termination_with(&currents, Some(&beach), 0.0, zero_motion()),
            PathTerminationReason::Beaching
        );

        assert_eq!(
            termination_with(&currents, None, -1.0, zero_motion()),
            PathTerminationReason::OutsideTimeSupport
        );

        let missing = constant_field(f32::NAN, 0.0);
        assert_eq!(
            termination_with(&missing, None, 0.0, zero_motion()),
            PathTerminationReason::MissingFieldCoverage
        );

        let mut rng = ChaCha8Rng::seed_from_u64(10);
        let outside_space = simulate_path(
            DriftEnvironment {
                currents: &currents,
                wind: None,
                stokes: None,
                coast: None,
            },
            LatLon::new(20.0, 0.0).unwrap(),
            0.0,
            86_400.0,
            zero_motion(),
            &mut rng,
        )
        .unwrap();
        assert_eq!(
            outside_space.termination.unwrap().reason,
            PathTerminationReason::OutsideSpatialSupport
        );
    }

    #[test]
    fn absent_required_wind_is_a_configuration_failure_not_missing_coverage() {
        let currents = constant_field(0.0, 0.0);
        let mut config = zero_motion();
        config.windage_fraction = 0.01;
        assert_eq!(
            termination_with(&currents, None, 0.0, config),
            PathTerminationReason::NumericalFailure
        );
    }
}
