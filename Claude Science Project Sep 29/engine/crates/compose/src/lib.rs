//! Stage 4, the composer: the flight posterior on the shared impact samples, reweighted by any
//! chosen set of impact-level modules, with the bookkeeping that makes the product legitimate.
//!
//! Inputs, per replicate: the impact samples (impacts.npy columns, with the `mh370 evaluate`
//! columns appended row-aligned), and the filter's per-mode evidence from run.json. The
//! samples' `weight` column is the hand-off weight: within a replicate the rows of stratum m
//! sum to P_i(m | D), the replicate's own posterior probability of that mode.
//!
//! For one evidence set with factors f (modules, or the terminal stage's 00:19 data option)
//! and the combinations c of the alternatives they declare, with prior P(c):
//!
//! ```text
//!   l_rc        = sum_f ln p(D_f | x_r, c)                       one value per factor and combination
//!   L_r         = sum_{c consistent with given} P(c | given) exp(l_rc)       joint marginalisation
//!   D_im        = sum_{r in (i,m)} w_r L_r / sum_{r in (i,m)} w_r           evidence increment
//!   w'_r        = w_r L_r / sum_r w_r L_r                         composed weight, within replicate i
//!   ln Z'_im    = ln Z_im + ln D_im                               per (replicate, mode), for summary.rs
//!   P(c | D)    ∝ P(c) sum_m prior_m mean_i Z_im D_imc            island estimator, as summary.rs pools
//! ```
//!
//! An alternative that two modules declare by the same name is one alternative: it is summed
//! once, inside L_r, over the product of both modules' likelihoods. Marginalising each module
//! separately and then multiplying treats one uncertain ocean as two independent ones.
//!
//! The composer does not pool replicates and draws no densities. It returns per-(replicate,
//! mode) evidence and composed weights, and summary.rs pools them with its own `pooling()` and
//! writes the PDFs, exactly as it does for final.npy. Pooling a composed product that way is
//! identical to reweighting the pooled base sample directly; the tests check that identity.
//!
//! Rules enforced rather than trusted (common.txt composition rules, composer.md section 2):
//! - each observation ID is used once, across the factors of a set and the base product;
//! - a factor already in the base product is never composed onto it again; every product
//!   records the factors and the sample columns it contains;
//! - a module that is not on an absolute scale is composed only within a single option of each
//!   alternative it declares (`given`), and the posterior probability of those options is not
//!   reported; alternatives followed per trajectory stratum count as mixing, so are refused;
//! - an alternative marginalised in the base product cannot be declared by a module composed
//!   later: modules sharing an alternative are composed in one set, or the marginalisation
//!   would not be joint;
//! - 0.0 is an exact "selected, no data used": the module is in the product and changes
//!   nothing. NaN is "not computed": never zero likelihood and never minus infinity. A row
//!   that any factor did not compute is carried at the mean likelihood ratio D_im of the
//!   computed rows of its (replicate, mode), so it neither gains nor loses share within it,
//!   and the evidence D_im is that of the computed rows. The count and the pre-composition
//!   weight of such rows are reported per factor, and the set is refused if that weight
//!   exceeds the set's tolerance in any replicate;
//! - conditionals are labelled: a product with `given` alternatives is conditional on them,
//!   says so, and carries P(option | D) beside p(x | D, option) where the scale allows it;
//! - a product whose effective number of parents falls below the set's floor in any
//!   replicate is marked unconverged, and summary.rs draws no PDF for it.
//!
//! Results per descent family come first: per replicate, each family's prior and posterior
//! mass and its Bayes factor ln(sum_family w L / sum_family w), which is independent of the
//! family prior and so supports a prior sensitivity. Any average across families appears only
//! beside such a sensitivity.

use hypothesis::{Alternatives, Hypothesis, MODES};
use serde::Serialize;
use std::collections::{BTreeMap, HashMap};

pub const MODE_COUNT: usize = MODES.len();

/// The base product's name in [`Product::contains`].
pub const FILTER: &str = "filter";

/// Sample columns the composer reads, named as in impacts.rs `IMPACT_COLUMNS`.
pub const WEIGHT: &str = "weight";
pub const PARENT: &str = "parent";
pub const STRATUM: &str = "mode";
pub const TRAJECTORY_OPTION: &str = "alternative";
pub const FAMILY: &str = "family";

/// Names of the terminal stage's alternatives: the chosen 00:19 data option (one option, so it
/// only labels the columns), and the BFO models it mixes by their priors.
pub const TERMINAL_DATA: &str = "terminal-data";
pub const BFO_MODEL: &str = "bfo-model";

/// Default floor on the effective number of parents per replicate: below it a product is
/// unconverged. The core's convention for 00:19 data options (about 1,000 effective parents).
pub const DEFAULT_ESS_FLOOR: f64 = 1000.0;

/// Default refusal threshold on the share of pre-composition weight that a factor did not
/// compute, as `[[compose]] tolerance` defaults in config.rs.
pub const DEFAULT_TOLERANCE: f64 = 1e-3;

/// What one factor declared: an impact module (as evaluate.json records it), or the terminal
/// stage's data option.
#[derive(Debug, Clone)]
pub struct Declaration {
    pub name: String,
    /// Column prefix: `<module>:loglik` for impact modules (evaluate columns), `loglik` for the
    /// terminal data option (impacts.npy). Under alternatives the column is
    /// `<prefix>:<label>/<label>...`, labels in declaration order.
    pub prefix: String,
    pub observations: Vec<String>,
    pub alternatives: Vec<Alternatives>,
    pub absolute_scale: bool,
}

impl Declaration {
    /// An impact module, from its own declarations.
    pub fn module(name: &str, module: &dyn Hypothesis) -> Self {
        Declaration {
            name: name.to_string(),
            prefix: format!("{name}:loglik"),
            observations: module.observations(),
            alternatives: module.alternatives(),
            absolute_scale: module.absolute_scale(),
        }
    }

