use std::{
    collections::{BTreeMap, BTreeSet},
    path::PathBuf,
};

use mh370_antenna::{
    evaluate_conditional_power, target_eirp_prediction, AircraftAttitude, AntennaError,
    ConditionalPowerObservation, DirectionalGainGrid, DirectionalPatternBasis, TargetEirpLinkModel,
};
use mh370_dynamics::OneTurnTrajectory;
use mh370_estimator::{FinalFlightLikelihood, FlightObservation};
use serde::Deserialize;
use serde_json::json;

#[derive(Debug, Clone, Deserialize)]
pub(crate) struct AccidentAntennaConfig {
    pub observations: PathBuf,
    pub surface: PathBuf,
    pub observation_sd_db: f64,
    pub reference_gain_dbic: f64,
    pub directional_departure_scale: f64,
    pub permit_unverified_reconstruction: bool,
    pub link: TargetEirpLinkModel,
}

#[derive(Debug, Clone, Deserialize)]
struct PowerRow {
    epoch_id: String,
    satcom_time_utc: String,
    power_time_utc: String,
    power_time_offset_s: f64,
    channel: String,
    raw_rows: usize,
    source_rows: String,
    observed_dbm: f64,
}

#[derive(Debug, Clone, Deserialize)]
struct PowerPackage {
    schema_version: String,
    source_id: String,
    status: String,
    surface_basis: String,
    source_result_sha256: String,
    observations: Vec<PowerRow>,
}

fn is_sha256(value: &str) -> bool {
    value.len() == 64 && value.bytes().all(|byte| byte.is_ascii_hexdigit())
}

pub(crate) struct AccidentAntennaLikelihood {
    rows: BTreeMap<String, PowerRow>,
    grid: DirectionalGainGrid,
    observation_sd_db: f64,
    reference_gain_dbic: f64,
    directional_departure_scale: f64,
    permit_unverified_reconstruction: bool,
    link: TargetEirpLinkModel,
    source_result_sha256: String,
}

impl AccidentAntennaLikelihood {
    pub(crate) fn parse(
        configuration: &AccidentAntennaConfig,
        package_bytes: &[u8],
        surface_bytes: &[u8],
        satcom_observations: &[FlightObservation],
    ) -> Result<Self, String> {
        let package: PowerPackage = serde_json::from_slice(package_bytes)
            .map_err(|error| format!("cannot parse MH370 antenna observations: {error}"))?;
        if package.schema_version != "mh370-conditional-antenna-power-v1"
            || package.source_id != "mh370-rxgain-conditional-sensitivity"
            || package.status != "conditional_sensitivity_only"
            || package.surface_basis != "unverified_first_pass_reconstruction"
            || !is_sha256(&package.source_result_sha256)
            || package.observations.is_empty()
        {
            return Err("MH370 antenna package identity is invalid".to_string());
        }
        if ![
            configuration.observation_sd_db,
            configuration.reference_gain_dbic,
            configuration.directional_departure_scale,
        ]
        .iter()
        .all(|value| value.is_finite())
            || configuration.observation_sd_db <= 0.0
            || !(0.0..=1.0).contains(&configuration.directional_departure_scale)
        {
            return Err("MH370 antenna configuration is invalid".to_string());
        }
        let satcom = satcom_observations
            .iter()
            .map(|observation| (observation.id.as_str(), observation.time_utc.as_str()))
            .collect::<BTreeMap<_, _>>();
        let mut epoch_ids = BTreeSet::new();
        let mut rows = BTreeMap::new();
        for row in package.observations {
            let time = satcom.get(row.epoch_id.as_str()).ok_or_else(|| {
                format!("antenna epoch {} is absent from SATCOM input", row.epoch_id)
            })?;
            if **time != row.satcom_time_utc
                || row.channel != "IOR-R1200-0-36ED"
                || row.power_time_utc.is_empty()
                || !row.power_time_offset_s.is_finite()
                || row.raw_rows == 0
                || row.source_rows.is_empty()
                || !row.observed_dbm.is_finite()
                || !epoch_ids.insert(row.epoch_id.clone())
            {
                return Err(format!("antenna observation {} is invalid", row.epoch_id));
            }
            rows.insert(row.epoch_id.clone(), row);
        }
        let grid = DirectionalGainGrid::parse(
            surface_bytes,
            DirectionalPatternBasis::UnverifiedReconstruction,
        )
        .map_err(|error| error.to_string())?;
        Ok(Self {
            rows,
            grid,
            observation_sd_db: configuration.observation_sd_db,
            reference_gain_dbic: configuration.reference_gain_dbic,
            directional_departure_scale: configuration.directional_departure_scale,
            permit_unverified_reconstruction: configuration.permit_unverified_reconstruction,
            link: configuration.link,
            source_result_sha256: package.source_result_sha256,
        })
    }

