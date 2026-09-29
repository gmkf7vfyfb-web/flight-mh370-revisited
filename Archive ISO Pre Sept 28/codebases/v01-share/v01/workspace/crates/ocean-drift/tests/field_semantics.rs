use mh370_domain::LatLon;
use mh370_ocean_drift::{FieldError, GriddedField};

fn monthly_field(error_with_missing_corner: bool) -> GriddedField {
    let mut bytes = b"MHGRID1\0".to_vec();
    bytes.extend(1u32.to_le_bytes());
    bytes.extend(1u32.to_le_bytes());
    for value in [12u32, 2, 2, 3] {
        bytes.extend(value.to_le_bytes());
    }
    for month in 0..12 {
        bytes.extend((month as f64).to_le_bytes());
    }
    for value in [-1.0_f64, 1.0, 10.0, 12.0] {
        bytes.extend(value.to_le_bytes());
    }
    for (name, value) in [("u", 0.0_f32), ("v", 0.0), ("u_error", 0.1)] {
        let mut encoded = [0u8; 16];
        encoded[..name.len()].copy_from_slice(name.as_bytes());
        bytes.extend(encoded);
        for index in 0..48 {
            let value = if name == "u" {
                (index / 4) as f32
            } else if name == "u_error" && error_with_missing_corner && index == 0 {
                f32::NAN
            } else {
                value
            };
            bytes.extend(value.to_le_bytes());
        }
    }
    GriddedField::from_bytes("monthly semantics", &bytes).unwrap()
}

#[test]
fn monthly_means_are_piecewise_and_december_does_not_blend_into_january() {
    let field = monthly_field(false);
    let position = LatLon::new(0.0, 11.0).unwrap();
    // 2014-12-31 23:59:59 UTC and 2015-01-01 00:00:00 UTC.
    assert_eq!(
        field.interpolate("u", 1_420_070_399.0, position).unwrap(),
        11.0
    );
    assert_eq!(
        field.interpolate("u", 1_420_070_400.0, position).unwrap(),
        0.0
    );
}

#[test]
fn missing_error_corners_are_not_silently_replaced_with_zero() {
    let field = monthly_field(true);
    let error = field
        .velocity(1_388_534_400.0, LatLon::new(0.0, 11.0).unwrap())
        .unwrap_err();
    assert_eq!(error, FieldError::MissingValue);
}
