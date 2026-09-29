use mh370_domain::{lla_to_ecef, local_basis, AircraftState, Degrees, Kilometers, Vec3};
use serde::{Deserialize, Serialize};
use thiserror::Error;

const DIRECTIONAL_GRID_MAGIC: &[u8; 8] = b"MH370AG1";
const DIRECTIONAL_GRID_HEADER_BYTES: usize = 48;

mod directional;
pub use directional::*;

const FEET_TO_KM: f64 = 0.000_304_8;

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum PatternBasis {
    Measured,
    Synthetic,
}

#[derive(Debug, Clone, Copy, PartialEq, Serialize, Deserialize)]
pub struct AntennaPattern {
    pub basis: PatternBasis,
    pub peak_gain_dbi: f64,
    pub half_power_beamwidth_deg: f64,
    pub floor_gain_dbi: f64,
}

#[derive(Debug, Clone, Copy, PartialEq, Serialize, Deserialize)]
pub struct PowerObservation {
    pub observed_db: f64,
    /// All declared path terms other than aircraft antenna gain and the
    /// unresolved precompensation term.
    pub path_intercept_db: f64,
    pub standard_deviation_db: f64,
    pub precompensation_min_db: f64,
    pub precompensation_max_db: f64,
    pub permit_synthetic_pattern: bool,
}

#[derive(Debug, Clone, Copy, PartialEq, Serialize, Deserialize)]
pub struct AntennaGeometry {
    pub azimuth_relative_true_north: Degrees,
    pub elevation_above_horizon: Degrees,
    pub off_zenith: Degrees,
    pub gain_dbi: f64,
}

#[derive(Debug, Clone, Copy, PartialEq, Serialize, Deserialize)]
pub struct PowerScore {
    pub geometry: AntennaGeometry,
    pub marginalized_log_likelihood: Option<f64>,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum DirectionalPatternBasis {
    Commissioned,
    UnverifiedReconstruction,
}

#[derive(Debug, Clone, PartialEq)]
pub struct DirectionalGainGrid {
    pub basis: DirectionalPatternBasis,
    azimuth_count: usize,
    elevation_count: usize,
    azimuth_min_deg: f64,
    azimuth_step_deg: f64,
    elevation_min_deg: f64,
    elevation_step_deg: f64,
    gains_dbic: Vec<f32>,
}

#[derive(Debug, Clone, Copy, PartialEq, Serialize, Deserialize)]
pub struct ConditionalPowerObservation {
    pub observed_dbm: f64,
    /// Frozen event/channel prediction under full target-EIRP precompensation.
    pub full_precompensation_prediction_dbm: f64,
    pub standard_deviation_db: f64,
    pub reference_gain_dbic: f64,
    /// Zero is full precompensation; one is the no-precompensation endpoint.
    pub directional_departure_scale: f64,
    pub permit_unverified_reconstruction: bool,
}

/// Aircraft attitude used to rotate an Earth-local line of sight into the
/// antenna-pattern coordinate frame.
///
/// Heading is clockwise from true north, pitch is positive nose-up, and roll
/// is positive right-wing-down. The rotation is the aerospace yaw-pitch-roll
/// convention with body axes forward, right, and down.
#[derive(Debug, Clone, Copy, PartialEq, Serialize, Deserialize)]
pub struct AircraftAttitude {
    pub heading_true: Degrees,
    pub pitch_nose_up: Degrees,
    pub roll_right_wing_down: Degrees,
}

impl AircraftAttitude {
    /// Explicit straight-and-level attitude at the supplied true heading.
    pub const fn level(heading_true: Degrees) -> Self {
        Self {
            heading_true,
            pitch_nose_up: Degrees(0.0),
            roll_right_wing_down: Degrees(0.0),
        }
    }

