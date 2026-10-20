//! Predictive hydroacoustic observables for a proposed ocean impact.
//!
//! This crate deliberately contains no observed-signal likelihood. The public
//! API predicts arrival and signal-scale intervals. A future likelihood must
//! be a separate, named observed-signal model with explicit false-alarm and
//! selection correction; publication-trace feature matching is not such a
//! model.

use mh370_domain::{great_circle_distance_nm, ImpactPoint, LatLon};
use serde::{Deserialize, Serialize};
use thiserror::Error;

mod diagnostic;
mod raw_triad;

pub use diagnostic::{
    predict_diagnostic_grid, reverse_trace_windows, DiagnosticGridError, DiagnosticGridInput,
    DiagnosticGridOutput, DiagnosticImpactScenario, DiagnosticSourceCell,
    ForwardScenarioPrediction, ObservedStationWindow, ReverseCellMatch, ReverseTraceInput,
    ReverseTraceOutput, DIAGNOSTIC_GRID_SCHEMA_ID, DIAGNOSTIC_GRID_SCHEMA_VERSION,
    REVERSE_TRACE_SCHEMA_ID, REVERSE_TRACE_SCHEMA_VERSION,
};
pub use raw_triad::{
    RawHydrophoneChannel, RawPressureUnit, RawTriadError, RawTriadInputV1, RAW_TRIAD_SCHEMA_ID,
    RAW_TRIAD_SCHEMA_VERSION,
};

const KM_PER_NM: f64 = 1.852;

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum HydroRole {
    /// Contextual prediction only. No likelihood is evaluated.
    OverlayOnly,
}

/// Legacy runner-facing timing overlay.
///
/// New scientific work should use [`ForwardModel::predict`]. This type remains
/// only so the runner can emit its current geometry diagnostic.
#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct HydroEvent {
    pub name: String,
    pub station: LatLon,
    pub arrival_time_s: f64,
    pub minimum_speed_km_s: f64,
    pub maximum_speed_km_s: f64,
    pub timing_sd_s: f64,
    pub role: HydroRole,
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct HydroScore {
    pub event: String,
    pub distance_km: f64,
    pub predicted_arrival_min_s: f64,
    pub predicted_arrival_max_s: f64,
    pub midpoint_residual_s: f64,
    /// Always `None`: an overlay is not an observed-signal model.
    pub log_likelihood: Option<f64>,
    pub role: HydroRole,
}

#[derive(Debug, Clone, Copy, PartialEq, Serialize, Deserialize)]
pub struct ClosedInterval {
    pub minimum: f64,
    pub maximum: f64,
}

impl ClosedInterval {
    pub fn new(minimum: f64, maximum: f64) -> Result<Self, HydroError> {
        let value = Self { minimum, maximum };
        value.validate_nonnegative()?;
        Ok(value)
    }

    fn validate_nonnegative(self) -> Result<(), HydroError> {
        if !self.minimum.is_finite()
            || !self.maximum.is_finite()
            || self.minimum < 0.0
            || self.maximum < self.minimum
        {
            return Err(HydroError::InvalidInterval);
        }
        Ok(())
    }

    fn product(self, other: Self) -> Self {
        Self {
            minimum: self.minimum * other.minimum,
            maximum: self.maximum * other.maximum,
        }
    }

    pub fn contains(self, value: f64) -> bool {
        value.is_finite() && value >= self.minimum && value <= self.maximum
    }

