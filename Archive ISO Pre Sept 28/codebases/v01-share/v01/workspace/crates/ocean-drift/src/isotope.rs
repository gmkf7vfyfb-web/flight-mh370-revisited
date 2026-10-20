use std::collections::HashSet;

use mh370_domain::LatLon;
use serde::{Deserialize, Serialize};
use thiserror::Error;

use crate::{DriftPath, GriddedField};

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct BarnacleRecord {
    pub sample_id: String,
    /// Shell calcite value on the VPDB scale. The canonical input contains
    /// exactly the 49 nonblank A2-G1 target samples.
    pub delta18o_calcite_per_mil: f64,
    /// Fractional position in the central chronology. Alternative growth
    /// chronologies stretch this same ordered shell record in time.
    pub growth_fraction: f64,
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct BarnacleChronology {
    pub name: String,
    pub start_unix_seconds: f64,
    /// The terminal shell value is anchored to 2015-07-29 in every chronology.
    pub end_unix_seconds: f64,
    /// Retained as provenance for chronology sensitivity. Compatibility is an
    /// envelope over alternatives, not a density-weighted chronology mixture.
    pub prior_weight: f64,
}

/// Conservative A2-G1 compatibility-screen sensitivities.
///
/// All uncertainty scales are predictive discrepancies. They are not fitted
/// from the 49 reconstructed-temperature rows in this crate.
#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct BarnacleIsotopeModel {
    pub records: Vec<BarnacleRecord>,
    pub chronologies: Vec<BarnacleChronology>,
    pub seawater_delta18o_per_mil: f64,
    /// Shared seawater-isotope (or salinity-proxy) uncertainty. Equation 2
    /// converts this to temperature with a factor of 4.63 degrees C per mil.
    pub seawater_delta18o_sd_per_mil: f64,
    /// Shared uncertainty in the isotope-temperature calibration, degrees C.
    pub calibration_sd_c: f64,
    /// Residual shell/path discrepancy, degrees C, with OU correlation below.
    pub residual_sd_c: f64,
    /// SST analysis uncertainty at a shell comparison, degrees C.
    pub sst_field_sd_c: f64,
    /// Width of the shell temporal averaging window. Windows are clipped to
    /// each chronology so the endpoint anchor remains inside the record.
    pub shell_smoothing_days: f64,
    /// OU correlation scale for residual shell/path discrepancy.
    pub correlation_days: f64,
    /// A path is neutral when any chronology lies within this simultaneous
    /// predictive envelope.
    pub compatible_simultaneous_confidence: f64,
    /// Strong suppression is allowed only when every chronology lies outside
    /// this wider simultaneous predictive envelope.
    pub rejection_simultaneous_confidence: f64,
    /// Largest magnitude of the log penalty for a marginal path.
    pub maximum_marginal_log_penalty: f64,
    /// Largest magnitude of the log penalty for a rejected path.
    pub maximum_rejection_log_penalty: f64,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum IsotopeClassification {
    Compatible,
    Marginal,
    Rejected,
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct IsotopeEvaluation {
    /// Never positive: compatible paths are neutral and other paths can only
    /// reduce compatibility conditional on represented flaperon arrival.
    pub conditional_log_compatibility: f64,
    pub record_count: usize,
    pub usable_arrival_weight_fraction: f64,
    pub arrival_effective_sample_size: f64,
    pub screened_arrival_effective_sample_size: f64,
    pub usable_paths: usize,
    pub compatible_paths: usize,
    pub marginal_paths: usize,
    pub rejected_paths: usize,
    pub missing_coverage_paths: usize,
    pub compatible_arrival_weight_fraction: f64,
    pub marginal_arrival_weight_fraction: f64,
    pub rejected_arrival_weight_fraction: f64,
    pub missing_coverage_arrival_weight_fraction: f64,
    pub compatible_simultaneous_confidence: f64,
    pub rejection_simultaneous_confidence: f64,
    pub maximum_marginal_log_penalty: f64,
    pub maximum_rejection_log_penalty: f64,
    pub chronology_names: Vec<String>,
}

#[derive(Debug, Error, Clone, PartialEq)]
pub enum IsotopeError {
    #[error("barnacle isotope configuration is invalid")]
    InvalidConfiguration,
    #[error("path and flaperon-arrival weights have different lengths")]
    LengthMismatch,
    #[error("no flaperon-arrival probability is represented")]
    NoArrivalSupport,
}

#[derive(Debug, Clone, Copy)]
struct ChronologyScreen {
    maximum_standardized_residual: f64,
    compatible_threshold: f64,
    rejection_threshold: f64,
}

#[derive(Debug, Clone, Copy)]
struct PathScreen {
    classification: IsotopeClassification,
    log_penalty: f64,
}

impl BarnacleIsotopeModel {
    pub fn validate(&self) -> Result<(), IsotopeError> {
        if self.records.len() < 2
            || self.chronologies.is_empty()
            || !self.seawater_delta18o_per_mil.is_finite()
            || !nonnegative(self.seawater_delta18o_sd_per_mil)
            || !nonnegative(self.calibration_sd_c)
            || !positive(self.residual_sd_c)
            || !nonnegative(self.sst_field_sd_c)
            || !positive(self.shell_smoothing_days)
            || !positive(self.correlation_days)
            || !probability(self.compatible_simultaneous_confidence)
            || !probability(self.rejection_simultaneous_confidence)
            || self.rejection_simultaneous_confidence <= self.compatible_simultaneous_confidence
            || !nonnegative(self.maximum_marginal_log_penalty)
            || !nonnegative(self.maximum_rejection_log_penalty)
            || self.maximum_rejection_log_penalty < self.maximum_marginal_log_penalty
        {
            return Err(IsotopeError::InvalidConfiguration);
        }
        let unique_records = self
            .records
            .iter()
            .map(|record| record.sample_id.as_str())
            .collect::<HashSet<_>>();
        if unique_records.len() != self.records.len()
            || self.records.iter().any(|record| {
                record.sample_id.trim().is_empty()
                    || !record.delta18o_calcite_per_mil.is_finite()
                    || !record.growth_fraction.is_finite()
                    || !(0.0..=1.0).contains(&record.growth_fraction)
            })
            || self
                .records
                .windows(2)
                .any(|pair| pair[1].growth_fraction <= pair[0].growth_fraction)
        {
            return Err(IsotopeError::InvalidConfiguration);
        }
        let unique_chronologies = self
            .chronologies
            .iter()
            .map(|chronology| chronology.name.as_str())
            .collect::<HashSet<_>>();
        if unique_chronologies.len() != self.chronologies.len()
            || self.chronologies.iter().any(|chronology| {
                chronology.name.trim().is_empty()
                    || !chronology.start_unix_seconds.is_finite()
                    || !chronology.end_unix_seconds.is_finite()
                    || chronology.end_unix_seconds <= chronology.start_unix_seconds
                    || !chronology.prior_weight.is_finite()
                    || chronology.prior_weight < 0.0
            })
        {
            return Err(IsotopeError::InvalidConfiguration);
        }
        Ok(())
    }

    /// Al-Qattan et al. (2023), equation 2.
    pub fn reconstructed_temperature_c(&self, delta18o_calcite_per_mil: f64) -> f64 {
        19.0 - 4.63 * (delta18o_calcite_per_mil - (self.seawater_delta18o_per_mil - 0.27))
    }

    /// Screen isotope compatibility conditional on represented flaperon arrival.
    ///
    /// A compatible chronology returns a factor of one, never a positive
    /// density boost. Missing SST histories are also neutral and are reported,
    /// preventing silent survivor conditioning. The 49 correlated rows enter a
    /// simultaneous covariance envelope rather than a product of 49 densities.
    pub fn evaluate_conditional(
        &self,
        paths: &[DriftPath],
        arrival_weights: &[f64],
        sst: &GriddedField,
    ) -> Result<IsotopeEvaluation, IsotopeError> {
        self.validate()?;
        if paths.len() != arrival_weights.len() {
            return Err(IsotopeError::LengthMismatch);
        }
        let arrival_sum = arrival_weights.iter().sum::<f64>();
        if !arrival_sum.is_finite() || arrival_sum <= 0.0 {
            return Err(IsotopeError::NoArrivalSupport);
        }

        let mut compatible_paths = 0;
        let mut marginal_paths = 0;
        let mut rejected_paths = 0;
        let mut missing_coverage_paths = 0;
        let mut compatible_weight = 0.0;
        let mut marginal_weight = 0.0;
        let mut rejected_weight = 0.0;
        let mut missing_weight = 0.0;
        let mut screened_weights = Vec::with_capacity(paths.len());

        for (path, arrival) in paths.iter().zip(arrival_weights) {
            if !arrival.is_finite() || *arrival <= 0.0 {
                screened_weights.push(0.0);
                continue;
            }
            match self.screen_path(path, sst) {
                Some(screen) => {
                    let factor = screen.log_penalty.exp();
                    screened_weights.push(arrival * factor);
                    match screen.classification {
                        IsotopeClassification::Compatible => {
                            compatible_paths += 1;
                            compatible_weight += arrival;
                        }
                        IsotopeClassification::Marginal => {
                            marginal_paths += 1;
                            marginal_weight += arrival;
                        }
                        IsotopeClassification::Rejected => {
                            rejected_paths += 1;
                            rejected_weight += arrival;
                        }
                    }
                }
                None => {
                    // Absence of an SST history is not evidence against the
                    // path. It remains neutral and is made visible in output.
                    missing_coverage_paths += 1;
                    missing_weight += arrival;
                    screened_weights.push(*arrival);
                }
            }
        }
        let screened_sum = screened_weights.iter().sum::<f64>();
        let usable_weight = compatible_weight + marginal_weight + rejected_weight;
        Ok(IsotopeEvaluation {
            conditional_log_compatibility: (screened_sum / arrival_sum).min(1.0).ln(),
            record_count: self.records.len(),
            usable_arrival_weight_fraction: usable_weight / arrival_sum,
            arrival_effective_sample_size: effective_sample_size(arrival_weights),
            screened_arrival_effective_sample_size: effective_sample_size(&screened_weights),
            usable_paths: compatible_paths + marginal_paths + rejected_paths,
            compatible_paths,
            marginal_paths,
            rejected_paths,
            missing_coverage_paths,
            compatible_arrival_weight_fraction: compatible_weight / arrival_sum,
            marginal_arrival_weight_fraction: marginal_weight / arrival_sum,
            rejected_arrival_weight_fraction: rejected_weight / arrival_sum,
            missing_coverage_arrival_weight_fraction: missing_weight / arrival_sum,
            compatible_simultaneous_confidence: self.compatible_simultaneous_confidence,
            rejection_simultaneous_confidence: self.rejection_simultaneous_confidence,
            maximum_marginal_log_penalty: self.maximum_marginal_log_penalty,
            maximum_rejection_log_penalty: self.maximum_rejection_log_penalty,
            chronology_names: self
                .chronologies
                .iter()
                .map(|chronology| chronology.name.clone())
                .collect(),
        })
    }

    fn screen_path(&self, path: &DriftPath, sst: &GriddedField) -> Option<PathScreen> {
        let mut screens = Vec::with_capacity(self.chronologies.len());
        for chronology in &self.chronologies {
            // Strong suppression requires all plausible chronologies to be
            // outside the rejection envelope. If even one chronology lacks a
            // complete path/SST history, that proposition is untestable and
            // the conservative screen is neutral for this trajectory.
            screens.push(self.screen_chronology(path, chronology, sst)?);
        }
        if screens
            .iter()
            .any(|screen| screen.maximum_standardized_residual <= screen.compatible_threshold)
        {
            return Some(PathScreen {
                classification: IsotopeClassification::Compatible,
                log_penalty: 0.0,
            });
        }
        if let Some(best) = screens
            .iter()
            .filter(|screen| screen.maximum_standardized_residual <= screen.rejection_threshold)
            .min_by(|a, b| {
                a.maximum_standardized_residual
                    .total_cmp(&b.maximum_standardized_residual)
            })
        {
            let span = (best.rejection_threshold - best.compatible_threshold).max(1e-12);
            let severity = ((best.maximum_standardized_residual - best.compatible_threshold)
                / span)
                .clamp(0.0, 1.0);
            return Some(PathScreen {
                classification: IsotopeClassification::Marginal,
                log_penalty: -self.maximum_marginal_log_penalty * severity,
            });
        }
        Some(PathScreen {
            classification: IsotopeClassification::Rejected,
            log_penalty: -self.maximum_rejection_log_penalty,
        })
    }

    fn screen_chronology(
        &self,
        path: &DriftPath,
        chronology: &BarnacleChronology,
        sst: &GriddedField,
    ) -> Option<ChronologyScreen> {
        let mut times = Vec::with_capacity(self.records.len());
        let mut residuals = Vec::with_capacity(self.records.len());
        let mut windows = Vec::with_capacity(self.records.len());
        for record in &self.records {
            let time = chronology.start_unix_seconds
                + record.growth_fraction
                    * (chronology.end_unix_seconds - chronology.start_unix_seconds);
            let half_window = 0.5 * self.shell_smoothing_days * 86_400.0;
            let window_start = (time - half_window).max(chronology.start_unix_seconds);
            let window_end = (time + half_window).min(chronology.end_unix_seconds);
            let modeled = smoothed_sst(path, sst, window_start, window_end)?;
            times.push(time);
            windows.push((window_start, window_end));
            residuals
                .push(modeled - self.reconstructed_temperature_c(record.delta18o_calcite_per_mil));
        }

        let covariance = self.predictive_covariance(&times, &windows);
        let factor = cholesky(&covariance)?;
        let standardized = forward_solve(&factor, &residuals)?;
        let maximum_standardized_residual = standardized
            .iter()
            .map(|value| value.abs())
            .fold(0.0, f64::max);
        let effective_records = covariance_effective_rank(&covariance).max(1.0);
        Some(ChronologyScreen {
            maximum_standardized_residual,
            compatible_threshold: simultaneous_normal_threshold(
                self.compatible_simultaneous_confidence,
                effective_records,
            ),
            rejection_threshold: simultaneous_normal_threshold(
                self.rejection_simultaneous_confidence,
                effective_records,
            ),
        })
    }

    fn predictive_covariance(&self, times: &[f64], windows: &[(f64, f64)]) -> Vec<Vec<f64>> {
        let count = times.len();
        let common_variance =
            self.calibration_sd_c.powi(2) + (4.63 * self.seawater_delta18o_sd_per_mil).powi(2);
        let residual_variance = self.residual_sd_c.powi(2);
        let sst_variance = self.sst_field_sd_c.powi(2);
        let mut covariance = vec![vec![0.0; count]; count];
        for row in 0..count {
            for column in 0..count {
                let elapsed_days = (times[row] - times[column]).abs() / 86_400.0;
                let residual_covariance =
                    residual_variance * (-elapsed_days / self.correlation_days).exp();
                let overlap = interval_overlap_fraction(windows[row], windows[column]);
                covariance[row][column] =
                    common_variance + residual_covariance + sst_variance * overlap;
            }
            covariance[row][row] += 1e-10;
        }
        covariance
    }
}

fn smoothed_sst(path: &DriftPath, sst: &GriddedField, start: f64, end: f64) -> Option<f64> {
    if end < start {
        return None;
    }
    let duration_days = (end - start) / 86_400.0;
    let intervals = duration_days.ceil().max(1.0) as usize;
    let mut total = 0.0;
    for index in 0..=intervals {
        let fraction = index as f64 / intervals as f64;
        let time = start + fraction * (end - start);
        let position = path_position(path, time)?;
        total += sst.interpolate("sst", time, position).ok()?;
    }
    Some(total / (intervals + 1) as f64)
}

fn path_position(path: &DriftPath, time: f64) -> Option<LatLon> {
    if time < path.points.first()?.unix_seconds || time > path.points.last()?.unix_seconds {
        return None;
    }
    match path
        .points
        .binary_search_by(|point| point.unix_seconds.total_cmp(&time))
    {
        Ok(index) => Some(path.points[index].position),
        Err(upper) => {
            let lower = upper.checked_sub(1)?;
            let first = path.points[lower];
            let second = path.points[upper];
            let fraction = (time - first.unix_seconds) / (second.unix_seconds - first.unix_seconds);
            LatLon::new(
                first.position.latitude.0
                    + fraction * (second.position.latitude.0 - first.position.latitude.0),
                first.position.longitude.0
                    + fraction * (second.position.longitude.0 - first.position.longitude.0),
            )
            .ok()
        }
    }
}

fn interval_overlap_fraction(first: (f64, f64), second: (f64, f64)) -> f64 {
    let overlap = (first.1.min(second.1) - first.0.max(second.0)).max(0.0);
    let first_width = (first.1 - first.0).max(1.0);
    let second_width = (second.1 - second.0).max(1.0);
    overlap / (first_width * second_width).sqrt()
}

fn cholesky(matrix: &[Vec<f64>]) -> Option<Vec<Vec<f64>>> {
    let count = matrix.len();
    let mut lower = vec![vec![0.0; count]; count];
    for row in 0..count {
        for column in 0..=row {
            let prior = (0..column)
                .map(|index| lower[row][index] * lower[column][index])
                .sum::<f64>();
            if row == column {
                let diagonal = matrix[row][row] - prior;
                if !diagonal.is_finite() || diagonal <= 0.0 {
                    return None;
                }
                lower[row][column] = diagonal.sqrt();
            } else {
                lower[row][column] = (matrix[row][column] - prior) / lower[column][column];
            }
        }
    }
    Some(lower)
}

fn forward_solve(lower: &[Vec<f64>], values: &[f64]) -> Option<Vec<f64>> {
    let mut result = vec![0.0; values.len()];
    for row in 0..values.len() {
        let prior = (0..row)
            .map(|column| lower[row][column] * result[column])
            .sum::<f64>();
        result[row] = (values[row] - prior) / lower[row][row];
        if !result[row].is_finite() {
            return None;
        }
    }
    Some(result)
}

fn covariance_effective_rank(covariance: &[Vec<f64>]) -> f64 {
    let count = covariance.len();
    let variances = (0..count)
        .map(|index| covariance[index][index])
        .collect::<Vec<_>>();
    let squared_correlation_sum = (0..count)
        .flat_map(|row| (0..count).map(move |column| (row, column)))
        .map(|(row, column)| {
            let denominator = (variances[row] * variances[column]).sqrt();
            (covariance[row][column] / denominator).powi(2)
        })
        .sum::<f64>();
    (count * count) as f64 / squared_correlation_sum.max(count as f64)
}

fn simultaneous_normal_threshold(confidence: f64, effective_records: f64) -> f64 {
    let individual_coverage = confidence.powf(1.0 / effective_records);
    normal_quantile(0.5 * (1.0 + individual_coverage))
}

fn normal_quantile(probability: f64) -> f64 {
    let mut lower = -10.0;
    let mut upper = 10.0;
    for _ in 0..80 {
        let middle = 0.5 * (lower + upper);
        if normal_cdf(middle) < probability {
            lower = middle;
        } else {
            upper = middle;
        }
    }
    0.5 * (lower + upper)
}

// Abramowitz and Stegun 7.1.26; sufficient for sensitivity thresholds.
fn normal_cdf(value: f64) -> f64 {
    let absolute = value.abs();
    let t = 1.0 / (1.0 + 0.231_641_9 * absolute);
    let polynomial = t
        * (0.319_381_530
            + t * (-0.356_563_782
                + t * (1.781_477_937 + t * (-1.821_255_978 + t * 1.330_274_429))));
    let density = (-0.5 * absolute * absolute).exp() / (2.0 * std::f64::consts::PI).sqrt();
    let upper_tail = density * polynomial;
    if value >= 0.0 {
        1.0 - upper_tail
    } else {
        upper_tail
    }
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

fn positive(value: f64) -> bool {
    value.is_finite() && value > 0.0
}

fn nonnegative(value: f64) -> bool {
    value.is_finite() && value >= 0.0
}

fn probability(value: f64) -> bool {
    value.is_finite() && value > 0.5 && value < 1.0
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn equation_two_reconstructs_published_endpoint_temperature() {
        let model = fixture_model(0.0);
        assert!((model.reconstructed_temperature_c(-0.89) - 23.7226).abs() < 1e-4);
    }

    #[test]
    fn simultaneous_threshold_increases_for_more_independent_records() {
        let one = simultaneous_normal_threshold(0.99, 1.0);
        let many = simultaneous_normal_threshold(0.99, 20.0);
        assert!(many > one);
        assert!((normal_cdf(one) - 0.995).abs() < 2e-5);
    }

    #[test]
    fn maximum_penalties_are_ordered_and_finite() {
        let model = fixture_model(0.0);
        assert!(model.validate().is_ok());
        assert!(model.maximum_rejection_log_penalty >= model.maximum_marginal_log_penalty);
    }

    fn fixture_model(delta: f64) -> BarnacleIsotopeModel {
        BarnacleIsotopeModel {
            records: vec![
                BarnacleRecord {
                    sample_id: "first".to_string(),
                    delta18o_calcite_per_mil: delta,
                    growth_fraction: 0.0,
                },
                BarnacleRecord {
                    sample_id: "last".to_string(),
                    delta18o_calcite_per_mil: delta,
                    growth_fraction: 1.0,
                },
            ],
            chronologies: vec![BarnacleChronology {
                name: "central".to_string(),
                start_unix_seconds: 0.0,
                end_unix_seconds: 86_400.0,
                prior_weight: 1.0,
            }],
            seawater_delta18o_per_mil: 0.4,
            seawater_delta18o_sd_per_mil: 0.2,
            calibration_sd_c: 1.0,
            residual_sd_c: 1.5,
            sst_field_sd_c: 0.5,
            shell_smoothing_days: 3.0,
            correlation_days: 7.0,
            compatible_simultaneous_confidence: 0.95,
            rejection_simultaneous_confidence: 0.995,
            maximum_marginal_log_penalty: 0.7,
            maximum_rejection_log_penalty: 4.0,
        }
    }
}
