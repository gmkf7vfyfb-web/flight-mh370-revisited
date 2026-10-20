#!/usr/bin/env python3
"""Render matched source and family-conditioned crash diagnostics.

This supporting report applies the same source-prior removal and nearest-cell
composition used by the canonical Rust runner.  It deliberately does not pool
ocean-current families or flight-control families without estimated model
weights.
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import hashlib
import json
import math
import resource
import sys
import time
from dataclasses import dataclass
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.lines import Line2D


LEVELS = (0.50, 0.90, 0.95, 0.99)
EARTH_RADIUS_NM = 3_440.065
MAXIMUM_CELL_DISTANCE_NM = 75.0
NAVY = "#17365D"
NATIVE_BLUE = "#2F75B5"
CMEMS_ORANGE = "#D97706"
GDP_PURPLE = "#6D5AA7"
FLIGHT_GREY = "#4B5563"
LIGHT_GREY = "#D1D5DB"
PALE_GREY = "#F3F4F6"


@dataclass(frozen=True)
class FlightInput:
    name: str
    label: str
    marker: str
    suite_summary: Path
    posterior_paths: tuple[Path, ...]


@dataclass
class FlightParticles:
    specification: FlightInput
    latitude_deg: np.ndarray
    longitude_deg: np.ndarray
    weight: np.ndarray
    input_records: list[dict]
    suite_record: dict


@dataclass
class SourceProfile:
    key: str
    label: str
    color: str
    path: Path
    document: dict
    cell_ids: list[str]
    latitude_deg: np.ndarray
    longitude_deg: np.ndarray
    prior_weight: np.ndarray
    evidence_log_likelihood: np.ndarray
    normalized_weight: np.ndarray
    arrival_ess: np.ndarray
    probability_floor: np.ndarray


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def normalized(weights: np.ndarray) -> np.ndarray:
    if np.any(~np.isfinite(weights)) or np.any(weights < 0.0):
        raise ValueError("weights must be finite and non-negative")
    total = float(np.sum(weights))
    if not math.isfinite(total) or total <= 0.0:
        raise ValueError("weights do not have positive finite mass")
    return weights / total


def effective_sample_size(weights: np.ndarray) -> float:
    total = float(np.sum(weights))
    squares = float(np.sum(weights * weights))
    return total * total / squares if squares > 0.0 else 0.0


def weighted_quantile(
    values: np.ndarray, weights: np.ndarray, probability: float
) -> float:
    order = np.argsort(values, kind="stable")
    ordered_values = values[order]
    ordered_weights = normalized(weights[order])
    cumulative = np.cumsum(ordered_weights)
    index = int(np.searchsorted(cumulative, probability, side="left"))
    return float(ordered_values[min(index, len(ordered_values) - 1)])


def equal_tail_intervals(
    values: np.ndarray, weights: np.ndarray
) -> dict[str, dict[str, float]]:
    result = {}
    for level in LEVELS:
        tail = 0.5 * (1.0 - level)
        result[f"{int(100 * level)}"] = {
            "lower": weighted_quantile(values, weights, tail),
            "upper": weighted_quantile(values, weights, 1.0 - tail),
        }
    return result


def haversine_distance_matrix_nm(
    latitude_deg: np.ndarray,
    longitude_deg: np.ndarray,
    cell_latitude_deg: np.ndarray,
    cell_longitude_deg: np.ndarray,
) -> np.ndarray:
    latitude = np.radians(latitude_deg)[:, None]
    cell_latitude = np.radians(cell_latitude_deg)[None, :]
    delta_latitude = cell_latitude - latitude
    delta_longitude = np.radians(
        cell_longitude_deg[None, :] - longitude_deg[:, None]
    )
    haversine = np.sin(delta_latitude / 2.0) ** 2 + np.cos(latitude) * np.cos(
        cell_latitude
    ) * np.sin(delta_longitude / 2.0) ** 2
    haversine = np.clip(haversine, 0.0, 1.0)
    return 2.0 * EARTH_RADIUS_NM * np.arcsin(np.sqrt(haversine))


def load_source(key: str, label: str, color: str, path: Path) -> SourceProfile:
    document = json.loads(path.read_text(encoding="utf-8"))
    cells = document["cells"]
    if not cells or not document.get("isotope_enabled", False):
        raise ValueError(f"{path} is not a non-empty isotope-screened source result")
    combined = [cell.get("combined_log_weight") for cell in cells]
    evidence = np.array(
        [
            -math.inf
            if value is None
            else float(value) - math.log(float(cell["prior_weight"]))
            for cell, value in zip(cells, combined)
        ],
        dtype=float,
    )
    arrival_ess = np.array(
        [
            max(
                (
                    float(recovery["effective_sample_size"])
                    for recovery in cell.get("recoveries", [])
                    if recovery.get("is_flaperon", False)
                ),
                default=0.0,
            )
            for cell in cells
        ],
        dtype=float,
    )
    debris_log = np.array(
        [float(cell["debris_log_compatibility"]) for cell in cells], dtype=float
    )
    # The canonical source configurations use a 1e-9 encounter floor.  The
    # tolerance also catches values whose isotope screen differs only at roundoff.
    floor_log = math.log(1e-9)
    return SourceProfile(
        key=key,
        label=label,
        color=color,
        path=path,
        document=document,
        cell_ids=[str(cell["id"]) for cell in cells],
        latitude_deg=np.array(
            [float(cell["position"]["latitude"]) for cell in cells], dtype=float
        ),
        longitude_deg=np.array(
            [float(cell["position"]["longitude"]) for cell in cells], dtype=float
        ),
        prior_weight=np.array(
            [float(cell["prior_weight"]) for cell in cells], dtype=float
        ),
        evidence_log_likelihood=evidence,
        normalized_weight=normalized(
            np.array([float(cell["normalized_weight"]) for cell in cells])
        ),
        arrival_ess=arrival_ess,
        probability_floor=debris_log <= floor_log + 1e-6,
    )


def validate_matched_sources(native: SourceProfile, cmems: SourceProfile) -> None:
    if native.cell_ids != cmems.cell_ids:
        raise ValueError("matched source families do not use identical source cells")
    if not np.allclose(native.latitude_deg, cmems.latitude_deg, atol=0.0, rtol=0.0):
        raise ValueError("matched source latitudes differ")
    if not np.allclose(native.longitude_deg, cmems.longitude_deg, atol=0.0, rtol=0.0):
        raise ValueError("matched source longitudes differ")
    for field in ("seed", "particles_per_cell", "isotope_enabled"):
        if native.document[field] != cmems.document[field]:
            raise ValueError(f"matched source field differs: {field}")


def read_posterior(path: Path) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    with path.open(newline="", encoding="utf-8") as stream:
        header = next(csv.reader(stream))
    required = ("weight", "impact_latitude_deg", "impact_longitude_deg")
    try:
        columns = tuple(header.index(name) for name in required)
    except ValueError as error:
        raise ValueError(f"{path} lacks a required posterior column") from error
    values = np.loadtxt(path, delimiter=",", skiprows=1, usecols=columns, ndmin=2)
    if values.shape[0] == 0:
        raise ValueError(f"{path} contains no posterior particles")
    return values[:, 1], values[:, 2], values[:, 0]


def load_flight(specification: FlightInput) -> FlightParticles:
    suite = json.loads(specification.suite_summary.read_text(encoding="utf-8"))
    matches = [
        family
        for family in suite["families"]
        if family["name"] == specification.name
    ]
    if len(matches) != 1 or not matches[0].get("converged", False):
        raise ValueError(f"selected flight family is not converged: {specification.name}")
    latitudes = []
    longitudes = []
    weights = []
    records = []
    for path in specification.posterior_paths:
        latitude, longitude, weight = read_posterior(path)
        latitudes.append(latitude)
        longitudes.append(longitude)
        # Equal seed-family weight, matching the runner's pooled report logic.
        weights.append(normalized(weight) / len(specification.posterior_paths))
        records.append(
            {
                "path": str(path),
                "sha256": sha256(path),
                "particles": int(len(weight)),
            }
        )
    result = FlightParticles(
        specification=specification,
        latitude_deg=np.concatenate(latitudes),
        longitude_deg=np.concatenate(longitudes),
        weight=normalized(np.concatenate(weights)),
        input_records=records,
        suite_record={
            "path": str(specification.suite_summary),
            "sha256": sha256(specification.suite_summary),
            "status": suite["status"],
            "family_converged": True,
            "maximum_seed_mean_separation_nm": float(
                matches[0]["maximum_seed_mean_separation_nm"]
            ),
            "log_evidence_range": float(matches[0]["log_evidence_range"]),
        },
    )
    if int(matches[0]["pooled_particles"]) != len(result.weight):
        raise ValueError("suite particle count does not match posterior CSV inputs")
    return result


def summarize_distribution(
    latitude_deg: np.ndarray,
    longitude_deg: np.ndarray,
    weights: np.ndarray,
) -> dict:
    weights = normalized(weights)
    latitude_s = -latitude_deg
    return {
        "particles": int(len(weights)),
        "effective_sample_size": effective_sample_size(weights),
        "mean_latitude_s": float(np.sum(latitude_s * weights)),
        "mean_longitude_e": float(np.sum(longitude_deg * weights)),
        "latitude_equal_tail": equal_tail_intervals(latitude_s, weights),
        "longitude_equal_tail": equal_tail_intervals(longitude_deg, weights),
    }


def summarize_source(source: SourceProfile) -> dict:
    latitude_s = -source.latitude_deg
    peak = int(np.argmax(source.normalized_weight))
    entropy = -float(
        np.sum(
            source.normalized_weight[source.normalized_weight > 0.0]
            * np.log(source.normalized_weight[source.normalized_weight > 0.0])
        )
    )
    return {
        "family": source.document["family"],
        "seed": int(source.document["seed"]),
        "particles_per_cell": int(source.document["particles_per_cell"]),
        "isotope_enabled": bool(source.document["isotope_enabled"]),
        "peak_cell": source.cell_ids[peak],
        "peak_latitude_s": float(latitude_s[peak]),
        "peak_longitude_e": float(source.longitude_deg[peak]),
        "equal_tail": equal_tail_intervals(latitude_s, source.normalized_weight),
        "entropy_effective_cells": math.exp(entropy),
        "mean_importance_weighted_terminated_fraction": float(
            source.document["mean_terminated_fraction"]
        ),
        "maximum_arrival_effective_sample_size": float(np.max(source.arrival_ess)),
        "median_arrival_effective_sample_size": float(np.median(source.arrival_ess)),
        "source_mass_arrival_ess_at_least_100": float(
            np.sum(source.normalized_weight[source.arrival_ess >= 100.0])
        ),
        "source_mass_arrival_ess_at_least_200": float(
            np.sum(source.normalized_weight[source.arrival_ess >= 200.0])
        ),
        "probability_floor_source_mass": float(
            np.sum(source.normalized_weight[source.probability_floor])
        ),
    }


def apply_source(
    flight: FlightParticles, source: SourceProfile
) -> tuple[np.ndarray, np.ndarray, np.ndarray, dict]:
    nearest = np.empty(len(flight.weight), dtype=np.int32)
    distances = np.empty(len(flight.weight), dtype=float)
    chunk_size = 20_000
    for start in range(0, len(flight.weight), chunk_size):
        stop = min(start + chunk_size, len(flight.weight))
        matrix = haversine_distance_matrix_nm(
            flight.latitude_deg[start:stop],
            flight.longitude_deg[start:stop],
            source.latitude_deg,
            source.longitude_deg,
        )
        selected = np.argmin(matrix, axis=1)
        nearest[start:stop] = selected
        distances[start:stop] = matrix[np.arange(stop - start), selected]
    maximum_distance = float(np.max(distances))
    if maximum_distance > MAXIMUM_CELL_DISTANCE_NM:
        raise ValueError(
            "flight posterior lies outside source support by "
            f"{maximum_distance:.1f} nm (limit {MAXIMUM_CELL_DISTANCE_NM:.1f} nm)"
        )
    log_weight = np.full(len(flight.weight), -math.inf, dtype=float)
    positive = flight.weight > 0.0
    selected_evidence = source.evidence_log_likelihood[nearest]
    finite = positive & np.isfinite(selected_evidence)
    log_weight[finite] = np.log(flight.weight[finite]) + selected_evidence[finite]
    maximum = float(np.max(log_weight))
    if not math.isfinite(maximum):
        raise ValueError("source evidence gives zero support to all flight particles")
    conditioned = np.zeros(len(flight.weight), dtype=float)
    conditioned[finite] = np.exp(log_weight[finite] - maximum)
    conditioned = normalized(conditioned)
    summary = summarize_distribution(
        flight.latitude_deg, flight.longitude_deg, conditioned
    )
    summary.update(
        {
            "current_family": source.document["family"],
            "flight_family": flight.specification.name,
            "before_effective_sample_size": effective_sample_size(flight.weight),
            "after_effective_sample_size": effective_sample_size(conditioned),
            "zero_likelihood_particles": int(np.count_nonzero(~finite)),
            "maximum_cell_distance_nm": maximum_distance,
            "conditioned_mass_on_source_arrival_ess_at_least_100": float(
                np.sum(conditioned[source.arrival_ess[nearest] >= 100.0])
            ),
            "conditioned_mass_on_source_arrival_ess_at_least_200": float(
                np.sum(conditioned[source.arrival_ess[nearest] >= 200.0])
            ),
            "conditioned_mass_on_probability_floor_cells": float(
                np.sum(conditioned[source.probability_floor[nearest]])
            ),
            "median_assigned_source_arrival_ess": weighted_quantile(
                source.arrival_ess[nearest], conditioned, 0.5
            ),
            "composition": (
                "normalized flight posterior times source combined_log_weight "
                "after removing source prior; nearest source cell on the legacy "
                "3440.065-nm sphere"
            ),
            "scientific_status": "diagnostic_only_not_calibrated",
        }
    )
    if summary["after_effective_sample_size"] < 100.0:
        summary["numerical_note"] = "severe_posthoc_importance_collapse"
    else:
        summary["numerical_note"] = "posthoc_particle_ess_reported"
    if summary["conditioned_mass_on_source_arrival_ess_at_least_100"] < 0.9:
        summary["source_support_note"] = (
            "combined mass depends materially on source cells with fewer than "
            "100 effective Reunion arrivals"
        )
    else:
        summary["source_support_note"] = (
            "at least 90% of combined mass maps to source cells with arrival ESS >=100"
        )
    return conditioned, nearest, distances, summary


def compare_sources(native: SourceProfile, cmems: SourceProfile) -> dict:
    left = native.normalized_weight
    right = cmems.normalized_weight
    midpoint = 0.5 * (left + right)

    def kl(values: np.ndarray) -> float:
        selected = values > 0.0
        return float(np.sum(values[selected] * np.log(values[selected] / midpoint[selected])))

    return {
        "total_variation": 0.5 * float(np.sum(np.abs(left - right))),
        "bhattacharyya_coefficient": float(np.sum(np.sqrt(left * right))),
        "jensen_shannon_nats": 0.5 * (kl(left) + kl(right)),
        "interpretation": (
            "case-matched currents-only families share a northern mode but retain "
            "materially different profile shapes; they are not pooled"
        ),
    }


def profile_xy(source: SourceProfile) -> tuple[np.ndarray, np.ndarray]:
    order = np.argsort(-source.latitude_deg)
    return -source.latitude_deg[order], source.normalized_weight[order]


def draw_interval(
    axis,
    y: float,
    interval: dict[str, float],
    color: str,
    linewidth: float,
    linestyle: str = "-",
) -> None:
    axis.plot(
        [interval["lower"], interval["upper"]],
        [y, y],
        color=color,
        linewidth=linewidth,
        linestyle=linestyle,
        solid_capstyle="butt",
    )


def configure_style() -> None:
    matplotlib.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "font.size": 9.3,
            "axes.titlesize": 12.5,
            "axes.labelsize": 10.5,
            "axes.edgecolor": "#374151",
            "axes.linewidth": 0.8,
            "axes.grid": True,
            "grid.color": LIGHT_GREY,
            "grid.linewidth": 0.6,
            "grid.alpha": 0.8,
            "legend.frameon": False,
            "svg.hashsalt": "mh370-family-conditioned-source-crash",
        }
    )


def render_summary_page(
    sources: list[SourceProfile],
    source_summaries: dict[str, dict],
    flights: list[FlightParticles],
    flight_summaries: dict[str, dict],
    conditioned: dict[tuple[str, str], dict],
) -> tuple[plt.Figure, dict]:
    figure = plt.figure(figsize=(15.0, 10.5), facecolor="white")
    grid = figure.add_gridspec(
        2, 2, height_ratios=(1.0, 1.45), width_ratios=(1.0, 1.0), hspace=0.34, wspace=0.24
    )
    profile_axis = figure.add_subplot(grid[0, 0])
    map_axis = figure.add_subplot(grid[0, 1])
    lane_axis = figure.add_subplot(grid[1, :])

    for source in sources:
        x, y = profile_xy(source)
        linestyle = "--" if source.key == "gdp" else "-"
        linewidth = 1.6 if source.key == "gdp" else 2.2
        profile_axis.step(
            x,
            y,
            where="mid",
            color=source.color,
            linewidth=linewidth,
            linestyle=linestyle,
            label=source.label,
        )
    profile_axis.set_title("A  Source-area probability mass", loc="left", fontweight="bold")
    profile_axis.set_xlabel("Seventh-arc latitude (degrees south)")
    profile_axis.set_ylabel("Normalized mass per arc cell", labelpad=22)
    profile_axis.yaxis.set_label_coords(-0.105, 0.5)
    profile_axis.set_xlim(9.5, 44.5)
    profile_axis.set_ylim(bottom=0.0)
    profile_axis.spines[["top", "right"]].set_visible(False)
    profile_axis.legend(fontsize=8.2, loc="upper right")
    profile_axis.text(
        0.02,
        0.96,
        "Matched current-only modes:\n"
        f"native {source_summaries['native']['peak_latitude_s']:.1f}°S; "
        f"CMEMS {source_summaries['cmems']['peak_latitude_s']:.1f}°S",
        transform=profile_axis.transAxes,
        ha="left",
        va="top",
        fontsize=8.4,
        color=NAVY,
        bbox={"boxstyle": "round,pad=0.3", "facecolor": "white", "edgecolor": LIGHT_GREY},
    )

    arc = sources[0]
    order = np.argsort(-arc.latitude_deg)
    map_axis.plot(
        arc.longitude_deg[order],
        arc.latitude_deg[order],
        color="#9CA3AF",
        linewidth=1.4,
        label="Seventh-arc source cells",
        zorder=1,
    )
    for source in sources[:2]:
        summary = source_summaries[source.key]
        map_axis.scatter(
            [summary["peak_longitude_e"]],
            [-summary["peak_latitude_s"]],
            marker="*",
            s=125,
            color=source.color,
            edgecolor="white",
            linewidth=0.8,
            zorder=6,
            label=f"{source.label} source mode",
        )
    for flight in flights:
        base = flight_summaries[flight.specification.name]
        map_axis.scatter(
            [base["mean_longitude_e"]],
            [-base["mean_latitude_s"]],
            marker=flight.specification.marker,
            s=36,
            color=FLIGHT_GREY,
            alpha=0.65,
            zorder=3,
        )
        for source in sources[:2]:
            summary = conditioned[(flight.specification.name, source.key)]
            map_axis.scatter(
                [summary["mean_longitude_e"]],
                [-summary["mean_latitude_s"]],
                marker=flight.specification.marker,
                s=55,
                facecolor=source.color,
                edgecolor="white",
                linewidth=0.7,
                zorder=5,
            )
    map_axis.set_title("B  Source modes and flight-conditioned means", loc="left", fontweight="bold")
    map_axis.set_xlabel("Longitude (degrees east)")
    map_axis.set_ylabel("Latitude (degrees)")
    map_axis.set_xlim(84.0, 109.0)
    map_axis.set_ylim(-40.0, -8.0)
    map_axis.spines[["top", "right"]].set_visible(False)
    map_axis.text(
        0.02,
        0.97,
        "Stars: drift-only source modes\nSymbols: flight family means after conditioning",
        transform=map_axis.transAxes,
        ha="left",
        va="top",
        fontsize=8.1,
        color=FLIGHT_GREY,
        bbox={"boxstyle": "round,pad=0.3", "facecolor": "white", "edgecolor": LIGHT_GREY},
    )

    source_rows = [source for source in sources]
    lane_labels = [source.label for source in source_rows] + [
        flight.specification.label for flight in flights
    ]
    y_values = list(reversed(range(len(lane_labels))))
    for y, source in zip(y_values, source_rows):
        summary = source_summaries[source.key]
        draw_interval(lane_axis, y, summary["equal_tail"]["99"], source.color, 2.0, ":")
        draw_interval(lane_axis, y, summary["equal_tail"]["95"], source.color, 4.0, "-")
        draw_interval(lane_axis, y, summary["equal_tail"]["90"], source.color, 7.0, "-")
        lane_axis.scatter(
            [summary["peak_latitude_s"]], [y], marker="*", s=75, color=source.color, zorder=6
        )
    flight_start = len(source_rows)
    for row_index, flight in enumerate(flights, start=flight_start):
        y = y_values[row_index]
        base = flight_summaries[flight.specification.name]
        draw_interval(lane_axis, y + 0.20, base["latitude_equal_tail"]["90"], FLIGHT_GREY, 3.0)
        lane_axis.scatter([base["mean_latitude_s"]], [y + 0.20], s=22, color=FLIGHT_GREY, zorder=5)
        for offset, source in ((0.0, sources[0]), (-0.20, sources[1])):
            summary = conditioned[(flight.specification.name, source.key)]
            draw_interval(
                lane_axis,
                y + offset,
                summary["latitude_equal_tail"]["90"],
                source.color,
                4.2,
            )
            lane_axis.scatter(
                [summary["mean_latitude_s"]],
                [y + offset],
                marker=flight.specification.marker,
                s=30,
                color=source.color,
                edgecolor="white",
                linewidth=0.5,
                zorder=6,
            )
    lane_axis.axhline(y_values[len(source_rows) - 1] - 0.55, color="#9CA3AF", linewidth=0.8)
    lane_axis.set_yticks(y_values, labels=lane_labels)
    lane_axis.tick_params(axis="y", pad=8, length=0)
    lane_axis.set_xlim(9.5, 44.5)
    lane_axis.set_ylim(-0.7, y_values[0] + 0.7)
    lane_axis.set_xlabel("Seventh-arc latitude (degrees south)", labelpad=8)
    lane_axis.set_title(
        "C  Source intervals and inferred crash-location intervals",
        loc="left",
        fontweight="bold",
    )
    lane_axis.spines[["top", "right", "left"]].set_visible(False)
    lane_axis.grid(axis="y", visible=False)
    lane_axis.xaxis.set_major_locator(matplotlib.ticker.MultipleLocator(5.0))
    lane_axis.xaxis.set_minor_locator(matplotlib.ticker.MultipleLocator(1.0))
    handles = [
        Line2D([0], [0], color=FLIGHT_GREY, linewidth=3, label="Flight evidence only (90%)"),
        Line2D([0], [0], color=NATIVE_BLUE, linewidth=4, label="+ native HYCOM current-only (90%)"),
        Line2D([0], [0], color=CMEMS_ORANGE, linewidth=4, label="+ CMEMS current-only (90%)"),
        Line2D([0], [0], color=GDP_PURPLE, linestyle="--", linewidth=2, label="GDP+Stokes source sensitivity; not applied"),
    ]
    lane_axis.legend(
        handles=handles,
        loc="lower left",
        bbox_to_anchor=(0.0, -0.28),
        ncol=2,
        fontsize=8.2,
    )

    figure.suptitle(
        "MH370 flaperon source and inferred crash-location diagnostics",
        x=0.18,
        y=0.975,
        ha="left",
        fontsize=18,
        fontweight="bold",
        color=NAVY,
    )
    figure.text(
        0.18,
        0.947,
        "Matched 8,192-particle currents-only source runs; four converged flight-control families; no family pooling",
        ha="left",
        va="top",
        fontsize=10.2,
        color=FLIGHT_GREY,
    )
    figure.text(
        0.18,
        0.018,
        "Diagnostic only. A source cell is a candidate crash point only conditional on seventh-arc release at impact.\n"
        "The flight overlap lies in weakly sampled drift tails, so these curves are not an accepted narrow crash posterior.",
        ha="left",
        va="bottom",
        fontsize=7.9,
        color=FLIGHT_GREY,
    )
    figure.subplots_adjust(left=0.18, right=0.975, top=0.895, bottom=0.145)
    figure.canvas.draw()
    renderer = figure.canvas.get_renderer()
    y_label_box = profile_axis.yaxis.label.get_window_extent(renderer)
    tick_boxes = [
        label.get_window_extent(renderer)
        for label in profile_axis.get_yticklabels()
        if label.get_visible() and label.get_text()
    ]
    gap = min(box.x0 for box in tick_boxes) - y_label_box.x1
    lane_boxes = [
        label.get_window_extent(renderer)
        for label in lane_axis.get_yticklabels()
        if label.get_visible() and label.get_text()
    ]
    audit = {
        "profile_y_label_to_tick_gap_pixels": float(gap),
        "profile_y_label_does_not_overlap_ticks": bool(gap >= 8.0),
        "lane_labels_inside_canvas": bool(min(box.x0 for box in lane_boxes) >= 0.0),
    }
    audit["all_pass"] = all(audit[key] for key in audit if key != "profile_y_label_to_tick_gap_pixels")
    if not audit["all_pass"]:
        raise RuntimeError(f"summary layout audit failed: {audit}")
    return figure, audit


def histogram_density(
    values: np.ndarray, weights: np.ndarray, edges: np.ndarray
) -> tuple[np.ndarray, np.ndarray]:
    counts, _ = np.histogram(values, bins=edges, weights=normalized(weights))
    widths = np.diff(edges)
    centers = 0.5 * (edges[:-1] + edges[1:])
    return centers, counts / widths


def render_density_page(
    flights: list[FlightParticles],
    sources: list[SourceProfile],
    conditioned_weights: dict[tuple[str, str], np.ndarray],
    conditioned: dict[tuple[str, str], dict],
) -> plt.Figure:
    figure, axes = plt.subplots(2, 2, figsize=(15.0, 10.5), facecolor="white")
    edges = np.arange(30.0, 39.05, 0.05)
    for axis, flight in zip(axes.flat, flights):
        latitude_s = -flight.latitude_deg
        x, y = histogram_density(latitude_s, flight.weight, edges)
        axis.step(x, y, where="mid", color=FLIGHT_GREY, linewidth=1.7, label="Flight only")
        for source in sources[:2]:
            weights = conditioned_weights[(flight.specification.name, source.key)]
            x, y = histogram_density(latitude_s, weights, edges)
            axis.step(x, y, where="mid", color=source.color, linewidth=2.0, label=f"+ {source.label}")
        native = conditioned[(flight.specification.name, "native")]
        cmems = conditioned[(flight.specification.name, "cmems")]
        axis.set_title(flight.specification.label, loc="left", fontweight="bold")
        axis.set_xlabel("Inferred impact latitude (degrees south)")
        axis.set_ylabel("Probability density per degree")
        axis.set_xlim(30.5, 38.5)
        axis.set_ylim(bottom=0.0)
        axis.spines[["top", "right"]].set_visible(False)
        axis.text(
            0.02,
            0.97,
            f"Native: mean {native['mean_latitude_s']:.2f}°S, ESS {native['after_effective_sample_size']:.0f}, "
            f"arrival-ESS≥100 mass {100*native['conditioned_mass_on_source_arrival_ess_at_least_100']:.0f}%\n"
            f"CMEMS: mean {cmems['mean_latitude_s']:.2f}°S, ESS {cmems['after_effective_sample_size']:.0f}, "
            f"arrival-ESS≥100 mass {100*cmems['conditioned_mass_on_source_arrival_ess_at_least_100']:.0f}%",
            transform=axis.transAxes,
            ha="left",
            va="top",
            fontsize=7.8,
            color=FLIGHT_GREY,
            bbox={"boxstyle": "round,pad=0.3", "facecolor": "white", "edgecolor": LIGHT_GREY},
        )
    axes.flat[0].legend(loc="upper right", fontsize=8.0)
    figure.suptitle(
        "Flight-family-conditioned crash-location densities",
        x=0.07,
        y=0.975,
        ha="left",
        fontsize=18,
        fontweight="bold",
        color=NAVY,
    )
    figure.text(
        0.07,
        0.945,
        "Each panel multiplies one converged flight posterior by one source-family likelihood after removing the source prior",
        ha="left",
        fontsize=10.0,
        color=FLIGHT_GREY,
    )
    figure.text(
        0.07,
        0.018,
        "The jagged changes are native source-cell likelihoods, not a smoothed fit. Low arrival-ESS mass and probability-floor dependence are retained, not hidden.",
        ha="left",
        fontsize=8.4,
        color=FLIGHT_GREY,
    )
    figure.subplots_adjust(left=0.07, right=0.975, top=0.90, bottom=0.09, hspace=0.28, wspace=0.20)
    return figure


def concise_interval(interval: dict[str, float]) -> str:
    return f"{interval['lower']:.2f}–{interval['upper']:.2f}"


def render_status_page(
    source_summaries: dict[str, dict],
    flights: list[FlightParticles],
    conditioned: dict[tuple[str, str], dict],
    matched: dict,
) -> plt.Figure:
    figure = plt.figure(figsize=(15.0, 10.5), facecolor="white")
    axis = figure.add_axes([0.045, 0.07, 0.91, 0.82])
    axis.axis("off")
    figure.suptitle(
        "Quantitative status and interpretation",
        x=0.055,
        y=0.97,
        ha="left",
        fontsize=18,
        fontweight="bold",
        color=NAVY,
    )
    figure.text(
        0.055,
        0.925,
        "The source and crash concepts are related but not interchangeable",
        ha="left",
        fontsize=12,
        fontweight="bold",
        color=NAVY,
    )
    interpretation = (
        "A drift source cell is the simulated flaperon's release point on the seventh arc. It is also a candidate crash point "
        "only if the flaperon separated at impact at 00:19 UTC. Source-only mass uses debris recovery, the conservative isotope "
        "screen, and its explicit arc prior; it does not yet enforce flight feasibility. The inferred crash rows below multiply "
        "the converged flight posterior by the source likelihood after removing that source prior. No HYCOM/CMEMS or autopilot-family "
        "weight has been invented."
    )
    figure.text(0.055, 0.892, interpretation, ha="left", va="top", fontsize=9.2, color=FLIGHT_GREY, wrap=True)

    source_columns = ["Current family", "Mode °S", "90% °S", "95% °S", "99% °S", "Terminated", "Max arrival ESS", "Mass ESS≥200"]
    source_rows = []
    for key in ("native", "cmems", "gdp"):
        summary = source_summaries[key]
        source_rows.append(
            [
                {"native": "Native HYCOM current-only", "cmems": "CMEMS current-only", "gdp": "GDP + coarse Stokes sensitivity"}[key],
                f"{summary['peak_latitude_s']:.2f}",
                concise_interval(summary["equal_tail"]["90"]),
                concise_interval(summary["equal_tail"]["95"]),
                concise_interval(summary["equal_tail"]["99"]),
                f"{100*summary['mean_importance_weighted_terminated_fraction']:.1f}%",
                f"{summary['maximum_arrival_effective_sample_size']:.0f}",
                f"{100*summary['source_mass_arrival_ess_at_least_200']:.0f}%",
            ]
        )
    source_table = axis.table(
        cellText=source_rows,
        colLabels=source_columns,
        cellLoc="center",
        colLoc="center",
        bbox=[0.0, 0.58, 1.0, 0.20],
        colWidths=[0.22, 0.08, 0.12, 0.12, 0.12, 0.10, 0.12, 0.12],
    )
    source_table.auto_set_font_size(False)
    source_table.set_fontsize(7.8)
    for (row, column), cell in source_table.get_celld().items():
        cell.set_edgecolor(LIGHT_GREY)
        if row == 0:
            cell.set_facecolor(NAVY)
            cell.get_text().set_color("white")
            cell.get_text().set_fontweight("bold")
        elif row % 2 == 0:
            cell.set_facecolor(PALE_GREY)
        if column == 0 and row > 0:
            cell.get_text().set_ha("left")

    crash_columns = ["Flight family", "Current", "Mean °S / °E", "90% latitude °S", "Post-hoc ESS", "Mass source ESS≥100 / ≥200", "Floor-cell mass"]
    crash_rows = []
    for flight in flights:
        for source_key, source_label in (("native", "Native"), ("cmems", "CMEMS")):
            summary = conditioned[(flight.specification.name, source_key)]
            crash_rows.append(
                [
                    flight.specification.label,
                    source_label,
                    f"{summary['mean_latitude_s']:.2f} / {summary['mean_longitude_e']:.2f}",
                    concise_interval(summary["latitude_equal_tail"]["90"]),
                    f"{summary['after_effective_sample_size']:.0f}",
                    f"{100*summary['conditioned_mass_on_source_arrival_ess_at_least_100']:.0f}% / "
                    f"{100*summary['conditioned_mass_on_source_arrival_ess_at_least_200']:.0f}%",
                    f"{100*summary['conditioned_mass_on_probability_floor_cells']:.1f}%",
                ]
            )
    crash_table = axis.table(
        cellText=crash_rows,
        colLabels=crash_columns,
        cellLoc="center",
        colLoc="center",
        bbox=[0.0, 0.15, 1.0, 0.34],
        colWidths=[0.24, 0.09, 0.15, 0.16, 0.10, 0.15, 0.11],
    )
    crash_table.auto_set_font_size(False)
    crash_table.set_fontsize(7.7)
    for (row, column), cell in crash_table.get_celld().items():
        cell.set_edgecolor(LIGHT_GREY)
        if row == 0:
            cell.set_facecolor(NAVY)
            cell.get_text().set_color("white")
            cell.get_text().set_fontweight("bold")
        elif row % 2 == 0:
            cell.set_facecolor(PALE_GREY)
        if column == 0 and row > 0:
            cell.get_text().set_ha("left")

    figure.text(0.055, 0.695, "Matched source-family diagnostics", ha="left", fontsize=11, fontweight="bold", color=NAVY)
    figure.text(0.055, 0.510, "Post-hoc family-conditioned inferred crash locations", ha="left", fontsize=11, fontweight="bold", color=NAVY)
    figure.text(
        0.055,
        0.116,
        "Decision: diagnostic only — do not publish a single narrow crash posterior. "
        f"Native versus CMEMS source TV is {matched['total_variation']:.3f} (overlap coefficient {matched['bhattacharyya_coefficient']:.3f}). "
        "The flight families occupy ~32–37°S, while drift-only modes are ~13–14°S. Their intersections rely on the southern drift tails; "
        "several CMEMS combinations depend on arrival ESS near one or the recovery probability floor, and one post-hoc family collapses to only tens of effective particles.",
        ha="left",
        va="top",
        fontsize=9.0,
        color="#991B1B",
        wrap=True,
    )
    figure.text(
        0.055,
        0.035,
        "GDP remains visible as a separate sensitivity but is not applied: about 61% of its importance-weighted paths terminate at missing field coverage and its replicated shape is unstable.",
        ha="left",
        fontsize=8.3,
        color=FLIGHT_GREY,
    )
    return figure


def write_csv(
    path: Path,
    source_summaries: dict[str, dict],
    flights: list[FlightParticles],
    flight_summaries: dict[str, dict],
    conditioned: dict[tuple[str, str], dict],
) -> None:
    columns = [
        "estimate_kind",
        "current_family",
        "flight_family",
        "particles",
        "point_latitude_s",
        "point_longitude_e",
        "latitude_50_min_s",
        "latitude_50_max_s",
        "latitude_90_min_s",
        "latitude_90_max_s",
        "latitude_95_min_s",
        "latitude_95_max_s",
        "latitude_99_min_s",
        "latitude_99_max_s",
        "before_effective_sample_size",
        "after_effective_sample_size",
        "terminated_fraction",
        "maximum_arrival_effective_sample_size",
        "mass_source_arrival_ess_at_least_100",
        "mass_source_arrival_ess_at_least_200",
        "probability_floor_mass",
        "scientific_status",
    ]

    def interval_values(summary: dict) -> dict:
        intervals = summary.get("latitude_equal_tail", summary.get("equal_tail"))
        result = {}
        for level in ("50", "90", "95", "99"):
            result[f"latitude_{level}_min_s"] = intervals[level]["lower"]
            result[f"latitude_{level}_max_s"] = intervals[level]["upper"]
        return result

    rows = []
    for key in ("native", "cmems", "gdp"):
        summary = source_summaries[key]
        rows.append(
            {
                "estimate_kind": "source_area",
                "current_family": summary["family"],
                "flight_family": "",
                "particles": summary["particles_per_cell"],
                "point_latitude_s": summary["peak_latitude_s"],
                "point_longitude_e": summary["peak_longitude_e"],
                **interval_values(summary),
                "terminated_fraction": summary["mean_importance_weighted_terminated_fraction"],
                "maximum_arrival_effective_sample_size": summary["maximum_arrival_effective_sample_size"],
                "mass_source_arrival_ess_at_least_100": summary["source_mass_arrival_ess_at_least_100"],
                "mass_source_arrival_ess_at_least_200": summary["source_mass_arrival_ess_at_least_200"],
                "probability_floor_mass": summary["probability_floor_source_mass"],
                "scientific_status": "diagnostic_only",
            }
        )
    for flight in flights:
        base = flight_summaries[flight.specification.name]
        rows.append(
            {
                "estimate_kind": "flight_only_impact",
                "current_family": "",
                "flight_family": flight.specification.name,
                "particles": base["particles"],
                "point_latitude_s": base["mean_latitude_s"],
                "point_longitude_e": base["mean_longitude_e"],
                **interval_values(base),
                "before_effective_sample_size": base["effective_sample_size"],
                "after_effective_sample_size": base["effective_sample_size"],
                "scientific_status": "converged_model_conditional",
            }
        )
        for source_key in ("native", "cmems"):
            summary = conditioned[(flight.specification.name, source_key)]
            rows.append(
                {
                    "estimate_kind": "flight_times_source_likelihood",
                    "current_family": summary["current_family"],
                    "flight_family": flight.specification.name,
                    "particles": summary["particles"],
                    "point_latitude_s": summary["mean_latitude_s"],
                    "point_longitude_e": summary["mean_longitude_e"],
                    **interval_values(summary),
                    "before_effective_sample_size": summary["before_effective_sample_size"],
                    "after_effective_sample_size": summary["after_effective_sample_size"],
                    "mass_source_arrival_ess_at_least_100": summary["conditioned_mass_on_source_arrival_ess_at_least_100"],
                    "mass_source_arrival_ess_at_least_200": summary["conditioned_mass_on_source_arrival_ess_at_least_200"],
                    "probability_floor_mass": summary["conditioned_mass_on_probability_floor_cells"],
                    "scientific_status": summary["scientific_status"],
                }
            )
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=columns, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {
                    key: (f"{value:.12g}" if isinstance(value, float) else value)
                    for key, value in row.items()
                }
            )


def run_self_test() -> None:
    weights = normalized(np.array([1.0, 3.0]))
    if abs(effective_sample_size(weights) - 1.6) > 1e-12:
        raise AssertionError("ESS limiting fixture failed")
    if weighted_quantile(np.array([10.0, 20.0]), weights, 0.5) != 20.0:
        raise AssertionError("weighted quantile fixture failed")
    distance = haversine_distance_matrix_nm(
        np.array([-30.0]), np.array([95.0]), np.array([-30.0]), np.array([95.0])
    )[0, 0]
    if distance != 0.0:
        raise AssertionError("haversine zero-distance fixture failed")
    one_degree = haversine_distance_matrix_nm(
        np.array([0.0]), np.array([0.0]), np.array([0.0]), np.array([1.0])
    )[0, 0]
    if abs(one_degree - math.pi * EARTH_RADIUS_NM / 180.0) > 1e-10:
        raise AssertionError("haversine one-degree fixture failed")


def default_flight_inputs(root: Path) -> list[FlightInput]:
    medium = root / "runs/mh370/through-0011-antenna-autopilot-modes-medium"
    refined = root / "runs/mh370/through-0011-antenna-autopilot-evidence-refinement"

    def paths(base: Path, family: str) -> tuple[Path, ...]:
        return tuple(
            base / family / f"seed-{seed}" / "posterior.csv"
            for seed in (370023, 370024, 370025)
        )

    return [
        FlightInput(
            "constant-true-track",
            "Constant true track",
            "o",
            medium / "suite-summary.json",
            paths(medium, "constant-true-track"),
        ),
        FlightInput(
            "constant-true-heading",
            "Constant true heading",
            "s",
            refined / "suite-summary.json",
            paths(refined, "constant-true-heading"),
        ),
        FlightInput(
            "constant-magnetic-track",
            "Constant magnetic track",
            "D",
            refined / "suite-summary.json",
            paths(refined, "constant-magnetic-track"),
        ),
        FlightInput(
            "constant-magnetic-heading",
            "Constant magnetic heading",
            "^",
            medium / "suite-summary.json",
            paths(medium, "constant-magnetic-heading"),
        ),
    ]


def main() -> None:
    started = time.perf_counter()
    root = Path(__file__).resolve().parents[3]
    preparation = root / ".sources/ocean-drift-input-preparation"
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--native-source",
        type=Path,
        default=preparation
        / "outputs/native-hycom-current-only-stability/runs/doubled/source-area.json",
    )
    parser.add_argument(
        "--cmems-source",
        type=Path,
        default=preparation
        / "outputs/cmems-glorys12-arrival-stability/runs/doubled/source-area.json",
    )
    parser.add_argument(
        "--gdp-source",
        type=Path,
        default=preparation
        / "outputs/gdp-adaptive-stability/runs/double-particles-2048/source-area.json",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=preparation / "outputs/family-conditioned-source-crash",
    )
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    run_self_test()
    if args.self_test:
        print("family-conditioned source/crash fixtures passed")
        return

    configure_style()
    sources = [
        load_source("native", "Native HYCOM current-only", NATIVE_BLUE, args.native_source),
        load_source("cmems", "CMEMS GLORYS12 current-only", CMEMS_ORANGE, args.cmems_source),
        load_source("gdp", "GDP + Stokes sensitivity", GDP_PURPLE, args.gdp_source),
    ]
    validate_matched_sources(sources[0], sources[1])
    source_summaries = {source.key: summarize_source(source) for source in sources}
    matched = compare_sources(sources[0], sources[1])
    flights = [load_flight(specification) for specification in default_flight_inputs(root)]
    flight_summaries = {
        flight.specification.name: summarize_distribution(
            flight.latitude_deg, flight.longitude_deg, flight.weight
        )
        for flight in flights
    }
    conditioned_weights = {}
    conditioned = {}
    for flight in flights:
        for source in sources[:2]:
            weights, _, _, summary = apply_source(flight, source)
            key = (flight.specification.name, source.key)
            conditioned_weights[key] = weights
            conditioned[key] = summary

    args.output.mkdir(parents=True, exist_ok=True)
    stem = args.output / "family-conditioned-source-crash"
    csv_path = stem.with_suffix(".csv")
    png_path = stem.with_suffix(".png")
    svg_path = stem.with_suffix(".svg")
    pdf_path = stem.with_suffix(".pdf")
    receipt_path = stem.with_suffix(".json")
    runtime_path = args.output / "runtime-receipt.json"
    write_csv(csv_path, source_summaries, flights, flight_summaries, conditioned)
    summary_page, layout_audit = render_summary_page(
        sources, source_summaries, flights, flight_summaries, conditioned
    )
    density_page = render_density_page(
        flights, sources, conditioned_weights, conditioned
    )
    status_page = render_status_page(source_summaries, flights, conditioned, matched)
    deterministic_date = dt.datetime(2014, 3, 8, tzinfo=dt.timezone.utc)
    summary_page.savefig(
        png_path,
        dpi=300,
        facecolor="white",
        metadata={"Software": "MH370 family-conditioned source/crash report"},
    )
    summary_page.savefig(
        svg_path,
        facecolor="white",
        metadata={
            "Creator": "MH370 family-conditioned source/crash report",
            "Date": "2014-03-08T00:00:00Z",
        },
    )
    pdf_metadata = {
        "Title": "MH370 family-conditioned source and crash-location diagnostics",
        "Author": "MH370 canonical ocean-drift investigation",
        "Creator": "MH370 family-conditioned source/crash report",
        "CreationDate": deterministic_date,
        "ModDate": deterministic_date,
    }
    with PdfPages(pdf_path, metadata=pdf_metadata) as pdf:
        for figure in (summary_page, density_page, status_page):
            pdf.savefig(figure, facecolor="white")
    plt.close(summary_page)
    plt.close(density_page)
    plt.close(status_page)

    input_records = {
        "sources": {
            source.key: {
                "path": str(source.path),
                "sha256": sha256(source.path),
                "family": source.document["family"],
                "seed": source.document["seed"],
                "particles_per_cell": source.document["particles_per_cell"],
            }
            for source in sources
        },
        "flight_families": {
            flight.specification.name: {
                "suite": flight.suite_record,
                "posteriors": flight.input_records,
            }
            for flight in flights
        },
    }
    receipt = {
        "schema": "mh370-family-conditioned-source-crash-v1",
        "purpose": "diagnostic family-conditioned source and inferred crash-location comparison",
        "inputs": input_records,
        "method": {
            "source_release_assumption": "seventh-arc release at impact at 2014-03-08 00:19 UTC",
            "source_prior_removed_before_flight_composition": True,
            "maximum_nearest_cell_distance_nm": MAXIMUM_CELL_DISTANCE_NM,
            "distance_basis": "legacy 3440.065-nautical-mile sphere, matching canonical runner",
            "current_families_pooled": False,
            "flight_control_families_pooled": False,
            "model_weights": None,
            "gdp_application": "not applied because sparse-field termination and replication instability are material",
        },
        "matched_native_vs_cmems": matched,
        "source_summaries": source_summaries,
        "flight_only_summaries": flight_summaries,
        "conditioned_crash_summaries": {
            f"{flight_name}__{source_key}": summary
            for (flight_name, source_key), summary in conditioned.items()
        },
        "layout_audit": layout_audit,
        "scientific_decision": {
            "status": "diagnostic_only_not_accepted_as_narrow_crash_posterior",
            "reason": (
                "flight-supported locations intersect the weak southern tails of both drift families; "
                "several intersections have low source arrival ESS or probability-floor dependence, "
                "and one CMEMS post-hoc application has severe importance collapse"
            ),
            "source_is_candidate_crash_site_conditionally": True,
            "condition": "flaperon release coincides with impact on the represented seventh arc",
        },
        "software": {
            "python": ".".join(map(str, sys.version_info[:3])),
            "numpy": np.__version__,
            "matplotlib": matplotlib.__version__,
        },
        "outputs": {
            path.name: {"sha256": sha256(path), "bytes": path.stat().st_size}
            for path in (csv_path, png_path, svg_path, pdf_path)
        },
    }
    receipt_path.write_text(
        json.dumps(receipt, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    elapsed = time.perf_counter() - started
    runtime = {
        "command": "python .sources/ocean-drift-input-preparation/code/report_family_conditioned_crash.py",
        "elapsed_seconds": elapsed,
        "maximum_resident_set_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        "outputs": [str(path) for path in (csv_path, png_path, svg_path, pdf_path, receipt_path)],
    }
    runtime_path.write_text(
        json.dumps(runtime, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
