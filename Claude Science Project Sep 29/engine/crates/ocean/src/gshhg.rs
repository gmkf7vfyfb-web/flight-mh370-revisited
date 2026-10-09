//! The real coastline: GSHHG (Wessel and Smith 1996), version 2.3.7, full resolution, level 1
//! (ocean/land boundary) polygons, read directly from the distributed big-endian binary
//! `gshhs_f.b`. Implements [`Coastline`] with segment IDs and chainage, so a beaching carries the
//! coast segment itself rather than a position in some product's land mask.
//!
//! Geometry. Every kept ring is indexed on a regular lon/lat cell grid over a declared box
//! (default 30 W - 140 E, 62 S - 12 N, 0.05 deg cells). Each cell is sea, land, or coastal (holds
//! at least one shoreline edge). Sea and land cells are classified once by a west-to-east parity
//! scan along every row's centre line, starting from sea at the box's west edge (open Atlantic at
//! every latitude in the default box). In a coastal cell, `is_land` counts crossings of a westward
//! ray to the nearest classified cell. A step's beaching point is its first intersection with a
//! shoreline edge, intersected in the lon/lat plane like [`crate::StraightCoast`]. Lakes (level 2
//! and above) are not subtracted: an ocean particle cannot reach one without crossing land first.
//!
//! Lines and chainage. Each GSHHG ring is one chainage line; its `LineId` is the GSHHG polygon id
//! (stable within version 2.3.7). Chainage is great-circle arc length along the ring's vertices.
//! The origin is a segment boundary, so no segment straddles it; the jump from the ring's length
//! back to zero happens only there.
//!
//! Segments. Named segments are given as lon/lat boxes by the caller (drift owns their
//! definitions; [`g1_segments`] reproduces drift's six G1 boxes). A shoreline edge belongs to the
//! first named segment one of whose boxes contains its midpoint. Every contiguous run of named
//! edges along a ring is one [`SegmentEdges`] entry, so a named segment may span several lines
//! (Mauritius and Rodrigues) or several runs of one line. Every other run is cut into pieces of
//! about `piece_m` (100 km default) numbered from `first_unnamed_id` (100) in file order.
//!
//! Land-mask stranding. A gridded product's land mask does not coincide with GSHHG; a particle
//! may meet a cell with no sea node offshore of the GSHHG shore. [`Coastline::snap`] returns the
//! nearest shoreline point within `snap_max_m` (25 km default, about two GLORYS12 cells and one
//! WAVERYS cell) and the integrator records that as a beaching with `snapped_m` the distance moved.
//! Beyond `snap_max_m` the stranding stays a `FieldGap::Land` event (model error).

use crate::coast::{CoastHit, Coastline, LineId, SegmentEdges, SegmentId};
use crate::{distance_m, wrap_lon, LonLat, EARTH_RADIUS_M};
use serde::{Deserialize, Serialize};
use std::path::Path;

/// A caller-defined named segment: every shoreline edge whose midpoint lies in one of `boxes`
/// (`[lon_min, lon_max, lat_min, lat_max]`, degrees).
#[derive(Clone, Debug, PartialEq, Serialize, Deserialize)]
pub struct NamedSegment {
    pub id: SegmentId,
    pub name: String,
    pub boxes: Vec<[f64; 4]>,
}

impl NamedSegment {
    fn contains(&self, p: LonLat) -> bool {
        self.boxes.iter().any(|b| p[0] >= b[0] && p[0] <= b[1] && p[1] >= b[2] && p[1] <= b[3])
    }
}

