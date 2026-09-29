#!/usr/bin/env python3
"""Rerun PHaRLAP for selected coherent locator-uncertainty witnesses.

Witnesses are chosen with withheld truth and are therefore sensitivity cases,
not blind detections.  Only the links contributing to each witness cluster are
traced; the result asks whether that local >=3-link geometry survives the two
published PHaRLAP feasibility screens.  It is not a replacement for regenerating
and rerunning every candidate from independently verified antenna coordinates.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import dataclasses
import hashlib
import json
import math
import sys
from pathlib import Path
from typing import Mapping

import numpy as np
from scipy.stats import qmc


CODE_DIRECTORY = Path(__file__).resolve().parent
SOURCE_DIRECTORY = CODE_DIRECTORY.parent
DATA_DIRECTORY = SOURCE_DIRECTORY / "data" / "known-flight"
sys.path.insert(0, str(CODE_DIRECTORY))

import audit_known_flight_locator_uncertainty as locator_audit
import pharlap_raytrace_worker as ray_worker
import wspr_pharlap_control as control


class ExplicitCoordinateResolver:
    """Paper-compatible route resolver using declared endpoint coordinates."""

    def resolve(
        self,
        spot: control.SpotRecord,
        endpoint: str,
        candidate_latitude_deg: float,
        candidate_longitude_deg_e: float,
    ) -> control.ResolvedRoute:
        transmitter = (
            spot.archive_transmitter_lat_deg,
            spot.archive_transmitter_lon_deg_e,
        )
        receiver = (
            spot.archive_receiver_lat_deg,
            spot.archive_receiver_lon_deg_e,
        )
        if endpoint == "transmitter":
            origin, other = transmitter, receiver
        elif endpoint == "receiver":
            origin, other = receiver, transmitter
        else:
            raise ValueError(f"unknown endpoint: {endpoint}")
        _link_range, toward_bearing = control.published_spherical_inverse(*origin, *other)
        target_range, target_bearing = control.published_spherical_inverse(
            *origin, candidate_latitude_deg, candidate_longitude_deg_e
        )
        difference = (target_bearing - toward_bearing + 180.0) % 360.0 - 180.0
        toward = (
            math.isclose(
                target_range,
                math.pi * control.PHARLAP_EARTH_RADIUS_KM,
                abs_tol=1e-6,
            )
            or abs(difference) <= 90.0
        )
        bearing = toward_bearing if toward else (toward_bearing + 180.0) % 360.0
        bearing_difference = math.radians(
            (target_bearing - bearing + 180.0) % 360.0 - 180.0
        )
        cross_track = abs(control.PHARLAP_EARTH_RADIUS_KM * math.asin(
            max(
                -1.0,
                min(
                    1.0,
                    math.sin(target_range / control.PHARLAP_EARTH_RADIUS_KM)
                    * math.sin(bearing_difference),
                ),
            )
        ))
        return control.ResolvedRoute(
            branch=("toward_other_endpoint" if toward else "away_from_other_endpoint"),
            origin_latitude_deg=origin[0],
            origin_longitude_deg_e=origin[1],
            initial_bearing_deg=bearing,
            target_range_km=target_range,
            geometry_model=(
                "published geodetic-latitude great-circle sphere, R=6378.137 km; "
                "explicit coherent station coordinates within reported locator cells"
            ),
            primary_cross_track_mismatch_km=cross_track,
        )


def station_assignment(
    stations: tuple[tuple[str, str], ...],
    sample_index: int,
    seed: int,
) -> dict[tuple[str, str], tuple[float, float]]:
    sampler = qmc.Sobol(d=2 * len(stations), scramble=True, seed=seed)
    if sample_index:
        sampler.fast_forward(sample_index)
    vectors = locator_audit.station_points(sampler.random(1), stations)[0]
    latitudes = np.degrees(np.arcsin(np.clip(vectors[:, 2], -1.0, 1.0)))
    longitudes = np.degrees(np.arctan2(vectors[:, 1], vectors[:, 0]))
    return {
        station: (float(latitude), float(longitude))
        for station, latitude, longitude in zip(stations, latitudes, longitudes)
    }


def perturbed_pairs(
    epoch_id: str,
    sample_index: int,
    neighbor_candidate_ids: set[str],
    audit_spots: Mapping[int, locator_audit.Spot],
    audit_pairs: tuple[locator_audit.Pair, ...],
    coordinates: Mapping[tuple[str, str], tuple[float, float]],
) -> tuple[tuple[control.CandidatePair, ...], dict[int, control.SpotRecord]]:
    selected = [
        pair for pair in audit_pairs
        if pair.epoch_id == epoch_id and pair.candidate_id in neighbor_candidate_ids
    ]
    if {pair.candidate_id for pair in selected} != neighbor_candidate_ids:
        raise ValueError(f"{epoch_id}: witness candidate identity mismatch")
    used_spot_ids = sorted({
        spot_id for pair in selected for spot_id in (pair.spot_id_1, pair.spot_id_2)
    })
    station_vectors = {
        key: locator_audit.scalar_unit_vector(*value)
        for key, value in coordinates.items()
    }
    normals: dict[int, np.ndarray] = {}
    records: dict[int, control.SpotRecord] = {}
    original_records = control.read_spot_records(
        DATA_DIRECTORY / "known_flight_spot_records.csv.gz"
    )
    for spot_id in used_spot_ids:
        source = audit_spots[spot_id]
        transmitter = coordinates[source.transmitter_key]
        receiver = coordinates[source.receiver_key]
        normal = np.cross(
            station_vectors[source.transmitter_key],
            station_vectors[source.receiver_key],
        )
        normals[spot_id] = normal / np.linalg.norm(normal)
        records[spot_id] = dataclasses.replace(
            original_records[spot_id],
            archive_transmitter_lat_deg=transmitter[0],
            archive_transmitter_lon_deg_e=transmitter[1],
            archive_receiver_lat_deg=receiver[0],
            archive_receiver_lon_deg_e=receiver[1],
        )
    result: list[control.CandidatePair] = []
    for pair in selected:
        point = np.cross(normals[pair.spot_id_1], normals[pair.spot_id_2])
        point /= np.linalg.norm(point)
        frozen = locator_audit.scalar_unit_vector(pair.latitude_deg, pair.longitude_deg_e)
        if float(point @ frozen) < 0.0:
            point *= -1.0
        latitude = float(np.degrees(np.arcsin(np.clip(point[2], -1.0, 1.0))))
        longitude = float(np.degrees(np.arctan2(point[1], point[0])))
        angle = float(np.degrees(np.arccos(np.clip(
            abs(float(normals[pair.spot_id_1] @ normals[pair.spot_id_2])), 0.0, 1.0
        ))))
        if angle < locator_audit.MINIMUM_CROSSING_ANGLE_DEG:
            raise ValueError(f"{epoch_id}: witness lost crossing-angle eligibility")
        source_record = original_records[pair.spot_id_1]
        result.append(control.CandidatePair(
            candidate_id=pair.candidate_id,
            epoch_id=pair.epoch_id,
            condition="actual_time",
            physical_slot=pair.physical_slot,
            radio_time=source_record.time_utc,
            spot_id_1=pair.spot_id_1,
            spot_id_2=pair.spot_id_2,
            transmitter_1=audit_spots[pair.spot_id_1].transmitter,
            receiver_1=audit_spots[pair.spot_id_1].receiver,
            transmitter_2=audit_spots[pair.spot_id_2].transmitter,
            receiver_2=audit_spots[pair.spot_id_2].receiver,
            latitude_deg=latitude,
            longitude_deg_e=longitude,
            crossing_angle_deg=angle,
            source_fields={"locator_sensitivity_sample_index": str(sample_index)},
        ))
    return tuple(result), records


def run_witness(
    epoch_id: str,
    witness: Mapping[str, object],
    audit_spots: Mapping[int, locator_audit.Spot],
    audit_pairs: tuple[locator_audit.Pair, ...],
    truth: locator_audit.Truth,
    stations: tuple[tuple[str, str], ...],
    seed: int,
    dependencies: tuple[Path, Path, Path],
) -> dict[str, object]:
    sample_index = int(witness["sample_index_zero_based"])
    coordinates = station_assignment(stations, sample_index, seed)
    pairs, spots = perturbed_pairs(
        epoch_id,
        sample_index,
        set(map(str, witness["neighbor_candidate_ids"])),
        audit_spots,
        audit_pairs,
        coordinates,
    )
    plan = control.build_route_plan(pairs, spots, ExplicitCoordinateResolver())
    elevations = ray_worker.production_elevations_deg()
    jobs = control.worker_job_inputs(
        plan,
        elevations_deg=elevations,
        elevation_fan_provenance=(
            "Frozen primary convergence fan, applied to a truth-selected "
            "locator-coordinate sensitivity witness."
        ),
    )
    pharlap_home, iri_library, ray_library = dependencies
    adapted: list[dict[str, object]] = []
    for route, job in zip(plan.jobs, jobs):
        worker_result = ray_worker.run_job(job, pharlap_home, iri_library, ray_library)
        adapted.append(control.adapt_worker_result(route, worker_result))
    indexed = control.parse_route_results(adapted)
    surface_pairs = control.apply_surface_endpoint_screen(plan, indexed, tolerance_km=25.0)
    altitude_pairs = control.apply_common_altitude_screen(plan, indexed, tolerance_km=25.0)
    surface_clusters = control.cluster_screened_pairs(surface_pairs, 25.0, 3)
    altitude_source_clusters = control.cluster_screened_pairs(altitude_pairs, 25.0, 3)
    altitude_clusters = control.collapse_altitude_clusters(altitude_source_clusters, 25.0)
    clusters = (*surface_clusters, *altitude_clusters)
    scores: dict[str, object] = {}
    for screen in (control.SURFACE_SCREEN, control.ALTITUDE_SCREEN):
        reference = control.TruthReference(
            truth_id=f"{epoch_id}-{screen}",
            epoch_id=epoch_id,
            condition="actual_time",
            physical_slot=truth.physical_slot,
            latitude_deg=truth.latitude_deg,
            longitude_deg_e=truth.longitude_deg_e,
            altitude_km=(
                None if screen == control.SURFACE_SCREEN else truth.altitude_km
            ),
            screen=screen,
        )
        # The audit truth loader intentionally omits altitude.  Horizontal
        # recovery is still decisive for surface; altitude feasibility is
        # reported as its full retained grid rather than scored against truth.
        score = control.score_truth_references(
            clusters, (reference,), 25.0, 0.5
        )[0]
        scores[screen] = {
            "eligible_clusters": score.eligible_clusters,
            "nearest_horizontal_distance_km": (
                None if math.isinf(score.nearest_distance_km) else score.nearest_distance_km
            ),
            "horizontal_recovered": (
                score.nearest_distance_km <= 25.0 if score.eligible_clusters else False
            ),
            "nearest_altitude_gap_km": score.nearest_altitude_gap_km,
            "joint_horizontal_altitude_recovered": score.recovered,
        }
    return {
        "epoch_id": epoch_id,
        "sample_index_zero_based": sample_index,
        "source_witness": dict(witness),
        "truth_selected_sensitivity_not_blind_detection": True,
        "candidate_pairs_traced": len(pairs),
        "route_jobs_traced": len(jobs),
        "surface_pairs_passing_four_legs": len(surface_pairs),
        "common_altitude_pair_slices_passing_four_legs": len(altitude_pairs),
        "surface_pair_details": [
            {
                "candidate_id": item.pair.candidate_id,
                "leg_minimum_errors_km": {
                    f"{spot_id}:{endpoint}": match.minimum_error_km
                    for (spot_id, endpoint), match in item.leg_matches.items()
                },
            }
            for item in surface_pairs
        ],
        "common_altitude_pair_slice_details": [
            {
                "candidate_id": item.pair.candidate_id,
                "altitude_km": item.altitude_km,
                "leg_minimum_errors_km": {
                    f"{spot_id}:{endpoint}": match.minimum_error_km
                    for (spot_id, endpoint), match in item.leg_matches.items()
                },
            }
            for item in altitude_pairs
        ],
        "surface_clusters": [dataclasses.asdict(cluster) for cluster in surface_clusters],
        "common_altitude_clusters": [dataclasses.asdict(cluster) for cluster in altitude_clusters],
        "scores": scores,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--audit", type=Path, required=True)
    parser.add_argument("--pharlap-home", type=Path, required=True)
    parser.add_argument("--iri-library", type=Path, required=True)
    parser.add_argument("--ray-library", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument(
        "--witness-set",
        choices=("nearest", "all-primary"),
        default="nearest",
        help="trace the nearest witness per epoch or every primary-tolerance witness",
    )
    parser.add_argument("--processes", type=int, default=1)
    return parser.parse_args()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> None:
    args = parse_args()
    audit_document = json.loads(args.audit.read_text())
    audit_spots, audit_pairs, truths = locator_audit.read_inputs(
        DATA_DIRECTORY / "known_flight_pair_locations.csv.gz",
        DATA_DIRECTORY / "known_flight_spot_records.csv.gz",
        DATA_DIRECTORY / "known_flight_truth_references.csv",
    )
    used_spot_ids = sorted({
        spot_id for pair in audit_pairs for spot_id in (pair.spot_id_1, pair.spot_id_2)
    })
    stations = tuple(sorted({
        key
        for spot_id in used_spot_ids
        for key in (
            audit_spots[spot_id].transmitter_key,
            audit_spots[spot_id].receiver_key,
        )
    }))
    if not 1 <= args.processes <= 5:
        raise ValueError("processes must be between one and five")
    if args.witness_set == "nearest":
        selected = [
            (epoch_id, witness)
            for epoch_id, witness in audit_document["nearest_cluster_witnesses"].items()
            if float(witness["center_truth_distance_km"]) <= 25.0
        ]
    else:
        selected = [
            (epoch_id, witness)
            for epoch_id, witnesses in audit_document["primary_tolerance_witnesses"].items()
            for witness in witnesses
        ]
    selected.sort(key=lambda item: (
        item[0],
        int(item[1]["sample_index_zero_based"]),
        str(item[1]["center_candidate_id"]),
    ))
    common_arguments = (
        audit_spots,
        audit_pairs,
        stations,
        int(audit_document["seed"]),
        (args.pharlap_home, args.iri_library, args.ray_library),
    )
    results: list[dict[str, object]] = []
    if args.processes == 1:
        for epoch_id, witness in selected:
            results.append(run_witness(
                epoch_id,
                witness,
                common_arguments[0],
                common_arguments[1],
                truths[epoch_id],
                common_arguments[2],
                common_arguments[3],
                common_arguments[4],
            ))
    else:
        with concurrent.futures.ProcessPoolExecutor(max_workers=args.processes) as pool:
            futures = [
                pool.submit(
                    run_witness,
                    epoch_id,
                    witness,
                    common_arguments[0],
                    common_arguments[1],
                    truths[epoch_id],
                    common_arguments[2],
                    common_arguments[3],
                    common_arguments[4],
                )
                for epoch_id, witness in selected
            ]
            for future in concurrent.futures.as_completed(futures):
                results.append(future.result())
    results.sort(key=lambda result: (
        str(result["epoch_id"]),
        int(result["sample_index_zero_based"]),
        str(result["source_witness"]["center_candidate_id"]),
    ))
    output = {
        "schema": "mh370.wspr.locator-witness-pharlap.v1",
        "runner_source_sha256": sha256_file(Path(__file__).resolve()),
        "scope": (
            "Truth-selected local sensitivity witnesses only; not blind detections "
            "and not a full coordinate-uncertainty rerun."
        ),
        "audit_input": str(args.audit),
        "audit_input_sha256": sha256_file(args.audit),
        "witness_set": args.witness_set,
        "witness_count": len(selected),
        "route_job_count": sum(int(result["route_jobs_traced"]) for result in results),
        "dependencies": {
            "pharlap_home": str(args.pharlap_home.resolve()),
            "iri_library_sha256": sha256_file(args.iri_library),
            "ray_library_sha256": sha256_file(args.ray_library),
        },
        "results": results,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n")
    print(json.dumps(output, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
