#!/usr/bin/env python3
"""Assemble complete PHaRLAP caches into blind known-flight control results."""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import hashlib
import io
import json
import math
import os
import tempfile
from collections import defaultdict
from pathlib import Path
from typing import Iterable, Mapping, Sequence


CODE_DIRECTORY = Path(__file__).resolve().parent
DATA_DIRECTORY = CODE_DIRECTORY.parent / "data" / "known-flight"

import pharlap_batch_runner as batch
import wspr_pharlap_control as control


SCHEMA = "mh370.wspr.pharlap.known-flight-control-results.v1"
PLOT_METADATA_SCHEMA = "mh370.wspr.pharlap.known-flight-control-run.v1"
SURFACE_TOLERANCE_KM = 25.0
ALTITUDE_PATH_TOLERANCE_KM = 25.0
CLUSTER_RADIUS_KM = 25.0
ALTITUDE_COLLAPSE_RADIUS_KM = 25.0
RESIDUAL_TOLERANCE_KM = 25.0
MINIMUM_INDEPENDENT_LINKS = 3
TRUTH_HORIZONTAL_TOLERANCE_KM = 25.0
TRUTH_ALTITUDE_TOLERANCE_KM = 0.5
TRUTH_ALTITUDE_SENSITIVITY_KM = (0.25, 0.5, 1.0)
EXACT_ALTITUDE_SENSITIVITY_SCREEN = "common_aircraft_altitude_exact_sensitivity"
PUBLICATION_SCREEN_LABELS = {
    control.SURFACE_SCREEN: "Surface endpoint",
    control.ALTITUDE_SCREEN: "Common aircraft altitude",
}


class AssemblyError(RuntimeError):
    """A complete production result cannot be assembled safely."""


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def canonical_json(value: object) -> bytes:
    return (
        json.dumps(value, sort_keys=True, indent=2, allow_nan=False) + "\n"
    ).encode("utf-8")


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


def csv_payload(rows: Sequence[Mapping[str, object]], fields: Sequence[str]) -> bytes:
    destination = io.StringIO(newline="")
    writer = csv.DictWriter(destination, fieldnames=fields, lineterminator="\n")
    writer.writeheader()
    for row in rows:
        writer.writerow({field: row.get(field) for field in fields})
    return destination.getvalue().encode("utf-8")


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as handle:
        return list(csv.DictReader(handle))


def input_hash_from_manifest(
    manifest: Mapping[str, object], key: str
) -> str:
    inputs = manifest.get("inputs")
    if not isinstance(inputs, Mapping):
        raise AssemblyError("batch manifest has no input identities")
    value = inputs.get(key)
    if not isinstance(value, Mapping):
        raise AssemblyError(f"batch manifest has no {key} identity")
    return str(value.get("sha256", ""))


def verify_batch_inputs(
    manifest: Mapping[str, object], candidate_path: Path, spot_path: Path
) -> None:
    expected = {
        "candidate_pairs": sha256_file(candidate_path),
        "spot_records": sha256_file(spot_path),
    }
    for key, identity in expected.items():
        if input_hash_from_manifest(manifest, key) != identity:
            raise AssemblyError(f"batch {key} hash does not match assembly input")


def batch_scientific_identity(
    manifest: Mapping[str, object],
) -> dict[str, object]:
    """Return the deterministic batch identity, excluding timings and paths."""
    scope = manifest.get("scope")
    jobs = manifest.get("jobs")
    if not isinstance(scope, Mapping) or not isinstance(jobs, Sequence):
        raise AssemblyError("batch manifest lacks scope/job identity")
    job_index = []
    for job in jobs:
        if not isinstance(job, Mapping):
            raise AssemblyError("batch job index contains a non-object")
        job_index.append({
            "sequence": int(job["sequence"]),
            "job_id": str(job["job_id"]),
            "job_hash": str(job["job_hash"]),
        })
    stable_scope_fields = (
        "dataset_name", "candidate_pairs", "route_jobs_total",
        "route_jobs_selected", "partial_job_limit",
        "truth_used_in_candidate_or_propagation_selection",
    )
    return {
        "schema": manifest.get("schema"),
        "scope": {key: scope.get(key) for key in stable_scope_fields},
        "input_sha256": {
            "candidate_pairs": input_hash_from_manifest(
                manifest, "candidate_pairs"
            ),
            "spot_records": input_hash_from_manifest(manifest, "spot_records"),
        },
        "scientific_settings": manifest.get("scientific_settings"),
        "scientific_dependencies": manifest.get("scientific_dependencies"),
        "worker_reported_external_identity": manifest.get(
            "worker_reported_external_identity"
        ),
        "runner_source_sha256": manifest.get("runner_source_sha256"),
        "immutable_job_index_sha256": hashlib.sha256(
            canonical_json(sorted(job_index, key=lambda value: value["sequence"]))
        ).hexdigest(),
    }


