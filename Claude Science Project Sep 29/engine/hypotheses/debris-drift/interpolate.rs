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

    /// Correlation-length diagnostic (brief section 5, pilot number 3): the separation in NM over
    /// which ln L changes by one unit, from finite differences between evaluated neighbours,
    /// summarised as the weighted median over nodes with the given weights (e.g. posterior mass).
    pub fn ln_l_scale_nm(&self, weights: &[f64], spacing_nm: f64) -> f64 {
        let mut v: Vec<(f64, f64)> = Vec::new();
        for i in 0..self.nlat {
            for j in 0..self.nlon {
                let k = i * self.nlon + j;
                let Node::Value(l) = self.nodes[k] else { continue };
                let mut g2 = 0.0;
                let mut ok = 0;
                if i + 1 < self.nlat { if let Node::Value(l2) = self.nodes[k + self.nlon] { g2 += (l2 - l).powi(2); ok += 1; } }
                if j + 1 < self.nlon { if let Node::Value(l2) = self.nodes[k + 1] { g2 += (l2 - l).powi(2); ok += 1; } }
                if ok == 0 { continue; }
                let g = (g2 / ok as f64).sqrt() / spacing_nm;
                v.push((if g > 0.0 { 1.0 / g } else { f64::INFINITY }, weights.get(k).copied().unwrap_or(1.0)));
            }
        }
        if v.is_empty() { return f64::NAN; }
        v.sort_by(|a, b| a.0.partial_cmp(&b.0).unwrap());
        let tot: f64 = v.iter().map(|x| x.1).sum();
        let mut c = 0.0;
        for (s, w) in &v {
            c += w;
            if c >= 0.5 * tot { return *s; }
        }
        v.last().unwrap().0
    }
}
