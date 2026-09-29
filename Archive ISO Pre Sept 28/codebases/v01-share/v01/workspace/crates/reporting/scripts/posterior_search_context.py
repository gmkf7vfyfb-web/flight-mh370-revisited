#!/usr/bin/env python3
"""Render the canonical posterior evolution against searched-area context.

This is a reporting-only compositor. It never changes particle weights, pools
structural model families, or treats mapped search context as negative evidence.
The three posterior states are sequential/dependent and are normalized only for
their own display contours.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import html
import json
import math
import os
from pathlib import Path
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch, Polygon, Rectangle
from matplotlib.ticker import FuncFormatter
import numpy as np
from scipy.ndimage import gaussian_filter, gaussian_filter1d


SCHEMA_ID = "mh370-posterior-search-context"
SCHEMA_VERSION = 1
HPD_PROBABILITIES = (0.50, 0.95, 0.99)
DISPLAY_BANDWIDTH_NM = 7.5
DISPLAY_BANDWIDTH_KM = DISPLAY_BANDWIDTH_NM * 1.852
GRID_CELL_KM = 4.0
EARTH_KM_PER_DEGREE = 111.195
REFERENCE_LATITUDE_DEG = -36.5
REFERENCE_LONGITUDE_DEG = 90.0
MAIN_BOUNDS = (84.0, 97.0, -41.0, -32.5)
OVERVIEW_BOUNDS = (82.0, 106.5, -42.0, -19.0)
PRIMARY_IMPACT_FAMILY = "arc1-current-polar-best-glide-equal-feed"
FAMILY_STYLES = {
    "0011": {"label": "00:11 · BTO + medium BFO", "color": "#6553a3", "marker": "o"},
    "0019": {"label": "00:19:29 · corrected R600 BTO", "color": "#087f8c", "marker": "s"},
    "impact": {"label": "Impact · primary conditional EOF", "color": "#d45a24", "marker": "^"},
}
LEVEL_STYLES = {
    0.50: {"label": "50% HPD", "linestyle": "-", "linewidth": 2.1, "alpha": 1.0},
    0.95: {"label": "95% HPD", "linestyle": (0, (6, 3)), "linewidth": 1.45, "alpha": 0.9},
    0.99: {"label": "99% HPD", "linestyle": (0, (1.5, 2.2)), "linewidth": 1.05, "alpha": 0.78},
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def logical_path(path: Path, repository: Path) -> str:
    return Path(os.path.relpath(path.resolve(), repository.resolve())).as_posix()


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def normalized_log_weights(log_weights: np.ndarray) -> np.ndarray:
    if log_weights.size < 2 or not np.all(np.isfinite(log_weights)):
        raise ValueError("posterior needs at least two finite log weights")
    maximum = float(np.max(log_weights))
    weights = np.exp(log_weights - maximum)
    weights /= float(np.sum(weights))
    return weights


def validate_weights(weights: np.ndarray, label: str) -> None:
    if weights.size < 2 or not np.all(np.isfinite(weights)) or np.any(weights < 0.0):
        raise ValueError(f"{label} contains invalid weights")
    if abs(float(np.sum(weights)) - 1.0) > 1.0e-10:
        raise ValueError(f"{label} weights are not normalized")


def weighted_quantile(values: np.ndarray, weights: np.ndarray, probability: float) -> float:
    order = np.argsort(values, kind="stable")
    cumulative = np.cumsum(weights[order])
    index = min(int(np.searchsorted(cumulative, probability, side="left")), len(order) - 1)
    return float(values[order[index]])


def posterior_summary(longitude: np.ndarray, latitude: np.ndarray, weights: np.ndarray) -> dict:
    validate_weights(weights, "posterior")
    return {
        "particles": int(weights.size),
        "effective_sample_size": float(1.0 / np.sum(weights**2)),
        "weighted_mean": {
            "latitude_deg": float(np.sum(latitude * weights)),
            "longitude_deg": float(np.sum(longitude * weights)),
        },
        "latitude_central_95_deg": [
            weighted_quantile(latitude, weights, 0.025),
            weighted_quantile(latitude, weights, 0.975),
        ],
        "positive_weight_support": {
            "longitude_deg": [float(np.min(longitude)), float(np.max(longitude))],
            "latitude_deg": [float(np.min(latitude)), float(np.max(latitude))],
        },
    }


def read_core_0011(root: Path, input_hashes: dict[str, str], repository: Path) -> dict:
    paths = sorted((root / "bto-bfo-medium").glob("seed-*/posterior.csv"))
    if len(paths) != 5:
        raise ValueError("00:11 release requires exactly five medium-BFO seed CSVs")
    longitudes: list[np.ndarray] = []
    latitudes: list[np.ndarray] = []
    weights: list[np.ndarray] = []
    seeds = []
    for path in paths:
        seed = int(path.parent.name.removeprefix("seed-"))
        seeds.append(seed)
        longitude = []
        latitude = []
        weight = []
        with path.open(newline="", encoding="utf-8") as handle:
            for row in csv.DictReader(handle):
                if row["model_family"] != "bto-bfo-medium":
                    raise ValueError(f"unexpected 00:11 model family in {path}")
                longitude.append(float(row["last_contact_longitude_deg"]))
                latitude.append(float(row["last_contact_latitude_deg"]))
                weight.append(float(row["weight"]))
        seed_weights = np.asarray(weight, dtype=float)
        validate_weights(seed_weights, f"00:11 seed {seed}")
        longitudes.append(np.asarray(longitude, dtype=float))
        latitudes.append(np.asarray(latitude, dtype=float))
        weights.append(seed_weights / len(paths))
        input_hashes[logical_path(path, repository)] = sha256(path)
    manifest = root / "run-manifest.json"
    input_hashes[logical_path(manifest, repository)] = sha256(manifest)
    result = {
        "longitude": np.concatenate(longitudes),
        "latitude": np.concatenate(latitudes),
        "weights": np.concatenate(weights),
        "seeds": seeds,
        "evidence": "BTO and medium-BFO through 00:11 UTC",
        "model_scope": "five equally pooled numerical seeds; constant-true-track one-turn family",
    }
    validate_weights(result["weights"], "pooled 00:11")
    return result


def read_continuation_0019(root: Path, input_hashes: dict[str, str], repository: Path) -> dict:
    path = root / "posterior.csv"
    longitude = []
    latitude = []
    weight = []
    seed_mass: dict[int, float] = {}
    with path.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            if row["model_family"] != "bto-bfo-medium":
                raise ValueError("unexpected 00:19 model family")
            row_weight = float(row["weight"])
            seed = int(row["seed"])
            longitude.append(float(row["end_longitude_deg"]))
            latitude.append(float(row["end_latitude_deg"]))
            weight.append(row_weight)
            seed_mass[seed] = seed_mass.get(seed, 0.0) + row_weight
    weights = np.asarray(weight, dtype=float)
    validate_weights(weights, "00:19")
    if len(seed_mass) != 5 or any(abs(value - 0.2) > 1.0e-10 for value in seed_mass.values()):
        raise ValueError("00:19 continuation does not pool five seeds equally")
    manifest = root / "run-manifest.json"
    input_hashes[logical_path(path, repository)] = sha256(path)
    input_hashes[logical_path(manifest, repository)] = sha256(manifest)
    return {
        "longitude": np.asarray(longitude, dtype=float),
        "latitude": np.asarray(latitude, dtype=float),
        "weights": weights,
        "seeds": sorted(seed_mass),
        "evidence": "corrected 00:19:29 R600 BTO only",
        "model_scope": "510-second frozen-state continuation; five seed masses fixed at 0.2",
    }


def read_primary_impact(suite_path: Path, input_hashes: dict[str, str], repository: Path) -> dict:
    suite = load_json(suite_path)
    if suite.get("schema_id") != "mh370-impact-conditional-suite" or suite.get("family_combination") != "separate":
        raise ValueError("unexpected impact-suite contract")
    matches = [entry for entry in suite["families"] if entry["id"] == PRIMARY_IMPACT_FAMILY]
    if len(matches) != 1:
        raise ValueError("primary conditional impact family is missing or duplicated")
    entry = matches[0]
    if entry.get("source_seed_combination") != "equal_numerical_replicates" or len(entry["runs"]) != 5:
        raise ValueError("impact family must contain five equal numerical seed replicates")
    suite_root = suite_path.parent
    longitudes = []
    latitudes = []
    weights = []
    seeds = []
    for run in entry["runs"]:
        seed = int(run["source_seed"])
        path = suite_root / run["impact_handoff"]
        if sha256(path) != run["impact_handoff_sha256"]:
            raise ValueError(f"impact handoff hash mismatch for seed {seed}")
        handoff = load_json(path)
        if handoff.get("schema_id") != "mh370-impact-posterior-handoff" or handoff.get("scenario_combination") != {"kind": "separate"}:
            raise ValueError(f"unexpected impact handoff contract for seed {seed}")
        particles = handoff["particles"]
        seed_weights = normalized_log_weights(
            np.asarray([particle["normalized_log_weight"] for particle in particles], dtype=float)
        )
        longitudes.append(np.asarray([
            particle["kinematics"]["position_wgs84"]["longitude"] for particle in particles
        ], dtype=float))
        latitudes.append(np.asarray([
            particle["kinematics"]["position_wgs84"]["latitude"] for particle in particles
        ], dtype=float))
        weights.append(seed_weights / len(entry["runs"]))
        seeds.append(seed)
        input_hashes[logical_path(path, repository)] = sha256(path)
    input_hashes[logical_path(suite_path, repository)] = sha256(suite_path)
    result = {
        "longitude": np.concatenate(longitudes),
        "latitude": np.concatenate(latitudes),
        "weights": np.concatenate(weights),
        "seeds": seeds,
        "evidence": "00:11 medium-BFO source plus corrected R600 BTO",
        "model_scope": "primary v0.1 EOF proxy: dynamic ERA5, Martin Arc-1 fuel, current attached-flow polar, best glide, equal feed",
    }
    validate_weights(result["weights"], "pooled impact")
    return result


def metric_coordinates(longitude: np.ndarray, latitude: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    scale = EARTH_KM_PER_DEGREE * math.cos(math.radians(REFERENCE_LATITUDE_DEG))
    return (
        (longitude - REFERENCE_LONGITUDE_DEG) * scale,
        (latitude - REFERENCE_LATITUDE_DEG) * EARTH_KM_PER_DEGREE,
    )


def display_surface(posterior: dict, bounds: tuple[float, float, float, float], bandwidth_km: float) -> dict:
    xmin, xmax, ymin, ymax = bounds
    longitude = posterior["longitude"]
    latitude = posterior["latitude"]
    weights = posterior["weights"]
    inside = (longitude >= xmin) & (longitude <= xmax) & (latitude >= ymin) & (latitude <= ymax)
    outside_mass = float(np.sum(weights[~inside]))
    if outside_mass > 1.0e-12:
        raise ValueError(f"posterior plot bounds exclude positive mass {outside_mass:.3e}")
    x_km, y_km = metric_coordinates(longitude, latitude)
    x_bound, y_bound = metric_coordinates(
        np.asarray([xmin, xmax], dtype=float), np.asarray([ymin, ymax], dtype=float)
    )
    x_edges = np.arange(x_bound[0], x_bound[1] + GRID_CELL_KM, GRID_CELL_KM)
    y_edges = np.arange(y_bound[0], y_bound[1] + GRID_CELL_KM, GRID_CELL_KM)
    raw_mass, _, _ = np.histogram2d(y_km, x_km, bins=(y_edges, x_edges), weights=weights)
    smooth_mass = gaussian_filter(
        raw_mass,
        sigma=bandwidth_km / GRID_CELL_KM,
        mode="constant",
        truncate=4.0,
    )
    smooth_mass /= float(np.sum(smooth_mass))
    x_centers = (x_edges[:-1] + x_edges[1:]) / 2.0
    y_centers = (y_edges[:-1] + y_edges[1:]) / 2.0
    longitude_centers = REFERENCE_LONGITUDE_DEG + x_centers / (
        EARTH_KM_PER_DEGREE * math.cos(math.radians(REFERENCE_LATITUDE_DEG))
    )
    latitude_centers = REFERENCE_LATITUDE_DEG + y_centers / EARTH_KM_PER_DEGREE
    thresholds = {}
    achieved = {}
    areas = {}
    order = np.argsort(smooth_mass.ravel(), kind="stable")[::-1]
    cumulative = np.cumsum(smooth_mass.ravel()[order])
    for probability in HPD_PROBABILITIES:
        index = min(int(np.searchsorted(cumulative, probability, side="left")), len(order) - 1)
        threshold = float(smooth_mass.ravel()[order[index]])
        mask = smooth_mass >= threshold
        thresholds[str(probability)] = threshold
        achieved[str(probability)] = float(np.sum(smooth_mass[mask]))
        areas[str(probability)] = float(np.sum(mask) * GRID_CELL_KM**2)
    edge_mass = float(
        np.sum(smooth_mass[0, :])
        + np.sum(smooth_mass[-1, :])
        + np.sum(smooth_mass[1:-1, 0])
        + np.sum(smooth_mass[1:-1, -1])
    )
    if edge_mass > 1.0e-5:
        raise ValueError(f"display surface approaches plot edge ({edge_mass:.3e} mass)")
    return {
        "longitude": longitude_centers,
        "latitude": latitude_centers,
        "mass": smooth_mass,
        "thresholds": thresholds,
        "achieved_mass": achieved,
        "areas_km2": areas,
        "outside_input_mass": outside_mass,
        "edge_display_mass": edge_mass,
        "bandwidth_km": bandwidth_km,
    }


def read_davey(path: Path) -> dict:
    latitude = []
    density = []
    with path.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            latitude.append(float(row["latitude_deg"]))
            density.append(float(row["density_per_deg"]))
    latitude_array = np.asarray(latitude, dtype=float)
    density_array = np.asarray(density, dtype=float)
    if np.any(np.diff(latitude_array) <= 0.0) or np.any(density_array < 0.0):
        raise ValueError("invalid Davey latitude marginal")
    integral = float(np.trapezoid(density_array, latitude_array))
    if abs(integral - 1.0) > 1.0e-8:
        raise ValueError("Davey latitude marginal is not normalized")
    segment_mass = (density_array[:-1] + density_array[1:]) * np.diff(latitude_array) / 2.0
    cumulative = np.concatenate(([0.0], np.cumsum(segment_mass)))
    cumulative /= cumulative[-1]
    quantiles = {
        str(probability): float(np.interp(probability, cumulative, latitude_array))
        for probability in (0.025, 0.5, 0.975)
    }
    return {
        "latitude": latitude_array,
        "density": density_array,
        "quantiles": quantiles,
        "integral": integral,
        "source": "Davey et al. (2016), Figure 10.3 bottom panel, digitized",
    }


def latitude_marginal(posterior: dict, bounds: tuple[float, float]) -> tuple[np.ndarray, np.ndarray]:
    ymin, ymax = bounds
    step = 0.025
    edges = np.arange(ymin, ymax + step, step)
    mass, _ = np.histogram(posterior["latitude"], bins=edges, weights=posterior["weights"])
    mass = gaussian_filter1d(mass.astype(float), sigma=0.10 / step, mode="constant", truncate=4.0)
    centers = (edges[:-1] + edges[1:]) / 2.0
    density = mass / (float(np.sum(mass)) * step)
    return centers, density


def geometry_polygons(geometry: dict) -> list[list[list[float]]]:
    if geometry["type"] == "Polygon":
        return [geometry["coordinates"]]
    if geometry["type"] == "MultiPolygon":
        return geometry["coordinates"]
    return []


def add_polygon_geometry(ax, geometry: dict, **style) -> None:
    for polygon in geometry_polygons(geometry):
        exterior = np.asarray(polygon[0], dtype=float)
        ax.add_patch(Polygon(exterior, closed=True, **style))


SEARCH_STYLES = {
    "phase2_deep": {"facecolor": "#6dc9b5", "edgecolor": "#168979", "alpha": 0.15, "linewidth": 0.65},
    "phase2_coarse": {"facecolor": "none", "edgecolor": "#168979", "alpha": 0.65, "linewidth": 0.7, "hatch": "///"},
    "phase2_extent": {"facecolor": "none", "edgecolor": "#356f68", "alpha": 0.72, "linewidth": 0.75, "linestyle": "--"},
    "bluefin": {"facecolor": "#a977df", "edgecolor": "#7244b2", "alpha": 0.24, "linewidth": 0.8},
    "oi2018_proxy": {"facecolor": "#94a0ae", "edgecolor": "#5f6f82", "alpha": 0.09, "linewidth": 0.9, "linestyle": "--", "hatch": ".."},
    "oi2024_outboard_proxy": {"facecolor": "#7bb1ff", "edgecolor": "#397bc5", "alpha": 0.13, "linewidth": 0.95, "linestyle": "--"},
    "oi2024_inboard_proxy": {"facecolor": "#ffc766", "edgecolor": "#c38216", "alpha": 0.18, "linewidth": 0.95, "linestyle": "--"},
    "wide_area_context": {"facecolor": "none", "edgecolor": "#91a9c6", "alpha": 0.7, "linewidth": 0.75, "linestyle": "--"},
}


def draw_search_atlas(ax, atlas: dict) -> None:
    for feature in atlas["features"]:
        layer = feature["properties"]["atlas_layer"]
        geometry = feature["geometry"]
        if layer == "seventh_arc":
            points = np.asarray(geometry["coordinates"], dtype=float)
            ax.plot(points[:, 0], points[:, 1], color="#172334", linewidth=1.25, zorder=3)
        elif layer == "ais_proxy":
            points = np.asarray(geometry["coordinates"], dtype=float)
            ax.plot(points[:, 0], points[:, 1], color="#d95f5f", linewidth=0.65, linestyle=(0, (1, 2)), alpha=0.72, zorder=2.7)
        elif layer in SEARCH_STYLES:
            add_polygon_geometry(ax, geometry, zorder=1.0 if layer != "wide_area_context" else 0.7, **SEARCH_STYLES[layer])


def load_land(path: Path) -> list[np.ndarray]:
    source = load_json(path)
    polygons = []
    for feature in source["features"]:
        for polygon in geometry_polygons(feature["geometry"]):
            polygons.append(np.asarray(polygon[0], dtype=float))
    return polygons


def add_land(ax, polygons: list[np.ndarray], bounds: tuple[float, float, float, float]) -> None:
    xmin, xmax, ymin, ymax = bounds
    for points in polygons:
        if points[:, 0].max() < xmin or points[:, 0].min() > xmax or points[:, 1].max() < ymin or points[:, 1].min() > ymax:
            continue
        ax.add_patch(Polygon(points, closed=True, facecolor="#f0eee8", edgecolor="#88837a", linewidth=0.45, zorder=0.1))


def add_scale_bar(ax, bounds: tuple[float, float, float, float], length_nm: float) -> None:
    xmin, xmax, ymin, ymax = bounds
    latitude = ymin + 0.065 * (ymax - ymin)
    length_lon = length_nm / (60.0 * math.cos(math.radians(latitude)))
    start = xmin + 0.055 * (xmax - xmin)
    ax.plot([start, start + length_lon], [latitude, latitude], color="#242424", linewidth=1.8, zorder=20)
    ax.plot([start, start], [latitude - 0.035, latitude + 0.035], color="#242424", linewidth=1.1, zorder=20)
    ax.plot([start + length_lon, start + length_lon], [latitude - 0.035, latitude + 0.035], color="#242424", linewidth=1.1, zorder=20)
    ax.text(start + length_lon / 2.0, latitude + 0.06, f"{length_nm:g} NM", ha="center", va="bottom", fontsize=7, zorder=20)


def format_map_axis(ax, bounds: tuple[float, float, float, float]) -> None:
    ax.set_xlim(bounds[0], bounds[1])
    ax.set_ylim(bounds[2], bounds[3])
    ax.set_aspect(1.0 / math.cos(math.radians((bounds[2] + bounds[3]) / 2.0)))
    ax.xaxis.set_major_formatter(FuncFormatter(lambda value, _: f"{value:g}°E"))
    ax.yaxis.set_major_formatter(FuncFormatter(lambda value, _: f"{abs(value):g}°S"))
    ax.grid(color="#cfd5db", linewidth=0.4, alpha=0.7, zorder=0)
    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")


def contour_surface(ax, surface: dict, style: dict, fill: bool = True, overview: bool = False) -> None:
    longitude, latitude = np.meshgrid(surface["longitude"], surface["latitude"])
    mass = surface["mass"]
    if fill and not overview:
        threshold = surface["thresholds"]["0.5"]
        ax.contourf(
            longitude,
            latitude,
            mass,
            levels=[threshold, float(np.max(mass)) * 1.000001],
            colors=[style["color"]],
            alpha=0.075,
            zorder=4,
        )
    probabilities = (0.99,) if overview else (0.99, 0.95, 0.50)
    for probability in probabilities:
        level = LEVEL_STYLES[probability]
        ax.contour(
            longitude,
            latitude,
            mass,
            levels=[surface["thresholds"][str(probability)]],
            colors=[style["color"]],
            linestyles=[level["linestyle"]],
            linewidths=[0.8 if overview else level["linewidth"]],
            alpha=0.55 if overview else level["alpha"],
            zorder=6,
        )


def search_legend_handles() -> list:
    return [
        Patch(facecolor="#6dc9b5", edgecolor="#168979", alpha=0.3, label="Phase 2 official display geometry"),
        Line2D([0], [0], color="#5f6f82", linestyle="--", label="OI 2018 approximate outline (C)"),
        Line2D([0], [0], color="#397bc5", linestyle="--", label="Renewed outboard estimate (C)"),
        Line2D([0], [0], color="#c38216", linestyle="--", label="Renewed inboard estimate (C)"),
        Line2D([0], [0], color="#d95f5f", linestyle=(0, (1, 2)), label="AIS surface-vessel proxy (C)"),
        Line2D([0], [0], color="#172334", linewidth=1.25, label="Official seventh arc"),
        Patch(facecolor="#a977df", edgecolor="#7244b2", alpha=0.32, label="Bluefin official display polygons"),
    ]


def render_figure(
    posteriors: dict[str, dict],
    surfaces: dict[str, dict],
    davey: dict,
    atlas: dict,
    inventory: dict,
    land: list[np.ndarray],
    output_stem: Path,
) -> list[Path]:
    fig = plt.figure(figsize=(15.4, 10.2))
    grid = fig.add_gridspec(
        2,
        3,
        width_ratios=(1.55, 1.05, 0.78),
        height_ratios=(1.08, 0.92),
        left=0.055,
        right=0.985,
        top=0.91,
        bottom=0.085,
        wspace=0.15,
        hspace=0.22,
    )
    main = fig.add_subplot(grid[0, :2])
    marginal = fig.add_subplot(grid[0, 2], sharey=main)
    overview = fig.add_subplot(grid[1, :2])
    note = fig.add_subplot(grid[1, 2])

    add_land(main, land, MAIN_BOUNDS)
    draw_search_atlas(main, atlas)
    family_handles = []
    for key in ("0011", "0019", "impact"):
        style = FAMILY_STYLES[key]
        contour_surface(main, surfaces[key], style)
        summary = posteriors[key]["summary"]
        mean = summary["weighted_mean"]
        main.scatter(
            mean["longitude_deg"],
            mean["latitude_deg"],
            marker=style["marker"],
            s=34,
            facecolor="white",
            edgecolor=style["color"],
            linewidth=1.3,
            zorder=9,
        )
        family_handles.append(
            Line2D(
                [0], [0], color=style["color"], linewidth=1.8, marker=style["marker"],
                markerfacecolor="white", markeredgecolor=style["color"], label=style["label"],
            )
        )
    format_map_axis(main, MAIN_BOUNDS)
    main.set_title("A  Posterior evolution and southern search context", loc="left", fontsize=11.2, weight="bold")
    add_scale_bar(main, MAIN_BOUNDS, 100.0)
    first_legend = main.legend(handles=family_handles, loc="lower right", fontsize=7.3, frameon=True, facecolor="white", edgecolor="#c4c4c4")
    main.add_artist(first_legend)
    level_handles = [
        Line2D([0], [0], color="#303030", linestyle=LEVEL_STYLES[p]["linestyle"], linewidth=LEVEL_STYLES[p]["linewidth"], label=LEVEL_STYLES[p]["label"])
        for p in HPD_PROBABILITIES
    ]
    main.legend(handles=level_handles, loc="upper left", ncol=3, fontsize=7.2, frameon=True, facecolor="white", edgecolor="#c4c4c4")

    y_0019, density_0019 = latitude_marginal(posteriors["0019"], (MAIN_BOUNDS[2], MAIN_BOUNDS[3]))
    marginal.fill_betweenx(davey["latitude"], 0.0, davey["density"], color="#777777", alpha=0.16)
    marginal.plot(davey["density"], davey["latitude"], color="#303030", linewidth=1.45, linestyle=(0, (5, 3)), label="Davey Fig. 10.3")
    marginal.plot(density_0019, y_0019, color=FAMILY_STYLES["0019"]["color"], linewidth=1.5, label="Canonical 00:19")
    marginal.axhline(davey["quantiles"]["0.5"], color="#303030", linewidth=0.75, alpha=0.7)
    marginal.axhline(weighted_quantile(posteriors["0019"]["latitude"], posteriors["0019"]["weights"], 0.5), color=FAMILY_STYLES["0019"]["color"], linewidth=0.75, alpha=0.8)
    marginal.set_xlim(left=0.0)
    marginal.set_ylim(MAIN_BOUNDS[2], MAIN_BOUNDS[3])
    marginal.grid(color="#d7d7d7", linewidth=0.35, alpha=0.75)
    marginal.tick_params(axis="y", labelleft=False)
    marginal.set_xlabel("Latitude density (per degree)")
    marginal.set_title("B  Davey 00:19 latitude PDF", loc="left", fontsize=10.2, weight="bold")
    marginal.legend(loc="upper right", fontsize=7.1, frameon=True, facecolor="white", edgecolor="#c4c4c4")
    davey_q = davey["quantiles"]
    canonical_q = posteriors["0019"]["summary"]["latitude_central_95_deg"]
    marginal.text(
        0.03,
        0.03,
        "Davey: median {:.2f}°S; 95% {:.2f}–{:.2f}°S\n"
        "Canonical: 95% {:.2f}–{:.2f}°S\n\n"
        "Davey published no numerical 2D grid.\n"
        "Fig. 10.10 impact contours are raster-only;\n"
        "no geographic contour is inferred here.".format(
            abs(davey_q["0.5"]),
            abs(davey_q["0.975"]),
            abs(davey_q["0.025"]),
            abs(canonical_q[1]),
            abs(canonical_q[0]),
        ),
        transform=marginal.transAxes,
        ha="left",
        va="bottom",
        fontsize=7.0,
        linespacing=1.28,
        bbox={"boxstyle": "round,pad=0.3", "facecolor": "white", "edgecolor": "#c8c8c8", "alpha": 0.94},
    )

    add_land(overview, land, OVERVIEW_BOUNDS)
    draw_search_atlas(overview, atlas)
    for key in ("0011", "0019", "impact"):
        contour_surface(overview, surfaces[key], FAMILY_STYLES[key], fill=False, overview=True)
    overview.add_patch(
        Rectangle(
            (MAIN_BOUNDS[0], MAIN_BOUNDS[2]),
            MAIN_BOUNDS[1] - MAIN_BOUNDS[0],
            MAIN_BOUNDS[3] - MAIN_BOUNDS[2],
            facecolor="none",
            edgecolor="#1f2933",
            linewidth=0.9,
            linestyle=(0, (4, 3)),
            zorder=8,
        )
    )
    overview.text(MAIN_BOUNDS[0] + 0.2, MAIN_BOUNDS[3] - 0.45, "Panel A extent", fontsize=6.8, color="#1f2933", zorder=9)
    overview.text(103.1, -21.5, "Bluefin\ndisplay", color="#7244b2", fontsize=7.0, ha="center")
    overview.text(100.5, -26.0, "OI 2018 approximate\noutline", color="#5f6f82", fontsize=7.0, ha="center")
    overview.text(87.7, -38.65, "Official Phase 2", color="#168979", fontsize=7.0, ha="center")
    format_map_axis(overview, OVERVIEW_BOUNDS)
    overview.set_title("C  Full searched-area locator", loc="left", fontsize=11.2, weight="bold")
    add_scale_bar(overview, OVERVIEW_BOUNDS, 200.0)

    note.axis("off")
    note.text(0.0, 1.0, "D  Search-area evidence", ha="left", va="top", fontsize=11.2, weight="bold", color="#173a60")
    note.legend(handles=search_legend_handles(), loc="upper left", bbox_to_anchor=(-0.02, 0.92), fontsize=6.8, frameon=False, handlelength=2.4)
    rows = {row["id"]: row for row in inventory["rows"]}
    bluefin = rows["bluefin-artemis-2014"]
    oi2018 = rows["ocean-infinity-2018"]
    renewed = rows["ocean-infinity-2025-2026"]
    note.text(
        0.0,
        0.48,
        "Mapped / reported area context\n\n"
        "Phase 2 catalog: Deep Tow 130,961; DHJ 46,884;\n"
        "GO Phoenix 82,606 km² (overlap; not additive)\n"
        f"Bluefin {bluefin['plotted_or_catalog_area_km2']:.0f} km² display / "
        f"{bluefin['reported_area_km2']:.0f} km² reported\n"
        f"OI 2018 >{oi2018['reported_area_km2']['lower_bound']:,} km² reported;\n"
        "exact swaths unplotted\n"
        f"OI 2025–26 {renewed['reported_surveyed_area_km2']:,} km² surveyed;\n"
        f"{renewed['derived_rounded_remainder_km2']:,} km² arithmetic remainder only",
        ha="left",
        va="top",
        fontsize=6.7,
        linespacing=1.12,
    )
    note.text(
        0.0,
        0.025,
        "CONTEXT ONLY — no binary searched/not-searched mask.\n"
        "No calibrated target-specific probability of detection.\n"
        "Grade-C OI outlines and AIS tracks are educated context,\n"
        "not AUV sonar swaths.",
        ha="left",
        va="bottom",
        fontsize=6.65,
        weight="bold",
        color="#9f2424",
        linespacing=1.17,
        bbox={"facecolor": "white", "edgecolor": "none", "alpha": 0.97, "pad": 1.5},
    )

    fig.suptitle("MH370 posterior evolution and seabed-search context", fontsize=17.2, color="#173a60", y=0.975)
    fig.text(
        0.5,
        0.943,
        "00:11 medium-BFO posterior → corrected-R600 00:19 control → primary conditional v0.1 impact family",
        ha="center",
        fontsize=10.0,
        color="#343b43",
    )
    fig.text(
        0.5,
        0.025,
        "Posterior contours are separate 50/95/99% display HPDs on a 4 km local metric raster with a fixed 7.5 NM Gaussian kernel; numerical weights are unchanged. "
        "The states are sequential and dependent. Search geometry is contextual only; exact OI/Bluefin swaths, holidays, quality and calibrated PoD remain unresolved.",
        ha="center",
        va="bottom",
        fontsize=7.1,
        color="#505963",
        wrap=True,
    )

    metadata = {"Creator": "MH370 canonical report generator", "Date": None}
    png = output_stem.with_suffix(".png")
    svg = output_stem.with_suffix(".svg")
    pdf = output_stem.with_suffix(".pdf")
    fig.savefig(png, dpi=240, metadata={"Software": metadata["Creator"]})
    fig.savefig(svg, metadata=metadata)
    fig.savefig(pdf, metadata={"Creator": metadata["Creator"], "CreationDate": None, "ModDate": None})
    plt.close(fig)
    return [png, svg, pdf]


def write_caption(path: Path, summaries: dict, davey: dict) -> None:
    text = f"""# Figure caption

