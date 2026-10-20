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
    /// Core request 19: the route from the prior epoch to the stop (output.handoff_routes).
    pub route: Option<Vec<[f32; 2]>>,
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
    /// Core request 19: written to routes.npy, not to handoff.toml.
    #[serde(skip)]
    pub route: Option<Vec<[f32; 2]>>,
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
                route: c.route.clone(),
            });
        }
    }
    rows
}

/// Contract version of the northern supplement (supplement.json, mis.npy, production-mis.npy).
pub const SUPPLEMENT_VERSION: u32 = 1;

/// Per-mode record of a supplement draw (supplement.json).
#[derive(Serialize, Clone, Debug)]
pub struct SupplementMode {
    pub mode: usize,
    /// P(mode | data to the epoch), as the normal hand-off.
    pub probability: f64,
    /// Candidate (look-ahead) rows the draws come from, N_s.
    pub candidates: usize,
    /// Rows of this mode in the normal hand-off, K_s (0 if the mode has none).
    pub production_rows: usize,
    /// Rows of this mode in the supplement, K2_s.
    pub supplement_rows: usize,
    /// Mean of r over the candidates, rbar_s.
    pub mean_r: f64,
}

/// What a supplement draw used and how to combine it (written to supplement.json).
#[derive(Serialize, Clone, Debug)]
pub struct SupplementInfo {
    pub version: u32,
    pub epoch: String,
    pub rows: usize,
    pub defensive: f64,
    pub edges_deg: Vec<f64>,
    /// Normalised target shares per bin.
    pub target: Vec<f64>,
    /// Posterior probability of each bin at the epoch, p_b.
    pub posterior_bin_probability: Vec<f64>,
    /// h_b = target_b / p_b (0 where p_b = 0).
    pub h: Vec<f64>,
    /// H = sum of target_b over bins with p_b > 0.
    pub h_norm: f64,
    pub modes: Vec<SupplementMode>,
    pub r_rule: String,
    pub rho_rule: String,
    pub standalone_rule: String,
    pub mis_rule: String,
}

/// The tilt r(lat) of a supplement draw.
pub fn supplement_r(lat: f64, defensive: f64, edges: &[f64], h: &[f64], h_norm: f64) -> f64 {
    let flat = if lat >= edges[0] && lat < edges[edges.len() - 1] {
        let b = edges.partition_point(|&e| e <= lat) - 1;
        h[b] / h_norm
    } else {
        0.0
    };
    defensive + (1.0 - defensive) * flat
}

