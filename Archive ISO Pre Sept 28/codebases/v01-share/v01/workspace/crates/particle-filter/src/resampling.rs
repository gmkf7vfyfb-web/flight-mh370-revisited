use crate::SmcError;

#[derive(Debug, Clone, PartialEq, serde::Serialize, serde::Deserialize)]
pub struct ReweightedPopulation {
    pub normalized_log_weights: Vec<f64>,
    /// `log E_base[exp(log_density_ratio)]`; this is the incremental evidence
    /// estimate when the base weights represent the proposal population.
    pub log_normalizing_ratio: f64,
    pub effective_sample_size: f64,
    pub maximum_normalized_weight: f64,
}

fn valid_log_weight(value: f64) -> bool {
    value.is_finite() || value == f64::NEG_INFINITY
}

pub fn logsumexp(values: &[f64]) -> Result<f64, SmcError> {
    if values.is_empty() || values.iter().any(|value| !valid_log_weight(*value)) {
        return Err(SmcError::InvalidWeights);
    }
    let maximum = values.iter().copied().fold(f64::NEG_INFINITY, f64::max);
    if maximum == f64::NEG_INFINITY {
        return Err(SmcError::AllParticlesRejected);
    }
    let sum = values
        .iter()
        .map(|value| (*value - maximum).exp())
        .sum::<f64>();
    if !sum.is_finite() || sum <= 0.0 {
        return Err(SmcError::InvalidWeights);
    }
    Ok(maximum + sum.ln())
}

pub fn normalize_log_weights(values: &[f64]) -> Result<(Vec<f64>, f64), SmcError> {
    let normalizer = logsumexp(values)?;
    let normalized = values.iter().map(|value| value - normalizer).collect();
    Ok((normalized, normalizer))
}

pub fn effective_sample_size(log_weights: &[f64]) -> Result<f64, SmcError> {
    let (normalized, _) = normalize_log_weights(log_weights)?;
    let sum_squares = normalized
        .iter()
        .map(|value| (2.0 * value).exp())
        .sum::<f64>();
    if !sum_squares.is_finite() || sum_squares <= 0.0 {
        return Err(SmcError::InvalidWeights);
    }
    Ok(1.0 / sum_squares)
}

pub fn systematic_resample(
    normalized_weights: &[f64],
    first_offset: f64,
) -> Result<Vec<usize>, SmcError> {
    systematic_resample_n(normalized_weights, normalized_weights.len(), first_offset)
}

/// Systematically draw an explicitly sized sample from normalized weights.
/// This is used to preserve deliberate stratum allocations even when strata
/// contain different numbers of source and output particles.
pub fn systematic_resample_n(
    normalized_weights: &[f64],
    output_count: usize,
    first_offset: f64,
) -> Result<Vec<usize>, SmcError> {
    let source_count = normalized_weights.len();
    if source_count == 0
        || output_count == 0
        || normalized_weights
            .iter()
            .any(|weight| !weight.is_finite() || *weight < 0.0)
    {
        return Err(SmcError::InvalidWeights);
    }
    let total = normalized_weights.iter().sum::<f64>();
    if !total.is_finite() || total <= 0.0 {
        return Err(SmcError::InvalidWeights);
    }
    let step = 1.0 / output_count as f64;
    if !first_offset.is_finite() || first_offset < 0.0 || first_offset >= step {
        return Err(SmcError::InvalidResamplingOffset);
    }

    let mut result = Vec::with_capacity(output_count);
    let mut cumulative = normalized_weights[0] / total;
    let mut index = 0usize;
    for child in 0..output_count {
        let target = first_offset + child as f64 * step;
        while target > cumulative && index + 1 < source_count {
            index += 1;
            cumulative += normalized_weights[index] / total;
        }
        result.push(index);
    }
    Ok(result)
}

/// Aggregate descendant weights onto a checkpoint's ancestor slots.
///
/// The input weights may be normalized or unnormalized. The returned values
/// are logsumexp-normalized across all ancestor slots; ancestors without a
/// descendant receive negative infinity.
pub fn aggregate_log_weights_by_ancestor(
    ancestor_indices: &[usize],
    ancestor_count: usize,
    descendant_log_weights: &[f64],
) -> Result<Vec<f64>, SmcError> {
    if ancestor_count == 0 || ancestor_indices.len() != descendant_log_weights.len() {
        return Err(SmcError::InvalidAncestry);
    }
    let (normalized, _) = normalize_log_weights(descendant_log_weights)?;
    let mut totals = vec![0.0; ancestor_count];
    for (&ancestor, log_weight) in ancestor_indices.iter().zip(normalized) {
        if ancestor >= ancestor_count {
            return Err(SmcError::InvalidAncestry);
        }
        totals[ancestor] += log_weight.exp();
    }
    Ok(totals
        .into_iter()
        .map(|weight| {
            if weight > 0.0 {
                weight.ln()
            } else {
                f64::NEG_INFINITY
            }
        })
        .collect())
}

