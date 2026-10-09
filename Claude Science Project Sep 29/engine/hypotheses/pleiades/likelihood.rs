//! Deliverable 3: the Pléiades position likelihood with an ANALYTIC, NORMALISED spread.
//!
//!   ln L(s | H) = ln SUM_c w_c * p(y_c | s) * A_scene          (pleiades-origin = H)
//!   ln L(s | not-H) = 0                                         (the background, by construction)
//!
//! so that the composer's mixture over the prior pi on H reproduces the brief's
//! ln[(1 - pi) + pi SUM_c w_c p(y_c|s)/q_c] with q_c = 1/A_scene (A_scene = 500 km2: GA Record
//! 2017/13, "each scene is approximately 25 km x 20 km"). There is no identity likelihood: nothing
//! here depends on shape, size or rating except through the declared cluster weights w_c.
//!
//! p(y | s) = SUM_k pi_k SUM_j omega_j N2(y; X_k(s, t_y), v_j(dt) I)
//!   X_k     deterministic track from s under windage node k (release-grid table from
//!           `export.rs`, through mh370-ocean), bilinearly interpolated in the release position;
//!   pi_k    uniform windage prior over 0..5 % (the export grid);
//!   omega_j log-uniform K prior 30-1000 m2/s, Gauss-Legendre nodes in ln K (ONE K for every target:
//!           K is an eta component of the run, shared, per the ocean-transport ruling);
//!   v_j     2 K_j dt + 2 sigma_e^2 T_e [dt - T_e(1 - exp(-dt/T_e))] + sd_target^2, per component.
//!
//! Each term is a normalised density, the weights sum to one, and there is no random number
//! anywhere, so p integrates to one over the plane and the column is seed-free (tests below).
//! K is one eta draw shared by every target. Each term of SUM_c involves ONE target only (under the
//! brief's form exactly one cluster is 9M-MRO's), so marginalising K inside each term is exact. A
//! joint multi-object likelihood (brief section 13, deferred) would have to move K outside.

use std::path::Path;

pub const A_SCENE_KM2: f64 = 500.0;
const KM_PER_DEG: f64 = 6371.0088 * std::f64::consts::PI / 180.0;

#[derive(Clone, Debug)]
pub struct Table {
    pub lon0: f64,
    pub lat0: f64,
    pub step: f64,
    pub nlon: usize,
    pub nlat: usize,
    pub nw: usize,
    pub out_unix_s: Vec<f64>,
    #[allow(dead_code)]
    pub release_unix_s: f64,
    pub ocean_model: String,
    /// [lat][lon][windage][out_time][lon, lat]
    pub data: Vec<f32>,
}

#[derive(serde::Deserialize)]
struct TableMeta {
    lon0: f64,
    lat0: f64,
    step_deg: f64,
    nlon: usize,
    nlat: usize,
    windage_n: usize,
    out_unix_s: Vec<f64>,
    release_unix_s: f64,
    ocean_model: String,
    data_file: String,
    non_afloat_snapshots: usize,
}

impl Table {
    pub fn load(meta_toml: &Path) -> Result<Self, String> {
        let text = std::fs::read_to_string(meta_toml).map_err(|e| format!("{}: {e}", meta_toml.display()))?;
        let m: TableMeta = toml::from_str(&text).map_err(|e| format!("{}: {e}", meta_toml.display()))?;
        let bin = meta_toml.with_file_name(&m.data_file);
        let bytes = std::fs::read(&bin).map_err(|e| format!("{}: {e}", bin.display()))?;
        let n = m.nlat * m.nlon * m.windage_n * m.out_unix_s.len() * 2;
        if bytes.len() != 4 * n {
            return Err(format!("{}: {} bytes, expected {}", bin.display(), bytes.len(), 4 * n));
        }
        let data = bytes.chunks_exact(4).map(|b| f32::from_le_bytes([b[0], b[1], b[2], b[3]])).collect();
        let _ = m.non_afloat_snapshots;
        Ok(Table {
            lon0: m.lon0, lat0: m.lat0, step: m.step_deg, nlon: m.nlon, nlat: m.nlat, nw: m.windage_n,
            out_unix_s: m.out_unix_s, release_unix_s: m.release_unix_s, ocean_model: m.ocean_model, data,
        })
    }

