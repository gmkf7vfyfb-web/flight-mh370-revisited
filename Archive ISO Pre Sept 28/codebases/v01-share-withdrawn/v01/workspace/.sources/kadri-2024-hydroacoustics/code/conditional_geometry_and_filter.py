#!/usr/bin/env python3
"""Map conditional acoustic lines of position and filter H08S airgun pulses.

This derivation deliberately operates on calibrated path vertices extracted from
Kadri's already-filtered publication figure.  It does not recreate raw CTBTO
waveforms, array bearings, source energies or detection probabilities.
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
CONFIG_PATH = DATA / "conditional-geometry-config.json"
METADATA_PATH = DATA / "kadri-figure-extraction" / "metadata.json"
TRACE_ROOT = METADATA_PATH.parent
ARC_PATH = DATA / "seventh_arc_fl400.geojson"
ARC_PROVENANCE_PATH = DATA / "reference_geometry_provenance.json"
CORE_GRID_PATH = DATA / "posterior_grids.npz"
CORE_GRID_KEY = "reference_power_marginalization__core"
CANDIDATE_PATH = DATA / "observed-transient-candidates.csv"


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


def haversine_distance_km(
    latitude_deg: np.ndarray,
    longitude_deg: np.ndarray,
    origin: tuple[float, float],
    radius_km: float,
) -> np.ndarray:
    latitude = np.radians(latitude_deg)
    longitude = np.radians(longitude_deg)
    origin_latitude, origin_longitude = np.radians(origin)
    dlat = latitude - origin_latitude
    dlon = longitude - origin_longitude
    value = (
        np.sin(dlat / 2.0) ** 2
        + np.cos(origin_latitude) * np.cos(latitude) * np.sin(dlon / 2.0) ** 2
    )
    return 2.0 * radius_km * np.arcsin(np.sqrt(np.clip(value, 0.0, 1.0)))


def densify_polyline(coordinates: np.ndarray, maximum_step_deg: float = 0.02) -> np.ndarray:
    parts = []
    for start, end in zip(coordinates[:-1], coordinates[1:]):
        count = max(1, int(math.ceil(float(np.max(np.abs(end - start))) / maximum_step_deg)))
        fraction = np.arange(count, dtype=float) / count
        parts.append(start[None, :] + fraction[:, None] * (end - start)[None, :])
    parts.append(coordinates[-1:])
    return np.vstack(parts)


def hpd_threshold(grid: np.ndarray, area: np.ndarray, probability: float) -> float:
    density = grid / area
    order = np.argsort(density.ravel())[::-1]
    cumulative = np.cumsum(grid.ravel()[order])
    count = int(np.searchsorted(cumulative, probability, side="left")) + 1
    return float(density.ravel()[order[min(count - 1, order.size - 1)]])


def contiguous_segments(mask: np.ndarray) -> list[tuple[int, int]]:
    padded = np.r_[False, mask, False].astype(int)
    changes = np.diff(padded)
    starts = np.flatnonzero(changes == 1)
    ends = np.flatnonzero(changes == -1) - 1
    return list(zip(starts.tolist(), ends.tolist()))


def load_spatial_inputs(configuration: dict) -> dict:
    arc_payload = json.loads(ARC_PATH.read_text(encoding="utf-8"))
    original_arc = np.asarray(
        arc_payload["features"][0]["geometry"]["coordinates"], dtype=float
    )
    arc = densify_polyline(original_arc)
    with np.load(CORE_GRID_PATH) as payload:
        core = {
            "longitude": payload["longitude_deg_E"].copy(),
            "latitude": payload["latitude_deg"].copy(),
            "area": payload["cell_area_km2"].copy(),
            "grid": payload[CORE_GRID_KEY].copy(),
        }

    station = configuration["stations"]
    origin_h01 = (station["H01W"]["latitude_deg"], station["H01W"]["longitude_deg_e"])
    origin_h08 = (station["H08S"]["latitude_deg"], station["H08S"]["longitude_deg_e"])
    radius = float(configuration["earth_radius_km"])
    arc_h01 = haversine_distance_km(arc[:, 1], arc[:, 0], origin_h01, radius)
    arc_h08 = haversine_distance_km(arc[:, 1], arc[:, 0], origin_h08, radius)
    arc_difference = arc_h08 - arc_h01
    ranges = configuration["conditional_range_constraints_km"]
    h01_mask = (arc_h01 >= ranges["H01W"][0]) & (arc_h01 <= ranges["H01W"][1])
    h08_mask = (arc_h08 >= ranges["H08S"][0]) & (arc_h08 <= ranges["H08S"][1])
    difference_mask = (
        (arc_difference >= ranges["H08S_minus_H01W"][0])
        & (arc_difference <= ranges["H08S_minus_H01W"][1])
    )
    joint_mask = h01_mask & h08_mask & difference_mask
    return {
        "arc": arc,
        "arc_h01": arc_h01,
        "arc_h08": arc_h08,
        "arc_difference": arc_difference,
        "arc_h01_mask": h01_mask,
        "arc_h08_mask": h08_mask,
        "arc_difference_mask": difference_mask,
        "arc_joint_mask": joint_mask,
        "core": core,
    }


def spatial_rows(spatial: dict) -> list[dict]:
    rows = []
    for index, coordinate in enumerate(spatial["arc"]):
        rows.append(
            {
                "arc_sample": index,
                "longitude_deg_e": f"{coordinate[0]:.8f}",
                "latitude_deg": f"{coordinate[1]:.8f}",
                "range_h01w_km": f"{spatial['arc_h01'][index]:.6f}",
                "range_h08s_km": f"{spatial['arc_h08'][index]:.6f}",
                "range_difference_h08s_minus_h01w_km": f"{spatial['arc_difference'][index]:.6f}",
                "within_h01w_range_band": bool(spatial["arc_h01_mask"][index]),
                "within_h08s_range_band": bool(spatial["arc_h08_mask"][index]),
                "within_range_difference_band": bool(spatial["arc_difference_mask"][index]),
                "within_all_three_bands": bool(spatial["arc_joint_mask"][index]),
                "status": "DERIVED_CONDITIONAL_GEOMETRY_NOT_EVENT_LOCATION",
            }
        )
    return rows


def segment_summary(spatial: dict, mask_name: str) -> list[dict]:
    mask = spatial[mask_name]
    output = []
    for start, end in contiguous_segments(mask):
        middle = (start + end) // 2
        output.append(
            {
                "start_latitude_deg": float(spatial["arc"][start, 1]),
                "start_longitude_deg_e": float(spatial["arc"][start, 0]),
                "middle_latitude_deg": float(spatial["arc"][middle, 1]),
                "middle_longitude_deg_e": float(spatial["arc"][middle, 0]),
                "end_latitude_deg": float(spatial["arc"][end, 1]),
                "end_longitude_deg_e": float(spatial["arc"][end, 0]),
                "sample_count": int(end - start + 1),
            }
        )
    return output


def plot_spatial(configuration: dict, spatial: dict) -> None:
    map_config = configuration["map_grid"]
    spacing = float(map_config["spacing_deg"])
    longitude = np.arange(
        map_config["longitude_min_deg_e"],
        map_config["longitude_max_deg_e"] + spacing / 2,
        spacing,
    )
    latitude = np.arange(
        map_config["latitude_min_deg"],
        map_config["latitude_max_deg"] + spacing / 2,
        spacing,
    )
    mesh_lon, mesh_lat = np.meshgrid(longitude, latitude)
    station = configuration["stations"]
    origin_h01 = (station["H01W"]["latitude_deg"], station["H01W"]["longitude_deg_e"])
    origin_h08 = (station["H08S"]["latitude_deg"], station["H08S"]["longitude_deg_e"])
    radius = float(configuration["earth_radius_km"])
    distance_h01 = haversine_distance_km(mesh_lat, mesh_lon, origin_h01, radius)
    distance_h08 = haversine_distance_km(mesh_lat, mesh_lon, origin_h08, radius)
    difference = distance_h08 - distance_h01
    ranges = configuration["conditional_range_constraints_km"]
    h01_mask = (distance_h01 >= ranges["H01W"][0]) & (distance_h01 <= ranges["H01W"][1])
    h08_mask = (distance_h08 >= ranges["H08S"][0]) & (distance_h08 <= ranges["H08S"][1])
    difference_mask = (
        (difference >= ranges["H08S_minus_H01W"][0])
        & (difference <= ranges["H08S_minus_H01W"][1])
    )
    joint = h01_mask & h08_mask & difference_mask

    core = spatial["core"]
    core_density = core["grid"] / core["area"]
    core_lon, core_lat = np.meshgrid(core["longitude"], core["latitude"])
    hpd_levels = [
        hpd_threshold(core["grid"], core["area"], probability)
        for probability in (0.99, 0.90, 0.50)
    ]

    def draw(axis: plt.Axes, zoom: bool) -> None:
        axis.contourf(
            mesh_lon,
            mesh_lat,
            np.ma.masked_where(~h01_mask, np.ones_like(distance_h01)),
            levels=[0.5, 1.5],
            colors=["#4C9ED9"],
            alpha=0.23,
        )
        axis.contourf(
            mesh_lon,
            mesh_lat,
            np.ma.masked_where(~h08_mask, np.ones_like(distance_h08)),
            levels=[0.5, 1.5],
            colors=["#F2A65A"],
            alpha=0.24,
        )
        axis.contourf(
            mesh_lon,
            mesh_lat,
            np.ma.masked_where(~difference_mask, np.ones_like(difference)),
            levels=[0.5, 1.5],
            colors="none",
            hatches=["////"],
            alpha=0.0,
        )
        axis.contour(
            mesh_lon,
            mesh_lat,
            distance_h01,
            levels=ranges["H01W"],
            colors=["#1769AA"],
            linewidths=1.35,
        )
        axis.contour(
            mesh_lon,
            mesh_lat,
            distance_h08,
            levels=ranges["H08S"],
            colors=["#C86516"],
            linewidths=1.35,
        )
        axis.contour(
            mesh_lon,
            mesh_lat,
            difference,
            levels=ranges["H08S_minus_H01W"],
            colors=["#7B3294"],
            linewidths=1.2,
            linestyles="--",
        )
        axis.contourf(
            mesh_lon,
            mesh_lat,
            np.ma.masked_where(~joint, np.ones_like(distance_h01)),
            levels=[0.5, 1.5],
            colors=["#146B4A"],
            alpha=0.62,
        )
        contour = axis.contour(
            core_lon,
            core_lat,
            core_density,
            levels=hpd_levels,
            colors=["#6A8797", "#315E78", "#0B3954"],
            linewidths=[1.0, 1.3, 1.7],
        )
        axis.clabel(
            contour,
            fmt={hpd_levels[0]: "99% PDF", hpd_levels[1]: "90%", hpd_levels[2]: "50%"},
            fontsize=7.5,
        )
        axis.plot(
            spatial["arc"][:, 0],
            spatial["arc"][:, 1],
            color="#111111",
            linewidth=2.0,
            linestyle=(0, (5, 3)),
            label="official FL400 seventh-arc reference",
        )
        joint_arc = spatial["arc_joint_mask"]
        axis.plot(
            np.ma.masked_where(~joint_arc, spatial["arc"][:, 0]),
            np.ma.masked_where(~joint_arc, spatial["arc"][:, 1]),
            color="#00A676",
            linewidth=5.0,
            solid_capstyle="round",
            label="arc satisfying all three bands",
        )
        axis.scatter(
            station["H01W"]["longitude_deg_e"],
            station["H01W"]["latitude_deg"],
            marker="s",
            s=75,
            color="#1769AA",
            edgecolor="white",
            zorder=8,
        )
        axis.scatter(
            station["H08S"]["longitude_deg_e"],
            station["H08S"]["latitude_deg"],
            marker="s",
            s=75,
            color="#C86516",
            edgecolor="white",
            zorder=8,
        )
        axis.annotate("H01W Cape Leeuwin", (114.141, -34.892), xytext=(-118, -20), textcoords="offset points", fontsize=8.2)
        axis.annotate("H08S Diego Garcia", (72.484, -7.639), xytext=(8, 8), textcoords="offset points", fontsize=8.2)
        axis.set_xlabel("Longitude (°E)")
        axis.set_ylabel("Latitude (°; south negative)")
        axis.grid(alpha=0.2)
        if zoom:
            axis.set_xlim(79.0, 116.5)
            axis.set_ylim(-45.5, -15.0)
            axis.set_title("B. Seventh arc and integrated-PDF detail")
        else:
            axis.set_xlim(60.0, 122.0)
            axis.set_ylim(-48.0, 2.0)
            axis.set_title("A. Conditional station range and range-difference bands")

    fig, axes = plt.subplots(1, 2, figsize=(18.2, 8.3), gridspec_kw={"width_ratios": [1.08, 0.92]})
    draw(axes[0], zoom=False)
    draw(axes[1], zoom=True)
    legend_handles = [
        Patch(facecolor="#4C9ED9", alpha=0.28, edgecolor="#1769AA", label="H01W range 2,190–2,410 km"),
        Patch(facecolor="#F2A65A", alpha=0.30, edgecolor="#C86516", label="H08S range 3,580–3,930 km"),
        Patch(facecolor="white", edgecolor="#7B3294", hatch="////", label="H08S − H01W range 1,390–1,525 km"),
        Patch(facecolor="#146B4A", alpha=0.70, label="joint overlap of all three bands"),
        Line2D([0], [0], color="#111111", linestyle=(0, (5, 3)), linewidth=2, label="official FL400 seventh-arc reference"),
        Line2D([0], [0], color="#0B3954", linewidth=2, label="existing integrated PDF contours"),
    ]
    axes[0].legend(handles=legend_handles, loc="lower left", fontsize=8.0, framealpha=0.94)
    axes[1].legend(handles=legend_handles[3:], loc="lower left", fontsize=8.0, framealpha=0.94)
    fig.suptitle(
        "Conditional hydroacoustic lines of position compared with the seventh arc",
        fontsize=16.5,
        y=0.985,
    )
    fig.text(
        0.5,
        0.018,
        "Illustrative common-celerity geometry from two publication-trace features; not an acoustic association, bearing solution or posterior update.",
        ha="center",
        fontsize=9.2,
        color="#333333",
    )
    fig.tight_layout(rect=[0.0, 0.045, 1.0, 0.95])
    for suffix in ("png", "pdf"):
        fig.savefig(OUTPUT / f"conditional-acoustic-lop-seventh-arc.{suffix}", dpi=260 if suffix == "png" else None)
    plt.close(fig)


@dataclass
class TracePanel:
    panel: str
    start_epoch_s: float
    time_s: np.ndarray
    epoch_s: np.ndarray
    pressure_pa: np.ndarray


@dataclass
class FilterResult:
    panel: TracePanel
    period_s: float
    shot_centres_s: np.ndarray
    template_time_s: np.ndarray
    template_pa: np.ndarray
    fitted_periodic_pa: np.ndarray
    residual_pa: np.ndarray
    mask: np.ndarray
    mask_lower_s: float
    mask_upper_s: float
    scale_factors: np.ndarray


def rolling_rms(values: np.ndarray, count: int) -> np.ndarray:
    kernel = np.ones(max(2, count), dtype=float) / max(2, count)
    return np.sqrt(np.maximum(np.convolve(values * values, kernel, mode="same"), 0.0))


def load_h08_panels(configuration: dict) -> list[TracePanel]:
    metadata = json.loads(METADATA_PATH.read_text(encoding="utf-8"))
    dt = float(configuration["filter"]["regular_grid_dt_s"])
    panels = []
    for record in metadata["figure9_vector_traces"]:
        if record["station"] != "H08S":
            continue
        with (TRACE_ROOT / record["file"]).open(newline="", encoding="utf-8") as handle:
            rows = list(csv.DictReader(handle))
        source_time = np.asarray([float(row["plotted_time_s"]) for row in rows])
        pressure = np.asarray([float(row["pressure_pa"]) for row in rows])
        order = np.argsort(source_time)
        unique_time, unique_index = np.unique(source_time[order], return_index=True)
        source_pressure = pressure[order][unique_index]
        time_s = np.arange(0.0, 600.0, dt)
        regular_pressure = np.interp(time_s, unique_time, source_pressure)
        regular_pressure -= np.median(regular_pressure)
        start = parse_utc(record["start_utc"]).timestamp()
        panels.append(
            TracePanel(
                panel=record["panel"],
                start_epoch_s=start,
                time_s=time_s,
                epoch_s=start + time_s,
                pressure_pa=regular_pressure,
            )
        )
    return sorted(panels, key=lambda item: item.start_epoch_s)


def parabolic_peak(values: np.ndarray, index: int) -> float:
    if index <= 0 or index >= values.size - 1:
        return float(index)
    left, centre, right = values[index - 1 : index + 2]
    denominator = left - 2.0 * centre + right
    if abs(float(denominator)) < 1e-15:
        return float(index)
    return float(index + 0.5 * (left - right) / denominator)


def estimate_period(values: np.ndarray, dt: float, configuration: dict) -> tuple[float, np.ndarray]:
    window = max(2, int(round(configuration["envelope_window_s"] / dt)))
    envelope = rolling_rms(values - np.median(values), window)
    centred = envelope - np.median(envelope)
    autocorrelation = fftconvolve(centred, centred[::-1], mode="full")[values.size - 1 :]
    lower = int(round(configuration["period_search_s"][0] / dt))
    upper = int(round(configuration["period_search_s"][1] / dt))
    local_index = int(np.argmax(autocorrelation[lower : upper + 1])) + lower
    refined_index = parabolic_peak(autocorrelation, local_index)
    return refined_index * dt, envelope


def track_shots(
    time_s: np.ndarray,
    envelope: np.ndarray,
    period_s: float,
    dt: float,
    half_window_s: float,
) -> tuple[np.ndarray, float]:
    distance = max(1, int(round(0.72 * period_s / dt)))
    peaks, _ = find_peaks(envelope, distance=distance, prominence=0.08 * np.std(envelope))
    core = peaks[(time_s[peaks] > period_s / 2) & (time_s[peaks] < time_s[-1] - period_s / 2)]
    if core.size < 20:
        raise ValueError("Too few periodic pulse candidates")
    anchor_index = int(core[np.argmax(envelope[core])])
    anchor_time = float(time_s[anchor_index])
    final_centres = np.array([], dtype=float)
    for _iteration in range(3):
        k_min = int(math.ceil((time_s[0] - anchor_time) / period_s))
        k_max = int(math.floor((time_s[-1] - anchor_time) / period_s))
        k_values = np.arange(k_min, k_max + 1)
        predicted = anchor_time + period_s * k_values
        observed = []
        accepted_k = []
        for k_value, prediction in zip(k_values, predicted):
            mask = np.abs(time_s - prediction) <= half_window_s
            indices = np.flatnonzero(mask)
            if indices.size == 0:
                continue
            index = int(indices[np.argmax(envelope[indices])])
            observed.append(float(time_s[index]))
            accepted_k.append(int(k_value))
        observed_array = np.asarray(observed)
        accepted_array = np.asarray(accepted_k)
        fit = np.polyfit(accepted_array, observed_array, 1)
        period_s = float(fit[0])
        anchor_time = float(fit[1])
        residual = observed_array - (anchor_time + period_s * accepted_array)
        keep = np.abs(residual - np.median(residual)) <= max(0.35, 3.0 * 1.4826 * np.median(np.abs(residual - np.median(residual))))
        if np.count_nonzero(keep) >= 20:
            fit = np.polyfit(accepted_array[keep], observed_array[keep], 1)
            period_s = float(fit[0])
            anchor_time = float(fit[1])
        final_centres = anchor_time + period_s * np.arange(k_min, k_max + 1)
    return final_centres, period_s


def robust_scale_fit(template: np.ndarray, values: np.ndarray) -> float:
    weights = np.ones_like(values)
    denominator_floor = 1e-12
    scale = 1.0
    for _iteration in range(5):
        denominator = float(np.sum(weights * template * template))
        if denominator <= denominator_floor:
            return 0.0
        scale = float(np.sum(weights * template * values) / denominator)
        residual = values - scale * template
        robust_sigma = 1.4826 * float(np.median(np.abs(residual - np.median(residual))))
        if not robust_sigma > 0:
            break
        absolute = np.abs(residual) / (1.5 * robust_sigma)
        weights = np.ones_like(absolute)
        tail = absolute > 1.0
        weights[tail] = 1.0 / absolute[tail]
    return scale


def template_energy_support(
    template_time_s: np.ndarray,
    template_pa: np.ndarray,
    energy_fraction: float,
) -> tuple[float, float]:
    energy = template_pa * template_pa
    cumulative = np.cumsum(energy)
    if cumulative[-1] <= 0.0:
        raise ValueError("Zero periodic template energy")
    cumulative /= cumulative[-1]
    tail = (1.0 - energy_fraction) / 2.0
    lower = float(np.interp(tail, cumulative, template_time_s))
    upper = float(np.interp(1.0 - tail, cumulative, template_time_s))
    return lower, upper


def filter_panel(panel: TracePanel, configuration: dict, energy_fraction: float) -> FilterResult:
    filter_config = configuration["filter"]
    dt = float(filter_config["regular_grid_dt_s"])
    initial_period, envelope = estimate_period(panel.pressure_pa, dt, filter_config)
    centres, period = track_shots(
        panel.time_s,
        envelope,
        initial_period,
        dt,
        float(filter_config["shot_tracking_half_window_s"]),
    )
    template_time = np.arange(-period / 2.0, period / 2.0, dt)
    cycles = []
    valid_centres = centres[
        (centres + template_time[0] >= panel.time_s[0])
        & (centres + template_time[-1] <= panel.time_s[-1])
    ]
    for centre in valid_centres:
        cycles.append(np.interp(centre + template_time, panel.time_s, panel.pressure_pa))
    if len(cycles) < 20:
        raise ValueError("Too few complete airgun cycles for robust template")
    template = np.median(np.vstack(cycles), axis=0)
    template -= np.median(template)
    lower, upper = template_energy_support(template_time, template, energy_fraction)

    centre_index = np.argmin(np.abs(panel.time_s[:, None] - centres[None, :]), axis=1)
    nearest_centres = centres[centre_index]
    phase = panel.time_s - nearest_centres
    periodic_shape = np.interp(phase, template_time, template, left=0.0, right=0.0)
    scales = np.zeros(centres.size, dtype=float)
    fitted = np.zeros_like(panel.pressure_pa)
    for index in range(centres.size):
        sample_mask = centre_index == index
        if np.count_nonzero(sample_mask) < 10:
            continue
        scales[index] = robust_scale_fit(periodic_shape[sample_mask], panel.pressure_pa[sample_mask])
        fitted[sample_mask] = scales[index] * periodic_shape[sample_mask]
    residual = panel.pressure_pa - fitted
    mask = (phase >= lower) & (phase <= upper)
    return FilterResult(
        panel=panel,
        period_s=period,
        shot_centres_s=centres,
        template_time_s=template_time,
        template_pa=template,
        fitted_periodic_pa=fitted,
        residual_pa=residual,
        mask=mask,
        mask_lower_s=lower,
        mask_upper_s=upper,
        scale_factors=scales,
    )


def score_signal(values: np.ndarray, configuration: dict) -> np.ndarray:
    dt = float(configuration["filter"]["regular_grid_dt_s"])
    components = []
    for width_s in configuration["filter"]["candidate_energy_windows_s"]:
        rms = rolling_rms(values, int(round(float(width_s) / dt)))
        centre = float(np.median(rms))
        scale = float(1.4826 * np.median(np.abs(rms - centre)))
        components.append((rms - centre) / max(scale, 1e-12))
    return np.max(np.vstack(components), axis=0)


def top_candidates(result: FilterResult, configuration: dict) -> list[dict]:
    rows = []
    dt = float(configuration["filter"]["regular_grid_dt_s"])
    separation = int(round(configuration["filter"]["candidate_minimum_separation_s"] / dt))
    high_lower, high_upper = [
        parse_utc(value).timestamp() for value in configuration["filter"]["high_rate_window_utc"]
    ]
    for method, values in (
        ("original", result.panel.pressure_pa),
        ("template_subtracted", result.residual_pa),
    ):
        score = score_signal(values, configuration)
        peaks, _ = find_peaks(score, distance=separation)
        peaks = peaks[(result.panel.epoch_s[peaks] >= high_lower) & (result.panel.epoch_s[peaks] <= high_upper)]
        order = peaks[np.argsort(score[peaks])[::-1]][:12]
        threshold = float(np.quantile(score[peaks], configuration["filter"]["candidate_quantile"])) if peaks.size else float("nan")
        for rank, index in enumerate(order, start=1):
            rows.append(
                {
                    "panel": result.panel.panel,
                    "method": method,
                    "rank_within_high_rate_window": rank,
                    "event_utc": iso_utc(result.panel.epoch_s[index]),
                    "robust_excess_energy_score": f"{score[index]:.9g}",
                    "within_periodic_mask": bool(result.mask[index]),
                    "method_q99_peak_threshold": f"{threshold:.9g}",
                    "status": "PUBLICATION_TRACE_RANK_NOT_EVENT_PROBABILITY",
                }
            )
    return rows


def filter_metrics(result: FilterResult, configuration: dict) -> dict:
    intervals = np.diff(result.shot_centres_s)
    original_rms = float(np.sqrt(np.mean(result.panel.pressure_pa**2)))
    residual_rms = float(np.sqrt(np.mean(result.residual_pa**2)))
    event_epoch = parse_utc(configuration["filter"]["event_utc"]).timestamp()
    event_index = int(np.argmin(np.abs(result.panel.epoch_s - event_epoch)))
    local = np.abs(result.panel.epoch_s - event_epoch) <= 2.0
    nearest_shot = int(np.argmin(np.abs(result.shot_centres_s - result.panel.time_s[event_index])))
    nearest_shot_offset = float(result.panel.time_s[event_index] - result.shot_centres_s[nearest_shot])
    original_local_rms = float(np.sqrt(np.mean(result.panel.pressure_pa[local] ** 2)))
    residual_local_rms = float(np.sqrt(np.mean(result.residual_pa[local] ** 2)))
    return {
        "panel": result.panel.panel,
        "period_s": result.period_s,
        "shot_count": int(result.shot_centres_s.size),
        "shot_interval_median_s": float(np.median(intervals)),
        "shot_interval_q10_s": float(np.quantile(intervals, 0.10)),
        "shot_interval_q90_s": float(np.quantile(intervals, 0.90)),
        "template_mask_lower_s_relative_to_shot": result.mask_lower_s,
        "template_mask_upper_s_relative_to_shot": result.mask_upper_s,
        "masked_fraction": float(np.mean(result.mask)),
        "original_rms_pa": original_rms,
        "template_subtracted_rms_pa": residual_rms,
        "rms_reduction_fraction": 1.0 - residual_rms / original_rms,
        "event_in_panel": bool(result.panel.epoch_s[0] <= event_epoch <= result.panel.epoch_s[-1]),
        "event_nearest_shot_offset_s": nearest_shot_offset if result.panel.epoch_s[0] <= event_epoch <= result.panel.epoch_s[-1] else None,
        "event_within_periodic_mask": bool(result.mask[event_index]) if result.panel.epoch_s[0] <= event_epoch <= result.panel.epoch_s[-1] else None,
        "event_local_original_rms_pa_pm2s": original_local_rms if result.panel.epoch_s[0] <= event_epoch <= result.panel.epoch_s[-1] else None,
        "event_local_template_subtracted_rms_pa_pm2s": residual_local_rms if result.panel.epoch_s[0] <= event_epoch <= result.panel.epoch_s[-1] else None,
        "event_local_rms_retained_fraction": residual_local_rms / original_local_rms if result.panel.epoch_s[0] <= event_epoch <= result.panel.epoch_s[-1] else None,
        "status": "DERIVED_FROM_ALREADY_FILTERED_PUBLICATION_TRACE",
    }


def filtered_trace_rows(results: list[FilterResult]) -> list[dict]:
    rows = []
    for result in results:
        for index in range(result.panel.time_s.size):
            rows.append(
                {
                    "panel": result.panel.panel,
                    "utc": iso_utc(result.panel.epoch_s[index]),
                    "pressure_original_pa": f"{result.panel.pressure_pa[index]:.9g}",
                    "fitted_periodic_airgun_proxy_pa": f"{result.fitted_periodic_pa[index]:.9g}",
                    "pressure_template_subtracted_pa": f"{result.residual_pa[index]:.9g}",
                    "periodic_mask": bool(result.mask[index]),
                    "pressure_combined_pa": "" if result.mask[index] else f"{result.residual_pa[index]:.9g}",
                    "status": "FILTERED_PUBLICATION_GEOMETRY_NOT_RAW_PRESSURE",
                }
            )
    return rows


def plot_filter_comparison(results: list[FilterResult], configuration: dict) -> None:
    colours = {
        "original": "#4C4C4C",
        "periodic": "#C86516",
        "residual": "#1769AA",
        "combined": "#146B4A",
    }
    event = parse_utc(configuration["filter"]["event_utc"])
    medians = [parse_utc(value) for value in configuration["filter"]["reference_median_arrivals_utc"]]
    fig, axes = plt.subplots(4, 2, figsize=(18.0, 11.0), sharex="col")
    for column, result in enumerate(results):
        x = [datetime.fromtimestamp(value, timezone.utc) for value in result.panel.epoch_s]
        combined = result.residual_pa.copy()
        combined[result.mask] = np.nan
        series = [
            (result.panel.pressure_pa, colours["original"], "Original extracted trace"),
            (result.fitted_periodic_pa, colours["periodic"], "Adaptive periodic template"),
            (result.residual_pa, colours["residual"], "Template-subtracted residual"),
            (combined, colours["combined"], "Combined: residual outside mask"),
        ]
        maximum = max(0.5, float(np.quantile(np.abs(result.panel.pressure_pa), 0.998)) * 1.18)
        for row, (values, colour, label) in enumerate(series):
            axis = axes[row, column]
            axis.plot(x, values, color=colour, linewidth=0.55)
            axis.axhline(0.0, color="#888888", linewidth=0.5)
            axis.set_ylim(-maximum, maximum)
            axis.grid(alpha=0.16)
            if row == 0:
                for centre in result.shot_centres_s:
                    axis.axvline(
                        datetime.fromtimestamp(result.panel.start_epoch_s + centre, timezone.utc),
                        color="#C86516",
                        linewidth=0.35,
                        alpha=0.34,
                    )
            if row in (0, 3):
                for start, end in contiguous_segments(result.mask):
                    axis.axvspan(x[start], x[end], color="#F2A65A", alpha=0.10 if row == 0 else 0.16, linewidth=0)
            if result.panel.epoch_s[0] <= event.timestamp() <= result.panel.epoch_s[-1]:
                axis.axvline(event, color="#A61B29", linewidth=1.4, label="01:03:13 screen feature")
                for median in medians:
                    axis.axvline(median, color="#6B4C9A", linewidth=1.0, linestyle="--")
            axis.text(
                0.012,
                0.88,
                label,
                transform=axis.transAxes,
                fontsize=8.5,
                weight="bold",
                bbox={"boxstyle": "round,pad=0.2", "facecolor": "white", "edgecolor": "none", "alpha": 0.82},
            )
            if column == 0:
                axis.set_ylabel("Pressure proxy (Pa)")
            if row == 0:
                axis.set_title(
                    f"Figure 9{result.panel.panel}: {iso_utc(result.panel.start_epoch_s)[11:16]}–{iso_utc(result.panel.start_epoch_s + 600)[11:16]} UTC\n"
                    f"period {result.period_s:.3f} s; mask {100*np.mean(result.mask):.1f}% of samples"
                )
            if row == 3:
                axis.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M", tz=timezone.utc))
                axis.set_xlabel("UTC on 8 March 2014")
    legend = [
        Line2D([0], [0], color="#A61B29", linewidth=1.5, label="01:03:13 publication-trace feature"),
        Line2D([0], [0], color="#6B4C9A", linewidth=1.1, linestyle="--", label="reference median arrivals"),
        Patch(facecolor="#F2A65A", alpha=0.25, label="periodic-template energy mask"),
    ]
    axes[0, 0].legend(handles=legend, loc="lower right", fontsize=7.8)
    fig.suptitle(
        "Diego Garcia H08S: periodic airgun-proxy filtering of Kadri Figure 9",
        fontsize=16.0,
        y=0.992,
    )
    fig.text(
        0.5,
        0.012,
        "Masking creates missing data; template subtraction creates a model-dependent residual. Neither reconstructs the raw three-channel record.",
        ha="center",
        fontsize=9.0,
    )
    fig.tight_layout(rect=[0.0, 0.03, 1.0, 0.965])
    for suffix in ("png", "pdf"):
        fig.savefig(OUTPUT / f"h08s-periodic-filter-comparison.{suffix}", dpi=260 if suffix == "png" else None)
    plt.close(fig)

    first = results[0]
    x = np.asarray([datetime.fromtimestamp(value, timezone.utc) for value in first.panel.epoch_s])
    zoom = (first.panel.epoch_s >= event.timestamp() - 20.0) & (first.panel.epoch_s <= event.timestamp() + 20.0)
    combined = first.residual_pa.copy()
    combined[first.mask] = np.nan
    fig, axes = plt.subplots(4, 1, figsize=(14.0, 9.0), sharex=True)
    plotted = [
        (first.panel.pressure_pa, colours["original"], "Original extracted trace"),
        (first.fitted_periodic_pa, colours["periodic"], "Fitted periodic airgun proxy"),
        (first.residual_pa, colours["residual"], "Template-subtracted residual"),
        (combined, colours["combined"], "Combined residual outside periodic mask"),
    ]
    maximum = max(0.5, float(np.max(np.abs(first.panel.pressure_pa[zoom]))) * 1.08)
    for axis, (values, colour, label) in zip(axes, plotted):
        axis.plot(x[zoom], values[zoom], color=colour, linewidth=0.8)
        axis.axvline(event, color="#A61B29", linewidth=1.4)
        for median in medians:
            axis.axvline(median, color="#6B4C9A", linewidth=1.0, linestyle="--")
        axis.set_ylim(-maximum, maximum)
        axis.set_ylabel("Pa proxy")
        axis.set_title(label, loc="left", fontsize=10.0, weight="bold")
        axis.grid(alpha=0.18)
    axes[-1].xaxis.set_major_formatter(mdates.DateFormatter("%H:%M:%S", tz=timezone.utc))
    axes[-1].set_xlabel("UTC on 8 March 2014")
    fig.suptitle("H08S detail around the 01:03:13 publication-trace feature", fontsize=15.2)
    fig.text(
        0.5,
        0.012,
        "The red line marks the screened feature; orange-mask gaps are unobservable under the masking method.",
        ha="center",
        fontsize=9.0,
    )
    fig.tight_layout(rect=[0.0, 0.035, 1.0, 0.96])
    for suffix in ("png", "pdf"):
        fig.savefig(OUTPUT / f"h08s-010313-filter-zoom.{suffix}", dpi=280 if suffix == "png" else None)
    plt.close(fig)


def sensitivity_rows(panels: list[TracePanel], configuration: dict) -> list[dict]:
    rows = []
    for energy_fraction in configuration["filter"]["mask_energy_fraction_sensitivity"]:
        for panel in panels:
            result = filter_panel(panel, configuration, float(energy_fraction))
            metric = filter_metrics(result, configuration)
            rows.append(
                {
                    "panel": panel.panel,
                    "mask_template_energy_fraction": energy_fraction,
                    "estimated_period_s": f"{result.period_s:.9g}",
                    "mask_lower_s_relative_to_shot": f"{result.mask_lower_s:.9g}",
                    "mask_upper_s_relative_to_shot": f"{result.mask_upper_s:.9g}",
                    "masked_sample_fraction": f"{np.mean(result.mask):.9g}",
                    "template_subtracted_rms_pa": f"{np.sqrt(np.mean(result.residual_pa**2)):.9g}",
                    "event_within_mask": metric["event_within_periodic_mask"],
                    "status": "MASK_SENSITIVITY_ON_PUBLICATION_TRACE",
                }
            )
    return rows


def make_manifest(paths: list[Path]) -> dict:
    return {
        "status": "REPRODUCIBLE_OUTPUT_HASHES",
        "inputs": {
            str(path.relative_to(ROOT)): sha256(path)
            for path in (CONFIG_PATH, METADATA_PATH, ARC_PATH, ARC_PROVENANCE_PATH, CORE_GRID_PATH, CANDIDATE_PATH)
        },
        "code": {str(Path(__file__).relative_to(ROOT)): sha256(Path(__file__))},
        "outputs": {path.name: sha256(path) for path in paths},
    }


def main() -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    configuration = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))

    spatial = load_spatial_inputs(configuration)
    arc_rows = spatial_rows(spatial)
    arc_csv = OUTPUT / "seventh-arc-conditional-acoustic-constraints.csv"
    write_csv(arc_csv, arc_rows)
    plot_spatial(configuration, spatial)

    panels = load_h08_panels(configuration)
    principal_fraction = float(configuration["filter"]["mask_template_energy_fraction"])
    results = [filter_panel(panel, configuration, principal_fraction) for panel in panels]
    metrics = [filter_metrics(result, configuration) for result in results]
    trace_csv = OUTPUT / "h08s-filtered-publication-traces.csv"
    candidate_csv = OUTPUT / "h08s-filtered-candidates.csv"
    sensitivity_csv = OUTPUT / "h08s-filter-sensitivity.csv"
    write_csv(trace_csv, filtered_trace_rows(results))
    write_csv(candidate_csv, top_candidates(results[0], configuration))
    write_csv(sensitivity_csv, sensitivity_rows(panels, configuration))
    plot_filter_comparison(results, configuration)

    summary = {
        "status": "DERIVED_CONDITIONAL_GEOMETRY_AND_PUBLICATION_TRACE_FILTER_NOT_RAW_DATA_OR_MH370_ASSOCIATION",
        "spatial": {
            "constraints_km": configuration["conditional_range_constraints_km"],
            "basis": configuration["range_basis"],
            "seventh_arc_segments": {
                "h01w_range": segment_summary(spatial, "arc_h01_mask"),
                "h08s_range": segment_summary(spatial, "arc_h08_mask"),
                "range_difference": segment_summary(spatial, "arc_difference_mask"),
                "joint": segment_summary(spatial, "arc_joint_mask"),
            },
            "joint_arc_sample_count": int(np.count_nonzero(spatial["arc_joint_mask"])),
        },
        "filter": {
            "method": "per-panel autocorrelation period estimate; tracked pulse epochs; robust phase-folded median template; per-cycle Huber-like amplitude fit; central template-energy mask",
            "principal_mask_template_energy_fraction": principal_fraction,
            "panel_metrics": metrics,
            "limits": [
                "input is an already-filtered and decimated publication drawing",
                "masking removes observations rather than recovering them",
                "template subtraction may suppress a physical signal coincident and morphologically correlated with the airgun train",
                "single displayed traces cannot support beamforming, bearing or cross-station coherence",
            ],
        },
    }
    summary_path = OUTPUT / "summary.json"
    summary_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    generated = [
        arc_csv,
        trace_csv,
        candidate_csv,
        sensitivity_csv,
        summary_path,
        OUTPUT / "conditional-acoustic-lop-seventh-arc.png",
        OUTPUT / "conditional-acoustic-lop-seventh-arc.pdf",
        OUTPUT / "h08s-periodic-filter-comparison.png",
        OUTPUT / "h08s-periodic-filter-comparison.pdf",
        OUTPUT / "h08s-010313-filter-zoom.png",
        OUTPUT / "h08s-010313-filter-zoom.pdf",
    ]
    manifest_path = OUTPUT / "manifest.json"
    manifest_path.write_text(json.dumps(make_manifest(generated), indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
