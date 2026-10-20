#!/usr/bin/env python3
"""Run frozen WSPR/PHaRLAP route jobs with an immutable resumable cache."""

from __future__ import annotations

import argparse
import concurrent.futures
import copy
import datetime as dt
import hashlib
import json
import multiprocessing
import os
import platform
import sys
import tempfile
import time
import traceback
from pathlib import Path
from typing import Any, Iterable, Mapping


CODE_DIRECTORY = Path(__file__).resolve().parent
sys.path.insert(0, str(CODE_DIRECTORY))

import pharlap_raytrace_worker as ray_worker
import wspr_pharlap_control as control


CACHE_SCHEMA = "mh370.wspr.pharlap.cached-route.v1"
MANIFEST_SCHEMA = "mh370.wspr.pharlap.batch-manifest.v1"
PRIMARY_FAN_PROVENANCE = (
    "Frozen primary convergence fan: 0.5--15.0 degrees inclusive by 0.1 "
    "degree, then 15.5--89.5 degrees inclusive by 0.5 degree; declared before "
    "propagation filtering and independent of aircraft truth."
)
MAX_PROCESSES = 5


class BatchError(RuntimeError):
    """The batch input, cache, or dependency identity is invalid."""


def canonical_json(value: object, *, pretty: bool = False) -> bytes:
    options: dict[str, object] = {
        "sort_keys": True,
        "allow_nan": False,
    }
    if pretty:
        options["indent"] = 2
    else:
        options["separators"] = (",", ":")
    return (json.dumps(value, **options) + "\n").encode("utf-8")


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def tree_identity(root: Path) -> dict[str, object]:
    if not root.is_dir():
        raise BatchError(f"required data directory not found: {root}")
    digest = hashlib.sha256()
    file_count = 0
    byte_count = 0
    for path in sorted(item for item in root.rglob("*") if item.is_file()):
        relative = path.relative_to(root).as_posix()
        identity = sha256_file(path)
        size = path.stat().st_size
        digest.update(relative.encode("utf-8"))
        digest.update(b"\0")
        digest.update(str(size).encode("ascii"))
        digest.update(b"\0")
        digest.update(identity.encode("ascii"))
        digest.update(b"\n")
        file_count += 1
        byte_count += size
    return {
        "algorithm": "sorted-relative-path-null-size-null-file-sha256-newline",
        "sha256": digest.hexdigest(),
        "file_count": file_count,
        "byte_count": byte_count,
    }


def atomic_write(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".tmp", dir=path.parent
    )
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary_name, path)
    except BaseException:
        try:
            os.unlink(temporary_name)
        except FileNotFoundError:
            pass
        raise


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec="milliseconds").replace(
        "+00:00", "Z"
    )


def dependency_identity(
    pharlap_home: Path, iri_library: Path, ray_library: Path
) -> tuple[dict[str, object], dict[str, object]]:
    for label, path in (
        ("IRI library", iri_library),
        ("ray library", ray_library),
    ):
        if not path.is_file():
            raise BatchError(f"{label} not found: {path}")
    release_candidates = (
        pharlap_home / "RELEASE_NOTES.txt",
        pharlap_home / "00README.txt",
    )
    release_files = {
        path.name: sha256_file(path) for path in release_candidates if path.is_file()
    }
    identity: dict[str, object] = {
        "pharlap_release_files_sha256": release_files,
        "pharlap_iri2020_data_tree": tree_identity(pharlap_home / "dat" / "iri2020"),
        "iri_library_sha256": sha256_file(iri_library),
        "ray_library_sha256": sha256_file(ray_library),
        "ray_worker_source_sha256": sha256_file(CODE_DIRECTORY / "pharlap_raytrace_worker.py"),
        "control_source_sha256": sha256_file(CODE_DIRECTORY / "wspr_pharlap_control.py"),
    }
    paths: dict[str, object] = {
        "pharlap_home": str(pharlap_home.resolve()),
        "iri_library": str(iri_library.resolve()),
        "ray_library": str(ray_library.resolve()),
    }
    return identity, paths


def immutable_job_identity(
    raw_job: Mapping[str, object], dependencies: Mapping[str, object]
) -> dict[str, object]:
    return {
        "schema": "mh370.wspr.pharlap.immutable-job.v1",
        "job": raw_job,
        "scientific_dependencies": dependencies,
    }


def job_hash(
    raw_job: Mapping[str, object], dependencies: Mapping[str, object]
) -> str:
    return sha256_bytes(canonical_json(immutable_job_identity(raw_job, dependencies)))


