//! The profile query settling asked for: current, temperature, salinity and pressure on the
//! product's levels from the surface to the model bottom, at one horizontal position and time,
//! evaluated once per descending element.
//!
//! Two conditions are structural rather than conventions:
//! - vertical velocity is [`VerticalVelocity::Absent`] or `Present`, never a vector of zeros, and
//!   [`DepthSample::w_up`] is an `Option`;
//! - a seabed deeper than the model's local bottom is a flagged [`BottomRelation`], and any query
//!   below the model bottom either applies an explicit, caller-chosen [`BelowModelBottom`] rule
//!   (reported in [`DepthStatus::Extrapolated`]) or is refused.
//!
//! Depth is geometric depth in metres, positive downward, below the mean sea surface. Pressure is
//! provisional (Saunders 1981) until the TEOS-10 layer (deliverable 8) replaces it with
//! `gsw_p_from_z`; temperature keeps its product's kind (potential or in-situ) so the conversion
//! happens once, in that layer, not at three call sites.

use crate::field::{FieldGap, FieldMeta};
use crate::products::TimeAxis;
use crate::LonLat;
use serde::Serialize;

#[derive(Clone, Debug, PartialEq, Serialize)]
pub enum VerticalVelocity {
    /// The product has no resolved vertical velocity. Not zero.
    Absent,
    /// m/s, positive upward, one per level.
    Present(Vec<f64>),
}

#[derive(Clone, Debug, PartialEq, Serialize)]
pub enum Temperature {
    /// Potential temperature referenced to 0 dbar, degC (GLORYS12 `thetao`).
    Potential(Vec<f64>),
    /// In-situ temperature, degC (HYCOM).
    InSitu(Vec<f64>),
}

#[derive(Clone, Debug, PartialEq, Serialize)]
pub enum Salinity {
    Practical(Vec<f64>),
    /// g/kg
    Absolute(Vec<f64>),
}

/// One water column. Vectors are per level, ordered by increasing depth.
#[derive(Clone, Debug, Serialize)]
pub struct Profile {
    /// Level depths, geometric, m, positive down.
    pub depth_m: Vec<f64>,
    pub u_east: Vec<f64>,
    pub v_north: Vec<f64>,
    pub w_up: VerticalVelocity,
    pub temperature: Temperature,
    pub salinity: Salinity,
    pub pressure_dbar: Vec<f64>,
    /// The ocean model's own sea-floor depth in this column, m.
    pub model_bottom_m: f64,
    pub time_axis: TimeAxis,
}

/// What to do below the model bottom. The caller chooses and varies it; the choice is reported.
#[derive(Clone, Copy, Debug, PartialEq, Serialize)]
pub enum BelowModelBottom {
    Refuse,
    /// Hold the deepest model level's velocity down to the seabed.
    HoldDeepestLevel,
    /// Deepest level's velocity at the model bottom, decreasing linearly to zero at the seabed.
    LinearToZeroAtSeabed,
}

#[derive(Clone, Copy, Debug, PartialEq, Serialize)]
pub enum BottomRelation {
    /// The model column reaches at least as deep as the seabed.
    WithinModel,
    /// The detailed bathymetry is deeper than the model bottom by `gap_m`.
    SeabedDeeperThanModel { model_bottom_m: f64, seabed_m: f64, gap_m: f64 },
}

#[derive(Clone, Copy, Debug, PartialEq, Serialize)]
pub enum DepthStatus {
    /// Interpolated between model levels; above the first level and between the deepest level
    /// and the model bottom the nearest level is held.
    Resolved,
    Extrapolated { rule: BelowModelBottom, model_bottom_m: f64, seabed_m: Option<f64> },
}

#[derive(Clone, Copy, Debug, PartialEq, Serialize)]
pub struct DepthSample {
    pub u_east: f64,
    pub v_north: f64,
    /// `None` when the product has no vertical velocity.
    pub w_up: Option<f64>,
    pub status: DepthStatus,
}