/// Drift's six G1 detection segments, IDs 1-6, with the boxes of
/// `hypotheses/debris-drift/pilot.toml` at `9a9b0cc` (drift's definitions, provisional there).
pub fn g1_segments() -> Vec<NamedSegment> {
    let s = |id, name: &str, boxes: Vec<[f64; 4]>| NamedSegment { id, name: name.into(), boxes };
    vec![
        s(1, "S1-reunion", vec![[55.1, 56.0, -21.5, -20.7]]),
        s(2, "S2-mauritius-rodrigues", vec![[57.2, 57.9, -20.7, -19.8], [63.2, 63.65, -19.9, -19.55]]),
        s(3, "S3-southern-mozambique", vec![[33.5, 36.0, -25.3, -21.3]]),
        s(4, "S4-south-africa-south-coast", vec![[20.0, 26.5, -34.9, -33.6]]),
        s(5, "S5-ne-madagascar", vec![[49.0, 50.8, -18.0, -15.4]]),
        s(6, "S6-pemba", vec![[39.3, 40.3, -5.6, -4.6]]),
    ]
}

/// One closed shoreline ring (land on the inside), vertices in order, without a repeated last
/// vertex.
#[derive(Clone, Debug)]
pub struct Ring {
    pub id: LineId,
    pub points: Vec<LonLat>,
}

#[derive(Clone, Debug, PartialEq, Serialize)]
pub struct PolygonCoastOptions {
    /// `[lon_min, lon_max, lat_min, lat_max]` of the index; outside it every point is sea and no
    /// crossing is found. Its west edge must be sea at every latitude.
    pub bbox: [f64; 4],
    pub cell_deg: f64,
    /// Target length of unnamed pieces, m.
    pub piece_m: f64,
    pub first_unnamed_id: SegmentId,
    /// Largest land-mask stranding distance converted to a beaching, m; 0 disables snapping.
    pub snap_max_m: f64,
}

impl Default for PolygonCoastOptions {
    fn default() -> Self {
        Self { bbox: [-30.0, 140.0, -62.0, 12.0], cell_deg: 0.05, piece_m: 100_000.0, first_unnamed_id: 100, snap_max_m: 25_000.0 }
    }
}

#[derive(Clone, Debug, Serialize)]
pub struct RingInfo {
    pub line: LineId,
    pub vertices: usize,
    pub length_m: f64,
    /// Index into the ring's own vertex list of the chainage origin.
    pub origin: usize,
}

const SEA: u8 = 0;
const LAND: u8 = 1;
const COASTAL: u8 = 2;
const UNNAMED: SegmentId = SegmentId::MAX;

pub struct PolygonCoast {
    pub opts: PolygonCoastOptions,
    pub named: Vec<NamedSegment>,
    source: String,
    verts: Vec<LonLat>,
    /// Ring index of each vertex (and of the edge that starts there).
    ring_of: Vec<u32>,
    ring_start: Vec<usize>,
    pub rings: Vec<RingInfo>,
    /// Chainage of each vertex on its line, in [0, length).
    chain: Vec<f64>,
    edge_len: Vec<f64>,
    nx: usize,
    ny: usize,
    state: Vec<u8>,
    cell_off: Vec<u32>,
    cell_edges: Vec<u32>,
    /// All segment runs, grouped by ring in ring order and sorted by start within a ring.
    segs: Vec<SegmentEdges>,
    ring_segs: Vec<(usize, usize)>,
}

impl PolygonCoast {
    /// Read level-1 rings of a GSHHG binary (`gshhs_f.b` for full resolution) that have a vertex
    /// inside `opts.bbox` (padded by one cell), and build the coast.
    pub fn from_gshhg(path: &Path, named: Vec<NamedSegment>, opts: PolygonCoastOptions) -> Result<Self, String> {
        let bytes = std::fs::read(path).map_err(|e| format!("{}: {e}", path.display()))?;
        let pad = opts.cell_deg;
        let b = opts.bbox;
        let inside = |p: LonLat| p[0] >= b[0] - pad && p[0] <= b[1] + pad && p[1] >= b[2] - pad && p[1] <= b[3] + pad;
        let int = |o: usize| i32::from_be_bytes([bytes[o], bytes[o + 1], bytes[o + 2], bytes[o + 3]]);
        let (mut o, mut rings, mut polygons) = (0usize, Vec::new(), 0usize);
        while o + 44 <= bytes.len() {
            let (id, n, flag) = (int(o), int(o + 4) as usize, int(o + 8));
            o += 44;
            if o + 8 * n > bytes.len() {
                return Err(format!("{}: truncated polygon {id}", path.display()));
            }
            polygons += 1;
            if flag & 255 == 1 {
                let mut pts: Vec<LonLat> =
                    (0..n).map(|k| [wrap_lon(int(o + 8 * k) as f64 * 1e-6), int(o + 8 * k + 4) as f64 * 1e-6]).collect();
                if pts.len() > 1 && pts[0] == pts[pts.len() - 1] {
                    pts.pop();
                }
                if pts.len() >= 3 && pts.iter().any(|&p| inside(p)) {
                    rings.push(Ring { id: id as LineId, points: pts });
                }
            }
            o += 8 * n;
        }
        let label = format!("GSHHG 2.3.7 {} ({} bytes, {polygons} polygons, {} level-1 rings kept)", path.display(), bytes.len(), rings.len());
        Ok(Self::from_rings(rings, named, opts, label))
    }

