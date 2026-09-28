#!/usr/bin/env python3
"""Render the paired conditional-density report in the established map style."""

from __future__ import annotations

import csv
import json
import math
import textwrap
from datetime import datetime
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
from matplotlib.ticker import MultipleLocator


BUNDLE = Path(__file__).resolve().parents[1]
DATA = BUNDLE / "data"
OUTPUTS = BUNDLE / "outputs"
STEM = OUTPUTS / "pleiades-forward-impact-density"
MAP_EXTENT = (90.0, 94.0, -36.25, -34.0)
HPD_STYLES = {
    0.50: {"color": "#54278f", "alpha": 0.25, "linewidth": 1.35},
    0.90: {"color": "#9e9ac8", "alpha": 0.18, "linewidth": 1.05},
    0.95: {"color": "#dadaeb", "alpha": 0.28, "linewidth": 0.90},
}
MODEL_TITLES = {
    "bran2016": "BRAN2016 2.5 m layer",
    "oscar_v2_final": "OSCAR v2 Final upper-30-m control",
    "glorys12_waverys": "GLORYS12 0.494 m + WAVERYS Stokes",
    "equal_transport_family_model_average": "Equal-prior three-family model average",
}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def model_grid(rows: list[dict[str, str]]) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    along_count = max(int(row["alongIndex"]) for row in rows) + 1
    cross_count = max(int(row["crossIndex"]) for row in rows) + 1
    longitude = np.full((along_count, cross_count), np.nan)
    latitude = np.full((along_count, cross_count), np.nan)
    density = np.full((along_count, cross_count), np.nan)
    for row in rows:
        along = int(row["alongIndex"])
        cross = int(row["crossIndex"])
        longitude[along, cross] = float(row["longitude"])
        latitude[along, cross] = float(row["latitude"])
        density[along, cross] = float(row["densityPerKm2"])
    if not np.isfinite(longitude).all() or not np.isfinite(latitude).all():
        raise ValueError("source grid is incomplete")
    return longitude, latitude, density


def draw_hpd_layers(
    axis: plt.Axes,
    longitude: np.ndarray,
    latitude: np.ndarray,
    density: np.ndarray,
    model_summary: dict,
) -> None:
    upper = float(np.nanmax(density)) * (1.0 + 1e-9)
    for mass in (0.95, 0.90, 0.50):
        style = HPD_STYLES[mass]
        threshold = model_summary["hpd"][str(mass)]["densityThresholdPerKm2"]
        axis.contourf(
            longitude,
            latitude,
            density,
            levels=[threshold, upper],
            colors=[style["color"]],
            alpha=style["alpha"],
            zorder=0,
        )
        axis.contour(
            longitude,
            latitude,
            density,
            levels=[threshold],
            colors=[style["color"]],
            linewidths=style["linewidth"],
            linestyles="--" if mass == 0.95 else "-",
            zorder=1,
        )


def draw_arc_lines(axis: plt.Axes, rows: list[dict[str, str]]) -> None:
    by_cross: dict[float, list[dict[str, str]]] = {}
    for row in rows:
        cross = float(row["crossNm"])
        if cross in (-30.0, 0.0, 30.0):
            by_cross.setdefault(cross, []).append(row)
    styles = {
        -30.0: {"color": "#555555", "lw": 1.0, "ls": ":", "zorder": 4},
        0.0: {"color": "black", "lw": 1.8, "ls": "-", "zorder": 5},
        30.0: {"color": "black", "lw": 1.0, "ls": "--", "zorder": 4},
    }
    for cross, style in styles.items():
        ordered = sorted(by_cross[cross], key=lambda row: int(row["alongIndex"]))
        axis.plot(
            [float(row["longitude"]) for row in ordered],
            [float(row["latitude"]) for row in ordered],
            **style,
        )


