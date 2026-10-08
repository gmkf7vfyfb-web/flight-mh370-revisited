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
    pub alternatives: Vec<AlternativeReport>,
    /// Alternatives fixed to one option: every output of this product is conditional on them.
    pub conditional_on: BTreeMap<String, String>,
    /// Pooled log-evidence increment relative to the base (island estimator).
    pub log_evidence_increment: f64,
    pub factors: Vec<FactorReport>,
    /// Per replicate: ESS of the composed weights.
    pub ess: Vec<Ess>,
    pub families: Vec<FamilyReport>,
    pub split_half: Option<SplitHalf>,
    pub status: Status,
    pub replicates: Vec<ReplicateProduct>,
}

impl Product {
    /// The filter posterior on the impact samples: the hand-off weights, nothing composed.
    /// `observations` are those the filter used. Checks that each replicate's weights sum to
    /// one and that each stratum's rows carry its posterior probability.
    pub fn filter(samples: &[Replicate], observations: Vec<String>) -> Result<Product, String> {
        let _ = (samples, observations);
        unimplemented!()
    }

    /// Weighted mean and standard deviation of a sample column, per replicate.
    pub fn moments(&self, samples: &[Replicate], column: &str) -> Result<Vec<(f64, f64)>, String> {
        let _ = (samples, column);
        unimplemented!()
    }
}

/// Compose the set's factors onto `base`. `trajectory_alternative` names the run's
/// trajectory-level alternative, if it has one.
pub fn compose(base: &Product, samples: &[Replicate], declarations: &[Declaration], set: &Set, trajectory_alternative: Option<&str>) -> Result<Product, String> {
    let _ = (base, samples, declarations, set, trajectory_alternative, HashMap::<u8, u8>::new());
    unimplemented!()
}

#[cfg(test)]
mod tests;
