use crate::{Degrees, Kilometers, LatLon, NauticalMiles, Vec3};
use thiserror::Error;

pub const WGS84_A_KM: f64 = 6_378.137;
pub const WGS84_F: f64 = 1.0 / 298.257_223_563;
pub const WGS84_B_KM: f64 = WGS84_A_KM * (1.0 - WGS84_F);
pub const WGS84_E2: f64 = WGS84_F * (2.0 - WGS84_F);
pub const LEGACY_SPHERE_RADIUS_NM: f64 = 3_440.065;
pub const KM_PER_NM: f64 = 1.852;

#[derive(Debug, Error, Clone, PartialEq)]
pub enum GeodesyError {
    #[error("geodesic input is not finite")]
    NonFinite,
    #[error("geodesic distance {0} NM is negative")]
    NegativeDistance(f64),
    #[error("Vincenty direct solution did not converge")]
    DidNotConverge,
    #[error("cannot normalize a zero-length direction vector")]
    ZeroDirection,
}

pub fn lla_to_ecef(position: LatLon, altitude: Kilometers) -> Vec3 {
    let latitude = position.latitude.to_radians();
    let longitude = position.longitude.to_radians();
    let sin_latitude = latitude.sin();
    let cos_latitude = latitude.cos();
    let prime_vertical = WGS84_A_KM / (1.0 - WGS84_E2 * sin_latitude.powi(2)).sqrt();
    Vec3::new(
        (prime_vertical + altitude.0) * cos_latitude * longitude.cos(),
        (prime_vertical + altitude.0) * cos_latitude * longitude.sin(),
        (prime_vertical * (1.0 - WGS84_E2) + altitude.0) * sin_latitude,
    )
}

pub fn local_basis(position: LatLon) -> (Vec3, Vec3, Vec3) {
    let latitude = position.latitude.to_radians();
    let longitude = position.longitude.to_radians();
    let (sin_latitude, cos_latitude) = latitude.sin_cos();
    let (sin_longitude, cos_longitude) = longitude.sin_cos();
    let north = Vec3::new(
        -sin_latitude * cos_longitude,
        -sin_latitude * sin_longitude,
        cos_latitude,
    );
    let east = Vec3::new(-sin_longitude, cos_longitude, 0.0);
    let up = Vec3::new(
        cos_latitude * cos_longitude,
        cos_latitude * sin_longitude,
        sin_latitude,
    );
    (north, east, up)
}

pub fn destination_sphere(
    start: LatLon,
    bearing: Degrees,
    distance: NauticalMiles,
) -> Result<LatLon, GeodesyError> {
    if !start.latitude.is_finite()
        || !start.longitude.is_finite()
        || !bearing.is_finite()
        || !distance.is_finite()
    {
        return Err(GeodesyError::NonFinite);
    }
    if distance.0 < 0.0 {
        return Err(GeodesyError::NegativeDistance(distance.0));
    }
    let latitude = start.latitude.to_radians();
    let longitude = start.longitude.to_radians();
    let bearing = bearing.to_radians();
    let angular = distance.0 / LEGACY_SPHERE_RADIUS_NM;
    let latitude_2 = (latitude.sin() * angular.cos()
        + latitude.cos() * angular.sin() * bearing.cos())
    .clamp(-1.0, 1.0)
    .asin();
    let longitude_2 = longitude
        + (bearing.sin() * angular.sin() * latitude.cos())
            .atan2(angular.cos() - latitude.sin() * latitude_2.sin());
    LatLon::new(latitude_2.to_degrees(), longitude_2.to_degrees())
        .map_err(|_| GeodesyError::NonFinite)
}

