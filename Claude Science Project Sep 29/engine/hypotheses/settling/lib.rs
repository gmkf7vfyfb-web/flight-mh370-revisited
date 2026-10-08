//! Settling: where the wreckage of one ocean impact comes to rest on the seabed.
//!
//! A TRANSFORM, NOT EVIDENCE (brief section 2, rule 1). It returns no log-likelihood of its own
//! (`impact_log_likelihood` is the trait default, 0.0 = "adds nothing") and declares no
//! observations: the one thing that could be scored, the search having found nothing, belongs
//! to searched areas.
//!
//! PRIMARY OUTPUT: WRECKAGE SAMPLES (ARCHITECTURE decision 2, option 3). For each impact sample,
//! [`Settling::emit`] returns `draws` wreckage draws. A draw is ONE settled configuration W of the
//! whole field — one breakup family, one ocean-error realisation, and every class's pieces — and
//! carries weight 1 / draws of its parent, so creating descendants never creates probability.
//! Draws are alternative outcomes, not extra wreckage: a consumer AVERAGES over draws and never
//! multiplies (searched-areas brief, section 2). Within a draw each class is represented by up
//! to K representative elements (breakup.toml, `representatives_per_class`), each standing for
//! `multiplicity` physical pieces of a stated projected area. Draw d of an impact is a function
//! of the impact and d alone, so adaptive refinement from 512 to 4,096 draws keeps the first 512.
//! The runner stage that calls `emit` and stores its rows is core request 12, not built here.
//!
//! SECONDARY OUTPUT: `predict` / `prediction_columns`, a cheap moment diagnostic computed from the
//! same emitter with `moment_draws` draws (one implementation; deterministic per sample).
//!
//! MODEL (after the methodology Pete shared, input not truth):
//!   r_rest = r_contact + carry + drift afloat + integral of (U(z) + error) dt + glide
//!                                                               (+ seabed movement, not modelled)
//! - carry: travel along the impact track after contact (breakup, skipping), V_h x carry_s, with
//!   lateral scatter.
//! - drift afloat: (surface current + per-event surface error + leeway x 10 m wind) x float time,
//!   for the share of a class that floats before it sinks. The share that stays afloat for hours
//!   is surface-drift debris: emitted with fate `afloat` and no seabed position, as the
//!   sink-versus-float hook (queued with Pete; drift consumes the partition later).
//! - sinking: integrated layer by layer, dt = dz / w(z), w the terminal speed of a flooded body
//!   falling broadside, w = k sqrt(2 g s (1 - rho_w/rho_m) / (rho_w Cd)), with s mass per projected
//!   area and k >= 1 a descent factor for fluttering bodies (physics.rs). In-situ density enters
//!   per layer (about +3% by 6 km, so about -1.5% in w).
//! - glide: horizontal motion through the water at G w, heading diffusing with depth with memory
//!   l, giving E|offset|^2 = 2 G^2 l^2 (x - 1 + exp(-x)), x = depth / l (straight glide for l >>
//!   depth, random walk for l << depth). Bounded lateral motion with stated uncertainty, as the
//!   brief asks; not a hydrodynamic model of plate flutter (Andersen, Pesavento and Wang 2005,
//!   J. Fluid Mech. 541; Field et al. 1997, Nature 388) — those set the plausible G and l ranges.
//! - stop at first seabed contact (rule 9): sliding, rolling, burial and remobilisation are a
//!   separate step, not modelled. Contact is found against the seabed at the element's CURRENT
//!   position, so a slope is honoured.
//!
//! ASSUMPTIONS, each declared (brief section 8: educated estimates are acceptable when declared):
//! 1. Breakup families are selected by vertical and total SPECIFIC kinetic energy only
//!    (breakup.rs). The flight-path angle is implied by the two. Attitude and the energy-transfer
//!    duration are recorded upstream but unused here: the first pass spends its complexity on
//!    sinking rate, because at 4 km against 0.1 m/s a sink rate of 2, 0.5, 0.05 or 0.01 m/s moves
//!    an element 0.2, 0.8, 8 or 40 km (brief section 6) — no current precision compensates for an
//!    unsupported sink-rate assumption.
//! 2. Every number in breakup.toml (areal densities, material densities, drag coefficients, glide
//!    ranges, float times, piece counts, mass shares) is an educated estimate. Analogue anchors
//!    for the family selection are in breakup.toml's comments; the analogue and model survey is
//!    data/analogues.csv with primary sources.
//! 3. One family per draw: a field breaks up coherently. Families are mixed across draws in
//!    proportion to P(family | impact), never averaged within a draw.
//! 4. One ocean-error realisation per draw, shared by every element of that draw (rule 10).
//!    Independent per-fragment noise would shrink the field artificially.
//! 5. Element properties are independent across representatives: pieces of one class are not
//!    identical. Pieces represented by one representative sit at its point; the within-class
//!    spread is carried by the K representatives (a computational choice).
//! 6. Piece area follows from mass conservation: area = mass_share x impact mass / (pieces x s).
//! 7. THE OCEAN IS A PROVISIONAL STUB (ocean_stub.rs). No reanalysis, no product choice, no field
//!    interpolation (inbox ruling of 8 Oct 2026). Every number that depends on currents, density
//!    or bathymetry is PROVISIONAL until `crates/ocean` lands, and every output carries the
//!    stub's label. The profile is taken at the release point and held for the descent (column
//!    assumption); time is frozen within a descent.
//! 8. Below the ocean model's bottom one of the shared crate's three explicit rules applies
//!    (default `hold-deepest-level`; `linear-to-zero-at-seabed` and `refuse` are the declared
//!    alternatives), and the extrapolated depth range is reported per element. A zero is never
//!    substituted silently; `refuse` leaves the element not computed.
//! 9. Vertical velocity: the stub reports none. It is flagged absent and not read as zero; the
//!    descent uses w alone.
//!
//! WHAT IS NOT YET HERE, deliberately: the implosion-at-depth event (descent time is computed
//! and emitted per element, which is the hook), post-contact movement, and the shared breakup
//! field freeze (results/breakup-field-candidate.md is the candidate).

