//! A gridded [`ProfileSource`]: GLORYS12V1 full-depth daily means of u, v, potential temperature and
//! practical salinity, with the model's own sea-floor depth (`deptho`, static dataset). Settling's
//! request (architecture 9 Oct, 04:15 rulings).
//!
//! Storage (`prepare/profile_to_grid.py`): one little-endian f32 file laid out (time, lat, lon,
//! variable, depth), so a column is 4 x nz contiguous values read with positioned reads; nothing is
//! held in memory beyond the axes and `deptho`. NaN marks land and levels below the model floor.
//!
//! Interpolation, declared:
//! - time: linear between the two bracketing daily means, each placed at its interval centre
//!   (label + 12 h, as for the surface series); outside the axis is [`FieldGap::OutsideTime`];
//! - horizontal: bilinear over the four surrounding columns with land renormalisation **per level**:
//!   at each level the weights of the corners that have a value there are renormalised. The profile
//!   stops at the first level where no corner has a value. No corner at the top level is
//!   [`FieldGap::Land`];
//! - `model_bottom_m` is the deepest `deptho` among the corners that contribute, so it is never
//!   shallower than the deepest level returned. Where the four columns have different floors the
//!   deeper levels come from the deeper columns only; this is the renormalisation, not a fill.
//! - vertical velocity is `Absent` (the multiyear daily dataset has no `wo`).

use crate::field::{bracket, Component, FieldGap, FieldMeta};
use crate::products::product;
use crate::profile::{Profile, ProfileSource, Salinity, Temperature, VerticalVelocity};
use crate::LonLat;
use serde::Deserialize;
use std::fs::File;
use std::os::unix::fs::FileExt;
use std::path::Path;

#[derive(Deserialize)]
struct Manifest {
    product: String,
    description: String,
    lon: Vec<f64>,
    lat: Vec<f64>,
    depth_m: Vec<f64>,
    /// Instants the daily means represent (interval centres), unix s.
    time_unix_s: Vec<f64>,
    /// Order of the variables within a column: must be uo, vo, thetao, so.
    variables: Vec<String>,
    data_file: String,
    /// Model sea-floor depth, f32 (lat, lon), NaN on land.
    deptho_file: String,
}

pub struct GridProfile {
    meta: FieldMeta,
    lon: Vec<f64>,
    lat: Vec<f64>,
    depth: Vec<f64>,
    time: Vec<f64>,
    deptho: Vec<f32>,
    file: File,
}

impl GridProfile {
    pub fn load(manifest: &Path) -> Result<Self, String> {
        let text = std::fs::read_to_string(manifest).map_err(|e| format!("{}: {e}", manifest.display()))?;
        let m: Manifest = serde_json::from_str(&text).map_err(|e| format!("{}: {e}", manifest.display()))?;
        if m.variables != ["uo", "vo", "thetao", "so"] {
            return Err(format!("{}: variables must be [uo, vo, thetao, so], got {:?}", manifest.display(), m.variables));
        }
        let pm = product(&m.product).ok_or_else(|| format!("product {} is not in the catalogue", m.product))?;
        let dir = manifest.parent().unwrap_or(Path::new("."));
        let (nx, ny, nz, nt) = (m.lon.len(), m.lat.len(), m.depth_m.len(), m.time_unix_s.len());
        let file = File::open(dir.join(&m.data_file)).map_err(|e| format!("{}: {e}", m.data_file))?;
        let want = (nt * ny * nx * 4 * nz * 4) as u64;
        let got = file.metadata().map_err(|e| e.to_string())?.len();
        if got != want {
            return Err(format!("{}: {got} bytes, axes imply {want}", m.data_file));
        }
        let d = std::fs::read(dir.join(&m.deptho_file)).map_err(|e| format!("{}: {e}", m.deptho_file))?;
        if d.len() != nx * ny * 4 {
            return Err(format!("{}: {} bytes, axes imply {}", m.deptho_file, d.len(), nx * ny * 4));
        }
        let deptho = d.chunks_exact(4).map(|b| f32::from_le_bytes([b[0], b[1], b[2], b[3]])).collect();
        let meta = FieldMeta { product: m.product, component: Component::Current, contents: pm.contents, time_axis: pm.time_axis, description: m.description };
        Ok(GridProfile { meta, lon: m.lon, lat: m.lat, depth: m.depth_m, time: m.time_unix_s, deptho, file })
    }

