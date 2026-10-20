use mh370_domain::great_circle_distance_nm;
use mh370_domain::{AircraftState, LatLon};
use mh370_particle_filter::{FilterResult, SmcError};
use serde::{Deserialize, Serialize};

use crate::{SyntheticDataset, SyntheticError, ValidationThresholds};

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct SyntheticSummary {
    pub status: String,
    pub passed: bool,
    pub failures: Vec<String>,
    pub particles: usize,
    pub observations: usize,
    pub final_truth: AircraftState,
    pub posterior_mean: AircraftState,
    pub final_mean_error_nm: f64,
    pub posterior_latitude_95_deg: [f64; 2],
    pub mass_within_50_nm: f64,
    pub mass_within_100_nm: f64,
    pub final_ess: f64,
    pub log_evidence: f64,
    pub ancestor_resampling_count: usize,
    pub posterior_resampling_count: usize,
}

fn weighted_quantile(mut values: Vec<(f64, f64)>, probability: f64) -> f64 {
    values.sort_by(|first, second| first.0.total_cmp(&second.0));
    let total = values.iter().map(|(_, weight)| weight).sum::<f64>();
    let target = probability * total;
    let mut cumulative = 0.0;
    for (value, weight) in values {
        cumulative += weight;
        if cumulative >= target {
            return value;
        }
    }
    unreachable!("positive normalized weights have a terminal quantile")
}

fn circular_mean_degrees(values: impl Iterator<Item = (f64, f64)>) -> f64 {
    let mut sine = 0.0;
    let mut cosine = 0.0;
    for (degrees, weight) in values {
        sine += weight * degrees.to_radians().sin();
        cosine += weight * degrees.to_radians().cos();
    }
    sine.atan2(cosine).to_degrees()
}

pub fn summarize_synthetic(
    dataset: &SyntheticDataset,
    filter: &FilterResult<AircraftState>,
    thresholds: &ValidationThresholds,
) -> Result<SyntheticSummary, SyntheticError> {
    if filter.particles.is_empty()
        || filter.particles.len() != filter.log_weights.len()
        || dataset.truth_states.len() != dataset.observations.len() + 1
    {
        return Err(SyntheticError::Filter(SmcError::InvalidWeights));
    }
    let weights = filter.normalized_weights();
    let final_truth = *dataset
        .truth_states
        .last()
        .ok_or(SyntheticError::Filter(SmcError::InvalidWeights))?;

    let weighted = |selector: fn(&AircraftState) -> f64| {
        filter
            .particles
            .iter()
            .zip(&weights)
            .map(|(state, weight)| selector(state) * weight)
            .sum::<f64>()
    };
    let mean_position = LatLon::new(
        weighted(|state| state.position.latitude.0),
        circular_mean_degrees(
            filter
                .particles
                .iter()
                .zip(&weights)
                .map(|(state, weight)| (state.position.longitude.0, *weight)),
        ),
    )
    .map_err(|_| SyntheticError::InvalidCoordinate)?;
    let posterior_mean = AircraftState {
        time: final_truth.time,
        position: mean_position,
        altitude: mh370_domain::Feet(weighted(|state| state.altitude.0)),
        track_true: mh370_domain::Degrees(circular_mean_degrees(
            filter
                .particles
                .iter()
                .zip(&weights)
                .map(|(state, weight)| (state.track_true.0, *weight)),
        ))
        .wrapped_360(),
        ground_speed: mh370_domain::Knots(weighted(|state| state.ground_speed.0)),
        vertical_speed: mh370_domain::FeetPerMinute(weighted(|state| state.vertical_speed.0)),
        bfo_bias: mh370_domain::Hertz(weighted(|state| state.bfo_bias.0)),
    };
    let final_mean_error_nm =
        great_circle_distance_nm(posterior_mean.position, final_truth.position).0;
    let mass_within = |radius_nm: f64| {
        filter
            .particles
            .iter()
            .zip(&weights)
            .filter_map(|(state, weight)| {
                (great_circle_distance_nm(state.position, final_truth.position).0 <= radius_nm)
                    .then_some(*weight)
            })
            .sum::<f64>()
    };
    let final_ess = filter.effective_sample_size()?;
    let latitude_values = filter
        .particles
        .iter()
        .zip(&weights)
        .map(|(state, weight)| (state.position.latitude.0, *weight))
        .collect::<Vec<_>>();

    let mut failures = Vec::new();
    let mass_within_100_nm = mass_within(100.0);
    if final_mean_error_nm > thresholds.maximum_final_mean_error_nm {
        failures.push(format!(
            "final mean error {:.3} NM exceeds {:.3} NM",
            final_mean_error_nm, thresholds.maximum_final_mean_error_nm
        ));
    }
    if mass_within_100_nm < thresholds.minimum_mass_within_100_nm {
        failures.push(format!(
            "mass within 100 NM {:.6} is below {:.6}",
            mass_within_100_nm, thresholds.minimum_mass_within_100_nm
        ));
    }
    if final_ess < thresholds.minimum_final_ess {
        failures.push(format!(
            "final ESS {:.3} is below {:.3}",
            final_ess, thresholds.minimum_final_ess
        ));
    }
    if !filter.log_evidence.is_finite() {
        failures.push("log evidence is not finite".to_string());
    }

    let passed = failures.is_empty();
    Ok(SyntheticSummary {
        status: if passed {
            "complete_passed"
        } else {
            "complete_failed"
        }
        .to_string(),
        passed,
        failures,
        particles: filter.particles.len(),
        observations: dataset.observations.len(),
        final_truth,
        posterior_mean,
        final_mean_error_nm,
        posterior_latitude_95_deg: [
            weighted_quantile(latitude_values.clone(), 0.025),
            weighted_quantile(latitude_values, 0.975),
        ],
        mass_within_50_nm: mass_within(50.0),
        mass_within_100_nm,
        final_ess,
        log_evidence: filter.log_evidence,
        ancestor_resampling_count: filter
            .checkpoints
            .iter()
            .filter(|checkpoint| checkpoint.ancestor_resampled)
            .count(),
        posterior_resampling_count: filter
            .checkpoints
            .iter()
            .filter(|checkpoint| checkpoint.posterior_resampled)
            .count(),
    })
}
