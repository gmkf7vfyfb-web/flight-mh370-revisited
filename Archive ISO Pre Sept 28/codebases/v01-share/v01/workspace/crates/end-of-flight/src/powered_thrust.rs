//! Conditional OpenAP B772/Trent-895 cruise-thrust ceiling.
//!
//! This is a scalar implementation of the pinned OpenAP v2.6.0 cruise
//! equation for an engine that OpenAP accepts for B772.  It deliberately does
//! not force the rejected B772/Trent-892 pairing.  The caller owns the
//! uncertainty multiplier and static cap; neither is inferred here.

use mh370_domain::Feet;
use serde::{Deserialize, Serialize};
use thiserror::Error;

use crate::Newtons;

const FEET_TO_METRES: f64 = 0.304_8;
const SEA_LEVEL_PRESSURE_PA: f64 = 101_325.0;
const SEA_LEVEL_DENSITY_KG_M3: f64 = 1.225;
const SEA_LEVEL_TEMPERATURE_K: f64 = 288.15;
const TROPOPAUSE_TEMPERATURE_K: f64 = 216.65;
const TROPOSPHERIC_LAPSE_K_M: f64 = -0.006_5;
const SPECIFIC_GAS_CONSTANT_DRY_AIR: f64 = 287.052_87;
const HEAT_CAPACITY_RATIO: f64 = 1.4;
const TROPOSPHERIC_DENSITY_EXPONENT: f64 = 4.256_848_030_018_761;
const STRATOSPHERIC_DENSITY_SCALE_M: f64 = 6_341.552_161;
const OPENAP_CRUISE_ALTITUDE_M: f64 = 11_000.0;
const OPENAP_CRUISE_MACH: f64 = 0.84;
const OPENAP_ENGINE_MAX_STATIC_THRUST_N: f64 = 413_050.0;
const OPENAP_ENGINE_CRUISE_THRUST_N: f64 = 0.2 * OPENAP_ENGINE_MAX_STATIC_THRUST_N + 890.0;
const B772_ENGINE_COUNT: f64 = 2.0;

pub const OPENAP_B772_TRENT895_MINIMUM_PRESSURE_ALTITUDE_FT: f64 = 0.0;
pub const OPENAP_B772_TRENT895_MAXIMUM_PRESSURE_ALTITUDE_FT: f64 = 43_000.0;
pub const OPENAP_B772_TRENT895_MINIMUM_MACH: f64 = 0.1;
pub const OPENAP_B772_TRENT895_MAXIMUM_MACH: f64 = 0.89;

/// Exact local identities used to reproduce the conditional source equation.
pub const OPENAP_B772_TRENT895_THRUST_PROVENANCE: &[&str] = &[
    "OpenAP v2.6.0 commit 4fb21d6e402fd1f4a48b191ad6801c74479e71f5",
    "openap/thrust.py SHA-256 e79d18b156010a66f2e6f11a766a5257323665d4d9f93646f43809eb5d4d173a",
    "openap/data/aircraft/b772.yml SHA-256 6c056746a9430cf2dd4232ab3486e3c3141ed88478f7ab25959b52a2ed9b8273",
    "openap/data/engine/engines.csv SHA-256 90f58f10a25d71c9c1b18f4611a8bfcd4f2fd15382c57df428397344ee6333d2",
    "engine family is OpenAP's accepted B772 Trent 895 option, not a forced Trent 892 pairing",
];

/// Interpretation limits that must accompany this ceiling.
pub const OPENAP_B772_TRENT895_THRUST_LIMITATIONS: &[&str] = &[
    "conditional simplified two-shaft turbofan proxy; not a calibrated 9M-MRO Trent 892B-17 deck",
    "uses pressure altitude with ISA temperature and OpenAP's zero-rate cruise equation",
    "caller-declared multiplier and static cap are analyst choices, not source uncertainties",
    "no bleed, installation, deterioration, throttle/spool, asymmetric-control, or windmilling model",
    "audited B772 trajectory coverage is contextual and does not validate the thrust equation",
    "the numerical proxy domain is broader than the audited B772 trajectory coverage",
];

/// Whether the query lies inside the separately audited B772 climb-trajectory
/// coverage.  This status is not a thrust-validation claim.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum OpenapB772Trent895DomainStatus {
    WithinAuditedB772TrajectoryCoverage,
    EquationExtrapolationWithinDeclaredProxyDomain,
}

#[derive(Debug, Clone, Copy, PartialEq, Serialize, Deserialize)]
pub struct OpenapB772Trent895CruiseThrustInput {
    pub pressure_altitude: Feet,
    pub mach: f64,
    /// Must be 0, 1, or 2.  Scaling is symmetric and does not model yaw.
    pub operating_engine_count: u8,
    /// Caller-declared multiplicative allowance on the nominal equation.
    pub declared_multiplier: f64,
    /// Caller-declared cap for each operating engine.
    pub declared_static_cap_per_engine: Newtons,
}

