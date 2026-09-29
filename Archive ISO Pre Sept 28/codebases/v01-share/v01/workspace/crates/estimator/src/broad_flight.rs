//! Sequential, deliberately broad powered-flight inference through the last
//! ordinary SATCOM epoch.
//!
//! The model composes the dynamics, fuel, and SATCOM spokes without embedding
//! their equations in the particle filter. Fuel is propagated as a diagnostic
//! state through the filtering branch: exhaustion or a fuel-domain failure is
//! recorded but does not itself change the BTO/BFO weight. That ordinary
//! filtering branch deliberately retains its two-engine powered screen after a
//! diagnostic exhaustion; the explicit continuation below instead splits at
//! each engine boundary and uses the actual remaining-engine count.

use std::{
    collections::{BTreeMap, BTreeSet},
    sync::Mutex,
};

use mh370_domain::{
    destination_wgs84, AircraftState, Degrees, Feet, FeetPerMinute, Hertz, Knots, LatLon,
    Microseconds, NauticalMiles, Seconds,
};
use mh370_dynamics::{
    advance_powered_flight_step_with_budget,
    advance_powered_flight_step_with_budget_and_event_proposal, initialize_powered_flight,
    propagate_powered_flight, refresh_powered_event_renewal, EnvironmentError, ManeuverProcess,
    PoweredBoundarySeconds, PoweredEventBudget, PoweredEventCandidateScorer, PoweredEventClocks,
    PoweredEventCounters, PoweredEventKind, PoweredEventProposalCandidate,
    PoweredEventProposalConfig, PoweredEventProposalDiagnostic, PoweredEventProposalError,
    PoweredEventProposalEvent, PoweredEventProposalRng, PoweredFlightEnvironment,
    PoweredFlightError, PoweredFlightLimits, PoweredFlightSegment, PoweredFlightState,
    PoweredIntegration, PoweredLateralMode, PoweredLimitActivity, PoweredRenewalRefreshError,
    PoweredStepRegime, RadarPrior,
};
use mh370_end_of_flight::{
    advance_powered_fuel, evaluate_powered_segment_feasibility,
    evaluate_powered_segment_operational_feasibility, openap_b772_trent895_cruise_thrust_ceiling,
    project_frozen_powered_fuel_exhaustion, ConditionalB772AerodynamicFamily,
    DeclaredAdditionalDragAllowance, DeclaredTotalThrustRange, EngineFuelFlowShares,
    FrozenPoweredFuelOperatingPoint, FrozenPoweredFuelProjection, FrozenPoweredFuelProjectionError,
    Kilograms, KilogramsPerCubicMetre, MetresPerSecond, Newtons,
    OpenapB772Trent895CruiseThrustError, OpenapB772Trent895CruiseThrustInput, PoweredFuelError,
    PoweredFuelModel, PoweredFuelSegmentInput, PoweredFuelState, PoweredFuelStep,
    PoweredFuelWeather, PoweredSegmentFeasibilityError, PoweredSegmentFeasibilityInput,
    PoweredSegmentOperationalFeasibilityError, OPENAP_B772_TRENT895_MAXIMUM_MACH,
    OPENAP_B772_TRENT895_MAXIMUM_PRESSURE_ALTITUDE_FT, OPENAP_B772_TRENT895_MINIMUM_MACH,
    OPENAP_B772_TRENT895_MINIMUM_PRESSURE_ALTITUDE_FT,
};
use mh370_particle_filter::{
    Initialization, IntermediatePotentialBridge, IntermediatePotentialBridgePoint,
    IntermediatePotentialProposal, IntermediatePotentialStep, ParticleModel, PersistentTwist,
    Proposal, SelectionGuide, StratifiedPostResampleMove, StratifiedPostResampleMoveContext,
    StratumId,
};
use mh370_satcom::{
    bfo_components, bto, evaluate_observation, normal_log_density, BfoBiasState, ObservationFit,
    SatcomModelConfig, SatcomModelError,
};
use rand::Rng;
use rand_chacha::{rand_core::SeedableRng, ChaCha8Rng};
use rand_distr::{Distribution, StandardNormal};
use serde::{Deserialize, Serialize};
use thiserror::Error;

use crate::FlightObservation;

const TIME_TOLERANCE_S: f64 = 1.0e-8;
const MASS_TOLERANCE_KG: f64 = 1.0e-8;
const FUEL_SELECTION_WINDOW_TOLERANCE_S: f64 = 1.0e-6;

pub const BROAD_FLIGHT_MODEL_FAMILY: &str = "broad-powered-marked-jump-v1";

/// Stable identity for exact conditional refreshes of pending manoeuvre clocks.
pub const BROAD_PENDING_RENEWAL_REFRESH_FAMILY: &str =
    "broad-pending-renewal-post-resample-refresh-v1";

const BROAD_PENDING_RENEWAL_REFRESH_RNG_DOMAIN: &str =
    "broad-pending-renewal-post-resample-refresh-stream-v1";

/// Pending manoeuvre streams refreshed from their exact conditional law after
/// an ordinary posterior resample.
///
/// The runner and particle filter own the observation schedule. This config
/// says only which independent auxiliary clocks an invoked move refreshes.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
pub struct BroadPendingRenewalRefreshConfig {
    pub lateral: bool,
    pub speed: bool,
    pub altitude: bool,
}

impl BroadPendingRenewalRefreshConfig {
    pub fn validate(self) -> Result<(), BroadFlightError> {
        if !self.lateral && !self.speed && !self.altitude {
            return Err(BroadFlightError::InvalidConfiguration(
                "pending-renewal refresh must select at least one event stream",
            ));
        }
        Ok(())
    }

    fn kinds(self) -> impl Iterator<Item = PoweredEventKind> {
        [
            (PoweredEventKind::Lateral, self.lateral),
            (PoweredEventKind::Speed, self.speed),
            (PoweredEventKind::Altitude, self.altitude),
        ]
        .into_iter()
        .filter_map(|(kind, enabled)| enabled.then_some(kind))
    }

    /// Compact deterministic provenance. The external PF schedule remains the
    /// authoritative record of the exact observation indices where it ran.
    pub fn stable_descriptor(self) -> String {
        format!(
            "family={BROAD_PENDING_RENEWAL_REFRESH_FAMILY};lateral={};speed={};altitude={};law=exact-shape-one-pending-renewal-conditional;trigger=ordinary-posterior-resample-only;scientific-evidence=none",
            self.lateral, self.speed, self.altitude,
        )
    }
}

/// Cumulative count of exact auxiliary-clock refreshes along one lineage.
#[derive(Debug, Clone, Copy, Default, PartialEq, Eq, Serialize, Deserialize)]
pub struct BroadPendingRenewalRefreshDiagnostics {
    pub total_refreshes: u64,
    pub lateral_refreshes: u64,
    pub speed_refreshes: u64,
    pub altitude_refreshes: u64,
}

impl BroadPendingRenewalRefreshDiagnostics {
    pub const fn is_empty(&self) -> bool {
        self.total_refreshes == 0
            && self.lateral_refreshes == 0
            && self.speed_refreshes == 0
            && self.altitude_refreshes == 0
    }

    pub fn validate(self) -> bool {
        self.lateral_refreshes
            .checked_add(self.speed_refreshes)
            .and_then(|count| count.checked_add(self.altitude_refreshes))
            == Some(self.total_refreshes)
    }

    fn record(&mut self, kind: PoweredEventKind) -> Result<(), BroadFlightError> {
        self.total_refreshes = self.total_refreshes.checked_add(1).ok_or(
            BroadFlightError::InvalidPendingRenewalRefreshState(
                "pending-renewal refresh diagnostic counter overflow",
            ),
        )?;
        let counter = match kind {
            PoweredEventKind::Lateral => &mut self.lateral_refreshes,
            PoweredEventKind::Speed => &mut self.speed_refreshes,
            PoweredEventKind::Altitude => &mut self.altitude_refreshes,
        };
        *counter =
            counter
                .checked_add(1)
                .ok_or(BroadFlightError::InvalidPendingRenewalRefreshState(
                    "pending-renewal refresh diagnostic counter overflow",
                ))?;
        Ok(())
    }

    fn checked_add(self, other: Self) -> Result<Self, BroadFlightError> {
        let add = |left: u64, right: u64| {
            left.checked_add(right)
                .ok_or(BroadFlightError::InvalidPendingRenewalRefreshState(
                    "pending-renewal refresh diagnostic counter overflow",
                ))
        };
        Ok(Self {
            total_refreshes: add(self.total_refreshes, other.total_refreshes)?,
            lateral_refreshes: add(self.lateral_refreshes, other.lateral_refreshes)?,
            speed_refreshes: add(self.speed_refreshes, other.speed_refreshes)?,
            altitude_refreshes: add(self.altitude_refreshes, other.altitude_refreshes)?,
        })
    }
}

/// Exact target-invariant move for pending shape-one renewal clocks.
///
/// Each PF invocation obtains one child-specific hook stream. The kernel draws
/// one local seed from it, then derives a separately keyed substream for every
/// selected event kind, so enabling another kind cannot shift an existing
/// kind's refresh draw.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct BroadPendingRenewalRefreshKernel {
    config: BroadPendingRenewalRefreshConfig,
}

impl BroadPendingRenewalRefreshKernel {
    pub fn new(config: BroadPendingRenewalRefreshConfig) -> Result<Self, BroadFlightError> {
        config.validate()?;
        Ok(Self { config })
    }

    pub const fn config(self) -> BroadPendingRenewalRefreshConfig {
        self.config
    }

    pub fn stable_descriptor(self) -> String {
        self.config.stable_descriptor()
    }
}

/// Stable identity for the proposal-only lateral-event SATCOM guide.
pub const BROAD_SATCOM_EVENT_MARK_GUIDE_FAMILY: &str = "broad-satcom-lateral-event-mark-guide-v1";

/// Closed uniform interval. Equal endpoints represent a fixed value.
#[derive(Debug, Clone, Copy, PartialEq, Serialize, Deserialize)]
pub struct BroadUniformRange {
    pub minimum: f64,
    pub maximum: f64,
}

impl BroadUniformRange {
    pub const fn fixed(value: f64) -> Self {
        Self {
            minimum: value,
            maximum: value,
        }
    }

    pub fn validate(self) -> bool {
        self.minimum.is_finite() && self.maximum.is_finite() && self.maximum >= self.minimum
    }

    fn sample(self, rng: &mut ChaCha8Rng) -> f64 {
        if self.minimum == self.maximum {
            self.minimum
        } else {
            rng.gen_range(self.minimum..=self.maximum)
        }
    }

    fn sample_log_uniform(self, rng: &mut ChaCha8Rng) -> f64 {
        if self.minimum == self.maximum {
            self.minimum
        } else {
            rng.gen_range(self.minimum.ln()..=self.maximum.ln()).exp()
        }
    }
}

/// One immutable structural/process stratum. Current lateral mode may change;
/// this identifier remains fixed for representation and ancestry diagnostics.
#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct BroadFlightStratum {
    pub id: StratumId,
    pub name: String,
    pub initial_lateral_mode: PoweredLateralMode,
    pub maneuver_process: ManeuverProcess,
}

/// Particle-correlated fuel uncertainty. The quantity perturbation is held
/// through an optional Arc-1 reset, while the flow scale multiplies every
/// subsequent broad-family segment for that particle.
#[derive(Debug, Clone, Copy, PartialEq, Serialize, Deserialize)]
pub struct BroadFuelUncertainty {
    pub total_quantity_offset_kg: BroadUniformRange,
    pub flow_scale_log_uniform: BroadUniformRange,
}

/// Design used to represent the continuous log-uniform fuel-flow latent at
/// initialization. This is deliberately a model-construction choice rather
/// than a field on [`BroadFlightConfig`], preserving existing config literals
/// and callers.
#[derive(Debug, Clone, Copy, Default, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum BroadFuelFlowInitializationDesign {
    /// Independent draws from the declared log-uniform prior. This preserves
    /// the original broad-flight implementation exactly.
    #[default]
    IndependentLogUniform,
    /// One deterministic, interior point in every equal-probability log-space
    /// cell of each structural stratum. Equal root weights represent the cell
    /// masses, so this changes only computational coverage, not the prior.
    LogSpaceLatinHypercube,
}

impl BroadFuelFlowInitializationDesign {
    pub const fn as_str(self) -> &'static str {
        match self {
            Self::IndependentLogUniform => "independent_log_uniform",
            Self::LogSpaceLatinHypercube => "log_space_latin_hypercube",
        }
    }
}

/// One step in an observation-interval-dependent multiple-try proposal.
///
/// The configured count applies when the elapsed time since the preceding
/// operation is greater than or equal to `minimum_elapsed_seconds`. Tiers must
/// be supplied in strictly increasing elapsed-time order.
#[derive(Debug, Clone, Copy, PartialEq, Serialize, Deserialize)]
pub struct BroadProposalCandidateTier {
    pub minimum_elapsed_seconds: f64,
    pub proposal_candidates: usize,
}

/// Computational schedule for the exact multiple-try transition proposal.
///
/// This changes only how transitions from the declared scientific prior are
/// proposed. The returned `p/q` correction preserves that prior exactly.
/// `Constant` retains the historical behavior of using
/// [`BroadFlightConfig::proposal_candidates`] at every SATCOM epoch. With
/// `ObservationIntervalTiers`, that same field is the below-first-tier count,
/// and each elapsed-time tier replaces it at and above its boundary.
#[derive(Debug, Clone, Default, PartialEq, Serialize, Deserialize)]
#[serde(tag = "kind", rename_all = "snake_case")]
pub enum BroadProposalCandidateSchedule {
    #[default]
    Constant,
    ObservationIntervalTiers {
        tiers: Vec<BroadProposalCandidateTier>,
    },
}

impl BroadProposalCandidateSchedule {
    pub fn validate_with_baseline_candidates(
        &self,
        baseline_candidates: usize,
    ) -> Result<(), BroadFlightError> {
        validate_proposal_candidate_count(baseline_candidates)?;
        let Self::ObservationIntervalTiers { tiers } = self else {
            return Ok(());
        };
        if tiers.is_empty() {
            return Err(BroadFlightError::InvalidConfiguration(
                "observation-interval proposal schedule must contain at least one tier",
            ));
        }
        let mut previous_minimum = None;
        for tier in tiers {
            if !tier.minimum_elapsed_seconds.is_finite()
                || tier.minimum_elapsed_seconds < 0.0
                || previous_minimum.is_some_and(|previous| tier.minimum_elapsed_seconds <= previous)
            {
                return Err(BroadFlightError::InvalidConfiguration(
                    "proposal schedule tier boundaries must be finite, nonnegative, and strictly increasing",
                ));
            }
            validate_proposal_candidate_count(tier.proposal_candidates)?;
            previous_minimum = Some(tier.minimum_elapsed_seconds);
        }
        Ok(())
    }

    /// Exact proposal count selected for a SATCOM interval.
    pub fn candidates_for_elapsed_seconds(
        &self,
        baseline_candidates: usize,
        elapsed_seconds: f64,
    ) -> usize {
        debug_assert!(elapsed_seconds.is_finite() && elapsed_seconds >= 0.0);
        match self {
            Self::Constant => baseline_candidates,
            Self::ObservationIntervalTiers { tiers } => tiers
                .iter()
                .take_while(|tier| elapsed_seconds >= tier.minimum_elapsed_seconds)
                .last()
                .map_or(baseline_candidates, |tier| tier.proposal_candidates),
        }
    }

    /// Stable compact descriptor for artifact metadata. The configuration
    /// hash remains the authoritative exact identity.
    pub fn stable_descriptor(&self, baseline_candidates: usize) -> String {
        match self {
            Self::Constant => format!("proposal=constant-k{baseline_candidates}"),
            Self::ObservationIntervalTiers { tiers } => {
                let tiers = tiers
                    .iter()
                    .map(|tier| {
                        format!(
                            "ge{}s-k{}",
                            tier.minimum_elapsed_seconds, tier.proposal_candidates
                        )
                    })
                    .collect::<Vec<_>>()
                    .join(",");
                format!("proposal=elapsed-tiered-v1;base-k{baseline_candidates};{tiers}")
            }
        }
    }
}

fn validate_proposal_candidate_count(count: usize) -> Result<(), BroadFlightError> {
    if count == 0 || count > 64 {
        return Err(BroadFlightError::InvalidConfiguration(
            "proposal candidate count must lie in 1..=64",
        ));
    }
    Ok(())
}

/// One exact SATCOM endpoint at which lateral event marks may use a
/// proposal-only, finite prior-candidate guide.
///
/// A due lateral event is eligible when its remaining time to the physical
/// endpoint lies in the inclusive interval
/// `[minimum_lead, maximum_lookback]`. The endpoint likelihood remains the
/// ordinary enabled BTO/BFO likelihood and is assimilated only after the
/// transition.
#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct BroadSatcomEventMarkGuideEpoch {
    pub observation_id: String,
    pub minimum_lead: Seconds,
    pub maximum_lookback: Seconds,
    pub candidates_per_event: usize,
    pub defensive_prior_probability: f64,
    /// Nonnegative multiplier beta in `softmax(beta * log_likelihood)`.
    /// Exactly zero skips every proxy projection and gives valid candidates
    /// equal guide scores. Projection is also skipped when the defensive
    /// prior probability is one because the resulting proposal is uniform
    /// regardless of this multiplier.
    pub score_temperature: f64,
}

impl BroadSatcomEventMarkGuideEpoch {
    fn validate(&self) -> Result<(), BroadFlightError> {
        if self.observation_id.trim().is_empty()
            || !self.minimum_lead.is_finite()
            || !self.maximum_lookback.is_finite()
            || self.minimum_lead.0 < 0.0
            || self.maximum_lookback.0 <= self.minimum_lead.0
            || !(2..=mh370_dynamics::MAX_POWERED_EVENT_PROPOSAL_CANDIDATES)
                .contains(&self.candidates_per_event)
            || !self.defensive_prior_probability.is_finite()
            || self.defensive_prior_probability <= 0.0
            || self.defensive_prior_probability > 1.0
            || !self.score_temperature.is_finite()
            || self.score_temperature < 0.0
        {
            return Err(BroadFlightError::InvalidConfiguration(
                "invalid SATCOM event-mark guide epoch",
            ));
        }
        PoweredEventProposalConfig {
            candidates_per_event: self.candidates_per_event,
            defensive_prior_probability: self.defensive_prior_probability,
        }
        .validate()
        .map_err(|_| BroadFlightError::InvalidConfiguration("invalid SATCOM event-mark proposal"))
    }

    fn dynamics_config(&self) -> PoweredEventProposalConfig {
        PoweredEventProposalConfig {
            candidates_per_event: self.candidates_per_event,
            defensive_prior_probability: self.defensive_prior_probability,
        }
    }
}

/// Exact-ID schedule for the proposal-only lateral-event SATCOM guide.
#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct BroadSatcomEventMarkGuideConfig {
    pub epochs: Vec<BroadSatcomEventMarkGuideEpoch>,
}

impl BroadSatcomEventMarkGuideConfig {
    pub fn validate(&self) -> Result<(), BroadFlightError> {
        if self.epochs.is_empty() {
            return Err(BroadFlightError::InvalidConfiguration(
                "SATCOM event-mark guide must contain at least one epoch",
            ));
        }
        let mut ids = BTreeSet::new();
        for epoch in &self.epochs {
            epoch.validate()?;
            if !ids.insert(epoch.observation_id.as_str()) {
                return Err(BroadFlightError::InvalidConfiguration(
                    "duplicate SATCOM event-mark guide observation ID",
                ));
            }
        }
        Ok(())
    }

    pub fn epoch(&self, observation_id: &str) -> Option<&BroadSatcomEventMarkGuideEpoch> {
        self.epochs
            .iter()
            .find(|epoch| epoch.observation_id == observation_id)
    }

    /// Compact deterministic provenance. Serialized configuration remains the
    /// authoritative identity.
    pub fn stable_descriptor(&self) -> String {
        let epochs = self
            .epochs
            .iter()
            .map(|epoch| {
                format!(
                    "{}:[{},{}]s-k{}-eps{}-beta{}",
                    epoch.observation_id,
                    epoch.minimum_lead.0,
                    epoch.maximum_lookback.0,
                    epoch.candidates_per_event,
                    epoch.defensive_prior_probability,
                    epoch.score_temperature,
                )
            })
            .collect::<Vec<_>>()
            .join(",");
        format!(
            "family={BROAD_SATCOM_EVENT_MARK_GUIDE_FAMILY};events=lateral-only;epochs={epochs};projection=frozen-selected-command-to-physical-endpoint-with-future-event-clocks-disabled;proposal=q_j=eps/K+(1-eps)*softmax(beta*enabled-BTO-plus-predictive-BFO-log-likelihood)_j;beta0-or-eps1=skip-projection-equal-valid-candidate-scores;role=proposal-only-exact-auxiliary-correction"
        )
    }
}

/// Optional per-stratum replacement for the global fuel latent ranges.
///
/// This is supplied through an additive model constructor so existing
/// `BroadFlightConfig` literals and the global default remain source compatible.
#[derive(Debug, Clone, Copy, PartialEq, Serialize, Deserialize)]
pub struct BroadStratumFuelUncertaintyOverride {
    pub stratum: StratumId,
    pub fuel_uncertainty: BroadFuelUncertainty,
}

/// Conditional attached-flow performance screen applied to every accepted
/// powered segment. The OpenAP thrust multiplier and static cap are declared
/// model choices, not inferred engine uncertainties.
#[derive(Debug, Clone, Copy, PartialEq, Serialize, Deserialize)]
pub struct BroadPoweredFeasibilityConfig {
    pub aerodynamic_family: ConditionalB772AerodynamicFamily,
    pub thrust_multiplier: f64,
    pub static_thrust_cap_per_engine_n: f64,
    pub maximum_additional_drag_coefficient: f64,
}

/// Runner-independent configuration for filtering ordinary SATCOM epochs.
#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct BroadFlightConfig {
    pub radar_prior: RadarPrior,
    pub initial_vertical_speed_ft_min: BroadUniformRange,
    pub source_fuel: PoweredFuelState,
    pub fuel_uncertainty: BroadFuelUncertainty,
    pub fuel_model: PoweredFuelModel,
    pub fuel_flow_shares: EngineFuelFlowShares,
    pub powered_feasibility: BroadPoweredFeasibilityConfig,
    pub limits: PoweredFlightLimits,
    pub integration: PoweredIntegration,
    /// Exact multiple-try transition proposal count for SATCOM epochs. One is
    /// the bootstrap proposal. Values above one select among independent
    /// prior transitions and return the exact extended-space p/q correction.
    pub proposal_candidates: usize,
    pub satcom: SatcomModelConfig,
    pub strata: Vec<BroadFlightStratum>,
}

impl BroadFlightConfig {
    pub fn validate(&self) -> Result<(), BroadFlightError> {
        self.radar_prior
            .validate()
            .map_err(|_| BroadFlightError::InvalidConfiguration("invalid radar prior"))?;
        self.limits.validate().map_err(BroadFlightError::Dynamics)?;
        self.integration
            .validate()
            .map_err(BroadFlightError::Dynamics)?;
        validate_proposal_candidate_count(self.proposal_candidates)?;
        self.satcom.validate().map_err(BroadFlightError::Satcom)?;
        if !self.initial_vertical_speed_ft_min.validate()
            || !valid_fuel_uncertainty(self.fuel_uncertainty)
            || !valid_fuel_state(self.source_fuel)
            || (self.source_fuel.time.0 - self.radar_prior.time_s).abs() > TIME_TOLERANCE_S
        {
            return Err(BroadFlightError::InvalidConfiguration(
                "invalid initial state or fuel uncertainty",
            ));
        }
        if !self.powered_feasibility.thrust_multiplier.is_finite()
            || self.powered_feasibility.thrust_multiplier <= 0.0
            || !self
                .powered_feasibility
                .static_thrust_cap_per_engine_n
                .is_finite()
            || self.powered_feasibility.static_thrust_cap_per_engine_n <= 0.0
            || !self
                .powered_feasibility
                .maximum_additional_drag_coefficient
                .is_finite()
            || self.powered_feasibility.maximum_additional_drag_coefficient < 0.0
        {
            return Err(BroadFlightError::InvalidConfiguration(
                "invalid powered-segment feasibility configuration",
            ));
        }
        let aerodynamic_model = self.powered_feasibility.aerodynamic_family.model();
        if self.limits.minimum_pressure_altitude_ft
            < OPENAP_B772_TRENT895_MINIMUM_PRESSURE_ALTITUDE_FT
            || self.limits.maximum_pressure_altitude_ft
                > OPENAP_B772_TRENT895_MAXIMUM_PRESSURE_ALTITUDE_FT
            || self.limits.minimum_mach_floor < OPENAP_B772_TRENT895_MINIMUM_MACH
            || self.limits.mmo > OPENAP_B772_TRENT895_MAXIMUM_MACH
            || (self.limits.wing_area_m2 - aerodynamic_model.reference_area.0).abs() > 1.0e-9
            || self.limits.maximum_lift_coefficient > aerodynamic_model.maximum_lift_coefficient
            || self.limits.maximum_bank_deg > aerodynamic_model.maximum_bank_angle.0
        {
            return Err(BroadFlightError::InvalidConfiguration(
                "powered dynamics limits lie outside the selected aerodynamic or thrust proxy domain",
            ));
        }
        if matches!(self.fuel_model, PoweredFuelModel::MartinTrent892Lrc)
            && self.fuel_uncertainty.flow_scale_log_uniform != BroadUniformRange::fixed(1.0)
        {
            return Err(BroadFlightError::InvalidConfiguration(
                "strict Martin fuel does not admit an external flow scale",
            ));
        }
        if !self.fuel_flow_shares.left.is_finite()
            || !self.fuel_flow_shares.right.is_finite()
            || self.fuel_flow_shares.left <= 0.0
            || self.fuel_flow_shares.right <= 0.0
            || (self.fuel_flow_shares.left + self.fuel_flow_shares.right - 1.0).abs() > 1.0e-12
        {
            return Err(BroadFlightError::InvalidConfiguration(
                "invalid engine fuel-flow shares",
            ));
        }
        let mut ids = BTreeSet::new();
        let mut names = BTreeSet::new();
        for stratum in &self.strata {
            if stratum.name.trim().is_empty()
                || !ids.insert(stratum.id)
                || !names.insert(stratum.name.as_str())
            {
                return Err(BroadFlightError::InvalidConfiguration(
                    "strata must have unique non-empty identities",
                ));
            }
            stratum
                .maneuver_process
                .validate(self.limits)
                .map_err(BroadFlightError::Dynamics)?;
        }
        if self.strata.is_empty() {
            return Err(BroadFlightError::InvalidConfiguration(
                "at least one broad-flight stratum is required",
            ));
        }
        Ok(())
    }
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum BroadRejectionReason {
    InitialStateOutsideEnvironment,
    StateOutsideDeclaredEnvelope,
    EnvironmentOutsideDomain,
    MagneticEnvironmentUnavailable,
    MagneticAltitudeOutsideGrid,
    EmptySpeedEnvelope,
    InfeasibleGroundTrack,
    GeodesicPropagation,
    GreatCirclePropagation,
    ComputationalEventLimit,
    MachRateEnvelopeConflict,
    PoweredSegmentInfeasible,
}

#[derive(Debug, Clone, Copy, PartialEq, Serialize, Deserialize)]
#[serde(tag = "status", rename_all = "snake_case")]
pub enum BroadFlightParticleStatus {
    Active,
    Rejected {
        reason: BroadRejectionReason,
        at_time: Seconds,
    },
}

#[derive(Debug, Clone, Copy, PartialEq, Serialize, Deserialize)]
#[serde(tag = "status", rename_all = "snake_case")]
pub enum BroadFuelDiagnosticStatus {
    Valid,
    OutsideModelDomain { at_time: Seconds },
}

/// Aggregate, proposal-only diagnostics carried by a selected lineage.
///
/// These values describe computational allocation only. They are not SATCOM
/// scores and do not enter the scientific evidence ledger.
#[derive(Debug, Clone, Copy, Default, PartialEq, Serialize, Deserialize)]
pub struct BroadSatcomEventMarkGuideDiagnostics {
    pub eligible_lateral_events: u64,
    pub guided_lateral_events: u64,
    pub candidate_marks: u64,
    pub finite_candidate_scores: u64,
    pub materialization_failures: u64,
    pub proxy_projection_successes: u64,
    pub proxy_projection_failures: u64,
    /// Valid candidates scored uniformly without projection because beta is
    /// zero or epsilon is one.
    pub proxy_projection_skipped_candidates: u64,
    pub all_scores_negative_infinity_events: u64,
    pub sum_selection_effective_sample_size: f64,
    pub sum_selection_entropy_nats: f64,
    pub minimum_selected_probability: Option<f64>,
    pub maximum_selected_probability: Option<f64>,
    pub minimum_event_log_prior_over_proposal: Option<f64>,
    pub maximum_event_log_prior_over_proposal: Option<f64>,
    pub minimum_lead_seconds: Option<f64>,
    pub maximum_lead_seconds: Option<f64>,
    /// Sum of `ln(K)` over guided events.
    pub sum_log_candidate_count: f64,
    /// Sum of the normalized log probabilities actually sampled.
    pub sum_selected_log_probability: f64,
    pub cumulative_log_prior_over_proposal: f64,
    /// Sum of configured per-event lower bounds on `ln(p/q)`.
    pub sum_minimum_log_prior_over_proposal: f64,
    /// Sum of configured per-event upper bounds on `ln(p/q)`.
    pub sum_maximum_log_prior_over_proposal: f64,
}

impl BroadSatcomEventMarkGuideDiagnostics {
    fn is_empty(value: &Self) -> bool {
        *value == Self::default()
    }

    fn record_proxy_counts(&mut self, successes: u64, failures: u64, skipped: u64) {
        self.proxy_projection_successes += successes;
        self.proxy_projection_failures += failures;
        self.proxy_projection_skipped_candidates += skipped;
    }

    fn record_event(
        &mut self,
        diagnostic: &PoweredEventProposalDiagnostic,
        endpoint_time: Seconds,
        config: &BroadSatcomEventMarkGuideEpoch,
    ) {
        debug_assert_eq!(diagnostic.kind, PoweredEventKind::Lateral);
        self.eligible_lateral_events += 1;
        self.guided_lateral_events += 1;
        self.candidate_marks += diagnostic.candidate_count as u64;
        self.finite_candidate_scores += diagnostic.finite_score_count as u64;
        self.materialization_failures += diagnostic.materialization_failures as u64;
        self.all_scores_negative_infinity_events +=
            u64::from(diagnostic.all_scores_negative_infinity);
        self.sum_selection_effective_sample_size += diagnostic.selection_effective_sample_size;
        self.sum_selection_entropy_nats += diagnostic.selection_entropy_nats;

        let selected_probability = diagnostic.selected_log_probability.exp();
        update_optional_minimum(&mut self.minimum_selected_probability, selected_probability);
        update_optional_maximum(&mut self.maximum_selected_probability, selected_probability);
        update_optional_minimum(
            &mut self.minimum_event_log_prior_over_proposal,
            diagnostic.log_prior_over_proposal,
        );
        update_optional_maximum(
            &mut self.maximum_event_log_prior_over_proposal,
            diagnostic.log_prior_over_proposal,
        );
        let lead_seconds = endpoint_time.0 - diagnostic.event_time.0;
        update_optional_minimum(&mut self.minimum_lead_seconds, lead_seconds);
        update_optional_maximum(&mut self.maximum_lead_seconds, lead_seconds);

        let log_candidate_count = (diagnostic.candidate_count as f64).ln();
        self.sum_log_candidate_count += log_candidate_count;
        self.sum_selected_log_probability += diagnostic.selected_log_probability;
        self.cumulative_log_prior_over_proposal += diagnostic.log_prior_over_proposal;
        let maximum_selection_probability =
            config.defensive_prior_probability / config.candidates_per_event as f64 + 1.0
                - config.defensive_prior_probability;
        self.sum_minimum_log_prior_over_proposal +=
            -log_candidate_count - maximum_selection_probability.ln();
        self.sum_maximum_log_prior_over_proposal += -config.defensive_prior_probability.ln();
    }
}

fn update_optional_minimum(target: &mut Option<f64>, value: f64) {
    *target = Some(target.map_or(value, |current| current.min(value)));
}

fn update_optional_maximum(target: &mut Option<f64>, value: f64) {
    *target = Some(target.map_or(value, |current| current.max(value)));
}

#[derive(Debug, Clone, Copy, Default, PartialEq, Serialize, Deserialize)]
pub struct BroadFlightDiagnostics {
    pub integration_segments: u64,
    pub steady_segments: u64,
    pub transition_segments: u64,
    pub lateral_events: u64,
    pub speed_events: u64,
    pub altitude_events: u64,
    /// Time spent on each declared powered-flight envelope boundary. This is
    /// preserved separately from rejection status so posterior paths that are
    /// technically feasible but boundary-dominated remain auditable.
    #[serde(default)]
    pub powered_boundary_seconds: PoweredBoundarySeconds,
    /// Accepted integration segments whose target Mach was limited by the
    /// instantaneous stall/minimum-Mach or VMO/MMO envelope.
    #[serde(default)]
    pub powered_target_clamp_count: u64,
    pub magnetic_altitude_clamp_seconds: f64,
    pub fuel_outside_martin_domain_seconds: f64,
    pub fuel_flow_multiplier_bound_hits: u64,
    pub fuel_anchor_count: u32,
    pub powered_segments_screened: u64,
    pub powered_thrust_proxy_extrapolation_segments: u64,
    pub powered_thrust_proxy_cap_segments: u64,
    pub powered_additional_drag_required_segments: u64,
    pub powered_additional_drag_limit_exceeded_segments: u64,
    pub powered_upper_thrust_failure_segments: u64,
    /// New gross mass minus the pre-anchor propagated gross mass. This makes
    /// the conditional reset visible rather than hiding a mass discontinuity.
    pub last_fuel_anchor_mass_adjustment_kg: Option<f64>,
    #[serde(
        default,
        skip_serializing_if = "BroadSatcomEventMarkGuideDiagnostics::is_empty"
    )]
    pub satcom_event_mark_guide: BroadSatcomEventMarkGuideDiagnostics,
    /// Exact conditional renewals of disposable future-event randomness.
    /// These are computational rejuvenation moves, not manoeuvres or evidence.
    #[serde(
        default,
        skip_serializing_if = "BroadPendingRenewalRefreshDiagnostics::is_empty"
    )]
    pub pending_renewal_refresh: BroadPendingRenewalRefreshDiagnostics,
}