    pub fn all_finite(self) -> bool {
        self.heading_true.is_finite()
            && self.pitch_nose_up.is_finite()
            && self.roll_right_wing_down.is_finite()
    }
}

#[derive(Debug, Clone, Copy, PartialEq, Serialize, Deserialize)]
pub struct DirectionalAntennaGeometry {
    pub azimuth_true: Degrees,
    /// Earth-local elevation above the WGS-84 horizon.
    pub elevation_above_horizon: Degrees,
    /// Azimuth about the aircraft down axis: zero forward, positive right.
    pub azimuth_relative_aircraft: Degrees,
    /// Elevation above the aircraft forward-right plane.
    pub elevation_relative_aircraft: Degrees,
    pub gain_dbic: f64,
}

#[derive(Debug, Clone, Copy, PartialEq, Serialize, Deserialize)]
pub struct ConditionalPowerScore {
    pub geometry: DirectionalAntennaGeometry,
    pub predicted_dbm: f64,
    pub log_likelihood: Option<f64>,
}

/// Physical return-link terms used by the audited target-EIRP workbook model.
/// Wavelengths are metres; positions and ranges in the evaluator are kilometres.
#[derive(Debug, Clone, Copy, PartialEq, Serialize, Deserialize)]
pub struct TargetEirpLinkModel {
    pub requested_eirp_dbw: f64,
    pub uplink_wavelength_m: f64,
    pub downlink_wavelength_m: f64,
    pub satellite_gt_constant_db: f64,
    pub satellite_gt_linear_db_per_deg: f64,
    pub satellite_gt_quadratic_db_per_deg2: f64,
    pub satellite_receiver_offset_db: f64,
    pub unit_conversion_db: f64,
}

#[derive(Debug, Clone, Copy, PartialEq, Serialize, Deserialize)]
pub struct TargetEirpPrediction {
    pub aircraft_satellite_range_km: f64,
    pub full_precompensation_prediction_dbm: f64,
}

#[derive(Debug, Error)]
pub enum AntennaError {
    #[error("invalid antenna pattern")]
    InvalidPattern,
    #[error("invalid power observation")]
    InvalidObservation,
    #[error("aircraft and satellite geometry is degenerate")]
    DegenerateGeometry,
    #[error("invalid directional antenna grid")]
    InvalidGrid,
    #[error("invalid aircraft attitude")]
    InvalidAttitude,
    #[error("satellite is below the Earth-local or antenna-pattern horizon")]
    BelowHorizon,
}

impl AntennaPattern {
    pub fn validate(&self) -> Result<(), AntennaError> {
        if ![
            self.peak_gain_dbi,
            self.half_power_beamwidth_deg,
            self.floor_gain_dbi,
        ]
        .iter()
        .all(|value| value.is_finite())
            || self.half_power_beamwidth_deg <= 0.0
            || self.floor_gain_dbi > self.peak_gain_dbi
        {
            return Err(AntennaError::InvalidPattern);
        }
        Ok(())
    }

