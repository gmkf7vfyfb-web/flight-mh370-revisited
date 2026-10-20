//! Typed handoff into the end-of-flight kernel at an exact dual-feed boundary.
//!
//! The powered-flight model stops at the continuous instant at which both engine
//! feeds are empty.  The end-of-flight kernel owns the discrete consequences of
//! that boundary.  This adapter therefore constructs the state immediately
//! *before* discrete-event settlement. An engine exhausting at this boundary is
//! labelled running/online with zero feed, thrust, and flow; an engine that
//! exhausted earlier is already windmilling/offline. The kernel then emits the
//! final flameout, generator-loss, SATCOM-power, and optional APU events at
//! elapsed time zero. No positive-duration step uses a running boundary engine.

use mh370_domain::{AircraftState, Degrees, Seconds};
use serde::{Deserialize, Serialize};
use thiserror::Error;

use crate::{
    ApuMode, ApuState, ElectricalSource, ElectricalSystemState, EngineMode, EngineState,
    EngineSystemState, FuelState, Kilograms, KilogramsPerSecond, MassState, MetresPerSecond,
    Newtons, OcxoPowerState, OcxoState, PointMassState, PoweredFuelState,
    TransitionInitialCondition,
};

const TIME_TOLERANCE_SECONDS: f64 = 1.0e-8;
const MASS_TOLERANCE_KG: f64 = 1.0e-8;
const METRES_PER_SECOND_PER_FOOT_PER_MINUTE: f64 = 0.304_8 / 60.0;

/// Scientific boundaries that must remain attached to this conversion.
pub const EXACT_DUAL_EXHAUSTION_BOUNDARY_LIMITATIONS: &[&str] = &[
    "the input is the continuous dual-feed-zero boundary immediately before discrete-event settlement",
    "a running-engine and online-generator label exists only for an engine exhausting at this boundary, so the kernel emits its event at elapsed time zero; zero thrust and flow are never integrated",
    "an engine with an earlier recorded feed-exhaustion time enters windmilling with its generator offline; its earlier event remains part of upstream history",
    "APU-accessible fuel is a caller-declared partition of reserved fuel, not identified by the total-fuel record",
    "the boundary constructor represents the conditional family in which the APU is off before dual-generator loss; a pre-running APU requires a different initial-condition path",
    "the powered-flight BFO bias, autopilot mode, targets, and event clocks are not end-of-flight force or systems states",
    "this conversion assigns no probability and consumes no SATCOM or fuel-exhaustion evidence",
];

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum ExactDualExhaustionBoundaryConvention {
    PreDiscreteEvent,
}

/// Spoke-local inputs required to convert a powered-flight boundary.
///
/// `aircraft` supplies WGS84 position, pressure altitude, ground vertical speed,
/// and time. `heading_true` and `true_airspeed` are air-relative quantities that
/// the caller must obtain consistently from the same weather realization.
#[derive(Debug, Clone, Copy, PartialEq, Serialize, Deserialize)]
pub struct ExactDualExhaustionBoundaryInput {
    pub aircraft: AircraftState,
    pub heading_true: Degrees,
    pub true_airspeed: MetresPerSecond,
    pub powered_fuel: PoweredFuelState,
    /// The part of `powered_fuel.reserved_fuel` physically available to the APU
    /// under this conditional scenario. The remainder stays onboard as unusable.
    pub apu_accessible_reserved_fuel: Kilograms,
    /// Prior OCXO restarts, if any, carried as explicit systems provenance.
    pub ocxo_restart_count: u32,
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct ExactDualExhaustionBoundary {
    pub convention: ExactDualExhaustionBoundaryConvention,
    pub initial: TransitionInitialCondition,
    pub apu_accessible_reserved_fuel: Kilograms,
    pub inaccessible_reserved_fuel: Kilograms,
}

#[derive(Debug, Error, Clone, Copy, PartialEq)]
pub enum ExactDualExhaustionBoundaryError {
    #[error("aircraft boundary kinematics are invalid")]
    InvalidAircraft,
    #[error("air-relative boundary kinematics are invalid")]
    InvalidAirKinematics,
    #[error("powered fuel state is invalid")]
    InvalidFuelState,
    #[error("aircraft and powered-fuel times do not identify the same exact exhaustion boundary")]
    BoundaryTimeMismatch,
    #[error("both engine feeds must be zero at the exact dual-exhaustion boundary")]
    EngineFeedsNotEmpty,
    #[error("both engine exhaustion events must have occurred no later than the boundary")]
    MissingEngineExhaustion,
    #[error(
        "at least one engine exhaustion event must coincide with the dual-exhaustion boundary"
    )]
    NoEngineExhaustionAtBoundary,
    #[error("APU-accessible fuel must be a nonnegative subset of reserved fuel")]
    InvalidApuFuelPartition,
}

