#!/usr/bin/env python3
"""Hierarchical, blocked prediction of AES gain precompensation.

The two endpoint hypotheses are:

* beta = 0: full gain precompensation; and
* beta = 1: no gain precompensation.

The response is the observed received power minus the workbook's 12 dBic
physical-link prediction.  Exact-channel offsets and a continuous-time OU
nuisance process are integrated as Gaussian random effects.  The primary
assessment predicts whole held-out time events after purging nearby events.
"""

from __future__ import annotations

import hashlib
import itertools
import json
import math
import platform
from dataclasses import asdict, dataclass
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.linalg import cho_factor, cho_solve
from scipy.optimize import minimize
from scipy.special import gammaln
from scipy.stats import t as student_t


BUNDLE = Path(__file__).resolve().parents[1]
ROOT = BUNDLE
INPUT = BUNDLE / "data" / "event_channel_means.csv"
OUTPUT = BUNDLE / "outputs"
INPUT_SHA256 = "0a9a326d24aac8468f4378c2dd6b39dd7d4a8d4e43f12eeafe6bd4bba1e93530"
SEED = 20260823

MODEL_LABELS = {
    0.0: "full_gain_precompensation",
    1.0: "no_gain_precompensation",
}


@dataclass(frozen=True)
class AnalysisConfig:
    name: str
    purge_minutes: float
    use_time_process: bool = True
    independent_event_process: bool = False
    likelihood: str = "gaussian"
    student_df: float = 4.0
    split: str = "leave_event_out"


@dataclass
class FitResult:
    coefficients: np.ndarray
    covariance_parameters: dict[str, float]
    nll: float
    converged: bool
    message: str
    covariance: np.ndarray
    design_information: np.ndarray
    quadratic: float


CONFIGS = (
    AnalysisConfig("gaussian_ou_purge30_primary", 30.0),
    AnalysisConfig(
        "gaussian_independent_event_purge30",
        30.0,
        independent_event_process=True,
    ),
    AnalysisConfig("gaussian_ou_purge0", 0.0),
    AnalysisConfig("gaussian_ou_purge15", 15.0),
    AnalysisConfig("gaussian_ou_purge60", 60.0),
    AnalysisConfig(
        "student_t4_ou_purge30",
        30.0,
        likelihood="student_t",
        student_df=4.0,
    ),
    AnalysisConfig(
        "gaussian_no_time_purge30",
        30.0,
        use_time_process=False,
    ),
    AnalysisConfig(
        "gaussian_ou_forward30",
        30.0,
        split="forward",
    ),
)
PRIMARY_CONFIG = CONFIGS[0].name


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_data() -> pd.DataFrame:
    if sha256(INPUT) != INPUT_SHA256:
        raise RuntimeError("frozen event-channel input hash changed")
    frame = pd.read_csv(INPUT)
    required = {
        "event",
        "channel",
        "time_utc",
        "raw_rows",
        "observed_dbm",
        "fixed12_prediction_dbm",
        "delta_gain_to_12_db",
    }
    if set(frame) != required:
        raise RuntimeError(f"unexpected input fields: {set(frame)}")
    frame = frame.copy()
    frame["timestamp"] = pd.to_datetime(frame["time_utc"], utc=True)
    event_time = frame.groupby("event")["timestamp"].median()
    origin = event_time.min()
    event_hours = (event_time - origin).dt.total_seconds() / 3600.0
    frame["event_time_hours"] = frame["event"].map(event_hours).astype(float)
    frame["observation_id"] = np.arange(len(frame), dtype=int)
    frame["link_residual_at_12db"] = (
        frame["observed_dbm"] - frame["fixed12_prediction_dbm"]
    )
    if len(frame) != 69 or frame["event"].nunique() != 16:
        raise RuntimeError("unexpected unified sample dimensions")
    return frame


def covariance_matrix(
    left: pd.DataFrame,
    right: pd.DataFrame,
    parameters: dict[str, float],
    config: AnalysisConfig,
) -> np.ndarray:
    left_channel = left["channel"].astype(str).to_numpy()
    right_channel = right["channel"].astype(str).to_numpy()
    same_channel = left_channel[:, None] == right_channel[None, :]
    covariance = parameters["sigma_channel"] ** 2 * same_channel.astype(float)

    if config.use_time_process:
        left_time = left["event_time_hours"].to_numpy(float)
        right_time = right["event_time_hours"].to_numpy(float)
        if config.independent_event_process:
            same_event = np.isclose(left_time[:, None], right_time[None, :])
            covariance += parameters["sigma_time"] ** 2 * same_event.astype(float)
        else:
            distance = np.abs(left_time[:, None] - right_time[None, :])
            covariance += parameters["sigma_time"] ** 2 * np.exp(
                -distance / parameters["time_scale_hours"]
            )

    left_id = left["observation_id"].to_numpy(int)
    right_id = right["observation_id"].to_numpy(int)
    same_observation = left_id[:, None] == right_id[None, :]
    covariance += parameters["sigma_error"] ** 2 * same_observation.astype(float)
    return covariance