    /// Axisymmetric synthetic pattern around aircraft zenith.
    ///
    /// A measured two-dimensional commissioned surface can replace this
    /// function behind the same geometry interface when available.
    pub fn gain_at_off_zenith(self, off_zenith_deg: f64) -> Result<f64, AntennaError> {
        self.validate()?;
        if !off_zenith_deg.is_finite() || !(0.0..=180.0).contains(&off_zenith_deg) {
            return Err(AntennaError::InvalidPattern);
        }
        let loss = 3.0 * (off_zenith_deg / (0.5 * self.half_power_beamwidth_deg)).powi(2);
        Ok((self.peak_gain_dbi - loss).max(self.floor_gain_dbi))
    }
}

pub fn geometry(
    aircraft: AircraftState,
    satellite_position_km: Vec3,
    pattern: AntennaPattern,
) -> Result<AntennaGeometry, AntennaError> {
    let aircraft_position = lla_to_ecef(
        aircraft.position,
        Kilometers(aircraft.altitude.0 * FEET_TO_KM),
    );
    let line_of_sight = (satellite_position_km - aircraft_position)
        .normalized()
        .ok_or(AntennaError::DegenerateGeometry)?;
    let (north, east, up) = local_basis(aircraft.position);
    let north_component = line_of_sight.dot(north);
    let east_component = line_of_sight.dot(east);
    let up_component = line_of_sight.dot(up).clamp(-1.0, 1.0);
    let azimuth = Degrees(east_component.atan2(north_component).to_degrees()).wrapped_360();
    let elevation = Degrees(up_component.asin().to_degrees());
    let off_zenith = Degrees(up_component.acos().to_degrees());
    let gain_dbi = pattern.gain_at_off_zenith(off_zenith.0)?;
    Ok(AntennaGeometry {
        azimuth_relative_true_north: azimuth,
        elevation_above_horizon: elevation,
        off_zenith,
        gain_dbi,
    })
}

fn logsumexp(values: &[f64]) -> f64 {
    let maximum = values.iter().copied().fold(f64::NEG_INFINITY, f64::max);
    maximum
        + values
            .iter()
            .map(|value| (value - maximum).exp())
            .sum::<f64>()
            .ln()
}

pub fn evaluate_power(
    aircraft: AircraftState,
    satellite_position_km: Vec3,
    pattern: AntennaPattern,
    observation: PowerObservation,
) -> Result<PowerScore, AntennaError> {
    if ![
        observation.observed_db,
        observation.path_intercept_db,
        observation.standard_deviation_db,
        observation.precompensation_min_db,
        observation.precompensation_max_db,
    ]
    .iter()
    .all(|value| value.is_finite())
        || observation.standard_deviation_db <= 0.0
        || observation.precompensation_max_db < observation.precompensation_min_db
    {
        return Err(AntennaError::InvalidObservation);
    }
    let geometry = geometry(aircraft, satellite_position_km, pattern)?;
    if pattern.basis == PatternBasis::Synthetic && !observation.permit_synthetic_pattern {
        return Ok(PowerScore {
            geometry,
            marginalized_log_likelihood: None,
        });
    }

    const QUADRATURE_POINTS: usize = 33;
    let mut values = Vec::with_capacity(QUADRATURE_POINTS);
    for index in 0..QUADRATURE_POINTS {
        let fraction = index as f64 / (QUADRATURE_POINTS - 1) as f64;
        let precompensation = observation.precompensation_min_db
            + fraction * (observation.precompensation_max_db - observation.precompensation_min_db);
        let predicted = observation.path_intercept_db + geometry.gain_dbi + precompensation;
        let residual = observation.observed_db - predicted;
        values.push(
            -0.5 * (residual / observation.standard_deviation_db).powi(2)
                - (observation.standard_deviation_db * (2.0 * std::f64::consts::PI).sqrt()).ln(),
        );
    }
    Ok(PowerScore {
        geometry,
        marginalized_log_likelihood: Some(logsumexp(&values) - (QUADRATURE_POINTS as f64).ln()),
    })
}

#[cfg(test)]
mod tests {
    use mh370_domain::{Feet, FeetPerMinute, Hertz, Knots, LatLon, Seconds};

    use super::*;

    fn aircraft() -> AircraftState {
        AircraftState {
            time: Seconds(0.0),
            position: LatLon::new(-30.0, 95.0).unwrap(),
            altitude: Feet(35_000.0),
            track_true: Degrees(180.0),
            ground_speed: Knots(480.0),
            vertical_speed: FeetPerMinute(0.0),
            bfo_bias: Hertz(150.0),
        }
    }

    #[test]
    fn synthetic_pattern_requires_explicit_likelihood_opt_in() {
        let pattern = AntennaPattern {
            basis: PatternBasis::Synthetic,
            peak_gain_dbi: 14.5,
            half_power_beamwidth_deg: 45.0,
            floor_gain_dbi: -10.0,
        };
        let satellite = Vec3::new(18_161.0, 38_060.0, 1_029.0);
        let observation = PowerObservation {
            observed_db: -100.0,
            path_intercept_db: -110.0,
            standard_deviation_db: 2.0,
            precompensation_min_db: -3.0,
            precompensation_max_db: 3.0,
            permit_synthetic_pattern: false,
        };
        let score = evaluate_power(aircraft(), satellite, pattern, observation).unwrap();
        assert!(score.geometry.gain_dbi <= pattern.peak_gain_dbi);
        assert!(score.marginalized_log_likelihood.is_none());
    }
}
