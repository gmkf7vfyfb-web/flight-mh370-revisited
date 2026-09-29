use serde::{Deserialize, Serialize};

use crate::{Degrees, Feet, FeetPerMinute, Hertz, Knots, LatLon, Seconds};

#[derive(Debug, Clone, Copy, PartialEq, Serialize, Deserialize)]
pub struct VelocityEnu {
    pub north: Knots,
    pub east: Knots,
    pub vertical: FeetPerMinute,
}

#[derive(Debug, Clone, Copy, PartialEq, Serialize, Deserialize)]
pub struct AircraftState {
    pub time: Seconds,
    pub position: LatLon,
    pub altitude: Feet,
    pub track_true: Degrees,
    pub ground_speed: Knots,
    pub vertical_speed: FeetPerMinute,
    pub bfo_bias: Hertz,
}

impl AircraftState {
    pub fn velocity_enu(self) -> VelocityEnu {
        let track = self.track_true.to_radians();
        VelocityEnu {
            north: Knots(self.ground_speed.0 * track.cos()),
            east: Knots(self.ground_speed.0 * track.sin()),
            vertical: self.vertical_speed,
        }
    }

    pub fn all_finite(self) -> bool {
        self.time.is_finite()
            && self.position.latitude.is_finite()
            && self.position.longitude.is_finite()
            && self.altitude.is_finite()
            && self.track_true.is_finite()
            && self.ground_speed.is_finite()
            && self.vertical_speed.is_finite()
            && self.bfo_bias.is_finite()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn true_track_resolves_to_north_east_velocity() {
        let state = AircraftState {
            time: Seconds(0.0),
            position: LatLon::new(0.0, 0.0).unwrap(),
            altitude: Feet(35_000.0),
            track_true: Degrees(90.0),
            ground_speed: Knots(480.0),
            vertical_speed: FeetPerMinute(0.0),
            bfo_bias: Hertz(150.0),
        };
        let velocity = state.velocity_enu();
        assert!(velocity.north.0.abs() < 1e-12);
        assert!((velocity.east.0 - 480.0).abs() < 1e-12);
    }
}