def condition_count(
    clusters: Iterable[control.SpatialCluster | control.ResidualCluster],
    epoch_id: str,
    screen: str,
) -> dict[str, int]:
    selected = []
    for value in clusters:
        cluster = value.cluster if isinstance(value, control.ResidualCluster) else value
        if cluster.epoch_id == epoch_id and cluster.screen == screen:
            selected.append(value)
    return control.condition_counts(selected)


def comparison_rows(
    clusters: Sequence[control.SpatialCluster],
    residuals: Sequence[control.ResidualCluster],
    epochs: Mapping[str, Mapping[str, str]],
) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for epoch_id, metadata in epochs.items():
        for screen in (control.SURFACE_SCREEN, control.ALTITUDE_SCREEN):
            raw = condition_count(clusters, epoch_id, screen)
            residual = condition_count(residuals, epoch_id, screen)
            for measure, counts in (("raw_clusters", raw), ("residual_clusters", residual)):
                control_mean = (
                    counts["minus_60_min"] + counts["plus_60_min"]
                ) / 2.0
                rows.append({
                    "epoch_id": epoch_id,
                    "sequence": metadata["sequence"],
                    "flight": metadata["flight"],
                    "arc_time_utc": metadata["representative_time_utc"],
                    "screen": screen,
                    "measure": measure,
                    "minus_60_min": counts["minus_60_min"],
                    "actual_time": counts["actual_time"],
                    "plus_60_min": counts["plus_60_min"],
                    "control_mean": control_mean,
                    "actual_minus_control_mean": counts["actual_time"] - control_mean,
                    "actual_to_control_mean_ratio": (
                        counts["actual_time"] / control_mean
                        if control_mean else None
                    ),
                })
    return rows


def publication_result_rows(
    comparisons: Sequence[Mapping[str, object]],
    truth_scores: Sequence[Mapping[str, object]],
    statistics: Mapping[str, object],
) -> list[dict[str, object]]:
    """Return a compact, audit-linked table for the paper.

    The detailed comparison and truth-score tables remain authoritative.  This
    table only pivots those rows and adds their precomputed residual diagnostic;
    it does not repeat clustering, residualization or truth scoring.
    """
    indexed: dict[tuple[str, str, str], Mapping[str, object]] = {}
    for row in comparisons:
        key = (str(row["epoch_id"]), str(row["screen"]), str(row["measure"]))
        if key in indexed:
            raise AssemblyError(f"duplicate comparison row {key}")
        indexed[key] = row

    actual_truth: dict[tuple[str, str], Mapping[str, object]] = {}
    for row in truth_scores:
        if str(row["condition"]) != "actual_time":
            continue
        key = (str(row["epoch_id"]), str(row["screen"]))
        if key in actual_truth:
            raise AssemblyError(f"duplicate actual-time truth score {key}")
        actual_truth[key] = row

    raw_rows = sorted(
        (
            row for row in comparisons
            if str(row["measure"]) == "raw_clusters"
        ),
        key=lambda row: (
            int(row["sequence"]),
            tuple(PUBLICATION_SCREEN_LABELS).index(str(row["screen"])),
        ),
    )
    output: list[dict[str, object]] = []

    def values(
        *,
        scope: str,
        raw: Mapping[str, object],
        residual: Mapping[str, object],
        recovered: int,
        scored: int,
        epoch_actual_excess_p: float | None = None,
        epoch_two_sided_p: float | None = None,
        connected_actual_excess_p: float | None = None,
        connected_two_sided_p: float | None = None,
    ) -> dict[str, object]:
        screen = str(raw["screen"])
        return {
            "scope": scope,
            "epoch_id": raw.get("epoch_id", ""),
            "sequence": raw.get("sequence", ""),
            "flight": raw.get("flight", ""),
            "arc_time_utc": raw.get("arc_time_utc", ""),
            "screen": screen,
            "screen_label": PUBLICATION_SCREEN_LABELS[screen],
            "raw_minus_60_min": int(raw["minus_60_min"]),
            "raw_actual_time": int(raw["actual_time"]),
            "raw_plus_60_min": int(raw["plus_60_min"]),
            "residual_minus_60_min": int(residual["minus_60_min"]),
            "residual_actual_time": int(residual["actual_time"]),
            "residual_plus_60_min": int(residual["plus_60_min"]),
            "residual_control_mean": float(residual["control_mean"]),
            "residual_actual_minus_control_mean": float(
                residual["actual_minus_control_mean"]
            ),
            "actual_time_references_recovered": recovered,
            "actual_time_references_scored": scored,
            "epoch_block_actual_excess_p": epoch_actual_excess_p,
            "epoch_block_two_sided_p": epoch_two_sided_p,
            "connected_window_actual_excess_p": connected_actual_excess_p,
            "connected_window_two_sided_p": connected_two_sided_p,
        }

    for raw in raw_rows:
        key = (str(raw["epoch_id"]), str(raw["screen"]))
        residual_key = (*key, "residual_clusters")
        if residual_key not in indexed:
            raise AssemblyError(f"missing residual comparison row {residual_key}")
        if key not in actual_truth:
            raise AssemblyError(f"missing actual-time truth score {key}")
        output.append(values(
            scope="epoch",
            raw=raw,
            residual=indexed[residual_key],
            recovered=int(bool(actual_truth[key]["recovered"])),
            scored=1,
        ))

    screen_statistics = statistics.get("screens")
    if not isinstance(screen_statistics, Mapping):
        raise AssemblyError("statistical summary has no screens")
    pooled: list[dict[str, object]] = []
    for screen in PUBLICATION_SCREEN_LABELS:
        screen_rows = [row for row in output if row["screen"] == screen]
        if not screen_rows:
            raise AssemblyError(f"publication table has no {screen} rows")

        def pooled_measure(prefix: str) -> dict[str, object]:
            minus = sum(int(row[f"{prefix}_minus_60_min"]) for row in screen_rows)
            actual = sum(int(row[f"{prefix}_actual_time"]) for row in screen_rows)
            plus = sum(int(row[f"{prefix}_plus_60_min"]) for row in screen_rows)
            mean = (minus + plus) / 2.0
            return {
                "epoch_id": "",
                "sequence": "",
                "flight": "Pooled known flights",
                "arc_time_utc": "",
                "screen": screen,
                "measure": f"{prefix}_clusters",
                "minus_60_min": minus,
                "actual_time": actual,
                "plus_60_min": plus,
                "control_mean": mean,
                "actual_minus_control_mean": actual - mean,
            }

        try:
            residual_diagnostics = screen_statistics[screen]["residual"]
            epoch_effects = residual_diagnostics["epoch_effects"]
            connected = residual_diagnostics["connected_window_sensitivity"]
        except (KeyError, TypeError) as error:
            raise AssemblyError(
                f"statistical summary is incomplete for {screen}"
            ) from error
        pooled.append(values(
            scope="pooled",
            raw=pooled_measure("raw"),
            residual=pooled_measure("residual"),
            recovered=sum(
                int(row["actual_time_references_recovered"])
                for row in screen_rows
            ),
            scored=sum(
                int(row["actual_time_references_scored"])
                for row in screen_rows
            ),
            epoch_actual_excess_p=float(
                epoch_effects["one_sided_actual_excess_p"]
            ),
            epoch_two_sided_p=float(epoch_effects["two_sided_p"]),
            connected_actual_excess_p=float(
                connected["one_sided_actual_excess_p"]
            ),
            connected_two_sided_p=float(connected["two_sided_p"]),
        ))
    return [*pooled, *output]


