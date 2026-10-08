//! PROVISIONAL OCEAN STUB — NOT THE PROJECT'S OCEAN MODEL.
//!
//! Every number that passes through this file is provisional. It exists only so that settling
//! can be built and tested before `crates/ocean` (the shared ocean-transport owner, decision 4 of
//! ARCHITECTURE.md) delivers its API, and it is to be DELETED when that API lands. It does no
//! field interpolation, reads no reanalysis, and chooses no product (inbox ruling of 8 Oct 2026):
//! the stub is a closed-form, horizontally uniform, two-layer ocean over a planar seabed.
//!
//! What the stub ASSUMES, stated so the shared owner can reject it rather than inherit it (the
//! same list is in the interface request in coordination/OCEAN_TRANSPORT.md):
//! 1. The query is a PROFILE at (lat, lon, t): current, density and the model's own bottom on
//!    depth levels from the surface down — not a scattered point lookup.
//! 2. Currents are geographic east/north in m/s. Depth is geometric, positive down, in metres.
//! 3. Resolved vertical velocity is reported as ABSENT (a flag), never as zero.
//! 4. The model's bottom can be shallower than the seabed; below it the caller applies an
//!    explicit, variable extrapolation factor and records how far it extrapolated.
//! 5. Error is a per-EVENT realisation (one draw shared by every fragment of one impact), in
//!    three depth bands plus a near-bottom band for unresolved motion.
//! 6. The profile is taken at the release point and held for the whole descent (a column
//!    assumption); with the shared API it would be re-queried as the element moves.
//! 7. Time does not vary within the stub. Daily-mean products would make that nearly true for
//!    a 15-70 min descent and false for the slow-sinker tail.

use serde::Deserialize;

/// Mirrors `mh370_ocean::profile::VerticalVelocity` on `core/ocean-transport` (311e481).
/// `Present` is never built by the stub; it exists so the call shape matches the shared crate.
#[allow(dead_code)]
#[derive(Debug, Clone, PartialEq)]
pub enum VerticalVelocity {
    /// The product has no resolved vertical velocity. Not zero.
    Absent,
    /// m/s, positive upward, one per level.
    Present(Vec<f64>),
}

/// Mirrors `mh370_ocean::profile::BelowModelBottom`: the caller chooses and varies it, and the
/// choice is reported. No variant fills with zero by default.
#[derive(Debug, Clone, Copy, PartialEq)]
pub enum BelowModelBottom {
    Refuse,
    /// Hold the deepest model level's velocity down to the seabed.
    HoldDeepestLevel,
    /// Deepest level's velocity at the model bottom, decreasing linearly to zero at the seabed.
    LinearToZeroAtSeabed,
}

impl BelowModelBottom {
    pub fn parse(name: &str) -> Result<Self, String> {
        match name {
            "refuse" => Ok(Self::Refuse),
            "hold-deepest-level" => Ok(Self::HoldDeepestLevel),
            "linear-to-zero-at-seabed" => Ok(Self::LinearToZeroAtSeabed),
            other => Err(format!("below_model_bottom: unknown rule `{other}`; known: refuse, hold-deepest-level, linear-to-zero-at-seabed")),
        }
    }
}

/// Mirrors `mh370_ocean::profile::DepthSample` (status reduced to a flag).
#[derive(Debug, Clone, Copy, PartialEq)]
pub struct DepthSample {
    pub u_east: f64,
    pub v_north: f64,
    /// `None` when the product has no vertical velocity.
    pub w_up: Option<f64>,
    /// True when the value was extrapolated below the model bottom by the caller's rule.
    pub extrapolated: bool,
}

/// Mirrors `mh370_ocean::profile::DepthGap`.
#[derive(Debug, Clone, Copy, PartialEq)]
pub enum DepthGap {
    AboveSurface,
    BelowSeabed { seabed_m: f64 },
    BelowModelBottom { model_bottom_m: f64 },
}