mod breakup;
mod ocean_stub;
mod physics;

use breakup::{Breakup, FAMILIES};
use hypothesis::{Hypothesis, ImpactView};
use ocean_stub::{AnalyticStub, BelowModelBottom, ErrorModel, Profile, ProvisionalOcean};
use physics::{OceanRealisation, Rng, Sinker, Terms};
use serde::Deserialize;

#[derive(Deserialize)]
#[serde(deny_unknown_fields)]
struct Params {
    /// Draws behind each `predict` call (the moment diagnostic).
    moment_draws: usize,
    /// Integration step in depth (m).
    step_m: f64,
    /// Terms of the offset: carry, float, current, glide, ocean-error. All of them for the
    /// estimate; the report turns them off one at a time.
    #[serde(default = "all_terms")]
    terms: Vec<String>,
    /// Below the ocean model's own bottom: `hold-deepest-level`, `linear-to-zero-at-seabed` or
    /// `refuse` (the shared crate's three rules).
    below_model_bottom: String,
    /// PROVISIONAL. Deleted when crates/ocean lands.
    provisional_ocean_stub: AnalyticStub,
}

fn all_terms() -> Vec<String> {
    ["carry", "float", "current", "glide", "ocean-error"].map(String::from).to_vec()
}

/// Where an emitted element ended up.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum Fate {
    /// At rest on the seabed (first contact).
    Settled = 0,
    /// Stays afloat for hours: surface-drift debris, no seabed position (sink-versus-float hook).
    Afloat = 1,
    /// Could not be computed (no seabed in the column, outside the ocean's support, or an element
    /// not denser than the water). NaN position. Never read as "impossible".
    NotComputed = 2,
}

/// One representative element of one wreckage draw.
#[derive(Debug, Clone, Copy, PartialEq)]
pub struct WreckageElement {
    pub draw: u32,
    /// Share of the parent impact sample's weight carried by this element's DRAW (1 / draws).
    /// Every element of a draw has the same value: the draw is the unit of probability.
    pub draw_weight: f64,
    pub family: u8,
    pub class: u8,
    pub fate: Fate,
    /// Physical pieces this representative stands for.
    pub multiplicity: f64,
    pub piece_area_m2: f64,
    pub piece_mass_kg: f64,
    /// Offset of the resting point (or surface position, if afloat) from the impact (m).
    pub east_m: f64,
    pub north_m: f64,
    pub latitude_deg: f64,
    pub longitude_deg: f64,
    /// Seabed depth at first contact (m); NaN unless settled.
    pub depth_m: f64,
    /// Time afloat before sinking, and time from leaving the surface to the seabed (s).
    pub float_s: f64,
    pub descent_s: f64,
    pub mean_sink_mps: f64,
    pub below_model_bottom_m: f64,
}

