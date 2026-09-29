#!/usr/bin/env python3
"""Publication-trace significance controls and conditional source-time alignment.

This script operates on calibrated vectors extracted from Kadri Figure 9, not
raw CTBTO hydrophone channels.  It therefore provides exploratory
publication-trace screening controls, never calibrated receiver false-alarm
probabilities, bearings, or event associations.
"""

from __future__ import annotations

import copy
import csv
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
from scipy.signal import find_peaks

import event_pair_analysis as base
import filter_sensitivity as airgun
import publication_trace_score_overview as overview


HERE = Path(__file__).resolve().parents[1]
DATA = HERE / "data"
OUTPUT = HERE / "outputs"
CONFIG_PATH = DATA / "aligned-detection-config.json"
EVENT_CONFIG_PATH = DATA / "event-pair-analysis-config.json"
FILTER_CONFIG_PATH = DATA / "filter-sensitivity-config.json"
PDF_METADATA = {"CreationDate": None, "ModDate": None}


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


def utc(epoch_s: float) -> datetime:
    return datetime.fromtimestamp(float(epoch_s), timezone.utc)


def fmt_utc(epoch_s: float) -> str:
    return utc(epoch_s).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def candidate_peaks(score: np.ndarray, screen: dict) -> np.ndarray:
    dt = float(screen["regular_grid_dt_s"])
    separation = int(round(float(screen["candidate_minimum_separation_s"]) / dt))
    guard = int(round(float(screen["panel_edge_guard_s"]) / dt))
    peaks, _ = find_peaks(score, distance=separation)
    return peaks[(peaks >= guard) & (peaks < score.size - guard)]


def iaaft_surrogate(
    values: np.ndarray,
    rng: np.random.Generator,
    iterations: int,
) -> tuple[np.ndarray, float]:
    """Return one IAAFT surrogate and its relative amplitude-spectrum error."""
    target_sorted = np.sort(values)
    target_magnitude = np.abs(np.fft.rfft(values))
    surrogate = rng.permutation(values)
    for _ in range(iterations):
        spectrum = np.fft.rfft(surrogate)
        phase = np.exp(1j * np.angle(spectrum))
        spectrally_matched = np.fft.irfft(
            target_magnitude * phase, n=values.size
        )
        order = np.argsort(spectrally_matched, kind="stable")
        ranked = np.empty_like(order)
        ranked[order] = np.arange(order.size)
        surrogate = target_sorted[ranked]
    error = float(
        np.linalg.norm(np.abs(np.fft.rfft(surrogate)) - target_magnitude)
        / max(np.linalg.norm(target_magnitude), 1e-12)
    )
    return surrogate, error


