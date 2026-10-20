//! Display statistics of a finished run: the latitude density, the numbers quoted with
//! it, and the pooling that combines replicates.
//!
//! These are computed once, here, and written to `summary.json`. The report and the app
//! both read that file, so a figure and a panel cannot disagree about the same run.
//!
//! Replicates are combined as one sampler (island estimator): P(mode) comes from the
//! replicate-averaged evidence, and within a mode each replicate is weighted by its own
//! evidence. `pool_factors[replicate][mode]` is the per-particle multiplier that does it.

use crate::config::Config;
use crate::filter::Replicate;
use crate::output::{read_npy_rows, write_json};
use serde::Serialize;
use serde_json::{json, Value};
use std::path::Path;

/// Latitude grid for every density in a summary: degrees, north positive.
pub const GRID_MIN: f64 = -50.0;
pub const GRID_MAX: f64 = 50.0;
pub const GRID_STEP: f64 = 0.05;
/// Gaussian display kernel, in degrees. Densities are smoothed histograms.
pub const SMOOTH_DEG: f64 = 0.1;
/// The published northern shoulder of Davey et al. (2016) Fig. 10.3.
pub const SHOULDER: (f64, f64) = (-36.5, -34.5);
/// Map histogram: cell size and extent (latitude then longitude, degrees).
const MAP_STEP: f64 = 0.25;
const MAP_LAT: (f64, f64) = (-50.0, 10.0);
const MAP_LON: (f64, f64) = (55.0, 125.0);

const COL_WEIGHT: usize = 0;
const COL_LAT: usize = 1;
const COL_LON: usize = 2;
const COL_MACH: usize = 4;
const COL_TAU: usize = 5;
const COL_TURNS: usize = 6;
const COL_MODE: usize = 9;
const COL_STRATUM: usize = 12;

/// Recorded in summary.json when a run predates the `stratum` column and is pooled by its
/// final mode instead, which gives reverted lateral-navigation paths the wrong posterior.
const POOLED_BY_MODE: &str = "final mode (pre-fix run; biased for reverted lateral-navigation paths)";

/// The mode filter a row belongs to, or its final mode for runs without the `stratum` column.
fn stratum(row: &[f64]) -> usize {
    row.get(COL_STRATUM).copied().unwrap_or(row[COL_MODE]) as usize
}

pub fn points() -> usize {
    ((GRID_MAX - GRID_MIN) / GRID_STEP).round() as usize + 1
}

fn grid_value(i: usize) -> f64 {
    GRID_MIN + i as f64 * GRID_STEP
}

/// Rebuild the summary of a finished run from its own artifacts. `reference` supplies the
/// published curve: a run records its inputs relative to the directory it was made from,
/// which need not be the directory this runs in, and older runs did not record it at all.
pub fn rebuild(dir: &Path, reference: Option<std::path::PathBuf>) -> Result<Value, String> {
    let text = std::fs::read_to_string(dir.join("run.json")).map_err(|e| format!("{}: {e}", dir.display()))?;
    let manifest: Value = serde_json::from_str(&text).map_err(|e| format!("{}: {e}", dir.display()))?;
    let mut config: Config = serde_json::from_value(manifest["config"].clone()).map_err(|e| e.to_string())?;
    if let Some(path) = reference.filter(|p| p.is_file()) {
        config.inputs.reference_curve = Some(path);
    }
    let replicates: Vec<Replicate> = serde_json::from_value(manifest["replicates"].clone()).map_err(|e| e.to_string())?;
    write(dir, &config, &replicates)
}

/// Build the summary and write it next to the run artifacts.
pub fn write(out: &Path, config: &Config, replicates: &[Replicate]) -> Result<Value, String> {
    let summary = build(out, config, replicates)?;
    write_json(&out.join("summary.json"), &summary)?;
    Ok(summary)
}

