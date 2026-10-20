mod broad_flight;
mod broad_handoff;
mod final_flight;
mod posterior_handoff;

pub use broad_flight::{
    BroadDualEngineExhaustionOutcome, BroadDualEngineExhaustionResult, BroadFlightConfig,
    BroadFlightDiagnostics, BroadFlightError, BroadFlightModel, BroadFlightModelOptions,
    BroadFlightObservation, BroadFlightParticleStatus, BroadFlightScores, BroadFlightState,
    BroadFlightStratum, BroadFuelAnchorObservation, BroadFuelDiagnosticStatus,
    BroadFuelExhaustionSelectionGuide, BroadFuelExhaustionSelectionGuideConfig,
    BroadFuelExhaustionSelectionGuideEvaluation, BroadFuelExhaustionSelectionGuideOutcome,
    BroadFuelExhaustionSelectionGuidePoint, BroadFuelFlowInitializationDesign,
    BroadFuelUncertainty, BroadPendingRenewalRefreshConfig, BroadPendingRenewalRefreshDiagnostics,
    BroadPendingRenewalRefreshKernel, BroadPoweredFeasibilityConfig,
    BroadProposalCandidateSchedule, BroadProposalCandidateTier, BroadRejectionCounts,
    BroadRejectionReason, BroadSatcomEventMarkGuideConfig, BroadSatcomEventMarkGuideDiagnostics,
    BroadSatcomEventMarkGuideEpoch, BroadSatcomIntermediatePotentialBridge,
    BroadSatcomIntermediatePotentialConfig, BroadSatcomIntermediatePotentialContext,
    BroadSatcomIntermediatePotentialPoint, BroadSatcomIntermediatePotentialPointKind,
    BroadSatcomObservation, BroadStratumFuelUncertaintyOverride, BroadUniformRange,
    BROAD_FLIGHT_MODEL_FAMILY, BROAD_FUEL_EXHAUSTION_PERSISTENT_TWIST_FAMILY,
    BROAD_FUEL_EXHAUSTION_SELECTION_GUIDE_FAMILY, BROAD_PENDING_RENEWAL_REFRESH_FAMILY,
    BROAD_SATCOM_EVENT_MARK_GUIDE_FAMILY, BROAD_SATCOM_INTERMEDIATE_POTENTIAL_FAMILY,
};
pub use broad_handoff::{
    build_broad_filtering_handoff_v1, build_broad_smoothed_handoff_v1, BroadAggregateEvidenceV1,
    BroadCheckpointMetadataV1, BroadConditioningSemanticsV1, BroadEvidenceComponentV1,
    BroadEvidenceDispositionV1, BroadEvidenceEntryV1, BroadEvidenceIdentityV1,
    BroadEvidenceLedgerErrorV1, BroadEvidenceLedgerV1, BroadEvidenceStateEffectV1,
    BroadHandoffBuildErrorV1, BroadParticleEvidenceScoreV1, BroadPosteriorHandoffErrorV1,
    BroadPosteriorHandoffParticleV1, BroadPosteriorHandoffV1, BroadPosteriorParticleIdentityV1,
    BroadPosteriorReportRowV1, BroadPriorRootIdentityV1, BroadRunMetadataV1,
    BroadStratumMetadataV1, BROAD_POSTERIOR_HANDOFF_SCHEMA_VERSION,
};
pub use final_flight::{
    final_posterior_rows, parameter_names, run_final_flight_estimate,
    run_final_flight_estimate_with_environment_and_likelihood,
    run_final_flight_estimate_with_likelihood, FinalFlightConfig, FinalFlightError,
    FinalFlightLikelihood, FinalFlightParticle, FinalFlightRun, FinalFlightSummary,
};
pub use posterior_handoff::{
    EvidenceComponent, EvidenceDisposition, EvidenceEntry, EvidenceIdentity, EvidenceLedger,
    EvidenceLedgerError, FixedWaypointMetadata, PosteriorHandoff, PosteriorHandoffError,
    PosteriorHandoffParticle, PosteriorParticleIdentity, PosteriorRunMetadata, TurnMetadata,
    POSTERIOR_HANDOFF_SCHEMA_VERSION,
};