/// Construct the pre-discrete-event initial condition at exact dual exhaustion.
///
/// This function deliberately does not construct a control schedule, atmosphere,
/// aerodynamic family, APU-start policy, model weight, or likelihood. Those are
/// independent caller-selected parts of [`crate::TransitionKernelInput`].
pub fn exact_dual_exhaustion_boundary(
    input: ExactDualExhaustionBoundaryInput,
) -> Result<ExactDualExhaustionBoundary, ExactDualExhaustionBoundaryError> {
    validate_aircraft(input.aircraft)?;
    validate_fuel(input.powered_fuel)?;

    if !input.heading_true.is_finite()
        || !(0.0..360.0).contains(&input.heading_true.0)
        || !input.true_airspeed.is_finite()
        || input.true_airspeed.0 <= 0.0
    {
        return Err(ExactDualExhaustionBoundaryError::InvalidAirKinematics);
    }
    let vertical_speed_m_s =
        input.aircraft.vertical_speed.0 * METRES_PER_SECOND_PER_FOOT_PER_MINUTE;
    let sine_flight_path_angle = vertical_speed_m_s / input.true_airspeed.0;
    if !sine_flight_path_angle.is_finite() || sine_flight_path_angle.abs() >= 1.0 {
        return Err(ExactDualExhaustionBoundaryError::InvalidAirKinematics);
    }

    let fuel = input.powered_fuel;
    if (fuel.time.0 - input.aircraft.time.0).abs() > TIME_TOLERANCE_SECONDS
        || fuel.dual_engine_exhaustion_time.map_or(true, |time| {
            (time.0 - fuel.time.0).abs() > TIME_TOLERANCE_SECONDS
        })
    {
        return Err(ExactDualExhaustionBoundaryError::BoundaryTimeMismatch);
    }
    if fuel.left_usable_feed.0.abs() > MASS_TOLERANCE_KG
        || fuel.right_usable_feed.0.abs() > MASS_TOLERANCE_KG
    {
        return Err(ExactDualExhaustionBoundaryError::EngineFeedsNotEmpty);
    }
    if fuel
        .left_exhaustion_time
        .map_or(true, |time| time.0 > fuel.time.0 + TIME_TOLERANCE_SECONDS)
        || fuel
            .right_exhaustion_time
            .map_or(true, |time| time.0 > fuel.time.0 + TIME_TOLERANCE_SECONDS)
    {
        return Err(ExactDualExhaustionBoundaryError::MissingEngineExhaustion);
    }
    let left_exhaustion = fuel
        .left_exhaustion_time
        .expect("validated left exhaustion time");
    let right_exhaustion = fuel
        .right_exhaustion_time
        .expect("validated right exhaustion time");
    if (left_exhaustion.0 - fuel.time.0).abs() > TIME_TOLERANCE_SECONDS
        && (right_exhaustion.0 - fuel.time.0).abs() > TIME_TOLERANCE_SECONDS
    {
        return Err(ExactDualExhaustionBoundaryError::NoEngineExhaustionAtBoundary);
    }
    if !input.apu_accessible_reserved_fuel.is_finite()
        || input.apu_accessible_reserved_fuel.0 < 0.0
        || input.apu_accessible_reserved_fuel.0 > fuel.reserved_fuel.0 + MASS_TOLERANCE_KG
    {
        return Err(ExactDualExhaustionBoundaryError::InvalidApuFuelPartition);
    }

    let apu_accessible = input
        .apu_accessible_reserved_fuel
        .0
        .min(fuel.reserved_fuel.0);
    let inaccessible_reserved = fuel.reserved_fuel.0 - apu_accessible;
    let left_engine = engine_at_boundary(left_exhaustion, fuel.time);
    let right_engine = engine_at_boundary(right_exhaustion, fuel.time);
    let initial = TransitionInitialCondition {
        flight: PointMassState {
            time: input.aircraft.time,
            position: input.aircraft.position,
            altitude: input.aircraft.altitude,
            true_airspeed: input.true_airspeed,
            flight_path_angle: Degrees(sine_flight_path_angle.asin().to_degrees()),
            heading_true: input.heading_true,
        },
        mass: MassState {
            non_fuel_mass: fuel.zero_fuel_weight,
        },
        fuel: FuelState {
            left_engine_feed: Kilograms(0.0),
            right_engine_feed: Kilograms(0.0),
            apu_feed: Kilograms(apu_accessible),
            unusable: Kilograms(fuel.unusable_fuel.0 + inaccessible_reserved),
        },
        engines: EngineSystemState {
            left: left_engine,
            right: right_engine,
        },
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
            restart_count: input.ocxo_restart_count,
        },
    };

    Ok(ExactDualExhaustionBoundary {
        convention: ExactDualExhaustionBoundaryConvention::PreDiscreteEvent,
        initial,
        apu_accessible_reserved_fuel: Kilograms(apu_accessible),
        inaccessible_reserved_fuel: Kilograms(inaccessible_reserved),
    })
}