def surrogate_panel_test(
    trace: base.Trace,
    screen: dict,
    rng: np.random.Generator,
    replicates: int,
    iterations: int,
    exploratory_window: tuple[float, float] | None = None,
) -> dict:
    observed_peaks = trace.candidate_indices
    observed_scores = trace.score[observed_peaks]
    null_max = np.empty(replicates, dtype=float)
    null_window_max = np.full(replicates, -np.inf, dtype=float)
    null_peak_scores: list[np.ndarray] = []
    spectral_errors = np.empty(replicates, dtype=float)
    for index in range(replicates):
        surrogate, spectral_errors[index] = iaaft_surrogate(
            trace.pressure_pa, rng, iterations
        )
        score = base.score_signal(surrogate, screen)
        peaks = candidate_peaks(score, screen)
        values = score[peaks]
        null_peak_scores.append(values)
        null_max[index] = float(np.max(values))
        if exploratory_window is not None:
            within = peaks[
                (trace.epoch_s[peaks] >= exploratory_window[0])
                & (trace.epoch_s[peaks] <= exploratory_window[1])
            ]
            if within.size:
                null_window_max[index] = float(np.max(score[within]))

    pooled = np.concatenate(null_peak_scores)
    rows = []
    ordered = sorted(observed_peaks, key=lambda item: trace.score[item], reverse=True)
    for rank, peak in enumerate(ordered, start=1):
        value = float(trace.score[peak])
        rows.append(
            {
                "station": trace.station,
                "panel": trace.panel,
                "rank_within_panel": rank,
                "peak_utc": fmt_utc(trace.epoch_s[peak]),
                "score": f"{value:.9g}",
                "empirical_panel_peak_percentile": f"{100.0 * (np.count_nonzero(observed_scores <= value) - 0.5) / observed_scores.size:.6g}",
                "iaaft_p_local_peak": f"{(1 + np.count_nonzero(pooled >= value)) / (pooled.size + 1):.9g}",
                "iaaft_p_panel_max": f"{(1 + np.count_nonzero(null_max >= value)) / (replicates + 1):.9g}",
                "status": "EXPLORATORY_PUBLICATION_TRACE_SURROGATE_TEST",
            }
        )

    result = {
        "rows": rows,
        "null_max": null_max,
        "null_max_q90": float(np.quantile(null_max, 0.90)),
        "null_max_q95": float(np.quantile(null_max, 0.95)),
        "null_max_q99": float(np.quantile(null_max, 0.99)),
        "spectral_error_median": float(np.median(spectral_errors)),
        "spectral_error_q95": float(np.quantile(spectral_errors, 0.95)),
    }
    if exploratory_window is not None:
        observed_within = observed_peaks[
            (trace.epoch_s[observed_peaks] >= exploratory_window[0])
            & (trace.epoch_s[observed_peaks] <= exploratory_window[1])
        ]
        observed_window_max = float(np.max(trace.score[observed_within]))
        result["exploratory_window"] = {
            "start_utc": fmt_utc(exploratory_window[0]),
            "end_utc": fmt_utc(exploratory_window[1]),
            "observed_max": observed_window_max,
            "observed_max_utc": fmt_utc(
                trace.epoch_s[
                    int(observed_within[np.argmax(trace.score[observed_within])])
                ]
            ),
            "p_fixed_window_max": float(
                (1 + np.count_nonzero(null_window_max >= observed_window_max))
                / (replicates + 1)
            ),
            "p_full_panel_max": float(
                (1 + np.count_nonzero(null_max >= observed_window_max))
                / (replicates + 1)
            ),
            "null_window_q90": float(np.quantile(null_window_max, 0.90)),
            "null_window_q95": float(np.quantile(null_window_max, 0.95)),
            "null_window_q99": float(np.quantile(null_window_max, 0.99)),
            "selection_warning": (
                "Window selected after visual inspection; fixed-window p is "
                "exploratory and the full-panel maximum is the safer scan control."
            ),
        }
    return result


def load_targets(configuration: dict, event_configuration: dict) -> list[dict]:
    path = HERE / configuration["source_targets_csv"]
    with path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))

    grid_row = next(row for row in rows if row["target_id"] == "integrated_pdf_mode")
    with np.load(base.GRID_PATH) as payload:
        mass = payload[base.GRID_KEY]
        area = payload["cell_area_km2"]
        latitude = payload["latitude_deg"]
        longitude = payload["longitude_deg_E"]
    mode_index = np.unravel_index(int(np.argmax(mass / area)), mass.shape)
    calculated = (float(latitude[mode_index[0]]), float(longitude[mode_index[1]]))
    pinned = (float(grid_row["latitude_deg"]), float(grid_row["longitude_deg_e"]))
    if not np.allclose(calculated, pinned, atol=1e-10):
        raise ValueError(f"Pinned integrated density mode {pinned} != {calculated}")
    if grid_row["input_sha256"] != sha256(base.GRID_PATH):
        raise ValueError("Integrated PDF input hash no longer matches pinned target")

    stations = event_configuration["stations"]
    radius = float(event_configuration["earth_radius_km"])
    central = float(configuration["central_celerity_km_s"])
    low, high = map(float, configuration["celerity_range_km_s"])
    output = []
    for row in rows:
        latitude_value = float(row["latitude_deg"])
        longitude_value = float(row["longitude_deg_e"])
        distances = {}
        for station_id, station in stations.items():
            distance = float(
                base.haversine_distance_km(
                    np.asarray(latitude_value),
                    np.asarray(longitude_value),
                    (station["latitude_deg"], station["longitude_deg_e"]),
                    radius,
                )
            )
            distances[station_id] = {
                "distance_km": distance,
                "central_travel_min": distance / central / 60.0,
                "travel_min_at_1p57": distance / high / 60.0,
                "travel_min_at_1p43": distance / low / 60.0,
            }
        output.append({**row, "distances": distances})
    return output


