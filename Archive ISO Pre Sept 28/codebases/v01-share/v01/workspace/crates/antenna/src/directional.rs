use mh370_domain::{lla_to_ecef, local_basis, AircraftState, Degrees, Kilometers, Vec3};

use super::{
    AircraftAttitude, AntennaError, ConditionalPowerObservation, ConditionalPowerScore,
    DirectionalAntennaGeometry, DirectionalGainGrid, DirectionalPatternBasis, TargetEirpLinkModel,
    TargetEirpPrediction, DIRECTIONAL_GRID_HEADER_BYTES, DIRECTIONAL_GRID_MAGIC, FEET_TO_KM,
};

impl DirectionalGainGrid {
    /// Parse the compact, little-endian runtime grid.
    ///
    /// Layout: 8-byte magic; azimuth/elevation counts as u32; axis minima and
    /// steps as four f64 values; then azimuth-fast f32 gain values.
    pub fn parse(bytes: &[u8], basis: DirectionalPatternBasis) -> Result<Self, AntennaError> {
        if bytes.len() < DIRECTIONAL_GRID_HEADER_BYTES || &bytes[..8] != DIRECTIONAL_GRID_MAGIC {
            return Err(AntennaError::InvalidGrid);
        }
        let read_u32 = |offset: usize| {
            bytes
                .get(offset..offset + 4)
                .and_then(|value| value.try_into().ok())
                .map(u32::from_le_bytes)
                .ok_or(AntennaError::InvalidGrid)
        };
        let read_f64 = |offset: usize| {
            bytes
                .get(offset..offset + 8)
                .and_then(|value| value.try_into().ok())
                .map(f64::from_le_bytes)
                .ok_or(AntennaError::InvalidGrid)
        };
        let azimuth_count = read_u32(8)? as usize;
        let elevation_count = read_u32(12)? as usize;
        let azimuth_min_deg = read_f64(16)?;
        let azimuth_step_deg = read_f64(24)?;
        let elevation_min_deg = read_f64(32)?;
        let elevation_step_deg = read_f64(40)?;
        let count = azimuth_count
            .checked_mul(elevation_count)
            .ok_or(AntennaError::InvalidGrid)?;
        if azimuth_count < 2
            || elevation_count < 2
            || ![
                azimuth_min_deg,
                azimuth_step_deg,
                elevation_min_deg,
                elevation_step_deg,
            ]
            .iter()
            .all(|value| value.is_finite())
            || azimuth_step_deg <= 0.0
            || elevation_step_deg <= 0.0
            || bytes.len() != DIRECTIONAL_GRID_HEADER_BYTES + 4 * count
        {
            return Err(AntennaError::InvalidGrid);
        }
        let azimuth_max_deg = azimuth_min_deg + azimuth_step_deg * (azimuth_count - 1) as f64;
        let elevation_max_deg =
            elevation_min_deg + elevation_step_deg * (elevation_count - 1) as f64;
        if (azimuth_min_deg + 180.0).abs() > 1e-9
            || (azimuth_max_deg - 180.0).abs() > 1e-9
            || elevation_min_deg.abs() > 1e-9
            || (elevation_max_deg - 90.0).abs() > 1e-9
        {
            return Err(AntennaError::InvalidGrid);
        }
        let mut gains_dbic = Vec::with_capacity(count);
        for chunk in bytes[DIRECTIONAL_GRID_HEADER_BYTES..].chunks_exact(4) {
            let value =
                f32::from_le_bytes(chunk.try_into().map_err(|_| AntennaError::InvalidGrid)?);
            if !value.is_finite() {
                return Err(AntennaError::InvalidGrid);
            }
            gains_dbic.push(value);
        }
        Ok(Self {
            basis,
            azimuth_count,
            elevation_count,
            azimuth_min_deg,
            azimuth_step_deg,
            elevation_min_deg,
            elevation_step_deg,
            gains_dbic,
        })
    }