def unpack_parameters(values: np.ndarray, config: AnalysisConfig) -> dict[str, float]:
    output = {
        "sigma_channel": float(np.exp(values[0])),
        "sigma_error": float(np.exp(values[1])),
    }
    if config.use_time_process:
        output["sigma_time"] = float(np.exp(values[2]))
        output["time_scale_hours"] = (
            0.0
            if config.independent_event_process
            else float(np.exp(values[3]))
        )
    else:
        output["sigma_time"] = 0.0
        output["time_scale_hours"] = float("nan")
    return output


def profiled_likelihood(
    log_parameters: np.ndarray,
    frame: pd.DataFrame,
    response: np.ndarray,
    design: np.ndarray,
    config: AnalysisConfig,
) -> tuple[float, np.ndarray, np.ndarray, np.ndarray, float]:
    parameters = unpack_parameters(log_parameters, config)
    covariance = covariance_matrix(frame, frame, parameters, config)
    covariance.flat[:: len(covariance) + 1] += 1e-8
    try:
        factor = cho_factor(covariance, lower=True, check_finite=False)
        kinv_design = cho_solve(factor, design, check_finite=False)
        kinv_response = cho_solve(factor, response, check_finite=False)
        information = design.T @ kinv_design
        coefficients = np.linalg.solve(information, design.T @ kinv_response)
        residual = response - design @ coefficients
        kinv_residual = cho_solve(factor, residual, check_finite=False)
        quadratic = float(residual @ kinv_residual)
        logdet = 2.0 * float(np.log(np.diag(factor[0])).sum())
        sign, logdet_information = np.linalg.slogdet(information)
        if sign <= 0:
            raise np.linalg.LinAlgError("non-positive design information")
    except (np.linalg.LinAlgError, ValueError):
        return 1e100, np.zeros(design.shape[1]), covariance, np.eye(design.shape[1]), math.inf

    n, p = design.shape
    if config.likelihood == "gaussian":
        # Restricted likelihood prevents variance components from treating fitted
        # mean parameters as independent observations.
        nll = 0.5 * (
            (n - p) * math.log(2.0 * math.pi)
            + logdet
            + logdet_information
            + quadratic
        )
    elif config.likelihood == "student_t":
        nu = config.student_df
        # A multivariate-t process supplies a robust global-scale sensitivity.
        nll = -(
            gammaln((nu + n) / 2.0)
            - gammaln(nu / 2.0)
            - 0.5 * (n * math.log(nu * math.pi) + logdet)
            - 0.5 * (nu + n) * math.log1p(quadratic / nu)
        )
    else:
        raise ValueError(config.likelihood)
    return float(nll), coefficients, covariance, information, quadratic


def initial_values(response: np.ndarray, config: AnalysisConfig) -> list[np.ndarray]:
    scale = max(float(np.std(response)), 0.5)
    specifications = (
        (0.45, 0.45, 0.45, 0.5),
        (0.80, 0.35, 0.60, 1.5),
        (0.35, 0.80, 0.50, 4.0),
        (0.60, 0.60, 0.25, 0.15),
        (0.25, 0.45, 0.90, 8.0),
    )
    output = []
    for channel, error, temporal, time_scale in specifications:
        values = [math.log(scale * channel), math.log(scale * error)]
        if config.use_time_process:
            values.append(math.log(scale * temporal))
            if not config.independent_event_process:
                values.append(math.log(time_scale))
        output.append(np.asarray(values, dtype=float))
    return output


def fit_model(
    frame: pd.DataFrame,
    response: np.ndarray,
    design: np.ndarray,
    config: AnalysisConfig,
) -> FitResult:
    sigma_bounds = (math.log(0.02), math.log(12.0))
    bounds = [sigma_bounds, sigma_bounds]
    if config.use_time_process:
        bounds.append(sigma_bounds)
        if not config.independent_event_process:
            bounds.append((math.log(0.05), math.log(24.0)))

    best = None
    for start in initial_values(response, config):
        optimized = minimize(
            lambda values: profiled_likelihood(values, frame, response, design, config)[0],
            start,
            method="L-BFGS-B",
            bounds=bounds,
            options={"maxiter": 1000, "ftol": 1e-11, "gtol": 1e-8},
        )
        if best is None or float(optimized.fun) < float(best.fun):
            best = optimized
    if best is None:
        raise RuntimeError("no optimization attempted")
    nll, coefficients, covariance, information, quadratic = profiled_likelihood(
        np.asarray(best.x), frame, response, design, config
    )
    return FitResult(
        coefficients=coefficients,
        covariance_parameters=unpack_parameters(np.asarray(best.x), config),
        nll=nll,
        converged=bool(best.success),
        message=str(best.message),
        covariance=covariance,
        design_information=information,
        quadratic=quadratic,
    )


