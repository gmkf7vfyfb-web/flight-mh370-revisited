#!/usr/bin/env python3
"""Boundary-aware audit of the apparent OSCAR H01W-H08S source-time match.

This control uses vector-extracted, already-filtered Kadri Figure 9 traces. It
does not reproduce raw CTBTO detection, bearing estimation or event association.
"""

from __future__ import annotations

import copy
import csv
import hashlib
import json
import math
import sys
from datetime import datetime, timezone
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

HERE = Path(__file__).resolve().parents[1]
DATA = HERE / "data"
OUTPUT = HERE / "outputs"
CONFIG_PATH = DATA / "oscar-boundary-audit-config.json"
EVENT_CONFIG_PATH = DATA / "event-pair-analysis-config.json"
FILTER_CONFIG_PATH = DATA / "filter-sensitivity-config.json"
ALIGN_CONFIG_PATH = DATA / "aligned-detection-config.json"
TARGET_PATH = DATA / "acoustic-alignment-source-targets.csv"
SIGNIFICANCE_PATH = OUTPUT / "h01w-publication-trace-significance.csv"
PDF_METADATA = {"CreationDate": None, "ModDate": None}

sys.path.insert(0, str(HERE / "code"))
import aligned_detection_analysis as aligned
import event_pair_analysis as base


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def iso_utc(epoch_s: float) -> str:
    return (
        datetime.fromtimestamp(float(epoch_s), timezone.utc)
        .isoformat(timespec="milliseconds")
        .replace("+00:00", "Z")
    )


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        raise ValueError(f"No rows supplied for {path}")
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


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


def forward_multiscale_score(
    values: np.ndarray,
    dt: float,
    widths_s: list[float],
    core_edge_s: float,
) -> tuple[np.ndarray, list[dict]]:
    components = []
    metadata = []
    duration_s = (values.size - 1) * dt
    squared_sum = np.concatenate(([0.0], np.cumsum(values * values)))
    for width_s in widths_s:
        count = int(round(width_s / dt))
        energy = (squared_sum[count:] - squared_sum[:-count]) / count
        rms = np.sqrt(np.maximum(energy, 0.0))
        start_s = np.arange(rms.size) * dt
        core = (
            (start_s >= core_edge_s)
            & (start_s + width_s <= duration_s - core_edge_s)
        )
        centre = float(np.median(rms[core]))
        scale = float(1.4826 * np.median(np.abs(rms[core] - centre)))
        score = np.full(values.size, np.nan)
        score[: rms.size] = (rms - centre) / max(scale, 1e-12)
        components.append(score)
        metadata.append(
            {
                "width_s": float(width_s),
                "robust_centre_rms_pa": centre,
                "robust_mad_sigma_pa": scale,
            }
        )
    stack = np.vstack(components)
    score = np.full(values.size, np.nan)
    supported = np.any(np.isfinite(stack), axis=0)
    score[supported] = np.nanmax(stack[:, supported], axis=0)
    return score, metadata


def initial_bearing_deg(
    start_latitude_deg: float,
    start_longitude_deg: float,
    end_latitude_deg: float,
    end_longitude_deg: float,
) -> float:
    latitude_1 = math.radians(start_latitude_deg)
    latitude_2 = math.radians(end_latitude_deg)
    delta_longitude = math.radians(end_longitude_deg - start_longitude_deg)
    y = math.sin(delta_longitude) * math.cos(latitude_2)
    x = (
        math.cos(latitude_1) * math.sin(latitude_2)
        - math.sin(latitude_1)
        * math.cos(latitude_2)
        * math.cos(delta_longitude)
    )
    return (math.degrees(math.atan2(y, x)) + 360.0) % 360.0


def circular_difference_deg(first: float, second: float) -> float:
    return abs((first - second + 180.0) % 360.0 - 180.0)


