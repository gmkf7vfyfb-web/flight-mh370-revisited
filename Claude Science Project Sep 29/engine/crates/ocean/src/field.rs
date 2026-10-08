//! Field access. [`VectorField`] is the one trait every horizontal velocity source implements:
//! analytic fields now, gridded products ([`GridField`]) as soon as data arrive. A gridded product
//! is a drop-in because the integrator never sees anything but this trait and the field's
//! declared [`FieldMeta`].

use crate::products::{Contents, TimeAxis};
use crate::LonLat;
use serde::Serialize;

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
#[derive(Clone, Copy, Debug, PartialEq, Eq, Serialize)]
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
}

/// Index of the lower bracket and the fractional weight of the upper, or None if outside.
fn bracket(axis: &[f64], x: f64) -> Option<(usize, f64)> {
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