def multivariate_gaussian_logpdf(
    value: np.ndarray, mean: np.ndarray, covariance: np.ndarray
) -> float:
    covariance = covariance.copy()
    covariance.flat[:: len(covariance) + 1] += 1e-8
    factor = cho_factor(covariance, lower=True, check_finite=False)
    residual = value - mean
    quadratic = float(residual @ cho_solve(factor, residual, check_finite=False))
    logdet = 2.0 * float(np.log(np.diag(factor[0])).sum())
    return -0.5 * (len(value) * math.log(2.0 * math.pi) + logdet + quadratic)


def multivariate_t_logpdf(
    value: np.ndarray,
    mean: np.ndarray,
    scale: np.ndarray,
    degrees_freedom: float,
) -> float:
    scale = scale.copy()
    scale.flat[:: len(scale) + 1] += 1e-8
    factor = cho_factor(scale, lower=True, check_finite=False)
    residual = value - mean
    quadratic = float(residual @ cho_solve(factor, residual, check_finite=False))
    logdet = 2.0 * float(np.log(np.diag(factor[0])).sum())
    dimension = len(value)
    return float(
        gammaln((degrees_freedom + dimension) / 2.0)
        - gammaln(degrees_freedom / 2.0)
        - 0.5 * (dimension * math.log(degrees_freedom * math.pi) + logdet)
        - 0.5
        * (degrees_freedom + dimension)
        * math.log1p(quadratic / degrees_freedom)
    )


def event_training_mask(
    frame: pd.DataFrame, held_event: int, config: AnalysisConfig
) -> np.ndarray:
    event_times = frame.groupby("event")["event_time_hours"].first()
    held_time = float(event_times.loc[held_event])
    separation_minutes = (
        frame["event"].map(event_times).astype(float).to_numpy() - held_time
    ) * 60.0
    if config.split == "leave_event_out":
        return (frame["event"].to_numpy(int) != held_event) & (
            np.abs(separation_minutes) > config.purge_minutes + 1e-9
        )
    if config.split == "forward":
        return separation_minutes < -config.purge_minutes - 1e-9
    raise ValueError(config.split)


def conditional_prediction(
    train: pd.DataFrame,
    test: pd.DataFrame,
    train_response: np.ndarray,
    test_response: np.ndarray,
    fit: FitResult,
    config: AnalysisConfig,
) -> tuple[np.ndarray, np.ndarray, float]:
    parameters = fit.covariance_parameters
    k_train = fit.covariance
    k_test_train = covariance_matrix(test, train, parameters, config)
    k_test = covariance_matrix(test, test, parameters, config)
    factor = cho_factor(k_train, lower=True, check_finite=False)
    train_design = np.ones((len(train), 1))
    test_design = np.ones((len(test), 1))
    coefficient = fit.coefficients
    centered = train_response - train_design @ coefficient
    conditional_mean = (
        test_design @ coefficient
        + k_test_train @ cho_solve(factor, centered, check_finite=False)
    )
    conditional_covariance = (
        k_test
        - k_test_train
        @ cho_solve(factor, k_test_train.T, check_finite=False)
    )
    mean_remainder = (
        test_design
        - k_test_train @ cho_solve(factor, train_design, check_finite=False)
    )
    conditional_covariance += (
        mean_remainder
        @ np.linalg.inv(fit.design_information)
        @ mean_remainder.T
    )
    conditional_covariance = 0.5 * (
        conditional_covariance + conditional_covariance.T
    )

    if config.likelihood == "gaussian":
        log_score = multivariate_gaussian_logpdf(
            test_response, conditional_mean, conditional_covariance
        )
        predictive_covariance = conditional_covariance
    else:
        conditional_df = config.student_df + len(train)
        scale_multiplier = (
            config.student_df + fit.quadratic
        ) / conditional_df
        conditional_scale = conditional_covariance * scale_multiplier
        log_score = multivariate_t_logpdf(
            test_response,
            conditional_mean,
            conditional_scale,
            conditional_df,
        )
        predictive_covariance = (
            conditional_scale
            * conditional_df
            / max(conditional_df - 2.0, 1.0)
        )
    return conditional_mean, predictive_covariance, log_score