fn engine_at_boundary(exhaustion_time: Seconds, boundary_time: Seconds) -> EngineState {
    let exhausts_now = (exhaustion_time.0 - boundary_time.0).abs() <= TIME_TOLERANCE_SECONDS;
    EngineState {
        mode: if exhausts_now {
            EngineMode::Running
        } else {
            EngineMode::Windmilling
        },
        thrust: Newtons(0.0),
        fuel_flow: KilogramsPerSecond(0.0),
        generator_online: exhausts_now,
    }
}

fn validate_aircraft(aircraft: AircraftState) -> Result<(), ExactDualExhaustionBoundaryError> {
    if !aircraft.all_finite()
        || !(-90.0..=90.0).contains(&aircraft.position.latitude.0)
        || !(-180.0..180.0).contains(&aircraft.position.longitude.0)
        || !(0.0..360.0).contains(&aircraft.track_true.0)
        || aircraft.ground_speed.0 <= 0.0
    {
        Err(ExactDualExhaustionBoundaryError::InvalidAircraft)
    } else {
        Ok(())
    }
}

fn validate_fuel(fuel: PoweredFuelState) -> Result<(), ExactDualExhaustionBoundaryError> {
    let finite = [
        fuel.time.0,
        fuel.zero_fuel_weight.0,
        fuel.left_usable_feed.0,
        fuel.right_usable_feed.0,
        fuel.reserved_fuel.0,
        fuel.unusable_fuel.0,
    ]
    .into_iter()
    .all(f64::is_finite)
        && [
            fuel.left_exhaustion_time,
            fuel.right_exhaustion_time,
            fuel.dual_engine_exhaustion_time,
        ]
        .into_iter()
        .flatten()
        .all(|time| time.is_finite());
    if !finite
        || fuel.zero_fuel_weight.0 <= 0.0
        || fuel.left_usable_feed.0 < 0.0
        || fuel.right_usable_feed.0 < 0.0
        || fuel.reserved_fuel.0 < 0.0
        || fuel.unusable_fuel.0 < 0.0
    {
        Err(ExactDualExhaustionBoundaryError::InvalidFuelState)
    } else {
        Ok(())
    }
}

#[cfg(test)]
mod tests {
    use mh370_domain::{Feet, FeetPerMinute, Hertz, Knots, LatLon};

    use super::*;
    use crate::{
        attempt_controlled_to_uncontrolled_with_checkpoints, AerodynamicModel, ApuStartPolicy,
        AtmosphereNode, AtmosphereProfile, ConditionalModelFamily, ControlCommand, ControlFamily,
        ControlSchedule, ControlSegment, ControlTransitionOutcome, ControlTransitionTrigger,
        ControlledToUncontrolledPolicy, ControlledToUncontrolledScenario,
        ExactTimeCheckpointSchedule, IntegrationSettings, KilogramsPerCubicMetre, ModelWeight,
        RequestedCheckpointStatus, RestartTransientFamily, SquareMetres, TransitionEventKind,
    };

