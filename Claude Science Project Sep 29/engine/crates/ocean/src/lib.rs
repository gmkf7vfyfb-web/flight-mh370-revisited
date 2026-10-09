//! Shared ocean transport for the MH370 reconstruction (ARCHITECTURE decision 4).
//!
//! One crate owns the project's ocean so that no consumer's assumptions become the ocean model by
//! default. It returns no likelihood. Consumers: ocean drift and Pleiades (the batch forward
//! integrator, [`integrate::integrate`]), ocean settling (the profile query,
//! [`profile::ProfileSource`]); hydroacoustics and searched areas will consume bathymetry here
//! later.
//!
//! Binding rules from the brief (`threads/master-prompts/ocean-transport.md` section 3), and where
//! each is made structural:
//! 1. Velocity components are never pre-summed: [`integrate::Forcing`] takes current, Stokes and
//!    10 m wind as separate fields, and `v = u_current + a_stokes*u_stokes + c_wind*R(wind_angle)*U10
//!    + leeway_speed*R(leeway_angle)*U10/|U10| + ocean_error + diffusion` (separate angles, ruling D-f) is formed inside the integrator with a persistent per-particle
//!    [`integrate::ObjectResponse`].
//! 2. Every field declares what its "current" already contains ([`products::Contents`]); the
//!    integrator refuses a composition that counts Stokes drift twice.
//! 3. Diffusion is a declared, variable model ([`stochastic::Diffusion`]), applied per step; the
//!    diffusivity K is an eta component with a declared prior ([`stochastic::DiffusivityPrior`]).
//! 4. Ocean error is one coherent realisation per run ([`stochastic::OceanErrorRealisation`]),
//!    shared by every particle; diffusion is the only per-particle randomness.
//! 5. Land is renormalised away, never filled with zero ([`field::GridField`]).
//! 7. The product is a run argument; the alternative's name is [`OCEAN_MODEL_ALTERNATIVE`].
//!
//! Conventions. Positions are `[longitude_deg, latitude_deg]` (east-positive, -180..180). Times are
//! unix seconds UTC, as in the hook API. Velocities are geographic east/north in m/s. Depth is
//! geometric depth in metres, positive downward. The sphere has the IUGG mean radius; the
//! integrator is RK2 (midpoint) on the sphere, which is what the archive used and what drift's
//! pilot assumes.
//!
//! Departure from the archive (`transport_core.mjs`, withdrawn Pleiades share): the archive
//! clamped time outside a field's axis to its end values; here a query outside the time axis is a
//! flagged gap ([`field::FieldGap::OutsideTime`]), because a silently frozen field is a silent
//! model change.

pub mod analytic;
pub mod bathy;
pub mod coast;
pub mod field;
pub mod gridprofile;
pub mod gshhg;
pub mod integrate;
pub mod products;
pub mod profile;
pub mod stochastic;
pub mod soundspeed;
pub mod teos10;

pub use coast::{CoastHit, Coastline, LineId, NoCoast, SegmentEdges, SegmentId, StraightCoast};
pub use gridprofile::GridProfile;
pub use gshhg::{g1_segments, NamedSegment, PolygonCoast, PolygonCoastOptions};
pub use field::{Component, FieldGap, FieldMeta, GridField, LoadWindow, VectorField};
pub use integrate::{integrate, Domain, LEEWAY_CALM_WIND_MPS, Event, Fate, Forcing, ObjectResponse, Particle, Refloat, RunOutput, RunSpec, Snapshot};
pub use products::{Contents, Inclusion, TimeAxis};
pub use profile::{BelowModelBottom, BottomRelation, Profile, ProfileSource};
pub use stochastic::{Diffusion, DiffusivityPrior, OceanErrorModel, OceanErrorRealisation};

/// The name under which the ocean product is declared as a discrete alternative, shared by drift
/// and Pleiades and marginalised jointly by the composer (brief rule 7).
pub const OCEAN_MODEL_ALTERNATIVE: &str = "ocean-model";

/// IUGG mean Earth radius, m (as in the archive transport core).
pub const EARTH_RADIUS_M: f64 = 6_371_008.8;
pub const METRES_PER_NM: f64 = 1852.0;
pub const SECONDS_PER_DAY: f64 = 86_400.0;

/// `[longitude_deg, latitude_deg]`.
pub type LonLat = [f64; 2];

/// Move a position by a small east/north displacement in metres on the sphere. The longitude step
/// uses the cosine of the mean of the start and end latitudes.
pub fn displace(p: LonLat, east_m: f64, north_m: f64) -> LonLat {
    let lat1 = p[1] + (north_m / EARTH_RADIUS_M).to_degrees();
    let cos_mid = ((p[1] + lat1) * 0.5).to_radians().cos().max(1e-8);
    let lon1 = p[0] + (east_m / (EARTH_RADIUS_M * cos_mid)).to_degrees();
    [wrap_lon(lon1), lat1]
}

/// Great-circle (haversine) distance in metres.
pub fn distance_m(a: LonLat, b: LonLat) -> f64 {
    let (p1, p2) = (a[1].to_radians(), b[1].to_radians());
    let dp = p2 - p1;
    let dl = (b[0] - a[0]).to_radians();
    let h = (dp * 0.5).sin().powi(2) + p1.cos() * p2.cos() * (dl * 0.5).sin().powi(2);
    2.0 * EARTH_RADIUS_M * h.sqrt().min(1.0).asin()
}

pub fn wrap_lon(lon: f64) -> f64 {
    let x = (lon + 180.0).rem_euclid(360.0) - 180.0;
    if x == -180.0 && lon > 0.0 { 180.0 } else { x }
}

/// Unit position vector and local east/north unit vectors (Earth-centred frame).
pub(crate) fn enu_basis(p: LonLat) -> ([f64; 3], [f64; 3], [f64; 3]) {
    let (lam, phi) = (p[0].to_radians(), p[1].to_radians());
    let (sl, cl, sp, cp) = (lam.sin(), lam.cos(), phi.sin(), phi.cos());
    ([cp * cl, cp * sl, sp], [-sl, cl, 0.0], [-sp * cl, -sp * sl, cp])
}

pub(crate) fn dot(a: [f64; 3], b: [f64; 3]) -> f64 {
    a[0] * b[0] + a[1] * b[1] + a[2] * b[2]
}

pub(crate) fn cross(a: [f64; 3], b: [f64; 3]) -> [f64; 3] {
    [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]]
}