/// Column names (with units) of [`WreckageElement::row`], for the runner's store (core request 12).
pub const WRECKAGE_COLUMNS: [&str; 17] = [
    "draw",
    "draw weight",
    "family",
    "class",
    "fate",
    "multiplicity (pieces)",
    "piece area (m2)",
    "piece mass (kg)",
    "east (m)",
    "north (m)",
    "latitude (deg)",
    "longitude (deg)",
    "depth (m)",
    "float time (s)",
    "descent time (s)",
    "mean sink speed (m per s)",
    "below model bottom (m)",
];

impl WreckageElement {
    pub fn row(&self) -> [f64; 17] {
        [
            self.draw as f64,
            self.draw_weight,
            self.family as f64,
            self.class as f64,
            self.fate as u8 as f64,
            self.multiplicity,
            self.piece_area_m2,
            self.piece_mass_kg,
            self.east_m,
            self.north_m,
            self.latitude_deg,
            self.longitude_deg,
            self.depth_m,
            self.float_s,
            self.descent_s,
            self.mean_sink_mps,
            self.below_model_bottom_m,
        ]
    }
}

pub struct Settling {
    breakup: Breakup,
    ocean: Box<dyn ProvisionalOcean>,
    terms: Terms,
    rule: BelowModelBottom,
    step_m: f64,
    moment_draws: usize,
}

pub fn new(params: &toml::Value) -> Result<Box<dyn Hypothesis>, String> {
    Ok(Box::new(Settling::from_params(params)?))
}

/// Per class, in this order, for the moment diagnostic (piece-weighted over draws).
const CLASS_COLUMNS: [&str; 7] = [
    "settled share",
    "mean east (m)",
    "mean north (m)",
    "sd east (m)",
    "sd north (m)",
    "p90 offset (m)",
    "median descent (s)",
];

impl Settling {
    pub fn from_params(params: &toml::Value) -> Result<Settling, String> {
        let p: Params = params.clone().try_into().map_err(|e| format!("settling: {e}"))?;
        p.provisional_ocean_stub.check()?;
        let breakup = Breakup::parse(include_str!("breakup.toml"))?;
        Settling::with(breakup, Box::new(p.provisional_ocean_stub), &p.terms, BelowModelBottom::parse(&p.below_model_bottom)?, p.step_m, p.moment_draws)
    }

    fn with(breakup: Breakup, ocean: Box<dyn ProvisionalOcean>, terms: &[String], rule: BelowModelBottom, step_m: f64, moment_draws: usize) -> Result<Settling, String> {
        if let Some(t) = terms.iter().find(|t| !all_terms().contains(t)) {
            return Err(format!("settling: unknown term `{t}`; known: {:?}", all_terms()));
        }
        if !(step_m > 0.0 && step_m <= 500.0) || moment_draws == 0 {
            return Err("settling: step_m in (0, 500] and moment_draws positive".into());
        }
        let has = |name: &str| terms.iter().any(|t| t == name);
        let terms = Terms { carry: has("carry"), float: has("float"), current: has("current"), glide: has("glide"), ocean_error: has("ocean-error") };
        Ok(Settling { breakup, ocean, terms, rule, step_m, moment_draws })
    }

    pub fn classes(&self) -> &[String] {
        &self.breakup.classes
    }

    pub fn ocean_label(&self) -> &str {
        self.ocean.label()
    }

    /// P(family | impact), or None outside the selection rule's domain.
    pub fn family_probabilities(&self, impact: &ImpactView) -> Option<[f64; 3]> {
        if !(impact.mass_kg > 0.0) {
            return None;
        }
        self.breakup.selection.from_energy(impact.kinetic_energy_j / impact.mass_kg, impact.vertical_kinetic_energy_j / impact.mass_kg)
    }

    /// The wreckage draws of one impact sample: `draws` settled configurations, each with weight
    /// 1 / draws. Err if the impact is outside the module's domain (no mass or energy, or no
    /// ocean profile at the contact point); the caller then records NaN, not an empty field.
    pub fn emit(&self, impact: &ImpactView, draws: usize) -> Result<Vec<WreckageElement>, String> {
        self.emit_with(impact, 0..draws, 1.0 / draws as f64, None)
    }