    /// The terminal stage's data option `option`: impacts.npy column `loglik:<option>`, or
    /// `loglik:<option>/<bfo model>` per BFO model (label, prior). The 00:19 observations it
    /// scores are named by the caller, from the configured target. Gaussian BTO and BFO
    /// densities: an absolute scale.
    pub fn terminal(option: &str, bfo_models: &[(String, f64)], observations: Vec<String>) -> Self {
        let mut alternatives = vec![Alternatives::new(TERMINAL_DATA, &[(option, 1.0)])];
        if !bfo_models.is_empty() {
            alternatives.push(Alternatives { name: BFO_MODEL.to_string(), options: bfo_models.to_vec(), sweep_label: None });
        }
        Declaration { name: format!("terminal:{option}"), prefix: "loglik".to_string(), observations, alternatives, absolute_scale: true }
    }

    fn column(&self, labels: &[&str]) -> String {
        if labels.is_empty() {
            self.prefix.clone()
        } else {
            format!("{}:{}", self.prefix, labels.join("/"))
        }
    }
}

/// The filter's evidence for one autopilot-mode stratum of one replicate, as run.json records
/// it (`replicates[].modes[]`).
#[derive(Debug, Clone, Copy, PartialEq, Serialize)]
pub struct Mode {
    pub prior_weight: f64,
    /// Minus infinity for a mode that was not run (JSON null).
    pub log_evidence: f64,
    pub posterior_probability: f64,
}

/// One replicate's impact samples: named columns, row-major values.
#[derive(Debug, Clone)]
pub struct Replicate {
    pub seed: u64,
    pub columns: Vec<String>,
    pub values: Vec<f64>,
    pub modes: [Mode; MODE_COUNT],
}

impl Replicate {
    pub fn rows(&self) -> usize {
        if self.columns.is_empty() {
            0
        } else {
            self.values.len() / self.columns.len()
        }
    }

    pub fn column(&self, name: &str) -> Option<usize> {
        self.columns.iter().position(|c| c == name)
    }

    fn get(&self, row: usize, column: usize) -> f64 {
        self.values[row * self.columns.len() + column]
    }
}

/// One evidence set, as `[[compose]]` in config.rs declares it (`option` becomes a terminal
/// [`Declaration`] named in `modules`), plus the ESS floor.
#[derive(Debug, Clone)]
pub struct Set {
    pub id: String,
    /// Declaration names, applied together.
    pub modules: Vec<String>,
    /// Alternatives fixed to one option (name -> label): the product is conditional on them.
    pub given: BTreeMap<String, String>,
    /// Prior overrides: name -> one probability per option, in declaration order.
    pub priors: BTreeMap<String, Vec<f64>>,
    /// Largest share of pre-composition weight a factor may leave not computed.
    pub tolerance: f64,
    /// Smallest effective number of parents, per replicate, of a converged product.
    pub ess_floor: f64,
}

impl Set {
    pub fn new(id: &str, modules: &[&str]) -> Self {
        Set {
            id: id.to_string(),
            modules: modules.iter().map(|m| m.to_string()).collect(),
            given: BTreeMap::new(),
            priors: BTreeMap::new(),
            tolerance: DEFAULT_TOLERANCE,
            ess_floor: DEFAULT_ESS_FLOOR,
        }
    }
}

/// Effective sample size over rows, and over parents (children of one hand-off row summed).
#[derive(Debug, Clone, Copy, PartialEq, Serialize)]
pub struct Ess {
    pub rows: f64,
    pub parents: f64,
}

/// How an alternative entered a product.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize)]
pub enum Role {
    /// Summed over its prior, jointly across every module declaring it.
    Marginalised,
    /// Fixed to one option: the product is conditional on it.
    Given(usize),
    /// Each impact uses its parent stratum's option (the run's trajectory-level alternative).
    Trajectory,
}

#[derive(Debug, Clone, Serialize)]
pub struct AlternativeReport {
    pub name: String,
    pub labels: Vec<String>,
    pub prior: Vec<f64>,
    pub role: Role,
    pub declared_by: Vec<String>,
    /// P(option | D), pooled over replicates by the island estimator. None where a declaring
    /// module is not on an absolute scale, or for a trajectory alternative.
    pub posterior: Option<Vec<f64>>,
    /// The same, per replicate.
    pub posterior_per_replicate: Option<Vec<Vec<f64>>>,
}

#[derive(Debug, Clone, Serialize)]
pub struct FactorReport {
    pub name: String,
    pub absolute_scale: bool,
    /// Per replicate: rows this factor did not compute (NaN), and their pre-composition weight.
    pub not_computed_rows: Vec<usize>,
    pub not_computed_weight: Vec<f64>,
    /// Per replicate: ESS of the pre-composition weights times this factor alone.
    pub ess: Vec<Ess>,
}

#[derive(Debug, Clone, Serialize)]
pub struct FamilyReport {
    pub family: usize,
    /// Per replicate: pre-composition and composed mass, and ln(sum w L / sum w) over the
    /// family's rows (NaN where the replicate has none).
    pub base_mass: Vec<f64>,
    pub mass: Vec<f64>,
    pub log_bayes_factor: Vec<f64>,
}

#[derive(Debug, Clone, Serialize)]
pub struct SplitHalf {
    /// Pooled log-evidence increment of each half of the replicates.
    pub log_evidence_increment: [f64; 2],
    /// Per reported alternative: P(option | D) from each half.
    pub alternatives: Vec<(String, [Vec<f64>; 2])>,
    /// Largest difference between the halves in any reported option probability.
    pub max_probability_difference: f64,
}

