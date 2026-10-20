#!/usr/bin/env python3
"""Fail-closed provenance audit for a broad-flight release.

The audit joins the runner configuration, run manifest, suite summary, binary,
and spatial-report audit into one closed set of byte identities.  It is
deliberately stricter than the individual producers: a release must use the
canonical repeated-manoeuvre model, retain more than one numerical seed, and
must not substitute a legacy one-turn or fixed-track artifact.

The JSON result contains no clock time or host-dependent resolved paths.  The
same bytes and command-line path spellings therefore produce the same audit.
Exit status is zero only when every check passes, one for a completed audit
that refuses the release, and two for command-line usage errors.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import re
import sys
import tempfile
import tomllib
from typing import Any, Iterable


SCHEMA_ID = "mh370-broad-release-validation"
SCHEMA_VERSION = 1
EXPECTED_MODEL_FAMILY = "broad-powered-marked-jump-v1"
EXPECTED_COMMAND = "estimate-broad-flight"
EXPECTED_RUN_STATUS = "conditional_broad_filter_complete"
REPORT_SCHEMA_ID = "mh370-broad-flight-spatial-report"
SNAPSHOT_REPORT_SCHEMA_ID = "mh370-broad-snapshot-diagnostic"
CONDITIONAL_PROBABILITY_INTERPRETATION = (
    "conditional_on_declared_model_not_calibrated_true_probability"
)
SHA256_PATTERN = re.compile(r"[0-9a-f]{64}\Z")
LEGACY_PATTERN = re.compile(
    r"(?:^|[^a-z0-9])(?:one[-_ ]turn|single[-_ ]turn|fixed[-_ ]track|"
    r"fixed[-_ ]waypoint|fixed[-_ ]route)(?:$|[^a-z0-9])",
    re.IGNORECASE,
)


class DuplicateJsonKey(ValueError):
    """Raised when provenance JSON tries to hide a duplicate field."""


def _reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise DuplicateJsonKey(f"duplicate JSON key {key!r}")
        result[key] = value
    return result


def _reject_nonfinite_json(value: str) -> Any:
    raise ValueError(f"non-finite JSON number {value}")


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as stream:
        return json.load(
            stream,
            object_pairs_hook=_reject_duplicate_keys,
            parse_constant=_reject_nonfinite_json,
        )


def load_top_level_json_members(
    path: Path,
    names: Iterable[str],
    *,
    prefix_limit_bytes: int = 16 * 1024 * 1024,
) -> dict[str, Any]:
    """Decode selected early members without materializing a particle array.

    Canonical broad handoffs put compact provenance before ``particles``.  A
    bounded parser keeps release validation practical for production handoffs;
    failing to find the provenance within the bound refuses the artifact.
    """

    wanted = set(names)
    with path.open("r", encoding="utf-8") as stream:
        text = stream.read(prefix_limit_bytes + 1)
    if len(text.encode("utf-8")) > prefix_limit_bytes:
        text = text[:prefix_limit_bytes]
    decoder = json.JSONDecoder(
        object_pairs_hook=_reject_duplicate_keys,
        parse_constant=_reject_nonfinite_json,
    )

    def whitespace(index: int) -> int:
        while index < len(text) and text[index].isspace():
            index += 1
        return index

    index = whitespace(0)
    if index >= len(text) or text[index] != "{":
        raise ValueError("top-level JSON value is not an object")
    index += 1
    found: dict[str, Any] = {}
    while True:
        index = whitespace(index)
        if index >= len(text):
            break
        if text[index] == "}":
            break
        try:
            key, index = decoder.raw_decode(text, index)
        except json.JSONDecodeError as error:
            raise ValueError("cannot decode a top-level provenance key") from error
        if not isinstance(key, str):
            raise ValueError("top-level JSON member name is not a string")
        index = whitespace(index)
        if index >= len(text) or text[index] != ":":
            raise ValueError("top-level JSON member lacks a colon")
        index = whitespace(index + 1)
        try:
            value, index = decoder.raw_decode(text, index)
        except json.JSONDecodeError as error:
            raise ValueError(
                f"top-level provenance member {key!r} is not complete within "
                f"{prefix_limit_bytes} bytes"
            ) from error
        if key in found:
            raise DuplicateJsonKey(f"duplicate JSON key {key!r}")
        if key in wanted:
            found[key] = value
            if set(found) == wanted:
                return found
        index = whitespace(index)
        if index >= len(text):
            break
        if text[index] == ",":
            index += 1
            continue
        if text[index] == "}":
            break
        raise ValueError("invalid top-level JSON member delimiter")
    missing = ", ".join(sorted(wanted - set(found)))
    raise ValueError(f"missing early top-level provenance member(s): {missing}")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def is_sha256(value: Any) -> bool:
    return isinstance(value, str) and SHA256_PATTERN.fullmatch(value) is not None


def is_int(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def finite_positive(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value) and value > 0.0


def portable_relative_path(value: Any) -> bool:
    if not isinstance(value, str) or not value or "\\" in value:
        return False
    path = Path(value)
    return not path.is_absolute() and all(part not in {"", ".", ".."} for part in path.parts)


def resolve_inside(root: Path, logical_path: str) -> Path | None:
    if not portable_relative_path(logical_path):
        return None
    try:
        root = root.resolve(strict=True)
        result = (root / logical_path).resolve(strict=True)
    except OSError:
        return None
    if not result.is_file() or not result.is_relative_to(root):
        return None
    return result


def resolve_from_file(reference_file: Path, logical_path: Any) -> Path | None:
    if not isinstance(logical_path, str) or not logical_path:
        return None
    path = Path(logical_path)
    candidate = path if path.is_absolute() else reference_file.parent / path
    try:
        candidate = candidate.resolve(strict=True)
    except OSError:
        return None
    return candidate if candidate.is_file() else None


def expected_run_identity(
    config_sha256: str,
    family: str,
    seed: int,
    input_sha256: dict[str, str],
) -> str:
    inputs = "\n".join(f"{name}={input_sha256[name]}" for name in sorted(input_sha256))
    payload = f"mh370-broad-filter-v1\n{config_sha256}\n{family}\n{seed}\n{inputs}"
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def json_safe(value: Any) -> Any:
    if isinstance(value, float) and not math.isfinite(value):
        return str(value)
    if isinstance(value, dict):
        return {str(key): json_safe(item) for key, item in value.items()}
    if isinstance(value, set):
        return [json_safe(item) for item in sorted(value, key=repr)]
    if isinstance(value, (list, tuple)):
        return [json_safe(item) for item in value]
    if isinstance(value, Path):
        return str(value)
    return value


def collect_strings(value: Any) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, dict):
        result = [str(key) for key in value]
        for item in value.values():
            result.extend(collect_strings(item))
        return result
    if isinstance(value, list):
        result: list[str] = []
        for item in value:
            result.extend(collect_strings(item))
        return result
    return []


class Checks:
    def __init__(self) -> None:
        self.items: list[dict[str, Any]] = []

    def add(
        self,
        check_id: str,
        passed: bool,
        *,
        expected: Any,
        observed: Any,
        detail: str,
    ) -> None:
        self.items.append(
            {
                "id": check_id,
                "status": "passed" if passed else "failed",
                "expected": json_safe(expected),
                "observed": json_safe(observed),
                "detail": detail,
            }
        )

    def failed(self) -> bool:
        return any(item["status"] != "passed" for item in self.items)


def refused_audit(checks: Checks, detail: str) -> dict[str, Any]:
    checks.add(
        "inputs.parseable",
        False,
        expected="valid JSON/TOML files",
        observed="invalid",
        detail=detail,
    )
    return finish_audit(checks, {})


def finish_audit(checks: Checks, identities: dict[str, Any]) -> dict[str, Any]:
    passed = not checks.failed()
    return {
        "schema_id": SCHEMA_ID,
        "schema_version": SCHEMA_VERSION,
        "status": "passed" if passed else "failed",
        "release_eligible": passed,
        "required_model_family": EXPECTED_MODEL_FAMILY,
        "identities": identities,
        "checks": checks.items,
    }


def configured_input_paths(config: dict[str, Any]) -> tuple[dict[str, str], list[str]]:
    errors: list[str] = []
    result: dict[str, str] = {}
    inputs = config.get("inputs")
    if not isinstance(inputs, dict):
        return {}, ["configuration inputs is not an object"]
    mappings = {
        "satcom_observations": "observations",
        "satellite_ephemeris": "satellite_ephemeris",
        "era5": "era5",
        "igrf": "igrf",
    }
    for manifest_name, config_name in mappings.items():
        raw = inputs.get(config_name)
        if isinstance(raw, str) and raw:
            result[manifest_name] = raw
        else:
            errors.append(f"inputs.{config_name} is missing")

    guide_paths = []
    for name in ("fuel_exhaustion_selection_guide", "fuel_exhaustion_persistent_twist"):
        value = config.get(name)
        if value is not None:
            if not isinstance(value, dict):
                errors.append(f"{name} is not an object")
            else:
                raw = value.get("canonical_full_satcom_observations")
                if isinstance(raw, str) and raw:
                    guide_paths.append(raw)
                else:
                    errors.append(f"{name}.canonical_full_satcom_observations is missing")
    if guide_paths:
        if len(set(guide_paths)) != 1:
            errors.append("fuel guides do not use one canonical SATCOM input")
        else:
            result["fuel_guide_canonical_satcom_observations"] = guide_paths[0]
    return result, errors


def active_probability_entries(value: Any, item_name: str) -> tuple[list[dict[str, Any]], list[str]]:
    if not isinstance(value, list):
        return [], [f"{item_name} is not an array"]
    active: list[dict[str, Any]] = []
    errors: list[str] = []
    names: set[str] = set()
    total = 0.0
    for index, entry in enumerate(value):
        if not isinstance(entry, dict):
            errors.append(f"{item_name}[{index}] is not an object")
            continue
        name = entry.get("name")
        probability = entry.get("scientific_probability")
        if not isinstance(name, str) or not name.strip() or name in names:
            errors.append(f"{item_name}[{index}] has an invalid or duplicate name")
        else:
            names.add(name)
        if not finite_positive(probability):
            errors.append(f"{item_name}[{index}] has a non-positive scientific probability")
            continue
        total += float(probability)
        active.append(entry)
    if active and not math.isclose(total, 1.0, rel_tol=0.0, abs_tol=1.0e-9):
        errors.append(f"{item_name} scientific probabilities sum to {total:.17g}, not one")
    return active, errors


def validate_release(
    manifest_path: Path,
    summary_path: Path,
    config_path: Path,
    binary_path: Path,
    report_audit_path: Path,
) -> dict[str, Any]:
    checks = Checks()
    try:
        manifest = load_json(manifest_path)
        summary = load_json(summary_path)
        report = load_json(report_audit_path)
        with config_path.open("rb") as stream:
            config = tomllib.load(stream)
    except (OSError, UnicodeError, ValueError, json.JSONDecodeError, tomllib.TOMLDecodeError, DuplicateJsonKey) as error:
        return refused_audit(checks, f"{type(error).__name__}: {error}")
    if not all(isinstance(value, dict) for value in (manifest, summary, report, config)):
        return refused_audit(checks, "each top-level artifact must be an object/table")
    try:
        binary_digest = sha256(binary_path)
        config_digest = sha256(config_path)
        manifest_digest = sha256(manifest_path)
        summary_digest = sha256(summary_path)
        report_digest = sha256(report_audit_path)
    except OSError as error:
        return refused_audit(checks, f"cannot hash a supplied artifact: {error}")

    identities: dict[str, Any] = {
        "binary_sha256": binary_digest,
        "config_sha256": config_digest,
        "manifest_sha256": manifest_digest,
        "summary_sha256": summary_digest,
        "report_audit_sha256": report_digest,
    }
    report_schema = report.get("schema_id")
    snapshot_report = report_schema == SNAPSHOT_REPORT_SCHEMA_ID

    # The broad runner and current artifact schemas are intentionally exact.
    manifest_shape = (
        manifest.get("schema_version") == 1
        and manifest.get("command") == EXPECTED_COMMAND
        and manifest.get("status") == EXPECTED_RUN_STATUS
    )
    checks.add(
        "manifest.broad_runner_schema",
        manifest_shape,
        expected={"schema_version": 1, "command": EXPECTED_COMMAND, "status": EXPECTED_RUN_STATUS},
        observed={key: manifest.get(key) for key in ("schema_version", "command", "status")},
        detail="Only the canonical broad-flight runner is releasable.",
    )
    summary_shape = (
        summary.get("schema_version") == 1
        and summary.get("status") == EXPECTED_RUN_STATUS
        and summary.get("model_family") == EXPECTED_MODEL_FAMILY
    )
    checks.add(
        "summary.canonical_model_family",
        summary_shape,
        expected={"schema_version": 1, "status": EXPECTED_RUN_STATUS, "model_family": EXPECTED_MODEL_FAMILY},
        observed={key: summary.get(key) for key in ("schema_version", "status", "model_family")},
        detail="A one-turn or fixed-track summary cannot stand in for the marked-jump model.",
    )
    checks.add(
        "manifest.summary_status_agreement",
        manifest.get("status") == summary.get("status"),
        expected=manifest.get("status"),
        observed=summary.get("status"),
        detail="Manifest and suite summary must describe the same completed run.",
    )

    # Scientific support: multiple starting controls and recurring manoeuvres.
    raw_seeds = config.get("seeds")
    seeds = raw_seeds if isinstance(raw_seeds, list) and all(is_int(seed) for seed in raw_seeds) else []
    seed_ok = len(seeds) >= 2 and len(set(seeds)) == len(seeds)
    checks.add(
        "config.independent_seeds",
        seed_ok,
        expected="at least two distinct integer seeds",
        observed=seeds if seeds else raw_seeds,
        detail="A single numerical realization cannot establish repeatability.",
    )
    model = config.get("model") if isinstance(config.get("model"), dict) else {}
    initial_modes, initial_errors = active_probability_entries(model.get("initial_modes"), "model.initial_modes")
    distinct_initial_modes = sorted(
        {entry.get("mode") for entry in initial_modes if isinstance(entry.get("mode"), str) and entry.get("mode")}
    )
    initial_ok = len(initial_modes) >= 2 and len(distinct_initial_modes) >= 2 and not initial_errors
    checks.add(
        "config.multiple_initial_control_modes",
        initial_ok,
        expected="at least two distinct positive-probability modes summing to one",
        observed={"modes": distinct_initial_modes, "errors": initial_errors},
        detail="Initial control mode is structural uncertainty, not a fixed trajectory assumption.",
    )
    maneuver_families, maneuver_errors = active_probability_entries(
        model.get("maneuver_families"), "model.maneuver_families"
    )
    clocks: list[dict[str, Any]] = []
    event_modes: set[str] = set()
    for index, family in enumerate(maneuver_families):
        process = family.get("process")
        if not isinstance(process, dict):
            maneuver_errors.append(f"model.maneuver_families[{index}].process is missing")
            continue
        clock = process.get("lateral_clock")
        if not isinstance(clock, dict):
            maneuver_errors.append(f"model.maneuver_families[{index}] disables the lateral renewal clock")
            continue
        mean = clock.get("mean_interval_s")
        minimum = clock.get("minimum_interval_s")
        shape = clock.get("gamma_shape")
        clock_ok = finite_positive(mean) and finite_positive(minimum) and finite_positive(shape) and float(mean) > float(minimum)
        if not clock_ok:
            maneuver_errors.append(f"model.maneuver_families[{index}] has an invalid lateral renewal clock")
        clocks.append(
            {
                "name": family.get("name"),
                "mean_interval_s": mean,
                "minimum_interval_s": minimum,
                "gamma_shape": shape,
            }
        )
        weights = process.get("lateral_mode_weights")
        if isinstance(weights, dict):
            event_modes.update(
                str(name) for name, weight in weights.items() if finite_positive(weight)
            )
    integration = model.get("integration") if isinstance(model.get("integration"), dict) else {}
    maximum_events = integration.get("maximum_events_per_transition")
    recurring_ok = (
        len(maneuver_families) >= 2
        and len(clocks) == len(maneuver_families)
        and len(event_modes) >= 2
        and is_int(maximum_events)
        and maximum_events >= 2
        and not maneuver_errors
    )
    checks.add(
        "config.recurring_lateral_manoeuvres",
        recurring_ok,
        expected="at least two positive-probability manoeuvre families, recurring lateral clocks, two event modes, and event budget >=2",
        observed={
            "family_count": len(maneuver_families),
            "lateral_clocks": clocks,
            "event_modes": sorted(event_modes),
            "maximum_events_per_transition": maximum_events,
            "errors": maneuver_errors,
        },
        detail="The release must permit repeated turns rather than a single sampled turn.",
    )

    config_families_raw = config.get("families")
    config_family_ids = []
    if isinstance(config_families_raw, list):
        config_family_ids = [
            item.get("id") for item in config_families_raw if isinstance(item, dict) and isinstance(item.get("id"), str)
        ]
    family_ids_ok = bool(config_family_ids) and len(config_family_ids) == len(set(config_family_ids))
    checks.add(
        "config.evidence_families",
        family_ids_ok,
        expected="one or more unique evidence-family identifiers",
        observed=config_family_ids,
        detail="Evidence alternatives are compared by explicit family, never silently pooled.",
    )
    checks.add(
        "summary.configuration_name",
        isinstance(config.get("name"), str) and summary.get("name") == config.get("name"),
        expected=config.get("name"),
        observed=summary.get("name"),
        detail="Configuration and summary names must agree.",
    )

    # Binary and configuration bytes close against the run manifest.
    checks.add(
        "manifest.executable_hash",
        is_sha256(manifest.get("executable_sha256")) and manifest.get("executable_sha256") == binary_digest,
        expected=binary_digest,
        observed=manifest.get("executable_sha256"),
        detail="The supplied executable must be the producer recorded by the run.",
    )
    checks.add(
        "manifest.configuration_hash",
        is_sha256(manifest.get("config_sha256")) and manifest.get("config_sha256") == config_digest,
        expected=config_digest,
        observed=manifest.get("config_sha256"),
        detail="The supplied TOML bytes must be exactly those consumed by the runner.",
    )

    configured_paths, configured_path_errors = configured_input_paths(config)
    manifest_inputs = manifest.get("input_sha256")
    input_mismatches: list[dict[str, Any]] = []
    if not isinstance(manifest_inputs, dict):
        input_mismatches.append({"reason": "manifest input_sha256 is not an object"})
        manifest_inputs = {}
    if set(manifest_inputs) != set(configured_paths):
        input_mismatches.append(
            {"reason": "input key set differs", "configured": sorted(configured_paths), "manifest": sorted(manifest_inputs)}
        )
    for name in sorted(configured_paths):
        raw_path = configured_paths[name]
        input_path = resolve_from_file(config_path, raw_path)
        observed = manifest_inputs.get(name)
        if input_path is None:
            input_mismatches.append({"name": name, "reason": "configured input is missing", "path": raw_path})
            continue
        actual = sha256(input_path)
        if not is_sha256(observed) or actual != observed:
            input_mismatches.append({"name": name, "expected": actual, "observed": observed})
    input_mismatches.extend({"reason": error} for error in configured_path_errors)
    checks.add(
        "manifest.input_hash_closure",
        not input_mismatches,
        expected="all and only configured scientific inputs, byte-for-byte",
        observed=input_mismatches,
        detail="Every input identity in the manifest is recomputed from its configured path.",
    )

    # Close every manifest output to a file beneath the manifest directory.
    run_root = manifest_path.parent
    manifest_outputs = manifest.get("outputs")
    output_mismatches: list[dict[str, Any]] = []
    output_paths: dict[str, Path] = {}
    if not isinstance(manifest_outputs, dict) or not manifest_outputs:
        output_mismatches.append({"reason": "manifest outputs is empty or not an object"})
        manifest_outputs = {}
    for logical_path in sorted(manifest_outputs):
        expected_digest = manifest_outputs[logical_path]
        path = resolve_inside(run_root, logical_path)
        if path is None:
            output_mismatches.append({"path": logical_path, "reason": "unsafe, missing, or non-file output"})
            continue
        output_paths[logical_path] = path
        actual_digest = sha256(path)
        if not is_sha256(expected_digest) or actual_digest != expected_digest:
            output_mismatches.append({"path": logical_path, "expected": actual_digest, "observed": expected_digest})
    checks.add(
        "manifest.output_hash_closure",
        not output_mismatches,
        expected="every declared output hashes correctly inside the run directory",
        observed=output_mismatches,
        detail="No unverified output can be packaged as part of the run.",
    )
    canonical_summary = output_paths.get("summary.json")
    checks.add(
        "manifest.supplied_summary_is_output",
        canonical_summary is not None and canonical_summary == summary_path.resolve(),
        expected="manifest output summary.json",
        observed=("summary.json" if canonical_summary == summary_path.resolve() else "different path"),
        detail="The audited suite summary must be the run's own hashed summary output.",
    )

    expected_outputs = {"summary.json"}
    outputs_config = config.get("outputs") if isinstance(config.get("outputs"), dict) else {}
    output_flag_names = (
        "write_builtin_report_artifacts",
        "write_posterior_csv",
        "write_posterior_handoff",
        "write_observation_snapshot_csvs",
    )
    configured_output_flags = {
        name: outputs_config.get(name, name != "write_observation_snapshot_csvs")
        for name in output_flag_names
    }
    output_artifact_errors: list[str] = []
    if any(not isinstance(value, bool) for value in configured_output_flags.values()):
        output_artifact_errors.append("configuration output switches must be booleans")
    require_builtin = configured_output_flags["write_builtin_report_artifacts"] is True
    require_csv = configured_output_flags["write_posterior_csv"] is True
    require_handoff = configured_output_flags["write_posterior_handoff"] is True
    require_snapshots = configured_output_flags["write_observation_snapshot_csvs"] is True
    if snapshot_report:
        if not require_snapshots:
            output_artifact_errors.append(
                "snapshot diagnostic report requires write_observation_snapshot_csvs = true"
            )
        manifest_output_configuration = manifest.get("output_configuration")
        if manifest_output_configuration != configured_output_flags:
            output_artifact_errors.append(
                "manifest output_configuration differs from the resolved configuration switches"
            )
    elif not (require_builtin and require_csv and require_handoff):
        output_artifact_errors.append(
            "legacy spatial release requires built-in reports, posterior CSVs, and provenance handoffs"
        )
    for family in config_family_ids:
        if require_builtin:
            expected_outputs.update(
                {f"{family}/report.pdf", f"{family}/posterior.svg", f"{family}/posterior.png"}
            )
        for seed in seeds:
            prefix = f"{family}/seed-{seed}"
            expected_outputs.update(
                {f"{prefix}/summary.json", f"{prefix}/checkpoints.json"}
            )
            if require_csv:
                expected_outputs.add(f"{prefix}/posterior.csv")
            if require_handoff:
                expected_outputs.add(f"{prefix}/posterior-handoff.json")
            if require_snapshots:
                expected_outputs.add(f"{prefix}/observation-snapshots/index.json")
    missing_expected_outputs = sorted(expected_outputs - set(manifest_outputs))
    suppressed_outputs: list[str] = []
    for family in config_family_ids:
        if not require_builtin:
            for name in ("report.pdf", "posterior.svg", "posterior.png"):
                logical = f"{family}/{name}"
                if logical in manifest_outputs:
                    suppressed_outputs.append(logical)
        for seed in seeds:
            prefix = f"{family}/seed-{seed}"
            if not require_csv and f"{prefix}/posterior.csv" in manifest_outputs:
                suppressed_outputs.append(f"{prefix}/posterior.csv")
            if not require_handoff and f"{prefix}/posterior-handoff.json" in manifest_outputs:
                suppressed_outputs.append(f"{prefix}/posterior-handoff.json")
            if not require_snapshots and any(
                logical.startswith(f"{prefix}/observation-snapshots/")
                for logical in manifest_outputs
            ):
                suppressed_outputs.append(f"{prefix}/observation-snapshots/*")
    foreign_output_paths = []
    for logical_path in manifest_outputs:
        parts = Path(logical_path).parts
        if logical_path == "summary.json":
            continue
        if not parts or parts[0] not in config_family_ids:
            foreign_output_paths.append(logical_path)
        if len(parts) >= 2 and parts[1].startswith("seed-"):
            try:
                output_seed = int(parts[1][5:])
            except ValueError:
                foreign_output_paths.append(logical_path)
            else:
                if output_seed not in seeds:
                    foreign_output_paths.append(logical_path)
    checks.add(
        "manifest.complete_family_seed_artifacts",
        not missing_expected_outputs
        and not suppressed_outputs
        and not foreign_output_paths
        and not output_artifact_errors,
        expected=(
            "configured snapshot indices/populations plus seed checkpoints and summaries"
            if snapshot_report
            else "complete broad CSV, handoff, checkpoint, summary, and built-in report outputs"
        ),
        observed={
            "missing": missing_expected_outputs,
            "unexpected_suppressed": sorted(set(suppressed_outputs)),
            "foreign": sorted(set(foreign_output_paths)),
            "errors": output_artifact_errors,
        },
        detail="Artifact presence must follow the runner output switches; partial, cherry-picked, or cross-run sets are refused.",
    )

    # Suite and per-seed summaries must be a complete Cartesian family/seed set.
    summary_families = summary.get("families")
    summary_pairs: dict[tuple[str, int], dict[str, Any]] = {}
    summary_errors: list[str] = []
    summary_family_ids: list[str] = []
    if not isinstance(summary_families, list):
        summary_errors.append("summary families is not an array")
    else:
        for family_index, family in enumerate(summary_families):
            if not isinstance(family, dict) or not isinstance(family.get("id"), str):
                summary_errors.append(f"summary family {family_index} is invalid")
                continue
            family_id = family["id"]
            summary_family_ids.append(family_id)
            family_seeds = family.get("seeds")
            if not isinstance(family_seeds, list):
                summary_errors.append(f"summary family {family_id} has no seeds array")
                continue
            if len(seeds) >= 2 and not isinstance(family.get("independent_seed_pooling"), dict):
                summary_errors.append(f"summary family {family_id} lacks independent-seed pooling provenance")
            for item in family_seeds:
                if not isinstance(item, dict) or item.get("family") != family_id or not is_int(item.get("seed")):
                    summary_errors.append(f"summary family {family_id} has an invalid seed entry")
                    continue
                pair = (family_id, item["seed"])
                if pair in summary_pairs:
                    summary_errors.append(f"summary repeats {family_id}/seed-{item['seed']}")
                summary_pairs[pair] = item
    expected_pairs = {(family, seed) for family in config_family_ids for seed in seeds}
    if set(summary_pairs) != expected_pairs:
        summary_errors.append(
            f"summary pairs differ: expected {sorted(expected_pairs)}, observed {sorted(summary_pairs)}"
        )
    if summary_family_ids != config_family_ids:
        summary_errors.append(
            f"summary family order/content differs: expected {config_family_ids}, observed {summary_family_ids}"
        )
    for family, seed in sorted(expected_pairs):
        path = output_paths.get(f"{family}/seed-{seed}/summary.json")
        if path is None:
            continue
        try:
            item = load_json(path)
        except (OSError, ValueError, json.JSONDecodeError, DuplicateJsonKey) as error:
            summary_errors.append(f"cannot parse {family}/seed-{seed}/summary.json: {error}")
            continue
        if item != summary_pairs.get((family, seed)):
            summary_errors.append(f"suite and per-seed summary differ for {family}/seed-{seed}")
    checks.add(
        "summary.complete_family_seed_set",
        not summary_errors,
        expected=sorted(f"{family}/seed-{seed}" for family, seed in expected_pairs),
        observed=summary_errors,
        detail="Every configured numerical replicate must occur once and agree byte-semantically with its seed summary.",
    )

    manifest_pooling = manifest.get("independent_seed_pooling_by_family")
    pooling_ok = (
        isinstance(manifest_pooling, dict)
        and set(manifest_pooling) == set(config_family_ids)
        and all(isinstance(manifest_pooling.get(family), dict) for family in config_family_ids)
    )
    checks.add(
        "manifest.independent_seed_pooling",
        pooling_ok,
        expected=sorted(config_family_ids),
        observed=sorted(manifest_pooling) if isinstance(manifest_pooling, dict) else manifest_pooling,
        detail="Multi-seed pooling provenance must be recorded for every evidence family.",
    )

    # Each posterior handoff carries a run identity that binds family and seed.
    handoff_errors: list[str] = []
    if isinstance(manifest_inputs, dict) and all(is_sha256(value) for value in manifest_inputs.values()) and is_sha256(manifest.get("config_sha256")):
        for family, seed in sorted(expected_pairs):
            logical = f"{family}/seed-{seed}/posterior-handoff.json"
            path = output_paths.get(logical)
            if path is None:
                if require_handoff:
                    handoff_errors.append(f"configured handoff is missing: {logical}")
                continue
            try:
                handoff = load_top_level_json_members(path, {"run"})
            except (OSError, ValueError, json.JSONDecodeError, DuplicateJsonKey) as error:
                handoff_errors.append(f"cannot parse {logical}: {error}")
                continue
            run = handoff.get("run") if isinstance(handoff, dict) else None
            expected_identity = expected_run_identity(manifest["config_sha256"], family, seed, manifest_inputs)
            if not isinstance(run, dict) or (
                run.get("model_family") != EXPECTED_MODEL_FAMILY
                or run.get("seed") != seed
                or run.get("config_sha256") != manifest.get("config_sha256")
                or run.get("input_sha256") != manifest_inputs
                or run.get("run_identity_sha256") != expected_identity
            ):
                handoff_errors.append(f"run provenance mismatch in {logical}")
    elif require_handoff:
        handoff_errors.append("manifest cannot support handoff run-identity reconstruction")
    if not require_handoff:
        unexpected_handoffs = sorted(
            logical
            for logical in manifest_outputs
            if logical.endswith("/posterior-handoff.json")
        )
        if unexpected_handoffs:
            handoff_errors.append(
                f"handoffs are suppressed but present: {', '.join(unexpected_handoffs)}"
            )
    checks.add(
        "outputs.handoff_run_identity",
        not handoff_errors,
        expected=(
            "canonical model/config/input/family/seed identity in every configured handoff"
            if require_handoff
            else "handoff output explicitly suppressed and absent"
        ),
        observed={"configured": require_handoff, "errors": handoff_errors},
        detail="A path name alone is not accepted as family/seed provenance, and a suppressed handoff cannot pass vacuously if present.",
    )

    # Close and interpret the report generator's own audit.
    report_shape = report_schema in {REPORT_SCHEMA_ID, SNAPSHOT_REPORT_SCHEMA_ID} and report.get("schema_version") == 1
    checks.add(
        "report.audit_schema",
        report_shape,
        expected={"schema_id": [REPORT_SCHEMA_ID, SNAPSHOT_REPORT_SCHEMA_ID], "schema_version": 1},
        observed={key: report.get(key) for key in ("schema_id", "schema_version")},
        detail="Only the fail-closed broad spatial reporter audit is accepted.",
    )
    numerical = report.get("numerical_support")
    criteria = numerical.get("criteria") if isinstance(numerical, dict) else None
    report_gate_errors: list[str] = []
    calculated_status = None
    if not isinstance(criteria, list) or not criteria:
        report_gate_errors.append("numerical criteria are missing")
    else:
        statuses = [item.get("status") if isinstance(item, dict) else None for item in criteria]
        if any(status not in {"passed", "failed", "unassessed"} for status in statuses):
            report_gate_errors.append("a numerical criterion has an invalid status")
        else:
            calculated_status = "failed" if "failed" in statuses else "unassessed" if "unassessed" in statuses else "passed"
            failed_count = statuses.count("failed")
            unassessed_count = statuses.count("unassessed")
            if numerical.get("status") != calculated_status:
                report_gate_errors.append("numerical status does not follow its criteria")
            if not snapshot_report and (
                numerical.get("failed_criteria") != failed_count
                or numerical.get("unassessed_criteria") != unassessed_count
            ):
                report_gate_errors.append("numerical failure counts do not follow their criteria")
            if snapshot_report:
                if report.get("artifact_class") != "diagnostic":
                    report_gate_errors.append("snapshot report is not labelled diagnostic")
                if numerical.get("publication_eligible") is not False:
                    report_gate_errors.append("snapshot diagnostic claims publication eligibility")
                if "publication_eligible" in report and report.get("publication_eligible") is not False:
                    report_gate_errors.append("snapshot top level claims publication eligibility")
                expected_watermark = {
                    "failed": "FAILED NUMERICAL SUPPORT — DIAGNOSTIC ONLY",
                    "unassessed": "UNASSESSED NUMERICAL SUPPORT — DIAGNOSTIC ONLY",
                    "passed": "CONDITIONAL MODEL DIAGNOSTIC — NOT CALIBRATED",
                }.get(calculated_status)
                if numerical.get("watermark") != expected_watermark:
                    report_gate_errors.append("snapshot watermark does not follow numerical status")
            else:
                expected_eligible = calculated_status == "passed"
                if numerical.get("publication_eligible") is not expected_eligible:
                    report_gate_errors.append("nested publication eligibility does not follow numerical status")
                if report.get("publication_eligible") is not expected_eligible:
                    report_gate_errors.append("top-level publication eligibility does not follow numerical status")
                if calculated_status != "passed" and report.get("artifact_class") != "diagnostic":
                    report_gate_errors.append("failed or unassessed numerical support is not labelled diagnostic")
                if calculated_status != "passed" and (
                    report.get("publication_eligible") is not False
                    or numerical.get("publication_eligible") is not False
                ):
                    report_gate_errors.append("failed or unassessed report claims publication eligibility")
    checks.add(
        "report.numerical_gate",
        not report_gate_errors,
        expected="criteria-derived status; failures are diagnostic and never publication eligible",
        observed={"calculated_status": calculated_status, "errors": report_gate_errors},
        detail="A rendered diagnostic cannot turn a failed numerical assessment into a publication claim.",
    )
    conditional_semantics_ok = (
        not snapshot_report
        or report.get("probability_interpretation")
        == CONDITIONAL_PROBABILITY_INTERPRETATION
    )
    checks.add(
        "report.conditional_probability_interpretation",
        conditional_semantics_ok,
        expected=(
            CONDITIONAL_PROBABILITY_INTERPRETATION
            if snapshot_report
            else "not applicable to the legacy spatial audit schema"
        ),
        observed=(
            report.get("probability_interpretation")
            if snapshot_report
            else "not applicable"
        ),
        detail="The all-epoch diagnostic must not present a declared conditional model as calibrated true probability.",
    )
    checks.add(
        "report.no_structural_family_pooling",
        report.get("family_pooling") == "none",
        expected="none",
        observed=report.get("family_pooling"),
        detail="Numerical seeds may pool within a family; structural evidence families may not.",
    )

    if snapshot_report and isinstance(report.get("specification"), dict):
        report_spec_raw = report["specification"].get("path")
        report_spec_digest = report["specification"].get("sha256")
    else:
        report_spec_raw = report.get("specification_logical_path")
        report_spec_digest = report.get("specification_sha256")
    report_spec_path = resolve_from_file(report_audit_path, report_spec_raw)
    report_provenance_errors: list[str] = []
    if report_spec_path is None:
        report_provenance_errors.append("report specification is missing")
    elif not is_sha256(report_spec_digest) or sha256(report_spec_path) != report_spec_digest:
        report_provenance_errors.append("report specification hash mismatch")
    if snapshot_report and isinstance(report.get("generator"), dict):
        generator_raw = report["generator"].get("path")
        generator_digest = report["generator"].get("sha256")
    else:
        generator_raw = report.get("generator")
        generator_digest = report.get("generator_sha256")
    generator_path = resolve_from_file(report_audit_path, generator_raw)
    if generator_path is None:
        report_provenance_errors.append("report generator is missing")
    elif not is_sha256(generator_digest) or sha256(generator_path) != generator_digest:
        report_provenance_errors.append("report generator hash mismatch")
    report_outputs = report.get("outputs")
    if not isinstance(report_outputs, dict) or not report_outputs:
        report_provenance_errors.append("report outputs are empty or invalid")
    else:
        for logical in sorted(report_outputs):
            record = report_outputs[logical]
            if snapshot_report:
                raw_path = record.get("path") if isinstance(record, dict) else None
                expected_digest = record.get("sha256") if isinstance(record, dict) else None
                path = resolve_from_file(report_audit_path, raw_path)
                try:
                    inside_report = path is not None and path.is_relative_to(report_audit_path.parent.resolve(strict=True))
                except OSError:
                    inside_report = False
            else:
                expected_digest = record
                path = resolve_inside(report_audit_path.parent, logical)
                inside_report = path is not None
            if path is None or not inside_report:
                report_provenance_errors.append(f"report output is unsafe or missing: {logical}")
            elif not is_sha256(expected_digest) or sha256(path) != expected_digest:
                report_provenance_errors.append(f"report output hash mismatch: {logical}")
    checks.add(
        "report.provenance_hash_closure",
        not report_provenance_errors,
        expected="hashed specification, generator, and rendered outputs",
        observed=report_provenance_errors,
        detail="The report audit must close over the exact materials that produced it.",
    )

    truth_errors: list[str] = []
    if snapshot_report:
        report_specification: dict[str, Any] = {}
        if report_spec_path is not None:
            try:
                loaded_specification = load_json(report_spec_path)
            except (OSError, ValueError, json.JSONDecodeError, DuplicateJsonKey) as error:
                truth_errors.append(f"cannot parse snapshot report specification: {error}")
            else:
                if isinstance(loaded_specification, dict):
                    report_specification = loaded_specification
                else:
                    truth_errors.append("snapshot report specification is not an object")
        expected_truth_digest = report_specification.get("expected_truth_sha256")
        if expected_truth_digest is not None and not is_sha256(expected_truth_digest):
            truth_errors.append("report specification expected_truth_sha256 is invalid")
        truth_record = report.get("truth_input")
        if truth_record is None:
            if expected_truth_digest is not None:
                truth_errors.append("report specification requires held-back truth but audit has none")
            if report.get("truth_role") != "absent; no accuracy claims":
                truth_errors.append("truth-free report does not explicitly reject accuracy claims")
        elif not isinstance(truth_record, dict):
            truth_errors.append("truth_input is neither null nor an object")
        else:
            truth_path = resolve_from_file(report_audit_path, truth_record.get("path"))
            truth_digest = truth_record.get("sha256")
            if (
                truth_path is None
                or not is_sha256(truth_digest)
                or sha256(truth_path) != truth_digest
            ):
                truth_errors.append("held-back truth path/hash mismatch")
            if expected_truth_digest is not None and truth_digest != expected_truth_digest:
                truth_errors.append("held-back truth hash differs from report specification")
            if (
                report.get("truth_role")
                != "held back from inference and loaded only by reporter/scorer"
            ):
                truth_errors.append("held-back truth role is not explicit")
    checks.add(
        "report.truth_provenance",
        not truth_errors,
        expected=(
            "truth absent with no accuracy claims, or a hash-bound held-back truth input matching the specification"
            if snapshot_report
            else "not applicable to the legacy spatial report schema"
        ),
        observed=truth_errors,
        detail="Known-flight accuracy claims must remain bound to the exact truth bytes loaded only by the reporter.",
    )

    report_pairs: set[tuple[str, int]] = set()
    report_source_errors: list[str] = []
    report_family_ids: list[str] = []
    report_families = report.get("families")
    if not isinstance(report_families, list):
        report_source_errors.append("report families is not an array")
    elif report_spec_path is None:
        report_source_errors.append("report source paths cannot resolve without its specification")
    else:
        resolved_manifest_outputs = {path: logical for logical, path in output_paths.items()}
        for family in report_families:
            if not isinstance(family, dict) or not isinstance(family.get("id"), str):
                report_source_errors.append("report contains an invalid family")
                continue
            family_id = family["id"]
            report_family_ids.append(family_id)
            if family.get("seed_pooling") != "equal numerical-replicate weight within this family":
                report_source_errors.append(f"report family {family_id} has invalid seed-pooling semantics")
            if snapshot_report and family.get("scientific_family_pooling") != "none":
                report_source_errors.append(f"snapshot report family {family_id} pools scientific families")
            sources = family.get("sources")
            if not isinstance(sources, list):
                report_source_errors.append(f"report family {family_id} has no sources")
                continue
            for source in sources:
                if not isinstance(source, dict) or not is_int(source.get("seed")):
                    report_source_errors.append(f"report family {family_id} has an invalid source")
                    continue
                seed = source["seed"]
                pair = (family_id, seed)
                if pair in report_pairs:
                    report_source_errors.append(f"report repeats {family_id}/seed-{seed}")
                report_pairs.add(pair)
                if snapshot_report:
                    expected_prefix = f"{family_id}/seed-{seed}/"
                    expected_summary_path = output_paths.get(f"{expected_prefix}summary.json")
                    summary_record = source.get("summary")
                    source_summary_path = resolve_from_file(
                        report_audit_path if snapshot_report else report_spec_path,
                        summary_record.get("path") if isinstance(summary_record, dict) else None,
                    )
                    if (
                        not isinstance(summary_record, dict)
                        or source_summary_path is None
                        or expected_summary_path is None
                        or source_summary_path != expected_summary_path
                        or not is_sha256(summary_record.get("sha256"))
                        or sha256(source_summary_path) != summary_record.get("sha256")
                    ):
                        report_source_errors.append(f"snapshot report seed-summary mismatch for {family_id}/seed-{seed}")

                    index_record = source.get("snapshot_index")
                    index_path = resolve_from_file(
                        report_audit_path if snapshot_report else report_spec_path,
                        index_record.get("path") if isinstance(index_record, dict) else None,
                    )
                    expected_index_path = output_paths.get(
                        f"{expected_prefix}observation-snapshots/index.json"
                    )
                    if (
                        not isinstance(index_record, dict)
                        or index_path is None
                        or expected_index_path is None
                        or index_path != expected_index_path
                        or not is_sha256(index_record.get("sha256"))
                        or sha256(index_path) != index_record.get("sha256")
                    ):
                        report_source_errors.append(f"snapshot index mismatch for {family_id}/seed-{seed}")
                        continue

                    raw_snapshots = source.get("snapshots")
                    reported_snapshots: dict[
                        Path, tuple[str, str, str, tuple[str, ...]]
                    ] = {}
                    if not isinstance(raw_snapshots, list) or not raw_snapshots:
                        report_source_errors.append(f"snapshot list is missing for {family_id}/seed-{seed}")
                        continue
                    for snapshot_record in raw_snapshots:
                        if not isinstance(snapshot_record, dict):
                            report_source_errors.append(f"invalid snapshot record for {family_id}/seed-{seed}")
                            continue
                        snapshot_path = resolve_from_file(
                            report_audit_path if snapshot_report else report_spec_path,
                            snapshot_record.get("path"),
                        )
                        snapshot_digest = snapshot_record.get("sha256")
                        epoch = snapshot_record.get("epoch_id")
                        observation_kind = snapshot_record.get("observation_kind")
                        evidence_components = snapshot_record.get(
                            "enabled_evidence_components"
                        )
                        evidence_ledger_ok = (
                            isinstance(evidence_components, list)
                            and all(
                                component in {"bto", "bfo"}
                                for component in evidence_components
                            )
                            and len(evidence_components) == len(set(evidence_components))
                            and (
                                (
                                    observation_kind
                                    in {"checkpoint", "fuel_anchor"}
                                    and not evidence_components
                                )
                                or (
                                    observation_kind == "satcom"
                                    and bool(evidence_components)
                                )
                            )
                        )
                        manifest_logical = resolved_manifest_outputs.get(snapshot_path) if snapshot_path is not None else None
                        if (
                            snapshot_path is None
                            or not isinstance(epoch, str)
                            or not epoch
                            or not evidence_ledger_ok
                            or not is_sha256(snapshot_digest)
                            or sha256(snapshot_path) != snapshot_digest
                            or manifest_logical is None
                            or not manifest_logical.startswith(f"{expected_prefix}observation-snapshots/")
                        ):
                            report_source_errors.append(f"snapshot path/hash is not a same-run manifest output for {family_id}/seed-{seed}/{epoch}")
                            continue
                        if snapshot_path in reported_snapshots:
                            report_source_errors.append(f"snapshot path is repeated for {family_id}/seed-{seed}: {snapshot_path.name}")
                        reported_snapshots[snapshot_path] = (
                            epoch,
                            snapshot_digest,
                            observation_kind,
                            tuple(evidence_components),
                        )

                    try:
                        index = load_json(index_path)
                    except (OSError, ValueError, json.JSONDecodeError, DuplicateJsonKey) as error:
                        report_source_errors.append(f"cannot parse snapshot index for {family_id}/seed-{seed}: {error}")
                        continue
                    if not isinstance(index, dict) or (
                        index.get("schema") != "mh370-broad-observation-snapshot-index"
                        or index.get("schema_version") != 1
                        or index.get("family") != family_id
                        or index.get("seed") != seed
                    ):
                        report_source_errors.append(f"snapshot index identity mismatch for {family_id}/seed-{seed}")
                        continue
                    expected_reported_snapshots: dict[
                        Path, tuple[str, str, str, tuple[str, ...]]
                    ] = {}
                    indexed_population_paths: set[Path] = set()
                    entries = index.get("snapshots")
                    if not isinstance(entries, list):
                        report_source_errors.append(f"snapshot index entries are missing for {family_id}/seed-{seed}")
                        continue
                    for entry in entries:
                        if not isinstance(entry, dict):
                            report_source_errors.append(
                                f"snapshot index contains a non-object entry for {family_id}/seed-{seed}"
                            )
                            continue
                        observation_kind = entry.get("observation_kind")
                        if observation_kind not in {
                            "initial",
                            "fuel_anchor",
                            "satcom",
                            "checkpoint",
                        }:
                            report_source_errors.append(
                                f"snapshot index contains an invalid observation kind for {family_id}/seed-{seed}"
                            )
                            continue
                        raw_path = entry.get("path")
                        snapshot_path = resolve_from_file(index_path, raw_path)
                        snapshot_digest = entry.get("sha256")
                        epoch = entry.get("observation_id")
                        evidence_components = entry.get(
                            "enabled_evidence_components", []
                        )
                        evidence_ledger_ok = (
                            isinstance(evidence_components, list)
                            and all(
                                component in {"bto", "bfo"}
                                for component in evidence_components
                            )
                            and len(evidence_components) == len(set(evidence_components))
                            and (
                                (
                                    observation_kind == "satcom"
                                    and bool(evidence_components)
                                )
                                or (
                                    observation_kind != "satcom"
                                    and not evidence_components
                                )
                            )
                        )
                        manifest_logical = resolved_manifest_outputs.get(snapshot_path) if snapshot_path is not None else None
                        if (
                            snapshot_path is None
                            or not isinstance(epoch, str)
                            or not epoch
                            or not evidence_ledger_ok
                            or not is_sha256(snapshot_digest)
                            or sha256(snapshot_path) != snapshot_digest
                            or manifest_logical is None
                            or not manifest_logical.startswith(f"{expected_prefix}observation-snapshots/")
                        ):
                            report_source_errors.append(f"snapshot index contains an unbound SATCOM artifact for {family_id}/seed-{seed}/{epoch}")
                            continue
                        if snapshot_path in indexed_population_paths:
                            report_source_errors.append(
                                f"snapshot index repeats a population path for {family_id}/seed-{seed}: {snapshot_path.name}"
                            )
                        indexed_population_paths.add(snapshot_path)
                        if observation_kind in {
                            "satcom",
                            "checkpoint",
                            "fuel_anchor",
                        }:
                            reported_epoch = (
                                epoch.removeprefix("held-out-")
                                if observation_kind == "checkpoint"
                                else epoch
                            )
                            expected_reported_snapshots[snapshot_path] = (
                                reported_epoch,
                                snapshot_digest,
                                observation_kind,
                                tuple(evidence_components),
                            )
                    manifest_snapshot_paths = {
                        path
                        for logical, path in output_paths.items()
                        if logical.startswith(
                            f"{expected_prefix}observation-snapshots/"
                        )
                        and logical
                        != f"{expected_prefix}observation-snapshots/index.json"
                    }
                    if indexed_population_paths != manifest_snapshot_paths:
                        report_source_errors.append(
                            f"snapshot index/manifest population sets differ for {family_id}/seed-{seed}"
                        )
                    if reported_snapshots != expected_reported_snapshots:
                        report_source_errors.append(
                            f"snapshot report/index physical-epoch sets differ for {family_id}/seed-{seed}"
                        )
                    continue

                input_record = source.get("input")
                if not isinstance(input_record, dict):
                    report_source_errors.append(f"report source {family_id}/seed-{seed} lacks input provenance")
                    continue
                source_path = resolve_from_file(report_spec_path, input_record.get("logical_path"))
                if source_path is None or not is_sha256(input_record.get("sha256")) or sha256(source_path) != input_record.get("sha256"):
                    report_source_errors.append(f"report source hash/path mismatch for {family_id}/seed-{seed}")
                    continue
                summary_record = input_record.get("summary")
                expected_summary_path = output_paths.get(f"{family_id}/seed-{seed}/summary.json")
                if not isinstance(summary_record, dict):
                    report_source_errors.append(f"report source {family_id}/seed-{seed} lacks seed-summary provenance")
                else:
                    source_summary_path = resolve_from_file(report_spec_path, summary_record.get("logical_path"))
                    if (
                        source_summary_path is None
                        or expected_summary_path is None
                        or source_summary_path != expected_summary_path
                        or not is_sha256(summary_record.get("sha256"))
                        or sha256(source_summary_path) != summary_record.get("sha256")
                    ):
                        report_source_errors.append(f"report seed-summary mismatch for {family_id}/seed-{seed}")
                manifest_logical = resolved_manifest_outputs.get(source_path)
                if manifest_logical is not None:
                    expected_prefix = f"{family_id}/seed-{seed}/"
                    if not manifest_logical.startswith(expected_prefix):
                        report_source_errors.append(f"report source belongs to another manifest family/seed: {family_id}/seed-{seed}")
                elif source.get("source_format") in {"broad_impact_json", "broad_impact_parent_checkpoint_json"}:
                    try:
                        impact = load_top_level_json_members(source_path, {"parent"})
                    except (OSError, ValueError, json.JSONDecodeError, DuplicateJsonKey) as error:
                        report_source_errors.append(f"cannot parse terminal source for {family_id}/seed-{seed}: {error}")
                        continue
                    parent = impact.get("parent") if isinstance(impact, dict) else None
                    expected_handoff_logical = f"{family_id}/seed-{seed}/posterior-handoff.json"
                    expected_handoff_hash = manifest_outputs.get(expected_handoff_logical)
                    expected_identity = (
                        expected_run_identity(manifest["config_sha256"], family_id, seed, manifest_inputs)
                        if is_sha256(manifest.get("config_sha256")) and isinstance(manifest_inputs, dict) and all(is_sha256(value) for value in manifest_inputs.values())
                        else None
                    )
                    if not isinstance(parent, dict) or (
                        parent.get("model_family") != EXPECTED_MODEL_FAMILY
                        or parent.get("seed") != seed
                        or parent.get("config_sha256") != manifest.get("config_sha256")
                        or parent.get("input_sha256") != manifest_inputs
                        or parent.get("run_identity_sha256") != expected_identity
                        or parent.get("handoff_sha256") != expected_handoff_hash
                    ):
                        report_source_errors.append(f"terminal source parent belongs to another run: {family_id}/seed-{seed}")
                    parent_record = input_record.get("parent_handoff")
                    if parent_record is not None:
                        parent_path = resolve_from_file(report_spec_path, parent_record.get("logical_path") if isinstance(parent_record, dict) else None)
                        expected_handoff_path = output_paths.get(expected_handoff_logical)
                        if (
                            not isinstance(parent_record, dict)
                            or parent_path is None
                            or parent_path != expected_handoff_path
                            or parent_record.get("sha256") != expected_handoff_hash
                        ):
                            report_source_errors.append(f"terminal parent handoff path/hash mismatch: {family_id}/seed-{seed}")
                else:
                    report_source_errors.append(f"report source is not a hashed output of this run: {family_id}/seed-{seed}")
    if report_family_ids != config_family_ids:
        report_source_errors.append(
            f"report family order/content differs: expected {config_family_ids}, observed {report_family_ids}"
        )
    if report_pairs != expected_pairs:
        report_source_errors.append(
            f"report pairs differ: expected {sorted(expected_pairs)}, observed {sorted(report_pairs)}"
        )
    checks.add(
        "report.complete_same_run_family_seed_set",
        not report_source_errors,
        expected=sorted(f"{family}/seed-{seed}" for family, seed in expected_pairs),
        observed=report_source_errors,
        detail="Every report source must be an exact run output or a terminal descendant cryptographically tied to its broad parent.",
    )

    critical_strings: list[str] = collect_strings(config)
    for value in (
        config.get("name"),
        manifest.get("command"),
        manifest.get("status"),
        manifest.get("config_path"),
        summary.get("name"),
        summary.get("model_family"),
        report.get("title"),
    ):
        if isinstance(value, str):
            critical_strings.append(value)
    critical_strings.extend(str(value) for value in config_family_ids)
    critical_strings.extend(str(value) for value in distinct_initial_modes)
    critical_strings.extend(str(item.get("name", "")) for item in initial_modes)
    critical_strings.extend(str(item.get("name", "")) for item in maneuver_families)
    critical_strings.extend(str(value) for value in manifest_outputs)
    if isinstance(report_families, list):
        for family in report_families:
            if not isinstance(family, dict):
                continue
            critical_strings.append(str(family.get("id", "")))
            for source in family.get("sources", []) if isinstance(family.get("sources"), list) else []:
                if not isinstance(source, dict):
                    continue
                if isinstance(source.get("input"), dict):
                    critical_strings.append(str(source["input"].get("logical_path", "")))
                for key in ("snapshot_index", "summary"):
                    if isinstance(source.get(key), dict):
                        critical_strings.append(str(source[key].get("path", "")))
                for snapshot in source.get("snapshots", []) if isinstance(source.get("snapshots"), list) else []:
                    if isinstance(snapshot, dict):
                        critical_strings.append(str(snapshot.get("path", "")))
    legacy_hits = sorted({value for value in critical_strings if LEGACY_PATTERN.search(value)})
    checks.add(
        "release.no_legacy_fixed_trajectory_artifacts",
        not legacy_hits,
        expected="no one-turn, single-turn, fixed-track, fixed-waypoint, or fixed-route identities",
        observed=legacy_hits,
        detail="Legacy fixed-trajectory products cannot be substituted into a broad-flight release.",
    )

    return finish_audit(checks, identities)


def emit_audit(audit: dict[str, Any], output: Path | None) -> None:
    payload = json.dumps(audit, indent=2, sort_keys=True, allow_nan=False) + "\n"
    if output is None:
        sys.stdout.write(payload)
        return
    output.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(prefix=f".{output.name}.", dir=output.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary_name, output)
    except Exception:
        try:
            os.unlink(temporary_name)
        except OSError:
            pass
        raise


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True, help="broad run-manifest.json")
    parser.add_argument("--summary", type=Path, required=True, help="broad suite summary.json")
    parser.add_argument("--config", type=Path, required=True, help="broad runner TOML")
    parser.add_argument("--binary", type=Path, required=True, help="runner executable recorded by the manifest")
    parser.add_argument("--report-audit", type=Path, required=True, help="broad_flight_spatial_report.json")
    parser.add_argument("--output", type=Path, help="write audit atomically here instead of stdout")
    args = parser.parse_args(argv)
    audit = validate_release(args.manifest, args.summary, args.config, args.binary, args.report_audit)
    try:
        emit_audit(audit, args.output)
    except OSError as error:
        print(f"error: cannot write audit: {error}", file=sys.stderr)
        return 2
    return 0 if audit["release_eligible"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
