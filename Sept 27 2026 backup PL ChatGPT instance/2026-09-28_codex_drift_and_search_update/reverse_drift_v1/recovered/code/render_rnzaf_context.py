#!/usr/bin/env python3
"""Render RNZAF-labelled image GPS metadata beside Pléiades sensitivities.

The workbook contains point metadata, not image footprints or searched-area
coverage.  This source-only renderer keeps that distinction visible and can
optionally overlay a runner-generated parent/conditional impact particle pair.
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import hashlib
import json
import math
import re
import zipfile
from collections import Counter
from pathlib import Path
from xml.etree import ElementTree

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


SCHEMA = "mh370-rnzaf-image-metadata-context/1"
XLSX_NS = {"x": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
COORDINATE = re.compile(r"^([0-9. ]+)\s*([NSEW])\s*$", re.IGNORECASE)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def column_index(reference: str) -> int:
    letters = "".join(character for character in reference if character.isalpha())
    value = 0
    for character in letters.upper():
        value = value * 26 + ord(character) - ord("A") + 1
    return value - 1


def workbook_rows(path: Path) -> list[dict[str, str]]:
    with zipfile.ZipFile(path) as archive:
        shared_root = ElementTree.fromstring(archive.read("xl/sharedStrings.xml"))
        shared = [
            "".join(node.text or "" for node in item.findall(".//x:t", XLSX_NS))
            for item in shared_root.findall("x:si", XLSX_NS)
        ]
        sheet = ElementTree.fromstring(archive.read("xl/worksheets/sheet1.xml"))
    records: list[list[str]] = []
    for row in sheet.findall(".//x:sheetData/x:row", XLSX_NS):
        values: dict[int, str] = {}
        for cell in row.findall("x:c", XLSX_NS):
            reference = cell.attrib["r"]
            value_node = cell.find("x:v", XLSX_NS)
            value = "" if value_node is None else value_node.text or ""
            if cell.attrib.get("t") == "s" and value:
                value = shared[int(value)]
            values[column_index(reference)] = value
        width = max(values, default=-1) + 1
        records.append([values.get(index, "") for index in range(width)])
    if not records:
        raise ValueError("RNZAF workbook has no rows")
    headers = records[0]
    required = {"SourceFile", "GPSLatitude", "GPSLongitude", "DateTimeDigitized"}
    if not required.issubset(headers):
        raise ValueError(f"RNZAF workbook headers differ from the audited schema: {headers}")
    return [
        {header: row[index] if index < len(row) else "" for index, header in enumerate(headers)}
        for row in records[1:]
    ]


def coordinate(text: str) -> tuple[float, str] | None:
    text = text.strip()
    if not text:
        return None
    match = COORDINATE.match(text)
    if not match:
        raise ValueError(f"unparseable coordinate {text!r}")
    numeric = float(match.group(1).replace(" ", ""))
    return numeric, match.group(2).upper()


def normalize_records(rows: list[dict[str, str]]) -> list[dict[str, object]]:
    normalized = []
    for row_number, row in enumerate(rows, start=2):
        latitude = coordinate(row["GPSLatitude"])
        longitude = coordinate(row["GPSLongitude"])
        if (latitude is None) != (longitude is None):
            raise ValueError(f"row {row_number} has only one coordinate")
        corrected = False
        if latitude is None:
            latitude_deg = longitude_deg = None
        else:
            latitude_value, latitude_suffix = latitude
            longitude_value, longitude_suffix = longitude  # type: ignore[misc]
            if latitude_suffix in "EW" and longitude_suffix in "NS":
                corrected = True
                latitude_suffix, longitude_suffix = longitude_suffix, latitude_suffix
            if latitude_suffix not in "NS" or longitude_suffix not in "EW":
                raise ValueError(f"row {row_number} has unresolved coordinate suffixes")
            latitude_deg = latitude_value * (-1.0 if latitude_suffix == "S" else 1.0)
            longitude_deg = longitude_value * (-1.0 if longitude_suffix == "W" else 1.0)
            if not (-90.0 <= latitude_deg <= 90.0 and -180.0 <= longitude_deg < 180.0):
                raise ValueError(f"row {row_number} is outside WGS84 degree ranges")
        raw_time = row["DateTimeDigitized"].strip()
        normalized.append(
            {
                "row": row_number,
                "source_file": row["SourceFile"].strip(),
                "date": raw_time[:10].replace(":", "-") if raw_time else "",
                "raw_datetime": raw_time,
                "latitude_deg": latitude_deg,
                "longitude_deg": longitude_deg,
                "suffix_corrected": corrected,
            }
        )
    return normalized


def read_arc(path: Path) -> list[tuple[float, float]]:
    geometry = json.loads(path.read_text(encoding="utf-8"))
    if geometry.get("type") == "FeatureCollection":
        coordinates = geometry["features"][0]["geometry"]["coordinates"]
    elif geometry.get("type") == "Feature":
        coordinates = geometry["geometry"]["coordinates"]
    else:
        coordinates = geometry["coordinates"]
    return [(float(longitude), float(latitude)) for longitude, latitude in coordinates]


def read_pleiades(grid_path: Path, surfaces_path: Path, surface_id: str) -> dict[str, np.ndarray]:
    with grid_path.open(newline="", encoding="utf-8") as stream:
        grid_rows = list(csv.DictReader(stream))
    with surfaces_path.open(newline="", encoding="utf-8") as stream:
        values = {
            row["cell_id"]: row
            for row in csv.DictReader(stream)
            if row["surface_id"] == surface_id
        }
    if not grid_rows or len(values) != len(grid_rows):
        raise ValueError("selected Pléiades surface does not cover the common grid")
    along_count = max(int(row["along_index"]) for row in grid_rows) + 1
    cross_count = max(int(row["cross_index"]) for row in grid_rows) + 1
    latitude = np.full((along_count, cross_count), np.nan)
    longitude = np.full_like(latitude, np.nan)
    score = np.full_like(latitude, np.nan)
    probability = np.full_like(latitude, np.nan)
    for row in grid_rows:
        along = int(row["along_index"])
        cross = int(row["cross_index"])
        value = values[row["cell_id"]]
        latitude[along, cross] = float(row["latitude_deg"])
        longitude[along, cross] = float(row["longitude_deg"])
        score[along, cross] = float(value["relative_likelihood"])
        probability[along, cross] = float(value["normalized_probability_mass"])
    if not all(np.isfinite(array).all() for array in (latitude, longitude, score, probability)):
        raise ValueError("Pléiades grid has missing/non-finite values")
    return {"latitude": latitude, "longitude": longitude, "score": score, "probability": probability}


def hpd_threshold(values: np.ndarray, masses: np.ndarray, target: float) -> float:
    order = np.argsort(values.ravel())[::-1]
    cumulative = np.cumsum(masses.ravel()[order])
    index = min(int(np.searchsorted(cumulative, target, side="left")), len(order) - 1)
    return float(values.ravel()[order[index]])


def effective_sample_size(weights: np.ndarray) -> float:
    if weights.ndim != 1 or not np.isfinite(weights).all() or np.any(weights < 0.0):
        raise ValueError("particle weights must be a finite nonnegative vector")
    total = float(weights.sum())
    if total <= 0.0:
        raise ValueError("particle weights have no positive mass")
    normalized = weights / total
    return float(1.0 / np.square(normalized).sum())


def read_particles(path: Path | None) -> dict[str, np.ndarray | float] | None:
    if path is None:
        return None
    with path.open(newline="", encoding="utf-8") as stream:
        rows = list(csv.DictReader(stream))
    if not rows:
        raise ValueError("conditional-particle CSV is empty")
    conditional = np.asarray([float(row["conditional_weight"]) for row in rows])
    return {
        "latitude": np.asarray([float(row["latitude_deg"]) for row in rows]),
        "longitude": np.asarray([float(row["longitude_deg"]) for row in rows]),
        "baseline": np.asarray([float(row["baseline_weight"]) for row in rows]),
        "conditional": conditional,
        "conditional_ess": effective_sample_size(conditional),
    }


def smooth_density(
    latitude: np.ndarray,
    longitude: np.ndarray,
    weight: np.ndarray,
    bounds: tuple[float, float, float, float],
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    longitude_min, longitude_max, latitude_min, latitude_max = bounds
    density, latitude_edges, longitude_edges = np.histogram2d(
        latitude,
        longitude,
        bins=(96, 96),
        range=((latitude_min, latitude_max), (longitude_min, longitude_max)),
        weights=weight,
    )
    kernel_axis = np.arange(-4, 5, dtype=float)
    kernel = np.exp(-0.5 * (kernel_axis / 1.6) ** 2)
    kernel /= kernel.sum()
    density = np.apply_along_axis(lambda values: np.convolve(values, kernel, mode="same"), 0, density)
    density = np.apply_along_axis(lambda values: np.convolve(values, kernel, mode="same"), 1, density)
    total = density.sum()
    if total <= 0:
        raise ValueError("particle density has no mass in the plotted bounds")
    density /= total
    latitude_centres = 0.5 * (latitude_edges[:-1] + latitude_edges[1:])
    longitude_centres = 0.5 * (longitude_edges[:-1] + longitude_edges[1:])
    return longitude_centres, latitude_centres, density


def particle_threshold(density: np.ndarray, target: float) -> float:
    ordered = np.sort(density.ravel())[::-1]
    cumulative = np.cumsum(ordered)
    return float(ordered[min(int(np.searchsorted(cumulative, target)), len(ordered) - 1)])


def draw_land(axis: plt.Axes, land_path: Path) -> None:
    features = json.loads(land_path.read_text(encoding="utf-8"))["features"]
    for feature in features:
        geometry = feature["geometry"]
        polygons = geometry["coordinates"] if geometry["type"] == "MultiPolygon" else [geometry["coordinates"]]
        for polygon in polygons:
            ring = np.asarray(polygon[0], dtype=float)
            if (
                ring[:, 0].max() < 85.0
                or ring[:, 0].min() > 105.0
                or ring[:, 1].max() < -50.0
                or ring[:, 1].min() > -15.0
            ):
                continue
            axis.fill(ring[:, 0], ring[:, 1], color="#f4f1ea", edgecolor="#888888", linewidth=0.35, zorder=0)


def draw_pleiades(axis: plt.Axes, surface: dict[str, np.ndarray], label: bool = True) -> None:
    thresholds = [
        hpd_threshold(surface["score"], surface["probability"], probability)
        for probability in (0.99, 0.95, 0.90, 0.50)
    ]
    axis.contourf(
        surface["longitude"],
        surface["latitude"],
        surface["score"],
        levels=[thresholds[0], thresholds[1], thresholds[2], thresholds[3], float(surface["score"].max()) * 1.000001],
        colors=["#ece9f5", "#ddd7ed", "#c8bde2", "#aa96d1"],
        alpha=0.62,
        zorder=1,
    )
    contours = axis.contour(
        surface["longitude"],
        surface["latitude"],
        surface["score"],
        levels=thresholds,
        colors=["#8b7aa8", "#735d96", "#5d447f", "#3f2866"],
        linewidths=[0.65, 0.8, 0.95, 1.2],
        zorder=3,
    )
    if label:
        labels = {level: text for level, text in zip(contours.levels, ("99%", "95%", "90%", "50%"))}
        axis.clabel(contours, contours.levels, fmt=labels, fontsize=6, inline_spacing=2)
    longitude = surface["longitude"]
    latitude = surface["latitude"]
    boundary_longitude = np.concatenate((longitude[0, :], longitude[1:, -1], longitude[-1, -2::-1], longitude[-2:0:-1, 0]))
    boundary_latitude = np.concatenate((latitude[0, :], latitude[1:, -1], latitude[-1, -2::-1], latitude[-2:0:-1, 0]))
    axis.plot(boundary_longitude, boundary_latitude, color="#3f2866", linewidth=0.7, linestyle="--", zorder=3)


def draw_particle_contours(
    axis: plt.Axes,
    particles: dict[str, np.ndarray],
    weight_name: str,
    bounds: tuple[float, float, float, float],
    color: str,
    linestyle: str,
    label: str,
) -> None:
    longitude, latitude, density = smooth_density(
        particles["latitude"], particles["longitude"], particles[weight_name], bounds
    )
    levels = [particle_threshold(density, probability) for probability in (0.99, 0.95, 0.90, 0.50)]
    axis.contour(
        longitude,
        latitude,
        density,
        levels=levels,
        colors=[color] * 4,
        linewidths=[0.7, 0.85, 1.0, 1.35],
        linestyles=[linestyle] * 4,
        zorder=5,
    )
    axis.plot([], [], color=color, linestyle=linestyle, linewidth=1.2, label=label)


def render(
    records: list[dict[str, object]],
    arc: list[tuple[float, float]],
    surface: dict[str, np.ndarray],
    particles: dict[str, np.ndarray | float] | None,
    land_path: Path,
    surface_id: str,
    output: Path,
) -> None:
    matplotlib.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "font.size": 8.2,
            "axes.titlesize": 9.4,
            "axes.labelsize": 8.0,
            "svg.hashsalt": "mh370-rnzaf-context-v1",
        }
    )
    figure, axes = plt.subplots(1, 3, figsize=(15.2, 6.3), constrained_layout=False)
    figure.subplots_adjust(left=0.045, right=0.985, top=0.865, bottom=0.155, wspace=0.18)
    figure.suptitle("RNZAF-labelled image GPS metadata in seventh-arc and Pléiades context", fontsize=12.5, y=0.965)
    figure.text(
        0.5,
        0.918,
        "Reported point metadata only — not image footprints, searched-area coverage, debris detections, or estimator evidence",
        ha="center",
        fontsize=8.6,
        color="#4b5563",
    )
    arc_longitude = [point[0] for point in arc]
    arc_latitude = [point[1] for point in arc]
    georeferenced = [record for record in records if record["latitude_deg"] is not None]
    positions = Counter(
        (round(float(record["latitude_deg"]), 6), round(float(record["longitude_deg"]), 6))
        for record in georeferenced
    )
    corrected_positions = {
        (round(float(record["latitude_deg"]), 6), round(float(record["longitude_deg"]), 6))
        for record in georeferenced
        if record["suffix_corrected"]
    }

    for axis in axes:
        draw_land(axis, land_path)
        axis.plot(arc_longitude, arc_latitude, color="#202020", linewidth=1.05, label="FL400 seventh arc", zorder=4)
        axis.grid(color="#d7dce2", linewidth=0.4, alpha=0.75)
        axis.set_xlabel("Longitude (°E)")
        axis.set_ylabel("Latitude (°)")
        axis.set_aspect(1.0 / math.cos(math.radians(-34.0)), adjustable="box")

    context = axes[0]
    draw_pleiades(context, surface, label=False)
    for (latitude, longitude), count in positions.items():
        context.scatter(
            longitude,
            latitude,
            s=11.0 + 8.0 * math.sqrt(count),
            facecolor="#1f78b4" if (latitude, longitude) not in corrected_positions else "white",
            edgecolor="#0e4f7a" if (latitude, longitude) not in corrected_positions else "#c2410c",
            marker="o" if (latitude, longitude) not in corrected_positions else "D",
            linewidth=0.7,
            alpha=0.82,
            zorder=6,
        )
    context.set_xlim(91.2, 99.0)
    context.set_ylim(-45.0, -19.0)
    context.set_title("A  RNZAF metadata locator\nmarker area scales with image multiplicity", loc="left")
    context.plot([], [], "o", color="#1f78b4", markersize=4, label="reported GPS position")
    context.plot([], [], "D", markerfacecolor="white", markeredgecolor="#c2410c", markersize=4, label="suffix corrected")
    context.legend(loc="lower right", frameon=True, framealpha=0.96, fontsize=6.8)

    proxy = axes[1]
    draw_pleiades(proxy, surface)
    proxy.set_xlim(89.8, 99.0)
    proxy.set_ylim(-40.2, -30.0)
    proxy.set_title(f"B  Pléiades conditional proxy: {surface_id}\n50/90/95/99% HPD; uncalibrated sensitivity", loc="left")
    proxy.plot([], [], color="#5d447f", linestyle="--", label="native ±100 NM support")
    proxy.legend(loc="lower left", frameon=True, framealpha=0.96, fontsize=6.8)

    comparison = axes[2]
    draw_pleiades(comparison, surface, label=False)
    comparison.set_xlim(87.0, 100.0)
    comparison.set_ylim(-45.0, -29.5)
    if particles is not None:
        conditional_ess = float(particles["conditional_ess"])
        bounds = (87.0, 100.0, -45.0, -29.5)
        draw_particle_contours(
            comparison, particles, "baseline", bounds, "#172554", "--", "parent impact PDF"
        )
        draw_particle_contours(
            comparison,
            particles,
            "conditional",
            bounds,
            "#b91c1c",
            "-",
            "Pléiades sensitivity (unresolved)",
        )
        comparison.set_title(
            "C  Impact-particle comparison\n"
            f"numerically unresolved · display only · conditional ESS {conditional_ess:.2f}",
            loc="left",
        )
        comparison.legend(loc="lower left", frameon=True, framealpha=0.96, fontsize=6.8)
    else:
        comparison.text(
            0.5,
            0.5,
            "Impact-particle branch not supplied\n(panel intentionally left diagnostic-only)",
            transform=comparison.transAxes,
            ha="center",
            va="center",
            color="#6b7280",
        )
        comparison.set_title("C  Optional integrated impact comparison", loc="left")

    conditional_note = (
        f" Panel C conditional ESS is {float(particles['conditional_ess']):.2f}; its red contours are "
        "numerically unresolved and display only."
        if particles is not None
        else ""
    )
    figure.text(
        0.045,
        0.055,
        "Coordinate suffix corrections affect six rows where latitude carried E and longitude carried S; numeric columns were retained. "
        "RNZAF timestamps lack a declared time zone, datum, altitude, orientation/FOV, outcome, and completeness statement. "
        "Pléiades components are alternative transport families; this figure applies one named surface only."
        + conditional_note,
        ha="left",
        va="bottom",
        fontsize=6.8,
        color="#4b5563",
        wrap=True,
    )
    metadata = {
        "Title": "RNZAF-labelled image GPS metadata in Pléiades context",
        "Author": "MH370 estimator source recreation",
        "Subject": "Display-only RNZAF point metadata and conditional Pléiades sensitivity",
        "CreationDate": dt.datetime(2014, 3, 8, tzinfo=dt.timezone.utc),
        "ModDate": dt.datetime(2014, 3, 8, tzinfo=dt.timezone.utc),
    }
    figure.savefig(output.with_suffix(".svg"), format="svg", metadata={"Date": "2014-03-08"})
    figure.savefig(output.with_suffix(".pdf"), format="pdf", metadata=metadata)
    figure.savefig(output.with_suffix(".png"), format="png", dpi=260, metadata={"Software": "matplotlib"})
    plt.close(figure)


def write_records(path: Path, records: list[dict[str, object]]) -> None:
    fields = [
        "row",
        "source_file",
        "date",
        "raw_datetime",
        "latitude_deg",
        "longitude_deg",
        "suffix_corrected",
    ]
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(records)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workbook", type=Path, required=True)
    parser.add_argument("--grid", type=Path, required=True)
    parser.add_argument("--surfaces", type=Path, required=True)
    parser.add_argument("--surface-id", default="equal_transport_family_model_average")
    parser.add_argument("--seventh-arc", type=Path, required=True)
    parser.add_argument("--land", type=Path, required=True)
    parser.add_argument("--conditional-particles", type=Path)
    parser.add_argument("--output-directory", type=Path, required=True)
    arguments = parser.parse_args()
    arguments.output_directory.mkdir(parents=True, exist_ok=True)

    records = normalize_records(workbook_rows(arguments.workbook))
    surface = read_pleiades(arguments.grid, arguments.surfaces, arguments.surface_id)
    particles = read_particles(arguments.conditional_particles)
    stem = arguments.output_directory / "rnzaf-pleiades-impact-context"
    render(
        records,
        read_arc(arguments.seventh_arc),
        surface,
        particles,
        arguments.land,
        arguments.surface_id,
        stem,
    )
    records_path = arguments.output_directory / "rnzaf-image-metadata.csv"
    write_records(records_path, records)
    georeferenced = [record for record in records if record["latitude_deg"] is not None]
    distinct = {
        (round(float(record["latitude_deg"]), 6), round(float(record["longitude_deg"]), 6))
        for record in georeferenced
    }
    inputs = {
        "workbook": sha256(arguments.workbook),
        "grid": sha256(arguments.grid),
        "surfaces": sha256(arguments.surfaces),
        "seventh_arc": sha256(arguments.seventh_arc),
        "land": sha256(arguments.land),
    }
    if arguments.conditional_particles is not None:
        inputs["conditional_particles"] = sha256(arguments.conditional_particles)
    artifact_names = [
        "rnzaf-pleiades-impact-context.svg",
        "rnzaf-pleiades-impact-context.pdf",
        "rnzaf-pleiades-impact-context.png",
        "rnzaf-image-metadata.csv",
    ]
    summary = {
        "schema": SCHEMA,
        "status": "display_context_only",
        "surface_id": arguments.surface_id,
        "records": len(records),
        "georeferenced_records": len(georeferenced),
        "missing_coordinate_records": len(records) - len(georeferenced),
        "distinct_positions": len(distinct),
        "suffix_corrected_records": sum(bool(record["suffix_corrected"]) for record in records),
        "dates": sorted({str(record["date"]) for record in records if record["date"]}),
        "conditional_impact_particles_included": particles is not None,
        "conditional_effective_sample_size": (
            float(particles["conditional_ess"]) if particles is not None else None
        ),
        "conditional_resolution_status": (
            "numerically_unresolved_display_only" if particles is not None else "not_supplied"
        ),
        "input_sha256": inputs,
        "artifact_sha256": {
            name: sha256(arguments.output_directory / name) for name in artifact_names
        },
        "scientific_scope": (
            "Reported RNZAF-labelled GPS metadata points only—not image footprints, searched-area coverage, "
            "non-detection evidence, debris observations, or an estimator likelihood. The selected Pléiades "
            "surface and any impact update are explicitly uncalibrated conditional sensitivities."
        ),
    }
    summary_path = arguments.output_directory / "rnzaf-context-summary.json"
    summary_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    hashes = {name: sha256(arguments.output_directory / name) for name in artifact_names + [summary_path.name]}
    (arguments.output_directory / "SHA256SUMS").write_text(
        "".join(f"{digest}  {name}\n" for name, digest in sorted(hashes.items())),
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