    fn input() -> ExactDualExhaustionBoundaryInput {
        ExactDualExhaustionBoundaryInput {
            aircraft: AircraftState {
                time: Seconds(22_541.416),
                position: LatLon::new(-34.0, 94.0).unwrap(),
                altitude: Feet(35_000.0),
                track_true: Degrees(180.0),
                ground_speed: Knots(470.0),
                vertical_speed: FeetPerMinute(-1_200.0),
                bfo_bias: Hertz(145.0),
            },
            heading_true: Degrees(178.0),
            true_airspeed: MetresPerSecond(240.0),
            powered_fuel: PoweredFuelState {
                time: Seconds(22_541.416),
                zero_fuel_weight: Kilograms(174_369.0),
                left_usable_feed: Kilograms(0.0),
                right_usable_feed: Kilograms(0.0),
                reserved_fuel: Kilograms(15.0),
                unusable_fuel: Kilograms(2.0),
                left_exhaustion_time: Some(Seconds(22_541.416)),
                right_exhaustion_time: Some(Seconds(22_541.416)),
                dual_engine_exhaustion_time: Some(Seconds(22_541.416)),
            },
            apu_accessible_reserved_fuel: Kilograms(5.0),
            ocxo_restart_count: 0,
        }
    }

    fn control(command: ControlCommand) -> ControlSchedule {
        ControlSchedule {
            segments: vec![ControlSegment {
                start_offset: Seconds(0.0),
                command,
            }],
        }
    }

    #[test]
    fn mapping_preserves_mass_and_makes_partition_explicit() {
        let source = input();
        let boundary = exact_dual_exhaustion_boundary(source).unwrap();
        assert_eq!(
            boundary.convention,
            ExactDualExhaustionBoundaryConvention::PreDiscreteEvent
        );
        assert_eq!(boundary.apu_accessible_reserved_fuel, Kilograms(5.0));
        assert_eq!(boundary.inaccessible_reserved_fuel, Kilograms(10.0));
        assert_eq!(boundary.initial.fuel.apu_feed, Kilograms(5.0));
        assert_eq!(boundary.initial.fuel.unusable, Kilograms(12.0));
        assert_eq!(boundary.initial.mass.non_fuel_mass, Kilograms(174_369.0));
        assert_eq!(
            boundary.initial.mass.non_fuel_mass.0 + boundary.initial.fuel.total_mass().0,
            source.powered_fuel.gross_mass().0
        );
        assert_eq!(boundary.initial.engines.left.mode, EngineMode::Running);
        assert_eq!(boundary.initial.engines.left.thrust, Newtons(0.0));
        assert!(boundary.initial.engines.left.generator_online);
        assert_eq!(
            boundary.initial.electrical.source,
            ElectricalSource::EngineGenerators
        );
        assert!(boundary.initial.electrical.satcom_powered);
        assert_eq!(boundary.initial.ocxo.power, OcxoPowerState::Powered);
    }

