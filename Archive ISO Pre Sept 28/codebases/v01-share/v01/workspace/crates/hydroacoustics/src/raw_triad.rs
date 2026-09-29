//! Input contract for later calibrated raw hydrophone-triad processing.

use std::collections::BTreeSet;

use mh370_domain::LatLon;
use serde::{Deserialize, Serialize};
use thiserror::Error;

pub const RAW_TRIAD_SCHEMA_ID: &str = "mh370-raw-hydrophone-triad";
pub const RAW_TRIAD_SCHEMA_VERSION: u32 = 1;

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum RawPressureUnit {
    Pascal,
    InstrumentCounts,
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct RawHydrophoneChannel {
    pub id: String,
    pub input_column: String,
    pub local_east_m: f64,
    pub local_north_m: f64,
    pub local_up_m: f64,
    /// Required for instrument counts and forbidden for pascals.
    pub pascal_per_count: Option<f64>,
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct RawTriadInputV1 {
    pub schema_id: String,
    pub schema_version: u32,
    pub station_id: String,
    pub station_position_wgs84: LatLon,
    pub start_time_utc: String,
    pub sample_rate_hz: f64,
    pub pressure_unit: RawPressureUnit,
    pub sample_file: String,
    pub time_offset_column: String,
    pub channels: Vec<RawHydrophoneChannel>,
    pub instrument_response_id: String,
    pub timing_correction_id: String,
}

#[derive(Debug, Error, Clone, PartialEq)]
pub enum RawTriadError {
    #[error("unsupported raw-triad schema")]
    UnsupportedSchema,
    #[error("invalid raw-triad metadata")]
    InvalidMetadata,
    #[error("a hydrophone triad requires exactly three channels")]
    NotATriad,
    #[error("duplicate hydrophone channel or input column")]
    DuplicateChannel,
    #[error("pressure-unit calibration contract is inconsistent")]
    InvalidCalibration,
}

impl RawTriadInputV1 {
    pub fn validate(&self) -> Result<(), RawTriadError> {
        if self.schema_id != RAW_TRIAD_SCHEMA_ID || self.schema_version != RAW_TRIAD_SCHEMA_VERSION
        {
            return Err(RawTriadError::UnsupportedSchema);
        }
        if self.station_id.trim().is_empty()
            || self.start_time_utc.trim().is_empty()
            || !self.sample_rate_hz.is_finite()
            || self.sample_rate_hz <= 0.0
            || self.sample_file.trim().is_empty()
            || self.time_offset_column.trim().is_empty()
            || self.instrument_response_id.trim().is_empty()
            || self.timing_correction_id.trim().is_empty()
            || !valid_position(self.station_position_wgs84)
        {
            return Err(RawTriadError::InvalidMetadata);
        }
        if self.channels.len() != 3 {
            return Err(RawTriadError::NotATriad);
        }
        let mut ids = BTreeSet::new();
        let mut columns = BTreeSet::new();
        for channel in &self.channels {
            if channel.id.trim().is_empty()
                || channel.input_column.trim().is_empty()
                || !ids.insert(channel.id.as_str())
                || !columns.insert(channel.input_column.as_str())
                || ![
                    channel.local_east_m,
                    channel.local_north_m,
                    channel.local_up_m,
                ]
                .into_iter()
                .all(f64::is_finite)
            {
                return Err(RawTriadError::DuplicateChannel);
            }
            match (self.pressure_unit, channel.pascal_per_count) {
                (RawPressureUnit::Pascal, None) => {}
                (RawPressureUnit::InstrumentCounts, Some(value))
                    if value.is_finite() && value > 0.0 => {}
                _ => return Err(RawTriadError::InvalidCalibration),
            }
        }
        Ok(())
    }
}

fn valid_position(position: LatLon) -> bool {
    position.latitude.0.is_finite()
        && (-90.0..=90.0).contains(&position.latitude.0)
        && position.longitude.0.is_finite()
        && (-180.0..180.0).contains(&position.longitude.0)
}

#[cfg(test)]
mod tests {
    use super::*;

    fn input(unit: RawPressureUnit) -> RawTriadInputV1 {
        RawTriadInputV1 {
            schema_id: RAW_TRIAD_SCHEMA_ID.to_string(),
            schema_version: RAW_TRIAD_SCHEMA_VERSION,
            station_id: "H01W".to_string(),
            station_position_wgs84: LatLon::new(-34.892, 114.141).unwrap(),
            start_time_utc: "2014-03-08T00:00:00Z".to_string(),
            sample_rate_hz: 100.0,
            pressure_unit: unit,
            sample_file: "h01w.csv".to_string(),
            time_offset_column: "time_offset_s".to_string(),
            channels: (0..3)
                .map(|index| RawHydrophoneChannel {
                    id: format!("H01W{index}"),
                    input_column: format!("channel_{index}"),
                    local_east_m: index as f64 * 500.0,
                    local_north_m: 0.0,
                    local_up_m: 0.0,
                    pascal_per_count: match unit {
                        RawPressureUnit::Pascal => None,
                        RawPressureUnit::InstrumentCounts => Some(1.0e-6),
                    },
                })
                .collect(),
            instrument_response_id: "response-receipt-sha256".to_string(),
            timing_correction_id: "timing-receipt-sha256".to_string(),
        }
    }

    #[test]
    fn calibrated_counts_and_pascal_triads_validate() {
        input(RawPressureUnit::Pascal).validate().unwrap();
        input(RawPressureUnit::InstrumentCounts).validate().unwrap();
    }

    #[test]
    fn unit_calibration_mismatch_and_non_triad_fail_closed() {
        let mut invalid = input(RawPressureUnit::InstrumentCounts);
        invalid.channels[0].pascal_per_count = None;
        assert_eq!(invalid.validate(), Err(RawTriadError::InvalidCalibration));

        let mut short = input(RawPressureUnit::Pascal);
        short.channels.pop();
        assert_eq!(short.validate(), Err(RawTriadError::NotATriad));
    }
}
