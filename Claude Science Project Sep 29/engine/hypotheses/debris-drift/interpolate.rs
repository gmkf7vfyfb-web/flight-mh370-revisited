//! Reading the likelihood surface at an impact sample (brief section 4, contract rules 1, 3, 4).
//!
//! Bilinear interpolation of RELATIVE LIKELIHOOD (linear in L, not in ln L), never of cell
//! probability mass, and never an extrapolation. The sample keeps its own position; no source-cell
//! area factor enters (rule 1). Interpolation is linear in L, so the reference offset used for
//! numerical range cancels exactly and the absolute scale is preserved across ocean models.
//!
//! Node states are kept distinct, because "not computed" is not "impossible" (rule 4):
//! - `Value`: evaluated;
//! - `Land`: not a valid release point. A corner on land is dropped and the remaining weights are
//!   renormalised - the field rule "renormalise across land only, never fill with zero";
//! - `Unresolved`: released but the Monte Carlo estimate is zero for some observation - more
//!   particles are needed. Never read as zero likelihood;
//! - `NotComputed`: outside the evaluated support.
//! A sample touching an Unresolved or NotComputed corner is flagged, not scored.

#[derive(Debug, Clone, Copy, PartialEq)]
pub enum Node {
    Value(f64),
    Land,
    Unresolved,
    NotComputed,
}

#[derive(Debug, Clone, Copy, PartialEq)]
pub enum Lookup {
    Value(f64),
    Unresolved,
    OutsideSupport,
}

#[derive(Debug, Clone)]
pub struct Surface {
    pub lat0: f64,
    pub lon0: f64,
    pub dlat: f64,
    pub dlon: f64,
    pub nlat: usize,
    pub nlon: usize,
    /// ln L per node.
    pub nodes: Vec<Node>,
}

impl Surface {
    pub fn ln_likelihood(&self, lat: f64, lon: f64) -> Lookup {
        let fi = (lat - self.lat0) / self.dlat;
        let fj = (lon - self.lon0) / self.dlon;
        if !(fi >= 0.0 && fj >= 0.0) || fi > (self.nlat - 1) as f64 || fj > (self.nlon - 1) as f64 {
            return Lookup::OutsideSupport;
        }
        let i = (fi.floor() as usize).min(self.nlat.saturating_sub(2));
        let j = (fj.floor() as usize).min(self.nlon.saturating_sub(2));
        let (ti, tj) = (fi - i as f64, fj - j as f64);
        let corners = [
            (i, j, (1.0 - ti) * (1.0 - tj)),
            (i + 1, j, ti * (1.0 - tj)),
            (i, j + 1, (1.0 - ti) * tj),
            (i + 1, j + 1, ti * tj),
        ];
        let mut vals = [(0.0, 0.0); 4];
        let mut n = 0;
        for &(ci, cj, w) in &corners {
            if ci >= self.nlat || cj >= self.nlon {
                if w > 0.0 { return Lookup::OutsideSupport; }
                continue;
            }
            match self.nodes[ci * self.nlon + cj] {
                Node::Value(l) => { if w > 0.0 { vals[n] = (w, l); n += 1; } }
                Node::Land => {}
                Node::Unresolved => { if w > 0.0 { return Lookup::Unresolved; } }
                Node::NotComputed => { if w > 0.0 { return Lookup::OutsideSupport; } }
            }
        }
        if n == 0 {
            return Lookup::OutsideSupport;
        }
        let wsum: f64 = vals[..n].iter().map(|v| v.0).sum();
        let lref = vals[..n].iter().map(|v| v.1).fold(f64::NEG_INFINITY, f64::max);
        if lref == f64::NEG_INFINITY {
            return Lookup::Value(f64::NEG_INFINITY);
        }
        let s: f64 = vals[..n].iter().map(|(w, l)| w / wsum * (l - lref).exp()).sum();
        Lookup::Value(lref + s.ln())
    }
}
