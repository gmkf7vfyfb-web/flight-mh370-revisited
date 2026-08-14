#!/usr/bin/env python3
"""Render the MH370 searched-area audit map from the generated GeoJSON package."""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Polygon as MplPolygon
import numpy as np


ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "outputs" / "mh370_search_evidence"
OUT = DATA_DIR / "mh370_search_evidence_map.png"

data = json.loads((DATA_DIR / "map_data.json").read_text())


def rings(geometry):
    kind = geometry["type"]
    coords = geometry["coordinates"]
    if kind == "Polygon":
        yield coords
    elif kind == "MultiPolygon":
        yield from coords


def plot_polygon(ax, geometry, *, facecolor, edgecolor, alpha=1, linewidth=1, hatch=None, zorder=1):
    for polygon in rings(geometry):
        outer = np.asarray(polygon[0])
        ax.add_patch(
            MplPolygon(
                outer,
                closed=True,
                facecolor=facecolor,
                edgecolor=edgecolor,
                alpha=alpha,
                linewidth=linewidth,
                hatch=hatch,
                zorder=zorder,
            )
        )
        for hole in polygon[1:]:
            ax.add_patch(
                MplPolygon(
                    np.asarray(hole),
                    closed=True,
                    facecolor=ax.get_facecolor(),
                    edgecolor="none",
                    zorder=zorder + 0.1,
                )
            )


def line_coords(geometry):
    if geometry["type"] == "LineString":
        yield geometry["coordinates"]
    elif geometry["type"] == "MultiLineString":
        yield from geometry["coordinates"]


by_id = {f["properties"].get("id"): f for f in data["footprints"]["features"]}

fig, axes = plt.subplots(1, 2, figsize=(16, 10), constrained_layout=False)
fig.subplots_adjust(left=0.055, right=0.985, top=0.90, bottom=0.23, wspace=0.14)
fig.suptitle("MH370 search evidence: actual high-resolution coverage versus likely remaining area", fontsize=17, weight="bold")

views = [
    (axes[0], (83, 116), (-42, -18), "Southern Indian Ocean overview"),
    (axes[1], (90.5, 96.5), (-37.0, -32.2), "Renewed-search detail (33–36°S)"),
]

for ax, xlim, ylim, title in views:
    ax.set_facecolor("#eef6fb")
    for feature in data["land"]["features"]:
        plot_polygon(ax, feature["geometry"], facecolor="#ded8c8", edgecolor="#8b836e", linewidth=0.6, zorder=0)

    if xlim[1] - xlim[0] > 10:
        plot_polygon(
            ax,
            by_id["initial_100nm_wide_area_context"]["geometry"],
            facecolor="#d6d3e8",
            edgecolor="#7d73a3",
            alpha=0.22,
            linewidth=0.8,
            zorder=0.3,
        )

    bins = data["posterior_bins"]
    for item in bins:
        if item["density"] < 0.04:
            continue
        ax.add_patch(
            MplPolygon(
                [
                    [item["lon"], item["lat"]],
                    [item["lon"] + 0.25, item["lat"]],
                    [item["lon"] + 0.25, item["lat"] + 0.25],
                    [item["lon"], item["lat"] + 0.25],
                ],
                closed=True,
                facecolor="#bf3f45",
                edgecolor="none",
                alpha=0.05 + 0.38 * item["density"],
                zorder=0.8,
            )
        )

    plot_polygon(
        ax,
        by_id["atsb_phase2_2014_2017"]["geometry"],
        facecolor="#4c78a8",
        edgecolor="#2e5c8a",
        alpha=0.42,
        linewidth=0.8,
        zorder=1,
    )
    plot_polygon(
        ax,
        by_id["oi2018_total_outline_approx"]["geometry"],
        facecolor="#f2a541",
        edgecolor="#b96c08",
        alpha=0.30,
        linewidth=1.0,
        hatch="//",
        zorder=1.2,
    )
    plot_polygon(
        ax,
        by_id["oi2024_proposed_outboard_southeast"]["geometry"],
        facecolor="#4aa56d",
        edgecolor="#247346",
        alpha=0.32,
        linewidth=1.4,
        zorder=2,
    )
    plot_polygon(
        ax,
        by_id["oi2024_proposed_inboard_northwest"]["geometry"],
        facecolor="#d95a5a",
        edgecolor="#8f1d1d",
        alpha=0.18,
        linewidth=2.0,
        hatch="xx",
        zorder=2.1,
    )
    for line in line_coords(by_id["seventh_arc_fl400"]["geometry"]):
        line = np.asarray(line)
        ax.plot(line[:, 0], line[:, 1], color="#252525", linewidth=1.3, linestyle="--", zorder=3)

    if xlim[1] - xlim[0] < 10:
        for feature in data["tracks"]["features"]:
            line = np.asarray(feature["geometry"]["coordinates"])
            if len(line):
                ax.plot(line[:, 0], line[:, 1], color="#7a4da3", linewidth=0.9, alpha=0.75, zorder=3.2)

    ax.set_xlim(*xlim)
    ax.set_ylim(*ylim)
    ax.set_title(title, fontsize=13, weight="bold")
    ax.set_xlabel("Longitude east")
    ax.set_ylabel("Latitude")
    ax.grid(color="#83919a", linewidth=0.45, alpha=0.45)
    mean_lat = sum(ylim) / 2
    ax.set_aspect(1 / np.cos(np.radians(mean_lat)))

axes[0].annotate("Western Australia", xy=(114, -26), xytext=(111.5, -24), fontsize=10, color="#5a5345")
axes[1].annotate("Likely residual concentration\n(not an official polygon)", xy=(92.7, -34.3), xytext=(94.5, -33.0),
                 arrowprops={"arrowstyle": "->", "color": "#8f1d1d"}, color="#8f1d1d", fontsize=10, ha="right")

legend = [
    Line2D([0], [0], color="#bf3f45", linewidth=8, alpha=0.35, label="Existing Stage-1 impact density (context)"),
    Line2D([0], [0], color="#4c78a8", linewidth=8, alpha=0.55, label="ATSB 2014–2017 official high-res footprint"),
    Line2D([0], [0], color="#f2a541", linewidth=8, alpha=0.5, label="OI2018 approximate total outline"),
    Line2D([0], [0], color="#4aa56d", linewidth=8, alpha=0.55, label="Renewed-search outboard band, likely substantially searched"),
    Line2D([0], [0], color="#d95a5a", linewidth=8, alpha=0.45, label="Renewed-search inboard band, likely residual concentration"),
    Line2D([0], [0], color="#252525", linewidth=1.5, linestyle="--", label="Official 7th arc at FL400"),
    Line2D([0], [0], color="#7d73a3", linewidth=8, alpha=0.25, label="Official ±100 NM planning context (not searched)"),
]
fig.legend(
    handles=legend,
    loc="lower center",
    bbox_to_anchor=(0.5, 0.055),
    ncol=3,
    frameon=False,
    fontsize=9.5,
    columnspacing=1.6,
    handlelength=3.2,
)
fig.text(
    0.5,
    0.022,
    "Official remaining area: 7,428.54 km². Exact Ocean Infinity AUV swaths and remaining polygon are not public; OI outlines/tracks are source-graded reconstructions.",
    ha="center",
    fontsize=10,
)

fig.savefig(OUT, dpi=180, bbox_inches="tight")
print(OUT)
