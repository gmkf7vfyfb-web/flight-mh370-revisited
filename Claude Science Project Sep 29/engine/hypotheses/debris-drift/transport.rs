//! The drift side of the shared transport boundary. Types mirror `mh370_ocean` on
//! `core/ocean-transport` at 311e481 (coordination/OCEAN_TRANSPORT.md, 2026-10-08 entry "the API
//! exists"): positions `[lon, lat]`, unix seconds, a persistent `ObjectResponse` per particle, one
//! ocean realisation per run from `seed`, and a terminal fate per particle. Until core requests O1/O2
//! let hypotheses depend on `mh370-ocean`, the only implementation is the provisional analytic stub;
//! the swap is one `impl Transport` and deleting the stub.
//!
//! One field drift needs that the shared API does not yet return: `chainage_km`, the along-coast
//! arc length of the beaching point on the segmented coastline, continuous across segment
//! boundaries. The recovery layer's locality kernel and its normaliser Q(x) are defined along the
//! coast (recovery.rs); a segment ID alone cannot place a find within a segment. Requested in
//! coordination/OCEAN_TRANSPORT.md.

use super::provisional_analytic_ocean::{AnalyticOcean, LocalPlane, Response};
use super::rng::Rng;

pub type LonLat = [f64; 2];

#[derive(Debug, Clone, Copy, PartialEq)]
pub struct ObjectResponse {
    pub a_stokes: f64,
    pub c_wind: f64,
    /// Degrees, positive clockwise from downwind; 0 in the first pass.
    pub leeway_angle_deg: f64,
}

#[derive(Debug, Clone, Copy, PartialEq)]
pub struct Particle {
    pub release: LonLat,
    pub release_time: f64,
    pub response: ObjectResponse,
}

/// Terminal fate. Every fate other than `Beached` and `Afloat` is MODEL ERROR, not a non-arrival:
/// the recovery layer counts such particles in the release total and reports their fraction as a
/// quality flag rather than silently treating them as lost at sea (review item 4, rule 4).
#[derive(Debug, Clone, Copy, PartialEq)]
pub enum Fate {
    Afloat,
    Beached { t: f64, at: LonLat, segment: u32, chainage_km: f64 },
    // Constructed by the shared transport; the analytic stub has no domain edge and no field gaps.
    #[allow(dead_code)]
    LeftDomain,
    #[allow(dead_code)]
    FieldGap,
    NonFinite,
    ReleasedOnLand,
}

pub trait Transport {
    /// The `ocean-model` label of this transport, for provenance and the shared alternative.
    fn label(&self) -> &str;
    /// Integrate every particle to `end_time` (unix s) through one ocean realisation set by `seed`.
    fn integrate(&self, particles: &[Particle], seed: u64, end_time: f64) -> Vec<Fate>;
}

/// The provisional analytic ocean behind the `Transport` boundary.
pub struct StubTransport {
    pub ocean: AnalyticOcean,
    pub plane: LocalPlane,
    pub step_s: f64,
    /// Segment length along the stub coast (stub-only segmentation), km.
    pub segment_km: f64,
    pub label: String,
}

impl Transport for StubTransport {
    fn label(&self) -> &str {
        &self.label
    }
    fn integrate(&self, particles: &[Particle], seed: u64, end_time: f64) -> Vec<Fate> {
        particles
            .iter()
            .enumerate()
            .map(|(i, p)| {
                let (x, y) = self.plane.to_xy(p.release[1], p.release[0]);
                if let Some(c) = &self.ocean.coast {
                    if c.signed(x, y) >= 0.0 {
                        return Fate::ReleasedOnLand;
                    }
                }
                let steps = ((end_time - p.release_time) / self.step_s).ceil().max(0.0) as usize;
                let mut rng = Rng::derive(&[seed, i as u64]);
                let r = Response { a_stokes: p.response.a_stokes, c_wind: p.response.c_wind };
                let f = self.ocean.integrate(x, y, &r, self.step_s, steps, &mut rng);
                if !f.beached {
                    return if f.x_km.is_finite() && f.y_km.is_finite() { Fate::Afloat } else { Fate::NonFinite };
                }
                let at = self.plane.to_lonlat(f.x_km, f.y_km);
                let segment = ((f.s_km / self.segment_km).floor() + 1.0e6) as u32;
                Fate::Beached { t: p.release_time + f.t_days * 86_400.0, at, segment, chainage_km: f.s_km }
            })
            .collect()
    }
}