**MH370 posterior evolution and seabed-search context.** The geographic panel
shows independently normalized 50%, 95%, and 99% highest-posterior-density
display contours for the five-seed 00:11 BTO+medium-BFO posterior, its
fixed-state 510-second continuation selected by the corrected 00:19:29 R600
BTO, and the v0.1 primary conditional end-of-flight family. Weighted means are
{abs(summaries['0011']['weighted_mean']['latitude_deg']):.3f}°S,
{summaries['0011']['weighted_mean']['longitude_deg']:.3f}°E;
{abs(summaries['0019']['weighted_mean']['latitude_deg']):.3f}°S,
{summaries['0019']['weighted_mean']['longitude_deg']:.3f}°E; and
{abs(summaries['impact']['weighted_mean']['latitude_deg']):.3f}°S,
{summaries['impact']['weighted_mean']['longitude_deg']:.3f}°E, respectively.
Contours use a fixed {DISPLAY_BANDWIDTH_NM:g} NM Gaussian display kernel on a
{GRID_CELL_KM:g} km local metric raster; particle weights and numerical
summaries are unchanged.

The aligned side panel reproduces the digitized one-dimensional latitude
marginal published by Davey et al. (2016), Figure 10.3, for 00:19. Davey did
not publish a numerical two-dimensional density grid or a separate 00:11
position PDF. Their Figure 10.10 predicted impact surface is available only as
a raster with 90/95/99% contours, so no geographic Davey contour is inferred.