def draw_context(
    axis: plt.Axes,
    objects: list[dict[str, str]],
    model_summary: dict,
) -> None:
    axis.scatter(
        [float(row["longitude_deg"]) for row in objects],
        [float(row["latitude_deg"]) for row in objects],
        s=18,
        color="#4e79a7",
        edgecolors="black",
        linewidths=0.25,
        alpha=0.90,
        zorder=7,
    )
    shortlist = [row for row in objects if "morphology_shortlist5" in row["object_set"]]
    axis.scatter(
        [float(row["longitude_deg"]) for row in shortlist],
        [float(row["latitude_deg"]) for row in shortlist],
        s=48,
        facecolors="none",
        edgecolors="#00a6a6",
        linewidths=1.0,
        zorder=8,
    )
    axis.scatter(
        [92.8], [-35.6], marker="P", s=62, color="#8a2be2",
        edgecolor="white", linewidth=0.55, zorder=8,
    )
    axis.scatter(
        [92.6, 91.8], [-34.7, -35.3], marker="^", s=42,
        facecolors="white", edgecolors="#8a2be2", linewidths=1.1, zorder=8,
    )
    mode = model_summary["mode"]
    axis.scatter(
        [mode["longitude"]], [mode["latitude"]], marker="*", s=105,
        color="black", edgecolor="white", linewidth=0.55, zorder=9,
    )
    axis.annotate(
        "mode", (mode["longitude"], mode["latitude"]), xytext=(7, -10),
        textcoords="offset points", fontsize=8.0, fontweight="bold", zorder=10,
    )


def panel_stats(model_summary: dict) -> str:
    return (
        f"90% HDR: {model_summary['hpd']['0.9']['areaKm2']:,.0f} km²\n"
        f"mass within ±30 NM: {100 * model_summary['massWithin30NmOfArc']:.1f}%\n"
        f"east | west: {100 * model_summary['massEastOfArc']:.1f}% | "
        f"{100 * model_summary['massWestOfArc']:.1f}%"
    )


def figure_handles() -> list:
    return [
        Line2D([], [], color="black", lw=1.8, label="seventh BTO arc"),
        Line2D([], [], color="#555555", lw=1.0, ls=":", label="30 NM inward/west boundary"),
        Line2D([], [], color="black", lw=1.0, ls="--", label="30 NM outward/east boundary"),
        Patch(facecolor=HPD_STYLES[0.50]["color"], alpha=HPD_STYLES[0.50]["alpha"], label="50% HPD"),
        Patch(facecolor=HPD_STYLES[0.90]["color"], alpha=HPD_STYLES[0.90]["alpha"], label="90% HPD"),
        Patch(facecolor=HPD_STYLES[0.95]["color"], alpha=HPD_STYLES[0.95]["alpha"], label="95% HPD"),
        Line2D([], [], marker="*", color="black", markeredgecolor="white", linestyle="none", markersize=9, label="conditional-density mode"),
        Line2D([], [], marker="o", color="#4e79a7", markeredgecolor="black", linestyle="none", markersize=4.5, label="GA rating-5 object"),
        Line2D([], [], marker="o", color="#00a6a6", markerfacecolor="none", linestyle="none", markersize=7, label="five-object morphology subset"),
        Line2D([], [], marker="P", color="#8a2be2", markeredgecolor="white", linestyle="none", markersize=6.5, label="CSIRO primary source"),
        Line2D([], [], marker="^", color="#8a2be2", markerfacecolor="white", linestyle="none", markersize=6, label="CSIRO alternative source"),
    ]


