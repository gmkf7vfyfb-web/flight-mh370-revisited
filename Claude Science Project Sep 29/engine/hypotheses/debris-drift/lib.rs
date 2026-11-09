//! Debris drift: the likelihood of the recovered-debris evidence given each impact location,
//! by forward transport from a source grid and a recovery-observation model, evaluated at the
//! shared impact samples. Brief: threads/master-prompts/ocean-drift.md; rulings in
//! coordination/OCEAN_DRIFT.md; Davey alignment in results/davey-ch11-alignment.md.
//!
//! STATUS: transport is the shared `ocean` crate (the provisional stub is deleted). Two modes:
//! `synthetic` scores finds generated from a declared source, through any transport, and is
//! never evidence; `evidence` scores the stringent nine through gridded products. Every evidence
//! result is PROVISIONAL until the real coastline exists, because beaching is read from product
//! land-mask stranding (transport.rs).
//!
//! The estimator, and the contract rules each part answers to:
//! - Forward physics only; reverse inference by Bayes. Returns ln p(finds | impact sample, ocean
//!   model); the composer applies the weights (rule 1). No source-cell area factor (rule 1).
//! - One reusable ensemble per (source node, environment realisation, object class);
//!   `source_grid` places nodes over the coverage region of a declared posterior, `interpolate`
//!   reads the surface at each impact sample linearly in L, never extrapolating (rules 3, 4).
//!   Common random numbers across nodes: every node uses the same object-response draws and the
//!   same diffusion streams, so differences between nodes are not inflated by sampling noise.
//! - Recovery layer: the D5 conditional likelihood with the G1 find episodes - nine object
//!   factors, detection blocks (segment x period) with latent relative levels nu marginalised
//!   under a declared prior, lambda cancelled exactly (`recovery`).
//! - Shared environment (diffusivity K, drawn from the shared ocean's DiffusivityPrior) and the
//!   levels nu marginalised ONCE outside the product over finds (rule 8). The ocean model is the
//!   shared alternative `ocean-model`, one option per configuration, never rescaled (rule 7).
//! - Object response per class, drawn once per particle from declared distributions and
//!   persistent (rule 9). Default system is CSIRO's implicit one (rulings D-a, D-b): current plus a
//!   wind fraction plus, for the flaperon, a constant 10 cm/s at theta ~ U(0, 30) deg left of
//!   downwind; no explicit Stokes, declared through `leeway_absorbs_stokes` so the transport
//!   refuses a Stokes field (rule 10). The explicit-Stokes arm is config-gated, default off.
//! - Monte Carlo: a node whose ensemble gives zero for any find is Unresolved, never zero
//!   likelihood; per-find Kish effective counts and a split-half ln L are reported (rule 6).
//!
//! First-pass scope (brief section 6): release at the impact point at `release_unix_s`, floating,
//! no family-dependent release, no resurfacing, no refloating. Coasts outside the declared
//! segments carry no identification (brief section 13 defers the Western Australia term). The
//! first version does not test the mechanisms it assumes away.
//!
//! Departures from Davey et al. (2016) ch. 11 (printed pp. 101-109) are D1-D5 of
//! results/davey-ch11-alignment.md; the GDP-empirical arm (A1) is prepared under prepare/gdp/.

mod evidence;
mod interpolate;
mod recovery;
mod rng;
mod segments;
mod source_grid;
mod transport;

use hypothesis::{Alternatives, Hypothesis, ImpactView};
use interpolate::{Lookup, Node, Surface};
use ocean::{Diffusion, DiffusivityPrior, Domain, ObjectResponse, Particle};
use recovery::{dot, Arrival, Delay, Edge, LevelDraws, Observation, Place, Recovery};
use rng::Rng;
use segments::{Segment, SegmentMap};
use serde::Deserialize;
use source_grid::{SourceGrid, WeightedCell};
use transport::{Episode, Fate, OceanSetup, TransportParams};

const REFERENCE_MAP: &str = include_str!("data/reference-map-no-exhaustion-prior-m0019b.csv");

fn d_coverage() -> f64 { 0.99 }
fn d_spacing() -> f64 { 10.0 }
fn d_margin() -> f64 { 100.0 }
fn d_link() -> f64 { 40.0 }
fn d_particles() -> usize { 1000 }
fn d_seed() -> u64 { 1 }
fn d_release() -> f64 { 1_394_237_977.0 }
fn d_dt() -> f64 { 6.0 }
fn d_threads() -> usize { 2 }
fn d_true() -> bool { true }
fn d_domain() -> [f64; 4] { [15.0, 120.0, -50.0, 0.0] }
fn d_env() -> Vec<u64> { vec![1] }
fn d_stride() -> usize { 1 }
fn d_fixed_zero() -> Dist { Dist::Fixed { value: 0.0 } }

/// A declared sampling distribution (rule 9: sampling a range is marginalisation only if the
/// distribution is stated). Truncation is by rejection.
#[derive(Deserialize, Clone, Debug, PartialEq)]
#[serde(deny_unknown_fields, tag = "dist", rename_all = "kebab-case")]
pub(crate) enum Dist {
    Fixed { value: f64 },
    Uniform { lo: f64, hi: f64 },
    Normal { mean: f64, sd: f64, lo: f64, hi: f64 },
    LogNormal { median: f64, sigma: f64, lo: f64, hi: f64 },
}

impl Dist {
    fn validate(&self) -> Result<(), String> {
        let ok = match *self {
            Dist::Fixed { value } => value.is_finite(),
            Dist::Uniform { lo, hi } => lo <= hi,
            Dist::Normal { mean, sd, lo, hi } => sd >= 0.0 && lo <= hi && mean.is_finite(),
            Dist::LogNormal { median, sigma, lo, hi } => median > 0.0 && sigma >= 0.0 && lo <= hi,
        };
        if ok { Ok(()) } else { Err(format!("debris-drift: bad distribution {self:?}")) }
    }
    fn draw(&self, rng: &mut Rng) -> f64 {
        match *self {
            Dist::Fixed { value } => value,
            Dist::Uniform { lo, hi } => lo + (hi - lo) * rng.uniform(),
            Dist::Normal { mean, sd, lo, hi } => loop {
                let v = mean + sd * rng.normal();
                if (lo..=hi).contains(&v) || sd == 0.0 {
                    return v.clamp(lo, hi);
                }
            },
            Dist::LogNormal { median, sigma, lo, hi } => loop {
                let v = median * (sigma * rng.normal()).exp();
                if (lo..=hi).contains(&v) || sigma == 0.0 {
                    return v.clamp(lo, hi);
                }
            },
        }
    }
}

#[derive(Deserialize, Clone, Debug)]
#[serde(deny_unknown_fields)]
pub(crate) struct ClassParams {
    name: String,
    /// Evidence-table `motion_class` values this class serves.
    #[serde(default)]
    motion_classes: Vec<String>,
    a_stokes: Dist,
    c_wind: Dist,
    /// Deflection of the `c_wind` term from downwind, positive clockwise (ruling D-f; default 0,
    /// CSIRO's proportional windage being downwind).
    #[serde(default = "d_fixed_zero")]
    wind_angle_deg: Dist,
    /// Deflection of the constant-magnitude `leeway_speed_mps` term only, positive clockwise from
    /// downwind (the shared API's sign): CSIRO's "left" is negative (Part II p. 13; ruling D-f).
    leeway_angle_deg: Dist,
    leeway_speed_mps: Dist,
}

#[derive(Deserialize, Clone, Debug)]
#[serde(deny_unknown_fields, tag = "kind", rename_all = "kebab-case")]
enum DiffusivityParams {
    Fixed { k_m2_s: f64 },
    LogUniform { k_min_m2_s: f64, k_max_m2_s: f64 },
}

#[derive(Deserialize, Clone, Debug)]
#[serde(deny_unknown_fields)]
struct RecoveryParams {
    bandwidth_km: f64,
    delay: String,
    delay_days: f64,
    /// ISO dates bounding the discovery periods (G1: I1 | I2 | I3).
    period_breaks: Vec<String>,
    /// ISO date ending the discovery window.
    window_end: String,
    /// Further bandwidths reported as sensitivity columns (`ln_l_h<km>`), same ensembles.
    #[serde(default)]
    extra_bandwidths_km: Vec<f64>,
    /// Chainage edges on coast line 0 (analytic straight coast only); segments are then the
    /// intervals between consecutive edges.
    #[serde(default)]
    segment_edges_km: Vec<f64>,
}

#[derive(Deserialize, Clone, Debug)]
#[serde(deny_unknown_fields)]
struct LevelParams {
    /// ln of the relative identification level by period (prior mean), one per period.
    ln_mean_by_period: Vec<f64>,
    sigma: f64,
    draws: usize,
    seed: u64,
    /// Per-segment overrides of `ln_mean_by_period` for the primary surface (e.g. coasts with no finds).
    #[serde(default)]
    segment_ln_mean_by_period: Vec<SegmentLevel>,
    /// Further level priors scored from the same ensembles, written as `ln_l_lev_<name>` (+ halves).
    /// Each is `ln_mean_by_period` with its own per-segment overrides (the primary overrides do not apply).
    #[serde(default)]
    alternatives: Vec<LevelAlternative>,
}

#[derive(Deserialize, Clone, Debug)]
#[serde(deny_unknown_fields)]
struct SegmentLevel {
    segment: String,
    ln_mean_by_period: Vec<f64>,
}

#[derive(Deserialize, Clone, Debug)]
#[serde(deny_unknown_fields)]
struct LevelAlternative {
    name: String,
    #[serde(default)]
    segment_ln_mean_by_period: Vec<SegmentLevel>,
}

/// Prior mean of ln nu per block (segment * n_periods + period): `base` by period, with per-segment overrides.
fn block_means(base: &[f64], overrides: &[SegmentLevel], segnames: &[String]) -> Result<Vec<f64>, String> {
    let np = base.len();
    let mut mu: Vec<f64> = (0..segnames.len() * np).map(|b| base[b % np]).collect();
    for o in overrides {
        let s = segnames.iter().position(|n| *n == o.segment).ok_or_else(|| format!("debris-drift: level override for unknown segment `{}`", o.segment))?;
        if o.ln_mean_by_period.len() != np {
            return Err(format!("debris-drift: level override for `{}` has {} periods, expected {np}", o.segment, o.ln_mean_by_period.len()));
        }
        mu[s * np..(s + 1) * np].copy_from_slice(&o.ln_mean_by_period);
    }
    Ok(mu)
}

#[derive(Deserialize, Clone, Debug)]
#[serde(deny_unknown_fields)]
struct SyntheticParams {
    true_lat_deg: f64,
    true_lon_deg: f64,
    finds: usize,
    seed: u64,
    #[serde(default)]
    class: usize,
}

#[derive(Deserialize, Clone, Debug)]
#[serde(deny_unknown_fields)]
struct ShadowFind {
    /// Label in the coefficient file (`shadow:<name>`).
    name: String,
    /// Row of the evidence table (any row, not only the stringent set).
    object_id: String,
    /// Discovery interval; defaults to the table's dates. An end without a start is refused.
    #[serde(default)]
    discovery_start: Option<String>,
    #[serde(default)]
    discovery_end: Option<String>,
    /// Freshness mark (biofouling, observed arrival): P(fresh | time ashore tau) = exp(-tau / fresh_days).
    /// With the exponential delay of mean D this find's kernel uses an exponential delay of mean D F / (D + F);
    /// the constant factor (D_eff / D) is the same at every node and cancels. The class total A is unchanged
    /// (a mark does not change the expected number of finds). Needs the exponential delay.
    #[serde(default)]
    fresh_days: Option<f64>,
}