    pub fn gain_dbic(
        &self,
        azimuth_relative_aircraft_deg: f64,
        elevation_above_horizon_deg: f64,
    ) -> Result<f64, AntennaError> {
        if !azimuth_relative_aircraft_deg.is_finite()
            || !elevation_above_horizon_deg.is_finite()
            || !(0.0..=90.0).contains(&elevation_above_horizon_deg)
        {
            return Err(AntennaError::InvalidGrid);
        }
        let azimuth = (azimuth_relative_aircraft_deg + 180.0).rem_euclid(360.0) - 180.0;
        let azimuth_index = (azimuth - self.azimuth_min_deg) / self.azimuth_step_deg;
        let elevation_index =
            (elevation_above_horizon_deg - self.elevation_min_deg) / self.elevation_step_deg;
        let azimuth_low = azimuth_index.floor() as usize;
        let elevation_low = elevation_index.floor() as usize;
        let azimuth_high = (azimuth_low + 1).min(self.azimuth_count - 1);
        let elevation_high = (elevation_low + 1).min(self.elevation_count - 1);
        let azimuth_fraction = azimuth_index - azimuth_low as f64;
        let elevation_fraction = elevation_index - elevation_low as f64;
        let at = |azimuth: usize, elevation: usize| {
            self.gains_dbic[elevation * self.azimuth_count + azimuth] as f64
        };
        let lower = at(azimuth_low, elevation_low) * (1.0 - azimuth_fraction)
            + at(azimuth_high, elevation_low) * azimuth_fraction;
        let upper = at(azimuth_low, elevation_high) * (1.0 - azimuth_fraction)
            + at(azimuth_high, elevation_high) * azimuth_fraction;
        Ok(lower * (1.0 - elevation_fraction) + upper * elevation_fraction)
    }
}

pub fn directional_geometry(
    aircraft: AircraftState,
    attitude: AircraftAttitude,
    satellite_position_km: Vec3,
    grid: &DirectionalGainGrid,
) -> Result<DirectionalAntennaGeometry, AntennaError> {
    if !attitude.all_finite() {
        return Err(AntennaError::InvalidAttitude);
    }
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
    let azimuth_true = Degrees(east_component.atan2(north_component).to_degrees()).wrapped_360();
    let earth_elevation = Degrees(
        up_component
            .atan2(north_component.hypot(east_component))
            .to_degrees(),
    );
    if !(0.0..=90.0).contains(&earth_elevation.0) {
        return Err(AntennaError::BelowHorizon);
    }

    // Rotate local NED line-of-sight coordinates into aerospace body axes.
    // C_bn = R_z(heading) R_y(pitch) R_x(roll); dotting the NED LOS with
    // C_bn's columns applies C_nb = C_bn^T. Body z is positive down.
    let heading = attitude.heading_true.to_radians();
    let pitch = attitude.pitch_nose_up.to_radians();
    let roll = attitude.roll_right_wing_down.to_radians();
    let (sin_heading, cos_heading) = heading.sin_cos();
    let (sin_pitch, cos_pitch) = pitch.sin_cos();
    let (sin_roll, cos_roll) = roll.sin_cos();
    let line_of_sight_ned = Vec3::new(north_component, east_component, -up_component);
    let forward_ned = Vec3::new(cos_pitch * cos_heading, cos_pitch * sin_heading, -sin_pitch);
    let right_ned = Vec3::new(
        sin_roll * sin_pitch * cos_heading - cos_roll * sin_heading,
        sin_roll * sin_pitch * sin_heading + cos_roll * cos_heading,
        sin_roll * cos_pitch,
    );
    let down_ned = Vec3::new(
        cos_roll * sin_pitch * cos_heading + sin_roll * sin_heading,
        cos_roll * sin_pitch * sin_heading - sin_roll * cos_heading,
        cos_roll * cos_pitch,
    );
    let forward_component = line_of_sight_ned.dot(forward_ned);
    let right_component = line_of_sight_ned.dot(right_ned);
    let down_component = line_of_sight_ned.dot(down_ned);
    let azimuth_relative_aircraft =
        Degrees(right_component.atan2(forward_component).to_degrees()).wrapped_180();
    let elevation_relative_aircraft = Degrees(
        (-down_component)
            .atan2(forward_component.hypot(right_component))
            .to_degrees(),
    );
    if !(0.0..=90.0).contains(&elevation_relative_aircraft.0) {
        return Err(AntennaError::BelowHorizon);
    }
    let gain_dbic = grid.gain_dbic(azimuth_relative_aircraft.0, elevation_relative_aircraft.0)?;
    Ok(DirectionalAntennaGeometry {
        azimuth_true,
        elevation_above_horizon: earth_elevation,
        azimuth_relative_aircraft,
        elevation_relative_aircraft,
        gain_dbic,
    })
}

