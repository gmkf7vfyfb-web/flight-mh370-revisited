#!/usr/bin/env python3
"""Expanded H08S periodic-airgun filter and mask sensitivity analysis.

The only waveform input is Kadri Figure 9d: calibrated vector vertices from an
already-filtered publication plot.  This script therefore compares filters in
the publication representation; it cannot reproduce raw-array processing.
"""

from __future__ import annotations

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
from matplotlib.patches import Patch
from scipy.signal import fftconvolve, find_peaks


HERE = Path(__file__).resolve().parents[1]
ROOT = HERE
DATA = HERE / "data"
OUTPUT = HERE / "outputs"
CONFIG_PATH = DATA / "filter-sensitivity-config.json"
METADATA_PATH = DATA / "kadri-figure-extraction" / "metadata.json"
TRACE_ROOT = METADATA_PATH.parent
CANDIDATE_PATH = DATA / "observed-transient-candidates.csv"
PDF_METADATA = {"CreationDate": None, "ModDate": None}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def parse_utc(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)


def iso_utc(epoch_s: float) -> str:
    return (
        datetime.fromtimestamp(float(epoch_s), timezone.utc)
        .isoformat(timespec="milliseconds")
        .replace("+00:00", "Z")
    )


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        raise ValueError(f"No rows for {path}")
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def rolling_rms(values: np.ndarray, count: int) -> np.ndarray:
    count = max(2, int(count))
    return np.sqrt(
        np.maximum(
            np.convolve(values * values, np.ones(count, dtype=float) / count, mode="same"),
            0.0,
        )
    )


@dataclass
class TracePanel:
    panel: str
    start_epoch_s: float
    time_s: np.ndarray
    epoch_s: np.ndarray
    pressure_pa: np.ndarray


@dataclass
class ShotGeometry:
    initial_period_s: float
    fitted_period_s: float
    fitted_intercept_s: float
    cycle_numbers: np.ndarray
    predicted_centres_s: np.ndarray
    observed_centres_s: np.ndarray
    target_cycle_index: int
    phase_fit_indices: np.ndarray
    envelope: np.ndarray


@dataclass
class CycleSet:
    time_s: np.ndarray
    values: np.ndarray
    aligned_values: np.ndarray
    alignment_shifts_s: np.ndarray


def load_panel_d(configuration: dict) -> TracePanel:
    metadata = json.loads(METADATA_PATH.read_text(encoding="utf-8"))
    record = next(
        row
        for row in metadata["figure9_vector_traces"]
        if row["station"] == "H08S" and row["panel"] == "d"
    )
    with (TRACE_ROOT / record["file"]).open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    source_time = np.asarray([float(row["plotted_time_s"]) for row in rows])
    source_pressure = np.asarray([float(row["pressure_pa"]) for row in rows])
    order = np.argsort(source_time)
    unique_time, unique_index = np.unique(source_time[order], return_index=True)
    source_pressure = source_pressure[order][unique_index]
    dt = float(configuration["regular_grid_dt_s"])
    time_s = np.arange(0.0, 600.0, dt)
    pressure = np.interp(time_s, unique_time, source_pressure)
    pressure -= np.median(pressure)
    start = parse_utc(record["start_utc"]).timestamp()
    return TracePanel(
        panel="d",
        start_epoch_s=start,
        time_s=time_s,
        epoch_s=start + time_s,
        pressure_pa=pressure,
    )


def parabolic_peak(values: np.ndarray, index: int) -> float:
    if index <= 0 or index >= values.size - 1:
        return float(index)
    left, centre, right = values[index - 1 : index + 2]
    denominator = left - 2.0 * centre + right
    if abs(float(denominator)) < 1e-15:
        return float(index)
    return float(index + 0.5 * (left - right) / denominator)


def initial_period_and_envelope(panel: TracePanel, configuration: dict) -> tuple[float, np.ndarray]:
    dt = float(configuration["regular_grid_dt_s"])
    envelope = rolling_rms(
        panel.pressure_pa,
        int(round(float(configuration["envelope_window_s"]) / dt)),
    )
    centred = envelope - np.median(envelope)
    autocorrelation = fftconvolve(centred, centred[::-1], mode="full")[panel.time_s.size - 1 :]
    lower = int(round(float(configuration["period_search_s"][0]) / dt))
    upper = int(round(float(configuration["period_search_s"][1]) / dt))
    index = lower + int(np.argmax(autocorrelation[lower : upper + 1]))
    return parabolic_peak(autocorrelation, index) * dt, envelope