#[derive(Deserialize, Clone, Debug)]
#[serde(deny_unknown_fields)]
struct DateOverride {
    object_id: String,
    discovery_start: String,
    discovery_end: String,
}

#[derive(Deserialize, Clone, Debug)]
#[serde(deny_unknown_fields)]
pub(crate) struct Params {
    mode: String,
    #[serde(default = "d_coverage")]
    coverage: f64,
    #[serde(default = "d_spacing")]
    spacing_nm: f64,
    #[serde(default = "d_margin")]
    margin_nm: f64,
    #[serde(default = "d_link")]
    island_link_nm: f64,
    #[serde(default)]
    include_island: bool,
    #[serde(default)]
    extent_map_path: Option<String>,
    /// Particles per (node, environment realisation, class).
    #[serde(default = "d_particles")]
    particles_per_class: usize,
    #[serde(default = "d_seed")]
    seed: u64,
    #[serde(default = "d_release")]
    release_unix_s: f64,
    #[serde(default = "d_dt")]
    dt_hours: f64,
    #[serde(default = "d_threads")]
    threads: usize,
    #[serde(default = "d_domain")]
    domain: [f64; 4],
    #[serde(default = "d_true")]
    land_gap_is_beaching: bool,
    #[serde(default = "d_true")]
    leeway_absorbs_stokes: bool,
    #[serde(default)]
    explicit_residual: bool,
    /// Declared sensitivity: refloat rate per day after beaching (0 = off, the default).
    #[serde(default)]
    refloat_per_day: f64,
    transport: TransportParams,
    diffusivity: DiffusivityParams,
    /// One shared-environment realisation per seed (K drawn from the prior with that seed).
    #[serde(default = "d_env")]
    env_seeds: Vec<u64>,
    classes: Vec<ClassParams>,
    #[serde(default)]
    segments: Vec<Segment>,
    recovery: RecoveryParams,
    levels: LevelParams,
    #[serde(default)]
    synthetic: Option<SyntheticParams>,
    #[serde(default)]
    date_overrides: Vec<DateOverride>,
    /// Keep only the scored finds of the named classes (evidence mode). A class without a scored find is not
    /// transported, so a run for one class costs about that class's share. Empty (default) keeps every class:
    /// byte-identical. Shadow finds of a dropped class must be removed from the configuration.
    #[serde(default)]
    restrict_to_classes: Vec<String>,
    /// Restrict release to these node indices (smoke tests); empty means every active node.
    #[serde(default)]
    node_subset: Vec<usize>,
    /// Let `node_subset` name grid nodes outside the extent map (component -1): coverage extensions on the
    /// SAME grid, so their values merge cell-for-cell with the main run. Off by default (byte-identical).
    #[serde(default)]
    node_subset_outside_extent: bool,
    /// Product-relative windage (audit F1, 10 Oct): added to every drawn `c_wind` (fraction of U10, e.g. -0.006),
    /// floored at zero, for a current product that already carries part of the near-surface wind drift. Default 0
    /// (byte-identical; the reproduction and GLORYS12 arms leave it at 0).
    #[serde(default)]
    c_wind_product_offset: f64,
    /// Product-relative windage drawn per particle, uniform in [lo, hi] (fractions of U10, e.g. [-0.0075, -0.0060]),
    /// from its own random stream so every other response draw is identical to a fixed-offset run. Replaces
    /// `c_wind_product_offset` when set (validation refuses both). Default None (byte-identical).
    #[serde(default)]
    c_wind_product_offset_range: Option<[f64; 2]>,
    /// Release every n-th active node only (checks; production uses 1).
    #[serde(default = "d_stride")]
    node_stride: usize,
    /// First active node taken when striding (chunked runs: offsets 0..stride cover every node).
    #[serde(default)]
    node_offset: usize,
    /// Write the node table and summary here (pilot and diagnostics).
    #[serde(default)]
    output_dir: Option<String>,
    /// Also write the per-node, per-environment, per-class recovery coefficients (`coefficients.jsonl`)
    /// and the level-draw matrix (`coefficients-meta.json`) to `output_dir`, so that any subset of finds,
    /// any level prior and any detection scheme can be scored offline exactly. Output only; off by
    /// default (node table byte-identical either way).
    #[serde(default)]
    write_coefficients: bool,
    /// Extra finds or alternative dates scored from the SAME ensembles and written to the coefficient file only
    /// (never to ln L): later finds, disputed dates. Any subset is then an exact offline choice. Needs write_coefficients.
    #[serde(default)]
    shadow_finds: Vec<ShadowFind>,
    /// Write every beaching of every scored class, node and environment to `arrivals.bin`, and the class
    /// response draws to `responses.json`, so that the recovery layer (segments, delay and freshness models,
    /// identity weights, windage reweighting inside the sampled range, kernel, periods) can be re-run offline.
    /// Output only: node table unchanged. Needs output_dir.
    #[serde(default)]
    write_arrivals: bool,
    /// Importance splitting for finds that forward release alone cannot resolve (off by default).
    #[serde(default)]
    splitting: Option<SplittingParams>,
    /// Transport-model error as the shared ocean's eddying error field, one realisation per
    /// environment seed (off by default). Values from ocean transport's GDP replay
    /// (`results/ocean-transport-error-gdp-replay.md`) once ruled.
    #[serde(default)]
    pub(crate) ocean_error: Option<OceanErrorParams>,
}

#[derive(Deserialize, Clone, Debug)]
#[serde(deny_unknown_fields)]
pub(crate) struct OceanErrorParams {
    pub(crate) sigma_m_s: f64,
    pub(crate) length_scale_km: f64,
    pub(crate) time_scale_days: f64,
    #[serde(default = "d_modes")]
    pub(crate) modes: usize,
}

fn d_modes() -> usize {
    64
}

/// Fixed-factor importance splitting (a variance-reduction device, not a model change). A particle
/// of a listed class whose afloat position, sampled every `snapshot_hours`, first comes within
/// `radius_km` of a target is replaced at that time and place by `factor` children with the same
/// response, independent diffusion and weight 1/factor each. Every statistic is a weighted sum
/// over trajectories, so its expectation is unchanged (the transport is Markov in position and
/// time given the response); only its Monte Carlo variance changes.
#[derive(Deserialize, Clone, Debug)]
#[serde(deny_unknown_fields)]
pub(crate) struct SplittingParams {
    pub(crate) targets: Vec<SplitTarget>,
    pub(crate) factor: usize,
    #[serde(default = "d_snapshot_hours")]
    pub(crate) snapshot_hours: f64,
    /// Class names that split; empty means every class.
    #[serde(default)]
    pub(crate) classes: Vec<String>,
}

#[derive(Deserialize, Clone, Debug)]
#[serde(deny_unknown_fields)]
pub(crate) struct SplitTarget {
    pub(crate) name: String,
    pub(crate) lon_deg: f64,
    pub(crate) lat_deg: f64,
    pub(crate) radius_km: f64,
    /// Overrides `SplittingParams::factor` for this target.
    #[serde(default)]
    pub(crate) factor: Option<usize>,
}

fn d_snapshot_hours() -> f64 {
    24.0
}

pub(crate) fn parse_cells(text: &str) -> Result<Vec<WeightedCell>, String> {
    let mut out = Vec::new();
    for line in text.lines() {
        let l = line.trim();
        if l.is_empty() || l.starts_with('#') || l.starts_with("lat") {
            continue;
        }
        let f: Vec<f64> = l.split(',').map(|x| x.trim().parse::<f64>()).collect::<Result<_, _>>().map_err(|e| format!("extent map: {e} in `{l}`"))?;
        if f.len() != 3 {
            return Err(format!("extent map: expected 3 fields in `{l}`"));
        }
        out.push(WeightedCell { lat: f[0], lon: f[1], mass: f[2] });
    }
    Ok(out)
}

fn day_of(release: f64, iso: &str) -> Result<f64, String> {
    Ok((evidence::iso_date_unix_s(iso)? - release) / 86_400.0)
}

#[cfg(test)]
fn draw_response(c: &ClassParams, rng: &mut Rng) -> ObjectResponse {
    draw_response_offset(c, rng, 0.0)
}

/// As `draw_response`, with the product-relative windage offset added to every drawn `c_wind` and floored at
/// zero (audit F1, 10 Oct: a current that already carries part of the wind drift needs less object windage).
/// The draw sequence is unchanged, so an offset of 0 reproduces `draw_response` exactly.
fn draw_response_offset(c: &ClassParams, rng: &mut Rng, c_wind_offset: f64) -> ObjectResponse {
    {
    let (a, w) = (c.a_stokes.draw(rng), c.c_wind.draw(rng));
    let w = if c_wind_offset == 0.0 { w } else { (w + c_wind_offset).max(0.0) };
    let (la, ls) = (c.leeway_angle_deg.draw(rng), c.leeway_speed_mps.draw(rng));
    transport::response(a, w, c.wind_angle_deg.draw(rng), la, ls)
    }
}

/// The common response draws of class `c` (shared by every node: common random numbers).
fn class_responses(p: &Params, c: usize) -> Vec<ObjectResponse> {
    let mut rng = Rng::derive(&[p.seed, 0xC1A5, c as u64]);
    match p.c_wind_product_offset_range {
        None => (0..p.particles_per_class).map(|_| draw_response_offset(&p.classes[c], &mut rng, p.c_wind_product_offset)).collect(),
        Some([lo, hi]) => {
            let mut off_rng = Rng::derive(&[p.seed, 0x0FF5E7, c as u64]);
            (0..p.particles_per_class).map(|_| draw_response_offset(&p.classes[c], &mut rng, lo + (hi - lo) * off_rng.uniform())).collect()
        }
    }
}

/// Where a beaching sits for the recovery layer.
struct Locator {
    map: Option<SegmentMap>,
    edges: Vec<Edge>,
}

impl Locator {
    fn arrival(&self, t_days: f64, at: [f64; 2], line: Option<u32>, chainage_km: f64) -> Arrival {
        let place = match line {
            Some(l) if chainage_km.is_finite() => Place::on_line(l, chainage_km, at),
            _ => Place::at(at),
        };
        let segment = match (&self.map, place.line) {
            (Some(m), _) => m.locate(at),
            (None, Some(l)) => self.edges.iter().find(|e| e.line == l && place.s_km >= e.start_km && place.s_km < e.end_km).map(|e| e.segment),
            (None, None) => None,
        };
        Arrival { place, segment, t_days, t_leave_days: f64::INFINITY, w: 1.0 }
    }
}

/// One ensemble's beachings, with the particle index of each, and its counts.
struct Ensemble {
    /// (released-particle index, arrival); children carry their parent's index.
    arrivals: Vec<(usize, Arrival)>,
    /// Weighted counts (a child counts 1/factor).
    model_error: f64,
    left_domain: f64,
    on_land: usize,
    /// Released particles that were split, and children integrated.
    split: usize,
    children: usize,
}

