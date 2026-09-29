use serde::{Deserialize, Serialize};

use crate::{Hertz, Microseconds, Seconds, Vec3};

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct SatcomObservation {
    pub time: Seconds,
    /// Earth-centred Earth-fixed satellite position in kilometres.
    pub satellite_position_km: Vec3,
    /// Earth-centred Earth-fixed satellite velocity in kilometres per second.
    pub satellite_velocity_km_s: Vec3,
    /// Earth-centred Earth-fixed ground-earth-station position in kilometres.
    pub ground_station_position_km: Vec3,
    pub bto: Option<Microseconds>,
    pub bto_sd: Option<Microseconds>,
    pub bfo: Option<Hertz>,
    pub bfo_sd: Option<Hertz>,
}

impl SatcomObservation {
    pub fn validate(&self) -> Result<(), &'static str> {
        if !self.time.is_finite()
            || !self.satellite_position_km.is_finite()
            || !self.satellite_velocity_km_s.is_finite()
            || !self.ground_station_position_km.is_finite()
        {
            return Err("non-finite observation geometry");
        }
        match (self.bto, self.bto_sd) {
            (Some(value), Some(sd)) if value.is_finite() && sd.0 > 0.0 && sd.is_finite() => {}
            (None, None) => {}
            _ => return Err("BTO value and positive SD must appear together"),
        }
        match (self.bfo, self.bfo_sd) {
            (Some(value), Some(sd)) if value.is_finite() && sd.0 > 0.0 && sd.is_finite() => {}
            (None, None) => {}
            _ => return Err("BFO value and positive SD must appear together"),
        }
        if self.bto.is_none() && self.bfo.is_none() {
            return Err("observation must contain BTO or BFO");
        }
        Ok(())
    }
}
