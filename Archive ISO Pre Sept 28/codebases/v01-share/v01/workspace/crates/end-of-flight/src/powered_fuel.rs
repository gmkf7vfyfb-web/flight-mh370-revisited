//! Fast, deterministic fuel propagation for a time-varying powered-flight path.
//!
//! This module consumes a caller-sampled mass/feed state. It never chooses an initial
//! fuel value, tunes fuel to an exhaustion time, or evaluates SATCOM evidence. The
//! Martin model is valid only as a conditional FL350--FL410 LRC proxy. The broader
//! model exposes every extension/discrepancy coefficient as a declared input.

use mh370_domain::{Degrees, Feet, FeetPerMinute, Seconds};
use serde::{Deserialize, Serialize};
use thiserror::Error;

use crate::{
    martin_trent892_lrc_coefficient, Kilograms, KilogramsPerSecond, MartinTrent892LrcCoefficient,
};

pub(crate) const EVENT_TIME_TOLERANCE_S: f64 = 1.0e-9;
const MASS_TOLERANCE_KG: f64 = 1.0e-8;

/// Scientific boundaries that must accompany any result from this module.
pub const POWERED_FUEL_LIMITATIONS: &[&str] = &[
    "Martin BSM v7.9.4 is a conditional spreadsheet proxy, not a Boeing or Rolls-Royce performance deck",
    "the Martin coefficients represent two-engine long-range cruise only at FL350-FL410",
    "Mach, bank, climb, descent, temperature, and off-table altitude effects in the broad family are declared model choices",
    "total reported fuel does not identify physical tank, crossfeed, APU, unusable, or left/right feed state",
    "initial fuel and feed state must be sampled upstream without conditioning on a desired exhaustion time",
    "predicted exhaustion timestamps carry no fuel-exhaustion-window or SATCOM likelihood",
];

/// Compact fuel state carried beside, never inside, an AircraftState.
#[derive(Debug, Clone, Copy, PartialEq, Serialize, Deserialize)]
pub struct PoweredFuelState {
    pub time: Seconds,
    pub zero_fuel_weight: Kilograms,
    pub left_usable_feed: Kilograms,
    pub right_usable_feed: Kilograms,
    pub reserved_fuel: Kilograms,
    pub unusable_fuel: Kilograms,
    pub left_exhaustion_time: Option<Seconds>,
    pub right_exhaustion_time: Option<Seconds>,
    pub dual_engine_exhaustion_time: Option<Seconds>,
}

impl PoweredFuelState {
    pub fn onboard_fuel(self) -> Kilograms {
        Kilograms(
            self.left_usable_feed.0
                + self.right_usable_feed.0
                + self.reserved_fuel.0
                + self.unusable_fuel.0,
        )
    }

    pub fn gross_mass(self) -> Kilograms {
        Kilograms(self.zero_fuel_weight.0 + self.onboard_fuel().0)
    }
}

/// Nominal fractions of the Martin two-engine flow assigned to each engine.
///
/// Fractions must be positive and sum to one. After one feed empties, the remaining
/// engine continues at its declared fraction; one-engine performance is not inferred.
#[derive(Debug, Clone, Copy, PartialEq, Serialize, Deserialize)]
pub struct EngineFuelFlowShares {
    pub left: f64,
    pub right: f64,
}

/// Caller-declared extension of the narrow Martin table.
///
/// No field below is estimated here. A run must record the selected values or their
/// upstream sampling distribution. Flow multipliers are bounded explicitly; hitting a
/// bound is reported so it cannot masquerade as physical precision.
#[derive(Debug, Clone, Copy, PartialEq, Serialize, Deserialize)]
pub struct DeclaredBroadFuelExtension {
    pub minimum_pressure_altitude: Feet,
    pub maximum_pressure_altitude: Feet,
    pub minimum_mach: f64,
    pub maximum_mach: f64,
    pub maximum_absolute_bank: Degrees,
    pub reference_mach: f64,
    pub nominal_flow_scale: f64,
    pub mach_log_sensitivity_per_mach: f64,
    pub below_fl350_log_sensitivity_per_1000_ft: f64,
    pub above_fl410_log_sensitivity_per_1000_ft: f64,
    pub bank_induced_drag_fraction: f64,
    pub climb_log_sensitivity_per_1000_ft_min: f64,
    pub descent_log_relief_per_1000_ft_min: f64,
    pub minimum_flow_multiplier: f64,
    pub maximum_flow_multiplier: f64,
}

