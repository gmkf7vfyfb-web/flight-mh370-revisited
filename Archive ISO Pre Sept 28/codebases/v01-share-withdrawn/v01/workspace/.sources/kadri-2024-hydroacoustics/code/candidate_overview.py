#!/usr/bin/env python3
"""Consolidate Kadri source signals, screened times, seventh arc and spatial PDF."""

from __future__ import annotations

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
from matplotlib.patches import Patch, Rectangle

import event_pair_analysis as base


HERE = Path(__file__).resolve().parents[1]
DATA = HERE / "data"
OUTPUT = HERE / "outputs"
CONFIG_PATH = DATA / "event-pair-analysis-config.json"
PAIR_PATH = OUTPUT / "conditional-event-pair-overlaps.csv"
PDF_METADATA = {"CreationDate": None, "ModDate": None}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def write_csv(path: Path, rows: list[dict]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def destination_sphere(
    latitude_deg: float,
    longitude_deg: float,
    bearing_deg: float,
    distance_km: np.ndarray,
    radius_km: float,
) -> tuple[np.ndarray, np.ndarray]:
    latitude = np.radians(latitude_deg)
    longitude = np.radians(longitude_deg)
    bearing = np.radians(bearing_deg)
    angular = np.asarray(distance_km, dtype=float) / radius_km
    result_latitude = np.arcsin(
        np.sin(latitude) * np.cos(angular)
        + np.cos(latitude) * np.sin(angular) * np.cos(bearing)
    )
    result_longitude = longitude + np.arctan2(
        np.sin(bearing) * np.sin(angular) * np.cos(latitude),
        np.cos(angular) - np.sin(latitude) * np.sin(result_latitude),
    )
    return np.degrees(result_latitude), np.degrees(result_longitude) % 360.0


def source_events(configuration: dict) -> list[dict]:
    events = []
    for record in configuration["source_reported_figure9_signals"]:
        time = base.parse_utc(record["arrival_utc"])
        events.append(
            {
                "event_id": record["id"],
                "time_utc": time.strftime("%H:%M:%S"),
                "epoch_s": time.timestamp(),
                "bearing_deg": float(record["bearing_deg"]),
                "source_status": record["status"],
            }
        )
    with (DATA / "kadri-table1-transients.csv").open(newline="", encoding="utf-8") as handle:
        table = {row["event_id"]: row for row in csv.DictReader(handle)}
    for event_id in configuration["selected_table_events"]:
        row = table[event_id]
        time = base.parse_utc(f"2014-03-08T{row['time_utc']}Z")
        events.append(
            {
                **row,
                "epoch_s": time.timestamp(),
                "bearing_deg": float(row["bearing_deg"]),
            }
        )
    return events


def draw_pdf(axis: plt.Axes, spatial: dict, full_extent: bool) -> None:
    log_density = np.log10(np.maximum(spatial["density"], 1e-16))
    axis.pcolormesh(
        spatial["mesh_lon"],
        spatial["mesh_lat"],
        log_density,
        shading="auto",
        cmap="Greys",
        alpha=0.76,
        rasterized=True,
    )
    thresholds = [
        base.hpd_threshold(spatial["probability"], spatial["area"], probability)
        for probability in (0.99, 0.90, 0.50)
    ]
    contours = axis.contour(
        spatial["mesh_lon"],
        spatial["mesh_lat"],
        spatial["density"],
        levels=thresholds,
        colors=["#777777", "#444444", "#111111"],
        linewidths=[0.75, 1.0, 1.45],
    )
    axis.clabel(
        contours,
        fmt={thresholds[0]: "99%", thresholds[1]: "90%", thresholds[2]: "50%"},
        fontsize=7,
    )
    arc = spatial["arc"]
    southern = arc[:, 1] <= 5.0
    axis.plot(arc[southern, 0], arc[southern, 1], color="#009E73", linewidth=1.45)
    if full_extent:
        axis.set_xlim(60.0, 120.0)
        axis.set_ylim(-50.0, 5.0)
    else:
        axis.set_xlim(float(spatial["longitude"][0]), float(spatial["longitude"][-1]))
        axis.set_ylim(float(spatial["latitude"][0]), float(spatial["latitude"][-1]))
    axis.set_xlabel("Longitude (°E)")
    axis.set_ylabel("Latitude (°)")
    axis.grid(alpha=0.13)


def main() -> None:
    configuration = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    traces = base.load_traces(configuration)
    events = source_events(configuration)
    audit_rows = base.audit_table_events(configuration, traces, events)
    spatial = base.load_spatial(configuration)
    with PAIR_PATH.open(newline="", encoding="utf-8") as handle:
        pairing = list(csv.DictReader(handle))
    screen_pairs = [
        row for row in pairing
        if row["pair_family"] == "independently_screened_times_without_bearing"
    ]

    audit_path = OUTPUT / "source-and-table-event-trace-audit.csv"
    write_csv(audit_path, audit_rows)

    colours = {
        "figure9_rectangle_1": "#E69F00",
        "figure9_rectangle_2": "#D55E00",
        "event_004958": "#0072B2",
        "event_005331": "#6B4C9A",
    }
    labels = {
        "figure9_rectangle_1": "Figure 9 rectangle 1: about 00:52, 57°",
        "figure9_rectangle_2": "preferred rectangle 2: 00:54:30, 306.18°",
        "event_004958": "Table 1: 00:49:58, 260.41°",
        "event_005331": "Table 1: 00:53:31, 257.58°",
    }
    pair_colours = ["#CC6677", "#DDCC77", "#44AA99", "#332288"]
    pair_linestyles = ["-", "--", "-", "--"]

    figure = plt.figure(figsize=(17.0, 11.0))
    grid = figure.add_gridspec(2, 2, height_ratios=[1.05, 0.72], hspace=0.30, wspace=0.18)
    overview = figure.add_subplot(grid[0, 0])
    zoom = figure.add_subplot(grid[0, 1])
    trace_axis = figure.add_subplot(grid[1, :])

    draw_pdf(overview, spatial, full_extent=True)
    station = configuration["stations"]["H01W"]
    overview.scatter(
        station["longitude_deg_e"],
        station["latitude_deg"],
        marker="^",
        s=75,
        color="#111111",
        zorder=10,
    )
    overview.annotate(
        "H01W Cape Leeuwin",
        (station["longitude_deg_e"], station["latitude_deg"]),
        xytext=(-6, -14),
        textcoords="offset points",
        ha="right",
        fontsize=8.5,
    )
    distances = np.linspace(0.0, 6500.0, 900)
    for event in events:
        latitude, longitude = destination_sphere(
            station["latitude_deg"],
            station["longitude_deg_e"],
            event["bearing_deg"],
            distances,
            float(configuration["earth_radius_km"]),
        )
        overview.plot(
            longitude,
            latitude,
            color=colours[event["event_id"]],
            linewidth=1.7,
            label=labels[event["event_id"]],
        )
    overview.add_patch(
        Rectangle(
            (float(spatial["longitude"][0]), float(spatial["latitude"][0])),
            float(spatial["longitude"][-1] - spatial["longitude"][0]),
            float(spatial["latitude"][-1] - spatial["latitude"][0]),
            fill=False,
            edgecolor="#111111",
            linewidth=0.8,
            linestyle=":",
        )
    )
    overview.set_title(
        "A. H01W source bearings against the seventh arc and integrated spatial PDF\n"
        "The preferred 306.18° line meets the arc well north of the integrated high-density area"
    )

    draw_pdf(zoom, spatial, full_extent=False)
    minimum_difference = float(np.min(spatial["range_difference"]))
    maximum_difference = float(np.max(spatial["range_difference"]))
    for row, colour, linestyle in zip(screen_pairs, pair_colours, pair_linestyles):
        lower = float(row["range_difference_low_km"])
        upper = float(row["range_difference_high_km"])
        if upper >= minimum_difference and lower <= maximum_difference:
            levels = [
                value for value in (lower, upper)
                if minimum_difference <= value <= maximum_difference
            ]
            if levels:
                zoom.contour(
                    spatial["mesh_lon"],
                    spatial["mesh_lat"],
                    spatial["range_difference"],
                    levels=levels,
                    colors=[colour],
                    linewidths=1.25,
                    linestyles=[linestyle],
                )
        toa_mass = 100.0 * float(row["independent_pdf_mass_within_range_band"])
        joint_mass = 100.0 * float(row["independent_pdf_mass_within_range_and_impact_time"])
        zoom.plot(
            [],
            [],
            color=colour,
            linestyle=linestyle,
            linewidth=1.6,
            label=(
                f"{row['h01w_arrival_utc'][11:19]}→{row['h08s_screened_arrival_utc'][11:19]}: "
                f"TOA {toa_mass:.2f}%, +source time {joint_mass:.2f}%"
            ),
        )
    for event in events:
        if event["event_id"] not in ("event_004958", "event_005331"):
            continue
        difference = np.abs(
            base.angular_difference_deg(spatial["bearing_h01"], event["bearing_deg"])
        )
        zoom.contour(
            spatial["mesh_lon"],
            spatial["mesh_lat"],
            difference,
            levels=[float(configuration["bearing_half_widths_deg"]["formal"])],
            colors=[colours[event["event_id"]]],
            linewidths=1.8,
        )
    zoom.legend(loc="lower left", fontsize=7.3, framealpha=0.90)
    zoom.set_title(
        "B. Independently screened H01W–H08S arrival-difference bands\n"
        "Percentages are integrated-PDF compatibility masses, not event probabilities"
    )

    trace = traces["c"]
    times = np.asarray(
        [datetime.fromtimestamp(value, timezone.utc) for value in trace.epoch_s]
    )
    lower_time = base.parse_utc("2014-03-08T00:49:30Z")
    upper_time = base.parse_utc("2014-03-08T00:55:10Z")
    visible = (
        (trace.epoch_s >= lower_time.timestamp())
        & (trace.epoch_s <= upper_time.timestamp())
    )
    trace_axis.plot(times[visible], trace.pressure_pa[visible], color="#B8B8B8", linewidth=0.55, alpha=0.82)
    score_axis = trace_axis.twinx()
    score_axis.plot(times[visible], trace.score[visible], color="#3F145D", linewidth=1.55, alpha=0.98)
    score_axis.axhline(trace.threshold, color="#A61B29", linestyle="--", linewidth=1.15)
    for event in events:
        event_time = datetime.fromtimestamp(event["epoch_s"], timezone.utc)
        if lower_time <= event_time <= upper_time:
            trace_axis.axvline(
                event_time,
                color=colours[event["event_id"]],
                linewidth=1.6,
                label=labels[event["event_id"]],
            )
    screened = base.parse_utc("2014-03-08T00:52:04.350Z")
    trace_axis.axvline(screened, color="#111111", linewidth=1.0, linestyle=":")
    trace_axis.annotate(
        "independent q99 screen 00:52:04.35",
        (screened, 0.94),
        xytext=(5, -4),
        textcoords="offset points",
        transform=trace_axis.get_xaxis_transform(),
        fontsize=8.0,
        va="top",
    )
    preferred_score = next(
        row for row in audit_rows
        if row["event_id"] == "figure9_rectangle_2"
        and row["search_half_window_s"] == "2.0"
    )
    trace_axis.text(
        0.985,
        0.05,
        "00:54:30 local score "
        f"{float(preferred_score['local_max_score']):.2f}; panel q99 {trace.threshold:.2f}\n"
        "The publication trace retains timing but cannot recover the 306.18° bearing.",
        transform=trace_axis.transAxes,
        ha="right",
        va="bottom",
        fontsize=8.4,
        bbox={"facecolor": "white", "alpha": 0.88, "edgecolor": "none"},
    )
    trace_axis.set_xlim(lower_time, upper_time)
    trace_axis.set_ylabel("Plotted pressure (Pa)")
    score_axis.set_ylabel("Robust local-energy score", color="#3F145D", weight="bold")
    trace_axis.set_xlabel("UTC on 8 March 2014")
    trace_axis.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M:%S", tz=timezone.utc))
    trace_axis.grid(alpha=0.16)
    trace_axis.legend(loc="upper left", fontsize=8.0)
    trace_axis.set_title(
        "C. Figure 9c: light-grey pressure and high-contrast local-energy score at all noted source times"
    )

    handles = [
        Line2D([0], [0], color="#009E73", linewidth=1.5, label="seventh BTO arc"),
        Line2D([0], [0], color="#111111", linewidth=1.5, label="integrated PDF 50/90/99% contours"),
        Patch(facecolor="#777777", alpha=0.35, label="integrated PDF density"),
    ]
    figure.legend(handles=handles, loc="lower center", bbox_to_anchor=(0.5, 0.040), ncol=3, frameon=False)
    figure.suptitle(
        "Kadri source-signal timing, candidate bearings and two-station timing controls",
        fontsize=15.0,
    )
    figure.text(
        0.5,
        0.010,
        "Figure 9 rectangle 1 (~00:52/57°) and preferred rectangle 2 (00:54:30/306.18°) are distinct; the p. 9 prose appears to conflate them. Arrival-difference bands cancel impact time; the second percentage also enforces impact during 00:19:37–00:49:37.",
        ha="center",
        fontsize=8.4,
    )
    figure.tight_layout(rect=[0.0, 0.075, 1.0, 0.95])

    paths = [audit_path]
    for suffix in ("png", "pdf"):
        path = OUTPUT / f"candidate-bearing-and-timing-overview.{suffix}"
        figure.savefig(
            path,
            dpi=280 if suffix == "png" else None,
            metadata=PDF_METADATA if suffix == "pdf" else None,
        )
        paths.append(path)
    plt.close(figure)

    manifest = {
        "status": "SOURCE_SIGNAL_AND_CONDITIONAL_GEOMETRY_OVERVIEW_NOT_ASSOCIATION_POSTERIOR",
        "inputs": {
            str(CONFIG_PATH.relative_to(HERE)): sha256(CONFIG_PATH),
            str(PAIR_PATH.relative_to(HERE)): sha256(PAIR_PATH),
            "data/posterior_grids.npz": sha256(DATA / "posterior_grids.npz"),
            "data/seventh_arc_fl400.geojson": sha256(DATA / "seventh_arc_fl400.geojson"),
            "data/kadri-figure-extraction/metadata.json": sha256(DATA / "kadri-figure-extraction" / "metadata.json"),
        },
        "code": {
            str(Path(__file__).relative_to(HERE)): sha256(Path(__file__)),
            "code/event_pair_analysis.py": sha256(Path(base.__file__)),
        },
        "outputs": {path.name: sha256(path) for path in paths},
        "interpretive_limits": [
            "publication-vector pressure cannot reproduce Kadri's triad bearing calculation",
            "TOA-difference masses are spatial compatibility fractions, not association probabilities",
            "the 30-minute impact-time control is an explicit alternative, not part of the baseline percentages",
        ],
    }
    (OUTPUT / "candidate-overview-manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
