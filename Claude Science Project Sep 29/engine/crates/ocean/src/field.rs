//! Field access. [`VectorField`] is the one trait every horizontal velocity source implements:
//! analytic fields now, gridded products ([`GridField`]) as soon as data arrive. A gridded product
//! is a drop-in because the integrator never sees anything but this trait and the field's
//! declared [`FieldMeta`].

use crate::products::{product, Contents, TimeAxis};
use crate::LonLat;
use serde::{Deserialize, Serialize};
use std::path::Path;

/// Why a field has no value at a query point. Never a silent zero.
#[derive(Clone, Copy, Debug, PartialEq, Eq, Serialize)]
pub enum FieldGap {
    /// Every grid node that would contribute is land in the product's mask.
    Land,
    /// Outside the field's horizontal extent.
    OutsideDomain,
    /// Outside the field's time axis (the archive clamped; this does not).
    OutsideTime,
    /// A node the product calls sea holds a non-finite value.
    NonFinite,
}

/// Which velocity component a field supplies.
#[derive(Clone, Copy, Debug, PartialEq, Eq, Serialize, Deserialize)]
pub enum Component {
    Current,
    StokesDrift,
    Wind10m,
}

/// Declared identity of a field: the product it came from and what it contains.
#[derive(Clone, Debug, Serialize)]
pub struct FieldMeta {
    /// Product id (`products::catalogue()` id, or `analytic:<name>`), used for `ocean-model`.
    pub product: String,
    pub component: Component,
    pub contents: Contents,
    pub time_axis: TimeAxis,
    pub description: String,
}

/// A horizontal vector field, east/north in m/s.
pub trait VectorField: Send + Sync {
    fn sample(&self, t: f64, p: LonLat) -> Result<[f64; 2], FieldGap>;
    fn meta(&self) -> &FieldMeta;
}

/// A regular longitude-latitude-time grid of float32 vectors, as a server-side subset of a
/// reanalysis is stored. Trilinear in (time, latitude, longitude) with **land renormalisation**:
/// land nodes are dropped and the remaining weights renormalised, never filled with zero.
///
/// Times are the instants each slice represents: for a daily-mean product the loader must pass
/// interval centres (see `products::TimeAxis::Mean`).
pub struct GridField {
    meta: FieldMeta,
    lon: Vec<f64>,
    lat: Vec<f64>,
    time: Vec<f64>,
    /// `[time][lat][lon][2]`, NaN at land.
    data: Vec<f32>,
    /// Optional static `[lat][lon]` sea mask (true = sea). With it, NaN at a sea node is
    /// `NonFinite`; without it, every NaN is land.
    sea: Option<Vec<bool>>,
}

impl GridField {
    pub fn new(
        meta: FieldMeta,
        lon: Vec<f64>,
        lat: Vec<f64>,
        time: Vec<f64>,
        data: Vec<f32>,
        sea: Option<Vec<bool>>,
    ) -> Result<Self, String> {
        let ascending = |v: &[f64]| !v.is_empty() && v.windows(2).all(|w| w[1] > w[0]);
        if !ascending(&lon) || !ascending(&lat) || !ascending(&time) {
            return Err("grid axes must be non-empty and strictly ascending".into());
        }
        if data.len() != time.len() * lat.len() * lon.len() * 2 {
            return Err(format!("data length {} does not match axes", data.len()));
        }
        if let Some(m) = &sea {
            if m.len() != lat.len() * lon.len() {
                return Err("sea mask length does not match axes".into());
            }
        }
        Ok(GridField { meta, lon, lat, time, data, sea })
    }

    /// Load a grid written by `prepare/netcdf_to_grid.py`: a JSON manifest beside a little-endian
    /// float32 file laid out `[time][lat][lon][east, north]`, NaN at land, with times already at the
    /// instants the values represent (interval centres for means). The product must be in
    /// `products::catalogue()`; its contents and time axis come from there, never from the file.
    pub fn load(manifest: &Path) -> Result<Self, String> {
        Self::load_part(manifest, &LoadWindow::all())
    }

    /// Load a part manifest or a series manifest (`*.series.json`) cut to `window`. Only the
    /// needed rows are read from disk. The window keeps the bracketing grid nodes and slices, so
    /// every query inside it interpolates exactly as on the full grid; outside it the field
    /// answers `OutsideDomain` / `OutsideTime`.
    pub fn load_window(path: &Path, window: &LoadWindow) -> Result<Self, String> {
        if path.to_string_lossy().ends_with(".series.json") {
            Self::load_series_window(path, window)
        } else {
            Self::load_part(path, window)
        }
    }

    fn read_manifest(manifest: &Path) -> Result<PartManifest, String> {
        let text = std::fs::read_to_string(manifest).map_err(|e| format!("{}: {e}", manifest.display()))?;
        serde_json::from_str(&text).map_err(|e| format!("{}: {e}", manifest.display()))
    }

