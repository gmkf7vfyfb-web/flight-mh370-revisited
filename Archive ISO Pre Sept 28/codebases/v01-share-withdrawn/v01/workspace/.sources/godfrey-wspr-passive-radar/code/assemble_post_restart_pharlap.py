#!/usr/bin/env python3
"""Assemble a complete trajectory-blind post-restart PHaRLAP control batch."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import assemble_known_flight_pharlap as shared
import pharlap_batch_runner as batch
import wspr_pharlap_control as control


CODE_DIRECTORY = Path(__file__).resolve().parent
DATA_DIRECTORY = CODE_DIRECTORY.parent / "data" / "post-restart"
SCHEMA = "mh370.wspr.pharlap.post-restart-control-results.v1"
PLOT_METADATA_SCHEMA = "mh370.wspr.pharlap.post-restart-control-run.v1"
SURFACE_TOLERANCE_KM = 25.0
ALTITUDE_PATH_TOLERANCE_KM = 25.0
CLUSTER_RADIUS_KM = 25.0
ALTITUDE_COLLAPSE_RADIUS_KM = 25.0
RESIDUAL_TOLERANCE_KM = 25.0
MINIMUM_INDEPENDENT_LINKS = 3
EXACT_ALTITUDE_SENSITIVITY_SCREEN = "common_aircraft_altitude_exact_sensitivity"


class AssemblyError(RuntimeError):
    """The completed route cache or post-restart input contract is invalid."""


def run(arguments: argparse.Namespace) -> int:
    batch_manifest, route_documents = batch.load_complete_route_documents(
        arguments.batch_directory
    )
    shared.verify_batch_inputs(
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
            min(source_nearest[source_id] for source_id in cluster.source_altitude_cluster_ids),
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

    audit_rows = shared.read_csv(arguments.arc_audit)
    epochs = {row["epoch"]: row for row in audit_rows}
    if set(epochs) != {pair.epoch_id for pair in pairs}:
        raise AssemblyError("arc audit epochs do not match candidate epochs")
    if any(row.get("truth_used_in_candidate_selection", "").lower() != "false"
           for row in audit_rows):
        raise AssemblyError("post-restart audit does not declare blind selection")

    cluster_rows: list[dict[str, object]] = []

    def append_cluster_row(
        residual: control.ResidualCluster,
        screen_override: str | None = None,
    ) -> None:
        cluster = residual.cluster
        row = control.spatial_cluster_record(cluster, residual)
        if screen_override is not None:
            row["screen"] = screen_override
        metadata = epochs[cluster.epoch_id]
        row["flight"] = metadata["flight"]
        row["arc_time_utc"] = metadata["representative_time_utc"]
        cluster_rows.append(row)

    for residual in primary_residuals:
        append_cluster_row(residual)
    for residual in exact_altitude_residuals:
        append_cluster_row(residual, EXACT_ALTITUDE_SENSITIVITY_SCREEN)
    cluster_rows.sort(key=lambda row: (
        int(epochs[str(row["epoch_id"])]["sequence"]),
        str(row["screen"]), str(row["condition"]),
        str(row["physical_slot"]), int(row["cluster_rank"]),
    ))

    comparisons = shared.comparison_rows(
        primary_clusters, primary_residuals, epochs
    )
    statistics = shared.statistical_summary(
        primary_clusters, primary_residuals, epochs
    )
    assembly_settings = {
        "surface_endpoint_tolerance_km": SURFACE_TOLERANCE_KM,
        "aircraft_path_horizontal_tolerance_km": ALTITUDE_PATH_TOLERANCE_KM,
        "cluster_radius_km": CLUSTER_RADIUS_KM,
        "minimum_independent_links": MINIMUM_INDEPENDENT_LINKS,
        "source_residual_tolerance_km": RESIDUAL_TOLERANCE_KM,
        "source_residual_altitude_matching": "ignore_modeled_altitude",
        "altitude_survivor_collapse_radius_km": ALTITUDE_COLLAPSE_RADIUS_KM,
        "statistical_primary_block": "epoch_by_screen; exploratory only",
    }
    deterministic_batch_identity = shared.batch_scientific_identity(batch_manifest)
    identity_inputs = {
        "pharlap_batch_scientific_identity": deterministic_batch_identity,
        "candidate_pairs_sha256": shared.sha256_file(arguments.candidate_pairs),
        "spot_records_sha256": shared.sha256_file(arguments.spot_records),
        "arc_audit_sha256": shared.sha256_file(arguments.arc_audit),
        "arcs_sha256": shared.sha256_file(arguments.arcs),
        "assembler_sha256": shared.sha256_file(Path(__file__)),
        "shared_assembler_sha256": shared.sha256_file(
            CODE_DIRECTORY / "assemble_known_flight_pharlap.py"
        ),
        "control_source_sha256": shared.sha256_file(
            CODE_DIRECTORY / "wspr_pharlap_control.py"
        ),
        "assembly_scientific_settings": assembly_settings,
    }
    run_identity = hashlib.sha256(shared.canonical_json(identity_inputs)).hexdigest()
    metadata = {
        "schema": PLOT_METADATA_SCHEMA,
        "run_id": run_identity,
        "known_aircraft_truth_available": False,
        "known_aircraft_truth_used_in_candidate_selection": False,
        "control_offsets_minutes": {
            "minus_60_min": -60, "actual_time": 0, "plus_60_min": 60,
        },
        "map_extent_lon_lat": [64.0, 110.0, -45.0, 10.0],
        "route_geometry": "PublishedSphericalRouteResolver",
        "ionosphere_model": "PHaRLAP 4.7.4 IRI-2020 spherical 2-D",
        "assembly_scientific_settings": assembly_settings,
        "pharlap_batch_scientific_settings": batch_manifest.get("scientific_settings"),
        "pharlap_scientific_dependencies": batch_manifest.get("scientific_dependencies"),
        "pharlap_worker_reported_external_identity": batch_manifest.get(
            "worker_reported_external_identity"
        ),
        "run_identity_inputs": identity_inputs,
        "batch_manifest_sha256": shared.sha256_file(
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
            "surviving_altitude_source_clusters": len(surviving_altitude_slices),
            "collapsed_altitude_residual_events": len(altitude_residual_clusters),
            "primary_residual_clusters": sum(
                item.is_residual for item in primary_residuals
            ),
        },
        "comparisons": comparisons,
        "statistical_diagnostics": statistics,
        "interpretation": (
            "Propagation feasibility is a filter, not evidence that a returned "
            "mode occurred. No assumed post-radar aircraft position or trajectory "
            "was supplied to candidate construction, propagation, or scoring."
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
    output = arguments.output_directory
    payloads = {
        "post_restart_pharlap_clusters.csv": shared.csv_payload(
            cluster_rows, cluster_fields
        ),
        "post_restart_pharlap_comparison.csv": shared.csv_payload(
            comparisons, tuple(comparisons[0])
        ),
        "run_metadata.json": shared.canonical_json(metadata),
        "results.json": shared.canonical_json(summary),
    }
    for name, payload in payloads.items():
        shared.atomic_write(output / name, payload)
    output_manifest = {
        "schema": "mh370.wspr.pharlap.post-restart-output-manifest.v1",
        "run_id": run_identity,
        "inputs": identity_inputs,
        "outputs": {
            name: hashlib.sha256(payload).hexdigest()
            for name, payload in payloads.items()
        },
    }
    shared.atomic_write(output / "manifest.json", shared.canonical_json(output_manifest))
    print(json.dumps({
        "status": "complete", "run_id": run_identity,
        "output_directory": str(output), **summary["counts"],
    }, sort_keys=True))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--batch-directory", type=Path, required=True)
    parser.add_argument(
        "--candidate-pairs", type=Path,
        default=DATA_DIRECTORY / "post_restart_pair_locations.csv.gz",
    )
    parser.add_argument(
        "--spot-records", type=Path,
        default=DATA_DIRECTORY / "post_restart_spot_records.csv.gz",
    )
    parser.add_argument(
        "--arc-audit", type=Path,
        default=DATA_DIRECTORY / "post_restart_arc_audit.csv",
    )
    parser.add_argument(
        "--arcs", type=Path,
        default=DATA_DIRECTORY / "post_restart_arcs.csv",
    )
    parser.add_argument("--dataset-name", default="post-restart")
    parser.add_argument("--output-directory", type=Path, required=True)
    return parser


def main() -> int:
    try:
        return run(build_parser().parse_args())
    except (AssemblyError, shared.AssemblyError, batch.BatchError, ValueError, OSError) as error:
        print(f"error: {error}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
