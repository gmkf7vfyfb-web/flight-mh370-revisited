use mh370_domain::{AircraftState, Hertz, Kilometers, LatLon, Microseconds, Vec3};
use serde::{Deserialize, Serialize};

use mh370_domain::{lla_to_ecef, local_basis};

const FT_TO_KM: f64 = 0.000_304_8;
const KM_PER_NM: f64 = 1.852;
const KT_TO_KM_S: f64 = KM_PER_NM / 3_600.0;
const FPM_TO_KM_S: f64 = FT_TO_KM / 60.0;

#[derive(Debug, Clone, Copy, PartialEq, Serialize, Deserialize)]
pub struct BtoConstants {
    pub speed_of_light_km_s: f64,
    pub nominal_delay_us: f64,
    pub channel_term_us: f64,
}

#[derive(Debug, Clone, Copy, PartialEq, Serialize, Deserialize)]
pub struct BfoConstants {
    pub satellite_afc_hz: f64,
    pub uplink_hz: f64,
    pub downlink_hz: f64,
    pub speed_of_light_km_s: f64,
    pub nominal_satellite_longitude_deg: f64,
    pub nominal_satellite_altitude_km: f64,
}

#[derive(Debug, Clone, Copy, PartialEq)]
pub struct BfoComponents {
    pub uplink: Hertz,
    pub downlink: Hertz,
    pub compensation: Hertz,
    pub satellite_afc: Hertz,
    pub base_without_bias: Hertz,
}

pub fn bto(
    position: LatLon,
    altitude_ft: f64,
    satellite_position_km: Vec3,
    ground_station_position_km: Vec3,
    constants: BtoConstants,
) -> Microseconds {
    let aircraft = lla_to_ecef(position, Kilometers(altitude_ft * FT_TO_KM));
    let satellite_aircraft_range = (satellite_position_km - aircraft).norm();
    let satellite_ground_range = (satellite_position_km - ground_station_position_km).norm();
    let propagation_us = 2.0 * (satellite_aircraft_range + satellite_ground_range)
        / constants.speed_of_light_km_s
        * 1e6;
    Microseconds(propagation_us - constants.nominal_delay_us + constants.channel_term_us)
}

pub fn bfo_components(
    state: AircraftState,
    satellite_position_km: Vec3,
    satellite_velocity_km_s: Vec3,
    ground_station_position_km: Vec3,
    constants: BfoConstants,
) -> BfoComponents {
    let aircraft = lla_to_ecef(state.position, Kilometers(state.altitude.0 * FT_TO_KM));
    let surface_aircraft = lla_to_ecef(state.position, Kilometers(0.0));
    let (north_basis, east_basis, up_basis) = local_basis(state.position);
    let velocity = state.velocity_enu();
    let horizontal_velocity =
        north_basis * (velocity.north.0 * KT_TO_KM_S) + east_basis * (velocity.east.0 * KT_TO_KM_S);
    let aircraft_velocity = horizontal_velocity + up_basis * (velocity.vertical.0 * FPM_TO_KM_S);

    let aircraft_to_satellite = (satellite_position_km - aircraft)
        .normalized()
        .expect("aircraft and satellite positions differ");
    let uplink = -constants.uplink_hz / constants.speed_of_light_km_s
        * (satellite_velocity_km_s - aircraft_velocity).dot(aircraft_to_satellite);

    let ground_to_satellite = (satellite_position_km - ground_station_position_km)
        .normalized()
        .expect("ground station and satellite positions differ");
    let downlink = -constants.downlink_hz / constants.speed_of_light_km_s
        * satellite_velocity_km_s.dot(ground_to_satellite);

    let nominal_satellite = lla_to_ecef(
        LatLon::new(0.0, constants.nominal_satellite_longitude_deg)
            .expect("valid nominal satellite longitude"),
        Kilometers(constants.nominal_satellite_altitude_km),
    );
    let nominal_to_aircraft = (surface_aircraft - nominal_satellite)
        .normalized()
        .expect("nominal satellite and surface position differ");
    let compensation = constants.uplink_hz / constants.speed_of_light_km_s
        * horizontal_velocity.dot(nominal_to_aircraft);
    let base = uplink + downlink + compensation + constants.satellite_afc_hz;

    BfoComponents {
        uplink: Hertz(uplink),
        downlink: Hertz(downlink),
        compensation: Hertz(compensation),
        satellite_afc: Hertz(constants.satellite_afc_hz),
        base_without_bias: Hertz(base),
    }
}

#[cfg(test)]
mod tests {
    use approx::assert_abs_diff_eq;
    use mh370_domain::{Degrees, Feet, FeetPerMinute, Knots, Seconds};

    use super::*;

    fn state(position: LatLon, altitude_ft: f64, north: f64, east: f64) -> AircraftState {
        let speed = north.hypot(east);
        let track = east.atan2(north).to_degrees();
        AircraftState {
            time: Seconds(0.0),
            position,
            altitude: Feet(altitude_ft),
            track_true: Degrees(track),
            ground_speed: Knots(speed),
            vertical_speed: FeetPerMinute(0.0),
            bfo_bias: Hertz(0.0),
        }
    }

    #[test]
    fn bto_matches_frozen_scalar_regression_fixture() {
        let satellite = Vec3::new(18_161.906_97, 38_060.473_36, 1_029.903_202);
        let ground = Vec3::new(-2_368.8, 4_881.1, -3_342.0);
        let value = bto(
            LatLon::new(-10.0, 85.0).unwrap(),
            25_000.0,
            satellite,
            ground,
            BtoConstants {
                speed_of_light_km_s: 299_792.458,
                nominal_delay_us: 499_962.0,
                channel_term_us: 4_283.0,
            },
        );
        assert_abs_diff_eq!(value.0, 9_151.491_113_446_828, epsilon = 2e-9);
    }

    #[test]
    fn physical_doppler_sign_and_altitude_limit_hold() {
        let ground_position = LatLon::new(0.0, 0.0).unwrap();
        let ground = lla_to_ecef(ground_position, Kilometers(0.0));
        let satellite = lla_to_ecef(LatLon::new(0.0, 10.0).unwrap(), Kilometers(35_786.0));
        let constants = BfoConstants {
            satellite_afc_hz: 0.0,
            uplink_hz: 1_646_652_500.0,
            downlink_hz: 3_615_152_500.0,
            speed_of_light_km_s: 299_792.458,
            nominal_satellite_longitude_deg: 64.5,
            nominal_satellite_altitude_km: 36_210.12,
        };
        let toward = bfo_components(
            state(ground_position, 0.0, 0.0, 500.0),
            satellite,
            Vec3::default(),
            ground,
            constants,
        );
        let away = bfo_components(
            state(ground_position, 0.0, 0.0, -500.0),
            satellite,
            Vec3::default(),
            ground,
            constants,
        );
        assert!(toward.uplink.0 > away.uplink.0);

        let bto_constants = BtoConstants {
            speed_of_light_km_s: 299_792.458,
            nominal_delay_us: 0.0,
            channel_term_us: 0.0,
        };
        let low = bto(ground_position, 0.0, satellite, ground, bto_constants);
        let high = bto(ground_position, 40_000.0, satellite, ground, bto_constants);
        assert!(high.0 < low.0);
    }
}