def fit_shot_geometry(panel: TracePanel, configuration: dict) -> ShotGeometry:
    dt = float(configuration["regular_grid_dt_s"])
    initial_period, envelope = initial_period_and_envelope(panel, configuration)
    event_time_s = parse_utc(configuration["event_utc"]).timestamp() - panel.start_epoch_s
    separation = int(round(0.70 * initial_period / dt))
    peaks, _ = find_peaks(
        envelope,
        distance=separation,
        prominence=0.06 * float(np.std(envelope)),
    )
    eligible = peaks[
        (panel.time_s[peaks] > initial_period)
        & (panel.time_s[peaks] < panel.time_s[-1] - initial_period)
        & (np.abs(panel.time_s[peaks] - event_time_s) > 1.5 * initial_period)
    ]
    if eligible.size < 20:
        raise ValueError("Too few non-target pulses to initialise the periodic fit")
    anchor_index = int(eligible[np.argmax(envelope[eligible])])
    intercept = float(panel.time_s[anchor_index])
    period = float(initial_period)
    search_half = float(configuration["shot_search_half_window_s"])

    final_numbers = np.array([], dtype=int)
    final_observed = np.array([], dtype=float)
    final_keep = np.array([], dtype=bool)
    for _iteration in range(5):
        k_min = int(math.ceil((panel.time_s[0] - intercept) / period))
        k_max = int(math.floor((panel.time_s[-1] - intercept) / period))
        numbers = np.arange(k_min, k_max + 1)
        predicted = intercept + period * numbers
        observed = []
        accepted_numbers = []
        for number, centre in zip(numbers, predicted):
            indices = np.flatnonzero(np.abs(panel.time_s - centre) <= search_half)
            if indices.size == 0:
                continue
            selected = int(indices[np.argmax(envelope[indices])])
            observed.append(float(panel.time_s[selected]))
            accepted_numbers.append(int(number))
        observed_array = np.asarray(observed)
        number_array = np.asarray(accepted_numbers, dtype=int)
        target_cycle = int(np.argmin(np.abs(observed_array - event_time_s)))
        fit_mask = (
            (np.arange(observed_array.size) != target_cycle)
            & (np.abs(observed_array - event_time_s) > 0.55 * period)
        )
        fit = np.polyfit(number_array[fit_mask], observed_array[fit_mask], 1)
        period, intercept = float(fit[0]), float(fit[1])
        residual = observed_array - (intercept + period * number_array)
        centre = float(np.median(residual[fit_mask]))
        scale = 1.4826 * float(np.median(np.abs(residual[fit_mask] - centre)))
        robust_keep = np.abs(residual - centre) <= max(0.35, 3.5 * scale)
        fit_mask &= robust_keep
        fit = np.polyfit(number_array[fit_mask], observed_array[fit_mask], 1)
        period, intercept = float(fit[0]), float(fit[1])
        final_numbers = number_array
        final_observed = observed_array
        final_keep = fit_mask

    predicted = intercept + period * final_numbers
    target_cycle = int(np.argmin(np.abs(final_observed - event_time_s)))
    return ShotGeometry(
        initial_period_s=initial_period,
        fitted_period_s=period,
        fitted_intercept_s=intercept,
        cycle_numbers=final_numbers,
        predicted_centres_s=predicted,
        observed_centres_s=final_observed,
        target_cycle_index=target_cycle,
        phase_fit_indices=np.flatnonzero(final_keep),
        envelope=envelope,
    )


def normalised_correlation(left: np.ndarray, right: np.ndarray) -> float:
    left = left - np.median(left)
    right = right - np.median(right)
    denominator = float(np.linalg.norm(left) * np.linalg.norm(right))
    return float(np.dot(left, right) / denominator) if denominator > 0.0 else -1.0


def shifted_cycle(cycle: np.ndarray, time_s: np.ndarray, shift_s: float) -> np.ndarray:
    return np.interp(time_s + shift_s, time_s, cycle, left=cycle[0], right=cycle[-1])


def align_to_template(
    cycle: np.ndarray,
    time_s: np.ndarray,
    template: np.ndarray,
    maximum_shift_s: float,
    dt: float,
) -> tuple[np.ndarray, float]:
    if maximum_shift_s <= 0.0:
        return cycle.copy(), 0.0
    shifts = np.arange(-maximum_shift_s, maximum_shift_s + dt / 2.0, dt)
    candidates = [shifted_cycle(cycle, time_s, float(shift)) for shift in shifts]
    scores = [normalised_correlation(candidate, template) for candidate in candidates]
    best = int(np.argmax(scores))
    return candidates[best], float(shifts[best])


def extract_and_align_cycles(
    panel: TracePanel,
    geometry: ShotGeometry,
    configuration: dict,
) -> CycleSet:
    dt = float(configuration["regular_grid_dt_s"])
    half_width = float(configuration["cycle_half_width_s"])
    time_s = np.arange(-half_width, half_width + dt / 2.0, dt)
    cycles = []
    retained_centres = []
    retained_indices = []
    for index, centre in enumerate(geometry.observed_centres_s):
        if centre + time_s[0] < panel.time_s[0] or centre + time_s[-1] > panel.time_s[-1]:
            continue
        cycle = np.interp(centre + time_s, panel.time_s, panel.pressure_pa)
        cycle -= np.median(cycle)
        cycles.append(cycle)
        retained_centres.append(centre)
        retained_indices.append(index)
    values = np.vstack(cycles)
    if values.shape[0] < 45:
        raise ValueError("Too few complete cycles")
    template = np.median(values, axis=0)
    maximum_shift = float(configuration["alignment_max_shift_s"])
    shifts = np.zeros(values.shape[0], dtype=float)
    aligned = values.copy()
    for _iteration in range(3):
        for index, cycle in enumerate(values):
            aligned[index], shifts[index] = align_to_template(
                cycle, time_s, template, maximum_shift, dt
            )
        template = np.median(aligned, axis=0)

    original_target = geometry.target_cycle_index
    mapped_target = retained_indices.index(original_target)
    geometry.target_cycle_index = mapped_target
    geometry.observed_centres_s = np.asarray(retained_centres)
    geometry.predicted_centres_s = geometry.predicted_centres_s[retained_indices]
    geometry.cycle_numbers = geometry.cycle_numbers[retained_indices]
    return CycleSet(
        time_s=time_s,
        values=values,
        aligned_values=aligned,
        alignment_shifts_s=shifts,
    )


