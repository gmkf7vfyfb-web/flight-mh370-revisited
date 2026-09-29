use mh370_domain::{
    destination_wgs84, great_circle_distance_nm, AircraftState, Degrees, ImpactPoint,
    NauticalMiles, Seconds,
};
use rand::Rng;
use rand_chacha::ChaCha8Rng;
use rand_distr::{Distribution, StandardNormal};
use serde::{Deserialize, Serialize};
use thiserror::Error;

mod aerodynamic_approximations;
mod exhaustion_boundary;
mod frozen_powered_fuel_projection;
mod fuel_allocation;
mod fuel_performance;
mod kernel;
mod powered_drag_allowance;
mod powered_fuel;
mod powered_segment_feasibility;
mod powered_thrust;
mod systems_timing;

pub use aerodynamic_approximations::*;
pub use exhaustion_boundary::*;
pub use frozen_powered_fuel_projection::*;
pub use fuel_allocation::*;
pub use fuel_performance::*;
pub use kernel::*;
pub use powered_drag_allowance::*;
pub use powered_fuel::*;
pub use powered_segment_feasibility::*;
pub use powered_thrust::*;
pub use systems_timing::*;

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum EndOfFlightMode {
    /// Report the final SATCOM state without claiming an impact displacement.
    LastContact,
    /// Conditional use of the 4.7--8.0 NM local Boeing high-rate envelope.
    BoeingLocalEnvelope,
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct EndOfFlightConfig {
    pub mode: EndOfFlightMode,
    pub minimum_along_track_nm: f64,
    pub maximum_along_track_nm: f64,
    pub cross_track_sd_nm: f64,
    pub minimum_delay_seconds: f64,
    pub maximum_delay_seconds: f64,
}

impl EndOfFlightConfig {
    pub fn validate(&self) -> Result<(), EndOfFlightError> {
        if ![
            self.minimum_along_track_nm,
            self.maximum_along_track_nm,
            self.cross_track_sd_nm,
            self.minimum_delay_seconds,
            self.maximum_delay_seconds,
        ]
        .iter()
        .all(|value| value.is_finite())
            || self.minimum_along_track_nm < 0.0
            || self.maximum_along_track_nm < self.minimum_along_track_nm
            || self.cross_track_sd_nm < 0.0
            || self.minimum_delay_seconds < 0.0
            || self.maximum_delay_seconds < self.minimum_delay_seconds
        {
            return Err(EndOfFlightError::InvalidConfiguration);
        }
        Ok(())
    }
}

#[derive(Debug, Error)]
pub enum EndOfFlightError {
    #[error("invalid end-of-flight configuration")]
    InvalidConfiguration,
    #[error("end-of-flight geodesic projection failed")]
    Geodesy,
}

pub fn project_impact(
    last_contact: AircraftState,
    config: &EndOfFlightConfig,
    rng: &mut ChaCha8Rng,
) -> Result<ImpactPoint, EndOfFlightError> {
    config.validate()?;
    if config.mode == EndOfFlightMode::LastContact {
        return Ok(ImpactPoint {
            time: last_contact.time,
            position: last_contact.position,
            bearing_true: last_contact.track_true,
            displacement_from_last_contact: NauticalMiles(0.0),
        });
    }

    let along = if config.maximum_along_track_nm > config.minimum_along_track_nm {
        rng.gen_range(config.minimum_along_track_nm..config.maximum_along_track_nm)
    } else {
        config.minimum_along_track_nm
    };
    let normal_draw: f64 = StandardNormal.sample(rng);
    let cross = config.cross_track_sd_nm * normal_draw;
    let along_position = destination_wgs84(
        last_contact.position,
        last_contact.track_true,
        NauticalMiles(along),
    )
    .map_err(|_| EndOfFlightError::Geodesy)?;
    let cross_bearing =
        Degrees(last_contact.track_true.0 + if cross >= 0.0 { 90.0 } else { -90.0 }).wrapped_360();
    let position = destination_wgs84(along_position, cross_bearing, NauticalMiles(cross.abs()))
        .map_err(|_| EndOfFlightError::Geodesy)?;
    let delay = if config.maximum_delay_seconds > config.minimum_delay_seconds {
        rng.gen_range(config.minimum_delay_seconds..config.maximum_delay_seconds)
    } else {
        config.minimum_delay_seconds
    };
    Ok(ImpactPoint {
        time: Seconds(last_contact.time.0 + delay),
        position,
        bearing_true: last_contact.track_true,
        displacement_from_last_contact: great_circle_distance_nm(last_contact.position, position),
    })
}

#[cfg(test)]
mod tests {
    use mh370_domain::{Feet, FeetPerMinute, Hertz, Knots, LatLon};
    use rand::SeedableRng;

    use super::*;

    fn state() -> AircraftState {
        AircraftState {
            time: Seconds(22_668.0),
            position: LatLon::new(-35.0, 93.0).unwrap(),
            altitude: Feet(20_000.0),
            track_true: Degrees(180.0),
            ground_speed: Knots(480.0),
            vertical_speed: FeetPerMinute(-15_000.0),
            bfo_bias: Hertz(150.0),
        }
    }

    #[test]
    fn last_contact_mode_is_exactly_identity() {
        let mut rng = ChaCha8Rng::seed_from_u64(1);
        let result = project_impact(
            state(),
            &EndOfFlightConfig {
                mode: EndOfFlightMode::LastContact,
                minimum_along_track_nm: 0.0,
                maximum_along_track_nm: 0.0,
                cross_track_sd_nm: 0.0,
                minimum_delay_seconds: 0.0,
                maximum_delay_seconds: 0.0,
            },
            &mut rng,
        )
        .unwrap();
        assert_eq!(result.position, state().position);
        assert_eq!(result.displacement_from_last_contact.0, 0.0);
    }

    #[test]
    fn conditional_boeing_projection_is_local_and_repeatable() {
        let config = EndOfFlightConfig {
            mode: EndOfFlightMode::BoeingLocalEnvelope,
            minimum_along_track_nm: 4.7,
            maximum_along_track_nm: 8.0,
            cross_track_sd_nm: 0.5,
            minimum_delay_seconds: 60.0,
            maximum_delay_seconds: 180.0,
        };
        let mut first_rng = ChaCha8Rng::seed_from_u64(2);
        let mut second_rng = ChaCha8Rng::seed_from_u64(2);
        let first = project_impact(state(), &config, &mut first_rng).unwrap();
        let second = project_impact(state(), &config, &mut second_rng).unwrap();
        assert_eq!(first, second);
        assert!(first.displacement_from_last_contact.0 > 3.0);
        assert!(first.displacement_from_last_contact.0 < 10.0);
    }
}
