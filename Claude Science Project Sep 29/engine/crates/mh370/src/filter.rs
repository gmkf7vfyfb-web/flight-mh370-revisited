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
pub const FINAL_COLUMNS: [&str; 18] = [
    "weight", "latitude_deg", "longitude_deg", "altitude_ft", "mach", "tau_h", "turns", "accelerations", "climbs", "mode",
    "bfo_bias_hz", "origin", "stratum",
    // NaN throughout when the run does not model fuel. `fuel_exhausted_unix_s` is NaN for a
    // path that still had fuel at the final step; the two coverage columns say how many seconds
    // of the path were flown where the tables needed clamping or extrapolating.
    "fuel_kg", "fuel_exhausted_unix_s", "fuel_below_tables_s", "fuel_extrapolated_s",
    "fuel_above_ceiling_s",
];

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
    seconds: f64,
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
    let mut routes_by_mode = Vec::new();
    let mut runs = Vec::new();
    let mut strata = Vec::new();
    for (m, mode) in Mode::ALL.into_iter().enumerate() {
        let weight = ctx.mode_weights[m];
        let (r, routes, run, snapshots, h, candidates) = if weight > 0.0 {
            run_filter(ctx, case, seed, m as u64, mode)?
        } else {
            (Vec::new(), Vec::new(), ModeRun::skipped(mode), Vec::new(), Vec::new(), Vec::new())
        };
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
            epochs: Vec::new(),
            runtime_s: 0.0,
        }
    }
}

type Snapshot = (String, Vec<f64>);
type History = Vec<[f64; 4]>;
type FilterOutput = (Rows, Vec<Vec<[f32; 2]>>, ModeRun, Vec<Snapshot>, History, Vec<handoff::Candidate>);

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

