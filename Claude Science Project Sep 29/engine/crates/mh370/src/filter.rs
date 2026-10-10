//! The particle filter: one filter per autopilot mode, combined by evidence.
//!
//! Each filter draws particles from the prior, propagates them with the flight spoke to
//! each step, weights them with the satcom spoke (BTO Gaussian; BFO marginalised over a
//! per-particle Kalman bias) and with any enabled hypotheses, and resamples
//! systematically when the effective sample size is low.
//!
//! Davey et al. (2016, sec. 10.4) warn that conventional resampling collapses static
//! parameters onto a few values; their variable-rate branching avoids it. Here the two
//! static parameters are handled exactly instead: the autopilot mode is stratified,
//! P(mode | data) ~ prior weight x Z_mode, and the manoeuvre time constant is
//! Gibbs-refreshed from its path conditional after every resampling step.

use crate::config::{Case, Config};
use crate::handoff;
use crate::output::write_npy;
use flight::environment::{Environment, Gridded};
use flight::{Aircraft, Mode, Parameters, Prior};
use hypothesis::{EpochView, Hypothesis, StateView};
use rand::{Rng, SeedableRng};
use rand_chacha::ChaCha8Rng;
use rayon::prelude::*;
use satcom::{bfo_without_bias_hz, bto_us, gaussian_log_likelihood, BfoBias, Epoch};
use serde::{Deserialize, Serialize};
use std::path::Path;
use std::sync::atomic::{AtomicBool, Ordering};
use std::time::Instant;

pub const MAX_ROUTE_POINTS: usize = 64;
/// Memory a particle occupies while a filter runs; the app estimates run size from it.
pub const PARTICLE_BYTES: usize = std::mem::size_of::<Particle>();
/// `mode` is the autopilot mode the particle is flying at the end, which differs from its
/// stratum once a lateral-navigation path has reverted to heading hold. `stratum` is the
/// mode filter the particle belongs to: weights and pooling use it.
pub const FINAL_COLUMNS: [&str; 21] = [
    "weight", "latitude_deg", "longitude_deg", "altitude_ft", "mach", "tau_h", "turns", "accelerations", "climbs", "mode",
    "bfo_bias_hz", "origin", "stratum",
    // NaN throughout when the run does not model fuel. `fuel_exhausted_unix_s` is NaN for a
    // path that still had fuel at the final step; the two coverage columns say how many seconds
    // of the path were flown where the tables needed clamping or extrapolating.
    "fuel_kg", "fuel_exhausted_unix_s", "fuel_below_tables_s", "fuel_extrapolated_s",
    "fuel_above_ceiling_s",
    // Any nonzero fuel_no_flow_s is a defect: the tables returned no flow and the step burnt
    // nothing. fuel_no_flow_cause codes why - 1 flight level, 2 Mach, 3 weight, 4 the tables.
    "fuel_no_flow_s", "fuel_no_flow_cause",
    // Fuel audit F12: final.npy is float32, which holds `fuel_exhausted_unix_s` only to 128 s.
    // This is the same instant as seconds after FINAL_TIME_ORIGIN_UNIX_S (2014-03-08 00:00:00
    // UTC; negative before midnight), resolved to better than 1 ms. Use it for any timing.
    "fuel_exhausted_s_after_0000",
];

/// Origin of final.npy's `*_s_after_0000` columns: 2014-03-08 00:00:00 UTC, the convention of
/// the compact run C files (end of flight's impacts32, core's tanks32).
pub const FINAL_TIME_ORIGIN_UNIX_S: f64 = 1_394_236_800.0;

/// A time at which the filter stops and weights particles: a SATCOM epoch, or an epoch
/// requested by a hypothesis.
pub struct Step {
    pub id: String,
    pub unix_s: f64,
    pub satcom: Option<Epoch>,
}

/// Everything a filter run shares. `E` is the weather source: the gridded ERA5/IGRF fields in
/// runs, still air in tests.
pub struct Context<'a, E = Gridded> {
    pub config: &'a Config,
    pub params: &'a Parameters,
    pub prior: &'a Prior,
    pub mode_weights: [f64; 5],
    pub steps: &'a [Step],
    pub environment: &'a E,
    pub hypotheses: &'a [Box<dyn Hypothesis>],
    pub route_points: usize,
    /// Called after every filtered step. The app draws its progress from this; it observes
    /// the filter and cannot change it.
    pub progress: Option<&'a (dyn Fn(&Progress) + Sync)>,
    /// Set by the app to stop a run between steps.
    pub cancel: Option<&'a AtomicBool>,
    /// Trajectories per replicate handed to the end-of-flight stage (0: no hand-off), and the
    /// fewest any stratum with posterior mass keeps.
    pub handoff: usize,
    pub handoff_floor: usize,
}

/// One filtered step, reported as it happens.
#[derive(Serialize, Clone)]
pub struct Progress {
    pub case: String,
    pub seed: u64,
    pub mode: String,
    pub mode_index: usize,
    pub epoch: String,
    pub step_index: usize,
    pub steps: usize,
    pub ess: f64,
    pub particles: usize,
    pub resampled: bool,
    pub seconds: f64,
}

impl<E> Context<'_, E> {
    fn cancelled(&self) -> bool {
        self.cancel.is_some_and(|c| c.load(Ordering::Relaxed))
    }
}

#[derive(Clone)]
struct Particle {
    aircraft: Aircraft,
    bias: BfoBias,
    /// Index of the prior draw this particle descends from.
    origin: u32,
    route: [[f32; 2]; MAX_ROUTE_POINTS],
    /// At the latest SATCOM step: BTO residual (us), BFO innovation (Hz) and its
    /// predictive s.d. (Hz), and this step's log-likelihood. Output-only; NaN if absent.
    residual: [f32; 4],
    /// Core request 10: this particle's ancestor index at up to two look-ahead hand-off epochs
    /// (u32::MAX: none). Inherited through resampling, tempering and rejuvenation.
    tags: [u32; 2],
    /// Manoeuvre counters (turns, speed changes, altitude changes, degrees turned) at
    /// `output.history_after_epoch`. Output-only.
    history_start: [f32; 4],
    /// Whether this path has already been charged the fuel rejection penalty, so that the
    /// early endurance test and the deadline test cannot both charge it.
    fuel_penalised: bool,
}

impl Particle {
    fn history(&self) -> [f32; 4] {
        let a = &self.aircraft;
        [f32::from(a.turns), f32::from(a.accelerations), f32::from(a.climbs), a.turned_rad.to_degrees() as f32]
    }
}

impl Particle {
    fn view(&self) -> StateView {
        let a = &self.aircraft;
        StateView {
            unix_s: a.unix_s,
            latitude_deg: a.lat,
            longitude_deg: a.lon,
            altitude_ft: a.alt_ft,
            ground_velocity_north_kt: a.v_north_kt,
            ground_velocity_east_kt: a.v_east_kt,
            mach: a.mach,
            mode: a.mode as usize,
            manoeuvre_time_constant_h: a.tau_s / 3600.0,
            turns: a.turns,
            accelerations: a.accelerations,
            climbs: a.climbs,
            bfo_bias_hz: self.bias.mean_hz,
            alternative: 0,
        }
    }
}

#[derive(Serialize, Deserialize)]
struct StepDiagnostics {
    epoch: String,
    ess_after_update: f64,
    log_evidence_increment: f64,
    resampled: bool,
    distinct_parents: Option<usize>,
    /// Live particle count after this epoch. Constant unless branching is enabled.
    #[serde(default, skip_serializing_if = "Option::is_none")]
    population: Option<usize>,
    seconds: f64,
}

/// Core request 10 diagnostics for one look-ahead hand-off in one mode. The ESS fractions say how
/// many of the rows would be effective if the continuing stage's likelihood were g itself:
/// without the look-ahead (rows drawn uniformly) and with it (rows drawn from q).
#[derive(Serialize, Deserialize, Clone, Debug)]
pub struct LookaheadDiagnostics {
    pub epoch: String,
    pub horizon: String,
    pub g_source: String,
    pub candidates: usize,
    pub rows: usize,
    /// Mean of (1 - defensive) g + defensive over the candidates (the normaliser of q).
    pub mean_mixture: f64,
    /// Share of candidates with g > 0.
    pub g_positive_fraction: f64,
    pub ess_fraction_uniform: f64,
    pub ess_fraction_lookahead: f64,
}

#[derive(Serialize, Deserialize)]
pub struct ModeRun {
    pub mode: String,
    pub prior_weight: f64,
    /// Minus infinity for a mode that was not run; JSON writes that as null.
    #[serde(deserialize_with = "null_is_minus_infinity")]
    pub log_evidence: f64,
    pub posterior_probability: f64,
    pub final_ess: f64,
    pub distinct_origins: usize,
    /// Times the auxiliary look-ahead triggered a resample of its own, ahead of a BTO epoch.
    #[serde(default)]
    pub lookahead_resamples: u32,
    /// Core request 10: the hand-off look-ahead at each of its epochs (empty when off).
    #[serde(default, skip_serializing_if = "Vec::is_empty")]
    pub handoff_lookahead: Vec<LookaheadDiagnostics>,
    /// Rejuvenation moves accepted, and proposed.
    #[serde(default)]
    pub rejuvenation_accepted: u64,
    #[serde(default)]
    pub rejuvenation_proposed: u64,
    epochs: Vec<StepDiagnostics>,
    runtime_s: f64,
}

#[derive(Serialize, Deserialize)]
pub struct Replicate {
    pub case: String,
    pub seed: u64,
    pub particles_per_mode: [usize; 5],
    /// Log marginal likelihood, averaged over modes with their prior weights.
    #[serde(deserialize_with = "null_is_minus_infinity")]
    pub log_evidence: f64,
    pub modes: Vec<ModeRun>,
    runtime_s: f64,
}

fn null_is_minus_infinity<'de, D: serde::Deserializer<'de>>(d: D) -> Result<f64, D::Error> {
    Ok(Option::<f64>::deserialize(d)?.unwrap_or(f64::NEG_INFINITY))
}

type Rows = Vec<[f64; FINAL_COLUMNS.len()]>;

