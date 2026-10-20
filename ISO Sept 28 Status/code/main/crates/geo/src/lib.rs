//! Shared WGS-84 geometry and unit conversions.
//!
//! Conventions used throughout the workspace: latitude/longitude in degrees
//! (longitude east-positive), altitude in feet, horizontal speed in knots,
//! Earth-centred Earth-fixed (ECEF) positions in kilometres.

use std::ops::{Add, Mul, Sub};

pub const WGS84_A_KM: f64 = 6_378.137;
pub const WGS84_F: f64 = 1.0 / 298.257_223_563;
pub const WGS84_E2: f64 = WGS84_F * (2.0 - WGS84_F);

pub const KM_PER_FT: f64 = 0.000_304_8;
pub const KM_PER_NM: f64 = 1.852;
pub const M_PER_KT_S: f64 = 1852.0 / 3600.0;
pub const KM_S_PER_KT: f64 = KM_PER_NM / 3600.0;

#[derive(Debug, Clone, Copy, Default, PartialEq)]
pub struct Vec3 {
    pub x: f64,
    pub y: f64,
    pub z: f64,
}

impl Vec3 {
    pub const fn new(x: f64, y: f64, z: f64) -> Self {
        Self { x, y, z }
    }
    pub fn dot(self, other: Self) -> f64 {
        self.x * other.x + self.y * other.y + self.z * other.z
    }
    pub fn norm(self) -> f64 {
        self.dot(self).sqrt()
    }
    pub fn unit(self) -> Self {
        self * (1.0 / self.norm())
    }
}

impl Add for Vec3 {
    type Output = Self;
    fn add(self, o: Self) -> Self {
        Self::new(self.x + o.x, self.y + o.y, self.z + o.z)
    }
}

impl Sub for Vec3 {
    type Output = Self;
    fn sub(self, o: Self) -> Self {
        Self::new(self.x - o.x, self.y - o.y, self.z - o.z)
    }
}

impl Mul<f64> for Vec3 {
    type Output = Self;
    fn mul(self, s: f64) -> Self {
        Self::new(self.x * s, self.y * s, self.z * s)
    }
}

/// Geodetic latitude/longitude (degrees) and height above the ellipsoid (km) to ECEF (km).
pub fn lla_to_ecef(lat_deg: f64, lon_deg: f64, height_km: f64) -> Vec3 {
    let (sin_lat, cos_lat) = lat_deg.to_radians().sin_cos();
    let (sin_lon, cos_lon) = lon_deg.to_radians().sin_cos();
    let n = WGS84_A_KM / (1.0 - WGS84_E2 * sin_lat * sin_lat).sqrt();
    Vec3::new(
        (n + height_km) * cos_lat * cos_lon,
        (n + height_km) * cos_lat * sin_lon,
        (n * (1.0 - WGS84_E2) + height_km) * sin_lat,
    )
}

/// Local north, east and up unit vectors in ECEF.
pub fn local_basis(lat_deg: f64, lon_deg: f64) -> (Vec3, Vec3, Vec3) {
    let (sin_lat, cos_lat) = lat_deg.to_radians().sin_cos();
    let (sin_lon, cos_lon) = lon_deg.to_radians().sin_cos();
    (
        Vec3::new(-sin_lat * cos_lon, -sin_lat * sin_lon, cos_lat),
        Vec3::new(-sin_lon, cos_lon, 0.0),
        Vec3::new(cos_lat * cos_lon, cos_lat * sin_lon, sin_lat),
    )
}

/// Meridional and prime-vertical radii of curvature (km).
pub fn radii_of_curvature_km(lat_deg: f64) -> (f64, f64) {
    let s = lat_deg.to_radians().sin();
    let w2 = 1.0 - WGS84_E2 * s * s;
    let n = WGS84_A_KM / w2.sqrt();
    (WGS84_A_KM * (1.0 - WGS84_E2) / (w2 * w2.sqrt()), n)
}

/// Advance a position by a north/east velocity (knots) for `dt_s` seconds at altitude `alt_ft`.
pub fn advance(lat_deg: f64, lon_deg: f64, alt_ft: f64, v_north_kt: f64, v_east_kt: f64, dt_s: f64) -> (f64, f64) {
    let (m, n) = radii_of_curvature_km(lat_deg);
    let h = alt_ft * KM_PER_FT;
    let north_km = v_north_kt * KM_S_PER_KT * dt_s;
    let east_km = v_east_kt * KM_S_PER_KT * dt_s;
    let lat = lat_deg + (north_km / (m + h)).to_degrees();
    let lon = lon_deg + (east_km / ((n + h) * lat_deg.to_radians().cos())).to_degrees();
    (lat, wrap_longitude(lon))
}

pub fn wrap_longitude(lon_deg: f64) -> f64 {
    (lon_deg + 180.0).rem_euclid(360.0) - 180.0
}

/// Pressure (Pa) of the ICAO standard atmosphere at a pressure altitude (ft): the definition
/// of pressure altitude, which is the altitude everywhere in this workspace. Troposphere to
/// 11 km, then the isothermal layer (valid to 20 km, 65,617 ft).
pub fn isa_pressure_pa(pressure_altitude_ft: f64) -> f64 {
    let h = pressure_altitude_ft * KM_PER_FT * 1000.0;
    if h <= 11_000.0 {
        101_325.0 * (1.0 - 2.255_77e-5 * h).powf(5.255_88)
    } else {
        22_632.06 * (-1.576_883e-4 * (h - 11_000.0)).exp()
    }
}

/// Wrap an angle in radians to (-pi, pi].
pub fn wrap_pi(a: f64) -> f64 {
    let w = (a + std::f64::consts::PI).rem_euclid(std::f64::consts::TAU) - std::f64::consts::PI;
    if w == -std::f64::consts::PI { std::f64::consts::PI } else { w }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn ecef_matches_independent_fixture() {
        // Independent Python forward-model fixture (Davey-parameter reconstruction).
        let p = lla_to_ecef(-25.0, 95.0, 35_000.0 * KM_PER_FT);
        assert!((p.x - -504.952_710_787_359_76).abs() < 1e-9);
        assert!((p.y - 5_771.635_894_720_64).abs() < 1e-9);
        assert!((p.z - -2_683.582_954_574_037).abs() < 1e-9);
    }

    #[test]
    fn isa_pressure_matches_the_icao_table() {
        // ICAO standard atmosphere table: sea level, FL350 (238.42 hPa), FL500 (115.97 hPa).
        for (ft, hpa) in [(0.0, 1013.25), (35_000.0, 238.42), (50_000.0, 115.97)] {
            assert!((isa_pressure_pa(ft) / 100.0 - hpa).abs() < 0.05, "{ft} ft: {}", isa_pressure_pa(ft) / 100.0);
        }
    }

    #[test]
    fn advance_moves_one_nautical_mile_per_arcminute_near_equator() {
        // 60 kt north for one hour is ~60 NM, i.e. ~1 degree of latitude.
        let (lat, lon) = advance(0.0, 90.0, 0.0, 60.0, 0.0, 3600.0);
        assert!((lat - 1.0).abs() < 0.01, "{lat}");
        assert_eq!(lon, 90.0);
    }
}
