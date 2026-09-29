use serde::{Deserialize, Serialize};

use crate::{Degrees, LatLon, NauticalMiles, Seconds};

#[derive(Debug, Clone, Copy, PartialEq, Serialize, Deserialize)]
pub struct ImpactPoint {
    pub time: Seconds,
    pub position: LatLon,
    pub bearing_true: Degrees,
    pub displacement_from_last_contact: NauticalMiles,
}