#[derive(Debug, Clone, Copy, Default, PartialEq, Serialize, Deserialize)]
pub struct BroadFlightScores {
    pub cumulative_bto_log_likelihood: f64,
    pub cumulative_bfo_log_likelihood: f64,
    pub bto_observations: u32,
    pub bfo_observations: u32,
}

/// Fixed-size marked-jump state. Fuel is carried beside AircraftState and its
/// two uncertainty latents survive resampling for later exhaustion selection.
#[derive(Debug, Clone, Copy, PartialEq, Serialize, Deserialize)]
pub struct BroadFlightState {
    pub stratum: StratumId,
    pub powered_flight: PoweredFlightState,
    pub fuel: PoweredFuelState,
    pub fuel_flow_scale: f64,
    pub fuel_quantity_offset_kg: f64,
    pub bfo_bias: BfoBiasState,
    pub status: BroadFlightParticleStatus,
    pub fuel_status: BroadFuelDiagnosticStatus,
    pub scores: BroadFlightScores,
    pub last_fit: Option<ObservationFit>,
    pub diagnostics: BroadFlightDiagnostics,
}

impl BroadFlightState {
    pub fn is_active(self) -> bool {
        matches!(self.status, BroadFlightParticleStatus::Active)
    }

    pub fn satcom_log_likelihood(self) -> f64 {
        self.scores.cumulative_bto_log_likelihood + self.scores.cumulative_bfo_log_likelihood
    }
}

/// Exact, zero-statistical-likelihood initialization operation. For the
/// primary MH370 branch the caller supplies the official calculated Arc-1
/// total and its stated checkpoint time; this event is not an observation of
/// pre-Arc-1 burn.
#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct BroadFuelAnchorObservation {
    pub id: String,
    pub time: Seconds,
    pub zero_fuel_weight_kg: f64,
    pub total_onboard_fuel_kg: f64,
    pub reserved_fuel_kg: f64,
    pub unusable_fuel_kg: f64,
    pub left_usable_fraction: f64,
}

impl BroadFuelAnchorObservation {
    fn validate(&self) -> Result<(), BroadFlightError> {
        let values = [
            self.time.0,
            self.zero_fuel_weight_kg,
            self.total_onboard_fuel_kg,
            self.reserved_fuel_kg,
            self.unusable_fuel_kg,
            self.left_usable_fraction,
        ];
        if self.id.trim().is_empty()
            || values.iter().any(|value| !value.is_finite())
            || self.zero_fuel_weight_kg <= 0.0
            || self.total_onboard_fuel_kg < 0.0
            || self.reserved_fuel_kg < 0.0
            || self.unusable_fuel_kg < 0.0
            || !(0.0..=1.0).contains(&self.left_usable_fraction)
            || self.reserved_fuel_kg + self.unusable_fuel_kg
                > self.total_onboard_fuel_kg + MASS_TOLERANCE_KG
        {
            return Err(BroadFlightError::InvalidObservation(
                "invalid conditional fuel anchor",
            ));
        }
        Ok(())
    }
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct BroadSatcomObservation {
    pub flight: FlightObservation,
    pub use_bto: bool,
    pub use_bfo: bool,
}

/// Stable identity for the strictly-positive, terminal-tangent SATCOM guide.
/// The guide changes only the computational proposal; the physical endpoint
/// still receives the ordinary exact SATCOM likelihood exactly once.
pub const BROAD_SATCOM_INTERMEDIATE_POTENTIAL_FAMILY: &str =
    "broad-satcom-terminal-tangent-intermediate-potential-v1";

/// Stable identity for the strictly-positive fuel-exhaustion selection guide.
/// The guide allocates proposals only; it is exactly removed by the particle
/// filter and never becomes a fuel, logon, or SATCOM likelihood.
pub const BROAD_FUEL_EXHAUSTION_SELECTION_GUIDE_FAMILY: &str =
    "broad-frozen-fuel-exhaustion-selection-guide-v1";

/// Stable identity for carrying the frozen fuel-exhaustion potential across
/// filtering epochs and removing it once at the declared final epoch.
///
/// This adapter owns no additional scientific equation: it evaluates exactly
/// [`BROAD_FUEL_EXHAUSTION_SELECTION_GUIDE_FAMILY`] through the same typed
/// configuration and point.
pub const BROAD_FUEL_EXHAUSTION_PERSISTENT_TWIST_FAMILY: &str =
    "broad-frozen-fuel-exhaustion-persistent-twist-v1";

/// Computational floor in `delta + (1 - delta) * compatibility`.
///
/// `compatibility` is binary and identifies a frozen-operating-point
/// projection whose dual-engine exhaustion lies strictly inside the supplied
/// time window. The floor must remain positive so the proposal preserves the
/// complete scientific target support.
#[derive(Debug, Clone, Copy, PartialEq, Serialize, Deserialize)]
pub struct BroadFuelExhaustionSelectionGuideConfig {
    pub potential_floor: f64,
}

impl Default for BroadFuelExhaustionSelectionGuideConfig {
    fn default() -> Self {
        Self {
            potential_floor: 0.02,
        }
    }
}

impl BroadFuelExhaustionSelectionGuideConfig {
    pub fn validate(self) -> Result<(), BroadFlightError> {
        if !self.potential_floor.is_finite()
            || self.potential_floor <= 0.0
            || self.potential_floor > 1.0
        {
            return Err(BroadFlightError::InvalidConfiguration(
                "invalid fuel-exhaustion selection-guide floor",
            ));
        }
        Ok(())
    }

    /// Compact deterministic provenance. The realized point carries the exact
    /// window times and is serialized separately by the particle-filter plan.
    pub fn stable_descriptor(self) -> String {
        format!(
            "family={BROAD_FUEL_EXHAUSTION_SELECTION_GUIDE_FAMILY};delta={};projection=frozen-current-operating-point-exact-analytic;compatibility=tau>window-start+{}s-and-tau<window-end-{}s;role=proposal-only-exactly-corrected",
            self.potential_floor,
            FUEL_SELECTION_WINDOW_TOLERANCE_S,
            FUEL_SELECTION_WINDOW_TOLERANCE_S,
        )
    }
}

/// Exact future interval used by one realized selection-guide step.
#[derive(Debug, Clone, Copy, PartialEq, Serialize, Deserialize)]
pub struct BroadFuelExhaustionSelectionGuidePoint {
    pub window_start: Seconds,
    pub window_end: Seconds,
}

impl BroadFuelExhaustionSelectionGuidePoint {
    pub fn validate(self) -> Result<(), BroadFlightError> {
        if !self.window_start.is_finite()
            || !self.window_end.is_finite()
            || self.window_end.0 <= self.window_start.0 + TIME_TOLERANCE_S
        {
            return Err(BroadFlightError::InvalidConfiguration(
                "invalid fuel-exhaustion selection-guide window",
            ));
        }
        Ok(())
    }
}

/// Model-owned classification exposed for proposal diagnostics. None of these
/// outcomes changes the scientific state or evidence ledger.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum BroadFuelExhaustionSelectionGuideOutcome {
    Compatible,
    OutsideWindow,
    NoExhaustionByBound,
    AlreadyExhausted,
    InactiveParticle,
    FuelModelUnavailable,
}

#[derive(Debug, Clone, Copy, PartialEq, Serialize, Deserialize)]
pub struct BroadFuelExhaustionSelectionGuideEvaluation {
    pub outcome: BroadFuelExhaustionSelectionGuideOutcome,
    pub projected_dual_engine_exhaustion_time: Option<Seconds>,
    pub log_selection_guide: f64,
}

/// Pure estimator adapter for the generic exact selection-guide engine.
#[derive(Debug, Clone, Copy, Default, PartialEq)]
pub struct BroadFuelExhaustionSelectionGuide {
    config: BroadFuelExhaustionSelectionGuideConfig,
}

impl BroadFuelExhaustionSelectionGuide {
    pub fn new(config: BroadFuelExhaustionSelectionGuideConfig) -> Result<Self, BroadFlightError> {
        config.validate()?;
        Ok(Self { config })
    }

    pub const fn config(self) -> BroadFuelExhaustionSelectionGuideConfig {
        self.config
    }

    /// Deterministic provenance for the persistent transport of this exact
    /// potential. The realized point supplies the window times separately.
    pub fn persistent_twist_stable_descriptor(self) -> String {
        format!(
            "{};persistent-twist-family={BROAD_FUEL_EXHAUSTION_PERSISTENT_TWIST_FAMILY};persistent-target=physical-filter-times-potential;finalization=single-global-inverse-potential-no-resampling;scientific-evidence=none",
            self.config.stable_descriptor(),
        )
    }
}

/// Declared two-point guide used inside long physical SATCOM intervals.
///
/// With `r` hours remaining until the physical endpoint, the BTO projection
/// standard deviation is
/// `hypot(observation_sd, bto_projection_sd_per_remaining_hour * r)`.
/// The optional late BFO component uses the analogous process scale and also
/// carries the particle's predictive bias variance. `potential_floor` is the
/// strictly-positive mixture floor `delta` in
/// `delta + (1 - delta) * exp(-0.5 * q)`.
#[derive(Debug, Clone, Copy, PartialEq, Serialize, Deserialize)]
pub struct BroadSatcomIntermediatePotentialConfig {
    pub early_offset: Seconds,
    pub late_offset: Seconds,
    pub minimum_interval: Seconds,
    pub early_candidates_per_particle: usize,
    pub late_candidates_per_particle: usize,
    pub potential_floor: f64,
    pub bto_projection_sd_per_remaining_hour: Microseconds,
    pub bfo_projection_sd_per_remaining_hour: Hertz,
}

impl Default for BroadSatcomIntermediatePotentialConfig {
    fn default() -> Self {
        Self {
            early_offset: Seconds(1_800.0),
            late_offset: Seconds(2_940.0),
            minimum_interval: Seconds(3_000.0),
            early_candidates_per_particle: 2,
            late_candidates_per_particle: 4,
            potential_floor: 0.02,
            bto_projection_sd_per_remaining_hour: Microseconds(900.0),
            bfo_projection_sd_per_remaining_hour: Hertz(60.0),
        }
    }
}

impl BroadSatcomIntermediatePotentialConfig {
    pub fn validate(self) -> Result<(), BroadFlightError> {
        if !self.early_offset.is_finite()
            || !self.late_offset.is_finite()
            || !self.minimum_interval.is_finite()
            || self.early_offset.0 <= 0.0
            || self.late_offset.0 <= self.early_offset.0
            || self.minimum_interval.0 <= self.late_offset.0
            || self.early_candidates_per_particle == 0
            || self.late_candidates_per_particle == 0
            || !self.potential_floor.is_finite()
            || !(0.0..=1.0).contains(&self.potential_floor)
            || self.potential_floor == 0.0
            || !self.bto_projection_sd_per_remaining_hour.is_finite()
            || self.bto_projection_sd_per_remaining_hour.0 <= 0.0
            || !self.bfo_projection_sd_per_remaining_hour.is_finite()
            || self.bfo_projection_sd_per_remaining_hour.0 <= 0.0
        {
            return Err(BroadFlightError::InvalidConfiguration(
                "invalid intermediate SATCOM potential configuration",
            ));
        }
        Ok(())
    }

    /// Build the exact per-observation particle-filter step. Only a real BTO
    /// endpoint with enough interior duration is bridged. BFO-only, checkpoint,
    /// fuel-anchor, and short intervals retain the ordinary filter operation.
    pub fn step_for_endpoint(
        self,
        interval_start: Seconds,
        endpoint: &BroadFlightObservation,
    ) -> Result<IntermediatePotentialStep<BroadSatcomIntermediatePotentialPoint>, BroadFlightError>
    {
        self.validate()?;
        endpoint.validate()?;
        if !interval_start.is_finite() || interval_start.0 > endpoint.time().0 + TIME_TOLERANCE_S {
            return Err(BroadFlightError::InvalidObservation(
                "invalid intermediate SATCOM interval start",
            ));
        }
        let BroadFlightObservation::Satcom(satcom) = endpoint else {
            return Ok(IntermediatePotentialStep::Standard);
        };
        if !satcom.use_bto
            || endpoint.time().0 - interval_start.0 + TIME_TOLERANCE_S < self.minimum_interval.0
        {
            return Ok(IntermediatePotentialStep::Standard);
        }
        Ok(IntermediatePotentialStep::Bridge {
            points: vec![
                IntermediatePotentialBridgePoint {
                    point: BroadSatcomIntermediatePotentialPoint {
                        interval_start,
                        time: Seconds(interval_start.0 + self.early_offset.0),
                        kind: BroadSatcomIntermediatePotentialPointKind::EarlyBtoOnly,
                    },
                    candidates_per_particle: self.early_candidates_per_particle,
                },
                IntermediatePotentialBridgePoint {
                    point: BroadSatcomIntermediatePotentialPoint {
                        interval_start,
                        time: Seconds(interval_start.0 + self.late_offset.0),
                        kind: BroadSatcomIntermediatePotentialPointKind::LateEnabledSatcom,
                    },
                    candidates_per_particle: self.late_candidates_per_particle,
                },
            ],
        })
    }

    /// Compact, deterministic provenance descriptor. Serialized configuration
    /// remains the authoritative complete identity.
    pub fn stable_descriptor(self) -> String {
        format!(
            "family={BROAD_SATCOM_INTERMEDIATE_POTENTIAL_FAMILY};minimum-interval={}s;early={}s-k{}-bto;late={}s-k{}-enabled-satcom;delta={};bto-process={}us-per-remaining-hour;bfo-process={}hz-per-remaining-hour;projection=terminal-tangent-wgs84-altitude-clamped",
            self.minimum_interval.0,
            self.early_offset.0,
            self.early_candidates_per_particle,
            self.late_offset.0,
            self.late_candidates_per_particle,
            self.potential_floor,
            self.bto_projection_sd_per_remaining_hour.0,
            self.bfo_projection_sd_per_remaining_hour.0,
        )
    }
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum BroadSatcomIntermediatePotentialPointKind {
    EarlyBtoOnly,
    /// Uses BTO and, only when enabled at the physical endpoint, BFO.
    LateEnabledSatcom,
}

/// Typed scientific description of one guide point. Absolute times are
/// retained so the realized schedule can be recorded without reconstructing
/// it from runner-local assumptions.
#[derive(Debug, Clone, Copy, PartialEq, Serialize, Deserialize)]
pub struct BroadSatcomIntermediatePotentialPoint {
    pub interval_start: Seconds,
    pub time: Seconds,
    pub kind: BroadSatcomIntermediatePotentialPointKind,
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(tag = "kind", rename_all = "snake_case")]
pub enum BroadFlightObservation {
    FuelAnchor(BroadFuelAnchorObservation),
    Satcom(BroadSatcomObservation),
    /// Propagate and retain a state without introducing an observation.
    Checkpoint {
        id: String,
        time: Seconds,
    },
}

impl BroadFlightObservation {
    pub fn id(&self) -> &str {
        match self {
            Self::FuelAnchor(anchor) => &anchor.id,
            Self::Satcom(observation) => &observation.flight.id,
            Self::Checkpoint { id, .. } => id,
        }
    }

    pub fn time(&self) -> Seconds {
        match self {
            Self::FuelAnchor(anchor) => anchor.time,
            Self::Satcom(observation) => observation.flight.measurement.time,
            Self::Checkpoint { time, .. } => *time,
        }
    }