/// Run every mode with positive prior weight and write one combined weighted particle set,
/// and the hand-off when the context asks for one.
pub fn run_case<E: Environment>(ctx: &Context<E>, case: &Case, seed: u64, dir: &Path) -> Result<(Replicate, Vec<handoff::Row>), String> {
    let started = Instant::now();
    let mut rows: Rows = Vec::new();
    let mut history: History = Vec::new();
    let mut early: Early = Vec::new();
    let mut tanks: TankRows = Vec::new();
    let mut routes_by_mode = Vec::new();
    let mut runs = Vec::new();
    let mut strata = Vec::new();
    let mut epoch_draws: Vec<Vec<EpochDraw>> = Vec::new();
    for (m, mode) in Mode::ALL.into_iter().enumerate() {
        let weight = ctx.mode_weights[m];
        let (r, routes, run, snapshots, h, candidates, draws, e, t) = if weight > 0.0 {
            run_filter(ctx, case, seed, m as u64, mode)?
        } else {
            (Vec::new(), Vec::new(), ModeRun::skipped(mode), Vec::new(), Vec::new(), Vec::new(), Vec::new(), Vec::new(), Vec::new())
        };
        early.extend(e);
        tanks.extend(t);
        epoch_draws.push(draws);
        strata.push(handoff::Stratum { mode: m, probability: 0.0, final_offset: rows.len(), candidates });
        history.extend(h);
        if !snapshots.is_empty() {
            std::fs::create_dir_all(dir.join("residuals")).map_err(|e| e.to_string())?;
        }
        for (epoch, rows) in snapshots {
            let path = dir.join("residuals").join(format!("{mode:?}-{epoch}.npy"));
            write_npy(&path, &[rows.len() / RESIDUAL_COLUMNS.len(), RESIDUAL_COLUMNS.len()], &rows)?;
        }
        rows.extend(r);
        routes_by_mode.push(routes);
        runs.push(ModeRun { prior_weight: weight, ..run });
    }
    // P(mode | data) is proportional to prior weight x marginal likelihood.
    let log_posterior: Vec<f64> = runs.iter().map(|r| r.log_evidence + r.prior_weight.ln()).collect();
    let total = log_sum_exp(&log_posterior);
    for ((run, lp), stratum) in runs.iter_mut().zip(&log_posterior).zip(&mut strata) {
        run.posterior_probability = (lp - total).exp();
        stratum.probability = run.posterior_probability;
    }
    // Each row carries its within-stratum weight; P(stratum | data) makes them one sample.
    let stratum_column = FINAL_COLUMNS.iter().position(|c| *c == "stratum").unwrap();
    for row in &mut rows {
        row[0] *= runs[row[stratum_column] as usize].posterior_probability;
    }
    write_npy(&dir.join("final.npy"), &[rows.len(), FINAL_COLUMNS.len()], rows.as_flattened())?;
    if !history.is_empty() {
        // Row-aligned with final.npy: turns, speed changes, altitude changes, degrees turned after the epoch.
        write_npy(&dir.join("history.npy"), &[history.len(), 4], history.as_flattened())?;
    }
    if ctx.config.dynamics.early.is_some() {
        assert_eq!(early.len(), rows.len(), "early.npy must be row-aligned with final.npy");
        write_npy(&dir.join("early.npy"), &[early.len(), EARLY_COLUMNS.len()], early.as_flattened())?;
    }
    if ctx.config.fuel.as_ref().and_then(|f| f.tanks) == Some(2) {
        assert_eq!(tanks.len(), rows.len(), "tanks.npy must be row-aligned with final.npy");
        crate::output::write_npy64(&dir.join("tanks.npy"), &[tanks.len(), TANK_COLUMNS.len()], tanks.as_flattened())?;
    }

    let mut rng = ChaCha8Rng::seed_from_u64(seed);
    rng.set_stream(u64::MAX); // distinct from every filter stream
    // Each mode keeps an equally weighted route sample; draw modes by their posterior probability.
    let log_mode: Vec<f64> = runs.iter().map(|r| r.posterior_probability.ln()).collect();
    let chosen_modes = systematic_resample(&log_mode, ctx.config.output.route_samples, &mut rng);
    let mut used = vec![0; Mode::ALL.len()];
    let routes: Vec<f64> = chosen_modes
        .iter()
        .flat_map(|&m| {
            used[m] += 1;
            routes_by_mode[m][used[m] - 1].iter().flat_map(|p| [f64::from(p[0]), f64::from(p[1])])
        })
        .collect();
    write_npy(&dir.join("routes.npy"), &[chosen_modes.len(), ctx.route_points, 2], &routes)?;

    let mut handoff_rows = Vec::new();
    if ctx.handoff > 0 {
        let mut rng = ChaCha8Rng::seed_from_u64(seed);
        rng.set_stream(u64::MAX - 1); // distinct from every filter stream and the route draw
        handoff_rows = handoff::select(strata, ctx.handoff, ctx.handoff_floor, &mut rng);
        let (k, stop) = (ctx.steps.len() - 1, ctx.steps.last().unwrap());
        handoff::write(dir, &handoff::Stop { epoch: stop.id.clone(), step: k, unix_s: stop.unix_s }, &handoff_rows)?;
    }

    // Hand-offs at named epochs, written while the filter ran on (output.handoff_epochs). Each
    // epoch's mode probabilities come from the evidence to that epoch alone, so the snapshot is
    // P(state | data to the epoch) and carries nothing from the measurements after it.
    let output = &ctx.config.output;
    for (e, id) in output.handoff_epochs.iter().enumerate() {
        let mut found = None;
        let log_posterior: Vec<f64> = runs
            .iter()
            .zip(&epoch_draws)
            .map(|(run, draws)| match draws.iter().find(|d| d.epoch == *id) {
                Some(d) => {
                    found = Some((d.step, d.unix_s));
                    d.log_evidence + run.prior_weight.ln()
                }
                None => f64::NEG_INFINITY,
            })
            .collect();
        let Some((k, unix_s)) = found else { continue };
        let total = log_sum_exp(&log_posterior);
        let strata: Vec<handoff::Stratum> = epoch_draws
            .iter_mut()
            .zip(&log_posterior)
            .enumerate()
            .map(|(m, (draws, lp))| {
                let candidates = draws.iter_mut().find(|d| d.epoch == *id).map(|d| std::mem::take(&mut d.candidates)).unwrap_or_default();
                handoff::Stratum { mode: m, probability: (lp - total).exp(), final_offset: 0, candidates }
            })
            .collect();
        let mut rng = ChaCha8Rng::seed_from_u64(seed);
        rng.set_stream(u64::MAX - 2 - e as u64); // distinct from the route draw and the stop hand-off
        let mut rows = handoff::select(strata, output.handoff_rows.unwrap_or(0), output.handoff_floor.unwrap_or(1), &mut rng);
        // The filter resampled after this epoch, so no final.npy row corresponds to these.
        for row in &mut rows {
            row.final_row = handoff::NO_FINAL_ROW;
        }
        let sub = dir.join(format!("handoff-{id}"));
        std::fs::create_dir_all(&sub).map_err(|err| err.to_string())?;
        let lookahead = output.handoff_lookahead.as_ref().and_then(|l| {
            l.horizons.get(id).map(|h| {
                let file = l.g_files.as_ref().is_some_and(|m| m.contains_key(id));
                handoff::Lookahead {
                    version: handoff::LOOKAHEAD_VERSION,
                    horizon: if file { "file".into() } else { h.clone() },
                    defensive: l.defensive.unwrap_or(0.2),
                    oversample: l.oversample.unwrap_or(10),
                    g_source: if file { "file".into() } else { "smoothing".into() },
                    rule: handoff::LOOKAHEAD_RULE.into(),
                }
            })
        });
        handoff::write_with(&sub, &handoff::Stop { epoch: id.clone(), step: k, unix_s }, &rows, lookahead.as_ref())?;
    }

    let replicate = Replicate {
        case: case.id.clone(),
        seed,
        particles_per_mode: ctx.config.particles_per_mode,
        log_evidence: total - ctx.mode_weights.iter().sum::<f64>().ln(),
        modes: runs,
        runtime_s: started.elapsed().as_secs_f64(),
    };
    Ok((replicate, handoff_rows))
}

impl ModeRun {
    fn skipped(mode: Mode) -> Self {
        ModeRun {
            mode: format!("{mode:?}"),
            prior_weight: 0.0,
            log_evidence: f64::NEG_INFINITY,
            posterior_probability: 0.0,
            final_ess: 0.0,
            distinct_origins: 0,
            lookahead_resamples: 0,
            handoff_lookahead: Vec::new(),
            rejuvenation_accepted: 0,
            rejuvenation_proposed: 0,
            epochs: Vec::new(),
            runtime_s: 0.0,
        }
    }
}

type Snapshot = (String, Vec<f64>);
type History = Vec<[f64; 4]>;

/// Columns of early.npy (written only with `[dynamics.early]`), row-aligned with final.npy.
/// Times are seconds after the prior epoch; NaN where the particle drew no excursion or turn.
pub const EARLY_COLUMNS: [&str; 16] = [
    "excursion", "start_s", "low_s", "climb_s", "end_s", "from_ft", "low_ft", "end_ft",
    "descent_fpm", "climb_fpm", "cas_kt", "turn", "turn_track_deg", "initial_mach", "excursion_rejected",
    "route",
];
type Early = Vec<[f64; EARLY_COLUMNS.len()]>;

fn early_row(a: &flight::Aircraft, t0: f64) -> [f64; EARLY_COLUMNS.len()] {
    let mut r = [f64::NAN; EARLY_COLUMNS.len()];
    let Some(rec) = a.early.as_deref() else { return r };
    r[0] = 0.0;
    if let Some(x) = &rec.excursion {
        r[..11].copy_from_slice(&[
            1.0, x.start_s - t0, x.low_s - t0, x.climb_s - t0, x.end_s - t0, x.from_ft, x.low_ft, x.end_ft,
            x.descent_fpm, x.climb_fpm, x.cas_kt,
        ]);
    }
    r[11] = 0.0;
    if let Some(t) = &rec.turn {
        r[11] = 1.0;
        r[12] = t.track_deg;
    }
    r[13] = rec.initial_mach;
    r[14] = f64::from(rec.excursion_rejected);
    r[15] = rec.route.as_ref().map_or(-1.0, |x| f64::from(x.index));
    r
}

type FilterOutput = (Rows, Vec<Vec<[f32; 2]>>, ModeRun, Vec<Snapshot>, History, Vec<handoff::Candidate>, Vec<EpochDraw>, Early, TankRows);

/// Columns of tanks.npy (float64, row-aligned with final.npy), written when the run carries two
/// fuel tanks (core request 16 C-7(b)). Times are unix seconds, NaN while the engine runs.
pub const TANK_COLUMNS: [&str; 8] = [
    "left_kg", "right_kg", "flow_ratio_r_to_l", "left_exhausted_unix_s", "right_exhausted_unix_s",
    "first_exhausted_unix_s", "single_engine_s", "single_engine_above_ceiling_s",
];
type TankRows = Vec<[f64; TANK_COLUMNS.len()]>;

/// One mode's equally weighted draws at one of output.handoff_epochs, with the mode's log
/// evidence up to and including that epoch.
struct EpochDraw {
    epoch: String,
    step: usize,
    unix_s: f64,
    log_evidence: f64,
    candidates: Vec<handoff::Candidate>,
}

/// A look-ahead hand-off waiting for its horizon (core request 10).
struct PendingLookahead {
    slot: usize,
    epoch: String,
    horizon: String,
    step: usize,
    unix_s: f64,
    log_evidence: f64,
    /// Normalised filtered weight of each particle at the hand-off epoch.
    filtered: Vec<f64>,
    candidates: Vec<handoff::Candidate>,
    g_file: Option<String>,
}

/// ESS of positive weights as a fraction of their count.
fn ess_fraction(w: &[f64]) -> f64 {
    let (s, s2) = w.iter().fold((0.0, 0.0), |(a, b), x| (a + x, b + x * x));
    if s2 > 0.0 { s * s / s2 / w.len() as f64 } else { 0.0 }
}

