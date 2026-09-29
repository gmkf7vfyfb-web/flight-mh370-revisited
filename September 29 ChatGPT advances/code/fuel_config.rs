//! Backward-compatible fuel configuration for the September 29 working model.
//!
//! Intended insertion into `mh370::config::Config`:
//!     #[serde(default, skip_serializing_if = "Option::is_none")]
//!     pub fuel: Option<FuelConfig>,
//!
//! Keeping the top-level field optional is important: every historical TOML file that omits
//! `fuel` deserializes exactly as before, and the filter must route `None` through the historical
//! propagation path.  Fuel is therefore opt-in for the A/B experiment.

use serde::{Deserialize, Serialize};

#[derive(Deserialize, Serialize, Clone, Debug, PartialEq)]
#[serde(deny_unknown_fields)]
pub struct FuelConfig {
    /// UTC anchor corresponding to `anchor_kg`; expected scientific value 17:06:43 UTC.
    pub anchor_time_utc: String,
    /// Total fuel at the anchor; current recovered design value 43,800 kg.
    pub anchor_kg: f64,
    /// Optional uncertainty on anchor fuel. Omit until a defensible source value is recovered.
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub anchor_sd_kg: Option<f64>,
    /// Multiplicative fuel-flow correction mean; current design value 1.009.
    pub flow_factor_mean: f64,
    /// Multiplicative fuel-flow correction SD; current design value 0.018.
    pub flow_factor_sd: f64,
    /// Zero-fuel mass is intentionally required when fuel is enabled.  There is no hidden
    /// default because guessing it would contaminate the gross-weight feedback.
    pub zero_fuel_mass_kg: f64,
    /// Extracted Ulich table/model path. The adapter owns parsing/interpolation semantics.
    pub table: std::path::PathBuf,
}

impl FuelConfig {
    pub fn validate(&self) -> Result<(), String> {
        if !(self.anchor_kg >= 0.0 && self.anchor_kg.is_finite()) {
            return Err("fuel.anchor_kg must be finite and non-negative".into());
        }
        if self.anchor_sd_kg.is_some_and(|x| !(x >= 0.0 && x.is_finite())) {
            return Err("fuel.anchor_sd_kg must be finite and non-negative".into());
        }
        if !(self.flow_factor_mean > 0.0 && self.flow_factor_mean.is_finite()) {
            return Err("fuel.flow_factor_mean must be finite and positive".into());
        }
        if !(self.flow_factor_sd >= 0.0 && self.flow_factor_sd.is_finite()) {
            return Err("fuel.flow_factor_sd must be finite and non-negative".into());
        }
        if !(self.zero_fuel_mass_kg > 0.0 && self.zero_fuel_mass_kg.is_finite()) {
            return Err("fuel.zero_fuel_mass_kg must be finite and positive".into());
        }
        Ok(())
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn omitted_optional_anchor_sd_is_valid() {
        let cfg = FuelConfig {
            anchor_time_utc: "2014-03-07T17:06:43Z".into(),
            anchor_kg: 43_800.0,
            anchor_sd_kg: None,
            flow_factor_mean: 1.009,
            flow_factor_sd: 0.018,
            zero_fuel_mass_kg: 150_000.0, // test fixture only; NOT a 9M-MRO scientific value
            table: "test-table.csv".into(),
        };
        assert!(cfg.validate().is_ok());
    }

    #[test]
    fn rejects_nonphysical_values() {
        let mut cfg = FuelConfig {
            anchor_time_utc: "2014-03-07T17:06:43Z".into(),
            anchor_kg: 43_800.0,
            anchor_sd_kg: None,
            flow_factor_mean: 1.009,
            flow_factor_sd: 0.018,
            zero_fuel_mass_kg: 1.0,
            table: "x".into(),
        };
        cfg.flow_factor_mean = 0.0;
        assert!(cfg.validate().is_err());
    }
}