    pub fn intersection(self, other: Self) -> Option<Self> {
        let minimum = self.minimum.max(other.minimum);
        let maximum = self.maximum.min(other.maximum);
        (maximum >= minimum).then_some(Self { minimum, maximum })
    }
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum EnergyBasis {
    /// Total translational kinetic energy at first water contact.
    TotalVelocity,
    /// Kinetic energy in the local vertical component only.
    VerticalVelocity,
}

/// Aircraft state at first water contact, in a local east/north/up frame.
#[derive(Debug, Clone, Copy, PartialEq, Serialize, Deserialize)]
pub struct ImpactState {
    pub point: ImpactPoint,
    pub mass_kg: f64,
    pub east_velocity_m_s: f64,
    pub north_velocity_m_s: f64,
    /// Positive upwards; the sign is removed when energy is calculated.
    pub up_velocity_m_s: f64,
    pub pitch_deg: f64,
    pub roll_deg: f64,
    pub yaw_true_deg: f64,
    /// Duration over which the principal water-contact impulse is applied.
    pub contact_duration_s: f64,
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct SourceCouplingFamily {
    pub name: String,
    pub energy_basis: EnergyBasis,
    /// Fraction of the selected kinetic-energy basis launched into the
    /// propagating hydroacoustic family.
    pub acoustic_energy_fraction: ClosedInterval,
    pub minimum_frequency_hz: f64,
    pub maximum_frequency_hz: f64,
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct PropagationFamily {
    pub name: String,
    /// Effective group-celerity family, not a single assumed SOFAR speed.
    pub celerity_km_s: ClosedInterval,
    /// Additional received-signal broadening caused by dispersion and
    /// unresolved multipath.
    pub dispersion_duration_s: ClosedInterval,
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct PathFamily {
    pub name: String,
    pub bathymetry_basis: String,
    /// End-to-end pressure-squared-exposure transfer in Pa^2 s per joule
    /// launched by the source. It intentionally remains an externally
    /// calibrated interval until path Green functions are available.
    pub pressure_exposure_transfer_pa2_s_per_j: ClosedInterval,
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct StationResponseFamily {
    pub name: String,
    pub station_name: String,
    pub station: LatLon,
    /// Dimensionless pressure-amplitude response over the declared band.
    pub amplitude_gain: ClosedInterval,
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct StationPredictionModel {
    pub propagation: PropagationFamily,
    pub path: PathFamily,
    pub response: StationResponseFamily,
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct ForwardModel {
    pub source: SourceCouplingFamily,
    pub stations: Vec<StationPredictionModel>,
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct StationPrediction {
    pub station_name: String,
    pub source_family: String,
    pub propagation_family: String,
    pub path_family: String,
    pub station_response_family: String,
    pub bathymetry_basis: String,
    pub distance_km: f64,
    pub arrival_time_s: ClosedInterval,
    pub incident_kinetic_energy_j: f64,
    pub coupled_acoustic_energy_j: ClosedInterval,
    pub pressure_squared_exposure_pa2_s: ClosedInterval,
    pub effective_signal_duration_s: ClosedInterval,
    pub rms_pressure_pa: ClosedInterval,
    pub frequency_hz: ClosedInterval,
    /// Constant by construction: a prediction must not be mistaken for evidence.
    pub likelihood_evaluated: bool,
}

#[derive(Debug, Error, Clone, PartialEq)]
pub enum HydroError {
    #[error("invalid hydroacoustic event configuration")]
    InvalidEvent,
    #[error("invalid closed interval")]
    InvalidInterval,
    #[error("invalid impact state")]
    InvalidImpactState,
    #[error("invalid source-coupling family")]
    InvalidSourceFamily,
    #[error("invalid propagation family")]
    InvalidPropagationFamily,
    #[error("invalid path family")]
    InvalidPathFamily,
    #[error("invalid station-response family")]
    InvalidStationResponse,
    #[error("at least one station prediction model is required")]
    NoStations,
}

impl HydroEvent {
    pub fn validate(&self) -> Result<(), HydroError> {
        if self.name.trim().is_empty()
            || ![
                self.arrival_time_s,
                self.minimum_speed_km_s,
                self.maximum_speed_km_s,
                self.timing_sd_s,
            ]
            .iter()
            .all(|value| value.is_finite())
            || self.minimum_speed_km_s <= 0.0
            || self.maximum_speed_km_s < self.minimum_speed_km_s
            || self.timing_sd_s <= 0.0
        {
            return Err(HydroError::InvalidEvent);
        }
        Ok(())
    }

    /// Evaluate a transparent straight-path timing overlay.
    ///
    /// The residual is descriptive. It is never converted into a likelihood.
    pub fn score(&self, impact: ImpactPoint) -> Result<HydroScore, HydroError> {
        self.validate()?;
        let distance_km = great_circle_distance_nm(impact.position, self.station).0 * KM_PER_NM;
        let earliest = impact.time.0 + distance_km / self.maximum_speed_km_s;
        let latest = impact.time.0 + distance_km / self.minimum_speed_km_s;
        let midpoint = 0.5 * (earliest + latest);
        Ok(HydroScore {
            event: self.name.clone(),
            distance_km,
            predicted_arrival_min_s: earliest,
            predicted_arrival_max_s: latest,
            midpoint_residual_s: self.arrival_time_s - midpoint,
            log_likelihood: None,
            role: self.role,
        })
    }
}

impl ImpactState {
    fn validate(self) -> Result<(), HydroError> {
        if ![
            self.point.time.0,
            self.mass_kg,
            self.east_velocity_m_s,
            self.north_velocity_m_s,
            self.up_velocity_m_s,
            self.pitch_deg,
            self.roll_deg,
            self.yaw_true_deg,
            self.contact_duration_s,
        ]
        .iter()
        .all(|value| value.is_finite())
            || self.mass_kg <= 0.0
            || self.contact_duration_s <= 0.0
        {
            return Err(HydroError::InvalidImpactState);
        }
        Ok(())
    }

    pub fn kinetic_energy_j(self, basis: EnergyBasis) -> Result<f64, HydroError> {
        self.validate()?;
        let speed_squared = match basis {
            EnergyBasis::TotalVelocity => {
                self.east_velocity_m_s.powi(2)
                    + self.north_velocity_m_s.powi(2)
                    + self.up_velocity_m_s.powi(2)
            }
            EnergyBasis::VerticalVelocity => self.up_velocity_m_s.powi(2),
        };
        Ok(0.5 * self.mass_kg * speed_squared)
    }
}

impl ForwardModel {
    pub fn validate(&self) -> Result<(), HydroError> {
        if self.stations.is_empty() {
            return Err(HydroError::NoStations);
        }
        validate_name(&self.source.name).map_err(|_| HydroError::InvalidSourceFamily)?;
        self.source
            .acoustic_energy_fraction
            .validate_nonnegative()
            .map_err(|_| HydroError::InvalidSourceFamily)?;
        if self.source.acoustic_energy_fraction.maximum > 1.0
            || !valid_positive_band(
                self.source.minimum_frequency_hz,
                self.source.maximum_frequency_hz,
            )
        {
            return Err(HydroError::InvalidSourceFamily);
        }
        for station in &self.stations {
            validate_name(&station.propagation.name)
                .map_err(|_| HydroError::InvalidPropagationFamily)?;
            station
                .propagation
                .celerity_km_s
                .validate_nonnegative()
                .map_err(|_| HydroError::InvalidPropagationFamily)?;
            station
                .propagation
                .dispersion_duration_s
                .validate_nonnegative()
                .map_err(|_| HydroError::InvalidPropagationFamily)?;
            if station.propagation.celerity_km_s.minimum <= 0.0 {
                return Err(HydroError::InvalidPropagationFamily);
            }
            validate_name(&station.path.name).map_err(|_| HydroError::InvalidPathFamily)?;
            validate_name(&station.path.bathymetry_basis)
                .map_err(|_| HydroError::InvalidPathFamily)?;
            station
                .path
                .pressure_exposure_transfer_pa2_s_per_j
                .validate_nonnegative()
                .map_err(|_| HydroError::InvalidPathFamily)?;
            validate_name(&station.response.name)
                .map_err(|_| HydroError::InvalidStationResponse)?;
            validate_name(&station.response.station_name)
                .map_err(|_| HydroError::InvalidStationResponse)?;
            station
                .response
                .amplitude_gain
                .validate_nonnegative()
                .map_err(|_| HydroError::InvalidStationResponse)?;
        }
        Ok(())
    }

    /// Predict station-specific arrival and signal-scale intervals.
    ///
    /// No observed trace is accepted and no probability of the impact state is
    /// returned. The path-transfer interval must come from an independent
    /// propagation calculation, calibration event or deliberately broad
    /// sensitivity family.
    pub fn predict(&self, impact: ImpactState) -> Result<Vec<StationPrediction>, HydroError> {
        self.validate()?;
        impact.validate()?;
        let incident = impact.kinetic_energy_j(self.source.energy_basis)?;
        let coupled = ClosedInterval {
            minimum: incident * self.source.acoustic_energy_fraction.minimum,
            maximum: incident * self.source.acoustic_energy_fraction.maximum,
        };
        let frequency_hz = ClosedInterval {
            minimum: self.source.minimum_frequency_hz,
            maximum: self.source.maximum_frequency_hz,
        };

        self.stations
            .iter()
            .map(|station| {
                let distance_km =
                    great_circle_distance_nm(impact.point.position, station.response.station).0
                        * KM_PER_NM;
                let arrival_time_s = ClosedInterval {
                    minimum: impact.point.time.0
                        + distance_km / station.propagation.celerity_km_s.maximum,
                    maximum: impact.point.time.0
                        + distance_km / station.propagation.celerity_km_s.minimum,
                };
                let response_power = ClosedInterval {
                    minimum: station.response.amplitude_gain.minimum.powi(2),
                    maximum: station.response.amplitude_gain.maximum.powi(2),
                };
                let exposure = coupled
                    .product(station.path.pressure_exposure_transfer_pa2_s_per_j)
                    .product(response_power);
                let duration = ClosedInterval {
                    minimum: impact.contact_duration_s
                        + station.propagation.dispersion_duration_s.minimum,
                    maximum: impact.contact_duration_s
                        + station.propagation.dispersion_duration_s.maximum,
                };
                let rms_pressure = ClosedInterval {
                    minimum: (exposure.minimum / duration.maximum).sqrt(),
                    maximum: (exposure.maximum / duration.minimum).sqrt(),
                };
                Ok(StationPrediction {
                    station_name: station.response.station_name.clone(),
                    source_family: self.source.name.clone(),
                    propagation_family: station.propagation.name.clone(),
                    path_family: station.path.name.clone(),
                    station_response_family: station.response.name.clone(),
                    bathymetry_basis: station.path.bathymetry_basis.clone(),
                    distance_km,
                    arrival_time_s,
                    incident_kinetic_energy_j: incident,
                    coupled_acoustic_energy_j: coupled,
                    pressure_squared_exposure_pa2_s: exposure,
                    effective_signal_duration_s: duration,
                    rms_pressure_pa: rms_pressure,
                    frequency_hz,
                    likelihood_evaluated: false,
                })
            })
            .collect()
    }
}

fn validate_name(value: &str) -> Result<(), ()> {
    if value.trim().is_empty() {
        Err(())
    } else {
        Ok(())
    }
}

fn valid_positive_band(minimum: f64, maximum: f64) -> bool {
    minimum.is_finite() && maximum.is_finite() && minimum > 0.0 && maximum >= minimum
}

#[cfg(test)]
mod tests {
    use mh370_domain::{Degrees, NauticalMiles, Seconds};

    use super::*;

    fn impact(position: LatLon) -> ImpactState {
        ImpactState {
            point: ImpactPoint {
                time: Seconds(1_000.0),
                position,
                bearing_true: Degrees(180.0),
                displacement_from_last_contact: NauticalMiles(0.0),
            },
            mass_kg: 174_000.0,
            east_velocity_m_s: 80.0,
            north_velocity_m_s: 0.0,
            up_velocity_m_s: -100.0,
            pitch_deg: -35.0,
            roll_deg: 0.0,
            yaw_true_deg: 180.0,
            contact_duration_s: 2.0,
        }
    }

    fn station_model(station_name: &str, position: LatLon) -> StationPredictionModel {
        StationPredictionModel {
            propagation: PropagationFamily {
                name: "sofar_group_celerity_sensitivity".to_string(),
                celerity_km_s: ClosedInterval::new(1.45, 1.55).unwrap(),
                dispersion_duration_s: ClosedInterval::new(8.0, 18.0).unwrap(),
            },
            path: PathFamily {
                name: "uncalibrated_path_sensitivity".to_string(),
                bathymetry_basis: "declared_fixture".to_string(),
                pressure_exposure_transfer_pa2_s_per_j: ClosedInterval::new(1.0e-12, 4.0e-12)
                    .unwrap(),
            },
            response: StationResponseFamily {
                name: "flat_band_fixture".to_string(),
                station_name: station_name.to_string(),
                station: position,
                amplitude_gain: ClosedInterval::new(0.8, 1.2).unwrap(),
            },
        }
    }

    fn model(stations: Vec<StationPredictionModel>) -> ForwardModel {
        ForwardModel {
            source: SourceCouplingFamily {
                name: "broad_impact_coupling_sensitivity".to_string(),
                energy_basis: EnergyBasis::TotalVelocity,
                acoustic_energy_fraction: ClosedInterval::new(1.0e-8, 1.0e-5).unwrap(),
                minimum_frequency_hz: 1.0,
                maximum_frequency_hz: 40.0,
            },
            stations,
        }
    }

    #[test]
    fn overlay_never_returns_a_likelihood() {
        let event = HydroEvent {
            name: "context".to_string(),
            station: LatLon::new(-7.0, 72.0).unwrap(),
            arrival_time_s: 20_000.0,
            minimum_speed_km_s: 1.45,
            maximum_speed_km_s: 1.55,
            timing_sd_s: 60.0,
            role: HydroRole::OverlayOnly,
        };
        let score = event
            .score(impact(LatLon::new(-30.0, 95.0).unwrap()).point)
            .unwrap();
        assert!(score.distance_km > 0.0);
        assert!(score.log_likelihood.is_none());
        assert!(score.predicted_arrival_max_s >= score.predicted_arrival_min_s);
    }

    #[test]
    fn zero_range_has_zero_travel_time_and_no_likelihood() {
        let position = LatLon::new(-35.0, 92.0).unwrap();
        let prediction = model(vec![station_model("coincident", position)])
            .predict(impact(position))
            .unwrap()
            .remove(0);
        assert_eq!(prediction.distance_km, 0.0);
        assert_eq!(prediction.arrival_time_s.minimum, 1_000.0);
        assert_eq!(prediction.arrival_time_s.maximum, 1_000.0);
        assert!(!prediction.likelihood_evaluated);
    }

    #[test]
    fn cape_leeuwin_and_diego_garcia_arrivals_match_independent_scale() {
        let source = LatLon::new(-34.9167, 92.0472).unwrap();
        let predictions = model(vec![
            station_model("Cape Leeuwin H01W", LatLon::new(-34.892, 114.141).unwrap()),
            station_model("Diego Garcia H08S", LatLon::new(-7.639, 72.484).unwrap()),
        ])
        .predict(impact(source))
        .unwrap();

        assert!((predictions[0].distance_km - 2_011.0).abs() < 10.0);
        assert!((predictions[1].distance_km - 3_632.0).abs() < 15.0);
        let leeuwin_mid_travel = 0.5
            * (predictions[0].arrival_time_s.minimum + predictions[0].arrival_time_s.maximum)
            - 1_000.0;
        let diego_mid_travel = 0.5
            * (predictions[1].arrival_time_s.minimum + predictions[1].arrival_time_s.maximum)
            - 1_000.0;
        assert!((leeuwin_mid_travel / 60.0 - 22.4).abs() < 0.2);
        assert!((diego_mid_travel / 60.0 - 40.5).abs() < 0.3);
    }

    #[test]
    fn energy_and_pressure_follow_declared_limiting_scales() {
        let position = LatLon::new(-35.0, 92.0).unwrap();
        let base = impact(position);
        let forward = model(vec![station_model(
            "Cape Leeuwin H01W",
            LatLon::new(-34.892, 114.141).unwrap(),
        )]);
        let first = forward.predict(base).unwrap().remove(0);
        let mut faster = base;
        faster.east_velocity_m_s *= 2.0;
        faster.north_velocity_m_s *= 2.0;
        faster.up_velocity_m_s *= 2.0;
        let second = forward.predict(faster).unwrap().remove(0);

        assert!(
            (second.incident_kinetic_energy_j / first.incident_kinetic_energy_j - 4.0).abs()
                < 1e-12
        );
        assert!(
            (second.rms_pressure_pa.minimum / first.rms_pressure_pa.minimum - 2.0).abs() < 1e-12
        );
        assert!(
            (second.rms_pressure_pa.maximum / first.rms_pressure_pa.maximum - 2.0).abs() < 1e-12
        );
    }

    #[test]
    fn vertical_basis_excludes_horizontal_energy() {
        let state = impact(LatLon::new(-35.0, 92.0).unwrap());
        let expected = 0.5 * state.mass_kg * state.up_velocity_m_s.powi(2);
        assert_eq!(
            state
                .kinetic_energy_j(EnergyBasis::VerticalVelocity)
                .unwrap(),
            expected
        );
        assert!(state.kinetic_energy_j(EnergyBasis::TotalVelocity).unwrap() > expected);
    }

    #[test]
    fn invalid_or_uncommissioned_models_fail_closed() {
        let position = LatLon::new(-35.0, 92.0).unwrap();
        assert_eq!(
            model(Vec::new()).predict(impact(position)),
            Err(HydroError::NoStations)
        );

        let mut invalid = model(vec![station_model("H01W", position)]);
        invalid.source.acoustic_energy_fraction.maximum = 1.1;
        assert_eq!(
            invalid.predict(impact(position)),
            Err(HydroError::InvalidSourceFamily)
        );
    }
}
