//! Table-driven fuel state for the pre-00:11 estimator.
//!
//! Deliberately independent of the Ulich workbook parser: the workbook is an input
//! adapter; this module owns interpolation, uncertainty scaling and fuel accounting.
//! Fuel is propagated with the same dt as aircraft kinematics.

#[derive(Debug, Clone, Copy, PartialEq)]
pub struct FuelState {
    pub remaining_kg: f64,
    /// Particle-level multiplicative calibration factor; design prior N(1.009, 0.018).
    pub flow_factor: f64,
    pub exhausted_unix_s: Option<f64>,
}

impl FuelState {
    pub fn new(remaining_kg: f64, flow_factor: f64) -> Self {
        assert!(remaining_kg >= 0.0);
        assert!(flow_factor > 0.0);
        Self { remaining_kg, flow_factor, exhausted_unix_s: None }
    }

    /// Advance by dt using total two-engine fuel flow in kg/h.
    /// Returns fuel burned during this step. If exhaustion occurs inside the step,
    /// its time is linearly interpolated from the pre-step fuel and burn rate.
    pub fn advance(&mut self, unix_s: f64, dt_s: f64, nominal_flow_kg_h: f64) -> f64 {
        assert!(dt_s >= 0.0);
        assert!(nominal_flow_kg_h >= 0.0);
        if self.remaining_kg == 0.0 || dt_s == 0.0 { return 0.0; }
        let rate_kg_s = nominal_flow_kg_h * self.flow_factor / 3600.0;
        if rate_kg_s == 0.0 { return 0.0; }
        let requested = rate_kg_s * dt_s;
        let burned = requested.min(self.remaining_kg);
        if requested >= self.remaining_kg && self.exhausted_unix_s.is_none() {
            self.exhausted_unix_s = Some(unix_s + self.remaining_kg / rate_kg_s);
        }
        self.remaining_kg -= burned;
        burned
    }

    pub fn predicted_endurance_s(&self, nominal_flow_kg_h: f64) -> Option<f64> {
        let rate = nominal_flow_kg_h * self.flow_factor / 3600.0;
        (rate > 0.0).then(|| self.remaining_kg / rate)
    }
}

/// Generic multilinear table interface. The real workbook adapter can implement this
/// without leaking spreadsheet details into the flight model.
pub trait FuelFlowModel {
    /// Total two-engine flow, kg/h, at the instantaneous aircraft state.
    fn flow_kg_h(&self, mach: f64, altitude_ft: f64, gross_weight_kg: f64, temperature_k: f64) -> f64;
}

/// Small deterministic model used only for plumbing/regression tests.
#[derive(Debug, Clone, Copy)]
pub struct SyntheticFuelFlow {
    pub base_kg_h: f64,
}

impl FuelFlowModel for SyntheticFuelFlow {
    fn flow_kg_h(&self, mach: f64, altitude_ft: f64, gross_weight_kg: f64, temperature_k: f64) -> f64 {
        // Smooth monotone response, intentionally not a physical 777 model.
        let mach_term = 1.0 + 1.5 * (mach - 0.80);
        let alt_term = 1.0 - 0.000_005 * (altitude_ft - 35_000.0);
        let weight_term = gross_weight_kg / 200_000.0;
        let temp_term = 1.0 + 0.002 * (temperature_k - 220.0);
        (self.base_kg_h * mach_term * alt_term * weight_term * temp_term).max(0.0)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn constant_flow_accounting_is_exact() {
        let mut f = FuelState::new(10_000.0, 1.0);
        let burned = f.advance(0.0, 3600.0, 5_000.0);
        assert!((burned - 5_000.0).abs() < 1e-9);
        assert!((f.remaining_kg - 5_000.0).abs() < 1e-9);
        assert_eq!(f.exhausted_unix_s, None);
    }

    #[test]
    fn exhaustion_time_is_inside_step_not_quantized_to_step_end() {
        let mut f = FuelState::new(100.0, 1.0);
        f.advance(1_000.0, 100.0, 7_200.0); // 2 kg/s => exhaustion after 50 s
        assert_eq!(f.remaining_kg, 0.0);
        assert_eq!(f.exhausted_unix_s, Some(1_050.0));
    }

    #[test]
    fn flow_factor_scales_burn_and_endurance() {
        let a = FuelState::new(10_000.0, 1.0);
        let b = FuelState::new(10_000.0, 1.01);
        let ea = a.predicted_endurance_s(5_000.0).unwrap();
        let eb = b.predicted_endurance_s(5_000.0).unwrap();
        assert!(eb < ea);
        assert!((eb / ea - 1.0 / 1.01).abs() < 1e-12);
    }

    #[test]
    fn zero_dt_is_neutral() {
        let mut f = FuelState::new(10_000.0, 1.009);
        assert_eq!(f.advance(123.0, 0.0, 5_000.0), 0.0);
        assert_eq!(f.remaining_kg, 10_000.0);
    }

    #[test]
    fn synthetic_model_responds_to_state() {
        let m = SyntheticFuelFlow { base_kg_h: 5_000.0 };
        let x = m.flow_kg_h(0.80, 35_000.0, 200_000.0, 220.0);
        assert!((x - 5_000.0).abs() < 1e-9);
        assert!(m.flow_kg_h(0.82, 35_000.0, 200_000.0, 220.0) > x);
    }
}
