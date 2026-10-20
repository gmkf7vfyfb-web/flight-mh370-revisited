#!/usr/bin/env python3
"""Lightweight, non-destructive validation of the MH370 migration handoff."""

from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.metadata
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]

REQUIRED_FILES = [
    "README.md",
    "AGENTS.md",
    ".gitattributes",
    ".gitignore",
    "handoff/START_HERE.md",
    "handoff/PROJECT_STATE.md",
    "handoff/ASSUMPTIONS.md",
    "handoff/DECISION_LOG.md",
    "handoff/OPEN_QUESTIONS.md",
    "handoff/REPRODUCIBILITY_STATUS.md",
    "handoff/DATA_AND_PROVENANCE.md",
    "history/PROJECT_CONVERSATION_TIMELINE.md",
    "environment/requirements-lock.txt",
    "run_integrated_0011_stage1.py",
    "run_refined_bfo_0011_airborne.py",
    "run_pleiades_bran_diagnostic.py",
    "run_pp_descent_climb_sensitivity.py",
    "outputs/mh370_stage1_0011/run_manifest.json",
    "outputs/mh370_stage1_0011/stage1_summary.csv",
    "outputs/mh370_stage1_0011/MH370_stage1_integrated_estimate_through_0011Z.pdf",
    "outputs/mh370_refined_bfo_0011_airborne/bfo_random_noise_estimate.csv",
    "outputs/mh370_search_evidence/source_register.csv",
    "outputs/paper_draft/Flight_MH370_Revisited_Sections_1_2_First_Pass.docx",
]

PACKAGES = {
    "numpy": "numpy",
    "pandas": "pandas",
    "scipy": "scipy",
    "matplotlib": "matplotlib",
    "Pillow": "PIL",
    "python-docx": "docx",
    "reportlab": "reportlab",
    "lxml": "lxml",
    "contourpy": "contourpy",
    "openpyxl": "openpyxl",
}


def read_single_row(path: Path, predicate) -> dict[str, str]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        for row in csv.DictReader(handle):
            if predicate(row):
                return row
    raise RuntimeError(f"Expected row not found in {path.relative_to(ROOT)}")


def verify_manifest(path: Path) -> tuple[int, list[str]]:
    checked = 0
    failures: list[str] = []
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            line = line.rstrip("\n")
            if not line:
                continue
            digest, rel = line.split("  ", 1)
            target = ROOT / rel
            if not target.is_file():
                failures.append(f"missing: {rel}")
                continue
            h = hashlib.sha256()
            with target.open("rb") as stream:
                for block in iter(lambda: stream.read(1024 * 1024), b""):
                    h.update(block)
            checked += 1
            if h.hexdigest() != digest:
                failures.append(f"hash mismatch: {rel}")
    return checked, failures


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--full",
        action="store_true",
        help="also verify every file against the generated SHA-256 manifest",
    )
    args = parser.parse_args()

    errors: list[str] = []
    warnings: list[str] = []

    for rel in REQUIRED_FILES:
        if not (ROOT / rel).is_file():
            errors.append(f"required file missing: {rel}")

    for package in PACKAGES:
        try:
            importlib.metadata.version(package)
        except importlib.metadata.PackageNotFoundError:
            warnings.append(f"Python package not installed: {package}")

    if not errors:
        stage = read_single_row(
            ROOT / "outputs/mh370_stage1_0011/stage1_summary.csv",
            lambda row: row["case"] == "Primary equal-control priors"
            and row["estimate"] == "Impact after model-averaged drift",
        )
        checks = {
            "stage-one mode latitude": (float(stage["mode_lat_deg"]), -37.2625, 1e-8),
            "stage-one mode longitude": (float(stage["mode_lon_deg_E"]), 89.2375, 1e-8),
            "stage-one median latitude": (float(stage["median_lat_deg"]), -37.03148801790519, 1e-8),
        }

        bfo = read_single_row(
            ROOT / "outputs/mh370_refined_bfo_0011_airborne/bfo_random_noise_estimate.csv",
            lambda row: row["basis"].startswith("Pooled"),
        )
        checks["fast BFO sigma"] = (
            float(bfo["sigma_random_Hz"]),
            0.9953793624482928,
            1e-10,
        )

        pp = read_single_row(
            ROOT / "outputs/mh370_pp_descent_climb_sensitivity/scenario_summary.csv",
            lambda row: row["scenario"] == "full_pp",
        )
        checks["full PP primary latitude shift"] = (
            float(pp["lat_shift_vs_no_PP_same_window_deg"]),
            -0.0026864587686574737,
            1e-10,
        )

        for label, (actual, expected, tolerance) in checks.items():
            if abs(actual - expected) > tolerance:
                errors.append(
                    f"reference mismatch for {label}: {actual} vs {expected}"
                )

    missing_module = ROOT / "run_pleiades_bran_fl400_expanded.py"
    if not missing_module.exists():
        warnings.append(
            "known gap retained: run_pleiades_bran_fl400_expanded.py is absent"
        )

    hardcoded = ROOT / "build_interactive_search_map.py"
    if hardcoded.is_file() and 'Path("/workspace/' in hardcoded.read_text(encoding="utf-8"):
        errors.append(
            "portability regression: build_interactive_search_map.py uses /workspace"
        )

    if args.full:
        manifest = ROOT / "migration/package/MH370_file_manifest_2026-08-14.sha256"
        if not manifest.is_file():
            errors.append("full verification requested but file manifest is absent")
        else:
            checked, failures = verify_manifest(manifest)
            if failures:
                errors.extend(failures)
            else:
                print(f"Full manifest verified: {checked} files")

    print(f"Critical errors: {len(errors)}")
    for item in errors:
        print(f"  ERROR: {item}")
    print(f"Warnings: {len(warnings)}")
    for item in warnings:
        print(f"  WARNING: {item}")

    if errors:
        return 1
    print("Handoff validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
