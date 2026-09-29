#!/usr/bin/env python3
"""Render separately normalized conditional impact families.

The renderer never pools model families and never edits run artifacts.  It consumes the
typed impact handoffs plus transition sidecars emitted by the Rust hub, performs only
display normalization and weighted descriptive summaries, and writes deterministic
publication graphics and a browser report.
"""

from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone
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
from matplotlib.patches import Polygon
import numpy as np
from scipy.stats import gaussian_kde


SCHEMA_ID = "mh370-impact-release-report"
SCHEMA_VERSION = 1
HPD_MASSES = (0.50, 0.90, 0.95, 0.99)
EARTH_KM_PER_DEGREE = 111.195
SOURCE_UTC_UNIX_S = 1_394_237_459.0
FAMILY_TAGS = ("P", "F", "A", "C", "E")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def logical_path(path: Path, relative_to: Path) -> str:
    return Path(os.path.relpath(path.resolve(), relative_to.resolve())).as_posix()


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def normalized_weights(particles: list[dict]) -> np.ndarray:
    logs = np.asarray([particle["normalized_log_weight"] for particle in particles], dtype=float)
    if logs.size < 2 or not np.all(np.isfinite(logs)):
        raise ValueError("impact family needs at least two particles with finite log weights")
    maximum = float(np.max(logs))
    weights = np.exp(logs - maximum)
    weights /= np.sum(weights)
    if abs(float(np.sum(weights)) - 1.0) > 1.0e-12:
        raise ValueError("impact weights failed independent normalization")
    return weights


def weighted_quantile(values: np.ndarray, weights: np.ndarray, probability: float) -> float:
    order = np.argsort(values, kind="stable")
    ordered_values = values[order]
    cumulative = np.cumsum(weights[order])
    return float(ordered_values[np.searchsorted(cumulative, probability, side="left")])


def weighted_mean(values: np.ndarray, weights: np.ndarray) -> float:
    return float(np.sum(values * weights))


def weighted_circular_mean_degrees(values: np.ndarray, weights: np.ndarray) -> float:
    radians = np.deg2rad(values)
    return math.degrees(
        math.atan2(float(np.sum(weights * np.sin(radians))), float(np.sum(weights * np.cos(radians))))
    ) % 360.0