/// One water column, surface first. Field names follow `mh370_ocean::profile::Profile` so the
/// swap is a field change. Two STUB-ONLY extras, both to be removed at the swap:
/// `density_kg_m3` (the shared profile carries T, S and p; in-situ density will come from its
/// TEOS-10 layer, deliverable 8), and the surface current and wind (the shared crate serves these
/// through its fields and integrator, not through a profile).
#[derive(Debug, Clone, PartialEq)]
pub struct Profile {
    pub depth_m: Vec<f64>,
    pub u_east: Vec<f64>,
    pub v_north: Vec<f64>,
    pub w_up: VerticalVelocity,
    pub model_bottom_m: f64,
    pub density_kg_m3: Vec<f64>,
    pub surface_current_mps: [f64; 2],
    pub wind_mps: [f64; 2],
}

impl Profile {
    /// Same semantics as the shared `Profile::at_depth`: linear between levels, nearest level held
    /// above the first and between the deepest level and the model bottom; below the model bottom
    /// the caller's rule applies, or the query is refused. (A second copy of that function, which
    /// is acceptable only because this file is deleted at the swap.)
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
            let (i, f) = bracket(&self.depth_m, z_m);
            let lerp = |v: &[f64]| v[i] + f * (v[(i + 1).min(v.len() - 1)] - v[i]);
            return Ok(DepthSample { u_east: lerp(&self.u_east), v_north: lerp(&self.v_north), w_up: w.map(lerp), extrapolated: false });
        }
        let gap = DepthGap::BelowModelBottom { model_bottom_m: self.model_bottom_m };
        // The deepest level at or above the model bottom.
        let last = self.depth_m.partition_point(|&d| d <= self.model_bottom_m).max(1) - 1;
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
            extrapolated: true,
        })
    }

    /// STUB-ONLY: in-situ density at depth, linear between levels and continued on the deepest
    /// pair's gradient below the last level.
    pub fn density_at(&self, z_m: f64) -> f64 {
        let (d, r) = (&self.depth_m, &self.density_kg_m3);
        let n = d.len();
        if n > 1 && z_m > d[n - 1] {
            return r[n - 1] + (z_m - d[n - 1]) * (r[n - 1] - r[n - 2]) / (d[n - 1] - d[n - 2]);
        }
        let (i, f) = bracket(d, z_m);
        r[i] + f * (r[(i + 1).min(n - 1)] - r[i])
    }
}

/// Lower level index and fraction toward the next; clamps above the first and below the last.
fn bracket(depths: &[f64], z: f64) -> (usize, f64) {
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

/// The declared, variable model of what the product does not resolve: one realisation per
/// impact event (rule 10), drawn by the caller from these standard deviations (m/s, per
/// east/north component).
#[derive(Debug, Clone, Copy, PartialEq, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct ErrorModel {
    pub surface_mps: f64,
    pub upper_mps: f64,
    pub upper_depth_m: f64,
    pub deep_mps: f64,
    /// Unresolved near-bottom motion (bottom boundary layer, topographic steering, internal
    /// tides), applied within `near_bottom_m` of the seabed, on top of the deep error.
    pub near_bottom_mps: f64,
    pub near_bottom_m: f64,
}

/// What settling needs from an ocean. Implemented here by the stub only; the shared crate's
/// API replaces this trait.
pub trait ProvisionalOcean: Send + Sync {
    fn profile(&self, latitude_deg: f64, longitude_deg: f64, unix_s: f64) -> Option<Profile>;
    /// Seabed depth (m, positive down); None on land or outside the grid.
    fn seabed_depth_m(&self, latitude_deg: f64, longitude_deg: f64) -> Option<f64>;
    fn error_model(&self) -> ErrorModel;
    /// A label carried into every output so a result names the ocean it came from.
    fn label(&self) -> &str;
}

