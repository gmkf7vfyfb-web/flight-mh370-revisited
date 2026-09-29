use std::collections::BTreeSet;

use mh370_antenna::{ConditionalPowerObservation, DirectionalGainGrid};
use serde::{Deserialize, Serialize};
use serde_json::Value;

use super::{is_sha256, reject_truth_keys, KnownFlightAntennaConfig, KnownFlightError};

const ANTENNA_PACKAGE_SCHEMA: &str = "mh371-conditional-antenna-power-v1";

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct KnownFlightAntennaObservation {
    pub channel: String,
    pub raw_rows: usize,
    pub power_time_utc: String,
    pub power_time_offset_s: f64,
    pub power: ConditionalPowerObservation,
}

#[derive(Debug, Clone, Deserialize)]
struct PackagePowerRow {
    epoch_id: String,
    satcom_time_utc: String,
    power_time_utc: String,
    power_time_offset_s: f64,
    channel: String,
    raw_rows: usize,
    observed_dbm: f64,
    full_precompensation_prediction_dbm: f64,
}

#[derive(Debug, Clone, Deserialize)]
pub struct KnownFlightAntennaPowerPackage {
    schema_version: String,
    source_id: String,
    status: String,
    surface_basis: String,
    source_result_sha256: String,
    observations: Vec<PackagePowerRow>,
}

impl KnownFlightAntennaPowerPackage {
    fn validate(&self) -> Result<(), KnownFlightError> {
        if self.schema_version != ANTENNA_PACKAGE_SCHEMA
            || self.source_id != "mh371-rxgain-conditional-control"
            || self.status != "conditional_sensitivity_only"
            || self.surface_basis != "unverified_first_pass_reconstruction"
            || !is_sha256(&self.source_result_sha256)
            || self.observations.is_empty()
        {
            return Err(KnownFlightError::InvalidPackage(
                "conditional antenna package identity is invalid".to_string(),
            ));
        }
        let mut epoch_ids = BTreeSet::new();
        for row in &self.observations {
            if row.epoch_id.is_empty()
                || row.satcom_time_utc.is_empty()
                || row.power_time_utc.is_empty()
                || row.channel.is_empty()
                || row.raw_rows == 0
                || !row.power_time_offset_s.is_finite()
                || !row.observed_dbm.is_finite()
                || !row.full_precompensation_prediction_dbm.is_finite()
                || !epoch_ids.insert(row.epoch_id.clone())
            {
                return Err(KnownFlightError::InvalidPackage(
                    "conditional antenna observation is invalid".to_string(),
                ));
            }
        }
        Ok(())
    }

    pub(crate) fn align(
        &self,
        epochs: &[(String, String)],
        configuration: &KnownFlightAntennaConfig,
    ) -> Result<Vec<KnownFlightAntennaObservation>, KnownFlightError> {
        if self.observations.len() != epochs.len() {
            return Err(KnownFlightError::InvalidPackage(
                "conditional antenna epochs do not match SATCOM epochs".to_string(),
            ));
        }
        epochs
            .iter()
            .map(|(epoch_id, time_utc)| {
                let row = self
                    .observations
                    .iter()
                    .find(|candidate| &candidate.epoch_id == epoch_id)
                    .ok_or_else(|| {
                        KnownFlightError::InvalidPackage(format!(
                            "conditional antenna observation is absent for {epoch_id}"
                        ))
                    })?;
                if &row.satcom_time_utc != time_utc {
                    return Err(KnownFlightError::InvalidPackage(format!(
                        "conditional antenna time differs for {epoch_id}"
                    )));
                }
                Ok(KnownFlightAntennaObservation {
                    channel: row.channel.clone(),
                    raw_rows: row.raw_rows,
                    power_time_utc: row.power_time_utc.clone(),
                    power_time_offset_s: row.power_time_offset_s,
                    power: ConditionalPowerObservation {
                        observed_dbm: row.observed_dbm,
                        full_precompensation_prediction_dbm: row
                            .full_precompensation_prediction_dbm,
                        standard_deviation_db: configuration.observation_sd_db,
                        reference_gain_dbic: configuration.reference_gain_dbic,
                        directional_departure_scale: configuration.directional_departure_scale,
                        permit_unverified_reconstruction: configuration
                            .permit_unverified_reconstruction,
                    },
                })
            })
            .collect()
    }

    pub fn source_status(&self) -> &str {
        &self.status
    }
}

pub struct KnownFlightAntennaInputs<'a> {
    pub package: &'a KnownFlightAntennaPowerPackage,
    pub observations_sha256: &'a str,
    pub surface: &'a DirectionalGainGrid,
    pub surface_sha256: &'a str,
}

pub fn parse_known_flight_antenna_power(
    bytes: &[u8],
) -> Result<KnownFlightAntennaPowerPackage, KnownFlightError> {
    let value: Value = serde_json::from_slice(bytes)?;
    reject_truth_keys(&value, "$antenna")?;
    let package: KnownFlightAntennaPowerPackage = serde_json::from_value(value)?;
    package.validate()?;
    Ok(package)
}