def utc_text(unix_s: float) -> str:
    return datetime.fromtimestamp(unix_s, timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")


def first_event_elapsed(record: dict, event_name: str, sidecar: dict) -> float | None:
    origin = sidecar["source_checkpoint_time_unix_s_utc"] - sidecar["relative_time_origin_unix_s_utc"]
    for event in record["transition"]["events"]:
        if event["kind"]["event"] == event_name:
            return float(event["time"]) - origin
    return None


def record_index(sidecar: dict) -> dict[int, dict]:
    result = {}
    for record in sidecar["records"]:
        draw = int(record["eof_draw_id"])
        if draw in result:
            raise ValueError("duplicate EOF draw identity in transition sidecar")
        result[draw] = record
    return result


def family_arrays(handoff: dict, sidecar: dict) -> tuple[dict[str, np.ndarray], np.ndarray]:
    if handoff.get("scenario_combination") != {"kind": "separate"} or len(handoff.get("eof_scenarios", [])) != 1:
        raise ValueError("renderer accepts only one separately normalized EOF family per handoff")
    particles = handoff["particles"]
    if any(particle.get("attitude") is not None or particle.get("contact_duration_s") is not None for particle in particles):
        raise ValueError("v0.1 report requires unresolved attitude and contact duration to remain null")
    weights = normalized_weights(particles)
    records = record_index(sidecar)
    selected_records = [records[int(particle["identity"]["eof_draw_id"])] for particle in particles]

    east = np.asarray([particle["kinematics"]["ground_velocity_enu_m_s"]["east"] for particle in particles])
    north = np.asarray([particle["kinematics"]["ground_velocity_enu_m_s"]["north"] for particle in particles])
    arrays = {
        "latitude_deg": np.asarray([particle["kinematics"]["position_wgs84"]["latitude"] for particle in particles]),
        "longitude_deg": np.asarray([particle["kinematics"]["position_wgs84"]["longitude"] for particle in particles]),
        "impact_utc_unix_s": np.asarray([particle["kinematics"]["time_utc_unix_s"] for particle in particles]),
        "vertical_speed_m_s": np.asarray([particle["kinematics"]["ground_velocity_enu_m_s"]["up"] for particle in particles]),
        "horizontal_speed_m_s": np.hypot(east, north),
        "ground_heading_deg": np.mod(np.degrees(np.arctan2(east, north)), 360.0),
        "total_energy_j": np.asarray([particle["energy"]["total_j"] for particle in particles]),
        "horizontal_energy_j": np.asarray([particle["energy"]["horizontal_j"] for particle in particles]),
        "vertical_energy_j": np.asarray([particle["energy"]["vertical_j"] for particle in particles]),
        "displacement_nm": np.asarray([particle["kinematics"]["displacement_from_last_contact_nm"] for particle in particles]),
        "impact_angle_deg": np.asarray([record["transition"]["impact"]["impact_angle"] for record in selected_records]),
        "dual_flameout_elapsed_s": np.asarray([
            first_event_elapsed(record, "dual_engine_generator_loss", sidecar) for record in selected_records
        ], dtype=float),
    }
    if any(not np.all(np.isfinite(values)) for values in arrays.values()):
        raise ValueError("impact family contains missing or non-finite reported dynamics")
    return arrays, weights


def load_seed_pool(
    entry: dict,
    suite_root: Path,
    input_hashes: dict[str, str],
) -> dict:
    if entry.get("source_seed_combination") != "equal_numerical_replicates":
        raise ValueError(f"family {entry['id']} lacks the numerical-replicate contract")
    handoffs = []
    sidecars = []
    array_parts = []
    weight_parts = []
    scenario_hashes = set()
    source_model_families = set()
    upstream_input_hashes = set()
    source_seeds = set()
    for run in entry["runs"]:
        source_seed = int(run["source_seed"])
        if source_seed in source_seeds:
            raise ValueError(f"family {entry['id']} repeats source seed {source_seed}")
        source_seeds.add(source_seed)
        handoff_path = suite_root / run["impact_handoff"]
        sidecar_path = suite_root / run["transition_sidecar"]
        if (
            sha256(handoff_path) != run["impact_handoff_sha256"]
            or sha256(sidecar_path) != run["transition_sidecar_sha256"]
        ):
            raise ValueError(
                f"suite artifact hash mismatch for {entry['id']} seed {source_seed}"
            )
        handoff = load_json(handoff_path)
        sidecar = load_json(sidecar_path)
        arrays, weights = family_arrays(handoff, sidecar)
        handoffs.append(handoff)
        sidecars.append(sidecar)
        array_parts.append(arrays)
        weight_parts.append(weights)
        scenario_hashes.add(handoff["eof_scenarios"][0]["config_sha256"])
        source_model_families.add(handoff["source_runs"][0]["model_family"])
        upstream_input_hashes.add(
            json.dumps(
                handoff["source_runs"][0]["upstream_input_sha256"], sort_keys=True
            )
        )
        input_hashes[
            f"{entry['id']}/seed-{source_seed}/impact-posterior-handoff.json"
        ] = sha256(handoff_path)
        input_hashes[
            f"{entry['id']}/seed-{source_seed}/transition-sidecar.json"
        ] = sha256(sidecar_path)
    if (
        len(scenario_hashes) != 1
        or len(source_model_families) != 1
        or len(upstream_input_hashes) != 1
    ):
        raise ValueError(
            f"family {entry['id']} mixes scenario or upstream model identities"
        )
    replicate_count = len(weight_parts)
    if replicate_count < 2:
        raise ValueError(
            f"family {entry['id']} needs at least two numerical-seed replicates"
        )
    arrays = {
        name: np.concatenate([part[name] for part in array_parts])
        for name in array_parts[0]
    }
    weights = np.concatenate([part / replicate_count for part in weight_parts])
    if abs(float(np.sum(weights)) - 1.0) > 1.0e-12:
        raise ValueError(f"family {entry['id']} seed pool failed normalization")
    return {
        "entry": entry,
        "handoffs": handoffs,
        "sidecars": sidecars,
        "arrays": arrays,
        "weights": weights,
        "scenario_config_sha256": next(iter(scenario_hashes)),
        "source_model_family": next(iter(source_model_families)),
    }


def hpd_surface(
    longitude: np.ndarray,
    latitude: np.ndarray,
    weights: np.ndarray,
    bounds: tuple[float, float, float, float],
) -> dict:
    xmin, xmax, ymin, ymax = bounds
    x = np.linspace(xmin, xmax, 241)
    y = np.linspace(ymin, ymax, 241)
    xx, yy = np.meshgrid(x, y)
    kde = gaussian_kde(np.vstack((longitude, latitude)), weights=weights, bw_method="scott")
    density = kde(np.vstack((xx.ravel(), yy.ravel()))).reshape(xx.shape)
    dx = float(x[1] - x[0])
    dy = float(y[1] - y[0])
    mass = density * dx * dy
    mass /= float(np.sum(mass))
    order = np.argsort(density.ravel())[::-1]
    cumulative = np.cumsum(mass.ravel()[order])
    thresholds = {}
    areas = {}
    cell_area = EARTH_KM_PER_DEGREE**2 * np.cos(np.deg2rad(yy)) * dx * dy
    for probability in HPD_MASSES:
        index = min(int(np.searchsorted(cumulative, probability, side="left")), len(order) - 1)
        threshold = float(density.ravel()[order[index]])
        thresholds[str(probability)] = threshold
        areas[str(probability)] = float(np.sum(cell_area[density >= threshold]))
    return {
        "x": x,
        "y": y,
        "xx": xx,
        "yy": yy,
        "density": density,
        "thresholds": thresholds,
        "areas_km2": areas,
    }


def load_land(path: Path) -> list[np.ndarray]:
    source = load_json(path)
    polygons = []
    for feature in source["features"]:
        geometry = feature["geometry"]
        coordinates = geometry["coordinates"]
        if geometry["type"] == "Polygon":
            coordinates = [coordinates]
        elif geometry["type"] != "MultiPolygon":
            raise ValueError(f"unexpected land geometry {geometry['type']}")
        for polygon in coordinates:
            polygons.append(np.asarray(polygon[0], dtype=float))
    return polygons


def add_land(ax, polygons: list[np.ndarray], bounds: tuple[float, float, float, float]) -> None:
    xmin, xmax, ymin, ymax = bounds
    for points in polygons:
        if points[:, 0].max() < xmin or points[:, 0].min() > xmax or points[:, 1].max() < ymin or points[:, 1].min() > ymax:
            continue
        ax.add_patch(Polygon(points, closed=True, facecolor="#f2f1ec", edgecolor="#858585", linewidth=0.5, zorder=0))


def add_scale_bar(ax, bounds: tuple[float, float, float, float]) -> None:
    xmin, xmax, ymin, ymax = bounds
    latitude = ymin + 0.07 * (ymax - ymin)
    length_nm = 50.0
    length_lon = length_nm / (60.0 * math.cos(math.radians(latitude)))
    start = xmin + 0.07 * (xmax - xmin)
    ax.plot([start, start + length_lon], [latitude, latitude], color="#222222", linewidth=2.0, zorder=10)
    ax.plot([start, start], [latitude - 0.025, latitude + 0.025], color="#222222", linewidth=1.2, zorder=10)
    ax.plot([start + length_lon, start + length_lon], [latitude - 0.025, latitude + 0.025], color="#222222", linewidth=1.2, zorder=10)
    ax.text(start + length_lon / 2, latitude + 0.045, "50 NM", ha="center", va="bottom", fontsize=7)


def summary_for_family(entry: dict, sidecars: list[dict], arrays: dict, weights: np.ndarray, surface: dict) -> dict:
    r600_kinds: dict[str, int] = {}
    for sidecar in sidecars:
        for record in sidecar["records"]:
            kind = record["r600_score"]["status"]["kind"]
            r600_kinds[kind] = r600_kinds.get(kind, 0) + 1
    sidecar = sidecars[0]
    projection = sidecar["fuel_model_resolution"].get("martin_projection")
    metric_names = [
        "impact_utc_unix_s",
        "vertical_speed_m_s",
        "horizontal_speed_m_s",
        "total_energy_j",
        "displacement_nm",
        "impact_angle_deg",
        "dual_flameout_elapsed_s",
    ]
    metrics = {}
    for name in metric_names:
        values = arrays[name]
        metrics[name] = {
            "mean": weighted_mean(values, weights),
            "median": weighted_quantile(values, weights, 0.5),
            "central_90": [
                weighted_quantile(values, weights, 0.05),
                weighted_quantile(values, weights, 0.95),
            ],
        }
    return {
        "id": entry["id"],
        "title": entry["title"],
        "role": entry["role"],
        "source_seeds": [run["source_seed"] for run in entry["runs"]],
        "source_seed_combination": "equal_numerical_replicates",
        "particles": len(weights),
        "effective_sample_size": 1.0 / float(np.sum(weights**2)),
        "weighted_mean_position": {
            "latitude_deg": weighted_mean(arrays["latitude_deg"], weights),
            "longitude_deg": weighted_mean(arrays["longitude_deg"], weights),
        },
        "weighted_mean_ground_heading_deg": weighted_circular_mean_degrees(arrays["ground_heading_deg"], weights),
        "hpd_area_km2": surface["areas_km2"],
        "r600_status_counts": r600_kinds,
        "r600_log_evidence_increment_by_seed": {
            str(run["source_seed"]): run_sidecar["log_evidence_increment"]
            for run, run_sidecar in zip(entry["runs"], sidecars)
        },
        "r600_log_evidence_increment_mean": float(
            np.mean([item["log_evidence_increment"] for item in sidecars])
        ),
        "fuel_at_0011_kg": projection["end_total_fuel"] if projection else None,
        "fuel_anchor_kg": projection["start_total_fuel"] if projection else None,
        "fuel_projection_elapsed_s": projection["elapsed_seconds"] if projection else None,
        "left_feed_endurance_s": sidecar["fuel_allocation"]["left_endurance"],
        "right_feed_endurance_s": sidecar["fuel_allocation"]["right_endurance"],
        "kong_minus_martin_arc1_fraction": sidecar["fuel_model_resolution"].get("kong_minus_martin_arc1_fraction"),
        "aerodynamic_family": sidecar["scenario"]["aerodynamic_family"],
        "environment_diagnostics_by_seed": {
            str(run["source_seed"]): run_sidecar["environment_diagnostics"]
            for run, run_sidecar in zip(entry["runs"], sidecars)
        },
        "outcome_mass_by_seed": {
            str(run["source_seed"]): run_sidecar["outcome_mass"]
            for run, run_sidecar in zip(entry["runs"], sidecars)
        },
        "metrics": metrics,
        "attitude": "unresolved_null",
        "contact_duration": "unresolved_null",
    }


def save_figure(fig, output_stem: Path) -> list[Path]:
    paths = []
    metadata = {"Creator": "MH370 canonical report generator", "Date": None}
    png = output_stem.with_suffix(".png")
    svg = output_stem.with_suffix(".svg")
    pdf = output_stem.with_suffix(".pdf")
    fig.savefig(png, dpi=240, metadata={"Software": metadata["Creator"]})
    fig.savefig(svg, metadata=metadata)
    fig.savefig(pdf, metadata={"Creator": metadata["Creator"], "CreationDate": None, "ModDate": None})
    paths.extend((png, svg, pdf))
    return paths


def location_figure(families: list[dict], land: list[np.ndarray], bounds: tuple[float, float, float, float], output: Path) -> list[Path]:
    fig, axes = plt.subplots(2, 3, figsize=(13.2, 8.3), sharex=True, sharey=True)
    axes = axes.ravel()
    fills = ["#edf3fa", "#dce9f6", "#c8dcf0", "#a8c9e7"]
    for index, family in enumerate(families):
        ax = axes[index]
        add_land(ax, land, bounds)
        surface = family["surface"]
        density = surface["density"]
        threshold = surface["thresholds"]
        levels = [threshold[str(value)] for value in (0.99, 0.95, 0.90, 0.50)]
        levels = np.maximum.accumulate(np.asarray(levels, dtype=float))
        for position in range(1, len(levels)):
            if levels[position] <= levels[position - 1]:
                levels[position] = np.nextafter(levels[position - 1], math.inf)
        upper = float(np.max(density)) * 1.000001
        ax.contourf(surface["xx"], surface["yy"], density, levels=[*levels, upper], colors=fills, antialiased=True, zorder=1)
        contours = ax.contour(surface["xx"], surface["yy"], density, levels=levels, colors=["#7c9fc5", "#648ab3", "#446f9d", "#264f7d"], linewidths=[0.65, 0.75, 0.9, 1.05], zorder=3)
        labels = {level: label for level, label in zip(levels, ("99%", "95%", "90%", "50%"))}
        ax.clabel(contours, fmt=labels, inline=True, fontsize=6.5)
        summary = family["summary"]
        mean = summary["weighted_mean_position"]
        ax.scatter(mean["longitude_deg"], mean["latitude_deg"], marker="+", s=55, linewidth=1.3, color="#0f355e", zorder=8)
        heading = math.radians(summary["weighted_mean_ground_heading_deg"])
        dx = 0.18 * math.sin(heading)
        dy = 0.18 * math.cos(heading)
        ax.annotate("", xy=(mean["longitude_deg"] + dx, mean["latitude_deg"] + dy), xytext=(mean["longitude_deg"], mean["latitude_deg"]), arrowprops={"arrowstyle": "-|>", "color": "#0f355e", "lw": 1.0}, zorder=8)
        add_scale_bar(ax, bounds)
        tag = FAMILY_TAGS[index] if index < len(FAMILY_TAGS) else str(index + 1)
        ax.set_title(f"{tag}  {family['entry']['title']}", fontsize=9.2, pad=6)
        ax.text(0.02, 0.98, f"5 seeds · N={summary['particles']} · ESS={summary['effective_sample_size']:.1f}\n90% HPD≈{summary['hpd_area_km2']['0.9']:,.0f} km²\nmean {abs(mean['latitude_deg']):.2f}°S, {mean['longitude_deg']:.2f}°E", transform=ax.transAxes, ha="left", va="top", fontsize=7, bbox={"boxstyle": "round,pad=0.25", "facecolor": "white", "edgecolor": "#cccccc", "alpha": 0.92}, zorder=9)
        ax.grid(color="#d7d7d7", linewidth=0.35, alpha=0.8)
        ax.set_xlim(bounds[0], bounds[1])
        ax.set_ylim(bounds[2], bounds[3])
        ax.set_aspect(1.0 / math.cos(math.radians((bounds[2] + bounds[3]) / 2.0)))
    note = axes[-1]
    note.axis("off")
    fig.text(0.69, 0.405, "Scientific boundary", ha="left", va="top", fontsize=12, color="#173a60", weight="bold")
    fig.text(0.69, 0.37, "Each panel pools five numerical seeds equally, then is\nnormalized independently. No probability or averaging\nacross terminal families is shown.\n\nR600 BTO is the only new SATCOM likelihood; R1200\nBTO is held out, and final BFO/log-on timing do not\nupdate weights. OpenAP is an attached-flow proxy, not\ncalibrated B777 terminal aerodynamics. Attitude and\nwater-contact duration remain unresolved.", ha="left", va="top", fontsize=8.2, linespacing=1.35)
    handles = [Line2D([0], [0], color=color, lw=5, label=label) for color, label in zip(fills[::-1], ("50% HPD", "90% HPD", "95% HPD", "99% HPD"))]
    handles += [Line2D([0], [0], marker="+", color="#0f355e", lw=0, label="weighted mean + terminal heading")]
    note.legend(handles=handles, loc="lower left", frameon=True, facecolor="white", edgecolor="#cccccc", fontsize=8)
    fig.suptitle("MH370 conditional impact-location sensitivities", fontsize=15, y=0.995, color="#173a60")
    fig.text(0.5, 0.965, "Dynamic ERA5 atmosphere · Martin Trent-892 LRC fuel conditional · corrected R600 BTO only", ha="center", fontsize=9.5)
    for ax in axes[[0, 3]]:
        ax.set_ylabel("Latitude (°)")
    for ax in axes[3:5]:
        ax.set_xlabel("Longitude (°)")
    fig.subplots_adjust(left=0.055, right=0.985, top=0.92, bottom=0.065, wspace=0.12, hspace=0.18)
    paths = save_figure(fig, output / "impact-location-comparison")
    plt.close(fig)
    return paths


def great_circle_nm(first: dict, second: dict) -> float:
    lat1 = math.radians(first["latitude_deg"])
    lat2 = math.radians(second["latitude_deg"])
    dlat = lat2 - lat1
    dlon = math.radians(second["longitude_deg"] - first["longitude_deg"])
    value = math.sin(dlat / 2.0) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2.0) ** 2
    return 3440.065 * 2.0 * math.asin(min(1.0, math.sqrt(value)))