    /// Draws `indices` of an impact, each with `draw_weight`, optionally forcing the family (for
    /// the report's per-family panels). Draw d is the same whatever range it is emitted in, so
    /// adaptive refinement emits only the new indices.
    pub fn emit_with(&self, impact: &ImpactView, indices: std::ops::Range<usize>, draw_weight: f64, force_family: Option<usize>) -> Result<Vec<WreckageElement>, String> {
        let families = self.family_probabilities(impact).ok_or("settling: impact outside the family-selection domain (mass, energy)")?;
        let profile = self
            .ocean
            .profile(impact.latitude_deg, impact.longitude_deg, impact.unix_s)
            .ok_or("settling: no ocean profile at the contact point")?;
        let error = self.ocean.error_model();
        let mut out = Vec::new();
        for d in indices {
            let mut rng = Rng::seeded(&seed_words(impact, d));
            let u = rng.uniform();
            let family = force_family.unwrap_or_else(|| pick(&families, u));
            let realised = OceanRealisation::draw(&error, &mut rng);
            let ocean = if self.terms.ocean_error { realised } else { OceanRealisation::default() };
            self.draw_field(impact, d, draw_weight, family, &profile, &ocean, &error, &mut rng, &mut out);
        }
        Ok(out)
    }

    #[allow(clippy::too_many_arguments)]
    fn draw_field(
        &self,
        impact: &ImpactView,
        draw: usize,
        draw_weight: f64,
        family: usize,
        profile: &Profile,
        ocean: &OceanRealisation,
        error: &ErrorModel,
        rng: &mut Rng,
        out: &mut Vec<WreckageElement>,
    ) {
        let (lat0, lon0) = (impact.latitude_deg, impact.longitude_deg);
        let position = |offset: [f64; 2]| geo::advance(lat0, lon0, 0.0, offset[1] / geo::M_PER_KT_S, offset[0] / geo::M_PER_KT_S, 1.0);
        let seabed = |offset: [f64; 2]| {
            let (lat, lon) = position(offset);
            self.ocean.seabed_depth_m(lat, lon)
        };
        let velocity = [impact.velocity_east_mps, impact.velocity_north_mps];
        let speed = velocity[0].hypot(velocity[1]);
        for (c, element) in self.breakup.elements[family].iter().enumerate() {
            let pieces = element.pieces.draw(rng).round().max(1.0);
            let k = (pieces as usize).min(self.breakup.representatives_per_class);
            for _ in 0..k {
                let sinker = Sinker::draw(element, rng);
                let piece_mass = element.mass_share * impact.mass_kg / pieces;
                let mut at = [0.0; 2];
                // Drawn whether or not the term is on (common random numbers across the report's
                // term-by-term runs).
                let (carry_t, carry_x) = (element.carry_s.draw(rng), 2.0 * rng.uniform() - 1.0);
                if self.terms.carry && speed > 0.0 {
                    let along = [velocity[0] / speed, velocity[1] / speed];
                    let d = speed * carry_t;
                    let lateral = element.carry_lateral * d * carry_x;
                    at = [d * along[0] - lateral * along[1], d * along[1] + lateral * along[0]];
                }
                let fate_u = rng.uniform();
                let mut row = WreckageElement {
                    draw: draw as u32,
                    draw_weight,
                    family: family as u8,
                    class: c as u8,
                    fate: Fate::NotComputed,
                    multiplicity: pieces / k as f64,
                    piece_area_m2: piece_mass / sinker.areal_density_kg_m2,
                    piece_mass_kg: piece_mass,
                    east_m: f64::NAN,
                    north_m: f64::NAN,
                    latitude_deg: f64::NAN,
                    longitude_deg: f64::NAN,
                    depth_m: f64::NAN,
                    float_s: 0.0,
                    descent_s: f64::NAN,
                    mean_sink_mps: f64::NAN,
                    below_model_bottom_m: f64::NAN,
                };
                if fate_u < element.stays_afloat {
                    let (lat, lon) = position(at);
                    row.fate = Fate::Afloat;
                    row.float_s = f64::INFINITY;
                    (row.east_m, row.north_m, row.latitude_deg, row.longitude_deg) = (at[0], at[1], lat, lon);
                    out.push(row);
                    continue;
                }
                // Floats first unless it is among the share that sinks at once.
                if fate_u >= element.stays_afloat + element.sinks_at_once {
                    let t = element.float_s.draw(rng);
                    let a = element.leeway.draw(rng);
                    if self.terms.float {
                        let (s, w) = (profile.surface_current_mps, profile.wind_mps);
                        let e = if self.terms.ocean_error { ocean.surface } else { [0.0; 2] };
                        at = [at[0] + t * (s[0] + e[0] + a * w[0]), at[1] + t * (s[1] + e[1] + a * w[1])];
                        row.float_s = t;
                    }
                }
                if let Some(landing) = physics::sink(at, &sinker, profile, ocean, error, &self.terms, self.rule, self.step_m, &seabed, rng) {
                    let rest = [at[0] + landing.offset_m[0], at[1] + landing.offset_m[1]];
                    let (lat, lon) = position(rest);
                    row.fate = Fate::Settled;
                    (row.east_m, row.north_m, row.latitude_deg, row.longitude_deg) = (rest[0], rest[1], lat, lon);
                    (row.depth_m, row.descent_s, row.mean_sink_mps, row.below_model_bottom_m) =
                        (landing.depth_m, landing.descent_s, landing.mean_sink_mps, landing.below_model_bottom_m);
                }
                out.push(row);
            }
        }
    }
}

