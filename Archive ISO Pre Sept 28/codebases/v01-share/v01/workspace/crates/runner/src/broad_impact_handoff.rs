//! Versioned, broad-flight-aware terminal/impact handoff.
//!
//! This schema carries every terminal draw, including zero-support and
//! non-impact outcomes. It therefore does not silently condition the exported
//! population on impact. One artifact represents one numerical seed and one
//! explicitly named terminal family; family comparison remains external.

use std::{
    collections::{BTreeMap, BTreeSet},
    error::Error,
    fmt,
};

use mh370_domain::LatLon;
use mh370_end_of_flight::TransitionTermination;
use mh370_estimator::{
    BroadConditioningSemanticsV1, BroadPosteriorParticleIdentityV1, BroadPriorRootIdentityV1,
    BroadRejectionReason, BROAD_POSTERIOR_HANDOFF_SCHEMA_VERSION,
};
use mh370_particle_filter::StratumId;
use serde::{Deserialize, Serialize};

use crate::impact_handoff::{
    AbsoluteTimeBasisV1, EnuVelocityV1, EvidenceApplicationRoleV1, EvidenceDispositionV2,
    EvidenceIdentityV2, EvidenceLedgerV2, ImpactAttitudeIntervalsV1, ImpactEnergyV1,
    PositiveIntervalV1,
};

pub(crate) const BROAD_IMPACT_HANDOFF_SCHEMA_ID: &str = "mh370-broad-terminal-impact-handoff";
pub(crate) const BROAD_IMPACT_HANDOFF_SCHEMA_VERSION: u32 = 1;

