//! Detection segments: the coast stretches over which identification probability is modelled
//! (the S1-S6 of results/debris-drift-find-episodes.md). Until the shared transport's real
//! coastline and segmentation exist (ocean transport deliverable 6), a segment is a set of
//! lon/lat boxes, declared in run.toml, that a beaching or stranding point is located in.
//! PROVISIONAL: the boxes are this module's observation model, not the transport's coastline.

use serde::Deserialize;

#[derive(Debug, Clone, Deserialize, PartialEq)]
#[serde(deny_unknown_fields)]
pub struct Segment {
    pub name: String,
    /// [lon_min, lon_max, lat_min, lat_max] boxes.
    pub boxes: Vec<[f64; 4]>,
}

#[derive(Debug, Clone, PartialEq)]
pub struct SegmentMap {
    pub segments: Vec<Segment>,
}

impl SegmentMap {
    pub fn new(segments: Vec<Segment>) -> Result<Self, String> {
        for s in &segments {
            if s.boxes.is_empty() || s.boxes.iter().any(|b| !(b[0] < b[1] && b[2] < b[3])) {
                return Err(format!("segment `{}`: boxes must be [lon_min, lon_max, lat_min, lat_max] with min < max", s.name));
            }
        }
        Ok(SegmentMap { segments })
    }
    pub fn locate(&self, p: [f64; 2]) -> Option<usize> {
        self.segments.iter().position(|s| s.boxes.iter().any(|b| p[0] >= b[0] && p[0] <= b[1] && p[1] >= b[2] && p[1] <= b[3]))
    }
    pub fn len(&self) -> usize {
        self.segments.len()
    }
}