    fn at(&self, j: usize, i: usize, k: usize, t: usize) -> [f64; 2] {
        let nt = self.out_unix_s.len();
        let o = (((j * self.nlon + i) * self.nw + k) * nt + t) * 2;
        [self.data[o] as f64, self.data[o + 1] as f64]
    }

    /// Bilinear interpolation of the deterministic endpoint in the release position. None outside
    /// the table or where a corner did not stay afloat (NaN), i.e. "not computed".
    pub fn endpoint(&self, lon: f64, lat: f64, k: usize, t: usize) -> Option<[f64; 2]> {
        let x = (lon - self.lon0) / self.step;
        let y = (lat - self.lat0) / self.step;
        if !(x >= 0.0 && y >= 0.0) {
            return None;
        }
        let (i, j) = (x.floor() as usize, y.floor() as usize);
        if i + 1 >= self.nlon || j + 1 >= self.nlat {
            return None;
        }
        let (fx, fy) = (x - i as f64, y - j as f64);
        let mut out = [0.0; 2];
        for (dj, wy) in [(0, 1.0 - fy), (1, fy)] {
            for (di, wx) in [(0, 1.0 - fx), (1, fx)] {
                let p = self.at(j + dj, i + di, k, t);
                if !(p[0].is_finite() && p[1].is_finite()) {
                    return None;
                }
                out[0] += wx * wy * p[0];
                out[1] += wx * wy * p[1];
            }
        }
        Some(out)
    }

    pub fn time_index(&self, t: f64) -> Option<usize> {
        self.out_unix_s.iter().position(|&x| (x - t).abs() < 1.0)
    }
}

#[derive(Clone, Debug)]
#[allow(dead_code)]
pub struct Target {
    pub scene: String,
    pub lon: f64,
    pub lat: f64,
    pub w_equal: f64,
    pub w_count: f64,
    pub time_index: usize,
    pub dt_ref_unix_s: f64,
}

#[derive(Clone, Debug)]
pub struct Spread {
    pub sigma_e_ms: f64,
    pub t_e_s: f64,
    pub sd_target_km: f64,
    pub k_nodes: Vec<(f64, f64)>,
}

impl Spread {
    pub fn new(sigma_e_ms: f64, t_e_s: f64, sd_target_km: f64, k_min: f64, k_max: f64, n: usize) -> Self {
        Spread { sigma_e_ms, t_e_s, sd_target_km, k_nodes: log_uniform_nodes(k_min, k_max, n) }
    }

    /// Per-component variance, km^2, for node (K, .) over dt seconds.
    pub fn var_km2(&self, k_m2_s: f64, dt: f64) -> f64 {
        let ou = if self.sigma_e_ms > 0.0 {
            2.0 * self.sigma_e_ms.powi(2) * self.t_e_s * (dt - self.t_e_s * (1.0 - (-dt / self.t_e_s).exp()))
        } else {
            0.0
        };
        (2.0 * k_m2_s * dt + ou) / 1e6 + self.sd_target_km.powi(2)
    }
}

/// Gauss-Legendre nodes in ln K on [ln k_min, ln k_max] with weights summing to one.
pub fn log_uniform_nodes(k_min: f64, k_max: f64, n: usize) -> Vec<(f64, f64)> {
    if k_min == k_max || n == 1 {
        return vec![(k_min.max(k_max), 1.0)];
    }
    let (x, w) = gauss_legendre(n);
    let (a, b) = (k_min.ln(), k_max.ln());
    let s: f64 = w.iter().sum();
    x.iter().zip(&w).map(|(xi, wi)| ((0.5 * (b - a) * xi + 0.5 * (b + a)).exp(), wi / s)).collect()
}

fn gauss_legendre(n: usize) -> (Vec<f64>, Vec<f64>) {
    let mut x = vec![0.0; n];
    let mut w = vec![0.0; n];
    for i in 0..n {
        let mut z = (std::f64::consts::PI * (i as f64 + 0.75) / (n as f64 + 0.5)).cos();
        for _ in 0..100 {
            let (mut p1, mut p2) = (1.0, 0.0);
            for j in 0..n {
                let p3 = p2;
                p2 = p1;
                p1 = ((2 * j + 1) as f64 * z * p2 - j as f64 * p3) / (j + 1) as f64;
            }
            let pp = n as f64 * (z * p1 - p2) / (z * z - 1.0);
            let dz = p1 / pp;
            z -= dz;
            if dz.abs() < 1e-15 {
                let wi = 2.0 / ((1.0 - z * z) * pp * pp);
                x[i] = z;
                w[i] = wi;
                break;
            }
        }
    }
    (x, w)
}

