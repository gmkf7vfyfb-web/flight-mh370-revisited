#!/usr/bin/env python3
"""Audit two Kadri Table 1 times and map conditional two-station geometry.

This operates on filtered publication-figure vectors, not raw CTBTO channels.
Bearing and cross-station pairings are conditional controls and are never
treated as observed associations or likelihood updates.
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
from scipy.signal import find_peaks


HERE = Path(__file__).resolve().parents[1]
DATA = HERE / "data"
OUTPUT = HERE / "outputs"
CONFIG_PATH = DATA / "event-pair-analysis-config.json"
METADATA_PATH = DATA / "kadri-figure-extraction" / "metadata.json"
TRACE_ROOT = METADATA_PATH.parent
TABLE_PATH = DATA / "kadri-table1-transients.csv"
CANDIDATE_PATH = DATA / "observed-transient-candidates.csv"
GRID_PATH = DATA / "posterior_grids.npz"
GRID_KEY = "reference_power_marginalization__core"
ARC_PATH = DATA / "seventh_arc_fl400.geojson"
FILTERED_H08_PATH = OUTPUT / "h08s-filtered-publication-traces.csv"
PDF_METADATA = {"CreationDate": None, "ModDate": None}


@dataclass
class Trace:
    panel: str
    station: str
    start_epoch_s: float
    epoch_s: np.ndarray
    pressure_pa: np.ndarray
    score: np.ndarray
    candidate_indices: np.ndarray
    threshold: float


def parse_utc(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)


def iso_utc(epoch_s: float) -> str:
    return (
        datetime.fromtimestamp(float(epoch_s), timezone.utc)
        .isoformat(timespec="milliseconds")
        .replace("+00:00", "Z")
    )


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


def rolling_rms(values: np.ndarray, count: int) -> np.ndarray:
    kernel = np.ones(max(2, count), dtype=float) / max(2, count)
    return np.sqrt(np.maximum(np.convolve(values * values, kernel, mode="same"), 0.0))


def score_signal(values: np.ndarray, screen: dict) -> np.ndarray:
    dt = float(screen["regular_grid_dt_s"])
    guard = int(round(float(screen["panel_edge_guard_s"]) / dt))
    components = []
    for width_s in screen["energy_windows_s"]:
        rms = rolling_rms(values, int(round(float(width_s) / dt)))
        core = rms[guard:-guard]
        centre = float(np.median(core))
        scale = float(1.4826 * np.median(np.abs(core - centre)))
        components.append((rms - centre) / max(scale, 1e-12))
    return np.max(np.vstack(components), axis=0)


def load_traces(configuration: dict) -> dict[str, Trace]:
    metadata = json.loads(METADATA_PATH.read_text(encoding="utf-8"))
    screen = configuration["trace_screen"]
    dt = float(screen["regular_grid_dt_s"])
    separation = int(round(float(screen["candidate_minimum_separation_s"]) / dt))
    guard = int(round(float(screen["panel_edge_guard_s"]) / dt))
    traces = {}
    for record in metadata["figure9_vector_traces"]:
        with (TRACE_ROOT / record["file"]).open(newline="", encoding="utf-8") as handle:
            rows = list(csv.DictReader(handle))
        source_time = np.asarray([float(row["plotted_time_s"]) for row in rows])
        source_pressure = np.asarray([float(row["pressure_pa"]) for row in rows])
        order = np.argsort(source_time)
        unique_time, unique_index = np.unique(source_time[order], return_index=True)
        source_pressure = source_pressure[order][unique_index]
        regular_time = np.arange(0.0, 600.0, dt)
        pressure = np.interp(regular_time, unique_time, source_pressure)
        pressure -= np.median(pressure)
        score = score_signal(pressure, screen)
        peaks, _ = find_peaks(score, distance=separation)
        peaks = peaks[(peaks >= guard) & (peaks < score.size - guard)]
        threshold = float(np.quantile(score[peaks], screen["candidate_score_quantile_per_panel"]))
        start = parse_utc(record["start_utc"]).timestamp()
        traces[record["panel"]] = Trace(
            panel=record["panel"],
            station=record["station"],
            start_epoch_s=start,
            epoch_s=start + regular_time,
            pressure_pa=pressure,
            score=score,
            candidate_indices=peaks,
            threshold=threshold,
        )
    return traces


def load_selected_table_events(configuration: dict) -> list[dict]:
    with TABLE_PATH.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    selected = set(configuration["selected_table_events"])
    events = []
    for row in rows:
        if row["event_id"] not in selected:
            continue
        events.append(
            {
                **row,
                "epoch_s": parse_utc(f"2014-03-08T{row['time_utc']}Z").timestamp(),
                "bearing_deg": float(row["bearing_deg"]),
            }
        )
    if len(events) != len(selected):
        raise ValueError("A selected Table 1 event is missing")
    return events


def audit_table_events(
    configuration: dict, traces: dict[str, Trace], events: list[dict]
) -> list[dict]:
    rows = []
    for event in events:
        trace = next(
            trace
            for trace in traces.values()
            if trace.station == "H01W"
            and trace.start_epoch_s <= event["epoch_s"] < trace.start_epoch_s + 600.0
        )
        nearest_candidate = int(
            trace.candidate_indices[
                np.argmin(np.abs(trace.epoch_s[trace.candidate_indices] - event["epoch_s"]))
            ]
        )
        for half_window_s in configuration["table_trace_search_half_windows_s"]:
            indices = np.flatnonzero(
                np.abs(trace.epoch_s - event["epoch_s"]) <= float(half_window_s)
            )
            local_index = int(indices[np.argmax(trace.score[indices])])
            rows.append(
                {
                    "event_id": event["event_id"],
                    "table_time_utc": f"2014-03-08T{event['time_utc']}Z",
                    "bearing_deg": f"{event['bearing_deg']:.2f}",
                    "panel": trace.panel,
                    "search_half_window_s": f"{float(half_window_s):.1f}",
                    "local_max_score": f"{trace.score[local_index]:.9g}",
                    "panel_q99_threshold": f"{trace.threshold:.9g}",
                    "above_panel_q99": bool(trace.score[local_index] >= trace.threshold),
                    "local_score_peak_utc": iso_utc(trace.epoch_s[local_index]),
                    "nearest_detector_candidate_utc": iso_utc(trace.epoch_s[nearest_candidate]),
                    "nearest_candidate_offset_s": f"{trace.epoch_s[nearest_candidate] - event['epoch_s']:.3f}",
                    "status": "PUBLICATION_TRACE_LOCAL_SCORE_NOT_RAW_DATA_EVENT_EVIDENCE",
                }
            )
    return rows


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


def initial_bearing_deg(
    latitude_deg: np.ndarray,
    longitude_deg: np.ndarray,
    origin: tuple[float, float],
) -> np.ndarray:
    latitude = np.radians(latitude_deg)
    longitude = np.radians(longitude_deg)
    origin_latitude, origin_longitude = np.radians(origin)
    dlon = longitude - origin_longitude
    y = np.sin(dlon) * np.cos(latitude)
    x = (
        np.cos(origin_latitude) * np.sin(latitude)
        - np.sin(origin_latitude) * np.cos(latitude) * np.cos(dlon)
    )
    return np.degrees(np.arctan2(y, x)) % 360.0


def angular_difference_deg(first: np.ndarray, second: float) -> np.ndarray:
    return (first - second + 180.0) % 360.0 - 180.0


def hpd_threshold(grid: np.ndarray, area: np.ndarray, probability: float) -> float:
    density = grid / area
    order = np.argsort(density.ravel())[::-1]
    cumulative = np.cumsum(grid.ravel()[order])
    index = min(int(np.searchsorted(cumulative, probability, side="left")), order.size - 1)
    return float(density.ravel()[order[index]])


def load_spatial(configuration: dict) -> dict:
    with np.load(GRID_PATH) as payload:
        longitude = payload["longitude_deg_E"].copy()
        latitude = payload["latitude_deg"].copy()
        area = payload["cell_area_km2"].copy()
        probability = payload[GRID_KEY].copy()
    mesh_lon, mesh_lat = np.meshgrid(longitude, latitude)
    stations = configuration["stations"]
    h01 = (stations["H01W"]["latitude_deg"], stations["H01W"]["longitude_deg_e"])
    h08 = (stations["H08S"]["latitude_deg"], stations["H08S"]["longitude_deg_e"])
    radius = float(configuration["earth_radius_km"])
    distance_h01 = haversine_distance_km(mesh_lat, mesh_lon, h01, radius)
    distance_h08 = haversine_distance_km(mesh_lat, mesh_lon, h08, radius)
    bearing_h01 = initial_bearing_deg(mesh_lat, mesh_lon, h01)
    arc_payload = json.loads(ARC_PATH.read_text(encoding="utf-8"))
    arc = np.asarray(arc_payload["features"][0]["geometry"]["coordinates"], dtype=float)
    return {
        "longitude": longitude,
        "latitude": latitude,
        "mesh_lon": mesh_lon,
        "mesh_lat": mesh_lat,
        "area": area,
        "probability": probability,
        "density": probability / area,
        "distance_h01": distance_h01,
        "distance_h08": distance_h08,
        "range_difference": distance_h08 - distance_h01,
        "bearing_h01": bearing_h01,
        "arc": arc,
    }


def conditional_h08_windows(
    configuration: dict, spatial: dict, events: list[dict]
) -> list[dict]:
    rng = np.random.default_rng(int(configuration["random_seed"]))
    count = int(configuration["monte_carlo_sample_count"])
    celerity_low, celerity_high = map(float, configuration["acoustic_celerity_km_s"])
    tolerance_s = float(configuration["interstation_arrival_tolerance_s"])
    rows = []
    for event in events:
        difference = np.abs(angular_difference_deg(spatial["bearing_h01"], event["bearing_deg"]))
        for width_name, width in configuration["bearing_half_widths_deg"].items():
            mask = difference <= float(width)
            weights = spatial["probability"][mask]
            mass = float(np.sum(weights))
            if not mass > 0.0:
                raise ValueError(f"No PDF support for {event['event_id']} at {width_name}")
            probabilities = weights / mass
            selected = rng.choice(weights.size, size=count, replace=True, p=probabilities)
            range_difference = spatial["range_difference"][mask][selected]
            celerity = rng.uniform(celerity_low, celerity_high, size=count)
            timing_control = rng.uniform(-tolerance_s, tolerance_s, size=count)
            h08_epoch = event["epoch_s"] + range_difference / celerity + timing_control
            quantiles = np.quantile(h08_epoch, [0.025, 0.5, 0.975])
            rows.append(
                {
                    "event_id": event["event_id"],
                    "h01w_arrival_utc": f"2014-03-08T{event['time_utc']}Z",
                    "h01w_bearing_deg": f"{event['bearing_deg']:.2f}",
                    "bearing_control": width_name,
                    "bearing_half_width_deg": f"{float(width):.1f}",
                    "independent_pdf_mass_within_bearing_band": f"{mass:.9g}",
                    "h08s_arrival_q2p5_utc": iso_utc(quantiles[0]),
                    "h08s_arrival_median_utc": iso_utc(quantiles[1]),
                    "h08s_arrival_q97p5_utc": iso_utc(quantiles[2]),
                    "celerity_km_s": f"{celerity_low:.2f}–{celerity_high:.2f}",
                    "arrival_tolerance_s": f"±{tolerance_s:.1f}",
                    "status": "CONDITIONAL_TIMING_CONTROL_NOT_CROSS_STATION_ASSOCIATION",
                }
            )
    return rows


def range_difference_bounds(
    first_epoch_s: float,
    second_epoch_s: float,
    celerity: tuple[float, float],
    tolerance_s: float,
) -> tuple[float, float]:
    delta_s = second_epoch_s - first_epoch_s
    low = celerity[0] * max(0.0, delta_s - tolerance_s)
    high = celerity[1] * (delta_s + tolerance_s)
    return low, high


def common_source_time_masks(
    configuration: dict,
    spatial: dict,
    first_epoch_s: float,
    second_epoch_s: float,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Return celerity-existence masks for TOA difference, source time and both."""
    celerity_low, celerity_high = map(float, configuration["acoustic_celerity_km_s"])
    tolerance_s = float(configuration["interstation_arrival_tolerance_s"])
    source_low, source_high = [
        parse_utc(value).timestamp() for value in configuration["impact_time_control_utc"]
    ]
    delta_s = second_epoch_s - first_epoch_s
    if delta_s <= tolerance_s or first_epoch_s <= source_low:
        empty = np.zeros_like(spatial["probability"], dtype=bool)
        return empty, empty, empty

    range_difference = spatial["range_difference"]
    timing_c_low = range_difference / (delta_s + tolerance_s)
    timing_c_high = range_difference / (delta_s - tolerance_s)

    source_denominator_low = first_epoch_s - source_low
    source_c_low = spatial["distance_h01"] / source_denominator_low
    if first_epoch_s <= source_high:
        source_c_high = np.full_like(source_c_low, np.inf)
    else:
        source_c_high = spatial["distance_h01"] / (first_epoch_s - source_high)

    timing = (
        (range_difference > 0.0)
        & (np.maximum(celerity_low, timing_c_low) <= np.minimum(celerity_high, timing_c_high))
    )
    source = (
        np.maximum(celerity_low, source_c_low)
        <= np.minimum(celerity_high, source_c_high)
    )
    joint = (
        (range_difference > 0.0)
        & (
            np.maximum.reduce([
                np.full_like(range_difference, celerity_low),
                timing_c_low,
                source_c_low,
            ])
            <= np.minimum.reduce([
                np.full_like(range_difference, celerity_high),
                timing_c_high,
                source_c_high,
            ])
        )
    )
    return timing, source, joint