use std::collections::HashMap;

use mh370_domain::{Hertz, Microseconds, SatcomObservation, Seconds, Vec3};
use serde::{Deserialize, Serialize};
use thiserror::Error;

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct FlightObservation {
    pub id: String,
    pub time_utc: String,
    pub satellite_afc_hz: f64,
    pub measurement: SatcomObservation,
}

#[derive(Debug, Error)]
pub enum InputError {
    #[error("input table is empty or lacks required columns")]
    InvalidHeader,
    #[error("invalid input row {0}")]
    InvalidRow(usize),
    #[error("observation {0} has no satellite ephemeris")]
    MissingSatellite(String),
    #[error("duplicate satellite ephemeris identifier {0}")]
    DuplicateSatellite(String),
    #[error("at least one observation is required")]
    NoObservations,
    #[error("observations are not ordered by time")]
    ObservationOrder,
    #[error("BFO standard-deviation override must be finite and positive")]
    InvalidBfoDeviation,
}

fn column_indices(
    header: &str,
    required: &[&'static str],
) -> Result<HashMap<&'static str, usize>, InputError> {
    let columns = header.split(',').collect::<Vec<_>>();
    required
        .iter()
        .map(|name| {
            columns
                .iter()
                .position(|column| column == name)
                .map(|index| (*name, index))
                .ok_or(InputError::InvalidHeader)
        })
        .collect()
}

fn parse_number(value: &str, row: usize) -> Result<f64, InputError> {
    value
        .parse::<f64>()
        .map_err(|_| InputError::InvalidRow(row))
}

fn parse_optional(value: &str, row: usize) -> Result<Option<f64>, InputError> {
    if value.is_empty() {
        Ok(None)
    } else {
        parse_number(value, row).map(Some)
    }
}