    pub fn validate(&self) -> Result<(), BroadFlightError> {
        if self.id().trim().is_empty() || !self.time().is_finite() {
            return Err(BroadFlightError::InvalidObservation(
                "missing identity or non-finite time",
            ));
        }
        match self {
            Self::FuelAnchor(anchor) => anchor.validate(),
            Self::Satcom(observation) => {
                observation
                    .flight
                    .measurement
                    .validate()
                    .map_err(BroadFlightError::InvalidObservation)?;
                if !observation.use_bto && !observation.use_bfo {
                    return Err(BroadFlightError::InvalidObservation(
                        "SATCOM observation enables neither BTO nor BFO",
                    ));
                }
                if (observation.use_bto && observation.flight.measurement.bto.is_none())
                    || (observation.use_bfo && observation.flight.measurement.bfo.is_none())
                {
                    return Err(BroadFlightError::InvalidObservation(
                        "enabled SATCOM component is absent",
                    ));
                }
                Ok(())
            }
            Self::Checkpoint { .. } => Ok(()),
        }
    }
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct BroadRejectionCounts {
    pub total_particles: usize,
    pub active_particles: usize,
    pub by_reason: BTreeMap<BroadRejectionReason, usize>,
    pub fuel_outside_model_domain: usize,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum BroadDualEngineExhaustionOutcome {
    Exhausted,
    AlreadyExhaustedBeforeStart,
    NoExhaustionByBound,
    TrajectoryRejected,
    FuelModelUnavailable,
}

#[derive(Debug, Clone, Copy, PartialEq, Serialize, Deserialize)]
pub struct BroadDualEngineExhaustionResult {
    pub outcome: BroadDualEngineExhaustionOutcome,
    pub state: BroadFlightState,
    pub target_bound: Seconds,
    pub exhaustion_time: Option<Seconds>,
    pub transition_diagnostics: BroadFlightDiagnostics,
    /// Number of provisional segments discarded and replayed at a fuel event.
    pub exact_boundary_reintegrations: u32,
    pub boundary_events_at_start: PoweredEventCounters,
    pub boundary_events_at_end: PoweredEventCounters,
}

impl BroadRejectionCounts {
    pub fn from_states(states: &[BroadFlightState]) -> Self {
        let mut by_reason = BTreeMap::new();
        let mut active_particles = 0;
        let mut fuel_outside_model_domain = 0;
        for state in states {
            match state.status {
                BroadFlightParticleStatus::Active => active_particles += 1,
                BroadFlightParticleStatus::Rejected { reason, .. } => {
                    *by_reason.entry(reason).or_default() += 1;
                }
            }
            fuel_outside_model_domain += usize::from(matches!(
                state.fuel_status,
                BroadFuelDiagnosticStatus::OutsideModelDomain { .. }
            ));
        }
        Self {
            total_particles: states.len(),
            active_particles,
            by_reason,
            fuel_outside_model_domain,
        }
    }
}

#[derive(Debug, Error)]
pub enum BroadFlightError {
    #[error("invalid broad-flight configuration: {0}")]
    InvalidConfiguration(&'static str),
    #[error("invalid broad-flight observation: {0}")]
    InvalidObservation(&'static str),
    #[error("unknown broad-flight stratum {0:?}")]
    UnknownStratum(StratumId),
    #[error("fuel anchor was applied more than once or away from its declared time")]
    FuelAnchorOrder,
    #[error("powered-flight/fuel time synchronization failed")]
    StateTimeMismatch,
    #[error("state is not valid for exact fuel-exhaustion continuation")]
    InvalidContinuationState,
    #[error("state is not valid for the fuel-exhaustion selection guide")]
    InvalidFuelSelectionGuideState,
    #[error("state is not valid for pending-renewal refresh: {0}")]
    InvalidPendingRenewalRefreshState(&'static str),
    #[error("fuel exhaustion did not reproduce at the exact reintegrated boundary")]
    FuelBoundaryMismatch,
    #[error(transparent)]
    Dynamics(#[from] PoweredFlightError),
    #[error(transparent)]
    PendingRenewalRefresh(#[from] PoweredRenewalRefreshError),
    #[error(transparent)]
    Fuel(#[from] PoweredFuelError),
    #[error(transparent)]
    FrozenFuelProjection(#[from] FrozenPoweredFuelProjectionError),
    #[error(transparent)]
    PoweredFeasibility(#[from] PoweredSegmentFeasibilityError),
    #[error(transparent)]
    PoweredOperationalFeasibility(#[from] PoweredSegmentOperationalFeasibilityError),
    #[error(transparent)]
    ThrustCeiling(#[from] OpenapB772Trent895CruiseThrustError),
    #[error(transparent)]
    Satcom(#[from] SatcomModelError),
}

pub struct BroadFlightModel<'a> {
    config: BroadFlightConfig,
    environment: PoweredFlightEnvironment<'a>,
    stratum_fuel_uncertainty_overrides: BTreeMap<StratumId, BroadFuelUncertainty>,
    fuel_flow_initialization_design: BroadFuelFlowInitializationDesign,
    proposal_candidate_schedule: BroadProposalCandidateSchedule,
    satcom_event_mark_guide: Option<BroadSatcomEventMarkGuideConfig>,
}

/// Additive computational options for broad-flight model construction.
/// Defaults reproduce [`BroadFlightModel::new`] exactly.
#[derive(Debug, Clone, Default, PartialEq, Serialize, Deserialize)]
pub struct BroadFlightModelOptions {
    pub stratum_fuel_uncertainty_overrides: Vec<BroadStratumFuelUncertaintyOverride>,
    pub fuel_flow_initialization_design: BroadFuelFlowInitializationDesign,
    pub proposal_candidate_schedule: BroadProposalCandidateSchedule,
    #[serde(default)]
    pub satcom_event_mark_guide: Option<BroadSatcomEventMarkGuideConfig>,
}

#[derive(Debug, Error)]
enum BroadSatcomEventMarkScorerError {
    #[error("event-mark scorer received an inconsistent candidate")]
    InconsistentCandidate,
    #[error("event-mark proxy projection failed: {0}")]
    Projection(#[source] PoweredFlightError),
    #[error(transparent)]
    Satcom(#[from] SatcomModelError),
}

struct BroadSatcomEventMarkScorer<'model, 'environment, 'observation> {
    model: &'model BroadFlightModel<'environment>,
    observation: &'observation BroadSatcomObservation,
    epoch: &'observation BroadSatcomEventMarkGuideEpoch,
    process: ManeuverProcess,
    gross_mass_kg: f64,
    bfo_bias: BfoBiasState,
    proxy_counts_by_event: Mutex<BTreeMap<(u8, u64), BroadEventMarkProxyCounts>>,
}

#[derive(Debug, Clone, Copy, Default, PartialEq, Eq)]
struct BroadEventMarkProxyCounts {
    successes: u64,
    failures: u64,
    skipped: u64,
}

impl BroadEventMarkProxyCounts {
    fn add(&mut self, other: Self) {
        self.successes += other.successes;
        self.failures += other.failures;
        self.skipped += other.skipped;
    }

    const fn tuple(self) -> (u64, u64, u64) {
        (self.successes, self.failures, self.skipped)
    }
}

const fn event_proxy_count_key(kind: PoweredEventKind, event_number: u64) -> (u8, u64) {
    let kind_key = match kind {
        PoweredEventKind::Lateral => 0,
        PoweredEventKind::Speed => 1,
        PoweredEventKind::Altitude => 2,
    };
    (kind_key, event_number)
}

impl BroadSatcomEventMarkScorer<'_, '_, '_> {
    fn update_proxy_counts(
        &self,
        event: PoweredEventProposalEvent,
        update: impl FnOnce(&mut BroadEventMarkProxyCounts),
    ) {
        let mut counts = self
            .proxy_counts_by_event
            .lock()
            .unwrap_or_else(|poisoned| poisoned.into_inner());
        update(
            counts
                .entry(event_proxy_count_key(event.kind, event.event_number))
                .or_default(),
        );
    }

    fn proxy_counts_for_event(
        &self,
        kind: PoweredEventKind,
        event_number: u64,
    ) -> BroadEventMarkProxyCounts {
        self.proxy_counts_by_event
            .lock()
            .unwrap_or_else(|poisoned| poisoned.into_inner())
            .get(&event_proxy_count_key(kind, event_number))
            .copied()
            .unwrap_or_default()
    }

    fn proxy_counts_for_diagnostics(
        &self,
        diagnostics: &[PoweredEventProposalDiagnostic],
    ) -> BroadEventMarkProxyCounts {
        let counts = self
            .proxy_counts_by_event
            .lock()
            .unwrap_or_else(|poisoned| poisoned.into_inner());
        let mut seen = BTreeSet::new();
        let mut total = BroadEventMarkProxyCounts::default();
        for diagnostic in diagnostics {
            let key = event_proxy_count_key(diagnostic.kind, diagnostic.event_number);
            if !seen.insert(key) {
                debug_assert!(false, "duplicate powered-event proposal diagnostic key");
                continue;
            }
            total.add(counts.get(&key).copied().unwrap_or_default());
        }
        total
    }

    #[cfg(test)]
    fn proxy_counts(&self) -> (u64, u64, u64) {
        let counts = self
            .proxy_counts_by_event
            .lock()
            .unwrap_or_else(|poisoned| poisoned.into_inner());
        let mut total = BroadEventMarkProxyCounts::default();
        for event_counts in counts.values() {
            total.add(*event_counts);
        }
        total.tuple()
    }
}

impl PoweredEventCandidateScorer for BroadSatcomEventMarkScorer<'_, '_, '_> {
    type Error = BroadSatcomEventMarkScorerError;

    fn is_eligible(&self, event: &PoweredEventProposalEvent) -> Result<bool, Self::Error> {
        let remaining_seconds =
            self.observation.flight.measurement.time.0 - event.before.aircraft.time.0;
        Ok(event.kind == PoweredEventKind::Lateral
            && remaining_seconds >= self.epoch.minimum_lead.0
            && remaining_seconds <= self.epoch.maximum_lookback.0)
    }

    fn log_score(&self, candidate: &PoweredEventProposalCandidate) -> Result<f64, Self::Error> {
        if candidate.event.kind != PoweredEventKind::Lateral
            || candidate.after_mark.aircraft.time != candidate.event.before.aircraft.time
        {
            return Err(BroadSatcomEventMarkScorerError::InconsistentCandidate);
        }
        if self.epoch.score_temperature == 0.0 || self.epoch.defensive_prior_probability == 1.0 {
            self.update_proxy_counts(candidate.event, |counts| counts.skipped += 1);
            return Ok(0.0);
        }
        let projected = match self.model.frozen_command_satcom_proxy(
            candidate.after_mark,
            self.process,
            self.gross_mass_kg,
            self.observation.flight.measurement.time,
        ) {
            Ok(projected) => {
                self.update_proxy_counts(candidate.event, |counts| counts.successes += 1);
                projected
            }
            Err(error) if routine_rejection_reason(&error).is_some() => {
                self.update_proxy_counts(candidate.event, |counts| counts.failures += 1);
                return Ok(f64::NEG_INFINITY);
            }
            Err(error) => return Err(BroadSatcomEventMarkScorerError::Projection(error)),
        };
        let log_score =
            self.model
                .satcom_proxy_log_likelihood(projected, self.bfo_bias, self.observation)?;
        Ok(self.epoch.score_temperature * log_score)
    }
}

impl<'a> BroadFlightModel<'a> {
    pub fn new(
        config: BroadFlightConfig,
        environment: PoweredFlightEnvironment<'a>,
    ) -> Result<Self, BroadFlightError> {
        Self::new_with_options(config, environment, BroadFlightModelOptions::default())
    }

    pub fn new_with_stratum_fuel_uncertainty_overrides(
        config: BroadFlightConfig,
        environment: PoweredFlightEnvironment<'a>,
        overrides: Vec<BroadStratumFuelUncertaintyOverride>,
    ) -> Result<Self, BroadFlightError> {
        Self::new_with_options(
            config,
            environment,
            BroadFlightModelOptions {
                stratum_fuel_uncertainty_overrides: overrides,
                ..BroadFlightModelOptions::default()
            },
        )
    }

    /// Construct the model with an explicit continuous fuel-flow
    /// initialization design. The declared fuel prior is unchanged.
    pub fn new_with_fuel_flow_initialization_design(
        config: BroadFlightConfig,
        environment: PoweredFlightEnvironment<'a>,
        design: BroadFuelFlowInitializationDesign,
    ) -> Result<Self, BroadFlightError> {
        Self::new_with_options(
            config,
            environment,
            BroadFlightModelOptions {
                fuel_flow_initialization_design: design,
                ..BroadFlightModelOptions::default()
            },
        )
    }

    pub fn new_with_options(
        config: BroadFlightConfig,
        environment: PoweredFlightEnvironment<'a>,
        options: BroadFlightModelOptions,
    ) -> Result<Self, BroadFlightError> {
        config.validate()?;
        options
            .proposal_candidate_schedule
            .validate_with_baseline_candidates(config.proposal_candidates)?;
        if let Some(event_mark_guide) = &options.satcom_event_mark_guide {
            event_mark_guide.validate()?;
            if config.proposal_candidates != 1
                || !matches!(
                    &options.proposal_candidate_schedule,
                    BroadProposalCandidateSchedule::Constant
                )
            {
                return Err(BroadFlightError::InvalidConfiguration(
                    "SATCOM event-mark guide requires constant model-local proposal count one",
                ));
            }
        }
        let mut stratum_fuel_uncertainty_overrides = BTreeMap::new();
        for fuel_override in options.stratum_fuel_uncertainty_overrides {
            if !config
                .strata
                .iter()
                .any(|stratum| stratum.id == fuel_override.stratum)
                || !valid_fuel_uncertainty(fuel_override.fuel_uncertainty)
                || (matches!(config.fuel_model, PoweredFuelModel::MartinTrent892Lrc)
                    && fuel_override.fuel_uncertainty.flow_scale_log_uniform
                        != BroadUniformRange::fixed(1.0))
                || stratum_fuel_uncertainty_overrides
                    .insert(fuel_override.stratum, fuel_override.fuel_uncertainty)
                    .is_some()
            {
                return Err(BroadFlightError::InvalidConfiguration(
                    "invalid or duplicate stratum fuel-uncertainty override",
                ));
            }
        }
        Ok(Self {
            config,
            environment,
            stratum_fuel_uncertainty_overrides,
            fuel_flow_initialization_design: options.fuel_flow_initialization_design,
            proposal_candidate_schedule: options.proposal_candidate_schedule,
            satcom_event_mark_guide: options.satcom_event_mark_guide,
        })
    }

    pub fn config(&self) -> &BroadFlightConfig {
        &self.config
    }

    pub fn fuel_uncertainty_for_stratum(
        &self,
        stratum: StratumId,
    ) -> Result<BroadFuelUncertainty, BroadFlightError> {
        self.stratum(stratum)?;
        Ok(self
            .stratum_fuel_uncertainty_overrides
            .get(&stratum)
            .copied()
            .unwrap_or(self.config.fuel_uncertainty))
    }

    pub fn stratum_fuel_uncertainty_overrides(&self) -> &BTreeMap<StratumId, BroadFuelUncertainty> {
        &self.stratum_fuel_uncertainty_overrides
    }

    pub const fn fuel_flow_initialization_design(&self) -> BroadFuelFlowInitializationDesign {
        self.fuel_flow_initialization_design
    }

    pub fn proposal_candidate_schedule(&self) -> &BroadProposalCandidateSchedule {
        &self.proposal_candidate_schedule
    }

    pub fn satcom_event_mark_guide(&self) -> Option<&BroadSatcomEventMarkGuideConfig> {
        self.satcom_event_mark_guide.as_ref()
    }

    fn frozen_command_satcom_proxy(
        &self,
        mut powered_flight: PoweredFlightState,
        process: ManeuverProcess,
        gross_mass_kg: f64,
        endpoint_time: Seconds,
    ) -> Result<AircraftState, PoweredFlightError> {
        powered_flight.event_clocks = PoweredEventClocks {
            lateral: None,
            speed: None,
            altitude: None,
        };
        let no_future_events = ManeuverProcess {
            lateral_clock: None,
            speed_clock: None,
            altitude_clock: None,
            ..process
        };
        // No event clock is present, so this RNG is never consumed. It is
        // deliberately separate from both the physical and proposal streams.
        let mut proxy_rng = ChaCha8Rng::from_seed([0x53; 32]);
        propagate_powered_flight(
            powered_flight,
            endpoint_time.0,
            self.config.limits,
            no_future_events,
            self.config.integration,
            self.environment,
            gross_mass_kg,
            &mut proxy_rng,
        )
        .map(|transition| transition.state.aircraft)
    }

    fn satcom_proxy_log_likelihood(
        &self,
        aircraft: AircraftState,
        mut bias: BfoBiasState,
        observation: &BroadSatcomObservation,
    ) -> Result<f64, SatcomModelError> {
        let mut measurement = observation.flight.measurement.clone();
        if !observation.use_bto {
            measurement.bto = None;
            measurement.bto_sd = None;
        }
        if !observation.use_bfo {
            measurement.bfo = None;
            measurement.bfo_sd = None;
        }
        evaluate_observation(
            aircraft,
            &mut bias,
            &measurement,
            observation.flight.satellite_afc_hz,
            observation.use_bfo,
            &self.config.satcom,
        )
        .map(|fit| fit.log_likelihood)
    }

    /// Proposal candidates actually used for this operation. Non-SATCOM
    /// operations always use one prior transition and do not invoke the
    /// multiple-try selector.
    pub fn proposal_candidates_for_observation(
        &self,
        observation: &BroadFlightObservation,
        elapsed_seconds: f64,
    ) -> usize {
        if matches!(observation, BroadFlightObservation::Satcom(_)) {
            self.proposal_candidate_schedule
                .candidates_for_elapsed_seconds(self.config.proposal_candidates, elapsed_seconds)
        } else {
            1
        }
    }

    pub fn propagate_without_observation(
        &self,
        state: &BroadFlightState,
        target_time: Seconds,
        rng: &mut ChaCha8Rng,
    ) -> Result<BroadFlightState, BroadFlightError> {
        let mut next = *state;
        self.propagate_state(&mut next, target_time.0, rng)?;
        Ok(next)
    }

    /// Continue a valid filtering state to the exact dual-engine fuel boundary.
    ///
    /// Unlike filtering propagation, this method treats fuel availability as a
    /// transition boundary. If a provisional dynamics segment spans exhaustion,
    /// it restores both the pre-segment state and RNG, then repeats the segment
    /// only to the fuel model's exact event timestamp.
    pub fn continue_to_exact_dual_engine_exhaustion(
        &self,
        initial: &BroadFlightState,
        target_bound: Seconds,
        rng: &mut ChaCha8Rng,
    ) -> Result<BroadDualEngineExhaustionResult, BroadFlightError> {
        if !initial.is_active()
            || !matches!(initial.fuel_status, BroadFuelDiagnosticStatus::Valid)
            || !target_bound.is_finite()
            || target_bound.0 < initial.powered_flight.aircraft.time.0 - TIME_TOLERANCE_S
            || (initial.powered_flight.aircraft.time.0 - initial.fuel.time.0).abs()
                > TIME_TOLERANCE_S
            || (initial.fuel.left_usable_feed.0 <= MASS_TOLERANCE_KG
                && initial.fuel.left_exhaustion_time.is_none())
            || (initial.fuel.right_usable_feed.0 <= MASS_TOLERANCE_KG
                && initial.fuel.right_exhaustion_time.is_none())
        {
            return Err(BroadFlightError::InvalidContinuationState);
        }
        if let Some(exhaustion_time) = initial.fuel.dual_engine_exhaustion_time {
            return Ok(BroadDualEngineExhaustionResult {
                outcome: if (exhaustion_time.0 - initial.fuel.time.0).abs() <= TIME_TOLERANCE_S {
                    BroadDualEngineExhaustionOutcome::Exhausted
                } else {
                    BroadDualEngineExhaustionOutcome::AlreadyExhaustedBeforeStart
                },
                state: *initial,
                target_bound,
                exhaustion_time: Some(exhaustion_time),
                transition_diagnostics: BroadFlightDiagnostics::default(),
                exact_boundary_reintegrations: 0,
                boundary_events_at_start: PoweredEventCounters::default(),
                boundary_events_at_end: PoweredEventCounters::default(),
            });
        }

        let process = self.stratum(initial.stratum)?.maneuver_process;
        let mut state = *initial;
        let mut transition_diagnostics = BroadFlightDiagnostics::default();
        let mut event_budget =
            PoweredEventBudget::new(self.config.integration.maximum_events_per_transition)?;
        let mut exact_boundary_reintegrations = 0;
        let mut last_events_at_start = PoweredEventCounters::default();
        let mut last_events_at_end = PoweredEventCounters::default();

        while state.powered_flight.aircraft.time.0 < target_bound.0 - TIME_TOLERANCE_S {
            let pre_state = state;
            let pre_rng = rng.clone();
            let pre_budget = event_budget;
            let segment = match advance_powered_flight_step_with_budget(
                pre_state.powered_flight,
                target_bound.0,
                self.config.limits,
                process,
                self.config.integration,
                self.environment,
                pre_state.fuel.gross_mass().0,
                &mut event_budget,
                rng,
            ) {
                Ok(Some(segment)) => segment,
                Ok(None) => return Err(BroadFlightError::StateTimeMismatch),
                Err(error) => {
                    if let Some(reason) = routine_rejection_reason(&error) {
                        state.status = BroadFlightParticleStatus::Rejected {
                            reason,
                            at_time: pre_state.powered_flight.aircraft.time,
                        };
                        return Ok(exhaustion_result(
                            BroadDualEngineExhaustionOutcome::TrajectoryRejected,
                            state,
                            target_bound,
                            transition_diagnostics,
                            exact_boundary_reintegrations,
                            last_events_at_start,
                            last_events_at_end,
                        ));
                    }
                    return Err(error.into());
                }
            };
            let mut provisional_fuel = pre_state.fuel;
            let fuel_step = match advance_powered_fuel(
                &mut provisional_fuel,
                scaled_fuel_model(self.config.fuel_model, pre_state.fuel_flow_scale),
                self.config.fuel_flow_shares,
                fuel_input(segment),
            ) {
                Ok(step) => step,
                Err(PoweredFuelError::OutsideModelDomain) => {
                    state = pre_state;
                    state.fuel_status = BroadFuelDiagnosticStatus::OutsideModelDomain {
                        at_time: pre_state.powered_flight.aircraft.time,
                    };
                    return Ok(exhaustion_result(
                        BroadDualEngineExhaustionOutcome::FuelModelUnavailable,
                        state,
                        target_bound,
                        transition_diagnostics,
                        exact_boundary_reintegrations,
                        last_events_at_start,
                        last_events_at_end,
                    ));
                }
                Err(error) => return Err(error.into()),
            };
            if let Some(exhaustion_time) =
                earliest_new_engine_exhaustion(pre_state.fuel, provisional_fuel)
            {
                if exhaustion_time.0 < segment.end.aircraft.time.0 - TIME_TOLERANCE_S {
                    *rng = pre_rng;
                    event_budget = pre_budget;
                    let exact_segment = match advance_powered_flight_step_with_budget(
                        pre_state.powered_flight,
                        exhaustion_time.0,
                        self.config.limits,
                        process,
                        self.config.integration,
                        self.environment,
                        pre_state.fuel.gross_mass().0,
                        &mut event_budget,
                        rng,
                    ) {
                        Ok(Some(segment)) => segment,
                        Ok(None) => return Err(BroadFlightError::FuelBoundaryMismatch),
                        Err(error) => {
                            if let Some(reason) = routine_rejection_reason(&error) {
                                state = pre_state;
                                state.status = BroadFlightParticleStatus::Rejected {
                                    reason,
                                    at_time: pre_state.powered_flight.aircraft.time,
                                };
                                return Ok(exhaustion_result(
                                    BroadDualEngineExhaustionOutcome::TrajectoryRejected,
                                    state,
                                    target_bound,
                                    transition_diagnostics,
                                    exact_boundary_reintegrations,
                                    last_events_at_start,
                                    last_events_at_end,
                                ));
                            }
                            return Err(error.into());
                        }
                    };
                    let mut exact_fuel = pre_state.fuel;
                    let exact_step = match advance_powered_fuel(
                        &mut exact_fuel,
                        scaled_fuel_model(self.config.fuel_model, pre_state.fuel_flow_scale),
                        self.config.fuel_flow_shares,
                        fuel_input(exact_segment),
                    ) {
                        Ok(step) => step,
                        Err(PoweredFuelError::OutsideModelDomain) => {
                            state = pre_state;
                            state.fuel_status = BroadFuelDiagnosticStatus::OutsideModelDomain {
                                at_time: pre_state.powered_flight.aircraft.time,
                            };
                            return Ok(exhaustion_result(
                                BroadDualEngineExhaustionOutcome::FuelModelUnavailable,
                                state,
                                target_bound,
                                transition_diagnostics,
                                exact_boundary_reintegrations,
                                last_events_at_start,
                                last_events_at_end,
                            ));
                        }
                        Err(error) => return Err(error.into()),
                    };
                    let reproduced_time =
                        earliest_new_engine_exhaustion(pre_state.fuel, exact_fuel)
                            .ok_or(BroadFlightError::FuelBoundaryMismatch)?;
                    if (reproduced_time.0 - exhaustion_time.0).abs() > TIME_TOLERANCE_S
                        || (exact_segment.end.aircraft.time.0 - exhaustion_time.0).abs()
                            > TIME_TOLERANCE_S
                    {
                        return Err(BroadFlightError::FuelBoundaryMismatch);
                    }
                    let performance = self.evaluate_segment_feasibility_with_conditions(
                        &exact_segment,
                        operating_engine_count(pre_state.fuel),
                        midpoint_fuel_mass(&exact_step),
                    )?;
                    if !performance.2.flags.operationally_feasible {
                        state = pre_state;
                        state.status = BroadFlightParticleStatus::Rejected {
                            reason: BroadRejectionReason::PoweredSegmentInfeasible,
                            at_time: exact_segment.start.aircraft.time,
                        };
                        return Ok(exhaustion_result(
                            BroadDualEngineExhaustionOutcome::TrajectoryRejected,
                            state,
                            target_bound,
                            transition_diagnostics,
                            exact_boundary_reintegrations,
                            last_events_at_start,
                            last_events_at_end,
                        ));
                    }
                    state.powered_flight = exact_segment.end;
                    state.fuel = exact_fuel;
                    accumulate_coupled_diagnostics(
                        &mut state.diagnostics,
                        &exact_segment,
                        &exact_step,
                    );
                    accumulate_coupled_diagnostics(
                        &mut transition_diagnostics,
                        &exact_segment,
                        &exact_step,
                    );
                    accumulate_performance_diagnostics(
                        &mut state.diagnostics,
                        performance.1,
                        performance.2,
                    );
                    accumulate_performance_diagnostics(
                        &mut transition_diagnostics,
                        performance.1,
                        performance.2,
                    );
                    exact_boundary_reintegrations += 1;
                    last_events_at_start = exact_segment.events_at_start;
                    last_events_at_end = exact_segment.events_at_end;
                    if state.fuel.dual_engine_exhaustion_time.is_some() {
                        return Ok(exhaustion_result(
                            BroadDualEngineExhaustionOutcome::Exhausted,
                            state,
                            target_bound,
                            transition_diagnostics,
                            exact_boundary_reintegrations,
                            last_events_at_start,
                            last_events_at_end,
                        ));
                    }
                    continue;
                }
            }

            let performance = self.evaluate_segment_feasibility_with_conditions(
                &segment,
                operating_engine_count(pre_state.fuel),
                midpoint_fuel_mass(&fuel_step),
            )?;
            if !performance.2.flags.operationally_feasible {
                state = pre_state;
                state.status = BroadFlightParticleStatus::Rejected {
                    reason: BroadRejectionReason::PoweredSegmentInfeasible,
                    at_time: segment.start.aircraft.time,
                };
                return Ok(exhaustion_result(
                    BroadDualEngineExhaustionOutcome::TrajectoryRejected,
                    state,
                    target_bound,
                    transition_diagnostics,
                    exact_boundary_reintegrations,
                    last_events_at_start,
                    last_events_at_end,
                ));
            }
            state.powered_flight = segment.end;
            state.fuel = provisional_fuel;
            accumulate_coupled_diagnostics(&mut state.diagnostics, &segment, &fuel_step);
            accumulate_coupled_diagnostics(&mut transition_diagnostics, &segment, &fuel_step);
            accumulate_performance_diagnostics(
                &mut state.diagnostics,
                performance.1,
                performance.2,
            );
            accumulate_performance_diagnostics(
                &mut transition_diagnostics,
                performance.1,
                performance.2,
            );
            last_events_at_start = segment.events_at_start;
            last_events_at_end = segment.events_at_end;
            if state.fuel.dual_engine_exhaustion_time.is_some() {
                return Ok(exhaustion_result(
                    BroadDualEngineExhaustionOutcome::Exhausted,
                    state,
                    target_bound,
                    transition_diagnostics,
                    exact_boundary_reintegrations,
                    last_events_at_start,
                    last_events_at_end,
                ));
            }
        }
        Ok(exhaustion_result(
            BroadDualEngineExhaustionOutcome::NoExhaustionByBound,
            state,
            target_bound,
            transition_diagnostics,
            exact_boundary_reintegrations,
            last_events_at_start,
            last_events_at_end,
        ))
    }

    fn stratum(&self, id: StratumId) -> Result<&BroadFlightStratum, BroadFlightError> {
        self.config
            .strata
            .iter()
            .find(|stratum| stratum.id == id)
            .ok_or(BroadFlightError::UnknownStratum(id))
    }

    fn initialize_for_stratum(
        &self,
        stratum: StratumId,
        rng: &mut ChaCha8Rng,
    ) -> Result<BroadFlightState, BroadFlightError> {
        self.initialize_for_stratum_cell(stratum, 0, 1, rng)
    }

    fn initialize_for_stratum_cell(
        &self,
        stratum: StratumId,
        particle_index_within_stratum: usize,
        particles_in_stratum: usize,
        rng: &mut ChaCha8Rng,
    ) -> Result<BroadFlightState, BroadFlightError> {
        let stratum_config = self.stratum(stratum)?;
        let radar = self.config.radar_prior;
        let normal_north: f64 = StandardNormal.sample(rng);
        let normal_east: f64 = StandardNormal.sample(rng);
        let normal_track: f64 = StandardNormal.sample(rng);
        let north_nm = radar.position_sd_nm * normal_north;
        let east_nm = radar.position_sd_nm * normal_east;
        let latitude_deg = radar.latitude_deg + north_nm / 60.0;
        let longitude_scale = 60.0 * radar.latitude_deg.to_radians().cos();
        if longitude_scale.abs() < 1.0e-8 {
            return Err(BroadFlightError::InvalidConfiguration(
                "radar prior is too close to a pole",
            ));
        }
        let position = match LatLon::new(
            latitude_deg,
            radar.longitude_deg + east_nm / longitude_scale,
        ) {
            Ok(position) => position,
            Err(_) => LatLon::new(radar.latitude_deg, radar.longitude_deg)
                .map_err(|_| BroadFlightError::InvalidConfiguration("invalid radar position"))?,
        };
        let track = Degrees(radar.control_mean_deg_true + radar.control_sd_deg * normal_track)
            .wrapped_360();
        let mach = BroadUniformRange {
            minimum: radar.mach_min,
            maximum: radar.mach_max,
        }
        .sample(rng);
        let altitude = BroadUniformRange {
            minimum: radar.altitude_min_ft,
            maximum: radar.altitude_max_ft,
        }
        .sample(rng);
        let vertical_speed = self.config.initial_vertical_speed_ft_min.sample(rng);
        let bfo_bias = self.config.satcom.initial_bias();
        let aircraft = AircraftState {
            time: Seconds(radar.time_s),
            position,
            altitude: Feet(altitude),
            track_true: track,
            ground_speed: Knots(1.0),
            vertical_speed: FeetPerMinute(vertical_speed),
            bfo_bias: Hertz(bfo_bias.mean_hz),
        };
        let fuel_uncertainty = self.fuel_uncertainty_for_stratum(stratum)?;
        let fuel_flow_scale = match self.fuel_flow_initialization_design {
            BroadFuelFlowInitializationDesign::IndependentLogUniform => fuel_uncertainty
                .flow_scale_log_uniform
                .sample_log_uniform(rng),
            BroadFuelFlowInitializationDesign::LogSpaceLatinHypercube => {
                sample_log_space_latin_hypercube(
                    fuel_uncertainty.flow_scale_log_uniform,
                    stratum,
                    particle_index_within_stratum,
                    particles_in_stratum,
                )?
            }
        };
        let fuel_quantity_offset_kg = fuel_uncertainty.total_quantity_offset_kg.sample(rng);
        let fuel = self.config.source_fuel;
        let initialized = initialize_powered_flight(
            aircraft,
            mach,
            stratum_config.initial_lateral_mode,
            self.config.limits,
            stratum_config.maneuver_process,
            self.environment,
            fuel.gross_mass().0,
            rng,
        );
        let (powered_flight, status) = match initialized {
            Ok(state) => (state, BroadFlightParticleStatus::Active),
            Err(error) => match routine_rejection_reason(&error) {
                Some(reason) => (
                    fallback_powered_state(aircraft, mach),
                    BroadFlightParticleStatus::Rejected {
                        reason,
                        at_time: aircraft.time,
                    },
                ),
                None => return Err(error.into()),
            },
        };
        Ok(BroadFlightState {
            stratum,
            powered_flight,
            fuel,
            fuel_flow_scale,
            fuel_quantity_offset_kg,
            bfo_bias,
            status,
            fuel_status: BroadFuelDiagnosticStatus::Valid,
            scores: BroadFlightScores::default(),
            last_fit: None,
            diagnostics: BroadFlightDiagnostics::default(),
        })
    }

    fn propagate_state(
        &self,
        state: &mut BroadFlightState,
        target_time_s: f64,
        rng: &mut ChaCha8Rng,
    ) -> Result<(), BroadFlightError> {
        let mut event_budget =
            PoweredEventBudget::new(self.config.integration.maximum_events_per_transition)?;
        self.propagate_state_with_budget(state, target_time_s, &mut event_budget, rng)
    }

    /// Internal split-transition primitive. A bridge retains one budget and
    /// passes it to every subdivision; ordinary propagation creates one fresh
    /// budget for the complete observation interval above.
    fn propagate_state_with_budget(
        &self,
        state: &mut BroadFlightState,
        target_time_s: f64,
        event_budget: &mut PoweredEventBudget,
        rng: &mut ChaCha8Rng,
    ) -> Result<(), BroadFlightError> {
        if !target_time_s.is_finite()
            || target_time_s < state.powered_flight.aircraft.time.0 - TIME_TOLERANCE_S
        {
            return Err(BroadFlightError::InvalidObservation(
                "target time precedes particle state",
            ));
        }
        if event_budget.maximum_events != self.config.integration.maximum_events_per_transition {
            return Err(BroadFlightError::InvalidConfiguration(
                "split transition event budget does not match model configuration",
            ));
        }
        if !state.is_active() {
            return Ok(());
        }
        let process = self.stratum(state.stratum)?.maneuver_process;
        while state.powered_flight.aircraft.time.0 < target_time_s - TIME_TOLERANCE_S {
            let segment = match advance_powered_flight_step_with_budget(
                state.powered_flight,
                target_time_s,
                self.config.limits,
                process,
                self.config.integration,
                self.environment,
                state.fuel.gross_mass().0,
                event_budget,
                rng,
            ) {
                Ok(Some(segment)) => segment,
                Ok(None) => return Err(BroadFlightError::StateTimeMismatch),
                Err(error) => {
                    if let Some(reason) = routine_rejection_reason(&error) {
                        state.status = BroadFlightParticleStatus::Rejected {
                            reason,
                            at_time: state.powered_flight.aircraft.time,
                        };
                        return Ok(());
                    }
                    return Err(error.into());
                }
            };
            if !self.accept_powered_segment(state, &segment)? {
                return Ok(());
            }
        }
        Ok(())
    }

    fn propagate_state_with_satcom_event_mark_guide(
        &self,
        state: &mut BroadFlightState,
        observation: &BroadSatcomObservation,
        epoch: &BroadSatcomEventMarkGuideEpoch,
        event_budget: &mut PoweredEventBudget,
        rng: &mut ChaCha8Rng,
    ) -> Result<f64, BroadFlightError> {
        let target_time_s = observation.flight.measurement.time.0;
        if !target_time_s.is_finite()
            || target_time_s < state.powered_flight.aircraft.time.0 - TIME_TOLERANCE_S
        {
            return Err(BroadFlightError::InvalidObservation(
                "event-mark guide target time precedes particle state",
            ));
        }
        if event_budget.maximum_events != self.config.integration.maximum_events_per_transition {
            return Err(BroadFlightError::InvalidConfiguration(
                "event-mark guide budget does not match model configuration",
            ));
        }
        if !state.is_active() {
            return Ok(0.0);
        }
        let process = self.stratum(state.stratum)?.maneuver_process;
        let proposal_rng = PoweredEventProposalRng::from_rng(rng);
        let mut log_prior_over_proposal = 0.0;
        while state.powered_flight.aircraft.time.0 < target_time_s - TIME_TOLERANCE_S {
            let scorer = BroadSatcomEventMarkScorer {
                model: self,
                observation,
                epoch,
                process,
                gross_mass_kg: state.fuel.gross_mass().0,
                bfo_bias: state.bfo_bias,
                proxy_counts_by_event: Mutex::new(BTreeMap::new()),
            };
            let proposed = advance_powered_flight_step_with_budget_and_event_proposal(
                state.powered_flight,
                target_time_s,
                self.config.limits,
                process,
                self.config.integration,
                self.environment,
                state.fuel.gross_mass().0,
                event_budget,
                epoch.dynamics_config(),
                rng,
                &proposal_rng,
                &scorer,
            );
            let proposed = match proposed {
                Ok(Some(proposed)) => {
                    let proxy_counts = scorer
                        .proxy_counts_for_diagnostics(&proposed.event_proposals)
                        .tuple();
                    state
                        .diagnostics
                        .satcom_event_mark_guide
                        .record_proxy_counts(proxy_counts.0, proxy_counts.1, proxy_counts.2);
                    proposed
                }
                Ok(None) => return Err(BroadFlightError::StateTimeMismatch),
                Err(PoweredEventProposalError::SelectedCandidate { diagnostic, source }) => {
                    let proxy_counts = scorer
                        .proxy_counts_for_event(diagnostic.kind, diagnostic.event_number)
                        .tuple();
                    state
                        .diagnostics
                        .satcom_event_mark_guide
                        .record_proxy_counts(proxy_counts.0, proxy_counts.1, proxy_counts.2);
                    state.diagnostics.satcom_event_mark_guide.record_event(
                        &diagnostic,
                        observation.flight.measurement.time,
                        epoch,
                    );
                    log_prior_over_proposal += diagnostic.log_prior_over_proposal;
                    if let Some(reason) = routine_rejection_reason(&source) {
                        state.status = BroadFlightParticleStatus::Rejected {
                            reason,
                            at_time: state.powered_flight.aircraft.time,
                        };
                        return Ok(log_prior_over_proposal);
                    }
                    return Err(source.into());
                }
                Err(PoweredEventProposalError::Dynamics(error)) => {
                    if let Some(reason) = routine_rejection_reason(&error) {
                        state.status = BroadFlightParticleStatus::Rejected {
                            reason,
                            at_time: state.powered_flight.aircraft.time,
                        };
                        return Ok(log_prior_over_proposal);
                    }
                    return Err(error.into());
                }
                Err(PoweredEventProposalError::Configuration(_)) => {
                    return Err(BroadFlightError::InvalidConfiguration(
                        "invalid dynamics event-mark proposal configuration",
                    ));
                }
                Err(PoweredEventProposalError::InvalidScore { .. }) => {
                    return Err(BroadFlightError::InvalidObservation(
                        "event-mark guide produced NaN or positive-infinite score",
                    ));
                }
                Err(PoweredEventProposalError::Scorer(
                    BroadSatcomEventMarkScorerError::InconsistentCandidate,
                )) => {
                    return Err(BroadFlightError::InvalidObservation(
                        "event-mark guide received an inconsistent candidate",
                    ));
                }
                Err(PoweredEventProposalError::Scorer(
                    BroadSatcomEventMarkScorerError::Projection(error),
                )) => return Err(error.into()),
                Err(PoweredEventProposalError::Scorer(
                    BroadSatcomEventMarkScorerError::Satcom(error),
                )) => return Err(error.into()),
            };

            for diagnostic in &proposed.event_proposals {
                state.diagnostics.satcom_event_mark_guide.record_event(
                    diagnostic,
                    observation.flight.measurement.time,
                    epoch,
                );
            }
            log_prior_over_proposal += proposed.log_prior_over_proposal;
            if !self.accept_powered_segment(state, &proposed.segment)? {
                return Ok(log_prior_over_proposal);
            }
        }
        Ok(log_prior_over_proposal)
    }

    /// Apply the estimator-owned performance and fuel composition to one
    /// accepted dynamics segment. `false` means the scientific path became an
    /// absorbing rejected state.
    fn accept_powered_segment(
        &self,
        state: &mut BroadFlightState,
        segment: &PoweredFlightSegment,
    ) -> Result<bool, BroadFlightError> {
        let performance = self.evaluate_segment_feasibility(state, segment)?;
        accumulate_performance_diagnostics(&mut state.diagnostics, performance.1, performance.2);
        if !performance.2.flags.operationally_feasible {
            state.status = BroadFlightParticleStatus::Rejected {
                reason: BroadRejectionReason::PoweredSegmentInfeasible,
                at_time: segment.start.aircraft.time,
            };
            return Ok(false);
        }
        state.powered_flight = segment.end;
        accumulate_segment_diagnostics(&mut state.diagnostics, segment);
        if matches!(state.fuel_status, BroadFuelDiagnosticStatus::Valid) {
            let input = PoweredFuelSegmentInput {
                start_time: segment.start.aircraft.time,
                end_time: segment.end.aircraft.time,
                midpoint_pressure_altitude: segment.midpoint_pressure_altitude,
                midpoint_mach: segment.midpoint_mach,
                midpoint_bank_angle: segment.midpoint_bank_angle,
                midpoint_vertical_speed: segment.midpoint_vertical_speed,
                midpoint_weather: PoweredFuelWeather {
                    static_air_temperature_celsius: segment.midpoint_weather.temperature_k - 273.15,
                    air_density_kg_m3: segment
                        .midpoint_weather
                        .dry_air_density_kg_m3(segment.midpoint_pressure_altitude.0),
                },
            };
            let fuel_model = scaled_fuel_model(self.config.fuel_model, state.fuel_flow_scale);
            match advance_powered_fuel(
                &mut state.fuel,
                fuel_model,
                self.config.fuel_flow_shares,
                input,
            ) {
                Ok(step) => {
                    state.diagnostics.fuel_outside_martin_domain_seconds +=
                        step.diagnostics.outside_martin_domain_seconds.0;
                    state.diagnostics.fuel_flow_multiplier_bound_hits +=
                        u64::from(step.diagnostics.flow_multiplier_limited);
                }
                Err(PoweredFuelError::OutsideModelDomain) => {
                    state.fuel_status = BroadFuelDiagnosticStatus::OutsideModelDomain {
                        at_time: segment.start.aircraft.time,
                    };
                }
                Err(error) => return Err(error.into()),
            }
        }
        Ok(true)
    }

    fn evaluate_segment_feasibility(
        &self,
        state: &BroadFlightState,
        segment: &mh370_dynamics::PoweredFlightSegment,
    ) -> Result<
        (
            mh370_end_of_flight::PoweredSegmentFeasibility,
            mh370_end_of_flight::OpenapB772Trent895CruiseThrustCeiling,
            mh370_end_of_flight::PoweredSegmentOperationalFeasibility,
        ),
        BroadFlightError,
    > {
        self.evaluate_segment_feasibility_with_conditions(segment, 2, state.fuel.gross_mass())
    }

    fn evaluate_segment_feasibility_with_conditions(
        &self,
        segment: &mh370_dynamics::PoweredFlightSegment,
        operating_engine_count: u8,
        mass: Kilograms,
    ) -> Result<
        (
            mh370_end_of_flight::PoweredSegmentFeasibility,
            mh370_end_of_flight::OpenapB772Trent895CruiseThrustCeiling,
            mh370_end_of_flight::PoweredSegmentOperationalFeasibility,
        ),
        BroadFlightError,
    > {
        const KNOT_M_S: f64 = 1_852.0 / 3_600.0;
        const FPM_M_S: f64 = 0.304_8 / 60.0;
        let start_tas =
            segment.start.mach * segment.start_weather.speed_of_sound_knots() * KNOT_M_S;
        let end_tas = segment.end.mach * segment.end_weather.speed_of_sound_knots() * KNOT_M_S;
        let flight_path_angle = |vertical_speed_ft_min: f64, tas_m_s: f64| {
            Degrees(
                (vertical_speed_ft_min * FPM_M_S / tas_m_s)
                    .clamp(-1.0, 1.0)
                    .asin()
                    .to_degrees(),
            )
        };
        let thrust =
            openap_b772_trent895_cruise_thrust_ceiling(OpenapB772Trent895CruiseThrustInput {
                pressure_altitude: segment.midpoint_pressure_altitude,
                mach: segment.midpoint_mach,
                operating_engine_count,
                declared_multiplier: self.config.powered_feasibility.thrust_multiplier,
                declared_static_cap_per_engine: Newtons(
                    self.config
                        .powered_feasibility
                        .static_thrust_cap_per_engine_n,
                ),
            })?;
        let feasibility = evaluate_powered_segment_feasibility(PoweredSegmentFeasibilityInput {
            aerodynamic_family: self.config.powered_feasibility.aerodynamic_family,
            duration: segment.duration,
            start_true_airspeed: MetresPerSecond(start_tas),
            end_true_airspeed: MetresPerSecond(end_tas),
            start_flight_path_angle: flight_path_angle(
                segment.start.aircraft.vertical_speed.0,
                start_tas,
            ),
            end_flight_path_angle: flight_path_angle(
                segment.end.aircraft.vertical_speed.0,
                end_tas,
            ),
            midpoint_density: KilogramsPerCubicMetre(
                segment
                    .midpoint_weather
                    .dry_air_density_kg_m3(segment.midpoint_pressure_altitude.0),
            ),
            mass,
            bank_angle: segment.midpoint_bank_angle,
            declared_total_thrust: DeclaredTotalThrustRange {
                minimum_commandable: Newtons(0.0),
                maximum_available: thrust.total_ceiling,
            },
        })?;
        let operational = evaluate_powered_segment_operational_feasibility(
            &feasibility,
            DeclaredAdditionalDragAllowance {
                maximum_delta_drag_coefficient: self
                    .config
                    .powered_feasibility
                    .maximum_additional_drag_coefficient,
            },
        )?;
        Ok((feasibility, thrust, operational))
    }

    fn observe_state(
        &self,
        state: &mut BroadFlightState,
        observation: &BroadFlightObservation,
    ) -> Result<f64, BroadFlightError> {
        observation.validate()?;
        match observation {
            BroadFlightObservation::FuelAnchor(anchor) => {
                if !state.is_active() {
                    return Ok(f64::NEG_INFINITY);
                }
                self.apply_fuel_anchor(state, anchor)?;
                Ok(0.0)
            }
            BroadFlightObservation::Checkpoint { .. } => Ok(if state.is_active() {
                0.0
            } else {
                f64::NEG_INFINITY
            }),
            BroadFlightObservation::Satcom(observation) => {
                if !state.is_active() {
                    return Ok(f64::NEG_INFINITY);
                }
                if (state.powered_flight.aircraft.time.0 - observation.flight.measurement.time.0)
                    .abs()
                    > TIME_TOLERANCE_S
                {
                    return Err(BroadFlightError::StateTimeMismatch);
                }
                let mut measurement = observation.flight.measurement.clone();
                if !observation.use_bto {
                    measurement.bto = None;
                    measurement.bto_sd = None;
                }
                if !observation.use_bfo {
                    measurement.bfo = None;
                    measurement.bfo_sd = None;
                }
                let mut bias = state.bfo_bias;
                let fit = evaluate_observation(
                    state.powered_flight.aircraft,
                    &mut bias,
                    &measurement,
                    observation.flight.satellite_afc_hz,
                    observation.use_bfo,
                    &self.config.satcom,
                )?;
                let bto_log_likelihood = match (fit.bto_residual_us, measurement.bto_sd) {
                    (Some(residual), Some(sd)) => {
                        normal_log_density(residual, sd.0).map_err(SatcomModelError::Statistics)?
                    }
                    _ => 0.0,
                };
                let bfo_log_likelihood = fit.log_likelihood - bto_log_likelihood;
                if observation.use_bto {
                    state.scores.cumulative_bto_log_likelihood += bto_log_likelihood;
                    state.scores.bto_observations += 1;
                }
                if observation.use_bfo {
                    state.scores.cumulative_bfo_log_likelihood += bfo_log_likelihood;
                    state.scores.bfo_observations += 1;
                }
                state.bfo_bias = bias;
                state.powered_flight.aircraft.bfo_bias = Hertz(bias.mean_hz);
                state.last_fit = Some(fit);
                Ok(fit.log_likelihood)
            }
        }
    }

    fn apply_fuel_anchor(
        &self,
        state: &mut BroadFlightState,
        anchor: &BroadFuelAnchorObservation,
    ) -> Result<(), BroadFlightError> {
        if state.diagnostics.fuel_anchor_count != 0
            || (state.powered_flight.aircraft.time.0 - anchor.time.0).abs() > TIME_TOLERANCE_S
        {
            return Err(BroadFlightError::FuelAnchorOrder);
        }
        let total = anchor.total_onboard_fuel_kg + state.fuel_quantity_offset_kg;
        let usable = total - anchor.reserved_fuel_kg - anchor.unusable_fuel_kg;
        if total < 0.0 || usable < -MASS_TOLERANCE_KG {
            return Err(BroadFlightError::InvalidObservation(
                "fuel quantity uncertainty makes the anchor negative",
            ));
        }
        let usable = usable.max(0.0);
        let anchored = PoweredFuelState {
            time: anchor.time,
            zero_fuel_weight: Kilograms(anchor.zero_fuel_weight_kg),
            left_usable_feed: Kilograms(usable * anchor.left_usable_fraction),
            right_usable_feed: Kilograms(usable * (1.0 - anchor.left_usable_fraction)),
            reserved_fuel: Kilograms(anchor.reserved_fuel_kg),
            unusable_fuel: Kilograms(anchor.unusable_fuel_kg),
            left_exhaustion_time: None,
            right_exhaustion_time: None,
            dual_engine_exhaustion_time: None,
        };
        state.diagnostics.last_fuel_anchor_mass_adjustment_kg =
            Some(anchored.gross_mass().0 - state.fuel.gross_mass().0);
        state.diagnostics.fuel_anchor_count = 1;
        state.fuel = anchored;
        state.fuel_status = BroadFuelDiagnosticStatus::Valid;
        Ok(())
    }
}

impl BroadFuelExhaustionSelectionGuide {
    fn evaluation(
        &self,
        outcome: BroadFuelExhaustionSelectionGuideOutcome,
        projected_dual_engine_exhaustion_time: Option<Seconds>,
    ) -> BroadFuelExhaustionSelectionGuideEvaluation {
        let compatible = matches!(
            outcome,
            BroadFuelExhaustionSelectionGuideOutcome::Compatible
        );
        let compatibility = if compatible { 1.0 } else { 0.0 };
        let potential =
            self.config.potential_floor + (1.0 - self.config.potential_floor) * compatibility;
        BroadFuelExhaustionSelectionGuideEvaluation {
            outcome,
            projected_dual_engine_exhaustion_time,
            log_selection_guide: potential.ln(),
        }
    }

    /// Evaluate the proposal-only compatibility guide without mutating the
    /// particle, its BFO bias, or either cumulative SATCOM score.
    pub fn evaluate(
        &self,
        model: &BroadFlightModel<'_>,
        state: &BroadFlightState,
        endpoint_observation: &BroadFlightObservation,
        point: &BroadFuelExhaustionSelectionGuidePoint,
    ) -> Result<BroadFuelExhaustionSelectionGuideEvaluation, BroadFlightError> {
        self.config.validate()?;
        point.validate()?;
        endpoint_observation.validate()?;
        let state_time = state.powered_flight.aircraft.time;
        let endpoint_time = endpoint_observation.time();
        if state.diagnostics.fuel_anchor_count != 1
            || (state.fuel.time.0 - state_time.0).abs() > TIME_TOLERANCE_S
            || state_time.0 > endpoint_time.0 + TIME_TOLERANCE_S
            || endpoint_time.0 > point.window_start.0 + TIME_TOLERANCE_S
            || matches!(endpoint_observation, BroadFlightObservation::FuelAnchor(_))
        {
            return Err(BroadFlightError::InvalidFuelSelectionGuideState);
        }
        if !state.is_active() {
            return Ok(self.evaluation(
                BroadFuelExhaustionSelectionGuideOutcome::InactiveParticle,
                state.fuel.dual_engine_exhaustion_time,
            ));
        }
        if !matches!(state.fuel_status, BroadFuelDiagnosticStatus::Valid) {
            return Ok(self.evaluation(
                BroadFuelExhaustionSelectionGuideOutcome::FuelModelUnavailable,
                state.fuel.dual_engine_exhaustion_time,
            ));
        }

        let aircraft = state.powered_flight.aircraft;
        let sampled_weather = match model.environment.weather.sample(
            model.environment.time_origin_unix_s + state_time.0,
            aircraft.altitude.0,
            aircraft.position,
        ) {
            Ok(weather) => weather,
            Err(EnvironmentError::OutsideDomain) => {
                return Ok(self.evaluation(
                    BroadFuelExhaustionSelectionGuideOutcome::FuelModelUnavailable,
                    state.fuel.dual_engine_exhaustion_time,
                ));
            }
            Err(error) => return Err(PoweredFlightError::Environment(error).into()),
        };
        let operating_point = FrozenPoweredFuelOperatingPoint {
            state_time,
            pressure_altitude: aircraft.altitude,
            mach: state.powered_flight.mach,
            bank_angle: state.powered_flight.bank_angle,
            vertical_speed: aircraft.vertical_speed,
            weather: PoweredFuelWeather {
                static_air_temperature_celsius: sampled_weather.temperature_k - 273.15,
                air_density_kg_m3: sampled_weather.dry_air_density_kg_m3(aircraft.altitude.0),
            },
        };
        let projection = project_frozen_powered_fuel_exhaustion(
            state.fuel,
            model.config.fuel_model,
            model.config.fuel_flow_shares,
            operating_point,
            state.fuel_flow_scale,
            point.window_end,
        )?;
        Ok(match projection {
            FrozenPoweredFuelProjection::ExhaustsAtOrBeforeBound { time, .. } => {
                let compatible = time.0 > point.window_start.0 + FUEL_SELECTION_WINDOW_TOLERANCE_S
                    && time.0 < point.window_end.0 - FUEL_SELECTION_WINDOW_TOLERANCE_S;
                self.evaluation(
                    if compatible {
                        BroadFuelExhaustionSelectionGuideOutcome::Compatible
                    } else {
                        BroadFuelExhaustionSelectionGuideOutcome::OutsideWindow
                    },
                    Some(time),
                )
            }
            FrozenPoweredFuelProjection::NoExhaustionByBound { .. } => self.evaluation(
                BroadFuelExhaustionSelectionGuideOutcome::NoExhaustionByBound,
                None,
            ),
            FrozenPoweredFuelProjection::AlreadyExhaustedBeforeStart { time, .. } => self
                .evaluation(
                    BroadFuelExhaustionSelectionGuideOutcome::AlreadyExhausted,
                    Some(time),
                ),
            FrozenPoweredFuelProjection::FuelModelUnavailable { .. } => self.evaluation(
                BroadFuelExhaustionSelectionGuideOutcome::FuelModelUnavailable,
                None,
            ),
        })
    }
}

impl<'a> SelectionGuide<BroadFlightModel<'a>> for BroadFuelExhaustionSelectionGuide {
    type Point = BroadFuelExhaustionSelectionGuidePoint;

    fn log_selection_guide(
        &self,
        model: &BroadFlightModel<'a>,
        state: &BroadFlightState,
        endpoint_observation: &BroadFlightObservation,
        point: &Self::Point,
    ) -> Result<f64, BroadFlightError> {
        Ok(self
            .evaluate(model, state, endpoint_observation, point)?
            .log_selection_guide)
    }
}

impl<'a> PersistentTwist<BroadFlightModel<'a>> for BroadFuelExhaustionSelectionGuide {
    type Point = BroadFuelExhaustionSelectionGuidePoint;

    fn log_twist_potential(
        &self,
        model: &BroadFlightModel<'a>,
        state: &BroadFlightState,
        endpoint_observation: &BroadFlightObservation,
        point: &Self::Point,
    ) -> Result<f64, BroadFlightError> {
        Ok(self
            .evaluate(model, state, endpoint_observation, point)?
            .log_selection_guide)
    }
}

/// Estimator-owned adapter for the generic exact intermediate-potential SMC
/// engine. It carries no mutable state between lineages.
#[derive(Debug, Clone, Copy, Default, PartialEq)]
pub struct BroadSatcomIntermediatePotentialBridge {
    config: BroadSatcomIntermediatePotentialConfig,
}

impl BroadSatcomIntermediatePotentialBridge {
    pub fn new(config: BroadSatcomIntermediatePotentialConfig) -> Result<Self, BroadFlightError> {
        config.validate()?;
        Ok(Self { config })
    }

    pub const fn config(self) -> BroadSatcomIntermediatePotentialConfig {
        self.config
    }

    fn satcom_endpoint<'a>(
        &self,
        endpoint: &'a BroadFlightObservation,
    ) -> Result<&'a BroadSatcomObservation, BroadFlightError> {
        endpoint.validate()?;
        match endpoint {
            BroadFlightObservation::Satcom(satcom) if satcom.use_bto => Ok(satcom),
            _ => Err(BroadFlightError::InvalidObservation(
                "intermediate SATCOM potential requires a BTO endpoint",
            )),
        }
    }

    fn validate_point(
        &self,
        point: &BroadSatcomIntermediatePotentialPoint,
        endpoint: &BroadFlightObservation,
    ) -> Result<f64, BroadFlightError> {
        let _ = self.satcom_endpoint(endpoint)?;
        if !point.interval_start.is_finite() || !point.time.is_finite() {
            return Err(BroadFlightError::InvalidObservation(
                "non-finite intermediate SATCOM point",
            ));
        }
        let expected_offset = match point.kind {
            BroadSatcomIntermediatePotentialPointKind::EarlyBtoOnly => self.config.early_offset.0,
            BroadSatcomIntermediatePotentialPointKind::LateEnabledSatcom => {
                self.config.late_offset.0
            }
        };
        if (point.time.0 - point.interval_start.0 - expected_offset).abs() > TIME_TOLERANCE_S
            || point.time.0 <= point.interval_start.0 + TIME_TOLERANCE_S
            || point.time.0 >= endpoint.time().0 - TIME_TOLERANCE_S
        {
            return Err(BroadFlightError::InvalidObservation(
                "intermediate SATCOM point is inconsistent with its declared interval",
            ));
        }
        let duration = endpoint.time().0 - point.interval_start.0;
        let fraction = (point.time.0 - point.interval_start.0) / duration;
        if !fraction.is_finite() || !(0.0..1.0).contains(&fraction) {
            return Err(BroadFlightError::InvalidObservation(
                "invalid intermediate SATCOM interval fraction",
            ));
        }
        Ok(fraction)
    }

    fn terminal_tangent_projection(
        &self,
        model: &BroadFlightModel<'_>,
        state: &BroadFlightState,
        endpoint_time: Seconds,
    ) -> Result<AircraftState, BroadFlightError> {
        let aircraft = state.powered_flight.aircraft;
        let remaining_seconds = endpoint_time.0 - aircraft.time.0;
        if !aircraft.all_finite() || !remaining_seconds.is_finite() || remaining_seconds < 0.0 {
            return Err(BroadFlightError::InvalidObservation(
                "invalid terminal-tangent SATCOM projection",
            ));
        }
        let position = destination_wgs84(
            aircraft.position,
            aircraft.track_true,
            NauticalMiles(aircraft.ground_speed.0 * remaining_seconds / 3_600.0),
        )
        .map_err(|_| {
            BroadFlightError::InvalidObservation("terminal-tangent SATCOM projection failed")
        })?;
        let altitude = Feet(
            (aircraft.altitude.0 + aircraft.vertical_speed.0 * remaining_seconds / 60.0).clamp(
                model.config.limits.minimum_pressure_altitude_ft,
                model.config.limits.maximum_pressure_altitude_ft,
            ),
        );
        if !altitude.is_finite() {
            return Err(BroadFlightError::InvalidObservation(
                "non-finite terminal-tangent altitude",
            ));
        }
        Ok(AircraftState {
            time: endpoint_time,
            position,
            altitude,
            track_true: aircraft.track_true,
            ground_speed: aircraft.ground_speed,
            vertical_speed: aircraft.vertical_speed,
            bfo_bias: Hertz(state.bfo_bias.mean_hz),
        })
    }

    fn potential_for_point(
        &self,
        model: &BroadFlightModel<'_>,
        state: &BroadFlightState,
        endpoint: &BroadFlightObservation,
        point: &BroadSatcomIntermediatePotentialPoint,
    ) -> Result<f64, BroadFlightError> {
        let _ = self.validate_point(point, endpoint)?;
        if !state.is_active() {
            // The generic bridge requires h > 0 on every carried state. A
            // physically rejected state is absorbing and therefore receives
            // only the declared floor here; the exact endpoint observation
            // assigns it -infinity before any posterior snapshot or handoff.
            return Ok(self.config.potential_floor.ln());
        }
        if (state.powered_flight.aircraft.time.0 - point.time.0).abs() > TIME_TOLERANCE_S
            || (state.fuel.time.0 - point.time.0).abs() > TIME_TOLERANCE_S
        {
            return Err(BroadFlightError::StateTimeMismatch);
        }
        let satcom = self.satcom_endpoint(endpoint)?;
        let measurement = &satcom.flight.measurement;
        let projected = self.terminal_tangent_projection(model, state, endpoint.time())?;
        let remaining_hours = (endpoint.time().0 - point.time.0) / 3_600.0;

        let observed_bto = measurement.bto.ok_or(BroadFlightError::InvalidObservation(
            "BTO guide endpoint has no BTO value",
        ))?;
        let observed_bto_sd = measurement
            .bto_sd
            .ok_or(BroadFlightError::InvalidObservation(
                "BTO guide endpoint has no BTO deviation",
            ))?;
        let predicted_bto = bto(
            projected.position,
            projected.altitude.0,
            measurement.satellite_position_km,
            measurement.ground_station_position_km,
            model.config.satcom.bto,
        );
        let bto_sd = observed_bto_sd
            .0
            .hypot(self.config.bto_projection_sd_per_remaining_hour.0 * remaining_hours);
        let mut squared_standardized_residual =
            ((observed_bto.0 - predicted_bto.0) / bto_sd).powi(2);

        if matches!(
            point.kind,
            BroadSatcomIntermediatePotentialPointKind::LateEnabledSatcom
        ) && satcom.use_bfo
        {
            let observed_bfo = measurement.bfo.ok_or(BroadFlightError::InvalidObservation(
                "BFO guide endpoint has no BFO value",
            ))?;
            let observed_bfo_sd =
                measurement
                    .bfo_sd
                    .ok_or(BroadFlightError::InvalidObservation(
                        "BFO guide endpoint has no BFO deviation",
                    ))?;
            if !state.bfo_bias.mean_hz.is_finite()
                || !state.bfo_bias.variance_hz2.is_finite()
                || state.bfo_bias.variance_hz2 < 0.0
            {
                return Err(BroadFlightError::InvalidObservation(
                    "invalid BFO bias state at intermediate SATCOM point",
                ));
            }
            let mut constants = model.config.satcom.bfo;
            constants.satellite_afc_hz = satcom.flight.satellite_afc_hz;
            let predicted_without_bias = bfo_components(
                projected,
                measurement.satellite_position_km,
                measurement.satellite_velocity_km_s,
                measurement.ground_station_position_km,
                constants,
            )
            .base_without_bias
            .0;
            let innovation = observed_bfo.0 - predicted_without_bias - state.bfo_bias.mean_hz;
            let bfo_variance = observed_bfo_sd.0.powi(2)
                + state.bfo_bias.variance_hz2
                + (self.config.bfo_projection_sd_per_remaining_hour.0 * remaining_hours).powi(2);
            squared_standardized_residual += innovation.powi(2) / bfo_variance;
        }

        if squared_standardized_residual.is_nan() {
            return Err(BroadFlightError::InvalidObservation(
                "non-finite intermediate SATCOM residual",
            ));
        }
        let compatibility = (-0.5 * squared_standardized_residual).exp();
        let potential =
            self.config.potential_floor + (1.0 - self.config.potential_floor) * compatibility;
        let log_potential = potential.ln();
        if !log_potential.is_finite() {
            return Err(BroadFlightError::InvalidObservation(
                "intermediate SATCOM potential is not strictly positive",
            ));
        }
        Ok(log_potential)
    }
}

/// Ephemeral transition bookkeeping retained by the particle engine only.
/// In particular, this type is deliberately not serializable and never enters
/// [`BroadFlightState`] or a posterior handoff.
#[derive(Debug, Clone)]
pub struct BroadSatcomIntermediatePotentialContext {
    interval_start: Seconds,
    endpoint_time: Seconds,
    last_target_time: Seconds,
    interval_start_event_counters: PoweredEventCounters,
    event_budget: PoweredEventBudget,
}

fn event_counter_delta(
    start: PoweredEventCounters,
    end: PoweredEventCounters,
) -> Option<PoweredEventCounters> {
    Some(PoweredEventCounters {
        lateral: end.lateral.checked_sub(start.lateral)?,
        speed: end.speed.checked_sub(start.speed)?,
        altitude: end.altitude.checked_sub(start.altitude)?,
    })
}

impl BroadSatcomIntermediatePotentialContext {
    fn validate_for(
        &self,
        model: &BroadFlightModel<'_>,
        state: &BroadFlightState,
        endpoint: &BroadFlightObservation,
    ) -> Result<(), BroadFlightError> {
        if (self.endpoint_time.0 - endpoint.time().0).abs() > TIME_TOLERANCE_S
            || self.event_budget.maximum_events
                != model.config.integration.maximum_events_per_transition
            || !self.interval_start.is_finite()
            || !self.last_target_time.is_finite()
            || self.last_target_time.0 < self.interval_start.0 - TIME_TOLERANCE_S
            || self.last_target_time.0 > self.endpoint_time.0 + TIME_TOLERANCE_S
        {
            return Err(BroadFlightError::InvalidObservation(
                "intermediate SATCOM transition context mismatch",
            ));
        }
        if state.is_active()
            && ((state.powered_flight.aircraft.time.0 - self.last_target_time.0).abs()
                > TIME_TOLERANCE_S
                || (state.fuel.time.0 - self.last_target_time.0).abs() > TIME_TOLERANCE_S
                || event_counter_delta(
                    self.interval_start_event_counters,
                    state.powered_flight.event_counters,
                ) != Some(self.event_budget.consumed))
        {
            return Err(BroadFlightError::InvalidObservation(
                "intermediate SATCOM event-budget context is inconsistent",
            ));
        }
        Ok(())
    }
}

impl<'a> IntermediatePotentialBridge<BroadFlightModel<'a>>
    for BroadSatcomIntermediatePotentialBridge
{
    type Point = BroadSatcomIntermediatePotentialPoint;
    type Context = BroadSatcomIntermediatePotentialContext;

    fn point_time_s(&self, point: &Self::Point) -> f64 {
        point.time.0
    }

    fn begin_interval(
        &self,
        model: &BroadFlightModel<'a>,
        state: &BroadFlightState,
        endpoint_observation: &BroadFlightObservation,
    ) -> Result<Self::Context, BroadFlightError> {
        self.config.validate()?;
        let _ = self.satcom_endpoint(endpoint_observation)?;
        let interval_start = state.powered_flight.aircraft.time;
        let endpoint_time = endpoint_observation.time();
        let elapsed_seconds = endpoint_time.0 - interval_start.0;
        if !state.is_active()
            || (state.fuel.time.0 - interval_start.0).abs() > TIME_TOLERANCE_S
            || !elapsed_seconds.is_finite()
            || elapsed_seconds + TIME_TOLERANCE_S < self.config.minimum_interval.0
        {
            return Err(BroadFlightError::InvalidObservation(
                "invalid intermediate SATCOM interval",
            ));
        }
        if model.proposal_candidates_for_observation(endpoint_observation, elapsed_seconds) != 1 {
            return Err(BroadFlightError::InvalidConfiguration(
                "intermediate SATCOM potentials require one model-local proposal candidate",
            ));
        }
        Ok(BroadSatcomIntermediatePotentialContext {
            interval_start,
            endpoint_time,
            last_target_time: interval_start,
            interval_start_event_counters: state.powered_flight.event_counters,
            event_budget: PoweredEventBudget::new(
                model.config.integration.maximum_events_per_transition,
            )?,
        })
    }

    fn propose_to_point(
        &self,
        model: &BroadFlightModel<'a>,
        state: &BroadFlightState,
        endpoint_observation: &BroadFlightObservation,
        point: &Self::Point,
        context: &Self::Context,
        elapsed_seconds: f64,
        rng: &mut ChaCha8Rng,
    ) -> Result<IntermediatePotentialProposal<BroadFlightState, Self::Context>, BroadFlightError>
    {
        context.validate_for(model, state, endpoint_observation)?;
        let _ = self.validate_point(point, endpoint_observation)?;
        if (point.interval_start.0 - context.interval_start.0).abs() > TIME_TOLERANCE_S
            || point.time.0 <= context.last_target_time.0 + TIME_TOLERANCE_S
            || (point.time.0 - context.last_target_time.0 - elapsed_seconds).abs()
                > TIME_TOLERANCE_S
        {
            return Err(BroadFlightError::InvalidObservation(
                "intermediate SATCOM point order or elapsed time mismatch",
            ));
        }
        let mut proposed = *state;
        let mut next_context = context.clone();
        model.propagate_state_with_budget(
            &mut proposed,
            point.time.0,
            &mut next_context.event_budget,
            rng,
        )?;
        next_context.last_target_time = point.time;
        next_context.validate_for(model, &proposed, endpoint_observation)?;
        Ok(IntermediatePotentialProposal {
            proposal: Proposal::from_prior(proposed),
            context: next_context,
        })
    }

    fn propose_to_endpoint(
        &self,
        model: &BroadFlightModel<'a>,
        state: &BroadFlightState,
        endpoint_observation: &BroadFlightObservation,
        context: &Self::Context,
        elapsed_seconds: f64,
        rng: &mut ChaCha8Rng,
    ) -> Result<Proposal<BroadFlightState>, BroadFlightError> {
        context.validate_for(model, state, endpoint_observation)?;
        if (context.endpoint_time.0 - context.last_target_time.0 - elapsed_seconds).abs()
            > TIME_TOLERANCE_S
            || elapsed_seconds <= 0.0
        {
            return Err(BroadFlightError::InvalidObservation(
                "intermediate SATCOM endpoint elapsed time mismatch",
            ));
        }
        let mut proposed = *state;
        let mut completed_context = context.clone();
        model.propagate_state_with_budget(
            &mut proposed,
            context.endpoint_time.0,
            &mut completed_context.event_budget,
            rng,
        )?;
        completed_context.last_target_time = context.endpoint_time;
        completed_context.validate_for(model, &proposed, endpoint_observation)?;
        Ok(Proposal::from_prior(proposed))
    }

    fn log_potential(
        &self,
        model: &BroadFlightModel<'a>,
        state: &BroadFlightState,
        endpoint_observation: &BroadFlightObservation,
        point: &Self::Point,
    ) -> Result<f64, BroadFlightError> {
        self.potential_for_point(model, state, endpoint_observation, point)
    }
}

impl StratifiedPostResampleMove<BroadFlightModel<'_>> for BroadPendingRenewalRefreshKernel {
    fn apply(
        &self,
        model: &BroadFlightModel<'_>,
        state: &mut BroadFlightState,
        context: StratifiedPostResampleMoveContext,
        rng: &mut ChaCha8Rng,
    ) -> Result<(), BroadFlightError> {
        if !state.is_active() {
            return Ok(());
        }
        if state.stratum != context.stratum {
            return Err(BroadFlightError::InvalidPendingRenewalRefreshState(
                "particle and move-context strata differ",
            ));
        }
        let current_time = state.powered_flight.aircraft.time;
        if current_time != Seconds(context.observation_time_s) {
            return Err(BroadFlightError::InvalidPendingRenewalRefreshState(
                "particle and move-context times differ",
            ));
        }
        if current_time != state.fuel.time {
            return Err(BroadFlightError::StateTimeMismatch);
        }
        if !state.diagnostics.pending_renewal_refresh.validate() {
            return Err(BroadFlightError::InvalidPendingRenewalRefreshState(
                "pending-renewal refresh diagnostics are inconsistent",
            ));
        }

        let process = model.stratum(state.stratum)?.maneuver_process;
        let mut increment = BroadPendingRenewalRefreshDiagnostics::default();
        for kind in self.config.kinds() {
            increment.record(kind)?;
        }
        let diagnostics = state
            .diagnostics
            .pending_renewal_refresh
            .checked_add(increment)?;

        // The PF hook stream is already keyed by observation, output slot, and
        // stratum. One seed fans out into fixed, kind-specific substreams.
        let refresh_seed = rng.gen::<u64>();
        let mut powered_flight = state.powered_flight;
        for kind in self.config.kinds() {
            let kind_tag = match kind {
                PoweredEventKind::Lateral => 0,
                PoweredEventKind::Speed => 1,
                PoweredEventKind::Altitude => 2,
            };
            let mut kind_rng = mh370_particle_filter::rng_for(
                refresh_seed,
                BROAD_PENDING_RENEWAL_REFRESH_RNG_DOMAIN,
                0,
                0,
                kind_tag,
            );
            powered_flight = refresh_powered_event_renewal(
                powered_flight,
                kind,
                process,
                current_time,
                &mut kind_rng,
            )?;
        }

        state.powered_flight = powered_flight;
        state.diagnostics.pending_renewal_refresh = diagnostics;
        Ok(())
    }
}

impl ParticleModel for BroadFlightModel<'_> {
    type State = BroadFlightState;
    type Observation = BroadFlightObservation;
    type Error = BroadFlightError;

    fn observation_time_s(&self, observation: &Self::Observation) -> f64 {
        observation.time().0
    }

    fn initialize(
        &self,
        _particle_index: usize,
        rng: &mut ChaCha8Rng,
    ) -> Result<Self::State, Self::Error> {
        self.initialize_for_stratum(self.config.strata[0].id, rng)
    }

    fn initialize_in_stratum(
        &self,
        stratum: StratumId,
        _particle_index: usize,
        particle_index_within_stratum: usize,
        particles_in_stratum: usize,
        rng: &mut ChaCha8Rng,
    ) -> Result<Initialization<Self::State>, Self::Error> {
        Ok(Initialization::from_prior(
            self.initialize_for_stratum_cell(
                stratum,
                particle_index_within_stratum,
                particles_in_stratum,
                rng,
            )?,
        ))
    }

    fn stratum(&self, state: &Self::State) -> StratumId {
        state.stratum
    }

    fn propose(
        &self,
        state: &Self::State,
        observation: &Self::Observation,
        elapsed_seconds: f64,
        rng: &mut ChaCha8Rng,
    ) -> Result<Proposal<Self::State>, Self::Error> {
        observation.validate()?;
        let proposal_candidates =
            self.proposal_candidates_for_observation(observation, elapsed_seconds);
        if let Some(epoch) = self
            .satcom_event_mark_guide
            .as_ref()
            .and_then(|guide| guide.epoch(observation.id()))
        {
            let BroadFlightObservation::Satcom(satcom) = observation else {
                return Err(BroadFlightError::InvalidConfiguration(
                    "event-mark guide observation ID does not identify SATCOM",
                ));
            };
            if proposal_candidates != 1 {
                return Err(BroadFlightError::InvalidConfiguration(
                    "event-mark guide requires one model-local proposal candidate",
                ));
            }
            let mut proposed = *state;
            let mut event_budget =
                PoweredEventBudget::new(self.config.integration.maximum_events_per_transition)?;
            let log_prior_over_proposal = self.propagate_state_with_satcom_event_mark_guide(
                &mut proposed,
                satcom,
                epoch,
                &mut event_budget,
                rng,
            )?;
            return Ok(Proposal {
                state: proposed,
                log_prior_over_proposal,
            });
        }
        if proposal_candidates == 1 {
            let mut proposed = *state;
            self.propagate_state(&mut proposed, observation.time().0, rng)?;
            return Ok(Proposal::from_prior(proposed));
        }
        let mut candidates = Vec::with_capacity(proposal_candidates);
        let mut log_likelihoods = Vec::with_capacity(proposal_candidates);
        for _ in 0..proposal_candidates {
            let mut proposed = *state;
            self.propagate_state(&mut proposed, observation.time().0, rng)?;
            let mut scored = proposed;
            let log_likelihood = self.observe_state(&mut scored, observation)?;
            candidates.push(proposed);
            log_likelihoods.push(log_likelihood);
        }
        let Some((selected, log_prior_over_proposal)) =
            select_multiple_try_candidate(&log_likelihoods, rng)
        else {
            return Ok(Proposal::from_prior(candidates[0]));
        };
        Ok(Proposal {
            state: candidates[selected],
            log_prior_over_proposal,
        })
    }

    fn log_likelihood(
        &self,
        state: &Self::State,
        observation: &Self::Observation,
    ) -> Result<f64, Self::Error> {
        let mut copy = *state;
        self.observe_state(&mut copy, observation)
    }

    fn observe(
        &self,
        state: &mut Self::State,
        observation: &Self::Observation,
    ) -> Result<f64, Self::Error> {
        self.observe_state(state, observation)
    }
}

fn select_multiple_try_candidate(
    log_likelihoods: &[f64],
    rng: &mut ChaCha8Rng,
) -> Option<(usize, f64)> {
    let maximum = log_likelihoods
        .iter()
        .copied()
        .filter(|value| value.is_finite())
        .fold(f64::NEG_INFINITY, f64::max);
    if !maximum.is_finite() {
        return None;
    }
    let scaled = log_likelihoods
        .iter()
        .map(|value| {
            if value.is_finite() {
                (*value - maximum).exp()
            } else {
                0.0
            }
        })
        .collect::<Vec<_>>();
    let total = scaled.iter().sum::<f64>();
    let mut threshold = rng.gen::<f64>() * total;
    let selected = scaled
        .iter()
        .enumerate()
        .find_map(|(index, weight)| {
            threshold -= *weight;
            (threshold <= 0.0 && *weight > 0.0).then_some(index)
        })
        .unwrap_or_else(|| {
            scaled
                .iter()
                .rposition(|weight| *weight > 0.0)
                .expect("finite maximum implies a positive scaled weight")
        });
    let log_mean_likelihood = maximum + total.ln() - (log_likelihoods.len() as f64).ln();
    Some((selected, log_mean_likelihood - log_likelihoods[selected]))
}

fn scaled_fuel_model(model: PoweredFuelModel, scale: f64) -> PoweredFuelModel {
    match model {
        PoweredFuelModel::MartinTrent892Lrc => PoweredFuelModel::MartinTrent892Lrc,
        PoweredFuelModel::DeclaredBroadExtension(mut extension) => {
            extension.nominal_flow_scale *= scale;
            PoweredFuelModel::DeclaredBroadExtension(extension)
        }
    }
}

fn fuel_input(segment: PoweredFlightSegment) -> PoweredFuelSegmentInput {
    PoweredFuelSegmentInput {
        start_time: segment.start.aircraft.time,
        end_time: segment.end.aircraft.time,
        midpoint_pressure_altitude: segment.midpoint_pressure_altitude,
        midpoint_mach: segment.midpoint_mach,
        midpoint_bank_angle: segment.midpoint_bank_angle,
        midpoint_vertical_speed: segment.midpoint_vertical_speed,
        midpoint_weather: PoweredFuelWeather {
            static_air_temperature_celsius: segment.midpoint_weather.temperature_k - 273.15,
            air_density_kg_m3: segment
                .midpoint_weather
                .dry_air_density_kg_m3(segment.midpoint_pressure_altitude.0),
        },
    }
}

fn accumulate_coupled_diagnostics(
    diagnostics: &mut BroadFlightDiagnostics,
    segment: &PoweredFlightSegment,
    fuel: &PoweredFuelStep,
) {
    accumulate_segment_diagnostics(diagnostics, segment);
    diagnostics.fuel_outside_martin_domain_seconds +=
        fuel.diagnostics.outside_martin_domain_seconds.0;
    diagnostics.fuel_flow_multiplier_bound_hits +=
        u64::from(fuel.diagnostics.flow_multiplier_limited);
}

fn accumulate_performance_diagnostics(
    diagnostics: &mut BroadFlightDiagnostics,
    thrust: mh370_end_of_flight::OpenapB772Trent895CruiseThrustCeiling,
    operational: mh370_end_of_flight::PoweredSegmentOperationalFeasibility,
) {
    diagnostics.powered_segments_screened += 1;
    diagnostics.powered_thrust_proxy_extrapolation_segments += u64::from(matches!(
        thrust.domain_status,
        mh370_end_of_flight::OpenapB772Trent895DomainStatus::EquationExtrapolationWithinDeclaredProxyDomain
    ));
    diagnostics.powered_thrust_proxy_cap_segments += u64::from(thrust.static_cap_applied);
    diagnostics.powered_additional_drag_required_segments +=
        u64::from(operational.required_additional_drag.0 > 0.0);
    diagnostics.powered_additional_drag_limit_exceeded_segments +=
        u64::from(!operational.flags.lower_thrust_or_additional_drag_feasible);
    diagnostics.powered_upper_thrust_failure_segments +=
        u64::from(!operational.flags.upper_thrust_feasible);
}

fn operating_engine_count(fuel: PoweredFuelState) -> u8 {
    u8::from(fuel.left_exhaustion_time.is_none() && fuel.left_usable_feed.0 > MASS_TOLERANCE_KG)
        + u8::from(
            fuel.right_exhaustion_time.is_none() && fuel.right_usable_feed.0 > MASS_TOLERANCE_KG,
        )
}

fn midpoint_fuel_mass(step: &PoweredFuelStep) -> Kilograms {
    Kilograms(0.5 * (step.diagnostics.start_gross_mass.0 + step.diagnostics.end_gross_mass.0))
}

fn earliest_new_engine_exhaustion(
    before: PoweredFuelState,
    after: PoweredFuelState,
) -> Option<Seconds> {
    let left = before
        .left_exhaustion_time
        .is_none()
        .then_some(after.left_exhaustion_time)
        .flatten();
    let right = before
        .right_exhaustion_time
        .is_none()
        .then_some(after.right_exhaustion_time)
        .flatten();
    match (left, right) {
        (Some(left), Some(right)) => Some(Seconds(left.0.min(right.0))),
        (Some(time), None) | (None, Some(time)) => Some(time),
        (None, None) => None,
    }
}

fn exhaustion_result(
    outcome: BroadDualEngineExhaustionOutcome,
    state: BroadFlightState,
    target_bound: Seconds,
    transition_diagnostics: BroadFlightDiagnostics,
    exact_boundary_reintegrations: u32,
    boundary_events_at_start: PoweredEventCounters,
    boundary_events_at_end: PoweredEventCounters,
) -> BroadDualEngineExhaustionResult {
    BroadDualEngineExhaustionResult {
        outcome,
        state,
        target_bound,
        exhaustion_time: state.fuel.dual_engine_exhaustion_time,
        transition_diagnostics,
        exact_boundary_reintegrations,
        boundary_events_at_start,
        boundary_events_at_end,
    }
}

fn fallback_powered_state(aircraft: AircraftState, mach: f64) -> PoweredFlightState {
    use mh370_dynamics::{PoweredEventClocks, PoweredEventCounters, PoweredFlightCommand};
    PoweredFlightState {
        aircraft,
        heading_true: aircraft.track_true,
        mach,
        bank_angle: Degrees(0.0),
        command: PoweredFlightCommand {
            lateral_mode: PoweredLateralMode::ConstantTrueTrack,
            selected_control: aircraft.track_true,
            great_circle_destination: None,
            target_mach: mach,
            target_pressure_altitude: aircraft.altitude,
        },
        event_clocks: PoweredEventClocks {
            lateral: None,
            speed: None,
            altitude: None,
        },
        event_counters: PoweredEventCounters::default(),
    }
}

fn routine_rejection_reason(error: &PoweredFlightError) -> Option<BroadRejectionReason> {
    match error {
        PoweredFlightError::InvalidState => {
            Some(BroadRejectionReason::StateOutsideDeclaredEnvelope)
        }
        PoweredFlightError::MissingMagneticEnvironment => {
            Some(BroadRejectionReason::MagneticEnvironmentUnavailable)
        }
        PoweredFlightError::MagneticAltitudeOutsideGrid { .. } => {
            Some(BroadRejectionReason::MagneticAltitudeOutsideGrid)
        }
        PoweredFlightError::EmptySpeedEnvelope => Some(BroadRejectionReason::EmptySpeedEnvelope),
        PoweredFlightError::EventLimitExceeded => {
            Some(BroadRejectionReason::ComputationalEventLimit)
        }
        PoweredFlightError::Environment(EnvironmentError::OutsideDomain) => {
            Some(BroadRejectionReason::EnvironmentOutsideDomain)
        }
        PoweredFlightError::Geodesy(_) => Some(BroadRejectionReason::GeodesicPropagation),
        PoweredFlightError::GreatCircle(_) => Some(BroadRejectionReason::GreatCirclePropagation),
        PoweredFlightError::InfeasibleGroundTrack => {
            Some(BroadRejectionReason::InfeasibleGroundTrack)
        }
        PoweredFlightError::MachRateEnvelopeConflict { .. } => {
            Some(BroadRejectionReason::MachRateEnvelopeConflict)
        }
        PoweredFlightError::InvalidLimits
        | PoweredFlightError::InvalidManeuverProcess
        | PoweredFlightError::InvalidIntegration
        | PoweredFlightError::InvalidTargetTime
        | PoweredFlightError::EventCounterOverflow
        | PoweredFlightError::Environment(EnvironmentError::InvalidFormat)
        | PoweredFlightError::Environment(EnvironmentError::InvalidAxis) => None,
    }
}

fn accumulate_segment_diagnostics(
    diagnostics: &mut BroadFlightDiagnostics,
    segment: &mh370_dynamics::PoweredFlightSegment,
) {
    diagnostics.integration_segments += 1;
    match segment.regime {
        PoweredStepRegime::Steady => diagnostics.steady_segments += 1,
        PoweredStepRegime::Transition => diagnostics.transition_segments += 1,
    }
    let events = [segment.events_at_start, segment.events_at_end];
    diagnostics.lateral_events += events
        .iter()
        .map(|event| u64::from(event.lateral))
        .sum::<u64>();
    diagnostics.speed_events += events
        .iter()
        .map(|event| u64::from(event.speed))
        .sum::<u64>();
    diagnostics.altitude_events += events
        .iter()
        .map(|event| u64::from(event.altitude))
        .sum::<u64>();
    accumulate_powered_limit_activity(
        diagnostics,
        segment.active_limits,
        segment.duration.0,
        segment.magnetic_altitude_clamped,
    );
    diagnostics.magnetic_altitude_clamp_seconds +=
        segment.duration.0 * f64::from(segment.magnetic_altitude_clamped);
}

fn accumulate_powered_limit_activity(
    diagnostics: &mut BroadFlightDiagnostics,
    active: PoweredLimitActivity,
    duration_seconds: f64,
    magnetic_altitude_clamped: bool,
) {
    diagnostics.powered_target_clamp_count +=
        u64::from(active.stall_or_minimum_mach_floor || active.vmo_or_mmo_ceiling);
    let boundary = &mut diagnostics.powered_boundary_seconds;
    boundary.stall_or_minimum_mach_floor +=
        duration_seconds * f64::from(active.stall_or_minimum_mach_floor);
    boundary.vmo_or_mmo_ceiling += duration_seconds * f64::from(active.vmo_or_mmo_ceiling);
    boundary.bank += duration_seconds * f64::from(active.bank);
    boundary.roll_rate += duration_seconds * f64::from(active.roll_rate);
    boundary.climb_rate += duration_seconds * f64::from(active.climb_rate);
    boundary.descent_rate += duration_seconds * f64::from(active.descent_rate);
    boundary.vertical_acceleration += duration_seconds * f64::from(active.vertical_acceleration);
    boundary.lower_altitude += duration_seconds * f64::from(active.lower_altitude);
    boundary.upper_altitude += duration_seconds * f64::from(active.upper_altitude);
    boundary.magnetic_altitude_clamp += duration_seconds * f64::from(magnetic_altitude_clamped);
}

fn valid_fuel_state(state: PoweredFuelState) -> bool {
    let values = [
        state.time.0,
        state.zero_fuel_weight.0,
        state.left_usable_feed.0,
        state.right_usable_feed.0,
        state.reserved_fuel.0,
        state.unusable_fuel.0,
    ];
    values.iter().all(|value| value.is_finite())
        && state.zero_fuel_weight.0 > 0.0
        && values[2..].iter().all(|value| *value >= 0.0)
        && state.left_exhaustion_time.is_none()
        && state.right_exhaustion_time.is_none()
        && state.dual_engine_exhaustion_time.is_none()
}

fn valid_fuel_uncertainty(uncertainty: BroadFuelUncertainty) -> bool {
    uncertainty.total_quantity_offset_kg.validate()
        && uncertainty.flow_scale_log_uniform.validate()
        && uncertainty.flow_scale_log_uniform.minimum > 0.0
}

/// Deterministic balanced jitter for a log-space Latin hypercube. Mirrored
/// cells receive antithetic offsets, giving an exact population mean of 1/2 in
/// prior-quantile space while retaining an interior, non-midpoint design. The
/// key depends only on the immutable stratum, allocation size, and mirrored
/// cell pair, so evaluation order and Rayon scheduling cannot affect it.
fn balanced_latin_hypercube_jitter(
    stratum: StratumId,
    particle_index_within_stratum: usize,
    particles_in_stratum: usize,
) -> Result<f64, BroadFlightError> {
    if particles_in_stratum == 0 || particle_index_within_stratum >= particles_in_stratum {
        return Err(BroadFlightError::InvalidConfiguration(
            "invalid Latin-hypercube fuel allocation",
        ));
    }
    let mirror = particles_in_stratum - 1 - particle_index_within_stratum;
    if mirror == particle_index_within_stratum {
        return Ok(0.5);
    }
    let pair = particle_index_within_stratum.min(mirror) as u64;
    let mut key = 0x6a09_e667_f3bc_c909_u64
        ^ u64::from(stratum.0).wrapping_mul(0x9e37_79b9_7f4a_7c15)
        ^ (particles_in_stratum as u64).rotate_left(21)
        ^ pair.wrapping_mul(0xbf58_476d_1ce4_e5b9);
    // SplitMix64 finalizer: a small, stable keyed stream without consuming the
    // particle's dynamics RNG.
    key ^= key >> 30;
    key = key.wrapping_mul(0xbf58_476d_1ce4_e5b9);
    key ^= key >> 27;
    key = key.wrapping_mul(0x94d0_49bb_1331_11eb);
    key ^= key >> 31;
    let unit = (((key >> 11) as f64 + 0.5) * (1.0 / ((1_u64 << 53) as f64)))
        .clamp(f64::EPSILON, 1.0 - f64::EPSILON);
    Ok(if particle_index_within_stratum < mirror {
        unit
    } else {
        1.0 - unit
    })
}

fn sample_log_space_latin_hypercube(
    range: BroadUniformRange,
    stratum: StratumId,
    particle_index_within_stratum: usize,
    particles_in_stratum: usize,
) -> Result<f64, BroadFlightError> {
    if range.minimum == range.maximum {
        return Ok(range.minimum);
    }
    let jitter = balanced_latin_hypercube_jitter(
        stratum,
        particle_index_within_stratum,
        particles_in_stratum,
    )?;
    let quantile = (particle_index_within_stratum as f64 + jitter) / particles_in_stratum as f64;
    Ok((range.minimum.ln() + quantile * (range.maximum / range.minimum).ln()).exp())
}

#[cfg(test)]
mod tests {
    use mh370_domain::{great_circle_distance_nm, Microseconds, SatcomObservation, Vec3};
    use mh370_dynamics::{
        Era5Grid, MagneticAltitudePolicy, PendingRenewal, PoweredLateralModeWeights, RenewalClock,
    };
    use mh370_end_of_flight::DeclaredBroadFuelExtension;
    use mh370_particle_filter::{
        rng_for, run_stratified_bootstrap_filter_with_post_resample_move,
        run_stratified_filter_with_intermediate_potentials,
        run_stratified_filter_with_intermediate_potentials_and_persistent_twist,
        run_stratified_filter_with_root_stratified_transition_pool,
        run_stratified_filter_with_snapshot_retention, Algorithm, FilterConfig,
        PersistentTwistPhase, PersistentTwistStep, RootStratifiedTransitionPoolStep,
        SnapshotRetention, StratifiedFilterPlan, StratifiedPostResampleMoveStep, StratumAllocation,
        WithinStratumResamplingPolicy,
    };
    use mh370_satcom::{BfoConstants, BtoConstants};
    use rand::SeedableRng;

    use super::*;

    fn pending_at(time_s: f64) -> Option<PendingRenewal> {
        Some(PendingRenewal {
            not_before: Seconds(time_s),
            next_event: Seconds(time_s),
        })
    }

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

    fn process(clock: Option<RenewalClock>) -> ManeuverProcess {
        ManeuverProcess {
            lateral_clock: clock,
            speed_clock: clock,
            altitude_clock: clock,
            lateral_mode_weights: PoweredLateralModeWeights {
                constant_true_heading: 1.0,
                constant_magnetic_heading: 0.0,
                constant_true_track: 1.0,
                constant_magnetic_track: 0.0,
                great_circle_track_continuation: 0.0,
            },
            maximum_course_change_deg: 90.0,
            target_mach_min: 0.72,
            target_mach_max: 0.84,
            target_altitude_min_ft: 30_000.0,
            target_altitude_max_ft: 40_000.0,
            great_circle_leg_length_nm: 2_000.0,
        }
    }

    fn fuel_model() -> PoweredFuelModel {
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

    fn config() -> BroadFlightConfig {
        let clock = RenewalClock {
            mean_interval_s: 1_000.0,
            minimum_interval_s: 100.0,
            gamma_shape: 1.5,
        };
        BroadFlightConfig {
            radar_prior: RadarPrior {
                time_s: 0.0,
                latitude_deg: 5.6,
                longitude_deg: 99.0,
                position_sd_nm: 0.01,
                control_mean_deg_true: 180.0,
                control_sd_deg: 0.01,
                mach_min: 0.779,
                mach_max: 0.781,
                altitude_min_ft: 34_990.0,
                altitude_max_ft: 35_010.0,
            },
            initial_vertical_speed_ft_min: BroadUniformRange::fixed(0.0),
            source_fuel: PoweredFuelState {
                time: Seconds(0.0),
                zero_fuel_weight: Kilograms(174_369.0),
                left_usable_feed: Kilograms(17_000.0),
                right_usable_feed: Kilograms(17_000.0),
                reserved_fuel: Kilograms(15.0),
                unusable_fuel: Kilograms(0.0),
                left_exhaustion_time: None,
                right_exhaustion_time: None,
                dual_engine_exhaustion_time: None,
            },
            fuel_uncertainty: BroadFuelUncertainty {
                total_quantity_offset_kg: BroadUniformRange::fixed(0.0),
                flow_scale_log_uniform: BroadUniformRange {
                    minimum: 0.9,
                    maximum: 1.1,
                },
            },
            fuel_model: fuel_model(),
            fuel_flow_shares: EngineFuelFlowShares {
                left: 0.5,
                right: 0.5,
            },
            powered_feasibility: BroadPoweredFeasibilityConfig {
                aerodynamic_family: ConditionalB772AerodynamicFamily::OpenapV2_6_0AttachedFlow,
                thrust_multiplier: 1.25,
                static_thrust_cap_per_engine_n: 411_480.0,
                maximum_additional_drag_coefficient: 0.08,
            },
            limits: limits(),
            integration: PoweredIntegration {
                steady_step_s: 30.0,
                transition_step_s: 5.0,
                heading_capture_tolerance_deg: 0.05,
                maximum_events_per_transition: 30,
            },
            proposal_candidates: 1,
            satcom: SatcomModelConfig {
                bto: BtoConstants {
                    speed_of_light_km_s: 299_792.458,
                    nominal_delay_us: 499_962.0,
                    channel_term_us: 4_283.0,
                },
                bfo: BfoConstants {
                    satellite_afc_hz: 0.0,
                    uplink_hz: 1_646_652_500.0,
                    downlink_hz: 3_615_152_500.0,
                    speed_of_light_km_s: 299_792.458,
                    nominal_satellite_longitude_deg: 64.5,
                    nominal_satellite_altitude_km: 36_210.12,
                },
                bfo_bias_prior_mean_hz: 150.0,
                bfo_bias_prior_sd_hz: 25.0,
            },
            strata: vec![
                BroadFlightStratum {
                    id: StratumId(1),
                    name: "persistent".to_string(),
                    initial_lateral_mode: PoweredLateralMode::ConstantTrueTrack,
                    maneuver_process: process(None),
                },
                BroadFlightStratum {
                    id: StratumId(2),
                    name: "flexible".to_string(),
                    initial_lateral_mode: PoweredLateralMode::ConstantTrueHeading,
                    maneuver_process: process(Some(clock)),
                },
            ],
        }
    }

    fn continuation_model(weather: &Era5Grid, cadence_s: f64) -> BroadFlightModel<'_> {
        let mut config = config();
        config.integration.steady_step_s = cadence_s;
        config.integration.transition_step_s = cadence_s;
        BroadFlightModel::new(
            config,
            PoweredFlightEnvironment {
                weather,
                magnetic: None,
                magnetic_altitude_policy: MagneticAltitudePolicy::ClampToGridAltitude,
                time_origin_unix_s: 1_000.0,
            },
        )
        .unwrap()
    }

    fn continuation_state(
        model: &BroadFlightModel<'_>,
        stratum: StratumId,
        seed: u64,
        left_fuel_kg: f64,
        right_fuel_kg: f64,
    ) -> (BroadFlightState, ChaCha8Rng) {
        let mut rng = ChaCha8Rng::seed_from_u64(seed);
        let mut state = model.initialize_for_stratum(stratum, &mut rng).unwrap();
        assert!(state.is_active());
        state.fuel = PoweredFuelState {
            time: state.powered_flight.aircraft.time,
            zero_fuel_weight: Kilograms(174_369.0),
            left_usable_feed: Kilograms(left_fuel_kg),
            right_usable_feed: Kilograms(right_fuel_kg),
            reserved_fuel: Kilograms(0.0),
            unusable_fuel: Kilograms(0.0),
            left_exhaustion_time: None,
            right_exhaustion_time: None,
            dual_engine_exhaustion_time: None,
        };
        state.fuel_flow_scale = 1.0;
        state.fuel_status = BroadFuelDiagnosticStatus::Valid;
        state.diagnostics = BroadFlightDiagnostics::default();
        (state, rng)
    }

    fn loose_satcom_observation(time_s: f64) -> BroadFlightObservation {
        BroadFlightObservation::Satcom(BroadSatcomObservation {
            flight: FlightObservation {
                id: format!("synthetic-{time_s}"),
                time_utc: "2014-03-09T00:11:00Z".to_string(),
                satellite_afc_hz: 0.0,
                measurement: SatcomObservation {
                    time: Seconds(time_s),
                    satellite_position_km: Vec3::new(18_161.0, 38_060.0, 1_029.0),
                    satellite_velocity_km_s: Vec3::new(0.002, -0.001, -0.046),
                    ground_station_position_km: Vec3::new(-2_368.8, 4_881.1, -3_342.0),
                    bto: Some(Microseconds(12_000.0)),
                    bto_sd: Some(Microseconds(1_000_000.0)),
                    bfo: Some(Hertz(170.0)),
                    bfo_sd: Some(Hertz(1_000_000.0)),
                },
            },
            use_bto: true,
            use_bfo: true,
        })
    }

    fn satcom_observation_with_id(id: &str, time_s: f64) -> BroadFlightObservation {
        let mut observation = loose_satcom_observation(time_s);
        let BroadFlightObservation::Satcom(satcom) = &mut observation else {
            unreachable!("loose SATCOM helper always returns SATCOM")
        };
        satcom.flight.id = id.to_string();
        observation
    }

    fn event_mark_guide_epoch(
        observation_id: &str,
        minimum_lead_s: f64,
        maximum_lookback_s: f64,
        score_temperature: f64,
    ) -> BroadSatcomEventMarkGuideEpoch {
        BroadSatcomEventMarkGuideEpoch {
            observation_id: observation_id.to_string(),
            minimum_lead: Seconds(minimum_lead_s),
            maximum_lookback: Seconds(maximum_lookback_s),
            candidates_per_event: 4,
            defensive_prior_probability: 0.2,
            score_temperature,
        }
    }

    fn event_mark_guide_model<'a>(
        weather: &'a Era5Grid,
        epochs: Vec<BroadSatcomEventMarkGuideEpoch>,
    ) -> BroadFlightModel<'a> {
        let mut config = config();
        let flexible = &mut config.strata[1].maneuver_process;
        flexible.lateral_clock = Some(RenewalClock {
            mean_interval_s: 20_000.0,
            minimum_interval_s: 10_000.0,
            gamma_shape: 1.0,
        });
        flexible.speed_clock = None;
        flexible.altitude_clock = None;
        flexible.maximum_course_change_deg = 10.0;
        BroadFlightModel::new_with_options(
            config,
            PoweredFlightEnvironment {
                weather,
                magnetic: None,
                magnetic_altitude_policy: MagneticAltitudePolicy::ClampToGridAltitude,
                time_origin_unix_s: 1_000.0,
            },
            BroadFlightModelOptions {
                satcom_event_mark_guide: Some(BroadSatcomEventMarkGuideConfig { epochs }),
                ..BroadFlightModelOptions::default()
            },
        )
        .unwrap()
    }

    fn pending_refresh_config() -> BroadPendingRenewalRefreshConfig {
        BroadPendingRenewalRefreshConfig {
            lateral: true,
            speed: true,
            altitude: true,
        }
    }

    fn pending_refresh_model(weather: &Era5Grid, gamma_shape: f64) -> BroadFlightModel<'_> {
        let mut model_config = config();
        model_config.radar_prior.position_sd_nm = 5.0;
        let mut stratum = model_config.strata[1].clone();
        stratum.maneuver_process = process(Some(RenewalClock {
            mean_interval_s: 10_000.0,
            minimum_interval_s: 100.0,
            gamma_shape,
        }));
        model_config.strata = vec![stratum];
        BroadFlightModel::new(
            model_config,
            PoweredFlightEnvironment {
                weather,
                magnetic: None,
                magnetic_altitude_policy: MagneticAltitudePolicy::ClampToGridAltitude,
                time_origin_unix_s: 1_000.0,
            },
        )
        .unwrap()
    }

    fn pending_refresh_context(
        state: BroadFlightState,
        output_slot: usize,
    ) -> StratifiedPostResampleMoveContext {
        StratifiedPostResampleMoveContext {
            observation_index: 1,
            observation_time_s: state.powered_flight.aircraft.time.0,
            stratum: state.stratum,
            output_slot,
            parent_slot: 0,
        }
    }

    fn event_mark_state(model: &BroadFlightModel<'_>, event_time_s: f64) -> BroadFlightState {
        let mut rng = ChaCha8Rng::seed_from_u64(73_019);
        let mut state = model
            .initialize_for_stratum(StratumId(2), &mut rng)
            .unwrap();
        state.powered_flight.event_clocks = PoweredEventClocks {
            lateral: pending_at(event_time_s),
            speed: None,
            altitude: None,
        };
        state
    }

    fn canonical_bridge_points(
        config: BroadSatcomIntermediatePotentialConfig,
        interval_start: Seconds,
        endpoint: &BroadFlightObservation,
    ) -> Vec<IntermediatePotentialBridgePoint<BroadSatcomIntermediatePotentialPoint>> {
        match config.step_for_endpoint(interval_start, endpoint).unwrap() {
            IntermediatePotentialStep::Bridge { points } => points,
            IntermediatePotentialStep::Standard
            | IntermediatePotentialStep::BridgeWithEndpointPool { .. } => {
                panic!("expected an ordinary bridge interval")
            }
        }
    }

    fn fuel_selection_state(
        model: &BroadFlightModel<'_>,
        left_fuel_kg: f64,
        right_fuel_kg: f64,
    ) -> BroadFlightState {
        let (mut state, _) =
            continuation_state(model, StratumId(1), 91_337, left_fuel_kg, right_fuel_kg);
        state.powered_flight.aircraft.time = Seconds(100.0);
        state.powered_flight.aircraft.altitude = Feet(35_000.0);
        state.powered_flight.aircraft.vertical_speed = FeetPerMinute(0.0);
        state.powered_flight.mach = 0.82;
        state.powered_flight.bank_angle = Degrees(0.0);
        state.fuel.time = Seconds(100.0);
        state.diagnostics.fuel_anchor_count = 1;
        state
    }

    fn fuel_selection_point() -> BroadFuelExhaustionSelectionGuidePoint {
        BroadFuelExhaustionSelectionGuidePoint {
            window_start: Seconds(200.0),
            window_end: Seconds(300.0),
        }
    }

    #[test]
    fn powered_limit_activity_is_preserved_for_posterior_audit() {
        let mut diagnostics = BroadFlightDiagnostics::default();
        accumulate_powered_limit_activity(
            &mut diagnostics,
            PoweredLimitActivity {
                stall_or_minimum_mach_floor: true,
                vmo_or_mmo_ceiling: false,
                bank: true,
                roll_rate: false,
                climb_rate: true,
                descent_rate: false,
                vertical_acceleration: true,
                lower_altitude: false,
                upper_altitude: true,
            },
            12.5,
            true,
        );
        accumulate_powered_limit_activity(
            &mut diagnostics,
            PoweredLimitActivity {
                stall_or_minimum_mach_floor: false,
                vmo_or_mmo_ceiling: true,
                bank: false,
                roll_rate: true,
                climb_rate: false,
                descent_rate: true,
                vertical_acceleration: false,
                lower_altitude: true,
                upper_altitude: false,
            },
            7.5,
            false,
        );

        assert_eq!(diagnostics.powered_target_clamp_count, 2);
        assert_eq!(
            diagnostics.powered_boundary_seconds,
            PoweredBoundarySeconds {
                stall_or_minimum_mach_floor: 12.5,
                vmo_or_mmo_ceiling: 7.5,
                bank: 12.5,
                roll_rate: 7.5,
                climb_rate: 12.5,
                descent_rate: 7.5,
                vertical_acceleration: 12.5,
                lower_altitude: 7.5,
                upper_altitude: 12.5,
                magnetic_altitude_clamp: 12.5,
            }
        );
    }

    #[test]
    fn fuel_selection_guide_configuration_and_post_anchor_guard_are_typed() {
        let config = BroadFuelExhaustionSelectionGuideConfig::default();
        config.validate().unwrap();
        assert_eq!(
            config.stable_descriptor(),
            format!(
                "family={BROAD_FUEL_EXHAUSTION_SELECTION_GUIDE_FAMILY};delta=0.02;projection=frozen-current-operating-point-exact-analytic;compatibility=tau>window-start+0.000001s-and-tau<window-end-0.000001s;role=proposal-only-exactly-corrected"
            )
        );
        let guide = BroadFuelExhaustionSelectionGuide::new(config).unwrap();
        assert_eq!(
            guide.persistent_twist_stable_descriptor(),
            format!(
                "family={BROAD_FUEL_EXHAUSTION_SELECTION_GUIDE_FAMILY};delta=0.02;projection=frozen-current-operating-point-exact-analytic;compatibility=tau>window-start+0.000001s-and-tau<window-end-0.000001s;role=proposal-only-exactly-corrected;persistent-twist-family={BROAD_FUEL_EXHAUSTION_PERSISTENT_TWIST_FAMILY};persistent-target=physical-filter-times-potential;finalization=single-global-inverse-potential-no-resampling;scientific-evidence=none"
            )
        );
        for potential_floor in [0.0, -0.1, 1.1, f64::NAN] {
            assert!(BroadFuelExhaustionSelectionGuideConfig { potential_floor }
                .validate()
                .is_err());
        }
        assert!(BroadFuelExhaustionSelectionGuidePoint {
            window_start: Seconds(300.0),
            window_end: Seconds(300.0),
        }
        .validate()
        .is_err());

        let weather = constant_weather();
        let model = continuation_model(&weather, 60.0);
        let mut state = fuel_selection_state(&model, 105.0, 105.0);
        let endpoint = loose_satcom_observation(150.0);
        state.diagnostics.fuel_anchor_count = 0;
        assert!(matches!(
            guide.evaluate(&model, &state, &endpoint, &fuel_selection_point()),
            Err(BroadFlightError::InvalidFuelSelectionGuideState)
        ));
        state.diagnostics.fuel_anchor_count = 1;
        let anchor_endpoint = BroadFlightObservation::FuelAnchor(BroadFuelAnchorObservation {
            id: "unexpected-anchor".to_string(),
            time: Seconds(150.0),
            zero_fuel_weight_kg: 174_369.0,
            total_onboard_fuel_kg: 200.0,
            reserved_fuel_kg: 0.0,
            unusable_fuel_kg: 0.0,
            left_usable_fraction: 0.5,
        });
        assert!(matches!(
            guide.evaluate(&model, &state, &anchor_endpoint, &fuel_selection_point()),
            Err(BroadFlightError::InvalidFuelSelectionGuideState)
        ));
        let mut desynchronized = state;
        desynchronized.fuel.time = Seconds(99.0);
        assert!(matches!(
            guide.evaluate(&model, &desynchronized, &endpoint, &fuel_selection_point()),
            Err(BroadFlightError::InvalidFuelSelectionGuideState)
        ));
        assert!(matches!(
            guide.evaluate(
                &model,
                &state,
                &loose_satcom_observation(250.0),
                &fuel_selection_point()
            ),
            Err(BroadFlightError::InvalidFuelSelectionGuideState)
        ));
    }

    #[test]
    fn fuel_selection_guide_is_pure_and_independent_of_satcom_values() {
        let weather = constant_weather();
        let model = continuation_model(&weather, 60.0);
        let guide = BroadFuelExhaustionSelectionGuide::default();
        let state = fuel_selection_state(&model, 105.0, 105.0);
        let before = state;
        let endpoint = loose_satcom_observation(150.0);
        let evaluation = guide
            .evaluate(&model, &state, &endpoint, &fuel_selection_point())
            .unwrap();
        assert_eq!(state, before);
        assert_eq!(
            evaluation.outcome,
            BroadFuelExhaustionSelectionGuideOutcome::Compatible
        );
        let exhaustion = evaluation.projected_dual_engine_exhaustion_time.unwrap();
        assert!((exhaustion.0 - 241.2).abs() < 0.5);
        assert_eq!(evaluation.log_selection_guide, 0.0);

        let mut changed_satcom = endpoint.clone();
        let BroadFlightObservation::Satcom(satcom) = &mut changed_satcom else {
            unreachable!()
        };
        satcom.flight.measurement.bto = Some(Microseconds(500_000.0));
        satcom.flight.measurement.bfo = Some(Hertz(-20_000.0));
        let changed = guide
            .evaluate(&model, &state, &changed_satcom, &fuel_selection_point())
            .unwrap();
        assert_eq!(evaluation, changed);
        let selection_log_potential = SelectionGuide::log_selection_guide(
            &guide,
            &model,
            &state,
            &changed_satcom,
            &fuel_selection_point(),
        )
        .unwrap();
        let twist_log_potential = PersistentTwist::log_twist_potential(
            &guide,
            &model,
            &state,
            &changed_satcom,
            &fuel_selection_point(),
        )
        .unwrap();
        assert_eq!(selection_log_potential, 0.0);
        assert_eq!(
            selection_log_potential.to_bits(),
            twist_log_potential.to_bits()
        );
        assert_eq!(state, before);
    }

    #[test]
    fn fuel_selection_guide_classifies_strict_window_and_floor_outcomes() {
        let weather = constant_weather();
        let model = continuation_model(&weather, 60.0);
        let guide = BroadFuelExhaustionSelectionGuide::default();
        let endpoint = loose_satcom_observation(150.0);
        let state = fuel_selection_state(&model, 105.0, 105.0);
        let compatible = guide
            .evaluate(&model, &state, &endpoint, &fuel_selection_point())
            .unwrap();
        let exhaustion = compatible.projected_dual_engine_exhaustion_time.unwrap();
        let floor = BroadFuelExhaustionSelectionGuideConfig::default()
            .potential_floor
            .ln();

        let starts_at_exhaustion = BroadFuelExhaustionSelectionGuidePoint {
            window_start: exhaustion,
            window_end: Seconds(exhaustion.0 + 50.0),
        };
        let at_start = guide
            .evaluate(&model, &state, &endpoint, &starts_at_exhaustion)
            .unwrap();
        assert_eq!(
            at_start.outcome,
            BroadFuelExhaustionSelectionGuideOutcome::OutsideWindow
        );
        assert_eq!(at_start.log_selection_guide, floor);
        assert_eq!(
            PersistentTwist::log_twist_potential(
                &guide,
                &model,
                &state,
                &endpoint,
                &starts_at_exhaustion,
            )
            .unwrap()
            .to_bits(),
            at_start.log_selection_guide.to_bits()
        );
        let within_start_tolerance = BroadFuelExhaustionSelectionGuidePoint {
            window_start: Seconds(exhaustion.0 - 0.5 * FUEL_SELECTION_WINDOW_TOLERANCE_S),
            window_end: Seconds(exhaustion.0 + 50.0),
        };
        assert_eq!(
            guide
                .evaluate(&model, &state, &endpoint, &within_start_tolerance)
                .unwrap()
                .outcome,
            BroadFuelExhaustionSelectionGuideOutcome::OutsideWindow
        );
        let beyond_start_tolerance = BroadFuelExhaustionSelectionGuidePoint {
            window_start: Seconds(exhaustion.0 - 2.0 * FUEL_SELECTION_WINDOW_TOLERANCE_S),
            window_end: Seconds(exhaustion.0 + 50.0),
        };
        assert_eq!(
            guide
                .evaluate(&model, &state, &endpoint, &beyond_start_tolerance)
                .unwrap()
                .outcome,
            BroadFuelExhaustionSelectionGuideOutcome::Compatible
        );

        let endpoint_before_window = loose_satcom_observation(100.5);
        let ends_at_exhaustion = BroadFuelExhaustionSelectionGuidePoint {
            window_start: Seconds(101.0),
            window_end: exhaustion,
        };
        let at_end = guide
            .evaluate(&model, &state, &endpoint_before_window, &ends_at_exhaustion)
            .unwrap();
        assert_eq!(
            at_end.outcome,
            BroadFuelExhaustionSelectionGuideOutcome::OutsideWindow
        );
        assert_eq!(at_end.log_selection_guide, floor);
        assert_eq!(
            PersistentTwist::log_twist_potential(
                &guide,
                &model,
                &state,
                &endpoint_before_window,
                &ends_at_exhaustion,
            )
            .unwrap()
            .to_bits(),
            at_end.log_selection_guide.to_bits()
        );

        let early = fuel_selection_state(&model, 5.0, 5.0);
        let early = guide
            .evaluate(&model, &early, &endpoint, &fuel_selection_point())
            .unwrap();
        assert_eq!(
            early.outcome,
            BroadFuelExhaustionSelectionGuideOutcome::OutsideWindow
        );
        let late = fuel_selection_state(&model, 500.0, 500.0);
        let late = guide
            .evaluate(&model, &late, &endpoint, &fuel_selection_point())
            .unwrap();
        assert_eq!(
            late.outcome,
            BroadFuelExhaustionSelectionGuideOutcome::NoExhaustionByBound
        );

        let mut already = fuel_selection_state(&model, 0.0, 0.0);
        already.fuel.left_exhaustion_time = Some(Seconds(90.0));
        already.fuel.right_exhaustion_time = Some(Seconds(90.0));
        already.fuel.dual_engine_exhaustion_time = Some(Seconds(90.0));
        let already = guide
            .evaluate(&model, &already, &endpoint, &fuel_selection_point())
            .unwrap();
        assert_eq!(
            already.outcome,
            BroadFuelExhaustionSelectionGuideOutcome::AlreadyExhausted
        );

        let mut inactive = state;
        inactive.status = BroadFlightParticleStatus::Rejected {
            reason: BroadRejectionReason::PoweredSegmentInfeasible,
            at_time: Seconds(100.0),
        };
        let inactive = guide
            .evaluate(&model, &inactive, &endpoint, &fuel_selection_point())
            .unwrap();
        assert_eq!(
            inactive.outcome,
            BroadFuelExhaustionSelectionGuideOutcome::InactiveParticle
        );

        let mut unavailable = state;
        unavailable.powered_flight.aircraft.altitude = Feet(24_000.0);
        let unavailable = guide
            .evaluate(&model, &unavailable, &endpoint, &fuel_selection_point())
            .unwrap();
        assert_eq!(
            unavailable.outcome,
            BroadFuelExhaustionSelectionGuideOutcome::FuelModelUnavailable
        );
        for evaluation in [early, late, already, inactive, unavailable] {
            assert_eq!(evaluation.log_selection_guide, floor);
        }
    }

    #[test]
    fn neutral_fuel_selection_guide_is_exactly_one_for_every_outcome() {
        let weather = constant_weather();
        let model = continuation_model(&weather, 60.0);
        let guide =
            BroadFuelExhaustionSelectionGuide::new(BroadFuelExhaustionSelectionGuideConfig {
                potential_floor: 1.0,
            })
            .unwrap();
        let endpoint = loose_satcom_observation(150.0);
        for fuel in [5.0, 105.0, 500.0] {
            let state = fuel_selection_state(&model, fuel, fuel);
            assert_eq!(
                guide
                    .evaluate(&model, &state, &endpoint, &fuel_selection_point())
                    .unwrap()
                    .log_selection_guide,
                0.0
            );
        }
    }

    #[test]
    fn persistent_fuel_twist_finalizes_to_physical_weights_and_evidence() {
        let weather = constant_weather();
        let mut model_config = config();
        model_config.fuel_uncertainty.flow_scale_log_uniform = BroadUniformRange::fixed(1.0);
        model_config.strata.truncate(1);
        let model = BroadFlightModel::new(
            model_config,
            PoweredFlightEnvironment {
                weather: &weather,
                magnetic: None,
                magnetic_altitude_policy: MagneticAltitudePolicy::ClampToGridAltitude,
                time_origin_unix_s: 1_000.0,
            },
        )
        .unwrap();
        let observations = [
            BroadFlightObservation::FuelAnchor(BroadFuelAnchorObservation {
                id: "synthetic-fuel-anchor".to_string(),
                time: Seconds(0.9),
                zero_fuel_weight_kg: 174_369.0,
                total_onboard_fuel_kg: 33_524.104_881_96,
                reserved_fuel_kg: 15.0,
                unusable_fuel_kg: 0.0,
                left_usable_fraction: 0.5,
            }),
            BroadFlightObservation::Checkpoint {
                id: "twist-activation".to_string(),
                time: Seconds(60.0),
            },
            BroadFlightObservation::Checkpoint {
                id: "twist-finalization".to_string(),
                time: Seconds(120.0),
            },
        ];
        let point = BroadFuelExhaustionSelectionGuidePoint {
            window_start: Seconds(1_000.0),
            window_end: Seconds(1_100.0),
        };
        let intermediate_steps = [
            IntermediatePotentialStep::Standard,
            IntermediatePotentialStep::Standard,
            IntermediatePotentialStep::Standard,
        ];
        let twist_steps = [
            PersistentTwistStep::Inactive,
            PersistentTwistStep::Activate { point },
            PersistentTwistStep::Finalize { point },
        ];
        let filter = FilterConfig {
            particles: 8,
            seed: 370_120,
            algorithm: Algorithm::Bootstrap,
            initial_time_s: 0.0,
            ess_resample_fraction: 0.5,
        };
        let plan = StratifiedFilterPlan {
            strata: vec![StratumAllocation {
                id: StratumId(1),
                particles: 8,
                log_prior_probability: 0.0,
            }],
        };
        let bridge = BroadSatcomIntermediatePotentialBridge::default();
        let run = |guide: &BroadFuelExhaustionSelectionGuide| {
            run_stratified_filter_with_intermediate_potentials_and_persistent_twist(
                &model,
                &bridge,
                guide,
                &observations,
                &filter,
                &plan,
                &SnapshotRetention::All,
                WithinStratumResamplingPolicy {
                    uniform_root_mixture_epsilon: 0.1,
                },
                &intermediate_steps,
                &twist_steps,
            )
            .unwrap()
        };
        let guided = run(&BroadFuelExhaustionSelectionGuide::default());
        let neutral = run(&BroadFuelExhaustionSelectionGuide::new(
            BroadFuelExhaustionSelectionGuideConfig {
                potential_floor: 1.0,
            },
        )
        .unwrap());

        assert_eq!(guided.persistent_twist_checkpoints.len(), 2);
        let activation = &guided.persistent_twist_checkpoints[0];
        assert_eq!(activation.observation_index, 1);
        assert_eq!(activation.phase, PersistentTwistPhase::Activate);
        assert!(activation.output_is_twisted);
        assert!((activation.twisted_target_log_evidence_increment - 0.02_f64.ln()).abs() < 1.0e-12);
        assert_eq!(activation.final_untwist_log_evidence_correction, None);
        let finalization = &guided.persistent_twist_checkpoints[1];
        assert_eq!(finalization.observation_index, 2);
        assert_eq!(finalization.phase, PersistentTwistPhase::Finalize);
        assert!(!finalization.output_is_twisted);
        assert!(
            (finalization.final_untwist_log_evidence_correction.unwrap() + 0.02_f64.ln()).abs()
                < 1.0e-12
        );
        assert_eq!(guided.twisted_filtering_observation_indices, vec![1]);
        assert!(guided.pooled.log_evidence.abs() < 1.0e-12);
        assert!(guided.pooled.checkpoints[2].cumulative_log_evidence.abs() < 1.0e-12);
        assert_eq!(guided.pooled.particles, neutral.pooled.particles);
        assert_eq!(guided.pooled.log_weights, neutral.pooled.log_weights);
        assert_eq!(guided.pooled.root_ids, neutral.pooled.root_ids);
        assert_eq!(guided.pooled.ancestry, neutral.pooled.ancestry);
        let final_snapshot = guided.pooled.snapshots.last().unwrap();
        assert_eq!(final_snapshot.observation_index, Some(2));
        assert_eq!(final_snapshot.log_weights, guided.pooled.log_weights);
        assert!(guided.pooled.particles.iter().all(|state| {
            state.is_active()
                && state.diagnostics.fuel_anchor_count == 1
                && state.scores.bto_observations == 0
                && state.scores.bfo_observations == 0
        }));
    }

    #[test]
    fn satcom_intermediate_schedule_is_typed_and_has_exact_boundaries() {
        let guide = BroadSatcomIntermediatePotentialConfig::default();
        guide.validate().unwrap();
        let endpoint = loose_satcom_observation(3_000.0);
        let points = canonical_bridge_points(guide, Seconds(0.0), &endpoint);
        assert_eq!(points.len(), 2);
        assert_eq!(points[0].point.time, Seconds(1_800.0));
        assert_eq!(points[0].candidates_per_particle, 2);
        assert_eq!(
            points[0].point.kind,
            BroadSatcomIntermediatePotentialPointKind::EarlyBtoOnly
        );
        assert_eq!(points[1].point.time, Seconds(2_940.0));
        assert_eq!(points[1].candidates_per_particle, 4);
        assert_eq!(
            points[1].point.kind,
            BroadSatcomIntermediatePotentialPointKind::LateEnabledSatcom
        );
        let mut bto_only = loose_satcom_observation(3_600.0);
        let BroadFlightObservation::Satcom(satcom) = &mut bto_only else {
            unreachable!()
        };
        satcom.use_bfo = false;
        assert_eq!(
            canonical_bridge_points(guide, Seconds(0.0), &bto_only).len(),
            2
        );

        assert!(matches!(
            guide
                .step_for_endpoint(Seconds(0.0), &loose_satcom_observation(2_999.0))
                .unwrap(),
            IntermediatePotentialStep::Standard
        ));
        let mut bfo_only = loose_satcom_observation(3_600.0);
        let BroadFlightObservation::Satcom(satcom) = &mut bfo_only else {
            unreachable!()
        };
        satcom.use_bto = false;
        assert!(matches!(
            guide.step_for_endpoint(Seconds(0.0), &bfo_only).unwrap(),
            IntermediatePotentialStep::Standard
        ));
        assert!(matches!(
            guide
                .step_for_endpoint(
                    Seconds(0.0),
                    &BroadFlightObservation::Checkpoint {
                        id: "held-out".to_string(),
                        time: Seconds(3_600.0),
                    },
                )
                .unwrap(),
            IntermediatePotentialStep::Standard
        ));

        let mut neutral = guide;
        neutral.potential_floor = 1.0;
        neutral.validate().unwrap();
        let mut invalid = guide;
        invalid.minimum_interval = invalid.late_offset;
        assert!(matches!(
            invalid.validate(),
            Err(BroadFlightError::InvalidConfiguration(_))
        ));
        assert!(guide
            .stable_descriptor()
            .contains("bto-process=900us-per-remaining-hour"));
    }

    #[test]
    fn exact_intermediate_filter_assimilates_only_the_physical_endpoint() {
        let weather = constant_weather();
        let model = BroadFlightModel::new(
            config(),
            PoweredFlightEnvironment {
                weather: &weather,
                magnetic: None,
                magnetic_altitude_policy: MagneticAltitudePolicy::ClampToGridAltitude,
                time_origin_unix_s: 1_000.0,
            },
        )
        .unwrap();
        let guide_config = BroadSatcomIntermediatePotentialConfig::default();
        let bridge = BroadSatcomIntermediatePotentialBridge::new(guide_config).unwrap();
        let observations = [loose_satcom_observation(3_600.0)];
        let steps = [guide_config
            .step_for_endpoint(Seconds(0.0), &observations[0])
            .unwrap()];
        let result = run_stratified_filter_with_intermediate_potentials(
            &model,
            &bridge,
            &observations,
            &FilterConfig {
                particles: 8,
                seed: 37_000,
                algorithm: Algorithm::Bootstrap,
                initial_time_s: 0.0,
                ess_resample_fraction: 0.5,
            },
            &StratifiedFilterPlan {
                strata: vec![StratumAllocation {
                    id: StratumId(1),
                    particles: 8,
                    log_prior_probability: 0.0,
                }],
            },
            &SnapshotRetention::All,
            WithinStratumResamplingPolicy {
                uniform_root_mixture_epsilon: 0.1,
            },
            &steps,
        )
        .unwrap();
        assert_eq!(result.intermediate_potential_checkpoints.len(), 1);
        assert_eq!(result.intermediate_potential_checkpoints[0].points.len(), 2);
        // Only the ordinary initial and physical-endpoint snapshots exist;
        // ephemeral guide points cannot become handoff checkpoints.
        assert_eq!(result.pooled.snapshots.len(), 2);
        assert_eq!(result.pooled.snapshots[0].observation_index, None);
        assert_eq!(result.pooled.snapshots[1].observation_index, Some(0));
        assert!(result.pooled.particles.iter().all(|state| {
            state.scores.bto_observations == 1
                && state.scores.bfo_observations == 1
                && (state.powered_flight.aircraft.time.0 - 3_600.0).abs() < TIME_TOLERANCE_S
        }));
    }

    #[test]
    fn neutral_satcom_potentials_are_exactly_one_and_do_not_assimilate() {
        let weather = constant_weather();
        let model = BroadFlightModel::new(
            config(),
            PoweredFlightEnvironment {
                weather: &weather,
                magnetic: None,
                magnetic_altitude_policy: MagneticAltitudePolicy::ClampToGridAltitude,
                time_origin_unix_s: 1_000.0,
            },
        )
        .unwrap();
        let guide_config = BroadSatcomIntermediatePotentialConfig {
            potential_floor: 1.0,
            ..BroadSatcomIntermediatePotentialConfig::default()
        };
        let bridge = BroadSatcomIntermediatePotentialBridge::new(guide_config).unwrap();
        let endpoint = loose_satcom_observation(3_600.0);
        let points = canonical_bridge_points(guide_config, Seconds(0.0), &endpoint);
        let mut rng = ChaCha8Rng::seed_from_u64(37_011);
        let initial = model
            .initialize_for_stratum(StratumId(1), &mut rng)
            .unwrap();
        let initial_scores = initial.scores;
        let initial_bias = initial.bfo_bias;
        let context = bridge.begin_interval(&model, &initial, &endpoint).unwrap();
        let first = bridge
            .propose_to_point(
                &model,
                &initial,
                &endpoint,
                &points[0].point,
                &context,
                1_800.0,
                &mut rng,
            )
            .unwrap();
        let first_before_potential = first.proposal.state;
        assert_eq!(
            bridge
                .log_potential(&model, &first.proposal.state, &endpoint, &points[0].point)
                .unwrap(),
            0.0
        );
        assert_eq!(first.proposal.state, first_before_potential);
        assert_eq!(first.proposal.state.scores, initial_scores);
        assert_eq!(first.proposal.state.bfo_bias, initial_bias);

        let second = bridge
            .propose_to_point(
                &model,
                &first.proposal.state,
                &endpoint,
                &points[1].point,
                &first.context,
                1_140.0,
                &mut rng,
            )
            .unwrap();
        let second_before_potential = second.proposal.state;
        assert_eq!(
            bridge
                .log_potential(&model, &second.proposal.state, &endpoint, &points[1].point)
                .unwrap(),
            0.0
        );
        assert_eq!(second.proposal.state, second_before_potential);
        assert_eq!(second.proposal.state.scores, initial_scores);
        assert_eq!(second.proposal.state.bfo_bias, initial_bias);

        let mut endpoint_state = bridge
            .propose_to_endpoint(
                &model,
                &second.proposal.state,
                &endpoint,
                &second.context,
                660.0,
                &mut rng,
            )
            .unwrap()
            .state;
        assert_eq!(endpoint_state.scores, initial_scores);
        assert_eq!(endpoint_state.bfo_bias, initial_bias);
        let likelihood = model.observe(&mut endpoint_state, &endpoint).unwrap();
        assert!(likelihood.is_finite());
        assert_eq!(endpoint_state.scores.bto_observations, 1);
        assert_eq!(endpoint_state.scores.bfo_observations, 1);
    }

    #[test]
    fn satcom_potential_matches_remaining_hour_process_scales_and_bias_variance() {
        let weather = constant_weather();
        let model = BroadFlightModel::new(
            config(),
            PoweredFlightEnvironment {
                weather: &weather,
                magnetic: None,
                magnetic_altitude_policy: MagneticAltitudePolicy::ClampToGridAltitude,
                time_origin_unix_s: 1_000.0,
            },
        )
        .unwrap();
        let bridge = BroadSatcomIntermediatePotentialBridge::default();
        let mut endpoint = loose_satcom_observation(3_600.0);
        let points = canonical_bridge_points(bridge.config(), Seconds(0.0), &endpoint);
        let mut rng = ChaCha8Rng::seed_from_u64(98_771);
        let initial = model
            .initialize_for_stratum(StratumId(1), &mut rng)
            .unwrap();
        let context = bridge.begin_interval(&model, &initial, &endpoint).unwrap();
        let first = bridge
            .propose_to_point(
                &model,
                &initial,
                &endpoint,
                &points[0].point,
                &context,
                1_800.0,
                &mut rng,
            )
            .unwrap();
        let second = bridge
            .propose_to_point(
                &model,
                &first.proposal.state,
                &endpoint,
                &points[1].point,
                &first.context,
                1_140.0,
                &mut rng,
            )
            .unwrap();

        let endpoint_time = endpoint.time();
        let independently_project = |state: BroadFlightState| {
            let aircraft = state.powered_flight.aircraft;
            let remaining_s = endpoint_time.0 - aircraft.time.0;
            AircraftState {
                time: endpoint_time,
                position: destination_wgs84(
                    aircraft.position,
                    aircraft.track_true,
                    NauticalMiles(aircraft.ground_speed.0 * remaining_s / 3_600.0),
                )
                .unwrap(),
                altitude: Feet(
                    (aircraft.altitude.0 + aircraft.vertical_speed.0 * remaining_s / 60.0).clamp(
                        model.config.limits.minimum_pressure_altitude_ft,
                        model.config.limits.maximum_pressure_altitude_ft,
                    ),
                ),
                track_true: aircraft.track_true,
                ground_speed: aircraft.ground_speed,
                vertical_speed: aircraft.vertical_speed,
                bfo_bias: Hertz(state.bfo_bias.mean_hz),
            }
        };
        let late_projected = independently_project(second.proposal.state);
        let BroadFlightObservation::Satcom(satcom) = &mut endpoint else {
            unreachable!()
        };
        let late_bto = bto(
            late_projected.position,
            late_projected.altitude.0,
            satcom.flight.measurement.satellite_position_km,
            satcom.flight.measurement.ground_station_position_km,
            model.config.satcom.bto,
        );
        let mut bfo_constants = model.config.satcom.bfo;
        bfo_constants.satellite_afc_hz = satcom.flight.satellite_afc_hz;
        let late_bfo = bfo_components(
            late_projected,
            satcom.flight.measurement.satellite_position_km,
            satcom.flight.measurement.satellite_velocity_km_s,
            satcom.flight.measurement.ground_station_position_km,
            bfo_constants,
        )
        .base_without_bias
        .0;
        satcom.flight.measurement.bto = Some(Microseconds(late_bto.0 + 100.0));
        satcom.flight.measurement.bto_sd = Some(Microseconds(40.0));
        satcom.flight.measurement.bfo = Some(Hertz(
            late_bfo + second.proposal.state.bfo_bias.mean_hz + 20.0,
        ));
        satcom.flight.measurement.bfo_sd = Some(Hertz(3.0));

        let early_projected = independently_project(first.proposal.state);
        let BroadFlightObservation::Satcom(satcom) = &endpoint else {
            unreachable!()
        };
        let early_bto = bto(
            early_projected.position,
            early_projected.altitude.0,
            satcom.flight.measurement.satellite_position_km,
            satcom.flight.measurement.ground_station_position_km,
            model.config.satcom.bto,
        );
        let early_residual = satcom.flight.measurement.bto.unwrap().0 - early_bto.0;
        let early_sd = 40.0_f64.hypot(900.0 * 0.5);
        let early_q = (early_residual / early_sd).powi(2);
        let expected_early = (0.02 + 0.98 * (-0.5 * early_q).exp()).ln();
        let actual_early = bridge
            .log_potential(&model, &first.proposal.state, &endpoint, &points[0].point)
            .unwrap();
        assert!((actual_early - expected_early).abs() < 1.0e-12);

        let late_remaining_hours = (3_600.0 - 2_940.0) / 3_600.0;
        let late_bto_sd = 40.0_f64.hypot(900.0 * late_remaining_hours);
        let late_bfo_variance = 3.0_f64.powi(2)
            + second.proposal.state.bfo_bias.variance_hz2
            + (60.0 * late_remaining_hours).powi(2);
        let late_q = (100.0 / late_bto_sd).powi(2) + 20.0_f64.powi(2) / late_bfo_variance;
        let expected_late = (0.02 + 0.98 * (-0.5 * late_q).exp()).ln();
        let state_before = second.proposal.state;
        let actual_late = bridge
            .log_potential(&model, &second.proposal.state, &endpoint, &points[1].point)
            .unwrap();
        assert!((actual_late - expected_late).abs() < 1.0e-12);
        assert_eq!(second.proposal.state, state_before);
        assert_eq!(second.proposal.state.bfo_bias, initial.bfo_bias);
        assert_eq!(second.proposal.state.scores, initial.scores);

        let mut bto_only_endpoint = endpoint.clone();
        if let BroadFlightObservation::Satcom(bto_only) = &mut bto_only_endpoint {
            bto_only.use_bfo = false;
        } else {
            unreachable!();
        }
        let bto_only_log = bridge
            .log_potential(
                &model,
                &second.proposal.state,
                &bto_only_endpoint,
                &points[1].point,
            )
            .unwrap();
        if let BroadFlightObservation::Satcom(bto_only) = &mut bto_only_endpoint {
            bto_only.flight.measurement.bfo = Some(Hertz(1.0e9));
        } else {
            unreachable!();
        }
        assert_eq!(
            bridge
                .log_potential(
                    &model,
                    &second.proposal.state,
                    &bto_only_endpoint,
                    &points[1].point,
                )
                .unwrap(),
            bto_only_log
        );
    }

    #[test]
    fn terminal_tangent_guide_clamps_altitude_to_declared_limits() {
        let weather = constant_weather();
        let model = BroadFlightModel::new(
            config(),
            PoweredFlightEnvironment {
                weather: &weather,
                magnetic: None,
                magnetic_altitude_policy: MagneticAltitudePolicy::ClampToGridAltitude,
                time_origin_unix_s: 1_000.0,
            },
        )
        .unwrap();
        let bridge = BroadSatcomIntermediatePotentialBridge::default();
        let mut rng = ChaCha8Rng::seed_from_u64(82);
        let mut state = model
            .initialize_for_stratum(StratumId(1), &mut rng)
            .unwrap();
        state.powered_flight.aircraft.time = Seconds(1_800.0);
        state.fuel.time = Seconds(1_800.0);
        state.powered_flight.aircraft.vertical_speed = FeetPerMinute(4_000.0);
        let upper = bridge
            .terminal_tangent_projection(&model, &state, Seconds(3_600.0))
            .unwrap();
        assert_eq!(
            upper.altitude,
            Feet(model.config.limits.maximum_pressure_altitude_ft)
        );
        state.powered_flight.aircraft.vertical_speed = FeetPerMinute(-4_000.0);
        let lower = bridge
            .terminal_tangent_projection(&model, &state, Seconds(3_600.0))
            .unwrap();
        assert_eq!(
            lower.altitude,
            Feet(model.config.limits.minimum_pressure_altitude_ft)
        );
        assert_eq!(upper.vertical_speed, FeetPerMinute(4_000.0));
        assert_eq!(lower.vertical_speed, FeetPerMinute(-4_000.0));
    }

    #[test]
    fn split_satcom_transition_enforces_one_cumulative_event_budget() {
        let weather = constant_weather();
        let mut model_config = config();
        model_config.integration.maximum_events_per_transition = 1;
        model_config.strata[0]
            .maneuver_process
            .maximum_course_change_deg = 0.1;
        let model = BroadFlightModel::new(
            model_config,
            PoweredFlightEnvironment {
                weather: &weather,
                magnetic: None,
                magnetic_altitude_policy: MagneticAltitudePolicy::ClampToGridAltitude,
                time_origin_unix_s: 1_000.0,
            },
        )
        .unwrap();
        let bridge = BroadSatcomIntermediatePotentialBridge::default();
        let endpoint = loose_satcom_observation(3_600.0);
        let points = canonical_bridge_points(bridge.config(), Seconds(0.0), &endpoint);
        let mut rng = ChaCha8Rng::seed_from_u64(19);
        let mut initial = model
            .initialize_for_stratum(StratumId(1), &mut rng)
            .unwrap();
        initial.powered_flight.event_clocks.lateral = pending_at(1_000.0);
        initial.powered_flight.event_clocks.speed = pending_at(2_500.0);
        initial.powered_flight.event_clocks.altitude = None;
        let context = bridge.begin_interval(&model, &initial, &endpoint).unwrap();
        let first = bridge
            .propose_to_point(
                &model,
                &initial,
                &endpoint,
                &points[0].point,
                &context,
                1_800.0,
                &mut rng,
            )
            .unwrap();
        assert!(first.proposal.state.is_active());
        assert_eq!(first.context.event_budget.consumed.total(), 1);
        let second = bridge
            .propose_to_point(
                &model,
                &first.proposal.state,
                &endpoint,
                &points[1].point,
                &first.context,
                1_140.0,
                &mut rng,
            )
            .unwrap();
        assert!(matches!(
            second.proposal.state.status,
            BroadFlightParticleStatus::Rejected {
                reason: BroadRejectionReason::ComputationalEventLimit,
                ..
            }
        ));
        assert!(second.context.event_budget.consumed.total() > 1);
        assert_eq!(
            bridge
                .log_potential(&model, &second.proposal.state, &endpoint, &points[1].point)
                .unwrap(),
            bridge.config().potential_floor.ln()
        );
        let mut rejected_endpoint = bridge
            .propose_to_endpoint(
                &model,
                &second.proposal.state,
                &endpoint,
                &second.context,
                660.0,
                &mut rng,
            )
            .unwrap()
            .state;
        assert_eq!(
            model.observe(&mut rejected_endpoint, &endpoint).unwrap(),
            f64::NEG_INFINITY
        );
    }

    #[test]
    fn neutral_bridge_subdivision_preserves_random_event_cadence_within_one_nm() {
        let weather = constant_weather();
        let mut model_config = config();
        model_config.integration.steady_step_s = 60.0;
        model_config.integration.transition_step_s = 15.0;
        model_config.integration.maximum_events_per_transition = 100;
        model_config.strata[1]
            .maneuver_process
            .maximum_course_change_deg = 20.0;
        model_config.strata[1].maneuver_process.target_mach_min = 0.76;
        model_config.strata[1].maneuver_process.target_mach_max = 0.82;
        model_config.strata[1]
            .maneuver_process
            .target_altitude_min_ft = 33_000.0;
        model_config.strata[1]
            .maneuver_process
            .target_altitude_max_ft = 37_000.0;
        let model = BroadFlightModel::new(
            model_config,
            PoweredFlightEnvironment {
                weather: &weather,
                magnetic: None,
                magnetic_altitude_policy: MagneticAltitudePolicy::ClampToGridAltitude,
                time_origin_unix_s: 1_000.0,
            },
        )
        .unwrap();
        let guide_config = BroadSatcomIntermediatePotentialConfig {
            potential_floor: 1.0,
            ..BroadSatcomIntermediatePotentialConfig::default()
        };
        let bridge = BroadSatcomIntermediatePotentialBridge::new(guide_config).unwrap();
        let endpoint = loose_satcom_observation(3_600.0);
        let points = canonical_bridge_points(guide_config, Seconds(0.0), &endpoint);
        let mut maximum_endpoint_separation_nm = 0.0_f64;
        let mut histories_with_events = 0;

        for seed in 0..16 {
            let mut initialization_rng = ChaCha8Rng::seed_from_u64(90_000 + seed);
            let initial = model
                .initialize_for_stratum(StratumId(2), &mut initialization_rng)
                .unwrap();
            let mut direct_rng = initialization_rng.clone();
            let direct = model
                .propagate_without_observation(&initial, endpoint.time(), &mut direct_rng)
                .unwrap();
            let mut split_rng = initialization_rng;
            let context = bridge.begin_interval(&model, &initial, &endpoint).unwrap();
            let first = bridge
                .propose_to_point(
                    &model,
                    &initial,
                    &endpoint,
                    &points[0].point,
                    &context,
                    1_800.0,
                    &mut split_rng,
                )
                .unwrap();
            let second = bridge
                .propose_to_point(
                    &model,
                    &first.proposal.state,
                    &endpoint,
                    &points[1].point,
                    &first.context,
                    1_140.0,
                    &mut split_rng,
                )
                .unwrap();
            let split = bridge
                .propose_to_endpoint(
                    &model,
                    &second.proposal.state,
                    &endpoint,
                    &second.context,
                    660.0,
                    &mut split_rng,
                )
                .unwrap()
                .state;
            assert_eq!(direct.status, split.status, "seed {seed}");
            assert_eq!(
                direct.powered_flight.event_counters, split.powered_flight.event_counters,
                "seed {seed}"
            );
            if direct.powered_flight.event_counters.total() > 0 {
                histories_with_events += 1;
            }
            let separation = great_circle_distance_nm(
                direct.powered_flight.aircraft.position,
                split.powered_flight.aircraft.position,
            )
            .0;
            maximum_endpoint_separation_nm = maximum_endpoint_separation_nm.max(separation);
            assert!(
                separation <= 1.0,
                "seed {seed} direct-vs-subdivided endpoint separation {separation} NM"
            );
            assert_eq!(
                direct_rng.gen::<u64>(),
                split_rng.gen::<u64>(),
                "seed {seed}"
            );
        }
        assert!(histories_with_events > 0);
        eprintln!(
            "maximum direct-vs-neutral-subdivision endpoint separation: {maximum_endpoint_separation_nm:.9} NM"
        );
    }

    #[test]
    fn stratified_filter_recovers_ordered_anchor_and_satcom_state() {
        let weather = constant_weather();
        let model = BroadFlightModel::new(
            config(),
            PoweredFlightEnvironment {
                weather: &weather,
                magnetic: None,
                magnetic_altitude_policy: MagneticAltitudePolicy::ClampToGridAltitude,
                time_origin_unix_s: 1_000.0,
            },
        )
        .unwrap();
        let observations = vec![
            BroadFlightObservation::FuelAnchor(BroadFuelAnchorObservation {
                id: "m1828a-fuel-anchor".to_string(),
                time: Seconds(0.9),
                zero_fuel_weight_kg: 174_369.0,
                total_onboard_fuel_kg: 33_524.104_881_96,
                reserved_fuel_kg: 15.0,
                unusable_fuel_kg: 0.0,
                left_usable_fraction: 0.5,
            }),
            BroadFlightObservation::Satcom(BroadSatcomObservation {
                flight: FlightObservation {
                    id: "synthetic-m0011".to_string(),
                    time_utc: "2014-03-09T00:11:00Z".to_string(),
                    satellite_afc_hz: 0.0,
                    measurement: SatcomObservation {
                        time: Seconds(60.0),
                        satellite_position_km: Vec3::new(18_161.0, 38_060.0, 1_029.0),
                        satellite_velocity_km_s: Vec3::new(0.002, -0.001, -0.046),
                        ground_station_position_km: Vec3::new(-2_368.8, 4_881.1, -3_342.0),
                        bto: Some(Microseconds(12_000.0)),
                        bto_sd: Some(Microseconds(1_000_000.0)),
                        bfo: Some(Hertz(170.0)),
                        bfo_sd: Some(Hertz(1_000_000.0)),
                    },
                },
                use_bto: true,
                use_bfo: true,
            }),
        ];
        let filter = FilterConfig {
            particles: 16,
            seed: 370_011,
            algorithm: Algorithm::Auxiliary,
            initial_time_s: 0.0,
            ess_resample_fraction: 0.5,
        };
        let plan = StratifiedFilterPlan {
            strata: vec![
                StratumAllocation {
                    id: StratumId(2),
                    particles: 8,
                    log_prior_probability: 0.5_f64.ln(),
                },
                StratumAllocation {
                    id: StratumId(1),
                    particles: 8,
                    log_prior_probability: 0.5_f64.ln(),
                },
            ],
        };
        let result = run_stratified_filter_with_snapshot_retention(
            &model,
            &observations,
            &filter,
            &plan,
            &SnapshotRetention::SelectedObservationIndices(vec![1]),
        )
        .unwrap();
        assert_eq!(result.snapshots.len(), 1);
        assert_eq!(result.snapshots[0].observation_index, Some(1));
        assert!(result.particles.iter().all(|state| {
            state.is_active()
                && state.diagnostics.fuel_anchor_count == 1
                && state.scores.bto_observations == 1
                && state.scores.bfo_observations == 1
                && (state.powered_flight.aircraft.time.0 - 60.0).abs() < TIME_TOLERANCE_S
                && (state.fuel.time.0 - 60.0).abs() < TIME_TOLERANCE_S
        }));
        assert_eq!(
            BroadRejectionCounts::from_states(&result.particles).active_particles,
            16
        );
        assert_eq!(result.checkpoints.len(), 2);
        assert_eq!(result.checkpoints[1].strata.len(), 2);
    }

    #[test]
    fn exact_dual_exhaustion_boundary_is_cadence_independent() {
        let weather = constant_weather();
        let mut reference = None;
        for cadence_s in [60.0, 30.0, 15.0] {
            let model = continuation_model(&weather, cadence_s);
            let (mut state, mut rng) = continuation_state(&model, StratumId(1), 1_237, 5.0, 5.0);
            state.powered_flight.event_clocks.lateral = None;
            state.powered_flight.event_clocks.speed = None;
            state.powered_flight.event_clocks.altitude = None;
            let result = model
                .continue_to_exact_dual_engine_exhaustion(&state, Seconds(120.0), &mut rng)
                .unwrap();
            assert_eq!(result.outcome, BroadDualEngineExhaustionOutcome::Exhausted);
            assert_eq!(result.exact_boundary_reintegrations, 1);
            let exhaustion_time = result.exhaustion_time.unwrap();
            assert!(exhaustion_time.0 > 0.0 && exhaustion_time.0 < 15.0);
            assert!(
                (result.state.powered_flight.aircraft.time.0 - exhaustion_time.0).abs()
                    <= TIME_TOLERANCE_S
            );
            assert!((result.state.fuel.time.0 - exhaustion_time.0).abs() <= TIME_TOLERANCE_S);
            assert_eq!(result.state.fuel.left_usable_feed, Kilograms(0.0));
            assert_eq!(result.state.fuel.right_usable_feed, Kilograms(0.0));
            assert_eq!(result.transition_diagnostics.powered_segments_screened, 1);
            if let Some(reference) = reference {
                assert_eq!(result, reference);
            } else {
                reference = Some(result);
            }
        }
    }

    #[test]
    fn exact_boundary_replay_restores_rng_and_splits_engine_events() {
        let weather = constant_weather();
        let mut model = continuation_model(&weather, 60.0);
        // This test exercises event splitting, not the conditional thrust
        // family: make the caller-declared one-engine proxy deliberately loose.
        model.config.powered_feasibility.thrust_multiplier = 10.0;
        model
            .config
            .powered_feasibility
            .static_thrust_cap_per_engine_n = 4_000_000.0;
        let (mut initial, initial_rng) = continuation_state(&model, StratumId(2), 8_819, 2.0, 5.0);
        initial.powered_flight.event_clocks.lateral = pending_at(10.0);
        initial.powered_flight.event_clocks.speed = None;
        initial.powered_flight.event_clocks.altitude = None;

        let mut first_rng = initial_rng.clone();
        let first = model
            .continue_to_exact_dual_engine_exhaustion(&initial, Seconds(120.0), &mut first_rng)
            .unwrap();
        let mut second_rng = initial_rng.clone();
        let second = model
            .continue_to_exact_dual_engine_exhaustion(&initial, Seconds(120.0), &mut second_rng)
            .unwrap();
        assert_eq!(first, second);
        assert_eq!(
            first_rng.clone().gen::<u64>(),
            second_rng.clone().gen::<u64>()
        );
        assert_eq!(first.outcome, BroadDualEngineExhaustionOutcome::Exhausted);
        assert_eq!(first.exact_boundary_reintegrations, 2);
        assert_eq!(first.transition_diagnostics.powered_segments_screened, 2);
        assert!(first.state.fuel.left_exhaustion_time.unwrap().0 < 10.0);
        assert!(first.state.fuel.dual_engine_exhaustion_time.unwrap().0 < 20.0);
        assert_eq!(
            first.boundary_events_at_end,
            PoweredEventCounters::default()
        );

        let exhaustion_time = first.exhaustion_time.unwrap();
        let mut expected_rng = initial_rng;
        let mut budget =
            PoweredEventBudget::new(model.config.integration.maximum_events_per_transition)
                .unwrap();
        let expected_segment = advance_powered_flight_step_with_budget(
            initial.powered_flight,
            exhaustion_time.0,
            model.config.limits,
            model.stratum(initial.stratum).unwrap().maneuver_process,
            model.config.integration,
            model.environment,
            initial.fuel.gross_mass().0,
            &mut budget,
            &mut expected_rng,
        )
        .unwrap()
        .unwrap();
        assert_eq!(
            expected_segment.events_at_end,
            PoweredEventCounters::default()
        );
        assert_eq!(first_rng.gen::<u64>(), expected_rng.gen::<u64>());
    }

    #[test]
    fn exact_continuation_reports_no_exhaustion_by_bound() {
        let weather = constant_weather();
        let model = continuation_model(&weather, 60.0);
        let (state, mut rng) = continuation_state(&model, StratumId(1), 501, 100.0, 100.0);
        let result = model
            .continue_to_exact_dual_engine_exhaustion(&state, Seconds(5.0), &mut rng)
            .unwrap();
        assert_eq!(
            result.outcome,
            BroadDualEngineExhaustionOutcome::NoExhaustionByBound
        );
        assert_eq!(result.state.powered_flight.aircraft.time, Seconds(5.0));
        assert_eq!(result.exhaustion_time, None);
        assert_eq!(result.exact_boundary_reintegrations, 0);
    }

    #[test]
    fn continuation_preclassifies_exhaustion_before_checkpoint() {
        let weather = constant_weather();
        let model = continuation_model(&weather, 30.0);
        let (mut state, mut rng) = continuation_state(&model, StratumId(1), 907, 5.0, 5.0);
        state.powered_flight.aircraft.time = Seconds(10.0);
        state.fuel.time = Seconds(10.0);
        state.fuel.left_usable_feed = Kilograms(0.0);
        state.fuel.right_usable_feed = Kilograms(0.0);
        state.fuel.left_exhaustion_time = Some(Seconds(5.0));
        state.fuel.right_exhaustion_time = Some(Seconds(5.0));
        state.fuel.dual_engine_exhaustion_time = Some(Seconds(5.0));
        let result = model
            .continue_to_exact_dual_engine_exhaustion(&state, Seconds(20.0), &mut rng)
            .unwrap();
        assert_eq!(
            result.outcome,
            BroadDualEngineExhaustionOutcome::AlreadyExhaustedBeforeStart
        );
        assert_eq!(result.exhaustion_time, Some(Seconds(5.0)));
        assert_eq!(result.state.powered_flight.aircraft.time, Seconds(10.0));
        assert_eq!(result.exact_boundary_reintegrations, 0);
    }

    #[test]
    fn stratum_override_initializes_within_each_log_flow_bin() {
        let weather = constant_weather();
        let mut broad_config = config();
        let template = broad_config.strata[0].clone();
        broad_config.strata = (0..5)
            .map(|index| BroadFlightStratum {
                id: StratumId(10 + index),
                name: format!("fuel-bin-{index}"),
                initial_lateral_mode: template.initial_lateral_mode,
                maneuver_process: template.maneuver_process,
            })
            .collect();
        let log_minimum = 0.9_f64.ln();
        let log_width = (1.1_f64.ln() - log_minimum) / 5.0;
        let overrides = broad_config
            .strata
            .iter()
            .enumerate()
            .map(|(index, stratum)| BroadStratumFuelUncertaintyOverride {
                stratum: stratum.id,
                fuel_uncertainty: BroadFuelUncertainty {
                    total_quantity_offset_kg: BroadUniformRange::fixed(0.0),
                    flow_scale_log_uniform: BroadUniformRange {
                        minimum: (log_minimum + index as f64 * log_width).exp(),
                        maximum: (log_minimum + (index + 1) as f64 * log_width).exp(),
                    },
                },
            })
            .collect::<Vec<_>>();
        let model = BroadFlightModel::new_with_stratum_fuel_uncertainty_overrides(
            broad_config,
            PoweredFlightEnvironment {
                weather: &weather,
                magnetic: None,
                magnetic_altitude_policy: MagneticAltitudePolicy::ClampToGridAltitude,
                time_origin_unix_s: 1_000.0,
            },
            overrides,
        )
        .unwrap();
        assert_eq!(model.stratum_fuel_uncertainty_overrides().len(), 5);
        for index in 0..5 {
            let stratum = StratumId(10 + index);
            let range = model
                .fuel_uncertainty_for_stratum(stratum)
                .unwrap()
                .flow_scale_log_uniform;
            let mut rng = ChaCha8Rng::seed_from_u64(71_000 + u64::from(index));
            for _ in 0..32 {
                let state = model.initialize_for_stratum(stratum, &mut rng).unwrap();
                assert!(state.fuel_flow_scale >= range.minimum);
                assert!(state.fuel_flow_scale <= range.maximum);
            }
        }

        let default_model = continuation_model(&weather, 30.0);
        assert_eq!(
            default_model
                .fuel_uncertainty_for_stratum(StratumId(1))
                .unwrap(),
            default_model.config.fuel_uncertainty
        );
        assert_eq!(
            default_model.fuel_flow_initialization_design(),
            BroadFuelFlowInitializationDesign::IndependentLogUniform
        );
    }

    #[test]
    fn log_space_latin_hypercube_has_exact_cell_cdf_and_log_mean() {
        let range = BroadUniformRange {
            minimum: 0.9,
            maximum: 1.1,
        };
        let stratum = StratumId(37);
        let particles = 101usize;
        let forward = (0..particles)
            .map(|within| {
                sample_log_space_latin_hypercube(range, stratum, within, particles).unwrap()
            })
            .collect::<Vec<_>>();
        let mut reverse = (0..particles)
            .rev()
            .map(|within| {
                (
                    within,
                    sample_log_space_latin_hypercube(range, stratum, within, particles).unwrap(),
                )
            })
            .collect::<Vec<_>>();
        reverse.sort_by_key(|(within, _)| *within);
        assert_eq!(
            forward,
            reverse
                .into_iter()
                .map(|(_, sample)| sample)
                .collect::<Vec<_>>()
        );

        let log_minimum = range.minimum.ln();
        let log_width = (range.maximum / range.minimum).ln();
        for (within, &sample) in forward.iter().enumerate() {
            assert!(sample > range.minimum && sample < range.maximum);
            let quantile = (sample.ln() - log_minimum) / log_width;
            assert!(quantile > within as f64 / particles as f64);
            assert!(quantile < (within + 1) as f64 / particles as f64);
        }
        for boundary in 1..particles {
            let boundary_value =
                (log_minimum + boundary as f64 / particles as f64 * log_width).exp();
            assert_eq!(
                forward
                    .iter()
                    .filter(|&&sample| sample < boundary_value)
                    .count(),
                boundary
            );
        }
        let empirical_log_mean =
            forward.iter().map(|sample| sample.ln()).sum::<f64>() / particles as f64;
        let exact_log_mean = 0.5 * (range.minimum.ln() + range.maximum.ln());
        assert!((empirical_log_mean - exact_log_mean).abs() < 2.0e-15);
    }

    #[test]
    fn latin_hypercube_model_uses_every_quantile_cell_once_without_weight_correction() {
        let weather = constant_weather();
        let model = BroadFlightModel::new_with_fuel_flow_initialization_design(
            config(),
            PoweredFlightEnvironment {
                weather: &weather,
                magnetic: None,
                magnetic_altitude_policy: MagneticAltitudePolicy::ClampToGridAltitude,
                time_origin_unix_s: 1_000.0,
            },
            BroadFuelFlowInitializationDesign::LogSpaceLatinHypercube,
        )
        .unwrap();
        let particles = 32usize;
        for within in 0..particles {
            let mut first_rng = ChaCha8Rng::seed_from_u64(90_000 + within as u64);
            let mut second_rng = ChaCha8Rng::seed_from_u64(90_000 + within as u64);
            let first = model
                .initialize_in_stratum(StratumId(1), within, within, particles, &mut first_rng)
                .unwrap();
            let second = model
                .initialize_in_stratum(StratumId(1), within, within, particles, &mut second_rng)
                .unwrap();
            assert_eq!(first.state, second.state);
            assert_eq!(first.log_prior_over_proposal, 0.0);
            let range = model.config.fuel_uncertainty.flow_scale_log_uniform;
            let quantile = (first.state.fuel_flow_scale.ln() - range.minimum.ln())
                / (range.maximum / range.minimum).ln();
            assert!(quantile > within as f64 / particles as f64);
            assert!(quantile < (within + 1) as f64 / particles as f64);
        }
        assert_eq!(
            model.fuel_flow_initialization_design(),
            BroadFuelFlowInitializationDesign::LogSpaceLatinHypercube
        );
    }

    #[test]
    fn powered_feasibility_requires_nonnegative_finite_drag_allowance() {
        let weather = constant_weather();
        for invalid in [-0.01, f64::NAN, f64::INFINITY] {
            let mut invalid_config = config();
            invalid_config
                .powered_feasibility
                .maximum_additional_drag_coefficient = invalid;
            assert!(matches!(
                BroadFlightModel::new(
                    invalid_config,
                    PoweredFlightEnvironment {
                        weather: &weather,
                        magnetic: None,
                        magnetic_altitude_policy: MagneticAltitudePolicy::ClampToGridAltitude,
                        time_origin_unix_s: 1_000.0,
                    },
                ),
                Err(BroadFlightError::InvalidConfiguration(_))
            ));
        }
    }

    #[test]
    fn multiple_try_correction_is_exact_and_keyed_rng_deterministic() {
        let log_likelihoods = [-2.0, -0.25, f64::NEG_INFINITY, -1.0];
        let mut first_rng = ChaCha8Rng::seed_from_u64(9_901);
        let mut second_rng = ChaCha8Rng::seed_from_u64(9_901);
        let first = select_multiple_try_candidate(&log_likelihoods, &mut first_rng).unwrap();
        let second = select_multiple_try_candidate(&log_likelihoods, &mut second_rng).unwrap();
        assert_eq!(first, second);
        assert_eq!(first_rng.gen::<u64>(), second_rng.gen::<u64>());

        let log_sum = log_likelihoods
            .iter()
            .filter(|value| value.is_finite())
            .map(|value| value.exp())
            .sum::<f64>()
            .ln();
        let expected_log_mean = log_sum - (log_likelihoods.len() as f64).ln();
        assert!((first.1 + log_likelihoods[first.0] - expected_log_mean).abs() < 1.0e-14);
        assert!(select_multiple_try_candidate(
            &[f64::NEG_INFINITY, f64::NEG_INFINITY],
            &mut first_rng
        )
        .is_none());
    }

    #[test]
    fn pending_renewal_refresh_is_exact_typed_and_kind_domain_separated() {
        let all = pending_refresh_config();
        all.validate().unwrap();
        assert_eq!(
            all.stable_descriptor(),
            "family=broad-pending-renewal-post-resample-refresh-v1;lateral=true;speed=true;altitude=true;law=exact-shape-one-pending-renewal-conditional;trigger=ordinary-posterior-resample-only;scientific-evidence=none"
        );
        assert!(BroadPendingRenewalRefreshConfig {
            lateral: false,
            speed: false,
            altitude: false,
        }
        .validate()
        .is_err());

        let weather = constant_weather();
        let model = pending_refresh_model(&weather, 1.0);
        let mut initialization_rng = ChaCha8Rng::seed_from_u64(370_051);
        let initial = model
            .initialize_for_stratum(StratumId(2), &mut initialization_rng)
            .unwrap();
        let context = pending_refresh_context(initial, 7);

        let mut all_state = initial;
        let mut all_rng = ChaCha8Rng::seed_from_u64(370_052);
        BroadPendingRenewalRefreshKernel::new(all)
            .unwrap()
            .apply(&model, &mut all_state, context, &mut all_rng)
            .unwrap();
        assert_eq!(
            all_state.diagnostics.pending_renewal_refresh,
            BroadPendingRenewalRefreshDiagnostics {
                total_refreshes: 3,
                lateral_refreshes: 1,
                speed_refreshes: 1,
                altitude_refreshes: 1,
            }
        );
        assert!(all_state.diagnostics.pending_renewal_refresh.validate());

        let mut lateral_only = initial;
        let mut lateral_rng = ChaCha8Rng::seed_from_u64(370_052);
        BroadPendingRenewalRefreshKernel::new(BroadPendingRenewalRefreshConfig {
            lateral: true,
            speed: false,
            altitude: false,
        })
        .unwrap()
        .apply(&model, &mut lateral_only, context, &mut lateral_rng)
        .unwrap();
        assert_eq!(
            lateral_only.powered_flight.event_clocks.lateral,
            all_state.powered_flight.event_clocks.lateral
        );
        assert_eq!(
            lateral_only.powered_flight.event_clocks.speed,
            initial.powered_flight.event_clocks.speed
        );
        assert_eq!(
            lateral_only.powered_flight.event_clocks.altitude,
            initial.powered_flight.event_clocks.altitude
        );

        let mut expected = initial;
        expected.powered_flight.event_clocks = all_state.powered_flight.event_clocks;
        expected.diagnostics.pending_renewal_refresh =
            all_state.diagnostics.pending_renewal_refresh;
        assert_eq!(all_state, expected);

        let mut inactive = initial;
        inactive.status = BroadFlightParticleStatus::Rejected {
            reason: BroadRejectionReason::StateOutsideDeclaredEnvelope,
            at_time: inactive.powered_flight.aircraft.time,
        };
        let inactive_before = inactive;
        let mut inactive_rng = ChaCha8Rng::seed_from_u64(370_053);
        let mut untouched_rng = inactive_rng.clone();
        BroadPendingRenewalRefreshKernel::new(all)
            .unwrap()
            .apply(
                &model,
                &mut inactive,
                pending_refresh_context(inactive_before, 8),
                &mut inactive_rng,
            )
            .unwrap();
        assert_eq!(inactive, inactive_before);
        assert_eq!(inactive_rng.gen::<u64>(), untouched_rng.gen::<u64>());
    }

    #[test]
    fn pending_renewal_refresh_fails_closed_for_due_and_nonunit_clocks() {
        let weather = constant_weather();
        let shape_one_model = pending_refresh_model(&weather, 1.0);
        let mut initialization_rng = ChaCha8Rng::seed_from_u64(370_054);
        let mut due = shape_one_model
            .initialize_for_stratum(StratumId(2), &mut initialization_rng)
            .unwrap();
        let current_time = due.powered_flight.aircraft.time;
        due.powered_flight.event_clocks.lateral = Some(PendingRenewal {
            not_before: current_time,
            next_event: current_time,
        });
        let due_before = due;
        let due_error = BroadPendingRenewalRefreshKernel::new(BroadPendingRenewalRefreshConfig {
            lateral: true,
            speed: false,
            altitude: false,
        })
        .unwrap()
        .apply(
            &shape_one_model,
            &mut due,
            pending_refresh_context(due_before, 0),
            &mut ChaCha8Rng::seed_from_u64(370_055),
        )
        .unwrap_err();
        assert!(matches!(
            due_error,
            BroadFlightError::PendingRenewalRefresh(PoweredRenewalRefreshError::ClockDue {
                kind: PoweredEventKind::Lateral
            })
        ));
        assert_eq!(due, due_before);

        let nonunit_model = pending_refresh_model(&weather, 1.5);
        let mut nonunit_rng = ChaCha8Rng::seed_from_u64(370_056);
        let mut nonunit = nonunit_model
            .initialize_for_stratum(StratumId(2), &mut nonunit_rng)
            .unwrap();
        let nonunit_before = nonunit;
        let nonunit_error =
            BroadPendingRenewalRefreshKernel::new(BroadPendingRenewalRefreshConfig {
                lateral: true,
                speed: false,
                altitude: false,
            })
            .unwrap()
            .apply(
                &nonunit_model,
                &mut nonunit,
                pending_refresh_context(nonunit_before, 0),
                &mut ChaCha8Rng::seed_from_u64(370_057),
            )
            .unwrap_err();
        assert!(matches!(
            nonunit_error,
            BroadFlightError::PendingRenewalRefresh(
                PoweredRenewalRefreshError::UnsupportedGammaShape {
                    kind: PoweredEventKind::Lateral
                }
            )
        ));
        assert_eq!(nonunit, nonunit_before);
    }

    #[test]
    fn no_resample_refresh_seam_preserves_legacy_filter_bytes() {
        let weather = constant_weather();
        let model = pending_refresh_model(&weather, 1.0);
        let observations = [
            BroadFlightObservation::Checkpoint {
                id: "before-m1839".to_string(),
                time: Seconds(0.0),
            },
            BroadFlightObservation::Checkpoint {
                id: "after-m1839".to_string(),
                time: Seconds(0.0),
            },
        ];
        let filter = FilterConfig {
            particles: 8,
            seed: 370_058,
            algorithm: Algorithm::Bootstrap,
            initial_time_s: 0.0,
            ess_resample_fraction: 0.5,
        };
        let plan = StratifiedFilterPlan {
            strata: vec![StratumAllocation {
                id: StratumId(2),
                particles: 8,
                log_prior_probability: 0.0,
            }],
        };
        let retention = SnapshotRetention::SelectedObservationIndices(vec![1]);
        let legacy = run_stratified_filter_with_snapshot_retention(
            &model,
            &observations,
            &filter,
            &plan,
            &retention,
        )
        .unwrap();
        let moved = run_stratified_bootstrap_filter_with_post_resample_move(
            &model,
            &BroadPendingRenewalRefreshKernel::new(pending_refresh_config()).unwrap(),
            &observations,
            &filter,
            &plan,
            &retention,
            WithinStratumResamplingPolicy::default(),
            &[
                StratifiedPostResampleMoveStep::Apply,
                StratifiedPostResampleMoveStep::Apply,
            ],
        )
        .unwrap();

        assert_eq!(
            serde_json::to_vec(&legacy).unwrap(),
            serde_json::to_vec(&moved.pooled).unwrap()
        );
        assert!(moved
            .post_resample_move_checkpoints
            .iter()
            .all(|checkpoint| !checkpoint.posterior_resampling_occurred
                && checkpoint.output_move_invocations == 0));
    }

    #[test]
    fn real_broad_filter_refreshes_only_m1839_resample_without_changing_target_state() {
        let weather = constant_weather();
        let model = pending_refresh_model(&weather, 1.0);
        let filter = FilterConfig {
            particles: 12,
            seed: 370_059,
            algorithm: Algorithm::Bootstrap,
            initial_time_s: 0.0,
            ess_resample_fraction: 0.9,
        };
        let plan = StratifiedFilterPlan {
            strata: vec![StratumAllocation {
                id: StratumId(2),
                particles: filter.particles,
                log_prior_probability: 0.0,
            }],
        };
        let target_slot = 3;
        let mut target_rng = rng_for(
            filter.seed,
            "stratified-initialize",
            0,
            target_slot,
            u64::from(StratumId(2).0),
        );
        let target = model
            .initialize_in_stratum(
                StratumId(2),
                target_slot,
                target_slot,
                filter.particles,
                &mut target_rng,
            )
            .unwrap()
            .state;
        let satellite_position = Vec3::new(18_161.0, 38_060.0, 1_029.0);
        let ground_station_position = Vec3::new(-2_368.8, 4_881.1, -3_342.0);
        let target_bto = bto(
            target.powered_flight.aircraft.position,
            target.powered_flight.aircraft.altitude.0,
            satellite_position,
            ground_station_position,
            model.config.satcom.bto,
        );
        let observations = [
            BroadFlightObservation::Checkpoint {
                id: "m1828-checkpoint".to_string(),
                time: Seconds(0.0),
            },
            BroadFlightObservation::Satcom(BroadSatcomObservation {
                flight: FlightObservation {
                    id: "m1839".to_string(),
                    time_utc: "2014-03-08T18:39:00Z".to_string(),
                    satellite_afc_hz: 0.0,
                    measurement: SatcomObservation {
                        time: Seconds(0.0),
                        satellite_position_km: satellite_position,
                        satellite_velocity_km_s: Vec3::new(0.002, -0.001, -0.046),
                        ground_station_position_km: ground_station_position,
                        bto: Some(target_bto),
                        bto_sd: Some(Microseconds(1.0e-6)),
                        bfo: None,
                        bfo_sd: None,
                    },
                },
                use_bto: true,
                use_bfo: false,
            }),
            BroadFlightObservation::Checkpoint {
                id: "post-m1839-refresh".to_string(),
                time: Seconds(0.0),
            },
        ];
        let retention = SnapshotRetention::SelectedObservationIndices(vec![2]);
        let legacy = run_stratified_filter_with_snapshot_retention(
            &model,
            &observations,
            &filter,
            &plan,
            &retention,
        )
        .unwrap();
        let moved = run_stratified_bootstrap_filter_with_post_resample_move(
            &model,
            &BroadPendingRenewalRefreshKernel::new(pending_refresh_config()).unwrap(),
            &observations,
            &filter,
            &plan,
            &retention,
            WithinStratumResamplingPolicy::default(),
            &[
                StratifiedPostResampleMoveStep::Inactive,
                StratifiedPostResampleMoveStep::Apply,
                StratifiedPostResampleMoveStep::Inactive,
            ],
        )
        .unwrap();

        assert_eq!(moved.pooled.log_weights, legacy.log_weights);
        assert_eq!(moved.pooled.log_evidence, legacy.log_evidence);
        assert_eq!(moved.pooled.root_ids, legacy.root_ids);
        assert_eq!(moved.pooled.ancestry, legacy.ancestry);
        assert_eq!(moved.pooled.checkpoints, legacy.checkpoints);
        assert_eq!(moved.pooled.snapshots.len(), 1);
        assert_eq!(legacy.snapshots.len(), 1);
        let move_checkpoints = &moved.post_resample_move_checkpoints;
        assert_eq!(move_checkpoints.len(), 3);
        assert!(!move_checkpoints[0].posterior_resampling_occurred);
        assert_eq!(move_checkpoints[0].output_move_invocations, 0);
        assert!(move_checkpoints[1].posterior_resampling_occurred);
        assert_eq!(
            move_checkpoints[1].output_move_invocations,
            filter.particles
        );
        assert!(!move_checkpoints[2].posterior_resampling_occurred);
        assert_eq!(move_checkpoints[2].output_move_invocations, 0);

        for (legacy_state, moved_state) in legacy.particles.iter().zip(&moved.pooled.particles) {
            for (legacy_pending, moved_pending) in [
                (
                    legacy_state.powered_flight.event_clocks.lateral,
                    moved_state.powered_flight.event_clocks.lateral,
                ),
                (
                    legacy_state.powered_flight.event_clocks.speed,
                    moved_state.powered_flight.event_clocks.speed,
                ),
                (
                    legacy_state.powered_flight.event_clocks.altitude,
                    moved_state.powered_flight.event_clocks.altitude,
                ),
            ] {
                assert_eq!(
                    legacy_pending.unwrap().not_before,
                    moved_pending.unwrap().not_before
                );
            }
            assert_eq!(
                moved_state.diagnostics.pending_renewal_refresh,
                BroadPendingRenewalRefreshDiagnostics {
                    total_refreshes: 3,
                    lateral_refreshes: 1,
                    speed_refreshes: 1,
                    altitude_refreshes: 1,
                }
            );
            let mut target_invariant = *moved_state;
            target_invariant.powered_flight.event_clocks = legacy_state.powered_flight.event_clocks;
            target_invariant.diagnostics.pending_renewal_refresh =
                legacy_state.diagnostics.pending_renewal_refresh;
            assert_eq!(&target_invariant, legacy_state);
        }

        let mut siblings_by_root = BTreeMap::<usize, Vec<usize>>::new();
        for (slot, root) in moved.pooled.root_ids.iter().copied().enumerate() {
            siblings_by_root.entry(root).or_default().push(slot);
        }
        let sibling_slots = siblings_by_root
            .values()
            .max_by_key(|slots| slots.len())
            .unwrap();
        assert!(sibling_slots.len() >= 2);
        for clock in [
            |state: &BroadFlightState| state.powered_flight.event_clocks.lateral.unwrap(),
            |state: &BroadFlightState| state.powered_flight.event_clocks.speed.unwrap(),
            |state: &BroadFlightState| state.powered_flight.event_clocks.altitude.unwrap(),
        ] {
            let next_events = sibling_slots
                .iter()
                .map(|&slot| clock(&moved.pooled.particles[slot]).next_event.0.to_bits())
                .collect::<BTreeSet<_>>();
            assert!(next_events.len() >= 2);
        }
    }

    #[test]
    fn event_mark_guide_configuration_is_exact_id_typed_and_requires_local_k1() {
        let epoch = event_mark_guide_epoch("m1941", 60.0, 900.0, 0.25);
        let guide = BroadSatcomEventMarkGuideConfig {
            epochs: vec![epoch.clone()],
        };
        guide.validate().unwrap();
        assert_eq!(guide.epoch("m1941"), Some(&epoch));
        assert!(guide.epoch("m2041").is_none());
        assert_eq!(
            guide.stable_descriptor(),
            "family=broad-satcom-lateral-event-mark-guide-v1;events=lateral-only;epochs=m1941:[60,900]s-k4-eps0.2-beta0.25;projection=frozen-selected-command-to-physical-endpoint-with-future-event-clocks-disabled;proposal=q_j=eps/K+(1-eps)*softmax(beta*enabled-BTO-plus-predictive-BFO-log-likelihood)_j;beta0-or-eps1=skip-projection-equal-valid-candidate-scores;role=proposal-only-exact-auxiliary-correction"
        );

        let duplicate = BroadSatcomEventMarkGuideConfig {
            epochs: vec![epoch.clone(), epoch.clone()],
        };
        assert!(duplicate.validate().is_err());
        let mut invalid = epoch.clone();
        invalid.minimum_lead = invalid.maximum_lookback;
        assert!(BroadSatcomEventMarkGuideConfig {
            epochs: vec![invalid]
        }
        .validate()
        .is_err());
        let mut invalid = epoch.clone();
        invalid.candidates_per_event = 1;
        assert!(BroadSatcomEventMarkGuideConfig {
            epochs: vec![invalid]
        }
        .validate()
        .is_err());

        let weather = constant_weather();
        let environment = PoweredFlightEnvironment {
            weather: &weather,
            magnetic: None,
            magnetic_altitude_policy: MagneticAltitudePolicy::ClampToGridAltitude,
            time_origin_unix_s: 1_000.0,
        };
        let mut nonlocal_k1 = config();
        nonlocal_k1.proposal_candidates = 2;
        assert!(BroadFlightModel::new_with_options(
            nonlocal_k1,
            environment,
            BroadFlightModelOptions {
                satcom_event_mark_guide: Some(guide.clone()),
                ..BroadFlightModelOptions::default()
            }
        )
        .is_err());
        assert!(BroadFlightModel::new_with_options(
            config(),
            environment,
            BroadFlightModelOptions {
                proposal_candidate_schedule:
                    BroadProposalCandidateSchedule::ObservationIntervalTiers {
                        tiers: vec![BroadProposalCandidateTier {
                            minimum_elapsed_seconds: 600.0,
                            proposal_candidates: 1,
                        }],
                    },
                satcom_event_mark_guide: Some(guide),
                ..BroadFlightModelOptions::default()
            }
        )
        .is_err());
    }

    #[test]
    fn event_mark_guide_uses_inclusive_lead_bounds_and_only_lateral_events() {
        let weather = constant_weather();
        let model = event_mark_guide_model(
            &weather,
            vec![event_mark_guide_epoch("guided", 60.0, 900.0, 0.0)],
        );
        let observation = satcom_observation_with_id("guided", 1_000.0);
        for (event_time, expected_guided) in [
            (100.0, 1),
            (940.0, 1),
            (99.999, 0),
            (940.001, 0),
            (1_000.0, 0),
        ] {
            let state = event_mark_state(&model, event_time);
            let mut rng = ChaCha8Rng::seed_from_u64(event_time.to_bits());
            let proposal = model
                .propose(&state, &observation, 1_000.0, &mut rng)
                .unwrap();
            assert_eq!(
                proposal
                    .state
                    .diagnostics
                    .satcom_event_mark_guide
                    .guided_lateral_events,
                expected_guided
            );
        }

        let mut nonlateral = event_mark_state(&model, 100.0);
        nonlateral.powered_flight.event_clocks = PoweredEventClocks {
            lateral: None,
            speed: pending_at(100.0),
            altitude: pending_at(100.0),
        };
        let proposal = model
            .propose(
                &nonlateral,
                &observation,
                1_000.0,
                &mut ChaCha8Rng::seed_from_u64(91),
            )
            .unwrap();
        assert_eq!(
            proposal.state.diagnostics.satcom_event_mark_guide,
            BroadSatcomEventMarkGuideDiagnostics::default()
        );
        assert_eq!(proposal.state.powered_flight.event_counters.speed, 1);
        assert_eq!(proposal.state.powered_flight.event_counters.altitude, 1);
    }

    #[test]
    fn epsilon_one_event_mark_proposal_is_uniform_and_skips_every_proxy() {
        let weather = constant_weather();
        let mut epoch = event_mark_guide_epoch("guided", 60.0, 900.0, 0.25);
        epoch.defensive_prior_probability = 1.0;
        let mut model = event_mark_guide_model(&weather, vec![epoch]);
        model.config.strata[1].maneuver_process.lateral_mode_weights = PoweredLateralModeWeights {
            constant_true_heading: 0.0,
            constant_magnetic_heading: 0.0,
            constant_true_track: 1.0,
            constant_magnetic_track: 0.0,
            great_circle_track_continuation: 0.0,
        };
        let state = event_mark_state(&model, 100.0);
        let observation = satcom_observation_with_id("guided", 1_000.0);
        let proposal = model
            .propose(
                &state,
                &observation,
                1_000.0,
                &mut ChaCha8Rng::seed_from_u64(370_048),
            )
            .unwrap();
        let diagnostics = proposal.state.diagnostics.satcom_event_mark_guide;
        assert_eq!(proposal.log_prior_over_proposal, 0.0);
        assert_eq!(diagnostics.cumulative_log_prior_over_proposal, 0.0);
        assert_eq!(diagnostics.guided_lateral_events, 1);
        assert_eq!(diagnostics.candidate_marks, 4);
        assert_eq!(diagnostics.finite_candidate_scores, 4);
        assert_eq!(diagnostics.proxy_projection_successes, 0);
        assert_eq!(diagnostics.proxy_projection_failures, 0);
        assert_eq!(diagnostics.proxy_projection_skipped_candidates, 4);
        assert_eq!(diagnostics.materialization_failures, 0);
        assert_eq!(proposal.state.scores, state.scores);
        assert_eq!(proposal.state.bfo_bias, state.bfo_bias);
    }

    #[test]
    fn event_mark_guide_is_pure_corrected_and_observation_is_assimilated_once() {
        let weather = constant_weather();
        let model = event_mark_guide_model(
            &weather,
            vec![
                event_mark_guide_epoch("guided-one", 60.0, 900.0, 0.25),
                event_mark_guide_epoch("guided-two", 60.0, 900.0, 0.25),
            ],
        );
        let observation = satcom_observation_with_id("guided-one", 1_000.0);
        let state = event_mark_state(&model, 100.0);
        let original = state;
        let first = model
            .propose(
                &state,
                &observation,
                1_000.0,
                &mut ChaCha8Rng::seed_from_u64(370_041),
            )
            .unwrap();
        assert_eq!(state, original);
        assert_eq!(first.state.scores, original.scores);
        assert_eq!(first.state.bfo_bias, original.bfo_bias);
        assert_eq!(first.state.last_fit, original.last_fit);
        let diagnostics = first.state.diagnostics.satcom_event_mark_guide;
        assert_eq!(diagnostics.eligible_lateral_events, 1);
        assert_eq!(diagnostics.guided_lateral_events, 1);
        assert_eq!(diagnostics.candidate_marks, 4);
        assert_eq!(
            diagnostics.proxy_projection_successes
                + diagnostics.proxy_projection_failures
                + diagnostics.proxy_projection_skipped_candidates
                + diagnostics.materialization_failures,
            diagnostics.candidate_marks
        );
        assert!(
            (first.log_prior_over_proposal - diagnostics.cumulative_log_prior_over_proposal).abs()
                < 1.0e-14
        );
        assert!(
            (diagnostics.cumulative_log_prior_over_proposal
                + diagnostics.sum_log_candidate_count
                + diagnostics.sum_selected_log_probability)
                .abs()
                < 1.0e-14
        );
        assert!(
            diagnostics.cumulative_log_prior_over_proposal
                >= diagnostics.sum_minimum_log_prior_over_proposal - 1.0e-14
        );
        assert!(
            diagnostics.cumulative_log_prior_over_proposal
                <= diagnostics.sum_maximum_log_prior_over_proposal + 1.0e-14
        );

        let mut assimilated = first.state;
        let likelihood = model.observe(&mut assimilated, &observation).unwrap();
        assert!(likelihood.is_finite());
        assert_eq!(assimilated.scores.bto_observations, 1);
        assert_eq!(assimilated.scores.bfo_observations, 1);
        assert!(assimilated.last_fit.is_some());
        let cumulative_before_second = assimilated
            .diagnostics
            .satcom_event_mark_guide
            .cumulative_log_prior_over_proposal;

        assimilated.powered_flight.event_clocks.lateral = pending_at(1_200.0);
        let second_observation = satcom_observation_with_id("guided-two", 2_000.0);
        let second = model
            .propose(
                &assimilated,
                &second_observation,
                1_000.0,
                &mut ChaCha8Rng::seed_from_u64(370_042),
            )
            .unwrap();
        let cumulative_after_second = second
            .state
            .diagnostics
            .satcom_event_mark_guide
            .cumulative_log_prior_over_proposal;
        assert!(
            (second.log_prior_over_proposal - (cumulative_after_second - cumulative_before_second))
                .abs()
                < 1.0e-13
        );
        assert_eq!(second.state.scores, assimilated.scores);
        assert_eq!(second.state.bfo_bias, assimilated.bfo_bias);
    }

    #[test]
    fn frozen_command_proxy_is_candidate_sensitive_clock_independent_and_uses_carried_bfo_state() {
        use mh370_dynamics::PoweredEventMark;

        let weather = constant_weather();
        let model = event_mark_guide_model(
            &weather,
            vec![event_mark_guide_epoch("guided", 60.0, 900.0, 0.25)],
        );
        let mut observation = satcom_observation_with_id("guided", 600.0);
        let BroadFlightObservation::Satcom(satcom) = &mut observation else {
            unreachable!()
        };
        satcom.flight.measurement.bto_sd = Some(Microseconds(29.0));
        satcom.flight.measurement.bfo_sd = Some(Hertz(7.0));
        satcom.flight.satellite_afc_hz = -18.5;
        let state = event_mark_state(&model, 0.0);
        let before = state.powered_flight;
        let event = PoweredEventProposalEvent {
            kind: PoweredEventKind::Lateral,
            event_number: 1,
            before,
        };
        let mut east = before;
        east.command.lateral_mode = PoweredLateralMode::ConstantTrueTrack;
        east.command.selected_control = Degrees(90.0);
        east.command.great_circle_destination = None;
        east.event_clocks.lateral = pending_at(10.0);
        let mut south = east;
        south.command.selected_control = Degrees(180.0);
        south.event_clocks.lateral = pending_at(20.0);
        let scorer = BroadSatcomEventMarkScorer {
            model: &model,
            observation: satcom,
            epoch: model
                .satcom_event_mark_guide()
                .unwrap()
                .epoch("guided")
                .unwrap(),
            process: model.stratum(StratumId(2)).unwrap().maneuver_process,
            gross_mass_kg: state.fuel.gross_mass().0,
            bfo_bias: state.bfo_bias,
            proxy_counts_by_event: Mutex::new(BTreeMap::new()),
        };
        let candidate = |candidate_index, after_mark| PoweredEventProposalCandidate {
            event,
            candidate_index,
            mark: PoweredEventMark::Lateral {
                mode: PoweredLateralMode::ConstantTrueTrack,
                course_change_deg: 0.0,
            },
            after_mark,
        };
        let east_before = east;
        let east_score = scorer.log_score(&candidate(0, east)).unwrap();
        let south_score = scorer.log_score(&candidate(1, south)).unwrap();
        assert_ne!(east_score, south_score);
        let mut east_other_clock = east;
        east_other_clock.event_clocks.lateral = pending_at(599.0);
        assert_eq!(
            east_score,
            scorer.log_score(&candidate(2, east_other_clock)).unwrap()
        );
        assert_eq!(east, east_before);
        let mut outside_proxy_domain = east;
        outside_proxy_domain.aircraft.position = LatLon::new(30.0, 99.0).unwrap();
        assert_eq!(
            scorer
                .log_score(&candidate(3, outside_proxy_domain))
                .unwrap(),
            f64::NEG_INFINITY
        );
        assert_eq!(scorer.proxy_counts(), (3, 1, 0));

        let mut invalid_model = event_mark_guide_model(
            &weather,
            vec![event_mark_guide_epoch("guided", 60.0, 900.0, 0.25)],
        );
        invalid_model.config.integration.steady_step_s = 0.0;
        let invalid_scorer = BroadSatcomEventMarkScorer {
            model: &invalid_model,
            observation: satcom,
            epoch: invalid_model
                .satcom_event_mark_guide()
                .unwrap()
                .epoch("guided")
                .unwrap(),
            process: invalid_model
                .stratum(StratumId(2))
                .unwrap()
                .maneuver_process,
            gross_mass_kg: state.fuel.gross_mass().0,
            bfo_bias: state.bfo_bias,
            proxy_counts_by_event: Mutex::new(BTreeMap::new()),
        };
        let nonroutine_error = invalid_scorer.log_score(&candidate(5, east)).unwrap_err();
        assert!(
            matches!(
                nonroutine_error,
                BroadSatcomEventMarkScorerError::Projection(PoweredFlightError::InvalidIntegration)
            ),
            "{nonroutine_error:?}"
        );
        assert_eq!(invalid_scorer.proxy_counts(), (0, 0, 0));

        let mut neutral_epoch = scorer.epoch.clone();
        neutral_epoch.score_temperature = 0.0;
        let neutral_scorer = BroadSatcomEventMarkScorer {
            model: &model,
            observation: satcom,
            epoch: &neutral_epoch,
            process: model.stratum(StratumId(2)).unwrap().maneuver_process,
            gross_mass_kg: state.fuel.gross_mass().0,
            bfo_bias: state.bfo_bias,
            proxy_counts_by_event: Mutex::new(BTreeMap::new()),
        };
        assert_eq!(
            neutral_scorer
                .log_score(&candidate(4, outside_proxy_domain))
                .unwrap(),
            0.0
        );
        let mut next_event_candidate = candidate(5, east);
        next_event_candidate.event.event_number = 2;
        assert_eq!(
            neutral_scorer.log_score(&next_event_candidate).unwrap(),
            0.0
        );
        assert_eq!(neutral_scorer.proxy_counts(), (0, 0, 2));
        assert_eq!(
            neutral_scorer
                .proxy_counts_for_event(PoweredEventKind::Lateral, 2)
                .tuple(),
            (0, 0, 1)
        );

        let proxy = model
            .frozen_command_satcom_proxy(
                south,
                model.stratum(StratumId(2)).unwrap().maneuver_process,
                state.fuel.gross_mass().0,
                satcom.flight.measurement.time,
            )
            .unwrap();
        let mut carried_bias = state.bfo_bias;
        carried_bias.mean_hz += 3.0;
        carried_bias.variance_hz2 = 123.0;
        let helper_score = model
            .satcom_proxy_log_likelihood(proxy, carried_bias, satcom)
            .unwrap();
        let mut independent_bias = carried_bias;
        let independent = evaluate_observation(
            proxy,
            &mut independent_bias,
            &satcom.flight.measurement,
            satcom.flight.satellite_afc_hz,
            true,
            &model.config.satcom,
        )
        .unwrap();
        assert_eq!(helper_score, independent.log_likelihood);
        assert_ne!(independent_bias, carried_bias);
        let mut changed_afc = satcom.clone();
        changed_afc.flight.satellite_afc_hz += 10.0;
        assert_ne!(
            helper_score,
            model
                .satcom_proxy_log_likelihood(proxy, carried_bias, &changed_afc)
                .unwrap()
        );

        let mut bto_only = satcom.clone();
        bto_only.use_bfo = false;
        let bto_only_score = model
            .satcom_proxy_log_likelihood(proxy, carried_bias, &bto_only)
            .unwrap();
        let mut changed_disabled_bfo = bto_only;
        changed_disabled_bfo.flight.measurement.bfo = Some(Hertz(-9_000.0));
        changed_disabled_bfo.flight.measurement.bfo_sd = Some(Hertz(0.5));
        changed_disabled_bfo.flight.satellite_afc_hz += 1_000.0;
        let changed_disabled_bias = BfoBiasState {
            mean_hz: carried_bias.mean_hz + 2_000.0,
            variance_hz2: carried_bias.variance_hz2 + 3_000.0,
        };
        assert_eq!(
            bto_only_score,
            model
                .satcom_proxy_log_likelihood(proxy, changed_disabled_bias, &changed_disabled_bfo,)
                .unwrap()
        );

        let mut bfo_only = satcom.clone();
        bfo_only.use_bto = false;
        let bfo_only_score = model
            .satcom_proxy_log_likelihood(proxy, carried_bias, &bfo_only)
            .unwrap();
        let mut changed_disabled_bto = bfo_only;
        changed_disabled_bto.flight.measurement.bto = Some(Microseconds(-9_000.0));
        changed_disabled_bto.flight.measurement.bto_sd = Some(Microseconds(0.5));
        assert_eq!(
            bfo_only_score,
            model
                .satcom_proxy_log_likelihood(proxy, carried_bias, &changed_disabled_bto)
                .unwrap()
        );
    }

    #[test]
    fn selected_unmaterializable_mark_retains_proposal_diagnostic_before_rejection() {
        let weather = constant_weather();
        let mut model = event_mark_guide_model(
            &weather,
            vec![event_mark_guide_epoch("guided", 60.0, 900.0, 0.25)],
        );
        model.config.strata[1].maneuver_process.lateral_mode_weights = PoweredLateralModeWeights {
            constant_true_heading: 0.0,
            constant_magnetic_heading: 1.0,
            constant_true_track: 0.0,
            constant_magnetic_track: 0.0,
            great_circle_track_continuation: 0.0,
        };
        let state = event_mark_state(&model, 100.0);
        let observation = satcom_observation_with_id("guided", 1_000.0);
        let proposal = model
            .propose(
                &state,
                &observation,
                1_000.0,
                &mut ChaCha8Rng::seed_from_u64(370_043),
            )
            .unwrap();
        assert!(matches!(
            proposal.state.status,
            BroadFlightParticleStatus::Rejected {
                reason: BroadRejectionReason::MagneticEnvironmentUnavailable,
                ..
            }
        ));
        let diagnostics = proposal.state.diagnostics.satcom_event_mark_guide;
        assert_eq!(diagnostics.guided_lateral_events, 1);
        assert_eq!(diagnostics.candidate_marks, 4);
        assert_eq!(diagnostics.materialization_failures, 4);
        assert_eq!(diagnostics.proxy_projection_successes, 0);
        assert_eq!(diagnostics.proxy_projection_failures, 0);
        assert_eq!(diagnostics.proxy_projection_skipped_candidates, 0);
        assert_eq!(diagnostics.all_scores_negative_infinity_events, 1);
        assert_eq!(proposal.log_prior_over_proposal, 0.0);
        assert_eq!(diagnostics.cumulative_log_prior_over_proposal, 0.0);
        let mut rejected = proposal.state;
        assert_eq!(
            model.observe(&mut rejected, &observation).unwrap(),
            f64::NEG_INFINITY
        );
        assert_eq!(rejected.scores, BroadFlightScores::default());
    }

    #[test]
    fn post_proposal_dynamics_rejection_discards_orphan_proxy_counts() {
        let weather = constant_weather();
        let mut model = event_mark_guide_model(
            &weather,
            vec![event_mark_guide_epoch("guided", 60.0, 900.0, 0.25)],
        );
        model.config.strata[1].maneuver_process.lateral_mode_weights = PoweredLateralModeWeights {
            constant_true_heading: 0.0,
            constant_magnetic_heading: 0.0,
            constant_true_track: 1.0,
            constant_magnetic_track: 0.0,
            great_circle_track_continuation: 0.0,
        };
        let mut state = event_mark_state(&model, 0.0);
        state.powered_flight.aircraft.position = LatLon::new(30.0, 99.0).unwrap();
        let observation = satcom_observation_with_id("guided", 900.0);
        let proposal = model
            .propose(
                &state,
                &observation,
                900.0,
                &mut ChaCha8Rng::seed_from_u64(370_047),
            )
            .unwrap();
        assert!(matches!(
            proposal.state.status,
            BroadFlightParticleStatus::Rejected {
                reason: BroadRejectionReason::EnvironmentOutsideDomain,
                at_time: Seconds(0.0),
            }
        ));
        assert_eq!(proposal.log_prior_over_proposal, 0.0);
        assert_eq!(
            proposal.state.diagnostics.satcom_event_mark_guide,
            BroadSatcomEventMarkGuideDiagnostics::default()
        );
    }

    #[test]
    fn selected_end_event_commits_only_its_keyed_proxy_counts() {
        let weather = constant_weather();
        let mut epoch = event_mark_guide_epoch("guided", 60.0, 900.0, 0.25);
        epoch.defensive_prior_probability = 1.0;
        let mut model = event_mark_guide_model(&weather, vec![epoch]);
        {
            let process = &mut model.config.strata[1].maneuver_process;
            process.lateral_clock = Some(RenewalClock {
                mean_interval_s: 0.002,
                minimum_interval_s: 0.001,
                gamma_shape: 1.0,
            });
            process.lateral_mode_weights = PoweredLateralModeWeights {
                constant_true_heading: 0.0,
                constant_magnetic_heading: 0.5,
                constant_true_track: 0.5,
                constant_magnetic_track: 0.0,
                great_circle_track_continuation: 0.0,
            };
        }
        let process = model.config.strata[1].maneuver_process;
        let state = event_mark_state(&model, 0.0);
        let observation = satcom_observation_with_id("guided", 900.0);
        let BroadFlightObservation::Satcom(satcom) = &observation else {
            unreachable!()
        };
        let epoch = model
            .satcom_event_mark_guide()
            .unwrap()
            .epoch("guided")
            .unwrap();
        let seed = (0_u64..256)
            .find(|seed| {
                let mut rng = ChaCha8Rng::seed_from_u64(*seed);
                let proposal_rng = PoweredEventProposalRng::from_rng(&mut rng);
                let mut event_budget =
                    PoweredEventBudget::new(model.config.integration.maximum_events_per_transition)
                        .unwrap();
                let scorer = BroadSatcomEventMarkScorer {
                    model: &model,
                    observation: satcom,
                    epoch,
                    process,
                    gross_mass_kg: state.fuel.gross_mass().0,
                    bfo_bias: state.bfo_bias,
                    proxy_counts_by_event: Mutex::new(BTreeMap::new()),
                };
                matches!(
                    advance_powered_flight_step_with_budget_and_event_proposal(
                        state.powered_flight,
                        satcom.flight.measurement.time.0,
                        model.config.limits,
                        process,
                        model.config.integration,
                        model.environment,
                        state.fuel.gross_mass().0,
                        &mut event_budget,
                        epoch.dynamics_config(),
                        &mut rng,
                        &proposal_rng,
                        &scorer,
                    ),
                    Err(PoweredEventProposalError::SelectedCandidate {
                        diagnostic,
                        source: PoweredFlightError::MissingMagneticEnvironment,
                    }) if diagnostic.event_number == 2
                )
            })
            .expect("fixture should expose a selected-invalid second lateral event");
        let proposal = model
            .propose(
                &state,
                &observation,
                900.0,
                &mut ChaCha8Rng::seed_from_u64(seed),
            )
            .unwrap();
        assert!(matches!(
            proposal.state.status,
            BroadFlightParticleStatus::Rejected {
                reason: BroadRejectionReason::MagneticEnvironmentUnavailable,
                ..
            }
        ));
        let diagnostics = proposal.state.diagnostics.satcom_event_mark_guide;
        assert_eq!(proposal.log_prior_over_proposal, 0.0);
        assert_eq!(diagnostics.guided_lateral_events, 1);
        assert_eq!(diagnostics.candidate_marks, 4);
        assert_eq!(diagnostics.proxy_projection_successes, 0);
        assert_eq!(diagnostics.proxy_projection_failures, 0);
        assert_eq!(
            diagnostics.proxy_projection_skipped_candidates + diagnostics.materialization_failures,
            diagnostics.candidate_marks
        );
    }

    #[test]
    fn unmatched_event_mark_schedule_preserves_legacy_proposal_bytes_and_rng_tail() {
        let weather = constant_weather();
        let environment = PoweredFlightEnvironment {
            weather: &weather,
            magnetic: None,
            magnetic_altitude_policy: MagneticAltitudePolicy::ClampToGridAltitude,
            time_origin_unix_s: 1_000.0,
        };
        let legacy = BroadFlightModel::new(config(), environment).unwrap();
        let scheduled = BroadFlightModel::new_with_options(
            config(),
            environment,
            BroadFlightModelOptions {
                satcom_event_mark_guide: Some(BroadSatcomEventMarkGuideConfig {
                    epochs: vec![event_mark_guide_epoch("other", 60.0, 900.0, 0.25)],
                }),
                ..BroadFlightModelOptions::default()
            },
        )
        .unwrap();
        let mut first_init_rng = ChaCha8Rng::seed_from_u64(370_044);
        let mut second_init_rng = ChaCha8Rng::seed_from_u64(370_044);
        let first_state = legacy
            .initialize_for_stratum(StratumId(2), &mut first_init_rng)
            .unwrap();
        let second_state = scheduled
            .initialize_for_stratum(StratumId(2), &mut second_init_rng)
            .unwrap();
        assert_eq!(first_state, second_state);
        let observation = satcom_observation_with_id("actual", 1_000.0);
        let mut first_rng = ChaCha8Rng::seed_from_u64(370_045);
        let mut second_rng = ChaCha8Rng::seed_from_u64(370_045);
        let first = legacy
            .propose(&first_state, &observation, 1_000.0, &mut first_rng)
            .unwrap();
        let second = scheduled
            .propose(&second_state, &observation, 1_000.0, &mut second_rng)
            .unwrap();
        assert_eq!(
            serde_json::to_vec(&(first.state, first.log_prior_over_proposal)).unwrap(),
            serde_json::to_vec(&(second.state, second.log_prior_over_proposal)).unwrap()
        );
        assert_eq!(first_rng.gen::<u64>(), second_rng.gen::<u64>());
    }

    #[test]
    fn event_mark_proposal_composes_with_root_stratified_transition_pool() {
        let weather = constant_weather();
        let mut model = event_mark_guide_model(
            &weather,
            vec![event_mark_guide_epoch("guided", 60.0, 900.0, 0.25)],
        );
        model.config.strata[1].maneuver_process.lateral_clock = Some(RenewalClock {
            mean_interval_s: 180.0,
            minimum_interval_s: 60.0,
            gamma_shape: 1.0,
        });
        let observations = [satcom_observation_with_id("guided", 1_000.0)];
        let result = run_stratified_filter_with_root_stratified_transition_pool(
            &model,
            &observations,
            &FilterConfig {
                particles: 8,
                seed: 370_046,
                algorithm: Algorithm::Bootstrap,
                initial_time_s: 0.0,
                ess_resample_fraction: 0.5,
            },
            &StratifiedFilterPlan {
                strata: vec![StratumAllocation {
                    id: StratumId(2),
                    particles: 8,
                    log_prior_probability: 0.0,
                }],
            },
            &SnapshotRetention::All,
            WithinStratumResamplingPolicy {
                uniform_root_mixture_epsilon: 0.2,
            },
            &[RootStratifiedTransitionPoolStep::Pool {
                candidates_per_positive_root: 2,
            }],
        )
        .unwrap();
        assert!(result.pooled.log_evidence.is_finite());
        assert_eq!(result.root_stratified_candidate_pool_checkpoints.len(), 1);
        assert!(result.pooled.particles.iter().all(|state| {
            state.scores.bto_observations == 1 && state.scores.bfo_observations == 1
        }));
        assert!(result.pooled.particles.iter().any(|state| {
            state
                .diagnostics
                .satcom_event_mark_guide
                .guided_lateral_events
                > 0
        }));
    }

    #[test]
    fn proposal_candidate_schedule_has_exact_deterministic_boundaries() {
        let schedule = BroadProposalCandidateSchedule::ObservationIntervalTiers {
            tiers: vec![
                BroadProposalCandidateTier {
                    minimum_elapsed_seconds: 600.0,
                    proposal_candidates: 4,
                },
                BroadProposalCandidateTier {
                    minimum_elapsed_seconds: 1_800.0,
                    proposal_candidates: 8,
                },
            ],
        };
        assert_eq!(schedule.candidates_for_elapsed_seconds(1, 599.999), 1);
        assert_eq!(schedule.candidates_for_elapsed_seconds(1, 600.0), 4);
        assert_eq!(schedule.candidates_for_elapsed_seconds(1, 1_799.999), 4);
        assert_eq!(schedule.candidates_for_elapsed_seconds(1, 1_800.0), 8);
        assert_eq!(schedule.candidates_for_elapsed_seconds(1, 3_600.0), 8);
        assert_eq!(
            schedule.stable_descriptor(1),
            "proposal=elapsed-tiered-v1;base-k1;ge600s-k4,ge1800s-k8"
        );

        let invalid = BroadProposalCandidateSchedule::ObservationIntervalTiers {
            tiers: vec![
                BroadProposalCandidateTier {
                    minimum_elapsed_seconds: 600.0,
                    proposal_candidates: 4,
                },
                BroadProposalCandidateTier {
                    minimum_elapsed_seconds: 600.0,
                    proposal_candidates: 8,
                },
            ],
        };
        assert!(matches!(
            invalid.validate_with_baseline_candidates(1),
            Err(BroadFlightError::InvalidConfiguration(_))
        ));
    }

    #[test]
    fn tiered_short_interval_k1_is_byte_compatible_with_legacy_k1() {
        let weather = constant_weather();
        let environment = PoweredFlightEnvironment {
            weather: &weather,
            magnetic: None,
            magnetic_altitude_policy: MagneticAltitudePolicy::ClampToGridAltitude,
            time_origin_unix_s: 1_000.0,
        };
        let legacy = BroadFlightModel::new(config(), environment).unwrap();
        let tiered = BroadFlightModel::new_with_options(
            config(),
            environment,
            BroadFlightModelOptions {
                proposal_candidate_schedule:
                    BroadProposalCandidateSchedule::ObservationIntervalTiers {
                        tiers: vec![BroadProposalCandidateTier {
                            minimum_elapsed_seconds: 600.0,
                            proposal_candidates: 8,
                        }],
                    },
                ..BroadFlightModelOptions::default()
            },
        )
        .unwrap();
        let mut legacy_initial_rng = ChaCha8Rng::seed_from_u64(44_011);
        let mut tiered_initial_rng = ChaCha8Rng::seed_from_u64(44_011);
        let legacy_state = legacy
            .initialize_for_stratum(StratumId(1), &mut legacy_initial_rng)
            .unwrap();
        let tiered_state = tiered
            .initialize_for_stratum(StratumId(1), &mut tiered_initial_rng)
            .unwrap();
        assert_eq!(legacy_state, tiered_state);
        assert_eq!(
            legacy_initial_rng.gen::<u64>(),
            tiered_initial_rng.gen::<u64>()
        );

        let observation = loose_satcom_observation(60.0);
        let mut legacy_rng = ChaCha8Rng::seed_from_u64(88_019);
        let mut tiered_rng = ChaCha8Rng::seed_from_u64(88_019);
        let legacy_proposal = legacy
            .propose(&legacy_state, &observation, 60.0, &mut legacy_rng)
            .unwrap();
        let tiered_proposal = tiered
            .propose(&tiered_state, &observation, 60.0, &mut tiered_rng)
            .unwrap();
        let legacy_bytes = serde_json::to_vec(&(
            legacy_proposal.state,
            legacy_proposal.log_prior_over_proposal,
        ))
        .unwrap();
        let tiered_bytes = serde_json::to_vec(&(
            tiered_proposal.state,
            tiered_proposal.log_prior_over_proposal,
        ))
        .unwrap();
        assert_eq!(legacy_bytes, tiered_bytes);
        assert_eq!(legacy_rng.gen::<u64>(), tiered_rng.gen::<u64>());
    }

    #[test]
    fn zero_likelihood_operations_do_not_revive_rejected_particles() {
        let weather = constant_weather();
        let model = continuation_model(&weather, 30.0);
        let (mut rejected, _) = continuation_state(&model, StratumId(1), 4_119, 100.0, 100.0);
        rejected.status = BroadFlightParticleStatus::Rejected {
            reason: BroadRejectionReason::PoweredSegmentInfeasible,
            at_time: Seconds(0.0),
        };
        let original = rejected;
        let anchor = BroadFlightObservation::FuelAnchor(BroadFuelAnchorObservation {
            id: "synthetic-anchor".to_string(),
            time: Seconds(0.0),
            zero_fuel_weight_kg: 174_369.0,
            total_onboard_fuel_kg: 100.0,
            reserved_fuel_kg: 0.0,
            unusable_fuel_kg: 0.0,
            left_usable_fraction: 0.5,
        });
        assert_eq!(
            model.observe_state(&mut rejected, &anchor).unwrap(),
            f64::NEG_INFINITY
        );
        assert_eq!(rejected, original);
        let checkpoint = BroadFlightObservation::Checkpoint {
            id: "synthetic-checkpoint".to_string(),
            time: Seconds(0.0),
        };
        assert_eq!(
            model.observe_state(&mut rejected, &checkpoint).unwrap(),
            f64::NEG_INFINITY
        );
        assert_eq!(rejected, original);
    }
}