def pairing_rows(
    configuration: dict, spatial: dict, events: list[dict]
) -> list[dict]:
    celerity = tuple(map(float, configuration["acoustic_celerity_km_s"]))
    tolerance_s = float(configuration["interstation_arrival_tolerance_s"])
    h08_features = configuration["screened_features"]["H08S"]
    rows = []
    for event in events:
        bearing_difference = np.abs(
            angular_difference_deg(spatial["bearing_h01"], event["bearing_deg"])
        )
        for feature in h08_features:
            second = parse_utc(feature["event_utc"]).timestamp()
            lower, upper = range_difference_bounds(
                event["epoch_s"], second, celerity, tolerance_s
            )
            range_mask, source_time_mask, range_and_source_time_mask = common_source_time_masks(
                configuration, spatial, event["epoch_s"], second
            )
            for width_name, width in configuration["bearing_half_widths_deg"].items():
                bearing_mask = bearing_difference <= float(width)
                joint = range_mask & bearing_mask
                rows.append(
                    {
                        "pair_family": "kadri_table_bearing_plus_h08s_screened_time",
                        "h01w_event_id": event["event_id"],
                        "h01w_arrival_utc": f"2014-03-08T{event['time_utc']}Z",
                        "h01w_bearing_deg": f"{event['bearing_deg']:.2f}",
                        "h08s_screened_arrival_utc": feature["event_utc"],
                        "bearing_control": width_name,
                        "range_difference_low_km": f"{lower:.6f}",
                        "range_difference_high_km": f"{upper:.6f}",
                        "independent_pdf_mass_within_range_band": f"{np.sum(spatial['probability'][range_mask]):.9g}",
                        "independent_pdf_mass_within_bearing_band": f"{np.sum(spatial['probability'][bearing_mask]):.9g}",
                        "independent_pdf_mass_within_joint_bands": f"{np.sum(spatial['probability'][joint]):.9g}",
                        "impact_time_control_utc": "–".join(configuration["impact_time_control_utc"]),
                        "independent_pdf_mass_within_impact_time_control": f"{np.sum(spatial['probability'][source_time_mask]):.9g}",
                        "independent_pdf_mass_within_range_and_impact_time": f"{np.sum(spatial['probability'][range_and_source_time_mask]):.9g}",
                        "independent_pdf_mass_within_bearing_range_and_impact_time": f"{np.sum(spatial['probability'][bearing_mask & range_and_source_time_mask]):.9g}",
                        "h08s_periodic_context": feature["periodic_context"],
                        "status": "POST_HOC_CONDITIONAL_PAIRING_CONTROL_NOT_ASSOCIATION_PROBABILITY",
                    }
                )
    for h01_feature in configuration["screened_features"]["H01W"]:
        first = parse_utc(h01_feature["event_utc"]).timestamp()
        for h08_feature in h08_features:
            second = parse_utc(h08_feature["event_utc"]).timestamp()
            lower, upper = range_difference_bounds(first, second, celerity, tolerance_s)
            mask, source_time_mask, range_and_source_time_mask = common_source_time_masks(
                configuration, spatial, first, second
            )
            rows.append(
                {
                    "pair_family": "independently_screened_times_without_bearing",
                    "h01w_event_id": f"screened_{h01_feature['event_utc'][11:19].replace(':', '')}",
                    "h01w_arrival_utc": h01_feature["event_utc"],
                    "h01w_bearing_deg": "",
                    "h08s_screened_arrival_utc": h08_feature["event_utc"],
                    "bearing_control": "none",
                    "range_difference_low_km": f"{lower:.6f}",
                    "range_difference_high_km": f"{upper:.6f}",
                    "independent_pdf_mass_within_range_band": f"{np.sum(spatial['probability'][mask]):.9g}",
                    "independent_pdf_mass_within_bearing_band": "",
                    "independent_pdf_mass_within_joint_bands": "",
                    "impact_time_control_utc": "–".join(configuration["impact_time_control_utc"]),
                    "independent_pdf_mass_within_impact_time_control": f"{np.sum(spatial['probability'][source_time_mask]):.9g}",
                    "independent_pdf_mass_within_range_and_impact_time": f"{np.sum(spatial['probability'][range_and_source_time_mask]):.9g}",
                    "independent_pdf_mass_within_bearing_range_and_impact_time": "",
                    "h08s_periodic_context": h08_feature["periodic_context"],
                    "status": "POST_HOC_CONDITIONAL_PAIRING_CONTROL_NOT_ASSOCIATION_PROBABILITY",
                }
            )
    return rows


