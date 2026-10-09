//! PROVISIONAL INPUTS - what settling still has to supply itself, on top of `mh370-ocean`.
//!
//! Since 9 October settling's currents, its float phase and its ocean error come from the shared
//! crate (`mh370-ocean`, merged at 77109b7 / 8d1160f): the `ProfileSource` trait and
//! `Profile::at_depth`, the batch integrator `integrate`, `OceanErrorModel`/`DiffusivityPrior`.
//! This file holds only the three things the shared crate does not yet serve, each to be deleted
//! when it does. Every number through them is provisional.
//!
//! 1. `LayeredColumn` - a closed-form two-layer water column implementing the shared
//!    `ProfileSource` trait. The shared crate's analytic `UniformColumn` is depth-uniform, and
//!    settling's closed-form tests and sensitivities need a current that changes with depth. No
//!    interpolation of data and no product choice: a gridded `ProfileSource` from the shared owner
//!    replaces it.
//! 2. `PlanarSeabed` - seabed depth as a plane. Bathymetry is the shared owner's deliverable 7
//!    (AusSeabed 150 m / GEBCO_2026 with per-cell provenance), not started.
//! 3. `DensityStub` - in-situ density linear in depth. In-situ density is the shared owner's
//!    TEOS-10 layer, deliverable 8, not started. It moves a terminal speed by about 1.5% by 6 km.

use ocean::field::{Component, FieldGap, FieldMeta};
use ocean::profile::{pressure_dbar_saunders, Profile, ProfileSource, Salinity, Temperature, VerticalVelocity};
use ocean::products::{Contents, TimeAxis};
use ocean::LonLat;
use serde::Deserialize;

/// A horizontally uniform column: `upper` above `layer_depth_m`, `deep` below, on levels every
/// `level_spacing_m` from the surface to the model bottom. A level exactly at the interface takes
/// the deep value, so linear interpolation smears the step over one level spacing above it.
pub struct LayeredColumn {
    pub upper_mps: [f64; 2],
    pub deep_mps: [f64; 2],
    pub layer_depth_m: f64,
    pub level_spacing_m: f64,
    pub model_bottom_m: f64,
    meta: FieldMeta,
}

impl LayeredColumn {
    pub fn new(upper_mps: [f64; 2], deep_mps: [f64; 2], layer_depth_m: f64, level_spacing_m: f64, model_bottom_m: f64) -> Self {
        let meta = FieldMeta {
            product: "analytic:settling-layered-column".into(),
            component: Component::Current,
            contents: Contents::analytic(),
            time_axis: TimeAxis::Steady,
            description: format!("PROVISIONAL two-layer column {upper_mps:?} above {layer_depth_m} m, {deep_mps:?} below"),
        };
        LayeredColumn { upper_mps, deep_mps, layer_depth_m, level_spacing_m, model_bottom_m, meta }
    }
}

impl ProfileSource for LayeredColumn {
    fn profile(&self, _t: f64, p: LonLat) -> Result<Profile, FieldGap> {
        let n = (self.model_bottom_m / self.level_spacing_m).floor() as usize;
        let mut depth_m: Vec<f64> = (0..=n).map(|k| k as f64 * self.level_spacing_m).collect();
        if *depth_m.last().unwrap() < self.model_bottom_m {
            depth_m.push(self.model_bottom_m);
        }
        let layer = |z: f64| if z < self.layer_depth_m { self.upper_mps } else { self.deep_mps };
        let k = depth_m.len();
        Ok(Profile {
            u_east: depth_m.iter().map(|&z| layer(z)[0]).collect(),
            v_north: depth_m.iter().map(|&z| layer(z)[1]).collect(),
            w_up: VerticalVelocity::Absent,
            temperature: Temperature::Potential(vec![2.0; k]),
            salinity: Salinity::Practical(vec![34.7; k]),
            pressure_dbar: depth_m.iter().map(|&z| pressure_dbar_saunders(z, p[1])).collect(),
            depth_m,
            model_bottom_m: self.model_bottom_m,
            time_axis: TimeAxis::Steady,
        })
    }
    fn meta(&self) -> &FieldMeta {
        &self.meta
    }
}

/// Seabed depth (m, positive down) as a plane through `depth_m` at the reference point, deepening
/// at `slope_deg` toward `slope_azimuth_deg` (clockwise from north). Local offsets use the shared
/// crate's sphere, the same geometry as its integrator.
#[derive(Debug, Clone, Copy, PartialEq, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct PlanarSeabed {
    pub reference: LonLat,
    pub depth_m: f64,
    #[serde(default)]
    pub slope_deg: f64,
    #[serde(default)]
    pub slope_azimuth_deg: f64,
}

impl PlanarSeabed {
    pub fn depth_at(&self, p: LonLat) -> Option<f64> {
        let [e, n] = offset_m(self.reference, p);
        let az = self.slope_azimuth_deg.to_radians();
        let d = self.depth_m + (e * az.sin() + n * az.cos()) * self.slope_deg.to_radians().tan();
        (d > 0.0).then_some(d)
    }
}

/// In-situ density (kg/m3) linear in depth.
#[derive(Debug, Clone, Copy, PartialEq, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct DensityStub {
    pub surface_kg_m3: f64,
    pub gradient_kg_m3_per_km: f64,
}

impl DensityStub {
    pub fn at(&self, z_m: f64) -> f64 {
        self.surface_kg_m3 + self.gradient_kg_m3_per_km * z_m / 1000.0
    }
}

/// East/north offset (m) of `p` from `origin`: the exact inverse of `ocean::displace`.
pub fn offset_m(origin: LonLat, p: LonLat) -> [f64; 2] {
    let r = ocean::EARTH_RADIUS_M;
    let cos_mid = ((origin[1] + p[1]) * 0.5).to_radians().cos().max(1e-8);
    let mut dlon = p[0] - origin[0];
    dlon -= 360.0 * (dlon / 360.0).round();
    [r * cos_mid * dlon.to_radians(), r * (p[1] - origin[1]).to_radians()]
}

/// The provisional table in run.toml.
#[derive(Debug, Clone, PartialEq, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct ProvisionalSpec {
    pub label: String,
    pub surface_current_mps: [f64; 2],
    pub wind_mps: [f64; 2],
    #[serde(default)]
    pub stokes_mps: [f64; 2],
    pub upper_current_mps: [f64; 2],
    pub deep_current_mps: [f64; 2],
    pub layer_depth_m: f64,
    pub level_spacing_m: f64,
    pub model_bottom_m: f64,
    pub seabed: PlanarSeabed,
    pub density: DensityStub,
}

impl ProvisionalSpec {
    pub fn check(&self) -> Result<(), String> {
        let ok = self.seabed.depth_m > 0.0
            && self.seabed.slope_deg.abs() < 45.0
            && self.layer_depth_m >= 0.0
            && self.level_spacing_m > 0.0
            && self.model_bottom_m > 0.0
            && self.density.surface_kg_m3 > 1000.0;
        if ok {
            Ok(())
        } else {
            Err("settling provisional: depths, spacing and density must be positive, slope under 45 deg".into())
        }
    }
}