/// East/north offset in km of `y` from `x` (both [lon, lat]), local tangent plane.
pub fn offset_km(x: [f64; 2], y: [f64; 2]) -> [f64; 2] {
    let c = (0.5 * (x[1] + y[1])).to_radians().cos();
    [(y[0] - x[0]) * c * KM_PER_DEG, (y[1] - x[1]) * KM_PER_DEG]
}

/// p(y | track endpoints, spread), per km^2: mixture over windage nodes (uniform) and K nodes.
/// `endpoints[k]` is the deterministic position under windage node k; None marks a node not computed.
pub fn density(endpoints: &[Option<[f64; 2]>], y: [f64; 2], dt: f64, spread: &Spread) -> Option<f64> {
    let nk = endpoints.len() as f64;
    let mut p = 0.0;
    for e in endpoints {
        let x = (*e)?;
        let d = offset_km(x, y);
        let r2 = d[0] * d[0] + d[1] * d[1];
        for (k, w) in &spread.k_nodes {
            let v = spread.var_km2(*k, dt);
            p += w / nk * (-r2 / (2.0 * v)).exp() / (2.0 * std::f64::consts::PI * v);
        }
    }
    Some(p)
}

pub struct PositionLikelihood {
    pub table: Table,
    pub spread: Spread,
    /// Targets per object-rating option, in option order.
    pub arms: Vec<Vec<Target>>,
}

