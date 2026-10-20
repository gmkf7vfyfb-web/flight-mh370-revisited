use std::fmt;

#[path = "known_flight_antenna.rs"]
mod antenna_inputs;
pub use antenna_inputs::{
    parse_known_flight_antenna_power, KnownFlightAntennaInputs, KnownFlightAntennaObservation,
    KnownFlightAntennaPowerPackage,
};
use mh370_antenna::{
    evaluate_conditional_power, AircraftAttitude, AntennaError, DirectionalGainGrid,
};
use mh370_domain::{
    destination_wgs84, AircraftState, Degrees, Feet, FeetPerMinute, GeodesyError, Hertz, Knots,
    LatLon, Microseconds, NauticalMiles, SatcomObservation, Seconds, Vec3,
};
use mh370_dynamics::{
    ground_velocity_from_control, propagate_constant_track, DynamicsError, EnvironmentError,
    Era5Grid, IgrfGrid, LateralMode,
};
use mh370_particle_filter::{
    run_filter_with_options, Algorithm, FilterConfig, FilterResult, FilterRunOptions,
    ParticleModel, Proposal, SmcError,
};
use mh370_satcom::{evaluate_observation, BfoBiasState, SatcomModelConfig, SatcomModelError};
use rand::Rng;
use rand_chacha::ChaCha8Rng;
use rand_distr::{Distribution, StandardNormal};
use serde::{Deserialize, Serialize};
use serde_json::Value;
use thiserror::Error;

const PACKAGE_SCHEMA: &str = "mh371-known-flight-package-v2";
const RUN_SCHEMA: &str = "mh370-known-flight-inference-v2";

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct KnownFlightInferenceConfig {
    pub schema_version: u32,
    pub name: String,
    pub model_family: String,
    pub expected_inference_sha256: String,
    pub expected_weather_sha256: String,
    pub expected_magnetic_sha256: String,
    pub expected_package_schema: String,
    pub particles: usize,
    pub seeds: Vec<u64>,
    pub algorithm: Algorithm,
    pub ess_resample_fraction: f64,
    pub prior: KnownFlightPriorConfig,
    pub model: KnownFlightModelConfig,
}

impl KnownFlightInferenceConfig {
    pub fn validate(&self) -> Result<(), &'static str> {
        if self.schema_version != 2 {
            return Err("unsupported known-flight inference schema");
        }
        if self.name.trim().is_empty() || self.model_family.trim().is_empty() {
            return Err("known-flight names must not be empty");
        }
        if self.expected_package_schema != PACKAGE_SCHEMA {
            return Err("known-flight package schema is not supported");
        }
        if !is_sha256(&self.expected_inference_sha256)
            || !is_sha256(&self.expected_weather_sha256)
            || !is_sha256(&self.expected_magnetic_sha256)
        {
            return Err("an expected input SHA-256 is invalid");
        }
        if self.particles < 2 || self.seeds.is_empty() {
            return Err("known-flight particle and seed plan is invalid");
        }
        if self
            .seeds
            .iter()
            .enumerate()
            .any(|(index, value)| self.seeds[..index].contains(value))
        {
            return Err("known-flight seeds must be unique");
        }
        FilterConfig {
            particles: self.particles,
            seed: self.seeds[0],
            algorithm: self.algorithm,
            initial_time_s: 0.0,
            ess_resample_fraction: self.ess_resample_fraction,
        }
        .validate()?;
        self.prior.validate()?;
        self.model.validate()
    }
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct KnownFlightPriorConfig {
    pub mach_min: f64,
    pub mach_max: f64,
    pub altitude_min_ft: f64,
    pub altitude_max_ft: f64,
}