def robust_predecessor_fit(
    geometry,
    seed: int,
    replicates: int,
    minimum_half_width_s: float,
) -> dict:
    numbers = geometry.cycle_numbers.astype(float)
    observed = geometry.observed_centres_s.astype(float)
    predicted = geometry.fitted_intercept_s + geometry.fitted_period_s * numbers
    residual = observed - predicted
    centre = float(np.median(residual))
    scale = float(1.4826 * np.median(np.abs(residual - centre)))
    keep = np.abs(residual - centre) <= max(minimum_half_width_s, 3.5 * scale)
    keep[int(geometry.target_cycle_index)] = False
    x = numbers[keep]
    y = observed[keep]
    design = np.column_stack((np.ones(x.size), x))
    coefficients = np.linalg.lstsq(design, y, rcond=None)[0]
    fitted = design @ coefficients
    fit_residual = y - fitted
    predecessor_number = float(np.min(numbers) - 1.0)
    predecessor = float(coefficients @ np.asarray([1.0, predecessor_number]))
    rng = np.random.default_rng(seed)
    draws = np.empty(replicates)
    for index in range(replicates):
        simulated = fitted + rng.choice(fit_residual, size=fit_residual.size, replace=True)
        draw_coefficients = np.linalg.lstsq(design, simulated, rcond=None)[0]
        draws[index] = draw_coefficients @ np.asarray([1.0, predecessor_number])
    return {
        "retained_centre_count": int(x.size),
        "intercept_s": float(coefficients[0]),
        "period_s": float(coefficients[1]),
        "predecessor_centre_s": predecessor,
        "predecessor_centre_q025_s": float(np.quantile(draws, 0.025)),
        "predecessor_centre_q50_s": float(np.quantile(draws, 0.50)),
        "predecessor_centre_q975_s": float(np.quantile(draws, 0.975)),
        "probability_centre_within_half_second_of_boundary": float(
            np.mean(np.abs(draws) <= 0.5)
        ),
        "residual_rms_s": float(np.sqrt(np.mean(fit_residual * fit_residual))),
    }


def h01_significance(candidate_utc: str) -> dict:
    with SIGNIFICANCE_PATH.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    row = min(
        rows,
        key=lambda item: abs(
            base.parse_utc(item["peak_utc"]).timestamp()
            - base.parse_utc(candidate_utc).timestamp()
        ),
    )
    return row


def metric_rows(summary: dict) -> list[dict]:
    values = [
        ("observed_interstation_lag", summary["timing"]["observed_interstation_lag_s"], "s", "H08S peak minus H01W peak"),
        ("oscar_predicted_interstation_lag", summary["timing"]["oscar_predicted_interstation_lag_s"], "s", "OSCAR point mode at central celerity"),
        ("source_time_offset", summary["timing"]["source_time_offset_s"], "s", "H08S implied source time minus H01W"),
        ("pair_implied_celerity", summary["timing"]["pair_implied_celerity_km_s"], "km s^-1", "Distance difference divided by observed lag"),
        ("central_expected_h08_panel_time", summary["timing"]["central_expected_h08_panel_time_s"], "s", "Seconds after Figure 9e begins"),
        ("fitted_airgun_period", summary["cadence"]["fitted_period_s"], "s", "Interior panel-e periodic fit"),
        ("fitted_predecessor_centre", summary["cadence"]["fitted_predecessor_centre_s"], "s", "Extrapolated from original cadence fit"),
        ("robust_predecessor_centre", summary["cadence"]["robust_predecessor_centre_s"], "s", "Robust refit after cycle extraction"),
        ("robust_predecessor_q025", summary["cadence"]["robust_predecessor_q025_s"], "s", "Residual-bootstrap lower bound"),
        ("robust_predecessor_q975", summary["cadence"]["robust_predecessor_q975_s"], "s", "Residual-bootstrap upper bound"),
        ("boundary_forward_score", summary["energy_control"]["boundary_forward_score"], "dimensionless", "Fully supported forward score at panel start"),
        ("boundary_forward_point_percentile", 100.0 * summary["energy_control"]["boundary_forward_point_percentile"], "%", "Against all supported starts"),
        ("expected_window_maximum_score", summary["energy_control"]["expected_window_maximum_score"], "dimensionless", "Maximum in central expected arrival +/- tolerance"),
        ("matched_ten_second_window_p", summary["energy_control"]["matched_ten_second_window_p"], "probability", "Overlapping interior ten-second controls"),
        ("cycle_window_p", summary["energy_control"]["cycle_window_p"], "probability", "Interior airgun-cycle ten-second controls"),
        ("periodic_phase_probability", summary["energy_control"]["periodic_phase_probability"], "probability", "Random phase chance of a pulse within the observed offset"),
        ("boundary_four_second_rms_percentile_among_pulses", 100.0 * summary["energy_control"]["boundary_four_second_rms_percentile_among_pulses"], "%", "Raw boundary segment versus interior pulse tails"),
        ("h01_panel_max_surrogate_p", summary["h01w"]["iaaft_panel_max_p"], "probability", "Existing publication-trace IAAFT control"),
        ("oscar_expected_h01w_bearing", summary["h01w"]["oscar_expected_bearing_deg"], "deg", "Initial great-circle bearing"),
        ("reported_nearby_h01w_bearing", summary["h01w"]["source_reported_bearing_deg"], "deg", "Kadri Figure 9 rectangle 1"),
        ("bearing_difference", summary["h01w"]["bearing_difference_deg"], "deg", "Circular absolute difference"),
    ]
    return [
        {
            "metric": name,
            "value": f"{float(value):.9g}",
            "unit": unit,
            "interpretation": interpretation,
        }
        for name, value, unit, interpretation in values
    ]