/// The look-ahead draw on g alone: `rows` indices from q = ((1 - eps) g + eps) / (M Z), each
/// with its correction ln Z - ln((1 - eps) g + eps), so E_q[exp(correction) f] is the uniform
/// mean of f over the M candidates. Also returns Z, the share of g > 0, and the ESS fractions
/// of g over the candidates (uniform) and of g x exp(correction) over the rows (look-ahead).
fn lookahead_plan(g: &[f64], eps: f64, rows: usize, rng: &mut impl Rng) -> (Vec<usize>, Vec<f64>, f64, f64, f64, f64) {
    let mix: Vec<f64> = g.iter().map(|&x| (1.0 - eps) * x.max(0.0) + eps).collect();
    let z = mix.iter().sum::<f64>() / mix.len() as f64;
    let total = z * mix.len() as f64;
    let log_q: Vec<f64> = mix.iter().map(|a| (a / total).ln()).collect();
    let picks = systematic_resample(&log_q, rows, rng);
    let corrections: Vec<f64> = picks.iter().map(|&c| z.ln() - mix[c].ln()).collect();
    let corrected: Vec<f64> = picks.iter().zip(&corrections).map(|(&c, lc)| g[c] * lc.exp()).collect();
    let positive = g.iter().filter(|&&x| x > 0.0).count() as f64 / g.len() as f64;
    (picks, corrections, z, positive, ess_fraction(g), ess_fraction(&corrected))
}

/// `lookahead_plan` applied to the candidates themselves.
fn lookahead_draw(
    candidates: &[handoff::Candidate],
    g: &[f64],
    eps: f64,
    rows: usize,
    rng: &mut impl Rng,
) -> (Vec<handoff::Candidate>, f64, f64, f64, f64) {
    assert_eq!(candidates.len(), g.len());
    let (picks, corrections, z, positive, ess_uniform, ess_lookahead) = lookahead_plan(g, eps, rows, rng);
    let drawn = picks
        .iter()
        .zip(corrections)
        .map(|(&c, lc)| {
            let mut x = candidates[c].clone();
            x.log_correction = lc;
            x
        })
        .collect();
    (drawn, z, positive, ess_uniform, ess_lookahead)
}

/// The independent, schedule-free random stream of one (stratum, step, particle).
fn stream(seed: u64, stratum: u64, step: u64, particle: usize) -> ChaCha8Rng {
    let mut rng = ChaCha8Rng::seed_from_u64(seed);
    rng.set_stream((stream_mix(stratum, step) << 32) | particle as u64);
    rng
}

/// Propagate one particle to `to`, recording route points on the way. The filter and a
/// continuation from the hand-off share it, so both split the flight at the same times.
fn advance<E: Environment>(p: &mut Particle, to: f64, ctx: &Context<E>, rng: &mut ChaCha8Rng) {
    let (prior, interval) = (ctx.prior, ctx.config.output.route_interval_s);
    let route_time = |k: usize| prior.unix_s + k as f64 * interval;
    let a = &mut p.aircraft;
    let mut r = ((a.unix_s - prior.unix_s) / interval).floor() as usize + 1;
    while r < ctx.route_points && route_time(r) <= to {
        a.propagate(route_time(r), ctx.params, ctx.environment, rng);
        p.route[r] = [a.lat as f32, a.lon as f32];
        r += 1;
    }
    a.propagate(to, ctx.params, ctx.environment, rng);
}

/// Log-weight penalty standing in for rejecting a path on fuel grounds. Finite so that a
/// fully rejected stratum still reports an evidence and an ESS rather than NaN; e^-50 is 2e-22.
const FUEL_REJECT_LOG_PENALTY: f64 = -50.0;
const FUEL_HARD_REJECT_LOG_PENALTY: f64 = -1.0e6;

