//! Integration layer for the September 29 fuel experiment.
//!
//! This deliberately wraps the frozen September 28 flight dynamics rather than
//! modifying them.  When fuel is disabled, `advance` calls `Aircraft::propagate`
//! exactly once with the original arguments and performs no RNG draws.  That makes
//! the existing fixed-seed estimator the regression oracle.

use flight::{Aircraft, Parameters};
use flight::environment::Environment;
use rand::Rng;

use crate::fuel::{FuelFlowModel, FuelState};

#[derive(Debug, Clone)]
pub enum FuelMode {
    Off,
    On(FuelState),
}

#[derive(Debug, Clone)]
pub struct FuelledAircraft {
    pub aircraft: Aircraft,
    pub fuel: FuelMode,
    /// Zero-fuel mass plus payload/crew/etc. held fixed for the experiment.
    pub non_fuel_mass_kg: f64,
}

impl FuelledAircraft {
    pub fn off(aircraft: Aircraft) -> Self {
        Self { aircraft, fuel: FuelMode::Off, non_fuel_mass_kg: 0.0 }
    }

    pub fn on(aircraft: Aircraft, fuel: FuelState, non_fuel_mass_kg: f64) -> Self {
        assert!(non_fuel_mass_kg > 0.0);
        Self { aircraft, fuel: FuelMode::On(fuel), non_fuel_mass_kg }
    }

    /// Propagate to `to_unix_s`.  The OFF branch is intentionally the historical
    /// propagation call, with no additional RNG use or state mutation.
    ///
    /// The ON branch currently advances fuel over the same outer interval using
    /// the aircraft state at the start of the interval.  Before scientific runs,
    /// this hook must move inside the 5/10 s flight integration loop so Mach,
    /// altitude, temperature and gross weight are evaluated each kinematic step.
    pub fn advance<R: Rng, E: Environment, F: FuelFlowModel>(
        &mut self,
        to_unix_s: f64,
        params: &Parameters,
        env: &E,
        flow: &F,
        rng: &mut R,
    ) {
        match &mut self.fuel {
            FuelMode::Off => self.aircraft.propagate(to_unix_s, params, env, rng),
            FuelMode::On(fuel) => {
                let from = self.aircraft.unix_s;
                let dt = (to_unix_s - from).max(0.0);
                let air = self.aircraft.air_data();
                let gross = self.non_fuel_mass_kg + fuel.remaining_kg;
                let nominal = flow.flow_kg_h(
                    self.aircraft.mach,
                    self.aircraft.alt_ft,
                    gross,
                    air.temperature_k,
                );
                fuel.advance(from, dt, nominal);
                self.aircraft.propagate(to_unix_s, params, env, rng);
            }
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::fuel::SyntheticFuelFlow;
    use flight::environment::CalmAir;
    use flight::{Mode, Prior};
    use rand::SeedableRng;
    use rand_chacha::ChaCha8Rng;

    fn prior(p: &Parameters) -> Prior {
        Prior {
            unix_s: 1_000.0,
            lat: 6.0,
            lon: 96.0,
            position_sd_nm: 0.0,
            track_deg: 180.0,
            track_sd_deg: 0.0,
            mach_range: (0.80, 0.81),
            mach_gaussian: None,
            altitude_levels: Prior::uniform_altitude_levels(p),
        }
    }

    #[test]
    fn fuel_off_is_bit_for_bit_the_historical_propagation() {
        let p = Parameters::default();
        let env = CalmAir;
        let mut init_rng = ChaCha8Rng::seed_from_u64(1234);
        let a = Aircraft::sample(&prior(&p), Mode::TrueTrack, &p, &env, &mut init_rng);
        let mut historical = a.clone();
        let mut wrapped = FuelledAircraft::off(a);
        let mut r1 = ChaCha8Rng::seed_from_u64(9876);
        let mut r2 = ChaCha8Rng::seed_from_u64(9876);
        let flow = SyntheticFuelFlow { base_kg_h: 5_000.0 };
        historical.propagate(4_600.0, &p, &env, &mut r1);
        wrapped.advance(4_600.0, &p, &env, &flow, &mut r2);
        let x = serde_json::to_vec(&historical).unwrap();
        let y = serde_json::to_vec(&wrapped.aircraft).unwrap();
        assert_eq!(x, y, "fuel-off changed the historical aircraft trajectory");
        assert_eq!(r1.next_u64(), r2.next_u64(), "fuel-off consumed a different RNG sequence");
    }

    #[test]
    fn fuel_on_tracks_burn_without_changing_rng_schedule() {
        let p = Parameters::default();
        let env = CalmAir;
        let mut init_rng = ChaCha8Rng::seed_from_u64(1234);
        let a = Aircraft::sample(&prior(&p), Mode::TrueTrack, &p, &env, &mut init_rng);
        let fuel = FuelState::new(43_800.0, 1.009);
        let mut wrapped = FuelledAircraft::on(a, fuel, 180_000.0);
        let mut rng = ChaCha8Rng::seed_from_u64(9876);
        let flow = SyntheticFuelFlow { base_kg_h: 5_000.0 };
        wrapped.advance(4_600.0, &p, &env, &flow, &mut rng);
        match wrapped.fuel {
            FuelMode::On(f) => assert!(f.remaining_kg < 43_800.0),
            FuelMode::Off => panic!("fuel unexpectedly disabled"),
        }
    }
}