def run_blocked_predictions(
    frame: pd.DataFrame, beta: float, config: AnalysisConfig
) -> tuple[pd.DataFrame, pd.DataFrame]:
    observation_records: list[dict[str, object]] = []
    event_records: list[dict[str, object]] = []
    for held_event in sorted(frame["event"].unique()):
        test = frame.loc[frame["event"] == held_event].copy()
        train = frame.loc[event_training_mask(frame, int(held_event), config)].copy()
        if len(train) < 20 or train["event"].nunique() < 5:
            continue
        train_response = (
            train["link_residual_at_12db"].to_numpy(float)
            - beta * train["delta_gain_to_12_db"].to_numpy(float)
        )
        test_response = (
            test["link_residual_at_12db"].to_numpy(float)
            - beta * test["delta_gain_to_12_db"].to_numpy(float)
        )
        fit = fit_model(
            train,
            train_response,
            np.ones((len(train), 1)),
            config,
        )
        conditional_mean, predictive_covariance, log_score = conditional_prediction(
            train,
            test,
            train_response,
            test_response,
            fit,
            config,
        )
        predicted_dbm = (
            test["fixed12_prediction_dbm"].to_numpy(float)
            + beta * test["delta_gain_to_12_db"].to_numpy(float)
            + conditional_mean
        )
        residual = test["observed_dbm"].to_numpy(float) - predicted_dbm
        predictive_sd = np.sqrt(np.maximum(np.diag(predictive_covariance), 0.0))
        event_time = str(test["time_utc"].min())
        for index, (_, row) in enumerate(test.iterrows()):
            observation_records.append(
                {
                    "configuration": config.name,
                    "hypothesis": MODEL_LABELS[beta],
                    "beta": beta,
                    "held_event": int(held_event),
                    "event_time_utc": event_time,
                    "channel": row["channel"],
                    "observed_dbm": float(row["observed_dbm"]),
                    "predicted_dbm": float(predicted_dbm[index]),
                    "residual_db": float(residual[index]),
                    "predictive_sd_db": float(predictive_sd[index]),
                    "training_points": len(train),
                    "training_events": int(train["event"].nunique()),
                }
            )
        event_records.append(
            {
                "configuration": config.name,
                "hypothesis": MODEL_LABELS[beta],
                "beta": beta,
                "held_event": int(held_event),
                "event_time_utc": event_time,
                "test_points": len(test),
                "training_points": len(train),
                "training_events": int(train["event"].nunique()),
                "log_predictive_density": float(log_score),
                "log_predictive_density_per_point": float(log_score / len(test)),
                "mae_db": float(np.mean(np.abs(residual))),
                "mse_db2": float(np.mean(np.square(residual))),
                "rmse_db": float(np.sqrt(np.mean(np.square(residual)))),
                "sigma_channel_db": fit.covariance_parameters["sigma_channel"],
                "sigma_time_db": fit.covariance_parameters["sigma_time"],
                "sigma_error_db": fit.covariance_parameters["sigma_error"],
                "time_scale_hours": fit.covariance_parameters["time_scale_hours"],
                "optimizer_converged": fit.converged,
                "optimizer_message": fit.message,
            }
        )
    return pd.DataFrame(observation_records), pd.DataFrame(event_records)


def exact_signflip_p(values: np.ndarray) -> float:
    observed = abs(float(np.mean(values)))
    randomized = (
        abs(float(np.mean(values * np.asarray(signs, dtype=float))))
        for signs in itertools.product((-1.0, 1.0), repeat=len(values))
    )
    return float(
        sum(value >= observed - 1e-14 for value in randomized)
        / (2 ** len(values))
    )


def bootstrap_mean_interval(values: np.ndarray, seed_offset: int) -> tuple[float, float]:
    rng = np.random.default_rng(SEED + seed_offset)
    samples = rng.integers(0, len(values), size=(200_000, len(values)))
    distribution = np.mean(values[samples], axis=1)
    lower, upper = np.quantile(distribution, (0.025, 0.975))
    return float(lower), float(upper)