fn run_filter<E: Environment>(ctx: &Context<E>, case: &Case, seed: u64, stratum: u64, mode: Mode) -> Result<FilterOutput, String> {
    let started = Instant::now();
    let config = ctx.config;
    let (prior, environment) = (ctx.prior, ctx.environment);
    let n = config.particles_per_mode[stratum as usize];
    let params = ctx.params;
    let stream = |step: u64, i: usize| stream(seed, stratum, step, i);
    // Fuel evidence, resolved once: the time the aircraft must still have had fuel at, and the
    // Gaussian on when it ran out. Both are optional and declared in `[fuel]`.
    // Audit F7: `hard_reject` gives a contradicted path weight exactly zero rather than e^-50.
    // -1e6 rather than minus infinity: e^-1e6 underflows to 0.0 in f64, so the path's weight is
    // zero, while a mode in which every path is rejected still has a finite log evidence and
    // probability zero instead of NaN weights (minus infinity minus minus infinity).
    let fuel_reject = if config.fuel.as_ref().and_then(|f| f.hard_reject) == Some(true) { FUEL_HARD_REJECT_LOG_PENALTY } else { FUEL_REJECT_LOG_PENALTY };
    let fuel_power_until = config.fuel.as_ref().and_then(|f| f.require_power_until.as_ref()).and_then(|id| {
        ctx.steps.iter().find(|s| s.id == *id).map(|s| s.unix_s)
    });
    // The case's evidence set: whether the BTO is scored at all, and the last epoch whose
    // measurements enter the likelihood. Later epochs are still flown and still reported.
    let use_bto = case.use_bto.unwrap_or(true);
    let scored_until = case.likelihood_until.as_ref().and_then(|id| {
        ctx.steps.iter().find(|s| s.id == *id).map(|s| s.unix_s)
    });
    if case.likelihood_until.is_some() && scored_until.is_none() {
        return Err(format!("case {}: likelihood_until names no epoch", case.id));
    }
    let fuel_exhaustion = config.fuel.as_ref().and_then(|f| {
        match (&f.exhaustion_target_utc, f.exhaustion_sd_s) {
            (Some(t), Some(sd)) => satcom::parse_utc(t).ok().map(|t| (t, sd)),
            _ => None,
        }
    });

    let mut particles: Vec<Particle> = (0..n)
        .into_par_iter()
        .map(|i| {
            let aircraft = Aircraft::sample(prior, mode, params, environment, &mut stream(0, i));
            let mut route = [[f32::NAN; 2]; MAX_ROUTE_POINTS];
            route[0] = [aircraft.lat as f32, aircraft.lon as f32];
            let bias = BfoBias { mean_hz: config.bfo_bias.mean_hz, variance_hz2: config.bfo_bias.sd_hz.powi(2) };
            Particle { aircraft, bias, origin: i as u32, route, residual: [f32::NAN; 4], tags: [u32::MAX; 2], history_start: [0.0; 4], fuel_penalised: false }
        })
        .collect();
    // Auxiliary look-ahead: extra standard deviation, in microseconds, added in quadrature to
    // the epoch's own BTO sd when scoring a dead-reckoned prediction. None disables the step.
    let lookahead_sd_us = config.sampler.as_ref().and_then(|s| s.lookahead_bto_sd_us);
    let rejuvenate: Vec<String> = config.sampler.as_ref().map(|s| s.rejuvenate_epochs.clone()).unwrap_or_default();
    let temper_epochs: Vec<String> = config.sampler.as_ref().map(|s| s.temper_epochs.clone()).unwrap_or_default();
    let temper_stages = config.sampler.as_ref().and_then(|s| s.temper_stages).unwrap_or(4).max(1);
    // Core request 17 guard: the rejuvenation move after a resample re-simulates from
    // `before_step` by the resample's parents, which index the population as it stood before
    // the epoch. A tempered epoch has replaced that population by then, so the two must not
    // share an epoch.
    if let Some(e) = temper_epochs.iter().find(|e| rejuvenate.contains(e)) {
        return Err(format!("sampler: epoch {e} is in both temper_epochs and rejuvenate_epochs; choose one"));
    }
    let bridge = config.sampler.as_ref().and_then(|s| s.bridge_prior_mix.map(|mix| {
        (mix, s.bridge_window_sd.unwrap_or(3.0), s.bridge_cells.unwrap_or(24))
    }));
    // Davey's branching resampler. Incompatible with the three fixed-population steps above:
    // each of those inherits or divides out a per-particle factor indexed against a population
    // that branching changes underneath them.
    let branching = config.sampler.as_ref().and_then(|s| s.branching.clone());
    if let Some(b) = &branching {
        if lookahead_sd_us.is_some() || !rejuvenate.is_empty() || bridge.is_some() {
            return Err("sampler.branching cannot be combined with the look-ahead, rejuvenation or bridge steps".into());
        }
        if b.branch_factor < 2 {
            return Err(format!("sampler.branching.branch_factor is {}, must be at least 2", b.branch_factor));
        }
    }
    let branch_cap = branching.as_ref().map(|b| b.max_particles.unwrap_or(2 * n)).unwrap_or(n);
    let handoff_epochs = &config.output.handoff_epochs;
    let epoch_rows = config.output.handoff_rows.unwrap_or(0);
    if !handoff_epochs.is_empty() {
        if epoch_rows == 0 {
            return Err("output.handoff_epochs needs output.handoff_rows of at least 1".into());
        }
        if branching.is_some() {
            return Err("output.handoff_epochs cannot be combined with sampler.branching, whose weights are unnormalised between epochs".into());
        }
        if let Some(id) = handoff_epochs.iter().find(|id| !ctx.steps.iter().any(|s| s.id == **id)) {
            return Err(format!("output.handoff_epochs: {id} is not among the filter's epochs (excluded, or unknown)"));
        }
    }
    // Core request 10: the hand-off look-ahead.
    let lookahead = config.output.handoff_lookahead.as_ref();
    let mut lookahead_slots: Vec<(String, String, Option<String>)> = Vec::new();
    let (lookahead_oversample, lookahead_eps) = match lookahead {
        Some(l) => (l.oversample.unwrap_or(10), l.defensive.unwrap_or(0.2)),
        None => (1, 1.0),
    };
    if let Some(l) = lookahead {
        if l.horizons.len() > 2 {
            return Err("output.handoff_lookahead: at most two hand-off epochs".into());
        }
        if !(lookahead_eps > 0.0 && lookahead_eps <= 1.0) || lookahead_oversample == 0 {
            return Err("output.handoff_lookahead: defensive must be in (0, 1] and oversample at least 1".into());
        }
        for (epoch, horizon) in &l.horizons {
            if !handoff_epochs.contains(epoch) {
                return Err(format!("output.handoff_lookahead: {epoch} is not one of output.handoff_epochs"));
            }
            let g_file = l.g_files.as_ref().and_then(|m| m.get(epoch)).cloned();
            let ke = ctx.steps.iter().position(|s| s.id == *epoch).unwrap();
            if g_file.is_none() {
                match ctx.steps.iter().position(|s| s.id == *horizon) {
                    Some(kh) if kh > ke => {}
                    _ => return Err(format!("output.handoff_lookahead: horizon {horizon} of {epoch} is not a later epoch of this filter")),
                }
            }
            lookahead_slots.push((epoch.clone(), horizon.clone(), g_file));
        }
        if let Some(files) = &l.g_files {
            if let Some(e) = files.keys().find(|e| !l.horizons.contains_key(*e)) {
                return Err(format!("output.handoff_lookahead.g_files: {e} has no entry in horizons"));
            }
        }
    }
    let mut pending: Vec<PendingLookahead> = Vec::new();
    let mut lookahead_diagnostics: Vec<LookaheadDiagnostics> = Vec::new();
    let mut epoch_draws = Vec::new();
    let mut rejuvenated = [0u64; 2];
    let mut lookahead_resamples = 0u32;
    let mut log_weights = vec![-(n as f64).ln(); n];
    let mut log_evidence = 0.0;
    // Branching leaves the weights unnormalised, as the published scheme does. Every epoch the
    // population is rescaled so its best member sits at zero log-weight and the shift is banked
    // here, which keeps the threshold comparison scale-free and the arithmetic in range; the
    // evidence is this plus the log of the surviving weight sum.
    let mut log_scale = 0.0f64;
    // Log of the weighted total, which under branching is the running evidence estimate. The
    // weights start at 1/n apiece, so it starts at zero.
    let mut running_total = 0.0f64;
    let mut diagnostics = Vec::new();
    let mut snapshots = Vec::new();
    // Time of the previous BFO-bearing epoch, for the bias random walk. The first BFO gets no
    // drift: its gap is from the prior, where the 25 Hz prior standard deviation already stands
    // for everything that happened before the filter starts.
    let mut last_bfo_unix_s: Option<f64> = None;

    for (k, step) in ctx.steps.iter().enumerate() {
        if ctx.cancelled() {
            return Err("cancelled".into());
        }
        let t_step = Instant::now();
        let last = k + 1 == ctx.steps.len();
        let epoch_view = EpochView { id: &step.id, unix_s: step.unix_s, satcom: step.satcom.is_some() };
        let has_bfo = step.satcom.as_ref().is_some_and(|e| case.use_bfo && e.cruise_bfo && e.bfo_hz.is_some());
        let bfo_gap_s = match (has_bfo, last_bfo_unix_s) {
            (true, Some(prev)) => step.unix_s - prev,
            _ => 0.0,
        };
        if has_bfo {
            last_bfo_unix_s = Some(step.unix_s);
        }
        // Auxiliary look-ahead (Pitt & Shephard). Before propagating into a BTO epoch, score
        // each particle by where a dead-reckoned continuation of its present velocity would put
        // it on that epoch's arc, fold that into the resampling weights, and divide it out again
        // after the real propagation and the real likelihood. The division is exact and the
        // auxiliary factor only has to be positive, so the dead-reckoning approximation inside
        // it cannot bias the posterior - it only decides which particles get the effort.
        //
        // Why this epoch set matters. At 19:41 the track is within 2 degrees of tangential to
        // the arc: one BTO standard deviation admits about 122 NM along track against 4.2 NM
        // across it, a 29:1 sliver, because the range is at its minimum there (closest approach
        // is 19:55). A proposal that scatters particles isotropically puts almost none of them
        // in that sliver, which is what the recorded m1941 ESS measures. Across the 26 distinct
        // untempered full-scale runs in results/convergence-ledger.csv it spans 0.08-2.03%:
        // 0.08-0.13% in the three endurance rungs that score fuel at 00:11 or 00:19 without
        // tempering, 0.70-2.03% everywhere else, and 5.7-6.0% once 19:41 is annealed at 16
        // stages. The bare 0.08-0.13% quoted here previously was the endurance rungs alone and
        // is not the general case. The
        // look-ahead aims the resampling at the sliver before the propagation is spent.
        let aux: Vec<f64> = match (lookahead_sd_us, step.satcom.as_ref()) {
            (Some(sd_extra), Some(epoch)) if epoch.cruise_bto && epoch.bto_us.is_some() && use_bto => {
                let z = epoch.bto_us.unwrap();
                // Inflated so the auxiliary weight stays a soft steer rather than a second
                // likelihood: the dead-reckoned prediction carries real error over an hour of
                // flight, and under-stating it would make the correction term violent.
                let sd = (epoch.bto_sd_us.powi(2) + sd_extra * sd_extra).sqrt();
                particles
                    .par_iter()
                    .map(|p| {
                        let a = &p.aircraft;
                        let dt = step.unix_s - a.unix_s;
                        let (lat, lon) = geo::advance(a.lat, a.lon, a.alt_ft, a.v_north_kt, a.v_east_kt, dt);
                        let predicted = bto_us(epoch.satellite_km, lat, lon, a.alt_ft);
                        gaussian_log_likelihood(z - predicted, sd)
                    })
                    .collect()
            }
            _ => Vec::new(),
        };
        if !aux.is_empty() {
            // Fold in, then take the normaliser into the evidence so the two halves of the
            // auxiliary step telescope: log sum(w * lambda) here, log mean(L / lambda) below.
            log_weights.par_iter_mut().zip(&aux).for_each(|(lw, a)| *lw += a);
            let inc = log_sum_exp(&log_weights);
            log_evidence += inc;
            log_weights.par_iter_mut().for_each(|lw| *lw -= inc);
            let ess_aux = effective_sample_size(&log_weights);
            if ess_aux < config.resample_ess_fraction * n as f64 {
                let parents = systematic_resample(&log_weights, n, &mut stream(6000 + k as u64, 0));
                let refresh = 7000 + k as u64;
                let picked: Vec<(Particle, f64)> = parents
                    .par_iter()
                    .enumerate()
                    .map(|(i, &j)| {
                        let mut p = particles[j].clone();
                        p.aircraft.refresh_manoeuvre_rate(params, &mut stream(refresh, i));
                        (p, aux[j])
                    })
                    .collect();
                particles = picked.iter().map(|(p, _)| p.clone()).collect();
                // Each child inherits its parent's auxiliary factor so the division below
                // removes exactly what was added.
                let inherited: Vec<f64> = picked.iter().map(|&(_, a)| a).collect();
                log_weights
                    .par_iter_mut()
                    .zip(&inherited)
                    .for_each(|(lw, a)| *lw = -(n as f64).ln() - a);
                lookahead_resamples += 1;
            } else {
                log_weights.par_iter_mut().zip(&aux).for_each(|(lw, a)| *lw -= a);
            }
        }
        // One epoch's propagation and weighting for a single particle, returning the
        // log-weight increment. Factored out so the resample-move rejuvenation below can score a
        // re-simulated candidate through exactly the same code as the particle it competes with;
        // two copies of this arithmetic would be two chances to diverge.
        let step_update = |p: &mut Particle, i: usize, stream_base: u64| -> f64 {
            let mut delta = 0.0f64;
            advance(p, step.unix_s, ctx, &mut stream(stream_base, i));
            let a = &mut p.aircraft;
            if config.output.history_after_epoch.as_deref() == Some(step.id.as_str()) {
                p.history_start = [f32::from(a.turns), f32::from(a.accelerations), f32::from(a.climbs), a.turned_rad.to_degrees() as f32];
            }
            // The endurance proposal's exact log prior-to-proposal ratio, accumulated over the
            // steps since the last epoch. Draining it here rather than inside the dynamics
            // keeps the correction in the weight and out of the trajectory.
            delta += std::mem::take(&mut a.fuel_log_weight_correction);
            // A path the fuel state has already ruled out: it cannot reach the deadline on any
            // continuation, so it would be rejected there. Charging the same penalty now lets
            // the resampling that follows reallocate its share while there is still flight to
            // explore. Charged once; the deadline test below then skips it.
            if a.fuel_doomed && !p.fuel_penalised {
                p.fuel_penalised = true;
                delta += fuel_reject;
            }
            if let Some(epoch) = &step.satcom {
                let before = delta;
                p.residual = [f32::NAN; 4];
                // Only measurements the cruise model applies to (the table's `cruise` column),
                // and only up to the case's likelihood cutoff: later epochs are still flown
                // through and their residuals still recorded, as diagnostics on a posterior
                // that was not fitted to them.
                let scored = scored_until.is_none_or(|t| epoch.unix_s <= t);
                if let (true, Some(z)) = (epoch.cruise_bto, epoch.bto_us) {
                    let residual = z - bto_us(epoch.satellite_km, a.lat, a.lon, a.alt_ft);
                    p.residual[0] = residual as f32;
                    if use_bto && scored {
                        delta += gaussian_log_likelihood(residual, epoch.bto_sd_us);
                    }
                }
                if let (true, true, Some(z)) = (case.use_bfo && scored, epoch.cruise_bfo, epoch.bfo_hz) {
                    // The bias wanders over the gap since the previous BFO; the gap is a
                    // property of the measurement schedule, so it is computed once per step.
                    if let Some(rate) = config.bfo_bias.drift_hz2_per_s {
                        p.bias.drift(bfo_gap_s, rate);
                    }
                    // Davey sec. 7.2 carries no vertical rate in cruise, so the published model
                    // scores a particle in a level change as though it were level. The end-of-flight
                    // stage already passes the real rate (terminal.rs); `bfo_vertical_rate` passes it
                    // here too. 17.5 Hz per 1,000 ft/min at the 00:11 geometry.
                    let v_up = if params.bfo_vertical_rate { a.vertical_speed_fpm(params) } else { 0.0 };
                    let predicted = bfo_without_bias_hz(epoch, a.lat, a.lon, a.alt_ft, a.v_north_kt, a.v_east_kt, v_up);
                    p.residual[1] = (z - predicted - p.bias.mean_hz) as f32;
                    p.residual[2] = (p.bias.variance_hz2 + epoch.bfo_sd_hz.powi(2)).sqrt() as f32;
                    delta += p.bias.update(predicted, z, epoch.bfo_sd_hz);
                }
                // Fuel as evidence. The aircraft transmitted at this epoch, so a path whose
                // tank ran dry before it contradicts the observation. Rejection is applied as a
                // large finite penalty rather than negative infinity so that a stratum in which
                // every path is rejected still yields a finite evidence and a readable
                // diagnostic instead of a NaN; e^-50 is 2e-22, which is zero against any
                // surviving path.
                if let Some(until) = fuel_power_until {
                    if epoch.unix_s <= until && a.fuel_exhausted_unix_s < epoch.unix_s && !p.fuel_penalised {
                        p.fuel_penalised = true;
                        delta += fuel_reject;
                    }
                }
                p.residual[3] = (delta - before) as f32;
            }
            if last {
                // When the engines stopped. The 00:19 log-on followed engine failure and an APU
                // start, so exhaustion should sit shortly before it. A path still holding fuel at
                // the final step has not contradicted anything yet, but it is further from the
                // target the more fuel it has left, so it is scored at the final step time — a
                // lower bound on its exhaustion — which penalises it smoothly rather than by a
                // cliff.
                if let Some((target, sd)) = fuel_exhaustion {
                    let when = if a.fuel_exhausted_unix_s.is_finite() { a.fuel_exhausted_unix_s } else { a.unix_s };
                    delta += gaussian_log_likelihood(when - target, sd);
                }
            }
            if !ctx.hypotheses.is_empty() {
                let view = p.view();
                for h in ctx.hypotheses {
                    delta += h.epoch_log_likelihood(&epoch_view, &view);
                    if last {
                        delta += h.final_log_likelihood(&view);
                    }
                }
            }
            delta
        };
        // The state every particle is in before this epoch's propagation, kept only when this
        // epoch is to be rejuvenated: the move needs the parent's pre-epoch state to re-simulate
        // the same segment a second time.
        // The arc this step ends on, handed to the dynamics as pure geometry: the filter owns
        // the measurement model, so it converts the BTO into the aircraft-to-satellite range it
        // implies and the flight crate never needs to know about timing offsets or the ground
        // station. Cleared when this step carries no BTO, so turns fall back to the prior.
        let arc_target = match (bridge, step.satcom.as_ref()) {
            (Some((mix, window, cells)), Some(epoch)) if epoch.cruise_bto && epoch.bto_us.is_some() && use_bto => {
                let total_km = (epoch.bto_us.unwrap() + satcom::BTO_FIXED_OFFSET_US)
                    * satcom::SPEED_OF_LIGHT_KM_S * 1e-6 / 2.0;
                let ges_km = (epoch.satellite_km - satcom::PERTH_GES_KM).norm();
                Some(flight::ArcTarget {
                    unix_s: step.unix_s,
                    satellite_km: epoch.satellite_km,
                    range_km: total_km - ges_km,
                    sd_km: epoch.bto_sd_us * satcom::SPEED_OF_LIGHT_KM_S * 1e-6 / 2.0,
                    prior_mix: mix,
                    cells,
                    window_sd: window,
                })
            }
            _ => None,
        };
        if bridge.is_some() {
            particles.par_iter_mut().for_each(|p| p.aircraft.arc_target = arc_target);
        }
        let rejuvenating = rejuvenate.iter().any(|e| e == &step.id);
        let tempering = temper_epochs.iter().any(|e| e == &step.id).then_some(temper_stages);
        let before_step: Vec<Particle> =
            if rejuvenating || tempering.is_some() { particles.clone() } else { Vec::new() };
        // The epoch's full log-likelihood increment per particle. Added to the weights here
        // unless the epoch is tempered, in which case it is paid out in stages below.
        let mut deltas: Vec<f64> = particles
            .par_iter_mut()
            .enumerate()
            .map(|(i, p)| step_update(p, i, k as u64 + 1))
            .collect();
        if tempering.is_none() {
            log_weights.par_iter_mut().zip(&deltas).for_each(|(lw, d)| *lw += d);
        }
        // Annealed SMC at a degenerate epoch. The increment is applied as L^beta over equal
        // stages; between stages the population is resampled and then moved by the same
        // invariant kernel the rejuvenation step uses, accepted against the *tempered* ratio so
        // each intermediate distribution is left invariant. The exponents sum to one, so the
        // epoch's contribution to the weight and to the evidence is unchanged: what changes is
        // that the population is given several chances to migrate into a sharp likelihood,
        // with its diversity restored between them, instead of one.
        let mut tempered_increment = 0.0f64;
        // The epoch's effective sample size at its worst moment: measured after each stage's
        // weight update and before that stage's resample, which is the same point in the cycle
        // the untempered diagnostic is taken at. Measuring after the resample instead would
        // report the population size and say nothing.
        let mut tempered_ess = f64::INFINITY;
        if let Some(stages) = tempering {
            let share = 1.0 / stages as f64;
            // Core request 17: which pre-epoch state each member of the current population
            // descends from. `before_step` is indexed by the population as it stood at the
            // start of the epoch; after a stage resamples, member c descends from
            // ancestry[parents[c]], and a move must re-simulate from that history, not from
            // before_step[c] (another particle's history, which drops its pre-epoch weight).
            let mut ancestry: Vec<usize> = (0..n).collect();
            for j in 0..stages {
                log_weights.par_iter_mut().zip(&deltas).for_each(|(lw, d)| *lw += d * share);
                let inc = log_sum_exp(&log_weights);
                log_evidence += inc;
                tempered_increment += inc;
                log_weights.par_iter_mut().for_each(|lw| *lw -= inc);
                let stage_ess = effective_sample_size(&log_weights);
                tempered_ess = tempered_ess.min(stage_ess);
                if stage_ess >= config.resample_ess_fraction * n as f64 {
                    continue;
                }
                let tag = (k * 16 + j) as u64;
                let parents = systematic_resample(&log_weights, n, &mut stream(9500 + tag, 0));
                // The move targets the tempered distribution reached so far, so the Metropolis
                // ratio carries the same exponent the weights have been charged.
                let beta = share * (j + 1) as f64;
                let moved: Vec<(Particle, f64)> = parents
                    .par_iter()
                    .enumerate()
                    .map(|(c, &anc)| {
                        let mut cand = before_step[ancestry[anc]].clone();
                        cand.aircraft.refresh_manoeuvre_rate(params, &mut stream(9600 + tag, c));
                        let d_new = step_update(&mut cand, c, 9700 + tag);
                        let u: f64 = stream(9800 + tag, c).gen();
                        if u.ln() < beta * (d_new - deltas[anc]) {
                            (cand, d_new)
                        } else {
                            (particles[anc].clone(), deltas[anc])
                        }
                    })
                    .collect();
                rejuvenated[0] += moved
                    .iter()
                    .zip(&parents)
                    .filter(|((_, d), &anc)| *d != deltas[anc])
                    .count() as u64;
                rejuvenated[1] += moved.len() as u64;
                let (kids, d): (Vec<Particle>, Vec<f64>) = moved.into_iter().unzip();
                particles = kids;
                deltas = d;
                ancestry = compose_ancestry(&ancestry, &parents);
                log_weights.fill(-(n as f64).ln());
            }
        }

        if config.output.residual_samples > 0 && step.satcom.is_some() {
            snapshots.push((step.id.clone(), residual_snapshot(&particles, &log_weights, config.output.residual_samples, &mut stream(4000 + k as u64, 0))));
        }
        // The evidence, and the weight normalisation the rest of the step works from. Without
        // branching the weights are renormalised to sum to one each epoch and the normaliser is
        // the evidence increment. With branching they stay unnormalised and are instead shifted
        // so the best sits at zero, so the increment has to be read off the running total.
        let increment;
        if branching.is_some() {
            let top = log_weights.par_iter().cloned().reduce(|| f64::NEG_INFINITY, f64::max);
            if n > 0 && !top.is_finite() {
                return Err(format!("{} seed {seed} {mode:?}: every particle was eliminated at {}", case.id, step.id));
            }
            log_weights.par_iter_mut().for_each(|lw| *lw -= top);
            log_scale += top;
            // The running weighted total is the evidence estimate so far; this epoch's
            // contribution is how much it moved. Measured against the total left by the
            // previous epoch's branching, so the branching's own sampling noise stays inside
            // the estimator rather than being charged to a measurement.
            let total = log_sum_exp(&log_weights) + log_scale;
            increment = total - running_total;
            running_total = total;
        } else if tempering.is_some() {
            // Already paid out and renormalised stage by stage; the epoch's contribution is
            // the sum of the stage normalisers.
            increment = tempered_increment;
        } else {
            increment = log_sum_exp(&log_weights);
            log_evidence += increment;
            log_weights.par_iter_mut().for_each(|lw| *lw -= increment);
        }
        // ESS and systematic resampling both read normalised weights; under branching the
        // stored weights are not normalised, so the diagnostic works on a normalised copy.
        let ess = if branching.is_some() {
            let t = log_sum_exp(&log_weights);
            effective_sample_size(&log_weights.par_iter().map(|lw| lw - t).collect::<Vec<_>>())
        } else if tempering.is_some() {
            tempered_ess
        } else {
            effective_sample_size(&log_weights)
        };
        let mut population = None;
        if let Some(b) = &branching {
            // Davey Eq. 8.6. Weights are relative to the best surviving path, so the threshold
            // reads as a number of nats behind it; children of a branching parent take its
            // weight divided by the branch factor, and a pruned parent's rare survivor is
            // promoted to weight one. Both arms leave the weighted sum unchanged in
            // expectation, which is what makes the floating population size legitimate.
            let ln_nbar = f64::from(b.branch_factor).ln();
            let counts: Vec<u32> = log_weights
                .par_iter()
                .enumerate()
                .map(|(i, &lw)| {
                    if lw >= b.log_threshold {
                        b.branch_factor
                    } else {
                        let u: f64 = stream(8000 + k as u64, i).gen();
                        u32::from(u.ln() < lw)
                    }
                })
                .collect();
            let offsets: Vec<usize> = counts
                .iter()
                .scan(0usize, |acc, &c| {
                    let at = *acc;
                    *acc += c as usize;
                    Some(at)
                })
                .collect();
            let total: usize = offsets.last().copied().unwrap_or(0) + counts.last().copied().unwrap_or(0) as usize;
            if n > 0 && total == 0 {
                return Err(format!("{} seed {seed} {mode:?}: branching pruned every particle at {}", case.id, step.id));
            }
            // Overflow is handled before the children exist. Every child of a parent is an
            // identical copy carrying the same weight, so drawing the capped population from
            // the children is the same draw as taking it from the parents weighted by the
            // mass each parent's block would have carried. Doing it at the parent level is
            // distributionally identical and never materialises the oversized population,
            // which would otherwise peak at the branch factor times the live count.
            if total > branch_cap {
                let mass: Vec<f64> = counts
                    .par_iter()
                    .zip(&log_weights)
                    .map(|(&c, &lw)| {
                        if c == 0 {
                            f64::NEG_INFINITY
                        } else if lw >= b.log_threshold {
                            lw - ln_nbar + f64::from(c).ln()
                        } else {
                            0.0
                        }
                    })
                    .collect();
                let total_w = log_sum_exp(&mass);
                let normalised: Vec<f64> = mass.par_iter().map(|x| x - total_w).collect();
                let picked = systematic_resample(&normalised, branch_cap, &mut stream(8100 + k as u64, 0));
                particles = picked
                    .par_iter()
                    .enumerate()
                    .map(|(c, &j)| {
                        let mut p = particles[j].clone();
                        if b.refresh_tau {
                            p.aircraft.refresh_manoeuvre_rate(params, &mut stream(8200 + k as u64, c));
                        }
                        p
                    })
                    .collect();
                log_weights = vec![total_w - (branch_cap as f64).ln(); branch_cap];
            } else {
                let children: Vec<(Particle, f64)> = (0..total)
                    .into_par_iter()
                    .map(|c| {
                        // Which parent this child belongs to: offsets is ascending, so the
                        // parent is the last one whose block starts at or before c.
                        let i = offsets.partition_point(|&o| o <= c) - 1;
                        let mut p = particles[i].clone();
                        if b.refresh_tau {
                            p.aircraft.refresh_manoeuvre_rate(params, &mut stream(8200 + k as u64, c));
                        }
                        let w = if log_weights[i] >= b.log_threshold { log_weights[i] - ln_nbar } else { 0.0 };
                        (p, w)
                    })
                    .collect();
                let (kids, w): (Vec<Particle>, Vec<f64>) = children.into_iter().unzip();
                particles = kids;
                log_weights = w;
            }
            population = Some(particles.len());
            running_total = log_sum_exp(&log_weights) + log_scale;
        }
        let resample = branching.is_none() && ess < config.resample_ess_fraction * n as f64;
        let mut distinct_parents = None;
        let mut parents_for_move: Option<Vec<usize>> = None;
        if resample {
            let parents = systematic_resample(&log_weights, n, &mut stream(2000 + k as u64, 0));
            distinct_parents = Some(count_distinct(&parents));
            parents_for_move = Some(parents.clone());
            let refresh_step = 1000 + k as u64;
            particles = parents
                .par_iter()
                .enumerate()
                .map(|(i, &j)| {
                    let mut p = particles[j].clone();
                    p.aircraft.refresh_manoeuvre_rate(params, &mut stream(refresh_step, i));
                    p
                })
                .collect();
            log_weights.fill(-(n as f64).ln());
            // Resample-move rejuvenation. The resample above has just made many children exact
            // copies of one parent; this gives each of them an independent second draw of the
            // segment into this epoch and keeps whichever the Metropolis ratio prefers. Because
            // the proposal is the model's own transition, that ratio is the ratio of incremental
            // weights, and the move is invariant for the current target - it adds path diversity
            // without moving the posterior.
            if rejuvenating {
                let parents = parents_for_move.as_ref().expect("parents are set when resampling");
                let moved: Vec<(Particle, bool)> = parents
                    .par_iter()
                    .enumerate()
                    .map(|(j, &anc)| {
                        let mut cand = before_step[anc].clone();
                        cand.aircraft.refresh_manoeuvre_rate(params, &mut stream(9100 + k as u64, j));
                        let d_new = step_update(&mut cand, j, 9000 + k as u64);
                        let d_old = deltas[anc];
                        let u: f64 = stream(9200 + k as u64, j).gen();
                        if u.ln() < d_new - d_old { (cand, true) } else { (particles[j].clone(), false) }
                    })
                    .collect();
                rejuvenated[0] += moved.iter().filter(|&&(_, a)| a).count() as u64;
                rejuvenated[1] += moved.len() as u64;
                particles = moved.into_iter().map(|(p, _)| p).collect();
            }
        }
        // A hand-off at this epoch: after its update, tempering and resampling, so the draw is
        // from the posterior given the data to here and the filter's own state is untouched.
        // Core request 10: look-ahead hand-offs whose horizon is this epoch draw their rows now,
        // from the candidates taken at their own epoch, with g from the tags' smoothed shares.
        let mut i = 0;
        while i < pending.len() {
            if pending[i].g_file.is_some() || pending[i].horizon != step.id {
                i += 1;
                continue;
            }
            let p = pending.remove(i);
            let mut smoothed = vec![0.0f64; p.filtered.len()];
            for (part, lw) in particles.iter().zip(&log_weights) {
                let t = part.tags[p.slot];
                if t != u32::MAX {
                    smoothed[t as usize] += lw.exp();
                }
            }
            let g: Vec<f64> = p.candidates.iter().map(|c| if p.filtered[c.particle] > 0.0 { smoothed[c.particle] / p.filtered[c.particle] } else { 0.0 }).collect();
            let (candidates, z, pos, eu, el) = lookahead_draw(&p.candidates, &g, lookahead_eps, epoch_rows, &mut stream(5150 + p.step as u64, 0));
            lookahead_diagnostics.push(LookaheadDiagnostics {
                epoch: p.epoch.clone(), horizon: p.horizon.clone(), g_source: "smoothing".into(), candidates: p.candidates.len(), rows: epoch_rows,
                mean_mixture: z, g_positive_fraction: pos, ess_fraction_uniform: eu, ess_fraction_lookahead: el,
            });
            epoch_draws.push(EpochDraw { epoch: p.epoch, step: p.step, unix_s: p.unix_s, log_evidence: p.log_evidence, candidates });
        }
        if handoff_epochs.iter().any(|e| e == &step.id) {
            let slot = lookahead_slots.iter().position(|(e, ..)| e == &step.id);
            let draw_count = if slot.is_some() { epoch_rows * lookahead_oversample } else { epoch_rows };
            let candidates: Vec<handoff::Candidate> = systematic_resample(&log_weights, draw_count, &mut stream(5100 + k as u64, 0))
                .into_iter()
                .map(|j| {
                    let p = &particles[j];
                    handoff::Candidate { particle: j, aircraft: p.aircraft.clone(), bias: p.bias, origin: p.origin, log_correction: 0.0 }
                })
                .collect();
            match slot {
                None => epoch_draws.push(EpochDraw { epoch: step.id.clone(), step: k, unix_s: step.unix_s, log_evidence, candidates }),
                Some(slot) => {
                    let (_, horizon, g_file) = lookahead_slots[slot].clone();
                    if let Some(pattern) = g_file {
                        // Hook (5): g supplied per candidate by the continuing stage.
                        let path = pattern.replace("{seed}", &seed.to_string()).replace("{mode}", &format!("{mode:?}"));
                        let mut g = Vec::with_capacity(candidates.len());
                        crate::output::read_npy_rows(std::path::Path::new(&path), |row| g.push(row[0]))?;
                        if g.len() != candidates.len() || g.iter().any(|x| !(x.is_finite() && *x >= 0.0)) {
                            return Err(format!("{path}: needs {} finite non-negative g values, one per candidate", candidates.len()));
                        }
                        let (drawn, z, pos, eu, el) = lookahead_draw(&candidates, &g, lookahead_eps, epoch_rows, &mut stream(5150 + k as u64, 0));
                        lookahead_diagnostics.push(LookaheadDiagnostics {
                            epoch: step.id.clone(), horizon: "file".into(), g_source: "file".into(), candidates: candidates.len(), rows: epoch_rows,
                            mean_mixture: z, g_positive_fraction: pos, ess_fraction_uniform: eu, ess_fraction_lookahead: el,
                        });
                        epoch_draws.push(EpochDraw { epoch: step.id.clone(), step: k, unix_s: step.unix_s, log_evidence, candidates: drawn });
                    } else {
                        particles.par_iter_mut().enumerate().for_each(|(j, p)| p.tags[slot] = j as u32);
                        let filtered: Vec<f64> = log_weights.iter().map(|lw| lw.exp()).collect();
                        pending.push(PendingLookahead {
                            slot, epoch: step.id.clone(), horizon, step: k, unix_s: step.unix_s, log_evidence, filtered, candidates, g_file: None,
                        });
                    }
                }
            }
        }
        eprintln!(
            "{} seed {seed} {:?} {:>7}: ESS {:>10.0}{} ({:.1} s)",
            case.id,
            mode,
            step.id,
            ess,
            distinct_parents.map(|d| format!(", resampled from {d} parents")).unwrap_or_default(),
            t_step.elapsed().as_secs_f64()
        );
        diagnostics.push(StepDiagnostics {
            epoch: step.id.clone(),
            ess_after_update: ess,
            log_evidence_increment: increment,
            resampled: resample,
            distinct_parents,
            population,
            seconds: t_step.elapsed().as_secs_f64(),
        });
        if let Some(report) = ctx.progress {
            report(&Progress {
                case: case.id.clone(),
                seed,
                mode: format!("{mode:?}"),
                mode_index: stratum as usize,
                epoch: step.id.clone(),
                step_index: k + 1,
                steps: ctx.steps.len(),
                ess,
                particles: n,
                resampled: resample,
                seconds: t_step.elapsed().as_secs_f64(),
            });
        }
    }

    // Branching carried the weights unnormalised all the way through, which is where its
    // evidence estimate lives: the surviving weight sum times everything banked in the
    // rescalings. Normalising here puts the population back on the footing the output,
    // route sampling and hand-off all assume.
    if branching.is_some() {
        let total = log_sum_exp(&log_weights);
        log_evidence = total + log_scale;
        log_weights.par_iter_mut().for_each(|lw| *lw -= total);
    }

    // Compact output: one row per particle (weight normalised within this mode) and a route sample.
    let rows = particles
        .par_iter()
        .zip(&log_weights)
        .map(|(p, lw)| {
            let a = &p.aircraft;
            [
                lw.exp(),
                a.lat,
                a.lon,
                a.alt_ft,
                a.mach,
                a.tau_s / 3600.0,
                f64::from(a.turns),
                f64::from(a.accelerations),
                f64::from(a.climbs),
                f64::from(a.mode as u8),
                p.bias.mean_hz,
                f64::from(p.origin),
                stratum as f64,
                a.fuel_kg,
                a.fuel_exhausted_unix_s,
                a.fuel_below_tables_s,
                a.fuel_extrapolated_s,
                a.fuel_above_ceiling_s,
                a.fuel_no_flow_s,
                a.fuel_no_flow_cause,
                a.fuel_exhausted_unix_s - FINAL_TIME_ORIGIN_UNIX_S,
            ]
        })
        .collect();
    let chosen = systematic_resample(&log_weights, config.output.route_samples, &mut stream(3000, 0));
    let routes = chosen.iter().map(|&j| particles[j].route[..ctx.route_points].to_vec()).collect();
    let origins: Vec<usize> = particles.iter().map(|p| p.origin as usize).collect();
    if let Some(p) = pending.first() {
        return Err(format!("output.handoff_lookahead: the filter stopped before horizon {} of {}", p.horizon, p.epoch));
    }
    let run = ModeRun {
        mode: format!("{mode:?}"),
        prior_weight: f64::NAN,
        log_evidence,
        posterior_probability: f64::NAN,
        final_ess: effective_sample_size(&log_weights),
        distinct_origins: count_distinct(&origins),
        lookahead_resamples,
        handoff_lookahead: lookahead_diagnostics,
        rejuvenation_accepted: rejuvenated[0],
        rejuvenation_proposed: rejuvenated[1],
        epochs: diagnostics,
        runtime_s: started.elapsed().as_secs_f64(),
    };
    // The hand-off draws: equally weighted within this mode; run_case keeps a share of them.
    let candidates = if ctx.handoff > 0 {
        systematic_resample(&log_weights, ctx.handoff, &mut stream(5000, 0))
            .into_iter()
            .map(|j| {
                let p = &particles[j];
                handoff::Candidate { particle: j, aircraft: p.aircraft.clone(), bias: p.bias, origin: p.origin, log_correction: 0.0 }
            })
            .collect()
    } else {
        Vec::new()
    };
    let history = if config.output.history_after_epoch.is_some() {
        particles
            .iter()
            .map(|p| {
                let (end, start) = (p.history(), p.history_start);
                [0, 1, 2, 3].map(|i| f64::from(end[i] - start[i]))
            })
            .collect()
    } else {
        Vec::new()
    };
    let early = if ctx.config.dynamics.early.is_some() {
        particles.iter().map(|p| early_row(&p.aircraft, ctx.prior.unix_s)).collect()
    } else {
        Vec::new()
    };
    let tank_rows = if ctx.config.fuel.as_ref().and_then(|f| f.tanks) == Some(2) {
        particles
            .iter()
            .map(|p| match &p.aircraft.tanks {
                Some(t) => [
                    t.left_kg,
                    t.right_kg,
                    t.ratio,
                    t.left_exhausted_unix_s,
                    t.right_exhausted_unix_s,
                    t.first_exhausted_unix_s(),
                    t.single_engine_s,
                    t.single_engine_above_ceiling_s,
                ],
                None => [f64::NAN; TANK_COLUMNS.len()],
            })
            .collect()
    } else {
        Vec::new()
    };
    Ok((rows, routes, run, snapshots, history, candidates, epoch_draws, early, tank_rows))
}

