//! Gridded ERA5 wind/temperature and IGRF-14 magnetic declination.
//!
//! Binary layouts (little-endian, C order, longitude fastest):
//! - ERA5: `MHERA5V1`, u32 nt/na/ny/nx, i64 unix times, f32 pressure-altitude (ft),
//!   latitude and longitude axes, then f32 fields temperature (K), eastward and
//!   northward wind (m/s), each shaped [time, altitude, latitude, longitude].
//! - IGRF: `MHIGRFV1`, u32 na/ny/nx, i64 reference time, f64 decimal year,
//!   f32 altitude/latitude/longitude axes, then f32 east-positive declination (deg).
//! Interpolation is multilinear. Both grids are global; queries outside the time
//! or altitude axes are clamped to the nearest level (the model keeps 25-43 kft
//! within the 18:00-01:00 UTC window, so clamping does not occur in practice).

use serde::{Deserialize, Serialize};
use std::path::Path;

pub const MPS_PER_KNOT: f64 = 1852.0 / 3600.0;
const DRY_AIR_GAS_CONSTANT: f64 = 287.052_87;
const HEAT_CAPACITY_RATIO: f64 = 1.4;

#[derive(Debug, Clone, Copy, Serialize, Deserialize)]
pub struct Weather {
    pub temperature_k: f64,
    pub wind_east_kt: f64,
    pub wind_north_kt: f64,
}

impl Weather {
    pub fn speed_of_sound_kt(&self) -> f64 {
        (HEAT_CAPACITY_RATIO * DRY_AIR_GAS_CONSTANT * self.temperature_k).sqrt() / MPS_PER_KNOT
    }
}

/// Source of weather and declination for the dynamics model.
pub trait Environment: Sync {
    fn weather(&self, unix_s: f64, alt_ft: f64, lat: f64, lon: f64) -> Weather;
    fn declination_deg(&self, alt_ft: f64, lat: f64, lon: f64) -> f64;
}

/// Still air, ISA tropopause temperature, zero declination. Used by tests.
pub struct CalmAir;

impl Environment for CalmAir {
    fn weather(&self, _: f64, _: f64, _: f64, _: f64) -> Weather {
        Weather { temperature_k: 216.65, wind_east_kt: 0.0, wind_north_kt: 0.0 }
    }
    fn declination_deg(&self, _: f64, _: f64, _: f64) -> f64 {
        0.0
    }
}

pub struct Gridded {
    /// Multiplier on the nominal (gridded) wind. 1.0 for the estimate; other values are
    /// sensitivity runs. The OU wind-error process in the dynamics is unaffected.
    pub wind_scale: f64,
    /// Multiplier on magnetic declination. 1.0 for the estimate; -1.0 reverses the sign
    /// convention (a diagnostic of how magnetic modes depend on it).
    pub declination_scale: f64,
    era5_axes: [Vec<f64>; 4],
    temperature: Vec<f32>,
    wind_east: Vec<f32>,
    wind_north: Vec<f32>,
    igrf_axes: [Vec<f64>; 3],
    declination: Vec<f32>,
}

impl Gridded {
    pub fn load(era5: &Path, igrf: &Path) -> Result<Self, String> {
        let bytes = std::fs::read(era5).map_err(|e| format!("{}: {e}", era5.display()))?;
        let mut r = Reader { bytes: &bytes, at: 0 };
        r.magic(b"MHERA5V1")?;
        let n = [r.u32()?, r.u32()?, r.u32()?, r.u32()?];
        let times = (0..n[0]).map(|_| r.i64().map(|t| t as f64)).collect::<Result<Vec<_>, _>>()?;
        let era5_axes = [times, r.f32s(n[1])?, r.f32s(n[2])?, r.f32s(n[3])?];
        let count = n.iter().product();
        let temperature = r.raw_f32(count)?;
        let wind_east = r.raw_f32(count)?;
        let wind_north = r.raw_f32(count)?;
        r.end()?;

        let bytes = std::fs::read(igrf).map_err(|e| format!("{}: {e}", igrf.display()))?;
        let mut r = Reader { bytes: &bytes, at: 0 };
        r.magic(b"MHIGRFV1")?;
        let n = [r.u32()?, r.u32()?, r.u32()?];
        r.i64()?;
        r.skip(8)?;
        let igrf_axes = [r.f32s(n[0])?, r.f32s(n[1])?, r.f32s(n[2])?];
        let declination = r.raw_f32(n.iter().product())?;
        r.end()?;

        for axis in era5_axes.iter().chain(igrf_axes.iter()) {
            if axis.len() < 2 || axis.windows(2).any(|w| (w[1] - w[0]).signum() != (axis[1] - axis[0]).signum()) {
                return Err("environment axis is not strictly monotonic".into());
            }
        }
        Ok(Self { wind_scale: 1.0, declination_scale: 1.0, era5_axes, temperature, wind_east, wind_north, igrf_axes, declination })
    }

    /// The ERA5 grid's time span (Unix s) and pressure-altitude span (ft); `weather` clamps
    /// queries outside them.
    pub fn era5_span(&self) -> [(f64, f64); 2] {
        let span = |axis: &[f64]| (axis[0].min(axis[axis.len() - 1]), axis[0].max(axis[axis.len() - 1]));
        [span(&self.era5_axes[0]), span(&self.era5_axes[1])]
    }
}

