//! Event-driven powered-flight kinematics for broad trajectory inference.
//!
//! This module deliberately separates a declared kinematic/performance envelope
//! from a declared stochastic manoeuvre process.  The envelope is a conservative
//! public-data proxy, not a calibrated Boeing 777 control-law or propulsion
//! model.  Fuel, thrust availability, engine state, and likelihoods remain
//! caller-owned and can be composed through the per-step observer API.
//!
//! Random marks and renewal clocks consume only the `ChaCha8Rng` supplied by
//! the caller.  Absolute next-event times live in `PoweredFlightState`, so
//! changing numerical substep cadence does not itself create random draws.

use std::{convert::Infallible, error::Error};

use mh370_domain::{
    destination_wgs84, AircraftState, Degrees, Feet, FeetPerMinute, Knots, LatLon, NauticalMiles,
    Seconds,
};
use rand::{Rng, RngCore, SeedableRng};
use rand_chacha::ChaCha8Rng;
use rand_distr::{Distribution, Exp, Gamma};
use serde::{Deserialize, Serialize};
use sha2::{Digest, Sha256};
use thiserror::Error;

use crate::{
    fixed_waypoint_guidance, ground_velocity_from_control, EnvironmentError, Era5Grid,
    FixedWaypointLeg, IgrfGrid, LateralMode, WaypointError, WeatherSample,
};

const KNOT_M_S: f64 = 0.514_444_444_444_444_5;
const STANDARD_GRAVITY_M_S2: f64 = 9.806_65;
const SEA_LEVEL_PRESSURE_PA: f64 = 101_325.0;
const SEA_LEVEL_SOUND_SPEED_M_S: f64 = 340.294;
const TIME_TOLERANCE_S: f64 = 1.0e-9;
const EVENT_PROPOSAL_RNG_DOMAIN: &[u8] = b"mh370-powered-event-proposal-v1";
pub const MAX_POWERED_EVENT_PROPOSAL_CANDIDATES: usize = 64;

/// Lateral control semantics supported by the broad powered-flight kernel.
///
/// `GreatCircleTrackContinuation` is only a geometric long-leg continuation.
/// It does not imply an operational LNAV waypoint or pilot intent.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum PoweredLateralMode {
    ConstantTrueHeading,
    ConstantMagneticHeading,
    ConstantTrueTrack,
    ConstantMagneticTrack,
    GreatCircleTrackContinuation,
}

#[derive(Debug, Clone, Copy, PartialEq, Serialize, Deserialize)]
pub struct PoweredLateralModeWeights {
    pub constant_true_heading: f64,
    pub constant_magnetic_heading: f64,
    pub constant_true_track: f64,
    pub constant_magnetic_track: f64,
    pub great_circle_track_continuation: f64,
}

impl PoweredLateralModeWeights {
    fn values(self) -> [(PoweredLateralMode, f64); 5] {
        [
            (
                PoweredLateralMode::ConstantTrueHeading,
                self.constant_true_heading,
            ),
            (
                PoweredLateralMode::ConstantMagneticHeading,
                self.constant_magnetic_heading,
            ),
            (
                PoweredLateralMode::ConstantTrueTrack,
                self.constant_true_track,
            ),
            (
                PoweredLateralMode::ConstantMagneticTrack,
                self.constant_magnetic_track,
            ),
            (
                PoweredLateralMode::GreatCircleTrackContinuation,
                self.great_circle_track_continuation,
            ),
        ]
    }

    fn validate(self) -> Result<(), PoweredFlightError> {
        let values = self.values();
        if values
            .iter()
            .any(|(_, weight)| !weight.is_finite() || *weight < 0.0)
            || values.iter().map(|(_, weight)| weight).sum::<f64>() <= 0.0
        {
            return Err(PoweredFlightError::InvalidManeuverProcess);
        }
        Ok(())
    }
}

/// Shifted-gamma renewal clock.  Shape 1 is exponential; other positive shapes
/// permit a declared semi-Markov dwell-time family.
#[derive(Debug, Clone, Copy, PartialEq, Serialize, Deserialize)]
pub struct RenewalClock {
    pub mean_interval_s: f64,
    pub minimum_interval_s: f64,
    pub gamma_shape: f64,
}

impl RenewalClock {
    fn validate(self) -> Result<(), PoweredFlightError> {
        if !self.mean_interval_s.is_finite()
            || !self.minimum_interval_s.is_finite()
            || !self.gamma_shape.is_finite()
            || self.minimum_interval_s <= 0.0
            || self.mean_interval_s <= self.minimum_interval_s
            || self.gamma_shape <= 0.0
        {
            return Err(PoweredFlightError::InvalidManeuverProcess);
        }
        Ok(())
    }

    fn sample_wait_s(self, rng: &mut ChaCha8Rng) -> Result<f64, PoweredFlightError> {
        self.validate()?;
        let scale = (self.mean_interval_s - self.minimum_interval_s) / self.gamma_shape;
        let gamma = Gamma::new(self.gamma_shape, scale)
            .map_err(|_| PoweredFlightError::InvalidManeuverProcess)?;
        Ok(self.minimum_interval_s + gamma.sample(rng))
    }
}

/// Declared stochastic law for control-target changes.  `None` disables that
/// event stream.  No field is a Boeing probability or inferred pilot intent.
#[derive(Debug, Clone, Copy, PartialEq, Serialize, Deserialize)]
pub struct ManeuverProcess {
    pub lateral_clock: Option<RenewalClock>,
    pub speed_clock: Option<RenewalClock>,
    pub altitude_clock: Option<RenewalClock>,
    pub lateral_mode_weights: PoweredLateralModeWeights,
    pub maximum_course_change_deg: f64,
    pub target_mach_min: f64,
    pub target_mach_max: f64,
    pub target_altitude_min_ft: f64,
    pub target_altitude_max_ft: f64,
    pub great_circle_leg_length_nm: f64,
}

impl ManeuverProcess {
    pub fn validate(self, limits: PoweredFlightLimits) -> Result<(), PoweredFlightError> {
        for clock in [self.lateral_clock, self.speed_clock, self.altitude_clock]
            .into_iter()
            .flatten()
        {
            clock.validate()?;
        }
        self.lateral_mode_weights.validate()?;
        if ![
            self.maximum_course_change_deg,
            self.target_mach_min,
            self.target_mach_max,
            self.target_altitude_min_ft,
            self.target_altitude_max_ft,
            self.great_circle_leg_length_nm,
        ]
        .iter()
        .all(|value| value.is_finite())
            || !(0.0..=180.0).contains(&self.maximum_course_change_deg)
            || self.target_mach_min <= 0.0
            || self.target_mach_max <= self.target_mach_min
            || self.target_mach_max > limits.mmo
            || self.target_altitude_min_ft < limits.minimum_pressure_altitude_ft
            || self.target_altitude_max_ft > limits.maximum_pressure_altitude_ft
            || self.target_altitude_max_ft <= self.target_altitude_min_ft
            || self.great_circle_leg_length_nm <= 0.0
        {
            return Err(PoweredFlightError::InvalidManeuverProcess);
        }
        Ok(())
    }
}

/// Declared conservative kinematic and lift/speed envelope.
///
/// VMO is represented as calibrated airspeed using subsonic compressible-flow
/// conversion.  The stall floor is calculated from caller-supplied gross mass,
/// wing area, CLmax, bank load factor, and local ERA5 density.  Climb, descent,
/// acceleration and roll limits are explicit proxy caps.  Thrust-required and
/// thrust-available checks are intentionally external to this crate.
#[derive(Debug, Clone, Copy, PartialEq, Serialize, Deserialize)]
pub struct PoweredFlightLimits {
    pub minimum_pressure_altitude_ft: f64,
    pub maximum_pressure_altitude_ft: f64,
    pub minimum_mach_floor: f64,
    pub mmo: f64,
    pub vmo_kcas: f64,
    pub wing_area_m2: f64,
    pub maximum_lift_coefficient: f64,
    pub stall_speed_margin: f64,
    pub maximum_bank_deg: f64,
    pub maximum_roll_rate_deg_s: f64,
    pub maximum_mach_rate_per_s: f64,
    pub maximum_climb_rate_ft_min: f64,
    pub maximum_descent_rate_ft_min: f64,
    pub maximum_vertical_acceleration_ft_min_s: f64,
    pub heading_capture_time_s: f64,
    pub altitude_capture_time_s: f64,
}

impl PoweredFlightLimits {
    pub fn validate(self) -> Result<(), PoweredFlightError> {
        let values = [
            self.minimum_pressure_altitude_ft,
            self.maximum_pressure_altitude_ft,
            self.minimum_mach_floor,
            self.mmo,
            self.vmo_kcas,
            self.wing_area_m2,
            self.maximum_lift_coefficient,
            self.stall_speed_margin,
            self.maximum_bank_deg,
            self.maximum_roll_rate_deg_s,
            self.maximum_mach_rate_per_s,
            self.maximum_climb_rate_ft_min,
            self.maximum_descent_rate_ft_min,
            self.maximum_vertical_acceleration_ft_min_s,
            self.heading_capture_time_s,
            self.altitude_capture_time_s,
        ];
        if values.iter().any(|value| !value.is_finite())
            || self.minimum_pressure_altitude_ft < 0.0
            || self.maximum_pressure_altitude_ft <= self.minimum_pressure_altitude_ft
            || self.minimum_mach_floor <= 0.0
            || self.mmo <= self.minimum_mach_floor
            || self.mmo >= 1.0
            || self.vmo_kcas <= 0.0
            || self.wing_area_m2 <= 0.0
            || self.maximum_lift_coefficient <= 0.0
            || self.stall_speed_margin < 1.0
            || !(0.0..89.0).contains(&self.maximum_bank_deg)
            || self.maximum_roll_rate_deg_s <= 0.0
            || self.maximum_mach_rate_per_s <= 0.0
            || self.maximum_climb_rate_ft_min <= 0.0
            || self.maximum_descent_rate_ft_min <= 0.0
            || self.maximum_vertical_acceleration_ft_min_s <= 0.0
            || self.heading_capture_time_s <= 0.0
            || self.altitude_capture_time_s <= 0.0
        {
            return Err(PoweredFlightError::InvalidLimits);
        }
        Ok(())
    }
}

#[derive(Debug, Clone, Copy, PartialEq, Serialize, Deserialize)]
pub struct PoweredIntegration {
    pub steady_step_s: f64,
    pub transition_step_s: f64,
    pub heading_capture_tolerance_deg: f64,
    pub maximum_events_per_transition: u32,
}

impl PoweredIntegration {
    pub fn validate(self) -> Result<(), PoweredFlightError> {
        if !self.steady_step_s.is_finite()
            || !self.transition_step_s.is_finite()
            || !self.heading_capture_tolerance_deg.is_finite()
            || self.steady_step_s <= 0.0
            || self.transition_step_s <= 0.0
            || self.heading_capture_tolerance_deg <= 0.0
            || self.heading_capture_tolerance_deg >= 10.0
            || self.maximum_events_per_transition == 0
        {
            return Err(PoweredFlightError::InvalidIntegration);
        }
        Ok(())
    }
}

#[derive(Debug, Clone, Copy)]
pub struct PoweredFlightEnvironment<'a> {
    pub weather: &'a Era5Grid,
    pub magnetic: Option<&'a IgrfGrid>,
    pub magnetic_altitude_policy: MagneticAltitudePolicy,
    pub time_origin_unix_s: f64,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum MagneticAltitudePolicy {
    RejectOutsideGrid,
    ClampToGridAltitude,
}

#[derive(Debug, Clone, Copy, PartialEq, Serialize, Deserialize)]
pub struct PoweredFlightCommand {
    pub lateral_mode: PoweredLateralMode,
    /// Heading or track in the reference frame named by `lateral_mode`.
    pub selected_control: Degrees,
    /// Present only for the explicitly geometric great-circle mode.
    pub great_circle_destination: Option<LatLon>,
    pub target_mach: f64,
    pub target_pressure_altitude: Feet,
}

/// One scheduled renewal event and the end of its compulsory dwell period.
///
/// `not_before` records the event origin that a bare next-event timestamp
/// loses: it is the preceding event time (or initialization time) plus the
/// renewal law's minimum interval.  This makes an exact memoryless refresh of
/// a surviving shape-one renewal possible both before and after that boundary.
#[derive(Debug, Clone, Copy, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct PendingRenewal {
    pub not_before: Seconds,
    pub next_event: Seconds,
}

/// Pending renewals for the three independent manoeuvre streams.
///
/// This object schema intentionally rejects the former serialized numeric
/// `next_*_event` fields.  Those timestamps do not contain enough information
/// to reconstruct `not_before`; persisted states using the old schema must be
/// regenerated from their declared initialization inputs.
#[derive(Debug, Clone, Copy, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct PoweredEventClocks {
    pub lateral: Option<PendingRenewal>,
    pub speed: Option<PendingRenewal>,
    pub altitude: Option<PendingRenewal>,
}

#[derive(Debug, Clone, Copy, Default, PartialEq, Eq, Serialize, Deserialize)]
pub struct PoweredEventCounters {
    pub lateral: u32,
    pub speed: u32,
    pub altitude: u32,
}

impl PoweredEventCounters {
    pub fn total(self) -> u32 {
        self.lateral
            .saturating_add(self.speed)
            .saturating_add(self.altitude)
    }

    fn checked_add(&mut self, other: Self) -> Result<(), PoweredFlightError> {
        self.lateral = self
            .lateral
            .checked_add(other.lateral)
            .ok_or(PoweredFlightError::EventCounterOverflow)?;
        self.speed = self
            .speed
            .checked_add(other.speed)
            .ok_or(PoweredFlightError::EventCounterOverflow)?;
        self.altitude = self
            .altitude
            .checked_add(other.altitude)
            .ok_or(PoweredFlightError::EventCounterOverflow)?;
        Ok(())
    }
}

/// Fixed-size Markov state.  Fuel and electrical state are deliberately not
/// embedded here; the estimator composes those correlated states separately.
#[derive(Debug, Clone, Copy, PartialEq, Serialize, Deserialize)]
pub struct PoweredFlightState {
    pub aircraft: AircraftState,
    pub heading_true: Degrees,
    pub mach: f64,
    pub bank_angle: Degrees,
    pub command: PoweredFlightCommand,
    pub event_clocks: PoweredEventClocks,
    pub event_counters: PoweredEventCounters,
}

/// One of the independent marked renewal processes in the powered-flight
/// kernel.  Events that are due at the same instant are always applied in
/// lateral, speed, then altitude order.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum PoweredEventKind {
    Lateral,
    Speed,
    Altitude,
}

impl PoweredEventClocks {
    const fn pending(self, kind: PoweredEventKind) -> Option<PendingRenewal> {
        match kind {
            PoweredEventKind::Lateral => self.lateral,
            PoweredEventKind::Speed => self.speed,
            PoweredEventKind::Altitude => self.altitude,
        }
    }

    fn set_pending(&mut self, kind: PoweredEventKind, pending: Option<PendingRenewal>) {
        match kind {
            PoweredEventKind::Lateral => self.lateral = pending,
            PoweredEventKind::Speed => self.speed = pending,
            PoweredEventKind::Altitude => self.altitude = pending,
        }
    }
}

impl ManeuverProcess {
    const fn renewal_clock(self, kind: PoweredEventKind) -> Option<RenewalClock> {
        match kind {
            PoweredEventKind::Lateral => self.lateral_clock,
            PoweredEventKind::Speed => self.speed_clock,
            PoweredEventKind::Altitude => self.altitude_clock,
        }
    }
}

/// The primitive latent mark sampled by a powered-flight event.
///
/// The lateral course change is deliberately retained before wrapping to a
/// heading or track.  That makes it an unambiguous draw from the declared
/// uniform prior even at the zero/360-degree boundary.
#[derive(Debug, Clone, Copy, PartialEq, Serialize, Deserialize)]
#[serde(tag = "kind", rename_all = "snake_case")]
pub enum PoweredEventMark {
    Lateral {
        mode: PoweredLateralMode,
        course_change_deg: f64,
    },
    Speed {
        target_mach: f64,
    },
    Altitude {
        target_pressure_altitude_ft: f64,
    },
}

/// A due event presented before any proposal candidates are generated.
///
/// `event_number` is one-based within `kind`.  A guide should make its
/// eligibility decision from this context, including any fixed physical
/// observation horizon it owns, rather than from a numerical step endpoint.
#[derive(Debug, Clone, Copy, PartialEq, Serialize, Deserialize)]
pub struct PoweredEventProposalEvent {
    pub kind: PoweredEventKind,
    pub event_number: u64,
    pub before: PoweredFlightState,
}

/// A valid prior-mark candidate presented to a caller-owned guide scorer.
///
/// `after_mark` contains the changed command but not a renewed event clock or
/// incremented counter.  A predictive scorer must therefore replace/disable
/// due clocks before propagating this state to its fixed observation horizon.
#[derive(Debug, Clone, Copy, PartialEq, Serialize, Deserialize)]
pub struct PoweredEventProposalCandidate {
    pub event: PoweredEventProposalEvent,
    pub candidate_index: usize,
    pub mark: PoweredEventMark,
    pub after_mark: PoweredFlightState,
}

/// Caller-owned, evidence-aware scoring at the dynamics/evidence boundary.
///
/// Dynamics owns every prior draw, the defensive categorical proposal, and
/// its exact correction.  Implementations only decide which due events are
/// worth proposing and supply relative log scores for valid candidates.  A
/// score may be a proxy or tempered prediction of upcoming evidence, but the
/// guide must not mutate the scientific likelihood/evidence state or
/// assimilate the eventual observation here.  Both methods must be replay
/// deterministic functions of their inputs and immutable configuration;
/// interior mutability must not make a repeated call return a different
/// eligibility decision or score.
pub trait PoweredEventCandidateScorer: Sync {
    type Error: Error + 'static;

    fn is_eligible(&self, event: &PoweredEventProposalEvent) -> Result<bool, Self::Error>;

    /// Return a finite relative log score or negative infinity to give a
    /// candidate only the defensive-prior probability.  NaN and positive
    /// infinity are rejected.  A recoverable candidate-specific projection
    /// failure should return negative infinity; `Err` aborts the transition.
    fn log_score(&self, candidate: &PoweredEventProposalCandidate) -> Result<f64, Self::Error>;
}

/// Tuning of the finite prior-candidate proposal at an eligible event.
#[derive(Debug, Clone, Copy, PartialEq, Serialize, Deserialize)]
pub struct PoweredEventProposalConfig {
    pub candidates_per_event: usize,
    /// Positive probability assigned to the uniform choice among prior
    /// candidates.  This must lie in `(0, 1]`.
    pub defensive_prior_probability: f64,
}

impl PoweredEventProposalConfig {
    pub fn validate(self) -> Result<(), PoweredEventProposalConfigError> {
        if !(1..=MAX_POWERED_EVENT_PROPOSAL_CANDIDATES).contains(&self.candidates_per_event) {
            return Err(PoweredEventProposalConfigError::InvalidCandidateCount);
        }
        let defensive_per_candidate =
            self.defensive_prior_probability / self.candidates_per_event as f64;
        if !self.defensive_prior_probability.is_finite()
            || self.defensive_prior_probability <= 0.0
            || self.defensive_prior_probability > 1.0
            || !defensive_per_candidate.is_finite()
            || defensive_per_candidate <= 0.0
        {
            return Err(PoweredEventProposalConfigError::InvalidDefensivePriorProbability);
        }
        Ok(())
    }
}

#[derive(Debug, Error, Clone, Copy, PartialEq, Eq)]
pub enum PoweredEventProposalConfigError {
    #[error(
        "powered-event proposal candidate count must be between 1 and {MAX_POWERED_EVENT_PROPOSAL_CANDIDATES}"
    )]
    InvalidCandidateCount,
    #[error("powered-event defensive prior probability must remain positive after division by K")]
    InvalidDefensivePriorProbability,
}

/// Transition-scoped key for collision-separated event-proposal randomness.
///
/// Construct this exactly once per particle's complete physical observation
/// transition and reuse it across every numerical segment or bridge split.
/// Candidate indices are keyed independently, so adding candidates or an
/// unrelated event cannot shift an existing candidate stream.
#[derive(Clone, Copy, PartialEq, Eq)]
pub struct PoweredEventProposalRng {
    transition_key: [u8; 32],
}

impl std::fmt::Debug for PoweredEventProposalRng {
    fn fmt(&self, formatter: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        formatter
            .debug_struct("PoweredEventProposalRng")
            .finish_non_exhaustive()
    }
}

impl PoweredEventProposalRng {
    /// Use a caller-derived key that is unique to the particle and physical
    /// observation transition.
    pub const fn from_seed(transition_key: [u8; 32]) -> Self {
        Self { transition_key }
    }

    /// Consume one fixed-size key from a caller RNG.  Call this once before a
    /// complete physical observation transition, never once per step.
    pub fn from_rng(rng: &mut ChaCha8Rng) -> Self {
        let mut transition_key = [0_u8; 32];
        rng.fill_bytes(&mut transition_key);
        Self { transition_key }
    }

