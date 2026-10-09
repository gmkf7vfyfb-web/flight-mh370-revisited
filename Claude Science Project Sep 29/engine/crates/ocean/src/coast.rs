//! Coastlines and beaching. A [`Coastline`] answers two questions: is a point land, and where does
//! a step from sea first cross onto land, on which segment. Segment IDs are what drift maps its
//! evidence table onto. The real coastline (GSHHG full resolution, keeping Reunion, Mauritius and
//! Rodrigues) is [`crate::gshhg::PolygonCoast`]; the analytic straight coast stays for tests.
//!
//! Chainage (drift's request, 9 October): every hit also carries `chainage_m`, the arc length along
//! its coast *line* from that line's own origin, continuous across segment boundaries. Each island
//! is its own line with its own origin, so finds on two islands are never "close along the coast".
//! [`Coastline::segments`] publishes every segment's edges in the same chainage.

use crate::{LonLat, EARTH_RADIUS_M};
use serde::Serialize;

pub type SegmentId = u32;
/// One continuous chainage line: a mainland stretch or one island.
pub type LineId = u32;

#[derive(Clone, Copy, Debug, PartialEq, Serialize)]
pub struct CoastHit {
    pub segment: SegmentId,
    pub line: LineId,
    /// Arc length along `line` from its origin, m.
    pub chainage_m: f64,
    /// Fraction of the step at which the crossing occurs, 0..=1.
    pub fraction: f64,
    pub point: LonLat,
    /// Distance moved onto the shoreline, m: 0 for a crossing, positive for a land-mask stranding
    /// snapped to the nearest shore ([`Coastline::snap`]).
    pub snapped_m: f64,
}

/// A segment's extent in its line's chainage.
#[derive(Clone, Copy, Debug, PartialEq, Serialize)]
pub struct SegmentEdges {
    pub segment: SegmentId,
    pub line: LineId,
    pub start_m: f64,
    pub end_m: f64,
}

pub trait Coastline: Send + Sync {
    fn is_land(&self, p: LonLat) -> bool;
    /// First crossing from sea onto land along the straight (lon, lat) segment `from -> to`.
    fn first_crossing(&self, from: LonLat, to: LonLat) -> Option<CoastHit>;
    fn label(&self) -> String;
    /// Every segment's edges in chainage; empty for open ocean.
    fn segments(&self) -> Vec<SegmentEdges>;
    /// The nearest shoreline point to a sea position at which a product's land mask stranded a
    /// particle, if the coast converts such strandings to beachings; `None` keeps the stranding a
    /// `FieldGap::Land` event.
    fn snap(&self, _p: LonLat) -> Option<CoastHit> {
        None
    }
    /// Names of named segments (IDs without a name are unnamed pieces).
    fn segment_names(&self) -> Vec<(SegmentId, String)> {
        vec![]
    }
}

/// Open ocean everywhere.
pub struct NoCoast;

impl Coastline for NoCoast {
    fn is_land(&self, _p: LonLat) -> bool {
        false
    }
    fn first_crossing(&self, _from: LonLat, _to: LonLat) -> Option<CoastHit> {
        None
    }
    fn label(&self) -> String {
        "none".into()
    }
    fn segments(&self) -> Vec<SegmentEdges> {
        vec![]
    }
}

/// The straight line through `a` and `b` in (lon, lat), land on one side. The span a..b is cut
/// into `segments` equal pieces numbered `first_id..first_id+segments`; beyond the ends the line
/// continues and takes the end segments' IDs. Chainage is measured from `a` along the line (negative
/// before `a`); the coast is one chainage line, `line`.
pub struct StraightCoast {
    pub a: LonLat,
    pub b: LonLat,
    pub segments: u32,
    pub first_id: SegmentId,
    /// Land to the left of a -> b (looking along it in lon/lat axes).
    pub land_left: bool,
    pub line: LineId,
}

impl StraightCoast {
    fn side(&self, p: LonLat) -> f64 {
        let (dx, dy) = (self.b[0] - self.a[0], self.b[1] - self.a[1]);
        let s = dx * (p[1] - self.a[1]) - dy * (p[0] - self.a[0]);
        if self.land_left { s } else { -s }
    }
    /// Line parameter of the foot of `p` (0 at `a`, 1 at `b`).
    fn param(&self, p: LonLat) -> f64 {
        let (dx, dy) = (self.b[0] - self.a[0], self.b[1] - self.a[1]);
        (dx * (p[0] - self.a[0]) + dy * (p[1] - self.a[1])) / (dx * dx + dy * dy)
    }
    pub fn segment_at(&self, p: LonLat) -> SegmentId {
        let k = (self.param(p) * self.segments as f64).floor().clamp(0.0, (self.segments - 1) as f64);
        self.first_id + k as SegmentId
    }
    /// Arc length on the sphere along the (lon, lat)-straight line from `a` to parameter `s`
    /// (Simpson's rule, 64 intervals; exact for meridians and parallels).
    pub fn chainage_at_param(&self, s: f64) -> f64 {
        let (dl, dp) = ((self.b[0] - self.a[0]).to_radians(), (self.b[1] - self.a[1]).to_radians());
        let speed = |u: f64| {
            let phi = (self.a[1] + u * (self.b[1] - self.a[1])).to_radians();
            EARTH_RADIUS_M * ((phi.cos() * dl).powi(2) + dp * dp).sqrt()
        };
        let n = 64;
        let h = s / n as f64;
        let mut acc = speed(0.0) + speed(s);
        for i in 1..n {
            acc += if i % 2 == 1 { 4.0 } else { 2.0 } * speed(i as f64 * h);
        }
        acc * h / 3.0
    }
}

impl Coastline for StraightCoast {
    fn is_land(&self, p: LonLat) -> bool {
        self.side(p) > 0.0
    }
    fn first_crossing(&self, from: LonLat, to: LonLat) -> Option<CoastHit> {
        let (d0, d1) = (self.side(from), self.side(to));
        if d0 > 0.0 || d1 <= 0.0 {
            return None;
        }
        let f = d0 / (d0 - d1);
        let point = [from[0] + f * (to[0] - from[0]), from[1] + f * (to[1] - from[1])];
        Some(CoastHit {
            segment: self.segment_at(point),
            line: self.line,
            chainage_m: self.chainage_at_param(self.param(point)),
            fraction: f,
            point,
            snapped_m: 0.0,
        })
    }
    fn label(&self) -> String {
        format!(
            "straight coast ({}, {}) -> ({}, {}), {} segments from id {}",
            self.a[0], self.a[1], self.b[0], self.b[1], self.segments, self.first_id
        )
    }
    /// Interior edges at equal parameter steps; the end segments extend without limit.
    fn segments(&self) -> Vec<SegmentEdges> {
        let n = self.segments;
        (0..n)
            .map(|k| SegmentEdges {
                segment: self.first_id + k,
                line: self.line,
                start_m: if k == 0 { f64::NEG_INFINITY } else { self.chainage_at_param(k as f64 / n as f64) },
                end_m: if k == n - 1 { f64::INFINITY } else { self.chainage_at_param((k + 1) as f64 / n as f64) },
            })
            .collect()
    }
}
