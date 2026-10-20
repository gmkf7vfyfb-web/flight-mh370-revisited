//! Air properties and the pressure-altitude / geometric-altitude distinction.
//!
//! The core carries altitude as **pressure altitude in feet** everywhere, and the runner's
//! `Air::pressure_pa` is `geo::isa_pressure_pa(altitude_ft)` — pressure is an exact function of
//! the pressure altitude, while temperature comes from ERA5. Two consequences the integrator
//! must respect:
//!
//! 1. density is `p/(R T)` with the ISA pressure and the *measured* temperature, so a warm or
//!    cold anomaly changes density and therefore lift and drag;
//! 2. a rate of change of pressure altitude is not a geometric rate of climb. From the
//!    hydrostatic relation with the same pressure in both, `dh_geom/dh_press = T / T_ISA`. The
//!    BFO responds to the geometric rate, so the two are kept separate and converted once, here.
//!
//! The ISA constants are the standard ones (ICAO Standard Atmosphere); nothing here is fitted.

/// Specific gas constant of dry air, J/(kg K).
pub const R_AIR: f64 = 287.052_87;
/// Ratio of specific heats for air.
pub const GAMMA: f64 = 1.4;
/// Standard gravity, m/s^2.
pub const G0: f64 = 9.806_65;
/// ISA sea-level temperature, K.
pub const ISA_T0_K: f64 = 288.15;
/// ISA tropospheric lapse rate, K/m.
pub const ISA_LAPSE_K_PER_M: f64 = 0.006_5;
/// ISA tropopause, geopotential metres.
pub const ISA_TROPOPAUSE_M: f64 = 11_000.0;
/// ISA temperature above the tropopause, K.
pub const ISA_T_TROPOPAUSE_K: f64 = 216.65;

pub const M_PER_FT: f64 = 0.304_8;
pub const FPM_PER_MPS: f64 = 60.0 / M_PER_FT;
#[cfg_attr(not(test), allow(dead_code))] // model surface exercised by this module's tests
pub const M_PER_NM: f64 = 1_852.0;

/// ISA temperature at a pressure altitude, K. Used only to convert between pressure-altitude
/// and geometric rates, and as the standalone atmosphere in this module's own tests.
pub fn isa_temperature_k(pressure_altitude_ft: f64) -> f64 {
    let h_m = pressure_altitude_ft * M_PER_FT;
    if h_m <= ISA_TROPOPAUSE_M {
        ISA_T0_K - ISA_LAPSE_K_PER_M * h_m
    } else {
        ISA_T_TROPOPAUSE_K
    }
}

/// Air density, kg/m^3.
pub fn density_kg_m3(pressure_pa: f64, temperature_k: f64) -> f64 {
    pressure_pa / (R_AIR * temperature_k)
}

/// Speed of sound, m/s.
pub fn sound_speed_mps(temperature_k: f64) -> f64 {
    (GAMMA * R_AIR * temperature_k).sqrt()
}

/// Dynamic pressure from Mach and static pressure: q = gamma/2 * p * M^2, which avoids forming
/// density and true airspeed separately.
pub fn dynamic_pressure_pa(pressure_pa: f64, mach: f64) -> f64 {
    0.5 * GAMMA * pressure_pa * mach * mach
}

/// Factor converting a rate of change of pressure altitude into a geometric rate of climb at a
/// measured temperature: `dh_geom = (T / T_ISA) dh_press`. Returns 1 if either temperature is
/// not usable, so a missing weather field degrades to the ISA identity rather than to NaN.
pub fn geometric_rate_factor(pressure_altitude_ft: f64, temperature_k: f64) -> f64 {
    let isa = isa_temperature_k(pressure_altitude_ft);
    if temperature_k.is_finite() && temperature_k > 100.0 && isa > 0.0 {
        temperature_k / isa
    } else {
        1.0
    }
}

/// The International Standard Atmosphere, still air, zero declination, sea-level surface.
///
/// The runner always supplies ERA5 through `hypothesis::Atmosphere`; this exists so the physics
/// tests in this module can be run against a known analytic atmosphere, and so a descent can be
/// integrated standalone when checking the integrator. It is never used in a run.
#[cfg_attr(not(test), allow(dead_code))] // model surface exercised by this module's tests
pub struct Standard;

impl hypothesis::Atmosphere for Standard {
    fn at(&self, _unix_s: f64, altitude_ft: f64, _latitude_deg: f64, _longitude_deg: f64) -> hypothesis::Air {
        hypothesis::Air {
            temperature_k: isa_temperature_k(altitude_ft),
            pressure_pa: geo::isa_pressure_pa(altitude_ft),
            wind_east_mps: 0.0,
            wind_north_mps: 0.0,
            declination_deg: 0.0,
            surface_pressure_altitude_ft: 0.0,
            clamped: false,
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    /// Hand-computed ISA fixture at FL350 (35,000 ft = 10,668 m, below the tropopause):
    ///   T = 288.15 - 0.0065 * 10668          = 218.808 K
    ///   p = 101325 * (T/288.15)^(g/(R*L))    = 23,842.3 Pa   (exponent 5.255 88)
    ///   rho = p/(R T)                        = 0.379 60 kg/m^3
    ///   a = sqrt(1.4 * 287.052 87 * T)       = 296.54 m/s
    #[test]
    fn isa_at_fl350_matches_a_hand_computation() {
        let t = isa_temperature_k(35_000.0);
        assert!((t - 218.808).abs() < 1e-3, "T = {t}");
        let exponent = G0 / (R_AIR * ISA_LAPSE_K_PER_M);
        let p_hand = 101_325.0 * (t / ISA_T0_K).powf(exponent);
        let p = geo::isa_pressure_pa(35_000.0);
        assert!((p - p_hand).abs() / p_hand < 1e-4, "p = {p}, hand {p_hand}");
        assert!((p - 23_842.3).abs() < 2.0, "p = {p}");
        let rho = density_kg_m3(p, t);
        assert!((rho - 0.379_60).abs() < 5e-5, "rho = {rho}");
        let a = sound_speed_mps(t);
        assert!((a - 296.54).abs() < 0.02, "a = {a}");
    }

    /// q = gamma/2 p M^2 and q = rho V^2 / 2 are the same number.
    #[test]
    fn dynamic_pressure_agrees_with_half_rho_v_squared() {
        let (p, t, mach) = (geo::isa_pressure_pa(20_000.0), isa_temperature_k(20_000.0), 0.72);
        let v = mach * sound_speed_mps(t);
        let direct = 0.5 * density_kg_m3(p, t) * v * v;
        assert!((dynamic_pressure_pa(p, mach) - direct).abs() / direct < 1e-12);
    }

    /// In ISA the two altitude rates coincide; 10 K warm at FL350 makes the geometric rate
    /// 10/218.808 = 4.57% larger, which is 137 ft/min on a 3,000 ft/min pressure-altitude rate.
    #[test]
    fn a_warm_anomaly_makes_the_geometric_rate_larger() {
        assert!((geometric_rate_factor(35_000.0, isa_temperature_k(35_000.0)) - 1.0).abs() < 1e-12);
        let f = geometric_rate_factor(35_000.0, isa_temperature_k(35_000.0) + 10.0);
        assert!((f - 1.045_70).abs() < 1e-4, "factor {f}");
        assert!((3_000.0 * f - 3_137.1).abs() < 0.5);
        assert_eq!(geometric_rate_factor(35_000.0, f64::NAN), 1.0);
    }
}
