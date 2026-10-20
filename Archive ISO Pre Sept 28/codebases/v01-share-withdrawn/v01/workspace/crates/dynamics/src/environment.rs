use mh370_domain::{Degrees, Knots, LatLon};
use serde::{Deserialize, Serialize};
use thiserror::Error;

const ERA5_MAGIC: &[u8; 8] = b"MHERA5V1";
const IGRF_MAGIC: &[u8; 8] = b"MHIGRFV1";
const MPS_PER_KNOT: f64 = 0.514_444;
const DRY_AIR_GAS_CONSTANT_J_KG_K: f64 = 287.052_87;
const STANDARD_GRAVITY_M_S2: f64 = 9.806_65;
const ISA_SEA_LEVEL_PRESSURE_PA: f64 = 101_325.0;
const ISA_SEA_LEVEL_TEMPERATURE_K: f64 = 288.15;
const ISA_TROPOSPHERE_LAPSE_RATE_K_M: f64 = 0.0065;
const ISA_TROPOPAUSE_HEIGHT_M: f64 = 11_000.0;
const ISA_TROPOPAUSE_TEMPERATURE_K: f64 = 216.65;
const METRES_PER_FOOT: f64 = 0.3048;

#[derive(Debug, Error, Clone, PartialEq)]
pub enum EnvironmentError {
    #[error("environment grid has an invalid header or byte count")]
    InvalidFormat,
    #[error("environment grid contains invalid or unordered coordinates")]
    InvalidAxis,
    #[error("state lies outside the environmental grid")]
    OutsideDomain,
}

#[derive(Debug, Clone, Copy, PartialEq, Serialize, Deserialize)]
pub struct WeatherSample {
    pub temperature_k: f64,
    pub wind_east: Knots,
    pub wind_north: Knots,
}

impl WeatherSample {
    pub fn speed_of_sound_knots(self) -> f64 {
        // Dry-air approximation using the local ERA5 pressure-level temperature.
        (1.4 * DRY_AIR_GAS_CONSTANT_J_KG_K * self.temperature_k).sqrt() / MPS_PER_KNOT
    }

    /// Dry-air density using ERA5 temperature and the ISA pressure represented by the
    /// pressure-altitude coordinate of the runtime grid.
    pub fn dry_air_density_kg_m3(self, pressure_altitude_ft: f64) -> f64 {
        isa_pressure_pa(pressure_altitude_ft) / (DRY_AIR_GAS_CONSTANT_J_KG_K * self.temperature_k)
    }
}

/// ICAO/ISA pressure represented by a pressure-altitude coordinate.
pub fn isa_pressure_pa(pressure_altitude_ft: f64) -> f64 {
    let height_m = pressure_altitude_ft * METRES_PER_FOOT;
    let tropopause_pressure = ISA_SEA_LEVEL_PRESSURE_PA
        * (ISA_TROPOPAUSE_TEMPERATURE_K / ISA_SEA_LEVEL_TEMPERATURE_K).powf(
            STANDARD_GRAVITY_M_S2 / (DRY_AIR_GAS_CONSTANT_J_KG_K * ISA_TROPOSPHERE_LAPSE_RATE_K_M),
        );
    if height_m <= ISA_TROPOPAUSE_HEIGHT_M {
        let temperature = ISA_SEA_LEVEL_TEMPERATURE_K - ISA_TROPOSPHERE_LAPSE_RATE_K_M * height_m;
        ISA_SEA_LEVEL_PRESSURE_PA
            * (temperature / ISA_SEA_LEVEL_TEMPERATURE_K).powf(
                STANDARD_GRAVITY_M_S2
                    / (DRY_AIR_GAS_CONSTANT_J_KG_K * ISA_TROPOSPHERE_LAPSE_RATE_K_M),
            )
    } else {
        tropopause_pressure
            * (-STANDARD_GRAVITY_M_S2 * (height_m - ISA_TROPOPAUSE_HEIGHT_M)
                / (DRY_AIR_GAS_CONSTANT_J_KG_K * ISA_TROPOPAUSE_TEMPERATURE_K))
                .exp()
    }
}

