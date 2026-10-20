#!/usr/bin/env python3
"""Check whether a coordinate witness survives frozen-pair control subtraction.

This audit is intentionally narrower than full rematerialization.  It keeps all
candidate pairs selected by the cell-centre experiment, applies one coherent
within-cell coordinate assignment, and searches every control slot for a raw
>=3-independent-link proposal close enough to subtract the actual witness.
Because a propagation screen can only remove links, every later qualifying
cluster centre must already be a qualifying raw proposal centre.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from collections import defaultdict
from pathlib import Path
from typing import Mapping, Sequence

import numpy as np


CODE_DIRECTORY = Path(__file__).resolve().parent
SOURCE_DIRECTORY = CODE_DIRECTORY.parent
DATA_DIRECTORY = SOURCE_DIRECTORY / "data" / "known-flight"
sys.path.insert(0, str(CODE_DIRECTORY))

import audit_known_flight_locator_uncertainty as uncertainty
import run_locator_witness_pharlap as witness_runner
import wspr_pharlap_control as control


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def perturbed_epoch(
    epoch_id: str,
    sample_index: int,
    pairs_path: Path,
    spots_path: Path,
    truth_path: Path,
    seed: int,
) -> tuple[
    dict[tuple[str, str], list[uncertainty.Pair]],
    dict[int, uncertainty.Spot],
    uncertainty.Truth,
]:
    audit_spots, nearest_pairs, truths = uncertainty.read_inputs(
        pairs_path, spots_path, truth_path
    )
    all_pairs = tuple(
        pair
        for pair in control.read_candidate_pairs(pairs_path, "known-flight")
        if pair.epoch_id == epoch_id
    )
    source_spots = control.read_spot_records(spots_path)
    nearest_spot_ids = sorted({
        spot_id
        for pair in nearest_pairs
        for spot_id in (pair.spot_id_1, pair.spot_id_2)
    })
    sobol_stations = tuple(sorted({
        key
        for spot_id in nearest_spot_ids
        for key in (
            audit_spots[spot_id].transmitter_key,
            audit_spots[spot_id].receiver_key,
        )
    }))
    coordinates = witness_runner.station_assignment(
        sobol_stations, sample_index, seed
    )
    used_spot_ids = sorted({
        spot_id for pair in all_pairs for spot_id in pair.spot_ids
    })
    spots: dict[int, uncertainty.Spot] = {}
    for spot_id in used_spot_ids:
        source = source_spots[spot_id]
        spot = uncertainty.Spot(
            spot_id,
            source.transmitter,
            source.receiver,
            source.transmitter_locator,
            source.receiver_locator,
        )
        spots[spot_id] = spot
        for station in (spot.transmitter_key, spot.receiver_key):
            coordinates.setdefault(
                station, control.maidenhead_six_character_center(station[1])
            )
    vectors = {
        station: uncertainty.scalar_unit_vector(*position)
        for station, position in coordinates.items()
    }
    normals: dict[int, np.ndarray] = {}
    for spot_id, spot in spots.items():
        normal = np.cross(vectors[spot.transmitter_key], vectors[spot.receiver_key])
        normals[spot_id] = normal / np.linalg.norm(normal)

    groups: dict[tuple[str, str], list[uncertainty.Pair]] = defaultdict(list)
    for pair in all_pairs:
        first, second = normals[pair.spot_id_1], normals[pair.spot_id_2]
        angle = float(np.degrees(np.arccos(np.clip(abs(float(first @ second)), 0.0, 1.0))))
        if angle < uncertainty.MINIMUM_CROSSING_ANGLE_DEG:
            continue
        point = np.cross(first, second)
        point /= np.linalg.norm(point)
        frozen = uncertainty.scalar_unit_vector(pair.latitude_deg, pair.longitude_deg_e)
        if float(point @ frozen) < 0.0:
            point *= -1.0
        groups[(pair.condition, pair.physical_slot)].append(uncertainty.Pair(
            pair.candidate_id,
            pair.epoch_id,
            pair.physical_slot,
            pair.spot_id_1,
            pair.spot_id_2,
            float(np.degrees(np.arcsin(np.clip(point[2], -1.0, 1.0)))),
            float(np.degrees(np.arctan2(point[1], point[0]))),
        ))
    return dict(groups), spots, truths[epoch_id]


def strict_proposals(
    groups: Mapping[tuple[str, str], Sequence[uncertainty.Pair]],
    spots: Mapping[int, uncertainty.Spot],
) -> list[dict[str, object]]:
    proposals: list[dict[str, object]] = []
    for (condition, physical_slot), pairs in sorted(groups.items()):
        positions = np.asarray([
            (pair.latitude_deg, pair.longitude_deg_e) for pair in pairs
        ])
        vectors = uncertainty.unit_vector(positions[:, 0], positions[:, 1])
        distances = uncertainty.EARTH_MEAN_RADIUS_KM * np.arccos(
            np.clip(vectors @ vectors.T, -1.0, 1.0)
        )
        for center, pair in enumerate(pairs):
            neighbors = np.flatnonzero(distances[center] <= uncertainty.CLUSTER_RADIUS_KM)
            spot_ids = {
                spot_id
                for index in neighbors
                for spot_id in (pairs[index].spot_id_1, pairs[index].spot_id_2)
            }
            independent = uncertainty.maximum_independent_links(spot_ids, spots)
            if independent < 3:
                continue
            proposals.append({
                "condition": condition,
                "physical_slot": physical_slot,
                "center_candidate_id": pair.candidate_id,
                "latitude_deg": pair.latitude_deg,
                "longitude_deg_e": pair.longitude_deg_e,
                "independent_links": independent,
                "pair_intersections": len(neighbors),
            })
    return proposals


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--audit", type=Path, required=True)
    parser.add_argument("--epoch", default="mh370_1642")
    parser.add_argument("--sample-index", type=int, default=23526)
    parser.add_argument("--actual-center-candidate", default="known-flight:mh370_1642:00000658")
    parser.add_argument("--pairs", type=Path, default=DATA_DIRECTORY / "known_flight_pair_locations.csv.gz")
    parser.add_argument("--spots", type=Path, default=DATA_DIRECTORY / "known_flight_spot_records.csv.gz")
    parser.add_argument("--truth", type=Path, default=DATA_DIRECTORY / "known_flight_truth_references.csv")
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    audit_document = json.loads(args.audit.read_text())
    groups, spots, truth = perturbed_epoch(
        args.epoch,
        args.sample_index,
        args.pairs,
        args.spots,
        args.truth,
        int(audit_document["seed"]),
    )
    proposals = strict_proposals(groups, spots)
    actual_pairs = groups[("actual_time", truth.physical_slot)]
    actual = next(
        pair for pair in actual_pairs
        if pair.candidate_id == args.actual_center_candidate
    )
    control_proposals = [
        proposal for proposal in proposals
        if proposal["condition"] != "actual_time"
    ]
    for proposal in proposals:
        proposal["distance_to_actual_witness_center_km"] = (
            control.great_circle_distance_km(
                actual.latitude_deg,
                actual.longitude_deg_e,
                float(proposal["latitude_deg"]),
                float(proposal["longitude_deg_e"]),
            )
        )
    minimum_control = min(
        float(proposal["distance_to_actual_witness_center_km"])
        for proposal in control_proposals
    )
    document = {
        "schema": "mh370.wspr.locator-witness-control-geometry.v1",
        "scope": (
            "All cell-centre-retained pairs for one epoch, with one coherent "
            "in-cell coordinate completion; no excluded pair is rematerialized."
        ),
        "logical_bound": (
            "Propagation filtering can only remove links. Every screened >=3-link "
            "cluster centre must therefore be an already qualifying raw proposal centre."
        ),
        "epoch_id": args.epoch,
        "sample_index_zero_based": args.sample_index,
        "actual_center_candidate_id": actual.candidate_id,
        "actual_center_latitude_deg": actual.latitude_deg,
        "actual_center_longitude_deg_e": actual.longitude_deg_e,
        "retained_epoch_pair_count": sum(len(pairs) for pairs in groups.values()),
        "strict_raw_proposal_count": len(proposals),
        "strict_control_proposal_count": len(control_proposals),
        "minimum_control_proposal_distance_to_actual_center_km": minimum_control,
        "residual_tolerance_km": 25.0,
        "no_screened_control_can_subtract_within_frozen_pair_universe": (
            minimum_control > 25.0
        ),
        "limitations": [
            "truth-selected coordinate sensitivity, not a blind detection",
            "pairs excluded by the original map/100-NM filter are absent",
            "newly entering pairs could change the control field after full rematerialization",
        ],
        "inputs": {
            "audit_sha256": sha256_file(args.audit),
            "pairs_sha256": sha256_file(args.pairs),
            "spots_sha256": sha256_file(args.spots),
            "truth_sha256": sha256_file(args.truth),
            "source_sha256": sha256_file(Path(__file__).resolve()),
        },
        "strict_raw_proposals": sorted(
            proposals,
            key=lambda proposal: (
                float(proposal["distance_to_actual_witness_center_km"]),
                str(proposal["condition"]),
                str(proposal["physical_slot"]),
                str(proposal["center_candidate_id"]),
            ),
        ),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(document, indent=2, sort_keys=True) + "\n")
    print(json.dumps({
        key: value for key, value in document.items()
        if key != "strict_raw_proposals"
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