fn run_ensemble(setup: &OceanSetup, loc: &Locator, release: [f64; 2], t0: f64, t_end: f64, responses: &[ObjectResponse], seed: u64, diffusion: Diffusion, split: Option<&SplittingParams>) -> Result<(Ensemble, f64), String> {
    let particles: Vec<Particle> = responses.iter().map(|&response| Particle::new(release, t0, response)).collect();
    let mut e = Ensemble { arrivals: Vec::new(), model_error: 0.0, left_domain: 0.0, on_land: 0, split: 0, children: 0 };
    // Arrivals come from the beaching episodes (one per stay on the coast; with refloat off, the
    // first beaching only, as before); the fate gives the non-beach counts.
    let tally = |e: &mut Ensemble, i: usize, f: Fate, eps: &[Episode], w: f64| {
        for ep in eps {
            let mut a = loc.arrival((ep.t - t0) / 86_400.0, ep.at, ep.line, ep.chainage_km);
            a.t_leave_days = (ep.t_leave - t0) / 86_400.0;
            a.w = w;
            e.arrivals.push((i, a));
        }
        match f {
            Fate::Beached { .. } | Fate::Afloat => {}
            Fate::LeftDomain => e.left_domain += w,
            Fate::ReleasedOnLand => e.on_land += 1,
            Fate::ModelError => e.model_error += w,
        }
    };
    let Some(sp) = split.filter(|s| !s.targets.is_empty() && s.targets.iter().any(|g| g.factor.unwrap_or(s.factor) > 1)) else {
        let (fates, eps, steps) = setup.run_ep(&particles, seed, diffusion, t_end)?;
        for (i, f) in fates.into_iter().enumerate() {
            tally(&mut e, i, f, &eps[i], 1.0);
        }
        return Ok((e, steps));
    };
    let dt = sp.snapshot_hours * 3600.0;
    let mut times: Vec<f64> = (1..).map(|k| t0 + k as f64 * dt).take_while(|&t| t < t_end).collect();
    times.push(t_end);
    let (fates, eps, pos, mut steps) = setup.run_tracks_ep(&particles, seed, diffusion, &times)?;
    let mut kids: Vec<Particle> = Vec::new();
    let mut parent: Vec<usize> = Vec::new();
    let mut weight: Vec<f64> = Vec::new();
    for (i, f) in fates.into_iter().enumerate() {
        let entry = pos[i].iter().enumerate().take(times.len() - 1).find_map(|(k, p)| {
            p.and_then(|at| sp.targets.iter().find(|g| ocean::distance_m(at, [g.lon_deg, g.lat_deg]) <= g.radius_km * 1000.0).map(|g| (times[k], at, g.factor.unwrap_or(sp.factor).max(1))))
        });
        match entry {
            // Entered a target zone while afloat: everything after the entry is replaced by the
            // children (weight 1/m each), so the parent's own fate (necessarily later) is discarded.
            Some((te, at, m)) if m > 1 => {
                e.split += 1;
                for _ in 0..m {
                    kids.push(Particle::new(at, te, particles[i].response));
                    parent.push(i);
                    weight.push(1.0 / m as f64);
                }
            }
            _ => tally(&mut e, i, f, &eps[i], 1.0),
        }
    }
    if !kids.is_empty() {
        // The children run under the SAME seed, so they see the same ocean-error realisation as
        // their parents (one realisation per seed), with diffusion streams that are their own:
        // the integrator keys each particle's stream on (seed, index), so n inert placeholders
        // (ending at release, zero steps) push the children's indices past every parent's.
        let n = particles.len();
        let mut batch: Vec<Particle> = particles.iter().map(|q| Particle { end_time: Some(q.release_time), ..*q }).collect();
        batch.extend(kids.iter().copied());
        let (kf, keps, ks) = setup.run_ep(&batch, seed, diffusion, t_end)?;
        steps += ks;
        e.children = kids.len();
        for (k, f) in kf.into_iter().enumerate().skip(n) {
            tally(&mut e, parent[k - n], f, &keps[k], weight[k - n]);
        }
    }
    Ok((e, steps))
}

/// ln L at one node from per-(environment, class) coefficients, marginalising environment and
/// levels outside the product over finds. `coef[e][c]` covers the finds `by_class[c]`.
fn node_ln_likelihood(coef: &[Vec<Option<recovery::Coefficients>>], by_class: &[Vec<usize>], levels: &LevelDraws) -> Node {
    node_ln_likelihood_zeros(coef, by_class, levels).0
}

/// As `node_ln_likelihood`, also returning the fraction of environment realisations whose
/// product is zero (some find with no particle in its kernel). A zero environment term is the
/// unbiased Monte Carlo estimate of a small positive value and enters the mean over environments
/// as zero; it is not floored. The node is Unresolved only when every environment's product is
/// zero (with one environment: whenever any find has no particle, as before).
fn node_ln_likelihood_zeros(coef: &[Vec<Option<recovery::Coefficients>>], by_class: &[Vec<usize>], levels: &LevelDraws) -> (Node, f64) {
    let mut terms = Vec::with_capacity(coef.len() * levels.draws.len());
    let mut zero_envs = 0usize;
    for env in coef {
        let mut env_zero = false;
        for nu in &levels.draws {
            let mut s = 0.0;
            'classes: for (c, finds) in by_class.iter().enumerate() {
                let Some(k) = &env[c] else { continue };
                let q_tot = dot(&k.big_a, nu);
                for (jj, _) in finds.iter().enumerate() {
                    let q = dot(&k.a[jj], nu);
                    if !(q > 0.0) || !(q_tot > 0.0) {
                        s = f64::NEG_INFINITY;
                        env_zero = true;
                        break 'classes;
                    }
                    s += q.ln() - q_tot.ln();
                }
            }
            terms.push(s);
        }
        zero_envs += env_zero as usize;
    }
    let zf = zero_envs as f64 / coef.len().max(1) as f64;
    let m = terms.iter().copied().fold(f64::NEG_INFINITY, f64::max);
    if !m.is_finite() {
        return (Node::Unresolved, zf);
    }
    (Node::Value(m + terms.iter().map(|v| (v - m).exp()).sum::<f64>().ln() - (terms.len() as f64).ln()), zf)
}

pub(crate) struct Built {
    pub grid: SourceGrid,
    pub surface: Surface,
    pub observations: Vec<Observation>,
    pub ocean_model: String,
    pub summary: Vec<(String, String)>,
}

fn build_recovery(p: &Params) -> Result<(Recovery, Locator), String> {
    let rp = &p.recovery;
    let delay = match rp.delay.as_str() {
        "uniform" => Delay::Uniform { max_days: rp.delay_days },
        "exponential" => Delay::Exponential { mean_days: rp.delay_days },
        d => return Err(format!("debris-drift: unknown delay `{d}`")),
    };
    let breaks: Vec<f64> = rp.period_breaks.iter().map(|d| day_of(p.release_unix_s, d)).collect::<Result<_, _>>()?;
    if breaks.windows(2).any(|w| w[1] <= w[0]) {
        return Err("debris-drift: period breaks must increase".into());
    }
    let window_end_days = day_of(p.release_unix_s, &rp.window_end)?;
    let (n_segments, map, edges) = if !p.segments.is_empty() {
        let m = SegmentMap::new(p.segments.clone())?;
        (m.len(), Some(m), Vec::new())
    } else if rp.segment_edges_km.len() >= 2 {
        let e = &rp.segment_edges_km;
        if e.windows(2).any(|w| w[1] <= w[0]) {
            return Err("debris-drift: segment edges must increase".into());
        }
        let edges = e.windows(2).enumerate().map(|(k, w)| Edge { line: 0, start_km: w[0], end_km: w[1], segment: k }).collect();
        (e.len() - 1, None, edges)
    } else {
        return Err("debris-drift: declare `segments` (boxes) or `recovery.segment_edges_km`".into());
    };
    if p.levels.ln_mean_by_period.len() != breaks.len() + 1 {
        return Err(format!("debris-drift: {} periods but {} level means", breaks.len() + 1, p.levels.ln_mean_by_period.len()));
    }
    let rec = Recovery { n_segments, breaks_days: breaks, edges: edges.clone(), delay, bandwidth_km: rp.bandwidth_km, window_end_days };
    Ok((rec, Locator { map, edges }))
}

fn evidence_observations(p: &Params, rec: &Recovery, loc: &Locator) -> Result<Vec<Observation>, String> {
    let map = loc.map.as_ref().ok_or("debris-drift: evidence mode needs geographic `segments`")?;
    let mut out = Vec::new();
    for r in evidence::parse(evidence::TABLE)?.into_iter().filter(|r| r.stringent) {
        let (ds, de) = match p.date_overrides.iter().find(|o| o.object_id == r.object_id) {
            Some(o) => (o.discovery_start.clone(), o.discovery_end.clone()),
            None => (r.discovery_start.clone(), r.discovery_end.clone()),
        };
        let class = p.classes.iter().position(|c| c.motion_classes.contains(&r.motion_class)).ok_or(format!("debris-drift: no class serves motion_class `{}`", r.motion_class))?;
        if !p.restrict_to_classes.is_empty() && !p.restrict_to_classes.contains(&p.classes[class].name) {
            continue;
        }
        let at = [r.longitude_deg, r.latitude_deg];
        let segment = map.locate(at).ok_or(format!("debris-drift: find `{}` lies in no declared segment", r.object_id))?;
        let (a, b) = (day_of(p.release_unix_s, &ds)?, day_of(p.release_unix_s, &de)? + 1.0);
        if b > rec.window_end_days {
            return Err(format!("debris-drift: find `{}` is discovered after the window end", r.object_id));
        }
        out.push(Observation { id: format!("debris:{}", r.object_id), class, place: Place::at(at), segment, t_start_days: a, t_end_days: b });
    }
    Ok(out)
}

/// Shadow finds (coefficient output only): the same construction as `evidence_observations`, for named table rows.
fn shadow_observations(p: &Params, rec: &Recovery, loc: &Locator) -> Result<Vec<Observation>, String> {
    if p.shadow_finds.is_empty() {
        return Ok(Vec::new());
    }
    let map = loc.map.as_ref().ok_or("debris-drift: shadow finds need geographic `segments`")?;
    let table = evidence::parse(evidence::TABLE)?;
    let mut out = Vec::new();
    for s in &p.shadow_finds {
        let r = table.iter().find(|r| r.object_id == s.object_id).ok_or(format!("debris-drift: shadow find `{}`: no table row `{}`", s.name, s.object_id))?;
        let (ds, de) = match (&s.discovery_start, &s.discovery_end) {
            (Some(a), Some(b)) => (a.clone(), b.clone()),
            (Some(a), None) => (a.clone(), a.clone()),
            (None, None) => (r.discovery_start.clone(), r.discovery_end.clone()),
            (None, Some(_)) => return Err(format!("debris-drift: shadow find `{}` has an end date without a start date", s.name)),
        };
        let class = p.classes.iter().position(|c| c.motion_classes.contains(&r.motion_class)).ok_or(format!("debris-drift: no class serves motion_class `{}`", r.motion_class))?;
        let at = [r.longitude_deg, r.latitude_deg];
        let segment = map.locate(at).ok_or(format!("debris-drift: shadow find `{}` lies in no declared segment", s.name))?;
        let (a, b) = (day_of(p.release_unix_s, &ds)?, day_of(p.release_unix_s, &de)? + 1.0);
        if b > rec.window_end_days {
            return Err(format!("debris-drift: shadow find `{}` is discovered after the window end", s.name));
        }
        if let Some(f) = s.fresh_days {
            if !(f > 0.0) || !matches!(rec.delay, Delay::Exponential { .. }) {
                return Err(format!("debris-drift: shadow find `{}`: fresh_days needs a positive value and the exponential delay", s.name));
            }
        }
        out.push(Observation { id: format!("shadow:{}", s.name), class, place: Place::at(at), segment, t_start_days: a, t_end_days: b });
    }
    Ok(out)
}

