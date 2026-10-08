//! Debris drift: the likelihood of the recovered-debris evidence given each impact location,
//! by forward transport from a source grid and a recovery-observation model, evaluated at the
//! shared impact samples. Brief: threads/master-prompts/ocean-drift.md; rulings in
//! coordination/OCEAN_DRIFT.md; Davey alignment in results/davey-ch11-alignment.md.
//!
//! STATUS: FIRST BUILD ON A PROVISIONAL ANALYTIC OCEAN. `crates/ocean` (the shared transport) has
//! no owner yet, so the only transport here is `provisional_analytic_ocean` - closed-form fields,
//! straight coast, no data. In `mode = "stub-synthetic"` (the default and the only mode that runs)
//! the module scores SYNTHETIC finds generated from a declared source; nothing it returns is
//! evidence about MH370. `mode = "evidence"` refuses to construct until the shared transport
//! exists, so no stub number can be mistaken for a result.
//!
//! The estimator, and the contract rules each part answers to:
//! - Forward physics only; reverse inference by Bayes. Returns ln p(finds | impact sample, ocean
//!   model); the composer applies the weights (rule 1). No source-cell area factor (rule 1).
//! - One reusable ensemble per (source node, shared-environment realisation, object class);
//!   `source_grid` places nodes over the coverage region of a declared posterior, `interpolate`
//!   reads the surface at each impact sample linearly in L, never extrapolating (rules 3, 4).
//! - Recovery layer: the D5 conditional likelihood prod_j q(y_j|x)/Q(x), lambda cancelled exactly
//!   under p(lambda) ~ 1/lambda, relative identification probability by coast segment and time,
//!   arrival time and discovery time distinct with a declared delay (`recovery`).
//! - Shared environment marginalised ONCE outside the product over objects:
//!   L_m(x) = (1/E) sum_e prod_j L_j(x | m, e) (rule 8). Ocean models are the declared shared
//!   alternative `ocean-model`, never rescaled per model (rule 7); until the observation model
//!   supports comparable likelihoods the combination is a SENSITIVITY MIXTURE.
//! - Object response per class: (a_stokes, c_wind) drawn once per particle from declared uniform
//!   priors and persistent along the path (rule 9). Waves: a_stokes multiplies an explicit Stokes
//!   field and c_wind is drag BEYOND Stokes; a fitted total-leeway coefficient must not be put in
//!   c_wind alongside a_stokes > 0 (rule 10, arXiv:2005.09527).
//! - Monte Carlo: a node whose estimate is zero for any find is Unresolved, never zero likelihood;
//!   per-node minimum effective particle count is kept as a quality flag (rule 6).
//!
//! First-pass scope (brief section 6): release at the impact point at impact time (the ensemble
//! release time is `release_unix_s`, the 00:19:37 epoch; impact-time differences of minutes are
//! neglected against months of drift), initially floating, no family-dependent release, no
//! resurfacing, no refloating. The first version does not test the mechanisms it assumes away.
//!
//! Departures from Davey et al. (2016) ch. 11 (printed pp. 101-109) are D1-D5 of
//! results/davey-ch11-alignment.md; the GDP-empirical arm (A1) is prepared under prepare/gdp/.

mod evidence;
mod interpolate;
mod provisional_analytic_ocean;
mod recovery;
mod rng;
mod source_grid;

use hypothesis::{Alternatives, Hypothesis, ImpactView};
use interpolate::{Lookup, Node, Surface};
use provisional_analytic_ocean::{AnalyticOcean, Coast, Current, LocalPlane, Response};
use recovery::{Arrival, Delay, Identification, Observation, Recovery};
use rng::Rng;
use serde::Deserialize;
use source_grid::{SourceGrid, WeightedCell};

const REFERENCE_MAP: &str = include_str!("data/reference-map-no-exhaustion-prior-m0019b.csv");

fn d_coverage() -> f64 { 0.99 }
fn d_spacing() -> f64 { 10.0 }
fn d_margin() -> f64 { 100.0 }
fn d_particles() -> usize { 1000 }
fn d_seed() -> u64 { 1 }
fn d_release() -> f64 { 1_394_237_977.0 }
fn d_dt() -> f64 { 6.0 }
fn d_duration() -> f64 { 730.0 }
fn d_mode() -> String { "stub-synthetic".into() }
fn d_models() -> Vec<String> { vec!["provisional-analytic-stub".into()] }
fn d_scales() -> Vec<f64> { vec![1.0] }

