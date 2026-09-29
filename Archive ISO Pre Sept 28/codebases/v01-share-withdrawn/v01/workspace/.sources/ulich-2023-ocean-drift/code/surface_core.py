"""Pure numerical helpers for two-dimensional ocean-drift likelihood surfaces."""

from __future__ import annotations

import numpy as np


def weighted_log_probability(probability: np.ndarray, weight: np.ndarray) -> np.ndarray:
    """Return ``weight * log(probability)`` with exact zero handling."""
    probability = np.asarray(probability, dtype=float)
    weight = np.asarray(weight, dtype=float)
    probability, weight = np.broadcast_arrays(probability, weight)
    if not np.isfinite(probability).all() or np.any(
        (probability < 0.0) | (probability > 1.0)
    ):
        raise ValueError("Probabilities must be finite and lie in [0, 1]")
    if not np.isfinite(weight).all() or np.any(weight < 0.0):
        raise ValueError("Generalized-likelihood weights must be finite and nonnegative")
    output = np.zeros(probability.shape, dtype=float)
    positive_weight = weight > 0.0
    positive_probability = probability > 0.0
    impossible = positive_weight & ~positive_probability
    output[impossible] = -np.inf
    valid = positive_weight & positive_probability
    output[valid] = weight[valid] * np.log(probability[valid])
    return output


def combine_log_likelihood_with_conditional_mark(
    log_base_likelihood: np.ndarray,
    log_conditional_mark_density: np.ndarray,
) -> np.ndarray:
    """Multiply a base likelihood by a conditional mark in log space.

    A conditional density is unidentified when the conditioning event has
    exactly zero likelihood. In that case an undefined mark (NaN or -inf)
    cannot turn the exact-zero joint likelihood into NaN: the joint remains
    exactly zero (-inf in log space). On finite base support, however, every
    conditional mark must be finite; missing support is an explicit error and
    is never replaced by a pseudocount or an arbitrary density.
    """
    base = np.asarray(log_base_likelihood, dtype=float)
    mark = np.asarray(log_conditional_mark_density, dtype=float)
    if base.shape != mark.shape:
        raise ValueError("Base likelihood and conditional mark must have equal shape")
    if np.any(np.isnan(base)) or np.any(np.isposinf(base)):
        raise ValueError("Base log likelihood contains NaN or positive infinity")
    if np.any(np.isposinf(mark)):
        raise ValueError("Conditional log mark contains positive infinity")
    positive_support = np.isfinite(base)
    unsupported = positive_support & ~np.isfinite(mark)
    if np.any(unsupported):
        raise ValueError(
            "Conditional mark is undefined on "
            f"{int(np.count_nonzero(unsupported))} positive-base cells"
        )
    output = np.full(base.shape, -np.inf, dtype=float)
    output[positive_support] = base[positive_support] + mark[positive_support]
    return output


def logsumexp(values: np.ndarray, axis: int | tuple[int, ...] | None = None) -> np.ndarray:
    """Numerically stable log-sum-exp that preserves all-negative-infinity slices."""
    values = np.asarray(values, dtype=float)
    maximum = np.max(values, axis=axis, keepdims=True)
    finite = np.isfinite(maximum)
    with np.errstate(invalid="ignore", divide="ignore"):
        shifted = np.where(finite, values - maximum, -np.inf)
        summed = np.sum(np.exp(shifted), axis=axis, keepdims=True)
        result = np.where(finite, maximum + np.log(summed), -np.inf)
    if axis is None:
        return np.asarray(result.squeeze())
    return np.squeeze(result, axis=axis)


