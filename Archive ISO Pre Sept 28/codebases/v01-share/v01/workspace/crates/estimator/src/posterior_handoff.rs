use std::collections::{BTreeMap, BTreeSet};

use mh370_domain::{AircraftState, Degrees, LatLon, NauticalMiles, Seconds};
use mh370_dynamics::LateralMode;
use mh370_satcom::BfoBiasState;
use serde::{Deserialize, Serialize};
use thiserror::Error;

pub const POSTERIOR_HANDOFF_SCHEMA_VERSION: u32 = 2;
const LEGACY_SCALAR_HANDOFF_SCHEMA_VERSION: u32 = 1;
const NORMALIZED_LOG_WEIGHT_TOLERANCE: f64 = 1e-10;

#[derive(Debug, Clone, PartialEq, Eq, PartialOrd, Ord, Serialize, Deserialize)]
pub struct PosteriorParticleIdentity {
    pub model_family: String,
    pub seed: u64,
    pub particle: usize,
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct PosteriorRunMetadata {
    pub model_family: String,
    pub seed: u64,
    /// Structural lateral mode is mandatory in schema v2. It is optional only
    /// while reading legacy schema-v1 scalar handoffs, whose particles still
    /// must all declare one identical scalar mode.
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub lateral_mode: Option<LateralMode>,
    /// SHA-256 identity of the completed upstream run used to make the handoff.
    pub run_identity_sha256: String,
    pub config_sha256: String,
    /// Input path or stable input identifier to its SHA-256 digest.
    pub input_sha256: BTreeMap<String, String>,
    /// Explicit fixed destination for a direct-to/LNAV structural family.
    ///
    /// This is run-level metadata because every particle in one structural
    /// family shares the same predeclared destination. Scalar-control families
    /// leave it absent.
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub fixed_waypoint: Option<FixedWaypointMetadata>,
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct FixedWaypointMetadata {
    pub target_name: String,
    pub position: LatLon,
    pub arrival_radius: NauticalMiles,
    pub coordinate_source_title: String,
    pub coordinate_source_uri: String,
    pub coordinate_frame_assumption: String,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub coordinate_source_date: Option<String>,
    pub coordinate_note: String,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum EvidenceComponent {
    Bto,
    Bfo,
    ReceivedPower,
    LogonRequestTime,
    LogonOccurrence,
}

#[derive(Debug, Clone, PartialEq, Eq, PartialOrd, Ord, Serialize, Deserialize)]
pub struct EvidenceIdentity {
    pub epoch_id: String,
    pub channel: Option<String>,
    pub component: EvidenceComponent,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum EvidenceDisposition {
    Consumed,
    HeldOut,
    Diagnostic,
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct EvidenceEntry {
    pub identity: EvidenceIdentity,
    pub disposition: EvidenceDisposition,
}

#[derive(Debug, Clone, Default, PartialEq, Eq, Serialize, Deserialize)]
pub struct EvidenceLedger {
    entries: Vec<EvidenceEntry>,
}

#[derive(Debug, Error, Clone, PartialEq, Eq)]
pub enum EvidenceLedgerError {
    #[error("evidence epoch and channel identifiers must not be empty")]
    EmptyIdentity,
    #[error("evidence identity is recorded more than once: {0:?}")]
    DuplicateIdentity(EvidenceIdentity),
    #[error("evidence has already been consumed: {0:?}")]
    DuplicateConsumption(EvidenceIdentity),
}

impl EvidenceLedger {
    pub fn new() -> Self {
        Self::default()
    }

    pub fn from_entries(entries: Vec<EvidenceEntry>) -> Result<Self, EvidenceLedgerError> {
        let ledger = Self { entries };
        ledger.validate()?;
        Ok(ledger)
    }

    pub fn entries(&self) -> &[EvidenceEntry] {
        &self.entries
    }

    pub fn record(
        &mut self,
        identity: EvidenceIdentity,
        disposition: EvidenceDisposition,
    ) -> Result<(), EvidenceLedgerError> {
        validate_evidence_identity(&identity)?;
        if self.entries.iter().any(|entry| entry.identity == identity) {
            return Err(EvidenceLedgerError::DuplicateIdentity(identity));
        }
        self.entries.push(EvidenceEntry {
            identity,
            disposition,
        });
        Ok(())
    }

    /// Marks an evidence component as used exactly once.
    ///
    /// A previously held-out or diagnostic component may be consumed. A second
    /// consumption of the same component is rejected.
    pub fn consume(&mut self, identity: EvidenceIdentity) -> Result<(), EvidenceLedgerError> {
        validate_evidence_identity(&identity)?;
        if let Some(entry) = self
            .entries
            .iter_mut()
            .find(|entry| entry.identity == identity)
        {
            if entry.disposition == EvidenceDisposition::Consumed {
                return Err(EvidenceLedgerError::DuplicateConsumption(identity));
            }
            entry.disposition = EvidenceDisposition::Consumed;
            return Ok(());
        }
        self.entries.push(EvidenceEntry {
            identity,
            disposition: EvidenceDisposition::Consumed,
        });
        Ok(())
    }

    pub fn validate(&self) -> Result<(), EvidenceLedgerError> {
        let mut identities = BTreeSet::new();
        for entry in &self.entries {
            validate_evidence_identity(&entry.identity)?;
            if !identities.insert(&entry.identity) {
                return Err(EvidenceLedgerError::DuplicateIdentity(
                    entry.identity.clone(),
                ));
            }
        }
        Ok(())
    }
}

fn validate_evidence_identity(identity: &EvidenceIdentity) -> Result<(), EvidenceLedgerError> {
    if identity.epoch_id.trim().is_empty()
        || identity
            .channel
            .as_ref()
            .is_some_and(|channel| channel.trim().is_empty())
    {
        return Err(EvidenceLedgerError::EmptyIdentity);
    }
    Ok(())
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct TurnMetadata {
    pub initial_position: LatLon,
    pub initial_track_true: Degrees,
    pub turn_time: Seconds,
    /// Scalar control for selected-control families; actual WGS84 initial
    /// direct-to course at the turn for a fixed-waypoint family. It is never
    /// the inactive internal LNAV parameter sentinel.
    pub post_turn_track_true: Degrees,
    pub turn_count: u8,
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct PosteriorHandoffParticle {
    pub identity: PosteriorParticleIdentity,
    pub normalized_log_weight: f64,
    pub source_log_likelihood: f64,
    pub aircraft: AircraftState,
    pub heading_true: Degrees,
    pub lateral_mode: LateralMode,
    pub mach: f64,
    pub turn: TurnMetadata,
    pub bfo_bias: BfoBiasState,
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct PosteriorHandoff {
    pub schema_version: u32,
    pub run: PosteriorRunMetadata,
    pub evidence: EvidenceLedger,
    pub particles: Vec<PosteriorHandoffParticle>,
}

#[derive(Debug, Error, Clone, PartialEq)]
pub enum PosteriorHandoffError {
    #[error("unsupported posterior handoff schema version {0}")]
    UnsupportedSchema(u32),
    #[error("posterior handoff metadata is incomplete")]
    IncompleteMetadata,
    #[error("posterior handoff SHA-256 identity is invalid: {0}")]
    InvalidSha256(String),
    #[error("posterior handoff contains no particles")]
    NoParticles,
    #[error("posterior particle identity is duplicated: {0:?}")]
    DuplicateParticle(PosteriorParticleIdentity),
    #[error("posterior particle does not match its run identity: {0:?}")]
    ParticleRunMismatch(PosteriorParticleIdentity),
    #[error("posterior lateral guidance does not match its run-level fixed-waypoint metadata")]
    FixedWaypointMismatch,
    #[error("posterior particle has invalid state or trajectory metadata: {0:?}")]
    InvalidParticle(PosteriorParticleIdentity),
    #[error("aircraft BFO bias and full BFO-bias state disagree: {0:?}")]
    BfoBiasMeanMismatch(PosteriorParticleIdentity),
    #[error("posterior log weights are not normalized; logsumexp={0}")]
    UnnormalizedLogWeights(f64),
    #[error(transparent)]
    Evidence(#[from] EvidenceLedgerError),
}

impl PosteriorHandoff {
    pub fn validate(&self) -> Result<(), PosteriorHandoffError> {
        if !matches!(
            self.schema_version,
            LEGACY_SCALAR_HANDOFF_SCHEMA_VERSION | POSTERIOR_HANDOFF_SCHEMA_VERSION
        ) {
            return Err(PosteriorHandoffError::UnsupportedSchema(
                self.schema_version,
            ));
        }
        if self.run.model_family.trim().is_empty()
            || self.run.input_sha256.is_empty()
            || self
                .run
                .input_sha256
                .keys()
                .any(|identity| identity.trim().is_empty())
        {
            return Err(PosteriorHandoffError::IncompleteMetadata);
        }
        validate_sha256(&self.run.run_identity_sha256)?;
        validate_sha256(&self.run.config_sha256)?;
        for digest in self.run.input_sha256.values() {
            validate_sha256(digest)?;
        }
        if let Some(route) = &self.run.fixed_waypoint {
            if route.target_name.trim().is_empty()
                || !valid_position(route.position)
                || !route.arrival_radius.is_finite()
                || route.arrival_radius.0 <= 0.0
                || route.coordinate_source_title.trim().is_empty()
                || route.coordinate_source_uri.trim().is_empty()
                || route.coordinate_frame_assumption.trim().is_empty()
                || route
                    .coordinate_source_date
                    .as_ref()
                    .is_some_and(|date| date.trim().is_empty())
                || route.coordinate_note.trim().is_empty()
            {
                return Err(PosteriorHandoffError::FixedWaypointMismatch);
            }
        }
        self.evidence.validate()?;
        if self.particles.is_empty() {
            return Err(PosteriorHandoffError::NoParticles);
        }

        // Schema v1 predates typed fixed-waypoint guidance. A v1 LNAV value
        // could be silently mis-propagated by a legacy reader, so the
        // combination is invalid even when waypoint metadata is present.
        if self.schema_version == LEGACY_SCALAR_HANDOFF_SCHEMA_VERSION
            && (self.run.fixed_waypoint.is_some()
                || self
                    .particles
                    .iter()
                    .any(|particle| particle.lateral_mode == LateralMode::LateralNavigation))
        {
            return Err(PosteriorHandoffError::FixedWaypointMismatch);
        }
        if self.schema_version == POSTERIOR_HANDOFF_SCHEMA_VERSION
            && self.run.lateral_mode.is_none()
        {
            return Err(PosteriorHandoffError::FixedWaypointMismatch);
        }

        let declared_mode = self
            .run
            .lateral_mode
            .unwrap_or(self.particles[0].lateral_mode);
        if self
            .particles
            .iter()
            .any(|particle| particle.lateral_mode != declared_mode)
            || (declared_mode == LateralMode::LateralNavigation)
                != self.run.fixed_waypoint.is_some()
        {
            return Err(PosteriorHandoffError::FixedWaypointMismatch);
        }

        let mut identities = BTreeSet::new();
        for particle in &self.particles {
            if !identities.insert(&particle.identity) {
                return Err(PosteriorHandoffError::DuplicateParticle(
                    particle.identity.clone(),
                ));
            }
            if particle.identity.model_family != self.run.model_family
                || particle.identity.seed != self.run.seed
            {
                return Err(PosteriorHandoffError::ParticleRunMismatch(
                    particle.identity.clone(),
                ));
            }
            if !particle.normalized_log_weight.is_finite()
                || !particle.source_log_likelihood.is_finite()
                || !particle.aircraft.all_finite()
                || !valid_position(particle.aircraft.position)
                || !valid_bearing(particle.aircraft.track_true)
                || particle.aircraft.ground_speed.0 <= 0.0
                || !valid_bearing(particle.heading_true)
                || !particle.mach.is_finite()
                || particle.mach <= 0.0
                || !valid_position(particle.turn.initial_position)
                || !valid_bearing(particle.turn.initial_track_true)
                || !particle.turn.turn_time.is_finite()
                || !valid_bearing(particle.turn.post_turn_track_true)
                || !particle.bfo_bias.mean_hz.is_finite()
                || !particle.bfo_bias.variance_hz2.is_finite()
                || particle.bfo_bias.variance_hz2 < 0.0
            {
                return Err(PosteriorHandoffError::InvalidParticle(
                    particle.identity.clone(),
                ));
            }
            if particle.aircraft.bfo_bias.0 != particle.bfo_bias.mean_hz {
                return Err(PosteriorHandoffError::BfoBiasMeanMismatch(
                    particle.identity.clone(),
                ));
            }
        }

        let maximum = self
            .particles
            .iter()
            .map(|particle| particle.normalized_log_weight)
            .fold(f64::NEG_INFINITY, f64::max);
        let log_sum = maximum
            + self
                .particles
                .iter()
                .map(|particle| (particle.normalized_log_weight - maximum).exp())
                .sum::<f64>()
                .ln();
        if !log_sum.is_finite() || log_sum.abs() > NORMALIZED_LOG_WEIGHT_TOLERANCE {
            return Err(PosteriorHandoffError::UnnormalizedLogWeights(log_sum));
        }
        Ok(())
    }
}

fn valid_bearing(value: Degrees) -> bool {
    value.is_finite() && (0.0..360.0).contains(&value.0)
}

fn valid_position(value: LatLon) -> bool {
    value.latitude.is_finite()
        && (-90.0..=90.0).contains(&value.latitude.0)
        && value.longitude.is_finite()
        && (-180.0..180.0).contains(&value.longitude.0)
}

fn validate_sha256(value: &str) -> Result<(), PosteriorHandoffError> {
    if value.len() != 64
        || !value
            .bytes()
            .all(|byte| byte.is_ascii_digit() || (b'a'..=b'f').contains(&byte))
    {
        return Err(PosteriorHandoffError::InvalidSha256(value.to_string()));
    }
    Ok(())
}

#[cfg(test)]
mod tests {
    use mh370_domain::{Feet, FeetPerMinute, Hertz, Knots};

    use super::*;

    fn evidence(component: EvidenceComponent) -> EvidenceIdentity {
        EvidenceIdentity {
            epoch_id: "m0011".to_string(),
            channel: Some("R1200".to_string()),
            component,
        }
    }

    fn particle(index: usize, weight: f64) -> PosteriorHandoffParticle {
        let bfo_bias = BfoBiasState {
            mean_hz: 151.25 + index as f64,
            variance_hz2: 3.5,
        };
        PosteriorHandoffParticle {
            identity: PosteriorParticleIdentity {
                model_family: "through-0011-medium-bfo".to_string(),
                seed: 370_023,
                particle: index,
            },
            normalized_log_weight: weight.ln(),
            source_log_likelihood: -12.5 - index as f64,
            aircraft: AircraftState {
                time: Seconds(22_150.0),
                position: LatLon::new(-31.0 - index as f64, 96.0).unwrap(),
                altitude: Feet(35_000.0),
                track_true: Degrees(180.0),
                ground_speed: Knots(480.0),
                vertical_speed: FeetPerMinute(0.0),
                bfo_bias: Hertz(bfo_bias.mean_hz),
            },
            heading_true: Degrees(182.0),
            lateral_mode: LateralMode::ConstantTrueTrack,
            mach: 0.82,
            turn: TurnMetadata {
                initial_position: LatLon::new(6.0, 96.0).unwrap(),
                initial_track_true: Degrees(295.0),
                turn_time: Seconds(1_700.0),
                post_turn_track_true: Degrees(180.0),
                turn_count: 1,
            },
            bfo_bias,
        }
    }

    fn handoff() -> PosteriorHandoff {
        let mut ledger = EvidenceLedger::new();
        ledger.consume(evidence(EvidenceComponent::Bto)).unwrap();
        ledger
            .record(
                evidence(EvidenceComponent::Bfo),
                EvidenceDisposition::HeldOut,
            )
            .unwrap();
        PosteriorHandoff {
            schema_version: POSTERIOR_HANDOFF_SCHEMA_VERSION,
            run: PosteriorRunMetadata {
                model_family: "through-0011-medium-bfo".to_string(),
                seed: 370_023,
                lateral_mode: Some(LateralMode::ConstantTrueTrack),
                run_identity_sha256: "a".repeat(64),
                config_sha256: "b".repeat(64),
                input_sha256: BTreeMap::from([
                    ("observations".to_string(), "c".repeat(64)),
                    ("ephemeris".to_string(), "d".repeat(64)),
                ]),
                fixed_waypoint: None,
            },
            evidence: ledger,
            particles: vec![particle(0, 0.25), particle(1, 0.75)],
        }
    }

    #[test]
    fn exact_two_particle_serde_round_trip() {
        let source = handoff();
        source.validate().unwrap();
        let bytes = serde_json::to_vec(&source).unwrap();
        let decoded: PosteriorHandoff = serde_json::from_slice(&bytes).unwrap();
        assert_eq!(decoded, source);
        decoded.validate().unwrap();
    }

    #[test]
    fn validation_requires_logsumexp_normalized_weights() {
        let mut value = handoff();
        value.validate().unwrap();
        value.particles[0].normalized_log_weight = 0.8_f64.ln();
        value.particles[1].normalized_log_weight = 0.8_f64.ln();
        assert!(matches!(
            value.validate(),
            Err(PosteriorHandoffError::UnnormalizedLogWeights(_))
        ));
    }

    #[test]
    fn validation_rejects_mismatched_aircraft_and_full_bias_mean() {
        let mut value = handoff();
        value.particles[0].aircraft.bfo_bias = Hertz(999.0);
        assert!(matches!(
            value.validate(),
            Err(PosteriorHandoffError::BfoBiasMeanMismatch(identity))
                if identity.particle == 0
        ));
    }

    #[test]
    fn fixed_waypoint_is_typed_once_at_run_level_and_required_for_lnav() {
        let mut value = handoff();
        for particle in &mut value.particles {
            particle.lateral_mode = LateralMode::LateralNavigation;
        }
        value.run.lateral_mode = Some(LateralMode::LateralNavigation);
        assert_eq!(
            value.validate(),
            Err(PosteriorHandoffError::FixedWaypointMismatch)
        );

        value.run.fixed_waypoint = Some(FixedWaypointMetadata {
            target_name: "Fixture skiway".to_string(),
            position: LatLon::new(-68.5, 78.8).unwrap(),
            arrival_radius: NauticalMiles(1.0),
            coordinate_source_title: "Official fixture register".to_string(),
            coordinate_source_uri: "https://example.invalid/register".to_string(),
            coordinate_frame_assumption: "treated as WGS84".to_string(),
            coordinate_source_date: Some("2014".to_string()),
            coordinate_note: "Fixture reference point".to_string(),
        });
        value.validate().unwrap();

        let bytes = serde_json::to_vec(&value).unwrap();
        let decoded: PosteriorHandoff = serde_json::from_slice(&bytes).unwrap();
        assert_eq!(decoded, value);
        decoded.validate().unwrap();

        let mut mixed = value.clone();
        mixed.particles[0].lateral_mode = LateralMode::ConstantTrueTrack;
        assert_eq!(
            mixed.validate(),
            Err(PosteriorHandoffError::FixedWaypointMismatch)
        );

        let mut scalar_with_route = handoff();
        scalar_with_route.run.fixed_waypoint = value.run.fixed_waypoint.clone();
        assert_eq!(
            scalar_with_route.validate(),
            Err(PosteriorHandoffError::FixedWaypointMismatch)
        );

        value.run.fixed_waypoint.as_mut().unwrap().arrival_radius = NauticalMiles(0.0);
        assert_eq!(
            value.validate(),
            Err(PosteriorHandoffError::FixedWaypointMismatch)
        );
    }

    #[test]
    fn current_reader_accepts_legacy_v1_scalar_handoffs_only() {
        let mut legacy = handoff();
        legacy.schema_version = LEGACY_SCALAR_HANDOFF_SCHEMA_VERSION;
        legacy.run.lateral_mode = None;
        legacy.validate().unwrap();

        legacy.run.fixed_waypoint = Some(FixedWaypointMetadata {
            target_name: "Fixture skiway".to_string(),
            position: LatLon::new(-68.5, 78.8).unwrap(),
            arrival_radius: NauticalMiles(1.0),
            coordinate_source_title: "Official fixture register".to_string(),
            coordinate_source_uri: "https://example.invalid/register".to_string(),
            coordinate_frame_assumption: "treated as WGS84".to_string(),
            coordinate_source_date: Some("2014".to_string()),
            coordinate_note: "Fixture reference point".to_string(),
        });
        for particle in &mut legacy.particles {
            particle.lateral_mode = LateralMode::LateralNavigation;
        }
        assert_eq!(
            legacy.validate(),
            Err(PosteriorHandoffError::FixedWaypointMismatch)
        );

        legacy.run.fixed_waypoint = None;
        assert_eq!(
            legacy.validate(),
            Err(PosteriorHandoffError::FixedWaypointMismatch)
        );
    }

    fn assert_invalid_particle(value: PosteriorHandoff) {
        assert!(matches!(
            value.validate(),
            Err(PosteriorHandoffError::InvalidParticle(_))
        ));
    }

    #[test]
    fn validation_requires_canonical_aircraft_and_turn_positions() {
        let mut boundaries = handoff();
        boundaries.particles[0].aircraft.position = LatLon {
            latitude: Degrees(90.0),
            longitude: Degrees(-180.0),
        };
        boundaries.particles[0].turn.initial_position = LatLon {
            latitude: Degrees(-90.0),
            longitude: Degrees(179.0),
        };
        boundaries.validate().unwrap();

        let mut aircraft_latitude = handoff();
        aircraft_latitude.particles[0].aircraft.position.latitude = Degrees(90.1);
        assert_invalid_particle(aircraft_latitude);

        let mut aircraft_longitude = handoff();
        aircraft_longitude.particles[0].aircraft.position.longitude = Degrees(180.0);
        assert_invalid_particle(aircraft_longitude);

        let mut turn_latitude = handoff();
        turn_latitude.particles[0].turn.initial_position.latitude = Degrees(-90.1);
        assert_invalid_particle(turn_latitude);

        let mut turn_longitude = handoff();
        turn_longitude.particles[0].turn.initial_position.longitude = Degrees(180.0);
        assert_invalid_particle(turn_longitude);
    }

    #[test]
    fn validation_requires_canonical_aircraft_heading_and_turn_bearings() {
        let mut track = handoff();
        track.particles[0].aircraft.track_true = Degrees(360.0);
        assert_invalid_particle(track);

        let mut heading = handoff();
        heading.particles[0].heading_true = Degrees(-0.1);
        assert_invalid_particle(heading);

        let mut initial_track = handoff();
        initial_track.particles[0].turn.initial_track_true = Degrees(360.0);
        assert_invalid_particle(initial_track);

        let mut post_turn_track = handoff();
        post_turn_track.particles[0].turn.post_turn_track_true = Degrees(-0.1);
        assert_invalid_particle(post_turn_track);
    }

    #[test]
    fn validation_requires_strictly_positive_ground_speed() {
        let mut zero = handoff();
        zero.particles[0].aircraft.ground_speed = Knots(0.0);
        assert_invalid_particle(zero);

        let mut negative = handoff();
        negative.particles[0].aircraft.ground_speed = Knots(-1.0);
        assert_invalid_particle(negative);
    }

    #[test]
    fn evidence_can_only_be_consumed_once() {
        let identity = evidence(EvidenceComponent::LogonRequestTime);
        let mut ledger = EvidenceLedger::new();
        ledger.consume(identity.clone()).unwrap();
        assert_eq!(
            ledger.consume(identity.clone()),
            Err(EvidenceLedgerError::DuplicateConsumption(identity))
        );
    }
}