pub fn evaluate_conditional_power(
    aircraft: AircraftState,
    attitude: AircraftAttitude,
    satellite_position_km: Vec3,
    grid: &DirectionalGainGrid,
    observation: ConditionalPowerObservation,
) -> Result<ConditionalPowerScore, AntennaError> {
    if ![
        observation.observed_dbm,
        observation.full_precompensation_prediction_dbm,
        observation.standard_deviation_db,
        observation.reference_gain_dbic,
        observation.directional_departure_scale,
    ]
    .iter()
    .all(|value| value.is_finite())
        || observation.standard_deviation_db <= 0.0
        || !(0.0..=1.0).contains(&observation.directional_departure_scale)
    {
        return Err(AntennaError::InvalidObservation);
    }
    let geometry = directional_geometry(aircraft, attitude, satellite_position_km, grid)?;
    let predicted_dbm = observation.full_precompensation_prediction_dbm
        + observation.directional_departure_scale
            * (geometry.gain_dbic - observation.reference_gain_dbic);
    if grid.basis == DirectionalPatternBasis::UnverifiedReconstruction
        && !observation.permit_unverified_reconstruction
    {
        return Ok(ConditionalPowerScore {
            geometry,
            predicted_dbm,
            log_likelihood: None,
        });
    }
    let residual = observation.observed_dbm - predicted_dbm;
    let standard_deviation = observation.standard_deviation_db;
    Ok(ConditionalPowerScore {
        geometry,
        predicted_dbm,
        log_likelihood: Some(
            -0.5 * (residual / standard_deviation).powi(2)
                - (standard_deviation * (2.0 * std::f64::consts::PI).sqrt()).ln(),
        ),
    })
}

fn free_space_gain_db(wavelength_m: f64, range_km: f64) -> f64 {
    20.0 * (wavelength_m / (4.0 * std::f64::consts::PI * range_km * 1_000.0)).log10()
}

fn target_eirp_prediction_from_ranges(
    aircraft_satellite_range_km: f64,
    satellite_ground_range_km: f64,
    aircraft_geocentric_radius_km: f64,
    satellite_geocentric_radius_km: f64,
    model: TargetEirpLinkModel,
) -> Result<f64, AntennaError> {
    if ![
        aircraft_satellite_range_km,
        satellite_ground_range_km,
        aircraft_geocentric_radius_km,
        satellite_geocentric_radius_km,
        model.requested_eirp_dbw,
        model.uplink_wavelength_m,
        model.downlink_wavelength_m,
        model.satellite_gt_constant_db,
        model.satellite_gt_linear_db_per_deg,
        model.satellite_gt_quadratic_db_per_deg2,
        model.satellite_receiver_offset_db,
        model.unit_conversion_db,
    ]
    .iter()
    .all(|value| value.is_finite())
        || aircraft_satellite_range_km <= 0.0
        || satellite_ground_range_km <= 0.0
        || aircraft_geocentric_radius_km <= 0.0
        || satellite_geocentric_radius_km <= 0.0
        || model.uplink_wavelength_m <= 0.0
        || model.downlink_wavelength_m <= 0.0
    {
        return Err(AntennaError::InvalidObservation);
    }
    let denominator = 2.0 * aircraft_geocentric_radius_km * aircraft_satellite_range_km;
    let elevation_argument = ((aircraft_geocentric_radius_km.powi(2)
        + aircraft_satellite_range_km.powi(2)
        - satellite_geocentric_radius_km.powi(2))
        / denominator)
        .clamp(-1.0, 1.0);
    let elevation_deg = elevation_argument.acos().to_degrees() - 90.0;
    let satellite_gt_db = model.satellite_gt_constant_db
        + model.satellite_gt_linear_db_per_deg * elevation_deg
        + model.satellite_gt_quadratic_db_per_deg2 * elevation_deg.powi(2);
    Ok(model.requested_eirp_dbw
        + free_space_gain_db(model.uplink_wavelength_m, aircraft_satellite_range_km)
        + satellite_gt_db
        + model.satellite_receiver_offset_db
        + free_space_gain_db(model.downlink_wavelength_m, satellite_ground_range_km)
        + model.unit_conversion_db)
}