def compare_hypotheses(
    observations: pd.DataFrame, events: pd.DataFrame
) -> tuple[pd.DataFrame, pd.DataFrame]:
    comparison_rows: list[dict[str, object]] = []
    paired_rows: list[pd.DataFrame] = []
    for config_index, configuration in enumerate(sorted(events["configuration"].unique())):
        subset = events.loc[events["configuration"] == configuration].copy()
        metrics = [
            "log_predictive_density_per_point",
            "mae_db",
            "mse_db2",
            "rmse_db",
        ]
        paired = subset.pivot(index="held_event", columns="hypothesis", values=metrics)
        full = "full_gain_precompensation"
        none = "no_gain_precompensation"
        paired = paired.dropna()
        delta_lpd = (
            paired["log_predictive_density_per_point"][none]
            - paired["log_predictive_density_per_point"][full]
        ).to_numpy(float)
        delta_mae = (
            paired["mae_db"][full] - paired["mae_db"][none]
        ).to_numpy(float)
        delta_mse = (
            paired["mse_db2"][full] - paired["mse_db2"][none]
        ).to_numpy(float)
        lpd_interval = bootstrap_mean_interval(delta_lpd, config_index * 10 + 1)
        mae_interval = bootstrap_mean_interval(delta_mae, config_index * 10 + 2)
        mse_interval = bootstrap_mean_interval(delta_mse, config_index * 10 + 3)

        observation_subset = observations.loc[
            observations["configuration"] == configuration
        ]
        point_metrics = {}
        for hypothesis in (full, none):
            residual = observation_subset.loc[
                observation_subset["hypothesis"] == hypothesis, "residual_db"
            ].to_numpy(float)
            point_metrics[hypothesis] = {
                "point_mae_db": float(np.mean(np.abs(residual))),
                "point_rmse_db": float(np.sqrt(np.mean(np.square(residual)))),
            }
        comparison_rows.append(
            {
                "configuration": configuration,
                "paired_events": len(paired),
                "test_points_per_hypothesis": len(observation_subset) // 2,
                "mean_event_lpd_no_minus_full": float(np.mean(delta_lpd)),
                "lpd_bootstrap_95_lower": lpd_interval[0],
                "lpd_bootstrap_95_upper": lpd_interval[1],
                "lpd_exact_signflip_two_sided_p": exact_signflip_p(delta_lpd),
                "events_lpd_favor_no": int(np.count_nonzero(delta_lpd > 0)),
                "events_lpd_favor_full": int(np.count_nonzero(delta_lpd < 0)),
                "mean_event_mae_full_minus_no_db": float(np.mean(delta_mae)),
                "mae_bootstrap_95_lower_db": mae_interval[0],
                "mae_bootstrap_95_upper_db": mae_interval[1],
                "mae_exact_signflip_two_sided_p": exact_signflip_p(delta_mae),
                "mean_event_mse_full_minus_no_db2": float(np.mean(delta_mse)),
                "mse_bootstrap_95_lower_db2": mse_interval[0],
                "mse_bootstrap_95_upper_db2": mse_interval[1],
                "mse_exact_signflip_two_sided_p": exact_signflip_p(delta_mse),
                "point_mae_no_db": point_metrics[none]["point_mae_db"],
                "point_mae_full_db": point_metrics[full]["point_mae_db"],
                "point_rmse_no_db": point_metrics[none]["point_rmse_db"],
                "point_rmse_full_db": point_metrics[full]["point_rmse_db"],
            }
        )
        flat = pd.DataFrame(
            {
                "configuration": configuration,
                "held_event": paired.index.astype(int),
                "delta_lpd_per_point_no_minus_full": delta_lpd,
                "delta_mae_full_minus_no_db": delta_mae,
                "delta_mse_full_minus_no_db2": delta_mse,
            }
        )
        event_times = (
            subset.groupby("held_event")["event_time_utc"].first().astype(str)
        )
        flat["event_time_utc"] = flat["held_event"].map(event_times)
        paired_rows.append(flat)
    return pd.DataFrame(comparison_rows), pd.concat(paired_rows, ignore_index=True)


def fit_continuous_beta(
    frame: pd.DataFrame, configuration: str = PRIMARY_CONFIG
) -> tuple[dict[str, object], pd.DataFrame]:
    config = next(item for item in CONFIGS if item.name == configuration)
    response = frame["link_residual_at_12db"].to_numpy(float)
    design = np.column_stack(
        (
            np.ones(len(frame)),
            frame["delta_gain_to_12_db"].to_numpy(float),
        )
    )
    fit = fit_model(frame, response, design, config)
    covariance_coefficients = np.linalg.inv(fit.design_information)
    beta = float(fit.coefficients[1])
    beta_se = float(np.sqrt(covariance_coefficients[1, 1]))
    critical = float(student_t.ppf(0.975, frame["event"].nunique() - 1))
    interval = (beta - critical * beta_se, beta + critical * beta_se)

    gain = frame["delta_gain_to_12_db"].to_numpy(float)
    ones = np.ones((len(frame), 1))
    factor = cho_factor(fit.covariance, lower=True, check_finite=False)
    beta_grid = np.linspace(-0.5, 1.5, 161)
    profile_rows = []
    for candidate in beta_grid:
        adjusted = response - candidate * gain
        information = ones.T @ cho_solve(factor, ones, check_finite=False)
        intercept = float(
            np.linalg.solve(
                information,
                ones.T @ cho_solve(factor, adjusted, check_finite=False),
            )[0]
        )
        residual = adjusted - intercept
        quadratic = float(
            residual @ cho_solve(factor, residual, check_finite=False)
        )
        profile_rows.append(
            {
                "beta": float(candidate),
                "relative_nll_fixed_covariance": 0.5
                * (quadratic - fit.quadratic),
            }
        )
    summary = {
        "configuration": config.name,
        "beta_hat": beta,
        "conditional_standard_error": beta_se,
        "event_t_approx_95_lower": interval[0],
        "event_t_approx_95_upper": interval[1],
        "beta0_standardized_distance": beta / beta_se,
        "beta1_standardized_distance": (beta - 1.0) / beta_se,
        **fit.covariance_parameters,
        "optimizer_converged": fit.converged,
        "optimizer_message": fit.message,
    }
    return summary, pd.DataFrame(profile_rows)