#[derive(Debug, Clone, Copy, PartialEq, Serialize, Deserialize)]
pub struct OpenapB772Trent895CruiseThrustCeiling {
    pub nominal_two_engine_total: Newtons,
    pub nominal_operating_engine_total: Newtons,
    pub multiplied_uncapped_total: Newtons,
    pub declared_static_cap_total: Newtons,
    pub total_ceiling: Newtons,
    pub static_cap_applied: bool,
    pub domain_status: OpenapB772Trent895DomainStatus,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, Error)]
pub enum OpenapB772Trent895CruiseThrustError {
    #[error("pressure altitude is outside the declared OpenAP proxy domain")]
    PressureAltitudeOutsideProxyDomain,
    #[error("Mach is outside the declared OpenAP proxy domain")]
    MachOutsideProxyDomain,
    #[error("operating engine count must be 0, 1, or 2")]
    InvalidOperatingEngineCount,
    #[error("declared thrust multiplier must be finite and strictly positive")]
    InvalidDeclaredMultiplier,
    #[error("declared static cap per engine must be finite and strictly positive")]
    InvalidDeclaredStaticCap,
    #[error("OpenAP cruise-thrust proxy produced a non-finite or negative result")]
    NonFiniteResult,
}

/// Evaluate the pinned OpenAP cruise equation and apply caller-owned bounds.
pub fn openap_b772_trent895_cruise_thrust_ceiling(
    input: OpenapB772Trent895CruiseThrustInput,
) -> Result<OpenapB772Trent895CruiseThrustCeiling, OpenapB772Trent895CruiseThrustError> {
    validate_input(input)?;

    let nominal_two_engine_total =
        nominal_two_engine_cruise_thrust_n(input.pressure_altitude.0, input.mach);
    let engine_fraction = f64::from(input.operating_engine_count) / B772_ENGINE_COUNT;
    let nominal_operating_engine_total = nominal_two_engine_total * engine_fraction;
    let multiplied_uncapped_total = nominal_operating_engine_total * input.declared_multiplier;
    let declared_static_cap_total =
        input.declared_static_cap_per_engine.0 * f64::from(input.operating_engine_count);
    let static_cap_applied = multiplied_uncapped_total > declared_static_cap_total;
    let total_ceiling = multiplied_uncapped_total.min(declared_static_cap_total);

    if [
        nominal_two_engine_total,
        nominal_operating_engine_total,
        multiplied_uncapped_total,
        declared_static_cap_total,
        total_ceiling,
    ]
    .into_iter()
    .any(|value| !value.is_finite() || value < 0.0)
    {
        return Err(OpenapB772Trent895CruiseThrustError::NonFiniteResult);
    }

    let domain_status = if (125.0..=24_975.0).contains(&input.pressure_altitude.0)
        && (0.1..=0.768).contains(&input.mach)
    {
        OpenapB772Trent895DomainStatus::WithinAuditedB772TrajectoryCoverage
    } else {
        OpenapB772Trent895DomainStatus::EquationExtrapolationWithinDeclaredProxyDomain
    };

    Ok(OpenapB772Trent895CruiseThrustCeiling {
        nominal_two_engine_total: Newtons(nominal_two_engine_total),
        nominal_operating_engine_total: Newtons(nominal_operating_engine_total),
        multiplied_uncapped_total: Newtons(multiplied_uncapped_total),
        declared_static_cap_total: Newtons(declared_static_cap_total),
        total_ceiling: Newtons(total_ceiling),
        static_cap_applied,
        domain_status,
    })
}

fn validate_input(
    input: OpenapB772Trent895CruiseThrustInput,
) -> Result<(), OpenapB772Trent895CruiseThrustError> {
    if !input.pressure_altitude.is_finite()
        || !(OPENAP_B772_TRENT895_MINIMUM_PRESSURE_ALTITUDE_FT
            ..=OPENAP_B772_TRENT895_MAXIMUM_PRESSURE_ALTITUDE_FT)
            .contains(&input.pressure_altitude.0)
    {
        return Err(OpenapB772Trent895CruiseThrustError::PressureAltitudeOutsideProxyDomain);
    }
    if !input.mach.is_finite()
        || !(OPENAP_B772_TRENT895_MINIMUM_MACH..=OPENAP_B772_TRENT895_MAXIMUM_MACH)
            .contains(&input.mach)
    {
        return Err(OpenapB772Trent895CruiseThrustError::MachOutsideProxyDomain);
    }
    if input.operating_engine_count > 2 {
        return Err(OpenapB772Trent895CruiseThrustError::InvalidOperatingEngineCount);
    }
    if !input.declared_multiplier.is_finite() || input.declared_multiplier <= 0.0 {
        return Err(OpenapB772Trent895CruiseThrustError::InvalidDeclaredMultiplier);
    }
    if !input.declared_static_cap_per_engine.is_finite()
        || input.declared_static_cap_per_engine.0 <= 0.0
    {
        return Err(OpenapB772Trent895CruiseThrustError::InvalidDeclaredStaticCap);
    }
    Ok(())
}