impl KnownFlightPriorConfig {
    fn validate(&self) -> Result<(), &'static str> {
        if ![
            self.mach_min,
            self.mach_max,
            self.altitude_min_ft,
            self.altitude_max_ft,
        ]
        .iter()
        .all(|value| value.is_finite())
            || self.mach_min <= 0.0
            || self.mach_min >= self.mach_max
            || self.altitude_min_ft < 10_000.0
            || self.altitude_min_ft >= self.altitude_max_ft
            || self.altitude_max_ft > 43_000.0
        {
            return Err("known-flight Mach or altitude prior is invalid");
        }
        Ok(())
    }
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct KnownFlightModelConfig {
    pub process_magnetic_heading_sd_deg_per_sqrt_hour: f64,
    pub process_mach_sd_per_sqrt_hour: f64,
    pub process_altitude_sd_ft_per_sqrt_hour: f64,
    pub propagation_step_s: f64,
    pub guide_inflation: f64,
    pub bfo_observation_sd_hz: f64,
    pub ground_station_position_km: Vec3,
    pub satcom: SatcomModelConfig,
    #[serde(default)]
    pub antenna: Option<KnownFlightAntennaConfig>,
}

impl KnownFlightModelConfig {
    fn validate(&self) -> Result<(), &'static str> {
        if ![
            self.propagation_step_s,
            self.guide_inflation,
            self.bfo_observation_sd_hz,
        ]
        .iter()
        .all(|value| value.is_finite() && *value > 0.0)
            || self.propagation_step_s > 600.0
        {
            return Err("known-flight positive model parameter is invalid");
        }
        if ![
            self.process_magnetic_heading_sd_deg_per_sqrt_hour,
            self.process_mach_sd_per_sqrt_hour,
            self.process_altitude_sd_ft_per_sqrt_hour,
        ]
        .iter()
        .all(|value| value.is_finite() && *value >= 0.0)
            || !self.ground_station_position_km.is_finite()
        {
            return Err("known-flight process or geometry parameter is invalid");
        }
        self.satcom
            .validate()
            .map_err(|_| "known-flight SATCOM configuration is invalid")?;
        if let Some(antenna) = &self.antenna {
            antenna.validate()?;
        }
        Ok(())
    }
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct KnownFlightAntennaConfig {
    pub expected_observations_sha256: String,
    pub expected_surface_sha256: String,
    pub observation_sd_db: f64,
    pub reference_gain_dbic: f64,
    pub directional_departure_scale: f64,
    pub permit_unverified_reconstruction: bool,
}

impl KnownFlightAntennaConfig {
    fn validate(&self) -> Result<(), &'static str> {
        if !is_sha256(&self.expected_observations_sha256)
            || !is_sha256(&self.expected_surface_sha256)
            || ![
                self.observation_sd_db,
                self.reference_gain_dbic,
                self.directional_departure_scale,
            ]
            .iter()
            .all(|value| value.is_finite())
            || self.observation_sd_db <= 0.0
            || !(0.0..=1.0).contains(&self.directional_departure_scale)
            || !self.permit_unverified_reconstruction
        {
            return Err("known-flight conditional antenna configuration is invalid");
        }
        Ok(())
    }
}

fn is_sha256(value: &str) -> bool {
    value.len() == 64 && value.bytes().all(|byte| byte.is_ascii_hexdigit())
}

#[derive(Debug, Clone, Deserialize)]
struct PackageInitialState {
    lat_deg: f64,
    lon_deg: f64,
    heading_true_deg: f64,
}

#[derive(Debug, Clone, Deserialize)]
struct PackageInitialPrior {
    north_sd_nm: f64,
    east_sd_nm: f64,
    heading_sd_deg: f64,
}

#[derive(Debug, Clone, Deserialize)]
struct PackageObservation {
    epoch_id: String,
    time_utc: String,
    seconds_from_t0: f64,
    bto_us: f64,
    bto_sd_us: f64,
    bfo_hz: f64,
    satellite_oscillator_hz: f64,
    perth_ges_afc_hz: f64,
    sat_position: [f64; 3],
    sat_velocity: [f64; 3],
}

