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

/// One depth level of a profile.
#[derive(Debug, Clone, Copy, PartialEq)]
pub struct Level {
    pub depth_m: f64,
    pub east_mps: f64,
    pub north_mps: f64,
    /// In-situ density (kg/m3).
    pub density_kg_m3: f64,
}

/// A water column at one place and time, surface first.
#[derive(Debug, Clone, PartialEq)]
pub struct Profile {
    pub levels: Vec<Level>,
    /// The ocean model's own bottom at this column (m): below it the current is extrapolated.
    pub model_bottom_m: f64,
    /// False: the product resolves no vertical velocity. Never read as zero.
    pub vertical_velocity_present: bool,
    /// Surface current and 10 m wind (m/s), for elements that float before sinking.
    pub surface_current_mps: [f64; 2],
    pub wind_mps: [f64; 2],
}

impl Profile {
    /// Current and density at depth z, linear between levels and held beyond the last level
    /// that is not below the model bottom. Returns (current, density, below_model_bottom).
    pub fn at(&self, z: f64) -> ([f64; 2], f64, bool) {
        let below = z > self.model_bottom_m;
        let zq = z.min(self.model_bottom_m);
        let l = &self.levels;
        let i = l.partition_point(|v| v.depth_m <= zq);
        let (a, b) = if i == 0 {
            (l[0], l[0])
        } else if i >= l.len() {
            (l[l.len() - 1], l[l.len() - 1])
        } else {
            (l[i - 1], l[i])
        };
        let f = if b.depth_m > a.depth_m { (zq - a.depth_m) / (b.depth_m - a.depth_m) } else { 0.0 };
        let lerp = |x: f64, y: f64| x + f * (y - x);
        // Density keeps its pressure trend below the model bottom (z, not zq).
        let rho = if below && l.len() > 1 {
            let (p, q) = (l[l.len() - 2], l[l.len() - 1]);
            q.density_kg_m3 + (z - q.depth_m) * (q.density_kg_m3 - p.density_kg_m3) / (q.depth_m - p.depth_m)
        } else {
            lerp(a.density_kg_m3, b.density_kg_m3)
        };
        ([lerp(a.east_mps, b.east_mps), lerp(a.north_mps, b.north_mps)], rho, below)
    }
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
        // Levels every 50 m to 8 km, each layer constant; a level exactly at the interface takes
        // the deep value so the step is resolved to within one level.
        let levels = (0..=160)
            .map(|k| {
                let z = 50.0 * k as f64;
                let c = if z < self.layer_depth_m { self.upper_current_mps } else { self.deep_current_mps };
                Level {
                    depth_m: z,
                    east_mps: c[0],
                    north_mps: c[1],
                    density_kg_m3: self.surface_density_kg_m3 + self.density_gradient_kg_m3_per_km * z / 1000.0,
                }
            })
            .collect();
        Some(Profile {
            levels,
            model_bottom_m: self.model_bottom_m,
            vertical_velocity_present: false,
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