fn run_filter<E: Environment>(ctx: &Context<E>, case: &Case, seed: u64, stratum: u64, mode: Mode) -> Result<FilterOutput, String> {
    let started = Instant::now();
    let config = ctx.config;
    let (prior, environment) = (ctx.prior, ctx.environment);
    let n = config.particles_per_mode[stratum as usize];
    let params = ctx.params;
    let stream = |step: u64, i: usize| stream(seed, stratum, step, i);
    // Fuel evidence, resolved once: the time the aircraft must still have had fuel at, and the
    // Gaussian on when it ran out. Both are optional and declared in `[fuel]`.
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
            Particle { aircraft, bias, origin: i as u32, route, residual: [f32::NAN; 4], history_start: [0.0; 4], fuel_penalised: false }
        })
        .collect();
    // Auxiliary look-ahead: extra standard deviation, in microseconds, added in quadrature to
    // the epoch's own BTO sd when scoring a dead-reckoned prediction. None disables the step.
    let lookahead_sd_us = config.sampler.as_ref().and_then(|s| s.lookahead_bto_sd_us);
    let mut lookahead_resamples = 0u32;
    let mut log_weights = vec![-(n as f64).ln(); n];
    let mut log_evidence = 0.0;
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
        // in that sliver, which is what the recorded m1941 ESS of 0.08-0.13% measures. The
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
        particles.par_iter_mut().zip(log_weights.par_iter_mut()).enumerate().for_each(|(i, (p, lw))| {
            advance(p, step.unix_s, ctx, &mut stream(k as u64 + 1, i));
            let a = &mut p.aircraft;
            if config.output.history_after_epoch.as_deref() == Some(step.id.as_str()) {
                p.history_start = [f32::from(a.turns), f32::from(a.accelerations), f32::from(a.climbs), a.turned_rad.to_degrees() as f32];
            }
            // The endurance proposal's exact log prior-to-proposal ratio, accumulated over the
            // steps since the last epoch. Draining it here rather than inside the dynamics
            // keeps the correction in the weight and out of the trajectory.
            *lw += std::mem::take(&mut a.fuel_log_weight_correction);
            // A path the fuel state has already ruled out: it cannot reach the deadline on any
            // continuation, so it would be rejected there. Charging the same penalty now lets
            // the resampling that follows reallocate its share while there is still flight to
            // explore. Charged once; the deadline test below then skips it.
            if a.fuel_doomed && !p.fuel_penalised {
                p.fuel_penalised = true;
                *lw += FUEL_REJECT_LOG_PENALTY;
            }
            if let Some(epoch) = &step.satcom {
                let before = *lw;
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
                        *lw += gaussian_log_likelihood(residual, epoch.bto_sd_us);
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
                    *lw += p.bias.update(predicted, z, epoch.bfo_sd_hz);
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
                        *lw += FUEL_REJECT_LOG_PENALTY;
                    }
                }
                p.residual[3] = (*lw - before) as f32;
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
                    *lw += gaussian_log_likelihood(when - target, sd);
                }
            }
            if !ctx.hypotheses.is_empty() {
                let view = p.view();
                for h in ctx.hypotheses {
                    *lw += h.epoch_log_likelihood(&epoch_view, &view);
                    if last {
                        *lw += h.final_log_likelihood(&view);
                    }
                }
            }
        });

        if config.output.residual_samples > 0 && step.satcom.is_some() {
            snapshots.push((step.id.clone(), residual_snapshot(&particles, &log_weights, config.output.residual_samples, &mut stream(4000 + k as u64, 0))));
        }
        let increment = log_sum_exp(&log_weights);
        log_evidence += increment;
        log_weights.par_iter_mut().for_each(|lw| *lw -= increment);
        let ess = effective_sample_size(&log_weights);
        let resample = ess < config.resample_ess_fraction * n as f64;
        let mut distinct_parents = None;
        if resample {
            let parents = systematic_resample(&log_weights, n, &mut stream(2000 + k as u64, 0));
            distinct_parents = Some(count_distinct(&parents));
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
            ]
        })
        .collect();
    let chosen = systematic_resample(&log_weights, config.output.route_samples, &mut stream(3000, 0));
    let routes = chosen.iter().map(|&j| particles[j].route[..ctx.route_points].to_vec()).collect();
    let origins: Vec<usize> = particles.iter().map(|p| p.origin as usize).collect();
    let run = ModeRun {
        mode: format!("{mode:?}"),
        prior_weight: f64::NAN,
        log_evidence,
        posterior_probability: f64::NAN,
        final_ess: effective_sample_size(&log_weights),
        distinct_origins: count_distinct(&origins),
        lookahead_resamples,
        epochs: diagnostics,
        runtime_s: started.elapsed().as_secs_f64(),
    };
    // The hand-off draws: equally weighted within this mode; run_case keeps a share of them.
    let candidates = if ctx.handoff > 0 {
        systematic_resample(&log_weights, ctx.handoff, &mut stream(5000, 0))
            .into_iter()
            .map(|j| {
                let p = &particles[j];
                handoff::Candidate { particle: j, aircraft: p.aircraft.clone(), bias: p.bias, origin: p.origin }
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
    Ok((rows, routes, run, snapshots, history, candidates))
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

fn count_distinct(indices: &[usize]) -> usize {
    let mut v = indices.to_vec();
    v.par_sort_unstable();
    v.dedup();
    v.len()
}

#[cfg(test)]
mod tests {
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
                let mut p = Particle { aircraft: row.aircraft.clone(), bias, origin: row.origin, route, residual: [f32::NAN; 4], history_start: [0.0; 4], fuel_penalised: false };
                advance(&mut p, 7200.0, &straight, &mut stream(seed, m as u64, stop.step as u64 + 2, row.particle));
                let a = &p.aircraft;
                let e = &expected[row.particle];
                let got = [a.lat, a.lon, a.alt_ft, a.mach, a.tau_s / 3600.0, f64::from(a.turns), p.bias.mean_hz, f64::from(p.origin)];
                let want = [e[1], e[2], e[3], e[4], e[5], e[6], e[10], e[11]];
                assert_eq!(got.map(f64::to_bits), want.map(f64::to_bits), "mode {m}, particle {}", row.particle);
            }
        }
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
