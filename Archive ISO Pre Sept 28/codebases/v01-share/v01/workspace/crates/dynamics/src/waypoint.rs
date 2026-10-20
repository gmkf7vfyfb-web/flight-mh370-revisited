use mh370_domain::{Degrees, LatLon, NauticalMiles, KM_PER_NM, WGS84_A_KM, WGS84_B_KM, WGS84_F};
use serde::{Deserialize, Serialize};
use thiserror::Error;

use crate::LateralMode;

const INVERSE_TOLERANCE_RAD: f64 = 1e-13;
const MAX_INVERSE_ITERATIONS: usize = 100;

/// A single direct-to leg with no implicit route continuation after arrival.
///
/// `arrival_radius` is deliberately part of the typed leg. Propagation reports
/// route completion before entering that radius rather than silently flying
/// through the fix or inventing a subsequent leg.
#[derive(Debug, Clone, Copy, PartialEq, Serialize, Deserialize)]
pub struct FixedWaypointLeg {
    pub waypoint: LatLon,
    pub arrival_radius: NauticalMiles,
}

impl FixedWaypointLeg {
    pub fn new(waypoint: LatLon, arrival_radius: NauticalMiles) -> Result<Self, WaypointError> {
        let leg = Self {
            waypoint,
            arrival_radius,
        };
        leg.validate()?;
        Ok(leg)
    }

    pub fn validate(self) -> Result<(), WaypointError> {
        if !self.arrival_radius.is_finite() || self.arrival_radius.0 <= 0.0 {
            return Err(WaypointError::InvalidArrivalRadius);
        }
        Ok(())
    }
}

/// Guidance selected for the environment-aware one-turn trajectory.
///
/// A direct-to trajectory retains constant true track on the known initial
/// radar leg, then changes to the fixed-waypoint leg at the sampled turn time.
#[derive(Debug, Clone, Copy, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum LateralGuidance {
    SelectedControl(LateralMode),
    DirectTo(FixedWaypointLeg),
}

impl Default for LateralGuidance {
    fn default() -> Self {
        Self::SelectedControl(LateralMode::ConstantTrueTrack)
    }
}

impl LateralGuidance {
    pub fn validate(self) -> Result<(), WaypointError> {
        match self {
            Self::SelectedControl(LateralMode::LateralNavigation) => {
                Err(WaypointError::UntypedLateralNavigation)
            }
            Self::SelectedControl(_) => Ok(()),
            Self::DirectTo(leg) => leg.validate(),
        }
    }

    pub const fn lateral_mode(self) -> LateralMode {
        match self {
            Self::SelectedControl(mode) => mode,
            Self::DirectTo(_) => LateralMode::LateralNavigation,
        }
    }

    pub const fn direct_to_leg(self) -> Option<FixedWaypointLeg> {
        match self {
            Self::DirectTo(leg) => Some(leg),
            Self::SelectedControl(_) => None,
        }
    }
}

#[derive(Debug, Clone, Copy, PartialEq, Serialize, Deserialize)]
pub struct FixedWaypointGuidance {
    pub track_true: Degrees,
    pub distance_remaining: NauticalMiles,
}

#[derive(Debug, Error)]
pub enum WaypointError {
    #[error("fixed-waypoint arrival radius must be finite and positive")]
    InvalidArrivalRadius,
    #[error("the lateral-navigation placeholder is not a typed selected control")]
    UntypedLateralNavigation,
    #[error("WGS84 inverse geodesic did not converge")]
    InverseDidNotConverge,
    #[error(
        "fixed-waypoint leg is complete at {distance_remaining_nm:.6} NM remaining (arrival radius {arrival_radius_nm:.6} NM)"
    )]
    LegComplete {
        distance_remaining_nm: f64,
        arrival_radius_nm: f64,
    },
    #[error(
        "fixed-waypoint leg would complete during the next integration step: {distance_remaining_nm:.6} NM remaining, {step_distance_nm:.6} NM step, {arrival_radius_nm:.6} NM arrival radius"
    )]
    LegCompletesDuringStep {
        distance_remaining_nm: f64,
        step_distance_nm: f64,
        arrival_radius_nm: f64,
    },
}

/// Return the ellipsoidal track and remaining distance for a direct-to leg.
///
/// This is the Vincenty inverse solution paired with the repository's WGS84
/// direct propagator. The bearing is recomputed from the current position at
/// every integration step so the commanded track follows the geodesic rather
/// than preserving its initial course as a rhumb line.
pub fn fixed_waypoint_guidance(
    position: LatLon,
    leg: FixedWaypointLeg,
) -> Result<FixedWaypointGuidance, WaypointError> {
    leg.validate()?;
    let guidance = inverse_wgs84(position, leg.waypoint)?;
    if guidance.distance_remaining.0 <= leg.arrival_radius.0 {
        return Err(WaypointError::LegComplete {
            distance_remaining_nm: guidance.distance_remaining.0,
            arrival_radius_nm: leg.arrival_radius.0,
        });
    }
    Ok(guidance)
}