/// The northern supplement draw (config::HandoffSupplement). `strata` are the same per-mode
/// candidates the normal hand-off was selected from, and `k`/`floor` its row count and floor,
/// so each mode's normal row count K_s is known; `production` are the normal rows. Returns the
/// supplement rows, ln rho for each of them, ln rho for each normal row, and the record.
pub fn supplement(
    strata: &[Stratum],
    production: &[Row],
    k: usize,
    floor: usize,
    rows: usize,
    defensive: f64,
    edges: &[f64],
    target_raw: &[f64],
    epoch: &str,
    rng: &mut impl Rng,
) -> Result<(Vec<Row>, Vec<f64>, Vec<f64>, SupplementInfo), String> {
    let nb = target_raw.len();
    let tsum: f64 = target_raw.iter().sum();
    let target: Vec<f64> = target_raw.iter().map(|t| t / tsum).collect();
    let bin = |lat: f64| -> Option<usize> {
        (lat >= edges[0] && lat < edges[nb]).then(|| edges.partition_point(|&e| e <= lat) - 1)
    };
    // Posterior bin probabilities from the candidates: each candidate of mode s has base mass
    // P(s) / N_s (its look-ahead correction stays a multiplier, exactly as in the normal draw).
    let mut p = vec![0.0f64; nb];
    for s in strata.iter().filter(|s| s.probability > 0.0 && !s.candidates.is_empty()) {
        let w = s.probability / s.candidates.len() as f64;
        for c in &s.candidates {
            if let Some(b) = bin(c.aircraft.lat) {
                p[b] += w;
            }
        }
    }
    let h: Vec<f64> = target.iter().zip(&p).map(|(t, pb)| if *pb > 0.0 { t / pb } else { 0.0 }).collect();
    let h_norm: f64 = target.iter().zip(&p).filter(|(_, pb)| **pb > 0.0).map(|(t, _)| t).sum();
    if !(h_norm > 0.0) {
        return Err(format!("output.handoff_supplement: no candidate at {epoch} lies in any target bin"));
    }
    let r_of = |lat: f64| supplement_r(lat, defensive, edges, &h, h_norm);
    let mut out = Vec::new();
    let mut log_rho = Vec::new();
    let mut modes = Vec::new();
    let mut rho_factor = vec![f64::NAN; strata.iter().map(|s| s.mode + 1).max().unwrap_or(0)];
    for s in strata {
        let drawn = s.candidates.len();
        if s.probability <= 0.0 || drawn == 0 {
            continue;
        }
        // The normal hand-off's count for this mode, exactly as `select` computes it.
        let keep = ((k as f64 * s.probability).round() as usize).max(floor).clamp(1, drawn);
        let r: Vec<f64> = s.candidates.iter().map(|c| r_of(c.aircraft.lat)).collect();
        let rsum: f64 = r.iter().sum();
        let rbar = rsum / drawn as f64;
        let keep2 = ((rows as f64 * s.probability * rbar).round() as usize).max(1);
        let log_q: Vec<f64> = r.iter().map(|x| (x / rsum).ln()).collect();
        // rho = q_supp / q_prod per candidate = (K2_s r / (N_s rbar)) / (K_s / N_s).
        let factor = keep2 as f64 / (keep as f64 * rbar);
        rho_factor[s.mode] = factor;
        for j in crate::filter::systematic_resample(&log_q, keep2, rng) {
            let c = &s.candidates[j];
            out.push(Row {
                weight: s.probability / keep2 as f64,
                mode: s.mode,
                alternative: 0,
                particle: c.particle,
                final_row: NO_FINAL_ROW,
                origin: c.origin,
                bias: Bias { mean_hz: c.bias.mean_hz, variance_hz2: c.bias.variance_hz2 },
                aircraft: c.aircraft.clone(),
                log_correction: c.log_correction + rbar.ln() - r[j].ln(),
                route: None,
            });
            log_rho.push((factor * r[j]).ln());
        }
        modes.push(SupplementMode { mode: s.mode, probability: s.probability, candidates: drawn, production_rows: keep, supplement_rows: keep2, mean_r: rbar });
    }
    let production_log_rho = production
        .iter()
        .map(|row| {
            let f = rho_factor.get(row.mode).copied().unwrap_or(f64::NAN);
            (f * r_of(row.aircraft.lat)).ln()
        })
        .collect();
    let info = SupplementInfo {
        version: SUPPLEMENT_VERSION,
        epoch: epoch.to_string(),
        rows,
        defensive,
        edges_deg: edges.to_vec(),
        target,
        posterior_bin_probability: p,
        h,
        h_norm,
        modes,
        r_rule: "r(lat) = defensive + (1 - defensive) * h[bin(lat)] / h_norm, with h = 0 outside edges_deg; bins are [edges[i], edges[i+1])".into(),
        rho_rule: "rho = q_supp / q_prod = supplement_rows_s / (production_rows_s * mean_r_s) * r(lat), for a row of mode s at latitude lat (handoff.npy column latitude_deg)".into(),
        standalone_rule: "the supplement alone: multiply each row's weight by exp(log_correction), as for the normal hand-off (handoff::read_corrected)".into(),
        mis_rule: "with the normal hand-off of the SAME replicate (balance heuristic): normal row weight * exp(log_correction) / (1 + rho); supplement row weight * exp(log_correction) * rho / (1 + rho); rho = exp(production-mis.npy) and exp(mis.npy), row-aligned".into(),
    };
    Ok((out, log_rho, production_log_rho, info))
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

#[cfg(test)]
mod tests {
    use super::*;

    fn test_strata() -> Vec<Stratum> {
        use rand::SeedableRng;
        let q = flight::Parameters::default();
        let prior = flight::Prior {
            unix_s: 0.0, lat: -30.0, lon: 95.0, position_sd_nm: 0.0, track_deg: 180.0, track_sd_deg: 0.0,
            mach_range: (0.73, 0.84), mach_gaussian: None, altitude_levels: flight::Prior::uniform_altitude_levels(&q),
        };
        let a = Aircraft::sample(&prior, flight::Mode::TrueTrack, &q, &flight::environment::CalmAir, &mut rand_chacha::ChaCha8Rng::seed_from_u64(1));
        let make = |mode: usize, p: f64, n: usize, south: f64, span: f64| {
            let candidates = (0..n)
                .map(|i| {
                    let mut x = a.clone();
                    // Deterministic spread, denser in the south as the real posterior is.
                    let u = (i as f64 + 0.5) / n as f64;
                    x.lat = south + span * u * u;
                    Candidate { particle: i, aircraft: x, bias: BfoBias { mean_hz: 150.0, variance_hz2: 4.0 }, origin: i as u32,
                                log_correction: 0.3 * ((i * 7919 % 13) as f64 / 13.0 - 0.5), route: None }
                })
                .collect();
            Stratum { mode, probability: p, final_offset: 0, candidates }
        };
        vec![make(0, 0.62, 300, -38.0, 14.0), make(1, 0.0, 50, -38.0, 10.0), make(2, 0.38, 200, -36.0, 17.0)]
    }

    fn exact(strata: &[Stratum], f: impl Fn(f64) -> f64) -> f64 {
        strata.iter().filter(|s| s.probability > 0.0)
            .map(|s| s.probability / s.candidates.len() as f64 * s.candidates.iter().map(|c| c.log_correction.exp() * f(c.aircraft.lat)).sum::<f64>())
            .sum()
    }

    fn copy(strata: &[Stratum]) -> Vec<Stratum> {
        strata.iter().map(|s| Stratum { mode: s.mode, probability: s.probability, final_offset: 0, candidates: s.candidates.clone() }).collect()
    }

    /// Run-J northern supplement: the corrected supplement rows alone, and the balance-heuristic
    /// combination with the normal rows, both estimate the hand-off posterior exactly (in
    /// expectation over the draw), for f = 1, latitude and a northern indicator; the tilt has
    /// posterior mean exactly 1; and the rows are moved north.
    #[test]
    fn supplement_is_exact_alone_and_combined() {
        use rand::SeedableRng;
        let strata = test_strata();
        let (edges, target) = (vec![-34.0, -30.0, -26.0, -22.0], vec![0.5, 0.35, 0.15]);
        let fs: [(&str, fn(f64) -> f64); 3] = [("one", |_| 1.0), ("lat", |x| x), ("north", |x| if x > -30.0 { 1.0 } else { 0.0 })];
        let reps = 3000;
        let (mut alone, mut mis) = ([0.0f64; 3], [0.0f64; 3]);
        let mut north_share = 0.0;
        for rep in 0..reps {
            let mut rng = rand_chacha::ChaCha8Rng::seed_from_u64(1000 + rep);
            let prod = select(copy(&strata), 40, 5, &mut rng);
            let (srows, lr, plr, info) = supplement(&strata, &prod, 40, 5, 60, 0.2, &edges, &target, "m0011", &mut rng).unwrap();
            if rep == 0 {
                let mean: f64 = info.modes.iter().map(|m| m.probability * m.mean_r).sum();
                assert!((mean - 1.0).abs() < 1e-12, "posterior mean of r {mean}");
                assert_eq!(lr.len(), srows.len());
                assert_eq!(plr.len(), prod.len());
                assert!(plr.iter().all(|x| x.is_finite()) && lr.iter().all(|x| x.is_finite()));
            }
            north_share += srows.iter().filter(|r| r.aircraft.lat > -30.0).count() as f64 / srows.len() as f64 / reps as f64;
            for (i, (_, f)) in fs.iter().enumerate() {
                alone[i] += srows.iter().map(|r| r.weight * r.log_correction.exp() * f(r.aircraft.lat)).sum::<f64>() / reps as f64;
                let a: f64 = prod.iter().zip(&plr).map(|(r, l)| r.weight * r.log_correction.exp() / (1.0 + l.exp()) * f(r.aircraft.lat)).sum();
                let b: f64 = srows.iter().zip(&lr).map(|(r, l)| { let rho = l.exp(); r.weight * r.log_correction.exp() * rho / (1.0 + rho) * f(r.aircraft.lat) }).sum();
                mis[i] += (a + b) / reps as f64;
            }
        }
        for (i, (name, f)) in fs.iter().enumerate() {
            let e = exact(&strata, f);
            let tol = 0.004 * e.abs().max(0.05);
            assert!((alone[i] - e).abs() < tol, "{name}: supplement alone {} against exact {e}", alone[i]);
            assert!((mis[i] - e).abs() < tol, "{name}: combined {} against exact {e}", mis[i]);
        }
        let prior_north = exact(&strata, |x| if x > -30.0 { 1.0 } else { 0.0 }) / exact(&strata, |_| 1.0);
        // Expected share north of 30 S: defensive x posterior + (1 - defensive) x target share (0.35 + 0.15).
        let expected = 0.2 * prior_north + 0.8 * 0.5;
        assert!((north_share - expected).abs() < 0.01, "supplement north share {north_share} against {expected} (posterior {prior_north})");
    }

    /// rho for a normal row is the same function of mode and latitude as for a supplement row.
    #[test]
    fn supplement_rho_is_one_function_of_mode_and_latitude() {
        use rand::SeedableRng;
        let strata = test_strata();
        let (edges, target) = (vec![-34.0, -30.0, -26.0, -22.0], vec![0.5, 0.35, 0.15]);
        let mut rng = rand_chacha::ChaCha8Rng::seed_from_u64(7);
        let prod = select(copy(&strata), 40, 5, &mut rng);
        let (srows, lr, plr, info) = supplement(&strata, &prod, 40, 5, 60, 0.2, &edges, &target, "m0011", &mut rng).unwrap();
        let rho = |mode: usize, lat: f64| {
            let m = info.modes.iter().find(|m| m.mode == mode).unwrap();
            m.supplement_rows as f64 / (m.production_rows as f64 * m.mean_r) * supplement_r(lat, info.defensive, &info.edges_deg, &info.h, info.h_norm)
        };
        for (r, l) in prod.iter().zip(&plr).chain(srows.iter().zip(&lr)) {
            assert!((rho(r.mode, r.aircraft.lat).ln() - l).abs() < 1e-12);
        }
        // A mode with zero probability gets no supplement rows.
        assert!(srows.iter().all(|r| r.mode != 1));
    }

    #[test]
    fn supplement_config_is_validated() {
        let ok = crate::config::HandoffSupplement { epoch: "m0011".into(), rows: 10, defensive: 0.1, edges_deg: vec![-35.0, -30.0, -20.0], target: vec![0.5, 0.5] };
        let epochs = vec!["m2241".to_string(), "m0011".to_string()];
        assert!(ok.validate(&epochs).is_ok());
        let bad = |f: &dyn Fn(&mut crate::config::HandoffSupplement)| { let mut c = ok.clone(); f(&mut c); c.validate(&epochs).is_err() };
        assert!(bad(&|c| c.epoch = "m0019a".into()));
        assert!(bad(&|c| c.rows = 0));
        assert!(bad(&|c| c.defensive = 0.0));
        assert!(bad(&|c| c.edges_deg = vec![-30.0, -35.0, -20.0]));
        assert!(bad(&|c| c.target = vec![1.0]));
        assert!(bad(&|c| c.target = vec![0.0, 0.0]));
    }

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
}
