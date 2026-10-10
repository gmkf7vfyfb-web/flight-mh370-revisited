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
use transport::{Fate, OceanSetup, TransportParams};

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
    /// Restrict release to these node indices (smoke tests); empty means every active node.
    #[serde(default)]
    node_subset: Vec<usize>,
    /// Let `node_subset` name grid nodes outside the extent map (component -1): coverage extensions on the
    /// SAME grid, so their values merge cell-for-cell with the main run. Off by default (byte-identical).
    #[serde(default)]
    node_subset_outside_extent: bool,
    /// Release every n-th active node only (checks; production uses 1).
    #[serde(default = "d_stride")]
    node_stride: usize,
    /// First active node taken when striding (chunked runs: offsets 0..stride cover every node).
    #[serde(default)]
    node_offset: usize,
    /// Write the node table and summary here (pilot and diagnostics).
    #[serde(default)]
    output_dir: Option<String>,
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

fn draw_response(c: &ClassParams, rng: &mut Rng) -> ObjectResponse {
    {
    let (a, w) = (c.a_stokes.draw(rng), c.c_wind.draw(rng));
    let (la, ls) = (c.leeway_angle_deg.draw(rng), c.leeway_speed_mps.draw(rng));
    transport::response(a, w, c.wind_angle_deg.draw(rng), la, ls)
    }
}

/// The common response draws of class `c` (shared by every node: common random numbers).
fn class_responses(p: &Params, c: usize) -> Vec<ObjectResponse> {
    let mut rng = Rng::derive(&[p.seed, 0xC1A5, c as u64]);
    (0..p.particles_per_class).map(|_| draw_response(&p.classes[c], &mut rng)).collect()
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
        Arrival { place, segment, t_days, w: 1.0 }
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
    let tally = |e: &mut Ensemble, i: usize, f: Fate, w: f64| match f {
        Fate::Beached { t, at, line, chainage_km } => {
            let mut a = loc.arrival((t - t0) / 86_400.0, at, line, chainage_km);
            a.w = w;
            e.arrivals.push((i, a));
        }
        Fate::Afloat => {}
        Fate::LeftDomain => e.left_domain += w,
        Fate::ReleasedOnLand => e.on_land += 1,
        Fate::ModelError => e.model_error += w,
    };
    let Some(sp) = split.filter(|s| !s.targets.is_empty() && s.targets.iter().any(|g| g.factor.unwrap_or(s.factor) > 1)) else {
        let (fates, steps) = setup.run(&particles, seed, diffusion, t_end)?;
        for (i, f) in fates.into_iter().enumerate() {
            tally(&mut e, i, f, 1.0);
        }
        return Ok((e, steps));
    };
    let dt = sp.snapshot_hours * 3600.0;
    let mut times: Vec<f64> = (1..).map(|k| t0 + k as f64 * dt).take_while(|&t| t < t_end).collect();
    times.push(t_end);
    let (fates, pos, mut steps) = setup.run_tracks(&particles, seed, diffusion, &times)?;
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
            _ => tally(&mut e, i, f, 1.0),
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
        let (kf, ks) = setup.run(&batch, seed, diffusion, t_end)?;
        steps += ks;
        e.children = kids.len();
        for (k, f) in kf.into_iter().enumerate().skip(n) {
            tally(&mut e, parent[k - n], f, weight[k - n]);
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
        let responses: Vec<ObjectResponse> = (0..1000).map(|_| draw_response(class, &mut rng)).collect();
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
    let levels = LevelDraws::new(rec.n_segments, &p.levels.ln_mean_by_period, p.levels.sigma, p.levels.draws, p.levels.seed);
    let t_end = p.release_unix_s + rec.window_end_days * 86_400.0;
    let n = p.particles_per_class;
    let half = n / 2;

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
        for &(seed, diffusion) in &envs {
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
                    continue;
                }
                let split = p.splitting.as_ref().filter(|s| s.classes.is_empty() || s.classes.iter().any(|n| *n == p.classes[c].name));
                let (e, steps) = run_ensemble(&setup, &loc, [lo, la], p.release_unix_s, t_end, &responses[c], seed, diffusion, split)?;
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
        ("splitting".into(), match &p.splitting { Some(s) => format!("factor {} at {} (snapshots {} h; classes {:?})", s.factor, s.targets.iter().map(|g| format!("{} {:.0} km", g.name, g.radius_km)).collect::<Vec<_>>().join(", "), s.snapshot_hours, s.classes), None => "off".into() }),
        ("bandwidth_km".into(), format!("{} (sensitivities {:?})", rec.bandwidth_km, p.recovery.extra_bandwidths_km)),
        ("particle_steps".into(), format!("{steps_total:.4e}")),
        ("wall_s".into(), format!("{wall:.1}")),
        ("particle_steps_per_s".into(), format!("{:.4e}", steps_total / wall.max(1e-9))),
        ("threads".into(), p.threads.to_string()),
        ("env_realisations".into(), envs.len().to_string()),
        ("diffusivity_m2_s".into(), envs.iter().map(|e| format!("{:.1}", e.1.long_time_diffusivity_m2_s())).collect::<Vec<_>>().join(";")),
        ("level_draws".into(), levels.draws.len().to_string()),
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
        let segnames: Vec<String> = match &loc.map { Some(m) => m.segments.iter().map(|s| s.name.clone()).collect(), None => (0..ns).map(|s| format!("edge-{s}")).collect() };
        let mut text: String = summary.iter().map(|(k, v)| format!("{k} = {v:?}\n")).collect();
        text += &format!("segments = {segnames:?}\nclasses = {:?}\ngrid = {{ lat0 = {}, lon0 = {}, dlat = {}, dlon = {}, nlat = {}, nlon = {} }}\n", p.classes.iter().map(|c| c.name.clone()).collect::<Vec<_>>(), grid.lat0, grid.lon0, grid.dlat, grid.dlon, grid.nlat, grid.nlon);
        std::fs::write(format!("{dir}/summary.toml"), text).map_err(|e| e.to_string())?;
    }
    Ok(Built { grid, surface, observations, ocean_model: setup.ocean_model(), summary })
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
    format!("beaching: {coast}; {gap}; extent map: {extent}")
}

