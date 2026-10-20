#!/usr/bin/env python3
"""Run and summarize deterministic ocean-source replication diagnostics.

This script changes seed, particle count, and optionally the explicit Stokes
surface-response scale in a base TOML. It invokes the canonical runner and
keeps each resolved config beside the output, so Monte Carlo replication and
response sensitivity remain reproducible without runner-only sweep logic.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import subprocess
from pathlib import Path


LEVELS = (0.90, 0.95, 0.99)
TERMINATION_REASONS = (
    "missing_field_coverage",
    "outside_spatial_support",
    "land_encounter",
    "beaching",
    "outside_time_support",
    "numerical_failure",
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def replace_scalar(text: str, name: str, value: int) -> str:
    pattern = re.compile(rf"(?m)^{re.escape(name)}\s*=\s*\d+\s*$")
    replaced, count = pattern.subn(f"{name} = {value}", text)
    if count != 1:
        raise ValueError(f"expected exactly one {name} assignment, found {count}")
    return replaced


def replace_float_scalar(text: str, name: str, value: float) -> str:
    pattern = re.compile(
        rf"(?m)^{re.escape(name)}\s*=\s*[-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][-+]?\d+)?\s*$"
    )
    replaced, count = pattern.subn(f"{name} = {value:g}", text)
    if count < 1:
        raise ValueError(f"expected at least one {name} assignment, found {count}")
    return replaced


def arc_index(identifier: str) -> int:
    match = re.fullmatch(r"arc-(\d+)", identifier)
    if match is None:
        raise ValueError(f"source identifier is not an arc index: {identifier}")
    return int(match.group(1))


def weighted_quantile(cells: list[dict], probability: float) -> int:
    cumulative = 0.0
    for cell in sorted(cells, key=lambda item: arc_index(item["id"])):
        cumulative += cell["normalized_weight"]
        if cumulative >= probability:
            return arc_index(cell["id"])
    return arc_index(max(cells, key=lambda item: arc_index(item["id"]))["id"])


def contour(cells: list[dict], level: float) -> dict:
    tail = (1.0 - level) / 2.0
    lower = weighted_quantile(cells, tail)
    upper = weighted_quantile(cells, 1.0 - tail)
    ranked = sorted(
        cells,
        key=lambda item: (-item["normalized_weight"], arc_index(item["id"])),
    )
    total = 0.0
    selected = []
    for cell in ranked:
        selected.append(arc_index(cell["id"]))
        total += cell["normalized_weight"]
        if total >= level:
            break
    selected.sort()
    return {
        "level": level,
        "equal_tail_arc_interval": [lower, upper],
        "highest_weight_arc_indices": selected,
        "highest_weight_mass": total,
    }


def flaperon_ess(cell: dict) -> float:
    recoveries = cell.get("recoveries", [])
    matches = [item for item in recoveries if item.get("is_flaperon")]
    if len(matches) != 1:
        raise ValueError(f"expected one confirmed-flaperon recovery in {cell['id']}")
    return float(matches[0]["effective_sample_size"])


def minimum_recovery_ess(cell: dict) -> float:
    recoveries = cell.get("recoveries", [])
    if not recoveries:
        raise ValueError(f"no recovery evaluations in {cell['id']}")
    return min(float(item["effective_sample_size"]) for item in recoveries)


def median(values: list[float]) -> float:
    ordered = sorted(values)
    middle = len(ordered) // 2
    if len(ordered) % 2:
        return ordered[middle]
    return (ordered[middle - 1] + ordered[middle]) / 2.0


def summarize_run(name: str, output: Path, config: Path) -> dict:
    result = json.loads((output / "source-area.json").read_text(encoding="utf-8"))
    runtime = json.loads((output / "runtime-receipt.json").read_text(encoding="utf-8"))
    manifest = json.loads((output / "run-manifest.json").read_text(encoding="utf-8"))
    cells = result["cells"]
    ess = [flaperon_ess(cell) for cell in cells]
    minimum_ess = [minimum_recovery_ess(cell) for cell in cells]
    isotope = [cell.get("isotope") for cell in cells if cell.get("isotope")]
    weighted_termination_fractions = {
        reason: sum(
            cell["termination_reason_fractions"].get(reason, 0.0) for cell in cells
        )
        / len(cells)
        for reason in TERMINATION_REASONS
    }
    proposal_termination_fractions = {
        reason: sum(cell["termination_reasons"].get(reason, 0) for cell in cells)
        / runtime["simulated_paths"]
        for reason in TERMINATION_REASONS
    }
    stokes_scales = manifest.get("stokes_velocity_scales")
    if stokes_scales is None:
        stokes_scales = {"configured-object-motion": manifest["stokes_velocity_scale"]}
    unique_stokes_scales = set(stokes_scales.values())
    common_stokes_scale = (
        next(iter(unique_stokes_scales)) if len(unique_stokes_scales) == 1 else None
    )
    return {
        "name": name,
        "config": str(config),
        "config_sha256": sha256(config),
        "output": str(output),
        "seed": result["seed"],
        "particles_per_cell": result["particles_per_cell"],
        "selection_strength": manifest["sampling"]["selection_strength"],
        "sampling_start_days_before_recovery": manifest["sampling"][
            "start_days_before_recovery"
        ],
        "resampling_interval_days": manifest["sampling"]["resampling_interval_days"],
        "stokes_velocity_scale": common_stokes_scale,
        "stokes_velocity_scales": stokes_scales,
        "peak_arc_index": arc_index(result["peak_cell_id"]),
        "maximum_arrival_effective_sample_size": max(ess),
        "median_arrival_effective_sample_size": median(ess),
        "cells_arrival_ess_at_least_100": sum(value >= 100.0 for value in ess),
        "cells_arrival_ess_at_least_200": sum(value >= 200.0 for value in ess),
        "cells_arrival_ess_at_least_300": sum(value >= 300.0 for value in ess),
        "source_mass_with_arrival_ess_at_least_100": sum(
            cell["normalized_weight"]
            for cell, value in zip(cells, ess, strict=True)
            if value >= 100.0
        ),
        "source_mass_with_arrival_ess_at_least_200": sum(
            cell["normalized_weight"]
            for cell, value in zip(cells, ess, strict=True)
            if value >= 200.0
        ),
        "source_mass_with_arrival_ess_at_least_300": sum(
            cell["normalized_weight"]
            for cell, value in zip(cells, ess, strict=True)
            if value >= 300.0
        ),
        "minimum_recovery_effective_sample_size": min(minimum_ess),
        "median_cell_minimum_recovery_effective_sample_size": median(minimum_ess),
        "source_mass_with_every_recovery_ess_at_least_100": sum(
            cell["normalized_weight"]
            for cell, value in zip(cells, minimum_ess, strict=True)
            if value >= 100.0
        ),
        "source_mass_with_every_recovery_ess_at_least_200": sum(
            cell["normalized_weight"]
            for cell, value in zip(cells, minimum_ess, strict=True)
            if value >= 200.0
        ),
        "source_mass_with_every_recovery_ess_at_least_300": sum(
            cell["normalized_weight"]
            for cell, value in zip(cells, minimum_ess, strict=True)
            if value >= 300.0
        ),
        "mean_importance_weighted_terminated_fraction": result[
            "mean_terminated_fraction"
        ],
        "mean_proposal_terminated_fraction": result[
            "mean_proposal_terminated_fraction"
        ],
        "mean_importance_weighted_termination_reason_fractions": weighted_termination_fractions,
        "mean_proposal_termination_reason_fractions": proposal_termination_fractions,
        "isotope_path_counts": {
            "compatible": sum(item["compatible_paths"] for item in isotope),
            "marginal": sum(item["marginal_paths"] for item in isotope),
            "rejected": sum(item["rejected_paths"] for item in isotope),
            "missing_sst": sum(item["missing_coverage_paths"] for item in isotope),
        },
        "contours": [contour(cells, level) for level in LEVELS],
        "weights": {cell["id"]: cell["normalized_weight"] for cell in cells},
        "elapsed_seconds": runtime["elapsed_seconds"],
        "peak_memory_kib": runtime["peak_memory_kib"],
    }


def compare(first: dict, second: dict) -> dict:
    identifiers = sorted(set(first["weights"]) | set(second["weights"]))
    total_variation = 0.5 * sum(
        abs(first["weights"].get(item, 0.0) - second["weights"].get(item, 0.0))
        for item in identifiers
    )
    contours = []
    for left, right in zip(first["contours"], second["contours"], strict=True):
        left_set = set(left["highest_weight_arc_indices"])
        right_set = set(right["highest_weight_arc_indices"])
        contours.append(
            {
                "level": left["level"],
                "equal_tail_endpoint_maximum_shift_cells": max(
                    abs(left["equal_tail_arc_interval"][0] - right["equal_tail_arc_interval"][0]),
                    abs(left["equal_tail_arc_interval"][1] - right["equal_tail_arc_interval"][1]),
                ),
                "highest_weight_set_jaccard": len(left_set & right_set)
                / len(left_set | right_set),
            }
        )
    return {
        "first": first["name"],
        "second": second["name"],
        "peak_shift_arc_cells": abs(first["peak_arc_index"] - second["peak_arc_index"]),
        "weight_total_variation": total_variation,
        "contours": contours,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--runner", type=Path, required=True)
    parser.add_argument("--base-config", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument(
        "--case",
        action="append",
        required=True,
        help=(
            "NAME:SEED:PARTICLES[:STOKES_SCALE_OR_DASH[:SELECTION_STRENGTH"
            "[:START_DAYS_BEFORE_RECOVERY[:RESAMPLING_INTERVAL_DAYS]]]]; "
            "may be repeated"
        ),
    )
    parser.add_argument(
        "--existing-case",
        action="append",
        default=[],
        help="NAME:OUTPUT_DIRECTORY:CONFIG; reference an existing canonical run without copying it",
    )
    args = parser.parse_args()
    if not args.runner.is_file() or not args.base_config.is_file():
        parser.error("runner and base config must exist")

    cases = []
    for item in args.case:
        parts = item.split(":")
        if len(parts) not in {3, 4, 5, 6, 7} or not re.fullmatch(
            r"[a-z][a-z0-9-]*", parts[0]
        ):
            parser.error(f"invalid case: {item}")
        scale = None if len(parts) == 3 or parts[3] == "-" else float(parts[3])
        if scale is not None and not 0.0 <= scale <= 2.0:
            parser.error(f"Stokes response must lie between zero and two: {item}")
        selection_strength = (
            None if len(parts) < 5 or parts[4] == "-" else float(parts[4])
        )
        if selection_strength is not None and selection_strength <= 0.0:
            parser.error(f"selection strength must be positive: {item}")
        start_days = None if len(parts) < 6 or parts[5] == "-" else float(parts[5])
        if start_days is not None and start_days <= 0.0:
            parser.error(f"sampling start days must be positive: {item}")
        interval_days = None if len(parts) < 7 or parts[6] == "-" else float(parts[6])
        if interval_days is not None and interval_days <= 0.0:
            parser.error(f"resampling interval must be positive: {item}")
        cases.append(
            (
                parts[0],
                int(parts[1]),
                int(parts[2]),
                scale,
                selection_strength,
                start_days,
                interval_days,
            )
        )
    existing_cases = []
    for item in args.existing_case:
        parts = item.split(":")
        if len(parts) != 3 or not re.fullmatch(r"[a-z][a-z0-9-]*", parts[0]):
            parser.error(f"invalid existing case: {item}")
        output = Path(parts[1])
        config = Path(parts[2])
        if not output.is_dir() or not config.is_file():
            parser.error(f"existing case output or config is absent: {item}")
        existing_cases.append((parts[0], output, config))
    names = [name for name, _, _, _, _, _, _ in cases] + [
        name for name, _, _ in existing_cases
    ]
    if len(set(names)) != len(names):
        parser.error("case names must be unique")

    args.output.mkdir(parents=True, exist_ok=True)
    config_directory = args.output / "configs"
    config_directory.mkdir(exist_ok=True)
    base_text = args.base_config.read_text(encoding="utf-8")
    summaries = [
        summarize_run(name, output, config)
        for name, output, config in existing_cases
    ]
    for (
        name,
        seed,
        particles,
        stokes_scale,
        selection_strength,
        start_days,
        interval_days,
    ) in cases:
        text = replace_scalar(base_text, "seed", seed)
        text = replace_scalar(text, "particles_per_cell", particles)
        if stokes_scale is not None:
            text = replace_float_scalar(text, "stokes_velocity_scale", stokes_scale)
        if selection_strength is not None:
            text = replace_float_scalar(
                text, "selection_strength", selection_strength
            )
        if start_days is not None:
            text = replace_float_scalar(
                text, "start_days_before_recovery", start_days
            )
        if interval_days is not None:
            text = replace_float_scalar(
                text, "resampling_interval_days", interval_days
            )
        config = config_directory / f"{name}.toml"
        config.write_text(text, encoding="utf-8")
        output = args.output / "runs" / name
        completed_outputs = [
            output / "source-area.json",
            output / "runtime-receipt.json",
            output / "run-manifest.json",
        ]
        if not all(path.is_file() for path in completed_outputs):
            if output.exists() and any(output.iterdir()):
                raise RuntimeError(f"partial nonempty run requires inspection: {output}")
            subprocess.run(
                [
                    str(args.runner.resolve()),
                    "estimate-ocean-drift",
                    "--config",
                    str(config.resolve()),
                    "--output",
                    str(output.resolve()),
                ],
                check=True,
            )
        summaries.append(summarize_run(name, output, config))

    comparisons = [
        compare(summaries[first], summaries[second])
        for first in range(len(summaries))
        for second in range(first + 1, len(summaries))
    ]
    response_sensitivity = len({run["stokes_velocity_scale"] for run in summaries}) > 1
    payload = {
        "schema": (
            "mh370-ocean-source-stokes-response-v1"
            if response_sensitivity
            else "mh370-ocean-source-stability-v1"
        ),
        "base_config": str(args.base_config),
        "base_config_sha256": sha256(args.base_config),
        "runs": summaries,
        "pairwise_comparisons": comparisons,
        "interpretation": (
            "These are explicit Stokes surface-response sensitivities within one current family. They remain separate and are not mixed or subjectively weighted."
            if response_sensitivity
            else "These are Monte Carlo stability diagnostics within one explicit current family. No family mixing or model weighting is performed."
        ),
    }
    (args.output / "stability-summary.json").write_text(
        json.dumps(payload, indent=2) + "\n", encoding="utf-8"
    )
    with (args.output / "stability-runs.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.writer(stream)
        writer.writerow(
            [
                "name",
                "seed",
                "particles_per_cell",
                "selection_strength",
                "sampling_start_days_before_recovery",
                "resampling_interval_days",
                "stokes_velocity_scale",
                "peak_arc_index",
                "maximum_arrival_ess",
                "median_arrival_ess",
                "cells_arrival_ess_at_least_100",
                "cells_arrival_ess_at_least_200",
                "cells_arrival_ess_at_least_300",
                "source_mass_with_arrival_ess_at_least_100",
                "source_mass_with_arrival_ess_at_least_200",
                "source_mass_with_arrival_ess_at_least_300",
                "minimum_recovery_ess",
                "median_cell_minimum_recovery_ess",
                "source_mass_with_every_recovery_ess_at_least_100",
                "source_mass_with_every_recovery_ess_at_least_200",
                "source_mass_with_every_recovery_ess_at_least_300",
                "mean_importance_weighted_terminated_fraction",
                "mean_proposal_terminated_fraction",
                *(
                    f"importance_weighted_{reason}_fraction"
                    for reason in TERMINATION_REASONS
                ),
                "elapsed_seconds",
                "peak_memory_kib",
            ]
        )
        for run in summaries:
            writer.writerow(
                [
                    run["name"],
                    run["seed"],
                    run["particles_per_cell"],
                    run["selection_strength"],
                    run["sampling_start_days_before_recovery"],
                    run["resampling_interval_days"],
                    run["stokes_velocity_scale"],
                    run["peak_arc_index"],
                    run["maximum_arrival_effective_sample_size"],
                    run["median_arrival_effective_sample_size"],
                    run["cells_arrival_ess_at_least_100"],
                    run["cells_arrival_ess_at_least_200"],
                    run["cells_arrival_ess_at_least_300"],
                    run["source_mass_with_arrival_ess_at_least_100"],
                    run["source_mass_with_arrival_ess_at_least_200"],
                    run["source_mass_with_arrival_ess_at_least_300"],
                    run["minimum_recovery_effective_sample_size"],
                    run["median_cell_minimum_recovery_effective_sample_size"],
                    run["source_mass_with_every_recovery_ess_at_least_100"],
                    run["source_mass_with_every_recovery_ess_at_least_200"],
                    run["source_mass_with_every_recovery_ess_at_least_300"],
                    run["mean_importance_weighted_terminated_fraction"],
                    run["mean_proposal_terminated_fraction"],
                    *(
                        run[
                            "mean_importance_weighted_termination_reason_fractions"
                        ][reason]
                        for reason in TERMINATION_REASONS
                    ),
                    run["elapsed_seconds"],
                    run["peak_memory_kib"],
                ]
            )


if __name__ == "__main__":
    main()