    pub(crate) fn metadata(&self, applied_to_posterior: bool) -> serde_json::Value {
        json!({
            "applied_to_posterior": applied_to_posterior,
            "status": "conditional_sensitivity_only",
            "endpoint": if self.directional_departure_scale == 0.0 {
                "full_target_eirp_precompensation"
            } else if self.directional_departure_scale == 1.0 {
                "no_gain_precompensation"
            } else {
                "intermediate_directional_departure"
            },
            "directional_departure_scale": self.directional_departure_scale,
            "observation_sd_db": self.observation_sd_db,
            "reference_gain_dbic": self.reference_gain_dbic,
            "power_observations": self.rows.len(),
            "epochs": self.rows.keys().collect::<Vec<_>>(),
            "source_result_sha256": self.source_result_sha256,
            "surface_basis": "unverified_first_pass_reconstruction",
            "airframe_heading_treatment": "trajectory true heading; equals the ground-track proxy only for environment-free constant-track runs",
            "excluded_power_data": [
                "18:25-18:28 restart rows: source workbook identity failure",
                "18:39 and 23:15 telephony: unresolved channel/beam calibration"
            ],
            "model_weight": null,
        })
    }

    pub(crate) fn evidence_identities(&self) -> impl Iterator<Item = (&str, &str)> {
        self.rows
            .values()
            .map(|row| (row.epoch_id.as_str(), row.channel.as_str()))
    }
}

impl FinalFlightLikelihood for AccidentAntennaLikelihood {
    fn log_likelihood(
        &self,
        trajectory: &OneTurnTrajectory,
        observation: &FlightObservation,
    ) -> Result<f64, String> {
        let Some(row) = self.rows.get(&observation.id) else {
            return Ok(0.0);
        };
        let link = target_eirp_prediction(
            trajectory.aircraft,
            observation.measurement.satellite_position_km,
            observation.measurement.ground_station_position_km,
            self.link,
        )
        .map_err(|error| error.to_string())?;
        let score = evaluate_conditional_power(
            trajectory.aircraft,
            AircraftAttitude::level(trajectory.heading_true),
            observation.measurement.satellite_position_km,
            &self.grid,
            ConditionalPowerObservation {
                observed_dbm: row.observed_dbm,
                full_precompensation_prediction_dbm: link.full_precompensation_prediction_dbm,
                standard_deviation_db: self.observation_sd_db,
                reference_gain_dbic: self.reference_gain_dbic,
                directional_departure_scale: self.directional_departure_scale,
                permit_unverified_reconstruction: self.permit_unverified_reconstruction,
            },
        );
        let score = match score {
            Ok(score) => score,
            Err(AntennaError::BelowHorizon) => return Ok(f64::NEG_INFINITY),
            Err(error) => return Err(error.to_string()),
        };
        score
            .log_likelihood
            .ok_or_else(|| "unverified antenna likelihood was not explicitly permitted".to_string())
    }
}