    pub fn from_rings(rings: Vec<Ring>, named: Vec<NamedSegment>, opts: PolygonCoastOptions, source: String) -> Self {
        let total: usize = rings.iter().map(|r| r.points.len()).sum();
        let mut c = PolygonCoast {
            nx: ((opts.bbox[1] - opts.bbox[0]) / opts.cell_deg).round() as usize,
            ny: ((opts.bbox[3] - opts.bbox[2]) / opts.cell_deg).round() as usize,
            opts,
            named,
            source,
            verts: Vec::with_capacity(total),
            ring_of: Vec::with_capacity(total),
            ring_start: Vec::with_capacity(rings.len()),
            rings: Vec::with_capacity(rings.len()),
            chain: vec![0.0; total],
            edge_len: Vec::with_capacity(total),
            state: vec![],
            cell_off: vec![],
            cell_edges: vec![],
            segs: vec![],
            ring_segs: vec![],
        };
        for (ri, r) in rings.iter().enumerate() {
            c.ring_start.push(c.verts.len());
            let n = r.points.len();
            for k in 0..n {
                c.verts.push(r.points[k]);
                c.ring_of.push(ri as u32);
                c.edge_len.push(distance_m(r.points[k], r.points[(k + 1) % n]));
            }
        }
        let mut next_id = c.opts.first_unnamed_id;
        for (ri, r) in rings.iter().enumerate() {
            let s0 = c.segs.len();
            let info = c.segment_ring(ri, r.id, &mut next_id);
            c.rings.push(info);
            c.ring_segs.push((s0, c.segs.len()));
        }
        c.build_index();
        c
    }

    fn next(&self, i: usize) -> usize {
        let r = self.ring_of[i] as usize;
        let (s, n) = (self.ring_start[r], self.ring_len(r));
        if i + 1 == s + n { s } else { i + 1 }
    }

    fn ring_len(&self, r: usize) -> usize {
        let end = if r + 1 < self.ring_start.len() { self.ring_start[r + 1] } else { self.verts.len() };
        end - self.ring_start[r]
    }

    fn edge(&self, i: usize) -> Option<(LonLat, LonLat)> {
        let (a, b) = (self.verts[i], self.verts[self.next(i)]);
        if (b[0] - a[0]).abs() > 180.0 { None } else { Some((a, b)) }
    }