/// Shadow coefficients for one class: shadows without a freshness mark in one call (the plain kernel),
/// each marked shadow with its own shortened exponential delay. A is always the primary-delay class total.
fn shadow_coefficients(rr: &Recovery, sobs: &[&Observation], fresh: &[Option<f64>], arr: &[Arrival], n: usize) -> recovery::Coefficients {
    let plain: Vec<usize> = (0..sobs.len()).filter(|&k| fresh[k].is_none()).collect();
    if plain.len() == sobs.len() {
        return rr.coefficients(sobs, arr, n);
    }
    let m = sobs.len();
    let (mut a, mut n_eff, mut hits) = (vec![Vec::new(); m], vec![0.0; m], vec![0usize; m]);
    let big_a;
    if plain.is_empty() {
        big_a = rr.coefficients(&[], arr, n).big_a;
    } else {
        let po: Vec<&Observation> = plain.iter().map(|&k| sobs[k]).collect();
        let k0 = rr.coefficients(&po, arr, n);
        for (i, &k) in plain.iter().enumerate() {
            a[k] = k0.a[i].clone();
            n_eff[k] = k0.n_eff[i];
            hits[k] = k0.hits[i];
        }
        big_a = k0.big_a;
    }
    for k in 0..m {
        if let Some(f) = fresh[k] {
            let d = match rr.delay { Delay::Exponential { mean_days } => mean_days, Delay::Uniform { .. } => unreachable!("checked in shadow_observations") };
            let rf = Recovery { delay: Delay::Exponential { mean_days: d * f / (d + f) }, ..rr.clone() };
            let kk = rf.coefficients(&[sobs[k]], arr, n);
            a[k] = kk.a[0].clone();
            n_eff[k] = kk.n_eff[0];
            hits[k] = kk.hits[0];
        }
    }
    recovery::Coefficients { a, big_a, n_eff, hits }
}

/// One block of `arrivals.bin` (little-endian). Header 60 bytes: b"ARV1", node u32, lat f64, lon f64,
/// environment seed u64, class u32, released u32, n_arrivals u32, model_error f64, left_domain f64.
/// Then n_arrivals records of 52 bytes: particle u32, weight f32, t_days f64, t_leave_days f32 (inf = no
/// refloat), lon f64, lat f64, coast line i32 (-1 none), chainage_km f64, segment i32 (-1 = no segment).
fn write_arrival_block(w: &mut impl std::io::Write, node: usize, lat: f64, lon: f64, env_seed: u64, class: usize, released: usize, e: &Ensemble) -> Result<(), String> {
    let mut b: Vec<u8> = Vec::with_capacity(60 + 52 * e.arrivals.len());
    b.extend_from_slice(b"ARV1");
    b.extend_from_slice(&(node as u32).to_le_bytes());
    b.extend_from_slice(&lat.to_le_bytes());
    b.extend_from_slice(&lon.to_le_bytes());
    b.extend_from_slice(&env_seed.to_le_bytes());
    b.extend_from_slice(&(class as u32).to_le_bytes());
    b.extend_from_slice(&(released as u32).to_le_bytes());
    b.extend_from_slice(&(e.arrivals.len() as u32).to_le_bytes());
    b.extend_from_slice(&e.model_error.to_le_bytes());
    b.extend_from_slice(&e.left_domain.to_le_bytes());
    for (i, a) in &e.arrivals {
        b.extend_from_slice(&(*i as u32).to_le_bytes());
        b.extend_from_slice(&(a.w as f32).to_le_bytes());
        b.extend_from_slice(&a.t_days.to_le_bytes());
        b.extend_from_slice(&(a.t_leave_days as f32).to_le_bytes());
        b.extend_from_slice(&a.place.lonlat[0].to_le_bytes());
        b.extend_from_slice(&a.place.lonlat[1].to_le_bytes());
        b.extend_from_slice(&a.place.line.map_or(-1i32, |l| l as i32).to_le_bytes());
        b.extend_from_slice(&a.place.s_km.to_le_bytes());
        b.extend_from_slice(&a.segment.map_or(-1i32, |g| g as i32).to_le_bytes());
    }
    w.write_all(&b).map_err(|e| e.to_string())
}

/// Synthetic finds from an INDEPENDENT ensemble at the declared source (no inverse crime): a
/// beached particle is discovered after a delay from the declared model, reported at a locality
/// displaced along the coast by the bandwidth (chainage mode; no displacement without chainage),
/// and identified with probability proportional to the prior-median level of its block.
fn synthetic_observations(p: &Params, setup: &OceanSetup, rec: &Recovery, loc: &Locator, diffusion: Diffusion) -> Result<Vec<Observation>, String> {
    let s = p.synthetic.as_ref().ok_or("debris-drift: synthetic mode needs [synthetic]")?;
    let class = &p.classes[s.class];
    let mut rng = Rng::derive(&[s.seed, 0x5F1D5]);
    let level = |seg: usize, t: f64| p.levels.ln_mean_by_period[rec.period(t)].exp() * if seg < rec.n_segments { 1.0 } else { 0.0 };
    let lmax = p.levels.ln_mean_by_period.iter().copied().fold(f64::NEG_INFINITY, f64::max).exp();
    let t_end = p.release_unix_s + rec.window_end_days * 86_400.0;
    let mut out = Vec::new();
    for batch in 0..200u64 {
        let responses: Vec<ObjectResponse> = (0..1000).map(|_| draw_response_offset(class, &mut rng, p.c_wind_product_offset)).collect();
        let (e, _) = run_ensemble(setup, loc, [s.true_lon_deg, s.true_lat_deg], p.release_unix_s, t_end, &responses, s.seed ^ ((batch + 1) << 32), diffusion, None)?;
        for (_, a) in e.arrivals {
            if out.len() >= s.finds {
                return Ok(out);
            }
            let d = match rec.delay {
                Delay::Uniform { max_days } => max_days * rng.uniform(),
                Delay::Exponential { mean_days } => -mean_days * (1.0 - rng.uniform()).ln(),
            };
            let t = a.t_days + d;
            if t >= rec.window_end_days {
                continue;
            }
            let place = match a.place.line {
                Some(l) => Place::on_line(l, a.place.s_km + rec.bandwidth_km * rng.normal(), a.place.lonlat),
                None => a.place,
            };
            let seg = loc.arrival(a.t_days, place.lonlat, place.line, place.s_km).segment;
            let Some(seg) = seg else { continue };
            if rng.uniform() * lmax >= level(seg, t) {
                continue;
            }
            let day = t.floor();
            out.push(Observation { id: format!("synthetic:find-{:02}", out.len() + 1), class: s.class, place, segment: seg, t_start_days: day, t_end_days: day + 1.0 });
        }
    }
    if out.len() < s.finds {
        return Err("debris-drift: synthetic source produced too few identifiable finds".into());
    }
    Ok(out)
}

fn diffusivity_prior(p: &Params) -> DiffusivityPrior {
    match p.diffusivity {
        DiffusivityParams::Fixed { k_m2_s } => DiffusivityPrior::Fixed { k_m2_s },
        DiffusivityParams::LogUniform { k_min_m2_s, k_max_m2_s } => DiffusivityPrior::LogUniform { k_min_m2_s, k_max_m2_s },
    }
}

