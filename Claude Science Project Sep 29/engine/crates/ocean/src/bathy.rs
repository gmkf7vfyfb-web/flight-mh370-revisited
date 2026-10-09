//! The project's one bathymetry surface (brief rule 8): shared by settling's impact-point lookup,
//! hydroacoustics' path sampling and searched areas' terrain masking.
//!
//! Layers in priority order; the first layer with a value at a point answers, and every answer carries
//! its [`BathySource`] (the per-cell provenance flag) and, for GEBCO, the Type Identifier (TID) of
//! that cell. Layers: AusSeabed MH370 Phase 1 150 m inside its coverage (Geoscience Australia
//! ga/100315, kept on its distributed EPSG:3857 grid, no resampling), GEBCO_2026 (15 arc-second)
//! everywhere else. Elevation is positive up, metres, on the grid's own vertical datum (GEBCO:
//! mean sea level); `depth_m` is its negative.
//!
//! Paths are WGS84 geodesics (Karney's algorithm). [`Bathymetry::path`] samples the track at a stated
//! spacing, nearest cell (no interpolation, so every value is a real grid value with its own TID), and
//! reports the corridor maximum: the highest elevation within a stated cross-track half-width, sampled
//! along the perpendicular geodesics at the same spacing, because blockage is set by the shallowest
//! feature in the ensonified corridor.

use crate::LonLat;
use geographiclib_rs::{DirectGeodesic, Geodesic, InverseGeodesic};
use serde::{Deserialize, Serialize};
use std::fs::File;
use std::io::{Read, Seek, SeekFrom};
use std::path::Path;

#[derive(Clone, Copy, Debug, PartialEq, Eq, Serialize, Deserialize)]
pub enum BathySource {
    #[serde(rename = "ausseabed")]
    AusSeabed,
    #[serde(rename = "gebco_2026")]
    Gebco2026,
}

#[derive(Clone, Copy, Debug, PartialEq, Serialize)]
pub struct BathySample {
    pub point: LonLat,
    pub elevation_m: f64,
    pub depth_m: f64,
    pub source: BathySource,
    /// GEBCO Type Identifier of the answering cell (`None` for layers without one).
    pub tid: Option<u8>,
}

#[derive(Clone, Copy, Debug, PartialEq, Serialize)]
pub struct PathSample {
    /// Distance along the geodesic from the start, m.
    pub s_m: f64,
    pub track: BathySample,
    /// Highest elevation within the corridor (including the track point).
    pub corridor_max: BathySample,
    /// Signed cross-track offset of `corridor_max`, m, positive to the right of the direction of travel.
    pub corridor_max_offset_m: f64,
}

enum Values {
    I16(Vec<i16>),
    F32(Vec<f32>),
}

/// Grid axes of a layer.
#[derive(Clone, Copy, Debug, PartialEq)]
enum Proj {
    /// Regular longitude/latitude, degrees.
    LonLat,
    /// EPSG:3857 WGS 84 / Pseudo-Mercator, metres: x = a*lon, y = a*ln(tan(pi/4 + lat/2)), a = 6378137
    /// m, applied to WGS84 geodetic coordinates (the EPSG definition, exact).
    WebMercator,
}

const WEB_MERCATOR_A: f64 = 6_378_137.0;

impl Proj {
    fn native(self, p: LonLat) -> [f64; 2] {
        match self {
            Proj::LonLat => p,
            Proj::WebMercator => {
                let phi = p[1].clamp(-89.9, 89.9).to_radians();
                [WEB_MERCATOR_A * p[0].to_radians(), WEB_MERCATOR_A * (std::f64::consts::FRAC_PI_4 + 0.5 * phi).tan().ln()]
            }
        }
    }
}

/// One regular, cell-centred grid (lon/lat or Web Mercator).
struct Layer {
    source: BathySource,
    proj: Proj,
    lon0: f64,
    lat0: f64,
    step: f64,
    nlon: usize,
    nlat: usize,
    z: Values,
    tid: Option<Vec<u8>>,
}