pub fn parse_satcom_observations(
    observation_csv: &str,
    ephemeris_csv: &str,
    ground_station_position_km: Vec3,
    bfo_sd_override_hz: Option<f64>,
) -> Result<Vec<FlightObservation>, InputError> {
    if bfo_sd_override_hz.is_some_and(|value| !value.is_finite() || value <= 0.0) {
        return Err(InputError::InvalidBfoDeviation);
    }

    let mut ephemeris_lines = ephemeris_csv.lines();
    let ephemeris_header = ephemeris_lines.next().ok_or(InputError::InvalidHeader)?;
    let ephemeris_columns = ephemeris_header.split(',').count();
    let ephemeris_index = column_indices(
        ephemeris_header,
        &[
            "epoch_id", "x_km", "y_km", "z_km", "vx_km_s", "vy_km_s", "vz_km_s",
        ],
    )?;
    let mut ephemeris = HashMap::new();
    for (line_index, line) in ephemeris_lines.enumerate() {
        let row = line_index + 2;
        if line.trim().is_empty() {
            continue;
        }
        let fields = line.split(',').collect::<Vec<_>>();
        if fields.len() != ephemeris_columns {
            return Err(InputError::InvalidRow(row));
        }
        let id = fields[ephemeris_index["epoch_id"]].to_string();
        let geometry = (
            Vec3::new(
                parse_number(fields[ephemeris_index["x_km"]], row)?,
                parse_number(fields[ephemeris_index["y_km"]], row)?,
                parse_number(fields[ephemeris_index["z_km"]], row)?,
            ),
            Vec3::new(
                parse_number(fields[ephemeris_index["vx_km_s"]], row)?,
                parse_number(fields[ephemeris_index["vy_km_s"]], row)?,
                parse_number(fields[ephemeris_index["vz_km_s"]], row)?,
            ),
        );
        if ephemeris.insert(id.clone(), geometry).is_some() {
            return Err(InputError::DuplicateSatellite(id));
        }
    }

    let mut observation_lines = observation_csv.lines();
    let observation_header = observation_lines.next().ok_or(InputError::InvalidHeader)?;
    let observation_columns = observation_header.split(',').count();
    let observation_index = column_indices(
        observation_header,
        &[
            "epoch_id",
            "time_utc",
            "seconds_from_t0",
            "bto_us",
            "bto_sd_us",
            "bfo_hz",
            "bfo_sd_hz",
            "satellite_afc_hz",
        ],
    )?;
    let mut observations = Vec::new();
    for (line_index, line) in observation_lines.enumerate() {
        let row = line_index + 2;
        if line.trim().is_empty() {
            continue;
        }
        let fields = line.split(',').collect::<Vec<_>>();
        if fields.len() != observation_columns {
            return Err(InputError::InvalidRow(row));
        }
        let id = fields[observation_index["epoch_id"]].to_string();
        let (satellite_position_km, satellite_velocity_km_s) = ephemeris
            .get(&id)
            .copied()
            .ok_or_else(|| InputError::MissingSatellite(id.clone()))?;
        let bto = parse_optional(fields[observation_index["bto_us"]], row)?;
        let bto_sd = parse_optional(fields[observation_index["bto_sd_us"]], row)?;
        let bfo = parse_optional(fields[observation_index["bfo_hz"]], row)?;
        let mut bfo_sd = parse_optional(fields[observation_index["bfo_sd_hz"]], row)?;
        if bfo.is_some() {
            if let Some(override_value) = bfo_sd_override_hz {
                bfo_sd = Some(override_value);
            }
        }
        let measurement = SatcomObservation {
            time: Seconds(parse_number(
                fields[observation_index["seconds_from_t0"]],
                row,
            )?),
            satellite_position_km,
            satellite_velocity_km_s,
            ground_station_position_km,
            bto: bto.map(Microseconds),
            bto_sd: bto_sd.map(Microseconds),
            bfo: bfo.map(Hertz),
            bfo_sd: bfo_sd.map(Hertz),
        };
        measurement
            .validate()
            .map_err(|_| InputError::InvalidRow(row))?;
        observations.push(FlightObservation {
            id,
            time_utc: fields[observation_index["time_utc"]].to_string(),
            satellite_afc_hz: parse_number(fields[observation_index["satellite_afc_hz"]], row)?,
            measurement,
        });
    }
    if observations.is_empty() {
        return Err(InputError::NoObservations);
    }
    if observations
        .windows(2)
        .any(|pair| pair[1].measurement.time.0 < pair[0].measurement.time.0)
    {
        return Err(InputError::ObservationOrder);
    }
    Ok(observations)
}

#[cfg(test)]
mod tests {
    use super::*;

    const EPHEMERIS: &str = "epoch_id,time_utc,x_km,y_km,z_km,vx_km_s,vy_km_s,vz_km_s\n\
one,t,18161,38060,1029,0.002,-0.001,-0.046\n";
    const OBSERVATIONS: &str =
        "epoch_id,time_utc,seconds_from_t0,bto_us,bto_sd_us,bfo_hz,bfo_sd_hz,satellite_afc_hz,note\n\
one,t,60,12000,100000,,,0,fixture\n";

    #[test]
    fn compact_parser_joins_ephemeris_by_identifier() {
        let observations = parse_satcom_observations(
            OBSERVATIONS,
            EPHEMERIS,
            Vec3::new(-2_368.8, 4_881.1, -3_342.0),
            None,
        )
        .unwrap();
        assert_eq!(observations.len(), 1);
        assert_eq!(observations[0].id, "one");
        assert_eq!(observations[0].measurement.time.0, 60.0);
    }

    #[test]
    fn parser_rejects_missing_ephemeris_and_invalid_bfo_override() {
        let missing = OBSERVATIONS.replace("one,t,60", "missing,t,60");
        assert!(matches!(
            parse_satcom_observations(&missing, EPHEMERIS, Vec3::default(), None),
            Err(InputError::MissingSatellite(_))
        ));
        assert!(matches!(
            parse_satcom_observations(OBSERVATIONS, EPHEMERIS, Vec3::default(), Some(0.0)),
            Err(InputError::InvalidBfoDeviation)
        ));
    }
}
