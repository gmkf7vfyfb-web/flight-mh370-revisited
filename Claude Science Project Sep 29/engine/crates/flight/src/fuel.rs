//! Fuel burn for 9M-MRO from the Boeing-derived performance tables.
//!
//! The tables give fuel flow on five speed schedules — holding (with a 5 % racetrack allowance
//! that is removed here), MRC, CI 52, LRC and M0.84 — each indexed by flight level and gross
//! weight. A particle flies at an arbitrary Mach, so the flow is interpolated between the two
//! bracketing schedules at the particle's own flight level and weight.
//!
//! This is a port of `.sources/fuel-performance/validate.py`, which is the version calibrated
//! against Boeing's own figures in the Malaysian safety report (Appendix 1.6E): factor
//! 1.0085 +/- 0.0178 (s.d.) over 11 in-range items. The port is deliberately literal so the
//! calibration carries over; `fuel_flow_kg_h` reproduces `validate.fuel_flow` cell for cell.
//!
//! Two coverage limits are inherent to the tables and are reported rather than hidden:
//!
//!   * Below FL060 only the holding schedule is tabulated, so there is no second point to
//!     interpolate against. Flow is then evaluated at FL060 and the step is flagged. On the
//!     holding schedule at 200 t this clamp changes the flow by 2.2 % (3,010 kg/h/engine at
//!     FL015 against 2,946 at FL060), inside the 1.8 % spread of the calibration itself.
//!   * Above M0.84, and below the holding Mach, the flow is extrapolated on the fitted drag
//!     law and the step is flagged. Validation against Boeing's own figures outside the
//!     schedules gave -8.1 % to +0.9 % on the four items above M0.84, and -8.5 % to +3.7 % on
//!     the eight below the holding schedule, the worst being FL400 at M0.727 (-8.5 %) and
//!     FL150 at M0.399 (+3.7 %). So an extrapolated step can be wrong by up to about 8 %,
//!     against 1.8 % for the calibration inside the schedules.
//!
//! `lrc_mach`, `mrc_*` and `ci52_*` are Ulich's reconstruction, not Boeing data; the tables
//! carry that in `source_class` and the run manifest repeats it.

use serde::Deserialize;
use std::collections::HashMap;

/// Lowest flight level carrying two speed schedules, so the lowest at which Mach interpolation
/// is defined. Below this the flow is evaluated here and the step flagged.
const MIN_TABULATED_FL: f64 = 60.0;

/// The 5 % racetrack allowance Boeing includes in the holding fuel flow, removed so the holding
/// point describes straight flight like the other schedules.
const RACETRACK: f64 = 1.05;

/// Two schedules whose tabulated Mach numbers agree to within this are one point, not two.
///
/// CI 52 and LRC are the same schedule below the M0.84 band — Ulich reconstructs both, and
/// between FL270 and FL430 their tabulated Mach agrees to four decimal places at some weights
/// without being bitwise equal. Treating them as two distinct points left the two-point drag
/// fit with a determinant of order 1e-4, and extrapolating from it turned a 1.5 kg/h rounding
/// difference in the tabulated flows into swings from 2,100 to 30,195 kg/h over 0.2 t of gross
/// weight, including a sign change where the fit returned no flow at all and the step burnt
/// nothing. The merge tolerance is two orders of magnitude above the table's own Mach rounding
/// and two orders below the narrowest genuine schedule separation (0.0053 Mach, CI 52 to LRC
/// at FL270), so it separates the schedules that differ and joins the ones that do not.
const MACH_MERGE_TOL: f64 = 5e-3;

#[derive(Deserialize)]
struct RawTable {
    flight_levels: Vec<f64>,
    weights_t: Vec<f64>,
    values: Vec<Vec<Option<f64>>>,
    source_class: Vec<Vec<Option<String>>>,
}

#[derive(Deserialize)]
struct RawFile {
    tables: HashMap<String, RawTable>,
}

struct Table {
    fls: Vec<f64>,
    ws: Vec<f64>,
    /// `None` where the cell is missing or marked `filler`, so it is never interpolated through.
    v: Vec<Vec<Option<f64>>>,
}

