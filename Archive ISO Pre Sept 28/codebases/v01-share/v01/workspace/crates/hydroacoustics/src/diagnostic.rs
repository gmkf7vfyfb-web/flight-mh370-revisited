//! Typed, zero-weight forward and reverse hydroacoustic diagnostics.
//!
//! These types are the narrow handoff between an impact ensemble and a
//! hydroacoustic source-grid report. They intentionally cannot express an
//! observed-signal likelihood. A later calibrated likelihood needs a new API
//! backed by raw-channel injections and complete-search false-alarm controls.

use std::collections::{BTreeMap, BTreeSet};

use mh370_domain::{great_circle_distance_nm, LatLon};
use serde::{Deserialize, Serialize};
use thiserror::Error;

use crate::{ClosedInterval, ForwardModel, HydroError, ImpactState, StationPrediction};

const KM_PER_NM: f64 = 1.852;
const NORMALIZATION_TOLERANCE: f64 = 1.0e-10;

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct DiagnosticSourceCell {
    pub id: String,
    pub along_arc_nm: f64,
    pub cross_arc_nm: f64,
    pub position_wgs84: LatLon,
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct DiagnosticImpactScenario {
    pub id: String,
    pub source_cell_id: String,
    pub sampling_weight: f64,
    pub impact: ImpactState,
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct DiagnosticGridInput {
    pub schema_id: String,
    pub schema_version: u32,
    pub source_grid_family: String,
    pub cells: Vec<DiagnosticSourceCell>,
    pub scenarios: Vec<DiagnosticImpactScenario>,
    pub forward_model: ForwardModel,
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct ForwardScenarioPrediction {
    pub scenario_id: String,
    pub source_cell_id: String,
    pub sampling_weight: f64,
    pub stations: Vec<StationPrediction>,
    /// Always false in schema v1. The result is a posterior-predictive overlay.
    pub likelihood_evaluated: bool,
    /// Always zero. It is present so reports cannot silently treat the overlay
    /// as a particle-weight update.
    pub log_weight_increment: f64,
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct DiagnosticGridOutput {
    pub schema_id: String,
    pub schema_version: u32,
    pub source_grid_family: String,
    pub predictions: Vec<ForwardScenarioPrediction>,
    pub evidence_disposition: String,
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct ObservedStationWindow {
    pub station_name: String,
    pub station: LatLon,
    pub arrival_time_utc_unix_s: ClosedInterval,
    /// Optional source-reported station-to-source bearing. It is a joint part
    /// of this selected window, never an independent observation.
    pub bearing_true_deg: Option<f64>,
    pub bearing_half_width_deg: Option<f64>,
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct ReverseTraceInput {
    pub schema_id: String,
    pub schema_version: u32,
    pub request_id: String,
    pub source_grid_family: String,
    pub cells: Vec<DiagnosticSourceCell>,
    pub station_windows: Vec<ObservedStationWindow>,
    pub impact_time_utc_unix_s: ClosedInterval,
    pub celerity_km_s: ClosedInterval,
    pub unresolved_path_timing_s: ClosedInterval,
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct ReverseCellMatch {
    pub source_cell_id: String,
    pub position_wgs84: LatLon,
    pub compatible_impact_time_utc_unix_s: ClosedInterval,
    pub station_distance_km: BTreeMap<String, f64>,
    pub station_bearing_residual_deg: BTreeMap<String, f64>,
    pub likelihood_evaluated: bool,
    pub log_weight_increment: f64,
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct ReverseTraceOutput {
    pub schema_id: String,
    pub schema_version: u32,
    pub request_id: String,
    pub source_grid_family: String,
    pub matches: Vec<ReverseCellMatch>,
    pub evidence_disposition: String,
}

#[derive(Debug, Error, Clone, PartialEq)]
pub enum DiagnosticGridError {
    #[error("unsupported diagnostic hydroacoustic schema")]
    UnsupportedSchema,
    #[error("invalid diagnostic source cell")]
    InvalidCell,
    #[error("duplicate diagnostic source-cell identity")]
    DuplicateCell,
    #[error("invalid diagnostic impact scenario")]
    InvalidScenario,
    #[error("duplicate diagnostic impact-scenario identity")]
    DuplicateScenario,
    #[error("scenario weights are not normalized")]
    UnnormalizedScenarioWeights,
    #[error("invalid observed station window")]
    InvalidStationWindow,
    #[error("at least one station window is required")]
    NoStationWindows,
    #[error("duplicate station-window name")]
    DuplicateStationWindow,
    #[error("invalid reverse-trace input")]
    InvalidReverseInput,
    #[error(transparent)]
    Forward(#[from] HydroError),
}

pub const DIAGNOSTIC_GRID_SCHEMA_ID: &str = "mh370-hydroacoustic-diagnostic-grid";
pub const DIAGNOSTIC_GRID_SCHEMA_VERSION: u32 = 1;
pub const REVERSE_TRACE_SCHEMA_ID: &str = "mh370-hydroacoustic-reverse-trace";
pub const REVERSE_TRACE_SCHEMA_VERSION: u32 = 1;

pub fn predict_diagnostic_grid(
    input: &DiagnosticGridInput,
) -> Result<DiagnosticGridOutput, DiagnosticGridError> {
    let cells = validate_cells(&input.cells)?;
    validate_schema(
        &input.schema_id,
        input.schema_version,
        DIAGNOSTIC_GRID_SCHEMA_ID,
        DIAGNOSTIC_GRID_SCHEMA_VERSION,
    )?;
    if input.source_grid_family.trim().is_empty() || input.scenarios.is_empty() {
        return Err(DiagnosticGridError::InvalidScenario);
    }
    input.forward_model.validate()?;

    let mut scenario_ids = BTreeSet::new();
    let mut weight_sum = 0.0;
    let mut predictions = Vec::with_capacity(input.scenarios.len());
    for scenario in &input.scenarios {
        if scenario.id.trim().is_empty()
            || !cells.contains_key(scenario.source_cell_id.as_str())
            || !scenario.sampling_weight.is_finite()
            || scenario.sampling_weight < 0.0
        {
            return Err(DiagnosticGridError::InvalidScenario);
        }
        if !scenario_ids.insert(scenario.id.as_str()) {
            return Err(DiagnosticGridError::DuplicateScenario);
        }
        let expected = cells[scenario.source_cell_id.as_str()].position_wgs84;
        if scenario.impact.point.position != expected {
            return Err(DiagnosticGridError::InvalidScenario);
        }
        weight_sum += scenario.sampling_weight;
        predictions.push(ForwardScenarioPrediction {
            scenario_id: scenario.id.clone(),
            source_cell_id: scenario.source_cell_id.clone(),
            sampling_weight: scenario.sampling_weight,
            stations: input.forward_model.predict(scenario.impact)?,
            likelihood_evaluated: false,
            log_weight_increment: 0.0,
        });
    }
    if (weight_sum - 1.0).abs() > NORMALIZATION_TOLERANCE {
        return Err(DiagnosticGridError::UnnormalizedScenarioWeights);
    }

    Ok(DiagnosticGridOutput {
        schema_id: DIAGNOSTIC_GRID_SCHEMA_ID.to_string(),
        schema_version: DIAGNOSTIC_GRID_SCHEMA_VERSION,
        source_grid_family: input.source_grid_family.clone(),
        predictions,
        evidence_disposition: "diagnostic_zero_weight".to_string(),
    })
}

pub fn reverse_trace_windows(
    input: &ReverseTraceInput,
) -> Result<ReverseTraceOutput, DiagnosticGridError> {
    validate_schema(
        &input.schema_id,
        input.schema_version,
        REVERSE_TRACE_SCHEMA_ID,
        REVERSE_TRACE_SCHEMA_VERSION,
    )?;
    let cells = validate_cells(&input.cells)?;
    if input.request_id.trim().is_empty()
        || input.source_grid_family.trim().is_empty()
        || input.station_windows.is_empty()
        || input.impact_time_utc_unix_s.validate_nonnegative().is_err()
        || input.celerity_km_s.validate_nonnegative().is_err()
        || input.celerity_km_s.minimum <= 0.0
        || input
            .unresolved_path_timing_s
            .validate_nonnegative()
            .is_err()
    {
        return if input.station_windows.is_empty() {
            Err(DiagnosticGridError::NoStationWindows)
        } else {
            Err(DiagnosticGridError::InvalidReverseInput)
        };
    }

    let mut station_names = BTreeSet::new();
    for window in &input.station_windows {
        if window.station_name.trim().is_empty()
            || !valid_position(window.station)
            || window
                .arrival_time_utc_unix_s
                .validate_nonnegative()
                .is_err()
            || matches!(window.bearing_true_deg, Some(value) if !value.is_finite() || !(0.0..360.0).contains(&value))
            || matches!(window.bearing_half_width_deg, Some(value) if !value.is_finite() || !(0.0..=180.0).contains(&value))
            || window.bearing_true_deg.is_some() != window.bearing_half_width_deg.is_some()
        {
            return Err(DiagnosticGridError::InvalidStationWindow);
        }
        if !station_names.insert(window.station_name.as_str()) {
            return Err(DiagnosticGridError::DuplicateStationWindow);
        }
    }

    let mut matches = Vec::new();
    for cell in cells.values() {
        let mut compatible = Some(input.impact_time_utc_unix_s);
        let mut distances = BTreeMap::new();
        let mut bearing_residuals = BTreeMap::new();

        for window in &input.station_windows {
            let distance_km =
                great_circle_distance_nm(window.station, cell.position_wgs84).0 * KM_PER_NM;
            let earliest_travel =
                distance_km / input.celerity_km_s.maximum + input.unresolved_path_timing_s.minimum;
            let latest_travel =
                distance_km / input.celerity_km_s.minimum + input.unresolved_path_timing_s.maximum;
            let station_implied = ClosedInterval {
                minimum: window.arrival_time_utc_unix_s.minimum - latest_travel,
                maximum: window.arrival_time_utc_unix_s.maximum - earliest_travel,
            };
            compatible = compatible.and_then(|prior| prior.intersection(station_implied));
            distances.insert(window.station_name.clone(), distance_km);

            if let (Some(expected), Some(width)) =
                (window.bearing_true_deg, window.bearing_half_width_deg)
            {
                let actual = initial_bearing_deg(window.station, cell.position_wgs84);
                let residual = circular_residual_deg(actual, expected);
                bearing_residuals.insert(window.station_name.clone(), residual);
                if residual.abs() > width {
                    compatible = None;
                }
            }
        }

        if let Some(interval) = compatible {
            matches.push(ReverseCellMatch {
                source_cell_id: cell.id.clone(),
                position_wgs84: cell.position_wgs84,
                compatible_impact_time_utc_unix_s: interval,
                station_distance_km: distances,
                station_bearing_residual_deg: bearing_residuals,
                likelihood_evaluated: false,
                log_weight_increment: 0.0,
            });
        }
    }

    Ok(ReverseTraceOutput {
        schema_id: REVERSE_TRACE_SCHEMA_ID.to_string(),
        schema_version: REVERSE_TRACE_SCHEMA_VERSION,
        request_id: input.request_id.clone(),
        source_grid_family: input.source_grid_family.clone(),
        matches,
        evidence_disposition: "diagnostic_zero_weight".to_string(),
    })
}

fn validate_cells(
    cells: &[DiagnosticSourceCell],
) -> Result<BTreeMap<&str, &DiagnosticSourceCell>, DiagnosticGridError> {
    if cells.is_empty() {
        return Err(DiagnosticGridError::InvalidCell);
    }
    let mut result = BTreeMap::new();
    for cell in cells {
        if cell.id.trim().is_empty()
            || !cell.along_arc_nm.is_finite()
            || cell.along_arc_nm < 0.0
            || !cell.cross_arc_nm.is_finite()
            || !valid_position(cell.position_wgs84)
        {
            return Err(DiagnosticGridError::InvalidCell);
        }
        if result.insert(cell.id.as_str(), cell).is_some() {
            return Err(DiagnosticGridError::DuplicateCell);
        }
    }
    Ok(result)
}

fn validate_schema(
    schema_id: &str,
    schema_version: u32,
    expected_id: &str,
    expected_version: u32,
) -> Result<(), DiagnosticGridError> {
    if schema_id != expected_id || schema_version != expected_version {
        Err(DiagnosticGridError::UnsupportedSchema)
    } else {
        Ok(())
    }
}

fn valid_position(position: LatLon) -> bool {
    position.latitude.0.is_finite()
        && (-90.0..=90.0).contains(&position.latitude.0)
        && position.longitude.0.is_finite()
        && (-180.0..180.0).contains(&position.longitude.0)
}

fn initial_bearing_deg(from: LatLon, to: LatLon) -> f64 {
    let lat_1 = from.latitude.0.to_radians();
    let lat_2 = to.latitude.0.to_radians();
    let delta_lon = (to.longitude.0 - from.longitude.0).to_radians();
    let y = delta_lon.sin() * lat_2.cos();
    let x = lat_1.cos() * lat_2.sin() - lat_1.sin() * lat_2.cos() * delta_lon.cos();
    y.atan2(x).to_degrees().rem_euclid(360.0)
}

fn circular_residual_deg(actual: f64, expected: f64) -> f64 {
    (actual - expected + 180.0).rem_euclid(360.0) - 180.0
}

#[cfg(test)]
mod tests {
    use mh370_domain::{Degrees, ImpactPoint, NauticalMiles, Seconds};

    use super::*;
    use crate::{
        EnergyBasis, PathFamily, PropagationFamily, SourceCouplingFamily, StationPredictionModel,
        StationResponseFamily,
    };

    fn cell(id: &str, position: LatLon) -> DiagnosticSourceCell {
        DiagnosticSourceCell {
            id: id.to_string(),
            along_arc_nm: 100.0,
            cross_arc_nm: 0.0,
            position_wgs84: position,
        }
    }

    fn impact(position: LatLon, time_s: f64) -> ImpactState {
        ImpactState {
            point: ImpactPoint {
                time: Seconds(time_s),
                position,
                bearing_true: Degrees(180.0),
                displacement_from_last_contact: NauticalMiles(50.0),
            },
            mass_kg: 170_000.0,
            east_velocity_m_s: 20.0,
            north_velocity_m_s: -80.0,
            up_velocity_m_s: -100.0,
            pitch_deg: -30.0,
            roll_deg: 5.0,
            yaw_true_deg: 180.0,
            contact_duration_s: 1.0,
        }
    }

    fn model(station_position: LatLon) -> ForwardModel {
        ForwardModel {
            source: SourceCouplingFamily {
                name: "broad_source_sensitivity".to_string(),
                energy_basis: EnergyBasis::TotalVelocity,
                acoustic_energy_fraction: ClosedInterval::new(1.0e-8, 1.0e-4).unwrap(),
                minimum_frequency_hz: 2.0,
                maximum_frequency_hz: 40.0,
            },
            stations: vec![StationPredictionModel {
                propagation: PropagationFamily {
                    name: "celerity_fixture".to_string(),
                    celerity_km_s: ClosedInterval::new(1.45, 1.55).unwrap(),
                    dispersion_duration_s: ClosedInterval::new(1.0, 5.0).unwrap(),
                },
                path: PathFamily {
                    name: "path_fixture".to_string(),
                    bathymetry_basis: "fixture".to_string(),
                    pressure_exposure_transfer_pa2_s_per_j: ClosedInterval::new(1.0e-12, 2.0e-12)
                        .unwrap(),
                },
                response: StationResponseFamily {
                    name: "response_fixture".to_string(),
                    station_name: "H01W".to_string(),
                    station: station_position,
                    amplitude_gain: ClosedInterval::new(1.0, 1.0).unwrap(),
                },
            }],
        }
    }

    #[test]
    fn grid_predictions_are_explicitly_zero_weight() {
        let position = LatLon::new(-35.0, 92.0).unwrap();
        let input = DiagnosticGridInput {
            schema_id: DIAGNOSTIC_GRID_SCHEMA_ID.to_string(),
            schema_version: DIAGNOSTIC_GRID_SCHEMA_VERSION,
            source_grid_family: "seventh_arc_plus_minus_100nm".to_string(),
            cells: vec![cell("a020_x000", position)],
            scenarios: vec![DiagnosticImpactScenario {
                id: "scenario-1".to_string(),
                source_cell_id: "a020_x000".to_string(),
                sampling_weight: 1.0,
                impact: impact(position, 1_394_237_000.0),
            }],
            forward_model: model(LatLon::new(-34.892, 114.141).unwrap()),
        };
        let output = predict_diagnostic_grid(&input).unwrap();
        assert_eq!(output.evidence_disposition, "diagnostic_zero_weight");
        assert_eq!(output.predictions[0].log_weight_increment, 0.0);
        assert!(!output.predictions[0].likelihood_evaluated);
        assert!(!output.predictions[0].stations[0].likelihood_evaluated);
    }

    #[test]
    fn mismatched_cell_position_and_unnormalized_weights_fail() {
        let position = LatLon::new(-35.0, 92.0).unwrap();
        let mut input = DiagnosticGridInput {
            schema_id: DIAGNOSTIC_GRID_SCHEMA_ID.to_string(),
            schema_version: DIAGNOSTIC_GRID_SCHEMA_VERSION,
            source_grid_family: "grid".to_string(),
            cells: vec![cell("cell", position)],
            scenarios: vec![DiagnosticImpactScenario {
                id: "scenario".to_string(),
                source_cell_id: "cell".to_string(),
                sampling_weight: 0.5,
                impact: impact(position, 1_394_237_000.0),
            }],
            forward_model: model(position),
        };
        assert_eq!(
            predict_diagnostic_grid(&input),
            Err(DiagnosticGridError::UnnormalizedScenarioWeights)
        );
        input.scenarios[0].sampling_weight = 1.0;
        input.scenarios[0].impact.point.position = LatLon::new(-36.0, 92.0).unwrap();
        assert_eq!(
            predict_diagnostic_grid(&input),
            Err(DiagnosticGridError::InvalidScenario)
        );
    }

    #[test]
    fn duplicate_cell_and_scenario_identities_fail_closed() {
        let position = LatLon::new(-35.0, 92.0).unwrap();
        let mut input = DiagnosticGridInput {
            schema_id: DIAGNOSTIC_GRID_SCHEMA_ID.to_string(),
            schema_version: DIAGNOSTIC_GRID_SCHEMA_VERSION,
            source_grid_family: "grid".to_string(),
            cells: vec![cell("cell", position), cell("cell", position)],
            scenarios: vec![DiagnosticImpactScenario {
                id: "scenario".to_string(),
                source_cell_id: "cell".to_string(),
                sampling_weight: 1.0,
                impact: impact(position, 1_394_237_000.0),
            }],
            forward_model: model(position),
        };
        assert_eq!(
            predict_diagnostic_grid(&input),
            Err(DiagnosticGridError::DuplicateCell)
        );
        input.cells.pop();
        input.scenarios.push(input.scenarios[0].clone());
        input.scenarios[0].sampling_weight = 0.5;
        input.scenarios[1].sampling_weight = 0.5;
        assert_eq!(
            predict_diagnostic_grid(&input),
            Err(DiagnosticGridError::DuplicateScenario)
        );
    }

    #[test]
    fn reverse_trace_recovers_only_time_and_bearing_compatible_cell() {
        let station = LatLon::new(-34.892, 114.141).unwrap();
        let compatible = LatLon::new(-35.0, 92.0).unwrap();
        let incompatible = LatLon::new(-20.0, 92.0).unwrap();
        let travel_s = great_circle_distance_nm(station, compatible).0 * KM_PER_NM / 1.5;
        let impact_s = 1_394_237_000.0;
        let expected_bearing = initial_bearing_deg(station, compatible);
        let input = ReverseTraceInput {
            schema_id: REVERSE_TRACE_SCHEMA_ID.to_string(),
            schema_version: REVERSE_TRACE_SCHEMA_VERSION,
            request_id: "candidate".to_string(),
            source_grid_family: "grid".to_string(),
            cells: vec![cell("yes", compatible), cell("no", incompatible)],
            station_windows: vec![ObservedStationWindow {
                station_name: "H01W".to_string(),
                station,
                arrival_time_utc_unix_s: ClosedInterval::new(
                    impact_s + travel_s - 0.5,
                    impact_s + travel_s + 0.5,
                )
                .unwrap(),
                bearing_true_deg: Some(expected_bearing),
                bearing_half_width_deg: Some(1.0),
            }],
            impact_time_utc_unix_s: ClosedInterval::new(impact_s - 30.0, impact_s + 30.0).unwrap(),
            celerity_km_s: ClosedInterval::new(1.5, 1.5).unwrap(),
            unresolved_path_timing_s: ClosedInterval::new(0.0, 0.0).unwrap(),
        };
        let output = reverse_trace_windows(&input).unwrap();
        assert_eq!(output.matches.len(), 1);
        assert_eq!(output.matches[0].source_cell_id, "yes");
        assert_eq!(output.matches[0].log_weight_increment, 0.0);
    }
}
