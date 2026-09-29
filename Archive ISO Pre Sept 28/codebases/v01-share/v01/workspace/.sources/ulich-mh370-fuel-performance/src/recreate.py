#!/usr/bin/env python3
"""Run the complete deterministic source-only recreation and workbook audit."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import resource
import sys
import time
from typing import Any

sys.dont_write_bytecode = True

from public_performance import (  # noqa: E402
    PublicPerformanceModel,
    convergence_check,
    recreate_acars,
    recreate_official_post_acars,
    recreate_stress_family,
)
from report import render_report  # noqa: E402
from workbook_audit import audit_workbook, sha256_file  # noqa: E402


PACKAGE_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PACKAGE_ROOT / "data"
OUTPUT_DIR = PACKAGE_ROOT / "outputs"


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        allow_nan=False,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")


def write_json(path: Path, value: Any) -> None:
    path.write_text(
        json.dumps(value, allow_nan=False, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def validate_no_circular_inputs(paths: list[Path]) -> dict[str, Any]:
    prohibited_literals = {
        "legacy_1822_fuel": "18:22",
        "legacy_045t_sd": "0.45 t",
        "event_derived_exhaustion": "00:17:30",
    }
    findings = {}
    for identifier, literal in prohibited_literals.items():
        matches = []
        for path in paths:
            if literal.lower() in path.read_text(encoding="utf-8").lower():
                matches.append(path.name)
        findings[identifier] = {"literal_present": bool(matches), "files": matches}
    return {
        "checked_files": [path.name for path in paths],
        "findings": findings,
        "passed": not any(row["literal_present"] for row in findings.values()),
    }


def build_results(
    model: PublicPerformanceModel,
    acars: dict[str, Any],
    official: dict[str, Any],
    stress: dict[str, Any],
    contract: dict[str, Any],
    workbook_sha256: str,
) -> dict[str, Any]:
    acars_result = recreate_acars(model, acars)
    post_result = recreate_official_post_acars(model, acars, official)
    stress_result = recreate_stress_family(model, acars, stress)
    convergence = convergence_check(model, acars, model.p("convergence_step_sizes_s"))
    burn_values = [row["predicted_total_burn_kg"] for row in convergence]
    spread = max(burn_values) - min(burn_values)
    circular_check = validate_no_circular_inputs(
        [
            DATA_DIR / "model_parameters.json",
            DATA_DIR / "official_acars.json",
            DATA_DIR / "official_post_acars.json",
            DATA_DIR / "stress_families.json",
        ]
    )
    validations = {
        "official_anchor_exact": acars["required_anchor"]
        == {
            "utc": "2014-03-07T17:06:43Z",
            "zero_fuel_weight_kg": 174369.0,
            "fuel_kg": 43800.0,
            "altitude_ft": 35004.0,
            "mach": 0.821,
            "sat_c": -43.8,
        },
        "six_official_fuel_values_exact": [row["fuel_kg"] for row in acars["records"]]
        == [49200.0, 47800.0, 46500.0, 45400.0, 44500.0, 43800.0],
        "coarse_acars_total_error_passed": abs(
            acars_result["total_error_predicted_minus_observed_kg"]
        )
        <= model.p("acars_total_abs_error_acceptance_kg"),
        "coarse_acars_interval_rmse_passed": acars_result["interval_rmse_kg"]
        <= model.p("acars_interval_rmse_acceptance_kg"),
        "integration_convergence_passed": spread
        <= model.p("integration_convergence_max_spread_kg"),
        "circular_input_exclusion_passed": circular_check["passed"],
        "stress_family_has_zero_weight": all(
            row["likelihood_weight"] == 0.0 and not row["initializer_eligible"]
            for row in stress_result["profiles"]
        ),
        "canonical_initializer_eligible": False,
    }
    result: dict[str, Any] = {
        "schema_version": 1,
        "recreation_id": "ulich-v56-public-equation-discrepancy-v1",
        "scientific_model": {
            "id": model.document["model_id"],
            "eligibility": model.document["eligibility"],
            "fuel_flow_scale": model.p("fuel_flow_scale"),
            "workbook_tables_used": False,
            "parameter_document_sha256": sha256_file(DATA_DIR / "model_parameters.json"),
        },
        "input_identities": {
            "workbook_evidence_sha256": workbook_sha256,
            "official_acars_sha256": sha256_file(DATA_DIR / "official_acars.json"),
            "official_post_acars_sha256": sha256_file(DATA_DIR / "official_post_acars.json"),
            "stress_family_sha256": sha256_file(DATA_DIR / "stress_families.json"),
            "initializer_contract_sha256": sha256_file(DATA_DIR / "initializer_contract.json"),
            "public_performance_code_sha256": sha256_file(PACKAGE_ROOT / "src" / "public_performance.py"),
            "runner_code_sha256": sha256_file(PACKAGE_ROOT / "src" / "recreate.py"),
        },
        "official_anchor": acars["required_anchor"],
        "calculation_conventions": {
            "seconds_per_hour": model.p("seconds_per_hour"),
            "celsius_zero_kelvin": model.p("celsius_zero_kelvin"),
            "feet_per_flight_level": model.p("feet_per_flight_level"),
        },
        "acars_validation": acars_result,
        "post_acars_comparison": post_result,
        "stress_family": stress_result,
        "numerical_convergence": {
            "runs": convergence,
            "spread_kg": spread,
            "acceptance_max_spread_kg": model.p("integration_convergence_max_spread_kg"),
        },
        "circular_input_exclusion": circular_check,
        "validation": validations,
        "initializer_contract": {
            "interface_id": contract["interface_id"],
            "integration_status": contract["integration_status"],
            "blocker_ids": [row["id"] for row in contract["blockers"]],
        },
        "interpretation": {
            "acars_total_agreement": "error-cancellation-not-uniform-accuracy",
            "post_acars_discrepancy": "reproduced-not-tuned",
            "official_post_acars_role": "calculated-comparator-not-measurement",
            "pulau_perak_role": "unweighted-stress-only",
        },
    }
    fingerprint_payload = dict(result)
    result["scientific_fingerprint_sha256"] = hashlib.sha256(
        canonical_json_bytes(fingerprint_payload)
    ).hexdigest()
    return result


def write_checksums() -> None:
    paths = []
    for path in PACKAGE_ROOT.rglob("*"):
        if not path.is_file():
            continue
        relative = path.relative_to(PACKAGE_ROOT)
        if relative.as_posix() == "SHA256SUMS" or "__pycache__" in relative.parts:
            continue
        paths.append((relative.as_posix(), path))
    lines = [f"{sha256_file(path)}  {relative}" for relative, path in sorted(paths)]
    (PACKAGE_ROOT / "SHA256SUMS").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--workbook",
        type=Path,
        required=True,
        help="preserved 9M-MRO Fuel Model V5.6 .xlsm; read-only and never executed",
    )
    parser.add_argument(
        "--reference-workbook",
        type=Path,
        help="optional public V5.6 artifact for a side-by-side range-hash audit",
    )
    arguments = parser.parse_args()
    start_wall = time.perf_counter()
    start_usage = resource.getrusage(resource.RUSAGE_SELF)

    if not arguments.workbook.is_file():
        parser.error(f"workbook does not exist: {arguments.workbook}")
    if arguments.reference_workbook is not None and not arguments.reference_workbook.is_file():
        parser.error(f"reference workbook does not exist: {arguments.reference_workbook}")
    OUTPUT_DIR.mkdir(exist_ok=True)

    pins = load_json(DATA_DIR / "workbook_pins.json")
    audit = audit_workbook(arguments.workbook, pins, arguments.reference_workbook)
    if not audit["audit_passed"]:
        raise RuntimeError("workbook audit failed; no scientific outputs were regenerated")

    model = PublicPerformanceModel.from_json(DATA_DIR / "model_parameters.json")
    acars = load_json(DATA_DIR / "official_acars.json")
    official = load_json(DATA_DIR / "official_post_acars.json")
    stress = load_json(DATA_DIR / "stress_families.json")
    contract = load_json(DATA_DIR / "initializer_contract.json")
    sources = load_json(DATA_DIR / "source_manifest.json")
    results = build_results(
        model, acars, official, stress, contract, audit["file"]["sha256"]
    )
    required_checks = [
        value
        for key, value in results["validation"].items()
        if key != "canonical_initializer_eligible"
    ]
    if not all(required_checks):
        raise RuntimeError(f"recreation validation failed: {results['validation']}")

    write_json(OUTPUT_DIR / "workbook_audit.json", audit)
    write_json(OUTPUT_DIR / "results.json", results)
    (OUTPUT_DIR / "report.html").write_text(
        render_report(results, audit, sources), encoding="utf-8"
    )

    end_usage = resource.getrusage(resource.RUSAGE_SELF)
    metrics = {
        "schema_version": 1,
        "run_specific_not_in_scientific_fingerprint": True,
        "wall_time_s": time.perf_counter() - start_wall,
        "user_cpu_s": end_usage.ru_utime - start_usage.ru_utime,
        "system_cpu_s": end_usage.ru_stime - start_usage.ru_stime,
        "peak_resident_memory_kib": end_usage.ru_maxrss,
        "peak_resident_memory_bytes": end_usage.ru_maxrss * 1024,
        "python": platform.python_version(),
        "platform": platform.platform(),
        "workbook_sha256": audit["file"]["sha256"],
        "scientific_fingerprint_sha256": results["scientific_fingerprint_sha256"],
        "process_id_recorded": False,
    }
    write_json(OUTPUT_DIR / "execution_metrics.json", metrics)
    write_checksums()

    print(
        json.dumps(
            {
                "audit_passed": audit["audit_passed"],
                "scientific_fingerprint_sha256": results["scientific_fingerprint_sha256"],
                "acars_total_error_kg": results["acars_validation"][
                    "total_error_predicted_minus_observed_kg"
                ],
                "acars_interval_rmse_kg": results["acars_validation"]["interval_rmse_kg"],
                "arc1_overburn_kg": results["post_acars_comparison"][
                    "overburn_vs_official_calculation_kg"
                ],
                "initializer_status": contract["integration_status"],
                "wall_time_s": metrics["wall_time_s"],
                "peak_resident_memory_kib": metrics["peak_resident_memory_kib"],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
