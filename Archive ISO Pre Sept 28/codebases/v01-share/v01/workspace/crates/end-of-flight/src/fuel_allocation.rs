//! Deterministic allocation of a caller-supplied powered-flight fuel total.
//!
//! This module does not estimate fuel, choose a flameout chronology, or assign a
//! probability. It only converts one explicitly selected total and feed-timing
//! scenario into the state types consumed by the end-of-flight transition kernel.

use mh370_domain::Seconds;
use serde::{Deserialize, Serialize};
use thiserror::Error;

use crate::{
    EngineMode, EngineSide, EngineState, EngineSystemState, FuelState, Kilograms,
    KilogramsPerSecond, MassState, Newtons,
};

/// Caller-selected relationship between the two constant-flow feed endurances.
#[derive(Debug, Clone, Copy, PartialEq, Serialize, Deserialize)]
#[serde(tag = "mode", content = "lead", rename_all = "snake_case")]
pub enum EffectiveFeedTiming {
    /// Both effective engine feeds reach zero at the same elapsed time.
    EqualEndurance,
    /// The left effective feed reaches zero this many seconds before the right.
    LeftFirstBy(Seconds),
    /// The right effective feed reaches zero this many seconds before the left.
    RightFirstBy(Seconds),
}

/// Physical inputs for one deterministic powered-flight allocation scenario.
#[derive(Debug, Clone, Copy, PartialEq, Serialize, Deserialize)]
pub struct PoweredFuelAllocationInput {
    pub zero_fuel_weight: Kilograms,
    pub total_onboard_fuel: Kilograms,
    pub apu_reserved_fuel: Kilograms,
    pub inaccessible_reported_fuel: Kilograms,
    pub left_fuel_flow: KilogramsPerSecond,
    pub right_fuel_flow: KilogramsPerSecond,
    pub left_thrust: Newtons,
    pub right_thrust: Newtons,
    pub left_generator_online: bool,
    pub right_generator_online: bool,
    pub effective_feed_timing: EffectiveFeedTiming,
}

/// Auditable mass-conservation quantities produced by the allocation.
#[derive(Debug, Clone, Copy, PartialEq, Serialize, Deserialize)]
pub struct PoweredFuelAllocationDiagnostics {
    /// Fuel available to the two engine feeds after the declared exclusions.
    pub accessible_engine_fuel: Kilograms,
    /// Sum of the allocated left and right effective feeds.
    pub allocated_engine_fuel: Kilograms,
    /// Sum of both engine feeds, the APU reserve, and inaccessible fuel.
    pub partitioned_onboard_fuel: Kilograms,
    /// Reported total minus the partitioned total; zero apart from roundoff.
    pub fuel_partition_residual: Kilograms,
    /// Zero-fuel weight plus the caller-supplied reported onboard fuel.
    pub gross_mass: Kilograms,
}

/// Kernel-ready powered state and the exact constant-flow endurance it represents.
#[derive(Debug, Clone, Copy, PartialEq, Serialize, Deserialize)]
pub struct PoweredFuelAllocation {
    pub mass: MassState,
    pub fuel: FuelState,
    pub engines: EngineSystemState,
    pub left_endurance: Seconds,
    pub right_endurance: Seconds,
    pub diagnostics: PoweredFuelAllocationDiagnostics,
}

#[derive(Debug, Clone, Copy, PartialEq, Error)]
pub enum PoweredFuelAllocationError {
    #[error("{field} must be finite")]
    NonFinite { field: &'static str },
    #[error("{field} must be nonnegative")]
    Negative { field: &'static str },
    #[error("zero-fuel weight must be strictly positive")]
    NonPositiveZeroFuelWeight,
    #[error("{engine:?} engine fuel flow must be strictly positive")]
    NonPositiveFuelFlow { engine: EngineSide },
    #[error("APU reserve plus inaccessible fuel exceeds reported onboard fuel")]
    FuelPartitionExceedsReportedTotal,
    #[error("no fuel remains accessible to the engine feeds")]
    NoAccessibleEngineFuel,
    #[error(
        "requested {first:?}-engine flameout lead of {lead_seconds} s exceeds the {maximum_seconds} s feasible maximum"
    )]
    InfeasibleFlameoutLead {
        first: EngineSide,
        lead_seconds: f64,
        maximum_seconds: f64,
    },
    #[error("allocation arithmetic produced a non-finite value")]
    NonFiniteAllocation,
}