/// Closed-form stub: two-layer current over a planar seabed. All provisional.
#[derive(Debug, Clone, PartialEq, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct AnalyticStub {
    pub label: String,
    /// Seabed: depth at the reference point, and a uniform slope (deg).
    pub reference_latitude_deg: f64,
    pub reference_longitude_deg: f64,
    pub seabed_depth_m: f64,
    #[serde(default)]
    pub seabed_slope_deg: f64,
    /// Direction (deg clockwise from north) in which the seabed DEEPENS.
    #[serde(default)]
    pub seabed_slope_azimuth_deg: f64,
    pub surface_current_mps: [f64; 2],
    pub wind_mps: [f64; 2],
    /// Current above `layer_depth_m`, and below it (m/s, east/north).
    pub upper_current_mps: [f64; 2],
    pub deep_current_mps: [f64; 2],
    pub layer_depth_m: f64,
    /// The stub ocean model's own bottom (m), to exercise the deeper-than-model-bottom flag.
    pub model_bottom_m: f64,
    /// Surface density and its increase per km of depth (kg/m3).
    pub surface_density_kg_m3: f64,
    pub density_gradient_kg_m3_per_km: f64,
    pub error: ErrorModel,
}

impl AnalyticStub {
    pub fn check(&self) -> Result<(), String> {
        let e = self.error;
        let ok = self.seabed_depth_m > 0.0
            && self.layer_depth_m >= 0.0
            && self.model_bottom_m > 0.0
            && self.surface_density_kg_m3 > 1000.0
            && [e.surface_mps, e.upper_mps, e.upper_depth_m, e.deep_mps, e.near_bottom_mps, e.near_bottom_m].iter().all(|x| *x >= 0.0)
            && self.seabed_slope_deg.abs() < 45.0;
        if ok {
            Ok(())
        } else {
            Err("provisional_ocean_stub: depths and densities must be positive, error sds non-negative, slope under 45 deg".into())
        }
    }

    /// Local east/north (m) of a point from the reference.
    fn local(&self, latitude_deg: f64, longitude_deg: f64) -> [f64; 2] {
        let (m, n) = geo::radii_of_curvature_km(self.reference_latitude_deg);
        let dlon = geo::wrap_longitude(longitude_deg - self.reference_longitude_deg);
        [
            1000.0 * n * self.reference_latitude_deg.to_radians().cos() * dlon.to_radians(),
            1000.0 * m * (latitude_deg - self.reference_latitude_deg).to_radians(),
        ]
    }
}

impl ProvisionalOcean for AnalyticStub {
    fn profile(&self, _latitude_deg: f64, _longitude_deg: f64, _unix_s: f64) -> Option<Profile> {
        // Levels every 50 m to 8 km; a level exactly at the interface takes the deep value, so
        // with linear interpolation the interface is smeared over the 50 m above it.
        let depth_m: Vec<f64> = (0..=160).map(|k| 50.0 * k as f64).collect();
        let layer = |z: f64| if z < self.layer_depth_m { self.upper_current_mps } else { self.deep_current_mps };
        Some(Profile {
            u_east: depth_m.iter().map(|&z| layer(z)[0]).collect(),
            v_north: depth_m.iter().map(|&z| layer(z)[1]).collect(),
            density_kg_m3: depth_m.iter().map(|&z| self.surface_density_kg_m3 + self.density_gradient_kg_m3_per_km * z / 1000.0).collect(),
            depth_m,
            w_up: VerticalVelocity::Absent,
            model_bottom_m: self.model_bottom_m,
            surface_current_mps: self.surface_current_mps,
            wind_mps: self.wind_mps,
        })
    }

    fn seabed_depth_m(&self, latitude_deg: f64, longitude_deg: f64) -> Option<f64> {
        let [e, n] = self.local(latitude_deg, longitude_deg);
        let az = self.seabed_slope_azimuth_deg.to_radians();
        let along = e * az.sin() + n * az.cos();
        let depth = self.seabed_depth_m + along * self.seabed_slope_deg.to_radians().tan();
        (depth > 0.0).then_some(depth)
    }

    fn error_model(&self) -> ErrorModel {
        self.error
    }

    fn label(&self) -> &str {
        &self.label
    }
}