#[derive(Debug, Clone)]
pub struct Era5Grid {
    times_unix_s: Vec<f64>,
    altitudes_ft: Vec<f64>,
    latitudes_deg: Vec<f64>,
    longitudes_deg: Vec<f64>,
    temperature_k: Vec<f32>,
    wind_east_m_s: Vec<f32>,
    wind_north_m_s: Vec<f32>,
}

#[derive(Debug, Clone)]
pub struct IgrfGrid {
    pub reference_time_unix_s: i64,
    pub decimal_year: f64,
    altitudes_ft: Vec<f64>,
    latitudes_deg: Vec<f64>,
    longitudes_deg: Vec<f64>,
    declination_east_deg: Vec<f32>,
}

fn read_exact<'a>(
    bytes: &'a [u8],
    cursor: &mut usize,
    count: usize,
) -> Result<&'a [u8], EnvironmentError> {
    let end = cursor
        .checked_add(count)
        .ok_or(EnvironmentError::InvalidFormat)?;
    let result = bytes
        .get(*cursor..end)
        .ok_or(EnvironmentError::InvalidFormat)?;
    *cursor = end;
    Ok(result)
}

fn read_u32(bytes: &[u8], cursor: &mut usize) -> Result<usize, EnvironmentError> {
    let raw: [u8; 4] = read_exact(bytes, cursor, 4)?.try_into().unwrap();
    Ok(u32::from_le_bytes(raw) as usize)
}

fn read_i64(bytes: &[u8], cursor: &mut usize) -> Result<i64, EnvironmentError> {
    let raw: [u8; 8] = read_exact(bytes, cursor, 8)?.try_into().unwrap();
    Ok(i64::from_le_bytes(raw))
}

fn read_f64(bytes: &[u8], cursor: &mut usize) -> Result<f64, EnvironmentError> {
    let raw: [u8; 8] = read_exact(bytes, cursor, 8)?.try_into().unwrap();
    Ok(f64::from_le_bytes(raw))
}

fn read_f32_vec(
    bytes: &[u8],
    cursor: &mut usize,
    count: usize,
) -> Result<Vec<f32>, EnvironmentError> {
    let byte_count = count
        .checked_mul(4)
        .ok_or(EnvironmentError::InvalidFormat)?;
    let raw = read_exact(bytes, cursor, byte_count)?;
    Ok(raw
        .chunks_exact(4)
        .map(|chunk| f32::from_le_bytes(chunk.try_into().unwrap()))
        .collect())
}

fn read_axis(bytes: &[u8], cursor: &mut usize, count: usize) -> Result<Vec<f64>, EnvironmentError> {
    let values = read_f32_vec(bytes, cursor, count)?
        .into_iter()
        .map(f64::from)
        .collect::<Vec<_>>();
    validate_axis(&values)?;
    Ok(values)
}

fn validate_axis(values: &[f64]) -> Result<(), EnvironmentError> {
    if values.is_empty() || values.iter().any(|value| !value.is_finite()) {
        return Err(EnvironmentError::InvalidAxis);
    }
    if values.len() == 1 {
        return Ok(());
    }
    let ascending = values[1] > values[0];
    if values.windows(2).any(|pair| {
        if ascending {
            pair[1] <= pair[0]
        } else {
            pair[1] >= pair[0]
        }
    }) {
        return Err(EnvironmentError::InvalidAxis);
    }
    Ok(())
}

fn validate_field(values: &[f32]) -> Result<(), EnvironmentError> {
    if values.iter().any(|value| !value.is_finite()) {
        Err(EnvironmentError::InvalidFormat)
    } else {
        Ok(())
    }
}