def gain_source_figure(
    primary: dict,
    gain: dict,
    land: list[np.ndarray],
    bounds: tuple[float, float, float, float],
    output: Path,
) -> list[Path]:
    fig, axes = plt.subplots(1, 3, figsize=(13.2, 4.7), gridspec_kw={"width_ratios": [1.0, 1.0, 0.82]})
    fills = ["#edf3fa", "#dce9f6", "#c8dcf0", "#a8c9e7"]
    titles = [
        "BTO + medium-BFO 00:11 source",
        "Conditional antenna-gain 00:11 source",
    ]
    for ax, family, title in zip(axes[:2], (primary, gain), titles):
        add_land(ax, land, bounds)
        surface = family["surface"]
        density = surface["density"]
        levels = np.asarray(
            [surface["thresholds"][str(value)] for value in (0.99, 0.95, 0.90, 0.50)],
            dtype=float,
        )
        levels = np.maximum.accumulate(levels)
        for position in range(1, len(levels)):
            if levels[position] <= levels[position - 1]:
                levels[position] = np.nextafter(levels[position - 1], math.inf)
        ax.contourf(
            surface["xx"], surface["yy"], density,
            levels=[*levels, float(np.max(density)) * 1.000001],
            colors=fills, antialiased=True,
        )
        ax.contour(
            surface["xx"], surface["yy"], density, levels=levels,
            colors=["#7c9fc5", "#648ab3", "#446f9d", "#264f7d"],
            linewidths=[0.65, 0.75, 0.9, 1.05],
        )
        summary = family["summary"]
        mean = summary["weighted_mean_position"]
        ax.scatter(mean["longitude_deg"], mean["latitude_deg"], marker="+", s=58, linewidth=1.4, color="#0f355e", zorder=8)
        add_scale_bar(ax, bounds)
        ax.set_title(title, fontsize=10)
        ax.text(
            0.02, 0.98,
            f"5 seeds · N={summary['particles']} · ESS={summary['effective_sample_size']:.1f}\n"
            f"90% HPD≈{summary['hpd_area_km2']['0.9']:,.0f} km²\n"
            f"mean {abs(mean['latitude_deg']):.2f}°S, {mean['longitude_deg']:.2f}°E",
            transform=ax.transAxes, ha="left", va="top", fontsize=7.2,
            bbox={"boxstyle": "round,pad=0.25", "facecolor": "white", "edgecolor": "#cccccc", "alpha": 0.92},
        )
        ax.grid(color="#d7d7d7", linewidth=0.35)
        ax.set_xlim(bounds[0], bounds[1])
        ax.set_ylim(bounds[2], bounds[3])
        ax.set_aspect(1.0 / math.cos(math.radians((bounds[2] + bounds[3]) / 2.0)))
        ax.set_xlabel("Longitude (°)")
    axes[0].set_ylabel("Latitude (°)")
    note = axes[2]
    note.axis("off")
    primary_summary = primary["summary"]
    gain_summary = gain["summary"]
    separation = great_circle_nm(
        primary_summary["weighted_mean_position"],
        gain_summary["weighted_mean_position"],
    )
    area_change = (
        gain_summary["hpd_area_km2"]["0.9"]
        / primary_summary["hpd_area_km2"]["0.9"]
        - 1.0
    ) * 100.0
    time_change = (
        gain_summary["metrics"]["impact_utc_unix_s"]["median"]
        - primary_summary["metrics"]["impact_utc_unix_s"]["median"]
    ) / 60.0
    note.text(0.02, 0.98, "Paired source sensitivity", ha="left", va="top", fontsize=12, color="#173a60", weight="bold")
    note.text(
        0.02, 0.87,
        f"EOF scenario hash is identical.\n"
        f"Weighted-mean separation: {separation:.1f} NM\n"
        f"90% HPD area change: {area_change:+.1f}%\n"
        f"Median impact-time change: {time_change:+.1f} min\n\n"
        "Only the 00:11 source posterior differs.\n"
        "The antenna-gain result is conditional and\n"
        "is not pooled with the baseline or treated\n"
        "as evidence for terminal-model selection.\n\n"
        "R600 BTO remains the sole added EOF\n"
        "likelihood in both panels.",
        ha="left", va="top", fontsize=9.2, linespacing=1.45,
    )
    fig.suptitle("Conditional antenna-gain sensitivity of the impact posterior", fontsize=15, color="#173a60")
    fig.subplots_adjust(left=0.06, right=0.985, top=0.86, bottom=0.12, wspace=0.18)
    paths = save_figure(fig, output / "impact-gain-source-comparison")
    plt.close(fig)
    return paths