/// The impact sample's own fields and the draw index, as generator seed words.
fn seed_words(impact: &ImpactView, draw: usize) -> Vec<u64> {
    vec![
        impact.parent as u64,
        impact.unix_s.to_bits(),
        impact.latitude_deg.to_bits(),
        impact.longitude_deg.to_bits(),
        impact.velocity_east_mps.to_bits(),
        impact.velocity_north_mps.to_bits(),
        impact.velocity_up_mps.to_bits(),
        draw as u64,
    ]
}

/// Index of the category u in [0, 1) falls into.
fn pick(p: &[f64], u: f64) -> usize {
    let total: f64 = p.iter().sum();
    let mut sum = 0.0;
    for (i, x) in p.iter().enumerate() {
        sum += x / total;
        if u < sum {
            return i;
        }
    }
    p.len() - 1
}

/// Weighted quantile of (value, weight) pairs.
fn quantile(mut v: Vec<(f64, f64)>, q: f64) -> f64 {
    v.retain(|(x, w)| x.is_finite() && *w > 0.0);
    if v.is_empty() {
        return f64::NAN;
    }
    v.sort_by(|a, b| a.0.total_cmp(&b.0));
    let total: f64 = v.iter().map(|x| x.1).sum();
    let mut sum = 0.0;
    for (x, w) in &v {
        sum += w;
        if sum >= q * total {
            return *x;
        }
    }
    v[v.len() - 1].0
}

impl Hypothesis for Settling {
    fn prediction_columns(&self) -> Vec<String> {
        let mut columns: Vec<String> = FAMILIES.iter().map(|f| format!("{f} probability")).collect();
        columns.push("contact depth (m)".into());
        for class in &self.breakup.classes {
            columns.extend(CLASS_COLUMNS.iter().map(|c| format!("{class} {c}")));
        }
        columns
    }

    /// The moment diagnostic: family probabilities, contact depth, and per class the piece-
    /// weighted settled share, mean and spread of the resting offset, its 90th-percentile
    /// distance and the median descent time, from `moment_draws` wreckage draws. NaN where not
    /// computed.
    fn predict(&self, impact: &ImpactView, out: &mut [f64]) {
        out.fill(f64::NAN);
        let Some(families) = self.family_probabilities(impact) else { return };
        out[..3].copy_from_slice(&families);
        out[3] = self.ocean.seabed_depth_m(impact.latitude_deg, impact.longitude_deg).unwrap_or(f64::NAN);
        let Ok(rows) = self.emit(impact, self.moment_draws) else { return };
        for (c, slot) in out[4..].chunks_exact_mut(CLASS_COLUMNS.len()).enumerate() {
            let class: Vec<&WreckageElement> = rows.iter().filter(|r| r.class as usize == c).collect();
            let all: f64 = class.iter().map(|r| r.multiplicity * r.draw_weight).sum();
            let settled: Vec<&&WreckageElement> = class.iter().filter(|r| r.fate == Fate::Settled).collect();
            let w: f64 = settled.iter().map(|r| r.multiplicity * r.draw_weight).sum();
            slot[0] = if all > 0.0 { w / all } else { f64::NAN };
            if !(w > 0.0) {
                continue;
            }
            let mean = |f: &dyn Fn(&WreckageElement) -> f64| settled.iter().map(|r| r.multiplicity * r.draw_weight * f(r)).sum::<f64>() / w;
            let (me, mn) = (mean(&|r| r.east_m), mean(&|r| r.north_m));
            slot[1] = me;
            slot[2] = mn;
            slot[3] = mean(&|r| (r.east_m - me).powi(2)).sqrt();
            slot[4] = mean(&|r| (r.north_m - mn).powi(2)).sqrt();
            slot[5] = quantile(settled.iter().map(|r| (r.east_m.hypot(r.north_m), r.multiplicity * r.draw_weight)).collect(), 0.9);
            slot[6] = quantile(settled.iter().map(|r| (r.descent_s, r.multiplicity * r.draw_weight)).collect(), 0.5);
        }
    }
}

#[cfg(test)]
mod tests;