def method_by_name(result: dict, name: str) -> dict:
    return next(row for row in result["methods"] if row["method"] == name)


def analyse_h08_all_methods(
    panel_name: str,
    event_utc: str,
    filter_configuration: dict,
    screen: dict,
) -> dict:
    panel = overview.load_h08_panel(panel_name, filter_configuration)
    local = copy.deepcopy(filter_configuration)
    local["event_utc"] = event_utc
    geometry = airgun.fit_shot_geometry(panel, local)
    cycles = airgun.extract_and_align_cycles(panel, geometry, local)
    methods = airgun.evaluate_methods(cycles, geometry, local)
    results = {"panel": panel, "geometry": geometry, "cycles": cycles, "methods": methods}
    for rank in (8, 20):
        method = next(row for row in methods if row["method"] == f"low_rank_{rank}_shift_0.30s")
        residual = airgun.build_full_trace(panel, geometry, cycles, method["_residuals"])
        score = base.score_signal(residual, screen)
        peaks = candidate_peaks(score, screen)
        results[f"rank_{rank}"] = {
            "method": method,
            "residual": residual,
            "score": score,
            "peaks": peaks,
            "threshold": float(np.quantile(score[peaks], 0.99)),
        }
    return results


def observed_centre_mask(result: dict, half_width_s: float) -> np.ndarray:
    """Mask observed pulse centres and the immediately cropped neighbour cycles."""
    panel = result["panel"]
    geometry = result["geometry"]
    centres = np.concatenate(
        (
            [geometry.observed_centres_s[0] - geometry.fitted_period_s],
            geometry.observed_centres_s,
            [geometry.observed_centres_s[-1] + geometry.fitted_period_s],
        )
    )
    mask = np.zeros(panel.time_s.size, dtype=bool)
    for centre in centres:
        mask |= np.abs(panel.time_s - float(centre)) <= half_width_s
    return mask


def injection_recovery(
    result: dict,
    filter_configuration: dict,
    configuration: dict,
) -> list[dict]:
    """Held-out single-cycle Gaussian injection sensitivity for ranks 8 and 20."""
    injection = configuration["stronger_airgun_control"]
    rng = np.random.default_rng(int(injection["injection_seed"]))
    cycles = result["cycles"]
    geometry = result["geometry"]
    count = int(injection["injection_count"])
    amplitude = float(injection["injection_amplitude_pa"])
    sigma = float(injection["injection_sigma_s"])
    cycle_indices = rng.integers(2, cycles.values.shape[0] - 2, size=count)
    centres = rng.uniform(-2.0, 2.0, size=count)
    rows = []
    for rank in (8, 20):
        baseline, _models, _shifts = airgun.low_rank_residual_cycles(
            cycles, rank, 0.30, filter_configuration
        )
        recovered = []
        correlations = []
        for cycle_index, centre in zip(cycle_indices, centres):
            pulse = amplitude * np.exp(
                -0.5 * ((cycles.time_s - float(centre)) / sigma) ** 2
            )
            modified = airgun.CycleSet(
                time_s=cycles.time_s,
                values=cycles.values.copy(),
                aligned_values=cycles.aligned_values.copy(),
                alignment_shifts_s=cycles.alignment_shifts_s.copy(),
            )
            modified.values[cycle_index] += pulse
            modified.aligned_values[cycle_index] += pulse
            residual, _models, _shifts = airgun.low_rank_residual_cycles(
                modified, rank, 0.30, filter_configuration
            )
            delta = residual[cycle_index] - baseline[cycle_index]
            recovered.append(float(np.dot(delta, pulse) / np.dot(pulse, pulse)))
            correlations.append(
                float(np.dot(delta, pulse) / max(np.linalg.norm(delta) * np.linalg.norm(pulse), 1e-12))
            )
        rows.append(
            {
                "panel": result["panel"].panel,
                "method": f"low_rank_{rank}_shift_0.30s",
                "injection_count": count,
                "injection_amplitude_pa": amplitude,
                "injection_sigma_s": sigma,
                "amplitude_recovery_median": float(np.median(recovered)),
                "amplitude_recovery_q10": float(np.quantile(recovered, 0.10)),
                "amplitude_recovery_min": float(np.min(recovered)),
                "waveform_correlation_median": float(np.median(correlations)),
                "waveform_correlation_q10": float(np.quantile(correlations, 0.10)),
                "status": "SYNTHETIC_HELD_OUT_CYCLE_SENSITIVITY_NOT_RAW_RECEIVER_VALIDATION",
            }
        )
    return rows