    fn event_rng(
        self,
        kind: PoweredEventKind,
        event_index: u32,
        purpose: EventProposalRngPurpose,
        replicate: usize,
    ) -> ChaCha8Rng {
        let replicate = u64::try_from(replicate)
            .expect("proposal configuration rejects candidate indices larger than u64");
        let mut hash = Sha256::new();
        hash.update(EVENT_PROPOSAL_RNG_DOMAIN);
        hash.update(self.transition_key);
        hash.update([kind.rng_tag()]);
        hash.update(event_index.to_le_bytes());
        hash.update([purpose as u8]);
        hash.update(replicate.to_le_bytes());
        ChaCha8Rng::from_seed(hash.finalize().into())
    }
}

#[derive(Debug, Clone, Copy)]
#[repr(u8)]
enum EventProposalRngPurpose {
    CandidateMark = 0,
    Selection = 1,
    RenewalClock = 2,
}

impl PoweredEventKind {
    const fn rng_tag(self) -> u8 {
        match self {
            Self::Lateral => 0,
            Self::Speed => 1,
            Self::Altitude => 2,
        }
    }
}

/// Numerically descriptive diagnostics for one eligible proposed event.
#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct PoweredEventProposalDiagnostic {
    pub event_time: Seconds,
    pub kind: PoweredEventKind,
    pub event_number: u64,
    pub candidate_count: usize,
    pub selected_candidate_index: usize,
    /// Log of the normalized floating-point probability actually sampled.
    pub selected_log_probability: f64,
    pub log_prior_over_proposal: f64,
    pub finite_score_count: usize,
    pub minimum_finite_log_score: Option<f64>,
    pub maximum_finite_log_score: Option<f64>,
    pub all_scores_negative_infinity: bool,
    pub selection_effective_sample_size: f64,
    pub selection_entropy_nats: f64,
    pub materialization_failures: usize,
}

/// One accepted dynamics segment plus exact event-proposal bookkeeping.
#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct ProposedPoweredFlightSegment {
    pub segment: PoweredFlightSegment,
    pub log_prior_over_proposal: f64,
    pub proposed_events: PoweredEventCounters,
    pub event_proposals: Vec<PoweredEventProposalDiagnostic>,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum PoweredStepRegime {
    Steady,
    Transition,
}

#[derive(Debug, Clone, Copy, Default, PartialEq, Serialize, Deserialize)]
pub struct PoweredLimitActivity {
    pub stall_or_minimum_mach_floor: bool,
    pub vmo_or_mmo_ceiling: bool,
    pub bank: bool,
    pub roll_rate: bool,
    pub climb_rate: bool,
    pub descent_rate: bool,
    pub vertical_acceleration: bool,
    pub lower_altitude: bool,
    pub upper_altitude: bool,
}

#[derive(Debug, Clone, Copy, PartialEq, Serialize, Deserialize)]
pub struct InstantaneousPoweredLimits {
    pub minimum_mach: f64,
    pub maximum_mach: f64,
    pub stall_mach: f64,
    pub vmo_mach: f64,
    pub load_factor_g: f64,
    pub lift_coefficient: f64,
    pub maximum_bank_for_lift_deg: f64,
    pub maximum_turn_rate_deg_s: f64,
}

/// One accepted event-aligned integration segment.  Its midpoint fields map
/// directly onto a path-dependent fuel operating point.
#[derive(Debug, Clone, Copy, PartialEq, Serialize, Deserialize)]
pub struct PoweredFlightSegment {
    pub start: PoweredFlightState,
    pub end: PoweredFlightState,
    pub duration: Seconds,
    /// ERA5 sample used to convert the start Mach to true airspeed.
    pub start_weather: WeatherSample,
    pub midpoint_pressure_altitude: Feet,
    pub midpoint_mach: f64,
    pub midpoint_bank_angle: Degrees,
    pub midpoint_vertical_speed: FeetPerMinute,
    pub midpoint_weather: WeatherSample,
    /// ERA5 sample used to convert the end Mach to true airspeed.
    pub end_weather: WeatherSample,
    pub midpoint_limits: InstantaneousPoweredLimits,
    pub regime: PoweredStepRegime,
    pub active_limits: PoweredLimitActivity,
    pub magnetic_altitude_clamped: bool,
    pub great_circle_leg_renewed_at_start: bool,
    pub events_at_start: PoweredEventCounters,
    pub events_at_end: PoweredEventCounters,
}

#[derive(Debug, Clone, Copy, Default, PartialEq, Serialize, Deserialize)]
pub struct PoweredBoundarySeconds {
    pub stall_or_minimum_mach_floor: f64,
    pub vmo_or_mmo_ceiling: f64,
    pub bank: f64,
    pub roll_rate: f64,
    pub climb_rate: f64,
    pub descent_rate: f64,
    pub vertical_acceleration: f64,
    pub lower_altitude: f64,
    pub upper_altitude: f64,
    pub magnetic_altitude_clamp: f64,
}

#[derive(Debug, Clone, Copy, Default, PartialEq, Serialize, Deserialize)]
pub struct PoweredFlightDiagnostics {
    pub integration_steps: u64,
    pub steady_steps: u64,
    pub transition_steps: u64,
    pub event_aligned_steps: u64,
    pub target_clamp_count: u64,
    pub great_circle_leg_renewals: u64,
    pub events: PoweredEventCounters,
    pub boundary_seconds: PoweredBoundarySeconds,
}

#[derive(Debug, Clone, Copy, PartialEq, Serialize, Deserialize)]
pub struct PoweredFlightTransition {
    pub state: PoweredFlightState,
    pub diagnostics: PoweredFlightDiagnostics,
}

/// Reusable event budget for callers that manually compose dynamics and fuel
/// one segment at a time.  Reuse one budget for the complete PF transition.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
pub struct PoweredEventBudget {
    pub maximum_events: u32,
    pub consumed: PoweredEventCounters,
}

impl PoweredEventBudget {
    pub fn new(maximum_events: u32) -> Result<Self, PoweredFlightError> {
        if maximum_events == 0 {
            return Err(PoweredFlightError::InvalidIntegration);
        }
        Ok(Self {
            maximum_events,
            consumed: PoweredEventCounters::default(),
        })
    }

    fn record(&mut self, events: PoweredEventCounters) -> Result<(), PoweredFlightError> {
        self.consumed.checked_add(events)?;
        if self.consumed.total() > self.maximum_events {
            return Err(PoweredFlightError::EventLimitExceeded);
        }
        Ok(())
    }
}

#[derive(Debug, Error)]
pub enum ObservedPoweredFlightError<E: Error + 'static> {
    #[error(transparent)]
    Dynamics(#[from] PoweredFlightError),
    #[error("powered-flight segment observer failed: {0}")]
    Observer(E),
}

#[derive(Debug, Error)]
pub enum PoweredEventProposalError<E: Error + 'static> {
    #[error(transparent)]
    Dynamics(#[from] PoweredFlightError),
    #[error(transparent)]
    Configuration(#[from] PoweredEventProposalConfigError),
    #[error(
        "event-proposal scorer returned NaN or positive infinity for {kind:?} event {event_number}, candidate {candidate_index}"
    )]
    InvalidScore {
        kind: PoweredEventKind,
        event_number: u64,
        candidate_index: usize,
    },
    #[error("powered-event proposal scorer failed: {0}")]
    Scorer(#[source] E),
    #[error("selected powered-event proposal candidate could not be materialized: {source}")]
    SelectedCandidate {
        diagnostic: Box<PoweredEventProposalDiagnostic>,
        #[source]
        source: PoweredFlightError,
    },
}

/// Fail-closed reasons that an exact pending-renewal refresh cannot be made.
#[derive(Debug, Error, Clone, Copy, PartialEq, Eq)]
pub enum PoweredRenewalRefreshError {
    #[error("powered-flight state is invalid for renewal refresh")]
    InvalidState,
    #[error("powered renewal clock parameters are invalid")]
    InvalidClock,
    #[error("powered renewal refresh produced a non-finite event time")]
    NonFiniteEventTime,
    #[error("renewal refresh time must exactly match powered-flight state time")]
    CurrentTimeMismatch,
    #[error("powered {kind:?} renewal enablement differs between state and process")]
    ClockProcessMismatch { kind: PoweredEventKind },
    #[error("powered {kind:?} renewal stream is disabled")]
    StreamDisabled { kind: PoweredEventKind },
    #[error("powered {kind:?} renewal is already due and cannot be refreshed")]
    ClockDue { kind: PoweredEventKind },
    #[error("powered {kind:?} renewal origin lies after the current state time")]
    RenewalOriginInFuture { kind: PoweredEventKind },
    #[error("powered {kind:?} renewal refresh currently requires gamma_shape = 1")]
    UnsupportedGammaShape { kind: PoweredEventKind },
}

#[derive(Debug, Error, Clone, PartialEq)]
pub enum PoweredFlightError {
    #[error("invalid broad powered-flight limits")]
    InvalidLimits,
    #[error("invalid broad powered-flight manoeuvre process")]
    InvalidManeuverProcess,
    #[error("invalid broad powered-flight integration settings")]
    InvalidIntegration,
    #[error("powered-flight state is invalid or outside its declared envelope")]
    InvalidState,
    #[error("target time must be finite and not precede the state time")]
    InvalidTargetTime,
    #[error("magnetic control requires an in-domain magnetic declination grid")]
    MissingMagneticEnvironment,
    #[error(
        "magnetic-control altitude {altitude_ft} ft is outside IGRF [{minimum_ft}, {maximum_ft}] ft"
    )]
    MagneticAltitudeOutsideGrid {
        altitude_ft: f64,
        minimum_ft: f64,
        maximum_ft: f64,
    },
    #[error("no valid Mach interval remains under stall, VMO, and MMO limits")]
    EmptySpeedEnvelope,
    #[error(
        "Mach envelope at {time_s} s does not intersect the rate-reachable interval: envelope [{envelope_min}, {envelope_max}], reachable [{reachable_min}, {reachable_max}]"
    )]
    MachRateEnvelopeConflict {
        time_s: f64,
        envelope_min: f64,
        envelope_max: f64,
        reachable_min: f64,
        reachable_max: f64,
    },
    #[error("event counter overflow")]
    EventCounterOverflow,
    #[error("maximum events per transition exceeded")]
    EventLimitExceeded,
    #[error(transparent)]
    Environment(#[from] EnvironmentError),
    #[error("geodesic propagation failed: {0}")]
    Geodesy(String),
    #[error("great-circle continuation failed: {0}")]
    GreatCircle(String),
    #[error("ground-track control is infeasible in the sampled wind")]
    InfeasibleGroundTrack,
}

fn signed_angle_difference(target_deg: f64, reference_deg: f64) -> f64 {
    (target_deg - reference_deg + 180.0).rem_euclid(360.0) - 180.0
}

fn move_toward(current: f64, target: f64, maximum_change: f64) -> f64 {
    if (target - current).abs() <= maximum_change {
        target
    } else {
        current + maximum_change.copysign(target - current)
    }
}

fn rate_reachable_mach(
    current_mach: f64,
    target_mach: f64,
    maximum_change: f64,
    envelope: InstantaneousPoweredLimits,
    time_s: f64,
) -> Result<f64, PoweredFlightError> {
    let reachable_min = current_mach - maximum_change;
    let reachable_max = current_mach + maximum_change;
    let admissible_min = envelope.minimum_mach.max(reachable_min);
    let admissible_max = envelope.maximum_mach.min(reachable_max);
    if admissible_min > admissible_max + 1.0e-12 {
        return Err(PoweredFlightError::MachRateEnvelopeConflict {
            time_s,
            envelope_min: envelope.minimum_mach,
            envelope_max: envelope.maximum_mach,
            reachable_min,
            reachable_max,
        });
    }
    // Independent envelope and rate calculations can make two boundaries
    // that are mathematically coincident cross by a few ulps.  `f64::clamp`
    // panics on that ordering, so collapse only the already-tolerated gap to
    // one deterministic boundary point.  Material gaps still return the
    // typed conflict above.
    let admissible_max = admissible_max.max(admissible_min);
    Ok(target_mach.clamp(admissible_min, admissible_max))
}

/// Time integral of tan(bank) for a bank that rolls linearly toward its
/// command at the declared roll-rate and then holds.  This retains the turn
/// accumulated during rollout even when bank reaches zero before mid-step.
fn integrated_tangent_bank_seconds(
    start_bank_deg: f64,
    target_bank_deg: f64,
    maximum_roll_rate_deg_s: f64,
    duration_s: f64,
) -> f64 {
    let difference = target_bank_deg - start_bank_deg;
    if difference.abs() <= 1.0e-15 {
        return duration_s * start_bank_deg.to_radians().tan();
    }
    let signed_rate_deg_s = maximum_roll_rate_deg_s.copysign(difference);
    let ramp_duration_s = (difference.abs() / maximum_roll_rate_deg_s).min(duration_s);
    let end_ramp_deg = start_bank_deg + signed_rate_deg_s * ramp_duration_s;
    let signed_rate_rad_s = signed_rate_deg_s.to_radians();
    let ramp_integral = (start_bank_deg.to_radians().cos().ln()
        - end_ramp_deg.to_radians().cos().ln())
        / signed_rate_rad_s;
    ramp_integral + (duration_s - ramp_duration_s) * target_bank_deg.to_radians().tan()
}

fn magnetic_declination(
    environment: PoweredFlightEnvironment<'_>,
    altitude_ft: f64,
    position: LatLon,
) -> Result<Degrees, PoweredFlightError> {
    let grid = environment
        .magnetic
        .ok_or(PoweredFlightError::MissingMagneticEnvironment)?;
    let (minimum_ft, maximum_ft) = grid.altitude_bounds_ft();
    let query_altitude_ft = if altitude_ft < minimum_ft || altitude_ft > maximum_ft {
        match environment.magnetic_altitude_policy {
            MagneticAltitudePolicy::RejectOutsideGrid => {
                return Err(PoweredFlightError::MagneticAltitudeOutsideGrid {
                    altitude_ft,
                    minimum_ft,
                    maximum_ft,
                });
            }
            MagneticAltitudePolicy::ClampToGridAltitude => {
                altitude_ft.clamp(minimum_ft, maximum_ft)
            }
        }
    } else {
        altitude_ft
    };
    Ok(grid.declination(query_altitude_ft, position)?)
}

fn magnetic_altitude_is_clamped(
    mode: PoweredLateralMode,
    altitude_ft: f64,
    environment: PoweredFlightEnvironment<'_>,
) -> bool {
    if !matches!(
        mode,
        PoweredLateralMode::ConstantMagneticHeading | PoweredLateralMode::ConstantMagneticTrack
    ) || environment.magnetic_altitude_policy != MagneticAltitudePolicy::ClampToGridAltitude
    {
        return false;
    }
    environment
        .magnetic
        .map(|grid| {
            let (minimum_ft, maximum_ft) = grid.altitude_bounds_ft();
            altitude_ft < minimum_ft || altitude_ft > maximum_ft
        })
        .unwrap_or(false)
}

fn weather_at(
    environment: PoweredFlightEnvironment<'_>,
    state: AircraftState,
) -> Result<WeatherSample, PoweredFlightError> {
    if !environment.time_origin_unix_s.is_finite() {
        return Err(PoweredFlightError::InvalidState);
    }
    Ok(environment.weather.sample(
        environment.time_origin_unix_s + state.time.0,
        state.altitude.0,
        state.position,
    )?)
}

fn sample_clock(
    clock: Option<RenewalClock>,
    event_origin_s: f64,
    rng: &mut ChaCha8Rng,
) -> Result<Option<PendingRenewal>, PoweredFlightError> {
    clock
        .map(|clock| {
            clock.sample_wait_s(rng).map(|wait| PendingRenewal {
                not_before: Seconds(event_origin_s + clock.minimum_interval_s),
                // Keep this addition and the existing shifted-gamma draw
                // unchanged so no-refresh propagation retains its exact RNG
                // stream and floating-point event times.
                next_event: Seconds(event_origin_s + wait),
            })
        })
        .transpose()
}

/// Refresh one not-yet-due shape-one renewal from its exact conditional law.
///
/// If `t` is before the end of the compulsory dwell, the refreshed event is
/// `not_before + Exp(mean - minimum)`.  If `t` is at or after that boundary,
/// exponential memorylessness gives `t + tolerance + Exp(mean - minimum)`.
/// The tolerance matches the kernel's definition that an event at or before
/// `t + tolerance` is already due.  The implemented expression is therefore
/// `max(t + tolerance, not_before) + Exp(mean - minimum)`.
///
/// The supplied time must be exactly the state's time.  State/process stream
/// enablement must agree for all three clocks, and the selected stream must be
/// enabled, not due, and have `gamma_shape == 1`.  The function returns a copy
/// with only the selected `next_event` changed; `not_before` and every other
/// state field remain fixed.  No likelihood correction is required.
///
/// `domain_separated_rng` is caller-owned and must be derived independently
/// from propagation, mark-proposal, and other refresh randomness.  Calling
/// this function is the only operation here that consumes it.
pub fn refresh_powered_event_renewal(
    mut state: PoweredFlightState,
    kind: PoweredEventKind,
    process: ManeuverProcess,
    current_time: Seconds,
    domain_separated_rng: &mut ChaCha8Rng,
) -> Result<PoweredFlightState, PoweredRenewalRefreshError> {
    validate_state_shape(state).map_err(|_| PoweredRenewalRefreshError::InvalidState)?;
    if current_time != state.aircraft.time {
        return Err(PoweredRenewalRefreshError::CurrentTimeMismatch);
    }

    for stream_kind in [
        PoweredEventKind::Lateral,
        PoweredEventKind::Speed,
        PoweredEventKind::Altitude,
    ] {
        let process_clock = process.renewal_clock(stream_kind);
        if state.event_clocks.pending(stream_kind).is_some() != process_clock.is_some() {
            return Err(PoweredRenewalRefreshError::ClockProcessMismatch { kind: stream_kind });
        }
        if let Some(clock) = process_clock {
            clock
                .validate()
                .map_err(|_| PoweredRenewalRefreshError::InvalidClock)?;
            let pending = state
                .event_clocks
                .pending(stream_kind)
                .expect("state/process enablement was checked above");
            let renewal_origin_s = pending.not_before.0 - clock.minimum_interval_s;
            if !renewal_origin_s.is_finite() || renewal_origin_s > current_time.0 + TIME_TOLERANCE_S
            {
                return Err(PoweredRenewalRefreshError::RenewalOriginInFuture {
                    kind: stream_kind,
                });
            }
        }
    }

    let Some(clock) = process.renewal_clock(kind) else {
        return Err(PoweredRenewalRefreshError::StreamDisabled { kind });
    };
    if clock.gamma_shape != 1.0 {
        return Err(PoweredRenewalRefreshError::UnsupportedGammaShape { kind });
    }
    let pending = state
        .event_clocks
        .pending(kind)
        .ok_or(PoweredRenewalRefreshError::ClockProcessMismatch { kind })?;
    if pending.next_event.0 <= current_time.0 + TIME_TOLERANCE_S {
        return Err(PoweredRenewalRefreshError::ClockDue { kind });
    }

    let exponential_mean_s = clock.mean_interval_s - clock.minimum_interval_s;
    let exponential = Exp::new(exponential_mean_s.recip())
        .map_err(|_| PoweredRenewalRefreshError::InvalidClock)?;
    let next_event_s = (current_time.0 + TIME_TOLERANCE_S).max(pending.not_before.0)
        + exponential.sample(domain_separated_rng);
    if !next_event_s.is_finite() {
        return Err(PoweredRenewalRefreshError::NonFiniteEventTime);
    }
    state.event_clocks.set_pending(
        kind,
        Some(PendingRenewal {
            not_before: pending.not_before,
            next_event: Seconds(next_event_s),
        }),
    );
    Ok(state)
}

fn sample_mode(
    weights: PoweredLateralModeWeights,
    rng: &mut ChaCha8Rng,
) -> Result<PoweredLateralMode, PoweredFlightError> {
    weights.validate()?;
    let values = weights.values();
    let total = values.iter().map(|(_, weight)| weight).sum::<f64>();
    let draw = rng.gen::<f64>() * total;
    let mut cumulative = 0.0;
    for (mode, weight) in values {
        cumulative += weight;
        if draw <= cumulative {
            return Ok(mode);
        }
    }
    Ok(PoweredLateralMode::GreatCircleTrackContinuation)
}

fn great_circle_destination(
    position: LatLon,
    track_true: Degrees,
    length_nm: f64,
) -> Result<LatLon, PoweredFlightError> {
    destination_wgs84(position, track_true, NauticalMiles(length_nm))
        .map_err(|error| PoweredFlightError::Geodesy(error.to_string()))
}