#[derive(Deserialize, Clone)]
#[serde(deny_unknown_fields)]
struct OceanParams {
    current_east_mps: f64,
    current_north_mps: f64,
    #[serde(default)]
    stokes_east_mps: f64,
    #[serde(default)]
    stokes_north_mps: f64,
    #[serde(default)]
    wind_east_mps: f64,
    #[serde(default)]
    wind_north_mps: f64,
    diffusivity_m2s: f64,
    /// Straight coast along this meridian (stub geometry), ocean to the east.
    coast_lon_deg: f64,
}

#[derive(Deserialize, Clone)]
#[serde(deny_unknown_fields)]
struct ClassParams {
    name: String,
    a_stokes: [f64; 2],
    c_wind: [f64; 2],
}

#[derive(Deserialize, Clone)]
#[serde(deny_unknown_fields)]
struct RecoveryParams {
    bandwidth_km: f64,
    delay: String,
    delay_days: f64,
    segment_edges_km: Vec<f64>,
    #[serde(default)]
    period_breaks_days: Vec<f64>,
    #[serde(default)]
    rel_identification: Vec<Vec<f64>>,
}

#[derive(Deserialize, Clone)]
#[serde(deny_unknown_fields)]
struct SyntheticParams {
    true_lat_deg: f64,
    true_lon_deg: f64,
    finds: usize,
    seed: u64,
}

