use std::{fs, path::Path};

use anyhow::{bail, Context, Result};
use mh370_domain::{great_circle_distance_nm, LatLon};
use mh370_ocean_drift::SourceAreaResult;
use mh370_reporting::ReportPoint;
use serde::Serialize;

#[derive(Debug, Clone, Serialize)]
pub(crate) struct DriftApplicationSummary {
    pub family: String,
    pub isotope_enabled: bool,
    pub applied_to_posterior: bool,
    pub particles: usize,
    pub before_effective_sample_size: f64,
    pub after_effective_sample_size: f64,
    pub zero_likelihood_particles: usize,
    pub maximum_cell_distance_nm: f64,
}

/// Apply the generated debris likelihood to an already normalized flight
/// posterior. The source-cell prior is removed before composition, so the
/// seventh-arc flight prior is not counted twice.
pub(crate) fn apply_source_area(
    path: &Path,
    expected_family: &str,
    expected_isotope_enabled: bool,
    maximum_cell_distance_nm: f64,
    points: &mut [ReportPoint],
) -> Result<DriftApplicationSummary> {
    if points.is_empty() || !maximum_cell_distance_nm.is_finite() || maximum_cell_distance_nm <= 0.0
    {
        bail!("invalid source-area application request");
    }
    let bytes = fs::read(path)
        .with_context(|| format!("cannot read source-area result {}", path.display()))?;
    let result: SourceAreaResult = serde_json::from_slice(&bytes)
        .with_context(|| format!("cannot parse source-area result {}", path.display()))?;
    if result.family != expected_family
        || result.isotope_enabled != expected_isotope_enabled
        || result.cells.is_empty()
    {
        bail!("source-area evidence selection does not match requested family/isotope condition");
    }
    if points
        .iter()
        .any(|point| !point.weight.is_finite() || point.weight < 0.0)
    {
        bail!("flight posterior has invalid weights");
    }
    let before_effective_sample_size =
        effective_sample_size(&points.iter().map(|point| point.weight).collect::<Vec<_>>());
    let mut log_weights = Vec::with_capacity(points.len());
    let mut zero_likelihood_particles = 0;
    for point in points.iter() {
        let position = LatLon::new(point.latitude_deg, point.longitude_deg)
            .context("flight posterior has invalid position")?;
        let (cell, distance_nm) = result
            .cells
            .iter()
            .map(|cell| (cell, great_circle_distance_nm(position, cell.position).0))
            .min_by(|first, second| first.1.total_cmp(&second.1))
            .context("source-area result is empty")?;
        if distance_nm > maximum_cell_distance_nm {
            bail!(
                "flight posterior lies outside source-area native support by {:.1} nm (limit {:.1} nm)",
                distance_nm,
                maximum_cell_distance_nm
            );
        }
        let evidence_log_likelihood = cell
            .combined_log_weight
            .map(|weight| weight - cell.prior_weight.ln());
        match (point.weight, evidence_log_likelihood) {
            (weight, Some(log_likelihood)) if weight > 0.0 => {
                log_weights.push(weight.ln() + log_likelihood);
            }
            _ => {
                zero_likelihood_particles += 1;
                log_weights.push(f64::NEG_INFINITY);
            }
        }
    }
    let maximum = log_weights
        .iter()
        .copied()
        .filter(|value| value.is_finite())
        .fold(f64::NEG_INFINITY, f64::max);
    if !maximum.is_finite() {
        bail!("source-area evidence gives zero support to every flight particle");
    }
    let total = log_weights
        .iter()
        .filter(|value| value.is_finite())
        .map(|value| (value - maximum).exp())
        .sum::<f64>();
    for (point, log_weight) in points.iter_mut().zip(log_weights) {
        point.weight = if log_weight.is_finite() {
            (log_weight - maximum).exp() / total
        } else {
            0.0
        };
    }
    let after_effective_sample_size =
        effective_sample_size(&points.iter().map(|point| point.weight).collect::<Vec<_>>());
    Ok(DriftApplicationSummary {
        family: result.family,
        isotope_enabled: result.isotope_enabled,
        applied_to_posterior: true,
        particles: points.len(),
        before_effective_sample_size,
        after_effective_sample_size,
        zero_likelihood_particles,
        maximum_cell_distance_nm,
    })
}

