#!/usr/bin/env python3
"""Stress-test known-flight intersections against Maidenhead cell uncertainty.

The frozen known-flight experiment uses the centre of every six-character
Maidenhead locator.  That is a reproducible convention, but it is not a
measurement of an antenna's exact position.  This audit varies every station
inside its reported locator cell while preserving one coherent position for a
``(callsign, locator)`` station across all links and epochs in a realization.

This is deliberately a geometry-only necessary-condition test.  It does not
rerun PHaRLAP and therefore cannot establish a detection.  Conversely, if no
raw >=3-independent-link cluster can occur near withheld truth, no later
propagation screen can create one from the same candidate pairs.
"""

from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import json
import math
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Mapping, Sequence

import numpy as np
from scipy.stats import qmc


CODE_DIRECTORY = Path(__file__).resolve().parent
SOURCE_DIRECTORY = CODE_DIRECTORY.parent
DATA_DIRECTORY = SOURCE_DIRECTORY / "data" / "known-flight"
EARTH_MEAN_RADIUS_KM = 6371.0088
MINIMUM_CROSSING_ANGLE_DEG = 20.0
CLUSTER_RADIUS_KM = 25.0
TRUTH_TOLERANCES_KM = (25.0, 50.0)
DEFAULT_SEED = 370371
DEFAULT_SAMPLE_POWER = 17


@dataclass(frozen=True)
class Spot:
    spot_id: int
    transmitter: str
    receiver: str
    transmitter_locator: str
    receiver_locator: str

    @property
    def transmitter_key(self) -> tuple[str, str]:
        return self.transmitter, self.transmitter_locator

    @property
    def receiver_key(self) -> tuple[str, str]:
        return self.receiver, self.receiver_locator


@dataclass(frozen=True)
class Pair:
    candidate_id: str
    epoch_id: str
    physical_slot: str
    spot_id_1: int
    spot_id_2: int
    latitude_deg: float
    longitude_deg_e: float


@dataclass(frozen=True)
class Truth:
    epoch_id: str
    physical_slot: str
    latitude_deg: float
    longitude_deg_e: float
    altitude_km: float


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def open_csv(path: Path):
    return gzip.open(path, "rt", newline="") if path.suffix == ".gz" else path.open(newline="")


def maidenhead_cell_bounds(locator: str) -> tuple[float, float, float, float]:
    """Return south, north, west, east bounds for one six-character cell."""
    value = locator.strip().upper()
    if not (
        len(value) == 6
        and "A" <= value[0] <= "R"
        and "A" <= value[1] <= "R"
        and value[2:4].isdigit()
        and "A" <= value[4] <= "X"
        and "A" <= value[5] <= "X"
    ):
        raise ValueError(f"invalid six-character Maidenhead locator: {locator!r}")
    west = (
        -180.0
        + (ord(value[0]) - ord("A")) * 20.0
        + int(value[2]) * 2.0
        + (ord(value[4]) - ord("A")) / 12.0
    )
    south = (
        -90.0
        + (ord(value[1]) - ord("A")) * 10.0
        + int(value[3])
        + (ord(value[5]) - ord("A")) / 24.0
    )
    return south, south + 1.0 / 24.0, west, west + 1.0 / 12.0


def unit_vector(latitude_deg: np.ndarray, longitude_deg_e: np.ndarray) -> np.ndarray:
    latitude = np.radians(latitude_deg)
    longitude = np.radians(longitude_deg_e)
    cosine = np.cos(latitude)
    return np.stack(
        (cosine * np.cos(longitude), cosine * np.sin(longitude), np.sin(latitude)),
        axis=-1,
    )


def scalar_unit_vector(latitude_deg: float, longitude_deg_e: float) -> np.ndarray:
    return unit_vector(np.asarray(latitude_deg), np.asarray(longitude_deg_e))