fn require_nonnegative_finite(
    value: f64,
    field: &'static str,
) -> Result<(), PoweredFuelAllocationError> {
    if !value.is_finite() {
        return Err(PoweredFuelAllocationError::NonFinite { field });
    }
    if value < 0.0 {
        return Err(PoweredFuelAllocationError::Negative { field });
    }
    Ok(())
}

fn require_positive_flow(
    value: KilogramsPerSecond,
    engine: EngineSide,
) -> Result<(), PoweredFuelAllocationError> {
    let field = match engine {
        EngineSide::Left => "left fuel flow",
        EngineSide::Right => "right fuel flow",
    };
    require_nonnegative_finite(value.0, field)?;
    if value.0 == 0.0 {
        return Err(PoweredFuelAllocationError::NonPositiveFuelFlow { engine });
    }
    Ok(())
}

fn validate_lead(lead: Seconds, first: EngineSide) -> Result<f64, PoweredFuelAllocationError> {
    let field = match first {
        EngineSide::Left => "left-first lead",
        EngineSide::Right => "right-first lead",
    };
    require_nonnegative_finite(lead.0, field)?;
    Ok(lead.0)
}

/// Allocate a reported fuel total into kernel feed states without assigning a weight.
pub fn allocate_powered_fuel(
    input: PoweredFuelAllocationInput,
) -> Result<PoweredFuelAllocation, PoweredFuelAllocationError> {
    for (value, field) in [
        (input.zero_fuel_weight.0, "zero-fuel weight"),
        (input.total_onboard_fuel.0, "total onboard fuel"),
        (input.apu_reserved_fuel.0, "APU reserved fuel"),
        (
            input.inaccessible_reported_fuel.0,
            "inaccessible reported fuel",
        ),
        (input.left_thrust.0, "left thrust"),
        (input.right_thrust.0, "right thrust"),
    ] {
        require_nonnegative_finite(value, field)?;
    }
    if input.zero_fuel_weight.0 == 0.0 {
        return Err(PoweredFuelAllocationError::NonPositiveZeroFuelWeight);
    }
    require_positive_flow(input.left_fuel_flow, EngineSide::Left)?;
    require_positive_flow(input.right_fuel_flow, EngineSide::Right)?;

    let excluded_fuel = input.apu_reserved_fuel.0 + input.inaccessible_reported_fuel.0;
    if !excluded_fuel.is_finite() {
        return Err(PoweredFuelAllocationError::NonFiniteAllocation);
    }
    if excluded_fuel > input.total_onboard_fuel.0 {
        return Err(PoweredFuelAllocationError::FuelPartitionExceedsReportedTotal);
    }
    let accessible = input.total_onboard_fuel.0 - excluded_fuel;
    if accessible == 0.0 {
        return Err(PoweredFuelAllocationError::NoAccessibleEngineFuel);
    }

    let left_flow = input.left_fuel_flow.0;
    let right_flow = input.right_fuel_flow.0;
    let combined_flow = left_flow + right_flow;
    if !combined_flow.is_finite() {
        return Err(PoweredFuelAllocationError::NonFiniteAllocation);
    }

    let left_feed = match input.effective_feed_timing {
        EffectiveFeedTiming::EqualEndurance => accessible * left_flow / combined_flow,
        EffectiveFeedTiming::LeftFirstBy(lead) => {
            let lead_seconds = validate_lead(lead, EngineSide::Left)?;
            let maximum_seconds = accessible / right_flow;
            if lead_seconds > maximum_seconds {
                return Err(PoweredFuelAllocationError::InfeasibleFlameoutLead {
                    first: EngineSide::Left,
                    lead_seconds,
                    maximum_seconds,
                });
            }
            left_flow * (accessible - right_flow * lead_seconds) / combined_flow
        }
        EffectiveFeedTiming::RightFirstBy(lead) => {
            let lead_seconds = validate_lead(lead, EngineSide::Right)?;
            let maximum_seconds = accessible / left_flow;
            if lead_seconds > maximum_seconds {
                return Err(PoweredFuelAllocationError::InfeasibleFlameoutLead {
                    first: EngineSide::Right,
                    lead_seconds,
                    maximum_seconds,
                });
            }
            // The left engine is the later engine in this scenario.
            left_flow * (accessible + right_flow * lead_seconds) / combined_flow
        }
    };
    // Construct one side as the exact remainder so the reported total is conserved.
    let right_feed = accessible - left_feed;
    let left_endurance = left_feed / left_flow;
    let right_endurance = right_feed / right_flow;
    let values = [
        accessible,
        left_feed,
        right_feed,
        left_endurance,
        right_endurance,
    ];
    if values
        .iter()
        .any(|value| !value.is_finite() || *value < 0.0)
    {
        return Err(PoweredFuelAllocationError::NonFiniteAllocation);
    }

    let fuel = FuelState {
        left_engine_feed: Kilograms(left_feed),
        right_engine_feed: Kilograms(right_feed),
        apu_feed: input.apu_reserved_fuel,
        unusable: input.inaccessible_reported_fuel,
    };
    let allocated_engine_fuel = fuel.left_engine_feed.0 + fuel.right_engine_feed.0;
    let partitioned_onboard_fuel = fuel.total_mass().0;
    let gross_mass = input.zero_fuel_weight.0 + input.total_onboard_fuel.0;
    if [allocated_engine_fuel, partitioned_onboard_fuel, gross_mass]
        .iter()
        .any(|value| !value.is_finite())
    {
        return Err(PoweredFuelAllocationError::NonFiniteAllocation);
    }

    Ok(PoweredFuelAllocation {
        mass: MassState {
            non_fuel_mass: input.zero_fuel_weight,
        },
        fuel,
        engines: EngineSystemState {
            left: EngineState {
                mode: EngineMode::Running,
                thrust: input.left_thrust,
                fuel_flow: input.left_fuel_flow,
                generator_online: input.left_generator_online,
            },
            right: EngineState {
                mode: EngineMode::Running,
                thrust: input.right_thrust,
                fuel_flow: input.right_fuel_flow,
                generator_online: input.right_generator_online,
            },
        },
        left_endurance: Seconds(left_endurance),
        right_endurance: Seconds(right_endurance),
        diagnostics: PoweredFuelAllocationDiagnostics {
            accessible_engine_fuel: Kilograms(accessible),
            allocated_engine_fuel: Kilograms(allocated_engine_fuel),
            partitioned_onboard_fuel: Kilograms(partitioned_onboard_fuel),
            fuel_partition_residual: Kilograms(
                input.total_onboard_fuel.0 - partitioned_onboard_fuel,
            ),
            gross_mass: Kilograms(gross_mass),
        },
    })
}