def sample_audit(frame: pd.DataFrame) -> pd.DataFrame:
    audit = (
        frame.groupby("event")
        .agg(
            event_time_utc=("time_utc", "min"),
            channel_event_points=("channel", "size"),
            raw_reports=("raw_rows", "sum"),
            gain_delta_min_db=("delta_gain_to_12_db", "min"),
            gain_delta_max_db=("delta_gain_to_12_db", "max"),
        )
        .reset_index()
    )
    audit["gain_delta_range_db"] = (
        audit["gain_delta_max_db"] - audit["gain_delta_min_db"]
    )
    audit["gain_varies_within_event_gt_0_05db"] = audit["gain_delta_range_db"] > 0.05
    return audit


def make_figures(
    paired: pd.DataFrame,
    comparisons: pd.DataFrame,
    continuous: dict[str, object],
    profile: pd.DataFrame,
) -> None:
    primary = paired.loc[paired["configuration"] == PRIMARY_CONFIG].copy()
    primary = primary.sort_values("held_event")
    colors = np.where(
        primary["delta_lpd_per_point_no_minus_full"] >= 0,
        "#0072B2",
        "#D55E00",
    )
    fig, ax = plt.subplots(figsize=(10.5, 4.8))
    ax.bar(
        np.arange(len(primary)),
        primary["delta_lpd_per_point_no_minus_full"],
        color=colors,
        width=0.76,
    )
    ax.axhline(0, color="#202020", linewidth=0.9)
    mean = float(primary["delta_lpd_per_point_no_minus_full"].mean())
    ax.axhline(mean, color="#009E73", linestyle="--", linewidth=1.5)
    labels = pd.to_datetime(primary["event_time_utc"]).dt.strftime("%H:%M")
    ax.set_xticks(np.arange(len(primary)), labels, rotation=55, ha="right")
    ax.set_ylabel("Held-out log predictive density difference per point\nno precompensation − full precompensation")
    ax.set_title(
        "Purged whole-event prediction under the two gain hypotheses",
        loc="left",
        fontsize=14,
        fontweight="bold",
    )
    row = comparisons.loc[comparisons["configuration"] == PRIMARY_CONFIG].iloc[0]
    ax.text(
        0.02,
        0.98,
        f"30-minute purge; {int(row['paired_events'])} paired events\n"
        f"mean={mean:+.3f}; paired sign-flip p={float(row['lpd_exact_signflip_two_sided_p']):.3f}",
        transform=ax.transAxes,
        va="top",
        fontsize=9,
        bbox={"facecolor": "white", "alpha": 0.88, "edgecolor": "0.75"},
    )
    ax.text(
        0.98,
        0.03,
        "Blue favors no gain precompensation\nOrange favors full gain precompensation",
        transform=ax.transAxes,
        ha="right",
        va="bottom",
        fontsize=8.5,
    )
    fig.tight_layout()
    fig.savefig(OUTPUT / "figure_1_purged_event_predictive_difference.png", dpi=300)
    fig.savefig(OUTPUT / "figure_1_purged_event_predictive_difference.pdf")
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(8.3, 4.8))
    ax.plot(profile["beta"], 2.0 * profile["relative_nll_fixed_covariance"], color="#202020")
    ax.axhline(3.841, color="#7A7A7A", linestyle=":", linewidth=1.2, label="95% likelihood threshold")
    ax.axvline(0, color="#D55E00", linestyle=":", linewidth=1.6, label="Full gain precompensation")
    ax.axvline(1, color="#0072B2", linestyle="--", linewidth=1.6, label="No gain precompensation")
    ax.axvline(float(continuous["beta_hat"]), color="#009E73", linewidth=1.7, label="Estimated β")
    ax.axvspan(
        float(continuous["event_t_approx_95_lower"]),
        float(continuous["event_t_approx_95_upper"]),
        color="#009E73",
        alpha=0.10,
    )
    ax.set_xlim(-0.5, 1.5)
    ax.set_ylim(0, max(8.0, float((2.0 * profile["relative_nll_fixed_covariance"]).max())))
    ax.set_xlabel("Fraction of modeled directional gain remaining, β")
    ax.set_ylabel("Conditional profile deviance, 2ΔNLL")
    ax.set_title(
        "Full-sample gain coefficient: an identifiability diagnostic",
        loc="left",
        fontsize=13.5,
        fontweight="bold",
    )
    ax.legend(frameon=False, fontsize=8.5)
    ax.text(
        0.02,
        0.96,
        f"β̂={float(continuous['beta_hat']):.3f}; "
        f"event-t interval [{float(continuous['event_t_approx_95_lower']):.3f}, "
        f"{float(continuous['event_t_approx_95_upper']):.3f}]\n"
        "Modeled gain varies >0.05 dB within only 2/16 events;\n"
        "this is not a blocked discrimination result.",
        transform=ax.transAxes,
        va="top",
        fontsize=9,
    )
    fig.tight_layout()
    fig.savefig(OUTPUT / "figure_2_continuous_beta_profile.png", dpi=300)
    fig.savefig(OUTPUT / "figure_2_continuous_beta_profile.pdf")
    plt.close(fig)

    ordered = comparisons.copy()
    no_purge = ordered.loc[
        ordered["configuration"] == "gaussian_ou_purge0"
    ].iloc[0]
    ordered = ordered.loc[ordered["configuration"] != "gaussian_ou_purge0"]
    ordered["label"] = ordered["configuration"].str.replace("_", " ", regex=False)
    ordered = ordered.sort_values("configuration")
    fig, ax = plt.subplots(figsize=(9.4, 5.6))
    y = np.arange(len(ordered))
    value = ordered["mean_event_lpd_no_minus_full"].to_numpy(float)
    lower = value - ordered["lpd_bootstrap_95_lower"].to_numpy(float)
    upper = ordered["lpd_bootstrap_95_upper"].to_numpy(float) - value
    ax.errorbar(
        value,
        y,
        xerr=np.vstack((lower, upper)),
        fmt="o",
        color="#202020",
        ecolor="#7A7A7A",
        capsize=4,
    )
    ax.axvline(0, color="#202020", linewidth=0.8)
    ax.set_yticks(y, ordered["label"])
    ax.set_xlabel(
        "Mean held-out log-density difference per point\n"
        "positive favors no gain precompensation"
    )
    ax.set_title(
        "Sensitivity across purge, temporal and robust likelihood choices",
        loc="left",
        fontsize=13.5,
        fontweight="bold",
    )
    ax.text(
        0.98,
        0.02,
        "No-purge leakage check omitted from scale: "
        f"{float(no_purge['mean_event_lpd_no_minus_full']):+.3f} "
        f"[{float(no_purge['lpd_bootstrap_95_lower']):+.3f}, "
        f"{float(no_purge['lpd_bootstrap_95_upper']):+.3f}]",
        transform=ax.transAxes,
        ha="right",
        va="bottom",
        fontsize=8.2,
    )
    fig.tight_layout()
    fig.savefig(OUTPUT / "figure_3_model_sensitivity.png", dpi=300)
    fig.savefig(OUTPUT / "figure_3_model_sensitivity.pdf")
    plt.close(fig)