Official Phase-2 and Bluefin display geometry is distinguished from Grade-C
Ocean Infinity outline reconstructions and surface-vessel AIS proxies. These
layers are planning context, not binary exclusions or negative-search
likelihoods. Exact AUV swaths, spatial quality/holiday masks and calibrated
target-specific probability of detection remain unresolved. Catalog and
reported areas overlap and are not summed.
"""
    path.write_text(text, encoding="utf-8", newline="\n")


def write_index(path: Path, summary: dict) -> None:
    posterior_rows = []
    for key in ("0011", "0019", "impact"):
        item = summary["posteriors"][key]
        mean = item["weighted_mean"]
        posterior_rows.append(
            "<tr>"
            f"<td>{html.escape(FAMILY_STYLES[key]['label'])}</td>"
            f"<td>{item['particles']:,}</td>"
            f"<td>{item['effective_sample_size']:,.1f}</td>"
            f"<td>{abs(mean['latitude_deg']):.4f}°S, {mean['longitude_deg']:.4f}°E</td>"
            f"<td>{item['display_hpd_area_km2']['0.5']:,.0f} / {item['display_hpd_area_km2']['0.95']:,.0f} / {item['display_hpd_area_km2']['0.99']:,.0f}</td>"
            "</tr>"
        )
    document = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>MH370 posterior evolution and search context</title>
<style>
body{{margin:0;background:#f4f6f8;color:#1e2935;font:15px/1.5 system-ui,sans-serif}}main{{max-width:1180px;margin:auto;padding:28px}}
h1{{color:#173a60;margin-bottom:4px}}.lead{{color:#52606d;margin-top:0}}.card{{background:white;border:1px solid #d8dee5;border-radius:9px;padding:20px;margin:18px 0;box-shadow:0 2px 10px #25364d12}}
img{{display:block;width:100%;height:auto}}a{{color:#195f92}}table{{border-collapse:collapse;width:100%;font-size:13px}}th,td{{padding:8px;border-bottom:1px solid #e0e5ea;text-align:left}}th{{background:#eef3f7}}.warning{{border-left:4px solid #b43737;padding-left:12px;color:#792222}}
</style></head><body><main>
<h1>MH370 posterior evolution and seabed-search context</h1>
<p class="lead">Canonical v0.1 posterior states with Davey and searched-area context.</p>
<div class="card"><p><a href="posterior-evolution-search-context.svg">SVG</a> · <a href="posterior-evolution-search-context.pdf">vector PDF</a> · <a href="posterior-evolution-search-context.png">PNG</a></p><img src="posterior-evolution-search-context.png" alt="MH370 posterior and search context"></div>
<div class="card"><h2>Numerical display summary</h2><table><thead><tr><th>State</th><th>N</th><th>ESS</th><th>Weighted mean</th><th>50 / 95 / 99% HPD km²</th></tr></thead><tbody>{''.join(posterior_rows)}</tbody></table></div>
<div class="card warning"><strong>Scientific boundary.</strong> The impact surface is conditional on the v0.1 primary end-of-flight proxy. Davey is shown only as the published one-dimensional 00:19 latitude marginal; no 2D Davey grid is invented. Search layers are context, not negative evidence or calibrated probability-of-detection masks.</div>
<div class="card"><p><a href="caption.md">Full caption</a> · <a href="summary.json">machine summary</a> · <a href="run-manifest.json">provenance manifest</a> · <a href="artifact-sha256.json">artifact hashes</a></p></div>
</main></body></html>"""
    path.write_text(document, encoding="utf-8", newline="\n")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--core-run", type=Path, required=True)
    parser.add_argument("--continuation-run", type=Path, required=True)
    parser.add_argument("--impact-suite", type=Path, required=True)
    parser.add_argument("--davey-latitude", type=Path, required=True)
    parser.add_argument("--search-atlas", type=Path, required=True)
    parser.add_argument("--area-inventory", type=Path, required=True)
    parser.add_argument("--land", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    output = args.output.resolve()
    if output.exists():
        raise FileExistsError(f"refusing to overwrite {output}")
    output.mkdir(parents=True)
    repository = args.land.resolve().parents[3]
    input_hashes: dict[str, str] = {}
    posteriors = {
        "0011": read_core_0011(args.core_run.resolve(), input_hashes, repository),
        "0019": read_continuation_0019(args.continuation_run.resolve(), input_hashes, repository),
        "impact": read_primary_impact(args.impact_suite.resolve(), input_hashes, repository),
    }
    if posteriors["0011"]["seeds"] != posteriors["0019"]["seeds"] or posteriors["0011"]["seeds"] != posteriors["impact"]["seeds"]:
        raise ValueError("posterior layers do not share the five numerical seed identities")

    davey_path = args.davey_latitude.resolve()
    atlas_path = args.search_atlas.resolve()
    inventory_path = args.area_inventory.resolve()
    land_path = args.land.resolve()
    davey = read_davey(davey_path)
    atlas = load_json(atlas_path)
    inventory = load_json(inventory_path)
    land = load_land(land_path)
    if atlas.get("metadata", {}).get("analysis_eligible") is not False or atlas.get("metadata", {}).get("negative_search_eligible") is not False:
        raise ValueError("search atlas is not explicitly context-only")
    input_hashes[logical_path(davey_path, repository)] = sha256(davey_path)
    input_hashes[logical_path(atlas_path, repository)] = sha256(atlas_path)
    input_hashes[logical_path(inventory_path, repository)] = sha256(inventory_path)
    input_hashes[logical_path(land_path, repository)] = sha256(land_path)

    surfaces = {
        key: display_surface(posterior, MAIN_BOUNDS, DISPLAY_BANDWIDTH_KM)
        for key, posterior in posteriors.items()
    }
    bandwidth_sensitivity = {}
    for bandwidth_nm in (5.0, 10.0):
        bandwidth_sensitivity[str(bandwidth_nm)] = {
            key: display_surface(posterior, MAIN_BOUNDS, bandwidth_nm * 1.852)["areas_km2"]
            for key, posterior in posteriors.items()
        }
    summaries = {}
    for key, posterior in posteriors.items():
        summary = posterior_summary(posterior["longitude"], posterior["latitude"], posterior["weights"])
        summary["display_hpd_area_km2"] = surfaces[key]["areas_km2"]
        summary["display_hpd_achieved_mass"] = surfaces[key]["achieved_mass"]
        summary["display_edge_mass"] = surfaces[key]["edge_display_mass"]
        summary["evidence"] = posterior["evidence"]
        summary["model_scope"] = posterior["model_scope"]
        summary["seeds"] = posterior["seeds"]
        posterior["summary"] = summary
        summaries[key] = summary

    matplotlib.rcParams.update({
        "font.family": "DejaVu Sans",
        "font.size": 9,
        "axes.titlesize": 10,
        "axes.labelsize": 9,
        "svg.hashsalt": "mh370-posterior-search-context-v1",
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
    })
    stem = output / "posterior-evolution-search-context"
    figure_paths = render_figure(posteriors, surfaces, davey, atlas, inventory, land, stem)
    summary = {
        "schema_id": SCHEMA_ID,
        "schema_version": SCHEMA_VERSION,
        "posterior_combination": "none; sequential states shown separately",
        "impact_family": PRIMARY_IMPACT_FAMILY,
        "display_method": {
            "projection": f"local equirectangular; reference {REFERENCE_LATITUDE_DEG} latitude, {REFERENCE_LONGITUDE_DEG} longitude",
            "grid_cell_km": GRID_CELL_KM,
            "gaussian_bandwidth_nm": DISPLAY_BANDWIDTH_NM,
            "hpd_probabilities": list(HPD_PROBABILITIES),
            "boundary_policy": "all positive input weight must lie inside plot bounds; edge display mass <=1e-5",
            "interpretation": "display-only; particle weights and estimator summaries unchanged",
        },
        "posteriors": summaries,
        "bandwidth_area_sensitivity_km2": bandwidth_sensitivity,
        "davey": {
            "scope": "one-dimensional 00:19 latitude marginal only",
            "source": davey["source"],
            "latitude_quantiles_deg": davey["quantiles"],
            "two_dimensional_grid_available": False,
            "impact_figure_10_10_numeric_georeference_available": False,
        },
        "search_context": {
            "analysis_eligible": False,
            "negative_search_eligible": False,
            "area_rule": inventory["area_rule"],
            "rounding": inventory["rounding"],
        },
        "limitations": [
            "00:19 is a frozen-state 510-second continuation and corrected-R600 selection, not a fully stochastic final-interval model.",
            "Impact is conditional on the primary v0.1 fuel/aerodynamic/control family, not a terminal-family model average.",
            "Davey supplies no numerical 2D density grid; only its digitized latitude marginal is shown.",
            "Search footprints, approximate outlines, and AIS tracks have different semantics and are not negative evidence.",
        ],
    }
    summary_path = output / "summary.json"
    summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8", newline="\n")
    caption_path = output / "caption.md"
    write_caption(caption_path, summaries, davey)
    index_path = output / "index.html"
    write_index(index_path, summary)

    generator = Path(__file__).resolve()
    stable_outputs = sorted([*figure_paths, summary_path, caption_path, index_path])
    manifest = {
        "schema_id": "mh370-posterior-search-context-manifest",
        "schema_version": 1,
        "path_basis": "repository_root",
        "generator": logical_path(generator, repository),
        "generator_sha256": sha256(generator),
        "input_sha256": dict(sorted(input_hashes.items())),
        "output_sha256": {path.name: sha256(path) for path in stable_outputs},
        "reproduction_command_template": (
            f"{Path(sys.executable).name} -B {logical_path(generator, repository)} "
            f"--core-run {logical_path(args.core_run, repository)} "
            f"--continuation-run {logical_path(args.continuation_run, repository)} "
            f"--impact-suite {logical_path(args.impact_suite, repository)} "
            f"--davey-latitude {logical_path(davey_path, repository)} "
            f"--search-atlas {logical_path(atlas_path, repository)} "
            f"--area-inventory {logical_path(inventory_path, repository)} "
            f"--land {logical_path(land_path, repository)} --output <new-empty-output-directory>"
        ),
        "command_working_directory": "repository_root",
    }
    manifest_path = output / "run-manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8", newline="\n")
    ledger_paths = sorted([*stable_outputs, manifest_path])
    ledger = {path.name: sha256(path) for path in ledger_paths}
    (output / "artifact-sha256.json").write_text(json.dumps(ledger, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    print(f"status=complete output={output} particles=150000,150000,2560")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, KeyError, np.linalg.LinAlgError) as error:
        print(f"error: {error}", file=sys.stderr)
        raise SystemExit(2)