def dynamics_figure(families: list[dict], output: Path) -> list[Path]:
    fig, axes = plt.subplots(2, 2, figsize=(11.2, 7.4))
    x = np.arange(len(families))
    colors = ["#234f7d", "#9a6336", "#6a5d9b", "#3d7c68", "#8c4966"]
    specs = [
        ("impact_utc_unix_s", "Impact time after 00:10:59 (min)", lambda value: (value - SOURCE_UTC_UNIX_S) / 60.0),
        ("vertical_speed_m_s", "Downward impact speed (m/s)", lambda value: -value),
        ("total_energy_j", "Total kinetic energy (GJ)", lambda value: value / 1.0e9),
        ("displacement_nm", "Displacement from 00:11 (NM)", lambda value: value),
    ]
    for ax, (name, title, transform) in zip(axes.ravel(), specs):
        medians = np.asarray([transform(family["summary"]["metrics"][name]["median"]) for family in families])
        lows = np.asarray([transform(family["summary"]["metrics"][name]["central_90"][0]) for family in families])
        highs = np.asarray([transform(family["summary"]["metrics"][name]["central_90"][1]) for family in families])
        lower = np.minimum(lows, highs)
        upper = np.maximum(lows, highs)
        for index, (median, low, high) in enumerate(zip(medians, lower, upper)):
            ax.errorbar(
                [index],
                [median],
                yerr=[[median - low], [high - median]],
                fmt="none",
                ecolor=colors[index],
                elinewidth=2,
                capsize=4,
                zorder=2,
            )
        ax.scatter(x, medians, s=48, color=colors, edgecolor="white", linewidth=0.6, zorder=3)
        ax.set_title(title, fontsize=10.5)
        ax.set_xticks(x, [FAMILY_TAGS[index] for index in range(len(families))])
        ax.grid(axis="y", color="#d5d5d5", linewidth=0.45)
        ax.text(0.02, 0.96, "median and central 90%", transform=ax.transAxes, ha="left", va="top", fontsize=7.5, color="#555555")
    fig.suptitle("Conditional impact dynamics and energy", fontsize=15, color="#173a60")
    legend_text = "   ".join(f"{FAMILY_TAGS[index]} {family['entry']['role']}" for index, family in enumerate(families))
    fig.text(0.5, 0.925, legend_text, ha="center", va="top", fontsize=7.5)
    fig.text(0.5, 0.012, "These intervals are within-family Monte Carlo summaries. They are not uncertainty across calibrated B777 terminal model families.", ha="center", fontsize=8)
    fig.subplots_adjust(left=0.09, right=0.98, top=0.87, bottom=0.09, wspace=0.20, hspace=0.28)
    paths = save_figure(fig, output / "impact-dynamics-comparison")
    plt.close(fig)
    return paths