#[cfg(test)]
mod tests {
    use mh370_domain::{Degrees, Feet, LatLon};

    use super::*;
    use crate::{
        propagate_transition, AerodynamicModel, ApuMode, ApuStartPolicy, ApuState, AtmosphereNode,
        AtmosphereProfile, ConditionalModelFamily, ControlCommand, ControlFamily, ControlSchedule,
        ControlSegment, ElectricalSource, ElectricalSystemState, IntegrationSettings,
        KilogramsPerCubicMetre, MetresPerSecond, ModelWeight, OcxoPowerState, OcxoState,
        PointMassState, RestartTransientFamily, SquareMetres, TransitionEventKind,
        TransitionInitialCondition, TransitionKernelInput,
    };

    const EPSILON: f64 = 1.0e-9;

    fn close(actual: f64, expected: f64) {
        assert!(
            (actual - expected).abs() <= EPSILON,
            "{actual} != {expected}"
        );
    }

    fn allocation_input(timing: EffectiveFeedTiming) -> PoweredFuelAllocationInput {
        PoweredFuelAllocationInput {
            zero_fuel_weight: Kilograms(174_369.0),
            total_onboard_fuel: Kilograms(43_800.0),
            apu_reserved_fuel: Kilograms(400.0),
            inaccessible_reported_fuel: Kilograms(200.0),
            left_fuel_flow: KilogramsPerSecond(0.8),
            right_fuel_flow: KilogramsPerSecond(1.2),
            left_thrust: Newtons(30_000.0),
            right_thrust: Newtons(31_000.0),
            left_generator_online: true,
            right_generator_online: true,
            effective_feed_timing: timing,
        }
    }