fn bracket(axis: &[f64], value: f64) -> Result<(usize, usize, f64), EnvironmentError> {
    if !value.is_finite() {
        return Err(EnvironmentError::OutsideDomain);
    }
    if axis.len() == 1 {
        return if (value - axis[0]).abs() <= f64::EPSILON {
            Ok((0, 0, 0.0))
        } else {
            Err(EnvironmentError::OutsideDomain)
        };
    }
    let ascending = axis[1] > axis[0];
    let low = axis[0].min(*axis.last().unwrap());
    let high = axis[0].max(*axis.last().unwrap());
    if value < low || value > high {
        return Err(EnvironmentError::OutsideDomain);
    }
    if value == *axis.last().unwrap() {
        let last = axis.len() - 1;
        return Ok((last - 1, last, 1.0));
    }
    let upper = axis.partition_point(|candidate| {
        if ascending {
            *candidate <= value
        } else {
            *candidate >= value
        }
    });
    let lower = upper.saturating_sub(1);
    if upper >= axis.len() {
        return Err(EnvironmentError::OutsideDomain);
    }
    let fraction = (value - axis[lower]) / (axis[upper] - axis[lower]);
    Ok((lower, upper, fraction))
}

fn checked_product(dimensions: &[usize]) -> Result<usize, EnvironmentError> {
    dimensions.iter().try_fold(1usize, |product, value| {
        product
            .checked_mul(*value)
            .ok_or(EnvironmentError::InvalidFormat)
    })
}

impl Era5Grid {
    pub fn parse(bytes: &[u8]) -> Result<Self, EnvironmentError> {
        let mut cursor = 0;
        if read_exact(bytes, &mut cursor, 8)? != ERA5_MAGIC {
            return Err(EnvironmentError::InvalidFormat);
        }
        let nt = read_u32(bytes, &mut cursor)?;
        let na = read_u32(bytes, &mut cursor)?;
        let ny = read_u32(bytes, &mut cursor)?;
        let nx = read_u32(bytes, &mut cursor)?;
        if [nt, na, ny, nx].contains(&0) {
            return Err(EnvironmentError::InvalidFormat);
        }
        let mut times_unix_s = Vec::with_capacity(nt);
        for _ in 0..nt {
            times_unix_s.push(read_i64(bytes, &mut cursor)? as f64);
        }
        validate_axis(&times_unix_s)?;
        let altitudes_ft = read_axis(bytes, &mut cursor, na)?;
        let latitudes_deg = read_axis(bytes, &mut cursor, ny)?;
        let longitudes_deg = read_axis(bytes, &mut cursor, nx)?;
        let count = checked_product(&[nt, na, ny, nx])?;
        let temperature_k = read_f32_vec(bytes, &mut cursor, count)?;
        let wind_east_m_s = read_f32_vec(bytes, &mut cursor, count)?;
        let wind_north_m_s = read_f32_vec(bytes, &mut cursor, count)?;
        if cursor != bytes.len() {
            return Err(EnvironmentError::InvalidFormat);
        }
        validate_field(&temperature_k)?;
        validate_field(&wind_east_m_s)?;
        validate_field(&wind_north_m_s)?;
        Ok(Self {
            times_unix_s,
            altitudes_ft,
            latitudes_deg,
            longitudes_deg,
            temperature_k,
            wind_east_m_s,
            wind_north_m_s,
        })
    }

    fn index(&self, time: usize, altitude: usize, latitude: usize, longitude: usize) -> usize {
        (((time * self.altitudes_ft.len() + altitude) * self.latitudes_deg.len() + latitude)
            * self.longitudes_deg.len())
            + longitude
    }

    fn interpolate(&self, field: &[f32], corners: [(usize, usize, f64); 4]) -> f64 {
        let [(t0, t1, ft), (a0, a1, fa), (y0, y1, fy), (x0, x1, fx)] = corners;
        let mut value = 0.0;
        for (t, wt) in [(t0, 1.0 - ft), (t1, ft)] {
            for (a, wa) in [(a0, 1.0 - fa), (a1, fa)] {
                for (y, wy) in [(y0, 1.0 - fy), (y1, fy)] {
                    for (x, wx) in [(x0, 1.0 - fx), (x1, fx)] {
                        value += f64::from(field[self.index(t, a, y, x)]) * wt * wa * wy * wx;
                    }
                }
            }
        }
        value
    }