def make_plot(
    panel,
    result: dict,
    forward_score: np.ndarray,
    expected_lower_s: float,
    expected_upper_s: float,
    expected_maximum: float,
    expected_maximum_time_s: float,
    control_maxima: np.ndarray,
    fitted_predecessor_s: float,
    cadence: dict,
    observed_boundary_peak_s: float,
    central_expected_s: float,
    matched_p: float,
) -> list[Path]:
    time = panel.time_s
    rank_20 = result["rank_20"]["residual"]
    geometry = result["geometry"]
    figure, axes = plt.subplots(3, 1, figsize=(15.8, 11.2))

    visible = (time >= 0.0) & (time <= 15.0)
    axes[0].plot(time[visible], panel.pressure_pa[visible], color="#A6A6A6", linewidth=1.0, label="publication pressure")
    axes[0].plot(time[visible], rank_20[visible], color="#35115A", linewidth=1.15, label="rank-20 output")
    axes[0].axvspan(
        cadence["predecessor_centre_q025_s"],
        cadence["predecessor_centre_q975_s"],
        color="#E08214",
        alpha=0.20,
        label="predecessor-centre bootstrap 95%",
    )
    axes[0].axvline(fitted_predecessor_s, color="#E08214", linestyle="--", linewidth=1.3)
    axes[0].axvline(observed_boundary_peak_s, color="#762A83", linestyle=":", linewidth=1.4, label="displayed edge-score peak")
    axes[0].axvline(central_expected_s, color="#1B7837", linestyle="-.", linewidth=1.4, label="central OSCAR expected arrival")
    axes[0].axvline(float(geometry.observed_centres_s[0]), color="#B2182B", linestyle="--", linewidth=1.2, label="first observed interior airgun centre")
    axes[0].set_xlim(-0.45, 15.0)
    axes[0].set_ylabel("Pressure (Pa)")
    axes[0].set_title("A. The rank-20 filter does not alter the cropped first segment; the periodic predecessor is fitted at the boundary")
    axes[0].legend(loc="upper right", ncol=2, fontsize=7.6, frameon=False)
    axes[0].grid(alpha=0.14)

    visible = (time >= 0.0) & (time <= 60.0)
    axes[1].plot(time[visible], forward_score[visible], color="#35115A", linewidth=1.25)
    axes[1].axvspan(expected_lower_s, expected_upper_s, color="#D9EAD3", alpha=0.55, label="central OSCAR arrival +/-5 s")
    extended_centres = np.concatenate(
        (
            [geometry.observed_centres_s[0] - geometry.fitted_period_s],
            geometry.observed_centres_s,
        )
    )
    for centre in extended_centres:
        if -1.0 <= centre <= 60.0:
            axes[1].axvline(float(centre), color="#B2182B", alpha=0.34, linewidth=0.8)
    axes[1].scatter(
        [expected_maximum_time_s],
        [expected_maximum],
        color="#1B7837",
        s=44,
        zorder=5,
        label=f"window maximum {expected_maximum:.2f}",
    )
    axes[1].set_xlim(-0.45, 60.0)
    axes[1].set_ylabel("Forward energy score")
    axes[1].set_title("B. Fully supported one-sided energy: the window includes the extrapolated boundary mask and the next observed shot")
    axes[1].legend(loc="upper right", frameon=False, fontsize=8.0)
    axes[1].grid(alpha=0.14)

    axes[2].hist(control_maxima, bins=24, color="#9ECAE1", edgecolor="white", alpha=0.95)
    axes[2].axvline(
        expected_maximum,
        color="#1B7837",
        linewidth=2.0,
        label=f"OSCAR +/-5 s window maximum; empirical p = {matched_p:.3f}",
    )
    axes[2].set_xlabel("Maximum forward-energy score in a ten-second control window")
    axes[2].set_ylabel("Control-window count")
    axes[2].set_title("C. Matched-window null: the apparent H08S energy is not unusual within panel e")
    axes[2].legend(loc="upper right", frameon=False, fontsize=8.3)
    axes[2].grid(axis="y", alpha=0.14)

    figure.suptitle(
        "OSCAR H01W-H08S boundary-aware coincidence audit",
        fontsize=15.8,
    )
    figure.text(
        0.5,
        0.013,
        "Already-filtered Figure 9 vectors, not raw CTBTO channels. Forward windows use only observed samples; "
        "pulse cadence is fitted from interior panel-e shots. Scores are screening statistics, not false-alarm probabilities.",
        ha="center",
        fontsize=8.3,
    )
    figure.tight_layout(rect=[0.0, 0.045, 1.0, 0.955])
    return save_figure(figure, "oscar-boundary-aware-coincidence-audit")