fn inverse_wgs84(
    start: LatLon,
    destination: LatLon,
) -> Result<FixedWaypointGuidance, WaypointError> {
    let phi_1 = start.latitude.to_radians();
    let phi_2 = destination.latitude.to_radians();
    let longitude_delta = Degrees(destination.longitude.0 - start.longitude.0)
        .wrapped_180()
        .to_radians();
    let reduced_1 = ((1.0 - WGS84_F) * phi_1.tan()).atan();
    let reduced_2 = ((1.0 - WGS84_F) * phi_2.tan()).atan();
    let (sin_reduced_1, cos_reduced_1) = reduced_1.sin_cos();
    let (sin_reduced_2, cos_reduced_2) = reduced_2.sin_cos();

    let mut lambda = longitude_delta;
    let mut converged = false;
    for _ in 0..MAX_INVERSE_ITERATIONS {
        let (sin_lambda, cos_lambda) = lambda.sin_cos();
        let first = cos_reduced_2 * sin_lambda;
        let second = cos_reduced_1 * sin_reduced_2 - sin_reduced_1 * cos_reduced_2 * cos_lambda;
        let sin_sigma = first.hypot(second);
        if sin_sigma <= f64::EPSILON {
            return Ok(FixedWaypointGuidance {
                track_true: Degrees(0.0),
                distance_remaining: NauticalMiles(0.0),
            });
        }
        let cos_sigma = sin_reduced_1 * sin_reduced_2 + cos_reduced_1 * cos_reduced_2 * cos_lambda;
        let sigma = sin_sigma.atan2(cos_sigma);
        let sin_alpha = cos_reduced_1 * cos_reduced_2 * sin_lambda / sin_sigma;
        let cos_sq_alpha = (1.0 - sin_alpha.powi(2)).max(0.0);
        let cos_two_sigma_m = if cos_sq_alpha > f64::EPSILON {
            cos_sigma - 2.0 * sin_reduced_1 * sin_reduced_2 / cos_sq_alpha
        } else {
            0.0
        };
        let coefficient_c =
            WGS84_F / 16.0 * cos_sq_alpha * (4.0 + WGS84_F * (4.0 - 3.0 * cos_sq_alpha));
        let updated_lambda = longitude_delta
            + (1.0 - coefficient_c)
                * WGS84_F
                * sin_alpha
                * (sigma
                    + coefficient_c
                        * sin_sigma
                        * (cos_two_sigma_m
                            + coefficient_c * cos_sigma * (-1.0 + 2.0 * cos_two_sigma_m.powi(2))));
        if (updated_lambda - lambda).abs() <= INVERSE_TOLERANCE_RAD {
            lambda = updated_lambda;
            converged = true;
            break;
        }
        lambda = updated_lambda;
    }
    if !converged {
        return Err(WaypointError::InverseDidNotConverge);
    }

    let (sin_lambda, cos_lambda) = lambda.sin_cos();
    let first = cos_reduced_2 * sin_lambda;
    let second = cos_reduced_1 * sin_reduced_2 - sin_reduced_1 * cos_reduced_2 * cos_lambda;
    let sin_sigma = first.hypot(second);
    let cos_sigma = sin_reduced_1 * sin_reduced_2 + cos_reduced_1 * cos_reduced_2 * cos_lambda;
    let sigma = sin_sigma.atan2(cos_sigma);
    let sin_alpha = cos_reduced_1 * cos_reduced_2 * sin_lambda / sin_sigma;
    let cos_sq_alpha = (1.0 - sin_alpha.powi(2)).max(0.0);
    let cos_two_sigma_m = if cos_sq_alpha > f64::EPSILON {
        cos_sigma - 2.0 * sin_reduced_1 * sin_reduced_2 / cos_sq_alpha
    } else {
        0.0
    };

    let u_sq = cos_sq_alpha * (WGS84_A_KM.powi(2) - WGS84_B_KM.powi(2)) / WGS84_B_KM.powi(2);
    let coefficient_a =
        1.0 + u_sq / 16_384.0 * (4_096.0 + u_sq * (-768.0 + u_sq * (320.0 - 175.0 * u_sq)));
    let coefficient_b = u_sq / 1_024.0 * (256.0 + u_sq * (-128.0 + u_sq * (74.0 - 47.0 * u_sq)));
    let delta_sigma = coefficient_b
        * sin_sigma
        * (cos_two_sigma_m
            + coefficient_b / 4.0
                * (cos_sigma * (-1.0 + 2.0 * cos_two_sigma_m.powi(2))
                    - coefficient_b / 6.0
                        * cos_two_sigma_m
                        * (-3.0 + 4.0 * sin_sigma.powi(2))
                        * (-3.0 + 4.0 * cos_two_sigma_m.powi(2))));
    let distance_nm = WGS84_B_KM * coefficient_a * (sigma - delta_sigma) / KM_PER_NM;
    let track_true = Degrees(
        (cos_reduced_2 * sin_lambda)
            .atan2(cos_reduced_1 * sin_reduced_2 - sin_reduced_1 * cos_reduced_2 * cos_lambda)
            .to_degrees(),
    )
    .wrapped_360();
    Ok(FixedWaypointGuidance {
        track_true,
        distance_remaining: NauticalMiles(distance_nm),
    })
}

