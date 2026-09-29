//! Fuel additions to the 00:11 posterior hand-off.
//!
//! Kept separate from the frozen September 28 handoff implementation.  When integrated into
//! the working crate, `Particle`, `handoff::Candidate` and `handoff::Row` each carry the same
//! `Option<FuelState>`.  Cloning/resampling therefore preserves fuel/trajectory correlation.

use crate::fuel::FuelState;
use serde::{Deserialize, Serialize};

/// Serializable fuel state handed from the pre-00:11 estimator to EOF.
/// `None` is the regression-compatible historical/fuel-disabled case.
#[derive(Debug, Clone, Copy, PartialEq, Serialize, Deserialize)]
pub struct FuelHandoff {
    pub remaining_kg: f64,
    pub flow_factor: f64,
    pub exhausted_unix_s: Option<f64>,
}

impl From<FuelState> for FuelHandoff {
    fn from(f: FuelState) -> Self {
        Self {
            remaining_kg: f.remaining_kg,
            flow_factor: f.flow_factor,
            exhausted_unix_s: f.exhausted_unix_s,
        }
    }
}

impl From<FuelHandoff> for FuelState {
    fn from(f: FuelHandoff) -> Self {
        FuelState {
            remaining_kg: f.remaining_kg,
            flow_factor: f.flow_factor,
            exhausted_unix_s: f.exhausted_unix_s,
        }
    }
}

/// Numeric columns appended only to fuel-enabled diagnostic output.
/// Keeping these out of the historical 13-column `final.npy` when fuel is disabled is the
/// safest route to a byte-identical baseline regression.
pub const FUEL_COLUMNS: [&str; 3] = [
    "fuel_remaining_kg",
    "fuel_flow_factor",
    "fuel_exhausted_unix_s",
];

pub fn diagnostic_row(fuel: Option<FuelState>) -> [f64; 3] {
    match fuel {
        None => [f64::NAN; 3],
        Some(f) => [
            f.remaining_kg,
            f.flow_factor,
            f.exhausted_unix_s.unwrap_or(f64::NAN),
        ],
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn handoff_round_trip_preserves_all_fuel_bits() {
        let f = FuelState {
            remaining_kg: 12_345.678_901,
            flow_factor: 1.009_123,
            exhausted_unix_s: Some(1_417_000_123.456),
        };
        let h = FuelHandoff::from(f);
        let r = FuelState::from(h);
        assert_eq!(r.remaining_kg.to_bits(), f.remaining_kg.to_bits());
        assert_eq!(r.flow_factor.to_bits(), f.flow_factor.to_bits());
        assert_eq!(r.exhausted_unix_s.unwrap().to_bits(), f.exhausted_unix_s.unwrap().to_bits());
    }

    #[test]
    fn disabled_diagnostics_are_nan_and_do_not_require_fake_fuel() {
        assert!(diagnostic_row(None).iter().all(|x| x.is_nan()));
    }
}
