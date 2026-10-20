#!/usr/bin/env python3
"""Plot current two-station candidate context from Kadri Figure 9 vectors."""

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


HERE = Path(__file__).resolve().parents[1]
DATA = HERE / "data"
OUTPUT = HERE / "outputs"
METADATA_PATH = DATA / "kadri-figure-extraction" / "metadata.json"
CONFIG_PATH = DATA / "candidate-context-config.json"
FILTER_SUMMARY_PATH = OUTPUT / "summary.json"
PDF_METADATA = {"CreationDate": None, "ModDate": None}


def parse_utc(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_trace(record: dict) -> tuple[np.ndarray, np.ndarray]:
    path = METADATA_PATH.parent / record["file"]
    with path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    seconds = np.asarray([float(row["plotted_time_s"]) for row in rows])
    pressure = np.asarray([float(row["pressure_pa"]) for row in rows])
    order = np.argsort(seconds)
    seconds, unique_index = np.unique(seconds[order], return_index=True)
    pressure = pressure[order][unique_index]
    epoch = parse_utc(record["start_utc"]).timestamp() + seconds
    time = np.asarray([datetime.fromtimestamp(value, timezone.utc) for value in epoch])
    return time, pressure


def main() -> None:
    configuration = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    metadata = json.loads(METADATA_PATH.read_text(encoding="utf-8"))
    filter_summary = json.loads(FILTER_SUMMARY_PATH.read_text(encoding="utf-8"))
    records = {row["panel"]: row for row in metadata["figure9_vector_traces"]}
    traces = {panel: load_trace(records[panel]) for panel in ("b", "c", "d")}

    h01_boundary = parse_utc(configuration["h01w"]["screened_boundary_feature_utc"])
    h01_source = parse_utc(configuration["h01w"]["figure9_rectangle1_time_utc_approximate"])
    h01_table = parse_utc(configuration["h01w"]["table1_major_candidate_time_utc"])
    h01_medians = [parse_utc(value) for value in configuration["h01w"]["high_rate_reference_median_arrivals_utc"]]
    h08_event = parse_utc(configuration["h08s"]["screened_feature_utc"])
    h08_medians = [parse_utc(value) for value in configuration["h08s"]["high_rate_reference_median_arrivals_utc"]]
    period_s = float(filter_summary["phase_fit"]["leave_target_out_fitted_period_s"])
    predicted_target = parse_utc(filter_summary["phase_fit"]["target_predicted_shot_utc"])
    predicted_shots = [
        datetime.fromtimestamp(predicted_target.timestamp() + period_s * index, timezone.utc)
        for index in range(-19, 43)
    ]

    fig, axes = plt.subplots(2, 2, figsize=(16.0, 9.5))
    colours = {
        "trace": "#4C4C4C",
        "screen": "#A61B29",
        "source": "#C86516",
        "table": "#A61B29",
        "model": "#6B4C9A",
        "airgun": "#1769AA",
    }

    axis = axes[0, 0]
    time_c, pressure_c = traces["c"]
    axis.plot(time_c, pressure_c, color=colours["trace"], linewidth=0.45)
    axis.axvline(h01_source, color=colours["source"], linewidth=1.5)
    axis.axvline(h01_table, color=colours["table"], linewidth=1.8)
    axis.axvline(h01_boundary, color=colours["screen"], linewidth=1.2)
    axis.annotate(
        "rectangle 1: about 00:52, 57°\n(p. 9 prose conflates this with 306°)",
        (h01_source, 0.95), xytext=(8, -20), textcoords="offset points",
        color=colours["source"], fontsize=8.5, va="top",
    )
    axis.annotate(
        "Table 1: 00:54:30, 306.18°",
        (h01_table, -0.95), xytext=(-8, 20), textcoords="offset points",
        color=colours["table"], fontsize=8.5, va="bottom", ha="right",
    )
    axis.set_ylim(-1.05, 1.05)
    axis.set_ylabel("Plotted pressure (Pa)")
    axis.set_title("A. H01W: Figure 9 signals and independently screened times")
    axis.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M", tz=timezone.utc))
    axis.grid(alpha=0.18)

    axis = axes[0, 1]
    for panel in ("b", "c"):
        time, pressure = traces[panel]
        axis.plot(time, pressure, color=colours["trace"], linewidth=0.75)
    boundary = parse_utc(records["c"]["start_utc"])
    axis.axvline(boundary, color="#111111", linewidth=1.0, linestyle=":")
    axis.axvline(h01_boundary, color=colours["screen"], linewidth=1.7)
    for arrival in h01_medians:
        axis.axvline(arrival, color=colours["model"], linewidth=1.1, linestyle="--")
    axis.set_xlim(
        datetime.fromtimestamp(boundary.timestamp() - 30.0, timezone.utc),
        datetime.fromtimestamp(boundary.timestamp() + 30.0, timezone.utc),
    )
    axis.set_ylim(-1.05, 1.05)
    axis.set_ylabel("Plotted pressure (Pa)")
    axis.set_title("B. H01W: the 00:47:01.7 screen is panel-edge affected")
    axis.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M:%S", tz=timezone.utc))
    axis.grid(alpha=0.18)
    axis.text(
        0.02, 0.04,
        "The selected time is 1.7 s into a separately drawn panel;\nits score is not robust evidence of a transient.",
        transform=axis.transAxes, fontsize=8.7, color=colours["screen"],
    )

    axis = axes[1, 0]
    time_d, pressure_d = traces["d"]
    axis.plot(time_d, pressure_d, color=colours["trace"], linewidth=0.40)
    for shot in predicted_shots:
        axis.axvline(shot, color=colours["airgun"], linewidth=0.35, alpha=0.40)
    axis.axvline(h08_event, color=colours["screen"], linewidth=1.8)
    for arrival in h08_medians:
        axis.axvline(arrival, color=colours["model"], linewidth=1.1, linestyle="--")
    axis.set_ylim(-2.1, 2.1)
    axis.set_ylabel("Plotted pressure (Pa)")
    axis.set_title("C. H08S: 01:03:13.15 lies in the periodic airgun train")
    axis.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M", tz=timezone.utc))
    axis.grid(alpha=0.18)

    axis = axes[1, 1]
    axis.plot(time_d, pressure_d, color=colours["trace"], linewidth=0.75)
    for shot in predicted_shots:
        axis.axvline(shot, color=colours["airgun"], linewidth=0.8, alpha=0.60)
    axis.axvline(h08_event, color=colours["screen"], linewidth=1.8)
    for arrival in h08_medians:
        axis.axvline(arrival, color=colours["model"], linewidth=1.1, linestyle="--")
    axis.set_xlim(
        datetime.fromtimestamp(h08_event.timestamp() - 30.0, timezone.utc),
        datetime.fromtimestamp(h08_event.timestamp() + 30.0, timezone.utc),
    )
    axis.set_ylim(-2.1, 2.1)
    axis.set_ylabel("Plotted pressure (Pa)")
    axis.set_title("D. H08S detail: timing compatibility is not source identity")
    axis.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M:%S", tz=timezone.utc))
    axis.grid(alpha=0.18)

    handles = [
        Line2D([0], [0], color=colours["trace"], label="Kadri Figure 9 vector trace"),
        Line2D([0], [0], color=colours["screen"], label="independently screened time"),
        Line2D([0], [0], color=colours["source"], label="Figure 9 rectangle 1 time (approximate)"),
        Line2D([0], [0], color=colours["table"], label="Table 1 major-candidate time"),
        Line2D([0], [0], color=colours["model"], linestyle="--", label="model-conditioned median arrival"),
        Line2D([0], [0], color=colours["airgun"], label="leave-target-out periodic prediction"),
    ]
    fig.legend(
        handles=handles, loc="lower center", bbox_to_anchor=(0.5, 0.048),
        ncol=3, frameon=False, fontsize=8.1,
    )
    fig.suptitle("Current hydroacoustic candidate context at H01W and H08S", fontsize=15.8)
    fig.text(
        0.5, 0.012,
        "The plotted traces have already been filtered and rendered for publication. They cannot establish event identity, bearing, array coherence or detection probability.",
        ha="center", fontsize=8.8,
    )
    fig.tight_layout(rect=[0.0, 0.125, 1.0, 0.95])
    OUTPUT.mkdir(parents=True, exist_ok=True)
    paths = []
    for suffix in ("png", "pdf"):
        path = OUTPUT / f"two-station-candidate-context.{suffix}"
        fig.savefig(path, dpi=280 if suffix == "png" else None, metadata=PDF_METADATA if suffix == "pdf" else None)
        paths.append(path)
    plt.close(fig)

    manifest = {
        "status": "REPRODUCIBLE_OUTPUT_HASHES",
        "inputs": {
            str(CONFIG_PATH.relative_to(HERE)): sha256(CONFIG_PATH),
            str(METADATA_PATH.relative_to(HERE)): sha256(METADATA_PATH),
            str(FILTER_SUMMARY_PATH.relative_to(HERE)): sha256(FILTER_SUMMARY_PATH),
        },
        "code": {str(Path(__file__).relative_to(HERE)): sha256(Path(__file__))},
        "outputs": {path.name: sha256(path) for path in paths},
    }
    (OUTPUT / "candidate-context-manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