def main() -> None:
    summary = json.loads((OUTPUTS / "summary.json").read_text(encoding="utf-8"))
    density_rows = read_csv(OUTPUTS / "conditional-impact-density.csv")
    model_average_path = OUTPUTS / "model-averaged-impact-density.csv"
    if model_average_path.exists():
        density_rows.extend(read_csv(model_average_path))
    objects = read_csv(DATA / "pleiades-rating5-objects.csv")
    model_ids = [model["id"] for model in summary["current_models"]]
    if "model_average" in summary:
        model_ids.append(summary["model_average"]["id"])
    if not model_ids:
        raise ValueError("no current family is present in summary.json")

    matplotlib.rcParams.update({
        "axes.unicode_minus": True,
        "font.family": "DejaVu Sans",
        "pdf.fonttype": 42,
        "svg.fonttype": "none",
        "svg.hashsalt": "pleiades-forward-impact-density",
    })
    figure, axes = plt.subplots(
        1, len(model_ids), figsize=(20.0, 8.4), sharex=True, sharey=True, squeeze=False,
    )
    axes = axes[0]
    for axis, model_id in zip(axes, model_ids):
        rows = [row for row in density_rows if row["current_model"] == model_id]
        longitude, latitude, density = model_grid(rows)
        model_summary = (summary["model_average"]["primary"]
                         if model_id == summary.get("model_average", {}).get("id")
                         else summary["summaries"][model_id]["primary"])
        draw_hpd_layers(axis, longitude, latitude, density, model_summary)
        draw_arc_lines(axis, rows)
        draw_context(axis, objects, model_summary)
        mode = model_summary["mode"]
        axis.set_title(
            f"{MODEL_TITLES.get(model_id, model_id)}\n"
            f"mode {abs(mode['latitude']):.3f}°S, {mode['longitude']:.3f}°E",
            fontsize=11,
        )
        axis.text(
            0.025, 0.975, panel_stats(model_summary), transform=axis.transAxes,
            va="top", ha="left", fontsize=8.0, linespacing=1.30,
            bbox={
                "boxstyle": "round,pad=0.4", "facecolor": "white",
                "edgecolor": "#aaaaaa", "alpha": 0.93,
            },
            zorder=10,
        )
        axis.set_xlim(MAP_EXTENT[0], MAP_EXTENT[1])
        axis.set_ylim(MAP_EXTENT[2], MAP_EXTENT[3])
        axis.set_aspect(1.0 / math.cos(math.radians(-35.0)))
        axis.xaxis.set_major_locator(MultipleLocator(0.5))
        axis.yaxis.set_major_locator(MultipleLocator(0.5))
        axis.tick_params(labelsize=8.5)
        axis.set_xlabel("Longitude (°E)", fontsize=9.5)
        axis.grid(alpha=0.18, zorder=-1)
    axes[0].set_ylabel("Latitude (°)", fontsize=9.5)

    figure.suptitle(
        "Pléiades-conditioned forward-transport source compatibility\n"
        "BRAN2016, OSCAR v2 Final, and GLORYS12–WAVERYS alternatives with a declared equal-prior mixture; conditional on an equal-weight rating-5 object-location mixture",
        fontsize=15,
        y=0.985,
    )
    figure.legend(
        handles=figure_handles(), loc="lower center", bbox_to_anchor=(0.5, 0.064),
        ncol=6, fontsize=7.5, frameon=True, framealpha=0.96,
        columnspacing=1.25, handlelength=2.0,
    )
    comparisons = summary["current_family_comparisons"]
    television = [entry["total_variation"] for entry in comparisons]
    mode_separations = [entry["mode_separation_km"] for entry in comparisons]
    note = (
        "Shading and contours are normalized two-dimensional source-cell density; no transverse display width was added. "
        f"The three transport families differ materially (pairwise total variation {min(television):.3f}–{max(television):.3f}; "
        f"mode separation {min(mode_separations):.1f}–{max(mode_separations):.1f} km). The final panel is their declared equal-prior mixture; "
        "the families are never multiplied as independent evidence and their spread is not treated as sampling error. "
        "This is transport compatibility, not an object-attribution result or a calibrated crash posterior."
    )
    figure.text(
        0.5, 0.012, textwrap.fill(note, width=225), ha="center", va="bottom",
        fontsize=7.5, color="#444444",
    )
    figure.subplots_adjust(
        left=0.055, right=0.985, bottom=0.165, top=0.845, wspace=0.13,
    )

    title = "Pléiades forward-transport conditional source compatibility"
    generated = datetime.fromisoformat(summary["generated_utc"].replace("Z", "+00:00"))
    figure.savefig(
        STEM.with_suffix(".png"), dpi=200,
        metadata={"Title": title, "Description": note},
    )
    figure.savefig(
        STEM.with_suffix(".svg"),
        metadata={"Title": title, "Description": note, "Date": summary["generated_utc"]},
    )
    figure.savefig(
        STEM.with_suffix(".pdf"),
        metadata={
            "Title": title, "Subject": note, "Author": "MH370 source recreation",
            "Creator": f"Matplotlib {matplotlib.__version__}",
            "CreationDate": generated, "ModDate": generated,
        },
    )
    plt.close(figure)


if __name__ == "__main__":
    main()