#[derive(Deserialize)]
struct Manifest {
    source: BathySource,
    /// `"epsg3857"` for a Web Mercator grid given by `x0_m`, `y0_m`, `step_m`; absent for lon/lat.
    #[serde(default)]
    projection: Option<String>,
    /// Centre of the first cell (south-west corner of the stored window).
    #[serde(default)]
    lon0: f64,
    #[serde(default)]
    lat0: f64,
    #[serde(default)]
    step_deg: f64,
    #[serde(default)]
    x0_m: f64,
    #[serde(default)]
    y0_m: f64,
    #[serde(default)]
    step_m: f64,
    nlon: usize,
    nlat: usize,
    elevation_file: String,
    /// "i16" or "f32" (NaN = no data), little-endian, rows south to north.
    elevation_dtype: String,
    tid_file: Option<String>,
}

fn read_window(path: &Path, elem: usize, nlon: usize, (i0, i1, j0, j1): (usize, usize, usize, usize)) -> Result<Vec<u8>, String> {
    let mut f = File::open(path).map_err(|e| format!("{}: {e}", path.display()))?;
    let w = i1 - i0;
    let mut out = vec![0u8; w * (j1 - j0) * elem];
    for (r, j) in (j0..j1).enumerate() {
        f.seek(SeekFrom::Start(((j * nlon + i0) * elem) as u64)).map_err(|e| e.to_string())?;
        f.read_exact(&mut out[r * w * elem..(r + 1) * w * elem]).map_err(|e| format!("{}: {e}", path.display()))?;
    }
    Ok(out)
}

impl Layer {
    fn load(manifest: &Path, window: Option<[f64; 4]>) -> Result<Layer, String> {
        let text = std::fs::read_to_string(manifest).map_err(|e| format!("{}: {e}", manifest.display()))?;
        let m: Manifest = serde_json::from_str(&text).map_err(|e| format!("{}: {e}", manifest.display()))?;
        let dir = manifest.parent().unwrap_or(Path::new("."));
        let (proj, x0, y0, step) = match m.projection.as_deref() {
            None | Some("lonlat") => (Proj::LonLat, m.lon0, m.lat0, m.step_deg),
            Some("epsg3857") => (Proj::WebMercator, m.x0_m, m.y0_m, m.step_m),
            Some(p) => return Err(format!("{}: unknown projection {p}", manifest.display())),
        };
        if !(step > 0.0) {
            return Err(format!("{}: grid step missing", manifest.display()));
        }
        // Both projections are monotonic in each axis, so the window's corners bound it.
        let [lon_min, lon_max, lat_min, lat_max] = window.unwrap_or([-180.0, 180.0, -89.9, 89.9]);
        let lo = proj.native([lon_min, lat_min]);
        let hi = proj.native([lon_max, lat_max]);
        let idx = |x: f64, x0: f64, n: usize| (((x - x0) / step).floor().max(0.0) as usize).min(n);
        let i0 = idx(lo[0], x0, m.nlon).saturating_sub(1);
        let i1 = (idx(hi[0], x0, m.nlon) + 2).min(m.nlon);
        let j0 = idx(lo[1], y0, m.nlat).saturating_sub(1);
        let j1 = (idx(hi[1], y0, m.nlat) + 2).min(m.nlat);
        if i1 <= i0 || j1 <= j0 {
            return Err("window does not overlap the grid".into());
        }
        let w = (i0, i1, j0, j1);
        let z = match m.elevation_dtype.as_str() {
            "i16" => Values::I16(read_window(&dir.join(&m.elevation_file), 2, m.nlon, w)?.chunks_exact(2).map(|b| i16::from_le_bytes([b[0], b[1]])).collect()),
            "f32" => Values::F32(read_window(&dir.join(&m.elevation_file), 4, m.nlon, w)?.chunks_exact(4).map(|b| f32::from_le_bytes([b[0], b[1], b[2], b[3]])).collect()),
            d => return Err(format!("unknown elevation dtype {d}")),
        };
        let tid = match &m.tid_file {
            Some(f) => Some(read_window(&dir.join(f), 1, m.nlon, w)?),
            None => None,
        };
        Ok(Layer {
            source: m.source,
            proj,
            lon0: x0 + i0 as f64 * step,
            lat0: y0 + j0 as f64 * step,
            step,
            nlon: i1 - i0,
            nlat: j1 - j0,
            z,
            tid,
        })
    }

