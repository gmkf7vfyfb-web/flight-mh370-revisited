#!/usr/bin/env python3
"""Build deterministic tables from current-trajectory replay JSON artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


def year(document: dict) -> int:
    match = re.search(r"(?:19|20)\d{2}", document["trajectory_file"])
    if match is None:
        raise ValueError(f"year absent from {document['trajectory_file']}")
    return int(match.group(0))


def row(document: dict, region: str, summary: dict) -> dict:
    return {
        "family": document["family"],
        "year": year(document),
        "horizon_days": document["horizon_days"],
        "region": region,
        "attempts": summary["cases"],
        "complete_fraction": summary["complete_fraction"],
        "median_current_terminal_hold_error_km": summary[
            "median_current_with_terminal_hold_error_km"
        ],
        "median_persistence_error_km": summary["median_persistence_error_km"],
        "median_prior_velocity_error_km": summary["median_prior_velocity_error_km"],
        "current_better_than_persistence_fraction": summary[
            "current_better_than_persistence_fraction"
        ],
        "current_better_than_prior_velocity_fraction": summary[
            "current_better_than_prior_velocity_fraction"
        ],
        "field_terminations_all_regions": document["field_terminated_segments"],
        "termination_reasons_all_regions": json.dumps(
            document["termination_reasons"], sort_keys=True, separators=(",", ":")
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output-prefix", type=Path, required=True)
    args = parser.parse_args()
    paths = sorted(args.input.glob("*.json"))
    if not paths:
        raise ValueError("no validation JSON files found")
    overall = []
    regional = []
    by_drogue_status = []
    for path in paths:
        document = json.loads(path.read_text(encoding="utf-8"))
        if document.get("schema") != "mh370-current-trajectory-replay-v5":
            continue
        overall.append(row(document, "all", document["all_attempts"]))
        for region, summary in document["by_longitude_region"].items():
            regional.append(row(document, region, summary))
        for status, summary in document["by_drogue_status"].items():
            item = row(document, "all", summary)
            item["drogue_status"] = status
            by_drogue_status.append(item)
    key = lambda item: (item["family"], item["year"], item["horizon_days"], item["region"])
    overall.sort(key=key)
    regional.sort(key=key)
    by_drogue_status.sort(
        key=lambda item: (
            item["family"],
            item["year"],
            item["horizon_days"],
            item["drogue_status"],
        )
    )
    if not overall:
        raise ValueError("no supported trajectory-replay schemas found")

    args.output_prefix.parent.mkdir(parents=True, exist_ok=True)
    columns = list(overall[0])
    for suffix, rows in (("overall.csv", overall), ("regions.csv", regional)):
        with args.output_prefix.with_name(
            args.output_prefix.name + "-" + suffix
        ).open("w", newline="", encoding="utf-8") as stream:
            writer = csv.DictWriter(stream, fieldnames=columns)
            writer.writeheader()
            writer.writerows(rows)
    if by_drogue_status:
        drogue_columns = [
            "family",
            "year",
            "horizon_days",
            "drogue_status",
            *[name for name in columns if name not in {"family", "year", "horizon_days", "region"}],
        ]
        with args.output_prefix.with_name(
            args.output_prefix.name + "-drogue-status.csv"
        ).open("w", newline="", encoding="utf-8") as stream:
            writer = csv.DictWriter(stream, fieldnames=drogue_columns, extrasaction="ignore")
            writer.writeheader()
            writer.writerows(by_drogue_status)

    lines = [
        "# Current-trajectory replay summary",
        "",
        "Every selected path is included. A terminated forecast holds its last valid position to the target epoch while termination remains separately counted.",
        "",
        "| Family | Year | Horizon | Attempts | Complete | Termination reasons | Median current / persistence / prior-velocity error (km) | Current better than persistence |",
        "| --- | ---: | ---: | ---: | ---: | --- | ---: | ---: |",
    ]
    for item in overall:
        velocity = item["median_prior_velocity_error_km"]
        velocity_text = "n/a" if velocity is None else f"{velocity:.1f}"
        reasons = json.loads(item["termination_reasons_all_regions"])
        reason_text = ", ".join(f"{name}={count}" for name, count in reasons.items())
        if not reason_text:
            reason_text = "none"
        lines.append(
            f"| {item['family']} | {item['year']} | {item['horizon_days']:g} d | "
            f"{item['attempts']} | {100 * item['complete_fraction']:.1f}% | "
            f"{reason_text} | "
            f"{item['median_current_terminal_hold_error_km']:.1f} / "
            f"{item['median_persistence_error_km']:.1f} / {velocity_text} | "
            f"{100 * item['current_better_than_persistence_fraction']:.1f}% |"
        )
    lines.extend(
        [
            "",
            "## Drogue-state separation",
            "",
            "Explicit surface Stokes drift is evaluated against undrogued segments separately from drogued segments; intervals spanning a recorded drogue-loss time remain a distinct transition group.",
            "",
            "| Family | Year | Horizon | Drogue status | Attempts | Complete | Median current / persistence error (km) | Current better than persistence |",
            "| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |",
        ]
    )
    for item in by_drogue_status:
        lines.append(
            f"| {item['family']} | {item['year']} | {item['horizon_days']:g} d | "
            f"{item['drogue_status']} | {item['attempts']} | "
            f"{100 * item['complete_fraction']:.1f}% | "
            f"{item['median_current_terminal_hold_error_km']:.1f} / "
            f"{item['median_persistence_error_km']:.1f} | "
            f"{100 * item['current_better_than_persistence_fraction']:.1f}% |"
        )
    lines.extend(
        [
            "",
            "The regional CSV contains the same metrics for western 10°E–60°E, central 60°E–100°E, and eastern 100°E–150°E starts. GDP is observational climatology; HYCOM+NCODA and GLORYS12 are assimilative, so no replay is guaranteed statistically held out.",
        ]
    )
    args.output_prefix.with_suffix(".md").write_text(
        "\n".join(lines) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