/// Columns of the residual snapshots written when `output.residual_samples > 0`.
pub const RESIDUAL_COLUMNS: [&str; 11] = [
    "latitude_deg", "longitude_deg", "altitude_ft", "ground_speed_kt", "track_deg", "mach", "tau_h",
    "bto_residual_us", "bfo_innovation_hz", "bfo_predictive_sd_hz", "log_likelihood",
];

/// An equally weighted sample of particles drawn with their weights *before* this step's
/// update, i.e. from the predictive distribution p(x_k | z_1..k-1), with their residuals.
/// Output-only: uses its own random stream and does not change the filter.
fn residual_snapshot(particles: &[Particle], log_weights: &[f64], count: usize, rng: &mut impl Rng) -> Vec<f64> {
    let prior: Vec<f64> = particles.iter().zip(log_weights).map(|(p, lw)| lw - f64::from(p.residual[3])).collect();
    let norm = log_sum_exp(&prior);
    let prior: Vec<f64> = prior.iter().map(|lw| lw - norm).collect();
    systematic_resample(&prior, count, rng)
        .into_iter()
        .flat_map(|j| {
            let p = &particles[j];
            let a = &p.aircraft;
            let track = a.v_east_kt.atan2(a.v_north_kt).to_degrees().rem_euclid(360.0);
            [
                a.lat,
                a.lon,
                a.alt_ft,
                a.v_north_kt.hypot(a.v_east_kt),
                track,
                a.mach,
                a.tau_s / 3600.0,
                f64::from(p.residual[0]),
                f64::from(p.residual[1]),
                f64::from(p.residual[2]),
                f64::from(p.residual[3]),
            ]
        })
        .collect()
}