#[derive(Debug, Clone, PartialEq, Serialize)]
pub enum Status {
    Converged,
    /// Smallest effective number of parents in any replicate, and the floor it fell below.
    Unconverged { ess_parents: f64, floor: f64 },
}

/// One replicate of a product.
#[derive(Debug, Clone, Serialize)]
pub struct ReplicateProduct {
    pub seed: u64,
    /// Row-aligned with the samples; sums to one.
    #[serde(skip)]
    pub weights: Vec<f64>,
    /// Evidence per mode after composition: summary.rs pools these.
    pub modes: [Mode; MODE_COUNT],
    /// ln D_im of this product relative to its base, per mode (NaN for a mode with no rows).
    pub log_evidence_increment: [f64; MODE_COUNT],
    /// ln sum_m prior_m Z_im after composition.
    pub log_evidence: f64,
    /// Rows some factor of this product, or of its base, did not compute.
    pub not_computed_rows: usize,
}

/// A posterior on the impact samples, and exactly what it contains.
#[derive(Debug, Clone, Serialize)]
pub struct Product {
    pub id: String,
    /// Factors in the order applied, starting with [`FILTER`].
    pub contains: Vec<String>,
    /// Sample columns read to make it.
    pub columns: Vec<String>,
    /// Observation IDs it has used.
    pub observations: Vec<String>,
    /// Per descent family first: report pages lead with these.
    pub families: Vec<FamilyReport>,
    pub alternatives: Vec<AlternativeReport>,
    /// Alternatives fixed to one option: every output of this product is conditional on them.
    pub conditional_on: BTreeMap<String, String>,
    /// Pooled log-evidence increment relative to the base (island estimator).
    pub log_evidence_increment: f64,
    pub factors: Vec<FactorReport>,
    /// Per replicate: ESS of the composed weights.
    pub ess: Vec<Ess>,
    pub split_half: Option<SplitHalf>,
    pub status: Status,
    pub replicates: Vec<ReplicateProduct>,
}

impl Product {
    /// The filter posterior on the impact samples: the hand-off weights, nothing composed.
    /// `observations` are those the filter used. Checks that each replicate's weights sum to
    /// one and that each stratum's rows carry its posterior probability.
    pub fn filter(samples: &[Replicate], observations: Vec<String>) -> Result<Product, String> {
        if samples.is_empty() {
            return Err("no replicates".into());
        }
        if let Some(o) = observations.iter().enumerate().find(|(k, o)| observations[..*k].contains(o)) {
            return Err(format!("the filter lists observation {} twice", o.1));
        }
        let prior: [f64; MODE_COUNT] = std::array::from_fn(|m| samples[0].modes[m].prior_weight);
        let mut replicates = Vec::new();
        for s in samples {
            let seed = s.seed;
            if s.columns.is_empty() || s.values.len() % s.columns.len() != 0 || s.rows() == 0 {
                return Err(format!("replicate seed {seed}: no rows, or values not a whole number of rows"));
            }
            if (0..MODE_COUNT).any(|m| s.modes[m].prior_weight != prior[m]) {
                return Err(format!("replicate seed {seed}: mode prior weights differ from the first replicate's"));
            }
            let wc = s.column(WEIGHT).ok_or_else(|| format!("replicate seed {seed}: no {WEIGHT} column"))?;
            let mc = s.column(STRATUM).ok_or_else(|| format!("replicate seed {seed}: no {STRATUM} column (the stratum)"))?;
            let mut weights: Vec<f64> = (0..s.rows()).map(|r| s.get(r, wc)).collect();
            if let Some(r) = weights.iter().position(|w| !(w.is_finite() && *w >= 0.0)) {
                return Err(format!("replicate seed {seed}: row {r} has weight {}", weights[r]));
            }
            let total: f64 = weights.iter().sum();
            if !(total > 0.0) || (total - 1.0).abs() > 1e-6 {
                return Err(format!("replicate seed {seed}: weights sum to {total}, not 1"));
            }
            weights.iter_mut().for_each(|w| *w /= total);
            let mut mass = [0.0; MODE_COUNT];
            for (r, w) in weights.iter().enumerate() {
                mass[stratum(s, r, mc)?] += w;
            }
            for m in 0..MODE_COUNT {
                if (mass[m] - s.modes[m].posterior_probability).abs() > 1e-6 {
                    return Err(format!(
                        "replicate seed {seed}: the rows of stratum {} carry {}, but the filter gives it posterior probability {}",
                        MODES[m], mass[m], s.modes[m].posterior_probability
                    ));
                }
            }
            let ln_z: Vec<f64> = (0..MODE_COUNT).filter(|&m| prior[m] > 0.0).map(|m| prior[m].ln() + s.modes[m].log_evidence).collect();
            replicates.push(ReplicateProduct {
                seed,
                weights,
                modes: s.modes,
                log_evidence_increment: [0.0; MODE_COUNT],
                log_evidence: log_sum(ln_z),
                not_computed_rows: 0,
            });
        }
        let ess = samples.iter().zip(&replicates).map(|(s, r)| ess(&r.weights, s)).collect();
        Ok(Product {
            id: FILTER.to_string(),
            contains: vec![FILTER.to_string()],
            columns: Vec::new(),
            observations,
            alternatives: Vec::new(),
            conditional_on: BTreeMap::new(),
            log_evidence_increment: 0.0,
            factors: Vec::new(),
            ess,
            families: Vec::new(),
            split_half: None,
            status: Status::Converged,
            replicates,
        })
    }