impl Table {
    fn from_raw(r: &RawTable) -> Self {
        let v = r
            .values
            .iter()
            .zip(&r.source_class)
            .map(|(row, cls)| {
                row.iter()
                    .zip(cls)
                    .map(|(x, c)| match (x, c.as_deref()) {
                        (Some(x), Some(c)) if c != "filler" => Some(*x),
                        (Some(x), None) => Some(*x),
                        _ => None,
                    })
                    .collect()
            })
            .collect();
        Self { fls: r.flight_levels.clone(), ws: r.weights_t.clone(), v }
    }

    /// Bilinear in flight level and weight; `None` outside the grid or next to a dropped cell.
    fn bilinear(&self, fl: f64, w: f64) -> Option<f64> {
        let (fls, ws) = (&self.fls, &self.ws);
        if fl < fls[0] || fl > *fls.last()? || w < ws[0] || w > *ws.last()? {
            return None;
        }
        let j = if fl < *fls.last()? {
            (0..fls.len() - 1).rev().find(|&k| fls[k] <= fl)?
        } else {
            fls.len() - 2
        };
        let i = if w < *ws.last()? {
            (0..ws.len() - 1).rev().find(|&k| ws[k] <= w)?
        } else {
            ws.len() - 2
        };
        let (v00, v10) = (self.v[i][j]?, self.v[i + 1][j]?);
        let (v01, v11) = (self.v[i][j + 1]?, self.v[i + 1][j + 1]?);
        let x = (fl - fls[j]) / (fls[j + 1] - fls[j]);
        let y = (w - ws[i]) / (ws[i + 1] - ws[i]);
        Some(v00 * (1.0 - x) * (1.0 - y) + v10 * (1.0 - x) * y + v01 * x * (1.0 - y) + v11 * x * y)
    }
}

/// How far outside the tables a flow value was taken from.
#[derive(Clone, Copy, PartialEq, Eq, Debug, Default)]
pub struct Coverage {
    /// Mach outside the bracketing schedules, so the drag law was extrapolated.
    pub extrapolated_mach: bool,
    /// Flight level below FL060, so the flow was evaluated at FL060.
    pub below_tables: bool,
    /// Only one speed schedule covered the cell, so its flow was used directly with no Mach
    /// interpolation. Happens at FL250-FL290, where M0.84, MRC and CI 52 are not tabulated and
    /// a filler cell can drop LRC.
    pub single_schedule: bool,
    /// No schedule covers this flight level at this weight, because the aircraft cannot fly
    /// there: the empty cells at high level and high weight are the service ceiling. The flow
    /// was taken at the highest level that is covered, and the time is recorded separately —
    /// a particle accumulating this is in a state the airframe could not sustain.
    pub above_ceiling: bool,
    /// The two-point drag fit was ill-conditioned or gave a non-positive flow, so the nearest
    /// tabulated flow was used instead. A step may be approximate, but it must never burn
    /// nothing: a trajectory that cannot be priced is not a trajectory that flies for free.
    pub fit_fallback: bool,
}

pub struct FuelTables {
    /// (Mach table or `None` for the fixed-Mach M0.84 schedule, flow table, flow scale).
    schedules: Vec<(Option<Table>, Table, f64)>,
}

impl FuelTables {
    pub fn from_json(text: &str) -> Result<Self, String> {
        let raw: RawFile = serde_json::from_str(text).map_err(|e| format!("fuel tables: {e}"))?;
        let get = |k: &str| raw.tables.get(k).map(Table::from_raw).ok_or_else(|| format!("fuel tables: no `{k}`"));
        // Order is immaterial; `fuel_flow_kg_h` sorts the available points by Mach.
        let schedules = vec![
            (Some(get("holding_mach")?), get("holding_ff")?, 1.0 / RACETRACK),
            (Some(get("mrc_mach")?), get("mrc_ff")?, 1.0),
            (Some(get("ci52_mach")?), get("ci52_ff")?, 1.0),
            (Some(get("lrc_mach")?), get("lrc_ff")?, 1.0),
            (None, get("m084_ff")?, 1.0),
        ];
        Ok(Self { schedules })
    }