pub(crate) fn build(p: &Params) -> Result<Built, String> {
    validate(p)?;
    let cells = match &p.extent_map_path {
        Some(path) => parse_cells(&std::fs::read_to_string(path).map_err(|e| format!("debris-drift: {path}: {e}"))?)?,
        None => parse_cells(REFERENCE_MAP)?,
    };
    let grid = SourceGrid::from_posterior(&cells, 0.25, p.coverage, p.spacing_nm, p.margin_nm, p.island_link_nm, p.include_island)?;
    let (rec, loc) = build_recovery(p)?;
    let domain = Domain { lon_min: p.domain[0], lon_max: p.domain[1], lat_min: p.domain[2], lat_max: p.domain[3] };
    let mut setup = OceanSetup::new(&p.transport, domain, p.dt_hours * 3600.0, p.threads, p.leeway_absorbs_stokes, p.explicit_residual, p.land_gap_is_beaching)?;
    setup.refloat_per_day = p.refloat_per_day;
    if let Some(oe) = &p.ocean_error {
        setup.ocean_error = ocean::OceanErrorModel::eddying(oe.sigma_m_s, oe.length_scale_km * 1000.0, oe.time_scale_days * 86_400.0, oe.modes);
    }
    let prior = diffusivity_prior(p);
    let envs: Vec<(u64, Diffusion)> = p.env_seeds.iter().map(|&s| (s, prior.draw(s))).collect();
    let observations = match p.mode.as_str() {
        "synthetic" => synthetic_observations(p, &setup, &rec, &loc, envs[0].1)?,
        "evidence" => evidence_observations(p, &rec, &loc)?,
        m => return Err(format!("debris-drift: unknown mode `{m}`")),
    };
    let nc = p.classes.len();
    let by_class: Vec<Vec<usize>> = (0..nc).map(|c| (0..observations.len()).filter(|&j| observations[j].class == c).collect()).collect();
    let responses: Vec<Vec<ObjectResponse>> = (0..nc).map(|c| if by_class[c].is_empty() { Vec::new() } else { class_responses(p, c) }).collect();
    let segnames: Vec<String> = match &loc.map { Some(m) => m.segments.iter().map(|s| s.name.clone()).collect(), None => (0..rec.n_segments).map(|s| format!("edge-{s}")).collect() };
    let levels = LevelDraws::from_block_means(&block_means(&p.levels.ln_mean_by_period, &p.levels.segment_ln_mean_by_period, &segnames)?, p.levels.sigma, p.levels.draws, p.levels.seed);
    let alt_levels: Vec<(String, LevelDraws)> = p
        .levels
        .alternatives
        .iter()
        .map(|a| Ok((a.name.clone(), LevelDraws::from_block_means(&block_means(&p.levels.ln_mean_by_period, &a.segment_ln_mean_by_period, &segnames)?, p.levels.sigma, p.levels.draws, p.levels.seed))))
        .collect::<Result<_, String>>()?;
    let t_end = p.release_unix_s + rec.window_end_days * 86_400.0;
    let n = p.particles_per_class;
    let half = n / 2;
    let shadows = if p.mode == "evidence" { shadow_observations(p, &rec, &loc)? } else { Vec::new() };
    let shadow_by_class: Vec<Vec<usize>> = (0..nc).map(|c| (0..shadows.len()).filter(|&j| shadows[j].class == c).collect()).collect();
    let shadow_fresh: Vec<Option<f64>> = if shadows.is_empty() { Vec::new() } else { p.shadow_finds.iter().map(|s| s.fresh_days).collect() };
    if !shadows.is_empty() && !p.write_coefficients {
        return Err("debris-drift: shadow_finds need write_coefficients = true".into());
    }
    for c in 0..nc {
        if !shadow_by_class[c].is_empty() && by_class[c].is_empty() {
            return Err(format!("debris-drift: shadow finds of class `{}` need at least one scored find of that class", p.classes[c].name));
        }
    }
    let mut coef_out: Option<std::io::BufWriter<std::fs::File>> = None;
    if p.write_coefficients {
        let dir = p.output_dir.as_ref().ok_or("debris-drift: write_coefficients needs output_dir")?;
        std::fs::create_dir_all(dir).map_err(|e| format!("debris-drift: {dir}: {e}"))?;
        coef_out = Some(std::io::BufWriter::new(std::fs::File::create(format!("{dir}/coefficients.jsonl")).map_err(|e| e.to_string())?));
        std::fs::write(format!("{dir}/coefficients-meta.json"), coefficients_meta(p, &rec, &segnames, &observations, &shadows, &envs)?).map_err(|e| e.to_string())?;
    }
    let mut arr_out: Option<std::io::BufWriter<std::fs::File>> = None;
    if p.write_arrivals {
        let dir = p.output_dir.as_ref().ok_or("debris-drift: write_arrivals needs output_dir")?;
        std::fs::create_dir_all(dir).map_err(|e| format!("debris-drift: {dir}: {e}"))?;
        arr_out = Some(std::io::BufWriter::new(std::fs::File::create(format!("{dir}/arrivals.bin")).map_err(|e| e.to_string())?));
        let cls: Vec<String> = (0..nc)
            .map(|c| {
                let r: Vec<String> = responses[c].iter().map(|o| format!("[{:e},{:e},{:e},{:e},{:e}]", o.a_stokes, o.c_wind, o.wind_angle_deg, o.leeway_angle_deg, o.leeway_speed_mps)).collect();
                format!("{{\"name\":\"{}\",\"responses\":[{}]}}", p.classes[c].name, r.join(","))
            })
            .collect();
        std::fs::write(format!("{dir}/responses.json"), format!("{{\"fields\":[\"a_stokes\",\"c_wind\",\"wind_angle_deg\",\"leeway_angle_deg\",\"leeway_speed_mps\"],\"release_unix_s\":{:e},\"window_end_days\":{:e},\"classes\":[{}]}}", p.release_unix_s, rec.window_end_days, cls.join(","))).map_err(|e| e.to_string())?;
    }

    let mut nodes = vec![Node::NotComputed; grid.nlat * grid.nlon];
    let mut rows: Vec<String> = Vec::new();
    let ns = rec.n_segments;
    let mut header = "node,lat_deg,lon_deg,component,state,ln_l,ln_l_half_a,ln_l_half_b,min_n_eff,model_error_fraction,left_domain_fraction".to_string();
    for h in &p.recovery.extra_bandwidths_km {
        header += &format!(",ln_l_h{h}");
    }
    for c in 0..nc {
        for s in 0..ns {
            header += &format!(",p_{}_{}", p.classes[c].name, s);
        }
        header += &format!(",p_{}_any_beach", p.classes[c].name);
    }
    for j in 0..observations.len() {
        header += &format!(",n_eff_{}", observations[j].id.replace(':', "_"));
    }
    // Sizing diagnostics (step 4): kernel hits per find at the primary bandwidth, and split halves
    // and per-find effective sizes at each extra bandwidth.
    for j in 0..observations.len() {
        header += &format!(",hits_{}", observations[j].id.replace(':', "_"));
    }
    header += ",zero_env_fraction";
    for h in &p.recovery.extra_bandwidths_km {
        header += &format!(",ln_l_h{h}_half_a,ln_l_h{h}_half_b");
        for j in 0..observations.len() {
            header += &format!(",n_eff_h{h}_{}", observations[j].id.replace(':', "_"));
        }
    }
    for (name, _) in &alt_levels {
        header += &format!(",ln_l_lev_{name},ln_l_lev_{name}_half_a,ln_l_lev_{name}_half_b");
    }
    let clock = std::time::Instant::now();
    let mut steps_total = 0.0;
    let (mut released, mut model_error, mut left_domain) = (0usize, 0.0f64, 0.0f64);
    let (mut split_total, mut children_total) = (0usize, 0usize);
    let candidates = select_candidates(&grid.active, &p.node_subset, p.node_stride, p.node_offset, p.node_subset_outside_extent);
    for (count, &k) in candidates.iter().enumerate() {
        let (la, lo) = grid.node(k);
        let mut coef_full: Vec<Vec<Option<recovery::Coefficients>>> = Vec::new();
        let (mut coef_a, mut coef_b) = (Vec::new(), Vec::new());
        let mut p_seg = vec![vec![0.0; ns + 1]; nc];
        let mut n_eff = vec![f64::NAN; observations.len()];
        let mut node_err = 0.0f64;
        let mut node_left = 0.0f64;
        let mut node_released = 0usize;
        let mut on_land = false;
        let nh = p.recovery.extra_bandwidths_km.len();
        let mut coef_h: Vec<Vec<Vec<Option<recovery::Coefficients>>>> = vec![Vec::new(); nh];
        let mut coef_ha: Vec<Vec<Vec<Option<recovery::Coefficients>>>> = vec![Vec::new(); nh];
        let mut coef_hb: Vec<Vec<Vec<Option<recovery::Coefficients>>>> = vec![Vec::new(); nh];
        let mut hits = vec![0usize; observations.len()];
        let mut n_eff_h = vec![vec![f64::NAN; observations.len()]; nh];
        // shadow coefficients: index 3*set + part (set 0 = primary bandwidth, 1.. = extra; part full, half a, half b) -> [env][class]
        let mut sh: Vec<Vec<Vec<Option<recovery::Coefficients>>>> = vec![Vec::new(); 3 * (1 + nh)];
        for &(seed, diffusion) in &envs {
            let mut she: Vec<Vec<Option<recovery::Coefficients>>> = vec![Vec::new(); 3 * (1 + nh)];
            let (mut full, mut ha, mut hb) = (Vec::new(), Vec::new(), Vec::new());
            let mut fh: Vec<Vec<Option<recovery::Coefficients>>> = vec![Vec::new(); nh];
            let mut fha: Vec<Vec<Option<recovery::Coefficients>>> = vec![Vec::new(); nh];
            let mut fhb: Vec<Vec<Option<recovery::Coefficients>>> = vec![Vec::new(); nh];
            for c in 0..nc {
                if responses[c].is_empty() {
                    full.push(None);
                    ha.push(None);
                    hb.push(None);
                    fh.iter_mut().for_each(|v| v.push(None));
                    fha.iter_mut().for_each(|v| v.push(None));
                    fhb.iter_mut().for_each(|v| v.push(None));
                    she.iter_mut().for_each(|v| v.push(None));
                    continue;
                }
                let split = p.splitting.as_ref().filter(|s| s.classes.is_empty() || s.classes.iter().any(|n| *n == p.classes[c].name));
                let (e, steps) = run_ensemble(&setup, &loc, [lo, la], p.release_unix_s, t_end, &responses[c], seed, diffusion, split)?;
                if let Some(w) = arr_out.as_mut() {
                    write_arrival_block(w, k, la, lo, seed, c, n, &e)?;
                }
                split_total += e.split;
                children_total += e.children;
                steps_total += steps;
                node_released += n;
                node_err += e.model_error;
                node_left += e.left_domain;
                if e.on_land == n {
                    on_land = true;
                }
                for (_, a) in &e.arrivals {
                    if a.t_days < rec.window_end_days {
                        p_seg[c][a.segment.unwrap_or(ns)] += a.w / (n * envs.len()) as f64;
                    }
                }
                let obs: Vec<&Observation> = by_class[c].iter().map(|&j| &observations[j]).collect();
                let all: Vec<Arrival> = e.arrivals.iter().map(|x| x.1).collect();
                let a_half: Vec<Arrival> = e.arrivals.iter().filter(|x| x.0 < half).map(|x| x.1).collect();
                let b_half: Vec<Arrival> = e.arrivals.iter().filter(|x| x.0 >= half).map(|x| x.1).collect();
                let kf = rec.coefficients(&obs, &all, n);
                for (jj, &j) in by_class[c].iter().enumerate() {
                    n_eff[j] = if n_eff[j].is_nan() { kf.n_eff[jj] } else { n_eff[j].min(kf.n_eff[jj]) };
                    hits[j] += kf.hits[jj];
                }
                for (hi, &h) in p.recovery.extra_bandwidths_km.iter().enumerate() {
                    let rh = Recovery { bandwidth_km: h, ..rec.clone() };
                    let kh = rh.coefficients(&obs, &all, n);
                    for (jj, &j) in by_class[c].iter().enumerate() {
                        let v = &mut n_eff_h[hi][j];
                        *v = if v.is_nan() { kh.n_eff[jj] } else { v.min(kh.n_eff[jj]) };
                    }
                    fh[hi].push(Some(kh));
                    fha[hi].push(Some(rh.coefficients(&obs, &a_half, half)));
                    fhb[hi].push(Some(rh.coefficients(&obs, &b_half, n - half)));
                }
                if shadow_by_class[c].is_empty() {
                    she.iter_mut().for_each(|v| v.push(None));
                } else {
                    let sobs: Vec<&Observation> = shadow_by_class[c].iter().map(|&j| &shadows[j]).collect();
                    let sfr: Vec<Option<f64>> = shadow_by_class[c].iter().map(|&j| shadow_fresh[j]).collect();
                    for (si, rr) in std::iter::once(rec.clone()).chain(p.recovery.extra_bandwidths_km.iter().map(|&h| Recovery { bandwidth_km: h, ..rec.clone() })).enumerate() {
                        she[3 * si].push(Some(shadow_coefficients(&rr, &sobs, &sfr, &all, n)));
                        she[3 * si + 1].push(Some(shadow_coefficients(&rr, &sobs, &sfr, &a_half, half)));
                        she[3 * si + 2].push(Some(shadow_coefficients(&rr, &sobs, &sfr, &b_half, n - half)));
                    }
                }
                full.push(Some(kf));
                ha.push(Some(rec.coefficients(&obs, &a_half, half)));
                hb.push(Some(rec.coefficients(&obs, &b_half, n - half)));
            }
            coef_full.push(full);
            for (hi, v) in fh.into_iter().enumerate() {
                coef_h[hi].push(v);
            }
            for (hi, v) in fha.into_iter().enumerate() {
                coef_ha[hi].push(v);
            }
            for (hi, v) in fhb.into_iter().enumerate() {
                coef_hb[hi].push(v);
            }
            coef_a.push(ha);
            coef_b.push(hb);
            for (k2, v) in she.into_iter().enumerate() {
                sh[k2].push(v);
            }
        }
        if let Some(w) = arr_out.as_mut() {
            std::io::Write::flush(w).map_err(|e| e.to_string())?;
        }
        if let Some(w) = coef_out.as_mut() {
            use std::io::Write;
            let mut line = format!("{{\"node\":{k},\"lat\":{la:e},\"lon\":{lo:e},\"land\":{on_land},\"bandwidths_km\":[{}",
                std::iter::once(rec.bandwidth_km).chain(p.recovery.extra_bandwidths_km.iter().copied()).map(|h| format!("{h:e}")).collect::<Vec<_>>().join(","));
            line += "],\"sets\":[";
            let mut sets: Vec<[&Vec<Vec<Option<recovery::Coefficients>>>; 3]> = vec![[&coef_full, &coef_a, &coef_b]];
            for hi in 0..nh {
                sets.push([&coef_h[hi], &coef_ha[hi], &coef_hb[hi]]);
            }
            line += &sets.iter().enumerate().map(|(si, s)| {
                let mut t = format!("{{\"full\":{},\"half_a\":{},\"half_b\":{}", coef_json(s[0], &by_class, &observations, rec.n_periods()), coef_json(s[1], &by_class, &observations, rec.n_periods()), coef_json(s[2], &by_class, &observations, rec.n_periods()));
                if !shadows.is_empty() {
                    t += &format!(",\"shadow_full\":{},\"shadow_half_a\":{},\"shadow_half_b\":{}", coef_json(&sh[3 * si], &shadow_by_class, &shadows, rec.n_periods()), coef_json(&sh[3 * si + 1], &shadow_by_class, &shadows, rec.n_periods()), coef_json(&sh[3 * si + 2], &shadow_by_class, &shadows, rec.n_periods()));
                }
                t + "}"
            }).collect::<Vec<_>>().join(",");
            line += "]}\n";
            w.write_all(line.as_bytes()).map_err(|e| e.to_string())?;
            w.flush().map_err(|e| e.to_string())?;
        }
        released += node_released;
        model_error += node_err;
        left_domain += node_left;
        let node = if on_land { Node::Land } else { node_ln_likelihood(&coef_full, &by_class, &levels) };
        let val = |x: Node| match x { Node::Value(v) => format!("{v:.6}"), _ => "nan".into() };
        let (na, nb) = if on_land { (Node::Land, Node::Land) } else { (node_ln_likelihood(&coef_a, &by_class, &levels), node_ln_likelihood(&coef_b, &by_class, &levels)) };
        let state = match node { Node::Value(_) => "value", Node::Land => "land", Node::Unresolved => "unresolved", Node::NotComputed => "not-computed" };
        let mut row = format!("{k},{la:.5},{lo:.5},{},{state},{},{},{},{:.3},{:.5},{:.5}", grid.component[k], val(node), val(na), val(nb), n_eff.iter().copied().fold(f64::INFINITY, f64::min), node_err / node_released.max(1) as f64, node_left / node_released.max(1) as f64);
        for ch in &coef_h {
            row += &format!(",{}", if on_land { "nan".into() } else { val(node_ln_likelihood(ch, &by_class, &levels)) });
        }
        for c in 0..nc {
            for s in 0..ns {
                row += &format!(",{:.6e}", p_seg[c][s]);
            }
            row += &format!(",{:.6e}", p_seg[c].iter().sum::<f64>());
        }
        for v in &n_eff {
            row += &format!(",{v:.3}");
        }
        for v in &hits {
            row += &format!(",{v}");
        }
        row += &format!(",{:.4}", if on_land { f64::NAN } else { node_ln_likelihood_zeros(&coef_full, &by_class, &levels).1 });
        for hi in 0..nh {
            for ch in [&coef_ha[hi], &coef_hb[hi]] {
                row += &format!(",{}", if on_land { "nan".into() } else { val(node_ln_likelihood(ch, &by_class, &levels)) });
            }
            for v in &n_eff_h[hi] {
                row += &format!(",{v:.3}");
            }
        }
        for (_, lv) in &alt_levels {
            for ch in [&coef_full, &coef_a, &coef_b] {
                row += &format!(",{}", if on_land { "nan".into() } else { val(node_ln_likelihood(ch, &by_class, lv)) });
            }
        }
        rows.push(row);
        nodes[k] = node;
        if p.output_dir.is_some() && (count + 1) % 50 == 0 {
            eprintln!("debris-drift: {} of {} nodes, {:.0} s", count + 1, candidates.len(), clock.elapsed().as_secs_f64());
        }
    }
    let wall = clock.elapsed().as_secs_f64();
    let surface = Surface { lat0: grid.lat0, lon0: grid.lon0, dlat: grid.dlat, dlon: grid.dlon, nlat: grid.nlat, nlon: grid.nlon, nodes };
    let count = |f: fn(&Node) -> bool| surface.nodes.iter().filter(|x| f(x)).count();
    let summary = vec![
        ("mode".into(), p.mode.clone()),
        ("ocean_model".into(), setup.ocean_model()),
        ("nodes_released".into(), candidates.len().to_string()),
        ("nodes_scored".into(), count(|x| matches!(x, Node::Value(_))).to_string()),
        ("nodes_unresolved".into(), count(|x| matches!(x, Node::Unresolved)).to_string()),
        ("nodes_land".into(), count(|x| matches!(x, Node::Land)).to_string()),
        ("trajectories".into(), released.to_string()),
        ("model_error_fraction".into(), format!("{:.6}", model_error / released.max(1) as f64)),
        ("left_domain_fraction".into(), format!("{:.6}", left_domain / released.max(1) as f64)),
        ("split_particles".into(), split_total.to_string()),
        ("split_children".into(), children_total.to_string()),
        ("splitting".into(), match &p.splitting { Some(s) => format!("factor {} at {} (snapshots {} h; classes {:?})", s.factor, s.targets.iter().map(|g| format!("{} {:.0} km x{}", g.name, g.radius_km, g.factor.unwrap_or(s.factor))).collect::<Vec<_>>().join(", "), s.snapshot_hours, s.classes), None => "off".into() }),
        ("bandwidth_km".into(), format!("{} (sensitivities {:?})", rec.bandwidth_km, p.recovery.extra_bandwidths_km)),
        ("particle_steps".into(), format!("{steps_total:.4e}")),
        ("wall_s".into(), format!("{wall:.1}")),
        ("particle_steps_per_s".into(), format!("{:.4e}", steps_total / wall.max(1e-9))),
        ("threads".into(), p.threads.to_string()),
        ("env_realisations".into(), envs.len().to_string()),
        ("diffusivity_m2_s".into(), envs.iter().map(|e| format!("{:.1}", e.1.long_time_diffusivity_m2_s())).collect::<Vec<_>>().join(";")),
        ("level_draws".into(), levels.draws.len().to_string()),
        ("level_overrides".into(), p.levels.segment_ln_mean_by_period.iter().map(|o| format!("{}:{:?}", o.segment, o.ln_mean_by_period)).collect::<Vec<_>>().join(";")),
        ("level_alternatives".into(), p.levels.alternatives.iter().map(|a| format!("{}[{}]", a.name, a.segment_ln_mean_by_period.iter().map(|o| format!("{}:{:?}", o.segment, o.ln_mean_by_period)).collect::<Vec<_>>().join(";"))).collect::<Vec<_>>().join(" ")),
        ("finds".into(), observations.iter().map(|o| format!("{}@seg{}:class{}:day{:.1}-{:.1}", o.id, o.segment, o.class, o.t_start_days, o.t_end_days)).collect::<Vec<_>>().join(";")),
        ("main_band_mass".into(), format!("{:.4}", grid.component_mass[grid.main_component])),
        ("coverage_reached".into(), format!("{:.4}", grid.covered_mass)),
        ("label".into(), run_label(p)),
    ];
    if let Some(dir) = &p.output_dir {
        std::fs::create_dir_all(dir).map_err(|e| format!("debris-drift: {dir}: {e}"))?;
        let mut csv = header + "\n";
        csv += &rows.join("\n");
        csv.push('\n');
        std::fs::write(format!("{dir}/nodes.csv"), csv).map_err(|e| e.to_string())?;
        let mut text: String = summary.iter().map(|(k, v)| format!("{k} = {v:?}\n")).collect();
        text += &format!("segments = {segnames:?}\nclasses = {:?}\ngrid = {{ lat0 = {}, lon0 = {}, dlat = {}, dlon = {}, nlat = {}, nlon = {} }}\n", p.classes.iter().map(|c| c.name.clone()).collect::<Vec<_>>(), grid.lat0, grid.lon0, grid.dlat, grid.dlon, grid.nlat, grid.nlon);
        std::fs::write(format!("{dir}/summary.toml"), text).map_err(|e| e.to_string())?;
    }
    Ok(Built { grid, surface, observations, ocean_model: setup.ocean_model(), summary })
}