pub fn destination_wgs84(
    start: LatLon,
    bearing: Degrees,
    distance: NauticalMiles,
) -> Result<LatLon, GeodesyError> {
    if !start.latitude.is_finite()
        || !start.longitude.is_finite()
        || !bearing.is_finite()
        || !distance.is_finite()
    {
        return Err(GeodesyError::NonFinite);
    }
    if distance.0 < 0.0 {
        return Err(GeodesyError::NegativeDistance(distance.0));
    }
    if distance.0 == 0.0 {
        return Ok(start);
    }

    let distance_km = distance.0 * KM_PER_NM;
    let phi_1 = start.latitude.to_radians();
    let alpha_1 = bearing.to_radians();
    let tangent_u_1 = (1.0 - WGS84_F) * phi_1.tan();
    let cos_u_1 = 1.0 / (1.0 + tangent_u_1.powi(2)).sqrt();
    let sin_u_1 = tangent_u_1 * cos_u_1;
    let sigma_1 = tangent_u_1.atan2(alpha_1.cos());
    let sin_alpha = cos_u_1 * alpha_1.sin();
    let cos_sq_alpha = (1.0 - sin_alpha.powi(2)).max(0.0);
    let u_sq = cos_sq_alpha * (WGS84_A_KM.powi(2) - WGS84_B_KM.powi(2)) / WGS84_B_KM.powi(2);
    let coefficient_a =
        1.0 + u_sq / 16_384.0 * (4_096.0 + u_sq * (-768.0 + u_sq * (320.0 - 175.0 * u_sq)));
    let coefficient_b = u_sq / 1_024.0 * (256.0 + u_sq * (-128.0 + u_sq * (74.0 - 47.0 * u_sq)));

    let mut sigma = distance_km / (WGS84_B_KM * coefficient_a);
    let mut converged = false;
    for _ in 0..100 {
        let two_sigma_m = 2.0 * sigma_1 + sigma;
        let (sin_sigma, cos_sigma) = sigma.sin_cos();
        let cos_two_sigma_m = two_sigma_m.cos();
        let delta_sigma = coefficient_b
            * sin_sigma
            * (cos_two_sigma_m
                + coefficient_b / 4.0
                    * (cos_sigma * (-1.0 + 2.0 * cos_two_sigma_m.powi(2))
                        - coefficient_b / 6.0
                            * cos_two_sigma_m
                            * (-3.0 + 4.0 * sin_sigma.powi(2))
                            * (-3.0 + 4.0 * cos_two_sigma_m.powi(2))));
        let updated = distance_km / (WGS84_B_KM * coefficient_a) + delta_sigma;
        if (updated - sigma).abs() <= 1e-13 {
            sigma = updated;
            converged = true;
            break;
        }
        sigma = updated;
    }
    if !converged {
        return Err(GeodesyError::DidNotConverge);
    }

    let (sin_sigma, cos_sigma) = sigma.sin_cos();
    let two_sigma_m = 2.0 * sigma_1 + sigma;
    let cos_two_sigma_m = two_sigma_m.cos();
    let numerator = sin_u_1 * cos_sigma + cos_u_1 * sin_sigma * alpha_1.cos();
    let denominator = (1.0 - WGS84_F)
        * (sin_alpha.powi(2) + (sin_u_1 * sin_sigma - cos_u_1 * cos_sigma * alpha_1.cos()).powi(2))
            .sqrt();
    let phi_2 = numerator.atan2(denominator);
    let lambda = (sin_sigma * alpha_1.sin())
        .atan2(cos_u_1 * cos_sigma - sin_u_1 * sin_sigma * alpha_1.cos());
    let correction_c = WGS84_F / 16.0 * cos_sq_alpha * (4.0 + WGS84_F * (4.0 - 3.0 * cos_sq_alpha));
    let longitude_delta = lambda
        - (1.0 - correction_c)
            * WGS84_F
            * sin_alpha
            * (sigma
                + correction_c
                    * sin_sigma
                    * (cos_two_sigma_m
                        + correction_c * cos_sigma * (-1.0 + 2.0 * cos_two_sigma_m.powi(2))));

    LatLon::new(
        phi_2.to_degrees(),
        start.longitude.0 + longitude_delta.to_degrees(),
    )
    .map_err(|_| GeodesyError::NonFinite)
}

pub fn great_circle_distance_nm(first: LatLon, second: LatLon) -> NauticalMiles {
    let latitude_1 = first.latitude.to_radians();
    let latitude_2 = second.latitude.to_radians();
    let delta_latitude = latitude_2 - latitude_1;
    let delta_longitude = (second.longitude.0 - first.longitude.0).to_radians();
    let haversine = (delta_latitude / 2.0).sin().powi(2)
        + latitude_1.cos() * latitude_2.cos() * (delta_longitude / 2.0).sin().powi(2);
    NauticalMiles(2.0 * LEGACY_SPHERE_RADIUS_NM * haversine.sqrt().asin())
}

#[cfg(test)]
mod tests {
    use approx::assert_abs_diff_eq;

    use super::*;

    #[test]
    fn wgs84_equatorial_degree_and_zero_distance() {
        let start = LatLon::new(0.0, 0.0).unwrap();
        let result = destination_wgs84(
            start,
            Degrees(90.0),
            NauticalMiles(111.319_490_793_273_57 / KM_PER_NM),
        )
        .unwrap();
        assert_abs_diff_eq!(result.latitude.0, 0.0, epsilon = 1e-10);
        assert_abs_diff_eq!(result.longitude.0, 1.0, epsilon = 1e-10);
        assert_eq!(
            destination_wgs84(
                LatLon::new(-32.5, 84.25).unwrap(),
                Degrees(11.0),
                NauticalMiles(0.0),
            )
            .unwrap(),
            LatLon::new(-32.5, 84.25).unwrap()
        );
    }

    #[test]
    fn ecef_equator_matches_wgs84_semi_major_axis() {
        let point = lla_to_ecef(LatLon::new(0.0, 0.0).unwrap(), Kilometers(0.0));
        assert_abs_diff_eq!(point.x, WGS84_A_KM, epsilon = 1e-12);
        assert_abs_diff_eq!(point.y, 0.0, epsilon = 1e-12);
        assert_abs_diff_eq!(point.z, 0.0, epsilon = 1e-12);
    }

    #[test]
    fn wgs84_does_not_silently_collapse_to_legacy_sphere() {
        let start = LatLon::new(-40.0, 105.0).unwrap();
        let wgs84 = destination_wgs84(start, Degrees(305.0), NauticalMiles(1_200.0)).unwrap();
        let sphere = destination_sphere(start, Degrees(305.0), NauticalMiles(1_200.0)).unwrap();
        assert!((wgs84.latitude.0 - sphere.latitude.0).abs() > 1e-3);
    }
}