pub fn build(out: &Path, config: &Config, replicates: &[Replicate]) -> Result<Value, String> {
    let reference = match &config.inputs.reference_curve {
        Some(path) => Some(load_reference(path)?),
        None => None,
    };
    let mut cases = Vec::new();
    for case in &config.cases {
        let indices: Vec<usize> = replicates.iter().enumerate().filter(|(_, r)| r.case == case.id).map(|(i, _)| i).collect();
        if indices.is_empty() {
            continue;
        }
        let reps: Vec<&Replicate> = indices.iter().map(|&i| &replicates[i]).collect();
        cases.push(case_summary(out, &case.id, &reps, reference.as_deref())?);
    }
    Ok(json!({
        "reference": reference.as_ref().map(|density| json!({
            "path": config.inputs.reference_curve, "density": round_all(density), "stats": stats(density)})),
        "grid": {"min": GRID_MIN, "max": GRID_MAX, "step": GRID_STEP, "points": points(), "smoothing_deg": SMOOTH_DEG},
        "map": {"lat": [MAP_LAT.0, MAP_LAT.1], "lon": [MAP_LON.0, MAP_LON.1], "step": MAP_STEP},
        "shoulder_interval": [SHOULDER.0, SHOULDER.1],
        "cases": cases,
    }))
}

/// Per-particle multipliers that combine replicates into one weighted sample.
#[derive(Serialize)]
pub struct Pooling {
    /// `[replicate][mode]`: multiply a particle's stored weight by this.
    pub factors: Vec<[f64; 5]>,
    /// P(mode | data) for the pooled sample.
    pub mode_probability: [f64; 5],
}

pub fn pooling(reps: &[&Replicate]) -> Pooling {
    let prior: [f64; 5] = std::array::from_fn(|m| reps[0].modes[m].prior_weight);
    let log_z: Vec<[f64; 5]> = reps.iter().map(|r| std::array::from_fn(|m| r.modes[m].log_evidence)).collect();
    let max = log_z.iter().flatten().copied().fold(f64::NEG_INFINITY, f64::max);
    let z: Vec<[f64; 5]> = log_z.iter().map(|row| std::array::from_fn(|m| (row[m] - max).exp())).collect();

    let mean: [f64; 5] = std::array::from_fn(|m| z.iter().map(|row| row[m]).sum::<f64>() / reps.len() as f64);
    let weighted: [f64; 5] = std::array::from_fn(|m| prior[m] * mean[m]);
    let total: f64 = weighted.iter().sum();
    let mode_probability: [f64; 5] = std::array::from_fn(|m| if total > 0.0 { weighted[m] / total } else { 0.0 });

    // Share of a mode's evidence carried by each replicate; zero where the mode was not run.
    let column: [f64; 5] = std::array::from_fn(|m| z.iter().map(|row| row[m]).sum());
    let factors = (0..reps.len())
        .map(|i| {
            std::array::from_fn(|m| {
                let share = if column[m] > 0.0 { z[i][m] / column[m] } else { 0.0 };
                let within = reps[i].modes[m].posterior_probability;
                mode_probability[m] * share / if within > 0.0 { within } else { 1.0 }
            })
        })
        .collect();
    Pooling { factors, mode_probability }
}