def draw_pdf_base(axis: plt.Axes, spatial: dict) -> None:
    log_density = np.log10(np.maximum(spatial["density"], 1e-16))
    axis.pcolormesh(
        spatial["mesh_lon"],
        spatial["mesh_lat"],
        log_density,
        shading="auto",
        cmap="Greys",
        alpha=0.72,
        rasterized=True,
    )
    thresholds = [
        hpd_threshold(spatial["probability"], spatial["area"], probability)
        for probability in (0.99, 0.90, 0.50)
    ]
    contours = axis.contour(
        spatial["mesh_lon"],
        spatial["mesh_lat"],
        spatial["density"],
        levels=thresholds,
        colors=["#777777", "#555555", "#111111"],
        linewidths=[0.75, 1.0, 1.45],
    )
    axis.clabel(contours, fmt={thresholds[0]: "99%", thresholds[1]: "90%", thresholds[2]: "50%"}, fontsize=7)
    axis.plot(spatial["arc"][:, 0], spatial["arc"][:, 1], color="#009E73", linewidth=1.35)
    axis.set_xlim(float(spatial["longitude"][0]), float(spatial["longitude"][-1]))
    axis.set_ylim(float(spatial["latitude"][0]), float(spatial["latitude"][-1]))
    axis.set_xlabel("Longitude (°E)")
    axis.set_ylabel("Latitude (°)")
    axis.grid(alpha=0.12)