    /// Chainage origin, chainage of every vertex, and the segment runs of ring `ri`.
    fn segment_ring(&mut self, ri: usize, line: LineId, next_id: &mut SegmentId) -> RingInfo {
        let (s, n) = (self.ring_start[ri], self.ring_len(ri));
        let label: Vec<SegmentId> = (0..n)
            .map(|k| {
                let (a, b) = (self.verts[s + k], self.verts[s + (k + 1) % n]);
                let m = [0.5 * (a[0] + b[0]), 0.5 * (a[1] + b[1])];
                self.named.iter().find(|g| g.contains(m)).map_or(UNNAMED, |g| g.id)
            })
            .collect();
        let origin = (0..n).find(|&k| label[k] != label[(k + n - 1) % n]).unwrap_or(0);
        let mut acc = 0.0;
        let mut runs: Vec<(SegmentId, f64, f64)> = Vec::new();
        for j in 0..n {
            let k = (origin + j) % n;
            self.chain[s + k] = acc;
            let len = self.edge_len[s + k];
            match runs.last_mut() {
                Some(r) if r.0 == label[k] => r.2 = acc + len,
                _ => runs.push((label[k], acc, acc + len)),
            }
            acc += len;
        }
        for (id, a, b) in runs {
            if id != UNNAMED {
                self.segs.push(SegmentEdges { segment: id, line, start_m: a, end_m: b });
            } else {
                let pieces = ((b - a) / self.opts.piece_m).round().max(1.0) as usize;
                for q in 0..pieces {
                    let (pa, pb) = (a + (b - a) * q as f64 / pieces as f64, a + (b - a) * (q + 1) as f64 / pieces as f64);
                    self.segs.push(SegmentEdges { segment: *next_id, line, start_m: pa, end_m: pb });
                    *next_id += 1;
                }
            }
        }
        RingInfo { line, vertices: n, length_m: acc, origin }
    }

    fn cell_x(&self, lon: f64) -> isize {
        ((lon - self.opts.bbox[0]) / self.opts.cell_deg).floor() as isize
    }
    fn cell_y(&self, lat: f64) -> isize {
        ((lat - self.opts.bbox[2]) / self.opts.cell_deg).floor() as isize
    }
    fn cell_range(&self, lo: f64, hi: f64, x: bool) -> Option<(usize, usize)> {
        let (a, b, n) = if x { (self.cell_x(lo), self.cell_x(hi), self.nx) } else { (self.cell_y(lo), self.cell_y(hi), self.ny) };
        if b < 0 || a >= n as isize { None } else { Some((a.max(0) as usize, b.min(n as isize - 1) as usize)) }
    }

    fn build_index(&mut self) {
        let (nx, ny) = (self.nx, self.ny);
        let mut count = vec![0u32; nx * ny + 1];
        let cells_of = |c: &Self, i: usize, f: &mut dyn FnMut(usize)| {
            if let Some((a, b)) = c.edge(i) {
                if let (Some((x0, x1)), Some((y0, y1))) =
                    (c.cell_range(a[0].min(b[0]), a[0].max(b[0]), true), c.cell_range(a[1].min(b[1]), a[1].max(b[1]), false))
                {
                    for y in y0..=y1 {
                        for x in x0..=x1 {
                            f(y * nx + x);
                        }
                    }
                }
            }
        };
        for i in 0..self.verts.len() {
            cells_of(self, i, &mut |k| count[k + 1] += 1);
        }
        for k in 0..nx * ny {
            count[k + 1] += count[k];
        }
        let mut fill = count.clone();
        let mut edges = vec![0u32; count[nx * ny] as usize];
        for i in 0..self.verts.len() {
            cells_of(self, i, &mut |k| {
                edges[fill[k] as usize] = i as u32;
                fill[k] += 1;
            });
        }
        self.cell_off = count;
        self.cell_edges = edges;
        let mut state = vec![SEA; nx * ny];
        for y in 0..ny {
            let yc = self.opts.bbox[2] + (y as f64 + 0.5) * self.opts.cell_deg;
            let mut land = false;
            for x in 0..nx {
                let k = y * nx + x;
                if self.cell_off[k + 1] > self.cell_off[k] {
                    state[k] = COASTAL;
                    land ^= self.crossings_in_cell(k, x, yc, f64::INFINITY) % 2 == 1;
                } else {
                    state[k] = if land { LAND } else { SEA };
                }
            }
        }
        self.state = state;
    }

    fn cell_edges(&self, k: usize) -> &[u32] {
        &self.cell_edges[self.cell_off[k] as usize..self.cell_off[k + 1] as usize]
    }