def angular_distance_km(first: np.ndarray, second: np.ndarray) -> np.ndarray:
    dots = np.einsum("...i,...i->...", first, second)
    return EARTH_MEAN_RADIUS_KM * np.arccos(np.clip(dots, -1.0, 1.0))


def read_inputs(
    pair_path: Path,
    spot_path: Path,
    truth_path: Path,
) -> tuple[dict[int, Spot], tuple[Pair, ...], dict[str, Truth]]:
    spots: dict[int, Spot] = {}
    with open_csv(spot_path) as handle:
        for row in csv.DictReader(handle):
            spot = Spot(
                spot_id=int(row["id"]),
                transmitter=row["tx_sign"],
                receiver=row["rx_sign"],
                transmitter_locator=row["tx_loc"].strip().upper(),
                receiver_locator=row["rx_loc"].strip().upper(),
            )
            if spot.spot_id in spots and spots[spot.spot_id] != spot:
                raise ValueError(f"conflicting spot metadata for {spot.spot_id}")
            spots[spot.spot_id] = spot

    truths: dict[str, Truth] = {}
    with open_csv(truth_path) as handle:
        for row in csv.DictReader(handle):
            if row["reference_role"] != "physical_slot" or row["is_nearest_arc_slot"] != "True":
                continue
            truth = Truth(
                epoch_id=row["epoch_id"],
                physical_slot=row["physical_slot"],
                latitude_deg=float(row["latitude_deg"]),
                longitude_deg_e=float(row["longitude_deg_e"]),
                altitude_km=float(row["altitude_km"]),
            )
            if truth.epoch_id in truths:
                raise ValueError(f"duplicate nearest-slot truth for {truth.epoch_id}")
            truths[truth.epoch_id] = truth

    pairs: list[Pair] = []
    with open_csv(pair_path) as handle:
        for row_number, row in enumerate(csv.DictReader(handle), 1):
            epoch_id = row["epoch"]
            if row["condition"] != "actual_time":
                continue
            truth = truths.get(epoch_id)
            if truth is None or row["physical_slot"] != truth.physical_slot:
                continue
            pair = Pair(
                candidate_id=f"known-flight:{epoch_id}:{row_number:08d}",
                epoch_id=epoch_id,
                physical_slot=row["physical_slot"],
                spot_id_1=int(row["spot_id_1"]),
                spot_id_2=int(row["spot_id_2"]),
                latitude_deg=float(row["lat_deg"]),
                longitude_deg_e=float(row["lon_deg_E"]),
            )
            for spot_id in (pair.spot_id_1, pair.spot_id_2):
                if spot_id not in spots:
                    raise ValueError(f"candidate references missing spot {spot_id}")
            pairs.append(pair)
    if not pairs or set(truths) != {pair.epoch_id for pair in pairs}:
        raise ValueError("nearest-slot candidate/truth epoch coverage is incomplete")
    return spots, tuple(pairs), truths


def maximum_independent_links(
    spot_ids: Iterable[int], spots: Mapping[int, Spot]
) -> int:
    adjacency: dict[str, set[str]] = defaultdict(set)
    for spot_id in set(spot_ids):
        spot = spots[spot_id]
        adjacency[spot.transmitter].add(spot.receiver)
    matched_receiver: dict[str, str] = {}

    def augment(transmitter: str, seen: set[str]) -> bool:
        for receiver in sorted(adjacency[transmitter]):
            if receiver in seen:
                continue
            seen.add(receiver)
            if receiver not in matched_receiver or augment(matched_receiver[receiver], seen):
                matched_receiver[receiver] = transmitter
                return True
        return False

    return sum(augment(transmitter, set()) for transmitter in sorted(adjacency))


