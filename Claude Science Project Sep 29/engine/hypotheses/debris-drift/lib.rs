//! <Hypothesis name>: <the assumption, its source, and how it enters the estimate>.
//!
//! Only the hooks in `hypothesis::Hypothesis` are available. A trajectory module uses the
//! filter hooks; an impact module (named in a `[[compose]]` set of its run.toml) implements
//! `impact_log_likelihood` and, if it predicts, `prediction_columns` and `predict`. Declare
//! every observation the module uses. Delete the hooks you do not use.

use hypothesis::{EpochView, Hypothesis, ImpactView, PriorSpec, StateView};
use serde::Deserialize;

#[derive(Deserialize)]
#[serde(deny_unknown_fields)]
struct Params {}

struct Template {
    #[allow(dead_code)]
    params: Params,
}

pub fn new(params: &toml::Value) -> Result<Box<dyn Hypothesis>, String> {
    let params: Params = params.clone().try_into().map_err(|e| format!("debris-drift: {e}"))?;
    Ok(Box::new(Template { params }))
}

impl Hypothesis for Template {
    fn observations(&self) -> Vec<String> {
        Vec::new()
    }

    fn adjust_prior(&self, _prior: &mut PriorSpec) {}

    fn epoch_log_likelihood(&self, _epoch: &EpochView, _state: &StateView) -> f64 {
        0.0
    }

    fn final_log_likelihood(&self, _state: &StateView) -> f64 {
        0.0
    }

    fn impact_log_likelihood(&self, _impact: &ImpactView, _choice: &[usize]) -> f64 {
        0.0
    }
}
