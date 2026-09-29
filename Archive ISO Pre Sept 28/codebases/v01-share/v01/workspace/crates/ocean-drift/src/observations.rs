use mh370_domain::{great_circle_distance_nm, LatLon};
use serde::{Deserialize, Serialize};
use thiserror::Error;

use crate::{DriftPath, PathTerminationReason};

/// A piecewise-uniform model for elapsed time between coastal arrival and
/// discovery. Probabilities are masses, not likelihood powers.
#[derive(Debug, Clone, Copy, PartialEq, Serialize, Deserialize)]
pub struct DiscoveryDelayBin {
    pub start_days: f64,
    pub end_days: f64,
    pub probability: f64,
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct RecoveryEvent {
    pub id: String,
    /// Objects represented by this independent recovery episode. Co-located
    /// pieces from one discovery episode belong in one event so they are not
    /// multiplied as independent evidence.
    #[serde(default)]
    pub object_ids: Vec<String>,
    pub location: String,
    pub position: LatLon,
    /// Discovery interval, not an asserted beaching interval.
    pub discovery_start_unix_seconds: f64,
    pub discovery_end_unix_seconds: f64,
    /// Piecewise-uniform elapsed-time distribution from arrival to discovery.
    /// An empty vector retains the legacy uniform pre-discovery window.
    #[serde(default)]
    pub discovery_delay: Vec<DiscoveryDelayBin>,
    /// Sensitivity power retained for schema compatibility. New evidence
    /// configurations use one; dependence is represented by grouping objects.
    #[serde(default = "unit_evidence_weight")]
    pub evidence_weight: f64,
    #[serde(default)]
    pub is_flaperon: bool,
}

const fn unit_evidence_weight() -> f64 {
    1.0
}

#[derive(Debug, Clone, Copy, PartialEq, Serialize, Deserialize)]
pub struct GeographicBounds {
    pub south_degrees: f64,
    pub north_degrees: f64,
    pub west_degrees: f64,
    pub east_degrees: f64,
}

impl GeographicBounds {
    fn validate(self) -> bool {
        self.south_degrees.is_finite()
            && self.north_degrees.is_finite()
            && self.west_degrees.is_finite()
            && self.east_degrees.is_finite()
            && self.south_degrees >= -90.0
            && self.north_degrees <= 90.0
            && self.south_degrees < self.north_degrees
            && self.west_degrees >= -180.0
            && self.east_degrees <= 180.0
            && self.west_degrees < self.east_degrees
    }