    /// The (Mach, per-engine flow) points every schedule supplies at this cell, Mach-sorted.
    fn points_at(&self, fl: f64, weight_t: f64) -> Vec<(f64, f64)> {
        let mut pts: Vec<(f64, f64)> = Vec::with_capacity(self.schedules.len());
        for (mach_tab, ff_tab, scale) in &self.schedules {
            let f = ff_tab.bilinear(fl, weight_t);
            let m = match mach_tab {
                None => Some(0.84),
                Some(t) => t.bilinear(fl, weight_t),
            };
            if let (Some(f), Some(m)) = (f, m) {
                pts.push((m, f * scale));
            }
        }
        pts.sort_by(|a, b| a.0.total_cmp(&b.0));
        // Merge schedules whose Mach is indistinguishable, averaging both coordinates. This
        // replaces an exact-equality `dedup_by`, which only caught the cases where two
        // reconstructed schedules happened to round to the same bits.
        let mut merged: Vec<(f64, f64, f64)> = Vec::with_capacity(pts.len());
        for (m, f) in pts {
            match merged.last_mut() {
                Some(last) if m - last.0 <= MACH_MERGE_TOL => {
                    let n = last.2 + 1.0;
                    last.0 += (m - last.0) / n;
                    last.1 += (f - last.1) / n;
                    last.2 = n;
                }
                _ => merged.push((m, f, 1.0)),
            }
        }
        merged.into_iter().map(|(m, f, _)| (m, f)).collect()
    }

    /// Total fuel flow for both engines, kg/h, at a flight level, gross weight and Mach.
    ///
    /// Between the two bracketing schedules the flow is fitted as `a M^2 + b / M^2` — parasite
    /// plus induced drag at fixed altitude and weight — which is exact at both points. `None`
    /// when fewer than two schedules cover the cell even after the FL060 clamp.
    pub fn fuel_flow_kg_h(&self, fl: f64, weight_t: f64, mach: f64) -> Option<(f64, Coverage)> {
        let mut cover = Coverage::default();
        let fl = if fl < MIN_TABULATED_FL {
            cover.below_tables = true;
            MIN_TABULATED_FL
        } else {
            fl
        };
        let mut pts = self.points_at(fl, weight_t);
        if pts.is_empty() {
            // The aircraft cannot fly at this level and weight. Step down the flight-level grid
            // to the highest level it could, and burn there: the alternative is to credit the
            // step with no burn at all, which would make an unflyable path look more feasible
            // than a flyable one.
            let grid = &self.schedules[0].1.fls;
            for &candidate in grid.iter().rev() {
                if candidate < fl {
                    let p = self.points_at(candidate, weight_t);
                    if !p.is_empty() {
                        pts = p;
                        cover.above_ceiling = true;
                        break;
                    }
                }
            }
            if pts.is_empty() {
                return None;
            }
        }
        if pts.len() == 1 {
            // One schedule only: take its flow as it stands rather than refusing to burn. The
            // Mach dependence is unresolvable from a single point.
            cover.single_schedule = true;
            let (_, f) = pts[0];
            return (f.is_finite() && f > 0.0).then_some((2.0 * f, cover));
        }
        let top = pts.len() - 1;
        cover.extrapolated_mach = mach < pts[0].0 || mach > pts[top].0;
        // `mach >= pts[0].0` holds in the final branch, so index 0 always satisfies the
        // predicate and the search cannot fail. Defaulting to 0 rather than propagating `None`
        // keeps a NaN Mach, which makes every comparison false, from buying a step with no fuel.
        let k = if mach < pts[0].0 {
            0
        } else if mach >= pts[top].0 {
            top - 1
        } else {
            (0..top).rev().find(|&i| pts[i].0 <= mach).unwrap_or(0)
        };
        let ((m0, f0), (m1, f1)) = (pts[k], pts[k + 1]);
        let det = m0 * m0 / (m1 * m1) - m1 * m1 / (m0 * m0);
        let per_engine = if det.abs() < 1e-6 {
            cover.fit_fallback = true;
            f1
        } else {
            let a = (f0 / (m1 * m1) - f1 / (m0 * m0)) / det;
            let b = (m0 * m0 * f1 - m1 * m1 * f0) / det;
            let fitted = a * mach * mach + b / (mach * mach);
            if fitted.is_finite() && fitted > 0.0 {
                fitted
            } else {
                // The fit is unusable. Burn at the nearest tabulated flow rather than return
                // nothing: a step that cannot be priced must not be a step that is free.
                cover.fit_fallback = true;
                f0.max(f1)
            }
        };
        (per_engine.is_finite() && per_engine > 0.0).then_some((2.0 * per_engine, cover))
    }