def selected_clusters(
    pair_positions: np.ndarray,
    valid: np.ndarray,
    pairs: Sequence[Pair],
    spots: Mapping[int, Spot],
    radius_km: float,
) -> tuple[tuple[int, int, tuple[int, ...]], ...]:
    """Return (centre, independent links, neighbour indices) as production."""
    valid_indices = np.flatnonzero(valid)
    if not len(valid_indices):
        return ()
    vectors = unit_vector(pair_positions[valid_indices, 0], pair_positions[valid_indices, 1])
    distances = EARTH_MEAN_RADIUS_KM * np.arccos(
        np.clip(vectors @ vectors.T, -1.0, 1.0)
    )
    proposals: list[tuple[int, int, int, int, tuple[int, ...], str]] = []
    for local_center, global_center in enumerate(valid_indices):
        local_neighbors = np.flatnonzero(distances[local_center] <= radius_km)
        global_neighbors = tuple(int(valid_indices[index]) for index in local_neighbors)
        spot_ids = tuple(sorted({
            spot_id
            for index in global_neighbors
            for spot_id in (pairs[index].spot_id_1, pairs[index].spot_id_2)
        }))
        independent = maximum_independent_links(spot_ids, spots)
        proposals.append(
            (
                int(global_center),
                independent,
                len(spot_ids),
                len(global_neighbors),
                global_neighbors,
                pairs[global_center].candidate_id,
            )
        )
    proposals.sort(key=lambda item: (-item[1], -item[2], -item[3], item[5]))
    selected: list[tuple[int, int, int, int, tuple[int, ...], str]] = []
    local_by_global = {int(global_index): local for local, global_index in enumerate(valid_indices)}
    for proposal in proposals:
        local_center = local_by_global[proposal[0]]
        if any(
            distances[local_center, local_by_global[prior[0]]] <= radius_km
            for prior in selected
        ):
            continue
        selected.append(proposal)
    return tuple(
        (proposal[0], proposal[1], proposal[4])
        for proposal in selected
        if proposal[1] >= 3
    )


def station_points(
    uniforms: np.ndarray,
    stations: Sequence[tuple[str, str]],
) -> np.ndarray:
    """Convert Sobol coordinates to points uniform in cell surface area."""
    count = uniforms.shape[0]
    points = np.empty((count, len(stations), 3), dtype=np.float64)
    for station_index, (_callsign, locator) in enumerate(stations):
        south, north, west, east = maidenhead_cell_bounds(locator)
        sine_south, sine_north = math.sin(math.radians(south)), math.sin(math.radians(north))
        sine_latitude = sine_south + uniforms[:, 2 * station_index] * (sine_north - sine_south)
        latitude = np.degrees(np.arcsin(sine_latitude))
        longitude = west + uniforms[:, 2 * station_index + 1] * (east - west)
        points[:, station_index] = unit_vector(latitude, longitude)
    return points