/// JSON for one coefficient set `coef[env][class]`: per environment, per class, either null or
/// {"a": [[own-segment values by period] per find of the class], "A": [recovery mass per block]}.
/// `a[j]` is non-zero only in find j's own segment (see `Recovery::coefficients`), so only that slice is written.
fn coef_json(coef: &[Vec<Option<recovery::Coefficients>>], by_class: &[Vec<usize>], obs: &[Observation], np: usize) -> String {
    let f = |v: &[f64]| v.iter().map(|x| format!("{x:e}")).collect::<Vec<_>>().join(",");
    let envs: Vec<String> = coef
        .iter()
        .map(|env| {
            let cls: Vec<String> = env
                .iter()
                .enumerate()
                .map(|(c, k)| match k {
                    None => "null".to_string(),
                    Some(k) => {
                        let a: Vec<String> = by_class[c]
                            .iter()
                            .enumerate()
                            .map(|(jj, &j)| {
                                let s = obs[j].segment;
                                debug_assert!(k.a[jj].iter().enumerate().all(|(b, &v)| b / np == s || v == 0.0));
                                format!("[{}]", f(&k.a[jj][s * np..(s + 1) * np]))
                            })
                            .collect();
                        format!("{{\"a\":[{}],\"A\":[{}]}}", a.join(","), f(&k.big_a))
                    }
                })
                .collect();
            format!("[{}]", cls.join(","))
        })
        .collect();
    format!("[{}]", envs.join(","))
}

/// Metadata for `coefficients.jsonl`: block layout, finds, environments, level priors and the standard
/// normal level draws z (draws x blocks), so that nu = exp(mu + sigma z) reproduces the module's draws exactly.
fn coefficients_meta(p: &Params, rec: &Recovery, segnames: &[String], obs: &[Observation], shadows: &[Observation], envs: &[(u64, Diffusion)]) -> Result<String, String> {
    let q = |s: &str| format!("\"{}\"", s.replace('\\', "\\\\").replace('"', "\\\""));
    let f = |v: &[f64]| v.iter().map(|x| format!("{x:e}")).collect::<Vec<_>>().join(",");
    let nb = rec.n_blocks();
    let z = LevelDraws::from_block_means(&vec![0.0; nb], 1.0, p.levels.draws, p.levels.seed);
    let zrows: Vec<String> = z.draws.iter().map(|d| format!("[{}]", f(&d.iter().map(|x| x.ln()).collect::<Vec<_>>()))).collect();
    let mu = block_means(&p.levels.ln_mean_by_period, &p.levels.segment_ln_mean_by_period, segnames)?;
    let mut alts = Vec::new();
    for a in &p.levels.alternatives {
        alts.push(format!("{{\"name\":{},\"mu\":[{}]}}", q(&a.name), f(&block_means(&p.levels.ln_mean_by_period, &a.segment_ln_mean_by_period, segnames)?)));
    }
    Ok(format!(
        "{{\"shadow_finds\":[{}],\"segments\":[{}],\"n_periods\":{},\"period_breaks_days\":[{}],\"window_end_days\":{:e},\"classes\":[{}],\"finds\":[{}],\"envs\":[{}],\"particles_per_class\":{},\"levels\":{{\"ln_mean_by_period\":[{}],\"sigma\":{:e},\"draws\":{},\"seed\":{},\"mu_primary\":[{}],\"alternatives\":[{}],\"z\":[{}]}}}}\n",
        shadows.iter().enumerate().map(|(k, o)| format!("{{\"id\":{},\"class\":{},\"segment\":{},\"t_start_days\":{:e},\"t_end_days\":{:e},\"fresh_days\":{}}}", q(&o.id), o.class, o.segment, o.t_start_days, o.t_end_days, p.shadow_finds[k].fresh_days.map_or("null".to_string(), |f| format!("{f:e}")))).collect::<Vec<_>>().join(","),
        segnames.iter().map(|s| q(s)).collect::<Vec<_>>().join(","),
        rec.n_periods(),
        f(&rec.breaks_days),
        rec.window_end_days,
        p.classes.iter().map(|c| q(&c.name)).collect::<Vec<_>>().join(","),
        obs.iter().map(|o| format!("{{\"id\":{},\"class\":{},\"segment\":{},\"t_start_days\":{:e},\"t_end_days\":{:e}}}", q(&o.id), o.class, o.segment, o.t_start_days, o.t_end_days)).collect::<Vec<_>>().join(","),
        envs.iter().map(|e| format!("{{\"seed\":{},\"diffusivity_m2_s\":{:e}}}", e.0, e.1.long_time_diffusivity_m2_s())).collect::<Vec<_>>().join(","),
        p.particles_per_class,
        f(&p.levels.ln_mean_by_period),
        p.levels.sigma,
        p.levels.draws,
        p.levels.seed,
        f(&mu),
        alts.join(","),
        zrows.join(",")
    ))
}

