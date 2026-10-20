#!/usr/bin/env python3
"""Scan two-station publication-trace correlation over seventh-arc source geometry.

The input waveforms are calibrated vectors extracted from Kadri Figure 9, not
raw CTBTO hydrophone channels. Source cells only select an interstation
distance-difference lag. Correlation maxima are therefore contours, not unique
locations or event associations.
"""

from __future__ import annotations

import copy
import csv
import hashlib
import json
import math
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.lines import Line2D
from scipy.ndimage import maximum_filter1d
from scipy.optimize import brentq
from scipy.signal import correlate, correlation_lags, find_peaks, hilbert

import aligned_detection_analysis as aligned
import event_pair_analysis as base

import simulated_waveforms as simulated

HERE = Path(__file__).resolve().parents[1]
DATA = HERE / "data"
OUTPUT = HERE / "outputs"
CONFIG_PATH = DATA / "two-station-correlation-config.json"
EVENT_CONFIG_PATH = DATA / "event-pair-analysis-config.json"
FILTER_CONFIG_PATH = DATA / "filter-sensitivity-config.json"
TARGET_PATH = DATA / "acoustic-alignment-source-targets.csv"
TABLE_PATH = DATA / "kadri-table1-transients.csv"
PDF_METADATA = {"CreationDate": None, "ModDate": None}


@dataclass
class Series:
    time_epoch_s: np.ndarray
    values: np.ndarray
    valid: np.ndarray


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        raise ValueError(f"No rows for {path}")
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def iso_utc(epoch_s: float) -> str:
    return (
        datetime.fromtimestamp(float(epoch_s), timezone.utc)
        .isoformat(timespec="milliseconds")
        .replace("+00:00", "Z")
    )


def panel_standardise(values: np.ndarray, indices: np.ndarray, valid: np.ndarray) -> None:
    selected = indices[valid[indices]]
    if selected.size < 3:
        raise ValueError("Too few valid samples to standardise a panel")
    centre = float(np.mean(values[selected]))
    scale = float(np.std(values[selected]))
    values[selected] = (values[selected] - centre) / max(scale, 1e-12)


def build_h01_series(traces: dict[str, base.Trace], guard_s: float, dt: float) -> Series:
    start = traces["b"].epoch_s[0]
    end = traces["c"].epoch_s[-1]
    time = np.arange(start, end + dt / 2.0, dt)
    values = np.zeros(time.size)
    valid = np.zeros(time.size, dtype=bool)
    panel_indices = {}
    for panel_name in ("b", "c"):
        trace = traces[panel_name]
        indices = np.rint((trace.epoch_s - start) / dt).astype(int)
        values[indices] = trace.score
        good = (
            (trace.epoch_s >= trace.epoch_s[0] + guard_s)
            & (trace.epoch_s <= trace.epoch_s[-1] - guard_s)
        )
        valid[indices[good]] = True
        panel_indices[panel_name] = indices
    for indices in panel_indices.values():
        panel_standardise(values, indices, valid)
    return Series(time, values, valid)


def build_h08_series(
    results: dict[str, dict],
    rank: int | None,
    mask_airgun: bool,
    mask_half_width_s: float,
    guard_s: float,
    dt: float,
    screen: dict,
) -> Series:
    start = results["d"]["panel"].epoch_s[0]
    end = results["e"]["panel"].epoch_s[-1]
    time = np.arange(start, end + dt / 2.0, dt)
    values = np.zeros(time.size)
    valid = np.zeros(time.size, dtype=bool)
    panel_indices = {}
    for panel_name in ("d", "e"):
        result = results[panel_name]
        panel = result["panel"]
        indices = np.rint((panel.epoch_s - start) / dt).astype(int)
        if rank is None:
            centred = panel.pressure_pa - float(np.median(panel.pressure_pa))
            panel_score = base.score_signal(centred, screen)
        else:
            panel_score = result[f"rank_{rank}"]["score"]
        values[indices] = panel_score
        good = (
            (panel.epoch_s >= panel.epoch_s[0] + guard_s)
            & (panel.epoch_s <= panel.epoch_s[-1] - guard_s)
        )
        valid[indices[good]] = True
        if mask_airgun:
            mask = aligned.observed_centre_mask(result, mask_half_width_s)
            valid[indices[mask]] = False
        panel_indices[panel_name] = indices
    for indices in panel_indices.values():
        panel_standardise(values, indices, valid)
    return Series(time, values, valid)

def build_trace_field_series(
    traces: dict[str, base.Trace],
    panel_names: tuple[str, ...],
    field: str,
    guard_s: float,
    dt: float,
    overrides: dict[str, np.ndarray] | None = None,
) -> Series:
    """Join publication panels without applying the periodic-airgun model."""
    start = traces[panel_names[0]].epoch_s[0]
    end = traces[panel_names[-1]].epoch_s[-1]
    time = np.arange(start, end + dt / 2.0, dt)
    values = np.zeros(time.size)
    valid = np.zeros(time.size, dtype=bool)
    panel_indices: list[np.ndarray] = []
    for panel_name in panel_names:
        trace = traces[panel_name]
        indices = np.rint((trace.epoch_s - start) / dt).astype(int)
        if overrides is not None and panel_name in overrides:
            panel_values = overrides[panel_name]
        elif field == "score":
            panel_values = trace.score
        elif field == "pressure":
            panel_values = trace.pressure_pa
        else:
            raise ValueError(f"Unsupported publication field {field}")
        if panel_values.size != indices.size:
            raise ValueError(f"Panel override size mismatch for {panel_name}")
        values[indices] = panel_values
        good = (
            (trace.epoch_s >= trace.epoch_s[0] + guard_s)
            & (trace.epoch_s <= trace.epoch_s[-1] - guard_s)
        )
        valid[indices[good]] = True
        panel_indices.append(indices)
    for indices in panel_indices:
        panel_standardise(values, indices, valid)
    return Series(time, values, valid)