def evaluate(
    spots: Mapping[int, Spot],
    all_pairs: Sequence[Pair],
    truths: Mapping[str, Truth],
    sample_power: int,
    seed: int,
    cluster_radius_km: float = CLUSTER_RADIUS_KM,
    truth_tolerances_km: Sequence[float] = TRUTH_TOLERANCES_KM,
    batch_size: int = 2048,
) -> tuple[list[dict[str, object]], dict[str, object]]:
    used_spot_ids = sorted({spot_id for pair in all_pairs for spot_id in (pair.spot_id_1, pair.spot_id_2)})
    stations = sorted({
        key
        for spot_id in used_spot_ids
        for key in (spots[spot_id].transmitter_key, spots[spot_id].receiver_key)
    })
    station_index = {key: index for index, key in enumerate(stations)}
    spot_order = {spot_id: index for index, spot_id in enumerate(used_spot_ids)}
    spot_endpoint_indices = np.asarray([
        (
            station_index[spots[spot_id].transmitter_key],
            station_index[spots[spot_id].receiver_key],
        )
        for spot_id in used_spot_ids
    ], dtype=np.int64)
    pairs_by_epoch: dict[str, list[Pair]] = defaultdict(list)
    for pair in all_pairs:
        pairs_by_epoch[pair.epoch_id].append(pair)

    # Reconstruct the frozen candidates at u=v=0.5 before sampling.  This is
    # an independent guard against a locator decoder or branch-selection error
    # masquerading as sensitivity.
    center_vectors = station_points(
        np.full((1, 2 * len(stations)), 0.5, dtype=np.float64), stations
    )
    center_tx = center_vectors[:, spot_endpoint_indices[:, 0]]
    center_rx = center_vectors[:, spot_endpoint_indices[:, 1]]
    center_normals = np.cross(center_tx, center_rx)
    center_normals /= np.linalg.norm(center_normals, axis=2)[:, :, None]
    maximum_center_reconstruction_error_km = 0.0
    for pair in all_pairs:
        intersection = np.cross(
            center_normals[0, spot_order[pair.spot_id_1]],
            center_normals[0, spot_order[pair.spot_id_2]],
        )
        intersection /= np.linalg.norm(intersection)
        frozen = scalar_unit_vector(pair.latitude_deg, pair.longitude_deg_e)
        if float(intersection @ frozen) < 0.0:
            intersection *= -1.0
        maximum_center_reconstruction_error_km = max(
            maximum_center_reconstruction_error_km,
            float(angular_distance_km(intersection, frozen)),
        )
    if maximum_center_reconstruction_error_km > 0.002:
        raise ValueError(
            "cell-centre geometry does not reproduce the frozen candidate table: "
            f"{maximum_center_reconstruction_error_km:.6f} km"
        )

    epoch_state: dict[str, dict[str, object]] = {}
    for epoch_id, epoch_pairs in sorted(pairs_by_epoch.items()):
        baseline_vectors = unit_vector(
            np.asarray([pair.latitude_deg for pair in epoch_pairs]),
            np.asarray([pair.longitude_deg_e for pair in epoch_pairs]),
        )
        truth_vector = scalar_unit_vector(
            truths[epoch_id].latitude_deg, truths[epoch_id].longitude_deg_e
        )
        baseline_truth_distances = angular_distance_km(baseline_vectors, truth_vector)
        epoch_state[epoch_id] = {
            "pairs": epoch_pairs,
            "baseline_vectors": baseline_vectors,
            "truth_vector": truth_vector,
            "baseline_minimum_truth_distance_km": float(np.min(baseline_truth_distances)),
            "sample_minimum_raw_truth_distance_km": math.inf,
            "maximum_intersection_shift_km": 0.0,
            "raw_within": {float(value): 0 for value in truth_tolerances_km},
            "cluster_within": {float(value): 0 for value in truth_tolerances_km},
            "minimum_cluster_truth_distance_km": math.inf,
            "maximum_near_truth_independent_links": 0,
            "best_sample_index": None,
            "best_candidate_id": None,
            "best_cluster_witness": None,
            "primary_tolerance_witnesses": [],
        }

    total_samples = 1 << sample_power
    sampler = qmc.Sobol(d=2 * len(stations), scramble=True, seed=seed)
    generated = 0
    while generated < total_samples:
        this_batch = min(batch_size, total_samples - generated)
        uniforms = sampler.random(this_batch)
        station_vectors = station_points(uniforms, stations)
        tx = station_vectors[:, spot_endpoint_indices[:, 0]]
        rx = station_vectors[:, spot_endpoint_indices[:, 1]]
        normals = np.cross(tx, rx)
        normal_lengths = np.linalg.norm(normals, axis=2)
        normals /= normal_lengths[:, :, None]

        for epoch_id, state in epoch_state.items():
            epoch_pairs = state["pairs"]
            first = np.asarray([spot_order[pair.spot_id_1] for pair in epoch_pairs])
            second = np.asarray([spot_order[pair.spot_id_2] for pair in epoch_pairs])
            first_normals, second_normals = normals[:, first], normals[:, second]
            normal_dots = np.einsum("bpi,bpi->bp", first_normals, second_normals)
            crossing_angles = np.degrees(np.arccos(np.clip(np.abs(normal_dots), 0.0, 1.0)))
            intersections = np.cross(first_normals, second_normals)
            intersection_lengths = np.linalg.norm(intersections, axis=2)
            valid = (
                (normal_lengths[:, first] > 1e-12)
                & (normal_lengths[:, second] > 1e-12)
                & (intersection_lengths > 1e-12)
                & (crossing_angles >= MINIMUM_CROSSING_ANGLE_DEG)
            )
            intersections /= intersection_lengths[:, :, None]
            baseline_vectors = state["baseline_vectors"]
            branch_dots = np.einsum("bpi,pi->bp", intersections, baseline_vectors)
            intersections = np.where(branch_dots[:, :, None] < 0.0, -intersections, intersections)
            truth_distances = angular_distance_km(intersections, state["truth_vector"])
            truth_distances[~valid] = math.inf
            shifts = angular_distance_km(intersections, np.broadcast_to(baseline_vectors, intersections.shape))
            shifts[~valid] = 0.0
            state["maximum_intersection_shift_km"] = max(
                float(state["maximum_intersection_shift_km"]), float(np.max(shifts))
            )
            batch_minima = np.min(truth_distances, axis=1)
            best_local = int(np.argmin(batch_minima))
            if batch_minima[best_local] < float(state["sample_minimum_raw_truth_distance_km"]):
                candidate_local = int(np.argmin(truth_distances[best_local]))
                state["sample_minimum_raw_truth_distance_km"] = float(batch_minima[best_local])
                state["best_sample_index"] = generated + best_local
                state["best_candidate_id"] = epoch_pairs[candidate_local].candidate_id
            for tolerance in truth_tolerances_km:
                state["raw_within"][float(tolerance)] += int(np.count_nonzero(batch_minima <= tolerance))

            possible = np.flatnonzero(batch_minima <= max(truth_tolerances_km))
            for local_sample in possible:
                sample_positions = np.column_stack((
                    np.degrees(np.arcsin(np.clip(intersections[local_sample, :, 2], -1.0, 1.0))),
                    np.degrees(np.arctan2(
                        intersections[local_sample, :, 1], intersections[local_sample, :, 0]
                    )),
                ))
                clusters = selected_clusters(
                    sample_positions,
                    valid[local_sample],
                    epoch_pairs,
                    spots,
                    cluster_radius_km,
                )
                if not clusters:
                    continue
                cluster_indices = np.asarray([cluster[0] for cluster in clusters], dtype=np.int64)
                cluster_distances = truth_distances[local_sample, cluster_indices]
                for cluster, distance in zip(clusters, cluster_distances):
                    if distance <= min(truth_tolerances_km):
                        center_index, independent_links, neighbor_indices = cluster
                        state["primary_tolerance_witnesses"].append({
                            "sample_index_zero_based": generated + int(local_sample),
                            "center_candidate_id": epoch_pairs[center_index].candidate_id,
                            "center_truth_distance_km": float(distance),
                            "independent_links": independent_links,
                            "neighbor_candidate_ids": [
                                epoch_pairs[index].candidate_id
                                for index in neighbor_indices
                            ],
                        })
                nearest_cluster_local = int(np.argmin(cluster_distances))
                nearest_distance = float(cluster_distances[nearest_cluster_local])
                if nearest_distance < float(state["minimum_cluster_truth_distance_km"]):
                    cluster = clusters[nearest_cluster_local]
                    center_index, independent_links, neighbor_indices = cluster
                    relevant_spot_ids = sorted({
                        spot_id
                        for neighbor_index in neighbor_indices
                        for spot_id in (
                            epoch_pairs[neighbor_index].spot_id_1,
                            epoch_pairs[neighbor_index].spot_id_2,
                        )
                    })
                    relevant_station_indices = sorted({
                        station_index[key]
                        for spot_id in relevant_spot_ids
                        for key in (
                            spots[spot_id].transmitter_key,
                            spots[spot_id].receiver_key,
                        )
                    })
                    witness_station_vectors = station_vectors[local_sample, relevant_station_indices]
                    witness_station_latitudes = np.degrees(np.arcsin(
                        np.clip(witness_station_vectors[:, 2], -1.0, 1.0)
                    ))
                    witness_station_longitudes = np.degrees(np.arctan2(
                        witness_station_vectors[:, 1], witness_station_vectors[:, 0]
                    ))
                    state["minimum_cluster_truth_distance_km"] = nearest_distance
                    state["best_cluster_witness"] = {
                        "sample_index_zero_based": generated + int(local_sample),
                        "center_candidate_id": epoch_pairs[center_index].candidate_id,
                        "center_truth_distance_km": nearest_distance,
                        "independent_links": independent_links,
                        "neighbor_candidate_ids": [
                            epoch_pairs[index].candidate_id for index in neighbor_indices
                        ],
                        "neighbor_candidates": [
                            {
                                "candidate_id": epoch_pairs[index].candidate_id,
                                "spot_id_1": epoch_pairs[index].spot_id_1,
                                "spot_id_2": epoch_pairs[index].spot_id_2,
                                "latitude_deg": float(sample_positions[index, 0]),
                                "longitude_deg_e": float(sample_positions[index, 1]),
                                "truth_distance_km": float(truth_distances[local_sample, index]),
                                "crossing_angle_deg": float(crossing_angles[local_sample, index]),
                            }
                            for index in neighbor_indices
                        ],
                        "relevant_station_coordinates": [
                            {
                                "callsign": stations[index][0],
                                "locator": stations[index][1],
                                "latitude_deg": float(latitude),
                                "longitude_deg_e": float(longitude),
                            }
                            for index, latitude, longitude in zip(
                                relevant_station_indices,
                                witness_station_latitudes,
                                witness_station_longitudes,
                            )
                        ],
                    }
                for tolerance in truth_tolerances_km:
                    within = cluster_distances <= tolerance
                    if np.any(within):
                        state["cluster_within"][float(tolerance)] += 1
                        state["maximum_near_truth_independent_links"] = max(
                            int(state["maximum_near_truth_independent_links"]),
                            max(
                                cluster[1]
                                for cluster, is_within in zip(clusters, within)
                                if is_within
                            ),
                        )
        generated += this_batch

    rows: list[dict[str, object]] = []
    for epoch_id, state in epoch_state.items():
        row: dict[str, object] = {
            "epoch_id": epoch_id,
            "physical_slot": truths[epoch_id].physical_slot,
            "candidate_pair_count": len(state["pairs"]),
            "station_count": len({
                key
                for pair in state["pairs"]
                for spot_id in (pair.spot_id_1, pair.spot_id_2)
                for key in (spots[spot_id].transmitter_key, spots[spot_id].receiver_key)
            }),
            "baseline_minimum_raw_truth_distance_km": state["baseline_minimum_truth_distance_km"],
            "sample_minimum_raw_truth_distance_km": state["sample_minimum_raw_truth_distance_km"],
            "maximum_intersection_shift_km": state["maximum_intersection_shift_km"],
            "minimum_selected_cluster_truth_distance_among_raw_within_search_km": (
                "" if math.isinf(float(state["minimum_cluster_truth_distance_km"]))
                else state["minimum_cluster_truth_distance_km"]
            ),
            "maximum_near_truth_independent_links": state["maximum_near_truth_independent_links"],
            "best_raw_sample_index": state["best_sample_index"],
            "best_raw_candidate_id": state["best_candidate_id"],
        }
        for tolerance in truth_tolerances_km:
            label = f"{float(tolerance):g}km"
            row[f"samples_with_raw_pair_within_{label}"] = state["raw_within"][float(tolerance)]
            row[f"samples_with_qualifying_cluster_within_{label}"] = state["cluster_within"][float(tolerance)]
        rows.append(row)
    audit = {
        "schema": "mh370.wspr.known-flight-locator-uncertainty-audit.v1",
        "scope": (
            "Geometry-only stress test of already frozen anomalous pair candidates at "
            "the nearest actual-time WSPR slot; PHaRLAP is not rerun."
        ),
        "interpretation": (
            "The scrambled Sobol sample is a sensitivity design, not a calibrated "
            "probability distribution for antenna locations."
        ),
        "coherence_key": "one surface-uniform point per (callsign, six-character locator) per realization",
        "sample_method": "scrambled Sobol low-discrepancy sequence",
        "seed": seed,
        "sample_power": sample_power,
        "sample_count": total_samples,
        "global_station_count": len(stations),
        "selected_spot_count": len(used_spot_ids),
        "selected_candidate_pair_count": len(all_pairs),
        "maximum_cell_center_reconstruction_error_km": (
            maximum_center_reconstruction_error_km
        ),
        "minimum_crossing_angle_deg": MINIMUM_CROSSING_ANGLE_DEG,
        "cluster_radius_km": cluster_radius_km,
        "minimum_independent_links": 3,
        "truth_tolerances_km": list(truth_tolerances_km),
        "cluster_distance_search_precondition": (
            "selected clusters were evaluated only in realizations having at "
            f"least one raw pair within {max(truth_tolerances_km):g} km; the "
            "reported minimum is not a global minimum outside that subset"
        ),
        "nearest_cluster_witnesses": {
            epoch_id: state["best_cluster_witness"]
            for epoch_id, state in epoch_state.items()
            if state["best_cluster_witness"] is not None
        },
        "primary_tolerance_witnesses": {
            epoch_id: state["primary_tolerance_witnesses"]
            for epoch_id, state in epoch_state.items()
            if state["primary_tolerance_witnesses"]
        },
    }
    return rows, audit


