//! The project's one bathymetry surface (brief rule 8): shared by settling's impact-point lookup,
//! hydroacoustics' path sampling and searched areas' terrain masking.
//!
//! Layers in priority order; the first layer with a value at a point answers, and every answer carries
//! its [`BathySource`] (the per-cell provenance flag) and, for GEBCO, the Type Identifier (TID) of
//! that cell. Intended layers: AusSeabed MH370 Phase 1 150 m inside its coverage, GEBCO_2026 (15 arc-
//! second) everywhere else. Elevation is positive up, metres, on the grid's own vertical datum (GEBCO:
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

/// One regular, cell-centred lon/lat grid.
struct Layer {
    source: BathySource,
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
    /// Centre of the first cell (south-west corner of the stored window).
    lon0: f64,
    lat0: f64,
    step_deg: f64,
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
        let [lon_min, lon_max, lat_min, lat_max] = window.unwrap_or([f64::NEG_INFINITY, f64::INFINITY, f64::NEG_INFINITY, f64::INFINITY]);
        let idx = |x: f64, x0: f64, n: usize| (((x - x0) / m.step_deg).floor().max(0.0) as usize).min(n);
        let i0 = idx(lon_min, m.lon0, m.nlon).saturating_sub(1);
        let i1 = (idx(lon_max, m.lon0, m.nlon) + 2).min(m.nlon);
        let j0 = idx(lat_min, m.lat0, m.nlat).saturating_sub(1);
        let j1 = (idx(lat_max, m.lat0, m.nlat) + 2).min(m.nlat);
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
            lon0: m.lon0 + i0 as f64 * m.step_deg,
            lat0: m.lat0 + j0 as f64 * m.step_deg,
            step: m.step_deg,
            nlon: i1 - i0,
            nlat: j1 - j0,
            z,
            tid,
        })
    }

    fn nearest(&self, p: LonLat) -> Option<BathySample> {
        let i = ((p[0] - self.lon0) / self.step).round();
        let j = ((p[1] - self.lat0) / self.step).round();
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