#[derive(Debug, Clone, Deserialize)]
pub struct KnownFlightInferencePackage {
    schema_version: String,
    source_id: String,
    status: String,
    time_origin_utc: String,
    time_origin_unix_s: i64,
    initial_state: PackageInitialState,
    initial_position_prior: PackageInitialPrior,
    observations: Vec<PackageObservation>,
}

impl KnownFlightInferencePackage {
    fn validate(&self) -> Result<(), KnownFlightError> {
        if self.schema_version != PACKAGE_SCHEMA || self.source_id != "mh371-cruise-control" {
            return Err(KnownFlightError::InvalidPackage(
                "unsupported known-flight package identity".to_string(),
            ));
        }
        if self.time_origin_utc.is_empty() || self.time_origin_unix_s <= 0 {
            return Err(KnownFlightError::InvalidPackage(
                "known-flight time origin is invalid".to_string(),
            ));
        }
        let initial = &self.initial_state;
        if !initial.heading_true_deg.is_finite()
            || LatLon::new(initial.lat_deg, initial.lon_deg).is_err()
        {
            return Err(KnownFlightError::InvalidPackage(
                "known-flight initial state is invalid".to_string(),
            ));
        }
        let prior = &self.initial_position_prior;
        if ![prior.north_sd_nm, prior.east_sd_nm, prior.heading_sd_deg]
            .iter()
            .all(|value| value.is_finite() && *value > 0.0)
        {
            return Err(KnownFlightError::InvalidPackage(
                "known-flight initial uncertainty is invalid".to_string(),
            ));
        }
        if self.observations.is_empty() {
            return Err(KnownFlightError::InvalidPackage(
                "known-flight package has no observations".to_string(),
            ));
        }
        let mut previous = 0.0;
        for observation in &self.observations {
            if observation.epoch_id.is_empty()
                || observation.time_utc.is_empty()
                || !observation.seconds_from_t0.is_finite()
                || observation.seconds_from_t0 <= previous
                || !observation.bto_us.is_finite()
                || !observation.bto_sd_us.is_finite()
                || observation.bto_sd_us <= 0.0
                || !observation.bfo_hz.is_finite()
                || !observation.satellite_oscillator_hz.is_finite()
                || !observation.perth_ges_afc_hz.is_finite()
                || observation
                    .sat_position
                    .iter()
                    .chain(&observation.sat_velocity)
                    .any(|value| !value.is_finite())
            {
                return Err(KnownFlightError::InvalidPackage(
                    "known-flight observation is invalid".to_string(),
                ));
            }
            previous = observation.seconds_from_t0;
        }
        Ok(())
    }

    fn initial_position(&self) -> Result<LatLon, KnownFlightError> {
        LatLon::new(self.initial_state.lat_deg, self.initial_state.lon_deg)
            .map_err(|_| KnownFlightError::InvalidCoordinate)
    }

    fn typed_observations(
        &self,
        model: &KnownFlightModelConfig,
        antenna_package: Option<&KnownFlightAntennaPowerPackage>,
    ) -> Result<Vec<KnownFlightObservation>, KnownFlightError> {
        let antenna = match (&model.antenna, antenna_package) {
            (Some(configuration), Some(package)) => package
                .align(
                    &self
                        .observations
                        .iter()
                        .map(|raw| (raw.epoch_id.clone(), raw.time_utc.clone()))
                        .collect::<Vec<_>>(),
                    configuration,
                )?
                .into_iter()
                .map(Some)
                .collect::<Vec<_>>(),
            (None, None) => vec![None; self.observations.len()],
            _ => {
                return Err(KnownFlightError::InvalidConfiguration(
                    "antenna configuration and inputs must be supplied together",
                ))
            }
        };
        Ok(self
            .observations
            .iter()
            .zip(antenna)
            .map(|(raw, antenna)| KnownFlightObservation {
                epoch_id: raw.epoch_id.clone(),
                time_utc: raw.time_utc.clone(),
                satellite_oscillator_hz: raw.satellite_oscillator_hz,
                perth_ges_afc_hz: raw.perth_ges_afc_hz,
                satcom: SatcomObservation {
                    time: Seconds(raw.seconds_from_t0),
                    satellite_position_km: Vec3::new(
                        raw.sat_position[0],
                        raw.sat_position[1],
                        raw.sat_position[2],
                    ),
                    satellite_velocity_km_s: Vec3::new(
                        raw.sat_velocity[0],
                        raw.sat_velocity[1],
                        raw.sat_velocity[2],
                    ),
                    ground_station_position_km: model.ground_station_position_km,
                    bto: Some(Microseconds(raw.bto_us)),
                    bto_sd: Some(Microseconds(raw.bto_sd_us)),
                    bfo: Some(Hertz(raw.bfo_hz)),
                    bfo_sd: Some(Hertz(model.bfo_observation_sd_hz)),
                },
                antenna,
            })
            .collect())
    }
}