def cache_path(output_directory: Path, identity: str) -> Path:
    return output_directory / "results" / identity[:2] / f"{identity}.json"


def read_cached_result(path: Path, expected_hash: str) -> dict[str, object] | None:
    if not path.exists():
        return None
    try:
        document = json.loads(path.read_text())
    except (OSError, json.JSONDecodeError) as error:
        raise BatchError(f"unreadable cache entry {path}: {error}") from error
    if document.get("schema") != CACHE_SCHEMA:
        raise BatchError(f"unexpected cache schema in {path}")
    if document.get("job_hash") != expected_hash:
        raise BatchError(f"cache filename/content identity mismatch in {path}")
    immutable_identity = document.get("immutable_identity")
    if not isinstance(immutable_identity, dict) or sha256_bytes(
        canonical_json(immutable_identity)
    ) != expected_hash:
        raise BatchError(f"cache immutable identity does not hash to its key: {path}")
    result = document.get("worker_result")
    if not isinstance(result, dict) or result.get("schema") != control.WORKER_RESULT_SCHEMA:
        raise BatchError(f"cache entry has no valid worker result: {path}")
    route_result = document.get("route_result")
    if not isinstance(route_result, dict) or route_result.get("schema") != control.ROUTE_RESULT_SCHEMA:
        raise BatchError(f"cache entry has no valid route result: {path}")
    return document


def load_complete_route_documents(
    output_directory: Path,
) -> tuple[dict[str, object], tuple[dict[str, object], ...]]:
    """Load a production cache only when every planned job is complete."""
    manifest_path = output_directory / "manifest.json"
    try:
        manifest = json.loads(manifest_path.read_text())
    except (OSError, json.JSONDecodeError) as error:
        raise BatchError(f"cannot read batch manifest {manifest_path}: {error}") from error
    if manifest.get("schema") != MANIFEST_SCHEMA:
        raise BatchError("unexpected batch manifest schema")
    if manifest.get("status") != "complete":
        raise BatchError(
            f"batch manifest is not production-complete: {manifest.get('status')}"
        )
    scope = manifest.get("scope")
    execution = manifest.get("execution")
    jobs = manifest.get("jobs")
    if not isinstance(scope, dict) or not isinstance(execution, dict):
        raise BatchError("batch manifest lacks scope/execution metadata")
    total = int(scope.get("route_jobs_total", -1))
    selected = int(scope.get("route_jobs_selected", -1))
    if total < 1 or selected != total or scope.get("partial_job_limit") is not None:
        raise BatchError("batch manifest represents an incomplete job selection")
    if int(execution.get("failure_count", -1)) != 0:
        raise BatchError("batch manifest records failed jobs")
    if int(execution.get("successful_selected_jobs", -1)) != total:
        raise BatchError("batch success count does not equal the complete plan")
    if not isinstance(jobs, list) or len(jobs) != total:
        raise BatchError("batch job index is incomplete")

    root = output_directory.resolve()
    documents: list[dict[str, object]] = []
    seen: set[str] = set()
    for job in sorted(jobs, key=lambda value: int(value["sequence"])):
        if not isinstance(job, dict) or job.get("status") != "complete":
            raise BatchError("batch job index contains a non-complete job")
        identity = str(job.get("job_hash", ""))
        if identity in seen or len(identity) != 64:
            raise BatchError("batch job index contains a duplicate/invalid hash")
        seen.add(identity)
        path = (output_directory / str(job.get("result_path", ""))).resolve()
        try:
            path.relative_to(root)
        except ValueError as error:
            raise BatchError("batch cache path escapes the output directory") from error
        cached = read_cached_result(path, identity)
        if cached is None:
            raise BatchError(f"batch cache file is missing: {path}")
        route_result = cached["route_result"]
        assert isinstance(route_result, dict)
        documents.append(route_result)
    return manifest, tuple(documents)


def normalized_scientific_result(
    raw_result: Mapping[str, object],
) -> tuple[dict[str, object], dict[str, object]]:
    result = copy.deepcopy(dict(raw_result))
    execution = result.pop("execution", {})
    external = result.get("external_identity")
    if isinstance(external, dict):
        external.pop("pharlap_home", None)
        external.pop("iri_library_path", None)
        external.pop("ray_library_path", None)
    return result, dict(execution) if isinstance(execution, dict) else {}