fn case_summary(out: &Path, case: &str, reps: &[&Replicate], reference: Option<&[f64]>) -> Result<Value, String> {
    let pool = pooling(reps);
    let half = reps.len() / 2;
    let halves = (half > 0).then(|| (pooling(&reps[..half]), pooling(&reps[half..])));

    let n = points();
    let mut pooled = vec![0.0; n];
    let mut per_mode = vec![vec![0.0; n]; 5];
    let mut per_replicate = vec![vec![0.0; n]; reps.len()];
    let mut halves_hist = [vec![0.0; n], vec![0.0; n]];
    let mut map = std::collections::BTreeMap::<(i32, i32), f64>::new();
    let mut mach = Histogram::new(0.70, 0.87, 34);
    let mut tau = Histogram::new(0.0, 10.0, 40);
    let mut turns = Histogram::new(-0.5, 9.5, 10);
    let mut shoulder = 0.0;
    let mut south = 0.0;
    let mut north_of_30s = 0.0;
    let mut mass = 0.0;
    let mut by_final_mode = false;

    for (i, replicate) in reps.iter().enumerate() {
        let path = out.join(case).join(format!("seed-{}", replicate.seed)).join("final.npy");
        let factors = pool.factors[i];
        let half_factors = halves.as_ref().map(|(a, b)| if i < half { a.factors[i] } else { b.factors[i - half] });
        read_npy_rows(&path, |row| {
            by_final_mode |= row.len() <= COL_STRATUM;
            let mode = stratum(row);
            let w = row[COL_WEIGHT] * factors[mode];
            let lat = row[COL_LAT];
            if let Some(bin) = grid_bin(lat) {
                pooled[bin] += w;
                per_mode[mode][bin] += w;
                per_replicate[i][bin] += row[COL_WEIGHT];
                if let Some(f) = half_factors {
                    halves_hist[usize::from(i >= half)][bin] += row[COL_WEIGHT] * f[mode];
                }
            }
            if let Some(cell) = map_cell(lat, row[COL_LON]) {
                *map.entry(cell).or_default() += w;
            }
            mach.add(row[COL_MACH], w);
            tau.add(row[COL_TAU], w);
            turns.add(row[COL_TURNS], w);
            mass += w;
            shoulder += if (SHOULDER.0..SHOULDER.1).contains(&lat) { w } else { 0.0 };
            south += if lat < 0.0 { w } else { 0.0 };
            north_of_30s += if lat > -30.0 { w } else { 0.0 };
        })?;
    }

    let density = smooth_to_density(&pooled);
    let mode_curves: Vec<Value> = per_mode
        .iter()
        .enumerate()
        .map(|(m, hist)| {
            let d = smooth_to_density(hist);
            json!({"mode": hypothesis::MODES[m], "probability": pool.mode_probability[m],
                   "density": round_all(&d), "stats": stats(&d)})
        })
        .collect();
    let replicate_curves: Vec<Value> = per_replicate
        .iter()
        .enumerate()
        .map(|(i, hist)| {
            let d = smooth_to_density(hist);
            json!({"seed": reps[i].seed, "stats": stats(&d), "density": round_all(&d),
                   "log_evidence": reps[i].log_evidence,
                   "mode_probability": reps[i].modes.iter().map(|m| m.posterior_probability).collect::<Vec<_>>(),
                   "final_ess": reps[i].modes.iter().map(|m| m.final_ess).collect::<Vec<_>>()})
        })
        .collect();
    let split_half = halves
        .is_some()
        .then(|| overlap(&smooth_to_density(&halves_hist[0]), &smooth_to_density(&halves_hist[1])));

    let map_cells: Vec<Value> = map
        .iter()
        .filter(|(_, &v)| v > 0.0)
        .map(|(&(y, x), &v)| json!([y, x, round(v / mass.max(f64::MIN_POSITIVE) / (MAP_STEP * MAP_STEP))]))
        .collect();

    Ok(json!({
        "case": case,
        "seeds": reps.iter().map(|r| r.seed).collect::<Vec<_>>(),
        "particles": reps[0].particles_per_mode.iter().sum::<usize>(),
        "log_evidence": reps.iter().map(|r| r.log_evidence).sum::<f64>() / reps.len() as f64,
        "mode_probability": pool.mode_probability,
        "pool_factors": pool.factors,
        "pooled_by": if by_final_mode { POOLED_BY_MODE } else { "stratum" },
        "density": round_all(&density),
        "stats": stats(&density),
        "split_half_overlap": split_half,
        "reference_overlap": reference.map(|r| overlap(&density, r)),
        "probability": {
            "shoulder": shoulder / mass,
            "south_of_equator": south / mass,
            "north_of_30s": north_of_30s / mass,
        },
        "mach": mach.json(),
        "tau_h": tau.json(),
        "turns": turns.json(),
        "map": map_cells,
        "modes": mode_curves,
        "replicates": replicate_curves,
    }))
}