    pub fn sample(
        &self,
        time_unix_s: f64,
        altitude_ft: f64,
        position: LatLon,
    ) -> Result<WeatherSample, EnvironmentError> {
        let corners = [
            bracket(&self.times_unix_s, time_unix_s)?,
            bracket(&self.altitudes_ft, altitude_ft)?,
            bracket(&self.latitudes_deg, position.latitude.0)?,
            bracket(&self.longitudes_deg, position.longitude.0)?,
        ];
        let sample = WeatherSample {
            temperature_k: self.interpolate(&self.temperature_k, corners),
            wind_east: Knots(self.interpolate(&self.wind_east_m_s, corners) / MPS_PER_KNOT),
            wind_north: Knots(self.interpolate(&self.wind_north_m_s, corners) / MPS_PER_KNOT),
        };
        if sample.temperature_k <= 0.0 {
            return Err(EnvironmentError::InvalidFormat);
        }
        Ok(sample)
    }

    pub fn pressure_altitude_bounds_ft(&self) -> (f64, f64) {
        let first = self.altitudes_ft[0];
        let last = *self.altitudes_ft.last().expect("validated non-empty axis");
        (first.min(last), first.max(last))
    }
}

impl IgrfGrid {
    pub fn parse(bytes: &[u8]) -> Result<Self, EnvironmentError> {
        let mut cursor = 0;
        if read_exact(bytes, &mut cursor, 8)? != IGRF_MAGIC {
            return Err(EnvironmentError::InvalidFormat);
        }
        let na = read_u32(bytes, &mut cursor)?;
        let ny = read_u32(bytes, &mut cursor)?;
        let nx = read_u32(bytes, &mut cursor)?;
        if [na, ny, nx].contains(&0) {
            return Err(EnvironmentError::InvalidFormat);
        }
        let reference_time_unix_s = read_i64(bytes, &mut cursor)?;
        let decimal_year = read_f64(bytes, &mut cursor)?;
        if !decimal_year.is_finite() {
            return Err(EnvironmentError::InvalidFormat);
        }
        let altitudes_ft = read_axis(bytes, &mut cursor, na)?;
        let latitudes_deg = read_axis(bytes, &mut cursor, ny)?;
        let longitudes_deg = read_axis(bytes, &mut cursor, nx)?;
        let count = checked_product(&[na, ny, nx])?;
        let declination_east_deg = read_f32_vec(bytes, &mut cursor, count)?;
        if cursor != bytes.len() {
            return Err(EnvironmentError::InvalidFormat);
        }
        validate_field(&declination_east_deg)?;
        Ok(Self {
            reference_time_unix_s,
            decimal_year,
            altitudes_ft,
            latitudes_deg,
            longitudes_deg,
            declination_east_deg,
        })
    }

    fn index(&self, altitude: usize, latitude: usize, longitude: usize) -> usize {
        (altitude * self.latitudes_deg.len() + latitude) * self.longitudes_deg.len() + longitude
    }

    pub fn declination(
        &self,
        altitude_ft: f64,
        position: LatLon,
    ) -> Result<Degrees, EnvironmentError> {
        let (a0, a1, fa) = bracket(&self.altitudes_ft, altitude_ft)?;
        let (y0, y1, fy) = bracket(&self.latitudes_deg, position.latitude.0)?;
        let (x0, x1, fx) = bracket(&self.longitudes_deg, position.longitude.0)?;
        let mut value = 0.0;
        for (a, wa) in [(a0, 1.0 - fa), (a1, fa)] {
            for (y, wy) in [(y0, 1.0 - fy), (y1, fy)] {
                for (x, wx) in [(x0, 1.0 - fx), (x1, fx)] {
                    value +=
                        f64::from(self.declination_east_deg[self.index(a, y, x)]) * wa * wy * wx;
                }
            }
        }
        Ok(Degrees(value))
    }

    pub fn altitude_bounds_ft(&self) -> (f64, f64) {
        let first = self.altitudes_ft[0];
        let last = *self.altitudes_ft.last().expect("validated non-empty axis");
        (first.min(last), first.max(last))
    }
}

