use mh370_domain::{
    AircraftState, Degrees, Feet, FeetPerMinute, Hertz, Knots, LatLon, Seconds, Vec3,
};
use mh370_particle_filter::FilterConfig;
use mh370_satcom::{BfoConstants, BtoConstants};
use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct ExperimentConfig {
    pub schema_version: u32,
    pub name: String,
    pub truth_seed: u64,
    pub filter: FilterConfig,
    pub synthetic: SyntheticScenario,
    pub validation: ValidationThresholds,
}

impl ExperimentConfig {
    pub fn validate(&self) -> Result<(), &'static str> {
        if self.schema_version != 1 {
            return Err("unsupported experiment schema version");
        }
        if self.name.trim().is_empty() {
            return Err("experiment name must not be empty");
        }
        self.filter.validate()?;
        self.synthetic.validate()?;
        self.validation.validate()?;
        if (self.filter.initial_time_s - self.synthetic.initial_time_s).abs() > 1e-12 {
            return Err("filter and synthetic initial times differ");
        }
        Ok(())
    }
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct SyntheticScenario {
    pub epochs: usize,
    pub epoch_interval_s: f64,

    pub initial_time_s: f64,
    pub initial_latitude_deg: f64,
    pub initial_longitude_deg: f64,
    pub initial_altitude_ft: f64,
    pub initial_track_deg: f64,
    pub initial_ground_speed_kt: f64,
    pub initial_vertical_speed_fpm: f64,
    pub initial_bfo_bias_hz: f64,

    pub prior_latitude_sd_deg: f64,
    pub prior_longitude_sd_deg: f64,
    pub prior_track_sd_deg: f64,
    pub prior_ground_speed_sd_kt: f64,
    pub prior_bfo_bias_sd_hz: f64,

    pub process_track_sd_deg_per_sqrt_hour: f64,
    pub process_ground_speed_sd_kt_per_sqrt_hour: f64,
    pub process_bfo_bias_sd_hz_per_sqrt_hour: f64,

    pub bto_sd_us: f64,
    pub bfo_sd_hz: f64,
    pub guide_inflation: f64,

    pub satellite_initial_position_km: Vec3,
    pub satellite_velocity_km_s: Vec3,
    pub ground_station_position_km: Vec3,
    pub bto_constants: BtoConstants,
    pub bfo_constants: BfoConstants,
}

impl SyntheticScenario {
    pub fn validate(&self) -> Result<(), &'static str> {
        if self.epochs < 2 {
            return Err("synthetic scenario requires at least two observation epochs");
        }
        let positive = [
            self.epoch_interval_s,
            self.prior_latitude_sd_deg,
            self.prior_longitude_sd_deg,
            self.prior_track_sd_deg,
            self.prior_ground_speed_sd_kt,
            self.prior_bfo_bias_sd_hz,
            self.bto_sd_us,
            self.bfo_sd_hz,
            self.guide_inflation,
            self.bto_constants.speed_of_light_km_s,
            self.bfo_constants.speed_of_light_km_s,
        ];
        if positive
            .iter()
            .any(|value| !value.is_finite() || *value <= 0.0)
        {
            return Err("declared positive synthetic parameter is invalid");
        }
        let nonnegative = [
            self.process_track_sd_deg_per_sqrt_hour,
            self.process_ground_speed_sd_kt_per_sqrt_hour,
            self.process_bfo_bias_sd_hz_per_sqrt_hour,
        ];
        if nonnegative
            .iter()
            .any(|value| !value.is_finite() || *value < 0.0)
        {
            return Err("declared non-negative process scale is invalid");
        }
        if !self.satellite_initial_position_km.is_finite()
            || !self.satellite_velocity_km_s.is_finite()
            || !self.ground_station_position_km.is_finite()
        {
            return Err("synthetic SATCOM geometry is not finite");
        }
        self.initial_state()
            .map(|_| ())
            .map_err(|_| "synthetic initial state is invalid")
    }

    pub fn initial_state(&self) -> Result<AircraftState, &'static str> {
        let position = LatLon::new(self.initial_latitude_deg, self.initial_longitude_deg)
            .map_err(|_| "initial coordinate is invalid")?;
        let state = AircraftState {
            time: Seconds(self.initial_time_s),
            position,
            altitude: Feet(self.initial_altitude_ft),
            track_true: Degrees(self.initial_track_deg).wrapped_360(),
            ground_speed: Knots(self.initial_ground_speed_kt),
            vertical_speed: FeetPerMinute(self.initial_vertical_speed_fpm),
            bfo_bias: Hertz(self.initial_bfo_bias_hz),
        };
        if state.all_finite() && state.ground_speed.0 > 0.0 {
            Ok(state)
        } else {
            Err("initial aircraft state is invalid")
        }
    }
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct ValidationThresholds {
    pub maximum_final_mean_error_nm: f64,
    pub minimum_mass_within_100_nm: f64,
    pub minimum_final_ess: f64,
}

impl ValidationThresholds {
    pub fn validate(&self) -> Result<(), &'static str> {
        if !self.maximum_final_mean_error_nm.is_finite()
            || self.maximum_final_mean_error_nm <= 0.0
            || !self.minimum_mass_within_100_nm.is_finite()
            || !(0.0..=1.0).contains(&self.minimum_mass_within_100_nm)
            || !self.minimum_final_ess.is_finite()
            || self.minimum_final_ess <= 0.0
        {
            return Err("validation threshold is invalid");
        }
        Ok(())
    }
}
