//! Exact-step fuel integration for the September 29 working model.
//!
//! This module is deliberately written as the minimal patch pattern for `flight::Aircraft`.
//! The frozen September 28 source remains untouched.  The important invariant is that the
//! existing `Aircraft::propagate` body remains the numerical reference when fuel is disabled.
//!
//! Integration rule
//! ----------------
//! Fuel must be advanced *inside* the existing propagation while-loop, after `dt` has been
//! clipped to manoeuvre/event/target times and after any required environment refresh, but
//! before the aircraft state is advanced to the end of the step.  Thus the fuel model sees
//! the state at the beginning of exactly the same 5/10-s step used by the kinematics.
//!
//! The production patch should factor the historical body into a private
//! `propagate_impl(..., fuel: Option<&mut FuelContext>)`; public `propagate` calls it with
//! `None`.  The enabled entry point calls it with `Some`.  The `None` branch MUST contain no
//! RNG calls and must not alter the order of any existing floating-point operation.

use crate::fuel::{FuelFlowModel, FuelState};

/// Non-fuel aircraft mass carried by the fuel model.  This is intentionally supplied by the
/// MH370 case configuration rather than hard-coded here; we must recover/validate the 9M-MRO
/// zero-fuel mass before producing scientific results.
#[derive(Debug, Clone, Copy, PartialEq)]
pub struct MassModel {
    pub zero_fuel_mass_kg: f64,
}

impl MassModel {
    pub fn gross_weight_kg(&self, fuel: &FuelState) -> f64 {
        self.zero_fuel_mass_kg + fuel.remaining_kg
    }
}

/// Mutable fuel state plus the immutable flow/mass models needed for one aircraft.
pub struct FuelContext<'a, F: FuelFlowModel> {
    pub state: &'a mut FuelState,
    pub flow: &'a F,
    pub mass: MassModel,
}

impl<F: FuelFlowModel> FuelContext<'_, F> {
    /// Advance fuel over one already-selected aircraft integration step.
    ///
    /// `unix_s`, Mach, altitude and temperature are BEGINNING-OF-STEP values.  This is
    /// intentional: the historical kinematic loop also computes its velocity from that state
    /// before applying the position/manoeuvre/OU updates for the step.
    pub fn advance_step(
        &mut self,
        unix_s: f64,
        dt_s: f64,
        mach: f64,
        altitude_ft: f64,
        temperature_k: f64,
    ) -> f64 {
        let gross_weight_kg = self.mass.gross_weight_kg(self.state);
        let nominal_flow_kg_h = self.flow.flow_kg_h(mach, altitude_ft, gross_weight_kg, temperature_k);
        self.state.advance(unix_s, dt_s, nominal_flow_kg_h)
    }
}

/// This function documents the exact insertion operation in `Aircraft::propagate`.
/// It is kept independent of `Aircraft` so it can be unit-tested before the production
/// flight crate is patched.
pub fn advance_fuel_if_enabled<F: FuelFlowModel>(
    fuel: Option<&mut FuelContext<'_, F>>,
    unix_s: f64,
    dt_s: f64,
    mach: f64,
    altitude_ft: f64,
    temperature_k: f64,
) -> f64 {
    match fuel {
        None => 0.0,
        Some(f) => f.advance_step(unix_s, dt_s, mach, altitude_ft, temperature_k),
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::fuel::SyntheticFuelFlow;

    #[test]
    fn disabled_step_is_exact_noop() {
        let burned = advance_fuel_if_enabled::<SyntheticFuelFlow>(None, 1_000.0, 10.0, 0.80, 35_000.0, 220.0);
        assert_eq!(burned.to_bits(), 0.0f64.to_bits());
    }

    #[test]
    fn gross_weight_falls_exactly_with_burned_fuel() {
        let flow = SyntheticFuelFlow { base_kg_h: 3_600.0 };
        let mass = MassModel { zero_fuel_mass_kg: 150_000.0 };
        let mut state = FuelState::new(40_000.0, 1.0);
        let before = mass.gross_weight_kg(&state);
        let mut ctx = FuelContext { state: &mut state, flow: &flow, mass };
        let burned = ctx.advance_step(0.0, 10.0, 0.80, 35_000.0, 220.0);
        let after = mass.gross_weight_kg(ctx.state);
        assert!((before - after - burned).abs() < 1e-9);
    }

    #[test]
    fn repeated_exact_steps_preserve_continuous_exhaustion_time() {
        struct ConstantFlow;
        impl FuelFlowModel for ConstantFlow {
            fn flow_kg_h(&self, _m: f64, _a: f64, _w: f64, _t: f64) -> f64 { 7_200.0 }
        }
        let flow = ConstantFlow;
        let mass = MassModel { zero_fuel_mass_kg: 150_000.0 };
        let mut state = FuelState::new(25.0, 1.0); // 2 kg/s -> 12.5 s endurance
        let mut ctx = FuelContext { state: &mut state, flow: &flow, mass };
        ctx.advance_step(1_000.0, 10.0, 0.80, 35_000.0, 220.0);
        ctx.advance_step(1_010.0, 10.0, 0.80, 35_000.0, 220.0);
        assert_eq!(ctx.state.exhausted_unix_s, Some(1_012.5));
        assert_eq!(ctx.state.remaining_kg, 0.0);
    }
}