fn reject_truth_keys(value: &Value, path: &str) -> Result<(), KnownFlightError> {
    match value {
        Value::Object(fields) => {
            for (key, nested) in fields {
                if key.to_ascii_lowercase().contains("truth") {
                    return Err(KnownFlightError::TruthBoundary(format!(
                        "truth-like key found in inference package: {path}.{key}"
                    )));
                }
                reject_truth_keys(nested, &format!("{path}.{key}"))?;
            }
        }
        Value::Array(items) => {
            for (index, nested) in items.iter().enumerate() {
                reject_truth_keys(nested, &format!("{path}[{index}]"))?;
            }
        }
        _ => {}
    }
    Ok(())
}

pub fn parse_known_flight_inference(
    bytes: &[u8],
) -> Result<KnownFlightInferencePackage, KnownFlightError> {
    let value: Value = serde_json::from_slice(bytes)?;
    reject_truth_keys(&value, "$")?;
    let package: KnownFlightInferencePackage = serde_json::from_value(value)?;
    package.validate()?;
    Ok(package)
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct KnownFlightObservation {
    pub epoch_id: String,
    pub time_utc: String,
    pub satellite_oscillator_hz: f64,
    pub perth_ges_afc_hz: f64,
    pub satcom: SatcomObservation,
    #[serde(default)]
    pub antenna: Option<KnownFlightAntennaObservation>,
}

impl KnownFlightObservation {
    pub fn combined_satellite_ges_hz(&self) -> f64 {
        self.satellite_oscillator_hz + self.perth_ges_afc_hz
    }
}

#[derive(Debug, Clone, Copy, PartialEq, Serialize, Deserialize)]
pub struct KnownFlightParticle {
    pub aircraft: AircraftState,
    pub mach: f64,
    pub magnetic_heading: Degrees,
    pub bfo_bias: BfoBiasState,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct KnownFlightInferenceRun {
    pub schema_version: String,
    pub status: String,
    pub experiment_name: String,
    pub model_family: String,
    pub inference_sha256: String,
    pub inference_config_sha256: String,
    pub weather_sha256: String,
    pub magnetic_sha256: String,
    #[serde(default)]
    pub antenna_observations_sha256: Option<String>,
    #[serde(default)]
    pub antenna_surface_sha256: Option<String>,
    #[serde(default)]
    pub antenna_source_status: Option<String>,
    pub source_package_id: String,
    pub source_status: String,
    pub time_origin_utc: String,
    pub seed: u64,
    pub particle_count: usize,
    pub observations: Vec<KnownFlightObservation>,
    pub limitations: Vec<String>,
    pub filter: FilterResult<KnownFlightParticle>,
}

#[derive(Debug, Error)]
pub enum KnownFlightError {
    #[error("invalid known-flight configuration: {0}")]
    InvalidConfiguration(&'static str),
    #[error("invalid known-flight package: {0}")]
    InvalidPackage(String),
    #[error("truth-separation boundary violation: {0}")]
    TruthBoundary(String),
    #[error("sampled known-flight coordinate is invalid")]
    InvalidCoordinate,
    #[error("known-flight input SHA-256 does not match configuration: {0}")]
    HashMismatch(&'static str),
    #[error(transparent)]
    Json(#[from] serde_json::Error),
    #[error(transparent)]
    Geodesy(#[from] GeodesyError),
    #[error(transparent)]
    Dynamics(#[from] DynamicsError),
    #[error(transparent)]
    Environment(#[from] EnvironmentError),
    #[error(transparent)]
    Satcom(#[from] SatcomModelError),
    #[error(transparent)]
    Antenna(#[from] AntennaError),
    #[error(transparent)]
    Filter(#[from] SmcError),
}

fn normal(rng: &mut ChaCha8Rng) -> f64 {
    StandardNormal.sample(rng)
}

#[derive(Clone)]
struct KnownFlightModel<'a> {
    initial_position: LatLon,
    initial_heading_true: Degrees,
    prior_uncertainty: PackageInitialPrior,
    prior: KnownFlightPriorConfig,
    configuration: KnownFlightModelConfig,
    time_origin_unix_s: f64,
    weather: &'a Era5Grid,
    magnetic: &'a IgrfGrid,
    antenna_surface: Option<&'a DirectionalGainGrid>,
}

impl KnownFlightModel<'_> {
    fn update_motion(&self, state: &mut KnownFlightParticle) -> Result<(), KnownFlightError> {
        let weather = self.weather.sample(
            self.time_origin_unix_s + state.aircraft.time.0,
            state.aircraft.altitude.0,
            state.aircraft.position,
        )?;
        let declination = self
            .magnetic
            .declination(state.aircraft.altitude.0, state.aircraft.position)?;
        let velocity = ground_velocity_from_control(
            Knots(state.mach * weather.speed_of_sound_knots()),
            state.magnetic_heading,
            LateralMode::ConstantMagneticHeading,
            weather.wind_north,
            weather.wind_east,
            declination,
        )?;
        state.aircraft.track_true = velocity.track_true;
        state.aircraft.ground_speed = velocity.speed;
        state.aircraft.bfo_bias = Hertz(state.bfo_bias.mean_hz);
        Ok(())
    }

    fn propagate(
        &self,
        state: &KnownFlightParticle,
        elapsed_seconds: f64,
    ) -> Result<KnownFlightParticle, KnownFlightError> {
        let mut result = *state;
        let mut remaining = elapsed_seconds;
        while remaining > 0.0 {
            self.update_motion(&mut result)?;
            let step = remaining.min(self.configuration.propagation_step_s);
            result.aircraft = propagate_constant_track(result.aircraft, Seconds(step))?;
            remaining -= step;
        }
        self.update_motion(&mut result)?;
        Ok(result)
    }

    fn fit(
        &self,
        state: &mut KnownFlightParticle,
        observation: &KnownFlightObservation,
        use_bfo: bool,
        use_antenna: bool,
        inflation: f64,
    ) -> Result<f64, KnownFlightError> {
        let mut satcom = observation.satcom.clone();
        if inflation != 1.0 {
            satcom.bto_sd = satcom.bto_sd.map(|value| Microseconds(value.0 * inflation));
            satcom.bfo_sd = satcom.bfo_sd.map(|value| Hertz(value.0 * inflation));
        }
        let fit = evaluate_observation(
            state.aircraft,
            &mut state.bfo_bias,
            &satcom,
            observation.combined_satellite_ges_hz(),
            use_bfo,
            &self.configuration.satcom,
        )?;
        state.aircraft.bfo_bias = Hertz(state.bfo_bias.mean_hz);
        let mut log_likelihood = fit.log_likelihood;
        if use_antenna {
            match (&observation.antenna, self.antenna_surface) {
                (Some(antenna), Some(surface)) => {
                    let declination = self
                        .magnetic
                        .declination(state.aircraft.altitude.0, state.aircraft.position)?;
                    let heading_true =
                        Degrees(state.magnetic_heading.0 + declination.0).wrapped_360();
                    log_likelihood += evaluate_conditional_power(
                        state.aircraft,
                        AircraftAttitude::level(heading_true),
                        observation.satcom.satellite_position_km,
                        surface,
                        antenna.power,
                    )?
                    .log_likelihood
                    .ok_or(KnownFlightError::InvalidConfiguration(
                        "conditional antenna surface was not explicitly permitted",
                    ))?;
                }
                (None, None) => {}
                _ => {
                    return Err(KnownFlightError::InvalidConfiguration(
                        "antenna observation and surface must be supplied together",
                    ))
                }
            }
        }
        Ok(log_likelihood)
    }
}

#[derive(Debug)]
struct ModelError(KnownFlightError);

impl fmt::Display for ModelError {
    fn fmt(&self, formatter: &mut fmt::Formatter<'_>) -> fmt::Result {
        self.0.fmt(formatter)
    }
}

impl std::error::Error for ModelError {}

impl From<KnownFlightError> for ModelError {
    fn from(value: KnownFlightError) -> Self {
        Self(value)
    }
}

impl From<GeodesyError> for ModelError {
    fn from(value: GeodesyError) -> Self {
        Self(KnownFlightError::from(value))
    }
}

impl From<EnvironmentError> for ModelError {
    fn from(value: EnvironmentError) -> Self {
        Self(KnownFlightError::from(value))
    }
}

impl ParticleModel for KnownFlightModel<'_> {
    type State = KnownFlightParticle;
    type Observation = KnownFlightObservation;
    type Error = ModelError;

    fn observation_time_s(&self, observation: &Self::Observation) -> f64 {
        observation.satcom.time.0
    }

    fn initialize(
        &self,
        _particle_index: usize,
        rng: &mut ChaCha8Rng,
    ) -> Result<Self::State, Self::Error> {
        let north = normal(rng) * self.prior_uncertainty.north_sd_nm;
        let east = normal(rng) * self.prior_uncertainty.east_sd_nm;
        let position = destination_wgs84(
            self.initial_position,
            Degrees(east.atan2(north).to_degrees()).wrapped_360(),
            NauticalMiles(north.hypot(east)),
        )?;
        let altitude_ft = rng.gen_range(self.prior.altitude_min_ft..=self.prior.altitude_max_ft);
        let mach = rng.gen_range(self.prior.mach_min..=self.prior.mach_max);
        let heading_true = Degrees(
            self.initial_heading_true.0 + normal(rng) * self.prior_uncertainty.heading_sd_deg,
        )
        .wrapped_360();
        let declination = self.magnetic.declination(altitude_ft, position)?;
        let bias = self.configuration.satcom.initial_bias();
        let mut state = KnownFlightParticle {
            aircraft: AircraftState {
                time: Seconds(0.0),
                position,
                altitude: Feet(altitude_ft),
                track_true: heading_true,
                ground_speed: Knots(1.0),
                vertical_speed: FeetPerMinute(0.0),
                bfo_bias: Hertz(bias.mean_hz),
            },
            mach,
            magnetic_heading: Degrees(heading_true.0 - declination.0).wrapped_360(),
            bfo_bias: bias,
        };
        self.update_motion(&mut state)?;
        Ok(state)
    }

    fn guide_log_likelihood(
        &self,
        state: &Self::State,
        observation: &Self::Observation,
    ) -> Result<f64, Self::Error> {
        let elapsed = observation.satcom.time.0 - state.aircraft.time.0;
        let mut forecast = self.propagate(state, elapsed)?;
        self.fit(
            &mut forecast,
            observation,
            false,
            false,
            self.configuration.guide_inflation,
        )
        .map_err(ModelError)
    }

    fn propose(
        &self,
        state: &Self::State,
        _observation: &Self::Observation,
        elapsed_seconds: f64,
        rng: &mut ChaCha8Rng,
    ) -> Result<Proposal<Self::State>, Self::Error> {
        let scale = (elapsed_seconds / 3_600.0).sqrt();
        let mut proposed = *state;
        proposed.magnetic_heading = Degrees(
            proposed.magnetic_heading.0
                + normal(rng)
                    * self
                        .configuration
                        .process_magnetic_heading_sd_deg_per_sqrt_hour
                    * scale,
        )
        .wrapped_360();
        proposed.mach = (proposed.mach
            + normal(rng) * self.configuration.process_mach_sd_per_sqrt_hour * scale)
            .clamp(self.prior.mach_min, self.prior.mach_max);
        proposed.aircraft.altitude = Feet(
            (proposed.aircraft.altitude.0
                + normal(rng) * self.configuration.process_altitude_sd_ft_per_sqrt_hour * scale)
                .clamp(self.prior.altitude_min_ft, self.prior.altitude_max_ft),
        );
        let propagated = self.propagate(&proposed, elapsed_seconds)?;
        Ok(Proposal::from_prior(propagated))
    }

    fn log_likelihood(
        &self,
        state: &Self::State,
        observation: &Self::Observation,
    ) -> Result<f64, Self::Error> {
        let mut clone = *state;
        self.fit(&mut clone, observation, true, true, 1.0)
            .map_err(ModelError)
    }

    fn observe(
        &self,
        state: &mut Self::State,
        observation: &Self::Observation,
    ) -> Result<f64, Self::Error> {
        self.fit(state, observation, true, true, 1.0)
            .map_err(ModelError)
    }
}

#[allow(clippy::too_many_arguments)]
pub fn run_known_flight_inference(
    configuration: &KnownFlightInferenceConfig,
    package: &KnownFlightInferencePackage,
    inference_sha256: &str,
    inference_config_sha256: &str,
    weather: &Era5Grid,
    weather_sha256: &str,
    magnetic: &IgrfGrid,
    magnetic_sha256: &str,
    antenna: Option<KnownFlightAntennaInputs<'_>>,
    seed: u64,
) -> Result<KnownFlightInferenceRun, KnownFlightError> {
    configuration
        .validate()
        .map_err(KnownFlightError::InvalidConfiguration)?;
    package.validate()?;
    if inference_sha256 != configuration.expected_inference_sha256 {
        return Err(KnownFlightError::HashMismatch("inference package"));
    }
    if weather_sha256 != configuration.expected_weather_sha256 {
        return Err(KnownFlightError::HashMismatch("ERA5 weather grid"));
    }
    if magnetic_sha256 != configuration.expected_magnetic_sha256 {
        return Err(KnownFlightError::HashMismatch("IGRF magnetic grid"));
    }
    match (&configuration.model.antenna, &antenna) {
        (Some(expected), Some(inputs)) => {
            if inputs.observations_sha256 != expected.expected_observations_sha256 {
                return Err(KnownFlightError::HashMismatch(
                    "conditional antenna observations",
                ));
            }
            if inputs.surface_sha256 != expected.expected_surface_sha256 {
                return Err(KnownFlightError::HashMismatch(
                    "conditional antenna gain surface",
                ));
            }
        }
        (None, None) => {}
        _ => {
            return Err(KnownFlightError::InvalidConfiguration(
                "antenna configuration and input bundle must be supplied together",
            ))
        }
    }
    if !configuration.seeds.contains(&seed) {
        return Err(KnownFlightError::InvalidConfiguration(
            "requested seed is outside the configured plan",
        ));
    }
    if (magnetic.reference_time_unix_s - package.time_origin_unix_s).abs() > 86_400 {
        return Err(KnownFlightError::InvalidPackage(
            "magnetic grid epoch does not match control date".to_string(),
        ));
    }

    let antenna_package = antenna.as_ref().map(|inputs| inputs.package);
    let antenna_surface = antenna.as_ref().map(|inputs| inputs.surface);
    let observations = package.typed_observations(&configuration.model, antenna_package)?;
    let model = KnownFlightModel {
        initial_position: package.initial_position()?,
        initial_heading_true: Degrees(package.initial_state.heading_true_deg),
        prior_uncertainty: package.initial_position_prior.clone(),
        prior: configuration.prior.clone(),
        configuration: configuration.model.clone(),
        time_origin_unix_s: package.time_origin_unix_s as f64,
        weather,
        magnetic,
        antenna_surface,
    };
    let filter_configuration = FilterConfig {
        particles: configuration.particles,
        seed,
        algorithm: configuration.algorithm,
        initial_time_s: 0.0,
        ess_resample_fraction: configuration.ess_resample_fraction,
    };
    let filter = run_filter_with_options(
        &model,
        &observations,
        &filter_configuration,
        FilterRunOptions {
            retain_snapshots: true,
        },
    )?;

    let has_antenna = antenna.is_some();
    let mut limitations = vec![
        "known-flight computational control; not evidence about MH370 geography".to_string(),
        "later ACARS positions and trajectories are absent from inference and used only by the scorer"
            .to_string(),
        "satellite oscillator and Perth GES AFC corrections are interpolated inputs distinct from the analytically estimated aircraft BFO bias"
            .to_string(),
        "constant magnetic heading is diffused between observations; airline flight-plan intent is not supplied"
            .to_string(),
    ];
    if has_antenna {
        limitations.extend([
            "conditional antenna sensitivity only: RxGain validation did not justify unconditional core use or a model-family mixture weight"
                .to_string(),
            "the explicitly permitted first-pass gain surface is uncommissioned, lacks verified port/starboard handoff, and does not reproduce every workbook event gain"
                .to_string(),
            "the event/channel full-precompensation prediction is frozen; the antenna likelihood contributes only the modeled directional departure"
                .to_string(),
            "event-level antenna residuals are treated as independent after aggregation"
                .to_string(),
        ]);
    }
    Ok(KnownFlightInferenceRun {
        schema_version: RUN_SCHEMA.to_string(),
        status: if has_antenna {
            "complete_truth_separated_conditional_antenna_control"
        } else {
            "complete_truth_separated_bto_bfo_control"
        }
        .to_string(),
        experiment_name: configuration.name.clone(),
        model_family: configuration.model_family.clone(),
        inference_sha256: inference_sha256.to_string(),
        inference_config_sha256: inference_config_sha256.to_string(),
        weather_sha256: weather_sha256.to_string(),
        magnetic_sha256: magnetic_sha256.to_string(),
        antenna_observations_sha256: antenna
            .as_ref()
            .map(|inputs| inputs.observations_sha256.to_string()),
        antenna_surface_sha256: antenna
            .as_ref()
            .map(|inputs| inputs.surface_sha256.to_string()),
        antenna_source_status: antenna
            .as_ref()
            .map(|inputs| inputs.package.source_status().to_string()),
        source_package_id: package.source_id.clone(),
        source_status: package.status.clone(),
        time_origin_utc: package.time_origin_utc.clone(),
        seed,
        particle_count: configuration.particles,
        observations,
        limitations,
        filter,
    })
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn parser_rejects_truth_like_fields_at_any_depth() {
        let bytes = br#"{
            "schema_version": "mh371-known-flight-package-v2",
            "truth_lat": 1.0
        }"#;
        assert!(matches!(
            parse_known_flight_inference(bytes),
            Err(KnownFlightError::TruthBoundary(_))
        ));
    }

    #[test]
    fn sha256_syntax_check_is_strict() {
        assert!(is_sha256(
            "344debab104b9429ecf2db0b6b54530b60db86d642fdcfc9e04baad76add159a"
        ));
        assert!(!is_sha256("not-a-hash"));
    }
}