fn stream_mix(stratum: u64, step: u64) -> u64 {
    (stratum << 16) | step
}

/// Sum of `f(x)` in parallel but in a fixed order: fixed-size chunks summed sequentially,
/// then the chunk sums in order. A plain parallel sum groups additions according to
/// thread scheduling, which makes results differ in the last bits from run to run and,
/// through resampling, occasionally changes the output.
fn ordered_sum(values: &[f64], f: impl Fn(f64) -> f64 + Sync) -> f64 {
    const CHUNK: usize = 1 << 16;
    let partial: Vec<f64> = values.par_chunks(CHUNK).map(|c| c.iter().map(|&v| f(v)).sum::<f64>()).collect();
    partial.iter().sum()
}

fn log_sum_exp(values: &[f64]) -> f64 {
    let max = values.par_iter().cloned().reduce(|| f64::NEG_INFINITY, f64::max);
    max + ordered_sum(values, |v| (v - max).exp()).ln()
}

/// ESS of normalised log-weights.
fn effective_sample_size(log_weights: &[f64]) -> f64 {
    1.0 / ordered_sum(log_weights, |lw| (2.0 * lw).exp())
}

pub fn systematic_resample(log_weights: &[f64], count: usize, rng: &mut impl Rng) -> Vec<usize> {
    let u0: f64 = rng.gen();
    let mut parents = Vec::with_capacity(count);
    let mut cumulative = 0.0;
    let mut j = 0;
    for (i, lw) in log_weights.iter().enumerate() {
        cumulative += lw.exp() * count as f64;
        while j < count && (j as f64 + u0) < cumulative {
            parents.push(i);
            j += 1;
        }
    }
    // Guard against rounding in the final cumulative sum.
    parents.resize(count, log_weights.len() - 1);
    parents
}