#[derive(Debug, Clone, Copy, PartialEq, Serialize, Deserialize)]
#[serde(tag = "family", rename_all = "snake_case")]
pub enum PoweredFuelModel {
    /// Narrow altitude-table transcription. Other kinematics/weather are carried but
    /// not represented by its equation and are flagged in diagnostics.
    MartinTrent892Lrc,
    /// Sensitivity model based on the nearest Martin altitude row and declared
    /// multiplicative extensions for speed, bank, vertical motion, and altitude.
    DeclaredBroadExtension(DeclaredBroadFuelExtension),
}

#[derive(Debug, Clone, Copy, PartialEq, Serialize, Deserialize)]
pub struct PoweredFuelWeather {
    pub static_air_temperature_celsius: f64,
    pub air_density_kg_m3: f64,
}

/// One event-aligned dynamics segment represented at its midpoint.
#[derive(Debug, Clone, Copy, PartialEq, Serialize, Deserialize)]
pub struct PoweredFuelSegmentInput {
    pub start_time: Seconds,
    pub end_time: Seconds,
    pub midpoint_pressure_altitude: Feet,
    pub midpoint_mach: f64,
    pub midpoint_bank_angle: Degrees,
    pub midpoint_vertical_speed: FeetPerMinute,
    pub midpoint_weather: PoweredFuelWeather,
}

#[derive(Debug, Clone, Copy, PartialEq, Serialize, Deserialize)]
pub struct PoweredFuelStepDiagnostics {
    pub segment_duration: Seconds,
    pub start_gross_mass: Kilograms,
    pub end_gross_mass: Kilograms,
    pub left_burn: Kilograms,
    pub right_burn: Kilograms,
    pub total_burn: Kilograms,
    pub nominal_two_engine_flow_at_start: KilogramsPerSecond,
    pub nominal_two_engine_flow_at_end: KilogramsPerSecond,
    pub mass_balance_residual: Kilograms,
    pub evaluated_flow_multiplier: f64,
    pub flow_multiplier_limited: bool,
    pub outside_martin_domain_seconds: Seconds,
    pub outside_martin_domain_burn: Kilograms,
    pub strict_martin_kinematics_and_weather_unmodelled: bool,
    pub left_exhausted_in_segment: bool,
    pub right_exhausted_in_segment: bool,
    pub dual_engine_exhausted_in_segment: bool,
}

#[derive(Debug, Clone, Copy, PartialEq, Serialize, Deserialize)]
pub struct PoweredFuelStep {
    pub state: PoweredFuelState,
    pub diagnostics: PoweredFuelStepDiagnostics,
}