def execute_worker(
    raw_job: dict[str, object],
    pharlap_home: str,
    iri_library: str,
    ray_library: str,
) -> dict[str, object]:
    import resource

    started = time.monotonic()
    result = ray_worker.run_job(
        raw_job, Path(pharlap_home), Path(iri_library), Path(ray_library)
    )
    scientific, native_timing = normalized_scientific_result(result)
    return {
        "worker_result": scientific,
        "native_timing": native_timing,
        "process_wall_seconds": time.monotonic() - started,
        "worker_peak_rss_kb": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
    }


def primary_jobs(
    candidate_path: Path,
    spot_path: Path,
    dataset_name: str,
) -> tuple[control.RoutePlan, list[dict[str, object]], list[float]]:
    pairs = control.read_candidate_pairs(candidate_path, dataset_name)
    spots = control.read_spot_records(spot_path)
    resolver = control.PublishedSphericalRouteResolver(
        include_auxiliary_diagnostics=False
    )
    plan = control.build_route_plan(pairs, spots, resolver)
    elevations = ray_worker.production_elevations_deg()
    if len(elevations) != 295:
        raise BatchError(f"primary elevation fan changed: {len(elevations)} rays")
    jobs = control.worker_job_inputs(
        plan,
        elevations_deg=elevations,
        elevation_fan_provenance=PRIMARY_FAN_PROVENANCE,
    )
    if len(jobs) != len(plan.jobs):
        raise BatchError("route plan and worker job counts differ")
    for raw_job in jobs:
        normalized = ray_worker.validate_and_normalize_job(raw_job)
        fan = normalized["elevation_fan"]
        if fan["definition"] != "explicit" or fan["elevations_deg"] != elevations:
            raise BatchError("worker did not retain the frozen primary elevation fan")
        reference = normalized["reference"]
        if reference.get("wspr_slot_midpoint_offset_seconds") != 56.242:
            raise BatchError("worker job does not use the frozen WSPR midpoint")
    return plan, jobs, elevations


def manifest_document(
    *,
    status: str,
    arguments: argparse.Namespace,
    plan: control.RoutePlan,
    all_jobs: list[dict[str, object]],
    selected: list[tuple[int, control.RouteJob, dict[str, object], str, Path]],
    dependencies: Mapping[str, object],
    dependency_paths: Mapping[str, object],
    elevations: list[float],
    started_utc: str,
    elapsed_seconds: float,
    cached_before_run: int,
    executed: int,
    failures: list[dict[str, object]],
    job_status: Mapping[str, Mapping[str, object]],
    external_identity: Mapping[str, object] | None,
) -> dict[str, object]:
    return {
        "schema": MANIFEST_SCHEMA,
        "status": status,
        "scope": {
            "dataset_name": arguments.dataset_name,
            "candidate_pairs": len(plan.pairs),
            "route_jobs_total": len(all_jobs),
            "route_jobs_selected": len(selected),
            "partial_job_limit": arguments.max_jobs,
            "truth_used_in_candidate_or_propagation_selection": False,
        },
        "inputs": {
            "candidate_pairs": {
                "path": str(arguments.candidate_pairs.resolve()),
                "sha256": sha256_file(arguments.candidate_pairs),
            },
            "spot_records": {
                "path": str(arguments.spot_records.resolve()),
                "sha256": sha256_file(arguments.spot_records),
            },
        },
        "scientific_settings": {
            "route_resolver": "PublishedSphericalRouteResolver",
            "earth_radius_km": control.PHARLAP_EARTH_RADIUS_KM,
            "elevation_fan": {
                "definition": "explicit nonuniform primary",
                "ray_count": len(elevations),
                "elevations_deg": elevations,
                "provenance": PRIMARY_FAN_PROVENANCE,
            },
            "aircraft_altitudes_km": [value / 2.0 for value in range(1, 27)],
            "maximum_hops": 10,
            "ionosphere_range_step_km": 25.0,
            "ionosphere_height_step_km": 3.0,
            "collision_frequency_model": (
                "zero; geometry/MUF feasibility only, not attenuation"
            ),
            "irregularities_enabled": False,
            "electron_density_5min_model": (
                "same as observation epoch; Doppler disabled"
            ),
            "worker_output_detail": "minima",
            "wspr_transmission_start_offset_seconds": 1.0,
            "wspr_transmission_duration_seconds": 110.484,
            "wspr_transmission_midpoint_offset_seconds": 56.242,
        },
        "scientific_dependencies": dependencies,
        "dependency_paths": dependency_paths,
        "worker_reported_external_identity": external_identity,
        "cache": {
            "schema": CACHE_SCHEMA,
            "directory": str((arguments.output_directory / "results").resolve()),
            "key": (
                "SHA-256 of canonical immutable worker job plus scientific "
                "dependency hashes; exactly one atomic result file per key"
            ),
        },
        "execution": {
            "started_utc": started_utc,
            "finished_utc": utc_now(),
            "elapsed_seconds": elapsed_seconds,
            "processes_requested": arguments.processes,
            "processes_hard_limit": MAX_PROCESSES,
            "cached_before_run": cached_before_run,
            "executed_this_run": executed,
            "successful_selected_jobs": sum(
                1 for value in job_status.values() if value.get("status") == "complete"
            ),
            "failure_count": len(failures),
            "failures": sorted(failures, key=lambda value: str(value["job_hash"])),
            "python": platform.python_version(),
        },
        "jobs": [
            {
                "sequence": sequence,
                "job_id": raw_job["job_id"],
                "job_hash": identity,
                "result_path": str(path.relative_to(arguments.output_directory)),
                **job_status.get(identity, {"status": "pending"}),
            }
            for sequence, _route, raw_job, identity, path in selected
        ],
        "runner_source_sha256": sha256_file(Path(__file__)),
    }


