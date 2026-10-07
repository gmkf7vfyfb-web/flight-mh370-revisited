//! The hand-off at the filter's stop epoch (00:11 in the integrated estimate): per replicate,
//! K trajectories drawn from the final posterior, each with its full continuation state, for
//! the end-of-flight stage to continue.
//!
//! The draw is stratified. Each stratum (autopilot mode) first draws K equally weighted
//! particles from its final weights; stratum s then keeps K_s = max(floor, round(K P(s|D)))
//! of them, by systematic resampling, each weighted P(s|D) / K_s. So a mode with little
//! posterior mass is still represented, and the rows pool across replicates with the
//! summary.rs factors exactly as final.npy rows do.
//!
//! Two files per replicate, row-aligned: handoff.npy (float64), a numeric index for analysis
//! (columns in [`COLUMNS`]); handoff.toml, the state itself: the serialised aircraft (guidance
//! included), the BFO-bias posterior, and the particle's index in its filter, so it can be
//! continued on that filter's own random streams. TOML because the manoeuvre clocks hold
//! infinities, which JSON cannot carry, and it round-trips every f64 exactly.

use crate::filter::systematic_resample;
use crate::output::write_npy64;
use flight::Aircraft;
use rand::Rng;
use satcom::BfoBias;
use serde::{Deserialize, Serialize};
use std::path::Path;

pub const COLUMNS: [&str; 13] = [
    "weight", "latitude_deg", "longitude_deg", "altitude_ft", "mach", "tau_h", "mode", "alternative",
    "bfo_bias_hz", "bfo_bias_variance_hz2", "origin", "final_row", "particle",
];

/// `final_row` of a hand-off taken at an intermediate epoch (output.handoff_epochs): the filter
/// resampled after it, so no final.npy row corresponds. NaN in handoff.npy. i64::MAX so the
/// TOML round-trip holds it.
pub const NO_FINAL_ROW: usize = i64::MAX as usize;

/// A particle drawn for the hand-off, equally weighted within its stratum.
pub struct Candidate {
    /// Index in its stratum's filter at the stop.
    pub particle: usize,
    pub aircraft: Aircraft,
    pub bias: BfoBias,
    pub origin: u32,
}

/// One stratum's draws, with its posterior probability and its first row in final.npy.
pub struct Stratum {
    pub mode: usize,
    pub probability: f64,
    pub final_offset: usize,
    pub candidates: Vec<Candidate>,
}

/// Where the filter stopped.
#[derive(Serialize, Deserialize, Clone, Debug, PartialEq)]
pub struct Stop {
    pub epoch: String,
    /// Index of the stop among the filter's steps: the next step's streams are step + 2.
    pub step: usize,
    pub unix_s: f64,
}

#[derive(Serialize, Deserialize, Clone, Copy, Debug, PartialEq)]
pub struct Bias {
    pub mean_hz: f64,
    pub variance_hz2: f64,
}

/// One handed-off trajectory.
#[derive(Serialize, Deserialize, Clone, Debug)]
pub struct Row {
    /// Share of the replicate's posterior; the rows of a replicate sum to one.
    pub weight: f64,
    pub mode: usize,
    pub alternative: usize,
    /// Index in its stratum's filter at the stop.
    pub particle: usize,
    /// Its row in final.npy.
    pub final_row: usize,
    /// The prior draw it descends from.
    pub origin: u32,
    pub bias: Bias,
    pub aircraft: Aircraft,
}

#[derive(Serialize, Deserialize)]
struct File {
    stop: Stop,
    row: Vec<Row>,
}

/// The stratified draw described at the top of this file.
pub fn select(strata: Vec<Stratum>, k: usize, floor: usize, rng: &mut impl Rng) -> Vec<Row> {
    let mut rows = Vec::new();
    for s in strata {
        let drawn = s.candidates.len();
        if s.probability <= 0.0 || drawn == 0 {
            continue;
        }
        let keep = ((k as f64 * s.probability).round() as usize).max(floor).clamp(1, drawn);
        let equal = vec![-(drawn as f64).ln(); drawn];
        for j in systematic_resample(&equal, keep, rng) {
            let c = &s.candidates[j];
            rows.push(Row {
                weight: s.probability / keep as f64,
                mode: s.mode,
                alternative: 0,
                particle: c.particle,
                final_row: s.final_offset + c.particle,
                origin: c.origin,
                bias: Bias { mean_hz: c.bias.mean_hz, variance_hz2: c.bias.variance_hz2 },
                aircraft: c.aircraft.clone(),
            });
        }
    }
    rows
}

pub fn write(dir: &Path, stop: &Stop, rows: &[Row]) -> Result<(), String> {
    let values: Vec<f64> = rows
        .iter()
        .flat_map(|r| {
            let a = &r.aircraft;
            [
                r.weight,
                a.lat,
                a.lon,
                a.alt_ft,
                a.mach,
                a.tau_s / 3600.0,
                r.mode as f64,
                r.alternative as f64,
                r.bias.mean_hz,
                r.bias.variance_hz2,
                f64::from(r.origin),
                if r.final_row == NO_FINAL_ROW { f64::NAN } else { r.final_row as f64 },
                r.particle as f64,
            ]
        })
        .collect();
    write_npy64(&dir.join("handoff.npy"), &[rows.len(), COLUMNS.len()], &values)?;
    let text = toml::to_string(&File { stop: stop.clone(), row: rows.to_vec() }).map_err(|e| format!("handoff.toml: {e}"))?;
    let path = dir.join("handoff.toml");
    std::fs::write(&path, text).map_err(|e| format!("{}: {e}", path.display()))
}

pub fn read(dir: &Path) -> Result<(Stop, Vec<Row>), String> {
    let path = dir.join("handoff.toml");
    let text = std::fs::read_to_string(&path).map_err(|e| format!("{}: {e}", path.display()))?;
    let file: File = toml::from_str(&text).map_err(|e| format!("{}: {e}", path.display()))?;
    Ok((file.stop, file.row))
}