def write_results_markdown(
    comparisons: pd.DataFrame, continuous: dict[str, object]
) -> None:
    primary = comparisons.loc[
        comparisons["configuration"] == PRIMARY_CONFIG
    ].iloc[0]
    boundary = comparisons.loc[
        comparisons["configuration"] == "gaussian_independent_event_purge30"
    ].iloc[0]
    forward = comparisons.loc[
        comparisons["configuration"] == "gaussian_ou_forward30"
    ].iloc[0]
    text = f"""# Antenna gain blocked-prediction results

## Primary blocked prediction

The primary analysis used a Gaussian channel-random/continuous-time OU model,
held out each complete time event, and purged observations within 30 minutes.
It retained {int(primary['paired_events'])} paired held-out events. Positive
log-density differences favor no gain precompensation.

- Mean event log-density difference per point:
  {float(primary['mean_event_lpd_no_minus_full']):+.4f}.
- Paired bootstrap 95% interval:
  [{float(primary['lpd_bootstrap_95_lower']):+.4f},
  {float(primary['lpd_bootstrap_95_upper']):+.4f}].
- Enumerated two-sided paired-event sign-flip p:
  {float(primary['lpd_exact_signflip_two_sided_p']):.4f}.
- Point RMSE: no precompensation
  {float(primary['point_rmse_no_db']):.3f} dB; full precompensation
  {float(primary['point_rmse_full_db']):.3f} dB.
- Point MAE: no precompensation
  {float(primary['point_mae_no_db']):.3f} dB; full precompensation
  {float(primary['point_mae_full_db']):.3f} dB.

## Temporal-boundary and forward diagnostics

The fitted OU timescale reached its 0.05-hour lower bound in most folds. In
the corresponding independent-event limit, the mean log-density difference
was {float(boundary['mean_event_lpd_no_minus_full']):+.4f}, with bootstrap
interval [{float(boundary['lpd_bootstrap_95_lower']):+.4f},
{float(boundary['lpd_bootstrap_95_upper']):+.4f}] and paired sign-flip
p={float(boundary['lpd_exact_signflip_two_sided_p']):.4f}. Its point RMSE was
{float(boundary['point_rmse_no_db']):.3f} dB under no gain precompensation and
{float(boundary['point_rmse_full_db']):.3f} dB under full gain precompensation.

Forward-only prediction reversed direction: the mean log-density difference
was {float(forward['mean_event_lpd_no_minus_full']):+.4f}, with bootstrap
interval [{float(forward['lpd_bootstrap_95_lower']):+.4f},
{float(forward['lpd_bootstrap_95_upper']):+.4f}]. These model-dependent sign
changes do not support a stable preference between the endpoint hypotheses.

The bootstrap and sign-flip values are dependence-sensitive diagnostics:
leave-event-out training sets overlap, and event exchangeability cannot be
verified from sixteen events.

## Continuous beta

The full-sample hierarchical estimate was beta =
{float(continuous['beta_hat']):.3f}, with conditional standard error
{float(continuous['conditional_standard_error']):.3f} and an event-t
approximation [{float(continuous['event_t_approx_95_lower']):.3f},
{float(continuous['event_t_approx_95_upper']):.3f}]. Beta=0 denotes full gain
precompensation and beta=1 denotes no gain precompensation.
Only 2 of 16 events contain more than 0.05 dB of within-event modeled gain
variation, so this interval is driven mainly by between-event comparisons. It
is conditional on the random-effects independence assumption and is not a
blocked or causal interval.

## Interpretation boundary

These are model-conditional predictions. The channel and temporal random
effects represent, but do not identify, propagation, receiver, satellite, HPA
or other persistent physical effects. Failure to distinguish the endpoints is
not proof that their mechanisms are equivalent.

The gain observable therefore remains excluded from the integrated estimator
under the tested physical model and available control sample.
"""
    (OUTPUT / "RESULTS.md").write_text(text, encoding="utf-8")