def h08_control_rows(results: dict[str, dict], configuration: dict) -> list[dict]:
    half_width = float(
        configuration["stronger_airgun_control"]["observed_centre_mask_half_width_s"]
    )
    score_half_width = float(
        configuration["stronger_airgun_control"]["score_exclusion_half_width_s"]
    )
    rows = []
    for panel_name, result in results.items():
        mask = observed_centre_mask(result, half_width)
        score_mask = observed_centre_mask(result, score_half_width)
        for rank in (8, 20):
            method = result[f"rank_{rank}"]["method"]
            rows.append(
                {
                    "panel": panel_name,
                    "method": method["method"],
                    "control_median_rms_removed_fraction": f"{method['control_median_rms_removed_fraction']:.9g}",
                    "control_median_rms_retained_fraction": f"{method['control_median_rms_retained_fraction']:.9g}",
                    "observed_centre_mask_half_width_s": f"{half_width:.3f}",
                    "publication_trace_fraction_masked": f"{np.mean(mask):.9g}",
                    "score_exclusion_half_width_s": f"{score_half_width:.3f}",
                    "local_energy_score_fraction_excluded": f"{np.mean(score_mask):.9g}",
                    "status": "PUBLICATION_TRACE_FILTER_CONTROL_NOT_EVENT_CLASSIFICATION",
                }
            )
    return rows


def concatenate_h01(traces: dict[str, base.Trace]) -> tuple[np.ndarray, np.ndarray]:
    epochs = np.concatenate([traces[name].epoch_s for name in ("b", "c")])
    score = np.concatenate([traces[name].score for name in ("b", "c")])
    order = np.argsort(epochs)
    epochs = epochs[order]
    score = score[order]
    unique, index = np.unique(epochs, return_index=True)
    return unique, score[index]