    /// Weighted mean and standard deviation of a sample column, per replicate.
    pub fn moments(&self, samples: &[Replicate], column: &str) -> Result<Vec<(f64, f64)>, String> {
        aligned(self, samples)?;
        samples
            .iter()
            .zip(&self.replicates)
            .map(|(s, r)| {
                let c = s.column(column).ok_or_else(|| format!("replicate seed {}: no column {column}", s.seed))?;
                let used = || r.weights.iter().enumerate().filter(|(_, w)| **w > 0.0).map(|(k, w)| (*w, s.get(k, c)));
                if used().any(|(_, x)| !x.is_finite()) {
                    return Err(format!("replicate seed {}: {column} is not finite on a weighted row", s.seed));
                }
                let mean: f64 = used().map(|(w, x)| w * x).sum();
                let variance: f64 = used().map(|(w, x)| w * (x - mean).powi(2)).sum();
                Ok((mean, variance.sqrt()))
            })
            .collect()
    }
}

/// The stratum of row `r`: a whole number below [`MODE_COUNT`].
fn stratum(s: &Replicate, r: usize, column: usize) -> Result<usize, String> {
    let v = s.get(r, column);
    if v >= 0.0 && v.fract() == 0.0 && (v as usize) < MODE_COUNT {
        Ok(v as usize)
    } else {
        Err(format!("replicate seed {}: row {r} has stratum {v}", s.seed))
    }
}

fn aligned(base: &Product, samples: &[Replicate]) -> Result<(), String> {
    if samples.len() != base.replicates.len() {
        return Err(format!("{} replicates of samples, but the product has {}", samples.len(), base.replicates.len()));
    }
    for (s, r) in samples.iter().zip(&base.replicates) {
        if s.seed != r.seed || s.rows() != r.weights.len() {
            return Err(format!("samples (seed {}, {} rows) do not match the product (seed {}, {} rows)", s.seed, s.rows(), r.seed, r.weights.len()));
        }
    }
    Ok(())
}

fn log_add(a: f64, b: f64) -> f64 {
    if a == f64::NEG_INFINITY {
        return b;
    }
    if b == f64::NEG_INFINITY {
        return a;
    }
    let m = a.max(b);
    m + ((a - m).exp() + (b - m).exp()).ln()
}

fn log_sum(values: impl IntoIterator<Item = f64>) -> f64 {
    let values: Vec<f64> = values.into_iter().collect();
    let max = values.iter().copied().fold(f64::NEG_INFINITY, f64::max);
    if max == f64::NEG_INFINITY || max.is_nan() {
        return max;
    }
    max + values.iter().map(|v| (v - max).exp()).sum::<f64>().ln()
}

/// ln sum_m prior_m mean_i exp(log_z[i][m]): the evidence of replicates pooled as one sampler,
/// as summary.rs `pooling()` pools them.
fn island(prior: &[f64; MODE_COUNT], log_z: &[[f64; MODE_COUNT]]) -> f64 {
    let max = log_z.iter().flatten().copied().fold(f64::NEG_INFINITY, f64::max);
    if max == f64::NEG_INFINITY {
        return max;
    }
    let total: f64 = (0..MODE_COUNT)
        .filter(|&m| prior[m] > 0.0)
        .map(|m| prior[m] * log_z.iter().map(|row| (row[m] - max).exp()).sum::<f64>() / log_z.len() as f64)
        .sum();
    max + total.ln()
}

/// ESS of row weights, over rows and over parents (rows of one hand-off row summed).
fn ess(weights: &[f64], s: &Replicate) -> Ess {
    let total: f64 = weights.iter().sum();
    let rows = total * total / weights.iter().map(|w| w * w).sum::<f64>();
    let parents = match s.column(PARENT) {
        None => rows,
        Some(pc) => {
            let mut by_parent = HashMap::<u64, f64>::new();
            for (r, w) in weights.iter().enumerate() {
                if *w > 0.0 {
                    *by_parent.entry(s.get(r, pc).to_bits()).or_default() += w;
                }
            }
            total * total / by_parent.values().map(|w| w * w).sum::<f64>()
        }
    };
    Ess { rows, parents }
}

/// One alternative of a set, across the factors declaring it.
struct Shared {
    name: String,
    labels: Vec<String>,
    prior: Vec<f64>,
    declared_by: Vec<usize>,
    absolute: bool,
    role: Role,
}

fn check_priors(what: &str, labels: &[String], prior: &[f64]) -> Result<(), String> {
    if labels.is_empty() || prior.len() != labels.len() {
        return Err(format!("{what}: {} priors for {} options", prior.len(), labels.len()));
    }
    if let Some(l) = labels.iter().enumerate().find(|(k, l)| labels[..*k].contains(l)) {
        return Err(format!("{what}: option {} appears twice", l.1));
    }
    let total: f64 = prior.iter().sum();
    if !prior.iter().all(|p| p.is_finite() && *p > 0.0) || (total - 1.0).abs() > 1e-6 {
        return Err(format!("{what}: priors {prior:?} must be positive and sum to one"));
    }
    Ok(())
}

/// Per-replicate results of one composition, kept for pooling.
struct Pass {
    product: ReplicateProduct,
    factors: Vec<(usize, f64, Ess)>,
    /// ln Z_im before, and ln D_im and ln D_imc (per combination) of this composition.
    log_z: [f64; MODE_COUNT],
    ln_d: [f64; MODE_COUNT],
    ln_dc: Vec<[f64; MODE_COUNT]>,
    ess: Ess,
    /// family -> (base mass, composed mass, ln Bayes factor), relative to the base.
    families: BTreeMap<usize, (f64, f64, f64)>,
    reportable: bool,
}

/// Compose the set's factors onto `base`. `trajectory_alternative` names the run's
/// trajectory-level alternative, if it has one.
pub fn compose(base: &Product, samples: &[Replicate], declarations: &[Declaration], set: &Set, trajectory_alternative: Option<&str>) -> Result<Product, String> {
    compose_checked(base, samples, declarations, set, trajectory_alternative).map_err(|e| format!("evidence set {}: {e}", set.id))
}