def plot_table_event_maps(
    configuration: dict, spatial: dict, events: list[dict], pairing: list[dict]
) -> list[Path]:
    colours = {
        configuration["screened_features"]["H08S"][0]["event_utc"]: "#CC3311",
        configuration["screened_features"]["H08S"][1]["event_utc"]: "#EE9911",
    }
    fig, axes = plt.subplots(1, 2, figsize=(15.8, 7.0), sharex=True, sharey=True)
    celerity = tuple(map(float, configuration["acoustic_celerity_km_s"]))
    tolerance_s = float(configuration["interstation_arrival_tolerance_s"])
    for axis, event in zip(axes, events):
        draw_pdf_base(axis, spatial)
        bearing_difference = np.abs(
            angular_difference_deg(spatial["bearing_h01"], event["bearing_deg"])
        )
        broad = bearing_difference <= float(configuration["bearing_half_widths_deg"]["broad_control"])
        axis.contourf(
            spatial["mesh_lon"],
            spatial["mesh_lat"],
            np.ma.masked_where(~broad, np.ones_like(broad, dtype=float)),
            levels=[0.5, 1.5],
            colors=["#4477AA"],
            alpha=0.20,
        )
        axis.contour(
            spatial["mesh_lon"],
            spatial["mesh_lat"],
            bearing_difference,
            levels=[
                float(configuration["bearing_half_widths_deg"]["formal"]),
                float(configuration["bearing_half_widths_deg"]["broad_control"]),
            ],
            colors=["#225588", "#4477AA"],
            linewidths=[1.35, 0.8],
        )
        for feature in configuration["screened_features"]["H08S"]:
            second = parse_utc(feature["event_utc"]).timestamp()
            lower, upper = range_difference_bounds(
                event["epoch_s"], second, celerity, tolerance_s
            )
            range_mask = (
                (spatial["range_difference"] >= lower)
                & (spatial["range_difference"] <= upper)
            )
            colour = colours[feature["event_utc"]]
            axis.contour(
                spatial["mesh_lon"],
                spatial["mesh_lat"],
                spatial["range_difference"],
                levels=[lower, upper],
                colors=[colour],
                linewidths=1.0,
                linestyles=["--", "--"],
            )
            joint = broad & range_mask
            if np.any(joint):
                axis.contourf(
                    spatial["mesh_lon"],
                    spatial["mesh_lat"],
                    np.ma.masked_where(~joint, np.ones_like(joint, dtype=float)),
                    levels=[0.5, 1.5],
                    colors="none",
                    hatches=["////"],
                )
        broad_rows = [
            row
            for row in pairing
            if row["pair_family"] == "kadri_table_bearing_plus_h08s_screened_time"
            and row["h01w_event_id"] == event["event_id"]
            and row["bearing_control"] == "broad_control"
        ]
        mass_text = "\n".join(
            f"to {row['h08s_screened_arrival_utc'][11:19]}: joint PDF mass "
            f"{100.0 * float(row['independent_pdf_mass_within_joint_bands']):.2f}%"
            for row in broad_rows
        )
        axis.text(
            0.02,
            0.02,
            mass_text,
            transform=axis.transAxes,
            fontsize=8.2,
            va="bottom",
            bbox={"facecolor": "white", "alpha": 0.84, "edgecolor": "none"},
        )
        axis.set_title(
            f"H01W Table 1: {event['time_utc']} UTC, bearing {event['bearing_deg']:.2f}°\n"
            "blue: bearing band; dashed: H08S range-difference timing bands"
        )
    handles = [
        Line2D([0], [0], color="#111111", linewidth=1.4, label="integrated PDF 50/90/99% contours"),
        Line2D([0], [0], color="#009E73", linewidth=1.4, label="seventh BTO arc"),
        Patch(facecolor="#4477AA", alpha=0.20, label="H01W bearing ±3.3° control (inner line ±0.5°)"),
        Line2D([0], [0], color="#CC3311", linestyle="--", label="pair to H08S 01:03:13.15"),
        Line2D([0], [0], color="#EE9911", linestyle="--", label="pair to H08S 01:12:49.50"),
        Patch(facecolor="none", hatch="////", label="bearing ∩ timing band"),
    ]
    fig.legend(
        handles=handles, loc="lower center", bbox_to_anchor=(0.5, 0.060),
        ncol=3, frameon=False, fontsize=8.2,
    )
    fig.suptitle(
        "Conditional geometry of the two Kadri Table 1 times and the screened H08S times",
        fontsize=14.4,
    )
    fig.text(
        0.5,
        0.012,
        "Underlay: independent flight + BTO/BFO/received-power + terminal-flight + drift PDF. Pairings are post-hoc controls; both H08S times occur in Kadri's periodic airgun panels.",
        ha="center",
        fontsize=8.4,
    )
    fig.tight_layout(rect=[0.0, 0.16, 1.0, 0.92])
    return save_figure(fig, "table-event-conditional-geometry")