    fn contains(self, position: LatLon) -> bool {
        (self.south_degrees..=self.north_degrees).contains(&position.latitude.0)
            && (self.west_degrees..=self.east_degrees).contains(&position.longitude.0)
    }
}

/// Negative evidence from a monitored region with no reported recovery.
///
/// `expected_reportable_items` is the Poisson exposure: the expected number
/// of independently reportable objects if every simulated object in this
/// motion family reached the region. It deliberately remains an explicit
/// sensitivity parameter because search effort and reporting probability are
/// not calibrated measurements.
#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct NonRecoveryObservation {
    pub id: String,
    pub location: String,
    pub bounds: GeographicBounds,
    pub observation_start_unix_seconds: f64,
    pub observation_end_unix_seconds: f64,
    pub expected_reportable_items: f64,
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct DebrisEvidence {
    pub events: Vec<RecoveryEvent>,
    /// Legacy fallback when an event has no explicit discovery-delay bins.
    pub pre_discovery_window_days: f64,
    pub spatial_bandwidth_km: f64,
    pub probability_floor: f64,
    #[serde(default)]
    pub non_recoveries: Vec<NonRecoveryObservation>,
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct RecoveryEvaluation {
    pub event_id: String,
    pub object_count: usize,
    #[serde(default)]
    pub is_flaperon: bool,
    pub mean_encounter_weight: f64,
    pub effective_sample_size: f64,
    pub evidence_weight: f64,
    /// Complete bounded recovery contribution, including the configured
    /// probability floor and evidence power.
    #[serde(default)]
    pub log_compatibility: f64,
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct NonRecoveryEvaluation {
    pub observation_id: String,
    pub estimated_landfall_probability: f64,
    /// Paths that failed before the observation ended. They count against
    /// compatibility so missing fields can never make non-recovery look more
    /// supportive.
    pub unresolved_path_probability: f64,
    pub conservative_scoring_probability: f64,
    pub effective_sample_size: f64,
    pub log_compatibility: f64,
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct DebrisEvaluation {
    pub log_compatibility: f64,
    pub recoveries: Vec<RecoveryEvaluation>,
    pub non_recoveries: Vec<NonRecoveryEvaluation>,
}

#[derive(Debug, Error, Clone, PartialEq)]
pub enum DebrisObservationError {
    #[error("debris evidence configuration is invalid")]
    InvalidConfiguration,
    #[error("debris trajectory ensemble is empty")]
    EmptyEnsemble,
    #[error("flaperon event is absent or duplicated")]
    InvalidFlaperonEvent,
}

impl DebrisEvidence {
    pub fn validate(&self) -> Result<(), DebrisObservationError> {
        if (self.events.is_empty() && self.non_recoveries.is_empty())
            || !self.pre_discovery_window_days.is_finite()
            || self.pre_discovery_window_days <= 0.0
            || !self.spatial_bandwidth_km.is_finite()
            || self.spatial_bandwidth_km <= 0.0
            || !self.probability_floor.is_finite()
            || !(0.0..0.1).contains(&self.probability_floor)
        {
            return Err(DebrisObservationError::InvalidConfiguration);
        }
        for event in &self.events {
            if event.id.trim().is_empty()
                || event.location.trim().is_empty()
                || !event.discovery_start_unix_seconds.is_finite()
                || !event.discovery_end_unix_seconds.is_finite()
                || event.discovery_end_unix_seconds < event.discovery_start_unix_seconds
                || !event.evidence_weight.is_finite()
                || !(0.0..=1.0).contains(&event.evidence_weight)
                || !valid_delay(&event.discovery_delay)
            {
                return Err(DebrisObservationError::InvalidConfiguration);
            }
        }
        for observation in &self.non_recoveries {
            if observation.id.trim().is_empty()
                || observation.location.trim().is_empty()
                || !observation.bounds.validate()
                || !observation.observation_start_unix_seconds.is_finite()
                || !observation.observation_end_unix_seconds.is_finite()
                || observation.observation_end_unix_seconds
                    <= observation.observation_start_unix_seconds
                || !observation.expected_reportable_items.is_finite()
                || observation.expected_reportable_items <= 0.0
            {
                return Err(DebrisObservationError::InvalidConfiguration);
            }
        }
        Ok(())
    }

    pub fn evaluate(
        &self,
        paths: &[DriftPath],
    ) -> Result<DebrisEvaluation, DebrisObservationError> {
        self.validate()?;
        if paths.is_empty() {
            return Err(DebrisObservationError::EmptyEnsemble);
        }
        let mut total_log_compatibility = 0.0;
        let mut recoveries = Vec::with_capacity(self.events.len());
        for event in &self.events {
            let weights = self.arrival_weights(paths, event);
            // Importance weights have mean one under the physical transport
            // law. Terminated paths remain in the denominator with zero
            // encounter contribution, so this is not survivor-conditioned.
            let mean = (weights.iter().sum::<f64>() / weights.len() as f64).clamp(0.0, 1.0);
            let probability = self.probability_floor + (1.0 - self.probability_floor) * mean;
            let log_compatibility = event.evidence_weight * probability.ln();
            total_log_compatibility += log_compatibility;
            recoveries.push(RecoveryEvaluation {
                event_id: event.id.clone(),
                object_count: event.object_ids.len().max(1),
                is_flaperon: event.is_flaperon,
                mean_encounter_weight: mean,
                effective_sample_size: effective_sample_size(&weights),
                evidence_weight: event.evidence_weight,
                log_compatibility,
            });
        }

        let mut non_recoveries = Vec::with_capacity(self.non_recoveries.len());
        for observation in &self.non_recoveries {
            let evaluation = evaluate_non_recovery(paths, observation);
            total_log_compatibility += evaluation.log_compatibility;
            non_recoveries.push(evaluation);
        }
        Ok(DebrisEvaluation {
            log_compatibility: total_log_compatibility,
            recoveries,
            non_recoveries,
        })
    }

    pub fn flaperon_arrival_weights(
        &self,
        paths: &[DriftPath],
    ) -> Result<Vec<f64>, DebrisObservationError> {
        let event = self.flaperon_event()?;
        Ok(self.arrival_weights(paths, event))
    }

    pub fn flaperon_event(&self) -> Result<&RecoveryEvent, DebrisObservationError> {
        let mut events = self.events.iter().filter(|event| event.is_flaperon);
        let event = events
            .next()
            .ok_or(DebrisObservationError::InvalidFlaperonEvent)?;
        if events.next().is_some() {
            return Err(DebrisObservationError::InvalidFlaperonEvent);
        }
        Ok(event)
    }

    fn arrival_weights(&self, paths: &[DriftPath], event: &RecoveryEvent) -> Vec<f64> {
        paths
            .iter()
            .map(|path| {
                let encounter = path
                    .points
                    .iter()
                    .map(|point| {
                        let distance_km =
                            great_circle_distance_nm(point.position, event.position).0 * 1.852;
                        let spatial =
                            (-0.5 * (distance_km / self.spatial_bandwidth_km).powi(2)).exp();
                        spatial * self.delay_compatibility(event, point.unix_seconds)
                    })
                    .fold(0.0, f64::max);
                path.importance_weight() * encounter
            })
            .collect()
    }

    fn delay_compatibility(&self, event: &RecoveryEvent, arrival_time: f64) -> f64 {
        let fallback;
        let bins = if event.discovery_delay.is_empty() {
            fallback = [DiscoveryDelayBin {
                start_days: 0.0,
                end_days: self.pre_discovery_window_days,
                probability: 1.0,
            }];
            &fallback[..]
        } else {
            &event.discovery_delay
        };
        let required_start = (event.discovery_start_unix_seconds - arrival_time) / 86_400.0;
        let required_end = (event.discovery_end_unix_seconds - arrival_time) / 86_400.0;
        if required_end < 0.0 {
            return 0.0;
        }
        let maximum_density = bins
            .iter()
            .map(|bin| bin.probability / (bin.end_days - bin.start_days))
            .fold(0.0, f64::max);
        let discovery_width = required_end - required_start;
        let density = if discovery_width > 1e-12 {
            bins.iter()
                .map(|bin| {
                    let overlap = (required_end.min(bin.end_days)
                        - required_start.max(bin.start_days))
                    .max(0.0);
                    overlap * bin.probability / (bin.end_days - bin.start_days)
                })
                .sum::<f64>()
                / discovery_width
        } else {
            bins.iter()
                .filter(|bin| required_start >= bin.start_days && required_start <= bin.end_days)
                .map(|bin| bin.probability / (bin.end_days - bin.start_days))
                .sum::<f64>()
        };
        (density / maximum_density).clamp(0.0, 1.0)
    }
}

fn valid_delay(bins: &[DiscoveryDelayBin]) -> bool {
    if bins.is_empty() {
        return true;
    }
    let mut previous_end = 0.0;
    let mut total = 0.0;
    for (index, bin) in bins.iter().enumerate() {
        if !bin.start_days.is_finite()
            || !bin.end_days.is_finite()
            || !bin.probability.is_finite()
            || bin.start_days < 0.0
            || bin.end_days <= bin.start_days
            || bin.probability <= 0.0
            || (index > 0 && bin.start_days < previous_end)
        {
            return false;
        }
        previous_end = bin.end_days;
        total += bin.probability;
    }
    (total - 1.0).abs() <= 1e-9
}

fn evaluate_non_recovery(
    paths: &[DriftPath],
    observation: &NonRecoveryObservation,
) -> NonRecoveryEvaluation {
    let mut landfall_weights = Vec::with_capacity(paths.len());
    let mut unresolved_weights = Vec::with_capacity(paths.len());
    let mut conservative_weights = Vec::with_capacity(paths.len());
    for path in paths {
        let importance = path.importance_weight();
        let landfall = path.termination.as_ref().is_some_and(|termination| {
            matches!(
                termination.reason,
                PathTerminationReason::LandEncounter | PathTerminationReason::Beaching
            ) && termination.unix_seconds >= observation.observation_start_unix_seconds
                && termination.unix_seconds <= observation.observation_end_unix_seconds
                && termination
                    .position
                    .is_some_and(|position| observation.bounds.contains(position))
        });
        let unresolved = path.termination.as_ref().is_some_and(|termination| {
            matches!(
                termination.reason,
                PathTerminationReason::MissingFieldCoverage
                    | PathTerminationReason::OutsideSpatialSupport
                    | PathTerminationReason::OutsideTimeSupport
                    | PathTerminationReason::NumericalFailure
            ) && termination.unix_seconds <= observation.observation_end_unix_seconds
        }) || (path.termination.is_none()
            && path.points.last().map_or(true, |point| {
                point.unix_seconds < observation.observation_end_unix_seconds
            }));
        landfall_weights.push(if landfall { importance } else { 0.0 });
        unresolved_weights.push(if unresolved { importance } else { 0.0 });
        conservative_weights.push(if landfall || unresolved {
            importance
        } else {
            0.0
        });
    }
    let count = paths.len() as f64;
    let landfall = (landfall_weights.iter().sum::<f64>() / count).clamp(0.0, 1.0);
    let unresolved = (unresolved_weights.iter().sum::<f64>() / count).clamp(0.0, 1.0);
    let conservative = (conservative_weights.iter().sum::<f64>() / count).clamp(0.0, 1.0);
    NonRecoveryEvaluation {
        observation_id: observation.id.clone(),
        estimated_landfall_probability: landfall,
        unresolved_path_probability: unresolved,
        conservative_scoring_probability: conservative,
        effective_sample_size: effective_sample_size(&conservative_weights),
        log_compatibility: -observation.expected_reportable_items * conservative,
    }
}

fn effective_sample_size(weights: &[f64]) -> f64 {
    let sum = weights.iter().sum::<f64>();
    let sum_of_squares = weights.iter().map(|weight| weight * weight).sum::<f64>();
    if sum_of_squares > 0.0 {
        sum * sum / sum_of_squares
    } else {
        0.0
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::{DriftPoint, PathTermination};

    fn event(delay: Vec<DiscoveryDelayBin>) -> RecoveryEvent {
        RecoveryEvent {
            id: "reunion-flaperon".to_string(),
            object_ids: vec!["right-flaperon".to_string()],
            location: "Reunion".to_string(),
            position: LatLon::new(-21.0, 55.5).unwrap(),
            discovery_start_unix_seconds: 100.0 * 86_400.0,
            discovery_end_unix_seconds: 100.0 * 86_400.0,
            discovery_delay: delay,
            evidence_weight: 1.0,
            is_flaperon: true,
        }
    }

    fn evidence(event: RecoveryEvent) -> DebrisEvidence {
        DebrisEvidence {
            events: vec![event],
            pre_discovery_window_days: 30.0,
            spatial_bandwidth_km: 100.0,
            probability_floor: 1e-6,
            non_recoveries: Vec::new(),
        }
    }

    fn path(day: f64, position: LatLon) -> DriftPath {
        DriftPath {
            points: vec![DriftPoint {
                unix_seconds: day * 86_400.0,
                position,
            }],
            termination: None,
            log_importance_weight: 0.0,
        }
    }

    #[test]
    fn legacy_recovery_window_is_not_exact_beaching_time() {
        let evaluation = evidence(event(Vec::new()))
            .evaluate(&[path(80.0, LatLon::new(-21.0, 55.5).unwrap())])
            .unwrap();
        assert_eq!(evaluation.recoveries[0].mean_encounter_weight, 1.0);
    }

    #[test]
    fn delay_bins_change_compatibility_without_multiplying_discovery_rows() {
        let model = evidence(event(vec![
            DiscoveryDelayBin {
                start_days: 0.0,
                end_days: 10.0,
                probability: 0.8,
            },
            DiscoveryDelayBin {
                start_days: 10.0,
                end_days: 50.0,
                probability: 0.2,
            },
        ]));
        let near = model
            .evaluate(&[path(95.0, LatLon::new(-21.0, 55.5).unwrap())])
            .unwrap();
        let delayed = model
            .evaluate(&[path(80.0, LatLon::new(-21.0, 55.5).unwrap())])
            .unwrap();
        let impossible = model
            .evaluate(&[path(40.0, LatLon::new(-21.0, 55.5).unwrap())])
            .unwrap();
        assert_eq!(near.recoveries[0].mean_encounter_weight, 1.0);
        assert!((delayed.recoveries[0].mean_encounter_weight - 0.0625).abs() < 1e-12);
        assert_eq!(impossible.recoveries[0].mean_encounter_weight, 0.0);
    }

    #[test]
    fn co_recovered_objects_are_one_likelihood_factor() {
        let mut grouped = event(Vec::new());
        grouped.object_ids = vec!["panel-a".to_string(), "panel-b".to_string()];
        let result = evidence(grouped)
            .evaluate(&[path(90.0, LatLon::new(-21.0, 55.5).unwrap())])
            .unwrap();
        assert_eq!(result.recoveries.len(), 1);
        assert_eq!(result.recoveries[0].object_count, 2);
        assert_eq!(result.log_compatibility, 0.0);
    }

    #[test]
    fn australian_non_recovery_penalizes_landfall_and_unresolved_coverage() {
        let observation = NonRecoveryObservation {
            id: "western-australia-no-recovery".to_string(),
            location: "Western Australia".to_string(),
            bounds: GeographicBounds {
                south_degrees: -40.0,
                north_degrees: -10.0,
                west_degrees: 110.0,
                east_degrees: 130.0,
            },
            observation_start_unix_seconds: 0.0,
            observation_end_unix_seconds: 100.0 * 86_400.0,
            expected_reportable_items: 2.0,
        };
        let terminate = |reason: PathTerminationReason, position: Option<LatLon>| DriftPath {
            points: vec![DriftPoint {
                unix_seconds: 20.0 * 86_400.0,
                position: position.unwrap_or(LatLon::new(0.0, 0.0).unwrap()),
            }],
            termination: Some(PathTermination {
                unix_seconds: 20.0 * 86_400.0,
                position,
                reason,
                detail: "fixture".to_string(),
            }),
            log_importance_weight: 0.0,
        };
        let paths = vec![
            terminate(
                PathTerminationReason::LandEncounter,
                Some(LatLon::new(-30.0, 115.0).unwrap()),
            ),
            terminate(PathTerminationReason::MissingFieldCoverage, None),
            terminate(
                PathTerminationReason::LandEncounter,
                Some(LatLon::new(-20.0, 55.0).unwrap()),
            ),
            path(100.0, LatLon::new(-20.0, 70.0).unwrap()),
        ];
        let result = evaluate_non_recovery(&paths, &observation);
        assert_eq!(result.estimated_landfall_probability, 0.25);
        assert_eq!(result.unresolved_path_probability, 0.25);
        assert_eq!(result.conservative_scoring_probability, 0.5);
        assert_eq!(result.log_compatibility, -1.0);
    }
}
