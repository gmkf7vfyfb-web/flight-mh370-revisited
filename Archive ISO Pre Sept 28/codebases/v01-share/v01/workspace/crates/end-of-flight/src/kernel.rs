//! Deterministic, conditional transition from a final powered-flight state to impact.
//!
//! This module deliberately contains no SATCOM observation or likelihood. The caller
//! supplies one explicitly weighted physical/model-family hypothesis; the returned
//! transition carries that weight unchanged. Combining families and normalising their
//! weights belongs to the estimator.

use mh370_domain::{
    destination_wgs84, great_circle_distance_nm, Degrees, Feet, GeodesyError, ImpactPoint, LatLon,
    NauticalMiles, Seconds,
};
use serde::{Deserialize, Serialize};
use thiserror::Error;

const FEET_PER_METRE: f64 = 3.280_839_895_013_123;
const METRES_PER_NAUTICAL_MILE: f64 = 1_852.0;
const STANDARD_GRAVITY_M_S2: f64 = 9.806_65;
const EVENT_EPSILON_S: f64 = 1.0e-9;

/// Important limits of the first transition-kernel increment.
///
/// These are model/data boundaries, not random errors. A caller must select conditional
/// inputs rather than silently broadening a numerical standard deviation.
pub const TRANSITION_KERNEL_LIMITATIONS: &[&str] = &[
    "point-mass dynamics do not resolve attitude, structural breakup, or water entry",
    "caller must supply configuration-specific lift/drag bounds and atmosphere",
    "engine thrust, fuel flow, feed availability, and generator state are conditional inputs",
    "APU start fuel and timing are conditional inputs; attitude-dependent pickup is not resolved",
    "OCXO/restart family is labelled but no SATCOM bias likelihood is evaluated",
    "no proprietary Boeing envelope is interpreted as a probability distribution",
    "requested checkpoints become integration boundaries; nonlinear results remain step-size dependent",
    "checkpoint times separated by one nanosecond or less are rejected rather than coalesced",
];

macro_rules! physical_quantity {
    ($name:ident) => {
        #[derive(Debug, Clone, Copy, Default, PartialEq, PartialOrd, Serialize, Deserialize)]
        #[serde(transparent)]
        pub struct $name(pub f64);

        impl $name {
            pub const fn new(value: f64) -> Self {
                Self(value)
            }

            pub const fn value(self) -> f64 {
                self.0
            }

            pub fn is_finite(self) -> bool {
                self.0.is_finite()
            }
        }
    };
}

physical_quantity!(Joules);
physical_quantity!(Kilograms);
physical_quantity!(KilogramsPerCubicMetre);
physical_quantity!(KilogramsPerSecond);
physical_quantity!(MetresPerSecond);
physical_quantity!(Newtons);
physical_quantity!(SquareMetres);

/// An unnormalised hypothesis weight. The kernel validates and preserves it exactly.
#[derive(Debug, Clone, Copy, Default, PartialEq, PartialOrd, Serialize, Deserialize)]
#[serde(transparent)]
pub struct ModelWeight(pub f64);

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum ControlFamily {
    Controlled,
    Uncontrolled,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum RestartTransientFamily {
    NoAdditionalTransient,
    CommonOcxoWarmup,
    R1200ChannelSettling,
    UnspecifiedRestartTransient,
}

/// A named conditional family, never an empirical frequency or probability by itself.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
pub struct ConditionalModelFamily {
    pub control: ControlFamily,
    pub restart_transient: RestartTransientFamily,
}

/// Air-relative point-mass kinematics. This intentionally contains no BFO state.
#[derive(Debug, Clone, Copy, PartialEq, Serialize, Deserialize)]
pub struct PointMassState {
    pub time: Seconds,
    pub position: LatLon,
    pub altitude: Feet,
    pub true_airspeed: MetresPerSecond,
    /// Positive above the local horizontal.
    pub flight_path_angle: Degrees,
    pub heading_true: Degrees,
}

#[derive(Debug, Clone, Copy, PartialEq, Serialize, Deserialize)]
pub struct MassState {
    /// Aircraft, occupants, payload, and fluids not represented in FuelState.
    pub non_fuel_mass: Kilograms,
}

#[derive(Debug, Clone, Copy, PartialEq, Serialize, Deserialize)]
pub struct FuelState {
    pub left_engine_feed: Kilograms,
    pub right_engine_feed: Kilograms,
    pub apu_feed: Kilograms,
    pub unusable: Kilograms,
}

impl FuelState {
    pub fn total_mass(self) -> Kilograms {
        Kilograms(
            self.left_engine_feed.0 + self.right_engine_feed.0 + self.apu_feed.0 + self.unusable.0,
        )
    }
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum EngineMode {
    Running,
    Windmilling,
    FlamedOut,
}

#[derive(Debug, Clone, Copy, PartialEq, Serialize, Deserialize)]
pub struct EngineState {
    pub mode: EngineMode,
    pub thrust: Newtons,
    pub fuel_flow: KilogramsPerSecond,
    pub generator_online: bool,
}

impl EngineState {
    fn active_thrust(self) -> f64 {
        if self.mode == EngineMode::Running {
            self.thrust.0
        } else {
            0.0
        }
    }

    fn active_fuel_flow(self) -> f64 {
        if self.mode == EngineMode::Running {
            self.fuel_flow.0
        } else {
            0.0
        }
    }

    fn active_generator(self) -> bool {
        self.mode == EngineMode::Running && self.generator_online
    }

    fn flame_out(&mut self) {
        self.mode = EngineMode::Windmilling;
        self.thrust = Newtons(0.0);
        self.fuel_flow = KilogramsPerSecond(0.0);
        self.generator_online = false;
    }
}

#[derive(Debug, Clone, Copy, PartialEq, Serialize, Deserialize)]
pub struct EngineSystemState {
    pub left: EngineState,
    pub right: EngineState,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum ElectricalSource {
    EngineGenerators,
    ApuGenerator,
    Unpowered,
}

#[derive(Debug, Clone, Copy, PartialEq, Serialize, Deserialize)]
pub struct ElectricalSystemState {
    pub source: ElectricalSource,
    pub satcom_powered: bool,
    /// Required when both engine generators were already lost before the kernel start.
    pub dual_engine_generator_loss_elapsed: Option<Seconds>,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum ApuMode {
    Off,
    Starting,
    Running,
    Unavailable,
}

#[derive(Debug, Clone, Copy, PartialEq, Serialize, Deserialize)]
pub struct ApuState {
    pub mode: ApuMode,
    pub elapsed_in_mode: Seconds,
    pub generator_online: bool,
    pub fuel_flow: KilogramsPerSecond,
}

#[derive(Debug, Clone, Copy, PartialEq, Serialize, Deserialize)]
#[serde(tag = "mode", rename_all = "snake_case")]
pub enum ApuStartPolicy {
    Disabled,
    OnDualEngineGeneratorLoss {
        start_delay: Seconds,
        start_fuel: Kilograms,
        generator_delay: Seconds,
        running_fuel_flow: KilogramsPerSecond,
    },
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum OcxoPowerState {
    Powered,
    Unpowered,
}

#[derive(Debug, Clone, Copy, PartialEq, Serialize, Deserialize)]
pub struct OcxoState {
    pub power: OcxoPowerState,
    pub unpowered_duration: Seconds,
    pub restart_count: u32,
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct TransitionInitialCondition {
    pub flight: PointMassState,
    pub mass: MassState,
    pub fuel: FuelState,
    pub engines: EngineSystemState,
    pub electrical: ElectricalSystemState,
    pub apu: ApuState,
    pub ocxo: OcxoState,
}

#[derive(Debug, Clone, Copy, PartialEq, Serialize, Deserialize)]
#[serde(tag = "mode", rename_all = "snake_case")]
pub enum ControlCommand {
    /// lift_load_factor is total lift divided by current weight, not vertical load factor.
    Controlled {
        lift_load_factor: f64,
        bank_angle: Degrees,
    },
    Uncontrolled {
        lift_coefficient: f64,
        bank_angle: Degrees,
    },
}

#[derive(Debug, Clone, Copy, PartialEq, Serialize, Deserialize)]
pub struct ControlSegment {
    pub start_offset: Seconds,
    pub command: ControlCommand,
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct ControlSchedule {
    pub segments: Vec<ControlSegment>,
}

#[derive(Debug, Clone, Copy, PartialEq, Serialize, Deserialize)]
pub struct AerodynamicModel {
    pub reference_area: SquareMetres,
    pub zero_lift_drag_coefficient: f64,
    /// Coefficient k in CD = CD0 + k * CL^2.
    pub induced_drag_factor: f64,
    pub minimum_lift_coefficient: f64,
    pub maximum_lift_coefficient: f64,
    pub maximum_bank_angle: Degrees,
    /// A declared numerical/physical validity envelope, not a stall model.
    pub minimum_true_airspeed: MetresPerSecond,
    pub maximum_true_airspeed: MetresPerSecond,
}

#[derive(Debug, Clone, Copy, PartialEq, Serialize, Deserialize)]
pub struct AtmosphereNode {
    pub altitude: Feet,
    pub density: KilogramsPerCubicMetre,
    pub wind_north: MetresPerSecond,
    pub wind_east: MetresPerSecond,
}

/// Piecewise-linear density and horizontal wind, clamped at the end nodes.
#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct AtmosphereProfile {
    pub nodes: Vec<AtmosphereNode>,
}

/// One atmosphere evaluation at the evolving point-mass state.
///
/// Implementations may be an altitude-only profile or a caller-owned, time-varying
/// four-dimensional field.  Keeping this narrow interface in the kernel lets the runner
/// compose ERA5 without making the end-of-flight spoke depend on the dynamics spoke.
#[derive(Debug, Clone, Copy, PartialEq)]
pub struct TransitionAtmosphereSample {
    pub density: KilogramsPerCubicMetre,
    pub wind_north: MetresPerSecond,
    pub wind_east: MetresPerSecond,
}

#[derive(Debug, Error, Clone, Copy, PartialEq, Eq)]
pub enum TransitionAtmosphereError {
    #[error("atmosphere state lies outside the supplied field")]
    OutsideDomain,
    #[error("atmosphere field returned a non-finite or non-physical sample")]
    InvalidSample,
}

/// Deterministic atmosphere supplied by the caller at each integration evaluation.
pub trait TransitionAtmosphere {
    fn sample(
        &self,
        time: Seconds,
        position: LatLon,
        pressure_altitude: Feet,
    ) -> Result<TransitionAtmosphereSample, TransitionAtmosphereError>;
}

#[derive(Debug, Clone, Copy, PartialEq, Serialize, Deserialize)]
pub struct IntegrationSettings {
    pub time_step: Seconds,
    pub maximum_duration: Seconds,
    pub sea_surface_altitude: Feet,
    pub maximum_steps: usize,
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct TransitionKernelInput {
    pub initial: TransitionInitialCondition,
    pub family: ConditionalModelFamily,
    pub model_weight: ModelWeight,
    pub control: ControlSchedule,
    pub aerodynamics: AerodynamicModel,
    pub atmosphere: AtmosphereProfile,
    pub apu_start_policy: ApuStartPolicy,
    pub integration: IntegrationSettings,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum EngineSide {
    Left,
    Right,
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(tag = "event", rename_all = "snake_case")]
pub enum TransitionEventKind {
    EngineFlameout {
        engine: EngineSide,
    },
    DualEngineGeneratorLoss,
    SatcomPowerLost,
    ApuStart,
    ApuStartFailedInsufficientFuel,
    ApuGeneratorOnline,
    ApuFuelExhausted,
    SatcomPowerRestored,
    OcxoRestart {
        family: RestartTransientFamily,
        outage_duration: Seconds,
    },
    LiftCoefficientLimited {
        requested: f64,
        applied: f64,
    },
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct TransitionEvent {
    pub time: Seconds,
    pub kind: TransitionEventKind,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum DeclaredEnvelopeExit {
    AirspeedBelowMinimum,
    AirspeedAboveMaximum,
    NearVerticalFlightPath,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum TransitionTermination {
    Impact,
    MaximumDuration,
    MaximumSteps,
    DeclaredEnvelopeExit(DeclaredEnvelopeExit),
}

#[derive(Debug, Clone, Copy, PartialEq, Serialize, Deserialize)]
pub struct TerminalKinematics {
    pub point_mass: PointMassState,
    pub ground_speed: MetresPerSecond,
    pub ground_track_true: Degrees,
    pub vertical_speed: MetresPerSecond,
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct TransitionTerminalState {
    pub kinematics: TerminalKinematics,
    pub mass: Kilograms,
    pub fuel: FuelState,
    pub engines: EngineSystemState,
    pub electrical: ElectricalSystemState,
    pub apu: ApuState,
    pub ocxo: OcxoState,
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct ImpactData {
    pub point: ImpactPoint,
    pub mass: Kilograms,
    pub true_airspeed: MetresPerSecond,
    pub ground_speed: MetresPerSecond,
    /// Positive upward.
    pub vertical_speed: MetresPerSecond,
    /// Positive below the local horizontal.
    pub impact_angle: Degrees,
    pub kinetic_energy: Joules,
    pub horizontal_kinetic_energy: Joules,
    pub vertical_kinetic_energy: Joules,
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct WeightedTransition {
    pub family: ConditionalModelFamily,
    pub model_weight: ModelWeight,
    pub terminal: TransitionTerminalState,
    pub events: Vec<TransitionEvent>,
    pub termination: TransitionTermination,
    pub impact: Option<ImpactData>,
}

/// Minimum separation at which requested checkpoint times are distinct to the kernel.
pub const EXACT_TIME_CHECKPOINT_MINIMUM_SEPARATION: Seconds = Seconds(EVENT_EPSILON_S);

/// Strictly ordered elapsed times at which the caller requests complete state snapshots.
///
/// Zero and the configured maximum duration are valid. Times closer together than
/// EXACT_TIME_CHECKPOINT_MINIMUM_SEPARATION are rejected rather than silently coalesced.
#[derive(Debug, Clone, Default, PartialEq, Serialize, Deserialize)]
pub struct ExactTimeCheckpointSchedule {
    pub requested_elapsed_times: Vec<Seconds>,
}

impl ExactTimeCheckpointSchedule {
    pub fn validate(
        &self,
        maximum_duration: Seconds,
    ) -> Result<(), ExactTimeCheckpointScheduleError> {
        if !maximum_duration.is_finite() || maximum_duration.0 < 0.0 {
            return Err(ExactTimeCheckpointScheduleError::InvalidMaximumDuration {
                maximum_duration,
            });
        }

        let mut previous: Option<Seconds> = None;
        for (index, requested) in self.requested_elapsed_times.iter().copied().enumerate() {
            if !requested.is_finite() {
                return Err(ExactTimeCheckpointScheduleError::NonFinite { index });
            }
            if requested.0 < 0.0 {
                return Err(ExactTimeCheckpointScheduleError::Negative {
                    index,
                    requested_elapsed: requested,
                });
            }
            if requested.0 > maximum_duration.0 {
                return Err(ExactTimeCheckpointScheduleError::BeyondMaximumDuration {
                    index,
                    requested_elapsed: requested,
                    maximum_duration,
                });
            }
            if let Some(previous_elapsed) = previous {
                if requested.0 <= previous_elapsed.0 {
                    return Err(ExactTimeCheckpointScheduleError::NotStrictlyIncreasing {
                        index,
                        previous_elapsed,
                        requested_elapsed: requested,
                    });
                }
                if requested.0 - previous_elapsed.0 <= EVENT_EPSILON_S {
                    return Err(ExactTimeCheckpointScheduleError::BelowMinimumSeparation {
                        index,
                        previous_elapsed,
                        requested_elapsed: requested,
                        minimum_separation: EXACT_TIME_CHECKPOINT_MINIMUM_SEPARATION,
                    });
                }
            } else if requested.0 > 0.0 && requested.0 <= EVENT_EPSILON_S {
                return Err(ExactTimeCheckpointScheduleError::BelowMinimumSeparation {
                    index,
                    previous_elapsed: Seconds(0.0),
                    requested_elapsed: requested,
                    minimum_separation: EXACT_TIME_CHECKPOINT_MINIMUM_SEPARATION,
                });
            }
            previous = Some(requested);
        }
        Ok(())
    }
}

/// A post-discrete-event snapshot at one exact caller-requested elapsed time.
#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct ExactTimeCheckpoint {
    pub requested_elapsed: Seconds,
    pub state: TransitionTerminalState,
    pub active_control: ControlCommand,
    /// Events committed at this same absolute time before the snapshot.
    pub events_at_time: Vec<TransitionEventKind>,
}

/// The ordinary terminal transition plus every requested exact-time snapshot.
#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct CheckpointedTransition {
    pub transition: WeightedTransition,
    pub checkpoints: Vec<ExactTimeCheckpoint>,
}

#[derive(Debug, Error, Clone, PartialEq)]
pub enum ExactTimeCheckpointScheduleError {
    #[error("checkpoint maximum duration is invalid: {maximum_duration:?}")]
    InvalidMaximumDuration { maximum_duration: Seconds },
    #[error("checkpoint time at index {index} is non-finite")]
    NonFinite { index: usize },
    #[error("checkpoint time at index {index} is negative: {requested_elapsed:?}")]
    Negative {
        index: usize,
        requested_elapsed: Seconds,
    },
    #[error(
        "checkpoint time at index {index} is not strictly greater than {previous_elapsed:?}: {requested_elapsed:?}"
    )]
    NotStrictlyIncreasing {
        index: usize,
        previous_elapsed: Seconds,
        requested_elapsed: Seconds,
    },
    #[error(
        "checkpoint time at index {index} is too close to {previous_elapsed:?}: {requested_elapsed:?}; minimum {minimum_separation:?}"
    )]
    BelowMinimumSeparation {
        index: usize,
        previous_elapsed: Seconds,
        requested_elapsed: Seconds,
        minimum_separation: Seconds,
    },
    #[error(
        "checkpoint time at index {index} exceeds maximum {maximum_duration:?}: {requested_elapsed:?}"
    )]
    BeyondMaximumDuration {
        index: usize,
        requested_elapsed: Seconds,
        maximum_duration: Seconds,
    },
}

#[derive(Debug, Error)]
pub enum ExactTimeCheckpointError {
    #[error(transparent)]
    Schedule(#[from] ExactTimeCheckpointScheduleError),
    #[error(transparent)]
    Transition(#[from] TransitionError),
    #[error("checkpoint {requested_elapsed:?} was not reached before termination {termination:?}")]
    Unreached {
        requested_elapsed: Seconds,
        termination: TransitionTermination,
    },
}
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum ControlTransitionTrigger {
    /// Switch when an engine-flameout event leaves neither engine running.
    DualEngineFlameout,
    /// Switch on the existing dual-engine-generator-loss discrete event.
    DualEngineGeneratorLoss,
}

/// Explicit label and physical trigger for one caller-selected conditional scenario.
#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct ControlledToUncontrolledScenario {
    pub label: String,
    pub trigger: ControlTransitionTrigger,
}

/// Deterministic schedules on either side of a caller-selected discrete trigger.
///
/// This type does not assert that either trigger causes loss of control. It describes a
/// conditional scenario selected outside the kernel. Post-trigger segment offsets are
/// measured from the exact switch time, not from kernel start.
#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct ControlledToUncontrolledPolicy {
    pub scenario: ControlledToUncontrolledScenario,
    pub pre_trigger_controlled: ControlSchedule,
    pub post_trigger_uncontrolled: ControlSchedule,
}

/// Typed control-mode switch and complete post-discrete-event state at the switch.
#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct ControlModeTransitionEvent {
    pub time: Seconds,
    pub elapsed: Seconds,
    pub trigger: ControlTransitionTrigger,
    pub from: ControlFamily,
    pub to: ControlFamily,
    pub pre_trigger_command: ControlCommand,
    pub post_trigger_command: ControlCommand,
    pub state: TransitionTerminalState,
}

/// Result for a labelled controlled-to-uncontrolled conditional scenario.
#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct ControlledToUncontrolledResult {
    pub scenario: ControlledToUncontrolledScenario,
    pub restart_transient: RestartTransientFamily,
    pub model_weight: ModelWeight,
    pub terminal: TransitionTerminalState,
    pub events: Vec<TransitionEvent>,
    pub control_transition: ControlModeTransitionEvent,
    pub terminal_control: ControlCommand,
    pub termination: TransitionTermination,
    pub impact: Option<ImpactData>,
}

/// One controlled-to-uncontrolled result plus every requested exact-time snapshot.
#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct CheckpointedControlledToUncontrolledResult {
    pub transition: ControlledToUncontrolledResult,
    pub checkpoints: Vec<ExactTimeCheckpoint>,
}

/// Whether every caller-requested checkpoint was reached before physical termination.
#[derive(Debug, Clone, Copy, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum RequestedCheckpointStatus {
    AllReached,
    Unreached {
        next_requested_elapsed: Seconds,
        termination: TransitionTermination,
    },
}

/// Physical outcome of the caller-selected control-transition trigger.
#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum ControlTransitionOutcome {
    Reached {
        event: Box<ControlModeTransitionEvent>,
    },
    NotReached {
        trigger: ControlTransitionTrigger,
        termination: TransitionTermination,
    },
}

/// Non-lossy result from one attempted controlled-to-uncontrolled propagation.
///
/// The ordinary transition is always retained after scientifically valid propagation.
/// `checkpoints` is the reached prefix of the requested schedule; the two outcome fields
/// distinguish physical non-reach from input, policy, schedule, and numerical errors.
#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct ControlledToUncontrolledAttempt {
    pub transition: WeightedTransition,
    pub checkpoints: Vec<ExactTimeCheckpoint>,
    pub checkpoint_status: RequestedCheckpointStatus,
    pub control_transition: ControlTransitionOutcome,
}