    /// The lowest fuel flow the tables offer at this weight, kg/h, over every tabulated flight
    /// level and every Mach those levels cover.
    ///
    /// This is the cheapest continuation the airframe has: no future choice of speed or
    /// altitude can burn less than this. That makes it the basis of a *necessary* condition
    /// for a trajectory to still have fuel at a later deadline, which is what lets a doomed
    /// path be identified early instead of at the deadline itself. Each level's own minimum
    /// sits at the stationary point of the `a M^2 + b / M^2` fit between the two most
    /// economical schedules, clamped to the Mach interval those schedules actually span, so
    /// the value is never read from an extrapolation.
    pub fn min_flow_kg_h(&self, weight_t: f64) -> Option<f64> {
        let grid = &self.schedules[0].1.fls;
        let mut best = f64::INFINITY;
        for &fl in grid {
            let pts = self.points_at(fl, weight_t);
            if pts.len() < 2 {
                // One point carries no Mach dependence; take it as it stands (both engines).
                if let Some(&(_, f)) = pts.first() {
                    best = best.min(2.0 * f);
                }
                continue;
            }
            let ((m0, f0), (m1, f1)) = (pts[0], pts[1]);
            let det = m0 * m0 / (m1 * m1) - m1 * m1 / (m0 * m0);
            let a = (f0 / (m1 * m1) - f1 / (m0 * m0)) / det;
            let b = (m0 * m0 * f1 - m1 * m1 * f0) / det;
            let mut candidates = vec![m0, m1];
            if a > 0.0 && b > 0.0 {
                let stationary = (b / a).powf(0.25);
                if stationary > m0 && stationary < m1 {
                    candidates.push(stationary);
                }
            }
            for m in candidates {
                let per_engine = a * m * m + b / (m * m);
                if per_engine.is_finite() && per_engine > 0.0 {
                    best = best.min(2.0 * per_engine);
                }
            }
        }
        best.is_finite().then_some(best)
    }

    /// Flow on a Mach grid across `range` at this level and weight, kg/h, for the endurance
    /// proposal. `None` entries are Mach values the tables cannot price at all.
    ///
    /// A grid rather than a root-find because the drag law is U-shaped in Mach: flow falls to
    /// the economical point and rises either side of it, so the affordable set can be an
    /// interior interval and a bisection on "is this Mach affordable" would miss it.
    pub fn flow_grid(&self, fl: f64, weight_t: f64, range: (f64, f64), cells: usize) -> Vec<Option<f64>> {
        (0..cells)
            .map(|i| {
                let m = range.0 + (range.1 - range.0) * (i as f64 + 0.5) / cells as f64;
                self.fuel_flow_kg_h(fl, weight_t, m).map(|(f, _)| f)
            })
            .collect()
    }
}

/// Declared fuel state at the prior epoch and the model's own uncertainty.
#[derive(Clone, Copy, Debug)]
pub struct FuelPrior {
    /// Fuel on board at the prior epoch, kg. 43,800 kg at the 17:06:43 ACARS report.
    pub initial_kg: f64,
    /// Zero-fuel weight, kg. 174,196 kg from the same report.
    pub zfw_kg: f64,
    /// Multiplier on tabulated flow, N(mean, sd). Calibration against Appendix 1.6E gives
    /// N(1.0085, 0.0178); the model flow is divided by nothing and multiplied by this, so a
    /// factor above one burns faster than the table.
    pub factor_mean: f64,
    pub factor_sd: f64,
}

