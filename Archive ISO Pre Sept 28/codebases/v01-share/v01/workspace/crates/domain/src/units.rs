use serde::{Deserialize, Serialize};
use thiserror::Error;

macro_rules! scalar_unit {
    ($name:ident) => {
        #[derive(Debug, Clone, Copy, Default, PartialEq, PartialOrd, Serialize, Deserialize)]
        #[serde(transparent)]
        pub struct $name(pub f64);

        impl $name {
            pub const fn new(value: f64) -> Self {
                Self(value)
            }

            pub const fn value(self) -> f64 {
                self.0
            }

            pub fn is_finite(self) -> bool {
                self.0.is_finite()
            }
        }
    };
}

scalar_unit!(Feet);
scalar_unit!(FeetPerMinute);
scalar_unit!(Hertz);
scalar_unit!(Kilometers);
scalar_unit!(Knots);
scalar_unit!(Microseconds);
scalar_unit!(NauticalMiles);
scalar_unit!(Seconds);

#[derive(Debug, Clone, Copy, Default, PartialEq, PartialOrd, Serialize, Deserialize)]
#[serde(transparent)]
pub struct Degrees(pub f64);

impl Degrees {
    pub const fn new(value: f64) -> Self {
        Self(value)
    }

    pub const fn value(self) -> f64 {
        self.0
    }

    pub fn is_finite(self) -> bool {
        self.0.is_finite()
    }

    pub fn wrapped_180(self) -> Self {
        Self((self.0 + 180.0).rem_euclid(360.0) - 180.0)
    }

    pub fn wrapped_360(self) -> Self {
        Self(self.0.rem_euclid(360.0))
    }

    pub fn to_radians(self) -> f64 {
        self.0.to_radians()
    }
}

#[derive(Debug, Clone, Copy, PartialEq, Serialize, Deserialize)]
pub struct LatLon {
    pub latitude: Degrees,
    pub longitude: Degrees,
}

impl LatLon {
    pub fn new(latitude_deg: f64, longitude_deg: f64) -> Result<Self, UnitError> {
        if !latitude_deg.is_finite() || !longitude_deg.is_finite() {
            return Err(UnitError::NonFiniteCoordinate);
        }
        if !(-90.0..=90.0).contains(&latitude_deg) {
            return Err(UnitError::LatitudeOutOfRange(latitude_deg));
        }
        Ok(Self {
            latitude: Degrees(latitude_deg),
            longitude: Degrees(longitude_deg).wrapped_180(),
        })
    }

    pub fn new_unchecked(latitude_deg: f64, longitude_deg: f64) -> Self {
        debug_assert!(latitude_deg.is_finite());
        debug_assert!((-90.0..=90.0).contains(&latitude_deg));
        Self {
            latitude: Degrees(latitude_deg),
            longitude: Degrees(longitude_deg).wrapped_180(),
        }
    }
}

#[derive(Debug, Error, Clone, PartialEq)]
pub enum UnitError {
    #[error("coordinate is not finite")]
    NonFiniteCoordinate,
    #[error("latitude {0} is outside [-90, 90] degrees")]
    LatitudeOutOfRange(f64),
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn longitude_and_bearing_wrap_at_declared_boundaries() {
        assert_eq!(Degrees(360.0).wrapped_360(), Degrees(0.0));
        assert_eq!(Degrees(-1.0).wrapped_360(), Degrees(359.0));
        assert_eq!(Degrees(180.0).wrapped_180(), Degrees(-180.0));
        assert_eq!(Degrees(541.0).wrapped_180(), Degrees(-179.0));
    }

    #[test]
    fn latitude_is_validated_and_longitude_is_normalized() {
        assert_eq!(
            LatLon::new(-35.0, 190.0).unwrap(),
            LatLon {
                latitude: Degrees(-35.0),
                longitude: Degrees(-170.0),
            }
        );
        assert_eq!(
            LatLon::new(91.0, 0.0),
            Err(UnitError::LatitudeOutOfRange(91.0))
        );
        assert_eq!(
            LatLon::new(f64::NAN, 0.0),
            Err(UnitError::NonFiniteCoordinate)
        );
    }
}