    fn load_part(manifest: &Path, w: &LoadWindow) -> Result<Self, String> {
        let m = Self::read_manifest(manifest)?;
        let (t0, t1) = keep(&m.time_unix_s, w.time).ok_or_else(|| format!("{}: time window outside the part", manifest.display()))?;
        Self::load_part_slices(manifest, m, w, t0, t1)
    }

    /// Read time slices `t0..=t1` of one part, cut horizontally to `w`.
    fn load_part_slices(manifest: &Path, m: PartManifest, w: &LoadWindow, t0: usize, t1: usize) -> Result<Self, String> {
        let meta = product(&m.product).ok_or_else(|| format!("product {} is not in the catalogue", m.product))?;
        let (nx, ny) = (m.lon.len(), m.lat.len());
        let (i0, i1) = keep(&m.lon, w.lon).ok_or_else(|| format!("{}: longitude window outside the grid", manifest.display()))?;
        let (j0, j1) = keep(&m.lat, w.lat).ok_or_else(|| format!("{}: latitude window outside the grid", manifest.display()))?;
        let path = manifest.parent().unwrap_or(Path::new(".")).join(&m.data_file);
        let file = std::fs::File::open(&path).map_err(|e| format!("{}: {e}", path.display()))?;
        let len = file.metadata().map_err(|e| e.to_string())?.len();
        if len != (m.time_unix_s.len() * ny * nx * 8) as u64 {
            return Err(format!("{}: {len} bytes, axes imply {}", path.display(), m.time_unix_s.len() * ny * nx * 8));
        }
        let wx = i1 - i0 + 1;
        let mut data = Vec::with_capacity((t1 - t0 + 1) * (j1 - j0 + 1) * wx * 2);
        if (i0, i1, j0, j1) == (0, nx - 1, 0, ny - 1) {
            let mut buf = vec![0u8; (t1 - t0 + 1) * ny * nx * 8];
            read_at(&file, &mut buf, (t0 * ny * nx * 8) as u64, &path)?;
            data.extend(buf.chunks_exact(4).map(|b| f32::from_le_bytes([b[0], b[1], b[2], b[3]])));
        } else {
            let mut buf = vec![0u8; wx * 8];
            for t in t0..=t1 {
                for j in j0..=j1 {
                    read_at(&file, &mut buf, (((t * ny + j) * nx + i0) * 8) as u64, &path)?;
                    data.extend(buf.chunks_exact(4).map(|b| f32::from_le_bytes([b[0], b[1], b[2], b[3]])));
                }
            }
        }
        let meta = FieldMeta {
            product: m.product,
            component: m.component,
            contents: meta.contents,
            time_axis: meta.time_axis,
            description: if w.is_all() { m.description } else { format!("{} (window {:?})", m.description, w) },
        };
        GridField::new(meta, m.lon[i0..=i1].to_vec(), m.lat[j0..=j1].to_vec(), m.time_unix_s[t0..=t1].to_vec(), data, None)
    }

    /// Bytes of field data held in memory.
    pub fn data_bytes(&self) -> usize {
        self.data.len() * 4
    }

    /// Time axis (unix s), longitudes and latitudes of the grid.
    pub fn axes(&self) -> (&[f64], &[f64], &[f64]) {
        (&self.time, &self.lon, &self.lat)
    }

    /// Load a series manifest (`{"parts": ["a.json", "b.json", ...]}`) whose parts share one grid
    /// and follow each other in time, as one field. Interpolation runs across part boundaries.
    pub fn load_series(series: &Path) -> Result<Self, String> {
        Self::load_series_window(series, &LoadWindow::all())
    }

    fn load_series_window(series: &Path, w: &LoadWindow) -> Result<Self, String> {
        #[derive(Deserialize)]
        struct Series {
            parts: Vec<String>,
        }
        let text = std::fs::read_to_string(series).map_err(|e| format!("{}: {e}", series.display()))?;
        let s: Series = serde_json::from_str(&text).map_err(|e| format!("{}: {e}", series.display()))?;
        let dir = series.parent().unwrap_or(Path::new("."));
        let manifests = s.parts.iter().map(|p| Self::read_manifest(&dir.join(p)).map(|m| (p, m))).collect::<Result<Vec<_>, _>>()?;
        // The window's slices on the joined time axis, so a bracket across a part seam is kept.
        let joined: Vec<f64> = manifests.iter().flat_map(|(_, m)| m.time_unix_s.iter().copied()).collect();
        if !joined.windows(2).all(|x| x[1] > x[0]) {
            return Err(format!("{}: part times do not follow each other", series.display()));
        }
        let (g0, g1) = keep(&joined, w.time).ok_or_else(|| format!("{}: time window outside the series", series.display()))?;
        let mut out: Option<GridField> = None;
        let mut offset = 0;
        for (part, m) in manifests {
            let n = m.time_unix_s.len();
            let (a, b) = (g0.max(offset), g1.min(offset + n - 1));
            offset += n;
            if a > b {
                continue;
            }
            let g = Self::load_part_slices(&dir.join(part), m, w, a - (offset - n), b - (offset - n))?;
            out = Some(match out {
                None => g,
                Some(mut acc) => {
                    if acc.lon != g.lon || acc.lat != g.lat || acc.meta.product != g.meta.product || acc.meta.component != g.meta.component {
                        return Err(format!("{part}: grid, product or component differs from the first part"));
                    }
                    acc.time.extend_from_slice(&g.time);
                    acc.data.extend_from_slice(&g.data);
                    acc.meta.description = format!("{}; {}", acc.meta.description, g.meta.description);
                    acc
                }
            });
        }
        out.ok_or_else(|| "empty series".into())
    }
}