def bayesian_model_average_log_likelihood(
    log_likelihood_by_family: np.ndarray,
    prior_probability: np.ndarray,
) -> np.ndarray:
    """Average common-scale raw family likelihoods before normalization."""
    likelihood = np.asarray(log_likelihood_by_family, dtype=float)
    prior = np.asarray(prior_probability, dtype=float)
    if likelihood.ndim < 1 or prior.ndim != 1:
        raise ValueError("Family likelihoods and prior must have a family axis")
    if likelihood.shape[0] != len(prior):
        raise ValueError("Family likelihood and prior counts must match")
    if np.any(prior <= 0.0) or not np.isclose(prior.sum(), 1.0):
        raise ValueError("Family priors must be positive and sum to one")
    prior_shape = (len(prior),) + (1,) * (likelihood.ndim - 1)
    return logsumexp(
        likelihood + np.log(prior).reshape(prior_shape), axis=0
    )


def trapezoid_widths(coordinates: np.ndarray) -> np.ndarray:
    """Quadrature widths on an ordered one-dimensional coordinate grid."""
    coordinates = np.asarray(coordinates, dtype=float)
    if coordinates.ndim != 1 or len(coordinates) < 2:
        raise ValueError("At least two one-dimensional coordinates are required")
    delta = np.diff(coordinates)
    if np.any(delta <= 0.0):
        raise ValueError("Coordinates must be strictly increasing")
    widths = np.empty_like(coordinates)
    widths[0] = 0.5 * delta[0]
    widths[-1] = 0.5 * delta[-1]
    widths[1:-1] = 0.5 * (delta[:-1] + delta[1:])
    return widths


def normalize_log_surface(
    log_likelihood: np.ndarray, area_weights: np.ndarray
) -> tuple[np.ndarray, float]:
    """Normalize a likelihood under explicit positive quadrature weights.

    Returns cell probability mass and the log evidence relative to the
    uniform-area density on the supplied domain.
    """
    log_likelihood = np.asarray(log_likelihood, dtype=float)
    area_weights = np.asarray(area_weights, dtype=float)
    if log_likelihood.shape != area_weights.shape:
        raise ValueError("Likelihood and area weights must have equal shape")
    if np.any(~np.isfinite(area_weights)) or np.any(area_weights <= 0.0):
        raise ValueError("Area weights must be finite and positive")
    log_weighted = log_likelihood + np.log(area_weights)
    normalizer = float(logsumexp(log_weighted))
    if not np.isfinite(normalizer):
        raise ValueError("Likelihood surface has no finite support")
    mass = np.exp(log_weighted - normalizer)
    log_evidence = normalizer - np.log(np.sum(area_weights))
    return mass, float(log_evidence)


def posterior_family_probabilities(
    log_evidence: np.ndarray, prior_probability: np.ndarray
) -> np.ndarray:
    """Bayes-update current-family probabilities on a common likelihood scale."""
    log_evidence = np.asarray(log_evidence, dtype=float)
    prior_probability = np.asarray(prior_probability, dtype=float)
    if log_evidence.shape != prior_probability.shape:
        raise ValueError("Evidence and prior vectors must have equal shape")
    if np.any(prior_probability <= 0.0) or not np.isclose(prior_probability.sum(), 1.0):
        raise ValueError("Family priors must be positive and sum to one")
    log_joint = log_evidence + np.log(prior_probability)
    return np.exp(log_joint - logsumexp(log_joint))


def total_variation(left: np.ndarray, right: np.ndarray) -> float:
    left = np.asarray(left, dtype=float)
    right = np.asarray(right, dtype=float)
    if left.shape != right.shape:
        raise ValueError("Distributions must have equal shape")
    return float(0.5 * np.sum(np.abs(left - right)))


def hellinger_distance(left: np.ndarray, right: np.ndarray) -> float:
    left = np.asarray(left, dtype=float)
    right = np.asarray(right, dtype=float)
    if left.shape != right.shape:
        raise ValueError("Distributions must have equal shape")
    return float(np.sqrt(0.5 * np.sum(np.square(np.sqrt(left) - np.sqrt(right)))))


def mode_index(probability: np.ndarray) -> tuple[int, int]:
    probability = np.asarray(probability, dtype=float)
    if probability.ndim != 2:
        raise ValueError("A two-dimensional surface is required")
    return tuple(int(value) for value in np.unravel_index(np.argmax(probability), probability.shape))

