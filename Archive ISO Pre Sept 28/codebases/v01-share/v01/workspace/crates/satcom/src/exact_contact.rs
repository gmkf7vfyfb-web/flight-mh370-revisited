use mh370_domain::{AircraftState, Hertz, Microseconds, SatcomObservation, Seconds, Vec3};
use serde::{Deserialize, Serialize};
use thiserror::Error;

use crate::{
    evaluate_observation, normal_log_density, BfoBiasState, PropagatedSatelliteEcefState,
    SatcomModelConfig, SatcomModelError, SatelliteEcefPropagationError,
    SatelliteEcefPropagationLimit, SatelliteEcefState,
};

/// Optional frequency datum associated with an exact-time SATCOM contact.
#[derive(Debug, Clone, Copy, PartialEq, Serialize, Deserialize)]
pub struct ExactTimeBfoDatum {
    pub observed: Hertz,
    pub standard_deviation: Hertz,
    pub satellite_afc: Hertz,
}

/// Geometry and measurements needed to score one exact-time SATCOM contact.
///
/// `satellite_source_epoch` and `aircraft.time` must use the same time basis.
/// The contact epoch is the source epoch plus `satellite_delta`.
#[derive(Debug, Clone, Copy, PartialEq, Serialize, Deserialize)]
pub struct ExactTimeSatcomContact {
    pub satellite_source_epoch: Seconds,
    pub satellite_source_state: SatelliteEcefState,
    pub satellite_delta: Seconds,
    pub satellite_propagation_limit: SatelliteEcefPropagationLimit,
    pub ground_station_position_km: Vec3,
    pub observed_bto: Microseconds,
    pub bto_standard_deviation: Microseconds,
    pub bfo: Option<ExactTimeBfoDatum>,
}

#[derive(Debug, Clone, Copy, PartialEq, Serialize, Deserialize)]
pub struct ExactTimeBtoFit {
    pub predicted: Microseconds,
    pub residual: Microseconds,
    pub log_likelihood: f64,
}

#[derive(Debug, Clone, Copy, PartialEq, Serialize, Deserialize)]
pub struct ExactTimeBfoFit {
    pub predicted_without_bias: Hertz,
    pub innovation: Hertz,
    pub log_likelihood: f64,
    pub updated_bias: BfoBiasState,
}

/// Pure result of scoring one exact-time contact.
///
/// This type deliberately carries no evidence identifier or consumption state;
/// evidence ownership remains with the estimator/runner ledger.
#[derive(Debug, Clone, Copy, PartialEq, Serialize, Deserialize)]
pub struct ExactTimeSatcomContactFit {
    pub source_epoch: Seconds,
    pub contact_epoch: Seconds,
    pub propagated_satellite: PropagatedSatelliteEcefState,
    pub bto: ExactTimeBtoFit,
    pub bfo: Option<ExactTimeBfoFit>,
    pub total_log_likelihood: f64,
}