def fft_correlation_response(
    h01: Series,
    h08: Series,
    dt: float,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Pearson response for every station-arrival lag using masked FFT sums."""
    x = h01.values
    y = h08.values
    mx = h01.valid.astype(float)
    my = h08.valid.astype(float)

    def cross(left: np.ndarray, right: np.ndarray) -> np.ndarray:
        return correlate(left, right, mode="full", method="fft")

    count = cross(my, mx)
    sum_x = cross(my, x * mx)
    sum_y = cross(y * my, mx)
    sum_x2 = cross(my, x * x * mx)
    sum_y2 = cross(y * y * my, mx)
    sum_xy = cross(y * my, x * mx)
    safe_count = np.maximum(count, 1.0)
    covariance = sum_xy - sum_x * sum_y / safe_count
    variance_x = sum_x2 - sum_x * sum_x / safe_count
    variance_y = sum_y2 - sum_y * sum_y / safe_count
    response = np.divide(
        covariance,
        np.sqrt(np.maximum(variance_x * variance_y, 1e-20)),
        out=np.full_like(covariance, np.nan),
        where=(count >= 100.0) & (variance_x > 0.0) & (variance_y > 0.0),
    )
    correlation_lag = correlation_lags(y.size, x.size, mode="full")
    start_difference_s = h08.time_epoch_s[0] - h01.time_epoch_s[0]
    arrival_lag_s = start_difference_s + correlation_lag * dt
    arrival_lag_steps = np.rint(arrival_lag_s / dt).astype(int)
    expected = np.arange(arrival_lag_steps[0], arrival_lag_steps[-1] + 1)
    if not np.array_equal(arrival_lag_steps, expected):
        raise ValueError("FFT lag grid is not contiguous")
    return arrival_lag_steps, response, np.rint(count).astype(int)


def response_at_steps(
    all_steps: np.ndarray,
    values: np.ndarray,
    requested_steps: np.ndarray,
) -> np.ndarray:
    indices = requested_steps - int(all_steps[0])
    if np.any(indices < 0) or np.any(indices >= values.size):
        raise ValueError("Requested acquisition lag lies outside FFT response")
    return values[indices]


def aligned_pair_arrays(
    h01: Series,
    h08: Series,
    lag_steps: int,
    dt: float,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    lag_s = lag_steps * dt
    h01_index = np.rint(
        (h08.time_epoch_s - lag_s - h01.time_epoch_s[0]) / dt
    ).astype(int)
    safe = np.clip(h01_index, 0, h01.values.size - 1)
    valid = (
        h08.valid
        & (h01_index >= 0)
        & (h01_index < h01.values.size)
        & h01.valid[safe]
    )
    return safe, h01.values[safe], h08.values, valid


def rolling_pair_series(
    left: np.ndarray,
    right: np.ndarray,
    valid: np.ndarray,
    product_width: int,
    correlation_width: int,
) -> tuple[np.ndarray, np.ndarray]:
    valid_float = valid.astype(float)
    product_kernel = np.ones(max(2, product_width))
    product = np.zeros(left.size)
    product[valid] = left[valid] * right[valid]
    product_count = np.convolve(valid_float, product_kernel, mode="same")
    rolling_product = np.divide(
        np.convolve(product, product_kernel, mode="same"),
        product_count,
        out=np.full(left.size, np.nan),
        where=product_count >= 0.75 * product_kernel.size,
    )

    correlation_kernel = np.ones(max(2, correlation_width))
    count = np.convolve(valid_float, correlation_kernel, mode="same")
    sum_left = np.convolve(left * valid_float, correlation_kernel, mode="same")
    sum_right = np.convolve(right * valid_float, correlation_kernel, mode="same")
    sum_left2 = np.convolve(left * left * valid_float, correlation_kernel, mode="same")
    sum_right2 = np.convolve(right * right * valid_float, correlation_kernel, mode="same")
    sum_cross = np.convolve(left * right * valid_float, correlation_kernel, mode="same")
    safe_count = np.maximum(count, 1.0)
    covariance = sum_cross - sum_left * sum_right / safe_count
    variance_left = sum_left2 - sum_left * sum_left / safe_count
    variance_right = sum_right2 - sum_right * sum_right / safe_count
    rolling_correlation = np.divide(
        covariance,
        np.sqrt(np.maximum(variance_left * variance_right, 1e-20)),
        out=np.full(left.size, np.nan),
        where=(
            (count >= 0.75 * correlation_kernel.size)
            & (variance_left > 0.0)
            & (variance_right > 0.0)
        ),
    )
    return rolling_product, rolling_correlation


def trailing_pearson_series(
    left: np.ndarray,
    right: np.ndarray,
    valid: np.ndarray,
    width: int,
) -> np.ndarray:
    """Pearson r for fully supported windows ending at each sample."""
    width = max(2, int(width))
    output = np.full(left.size, np.nan)
    if width > left.size:
        return output
    valid_float = valid.astype(float)

    def window_sum(values: np.ndarray) -> np.ndarray:
        cumulative = np.concatenate(([0.0], np.cumsum(values)))
        return cumulative[width:] - cumulative[:-width]

    count = window_sum(valid_float)
    sum_left = window_sum(left * valid_float)
    sum_right = window_sum(right * valid_float)
    sum_left2 = window_sum(left * left * valid_float)
    sum_right2 = window_sum(right * right * valid_float)
    sum_cross = window_sum(left * right * valid_float)
    safe_count = np.maximum(count, 1.0)
    covariance = sum_cross - sum_left * sum_right / safe_count
    variance_left = sum_left2 - sum_left * sum_left / safe_count
    variance_right = sum_right2 - sum_right * sum_right / safe_count
    values = np.divide(
        covariance,
        np.sqrt(np.maximum(variance_left * variance_right, 1e-20)),
        out=np.full_like(covariance, np.nan),
        where=(
            (count >= width)
            & (variance_left > 0.0)
            & (variance_right > 0.0)
        ),
    )
    output[width - 1:] = values
    return output


def finite_pearson(
    left: np.ndarray,
    right: np.ndarray,
    valid: np.ndarray,
) -> float:
    if np.count_nonzero(valid) < 3:
        return float("nan")
    return float(np.corrcoef(left[valid], right[valid])[0, 1])


def template_compatibility(
    values: np.ndarray,
    valid: np.ndarray,
    centre_index: int,
    half_width_steps: int,
    dt: float,
) -> float:
    start = max(0, centre_index - half_width_steps)
    end = min(values.size, centre_index + half_width_steps + 1)
    observed = values[start:end]
    observed_valid = valid[start:end]
    relative_s = (np.arange(start, end) - centre_index) * dt
    pulse = simulated.make_pulse(relative_s)
    envelope = np.abs(hilbert(pulse))
    best = -np.inf
    for shift_s in np.arange(-2.0, 2.0001, 0.25):
        shifted = np.interp(
            relative_s - shift_s,
            relative_s,
            envelope,
            left=0.0,
            right=0.0,
        )
        value = finite_pearson(observed, shifted, observed_valid)
        if np.isfinite(value):
            best = max(best, value)
    return float(best) if np.isfinite(best) else float("nan")


def nearest_periodic_context(
    h08_epoch_s: float,
    h08_results: dict[str, dict],
    screen: dict,
) -> dict:
    for panel_name in ("d", "e"):
        result = h08_results[panel_name]
        panel = result["panel"]
        if panel.epoch_s[0] <= h08_epoch_s <= panel.epoch_s[-1]:
            period = float(result["geometry"].fitted_period_s)
            centres = np.concatenate(
                (
                    [result["geometry"].observed_centres_s[0] - period],
                    result["geometry"].observed_centres_s,
                    [result["geometry"].observed_centres_s[-1] + period],
                )
            )
            panel_time_s = h08_epoch_s - panel.start_epoch_s
            nearest = float(centres[np.argmin(np.abs(centres - panel_time_s))])
            centred = panel.pressure_pa - float(np.median(panel.pressure_pa))
            raw_score = base.score_signal(centred, screen)
            pulse_maxima = []
            for centre in result["geometry"].observed_centres_s:
                within = np.abs(panel.time_s - float(centre)) <= 3.0
                if np.any(within):
                    pulse_maxima.append(float(np.max(raw_score[within])))
            target_window = np.abs(panel.time_s - panel_time_s) <= 3.0
            target_maximum = float(np.max(raw_score[target_window]))
            pulse_values = np.asarray(pulse_maxima)
            return {
                "h08_panel": panel_name,
                "seconds_from_nearest_periodic_centre": float(panel_time_s - nearest),
                "within_three_second_periodic_mask": bool(
                    abs(panel_time_s - nearest) <= 3.0
                ),
                "raw_energy_maximum_plus_minus_3s": target_maximum,
                "percentile_among_observed_pulse_windows": float(
                    np.mean(pulse_values <= target_maximum)
                ),
                "observed_pulse_window_count": int(pulse_values.size),
                "rank_among_observed_pulse_windows": int(1 + np.count_nonzero(pulse_values > target_maximum)),
            }
    return {
        "h08_panel": "",
        "seconds_from_nearest_periodic_centre": float("nan"),
        "within_three_second_periodic_mask": False,
        "raw_energy_maximum_plus_minus_3s": float("nan"),
        "percentile_among_observed_pulse_windows": float("nan"),
        "observed_pulse_window_count": 0,
        "rank_among_observed_pulse_windows": 0,
    }


def acquisition_hypothesis_steps(
    base_lag_s: np.ndarray,
    acquisition: dict,
    dt: float,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    base_steps = np.rint(base_lag_s / dt).astype(int)
    offset_s = np.arange(
        float(acquisition["fine_offset_min_s"]),
        float(acquisition["fine_offset_max_s"]) + 0.5 * float(acquisition["fine_offset_step_s"]),
        float(acquisition["fine_offset_step_s"]),
    )
    offset_steps = np.rint(offset_s / dt).astype(int)
    total_steps = np.unique((base_steps[:, None] + offset_steps[None, :]).ravel())
    return base_steps, offset_steps, total_steps


def select_independent_response_steps(
    steps: np.ndarray,
    response: np.ndarray,
    count: int,
    separation_steps: int,
) -> list[int]:
    eligible = np.flatnonzero(np.isfinite(response))
    ordered = eligible[np.argsort(response[eligible])[::-1]]
    selected: list[int] = []
    for index in ordered:
        step = int(steps[index])
        if all(abs(step - previous) > separation_steps for previous in selected):
            selected.append(step)
        if len(selected) >= count:
            break
    return selected


def acquisition_null_maxima(
    traces: dict[str, base.Trace],
    h01: Series,
    requested_steps: np.ndarray,
    event_configuration: dict,
    acquisition: dict,
    guard_s: float,
    dt: float,
) -> tuple[np.ndarray, np.ndarray]:
    rng = np.random.default_rng(int(acquisition["iaaft_random_seed"]))
    replicates = int(acquisition["iaaft_replicates"])
    iterations = int(acquisition["iaaft_iterations"])
    null_maxima = np.empty(replicates)
    spectral_errors = np.empty((replicates, 2))
    for replicate in range(replicates):
        overrides = {}
        for panel_index, panel_name in enumerate(("d", "e")):
            surrogate_pressure, error = aligned.iaaft_surrogate(
                traces[panel_name].pressure_pa,
                rng,
                iterations,
            )
            overrides[panel_name] = base.score_signal(
                surrogate_pressure,
                event_configuration["trace_screen"],
            )
            spectral_errors[replicate, panel_index] = error
        surrogate_h08 = build_trace_field_series(
            traces,
            ("d", "e"),
            "score",
            guard_s,
            dt,
            overrides,
        )
        all_steps, all_response, _ = fft_correlation_response(h01, surrogate_h08, dt)
        null_values = response_at_steps(all_steps, all_response, requested_steps)
        null_maxima[replicate] = float(np.nanmax(null_values))
    return null_maxima, spectral_errors

def score_series_null_maxima(
    h01: Series,
    h08: Series,
    requested_steps: np.ndarray,
    acquisition: dict,
    dt: float,
) -> tuple[np.ndarray, np.ndarray]:
    """IAAFT null for an already-derived score series, panel by panel."""
    rng = np.random.default_rng(int(acquisition["iaaft_random_seed"]))
    replicates = int(acquisition["iaaft_replicates"])
    iterations = int(acquisition["iaaft_iterations"])
    null_maxima = np.empty(replicates)
    spectral_errors = np.empty((replicates, 2))
    midpoint = base.parse_utc("2014-03-08T01:10:00Z").timestamp()
    panel_masks = (
        h08.valid & (h08.time_epoch_s < midpoint),
        h08.valid & (h08.time_epoch_s >= midpoint),
    )
    for replicate in range(replicates):
        surrogate = Series(
            time_epoch_s=h08.time_epoch_s,
            values=np.zeros_like(h08.values),
            valid=h08.valid.copy(),
        )
        for panel_index, panel_mask in enumerate(panel_masks):
            indices = np.flatnonzero(panel_mask)
            if indices.size < 100:
                raise ValueError("Too few filtered-score samples for IAAFT null")
            values, error = aligned.iaaft_surrogate(
                h08.values[indices], rng, iterations
            )
            surrogate.values[indices] = values
            spectral_errors[replicate, panel_index] = error
        all_steps, all_response, _ = fft_correlation_response(h01, surrogate, dt)
        null_values = response_at_steps(all_steps, all_response, requested_steps)
        null_maxima[replicate] = float(np.nanmax(null_values))
    return null_maxima, spectral_errors



def unfiltered_acquisition_scan(
    configuration: dict,
    event_configuration: dict,
    cells: list[dict],
    distance_h01: np.ndarray,
    distance_h08: np.ndarray,
    traces: dict[str, base.Trace],
    h08_results: dict[str, dict],
    h01_energy: Series,
    h08_energy: Series,
    h01_pressure: Series,
    h08_pressure: Series,
    dt: float,
    acquisition_key: str = "unfiltered_acquisition",
    null_mode: str = "publication_pressure",
) -> dict:
    acquisition = configuration[acquisition_key]
    central = float(configuration["central_celerity_km_s"])
    base_lag_s = (distance_h08 - distance_h01) / central
    base_steps, offset_steps, hypothesis_steps = acquisition_hypothesis_steps(
        base_lag_s,
        acquisition,
        dt,
    )

    all_energy_steps, all_energy_response, all_energy_count = fft_correlation_response(
        h01_energy,
        h08_energy,
        dt,
    )
    all_pressure_steps, all_pressure_response, _ = fft_correlation_response(
        h01_pressure,
        h08_pressure,
        dt,
    )
    energy_response = response_at_steps(
        all_energy_steps,
        all_energy_response,
        hypothesis_steps,
    )
    pressure_response = response_at_steps(
        all_pressure_steps,
        all_pressure_response,
        hypothesis_steps,
    )
    paired_count = response_at_steps(
        all_energy_steps,
        all_energy_count,
        hypothesis_steps,
    ).astype(int)

    separation_steps = int(
        round(float(acquisition["independent_response_separation_s"]) / dt)
    )
    selected_steps = select_independent_response_steps(
        hypothesis_steps,
        energy_response,
        int(acquisition["top_response_count"]),
        separation_steps,
    )
    if null_mode == "publication_pressure":
        null_maxima, spectral_errors = acquisition_null_maxima(
            traces,
            h01_energy,
            hypothesis_steps,
            event_configuration,
            acquisition,
            float(configuration["panel_edge_guard_s"]),
            dt,
        )
    elif null_mode == "score_series":
        null_maxima, spectral_errors = score_series_null_maxima(
            h01_energy, h08_energy, hypothesis_steps, acquisition, dt
        )
    else:
        raise ValueError(f"Unsupported acquisition null mode {null_mode}")

    response_centre = float(np.nanmedian(energy_response))
    response_scale = float(
        1.4826 * np.nanmedian(np.abs(energy_response - response_centre))
    )
    probability_mass = np.asarray([float(row["probabilityMass"]) for row in cells])
    density = np.asarray([float(row["densityPerKm2"]) for row in cells])
    source_start, source_end = (
        base.parse_utc(value).timestamp()
        for value in acquisition["source_time_control_utc"]
    )
    product_width = int(round(float(acquisition["local_product_window_s"]) / dt))
    correlation_width = int(
        round(float(acquisition["local_correlation_window_s"]) / dt)
    )
    local_half = correlation_width // 2
    rows: list[dict] = []
    internals: list[dict] = []
    offset_step_set = set(map(int, offset_steps))

    for rank, selected_step in enumerate(selected_steps, start=1):
        response_index = int(np.searchsorted(hypothesis_steps, selected_step))
        delta_steps = selected_step - base_steps
        compatible = np.asarray(
            [int(value) in offset_step_set for value in delta_steps],
            dtype=bool,
        )
        candidates = np.flatnonzero(compatible)
        if candidates.size == 0:
            raise ValueError("Selected acquisition lag has no source-cell hypothesis")
        representative = int(
            candidates[
                np.lexsort(
                    (
                        np.abs(delta_steps[candidates]),
                        -density[candidates],
                    )
                )[0]
            ]
        )
        lag_s = selected_step * dt
        safe, left, right, valid = aligned_pair_arrays(
            h01_energy,
            h08_energy,
            selected_step,
            dt,
        )
        rolling_product, rolling_correlation = rolling_pair_series(
            left,
            right,
            valid,
            product_width,
            correlation_width,
        )
        source_epoch = (
            h01_energy.time_epoch_s[safe]
            - distance_h01[representative] / central
        )
        eligible_time = (
            valid
            & np.isfinite(rolling_product)
            & (source_epoch >= source_start)
            & (source_epoch <= source_end)
        )
        eligible_indices = np.flatnonzero(eligible_time)
        if eligible_indices.size == 0:
            raise ValueError("No valid source-time samples for acquisition candidate")
        candidate_index = int(
            eligible_indices[np.argmax(rolling_product[eligible_indices])]
        )
        local = np.zeros(valid.size, dtype=bool)
        local[
            max(0, candidate_index - local_half):
            min(valid.size, candidate_index + local_half + 1)
        ] = True
        local &= valid
        local_energy_r = finite_pearson(left, right, local)

        pressure_safe, pressure_left, pressure_right, pressure_valid = aligned_pair_arrays(
            h01_pressure,
            h08_pressure,
            selected_step,
            dt,
        )
        if not np.array_equal(pressure_safe, safe):
            raise ValueError("Pressure and energy alignment indices differ")
        pressure_local = local & pressure_valid
        local_pressure_r = finite_pearson(
            pressure_left,
            pressure_right,
            pressure_local,
        )
        template_h01 = template_compatibility(
            left,
            valid,
            candidate_index,
            local_half,
            dt,
        )
        template_h08 = template_compatibility(
            right,
            valid,
            candidate_index,
            local_half,
            dt,
        )
        h08_arrival = float(h08_energy.time_epoch_s[candidate_index])
        periodic = nearest_periodic_context(
            h08_arrival,
            h08_results,
            event_configuration["trace_screen"],
        )
        local_background = rolling_product[
            np.isfinite(rolling_product)
            & (source_epoch >= source_start)
            & (source_epoch <= source_end)
        ]
        energy_r = float(energy_response[response_index])
        scan_p = float(
            (1 + np.count_nonzero(null_maxima >= energy_r))
            / (null_maxima.size + 1)
        )
        row = {
            "rank": rank,
            "energy_correlation_r": energy_r,
            "pressure_correlation_r": float(pressure_response[response_index]),
            "lag_response_percentile": float(
                np.mean(energy_response <= energy_r)
            ),
            "lag_response_robust_z": float(
                (energy_r - response_centre) / max(response_scale, 1e-12)
            ),
            "iaaft_scan_max_p": scan_p,
            "total_interstation_lag_s": lag_s,
            "base_geometry_lag_s": float(base_lag_s[representative]),
            "fine_propagation_offset_s": float(delta_steps[representative] * dt),
            "representative_cell_id": cells[representative]["id"],
            "along_nm": float(cells[representative]["alongNm"]),
            "cross_nm": float(cells[representative]["crossNm"]),
            "latitude_deg": float(cells[representative]["latitude"]),
            "longitude_deg_e": float(cells[representative]["longitude"]),
            "representative_density_per_km2": float(density[representative]),
            "representative_in_current_pleiades_hpd50": str(
                cells[representative]["in_hpd50"]
            ).lower() == "true",
            "representative_in_current_pleiades_hpd90": str(
                cells[representative]["in_hpd90"]
            ).lower() == "true",
            "representative_in_current_pleiades_hpd95": str(
                cells[representative]["in_hpd95"]
            ).lower() == "true",
            "compatible_cell_count": int(candidates.size),
            "compatible_pleiades_probability_mass": float(
                np.sum(probability_mass[compatible])
            ),
            "paired_sample_count": int(paired_count[response_index]),
            "primary_source_utc": iso_utc(source_epoch[candidate_index]),
            "h01_arrival_utc": iso_utc(
                h01_energy.time_epoch_s[safe[candidate_index]]
            ),
            "h08_arrival_utc": iso_utc(h08_arrival),
            "local_20s_energy_correlation_r": local_energy_r,
            "local_20s_pressure_correlation_r": local_pressure_r,
            "local_4s_product": float(rolling_product[candidate_index]),
            "local_4s_product_percentile": float(
                np.mean(local_background <= rolling_product[candidate_index])
            ),
            "generic_template_h01_correlation": template_h01,
            "generic_template_h08_correlation": template_h08,
            "generic_template_mean_correlation": float(
                np.nanmean([template_h01, template_h08])
            ),
            **periodic,
            "status": acquisition.get(
                "candidate_status",
                "UNFILTERED_PUBLICATION_TRACE_ACQUISITION_CANDIDATE_"
                "NOT_EVENT_ASSOCIATION",
            ),
        }
        rows.append(row)
        internals.append(
            {
                "row": row,
                "representative_index": representative,
                "lag_steps": selected_step,
                "candidate_index": candidate_index,
                "safe": safe,
                "left": left,
                "right": right,
                "valid": valid,
                "source_epoch": source_epoch,
                "rolling_product": rolling_product,
                "rolling_correlation": rolling_correlation,
            }
        )

    flattened_hypotheses = (
        base_steps[:, None] + offset_steps[None, :]
    ).ravel()
    unique_hypotheses, hypothesis_count = np.unique(
        flattened_hypotheses,
        return_counts=True,
    )
    if not np.array_equal(unique_hypotheses, hypothesis_steps):
        raise ValueError("Acquisition hypothesis accounting mismatch")
    response_rows = [
        {
            "total_interstation_lag_s": float(step * dt),
            "total_interstation_lag_min": float(step * dt / 60.0),
            "energy_correlation_r": float(energy_response[index]),
            "pressure_correlation_r": float(pressure_response[index]),
            "paired_sample_count": int(paired_count[index]),
            "cell_offset_hypothesis_count": int(hypothesis_count[index]),
        }
        for index, step in enumerate(hypothesis_steps)
        if np.isfinite(energy_response[index])
    ]
    return {
        "rows": rows,
        "internals": internals,
        "response_rows": response_rows,
        "hypothesis_steps": hypothesis_steps,
        "energy_response": energy_response,
        "pressure_response": pressure_response,
        "paired_count": paired_count,
        "null_maxima": null_maxima,
        "spectral_errors": spectral_errors,
        "response_centre": response_centre,
        "response_scale": response_scale,
        "offset_steps": offset_steps,
    }

def empirical_upper_tail_fraction(values: np.ndarray, value: float) -> float:
    """Conservative finite-sample upper-tail plotting fraction."""
    return float((1 + np.count_nonzero(values > value)) / (values.size + 1))


def pulse_cycle_distribution(
    h08_results: dict[str, dict],
    screen: dict,
    configuration: dict,
    dt: float,
) -> tuple[list[dict], list[dict]]:
    """Measure every fitted H08S cycle using its pulse core and local shoulders."""
    settings = configuration["pulse_conditioned_acquisition"]
    core_half = float(settings["cycle_core_half_width_s"])
    shoulder_inner = float(settings["cycle_shoulder_inner_s"])
    shoulder_outer = float(settings["cycle_shoulder_outer_s"])
    rows: list[dict] = []
    summaries: list[dict] = []

    for panel_name in ("d", "e"):
        result = h08_results[panel_name]
        panel = result["panel"]
        cycles = result["cycles"]
        geometry = result["geometry"]
        core = np.abs(cycles.time_s) <= core_half
        shoulder = (
            (np.abs(cycles.time_s) > shoulder_inner)
            & (np.abs(cycles.time_s) <= shoulder_outer)
        )
        full = np.abs(cycles.time_s) <= shoulder_outer
        if not np.any(core) or not np.any(shoulder):
            raise ValueError("Pulse core or shoulder definition has no samples")
        centred_panel = panel.pressure_pa - float(np.median(panel.pressure_pa))
        raw_score = base.score_signal(centred_panel, screen)
        panel_rows: list[dict] = []
        for index, (centre, cycle) in enumerate(
            zip(geometry.observed_centres_s, cycles.values)
        ):
            core_ms = float(np.mean(cycle[core] ** 2))
            shoulder_ms = float(np.mean(cycle[shoulder] ** 2))
            full_ms = float(np.mean(cycle[full] ** 2))
            exposure = float(np.sum(cycle[core] ** 2 - shoulder_ms) * dt)
            within_score = np.abs(panel.time_s - float(centre)) <= core_half
            panel_rows.append(
                {
                    "cycle_id": f"{panel_name}_{index:02d}",
                    "panel": panel_name,
                    "cycle_index": index,
                    "observed_centre_utc": iso_utc(
                        panel.start_epoch_s + float(centre)
                    ),
                    "fitted_period_s": float(geometry.fitted_period_s),
                    "core_half_width_s": core_half,
                    "shoulder_inner_s": shoulder_inner,
                    "shoulder_outer_s": shoulder_outer,
                    "core_rms_pa": math.sqrt(max(core_ms, 0.0)),
                    "shoulder_rms_pa": math.sqrt(max(shoulder_ms, 0.0)),
                    "full_cycle_rms_pa": math.sqrt(max(full_ms, 0.0)),
                    "core_to_shoulder_mean_square_ratio": core_ms
                    / max(shoulder_ms, 1e-12),
                    "core_minus_shoulder_exposure_pa2_s": exposure,
                    "raw_local_energy_maximum": float(np.max(raw_score[within_score])),
                }
            )
        exposures = np.asarray(
            [row["core_minus_shoulder_exposure_pa2_s"] for row in panel_rows]
        )
        centre = float(np.median(exposures))
        mad = 1.4826 * float(np.median(np.abs(exposures - centre)))
        scale = max(mad, float(np.std(exposures, ddof=1)), 1e-12)
        q90, q95, q99 = np.quantile(exposures, [0.90, 0.95, 0.99])
        q25, q75 = np.quantile(exposures, [0.25, 0.75])
        upper_fence = float(q75 + 1.5 * (q75 - q25))
        for row in panel_rows:
            value = float(row["core_minus_shoulder_exposure_pa2_s"])
            row["panel_exposure_robust_z"] = (value - centre) / scale
            row["panel_empirical_upper_tail_fraction"] = empirical_upper_tail_fraction(
                exposures, value
            )
            row["in_panel_upper_10_percent"] = bool(value >= q90)
            row["in_panel_upper_5_percent"] = bool(value >= q95)
            row["in_panel_upper_1_percent"] = bool(value >= q99)
            row["above_panel_tukey_upper_fence"] = bool(value > upper_fence)
            row["status"] = (
                "RAW_AIRGUN_CYCLE_PRESSURE_SQUARED_EXPOSURE_"
                "PUBLICATION_TRACE_NOT_RECEIVED_ACOUSTIC_ENERGY"
            )
        summaries.append(
            {
                "population": f"panel_{panel_name}",
                "cycle_count": len(panel_rows),
                "fitted_period_s": float(geometry.fitted_period_s),
                "mean_exposure_pa2_s": float(np.mean(exposures)),
                "standard_deviation_exposure_pa2_s": float(
                    np.std(exposures, ddof=1)
                ),
                "median_exposure_pa2_s": centre,
                "mad_scale_exposure_pa2_s": mad,
                "q90_exposure_pa2_s": float(q90),
                "q95_exposure_pa2_s": float(q95),
                "q99_exposure_pa2_s": float(q99),
                "tukey_upper_fence_pa2_s": upper_fence,
                "count_upper_10_percent": int(
                    np.count_nonzero(exposures >= q90)
                ),
                "count_upper_5_percent": int(
                    np.count_nonzero(exposures >= q95)
                ),
                "count_upper_1_percent": int(
                    np.count_nonzero(exposures >= q99)
                ),
                "count_above_tukey_upper_fence": int(
                    np.count_nonzero(exposures > upper_fence)
                ),
                "count_robust_z_above_2p5": int(
                    np.count_nonzero((exposures - centre) / scale > 2.5)
                ),
                "mean_core_rms_pa": float(
                    np.mean([row["core_rms_pa"] for row in panel_rows])
                ),
                "mean_shoulder_rms_pa": float(
                    np.mean([row["shoulder_rms_pa"] for row in panel_rows])
                ),
                "status": "EMPIRICAL_CYCLE_DISTRIBUTION_NO_PARAMETRIC_TAIL_FIT",
            }
        )
        rows.extend(panel_rows)

    pooled_z = np.asarray([row["panel_exposure_robust_z"] for row in rows])
    summaries.append(
        {
            "population": "panels_d_e_pooled_after_panel_robust_standardisation",
            "cycle_count": len(rows),
            "fitted_period_s": float("nan"),
            "mean_exposure_pa2_s": float("nan"),
            "standard_deviation_exposure_pa2_s": float("nan"),
            "median_exposure_pa2_s": float("nan"),
            "mad_scale_exposure_pa2_s": float("nan"),
            "q90_exposure_pa2_s": float(np.quantile(pooled_z, 0.90)),
            "q95_exposure_pa2_s": float(np.quantile(pooled_z, 0.95)),
            "q99_exposure_pa2_s": float(np.quantile(pooled_z, 0.99)),
            "tukey_upper_fence_pa2_s": float("nan"),
            "count_upper_10_percent": int(
                np.count_nonzero(pooled_z >= np.quantile(pooled_z, 0.90))
            ),
            "count_upper_5_percent": int(
                np.count_nonzero(pooled_z >= np.quantile(pooled_z, 0.95))
            ),
            "count_upper_1_percent": int(
                np.count_nonzero(pooled_z >= np.quantile(pooled_z, 0.99))
            ),
            "count_above_tukey_upper_fence": int(
                sum(bool(row["above_panel_tukey_upper_fence"]) for row in rows)
            ),
            "count_robust_z_above_2p5": int(np.count_nonzero(pooled_z > 2.5)),
            "mean_core_rms_pa": float(
                np.mean([row["core_rms_pa"] for row in rows])
            ),
            "mean_shoulder_rms_pa": float(
                np.mean([row["shoulder_rms_pa"] for row in rows])
            ),
            "status": (
                "POOLED_PANEL_STANDARDISED_CONTROL_RAW_PA2_S_VALUES_"
                "ARE_NOT_POOLED"
            ),
        }
    )
    return rows, summaries


def h01_window_feature(
    h01: Series,
    half_width_s: float,
    dt: float,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, list[np.ndarray]]:
    width = max(3, int(round(2.0 * half_width_s / dt)) + 1)
    feature = maximum_filter1d(h01.values, size=width, mode="nearest")
    support = np.convolve(
        h01.valid.astype(int), np.ones(width, dtype=int), mode="same"
    )
    valid = h01.valid & (support >= width)
    midpoint = base.parse_utc("2014-03-08T00:47:00Z").timestamp()
    panel_indices = [
        np.flatnonzero(valid & (h01.time_epoch_s < midpoint)),
        np.flatnonzero(valid & (h01.time_epoch_s >= midpoint)),
    ]
    reference_parts = [
        feature[indices[::width]] for indices in panel_indices if indices.size
    ]
    reference = np.concatenate(reference_parts)
    return feature, valid, np.sort(reference), panel_indices


def upper_tail_from_sorted(reference: np.ndarray, values: np.ndarray) -> np.ndarray:
    insertion = np.searchsorted(reference, values, side="left")
    return (1.0 + reference.size - insertion) / (reference.size + 1.0)


def pulse_conditioned_scan(
    configuration: dict,
    cells: list[dict],
    distance_h01: np.ndarray,
    distance_h08: np.ndarray,
    pulse_rows: list[dict],
    h01: Series,
    dt: float,
) -> dict:
    settings = configuration["pulse_conditioned_acquisition"]
    central = float(configuration["central_celerity_km_s"])
    base_lag_s = (distance_h08 - distance_h01) / central
    base_steps, offset_steps, hypothesis_steps = acquisition_hypothesis_steps(
        base_lag_s, settings, dt
    )
    pulse_epoch = np.asarray(
        [
            base.parse_utc(row["observed_centre_utc"]).timestamp()
            for row in pulse_rows
        ]
    )
    h08_tail = np.asarray(
        [float(row["panel_empirical_upper_tail_fraction"]) for row in pulse_rows]
    )
    h01_feature, h01_valid, h01_reference, h01_panel_indices = h01_window_feature(
        h01, float(settings["h01_peak_half_width_s"]), dt
    )
    h01_epoch = pulse_epoch[:, None] - hypothesis_steps[None, :] * dt
    query_index = np.rint(
        (h01_epoch - h01.time_epoch_s[0]) / dt
    ).astype(np.int32)
    safe_index = np.clip(query_index, 0, h01.values.size - 1)
    query_valid = (
        (query_index >= 0)
        & (query_index < h01.values.size)
        & h01_valid[safe_index]
    )
    h01_values = h01_feature[safe_index]
    h01_tail = upper_tail_from_sorted(h01_reference, h01_values)

    cell_index_flat = np.repeat(np.arange(len(cells)), offset_steps.size)
    step_flat = (
        base_steps[:, None] + offset_steps[None, :]
    ).ravel()
    step_group = np.searchsorted(hypothesis_steps, step_flat)
    minimum_distance = np.full(hypothesis_steps.size, np.inf)
    maximum_distance = np.full(hypothesis_steps.size, -np.inf)
    np.minimum.at(
        minimum_distance, step_group, distance_h01[cell_index_flat]
    )
    np.maximum.at(
        maximum_distance, step_group, distance_h01[cell_index_flat]
    )
    source_start, source_end = (
        base.parse_utc(value).timestamp()
        for value in settings["source_time_control_utc"]
    )
    earliest_source = h01_epoch - maximum_distance[None, :] / central
    latest_source = h01_epoch - minimum_distance[None, :] / central
    source_valid = (
        (earliest_source <= source_end) & (latest_source >= source_start)
    )
    tail_selected = h08_tail <= float(settings["h08_tail_fraction"])
    valid = query_valid & source_valid & tail_selected[:, None]
    observed_score = -2.0 * (
        np.log(np.maximum(h08_tail[:, None], 1e-12))
        + np.log(np.maximum(h01_tail, 1e-12))
    )
    observed_score[~valid] = np.nan

    rng = np.random.default_rng(int(settings["random_seed"]))
    replicates = int(settings["null_replicates"])
    mark_null = np.empty(replicates)
    slide_null = np.empty(replicates)
    panel_groups = {
        panel: np.asarray(
            [index for index, row in enumerate(pulse_rows) if row["panel"] == panel]
        )
        for panel in ("d", "e")
    }
    for replicate in range(replicates):
        permuted = h08_tail.copy()
        for indices in panel_groups.values():
            permuted[indices] = rng.permutation(permuted[indices])
        permuted_valid = (
            query_valid
            & source_valid
            & (permuted <= float(settings["h08_tail_fraction"]))[:, None]
        )
        permuted_score = -2.0 * (
            np.log(np.maximum(permuted[:, None], 1e-12))
            + np.log(np.maximum(h01_tail, 1e-12))
        )
        mark_null[replicate] = float(np.nanmax(
            np.where(permuted_valid, permuted_score, np.nan)
        ))

        shifted_feature = h01_feature.copy()
        for indices in h01_panel_indices:
            minimum_shift = max(
                1,
                int(
                    round(
                        2.0 * float(settings["h01_peak_half_width_s"]) / dt
                    )
                ),
            )
            if indices.size <= 2 * minimum_shift:
                raise ValueError("H01W panel too short for circular time-slide null")
            shift = int(rng.integers(minimum_shift, indices.size - minimum_shift))
            shifted_feature[indices] = np.roll(h01_feature[indices], shift)
        shifted_values = shifted_feature[safe_index]
        shifted_tail = upper_tail_from_sorted(h01_reference, shifted_values)
        shifted_score = -2.0 * (
            np.log(np.maximum(h08_tail[:, None], 1e-12))
            + np.log(np.maximum(shifted_tail, 1e-12))
        )
        slide_null[replicate] = float(np.nanmax(
            np.where(valid, shifted_score, np.nan)
        ))

    finite_flat = np.flatnonzero(np.isfinite(observed_score.ravel()))
    if finite_flat.size == 0:
        raise ValueError("No pulse-conditioned candidates survive timing controls")
    retain_count = min(50000, finite_flat.size)
    finite_scores = observed_score.ravel()[finite_flat]
    retained = np.argpartition(finite_scores, -retain_count)[-retain_count:]
    ordered = finite_flat[retained[np.argsort(finite_scores[retained])[::-1]]]
    selected: list[tuple[int, int]] = []
    selected_h01_epoch: list[float] = []
    used_pulses: set[int] = set()
    separation = float(settings["independent_pair_separation_s"])
    for flat_index in ordered:
        pulse_index, lag_index = np.unravel_index(
            int(flat_index), observed_score.shape
        )
        arrival = float(h01_epoch[pulse_index, lag_index])
        if pulse_index in used_pulses:
            continue
        if any(abs(arrival - previous) <= separation for previous in selected_h01_epoch):
            continue
        selected.append((pulse_index, lag_index))
        selected_h01_epoch.append(arrival)
        used_pulses.add(pulse_index)
        if len(selected) >= int(settings["top_pair_count"]):
            break
    if len(selected) < int(settings["top_pair_count"]):
        raise ValueError("Too few independent pulse-conditioned candidates")

    density = np.asarray([float(row["densityPerKm2"]) for row in cells])
    probability_mass = np.asarray(
        [float(row["probabilityMass"]) for row in cells]
    )
    offset_step_set = set(map(int, offset_steps))
    rows: list[dict] = []
    for rank, (pulse_index, lag_index) in enumerate(selected, start=1):
        step = int(hypothesis_steps[lag_index])
        delta_steps = step - base_steps
        compatible = np.asarray(
            [int(value) in offset_step_set for value in delta_steps], dtype=bool
        )
        h01_arrival = float(h01_epoch[pulse_index, lag_index])
        source_epoch_by_cell = h01_arrival - distance_h01 / central
        source_compatible = compatible & (
            (source_epoch_by_cell >= source_start)
            & (source_epoch_by_cell <= source_end)
        )
        candidates = np.flatnonzero(source_compatible)
        if not candidates.size:
            raise ValueError("Selected pulse pair has no source-time-compatible cell")
        representative = int(
            candidates[
                np.lexsort(
                    (
                        np.abs(delta_steps[candidates]),
                        -density[candidates],
                    )
                )[0]
            ]
        )
        score = float(observed_score[pulse_index, lag_index])
        mark_p = float(
            (1 + np.count_nonzero(mark_null >= score)) / (replicates + 1)
        )
        slide_p = float(
            (1 + np.count_nonzero(slide_null >= score)) / (replicates + 1)
        )
        pulse = pulse_rows[pulse_index]
        rows.append(
            {
                "rank": rank,
                "joint_fisher_score": score,
                "pulse_mark_complete_scan_p": mark_p,
                "h01_time_slide_complete_scan_p": slide_p,
                "conservative_complete_scan_p": max(mark_p, slide_p),
                "h08_cycle_id": pulse["cycle_id"],
                "h08_panel": pulse["panel"],
                "h08_arrival_utc": pulse["observed_centre_utc"],
                "h08_core_rms_pa": pulse["core_rms_pa"],
                "h08_shoulder_rms_pa": pulse["shoulder_rms_pa"],
                "h08_core_minus_shoulder_exposure_pa2_s": pulse[
                    "core_minus_shoulder_exposure_pa2_s"
                ],
                "h08_panel_exposure_robust_z": pulse[
                    "panel_exposure_robust_z"
                ],
                "h08_empirical_upper_tail_fraction": float(
                    h08_tail[pulse_index]
                ),
                "h08_in_panel_upper_5_percent": pulse[
                    "in_panel_upper_5_percent"
                ],
                "h01_arrival_utc": iso_utc(h01_arrival),
                "h01_four_second_local_energy_maximum": float(
                    h01_values[pulse_index, lag_index]
                ),
                "h01_empirical_upper_tail_fraction": float(
                    h01_tail[pulse_index, lag_index]
                ),
                "total_interstation_lag_s": float(step * dt),
                "base_geometry_lag_s": float(base_lag_s[representative]),
                "fine_propagation_offset_s": float(
                    delta_steps[representative] * dt
                ),
                "primary_source_utc": iso_utc(
                    source_epoch_by_cell[representative]
                ),
                "representative_cell_id": cells[representative]["id"],
                "along_nm": float(cells[representative]["alongNm"]),
                "cross_nm": float(cells[representative]["crossNm"]),
                "latitude_deg": float(cells[representative]["latitude"]),
                "longitude_deg_e": float(cells[representative]["longitude"]),
                "representative_density_per_km2": float(density[representative]),
                "representative_in_current_pleiades_hpd50": str(
                    cells[representative]["in_hpd50"]
                ).lower() == "true",
                "representative_in_current_pleiades_hpd90": str(
                    cells[representative]["in_hpd90"]
                ).lower() == "true",
                "representative_in_current_pleiades_hpd95": str(
                    cells[representative]["in_hpd95"]
                ).lower() == "true",
                "compatible_source_time_cell_count": int(candidates.size),
                "compatible_pleiades_probability_mass": float(
                    np.sum(probability_mass[source_compatible])
                ),
                "status": (
                    "PULSE_CONDITIONED_PUBLICATION_TRACE_CANDIDATE_"
                    "NOT_EVENT_ASSOCIATION"
                ),
            }
        )
    return {
        "rows": rows,
        "observed_score": observed_score,
        "mark_null_maxima": mark_null,
        "slide_null_maxima": slide_null,
        "h01_feature": h01_feature,
        "h01_feature_valid": h01_valid,
        "h01_tail": h01_tail,
        "h01_epoch": h01_epoch,
        "pulse_epoch": pulse_epoch,
        "hypothesis_steps": hypothesis_steps,
    }

def correlation_at_lag(
    h01: Series,
    h08: Series,
    lag_steps: int,
    dt: float,
) -> tuple[float, int]:
    lag_s = lag_steps * dt
    h01_index = np.rint(
        (h08.time_epoch_s - lag_s - h01.time_epoch_s[0]) / dt
    ).astype(int)
    valid = (
        h08.valid
        & (h01_index >= 0)
        & (h01_index < h01.values.size)
    )
    source_index = h01_index[valid]
    receiver_index = np.flatnonzero(valid)
    retained = h01.valid[source_index]
    source_values = h01.values[source_index[retained]]
    receiver_values = h08.values[receiver_index[retained]]
    if source_values.size < 100:
        return float("nan"), int(source_values.size)
    return float(np.corrcoef(source_values, receiver_values)[0, 1]), int(source_values.size)


def load_cells(path: Path) -> list[dict]:
    with path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    rows.sort(key=lambda row: (int(row["alongIndex"]), int(row["crossIndex"])))
    if len(rows) != 5289:
        raise ValueError(f"Expected 5,289 source cells, found {len(rows)}")
    return rows


def source_distances(
    cells: list[dict],
    event_configuration: dict,
) -> tuple[np.ndarray, np.ndarray]:
    latitude = np.asarray([float(row["latitude"]) for row in cells])
    longitude = np.asarray([float(row["longitude"]) for row in cells])
    stations = event_configuration["stations"]
    radius = float(event_configuration["earth_radius_km"])
    h01 = stations["H01W"]
    h08 = stations["H08S"]
    distance_h01 = base.haversine_distance_km(
        latitude,
        longitude,
        (h01["latitude_deg"], h01["longitude_deg_e"]),
        radius,
    )
    distance_h08 = base.haversine_distance_km(
        latitude,
        longitude,
        (h08["latitude_deg"], h08["longitude_deg_e"]),
        radius,
    )
    return distance_h01, distance_h08


def score_cells(
    cells: list[dict],
    distance_h01: np.ndarray,
    distance_h08: np.ndarray,
    celerity_km_s: float,
    h01: Series,
    h08: Series,
    dt: float,
    cache: dict[int, tuple[float, int]],
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    lag_s = (distance_h08 - distance_h01) / celerity_km_s
    lag_steps = np.rint(lag_s / dt).astype(int)
    for step in np.unique(lag_steps):
        key = int(step)
        if key not in cache:
            cache[key] = correlation_at_lag(h01, h08, key, dt)
    correlation = np.asarray([cache[int(step)][0] for step in lag_steps])
    sample_count = np.asarray([cache[int(step)][1] for step in lag_steps])
    return lag_s, correlation, sample_count


def maxima_rows(
    configuration: dict,
    cells: list[dict],
    distance_h01: np.ndarray,
    distance_h08: np.ndarray,
    h01: Series,
    variants: dict[str, Series],
    dt: float,
) -> tuple[list[dict], dict[tuple[str, float], dict], dict[str, dict[int, tuple[float, int]]]]:
    rows = []
    maxima = {}
    caches = {variant: {} for variant in variants}
    arc_mask = np.asarray([math.isclose(float(row["crossNm"]), 0.0) for row in cells])
    for variant, h08 in variants.items():
        for celerity in map(float, configuration["celerity_sensitivity_km_s"]):
            lag_s, correlation, sample_count = score_cells(
                cells,
                distance_h01,
                distance_h08,
                celerity,
                h01,
                h08,
                dt,
                caches[variant],
            )
            for domain, eligible in (
                ("full_plus_minus_100nm_grid", np.ones(len(cells), dtype=bool)),
                ("seventh_arc_centreline", arc_mask),
            ):
                candidates = np.flatnonzero(eligible & np.isfinite(correlation))
                selected = int(candidates[np.argmax(correlation[candidates])])
                best = float(correlation[selected])
                near = int(np.count_nonzero(eligible & (correlation >= best - 0.001)))
                row = {
                    "variant": variant,
                    "celerity_km_s": f"{celerity:.2f}",
                    "domain": domain,
                    "maximum_correlation_r": f"{best:.9g}",
                    "representative_cell_id": cells[selected]["id"],
                    "along_nm": cells[selected]["alongNm"],
                    "cross_nm": cells[selected]["crossNm"],
                    "latitude_deg": cells[selected]["latitude"],
                    "longitude_deg_e": cells[selected]["longitude"],
                    "interstation_lag_s": f"{lag_s[selected]:.6f}",
                    "interstation_lag_min": f"{lag_s[selected] / 60.0:.6f}",
                    "paired_sample_count": int(sample_count[selected]),
                    "cells_within_0p001_of_maximum": near,
                    "point_status": (
                        "REPRESENTATIVE_GRID_CELL_ON_RANGE_DIFFERENCE_CORRELATION_SURFACE"
                    ),
                }
                rows.append(row)
                maxima[(variant, celerity, domain)] = {
                    "row": row,
                    "index": selected,
                    "lag_s": float(lag_s[selected]),
                    "correlation": correlation,
                    "sample_count": sample_count,
                }
    return rows, maxima, caches


def reference_targets(
    event_configuration: dict,
) -> list[dict]:
    with TARGET_PATH.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    stations = event_configuration["stations"]
    radius = float(event_configuration["earth_radius_km"])
    output = []
    for row in rows:
        latitude = float(row["latitude_deg"])
        longitude = float(row["longitude_deg_e"])
        distances = {}
        for station_id in ("H01W", "H08S"):
            station = stations[station_id]
            distances[station_id] = float(
                base.haversine_distance_km(
                    np.asarray(latitude),
                    np.asarray(longitude),
                    (station["latitude_deg"], station["longitude_deg_e"]),
                    radius,
                )
            )
        output.append({**row, "distances": distances})
    return output


def reference_rows(
    configuration: dict,
    targets: list[dict],
    h01: Series,
    variants: dict[str, Series],
    caches: dict[str, dict[int, tuple[float, int]]],
    dt: float,
) -> list[dict]:
    rows = []
    for target in targets:
        difference = target["distances"]["H08S"] - target["distances"]["H01W"]
        for celerity in map(float, configuration["celerity_sensitivity_km_s"]):
            lag_s = difference / celerity
            step = int(round(lag_s / dt))
            for variant, h08 in variants.items():
                if step not in caches[variant]:
                    caches[variant][step] = correlation_at_lag(h01, h08, step, dt)
                correlation, count = caches[variant][step]
                rows.append(
                    {
                        "target_id": target["target_id"],
                        "target_label": target["label"],
                        "target_status": target["status"],
                        "variant": variant,
                        "celerity_km_s": f"{celerity:.2f}",
                        "distance_h01w_km": f"{target['distances']['H01W']:.6f}",
                        "distance_h08s_km": f"{target['distances']['H08S']:.6f}",
                        "interstation_lag_min": f"{lag_s / 60.0:.6f}",
                        "correlation_r": f"{correlation:.9g}",
                        "paired_sample_count": count,
                        "status": "REFERENCE_POINT_CORRELATION_NOT_EVENT_ASSOCIATION",
                    }
                )
    return rows


def rolling_contributions(
    configuration: dict,
    h01: Series,
    h08: Series,
    lag_s: float,
    dt: float,
) -> list[dict]:
    h01_index = np.rint(
        (h08.time_epoch_s - lag_s - h01.time_epoch_s[0]) / dt
    ).astype(int)
    valid = h08.valid & (h01_index >= 0) & (h01_index < h01.values.size)
    safe_index = np.clip(h01_index, 0, h01.values.size - 1)
    valid &= h01.valid[safe_index]
    product = np.zeros(h08.values.size)
    product[valid] = h01.values[safe_index[valid]] * h08.values[valid]
    width = int(round(float(configuration["contribution_window_s"]) / dt))
    kernel = np.ones(max(2, width))
    numerator = np.convolve(product, kernel, mode="same")
    denominator = np.convolve(valid.astype(float), kernel, mode="same")
    rolling = np.divide(
        numerator,
        denominator,
        out=np.full_like(numerator, np.nan),
        where=denominator >= 0.75 * width,
    )
    eligible = np.flatnonzero(np.isfinite(rolling))
    ordered = eligible[np.argsort(rolling[eligible])[::-1]]
    separation = int(
        round(float(configuration["contribution_minimum_separation_s"]) / dt)
    )
    selected = []
    for index in ordered:
        if all(abs(int(index) - previous) > separation for previous in selected):
            selected.append(int(index))
        if len(selected) >= int(configuration["contribution_limit"]):
            break
    return [
        {
            "h08_index": index,
            "h01_index": int(safe_index[index]),
            "h01_arrival_utc": iso_utc(h01.time_epoch_s[safe_index[index]]),
            "h08_arrival_utc": iso_utc(h08.time_epoch_s[index]),
            "rolling_mean_standardised_product": float(rolling[index]),
            "pointwise_standardised_product": float(product[index]),
        }
        for index in selected
    ]


def direction_events(configuration: dict) -> list[dict]:
    events = [
        {
            **row,
            "arrival_epoch_s": base.parse_utc(row["arrival_utc"]).timestamp(),
            "bearing_deg": float(row["bearing_deg"]),
        }
        for row in configuration["source_reported_direction_events"]
    ]
    with TABLE_PATH.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            arrival_epoch_s = base.parse_utc(
                f"2014-03-08T{row['time_utc']}Z"
            ).timestamp()
            bearing_deg = float(row["bearing_deg"])
            duplicate = any(
                abs(event["arrival_epoch_s"] - arrival_epoch_s) <= 0.5
                and abs(event["bearing_deg"] - bearing_deg) <= 0.1
                for event in events
            )
            if not duplicate:
                events.append(
                    {
                        "id": row["event_id"],
                        "arrival_epoch_s": arrival_epoch_s,
                        "bearing_deg": bearing_deg,
                        "source": "Kadri 2024 Table 1",
                    }
                )
    return events


def match_direction_event(
    epoch_s: float,
    events: list[dict],
    tolerance_s: float,
) -> tuple[dict | None, float]:
    nearest = min(events, key=lambda row: abs(row["arrival_epoch_s"] - epoch_s))
    offset = epoch_s - nearest["arrival_epoch_s"]
    return (nearest if abs(offset) <= tolerance_s else None), float(offset)


def destination_point(
    origin: tuple[float, float],
    bearing_deg: float,
    distance_km: float,
    radius_km: float,
) -> tuple[float, float]:
    latitude, longitude = np.radians(origin)
    bearing = math.radians(bearing_deg)
    angular = distance_km / radius_km
    destination_latitude = math.asin(
        math.sin(latitude) * math.cos(angular)
        + math.cos(latitude) * math.sin(angular) * math.cos(bearing)
    )
    destination_longitude = longitude + math.atan2(
        math.sin(bearing) * math.sin(angular) * math.cos(latitude),
        math.cos(angular) - math.sin(latitude) * math.sin(destination_latitude),
    )
    return math.degrees(destination_latitude), math.degrees(destination_longitude) % 360.0


def bearing_intersections(
    configuration: dict,
    event_configuration: dict,
    contributions: list[dict],
    events: list[dict],
    lag_s: float,
) -> list[dict]:
    stations = event_configuration["stations"]
    radius = float(event_configuration["earth_radius_km"])
    origin = (
        float(stations["H01W"]["latitude_deg"]),
        float(stations["H01W"]["longitude_deg_e"]),
    )
    h08 = (
        float(stations["H08S"]["latitude_deg"]),
        float(stations["H08S"]["longitude_deg_e"]),
    )
    celerity = float(configuration["central_celerity_km_s"])
    target_difference = celerity * lag_s
    rows = []
    used_events = set()
    for contribution_rank, contribution in enumerate(contributions, start=1):
        h01_epoch = base.parse_utc(contribution["h01_arrival_utc"]).timestamp()
        event, offset = match_direction_event(
            h01_epoch,
            events,
            float(configuration["bearing_time_match_tolerance_s"]),
        )
        contribution["contribution_rank"] = contribution_rank
        contribution["matched_direction_event_id"] = "" if event is None else event["id"]
        contribution["matched_bearing_deg"] = "" if event is None else f"{event['bearing_deg']:.2f}"
        contribution["direction_event_offset_s"] = f"{offset:.3f}"
        if event is None or event["id"] in used_events:
            continue
        used_events.add(event["id"])

        def difference_error(distance_km: float) -> float:
            latitude, longitude = destination_point(
                origin, event["bearing_deg"], distance_km, radius
            )
            distance_h08 = float(
                base.haversine_distance_km(
                    np.asarray(latitude),
                    np.asarray(longitude),
                    h08,
                    radius,
                )
            )
            return distance_h08 - distance_km - target_difference

        grid = np.linspace(0.0, 10000.0, 1001)
        values = np.asarray([difference_error(value) for value in grid])
        roots = []
        for lower, upper, first, second in zip(
            grid[:-1], grid[1:], values[:-1], values[1:]
        ):
            if first == 0.0:
                roots.append(float(lower))
            elif first * second < 0.0:
                roots.append(
                    float(brentq(difference_error, float(lower), float(upper)))
                )
        if not roots:
            rows.append(
                {
                    "event_id": event["id"],
                    "h01_arrival_utc": contribution["h01_arrival_utc"],
                    "bearing_deg": f"{event['bearing_deg']:.2f}",
                    "correlation_lag_min": f"{lag_s / 60.0:.6f}",
                    "conditional_distance_from_h01w_km": "",
                    "conditional_latitude_deg": "",
                    "conditional_longitude_deg_e": "",
                    "contribution_rank": contribution_rank,
                    "source": event["source"],
                    "status": "NO_FORWARD_BEARING_INTERSECTION_WITH_CORRELATION_RANGE_DIFFERENCE",
                }
            )
            continue
        for root_index, distance in enumerate(roots, start=1):
            latitude, longitude = destination_point(
                origin, event["bearing_deg"], distance, radius
            )
            rows.append(
                {
                    "event_id": event["id"],
                    "h01_arrival_utc": contribution["h01_arrival_utc"],
                    "bearing_deg": f"{event['bearing_deg']:.2f}",
                    "correlation_lag_min": f"{lag_s / 60.0:.6f}",
                    "conditional_distance_from_h01w_km": f"{distance:.6f}",
                    "conditional_latitude_deg": f"{latitude:.9f}",
                    "conditional_longitude_deg_e": f"{longitude:.9f}",
                    "contribution_rank": contribution_rank,
                    "source": event["source"],
                    "status": (
                        "CONDITIONAL_BEARING_AND_CORRELATION_LAG_INTERSECTION_"
                        f"{root_index}_NOT_EVENT_ASSOCIATION"
                    ),
                }
            )

    control = configuration["kadri_preferred_distance_control"]
    latitude, longitude = destination_point(
        origin,
        float(control["bearing_deg"]),
        float(control["distance_from_h01w_km"]),
        radius,
    )
    distance_h08 = float(
        base.haversine_distance_km(
            np.asarray(latitude), np.asarray(longitude), h08, radius
        )
    )
    control_lag_s = (
        distance_h08 - float(control["distance_from_h01w_km"])
    ) / celerity
    rows.append(
        {
            "event_id": control["event_id"],
            "h01_arrival_utc": "2014-03-08T00:54:30.000Z",
            "bearing_deg": f"{float(control['bearing_deg']):.2f}",
            "correlation_lag_min": f"{control_lag_s / 60.0:.6f}",
            "conditional_distance_from_h01w_km": f"{float(control['distance_from_h01w_km']):.6f}",
            "conditional_latitude_deg": f"{latitude:.9f}",
            "conditional_longitude_deg_e": f"{longitude:.9f}",
            "contribution_rank": "",
            "source": control["source"],
            "status": "SOURCE_REPORTED_SEVENTH_ARC_DISTANCE_CONTROL_NOT_CORRELATION_INTERSECTION",
        }
    )
    return rows


def oscar_feature_audit(
    configuration: dict,
    targets: list[dict],
    traces: dict[str, base.Trace],
    results: dict[str, dict],
    screen: dict,
) -> list[dict]:
    target = next(row for row in targets if row["target_id"] == "oscar_v2_final_mode")
    central = float(configuration["central_celerity_km_s"])
    start = base.parse_utc("2014-03-08T00:29:20Z").timestamp()
    end = base.parse_utc("2014-03-08T00:30:10Z").timestamp()
    rows = []
    for panel_name in ("b", "c"):
        trace = traces[panel_name]
        travel = target["distances"]["H01W"] / central
        for index in trace.candidate_indices:
            source_epoch = trace.epoch_s[index] - travel
            if start <= source_epoch <= end:
                edge = min(
                    trace.epoch_s[index] - trace.epoch_s[0],
                    trace.epoch_s[-1] - trace.epoch_s[index],
                )
                rows.append(
                    {
                        "station": "H01W",
                        "panel": panel_name,
                        "arrival_utc": iso_utc(trace.epoch_s[index]),
                        "implied_source_utc": iso_utc(source_epoch),
                        "local_energy_score": f"{trace.score[index]:.9g}",
                        "within_dilated_airgun_mask": "",
                        "seconds_from_panel_edge": f"{edge:.3f}",
                        "valid_after_10s_edge_guard": bool(edge >= 10.0),
                        "status": "H01W_PUBLICATION_TRACE_CANDIDATE",
                    }
                )
    dt = float(screen["regular_grid_dt_s"])
    separation = int(round(float(screen["candidate_minimum_separation_s"]) / dt))
    for panel_name in ("d", "e"):
        result = results[panel_name]
        panel = result["panel"]
        score = result["rank_20"]["score"]
        peaks, _ = find_peaks(score, distance=separation)
        mask = aligned.observed_centre_mask(
            result,
            float(configuration["dilated_airgun_score_mask_half_width_s"]),
        )
        travel = target["distances"]["H08S"] / central
        for index in peaks:
            source_epoch = panel.epoch_s[index] - travel
            if start <= source_epoch <= end:
                edge = min(panel.time_s[index], panel.time_s[-1] - panel.time_s[index])
                rows.append(
                    {
                        "station": "H08S",
                        "panel": panel_name,
                        "arrival_utc": iso_utc(panel.epoch_s[index]),
                        "implied_source_utc": iso_utc(source_epoch),
                        "local_energy_score": f"{score[index]:.9g}",
                        "within_dilated_airgun_mask": bool(mask[index]),
                        "seconds_from_panel_edge": f"{edge:.3f}",
                        "valid_after_10s_edge_guard": bool(edge >= 10.0),
                        "status": "H08S_RANK20_PUBLICATION_TRACE_CANDIDATE",
                    }
                )
    rows.sort(key=lambda row: row["implied_source_utc"])
    return rows


def correlation_grid_rows(
    cells: list[dict],
    lag_s: np.ndarray,
    correlation_by_variant: dict[str, np.ndarray],
    sample_by_variant: dict[str, np.ndarray],
) -> list[dict]:
    rows = []
    for variant, correlation in correlation_by_variant.items():
        for index, cell in enumerate(cells):
            rows.append(
                {
                    "variant": variant,
                    "cell_id": cell["id"],
                    "along_nm": cell["alongNm"],
                    "cross_nm": cell["crossNm"],
                    "latitude_deg": cell["latitude"],
                    "longitude_deg_e": cell["longitude"],
                    "interstation_lag_min_at_1p50": f"{lag_s[index] / 60.0:.6f}",
                    "correlation_r": f"{correlation[index]:.9g}",
                    "paired_sample_count": int(sample_by_variant[variant][index]),
                    "status": "DESCRIPTIVE_PUBLICATION_TRACE_CORRELATION_NOT_LOCATION_LIKELIHOOD",
                }
            )
    return rows


def plot_lag_and_arc(
    configuration: dict,
    cells: list[dict],
    distance_h01: np.ndarray,
    distance_h08: np.ndarray,
    h01: Series,
    variants: dict[str, Series],
    caches: dict[str, dict[int, tuple[float, int]]],
    central_correlations: dict[str, np.ndarray],
    targets: list[dict],
    maxima: dict,
    dt: float,
) -> list[Path]:
    colours = {
        "no_airgun_suppression": "#111111",
        "rank8_unmasked": "#2166AC",
        "rank8_masked": "#67A9CF",
        "rank20_unmasked": "#B2182B",
        "rank20_masked": "#EF8A62",
    }
    labels = {
        "no_airgun_suppression": "no additional airgun suppression",
        "rank8_unmasked": "rank 8, unmasked",
        "rank8_masked": "rank 8, ±3 s score exclusion",
        "rank20_unmasked": "rank 20, unmasked",
        "rank20_masked": "rank 20, ±3 s score exclusion",
    }
    central = float(configuration["central_celerity_km_s"])
    lag = (distance_h08 - distance_h01) / central
    minimum_step = int(math.floor(np.min(lag) / dt))
    maximum_step = int(math.ceil(np.max(lag) / dt))
    plot_steps = np.arange(minimum_step, maximum_step + 1, 5)
    figure, axes = plt.subplots(2, 1, figsize=(15.8, 10.2))
    for variant, h08 in variants.items():
        for step in plot_steps:
            key = int(step)
            if key not in caches[variant]:
                caches[variant][key] = correlation_at_lag(h01, h08, key, dt)
        values = np.asarray([caches[variant][int(step)][0] for step in plot_steps])
        axes[0].plot(
            plot_steps * dt / 60.0,
            values,
            color=colours[variant],
            linewidth=1.45,
            label=labels[variant],
        )
    target_colours = {
        "integrated_pdf_mode": "#542788",
        "bran2016_mode": "#1B7837",
        "oscar_v2_final_mode": "#E08214",
        "bran_oscar_model_average_mode": "#5AAE61",
    }
    reference_handles = []
    for target in targets:
        lag_min = (
            target["distances"]["H08S"] - target["distances"]["H01W"]
        ) / central / 60.0
        axes[0].axvline(
            lag_min,
            color=target_colours[target["target_id"]],
            linestyle="--",
            linewidth=1.15,
        )
        reference_handles.append(
            Line2D(
                [0],
                [0],
                color=target_colours[target["target_id"]],
                linestyle="--",
                linewidth=1.15,
                label=target["label"].replace(" transport mode", ""),
            )
        )
    axes[0].set_xlabel("Implied H08S minus H01W arrival lag at 1.50 km s⁻¹ (min)")
    axes[0].set_ylabel("Pearson correlation r")
    axes[0].set_title("A. Correlation as a function of the only timing quantity identified by a source point")
    axes[0].grid(alpha=0.16)
    data_legend = axes[0].legend(loc="lower left", frameon=False, ncol=2)
    axes[0].add_artist(data_legend)
    axes[0].legend(
        handles=reference_handles,
        loc="upper right",
        frameon=False,
        fontsize=7.4,
        ncol=2,
        title="Reference-source lag",
        title_fontsize=7.7,
    )

    arc_indices = np.asarray(
        [
            index
            for index, row in enumerate(cells)
            if math.isclose(float(row["crossNm"]), 0.0)
        ]
    )
    along = np.asarray([float(cells[index]["alongNm"]) for index in arc_indices])
    for variant in variants:
        axes[1].plot(
            along,
            central_correlations[variant][arc_indices],
            color=colours[variant],
            linewidth=1.45,
            label=labels[variant],
        )
        best = maxima[
            (variant, central, "seventh_arc_centreline")
        ]["index"]
        axes[1].scatter(
            float(cells[best]["alongNm"]),
            central_correlations[variant][best],
            color=colours[variant],
            s=42,
            zorder=5,
        )
    axes[1].set_xlabel("Distance along the declared seventh-arc source grid from its northern end (NM)")
    axes[1].set_ylabel("Pearson correlation r")
    axes[1].set_title("B. Centreline scan: changing filter or pulse exclusion changes the selected arc position")
    axes[1].grid(alpha=0.16)
    figure.suptitle(
        "Cape Leeuwin–Diego Garcia local-energy correlation sensitivity",
        fontsize=15.6,
    )
    figure.text(
        0.5,
        0.014,
        "Scores are standardised separately within each publication panel and exclude ten-second panel edges. "
        "This is a descriptive lag scan, not a calibrated association statistic or location likelihood.",
        ha="center",
        fontsize=8.5,
    )
    figure.tight_layout(rect=[0.0, 0.045, 1.0, 0.96])
    return save_figure(figure, "two-station-correlation-lag-and-arc-scan")


def add_pdf_contours(axis: plt.Axes, spatial: dict) -> None:
    levels = [
        base.hpd_threshold(spatial["probability"], spatial["area"], probability)
        for probability in (0.95, 0.90, 0.50)
    ]
    contours = axis.contour(
        spatial["mesh_lon"],
        spatial["mesh_lat"],
        spatial["density"],
        levels=sorted(levels),
        colors=["#888888", "#555555", "#111111"],
        linewidths=[0.8, 1.0, 1.3],
        zorder=5,
    )
    axis.clabel(contours, inline=True, fontsize=7, fmt="integrated PDF")


def save_figure(figure: plt.Figure, basename: str) -> list[Path]:
    paths = []
    for suffix in ("png", "pdf"):
        path = OUTPUT / f"{basename}.{suffix}"
        figure.savefig(
            path,
            dpi=280 if suffix == "png" else None,
            metadata=PDF_METADATA if suffix == "pdf" else None,
        )
        paths.append(path)
    plt.close(figure)
    return paths


def plot_spatial_screen(
    configuration: dict,
    event_configuration: dict,
    cells: list[dict],
    central_correlations: dict[str, np.ndarray],
    maxima: dict,
    targets: list[dict],
    intersections: list[dict],
    spatial: dict,
) -> list[Path]:
    along_count = max(int(row["alongIndex"]) for row in cells) + 1
    cross_count = max(int(row["crossIndex"]) for row in cells) + 1
    latitude = np.asarray([float(row["latitude"]) for row in cells]).reshape(
        along_count, cross_count
    )
    longitude = np.asarray([float(row["longitude"]) for row in cells]).reshape(
        along_count, cross_count
    )
    arc = np.asarray(
        [
            (float(row["longitude"]), float(row["latitude"]))
            for row in cells
            if math.isclose(float(row["crossNm"]), 0.0)
        ]
    )
    central = float(configuration["central_celerity_km_s"])
    figure, axes = plt.subplots(1, 3, figsize=(19.0, 7.1))
    panels = [
        ("rank8_unmasked", "A. Primary rank-8 correlation (airgun-contaminated)"),
        ("rank20_masked", "B. Rank-20 with ±3 s score exclusion"),
    ]
    colour_handles = []
    for axis, (variant, title) in zip(axes[:2], panels):
        values = central_correlations[variant].reshape(along_count, cross_count)
        colour = axis.contourf(
            longitude,
            latitude,
            values,
            levels=20,
            cmap="RdBu_r",
            extend="both",
            alpha=0.92,
        )
        colour_handles.append(colour)
        axis.plot(arc[:, 0], arc[:, 1], color="black", linewidth=1.1)
        add_pdf_contours(axis, spatial)
        full = maxima[(variant, central, "full_plus_minus_100nm_grid")]["index"]
        centreline = maxima[(variant, central, "seventh_arc_centreline")]["index"]
        axis.scatter(
            float(cells[full]["longitude"]),
            float(cells[full]["latitude"]),
            marker="*",
            s=115,
            color="#FFD92F",
            edgecolor="black",
            linewidth=0.7,
            zorder=8,
            label="representative full-grid maximum",
        )
        axis.scatter(
            float(cells[centreline]["longitude"]),
            float(cells[centreline]["latitude"]),
            marker="o",
            s=50,
            facecolor="white",
            edgecolor="black",
            linewidth=1.0,
            zorder=8,
            label="seventh-arc maximum",
        )
        axis.set_xlim(85.0, 97.5)
        axis.set_ylim(-40.2, -30.5)
        axis.set_xlabel("Longitude (°E)")
        axis.set_ylabel("Latitude (°)")
        axis.set_title(title)
        axis.grid(alpha=0.12)
        axis.legend(loc="lower left", frameon=True, fontsize=7.3)
        figure.colorbar(colour, ax=axis, fraction=0.046, pad=0.03, label="Pearson r")

    wide = axes[2]
    wide.plot(arc[:, 0], arc[:, 1], color="#444444", linewidth=1.0, label="seventh arc")
    add_pdf_contours(wide, spatial)
    stations = event_configuration["stations"]
    origin = (
        float(stations["H01W"]["latitude_deg"]),
        float(stations["H01W"]["longitude_deg_e"]),
    )
    wide.scatter(origin[1], origin[0], marker="^", s=70, color="black", label="H01W")
    point_colours = {"figure9_rectangle_2": "#B2182B", "event_004941": "#2166AC"}
    for row in intersections:
        if not row["conditional_latitude_deg"]:
            continue
        latitude_value = float(row["conditional_latitude_deg"])
        longitude_value = float(row["conditional_longitude_deg_e"])
        distance = float(row["conditional_distance_from_h01w_km"])
        bearing = float(row["bearing_deg"])
        points = [
            destination_point(
                origin,
                bearing,
                value,
                float(event_configuration["earth_radius_km"]),
            )
            for value in np.linspace(0.0, distance, 160)
        ]
        colour = point_colours.get(row["event_id"], "#777777")
        linestyle = ":" if row["status"].startswith("SOURCE_REPORTED") else "-"
        wide.plot(
            [point[1] for point in points],
            [point[0] for point in points],
            color=colour,
            linestyle=linestyle,
            linewidth=1.2,
        )
        marker = "D" if row["status"].startswith("SOURCE_REPORTED") else "o"
        wide.scatter(
            longitude_value,
            latitude_value,
            marker=marker,
            s=55,
            color=colour,
            edgecolor="white",
            linewidth=0.6,
            zorder=8,
        )
        label = (
            f"{row['event_id']}\n{distance:.0f} km from H01W"
            + ("\nKadri arc-distance control" if row["status"].startswith("SOURCE_REPORTED") else "")
        )
        if row["status"].startswith("SOURCE_REPORTED"):
            annotation_offset = (7, -24)
        elif row["event_id"] == "figure9_rectangle_2":
            annotation_offset = (7, 8)
        else:
            annotation_offset = (5, 5)
        wide.annotate(
            label,
            (longitude_value, latitude_value),
            xytext=annotation_offset,
            textcoords="offset points",
            fontsize=7.1,
            color=colour,
        )
    for target in targets:
        wide.scatter(
            float(target["longitude_deg_e"]),
            float(target["latitude_deg"]),
            marker="x",
            s=38,
            linewidth=1.2,
            label=target["label"] if target["target_id"] == "integrated_pdf_mode" else None,
        )
    wide.set_xlim(82.0, 116.0)
    wide.set_ylim(-49.0, -20.0)
    wide.set_xlabel("Longitude (°E)")
    wide.set_ylabel("Latitude (°)")
    wide.set_title("C. Conditional bearing–lag intersections")
    wide.grid(alpha=0.12)
    wide.legend(loc="lower right", frameon=True, fontsize=7.1)
    figure.suptitle(
        "Two-station correlation geometry compared with the independent integrated PDF",
        fontsize=15.4,
    )
    figure.text(
        0.5,
        0.014,
        "A source cell changes only the H08S−H01W travel-time difference. Stripes are range-difference contours. "
        "Panel C assumes the correlation lag and the labelled H01W signal are the same event; the points are conditional intersections, not detections.",
        ha="center",
        fontsize=8.3,
    )
    figure.tight_layout(rect=[0.0, 0.045, 1.0, 0.95])
    return save_figure(figure, "two-station-correlation-spatial-screen")


def oscar_unfiltered_time_series(
    configuration: dict,
    target: dict,
    h01_energy: Series,
    h08_energy: Series,
    dt: float,
) -> dict:
    acquisition = configuration["unfiltered_acquisition"]
    central = float(configuration["central_celerity_km_s"])
    lag_s = (
        target["distances"]["H08S"] - target["distances"]["H01W"]
    ) / central
    lag_steps = int(round(lag_s / dt))
    safe, left, right, valid = aligned_pair_arrays(
        h01_energy,
        h08_energy,
        lag_steps,
        dt,
    )
    rolling_product, rolling_correlation = rolling_pair_series(
        left,
        right,
        valid,
        int(round(float(acquisition["local_product_window_s"]) / dt)),
        int(round(float(acquisition["local_correlation_window_s"]) / dt)),
    )
    source_epoch = (
        h01_energy.time_epoch_s[safe]
        - target["distances"]["H01W"] / central
    )
    source_start, source_end = (
        base.parse_utc(value).timestamp()
        for value in acquisition["source_time_control_utc"]
    )
    control = valid & (source_epoch >= source_start) & (source_epoch <= source_end)
    audit_start, audit_end = (
        base.parse_utc(value).timestamp()
        for value in acquisition["oscar_audit_window_utc"]
    )
    audit = control & (source_epoch >= audit_start) & (source_epoch <= audit_end)
    audit_indices = np.flatnonzero(audit)
    if audit_indices.size == 0:
        raise ValueError("OSCAR audit window has no valid paired samples")

    def maximum_index(values: np.ndarray) -> int:
        finite = audit_indices[np.isfinite(values[audit_indices])]
        return int(finite[np.argmax(values[finite])])

    h08_index = maximum_index(right)
    product_index = maximum_index(rolling_product)
    correlation_index = maximum_index(rolling_correlation)
    audit_end_index = int(audit_indices[-1])
    trailing_controls = []
    for width_s in acquisition["edge_trailing_windows_s"]:
        width_steps = int(round(float(width_s) / dt))
        trailing = trailing_pearson_series(
            left,
            right,
            valid,
            width_steps,
        )
        background = trailing[control & np.isfinite(trailing)]
        candidate_r = float(trailing[audit_end_index])
        trailing_controls.append(
            {
                "window_s": float(width_s),
                "window_end_source_utc": iso_utc(source_epoch[audit_end_index]),
                "pearson_r": candidate_r,
                "empirical_percentile_among_control_endpoints": float(
                    np.mean(background <= candidate_r)
                ),
                "empirical_exceedance_fraction": float(
                    np.mean(background >= candidate_r)
                ),
                "control_endpoint_count": int(background.size),
                "control_maximum_r": float(np.max(background)),
                "status": (
                    "POST_HOC_FULLY_SUPPORTED_TRAILING_WINDOW_CONTROL_"
                    "NOT_FALSE_ALARM_PROBABILITY"
                ),
            }
        )
    rows = []
    for index in np.flatnonzero(
        (source_epoch >= source_start) & (source_epoch <= source_end)
    ):
        rows.append(
            {
                "source_utc": iso_utc(source_epoch[index]),
                "h01_standardised_local_energy": float(left[index]) if valid[index] else "",
                "h08_standardised_local_energy_no_airgun_suppression": float(right[index]) if valid[index] else "",
                "rolling_4s_mean_standardised_product": float(rolling_product[index]) if np.isfinite(rolling_product[index]) else "",
                "rolling_20s_pearson_r": float(rolling_correlation[index]) if np.isfinite(rolling_correlation[index]) else "",
                "paired_sample_valid": bool(valid[index]),
            }
        )
    return {
        "rows": rows,
        "lag_s": float(lag_steps * dt),
        "source_epoch": source_epoch,
        "left": left,
        "right": right,
        "valid": valid,
        "rolling_product": rolling_product,
        "rolling_correlation": rolling_correlation,
        "control": control,
        "audit": audit,
        "audit_h08_maximum": {
            "source_utc": iso_utc(source_epoch[h08_index]),
            "h01_score": float(left[h08_index]),
            "h08_score": float(right[h08_index]),
        },
        "audit_product_maximum": {
            "source_utc": iso_utc(source_epoch[product_index]),
            "rolling_product": float(rolling_product[product_index]),
            "h01_score": float(left[product_index]),
            "h08_score": float(right[product_index]),
        },
        "audit_correlation_maximum": {
            "source_utc": iso_utc(source_epoch[correlation_index]),
            "rolling_pearson_r": float(rolling_correlation[correlation_index]),
        },
        "audit_last_supported_source_utc": iso_utc(source_epoch[audit_end_index]),
        "trailing_window_controls": trailing_controls,
    }


def plot_oscar_unfiltered_time_series(
    configuration: dict,
    diagnostic: dict,
) -> list[Path]:
    acquisition = configuration["unfiltered_acquisition"]
    control = diagnostic["control"]
    source = diagnostic["source_epoch"]
    dates = [datetime.fromtimestamp(float(value), timezone.utc) for value in source]
    figure, axes = plt.subplots(3, 1, figsize=(16.5, 10.8), sharex=True)
    axes[0].plot(dates, np.where(control, diagnostic["left"], np.nan), color="#35115A", linewidth=1.05)
    axes[0].set_title("A. Cape Leeuwin H01W publication-trace local energy")
    axes[1].plot(dates, np.where(control, diagnostic["right"], np.nan), color="#7F7F7F", linewidth=0.85)
    axes[1].set_title("B. Diego Garcia H08S publication-trace local energy — no additional airgun suppression")
    axes[2].plot(
        dates,
        np.where(control, diagnostic["rolling_correlation"], np.nan),
        color="#2166AC",
        linewidth=1.15,
        label="20 s rolling Pearson r",
    )
    edge_twenty = next(
        row
        for row in diagnostic["trailing_window_controls"]
        if math.isclose(float(row["window_s"]), 20.0)
    )
    axes[2].scatter(
        base.parse_utc(edge_twenty["window_end_source_utc"]),
        edge_twenty["pearson_r"],
        color="#E66101",
        s=30,
        label="fully supported trailing 20 s r",
    )
    product_axis = axes[2].twinx()
    product_axis.plot(
        dates,
        np.where(control, diagnostic["rolling_product"], np.nan),
        color="#B2182B",
        linewidth=0.85,
        alpha=0.72,
        label="4 s mean standardised product",
    )
    axes[2].set_title("C. Acquisition response through source time")
    product_axis.set_ylabel("Mean product", color="#B2182B")
    audit_start, audit_end = (base.parse_utc(value) for value in acquisition["oscar_audit_window_utc"])
    for axis in axes:
        axis.axvspan(audit_start, audit_end, color="#FEE8C8", alpha=0.42)
        axis.grid(alpha=0.15)
        axis.set_ylabel("Standardised score" if axis is not axes[2] else "Pearson r")
    product_time = base.parse_utc(diagnostic["audit_product_maximum"]["source_utc"])
    for axis in axes:
        axis.axvline(product_time, color="#B2182B", linestyle=":", linewidth=1.0)
    axes[2].xaxis.set_major_formatter(mdates.DateFormatter("%H:%M", tz=timezone.utc))
    axes[2].set_xlabel("Implied source UTC at the OSCAR v2 Final transport mode")
    axes[2].legend(loc="upper left", frameon=False)
    product_axis.legend(loc="upper right", frameon=False)
    figure.suptitle("OSCAR-conditioned unfiltered two-station acquisition time series", fontsize=15.2)
    figure.text(
        0.5,
        0.012,
        "Unfiltered means no additional low-rank airgun suppression: the inputs remain Kadri's already-filtered Figure 9 publication vectors. "
        "The orange interval was selected after visual inspection and is exploratory.",
        ha="center",
        fontsize=8.3,
    )
    figure.tight_layout(rect=[0.0, 0.045, 1.0, 0.95])
    return save_figure(figure, "unfiltered-oscar-acquisition-time-series")


def plot_acquisition_overview(
    configuration: dict,
    cells: list[dict],
    targets: list[dict],
    scan: dict,
    title: str,
    basename: str,
) -> list[Path]:
    response_rows = scan["response_rows"]
    lag_min = np.asarray([float(row["total_interstation_lag_min"]) for row in response_rows])
    energy = np.asarray([float(row["energy_correlation_r"]) for row in response_rows])
    pressure = np.asarray([float(row["pressure_correlation_r"]) for row in response_rows])
    null_maxima = scan["null_maxima"]
    top = scan["rows"]
    figure, axes = plt.subplots(2, 2, figsize=(17.0, 11.4))

    axes[0, 0].plot(lag_min, energy, color="#35115A", linewidth=0.9, label="local-energy response")
    axes[0, 0].plot(lag_min, pressure, color="#999999", linewidth=0.65, alpha=0.75, label="pressure response")
    for row in top:
        axes[0, 0].scatter(row["total_interstation_lag_s"] / 60.0, row["energy_correlation_r"], s=24, color="#B2182B", zorder=4)
        axes[0, 0].annotate(
            str(row["rank"]),
            (row["total_interstation_lag_s"] / 60.0, row["energy_correlation_r"]),
            xytext=(3, 3),
            textcoords="offset points",
            fontsize=7.3,
        )
    for target in targets:
        lag = (target["distances"]["H08S"] - target["distances"]["H01W"]) / float(configuration["central_celerity_km_s"]) / 60.0
        if target["target_id"] in {"oscar_v2_final_mode", "bran2016_mode"}:
            axes[0, 0].axvline(lag, linestyle=":", linewidth=0.9, label=target["label"])
    axes[0, 0].set_title("A. Acquisition response over geometry plus ±5 s fine lag")
    axes[0, 0].set_xlabel("H08S−H01W arrival lag (min)")
    axes[0, 0].set_ylabel("Full-overlap Pearson r")
    axes[0, 0].legend(loc="upper right", frameon=False, fontsize=7.3)
    axes[0, 0].grid(alpha=0.15)

    axes[0, 1].hist(energy, bins=55, density=True, color="#9ECAE1", alpha=0.75, label="observed lag response")
    axes[0, 1].hist(null_maxima, bins=28, density=True, color="#F4A582", alpha=0.68, label="IAAFT scan maxima")
    axes[0, 1].axvline(max(row["energy_correlation_r"] for row in top), color="#35115A", linewidth=1.4, label="observed scan maximum")
    axes[0, 1].set_title("B. Overall lag noise and trials-aware surrogate maxima")
    axes[0, 1].set_xlabel("Pearson r")
    axes[0, 1].set_ylabel("Density")
    axes[0, 1].legend(frameon=False, fontsize=7.5)
    axes[0, 1].grid(alpha=0.15)

    longitude = np.asarray([float(row["longitude"]) for row in cells])
    latitude = np.asarray([float(row["latitude"]) for row in cells])
    density = np.asarray([float(row["densityPerKm2"]) for row in cells])
    positive = density[density > 0.0]
    floor = float(np.quantile(positive, 0.05))
    colour = np.log10(np.maximum(density, floor))
    axes[1, 0].scatter(longitude, latitude, c=colour, cmap="Blues", s=7, linewidth=0, alpha=0.72, rasterized=True)
    for row in top:
        axes[1, 0].scatter(row["longitude_deg_e"], row["latitude_deg"], s=34, facecolor="none", edgecolor="#B2182B", linewidth=1.2)
        axes[1, 0].annotate(str(row["rank"]), (row["longitude_deg_e"], row["latitude_deg"]), xytext=(3, 3), textcoords="offset points", fontsize=7.3)
    axes[1, 0].set_title("C. Highest-density representative source cell for each lag peak")
    axes[1, 0].set_xlabel("Longitude (°E)")
    axes[1, 0].set_ylabel("Latitude (°)")
    axes[1, 0].grid(alpha=0.12)

    ranks = np.arange(1, len(top) + 1)
    width = 0.36
    axes[1, 1].bar(ranks - width / 2, [row["energy_correlation_r"] for row in top], width, color="#35115A", label="energy")
    axes[1, 1].bar(ranks + width / 2, [row["pressure_correlation_r"] for row in top], width, color="#BDBDBD", label="pressure")
    axes[1, 1].set_title("D. Top independent lag responses")
    axes[1, 1].set_xlabel("Acquisition rank")
    axes[1, 1].set_ylabel("Full-overlap Pearson r")
    axes[1, 1].set_xticks(ranks)
    axes[1, 1].legend(frameon=False)
    axes[1, 1].grid(axis="y", alpha=0.15)

    figure.suptitle(title, fontsize=15.2)
    figure.text(
        0.5,
        0.012,
        "A source cell supplies only a range-difference lag; the plotted cells are highest-density representatives of non-unique contours. "
        "Candidates are ranked by energy correlation, not by pressure or the illustrative pulse template.",
        ha="center",
        fontsize=8.3,
    )
    figure.tight_layout(rect=[0.0, 0.045, 1.0, 0.95])
    return save_figure(figure, basename)


def plot_acquisition_top_pairs(
    configuration: dict,
    scan: dict,
    acquisition_key: str,
    h08_label: str,
    title: str,
    basename: str,
) -> list[Path]:
    half_width_s = float(configuration[acquisition_key]["matched_display_half_width_s"])
    figure, axes = plt.subplots(len(scan["internals"]), 2, figsize=(18.0, 28.0), sharex=False, sharey=False)
    for row_index, internal in enumerate(scan["internals"]):
        row = internal["row"]
        candidate = int(internal["candidate_index"])
        relative_s = internal["source_epoch"] - internal["source_epoch"][candidate]
        within = internal["valid"] & (relative_s >= -half_width_s) & (relative_s <= half_width_s)
        h01_axis, h08_axis = axes[row_index]
        h01_axis.plot(relative_s[within], internal["left"][within], color="#35115A", linewidth=1.05)
        h08_axis.plot(relative_s[within], internal["right"][within], color="#7F7F7F", linewidth=1.0)
        for axis in (h01_axis, h08_axis):
            axis.axvline(0.0, color="#B2182B", linestyle=":", linewidth=0.9)
            axis.axvspan(-10.0, 10.0, color="#D9EAD3", alpha=0.20)
            axis.grid(alpha=0.13)
        periodic_relative = -float(row["seconds_from_nearest_periodic_centre"])
        if np.isfinite(periodic_relative):
            h08_axis.axvline(periodic_relative, color="#E66101", linestyle="--", linewidth=0.9)
        h01_axis.set_ylabel(f"#{row['rank']} score\nstandardised", fontsize=8.0)
        h01_axis.set_title(
            f"H01W — {row['primary_source_utc'][11:23]} source; local energy r={row['local_20s_energy_correlation_r']:.3f}",
            fontsize=8.3,
        )
        h08_axis.set_title(
            f"H08S {h08_label} — periodic Δ={row['seconds_from_nearest_periodic_centre']:+.2f} s; template mean={row['generic_template_mean_correlation']:.2f}",
            fontsize=8.3,
        )
        if row_index == len(scan["internals"]) - 1:
            h01_axis.set_xlabel("Seconds relative to selected source time")
            h08_axis.set_xlabel("Seconds relative to selected source time")
    figure.suptitle(title, fontsize=15.0)
    figure.text(
        0.5,
        0.008,
        "Ranking uses full-overlap local-energy correlation after scanning source geometry and ±5 s fine lag. "
        "Green shows the 20 s local-correlation window; orange marks the nearest fitted H08S periodic centre. "
        "The generic-template correlations are secondary and use the existing illustrative—not hydrodynamically predicted—pulse.",
        ha="center",
        fontsize=8.1,
    )
    figure.tight_layout(rect=[0.0, 0.025, 1.0, 0.975])
    return save_figure(figure, basename)


def plot_pulse_cycle_distribution(
    pulse_rows: list[dict],
    summaries: list[dict],
) -> list[Path]:
    figure, axes = plt.subplots(2, 2, figsize=(17.0, 10.8))
    colours = {"d": "#2166AC", "e": "#B2182B"}
    for panel_name in ("d", "e"):
        panel_rows = [row for row in pulse_rows if row["panel"] == panel_name]
        times = [
            base.parse_utc(row["observed_centre_utc"]) for row in panel_rows
        ]
        exposure = np.asarray(
            [
                float(row["core_minus_shoulder_exposure_pa2_s"])
                for row in panel_rows
            ]
        )
        summary = next(
            row for row in summaries if row["population"] == f"panel_{panel_name}"
        )
        axes[0, 0].plot(
            times,
            exposure,
            marker="o",
            markersize=2.8,
            linewidth=0.9,
            color=colours[panel_name],
            label=f"Figure 9{panel_name}",
        )
        axes[0, 0].hlines(
            float(summary["q95_exposure_pa2_s"]),
            times[0],
            times[-1],
            color=colours[panel_name],
            linestyle="--",
            linewidth=1.0,
        )
        axes[0, 1].hist(
            exposure,
            bins=16,
            alpha=0.55,
            color=colours[panel_name],
            label=f"Figure 9{panel_name}",
        )
        axes[1, 0].scatter(
            [row["shoulder_rms_pa"] for row in panel_rows],
            [row["core_rms_pa"] for row in panel_rows],
            s=[
                46 if row["in_panel_upper_5_percent"] else 18
                for row in panel_rows
            ],
            facecolor=[
                colours[panel_name]
                if row["in_panel_upper_5_percent"]
                else "none"
                for row in panel_rows
            ],
            edgecolor=colours[panel_name],
            linewidth=0.8,
            alpha=0.85,
            label=f"Figure 9{panel_name}",
        )
    axes[0, 0].set_title("A. Core-minus-shoulder exposure by fitted airgun cycle")
    axes[0, 0].set_ylabel("Pressure-squared exposure proxy (Pa² s)")
    axes[0, 0].xaxis.set_major_formatter(
        mdates.DateFormatter("%H:%M", tz=timezone.utc)
    )
    axes[0, 0].legend(frameon=False)
    axes[0, 0].grid(alpha=0.15)

    axes[0, 1].set_title("B. Empirical exposure distributions")
    axes[0, 1].set_xlabel("Core-minus-shoulder exposure proxy (Pa² s)")
    axes[0, 1].set_ylabel("Cycle count")
    axes[0, 1].legend(frameon=False)
    axes[0, 1].grid(alpha=0.15)

    maximum = max(
        max(float(row["core_rms_pa"]), float(row["shoulder_rms_pa"]))
        for row in pulse_rows
    )
    axes[1, 0].plot(
        [0.0, maximum], [0.0, maximum], color="#777777", linestyle=":"
    )
    axes[1, 0].set_title("C. Pulse-core RMS against local-cycle shoulders")
    axes[1, 0].set_xlabel("Shoulder RMS (Pa)")
    axes[1, 0].set_ylabel("Core RMS (Pa)")
    axes[1, 0].legend(frameon=False)
    axes[1, 0].grid(alpha=0.15)

    ordered = sorted(
        pulse_rows,
        key=lambda row: float(row["panel_exposure_robust_z"]),
        reverse=True,
    )
    ranks = np.arange(1, len(ordered) + 1)
    axes[1, 1].plot(
        ranks,
        [float(row["panel_exposure_robust_z"]) for row in ordered],
        color="#35115A",
        linewidth=1.2,
    )
    axes[1, 1].axhline(
        2.5,
        color="#B2182B",
        linestyle="--",
        linewidth=1.0,
        label="robust z = 2.5 screen",
    )
    for rank, row in enumerate(ordered[:8], start=1):
        axes[1, 1].annotate(
            f"{row['observed_centre_utc'][11:19]} ({row['panel']})",
            (rank, float(row["panel_exposure_robust_z"])),
            xytext=(3, 3),
            textcoords="offset points",
            fontsize=7.0,
        )
    axes[1, 1].set_title("D. Panel-standardised upper tail")
    axes[1, 1].set_xlabel("Cycle rank")
    axes[1, 1].set_ylabel("Robust exposure z-score")
    axes[1, 1].legend(frameon=False)
    axes[1, 1].grid(alpha=0.15)

    figure.suptitle(
        "Diego Garcia 9.9-second pulse population: core and shoulder controls",
        fontsize=15.2,
    )
    figure.text(
        0.5,
        0.012,
        "Each fitted cycle uses a ±2 s pulse core and the 2–4.5 s shoulders from the same cycle. "
        "Pa² s is a pressure-squared exposure proxy, not acoustic energy without impedance and calibrated raw receiver data. "
        "Dashed lines in A are within-panel 95th percentiles; filled points in C are those upper-tail cycles.",
        ha="center",
        fontsize=8.2,
    )
    figure.tight_layout(rect=[0.0, 0.045, 1.0, 0.95])
    return save_figure(figure, "airgun-cycle-energy-distribution")


def plot_pulse_conditioned_overview(
    configuration: dict,
    cells: list[dict],
    scan: dict,
    spatial: dict,
) -> list[Path]:
    rows = scan["rows"]
    figure, axes = plt.subplots(2, 2, figsize=(17.2, 11.0))
    observed_maximum = max(float(row["joint_fisher_score"]) for row in rows)
    axes[0, 0].hist(
        scan["mark_null_maxima"],
        bins=24,
        alpha=0.62,
        color="#9ECAE1",
        label="pulse-mark permutations",
    )
    axes[0, 0].hist(
        scan["slide_null_maxima"],
        bins=24,
        alpha=0.55,
        color="#F4A582",
        label="H01W time slides",
    )
    axes[0, 0].axvline(
        observed_maximum,
        color="#35115A",
        linewidth=1.5,
        label="observed complete-search maximum",
    )
    axes[0, 0].set_title("A. Complete-search empirical null maxima")
    axes[0, 0].set_xlabel("Joint Fisher tail score")
    axes[0, 0].set_ylabel("Replicate count")
    axes[0, 0].legend(frameon=False)
    axes[0, 0].grid(alpha=0.15)

    ranks = np.arange(1, len(rows) + 1)
    width = 0.36
    axes[0, 1].bar(
        ranks - width / 2,
        [-math.log10(max(float(row["h08_empirical_upper_tail_fraction"]), 1e-12)) for row in rows],
        width,
        color="#B2182B",
        label="H08S cycle tail",
    )
    axes[0, 1].bar(
        ranks + width / 2,
        [-math.log10(max(float(row["h01_empirical_upper_tail_fraction"]), 1e-12)) for row in rows],
        width,
        color="#2166AC",
        label="H01W predicted-time tail",
    )
    axes[0, 1].set_title("B. Components of the top-ten joint scores")
    axes[0, 1].set_xlabel("Pair rank")
    axes[0, 1].set_ylabel("−log₁₀ empirical upper-tail fraction")
    axes[0, 1].set_xticks(ranks)
    axes[0, 1].legend(frameon=False)
    axes[0, 1].grid(axis="y", alpha=0.15)

    longitude = np.asarray([float(row["longitude"]) for row in cells])
    latitude = np.asarray([float(row["latitude"]) for row in cells])
    density = np.asarray([float(row["densityPerKm2"]) for row in cells])
    positive = density[density > 0.0]
    floor = float(np.quantile(positive, 0.05))
    axes[1, 0].scatter(
        longitude,
        latitude,
        c=np.log10(np.maximum(density, floor)),
        cmap="Blues",
        s=7,
        linewidth=0,
        alpha=0.68,
        rasterized=True,
    )
    add_pdf_contours(axes[1, 0], spatial)
    for row in rows:
        axes[1, 0].scatter(
            row["longitude_deg_e"],
            row["latitude_deg"],
            s=38,
            facecolor="none",
            edgecolor="#B2182B",
            linewidth=1.2,
        )
        axes[1, 0].annotate(
            str(row["rank"]),
            (row["longitude_deg_e"], row["latitude_deg"]),
            xytext=(3, 3),
            textcoords="offset points",
            fontsize=7.2,
        )
    axes[1, 0].set_title(
        "C. Highest-density representative cells for non-unique lag contours"
    )
    axes[1, 0].set_xlabel("Longitude (°E)")
    axes[1, 0].set_ylabel("Latitude (°)")
    axes[1, 0].grid(alpha=0.12)

    axes[1, 1].bar(
        ranks,
        [float(row["conservative_complete_scan_p"]) for row in rows],
        color="#756BB1",
    )
    axes[1, 1].axhline(0.05, color="#B2182B", linestyle="--", linewidth=1.0)
    axes[1, 1].set_ylim(0.0, 1.0)
    axes[1, 1].set_title("D. Conservative trials-aware empirical p-values")
    axes[1, 1].set_xlabel("Pair rank")
    axes[1, 1].set_ylabel("Larger of pulse-mark and H01W time-slide p")
    axes[1, 1].set_xticks(ranks)
    axes[1, 1].grid(axis="y", alpha=0.15)

    figure.suptitle(
        "Pulse-conditioned H08S–H01W scan over the Pléiades-conditioned grid",
        fontsize=15.2,
    )
    figure.text(
        0.5,
        0.012,
        "Only the upper 10% of H08S fitted-cycle exposures enter the scan. "
        "The joint statistic combines empirical H08S and H01W upper-tail fractions; no chi-square approximation is used. "
        "Both nulls repeat the complete geometry, source-time and ±5 s timing search.",
        ha="center",
        fontsize=8.2,
    )
    figure.tight_layout(rect=[0.0, 0.045, 1.0, 0.95])
    return save_figure(figure, "pulse-conditioned-acquisition-overview")


def plot_pulse_conditioned_pairs(
    configuration: dict,
    scan: dict,
    h01: Series,
    h08_results: dict[str, dict],
) -> list[Path]:
    settings = configuration["pulse_conditioned_acquisition"]
    half = float(settings["matched_display_half_width_s"])
    core = float(settings["cycle_core_half_width_s"])
    shoulder_outer = float(settings["cycle_shoulder_outer_s"])
    figure, axes = plt.subplots(
        len(scan["rows"]), 2, figsize=(18.0, 28.0), sharex=False, sharey=False
    )
    for row_index, row in enumerate(scan["rows"]):
        h01_epoch = base.parse_utc(row["h01_arrival_utc"]).timestamp()
        h01_relative = h01.time_epoch_s - h01_epoch
        h01_visible = h01.valid & (np.abs(h01_relative) <= half)
        h01_axis, h08_axis = axes[row_index]
        h01_axis.plot(
            h01_relative[h01_visible],
            h01.values[h01_visible],
            color="#35115A",
            linewidth=1.0,
        )
        result = h08_results[row["h08_panel"]]
        h08_epoch = base.parse_utc(row["h08_arrival_utc"]).timestamp()
        h08_relative = result["panel"].epoch_s - h08_epoch
        h08_visible = np.abs(h08_relative) <= half
        h08_axis.plot(
            h08_relative[h08_visible],
            result["panel"].pressure_pa[h08_visible],
            color="#666666",
            linewidth=0.9,
        )
        for axis in (h01_axis, h08_axis):
            axis.axvline(0.0, color="#B2182B", linestyle=":", linewidth=0.9)
            axis.grid(alpha=0.13)
        h01_axis.axvspan(
            -float(settings["h01_peak_half_width_s"]),
            float(settings["h01_peak_half_width_s"]),
            color="#D9EAD3",
            alpha=0.28,
        )
        h08_axis.axvspan(-core, core, color="#FEE8C8", alpha=0.34)
        h08_axis.axvspan(
            -shoulder_outer, -core, color="#D9D9D9", alpha=0.18
        )
        h08_axis.axvspan(
            core, shoulder_outer, color="#D9D9D9", alpha=0.18
        )
        h01_axis.set_ylabel(f"#{row['rank']} score\nstandardised", fontsize=8.0)
        h01_axis.set_title(
            f"H01W {row['h01_arrival_utc'][11:23]} — tail={row['h01_empirical_upper_tail_fraction']:.3f}",
            fontsize=8.3,
        )
        h08_axis.set_title(
            f"H08S {row['h08_arrival_utc'][11:23]} cycle {row['h08_cycle_id']} — tail={row['h08_empirical_upper_tail_fraction']:.3f}; z={row['h08_panel_exposure_robust_z']:.2f}",
            fontsize=8.3,
        )
        if row_index == len(scan["rows"]) - 1:
            h01_axis.set_xlabel("Seconds from predicted H01W arrival")
            h08_axis.set_xlabel("Seconds from fitted H08S pulse centre")
    figure.suptitle(
        "Top ten pulse-conditioned candidates — predicted H01W and observed H08S windows",
        fontsize=15.0,
    )
    figure.text(
        0.5,
        0.008,
        "Green marks the four-second H01W peak window. Orange marks the H08S ±2 s core and grey the 2–4.5 s shoulders. "
        "Each row is a different H08S cycle and a source-time-compatible lag; visual similarity did not select the ranking.",
        ha="center",
        fontsize=8.1,
    )
    figure.tight_layout(rect=[0.0, 0.025, 1.0, 0.975])
    return save_figure(figure, "pulse-conditioned-top10-matched-pairs")



def main() -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    configuration = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    event_configuration = json.loads(EVENT_CONFIG_PATH.read_text(encoding="utf-8"))

    filter_configuration = json.loads(FILTER_CONFIG_PATH.read_text(encoding="utf-8"))
    source_path = (HERE / configuration["source_grid"]["path"]).resolve()
    if sha256(source_path) != configuration["source_grid"]["sha256"]:
        raise ValueError("Pinned source grid hash does not match")

    traces = base.load_traces(event_configuration)
    screen = event_configuration["trace_screen"]
    dt = float(screen["regular_grid_dt_s"])
    filter_configuration = copy.deepcopy(filter_configuration)
    filter_configuration["low_rank_values"] = [8, 20]
    h08_results = {
        name: aligned.analyse_h08_all_methods(
            name, event_utc, filter_configuration, screen
        )
        for name, event_utc in {
            "d": "2014-03-08T01:03:13.150Z",
            "e": "2014-03-08T01:12:49.500Z",
        }.items()
    }
    h01 = build_h01_series(
        traces, float(configuration["panel_edge_guard_s"]), dt
    )
    variants = {
        row["id"]: build_h08_series(
            h08_results,
            None if row["rank"] is None else int(row["rank"]),
            bool(row["mask_airgun"]),
            float(configuration["dilated_airgun_score_mask_half_width_s"]),
            float(configuration["panel_edge_guard_s"]),
            dt,
            screen,
        )
        for row in configuration["correlation_variants"]
    }

    cells = load_cells(source_path)
    distance_h01, distance_h08 = source_distances(cells, event_configuration)
    maximum_rows, maxima, caches = maxima_rows(
        configuration,
        cells,
        distance_h01,
        distance_h08,
        h01,
        variants,
        dt,
    )
    maximum_path = OUTPUT / "two-station-correlation-maxima.csv"
    write_csv(maximum_path, maximum_rows)

    central = float(configuration["central_celerity_km_s"])
    central_lag = (distance_h08 - distance_h01) / central
    central_correlations = {}
    central_samples = {}
    for variant, h08 in variants.items():
        _, correlation, count = score_cells(
            cells,
            distance_h01,
            distance_h08,
            central,
            h01,
            h08,
            dt,
            caches[variant],
        )
        central_correlations[variant] = correlation
        central_samples[variant] = count
    grid_path = OUTPUT / "two-station-correlation-source-grid.csv"
    write_csv(
        grid_path,
        correlation_grid_rows(
            cells, central_lag, central_correlations, central_samples
        ),
    )

    targets = reference_targets(event_configuration)
    reference_path = OUTPUT / "reference-source-correlations.csv"
    write_csv(
        reference_path,
        reference_rows(
            configuration, targets, h01, variants, caches, dt
        ),
    )

    guard_s = float(configuration["panel_edge_guard_s"])
    h01_pressure = build_trace_field_series(
        traces,
        ("b", "c"),
        "pressure",
        guard_s,
        dt,
    )
    h08_pressure = build_trace_field_series(
        traces,
        ("d", "e"),
        "pressure",
        guard_s,
        dt,
    )
    acquisition_scan = unfiltered_acquisition_scan(
        configuration,
        event_configuration,
        cells,
        distance_h01,
        distance_h08,
        traces,
        h08_results,
        h01,
        variants[configuration["unfiltered_acquisition"]["variant"]],
        h01_pressure,
        h08_pressure,
        dt,
    )
    acquisition_top_path = OUTPUT / "unfiltered-acquisition-top10.csv"
    write_csv(acquisition_top_path, acquisition_scan["rows"])
    acquisition_response_path = OUTPUT / "unfiltered-acquisition-lag-response.csv"
    write_csv(acquisition_response_path, acquisition_scan["response_rows"])
    acquisition_null_path = OUTPUT / "unfiltered-acquisition-iaaft-null-maxima.csv"
    write_csv(
        acquisition_null_path,
        [
            {
                "replicate": index + 1,
                "maximum_energy_correlation_r": float(value),
                "panel_d_relative_spectral_error": float(
                    acquisition_scan["spectral_errors"][index, 0]
                ),
                "panel_e_relative_spectral_error": float(
                    acquisition_scan["spectral_errors"][index, 1]
                ),
            }
            for index, value in enumerate(acquisition_scan["null_maxima"])
        ],
    )

    filtered_scan = unfiltered_acquisition_scan(
        configuration,
        event_configuration,
        cells,
        distance_h01,
        distance_h08,
        traces,
        h08_results,
        h01,
        variants[configuration["filtered_acquisition"]["variant"]],
        h01_pressure,
        h08_pressure,
        dt,
        acquisition_key="filtered_acquisition",
        null_mode="score_series",
    )
    filtered_top_path = OUTPUT / "filtered-acquisition-top10.csv"
    filtered_response_path = OUTPUT / "filtered-acquisition-lag-response.csv"
    filtered_null_path = OUTPUT / "filtered-acquisition-iaaft-null-maxima.csv"
    write_csv(filtered_top_path, filtered_scan["rows"])
    write_csv(filtered_response_path, filtered_scan["response_rows"])
    write_csv(
        filtered_null_path,
        [
            {
                "replicate": index + 1,
                "maximum_energy_correlation_r": float(value),
                "panel_d_relative_spectral_error": float(
                    filtered_scan["spectral_errors"][index, 0]
                ),
                "panel_e_relative_spectral_error": float(
                    filtered_scan["spectral_errors"][index, 1]
                ),
            }
            for index, value in enumerate(filtered_scan["null_maxima"])
        ],
    )

    pulse_rows, pulse_summaries = pulse_cycle_distribution(
        h08_results, screen, configuration, dt
    )
    pulse_rows_path = OUTPUT / "airgun-cycle-energy-population.csv"
    pulse_summary_path = OUTPUT / "airgun-cycle-energy-summary.csv"
    write_csv(pulse_rows_path, pulse_rows)
    write_csv(pulse_summary_path, pulse_summaries)
    pulse_scan = pulse_conditioned_scan(
        configuration,
        cells,
        distance_h01,
        distance_h08,
        pulse_rows,
        h01,
        dt,
    )
    pulse_top_path = OUTPUT / "pulse-conditioned-acquisition-top10.csv"
    pulse_null_path = OUTPUT / "pulse-conditioned-complete-scan-nulls.csv"
    write_csv(pulse_top_path, pulse_scan["rows"])
    write_csv(
        pulse_null_path,
        [
            {
                "replicate": index + 1,
                "pulse_mark_permutation_maximum_joint_score": float(
                    pulse_scan["mark_null_maxima"][index]
                ),
                "h01_time_slide_maximum_joint_score": float(
                    pulse_scan["slide_null_maxima"][index]
                ),
            }
            for index in range(
                pulse_scan["mark_null_maxima"].size
            )
        ],
    )


    oscar_target = next(
        target for target in targets if target["target_id"] == "oscar_v2_final_mode"
    )
    oscar_unfiltered = oscar_unfiltered_time_series(
        configuration,
        oscar_target,
        h01,
        variants[configuration["unfiltered_acquisition"]["variant"]],
        dt,
    )
    audit_source_epoch = base.parse_utc(
        oscar_unfiltered["audit_h08_maximum"]["source_utc"]
    ).timestamp()
    audit_h08_epoch = (
        audit_source_epoch
        + oscar_target["distances"]["H08S"]
        / float(configuration["central_celerity_km_s"])
    )
    oscar_unfiltered["audit_h08_periodic_context"] = nearest_periodic_context(
        audit_h08_epoch,
        h08_results,
        screen,
    )
    oscar_time_series_path = OUTPUT / "unfiltered-oscar-acquisition-time-series.csv"
    write_csv(oscar_time_series_path, oscar_unfiltered["rows"])
    oscar_edge_control_path = (
        OUTPUT / "unfiltered-oscar-edge-window-controls.csv"
    )
    write_csv(oscar_edge_control_path, oscar_unfiltered["trailing_window_controls"])


    primary = configuration["primary_variant"]
    primary_maximum = maxima[
        (primary, central, "full_plus_minus_100nm_grid")
    ]
    contributions = rolling_contributions(
        configuration,
        h01,
        variants[primary],
        primary_maximum["lag_s"],
        dt,
    )
    events = direction_events(configuration)
    intersections = bearing_intersections(
        configuration,
        event_configuration,
        contributions,
        events,
        primary_maximum["lag_s"],
    )
    contribution_path = OUTPUT / "correlation-driving-windows.csv"
    write_csv(contribution_path, contributions)
    intersection_path = OUTPUT / "conditional-bearing-intersections.csv"
    write_csv(intersection_path, intersections)

    oscar_rows = oscar_feature_audit(
        configuration, targets, traces, h08_results, screen
    )
    oscar_path = OUTPUT / "oscar-near-0030-feature-audit.csv"
    write_csv(oscar_path, oscar_rows)

    spatial = base.load_spatial(event_configuration)
    paths: list[Path] = [
        maximum_path,
        grid_path,
        reference_path,
        contribution_path,
        intersection_path,
        oscar_path,
        oscar_edge_control_path,
        acquisition_top_path,
        acquisition_response_path,
        acquisition_null_path,
        oscar_time_series_path,
        filtered_top_path,
        filtered_response_path,
        filtered_null_path,
        pulse_rows_path,
        pulse_summary_path,
        pulse_top_path,
        pulse_null_path,
    ]
    paths.extend(
        plot_lag_and_arc(
            configuration,
            cells,
            distance_h01,
            distance_h08,
            h01,
            variants,
            caches,
            central_correlations,
            targets,
            maxima,
            dt,
        )
    )
    paths.extend(
        plot_spatial_screen(
            configuration,
            event_configuration,
            cells,
            central_correlations,
            maxima,
            targets,
            intersections,
            spatial,
        )
    )
    paths.extend(
        plot_oscar_unfiltered_time_series(configuration, oscar_unfiltered)
    )
    paths.extend(
        plot_acquisition_overview(
            configuration,
            cells,
            targets,
            acquisition_scan,
            "Unfiltered publication-trace acquisition scan over the Pléiades-conditioned source grid",
            "unfiltered-acquisition-response-overview",
        )
    )
    paths.extend(
        plot_acquisition_top_pairs(
            configuration,
            acquisition_scan,
            "unfiltered_acquisition",
            "without additional suppression",
            "Top ten independent unfiltered acquisition responses — matched station pairs",
            "unfiltered-acquisition-top10-matched-pairs",
        )
    )
    paths.extend(
        plot_acquisition_overview(
            configuration,
            cells,
            targets,
            filtered_scan,
            "Held-out-selected airgun-filter acquisition scan over the Pléiades-conditioned source grid",
            "filtered-acquisition-response-overview",
        )
    )
    paths.extend(
        plot_acquisition_top_pairs(
            configuration,
            filtered_scan,
            "filtered_acquisition",
            "after held-out-selected rank-8 suppression",
            "Top ten held-out-filtered acquisition responses — matched station pairs",
            "filtered-acquisition-top10-matched-pairs",
        )
    )
    paths.extend(plot_pulse_cycle_distribution(pulse_rows, pulse_summaries))
    paths.extend(
        plot_pulse_conditioned_overview(configuration, cells, pulse_scan, spatial)
    )
    paths.extend(
        plot_pulse_conditioned_pairs(configuration, pulse_scan, h01, h08_results)
    )

    oscar_h01 = next(
        row
        for row in oscar_rows
        if row["arrival_utc"] == "2014-03-08T00:52:04.350Z"
    )
    oscar_h08 = next(
        row
        for row in oscar_rows
        if row["arrival_utc"] == "2014-03-08T01:10:00.500Z"
    )
    summary = {
        "status": "EXPLORATORY_PUBLICATION_TRACE_CORRELATION_NOT_EVENT_ASSOCIATION_OR_LOCATION_LIKELIHOOD",
        "oscar_near_0030_visual_pair": {
            "h01w": oscar_h01,
            "h08s": oscar_h08,
            "source_time_offset_s": (
                base.parse_utc(oscar_h08["implied_source_utc"]).timestamp()
                - base.parse_utc(oscar_h01["implied_source_utc"]).timestamp()
            ),
            "conclusion": (
                "The H08S feature is only 0.5 s inside Figure 9e and fails the "
                "declared 10 s panel-edge guard, so it is not admitted to the "
                "main correlation scan. The separate boundary-aware audit treats "
                "the feature as worthy of raw-data follow-up but finds no "
                "significant association in matched publication-trace controls."
            ),
        },
        "reference_lags_at_1p50_km_s": {
            target["target_id"]: (
                target["distances"]["H08S"] - target["distances"]["H01W"]
            )
            / central
            / 60.0
            for target in targets
        },
        "maxima": maximum_rows,
        "primary_driving_windows": contributions,
        "conditional_bearing_intersections": intersections,
        "unfiltered_acquisition": {
            "definition": configuration["unfiltered_acquisition"],
            "search_unique_lag_hypotheses": len(acquisition_scan["response_rows"]),
            "fine_offset_value_count": int(acquisition_scan["offset_steps"].size),
            "observed_scan_maximum_r": float(
                acquisition_scan["rows"][0]["energy_correlation_r"]
            ),
            "observed_scan_maximum_iaaft_p": float(
                acquisition_scan["rows"][0]["iaaft_scan_max_p"]
            ),
            "iaaft_null_maximum_q90": float(
                np.quantile(acquisition_scan["null_maxima"], 0.90)
            ),
            "iaaft_null_maximum_q95": float(
                np.quantile(acquisition_scan["null_maxima"], 0.95)
            ),
            "iaaft_null_maximum_q99": float(
                np.quantile(acquisition_scan["null_maxima"], 0.99)
            ),
            "iaaft_relative_spectral_error_median": {
                "panel_d": float(
                    np.median(acquisition_scan["spectral_errors"][:, 0])
                ),
                "panel_e": float(
                    np.median(acquisition_scan["spectral_errors"][:, 1])
                ),
            },
            "top_ten_independent_lag_responses": acquisition_scan["rows"],
            "oscar_0034_visual_audit": {
                "h08_maximum": oscar_unfiltered["audit_h08_maximum"],
                "product_maximum": oscar_unfiltered["audit_product_maximum"],
                "correlation_maximum": oscar_unfiltered["audit_correlation_maximum"],
                "h08_periodic_context": oscar_unfiltered[
                    "audit_h08_periodic_context"
                ],
                "last_supported_source_utc": oscar_unfiltered[
                    "audit_last_supported_source_utc"
                ],
                "trailing_window_controls": oscar_unfiltered["trailing_window_controls"],
                "selection_warning": (
                    "The 00:34–00:35 source-time interval was selected after "
                    "visual inspection and the H01W trace terminates inside it."
                ),
            },
            "interpretation": [
                "no airgun suppression means no additional filtering beyond Kadri's already-filtered publication trace",
                "energy correlation is primary because long-range propagation need not preserve pressure phase",
                "the generic pulse-template scores are secondary diagnostics and did not select candidates",
                "a source cell supplies only a range-difference lag; representative points are not unique locations",
                "IAAFT scan-maximum p-values control the complete geometry-plus-offset lag search under a stationary publication-trace surrogate null",
            ],
        },
        "filtered_acquisition": {
            "definition": configuration["filtered_acquisition"],
            "search_unique_lag_hypotheses": len(filtered_scan["response_rows"]),
            "observed_scan_maximum_r": float(
                filtered_scan["rows"][0]["energy_correlation_r"]
            ),
            "observed_scan_maximum_iaaft_p": float(
                filtered_scan["rows"][0]["iaaft_scan_max_p"]
            ),
            "iaaft_null_maximum_q90": float(
                np.quantile(filtered_scan["null_maxima"], 0.90)
            ),
            "iaaft_null_maximum_q95": float(
                np.quantile(filtered_scan["null_maxima"], 0.95)
            ),
            "iaaft_null_maximum_q99": float(
                np.quantile(filtered_scan["null_maxima"], 0.99)
            ),
            "top_ten_independent_lag_responses": filtered_scan["rows"],
            "interpretation": [
                "rank 8 is the pre-existing held-out-selected compromise, not the numerically strongest possible subtraction",
                "the filtered-score IAAFT null repeats the complete geometry-plus-offset lag search",
                "a low-rank filter can attenuate a real signal that overlaps the learned airgun subspace",
            ],
        },
        "pulse_conditioned_acquisition": {
            "definition": configuration["pulse_conditioned_acquisition"],
            "cycle_population_summaries": pulse_summaries,
            "upper_five_percent_cycles": [
                row for row in pulse_rows if row["in_panel_upper_5_percent"]
            ],
            "observed_complete_search_maximum_joint_score": float(
                pulse_scan["rows"][0]["joint_fisher_score"]
            ),
            "observed_pulse_mark_complete_scan_p": float(
                pulse_scan["rows"][0]["pulse_mark_complete_scan_p"]
            ),
            "observed_h01_time_slide_complete_scan_p": float(
                pulse_scan["rows"][0]["h01_time_slide_complete_scan_p"]
            ),
            "observed_conservative_complete_scan_p": float(
                pulse_scan["rows"][0]["conservative_complete_scan_p"]
            ),
            "pulse_mark_null_maximum_q95": float(
                np.quantile(pulse_scan["mark_null_maxima"], 0.95)
            ),
            "h01_time_slide_null_maximum_q95": float(
                np.quantile(pulse_scan["slide_null_maxima"], 0.95)
            ),
            "top_ten_independent_pairs": pulse_scan["rows"],
            "interpretation": [
                "the cycle statistic compares each pulse core with shoulders from the same approximately 9.9-second cycle",
                "Pa squared seconds is a pressure-squared exposure proxy rather than received acoustic energy",
                "the empirical tail screen and both complete-search nulls avoid a Gaussian tail assumption",
                "representative source cells are points on non-unique range-difference contours",
            ],
        },

        "limits": [
            "inputs are already-filtered publication-figure vectors rather than raw CTBTO channels",
            "source geometry identifies only interstation distance difference, so a correlation maximum is a contour rather than a unique point",
            "the primary rank-8 maximum is dominated by alignments with residual periodic airgun peaks",
            "maxima move materially under filter rank, pulse exclusion and celerity controls",
            "correlations are descriptive and have not been calibrated as association probabilities or spatial likelihoods",
            "the no-suppression variant removes none of our periodic model but remains an already-filtered single publication trace",
            "geometry and fine timing offset are partially degenerate because both change only the interstation lag",
            "the simulated pulse shape is illustrative and cannot serve as a validated 777 matched-filter template",
        ],
    }
    summary_path = OUTPUT / "two-station-correlation-summary.json"
    summary_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    paths.append(summary_path)

    manifest = {
        "status": "REPRODUCIBLE_OUTPUT_HASHES",
        "inputs": {
            str(CONFIG_PATH.relative_to(HERE)): sha256(CONFIG_PATH),
            str(EVENT_CONFIG_PATH.relative_to(HERE)): sha256(EVENT_CONFIG_PATH),
            str(FILTER_CONFIG_PATH.relative_to(HERE)): sha256(FILTER_CONFIG_PATH),
            str(TARGET_PATH.relative_to(HERE)): sha256(TARGET_PATH),
            str(TABLE_PATH.relative_to(HERE)): sha256(TABLE_PATH),
            str(base.GRID_PATH.relative_to(HERE)): sha256(base.GRID_PATH),
            str(source_path): sha256(source_path),
        },
        "code": {
            str(Path(__file__).relative_to(HERE)): sha256(Path(__file__)),
            "code/aligned_detection_analysis.py": sha256(Path(aligned.__file__)),
            "code/event_pair_analysis.py": sha256(Path(base.__file__)),
            "code/simulated_waveforms.py": sha256(Path(simulated.__file__)),
        },
        "outputs": {path.name: sha256(path) for path in paths},
    }
    manifest_path = OUTPUT / "two-station-correlation-manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