fn renew_great_circle_leg_if_needed(
    state: &mut PoweredFlightState,
    process: ManeuverProcess,
) -> Result<bool, PoweredFlightError> {
    if !matches!(
        state.command.lateral_mode,
        PoweredLateralMode::GreatCircleTrackContinuation
    ) {
        return Ok(false);
    }
    let destination = state
        .command
        .great_circle_destination
        .ok_or(PoweredFlightError::InvalidState)?;
    let guidance = match fixed_waypoint_guidance(
        state.aircraft.position,
        FixedWaypointLeg {
            waypoint: destination,
            arrival_radius: NauticalMiles(0.01),
        },
    ) {
        Ok(guidance) => guidance,
        Err(WaypointError::LegComplete { .. }) => {
            state.command.great_circle_destination = Some(great_circle_destination(
                state.aircraft.position,
                state.aircraft.track_true,
                process.great_circle_leg_length_nm,
            )?);
            state.command.selected_control = state.aircraft.track_true;
            return Ok(true);
        }
        Err(error) => return Err(PoweredFlightError::GreatCircle(error.to_string())),
    };
    // Renew halfway down the explicitly declared geometric leg.  Rebuilding
    // the endpoint along the current geodesic tangent makes the arbitrary
    // finite construction distance irrelevant to a long continuation.
    if guidance.distance_remaining.0 <= 0.5 * process.great_circle_leg_length_nm {
        state.command.great_circle_destination = Some(great_circle_destination(
            state.aircraft.position,
            guidance.track_true,
            process.great_circle_leg_length_nm,
        )?);
        state.command.selected_control = guidance.track_true;
        return Ok(true);
    }
    Ok(false)
}

fn selected_control_for_ground_track(
    mode: PoweredLateralMode,
    ground_track_true: Degrees,
    heading_true: Degrees,
    declination: Degrees,
) -> Degrees {
    match mode {
        PoweredLateralMode::ConstantTrueHeading => heading_true,
        PoweredLateralMode::ConstantMagneticHeading => {
            Degrees(heading_true.0 - declination.0).wrapped_360()
        }
        PoweredLateralMode::ConstantTrueTrack
        | PoweredLateralMode::GreatCircleTrackContinuation => ground_track_true.wrapped_360(),
        PoweredLateralMode::ConstantMagneticTrack => {
            Degrees(ground_track_true.0 - declination.0).wrapped_360()
        }
    }
}

fn validate_coordinate(position: LatLon) -> bool {
    position.latitude.0.is_finite()
        && (-90.0..=90.0).contains(&position.latitude.0)
        && position.longitude.0.is_finite()
        && (-180.0..180.0).contains(&position.longitude.0)
}

fn validate_state_shape(state: PoweredFlightState) -> Result<(), PoweredFlightError> {
    let finite = state.aircraft.all_finite()
        && state.heading_true.0.is_finite()
        && state.mach.is_finite()
        && state.bank_angle.0.is_finite()
        && state.command.selected_control.0.is_finite()
        && state.command.target_mach.is_finite()
        && state.command.target_pressure_altitude.0.is_finite();
    let clocks_valid = [
        state.event_clocks.lateral,
        state.event_clocks.speed,
        state.event_clocks.altitude,
    ]
    .into_iter()
    .flatten()
    .all(|pending| {
        pending.not_before.0.is_finite()
            && pending.next_event.0.is_finite()
            && pending.next_event.0 >= pending.not_before.0
            && pending.next_event.0 >= state.aircraft.time.0 - TIME_TOLERANCE_S
    });
    let destination_valid = state
        .command
        .great_circle_destination
        .map(validate_coordinate)
        .unwrap_or(true);
    if !finite
        || !clocks_valid
        || !destination_valid
        || !validate_coordinate(state.aircraft.position)
        || !(0.0..360.0).contains(&state.aircraft.track_true.0)
        || !(0.0..360.0).contains(&state.heading_true.0)
        || !(0.0..360.0).contains(&state.command.selected_control.0)
        || state.aircraft.ground_speed.0 <= 0.0
        || state.mach <= 0.0
        || matches!(
            state.command.lateral_mode,
            PoweredLateralMode::GreatCircleTrackContinuation
        ) != state.command.great_circle_destination.is_some()
    {
        return Err(PoweredFlightError::InvalidState);
    }
    Ok(())
}

fn validate_state_limits(
    state: PoweredFlightState,
    limits: PoweredFlightLimits,
) -> Result<(), PoweredFlightError> {
    if state.aircraft.altitude.0 < limits.minimum_pressure_altitude_ft
        || state.aircraft.altitude.0 > limits.maximum_pressure_altitude_ft
        || state.command.target_pressure_altitude.0 < limits.minimum_pressure_altitude_ft
        || state.command.target_pressure_altitude.0 > limits.maximum_pressure_altitude_ft
        || state.command.target_mach <= 0.0
        || state.command.target_mach > limits.mmo
        || state.bank_angle.0.abs() > limits.maximum_bank_deg
        || state.aircraft.vertical_speed.0 > limits.maximum_climb_rate_ft_min
        || state.aircraft.vertical_speed.0 < -limits.maximum_descent_rate_ft_min
    {
        return Err(PoweredFlightError::InvalidState);
    }
    Ok(())
}

fn vmo_limit_mach(pressure_pa: f64, vmo_kcas: f64) -> f64 {
    let calibrated_mach_sea_level = vmo_kcas * KNOT_M_S / SEA_LEVEL_SOUND_SPEED_M_S;
    let impact_pressure_pa =
        SEA_LEVEL_PRESSURE_PA * ((1.0 + 0.2 * calibrated_mach_sea_level.powi(2)).powf(3.5) - 1.0);
    (5.0 * ((1.0 + impact_pressure_pa / pressure_pa).powf(2.0 / 7.0) - 1.0)).sqrt()
}

fn maximum_bank_for_lift_deg(
    limits: PoweredFlightLimits,
    weather: WeatherSample,
    pressure_altitude_ft: f64,
    gross_mass_kg: f64,
    mach: f64,
) -> f64 {
    let density = weather.dry_air_density_kg_m3(pressure_altitude_ft);
    let tas_m_s = mach * weather.speed_of_sound_knots() * KNOT_M_S;
    let dynamic_pressure_pa = 0.5 * density * tas_m_s.powi(2);
    // Retain the declared speed margin in turns: required lift may not consume
    // the CL headroom reserved by stall_speed_margin squared.
    let maximum_load = dynamic_pressure_pa * limits.wing_area_m2 * limits.maximum_lift_coefficient
        / (gross_mass_kg * STANDARD_GRAVITY_M_S2 * limits.stall_speed_margin.powi(2));
    if maximum_load <= 1.0 {
        0.0
    } else {
        (1.0 / maximum_load)
            .acos()
            .to_degrees()
            .min(limits.maximum_bank_deg)
    }
}

pub fn instantaneous_powered_limits(
    limits: PoweredFlightLimits,
    weather: WeatherSample,
    pressure_altitude_ft: f64,
    gross_mass_kg: f64,
    bank_angle: Degrees,
    mach: f64,
) -> Result<InstantaneousPoweredLimits, PoweredFlightError> {
    limits.validate()?;
    if !gross_mass_kg.is_finite()
        || gross_mass_kg <= 0.0
        || !pressure_altitude_ft.is_finite()
        || !bank_angle.0.is_finite()
        || !mach.is_finite()
        || bank_angle.0.abs() > limits.maximum_bank_deg + 1.0e-9
    {
        return Err(PoweredFlightError::InvalidState);
    }
    let density = weather.dry_air_density_kg_m3(pressure_altitude_ft);
    let load_factor = 1.0 / bank_angle.to_radians().cos();
    let stall_tas_m_s = (2.0 * gross_mass_kg * STANDARD_GRAVITY_M_S2 * load_factor
        / (density * limits.wing_area_m2 * limits.maximum_lift_coefficient))
        .sqrt()
        * limits.stall_speed_margin;
    let speed_of_sound_m_s = weather.speed_of_sound_knots() * KNOT_M_S;
    let stall_mach = stall_tas_m_s / speed_of_sound_m_s;
    let pressure_pa = crate::isa_pressure_pa(pressure_altitude_ft);
    let vmo_mach = vmo_limit_mach(pressure_pa, limits.vmo_kcas);
    let minimum_mach = limits.minimum_mach_floor.max(stall_mach);
    let maximum_mach = limits.mmo.min(vmo_mach);
    if !minimum_mach.is_finite() || !maximum_mach.is_finite() || minimum_mach >= maximum_mach {
        return Err(PoweredFlightError::EmptySpeedEnvelope);
    }
    let tas_m_s = mach.max(minimum_mach) * speed_of_sound_m_s;
    let dynamic_pressure_pa = 0.5 * density * tas_m_s.powi(2);
    let lift_coefficient = gross_mass_kg * STANDARD_GRAVITY_M_S2 * load_factor
        / (dynamic_pressure_pa * limits.wing_area_m2);
    let maximum_bank_for_lift_deg = maximum_bank_for_lift_deg(
        limits,
        weather,
        pressure_altitude_ft,
        gross_mass_kg,
        mach.max(minimum_mach),
    );
    let maximum_turn_rate_deg_s =
        (STANDARD_GRAVITY_M_S2 * maximum_bank_for_lift_deg.to_radians().tan() / tas_m_s)
            .to_degrees();
    Ok(InstantaneousPoweredLimits {
        minimum_mach,
        maximum_mach,
        stall_mach,
        vmo_mach,
        load_factor_g: load_factor,
        lift_coefficient,
        maximum_bank_for_lift_deg,
        maximum_turn_rate_deg_s,
    })
}

/// Initialize from an observed/sampled true ground track.  Heading-controlled
/// modes are resolved through local wind so every initial mode reproduces the
/// same ground-track prior rather than silently interpreting radar track as an
/// air heading.
#[allow(clippy::too_many_arguments)]
pub fn initialize_powered_flight(
    mut aircraft: AircraftState,
    initial_mach: f64,
    initial_mode: PoweredLateralMode,
    limits: PoweredFlightLimits,
    process: ManeuverProcess,
    environment: PoweredFlightEnvironment<'_>,
    gross_mass_kg: f64,
    rng: &mut ChaCha8Rng,
) -> Result<PoweredFlightState, PoweredFlightError> {
    limits.validate()?;
    process.validate(limits)?;
    if !aircraft.all_finite()
        || !validate_coordinate(aircraft.position)
        || !(0.0..360.0).contains(&aircraft.track_true.0)
        || !initial_mach.is_finite()
        || initial_mach <= 0.0
        || aircraft.altitude.0 < limits.minimum_pressure_altitude_ft
        || aircraft.altitude.0 > limits.maximum_pressure_altitude_ft
        || aircraft.vertical_speed.0 > limits.maximum_climb_rate_ft_min
        || aircraft.vertical_speed.0 < -limits.maximum_descent_rate_ft_min
    {
        return Err(PoweredFlightError::InvalidState);
    }
    let weather = weather_at(environment, aircraft)?;
    let instantaneous = instantaneous_powered_limits(
        limits,
        weather,
        aircraft.altitude.0,
        gross_mass_kg,
        Degrees(0.0),
        initial_mach,
    )?;
    if initial_mach < instantaneous.minimum_mach || initial_mach > instantaneous.maximum_mach {
        return Err(PoweredFlightError::InvalidState);
    }
    let declination = if matches!(
        initial_mode,
        PoweredLateralMode::ConstantMagneticHeading | PoweredLateralMode::ConstantMagneticTrack
    ) {
        magnetic_declination(environment, aircraft.altitude.0, aircraft.position)?
    } else {
        Degrees(0.0)
    };
    let track_solution = ground_velocity_from_control(
        Knots(initial_mach * weather.speed_of_sound_knots()),
        aircraft.track_true,
        LateralMode::ConstantTrueTrack,
        weather.wind_north,
        weather.wind_east,
        Degrees(0.0),
    )
    .map_err(|_| PoweredFlightError::InfeasibleGroundTrack)?;
    let selected_control = selected_control_for_ground_track(
        initial_mode,
        aircraft.track_true,
        track_solution.heading_true,
        declination,
    );
    let great_circle_destination = if matches!(
        initial_mode,
        PoweredLateralMode::GreatCircleTrackContinuation
    ) {
        Some(great_circle_destination(
            aircraft.position,
            aircraft.track_true,
            process.great_circle_leg_length_nm,
        )?)
    } else {
        None
    };
    aircraft.track_true = track_solution.track_true;
    aircraft.ground_speed = track_solution.speed;
    let state = PoweredFlightState {
        aircraft,
        heading_true: track_solution.heading_true,
        mach: initial_mach,
        bank_angle: Degrees(0.0),
        command: PoweredFlightCommand {
            lateral_mode: initial_mode,
            selected_control,
            great_circle_destination,
            target_mach: initial_mach,
            target_pressure_altitude: aircraft.altitude,
        },
        event_clocks: PoweredEventClocks {
            lateral: sample_clock(process.lateral_clock, aircraft.time.0, rng)?,
            speed: sample_clock(process.speed_clock, aircraft.time.0, rng)?,
            altitude: sample_clock(process.altitude_clock, aircraft.time.0, rng)?,
        },
        event_counters: PoweredEventCounters::default(),
    };
    validate_state_shape(state)?;
    Ok(state)
}

fn desired_heading_true(
    state: PoweredFlightState,
    weather: WeatherSample,
    environment: PoweredFlightEnvironment<'_>,
) -> Result<Degrees, PoweredFlightError> {
    let declination = match state.command.lateral_mode {
        PoweredLateralMode::ConstantMagneticHeading | PoweredLateralMode::ConstantMagneticTrack => {
            magnetic_declination(
                environment,
                state.aircraft.altitude.0,
                state.aircraft.position,
            )?
        }
        _ => Degrees(0.0),
    };
    match state.command.lateral_mode {
        PoweredLateralMode::ConstantTrueHeading => Ok(state.command.selected_control),
        PoweredLateralMode::ConstantMagneticHeading => {
            Ok(Degrees(state.command.selected_control.0 + declination.0).wrapped_360())
        }
        PoweredLateralMode::ConstantTrueTrack | PoweredLateralMode::ConstantMagneticTrack => {
            let mode = if matches!(
                state.command.lateral_mode,
                PoweredLateralMode::ConstantTrueTrack
            ) {
                LateralMode::ConstantTrueTrack
            } else {
                LateralMode::ConstantMagneticTrack
            };
            ground_velocity_from_control(
                Knots(state.mach * weather.speed_of_sound_knots()),
                state.command.selected_control,
                mode,
                weather.wind_north,
                weather.wind_east,
                declination,
            )
            .map(|velocity| velocity.heading_true)
            .map_err(|_| PoweredFlightError::InfeasibleGroundTrack)
        }
        PoweredLateralMode::GreatCircleTrackContinuation => {
            let destination = state
                .command
                .great_circle_destination
                .ok_or(PoweredFlightError::InvalidState)?;
            let guidance = fixed_waypoint_guidance(
                state.aircraft.position,
                FixedWaypointLeg {
                    waypoint: destination,
                    arrival_radius: NauticalMiles(0.01),
                },
            )
            .map_err(|error| PoweredFlightError::GreatCircle(error.to_string()))?;
            ground_velocity_from_control(
                Knots(state.mach * weather.speed_of_sound_knots()),
                guidance.track_true,
                LateralMode::ConstantTrueTrack,
                weather.wind_north,
                weather.wind_east,
                Degrees(0.0),
            )
            .map(|velocity| velocity.heading_true)
            .map_err(|_| PoweredFlightError::InfeasibleGroundTrack)
        }
    }
}

fn transition_active(
    state: PoweredFlightState,
    weather: WeatherSample,
    environment: PoweredFlightEnvironment<'_>,
    integration: PoweredIntegration,
) -> Result<bool, PoweredFlightError> {
    let desired = desired_heading_true(state, weather, environment)?;
    Ok(
        signed_angle_difference(desired.0, state.heading_true.0).abs()
            > integration.heading_capture_tolerance_deg
            || state.bank_angle.0.abs() > 1.0e-9
            || (state.command.target_mach - state.mach).abs() > 1.0e-12
            || (state.command.target_pressure_altitude.0 - state.aircraft.altitude.0).abs()
                > 1.0e-6
            || state.aircraft.vertical_speed.0.abs() > 1.0e-6,
    )
}

fn earliest_event_time(state: PoweredFlightState) -> Option<f64> {
    [
        state.event_clocks.lateral,
        state.event_clocks.speed,
        state.event_clocks.altitude,
    ]
    .into_iter()
    .flatten()
    .map(|pending| pending.next_event.0)
    .min_by(f64::total_cmp)
}

fn sample_lateral_event(
    state: &mut PoweredFlightState,
    process: ManeuverProcess,
    environment: PoweredFlightEnvironment<'_>,
    rng: &mut ChaCha8Rng,
) -> Result<(), PoweredFlightError> {
    let mode = sample_mode(process.lateral_mode_weights, rng)?;
    let base_true = match mode {
        PoweredLateralMode::ConstantTrueHeading | PoweredLateralMode::ConstantMagneticHeading => {
            state.heading_true
        }
        _ => state.aircraft.track_true,
    };
    let delta =
        rng.gen_range(-process.maximum_course_change_deg..=process.maximum_course_change_deg);
    let target_true = Degrees(base_true.0 + delta).wrapped_360();
    let declination = if matches!(
        mode,
        PoweredLateralMode::ConstantMagneticHeading | PoweredLateralMode::ConstantMagneticTrack
    ) {
        magnetic_declination(
            environment,
            state.aircraft.altitude.0,
            state.aircraft.position,
        )?
    } else {
        Degrees(0.0)
    };
    state.command.lateral_mode = mode;
    state.command.selected_control = if matches!(
        mode,
        PoweredLateralMode::ConstantMagneticHeading | PoweredLateralMode::ConstantMagneticTrack
    ) {
        Degrees(target_true.0 - declination.0).wrapped_360()
    } else {
        target_true
    };
    state.command.great_circle_destination =
        if matches!(mode, PoweredLateralMode::GreatCircleTrackContinuation) {
            Some(great_circle_destination(
                state.aircraft.position,
                target_true,
                process.great_circle_leg_length_nm,
            )?)
        } else {
            None
        };
    Ok(())
}

fn sample_event_mark(
    kind: PoweredEventKind,
    process: ManeuverProcess,
    rng: &mut ChaCha8Rng,
) -> Result<PoweredEventMark, PoweredFlightError> {
    Ok(match kind {
        PoweredEventKind::Lateral => PoweredEventMark::Lateral {
            mode: sample_mode(process.lateral_mode_weights, rng)?,
            course_change_deg: rng
                .gen_range(-process.maximum_course_change_deg..=process.maximum_course_change_deg),
        },
        PoweredEventKind::Speed => PoweredEventMark::Speed {
            target_mach: rng.gen_range(process.target_mach_min..=process.target_mach_max),
        },
        PoweredEventKind::Altitude => PoweredEventMark::Altitude {
            target_pressure_altitude_ft: rng
                .gen_range(process.target_altitude_min_ft..=process.target_altitude_max_ft),
        },
    })
}

fn apply_event_mark(
    state: &mut PoweredFlightState,
    mark: PoweredEventMark,
    process: ManeuverProcess,
    environment: PoweredFlightEnvironment<'_>,
) -> Result<(), PoweredFlightError> {
    match mark {
        PoweredEventMark::Lateral {
            mode,
            course_change_deg,
        } => {
            let base_true = match mode {
                PoweredLateralMode::ConstantTrueHeading
                | PoweredLateralMode::ConstantMagneticHeading => state.heading_true,
                _ => state.aircraft.track_true,
            };
            let target_true = Degrees(base_true.0 + course_change_deg).wrapped_360();
            let declination = if matches!(
                mode,
                PoweredLateralMode::ConstantMagneticHeading
                    | PoweredLateralMode::ConstantMagneticTrack
            ) {
                magnetic_declination(
                    environment,
                    state.aircraft.altitude.0,
                    state.aircraft.position,
                )?
            } else {
                Degrees(0.0)
            };
            state.command.lateral_mode = mode;
            state.command.selected_control = if matches!(
                mode,
                PoweredLateralMode::ConstantMagneticHeading
                    | PoweredLateralMode::ConstantMagneticTrack
            ) {
                Degrees(target_true.0 - declination.0).wrapped_360()
            } else {
                target_true
            };
            state.command.great_circle_destination =
                if matches!(mode, PoweredLateralMode::GreatCircleTrackContinuation) {
                    Some(great_circle_destination(
                        state.aircraft.position,
                        target_true,
                        process.great_circle_leg_length_nm,
                    )?)
                } else {
                    None
                };
        }
        PoweredEventMark::Speed { target_mach } => {
            state.command.target_mach = target_mach;
        }
        PoweredEventMark::Altitude {
            target_pressure_altitude_ft,
        } => {
            state.command.target_pressure_altitude = Feet(target_pressure_altitude_ft);
        }
    }
    Ok(())
}