/// Nodes a run releases: every `stride`-th active node from `offset`, or the named subset (active nodes
/// only, unless `outside_extent`, which admits any in-grid node, for coverage extensions).
fn select_candidates(active: &[bool], subset: &[usize], stride: usize, offset: usize, outside_extent: bool) -> Vec<usize> {
    if subset.is_empty() {
        (0..active.len()).filter(|&k| active[k]).skip(offset).step_by(stride.max(1)).collect()
    } else {
        subset.iter().copied().filter(|&k| k < active.len() && (outside_extent || active[k])).collect()
    }
}

/// Run label for `summary.toml`, derived from the configuration (the coastline and the extent map
/// actually used), so a summary can never describe a different set-up from the one that ran.
fn run_label(p: &Params) -> String {
    let coast = match &p.transport {
        TransportParams::Grid { gshhg_path: Some(_), gshhg_snap_km, .. } => format!("GSHHG coastline (snap {gshhg_snap_km} km)"),
        TransportParams::Grid { island_discs, .. } if !island_discs.is_empty() => "PROVISIONAL island-disc stub plus product land-mask stranding".to_string(),
        TransportParams::Grid { .. } => "PROVISIONAL product land-mask stranding only".to_string(),
        _ => "synthetic transport".to_string(),
    };
    let gap = if p.land_gap_is_beaching { "land gap counted as beaching" } else { "land gap is model error" };
    let extent = p.extent_map_path.as_deref().unwrap_or("synthetic extent (no map)");
    let wind = match p.c_wind_product_offset_range {
        Some([lo, hi]) => format!("; c_wind product offset U({lo:+.4}, {hi:+.4}) per particle"),
        None if p.c_wind_product_offset != 0.0 => format!("; c_wind product offset {:+.4}", p.c_wind_product_offset),
        None => String::new(),
    };
    format!("beaching: {coast}; {gap}; extent map: {extent}{wind}")
}

fn validate(p: &Params) -> Result<(), String> {
    if let Some([lo, hi]) = p.c_wind_product_offset_range {
        if p.c_wind_product_offset != 0.0 {
            return Err("debris-drift: set c_wind_product_offset or c_wind_product_offset_range, not both".into());
        }
        if !(lo.is_finite() && hi.is_finite() && lo <= hi && lo > -0.05 && hi < 0.05) {
            return Err(format!("debris-drift: c_wind_product_offset_range [{lo}, {hi}] must be finite, ordered and within +/-5% of U10"));
        }
    }
    if p.classes.is_empty() || p.env_seeds.is_empty() {
        return Err("debris-drift: need at least one object class and one environment realisation".into());
    }
    for n in &p.restrict_to_classes {
        if !p.classes.iter().any(|c| &c.name == n) {
            return Err(format!("debris-drift: restrict_to_classes names unknown class `{n}`"));
        }
    }
    for c in &p.classes {
        for d in [&c.a_stokes, &c.c_wind, &c.wind_angle_deg, &c.leeway_angle_deg, &c.leeway_speed_mps] {
            d.validate()?;
        }
    }
    if !p.release_unix_s.is_finite() || p.dt_hours <= 0.0 || p.particles_per_class < 2 {
        return Err("debris-drift: release time and dt must be positive, and at least 2 particles per class".into());
    }
    if p.levels.sigma < 0.0 || p.levels.draws == 0 {
        return Err("debris-drift: levels need sigma >= 0 and at least one draw".into());
    }
    if p.mode == "evidence" && matches!(p.transport, TransportParams::Analytic { .. }) {
        return Err("debris-drift: evidence mode may not run on analytic fields".into());
    }
    Ok(())
}

/// The stringent identity set with discovery intervals in days after `release_unix_s`
/// (a single reported day d is the interval [d, d + 1)).
#[cfg_attr(not(test), allow(dead_code))]
pub(crate) fn stringent_intervals(release_unix_s: f64) -> Result<Vec<(String, f64, f64, String)>, String> {
    let mut out = Vec::new();
    for r in evidence::parse(evidence::TABLE)?.into_iter().filter(|r| r.stringent) {
        let a = day_of(release_unix_s, &r.discovery_start)?;
        let b = day_of(release_unix_s, &r.discovery_end)? + 1.0;
        out.push((format!("debris:{}", r.object_id), a, b, r.motion_class));
    }
    Ok(out)
}

struct DebrisDrift {
    /// One (option label, surface) per `ocean-model` option, in declaration order.
    models: Vec<(String, Surface)>,
    observations: Vec<String>,
}

/// Composer-facing mode (composer pass 0 gap, 10 Oct): load merged production node tables instead of re-running the
/// transport. `[[hypotheses.debris-drift.surfaces]]` entries give `ocean_model` (the shared option label),
/// `nodes_csv` and `summary_toml` (from merge_chunks.py); `column` picks the bandwidth (default `ln_l`, 50 km).
#[derive(serde::Deserialize, Clone, Debug)]
#[serde(deny_unknown_fields)]
struct SurfaceFile {
    ocean_model: String,
    nodes_csv: String,
    summary_toml: String,
}

#[derive(serde::Deserialize, Clone, Debug)]
#[serde(deny_unknown_fields)]
struct SurfacesParams {
    surfaces: Vec<SurfaceFile>,
    #[serde(default = "d_column")]
    column: String,
}

fn d_column() -> String {
    "ln_l".into()
}

/// Read a merged node table into a `Surface`: `state` land -> Land; a finite value in `column` -> Value; otherwise
/// Unresolved; nodes absent from the table -> NotComputed (outside support, never zero).
fn load_surface(f: &SurfaceFile, column: &str) -> Result<Surface, String> {
    let sum: toml::Value = toml::from_str(&std::fs::read_to_string(&f.summary_toml).map_err(|e| format!("debris-drift: {}: {e}", f.summary_toml))?)
        .map_err(|e| format!("debris-drift: {}: {e}", f.summary_toml))?;
    let g = sum.get("grid").ok_or("debris-drift: summary has no grid")?;
    let num = |k: &str| g.get(k).and_then(|v| v.as_float().or_else(|| v.as_integer().map(|i| i as f64))).ok_or(format!("debris-drift: grid.{k} missing"));
    let (nlat, nlon) = (num("nlat")? as usize, num("nlon")? as usize);
    let mut nodes = vec![Node::NotComputed; nlat * nlon];
    let text = std::fs::read_to_string(&f.nodes_csv).map_err(|e| format!("debris-drift: {}: {e}", f.nodes_csv))?;
    let mut lines = text.lines();
    let head: Vec<&str> = lines.next().ok_or("debris-drift: empty nodes table")?.split(',').collect();
    let col = |name: &str| head.iter().position(|h| *h == name).ok_or(format!("debris-drift: column {name} not in {}", f.nodes_csv));
    let (ik, is, iv) = (col("node")?, col("state")?, col(column)?);
    for line in lines.filter(|l| !l.is_empty()) {
        let v: Vec<&str> = line.split(',').collect();
        let k: usize = v[ik].parse().map_err(|e| format!("debris-drift: node index: {e}"))?;
        if k >= nodes.len() {
            return Err(format!("debris-drift: node {k} outside the {nlat} x {nlon} grid"));
        }
        let x: f64 = v[iv].parse().unwrap_or(f64::NAN);
        nodes[k] = if v[is] == "land" { Node::Land } else if x.is_finite() { Node::Value(x) } else { Node::Unresolved };
    }
    Ok(Surface { lat0: num("lat0")?, lon0: num("lon0")?, dlat: num("dlat")?, dlon: num("dlon")?, nlat, nlon, nodes })
}

/// The stringent debris observation IDs (the evidence-mode set), without building the transport.
fn stringent_ids() -> Result<Vec<String>, String> {
    Ok(evidence::parse(evidence::TABLE)?.iter().filter(|r| r.stringent).map(|r| format!("debris:{}", r.object_id)).collect())
}

pub fn new(params: &toml::Value) -> Result<Box<dyn Hypothesis>, String> {
    if params.get("surfaces").is_some() {
        let sp: SurfacesParams = params.clone().try_into().map_err(|e| format!("debris-drift (surfaces): {e}"))?;
        if sp.surfaces.is_empty() {
            return Err("debris-drift: surfaces mode needs at least one surface".into());
        }
        let mut models = Vec::new();
        for f in &sp.surfaces {
            models.push((f.ocean_model.replace([':', '/', ','], "-"), load_surface(f, &sp.column)?));
        }
        eprintln!("debris-drift (SURFACES, PROVISIONAL): {} ocean-model options, column {}", models.len(), sp.column);
        return Ok(Box::new(DebrisDrift { models, observations: stringent_ids()? }));
    }
    let p: Params = params.clone().try_into().map_err(|e| format!("debris-drift: {e}"))?;
    let b = build(&p)?;
    eprintln!("debris-drift ({}): {}", if p.mode == "evidence" { "EVIDENCE, PROVISIONAL" } else { "SYNTHETIC finds, not evidence" }, b.summary.iter().take(12).map(|(k, v)| format!("{k}={v}")).collect::<Vec<_>>().join(", "));
    let _ = &b.grid;
    // Option labels become column names: no `,` `/` `:` or line breaks (crates/hypothesis).
    let model = b.ocean_model.replace([':', '/', ','], "-");
    Ok(Box::new(DebrisDrift { models: vec![(model, b.surface)], observations: b.observations.iter().map(|o| o.id.clone()).collect() }))
}

impl Hypothesis for DebrisDrift {
    fn observations(&self) -> Vec<String> {
        self.observations.clone()
    }

    fn alternatives(&self) -> Vec<Alternatives> {
        // Equal prior weight across the declared ocean-model options (ruling of 9 Oct; sensitivity mixture, rule 7).
        let w = 1.0 / self.models.len() as f64;
        let opts: Vec<(&str, f64)> = self.models.iter().map(|(m, _)| (m.as_str(), w)).collect();
        vec![Alternatives::new(ocean::OCEAN_MODEL_ALTERNATIVE, &opts)]
    }