def write_manifest(
    path: Path,
    **values: object,
) -> None:
    atomic_write(path, canonical_json(manifest_document(**values), pretty=True))


def run_batch(arguments: argparse.Namespace) -> int:
    if not 1 <= arguments.processes <= MAX_PROCESSES:
        raise BatchError(f"--processes must lie in [1, {MAX_PROCESSES}]")
    if arguments.max_jobs is not None and arguments.max_jobs < 1:
        raise BatchError("--max-jobs must be positive")
    if arguments.manifest_every < 1:
        raise BatchError("--manifest-every must be positive")

    started = time.monotonic()
    started_utc = utc_now()
    plan, all_jobs, elevations = primary_jobs(
        arguments.candidate_pairs,
        arguments.spot_records,
        arguments.dataset_name,
    )
    dependencies, dependency_paths = dependency_identity(
        arguments.pharlap_home,
        arguments.iri_library,
        arguments.ray_library,
    )
    count = len(all_jobs) if arguments.max_jobs is None else arguments.max_jobs
    selected: list[
        tuple[int, control.RouteJob, dict[str, object], str, Path]
    ] = []
    seen_hashes: set[str] = set()
    for sequence, (route, raw_job) in enumerate(
        zip(plan.jobs[:count], all_jobs[:count]), start=1
    ):
        identity = job_hash(raw_job, dependencies)
        if identity in seen_hashes:
            raise BatchError(f"duplicate immutable job hash: {identity}")
        seen_hashes.add(identity)
        selected.append(
            (
                sequence,
                route,
                raw_job,
                identity,
                cache_path(arguments.output_directory, identity),
            )
        )

    manifest_path = arguments.output_directory / "manifest.json"
    job_status: dict[str, dict[str, object]] = {}
    pending = []
    cached_before_run = 0
    external_identity: dict[str, object] | None = None
    for item in selected:
        _sequence, _route, _raw_job, identity, result_path = item
        cached = read_cached_result(result_path, identity)
        if cached is None:
            pending.append(item)
        else:
            cached_before_run += 1
            original_execution = cached.get("execution")
            job_status[identity] = {
                "status": "complete",
                "source": "cache",
                **(
                    {"original_execution": original_execution}
                    if isinstance(original_execution, dict)
                    else {}
                ),
            }
            worker_result = cached["worker_result"]
            if isinstance(worker_result, dict):
                reported = worker_result.get("external_identity")
                if isinstance(reported, dict):
                    if external_identity is None:
                        external_identity = reported
                    elif reported != external_identity:
                        raise BatchError(
                            "cached worker dependency identity differs within batch"
                        )

    base_manifest_values: dict[str, object] = {
        "arguments": arguments,
        "plan": plan,
        "all_jobs": all_jobs,
        "selected": selected,
        "dependencies": dependencies,
        "dependency_paths": dependency_paths,
        "elevations": elevations,
        "started_utc": started_utc,
        "cached_before_run": cached_before_run,
        "job_status": job_status,
    }
    initial_status = "dry_run" if arguments.dry_run else "running"
    write_manifest(
        manifest_path,
        status=initial_status,
        elapsed_seconds=time.monotonic() - started,
        executed=0,
        failures=[],
        external_identity=external_identity,
        **base_manifest_values,
    )
    if arguments.dry_run:
        print(
            json.dumps(
                {
                    "status": "dry_run",
                    "route_jobs_total": len(all_jobs),
                    "route_jobs_selected": len(selected),
                    "cached": cached_before_run,
                    "pending": len(pending),
                    "manifest": str(manifest_path),
                },
                sort_keys=True,
            )
        )
        return 0

    failures: list[dict[str, object]] = []
    executed = 0
    context = multiprocessing.get_context("spawn")
    with concurrent.futures.ProcessPoolExecutor(
        max_workers=arguments.processes, mp_context=context
    ) as executor:
        futures = {
            executor.submit(
                execute_worker,
                raw_job,
                str(arguments.pharlap_home),
                str(arguments.iri_library),
                str(arguments.ray_library),
            ): item
            for item in pending
            for _sequence, _route, raw_job, _identity, _result_path in (item,)
        }
        for future in concurrent.futures.as_completed(futures):
            sequence, route, raw_job, identity, result_path = futures[future]
            executed += 1
            try:
                outcome = future.result()
                worker_result = outcome["worker_result"]
                route_result = control.adapt_worker_result(route, worker_result)
                reported = worker_result.get("external_identity")
                if isinstance(reported, dict):
                    if external_identity is None:
                        external_identity = reported
                    elif reported != external_identity:
                        raise BatchError(
                            "worker dependency identity changed within one batch"
                        )
                execution_record = {
                    "process_wall_seconds": outcome["process_wall_seconds"],
                    "worker_peak_rss_kb": outcome["worker_peak_rss_kb"],
                    "native_timing": outcome["native_timing"],
                }
                envelope = {
                    "schema": CACHE_SCHEMA,
                    "job_hash": identity,
                    "immutable_identity": immutable_job_identity(raw_job, dependencies),
                    "worker_result": worker_result,
                    "route_result": route_result,
                    "execution": execution_record,
                }
                atomic_write(result_path, canonical_json(envelope, pretty=True))
                job_status[identity] = {
                    "status": "complete",
                    "source": "executed",
                    **execution_record,
                }
            except BaseException as error:
                failure = {
                    "sequence": sequence,
                    "job_id": raw_job["job_id"],
                    "job_hash": identity,
                    "exception_type": type(error).__name__,
                    "message": str(error),
                    "traceback": "".join(
                        traceback.format_exception(type(error), error, error.__traceback__)
                    ),
                }
                failures.append(failure)
                job_status[identity] = {
                    "status": "failed",
                    "exception_type": type(error).__name__,
                    "message": str(error),
                }
            if executed % arguments.manifest_every == 0:
                write_manifest(
                    manifest_path,
                    status="running",
                    elapsed_seconds=time.monotonic() - started,
                    executed=executed,
                    failures=failures,
                    external_identity=external_identity,
                    **base_manifest_values,
                )

    complete = not failures and all(
        value.get("status") == "complete" for value in job_status.values()
    ) and len(job_status) == len(selected)
    status = (
        "partial_complete"
        if complete and arguments.max_jobs is not None
        else "complete" if complete else "failed"
    )
    write_manifest(
        manifest_path,
        status=status,
        elapsed_seconds=time.monotonic() - started,
        executed=executed,
        failures=failures,
        external_identity=external_identity,
        **base_manifest_values,
    )
    print(
        json.dumps(
            {
                "status": status,
                "route_jobs_selected": len(selected),
                "cached_before_run": cached_before_run,
                "executed": executed,
                "failures": len(failures),
                "elapsed_seconds": time.monotonic() - started,
                "manifest": str(manifest_path),
            },
            sort_keys=True,
        )
    )
    return 0 if complete else 1


def path_argument(environment_name: str) -> Path | None:
    value = os.environ.get(environment_name)
    return Path(value) if value else None


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate-pairs", type=Path, required=True)
    parser.add_argument("--spot-records", type=Path, required=True)
    parser.add_argument("--dataset-name", default="known-flight")
    parser.add_argument("--output-directory", type=Path, required=True)
    parser.add_argument(
        "--pharlap-home",
        type=Path,
        default=path_argument("PHARLAP_HOME"),
        required=path_argument("PHARLAP_HOME") is None,
    )
    parser.add_argument("--iri-library", type=Path, required=True)
    parser.add_argument("--ray-library", type=Path, required=True)
    parser.add_argument("--processes", type=int, default=min(2, os.cpu_count() or 1))
    parser.add_argument(
        "--max-jobs",
        type=int,
        help="run only the first N sorted jobs; explicit fixture/diagnostic only",
    )
    parser.add_argument("--manifest-every", type=int, default=25)
    parser.add_argument("--dry-run", action="store_true")
    return parser


def main() -> int:
    try:
        return run_batch(build_parser().parse_args())
    except (BatchError, ValueError, OSError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