    /// Crossings of the horizontal line `lat = y` by edges of cell `k` (column `x`) at longitudes
    /// inside column `x` and below `x_max`. Half-open in latitude, so vertices count once.
    fn crossings_in_cell(&self, k: usize, x: usize, y: f64, x_max: f64) -> usize {
        self.cell_edges(k)
            .iter()
            .filter(|&&i| {
                let Some((a, b)) = self.edge(i as usize) else { return false };
                if (a[1] > y) == (b[1] > y) {
                    return false;
                }
                let xc = a[0] + (y - a[1]) / (b[1] - a[1]) * (b[0] - a[0]);
                xc < x_max && self.cell_x(xc) == x as isize
            })
            .count()
    }

    fn in_box(&self, p: LonLat) -> bool {
        let b = self.opts.bbox;
        p[0] >= b[0] && p[0] < b[1] && p[1] >= b[2] && p[1] < b[3]
    }

    fn segment_of(&self, line_ring: usize, chainage_m: f64) -> SegmentId {
        let (a, b) = self.ring_segs[line_ring];
        let s = &self.segs[a..b];
        let k = s.partition_point(|e| e.start_m <= chainage_m).saturating_sub(1);
        s[k].segment
    }

    fn hit_on_edge(&self, i: usize, u: f64, point: LonLat, fraction: f64, snapped_m: f64) -> CoastHit {
        let r = self.ring_of[i] as usize;
        let chainage_m = self.chain[i] + u.clamp(0.0, 1.0) * self.edge_len[i];
        CoastHit { segment: self.segment_of(r, chainage_m), line: self.rings[r].line, chainage_m, fraction, point, snapped_m }
    }

    /// Nearest shoreline point to `p` within `max_m` (local tangent plane at `p`), as a hit with
    /// `snapped_m` the distance. Also how drift maps a find's coordinates onto line and chainage.
    pub fn locate(&self, p: LonLat, max_m: f64) -> Option<CoastHit> {
        if !(max_m > 0.0) {
            return None;
        }
        let k_m = EARTH_RADIUS_M * std::f64::consts::PI / 180.0;
        let cos = p[1].to_radians().cos().max(1e-6);
        let (dlat, dlon) = (max_m / k_m, max_m / (k_m * cos));
        let (x0, x1) = self.cell_range(p[0] - dlon, p[0] + dlon, true)?;
        let (y0, y1) = self.cell_range(p[1] - dlat, p[1] + dlat, false)?;
        let mut best: Option<(f64, usize, f64)> = None;
        for y in y0..=y1 {
            for x in x0..=x1 {
                for &i in self.cell_edges(y * self.nx + x) {
                    let Some((a, b)) = self.edge(i as usize) else { continue };
                    let (ax, ay) = ((a[0] - p[0]) * cos * k_m, (a[1] - p[1]) * k_m);
                    let (bx, by) = ((b[0] - p[0]) * cos * k_m, (b[1] - p[1]) * k_m);
                    let (dx, dy) = (bx - ax, by - ay);
                    let l2 = dx * dx + dy * dy;
                    let u = if l2 > 0.0 { (-(ax * dx + ay * dy) / l2).clamp(0.0, 1.0) } else { 0.0 };
                    let d = ((ax + u * dx).powi(2) + (ay + u * dy).powi(2)).sqrt();
                    if best.map_or(true, |(bd, bi, _)| d < bd || (d == bd && (i as usize) < bi)) {
                        best = Some((d, i as usize, u));
                    }
                }
            }
        }
        let (d, i, u) = best.filter(|b| b.0 <= max_m)?;
        let (a, b) = self.edge(i).unwrap();
        let point = [a[0] + u * (b[0] - a[0]), a[1] + u * (b[1] - a[1])];
        Some(self.hit_on_edge(i, u, point, 0.0, d))
    }

    /// Lines (rings) and their lengths.
    pub fn ring_infos(&self) -> &[RingInfo] {
        &self.rings
    }