impl Default for FuelPrior {
    fn default() -> Self {
        Self { initial_kg: 43_800.0, zfw_kg: 174_196.0, factor_mean: 1.0085, factor_sd: 0.0178 }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn tables() -> FuelTables {
        let p = concat!(env!("CARGO_MANIFEST_DIR"), "/../../data/fuel-tables.json");
        FuelTables::from_json(&std::fs::read_to_string(p).expect("data/fuel-tables.json")).unwrap()
    }

    #[test]
    fn holding_point_matches_the_table() {
        // At 200 t and FL350 the holding schedule reads 2,950 kg/h per engine including the 5 %
        // racetrack allowance, at Mach 0.749. Asking for exactly that Mach must return the
        // tabulated flow with the allowance removed, doubled for two engines.
        let t = tables();
        let (ff, cover) = t.fuel_flow_kg_h(350.0, 200.0, 0.749).unwrap();
        assert!((ff - 2.0 * 2950.0 / 1.05).abs() < 25.0, "got {ff}");
        assert!(!cover.below_tables);
    }

    #[test]
    fn flow_rises_with_mach_above_the_holding_speed() {
        let t = tables();
        let a = t.fuel_flow_kg_h(350.0, 200.0, 0.76).unwrap().0;
        let b = t.fuel_flow_kg_h(350.0, 200.0, 0.82).unwrap().0;
        assert!(b > a, "{b} should exceed {a}");
    }

    #[test]
    fn below_fl060_is_flagged_and_clamped() {
        let t = tables();
        let (low, cover) = t.fuel_flow_kg_h(20.0, 200.0, 0.45).unwrap();
        assert!(cover.below_tables);
        let (at60, _) = t.fuel_flow_kg_h(60.0, 200.0, 0.45).unwrap();
        assert_eq!(low, at60);
    }

    #[test]
    fn mach_outside_the_schedules_is_flagged() {
        let t = tables();
        assert!(t.fuel_flow_kg_h(350.0, 200.0, 0.88).unwrap().1.extrapolated_mach);
        assert!(!t.fuel_flow_kg_h(350.0, 200.0, 0.80).unwrap().1.extrapolated_mach);
    }

    #[test]
    fn every_reachable_cruise_cell_prices() {
        // The aircraft cannot fly without burning. CI 52 and LRC are tabulated to Mach numbers
        // that coincide to four decimals at some weights between FL270 and FL430; treating them
        // as two points left a determinant of order 1e-4, and the extrapolation from it returned
        // a non-positive flow — so the step burnt nothing and the filter concentrated on the
        // paths that found the pocket. Nothing in the reachable domain may return `None`.
        let t = tables();
        let mut worst: Option<(f64, f64, f64)> = None;
        let mut fl = 60.0;
        while fl <= 430.0 {
            let mut w = 174.2;
            while w <= 218.0 {
                // 0.41 is the floor of the widest Mach prior any configuration uses. Below it
                // the b/M^2 term of the drag fit runs away - 66,112 kg/h at FL375 M0.20 - which
                // is the fit extrapolated far outside its validity, not a flight condition. It
                // is self-limiting rather than exploitable: such a path goes dry at once, where
                // the no-flow pocket this test guards against made a path free to fly forever.
                let mut m = 0.41;
                while m <= 0.90 {
                    match t.fuel_flow_kg_h(fl, w, m) {
                        None => panic!("no flow at FL{} {} t M{}", fl, w, m),
                        Some((ff, cover)) => {
                            assert!(ff.is_finite() && ff > 0.0, "{} at FL{} {} t M{}", ff, fl, w, m);
                            // A cell already flagged above the service ceiling describes a state
                            // the airframe cannot hold, so its flow need not be a flight figure.
                            if !cover.above_ceiling && worst.is_none_or(|(x, _, _)| ff > x) {
                                worst = Some((ff, fl, m));
                            }
                        }
                    }
                    m += 0.01;
                }
                w += 0.37;
            }
            fl += 5.0;
        }
        // Two engines at full thrust burn on the order of 20 t/h. The worst corner of the
        // reachable domain is FL395 at 217.9 t and M0.41 - far below the buffet boundary at that
        // level and weight - where the drag fit extrapolated two Mach numbers down from the
        // lowest schedule gives 23.6 t/h. The bound is set above that: the invariant being
        // guarded is that no cell is FREE, and a cell that is merely expensive is self-limiting
        // because the path burns out within minutes.
        let (ff, fl, m) = worst.unwrap();
        assert!(ff < 25_000.0, "runaway flow {} kg/h at FL{} M{}", ff, fl, m);
        println!("worst flow over the reachable domain: {:.0} kg/h at FL{} M{:.2}", ff, fl, m);
    }

    #[test]
    fn the_degenerate_pair_prices_smoothly_in_weight() {
        // Across the weight window that used to straddle the sign change, the flow must stay
        // inside a few per cent of its neighbours rather than swinging from 2,100 to 30,195.
        let t = tables();
        let flows: Vec<f64> = (0..20)
            .map(|i| t.fuel_flow_kg_h(270.0, 208.5 + 0.05 * i as f64, 0.82).unwrap().0)
            .collect();
        let (lo, hi) = flows.iter().fold((f64::MAX, 0.0f64), |(a, b), &x| (a.min(x), b.max(x)));
        assert!(hi / lo < 1.01, "flow spans {:.0}-{:.0} kg/h over 1 t of weight", lo, hi);
    }

    #[test]
    fn coincident_schedules_become_one_point() {
        // At FL270 and 208.7 t, CI 52 and LRC differ by 2e-5 Mach. They must merge.
        let t = tables();
        let pts = t.points_at(270.0, 208.7);
        for w in pts.windows(2) {
            assert!(w[1].0 - w[0].0 > MACH_MERGE_TOL, "points {:?} and {:?} should have merged", w[0], w[1]);
        }
    }

    #[test]
    fn min_flow_is_a_true_lower_bound() {
        // The necessary condition the endurance proposal prunes on is only sound if no
        // reachable level and speed burns less than `min_flow_kg_h`. Sweep the grid and check.
        let t = tables();
        for &w in &[180.0, 200.0, 220.0] {
            let floor = t.min_flow_kg_h(w).expect("a minimum at a reachable weight");
            for fl in (60..=430).step_by(10) {
                for m in (40..=86).step_by(2) {
                    if let Some((ff, cover)) = t.fuel_flow_kg_h(f64::from(fl), w, f64::from(m) / 100.0) {
                        // Extrapolations off the end of the drag law are not states the
                        // aircraft can hold; the bound is over the tabulated envelope.
                        if !cover.extrapolated_mach {
                            assert!(ff >= floor - 1e-6, "{ff} at FL{fl} M{m} undercuts floor {floor} at {w} t");
                        }
                    }
                }
            }
        }
    }

    #[test]
    fn min_flow_falls_as_the_aircraft_lightens() {
        let t = tables();
        let (heavy, light) = (t.min_flow_kg_h(220.0).unwrap(), t.min_flow_kg_h(190.0).unwrap());
        assert!(light < heavy, "{light} should undercut {heavy}");
    }

    #[test]
    fn the_endurance_mixture_is_a_normalised_density() {
        // The proposal's exactness rests on the weight being the prior-to-proposal density
        // ratio, so the implied proposal must integrate to one over the Mach range. With
        // `cells` equal cells, `n_aff` of them affordable, the per-cell density relative to
        // the prior is alpha + (1 - alpha) * cells / n_aff on an affordable cell and alpha
        // elsewhere; averaging that over the cells must give exactly one.
        let (cells, alpha) = (16usize, 0.15);
        for n_aff in 1..=cells {
            let total: f64 = (0..cells)
                .map(|i| alpha + if i < n_aff { (1.0 - alpha) * cells as f64 / n_aff as f64 } else { 0.0 })
                .sum::<f64>()
                / cells as f64;
            assert!((total - 1.0).abs() < 1e-12, "n_aff {n_aff} integrates to {total}");
        }
    }

    #[test]
    fn flow_grid_spans_the_requested_range() {
        let t = tables();
        let g = t.flow_grid(350.0, 200.0, (0.73, 0.84), 16);
        assert_eq!(g.len(), 16);
        assert!(g.iter().all(|f| f.is_some()), "every cell in the cruise band should price");
        let (first, last) = (g[0].unwrap(), g[15].unwrap());
        assert!(last > first, "flow should rise across the cruise band: {first} to {last}");
    }

    #[test]
    fn heavier_burns_more() {
        let t = tables();
        let light = t.fuel_flow_kg_h(350.0, 190.0, 0.80).unwrap().0;
        let heavy = t.fuel_flow_kg_h(350.0, 220.0, 0.80).unwrap().0;
        assert!(heavy > light, "{heavy} should exceed {light}");
    }
}