def robust_scale(template: np.ndarray, values: np.ndarray) -> float:
    weights = np.ones_like(values)
    scale = 1.0
    for _iteration in range(5):
        denominator = float(np.sum(weights * template * template))
        if denominator <= 1e-12:
            return 0.0
        scale = float(np.sum(weights * template * values) / denominator)
        residual = values - scale * template
        sigma = 1.4826 * float(np.median(np.abs(residual - np.median(residual))))
        if sigma <= 0.0:
            break
        ratio = np.abs(residual) / (1.5 * sigma)
        weights = np.ones_like(ratio)
        tail = ratio > 1.0
        weights[tail] = 1.0 / ratio[tail]
    return scale


def leave_out_indices(count: int, index: int, neighbours: int) -> np.ndarray:
    indices = np.arange(count)
    return indices[np.abs(indices - index) > neighbours]


def template_residual_cycles(
    cycles: CycleSet,
    maximum_shift_s: float,
    configuration: dict,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    count = cycles.values.shape[0]
    residuals = np.zeros_like(cycles.values)
    models = np.zeros_like(cycles.values)
    shifts = np.zeros(count, dtype=float)
    dt = float(configuration["regular_grid_dt_s"])
    neighbours = int(configuration["leave_out_neighbour_cycles"])
    for index in range(count):
        training = leave_out_indices(count, index, neighbours)
        template = np.median(cycles.aligned_values[training], axis=0)
        aligned, shift = align_to_template(
            cycles.values[index], cycles.time_s, template, maximum_shift_s, dt
        )
        scale = robust_scale(template, aligned)
        aligned_model = scale * template
        model = np.interp(
            cycles.time_s - shift,
            cycles.time_s,
            aligned_model,
            left=aligned_model[0],
            right=aligned_model[-1],
        )
        models[index] = model
        residuals[index] = cycles.values[index] - model
        shifts[index] = shift
    return residuals, models, shifts


def low_rank_residual_cycles(
    cycles: CycleSet,
    rank: int,
    maximum_shift_s: float,
    configuration: dict,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    count = cycles.values.shape[0]
    residuals = np.zeros_like(cycles.values)
    models = np.zeros_like(cycles.values)
    shifts = np.zeros(count, dtype=float)
    dt = float(configuration["regular_grid_dt_s"])
    neighbours = int(configuration["leave_out_neighbour_cycles"])
    shift_grid = np.arange(-maximum_shift_s, maximum_shift_s + dt / 2.0, dt)
    if maximum_shift_s <= 0.0:
        shift_grid = np.array([0.0])
    for index in range(count):
        training = leave_out_indices(count, index, neighbours)
        training_values = cycles.aligned_values[training]
        centre = np.median(training_values, axis=0)
        centred_training = training_values - centre
        _left, _singular, right = np.linalg.svd(centred_training, full_matrices=False)
        basis = right[: min(rank, right.shape[0])]
        best_loss = float("inf")
        best_model = np.zeros_like(centre)
        best_shift = 0.0
        for shift in shift_grid:
            aligned = shifted_cycle(cycles.values[index], cycles.time_s, float(shift))
            coefficients = basis @ (aligned - centre)
            aligned_model = centre + coefficients @ basis
            loss = float(np.median(np.abs(aligned - aligned_model)))
            if loss < best_loss:
                best_loss = loss
                best_model = aligned_model
                best_shift = float(shift)
        model = np.interp(
            cycles.time_s - best_shift,
            cycles.time_s,
            best_model,
            left=best_model[0],
            right=best_model[-1],
        )
        models[index] = model
        residuals[index] = cycles.values[index] - model
        shifts[index] = best_shift
    return residuals, models, shifts


def cycle_scores(values: np.ndarray, cycle_time_s: np.ndarray, half_width_s: float) -> np.ndarray:
    central = np.abs(cycle_time_s) <= half_width_s
    return np.sqrt(np.mean(values[:, central] ** 2, axis=1))


def empirical_percentile(values: np.ndarray, target_index: int) -> float:
    control = np.delete(values, target_index)
    return float(100.0 * (np.count_nonzero(control <= values[target_index]) + 0.5) / (control.size + 1.0))


def method_summary(
    label: str,
    family: str,
    parameter: float,
    cycles: CycleSet,
    geometry: ShotGeometry,
    residuals: np.ndarray,
    models: np.ndarray,
    shifts: np.ndarray,
    configuration: dict,
) -> dict:
    half = float(configuration["comparison_local_half_width_s"])
    original = cycle_scores(cycles.values, cycles.time_s, half)
    residual = cycle_scores(residuals, cycles.time_s, half)
    target = geometry.target_cycle_index
    control_indices = np.arange(original.size) != target
    ratio = residual / np.maximum(original, 1e-12)
    return {
        "method": label,
        "family": family,
        "parameter": parameter,
        "cycle_count": int(original.size),
        "control_median_original_rms_pa": float(np.median(original[control_indices])),
        "control_median_residual_rms_pa": float(np.median(residual[control_indices])),
        "control_median_rms_retained_fraction": float(np.median(ratio[control_indices])),
        "control_median_rms_removed_fraction": float(1.0 - np.median(ratio[control_indices])),
        "target_original_rms_pa": float(original[target]),
        "target_residual_rms_pa": float(residual[target]),
        "target_rms_retained_fraction": float(ratio[target]),
        "target_original_empirical_percentile": empirical_percentile(original, target),
        "target_residual_empirical_percentile": empirical_percentile(residual, target),
        "median_absolute_alignment_shift_s": float(np.median(np.abs(shifts))),
        "maximum_absolute_alignment_shift_s": float(np.max(np.abs(shifts))),
        "status": "LEAVE_ONE_SHOT_AND_NEIGHBOURS_OUT_PUBLICATION_TRACE_CONTROL",
        "_residuals": residuals,
        "_models": models,
    }


def evaluate_methods(
    cycles: CycleSet,
    geometry: ShotGeometry,
    configuration: dict,
) -> list[dict]:
    output = []
    for shift in configuration["adaptive_template_shift_s"]:
        residuals, models, shifts = template_residual_cycles(cycles, float(shift), configuration)
        output.append(
            method_summary(
                f"adaptive_template_shift_{float(shift):.2f}s",
                "adaptive_template",
                float(shift),
                cycles,
                geometry,
                residuals,
                models,
                shifts,
                configuration,
            )
        )
    for rank in configuration["low_rank_values"]:
        residuals, models, shifts = low_rank_residual_cycles(
            cycles,
            int(rank),
            0.30,
            configuration,
        )
        output.append(
            method_summary(
                f"low_rank_{int(rank)}_shift_0.30s",
                "low_rank",
                float(rank),
                cycles,
                geometry,
                residuals,
                models,
                shifts,
                configuration,
            )
        )
    return output


def mask_sensitivity(
    panel: TracePanel,
    geometry: ShotGeometry,
    cycles: CycleSet,
    configuration: dict,
) -> list[dict]:
    profile = np.median(cycles.aligned_values**2, axis=0)
    baseline = float(np.quantile(profile, 0.20))
    excess = np.maximum(profile - baseline, 0.0)
    total = float(np.sum(excess))
    event_time_s = parse_utc(configuration["event_utc"]).timestamp() - panel.start_epoch_s
    target_observed = float(geometry.observed_centres_s[geometry.target_cycle_index])
    target_predicted = float(geometry.predicted_centres_s[geometry.target_cycle_index])
    nearest_predicted = np.argmin(
        np.abs(panel.time_s[:, None] - geometry.predicted_centres_s[None, :]), axis=1
    )
    nearest_observed = np.argmin(
        np.abs(panel.time_s[:, None] - geometry.observed_centres_s[None, :]), axis=1
    )
    predicted_phase = panel.time_s - geometry.predicted_centres_s[nearest_predicted]
    observed_phase = panel.time_s - geometry.observed_centres_s[nearest_observed]
    output = []
    for half_width in configuration["fixed_mask_half_widths_s"]:
        half_width = float(half_width)
        predicted_mask = np.abs(predicted_phase) <= half_width
        observed_mask = np.abs(observed_phase) <= half_width
        template_mask = np.abs(cycles.time_s) <= half_width
        removed = float(np.sum(excess[template_mask]) / total) if total > 0.0 else float("nan")
        output.append(
            {
                "mask_half_width_s": half_width,
                "mask_total_width_s": 2.0 * half_width,
                "data_masked_fraction_predicted_phase": float(np.mean(predicted_mask)),
                "data_masked_fraction_observed_centres": float(np.mean(observed_mask)),
                "phase_folded_excess_energy_removed_fraction": removed,
                "phase_folded_excess_energy_remaining_fraction": 1.0 - removed,
                "event_offset_from_leave_target_out_predicted_shot_s": event_time_s - target_predicted,
                "event_offset_from_observed_envelope_peak_s": event_time_s - target_observed,
                "event_is_masked_predicted_phase": bool(
                    abs(event_time_s - target_predicted) <= half_width
                ),
                "event_is_masked_observed_centres": bool(
                    abs(event_time_s - target_observed) <= half_width
                ),
                "status": "PREDICTED_AND_OBSERVED_CENTRED_PERIODIC_MASK_PUBLICATION_TRACE_SENSITIVITY",
            }
        )
    return output


def build_full_trace(
    panel: TracePanel,
    geometry: ShotGeometry,
    cycles: CycleSet,
    residual_cycles: np.ndarray,
) -> np.ndarray:
    output = panel.pressure_pa.copy()
    nearest = np.argmin(np.abs(panel.time_s[:, None] - geometry.observed_centres_s[None, :]), axis=1)
    for index, centre in enumerate(geometry.observed_centres_s):
        samples = nearest == index
        relative = panel.time_s[samples] - centre
        inside = (relative >= cycles.time_s[0]) & (relative <= cycles.time_s[-1])
        sample_indices = np.flatnonzero(samples)
        output[sample_indices[inside]] = np.interp(
            relative[inside], cycles.time_s, residual_cycles[index]
        )
    return output


def serialisable_method_rows(methods: list[dict]) -> list[dict]:
    rows = []
    for method in methods:
        rows.append({key: value for key, value in method.items() if not key.startswith("_")})
    return rows


def shot_control_rows(
    panel: TracePanel,
    geometry: ShotGeometry,
    cycles: CycleSet,
    selected: dict,
    configuration: dict,
) -> list[dict]:
    original = cycle_scores(
        cycles.values, cycles.time_s, float(configuration["comparison_local_half_width_s"])
    )
    residual = cycle_scores(
        selected["_residuals"],
        cycles.time_s,
        float(configuration["comparison_local_half_width_s"]),
    )
    rows = []
    for index in range(original.size):
        rows.append(
            {
                "cycle_index": index,
                "observed_shot_utc": iso_utc(panel.start_epoch_s + geometry.observed_centres_s[index]),
                "predicted_shot_utc_leave_target_out_phase_fit": iso_utc(panel.start_epoch_s + geometry.predicted_centres_s[index]),
                "is_010313_target_cycle": bool(index == geometry.target_cycle_index),
                "original_local_rms_pa": f"{original[index]:.9g}",
                "selected_filter_residual_local_rms_pa": f"{residual[index]:.9g}",
                "residual_retained_fraction": f"{residual[index] / max(original[index], 1e-12):.9g}",
                "status": "EMPIRICAL_LEAVE_ONE_SHOT_OUT_CONTROL",
            }
        )
    return rows


def plot_tradeoffs(methods: list[dict], masks: list[dict], selected: dict) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(16.4, 6.8))
    axis = axes[0]
    x = np.asarray([100.0 * row["data_masked_fraction_observed_centres"] for row in masks])
    y = np.asarray([100.0 * row["phase_folded_excess_energy_removed_fraction"] for row in masks])
    axis.plot(x, y, marker="o", color="#7B3294", linewidth=2.0)
    for row, x_value, y_value in zip(masks, x, y):
        axis.annotate(
            (
                f"±{1000.0 * row['mask_half_width_s']:.0f} ms"
                if row["mask_half_width_s"] < 0.2
                else f"±{row['mask_half_width_s']:.2g} s"
            ),
            (x_value, y_value),
            xytext=(4, 5),
            textcoords="offset points",
            fontsize=7.8,
        )
    axis.set_xlabel("Publication-trace samples discarded by observed-centred masks (%)")
    axis.set_ylabel("Phase-folded excess energy removed (%)")
    axis.set_xlim(left=0.0)
    axis.set_ylim(0.0, 102.0)
    axis.grid(alpha=0.22)
    axis.set_title("A. Periodic-mask information-loss trade-off")

    axis = axes[1]
    colour = {"adaptive_template": "#1769AA", "low_rank": "#C86516"}
    marker = {"adaptive_template": "o", "low_rank": "s"}
    for method in methods:
        axis.scatter(
            100.0 * method["control_median_rms_removed_fraction"],
            method["target_residual_empirical_percentile"],
            s=90 if method["method"] == selected["method"] else 50,
            color=colour[method["family"]],
            marker=marker[method["family"]],
            edgecolor="#111111" if method["method"] == selected["method"] else "none",
            linewidth=1.2,
            zorder=4,
        )
        axis.annotate(
            f"{method['parameter']:g}",
            (
                100.0 * method["control_median_rms_removed_fraction"],
                method["target_residual_empirical_percentile"],
            ),
            xytext=(4, 4),
            textcoords="offset points",
            fontsize=7.4,
        )
    axis.axhline(95.0, color="#A61B29", linestyle="--", linewidth=1.0, label="95th percentile")
    axis.set_xlabel("Median control-pulse RMS removed (%)")
    axis.set_ylabel("01:03:13 residual percentile among shot controls")
    axis.set_ylim(0.0, 102.0)
    axis.grid(alpha=0.22)
    axis.set_title("B. Filter strength versus target residual rank")
    axis.legend(
        handles=[
            Line2D([0], [0], marker="o", linestyle="", color="#1769AA", label="adaptive template; label = shift (s)"),
            Line2D([0], [0], marker="s", linestyle="", color="#C86516", label="low rank; label = rank"),
            Line2D([0], [0], color="#A61B29", linestyle="--", label="95th percentile"),
        ],
        fontsize=7.8,
        loc="lower right",
    )
    fig.suptitle("H08S periodic-airgun filter and mask sensitivity", fontsize=15.8)
    fig.text(
        0.5,
        0.018,
        "Each filter treats every pulse as a held-out test cycle; labels show template shift allowance or low-rank dimension.",
        ha="center",
        fontsize=8.8,
    )
    fig.tight_layout(rect=[0.0, 0.045, 1.0, 0.95])
    for suffix in ("png", "pdf"):
        fig.savefig(OUTPUT / f"airgun-filter-mask-tradeoffs.{suffix}", dpi=270 if suffix == "png" else None, metadata=PDF_METADATA if suffix == "pdf" else None)
    plt.close(fig)


def plot_controls(
    panel: TracePanel,
    geometry: ShotGeometry,
    cycles: CycleSet,
    selected: dict,
    configuration: dict,
) -> None:
    original = cycle_scores(
        cycles.values, cycles.time_s, float(configuration["comparison_local_half_width_s"])
    )
    residual = cycle_scores(
        selected["_residuals"], cycles.time_s, float(configuration["comparison_local_half_width_s"])
    )
    target = geometry.target_cycle_index
    times = [
        datetime.fromtimestamp(panel.start_epoch_s + value, timezone.utc)
        for value in geometry.observed_centres_s
    ]
    fig, axes = plt.subplots(1, 2, figsize=(16.2, 6.4), gridspec_kw={"width_ratios": [1.25, 0.75]})
    axis = axes[0]
    axis.plot(times, original, color="#777777", marker="o", markersize=3.2, linewidth=0.8, label="original pulse RMS")
    axis.plot(times, residual, color="#1769AA", marker="o", markersize=3.2, linewidth=0.8, label=f"residual: {selected['method']}")
    axis.scatter(times[target], residual[target], s=105, marker="*", color="#A61B29", edgecolor="white", linewidth=0.8, zorder=6, label="01:03:13 cycle")
    axis.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M", tz=timezone.utc))
    axis.set_xlabel("Observed shot-centre time (UTC)")
    axis.set_ylabel("Local ±2 s RMS (Pa proxy)")
    axis.grid(alpha=0.2)
    axis.legend(fontsize=8.0)
    axis.set_title("A. Every airgun pulse treated as a held-out control")

    axis = axes[1]
    control = np.delete(residual, target)
    ordered = np.sort(control)
    cumulative = np.arange(1, ordered.size + 1) / ordered.size
    axis.step(ordered, cumulative, where="post", color="#1769AA", linewidth=2.0, label="other held-out pulses")
    axis.axvline(residual[target], color="#A61B29", linewidth=2.0, label=f"01:03:13: {selected['target_residual_empirical_percentile']:.1f}th percentile")
    axis.set_xlabel("Residual local RMS (Pa proxy)")
    axis.set_ylabel("Empirical cumulative fraction")
    axis.grid(alpha=0.2)
    axis.legend(fontsize=8.0, loc="lower right")
    axis.set_title("B. Residual-control distribution")
    fig.suptitle("Leave-one-shot-out test of the 01:03:13 H08S feature", fontsize=15.8)
    fig.text(
        0.5,
        0.018,
        "An elevated residual is an outlier relative to other plotted airgun cycles, not proof of a second physical source.",
        ha="center",
        fontsize=8.8,
    )
    fig.tight_layout(rect=[0.0, 0.045, 1.0, 0.95])
    for suffix in ("png", "pdf"):
        fig.savefig(OUTPUT / f"leave-one-shot-out-controls.{suffix}", dpi=270 if suffix == "png" else None, metadata=PDF_METADATA if suffix == "pdf" else None)
    plt.close(fig)


def plot_filtered_trace_and_zoom(
    panel: TracePanel,
    geometry: ShotGeometry,
    cycles: CycleSet,
    template_method: dict,
    low_rank_method: dict,
    selected: dict,
    masks: list[dict],
    configuration: dict,
) -> None:
    full_template = build_full_trace(panel, geometry, cycles, template_method["_residuals"])
    full_low_rank = build_full_trace(panel, geometry, cycles, low_rank_method["_residuals"])
    full_selected = build_full_trace(panel, geometry, cycles, selected["_residuals"])
    event_epoch = parse_utc(configuration["event_utc"]).timestamp()
    conservative_mask_row = next(row for row in masks if row["mask_half_width_s"] == 0.5)
    nearest = np.argmin(np.abs(panel.time_s[:, None] - geometry.predicted_centres_s[None, :]), axis=1)
    phase = panel.time_s - geometry.predicted_centres_s[nearest]
    narrow_mask = np.abs(phase) <= float(conservative_mask_row["mask_half_width_s"])
    combined = full_selected.copy()
    combined[narrow_mask] = np.nan
    x = np.asarray([datetime.fromtimestamp(value, timezone.utc) for value in panel.epoch_s])

    series = [
        (panel.pressure_pa, "#555555", "Original extracted trace"),
        (full_template, "#1769AA", f"Adaptive-template residual: {template_method['parameter']:.2f} s shift"),
        (full_low_rank, "#C86516", f"Low-rank residual: rank {int(low_rank_method['parameter'])}"),
        (combined, "#146B4A", f"Selected residual + ±0.5 s periodic mask ({100*conservative_mask_row['data_masked_fraction_predicted_phase']:.1f}% discarded)"),
    ]
    maximum = float(np.quantile(np.abs(panel.pressure_pa), 0.999)) * 1.15
    fig, axes = plt.subplots(4, 1, figsize=(15.0, 10.2), sharex=True)
    for axis, (values, colour, label) in zip(axes, series):
        axis.plot(x, values, color=colour, linewidth=0.55)
        axis.axvline(datetime.fromtimestamp(event_epoch, timezone.utc), color="#A61B29", linewidth=1.4)
        axis.set_ylim(-maximum, maximum)
        axis.set_ylabel("Pa proxy")
        axis.set_title(label, loc="left", fontsize=9.7, weight="bold")
        axis.grid(alpha=0.18)
    axes[-1].xaxis.set_major_formatter(mdates.DateFormatter("%H:%M", tz=timezone.utc))
    axes[-1].set_xlabel("UTC on 8 March 2014")
    fig.suptitle("H08S Figure 9d under expanded periodic filtering", fontsize=15.7)
    fig.text(0.5, 0.014, "Red line: 01:03:13.15; mask gaps are missing observations, not zero pressure.", ha="center", fontsize=8.8)
    fig.tight_layout(rect=[0.0, 0.035, 1.0, 0.96])
    for suffix in ("png", "pdf"):
        fig.savefig(OUTPUT / f"expanded-filter-full-trace.{suffix}", dpi=270 if suffix == "png" else None, metadata=PDF_METADATA if suffix == "pdf" else None)
    plt.close(fig)

    zoom = (panel.epoch_s >= event_epoch - 20.0) & (panel.epoch_s <= event_epoch + 20.0)
    fig, axes = plt.subplots(4, 1, figsize=(14.2, 9.2), sharex=True)
    zoom_maximum = float(np.max(np.abs(panel.pressure_pa[zoom]))) * 1.08
    for axis, (values, colour, label) in zip(axes, series):
        axis.plot(x[zoom], values[zoom], color=colour, linewidth=0.8)
        axis.axvline(datetime.fromtimestamp(event_epoch, timezone.utc), color="#A61B29", linewidth=1.4)
        axis.set_ylim(-zoom_maximum, zoom_maximum)
        axis.set_ylabel("Pa proxy")
        axis.set_title(label, loc="left", fontsize=9.7, weight="bold")
        axis.grid(alpha=0.18)
    axes[-1].xaxis.set_major_formatter(mdates.DateFormatter("%H:%M:%S", tz=timezone.utc))
    axes[-1].set_xlabel("UTC on 8 March 2014")
    fig.suptitle("Expanded-filter detail around the 01:03:13 H08S feature", fontsize=15.5)
    fig.text(0.5, 0.014, "The narrow mask still covers the target because it is phase-coincident with the periodic shot prediction.", ha="center", fontsize=8.8)
    fig.tight_layout(rect=[0.0, 0.035, 1.0, 0.96])
    for suffix in ("png", "pdf"):
        fig.savefig(OUTPUT / f"expanded-filter-010313-zoom.{suffix}", dpi=280 if suffix == "png" else None, metadata=PDF_METADATA if suffix == "pdf" else None)
    plt.close(fig)



def phase_mask(panel: TracePanel, centres_s: np.ndarray, half_width_s: float) -> np.ndarray:
    nearest = np.argmin(np.abs(panel.time_s[:, None] - centres_s[None, :]), axis=1)
    return np.abs(panel.time_s - centres_s[nearest]) <= half_width_s


def plot_subsecond_masks(
    panel: TracePanel,
    geometry: ShotGeometry,
    cycles: CycleSet,
    selected: dict,
    masks: list[dict],
    configuration: dict,
) -> None:
    """Show what ±100/±150 ms means under two different centring rules."""
    selected_residual = build_full_trace(panel, geometry, cycles, selected["_residuals"])
    event_epoch = parse_utc(configuration["event_utc"]).timestamp()
    event_time_s = event_epoch - panel.start_epoch_s
    target = geometry.target_cycle_index
    predicted_target = float(geometry.predicted_centres_s[target])
    observed_target = float(geometry.observed_centres_s[target])
    zoom = np.abs(panel.time_s - event_time_s) <= 1.25
    relative_ms = 1000.0 * (panel.time_s[zoom] - event_time_s)
    widths = (0.10, 0.15)
    colours = {
        "event": "#A61B29",
        "predicted": "#1769AA",
        "observed": "#C86516",
        "trace": "#444444",
        "residual": "#146B4A",
    }
    maximum = float(np.max(np.abs(panel.pressure_pa[zoom]))) * 1.10
    fig, axes = plt.subplots(3, 2, figsize=(15.2, 9.2), sharex=True, sharey=True)
    for column, half_width in enumerate(widths):
        row = next(item for item in masks if math.isclose(item["mask_half_width_s"], half_width))
        predicted_mask = phase_mask(panel, geometry.predicted_centres_s, half_width)
        observed_mask = phase_mask(panel, geometry.observed_centres_s, half_width)
        predicted_values = selected_residual.copy()
        observed_values = selected_residual.copy()
        predicted_values[predicted_mask] = np.nan
        observed_values[observed_mask] = np.nan

        axis = axes[0, column]
        axis.plot(relative_ms, panel.pressure_pa[zoom], color=colours["trace"], linewidth=1.0)
        axis.axvspan(
            1000.0 * (predicted_target - half_width - event_time_s),
            1000.0 * (predicted_target + half_width - event_time_s),
            color=colours["predicted"], alpha=0.18,
        )
        axis.axvspan(
            1000.0 * (observed_target - half_width - event_time_s),
            1000.0 * (observed_target + half_width - event_time_s),
            color=colours["observed"], alpha=0.18,
        )
        axis.set_title(
            f"±{1000 * half_width:.0f} ms half-width ({2000 * half_width:.0f} ms total)",
            fontsize=11.2,
            weight="bold",
        )
        axis.set_ylabel("Extracted trace\n(Pa proxy)")

        axis = axes[1, column]
        axis.plot(relative_ms, predicted_values[zoom], color=colours["residual"], linewidth=1.0)
        axis.set_ylabel("Residual after\npredicted-phase mask")
        axis.text(
            0.02, 0.90,
            "target retained" if not row["event_is_masked_predicted_phase"] else "target masked",
            transform=axis.transAxes, va="top", fontsize=9.0,
            color=colours["predicted"], weight="bold",
        )

        axis = axes[2, column]
        axis.plot(relative_ms, observed_values[zoom], color=colours["residual"], linewidth=1.0)
        axis.set_ylabel("Residual after\nobserved-centred mask")
        axis.text(
            0.02, 0.90,
            "target retained" if not row["event_is_masked_observed_centres"] else "target masked",
            transform=axis.transAxes, va="top", fontsize=9.0,
            color=colours["observed"], weight="bold",
        )
        axis.set_xlabel("Time relative to 01:03:13.150 UTC (ms)")

        for axis in axes[:, column]:
            axis.axvline(0.0, color=colours["event"], linewidth=1.5)
            axis.axvline(
                1000.0 * (predicted_target - event_time_s),
                color=colours["predicted"], linewidth=1.0, linestyle="--",
            )
            axis.axvline(
                1000.0 * (observed_target - event_time_s),
                color=colours["observed"], linewidth=1.0, linestyle=":",
            )
            axis.set_ylim(-maximum, maximum)
            axis.grid(alpha=0.18)

    axes[0, 0].legend(
        handles=[
            Line2D([0], [0], color=colours["event"], label="screened time"),
            Line2D([0], [0], color=colours["predicted"], linestyle="--", label="leave-target-out predicted shot"),
            Line2D([0], [0], color=colours["observed"], linestyle=":", label="observed envelope peak"),
            Patch(facecolor=colours["predicted"], alpha=0.18, label="predicted-phase mask window"),
            Patch(facecolor=colours["observed"], alpha=0.18, label="observed-centred mask window"),
        ],
        fontsize=7.6,
        loc="lower left",
    )
    fig.suptitle("H08S sub-second periodic-mask sensitivity", fontsize=15.6)
    fig.text(
        0.5, 0.018,
        "The screened time is +174 ms from the target-excluded periodic prediction and +50 ms from the observed peak. "
        "Both widths are below the publication line's indicative ±0.51 s timing thickness; raw channels are required.",
        ha="center", fontsize=8.6,
    )
    fig.tight_layout(rect=[0.0, 0.05, 1.0, 0.95])
    for suffix in ("png", "pdf"):
        fig.savefig(OUTPUT / f"subsecond-periodic-mask-comparison.{suffix}", dpi=280 if suffix == "png" else None, metadata=PDF_METADATA if suffix == "pdf" else None)
    plt.close(fig)

def manifest(paths: list[Path]) -> dict:
    input_paths = [CONFIG_PATH, METADATA_PATH, CANDIDATE_PATH]
    return {
        "status": "REPRODUCIBLE_OUTPUT_HASHES",
        "inputs": {str(path.relative_to(ROOT)): sha256(path) for path in input_paths},
        "code": {str(Path(__file__).relative_to(ROOT)): sha256(Path(__file__))},
        "outputs": {path.name: sha256(path) for path in paths},
    }


def main() -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    configuration = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    panel = load_panel_d(configuration)
    geometry = fit_shot_geometry(panel, configuration)
    cycles = extract_and_align_cycles(panel, geometry, configuration)
    methods = evaluate_methods(cycles, geometry, configuration)
    masks = mask_sensitivity(panel, geometry, cycles, configuration)

    # Selection is made only from median held-out control suppression, never from
    # the target cycle's residual.
    selected = min(methods, key=lambda row: row["control_median_rms_retained_fraction"])
    best_template = min(
        [row for row in methods if row["family"] == "adaptive_template"],
        key=lambda row: row["control_median_rms_retained_fraction"],
    )
    best_low_rank = min(
        [row for row in methods if row["family"] == "low_rank"],
        key=lambda row: row["control_median_rms_retained_fraction"],
    )

    method_csv = OUTPUT / "filter-method-sensitivity.csv"
    mask_csv = OUTPUT / "mask-width-sensitivity.csv"
    shot_csv = OUTPUT / "leave-one-shot-out-controls.csv"
    write_csv(method_csv, serialisable_method_rows(methods))
    write_csv(mask_csv, masks)
    write_csv(shot_csv, shot_control_rows(panel, geometry, cycles, selected, configuration))

    plot_tradeoffs(methods, masks, selected)
    plot_controls(panel, geometry, cycles, selected, configuration)
    plot_subsecond_masks(panel, geometry, cycles, selected, masks, configuration)
    plot_filtered_trace_and_zoom(
        panel,
        geometry,
        cycles,
        best_template,
        best_low_rank,
        selected,
        masks,
        configuration,
    )

    event_time_s = parse_utc(configuration["event_utc"]).timestamp() - panel.start_epoch_s
    target = geometry.target_cycle_index
    summary = {
        "status": "DERIVED_PUBLICATION_TRACE_SENSITIVITY_NOT_RAW_DATA_EVENT_IDENTITY_OR_MH370_ASSOCIATION",
        "source_boundary": "Kadri labels Figure 9d-e airgun noise; all periodicity, filtering and rankings below are independently derived from extracted Figure 9d vector geometry.",
        "phase_fit": {
            "initial_autocorrelation_period_s": geometry.initial_period_s,
            "leave_target_out_fitted_period_s": geometry.fitted_period_s,
            "complete_cycle_count": int(cycles.values.shape[0]),
            "target_cycle_index": int(target),
            "target_event_utc": configuration["event_utc"],
            "target_predicted_shot_utc": iso_utc(panel.start_epoch_s + geometry.predicted_centres_s[target]),
            "target_observed_envelope_peak_utc": iso_utc(panel.start_epoch_s + geometry.observed_centres_s[target]),
            "event_minus_leave_target_out_predicted_shot_s": float(event_time_s - geometry.predicted_centres_s[target]),
            "event_minus_observed_envelope_peak_s": float(event_time_s - geometry.observed_centres_s[target]),
            "target_excluded_from_period_and_phase_fit": True,
        },
        "selection": {
            "rule": "minimum median held-out control-pulse RMS retained fraction; target cycle not used",
            "selected_method": {key: value for key, value in selected.items() if not key.startswith("_")},
            "best_adaptive_template": {key: value for key, value in best_template.items() if not key.startswith("_")},
            "best_low_rank": {key: value for key, value in best_low_rank.items() if not key.startswith("_")},
        },
        "mask_sensitivity": masks,
        "interpretive_limits": [
            "an elevated held-out residual is not a source classifier",
            "at ±100 and ±150 ms the screened time is retained by blind predicted-phase masks but removed by observed-shot-centred masks",
            "filter coefficients fitted to a held-out cycle can remove a coincident signal component aligned with the airgun subspace",
            "the 20 Hz publication trace has already undergone Kadri's filtering and PDF rendering",
            "raw channels are required for spatial filtering, bearing and defensible signal detection",
        ],
    }
    summary_path = OUTPUT / "summary.json"
    summary_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    output_paths = [
        method_csv,
        mask_csv,
        shot_csv,
        summary_path,
        OUTPUT / "airgun-filter-mask-tradeoffs.png",
        OUTPUT / "airgun-filter-mask-tradeoffs.pdf",
        OUTPUT / "leave-one-shot-out-controls.png",
        OUTPUT / "leave-one-shot-out-controls.pdf",
        OUTPUT / "subsecond-periodic-mask-comparison.png",
        OUTPUT / "subsecond-periodic-mask-comparison.pdf",
        OUTPUT / "expanded-filter-full-trace.png",
        OUTPUT / "expanded-filter-full-trace.pdf",
        OUTPUT / "expanded-filter-010313-zoom.png",
        OUTPUT / "expanded-filter-010313-zoom.pdf",
    ]
    (OUTPUT / "manifest.json").write_text(
        json.dumps(manifest(output_paths), indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