fn effective_sample_size(weights: &[f64]) -> f64 {
    let sum = weights.iter().sum::<f64>();
    let squares = weights.iter().map(|weight| weight * weight).sum::<f64>();
    if squares > 0.0 {
        sum * sum / squares
    } else {
        0.0
    }
}

#[cfg(test)]
mod tests {
    use std::fs;

    use super::{apply_source_area, effective_sample_size};
    use mh370_reporting::ReportPoint;
    use serde_json::json;

    #[test]
    fn effective_sample_size_has_expected_limits() {
        assert_eq!(effective_sample_size(&[0.5, 0.5]), 2.0);
        assert_eq!(effective_sample_size(&[1.0, 0.0]), 1.0);
    }

    #[test]
    fn application_removes_source_prior_and_rejects_family_mismatch() {
        let path = std::env::temp_dir().join(format!(
            "mh370-drift-application-{}.json",
            std::process::id()
        ));
        let first_prior = 0.25_f64;
        let second_prior = 0.75_f64;
        let payload = json!({
            "family": "hycom",
            "seed": 1,
            "particles_per_cell": 2,
            "isotope_enabled": true,
            "motion_family_ids": ["fixture-motion"],
            "cells": [
                {
                    "id": "first",
                    "position": {"latitude": -30.0, "longitude": 95.0},
                    "prior_weight": first_prior,
                    "debris_log_compatibility": 2.0_f64.ln(),
                    "conditional_isotope_log_likelihood": 0.0,
                    "combined_log_weight": first_prior.ln() + 2.0_f64.ln(),
                    "normalized_weight": 0.4,
                    "terminated_fraction": 0.0,
                    "proposal_terminated_fraction": 0.0,
                    "termination_reasons": {},
                    "termination_reason_fractions": {},
                    "status": "supported",
                    "recoveries": [],
                    "isotope": null
                },
                {
                    "id": "second",
                    "position": {"latitude": -31.0, "longitude": 95.0},
                    "prior_weight": second_prior,
                    "debris_log_compatibility": 0.0,
                    "conditional_isotope_log_likelihood": 0.0,
                    "combined_log_weight": second_prior.ln(),
                    "normalized_weight": 0.6,
                    "terminated_fraction": 0.0,
                    "proposal_terminated_fraction": 0.0,
                    "termination_reasons": {},
                    "termination_reason_fractions": {},
                    "status": "supported",
                    "recoveries": [],
                    "isotope": null
                }
            ],
            "peak_cell_id": "second",
            "peak_position": {"latitude": -31.0, "longitude": 95.0},
            "mean_terminated_fraction": 0.0,
            "mean_proposal_terminated_fraction": 0.0
        });
        fs::write(&path, serde_json::to_vec(&payload).unwrap()).unwrap();
        let points = || {
            vec![
                ReportPoint {
                    latitude_deg: -30.0,
                    longitude_deg: 95.0,
                    weight: 0.5,
                },
                ReportPoint {
                    latitude_deg: -31.0,
                    longitude_deg: 95.0,
                    weight: 0.5,
                },
            ]
        };
        let mut mismatched = points();
        assert!(apply_source_area(&path, "gdp", true, 10.0, &mut mismatched).is_err());
        let mut isotope_mismatched = points();
        assert!(apply_source_area(&path, "hycom", false, 10.0, &mut isotope_mismatched).is_err());
        let mut applied = points();
        let summary = apply_source_area(&path, "hycom", true, 10.0, &mut applied).unwrap();
        assert!(summary.applied_to_posterior);
        assert!((applied[0].weight - 2.0 / 3.0).abs() < 1e-12);
        assert!((applied[1].weight - 1.0 / 3.0).abs() < 1e-12);
        assert!((applied.iter().map(|point| point.weight).sum::<f64>() - 1.0).abs() < 1e-12);
        let _ = fs::remove_file(path);
    }
}
