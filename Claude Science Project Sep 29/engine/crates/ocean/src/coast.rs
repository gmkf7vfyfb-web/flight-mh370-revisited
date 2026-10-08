//! Coastlines and beaching. A [`Coastline`] answers two questions: is a point land, and where does
//! a step from sea first cross onto land, on which segment. Segment IDs are what drift maps its
//! evidence table onto. The real coastline (keeping Reunion, Mauritius and Rodrigues) implements
//! the same trait in deliverable 6; tonight there is the analytic straight coast.

use crate::LonLat;
use serde::Serialize;

pub type SegmentId = u32;

#[derive(Clone, Copy, Debug, PartialEq, Serialize)]
pub struct CoastHit {
    pub segment: SegmentId,
    /// Fraction of the step at which the crossing occurs, 0..=1.
    pub fraction: f64,
    pub point: LonLat,
}

pub trait Coastline: Send + Sync {
    fn is_land(&self, p: LonLat) -> bool;
    /// First crossing from sea onto land along the straight (lon, lat) segment `from -> to`.
    fn first_crossing(&self, from: LonLat, to: LonLat) -> Option<CoastHit>;
    fn label(&self) -> String;
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
}

/// The straight line through `a` and `b` in (lon, lat), land on one side. The span a..b is cut
/// into `segments` equal pieces numbered `first_id..first_id+segments`; beyond the ends the line
/// continues and takes the end segments' IDs.
pub struct StraightCoast {
    pub a: LonLat,
    pub b: LonLat,
    pub segments: u32,
    pub first_id: SegmentId,
    /// Land to the left of a -> b (looking along it in lon/lat axes).
    pub land_left: bool,
}

impl StraightCoast {
    fn side(&self, p: LonLat) -> f64 {
        let (dx, dy) = (self.b[0] - self.a[0], self.b[1] - self.a[1]);
        let s = dx * (p[1] - self.a[1]) - dy * (p[0] - self.a[0]);
        if self.land_left { s } else { -s }
    }
    pub fn segment_at(&self, p: LonLat) -> SegmentId {
        let (dx, dy) = (self.b[0] - self.a[0], self.b[1] - self.a[1]);
        let s = (dx * (p[0] - self.a[0]) + dy * (p[1] - self.a[1])) / (dx * dx + dy * dy);
        let k = (s * self.segments as f64).floor().clamp(0.0, (self.segments - 1) as f64);
        self.first_id + k as SegmentId
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
        Some(CoastHit { segment: self.segment_at(point), fraction: f, point })
    }
    fn label(&self) -> String {
        format!(
            "straight coast ({}, {}) -> ({}, {}), {} segments from id {}",
            self.a[0], self.a[1], self.b[0], self.b[1], self.segments, self.first_id
        )
    }
}