#[cfg(test)]
mod tests {
    use approx::assert_abs_diff_eq;

    use super::*;

    fn push_u32(bytes: &mut Vec<u8>, value: u32) {
        bytes.extend(value.to_le_bytes());
    }

    fn push_f32s(bytes: &mut Vec<u8>, values: &[f32]) {
        for value in values {
            bytes.extend(value.to_le_bytes());
        }
    }

    #[test]
    fn era5_interpolates_all_four_axes_and_converts_wind_units() {
        let mut bytes = ERA5_MAGIC.to_vec();
        for count in [2, 2, 2, 2] {
            push_u32(&mut bytes, count);
        }
        for time in [1_000_i64, 2_000] {
            bytes.extend(time.to_le_bytes());
        }
        push_f32s(&mut bytes, &[10_000.0, 20_000.0]);
        push_f32s(&mut bytes, &[2.0, 0.0]);
        push_f32s(&mut bytes, &[100.0, 102.0]);
        let field = (0..16).map(|value| value as f32).collect::<Vec<_>>();
        push_f32s(
            &mut bytes,
            &field.iter().map(|value| 240.0 + value).collect::<Vec<_>>(),
        );
        push_f32s(&mut bytes, &field);
        push_f32s(
            &mut bytes,
            &field.iter().map(|value| 2.0 * value).collect::<Vec<_>>(),
        );
        let grid = Era5Grid::parse(&bytes).unwrap();
        let sample = grid
            .sample(1_500.0, 15_000.0, LatLon::new(1.0, 101.0).unwrap())
            .unwrap();
        assert_abs_diff_eq!(sample.temperature_k, 247.5, epsilon = 1e-12);
        assert_abs_diff_eq!(sample.wind_east.0, 7.5 / MPS_PER_KNOT, epsilon = 1e-12);
        assert_abs_diff_eq!(sample.wind_north.0, 15.0 / MPS_PER_KNOT, epsilon = 1e-12);
    }

    #[test]
    fn igrf_interpolates_east_positive_declination() {
        let mut bytes = IGRF_MAGIC.to_vec();
        for count in [2, 2, 2] {
            push_u32(&mut bytes, count);
        }
        bytes.extend(1_394_157_600_i64.to_le_bytes());
        bytes.extend(2014.18_f64.to_le_bytes());
        push_f32s(&mut bytes, &[10_000.0, 20_000.0]);
        push_f32s(&mut bytes, &[2.0, 0.0]);
        push_f32s(&mut bytes, &[100.0, 102.0]);
        push_f32s(&mut bytes, &[0.0, 2.0, 4.0, 6.0, 8.0, 10.0, 12.0, 14.0]);
        let grid = IgrfGrid::parse(&bytes).unwrap();
        let value = grid
            .declination(15_000.0, LatLon::new(1.0, 101.0).unwrap())
            .unwrap();
        assert_abs_diff_eq!(value.0, 7.0, epsilon = 1e-12);
    }

    #[test]
    fn parser_rejects_short_or_nonmonotonic_data() {
        assert!(matches!(
            Era5Grid::parse(b"short"),
            Err(EnvironmentError::InvalidFormat)
        ));
        assert_eq!(
            validate_axis(&[1.0, 3.0, 2.0]),
            Err(EnvironmentError::InvalidAxis)
        );
    }

    #[test]
    fn era5_temperature_and_pressure_altitude_reproduce_manifest_density_contract() {
        let sample = WeatherSample {
            temperature_k: 263.832_275_390_625,
            wind_east: Knots(0.0),
            wind_north: Knots(0.0),
        };
        assert_abs_diff_eq!(
            isa_pressure_pa(20_000.0),
            46_563.239_236_280_82,
            epsilon = 1.0e-8
        );
        assert_abs_diff_eq!(
            sample.dry_air_density_kg_m3(20_000.0),
            0.614_827_619_251_579_1,
            epsilon = 1.0e-12
        );
    }
}