#[derive(Clone, Copy, Debug, PartialEq, Serialize)]
pub enum DepthGap {
    AboveSurface,
    BelowSeabed { seabed_m: f64 },
    /// Below the model bottom with `Refuse`, or with a rule that needs a seabed depth and none given.
    BelowModelBottom { model_bottom_m: f64 },
}

impl Profile {
    pub fn bottom_relation(&self, seabed_m: f64) -> BottomRelation {
        if seabed_m > self.model_bottom_m {
            BottomRelation::SeabedDeeperThanModel {
                model_bottom_m: self.model_bottom_m,
                seabed_m,
                gap_m: seabed_m - self.model_bottom_m,
            }
        } else {
            BottomRelation::WithinModel
        }
    }

    /// Velocity at depth `z_m`. `seabed_m` is the detailed bathymetry at this position, if known.
    pub fn at_depth(&self, z_m: f64, seabed_m: Option<f64>, rule: BelowModelBottom) -> Result<DepthSample, DepthGap> {
        if z_m < 0.0 {
            return Err(DepthGap::AboveSurface);
        }
        if let Some(s) = seabed_m {
            if z_m > s {
                return Err(DepthGap::BelowSeabed { seabed_m: s });
            }
        }
        let w = match &self.w_up {
            VerticalVelocity::Absent => None,
            VerticalVelocity::Present(w) => Some(w.as_slice()),
        };
        if z_m <= self.model_bottom_m {
            let (i, f) = level_bracket(&self.depth_m, z_m);
            let lerp = |v: &[f64]| v[i] + f * (v[(i + 1).min(v.len() - 1)] - v[i]);
            return Ok(DepthSample {
                u_east: lerp(&self.u_east),
                v_north: lerp(&self.v_north),
                w_up: w.map(lerp),
                status: DepthStatus::Resolved,
            });
        }
        let gap = DepthGap::BelowModelBottom { model_bottom_m: self.model_bottom_m };
        let last = self.depth_m.len() - 1;
        let factor = match (rule, seabed_m) {
            (BelowModelBottom::Refuse, _) => return Err(gap),
            (BelowModelBottom::HoldDeepestLevel, _) => 1.0,
            (BelowModelBottom::LinearToZeroAtSeabed, Some(s)) => (s - z_m) / (s - self.model_bottom_m),
            (BelowModelBottom::LinearToZeroAtSeabed, None) => return Err(gap),
        };
        Ok(DepthSample {
            u_east: factor * self.u_east[last],
            v_north: factor * self.v_north[last],
            w_up: w.map(|w| factor * w[last]),
            status: DepthStatus::Extrapolated {
                rule,
                model_bottom_m: self.model_bottom_m,
                seabed_m,
            },
        })
    }
}

/// Lower level index and fraction toward the next; clamps above the first and below the last.
fn level_bracket(depths: &[f64], z: f64) -> (usize, f64) {
    let n = depths.len();
    if n == 1 || z <= depths[0] {
        return (0, 0.0);
    }
    if z >= depths[n - 1] {
        return (n - 1, 0.0);
    }
    let i = depths.partition_point(|&d| d <= z) - 1;
    (i, (z - depths[i]) / (depths[i + 1] - depths[i]))
}

/// Source of water-column profiles; a gridded product implements this beside `VectorField`.
pub trait ProfileSource: Send + Sync {
    fn profile(&self, t: f64, p: LonLat) -> Result<Profile, FieldGap>;
    fn meta(&self) -> &FieldMeta;
}

/// Pressure (dbar) from depth (m) and latitude, Saunders (1981), J. Phys. Oceanogr. 11, 573-574.
/// Provisional: replaced by TEOS-10 `p_from_z` in deliverable 8.
pub fn pressure_dbar_saunders(z_m: f64, lat_deg: f64) -> f64 {
    let s = lat_deg.to_radians().sin();
    let c1 = (5.92 + 5.25 * s * s) * 1e-3;
    ((1.0 - c1) - ((1.0 - c1).powi(2) - 8.84e-6 * z_m).sqrt()) / 4.42e-6
}