def write_outputs(rows: Sequence[Mapping[str, object]], audit: Mapping[str, object], output: Path) -> None:
    output.mkdir(parents=True, exist_ok=True)
    csv_path = output / "known-flight-locator-uncertainty-audit.csv"
    with csv_path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    json_path = output / "known-flight-locator-uncertainty-audit.json"
    json_path.write_text(json.dumps({**audit, "results": list(rows)}, indent=2, sort_keys=True) + "\n")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pairs", type=Path, default=DATA_DIRECTORY / "known_flight_pair_locations.csv.gz")
    parser.add_argument("--spots", type=Path, default=DATA_DIRECTORY / "known_flight_spot_records.csv.gz")
    parser.add_argument("--truth", type=Path, default=DATA_DIRECTORY / "known_flight_truth_references.csv")
    parser.add_argument("--sample-power", type=int, default=DEFAULT_SAMPLE_POWER)
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    parser.add_argument("--batch-size", type=int, default=2048)
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if not 1 <= args.sample_power <= 24:
        raise ValueError("sample power must be between 1 and 24")
    spots, pairs, truths = read_inputs(args.pairs, args.spots, args.truth)
    rows, audit = evaluate(
        spots,
        pairs,
        truths,
        sample_power=args.sample_power,
        seed=args.seed,
        batch_size=args.batch_size,
    )
    audit = {
        **audit,
        "audit_source_sha256": sha256_file(Path(__file__).resolve()),
        "numerical_environment": {
            "numpy": np.__version__,
            "scipy": __import__("scipy").__version__,
        },
        "inputs": {
            "pairs": {"path": str(args.pairs), "sha256": sha256_file(args.pairs)},
            "spots": {"path": str(args.spots), "sha256": sha256_file(args.spots)},
            "truth": {"path": str(args.truth), "sha256": sha256_file(args.truth)},
        },
    }
    write_outputs(rows, audit, args.output)
    print(json.dumps({"output": str(args.output), "results": rows}, indent=2))


if __name__ == "__main__":
    main()