fn nominal_two_engine_cruise_thrust_n(pressure_altitude_ft: f64, mach: f64) -> f64 {
    let altitude_m = pressure_altitude_ft * FEET_TO_METRES;
    let pressure_pa = isa_pressure_pa(altitude_m);
    let cruise_pressure_pa = isa_pressure_pa(OPENAP_CRUISE_ALTITUDE_M);
    let total_reference_thrust_n = OPENAP_ENGINE_CRUISE_THRUST_N * B772_ENGINE_COUNT;
    let calibrated_speed = mach_to_calibrated_speed_m_s(mach, altitude_m);
    let reference_calibrated_speed =
        mach_to_calibrated_speed_m_s(OPENAP_CRUISE_MACH, OPENAP_CRUISE_ALTITUDE_M);
    let calibrated_speed_ratio = calibrated_speed / reference_calibrated_speed;

    let ratio = if pressure_altitude_ft > 30_000.0 {
        let mach_ratio = mach / OPENAP_CRUISE_MACH;
        let d = -0.420_4 * mach_ratio + 1.082_4;
        let b = mach_ratio.powf(-0.11);
        d * (pressure_pa / cruise_pressure_pa).ln() + b
    } else {
        let a = calibrated_speed_ratio.powf(-0.1);
        let n = 0.863_3;
        let segment_two_ratio =
            a * (pressure_pa / cruise_pressure_pa).powf(-0.355 * calibrated_speed_ratio + n);
        if pressure_altitude_ft > 10_000.0 {
            segment_two_ratio
        } else {
            let pressure_10_000_pa = isa_pressure_pa(10_000.0 * FEET_TO_METRES);
            let thrust_10_000_n = total_reference_thrust_n
                * a
                * (pressure_10_000_pa / cruise_pressure_pa)
                    .powf(-0.355 * calibrated_speed_ratio + n);
            let m = -0.120_43 * calibrated_speed_ratio + 0.473_79;
            m * (pressure_pa / cruise_pressure_pa)
                + (thrust_10_000_n / total_reference_thrust_n
                    - m * (pressure_10_000_pa / cruise_pressure_pa))
        }
    };
    ratio * total_reference_thrust_n
}

fn isa_pressure_pa(altitude_m: f64) -> f64 {
    let temperature_k = (SEA_LEVEL_TEMPERATURE_K + TROPOSPHERIC_LAPSE_K_M * altitude_m)
        .max(TROPOPAUSE_TEMPERATURE_K);
    let height_above_tropopause_m = (altitude_m - OPENAP_CRUISE_ALTITUDE_M).max(0.0);
    let density_kg_m3 = SEA_LEVEL_DENSITY_KG_M3
        * (temperature_k / SEA_LEVEL_TEMPERATURE_K).powf(TROPOSPHERIC_DENSITY_EXPONENT)
        * (-height_above_tropopause_m / STRATOSPHERIC_DENSITY_SCALE_M).exp();
    density_kg_m3 * SPECIFIC_GAS_CONSTANT_DRY_AIR * temperature_k
}

fn mach_to_calibrated_speed_m_s(mach: f64, altitude_m: f64) -> f64 {
    let pressure_pa = isa_pressure_pa(altitude_m);
    let temperature_k = (SEA_LEVEL_TEMPERATURE_K + TROPOSPHERIC_LAPSE_K_M * altitude_m)
        .max(TROPOPAUSE_TEMPERATURE_K);
    let density_kg_m3 = pressure_pa / (SPECIFIC_GAS_CONSTANT_DRY_AIR * temperature_k);
    let true_airspeed_m_s =
        mach * (HEAT_CAPACITY_RATIO * SPECIFIC_GAS_CONSTANT_DRY_AIR * temperature_k).sqrt();
    let impact_pressure_pa = pressure_pa
        * ((1.0 + density_kg_m3 * true_airspeed_m_s.powi(2) / (7.0 * pressure_pa)).powf(3.5) - 1.0);
    (7.0 * SEA_LEVEL_PRESSURE_PA / SEA_LEVEL_DENSITY_KG_M3
        * ((impact_pressure_pa / SEA_LEVEL_PRESSURE_PA + 1.0).powf(2.0 / 7.0) - 1.0))
        .sqrt()
}