    #[test]
    fn official_acars_total_and_arc_one_total_preserve_gross_mass() {
        let acars =
            allocate_powered_fuel(allocation_input(EffectiveFeedTiming::EqualEndurance)).unwrap();
        close(acars.diagnostics.gross_mass.0, 218_169.0);
        close(acars.fuel.total_mass().0, 43_800.0);

        let mut arc_one_input = allocation_input(EffectiveFeedTiming::EqualEndurance);
        arc_one_input.total_onboard_fuel = Kilograms(33_524.104_881_96);
        let arc_one = allocate_powered_fuel(arc_one_input).unwrap();
        close(arc_one.fuel.total_mass().0, 33_524.104_881_96);
        close(arc_one.diagnostics.gross_mass.0, 207_893.104_881_96);
    }

    #[test]
    fn equal_endurance_with_unequal_flows_is_exact_and_conservative() {
        let allocation =
            allocate_powered_fuel(allocation_input(EffectiveFeedTiming::EqualEndurance)).unwrap();
        close(allocation.left_endurance.0, allocation.right_endurance.0);
        close(
            allocation.fuel.left_engine_feed.0 / allocation.fuel.right_engine_feed.0,
            0.8 / 1.2,
        );
        close(allocation.diagnostics.accessible_engine_fuel.0, 43_200.0);
        close(allocation.diagnostics.allocated_engine_fuel.0, 43_200.0);
        close(allocation.diagnostics.partitioned_onboard_fuel.0, 43_800.0);
        close(allocation.diagnostics.fuel_partition_residual.0, 0.0);
    }

    #[test]
    fn requested_sixty_second_leads_are_exact_in_both_directions() {
        for (timing, first) in [
            (
                EffectiveFeedTiming::LeftFirstBy(Seconds(60.0)),
                EngineSide::Left,
            ),
            (
                EffectiveFeedTiming::RightFirstBy(Seconds(60.0)),
                EngineSide::Right,
            ),
        ] {
            let allocation = allocate_powered_fuel(allocation_input(timing)).unwrap();
            let lead = match first {
                EngineSide::Left => allocation.right_endurance.0 - allocation.left_endurance.0,
                EngineSide::Right => allocation.left_endurance.0 - allocation.right_endurance.0,
            };
            close(lead, 60.0);
            close(allocation.fuel.total_mass().0, 43_800.0);
        }
    }

    #[test]
    fn impossible_or_invalid_inputs_are_rejected() {
        let mut input = allocation_input(EffectiveFeedTiming::EqualEndurance);
        input.left_fuel_flow = KilogramsPerSecond(0.0);
        assert_eq!(
            allocate_powered_fuel(input),
            Err(PoweredFuelAllocationError::NonPositiveFuelFlow {
                engine: EngineSide::Left
            })
        );

        let mut input = allocation_input(EffectiveFeedTiming::EqualEndurance);
        input.total_onboard_fuel = Kilograms(500.0);
        assert_eq!(
            allocate_powered_fuel(input),
            Err(PoweredFuelAllocationError::FuelPartitionExceedsReportedTotal)
        );

        let mut input = allocation_input(EffectiveFeedTiming::EqualEndurance);
        input.left_thrust = Newtons(f64::NAN);
        assert_eq!(
            allocate_powered_fuel(input),
            Err(PoweredFuelAllocationError::NonFinite {
                field: "left thrust"
            })
        );

        let mut input = allocation_input(EffectiveFeedTiming::LeftFirstBy(Seconds(50_000.0)));
        input.total_onboard_fuel = Kilograms(10.0);
        input.apu_reserved_fuel = Kilograms(0.0);
        input.inaccessible_reported_fuel = Kilograms(0.0);
        assert!(matches!(
            allocate_powered_fuel(input),
            Err(PoweredFuelAllocationError::InfeasibleFlameoutLead {
                first: EngineSide::Left,
                ..
            })
        ));

        let mut input = allocation_input(EffectiveFeedTiming::RightFirstBy(Seconds(-1.0)));
        input.apu_reserved_fuel = Kilograms(-1.0);
        assert_eq!(
            allocate_powered_fuel(input),
            Err(PoweredFuelAllocationError::Negative {
                field: "APU reserved fuel"
            })
        );
    }