def main() -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    configuration = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    event_configuration = json.loads(EVENT_CONFIG_PATH.read_text(encoding="utf-8"))
    filter_configuration = json.loads(FILTER_CONFIG_PATH.read_text(encoding="utf-8"))
    alignment_configuration = json.loads(ALIGN_CONFIG_PATH.read_text(encoding="utf-8"))
    filter_configuration = copy.deepcopy(filter_configuration)
    filter_configuration["low_rank_values"] = [8, 20]

    traces = base.load_traces(event_configuration)
    targets = aligned.load_targets(alignment_configuration, event_configuration)
    target = next(row for row in targets if row["target_id"] == configuration["target_id"])
    result = aligned.analyse_h08_all_methods(
        "e",
        "2014-03-08T01:12:49.500Z",
        filter_configuration,
        event_configuration["trace_screen"],
    )
    panel = result["panel"]
    geometry = result["geometry"]
    dt = float(event_configuration["trace_screen"]["regular_grid_dt_s"])

    h01_epoch = base.parse_utc(configuration["h01w_candidate_utc"]).timestamp()
    h08_epoch = base.parse_utc(configuration["h08s_boundary_peak_utc"]).timestamp()
    observed_lag_s = h08_epoch - h01_epoch
    distance_difference_km = (
        target["distances"]["H08S"]["distance_km"]
        - target["distances"]["H01W"]["distance_km"]
    )
    central_celerity = float(configuration["central_celerity_km_s"])
    predicted_lag_s = distance_difference_km / central_celerity
    source_offset_s = observed_lag_s - predicted_lag_s
    implied_celerity = distance_difference_km / observed_lag_s
    panel_start_minus_h01_s = panel.start_epoch_s - h01_epoch
    central_expected_s = predicted_lag_s - panel_start_minus_h01_s
    tolerance_s = float(configuration["central_arrival_tolerance_s"])
    expected_lower_s = max(0.0, central_expected_s - tolerance_s)
    expected_upper_s = min(panel.time_s[-1], central_expected_s + tolerance_s)
    celerity_low, celerity_high = map(float, configuration["celerity_range_km_s"])
    celerity_arrival_lower_s = (
        distance_difference_km / celerity_high - panel_start_minus_h01_s
    )
    celerity_arrival_upper_s = (
        distance_difference_km / celerity_low - panel_start_minus_h01_s
    )

    observed_boundary_peak_s = h08_epoch - panel.start_epoch_s
    boundary_index = int(round(observed_boundary_peak_s / dt))
    fitted_predecessor_s = float(
        geometry.fitted_intercept_s
        + geometry.fitted_period_s * (float(np.min(geometry.cycle_numbers)) - 1.0)
    )
    cadence = robust_predecessor_fit(
        geometry,
        int(configuration["cadence_bootstrap_seed"]),
        int(configuration["cadence_bootstrap_replicates"]),
        float(configuration["robust_cadence_minimum_residual_half_width_s"]),
    )
    cadence_summary = {
        "fitted_period_s": float(geometry.fitted_period_s),
        "fitted_predecessor_centre_s": fitted_predecessor_s,
        "robust_predecessor_centre_s": cadence["predecessor_centre_s"],
        "robust_predecessor_q025_s": cadence["predecessor_centre_q025_s"],
        "robust_predecessor_q50_s": cadence["predecessor_centre_q50_s"],
        "robust_predecessor_q975_s": cadence["predecessor_centre_q975_s"],
        "robust_retained_centre_count": cadence["retained_centre_count"],
        "robust_fit_residual_rms_s": cadence["residual_rms_s"],
        "probability_centre_within_half_second_of_boundary": cadence[
            "probability_centre_within_half_second_of_boundary"
        ],
        "displayed_peak_delay_after_fitted_predecessor_s": (
            observed_boundary_peak_s - fitted_predecessor_s
        ),
    }

    forward_score, forward_metadata = forward_multiscale_score(
        panel.pressure_pa,
        dt,
        [float(value) for value in configuration["forward_energy_windows_s"]],
        float(configuration["forward_score_core_edge_s"]),
    )
    supported = np.isfinite(forward_score)
    boundary_forward_score = float(forward_score[0])
    boundary_point_percentile = float(
        np.mean(forward_score[supported] <= boundary_forward_score)
    )
    expected = (
        (panel.time_s >= expected_lower_s)
        & (panel.time_s <= expected_upper_s)
        & supported
    )
    expected_indices = np.flatnonzero(expected)
    expected_best_index = int(expected_indices[np.argmax(forward_score[expected_indices])])
    expected_maximum = float(forward_score[expected_best_index])
    expected_maximum_time_s = float(panel.time_s[expected_best_index])

    control_window_s = float(configuration["matched_control_window_s"])
    control_step_s = float(configuration["matched_control_step_s"])
    control_starts = np.arange(
        float(configuration["forward_score_core_edge_s"]),
        panel.time_s[-1]
        - float(configuration["forward_score_core_edge_s"])
        - control_window_s,
        control_step_s,
    )
    control_rows = []
    control_maxima = []
    for start_s in control_starts:
        within = (
            (panel.time_s >= start_s)
            & (panel.time_s <= start_s + control_window_s)
            & supported
        )
        maximum = float(np.max(forward_score[within]))
        control_maxima.append(maximum)
        control_rows.append(
            {
                "window_start_s": f"{start_s:.3f}",
                "window_end_s": f"{start_s + control_window_s:.3f}",
                "maximum_forward_energy_score": f"{maximum:.9g}",
                "at_least_oscar_window_maximum": bool(maximum >= expected_maximum),
                "status": "OVERLAPPING_INTERIOR_MATCHED_WINDOW_CONTROL",
            }
        )
    control_maxima_array = np.asarray(control_maxima)
    matched_p = float(np.mean(control_maxima_array >= expected_maximum))

    cycle_maxima = []
    for centre in geometry.observed_centres_s:
        if (
            centre - control_window_s / 2.0
            < float(configuration["forward_score_core_edge_s"])
            or centre + control_window_s / 2.0
            > panel.time_s[-1] - float(configuration["forward_score_core_edge_s"])
        ):
            continue
        within = (
            (panel.time_s >= centre - control_window_s / 2.0)
            & (panel.time_s <= centre + control_window_s / 2.0)
            & supported
        )
        cycle_maxima.append(float(np.max(forward_score[within])))
    cycle_p = float(np.mean(np.asarray(cycle_maxima) >= expected_maximum))

    phase_probability = min(
        1.0,
        2.0 * abs(source_offset_s) / float(geometry.fitted_period_s),
    )
    tolerance_phase_probability = min(
        1.0,
        2.0 * tolerance_s / float(geometry.fitted_period_s),
    )

    phase_after_centre_s = -fitted_predecessor_s
    duration_s = 4.0
    segment_time = np.arange(0.0, duration_s, dt)
    boundary_segment = np.interp(segment_time, panel.time_s, panel.pressure_pa)
    pulse_segments = []
    for centre in geometry.observed_centres_s:
        sample_time = centre + phase_after_centre_s + segment_time
        if sample_time[-1] <= panel.time_s[-1]:
            pulse_segments.append(np.interp(sample_time, panel.time_s, panel.pressure_pa))
    pulse_segments_array = np.asarray(pulse_segments)
    boundary_rms = float(np.sqrt(np.mean(boundary_segment * boundary_segment)))
    pulse_rms = np.sqrt(np.mean(pulse_segments_array * pulse_segments_array, axis=1))
    boundary_rms_percentile = float(np.mean(pulse_rms <= boundary_rms))
    template = np.median(pulse_segments_array, axis=0)
    boundary_centre = boundary_segment - np.mean(boundary_segment)
    template_centre = template - np.mean(template)
    waveform_correlation = float(
        np.dot(boundary_centre, template_centre)
        / max(
            math.sqrt(
                float(np.dot(boundary_centre, boundary_centre))
                * float(np.dot(template_centre, template_centre))
            ),
            1e-12,
        )
    )

    corrected_mask = aligned.observed_centre_mask(
        result, float(configuration["airgun_score_mask_half_width_s"])
    )
    first_four = panel.time_s <= 4.0
    boundary_filter_maximum_change_pa = float(
        np.max(
            np.abs(
                result["rank_20"]["residual"][first_four]
                - panel.pressure_pa[first_four]
            )
        )
    )

    source_bearing = float(
        configuration["source_reported_h01w_signal"]["bearing_deg"]
    )
    station = event_configuration["stations"]["H01W"]
    oscar_bearing = initial_bearing_deg(
        float(station["latitude_deg"]),
        float(station["longitude_deg_e"]),
        float(target["latitude_deg"]),
        float(target["longitude_deg_e"]),
    )
    significance = h01_significance(configuration["h01w_candidate_utc"])

    visible_celerity_upper_s = min(panel.time_s[-1], celerity_arrival_upper_s)
    extended_pulse_centres = np.concatenate(
        (
            [fitted_predecessor_s],
            geometry.predicted_centres_s,
        )
    )
    pulse_count_in_visible_celerity_window = int(
        np.count_nonzero(
            (extended_pulse_centres >= max(0.0, celerity_arrival_lower_s))
            & (extended_pulse_centres <= visible_celerity_upper_s)
        )
    )

    summary = {
        "status": "WORTHY_OF_RAW_DATA_FOLLOWUP_BUT_NOT_SIGNIFICANT_IN_BOUNDARY_MATCHED_PUBLICATION_TRACE_CONTROL",
        "timing": {
            "h01w_arrival_utc": configuration["h01w_candidate_utc"],
            "h08s_arrival_utc": configuration["h08s_boundary_peak_utc"],
            "observed_interstation_lag_s": observed_lag_s,
            "oscar_distance_difference_km": distance_difference_km,
            "oscar_predicted_interstation_lag_s": predicted_lag_s,
            "source_time_offset_s": source_offset_s,
            "pair_implied_celerity_km_s": implied_celerity,
            "central_expected_h08_panel_time_s": central_expected_s,
            "central_expected_window_s": [expected_lower_s, expected_upper_s],
            "celerity_range_h08_panel_time_s": [
                celerity_arrival_lower_s,
                celerity_arrival_upper_s,
            ],
            "visible_periodic_centres_in_celerity_window": pulse_count_in_visible_celerity_window,
        },
        "cadence": cadence_summary,
        "energy_control": {
            "original_symmetric_rank20_score_at_boundary_peak": float(
                result["rank_20"]["score"][boundary_index]
            ),
            "corrected_extended_airgun_mask_at_boundary_peak": bool(
                corrected_mask[boundary_index]
            ),
            "rank20_maximum_pressure_change_in_first_four_seconds_pa": boundary_filter_maximum_change_pa,
            "forward_score_definition": (
                "maximum robust z-score of fully supported forward RMS over "
                + ", ".join(
                    f"{float(value):g} s"
                    for value in configuration["forward_energy_windows_s"]
                )
                + " windows"
            ),
            "forward_component_calibration": forward_metadata,
            "boundary_forward_score": boundary_forward_score,
            "boundary_forward_point_percentile": boundary_point_percentile,
            "expected_window_maximum_score": expected_maximum,
            "expected_window_maximum_time_s": expected_maximum_time_s,
            "matched_ten_second_control_count": int(control_maxima_array.size),
            "matched_ten_second_window_p": matched_p,
            "cycle_window_control_count": int(len(cycle_maxima)),
            "cycle_window_p": cycle_p,
            "periodic_phase_probability": phase_probability,
            "five_second_tolerance_periodic_phase_probability": tolerance_phase_probability,
            "boundary_four_second_rms_pa": boundary_rms,
            "boundary_four_second_rms_percentile_among_pulses": boundary_rms_percentile,
            "boundary_to_median_pulse_tail_waveform_correlation": waveform_correlation,
        },
        "h01w": {
            "local_energy_score": float(significance["score"]),
            "iaaft_panel_max_p": float(significance["iaaft_p_panel_max"]),
            "nearest_source_reported_signal": configuration[
                "source_reported_h01w_signal"
            ],
            "oscar_expected_bearing_deg": oscar_bearing,
            "source_reported_bearing_deg": source_bearing,
            "bearing_difference_deg": circular_difference_deg(
                oscar_bearing, source_bearing
            ),
            "identity_boundary": (
                "The publication vector cannot prove that the 00:52:04.350 "
                "energy peak is the same event as Kadri Figure 9 rectangle 1."
            ),
        },
        "conclusion": [
            "The H01W feature is strong in the publication trace and merits raw-data follow-up.",
            "The apparent H08S counterpart is a cropped, unfiltered boundary segment lying inside the extrapolated periodic-airgun mask.",
            "A fully supported boundary-compatible ten-second test is not unusual relative to panel-e controls.",
            "The observed central-celerity timing offset is expected under the 9.974-second periodic-pulse phase null.",
            "If the H01W feature is Kadri Figure 9 rectangle 1, its reported 57-degree bearing is incompatible with the 263.55-degree OSCAR direction.",
            "Raw three-channel H01W and H08S waveforms are required for coherent waveform, bearing and trials-corrected association tests.",
        ],
        "limits": [
            "already-filtered and raster-independent PDF-vector traces rather than raw CTBTO channels",
            "post-hoc inspection of the OSCAR alignment",
            "one-sided forward-energy controls are descriptive and not calibrated receiver false-alarm probabilities",
            "pulse-cadence null does not establish that the cropped boundary waveform is an airgun pulse",
            "source-reported H01W bearing cannot be attached to the screened peak from the single plotted pressure trace alone",
        ],
    }

    metrics_path = OUTPUT / "oscar-boundary-audit-metrics.csv"
    controls_path = OUTPUT / "oscar-boundary-window-controls.csv"
    cadence_path = OUTPUT / "oscar-boundary-cadence-centres.csv"
    summary_path = OUTPUT / "oscar-boundary-audit-summary.json"
    write_csv(metrics_path, metric_rows(summary))
    write_csv(controls_path, control_rows)
    cadence_rows = []
    for number, predicted, observed in zip(
        geometry.cycle_numbers,
        geometry.predicted_centres_s,
        geometry.observed_centres_s,
    ):
        cadence_rows.append(
            {
                "cycle_number": int(number),
                "predicted_centre_s": f"{float(predicted):.9f}",
                "observed_centre_s": f"{float(observed):.9f}",
                "residual_s": f"{float(observed - predicted):.9f}",
                "status": "INTERIOR_PANEL_E_PERIODIC_CENTRE",
            }
        )
    cadence_rows.insert(
        0,
        {
            "cycle_number": int(np.min(geometry.cycle_numbers) - 1),
            "predicted_centre_s": f"{fitted_predecessor_s:.9f}",
            "observed_centre_s": "",
            "residual_s": "",
            "status": "EXTRAPOLATED_PRE_PANEL_PERIODIC_CENTRE",
        },
    )
    write_csv(cadence_path, cadence_rows)
    summary_path.write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    figure_paths = make_plot(
        panel,
        result,
        forward_score,
        expected_lower_s,
        expected_upper_s,
        expected_maximum,
        expected_maximum_time_s,
        control_maxima_array,
        fitted_predecessor_s,
        cadence,
        observed_boundary_peak_s,
        central_expected_s,
        matched_p,
    )

    output_paths = [
        metrics_path,
        controls_path,
        cadence_path,
        summary_path,
        *figure_paths,
    ]
    manifest = {
        "status": "REPRODUCIBLE_OUTPUT_HASHES",
        "inputs": {
            str(path.relative_to(HERE)): sha256(path)
            for path in (
                CONFIG_PATH,
                EVENT_CONFIG_PATH,
                FILTER_CONFIG_PATH,
                ALIGN_CONFIG_PATH,
                TARGET_PATH,
                SIGNIFICANCE_PATH,
            )
        },
        "code": {
            "code/oscar_boundary_audit.py": sha256(Path(__file__)),
            "code/aligned_detection_analysis.py": sha256(HERE / "code/aligned_detection_analysis.py"),
            "code/event_pair_analysis.py": sha256(HERE / "code/event_pair_analysis.py"),
        },
        "outputs": {
            path.name: sha256(path)
            for path in output_paths
        },
    }
    manifest_path = OUTPUT / "oscar-boundary-audit-manifest.json"
    manifest_path.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