def plot_screened_pair_maps(
    configuration: dict, spatial: dict, pairing: list[dict]
) -> list[Path]:
    fig, axes = plt.subplots(2, 2, figsize=(14.5, 11.0), sharex=True, sharey=True)
    rows = [
        row for row in pairing
        if row["pair_family"] == "independently_screened_times_without_bearing"
    ]
    for axis, row in zip(axes.ravel(), rows):
        draw_pdf_base(axis, spatial)
        lower = float(row["range_difference_low_km"])
        upper = float(row["range_difference_high_km"])
        mask = (
            (spatial["range_difference"] >= lower)
            & (spatial["range_difference"] <= upper)
        )
        axis.contourf(
            spatial["mesh_lon"],
            spatial["mesh_lat"],
            np.ma.masked_where(~mask, np.ones_like(mask, dtype=float)),
            levels=[0.5, 1.5],
            colors=["#6B4C9A"],
            alpha=0.23,
        )
        axis.contour(
            spatial["mesh_lon"],
            spatial["mesh_lat"],
            spatial["range_difference"],
            levels=[lower, upper],
            colors=["#6B4C9A"],
            linewidths=1.0,
        )
        axis.set_title(
            f"H01W {row['h01w_arrival_utc'][11:19]} → H08S {row['h08s_screened_arrival_utc'][11:19]}\n"
            f"TOA-difference mass {100.0 * float(row['independent_pdf_mass_within_range_band']):.2f}%; "
            f"+ 00:19–00:49 impact-time control {100.0 * float(row['independent_pdf_mass_within_range_and_impact_time']):.2f}%"
        )
    handles = [
        Line2D([0], [0], color="#111111", linewidth=1.4, label="integrated PDF 50/90/99% contours"),
        Line2D([0], [0], color="#009E73", linewidth=1.4, label="seventh BTO arc"),
        Patch(facecolor="#6B4C9A", alpha=0.23, label="range-difference band at 1.43–1.57 km/s, ±5 s"),
    ]
    fig.legend(
        handles=handles, loc="lower center", bbox_to_anchor=(0.5, 0.050),
        ncol=3, frameon=False, fontsize=8.4,
    )
    fig.suptitle(
        "All pairings of the independently screened above-q99 publication-trace times",
        fontsize=14.4,
    )
    fig.text(
        0.5,
        0.012,
        "The timing band uses only the H08S–H01W arrival difference; the second percentage additionally requires a common source during 00:19:37–00:49:37. No recovered bearing is available; H08S features remain in the periodic airgun context.",
        ha="center",
        fontsize=8.4,
    )
    fig.tight_layout(rect=[0.0, 0.12, 1.0, 0.94])
    return save_figure(fig, "screened-event-pair-geometry")