fn validate(p: &Params) -> Result<(), String> {
    if p.classes.is_empty() || p.env_seeds.is_empty() {
        return Err("debris-drift: need at least one object class and one environment realisation".into());
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
    model: String,
    surface: Surface,
    observations: Vec<String>,
}

pub fn new(params: &toml::Value) -> Result<Box<dyn Hypothesis>, String> {
    let p: Params = params.clone().try_into().map_err(|e| format!("debris-drift: {e}"))?;
    let b = build(&p)?;
    eprintln!("debris-drift ({}): {}", if p.mode == "evidence" { "EVIDENCE, PROVISIONAL" } else { "SYNTHETIC finds, not evidence" }, b.summary.iter().take(12).map(|(k, v)| format!("{k}={v}")).collect::<Vec<_>>().join(", "));
    let _ = &b.grid;
    // Option labels become column names: no `,` `/` `:` or line breaks (crates/hypothesis).
    let model = b.ocean_model.replace([':', '/', ','], "-");
    Ok(Box::new(DebrisDrift { model, observations: b.observations.iter().map(|o| o.id.clone()).collect(), surface: b.surface }))
}

impl Hypothesis for DebrisDrift {
    fn observations(&self) -> Vec<String> {
        self.observations.clone()
    }

    fn alternatives(&self) -> Vec<Alternatives> {
        vec![Alternatives::new(ocean::OCEAN_MODEL_ALTERNATIVE, &[(self.model.as_str(), 1.0)])]
    }

    /// q/Q is a normalised density of the finds under every ocean model, so options may be
    /// mixed - as a sensitivity mixture (rule 7).
    fn absolute_scale(&self) -> bool {
        true
    }

    fn prediction_columns(&self) -> Vec<String> {
        vec!["drift_support_flag (1 scored 0 outside support 2 MC-unresolved)".into()]
    }

    fn impact_log_likelihood(&self, impact: &ImpactView, _choice: &[usize]) -> f64 {
        match self.surface.ln_likelihood(impact.latitude_deg, impact.longitude_deg) {
            Lookup::Value(l) => l,
            Lookup::Unresolved | Lookup::OutsideSupport => f64::NAN,
        }
    }

    fn predict(&self, impact: &ImpactView, out: &mut [f64]) {
        out[0] = match self.surface.ln_likelihood(impact.latitude_deg, impact.longitude_deg) {
            Lookup::Value(_) => 1.0,
            Lookup::OutsideSupport => 0.0,
            Lookup::Unresolved => 2.0,
        };
    }
}

#[cfg(test)]
mod tests;