/// Ancestry after a resample: member c of the new population descends from the pre-epoch
/// state its parent descended from.
fn compose_ancestry(ancestry: &[usize], parents: &[usize]) -> Vec<usize> {
    parents.iter().map(|&a| ancestry[a]).collect()
}

fn count_distinct(indices: &[usize]) -> usize {
    let mut v = indices.to_vec();
    v.par_sort_unstable();
    v.dedup();
    v.len()
}

#[cfg(test)]
mod tests {
    /// Fuel audit F12: as float32 the unix exhaustion time is quantised to 128 s; the offset
    /// column holds the same instant to better than 1 ms over the whole end of flight.
    #[test]
    fn exhaustion_offset_column_resolves_better_than_a_millisecond() {
        assert_eq!(FINAL_COLUMNS.last(), Some(&"fuel_exhausted_s_after_0000"));
        let mut worst_unix: f64 = 0.0;
        let mut worst_offset: f64 = 0.0;
        for k in 0..20_000 {
            let t = FINAL_TIME_ORIGIN_UNIX_S - 7_200.0 + k as f64 * 0.537;
            worst_unix = worst_unix.max((f64::from(t as f32) - t).abs());
            let off = t - FINAL_TIME_ORIGIN_UNIX_S;
            worst_offset = worst_offset.max((f64::from(off as f32) - off).abs());
        }
        assert!(worst_unix > 30.0, "float32 unix time should be coarse, got {worst_unix}");
        assert!(worst_offset < 1e-3, "offset column error {worst_offset} s");
    }


    /// Core request 10: with g = 1 everywhere and a fully defensive mixture, the look-ahead draw of
    /// K rows from K candidates returns each candidate once, in order, with zero correction - the
    /// current hand-off exactly.
    #[test]
    fn lookahead_with_flat_g_is_the_current_handoff() {
        let g = vec![1.0; 500];
        for eps in [1.0, 0.2] {
            let (picks, corr, z, pos, eu, el) = lookahead_plan(&g, eps, 500, &mut ChaCha8Rng::seed_from_u64(7));
            assert_eq!(picks, (0..500).collect::<Vec<_>>());
            assert!(corr.iter().all(|c| c.abs() < 1e-12));
            assert!((z - 1.0).abs() < 1e-12 && pos == 1.0 && (eu - 1.0).abs() < 1e-12 && (el - 1.0).abs() < 1e-12);
        }
    }

    /// Core request 10: on a toy, the corrected weighted mean of a statistic over the look-ahead
    /// rows matches its uniform mean over the candidates within Monte Carlo error, while the
    /// rows concentrate where g is large (the ESS gain).
    #[test]
    fn lookahead_correction_is_unbiased_and_concentrates() {
        let m = 20_000;
        let mut rng = ChaCha8Rng::seed_from_u64(11);
        // g: about 2% of candidates explain the later data; f is correlated with g.
        let x: Vec<f64> = (0..m).map(|_| rng.gen::<f64>()).collect();
        let g: Vec<f64> = x.iter().map(|&u| if u > 0.98 { 50.0 * (u - 0.98) / 0.02 } else { 0.0 }).collect();
        let f: Vec<f64> = x.iter().map(|&u| u * u).collect();
        let truth = f.iter().zip(&g).map(|(a, b)| a * b).sum::<f64>() / g.iter().sum::<f64>();
        let uniform_mean = f.iter().sum::<f64>() / m as f64;
        let (mut est_f, mut est_fg) = (Vec::new(), Vec::new());
        let mut el_last = 0.0;
        let mut eu_last = 0.0;
        for rep in 0..200 {
            let (picks, corr, _z, _p, eu, el) = lookahead_plan(&g, 0.2, 2_000, &mut ChaCha8Rng::seed_from_u64(1000 + rep));
            let w: Vec<f64> = corr.iter().map(|c| c.exp()).collect();
            let sw: f64 = w.iter().sum();
            est_f.push(picks.iter().zip(&w).map(|(&c, wi)| wi * f[c]).sum::<f64>() / sw);
            let num: f64 = picks.iter().zip(&w).map(|(&c, wi)| wi * g[c] * f[c]).sum();
            let den: f64 = picks.iter().zip(&w).map(|(&c, wi)| wi * g[c]).sum();
            est_fg.push(num / den);
            el_last = el;
            eu_last = eu;
        }
        let mean = |v: &[f64]| v.iter().sum::<f64>() / v.len() as f64;
        let sd = |v: &[f64]| { let mu = mean(v); (v.iter().map(|x| (x - mu).powi(2)).sum::<f64>() / (v.len() - 1) as f64).sqrt() };
        // The unproposed mean of f is recovered (self-normalised: within 4 standard errors).
        assert!((mean(&est_f) - uniform_mean).abs() < 4.0 * sd(&est_f) / (est_f.len() as f64).sqrt() + 2e-3, "{} vs {}", mean(&est_f), uniform_mean);
        // The continuing stage's g-weighted mean is recovered too.
        assert!((mean(&est_fg) - truth).abs() < 4.0 * sd(&est_fg) / (est_fg.len() as f64).sqrt() + 1e-3, "{} vs {}", mean(&est_fg), truth);
        // ESS gain: g alone has ESS about 1.3% of uniform rows; the look-ahead lifts it many-fold.
        assert!(eu_last < 0.02 && el_last > 10.0 * eu_last, "uniform {eu_last} look-ahead {el_last}");
    }
    use super::*;
    use flight::environment::CalmAir;
    use geo::Vec3;
    use hypothesis::Hypothesis;

    /// D3: a trajectory read back from the hand-off and continued on the filter's own stream for
    /// the next step reaches exactly (bit for bit) the state a straight-through run reaches.
    /// Still air, two modes, two BTO epochs to the stop, then an epoch without measurements, at
    /// which the straight run cannot resample, so particle indices stay aligned.
    #[test]
    fn a_handed_off_trajectory_continues_the_filter_exactly() {
        let config: Config = toml::from_str(
            "name = \"handoff\"\nparticles_per_mode = [300, 0, 300, 0, 0]\nseeds = [7]\nresample_ess_fraction = 0.5\n\
             [[cases]]\nid = \"bto\"\nuse_bfo = false\n\
             [inputs]\nobservations = \"-\"\nephemeris = \"-\"\nera5 = \"-\"\nigrf = \"-\"\n\
             [prior]\ntime_utc = \"-\"\nlatitude_deg = 0.0\nlongitude_deg = 90.0\nposition_sd_nm = 0.5\ntrack_deg = 180.0\ntrack_sd_deg = 1.0\n\
             [bfo_bias]\nmean_hz = 150.0\nsd_hz = 25.0\n[output]\nroute_interval_s = 600\nroute_samples = 10\n",
        )
        .unwrap();
        let params = Parameters::default();
        let prior = Prior {
            unix_s: 0.0,
            lat: 0.0,
            lon: 90.0,
            position_sd_nm: 0.5,
            track_deg: 180.0,
            track_sd_deg: 1.0,
            mach_range: params.mach_range,
            mach_gaussian: None,
            altitude_levels: Prior::uniform_altitude_levels(&params),
        };
        let satellite = Vec3::new(18_161.9, 38_060.5, 1_029.9);
        let measured = |id: &str, unix_s: f64, lat: f64| Step {
            id: id.into(),
            unix_s,
            satcom: Some(Epoch {
                id: id.into(),
                unix_s,
                logged_unix_s: unix_s,
                bto_us: Some(bto_us(satellite, lat, 90.0, 35_000.0)),
                bto_sd_us: 29.0,
                bfo_hz: None,
                bfo_sd_hz: f64::NAN,
                cruise_bto: true,
                cruise_bfo: false,
                events: Vec::new(),
                satellite_afc_hz: 0.0,
                satellite_km: satellite,
                satellite_velocity_km_s: Vec3::default(),
            }),
        };
        let steps = [measured("a", 3600.0, -7.9), measured("b", 5400.0, -11.9), Step { id: "c".into(), unix_s: 7200.0, satcom: None }];
        let none: [Box<dyn Hypothesis>; 0] = [];
        let context = |steps: &'static [Step], handoff: usize| Context {
            config: &config,
            params: &params,
            prior: &prior,
            mode_weights: [1.0, 0.0, 1.0, 0.0, 0.0],
            steps,
            environment: &CalmAir,
            hypotheses: &none,
            route_points: (steps.last().unwrap().unix_s / 600.0) as usize + 1,
            progress: None,
            cancel: None,
            handoff,
            handoff_floor: 40,
        };
        let steps: &'static [Step] = Box::leak(Box::new(steps));
        let (stopped, straight) = (context(&steps[..2], 120), context(steps, 0));
        let (case, seed) = (&config.cases[0], 7);