/// Quantiles by interpolating the density's cdf, and the grid point of highest density.
///
/// Each grid point is the centre of a bin one step wide, so the cumulative sum through
/// bin k is the probability below that bin's upper edge, not below its centre. The
/// quantiles are interpolated against those edges; reading the same cumulative sum
/// against the centres instead puts every quantile half a step (0.025 deg) too far south.
pub fn stats(density: &[f64]) -> Value {
    let upper_edge = |k: usize| grid_value(k) + GRID_STEP / 2.0;
    let mut cdf = Vec::with_capacity(density.len());
    let mut acc = 0.0;
    for d in density {
        acc += d * GRID_STEP;
        cdf.push(acc);
    }
    let q = |p: f64| -> f64 {
        match cdf.iter().position(|&c| c >= p) {
            None => upper_edge(density.len() - 1),
            Some(k) => {
                // Below the first bin's upper edge, the cdf runs from zero at its lower edge.
                let (below, x) = if k == 0 { (0.0, GRID_MIN - GRID_STEP / 2.0) } else { (cdf[k - 1], upper_edge(k - 1)) };
                let t = if cdf[k] > below { (p - below) / (cdf[k] - below) } else { 0.0 };
                x + t * GRID_STEP
            }
        }
    };
    let peak = density.iter().enumerate().fold((0, f64::NEG_INFINITY), |a, (i, &d)| if d > a.1 { (i, d) } else { a }).0;
    json!({"q025": q(0.025), "median": q(0.5), "q975": q(0.975), "mode": grid_value(peak)})
}

/// Integrated overlap of two densities on the shared grid, in [0, 1].
pub fn overlap(p: &[f64], q: &[f64]) -> f64 {
    p.iter().zip(q).map(|(a, b)| a.min(*b)).sum::<f64>() * GRID_STEP
}

/// Smooth a weighted histogram with the display kernel and normalise it to a density.
fn smooth_to_density(hist: &[f64]) -> Vec<f64> {
    let half = (4.0 * SMOOTH_DEG / GRID_STEP).round() as isize;
    let kernel: Vec<f64> = (-half..=half).map(|k| (-0.5 * (k as f64 * GRID_STEP / SMOOTH_DEG).powi(2)).exp()).collect();
    let norm: f64 = kernel.iter().sum();
    let mut out = vec![0.0; hist.len()];
    for (i, value) in hist.iter().enumerate() {
        if *value == 0.0 {
            continue;
        }
        for (k, weight) in kernel.iter().enumerate() {
            let j = i as isize + k as isize - half;
            if (0..hist.len() as isize).contains(&j) {
                out[j as usize] += value * weight / norm;
            }
        }
    }
    let total: f64 = out.iter().sum::<f64>() * GRID_STEP;
    if total > 0.0 {
        for v in &mut out {
            *v /= total;
        }
    }
    out
}

fn grid_bin(lat: f64) -> Option<usize> {
    let bin = ((lat - GRID_MIN + GRID_STEP / 2.0) / GRID_STEP).floor();
    (bin >= 0.0 && (bin as usize) < points()).then_some(bin as usize)
}

fn map_cell(lat: f64, lon: f64) -> Option<(i32, i32)> {
    let inside = (MAP_LAT.0..MAP_LAT.1).contains(&lat) && (MAP_LON.0..MAP_LON.1).contains(&lon);
    inside.then(|| (((lat - MAP_LAT.0) / MAP_STEP).floor() as i32, ((lon - MAP_LON.0) / MAP_STEP).floor() as i32))
}

struct Histogram {
    min: f64,
    step: f64,
    counts: Vec<f64>,
}