#[cfg(test)]
mod tests {
    use approx::assert_abs_diff_eq;
    use mh370_domain::{destination_wgs84, great_circle_distance_nm};

    use super::*;

    #[test]
    fn inverse_wgs84_matches_vincenty_flinders_peak_benchmark() {
        let flinders_peak = LatLon::new(
            -(37.0 + 57.0 / 60.0 + 3.720_30 / 3_600.0),
            144.0 + 25.0 / 60.0 + 29.524_40 / 3_600.0,
        )
        .unwrap();
        let buninyong = LatLon::new(
            -(37.0 + 39.0 / 60.0 + 10.156_10 / 3_600.0),
            143.0 + 55.0 / 60.0 + 35.383_90 / 3_600.0,
        )
        .unwrap();
        let guidance = inverse_wgs84(flinders_peak, buninyong).unwrap();
        assert_abs_diff_eq!(
            guidance.distance_remaining.0 * KM_PER_NM * 1_000.0,
            54_972.271,
            epsilon = 0.002
        );
        assert_abs_diff_eq!(
            guidance.track_true.0,
            306.0 + 52.0 / 60.0 + 5.37 / 3_600.0,
            epsilon = 2e-6
        );
    }

    #[test]
    fn guidance_rejects_arrival_instead_of_inventing_a_next_leg() {
        let waypoint = LatLon::new(-35.0, 90.0).unwrap();
        let leg = FixedWaypointLeg::new(waypoint, NauticalMiles(1.0)).unwrap();
        let error = fixed_waypoint_guidance(waypoint, leg).unwrap_err();
        assert!(matches!(error, WaypointError::LegComplete { .. }));
    }

    #[test]
    fn guidance_has_expected_cardinal_tracks_on_equator_and_meridian() {
        let east = fixed_waypoint_guidance(
            LatLon::new(0.0, 0.0).unwrap(),
            FixedWaypointLeg::new(LatLon::new(0.0, 10.0).unwrap(), NauticalMiles(0.1)).unwrap(),
        )
        .unwrap();
        assert_abs_diff_eq!(east.track_true.0, 90.0, epsilon = 1e-12);

        let south = fixed_waypoint_guidance(
            LatLon::new(-10.0, 80.0).unwrap(),
            FixedWaypointLeg::new(LatLon::new(-70.0, 80.0).unwrap(), NauticalMiles(0.1)).unwrap(),
        )
        .unwrap();
        assert_abs_diff_eq!(south.track_true.0, 180.0, epsilon = 1e-12);
    }

    #[test]
    fn configured_long_polar_davis_leg_matches_geographiclib_and_closes() {
        let start = LatLon::new(-0.612_051_25, 93.646_546_89).unwrap();
        let davis_plateau = LatLon::new(-68.470_60, 78.840_61).unwrap();
        let solution = inverse_wgs84(start, davis_plateau).unwrap();

        // Independent WGS84 result from GeographicLib GeodSolve 2.5.2,
        // precision=9, inverse mode, retrieved 2026-08-31:
        // https://geographiclib.sourceforge.io/cgi-bin/GeodSolve
        // azi1=-174.19137935864606 deg; s12=7614783.893277088 m.
        assert_abs_diff_eq!(
            solution.track_true.0,
            185.808_620_641_353_94,
            epsilon = 2e-9
        );
        assert_abs_diff_eq!(
            solution.distance_remaining.0 * KM_PER_NM * 1_000.0,
            7_614_783.893_277_088,
            epsilon = 0.002
        );

        let flown = NauticalMiles(600.0);
        let intermediate = destination_wgs84(start, solution.track_true, flown).unwrap();
        let remaining = inverse_wgs84(intermediate, davis_plateau).unwrap();
        assert_abs_diff_eq!(
            flown.0 + remaining.distance_remaining.0,
            solution.distance_remaining.0,
            epsilon = 2e-7
        );
        assert!((remaining.track_true.0 - solution.track_true.0).abs() > 0.05);

        let closed =
            destination_wgs84(start, solution.track_true, solution.distance_remaining).unwrap();
        assert!(great_circle_distance_nm(closed, davis_plateau).0 < 2e-7);
    }
}