    fn kernel_input(timing: EffectiveFeedTiming) -> TransitionKernelInput {
        let allocation = allocate_powered_fuel(PoweredFuelAllocationInput {
            zero_fuel_weight: Kilograms(10_000.0),
            total_onboard_fuel: Kilograms(6.0),
            apu_reserved_fuel: Kilograms(0.0),
            inaccessible_reported_fuel: Kilograms(0.0),
            left_fuel_flow: KilogramsPerSecond(1.0),
            right_fuel_flow: KilogramsPerSecond(1.0),
            left_thrust: Newtons(10_000.0),
            right_thrust: Newtons(10_000.0),
            left_generator_online: true,
            right_generator_online: true,
            effective_feed_timing: timing,
        })
        .unwrap();
        let density = 1.225;
        let speed: f64 = 100.0;
        let area = 100.0;
        let dynamic_pressure_area = 0.5 * density * speed.powi(2) * area;
        let lift_coefficient =
            allocation.diagnostics.gross_mass.0 * 9.806_65 / dynamic_pressure_area;

        TransitionKernelInput {
            initial: TransitionInitialCondition {
                flight: PointMassState {
                    time: Seconds(100.0),
                    position: LatLon::new(-35.0, 90.0).unwrap(),
                    altitude: Feet(10_000.0),
                    true_airspeed: MetresPerSecond(speed),
                    flight_path_angle: Degrees(0.0),
                    heading_true: Degrees(90.0),
                },
                mass: allocation.mass,
                fuel: allocation.fuel,
                engines: allocation.engines,
                electrical: ElectricalSystemState {
                    source: ElectricalSource::EngineGenerators,
                    satcom_powered: true,
                    dual_engine_generator_loss_elapsed: None,
                },
                apu: ApuState {
                    mode: ApuMode::Off,
                    elapsed_in_mode: Seconds(0.0),
                    generator_online: false,
                    fuel_flow: KilogramsPerSecond(0.0),
                },
                ocxo: OcxoState {
                    power: OcxoPowerState::Powered,
                    unpowered_duration: Seconds(0.0),
                    restart_count: 0,
                },
            },
            family: ConditionalModelFamily {
                control: ControlFamily::Uncontrolled,
                restart_transient: RestartTransientFamily::NoAdditionalTransient,
            },
            model_weight: ModelWeight(1.0),
            control: ControlSchedule {
                segments: vec![ControlSegment {
                    start_offset: Seconds(0.0),
                    command: ControlCommand::Uncontrolled {
                        lift_coefficient,
                        bank_angle: Degrees(0.0),
                    },
                }],
            },
            aerodynamics: AerodynamicModel {
                reference_area: SquareMetres(area),
                zero_lift_drag_coefficient: 0.02,
                induced_drag_factor: 0.0,
                minimum_lift_coefficient: -1.0,
                maximum_lift_coefficient: 2.0,
                maximum_bank_angle: Degrees(60.0),
                minimum_true_airspeed: MetresPerSecond(20.0),
                maximum_true_airspeed: MetresPerSecond(300.0),
            },
            atmosphere: AtmosphereProfile {
                nodes: vec![AtmosphereNode {
                    altitude: Feet(0.0),
                    density: KilogramsPerCubicMetre(density),
                    wind_north: MetresPerSecond(0.0),
                    wind_east: MetresPerSecond(0.0),
                }],
            },
            apu_start_policy: ApuStartPolicy::Disabled,
            integration: IntegrationSettings {
                time_step: Seconds(0.7),
                maximum_duration: Seconds(5.0),
                sea_surface_altitude: Feet(0.0),
                maximum_steps: 100,
            },
        }
    }

    #[test]
    fn kernel_emits_the_allocated_flameout_order_and_exact_times() {
        for (timing, first, second) in [
            (
                EffectiveFeedTiming::LeftFirstBy(Seconds(2.0)),
                EngineSide::Left,
                EngineSide::Right,
            ),
            (
                EffectiveFeedTiming::RightFirstBy(Seconds(2.0)),
                EngineSide::Right,
                EngineSide::Left,
            ),
        ] {
            let input = kernel_input(timing);
            let transition = propagate_transition(&input).unwrap();
            let flameouts: Vec<_> = transition
                .events
                .iter()
                .filter_map(|event| match event.kind {
                    TransitionEventKind::EngineFlameout { engine } => Some((engine, event.time.0)),
                    _ => None,
                })
                .collect();
            assert_eq!(flameouts.len(), 2);
            assert_eq!(flameouts[0].0, first);
            close(flameouts[0].1, 102.0);
            assert_eq!(flameouts[1].0, second);
            close(flameouts[1].1, 104.0);
        }
    }
}