fn compose_checked(base: &Product, samples: &[Replicate], declarations: &[Declaration], set: &Set, trajectory_alternative: Option<&str>) -> Result<Product, String> {
    aligned(base, samples)?;
    if set.modules.is_empty() {
        return Err("names no modules".into());
    }
    // Each factor once, and never one the base already contains.
    let mut factors: Vec<&Declaration> = Vec::new();
    for name in &set.modules {
        if factors.iter().any(|f| f.name == *name) {
            return Err(format!("{name} is named twice; a factor is applied once"));
        }
        if base.contains.contains(name) {
            return Err(format!("{name} is already in the base product ({}); a factor is never applied twice", base.contains.join(" + ")));
        }
        factors.push(declarations.iter().find(|d| d.name == *name).ok_or_else(|| format!("no declaration for module {name}"))?);
    }
    // Each observation once, across the base and the factors.
    let base_owner = format!("the base product ({})", base.contains.join(" + "));
    let mut owners: Vec<(&str, &str)> = base.observations.iter().map(|o| (o.as_str(), base_owner.as_str())).collect();
    for f in &factors {
        for o in &f.observations {
            if let Some((_, who)) = owners.iter().find(|(id, _)| id == o) {
                return Err(format!("observation {o} is used by both {who} and {}; each observation is used once", f.name));
            }
            owners.push((o.as_str(), f.name.as_str()));
        }
    }

    // Alternatives, aligned by name across the factors.
    let mut shared: Vec<Shared> = Vec::new();
    let mut uses: Vec<Vec<usize>> = Vec::new();
    for (k, f) in factors.iter().enumerate() {
        let mut used = Vec::new();
        for a in &f.alternatives {
            let labels: Vec<String> = a.options.iter().map(|o| o.0.clone()).collect();
            let prior: Vec<f64> = a.options.iter().map(|o| o.1).collect();
            check_priors(&format!("{}: alternative {}", f.name, a.name), &labels, &prior)?;
            match shared.iter().position(|s| s.name == a.name) {
                Some(j) => {
                    let s = &mut shared[j];
                    if s.declared_by.contains(&k) {
                        return Err(format!("{} declares alternative {} twice", f.name, a.name));
                    }
                    let first = factors[s.declared_by[0]].name.as_str();
                    if s.labels != labels {
                        return Err(format!(
                            "alternative {} has options {:?} in {first} but {:?} in {}; a shared name must mean the same options",
                            a.name, s.labels, labels, f.name
                        ));
                    }
                    if s.prior.iter().zip(&prior).any(|(p, q)| (p - q).abs() > 1e-12) && !set.priors.contains_key(&a.name) {
                        return Err(format!(
                            "alternative {} has priors {:?} in {first} but {:?} in {}; give one prior in the set's priors",
                            a.name, s.prior, prior, f.name
                        ));
                    }
                    s.declared_by.push(k);
                    s.absolute &= f.absolute_scale;
                    used.push(j);
                }
                None => {
                    shared.push(Shared { name: a.name.clone(), labels, prior, declared_by: vec![k], absolute: f.absolute_scale, role: Role::Marginalised });
                    used.push(shared.len() - 1);
                }
            }
        }
        uses.push(used);
    }
    for s in &mut shared {
        if Some(s.name.as_str()) == trajectory_alternative {
            s.role = Role::Trajectory;
        }
    }
    for (name, prior) in &set.priors {
        let s = shared.iter_mut().find(|s| s.name == *name).ok_or_else(|| format!("priors: {name} is not an alternative of this set's modules"))?;
        if s.role == Role::Trajectory {
            return Err(format!("priors: {name} is the trajectory alternative; its prior belongs to the filter"));
        }
        check_priors(&format!("priors for {name}"), &s.labels, prior)?;
        s.prior = prior.clone();
    }
    for (name, label) in &set.given {
        let s = shared.iter_mut().find(|s| s.name == *name).ok_or_else(|| format!("given: {name} is not an alternative of this set's modules"))?;
        if s.role == Role::Trajectory {
            return Err(format!("given: {name} is the trajectory alternative; condition on it with a run of that stratum"));
        }
        let o = s.labels.iter().position(|l| l == label).ok_or_else(|| format!("given: {name} has no option {label}"))?;
        s.role = Role::Given(o);
    }
    // An alternative already settled in the base can only be conditioned on the same way again.
    for s in &shared {
        let Some(b) = base.alternatives.iter().find(|b| b.name == s.name) else { continue };
        match (b.role, s.role) {
            (Role::Marginalised, _) => {
                return Err(format!(
                    "alternative {} was marginalised in the base product over {}; modules sharing an alternative are composed in one set, or the marginalisation is not joint",
                    s.name,
                    b.declared_by.join(", ")
                ))
            }
            (Role::Given(o), Role::Given(p)) if o == p && b.labels == s.labels => {}
            (Role::Trajectory, Role::Trajectory) => {}
            (Role::Given(o), _) => return Err(format!("the base product is conditional on {} = {}; give the same option", s.name, b.labels[o])),
            _ => return Err(format!("alternative {} enters the base product and this set in different roles", s.name)),
        }
    }
    // Rule 1: only absolute-scale likelihoods are mixed across options.
    for (k, f) in factors.iter().enumerate() {
        if f.absolute_scale {
            continue;
        }
        if let Some(&j) = uses[k].iter().find(|&&j| !matches!(shared[j].role, Role::Given(_))) {
            return Err(format!(
                "{} is not on an absolute scale, so it may be composed only within a single option of {}: fix it with given",
                f.name, shared[j].name
            ));
        }
    }

    // Combinations of the enumerated (not trajectory) alternatives, the first varying slowest.
    let enumerated: Vec<usize> = (0..shared.len()).filter(|&j| shared[j].role != Role::Trajectory).collect();
    let position: Vec<Option<usize>> = (0..shared.len()).map(|j| enumerated.iter().position(|&e| e == j)).collect();
    let count = enumerated.iter().try_fold(1usize, |n, &j| n.checked_mul(shared[j].labels.len())).filter(|&n| n <= 4096);
    let count = count.ok_or("more than 4096 combinations of alternatives")?;
    let combos: Vec<Vec<usize>> = (0..count)
        .map(|mut k| {
            let mut c = vec![0; enumerated.len()];
            for d in (0..enumerated.len()).rev() {
                let n = shared[enumerated[d]].labels.len();
                c[d] = k % n;
                k /= n;
            }
            c
        })
        .collect();
    let ln_prior: Vec<f64> = combos.iter().map(|c| c.iter().enumerate().map(|(d, &o)| shared[enumerated[d]].prior[o].ln()).sum()).collect();
    // Consistent with every given option, or with every given option except alternative g's.
    let consistent_except = |c: &[usize], skip: Option<usize>| {
        enumerated.iter().enumerate().all(|(d, &j)| Some(j) == skip || !matches!(shared[j].role, Role::Given(o) if o != c[d]))
    };
    let consistent: Vec<bool> = combos.iter().map(|c| consistent_except(c, None)).collect();
    let ln_norm = log_sum((0..count).filter(|&c| consistent[c]).map(|c| ln_prior[c]));
    let ln_conditional: Vec<f64> = (0..count).map(|c| if consistent[c] { ln_prior[c] - ln_norm } else { f64::NEG_INFINITY }).collect();
    let trajectory = shared.iter().position(|s| s.role == Role::Trajectory);
    let options = trajectory.map_or(1, |j| shared[j].labels.len());
    let column_name = |k: usize, c: &[usize], t: usize| {
        let labels: Vec<&str> = uses[k]
            .iter()
            .map(|&j| shared[j].labels[if shared[j].role == Role::Trajectory { t } else { c[position[j].unwrap()] }].as_str())
            .collect();
        factors[k].column(&labels)
    };
    let mut columns = base.columns.clone();
    for k in 0..factors.len() {
        for c in (0..count).filter(|&c| consistent[c]) {
            for t in 0..options {
                let name = column_name(k, &combos[c], t);
                if !columns.contains(&name) {
                    columns.push(name);
                }
            }
        }
    }

    let prior: [f64; MODE_COUNT] = std::array::from_fn(|m| samples[0].modes[m].prior_weight);
    let mut passes = Vec::new();
    for (s, b) in samples.iter().zip(&base.replicates) {
        passes.push(compose_replicate(s, b, set, &factors, &combos, &consistent, &ln_conditional, trajectory, options, &column_name)?);
    }

    // Pooled over replicates, as summary.rs pools: evidence, and P(option | D).
    let composed_z = |p: &Pass, d: &[f64; MODE_COUNT]| -> [f64; MODE_COUNT] {
        std::array::from_fn(|m| if d[m].is_nan() { f64::NEG_INFINITY } else { p.log_z[m] + d[m] })
    };
    let increment = |which: &[&Pass]| {
        let after: Vec<[f64; MODE_COUNT]> = which.iter().map(|p| composed_z(p, &p.ln_d)).collect();
        let before: Vec<[f64; MODE_COUNT]> = which.iter().map(|p| p.log_z).collect();
        island(&prior, &after) - island(&prior, &before)
    };
    let reportable = passes.iter().all(|p| p.reportable);
    // ln Z_c over a subset of replicates, then per alternative the posterior of its options.
    let posteriors = |which: &[&Pass]| -> Vec<Option<Vec<f64>>> {
        let ln_z: Vec<f64> = (0..count)
            .map(|c| ln_prior[c] + island(&prior, &which.iter().map(|p| composed_z(p, &p.ln_dc[c])).collect::<Vec<_>>()))
            .collect();
        shared
            .iter()
            .enumerate()
            .map(|(j, s)| {
                let skip = match s.role {
                    Role::Trajectory => return None,
                    Role::Given(_) if !(s.absolute && reportable) => return None,
                    Role::Given(_) => Some(j),
                    Role::Marginalised => None,
                };
                let d = position[j].unwrap();
                let mut mass = vec![f64::NEG_INFINITY; s.labels.len()];
                for c in (0..count).filter(|&c| consistent_except(&combos[c], skip)) {
                    mass[combos[c][d]] = log_add(mass[combos[c][d]], ln_z[c]);
                }
                let total = log_sum(mass.clone());
                Some(mass.iter().map(|v| (v - total).exp()).collect())
            })
            .collect()
    };
    let all: Vec<&Pass> = passes.iter().collect();
    let pooled = posteriors(&all);
    let per_replicate: Vec<Vec<Option<Vec<f64>>>> = passes.iter().map(|p| posteriors(&[p])).collect();
    let split_half = (passes.len() >= 2).then(|| {
        let half = passes.len() / 2;
        let (first, second) = (&all[..half], &all[half..]);
        let (a, b) = (posteriors(first), posteriors(second));
        let alternatives: Vec<(String, [Vec<f64>; 2])> = shared
            .iter()
            .enumerate()
            .filter_map(|(j, s)| Some((s.name.clone(), [a[j].clone()?, b[j].clone()?])))
            .collect();
        let max_probability_difference = alternatives.iter().flat_map(|(_, [x, y])| x.iter().zip(y).map(|(p, q)| (p - q).abs())).fold(0.0, f64::max);
        SplitHalf { log_evidence_increment: [increment(first), increment(second)], alternatives, max_probability_difference }
    });

    let mut alternatives = base.alternatives.clone();
    for (j, s) in shared.iter().enumerate() {
        if alternatives.iter().any(|a| a.name == s.name) {
            continue;
        }
        alternatives.push(AlternativeReport {
            name: s.name.clone(),
            labels: s.labels.clone(),
            prior: s.prior.clone(),
            role: s.role,
            declared_by: s.declared_by.iter().map(|&k| factors[k].name.clone()).collect(),
            posterior: pooled[j].clone(),
            posterior_per_replicate: per_replicate.iter().map(|p| p[j].clone()).collect(),
        });
    }
    let mut conditional_on = base.conditional_on.clone();
    conditional_on.extend(set.given.clone());
    let mut reports = base.factors.clone();
    for (k, f) in factors.iter().enumerate() {
        reports.push(FactorReport {
            name: f.name.clone(),
            absolute_scale: f.absolute_scale,
            not_computed_rows: passes.iter().map(|p| p.factors[k].0).collect(),
            not_computed_weight: passes.iter().map(|p| p.factors[k].1).collect(),
            ess: passes.iter().map(|p| p.factors[k].2).collect(),
        });
    }
    // Families, chained to the filter: masses from the first composition, Bayes factors added.
    let family_ids: Vec<usize> = passes.iter().flat_map(|p| p.families.keys().copied()).collect::<std::collections::BTreeSet<_>>().into_iter().collect();
    let families = family_ids
        .into_iter()
        .map(|family| {
            let earlier = base.families.iter().find(|f| f.family == family);
            let at = |i: usize, k: usize| passes[i].families.get(&family).map_or(f64::NAN, |v| [v.0, v.1, v.2][k]);
            let n = passes.len();
            FamilyReport {
                family,
                base_mass: (0..n).map(|i| earlier.map_or(at(i, 0), |e| e.base_mass[i])).collect(),
                mass: (0..n).map(|i| at(i, 1)).collect(),
                log_bayes_factor: (0..n).map(|i| at(i, 2) + earlier.map_or(0.0, |e| e.log_bayes_factor[i])).collect(),
            }
        })
        .collect();
    let ess: Vec<Ess> = passes.iter().map(|p| p.ess).collect();
    let least = ess.iter().map(|e| e.parents).fold(f64::INFINITY, f64::min);
    let status = if least < set.ess_floor { Status::Unconverged { ess_parents: least, floor: set.ess_floor } } else { Status::Converged };
    Ok(Product {
        id: set.id.clone(),
        contains: base.contains.iter().cloned().chain(factors.iter().map(|f| f.name.clone())).collect(),
        columns,
        observations: owners.iter().map(|(o, _)| o.to_string()).collect(),
        alternatives,
        conditional_on,
        log_evidence_increment: increment(&all),
        factors: reports,
        ess,
        families,
        split_half,
        status,
        replicates: passes.into_iter().map(|p| p.product).collect(),
    })
}