    #[test]
    fn kernel_settles_boundary_and_switches_control_at_elapsed_zero() {
        let boundary = exact_dual_exhaustion_boundary(input()).unwrap();
        let controlled = control(ControlCommand::Controlled {
            lift_load_factor: 1.0,
            bank_angle: Degrees(0.0),
        });
        let uncontrolled = control(ControlCommand::Uncontrolled {
            lift_coefficient: 0.7,
            bank_angle: Degrees(-5.0),
        });
        let kernel_input = crate::TransitionKernelInput {
            initial: boundary.initial,
            family: ConditionalModelFamily {
                control: ControlFamily::Controlled,
                restart_transient: RestartTransientFamily::NoAdditionalTransient,
            },
            model_weight: ModelWeight(0.25),
            control: controlled.clone(),
            aerodynamics: AerodynamicModel {
                reference_area: SquareMetres(427.8),
                zero_lift_drag_coefficient: 0.024,
                induced_drag_factor: 0.047,
                minimum_lift_coefficient: -1.5,
                maximum_lift_coefficient: 1.5,
                maximum_bank_angle: Degrees(60.0),
                minimum_true_airspeed: MetresPerSecond(50.0),
                maximum_true_airspeed: MetresPerSecond(700.0),
            },
            atmosphere: AtmosphereProfile {
                nodes: vec![AtmosphereNode {
                    altitude: Feet(0.0),
                    density: KilogramsPerCubicMetre(1.225),
                    wind_north: MetresPerSecond(0.0),
                    wind_east: MetresPerSecond(0.0),
                }],
            },
            apu_start_policy: ApuStartPolicy::Disabled,
            integration: IntegrationSettings {
                time_step: Seconds(1.0),
                maximum_duration: Seconds(1.0),
                sea_surface_altitude: Feet(0.0),
                maximum_steps: 4,
            },
        };
        let policy = ControlledToUncontrolledPolicy {
            scenario: ControlledToUncontrolledScenario {
                label: "dual-feed-zero-boundary-test".to_string(),
                trigger: ControlTransitionTrigger::DualEngineFlameout,
            },
            pre_trigger_controlled: controlled,
            post_trigger_uncontrolled: uncontrolled,
        };
        let result = attempt_controlled_to_uncontrolled_with_checkpoints(
            &kernel_input,
            &policy,
            &ExactTimeCheckpointSchedule {
                requested_elapsed_times: vec![Seconds(0.0)],
            },
        )
        .unwrap();

        assert_eq!(
            result.checkpoint_status,
            RequestedCheckpointStatus::AllReached
        );
        let ControlTransitionOutcome::Reached { event } = result.control_transition else {
            panic!("dual flameout trigger was not reached at the boundary");
        };
        assert_eq!(event.elapsed, Seconds(0.0));
        assert_eq!(event.time, input().aircraft.time);
        assert_eq!(
            event.post_trigger_command,
            policy.post_trigger_uncontrolled.segments[0].command
        );
        assert_eq!(event.state.engines.left.mode, EngineMode::Windmilling);
        assert_eq!(event.state.engines.right.mode, EngineMode::Windmilling);
        assert_eq!(event.state.electrical.source, ElectricalSource::Unpowered);
        assert!(!event.state.electrical.satcom_powered);

        let events = &result.checkpoints[0].events_at_time;
        assert_eq!(
            events
                .iter()
                .filter(|kind| matches!(kind, TransitionEventKind::EngineFlameout { .. }))
                .count(),
            2
        );
        assert!(events
            .iter()
            .any(|kind| matches!(kind, TransitionEventKind::DualEngineGeneratorLoss)));
        assert!(events
            .iter()
            .any(|kind| matches!(kind, TransitionEventKind::SatcomPowerLost)));
        assert_eq!(result.transition.model_weight, ModelWeight(0.25));
    }

    #[test]
    fn staggered_feed_history_does_not_reemit_the_earlier_flameout() {
        let mut source = input();
        source.powered_fuel.left_exhaustion_time = Some(Seconds(22_531.416));
        let boundary = exact_dual_exhaustion_boundary(source).unwrap();
        assert_eq!(boundary.initial.engines.left.mode, EngineMode::Windmilling);
        assert!(!boundary.initial.engines.left.generator_online);
        assert_eq!(boundary.initial.engines.right.mode, EngineMode::Running);
        assert!(boundary.initial.engines.right.generator_online);
        assert_eq!(
            boundary.initial.electrical.source,
            ElectricalSource::EngineGenerators
        );
    }

    #[test]
    fn rejects_non_boundary_state_and_invalid_apu_partition() {
        let mut nonempty = input();
        nonempty.powered_fuel.left_usable_feed = Kilograms(0.01);
        assert_eq!(
            exact_dual_exhaustion_boundary(nonempty),
            Err(ExactDualExhaustionBoundaryError::EngineFeedsNotEmpty)
        );

        let mut bad_partition = input();
        bad_partition.apu_accessible_reserved_fuel = Kilograms(16.0);
        assert_eq!(
            exact_dual_exhaustion_boundary(bad_partition),
            Err(ExactDualExhaustionBoundaryError::InvalidApuFuelPartition)
        );

        let mut mismatched = input();
        mismatched.powered_fuel.dual_engine_exhaustion_time = Some(Seconds(22_540.0));
        assert_eq!(
            exact_dual_exhaustion_boundary(mismatched),
            Err(ExactDualExhaustionBoundaryError::BoundaryTimeMismatch)
        );

        let mut no_boundary_event = input();
        no_boundary_event.powered_fuel.left_exhaustion_time = Some(Seconds(22_530.0));
        no_boundary_event.powered_fuel.right_exhaustion_time = Some(Seconds(22_540.0));
        assert_eq!(
            exact_dual_exhaustion_boundary(no_boundary_event),
            Err(ExactDualExhaustionBoundaryError::NoEngineExhaustionAtBoundary)
        );
    }
}
