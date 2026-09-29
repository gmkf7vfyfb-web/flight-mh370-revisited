use std::{
    collections::{BTreeMap, BTreeSet},
    error::Error,
    fmt,
};

use mh370_domain::LatLon;
use mh370_estimator::PosteriorParticleIdentity;
use serde::{Deserialize, Serialize};

pub(crate) const IMPACT_POSTERIOR_HANDOFF_SCHEMA_ID: &str = "mh370-impact-posterior-handoff";
pub(crate) const IMPACT_POSTERIOR_HANDOFF_SCHEMA_VERSION: u32 = 1;

const NORMALIZED_LOG_WEIGHT_TOLERANCE: f64 = 1.0e-10;
const PHYSICAL_RELATIVE_TOLERANCE: f64 = 1.0e-8;
const CONDITIONING_LABEL: &str = "transition_termination=impact";

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub(crate) struct ImpactPosteriorHandoffV1 {
    pub schema_id: String,
    pub schema_version: u32,
    pub time_basis: AbsoluteTimeBasisV1,
    pub run: ImpactRunProvenanceV1,
    pub source_runs: Vec<SourceRunRefV1>,
    pub scenario_combination: ScenarioCombinationV1,
    pub eof_scenarios: Vec<EofScenarioV1>,
    pub evidence: EvidenceLedgerV2,
    pub impact_conditioning: ImpactConditioningV1,
    pub particles: Vec<ImpactPosteriorParticleV1>,
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub(crate) struct AbsoluteTimeBasisV1 {
    pub scale: String,
    pub epoch: String,
    pub unit: String,
    pub convention: String,
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub(crate) struct ImpactRunProvenanceV1 {
    pub hypothesis_id: String,
    pub run_identity_sha256: String,
    pub producer_executable_sha256: String,
    pub config_sha256: String,
    pub input_sha256: BTreeMap<String, String>,
    pub code_revision: String,
    pub eof_seed: u64,
    /// Identity of the sidecar containing full transition inputs, terminal
    /// systems, events, and termination records. Those histories deliberately
    /// do not appear on every impact particle.
    pub transition_sidecar_sha256: String,
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub(crate) struct SourceRunRefV1 {
    pub id: String,
    pub model_family: String,
    pub seed: u64,
    /// Schema v1 carries one numerical seed per handoff, so this is zero.
    /// Pooling seeds belongs in suite/report composition and must not silently
    /// turn numerical replicates into a probabilistic mixture.
    pub pool_log_weight: f64,
    pub posterior_handoff_sha256: String,
    pub upstream_run_identity_sha256: String,
    pub upstream_config_sha256: String,
    pub upstream_input_sha256: BTreeMap<String, String>,
    /// POSIX UTC seconds corresponding to zero on the upstream relative time
    /// axis. The builder must derive this from explicit UTC-labelled input.
    pub relative_time_origin_unix_s_utc: f64,
    /// Absolute UTC time of the exported upstream checkpoint. Every impact
    /// represented by this source must occur at or after this instant.
    pub source_checkpoint_time_unix_s_utc: f64,
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
#[serde(tag = "kind", rename_all = "snake_case")]
pub(crate) enum ScenarioCombinationV1 {
    Separate,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub(crate) enum ControlTransitionTriggerV1 {
    DualEngineFlameout,
    DualEngineGeneratorLoss,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(tag = "kind", rename_all = "snake_case")]
pub(crate) enum EofControlPolicyFamilyV1 {
    Controlled,
    Uncontrolled,
    ControlledToUncontrolled { trigger: ControlTransitionTriggerV1 },
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub(crate) enum RestartTransientFamilyV1 {
    NoAdditionalTransient,
    CommonOcxoWarmup,
    R1200ChannelSettling,
    UnspecifiedRestartTransient,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
pub(crate) struct ConditionalModelFamilyV1 {
    pub control_policy: EofControlPolicyFamilyV1,
    pub restart_transient: RestartTransientFamilyV1,
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub(crate) struct EofScenarioV1 {
    pub id: String,
    pub family: ConditionalModelFamilyV1,
    pub log_weight: f64,
    pub config_sha256: String,
}

/// Evidence identity describes the underlying observation, never the model
/// used to score it. Open identifiers allow later evidence spokes without a
/// schema change.
#[derive(Debug, Clone, PartialEq, Eq, PartialOrd, Ord, Serialize, Deserialize)]
pub(crate) struct EvidenceIdentityV2 {
    pub dataset_id: String,
    pub observation_id: String,
    pub component_id: String,
    pub channel_id: Option<String>,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub(crate) enum EvidenceDispositionV2 {
    Consumed,
    HeldOut,
    Diagnostic,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub(crate) enum EvidenceApplicationRoleV1 {
    EmbeddedUpstream,
    WeightUpdate,
    Diagnostic,
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub(crate) struct EvidenceEntryV2 {
    pub identity: EvidenceIdentityV2,
    /// Components derived from one selected event or dependent observation set
    /// share this identifier and may be consumed only by one application.
    pub dependence_group_id: String,
    pub disposition: EvidenceDispositionV2,
    pub application_id: Option<String>,
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub(crate) struct EvidenceApplicationV1 {
    pub id: String,
    pub role: EvidenceApplicationRoleV1,
    pub model_family: String,
    pub config_sha256: String,
    pub input_sha256: BTreeMap<String, String>,
    /// Marginal log evidence for this atomic weight update. Required for a
    /// weight update and forbidden for embedded or diagnostic applications.
    pub log_evidence_increment: Option<f64>,
}

#[derive(Debug, Clone, Default, PartialEq, Serialize, Deserialize)]
pub(crate) struct EvidenceLedgerV2 {
    pub entries: Vec<EvidenceEntryV2>,
    pub applications: Vec<EvidenceApplicationV1>,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub(crate) enum TransitionTerminationV1 {
    Impact,
    MaximumDuration,
    MaximumSteps,
    AirspeedBelowMinimum,
    AirspeedAboveMaximum,
    NearVerticalFlightPath,
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub(crate) struct OutcomeWeightMassV1 {
    pub termination: TransitionTerminationV1,
    pub normalized_mass: f64,
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub(crate) struct ImpactConditioningV1 {
    pub conditioned_on: String,
    pub outcome_weight_mass: Vec<OutcomeWeightMassV1>,
}

#[derive(Debug, Clone, PartialEq, Eq, PartialOrd, Ord, Serialize, Deserialize)]
pub(crate) struct ImpactParticleIdentityV1 {
    pub source_run_id: String,
    pub upstream: PosteriorParticleIdentity,
    pub eof_scenario_id: String,
    pub eof_draw_id: u32,
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub(crate) struct ParticleLikelihoodTermV1 {
    pub application_id: String,
    pub log_likelihood: f64,
}

#[derive(Debug, Clone, Copy, PartialEq, Serialize, Deserialize)]
pub(crate) struct EnuVelocityV1 {
    pub east: f64,
    pub north: f64,
    /// Positive upward.
    pub up: f64,
}

#[derive(Debug, Clone, Copy, PartialEq, Serialize, Deserialize)]
pub(crate) struct ImpactKinematicsV1 {
    pub time_utc_unix_s: f64,
    pub position_wgs84: LatLon,
    pub true_airspeed_m_s: f64,
    pub ground_velocity_enu_m_s: EnuVelocityV1,
    pub displacement_from_last_contact_nm: f64,
}

#[derive(Debug, Clone, Copy, PartialEq, Serialize, Deserialize)]
pub(crate) struct ImpactEnergyV1 {
    pub total_j: f64,
    pub horizontal_j: f64,
    pub vertical_j: f64,
}

#[derive(Debug, Clone, Copy, PartialEq, Serialize, Deserialize)]
pub(crate) struct AngularIntervalV1 {
    pub center_deg: f64,
    pub half_width_deg: f64,
}

#[derive(Debug, Clone, Copy, PartialEq, Serialize, Deserialize)]
pub(crate) struct ImpactAttitudeIntervalsV1 {
    pub pitch_nose_up_deg: AngularIntervalV1,
    pub roll_right_wing_down_deg: AngularIntervalV1,
    pub yaw_true_deg: AngularIntervalV1,
}

#[derive(Debug, Clone, Copy, PartialEq, Serialize, Deserialize)]
pub(crate) struct PositiveIntervalV1 {
    pub minimum: f64,
    pub maximum: f64,
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub(crate) struct ImpactPosteriorParticleV1 {
    pub identity: ImpactParticleIdentityV1,
    /// Copied bit-for-bit from the parent handoff identified by the source
    /// hash. The builder must cross-check it there. Impact survivors are a
    /// subset, so their distinct upstream weights need not normalize to one.
    pub upstream_normalized_log_weight: f64,
    pub eof_draw_log_weight: f64,
    pub likelihood_terms: Vec<ParticleLikelihoodTermV1>,
    pub normalized_log_weight: f64,
    /// Physical aircraft mass at transition termination, not probability mass.
    pub termination_mass_kg: f64,
    pub kinematics: ImpactKinematicsV1,
    pub energy: ImpactEnergyV1,
    /// None means unresolved; it must never be interpreted as level attitude.
    pub attitude: Option<ImpactAttitudeIntervalsV1>,
    /// None means unresolved; downstream source models must not invent a
    /// nominal contact duration without an explicit conditional family.
    pub contact_duration_s: Option<PositiveIntervalV1>,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub(crate) enum ImpactHandoffError {
    UnsupportedSchema,
    InvalidTimeBasis,
    InvalidProvenance,
    InvalidSource,
    InvalidScenario,
    InvalidEvidence,
    InvalidConditioning,
    InvalidParticle,
    InvalidPhysicalState,
    UnnormalizedWeights(&'static str),
    InconsistentImpactOutcomeMass,
    HiddenWeight,
}

impl fmt::Display for ImpactHandoffError {
    fn fmt(&self, formatter: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            Self::UnsupportedSchema => write!(formatter, "unsupported impact handoff schema"),
            Self::InvalidTimeBasis => write!(formatter, "invalid absolute UTC time basis"),
            Self::InvalidProvenance => write!(formatter, "invalid impact handoff provenance"),
            Self::InvalidSource => write!(formatter, "invalid upstream source reference"),
            Self::InvalidScenario => write!(formatter, "invalid end-of-flight scenario"),
            Self::InvalidEvidence => write!(formatter, "invalid evidence ledger"),
            Self::InvalidConditioning => write!(formatter, "invalid impact conditioning"),
            Self::InvalidParticle => write!(formatter, "invalid impact particle"),
            Self::InvalidPhysicalState => write!(formatter, "invalid impact physical state"),
            Self::UnnormalizedWeights(scope) => {
                write!(formatter, "unnormalized {scope} log weights")
            }
            Self::InconsistentImpactOutcomeMass => {
                write!(
                    formatter,
                    "represented impact weights disagree with outcome mass"
                )
            }
            Self::HiddenWeight => write!(formatter, "particle weight contains a hidden term"),
        }
    }
}

impl Error for ImpactHandoffError {}

impl ImpactPosteriorHandoffV1 {
    pub(crate) fn validate(&self) -> Result<(), ImpactHandoffError> {
        self.validate_header()?;
        let sources = self.validate_sources()?;
        let scenarios = self.validate_scenarios()?;
        let applications = self.evidence.validate()?;
        let impact_outcome_mass = self.impact_conditioning.validate()?;
        self.validate_particles(&sources, &scenarios, &applications, impact_outcome_mass)
    }

    fn validate_header(&self) -> Result<(), ImpactHandoffError> {
        if self.schema_id != IMPACT_POSTERIOR_HANDOFF_SCHEMA_ID
            || self.schema_version != IMPACT_POSTERIOR_HANDOFF_SCHEMA_VERSION
        {
            return Err(ImpactHandoffError::UnsupportedSchema);
        }
        if self.time_basis.scale != "utc"
            || self.time_basis.epoch != "1970-01-01T00:00:00Z"
            || self.time_basis.unit != "second"
            || self.time_basis.convention != "posix_seconds_no_leap_representation"
        {
            return Err(ImpactHandoffError::InvalidTimeBasis);
        }
        if !valid_identifier(&self.run.hypothesis_id)
            || !valid_sha256(&self.run.run_identity_sha256)
            || !valid_sha256(&self.run.producer_executable_sha256)
            || !valid_sha256(&self.run.config_sha256)
            || !valid_sha256(&self.run.transition_sidecar_sha256)
            || self.run.code_revision.trim().is_empty()
            || !valid_hash_map(&self.run.input_sha256)
        {
            return Err(ImpactHandoffError::InvalidProvenance);
        }
        Ok(())
    }

    fn validate_sources(&self) -> Result<BTreeMap<&str, &SourceRunRefV1>, ImpactHandoffError> {
        if self.source_runs.len() != 1 {
            return Err(ImpactHandoffError::InvalidSource);
        }
        let mut sources = BTreeMap::new();
        for source in &self.source_runs {
            if !valid_identifier(&source.id)
                || !valid_identifier(&source.model_family)
                || !source.pool_log_weight.is_finite()
                || source.pool_log_weight.abs() > NORMALIZED_LOG_WEIGHT_TOLERANCE
                || !valid_sha256(&source.posterior_handoff_sha256)
                || !valid_sha256(&source.upstream_run_identity_sha256)
                || !valid_sha256(&source.upstream_config_sha256)
                || !valid_hash_map(&source.upstream_input_sha256)
                || !source.relative_time_origin_unix_s_utc.is_finite()
                || source.relative_time_origin_unix_s_utc <= 0.0
                || !source.source_checkpoint_time_unix_s_utc.is_finite()
                || source.source_checkpoint_time_unix_s_utc < source.relative_time_origin_unix_s_utc
                || sources.insert(source.id.as_str(), source).is_some()
            {
                return Err(ImpactHandoffError::InvalidSource);
            }
        }
        require_normalized(
            self.source_runs.iter().map(|source| source.pool_log_weight),
            "source-pool",
        )?;
        Ok(sources)
    }

    fn validate_scenarios(&self) -> Result<BTreeMap<&str, &EofScenarioV1>, ImpactHandoffError> {
        if self.eof_scenarios.is_empty() {
            return Err(ImpactHandoffError::InvalidScenario);
        }
        let mut scenarios = BTreeMap::new();
        for scenario in &self.eof_scenarios {
            if !valid_identifier(&scenario.id)
                || !scenario.log_weight.is_finite()
                || scenario.log_weight > NORMALIZED_LOG_WEIGHT_TOLERANCE
                || !valid_sha256(&scenario.config_sha256)
                || scenarios.insert(scenario.id.as_str(), scenario).is_some()
            {
                return Err(ImpactHandoffError::InvalidScenario);
            }
        }
        if self.eof_scenarios.len() != 1
            || self.eof_scenarios[0].log_weight.abs() > NORMALIZED_LOG_WEIGHT_TOLERANCE
        {
            return Err(ImpactHandoffError::InvalidScenario);
        }
        Ok(scenarios)
    }

    fn validate_particles(
        &self,
        sources: &BTreeMap<&str, &SourceRunRefV1>,
        scenarios: &BTreeMap<&str, &EofScenarioV1>,
        applications: &BTreeMap<&str, &EvidenceApplicationV1>,
        impact_outcome_mass: f64,
    ) -> Result<(), ImpactHandoffError> {
        if self.particles.is_empty() {
            return Err(ImpactHandoffError::InvalidParticle);
        }
        let weight_update_ids = applications
            .values()
            .filter(|application| application.role == EvidenceApplicationRoleV1::WeightUpdate)
            .map(|application| application.id.as_str())
            .collect::<BTreeSet<_>>();
        let mut identities = BTreeSet::new();
        let mut used_sources = BTreeSet::new();
        let mut used_scenarios = BTreeSet::new();
        let mut upstream_weights = BTreeMap::new();
        let mut raw_weights = Vec::with_capacity(self.particles.len());

        for particle in &self.particles {
            if !identities.insert(&particle.identity) {
                return Err(ImpactHandoffError::InvalidParticle);
            }
            let source = sources
                .get(particle.identity.source_run_id.as_str())
                .ok_or(ImpactHandoffError::InvalidParticle)?;
            let scenario = scenarios
                .get(particle.identity.eof_scenario_id.as_str())
                .ok_or(ImpactHandoffError::InvalidParticle)?;
            if particle.identity.upstream.model_family != source.model_family
                || particle.identity.upstream.seed != source.seed
                || !particle.upstream_normalized_log_weight.is_finite()
                || particle.upstream_normalized_log_weight > NORMALIZED_LOG_WEIGHT_TOLERANCE
                || !particle.eof_draw_log_weight.is_finite()
                || !particle.normalized_log_weight.is_finite()
                || particle.normalized_log_weight > NORMALIZED_LOG_WEIGHT_TOLERANCE
            {
                return Err(ImpactHandoffError::InvalidParticle);
            }

            used_sources.insert(source.id.as_str());
            used_scenarios.insert(scenario.id.as_str());
            let upstream_key = (source.id.clone(), particle.identity.upstream.clone());
            if let Some(previous) =
                upstream_weights.insert(upstream_key, particle.upstream_normalized_log_weight)
            {
                if previous.to_bits() != particle.upstream_normalized_log_weight.to_bits() {
                    return Err(ImpactHandoffError::InvalidParticle);
                }
            }

            particle.validate_physics(source.source_checkpoint_time_unix_s_utc)?;
            let term_sum = particle.validate_likelihood_terms(applications, &weight_update_ids)?;
            raw_weights.push(
                source.pool_log_weight
                    + particle.upstream_normalized_log_weight
                    + scenario.log_weight
                    + particle.eof_draw_log_weight
                    + term_sum,
            );
        }

        if used_sources.len() != sources.len() || used_scenarios.len() != scenarios.len() {
            return Err(ImpactHandoffError::InvalidParticle);
        }
        let evidence_log_increment = applications
            .values()
            .filter_map(|application| {
                match (application.role, application.log_evidence_increment) {
                    (EvidenceApplicationRoleV1::WeightUpdate, Some(value)) => Some(value),
                    _ => None,
                }
            })
            .sum::<f64>();
        let target_log_mass = evidence_log_increment + impact_outcome_mass.ln();
        let represented_log_mass = log_sum_exp(raw_weights.iter().copied())
            .ok_or(ImpactHandoffError::InconsistentImpactOutcomeMass)?;
        if !close(
            represented_log_mass,
            target_log_mass,
            NORMALIZED_LOG_WEIGHT_TOLERANCE,
        ) {
            return Err(ImpactHandoffError::InconsistentImpactOutcomeMass);
        }
        require_normalized(
            self.particles
                .iter()
                .map(|particle| particle.normalized_log_weight),
            "impact-particle",
        )?;

        let expected_shift = -target_log_mass;
        let reference_shift = self.particles[0].normalized_log_weight - raw_weights[0];
        if !close(
            reference_shift,
            expected_shift,
            NORMALIZED_LOG_WEIGHT_TOLERANCE,
        ) || self
            .particles
            .iter()
            .zip(raw_weights.iter().copied())
            .any(|(particle, raw)| {
                !close(
                    particle.normalized_log_weight - raw,
                    reference_shift,
                    NORMALIZED_LOG_WEIGHT_TOLERANCE,
                )
            })
        {
            return Err(ImpactHandoffError::HiddenWeight);
        }
        Ok(())
    }
}

impl EvidenceLedgerV2 {
    pub(crate) fn validate(
        &self,
    ) -> Result<BTreeMap<&str, &EvidenceApplicationV1>, ImpactHandoffError> {
        let mut applications = BTreeMap::new();
        for application in &self.applications {
            if !valid_identifier(&application.id)
                || !valid_identifier(&application.model_family)
                || !valid_sha256(&application.config_sha256)
                || !valid_hash_map(&application.input_sha256)
                || !match (application.role, application.log_evidence_increment) {
                    (EvidenceApplicationRoleV1::WeightUpdate, Some(value)) => value.is_finite(),
                    (
                        EvidenceApplicationRoleV1::EmbeddedUpstream
                        | EvidenceApplicationRoleV1::Diagnostic,
                        None,
                    ) => true,
                    _ => false,
                }
                || applications
                    .insert(application.id.as_str(), application)
                    .is_some()
            {
                return Err(ImpactHandoffError::InvalidEvidence);
            }
        }

        let mut identities = BTreeSet::new();
        let mut dependence_consumers = BTreeMap::<String, String>::new();
        let mut application_use = BTreeMap::<String, usize>::new();
        for entry in &self.entries {
            if !entry.identity.validate()
                || !valid_identifier(&entry.dependence_group_id)
                || !identities.insert(&entry.identity)
            {
                return Err(ImpactHandoffError::InvalidEvidence);
            }
            let application = match entry.application_id.as_deref() {
                Some(id) => {
                    if !valid_identifier(id) {
                        return Err(ImpactHandoffError::InvalidEvidence);
                    }
                    let application = applications
                        .get(id)
                        .copied()
                        .ok_or(ImpactHandoffError::InvalidEvidence)?;
                    *application_use.entry(id.to_string()).or_default() += 1;
                    Some(application)
                }
                None => None,
            };
            match (entry.disposition, application.map(|value| value.role)) {
                (
                    EvidenceDispositionV2::Consumed,
                    Some(EvidenceApplicationRoleV1::EmbeddedUpstream),
                )
                | (
                    EvidenceDispositionV2::Consumed,
                    Some(EvidenceApplicationRoleV1::WeightUpdate),
                )
                | (EvidenceDispositionV2::HeldOut, None)
                | (
                    EvidenceDispositionV2::Diagnostic,
                    Some(EvidenceApplicationRoleV1::Diagnostic),
                ) => {}
                _ => return Err(ImpactHandoffError::InvalidEvidence),
            }
            if entry.disposition == EvidenceDispositionV2::Consumed {
                let consumer = entry
                    .application_id
                    .as_ref()
                    .ok_or(ImpactHandoffError::InvalidEvidence)?;
                if let Some(previous) =
                    dependence_consumers.insert(entry.dependence_group_id.clone(), consumer.clone())
                {
                    if previous != *consumer {
                        return Err(ImpactHandoffError::InvalidEvidence);
                    }
                }
            }
        }
        if self
            .applications
            .iter()
            .any(|application| !application_use.contains_key(&application.id))
        {
            return Err(ImpactHandoffError::InvalidEvidence);
        }
        Ok(applications)
    }
}

impl EvidenceIdentityV2 {
    fn validate(&self) -> bool {
        valid_identifier(&self.dataset_id)
            && valid_identifier(&self.observation_id)
            && valid_identifier(&self.component_id)
            && match self.channel_id.as_deref() {
                Some(channel_id) => valid_identifier(channel_id),
                None => true,
            }
    }
}

impl ImpactConditioningV1 {
    fn validate(&self) -> Result<f64, ImpactHandoffError> {
        if self.conditioned_on != CONDITIONING_LABEL || self.outcome_weight_mass.is_empty() {
            return Err(ImpactHandoffError::InvalidConditioning);
        }
        let mut terminations = BTreeSet::new();
        let mut total = 0.0;
        let mut impact_mass = None;
        for outcome in &self.outcome_weight_mass {
            if !outcome.normalized_mass.is_finite()
                || !(0.0..=1.0).contains(&outcome.normalized_mass)
                || !terminations.insert(outcome.termination)
            {
                return Err(ImpactHandoffError::InvalidConditioning);
            }
            total += outcome.normalized_mass;
            if outcome.termination == TransitionTerminationV1::Impact {
                impact_mass = Some(outcome.normalized_mass);
            }
        }
        let impact_mass = impact_mass
            .filter(|mass| *mass > 0.0)
            .ok_or(ImpactHandoffError::InvalidConditioning)?;
        if !close(total, 1.0, NORMALIZED_LOG_WEIGHT_TOLERANCE) {
            return Err(ImpactHandoffError::InvalidConditioning);
        }
        Ok(impact_mass)
    }
}

impl ImpactPosteriorParticleV1 {
    fn validate_likelihood_terms(
        &self,
        applications: &BTreeMap<&str, &EvidenceApplicationV1>,
        required_weight_updates: &BTreeSet<&str>,
    ) -> Result<f64, ImpactHandoffError> {
        let mut seen = BTreeSet::new();
        let mut sum = 0.0;
        for term in &self.likelihood_terms {
            if !valid_identifier(&term.application_id)
                || !term.log_likelihood.is_finite()
                || !seen.insert(term.application_id.as_str())
                || match applications.get(term.application_id.as_str()) {
                    Some(application) => {
                        application.role != EvidenceApplicationRoleV1::WeightUpdate
                    }
                    None => true,
                }
            {
                return Err(ImpactHandoffError::InvalidEvidence);
            }
            sum += term.log_likelihood;
        }
        if &seen != required_weight_updates {
            return Err(ImpactHandoffError::InvalidEvidence);
        }
        Ok(sum)
    }

    fn validate_physics(&self, source_checkpoint_time: f64) -> Result<(), ImpactHandoffError> {
        let state = self.kinematics;
        let velocity = state.ground_velocity_enu_m_s;
        if !state.time_utc_unix_s.is_finite()
            || state.time_utc_unix_s < source_checkpoint_time
            || !valid_position(state.position_wgs84)
            || !state.true_airspeed_m_s.is_finite()
            || state.true_airspeed_m_s <= 0.0
            || !velocity.east.is_finite()
            || !velocity.north.is_finite()
            || !velocity.up.is_finite()
            || velocity.east.hypot(velocity.north) <= 0.0
            || !state.displacement_from_last_contact_nm.is_finite()
            || state.displacement_from_last_contact_nm < 0.0
            || !self.termination_mass_kg.is_finite()
            || self.termination_mass_kg <= 0.0
        {
            return Err(ImpactHandoffError::InvalidPhysicalState);
        }

        let expected_horizontal =
            0.5 * self.termination_mass_kg * (velocity.east.powi(2) + velocity.north.powi(2));
        let expected_vertical = 0.5 * self.termination_mass_kg * velocity.up.powi(2);
        if !self.energy.total_j.is_finite()
            || !self.energy.horizontal_j.is_finite()
            || !self.energy.vertical_j.is_finite()
            || self.energy.total_j < 0.0
            || self.energy.horizontal_j < 0.0
            || self.energy.vertical_j < 0.0
            || !close(
                self.energy.horizontal_j,
                expected_horizontal,
                PHYSICAL_RELATIVE_TOLERANCE,
            )
            || !close(
                self.energy.vertical_j,
                expected_vertical,
                PHYSICAL_RELATIVE_TOLERANCE,
            )
            || !close(
                self.energy.total_j,
                self.energy.horizontal_j + self.energy.vertical_j,
                PHYSICAL_RELATIVE_TOLERANCE,
            )
        {
            return Err(ImpactHandoffError::InvalidPhysicalState);
        }

        if self.attitude.is_some() || self.contact_duration_s.is_some() {
            return Err(ImpactHandoffError::InvalidPhysicalState);
        }
        Ok(())
    }
}

fn valid_position(position: LatLon) -> bool {
    position.latitude.is_finite()
        && (-90.0..=90.0).contains(&position.latitude.0)
        && position.longitude.is_finite()
        && (-180.0..180.0).contains(&position.longitude.0)
}

fn valid_identifier(value: &str) -> bool {
    let mut bytes = value.bytes();
    bytes
        .next()
        .is_some_and(|byte| byte.is_ascii_alphanumeric())
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
            .all(|(identity, digest)| !identity.trim().is_empty() && valid_sha256(digest))
}

fn log_sum_exp(values: impl Iterator<Item = f64>) -> Option<f64> {
    let values = values.collect::<Vec<_>>();
    if values.is_empty() || values.iter().any(|value| !value.is_finite()) {
        return None;
    }
    let maximum = values.iter().copied().fold(f64::NEG_INFINITY, f64::max);
    let log_sum = maximum
        + values
            .iter()
            .map(|value| (value - maximum).exp())
            .sum::<f64>()
            .ln();
    log_sum.is_finite().then_some(log_sum)
}

fn require_normalized(
    values: impl Iterator<Item = f64>,
    scope: &'static str,
) -> Result<(), ImpactHandoffError> {
    let values = values.collect::<Vec<_>>();
    if values.is_empty() || values.iter().any(|value| !value.is_finite()) {
        return Err(ImpactHandoffError::UnnormalizedWeights(scope));
    }
    let maximum = values.iter().copied().fold(f64::NEG_INFINITY, f64::max);
    let log_sum = maximum
        + values
            .iter()
            .map(|value| (value - maximum).exp())
            .sum::<f64>()
            .ln();
    if !log_sum.is_finite() || log_sum.abs() > NORMALIZED_LOG_WEIGHT_TOLERANCE {
        return Err(ImpactHandoffError::UnnormalizedWeights(scope));
    }
    Ok(())
}

fn close(first: f64, second: f64, relative_tolerance: f64) -> bool {
    (first - second).abs() <= relative_tolerance * first.abs().max(second.abs()).max(1.0)
}

#[cfg(test)]
mod tests {
    use super::*;

    fn digest(byte: char) -> String {
        std::iter::repeat_n(byte, 64).collect()
    }

    fn hash_map(label: &str, byte: char) -> BTreeMap<String, String> {
        BTreeMap::from([(label.to_string(), digest(byte))])
    }

    fn embedded_application(id: &str, byte: char) -> EvidenceApplicationV1 {
        EvidenceApplicationV1 {
            id: id.to_string(),
            role: EvidenceApplicationRoleV1::EmbeddedUpstream,
            model_family: "through-0011-medium".to_string(),
            config_sha256: digest(byte),
            input_sha256: hash_map("observations", byte),
            log_evidence_increment: None,
        }
    }

    fn particle(
        index: usize,
        scenario: &str,
        normalized_log_weight: f64,
    ) -> ImpactPosteriorParticleV1 {
        let mass = 1_000.0;
        let east: f64 = 100.0;
        let north: f64 = 0.0;
        let up: f64 = -10.0;
        let horizontal = 0.5 * mass * (east.powi(2) + north.powi(2));
        let vertical = 0.5 * mass * up.powi(2);
        ImpactPosteriorParticleV1 {
            identity: ImpactParticleIdentityV1 {
                source_run_id: "source-seed-7".to_string(),
                upstream: PosteriorParticleIdentity {
                    model_family: "through-0011-medium".to_string(),
                    seed: 7,
                    particle: index,
                },
                eof_scenario_id: scenario.to_string(),
                eof_draw_id: 0,
            },
            upstream_normalized_log_weight: -(2.0_f64).ln(),
            eof_draw_log_weight: 0.0,
            likelihood_terms: Vec::new(),
            normalized_log_weight,
            termination_mass_kg: mass,
            kinematics: ImpactKinematicsV1 {
                time_utc_unix_s: 1_394_234_400.0 + index as f64,
                position_wgs84: LatLon::new(-35.0 - index as f64 * 0.1, 92.0).unwrap(),
                true_airspeed_m_s: 101.0,
                ground_velocity_enu_m_s: EnuVelocityV1 { east, north, up },
                displacement_from_last_contact_nm: 5.0,
            },
            energy: ImpactEnergyV1 {
                total_j: horizontal + vertical,
                horizontal_j: horizontal,
                vertical_j: vertical,
            },
            attitude: None,
            contact_duration_s: None,
        }
    }

    fn handoff() -> ImpactPosteriorHandoffV1 {
        let half = -(2.0_f64).ln();
        ImpactPosteriorHandoffV1 {
            schema_id: IMPACT_POSTERIOR_HANDOFF_SCHEMA_ID.to_string(),
            schema_version: IMPACT_POSTERIOR_HANDOFF_SCHEMA_VERSION,
            time_basis: AbsoluteTimeBasisV1 {
                scale: "utc".to_string(),
                epoch: "1970-01-01T00:00:00Z".to_string(),
                unit: "second".to_string(),
                convention: "posix_seconds_no_leap_representation".to_string(),
            },
            run: ImpactRunProvenanceV1 {
                hypothesis_id: "baseline-eof".to_string(),
                run_identity_sha256: digest('a'),
                producer_executable_sha256: digest('b'),
                config_sha256: digest('c'),
                input_sha256: hash_map("eof-config", 'd'),
                code_revision: "0123456789abcdef".to_string(),
                eof_seed: 370_029,
                transition_sidecar_sha256: digest('e'),
            },
            source_runs: vec![SourceRunRefV1 {
                id: "source-seed-7".to_string(),
                model_family: "through-0011-medium".to_string(),
                seed: 7,
                pool_log_weight: 0.0,
                posterior_handoff_sha256: digest('f'),
                upstream_run_identity_sha256: digest('1'),
                upstream_config_sha256: digest('2'),
                upstream_input_sha256: hash_map("satcom", '3'),
                relative_time_origin_unix_s_utc: 1_394_215_309.0,
                source_checkpoint_time_unix_s_utc: 1_394_233_000.0,
            }],
            scenario_combination: ScenarioCombinationV1::Separate,
            eof_scenarios: vec![EofScenarioV1 {
                id: "uncontrolled-no-transient".to_string(),
                family: ConditionalModelFamilyV1 {
                    control_policy: EofControlPolicyFamilyV1::Uncontrolled,
                    restart_transient: RestartTransientFamilyV1::NoAdditionalTransient,
                },
                log_weight: 0.0,
                config_sha256: digest('4'),
            }],
            evidence: EvidenceLedgerV2 {
                entries: vec![EvidenceEntryV2 {
                    identity: EvidenceIdentityV2 {
                        dataset_id: "satcom-log-2014-03-08".to_string(),
                        observation_id: "m0011".to_string(),
                        component_id: "bto".to_string(),
                        channel_id: Some("r1200".to_string()),
                    },
                    dependence_group_id: "satcom-m0011".to_string(),
                    disposition: EvidenceDispositionV2::Consumed,
                    application_id: Some("satcom-core".to_string()),
                }],
                applications: vec![embedded_application("satcom-core", '5')],
            },
            impact_conditioning: ImpactConditioningV1 {
                conditioned_on: CONDITIONING_LABEL.to_string(),
                outcome_weight_mass: vec![OutcomeWeightMassV1 {
                    termination: TransitionTerminationV1::Impact,
                    normalized_mass: 1.0,
                }],
            },
            particles: vec![
                particle(0, "uncontrolled-no-transient", half),
                particle(1, "uncontrolled-no-transient", half),
            ],
        }
    }

    #[test]
    fn serde_round_trip_is_exact() {
        let handoff = handoff();
        handoff.validate().unwrap();
        let first = serde_json::to_vec_pretty(&handoff).unwrap();
        let decoded: ImpactPosteriorHandoffV1 = serde_json::from_slice(&first).unwrap();
        let second = serde_json::to_vec_pretty(&decoded).unwrap();
        assert_eq!(decoded, handoff);
        assert_eq!(second, first);
    }

    #[test]
    fn v1_requires_one_scenario_and_unresolved_attitude_and_contact_duration() {
        let mut handoff = handoff();
        assert!(handoff
            .particles
            .iter()
            .all(|particle| particle.attitude.is_none() && particle.contact_duration_s.is_none()));
        handoff.validate().unwrap();

        handoff.particles[0].contact_duration_s = Some(PositiveIntervalV1 {
            minimum: 0.1,
            maximum: 1.0,
        });
        assert_eq!(
            handoff.validate(),
            Err(ImpactHandoffError::InvalidPhysicalState)
        );

        handoff.particles[0].contact_duration_s = None;
        handoff.particles[0].attitude = Some(ImpactAttitudeIntervalsV1 {
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
            handoff.validate(),
            Err(ImpactHandoffError::InvalidPhysicalState)
        );
    }

    #[test]
    fn rejects_inconsistent_energy_and_particle_normalization() {
        let mut invalid_energy = handoff();
        invalid_energy.particles[0].energy.total_j += 1_000.0;
        assert_eq!(
            invalid_energy.validate(),
            Err(ImpactHandoffError::InvalidPhysicalState)
        );

        let mut invalid_weights = handoff();
        invalid_weights.particles[0].normalized_log_weight += 0.1;
        assert!(matches!(
            invalid_weights.validate(),
            Err(ImpactHandoffError::UnnormalizedWeights("impact-particle"))
                | Err(ImpactHandoffError::HiddenWeight)
        ));
    }

    #[test]
    fn separate_handoff_rejects_a_second_scenario() {
        let mut handoff = handoff();
        handoff.eof_scenarios.push(EofScenarioV1 {
            id: "controlled-common-ocxo".to_string(),
            family: ConditionalModelFamilyV1 {
                control_policy: EofControlPolicyFamilyV1::Controlled,
                restart_transient: RestartTransientFamilyV1::CommonOcxoWarmup,
            },
            log_weight: 0.0,
            config_sha256: digest('6'),
        });
        assert_eq!(handoff.validate(), Err(ImpactHandoffError::InvalidScenario));
    }

    #[test]
    fn rejects_duplicate_evidence_identity_and_dependence_group_consumption() {
        let mut duplicate_identity = handoff();
        duplicate_identity
            .evidence
            .entries
            .push(duplicate_identity.evidence.entries[0].clone());
        assert_eq!(
            duplicate_identity.validate(),
            Err(ImpactHandoffError::InvalidEvidence)
        );

        let mut duplicate_group = handoff();
        duplicate_group
            .evidence
            .applications
            .push(embedded_application("second-model", '6'));
        duplicate_group.evidence.entries.push(EvidenceEntryV2 {
            identity: EvidenceIdentityV2 {
                dataset_id: "satcom-log-2014-03-08".to_string(),
                observation_id: "m0011".to_string(),
                component_id: "bfo".to_string(),
                channel_id: Some("r1200".to_string()),
            },
            dependence_group_id: "satcom-m0011".to_string(),
            disposition: EvidenceDispositionV2::Consumed,
            application_id: Some("second-model".to_string()),
        });
        assert_eq!(
            duplicate_group.validate(),
            Err(ImpactHandoffError::InvalidEvidence)
        );
    }
    fn half_impact_handoff() -> ImpactPosteriorHandoffV1 {
        let mut handoff = handoff();
        let quarter = -(4.0_f64).ln();
        for particle in &mut handoff.particles {
            particle.upstream_normalized_log_weight = quarter;
        }
        handoff.impact_conditioning.outcome_weight_mass = vec![
            OutcomeWeightMassV1 {
                termination: TransitionTerminationV1::Impact,
                normalized_mass: 0.5,
            },
            OutcomeWeightMassV1 {
                termination: TransitionTerminationV1::MaximumDuration,
                normalized_mass: 0.5,
            },
        ];
        handoff
    }

    #[test]
    fn half_impact_survivors_preserve_parent_weights() {
        half_impact_handoff().validate().unwrap();
    }

    #[test]
    fn rejects_inconsistent_impact_outcome_mass() {
        let mut handoff = half_impact_handoff();
        handoff.impact_conditioning.outcome_weight_mass[0].normalized_mass = 0.6;
        handoff.impact_conditioning.outcome_weight_mass[1].normalized_mass = 0.4;
        assert_eq!(
            handoff.validate(),
            Err(ImpactHandoffError::InconsistentImpactOutcomeMass)
        );
    }

    #[test]
    fn source_checkpoint_must_follow_origin_and_precede_impacts() {
        let mut checkpoint_before_origin = handoff();
        checkpoint_before_origin.source_runs[0].source_checkpoint_time_unix_s_utc =
            checkpoint_before_origin.source_runs[0].relative_time_origin_unix_s_utc - 1.0;
        assert_eq!(
            checkpoint_before_origin.validate(),
            Err(ImpactHandoffError::InvalidSource)
        );

        let mut impact_before_checkpoint = handoff();
        impact_before_checkpoint.source_runs[0].source_checkpoint_time_unix_s_utc =
            impact_before_checkpoint.particles[0]
                .kinematics
                .time_utc_unix_s
                + 0.5;
        assert_eq!(
            impact_before_checkpoint.validate(),
            Err(ImpactHandoffError::InvalidPhysicalState)
        );
    }

    #[test]
    fn v1_rejects_source_seed_pooling() {
        let mut pooled = handoff();
        let mut second = pooled.source_runs[0].clone();
        second.id = "source-seed-8".to_string();
        second.seed = 8;
        pooled.source_runs.push(second);
        assert_eq!(pooled.validate(), Err(ImpactHandoffError::InvalidSource));
    }

    #[test]
    fn controlled_to_uncontrolled_policy_has_typed_trigger_serde() {
        let policies = [
            (
                EofControlPolicyFamilyV1::ControlledToUncontrolled {
                    trigger: ControlTransitionTriggerV1::DualEngineFlameout,
                },
                "dual_engine_flameout",
            ),
            (
                EofControlPolicyFamilyV1::ControlledToUncontrolled {
                    trigger: ControlTransitionTriggerV1::DualEngineGeneratorLoss,
                },
                "dual_engine_generator_loss",
            ),
        ];
        for (policy, trigger) in policies {
            let encoded = serde_json::to_value(policy).unwrap();
            assert_eq!(encoded["kind"], "controlled_to_uncontrolled");
            assert_eq!(encoded["trigger"], trigger);
            let decoded: EofControlPolicyFamilyV1 = serde_json::from_value(encoded).unwrap();
            assert_eq!(decoded, policy);
        }
    }

    #[test]
    fn weight_update_discloses_evidence_normalizer() {
        let mut handoff = handoff();
        let log_half = -(2.0_f64).ln();
        handoff.evidence.applications.push(EvidenceApplicationV1 {
            id: "startup-power".to_string(),
            role: EvidenceApplicationRoleV1::WeightUpdate,
            model_family: "conditional-startup-power".to_string(),
            config_sha256: digest('7'),
            input_sha256: hash_map("startup-power", '8'),
            log_evidence_increment: Some(log_half),
        });
        handoff.evidence.entries.push(EvidenceEntryV2 {
            identity: EvidenceIdentityV2 {
                dataset_id: "satcom-log-2014-03-08".to_string(),
                observation_id: "m0019".to_string(),
                component_id: "received-power".to_string(),
                channel_id: Some("c-channel".to_string()),
            },
            dependence_group_id: "satcom-m0019-power".to_string(),
            disposition: EvidenceDispositionV2::Consumed,
            application_id: Some("startup-power".to_string()),
        });
        for particle in &mut handoff.particles {
            particle.likelihood_terms.push(ParticleLikelihoodTermV1 {
                application_id: "startup-power".to_string(),
                log_likelihood: log_half,
            });
        }
        handoff.validate().unwrap();

        handoff.evidence.applications[1].log_evidence_increment = None;
        assert_eq!(handoff.validate(), Err(ImpactHandoffError::InvalidEvidence));
    }

    #[test]
    fn positive_importance_correction_is_explicit_and_weight_neutral() {
        let mut handoff = handoff();
        let correction = 2.0_f64.ln();
        handoff.particles[0].upstream_normalized_log_weight = -(4.0_f64).ln();
        handoff.particles[0].eof_draw_log_weight = correction;
        handoff.validate().unwrap();

        handoff.particles[0].eof_draw_log_weight += 0.25;
        assert_eq!(
            handoff.validate(),
            Err(ImpactHandoffError::InconsistentImpactOutcomeMass)
        );
    }
}
