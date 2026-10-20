//! Shared typed objects for the estimator.
//!
//! Units and coordinate frames are represented explicitly so degrees/radians,
//! feet/kilometres, BTO microseconds, and BFO hertz cannot be silently mixed.

mod geodesy;
mod impact;
mod observation;
mod state;
mod units;
mod vector;

pub use geodesy::{
    destination_sphere, destination_wgs84, great_circle_distance_nm, lla_to_ecef, local_basis,
    GeodesyError, KM_PER_NM, LEGACY_SPHERE_RADIUS_NM, WGS84_A_KM, WGS84_B_KM, WGS84_E2, WGS84_F,
};
pub use impact::ImpactPoint;
pub use observation::SatcomObservation;
pub use state::{AircraftState, VelocityEnu};
pub use units::{
    Degrees, Feet, FeetPerMinute, Hertz, Kilometers, Knots, LatLon, Microseconds, NauticalMiles,
    Seconds, UnitError,
};
pub use vector::Vec3;
