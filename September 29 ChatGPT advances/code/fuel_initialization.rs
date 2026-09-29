//! Fuel initialization for the September 29 MH370 working model.
//!
//! Scientific design constraints:
//! - fuel anchor: 43,800 kg at 17:06:43 UTC;
//! - particle fuel-flow multiplier approximately N(1.009, 0.018);
//! - fuel randomness must be independent of every historical flight/filter RNG stream;
//! - enabling/disabling fuel must therefore leave all historical trajectory draws unchanged.
//!
//! The anchor uncertainty is deliberately NOT invented here.  `FuelPrior` accepts an optional
//! anchor SD, but the default scientific configuration keeps the anchor deterministic until its
//! provenance/uncertainty is recovered from the fuel-model source material.

use crate::fuel::FuelState;
use rand::SeedableRng;
use rand_chacha::ChaCha8Rng;
use rand_distr::{Distribution, StandardNormal};

pub const FUEL_ANCHOR_KG: f64 = 43_800.0;
pub const FLOW_FACTOR_MEAN: f64 = 1.009;
pub const FLOW_FACTOR_SD: f64 = 0.018;

/// Domain separator for fuel-only RNG streams.  This is not a filter step number and is never
/// passed to the historical `filter::stream` function.  The independent seeded generator means
/// fuel draws cannot consume or shift aircraft/BFO/resampling random words.
const FUEL_STREAM_DOMAIN: u64 = 0x4655_454c_4d48_3337; // ASCII-ish "FUELMH37"

#[derive(Debug, Clone, Copy, PartialEq)]
pub struct FuelPrior {
    pub anchor_kg: f64,
    pub anchor_sd_kg: Option<f64>,
    pub flow_factor_mean: f64,
    pub flow_factor_sd: f64,
}

impl Default for FuelPrior {
    fn default() -> Self {
        Self {
            anchor_kg: FUEL_ANCHOR_KG,
            anchor_sd_kg: None,
            flow_factor_mean: FLOW_FACTOR_MEAN,
            flow_factor_sd: FLOW_FACTOR_SD,
        }
    }
}

/// SplitMix64 finalizer used only to map case/stratum/particle identity to a fuel stream id.
fn mix64(mut z: u64) -> u64 {
    z = (z ^ (z >> 30)).wrapping_mul(0xbf58_476d_1ce4_e5b9);
    z = (z ^ (z >> 27)).wrapping_mul(0x94d0_49bb_1331_11eb);
    z ^ (z >> 31)
}

/// Fuel-only RNG.  No caller should pass this generator to flight propagation, BFO bias,
/// resampling, route selection, or manoeuvre-rate refresh.
pub fn fuel_rng(seed: u64, stratum: u64, particle: usize) -> ChaCha8Rng {
    let mut rng = ChaCha8Rng::seed_from_u64(seed ^ FUEL_STREAM_DOMAIN);
    let identity = mix64(stratum ^ (particle as u64).rotate_left(32));
    rng.set_stream(identity);
    rng
}

pub fn sample_fuel_state(seed: u64, stratum: u64, particle: usize, prior: FuelPrior) -> FuelState {
    let mut rng = fuel_rng(seed, stratum, particle);
    let z_flow: f64 = StandardNormal.sample(&mut rng);
    let flow_factor = prior.flow_factor_mean + prior.flow_factor_sd * z_flow;
    let remaining_kg = match prior.anchor_sd_kg {
        None => prior.anchor_kg,
        Some(sd) => {
            let z_fuel: f64 = StandardNormal.sample(&mut rng);
            (prior.anchor_kg + sd * z_fuel).max(0.0)
        }
    };
    FuelState::new(remaining_kg, flow_factor)
}

#[cfg(test)]
mod tests {
    use super::*;
    use rand::RngCore;

    #[test]
    fn same_identity_reproduces_exact_fuel_draw() {
        let a = sample_fuel_state(123, 2, 17, FuelPrior::default());
        let b = sample_fuel_state(123, 2, 17, FuelPrior::default());
        assert_eq!(a.remaining_kg.to_bits(), b.remaining_kg.to_bits());
        assert_eq!(a.flow_factor.to_bits(), b.flow_factor.to_bits());
    }

    #[test]
    fn default_anchor_is_exact_until_uncertainty_is_sourced() {
        let a = sample_fuel_state(123, 2, 17, FuelPrior::default());
        assert_eq!(a.remaining_kg.to_bits(), FUEL_ANCHOR_KG.to_bits());
    }

    #[test]
    fn particle_identity_changes_fuel_stream() {
        let a = sample_fuel_state(123, 2, 17, FuelPrior::default());
        let b = sample_fuel_state(123, 2, 18, FuelPrior::default());
        assert_ne!(a.flow_factor.to_bits(), b.flow_factor.to_bits());
    }

    #[test]
    fn fuel_stream_does_not_touch_a_separate_historical_rng() {
        let mut historical = ChaCha8Rng::seed_from_u64(9876);
        historical.set_stream(42);
        let first = historical.next_u64();

        let _fuel = sample_fuel_state(9876, 1, 5, FuelPrior::default());

        let second = historical.next_u64();
        let mut reference = ChaCha8Rng::seed_from_u64(9876);
        reference.set_stream(42);
        assert_eq!(first, reference.next_u64());
        assert_eq!(second, reference.next_u64());
    }
}
