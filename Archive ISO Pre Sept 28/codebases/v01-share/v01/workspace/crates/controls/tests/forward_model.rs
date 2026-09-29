use approx::assert_abs_diff_eq;
use mh370_domain::{destination_wgs84, lla_to_ecef};
use mh370_domain::{
    AircraftState, Degrees, Feet, FeetPerMinute, Hertz, Kilometers, Knots, LatLon, Seconds, Vec3,
};
use mh370_satcom::{bfo_components, bto, BfoConstants, BtoConstants};
use serde_json::Value;

fn numbers(value: &Value) -> Vec<f64> {
    value
        .as_array()
        .unwrap()
        .iter()
        .map(|item| item.as_f64().unwrap())
        .collect()
}

#[test]
fn rust_forward_model_matches_hash_pinned_python_scalar_fixture() {
    let document: Value = serde_json::from_str(include_str!(
        "../../../inputs/controls/forward-model-golden.json"
    ))
    .unwrap();
    assert_eq!(
        document["source"]["sha256"].as_str().unwrap(),
        "1f9d6186c6f6ad7eae28a02daf9ea30fc4e6cf3f0dd134f2f8db91545349e96f"
    );

    let fixture = &document["fixture"];
    let expected = &document["expected"];
    let latitudes = numbers(&fixture["latitude_deg"]);
    let longitudes = numbers(&fixture["longitude_deg"]);
    let altitudes = numbers(&fixture["altitude_ft"]);
    let north = numbers(&fixture["north_velocity_kt"]);
    let east = numbers(&fixture["east_velocity_kt"]);
    let vertical = numbers(&fixture["vertical_velocity_fpm"]);
    let satellite_values = numbers(&fixture["satellite_position_km"]);
    let satellite_velocity_values = numbers(&fixture["satellite_velocity_km_s"]);
    let ground_values = numbers(&fixture["ground_station_position_km"]);
    let satellite = Vec3::new(
        satellite_values[0],
        satellite_values[1],
        satellite_values[2],
    );
    let satellite_velocity = Vec3::new(
        satellite_velocity_values[0],
        satellite_velocity_values[1],
        satellite_velocity_values[2],
    );
    let ground = Vec3::new(ground_values[0], ground_values[1], ground_values[2]);
    let expected_ecef = expected["ecef_km"].as_array().unwrap();
    let expected_bto = numbers(&expected["bto_us"]);
    let expected_uplink = numbers(&expected["bfo_uplink_hz"]);
    let expected_downlink = numbers(&expected["bfo_downlink_hz"]);
    let expected_compensation = numbers(&expected["bfo_compensation_hz"]);
    let expected_base = numbers(&expected["bfo_base_without_bias_hz"]);

    let bto_constants = BtoConstants {
        speed_of_light_km_s: 299_792.458,
        nominal_delay_us: 499_962.0,
        channel_term_us: 4_283.0,
    };
    let bfo_constants = BfoConstants {
        satellite_afc_hz: -18.075_833_333_333,
        uplink_hz: 1_646_652_500.0,
        downlink_hz: 3_615_152_500.0,
        speed_of_light_km_s: 299_792.458,
        nominal_satellite_longitude_deg: 64.5,
        nominal_satellite_altitude_km: 36_210.12,
    };

    for index in 0..latitudes.len() {
        let position = LatLon::new(latitudes[index], longitudes[index]).unwrap();
        let expected_point = numbers(&expected_ecef[index]);
        let point = lla_to_ecef(position, Kilometers(altitudes[index] * 0.000_304_8));
        assert_abs_diff_eq!(point.x, expected_point[0], epsilon = 2e-12);
        assert_abs_diff_eq!(point.y, expected_point[1], epsilon = 2e-12);
        assert_abs_diff_eq!(point.z, expected_point[2], epsilon = 2e-12);

        let bto_value = bto(position, altitudes[index], satellite, ground, bto_constants);
        assert_abs_diff_eq!(bto_value.0, expected_bto[index], epsilon = 2e-9);

        let speed = north[index].hypot(east[index]);
        let state = AircraftState {
            time: Seconds(0.0),
            position,
            altitude: Feet(altitudes[index]),
            track_true: Degrees(east[index].atan2(north[index]).to_degrees()),
            ground_speed: Knots(speed),
            vertical_speed: FeetPerMinute(vertical[index]),
            bfo_bias: Hertz(0.0),
        };
        let components =
            bfo_components(state, satellite, satellite_velocity, ground, bfo_constants);
        assert_abs_diff_eq!(components.uplink.0, expected_uplink[index], epsilon = 2e-10);
        assert_abs_diff_eq!(
            components.downlink.0,
            expected_downlink[index],
            epsilon = 2e-10
        );
        assert_abs_diff_eq!(
            components.compensation.0,
            expected_compensation[index],
            epsilon = 2e-10
        );
        assert_abs_diff_eq!(
            components.base_without_bias.0,
            expected_base[index],
            epsilon = 2e-10
        );
    }

    let destination = &expected["wgs84_destination"];
    let result = destination_wgs84(
        LatLon::new(
            destination["start_latitude_deg"].as_f64().unwrap(),
            destination["start_longitude_deg"].as_f64().unwrap(),
        )
        .unwrap(),
        Degrees(destination["bearing_deg"].as_f64().unwrap()),
        mh370_domain::NauticalMiles(destination["distance_nm"].as_f64().unwrap()),
    )
    .unwrap();
    assert_abs_diff_eq!(
        result.latitude.0,
        destination["latitude_deg"].as_f64().unwrap(),
        epsilon = 2e-12
    );
    assert_abs_diff_eq!(
        result.longitude.0,
        destination["longitude_deg"].as_f64().unwrap(),
        epsilon = 2e-12
    );
}