pub fn target_eirp_prediction(
    aircraft: AircraftState,
    satellite_position_km: Vec3,
    ground_station_position_km: Vec3,
    model: TargetEirpLinkModel,
) -> Result<TargetEirpPrediction, AntennaError> {
    let aircraft_position = lla_to_ecef(
        aircraft.position,
        Kilometers(aircraft.altitude.0 * FEET_TO_KM),
    );
    let aircraft_satellite_range_km = (satellite_position_km - aircraft_position).norm();
    let full_precompensation_prediction_dbm = target_eirp_prediction_from_ranges(
        aircraft_satellite_range_km,
        (satellite_position_km - ground_station_position_km).norm(),
        aircraft_position.norm(),
        satellite_position_km.norm(),
        model,
    )?;
    Ok(TargetEirpPrediction {
        aircraft_satellite_range_km,
        full_precompensation_prediction_dbm,
    })
}

#[cfg(test)]
mod tests {
    use super::*;
    use mh370_domain::{Feet, FeetPerMinute, Hertz, Knots, LatLon, Seconds};

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

    fn test_grid() -> DirectionalGainGrid {
        let mut bytes = Vec::new();
        bytes.extend_from_slice(DIRECTIONAL_GRID_MAGIC);
        bytes.extend_from_slice(&3_u32.to_le_bytes());
        bytes.extend_from_slice(&3_u32.to_le_bytes());
        bytes.extend_from_slice(&(-180.0_f64).to_le_bytes());
        bytes.extend_from_slice(&(180.0_f64).to_le_bytes());
        bytes.extend_from_slice(&0.0_f64.to_le_bytes());
        bytes.extend_from_slice(&45.0_f64.to_le_bytes());
        for elevation in [0.0_f32, 45.0, 90.0] {
            for azimuth in [-180.0_f32, 0.0, 180.0] {
                let gain = 10.0 + elevation / 90.0 + azimuth.abs() / 180.0;
                bytes.extend_from_slice(&gain.to_le_bytes());
            }
        }
        DirectionalGainGrid::parse(&bytes, DirectionalPatternBasis::UnverifiedReconstruction)
            .unwrap()
    }

    fn satellite_at_local_look(azimuth_true_deg: f64, elevation_deg: f64) -> Vec3 {
        let state = aircraft();
        let position = lla_to_ecef(state.position, Kilometers(state.altitude.0 * FEET_TO_KM));
        let (north, east, up) = local_basis(state.position);
        let azimuth = azimuth_true_deg.to_radians();
        let elevation = elevation_deg.to_radians();
        position
            + north * (elevation.cos() * azimuth.cos() * 40_000.0)
            + east * (elevation.cos() * azimuth.sin() * 40_000.0)
            + up * (elevation.sin() * 40_000.0)
    }

    #[test]
    fn target_eirp_link_reproduces_audited_workbook_row() {
        let model = TargetEirpLinkModel {
            requested_eirp_dbw: 10.5,
            uplink_wavelength_m: 0.182_061_8,
            downlink_wavelength_m: 0.083_275_7,
            satellite_gt_constant_db: -11.5,
            satellite_gt_linear_db_per_deg: 0.013_96,
            satellite_gt_quadratic_db_per_deg2: 1.535e-4,
            satellite_receiver_offset_db: 27.5,
            unit_conversion_db: 300.0,
        };
        let prediction = target_eirp_prediction_from_ranges(
            37_393.293_464_289_4,
            39_250.174_336_825_35,
            6_388.616_613_574_213,
            42_182.305_909_463_62,
            model,
        )
        .unwrap();
        assert!((prediction - (-56.235_803_534_946_1)).abs() < 1e-10);
    }

