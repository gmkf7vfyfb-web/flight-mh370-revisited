//! Explicit conditional fuel-performance families used by the end-of-flight runner.
//!
//! The Martin family is a compact transcription of the RR Trent 892 long-range-cruise
//! coefficients in the user-supplied BSM v7.9.4 workbook.  It is not a Boeing or
//! Rolls-Royce performance deck and carries no inferred probability.  The Kong check is
//! deliberately a comparison at one public-table fixture, not a second initializer.

use serde::{Deserialize, Serialize};
use thiserror::Error;

use crate::{Kilograms, KilogramsPerSecond};

pub const MARTIN_BSM_V7_9_4_WORKBOOK_SHA256: &str =
    "508d4288acac0b3eccf70ae200e0517d79979cbb47197155cee1b748142b8220";
pub const KONG_FUEL_TABLE_WORKBOOK_SHA256: &str =
    "5fee5196208c8655fb50af3f991df2e9a80298c84d800bb4990d5ca06f264437";

/// RR Trent 892 LRC total two-engine flow: `dm/dt = A + B * gross_mass_kg`.
#[derive(Debug, Clone, Copy, PartialEq, Serialize, Deserialize)]
pub struct MartinTrent892LrcCoefficient {
    pub flight_level: f64,
    pub intercept_kg_s: f64,
    pub gross_mass_coefficient_s_inv: f64,
}

pub const MARTIN_TRENT892_LRC_COEFFICIENTS: [MartinTrent892LrcCoefficient; 4] = [
    MartinTrent892LrcCoefficient {
        flight_level: 350.0,
        intercept_kg_s: -0.006,
        gross_mass_coefficient_s_inv: 8.566_666_7e-6,
    },
    MartinTrent892LrcCoefficient {
        flight_level: 370.0,
        intercept_kg_s: 0.084_166_666_667,
        gross_mass_coefficient_s_inv: 8.069_444_444_4e-6,
    },
    MartinTrent892LrcCoefficient {
        flight_level: 390.0,
        intercept_kg_s: 0.029_333_333_333,
        gross_mass_coefficient_s_inv: 8.433_333_333_3e-6,
    },
    MartinTrent892LrcCoefficient {
        flight_level: 410.0,
        intercept_kg_s: 0.001_481_481_481_5,
        gross_mass_coefficient_s_inv: 8.638_888_888_9e-6,
    },
];

#[derive(Debug, Error, Clone, Copy, PartialEq)]
pub enum FuelPerformanceError {
    #[error("fuel-performance input is non-finite or non-positive")]
    InvalidInput,
    #[error("Martin LRC pressure altitude is outside FL350-FL410")]
    OutsideMartinLrcAltitude,
    #[error("conditional fuel is exhausted before the requested endpoint")]
    ExhaustedBeforeEndpoint,
}

#[derive(Debug, Clone, Copy, PartialEq, Serialize, Deserialize)]
pub struct MartinFuelProjection {
    pub start_total_fuel: Kilograms,
    pub end_total_fuel: Kilograms,
    pub elapsed_seconds: f64,
    pub start_total_flow: KilogramsPerSecond,
    pub end_total_flow: KilogramsPerSecond,
    pub coefficient: MartinTrent892LrcCoefficient,
}

pub fn martin_trent892_lrc_coefficient(
    pressure_altitude_ft: f64,
) -> Result<MartinTrent892LrcCoefficient, FuelPerformanceError> {
    if !pressure_altitude_ft.is_finite() {
        return Err(FuelPerformanceError::InvalidInput);
    }
    let flight_level = pressure_altitude_ft / 100.0;
    let first = MARTIN_TRENT892_LRC_COEFFICIENTS[0];
    let last = *MARTIN_TRENT892_LRC_COEFFICIENTS.last().unwrap();
    if flight_level < first.flight_level || flight_level > last.flight_level {
        return Err(FuelPerformanceError::OutsideMartinLrcAltitude);
    }
    if flight_level == last.flight_level {
        return Ok(last);
    }
    let pair = MARTIN_TRENT892_LRC_COEFFICIENTS
        .windows(2)
        .find(|pair| flight_level >= pair[0].flight_level && flight_level <= pair[1].flight_level)
        .expect("validated flight level is bracketed");
    let fraction =
        (flight_level - pair[0].flight_level) / (pair[1].flight_level - pair[0].flight_level);
    Ok(MartinTrent892LrcCoefficient {
        flight_level,
        intercept_kg_s: pair[0].intercept_kg_s
            + fraction * (pair[1].intercept_kg_s - pair[0].intercept_kg_s),
        gross_mass_coefficient_s_inv: pair[0].gross_mass_coefficient_s_inv
            + fraction
                * (pair[1].gross_mass_coefficient_s_inv - pair[0].gross_mass_coefficient_s_inv),
    })
}