fn event_is_due(state: PoweredFlightState, kind: PoweredEventKind) -> bool {
    state
        .event_clocks
        .pending(kind)
        .map(|pending| pending.next_event.0 <= state.aircraft.time.0 + TIME_TOLERANCE_S)
        .unwrap_or(false)
}

fn event_index(state: PoweredFlightState, kind: PoweredEventKind) -> u32 {
    match kind {
        PoweredEventKind::Lateral => state.event_counters.lateral,
        PoweredEventKind::Speed => state.event_counters.speed,
        PoweredEventKind::Altitude => state.event_counters.altitude,
    }
}

fn one_event_counter(kind: PoweredEventKind) -> PoweredEventCounters {
    match kind {
        PoweredEventKind::Lateral => PoweredEventCounters {
            lateral: 1,
            ..PoweredEventCounters::default()
        },
        PoweredEventKind::Speed => PoweredEventCounters {
            speed: 1,
            ..PoweredEventCounters::default()
        },
        PoweredEventKind::Altitude => PoweredEventCounters {
            altitude: 1,
            ..PoweredEventCounters::default()
        },
    }
}

fn renew_event_clock(
    state: &mut PoweredFlightState,
    kind: PoweredEventKind,
    process: ManeuverProcess,
    rng: &mut ChaCha8Rng,
) -> Result<(), PoweredFlightError> {
    let renewed = sample_clock(process.renewal_clock(kind), state.aircraft.time.0, rng)?;
    state.event_clocks.set_pending(kind, renewed);
    Ok(())
}

fn sample_prior_event_in_place(
    state: &mut PoweredFlightState,
    kind: PoweredEventKind,
    process: ManeuverProcess,
    environment: PoweredFlightEnvironment<'_>,
    rng: &mut ChaCha8Rng,
) -> Result<(), PoweredFlightError> {
    match kind {
        PoweredEventKind::Lateral => sample_lateral_event(state, process, environment, rng)?,
        PoweredEventKind::Speed => {
            state.command.target_mach =
                rng.gen_range(process.target_mach_min..=process.target_mach_max);
        }
        PoweredEventKind::Altitude => {
            state.command.target_pressure_altitude = Feet(
                rng.gen_range(process.target_altitude_min_ft..=process.target_altitude_max_ft),
            );
        }
    }
    renew_event_clock(state, kind, process, rng)
}

#[derive(Debug)]
struct EventMarkCandidate {
    after_mark: Result<PoweredFlightState, PoweredFlightError>,
    log_score: f64,
}

#[derive(Debug)]
struct CandidateSelection {
    probabilities: Vec<f64>,
    finite_score_count: usize,
    minimum_finite_log_score: Option<f64>,
    maximum_finite_log_score: Option<f64>,
    all_scores_negative_infinity: bool,
    effective_sample_size: f64,
    entropy_nats: f64,
}

fn candidate_selection(
    candidates: &[EventMarkCandidate],
    defensive_prior_probability: f64,
) -> CandidateSelection {
    let candidate_count = candidates.len();
    let finite_scores: Vec<f64> = candidates
        .iter()
        .map(|candidate| candidate.log_score)
        .filter(|score| score.is_finite())
        .collect();
    let finite_score_count = finite_scores.len();
    let minimum_finite_log_score = finite_scores.iter().copied().min_by(f64::total_cmp);
    let maximum_finite_log_score = finite_scores.iter().copied().max_by(f64::total_cmp);
    let all_scores_negative_infinity = finite_score_count == 0;

    let probabilities = if all_scores_negative_infinity {
        vec![1.0 / candidate_count as f64; candidate_count]
    } else {
        let maximum_score = maximum_finite_log_score.expect("a finite score exists");
        let exponentials: Vec<f64> = candidates
            .iter()
            .map(|candidate| {
                if candidate.log_score.is_finite() {
                    (candidate.log_score - maximum_score).exp()
                } else {
                    0.0
                }
            })
            .collect();
        let exponential_sum = exponentials.iter().sum::<f64>();
        let uniform_probability = defensive_prior_probability / candidate_count as f64;
        let guided_probability = 1.0 - defensive_prior_probability;
        let mut probabilities: Vec<f64> = exponentials
            .into_iter()
            .map(|weight| uniform_probability + guided_probability * weight / exponential_sum)
            .collect();
        let total = probabilities.iter().sum::<f64>();
        for probability in &mut probabilities {
            *probability /= total;
        }
        probabilities
    };
    let effective_sample_size = 1.0
        / probabilities
            .iter()
            .map(|probability| probability * probability)
            .sum::<f64>();
    let entropy_nats = -probabilities
        .iter()
        .map(|probability| probability * probability.ln())
        .sum::<f64>();
    CandidateSelection {
        probabilities,
        finite_score_count,
        minimum_finite_log_score,
        maximum_finite_log_score,
        all_scores_negative_infinity,
        effective_sample_size,
        entropy_nats,
    }
}

fn select_candidate(probabilities: &[f64], rng: &mut ChaCha8Rng) -> usize {
    let draw = rng.gen::<f64>();
    let mut cumulative = 0.0;
    for (index, probability) in probabilities.iter().enumerate() {
        cumulative += probability;
        if draw < cumulative {
            return index;
        }
    }
    probabilities.len() - 1
}

#[derive(Debug, Default)]
struct ProposedEventApplication {
    applied: PoweredEventCounters,
    proposed: PoweredEventCounters,
    log_prior_over_proposal: f64,
    diagnostics: Vec<PoweredEventProposalDiagnostic>,
}

#[allow(clippy::too_many_arguments)]
fn propose_due_event<G: PoweredEventCandidateScorer>(
    state: &mut PoweredFlightState,
    kind: PoweredEventKind,
    process: ManeuverProcess,
    environment: PoweredFlightEnvironment<'_>,
    config: PoweredEventProposalConfig,
    proposal_rng: PoweredEventProposalRng,
    scorer: &G,
) -> Result<PoweredEventProposalDiagnostic, PoweredEventProposalError<G::Error>> {
    let event_index = event_index(*state, kind);
    let event = PoweredEventProposalEvent {
        kind,
        event_number: u64::from(event_index) + 1,
        before: *state,
    };
    let mut candidates = Vec::with_capacity(config.candidates_per_event);
    let mut materialization_failures = 0;
    for candidate_index in 0..config.candidates_per_event {
        let mut candidate_rng = proposal_rng.event_rng(
            kind,
            event_index,
            EventProposalRngPurpose::CandidateMark,
            candidate_index,
        );
        let mark = sample_event_mark(kind, process, &mut candidate_rng)?;
        let mut after_mark = *state;
        let after_mark =
            apply_event_mark(&mut after_mark, mark, process, environment).map(|()| after_mark);
        let log_score = match &after_mark {
            Ok(after_mark) => {
                let candidate = PoweredEventProposalCandidate {
                    event,
                    candidate_index,
                    mark,
                    after_mark: *after_mark,
                };
                let score = scorer
                    .log_score(&candidate)
                    .map_err(PoweredEventProposalError::Scorer)?;
                if score.is_nan() || score == f64::INFINITY {
                    return Err(PoweredEventProposalError::InvalidScore {
                        kind,
                        event_number: event.event_number,
                        candidate_index,
                    });
                }
                score
            }
            Err(_) => {
                materialization_failures += 1;
                f64::NEG_INFINITY
            }
        };
        candidates.push(EventMarkCandidate {
            after_mark,
            log_score,
        });
    }

    let selection = candidate_selection(&candidates, config.defensive_prior_probability);
    let mut selection_rng =
        proposal_rng.event_rng(kind, event_index, EventProposalRngPurpose::Selection, 0);
    let selected_candidate_index = if selection.all_scores_negative_infinity {
        selection_rng.gen_range(0..config.candidates_per_event)
    } else {
        select_candidate(&selection.probabilities, &mut selection_rng)
    };
    let selected_probability = selection.probabilities[selected_candidate_index];
    let log_candidate_count = (config.candidates_per_event as f64).ln();
    let selected_log_probability = if selection.all_scores_negative_infinity {
        -log_candidate_count
    } else {
        selected_probability.ln()
    };
    let log_prior_over_proposal = -log_candidate_count - selected_log_probability;
    let diagnostic = PoweredEventProposalDiagnostic {
        event_time: state.aircraft.time,
        kind,
        event_number: event.event_number,
        candidate_count: config.candidates_per_event,
        selected_candidate_index,
        selected_log_probability,
        log_prior_over_proposal,
        finite_score_count: selection.finite_score_count,
        minimum_finite_log_score: selection.minimum_finite_log_score,
        maximum_finite_log_score: selection.maximum_finite_log_score,
        all_scores_negative_infinity: selection.all_scores_negative_infinity,
        selection_effective_sample_size: selection.effective_sample_size,
        selection_entropy_nats: selection.entropy_nats,
        materialization_failures,
    };

    let selected = &candidates[selected_candidate_index];
    *state = selected.after_mark.clone().map_err(|source| {
        PoweredEventProposalError::SelectedCandidate {
            diagnostic: Box::new(diagnostic.clone()),
            source,
        }
    })?;
    let mut renewal_rng =
        proposal_rng.event_rng(kind, event_index, EventProposalRngPurpose::RenewalClock, 0);
    renew_event_clock(state, kind, process, &mut renewal_rng)?;
    Ok(diagnostic)
}

#[allow(clippy::too_many_arguments)]
fn apply_due_events_with_proposal<G: PoweredEventCandidateScorer>(
    state: &mut PoweredFlightState,
    process: ManeuverProcess,
    environment: PoweredFlightEnvironment<'_>,
    config: PoweredEventProposalConfig,
    proposal_rng: PoweredEventProposalRng,
    scorer: &G,
    legacy_rng: &mut ChaCha8Rng,
) -> Result<ProposedEventApplication, PoweredEventProposalError<G::Error>> {
    let mut result = ProposedEventApplication::default();
    for kind in [
        PoweredEventKind::Lateral,
        PoweredEventKind::Speed,
        PoweredEventKind::Altitude,
    ] {
        if !event_is_due(*state, kind) {
            continue;
        }
        let index = event_index(*state, kind);
        let event = PoweredEventProposalEvent {
            kind,
            event_number: u64::from(index) + 1,
            before: *state,
        };
        if scorer
            .is_eligible(&event)
            .map_err(PoweredEventProposalError::Scorer)?
        {
            let diagnostic = propose_due_event(
                state,
                kind,
                process,
                environment,
                config,
                proposal_rng,
                scorer,
            )?;
            result.proposed.checked_add(one_event_counter(kind))?;
            result.log_prior_over_proposal += diagnostic.log_prior_over_proposal;
            result.diagnostics.push(diagnostic);
        } else {
            sample_prior_event_in_place(state, kind, process, environment, legacy_rng)?;
        }
        result.applied.checked_add(one_event_counter(kind))?;
    }
    state.event_counters.checked_add(result.applied)?;
    Ok(result)
}

fn apply_due_events(
    state: &mut PoweredFlightState,
    process: ManeuverProcess,
    environment: PoweredFlightEnvironment<'_>,
    rng: &mut ChaCha8Rng,
) -> Result<PoweredEventCounters, PoweredFlightError> {
    let time_s = state.aircraft.time.0;
    let mut applied = PoweredEventCounters::default();
    if state
        .event_clocks
        .lateral
        .map(|pending| pending.next_event.0 <= time_s + TIME_TOLERANCE_S)
        .unwrap_or(false)
    {
        sample_lateral_event(state, process, environment, rng)?;
        state.event_clocks.lateral = sample_clock(process.lateral_clock, time_s, rng)?;
        applied.lateral = 1;
    }
    if state
        .event_clocks
        .speed
        .map(|pending| pending.next_event.0 <= time_s + TIME_TOLERANCE_S)
        .unwrap_or(false)
    {
        state.command.target_mach =
            rng.gen_range(process.target_mach_min..=process.target_mach_max);
        state.event_clocks.speed = sample_clock(process.speed_clock, time_s, rng)?;
        applied.speed = 1;
    }
    if state
        .event_clocks
        .altitude
        .map(|pending| pending.next_event.0 <= time_s + TIME_TOLERANCE_S)
        .unwrap_or(false)
    {
        state.command.target_pressure_altitude =
            Feet(rng.gen_range(process.target_altitude_min_ft..=process.target_altitude_max_ft));
        state.event_clocks.altitude = sample_clock(process.altitude_clock, time_s, rng)?;
        applied.altitude = 1;
    }
    state.event_counters.checked_add(applied)?;
    Ok(applied)
}

fn integrate_segment(
    start: PoweredFlightState,
    duration_s: f64,
    limits: PoweredFlightLimits,
    integration: PoweredIntegration,
    environment: PoweredFlightEnvironment<'_>,
    gross_mass_kg: f64,
    regime: PoweredStepRegime,
) -> Result<PoweredFlightSegment, PoweredFlightError> {
    let weather_start = weather_at(environment, start.aircraft)?;
    let start_limits = instantaneous_powered_limits(
        limits,
        weather_start,
        start.aircraft.altitude.0,
        gross_mass_kg,
        start.bank_angle,
        start.mach,
    )?;
    if start.mach < start_limits.minimum_mach - 1.0e-9
        || start.mach > start_limits.maximum_mach + 1.0e-9
        || start.aircraft.altitude.0 < limits.minimum_pressure_altitude_ft - 1.0e-9
        || start.aircraft.altitude.0 > limits.maximum_pressure_altitude_ft + 1.0e-9
        || start.aircraft.vertical_speed.0 > limits.maximum_climb_rate_ft_min + 1.0e-9
        || start.aircraft.vertical_speed.0 < -limits.maximum_descent_rate_ft_min - 1.0e-9
    {
        return Err(PoweredFlightError::InvalidState);
    }

    let desired_heading = desired_heading_true(start, weather_start, environment)?;
    let heading_error = signed_angle_difference(desired_heading.0, start.heading_true.0);
    let maximum_turn_rate = start_limits.maximum_turn_rate_deg_s;
    let desired_turn_rate = if heading_error.abs() <= integration.heading_capture_tolerance_deg {
        0.0
    } else {
        (heading_error / limits.heading_capture_time_s).clamp(-maximum_turn_rate, maximum_turn_rate)
    };
    let tas_m_s = start.mach * weather_start.speed_of_sound_knots() * KNOT_M_S;
    let desired_bank_deg = (desired_turn_rate.to_radians() * tas_m_s / STANDARD_GRAVITY_M_S2)
        .atan()
        .to_degrees()
        .clamp(
            -start_limits.maximum_bank_for_lift_deg,
            start_limits.maximum_bank_for_lift_deg,
        );
    let maximum_roll = limits.maximum_roll_rate_deg_s * duration_s;
    let midpoint_bank = move_toward(start.bank_angle.0, desired_bank_deg, maximum_roll * 0.5);
    let end_bank = move_toward(start.bank_angle.0, desired_bank_deg, maximum_roll);

    let altitude_error = start.command.target_pressure_altitude.0 - start.aircraft.altitude.0;
    let desired_vertical_speed = (altitude_error * 60.0 / limits.altitude_capture_time_s).clamp(
        -limits.maximum_descent_rate_ft_min,
        limits.maximum_climb_rate_ft_min,
    );
    let maximum_vertical_change = limits.maximum_vertical_acceleration_ft_min_s * duration_s;
    let midpoint_vertical_speed = move_toward(
        start.aircraft.vertical_speed.0,
        desired_vertical_speed,
        maximum_vertical_change * 0.5,
    );
    let mut end_vertical_speed = move_toward(
        start.aircraft.vertical_speed.0,
        desired_vertical_speed,
        maximum_vertical_change,
    );
    let mut end_altitude = start.aircraft.altitude.0 + midpoint_vertical_speed * duration_s / 60.0;
    if altitude_error.signum() != (start.command.target_pressure_altitude.0 - end_altitude).signum()
        || altitude_error == 0.0
    {
        end_altitude = start.command.target_pressure_altitude.0;
        end_vertical_speed = 0.0;
    }
    end_altitude = end_altitude.clamp(
        limits.minimum_pressure_altitude_ft,
        limits.maximum_pressure_altitude_ft,
    );
    if end_altitude <= limits.minimum_pressure_altitude_ft + 1.0e-9
        || end_altitude >= limits.maximum_pressure_altitude_ft - 1.0e-9
    {
        end_vertical_speed = 0.0;
    }
    let midpoint_altitude = 0.5 * (start.aircraft.altitude.0 + end_altitude);
    let midpoint_time = start.aircraft.time.0 + 0.5 * duration_s;
    let midpoint_template = AircraftState {
        time: Seconds(midpoint_time),
        position: start.aircraft.position,
        altitude: Feet(midpoint_altitude),
        track_true: start.aircraft.track_true,
        ground_speed: start.aircraft.ground_speed,
        vertical_speed: FeetPerMinute(midpoint_vertical_speed),
        bfo_bias: start.aircraft.bfo_bias,
    };
    let mut midpoint_weather = weather_at(environment, midpoint_template)?;
    let half_mach_change = limits.maximum_mach_rate_per_s * duration_s * 0.5;
    let bank_integral_half = integrated_tangent_bank_seconds(
        start.bank_angle.0,
        desired_bank_deg,
        limits.maximum_roll_rate_deg_s,
        duration_s * 0.5,
    );
    let bank_integral_total = integrated_tangent_bank_seconds(
        start.bank_angle.0,
        desired_bank_deg,
        limits.maximum_roll_rate_deg_s,
        duration_s,
    );
    let mut midpoint_mach = start.mach;
    let mut midpoint_heading = start.heading_true;
    let mut end_heading = start.heading_true;
    // A few fixed-point iterations make the constraint use ERA5 at the actual
    // midpoint reached with the constrained Mach, rather than at the start.
    for _ in 0..4 {
        let previous_mach = midpoint_mach;
        let previous_weather = midpoint_weather;
        let midpoint_limits = instantaneous_powered_limits(
            limits,
            midpoint_weather,
            midpoint_altitude,
            gross_mass_kg,
            Degrees(midpoint_bank),
            midpoint_mach,
        )?;
        midpoint_mach = rate_reachable_mach(
            start.mach,
            start.command.target_mach,
            half_mach_change,
            midpoint_limits,
            midpoint_time,
        )?;
        let turn_scale_deg = (STANDARD_GRAVITY_M_S2
            / (midpoint_mach * midpoint_weather.speed_of_sound_knots() * KNOT_M_S))
            .to_degrees();
        midpoint_heading =
            Degrees(start.heading_true.0 + turn_scale_deg * bank_integral_half).wrapped_360();
        end_heading =
            Degrees(start.heading_true.0 + turn_scale_deg * bank_integral_total).wrapped_360();
        let velocity = ground_velocity_from_control(
            Knots(midpoint_mach * midpoint_weather.speed_of_sound_knots()),
            midpoint_heading,
            LateralMode::ConstantTrueHeading,
            midpoint_weather.wind_north,
            midpoint_weather.wind_east,
            Degrees(0.0),
        )
        .map_err(|_| PoweredFlightError::InfeasibleGroundTrack)?;
        let midpoint_position = destination_wgs84(
            start.aircraft.position,
            velocity.track_true,
            NauticalMiles(velocity.speed.0 * duration_s / 7_200.0),
        )
        .map_err(|error| PoweredFlightError::Geodesy(error.to_string()))?;
        let updated_weather = weather_at(
            environment,
            AircraftState {
                position: midpoint_position,
                ..midpoint_template
            },
        )?;
        let converged = (midpoint_mach - previous_mach).abs() <= 1.0e-12
            && (updated_weather.temperature_k - previous_weather.temperature_k).abs() <= 1.0e-10
            && (updated_weather.wind_east.0 - previous_weather.wind_east.0).abs() <= 1.0e-10
            && (updated_weather.wind_north.0 - previous_weather.wind_north.0).abs() <= 1.0e-10;
        midpoint_weather = updated_weather;
        if converged {
            break;
        }
    }
    let midpoint_limits = instantaneous_powered_limits(
        limits,
        midpoint_weather,
        midpoint_altitude,
        gross_mass_kg,
        Degrees(midpoint_bank),
        midpoint_mach,
    )?;
    let verified_midpoint_mach = rate_reachable_mach(
        start.mach,
        start.command.target_mach,
        half_mach_change,
        midpoint_limits,
        midpoint_time,
    )?;
    if (verified_midpoint_mach - midpoint_mach).abs() > 1.0e-9 {
        return Err(PoweredFlightError::MachRateEnvelopeConflict {
            time_s: midpoint_time,
            envelope_min: midpoint_limits.minimum_mach,
            envelope_max: midpoint_limits.maximum_mach,
            reachable_min: start.mach - half_mach_change,
            reachable_max: start.mach + half_mach_change,
        });
    }
    let midpoint_velocity = ground_velocity_from_control(
        Knots(midpoint_mach * midpoint_weather.speed_of_sound_knots()),
        midpoint_heading,
        LateralMode::ConstantTrueHeading,
        midpoint_weather.wind_north,
        midpoint_weather.wind_east,
        Degrees(0.0),
    )
    .map_err(|_| PoweredFlightError::InfeasibleGroundTrack)?;
    let end_position = destination_wgs84(
        start.aircraft.position,
        midpoint_velocity.track_true,
        NauticalMiles(midpoint_velocity.speed.0 * duration_s / 3_600.0),
    )
    .map_err(|error| PoweredFlightError::Geodesy(error.to_string()))?;
    let mut end_aircraft = AircraftState {
        time: Seconds(start.aircraft.time.0 + duration_s),
        position: end_position,
        altitude: Feet(end_altitude),
        track_true: midpoint_velocity.track_true,
        ground_speed: midpoint_velocity.speed,
        vertical_speed: FeetPerMinute(end_vertical_speed),
        bfo_bias: start.aircraft.bfo_bias,
    };
    let end_weather = weather_at(environment, end_aircraft)?;
    let end_limits = instantaneous_powered_limits(
        limits,
        end_weather,
        end_altitude,
        gross_mass_kg,
        Degrees(end_bank),
        midpoint_mach,
    )?;
    let end_mach = rate_reachable_mach(
        midpoint_mach,
        start.command.target_mach,
        half_mach_change,
        end_limits,
        end_aircraft.time.0,
    )?;
    let end_velocity = ground_velocity_from_control(
        Knots(end_mach * end_weather.speed_of_sound_knots()),
        end_heading,
        LateralMode::ConstantTrueHeading,
        end_weather.wind_north,
        end_weather.wind_east,
        Degrees(0.0),
    )
    .map_err(|_| PoweredFlightError::InfeasibleGroundTrack)?;
    end_aircraft.track_true = end_velocity.track_true;
    end_aircraft.ground_speed = end_velocity.speed;

    let active_limits = PoweredLimitActivity {
        stall_or_minimum_mach_floor: start.command.target_mach
            <= midpoint_limits.minimum_mach + 1.0e-12,
        vmo_or_mmo_ceiling: start.command.target_mach >= midpoint_limits.maximum_mach - 1.0e-12,
        bank: desired_bank_deg.abs() >= start_limits.maximum_bank_for_lift_deg - 1.0e-9,
        roll_rate: (end_bank - desired_bank_deg).abs() > 1.0e-9,
        climb_rate: desired_vertical_speed >= limits.maximum_climb_rate_ft_min - 1.0e-9,
        descent_rate: desired_vertical_speed <= -limits.maximum_descent_rate_ft_min + 1.0e-9,
        vertical_acceleration: (end_vertical_speed - desired_vertical_speed).abs() > 1.0e-9,
        lower_altitude: end_altitude <= limits.minimum_pressure_altitude_ft + 1.0e-9,
        upper_altitude: end_altitude >= limits.maximum_pressure_altitude_ft - 1.0e-9,
    };
    let end = PoweredFlightState {
        aircraft: end_aircraft,
        heading_true: end_heading,
        mach: end_mach,
        bank_angle: Degrees(end_bank),
        ..start
    };
    Ok(PoweredFlightSegment {
        start,
        end,
        duration: Seconds(duration_s),
        start_weather: weather_start,
        midpoint_pressure_altitude: Feet(midpoint_altitude),
        midpoint_mach,
        midpoint_bank_angle: Degrees(midpoint_bank),
        midpoint_vertical_speed: FeetPerMinute(midpoint_vertical_speed),
        midpoint_weather,
        end_weather,
        midpoint_limits,
        regime,
        active_limits,
        magnetic_altitude_clamped: magnetic_altitude_is_clamped(
            start.command.lateral_mode,
            midpoint_altitude,
            environment,
        ),
        great_circle_leg_renewed_at_start: false,
        events_at_start: PoweredEventCounters::default(),
        events_at_end: PoweredEventCounters::default(),
    })
}