impl Environment for Gridded {
    fn weather(&self, unix_s: f64, alt_ft: f64, lat: f64, lon: f64) -> Weather {
        let [t, a, y, x] = [
            locate(&self.era5_axes[0], unix_s),
            locate(&self.era5_axes[1], alt_ft),
            locate(&self.era5_axes[2], lat),
            locate(&self.era5_axes[3], lon),
        ];
        let dims = [self.era5_axes[1].len(), self.era5_axes[2].len(), self.era5_axes[3].len()];
        let mut out = [0.0; 3];
        for corner in 0..16 {
            let pick = |(i, f): (usize, f64), bit: usize| if corner >> bit & 1 == 1 { (i + 1, f) } else { (i, 1.0 - f) };
            let (it, wt) = pick(t, 3);
            let (ia, wa) = pick(a, 2);
            let (iy, wy) = pick(y, 1);
            let (ix, wx) = pick(x, 0);
            let w = wt * wa * wy * wx;
            if w == 0.0 {
                continue;
            }
            let k = ((it * dims[0] + ia) * dims[1] + iy) * dims[2] + ix;
            out[0] += w * f64::from(self.temperature[k]);
            out[1] += w * f64::from(self.wind_east[k]);
            out[2] += w * f64::from(self.wind_north[k]);
        }
        Weather {
            temperature_k: out[0],
            wind_east_kt: self.wind_scale * out[1] / MPS_PER_KNOT,
            wind_north_kt: self.wind_scale * out[2] / MPS_PER_KNOT,
        }
    }

    fn declination_deg(&self, alt_ft: f64, lat: f64, lon: f64) -> f64 {
        // Linear in degrees: declination is far from its +/-180 wrap over the Indian Ocean.
        let [a, y, x] = [locate(&self.igrf_axes[0], alt_ft), locate(&self.igrf_axes[1], lat), locate(&self.igrf_axes[2], lon)];
        let (ny, nx) = (self.igrf_axes[1].len(), self.igrf_axes[2].len());
        let mut out = 0.0;
        for corner in 0..8 {
            let pick = |(i, f): (usize, f64), bit: usize| if corner >> bit & 1 == 1 { (i + 1, f) } else { (i, 1.0 - f) };
            let (ia, wa) = pick(a, 2);
            let (iy, wy) = pick(y, 1);
            let (ix, wx) = pick(x, 0);
            let w = wa * wy * wx;
            if w != 0.0 {
                out += w * f64::from(self.declination[(ia * ny + iy) * nx + ix]);
            }
        }
        self.declination_scale * out
    }
}

/// Lower index and fractional position of `v` on a monotonic axis, clamped to its ends.
fn locate(axis: &[f64], v: f64) -> (usize, f64) {
    let n = axis.len();
    let (first, last) = (axis[0], axis[n - 1]);
    let s = ((v - first) / (last - first)).clamp(0.0, 1.0);
    // Regular axes: the arithmetic guess is exact; irregular axes are corrected by a short walk.
    let mut i = ((s * (n - 1) as f64) as usize).min(n - 2);
    let asc = last > first;
    let below = |x: f64, y: f64| if asc { x < y } else { x > y };
    while i > 0 && below(v, axis[i]) {
        i -= 1;
    }
    while i < n - 2 && !below(v, axis[i + 1]) {
        i += 1;
    }
    let f = ((v - axis[i]) / (axis[i + 1] - axis[i])).clamp(0.0, 1.0);
    (i, f)
}

struct Reader<'a> {
    bytes: &'a [u8],
    at: usize,
}

impl Reader<'_> {
    fn take(&mut self, n: usize) -> Result<&[u8], String> {
        let s = self.bytes.get(self.at..self.at + n).ok_or("environment grid is truncated")?;
        self.at += n;
        Ok(s)
    }
    fn skip(&mut self, n: usize) -> Result<(), String> {
        self.take(n).map(|_| ())
    }
    fn magic(&mut self, m: &[u8; 8]) -> Result<(), String> {
        if self.take(8)? == m { Ok(()) } else { Err(format!("expected {} grid", String::from_utf8_lossy(m))) }
    }
    fn u32(&mut self) -> Result<usize, String> {
        Ok(u32::from_le_bytes(self.take(4)?.try_into().unwrap()) as usize)
    }
    fn i64(&mut self) -> Result<i64, String> {
        Ok(i64::from_le_bytes(self.take(8)?.try_into().unwrap()))
    }
    fn raw_f32(&mut self, n: usize) -> Result<Vec<f32>, String> {
        Ok(self.take(4 * n)?.chunks_exact(4).map(|c| f32::from_le_bytes(c.try_into().unwrap())).collect())
    }
    fn f32s(&mut self, n: usize) -> Result<Vec<f64>, String> {
        Ok(self.raw_f32(n)?.into_iter().map(f64::from).collect())
    }
    fn end(&self) -> Result<(), String> {
        if self.at == self.bytes.len() { Ok(()) } else { Err("environment grid has trailing bytes".into()) }
    }
}

#[cfg(test)]
mod tests {
    use super::locate;

    #[test]
    fn locate_handles_ascending_descending_and_irregular_axes() {
        assert_eq!(locate(&[0.0, 1.0, 2.0], 1.5), (1, 0.5));
        assert_eq!(locate(&[90.0, 89.5, 89.0], 89.75), (0, 0.5));
        let (i, f) = locate(&[500.0, 5000.0, 10000.0, 25000.0, 28000.0], 26500.0);
        assert_eq!(i, 3);
        assert!((f - 0.5).abs() < 1e-12);
        assert_eq!(locate(&[0.0, 1.0], 5.0), (0, 1.0));
    }
}
