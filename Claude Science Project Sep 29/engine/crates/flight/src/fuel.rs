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
        pts.dedup_by(|a, b| a.0 == b.0);
        pts
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
        let k = if mach < pts[0].0 {
            0
        } else if mach >= pts[pts.len() - 1].0 {
            pts.len() - 2
        } else {
            (0..pts.len() - 1).rev().find(|&i| pts[i].0 <= mach)?
        };
        let ((m0, f0), (m1, f1)) = (pts[k], pts[k + 1]);
        cover.extrapolated_mach = mach < pts[0].0 || mach > pts[pts.len() - 1].0;
        let det = m0 * m0 / (m1 * m1) - m1 * m1 / (m0 * m0);
        let a = (f0 / (m1 * m1) - f1 / (m0 * m0)) / det;
        let b = (m0 * m0 * f1 - m1 * m1 * f0) / det;
        let per_engine = a * mach * mach + b / (mach * mach);
        (per_engine.is_finite() && per_engine > 0.0).then_some((2.0 * per_engine, cover))
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
    fn heavier_burns_more() {
        let t = tables();
        let light = t.fuel_flow_kg_h(350.0, 190.0, 0.80).unwrap().0;
        let heavy = t.fuel_flow_kg_h(350.0, 220.0, 0.80).unwrap().0;
        assert!(heavy > light, "{heavy} should exceed {light}");
    }
}