fn accumulate_diagnostics(
    diagnostics: &mut PoweredFlightDiagnostics,
    segment: &PoweredFlightSegment,
    event_aligned: bool,
) {
    diagnostics.integration_steps += 1;
    match segment.regime {
        PoweredStepRegime::Steady => diagnostics.steady_steps += 1,
        PoweredStepRegime::Transition => diagnostics.transition_steps += 1,
    }
    diagnostics.event_aligned_steps += u64::from(event_aligned);
    diagnostics.target_clamp_count += u64::from(
        segment.active_limits.stall_or_minimum_mach_floor
            || segment.active_limits.vmo_or_mmo_ceiling,
    );
    diagnostics.great_circle_leg_renewals += u64::from(segment.great_circle_leg_renewed_at_start);
    let duration = segment.duration.0;
    let active = segment.active_limits;
    let boundary = &mut diagnostics.boundary_seconds;
    boundary.stall_or_minimum_mach_floor +=
        duration * f64::from(active.stall_or_minimum_mach_floor);
    boundary.vmo_or_mmo_ceiling += duration * f64::from(active.vmo_or_mmo_ceiling);
    boundary.bank += duration * f64::from(active.bank);
    boundary.roll_rate += duration * f64::from(active.roll_rate);
    boundary.climb_rate += duration * f64::from(active.climb_rate);
    boundary.descent_rate += duration * f64::from(active.descent_rate);
    boundary.vertical_acceleration += duration * f64::from(active.vertical_acceleration);
    boundary.lower_altitude += duration * f64::from(active.lower_altitude);
    boundary.upper_altitude += duration * f64::from(active.upper_altitude);
    boundary.magnetic_altitude_clamp += duration * f64::from(segment.magnetic_altitude_clamped);
}

/// Advance by one adaptive, event-aligned integration segment.  This primitive
/// lets a caller update path-dependent fuel/mass between segments.  Events at
/// the returned endpoint have already changed the returned command state.
#[allow(clippy::too_many_arguments)]
pub fn advance_powered_flight_step(
    state: PoweredFlightState,
    target_time_s: f64,
    limits: PoweredFlightLimits,
    process: ManeuverProcess,
    integration: PoweredIntegration,
    environment: PoweredFlightEnvironment<'_>,
    gross_mass_kg: f64,
    rng: &mut ChaCha8Rng,
) -> Result<Option<PoweredFlightSegment>, PoweredFlightError> {
    let mut event_budget = PoweredEventBudget::new(integration.maximum_events_per_transition)?;
    advance_powered_flight_step_with_budget(
        state,
        target_time_s,
        limits,
        process,
        integration,
        environment,
        gross_mass_kg,
        &mut event_budget,
        rng,
    )
}

/// Manual-step variant with a caller-retained event budget.  Reusing `budget`
/// across every segment makes the same transition-wide cap enforced by the
/// convenience propagator, including events already due on entry.
#[allow(clippy::too_many_arguments)]
pub fn advance_powered_flight_step_with_budget(
    mut state: PoweredFlightState,
    target_time_s: f64,
    limits: PoweredFlightLimits,
    process: ManeuverProcess,
    integration: PoweredIntegration,
    environment: PoweredFlightEnvironment<'_>,
    gross_mass_kg: f64,
    event_budget: &mut PoweredEventBudget,
    rng: &mut ChaCha8Rng,
) -> Result<Option<PoweredFlightSegment>, PoweredFlightError> {
    limits.validate()?;
    process.validate(limits)?;
    integration.validate()?;
    if event_budget.maximum_events > integration.maximum_events_per_transition {
        return Err(PoweredFlightError::InvalidIntegration);
    }
    validate_state_shape(state)?;
    validate_state_limits(state, limits)?;
    if !target_time_s.is_finite() || target_time_s < state.aircraft.time.0 - TIME_TOLERANCE_S {
        return Err(PoweredFlightError::InvalidTargetTime);
    }
    let events_before = apply_due_events(&mut state, process, environment, rng)?;
    event_budget.record(events_before)?;
    let great_circle_leg_renewed_at_start = renew_great_circle_leg_if_needed(&mut state, process)?;
    if target_time_s <= state.aircraft.time.0 + TIME_TOLERANCE_S {
        return Ok(None);
    }
    let weather = weather_at(environment, state.aircraft)?;
    let regime = if transition_active(state, weather, environment, integration)? {
        PoweredStepRegime::Transition
    } else {
        PoweredStepRegime::Steady
    };
    let nominal_step = match regime {
        PoweredStepRegime::Steady => integration.steady_step_s,
        PoweredStepRegime::Transition => integration.transition_step_s,
    };
    let event_time = earliest_event_time(state).unwrap_or(f64::INFINITY);
    let end_time = target_time_s
        .min(state.aircraft.time.0 + nominal_step)
        .min(event_time);
    let duration_s = end_time - state.aircraft.time.0;
    if duration_s <= 0.0 || !duration_s.is_finite() {
        return Err(PoweredFlightError::InvalidIntegration);
    }
    let mut segment = integrate_segment(
        state,
        duration_s,
        limits,
        integration,
        environment,
        gross_mass_kg,
        regime,
    )?;
    let events_at_end = apply_due_events(&mut segment.end, process, environment, rng)?;
    event_budget.record(events_at_end)?;
    segment.events_at_start = events_before;
    segment.events_at_end = events_at_end;
    segment.great_circle_leg_renewed_at_start = great_circle_leg_renewed_at_start;
    Ok(Some(segment))
}

/// Manual-step variant with an exact finite prior-candidate proposal for
/// eligible event marks.
///
/// For each eligible event this draws `K` marks independently from the
/// declared prior, obtains caller-supplied relative log scores, and selects
/// index `J` with
///
/// `q_j = epsilon / K + (1 - epsilon) * softmax(score)_j`.
///
/// The returned incremental correction is `-ln(K) - ln(q_J)`.  This is an
/// exact auxiliary-variable correction because, for any test function `f`,
/// `E[sum_j q_j * f(mark_j) / (K*q_j)] = E_prior[f(mark)]`.  When every score
/// is negative infinity the selection is exactly uniform and the correction
/// is zero.  The one renewed clock is drawn independently from its unchanged
/// prior only after selection, so no clock density enters the correction.
///
/// `proposal_rng` must be constructed once for the complete physical
/// observation transition and reused across all calls, including bridge
/// splits.  The scorer's physical prediction horizon must likewise remain
/// fixed; `target_time_s` is only this numerical propagation boundary.  The
/// legacy API above is unchanged and consumes no proposal randomness.
///
/// A caller that provisionally advances to locate a fuel or event boundary
/// must restore its legacy RNG and event budget and discard the provisional
/// correction/diagnostics before replaying.  It must reuse the same stateless
/// `proposal_rng`, which then regenerates the identical keyed marks, selection,
/// and renewal clock.
#[allow(clippy::too_many_arguments)]
pub fn advance_powered_flight_step_with_budget_and_event_proposal<G>(
    mut state: PoweredFlightState,
    target_time_s: f64,
    limits: PoweredFlightLimits,
    process: ManeuverProcess,
    integration: PoweredIntegration,
    environment: PoweredFlightEnvironment<'_>,
    gross_mass_kg: f64,
    event_budget: &mut PoweredEventBudget,
    config: PoweredEventProposalConfig,
    legacy_rng: &mut ChaCha8Rng,
    proposal_rng: &PoweredEventProposalRng,
    scorer: &G,
) -> Result<Option<ProposedPoweredFlightSegment>, PoweredEventProposalError<G::Error>>
where
    G: PoweredEventCandidateScorer,
{
    config.validate()?;
    limits.validate()?;
    process.validate(limits)?;
    integration.validate()?;
    if event_budget.maximum_events > integration.maximum_events_per_transition {
        return Err(PoweredFlightError::InvalidIntegration.into());
    }
    validate_state_shape(state)?;
    validate_state_limits(state, limits)?;
    if !target_time_s.is_finite() || target_time_s < state.aircraft.time.0 - TIME_TOLERANCE_S {
        return Err(PoweredFlightError::InvalidTargetTime.into());
    }
    let events_before = apply_due_events_with_proposal(
        &mut state,
        process,
        environment,
        config,
        *proposal_rng,
        scorer,
        legacy_rng,
    )?;
    event_budget.record(events_before.applied)?;
    let great_circle_leg_renewed_at_start = renew_great_circle_leg_if_needed(&mut state, process)?;
    if target_time_s <= state.aircraft.time.0 + TIME_TOLERANCE_S {
        return Ok(None);
    }
    let weather = weather_at(environment, state.aircraft)?;
    let regime = if transition_active(state, weather, environment, integration)? {
        PoweredStepRegime::Transition
    } else {
        PoweredStepRegime::Steady
    };
    let nominal_step = match regime {
        PoweredStepRegime::Steady => integration.steady_step_s,
        PoweredStepRegime::Transition => integration.transition_step_s,
    };
    let event_time = earliest_event_time(state).unwrap_or(f64::INFINITY);
    let end_time = target_time_s
        .min(state.aircraft.time.0 + nominal_step)
        .min(event_time);
    let duration_s = end_time - state.aircraft.time.0;
    if duration_s <= 0.0 || !duration_s.is_finite() {
        return Err(PoweredFlightError::InvalidIntegration.into());
    }
    let mut segment = integrate_segment(
        state,
        duration_s,
        limits,
        integration,
        environment,
        gross_mass_kg,
        regime,
    )?;
    let events_at_end = apply_due_events_with_proposal(
        &mut segment.end,
        process,
        environment,
        config,
        *proposal_rng,
        scorer,
        legacy_rng,
    )?;
    event_budget.record(events_at_end.applied)?;
    segment.events_at_start = events_before.applied;
    segment.events_at_end = events_at_end.applied;
    segment.great_circle_leg_renewed_at_start = great_circle_leg_renewed_at_start;

    let mut proposed_events = events_before.proposed;
    proposed_events.checked_add(events_at_end.proposed)?;
    let mut event_proposals = events_before.diagnostics;
    event_proposals.extend(events_at_end.diagnostics);
    Ok(Some(ProposedPoweredFlightSegment {
        segment,
        log_prior_over_proposal: events_before.log_prior_over_proposal
            + events_at_end.log_prior_over_proposal,
        proposed_events,
        event_proposals,
    }))
}

/// Propagate over an arbitrary elapsed interval while exposing each accepted
/// event-aligned segment to a caller-owned observer (for example fuel state).
#[allow(clippy::too_many_arguments)]
pub fn propagate_powered_flight_with_observer<E, F>(
    mut state: PoweredFlightState,
    target_time_s: f64,
    limits: PoweredFlightLimits,
    process: ManeuverProcess,
    integration: PoweredIntegration,
    environment: PoweredFlightEnvironment<'_>,
    gross_mass_kg: f64,
    rng: &mut ChaCha8Rng,
    mut observer: F,
) -> Result<PoweredFlightTransition, ObservedPoweredFlightError<E>>
where
    E: Error + 'static,
    F: FnMut(&PoweredFlightSegment) -> Result<(), E>,
{
    // This convenience wrapper holds gross mass fixed.  Coupled fuel inference
    // must instead loop over `advance_powered_flight_step`, update its separate
    // fuel state, and pass the new gross mass into the following step.
    let mut diagnostics = PoweredFlightDiagnostics::default();
    let mut event_budget = PoweredEventBudget::new(integration.maximum_events_per_transition)?;
    while state.aircraft.time.0 < target_time_s - TIME_TOLERANCE_S {
        let event_time = earliest_event_time(state);
        let segment = advance_powered_flight_step_with_budget(
            state,
            target_time_s,
            limits,
            process,
            integration,
            environment,
            gross_mass_kg,
            &mut event_budget,
            rng,
        )?
        .ok_or(PoweredFlightError::InvalidIntegration)?;
        let event_aligned = segment.events_at_start.total() > 0
            || event_time
                .map(|time| (segment.end.aircraft.time.0 - time).abs() <= TIME_TOLERANCE_S)
                .unwrap_or(false);
        diagnostics.events.checked_add(segment.events_at_start)?;
        diagnostics.events.checked_add(segment.events_at_end)?;
        accumulate_diagnostics(&mut diagnostics, &segment, event_aligned);
        observer(&segment).map_err(ObservedPoweredFlightError::Observer)?;
        state = segment.end;
    }
    // Apply a control change exactly coincident with the requested endpoint.
    let terminal_events = apply_due_events(&mut state, process, environment, rng)?;
    event_budget.record(terminal_events)?;
    diagnostics.events.checked_add(terminal_events)?;
    validate_state_shape(state)?;
    Ok(PoweredFlightTransition { state, diagnostics })
}

#[allow(clippy::too_many_arguments)]
pub fn propagate_powered_flight(
    state: PoweredFlightState,
    target_time_s: f64,
    limits: PoweredFlightLimits,
    process: ManeuverProcess,
    integration: PoweredIntegration,
    environment: PoweredFlightEnvironment<'_>,
    gross_mass_kg: f64,
    rng: &mut ChaCha8Rng,
) -> Result<PoweredFlightTransition, PoweredFlightError> {
    match propagate_powered_flight_with_observer::<Infallible, _>(
        state,
        target_time_s,
        limits,
        process,
        integration,
        environment,
        gross_mass_kg,
        rng,
        |_| Ok(()),
    ) {
        Ok(value) => Ok(value),
        Err(ObservedPoweredFlightError::Dynamics(error)) => Err(error),
        Err(ObservedPoweredFlightError::Observer(error)) => match error {},
    }
}

#[cfg(test)]
mod tests {
    use approx::assert_abs_diff_eq;
    use mh370_domain::{great_circle_distance_nm, Hertz};
    use rand::SeedableRng;
    use std::sync::Mutex;

    use super::*;

    fn constant_weather() -> Era5Grid {
        let mut bytes = b"MHERA5V1".to_vec();
        for count in [2_u32, 2, 2, 2] {
            bytes.extend(count.to_le_bytes());
        }
        for time in [1_000_i64, 50_000] {
            bytes.extend(time.to_le_bytes());
        }
        for value in [500_f32, 43_000.0, -50.0, 20.0, 70.0, 130.0] {
            bytes.extend(value.to_le_bytes());
        }
        for value in std::iter::repeat_n(220.0_f32, 16) {
            bytes.extend(value.to_le_bytes());
        }
        for _ in 0..32 {
            bytes.extend(0.0_f32.to_le_bytes());
        }
        Era5Grid::parse(&bytes).unwrap()
    }

    fn gradient_weather() -> Era5Grid {
        let mut bytes = b"MHERA5V1".to_vec();
        for count in [2_u32, 2, 2, 2] {
            bytes.extend(count.to_le_bytes());
        }
        for time in [1_000_i64, 50_000] {
            bytes.extend(time.to_le_bytes());
        }
        for value in [500_f32, 43_000.0, -50.0, 20.0, 70.0, 130.0] {
            bytes.extend(value.to_le_bytes());
        }
        for time in 0..2 {
            for altitude in 0..2 {
                for latitude in 0..2 {
                    for longitude in 0..2 {
                        let value = 210.0
                            + 8.0 * time as f32
                            + 20.0 * altitude as f32
                            + latitude as f32
                            + 0.5 * longitude as f32;
                        bytes.extend(value.to_le_bytes());
                    }
                }
            }
        }
        for field_offset in [0.0_f32, 5.0] {
            for index in 0..16 {
                bytes.extend((field_offset + index as f32).to_le_bytes());
            }
        }
        Era5Grid::parse(&bytes).unwrap()
    }

    fn constant_magnetic() -> IgrfGrid {
        let mut bytes = b"MHIGRFV1".to_vec();
        for count in [2_u32, 2, 2] {
            bytes.extend(count.to_le_bytes());
        }
        bytes.extend(1_000_i64.to_le_bytes());
        bytes.extend(2014.18_f64.to_le_bytes());
        for value in [500_f32, 43_000.0, -50.0, 20.0, 70.0, 130.0] {
            bytes.extend(value.to_le_bytes());
        }
        for _ in 0..8 {
            bytes.extend(5.0_f32.to_le_bytes());
        }
        IgrfGrid::parse(&bytes).unwrap()
    }

    fn cruise_altitude_only_magnetic() -> IgrfGrid {
        let mut bytes = b"MHIGRFV1".to_vec();
        for count in [2_u32, 2, 2] {
            bytes.extend(count.to_le_bytes());
        }
        bytes.extend(1_000_i64.to_le_bytes());
        bytes.extend(2014.18_f64.to_le_bytes());
        for value in [25_000_f32, 43_000.0, -50.0, 20.0, 70.0, 130.0] {
            bytes.extend(value.to_le_bytes());
        }
        for _ in 0..8 {
            bytes.extend(5.0_f32.to_le_bytes());
        }
        IgrfGrid::parse(&bytes).unwrap()
    }