/// Apply an additive log-density ratio to an existing weighted population.
///
/// This permits evidence sensitivities to reuse an identical propagated
/// population when (and only when) the changed evidence did not alter latent
/// state evolution or analytic state updates. Callers must rerun when overlap,
/// as exposed by ESS/max weight, is inadequate.
pub fn reweight_population(
    base_log_weights: &[f64],
    log_density_ratio: &[f64],
) -> Result<ReweightedPopulation, SmcError> {
    if base_log_weights.len() != log_density_ratio.len() || base_log_weights.is_empty() {
        return Err(SmcError::InvalidWeights);
    }
    let (normalized_base, _) = normalize_log_weights(base_log_weights)?;
    let raw = normalized_base
        .iter()
        .zip(log_density_ratio)
        .map(|(weight, ratio)| {
            if ratio.is_finite() || *ratio == f64::NEG_INFINITY {
                Ok(weight + ratio)
            } else {
                Err(SmcError::InvalidWeights)
            }
        })
        .collect::<Result<Vec<_>, _>>()?;
    let (normalized_log_weights, log_normalizing_ratio) = normalize_log_weights(&raw)?;
    let effective_sample_size = effective_sample_size(&normalized_log_weights)?;
    let maximum_normalized_weight = normalized_log_weights
        .iter()
        .map(|value| value.exp())
        .fold(0.0, f64::max);
    Ok(ReweightedPopulation {
        normalized_log_weights,
        log_normalizing_ratio,
        effective_sample_size,
        maximum_normalized_weight,
    })
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn normalization_and_ess_are_stable_in_log_space() {
        let (weights, normalizer) = normalize_log_weights(&[-1_001.0, -1_002.0, -1_003.0]).unwrap();
        let linear_sum = weights.iter().map(|value| value.exp()).sum::<f64>();
        assert!((linear_sum - 1.0).abs() < 2e-13);
        assert!(normalizer.is_finite());
        let ess = effective_sample_size(&weights).unwrap();
        assert!(ess > 1.0 && ess < 3.0);
    }

    #[test]
    fn systematic_resampling_has_declared_boundary_behavior() {
        let indices = systematic_resample(&[0.1, 0.2, 0.7], 0.0).unwrap();
        assert_eq!(indices, vec![0, 2, 2]);
        assert!(systematic_resample(&[0.1, 0.2, 0.7], 1.0 / 3.0).is_err());
    }

    #[test]
    fn sized_resampling_and_ancestor_aggregation_are_exact() {
        let indices = systematic_resample_n(&[0.25, 0.75], 4, 0.0).unwrap();
        assert_eq!(indices, vec![0, 0, 1, 1]);

        let aggregated = aggregate_log_weights_by_ancestor(
            &[0, 0, 1, 2],
            3,
            &[0.1_f64.ln(), 0.2_f64.ln(), 0.3_f64.ln(), 0.4_f64.ln()],
        )
        .unwrap();
        let weights = aggregated
            .iter()
            .map(|value| value.exp())
            .collect::<Vec<_>>();
        assert!((weights[0] - 0.3).abs() < 1e-14);
        assert!((weights[1] - 0.3).abs() < 1e-14);
        assert!((weights[2] - 0.4).abs() < 1e-14);
    }

    #[test]
    fn post_hoc_density_ratio_reports_overlap() {
        let result =
            reweight_population(&[0.5_f64.ln(), 0.5_f64.ln()], &[2.0_f64.ln(), 0.0]).unwrap();
        let weights = result
            .normalized_log_weights
            .iter()
            .map(|value| value.exp())
            .collect::<Vec<_>>();
        assert!((weights[0] - 2.0 / 3.0).abs() < 1e-14);
        assert!((weights[1] - 1.0 / 3.0).abs() < 1e-14);
        assert!((result.log_normalizing_ratio - 1.5_f64.ln()).abs() < 1e-14);
        assert!((result.effective_sample_size - 1.8).abs() < 1e-14);
        assert!((result.maximum_normalized_weight - 2.0 / 3.0).abs() < 1e-14);
    }
}