/// One replicate: the per-row joint likelihood, the per-(mode) and per-(mode, combination)
/// evidence increments, the NaN accounting and the composed weights.
#[allow(clippy::too_many_arguments)]
fn compose_replicate(
    s: &Replicate,
    b: &ReplicateProduct,
    set: &Set,
    factors: &[&Declaration],
    combos: &[Vec<usize>],
    consistent: &[bool],
    ln_conditional: &[f64],
    trajectory: Option<usize>,
    options: usize,
    column_name: &dyn Fn(usize, &[usize], usize) -> String,
) -> Result<Pass, String> {
    let seed = s.seed;
    let (nf, nc, rows) = (factors.len(), combos.len(), s.rows());
    let find = |name: &str| s.column(name).ok_or_else(|| format!("replicate seed {seed}: the samples have no column {name}"));
    // index[k][c][t]: the column of factor k under combination c and trajectory option t.
    let mut index = vec![vec![vec![0usize; options]; nc]; nf];
    for (k, by_combo) in index.iter_mut().enumerate() {
        for (c, by_option) in by_combo.iter_mut().enumerate() {
            for (t, slot) in by_option.iter_mut().enumerate() {
                *slot = find(&column_name(k, &combos[c], t))?;
            }
        }
    }
    let mc = find(STRATUM)?;
    let tc = trajectory.map(|_| find(TRAJECTORY_OPTION)).transpose()?;
    let fc = s.column(FAMILY);

    let mut values = vec![0.0; nf * nc];
    let mut joint = vec![0.0; nc];
    // ln L_r of each computed row; NaN for a row some factor did not compute.
    let mut row_ln_l = vec![f64::NAN; rows];
    let mut factor_ln_l = vec![vec![f64::NAN; rows]; nf];
    let mut mass = [0.0; MODE_COUNT];
    let mut shift = [f64::NEG_INFINITY; MODE_COUNT];
    let mut den = [0.0; MODE_COUNT];
    let mut num_c = vec![[f64::NEG_INFINITY; MODE_COUNT]; nc];
    let mut not_computed = vec![(0usize, 0.0f64); nf];
    let mut reportable = true;
    for r in 0..rows {
        let w = b.weights[r];
        let m = stratum(s, r, mc)?;
        mass[m] += w;
        let t = match tc {
            None => 0,
            Some(tc) => {
                let v = s.get(r, tc);
                if !(v >= 0.0 && v.fract() == 0.0 && (v as usize) < options) {
                    return Err(format!("replicate seed {seed}: row {r} has trajectory option {v}"));
                }
                v as usize
            }
        };
        let mut computed = true;
        for k in 0..nf {
            let mut missing = false;
            for c in 0..nc {
                let v = s.get(r, index[k][c][t]);
                if v == f64::INFINITY {
                    return Err(format!("{} returned +inf at replicate seed {seed}, row {r}", factors[k].name));
                }
                if v.is_nan() {
                    if consistent[c] {
                        missing = true;
                    } else {
                        reportable = false;
                    }
                }
                values[k * nc + c] = v;
            }
            if missing {
                computed = false;
                not_computed[k].0 += 1;
                not_computed[k].1 += w;
            } else {
                factor_ln_l[k][r] = log_sum((0..nc).filter(|&c| consistent[c]).map(|c| ln_conditional[c] + values[k * nc + c]));
            }
        }
        if !computed {
            continue;
        }
        for (c, j) in joint.iter_mut().enumerate() {
            *j = (0..nf).map(|k| values[k * nc + c]).sum();
        }
        let ln_l = log_sum((0..nc).filter(|&c| consistent[c]).map(|c| ln_conditional[c] + joint[c]));
        row_ln_l[r] = ln_l;
        if w > 0.0 {
            shift[m] = shift[m].max(ln_l);
            den[m] += w;
            let lw = w.ln();
            for c in 0..nc {
                num_c[c][m] = log_add(num_c[c][m], lw + joint[c]);
            }
        }
    }
    // Sums in linear space, shifted per mode by its largest ln L, so that a factor that is 0.0
    // everywhere gives exactly D = 1 and leaves the weights bit for bit unchanged.
    let mut num = [0.0; MODE_COUNT];
    for r in 0..rows {
        let w = b.weights[r];
        if w > 0.0 && !row_ln_l[r].is_nan() {
            let m = s.get(r, mc) as usize;
            num[m] += w * (row_ln_l[r] - shift[m]).exp();
        }
    }

    let total: f64 = mass.iter().sum();
    for (k, (count, weight)) in not_computed.iter_mut().enumerate() {
        *weight /= total;
        if *weight > set.tolerance {
            return Err(format!(
                "{} is not computed (NaN) on {count} samples of replicate seed {seed}, carrying {weight} of the pre-composition posterior, above the set's tolerance {}; refused",
                factors[k].name, set.tolerance
            ));
        }
    }
    let mut ln_d = [f64::NAN; MODE_COUNT];
    for m in 0..MODE_COUNT {
        if mass[m] <= 0.0 {
            if b.modes[m].prior_weight > 0.0 && b.modes[m].log_evidence.is_finite() {
                return Err(format!("replicate seed {seed}: stratum {} has evidence but no weighted impact samples", MODES[m]));
            }
            continue;
        }
        if den[m] <= 0.0 {
            return Err(format!("replicate seed {seed}: every sample of stratum {} is not computed", MODES[m]));
        }
        ln_d[m] = if shift[m] == f64::NEG_INFINITY { f64::NEG_INFINITY } else { shift[m] + (num[m] / den[m]).ln() };
    }
    // Normalise against the base's own total, so that D = 1 everywhere changes nothing.
    let top = (0..MODE_COUNT).filter(|&m| mass[m] > 0.0).map(|m| ln_d[m]).fold(f64::NEG_INFINITY, f64::max);
    if top == f64::NEG_INFINITY {
        return Err(format!("the data are impossible under every sample of replicate seed {seed}"));
    }
    let carried: [f64; MODE_COUNT] = std::array::from_fn(|m| if mass[m] > 0.0 { mass[m] * (ln_d[m] - top).exp() } else { 0.0 });
    let ratio = carried.iter().sum::<f64>() / total;
    let ln_total = top + ratio.ln();
    let weights: Vec<f64> = (0..rows)
        .map(|r| {
            let w = b.weights[r];
            if w == 0.0 {
                return 0.0;
            }
            let ln_l = if row_ln_l[r].is_nan() { ln_d[s.get(r, mc) as usize] } else { row_ln_l[r] };
            w * (ln_l - top).exp() / ratio
        })
        .collect();
    let carried_total: f64 = carried.iter().sum();
    let modes: [Mode; MODE_COUNT] = std::array::from_fn(|m| {
        let before = b.modes[m];
        if mass[m] <= 0.0 {
            return Mode { posterior_probability: 0.0, ..before };
        }
        Mode { prior_weight: before.prior_weight, log_evidence: before.log_evidence + ln_d[m], posterior_probability: carried[m] / carried_total }
    });
    let ln_dc: Vec<[f64; MODE_COUNT]> = num_c.iter().map(|n| std::array::from_fn(|m| if mass[m] > 0.0 { n[m] - den[m].ln() } else { f64::NAN })).collect();

    let mut families = BTreeMap::new();
    if let Some(fc) = fc {
        let mut sums = BTreeMap::<usize, (f64, f64)>::new();
        for r in 0..rows {
            let v = s.get(r, fc);
            if !(v >= 0.0 && v.fract() == 0.0) {
                return Err(format!("replicate seed {seed}: row {r} has family {v}"));
            }
            let e = sums.entry(v as usize).or_default();
            e.0 += b.weights[r];
            e.1 += weights[r];
        }
        for (family, (before, after)) in sums {
            families.insert(family, (before, after, after.ln() + ln_total - before.ln()));
        }
    }
    let factors_out = (0..nf)
        .map(|k| {
            let ln_l = &factor_ln_l[k];
            let max = ln_l.iter().copied().filter(|v| !v.is_nan()).fold(f64::NEG_INFINITY, f64::max);
            let w: Vec<f64> = (0..rows).map(|r| if ln_l[r].is_nan() || b.weights[r] == 0.0 { 0.0 } else { b.weights[r] * (ln_l[r] - max).exp() }).collect();
            (not_computed[k].0, not_computed[k].1, ess(&w, s))
        })
        .collect();
    let not_computed_rows = b.not_computed_rows + row_ln_l.iter().filter(|v| v.is_nan()).count();
    let prior_ln_z: [f64; MODE_COUNT] = std::array::from_fn(|m| b.modes[m].log_evidence);
    let composed_ess = ess(&weights, s);
    let product = ReplicateProduct { seed, weights, modes, log_evidence_increment: ln_d, log_evidence: b.log_evidence + ln_total, not_computed_rows };
    Ok(Pass { ess: composed_ess, product, factors: factors_out, log_z: prior_ln_z, ln_d, ln_dc, families, reportable })
}

#[cfg(test)]
mod tests;