#[derive(Debug, Error)]
pub enum ExactTimeSatcomContactError {
    #[error("aircraft state must be finite")]
    NonFiniteAircraftState,
    #[error("BFO bias mean must be finite and variance must be finite and non-negative")]
    InvalidBfoBiasState,
    #[error("aircraft BFO bias mean differs from the supplied full BFO bias state")]
    AircraftBiasMeanMismatch,
    #[error("satellite source epoch must be finite")]
    NonFiniteSourceEpoch,
    #[error("satellite source epoch plus propagation delta is not finite")]
    NonFiniteContactEpoch,
    #[error(
        "aircraft epoch {aircraft_seconds} s differs from propagated contact epoch {contact_seconds} s"
    )]
    AircraftEpochMismatch {
        aircraft_seconds: f64,
        contact_seconds: f64,
    },
    #[error(transparent)]
    SatellitePropagation(#[from] SatelliteEcefPropagationError),
    #[error(transparent)]
    SatcomModel(#[from] SatcomModelError),
    #[error("SATCOM model omitted a required fit component")]
    MissingFitComponent,
}

fn epochs_match(left: f64, right: f64) -> bool {
    let scale = left.abs().max(right.abs()).max(1.0);
    (left - right).abs() <= 8.0 * f64::EPSILON * scale
}

/// Score a contact after bounded constant-velocity propagation of its source
/// satellite ephemeris state.
///
/// The function is side-effect free: the supplied bias is copied, any update
/// is returned in `ExactTimeBfoFit`, and no evidence ledger is consumed.
pub fn score_exact_time_satcom_contact(
    aircraft: AircraftState,
    bfo_bias: BfoBiasState,
    contact: ExactTimeSatcomContact,
    config: &SatcomModelConfig,
) -> Result<ExactTimeSatcomContactFit, ExactTimeSatcomContactError> {
    if !aircraft.all_finite() {
        return Err(ExactTimeSatcomContactError::NonFiniteAircraftState);
    }
    if !bfo_bias.mean_hz.is_finite()
        || !bfo_bias.variance_hz2.is_finite()
        || bfo_bias.variance_hz2 < 0.0
    {
        return Err(ExactTimeSatcomContactError::InvalidBfoBiasState);
    }
    if aircraft.bfo_bias.0 != bfo_bias.mean_hz {
        return Err(ExactTimeSatcomContactError::AircraftBiasMeanMismatch);
    }
    if !contact.satellite_source_epoch.is_finite() {
        return Err(ExactTimeSatcomContactError::NonFiniteSourceEpoch);
    }

    let propagated_satellite = crate::propagate_satellite_ecef_constant_velocity(
        contact.satellite_source_state,
        contact.satellite_delta,
        contact.satellite_propagation_limit,
    )?;
    let contact_epoch = Seconds(contact.satellite_source_epoch.0 + contact.satellite_delta.0);
    if !contact_epoch.is_finite() {
        return Err(ExactTimeSatcomContactError::NonFiniteContactEpoch);
    }
    if !epochs_match(aircraft.time.0, contact_epoch.0) {
        return Err(ExactTimeSatcomContactError::AircraftEpochMismatch {
            aircraft_seconds: aircraft.time.0,
            contact_seconds: contact_epoch.0,
        });
    }

    let (observed_bfo, bfo_standard_deviation, satellite_afc_hz, use_bfo) = match contact.bfo {
        Some(datum) => (
            Some(datum.observed),
            Some(datum.standard_deviation),
            datum.satellite_afc.0,
            true,
        ),
        None => (None, None, 0.0, false),
    };
    let observation = SatcomObservation {
        time: contact_epoch,
        satellite_position_km: propagated_satellite.state.position_km,
        satellite_velocity_km_s: propagated_satellite.state.velocity_km_s,
        ground_station_position_km: contact.ground_station_position_km,
        bto: Some(contact.observed_bto),
        bto_sd: Some(contact.bto_standard_deviation),
        bfo: observed_bfo,
        bfo_sd: bfo_standard_deviation,
    };
    let mut updated_bias = bfo_bias;
    let fit = evaluate_observation(
        aircraft,
        &mut updated_bias,
        &observation,
        satellite_afc_hz,
        use_bfo,
        config,
    )?;

    let predicted_bto = fit
        .predicted_bto_us
        .ok_or(ExactTimeSatcomContactError::MissingFitComponent)?;
    let bto_residual = fit
        .bto_residual_us
        .ok_or(ExactTimeSatcomContactError::MissingFitComponent)?;
    let bto_log_likelihood = normal_log_density(bto_residual, contact.bto_standard_deviation.0)
        .map_err(SatcomModelError::Statistics)?;
    let bto = ExactTimeBtoFit {
        predicted: Microseconds(predicted_bto),
        residual: Microseconds(bto_residual),
        log_likelihood: bto_log_likelihood,
    };

    let bfo = if use_bfo {
        Some(ExactTimeBfoFit {
            predicted_without_bias: Hertz(
                fit.predicted_bfo_without_bias_hz
                    .ok_or(ExactTimeSatcomContactError::MissingFitComponent)?,
            ),
            innovation: Hertz(
                fit.bfo_innovation_hz
                    .ok_or(ExactTimeSatcomContactError::MissingFitComponent)?,
            ),
            log_likelihood: fit.log_likelihood - bto_log_likelihood,
            updated_bias,
        })
    } else {
        None
    };

    Ok(ExactTimeSatcomContactFit {
        source_epoch: contact.satellite_source_epoch,
        contact_epoch,
        propagated_satellite,
        bto,
        bfo,
        total_log_likelihood: fit.log_likelihood,
    })
}

#[cfg(test)]
mod tests {
    use approx::assert_abs_diff_eq;
    use mh370_domain::{Degrees, Feet, FeetPerMinute, Knots, LatLon};

    use super::*;
    use crate::{BfoConstants, BtoConstants, SatelliteEphemerisApproximation};

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

    fn aircraft(time_seconds: f64) -> AircraftState {
        AircraftState {
            time: Seconds(time_seconds),
            position: LatLon::new(-20.0, 90.0).unwrap(),
            altitude: Feet(35_000.0),
            track_true: Degrees(180.0),
            ground_speed: Knots(480.0),
            vertical_speed: FeetPerMinute(-500.0),
            bfo_bias: Hertz(150.0),
        }
    }

    fn source_satellite() -> SatelliteEcefState {
        SatelliteEcefState {
            position_km: Vec3::new(18_161.0, 38_060.0, 1_029.0),
            velocity_km_s: Vec3::new(0.002, -0.001, -0.046),
        }
    }

    fn limit(seconds: f64) -> SatelliteEcefPropagationLimit {
        SatelliteEcefPropagationLimit {
            maximum_absolute_delta: Seconds(seconds),
        }
    }

    #[test]
    fn zero_delta_fit_is_analytically_equivalent_to_existing_observation_api() {
        let aircraft = aircraft(100.0);
        let initial_bias = config().initial_bias();
        let source = source_satellite();
        let ground = Vec3::new(-2_368.8, 4_881.1, -3_342.0);
        let datum = ExactTimeSatcomContact {
            satellite_source_epoch: Seconds(100.0),
            satellite_source_state: source,
            satellite_delta: Seconds(0.0),
            satellite_propagation_limit: limit(0.5),
            ground_station_position_km: ground,
            observed_bto: Microseconds(12_000.0),
            bto_standard_deviation: Microseconds(29.0),
            bfo: Some(ExactTimeBfoDatum {
                observed: Hertz(170.0),
                standard_deviation: Hertz(7.0),
                satellite_afc: Hertz(-18.0),
            }),
        };
        let exact =
            score_exact_time_satcom_contact(aircraft, initial_bias, datum, &config()).unwrap();

        let observation = SatcomObservation {
            time: Seconds(100.0),
            satellite_position_km: source.position_km,
            satellite_velocity_km_s: source.velocity_km_s,
            ground_station_position_km: ground,
            bto: Some(datum.observed_bto),
            bto_sd: Some(datum.bto_standard_deviation),
            bfo: datum.bfo.map(|value| value.observed),
            bfo_sd: datum.bfo.map(|value| value.standard_deviation),
        };
        let mut legacy_bias = initial_bias;
        let legacy = evaluate_observation(
            aircraft,
            &mut legacy_bias,
            &observation,
            -18.0,
            true,
            &config(),
        )
        .unwrap();
        let exact_bfo = exact.bfo.unwrap();

        assert_eq!(exact.propagated_satellite.state, source);
        assert_abs_diff_eq!(
            exact.bto.predicted.0,
            legacy.predicted_bto_us.unwrap(),
            epsilon = 1e-12
        );
        assert_abs_diff_eq!(
            exact.bto.residual.0,
            legacy.bto_residual_us.unwrap(),
            epsilon = 1e-12
        );
        assert_abs_diff_eq!(
            exact_bfo.predicted_without_bias.0,
            legacy.predicted_bfo_without_bias_hz.unwrap(),
            epsilon = 1e-12
        );
        assert_abs_diff_eq!(
            exact_bfo.innovation.0,
            legacy.bfo_innovation_hz.unwrap(),
            epsilon = 1e-12
        );
        assert_abs_diff_eq!(
            exact.total_log_likelihood,
            legacy.log_likelihood,
            epsilon = 1e-12
        );
        assert_eq!(exact_bfo.updated_bias, legacy_bias);
    }

    #[test]
    fn subsecond_bto_only_contact_propagates_0416_seconds_before_scoring() {
        let delta_seconds = 0.416;
        let expected_displacement_km = 0.034_621;
        let source = SatelliteEcefState {
            position_km: Vec3::new(18_000.0, 38_000.0, 400.0),
            velocity_km_s: Vec3::new(expected_displacement_km / delta_seconds, 0.0, 0.0),
        };
        let initial_bias = config().initial_bias();
        let fit = score_exact_time_satcom_contact(
            aircraft(22_660.416),
            initial_bias,
            ExactTimeSatcomContact {
                satellite_source_epoch: Seconds(22_660.0),
                satellite_source_state: source,
                satellite_delta: Seconds(delta_seconds),
                satellite_propagation_limit: limit(0.5),
                ground_station_position_km: Vec3::new(-2_368.8, 4_881.1, -3_342.0),
                observed_bto: Microseconds(18_400.0),
                bto_standard_deviation: Microseconds(63.0),
                bfo: None,
            },
            &config(),
        )
        .unwrap();

        assert_eq!(fit.source_epoch, Seconds(22_660.0));
        assert_eq!(fit.contact_epoch, Seconds(22_660.416));
        assert_abs_diff_eq!(
            (fit.propagated_satellite.state.position_km - source.position_km).norm(),
            expected_displacement_km,
            epsilon = 2e-12
        );
        assert_eq!(
            fit.propagated_satellite.state.velocity_km_s,
            source.velocity_km_s
        );
        assert_eq!(
            fit.propagated_satellite.approximation,
            SatelliteEphemerisApproximation::ConstantVelocityEcef
        );
        assert!(fit.bto.predicted.0.is_finite());
        assert!(fit.bto.residual.0.is_finite());
        assert!(fit.bto.log_likelihood.is_finite());
        assert_eq!(fit.bfo, None);
        assert_eq!(fit.total_log_likelihood, fit.bto.log_likelihood);
    }

    #[test]
    fn epoch_and_bias_mismatches_are_rejected_before_scoring() {
        let mut datum = ExactTimeSatcomContact {
            satellite_source_epoch: Seconds(100.0),
            satellite_source_state: source_satellite(),
            satellite_delta: Seconds(0.25),
            satellite_propagation_limit: limit(0.5),
            ground_station_position_km: Vec3::new(-2_368.8, 4_881.1, -3_342.0),
            observed_bto: Microseconds(12_000.0),
            bto_standard_deviation: Microseconds(29.0),
            bfo: None,
        };
        let initial_bias = config().initial_bias();
        assert!(matches!(
            score_exact_time_satcom_contact(aircraft(100.0), initial_bias, datum, &config()),
            Err(ExactTimeSatcomContactError::AircraftEpochMismatch { .. })
        ));

        datum.satellite_delta = Seconds(0.0);
        let mismatched_bias = BfoBiasState {
            mean_hz: 151.0,
            ..initial_bias
        };
        assert!(matches!(
            score_exact_time_satcom_contact(aircraft(100.0), mismatched_bias, datum, &config()),
            Err(ExactTimeSatcomContactError::AircraftBiasMeanMismatch)
        ));

        let invalid_bias = BfoBiasState {
            variance_hz2: -1.0,
            ..initial_bias
        };
        assert!(matches!(
            score_exact_time_satcom_contact(aircraft(100.0), invalid_bias, datum, &config()),
            Err(ExactTimeSatcomContactError::InvalidBfoBiasState)
        ));
    }
}