const WEIGHT_TOLERANCE: f64 = 1.0e-10;
const PHYSICAL_TOLERANCE: f64 = 1.0e-8;
const TIME_TOLERANCE_S: f64 = 1.0e-6;
const M0011_TIME_UNIX_S: f64 = 1_394_237_459.0;
const CORRECTED_R600_TIME_UNIX_S: f64 = 1_394_237_969.416;
const CORRECTED_R600_ELAPSED_FROM_M0011_S: f64 = 510.416;
const CORRECTED_R600_BTO_US: f64 = 18_400.0;
const CORRECTED_R600_BTO_SD_US: f64 = 63.0;

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub(crate) struct BroadImpactHandoffV1 {
    pub schema_id: String,
    pub schema_version: u32,
    pub time_basis: AbsoluteTimeBasisV1,
    pub run: BroadImpactRunProvenanceV1,
    pub parent: BroadImpactParentV1,
    pub terminal_family: BroadTerminalFamilyV1,
    pub r600_evidence: BroadR600EvidenceV1,
    pub terminal_evidence_model: BroadTerminalEvidenceModelV1,
    pub evidence: EvidenceLedgerV2,
    pub outcome_mass: BroadOutcomeMassV1,
    pub particles: Vec<BroadTerminalParticleV1>,
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub(crate) struct BroadImpactRunProvenanceV1 {
    pub hypothesis_id: String,
    pub run_identity_sha256: String,
    pub producer_executable_sha256: String,
    pub config_sha256: String,
    pub input_sha256: BTreeMap<String, String>,
    pub model_sha256: BroadImpactModelHashesV1,
    pub code_revision: String,
    pub terminal_seed: u64,
    pub transition_sidecar_sha256: String,
}

/// Required hashes are typed so a run cannot satisfy provenance with an
/// unrelated single map entry.
#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub(crate) struct BroadImpactModelHashesV1 {
    pub dynamics_sha256: String,
    pub fuel_sha256: String,
    pub satcom_sha256: String,
    pub end_of_flight_sha256: String,
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub(crate) struct BroadImpactParentV1 {
    pub schema_version: u32,
    pub handoff_sha256: String,
    pub run_identity_sha256: String,
    pub config_sha256: String,
    pub input_sha256: BTreeMap<String, String>,
    /// Hash of the evidence ledger serialized inside the parent handoff.
    pub evidence_ledger_sha256: String,
    /// Exact identities consumed upstream. Every identity must also appear in
    /// this artifact's open ledger under an EmbeddedUpstream application.
    pub consumed_evidence: Vec<EvidenceIdentityV2>,
    pub model_family: String,
    pub seed: u64,
    pub checkpoint_id: String,
    pub source_epoch_id: String,
    pub checkpoint_time_unix_s_utc: f64,
    pub conditioning: BroadConditioningSemanticsV1,
    pub configured_particle_count: usize,
    pub retained_particle_count: usize,
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub(crate) struct BroadTerminalFamilyV1 {
    pub id: String,
    pub model_family: String,
    pub config_sha256: String,
    pub model_sha256: BroadTerminalModelHashesV1,
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub(crate) struct BroadTerminalModelHashesV1 {
    pub end_of_flight_sha256: String,
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub(crate) struct BroadR600EvidenceV1 {
    pub identity: EvidenceIdentityV2,
    pub dependence_group_id: String,
    pub application_id: String,
    pub time_utc_unix_s: f64,
    pub elapsed_from_parent_checkpoint_s: f64,
    pub observed_bto_us: f64,
    pub standard_deviation_us: f64,
}

/// The primary branch uses R600 BTO alone. The sensitivity branch applies one
/// atomic update to R600 BTO and a log-on request lag conditional on dual-engine
/// exhaustion; these branches are alternatives and cannot be stacked.
#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(tag = "branch", rename_all = "snake_case")]
pub(crate) enum BroadTerminalEvidenceModelV1 {
    R600BtoOnly,
    JointR600BtoAndLogonTiming {
        logon_request_identity: EvidenceIdentityV2,
        fuel_exhaustion_window_identity: EvidenceIdentityV2,
        logon_occurrence_identity: EvidenceIdentityV2,
        erlang_shape: u32,
        erlang_rate_per_s: f64,
    },
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub(crate) enum BroadLogonTimingZeroSupportReasonV1 {
    ExhaustionAtOrAfterLogonRequest,
    NoExhaustionByBound,
    ContinuationRejectedBeforeExhaustion,
    FuelModelUnavailable,
    AlreadyExhaustedBeforeCheckpoint,
}

#[derive(Debug, Clone, Copy, PartialEq, Serialize, Deserialize)]
#[serde(tag = "status", rename_all = "snake_case")]
pub(crate) enum BroadLogonTimingParticleEvidenceV1 {
    Scored {
        dual_engine_exhaustion_time_utc_unix_s: f64,
        logon_request_lag_s: f64,
        log_likelihood: f64,
    },
    ZeroSupport {
        reason: BroadLogonTimingZeroSupportReasonV1,
    },
}

#[derive(Debug, Clone, PartialEq, Eq, PartialOrd, Ord, Serialize, Deserialize)]
pub(crate) struct BroadTerminalDrawIdentityV1 {
    pub terminal_seed: u64,
    pub terminal_family_id: String,
    pub draw_id: u32,
}

#[derive(Debug, Clone, PartialEq, Eq, PartialOrd, Ord, Serialize, Deserialize)]
pub(crate) struct BroadTerminalParticleIdentityV1 {
    pub parent: BroadPosteriorParticleIdentityV1,
    pub prior_root: BroadPriorRootIdentityV1,
    pub stratum: StratumId,
    pub terminal_draw: BroadTerminalDrawIdentityV1,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub(crate) enum BroadR600ZeroSupportReasonV1 {
    DidNotReachEpoch,
    SatcomUnpowered,
    RejectedBeforeEpoch,
}

#[derive(Debug, Clone, Copy, PartialEq, Serialize, Deserialize)]
#[serde(tag = "status", rename_all = "snake_case")]
pub(crate) enum BroadR600ParticleEvidenceV1 {
    Scored {
        predicted_bto_us: f64,
        residual_observed_minus_predicted_us: f64,
        log_likelihood: f64,
    },
    ZeroSupport {
        reason: BroadR600ZeroSupportReasonV1,
    },
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(tag = "outcome", rename_all = "snake_case")]
pub(crate) enum BroadTerminalOutcomeV1 {
    Impact,
    NoExhaustionByBound,
    PoweredContinuationRejected { reason: BroadRejectionReason },
    FuelModelUnavailable,
    AlreadyExhaustedBeforeCheckpoint,
    EndOfFlightNonImpact { termination: TransitionTermination },
}

#[derive(Debug, Clone, Copy, PartialEq, Serialize, Deserialize)]
pub(crate) struct BroadImpactDataV1 {
    pub time_utc_unix_s: f64,
    pub position_wgs84: LatLon,
    pub true_airspeed_m_s: f64,
    pub ground_velocity_enu_m_s: EnuVelocityV1,
    pub impact_angle_below_horizontal_deg: f64,
    pub mass_kg: f64,
    pub energy: ImpactEnergyV1,
    /// `None` is unresolved and must not be interpreted as level attitude.
    pub attitude: Option<ImpactAttitudeIntervalsV1>,
    /// `None` is unresolved; no nominal source duration may be invented.
    pub contact_duration_s: Option<PositiveIntervalV1>,
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub(crate) struct BroadTerminalParticleV1 {
    pub identity: BroadTerminalParticleIdentityV1,
    /// Filtering or smoothed weight, as declared by `parent.conditioning`.
    pub upstream_normalized_log_weight: f64,
    /// Normalized proposal allocation among draws of this parent particle.
    pub terminal_draw_log_probability: f64,
    /// Exact `log p - log q` for the continuation proposal.
    pub continuation_log_prior_over_proposal: f64,
    /// Termination time for every draw, including rejected and non-impact
    /// outcomes. This makes R600 reachability auditable without conditioning
    /// on an impact record being present.
    pub terminal_time_utc_unix_s: f64,
    pub r600: BroadR600ParticleEvidenceV1,
    /// Present exactly for the joint R600/log-on-timing sensitivity branch.
    pub logon_timing: Option<BroadLogonTimingParticleEvidenceV1>,
    /// `None` denotes exact zero posterior support and is serialized as null.
    pub posterior_normalized_log_weight: Option<f64>,
    pub outcome: BroadTerminalOutcomeV1,
    /// Present exactly for an impact outcome.
    pub impact: Option<BroadImpactDataV1>,
}

#[derive(Debug, Clone, Copy, Default, PartialEq, Serialize, Deserialize)]
pub(crate) struct BroadOutcomeMassCellV1 {
    pub draw_count: usize,
    pub pre_r600_normalized_mass: f64,
    pub posterior_normalized_mass: f64,
}

#[derive(Debug, Clone, Copy, Default, PartialEq, Serialize, Deserialize)]
pub(crate) struct BroadOutcomeMassV1 {
    pub impact: BroadOutcomeMassCellV1,
    pub no_exhaustion_by_bound: BroadOutcomeMassCellV1,
    pub rejected: BroadOutcomeMassCellV1,
    pub fuel_model_unavailable: BroadOutcomeMassCellV1,
    pub already_exhausted_before_checkpoint: BroadOutcomeMassCellV1,
    pub end_of_flight_non_impact: BroadOutcomeMassCellV1,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub(crate) enum BroadImpactHandoffError {
    UnsupportedSchema,
    InvalidTimeBasis,
    InvalidProvenance,
    InvalidParent,
    InvalidTerminalFamily,
    InvalidEvidence,
    InvalidParticle,
    InvalidPhysicalState,
    InvalidWeights,
    InvalidOutcomeMass,
    HiddenWeight,
}

impl fmt::Display for BroadImpactHandoffError {
    fn fmt(&self, formatter: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(formatter, "invalid broad impact handoff: {self:?}")
    }
}

impl Error for BroadImpactHandoffError {}

impl BroadImpactModelHashesV1 {
    fn valid(&self) -> bool {
        valid_sha256(&self.dynamics_sha256)
            && valid_sha256(&self.fuel_sha256)
            && valid_sha256(&self.satcom_sha256)
            && valid_sha256(&self.end_of_flight_sha256)
    }
}

impl BroadTerminalModelHashesV1 {
    fn valid(&self) -> bool {
        valid_sha256(&self.end_of_flight_sha256)
    }
}

impl BroadImpactHandoffV1 {
    pub(crate) fn validate(&self) -> Result<(), BroadImpactHandoffError> {
        self.validate_header()?;
        self.validate_parent()?;
        self.validate_terminal_family()?;
        let evidence_log_increment = self.validate_evidence()?;
        self.validate_particles(evidence_log_increment)
    }

    fn validate_header(&self) -> Result<(), BroadImpactHandoffError> {
        if self.schema_id != BROAD_IMPACT_HANDOFF_SCHEMA_ID
            || self.schema_version != BROAD_IMPACT_HANDOFF_SCHEMA_VERSION
        {
            return Err(BroadImpactHandoffError::UnsupportedSchema);
        }
        if self.time_basis.scale != "utc"
            || self.time_basis.epoch != "1970-01-01T00:00:00Z"
            || self.time_basis.unit != "second"
            || self.time_basis.convention != "posix_seconds_no_leap_representation"
        {
            return Err(BroadImpactHandoffError::InvalidTimeBasis);
        }
        let run = &self.run;
        if !valid_identifier(&run.hypothesis_id)
            || !valid_sha256(&run.run_identity_sha256)
            || !valid_sha256(&run.producer_executable_sha256)
            || !valid_sha256(&run.config_sha256)
            || !valid_sha256(&run.transition_sidecar_sha256)
            || run.code_revision.trim().is_empty()
            || !valid_hash_map(&run.input_sha256)
            || !run.model_sha256.valid()
        {
            return Err(BroadImpactHandoffError::InvalidProvenance);
        }
        Ok(())
    }

    fn validate_parent(&self) -> Result<(), BroadImpactHandoffError> {
        let parent = &self.parent;
        let conditioning_valid = match &parent.conditioning {
            BroadConditioningSemanticsV1::Filtering { through_epoch_id } => {
                through_epoch_id == "m0011"
            }
            BroadConditioningSemanticsV1::Smoothed {
                filtering_checkpoint_id,
                conditioned_through_epoch_id,
            } => {
                let endpoint = conditioned_through_epoch_id.to_ascii_lowercase();
                valid_identifier(filtering_checkpoint_id)
                    && valid_identifier(conditioned_through_epoch_id)
                    && !endpoint.contains("r600")
                    && !endpoint.contains("m0019")
            }
        };
        if parent.schema_version != BROAD_POSTERIOR_HANDOFF_SCHEMA_VERSION
            || !valid_sha256(&parent.handoff_sha256)
            || !valid_sha256(&parent.run_identity_sha256)
            || !valid_sha256(&parent.config_sha256)
            || !valid_hash_map(&parent.input_sha256)
            || !valid_sha256(&parent.evidence_ledger_sha256)
            || parent.consumed_evidence.is_empty()
            || !valid_identifier(&parent.model_family)
            || !valid_identifier(&parent.checkpoint_id)
            || !valid_identifier(&parent.source_epoch_id)
            || !time_close(parent.checkpoint_time_unix_s_utc, M0011_TIME_UNIX_S)
            || parent.configured_particle_count == 0
            || parent.retained_particle_count == 0
            || parent.retained_particle_count > parent.configured_particle_count
            || !conditioning_valid
        {
            return Err(BroadImpactHandoffError::InvalidParent);
        }
        Ok(())
    }

    fn validate_terminal_family(&self) -> Result<(), BroadImpactHandoffError> {
        if !valid_identifier(&self.terminal_family.id)
            || !valid_identifier(&self.terminal_family.model_family)
            || !valid_sha256(&self.terminal_family.config_sha256)
            || !self.terminal_family.model_sha256.valid()
        {
            return Err(BroadImpactHandoffError::InvalidTerminalFamily);
        }
        Ok(())
    }

    fn validate_evidence(&self) -> Result<f64, BroadImpactHandoffError> {
        let applications = self
            .evidence
            .validate()
            .map_err(|_| BroadImpactHandoffError::InvalidEvidence)?;
        let r600 = &self.r600_evidence;
        if !valid_identifier(&r600.dependence_group_id)
            || !valid_identifier(&r600.application_id)
            || r600.identity.observation_id != "m0019-r600"
            || r600.identity.component_id != "bto"
            || r600.identity.channel_id.as_deref() != Some("r600")
            || !time_close(r600.time_utc_unix_s, CORRECTED_R600_TIME_UNIX_S)
            || !time_close(
                r600.elapsed_from_parent_checkpoint_s,
                CORRECTED_R600_ELAPSED_FROM_M0011_S,
            )
            || !time_close(
                r600.elapsed_from_parent_checkpoint_s,
                r600.time_utc_unix_s - self.parent.checkpoint_time_unix_s_utc,
            )
            || !r600.observed_bto_us.is_finite()
            || r600.observed_bto_us.to_bits() != CORRECTED_R600_BTO_US.to_bits()
            || !r600.standard_deviation_us.is_finite()
            || r600.standard_deviation_us.to_bits() != CORRECTED_R600_BTO_SD_US.to_bits()
        {
            return Err(BroadImpactHandoffError::InvalidEvidence);
        }
        let application = applications
            .get(r600.application_id.as_str())
            .copied()
            .ok_or(BroadImpactHandoffError::InvalidEvidence)?;
        if application.role != EvidenceApplicationRoleV1::WeightUpdate {
            return Err(BroadImpactHandoffError::InvalidEvidence);
        }
        let weight_updates = applications
            .values()
            .filter(|application| application.role == EvidenceApplicationRoleV1::WeightUpdate)
            .count();
        let embedded_upstream = self
            .evidence
            .entries
            .iter()
            .filter(|entry| {
                entry.disposition == EvidenceDispositionV2::Consumed
                    && entry
                        .application_id
                        .as_deref()
                        .and_then(|id| applications.get(id))
                        .is_some_and(|application| {
                            application.role == EvidenceApplicationRoleV1::EmbeddedUpstream
                        })
            })
            .map(|entry| &entry.identity)
            .collect::<BTreeSet<_>>();
        let declared_upstream = self
            .parent
            .consumed_evidence
            .iter()
            .collect::<BTreeSet<_>>();
        let matching_entries = self
            .evidence
            .entries
            .iter()
            .filter(|entry| entry.application_id.as_deref() == Some(r600.application_id.as_str()))
            .collect::<Vec<_>>();
        let branch_valid = match &self.terminal_evidence_model {
            BroadTerminalEvidenceModelV1::R600BtoOnly => {
                matching_entries.len() == 1
                    && matching_entries[0].identity == r600.identity
                    && matching_entries[0].dependence_group_id == r600.dependence_group_id
                    && matching_entries[0].disposition == EvidenceDispositionV2::Consumed
            }
            BroadTerminalEvidenceModelV1::JointR600BtoAndLogonTiming {
                logon_request_identity,
                fuel_exhaustion_window_identity,
                logon_occurrence_identity,
                erlang_shape,
                erlang_rate_per_s,
            } => {
                let r600_entry = matching_entries
                    .iter()
                    .copied()
                    .find(|entry| entry.identity == r600.identity);
                let logon_request = self.evidence.entries.iter().find(|entry| {
                    entry.identity == *logon_request_identity
                        && entry.application_id.as_deref() == Some(r600.application_id.as_str())
                });
                let fuel_window = self
                    .evidence
                    .entries
                    .iter()
                    .find(|entry| entry.identity == *fuel_exhaustion_window_identity);
                let logon_occurrence = self
                    .evidence
                    .entries
                    .iter()
                    .find(|entry| entry.identity == *logon_occurrence_identity);
                *erlang_shape > 0
                    && erlang_rate_per_s.is_finite()
                    && *erlang_rate_per_s > 0.0
                    && logon_request_identity.component_id == "logon_request_time"
                    && fuel_exhaustion_window_identity.component_id == "fuel_exhaustion_window"
                    && logon_occurrence_identity.component_id == "logon_occurrence"
                    && logon_request_identity != &r600.identity
                    && fuel_exhaustion_window_identity != &r600.identity
                    && logon_occurrence_identity != &r600.identity
                    && logon_request_identity != fuel_exhaustion_window_identity
                    && logon_request_identity != logon_occurrence_identity
                    && fuel_exhaustion_window_identity != logon_occurrence_identity
                    && matching_entries.len() == 2
                    && r600_entry.is_some_and(|entry| {
                        entry.dependence_group_id == r600.dependence_group_id
                            && entry.disposition == EvidenceDispositionV2::Consumed
                    })
                    && logon_request.is_some_and(|entry| {
                        entry.dependence_group_id == r600.dependence_group_id
                            && entry.disposition == EvidenceDispositionV2::Consumed
                    })
                    && fuel_window.is_some_and(|entry| {
                        entry.disposition == EvidenceDispositionV2::HeldOut
                            && entry.application_id.is_none()
                    })
                    && logon_occurrence.is_some_and(|entry| {
                        entry.disposition == EvidenceDispositionV2::HeldOut
                            && entry.application_id.is_none()
                    })
                    && !declared_upstream.contains(logon_request_identity)
            }
        };
        if declared_upstream.len() != self.parent.consumed_evidence.len()
            || declared_upstream.contains(&r600.identity)
            || embedded_upstream != declared_upstream
            || weight_updates != 1
            || !branch_valid
        {
            return Err(BroadImpactHandoffError::InvalidEvidence);
        }
        application
            .log_evidence_increment
            .filter(|value| value.is_finite())
            .ok_or(BroadImpactHandoffError::InvalidEvidence)
    }

    fn validate_particles(
        &self,
        declared_evidence_increment: f64,
    ) -> Result<(), BroadImpactHandoffError> {
        if self.particles.is_empty() {
            return Err(BroadImpactHandoffError::InvalidParticle);
        }
        let mut identities = BTreeSet::new();
        let mut parents = BTreeMap::<BroadPosteriorParticleIdentityV1, ParentDrawValidation>::new();
        let mut pre_weights = Vec::with_capacity(self.particles.len());
        let mut posterior_weights = Vec::new();
        let mut posterior_raw_weights = Vec::new();

        for particle in &self.particles {
            if !identities.insert(&particle.identity) {
                return Err(BroadImpactHandoffError::InvalidParticle);
            }
            self.validate_identity_and_weight(particle, &mut parents)?;
            self.validate_outcome_and_impact(particle)?;
            if !particle.terminal_time_utc_unix_s.is_finite()
                || particle.terminal_time_utc_unix_s
                    < self.parent.checkpoint_time_unix_s_utc - TIME_TOLERANCE_S
            {
                return Err(BroadImpactHandoffError::InvalidPhysicalState);
            }
            let pre_weight = particle.upstream_normalized_log_weight
                + particle.terminal_draw_log_probability
                + particle.continuation_log_prior_over_proposal;
            if !pre_weight.is_finite() {
                return Err(BroadImpactHandoffError::InvalidWeights);
            }
            pre_weights.push(pre_weight);
            match (
                self.validate_particle_evidence(particle)?,
                particle.posterior_normalized_log_weight,
            ) {
                (Some(log_likelihood), Some(posterior_weight)) if posterior_weight.is_finite() => {
                    posterior_raw_weights.push(pre_weight + log_likelihood);
                    posterior_weights.push(posterior_weight);
                }
                (None, None) => {}
                _ => return Err(BroadImpactHandoffError::InvalidWeights),
            }
        }

        if parents.len() != self.parent.retained_particle_count {
            return Err(BroadImpactHandoffError::InvalidParent);
        }
        require_normalized(
            parents
                .values()
                .map(|parent| parent.upstream_normalized_log_weight),
        )?;
        for parent in parents.values() {
            if parent.draws.len() != parent.draw_ids.len()
                || parent
                    .draw_ids
                    .iter()
                    .copied()
                    .enumerate()
                    .any(|(expected, observed)| observed as usize != expected)
            {
                return Err(BroadImpactHandoffError::InvalidParticle);
            }
            require_normalized(parent.draws.iter().copied())?;
        }

        let pre_normalizer = log_sum_exp(pre_weights.iter().copied())
            .ok_or(BroadImpactHandoffError::InvalidWeights)?;
        let posterior_normalizer = log_sum_exp(posterior_raw_weights.iter().copied())
            .ok_or(BroadImpactHandoffError::InvalidWeights)?;
        if !close(
            posterior_normalizer - pre_normalizer,
            declared_evidence_increment,
            WEIGHT_TOLERANCE,
        ) {
            return Err(BroadImpactHandoffError::HiddenWeight);
        }
        require_normalized(posterior_weights.iter().copied())?;
        let mut scored_index = 0;
        for particle in &self.particles {
            if let Some(posterior_weight) = particle.posterior_normalized_log_weight {
                if !close(
                    posterior_weight,
                    posterior_raw_weights[scored_index] - posterior_normalizer,
                    WEIGHT_TOLERANCE,
                ) {
                    return Err(BroadImpactHandoffError::HiddenWeight);
                }
                scored_index += 1;
            }
        }
        self.validate_outcome_mass(&pre_weights, pre_normalizer)
    }

    fn validate_particle_evidence(
        &self,
        particle: &BroadTerminalParticleV1,
    ) -> Result<Option<f64>, BroadImpactHandoffError> {
        let r600_log_likelihood = match particle.r600 {
            BroadR600ParticleEvidenceV1::Scored {
                predicted_bto_us,
                residual_observed_minus_predicted_us,
                log_likelihood,
            } => {
                if !valid_r600_score(
                    &self.r600_evidence,
                    predicted_bto_us,
                    residual_observed_minus_predicted_us,
                    log_likelihood,
                ) || particle.terminal_time_utc_unix_s
                    < CORRECTED_R600_TIME_UNIX_S - TIME_TOLERANCE_S
                {
                    return Err(BroadImpactHandoffError::InvalidEvidence);
                }
                Some(log_likelihood)
            }
            BroadR600ParticleEvidenceV1::ZeroSupport {
                reason:
                    BroadR600ZeroSupportReasonV1::DidNotReachEpoch
                    | BroadR600ZeroSupportReasonV1::RejectedBeforeEpoch,
            } if particle.terminal_time_utc_unix_s
                < CORRECTED_R600_TIME_UNIX_S - TIME_TOLERANCE_S =>
            {
                None
            }
            BroadR600ParticleEvidenceV1::ZeroSupport {
                reason: BroadR600ZeroSupportReasonV1::SatcomUnpowered,
            } if particle.terminal_time_utc_unix_s
                >= CORRECTED_R600_TIME_UNIX_S - TIME_TOLERANCE_S =>
            {
                None
            }
            _ => return Err(BroadImpactHandoffError::InvalidEvidence),
        };

        match (&self.terminal_evidence_model, r600_log_likelihood) {
            (BroadTerminalEvidenceModelV1::R600BtoOnly, value) => {
                if particle.logon_timing.is_some() {
                    return Err(BroadImpactHandoffError::InvalidEvidence);
                }
                Ok(value)
            }
            (
                BroadTerminalEvidenceModelV1::JointR600BtoAndLogonTiming {
                    erlang_shape,
                    erlang_rate_per_s,
                    ..
                },
                Some(r600_log_likelihood),
            ) => {
                let timing = particle
                    .logon_timing
                    .ok_or(BroadImpactHandoffError::InvalidEvidence)?;
                match timing {
                    BroadLogonTimingParticleEvidenceV1::Scored {
                        dual_engine_exhaustion_time_utc_unix_s,
                        logon_request_lag_s,
                        log_likelihood,
                    } => {
                        if !valid_erlang_lag_score(
                            dual_engine_exhaustion_time_utc_unix_s,
                            logon_request_lag_s,
                            log_likelihood,
                            *erlang_shape,
                            *erlang_rate_per_s,
                            self.parent.checkpoint_time_unix_s_utc,
                        ) {
                            return Err(BroadImpactHandoffError::InvalidEvidence);
                        }
                        Ok(Some(r600_log_likelihood + log_likelihood))
                    }
                    BroadLogonTimingParticleEvidenceV1::ZeroSupport { reason } => {
                        if !logon_zero_support_matches_outcome(reason, particle.outcome) {
                            return Err(BroadImpactHandoffError::InvalidEvidence);
                        }
                        Ok(None)
                    }
                }
            }
            (BroadTerminalEvidenceModelV1::JointR600BtoAndLogonTiming { .. }, None) => {
                if particle.logon_timing.is_some() {
                    return Err(BroadImpactHandoffError::InvalidEvidence);
                }
                Ok(None)
            }
        }
    }

    fn validate_identity_and_weight(
        &self,
        particle: &BroadTerminalParticleV1,
        parents: &mut BTreeMap<BroadPosteriorParticleIdentityV1, ParentDrawValidation>,
    ) -> Result<(), BroadImpactHandoffError> {
        let identity = &particle.identity;
        if identity.parent.model_family != self.parent.model_family
            || identity.parent.seed != self.parent.seed
            || identity.parent.checkpoint_id != self.parent.checkpoint_id
            || identity.parent.particle >= self.parent.configured_particle_count
            || identity.prior_root.model_family != self.parent.model_family
            || identity.prior_root.seed != self.parent.seed
            || identity.prior_root.source_epoch_id != self.parent.source_epoch_id
            || identity.prior_root.initial_particle >= self.parent.configured_particle_count
            || identity.prior_root.stratum != identity.stratum
            || identity.terminal_draw.terminal_seed != self.run.terminal_seed
            || identity.terminal_draw.terminal_family_id != self.terminal_family.id
            || !particle.upstream_normalized_log_weight.is_finite()
            || particle.upstream_normalized_log_weight > WEIGHT_TOLERANCE
            || !particle.terminal_draw_log_probability.is_finite()
            || particle.terminal_draw_log_probability > WEIGHT_TOLERANCE
            || !particle.continuation_log_prior_over_proposal.is_finite()
        {
            return Err(BroadImpactHandoffError::InvalidParticle);
        }
        match parents.get_mut(&identity.parent) {
            Some(parent) => {
                if parent.prior_root != identity.prior_root
                    || parent.stratum != identity.stratum
                    || parent.upstream_normalized_log_weight.to_bits()
                        != particle.upstream_normalized_log_weight.to_bits()
                    || !parent.draw_ids.insert(identity.terminal_draw.draw_id)
                {
                    return Err(BroadImpactHandoffError::InvalidParticle);
                }
                parent.draws.push(particle.terminal_draw_log_probability);
            }
            None => {
                parents.insert(
                    identity.parent.clone(),
                    ParentDrawValidation {
                        prior_root: identity.prior_root.clone(),
                        stratum: identity.stratum,
                        upstream_normalized_log_weight: particle.upstream_normalized_log_weight,
                        draw_ids: BTreeSet::from([identity.terminal_draw.draw_id]),
                        draws: vec![particle.terminal_draw_log_probability],
                    },
                );
            }
        }
        Ok(())
    }

    fn validate_outcome_and_impact(
        &self,
        particle: &BroadTerminalParticleV1,
    ) -> Result<(), BroadImpactHandoffError> {
        match (particle.outcome, particle.impact) {
            (BroadTerminalOutcomeV1::Impact, Some(impact)) => {
                if !time_close(impact.time_utc_unix_s, particle.terminal_time_utc_unix_s) {
                    return Err(BroadImpactHandoffError::InvalidPhysicalState);
                }
                validate_impact(impact, self.parent.checkpoint_time_unix_s_utc)
            }
            (
                BroadTerminalOutcomeV1::EndOfFlightNonImpact {
                    termination: TransitionTermination::Impact,
                },
                _,
            )
            | (BroadTerminalOutcomeV1::Impact, None)
            | (_, Some(_)) => Err(BroadImpactHandoffError::InvalidPhysicalState),
            _ => Ok(()),
        }
    }

    fn validate_outcome_mass(
        &self,
        pre_weights: &[f64],
        pre_normalizer: f64,
    ) -> Result<(), BroadImpactHandoffError> {
        let mut calculated = BroadOutcomeMassV1::default();
        for (particle, pre_weight) in self.particles.iter().zip(pre_weights) {
            let cell = calculated.cell_mut(particle.outcome);
            cell.draw_count += 1;
            cell.pre_r600_normalized_mass += (*pre_weight - pre_normalizer).exp();
            cell.posterior_normalized_mass += particle
                .posterior_normalized_log_weight
                .map_or(0.0, f64::exp);
        }
        if !self.outcome_mass.valid()
            || self
                .outcome_mass
                .cells()
                .into_iter()
                .zip(calculated.cells())
                .any(|(declared, observed)| {
                    declared.draw_count != observed.draw_count
                        || !close(
                            declared.pre_r600_normalized_mass,
                            observed.pre_r600_normalized_mass,
                            WEIGHT_TOLERANCE,
                        )
                        || !close(
                            declared.posterior_normalized_mass,
                            observed.posterior_normalized_mass,
                            WEIGHT_TOLERANCE,
                        )
                })
        {
            return Err(BroadImpactHandoffError::InvalidOutcomeMass);
        }
        Ok(())
    }
}

struct ParentDrawValidation {
    prior_root: BroadPriorRootIdentityV1,
    stratum: StratumId,
    upstream_normalized_log_weight: f64,
    draw_ids: BTreeSet<u32>,
    draws: Vec<f64>,
}

impl BroadOutcomeMassV1 {
    fn cells(&self) -> [&BroadOutcomeMassCellV1; 6] {
        [
            &self.impact,
            &self.no_exhaustion_by_bound,
            &self.rejected,
            &self.fuel_model_unavailable,
            &self.already_exhausted_before_checkpoint,
            &self.end_of_flight_non_impact,
        ]
    }

    fn cell_mut(&mut self, outcome: BroadTerminalOutcomeV1) -> &mut BroadOutcomeMassCellV1 {
        match outcome {
            BroadTerminalOutcomeV1::Impact => &mut self.impact,
            BroadTerminalOutcomeV1::NoExhaustionByBound => &mut self.no_exhaustion_by_bound,
            BroadTerminalOutcomeV1::PoweredContinuationRejected { .. } => &mut self.rejected,
            BroadTerminalOutcomeV1::FuelModelUnavailable => &mut self.fuel_model_unavailable,
            BroadTerminalOutcomeV1::AlreadyExhaustedBeforeCheckpoint => {
                &mut self.already_exhausted_before_checkpoint
            }
            BroadTerminalOutcomeV1::EndOfFlightNonImpact { .. } => {
                &mut self.end_of_flight_non_impact
            }
        }
    }

    fn valid(&self) -> bool {
        let cells = self.cells();
        let values_valid = cells.iter().all(|cell| {
            cell.pre_r600_normalized_mass.is_finite()
                && (0.0..=1.0).contains(&cell.pre_r600_normalized_mass)
                && cell.posterior_normalized_mass.is_finite()
                && (0.0..=1.0).contains(&cell.posterior_normalized_mass)
        });
        let pre_sum = cells
            .iter()
            .map(|cell| cell.pre_r600_normalized_mass)
            .sum::<f64>();
        let posterior_sum = cells
            .iter()
            .map(|cell| cell.posterior_normalized_mass)
            .sum::<f64>();
        values_valid
            && close(pre_sum, 1.0, WEIGHT_TOLERANCE)
            && close(posterior_sum, 1.0, WEIGHT_TOLERANCE)
    }
}

fn valid_r600_score(
    observation: &BroadR600EvidenceV1,
    predicted_bto_us: f64,
    residual_us: f64,
    log_likelihood: f64,
) -> bool {
    if !predicted_bto_us.is_finite()
        || !residual_us.is_finite()
        || !log_likelihood.is_finite()
        || !close(
            residual_us,
            observation.observed_bto_us - predicted_bto_us,
            PHYSICAL_TOLERANCE,
        )
    {
        return false;
    }
    let z = residual_us / observation.standard_deviation_us;
    let expected =
        -0.5 * z * z - observation.standard_deviation_us.ln() - 0.5 * std::f64::consts::TAU.ln();
    close(log_likelihood, expected, PHYSICAL_TOLERANCE)
}

fn valid_erlang_lag_score(
    dual_engine_exhaustion_time_utc_unix_s: f64,
    logon_request_lag_s: f64,
    log_likelihood: f64,
    shape: u32,
    rate_per_s: f64,
    parent_checkpoint_time: f64,
) -> bool {
    if shape == 0
        || !rate_per_s.is_finite()
        || rate_per_s <= 0.0
        || !dual_engine_exhaustion_time_utc_unix_s.is_finite()
        || dual_engine_exhaustion_time_utc_unix_s <= parent_checkpoint_time + TIME_TOLERANCE_S
        || dual_engine_exhaustion_time_utc_unix_s >= CORRECTED_R600_TIME_UNIX_S - TIME_TOLERANCE_S
        || !time_close(
            logon_request_lag_s,
            CORRECTED_R600_TIME_UNIX_S - dual_engine_exhaustion_time_utc_unix_s,
        )
        || logon_request_lag_s <= 0.0
        || !log_likelihood.is_finite()
    {
        return false;
    }
    let log_factorial = (1..shape).map(|value| f64::from(value).ln()).sum::<f64>();
    let expected = f64::from(shape) * rate_per_s.ln()
        + f64::from(shape - 1) * logon_request_lag_s.ln()
        - rate_per_s * logon_request_lag_s
        - log_factorial;
    close(log_likelihood, expected, PHYSICAL_TOLERANCE)
}

fn logon_zero_support_matches_outcome(
    reason: BroadLogonTimingZeroSupportReasonV1,
    outcome: BroadTerminalOutcomeV1,
) -> bool {
    matches!(
        (reason, outcome),
        (
            BroadLogonTimingZeroSupportReasonV1::ExhaustionAtOrAfterLogonRequest,
            BroadTerminalOutcomeV1::Impact | BroadTerminalOutcomeV1::EndOfFlightNonImpact { .. }
        ) | (
            BroadLogonTimingZeroSupportReasonV1::NoExhaustionByBound,
            BroadTerminalOutcomeV1::NoExhaustionByBound
        ) | (
            BroadLogonTimingZeroSupportReasonV1::ContinuationRejectedBeforeExhaustion,
            BroadTerminalOutcomeV1::PoweredContinuationRejected { .. }
        ) | (
            BroadLogonTimingZeroSupportReasonV1::FuelModelUnavailable,
            BroadTerminalOutcomeV1::FuelModelUnavailable
        ) | (
            BroadLogonTimingZeroSupportReasonV1::AlreadyExhaustedBeforeCheckpoint,
            BroadTerminalOutcomeV1::AlreadyExhaustedBeforeCheckpoint
        )
    )
}

fn validate_impact(
    impact: BroadImpactDataV1,
    parent_checkpoint_time: f64,
) -> Result<(), BroadImpactHandoffError> {
    let velocity = impact.ground_velocity_enu_m_s;
    if !impact.time_utc_unix_s.is_finite()
        || impact.time_utc_unix_s < parent_checkpoint_time
        || !valid_position(impact.position_wgs84)
        || !impact.true_airspeed_m_s.is_finite()
        || impact.true_airspeed_m_s <= 0.0
        || !velocity.east.is_finite()
        || !velocity.north.is_finite()
        || !velocity.up.is_finite()
        || velocity.up >= 0.0
        || velocity.east.hypot(velocity.north) <= 0.0
        || !impact.impact_angle_below_horizontal_deg.is_finite()
        || !(0.0..=90.0).contains(&impact.impact_angle_below_horizontal_deg)
        || !impact.mass_kg.is_finite()
        || impact.mass_kg <= 0.0
        || impact.attitude.is_some()
        || impact.contact_duration_s.is_some()
    {
        return Err(BroadImpactHandoffError::InvalidPhysicalState);
    }
    let expected_impact_angle = (-velocity.up)
        .atan2(velocity.east.hypot(velocity.north))
        .to_degrees();
    if !close(
        impact.impact_angle_below_horizontal_deg,
        expected_impact_angle,
        PHYSICAL_TOLERANCE,
    ) {
        return Err(BroadImpactHandoffError::InvalidPhysicalState);
    }
    let horizontal = 0.5 * impact.mass_kg * (velocity.east.powi(2) + velocity.north.powi(2));
    let vertical = 0.5 * impact.mass_kg * velocity.up.powi(2);
    if !impact.energy.total_j.is_finite()
        || !impact.energy.horizontal_j.is_finite()
        || !impact.energy.vertical_j.is_finite()
        || !close(impact.energy.horizontal_j, horizontal, PHYSICAL_TOLERANCE)
        || !close(impact.energy.vertical_j, vertical, PHYSICAL_TOLERANCE)
        || !close(
            impact.energy.total_j,
            horizontal + vertical,
            PHYSICAL_TOLERANCE,
        )
    {
        return Err(BroadImpactHandoffError::InvalidPhysicalState);
    }
    Ok(())
}

fn valid_position(position: LatLon) -> bool {
    position.latitude.is_finite()
        && (-90.0..=90.0).contains(&position.latitude.0)
        && position.longitude.is_finite()
        && (-180.0..180.0).contains(&position.longitude.0)
}

fn valid_identifier(value: &str) -> bool {
    let mut bytes = value.bytes();
    matches!(bytes.next(), Some(byte) if byte.is_ascii_alphanumeric())
        && bytes
            .all(|byte| byte.is_ascii_alphanumeric() || matches!(byte, b'.' | b'_' | b':' | b'-'))
}

fn valid_sha256(value: &str) -> bool {
    value.len() == 64
        && value
            .bytes()
            .all(|byte| byte.is_ascii_digit() || (b'a'..=b'f').contains(&byte))
}

fn valid_hash_map(values: &BTreeMap<String, String>) -> bool {
    !values.is_empty()
        && values
            .iter()
            .all(|(identity, digest)| valid_identifier(identity) && valid_sha256(digest))
}

fn log_sum_exp(values: impl Iterator<Item = f64>) -> Option<f64> {
    let values = values.collect::<Vec<_>>();
    if values.is_empty() || values.iter().any(|value| !value.is_finite()) {
        return None;
    }
    let maximum = values.iter().copied().fold(f64::NEG_INFINITY, f64::max);
    let result = maximum
        + values
            .iter()
            .map(|value| (value - maximum).exp())
            .sum::<f64>()
            .ln();
    result.is_finite().then_some(result)
}

fn require_normalized(values: impl Iterator<Item = f64>) -> Result<(), BroadImpactHandoffError> {
    let log_sum = log_sum_exp(values).ok_or(BroadImpactHandoffError::InvalidWeights)?;
    if !close(log_sum, 0.0, WEIGHT_TOLERANCE) {
        return Err(BroadImpactHandoffError::InvalidWeights);
    }
    Ok(())
}

fn close(first: f64, second: f64, tolerance: f64) -> bool {
    (first - second).abs() <= tolerance * first.abs().max(second.abs()).max(1.0)
}

fn time_close(first: f64, second: f64) -> bool {
    first.is_finite() && second.is_finite() && (first - second).abs() <= TIME_TOLERANCE_S
}

#[cfg(test)]
mod tests {

    use super::*;
    use crate::impact_handoff::{AngularIntervalV1, EvidenceApplicationV1, EvidenceEntryV2};

    fn digest(byte: char) -> String {
        std::iter::repeat(byte).take(64).collect()
    }

    fn hashes(label: &str, byte: char) -> BTreeMap<String, String> {
        BTreeMap::from([(label.to_string(), digest(byte))])
    }

    fn r600_log_likelihood(residual_us: f64) -> f64 {
        let sd = 63.0;
        let z = residual_us / sd;
        -0.5 * z * z - sd.ln() - 0.5 * std::f64::consts::TAU.ln()
    }

    fn erlang_log_likelihood(shape: u32, rate_per_s: f64, lag_s: f64) -> f64 {
        f64::from(shape) * rate_per_s.ln() + f64::from(shape - 1) * lag_s.ln()
            - rate_per_s * lag_s
            - (1..shape).map(|value| f64::from(value).ln()).sum::<f64>()
    }

    fn impact() -> BroadImpactDataV1 {
        let mass = 1_000.0;
        let velocity = EnuVelocityV1 {
            east: 100.0,
            north: 0.0,
            up: -10.0,
        };
        let horizontal = 0.5 * mass * velocity.east.powi(2);
        let vertical = 0.5 * mass * velocity.up.powi(2);
        BroadImpactDataV1 {
            time_utc_unix_s: 1_394_238_069.416,
            position_wgs84: LatLon::new(-35.0, 92.0).unwrap(),
            true_airspeed_m_s: 101.0,
            ground_velocity_enu_m_s: velocity,
            impact_angle_below_horizontal_deg: 5.710_593_137,
            mass_kg: mass,
            energy: ImpactEnergyV1 {
                total_j: horizontal + vertical,
                horizontal_j: horizontal,
                vertical_j: vertical,
            },
            attitude: None,
            contact_duration_s: None,
        }
    }

    fn particle(index: usize, outcome: BroadTerminalOutcomeV1) -> BroadTerminalParticleV1 {
        let scored = index < 2;
        BroadTerminalParticleV1 {
            identity: BroadTerminalParticleIdentityV1 {
                parent: BroadPosteriorParticleIdentityV1 {
                    model_family: "broad-powered-marked-jump-v1".to_string(),
                    seed: 7,
                    checkpoint_id: "m0011-filtered".to_string(),
                    particle: index,
                },
                prior_root: BroadPriorRootIdentityV1 {
                    model_family: "broad-powered-marked-jump-v1".to_string(),
                    seed: 7,
                    source_epoch_id: "m1825".to_string(),
                    stratum: StratumId(1),
                    initial_particle: index,
                },
                stratum: StratumId(1),
                terminal_draw: BroadTerminalDrawIdentityV1 {
                    terminal_seed: 370_019,
                    terminal_family_id: "conditional-terminal-family".to_string(),
                    draw_id: 0,
                },
            },
            upstream_normalized_log_weight: 0.25_f64.ln(),
            terminal_draw_log_probability: 0.0,
            continuation_log_prior_over_proposal: 0.0,
            terminal_time_utc_unix_s: match index {
                0 => 1_394_238_069.416,
                1 => 1_394_238_300.0,
                2 => 1_394_237_600.0,
                _ => 1_394_238_500.0,
            },
            r600: if scored {
                BroadR600ParticleEvidenceV1::Scored {
                    predicted_bto_us: 18_390.0,
                    residual_observed_minus_predicted_us: 10.0,
                    log_likelihood: r600_log_likelihood(10.0),
                }
            } else {
                BroadR600ParticleEvidenceV1::ZeroSupport {
                    reason: if index == 2 {
                        BroadR600ZeroSupportReasonV1::RejectedBeforeEpoch
                    } else {
                        BroadR600ZeroSupportReasonV1::SatcomUnpowered
                    },
                }
            },
            logon_timing: None,
            posterior_normalized_log_weight: scored.then_some(0.5_f64.ln()),
            outcome,
            impact: (index == 0).then_some(impact()),
        }
    }

    fn handoff() -> BroadImpactHandoffV1 {
        let parent_bto_identity = EvidenceIdentityV2 {
            dataset_id: "inmarsat-satcom-log".to_string(),
            observation_id: "bto-through-m0011".to_string(),
            component_id: "bto".to_string(),
            channel_id: None,
        };
        let parent_bfo_identity = EvidenceIdentityV2 {
            dataset_id: "inmarsat-satcom-log".to_string(),
            observation_id: "bfo-through-m0011".to_string(),
            component_id: "bfo".to_string(),
            channel_id: None,
        };
        let r600_identity = EvidenceIdentityV2 {
            dataset_id: "inmarsat-satcom-log".to_string(),
            observation_id: "m0019-r600".to_string(),
            component_id: "bto".to_string(),
            channel_id: Some("r600".to_string()),
        };
        let r600_application = "r600-bto-likelihood".to_string();
        let log_likelihood = r600_log_likelihood(10.0);
        BroadImpactHandoffV1 {
            schema_id: BROAD_IMPACT_HANDOFF_SCHEMA_ID.to_string(),
            schema_version: BROAD_IMPACT_HANDOFF_SCHEMA_VERSION,
            time_basis: AbsoluteTimeBasisV1 {
                scale: "utc".to_string(),
                epoch: "1970-01-01T00:00:00Z".to_string(),
                unit: "second".to_string(),
                convention: "posix_seconds_no_leap_representation".to_string(),
            },
            run: BroadImpactRunProvenanceV1 {
                hypothesis_id: "broad-baseline".to_string(),
                run_identity_sha256: digest('a'),
                producer_executable_sha256: digest('b'),
                config_sha256: digest('c'),
                input_sha256: hashes("terminal-input", 'd'),
                model_sha256: BroadImpactModelHashesV1 {
                    dynamics_sha256: digest('d'),
                    fuel_sha256: digest('e'),
                    satcom_sha256: digest('f'),
                    end_of_flight_sha256: digest('a'),
                },
                code_revision: "0123456789abcdef".to_string(),
                terminal_seed: 370_019,
                transition_sidecar_sha256: digest('b'),
            },
            parent: BroadImpactParentV1 {
                schema_version: BROAD_POSTERIOR_HANDOFF_SCHEMA_VERSION,
                handoff_sha256: digest('1'),
                run_identity_sha256: digest('2'),
                config_sha256: digest('3'),
                input_sha256: hashes("satcom-input", '4'),
                evidence_ledger_sha256: digest('9'),
                consumed_evidence: vec![parent_bto_identity.clone(), parent_bfo_identity.clone()],
                model_family: "broad-powered-marked-jump-v1".to_string(),
                seed: 7,
                checkpoint_id: "m0011-filtered".to_string(),
                source_epoch_id: "m1825".to_string(),
                checkpoint_time_unix_s_utc: M0011_TIME_UNIX_S,
                conditioning: BroadConditioningSemanticsV1::Filtering {
                    through_epoch_id: "m0011".to_string(),
                },
                configured_particle_count: 4,
                retained_particle_count: 4,
            },
            terminal_family: BroadTerminalFamilyV1 {
                id: "conditional-terminal-family".to_string(),
                model_family: "controlled-to-uncontrolled-point-mass".to_string(),
                config_sha256: digest('5'),
                model_sha256: BroadTerminalModelHashesV1 {
                    end_of_flight_sha256: digest('6'),
                },
            },
            r600_evidence: BroadR600EvidenceV1 {
                identity: r600_identity.clone(),
                dependence_group_id: "satcom-m0019-r600".to_string(),
                application_id: r600_application.clone(),
                time_utc_unix_s: 1_394_237_969.416,
                elapsed_from_parent_checkpoint_s: CORRECTED_R600_ELAPSED_FROM_M0011_S,
                observed_bto_us: 18_400.0,
                standard_deviation_us: 63.0,
            },
            terminal_evidence_model: BroadTerminalEvidenceModelV1::R600BtoOnly,
            evidence: EvidenceLedgerV2 {
                entries: vec![
                    EvidenceEntryV2 {
                        identity: parent_bto_identity,
                        dependence_group_id: "satcom-bto-through-m0011".to_string(),
                        disposition: EvidenceDispositionV2::Consumed,
                        application_id: Some("parent-satcom".to_string()),
                    },
                    EvidenceEntryV2 {
                        identity: parent_bfo_identity,
                        dependence_group_id: "satcom-bfo-through-m0011".to_string(),
                        disposition: EvidenceDispositionV2::Consumed,
                        application_id: Some("parent-satcom".to_string()),
                    },
                    EvidenceEntryV2 {
                        identity: r600_identity,
                        dependence_group_id: "satcom-m0019-r600".to_string(),
                        disposition: EvidenceDispositionV2::Consumed,
                        application_id: Some(r600_application.clone()),
                    },
                ],
                applications: vec![
                    EvidenceApplicationV1 {
                        id: "parent-satcom".to_string(),
                        role: EvidenceApplicationRoleV1::EmbeddedUpstream,
                        model_family: "broad-satcom-through-m0011".to_string(),
                        config_sha256: digest('0'),
                        input_sha256: hashes("parent-satcom", '1'),
                        log_evidence_increment: None,
                    },
                    EvidenceApplicationV1 {
                        id: r600_application,
                        role: EvidenceApplicationRoleV1::WeightUpdate,
                        model_family: "normal-r600-bto".to_string(),
                        config_sha256: digest('7'),
                        input_sha256: hashes("r600", '8'),
                        log_evidence_increment: Some(log_likelihood + 0.5_f64.ln()),
                    },
                ],
            },
            outcome_mass: BroadOutcomeMassV1 {
                impact: BroadOutcomeMassCellV1 {
                    draw_count: 1,
                    pre_r600_normalized_mass: 0.25,
                    posterior_normalized_mass: 0.5,
                },
                no_exhaustion_by_bound: BroadOutcomeMassCellV1 {
                    draw_count: 1,
                    pre_r600_normalized_mass: 0.25,
                    posterior_normalized_mass: 0.5,
                },
                rejected: BroadOutcomeMassCellV1 {
                    draw_count: 1,
                    pre_r600_normalized_mass: 0.25,
                    posterior_normalized_mass: 0.0,
                },
                fuel_model_unavailable: BroadOutcomeMassCellV1::default(),
                already_exhausted_before_checkpoint: BroadOutcomeMassCellV1::default(),
                end_of_flight_non_impact: BroadOutcomeMassCellV1 {
                    draw_count: 1,
                    pre_r600_normalized_mass: 0.25,
                    posterior_normalized_mass: 0.0,
                },
            },
            particles: vec![
                particle(0, BroadTerminalOutcomeV1::Impact),
                particle(1, BroadTerminalOutcomeV1::NoExhaustionByBound),
                particle(
                    2,
                    BroadTerminalOutcomeV1::PoweredContinuationRejected {
                        reason: BroadRejectionReason::PoweredSegmentInfeasible,
                    },
                ),
                particle(
                    3,
                    BroadTerminalOutcomeV1::EndOfFlightNonImpact {
                        termination: TransitionTermination::MaximumDuration,
                    },
                ),
            ],
        }
    }

    #[test]
    fn valid_handoff_round_trips_with_explicit_null_unknowns() {
        let handoff = handoff();
        handoff.validate().unwrap();
        let encoded = serde_json::to_vec_pretty(&handoff).unwrap();
        let decoded: BroadImpactHandoffV1 = serde_json::from_slice(&encoded).unwrap();
        assert_eq!(decoded, handoff);
        assert!(encoded
            .windows(b"\"attitude\": null".len())
            .any(|window| { window == b"\"attitude\": null" }));
        assert!(encoded
            .windows(b"\"contact_duration_s\": null".len())
            .any(|window| { window == b"\"contact_duration_s\": null" }));
        decoded.validate().unwrap();
    }

    #[test]
    fn continuation_correction_is_visible_in_both_mass_summaries() {
        let mut handoff = handoff();
        handoff.particles[0].continuation_log_prior_over_proposal = 2.0_f64.ln();
        handoff.particles[0].posterior_normalized_log_weight = Some((2.0_f64 / 3.0).ln());
        handoff.particles[1].posterior_normalized_log_weight = Some((1.0_f64 / 3.0).ln());
        handoff.evidence.applications[1].log_evidence_increment =
            Some(r600_log_likelihood(10.0) + 0.6_f64.ln());
        handoff.outcome_mass.impact.pre_r600_normalized_mass = 0.4;
        handoff.outcome_mass.impact.posterior_normalized_mass = 2.0 / 3.0;
        handoff
            .outcome_mass
            .no_exhaustion_by_bound
            .pre_r600_normalized_mass = 0.2;
        handoff
            .outcome_mass
            .no_exhaustion_by_bound
            .posterior_normalized_mass = 1.0 / 3.0;
        handoff.outcome_mass.rejected.pre_r600_normalized_mass = 0.2;
        handoff
            .outcome_mass
            .end_of_flight_non_impact
            .pre_r600_normalized_mass = 0.2;
        handoff.validate().unwrap();

        handoff.particles[0].continuation_log_prior_over_proposal += 0.1;
        assert!(matches!(
            handoff.validate(),
            Err(BroadImpactHandoffError::HiddenWeight)
                | Err(BroadImpactHandoffError::InvalidOutcomeMass)
        ));
    }

    #[test]
    fn duplicate_r600_evidence_is_rejected() {
        let mut handoff = handoff();
        handoff
            .evidence
            .entries
            .push(handoff.evidence.entries[0].clone());
        assert_eq!(
            handoff.validate(),
            Err(BroadImpactHandoffError::InvalidEvidence)
        );
    }

    #[test]
    fn impact_energy_and_unknown_attitude_are_validated() {
        let mut invalid_energy = handoff();
        invalid_energy.particles[0]
            .impact
            .as_mut()
            .unwrap()
            .energy
            .total_j += 1_000.0;
        assert_eq!(
            invalid_energy.validate(),
            Err(BroadImpactHandoffError::InvalidPhysicalState)
        );

        let mut invented_attitude = handoff();
        invented_attitude.particles[0]
            .impact
            .as_mut()
            .unwrap()
            .attitude = Some(ImpactAttitudeIntervalsV1 {
            pitch_nose_up_deg: AngularIntervalV1 {
                center_deg: 0.0,
                half_width_deg: 1.0,
            },
            roll_right_wing_down_deg: AngularIntervalV1 {
                center_deg: 0.0,
                half_width_deg: 1.0,
            },
            yaw_true_deg: AngularIntervalV1 {
                center_deg: 180.0,
                half_width_deg: 1.0,
            },
        });
        assert_eq!(
            invented_attitude.validate(),
            Err(BroadImpactHandoffError::InvalidPhysicalState)
        );

        let mut inconsistent_angle = handoff();
        inconsistent_angle.particles[0]
            .impact
            .as_mut()
            .unwrap()
            .impact_angle_below_horizontal_deg = 20.0;
        assert_eq!(
            inconsistent_angle.validate(),
            Err(BroadImpactHandoffError::InvalidPhysicalState)
        );

        let mut climbing = handoff();
        let impact = climbing.particles[0].impact.as_mut().unwrap();
        impact.ground_velocity_enu_m_s.up = 10.0;
        assert_eq!(
            climbing.validate(),
            Err(BroadImpactHandoffError::InvalidPhysicalState)
        );
    }

    #[test]
    fn exact_r600_chronology_and_upstream_exclusion_are_enforced() {
        let mut wrong_time = handoff();
        wrong_time.r600_evidence.time_utc_unix_s += 1.0;
        wrong_time.r600_evidence.elapsed_from_parent_checkpoint_s += 1.0;
        assert_eq!(
            wrong_time.validate(),
            Err(BroadImpactHandoffError::InvalidEvidence)
        );

        let mut consumed_upstream = handoff();
        consumed_upstream
            .parent
            .consumed_evidence
            .push(consumed_upstream.r600_evidence.identity.clone());
        assert_eq!(
            consumed_upstream.validate(),
            Err(BroadImpactHandoffError::InvalidEvidence)
        );

        let mut impact_before_contact = handoff();
        let time = CORRECTED_R600_TIME_UNIX_S - 1.0;
        impact_before_contact.particles[0].terminal_time_utc_unix_s = time;
        impact_before_contact.particles[0]
            .impact
            .as_mut()
            .unwrap()
            .time_utc_unix_s = time;
        assert_eq!(
            impact_before_contact.validate(),
            Err(BroadImpactHandoffError::InvalidEvidence)
        );
    }

    #[test]
    fn joint_logon_timing_is_one_atomic_alternative_update() {
        let mut handoff = handoff();
        let logon_request = EvidenceIdentityV2 {
            dataset_id: "inmarsat-satcom-log".to_string(),
            observation_id: "m0019-logon-request".to_string(),
            component_id: "logon_request_time".to_string(),
            channel_id: Some("r600".to_string()),
        };
        let fuel_window = EvidenceIdentityV2 {
            dataset_id: "conditional-event-model".to_string(),
            observation_id: "dual-engine-exhaustion-window".to_string(),
            component_id: "fuel_exhaustion_window".to_string(),
            channel_id: None,
        };
        let logon_occurrence = EvidenceIdentityV2 {
            dataset_id: "inmarsat-satcom-log".to_string(),
            observation_id: "m0019-logon-occurrence".to_string(),
            component_id: "logon_occurrence".to_string(),
            channel_id: Some("r600".to_string()),
        };
        let shape = 2;
        let rate_per_s = 1.0 / 60.0;
        let lag_s = 120.0;
        let timing_log_likelihood = erlang_log_likelihood(shape, rate_per_s, lag_s);
        handoff.terminal_evidence_model =
            BroadTerminalEvidenceModelV1::JointR600BtoAndLogonTiming {
                logon_request_identity: logon_request.clone(),
                fuel_exhaustion_window_identity: fuel_window.clone(),
                logon_occurrence_identity: logon_occurrence.clone(),
                erlang_shape: shape,
                erlang_rate_per_s: rate_per_s,
            };
        handoff.evidence.entries.extend([
            EvidenceEntryV2 {
                identity: logon_request,
                dependence_group_id: handoff.r600_evidence.dependence_group_id.clone(),
                disposition: EvidenceDispositionV2::Consumed,
                application_id: Some(handoff.r600_evidence.application_id.clone()),
            },
            EvidenceEntryV2 {
                identity: fuel_window,
                dependence_group_id: "conditional-fuel-exhaustion".to_string(),
                disposition: EvidenceDispositionV2::HeldOut,
                application_id: None,
            },
            EvidenceEntryV2 {
                identity: logon_occurrence,
                dependence_group_id: "m0019-logon-occurrence".to_string(),
                disposition: EvidenceDispositionV2::HeldOut,
                application_id: None,
            },
        ]);
        for particle in &mut handoff.particles[..2] {
            particle.logon_timing = Some(BroadLogonTimingParticleEvidenceV1::Scored {
                dual_engine_exhaustion_time_utc_unix_s: CORRECTED_R600_TIME_UNIX_S - lag_s,
                logon_request_lag_s: lag_s,
                log_likelihood: timing_log_likelihood,
            });
        }
        handoff.evidence.applications[1].log_evidence_increment =
            Some(r600_log_likelihood(10.0) + timing_log_likelihood + 0.5_f64.ln());
        handoff.validate().unwrap();

        handoff.particles[1].logon_timing = Some(BroadLogonTimingParticleEvidenceV1::ZeroSupport {
            reason: BroadLogonTimingZeroSupportReasonV1::NoExhaustionByBound,
        });
        handoff.particles[1].posterior_normalized_log_weight = None;
        handoff.particles[0].posterior_normalized_log_weight = Some(0.0);
        handoff.evidence.applications[1].log_evidence_increment =
            Some(r600_log_likelihood(10.0) + timing_log_likelihood + 0.25_f64.ln());
        handoff
            .outcome_mass
            .no_exhaustion_by_bound
            .posterior_normalized_mass = 0.0;
        handoff.outcome_mass.impact.posterior_normalized_mass = 1.0;
        handoff.validate().unwrap();

        handoff.evidence.entries[3].disposition = EvidenceDispositionV2::Diagnostic;
        assert_eq!(
            handoff.validate(),
            Err(BroadImpactHandoffError::InvalidEvidence)
        );
    }
}
