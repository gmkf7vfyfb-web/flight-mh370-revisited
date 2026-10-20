//! Sound-speed profiles with the product's own spread, for hydroacoustics (interface request of
//! 9 October). Product: World Ocean Atlas 2023, 1 degree, objectively analysed means (`t_an`, `s_an`)
//! and standard deviations (`t_sd`, `s_sd`). Monthly fields above 1,500 m and seasonal fields below,
//! as WOA itself distributes them. One decade per epoch: 1995-2004 (`95A4`) for the 2001 and 2003
//! Blackman events, 2005-2014 (`A5B4`) for March 2014, 2015-2022 (`B5C2`) for later events.
//!
//! The TEOS-10 conversion (in-situ t and SP to SA, CT; then c) is done once, in preparation
//! (`prepare/woa23_to_soundspeed.py`, official `gsw`), on the WOA grid. The spread is
//! `c_sd = sqrt((dc/dt * t_sd)^2 + (dc/dSP * s_sd)^2)`, linearised, **treating temperature and
//! salinity deviations as independent**. Warm and salty anomalies both raise c, so positively
//! correlated T-S deviations would make the true spread larger; this is declared, not hidden.
//!
//! Horizontal interpolation is bilinear on the 1-degree grid with renormalisation over the corners
//! that have data at that level (the land rule). A level with no data at any corner is NaN, never
//! filled. Pressure is TEOS-10 `p_from_z` at the query latitude.

use crate::teos10::pressure_dbar;
use crate::LonLat;
use serde::{Deserialize, Serialize};
use std::path::Path;

#[derive(Deserialize)]
struct Manifest {
    product: String,
    decade: String,
    month: u32,
    lon0: f64,
    lat0: f64,
    step_deg: f64,
    nlon: usize,
    nlat: usize,
    depth_m: Vec<f64>,
    c_mean_file: String,
    c_sd_file: String,
    sa_file: String,
    ct_file: String,
}

#[derive(Clone, Debug, Serialize)]
pub struct SoundSpeedProfile {
    pub product: String,
    pub decade: String,
    pub month: u32,
    pub point: LonLat,
    pub depth_m: Vec<f64>,
    pub pressure_dbar: Vec<f64>,
    pub c_mean_m_s: Vec<f64>,
    pub c_sd_m_s: Vec<f64>,
    pub absolute_salinity_g_kg: Vec<f64>,
    pub conservative_temperature_c: Vec<f64>,
}

/// One decade-month of the climatology, loaded from its prepared grids `[lat][lon][level]`.
pub struct SoundSpeedClimatology {
    m: Manifest,
    c_mean: Vec<f32>,
    c_sd: Vec<f32>,
    sa: Vec<f32>,
    ct: Vec<f32>,
}

fn read_f32(path: &Path) -> Result<Vec<f32>, String> {
    let b = std::fs::read(path).map_err(|e| format!("{}: {e}", path.display()))?;
    Ok(b.chunks_exact(4).map(|c| f32::from_le_bytes([c[0], c[1], c[2], c[3]])).collect())
}

/// WOA23 decade and month for a unix time (UTC).
pub fn woa23_period(unix_s: f64) -> (&'static str, u32) {
    let days = (unix_s / 86_400.0).floor() as i64;
    // civil-from-days (Howard Hinnant's algorithm)
    let z = days + 719_468;
    let era = z.div_euclid(146_097);
    let doe = z - era * 146_097;
    let yoe = (doe - doe / 1460 + doe / 36_524 - doe / 146_096) / 365;
    let doy = doe - (365 * yoe + yoe / 4 - yoe / 100);
    let mp = (5 * doy + 2) / 153;
    let month = if mp < 10 { mp + 3 } else { mp - 9 } as u32;
    let year = yoe + era * 400 + if month <= 2 { 1 } else { 0 };
    let decade = if year < 2005 { "95A4" } else if year < 2015 { "A5B4" } else { "B5C2" };
    (decade, month)
}

impl SoundSpeedClimatology {
    pub fn load(manifest: &Path) -> Result<Self, String> {
        let text = std::fs::read_to_string(manifest).map_err(|e| format!("{}: {e}", manifest.display()))?;
        let m: Manifest = serde_json::from_str(&text).map_err(|e| format!("{}: {e}", manifest.display()))?;
        let dir = manifest.parent().unwrap_or(Path::new("."));
        let n = m.nlat * m.nlon * m.depth_m.len();
        let c_mean = read_f32(&dir.join(&m.c_mean_file))?;
        let c_sd = read_f32(&dir.join(&m.c_sd_file))?;
        let sa = read_f32(&dir.join(&m.sa_file))?;
        let ct = read_f32(&dir.join(&m.ct_file))?;
        if [c_mean.len(), c_sd.len(), sa.len(), ct.len()].iter().any(|&l| l != n) {
            return Err(format!("{}: grid sizes do not match the manifest", manifest.display()));
        }
        Ok(SoundSpeedClimatology { m, c_mean, c_sd, sa, ct })
    }

    pub fn period(&self) -> (&str, u32) {
        (&self.m.decade, self.m.month)
    }

    /// Profile at `p`, or `None` outside the stored grid.
    pub fn profile(&self, p: LonLat) -> Option<SoundSpeedProfile> {
        let m = &self.m;
        let x = (p[0] - m.lon0) / m.step_deg;
        let y = (p[1] - m.lat0) / m.step_deg;
        if x < 0.0 || y < 0.0 || x > (m.nlon - 1) as f64 || y > (m.nlat - 1) as f64 {
            return None;
        }
        let (i, j) = ((x.floor() as usize).min(m.nlon - 2), (y.floor() as usize).min(m.nlat - 2));
        let (fx, fy) = (x - i as f64, y - j as f64);
        let nz = m.depth_m.len();
        let corners = [(i, j, (1.0 - fx) * (1.0 - fy)), (i + 1, j, fx * (1.0 - fy)), (i, j + 1, (1.0 - fx) * fy), (i + 1, j + 1, fx * fy)];
        let interp = |v: &[f32], k: usize| {
            let (mut acc, mut w) = (0.0, 0.0);
            for &(ci, cj, cw) in &corners {
                let val = v[(cj * m.nlon + ci) * nz + k] as f64;
                if cw > 0.0 && val.is_finite() {
                    acc += cw * val;
                    w += cw;
                }
            }
            if w > 0.0 { acc / w } else { f64::NAN }
        };
        let col = |v: &[f32]| (0..nz).map(|k| interp(v, k)).collect::<Vec<f64>>();
        Some(SoundSpeedProfile {
            product: m.product.clone(),
            decade: m.decade.clone(),
            month: m.month,
            point: p,
            depth_m: m.depth_m.clone(),
            pressure_dbar: m.depth_m.iter().map(|&z| pressure_dbar(z, p[1])).collect(),
            c_mean_m_s: col(&self.c_mean),
            c_sd_m_s: col(&self.c_sd),
            absolute_salinity_g_kg: col(&self.sa),
            conservative_temperature_c: col(&self.ct),
        })
    }
}