#[derive(Deserialize, Clone)]
#[serde(deny_unknown_fields)]
struct Params {
    #[serde(default = "d_mode")]
    mode: String,
    #[serde(default = "d_coverage")]
    coverage: f64,
    #[serde(default = "d_spacing")]
    spacing_nm: f64,
    #[serde(default = "d_margin")]
    margin_nm: f64,
    #[serde(default)]
    include_island: bool,
    #[serde(default = "d_particles")]
    particles_per_case: usize,
    #[serde(default = "d_seed")]
    seed: u64,
    #[serde(default = "d_release")]
    release_unix_s: f64,
    #[serde(default = "d_dt")]
    dt_hours: f64,
    #[serde(default = "d_duration")]
    duration_days: f64,
    /// Optional runtime path to an extent CSV (lat_deg,lon_deg,mass); default the embedded map.
    #[serde(default)]
    extent_map_path: Option<String>,
    #[serde(default = "d_models")]
    ocean_models: Vec<String>,
    /// Shared-environment realisations of the stub: a scale on the current per realisation.
    #[serde(default = "d_scales")]
    env_current_scales: Vec<f64>,
    ocean: OceanParams,
    classes: Vec<ClassParams>,
    recovery: RecoveryParams,
    synthetic: Option<SyntheticParams>,
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

/// A class's persistent response, drawn once per particle from the declared uniform prior.
fn draw_response(c: &ClassParams, rng: &mut Rng) -> Response {
    Response {
        a_stokes: c.a_stokes[0] + (c.a_stokes[1] - c.a_stokes[0]) * rng.uniform(),
        c_wind: c.c_wind[0] + (c.c_wind[1] - c.c_wind[0]) * rng.uniform(),
    }
}

/// Release `n` particles at (x, y) and return the beachings.
fn run_ensemble(ocean: &AnalyticOcean, x: f64, y: f64, class: &ClassParams, n: usize, dt_s: f64, steps: usize, rng: &mut Rng) -> Vec<Arrival> {
    let mut out = Vec::new();
    for _ in 0..n {
        let r = draw_response(class, rng);
        let f = ocean.integrate(x, y, &r, dt_s, steps, rng);
        if f.beached {
            out.push(Arrival { s_km: f.s_km, t_days: f.t_days });
        }
    }
    out
}

/// ln L at one node, environment marginalised outside the product over observations (rule 8).
/// `arrivals[e][c]` holds the ensemble for environment e and class c.
fn node_ln_likelihood(rec: &Recovery, obs: &[Observation], arrivals: &[Vec<Vec<Arrival>>], n: usize) -> (Node, f64) {
    let mut per_env = Vec::with_capacity(arrivals.len());
    let mut min_neff = f64::INFINITY;
    for env in arrivals {
        let q_tot: Vec<f64> = env.iter().map(|a| rec.q_total(a, n)).collect();
        let mut s = 0.0;
        for o in obs {
            let f = rec.q(o, &env[o.class], n);
            min_neff = min_neff.min(f.n_eff);
            if !(f.q > 0.0) || !(q_tot[o.class] > 0.0) {
                return (Node::Unresolved, 0.0);
            }
            s += f.q.ln() - q_tot[o.class].ln();
        }
        per_env.push(s);
    }
    let m = per_env.iter().copied().fold(f64::NEG_INFINITY, f64::max);
    let lse = m + per_env.iter().map(|v| (v - m).exp()).sum::<f64>().ln() - (per_env.len() as f64).ln();
    (Node::Value(lse), min_neff)
}

struct Built {
    grid: SourceGrid,
    surface: Surface,
    min_neff: Vec<f64>,
    observations: Vec<Observation>,
    arrival_fraction: f64,
    steps_per_second: f64,
    ln_l_scale_nm: f64,
}

fn build_stub(p: &Params) -> Result<Built, String> {
    let cells = match &p.extent_map_path {
        Some(path) => parse_cells(&std::fs::read_to_string(path).map_err(|e| format!("debris-drift: {path}: {e}"))?)?,
        None => parse_cells(REFERENCE_MAP)?,
    };
    let grid = SourceGrid::from_posterior(&cells, 0.25, p.coverage, p.spacing_nm, p.margin_nm, p.include_island)?;
    let (lat_mid, lon_mid) = grid.node(grid.index(grid.nlat / 2, grid.nlon / 2));
    let plane = LocalPlane { lat0: lat_mid, lon0: lon_mid };
    let (xc, _) = plane.to_xy(lat_mid, p.ocean.coast_lon_deg);
    let coast = Coast::through((xc, -5000.0), (xc, 5000.0), (xc + 1.0, 0.0));
    let rp = &p.recovery;
    let delay = match rp.delay.as_str() {
        "uniform" => Delay::Uniform { max_days: rp.delay_days },
        "exponential" => Delay::Exponential { mean_days: rp.delay_days },
        d => return Err(format!("debris-drift: unknown delay `{d}`")),
    };
    let nseg = rp.segment_edges_km.len().saturating_sub(1);
    let ident = if rp.rel_identification.is_empty() {
        Identification::uniform(rp.segment_edges_km.clone())
    } else {
        Identification { edges_km: rp.segment_edges_km.clone(), breaks_days: rp.period_breaks_days.clone(), rel: rp.rel_identification.clone() }
    };
    ident.validate()?;
    let _ = nseg;
    let rec = Recovery { ident, delay, bandwidth_km: rp.bandwidth_km, window_end_days: p.duration_days };
    let dt_s = p.dt_hours * 3600.0;
    let steps = (p.duration_days * 24.0 / p.dt_hours).round() as usize;
    let oceans: Vec<AnalyticOcean> = p.env_current_scales.iter().map(|&sc| AnalyticOcean {
        current: Current::Uniform { east: p.ocean.current_east_mps, north: p.ocean.current_north_mps },
        current_scale: sc,
        stokes: (p.ocean.stokes_east_mps, p.ocean.stokes_north_mps),
        wind: (p.ocean.wind_east_mps, p.ocean.wind_north_mps),
        diffusivity_m2s: p.ocean.diffusivity_m2s,
        coast: Some(coast),
    }).collect();

    // Synthetic finds from an INDEPENDENT ensemble at the declared true source (no inverse crime).
    let syn = p.synthetic.as_ref().ok_or("debris-drift: stub-synthetic mode needs [synthetic]")?;
    let (tx, ty) = plane.to_xy(syn.true_lat_deg, syn.true_lon_deg);
    let mut srng = Rng::derive(&[syn.seed, 0xF1_4D5]);
    let observations = synthetic_finds(&oceans[0], &rec, &p.classes[0], tx, ty, syn.finds, dt_s, steps, &mut srng)?;

    let n = p.particles_per_case;
    let mut nodes = vec![Node::NotComputed; grid.nlat * grid.nlon];
    let mut min_neff = vec![f64::NAN; grid.nlat * grid.nlon];
    let mut beached = 0usize;
    let mut released = 0usize;
    let clock = std::time::Instant::now();
    let mut steps_taken = 0.0;
    for k in 0..nodes.len() {
        if !grid.active[k] {
            continue;
        }
        let (la, lo) = grid.node(k);
        let (x, y) = plane.to_xy(la, lo);
        if coast.signed(x, y) >= 0.0 {
            nodes[k] = Node::Land;
            continue;
        }
        let arrivals: Vec<Vec<Vec<Arrival>>> = oceans.iter().enumerate().map(|(e, oc)| {
            p.classes.iter().enumerate().map(|(c, cl)| {
                let mut r = Rng::derive(&[p.seed, k as u64, e as u64, c as u64]);
                run_ensemble(oc, x, y, cl, n, dt_s, steps, &mut r)
            }).collect()
        }).collect();
        beached += arrivals[0][0].len();
        released += n;
        steps_taken += arrivals.iter().flatten().flatten().map(|a| a.t_days * 24.0 / p.dt_hours).sum::<f64>()
            + ((n * oceans.len() * p.classes.len()) as f64 - arrivals.iter().flatten().map(|a| a.len() as f64).sum::<f64>()) * steps as f64;
        let (node, ne) = node_ln_likelihood(&rec, &observations, &arrivals, n);
        nodes[k] = node;
        min_neff[k] = ne;
    }
    let elapsed = clock.elapsed().as_secs_f64();
    let surface = Surface { lat0: grid.lat0, lon0: grid.lon0, dlat: grid.dlat, dlon: grid.dlon, nlat: grid.nlat, nlon: grid.nlon, nodes };
    let ln_l_scale_nm = surface.ln_l_scale_nm(&vec![1.0; surface.nodes.len()], grid.spacing_nm);
    Ok(Built { grid, surface, min_neff, observations, arrival_fraction: beached as f64 / released.max(1) as f64, steps_per_second: steps_taken / elapsed.max(1e-9), ln_l_scale_nm })
}

/// Draw synthetic finds: a beached particle is identified with probability proportional to the
/// relative P_I at its discovery time, discovered after a delay drawn from the declared model,
/// and reported at a locality displaced by the declared bandwidth.
#[allow(clippy::too_many_arguments)]
fn synthetic_finds(ocean: &AnalyticOcean, rec: &Recovery, class: &ClassParams, x: f64, y: f64, finds: usize, dt_s: f64, steps: usize, rng: &mut Rng) -> Result<Vec<Observation>, String> {
    let pmax = rec.ident.rel.iter().flatten().copied().fold(0.0, f64::max);
    let mut out = Vec::new();
    let mut tries = 0usize;
    while out.len() < finds {
        tries += 1;
        if tries > 200_000 + 1000 * finds {
            return Err("debris-drift: synthetic source produced too few identifiable finds".into());
        }
        let r = draw_response(class, rng);
        let f = ocean.integrate(x, y, &r, dt_s, steps, rng);
        if !f.beached {
            continue;
        }
        let d = match rec.delay {
            Delay::Uniform { max_days } => max_days * rng.uniform(),
            Delay::Exponential { mean_days } => -mean_days * (1.0 - rng.uniform()).ln(),
        };
        let t = f.t_days + d;
        if t >= rec.window_end_days {
            continue;
        }
        let s = f.s_km + rec.bandwidth_km * rng.normal();
        let Some(k) = rec.ident.segment(s) else { continue };
        let pidx = rec.ident.breaks_days.partition_point(|&b| b <= t);
        if rng.uniform() * pmax >= rec.ident.rel[k][pidx] {
            continue;
        }
        let day = t.floor();
        out.push(Observation { id: format!("synthetic:find-{:02}", out.len() + 1), class: 0, s_km: s, t_start_days: day, t_end_days: day + 1.0 });
    }
    Ok(out)
}

fn validate(p: &Params) -> Result<(), String> {
    if p.classes.is_empty() || p.env_current_scales.is_empty() {
        return Err("debris-drift: need at least one object class and one environment realisation".into());
    }
    for c in &p.classes {
        if c.name.is_empty() || c.a_stokes[0] > c.a_stokes[1] || c.c_wind[0] > c.c_wind[1] {
            return Err(format!("debris-drift: class `{}` needs a name and ordered [lo, hi] ranges", c.name));
        }
        if c.c_wind[1] > 0.0 && c.a_stokes[1] == 0.0 {
            // Not an error: a total-leeway coefficient with Stokes off is a legitimate implicit
            // treatment. The reverse - fitted total leeway in c_wind with a_stokes > 0 - is the
            // double count (rule 10) and cannot be detected from numbers alone; documented above.
        }
    }
    if !(p.release_unix_s.is_finite()) || p.dt_hours <= 0.0 || p.duration_days <= 0.0 || p.particles_per_case == 0 {
        return Err("debris-drift: release time, dt, duration and particle count must be positive".into());
    }
    Ok(())
}

/// The stringent identity set with discovery intervals in days after `release_unix_s`
/// (a single reported day d is the interval [d, d + 1)). Observation IDs are `debris:<object_id>`,
/// prefixed by the data source so that two modules using the same datum collide.
pub(crate) fn stringent_intervals(release_unix_s: f64) -> Result<Vec<(String, f64, f64, String)>, String> {
    let mut out = Vec::new();
    for r in evidence::parse(evidence::TABLE)?.into_iter().filter(|r| r.stringent) {
        let a = (evidence::iso_date_unix_s(&r.discovery_start)? - release_unix_s) / 86_400.0;
        let b = (evidence::iso_date_unix_s(&r.discovery_end)? - release_unix_s) / 86_400.0 + 1.0;
        out.push((format!("debris:{}", r.object_id), a, b, r.motion_class));
    }
    Ok(out)
}

struct DebrisDrift {
    models: Vec<String>,
    surfaces: Vec<Surface>,
    observations: Vec<String>,
}

pub fn new(params: &toml::Value) -> Result<Box<dyn Hypothesis>, String> {
    let p: Params = params.clone().try_into().map_err(|e| format!("debris-drift: {e}"))?;
    match p.mode.as_str() {
        "stub-synthetic" => {}
        "evidence" => {
            let n = stringent_intervals(p.release_unix_s)?.len();
            return Err(format!("debris-drift: mode `evidence` ({n} stringent finds) needs the shared ocean transport (crates/ocean), which does not exist yet; the provisional analytic ocean may not score real finds"));
        }
        m => return Err(format!("debris-drift: unknown mode `{m}`")),
    }
    if p.ocean_models.len() != 1 {
        return Err("debris-drift: the provisional stub provides exactly one ocean model".into());
    }
    validate(&p)?;
    let b = build_stub(&p)?;
    let unresolved = b.surface.nodes.iter().filter(|n| matches!(n, Node::Unresolved)).count();
    eprintln!(
        "debris-drift PROVISIONAL STUB, synthetic finds, not evidence: {} active nodes ({} unresolved), coverage reached {:.4}, main-band mass {:.4}, arrival fraction {:.3}, {:.3e} particle-steps/s, ln L scale {:.1} NM, min n_eff {:.1}",
        b.grid.n_active(), unresolved, b.grid.covered_mass, b.grid.component_mass[b.grid.main_component], b.arrival_fraction, b.steps_per_second, b.ln_l_scale_nm,
        b.min_neff.iter().copied().filter(|x| x.is_finite()).fold(f64::INFINITY, f64::min)
    );
    Ok(Box::new(DebrisDrift {
        models: p.ocean_models.clone(),
        observations: b.observations.iter().map(|o| o.id.clone()).collect(),
        surfaces: vec![b.surface],
    }))
}

impl Hypothesis for DebrisDrift {
    fn observations(&self) -> Vec<String> {
        self.observations.clone()
    }