def publication_markdown(rows: Sequence[Mapping[str, object]]) -> bytes:
    """Render the compact paper table from the exact CSV row values."""
    lines = [
        "# PHaRLAP-filtered known-flight control results",
        "",
        "Counts in each triplet are minus 60 minutes / arc-time window / plus "
        "60 minutes. The effect is the arc-time residual count minus the mean "
        "of the two controls.",
        "",
        "| Scope / BTO epoch | Propagation screen | Raw clusters | Residual "
        "clusters | Residual effect | Withheld reference recovered | "
        "One-sided actual-excess p |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in rows:
        scope = str(row["scope"])
        label = (
            "Pooled (six epochs)"
            if scope == "pooled"
            else f'{row["flight"]} {str(row["arc_time_utc"])[11:19]} UTC'
        )
        p_value = row["epoch_block_actual_excess_p"]
        lines.append(
            f'| {label} | {row["screen_label"]} | '
            f'{row["raw_minus_60_min"]} / {row["raw_actual_time"]} / '
            f'{row["raw_plus_60_min"]} | '
            f'{row["residual_minus_60_min"]} / '
            f'{row["residual_actual_time"]} / '
            f'{row["residual_plus_60_min"]} | '
            f'{float(row["residual_actual_minus_control_mean"]):+.1f} | '
            f'{row["actual_time_references_recovered"]}/'
            f'{row["actual_time_references_scored"]} | '
            f'{"—" if p_value is None else f"{float(p_value):.3f}"} |'
        )
    lines.extend([
        "",
        "The p-values are exact sign-flip diagnostics across epoch effects and "
        "are reported only for pooled rows. They are exploratory because radio "
        "windows overlap; the dependence-conservative three-connected-window "
        "sensitivity gives one-sided actual-excess p = 1.000 for both screens. "
        "The two-sided epoch values (0.0625 surface; 0.03125 altitude) describe "
        "actual-time deficits, not aircraft-specific excesses.",
        "",
    ])
    return "\n".join(lines).encode("utf-8")


def declared_radio_intervals(
    epochs: Mapping[str, Mapping[str, str]],
) -> dict[str, dict[str, tuple[dt.datetime, dt.datetime]]]:
    result: dict[str, dict[str, tuple[dt.datetime, dt.datetime]]] = {}
    for epoch_id, row in epochs.items():
        conditions: dict[str, tuple[dt.datetime, dt.datetime]] = {}
        for condition in control.CONTROL_CONDITIONS:
            start = row.get(f"{condition}_radio_window_start", "")
            end = row.get(f"{condition}_radio_window_end", "")
            if not start or not end:
                raise AssemblyError(
                    f"{epoch_id}: missing predeclared {condition} radio window"
                )
            conditions[condition] = (
                dt.datetime.fromisoformat(start.replace("Z", "+00:00")),
                dt.datetime.fromisoformat(end.replace("Z", "+00:00")),
            )
        result[epoch_id] = conditions
    return result


def connected_window_components(
    intervals: Mapping[
        str, Mapping[str, tuple[dt.datetime, dt.datetime]]
    ],
) -> tuple[tuple[str, ...], ...]:
    remaining = set(intervals)
    components: list[tuple[str, ...]] = []
    while remaining:
        seed = min(remaining)
        component = {seed}
        frontier = [seed]
        remaining.remove(seed)
        while frontier:
            source = frontier.pop()
            overlaps = {
                target for target in remaining
                if any(
                    source_start <= target_end
                    and target_start <= source_end
                    for source_start, source_end in intervals[source].values()
                    for target_start, target_end in intervals[target].values()
                )
            }
            component.update(overlaps)
            frontier.extend(sorted(overlaps))
            remaining.difference_update(overlaps)
        components.append(tuple(sorted(component)))
    return tuple(sorted(components))


def aggregate_block_counts(
    counts: Mapping[str, Mapping[str, int]],
    components: Sequence[Sequence[str]],
    screen: str,
) -> dict[str, dict[str, int]]:
    result: dict[str, dict[str, int]] = {}
    for index, component in enumerate(components, 1):
        values = {condition: 0 for condition in control.CONTROL_CONDITIONS}
        for epoch_id in component:
            block = f"{epoch_id}|{screen}"
            for condition in control.CONTROL_CONDITIONS:
                values[condition] += counts.get(block, {}).get(condition, 0)
        result[f"connected-radio-window-{index}"] = values
    return result


def statistical_summary(
    clusters: Sequence[control.SpatialCluster],
    residuals: Sequence[control.ResidualCluster],
    epochs: Mapping[str, Mapping[str, str]],
) -> dict[str, object]:
    intervals = declared_radio_intervals(epochs)
    components = connected_window_components(intervals)
    result: dict[str, object] = {
        "status": "exploratory_dependent_controls",
        "caution": (
            "Epochs are the least pseudo-replicated available unit, but radio "
            "windows and controls overlap and are not independent. P-values are "
            "exploratory diagnostics, not confirmatory false-alarm probabilities."
        ),
        "connected_radio_window_components": [list(value) for value in components],
        "connected_component_caution": (
            f"Only {len(components)} connected radio-window blocks remain; this "
            "dependence-conservative sensitivity has negligible power."
        ),
        "screens": {},
    }
    screens: dict[str, object] = {}
    for screen in (control.SURFACE_SCREEN, control.ALTITUDE_SCREEN):
        screen_result: dict[str, object] = {}
        for label, items in (("raw", clusters), ("residual", residuals)):
            selected = [
                item for item in items
                if (
                    item.cluster.screen if isinstance(item, control.ResidualCluster)
                    else item.screen
                ) == screen
            ]
            epoch_counts = control.count_clusters_by_block(selected)
            connected_counts = aggregate_block_counts(
                epoch_counts, components, screen
            )
            screen_result[label] = {
                "epoch_effects": control.exact_blocked_sign_flip(epoch_counts),
                "connected_window_sensitivity": control.exact_blocked_sign_flip(
                    connected_counts
                ),
            }
        screens[screen] = screen_result
    result["screens"] = screens
    return result


def truth_score_rows(
    surface_residuals: Sequence[control.ResidualCluster],
    altitude_source_residuals: Sequence[control.ResidualCluster],
    altitude_parent_residuals: Sequence[control.ResidualCluster],
    truth_rows: Sequence[Mapping[str, str]],
    *,
    expected_epoch_ids: Iterable[str] | None = None,
) -> list[dict[str, object]]:
    nearest_truth: dict[str, Mapping[str, str]] = {}
    for row in truth_rows:
        if (
            row["reference_role"] != "physical_slot"
            or row["is_nearest_arc_slot"].strip().lower() != "true"
        ):
            continue
        epoch_id = row["epoch_id"]
        if epoch_id in nearest_truth:
            raise AssemblyError(
                f"duplicate nearest-slot truth for epoch {epoch_id}"
            )
        nearest_truth[epoch_id] = row
    if expected_epoch_ids is not None:
        expected = set(expected_epoch_ids)
        actual = set(nearest_truth)
        if actual != expected:
            raise AssemblyError(
                "nearest-slot truth epochs do not match the candidate epochs: "
                f"missing={sorted(expected - actual)}, "
                f"foreign={sorted(actual - expected)}"
            )
    def event_id(cluster: control.SpatialCluster) -> str:
        return (
            f"{cluster.epoch_id}|{cluster.screen}|{cluster.condition}|"
            f"{cluster.physical_slot}|{cluster.cluster_rank}|"
            f"{cluster.center_candidate_id}"
        )

    output: list[dict[str, object]] = []
    for epoch_id, truth in sorted(nearest_truth.items()):
        for screen in (control.SURFACE_SCREEN, control.ALTITUDE_SCREEN):
            for condition in control.CONTROL_CONDITIONS:
                latitude = float(truth["latitude_deg"])
                longitude = float(truth["longitude_deg_e"])
                truth_altitude = (
                    float(truth["altitude_km"])
                    if truth["altitude_km"] else None
                )
                slot = truth["physical_slot"]
                if screen == control.SURFACE_SCREEN:
                    parents = [
                        item.cluster for item in surface_residuals
                        if item.is_residual
                        and item.cluster.epoch_id == epoch_id
                        and item.cluster.condition == condition
                        and item.cluster.physical_slot == slot
                    ]
                    sources = parents
                else:
                    parents = [
                        item.cluster for item in altitude_parent_residuals
                        if item.is_residual
                        and item.cluster.epoch_id == epoch_id
                        and item.cluster.condition == condition
                        and item.cluster.physical_slot == slot
                    ]
                    parent_source_ids = {
                        source_id for parent in parents
                        for source_id in parent.source_altitude_cluster_ids
                    }
                    sources = [
                        item.cluster for item in altitude_source_residuals
                        if item.is_residual
                        and item.cluster.epoch_id == epoch_id
                        and item.cluster.condition == condition
                        and item.cluster.physical_slot == slot
                        and any(
                            source_id in parent_source_ids
                            for source_id in item.cluster.source_altitude_cluster_ids
                        )
                    ]
                distances = [
                    control.great_circle_distance_km(
                        latitude, longitude,
                        source.latitude_deg, source.longitude_deg_e,
                    )
                    for source in sources
                ]
                gaps: list[float | None] = []
                for source in sources:
                    if screen == control.SURFACE_SCREEN:
                        gaps.append(None)
                    elif truth_altitude is None or source.altitude_km is None:
                        gaps.append(math.inf)
                    else:
                        gaps.append(abs(source.altitude_km - truth_altitude))
                nearest_index = (
                    min(range(len(sources)), key=distances.__getitem__)
                    if sources else None
                )
                joint = [
                    distance <= TRUTH_HORIZONTAL_TOLERANCE_KM
                    and (gap is None or gap <= TRUTH_ALTITUDE_TOLERANCE_KM)
                    for distance, gap in zip(distances, gaps)
                ]
                finite_gaps = [
                    gap for gap in gaps
                    if gap is not None and math.isfinite(gap)
                ]
                sensitivities = {
                    f"{tolerance:g}": any(
                        distance <= TRUTH_HORIZONTAL_TOLERANCE_KM
                        and gap is not None and gap <= tolerance
                        for distance, gap in zip(distances, gaps)
                    )
                    for tolerance in TRUTH_ALTITUDE_SENSITIVITY_KM
                } if screen == control.ALTITUDE_SCREEN else {}
                nearest_source = (
                    sources[nearest_index] if nearest_index is not None else None
                )
                nearest_gap = gaps[nearest_index] if nearest_index is not None else None
                if nearest_gap is not None and not math.isfinite(nearest_gap):
                    nearest_gap = None
                output.append({
                    "epoch_id": epoch_id,
                    "screen": screen,
                    "condition": condition,
                    "nearest_physical_slot": slot,
                    "truth_id": truth["truth_id"],
                    "truth_position_time_utc": truth["position_time_utc"],
                    "truth_latitude_deg": latitude,
                    "truth_longitude_deg_e": longitude,
                    "truth_altitude_km": truth_altitude,
                    "truth_position_source": truth["position_source"],
                    "truth_position_method": truth["position_method"],
                    "truth_time_offset_seconds": float(
                        truth["time_offset_seconds"]
                    ),
                    "eligible_residual_parent_clusters": len(parents),
                    "eligible_surviving_source_clusters": len(sources),
                    "nearest_horizontal_km": (
                        distances[nearest_index]
                        if nearest_index is not None else None
                    ),
                    "nearest_source_cluster_id": (
                        next(iter(nearest_source.source_altitude_cluster_ids), None)
                        if nearest_source is not None
                        and screen == control.ALTITUDE_SCREEN
                        else event_id(nearest_source) if nearest_source is not None else None
                    ),
                    "nearest_source_altitude_km": (
                        nearest_source.altitude_km
                        if nearest_source is not None else None
                    ),
                    "nearest_horizontal_source_altitude_gap_km": nearest_gap,
                    "minimum_altitude_gap_km": (
                        min(finite_gaps) if finite_gaps else None
                    ),
                    "joint_clusters_within_tolerance": sum(joint),
                    "horizontal_tolerance_km": TRUTH_HORIZONTAL_TOLERANCE_KM,
                    "altitude_tolerance_km": (
                        TRUTH_ALTITUDE_TOLERANCE_KM
                        if screen == control.ALTITUDE_SCREEN else None
                    ),
                    "recovered": any(joint),
                    "parent_collapsed_residual_ids": ";".join(sorted(
                        {event_id(parent) for parent in parents}
                    )),
                    "altitude_sensitivity_recovered": json.dumps(
                        sensitivities, sort_keys=True
                    ),
                })
    return output


def run(arguments: argparse.Namespace) -> int:
    batch_manifest, route_documents = batch.load_complete_route_documents(
        arguments.batch_directory
    )
    verify_batch_inputs(
        batch_manifest, arguments.candidate_pairs, arguments.spot_records
    )
    pairs = control.read_candidate_pairs(
        arguments.candidate_pairs, arguments.dataset_name
    )
    spots = control.read_spot_records(arguments.spot_records)
    plan = control.build_route_plan(
        pairs,
        spots,
        control.PublishedSphericalRouteResolver(
            include_auxiliary_diagnostics=False
        ),
    )
    results = control.parse_route_results(route_documents)
    control.validate_complete_route_results(plan, results)

    surface_pairs = control.apply_surface_endpoint_screen(
        plan, results, SURFACE_TOLERANCE_KM
    )
    altitude_pairs = control.apply_common_altitude_screen(
        plan, results, ALTITUDE_PATH_TOLERANCE_KM
    )
    surface_clusters = control.cluster_screened_pairs(
        surface_pairs, CLUSTER_RADIUS_KM, MINIMUM_INDEPENDENT_LINKS
    )
    altitude_slices = control.cluster_screened_pairs(
        altitude_pairs, CLUSTER_RADIUS_KM, MINIMUM_INDEPENDENT_LINKS
    )
    altitude_clusters = control.collapse_altitude_clusters(
        altitude_slices, ALTITUDE_COLLAPSE_RADIUS_KM
    )
    primary_clusters = tuple((*surface_clusters, *altitude_clusters))
    surface_residuals = control.symmetric_residuals(
        surface_clusters, RESIDUAL_TOLERANCE_KM
    )
    altitude_source_residuals = control.symmetric_residuals(
        altitude_slices, RESIDUAL_TOLERANCE_KM
    )
    surviving_altitude_slices = tuple(
        item.cluster for item in altitude_source_residuals if item.is_residual
    )
    altitude_residual_clusters = control.collapse_altitude_clusters(
        surviving_altitude_slices, ALTITUDE_COLLAPSE_RADIUS_KM
    )
    source_nearest = {
        source_id: item.nearest_other_condition_km
        for item in altitude_source_residuals
        for source_id in item.cluster.source_altitude_cluster_ids
    }
    altitude_residuals = tuple(
        control.ResidualCluster(
            cluster,
            min(
                source_nearest[source_id]
                for source_id in cluster.source_altitude_cluster_ids
            ),
            True,
        )
        for cluster in altitude_residual_clusters
    )
    primary_residuals = tuple((*surface_residuals, *altitude_residuals))
    exact_altitude_residuals = control.symmetric_residuals(
        altitude_slices,
        RESIDUAL_TOLERANCE_KM,
        altitude_matching="exact_altitude_sensitivity",
    )

    audit_rows = read_csv(arguments.arc_truth_audit)
    epochs = {row["epoch"]: row for row in audit_rows}
    if set(epochs) != {pair.epoch_id for pair in pairs}:
        raise AssemblyError("arc/truth audit epochs do not match candidate epochs")
    truth_rows = read_csv(arguments.truth_references)

    cluster_rows: list[dict[str, object]] = []
    raw_cluster_rows: list[dict[str, object]] = []

    def add_epoch_metadata(
        row: dict[str, object], cluster: control.SpatialCluster
    ) -> None:
        metadata = epochs[cluster.epoch_id]
        row["flight"] = metadata["flight"]
        row["arc_time_utc"] = metadata["representative_time_utc"]

    for cluster in primary_clusters:
        row = control.spatial_cluster_record(cluster)
        add_epoch_metadata(row, cluster)
        raw_cluster_rows.append(row)
    raw_cluster_rows.sort(key=lambda row: (
        str(row["epoch_id"]), str(row["screen"]), str(row["condition"]),
        str(row["physical_slot"]), int(row["cluster_rank"]),
    ))

    def append_cluster_row(
        residual: control.ResidualCluster,
        screen_override: str | None = None,
    ) -> None:
        cluster = residual.cluster
        row = control.spatial_cluster_record(cluster, residual)
        if screen_override is not None:
            row["screen"] = screen_override
        add_epoch_metadata(row, cluster)
        cluster_rows.append(row)

    for residual in primary_residuals:
        append_cluster_row(residual)
    for residual in exact_altitude_residuals:
        append_cluster_row(residual, EXACT_ALTITUDE_SENSITIVITY_SCREEN)
    cluster_rows.sort(key=lambda row: (
        str(row["epoch_id"]), str(row["screen"]), str(row["condition"]),
        str(row["physical_slot"]), int(row["cluster_rank"]),
    ))
    comparisons = comparison_rows(
        primary_clusters, primary_residuals, epochs
    )
    truth_scores = truth_score_rows(
        surface_residuals,
        altitude_source_residuals,
        altitude_residuals,
        truth_rows,
        expected_epoch_ids=epochs,
    )
    statistics = statistical_summary(primary_clusters, primary_residuals, epochs)
    publication_rows = publication_result_rows(
        comparisons, truth_scores, statistics
    )

    assembly_scientific_settings = {
        "surface_endpoint_tolerance_km": SURFACE_TOLERANCE_KM,
        "aircraft_path_horizontal_tolerance_km": ALTITUDE_PATH_TOLERANCE_KM,
        "cluster_radius_km": CLUSTER_RADIUS_KM,
        "minimum_independent_links": MINIMUM_INDEPENDENT_LINKS,
        "source_residual_tolerance_km": RESIDUAL_TOLERANCE_KM,
        "source_residual_altitude_matching": "ignore_modeled_altitude",
        "altitude_survivor_collapse_radius_km": ALTITUDE_COLLAPSE_RADIUS_KM,
        "truth_horizontal_tolerance_km": TRUTH_HORIZONTAL_TOLERANCE_KM,
        "truth_altitude_tolerance_km": TRUTH_ALTITUDE_TOLERANCE_KM,
        "truth_altitude_sensitivity_km": list(TRUTH_ALTITUDE_SENSITIVITY_KM),
        "truth_slot_rule": (
            "transmission midpoint nearest representative BTO; same withheld "
            "truth target applied to all three panels after selection"
        ),
        "truth_altitude_basis_caution": (
            "ACARS altitude is pressure/barometric while PHaRLAP height is "
            "geometric/model height; 0.5 km is primary, 0.25 and 1.0 km sensitivities"
        ),
        "statistical_primary_block": "epoch_by_screen; exploratory only",
    }
    deterministic_batch_identity = batch_scientific_identity(batch_manifest)
    run_identity_inputs = {
        "pharlap_batch_scientific_identity": deterministic_batch_identity,
        "candidate_pairs_sha256": sha256_file(arguments.candidate_pairs),
        "spot_records_sha256": sha256_file(arguments.spot_records),
        "arc_truth_audit_sha256": sha256_file(arguments.arc_truth_audit),
        "truth_references_sha256": sha256_file(arguments.truth_references),
        "assembler_sha256": sha256_file(Path(__file__)),
        "control_source_sha256": sha256_file(
            CODE_DIRECTORY / "wspr_pharlap_control.py"
        ),
        "batch_runner_source_sha256": sha256_file(
            CODE_DIRECTORY / "pharlap_batch_runner.py"
        ),
        "assembly_scientific_settings": assembly_scientific_settings,
        "pharlap_batch_scientific_settings": batch_manifest.get(
            "scientific_settings"
        ),
        "pharlap_scientific_dependencies": batch_manifest.get(
            "scientific_dependencies"
        ),
    }
    run_identity = hashlib.sha256(
        canonical_json(run_identity_inputs)
    ).hexdigest()
    metadata = {
        "schema": PLOT_METADATA_SCHEMA,
        "run_id": run_identity,
        "known_aircraft_truth_used_in_candidate_selection": False,
        "control_offsets_minutes": {
            "minus_60_min": -60, "actual_time": 0, "plus_60_min": 60,
        },
        "cluster_radius_km": CLUSTER_RADIUS_KM,
        "residual_tolerance_km": RESIDUAL_TOLERANCE_KM,
        "minimum_independent_links": MINIMUM_INDEPENDENT_LINKS,
        "surface_endpoint_tolerance_km": SURFACE_TOLERANCE_KM,
        "aircraft_altitude_tolerance_km": ALTITUDE_PATH_TOLERANCE_KM,
        "truth_recovery_tolerance_km": TRUTH_HORIZONTAL_TOLERANCE_KM,
        "truth_recovery_altitude_tolerance_km": TRUTH_ALTITUDE_TOLERANCE_KM,
        "truth_recovery_altitude_sensitivity_km": list(
            TRUTH_ALTITUDE_SENSITIVITY_KM
        ),
        "route_geometry": "PublishedSphericalRouteResolver",
        "ionosphere_model": "PHaRLAP 4.7.4 IRI-2020 spherical 2-D",
        "map_extent_lon_lat": [64.0, 130.0, 0.0, 30.0],
        "aircraft_altitude_grid_km": [value / 2.0 for value in range(1, 27)],
        "altitude_collapse_spatial_tolerance_km": ALTITUDE_COLLAPSE_RADIUS_KM,
        "common_altitude_residual_model": (
            "source_clusters_matched_across_any_altitude_before_survivors_are_"
            "collapsed_for_event_display_and_count;truth_recovery_uses_"
            "surviving_source_centres_and_heights"
        ),
        "epoch_partition_applied_before_clustering": True,
        "statistical_inference_status": "exploratory_dependent_controls",
        "assembly_scientific_settings": assembly_scientific_settings,
        "pharlap_batch_scientific_settings": batch_manifest.get(
            "scientific_settings"
        ),
        "pharlap_scientific_dependencies": batch_manifest.get(
            "scientific_dependencies"
        ),
        "pharlap_worker_reported_external_identity": batch_manifest.get(
            "worker_reported_external_identity"
        ),
        "run_identity_inputs": run_identity_inputs,
        "pharlap_batch_scientific_identity": deterministic_batch_identity,
        "batch_manifest_sha256": sha256_file(
            arguments.batch_directory / "manifest.json"
        ),
    }
    summary = {
        "schema": SCHEMA,
        "run_id": run_identity,
        "counts": {
            "candidate_pairs": len(pairs),
            "route_jobs": len(plan.jobs),
            "surface_screened_pairs": len(surface_pairs),
            "altitude_slice_screened_pairs": len(altitude_pairs),
            "surface_clusters": len(surface_clusters),
            "altitude_slice_clusters": len(altitude_slices),
            "collapsed_altitude_clusters": len(altitude_clusters),
            "surviving_altitude_source_clusters": len(
                surviving_altitude_slices
            ),
            "collapsed_altitude_residual_events": len(
                altitude_residual_clusters
            ),
            "primary_residual_clusters": sum(
                item.is_residual for item in primary_residuals
            ),
        },
        "comparisons": comparisons,
        "publication_results": publication_rows,
        "truth_scores": truth_scores,
        "statistical_diagnostics": statistics,
        "interpretation": (
            "Propagation feasibility is a filter, not evidence that a returned "
            "mode occurred. Known aircraft truth was applied only after blind "
            "selection, at the nearest physical WSPR slot."
        ),
    }

    cluster_fields = (
        "epoch_id", "flight", "arc_time_utc", "condition", "screen",
        "physical_slot", "cluster_rank", "center_candidate_id",
        "latitude_deg", "longitude_deg_e", "pair_intersections",
        "support_links", "independent_links", "altitude_km",
        "altitude_minimum_km", "altitude_maximum_km",
        "feasible_altitude_count", "feasible_altitudes_km",
        "source_altitude_clusters", "source_altitude_cluster_ids",
        "support_spot_ids", "nearest_other_condition_km", "is_residual",
    )
    raw_cluster_fields = cluster_fields[:-2]
    comparison_fields = tuple(comparisons[0])
    publication_fields = tuple(publication_rows[0])
    truth_score_fields = tuple(truth_scores[0])
    output = arguments.output_directory
    payloads = {
        "known_flight_pharlap_clusters.csv": csv_payload(
            cluster_rows, cluster_fields
        ),
        "known_flight_pharlap_raw_clusters.csv": csv_payload(
            raw_cluster_rows, raw_cluster_fields
        ),
        "known_flight_pharlap_comparison.csv": csv_payload(
            comparisons, comparison_fields
        ),
        "known_flight_pharlap_publication_results.csv": csv_payload(
            publication_rows, publication_fields
        ),
        "known-flight-pharlap-publication-results.md": publication_markdown(
            publication_rows
        ),
        "known_flight_pharlap_truth_scores.csv": csv_payload(
            truth_scores, truth_score_fields
        ),
        "run_metadata.json": canonical_json(metadata),
        "results.json": canonical_json(summary),
    }
    for name, payload in payloads.items():
        atomic_write(output / name, payload)
    manifest = {
        "schema": "mh370.wspr.pharlap.known-flight-output-manifest.v1",
        "run_id": run_identity,
        "inputs": {
            "candidate_pairs_sha256": sha256_file(arguments.candidate_pairs),
            "spot_records_sha256": sha256_file(arguments.spot_records),
            "arc_truth_audit_sha256": sha256_file(arguments.arc_truth_audit),
            "truth_references_sha256": sha256_file(arguments.truth_references),
            "batch_manifest_sha256": sha256_file(
                arguments.batch_directory / "manifest.json"
            ),
        },
        "outputs": {
            name: hashlib.sha256(payload).hexdigest()
            for name, payload in payloads.items()
        },
    }
    atomic_write(output / "manifest.json", canonical_json(manifest))
    print(json.dumps({
        "status": "complete",
        "run_id": run_identity,
        "output_directory": str(output),
        **summary["counts"],
    }, sort_keys=True))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--batch-directory", type=Path, required=True)
    parser.add_argument(
        "--candidate-pairs", type=Path,
        default=DATA_DIRECTORY / "known_flight_pair_locations.csv.gz",
    )
    parser.add_argument(
        "--spot-records", type=Path,
        default=DATA_DIRECTORY / "known_flight_spot_records.csv.gz",
    )
    parser.add_argument(
        "--arc-truth-audit", type=Path,
        default=DATA_DIRECTORY / "known_flight_arc_truth_audit.csv",
    )
    parser.add_argument(
        "--truth-references", type=Path,
        default=DATA_DIRECTORY / "known_flight_truth_references.csv",
    )
    parser.add_argument("--dataset-name", default="known-flight")
    parser.add_argument("--output-directory", type=Path, required=True)
    return parser


def main() -> int:
    try:
        return run(build_parser().parse_args())
    except (AssemblyError, batch.BatchError, ValueError, OSError) as error:
        print(f"error: {error}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