    fn nearest(&self, p: LonLat) -> Option<BathySample> {
        let q = self.proj.native(p);
        let i = ((q[0] - self.lon0) / self.step).round();
        let j = ((q[1] - self.lat0) / self.step).round();
        if i < 0.0 || j < 0.0 || i as usize >= self.nlon || j as usize >= self.nlat {
            return None;
        }
        let k = j as usize * self.nlon + i as usize;
        let e = match &self.z {
            Values::I16(v) => v[k] as f64,
            Values::F32(v) => v[k] as f64,
        };
        if !e.is_finite() {
            return None;
        }
        Some(BathySample { point: p, elevation_m: e, depth_m: -e, source: self.source, tid: self.tid.as_ref().map(|t| t[k]) })
    }
}

/// The layered surface.
pub struct Bathymetry {
    layers: Vec<Layer>,
    geodesic: Geodesic,
}

impl Bathymetry {
    /// Load layers from manifests in priority order (finest first), each cut to `window`
    /// `[lon_min, lon_max, lat_min, lat_max]` if given.
    pub fn load(manifests: &[&Path], window: Option<[f64; 4]>) -> Result<Self, String> {
        let layers = manifests.iter().map(|m| Layer::load(m, window)).collect::<Result<Vec<_>, _>>()?;
        Ok(Bathymetry { layers, geodesic: Geodesic::wgs84() })
    }

    /// The answering layer's nearest cell.
    pub fn at(&self, p: LonLat) -> Option<BathySample> {
        self.layers.iter().find_map(|l| l.nearest(p))
    }

    /// Geodesic distance (m) and initial azimuth (deg) from `a` to `b` on WGS84.
    pub fn inverse(&self, a: LonLat, b: LonLat) -> (f64, f64) {
        let (s12, azi1, _azi2, _a12): (f64, f64, f64, f64) = self.geodesic.inverse(a[1], a[0], b[1], b[0]);
        (s12, azi1)
    }

    /// Depth along the WGS84 geodesic from `a` to `b`, every `spacing_m` (last sample at `b`), with
    /// the corridor maximum within `half_width_m` either side. `None` entries are off every layer.
    pub fn path(&self, a: LonLat, b: LonLat, spacing_m: f64, half_width_m: f64) -> Vec<Option<PathSample>> {
        let g = &self.geodesic;
        let (s12, azi1) = self.inverse(a, b);
        let n = (s12 / spacing_m).ceil().max(1.0) as usize;
        let m = (half_width_m / spacing_m).ceil() as usize;
        (0..=n)
            .map(|k| {
                let s = (k as f64 * spacing_m).min(s12);
                let (lat, lon, azi): (f64, f64, f64) = g.direct(a[1], a[0], azi1, s);
                let track = self.at([lon, lat])?;
                let (mut best, mut off) = (track, 0.0);
                for j in 1..=m {
                    let d = (j as f64 * spacing_m).min(half_width_m);
                    for side in [1.0, -1.0] {
                        let (clat, clon): (f64, f64) = g.direct(lat, lon, azi + 90.0 * side, d);
                        if let Some(c) = self.at([clon, clat]) {
                            if c.elevation_m > best.elevation_m {
                                best = c;
                                off = side * d;
                            }
                        }
                    }
                }
                Some(PathSample { s_m: s, track, corridor_max: best, corridor_max_offset_m: off })
            })
            .collect()
    }
}