/// A load window: longitude, latitude (degrees) and time (unix s) ranges, each `None` for the whole
/// axis. Bounds are inclusive; the loaded grid extends to the nodes that bracket them.
#[derive(Clone, Copy, Debug, Default, PartialEq, Serialize)]
pub struct LoadWindow {
    pub lon: Option<[f64; 2]>,
    pub lat: Option<[f64; 2]>,
    pub time: Option<[f64; 2]>,
}

impl LoadWindow {
    pub fn all() -> Self {
        Self::default()
    }
    /// `[lon_min, lon_max, lat_min, lat_max]` and `[t_start, t_end]`.
    pub fn new(bbox: [f64; 4], time: [f64; 2]) -> Self {
        LoadWindow { lon: Some([bbox[0], bbox[1]]), lat: Some([bbox[2], bbox[3]]), time: Some(time) }
    }
    fn is_all(&self) -> bool {
        self.lon.is_none() && self.lat.is_none() && self.time.is_none()
    }
}

#[derive(Deserialize)]
struct PartManifest {
    product: String,
    component: Component,
    description: String,
    lon: Vec<f64>,
    lat: Vec<f64>,
    time_unix_s: Vec<f64>,
    data_file: String,
}

/// Inclusive index range of an ascending axis that brackets `[lo, hi]`: from the last node at or
/// below `lo` to the first node at or above `hi`, clamped to the axis. `None` if the range misses
/// the axis or is inverted.
fn keep(axis: &[f64], range: Option<[f64; 2]>) -> Option<(usize, usize)> {
    let n = axis.len();
    let Some([lo, hi]) = range else { return Some((0, n - 1)) };
    if !(hi >= lo) || hi < axis[0] || lo > axis[n - 1] {
        return None;
    }
    let a = axis.partition_point(|&x| x <= lo).saturating_sub(1);
    let b = axis.partition_point(|&x| x < hi).min(n - 1);
    Some((a, b))
}

fn read_at(file: &std::fs::File, buf: &mut [u8], offset: u64, path: &Path) -> Result<(), String> {
    use std::os::unix::fs::FileExt;
    file.read_exact_at(buf, offset).map_err(|e| format!("{}: {e}", path.display()))
}

/// Index of the lower bracket and the fractional weight of the upper, or None if outside.
pub(crate) fn bracket(axis: &[f64], x: f64) -> Option<(usize, f64)> {
    let n = axis.len();
    if !(x >= axis[0] && x <= axis[n - 1]) {
        return None;
    }
    if n == 1 {
        return Some((0, 0.0));
    }
    let i = axis.partition_point(|&a| a <= x).saturating_sub(1).min(n - 2);
    Some((i, (x - axis[i]) / (axis[i + 1] - axis[i])))
}

impl VectorField for GridField {
    fn sample(&self, t: f64, p: LonLat) -> Result<[f64; 2], FieldGap> {
        let (it, wt) = bracket(&self.time, t).ok_or(FieldGap::OutsideTime)?;
        let (iy, wy) = bracket(&self.lat, p[1]).ok_or(FieldGap::OutsideDomain)?;
        let (ix, wx) = bracket(&self.lon, p[0]).ok_or(FieldGap::OutsideDomain)?;
        let (nx, ny) = (self.lon.len(), self.lat.len());
        let mut acc = [0.0f64; 2];
        let mut total = 0.0;
        for (dt, ft) in [(0usize, 1.0 - wt), (1, wt)] {
            for (dy, fy) in [(0usize, 1.0 - wy), (1, wy)] {
                for (dx, fx) in [(0usize, 1.0 - wx), (1, wx)] {
                    let w = ft * fy * fx;
                    if w == 0.0 {
                        continue;
                    }
                    let (k, j, i) = (it + dt, iy + dy, ix + dx);
                    let cell = j * nx + i;
                    let base = ((k * ny + j) * nx + i) * 2;
                    let (u, v) = (self.data[base] as f64, self.data[base + 1] as f64);
                    if u.is_finite() && v.is_finite() {
                        acc[0] += w * u;
                        acc[1] += w * v;
                        total += w;
                    } else if self.sea.as_ref().is_some_and(|m| m[cell]) {
                        return Err(FieldGap::NonFinite);
                    }
                }
            }
        }
        if total > 0.0 {
            Ok([acc[0] / total, acc[1] / total])
        } else {
            Err(FieldGap::Land)
        }
    }
    fn meta(&self) -> &FieldMeta {
        &self.meta
    }
}