        let dir = std::env::temp_dir().join(format!("handoff-test-{}", std::process::id()));
        std::fs::create_dir_all(&dir).unwrap();
        let (replicate, written) = run_case(&stopped, case, seed, &dir).unwrap();
        let (stop, rows) = handoff::read(&dir).unwrap();
        std::fs::remove_dir_all(&dir).unwrap();
        assert_eq!((stop.epoch.as_str(), stop.step), ("b", 1));
        assert_eq!(rows.len(), written.len());
        // Each mode keeps round(K P(mode)) rows but at least the floor; the rows sum to one.
        for m in [0, 2] {
            let kept = rows.iter().filter(|r| r.mode == m).count();
            let p = replicate.modes[m].posterior_probability;
            assert_eq!(kept, ((120.0 * p).round() as usize).max(40).min(120), "mode {m}");
        }
        assert!((rows.iter().map(|r| r.weight).sum::<f64>() - 1.0).abs() < 1e-12);

        for m in [0, 2] {
            let (expected, ..) = run_filter(&straight, case, seed, m as u64, Mode::ALL[m]).unwrap();
            for row in rows.iter().filter(|r| r.mode == m) {
                let bias = BfoBias { mean_hz: row.bias.mean_hz, variance_hz2: row.bias.variance_hz2 };
                let route = [[f32::NAN; 2]; MAX_ROUTE_POINTS];
                let mut p = Particle { aircraft: row.aircraft.clone(), bias, origin: row.origin, route, residual: [f32::NAN; 4], tags: [u32::MAX; 2], history_start: [0.0; 4], fuel_penalised: false };
                advance(&mut p, 7200.0, &straight, &mut stream(seed, m as u64, stop.step as u64 + 2, row.particle));
                let a = &p.aircraft;
                let e = &expected[row.particle];
                let got = [a.lat, a.lon, a.alt_ft, a.mach, a.tau_s / 3600.0, f64::from(a.turns), p.bias.mean_hz, f64::from(p.origin)];
                let want = [e[1], e[2], e[3], e[4], e[5], e[6], e[10], e[11]];
                assert_eq!(got.map(f64::to_bits), want.map(f64::to_bits), "mode {m}, particle {}", row.particle);
            }
        }
    }

    /// Core request 17 (filter audit F1). A tempered epoch must leave the evidence and the
    /// posterior unchanged against the plain update; tempering only changes how the population
    /// gets there. Still air, one mode, three BTO epochs; the first is mild and does not
    /// resample, so the weights entering the tempered epoch are uneven; the tempered epoch is
    /// sharper, so its stages resample and move; the third scores the moved population.
    /// This toy is well conditioned and is NOT sensitive to the ancestry defect (it passes
    /// before and after the fix, |z| < 0.3): it guards the invariance the fix must keep. The
    /// bookkeeping itself is tested in `ancestry_follows_the_stage_resamples`, and the size in
    /// the real filter is measured by smoke S0 against the same configuration with the defect.
    #[test]
    fn a_tempered_epoch_agrees_with_the_plain_update() {
        let base = "name = \"temper\"\nparticles_per_mode = [4000, 0, 0, 0, 0]\nseeds = [1]\nresample_ess_fraction = {frac}\n\
             [[cases]]\nid = \"bto\"\nuse_bfo = false\n\
             [inputs]\nobservations = \"-\"\nephemeris = \"-\"\nera5 = \"-\"\nigrf = \"-\"\n\
             [prior]\ntime_utc = \"-\"\nlatitude_deg = 0.0\nlongitude_deg = 90.0\nposition_sd_nm = 0.5\ntrack_deg = 180.0\ntrack_sd_deg = 1.0\n\
             [bfo_bias]\nmean_hz = 150.0\nsd_hz = 25.0\n[output]\nroute_interval_s = 600\nroute_samples = 10\n";
        let base = base.replace("{frac}", "0.5");
        let base = base.as_str();
        let plain: Config = toml::from_str(base).unwrap();
        let stages = 8;
        let tempered: Config = toml::from_str(&format!("{base}[sampler]\ntemper_epochs = [\"b\"]\ntemper_stages = {stages}\n")).unwrap();
        let params = Parameters::default();
        let prior = Prior {
            unix_s: 0.0,
            lat: 0.0,
            lon: 90.0,
            position_sd_nm: 0.5,
            track_deg: 180.0,
            track_sd_deg: 1.0,
            mach_range: params.mach_range,
            mach_gaussian: None,
            altitude_levels: Prior::uniform_altitude_levels(&params),
        };
        let satellite = Vec3::new(18_161.9, 38_060.5, 1_029.9);
        let measured = |id: &str, unix_s: f64, lat: f64, sd: f64| Step {
            id: id.into(),
            unix_s,
            satcom: Some(Epoch {
                id: id.into(),
                unix_s,
                logged_unix_s: unix_s,
                bto_us: Some(bto_us(satellite, lat, 90.0, 35_000.0)),
                bto_sd_us: sd,
                bfo_hz: None,
                bfo_sd_hz: f64::NAN,
                cruise_bto: true,
                cruise_bfo: false,
                events: Vec::new(),
                satellite_afc_hz: 0.0,
                satellite_km: satellite,
                satellite_velocity_km_s: Vec3::default(),
            }),
        };
        let steps: &'static [Step] = Box::leak(Box::new([measured("a", 3600.0, -7.0, 120.0), measured("b", 5400.0, -11.9, 20.0), measured("c", 7200.0, -15.9, 29.0)]));
        let none: [Box<dyn Hypothesis>; 0] = [];
        let context = |config: &'static Config| Context {
            config,
            params: &params,
            prior: &prior,
            mode_weights: [1.0, 0.0, 0.0, 0.0, 0.0],
            steps,
            environment: &CalmAir,
            hypotheses: &none,
            route_points: 10,
            progress: None,
            cancel: None,
            handoff: 0,
            handoff_floor: 0,
        };
        let (plain, tempered): (&'static Config, &'static Config) = (Box::leak(Box::new(plain)), Box::leak(Box::new(tempered)));
        // Per seed: log evidence and the posterior mean latitude.
        let summary = |config: &'static Config, seed: u64| {
            let ctx = context(config);
            let (rows, _, run, ..) = run_filter(&ctx, &config.cases[0], seed, 0, Mode::TrueHeading).unwrap();
            let w: f64 = rows.iter().map(|r| r[0]).sum();
            (run.log_evidence, rows.iter().map(|r| r[0] * r[1]).sum::<f64>() / w)
        };
        let seeds: Vec<u64> = (1..=12).collect();
        let stats = |config: &'static Config| {
            let v: Vec<(f64, f64)> = seeds.iter().map(|&s| summary(config, s)).collect();
            let k = v.len() as f64;
            let mean = |f: &dyn Fn(&(f64, f64)) -> f64| v.iter().map(f).sum::<f64>() / k;
            let (mz, ml) = (mean(&|x| x.0), mean(&|x| x.1));
            let se = |f: &dyn Fn(&(f64, f64)) -> f64, m: f64| (v.iter().map(|x| (f(x) - m).powi(2)).sum::<f64>() / (k - 1.0) / k).sqrt();
            (mz, se(&|x| x.0, mz), ml, se(&|x| x.1, ml))
        };
        let (pz, pzs, pl, pls) = stats(plain);
        let (tz, tzs, tl, tls) = stats(tempered);
        let zz = (tz - pz) / (pzs * pzs + tzs * tzs).sqrt();
        let zl = (tl - pl) / (pls * pls + tls * tls).sqrt();
        eprintln!("log Z plain {pz:.4} +/- {pzs:.4}, tempered {tz:.4} +/- {tzs:.4} (z {zz:.2}); lat plain {pl:.5} +/- {pls:.5}, tempered {tl:.5} +/- {tls:.5} (z {zl:.2})");
        assert!(zz.abs() < 4.0 && zl.abs() < 4.0, "tempered and plain disagree: z(log Z) {zz:.2}, z(lat) {zl:.2}");
    }

    /// Core request 17: two stages that resample in turn. Member c of the final population
    /// descends from parents2[c] of stage 2, which descends from parents1[parents2[c]].
    #[test]
    fn ancestry_follows_the_stage_resamples() {
        let start: Vec<usize> = (0..6).collect();
        let parents1 = [0, 0, 2, 3, 3, 5];
        let parents2 = [1, 1, 1, 4, 5, 5];
        let once = compose_ancestry(&start, &parents1);
        assert_eq!(once, parents1);
        let twice = compose_ancestry(&once, &parents2);
        assert_eq!(twice, [0, 0, 0, 3, 5, 5]);
        // The defect re-simulated member c from before_step[parents2[c]]: [1, 1, 1, 4, 5, 5],
        // which names states 1 and 4 that no member descends from.
        assert_ne!(twice, parents2);
    }

    #[test]
    fn weight_sums_are_bit_identical_across_thread_counts() {
        let values: Vec<f64> = (0..1_000_003).map(|i| ((i as f64) * 0.618).sin() * 30.0 - 40.0).collect();
        let sum_with = |threads| {
            let pool = rayon::ThreadPoolBuilder::new().num_threads(threads).build().unwrap();
            pool.install(|| (log_sum_exp(&values), effective_sample_size(&values)))
        };
        let (one, six) = (sum_with(1), sum_with(6));
        assert_eq!(one.0.to_bits(), six.0.to_bits());
        assert_eq!(one.1.to_bits(), six.1.to_bits());
    }

    #[test]
    fn systematic_resampling_is_unbiased_in_counts() {
        let w = [0.1f64, 0.6, 0.3];
        let lw: Vec<f64> = w.iter().map(|x| x.ln()).collect();
        let parents = systematic_resample(&lw, 1000, &mut ChaCha8Rng::seed_from_u64(3));
        for (i, wi) in w.iter().enumerate() {
            let c = parents.iter().filter(|&&p| p == i).count() as f64;
            assert!((c - wi * 1000.0).abs() <= 1.0);
        }
    }
}
