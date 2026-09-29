#!/usr/bin/env python3
"""Run the declared v0.1 impact conditionals through the canonical Rust hub.

This file contains no scientific equations.  It materializes explicit TOML inputs from
the checked-in base configuration and family matrix, invokes `mh370 infer-impact` once per
family, and hashes the resulting immutable family directories.  Families remain separate.
"""

from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys


PATH_KEYS = {
    "source_handoff",
    "observations",
    "satellite_ephemeris",
    "grid",
    "manifest",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def replace_once(text: str, old: str, new: str) -> str:
    count = text.count(old)
    if count != 1:
        raise ValueError(f"expected exactly one occurrence of {old!r}, found {count}")
    return text.replace(old, new)


def toml_inline(value: dict[str, object]) -> str:
    fields = []
    for key, item in value.items():
        rendered = f'"{item}"' if isinstance(item, str) else repr(item).lower()
        fields.append(f"{key} = {rendered}")
    return "{ " + ", ".join(fields) + " }"


def logical_path(path: Path, relative_to: Path) -> str:
    return Path(os.path.relpath(path.resolve(), relative_to.resolve())).as_posix()


def rebase_paths(text: str, base_directory: Path, target_directory: Path) -> str:
    output = []
    for line in text.splitlines():
        stripped = line.strip()
        if "=" in stripped and not stripped.startswith("#"):
            key, raw = (part.strip() for part in stripped.split("=", 1))
            if key in PATH_KEYS and raw.startswith('"') and raw.endswith('"'):
                path = Path(raw[1:-1])
                if not path.is_absolute():
                    path = (base_directory / path).resolve()
                prefix = line[: len(line) - len(line.lstrip())]
                line = f'{prefix}{key} = "{logical_path(path, target_directory)}"'
        output.append(line)
    return "\n".join(output) + "\n"


def materialize(
    base_text: str,
    base_directory: Path,
    family: dict[str, object],
    source_handoff: Path,
    source_seed: int,
    target_directory: Path,
    source_tree_sha256: str,
    source_draw_count: int | None,
    hypothesis_id: str | None = None,
) -> str:
    text = rebase_paths(base_text, base_directory, target_directory)
    base_source = logical_path(
        base_directory / "../runs/mh370/0011-core-comparison/bto-bfo-medium/seed-370023/posterior-handoff.json",
        target_directory,
    )
    text = replace_once(
        text,
        f'source_handoff = "{base_source}"',
        f'source_handoff = "{logical_path(source_handoff, target_directory)}"',
    )
    text = replace_once(text, "eof_seed = 3700230019", f"eof_seed = {source_seed}0019")
    text = replace_once(
        text,
        'code_revision = "source_revision_unavailable_direct_base_config"',
        f'code_revision = "source-tree-sha256-{source_tree_sha256}"',
    )
    family_id = str(family["id"])
    hypothesis_id = hypothesis_id or family_id
    text = replace_once(
        text,
        'hypothesis_id = "era5-martin-arc1-openap-current-best-glide"',
        f'hypothesis_id = "{hypothesis_id}"',
    )
    text = replace_once(
        text,
        'id = "martin-arc1-openap-current-best-glide"',
        f'id = "{family_id}"',
    )
    text = replace_once(
        text,
        'label = "martin-arc1-openap-current-best-glide"',
        f'label = "{family_id}"',
    )
    text = replace_once(
        text,
        'aerodynamic_family = "openap_v2_6_0_attached_flow"',
        f'aerodynamic_family = "{family["aerodynamic_family"]}"',
    )
    text = replace_once(
        text,
        "anchor_total_fuel = 33524.10488196",
        f'anchor_total_fuel = {family["fuel_anchor_kg"]}',
    )
    text = replace_once(
        text,
        'anchor_utc = "2014-03-07T18:28:05.9Z"',
        f'anchor_utc = "{family["fuel_anchor_utc"]}"',
    )
    text = replace_once(
        text,
        'effective_feed_timing = { mode = "equal_endurance" }',
        f'effective_feed_timing = {toml_inline(family["effective_feed_timing"])}',
    )
    text = replace_once(
        text,
        "command = { mode = \"uncontrolled\", lift_coefficient = 0.7145896010104964, bank_angle = 0.0 }",
        "command = { mode = \"uncontrolled\", lift_coefficient = "
        f'{family["post_flameout_lift_coefficient"]}, bank_angle = 0.0 }}',
    )
    if source_draw_count is not None:
        text = replace_once(text, "source_draw_count = 512", f"source_draw_count = {source_draw_count}")
    return text


def source_tree_lock(repository: Path) -> dict[str, object]:
    candidates = [
        repository / "Cargo.toml",
        repository / "Cargo.lock",
        repository / "rust-toolchain.toml",
    ]
    for crate in sorted((repository / "crates").iterdir()):
        if not crate.is_dir():
            continue
        cargo = crate / "Cargo.toml"
        if cargo.is_file():
            candidates.append(cargo)
        candidates.extend(sorted((crate / "src").rglob("*.rs")) if (crate / "src").is_dir() else [])
    files = {
        logical_path(path, repository): sha256(path)
        for path in sorted(set(candidates))
    }
    canonical = "".join(f"{name}\0{digest}\n" for name, digest in sorted(files.items())).encode()
    return {
        "schema_id": "mh370-source-tree-lock",
        "schema_version": 1,
        "algorithm": "sha256 of sorted UTF-8 logical-path, NUL, file-sha256, newline records",
        "source_tree_sha256": hashlib.sha256(canonical).hexdigest(),
        "files": files,
    }


def run_infer_impact(command: list[str]) -> subprocess.CompletedProcess[str]:
    """Run one independent impact inference while retaining ordered diagnostics."""

    return subprocess.run(command, check=False, capture_output=True, text=True)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--matrix", type=Path, required=True)
    parser.add_argument("--runner", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--draw-count", type=int)
    parser.add_argument("--jobs", type=int, default=1)
    args = parser.parse_args()

    matrix_path = args.matrix.resolve()
    matrix = json.loads(matrix_path.read_text(encoding="utf-8"))
    if matrix.get("schema_version") != 1 or not matrix.get("families") or not matrix.get("source_seeds"):
        raise ValueError("unsupported or empty impact release family matrix")
    if args.draw_count is not None and args.draw_count <= 0:
        raise ValueError("--draw-count must be positive")
    if args.jobs <= 0:
        raise ValueError("--jobs must be positive")
    base_path = (matrix_path.parent / matrix["base_config"]).resolve()
    repository = base_path.parent.parent.resolve()
    runner = args.runner.resolve()
    output = args.output.resolve()
    if output.exists():
        raise FileExistsError(f"refusing to overwrite {output}")
    if not runner.is_file():
        raise FileNotFoundError(f"runner executable not found: {runner}")
    output.mkdir(parents=True)
    tree_lock = source_tree_lock(repository)
    tree_lock_path = output / "source-tree.lock.json"
    tree_lock_path.write_text(
        json.dumps(tree_lock, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    source_seeds = [int(seed) for seed in matrix["source_seeds"]]
    if len(source_seeds) != len(set(source_seeds)) or any(seed <= 0 for seed in source_seeds):
        raise ValueError("source seeds must be unique positive integers")
    source_template = str(matrix["source_handoff_template"])
    config_directory = output / "configs"
    config_directory.mkdir()
    base_text = base_path.read_text(encoding="utf-8")

    families_by_id = {family["id"]: family for family in matrix["families"]}
    jobs = [
        {
            "id": family["id"],
            "title": family["title"],
            "role": family["role"],
            "family": family,
            "source_template": source_template,
            "kind": "terminal_family",
            "release_draw_count_per_seed": family["release_draw_count_per_seed"],
        }
        for family in matrix["families"]
    ]
    for branch in matrix.get("conditional_source_branches", []):
        terminal_family_id = branch["terminal_family_id"]
        if terminal_family_id not in families_by_id:
            raise ValueError(f"unknown terminal family for source branch: {terminal_family_id}")
        jobs.append(
            {
                "id": branch["id"],
                "title": branch["title"],
                "role": branch["role"],
                "family": families_by_id[terminal_family_id],
                "source_template": branch["source_handoff_template"],
                "kind": "conditional_source_branch",
                "release_draw_count_per_seed": branch["release_draw_count_per_seed"],
            }
        )

    output_ids = [str(job["id"]) for job in jobs]
    if len(output_ids) != len(set(output_ids)):
        raise ValueError("terminal-family and conditional-branch ids must be unique")

    planned_jobs = []
    planned_runs = []
    planned_outputs: set[Path] = set()
    for job in jobs:
        family = job["family"]
        output_id = job["id"]
        family_id = family["id"]
        draw_count = args.draw_count or int(job["release_draw_count_per_seed"])
        if draw_count <= 0:
            raise ValueError(f"invalid release draw count for {output_id}")
        family_config_directory = config_directory / output_id
        family_config_directory.mkdir()
        runs = []
        for source_seed in source_seeds:
            job_source_template = str(job["source_template"])
            source_handoff = (
                matrix_path.parent / job_source_template.format(seed=source_seed)
            ).resolve()
            if not source_handoff.is_file():
                raise FileNotFoundError(f"source handoff not found: {source_handoff}")
            config_path = family_config_directory / f"seed-{source_seed}.toml"
            config_text = materialize(
                base_text,
                base_path.parent,
                family,
                source_handoff,
                source_seed,
                config_path.parent,
                str(tree_lock["source_tree_sha256"]),
                draw_count,
                str(output_id),
            )
            config_path.write_text(config_text, encoding="utf-8", newline="\n")
            family_output = output / output_id / f"seed-{source_seed}"
            command = [
                logical_path(runner, Path.cwd()),
                "infer-impact",
                "--config",
                logical_path(config_path, Path.cwd()),
                "--output",
                logical_path(family_output, Path.cwd()),
            ]
            runs.append(
                {
                    "source_seed": source_seed,
                    "config_path": config_path,
                    "family_output": family_output,
                    "command": command,
                }
            )
            if family_output in planned_outputs:
                raise ValueError(f"duplicate planned output directory: {family_output}")
            planned_outputs.add(family_output)
            planned_runs.append(runs[-1])
        planned_jobs.append(
            {
                "job": job,
                "family_id": family_id,
                "draw_count": draw_count,
                "runs": runs,
            }
        )

    # Configs and output identities are fixed before subprocesses begin.  Results
    # are collected in this declared order, irrespective of completion order.
    with ThreadPoolExecutor(max_workers=args.jobs) as executor:
        completed_runs = list(
            executor.map(
                run_infer_impact,
                (planned["command"] for planned in planned_runs),
            )
        )
    for planned, completed in zip(planned_runs, completed_runs, strict=True):
        if completed.stdout:
            print(completed.stdout, end="")
        if completed.stderr:
            print(completed.stderr, end="", file=sys.stderr)
        if completed.returncode != 0:
            raise subprocess.CalledProcessError(
                completed.returncode,
                planned["command"],
                output=completed.stdout,
                stderr=completed.stderr,
            )

    entries = []
    source_branch_entries = []
    for planned_job in planned_jobs:
        job = planned_job["job"]
        runs = []
        for planned in planned_job["runs"]:
            config_path = planned["config_path"]
            family_output = planned["family_output"]
            runs.append(
                {
                    "source_seed": planned["source_seed"],
                    "config": str(config_path.relative_to(output)),
                    "config_sha256": sha256(config_path),
                    "impact_handoff": str(
                        (family_output / "impact-posterior-handoff.json").relative_to(output)
                    ),
                    "impact_handoff_sha256": sha256(
                        family_output / "impact-posterior-handoff.json"
                    ),
                    "transition_sidecar": str(
                        (family_output / "transition-sidecar.json").relative_to(output)
                    ),
                    "transition_sidecar_sha256": sha256(
                        family_output / "transition-sidecar.json"
                    ),
                    "run_manifest": str(
                        (family_output / "run-manifest.json").relative_to(output)
                    ),
                    "run_manifest_sha256": sha256(family_output / "run-manifest.json"),
                }
            )
        entry = {
            "id": job["id"],
            "title": job["title"],
            "role": job["role"],
            "eof_scenario_id": planned_job["family_id"],
            "draw_count_per_seed": planned_job["draw_count"],
            "source_seed_combination": "equal_numerical_replicates",
            "runs": runs,
        }
        if job["kind"] == "terminal_family":
            entries.append(entry)
        else:
            source_branch_entries.append(entry)

    suite = {
        "schema_id": "mh370-impact-conditional-suite",
        "schema_version": 1,
        "family_combination": "separate",
        "path_basis": "repository_root",
        "generator": logical_path(Path(__file__), repository),
        "generator_sha256": sha256(Path(__file__).resolve()),
        "matrix": logical_path(matrix_path, repository),
        "matrix_sha256": sha256(matrix_path),
        "base_config": logical_path(base_path, repository),
        "base_config_sha256": sha256(base_path),
        "runner": logical_path(runner, repository),
        "runner_sha256": sha256(runner),
        "source_tree_lock": tree_lock_path.name,
        "source_tree_lock_sha256": sha256(tree_lock_path),
        "source_tree_sha256": tree_lock["source_tree_sha256"],
        "requested_draw_count": args.draw_count,
        "policy": matrix["policy"],
        "families": entries,
        "conditional_source_branches": source_branch_entries,
    }
    suite_path = output / "suite-manifest.json"
    suite_path.write_text(
        json.dumps(suite, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(
        f"status=complete families={len(entries)} source_branches={len(source_branch_entries)} "
        f"manifest={suite_path}"
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, subprocess.CalledProcessError) as error:
        print(f"error: {error}", file=sys.stderr)
        raise SystemExit(2)
