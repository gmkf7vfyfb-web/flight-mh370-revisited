//! Streaming wreckage draws to a consumer (core request 12, ruled 9 Oct: STREAM, DO NOT STORE).
//!
//! The runner hook that will carry this is a `crates/hypothesis` change owned by core and not yet
//! built. This file is settling's side of it, against a STUB of that hook
//! (`WreckageConsumerStub`), so the producer drops in when core lands request 12: replace the stub
//! trait by core's and keep `stream_impact`.
//!
//! What the producer guarantees, and the driver relies on:
//! - a draw is ONE whole-field configuration W (one family, one ocean realisation, every class),
//!   with weight 1 / N of its impact sample; the consumer's per-draw value is AVERAGED over draws,
//!   never multiplied (draws are alternative outcomes, not extra wreckage);
//! - draw d depends only on (impact, d), so refinement emits only new indices and the earlier
//!   draws are unchanged (`Settling::emit_with` on an index range);
//! - values are averaged BEFORE any log or normalisation (searched-areas brief: average likelihoods
//!   before normalising).
//!
//! Draw count, adaptively by integration error (the searched-areas specification settling was told
//! to build to): 512 pilot draws, doubling to at most 4,096 until the 95% half-width of the mean is
//! within `abs_tol` (0.02 in non-detection probability), switching to a RELATIVE target
//! `rel_tol x mean` where the mean is small (below abs_tol / rel_tol). A case that does not meet
//! the target at the maximum is reported UNCONVERGED, never smoothed (contract rule 7).
//! `rel_tol` = 0.2 is settling's declared default; searched areas may set its own.

use super::{Settling, WreckageElement};
use hypothesis::ImpactView;

/// STUB of the core request-12 consumer hook: the consumer's value for one wreckage draw, for
/// example P(no detection | W, search record). Replaced by core's hook when it lands.
pub trait WreckageConsumerStub {
    fn draw_value(&self, impact: &ImpactView, draw: &[WreckageElement]) -> f64;
}

#[derive(Debug, Clone, Copy, PartialEq)]
pub struct StreamPolicy {
    pub pilot_draws: usize,
    pub max_draws: usize,
    pub abs_tol: f64,
    pub rel_tol: f64,
    /// Keep every emitted row (only for the declared handful of representative impacts).
    pub keep_rows: bool,
}

impl Default for StreamPolicy {
    fn default() -> Self {
        StreamPolicy { pilot_draws: 512, max_draws: 4096, abs_tol: 0.02, rel_tol: 0.2, keep_rows: false }
    }
}

/// Per-impact result: this is what the runner stores (plus `rows` for representative impacts).
#[derive(Debug, Clone, PartialEq)]
pub struct StreamResult {
    /// Mean of the consumer's per-draw value over all draws used.
    pub mean: f64,
    /// 95% half-width of that mean, from the between-draw spread.
    pub half_width_95: f64,
    pub draws: usize,
    pub converged: bool,
    /// Mean element rows per draw (the storage that streaming avoids).
    pub rows_per_draw: f64,
    pub rows: Vec<WreckageElement>,
}

/// Stream the draws of one impact to `consumer`, refining adaptively. `family`: the impact's
/// `debris_class` when the caller has it (see `Settling::emit_with`).
pub fn stream_impact(
    settling: &Settling,
    impact: &ImpactView,
    family: Option<usize>,
    consumer: &dyn WreckageConsumerStub,
    policy: &StreamPolicy,
) -> Result<StreamResult, String> {
    if policy.pilot_draws < 2 || policy.max_draws < policy.pilot_draws || !(policy.abs_tol > 0.0) || !(policy.rel_tol > 0.0) {
        return Err("stream: pilot >= 2, max >= pilot, positive tolerances".into());
    }
    let (mut sum, mut sum2, mut n, mut rows_total) = (0.0, 0.0, 0usize, 0usize);
    let mut kept = Vec::new();
    let mut target = policy.pilot_draws;
    loop {
        // Emit only the new indices; each draw's weight is fixed when the total is known, so the
        // per-draw value is accumulated unweighted and averaged at the end.
        let rows = settling.emit_with(impact, n..target, 1.0, family)?;
        rows_total += rows.len();
        let mut start = 0;
        for d in n..target {
            let end = start + rows[start..].iter().take_while(|r| r.draw as usize == d).count();
            let v = consumer.draw_value(impact, &rows[start..end]);
            if !v.is_finite() {
                return Err(format!("stream: consumer returned {v} for draw {d}"));
            }
            sum += v;
            sum2 += v * v;
            start = end;
        }
        if policy.keep_rows {
            kept.extend(rows);
        }
        n = target;
        let mean = sum / n as f64;
        let var = ((sum2 - n as f64 * mean * mean) / (n as f64 - 1.0)).max(0.0);
        let hw = 1.96 * (var / n as f64).sqrt();
        let tol = policy.abs_tol.min(policy.rel_tol * mean.abs());
        let converged = hw <= tol || var == 0.0;
        if converged || n >= policy.max_draws {
            for r in kept.iter_mut() {
                r.draw_weight = 1.0 / n as f64;
            }
            return Ok(StreamResult { mean, half_width_95: hw, draws: n, converged, rows_per_draw: rows_total as f64 / n as f64, rows: kept });
        }
        target = (2 * n).min(policy.max_draws);
    }
}

/// PLACEHOLDER consumer for tests and plumbing only - NOT searched areas' detection model, which
/// is that module's to build. A rectangular searched box (east/north metres from the impact) in
/// which each settled piece of area >= `min_area_m2` is detected independently with probability
/// `q`; P(no detection | W) = product over those pieces of (1 - q)^multiplicity. Pieces of ONE
/// configuration multiply; configurations (draws) average - the distinction the averaging test
/// checks.
pub struct BoxSearchPlaceholder {
    pub east_m: [f64; 2],
    pub north_m: [f64; 2],
    pub min_area_m2: f64,
    pub q: f64,
}

impl WreckageConsumerStub for BoxSearchPlaceholder {
    fn draw_value(&self, _impact: &ImpactView, draw: &[WreckageElement]) -> f64 {
        let ln_miss: f64 = draw
            .iter()
            .filter(|r| r.fate == super::Fate::Settled && r.piece_area_m2 >= self.min_area_m2)
            .filter(|r| (self.east_m[0]..=self.east_m[1]).contains(&r.east_m) && (self.north_m[0]..=self.north_m[1]).contains(&r.north_m))
            .map(|r| r.multiplicity * (1.0 - self.q).ln())
            .sum();
        ln_miss.exp()
    }
}
