use mh370_domain::{AircraftState, SatcomObservation};
use serde::{Deserialize, Serialize};
use thiserror::Error;

use crate::{
    bfo_bias_predictive_update, bfo_components, bto, normal_log_density, BfoBiasState,
    BfoConstants, BtoConstants, StatisticsError,
};

#[derive(Debug, Clone, Copy, PartialEq, Serialize, Deserialize)]
pub struct SatcomModelConfig {
    pub bto: BtoConstants,
    pub bfo: BfoConstants,
    pub bfo_bias_prior_mean_hz: f64,
    pub bfo_bias_prior_sd_hz: f64,
}

impl SatcomModelConfig {
    pub fn validate(&self) -> Result<(), SatcomModelError> {
        if ![
            self.bto.speed_of_light_km_s,
            self.bto.nominal_delay_us,
            self.bto.channel_term_us,
            self.bfo.uplink_hz,
            self.bfo.downlink_hz,
            self.bfo.speed_of_light_km_s,
            self.bfo.nominal_satellite_longitude_deg,
            self.bfo.nominal_satellite_altitude_km,
            self.bfo_bias_prior_mean_hz,
            self.bfo_bias_prior_sd_hz,
        ]
        .iter()
        .all(|value| value.is_finite())
            || self.bto.speed_of_light_km_s <= 0.0
            || self.bfo.speed_of_light_km_s <= 0.0
            || self.bfo.uplink_hz <= 0.0
            || self.bfo.downlink_hz <= 0.0
            || self.bfo.nominal_satellite_altitude_km <= 0.0
            || self.bfo_bias_prior_sd_hz <= 0.0
        {
            return Err(SatcomModelError::InvalidConfiguration);
        }
        Ok(())
    }

    pub fn initial_bias(&self) -> BfoBiasState {
        BfoBiasState {
            mean_hz: self.bfo_bias_prior_mean_hz,
            variance_hz2: self.bfo_bias_prior_sd_hz.powi(2),
        }
    }
}

#[derive(Debug, Clone, Copy, PartialEq, Serialize, Deserialize)]
pub struct ObservationFit {
    pub log_likelihood: f64,
    pub predicted_bto_us: Option<f64>,
    pub bto_residual_us: Option<f64>,
    pub predicted_bfo_without_bias_hz: Option<f64>,
    pub bfo_innovation_hz: Option<f64>,
}

#[derive(Debug, Error)]
pub enum SatcomModelError {
    #[error("invalid SATCOM model configuration")]
    InvalidConfiguration,
    #[error("invalid SATCOM observation: {0}")]
    InvalidObservation(&'static str),
    #[error(transparent)]
    Statistics(#[from] StatisticsError),
}

pub fn evaluate_observation(
    aircraft: AircraftState,
    bias: &mut BfoBiasState,
    observation: &SatcomObservation,
    satellite_afc_hz: f64,
    use_bfo: bool,
    config: &SatcomModelConfig,
) -> Result<ObservationFit, SatcomModelError> {
    config.validate()?;
    observation
        .validate()
        .map_err(SatcomModelError::InvalidObservation)?;
    if !satellite_afc_hz.is_finite() {
        return Err(SatcomModelError::InvalidObservation(
            "satellite correction is not finite",
        ));
    }

    let mut fit = ObservationFit {
        log_likelihood: 0.0,
        predicted_bto_us: None,
        bto_residual_us: None,
        predicted_bfo_without_bias_hz: None,
        bfo_innovation_hz: None,
    };

    if let (Some(observed), Some(sd)) = (observation.bto, observation.bto_sd) {
        let predicted = bto(
            aircraft.position,
            aircraft.altitude.0,
            observation.satellite_position_km,
            observation.ground_station_position_km,
            config.bto,
        )
        .0;
        let residual = observed.0 - predicted;
        fit.log_likelihood += normal_log_density(residual, sd.0)?;
        fit.predicted_bto_us = Some(predicted);
        fit.bto_residual_us = Some(residual);
    }

    if use_bfo {
        if let (Some(observed), Some(sd)) = (observation.bfo, observation.bfo_sd) {
            let mut constants = config.bfo;
            constants.satellite_afc_hz = satellite_afc_hz;
            let predicted = bfo_components(
                aircraft,
                observation.satellite_position_km,
                observation.satellite_velocity_km_s,
                observation.ground_station_position_km,
                constants,
            )
            .base_without_bias
            .0;
            let (increment, innovation, updated) =
                bfo_bias_predictive_update(*bias, observed.0, predicted, sd.0)?;
            fit.log_likelihood += increment;
            fit.predicted_bfo_without_bias_hz = Some(predicted);
            fit.bfo_innovation_hz = Some(innovation);
            *bias = updated;
        }
    }
    Ok(fit)
}

#[cfg(test)]
mod tests {
    use mh370_domain::{
        Degrees, Feet, FeetPerMinute, Hertz, Knots, LatLon, Microseconds, Seconds, Vec3,
    };

    use super::*;

    fn config() -> SatcomModelConfig {
        SatcomModelConfig {
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
        }
    }

    #[test]
    fn predictive_frequency_update_changes_only_bias_state() {
        let aircraft = AircraftState {
            time: Seconds(0.0),
            position: LatLon::new(-20.0, 90.0).unwrap(),
            altitude: Feet(35_000.0),
            track_true: Degrees(180.0),
            ground_speed: Knots(480.0),
            vertical_speed: FeetPerMinute(0.0),
            bfo_bias: Hertz(150.0),
        };
        let observation = SatcomObservation {
            time: Seconds(0.0),
            satellite_position_km: Vec3::new(18_161.0, 38_060.0, 1_029.0),
            satellite_velocity_km_s: Vec3::new(0.002, -0.001, -0.046),
            ground_station_position_km: Vec3::new(-2_368.8, 4_881.1, -3_342.0),
            bto: Some(Microseconds(12_000.0)),
            bto_sd: Some(Microseconds(29.0)),
            bfo: Some(Hertz(170.0)),
            bfo_sd: Some(Hertz(7.0)),
        };
        let mut bias = config().initial_bias();
        let prior_variance = bias.variance_hz2;
        let fit = evaluate_observation(aircraft, &mut bias, &observation, -18.0, true, &config())
            .unwrap();
        assert!(fit.log_likelihood.is_finite());
        assert!(fit.bto_residual_us.is_some());
        assert!(fit.bfo_innovation_hz.is_some());
        assert!(bias.variance_hz2 < prior_variance);
    }
}