    #[test]
    fn grid_interpolates_and_requires_explicit_opt_in() {
        let grid = test_grid();
        assert!((grid.gain_dbic(-90.0, 22.5).unwrap() - 10.75).abs() < 1e-6);
        let satellite = Vec3::new(18_161.0, 38_060.0, 1_029.0);
        let first = directional_geometry(
            aircraft(),
            AircraftAttitude::level(Degrees(180.0)),
            satellite,
            &grid,
        )
        .unwrap();
        let second = directional_geometry(
            aircraft(),
            AircraftAttitude::level(Degrees(200.0)),
            satellite,
            &grid,
        )
        .unwrap();
        assert!(
            (first.azimuth_relative_aircraft.0 - second.azimuth_relative_aircraft.0 - 20.0).abs()
                < 1e-9
        );
        let below_horizon = Vec3::new(-18_161.0, -38_060.0, -1_029.0);
        assert!(matches!(
            directional_geometry(
                aircraft(),
                AircraftAttitude::level(Degrees(180.0)),
                below_horizon,
                &grid
            ),
            Err(AntennaError::BelowHorizon)
        ));
        let observation = ConditionalPowerObservation {
            observed_dbm: -55.0,
            full_precompensation_prediction_dbm: -56.0,
            standard_deviation_db: 2.0,
            reference_gain_dbic: 12.16,
            directional_departure_scale: 1.0,
            permit_unverified_reconstruction: false,
        };
        let score = evaluate_conditional_power(
            aircraft(),
            AircraftAttitude::level(Degrees(180.0)),
            satellite,
            &grid,
            observation,
        )
        .unwrap();
        assert!(score.log_likelihood.is_none());
    }

    #[test]
    fn attitude_rotation_matches_independent_limiting_cases() {
        let grid = test_grid();

        // A level aircraft at 040 degrees sees an Earth-local 070/25-degree
        // look direction at body azimuth/elevation 030/25 degrees.
        let level = directional_geometry(
            aircraft(),
            AircraftAttitude::level(Degrees(40.0)),
            satellite_at_local_look(70.0, 25.0),
            &grid,
        )
        .unwrap();
        assert!((level.azimuth_relative_aircraft.0 - 30.0).abs() < 1e-10);
        assert!((level.elevation_relative_aircraft.0 - 25.0).abs() < 1e-10);
        assert!((level.elevation_above_horizon.0 - 25.0).abs() < 1e-10);

        // With the satellite directly ahead, ten degrees nose-up subtracts
        // ten degrees from its elevation in body coordinates.
        let pitched = directional_geometry(
            aircraft(),
            AircraftAttitude {
                heading_true: Degrees(40.0),
                pitch_nose_up: Degrees(10.0),
                roll_right_wing_down: Degrees(0.0),
            },
            satellite_at_local_look(40.0, 25.0),
            &grid,
        )
        .unwrap();
        assert!(pitched.azimuth_relative_aircraft.0.abs() < 1e-10);
        assert!((pitched.elevation_relative_aircraft.0 - 15.0).abs() < 1e-10);

        // A right-wing-down roll raises a look direction on the right by the
        // roll angle in body coordinates: 30 + 20 = 50 degrees.
        let rolled = directional_geometry(
            aircraft(),
            AircraftAttitude {
                heading_true: Degrees(40.0),
                pitch_nose_up: Degrees(0.0),
                roll_right_wing_down: Degrees(20.0),
            },
            satellite_at_local_look(130.0, 30.0),
            &grid,
        )
        .unwrap();
        assert!((rolled.azimuth_relative_aircraft.0 - 90.0).abs() < 1e-10);
        assert!((rolled.elevation_relative_aircraft.0 - 50.0).abs() < 1e-10);
    }
}