#[derive(Debug, Error, Clone, Copy, PartialEq)]
pub enum PoweredFuelError {
    #[error("{field} must be finite")]
    NonFinite { field: &'static str },
    #[error("{field} must be nonnegative")]
    Negative { field: &'static str },
    #[error("zero-fuel weight must be strictly positive")]
    NonPositiveZeroFuelWeight,
    #[error("segment start does not equal the current fuel-state time")]
    SegmentTimeMismatch,
    #[error("segment end must be later than its start")]
    NonPositiveSegmentDuration,
    #[error("engine flow shares must be positive and sum to one")]
    InvalidEngineFlowShares,
    #[error("fuel-model configuration is invalid")]
    InvalidModelConfiguration,
    #[error("operating point is outside the selected fuel-model domain")]
    OutsideModelDomain,
    #[error("fuel-flow arithmetic produced a non-finite or non-positive value")]
    InvalidFuelFlow,
    #[error("fuel propagation violated mass conservation")]
    MassConservationFailure,
}

#[derive(Debug, Clone, Copy)]
struct LinearFlowLaw {
    intercept_kg_s: f64,
    gross_mass_coefficient_s_inv: f64,
    multiplier: f64,
    multiplier_limited: bool,
    outside_martin_domain: bool,
    strict_unmodelled: bool,
}

fn finite(value: f64, field: &'static str) -> Result<(), PoweredFuelError> {
    if value.is_finite() {
        Ok(())
    } else {
        Err(PoweredFuelError::NonFinite { field })
    }
}

fn nonnegative(value: f64, field: &'static str) -> Result<(), PoweredFuelError> {
    finite(value, field)?;
    if value < 0.0 {
        Err(PoweredFuelError::Negative { field })
    } else {
        Ok(())
    }
}

pub(crate) fn validate_state(state: PoweredFuelState) -> Result<(), PoweredFuelError> {
    finite(state.time.0, "fuel-state time")?;
    nonnegative(state.zero_fuel_weight.0, "zero-fuel weight")?;
    if state.zero_fuel_weight.0 == 0.0 {
        return Err(PoweredFuelError::NonPositiveZeroFuelWeight);
    }
    for (value, field) in [
        (state.left_usable_feed.0, "left usable feed"),
        (state.right_usable_feed.0, "right usable feed"),
        (state.reserved_fuel.0, "reserved fuel"),
        (state.unusable_fuel.0, "unusable fuel"),
    ] {
        nonnegative(value, field)?;
    }
    for (time, field) in [
        (state.left_exhaustion_time, "left exhaustion time"),
        (state.right_exhaustion_time, "right exhaustion time"),
        (
            state.dual_engine_exhaustion_time,
            "dual-engine exhaustion time",
        ),
    ] {
        if let Some(time) = time {
            finite(time.0, field)?;
            if time.0 > state.time.0 + EVENT_TIME_TOLERANCE_S {
                return Err(PoweredFuelError::InvalidFuelFlow);
            }
        }
    }
    Ok(())
}

pub(crate) fn validate_segment(segment: PoweredFuelSegmentInput) -> Result<f64, PoweredFuelError> {
    for (value, field) in [
        (segment.start_time.0, "segment start time"),
        (segment.end_time.0, "segment end time"),
        (
            segment.midpoint_pressure_altitude.0,
            "midpoint pressure altitude",
        ),
        (segment.midpoint_mach, "midpoint Mach"),
        (segment.midpoint_bank_angle.0, "midpoint bank angle"),
        (segment.midpoint_vertical_speed.0, "midpoint vertical speed"),
        (
            segment.midpoint_weather.static_air_temperature_celsius,
            "midpoint static-air temperature",
        ),
        (
            segment.midpoint_weather.air_density_kg_m3,
            "midpoint air density",
        ),
    ] {
        finite(value, field)?;
    }
    if segment.midpoint_mach <= 0.0
        || segment.midpoint_weather.static_air_temperature_celsius <= -273.15
        || segment.midpoint_weather.air_density_kg_m3 <= 0.0
    {
        return Err(PoweredFuelError::OutsideModelDomain);
    }
    let duration = segment.end_time.0 - segment.start_time.0;
    if duration <= 0.0 {
        Err(PoweredFuelError::NonPositiveSegmentDuration)
    } else {
        Ok(duration)
    }
}

pub(crate) fn validate_shares(shares: EngineFuelFlowShares) -> Result<(), PoweredFuelError> {
    if !shares.left.is_finite()
        || !shares.right.is_finite()
        || shares.left <= 0.0
        || shares.right <= 0.0
        || (shares.left + shares.right - 1.0).abs() > 1.0e-12
    {
        Err(PoweredFuelError::InvalidEngineFlowShares)
    } else {
        Ok(())
    }
}

fn broad_configuration_valid(config: DeclaredBroadFuelExtension) -> bool {
    let values = [
        config.minimum_pressure_altitude.0,
        config.maximum_pressure_altitude.0,
        config.minimum_mach,
        config.maximum_mach,
        config.maximum_absolute_bank.0,
        config.reference_mach,
        config.nominal_flow_scale,
        config.mach_log_sensitivity_per_mach,
        config.below_fl350_log_sensitivity_per_1000_ft,
        config.above_fl410_log_sensitivity_per_1000_ft,
        config.bank_induced_drag_fraction,
        config.climb_log_sensitivity_per_1000_ft_min,
        config.descent_log_relief_per_1000_ft_min,
        config.minimum_flow_multiplier,
        config.maximum_flow_multiplier,
    ];
    values.iter().all(|value| value.is_finite())
        && config.minimum_pressure_altitude.0 < config.maximum_pressure_altitude.0
        && config.minimum_mach > 0.0
        && config.minimum_mach < config.maximum_mach
        && (0.0..90.0).contains(&config.maximum_absolute_bank.0)
        && config.reference_mach > 0.0
        && config.nominal_flow_scale > 0.0
        && config.bank_induced_drag_fraction >= 0.0
        && config.climb_log_sensitivity_per_1000_ft_min >= 0.0
        && config.descent_log_relief_per_1000_ft_min >= 0.0
        && config.minimum_flow_multiplier > 0.0
        && config.minimum_flow_multiplier <= config.maximum_flow_multiplier
}

fn scaled_coefficient(coefficient: MartinTrent892LrcCoefficient, multiplier: f64) -> LinearFlowLaw {
    LinearFlowLaw {
        intercept_kg_s: coefficient.intercept_kg_s * multiplier,
        gross_mass_coefficient_s_inv: coefficient.gross_mass_coefficient_s_inv * multiplier,
        multiplier,
        multiplier_limited: false,
        outside_martin_domain: false,
        strict_unmodelled: false,
    }
}

#[cfg(test)]
fn flow_law(
    model: PoweredFuelModel,
    segment: PoweredFuelSegmentInput,
) -> Result<LinearFlowLaw, PoweredFuelError> {
    flow_law_with_scale(model, segment, 1.0)
}

fn flow_law_with_scale(
    model: PoweredFuelModel,
    segment: PoweredFuelSegmentInput,
    particle_flow_scale: f64,
) -> Result<LinearFlowLaw, PoweredFuelError> {
    if !particle_flow_scale.is_finite() || particle_flow_scale <= 0.0 {
        return Err(PoweredFuelError::InvalidFuelFlow);
    }
    let altitude = segment.midpoint_pressure_altitude.0;
    match model {
        PoweredFuelModel::MartinTrent892Lrc => {
            let coefficient = martin_trent892_lrc_coefficient(altitude)
                .map_err(|_| PoweredFuelError::OutsideModelDomain)?;
            let mut law = scaled_coefficient(coefficient, particle_flow_scale);
            law.strict_unmodelled = true;
            Ok(law)
        }
        PoweredFuelModel::DeclaredBroadExtension(config) => {
            if !broad_configuration_valid(config) {
                return Err(PoweredFuelError::InvalidModelConfiguration);
            }
            if altitude < config.minimum_pressure_altitude.0
                || altitude > config.maximum_pressure_altitude.0
                || segment.midpoint_mach < config.minimum_mach
                || segment.midpoint_mach > config.maximum_mach
                || segment.midpoint_bank_angle.0.abs() > config.maximum_absolute_bank.0
            {
                return Err(PoweredFuelError::OutsideModelDomain);
            }
            let table_altitude = altitude.clamp(35_000.0, 41_000.0);
            let coefficient = martin_trent892_lrc_coefficient(table_altitude)
                .map_err(|_| PoweredFuelError::InvalidModelConfiguration)?;
            let below_kft = ((35_000.0 - altitude) / 1_000.0).max(0.0);
            let above_kft = ((altitude - 41_000.0) / 1_000.0).max(0.0);
            let climb_kft_min = (segment.midpoint_vertical_speed.0 / 1_000.0).max(0.0);
            let descent_kft_min = (-segment.midpoint_vertical_speed.0 / 1_000.0).max(0.0);
            let bank_radians = segment.midpoint_bank_angle.0.to_radians();
            let load_factor_squared = 1.0 / bank_radians.cos().powi(2);
            let bank_multiplier =
                1.0 + config.bank_induced_drag_fraction * (load_factor_squared - 1.0);
            let scaled_nominal_flow = config.nominal_flow_scale * particle_flow_scale;
            if !scaled_nominal_flow.is_finite() || scaled_nominal_flow <= 0.0 {
                return Err(PoweredFuelError::InvalidFuelFlow);
            }
            let log_multiplier = scaled_nominal_flow.ln()
                + config.mach_log_sensitivity_per_mach
                    * (segment.midpoint_mach - config.reference_mach)
                + config.below_fl350_log_sensitivity_per_1000_ft * below_kft
                + config.above_fl410_log_sensitivity_per_1000_ft * above_kft
                + config.climb_log_sensitivity_per_1000_ft_min * climb_kft_min
                - config.descent_log_relief_per_1000_ft_min * descent_kft_min
                + bank_multiplier.ln();
            let raw_multiplier = log_multiplier.exp();
            if !raw_multiplier.is_finite() || raw_multiplier <= 0.0 {
                return Err(PoweredFuelError::InvalidFuelFlow);
            }
            let multiplier = raw_multiplier.clamp(
                config.minimum_flow_multiplier,
                config.maximum_flow_multiplier,
            );
            let mut law = scaled_coefficient(coefficient, multiplier);
            law.multiplier_limited = multiplier != raw_multiplier;
            law.outside_martin_domain = !(35_000.0..=41_000.0).contains(&altitude);
            Ok(law)
        }
    }
}

fn exact_burn(law: LinearFlowLaw, gross_mass_kg: f64, active_share: f64, dt: f64) -> f64 {
    let a = law.intercept_kg_s;
    let b = law.gross_mass_coefficient_s_inv;
    let initial_flow = a + b * gross_mass_kg;
    if b.abs() < 1.0e-15 {
        active_share * initial_flow * dt
    } else {
        initial_flow / b * -(-b * active_share * dt).exp_m1()
    }
}

fn exact_time_for_burn(
    law: LinearFlowLaw,
    gross_mass_kg: f64,
    active_share: f64,
    burn_kg: f64,
) -> f64 {
    if burn_kg <= 0.0 {
        return 0.0;
    }
    let a = law.intercept_kg_s;
    let b = law.gross_mass_coefficient_s_inv;
    let initial_flow = a + b * gross_mass_kg;
    if b.abs() < 1.0e-15 {
        return burn_kg / (active_share * initial_flow);
    }
    let fraction = burn_kg * b / initial_flow;
    if fraction >= 1.0 {
        f64::INFINITY
    } else {
        -(-fraction).ln_1p() / (b * active_share)
    }
}

/// Advance a sampled fuel/feed state over one event-aligned powered-flight segment.
///
/// The flow law is evaluated at the caller's midpoint state. Within that segment the
/// linear mass ODE is solved analytically. If a feed empties, the step is split at its
/// exact analytic depletion time before propagation continues with the other engine.
pub fn advance_powered_fuel(
    state: &mut PoweredFuelState,
    model: PoweredFuelModel,
    shares: EngineFuelFlowShares,
    segment: PoweredFuelSegmentInput,
) -> Result<PoweredFuelStep, PoweredFuelError> {
    advance_powered_fuel_with_flow_scale(state, model, shares, segment, 1.0)
}

pub(crate) fn advance_powered_fuel_with_flow_scale(
    state: &mut PoweredFuelState,
    model: PoweredFuelModel,
    shares: EngineFuelFlowShares,
    segment: PoweredFuelSegmentInput,
    particle_flow_scale: f64,
) -> Result<PoweredFuelStep, PoweredFuelError> {
    let mut working = *state;
    let result =
        advance_powered_fuel_in_place(&mut working, model, shares, segment, particle_flow_scale)?;
    *state = working;
    Ok(result)
}

fn advance_powered_fuel_in_place(
    state: &mut PoweredFuelState,
    model: PoweredFuelModel,
    shares: EngineFuelFlowShares,
    segment: PoweredFuelSegmentInput,
    particle_flow_scale: f64,
) -> Result<PoweredFuelStep, PoweredFuelError> {
    validate_state(*state)?;
    validate_shares(shares)?;
    let duration = validate_segment(segment)?;
    if (state.time.0 - segment.start_time.0).abs() > EVENT_TIME_TOLERANCE_S {
        return Err(PoweredFuelError::SegmentTimeMismatch);
    }

    let initial = *state;
    let start_mass = state.gross_mass().0;
    let start_left = state.left_usable_feed.0;
    let start_right = state.right_usable_feed.0;
    let mut left_new_event = false;
    let mut right_new_event = false;

    if state.left_usable_feed.0 <= MASS_TOLERANCE_KG && state.left_exhaustion_time.is_none() {
        state.left_usable_feed.0 = 0.0;
        state.left_exhaustion_time = Some(segment.start_time);
        left_new_event = true;
    }
    if state.right_usable_feed.0 <= MASS_TOLERANCE_KG && state.right_exhaustion_time.is_none() {
        state.right_usable_feed.0 = 0.0;
        state.right_exhaustion_time = Some(segment.start_time);
        right_new_event = true;
    }
    if state.left_exhaustion_time.is_some()
        && state.right_exhaustion_time.is_some()
        && state.dual_engine_exhaustion_time.is_none()
    {
        state.dual_engine_exhaustion_time = Some(segment.start_time);
    }

    let law = flow_law_with_scale(model, segment, particle_flow_scale)?;
    let initial_nominal_flow =
        law.intercept_kg_s + law.gross_mass_coefficient_s_inv * state.gross_mass().0;
    if !initial_nominal_flow.is_finite() || initial_nominal_flow <= 0.0 {
        return Err(PoweredFuelError::InvalidFuelFlow);
    }

    let mut remaining = duration;
    while remaining > EVENT_TIME_TOLERANCE_S
        && (state.left_usable_feed.0 > 0.0 || state.right_usable_feed.0 > 0.0)
    {
        let left_active = state.left_usable_feed.0 > 0.0;
        let right_active = state.right_usable_feed.0 > 0.0;
        let active_share = if left_active { shares.left } else { 0.0 }
            + if right_active { shares.right } else { 0.0 };
        let gross_mass = state.gross_mass().0;
        let left_time = if left_active {
            exact_time_for_burn(
                law,
                gross_mass,
                active_share,
                state.left_usable_feed.0 * active_share / shares.left,
            )
        } else {
            f64::INFINITY
        };
        let right_time = if right_active {
            exact_time_for_burn(
                law,
                gross_mass,
                active_share,
                state.right_usable_feed.0 * active_share / shares.right,
            )
        } else {
            f64::INFINITY
        };
        let event_time = left_time.min(right_time);
        let advance = remaining.min(event_time);
        let burn = exact_burn(law, gross_mass, active_share, advance);
        if !burn.is_finite() || burn < 0.0 {
            return Err(PoweredFuelError::InvalidFuelFlow);
        }
        if left_active {
            state.left_usable_feed.0 -= burn * shares.left / active_share;
        }
        if right_active {
            state.right_usable_feed.0 -= burn * shares.right / active_share;
        }
        state.time.0 += advance;
        remaining -= advance;

        if event_time <= advance + EVENT_TIME_TOLERANCE_S {
            if left_active && (left_time - event_time).abs() <= EVENT_TIME_TOLERANCE_S {
                state.left_usable_feed.0 = 0.0;
                state.left_exhaustion_time = Some(state.time);
                left_new_event = true;
            }
            if right_active && (right_time - event_time).abs() <= EVENT_TIME_TOLERANCE_S {
                state.right_usable_feed.0 = 0.0;
                state.right_exhaustion_time = Some(state.time);
                right_new_event = true;
            }
            if state.left_exhaustion_time.is_some()
                && state.right_exhaustion_time.is_some()
                && state.dual_engine_exhaustion_time.is_none()
            {
                state.dual_engine_exhaustion_time = Some(state.time);
            }
        } else {
            break;
        }
    }
    state.time = segment.end_time;
    if state.left_usable_feed.0.abs() <= MASS_TOLERANCE_KG {
        state.left_usable_feed.0 = 0.0;
    }
    if state.right_usable_feed.0.abs() <= MASS_TOLERANCE_KG {
        state.right_usable_feed.0 = 0.0;
    }
    validate_state(*state)?;

    let left_burn = start_left - state.left_usable_feed.0;
    let right_burn = start_right - state.right_usable_feed.0;
    let total_burn = left_burn + right_burn;
    let end_mass = state.gross_mass().0;
    let end_nominal_flow =
        law.intercept_kg_s + law.gross_mass_coefficient_s_inv * state.gross_mass().0;
    let residual = start_mass - end_mass - total_burn;
    if !residual.is_finite() || residual.abs() > MASS_TOLERANCE_KG {
        *state = initial;
        return Err(PoweredFuelError::MassConservationFailure);
    }
    let dual_new_event = initial.dual_engine_exhaustion_time.is_none()
        && state.dual_engine_exhaustion_time.is_some();
    let outside_seconds = if law.outside_martin_domain {
        duration
    } else {
        0.0
    };
    Ok(PoweredFuelStep {
        state: *state,
        diagnostics: PoweredFuelStepDiagnostics {
            segment_duration: Seconds(duration),
            start_gross_mass: Kilograms(start_mass),
            end_gross_mass: Kilograms(end_mass),
            left_burn: Kilograms(left_burn),
            right_burn: Kilograms(right_burn),
            total_burn: Kilograms(total_burn),
            nominal_two_engine_flow_at_start: KilogramsPerSecond(initial_nominal_flow),
            nominal_two_engine_flow_at_end: KilogramsPerSecond(end_nominal_flow),
            mass_balance_residual: Kilograms(residual),
            evaluated_flow_multiplier: law.multiplier,
            flow_multiplier_limited: law.multiplier_limited,
            outside_martin_domain_seconds: Seconds(outside_seconds),
            outside_martin_domain_burn: Kilograms(if law.outside_martin_domain {
                total_burn
            } else {
                0.0
            }),
            strict_martin_kinematics_and_weather_unmodelled: law.strict_unmodelled,
            left_exhausted_in_segment: left_new_event,
            right_exhausted_in_segment: right_new_event,
            dual_engine_exhausted_in_segment: dual_new_event,
        },
    })
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::project_martin_trent892_lrc_fuel;

    fn state(left: f64, right: f64) -> PoweredFuelState {
        PoweredFuelState {
            time: Seconds(0.0),
            zero_fuel_weight: Kilograms(174_369.0),
            left_usable_feed: Kilograms(left),
            right_usable_feed: Kilograms(right),
            reserved_fuel: Kilograms(0.0),
            unusable_fuel: Kilograms(0.0),
            left_exhaustion_time: None,
            right_exhaustion_time: None,
            dual_engine_exhaustion_time: None,
        }
    }

    fn segment(start: f64, end: f64, altitude: f64) -> PoweredFuelSegmentInput {
        PoweredFuelSegmentInput {
            start_time: Seconds(start),
            end_time: Seconds(end),
            midpoint_pressure_altitude: Feet(altitude),
            midpoint_mach: 0.82,
            midpoint_bank_angle: Degrees(0.0),
            midpoint_vertical_speed: FeetPerMinute(0.0),
            midpoint_weather: PoweredFuelWeather {
                static_air_temperature_celsius: -45.0,
                air_density_kg_m3: 0.38,
            },
        }
    }

    fn shares() -> EngineFuelFlowShares {
        EngineFuelFlowShares {
            left: 0.5,
            right: 0.5,
        }
    }

    fn broad() -> PoweredFuelModel {
        PoweredFuelModel::DeclaredBroadExtension(DeclaredBroadFuelExtension {
            minimum_pressure_altitude: Feet(25_000.0),
            maximum_pressure_altitude: Feet(43_000.0),
            minimum_mach: 0.70,
            maximum_mach: 0.88,
            maximum_absolute_bank: Degrees(45.0),
            reference_mach: 0.82,
            nominal_flow_scale: 1.0,
            mach_log_sensitivity_per_mach: 1.5,
            below_fl350_log_sensitivity_per_1000_ft: 0.04,
            above_fl410_log_sensitivity_per_1000_ft: 0.02,
            bank_induced_drag_fraction: 0.45,
            climb_log_sensitivity_per_1000_ft_min: 0.04,
            descent_log_relief_per_1000_ft_min: 0.015,
            minimum_flow_multiplier: 0.5,
            maximum_flow_multiplier: 2.5,
        })
    }

    #[test]
    fn exact_constant_fl350_projection_matches_existing_independent_solution() {
        let initial_fuel = 33_524.104_881_96;
        let elapsed = 3_600.0;
        let expected =
            project_martin_trent892_lrc_fuel(174_369.0, initial_fuel, 35_000.0, elapsed).unwrap();
        let mut fuel = state(initial_fuel / 2.0, initial_fuel / 2.0);
        let step = advance_powered_fuel(
            &mut fuel,
            PoweredFuelModel::MartinTrent892Lrc,
            shares(),
            segment(0.0, elapsed, 35_000.0),
        )
        .unwrap();
        assert!((fuel.onboard_fuel().0 - expected.end_total_fuel.0).abs() < 1.0e-8);
        assert!(step.diagnostics.mass_balance_residual.0.abs() < 1.0e-10);
        assert!(
            step.diagnostics
                .strict_martin_kinematics_and_weather_unmodelled
        );
    }

    #[test]
    fn feed_exhaustion_time_is_exact_and_independent_of_outer_cadence() {
        fn run(step_seconds: f64) -> PoweredFuelState {
            let mut fuel = state(30.0, 70.0);
            while fuel.time.0 < 300.0 && fuel.dual_engine_exhaustion_time.is_none() {
                let end = (fuel.time.0 + step_seconds).min(300.0);
                let start = fuel.time.0;
                advance_powered_fuel(
                    &mut fuel,
                    PoweredFuelModel::MartinTrent892Lrc,
                    shares(),
                    segment(start, end, 35_000.0),
                )
                .unwrap();
            }
            fuel
        }
        let coarse = run(300.0);
        let fine = run(15.0);
        assert!(
            (coarse.left_exhaustion_time.unwrap().0 - fine.left_exhaustion_time.unwrap().0).abs()
                < 1.0e-8
        );
        assert!(
            (coarse.dual_engine_exhaustion_time.unwrap().0
                - fine.dual_engine_exhaustion_time.unwrap().0)
                .abs()
                < 1.0e-8
        );
        assert_eq!(coarse.left_usable_feed, Kilograms(0.0));
        assert_eq!(coarse.right_usable_feed, Kilograms(0.0));
    }

    #[test]
    fn declared_extension_reports_outside_table_reliance_and_conserves_mass() {
        let mut fuel = state(10_000.0, 10_000.0);
        let before = fuel.gross_mass().0;
        let result =
            advance_powered_fuel(&mut fuel, broad(), shares(), segment(0.0, 60.0, 30_000.0))
                .unwrap();
        assert_eq!(
            result.diagnostics.outside_martin_domain_seconds,
            Seconds(60.0)
        );
        assert!(result.diagnostics.outside_martin_domain_burn.0 > 0.0);
        assert!((before - fuel.gross_mass().0 - result.diagnostics.total_burn.0).abs() < 1.0e-8);

        let mut strict = state(10_000.0, 10_000.0);
        assert_eq!(
            advance_powered_fuel(
                &mut strict,
                PoweredFuelModel::MartinTrent892Lrc,
                shares(),
                segment(0.0, 60.0, 30_000.0),
            ),
            Err(PoweredFuelError::OutsideModelDomain)
        );
    }

    #[test]
    fn midpoint_cadence_60_30_15_seconds_converges_for_smooth_varying_path() {
        fn run(dt: f64) -> f64 {
            let mut fuel = state(20_000.0, 20_000.0);
            while fuel.time.0 < 3_600.0 {
                let start = fuel.time.0;
                let end = (start + dt).min(3_600.0);
                let midpoint = 0.5 * (start + end);
                let mut input = segment(start, end, 34_000.0 + 2_000.0 * (midpoint / 3_600.0));
                input.midpoint_mach = 0.78 + 0.06 * (midpoint / 3_600.0);
                input.midpoint_bank_angle = Degrees(12.0 * (midpoint / 600.0).sin());
                input.midpoint_vertical_speed = FeetPerMinute(2_000.0 / 60.0);
                advance_powered_fuel(&mut fuel, broad(), shares(), input).unwrap();
            }
            40_000.0 - fuel.left_usable_feed.0 - fuel.right_usable_feed.0
        }
        let burn_60 = run(60.0);
        let burn_30 = run(30.0);
        let burn_15 = run(15.0);
        assert!((burn_60 - burn_15).abs() < 0.05);
        assert!((burn_30 - burn_15).abs() < (burn_60 - burn_15).abs());
    }

    #[test]
    fn declared_climb_sensitivity_is_applied_exactly_once() {
        let PoweredFuelModel::DeclaredBroadExtension(mut config) = broad() else {
            unreachable!("broad fixture is the declared extension")
        };
        config.mach_log_sensitivity_per_mach = 0.0;
        config.below_fl350_log_sensitivity_per_1000_ft = 0.0;
        config.above_fl410_log_sensitivity_per_1000_ft = 0.0;
        config.bank_induced_drag_fraction = 0.0;
        config.climb_log_sensitivity_per_1000_ft_min = 0.1;
        config.descent_log_relief_per_1000_ft_min = 0.0;
        config.minimum_flow_multiplier = 0.1;
        config.maximum_flow_multiplier = 10.0;

        let mut input = segment(0.0, 60.0, 35_000.0);
        input.midpoint_vertical_speed = FeetPerMinute(2_000.0);
        let law = flow_law(PoweredFuelModel::DeclaredBroadExtension(config), input).unwrap();
        assert!((law.multiplier - 0.2_f64.exp()).abs() < 1.0e-14);
        assert!(!law.multiplier_limited);
    }

    #[test]
    fn invalid_domain_and_shares_are_typed_particle_rejections() {
        let mut fuel = state(1_000.0, 1_000.0);
        assert_eq!(
            advance_powered_fuel(
                &mut fuel,
                broad(),
                EngineFuelFlowShares {
                    left: 0.7,
                    right: 0.4
                },
                segment(0.0, 60.0, 35_000.0),
            ),
            Err(PoweredFuelError::InvalidEngineFlowShares)
        );
        let mut fuel = state(1_000.0, 1_000.0);
        let mut input = segment(0.0, 60.0, 35_000.0);
        input.midpoint_mach = 0.95;
        assert_eq!(
            advance_powered_fuel(&mut fuel, broad(), shares(), input),
            Err(PoweredFuelError::OutsideModelDomain)
        );
    }
}