def write_summary_csv(path: Path, summaries: list[dict]) -> None:
    fields = [
        "id", "title", "role", "particles", "effective_sample_size",
        "mean_latitude_deg", "mean_longitude_deg", "hpd90_area_km2",
        "r600_log_evidence_increment", "fuel_at_0011_kg", "left_feed_endurance_s",
        "right_feed_endurance_s", "median_impact_utc", "median_vertical_speed_m_s",
        "median_total_energy_j", "median_displacement_nm", "attitude", "contact_duration",
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        for summary in summaries:
            writer.writerow({
                "id": summary["id"], "title": summary["title"], "role": summary["role"],
                "particles": summary["particles"], "effective_sample_size": summary["effective_sample_size"],
                "mean_latitude_deg": summary["weighted_mean_position"]["latitude_deg"],
                "mean_longitude_deg": summary["weighted_mean_position"]["longitude_deg"],
                "hpd90_area_km2": summary["hpd_area_km2"]["0.9"],
                "r600_log_evidence_increment": summary["r600_log_evidence_increment_mean"],
                "fuel_at_0011_kg": summary["fuel_at_0011_kg"],
                "left_feed_endurance_s": summary["left_feed_endurance_s"],
                "right_feed_endurance_s": summary["right_feed_endurance_s"],
                "median_impact_utc": utc_text(summary["metrics"]["impact_utc_unix_s"]["median"]),
                "median_vertical_speed_m_s": summary["metrics"]["vertical_speed_m_s"]["median"],
                "median_total_energy_j": summary["metrics"]["total_energy_j"]["median"],
                "median_displacement_nm": summary["metrics"]["displacement_nm"]["median"],
                "attitude": summary["attitude"], "contact_duration": summary["contact_duration"],
            })


def write_report(
    path: Path,
    summaries: list[dict],
    conditional_source_summaries: list[dict],
) -> None:
    rows = []
    for index, summary in enumerate(summaries):
        mean = summary["weighted_mean_position"]
        metric = summary["metrics"]
        rows.append(
            "<tr>"
            f"<td>{FAMILY_TAGS[index]}</td><td><b>{html.escape(summary['title'])}</b><br><span>{html.escape(summary['role'])}</span></td>"
            f"<td>{summary['particles']} / {summary['effective_sample_size']:.1f}</td>"
            f"<td>{summary['fuel_at_0011_kg']:.1f}</td>"
            f"<td>{summary['left_feed_endurance_s']:.1f} / {summary['right_feed_endurance_s']:.1f}</td>"
            f"<td>{abs(mean['latitude_deg']):.3f}°S, {mean['longitude_deg']:.3f}°E</td>"
            f"<td>{summary['hpd_area_km2']['0.9']:,.0f}</td>"
            f"<td>{html.escape(utc_text(metric['impact_utc_unix_s']['median']))}</td>"
            f"<td>{-metric['vertical_speed_m_s']['median']:.2f}</td>"
            f"<td>{metric['total_energy_j']['median']/1e9:.3f}</td>"
            f"<td>{metric['displacement_nm']['median']:.1f}</td>"
            "</tr>"
        )
    gain = conditional_source_summaries[0]
    primary = summaries[0]
    gain_separation_nm = great_circle_nm(
        primary["weighted_mean_position"], gain["weighted_mean_position"]
    )
    document = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><title>MH370 conditional impact release</title>
<style>
body{{font:15px/1.5 system-ui,sans-serif;max-width:1500px;margin:2rem auto;padding:0 1.2rem;color:#222}}h1,h2{{color:#173a60}}.boundary{{background:#f4f7fa;border-left:5px solid #39658c;padding:1rem 1.2rem}}img{{max-width:100%;height:auto;border:1px solid #ddd}}table{{border-collapse:collapse;width:100%;font-size:12.5px}}th,td{{border-bottom:1px solid #ddd;padding:.5rem;vertical-align:top;text-align:right}}th:nth-child(2),td:nth-child(2){{text-align:left}}span{{color:#666}}code{{background:#f3f3f3;padding:.1rem .25rem}}a{{color:#165b92}}</style></head>
<body><h1>MH370 v0.1 conditional end-of-flight release</h1>
<div class="boundary"><b>Interpretive boundary.</b> The five terminal families are normalized and reported separately. They are sensitivity conditionals, not a calibrated family mixture. Dynamic ERA5 temperature and horizontal wind are sampled during propagation. Martin BSM Trent-892 LRC is a conditional fuel proxy and the Kong table is only a one-state coarse check. The OpenAP polars are attached-flow approximations, not B777 post-stall aerodynamics. Corrected 00:19:29 R600 BTO is the only added SATCOM likelihood; R1200 BTO is held out, while final BFO and log-on occurrence/timing do not update weights. Impact attitude and water-contact duration remain unresolved.</div>
<h2>Impact location</h2><p><a href="impact-location-comparison.svg">SVG</a> · <a href="impact-location-comparison.pdf">vector PDF</a> · <a href="impact-location-comparison.png">PNG</a></p><img src="impact-location-comparison.png" alt="Conditional impact maps">
<h2>Impact dynamics</h2><p><a href="impact-dynamics-comparison.svg">SVG</a> · <a href="impact-dynamics-comparison.pdf">vector PDF</a> · <a href="impact-dynamics-comparison.png">PNG</a></p><img src="impact-dynamics-comparison.png" alt="Impact dynamics sensitivities">
<h2>Conditional antenna-gain source branch</h2><p><a href="impact-gain-source-comparison.svg">SVG</a> · <a href="impact-gain-source-comparison.pdf">vector PDF</a> · <a href="impact-gain-source-comparison.png">PNG</a></p><img src="impact-gain-source-comparison.png" alt="Conditional gain source comparison"><p>The terminal scenario is byte-identical at its scenario hash. Changing only the five-seed 00:11 source from medium BFO to the conditional antenna-gain posterior shifts the weighted impact mean by {gain_separation_nm:.1f} NM. This is a conditional sensitivity, not a pooled estimate or terminal-family Bayes factor.</p>
<h2>Numerical comparison</h2><table><thead><tr><th>Tag</th><th>Family</th><th>N / ESS</th><th>Fuel at 00:11 kg</th><th>L/R feed endurance s</th><th>Weighted mean</th><th>90% HPD km²</th><th>Median impact UTC</th><th>Down m/s</th><th>Energy GJ</th><th>Distance NM</th></tr></thead><tbody>{''.join(rows)}</tbody></table>
<p>The HPD areas are descriptive KDE raster estimates for display, while every downstream composition must use the typed particle weights in the individual <code>impact-posterior-handoff.json</code> artifacts. The R600 log-evidence values are family-conditional normalizers and must not be interpreted as Bayes factors over these uncalibrated family choices.</p>
<h2>Files and reproducibility</h2><p><a href="summary.json">machine summary</a> · <a href="summary.csv">compact table</a> · <a href="report-manifest.json">report manifest</a> · <a href="artifact-sha256.json">artifact hashes</a></p>
</body></html>"""
    path.write_text(document, encoding="utf-8", newline="\n")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--suite", type=Path, required=True)
    parser.add_argument("--land", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    suite_path = args.suite.resolve()
    suite_root = suite_path.parent
    suite = load_json(suite_path)
    if suite.get("schema_id") != "mh370-impact-conditional-suite" or suite.get("family_combination") != "separate":
        raise ValueError("input is not a separate-family impact suite")
    if len(suite["families"]) != len(FAMILY_TAGS):
        raise ValueError(f"release report expects {len(FAMILY_TAGS)} declared families")
    output = args.output.resolve()
    if output.exists():
        raise FileExistsError(f"refusing to overwrite {output}")
    output.mkdir(parents=True)

    loaded = []
    all_latitude = []
    all_longitude = []
    input_hashes = {"suite-manifest.json": sha256(suite_path), "land.geojson": sha256(args.land.resolve())}
    for entry in suite["families"]:
        family = load_seed_pool(entry, suite_root, input_hashes)
        all_latitude.extend(family["arrays"]["latitude_deg"])
        all_longitude.extend(family["arrays"]["longitude_deg"])
        loaded.append(family)
    conditional_sources = []
    for entry in suite.get("conditional_source_branches", []):
        branch = load_seed_pool(entry, suite_root, input_hashes)
        all_latitude.extend(branch["arrays"]["latitude_deg"])
        all_longitude.extend(branch["arrays"]["longitude_deg"])
        conditional_sources.append(branch)

    longitude_padding = max(0.45, 0.12 * (max(all_longitude) - min(all_longitude)))
    latitude_padding = max(0.45, 0.12 * (max(all_latitude) - min(all_latitude)))
    bounds = (
        math.floor((min(all_longitude) - longitude_padding) * 4) / 4,
        math.ceil((max(all_longitude) + longitude_padding) * 4) / 4,
        math.floor((min(all_latitude) - latitude_padding) * 4) / 4,
        math.ceil((max(all_latitude) + latitude_padding) * 4) / 4,
    )
    for family in loaded:
        family["surface"] = hpd_surface(family["arrays"]["longitude_deg"], family["arrays"]["latitude_deg"], family["weights"], bounds)
        family["summary"] = summary_for_family(
            family["entry"],
            family["sidecars"],
            family["arrays"],
            family["weights"],
            family["surface"],
        )
    if len(conditional_sources) != 1:
        raise ValueError("release report requires exactly one conditional source branch")
    for branch in conditional_sources:
        branch["surface"] = hpd_surface(
            branch["arrays"]["longitude_deg"],
            branch["arrays"]["latitude_deg"],
            branch["weights"],
            bounds,
        )
        branch["summary"] = summary_for_family(
            branch["entry"],
            branch["sidecars"],
            branch["arrays"],
            branch["weights"],
            branch["surface"],
        )
    if conditional_sources[0]["scenario_config_sha256"] != loaded[0]["scenario_config_sha256"]:
        raise ValueError("conditional-gain source branch did not freeze the primary EOF scenario")
    if conditional_sources[0]["source_model_family"] != "bto-bfo-gain-conditional":
        raise ValueError("conditional source branch is not the declared gain-conditioned family")

    matplotlib.rcParams.update({
        "font.family": "DejaVu Sans", "font.size": 9, "axes.titlesize": 10,
        "axes.labelsize": 9, "svg.hashsalt": "mh370-impact-release-v1",
        "pdf.fonttype": 42, "ps.fonttype": 42,
    })
    land = load_land(args.land.resolve())
    figure_paths = location_figure(loaded, land, bounds, output)
    figure_paths += dynamics_figure(loaded, output)
    figure_paths += gain_source_figure(
        loaded[0], conditional_sources[0], land, bounds, output
    )
    summaries = [family["summary"] for family in loaded]
    conditional_source_summaries = [
        branch["summary"] for branch in conditional_sources
    ]
    summary = {
        "schema_id": SCHEMA_ID,
        "schema_version": SCHEMA_VERSION,
        "family_combination": "separate",
        "map_bounds_degrees": {"longitude": [bounds[0], bounds[1]], "latitude": [bounds[2], bounds[3]]},
        "hpd_method": "weighted Gaussian KDE on fixed 241x241 longitude-latitude raster; cell area uses spherical latitude scaling; display diagnostic only",
        "families": summaries,
        "conditional_source_branches": conditional_source_summaries,
        "scientific_boundary": [
            "No probability or averaging across terminal model families.",
            "R600 BTO is the only added SATCOM likelihood and recorded reception requires physical SATCOM power at the checkpoint.",
            "R1200 BTO is held out; final BFO and log-on time/occurrence do not update weights.",
            "OpenAP attached-flow polars are not calibrated B777 terminal aerodynamics.",
            "Impact attitude and contact duration are unresolved null fields."
        ],
    }
    summary_path = output / "summary.json"
    summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8", newline="\n")
    write_summary_csv(output / "summary.csv", summaries)
    write_report(output / "report.html", summaries, conditional_source_summaries)

    outputs = sorted([*figure_paths, summary_path, output / "summary.csv", output / "report.html"])
    repository = args.land.resolve().parents[3]
    report_manifest = {
        "schema_id": "mh370-impact-release-report-manifest",
        "schema_version": 1,
        "path_basis": "repository_root",
        "generator": logical_path(Path(__file__), repository),
        "generator_sha256": sha256(Path(__file__).resolve()),
        "input_sha256": dict(sorted(input_hashes.items())),
        "output_sha256": {path.name: sha256(path) for path in outputs},
        "reproduction_command_template": (
            f"{Path(sys.executable).name} {logical_path(Path(__file__), repository)} "
            f"--suite {logical_path(suite_path, repository)} "
            f"--land {logical_path(args.land, repository)} --output <new-empty-output-directory>"
        ),
        "command_working_directory": "repository_root",
    }
    manifest_path = output / "report-manifest.json"
    manifest_path.write_text(json.dumps(report_manifest, indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8", newline="\n")
    ledger_paths = sorted([*outputs, manifest_path])
    ledger = {path.name: sha256(path) for path in ledger_paths}
    (output / "artifact-sha256.json").write_text(json.dumps(ledger, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    print(f"status=complete families={len(families) if (families := loaded) else 0} report={output / 'report.html'}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, KeyError, np.linalg.LinAlgError) as error:
        print(f"error: {error}", file=sys.stderr)
        raise SystemExit(2)