    /// q/Q is a normalised density of the finds under every ocean model, so options may be
    /// mixed - as a sensitivity mixture (rule 7).
    fn absolute_scale(&self) -> bool {
        true
    }

    fn prediction_columns(&self) -> Vec<String> {
        // One support flag per ocean-model option (1 scored, 0 outside support, 2 Monte Carlo unresolved). With a single
        // option the column name is unchanged from earlier runs.
        if self.models.len() == 1 {
            return vec!["drift_support_flag (1 scored 0 outside support 2 MC-unresolved)".into()];
        }
        self.models.iter().map(|(m, _)| format!("drift_support_flag {m} (1 scored 0 outside support 2 MC-unresolved)")).collect()
    }

    fn impact_log_likelihood(&self, impact: &ImpactView, choice: &[usize]) -> f64 {
        let m = choice.first().copied().unwrap_or(0).min(self.models.len() - 1);
        match self.models[m].1.ln_likelihood(impact.latitude_deg, impact.longitude_deg) {
            Lookup::Value(l) => l,
            Lookup::Unresolved | Lookup::OutsideSupport => f64::NAN,
        }
    }

    fn predict(&self, impact: &ImpactView, out: &mut [f64]) {
        for (o, (_, surface)) in out.iter_mut().zip(&self.models) {
            *o = match surface.ln_likelihood(impact.latitude_deg, impact.longitude_deg) {
                Lookup::Value(_) => 1.0,
                Lookup::OutsideSupport => 0.0,
                Lookup::Unresolved => 2.0,
            };
        }
    }
}

#[cfg(test)]
mod tests;

// ---- Offline rescoring from the arrivals dump (write_arrivals) ------------------------------------------
// Re-runs the recovery layer on stored beachings with a new segment map, find list, window, periods, delay,
// freshness marks and bandwidths. It calls the same Recovery::coefficients and shadow_coefficients as a
// module run, so with the run's own settings it reproduces coefficients.jsonl (up to the f32 storage of
// particle weights). Entry: DRIFT_RESCORE=<config.toml> $BIN rescore_entry --ignored --nocapture.

#[derive(Deserialize, Clone, Debug)]
#[serde(deny_unknown_fields)]
struct RescoreFind {
    id: String,
    class: usize,
    lon: f64,
    lat: f64,
    t_start_days: f64,
    t_end_days: f64,
    #[serde(default)]
    fresh_days: Option<f64>,
}

#[derive(Deserialize, Clone, Debug)]
#[serde(deny_unknown_fields)]
struct RescoreConfig {
    arrivals: Vec<String>,
    output: String,
    n_classes: usize,
    /// Particles per class of the run (the halves split at n/2, as the module does).
    particles_per_class: usize,
    window_end_days: f64,
    period_breaks_days: Vec<f64>,
    delay_days: f64,
    /// First entry is the primary bandwidth (set 0), as in a module run.
    bandwidths_km: Vec<f64>,
    segments: Vec<Segment>,
    finds: Vec<RescoreFind>,
}

struct ArrBlock {
    node: u32,
    lat: f64,
    lon: f64,
    env_seed: u64,
    class: usize,
    released: usize,
    arrivals: Vec<(usize, Arrival)>,
}

fn read_arrival_blocks(path: &str, map: &SegmentMap, out: &mut Vec<ArrBlock>) -> Result<(), String> {
    let b = std::fs::read(path).map_err(|e| format!("rescore: {path}: {e}"))?;
    let u32_at = |o: usize| u32::from_le_bytes(b[o..o + 4].try_into().unwrap());
    let i32_at = |o: usize| i32::from_le_bytes(b[o..o + 4].try_into().unwrap());
    let u64_at = |o: usize| u64::from_le_bytes(b[o..o + 8].try_into().unwrap());
    let f64_at = |o: usize| f64::from_le_bytes(b[o..o + 8].try_into().unwrap());
    let f32_at = |o: usize| f32::from_le_bytes(b[o..o + 4].try_into().unwrap()) as f64;
    let mut o = 0usize;
    while o < b.len() {
        if o + 60 > b.len() || &b[o..o + 4] != b"ARV1" {
            return Err(format!("rescore: {path}: bad block header at byte {o}"));
        }
        let (node, lat, lon, env_seed) = (u32_at(o + 4), f64_at(o + 8), f64_at(o + 16), u64_at(o + 24));
        let (class, released, n) = (u32_at(o + 32) as usize, u32_at(o + 36) as usize, u32_at(o + 40) as usize);
        o += 60;
        if o + 52 * n > b.len() {
            return Err(format!("rescore: {path}: truncated block for node {node}"));
        }
        let mut arrivals = Vec::with_capacity(n);
        for r in 0..n {
            let q = o + 52 * r;
            let (lo, la, line, s) = (f64_at(q + 20), f64_at(q + 28), i32_at(q + 36), f64_at(q + 40));
            let place = if line >= 0 && s.is_finite() { Place::on_line(line as u32, s, [lo, la]) } else { Place::at([lo, la]) };
            arrivals.push((u32_at(q) as usize, Arrival { place, segment: map.locate([lo, la]), t_days: f64_at(q + 8), t_leave_days: f32_at(q + 16), w: f32_at(q + 4) }));
        }
        o += 52 * n;
        out.push(ArrBlock { node, lat, lon, env_seed, class, released, arrivals });
    }
    Ok(())
}

pub fn rescore(config_path: &str) -> Result<(), String> {
    let cfg: RescoreConfig = toml::from_str(&std::fs::read_to_string(config_path).map_err(|e| format!("rescore: {config_path}: {e}"))?).map_err(|e| format!("rescore: {config_path}: {e}"))?;
    let map = SegmentMap::new(cfg.segments.clone())?;
    let ns = map.len();
    let mut obs = Vec::new();
    for f in &cfg.finds {
        let segment = map.locate([f.lon, f.lat]).ok_or(format!("rescore: find `{}` lies in no segment", f.id))?;
        if f.class >= cfg.n_classes || !(f.t_end_days > f.t_start_days) || f.t_end_days > cfg.window_end_days {
            return Err(format!("rescore: find `{}`: bad class or dates", f.id));
        }
        if f.fresh_days.is_some_and(|x| !(x > 0.0)) {
            return Err(format!("rescore: find `{}`: fresh_days must be positive", f.id));
        }
        obs.push(Observation { id: f.id.clone(), class: f.class, place: Place::at([f.lon, f.lat]), segment, t_start_days: f.t_start_days, t_end_days: f.t_end_days });
    }
    let by_class: Vec<Vec<usize>> = (0..cfg.n_classes).map(|c| (0..obs.len()).filter(|&j| obs[j].class == c).collect()).collect();
    let fresh: Vec<Option<f64>> = cfg.finds.iter().map(|f| f.fresh_days).collect();
    let base = Recovery { n_segments: ns, breaks_days: cfg.period_breaks_days.clone(), edges: Vec::new(), delay: Delay::Exponential { mean_days: cfg.delay_days }, bandwidth_km: cfg.bandwidths_km[0], window_end_days: cfg.window_end_days };
    let recs: Vec<Recovery> = cfg.bandwidths_km.iter().map(|&h| Recovery { bandwidth_km: h, ..base.clone() }).collect();
    let np = base.n_periods();
    let n = cfg.particles_per_class;
    let half = n / 2;
    let mut w = std::io::BufWriter::new(std::fs::File::create(&cfg.output).map_err(|e| format!("rescore: {}: {e}", cfg.output))?);
    for path in &cfg.arrivals {
        let mut blocks = Vec::new();
        read_arrival_blocks(path, &map, &mut blocks)?;
        let mut nodes: Vec<u32> = Vec::new();
        for b in &blocks {
            if !nodes.contains(&b.node) {
                nodes.push(b.node);
            }
        }
        for &k in &nodes {
            let nb: Vec<&ArrBlock> = blocks.iter().filter(|b| b.node == k).collect();
            let mut seeds: Vec<u64> = Vec::new();
            for b in &nb {
                if !seeds.contains(&b.env_seed) {
                    seeds.push(b.env_seed);
                }
            }
            // sets[bandwidth][part] -> [env][class]
            let mut sets: Vec<[Vec<Vec<Option<recovery::Coefficients>>>; 3]> = (0..recs.len()).map(|_| [Vec::new(), Vec::new(), Vec::new()]).collect();
            for &s in &seeds {
                let mut per: Vec<[Vec<Option<recovery::Coefficients>>; 3]> = (0..recs.len()).map(|_| [Vec::new(), Vec::new(), Vec::new()]).collect();
                for c in 0..cfg.n_classes {
                    let blk = nb.iter().find(|b| b.env_seed == s && b.class == c);
                    for (ri, rr) in recs.iter().enumerate() {
                        match blk {
                            None => per[ri].iter_mut().for_each(|v| v.push(None)),
                            Some(b) => {
                                if b.released != n {
                                    return Err(format!("rescore: node {k}: released {} but particles_per_class {n}", b.released));
                                }
                                let all: Vec<Arrival> = b.arrivals.iter().map(|x| x.1).collect();
                                let ha: Vec<Arrival> = b.arrivals.iter().filter(|x| x.0 < half).map(|x| x.1).collect();
                                let hb: Vec<Arrival> = b.arrivals.iter().filter(|x| x.0 >= half).map(|x| x.1).collect();
                                let so: Vec<&Observation> = by_class[c].iter().map(|&j| &obs[j]).collect();
                                let sf: Vec<Option<f64>> = by_class[c].iter().map(|&j| fresh[j]).collect();
                                per[ri][0].push(Some(shadow_coefficients(rr, &so, &sf, &all, n)));
                                per[ri][1].push(Some(shadow_coefficients(rr, &so, &sf, &ha, half)));
                                per[ri][2].push(Some(shadow_coefficients(rr, &so, &sf, &hb, n - half)));
                            }
                        }
                    }
                }
                for (ri, p3) in per.into_iter().enumerate() {
                    for (pi, v) in p3.into_iter().enumerate() {
                        sets[ri][pi].push(v);
                    }
                }
            }
            let (la, lo) = (nb[0].lat, nb[0].lon);
            let body: Vec<String> = sets
                .iter()
                .map(|s| format!("{{\"full\":{},\"half_a\":{},\"half_b\":{}}}", coef_json(&s[0], &by_class, &obs, np), coef_json(&s[1], &by_class, &obs, np), coef_json(&s[2], &by_class, &obs, np)))
                .collect();
            std::io::Write::write_all(&mut w, format!("{{\"node\":{k},\"lat\":{la:e},\"lon\":{lo:e},\"env_seeds\":[{}],\"sets\":[{}]}}\n", seeds.iter().map(|x| x.to_string()).collect::<Vec<_>>().join(","), body.join(",")).as_bytes()).map_err(|e| e.to_string())?;
        }
        eprintln!("rescore: {path}: {} nodes", nodes.len());
    }
    std::io::Write::flush(&mut w).map_err(|e| e.to_string())?;
    Ok(())
}

#[cfg(test)]
mod rescore_entry {
    #[test]
    #[ignore]
    fn rescore() {
        super::rescore(&std::env::var("DRIFT_RESCORE").expect("DRIFT_RESCORE=<config.toml>")).unwrap();
    }
}