    fn environment<'a>(
        weather: &'a Era5Grid,
        magnetic: &'a IgrfGrid,
    ) -> PoweredFlightEnvironment<'a> {
        PoweredFlightEnvironment {
            weather,
            magnetic: Some(magnetic),
            magnetic_altitude_policy: MagneticAltitudePolicy::RejectOutsideGrid,
            time_origin_unix_s: 1_000.0,
        }
    }

    fn limits() -> PoweredFlightLimits {
        PoweredFlightLimits {
            minimum_pressure_altitude_ft: 500.0,
            maximum_pressure_altitude_ft: 43_000.0,
            minimum_mach_floor: 0.3,
            mmo: 0.87,
            vmo_kcas: 330.0,
            wing_area_m2: 427.8,
            maximum_lift_coefficient: 1.4,
            stall_speed_margin: 1.2,
            maximum_bank_deg: 30.0,
            maximum_roll_rate_deg_s: 3.0,
            maximum_mach_rate_per_s: 0.1 / 60.0,
            maximum_climb_rate_ft_min: 4_000.0,
            maximum_descent_rate_ft_min: 4_000.0,
            maximum_vertical_acceleration_ft_min_s: 200.0,
            heading_capture_time_s: 30.0,
            altitude_capture_time_s: 60.0,
        }
    }

    fn no_events() -> ManeuverProcess {
        ManeuverProcess {
            lateral_clock: None,
            speed_clock: None,
            altitude_clock: None,
            lateral_mode_weights: PoweredLateralModeWeights {
                constant_true_heading: 1.0,
                constant_magnetic_heading: 1.0,
                constant_true_track: 1.0,
                constant_magnetic_track: 1.0,
                great_circle_track_continuation: 1.0,
            },
            maximum_course_change_deg: 180.0,
            target_mach_min: 0.5,
            target_mach_max: 0.85,
            target_altitude_min_ft: 1_000.0,
            target_altitude_max_ft: 42_000.0,
            great_circle_leg_length_nm: 4_000.0,
        }
    }

    fn frequent_events() -> ManeuverProcess {
        let clock = RenewalClock {
            mean_interval_s: 1_000.0,
            minimum_interval_s: 10.0,
            gamma_shape: 1.5,
        };
        ManeuverProcess {
            lateral_clock: Some(clock),
            speed_clock: Some(clock),
            altitude_clock: Some(clock),
            ..no_events()
        }
    }

    fn shape_one_lateral_events() -> ManeuverProcess {
        ManeuverProcess {
            lateral_clock: Some(RenewalClock {
                mean_interval_s: 1_000.0,
                minimum_interval_s: 100.0,
                gamma_shape: 1.0,
            }),
            ..no_events()
        }
    }

    fn integration(step_s: f64) -> PoweredIntegration {
        PoweredIntegration {
            steady_step_s: step_s,
            transition_step_s: step_s,
            heading_capture_tolerance_deg: 0.05,
            maximum_events_per_transition: 100,
        }
    }

    fn aircraft() -> AircraftState {
        AircraftState {
            time: Seconds(0.0),
            position: LatLon::new(5.6, 99.0).unwrap(),
            altitude: Feet(35_000.0),
            track_true: Degrees(180.0),
            ground_speed: Knots(480.0),
            vertical_speed: FeetPerMinute(0.0),
            bfo_bias: Hertz(145.0),
        }
    }

    fn initial_state(
        process: ManeuverProcess,
        environment: PoweredFlightEnvironment<'_>,
        seed: u64,
    ) -> (PoweredFlightState, ChaCha8Rng) {
        let mut rng = ChaCha8Rng::seed_from_u64(seed);
        let state = initialize_powered_flight(
            aircraft(),
            0.78,
            PoweredLateralMode::ConstantTrueTrack,
            limits(),
            process,
            environment,
            210_000.0,
            &mut rng,
        )
        .unwrap();
        (state, rng)
    }

    fn pending_at(time_s: f64) -> Option<PendingRenewal> {
        Some(PendingRenewal {
            not_before: Seconds(time_s),
            next_event: Seconds(time_s),
        })
    }

    #[derive(Default)]
    struct NeverEligible;

    impl PoweredEventCandidateScorer for NeverEligible {
        type Error = Infallible;

        fn is_eligible(&self, _event: &PoweredEventProposalEvent) -> Result<bool, Self::Error> {
            Ok(false)
        }

        fn log_score(
            &self,
            _candidate: &PoweredEventProposalCandidate,
        ) -> Result<f64, Self::Error> {
            panic!("an ineligible event must not generate or score candidates")
        }
    }

    #[derive(Default)]
    struct RecordingScorer {
        eligible_kinds: Vec<PoweredEventKind>,
        eligibility_order: Mutex<Vec<(PoweredEventKind, f64, u64)>>,
        candidate_marks: Mutex<Vec<(PoweredEventKind, usize, PoweredEventMark)>>,
        score_by_index: bool,
        all_negative_infinity: bool,
    }

    impl PoweredEventCandidateScorer for RecordingScorer {
        type Error = Infallible;

        fn is_eligible(&self, event: &PoweredEventProposalEvent) -> Result<bool, Self::Error> {
            self.eligibility_order.lock().unwrap().push((
                event.kind,
                event.before.aircraft.time.0,
                event.event_number,
            ));
            Ok(self.eligible_kinds.contains(&event.kind))
        }

        fn log_score(&self, candidate: &PoweredEventProposalCandidate) -> Result<f64, Self::Error> {
            self.candidate_marks.lock().unwrap().push((
                candidate.event.kind,
                candidate.candidate_index,
                candidate.mark,
            ));
            if self.all_negative_infinity {
                Ok(f64::NEG_INFINITY)
            } else if self.score_by_index {
                Ok(candidate.candidate_index as f64)
            } else {
                Ok(0.0)
            }
        }
    }

    struct FixedScoreScorer(f64);

    impl PoweredEventCandidateScorer for FixedScoreScorer {
        type Error = Infallible;

        fn is_eligible(&self, _event: &PoweredEventProposalEvent) -> Result<bool, Self::Error> {
            Ok(true)
        }

        fn log_score(
            &self,
            _candidate: &PoweredEventProposalCandidate,
        ) -> Result<f64, Self::Error> {
            Ok(self.0)
        }
    }

    #[test]
    fn initialized_pending_renewals_record_their_dwell_origins_without_extra_rng_draws() {
        let weather = constant_weather();
        let magnetic = constant_magnetic();
        let env = environment(&weather, &magnetic);
        let process = shape_one_lateral_events();
        let origin_s = aircraft().time.0;
        let seed = 700;

        let mut expected_rng = ChaCha8Rng::seed_from_u64(seed);
        let expected_wait = process
            .lateral_clock
            .unwrap()
            .sample_wait_s(&mut expected_rng)
            .unwrap();
        let expected_tail = expected_rng.next_u64();

        let (state, mut actual_rng) = initial_state(process, env, seed);
        let pending = state.event_clocks.lateral.unwrap();
        assert_eq!(
            pending.not_before,
            Seconds(origin_s + process.lateral_clock.unwrap().minimum_interval_s)
        );
        assert_eq!(pending.next_event, Seconds(origin_s + expected_wait));
        assert_eq!(actual_rng.next_u64(), expected_tail);
        assert_eq!(state.event_clocks.speed, None);
        assert_eq!(state.event_clocks.altitude, None);
    }

    #[test]
    fn renewed_pending_clock_records_event_time_plus_minimum_dwell() {
        let weather = constant_weather();
        let magnetic = constant_magnetic();
        let env = environment(&weather, &magnetic);
        let process = shape_one_lateral_events();
        let (mut state, mut rng) = initial_state(process, env, 701);
        state.event_clocks.lateral = pending_at(25.0);

        let result = propagate_powered_flight(
            state,
            25.0,
            limits(),
            process,
            integration(60.0),
            env,
            210_000.0,
            &mut rng,
        )
        .unwrap();
        let renewed = result.state.event_clocks.lateral.unwrap();
        assert_eq!(renewed.not_before, Seconds(125.0));
        assert!(renewed.next_event.0 >= renewed.not_before.0);
        assert_eq!(result.state.event_counters.lateral, 1);
    }

    #[test]
    fn renewal_refresh_before_not_before_anchors_at_the_dwell_boundary() {
        let weather = constant_weather();
        let magnetic = constant_magnetic();
        let env = environment(&weather, &magnetic);
        let process = shape_one_lateral_events();
        let (state, _) = initial_state(process, env, 702);
        let before = state.event_clocks.lateral.unwrap();
        assert!(state.aircraft.time.0 < before.not_before.0);
        let mut expected_rng = ChaCha8Rng::seed_from_u64(9_702);
        let expected_residual = Exp::new(1.0 / 900.0).unwrap().sample(&mut expected_rng);
        let mut refresh_rng = ChaCha8Rng::seed_from_u64(9_702);

        let refreshed = refresh_powered_event_renewal(
            state,
            PoweredEventKind::Lateral,
            process,
            state.aircraft.time,
            &mut refresh_rng,
        )
        .unwrap();
        let after = refreshed.event_clocks.lateral.unwrap();
        assert_eq!(after.not_before, before.not_before);
        assert_eq!(
            after.next_event,
            Seconds(before.not_before.0 + expected_residual)
        );
        assert!(after.next_event.0 >= after.not_before.0);
    }

    #[test]
    fn renewal_refresh_after_not_before_uses_exponential_memorylessness() {
        let weather = constant_weather();
        let magnetic = constant_magnetic();
        let env = environment(&weather, &magnetic);
        let process = shape_one_lateral_events();
        let (mut state, _) = initial_state(process, env, 703);
        state.aircraft.time = Seconds(200.0);
        state.event_clocks.lateral = Some(PendingRenewal {
            not_before: Seconds(100.0),
            next_event: Seconds(500.0),
        });
        let mut expected_rng = ChaCha8Rng::seed_from_u64(9_703);
        let expected_residual = Exp::new(1.0 / 900.0).unwrap().sample(&mut expected_rng);
        let mut refresh_rng = ChaCha8Rng::seed_from_u64(9_703);

        let refreshed = refresh_powered_event_renewal(
            state,
            PoweredEventKind::Lateral,
            process,
            state.aircraft.time,
            &mut refresh_rng,
        )
        .unwrap();
        let after = refreshed.event_clocks.lateral.unwrap();
        assert_eq!(after.not_before, Seconds(100.0));
        assert_eq!(
            after.next_event,
            Seconds(200.0 + TIME_TOLERANCE_S + expected_residual)
        );
    }

    #[test]
    fn renewal_refresh_is_replay_pure_and_changes_only_the_selected_next_event() {
        let weather = constant_weather();
        let magnetic = constant_magnetic();
        let env = environment(&weather, &magnetic);
        let process = shape_one_lateral_events();
        let (state, _) = initial_state(process, env, 704);
        let original = state;
        let run = || {
            let mut rng = ChaCha8Rng::seed_from_u64(9_704);
            refresh_powered_event_renewal(
                state,
                PoweredEventKind::Lateral,
                process,
                state.aircraft.time,
                &mut rng,
            )
            .unwrap()
        };
        let first = run();
        let second = run();

        assert_eq!(first, second);
        assert_eq!(state, original);
        let mut expected = original;
        expected.event_clocks.lateral.as_mut().unwrap().next_event =
            first.event_clocks.lateral.unwrap().next_event;
        assert_eq!(first, expected);
    }

    #[test]
    fn renewal_refresh_rejects_disabled_due_and_nonunit_streams() {
        let weather = constant_weather();
        let magnetic = constant_magnetic();
        let env = environment(&weather, &magnetic);

        let disabled_process = no_events();
        let (disabled, _) = initial_state(disabled_process, env, 705);
        let mut rng = ChaCha8Rng::seed_from_u64(9_705);
        assert_eq!(
            refresh_powered_event_renewal(
                disabled,
                PoweredEventKind::Lateral,
                disabled_process,
                disabled.aircraft.time,
                &mut rng,
            ),
            Err(PoweredRenewalRefreshError::StreamDisabled {
                kind: PoweredEventKind::Lateral,
            })
        );

        let shape_one = shape_one_lateral_events();
        let (mut due, _) = initial_state(shape_one, env, 706);
        due.event_clocks.lateral = pending_at(due.aircraft.time.0);
        assert_eq!(
            refresh_powered_event_renewal(
                due,
                PoweredEventKind::Lateral,
                shape_one,
                due.aircraft.time,
                &mut rng,
            ),
            Err(PoweredRenewalRefreshError::ClockDue {
                kind: PoweredEventKind::Lateral,
            })
        );

        let nonunit = frequent_events();
        let (nonunit_state, _) = initial_state(nonunit, env, 707);
        assert_eq!(
            refresh_powered_event_renewal(
                nonunit_state,
                PoweredEventKind::Lateral,
                nonunit,
                nonunit_state.aircraft.time,
                &mut rng,
            ),
            Err(PoweredRenewalRefreshError::UnsupportedGammaShape {
                kind: PoweredEventKind::Lateral,
            })
        );
    }

    #[test]
    fn renewal_refresh_rejects_clock_process_and_current_time_mismatches() {
        let weather = constant_weather();
        let magnetic = constant_magnetic();
        let env = environment(&weather, &magnetic);
        let process = shape_one_lateral_events();
        let (state, _) = initial_state(process, env, 708);
        let mut rng = ChaCha8Rng::seed_from_u64(9_708);

        assert_eq!(
            refresh_powered_event_renewal(
                state,
                PoweredEventKind::Lateral,
                process,
                Seconds(state.aircraft.time.0 + 1.0),
                &mut rng,
            ),
            Err(PoweredRenewalRefreshError::CurrentTimeMismatch)
        );

        let mut mismatched = state;
        mismatched.event_clocks.speed = pending_at(500.0);
        assert_eq!(
            refresh_powered_event_renewal(
                mismatched,
                PoweredEventKind::Lateral,
                process,
                mismatched.aircraft.time,
                &mut rng,
            ),
            Err(PoweredRenewalRefreshError::ClockProcessMismatch {
                kind: PoweredEventKind::Speed,
            })
        );
    }

    #[test]
    fn renewal_refresh_rejects_only_origins_beyond_the_time_tolerance() {
        let weather = constant_weather();
        let magnetic = constant_magnetic();
        let env = environment(&weather, &magnetic);
        let process = shape_one_lateral_events();
        let (mut state, _) = initial_state(process, env, 709);
        let clock = process.lateral_clock.unwrap();
        let current = state.aircraft.time.0;
        let mut rng = ChaCha8Rng::seed_from_u64(9_709);

        state.event_clocks.lateral = Some(PendingRenewal {
            not_before: Seconds(current + clock.minimum_interval_s + 0.5 * TIME_TOLERANCE_S),
            next_event: Seconds(current + clock.minimum_interval_s + 10.0),
        });
        assert!(refresh_powered_event_renewal(
            state,
            PoweredEventKind::Lateral,
            process,
            state.aircraft.time,
            &mut rng,
        )
        .is_ok());

        state.event_clocks.lateral = Some(PendingRenewal {
            not_before: Seconds(current + clock.minimum_interval_s + 4.0 * TIME_TOLERANCE_S),
            next_event: Seconds(current + clock.minimum_interval_s + 10.0),
        });
        assert_eq!(
            refresh_powered_event_renewal(
                state,
                PoweredEventKind::Lateral,
                process,
                state.aircraft.time,
                &mut rng,
            ),
            Err(PoweredRenewalRefreshError::RenewalOriginInFuture {
                kind: PoweredEventKind::Lateral,
            })
        );
    }

    #[test]
    fn ulp_crossed_reachable_boundary_collapses_without_panicking() {
        let lower = 0.609_002_298_177_742_7;
        let upper = 0.609_002_298_177_742_5;
        let envelope = InstantaneousPoweredLimits {
            minimum_mach: lower,
            maximum_mach: 0.87,
            stall_mach: lower,
            vmo_mach: 0.87,
            load_factor_g: 1.0,
            lift_coefficient: 0.5,
            maximum_bank_for_lift_deg: 30.0,
            maximum_turn_rate_deg_s: 1.0,
        };
        let result = rate_reachable_mach(upper, 0.7, 0.0, envelope, 1_000.0).unwrap();
        assert_eq!(result, lower);
    }

    #[test]
    fn straight_level_zero_wind_closes_distance_and_preserves_state() {
        let weather = constant_weather();
        let magnetic = constant_magnetic();
        let env = environment(&weather, &magnetic);
        let process = no_events();
        let (state, mut rng) = initial_state(process, env, 1);
        let speed = state.aircraft.ground_speed.0;
        let result = propagate_powered_flight(
            state,
            3_600.0,
            limits(),
            process,
            integration(60.0),
            env,
            210_000.0,
            &mut rng,
        )
        .unwrap();
        let expected = destination_wgs84(
            state.aircraft.position,
            state.aircraft.track_true,
            NauticalMiles(speed),
        )
        .unwrap();
        assert_abs_diff_eq!(
            result.state.aircraft.position.latitude.0,
            expected.latitude.0,
            epsilon = 1.0e-9
        );
        assert_abs_diff_eq!(
            result.state.aircraft.position.longitude.0,
            expected.longitude.0,
            epsilon = 1.0e-9
        );
        assert_abs_diff_eq!(result.state.aircraft.altitude.0, 35_000.0, epsilon = 0.0);
        assert_abs_diff_eq!(result.state.mach, 0.78, epsilon = 0.0);
        assert_abs_diff_eq!(result.state.bank_angle.0, 0.0, epsilon = 0.0);
        assert_eq!(result.diagnostics.steady_steps, 60);
        assert_eq!(result.diagnostics.transition_steps, 0);
    }

    #[test]
    fn segment_carries_the_exact_weather_used_at_both_endpoints() {
        let weather = gradient_weather();
        let magnetic = constant_magnetic();
        let env = environment(&weather, &magnetic);
        let process = no_events();
        let (mut state, mut rng) = initial_state(process, env, 101);
        state.command.target_pressure_altitude = Feet(40_000.0);
        let segment = advance_powered_flight_step(
            state,
            15.0,
            limits(),
            process,
            integration(15.0),
            env,
            210_000.0,
            &mut rng,
        )
        .unwrap()
        .unwrap();
        let independently_sampled_start = weather_at(env, segment.start.aircraft).unwrap();
        let independently_sampled_end = weather_at(env, segment.end.aircraft).unwrap();

        assert_eq!(segment.start_weather, independently_sampled_start);
        assert_eq!(segment.end_weather, independently_sampled_end);
        assert_ne!(segment.start_weather, segment.end_weather);
    }

    #[test]
    fn finite_rate_course_speed_and_altitude_changes_respect_declared_caps() {
        let weather = constant_weather();
        let magnetic = constant_magnetic();
        let env = environment(&weather, &magnetic);
        let process = no_events();
        let (mut state, mut rng) = initial_state(process, env, 2);
        state.command.lateral_mode = PoweredLateralMode::ConstantTrueHeading;
        state.command.selected_control = Degrees(90.0);
        state.command.target_mach = 0.84;
        state.command.target_pressure_altitude = Feet(40_000.0);
        let result = propagate_powered_flight(
            state,
            15.0,
            limits(),
            process,
            integration(15.0),
            env,
            210_000.0,
            &mut rng,
        )
        .unwrap();
        assert!(result.state.bank_angle.0.abs() <= limits().maximum_bank_deg);
        assert!(
            (result.state.mach - state.mach).abs()
                <= limits().maximum_mach_rate_per_s * 15.0 + 1.0e-12
        );
        assert!(
            result.state.aircraft.vertical_speed.0
                <= limits().maximum_vertical_acceleration_ft_min_s * 15.0 + 1.0e-12
        );
        assert_eq!(result.diagnostics.transition_steps, 1);
        assert_eq!(result.diagnostics.steady_steps, 0);
    }

    #[test]
    fn events_are_exact_boundaries_and_endpoint_commands_are_post_event() {
        let weather = constant_weather();
        let magnetic = constant_magnetic();
        let env = environment(&weather, &magnetic);
        let process = frequent_events();
        let (mut state, mut rng) = initial_state(process, env, 3);
        state.event_clocks = PoweredEventClocks {
            lateral: pending_at(100.0),
            speed: pending_at(150.0),
            altitude: pending_at(200.0),
        };
        let original_command = state.command;
        let mut endpoints = Vec::new();
        let result = propagate_powered_flight_with_observer::<Infallible, _>(
            state,
            200.0,
            limits(),
            process,
            integration(60.0),
            env,
            210_000.0,
            &mut rng,
            |segment| {
                endpoints.push(segment.end.aircraft.time.0);
                Ok(())
            },
        )
        .unwrap();
        for event_time in [100.0, 150.0, 200.0] {
            assert!(endpoints.contains(&event_time));
        }
        assert_eq!(
            result.diagnostics.events,
            PoweredEventCounters {
                lateral: 1,
                speed: 1,
                altitude: 1,
            }
        );
        assert_eq!(result.state.event_counters, result.diagnostics.events);
        assert_ne!(result.state.command, original_command);
        assert!(result.diagnostics.event_aligned_steps >= 3);
    }

    #[test]
    fn same_seed_and_settings_are_bitwise_deterministic_including_events() {
        let weather = constant_weather();
        let magnetic = constant_magnetic();
        let env = environment(&weather, &magnetic);
        let process = frequent_events();
        let run = || {
            let (state, mut rng) = initial_state(process, env, 44);
            propagate_powered_flight(
                state,
                8_000.0,
                limits(),
                process,
                PoweredIntegration {
                    steady_step_s: 60.0,
                    transition_step_s: 15.0,
                    ..integration(60.0)
                },
                env,
                210_000.0,
                &mut rng,
            )
            .unwrap()
        };
        assert_eq!(run(), run());
    }

    #[test]
    fn randomized_history_respects_stepwise_rate_and_speed_envelopes() {
        let weather = constant_weather();
        let magnetic = constant_magnetic();
        let env = environment(&weather, &magnetic);
        let process = frequent_events();
        let (state, mut rng) = initial_state(process, env, 45);
        let result = propagate_powered_flight_with_observer::<Infallible, _>(
            state,
            8_000.0,
            limits(),
            process,
            PoweredIntegration {
                steady_step_s: 60.0,
                transition_step_s: 15.0,
                ..integration(60.0)
            },
            env,
            210_000.0,
            &mut rng,
            |segment| {
                let duration = segment.duration.0;
                assert!(
                    (segment.end.mach - segment.start.mach).abs()
                        <= limits().maximum_mach_rate_per_s * duration + 1.0e-9
                );
                assert!(
                    (segment.end.bank_angle.0 - segment.start.bank_angle.0).abs()
                        <= limits().maximum_roll_rate_deg_s * duration + 1.0e-9
                );
                assert!(
                    (segment.end.aircraft.vertical_speed.0
                        - segment.start.aircraft.vertical_speed.0)
                        .abs()
                        <= limits().maximum_vertical_acceleration_ft_min_s * duration + 1.0e-9
                );
                let end_weather = weather_at(env, segment.end.aircraft).unwrap();
                let end_limits = instantaneous_powered_limits(
                    limits(),
                    end_weather,
                    segment.end.aircraft.altitude.0,
                    210_000.0,
                    segment.end.bank_angle,
                    segment.end.mach,
                )
                .unwrap();
                assert!(segment.end.mach >= end_limits.minimum_mach - 1.0e-9);
                assert!(segment.end.mach <= end_limits.maximum_mach + 1.0e-9);
                assert!(segment.midpoint_mach >= segment.midpoint_limits.minimum_mach - 1.0e-9);
                assert!(segment.midpoint_mach <= segment.midpoint_limits.maximum_mach + 1.0e-9);
                assert!(segment.end.bank_angle.0.abs() <= limits().maximum_bank_deg + 1.0e-9);
                Ok(())
            },
        )
        .unwrap();
        assert!(result.diagnostics.events.total() > 0);
    }

    #[test]
    fn descent_from_vmo_decelerates_within_rate_or_returns_typed_conflict() {
        let weather = constant_weather();
        let magnetic = constant_magnetic();
        let env = environment(&weather, &magnetic);
        let process = no_events();
        let weather_at_start = weather
            .sample(1_000.0, 35_000.0, aircraft().position)
            .unwrap();
        let start_maximum = instantaneous_powered_limits(
            limits(),
            weather_at_start,
            35_000.0,
            210_000.0,
            Degrees(0.0),
            0.8,
        )
        .unwrap()
        .maximum_mach;
        let mut descending = aircraft();
        descending.vertical_speed = FeetPerMinute(-4_000.0);
        let mut rng = ChaCha8Rng::seed_from_u64(451);
        let mut state = initialize_powered_flight(
            descending,
            start_maximum,
            PoweredLateralMode::ConstantTrueTrack,
            limits(),
            process,
            env,
            210_000.0,
            &mut rng,
        )
        .unwrap();
        state.command.target_pressure_altitude = Feet(5_000.0);
        let segment = advance_powered_flight_step(
            state,
            120.0,
            limits(),
            process,
            PoweredIntegration {
                steady_step_s: 120.0,
                transition_step_s: 120.0,
                ..integration(60.0)
            },
            env,
            210_000.0,
            &mut rng,
        )
        .unwrap()
        .unwrap();
        assert!(segment.end.mach < state.mach);
        assert!(
            (segment.midpoint_mach - state.mach).abs()
                <= limits().maximum_mach_rate_per_s * 60.0 + 1.0e-12
        );
        assert!(
            (segment.end.mach - segment.midpoint_mach).abs()
                <= limits().maximum_mach_rate_per_s * 60.0 + 1.0e-12
        );
        assert!(segment.midpoint_mach <= segment.midpoint_limits.maximum_mach + 1.0e-12);

        let mut slow_limits = limits();
        slow_limits.maximum_mach_rate_per_s = 0.000_01;
        let mut slow_rng = ChaCha8Rng::seed_from_u64(452);
        let mut slow_state = initialize_powered_flight(
            descending,
            start_maximum,
            PoweredLateralMode::ConstantTrueTrack,
            slow_limits,
            process,
            env,
            210_000.0,
            &mut slow_rng,
        )
        .unwrap();
        slow_state.command.target_pressure_altitude = Feet(5_000.0);
        assert!(matches!(
            advance_powered_flight_step(
                slow_state,
                120.0,
                slow_limits,
                process,
                PoweredIntegration {
                    steady_step_s: 120.0,
                    transition_step_s: 120.0,
                    ..integration(60.0)
                },
                env,
                210_000.0,
                &mut slow_rng,
            ),
            Err(PoweredFlightError::MachRateEnvelopeConflict { .. })
        ));
    }

    #[test]
    fn climb_and_turn_near_stall_remain_inside_actual_midpoint_lift_envelope() {
        let weather = constant_weather();
        let magnetic = constant_magnetic();
        let env = environment(&weather, &magnetic);
        let process = no_events();
        let mut low = aircraft();
        low.altitude = Feet(10_000.0);
        let local_weather = weather.sample(1_000.0, 10_000.0, low.position).unwrap();
        let minimum_mach = instantaneous_powered_limits(
            limits(),
            local_weather,
            10_000.0,
            230_000.0,
            Degrees(0.0),
            0.6,
        )
        .unwrap()
        .minimum_mach;
        let mut rng = ChaCha8Rng::seed_from_u64(453);
        let mut state = initialize_powered_flight(
            low,
            minimum_mach + 0.02,
            PoweredLateralMode::ConstantTrueHeading,
            limits(),
            process,
            env,
            230_000.0,
            &mut rng,
        )
        .unwrap();
        state.command.selected_control = Degrees(90.0);
        state.command.target_pressure_altitude = Feet(20_000.0);
        state.command.target_mach = minimum_mach + 0.02;
        let segment = advance_powered_flight_step(
            state,
            60.0,
            limits(),
            process,
            integration(60.0),
            env,
            230_000.0,
            &mut rng,
        )
        .unwrap()
        .unwrap();
        assert!(segment.midpoint_bank_angle.0.abs() > 0.0);
        assert!(segment.midpoint_mach >= segment.midpoint_limits.minimum_mach - 1.0e-12);
        assert!(segment.midpoint_limits.lift_coefficient <= limits().maximum_lift_coefficient);
        assert!(
            segment.midpoint_bank_angle.0.abs()
                <= segment.midpoint_limits.maximum_bank_for_lift_deg + 1.0e-12
        );
    }

    #[test]
    fn initialization_rejects_vertical_speed_outside_declared_limits() {
        let weather = constant_weather();
        let magnetic = constant_magnetic();
        let env = environment(&weather, &magnetic);
        let mut invalid = aircraft();
        invalid.vertical_speed = FeetPerMinute(4_001.0);
        let mut rng = ChaCha8Rng::seed_from_u64(454);
        assert_eq!(
            initialize_powered_flight(
                invalid,
                0.78,
                PoweredLateralMode::ConstantTrueTrack,
                limits(),
                no_events(),
                env,
                210_000.0,
                &mut rng,
            )
            .unwrap_err(),
            PoweredFlightError::InvalidState
        );
    }

    #[test]
    fn bank_rollout_turn_is_retained_without_heading_snap() {
        let weather = constant_weather();
        let magnetic = constant_magnetic();
        let env = environment(&weather, &magnetic);
        let process = no_events();
        let (mut state, mut rng) = initial_state(process, env, 455);
        state.command.lateral_mode = PoweredLateralMode::ConstantTrueHeading;
        state.command.selected_control = state.heading_true;
        state.bank_angle = Degrees(1.0);
        let first = advance_powered_flight_step(
            state,
            1.0,
            limits(),
            process,
            integration(1.0),
            env,
            210_000.0,
            &mut rng,
        )
        .unwrap()
        .unwrap();
        let rollout_turn = signed_angle_difference(first.end.heading_true.0, state.heading_true.0);
        assert!(rollout_turn > 0.0);
        assert_abs_diff_eq!(first.end.bank_angle.0, 0.0, epsilon = 0.0);

        let second = advance_powered_flight_step(
            first.end,
            2.0,
            limits(),
            process,
            integration(1.0),
            env,
            210_000.0,
            &mut rng,
        )
        .unwrap()
        .unwrap();
        assert_abs_diff_eq!(
            second.end.heading_true.0,
            first.end.heading_true.0,
            epsilon = 1.0e-12
        );
    }

    #[test]
    fn reusable_manual_budget_counts_due_entry_and_cross_step_events() {
        let weather = constant_weather();
        let magnetic = constant_magnetic();
        let env = environment(&weather, &magnetic);
        let process = no_events();
        let (mut due, mut due_rng) = initial_state(process, env, 456);
        due.event_clocks = PoweredEventClocks {
            lateral: pending_at(0.0),
            speed: pending_at(0.0),
            altitude: pending_at(0.0),
        };
        let mut too_small = PoweredEventBudget::new(2).unwrap();
        assert_eq!(
            advance_powered_flight_step_with_budget(
                due,
                1.0,
                limits(),
                process,
                integration(1.0),
                env,
                210_000.0,
                &mut too_small,
                &mut due_rng,
            )
            .unwrap_err(),
            PoweredFlightError::EventLimitExceeded
        );

        let (mut state, mut rng) = initial_state(process, env, 457);
        state.event_clocks.lateral = pending_at(10.0);
        let mut budget = PoweredEventBudget::new(1).unwrap();
        let first = advance_powered_flight_step_with_budget(
            state,
            10.0,
            limits(),
            process,
            integration(60.0),
            env,
            210_000.0,
            &mut budget,
            &mut rng,
        )
        .unwrap()
        .unwrap();
        assert_eq!(first.events_at_end.lateral, 1);
        let mut second_state = first.end;
        second_state.event_clocks.lateral = pending_at(20.0);
        assert_eq!(
            advance_powered_flight_step_with_budget(
                second_state,
                20.0,
                limits(),
                process,
                integration(60.0),
                env,
                210_000.0,
                &mut budget,
                &mut rng,
            )
            .unwrap_err(),
            PoweredFlightError::EventLimitExceeded
        );
    }

    #[test]
    fn geometric_great_circle_leg_renews_before_artificial_endpoint() {
        let weather = constant_weather();
        let magnetic = constant_magnetic();
        let env = environment(&weather, &magnetic);
        let process = no_events();
        let (mut state, mut rng) = initial_state(process, env, 458);
        state.command.lateral_mode = PoweredLateralMode::GreatCircleTrackContinuation;
        state.command.selected_control = state.aircraft.track_true;
        state.command.great_circle_destination = Some(
            destination_wgs84(
                state.aircraft.position,
                state.aircraft.track_true,
                NauticalMiles(0.1),
            )
            .unwrap(),
        );
        let segment = advance_powered_flight_step(
            state,
            60.0,
            limits(),
            process,
            integration(60.0),
            env,
            210_000.0,
            &mut rng,
        )
        .unwrap()
        .unwrap();
        assert!(segment.great_circle_leg_renewed_at_start);
        let remaining = fixed_waypoint_guidance(
            segment.end.aircraft.position,
            FixedWaypointLeg {
                waypoint: segment.end.command.great_circle_destination.unwrap(),
                arrival_radius: NauticalMiles(0.01),
            },
        )
        .unwrap()
        .distance_remaining
        .0;
        assert!(remaining > 3_900.0);
    }

    #[test]
    fn adaptive_steps_use_coarse_cruise_and_fine_transition_segments() {
        let weather = constant_weather();
        let magnetic = constant_magnetic();
        let env = environment(&weather, &magnetic);
        let process = no_events();
        let (mut state, mut rng) = initial_state(process, env, 5);
        let steady = propagate_powered_flight(
            state,
            600.0,
            limits(),
            process,
            PoweredIntegration {
                steady_step_s: 60.0,
                transition_step_s: 15.0,
                ..integration(60.0)
            },
            env,
            210_000.0,
            &mut rng,
        )
        .unwrap();
        assert_eq!(steady.diagnostics.integration_steps, 10);

        state.command.selected_control = Degrees(90.0);
        let transition = propagate_powered_flight(
            state,
            600.0,
            limits(),
            process,
            PoweredIntegration {
                steady_step_s: 60.0,
                transition_step_s: 15.0,
                ..integration(60.0)
            },
            env,
            210_000.0,
            &mut rng,
        )
        .unwrap();
        assert!(transition.diagnostics.transition_steps > 0);
        assert!(transition.diagnostics.integration_steps > 10);
    }

    #[test]
    fn fifteen_second_solution_controls_thirty_and_sixty_second_error() {
        let weather = constant_weather();
        let magnetic = constant_magnetic();
        let env = environment(&weather, &magnetic);
        let process = no_events();
        let run = |step_s| {
            let (mut state, mut rng) = initial_state(process, env, 6);
            state.command.lateral_mode = PoweredLateralMode::ConstantTrueHeading;
            state.command.selected_control = Degrees(120.0);
            state.command.target_mach = 0.83;
            state.command.target_pressure_altitude = Feet(39_000.0);
            propagate_powered_flight(
                state,
                3_600.0,
                limits(),
                process,
                integration(step_s),
                env,
                210_000.0,
                &mut rng,
            )
            .unwrap()
        };
        let fine = run(15.0);
        let medium = run(30.0);
        let coarse = run(60.0);
        let medium_error =
            great_circle_distance_nm(fine.state.aircraft.position, medium.state.aircraft.position)
                .0;
        let coarse_error =
            great_circle_distance_nm(fine.state.aircraft.position, coarse.state.aircraft.position)
                .0;
        assert!(medium_error <= coarse_error + 1.0e-9);
        assert!(medium_error < 3.0);
        assert!(coarse_error < 8.0);
        assert_eq!(fine.state.event_counters, coarse.state.event_counters);
    }

    #[test]
    fn stall_floor_responds_to_mass_and_bank_and_vmo_caps_high_altitude() {
        let weather = WeatherSample {
            temperature_k: 220.0,
            wind_east: Knots(0.0),
            wind_north: Knots(0.0),
        };
        let light = instantaneous_powered_limits(
            limits(),
            weather,
            35_000.0,
            180_000.0,
            Degrees(0.0),
            0.78,
        )
        .unwrap();
        let heavy_banked = instantaneous_powered_limits(
            limits(),
            weather,
            35_000.0,
            230_000.0,
            Degrees(30.0),
            0.78,
        )
        .unwrap();
        assert!(heavy_banked.stall_mach > light.stall_mach);
        assert!(light.maximum_mach <= limits().mmo);
        assert!(light.maximum_mach <= light.vmo_mach + 1.0e-12);
        assert!(heavy_banked.lift_coefficient <= limits().maximum_lift_coefficient);
    }

    #[test]
    fn event_limit_is_a_reported_error_not_silent_truncation() {
        let weather = constant_weather();
        let magnetic = constant_magnetic();
        let env = environment(&weather, &magnetic);
        let process = frequent_events();
        let (mut state, mut rng) = initial_state(process, env, 7);
        state.event_clocks = PoweredEventClocks {
            lateral: pending_at(10.0),
            speed: pending_at(10.0),
            altitude: pending_at(10.0),
        };
        let error = propagate_powered_flight(
            state,
            20.0,
            limits(),
            process,
            PoweredIntegration {
                maximum_events_per_transition: 2,
                ..integration(60.0)
            },
            env,
            210_000.0,
            &mut rng,
        )
        .unwrap_err();
        assert_eq!(error, PoweredFlightError::EventLimitExceeded);
    }

    #[test]
    fn magnetic_modes_require_declination_but_true_modes_do_not() {
        let weather = constant_weather();
        let no_magnetic = PoweredFlightEnvironment {
            weather: &weather,
            magnetic: None,
            magnetic_altitude_policy: MagneticAltitudePolicy::RejectOutsideGrid,
            time_origin_unix_s: 1_000.0,
        };
        let mut first_rng = ChaCha8Rng::seed_from_u64(8);
        assert_eq!(
            initialize_powered_flight(
                aircraft(),
                0.78,
                PoweredLateralMode::ConstantMagneticHeading,
                limits(),
                no_events(),
                no_magnetic,
                210_000.0,
                &mut first_rng,
            )
            .unwrap_err(),
            PoweredFlightError::MissingMagneticEnvironment
        );
        let mut second_rng = ChaCha8Rng::seed_from_u64(8);
        initialize_powered_flight(
            aircraft(),
            0.78,
            PoweredLateralMode::ConstantTrueTrack,
            limits(),
            no_events(),
            no_magnetic,
            210_000.0,
            &mut second_rng,
        )
        .unwrap();
    }

    #[test]
    fn magnetic_altitude_clamp_is_declared_counted_and_can_be_rejected() {
        let weather = constant_weather();
        let magnetic = cruise_altitude_only_magnetic();
        let mut low_aircraft = aircraft();
        low_aircraft.altitude = Feet(10_000.0);
        let clamp_environment = PoweredFlightEnvironment {
            weather: &weather,
            magnetic: Some(&magnetic),
            magnetic_altitude_policy: MagneticAltitudePolicy::ClampToGridAltitude,
            time_origin_unix_s: 1_000.0,
        };
        let mut clamp_rng = ChaCha8Rng::seed_from_u64(81);
        let state = initialize_powered_flight(
            low_aircraft,
            0.55,
            PoweredLateralMode::ConstantMagneticTrack,
            limits(),
            no_events(),
            clamp_environment,
            210_000.0,
            &mut clamp_rng,
        )
        .unwrap();
        let result = propagate_powered_flight(
            state,
            60.0,
            limits(),
            no_events(),
            integration(60.0),
            clamp_environment,
            210_000.0,
            &mut clamp_rng,
        )
        .unwrap();
        assert_abs_diff_eq!(
            result.diagnostics.boundary_seconds.magnetic_altitude_clamp,
            60.0,
            epsilon = 0.0
        );

        let reject_environment = PoweredFlightEnvironment {
            magnetic_altitude_policy: MagneticAltitudePolicy::RejectOutsideGrid,
            ..clamp_environment
        };
        let mut reject_rng = ChaCha8Rng::seed_from_u64(81);
        assert!(matches!(
            initialize_powered_flight(
                low_aircraft,
                0.55,
                PoweredLateralMode::ConstantMagneticTrack,
                limits(),
                no_events(),
                reject_environment,
                210_000.0,
                &mut reject_rng,
            ),
            Err(PoweredFlightError::MagneticAltitudeOutsideGrid {
                altitude_ft: 10_000.0,
                minimum_ft: 25_000.0,
                maximum_ft: 43_000.0,
            })
        ));
    }

    #[test]
    fn state_and_declared_process_round_trip_through_serde() {
        let weather = constant_weather();
        let magnetic = constant_magnetic();
        let env = environment(&weather, &magnetic);
        let process = frequent_events();
        let (mut state, _) = initial_state(process, env, 9);
        state.event_clocks = PoweredEventClocks {
            lateral: pending_at(100.0),
            speed: pending_at(200.0),
            altitude: pending_at(300.0),
        };
        let value = (state, process, limits(), integration(30.0));
        let bytes = serde_json::to_vec(&value).unwrap();
        let decoded: (
            PoweredFlightState,
            ManeuverProcess,
            PoweredFlightLimits,
            PoweredIntegration,
        ) = serde_json::from_slice(&bytes).unwrap();
        assert_eq!(decoded, value);
    }

    #[test]
    fn obsolete_numeric_event_clock_schema_fails_closed() {
        let obsolete = r#"{
            "next_lateral_event": 100.0,
            "next_speed_event": null,
            "next_altitude_event": null
        }"#;
        assert!(serde_json::from_str::<PoweredEventClocks>(obsolete).is_err());

        let originless_canonical_names = r#"{
            "lateral": 100.0,
            "speed": null,
            "altitude": null
        }"#;
        assert!(serde_json::from_str::<PoweredEventClocks>(originless_canonical_names).is_err());
    }

    #[test]
    fn event_candidate_probabilities_give_the_exact_auxiliary_identity() {
        let state = PoweredFlightState {
            aircraft: aircraft(),
            heading_true: Degrees(180.0),
            mach: 0.78,
            bank_angle: Degrees(0.0),
            command: PoweredFlightCommand {
                lateral_mode: PoweredLateralMode::ConstantTrueTrack,
                selected_control: Degrees(180.0),
                great_circle_destination: None,
                target_mach: 0.78,
                target_pressure_altitude: Feet(35_000.0),
            },
            event_clocks: PoweredEventClocks {
                lateral: None,
                speed: None,
                altitude: None,
            },
            event_counters: PoweredEventCounters::default(),
        };
        let scores = [0.0, 3.0_f64.ln(), f64::NEG_INFINITY];
        let candidates: Vec<EventMarkCandidate> = scores
            .into_iter()
            .map(|log_score| EventMarkCandidate {
                after_mark: Ok(state),
                log_score,
            })
            .collect();
        let epsilon = 0.2;
        let selection = candidate_selection(&candidates, epsilon);
        assert_abs_diff_eq!(
            selection.probabilities.iter().sum::<f64>(),
            1.0,
            epsilon = 1.0e-15
        );
        assert_abs_diff_eq!(selection.probabilities[0], 4.0 / 15.0, epsilon = 1.0e-15);
        assert_abs_diff_eq!(selection.probabilities[1], 2.0 / 3.0, epsilon = 1.0e-15);
        assert_abs_diff_eq!(selection.probabilities[2], 1.0 / 15.0, epsilon = 1.0e-15);
        let recovered_prior_mass = selection
            .probabilities
            .iter()
            .map(|probability| {
                let correction = -(candidates.len() as f64).ln() - probability.ln();
                probability * correction.exp()
            })
            .sum::<f64>();
        assert_abs_diff_eq!(recovered_prior_mass, 1.0, epsilon = 1.0e-15);
        for probability in selection.probabilities {
            let correction = -(candidates.len() as f64).ln() - probability.ln();
            assert!(correction <= -epsilon.ln() + 1.0e-14);
        }
    }

    #[test]
    fn all_negative_infinity_scores_use_the_uniform_candidate_law() {
        let candidates: Vec<EventMarkCandidate> = (0..5)
            .map(|_| EventMarkCandidate {
                after_mark: Err(PoweredFlightError::InvalidState),
                log_score: f64::NEG_INFINITY,
            })
            .collect();
        let selection = candidate_selection(&candidates, 0.01);
        assert!(selection.all_scores_negative_infinity);
        assert_eq!(selection.finite_score_count, 0);
        assert_eq!(selection.minimum_finite_log_score, None);
        assert_eq!(selection.maximum_finite_log_score, None);
        for probability in selection.probabilities {
            assert_abs_diff_eq!(probability, 0.2, epsilon = 0.0);
        }
        assert_abs_diff_eq!(selection.effective_sample_size, 5.0, epsilon = 1.0e-14);
        assert_abs_diff_eq!(selection.entropy_nats, 5.0_f64.ln(), epsilon = 1.0e-14);
    }

    #[test]
    fn ineligible_proposal_path_is_bitwise_identical_to_the_legacy_step_and_rng_tail() {
        let weather = constant_weather();
        let magnetic = constant_magnetic();
        let env = environment(&weather, &magnetic);
        let process = frequent_events();
        let (mut state, rng) = initial_state(process, env, 901);
        state.event_clocks = PoweredEventClocks {
            lateral: pending_at(0.0),
            speed: pending_at(0.0),
            altitude: pending_at(0.0),
        };
        let mut legacy_rng = rng.clone();
        let mut proposed_legacy_rng = rng;
        let mut legacy_budget = PoweredEventBudget::new(100).unwrap();
        let mut proposed_budget = legacy_budget;
        let legacy = advance_powered_flight_step_with_budget(
            state,
            60.0,
            limits(),
            process,
            integration(60.0),
            env,
            210_000.0,
            &mut legacy_budget,
            &mut legacy_rng,
        )
        .unwrap()
        .unwrap();
        let scorer = NeverEligible;
        let proposed = advance_powered_flight_step_with_budget_and_event_proposal(
            state,
            60.0,
            limits(),
            process,
            integration(60.0),
            env,
            210_000.0,
            &mut proposed_budget,
            PoweredEventProposalConfig {
                candidates_per_event: 8,
                defensive_prior_probability: 0.1,
            },
            &mut proposed_legacy_rng,
            &PoweredEventProposalRng::from_seed([7; 32]),
            &scorer,
        )
        .unwrap()
        .unwrap();
        assert_eq!(proposed.segment, legacy);
        assert_eq!(
            proposed.log_prior_over_proposal.to_bits(),
            0.0_f64.to_bits()
        );
        assert_eq!(proposed.proposed_events, PoweredEventCounters::default());
        assert!(proposed.event_proposals.is_empty());
        assert_eq!(proposed_budget, legacy_budget);
        for _ in 0..8 {
            assert_eq!(proposed_legacy_rng.next_u64(), legacy_rng.next_u64());
        }
    }

    #[test]
    fn proposal_records_due_events_at_entry_and_endpoint_in_physical_order() {
        let weather = constant_weather();
        let magnetic = constant_magnetic();
        let env = environment(&weather, &magnetic);
        let process = frequent_events();
        let (mut state, mut legacy_rng) = initial_state(process, env, 902);
        state.event_clocks = PoweredEventClocks {
            lateral: pending_at(0.0),
            speed: pending_at(10.0),
            altitude: pending_at(10.0),
        };
        let mut budget = PoweredEventBudget::new(100).unwrap();
        let scorer = RecordingScorer {
            eligible_kinds: vec![
                PoweredEventKind::Lateral,
                PoweredEventKind::Speed,
                PoweredEventKind::Altitude,
            ],
            score_by_index: true,
            ..RecordingScorer::default()
        };
        let epsilon = 0.1;
        let result = advance_powered_flight_step_with_budget_and_event_proposal(
            state,
            10.0,
            limits(),
            process,
            integration(60.0),
            env,
            210_000.0,
            &mut budget,
            PoweredEventProposalConfig {
                candidates_per_event: 4,
                defensive_prior_probability: epsilon,
            },
            &mut legacy_rng,
            &PoweredEventProposalRng::from_seed([8; 32]),
            &scorer,
        )
        .unwrap()
        .unwrap();
        assert_eq!(
            result.segment.events_at_start,
            PoweredEventCounters {
                lateral: 1,
                speed: 0,
                altitude: 0,
            }
        );
        assert_eq!(
            result.segment.events_at_end,
            PoweredEventCounters {
                lateral: 0,
                speed: 1,
                altitude: 1,
            }
        );
        assert_eq!(
            result.proposed_events,
            PoweredEventCounters {
                lateral: 1,
                speed: 1,
                altitude: 1,
            }
        );
        let event_order: Vec<_> = result
            .event_proposals
            .iter()
            .map(|diagnostic| (diagnostic.kind, diagnostic.event_time.0))
            .collect();
        assert_eq!(
            event_order,
            vec![
                (PoweredEventKind::Lateral, 0.0),
                (PoweredEventKind::Speed, 10.0),
                (PoweredEventKind::Altitude, 10.0),
            ]
        );
        assert_abs_diff_eq!(
            result.log_prior_over_proposal,
            result
                .event_proposals
                .iter()
                .map(|diagnostic| diagnostic.log_prior_over_proposal)
                .sum::<f64>(),
            epsilon = 0.0
        );
        for diagnostic in &result.event_proposals {
            assert_eq!(diagnostic.candidate_count, 4);
            assert_eq!(diagnostic.finite_score_count, 4);
            assert!(!diagnostic.all_scores_negative_infinity);
            assert!(diagnostic.log_prior_over_proposal <= -epsilon.ln() + 1.0e-14);
            assert!(diagnostic.selection_effective_sample_size >= 1.0);
            assert!(diagnostic.selection_effective_sample_size <= 4.0);
            assert!(diagnostic.selection_entropy_nats >= 0.0);
            assert!(diagnostic.selection_entropy_nats <= 4.0_f64.ln() + 1.0e-14);
        }
        assert_eq!(
            scorer
                .eligibility_order
                .lock()
                .unwrap()
                .iter()
                .map(|(kind, time, _)| (*kind, *time))
                .collect::<Vec<_>>(),
            event_order
        );
    }

    #[test]
    fn invalid_candidates_keep_defensive_support_and_fail_only_when_selected() {
        let weather = constant_weather();
        let env = PoweredFlightEnvironment {
            weather: &weather,
            magnetic: None,
            magnetic_altitude_policy: MagneticAltitudePolicy::RejectOutsideGrid,
            time_origin_unix_s: 1_000.0,
        };
        let mut process = frequent_events();
        process.speed_clock = None;
        process.altitude_clock = None;
        process.lateral_mode_weights = PoweredLateralModeWeights {
            constant_true_heading: 0.0,
            constant_magnetic_heading: 1.0,
            constant_true_track: 0.0,
            constant_magnetic_track: 0.0,
            great_circle_track_continuation: 0.0,
        };
        let (mut state, mut legacy_rng) = initial_state(process, env, 903);
        state.event_clocks.lateral = pending_at(0.0);
        let mut budget = PoweredEventBudget::new(100).unwrap();
        let scorer = RecordingScorer {
            eligible_kinds: vec![PoweredEventKind::Lateral],
            ..RecordingScorer::default()
        };
        let error = advance_powered_flight_step_with_budget_and_event_proposal(
            state,
            10.0,
            limits(),
            process,
            integration(60.0),
            env,
            210_000.0,
            &mut budget,
            PoweredEventProposalConfig {
                candidates_per_event: 4,
                defensive_prior_probability: 0.1,
            },
            &mut legacy_rng,
            &PoweredEventProposalRng::from_seed([9; 32]),
            &scorer,
        )
        .unwrap_err();
        match error {
            PoweredEventProposalError::SelectedCandidate { diagnostic, source } => {
                assert_eq!(source, PoweredFlightError::MissingMagneticEnvironment);
                assert_eq!(diagnostic.materialization_failures, 4);
                assert_eq!(diagnostic.finite_score_count, 0);
                assert!(diagnostic.all_scores_negative_infinity);
                assert_eq!(
                    diagnostic.log_prior_over_proposal.to_bits(),
                    0.0_f64.to_bits()
                );
            }
            other => panic!("unexpected proposal error: {other:?}"),
        }
        assert!(scorer.candidate_marks.lock().unwrap().is_empty());
    }

    #[test]
    fn proposal_rng_keys_are_tuple_separated_and_candidate_stable() {
        use std::collections::HashSet;

        let proposal_rng = PoweredEventProposalRng::from_seed([10; 32]);
        let mut signatures = HashSet::new();
        for kind in [
            PoweredEventKind::Lateral,
            PoweredEventKind::Speed,
            PoweredEventKind::Altitude,
        ] {
            for event_index in 0..3 {
                for purpose in [
                    EventProposalRngPurpose::CandidateMark,
                    EventProposalRngPurpose::Selection,
                    EventProposalRngPurpose::RenewalClock,
                ] {
                    for replicate in 0..4 {
                        let mut rng = proposal_rng.event_rng(kind, event_index, purpose, replicate);
                        assert!(signatures.insert((rng.next_u64(), rng.next_u64())));
                    }
                }
            }
        }
        let mut first = proposal_rng.event_rng(
            PoweredEventKind::Lateral,
            7,
            EventProposalRngPurpose::CandidateMark,
            2,
        );
        let expected = [first.next_u64(), first.next_u64(), first.next_u64()];
        // Generate unrelated roots in a different order; the fixed tuple is unchanged.
        let mut unrelated = proposal_rng.event_rng(
            PoweredEventKind::Altitude,
            99,
            EventProposalRngPurpose::RenewalClock,
            0,
        );
        let _ = unrelated.next_u64();
        let mut repeated = proposal_rng.event_rng(
            PoweredEventKind::Lateral,
            7,
            EventProposalRngPurpose::CandidateMark,
            2,
        );
        assert_eq!(
            expected,
            [
                repeated.next_u64(),
                repeated.next_u64(),
                repeated.next_u64()
            ]
        );
    }

    #[test]
    fn adding_candidates_does_not_shift_existing_marks_or_the_renewal_clock() {
        let weather = constant_weather();
        let magnetic = constant_magnetic();
        let env = environment(&weather, &magnetic);
        let mut process = frequent_events();
        process.speed_clock = None;
        process.altitude_clock = None;
        let (mut state, rng) = initial_state(process, env, 904);
        state.event_clocks.lateral = pending_at(0.0);
        let proposal_rng = PoweredEventProposalRng::from_seed([11; 32]);
        let run = |candidate_count| {
            let scorer = RecordingScorer {
                eligible_kinds: vec![PoweredEventKind::Lateral],
                ..RecordingScorer::default()
            };
            let mut legacy_rng = rng.clone();
            let mut budget = PoweredEventBudget::new(100).unwrap();
            let result = advance_powered_flight_step_with_budget_and_event_proposal(
                state,
                10.0,
                limits(),
                process,
                integration(60.0),
                env,
                210_000.0,
                &mut budget,
                PoweredEventProposalConfig {
                    candidates_per_event: candidate_count,
                    defensive_prior_probability: 0.1,
                },
                &mut legacy_rng,
                &proposal_rng,
                &scorer,
            )
            .unwrap()
            .unwrap();
            (result, scorer.candidate_marks.into_inner().unwrap())
        };
        let (two, two_marks) = run(2);
        let (eight, eight_marks) = run(8);
        assert_eq!(two_marks, eight_marks[..2]);
        assert_eq!(
            two.segment.end.event_clocks.lateral,
            eight.segment.end.event_clocks.lateral
        );
    }

    #[test]
    fn bridge_split_reuses_one_transition_context_without_changing_results_or_rng_tail() {
        let weather = constant_weather();
        let magnetic = constant_magnetic();
        let env = environment(&weather, &magnetic);
        let process = frequent_events();
        let (mut initial, initial_rng) = initial_state(process, env, 905);
        initial.event_clocks = PoweredEventClocks {
            lateral: pending_at(100.0),
            speed: pending_at(150.0),
            altitude: None,
        };
        let proposal_rng = PoweredEventProposalRng::from_seed([12; 32]);
        let run = |boundaries: &[f64]| {
            let mut state = initial;
            let mut legacy_rng = initial_rng.clone();
            let mut budget = PoweredEventBudget::new(100).unwrap();
            let scorer = RecordingScorer {
                eligible_kinds: vec![PoweredEventKind::Lateral],
                score_by_index: true,
                ..RecordingScorer::default()
            };
            let mut correction = 0.0;
            let mut diagnostics = Vec::new();
            for &boundary in boundaries {
                while state.aircraft.time.0 < boundary - TIME_TOLERANCE_S {
                    let result = advance_powered_flight_step_with_budget_and_event_proposal(
                        state,
                        boundary,
                        limits(),
                        process,
                        PoweredIntegration {
                            steady_step_s: 60.0,
                            transition_step_s: 15.0,
                            ..integration(60.0)
                        },
                        env,
                        210_000.0,
                        &mut budget,
                        PoweredEventProposalConfig {
                            candidates_per_event: 4,
                            defensive_prior_probability: 0.1,
                        },
                        &mut legacy_rng,
                        &proposal_rng,
                        &scorer,
                    )
                    .unwrap()
                    .unwrap();
                    correction += result.log_prior_over_proposal;
                    diagnostics.extend(result.event_proposals);
                    state = result.segment.end;
                }
            }
            let tail = [legacy_rng.next_u64(), legacy_rng.next_u64()];
            (state, budget, correction, diagnostics, tail)
        };
        let direct = run(&[200.0]);
        let split = run(&[100.0, 200.0]);
        assert_eq!(direct.0, split.0);
        assert_eq!(direct.1, split.1);
        assert_eq!(direct.2.to_bits(), split.2.to_bits());
        assert_eq!(direct.3, split.3);
        assert_eq!(direct.4, split.4);
    }

    #[test]
    fn scorer_rejects_nan_and_positive_infinity_but_accepts_negative_infinity() {
        let weather = constant_weather();
        let magnetic = constant_magnetic();
        let env = environment(&weather, &magnetic);
        let mut process = frequent_events();
        process.lateral_clock = None;
        process.altitude_clock = None;
        let (mut state, initial_rng) = initial_state(process, env, 906);
        state.event_clocks.speed = pending_at(0.0);
        for invalid_score in [f64::NAN, f64::INFINITY] {
            let mut legacy_rng = initial_rng.clone();
            let mut budget = PoweredEventBudget::new(100).unwrap();
            let error = advance_powered_flight_step_with_budget_and_event_proposal(
                state,
                10.0,
                limits(),
                process,
                integration(60.0),
                env,
                210_000.0,
                &mut budget,
                PoweredEventProposalConfig {
                    candidates_per_event: 2,
                    defensive_prior_probability: 0.1,
                },
                &mut legacy_rng,
                &PoweredEventProposalRng::from_seed([13; 32]),
                &FixedScoreScorer(invalid_score),
            )
            .unwrap_err();
            assert!(matches!(
                error,
                PoweredEventProposalError::InvalidScore {
                    kind: PoweredEventKind::Speed,
                    event_number: 1,
                    candidate_index: 0,
                }
            ));
        }

        let mut legacy_rng = initial_rng;
        let mut budget = PoweredEventBudget::new(100).unwrap();
        let result = advance_powered_flight_step_with_budget_and_event_proposal(
            state,
            10.0,
            limits(),
            process,
            integration(60.0),
            env,
            210_000.0,
            &mut budget,
            PoweredEventProposalConfig {
                candidates_per_event: 2,
                defensive_prior_probability: 0.1,
            },
            &mut legacy_rng,
            &PoweredEventProposalRng::from_seed([13; 32]),
            &FixedScoreScorer(f64::NEG_INFINITY),
        )
        .unwrap()
        .unwrap();
        assert!(result.event_proposals[0].all_scores_negative_infinity);
        assert_eq!(
            result.event_proposals[0].log_prior_over_proposal.to_bits(),
            0.0_f64.to_bits()
        );
    }

    #[test]
    fn proposal_configuration_is_bounded_and_rejects_nonfinite_probabilities() {
        for invalid in [
            PoweredEventProposalConfig {
                candidates_per_event: 0,
                defensive_prior_probability: 0.1,
            },
            PoweredEventProposalConfig {
                candidates_per_event: MAX_POWERED_EVENT_PROPOSAL_CANDIDATES + 1,
                defensive_prior_probability: 0.1,
            },
            PoweredEventProposalConfig {
                candidates_per_event: 4,
                defensive_prior_probability: 0.0,
            },
            PoweredEventProposalConfig {
                candidates_per_event: 4,
                defensive_prior_probability: f64::NAN,
            },
            PoweredEventProposalConfig {
                candidates_per_event: MAX_POWERED_EVENT_PROPOSAL_CANDIDATES,
                defensive_prior_probability: f64::from_bits(1),
            },
            PoweredEventProposalConfig {
                candidates_per_event: 4,
                defensive_prior_probability: 1.1,
            },
        ] {
            assert!(invalid.validate().is_err());
        }
        assert!(PoweredEventProposalConfig {
            candidates_per_event: MAX_POWERED_EVENT_PROPOSAL_CANDIDATES,
            defensive_prior_probability: 1.0,
        }
        .validate()
        .is_ok());
    }

    #[test]
    #[ignore = "manual release-mode cadence throughput benchmark"]
    fn benchmark_six_hour_uniform_and_adaptive_cadences() {
        use std::{hint::black_box, time::Instant};

        let weather = constant_weather();
        let magnetic = constant_magnetic();
        let env = environment(&weather, &magnetic);
        let process = no_events();
        let cases = [
            ("uniform_60", 60.0, 60.0),
            ("uniform_30", 30.0, 30.0),
            ("uniform_15", 15.0, 15.0),
            ("adaptive_60_15", 60.0, 15.0),
        ];
        let trajectories = 500_u64;
        let mut endpoints = Vec::new();
        for (label, steady_step_s, transition_step_s) in cases {
            let started = Instant::now();
            let mut segments = 0_u64;
            let mut endpoint = aircraft().position;
            for seed in 0..trajectories {
                let (mut state, mut rng) = initial_state(process, env, seed + 10_000);
                state.command.lateral_mode = PoweredLateralMode::ConstantTrueHeading;
                state.command.selected_control = Degrees(150.0);
                state.command.target_mach = 0.82;
                state.command.target_pressure_altitude = Feet(39_000.0);
                let result = propagate_powered_flight(
                    state,
                    21_600.0,
                    limits(),
                    process,
                    PoweredIntegration {
                        steady_step_s,
                        transition_step_s,
                        ..integration(30.0)
                    },
                    env,
                    210_000.0,
                    &mut rng,
                )
                .unwrap();
                segments += result.diagnostics.integration_steps;
                endpoint = result.state.aircraft.position;
                black_box(result.state);
            }
            let elapsed = started.elapsed().as_secs_f64();
            eprintln!(
                "{label}: {trajectories} six-hour trajectories, {segments} segments, \
                 {elapsed:.6} s, {:.0} trajectories/s, {:.0} segments/s",
                trajectories as f64 / elapsed,
                segments as f64 / elapsed,
            );
            endpoints.push((label, endpoint));
        }
        let fine = endpoints
            .iter()
            .find(|(label, _)| *label == "uniform_15")
            .unwrap()
            .1;
        for (label, endpoint) in endpoints {
            eprintln!(
                "{label}: endpoint separation from uniform_15 = {:.6} NM",
                great_circle_distance_nm(fine, endpoint).0,
            );
        }
    }
}