def main() -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    frame = load_data()
    all_observations = []
    all_events = []
    for config in CONFIGS:
        for beta in (0.0, 1.0):
            observations, events = run_blocked_predictions(frame, beta, config)
            if observations.empty or events.empty:
                raise RuntimeError(
                    f"no predictions for {config.name}, beta={beta}"
                )
            all_observations.append(observations)
            all_events.append(events)
    observations = pd.concat(all_observations, ignore_index=True)
    events = pd.concat(all_events, ignore_index=True)
    comparisons, paired = compare_hypotheses(observations, events)
    continuous_summaries = []
    continuous = None
    profile = None
    for configuration in (
        PRIMARY_CONFIG,
        "gaussian_independent_event_purge30",
        "gaussian_no_time_purge30",
    ):
        summary, candidate_profile = fit_continuous_beta(frame, configuration)
        continuous_summaries.append(summary)
        if configuration == PRIMARY_CONFIG:
            continuous, profile = summary, candidate_profile

    sample_audit(frame).to_csv(OUTPUT / "sample_audit.csv", index=False)
    observations.to_csv(OUTPUT / "blocked_predictions.csv", index=False)
    events.to_csv(OUTPUT / "blocked_event_scores.csv", index=False)
    comparisons.to_csv(OUTPUT / "hypothesis_comparison.csv", index=False)
    paired.to_csv(OUTPUT / "paired_event_differences.csv", index=False)
    pd.DataFrame(continuous_summaries).to_csv(
        OUTPUT / "continuous_beta_summary.csv", index=False
    )
    profile.to_csv(OUTPUT / "continuous_beta_profile.csv", index=False)
    manifest = {
        "model": "antenna-gain-blocked-prediction",
        "status": "DERIVED, MODEL-CONDITIONAL",
        "python": platform.python_version(),
        "seed": SEED,
        "input": {
            "path": str(INPUT.relative_to(ROOT)),
            "sha256": sha256(INPUT),
        },
        "configurations": [asdict(config) for config in CONFIGS],
    }
    (OUTPUT / "manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    make_figures(paired, comparisons, continuous, profile)
    write_results_markdown(comparisons, continuous)


if __name__ == "__main__":
    main()