    fn alternatives(&self) -> Vec<Alternatives> {
        let w = 1.0 / self.models.len() as f64;
        let opts: Vec<(&str, f64)> = self.models.iter().map(|m| (m.as_str(), w)).collect();
        vec![Alternatives::new("ocean-model", &opts)]
    }

    /// Same observation space and normalisation under every ocean model (q/Q is a normalised
    /// density of the finds), so options may be mixed - as a sensitivity mixture (rule 7).
    fn absolute_scale(&self) -> bool {
        true
    }

    fn prediction_columns(&self) -> Vec<String> {
        vec!["drift_support_flag (1 scored 0 outside support 2 MC-unresolved)".into()]
    }

    fn impact_log_likelihood(&self, impact: &ImpactView, choice: &[usize]) -> f64 {
        let m = choice.first().copied().unwrap_or(0);
        match self.surfaces[m].ln_likelihood(impact.latitude_deg, impact.longitude_deg) {
            Lookup::Value(l) => l,
            Lookup::Unresolved | Lookup::OutsideSupport => f64::NAN,
        }
    }

    fn predict(&self, impact: &ImpactView, out: &mut [f64]) {
        out[0] = match self.surfaces[0].ln_likelihood(impact.latitude_deg, impact.longitude_deg) {
            Lookup::Value(_) => 1.0,
            Lookup::OutsideSupport => 0.0,
            Lookup::Unresolved => 2.0,
        };
    }
}

#[cfg(test)]
mod tests;