pub fn martin_trent892_lrc_total_flow(
    pressure_altitude_ft: f64,
    gross_mass_kg: f64,
) -> Result<KilogramsPerSecond, FuelPerformanceError> {
    if !gross_mass_kg.is_finite() || gross_mass_kg <= 0.0 {
        return Err(FuelPerformanceError::InvalidInput);
    }
    let coefficient = martin_trent892_lrc_coefficient(pressure_altitude_ft)?;
    let flow =
        coefficient.intercept_kg_s + coefficient.gross_mass_coefficient_s_inv * gross_mass_kg;
    if !flow.is_finite() || flow <= 0.0 {
        Err(FuelPerformanceError::InvalidInput)
    } else {
        Ok(KilogramsPerSecond(flow))
    }
}

/// Exact constant-flight-level solution of the workbook's linear total-flow equation.
pub fn project_martin_trent892_lrc_fuel(
    zero_fuel_weight_kg: f64,
    start_total_fuel_kg: f64,
    pressure_altitude_ft: f64,
    elapsed_seconds: f64,
) -> Result<MartinFuelProjection, FuelPerformanceError> {
    if !zero_fuel_weight_kg.is_finite()
        || zero_fuel_weight_kg <= 0.0
        || !start_total_fuel_kg.is_finite()
        || start_total_fuel_kg < 0.0
        || !elapsed_seconds.is_finite()
        || elapsed_seconds < 0.0
    {
        return Err(FuelPerformanceError::InvalidInput);
    }
    let coefficient = martin_trent892_lrc_coefficient(pressure_altitude_ft)?;
    let start_gross_mass = zero_fuel_weight_kg + start_total_fuel_kg;
    let a = coefficient.intercept_kg_s;
    let b = coefficient.gross_mass_coefficient_s_inv;
    let end_gross_mass = (start_gross_mass + a / b) * (-b * elapsed_seconds).exp() - a / b;
    let end_total_fuel = end_gross_mass - zero_fuel_weight_kg;
    if end_total_fuel < 0.0 {
        return Err(FuelPerformanceError::ExhaustedBeforeEndpoint);
    }
    Ok(MartinFuelProjection {
        start_total_fuel: Kilograms(start_total_fuel_kg),
        end_total_fuel: Kilograms(end_total_fuel),
        elapsed_seconds,
        start_total_flow: martin_trent892_lrc_total_flow(pressure_altitude_ft, start_gross_mass)?,
        end_total_flow: martin_trent892_lrc_total_flow(pressure_altitude_ft, end_gross_mass)?,
        coefficient,
    })
}

/// Independent coarse-table comparison at the official Arc-1 first-segment state.
///
/// The supplied Kong sheet omits units and provenance.  This value assumes its FL350/M0.829
/// cells are kg/h per engine and linearly interpolates the 200/220 tonne rows.  It is returned
/// only so a release manifest can quantify agreement; it must not initialize fuel.
pub fn kong_arc1_assumed_total_flow_kg_s(gross_mass_kg: f64) -> Result<f64, FuelPerformanceError> {
    if !gross_mass_kg.is_finite() || !(200_000.0..=220_000.0).contains(&gross_mass_kg) {
        return Err(FuelPerformanceError::InvalidInput);
    }
    let mach_fraction = 0.9;
    let per_engine_200 = 3_055.0 + mach_fraction * (3_115.0 - 3_055.0);
    let per_engine_220 = 3_257.0 + mach_fraction * (3_303.0 - 3_257.0);
    let mass_fraction = (gross_mass_kg - 200_000.0) / 20_000.0;
    let per_engine_kg_h = per_engine_200 + mass_fraction * (per_engine_220 - per_engine_200);
    Ok(2.0 * per_engine_kg_h / 3_600.0)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn workbook_fl350_coefficients_and_exact_projection_are_reproduced() {
        let coefficient = martin_trent892_lrc_coefficient(35_000.0).unwrap();
        assert_eq!(coefficient, MARTIN_TRENT892_LRC_COEFFICIENTS[0]);
        let projected =
            project_martin_trent892_lrc_fuel(174_369.0, 33_524.104_881_96, 35_000.0, 20_573.1)
                .unwrap();
        assert!((projected.end_total_fuel.0 - 44.728_094_939).abs() < 1.0e-8);
        assert!((projected.start_total_flow.0 - 1.774_950_938_75).abs() < 1.0e-11);
    }

    #[test]
    fn kong_fixture_is_an_independent_close_check_not_an_initializer() {
        let gross_mass = 174_369.0 + 33_524.104_881_96;
        let martin = martin_trent892_lrc_total_flow(35_000.0, gross_mass)
            .unwrap()
            .0;
        let kong = kong_arc1_assumed_total_flow_kg_s(gross_mass).unwrap();
        assert!(((kong - martin) / martin).abs() < 0.01);
    }

    #[test]
    fn invalid_altitude_and_exhausted_projection_are_explicit() {
        assert_eq!(
            martin_trent892_lrc_coefficient(34_999.0),
            Err(FuelPerformanceError::OutsideMartinLrcAltitude)
        );
        assert_eq!(
            project_martin_trent892_lrc_fuel(174_369.0, 10.0, 35_000.0, 60.0),
            Err(FuelPerformanceError::ExhaustedBeforeEndpoint)
        );
    }
}