#[cfg(test)]
mod tests {
    use super::*;

    fn input() -> OpenapB772Trent895CruiseThrustInput {
        OpenapB772Trent895CruiseThrustInput {
            pressure_altitude: Feet(35_000.0),
            mach: 0.84,
            operating_engine_count: 2,
            declared_multiplier: 1.0,
            declared_static_cap_per_engine: Newtons(411_480.0),
        }
    }

    #[test]
    fn pinned_runtime_probe_is_reproduced_without_forcing_trent892() {
        let result = openap_b772_trent895_cruise_thrust_ceiling(input()).unwrap();
        assert!((result.nominal_two_engine_total.0 - 172_760.213_763_354_67).abs() < 1.0e-6);
        assert_eq!(result.total_ceiling, result.nominal_two_engine_total);
        assert!(!result.static_cap_applied);
        assert_eq!(
            result.domain_status,
            OpenapB772Trent895DomainStatus::EquationExtrapolationWithinDeclaredProxyDomain
        );
    }

    #[test]
    fn declared_primary_multiplier_is_applied_exactly() {
        let mut input = input();
        input.declared_multiplier = 1.25;
        let result = openap_b772_trent895_cruise_thrust_ceiling(input).unwrap();
        assert!((result.total_ceiling.0 - 215_950.267_204_193_34).abs() < 1.0e-6);
        assert!(!result.static_cap_applied);
    }

    #[test]
    fn operating_engine_scaling_and_static_cap_are_explicit() {
        let two = openap_b772_trent895_cruise_thrust_ceiling(input()).unwrap();
        let mut one_input = input();
        one_input.operating_engine_count = 1;
        let one = openap_b772_trent895_cruise_thrust_ceiling(one_input).unwrap();
        assert_eq!(
            one.nominal_operating_engine_total.0 * 2.0,
            two.total_ceiling.0
        );

        let mut zero_input = input();
        zero_input.operating_engine_count = 0;
        let zero = openap_b772_trent895_cruise_thrust_ceiling(zero_input).unwrap();
        assert_eq!(zero.total_ceiling, Newtons(0.0));

        let mut capped_input = input();
        capped_input.declared_multiplier = 10.0;
        capped_input.declared_static_cap_per_engine = Newtons(100_000.0);
        let capped = openap_b772_trent895_cruise_thrust_ceiling(capped_input).unwrap();
        assert_eq!(capped.total_ceiling, Newtons(200_000.0));
        assert!(capped.static_cap_applied);
    }

    #[test]
    fn malformed_and_out_of_domain_inputs_are_typed() {
        let mut bad = input();
        bad.pressure_altitude = Feet(43_000.1);
        assert_eq!(
            openap_b772_trent895_cruise_thrust_ceiling(bad).unwrap_err(),
            OpenapB772Trent895CruiseThrustError::PressureAltitudeOutsideProxyDomain
        );

        let mut bad = input();
        bad.mach = 0.09;
        assert_eq!(
            openap_b772_trent895_cruise_thrust_ceiling(bad).unwrap_err(),
            OpenapB772Trent895CruiseThrustError::MachOutsideProxyDomain
        );

        let mut bad = input();
        bad.operating_engine_count = 3;
        assert_eq!(
            openap_b772_trent895_cruise_thrust_ceiling(bad).unwrap_err(),
            OpenapB772Trent895CruiseThrustError::InvalidOperatingEngineCount
        );

        let mut bad = input();
        bad.declared_multiplier = f64::NAN;
        assert_eq!(
            openap_b772_trent895_cruise_thrust_ceiling(bad).unwrap_err(),
            OpenapB772Trent895CruiseThrustError::InvalidDeclaredMultiplier
        );

        let mut bad = input();
        bad.declared_static_cap_per_engine = Newtons(0.0);
        assert_eq!(
            openap_b772_trent895_cruise_thrust_ceiling(bad).unwrap_err(),
            OpenapB772Trent895CruiseThrustError::InvalidDeclaredStaticCap
        );
    }

    #[test]
    fn audited_trajectory_coverage_status_is_not_silently_lost() {
        let mut covered_input = input();
        covered_input.pressure_altitude = Feet(20_000.0);
        covered_input.mach = 0.7;
        let result = openap_b772_trent895_cruise_thrust_ceiling(covered_input).unwrap();
        assert_eq!(
            result.domain_status,
            OpenapB772Trent895DomainStatus::WithinAuditedB772TrajectoryCoverage
        );
        assert!(result.total_ceiling.0.is_finite());
        assert!(result.total_ceiling.0 > 0.0);
    }
}
