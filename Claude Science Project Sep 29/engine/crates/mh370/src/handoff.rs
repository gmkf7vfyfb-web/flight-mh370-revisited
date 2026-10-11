
    /// Core request 18: a [stop] block written before the evidence fields still reads, and
    /// one with them round-trips.
    #[test]
    fn stop_reads_with_and_without_request_18_fields() {
        let old: Stop = toml::from_str("epoch = \"m2241\"\nstep = 16\nunix_s = 1394232081.0\n").unwrap();
        assert_eq!(old.log_evidence_by_mode, None);
        assert_eq!(old.observations_not_used, None);
        let new = Stop {
            epoch: "m2241".into(), step: 16, unix_s: 1394232081.0,
            log_evidence_by_mode: Some(vec![-1.0, f64::NEG_INFINITY, -2.0, -3.0, -4.0]),
            mode_probability: Some(vec![0.6, 0.0, 0.3, 0.07, 0.03]),
            log_evidence: Some(-1.5),
            observations_used: Some(vec!["m2241.bto".into()]),
            observations_not_used: Some(vec!["m0011.bto".into(), "m0019a.bto".into()]),
        };
        let back: Stop = toml::from_str(&toml::to_string(&new).unwrap()).unwrap();
        assert_eq!(back, new);
    }
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

/// A particle drawn for the hand-off, equally weighted within its stratum (times
/// exp(`log_correction`) when the hand-off look-ahead drew it).
#[derive(Clone)]
pub struct Candidate {
    /// Index in its stratum's filter at the stop.
    pub particle: usize,
    pub aircraft: Aircraft,
    pub bias: BfoBias,
    pub origin: u32,
    /// Core request 10: ln of the importance correction p/q for a candidate drawn by the
    /// hand-off look-ahead; zero otherwise.
    pub log_correction: f64,
}

/// Core request 10, the hand-off look-ahead, as recorded in handoff.toml. Its presence means
/// every consumer must multiply each row's weight by exp(log_correction).
#[derive(Serialize, Deserialize, Clone, Debug, PartialEq)]
pub struct Lookahead {
    /// Contract version; consumers check it.
    pub version: u32,
    /// Epoch whose data the look-ahead g anticipates (the smoothing horizon), or "file".
    pub horizon: String,
    /// Defensive mixture weight: q is proportional to (1 - defensive) g + defensive.
    pub defensive: f64,
    /// Candidates drawn per hand-off row before the look-ahead draw.
    pub oversample: usize,
    /// "smoothing" (fixed-lag smoothing on candidate tags) or "file" (g supplied per candidate).
    pub g_source: String,
    pub rule: String,
}

pub const LOOKAHEAD_VERSION: u32 = 1;
pub const LOOKAHEAD_RULE: &str = "multiply each row's weight by exp(log_correction); the corrected weights estimate the unproposed hand-off exactly in expectation";

fn is_zero(x: &f64) -> bool {
    *x == 0.0
}

/// One stratum's draws, with its posterior probability and its first row in final.npy.
pub struct Stratum {
    pub mode: usize,
    pub probability: f64,
    pub final_offset: usize,
    pub candidates: Vec<Candidate>,
}

/// Where the filter stopped.
#[derive(Serialize, Deserialize, Clone, Debug, PartialEq, Default)]
pub struct Stop {
    pub epoch: String,
    /// Index of the stop among the filter's steps: the next step's streams are step + 2.
    pub step: usize,
    pub unix_s: f64,
    /// Core request 18 (epoch hand-offs only): each mode's log evidence from the prior to the
    /// end of this epoch, in `filter::MODES` order (minus infinity for a mode not run). This is
    /// the evidence the rows' mode shares were computed from, and it uses no measurement after
    /// the stop. A consumer composing evidence must start from these, not from the final values.
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub log_evidence_by_mode: Option<Vec<f64>>,
    /// The same evidence as mode probabilities (prior mode weights applied).
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub mode_probability: Option<Vec<f64>>,
    /// The replicate's log evidence to the stop, averaged over modes with their prior weights.
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub log_evidence: Option<f64>,
    /// Satcom observations the filter had used by the end of the stop epoch, and those it had
    /// not yet used (for example the 00:19 BTO for a 22:41 stop). A continuing stage may claim
    /// only the second list. Observations claimed by trajectory hypotheses are not listed.
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub observations_used: Option<Vec<String>>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub observations_not_used: Option<Vec<String>>,
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
    /// Core request 10: see [`Lookahead`]. Absent (zero) without the look-ahead.
    #[serde(default, skip_serializing_if = "is_zero")]
    pub log_correction: f64,
}

#[derive(Serialize, Deserialize)]
struct File {
    stop: Stop,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    lookahead: Option<Lookahead>,
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
                log_correction: c.log_correction,
            });
        }
    }
    rows
}

pub fn write(dir: &Path, stop: &Stop, rows: &[Row]) -> Result<(), String> {
    write_with(dir, stop, rows, None)
}

/// As `write`; with the look-ahead, handoff.npy gains a 14th column `log_correction` (so a
/// reader expecting [`COLUMNS`] fails on the shape) and handoff.toml records the contract.
pub fn write_with(dir: &Path, stop: &Stop, rows: &[Row], lookahead: Option<&Lookahead>) -> Result<(), String> {
    let extra = lookahead.is_some();
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
            .into_iter()
            .chain(extra.then_some(r.log_correction))
        })
        .collect();
    write_npy64(&dir.join("handoff.npy"), &[rows.len(), COLUMNS.len() + usize::from(extra)], &values)?;
    let file = File { stop: stop.clone(), lookahead: lookahead.cloned(), row: rows.to_vec() };
    let text = toml::to_string(&file).map_err(|e| format!("handoff.toml: {e}"))?;
    let path = dir.join("handoff.toml");
    std::fs::write(&path, text).map_err(|e| format!("{}: {e}", path.display()))
}

/// Read a hand-off. A hand-off drawn with the look-ahead is refused here (a consumer that
/// ignored the correction would be biased): use [`read_corrected`].
pub fn read(dir: &Path) -> Result<(Stop, Vec<Row>), String> {
    let path = dir.join("handoff.toml");
    let file = read_file(&path)?;
    if file.lookahead.is_some() {
        return Err(format!("{}: drawn with the hand-off look-ahead; read it with read_corrected", path.display()));
    }
    Ok((file.stop, file.row))
}

/// Read a hand-off with or without the look-ahead; each row's weight comes back multiplied by
/// exp(log_correction) and the correction set to zero, so the rows are used as usual.
pub fn read_corrected(dir: &Path) -> Result<(Stop, Option<Lookahead>, Vec<Row>), String> {
    let path = dir.join("handoff.toml");
    let file = read_file(&path)?;
    if let Some(l) = &file.lookahead {
        if l.version != LOOKAHEAD_VERSION {
            return Err(format!("{}: look-ahead contract version {} (this build reads {LOOKAHEAD_VERSION})", path.display(), l.version));
        }
    }
    let rows = file
        .row
        .into_iter()
        .map(|mut r| {
            r.weight *= r.log_correction.exp();
            r.log_correction = 0.0;
            r
        })
        .collect();
    Ok((file.stop, file.lookahead, rows))
}

fn read_file(path: &Path) -> Result<File, String> {
    let text = std::fs::read_to_string(path).map_err(|e| format!("{}: {e}", path.display()))?;
    toml::from_str(&text).map_err(|e| format!("{}: {e}", path.display()))
}