    /// Ring index of a GSHHG id.
    pub fn ring_index(&self, line: LineId) -> Option<usize> {
        self.rings.iter().position(|r| r.line == line)
    }

    /// The vertices of one ring (for plotting and tests).
    pub fn ring_points(&self, ri: usize) -> &[LonLat] {
        let s = self.ring_start[ri];
        &self.verts[s..s + self.ring_len(ri)]
    }

    /// Fraction of index cells that are coastal / land / sea.
    pub fn cell_census(&self) -> [usize; 3] {
        let mut c = [0usize; 3];
        for &s in &self.state {
            c[s as usize] += 1;
        }
        [c[COASTAL as usize], c[LAND as usize], c[SEA as usize]]
    }
}

impl Coastline for PolygonCoast {
    fn is_land(&self, p: LonLat) -> bool {
        if !self.in_box(p) {
            return false;
        }
        let (x, y) = (self.cell_x(p[0]) as usize, self.cell_y(p[1]) as usize);
        let mut odd = false;
        let mut col = x as isize;
        let mut x_max = p[0];
        while col >= 0 {
            let k = y * self.nx + col as usize;
            match self.state[k] {
                COASTAL => {
                    odd ^= self.crossings_in_cell(k, col as usize, p[1], x_max) % 2 == 1;
                    x_max = f64::INFINITY;
                    col -= 1;
                }
                s => return odd ^ (s == LAND),
            }
        }
        odd
    }

    fn first_crossing(&self, from: LonLat, to: LonLat) -> Option<CoastHit> {
        if !self.in_box(from) {
            return None;
        }
        let (x0, x1) = self.cell_range(from[0].min(to[0]), from[0].max(to[0]), true)?;
        let (y0, y1) = self.cell_range(from[1].min(to[1]), from[1].max(to[1]), false)?;
        let mut cand: Vec<u32> = Vec::new();
        for y in y0..=y1 {
            for x in x0..=x1 {
                cand.extend_from_slice(self.cell_edges(y * self.nx + x));
            }
        }
        if cand.is_empty() || self.is_land(from) {
            return None;
        }
        cand.sort_unstable();
        cand.dedup();
        let (dx, dy) = (to[0] - from[0], to[1] - from[1]);
        let mut best: Option<(f64, usize, f64)> = None;
        for &i in &cand {
            let Some((a, b)) = self.edge(i as usize) else { continue };
            let (ex, ey) = (b[0] - a[0], b[1] - a[1]);
            let den = dx * ey - dy * ex;
            if den == 0.0 {
                continue;
            }
            let (wx, wy) = (a[0] - from[0], a[1] - from[1]);
            let s = (wx * ey - wy * ex) / den;
            let u = (wx * dy - wy * dx) / den;
            if (0.0..=1.0).contains(&s) && (0.0..1.0).contains(&u) && best.map_or(true, |(bs, bi, _)| s < bs || (s == bs && (i as usize) < bi)) {
                best = Some((s, i as usize, u));
            }
        }
        let (s, i, u) = best?;
        Some(self.hit_on_edge(i, u, [from[0] + s * dx, from[1] + s * dy], s, 0.0))
    }

    fn snap(&self, p: LonLat) -> Option<CoastHit> {
        self.locate(p, self.opts.snap_max_m)
    }

    fn label(&self) -> String {
        let o = &self.opts;
        let names: Vec<String> = self.named.iter().map(|g| format!("{}={}", g.id, g.name)).collect();
        format!(
            "{}; box {:?}, {} deg cells; named segments [{}]; unnamed pieces ~{} km from id {}; land-mask snap <= {} m",
            self.source,
            o.bbox,
            o.cell_deg,
            names.join(", "),
            o.piece_m / 1000.0,
            o.first_unnamed_id,
            o.snap_max_m
        )
    }

    fn segments(&self) -> Vec<SegmentEdges> {
        self.segs.clone()
    }

    fn segment_names(&self) -> Vec<(SegmentId, String)> {
        self.named.iter().map(|g| (g.id, g.name.clone())).collect()
    }
}