impl PositionLikelihood {
    /// ln SUM_c w_c p(y_c | s) A_scene for one arm and weight form. NaN if not computed.
    pub fn ln_l_h(&self, lon: f64, lat: f64, unix_s: f64, arm: usize, count_weights: bool) -> f64 {
        let targets = &self.arms[arm];
        let mut sum = 0.0;
        let mut wsum = 0.0;
        for t in targets {
            let ends: Vec<Option<[f64; 2]>> = (0..self.table.nw).map(|k| self.table.endpoint(lon, lat, k, t.time_index)).collect();
            let dt = t.dt_ref_unix_s - unix_s;
            let Some(p) = density(&ends, [t.lon, t.lat], dt, &self.spread) else {
                return f64::NAN;
            };
            let w = if count_weights { t.w_count } else { t.w_equal };
            sum += w * p * A_SCENE_KM2;
            wsum += w;
        }
        debug_assert!((wsum - 1.0).abs() < 1e-6, "cluster weights must sum to one, got {wsum}");
        sum.ln()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    /// A synthetic table: uniform current u (m/s east) and windage pushing v_w per unit c (m/s north).
    fn synthetic(u_e: f64, v_n_per_c: f64) -> Table {
        let (lon0, lat0, step, nlon, nlat, nw) = (90.0, -36.0, 0.1, 21, 21, 21);
        let release = 1_394_238_000.0;
        let outs = vec![1_395_548_640.0];
        let dt = outs[0] - release;
        let mut data = Vec::new();
        for j in 0..nlat {
            for i in 0..nlon {
                for k in 0..nw {
                    let (lon, lat) = (lon0 + i as f64 * step, lat0 + j as f64 * step);
                    let c = k as f64 * 0.0025;
                    let de = u_e * dt / 1000.0;
                    let dn = v_n_per_c * c * dt / 1000.0;
                    let lat1 = lat + dn / KM_PER_DEG;
                    let lon1 = lon + de / (KM_PER_DEG * (0.5 * (lat + lat1)).to_radians().cos());
                    data.push(lon1 as f32);
                    data.push(lat1 as f32);
                }
            }
        }
        Table { lon0, lat0, step, nlon, nlat, nw, out_unix_s: outs, release_unix_s: release, ocean_model: "analytic".into(), data }
    }

    fn spread() -> Spread {
        Spread::new(0.05, 2.0 * 86400.0, 0.5, 30.0, 1000.0, 8)
    }

    #[test]
    fn gauss_legendre_nodes_integrate_polynomials() {
        let (x, w) = gauss_legendre(8);
        let i4: f64 = x.iter().zip(&w).map(|(x, w)| w * x.powi(4)).sum();
        assert!((i4 - 0.4).abs() < 1e-12, "{i4}");
        assert!((w.iter().sum::<f64>() - 2.0).abs() < 1e-12);
    }

    #[test]
    fn density_integrates_to_one_over_the_plane() {
        // brief section 12: p(y|s) integrates to one, to tolerance, for a representative s.
        let t = synthetic(0.1, 4.0);
        let s = spread();
        let (lon, lat) = (91.03, -35.04);
        let ends: Vec<_> = (0..t.nw).map(|k| t.endpoint(lon, lat, k, 0)).collect();
        let dt = t.out_unix_s[0] - t.release_unix_s;
        let c = ends[10].unwrap();
        // integrate on a 4 km grid over +-600 km: windage nodes span +-131 km, widest node sd ~ 60 km
        let (h, n) = (4.0, 150);
        let mut total = 0.0;
        for a in -n..=n {
            for b in -n..=n {
                let (de, dn) = (a as f64 * h, b as f64 * h);
                let lat_y = c[1] + dn / KM_PER_DEG;
                let lon_y = c[0] + de / (KM_PER_DEG * (0.5 * (c[1] + lat_y)).to_radians().cos());
                total += density(&ends, [lon_y, lat_y], dt, &s).unwrap() * h * h;
            }
        }
        assert!((total - 1.0).abs() < 2e-3, "integral {total}");
    }

    #[test]
    fn column_is_seed_free_and_deterministic() {
        // brief section 12: two seeds give the same column. There is no seed: two independent
        // constructions must agree exactly, bit for bit.
        let make = || PositionLikelihood {
            table: synthetic(0.1, 4.0),
            spread: spread(),
            arms: vec![vec![Target { scene: "PHR_4".into(), lon: 91.4, lat: -35.0, w_equal: 1.0, w_count: 1.0, time_index: 0, dt_ref_unix_s: 1_395_548_640.0 }]],
        };
        let (a, b) = (make(), make());
        for i in 0..50 {
            let (lon, lat) = (90.2 + 0.03 * i as f64, -35.9 + 0.02 * i as f64);
            let (x, y) = (a.ln_l_h(lon, lat, 1_394_238_300.0, 0, false), b.ln_l_h(lon, lat, 1_394_238_300.0, 0, false));
            assert_eq!(x.to_bits(), y.to_bits());
        }
    }

    #[test]
    fn interpolation_is_exact_for_a_uniform_flow_and_outside_is_not_computed() {
        let t = synthetic(0.1, 4.0);
        let dt = t.out_unix_s[0] - t.release_unix_s;
        let e = t.endpoint(90.537, -35.513, 0, 0).unwrap();
        let d = offset_km([90.537, -35.513], e);
        assert!((d[0] - 0.1 * dt / 1000.0).abs() < 0.05, "{d:?}");
        assert!(t.endpoint(89.0, -35.5, 0, 0).is_none());
        assert!(t.endpoint(92.01, -35.5, 0, 0).is_none());
    }

    #[test]
    fn variance_has_the_declared_closed_form() {
        let s = Spread::new(0.05, 2.0 * 86400.0, 0.5, 248.0, 248.0, 1);
        let dt: f64 = 40.5 * 3600.0;
        let t_e: f64 = 2.0 * 86400.0;
        let ou = 2.0 * 0.0025 * t_e * (dt - t_e * (1.0 - (-dt / t_e).exp())) / 1e6;
        assert!((s.var_km2(248.0, dt) - (2.0 * 248.0 * dt / 1e6 + ou + 0.25)).abs() < 1e-12);
        // long-time limit of the OU part is diffusive: 2 sigma^2 T_e dt
        let s0 = Spread::new(0.05, 3600.0, 0.0, 0.0, 0.0, 1);
        let big = 1e7;
        assert!((s0.var_km2(0.0, big) / (2.0 * 0.0025 * 3600.0 * big / 1e6) - 1.0).abs() < 1e-3);
    }
}
