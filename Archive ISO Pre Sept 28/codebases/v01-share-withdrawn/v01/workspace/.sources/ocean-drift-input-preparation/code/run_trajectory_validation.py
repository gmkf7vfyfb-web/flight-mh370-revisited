#!/usr/bin/env python3
"""Run reproducible all-path drifter replay cases for one current family."""

from __future__ import annotations

import argparse
import hashlib
import json
import resource
import subprocess
import time
from pathlib import Path


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def safe_name(value: str) -> str:
    name = "".join(character if character.isalnum() else "-" for character in value)
    return "-".join(part for part in name.lower().split("-") if part)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--runner", type=Path, required=True)
    parser.add_argument("--family", required=True)
    parser.add_argument("--field", type=Path, required=True)
    parser.add_argument(
        "--trajectory",
        action="append",
        required=True,
        help="YEAR:PATH; may be repeated",
    )
    parser.add_argument("--horizon", type=float, action="append", required=True)
    parser.add_argument("--attempts", type=int, default=600)
    parser.add_argument("--stokes", type=Path)
    parser.add_argument(
        "--stokes-scale",
        type=float,
        action="append",
        help="surface-Stokes velocity multiplier; may be repeated",
    )
    parser.add_argument(
        "--renormalize-finite-stokes-corners",
        action="store_true",
        help="renormalize over finite corners of an audited persistent Stokes mask",
    )
    parser.add_argument(
        "--renormalize-finite-current-corners",
        action="store_true",
        help="renormalize only the typed persistent-land corners of the current field",
    )
    parser.add_argument("--maximum-interpolation-gap-hours", type=float)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    if args.attempts <= 0 or any(value <= 0.0 for value in args.horizon):
        parser.error("attempts and horizons must be positive")
    stokes_scales = args.stokes_scale or [1.0]
    if any(not 0.0 <= value <= 2.0 for value in stokes_scales):
        parser.error("Stokes scales must lie between zero and two")
    if args.stokes is None and args.stokes_scale is not None:
        parser.error("--stokes-scale requires --stokes")
    for path in (args.runner, args.field, args.stokes):
        if path is not None and not path.is_file():
            parser.error(f"required file is absent: {path}")
    trajectories = []
    for item in args.trajectory:
        year_text, separator, path_text = item.partition(":")
        if not separator or not year_text.isdigit():
            parser.error(f"invalid trajectory specification: {item}")
        path = Path(path_text)
        if not path.is_file():
            parser.error(f"trajectory file is absent: {path}")
        trajectories.append((int(year_text), path))

    args.output.mkdir(parents=True, exist_ok=True)
    runner = args.runner.resolve()
    field = args.field.resolve()
    modes = [(args.family, None, 1.0, "currents")]
    if args.stokes is not None:
        for scale in sorted(set(stokes_scales)):
            scale_text = f"{scale:g}"
            scale_name = scale_text.replace(".", "p")
            if len(stokes_scales) == 1 and scale == 1.0:
                family = f"{args.family}_plus_distinct_stokes"
                mode = "currents-stokes"
            else:
                family = f"{args.family}_plus_{scale_text}x_distinct_stokes"
                mode = f"currents-stokes-{scale_name}x"
            modes.append((family, args.stokes.resolve(), scale, mode))
    cases = []
    commands = []
    for family, stokes, stokes_scale, mode in modes:
        for year, trajectory in trajectories:
            for horizon in sorted(set(args.horizon)):
                horizon_text = f"{horizon:g}"
                output = args.output / (
                    f"{safe_name(args.family)}-{mode}-{year}-{horizon_text}d.json"
                )
                command = [
                    str(runner),
                    family,
                    str(field),
                    str(trajectory.resolve()),
                    horizon_text,
                    str(args.attempts),
                    str(output.resolve()),
                    "none" if stokes is None else str(stokes),
                    (
                        "none"
                        if args.maximum_interpolation_gap_hours is None
                        else f"{args.maximum_interpolation_gap_hours:g}"
                    ),
                    f"{stokes_scale:g}",
                    str(
                        args.renormalize_finite_stokes_corners and stokes is not None
                    ).lower(),
                    str(args.renormalize_finite_current_corners).lower(),
                ]
                if output.exists():
                    document = json.loads(output.read_text(encoding="utf-8"))
                    if (
                        document.get("schema") != "mh370-current-trajectory-replay-v5"
                        or document.get("family") != family
                        or document.get("horizon_days") != horizon
                        or document.get("stokes_velocity_scale") != stokes_scale
                        or document.get("renormalize_finite_stokes_corners")
                        != (args.renormalize_finite_stokes_corners and stokes is not None)
                        or document.get("renormalize_finite_current_corners")
                        != args.renormalize_finite_current_corners
                    ):
                        document = None
                    else:
                        elapsed = None
                else:
                    document = None
                if document is None:
                    started = time.perf_counter()
                    subprocess.run(command, check=True)
                    elapsed = time.perf_counter() - started
                cases.append(
                    {
                        "family": family,
                        "year": year,
                        "horizon_days": horizon,
                        "attempts": args.attempts,
                        "stokes_velocity_scale": stokes_scale,
                        "elapsed_wall_seconds": elapsed,
                        "output": str(output),
                        "output_sha256": sha256(output),
                    }
                )
                commands.append(command)

    usage = resource.getrusage(resource.RUSAGE_CHILDREN)
    receipt = {
        "schema": "mh370-trajectory-validation-resource-v1",
        "family": args.family,
        "commands": commands,
        "inputs": {
            "runner": {"path": str(runner), "sha256": sha256(runner)},
            "field": {"path": str(field), "sha256": sha256(field)},
            "trajectories": [
                {"year": year, "path": str(path), "sha256": sha256(path)}
                for year, path in trajectories
            ],
            "stokes": (
                None
                if args.stokes is None
                else {
                    "path": str(args.stokes.resolve()),
                    "sha256": sha256(args.stokes),
                }
            ),
            "stokes_velocity_scales": stokes_scales,
            "renormalize_finite_stokes_corners": args.renormalize_finite_stokes_corners,
            "renormalize_finite_current_corners": args.renormalize_finite_current_corners,
        },
        "cases": cases,
        "maximum_child_resident_set_kib": usage.ru_maxrss,
        "child_user_cpu_seconds": usage.ru_utime,
        "child_system_cpu_seconds": usage.ru_stime,
        "note": "Every attempted path remains in each score. ru_maxrss is the maximum resident set of any sequential child, not a sum.",
    }
    path = args.output / f"{safe_name(args.family)}-validation-resource.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