impl Histogram {
    fn new(min: f64, max: f64, bins: usize) -> Self {
        Histogram { min, step: (max - min) / bins as f64, counts: vec![0.0; bins] }
    }
    fn add(&mut self, value: f64, weight: f64) {
        let bin = ((value - self.min) / self.step).floor();
        if bin >= 0.0 && (bin as usize) < self.counts.len() {
            self.counts[bin as usize] += weight;
        }
    }
    fn json(&self) -> Value {
        let total: f64 = self.counts.iter().sum();
        let scale = if total > 0.0 { 1.0 / total } else { 0.0 };
        json!({"min": self.min, "step": self.step,
               "probability": self.counts.iter().map(|c| round(c * scale)).collect::<Vec<_>>()})
    }
}

fn round(v: f64) -> f64 {
    // Nine decimals: far below anything the report or the app prints, and it keeps
    // summary.json compact enough to read.
    let scaled = (v * 1e9).round() / 1e9;
    if scaled == 0.0 {
        0.0
    } else {
        scaled
    }
}

fn round_all(values: &[f64]) -> Vec<f64> {
    values.iter().map(|v| round(*v)).collect()
}

/// Digitised published curve: `latitude,density` with a header line, interpolated onto the grid.
pub fn load_reference(path: &Path) -> Result<Vec<f64>, String> {
    let text = std::fs::read_to_string(path).map_err(|e| format!("{}: {e}", path.display()))?;
    let curve: Vec<(f64, f64)> = text
        .lines()
        .skip(1)
        .filter_map(|line| {
            let mut fields = line.split(',');
            let lat = fields.next()?.trim().parse().ok()?;
            let density = fields.next()?.trim().parse().ok()?;
            Some((lat, density))
        })
        .collect();
    if curve.len() < 2 {
        return Err(format!("{}: fewer than two points", path.display()));
    }
    let mut out = vec![0.0; points()];
    for (i, value) in out.iter_mut().enumerate() {
        let x = grid_value(i);
        *value = match curve.iter().position(|(lat, _)| *lat >= x) {
            None | Some(0) => 0.0,
            Some(k) => {
                let ((x0, y0), (x1, y1)) = (curve[k - 1], curve[k]);
                if x < curve[0].0 {
                    0.0
                } else {
                    y0 + (y1 - y0) * (x - x0) / (x1 - x0)
                }
            }
        };
    }
    let total: f64 = out.iter().sum::<f64>() * GRID_STEP;
    if total > 0.0 {
        for v in &mut out {
            *v /= total;
        }
    }
    Ok(out)
}

#[cfg(test)]
mod tests {
    use super::*;

    /// A Gaussian recovers its own quantiles: median zero, 95% interval +/- 1.96 sd.
    #[test]
    fn stats_match_an_independently_known_distribution() {
        let sd = 2.0;
        let mut hist = vec![0.0; points()];
        for (i, h) in hist.iter_mut().enumerate() {
            *h = (-0.5 * (grid_value(i) / sd).powi(2)).exp();
        }
        let density = smooth_to_density(&hist);
        let s = stats(&density);
        let get = |k: &str| s[k].as_f64().unwrap();
        // Smoothing adds its own 0.1 deg in quadrature: sqrt(4 + 0.01) = 2.0025.
        let spread = 1.959_964 * 2.0025;
        assert!(get("median").abs() < 1e-3, "median {}", get("median"));
        assert!((get("q975") - spread).abs() < 5e-3, "q975 {}", get("q975"));
        assert!((get("q025") + spread).abs() < 5e-3, "q025 {}", get("q025"));
        assert!((overlap(&density, &density) - 1.0).abs() < 1e-9);
    }

    /// Two densities one standard deviation apart overlap by 2 Phi(-1/2) = 0.6171.
    #[test]
    fn overlap_matches_the_analytic_value() {
        let gaussian = |mean: f64| {
            let mut hist = vec![0.0; points()];
            for (i, h) in hist.iter_mut().enumerate() {
                *h = (-0.5 * (grid_value(i) - mean).powi(2)).exp();
            }
            smooth_to_density(&hist)
        };
        assert!((overlap(&gaussian(0.0), &gaussian(1.0)) - 0.617_075).abs() < 2e-3);
    }
}