def save_figure(fig: plt.Figure, stem: str) -> list[Path]:
    paths = []
    for suffix in ("png", "pdf"):
        path = OUTPUT / f"{stem}.{suffix}"
        fig.savefig(
            path,
            dpi=280 if suffix == "png" else None,
            metadata=PDF_METADATA if suffix == "pdf" else None,
        )
        paths.append(path)
    plt.close(fig)
    return paths


def plot_trace_audit(
    configuration: dict,
    traces: dict[str, Trace],
    events: list[dict],
    audit_rows: list[dict],
    window_rows: list[dict],
) -> list[Path]:
    fig, axes = plt.subplots(2, 2, figsize=(16.0, 9.2))
    event_colours = {events[0]["event_id"]: "#4477AA", events[1]["event_id"]: "#CC6677"}
    for axis, event in zip(axes[0], events):
        trace = traces["c"]
        relative = trace.epoch_s - event["epoch_s"]
        mask = np.abs(relative) <= 15.0
        axis.plot(relative[mask], trace.pressure_pa[mask], color="#333333", linewidth=0.8)
        axis.axvspan(-5.0, 5.0, color=event_colours[event["event_id"]], alpha=0.10)
        axis.axvline(0.0, color=event_colours[event["event_id"]], linewidth=1.5)
        axis.set_xlabel("Seconds relative to Table 1 time")
        axis.set_ylabel("Plotted pressure (Pa)")
        axis.grid(alpha=0.17)
        score_axis = axis.twinx()
        score_axis.plot(relative[mask], trace.score[mask], color="#6B4C9A", linewidth=0.9, alpha=0.78)
        score_axis.axhline(trace.threshold, color="#A61B29", linestyle="--", linewidth=1.0)
        score_axis.set_ylabel("Robust local-energy score", color="#6B4C9A")
        selected = [
            row for row in audit_rows
            if row["event_id"] == event["event_id"]
        ]
        summary = "; ".join(
            f"±{float(row['search_half_window_s']):g}s: {float(row['local_max_score']):.2f}"
            for row in selected
        )
        axis.set_title(
            f"H01W {event['time_utc']} UTC, {event['bearing_deg']:.2f}°\n"
            f"{summary}; panel q99 = {trace.threshold:.2f}",
            fontsize=10.0,
        )
    broad_windows = {
        row["event_id"]: row
        for row in window_rows
        if row["bearing_control"] == "broad_control"
    }
    for axis, panel_id in zip(axes[1], ("d", "e")):
        trace = traces[panel_id]
        time = np.asarray(
            [datetime.fromtimestamp(value, timezone.utc) for value in trace.epoch_s]
        )
        axis.plot(time, trace.pressure_pa, color="#555555", linewidth=0.42, rasterized=True)
        for event in events:
            row = broad_windows[event["event_id"]]
            lower = parse_utc(row["h08s_arrival_q2p5_utc"])
            upper = parse_utc(row["h08s_arrival_q97p5_utc"])
            axis.axvspan(
                lower,
                upper,
                color=event_colours[event["event_id"]],
                alpha=0.14,
                label=f"from H01W {event['time_utc']} / {event['bearing_deg']:.2f}°",
            )
        feature = next(
            item
            for item in configuration["screened_features"]["H08S"]
            if item["panel"] == panel_id
        )
        event_time = parse_utc(feature["event_utc"])
        axis.axvline(event_time, color="#A61B29", linewidth=1.6)
        axis.annotate(
            f"above-q99 screen {event_time.strftime('%H:%M:%S.%f')[:-3]}\nwithin periodic airgun mask",
            (event_time, 0.96),
            xytext=(5, -8),
            textcoords="offset points",
            transform=axis.get_xaxis_transform(),
            va="top",
            fontsize=8.1,
            color="#A61B29",
        )
        axis.set_ylabel("Plotted pressure (Pa)")
        axis.set_xlabel("UTC on 8 March 2014")
        axis.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M", tz=timezone.utc))
        axis.grid(alpha=0.17)
        axis.set_title(
            f"H08S Figure 9{panel_id}: conditional reception windows and screened periodic feature"
        )
    handles, labels = axes[1, 0].get_legend_handles_labels()
    fig.legend(
        handles, labels, loc="lower center", bbox_to_anchor=(0.5, 0.058),
        ncol=2, frameon=False, fontsize=8.5,
    )
    fig.suptitle(
        "Publication-trace audit of the two Kadri Table 1 times and conditional H08S reception",
        fontsize=14.5,
    )
    fig.text(
        0.5,
        0.012,
        "Top: pressure and the same robust local-energy score used for the catalogue screen. Bottom: filtered publication traces; coloured windows include the 1.43–1.57 km/s celerity range and ±5 s AGW/pick control.",
        ha="center",
        fontsize=8.3,
    )
    fig.tight_layout(rect=[0.0, 0.135, 1.0, 0.94])
    return save_figure(fig, "table-event-trace-and-cross-station-audit")