#[derive(Debug, Error)]
pub enum ControlledToUncontrolledError {
    #[error(transparent)]
    Transition(#[from] TransitionError),
    #[error("controlled-to-uncontrolled scenario label must not be empty")]
    EmptyScenarioLabel,
    #[error("kernel input family must be controlled before the selected trigger, got {actual:?}")]
    InputFamilyMustBeControlled { actual: ControlFamily },
    #[error("kernel input control schedule differs from the policy pre-trigger schedule")]
    PreTriggerScheduleMismatch,
    #[error("pre-trigger schedule is invalid: {reason}")]
    InvalidPreTriggerSchedule { reason: &'static str },
    #[error("post-trigger schedule is invalid: {reason}")]
    InvalidPostTriggerSchedule { reason: &'static str },
    #[error("selected trigger already occurred before kernel start: {trigger:?}")]
    TriggerAlreadyOccurred { trigger: ControlTransitionTrigger },
    #[error("selected trigger {trigger:?} was not reached before termination {termination:?}")]
    TriggerNotReached {
        trigger: ControlTransitionTrigger,
        termination: TransitionTermination,
    },
}

#[derive(Debug, Error)]
pub enum ControlledToUncontrolledCheckpointError {
    #[error(transparent)]
    Schedule(#[from] ExactTimeCheckpointScheduleError),
    #[error(transparent)]
    ControlledTransition(#[from] ControlledToUncontrolledError),
    #[error("checkpoint {requested_elapsed:?} was not reached before termination {termination:?}")]
    Unreached {
        requested_elapsed: Seconds,
        termination: TransitionTermination,
    },
}

#[derive(Debug, Error)]
pub enum ControlledToUncontrolledAttemptError {
    #[error(transparent)]
    Schedule(#[from] ExactTimeCheckpointScheduleError),
    #[error(transparent)]
    ControlledTransition(#[from] ControlledToUncontrolledError),
}

#[derive(Debug, Error)]
pub enum TransitionError {
    #[error("invalid transition input: {0}")]
    InvalidInput(&'static str),
    #[error("propagation produced a non-finite state")]
    NonFinitePropagation,
    #[error(transparent)]
    Atmosphere(#[from] TransitionAtmosphereError),
    #[error(transparent)]
    Geodesy(#[from] GeodesyError),
}

#[derive(Debug, Clone)]
struct ContinuousState {
    absolute_time_s: f64,
    position: LatLon,
    altitude_m: f64,
    true_airspeed_m_s: f64,
    flight_path_angle_rad: f64,
    heading_rad: f64,
}

#[derive(Debug, Clone)]
struct RuntimeState {
    continuous: ContinuousState,
    elapsed_s: f64,
    fuel: FuelState,
    engines: EngineSystemState,
    electrical: ElectricalSystemState,
    apu: ApuState,
    ocxo: OcxoState,
    lift_limited: bool,
}

#[derive(Debug)]
struct PropagationRun {
    transition: WeightedTransition,
    checkpoints: Vec<ExactTimeCheckpoint>,
    control_transition: Option<ControlModeTransitionEvent>,
}

#[derive(Debug, Clone, Copy)]
struct Derivative {
    airspeed_m_s2: f64,
    flight_path_angle_rad_s: f64,
    heading_rad_s: f64,
    altitude_m_s: f64,
    ground_north_m_s: f64,
    ground_east_m_s: f64,
    requested_cl: f64,
    applied_cl: f64,
}

#[derive(Debug, Clone, Copy)]
struct Motion {
    north_m_s: f64,
    east_m_s: f64,
    vertical_m_s: f64,
}

#[derive(Debug, Clone, Copy)]
struct StepMass {
    start_kg: f64,
    midpoint_kg: f64,
}

fn validate_nonnegative(value: f64, message: &'static str) -> Result<(), TransitionError> {
    if !value.is_finite() || value < 0.0 {
        return Err(TransitionError::InvalidInput(message));
    }
    Ok(())
}

fn validate_engine(engine: EngineState) -> Result<(), TransitionError> {
    validate_nonnegative(
        engine.thrust.0,
        "engine thrust must be finite and nonnegative",
    )?;
    validate_nonnegative(
        engine.fuel_flow.0,
        "engine fuel flow must be finite and nonnegative",
    )?;
    if engine.mode != EngineMode::Running
        && (engine.thrust.0 != 0.0 || engine.fuel_flow.0 != 0.0 || engine.generator_online)
    {
        return Err(TransitionError::InvalidInput(
            "non-running engine must have zero thrust/flow and no online generator",
        ));
    }
    Ok(())
}

fn expected_electrical_source(engines: EngineSystemState, apu: ApuState) -> ElectricalSource {
    if engines.left.active_generator() || engines.right.active_generator() {
        ElectricalSource::EngineGenerators
    } else if apu.mode == ApuMode::Running && apu.generator_online {
        ElectricalSource::ApuGenerator
    } else {
        ElectricalSource::Unpowered
    }
}

fn validate_control_schedule(
    schedule: &ControlSchedule,
    expected_family: ControlFamily,
    aerodynamics: AerodynamicModel,
) -> Result<(), &'static str> {
    if schedule.segments.is_empty() {
        return Err("control schedule must contain at least one segment");
    }
    if schedule.segments[0].start_offset.0 != 0.0 {
        return Err("control schedule must begin at zero offset");
    }

    let mut previous_start = -1.0;
    for segment in &schedule.segments {
        if !segment.start_offset.is_finite()
            || segment.start_offset.0 < 0.0
            || segment.start_offset.0 <= previous_start
        {
            return Err("control segment offsets must be finite and strictly increasing");
        }
        previous_start = segment.start_offset.0;
        let (command_family, bank, scalar) = match segment.command {
            ControlCommand::Controlled {
                lift_load_factor,
                bank_angle,
            } => (ControlFamily::Controlled, bank_angle, lift_load_factor),
            ControlCommand::Uncontrolled {
                lift_coefficient,
                bank_angle,
            } => (ControlFamily::Uncontrolled, bank_angle, lift_coefficient),
        };
        if command_family != expected_family {
            return Err("control commands must match the named control family");
        }
        if !scalar.is_finite() || (command_family == ControlFamily::Controlled && scalar < 0.0) {
            return Err("control command scalar is invalid");
        }
        if !bank.is_finite() || bank.0.abs() > aerodynamics.maximum_bank_angle.0 {
            return Err("control bank exceeds the declared aerodynamic bound");
        }
    }
    Ok(())
}

fn validate_control_transition_policy(
    input: &TransitionKernelInput,
    policy: &ControlledToUncontrolledPolicy,
) -> Result<(), ControlledToUncontrolledError> {
    if policy.scenario.label.trim().is_empty() {
        return Err(ControlledToUncontrolledError::EmptyScenarioLabel);
    }
    if input.family.control != ControlFamily::Controlled {
        return Err(ControlledToUncontrolledError::InputFamilyMustBeControlled {
            actual: input.family.control,
        });
    }
    if input.control != policy.pre_trigger_controlled {
        return Err(ControlledToUncontrolledError::PreTriggerScheduleMismatch);
    }
    validate_control_schedule(
        &policy.pre_trigger_controlled,
        ControlFamily::Controlled,
        input.aerodynamics,
    )
    .map_err(|reason| ControlledToUncontrolledError::InvalidPreTriggerSchedule { reason })?;
    validate_control_schedule(
        &policy.post_trigger_uncontrolled,
        ControlFamily::Uncontrolled,
        input.aerodynamics,
    )
    .map_err(|reason| ControlledToUncontrolledError::InvalidPostTriggerSchedule { reason })?;

    let already_occurred = match policy.scenario.trigger {
        ControlTransitionTrigger::DualEngineFlameout => {
            input.initial.engines.left.mode != EngineMode::Running
                && input.initial.engines.right.mode != EngineMode::Running
        }
        ControlTransitionTrigger::DualEngineGeneratorLoss => input
            .initial
            .electrical
            .dual_engine_generator_loss_elapsed
            .is_some(),
    };
    if already_occurred {
        return Err(ControlledToUncontrolledError::TriggerAlreadyOccurred {
            trigger: policy.scenario.trigger,
        });
    }
    Ok(())
}

fn validate_input(input: &TransitionKernelInput) -> Result<(), TransitionError> {
    let flight = input.initial.flight;
    if !flight.time.is_finite()
        || !flight.position.latitude.is_finite()
        || !flight.position.longitude.is_finite()
        || !flight.altitude.is_finite()
        || !flight.true_airspeed.is_finite()
        || !flight.flight_path_angle.is_finite()
        || !flight.heading_true.is_finite()
    {
        return Err(TransitionError::InvalidInput(
            "initial point-mass state must be finite",
        ));
    }
    if flight.true_airspeed.0 <= 0.0 {
        return Err(TransitionError::InvalidInput(
            "initial true airspeed must be positive",
        ));
    }
    if flight.flight_path_angle.0.abs() >= 90.0 {
        return Err(TransitionError::InvalidInput(
            "initial flight-path angle must be between -90 and 90 degrees",
        ));
    }

    validate_nonnegative(
        input.initial.mass.non_fuel_mass.0,
        "non-fuel mass must be finite and nonnegative",
    )?;
    if input.initial.mass.non_fuel_mass.0 <= 0.0 {
        return Err(TransitionError::InvalidInput(
            "non-fuel mass must be positive",
        ));
    }
    for value in [
        input.initial.fuel.left_engine_feed.0,
        input.initial.fuel.right_engine_feed.0,
        input.initial.fuel.apu_feed.0,
        input.initial.fuel.unusable.0,
    ] {
        validate_nonnegative(value, "fuel masses must be finite and nonnegative")?;
    }
    validate_engine(input.initial.engines.left)?;
    validate_engine(input.initial.engines.right)?;

    if !input.initial.apu.elapsed_in_mode.is_finite() || input.initial.apu.elapsed_in_mode.0 < 0.0 {
        return Err(TransitionError::InvalidInput(
            "APU elapsed time must be finite and nonnegative",
        ));
    }
    validate_nonnegative(
        input.initial.apu.fuel_flow.0,
        "APU fuel flow must be finite and nonnegative",
    )?;
    match input.initial.apu.mode {
        ApuMode::Off | ApuMode::Unavailable => {
            if input.initial.apu.generator_online || input.initial.apu.fuel_flow.0 != 0.0 {
                return Err(TransitionError::InvalidInput(
                    "off/unavailable APU cannot have generator or fuel flow",
                ));
            }
        }
        ApuMode::Starting => {
            if input.initial.apu.generator_online {
                return Err(TransitionError::InvalidInput(
                    "starting APU generator cannot already be online",
                ));
            }
        }
        ApuMode::Running => {}
    }

    let expected_source = expected_electrical_source(input.initial.engines, input.initial.apu);
    if input.initial.electrical.source != expected_source {
        return Err(TransitionError::InvalidInput(
            "electrical source is inconsistent with engine/APU generator state",
        ));
    }
    if input.initial.electrical.satcom_powered != (expected_source != ElectricalSource::Unpowered) {
        return Err(TransitionError::InvalidInput(
            "SATCOM power is inconsistent with electrical source",
        ));
    }
    let engine_generator_online = input.initial.engines.left.active_generator()
        || input.initial.engines.right.active_generator();
    match (
        engine_generator_online,
        input.initial.electrical.dual_engine_generator_loss_elapsed,
    ) {
        (true, Some(_)) => {
            return Err(TransitionError::InvalidInput(
                "dual-generator-loss elapsed time cannot be set while an engine generator is online",
            ));
        }
        (false, None) => {
            return Err(TransitionError::InvalidInput(
                "dual-generator-loss elapsed time is required after both engine generators are lost",
            ));
        }
        (_, Some(elapsed)) if !elapsed.is_finite() || elapsed.0 < 0.0 => {
            return Err(TransitionError::InvalidInput(
                "dual-generator-loss elapsed time must be finite and nonnegative",
            ));
        }
        _ => {}
    }

    let ocxo_powered = input.initial.ocxo.power == OcxoPowerState::Powered;
    if ocxo_powered != input.initial.electrical.satcom_powered {
        return Err(TransitionError::InvalidInput(
            "OCXO power must be consistent with SATCOM power",
        ));
    }
    if !input.initial.ocxo.unpowered_duration.is_finite()
        || input.initial.ocxo.unpowered_duration.0 < 0.0
        || (ocxo_powered && input.initial.ocxo.unpowered_duration.0 != 0.0)
    {
        return Err(TransitionError::InvalidInput(
            "OCXO outage duration is inconsistent or invalid",
        ));
    }

    if !input.model_weight.0.is_finite() || input.model_weight.0 < 0.0 {
        return Err(TransitionError::InvalidInput(
            "model weight must be finite and nonnegative",
        ));
    }

    let aero = input.aerodynamics;
    if !aero.reference_area.is_finite() || aero.reference_area.0 <= 0.0 {
        return Err(TransitionError::InvalidInput(
            "reference area must be finite and positive",
        ));
    }
    for (value, message) in [
        (
            aero.zero_lift_drag_coefficient,
            "zero-lift drag coefficient must be finite and nonnegative",
        ),
        (
            aero.induced_drag_factor,
            "induced drag factor must be finite and nonnegative",
        ),
    ] {
        validate_nonnegative(value, message)?;
    }
    if !aero.minimum_lift_coefficient.is_finite()
        || !aero.maximum_lift_coefficient.is_finite()
        || aero.minimum_lift_coefficient > aero.maximum_lift_coefficient
    {
        return Err(TransitionError::InvalidInput(
            "lift-coefficient bounds must be finite and ordered",
        ));
    }
    if !aero.maximum_bank_angle.is_finite() || !(0.0..90.0).contains(&aero.maximum_bank_angle.0) {
        return Err(TransitionError::InvalidInput(
            "maximum bank angle must be finite and between 0 and 90 degrees",
        ));
    }
    if !aero.minimum_true_airspeed.is_finite()
        || !aero.maximum_true_airspeed.is_finite()
        || aero.minimum_true_airspeed.0 <= 0.0
        || aero.minimum_true_airspeed.0 >= aero.maximum_true_airspeed.0
    {
        return Err(TransitionError::InvalidInput(
            "airspeed validity bounds must be finite, positive, and ordered",
        ));
    }

    validate_control_schedule(&input.control, input.family.control, aero)
        .map_err(TransitionError::InvalidInput)?;

    if input.atmosphere.nodes.is_empty() {
        return Err(TransitionError::InvalidInput(
            "atmosphere profile must contain at least one node",
        ));
    }
    let mut previous_altitude = f64::NEG_INFINITY;
    for node in &input.atmosphere.nodes {
        if !node.altitude.is_finite()
            || !node.density.is_finite()
            || !node.wind_north.is_finite()
            || !node.wind_east.is_finite()
            || node.density.0 < 0.0
            || node.altitude.0 <= previous_altitude
        {
            return Err(TransitionError::InvalidInput(
                "atmosphere nodes must be finite, nonnegative in density, and altitude ordered",
            ));
        }
        previous_altitude = node.altitude.0;
    }

    if !input.integration.time_step.is_finite()
        || !input.integration.maximum_duration.is_finite()
        || !input.integration.sea_surface_altitude.is_finite()
        || input.integration.time_step.0 <= 0.0
        || input.integration.maximum_duration.0 < 0.0
        || input.integration.maximum_steps == 0
    {
        return Err(TransitionError::InvalidInput(
            "integration settings are invalid",
        ));
    }

    match input.apu_start_policy {
        ApuStartPolicy::Disabled => {
            if input.initial.apu.mode == ApuMode::Starting {
                return Err(TransitionError::InvalidInput(
                    "a starting APU requires an explicit start policy",
                ));
            }
        }
        ApuStartPolicy::OnDualEngineGeneratorLoss {
            start_delay,
            start_fuel,
            generator_delay,
            running_fuel_flow,
        } => {
            for (value, message) in [
                (start_delay.0, "APU start delay must be nonnegative"),
                (start_fuel.0, "APU start fuel must be nonnegative"),
                (generator_delay.0, "APU generator delay must be nonnegative"),
                (
                    running_fuel_flow.0,
                    "APU running fuel flow must be nonnegative",
                ),
            ] {
                validate_nonnegative(value, message)?;
            }
        }
    }

    Ok(())
}

impl ControlSchedule {
    fn command_at(&self, elapsed_s: f64) -> ControlCommand {
        self.segments
            .iter()
            .rev()
            .find(|segment| segment.start_offset.0 <= elapsed_s + EVENT_EPSILON_S)
            .expect("validated schedule begins at zero")
            .command
    }

    fn next_boundary_after(&self, elapsed_s: f64) -> Option<f64> {
        self.segments
            .iter()
            .map(|segment| segment.start_offset.0)
            .find(|start| *start > elapsed_s + EVENT_EPSILON_S)
    }
}

impl AtmosphereProfile {
    fn sample_altitude(&self, altitude_ft: f64) -> TransitionAtmosphereSample {
        let first = self.nodes[0];
        if altitude_ft <= first.altitude.0 {
            return TransitionAtmosphereSample {
                density: first.density,
                wind_north: first.wind_north,
                wind_east: first.wind_east,
            };
        }

        for pair in self.nodes.windows(2) {
            let lower = pair[0];
            let upper = pair[1];
            if altitude_ft <= upper.altitude.0 {
                let fraction =
                    (altitude_ft - lower.altitude.0) / (upper.altitude.0 - lower.altitude.0);
                return TransitionAtmosphereSample {
                    density: KilogramsPerCubicMetre(
                        lower.density.0 + fraction * (upper.density.0 - lower.density.0),
                    ),
                    wind_north: MetresPerSecond(
                        lower.wind_north.0 + fraction * (upper.wind_north.0 - lower.wind_north.0),
                    ),
                    wind_east: MetresPerSecond(
                        lower.wind_east.0 + fraction * (upper.wind_east.0 - lower.wind_east.0),
                    ),
                };
            }
        }

        let last = *self.nodes.last().expect("validated non-empty atmosphere");
        TransitionAtmosphereSample {
            density: last.density,
            wind_north: last.wind_north,
            wind_east: last.wind_east,
        }
    }
}

impl TransitionAtmosphere for AtmosphereProfile {
    fn sample(
        &self,
        _time: Seconds,
        _position: LatLon,
        pressure_altitude: Feet,
    ) -> Result<TransitionAtmosphereSample, TransitionAtmosphereError> {
        let sample = self.sample_altitude(pressure_altitude.0);
        validate_atmosphere_sample(sample)?;
        Ok(sample)
    }
}

fn validate_atmosphere_sample(
    sample: TransitionAtmosphereSample,
) -> Result<(), TransitionAtmosphereError> {
    if !sample.density.is_finite()
        || !sample.wind_north.is_finite()
        || !sample.wind_east.is_finite()
        || sample.density.0 < 0.0
    {
        Err(TransitionAtmosphereError::InvalidSample)
    } else {
        Ok(())
    }
}

fn total_mass_kg(mass: MassState, fuel: FuelState) -> f64 {
    mass.non_fuel_mass.0 + fuel.total_mass().0
}

fn active_thrust_newtons(engines: EngineSystemState) -> f64 {
    engines.left.active_thrust() + engines.right.active_thrust()
}

fn atmosphere_at(
    state: &ContinuousState,
    atmosphere: &dyn TransitionAtmosphere,
) -> Result<TransitionAtmosphereSample, TransitionError> {
    let sample = atmosphere.sample(
        Seconds(state.absolute_time_s),
        state.position,
        Feet(state.altitude_m * FEET_PER_METRE),
    )?;
    validate_atmosphere_sample(sample)?;
    Ok(sample)
}

fn motion_at(
    state: &ContinuousState,
    atmosphere: &dyn TransitionAtmosphere,
) -> Result<Motion, TransitionError> {
    let sample = atmosphere_at(state, atmosphere)?;
    let horizontal_air = state.true_airspeed_m_s * state.flight_path_angle_rad.cos();
    Ok(Motion {
        north_m_s: horizontal_air * state.heading_rad.cos() + sample.wind_north.0,
        east_m_s: horizontal_air * state.heading_rad.sin() + sample.wind_east.0,
        vertical_m_s: state.true_airspeed_m_s * state.flight_path_angle_rad.sin(),
    })
}

fn derivative(
    state: &ContinuousState,
    mass_kg: f64,
    thrust_newtons: f64,
    command: ControlCommand,
    aerodynamics: AerodynamicModel,
    atmosphere: &dyn TransitionAtmosphere,
) -> Result<Derivative, TransitionError> {
    if !mass_kg.is_finite() || mass_kg <= 0.0 {
        return Err(TransitionError::NonFinitePropagation);
    }
    let cosine_gamma = state.flight_path_angle_rad.cos();
    if cosine_gamma.abs() < 1.0e-3 {
        return Err(TransitionError::InvalidInput(
            "point-mass turn equation is singular near vertical flight",
        ));
    }

    let sample = atmosphere_at(state, atmosphere)?;
    let dynamic_pressure_area =
        0.5 * sample.density.0 * state.true_airspeed_m_s.powi(2) * aerodynamics.reference_area.0;

    let (requested_cl, bank_rad) = match command {
        ControlCommand::Controlled {
            lift_load_factor,
            bank_angle,
        } => {
            if dynamic_pressure_area <= 0.0 && lift_load_factor > 0.0 {
                return Err(TransitionError::InvalidInput(
                    "controlled lift requires positive dynamic pressure",
                ));
            }
            let requested = if dynamic_pressure_area > 0.0 {
                lift_load_factor * mass_kg * STANDARD_GRAVITY_M_S2 / dynamic_pressure_area
            } else {
                0.0
            };
            (requested, bank_angle.to_radians())
        }
        ControlCommand::Uncontrolled {
            lift_coefficient,
            bank_angle,
        } => (lift_coefficient, bank_angle.to_radians()),
    };
    let applied_cl = requested_cl.clamp(
        aerodynamics.minimum_lift_coefficient,
        aerodynamics.maximum_lift_coefficient,
    );
    let lift_newtons = dynamic_pressure_area * applied_cl;
    let drag_coefficient = aerodynamics.zero_lift_drag_coefficient
        + aerodynamics.induced_drag_factor * applied_cl.powi(2);
    let drag_newtons = dynamic_pressure_area * drag_coefficient;

    let airspeed_m_s2 = (thrust_newtons - drag_newtons) / mass_kg
        - STANDARD_GRAVITY_M_S2 * state.flight_path_angle_rad.sin();
    let flight_path_angle_rad_s = (lift_newtons * bank_rad.cos() / mass_kg
        - STANDARD_GRAVITY_M_S2 * state.flight_path_angle_rad.cos())
        / state.true_airspeed_m_s;
    let heading_rad_s =
        lift_newtons * bank_rad.sin() / (mass_kg * state.true_airspeed_m_s * cosine_gamma);
    let motion = motion_at(state, atmosphere)?;

    let values = [
        airspeed_m_s2,
        flight_path_angle_rad_s,
        heading_rad_s,
        motion.vertical_m_s,
        motion.north_m_s,
        motion.east_m_s,
        requested_cl,
        applied_cl,
    ];
    if values.iter().any(|value| !value.is_finite()) {
        return Err(TransitionError::NonFinitePropagation);
    }

    Ok(Derivative {
        airspeed_m_s2,
        flight_path_angle_rad_s,
        heading_rad_s,
        altitude_m_s: motion.vertical_m_s,
        ground_north_m_s: motion.north_m_s,
        ground_east_m_s: motion.east_m_s,
        requested_cl,
        applied_cl,
    })
}
fn advance_position(
    start: LatLon,
    north_m_s: f64,
    east_m_s: f64,
    duration_s: f64,
) -> Result<LatLon, TransitionError> {
    let speed_m_s = north_m_s.hypot(east_m_s);
    if speed_m_s == 0.0 || duration_s == 0.0 {
        return Ok(start);
    }
    let bearing = Degrees(east_m_s.atan2(north_m_s).to_degrees()).wrapped_360();
    Ok(destination_wgs84(
        start,
        bearing,
        NauticalMiles(speed_m_s * duration_s / METRES_PER_NAUTICAL_MILE),
    )?)
}

fn midpoint_step(
    state: &ContinuousState,
    duration_s: f64,
    mass: StepMass,
    thrust_newtons: f64,
    command: ControlCommand,
    aerodynamics: AerodynamicModel,
    atmosphere: &dyn TransitionAtmosphere,
) -> Result<(ContinuousState, Derivative), TransitionError> {
    let first = derivative(
        state,
        mass.start_kg,
        thrust_newtons,
        command,
        aerodynamics,
        atmosphere,
    )?;
    let midpoint = ContinuousState {
        absolute_time_s: state.absolute_time_s + 0.5 * duration_s,
        position: state.position,
        altitude_m: state.altitude_m + 0.5 * duration_s * first.altitude_m_s,
        true_airspeed_m_s: state.true_airspeed_m_s + 0.5 * duration_s * first.airspeed_m_s2,
        flight_path_angle_rad: state.flight_path_angle_rad
            + 0.5 * duration_s * first.flight_path_angle_rad_s,
        heading_rad: state.heading_rad + 0.5 * duration_s * first.heading_rad_s,
    };
    let middle = derivative(
        &midpoint,
        mass.midpoint_kg.max(f64::MIN_POSITIVE),
        thrust_newtons,
        command,
        aerodynamics,
        atmosphere,
    )?;
    let next = ContinuousState {
        absolute_time_s: state.absolute_time_s + duration_s,
        position: advance_position(
            state.position,
            middle.ground_north_m_s,
            middle.ground_east_m_s,
            duration_s,
        )?,
        altitude_m: state.altitude_m + duration_s * middle.altitude_m_s,
        true_airspeed_m_s: state.true_airspeed_m_s + duration_s * middle.airspeed_m_s2,
        flight_path_angle_rad: state.flight_path_angle_rad
            + duration_s * middle.flight_path_angle_rad_s,
        heading_rad: state.heading_rad + duration_s * middle.heading_rad_s,
    };
    if [
        next.absolute_time_s,
        next.altitude_m,
        next.true_airspeed_m_s,
        next.flight_path_angle_rad,
        next.heading_rad,
    ]
    .iter()
    .any(|value| !value.is_finite())
    {
        return Err(TransitionError::NonFinitePropagation);
    }
    Ok((next, middle))
}

fn event_at(runtime: &RuntimeState, kind: TransitionEventKind) -> TransitionEvent {
    TransitionEvent {
        time: Seconds(runtime.continuous.absolute_time_s),
        kind,
    }
}

fn settle_discrete_events(
    runtime: &mut RuntimeState,
    input: &TransitionKernelInput,
    events: &mut Vec<TransitionEvent>,
) -> Result<(), TransitionError> {
    for _ in 0..16 {
        let mut changed = false;

        if runtime.engines.left.mode == EngineMode::Running
            && runtime.fuel.left_engine_feed.0 <= EVENT_EPSILON_S
        {
            runtime.fuel.left_engine_feed.0 = 0.0;
            runtime.engines.left.flame_out();
            events.push(event_at(
                runtime,
                TransitionEventKind::EngineFlameout {
                    engine: EngineSide::Left,
                },
            ));
            changed = true;
        }
        if runtime.engines.right.mode == EngineMode::Running
            && runtime.fuel.right_engine_feed.0 <= EVENT_EPSILON_S
        {
            runtime.fuel.right_engine_feed.0 = 0.0;
            runtime.engines.right.flame_out();
            events.push(event_at(
                runtime,
                TransitionEventKind::EngineFlameout {
                    engine: EngineSide::Right,
                },
            ));
            changed = true;
        }
        if runtime.apu.mode == ApuMode::Running
            && runtime.apu.fuel_flow.0 > 0.0
            && runtime.fuel.apu_feed.0 <= EVENT_EPSILON_S
        {
            runtime.fuel.apu_feed.0 = 0.0;
            runtime.apu = ApuState {
                mode: ApuMode::Unavailable,
                elapsed_in_mode: Seconds(0.0),
                generator_online: false,
                fuel_flow: KilogramsPerSecond(0.0),
            };
            events.push(event_at(runtime, TransitionEventKind::ApuFuelExhausted));
            changed = true;
        }

        let engine_generator_online =
            runtime.engines.left.active_generator() || runtime.engines.right.active_generator();
        if !engine_generator_online
            && runtime
                .electrical
                .dual_engine_generator_loss_elapsed
                .is_none()
        {
            runtime.electrical.dual_engine_generator_loss_elapsed = Some(Seconds(0.0));
            events.push(event_at(
                runtime,
                TransitionEventKind::DualEngineGeneratorLoss,
            ));
            changed = true;
        }

        if let ApuStartPolicy::OnDualEngineGeneratorLoss {
            start_delay,
            start_fuel,
            ..
        } = input.apu_start_policy
        {
            let start_due = runtime.apu.mode == ApuMode::Off
                && runtime
                    .electrical
                    .dual_engine_generator_loss_elapsed
                    .is_some_and(|elapsed| elapsed.0 + EVENT_EPSILON_S >= start_delay.0);
            if start_due {
                if runtime.fuel.apu_feed.0 + EVENT_EPSILON_S >= start_fuel.0 {
                    runtime.fuel.apu_feed.0 = (runtime.fuel.apu_feed.0 - start_fuel.0).max(0.0);
                    runtime.apu = ApuState {
                        mode: ApuMode::Starting,
                        elapsed_in_mode: Seconds(0.0),
                        generator_online: false,
                        fuel_flow: KilogramsPerSecond(0.0),
                    };
                    events.push(event_at(runtime, TransitionEventKind::ApuStart));
                } else {
                    runtime.apu = ApuState {
                        mode: ApuMode::Unavailable,
                        elapsed_in_mode: Seconds(0.0),
                        generator_online: false,
                        fuel_flow: KilogramsPerSecond(0.0),
                    };
                    events.push(event_at(
                        runtime,
                        TransitionEventKind::ApuStartFailedInsufficientFuel,
                    ));
                }
                changed = true;
            }
        }

        if let ApuStartPolicy::OnDualEngineGeneratorLoss {
            generator_delay,
            running_fuel_flow,
            ..
        } = input.apu_start_policy
        {
            if runtime.apu.mode == ApuMode::Starting
                && runtime.apu.elapsed_in_mode.0 + EVENT_EPSILON_S >= generator_delay.0
            {
                runtime.apu = ApuState {
                    mode: ApuMode::Running,
                    elapsed_in_mode: Seconds(0.0),
                    generator_online: true,
                    fuel_flow: running_fuel_flow,
                };
                events.push(event_at(runtime, TransitionEventKind::ApuGeneratorOnline));
                changed = true;
            }
        }

        let old_satcom_powered = runtime.electrical.satcom_powered;
        let source = expected_electrical_source(runtime.engines, runtime.apu);
        let new_satcom_powered = source != ElectricalSource::Unpowered;
        if source != runtime.electrical.source {
            runtime.electrical.source = source;
            changed = true;
        }
        if new_satcom_powered != old_satcom_powered {
            runtime.electrical.satcom_powered = new_satcom_powered;
            changed = true;
            if new_satcom_powered {
                events.push(event_at(runtime, TransitionEventKind::SatcomPowerRestored));
                let outage_duration = runtime.ocxo.unpowered_duration;
                runtime.ocxo = OcxoState {
                    power: OcxoPowerState::Powered,
                    unpowered_duration: Seconds(0.0),
                    restart_count: runtime.ocxo.restart_count.saturating_add(1),
                };
                events.push(event_at(
                    runtime,
                    TransitionEventKind::OcxoRestart {
                        family: input.family.restart_transient,
                        outage_duration,
                    },
                ));
            } else {
                events.push(event_at(runtime, TransitionEventKind::SatcomPowerLost));
                runtime.ocxo.power = OcxoPowerState::Unpowered;
                runtime.ocxo.unpowered_duration = Seconds(0.0);
            }
        }

        if !changed {
            return Ok(());
        }
    }

    Err(TransitionError::InvalidInput(
        "discrete system events did not settle",
    ))
}

fn advance_system_state(runtime: &mut RuntimeState, duration_s: f64) {
    runtime.fuel.left_engine_feed.0 = (runtime.fuel.left_engine_feed.0
        - runtime.engines.left.active_fuel_flow() * duration_s)
        .max(0.0);
    runtime.fuel.right_engine_feed.0 = (runtime.fuel.right_engine_feed.0
        - runtime.engines.right.active_fuel_flow() * duration_s)
        .max(0.0);
    if runtime.apu.mode == ApuMode::Running {
        runtime.fuel.apu_feed.0 =
            (runtime.fuel.apu_feed.0 - runtime.apu.fuel_flow.0 * duration_s).max(0.0);
    }
    if matches!(runtime.apu.mode, ApuMode::Starting | ApuMode::Running) {
        runtime.apu.elapsed_in_mode.0 += duration_s;
    }
    if let Some(elapsed) = &mut runtime.electrical.dual_engine_generator_loss_elapsed {
        elapsed.0 += duration_s;
    }
    if runtime.ocxo.power == OcxoPowerState::Unpowered {
        runtime.ocxo.unpowered_duration.0 += duration_s;
    }
    runtime.elapsed_s += duration_s;
}

fn time_until_next_event(
    runtime: &RuntimeState,
    input: &TransitionKernelInput,
    policy: Option<&ControlledToUncontrolledPolicy>,
    control_transition: Option<&ControlModeTransitionEvent>,
) -> Option<f64> {
    let mut next = f64::INFINITY;
    let mut consider = |candidate: f64| {
        if candidate > EVENT_EPSILON_S && candidate < next {
            next = candidate;
        }
    };

    let left_flow = runtime.engines.left.active_fuel_flow();
    if left_flow > 0.0 {
        consider(runtime.fuel.left_engine_feed.0 / left_flow);
    }
    let right_flow = runtime.engines.right.active_fuel_flow();
    if right_flow > 0.0 {
        consider(runtime.fuel.right_engine_feed.0 / right_flow);
    }
    if runtime.apu.mode == ApuMode::Running && runtime.apu.fuel_flow.0 > 0.0 {
        consider(runtime.fuel.apu_feed.0 / runtime.apu.fuel_flow.0);
    }

    if let ApuStartPolicy::OnDualEngineGeneratorLoss {
        start_delay,
        generator_delay,
        ..
    } = input.apu_start_policy
    {
        if runtime.apu.mode == ApuMode::Off {
            if let Some(elapsed) = runtime.electrical.dual_engine_generator_loss_elapsed {
                consider(start_delay.0 - elapsed.0);
            }
        } else if runtime.apu.mode == ApuMode::Starting {
            consider(generator_delay.0 - runtime.apu.elapsed_in_mode.0);
        }
    }

    match (policy, control_transition) {
        (Some(policy), Some(transition)) => {
            let post_trigger_elapsed_s = runtime.elapsed_s - transition.elapsed.0;
            if let Some(boundary) = policy
                .post_trigger_uncontrolled
                .next_boundary_after(post_trigger_elapsed_s)
            {
                consider(boundary - post_trigger_elapsed_s);
            }
        }
        (Some(policy), None) => {
            if let Some(boundary) = policy
                .pre_trigger_controlled
                .next_boundary_after(runtime.elapsed_s)
            {
                consider(boundary - runtime.elapsed_s);
            }
        }
        (None, _) => {
            if let Some(boundary) = input.control.next_boundary_after(runtime.elapsed_s) {
                consider(boundary - runtime.elapsed_s);
            }
        }
    }

    next.is_finite().then_some(next)
}

fn envelope_exit(
    runtime: &RuntimeState,
    aerodynamics: AerodynamicModel,
) -> Option<DeclaredEnvelopeExit> {
    let airspeed = runtime.continuous.true_airspeed_m_s;
    if airspeed < aerodynamics.minimum_true_airspeed.0 {
        Some(DeclaredEnvelopeExit::AirspeedBelowMinimum)
    } else if airspeed > aerodynamics.maximum_true_airspeed.0 {
        Some(DeclaredEnvelopeExit::AirspeedAboveMaximum)
    } else if runtime.continuous.flight_path_angle_rad.cos().abs() < 1.0e-3 {
        Some(DeclaredEnvelopeExit::NearVerticalFlightPath)
    } else {
        None
    }
}

fn terminal_state(
    runtime: &RuntimeState,
    input: &TransitionKernelInput,
    atmosphere: &dyn TransitionAtmosphere,
) -> Result<TransitionTerminalState, TransitionError> {
    let motion = motion_at(&runtime.continuous, atmosphere)?;
    let ground_speed = motion.north_m_s.hypot(motion.east_m_s);
    let ground_track = if ground_speed > 0.0 {
        Degrees(motion.east_m_s.atan2(motion.north_m_s).to_degrees()).wrapped_360()
    } else {
        Degrees(runtime.continuous.heading_rad.to_degrees()).wrapped_360()
    };
    Ok(TransitionTerminalState {
        kinematics: TerminalKinematics {
            point_mass: PointMassState {
                time: Seconds(runtime.continuous.absolute_time_s),
                position: runtime.continuous.position,
                altitude: Feet(runtime.continuous.altitude_m * FEET_PER_METRE),
                true_airspeed: MetresPerSecond(runtime.continuous.true_airspeed_m_s),
                flight_path_angle: Degrees(runtime.continuous.flight_path_angle_rad.to_degrees()),
                heading_true: Degrees(runtime.continuous.heading_rad.to_degrees()).wrapped_360(),
            },
            ground_speed: MetresPerSecond(ground_speed),
            ground_track_true: ground_track,
            vertical_speed: MetresPerSecond(motion.vertical_m_s),
        },
        mass: Kilograms(total_mass_kg(input.initial.mass, runtime.fuel)),
        fuel: runtime.fuel,
        engines: runtime.engines,
        electrical: runtime.electrical,
        apu: runtime.apu,
        ocxo: runtime.ocxo,
    })
}

fn selected_control_command(
    input: &TransitionKernelInput,
    policy: Option<&ControlledToUncontrolledPolicy>,
    control_transition: Option<&ControlModeTransitionEvent>,
    elapsed_s: f64,
) -> ControlCommand {
    match (policy, control_transition) {
        (Some(policy), Some(transition)) => policy
            .post_trigger_uncontrolled
            .command_at((elapsed_s - transition.elapsed.0).max(0.0)),
        (Some(policy), None) => policy.pre_trigger_controlled.command_at(elapsed_s),
        (None, _) => input.control.command_at(elapsed_s),
    }
}

fn apply_control_transition_if_triggered(
    runtime: &RuntimeState,
    input: &TransitionKernelInput,
    new_events: &[TransitionEvent],
    policy: Option<&ControlledToUncontrolledPolicy>,
    control_transition: &mut Option<ControlModeTransitionEvent>,
    atmosphere: &dyn TransitionAtmosphere,
) -> Result<(), TransitionError> {
    let Some(policy) = policy else {
        return Ok(());
    };
    if control_transition.is_some() {
        return Ok(());
    }

    let triggered = match policy.scenario.trigger {
        ControlTransitionTrigger::DualEngineFlameout => {
            let flameout_event = new_events
                .iter()
                .any(|event| matches!(event.kind, TransitionEventKind::EngineFlameout { .. }));
            flameout_event
                && runtime.engines.left.mode != EngineMode::Running
                && runtime.engines.right.mode != EngineMode::Running
        }
        ControlTransitionTrigger::DualEngineGeneratorLoss => new_events
            .iter()
            .any(|event| matches!(event.kind, TransitionEventKind::DualEngineGeneratorLoss)),
    };
    if !triggered {
        return Ok(());
    }

    *control_transition = Some(ControlModeTransitionEvent {
        time: Seconds(runtime.continuous.absolute_time_s),
        elapsed: Seconds(runtime.elapsed_s),
        trigger: policy.scenario.trigger,
        from: ControlFamily::Controlled,
        to: ControlFamily::Uncontrolled,
        pre_trigger_command: policy.pre_trigger_controlled.command_at(runtime.elapsed_s),
        post_trigger_command: policy.post_trigger_uncontrolled.command_at(0.0),
        state: terminal_state(runtime, input, atmosphere)?,
    });
    Ok(())
}

#[derive(Debug, Clone, Copy)]
struct ActiveControlSelection<'a> {
    policy: Option<&'a ControlledToUncontrolledPolicy>,
    transition: Option<&'a ControlModeTransitionEvent>,
}

fn capture_due_checkpoint(
    runtime: &mut RuntimeState,
    input: &TransitionKernelInput,
    control: ActiveControlSelection<'_>,
    events: &[TransitionEvent],
    schedule: &ExactTimeCheckpointSchedule,
    next_checkpoint_index: &mut usize,
    checkpoints: &mut Vec<ExactTimeCheckpoint>,
    atmosphere: &dyn TransitionAtmosphere,
) -> Result<(), TransitionError> {
    while let Some(requested) = schedule
        .requested_elapsed_times
        .get(*next_checkpoint_index)
        .copied()
    {
        let difference_s = requested.0 - runtime.elapsed_s;
        if difference_s > 0.0 {
            break;
        }
        if difference_s < -EVENT_EPSILON_S {
            return Err(TransitionError::InvalidInput(
                "integration passed an exact-time checkpoint",
            ));
        }

        runtime.elapsed_s = requested.0;
        runtime.continuous.absolute_time_s = input.initial.flight.time.0 + requested.0;
        let absolute_time_s = runtime.continuous.absolute_time_s;
        checkpoints.push(ExactTimeCheckpoint {
            requested_elapsed: requested,
            state: terminal_state(runtime, input, atmosphere)?,
            active_control: selected_control_command(
                input,
                control.policy,
                control.transition,
                requested.0,
            ),
            events_at_time: events
                .iter()
                .filter(|event| (event.time.0 - absolute_time_s).abs() <= EVENT_EPSILON_S)
                .map(|event| event.kind.clone())
                .collect(),
        });
        *next_checkpoint_index += 1;
    }
    Ok(())
}
fn impact_data(
    runtime: &RuntimeState,
    input: &TransitionKernelInput,
    atmosphere: &dyn TransitionAtmosphere,
) -> Result<ImpactData, TransitionError> {
    let terminal = terminal_state(runtime, input, atmosphere)?;
    let horizontal_speed = terminal.kinematics.ground_speed.0;
    let vertical_speed = terminal.kinematics.vertical_speed.0;
    let mass = terminal.mass.0;
    let horizontal_energy = 0.5 * mass * horizontal_speed.powi(2);
    let vertical_energy = 0.5 * mass * vertical_speed.powi(2);
    let displacement = great_circle_distance_nm(
        input.initial.flight.position,
        terminal.kinematics.point_mass.position,
    );
    Ok(ImpactData {
        point: ImpactPoint {
            time: terminal.kinematics.point_mass.time,
            position: terminal.kinematics.point_mass.position,
            bearing_true: terminal.kinematics.ground_track_true,
            displacement_from_last_contact: displacement,
        },
        mass: terminal.mass,
        true_airspeed: terminal.kinematics.point_mass.true_airspeed,
        ground_speed: terminal.kinematics.ground_speed,
        vertical_speed: terminal.kinematics.vertical_speed,
        impact_angle: Degrees((-vertical_speed).atan2(horizontal_speed).to_degrees()),
        kinetic_energy: Joules(horizontal_energy + vertical_energy),
        horizontal_kinetic_energy: Joules(horizontal_energy),
        vertical_kinetic_energy: Joules(vertical_energy),
    })
}

fn finished_transition(
    runtime: &RuntimeState,
    input: &TransitionKernelInput,
    events: Vec<TransitionEvent>,
    termination: TransitionTermination,
    atmosphere: &dyn TransitionAtmosphere,
) -> Result<WeightedTransition, TransitionError> {
    let impact = if termination == TransitionTermination::Impact {
        Some(impact_data(runtime, input, atmosphere)?)
    } else {
        None
    };
    Ok(WeightedTransition {
        family: input.family,
        model_weight: input.model_weight,
        terminal: terminal_state(runtime, input, atmosphere)?,
        events,
        termination,
        impact,
    })
}

fn finished_run(
    runtime: &RuntimeState,
    input: &TransitionKernelInput,
    events: Vec<TransitionEvent>,
    termination: TransitionTermination,
    checkpoints: Vec<ExactTimeCheckpoint>,
    control_transition: Option<ControlModeTransitionEvent>,
    atmosphere: &dyn TransitionAtmosphere,
) -> Result<PropagationRun, TransitionError> {
    Ok(PropagationRun {
        transition: finished_transition(runtime, input, events, termination, atmosphere)?,
        checkpoints,
        control_transition,
    })
}

/// Propagate one explicitly weighted, conditional physical hypothesis.
///
/// The function is deterministic. It does not sample a family, normalise weights, inspect
/// SATCOM observations, or infer an OCXO correction. This API is preserved exactly; use
/// propagate_transition_with_checkpoints when intermediate state is required.
pub fn propagate_transition(
    input: &TransitionKernelInput,
) -> Result<WeightedTransition, TransitionError> {
    validate_input(input)?;
    let run = propagate_transition_validated(
        input,
        &ExactTimeCheckpointSchedule::default(),
        None,
        &input.atmosphere,
    )?;
    Ok(run.transition)
}

/// Propagate while returning complete state at every exact requested elapsed time.
///
/// Requested times become integration boundaries. At a fuel, electrical, APU, or restart
/// event time, all co-temporal discrete events are settled before the snapshot. Impact is
/// terminal and therefore precedes any otherwise co-temporal post-impact system event.
/// If physical or declared-envelope termination occurs before a request, the function
/// returns Unreached instead of silently returning an incomplete checkpoint vector.
pub fn propagate_transition_with_checkpoints(
    input: &TransitionKernelInput,
    schedule: &ExactTimeCheckpointSchedule,
) -> Result<CheckpointedTransition, ExactTimeCheckpointError> {
    validate_input(input)?;
    schedule.validate(input.integration.maximum_duration)?;
    let run = propagate_transition_validated(input, schedule, None, &input.atmosphere)?;
    if run.checkpoints.len() != schedule.requested_elapsed_times.len() {
        return Err(ExactTimeCheckpointError::Unreached {
            requested_elapsed: schedule.requested_elapsed_times[run.checkpoints.len()],
            termination: run.transition.termination,
        });
    }
    Ok(CheckpointedTransition {
        transition: run.transition,
        checkpoints: run.checkpoints,
    })
}

fn validate_controlled_to_uncontrolled_request(
    input: &TransitionKernelInput,
    policy: &ControlledToUncontrolledPolicy,
) -> Result<(), ControlledToUncontrolledError> {
    validate_control_transition_policy(input, policy)?;
    validate_input(input)?;
    Ok(())
}

fn controlled_to_uncontrolled_result(
    input: &TransitionKernelInput,
    policy: &ControlledToUncontrolledPolicy,
    transition: WeightedTransition,
    control_transition: Option<ControlModeTransitionEvent>,
) -> Result<ControlledToUncontrolledResult, ControlledToUncontrolledError> {
    let control_transition = match control_transition {
        Some(transition) => transition,
        None => {
            return Err(ControlledToUncontrolledError::TriggerNotReached {
                trigger: policy.scenario.trigger,
                termination: transition.termination,
            });
        }
    };
    let terminal_elapsed_s =
        transition.terminal.kinematics.point_mass.time.0 - input.initial.flight.time.0;
    let terminal_control = selected_control_command(
        input,
        Some(policy),
        Some(&control_transition),
        terminal_elapsed_s,
    );
    let WeightedTransition {
        model_weight,
        terminal,
        events,
        termination,
        impact,
        ..
    } = transition;

    Ok(ControlledToUncontrolledResult {
        scenario: policy.scenario.clone(),
        restart_transient: input.family.restart_transient,
        model_weight,
        terminal,
        events,
        control_transition,
        terminal_control,
        termination,
        impact,
    })
}

/// Propagate one explicitly labelled controlled-to-uncontrolled conditional scenario.
///
/// The caller, not this kernel, selects the trigger and scenario. No probability, sampling,
/// SATCOM observation, or causal claim is attached to the switch.
pub fn propagate_controlled_to_uncontrolled(
    input: &TransitionKernelInput,
    policy: &ControlledToUncontrolledPolicy,
) -> Result<ControlledToUncontrolledResult, ControlledToUncontrolledError> {
    validate_controlled_to_uncontrolled_request(input, policy)?;

    let run = propagate_transition_validated(
        input,
        &ExactTimeCheckpointSchedule::default(),
        Some(policy),
        &input.atmosphere,
    )?;
    debug_assert!(run.checkpoints.is_empty());
    let transition =
        controlled_to_uncontrolled_result(input, policy, run.transition, run.control_transition)?;
    Ok(transition)
}

/// Attempt one labelled control transition while preserving every physical terminal outcome.
///
/// The deterministic kernel executes exactly once. Physical termination before a checkpoint or
/// before the selected trigger is returned in the typed outcome fields, never converted into an
/// error. Invalid input, policy, schedule, and numerical propagation still return typed errors.
/// A checkpoint coincident with the trigger retains post-event state and the first post-trigger
/// command, exactly as in `propagate_controlled_to_uncontrolled_with_checkpoints`.
pub fn attempt_controlled_to_uncontrolled_with_checkpoints(
    input: &TransitionKernelInput,
    policy: &ControlledToUncontrolledPolicy,
    schedule: &ExactTimeCheckpointSchedule,
) -> Result<ControlledToUncontrolledAttempt, ControlledToUncontrolledAttemptError> {
    attempt_controlled_to_uncontrolled_with_atmosphere_and_checkpoints(
        input,
        policy,
        schedule,
        &input.atmosphere,
    )
}

/// Attempt a controlled-to-uncontrolled transition using a caller-composed dynamic atmosphere.
///
/// The serialized altitude-only profile in `input` is still validated as the deterministic
/// fallback/replay declaration, but every force and ground-motion evaluation in this execution
/// uses `atmosphere`.  The atmosphere assigns no likelihood and cannot alter evidence weights.
pub fn attempt_controlled_to_uncontrolled_with_atmosphere_and_checkpoints(
    input: &TransitionKernelInput,
    policy: &ControlledToUncontrolledPolicy,
    schedule: &ExactTimeCheckpointSchedule,
    atmosphere: &dyn TransitionAtmosphere,
) -> Result<ControlledToUncontrolledAttempt, ControlledToUncontrolledAttemptError> {
    validate_controlled_to_uncontrolled_request(input, policy)?;
    schedule.validate(input.integration.maximum_duration)?;
    let run = propagate_transition_validated(input, schedule, Some(policy), atmosphere)
        .map_err(ControlledToUncontrolledError::from)?;

    let checkpoint_status = schedule
        .requested_elapsed_times
        .get(run.checkpoints.len())
        .copied()
        .map_or(RequestedCheckpointStatus::AllReached, |requested_elapsed| {
            RequestedCheckpointStatus::Unreached {
                next_requested_elapsed: requested_elapsed,
                termination: run.transition.termination,
            }
        });
    let control_transition = run.control_transition.map_or_else(
        || ControlTransitionOutcome::NotReached {
            trigger: policy.scenario.trigger,
            termination: run.transition.termination,
        },
        |event| ControlTransitionOutcome::Reached {
            event: Box::new(event),
        },
    );

    Ok(ControlledToUncontrolledAttempt {
        transition: run.transition,
        checkpoints: run.checkpoints,
        checkpoint_status,
        control_transition,
    })
}

/// Propagate one labelled control-transition scenario and exact checkpoints in one pass.
///
/// Checkpoints use the same post-discrete-event semantics as the fixed-family checkpoint API.
/// A checkpoint coincident with the selected trigger therefore contains the switched state and
/// the first post-trigger command. Neither policy nor schedule errors silently fall back.
pub fn propagate_controlled_to_uncontrolled_with_checkpoints(
    input: &TransitionKernelInput,
    policy: &ControlledToUncontrolledPolicy,
    schedule: &ExactTimeCheckpointSchedule,
) -> Result<CheckpointedControlledToUncontrolledResult, ControlledToUncontrolledCheckpointError> {
    let attempt = attempt_controlled_to_uncontrolled_with_checkpoints(input, policy, schedule)
        .map_err(|error| match error {
            ControlledToUncontrolledAttemptError::Schedule(error) => {
                ControlledToUncontrolledCheckpointError::Schedule(error)
            }
            ControlledToUncontrolledAttemptError::ControlledTransition(error) => {
                ControlledToUncontrolledCheckpointError::ControlledTransition(error)
            }
        })?;
    let control_transition = match attempt.control_transition {
        ControlTransitionOutcome::Reached { event } => Some(*event),
        ControlTransitionOutcome::NotReached { .. } => None,
    };
    let transition =
        controlled_to_uncontrolled_result(input, policy, attempt.transition, control_transition)?;

    if let RequestedCheckpointStatus::Unreached {
        next_requested_elapsed,
        termination,
    } = attempt.checkpoint_status
    {
        return Err(ControlledToUncontrolledCheckpointError::Unreached {
            requested_elapsed: next_requested_elapsed,
            termination,
        });
    }

    Ok(CheckpointedControlledToUncontrolledResult {
        transition,
        checkpoints: attempt.checkpoints,
    })
}

fn propagate_transition_validated(
    input: &TransitionKernelInput,
    schedule: &ExactTimeCheckpointSchedule,
    control_policy: Option<&ControlledToUncontrolledPolicy>,
    atmosphere: &dyn TransitionAtmosphere,
) -> Result<PropagationRun, TransitionError> {
    let mut runtime = RuntimeState {
        continuous: ContinuousState {
            absolute_time_s: input.initial.flight.time.0,
            position: input.initial.flight.position,
            altitude_m: input.initial.flight.altitude.0 / FEET_PER_METRE,
            true_airspeed_m_s: input.initial.flight.true_airspeed.0,
            flight_path_angle_rad: input.initial.flight.flight_path_angle.to_radians(),
            heading_rad: input.initial.flight.heading_true.to_radians(),
        },
        elapsed_s: 0.0,
        fuel: input.initial.fuel,
        engines: input.initial.engines,
        electrical: input.initial.electrical,
        apu: input.initial.apu,
        ocxo: input.initial.ocxo,
        lift_limited: false,
    };
    let sea_surface_m = input.integration.sea_surface_altitude.0 / FEET_PER_METRE;
    let mut events = Vec::new();
    let mut checkpoints = Vec::with_capacity(schedule.requested_elapsed_times.len());
    let mut next_checkpoint_index = 0usize;
    let mut control_transition = None;
    let mut steps = 0usize;

    loop {
        let first_new_event = events.len();
        settle_discrete_events(&mut runtime, input, &mut events)?;
        apply_control_transition_if_triggered(
            &runtime,
            input,
            &events[first_new_event..],
            control_policy,
            &mut control_transition,
            atmosphere,
        )?;
        capture_due_checkpoint(
            &mut runtime,
            input,
            ActiveControlSelection {
                policy: control_policy,
                transition: control_transition.as_ref(),
            },
            &events,
            schedule,
            &mut next_checkpoint_index,
            &mut checkpoints,
            atmosphere,
        )?;

        if runtime.continuous.altitude_m <= sea_surface_m {
            runtime.continuous.altitude_m = sea_surface_m;
            return finished_run(
                &runtime,
                input,
                events,
                TransitionTermination::Impact,
                checkpoints,
                control_transition.clone(),
                atmosphere,
            );
        }
        let pending_checkpoint_before_limit = schedule
            .requested_elapsed_times
            .get(next_checkpoint_index)
            .is_some_and(|requested| {
                requested.0 > runtime.elapsed_s
                    && requested.0 <= input.integration.maximum_duration.0
            });
        if runtime.elapsed_s + EVENT_EPSILON_S >= input.integration.maximum_duration.0
            && !pending_checkpoint_before_limit
        {
            return finished_run(
                &runtime,
                input,
                events,
                TransitionTermination::MaximumDuration,
                checkpoints,
                control_transition.clone(),
                atmosphere,
            );
        }
        if let Some(exit) = envelope_exit(&runtime, input.aerodynamics) {
            return finished_run(
                &runtime,
                input,
                events,
                TransitionTermination::DeclaredEnvelopeExit(exit),
                checkpoints,
                control_transition.clone(),
                atmosphere,
            );
        }
        if steps >= input.integration.maximum_steps {
            return finished_run(
                &runtime,
                input,
                events,
                TransitionTermination::MaximumSteps,
                checkpoints,
                control_transition.clone(),
                atmosphere,
            );
        }

        let remaining = input.integration.maximum_duration.0 - runtime.elapsed_s;
        let mut duration_s = input.integration.time_step.0.min(remaining);
        if let Some(until_event) =
            time_until_next_event(&runtime, input, control_policy, control_transition.as_ref())
        {
            duration_s = duration_s.min(until_event);
        }
        let mut checkpoint_boundary = false;
        if let Some(requested) = schedule.requested_elapsed_times.get(next_checkpoint_index) {
            let until_checkpoint_s = requested.0 - runtime.elapsed_s;
            if until_checkpoint_s > 0.0 && until_checkpoint_s <= duration_s {
                duration_s = until_checkpoint_s;
                checkpoint_boundary = true;
            }
        }
        if duration_s <= EVENT_EPSILON_S && !checkpoint_boundary {
            return Err(TransitionError::InvalidInput(
                "integration could not advance beyond a discrete-event boundary",
            ));
        }

        let before = runtime.clone();
        let command = selected_control_command(
            input,
            control_policy,
            control_transition.as_ref(),
            runtime.elapsed_s,
        );
        let mass_kg = total_mass_kg(input.initial.mass, runtime.fuel);
        let total_burn_kg_s = runtime.engines.left.active_fuel_flow()
            + runtime.engines.right.active_fuel_flow()
            + if runtime.apu.mode == ApuMode::Running {
                runtime.apu.fuel_flow.0
            } else {
                0.0
            };
        let midpoint_mass_kg = mass_kg - 0.5 * total_burn_kg_s * duration_s;
        let (next_continuous, middle) = midpoint_step(
            &runtime.continuous,
            duration_s,
            StepMass {
                start_kg: mass_kg,
                midpoint_kg: midpoint_mass_kg,
            },
            active_thrust_newtons(runtime.engines),
            command,
            input.aerodynamics,
            atmosphere,
        )?;

        let limited = (middle.requested_cl - middle.applied_cl).abs() > 1.0e-12;
        if limited && !runtime.lift_limited {
            events.push(event_at(
                &runtime,
                TransitionEventKind::LiftCoefficientLimited {
                    requested: middle.requested_cl,
                    applied: middle.applied_cl,
                },
            ));
        }

        let mut candidate = runtime.clone();
        candidate.continuous = next_continuous;
        candidate.lift_limited = limited;
        advance_system_state(&mut candidate, duration_s);

        if before.continuous.altitude_m > sea_surface_m
            && candidate.continuous.altitude_m <= sea_surface_m
        {
            let fraction = ((before.continuous.altitude_m - sea_surface_m)
                / (before.continuous.altitude_m - candidate.continuous.altitude_m))
                .clamp(0.0, 1.0);
            let impact_duration_s = duration_s * fraction;
            runtime = before;
            runtime.continuous = ContinuousState {
                absolute_time_s: runtime.continuous.absolute_time_s + impact_duration_s,
                position: advance_position(
                    runtime.continuous.position,
                    middle.ground_north_m_s,
                    middle.ground_east_m_s,
                    impact_duration_s,
                )?,
                altitude_m: sea_surface_m,
                true_airspeed_m_s: runtime.continuous.true_airspeed_m_s
                    + fraction
                        * (candidate.continuous.true_airspeed_m_s
                            - runtime.continuous.true_airspeed_m_s),
                flight_path_angle_rad: runtime.continuous.flight_path_angle_rad
                    + fraction
                        * (candidate.continuous.flight_path_angle_rad
                            - runtime.continuous.flight_path_angle_rad),
                heading_rad: runtime.continuous.heading_rad
                    + fraction
                        * (candidate.continuous.heading_rad - runtime.continuous.heading_rad),
            };
            runtime.lift_limited = limited;
            advance_system_state(&mut runtime, impact_duration_s);
            capture_due_checkpoint(
                &mut runtime,
                input,
                ActiveControlSelection {
                    policy: control_policy,
                    transition: control_transition.as_ref(),
                },
                &events,
                schedule,
                &mut next_checkpoint_index,
                &mut checkpoints,
                atmosphere,
            )?;
            return finished_run(
                &runtime,
                input,
                events,
                TransitionTermination::Impact,
                checkpoints,
                control_transition.clone(),
                atmosphere,
            );
        }

        runtime = candidate;
        steps += 1;
    }
}
#[cfg(test)]
mod kernel_tests {
    use std::cell::Cell;

    use super::*;

    struct TimeVaryingTestAtmosphere {
        calls: Cell<usize>,
    }

    impl TransitionAtmosphere for TimeVaryingTestAtmosphere {
        fn sample(
            &self,
            time: Seconds,
            _position: LatLon,
            _pressure_altitude: Feet,
        ) -> Result<TransitionAtmosphereSample, TransitionAtmosphereError> {
            self.calls.set(self.calls.get() + 1);
            Ok(TransitionAtmosphereSample {
                density: KilogramsPerCubicMetre(1.0),
                wind_north: MetresPerSecond(0.0),
                wind_east: MetresPerSecond((time.0 - 100.0).max(0.0)),
            })
        }
    }

    fn running_engine(thrust_newtons: f64) -> EngineState {
        EngineState {
            mode: EngineMode::Running,
            thrust: Newtons(thrust_newtons),
            fuel_flow: KilogramsPerSecond(0.0),
            generator_online: true,
        }
    }

    fn stopped_engine() -> EngineState {
        EngineState {
            mode: EngineMode::Windmilling,
            thrust: Newtons(0.0),
            fuel_flow: KilogramsPerSecond(0.0),
            generator_online: false,
        }
    }

    fn synthetic_level_input() -> TransitionKernelInput {
        let mass_kg = 10_000.0 + 100.0 + 100.0 + 10.0;
        let density_kg_m3 = 1.225;
        let true_airspeed_m_s: f64 = 100.0;
        let area_m2 = 100.0;
        let dynamic_pressure_area = 0.5 * density_kg_m3 * true_airspeed_m_s.powi(2) * area_m2;
        let lift_coefficient = mass_kg * STANDARD_GRAVITY_M_S2 / dynamic_pressure_area;
        let total_drag_newtons = dynamic_pressure_area * 0.02;

        TransitionKernelInput {
            initial: TransitionInitialCondition {
                flight: PointMassState {
                    time: Seconds(0.0),
                    position: LatLon::new_unchecked(-35.0, 90.0),
                    altitude: Feet(1_000.0 * FEET_PER_METRE),
                    true_airspeed: MetresPerSecond(true_airspeed_m_s),
                    flight_path_angle: Degrees(0.0),
                    heading_true: Degrees(90.0),
                },
                mass: MassState {
                    non_fuel_mass: Kilograms(10_000.0),
                },
                fuel: FuelState {
                    left_engine_feed: Kilograms(100.0),
                    right_engine_feed: Kilograms(100.0),
                    apu_feed: Kilograms(10.0),
                    unusable: Kilograms(0.0),
                },
                engines: EngineSystemState {
                    left: running_engine(total_drag_newtons / 2.0),
                    right: running_engine(total_drag_newtons / 2.0),
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
                    restart_count: 0,
                },
            },
            family: ConditionalModelFamily {
                control: ControlFamily::Uncontrolled,
                restart_transient: RestartTransientFamily::NoAdditionalTransient,
            },
            model_weight: ModelWeight(0.25),
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
                reference_area: SquareMetres(area_m2),
                zero_lift_drag_coefficient: 0.02,
                induced_drag_factor: 0.0,
                minimum_lift_coefficient: -1.0,
                maximum_lift_coefficient: 2.0,
                maximum_bank_angle: Degrees(60.0),
                minimum_true_airspeed: MetresPerSecond(40.0),
                maximum_true_airspeed: MetresPerSecond(400.0),
            },
            atmosphere: AtmosphereProfile {
                nodes: vec![AtmosphereNode {
                    altitude: Feet(0.0),
                    density: KilogramsPerCubicMetre(density_kg_m3),
                    wind_north: MetresPerSecond(0.0),
                    wind_east: MetresPerSecond(0.0),
                }],
            },
            apu_start_policy: ApuStartPolicy::Disabled,
            integration: IntegrationSettings {
                time_step: Seconds(0.25),
                maximum_duration: Seconds(10.0),
                sea_surface_altitude: Feet(0.0),
                maximum_steps: 1_000,
            },
        }
    }

    fn synthetic_event_input() -> TransitionKernelInput {
        let mut input = synthetic_level_input();
        input.initial.fuel.left_engine_feed = Kilograms(2.0);
        input.initial.fuel.right_engine_feed = Kilograms(4.0);
        input.initial.fuel.apu_feed = Kilograms(1.0);
        input.initial.engines.left.fuel_flow = KilogramsPerSecond(1.0);
        input.initial.engines.right.fuel_flow = KilogramsPerSecond(1.0);
        input.apu_start_policy = ApuStartPolicy::OnDualEngineGeneratorLoss {
            start_delay: Seconds(1.0),
            start_fuel: Kilograms(0.5),
            generator_delay: Seconds(2.0),
            running_fuel_flow: KilogramsPerSecond(0.0),
        };
        input.family.restart_transient = RestartTransientFamily::UnspecifiedRestartTransient;
        input.integration.time_step = Seconds(0.7);
        input.integration.maximum_duration = Seconds(8.0);
        input
    }

    fn synthetic_control_transition_input(time_step_s: f64) -> TransitionKernelInput {
        let mut input = synthetic_event_input();
        input.family.control = ControlFamily::Controlled;
        input.control = ControlSchedule {
            segments: vec![ControlSegment {
                start_offset: Seconds(0.0),
                command: ControlCommand::Controlled {
                    lift_load_factor: 1.0,
                    bank_angle: Degrees(0.0),
                },
            }],
        };
        input.integration.time_step = Seconds(time_step_s);
        input
    }

    fn synthetic_control_transition_policy(
        input: &TransitionKernelInput,
        trigger: ControlTransitionTrigger,
    ) -> ControlledToUncontrolledPolicy {
        ControlledToUncontrolledPolicy {
            scenario: ControlledToUncontrolledScenario {
                label: "synthetic conditional control transition".to_owned(),
                trigger,
            },
            pre_trigger_controlled: input.control.clone(),
            post_trigger_uncontrolled: ControlSchedule {
                segments: vec![
                    ControlSegment {
                        start_offset: Seconds(0.0),
                        command: ControlCommand::Uncontrolled {
                            lift_coefficient: 0.0,
                            bank_angle: Degrees(0.0),
                        },
                    },
                    ControlSegment {
                        start_offset: Seconds(1.25),
                        command: ControlCommand::Uncontrolled {
                            lift_coefficient: 0.1,
                            bank_angle: Degrees(0.0),
                        },
                    },
                ],
            },
        }
    }

    fn event_time(
        transition: &WeightedTransition,
        predicate: impl Fn(&TransitionEventKind) -> bool,
    ) -> f64 {
        transition
            .events
            .iter()
            .find(|event| predicate(&event.kind))
            .expect("expected event")
            .time
            .0
    }

    #[test]
    fn straight_level_force_equilibrium_is_a_limiting_case() {
        let input = synthetic_level_input();
        let output = propagate_transition(&input).unwrap();

        assert_eq!(output.termination, TransitionTermination::MaximumDuration);
        assert_eq!(output.model_weight, input.model_weight);
        assert_eq!(output.family.control, ControlFamily::Uncontrolled);
        assert!(
            (output.terminal.kinematics.point_mass.altitude.0 - input.initial.flight.altitude.0)
                .abs()
                < 1.0e-8
        );
        assert!(
            (output.terminal.kinematics.point_mass.true_airspeed.0
                - input.initial.flight.true_airspeed.0)
                .abs()
                < 1.0e-10
        );
        assert!(
            output
                .terminal
                .kinematics
                .point_mass
                .flight_path_angle
                .0
                .abs()
                < 1.0e-10
        );

        let mut controlled = input.clone();
        controlled.family.control = ControlFamily::Controlled;
        controlled.control.segments[0].command = ControlCommand::Controlled {
            lift_load_factor: 1.0,
            bank_angle: Degrees(0.0),
        };
        let controlled_output = propagate_transition(&controlled).unwrap();
        assert_eq!(controlled_output.family.control, ControlFamily::Controlled);
        assert_eq!(
            controlled_output.termination,
            TransitionTermination::MaximumDuration
        );
        assert!(
            (controlled_output.terminal.kinematics.point_mass.altitude.0
                - controlled.initial.flight.altitude.0)
                .abs()
                < 1.0e-8
        );
    }

    #[test]
    fn drag_free_ballistic_impact_conserves_mechanical_energy() {
        let mut input = synthetic_level_input();
        input.initial.flight.altitude = Feet(1_000.0 * FEET_PER_METRE);
        input.initial.flight.true_airspeed = MetresPerSecond(200.0);
        input.initial.flight.flight_path_angle = Degrees(-10.0);
        input.initial.mass.non_fuel_mass = Kilograms(10_000.0);
        input.initial.fuel = FuelState {
            left_engine_feed: Kilograms(0.0),
            right_engine_feed: Kilograms(0.0),
            apu_feed: Kilograms(0.0),
            unusable: Kilograms(0.0),
        };
        input.initial.engines = EngineSystemState {
            left: stopped_engine(),
            right: stopped_engine(),
        };
        input.initial.electrical = ElectricalSystemState {
            source: ElectricalSource::Unpowered,
            satcom_powered: false,
            dual_engine_generator_loss_elapsed: Some(Seconds(0.0)),
        };
        input.initial.apu = ApuState {
            mode: ApuMode::Unavailable,
            elapsed_in_mode: Seconds(0.0),
            generator_online: false,
            fuel_flow: KilogramsPerSecond(0.0),
        };
        input.initial.ocxo = OcxoState {
            power: OcxoPowerState::Unpowered,
            unpowered_duration: Seconds(0.0),
            restart_count: 0,
        };
        input.control.segments[0].command = ControlCommand::Uncontrolled {
            lift_coefficient: 0.0,
            bank_angle: Degrees(0.0),
        };
        input.aerodynamics.zero_lift_drag_coefficient = 0.0;
        input.aerodynamics.induced_drag_factor = 0.0;
        input.aerodynamics.minimum_true_airspeed = MetresPerSecond(10.0);
        input.aerodynamics.maximum_true_airspeed = MetresPerSecond(500.0);
        input.atmosphere.nodes[0].density = KilogramsPerCubicMetre(0.0);
        input.integration.time_step = Seconds(0.01);
        input.integration.maximum_duration = Seconds(30.0);
        input.integration.maximum_steps = 10_000;

        let initial_energy =
            0.5 * 10_000.0 * 200.0_f64.powi(2) + 10_000.0 * STANDARD_GRAVITY_M_S2 * 1_000.0;
        let output = propagate_transition(&input).unwrap();
        let impact = output.impact.expect("ballistic trajectory should impact");
        let relative_error = (impact.kinetic_energy.0 - initial_energy).abs() / initial_energy;

        assert_eq!(output.termination, TransitionTermination::Impact);
        assert!(impact.vertical_speed.0 < 0.0);
        assert!(impact.impact_angle.0 > 0.0);
        assert!(relative_error < 2.0e-4, "relative error {relative_error}");
    }

    #[test]
    fn event_boundaries_reproduce_analytic_flameout_and_restart_times() {
        let input = synthetic_event_input();

        let first = propagate_transition(&input).unwrap();
        let second = propagate_transition(&input).unwrap();

        assert_eq!(first, second);
        assert_eq!(first.model_weight, ModelWeight(0.25));
        assert!(
            (event_time(&first, |event| matches!(
                event,
                TransitionEventKind::EngineFlameout {
                    engine: EngineSide::Left
                }
            )) - 2.0)
                .abs()
                < 1.0e-10
        );
        assert!(
            (event_time(&first, |event| matches!(
                event,
                TransitionEventKind::EngineFlameout {
                    engine: EngineSide::Right
                }
            )) - 4.0)
                .abs()
                < 1.0e-10
        );
        assert!(
            (event_time(&first, |event| matches!(
                event,
                TransitionEventKind::DualEngineGeneratorLoss
            )) - 4.0)
                .abs()
                < 1.0e-10
        );
        assert!(
            (event_time(&first, |event| matches!(
                event,
                TransitionEventKind::ApuStart
            )) - 5.0)
                .abs()
                < 1.0e-10
        );
        assert!(
            (event_time(&first, |event| matches!(
                event,
                TransitionEventKind::ApuGeneratorOnline
            )) - 7.0)
                .abs()
                < 1.0e-10
        );
        assert!(
            (event_time(&first, |event| matches!(
                event,
                TransitionEventKind::SatcomPowerLost
            )) - 4.0)
                .abs()
                < 1.0e-10
        );
        assert!(
            (event_time(&first, |event| matches!(
                event,
                TransitionEventKind::SatcomPowerRestored
            )) - 7.0)
                .abs()
                < 1.0e-10
        );
        let restart = first
            .events
            .iter()
            .find_map(|event| match event.kind {
                TransitionEventKind::OcxoRestart {
                    family,
                    outage_duration,
                } => Some((event.time.0, family, outage_duration.0)),
                _ => None,
            })
            .expect("OCXO restart event");
        assert_eq!(
            restart.1,
            RestartTransientFamily::UnspecifiedRestartTransient
        );
        assert!((restart.0 - 7.0).abs() < 1.0e-10);
        assert!((restart.2 - 3.0).abs() < 1.0e-10);
    }

    #[test]
    fn checkpoint_off_the_base_step_returns_complete_exact_time_state() {
        let input = synthetic_level_input();
        let schedule = ExactTimeCheckpointSchedule {
            requested_elapsed_times: vec![Seconds(0.37)],
        };
        let output = propagate_transition_with_checkpoints(&input, &schedule).unwrap();

        assert_eq!(output.checkpoints.len(), 1);
        let checkpoint = &output.checkpoints[0];
        assert_eq!(checkpoint.requested_elapsed, Seconds(0.37));
        assert_eq!(
            checkpoint.state.kinematics.point_mass.time,
            Seconds(input.initial.flight.time.0 + 0.37)
        );
        assert!(
            (checkpoint.state.kinematics.point_mass.altitude.0 - input.initial.flight.altitude.0)
                .abs()
                < 1.0e-8
        );
        assert!(
            (checkpoint.state.kinematics.point_mass.true_airspeed.0
                - input.initial.flight.true_airspeed.0)
                .abs()
                < 1.0e-10
        );
        assert_eq!(checkpoint.state.fuel, input.initial.fuel);
        assert_eq!(checkpoint.state.engines, input.initial.engines);
        assert_eq!(checkpoint.state.electrical, input.initial.electrical);
        assert_eq!(checkpoint.state.apu, input.initial.apu);
        assert_eq!(checkpoint.state.ocxo, input.initial.ocxo);
        assert_eq!(checkpoint.active_control, input.control.segments[0].command);
        assert!(checkpoint.events_at_time.is_empty());
    }

    #[test]
    fn checkpoints_coincident_with_flameout_power_and_apu_events_are_post_event() {
        let input = synthetic_event_input();
        let schedule = ExactTimeCheckpointSchedule {
            requested_elapsed_times: vec![Seconds(2.0), Seconds(4.0), Seconds(5.0), Seconds(7.0)],
        };
        let output = propagate_transition_with_checkpoints(&input, &schedule).unwrap();
        let left_flameout = &output.checkpoints[0];
        let power_loss = &output.checkpoints[1];
        let apu_start = &output.checkpoints[2];
        let power_restore = &output.checkpoints[3];

        assert_eq!(
            left_flameout.state.engines.left.mode,
            EngineMode::Windmilling
        );
        assert_eq!(left_flameout.state.engines.right.mode, EngineMode::Running);
        assert_eq!(
            left_flameout.state.electrical.source,
            ElectricalSource::EngineGenerators
        );
        assert!(left_flameout.events_at_time.iter().any(|event| matches!(
            event,
            TransitionEventKind::EngineFlameout {
                engine: EngineSide::Left
            }
        )));

        assert_eq!(power_loss.state.engines.right.mode, EngineMode::Windmilling);
        assert_eq!(
            power_loss.state.electrical.source,
            ElectricalSource::Unpowered
        );
        assert!(!power_loss.state.electrical.satcom_powered);
        assert_eq!(power_loss.state.ocxo.power, OcxoPowerState::Unpowered);
        assert_eq!(power_loss.state.ocxo.unpowered_duration, Seconds(0.0));
        assert!(power_loss.events_at_time.iter().any(|event| matches!(
            event,
            TransitionEventKind::EngineFlameout {
                engine: EngineSide::Right
            }
        )));
        assert!(power_loss
            .events_at_time
            .iter()
            .any(|event| matches!(event, TransitionEventKind::DualEngineGeneratorLoss)));
        assert!(power_loss
            .events_at_time
            .iter()
            .any(|event| matches!(event, TransitionEventKind::SatcomPowerLost)));

        assert_eq!(apu_start.state.apu.mode, ApuMode::Starting);
        assert_eq!(
            apu_start.state.electrical.source,
            ElectricalSource::Unpowered
        );
        assert!((apu_start.state.ocxo.unpowered_duration.0 - 1.0).abs() < 1.0e-10);
        assert!(apu_start
            .events_at_time
            .iter()
            .any(|event| matches!(event, TransitionEventKind::ApuStart)));

        assert_eq!(power_restore.state.apu.mode, ApuMode::Running);
        assert!(power_restore.state.apu.generator_online);
        assert_eq!(
            power_restore.state.electrical.source,
            ElectricalSource::ApuGenerator
        );
        assert!(power_restore.state.electrical.satcom_powered);
        assert_eq!(power_restore.state.ocxo.power, OcxoPowerState::Powered);
        assert_eq!(power_restore.state.ocxo.restart_count, 1);
        assert!(power_restore
            .events_at_time
            .iter()
            .any(|event| matches!(event, TransitionEventKind::ApuGeneratorOnline)));
        assert!(power_restore
            .events_at_time
            .iter()
            .any(|event| matches!(event, TransitionEventKind::SatcomPowerRestored)));
        let restart_outage = power_restore
            .events_at_time
            .iter()
            .find_map(|event| match event {
                TransitionEventKind::OcxoRestart {
                    outage_duration, ..
                } => Some(outage_duration.0),
                _ => None,
            })
            .expect("restart event at checkpoint");
        assert!((restart_outage - 3.0).abs() < 1.0e-10);
    }

    #[test]
    fn checkpointed_runs_are_repeatable_and_empty_schedule_preserves_transition() {
        let input = synthetic_level_input();
        let schedule = ExactTimeCheckpointSchedule {
            requested_elapsed_times: vec![Seconds(0.0), Seconds(0.37), Seconds(10.0)],
        };

        let first = propagate_transition_with_checkpoints(&input, &schedule).unwrap();
        let second = propagate_transition_with_checkpoints(&input, &schedule).unwrap();
        assert_eq!(first, second);
        assert_eq!(first.checkpoints.len(), 3);
        assert_eq!(
            first.checkpoints[2].state.kinematics.point_mass.time,
            Seconds(10.0)
        );

        let plain = propagate_transition(&input).unwrap();
        let empty =
            propagate_transition_with_checkpoints(&input, &ExactTimeCheckpointSchedule::default())
                .unwrap();
        assert_eq!(empty.transition, plain);
        assert!(empty.checkpoints.is_empty());
    }

    #[test]
    fn invalid_checkpoint_schedules_are_rejected_strictly() {
        let maximum = Seconds(10.0);

        assert!(matches!(
            (ExactTimeCheckpointSchedule {
                requested_elapsed_times: vec![Seconds(f64::NAN)]
            })
            .validate(maximum),
            Err(ExactTimeCheckpointScheduleError::NonFinite { index: 0 })
        ));
        assert!(matches!(
            (ExactTimeCheckpointSchedule {
                requested_elapsed_times: vec![Seconds(-0.1)]
            })
            .validate(maximum),
            Err(ExactTimeCheckpointScheduleError::Negative { index: 0, .. })
        ));
        assert!(matches!(
            (ExactTimeCheckpointSchedule {
                requested_elapsed_times: vec![Seconds(10.1)]
            })
            .validate(maximum),
            Err(ExactTimeCheckpointScheduleError::BeyondMaximumDuration { index: 0, .. })
        ));
        assert!(matches!(
            (ExactTimeCheckpointSchedule {
                requested_elapsed_times: vec![Seconds(1.0), Seconds(1.0)]
            })
            .validate(maximum),
            Err(ExactTimeCheckpointScheduleError::NotStrictlyIncreasing { index: 1, .. })
        ));
        let unsorted = ExactTimeCheckpointSchedule {
            requested_elapsed_times: vec![Seconds(2.0), Seconds(1.0)],
        };
        assert!(matches!(
            propagate_transition_with_checkpoints(&synthetic_level_input(), &unsorted),
            Err(ExactTimeCheckpointError::Schedule(
                ExactTimeCheckpointScheduleError::NotStrictlyIncreasing { index: 1, .. }
            ))
        ));
        assert!(matches!(
            (ExactTimeCheckpointSchedule {
                requested_elapsed_times: vec![Seconds(1.0), Seconds(1.0 + 0.5 * EVENT_EPSILON_S)]
            })
            .validate(maximum),
            Err(ExactTimeCheckpointScheduleError::BelowMinimumSeparation { index: 1, .. })
        ));
    }

    #[test]
    fn checkpoint_after_early_termination_is_reported_as_unreached() {
        let mut input = synthetic_level_input();
        input.integration.maximum_steps = 1;
        let schedule = ExactTimeCheckpointSchedule {
            requested_elapsed_times: vec![Seconds(1.0)],
        };

        assert!(matches!(
            propagate_transition_with_checkpoints(&input, &schedule),
            Err(ExactTimeCheckpointError::Unreached {
                requested_elapsed: Seconds(1.0),
                termination: TransitionTermination::MaximumSteps,
            })
        ));
    }

    #[test]
    fn checkpointed_mixed_r600_style_sample_before_trigger_is_exact_and_controlled() {
        let input = synthetic_control_transition_input(0.7);
        let policy = synthetic_control_transition_policy(
            &input,
            ControlTransitionTrigger::DualEngineGeneratorLoss,
        );
        let schedule = ExactTimeCheckpointSchedule {
            requested_elapsed_times: vec![Seconds(3.37)],
        };

        let output =
            propagate_controlled_to_uncontrolled_with_checkpoints(&input, &policy, &schedule)
                .unwrap();
        let checkpoint = &output.checkpoints[0];

        assert_eq!(output.transition.control_transition.elapsed, Seconds(4.0));
        assert_eq!(checkpoint.requested_elapsed, Seconds(3.37));
        assert_eq!(
            checkpoint.state.kinematics.point_mass.time,
            Seconds(input.initial.flight.time.0 + 3.37)
        );
        assert_eq!(
            checkpoint.active_control,
            policy.pre_trigger_controlled.segments[0].command
        );
        assert_eq!(checkpoint.state.engines.left.mode, EngineMode::Windmilling);
        assert_eq!(checkpoint.state.engines.right.mode, EngineMode::Running);
        assert_eq!(
            checkpoint.state.electrical.source,
            ElectricalSource::EngineGenerators
        );
        assert!(checkpoint.events_at_time.is_empty());
    }

    #[test]
    fn checkpointed_mixed_trigger_checkpoint_contains_post_event_switched_state() {
        let input = synthetic_control_transition_input(0.7);
        let policy = synthetic_control_transition_policy(
            &input,
            ControlTransitionTrigger::DualEngineGeneratorLoss,
        );
        let schedule = ExactTimeCheckpointSchedule {
            requested_elapsed_times: vec![Seconds(4.0)],
        };

        let output =
            propagate_controlled_to_uncontrolled_with_checkpoints(&input, &policy, &schedule)
                .unwrap();
        let checkpoint = &output.checkpoints[0];
        let transition = &output.transition.control_transition;

        assert_eq!(checkpoint.state, transition.state);
        assert_eq!(transition.elapsed, Seconds(4.0));
        assert_eq!(transition.to, ControlFamily::Uncontrolled);
        assert_eq!(
            checkpoint.active_control,
            policy.post_trigger_uncontrolled.segments[0].command
        );
        assert!(checkpoint.events_at_time.iter().any(|event| matches!(
            event,
            TransitionEventKind::EngineFlameout {
                engine: EngineSide::Right
            }
        )));
        assert!(checkpoint
            .events_at_time
            .iter()
            .any(|event| matches!(event, TransitionEventKind::DualEngineGeneratorLoss)));
        assert!(checkpoint
            .events_at_time
            .iter()
            .any(|event| matches!(event, TransitionEventKind::SatcomPowerLost)));
    }

    #[test]
    fn checkpointed_mixed_post_trigger_checkpoint_uses_relative_schedule() {
        let input = synthetic_control_transition_input(0.7);
        let policy = synthetic_control_transition_policy(
            &input,
            ControlTransitionTrigger::DualEngineGeneratorLoss,
        );
        let schedule = ExactTimeCheckpointSchedule {
            requested_elapsed_times: vec![Seconds(5.5)],
        };

        let output =
            propagate_controlled_to_uncontrolled_with_checkpoints(&input, &policy, &schedule)
                .unwrap();
        let checkpoint = &output.checkpoints[0];

        assert_eq!(
            checkpoint.requested_elapsed.0 - output.transition.control_transition.elapsed.0,
            1.5
        );
        assert_eq!(
            checkpoint.active_control,
            policy.post_trigger_uncontrolled.segments[1].command
        );
        assert_eq!(checkpoint.state.apu.mode, ApuMode::Starting);
        assert!((checkpoint.state.apu.elapsed_in_mode.0 - 0.5).abs() < 1.0e-10);
        assert_eq!(
            checkpoint.state.electrical.source,
            ElectricalSource::Unpowered
        );
        assert!((checkpoint.state.ocxo.unpowered_duration.0 - 1.5).abs() < 1.0e-10);
    }

    #[test]
    fn checkpointed_mixed_runs_are_repeatable_and_base_step_event_invariant() {
        let coarse_input = synthetic_control_transition_input(0.7);
        let coarse_policy = synthetic_control_transition_policy(
            &coarse_input,
            ControlTransitionTrigger::DualEngineGeneratorLoss,
        );
        let schedule = ExactTimeCheckpointSchedule {
            requested_elapsed_times: vec![Seconds(3.37), Seconds(4.0), Seconds(5.5)],
        };

        let coarse_first = propagate_controlled_to_uncontrolled_with_checkpoints(
            &coarse_input,
            &coarse_policy,
            &schedule,
        )
        .unwrap();
        let coarse_second = propagate_controlled_to_uncontrolled_with_checkpoints(
            &coarse_input,
            &coarse_policy,
            &schedule,
        )
        .unwrap();
        assert_eq!(coarse_first, coarse_second);

        let fine_input = synthetic_control_transition_input(0.31);
        let fine_policy = synthetic_control_transition_policy(
            &fine_input,
            ControlTransitionTrigger::DualEngineGeneratorLoss,
        );
        let fine = propagate_controlled_to_uncontrolled_with_checkpoints(
            &fine_input,
            &fine_policy,
            &schedule,
        )
        .unwrap();

        for (coarse, fine) in coarse_first.checkpoints.iter().zip(&fine.checkpoints) {
            assert_eq!(coarse.requested_elapsed, fine.requested_elapsed);
            assert_eq!(
                coarse.state.kinematics.point_mass.time,
                fine.state.kinematics.point_mass.time
            );
            assert_eq!(coarse.active_control, fine.active_control);
            assert_eq!(coarse.state.engines, fine.state.engines);
            assert_eq!(coarse.state.electrical.source, fine.state.electrical.source);
            assert_eq!(
                coarse.state.electrical.satcom_powered,
                fine.state.electrical.satcom_powered
            );
            match (
                coarse.state.electrical.dual_engine_generator_loss_elapsed,
                fine.state.electrical.dual_engine_generator_loss_elapsed,
            ) {
                (Some(coarse_elapsed), Some(fine_elapsed)) => {
                    assert!((coarse_elapsed.0 - fine_elapsed.0).abs() < 1.0e-10);
                }
                (None, None) => {}
                _ => panic!("base step changed generator-loss timer presence"),
            }
            assert_eq!(coarse.state.apu.mode, fine.state.apu.mode);
            assert_eq!(
                coarse.state.apu.generator_online,
                fine.state.apu.generator_online
            );
            assert_eq!(coarse.state.apu.fuel_flow, fine.state.apu.fuel_flow);
            assert!(
                (coarse.state.apu.elapsed_in_mode.0 - fine.state.apu.elapsed_in_mode.0).abs()
                    < 1.0e-10
            );
            assert_eq!(coarse.state.ocxo.power, fine.state.ocxo.power);
            assert_eq!(
                coarse.state.ocxo.restart_count,
                fine.state.ocxo.restart_count
            );
            assert!(
                (coarse.state.ocxo.unpowered_duration.0 - fine.state.ocxo.unpowered_duration.0)
                    .abs()
                    < 1.0e-10
            );
            assert_eq!(coarse.events_at_time, fine.events_at_time);
        }
    }

    #[test]
    fn checkpointed_mixed_empty_schedule_matches_legacy_api() {
        let input = synthetic_control_transition_input(0.7);
        let policy = synthetic_control_transition_policy(
            &input,
            ControlTransitionTrigger::DualEngineFlameout,
        );

        let legacy = propagate_controlled_to_uncontrolled(&input, &policy).unwrap();
        let checkpointed = propagate_controlled_to_uncontrolled_with_checkpoints(
            &input,
            &policy,
            &ExactTimeCheckpointSchedule::default(),
        )
        .unwrap();

        assert_eq!(checkpointed.transition, legacy);
        assert!(checkpointed.checkpoints.is_empty());
    }

    #[test]
    fn checkpointed_mixed_wrapper_preserves_typed_validation_and_unreached_errors() {
        let input = synthetic_control_transition_input(0.7);
        let policy = synthetic_control_transition_policy(
            &input,
            ControlTransitionTrigger::DualEngineGeneratorLoss,
        );
        let unsorted = ExactTimeCheckpointSchedule {
            requested_elapsed_times: vec![Seconds(5.0), Seconds(4.0)],
        };
        assert!(matches!(
            propagate_controlled_to_uncontrolled_with_checkpoints(&input, &policy, &unsorted),
            Err(ControlledToUncontrolledCheckpointError::Schedule(
                ExactTimeCheckpointScheduleError::NotStrictlyIncreasing { index: 1, .. }
            ))
        ));

        let mut mismatched = policy.clone();
        mismatched.pre_trigger_controlled.segments[0].command = ControlCommand::Controlled {
            lift_load_factor: 0.9,
            bank_angle: Degrees(0.0),
        };
        assert!(matches!(
            propagate_controlled_to_uncontrolled_with_checkpoints(
                &input,
                &mismatched,
                &ExactTimeCheckpointSchedule::default(),
            ),
            Err(
                ControlledToUncontrolledCheckpointError::ControlledTransition(
                    ControlledToUncontrolledError::PreTriggerScheduleMismatch
                )
            )
        ));

        let mut early_input = input;
        early_input.integration.maximum_steps = 6;
        let early_policy = synthetic_control_transition_policy(
            &early_input,
            ControlTransitionTrigger::DualEngineGeneratorLoss,
        );
        let unreached = ExactTimeCheckpointSchedule {
            requested_elapsed_times: vec![Seconds(5.0)],
        };
        assert!(matches!(
            propagate_controlled_to_uncontrolled_with_checkpoints(
                &early_input,
                &early_policy,
                &unreached,
            ),
            Err(ControlledToUncontrolledCheckpointError::Unreached {
                requested_elapsed: Seconds(5.0),
                termination: TransitionTermination::MaximumSteps,
            })
        ));
    }

    #[test]
    fn attempt_preserves_pre_checkpoint_impact_and_nonreach_outcomes() {
        let mut input = synthetic_control_transition_input(0.7);
        input.initial.flight.altitude = Feet(1.0);
        input.initial.flight.flight_path_angle = Degrees(-45.0);
        let policy = synthetic_control_transition_policy(
            &input,
            ControlTransitionTrigger::DualEngineGeneratorLoss,
        );
        let schedule = ExactTimeCheckpointSchedule {
            requested_elapsed_times: vec![Seconds(1.0)],
        };

        let output =
            attempt_controlled_to_uncontrolled_with_checkpoints(&input, &policy, &schedule)
                .unwrap();

        assert_eq!(output.transition.termination, TransitionTermination::Impact);
        assert!(output.transition.impact.is_some());
        assert!(output.checkpoints.is_empty());
        assert!(matches!(
            output.checkpoint_status,
            RequestedCheckpointStatus::Unreached {
                next_requested_elapsed: Seconds(1.0),
                termination: TransitionTermination::Impact,
            }
        ));
        assert!(matches!(
            output.control_transition,
            ControlTransitionOutcome::NotReached {
                trigger: ControlTransitionTrigger::DualEngineGeneratorLoss,
                termination: TransitionTermination::Impact,
            }
        ));
    }

    #[test]
    fn attempt_returns_terminal_state_when_trigger_is_never_reached() {
        let mut input = synthetic_control_transition_input(0.7);
        input.initial.fuel.left_engine_feed = Kilograms(100.0);
        input.initial.fuel.right_engine_feed = Kilograms(100.0);
        input.integration.maximum_duration = Seconds(2.0);
        let policy = synthetic_control_transition_policy(
            &input,
            ControlTransitionTrigger::DualEngineGeneratorLoss,
        );
        let schedule = ExactTimeCheckpointSchedule {
            requested_elapsed_times: vec![Seconds(1.0)],
        };

        let output =
            attempt_controlled_to_uncontrolled_with_checkpoints(&input, &policy, &schedule)
                .unwrap();

        assert_eq!(
            output.transition.termination,
            TransitionTermination::MaximumDuration
        );
        assert_eq!(output.checkpoints.len(), 1);
        assert_eq!(
            output.checkpoint_status,
            RequestedCheckpointStatus::AllReached
        );
        assert!(matches!(
            output.control_transition,
            ControlTransitionOutcome::NotReached {
                trigger: ControlTransitionTrigger::DualEngineGeneratorLoss,
                termination: TransitionTermination::MaximumDuration,
            }
        ));
    }

    #[test]
    fn successful_attempt_exactly_matches_existing_checkpoint_wrapper() {
        let input = synthetic_control_transition_input(0.7);
        let policy = synthetic_control_transition_policy(
            &input,
            ControlTransitionTrigger::DualEngineGeneratorLoss,
        );
        let schedule = ExactTimeCheckpointSchedule {
            requested_elapsed_times: vec![Seconds(3.37), Seconds(4.0), Seconds(5.5)],
        };

        let attempt =
            attempt_controlled_to_uncontrolled_with_checkpoints(&input, &policy, &schedule)
                .unwrap();
        let existing =
            propagate_controlled_to_uncontrolled_with_checkpoints(&input, &policy, &schedule)
                .unwrap();
        let event = match &attempt.control_transition {
            ControlTransitionOutcome::Reached { event } => event.as_ref(),
            ControlTransitionOutcome::NotReached { .. } => panic!("expected transition"),
        };

        assert_eq!(
            attempt.checkpoint_status,
            RequestedCheckpointStatus::AllReached
        );
        assert_eq!(attempt.checkpoints, existing.checkpoints);
        assert_eq!(event, &existing.transition.control_transition);
        assert_eq!(
            attempt.transition.model_weight,
            existing.transition.model_weight
        );
        assert_eq!(attempt.transition.terminal, existing.transition.terminal);
        assert_eq!(attempt.transition.events, existing.transition.events);
        assert_eq!(
            attempt.transition.termination,
            existing.transition.termination
        );
        assert_eq!(attempt.transition.impact, existing.transition.impact);
        assert_eq!(attempt.transition.family, input.family);
    }

    #[test]
    fn attempts_are_repeatable_and_event_state_is_base_step_invariant() {
        let coarse_input = synthetic_control_transition_input(0.7);
        let coarse_policy = synthetic_control_transition_policy(
            &coarse_input,
            ControlTransitionTrigger::DualEngineGeneratorLoss,
        );
        let fine_input = synthetic_control_transition_input(0.31);
        let fine_policy = synthetic_control_transition_policy(
            &fine_input,
            ControlTransitionTrigger::DualEngineGeneratorLoss,
        );
        let schedule = ExactTimeCheckpointSchedule {
            requested_elapsed_times: vec![Seconds(3.37), Seconds(4.0), Seconds(5.5)],
        };

        let first = attempt_controlled_to_uncontrolled_with_checkpoints(
            &coarse_input,
            &coarse_policy,
            &schedule,
        )
        .unwrap();
        let repeated = attempt_controlled_to_uncontrolled_with_checkpoints(
            &coarse_input,
            &coarse_policy,
            &schedule,
        )
        .unwrap();
        let fine = attempt_controlled_to_uncontrolled_with_checkpoints(
            &fine_input,
            &fine_policy,
            &schedule,
        )
        .unwrap();

        assert_eq!(first, repeated);
        assert_eq!(first.checkpoint_status, fine.checkpoint_status);
        let first_event = match &first.control_transition {
            ControlTransitionOutcome::Reached { event } => event.as_ref(),
            ControlTransitionOutcome::NotReached { .. } => panic!("expected transition"),
        };
        let fine_event = match &fine.control_transition {
            ControlTransitionOutcome::Reached { event } => event.as_ref(),
            ControlTransitionOutcome::NotReached { .. } => panic!("expected transition"),
        };
        assert_eq!(first_event.elapsed, fine_event.elapsed);
        assert_eq!(first_event.time, fine_event.time);
        assert_eq!(first_event.trigger, fine_event.trigger);
        assert_eq!(first_event.state.engines, fine_event.state.engines);
        assert_eq!(first_event.state.electrical, fine_event.state.electrical);
        assert_eq!(first_event.state.apu, fine_event.state.apu);
        assert_eq!(first_event.state.ocxo, fine_event.state.ocxo);
        for (first_checkpoint, fine_checkpoint) in first.checkpoints.iter().zip(&fine.checkpoints) {
            assert_eq!(
                first_checkpoint.requested_elapsed,
                fine_checkpoint.requested_elapsed
            );
            assert_eq!(
                first_checkpoint.active_control,
                fine_checkpoint.active_control
            );
            assert_eq!(
                first_checkpoint.state.engines,
                fine_checkpoint.state.engines
            );
            assert_eq!(
                first_checkpoint.state.electrical.source,
                fine_checkpoint.state.electrical.source
            );
            assert_eq!(
                first_checkpoint.state.electrical.satcom_powered,
                fine_checkpoint.state.electrical.satcom_powered
            );
            match (
                first_checkpoint
                    .state
                    .electrical
                    .dual_engine_generator_loss_elapsed,
                fine_checkpoint
                    .state
                    .electrical
                    .dual_engine_generator_loss_elapsed,
            ) {
                (Some(first_elapsed), Some(fine_elapsed)) => {
                    assert!((first_elapsed.0 - fine_elapsed.0).abs() < 1.0e-10);
                }
                (None, None) => {}
                _ => panic!("base step changed generator-loss timer presence"),
            }
            assert_eq!(
                first_checkpoint.state.apu.mode,
                fine_checkpoint.state.apu.mode
            );
            assert_eq!(
                first_checkpoint.state.apu.generator_online,
                fine_checkpoint.state.apu.generator_online
            );
            assert_eq!(
                first_checkpoint.state.apu.fuel_flow,
                fine_checkpoint.state.apu.fuel_flow
            );
            assert!(
                (first_checkpoint.state.apu.elapsed_in_mode.0
                    - fine_checkpoint.state.apu.elapsed_in_mode.0)
                    .abs()
                    < 1.0e-10
            );
            assert_eq!(
                first_checkpoint.state.ocxo.power,
                fine_checkpoint.state.ocxo.power
            );
            assert_eq!(
                first_checkpoint.state.ocxo.restart_count,
                fine_checkpoint.state.ocxo.restart_count
            );
            assert!(
                (first_checkpoint.state.ocxo.unpowered_duration.0
                    - fine_checkpoint.state.ocxo.unpowered_duration.0)
                    .abs()
                    < 1.0e-10
            );
            assert_eq!(
                first_checkpoint.events_at_time,
                fine_checkpoint.events_at_time
            );
        }
    }

    #[test]
    fn attempt_rejects_invalid_checkpoint_schedule() {
        let input = synthetic_control_transition_input(0.7);
        let policy = synthetic_control_transition_policy(
            &input,
            ControlTransitionTrigger::DualEngineGeneratorLoss,
        );
        let unsorted = ExactTimeCheckpointSchedule {
            requested_elapsed_times: vec![Seconds(5.0), Seconds(4.0)],
        };

        assert!(matches!(
            attempt_controlled_to_uncontrolled_with_checkpoints(&input, &policy, &unsorted),
            Err(ControlledToUncontrolledAttemptError::Schedule(
                ExactTimeCheckpointScheduleError::NotStrictlyIncreasing { index: 1, .. }
            ))
        ));
    }

    #[test]
    fn mixed_control_matches_fixed_control_through_exact_dual_flameout() {
        let input = synthetic_control_transition_input(0.7);
        let policy = synthetic_control_transition_policy(
            &input,
            ControlTransitionTrigger::DualEngineFlameout,
        );

        let mixed = propagate_controlled_to_uncontrolled(&input, &policy).unwrap();
        let mut fixed_input = input.clone();
        fixed_input.integration.maximum_duration = Seconds(4.0);
        let fixed = propagate_transition(&fixed_input).unwrap();
        let transition = &mixed.control_transition;

        assert_eq!(fixed.termination, TransitionTermination::MaximumDuration);
        assert_eq!(transition.elapsed, Seconds(4.0));
        assert_eq!(
            transition.time,
            Seconds(input.initial.flight.time.0 + transition.elapsed.0)
        );
        assert_eq!(
            transition.trigger,
            ControlTransitionTrigger::DualEngineFlameout
        );
        assert_eq!(transition.from, ControlFamily::Controlled);
        assert_eq!(transition.to, ControlFamily::Uncontrolled);
        assert_eq!(transition.state, fixed.terminal);
        assert_eq!(
            transition.pre_trigger_command,
            policy.pre_trigger_controlled.segments[0].command
        );
        assert_eq!(
            transition.post_trigger_command,
            policy.post_trigger_uncontrolled.segments[0].command
        );
    }

    #[test]
    fn generator_loss_switch_uses_post_trigger_schedule_and_is_repeatable() {
        let input = synthetic_control_transition_input(0.7);
        let policy = synthetic_control_transition_policy(
            &input,
            ControlTransitionTrigger::DualEngineGeneratorLoss,
        );

        let first = propagate_controlled_to_uncontrolled(&input, &policy).unwrap();
        let second = propagate_controlled_to_uncontrolled(&input, &policy).unwrap();
        let fixed_controlled = propagate_transition(&input).unwrap();
        let switch = &first.control_transition;
        let mut fixed_post_input = input.clone();
        fixed_post_input.initial = TransitionInitialCondition {
            flight: switch.state.kinematics.point_mass,
            mass: input.initial.mass,
            fuel: switch.state.fuel,
            engines: switch.state.engines,
            electrical: switch.state.electrical,
            apu: switch.state.apu,
            ocxo: switch.state.ocxo,
        };
        fixed_post_input.family.control = ControlFamily::Uncontrolled;
        fixed_post_input.control = policy.post_trigger_uncontrolled.clone();
        fixed_post_input.integration.maximum_duration =
            Seconds(input.integration.maximum_duration.0 - switch.elapsed.0);
        let fixed_post = propagate_transition(&fixed_post_input).unwrap();

        assert_eq!(first, second);
        assert_eq!(first.terminal, fixed_post.terminal);
        assert_eq!(first.termination, fixed_post.termination);
        assert_eq!(first.impact, fixed_post.impact);
        assert_eq!(first.scenario, policy.scenario);
        assert_eq!(first.restart_transient, input.family.restart_transient);
        assert_eq!(first.model_weight, input.model_weight);
        assert_eq!(first.control_transition.elapsed, Seconds(4.0));
        assert_eq!(
            first.control_transition.trigger,
            ControlTransitionTrigger::DualEngineGeneratorLoss
        );
        assert_eq!(
            first.terminal_control,
            policy.post_trigger_uncontrolled.segments[1].command
        );
        assert!(
            first.terminal.kinematics.vertical_speed.0
                < fixed_controlled.terminal.kinematics.vertical_speed.0
        );
    }

    #[test]
    fn mixed_switch_discrete_state_is_base_step_invariant() {
        let coarse_input = synthetic_control_transition_input(0.7);
        let fine_input = synthetic_control_transition_input(0.31);
        let coarse_policy = synthetic_control_transition_policy(
            &coarse_input,
            ControlTransitionTrigger::DualEngineGeneratorLoss,
        );
        let fine_policy = synthetic_control_transition_policy(
            &fine_input,
            ControlTransitionTrigger::DualEngineGeneratorLoss,
        );

        let coarse = propagate_controlled_to_uncontrolled(&coarse_input, &coarse_policy).unwrap();
        let fine = propagate_controlled_to_uncontrolled(&fine_input, &fine_policy).unwrap();
        let coarse_switch = &coarse.control_transition;
        let fine_switch = &fine.control_transition;

        assert_eq!(coarse_switch.time, Seconds(4.0));
        assert_eq!(fine_switch.time, Seconds(4.0));
        assert_eq!(coarse_switch.elapsed, fine_switch.elapsed);
        assert_eq!(coarse_switch.trigger, fine_switch.trigger);
        assert_eq!(
            coarse_switch.pre_trigger_command,
            fine_switch.pre_trigger_command
        );
        assert_eq!(
            coarse_switch.post_trigger_command,
            fine_switch.post_trigger_command
        );
        assert_eq!(coarse_switch.state.mass, fine_switch.state.mass);
        assert_eq!(coarse_switch.state.fuel, fine_switch.state.fuel);
        assert_eq!(coarse_switch.state.engines, fine_switch.state.engines);
        assert_eq!(coarse_switch.state.electrical, fine_switch.state.electrical);
        assert_eq!(coarse_switch.state.apu, fine_switch.state.apu);
        assert_eq!(coarse_switch.state.ocxo, fine_switch.state.ocxo);
    }

    #[test]
    fn mixed_policy_rejects_mismatch_invalid_post_schedule_and_unreachable_trigger() {
        let input = synthetic_control_transition_input(0.7);

        let mut mismatched = synthetic_control_transition_policy(
            &input,
            ControlTransitionTrigger::DualEngineFlameout,
        );
        mismatched.pre_trigger_controlled.segments[0].command = ControlCommand::Controlled {
            lift_load_factor: 0.9,
            bank_angle: Degrees(0.0),
        };
        assert!(matches!(
            propagate_controlled_to_uncontrolled(&input, &mismatched),
            Err(ControlledToUncontrolledError::PreTriggerScheduleMismatch)
        ));

        let mut invalid_post = synthetic_control_transition_policy(
            &input,
            ControlTransitionTrigger::DualEngineFlameout,
        );
        invalid_post.post_trigger_uncontrolled = input.control.clone();
        assert!(matches!(
            propagate_controlled_to_uncontrolled(&input, &invalid_post),
            Err(ControlledToUncontrolledError::InvalidPostTriggerSchedule { .. })
        ));

        let mut unreachable_input = input;
        unreachable_input.initial.engines.left.fuel_flow = KilogramsPerSecond(0.0);
        unreachable_input.initial.engines.right.fuel_flow = KilogramsPerSecond(0.0);
        let unreachable_policy = synthetic_control_transition_policy(
            &unreachable_input,
            ControlTransitionTrigger::DualEngineFlameout,
        );
        assert!(matches!(
            propagate_controlled_to_uncontrolled(&unreachable_input, &unreachable_policy),
            Err(ControlledToUncontrolledError::TriggerNotReached {
                trigger: ControlTransitionTrigger::DualEngineFlameout,
                termination: TransitionTermination::MaximumDuration,
            })
        ));
    }

    #[test]
    fn family_and_control_schedule_cannot_be_silently_mixed() {
        let mut input = synthetic_level_input();
        input.family.control = ControlFamily::Controlled;
        assert!(matches!(
            propagate_transition(&input),
            Err(TransitionError::InvalidInput(
                "control commands must match the named control family"
            ))
        ));
    }

    #[test]
    fn caller_owned_time_varying_atmosphere_is_used_at_integration_evaluations() {
        let input = synthetic_control_transition_input(0.7);
        let policy = synthetic_control_transition_policy(
            &input,
            ControlTransitionTrigger::DualEngineFlameout,
        );
        let schedule = ExactTimeCheckpointSchedule {
            requested_elapsed_times: vec![Seconds(3.5)],
        };
        let atmosphere = TimeVaryingTestAtmosphere {
            calls: Cell::new(0),
        };
        let dynamic = attempt_controlled_to_uncontrolled_with_atmosphere_and_checkpoints(
            &input,
            &policy,
            &schedule,
            &atmosphere,
        )
        .unwrap();
        let static_result =
            attempt_controlled_to_uncontrolled_with_checkpoints(&input, &policy, &schedule)
                .unwrap();
        assert!(atmosphere.calls.get() > 4);
        assert_ne!(
            dynamic.transition.terminal.kinematics.point_mass.position,
            static_result
                .transition
                .terminal
                .kinematics
                .point_mass
                .position
        );
    }
}