    /// (time, lon, lat, depth) axes.
    pub fn axes(&self) -> (&[f64], &[f64], &[f64], &[f64]) {
        (&self.time, &self.lon, &self.lat, &self.depth)
    }

    fn column(&self, it: usize, j: usize, i: usize) -> Result<Vec<f32>, FieldGap> {
        let nz = self.depth.len();
        let k = ((it * self.lat.len() + j) * self.lon.len() + i) * 4 * nz;
        let mut buf = vec![0u8; 4 * nz * 4];
        self.file.read_exact_at(&mut buf, (k * 4) as u64).map_err(|_| FieldGap::NonFinite)?;
        Ok(buf.chunks_exact(4).map(|b| f32::from_le_bytes([b[0], b[1], b[2], b[3]])).collect())
    }
}

impl ProfileSource for GridProfile {
    fn profile(&self, t: f64, p: LonLat) -> Result<Profile, FieldGap> {
        let (it, wt) = bracket(&self.time, t).ok_or(FieldGap::OutsideTime)?;
        let (j, wy) = bracket(&self.lat, p[1]).ok_or(FieldGap::OutsideDomain)?;
        let (i, wx) = bracket(&self.lon, p[0]).ok_or(FieldGap::OutsideDomain)?;
        let nz = self.depth.len();
        let (nx, ny, nt) = (self.lon.len(), self.lat.len(), self.time.len());
        // (weight, column at t0, column at t1, deptho) for each corner with positive weight.
        let mut corners = Vec::with_capacity(4);
        for (dy, fy) in [(0usize, 1.0 - wy), (1, wy)] {
            for (dx, fx) in [(0usize, 1.0 - wx), (1, wx)] {
                let w = fy * fx;
                let (jj, ii) = ((j + dy).min(ny - 1), (i + dx).min(nx - 1));
                if w <= 0.0 {
                    continue;
                }
                let c0 = self.column(it, jj, ii)?;
                let c1 = if wt > 0.0 { self.column((it + 1).min(nt - 1), jj, ii)? } else { c0.clone() };
                corners.push((w, c0, c1, self.deptho[jj * nx + ii]));
            }
        }
        let mut out: [Vec<f64>; 4] = Default::default();
        let mut bottom = f64::NEG_INFINITY;
        for z in 0..nz {
            let mut acc = [0.0f64; 4];
            let mut total = 0.0;
            let mut deepest = f64::NEG_INFINITY;
            for (w, c0, c1, dep) in &corners {
                let vals: Vec<f64> = (0..4).map(|v| (1.0 - wt) * c0[v * nz + z] as f64 + wt * c1[v * nz + z] as f64).collect();
                if vals.iter().all(|x| x.is_finite()) {
                    for v in 0..4 {
                        acc[v] += w * vals[v];
                    }
                    total += w;
                    deepest = deepest.max(*dep as f64);
                }
            }
            if total <= 0.0 {
                break;
            }
            bottom = bottom.max(deepest);
            for v in 0..4 {
                out[v].push(acc[v] / total);
            }
        }
        let n = out[0].len();
        if n == 0 {
            return Err(FieldGap::Land);
        }
        let depth_m = self.depth[..n].to_vec();
        let model_bottom_m = if bottom.is_finite() { bottom.max(depth_m[n - 1]) } else { depth_m[n - 1] };
        let [u, v, th, s] = out;
        Ok(Profile {
            pressure_dbar: depth_m.iter().map(|&z| crate::teos10::pressure_dbar(z, p[1])).collect(),
            depth_m,
            u_east: u,
            v_north: v,
            w_up: VerticalVelocity::Absent,
            temperature: Temperature::Potential(th),
            salinity: Salinity::Practical(s),
            model_bottom_m,
            time_axis: self.meta.time_axis.clone(),
        })
    }

    fn meta(&self) -> &FieldMeta {
        &self.meta
    }
}