def main() -> None:
    configuration = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    OUTPUT.mkdir(parents=True, exist_ok=True)
    traces = load_traces(configuration)
    events = load_selected_table_events(configuration)
    audit_rows = audit_table_events(configuration, traces, events)
    spatial = load_spatial(configuration)
    window_rows = conditional_h08_windows(configuration, spatial, events)
    pairing = pairing_rows(configuration, spatial, events)

    audit_path = OUTPUT / "table-event-publication-trace-scores.csv"
    window_path = OUTPUT / "table-event-conditional-h08s-windows.csv"
    pairing_path = OUTPUT / "conditional-event-pair-overlaps.csv"
    write_csv(audit_path, audit_rows)
    write_csv(window_path, window_rows)
    write_csv(pairing_path, pairing)

    paths = [
        audit_path,
        window_path,
        pairing_path,
        *plot_trace_audit(configuration, traces, events, audit_rows, window_rows),
        *plot_table_event_maps(configuration, spatial, events, pairing),
        *plot_screened_pair_maps(configuration, spatial, pairing),
    ]
    summary = {
        "status": "PUBLICATION_TRACE_AND_POST_HOC_GEOMETRY_CONTROL_NOT_EVENT_ASSOCIATION",
        "table_event_results": [
            {
                "event_id": event["event_id"],
                "arrival_utc": f"2014-03-08T{event['time_utc']}Z",
                "bearing_deg": event["bearing_deg"],
                "above_panel_q99_at_any_tested_half_window": any(
                    row["above_panel_q99"]
                    for row in audit_rows
                    if row["event_id"] == event["event_id"]
                ),
                "broad_bearing_conditional_h08s_window": next(
                    {
                        "q2p5_utc": row["h08s_arrival_q2p5_utc"],
                        "median_utc": row["h08s_arrival_median_utc"],
                        "q97p5_utc": row["h08s_arrival_q97p5_utc"],
                    }
                    for row in window_rows
                    if row["event_id"] == event["event_id"]
                    and row["bearing_control"] == "broad_control"
                ),
            }
            for event in events
        ],
        "screened_h08s_context": [
            {
                "arrival_utc": feature["event_utc"],
                "above_publication_panel_q99": True,
                "periodic_context": feature["periodic_context"],
            }
            for feature in configuration["screened_features"]["H08S"]
        ],
        "interpretation": [
            "neither selected Table 1 time is above the publication-panel q99 screen within ±2, ±5 or ±10 seconds",
            "the 01:03:13.150 H08S feature is too early for the central 95% conditional timing windows of either selected Table 1 bearing",
            "the 01:12:49.500 H08S feature lies inside the broad 95% conditional window for the 00:53:31 bearing, but outside it for 00:49:58, and is within the periodic airgun mask",
            "range-difference and bearing intersections are compatibility regions, not source associations or posterior evidence",
        ],
    }
    summary_path = OUTPUT / "event-pair-analysis-summary.json"
    summary_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    paths.append(summary_path)
    manifest = {
        "status": "REPRODUCIBLE_OUTPUT_HASHES",
        "inputs": {
            str(path.relative_to(HERE)): sha256(path)
            for path in (
                CONFIG_PATH,
                METADATA_PATH,
                TABLE_PATH,
                CANDIDATE_PATH,
                GRID_PATH,
                ARC_PATH,
                FILTERED_H08_PATH,
            )
        },
        "code": {str(Path(__file__).relative_to(HERE)): sha256(Path(__file__))},
        "outputs": {path.name: sha256(path) for path in paths},
    }
    manifest_path = OUTPUT / "event-pair-analysis-manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
