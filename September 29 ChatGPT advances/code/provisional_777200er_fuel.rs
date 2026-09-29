//! PROVISIONAL / NON-SCIENTIFIC fuel-flow adapter for integration test runs only.
//!
//! Source basis: publicly digitised B-777-200ER Operational Data Manual long-range-cruise
//! table (20 Jan 2011).  The source table reports FUEL FLOW / ENGINE in lb/hr against gross
//! weight and pressure altitude.  This adapter intentionally uses a small, conservative subset
//! of clearly readable cells and linear interpolation.  Replace with the Ulich 9M-MRO table
//! before any scientific MH370 posterior is reported.
//!
//! Occurrence-flight mass baseline from the Malaysian Safety Investigation Report, Table 1.6D:
//! ZFW = 174,369 kg; TOW = 223,469 kg; take-off fuel = 49,100 kg.

use crate::fuel::FuelFlowModel;

pub const MH370_ZFW_KG: f64 = 174_369.0;
const LB_TO_KG: f64 = 0.453_592_37;
const KG_TO_LB: f64 = 1.0 / LB_TO_KG;

/// Subset of long-range-cruise fuel flow values, lb/hr PER ENGINE.
/// Rows are gross weight (lb); columns are pressure altitude (thousand ft).
/// Values transcribed only where the public text extraction is unambiguous.
const ALT_KFT: [f64; 6] = [21.0, 23.0, 25.0, 27.0, 29.0, 31.0];
const WEIGHT_LB: [f64; 6] = [300_000.0, 340_000.0, 380_000.0, 420_000.0, 460_000.0, 500_000.0];
const FLOW_LB_H_ENGINE: [[f64; 6]; 6] = [
    [7349.0, 7408.0, 7307.0, 7299.0, 7306.0, 7351.0],
    [8138.0, 8085.0, 8068.0, 8075.0, 8124.0, 8208.0],
    [8922.0, 8940.0, 8916.0, 8947.0, 9060.0, 9060.0], // 31k held at last readable value
    [9917.0, 9919.0, 9963.0, 10093.0, 10093.0, 10093.0], // edge holds are deliberate/test-only
    [10937.0, 10984.0, 11127.0, 11244.0, 11244.0, 11244.0],
    [12027.0, 12172.0, 12294.0, 12294.0, 12294.0, 12294.0],
];

#[derive(Debug, Clone, Copy, Default)]
pub struct Provisional777200ErLrc;

fn bracket(x: f64, grid: &[f64]) -> (usize, usize, f64) {
    if x <= grid[0] { return (0, 0, 0.0); }
    let last = grid.len() - 1;
    if x >= grid[last] { return (last, last, 0.0); }
    for i in 0..last {
        if x <= grid[i + 1] {
            let t = (x - grid[i]) / (grid[i + 1] - grid[i]);
            return (i, i + 1, t);
        }
    }
    unreachable!()
}

fn lerp(a: f64, b: f64, t: f64) -> f64 { a + t * (b - a) }

impl FuelFlowModel for Provisional777200ErLrc {
    fn flow_kg_h(&self, _mach: f64, altitude_ft: f64, gross_weight_kg: f64, _temperature_k: f64) -> f64 {
        let w_lb = gross_weight_kg * KG_TO_LB;
        let a_kft = altitude_ft / 1000.0;
        let (w0, w1, tw) = bracket(w_lb, &WEIGHT_LB);
        let (a0, a1, ta) = bracket(a_kft, &ALT_KFT);
        let f0 = lerp(FLOW_LB_H_ENGINE[w0][a0], FLOW_LB_H_ENGINE[w0][a1], ta);
        let f1 = lerp(FLOW_LB_H_ENGINE[w1][a0], FLOW_LB_H_ENGINE[w1][a1], ta);
        let per_engine_lb_h = lerp(f0, f1, tw);
        2.0 * per_engine_lb_h * LB_TO_KG
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn exact_table_cell_converts_two_engine_flow() {
        let m = Provisional777200ErLrc;
        let kg_h = m.flow_kg_h(0.8, 25_000.0, 500_000.0 * LB_TO_KG, 220.0);
        let expected = 2.0 * 12_294.0 * LB_TO_KG;
        assert!((kg_h - expected).abs() < 1e-9);
    }

    #[test]
    fn mh370_anchor_gross_mass_is_zfw_plus_fuel() {
        assert_eq!(MH370_ZFW_KG + 43_800.0, 218_169.0);
    }
}