def concatenate_h08(
    results: dict[str, dict], mask_half_width_s: float
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    epoch_parts = []
    score_parts = []
    mask_parts = []
    for name in ("d", "e"):
        result = results[name]
        epoch_parts.append(result["panel"].epoch_s)
        score_parts.append(result["rank_20"]["score"])
        mask_parts.append(observed_centre_mask(result, mask_half_width_s))
    epochs = np.concatenate(epoch_parts)
    score = np.concatenate(score_parts)
    mask = np.concatenate(mask_parts)
    order = np.argsort(epochs)
    epochs, score, mask = epochs[order], score[order], mask[order]
    unique, index = np.unique(epochs, return_index=True)
    return unique, score[index], mask[index]


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


def plot_h01_significance(
    configuration: dict,
    traces: dict[str, base.Trace],
    tests: dict[str, dict],
) -> list[Path]:
    windows = [
        tuple(base.parse_utc(value).timestamp() for value in configuration["h01_display_window_utc"]),
        tuple(base.parse_utc(value).timestamp() for value in configuration["h01_late_display_window_utc"]),
    ]
    figure, axes = plt.subplots(2, 1, figsize=(15.8, 9.0), sharey=False)
    for plot_index, (axis, limits) in enumerate(zip(axes, windows)):
        for panel_name, shade in (("b", "#EDF4F8"), ("c", "#F5F0F7")):
            trace = traces[panel_name]
            visible = (trace.epoch_s >= limits[0]) & (trace.epoch_s <= limits[1])
            if not np.any(visible):
                continue
            times = np.asarray([utc(value) for value in trace.epoch_s[visible]])
            axis.axvspan(times[0], times[-1], color=shade, alpha=0.70, zorder=0)
            axis.plot(times, trace.score[visible], color="#35115A", linewidth=1.55)
            axis.hlines(
                tests[panel_name]["null_max_q95"],
                times[0],
                times[-1],
                color="#B2182B",
                linestyle="--",
                linewidth=1.25,
            )
            lookup = {row["peak_utc"]: row for row in tests[panel_name]["rows"]}
            peaks = trace.candidate_indices[
                (trace.epoch_s[trace.candidate_indices] >= limits[0])
                & (trace.epoch_s[trace.candidate_indices] <= limits[1])
            ]
            for peak in peaks:
                row = lookup[fmt_utc(trace.epoch_s[peak])]
                global_p = float(row["iaaft_p_panel_max"])
                colour = "#B2182B" if global_p < 0.05 else "#2166AC"
                axis.scatter(utc(trace.epoch_s[peak]), trace.score[peak], s=35, color=colour, zorder=5)
                clock = utc(trace.epoch_s[peak]).strftime("%H:%M:%S")
                requested_labels = {
                    "00:46:07", "00:46:30", "00:46:43",
                    "00:47:14", "00:48:22", "00:49:14", "00:49:41",
                }
                late_labels = {"00:55:49", "00:56:42", "00:56:47"}
                selected = (
                    (plot_index == 0 and clock in requested_labels)
                    or (plot_index == 1 and clock in late_labels)
                )
                if selected:
                    axis.annotate(
                        f"{utc(trace.epoch_s[peak]):%H:%M:%S}\nscore {trace.score[peak]:.2f}\nscan p={global_p:.3f}",
                        (utc(trace.epoch_s[peak]), trace.score[peak]),
                        xytext=(5, 8 if peak % 2 else -34),
                        textcoords="offset points",
                        fontsize=7.4,
                        color=colour,
                    )
        axis.set_xlim(utc(limits[0]), utc(limits[1]))
        axis.set_ylabel("Local-energy score")
        axis.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M:%S", tz=timezone.utc))
        axis.grid(alpha=0.16)
    axes[0].set_title("A. Cape Leeuwin features around the visually selected 00:47–00:50 window")
    axes[1].set_title("B. Late Cape Leeuwin features near the end of Figure 9c")
    axes[1].set_xlabel("UTC on 8 March 2014")
    axes[0].legend(
        handles=[
            Line2D([0], [0], color="#35115A", linewidth=1.5, label="publication-trace local-energy score"),
            Line2D([0], [0], color="#B2182B", linestyle="--", label="IAAFT 95% full-panel maximum threshold"),
            Line2D([0], [0], marker="o", linestyle="", color="#2166AC", label="not significant after panel scan"),
            Line2D([0], [0], marker="o", linestyle="", color="#B2182B", label="p < 0.05 after panel scan"),
        ],
        loc="upper left",
        frameon=False,
        ncol=2,
    )
    figure.suptitle("Cape Leeuwin publication-trace peak and surrogate-noise controls", fontsize=15.5)
    figure.text(
        0.5,
        0.016,
        "IAAFT surrogates preserve each panel's amplitude distribution and approximate spectrum. "
        "The 00:47–00:50 interval was selected after inspection; p-values are exploratory, not receiver false-alarm rates.",
        ha="center",
        fontsize=8.5,
    )
    figure.tight_layout(rect=[0.0, 0.045, 1.0, 0.96])
    return save_figure(figure, "h01w-candidate-peak-significance")


def plot_h08_stronger_filter(
    results: dict[str, dict],
    configuration: dict,
    injection_rows: list[dict],
) -> list[Path]:
    half_width = float(configuration["stronger_airgun_control"]["observed_centre_mask_half_width_s"])
    score_half_width = float(configuration["stronger_airgun_control"]["score_exclusion_half_width_s"])
    figure, axes = plt.subplots(2, 1, figsize=(16.0, 9.2), sharey=False)
    for axis, panel_name in zip(axes, ("d", "e")):
        result = results[panel_name]
        times = np.asarray([utc(value) for value in result["panel"].epoch_s])
        mask = observed_centre_mask(result, score_half_width)
        masked_score = result["rank_20"]["score"].copy()
        masked_score[mask] = np.nan
        axis.plot(times, result["rank_8"]["score"], color="#B8B8B8", linewidth=1.0, label="rank-8 score")
        axis.plot(times, result["rank_20"]["score"], color="#8C6BB1", linewidth=0.75, alpha=0.65, label="rank-20 score before mask")
        axis.plot(times, masked_score, color="#35115A", linewidth=1.45, label="rank-20 score outside dilated pulse masks")
        for centre in result["geometry"].observed_centres_s:
            centre_epoch = result["panel"].start_epoch_s + float(centre)
            axis.axvspan(
                utc(centre_epoch - score_half_width),
                utc(centre_epoch + score_half_width),
                color="#D9D9D9",
                alpha=0.30,
                linewidth=0,
            )
        primary = result["rank_8"]["method"]
        stronger = result["rank_20"]["method"]
        axis.set_title(
            f"{panel_name.upper()}: median control-pulse RMS removed "
            f"{100*primary['control_median_rms_removed_fraction']:.1f}% (rank 8) versus "
            f"{100*stronger['control_median_rms_removed_fraction']:.1f}% (rank 20)"
        )
        axis.set_ylabel("Residual local-energy score")
        axis.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M", tz=timezone.utc))
        axis.grid(alpha=0.15)
    axes[-1].set_xlabel("UTC on 8 March 2014")
    axes[0].legend(loc="upper left", frameon=False, ncol=3)
    panel_d_rows = {row["method"]: row for row in injection_rows if row["panel"] == "d"}
    rank8 = panel_d_rows["low_rank_8_shift_0.30s"]
    rank20 = panel_d_rows["low_rank_20_shift_0.30s"]
    figure.suptitle("Diego Garcia stronger periodic-airgun suppression sensitivity", fontsize=15.5)
    figure.text(
        0.5,
        0.014,
        f"Grey gaps exclude scores within ±{score_half_width:.1f} s of observed pulse centres: the ±{half_width:.1f} s raw-pressure mask plus "
        "the 2 s half-width of the longest energy window.\nIn the synthetic held-out-cycle control, "
        f"median injected-amplitude recovery falls from {100*rank8['amplitude_recovery_median']:.0f}% at rank 8 to "
        f"{100*rank20['amplitude_recovery_median']:.0f}% at rank 20; stronger suppression can erase real coincident energy.",
        ha="center",
        fontsize=8.5,
    )
    figure.tight_layout(rect=[0.0, 0.045, 1.0, 0.96])
    return save_figure(figure, "h08s-stronger-airgun-suppression-control")


def plot_aligned_target(
    target: dict,
    h01_epoch: np.ndarray,
    h01_score: np.ndarray,
    h08_epoch: np.ndarray,
    h08_score: np.ndarray,
    h08_mask: np.ndarray,
    configuration: dict,
) -> list[Path]:
    central = float(configuration["central_celerity_km_s"])
    distances = target["distances"]
    h01_source = h01_epoch - distances["H01W"]["distance_km"] / central
    h08_source = h08_epoch - distances["H08S"]["distance_km"] / central
    masked_h08 = h08_score.copy()
    masked_h08[h08_mask] = np.nan
    minimum = min(float(np.min(h01_source)), float(np.min(h08_source)))
    maximum = max(float(np.max(h01_source)), float(np.max(h08_source)))
    figure, axes = plt.subplots(2, 1, figsize=(16.2, 8.7), sharex=True)
    axes[0].plot([utc(value) for value in h01_source], h01_score, color="#35115A", linewidth=1.35)
    axes[0].set_title(
        f"A. Cape Leeuwin H01W — {distances['H01W']['distance_km']:,.0f} km; "
        f"central travel {distances['H01W']['central_travel_min']:.2f} min"
    )
    axes[1].plot([utc(value) for value in h08_source], h08_score, color="#B8B8B8", linewidth=0.65)
    axes[1].plot([utc(value) for value in h08_source], masked_h08, color="#35115A", linewidth=1.25)
    axes[1].set_title(
        f"B. Diego Garcia H08S — {distances['H08S']['distance_km']:,.0f} km; "
        f"central travel {distances['H08S']['central_travel_min']:.2f} min; rank-20 residual with ±3 s score gaps"
    )
    for axis in axes:
        axis.axvspan(
            base.parse_utc("2014-03-08T00:19:37Z"),
            base.parse_utc("2014-03-08T00:49:37Z"),
            color="#D9EAD3",
            alpha=0.34,
            zorder=0,
        )
        axis.set_xlim(utc(minimum), utc(maximum))
        axis.set_ylabel("Local-energy score")
        axis.grid(alpha=0.15)
    axes[-1].xaxis.set_major_formatter(mdates.DateFormatter("%H:%M", tz=timezone.utc))
    axes[-1].set_xlabel("Implied source/impact UTC at 1.50 km s⁻¹")
    low, high = map(float, configuration["celerity_range_km_s"])
    figure.suptitle(
        f"Conditional source-time alignment at {target['label']}\n"
        f"{abs(float(target['latitude_deg'])):.4f}°S, {float(target['longitude_deg_e']):.4f}°E",
        fontsize=15.0,
    )
    figure.text(
        0.5,
        0.014,
        f"Central alignment uses 1.50 km s⁻¹; {low:.2f}–{high:.2f} km s⁻¹ changes each station's shift by minutes. "
        "Green is the declared 00:19:37–00:49:37 source-time control. Horizontal coincidence is a visual screen, not association evidence.",
        ha="center",
        fontsize=8.4,
    )
    figure.tight_layout(rect=[0.0, 0.052, 1.0, 0.93])
    return save_figure(figure, f"aligned-local-energy-{target['target_id'].replace('_', '-')}")


def alignment_rows(targets: list[dict], configuration: dict) -> list[dict]:
    rows = []
    for target in targets:
        for station, values in target["distances"].items():
            rows.append(
                {
                    "target_id": target["target_id"],
                    "target_label": target["label"],
                    "target_latitude_deg": target["latitude_deg"],
                    "target_longitude_deg_e": target["longitude_deg_e"],
                    "target_status": target["status"],
                    "station": station,
                    "distance_km": f"{values['distance_km']:.6f}",
                    "travel_min_at_1p50": f"{values['central_travel_min']:.6f}",
                    "travel_min_at_1p57": f"{values['travel_min_at_1p57']:.6f}",
                    "travel_min_at_1p43": f"{values['travel_min_at_1p43']:.6f}",
                    "alignment_status": "CONDITIONAL_POINT_AND_CELERITY_TIME_SHIFT_NOT_EVENT_ASSOCIATION",
                }
            )
    return rows


def main() -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    configuration = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    event_configuration = json.loads(EVENT_CONFIG_PATH.read_text(encoding="utf-8"))
    filter_configuration = json.loads(FILTER_CONFIG_PATH.read_text(encoding="utf-8"))
    filter_configuration = copy.deepcopy(filter_configuration)
    filter_configuration["low_rank_values"] = [8, 20]
    traces = base.load_traces(event_configuration)
    screen = event_configuration["trace_screen"]

    rng = np.random.default_rng(int(configuration["random_seed"]))
    window = tuple(
        base.parse_utc(value).timestamp()
        for value in configuration["exploratory_h01_window_utc"]
    )
    tests = {
        "b": surrogate_panel_test(
            traces["b"], screen, rng, int(configuration["iaaft_replicates"]), int(configuration["iaaft_iterations"])
        ),
        "c": surrogate_panel_test(
            traces["c"], screen, rng, int(configuration["iaaft_replicates"]), int(configuration["iaaft_iterations"]), window
        ),
    }
    significance_rows = tests["b"]["rows"] + tests["c"]["rows"]
    significance_path = OUTPUT / "h01w-publication-trace-significance.csv"
    write_csv(significance_path, significance_rows)

    h08_events = {"d": "2014-03-08T01:03:13.150Z", "e": "2014-03-08T01:12:49.500Z"}
    h08_results = {
        name: analyse_h08_all_methods(name, event, filter_configuration, screen)
        for name, event in h08_events.items()
    }
    controls = h08_control_rows(h08_results, configuration)
    controls_path = OUTPUT / "h08s-stronger-filter-controls.csv"
    write_csv(controls_path, controls)
    injection = []
    for name in ("d", "e"):
        injection.extend(
            injection_recovery(h08_results[name], filter_configuration, configuration)
        )
    injection_path = OUTPUT / "h08s-filter-injection-recovery.csv"
    write_csv(injection_path, injection)

    targets = load_targets(configuration, event_configuration)
    alignment_path = OUTPUT / "source-time-alignment-targets.csv"
    write_csv(alignment_path, alignment_rows(targets, configuration))
    h01_epoch, h01_score = concatenate_h01(traces)
    mask_half = float(configuration["stronger_airgun_control"]["observed_centre_mask_half_width_s"])
    score_mask_half = float(configuration["stronger_airgun_control"]["score_exclusion_half_width_s"])
    h08_epoch, h08_score, h08_mask = concatenate_h08(h08_results, score_mask_half)

    paths: list[Path] = [significance_path, controls_path, injection_path, alignment_path]
    paths.extend(plot_h01_significance(configuration, traces, tests))
    paths.extend(plot_h08_stronger_filter(h08_results, configuration, injection))
    for target in targets:
        paths.extend(
            plot_aligned_target(
                target, h01_epoch, h01_score, h08_epoch, h08_score, h08_mask, configuration
            )
        )

    summary = {
        "status": "EXPLORATORY_PUBLICATION_TRACE_CONTROLS_NOT_EVENT_ASSOCIATIONS",
        "h01w_surrogate_test": {
            "null": configuration["iaaft_null"],
            "replicates": configuration["iaaft_replicates"],
            "iterations": configuration["iaaft_iterations"],
            "panel_b_full_scan_thresholds": {
                key: tests["b"][key] for key in ("null_max_q90", "null_max_q95", "null_max_q99")
            },
            "panel_c_full_scan_thresholds": {
                key: tests["c"][key] for key in ("null_max_q90", "null_max_q95", "null_max_q99")
            },
            "panel_c_exploratory_window": tests["c"]["exploratory_window"],
            "spectral_error": {
                panel: {
                    "median": tests[panel]["spectral_error_median"],
                    "q95": tests[panel]["spectral_error_q95"],
                }
                for panel in ("b", "c")
            },
        },
        "stronger_h08s_control": {
            "rank_8_is_primary_held_out_control_selection": True,
            "rank_20_is_sensitivity_only": True,
            "mask_half_width_s": mask_half,
            "score_exclusion_half_width_s": score_mask_half,
            "filter_controls": controls,
            "injection_controls": injection,
        },
        "source_time_alignment": {
            "central_celerity_km_s": configuration["central_celerity_km_s"],
            "celerity_range_km_s": configuration["celerity_range_km_s"],
            "targets": alignment_rows(targets, configuration),
        },
        "limits": [
            "inputs are already-filtered publication-figure vectors, not raw multi-channel CTBTO data",
            "IAAFT p-values test a stationary surrogate null for the plotted trace and are not receiver false-alarm probabilities",
            "the 00:47–00:50 interval was selected after visual inspection, making its fixed-window p exploratory",
            "source-mode and 1.50 km/s shifts are conditional visual alignments, not measured cross-station associations",
            "rank-20 airgun suppression removes more periodic energy but attenuates synthetic transients more than rank 8",
        ],
    }
    summary_path = OUTPUT / "aligned-detection-analysis-summary.json"
    summary_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    paths.append(summary_path)

    manifest = {
        "status": "REPRODUCIBLE_OUTPUT_HASHES",
        "inputs": {
            str(CONFIG_PATH.relative_to(HERE)): sha256(CONFIG_PATH),
            str(EVENT_CONFIG_PATH.relative_to(HERE)): sha256(EVENT_CONFIG_PATH),
            str(FILTER_CONFIG_PATH.relative_to(HERE)): sha256(FILTER_CONFIG_PATH),
            str((HERE / configuration["source_targets_csv"]).relative_to(HERE)): sha256(HERE / configuration["source_targets_csv"]),
            "data/kadri-figure-extraction/metadata.json": sha256(base.METADATA_PATH),
            "data/posterior_grids.npz": sha256(base.GRID_PATH),
        },
        "code": {
            str(Path(__file__).relative_to(HERE)): sha256(Path(__file__)),
            "code/event_pair_analysis.py": sha256(Path(base.__file__)),
            "code/filter_sensitivity.py": sha256(Path(airgun.__file__)),
            "code/publication_trace_score_overview.py": sha256(Path(overview.__file__)),
        },
        "outputs": {path.name: sha256(path) for path in paths},
    }
    manifest_path = OUTPUT / "aligned-detection-analysis-manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
