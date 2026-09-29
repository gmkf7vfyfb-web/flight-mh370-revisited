#!/usr/bin/env python3
"""Publication figures for blind known-flight WSPR/PHaRLAP controls.

The plotting step is intentionally downstream of candidate generation,
PHaRLAP screening, spatial clustering and symmetric residualization.  Aircraft
truth is read from a separate file only after the residual table has been
loaded.  It is used solely for an overlay and proximity summaries.

Input contract
--------------
``clusters.csv`` contains one row per retained or subtracted cluster and the
columns listed in ``CLUSTER_COLUMNS``.  The three-condition figures draw only
rows with ``is_residual=true``; companion one-column figures draw every raw
cluster in the central arc-time condition before residual subtraction.
``arcs.csv`` contains an ordered polyline for every epoch.
``truth.csv`` contains post-selection arc and slot aircraft references,
including source and time offset. ``truth-scores.csv`` contains the
authoritative recovery calculation from surviving pre-collapse source
centres/heights. ``run-metadata.json`` records the frozen physical and control
settings and must explicitly state that truth was not used during selection.
``tracks.csv`` and its provenance JSON supply independently frozen ACARS report
positions for an arc-time-panel context overlay only; neither enters selection
or scoring, and the lines between reports are not continuously observed.

Each flight is drawn as epoch rows by three condition columns: minus 60
minutes, actual time and plus 60 minutes.  The raw companion has one central-
condition column. Pages contain at most three epochs.  Each epoch row has a
latitude range symmetric about withheld truth and shared by all conditions;
it is expanded as needed so that no frozen-domain arc or cluster is clipped.
A geographic scale ruler is drawn in the right-hand panel of every row.  A
paired summary CSV, raw summary CSV, lossless cluster-to-plot audit and hash
manifest accompany the PNG, PDF and SVG figures.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import platform
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from statistics import median
from typing import Iterable, Mapping, Sequence


METADATA_SCHEMA = "mh370.wspr.pharlap.known-flight-control-run.v1"
TRACK_PROVENANCE_SCHEMA = "mh370.wspr.known-flight-track-provenance.v1"
TRACK_SCHEMA = "mh370.wspr.known-flight-track-observations.v1"
CONDITIONS = ("minus_60_min", "actual_time", "plus_60_min")
CONDITION_LABELS = {
    "minus_60_min": "Control: −60 min",
    "actual_time": "Arc-time window",
    "plus_60_min": "Control: +60 min",
}
SCREENS = ("surface_endpoint", "common_aircraft_altitude")
SENSITIVITY_SCREEN = "common_aircraft_altitude_exact_sensitivity"
KNOWN_SCREENS = SCREENS + (SENSITIVITY_SCREEN,)
SCREEN_LABELS = {
    "surface_endpoint": "surface-endpoint propagation screen",
    "common_aircraft_altitude": "common-aircraft-altitude propagation screen",
    SENSITIVITY_SCREEN: "exact-altitude residual-matching sensitivity",
}
EARTH_MEAN_RADIUS_KM = 6371.0088

CLUSTER_COLUMNS = {
    "epoch_id",
    "flight",
    "arc_time_utc",
    "condition",
    "screen",
    "physical_slot",
    "cluster_rank",
    "center_candidate_id",
    "latitude_deg",
    "longitude_deg_e",
    "pair_intersections",
    "support_links",
    "independent_links",
    "altitude_km",
    "altitude_minimum_km",
    "altitude_maximum_km",
    "feasible_altitude_count",
    "feasible_altitudes_km",
    "source_altitude_clusters",
    "source_altitude_cluster_ids",
    "support_spot_ids",
    "nearest_other_condition_km",
    "is_residual",
}
RAW_CLUSTER_COLUMNS = CLUSTER_COLUMNS.difference({
    "nearest_other_condition_km", "is_residual"
})
ARC_COLUMNS = {
    "epoch_id",
    "sequence",
    "flight",
    "arc_time_utc",
    "arc_point_index",
    "latitude_deg",
    "longitude_deg_e",
}
TRUTH_COLUMNS = {
    "epoch_id",
    "truth_id",
    "reference_role",
    "physical_slot",
    "is_nearest_arc_slot",
    "position_time_utc",
    "latitude_deg",
    "longitude_deg_e",
    "altitude_km",
    "position_source",
    "position_method",
    "time_offset_seconds",
}
TRUTH_SCORE_COLUMNS = {
    "epoch_id",
    "screen",
    "condition",
    "nearest_physical_slot",
    "truth_id",
    "truth_position_time_utc",
    "truth_latitude_deg",
    "truth_longitude_deg_e",
    "truth_altitude_km",
    "truth_position_source",
    "truth_position_method",
    "truth_time_offset_seconds",
    "eligible_residual_parent_clusters",
    "eligible_surviving_source_clusters",
    "nearest_horizontal_km",
    "nearest_source_cluster_id",
    "nearest_source_altitude_km",
    "nearest_horizontal_source_altitude_gap_km",
    "minimum_altitude_gap_km",
    "joint_clusters_within_tolerance",
    "horizontal_tolerance_km",
    "altitude_tolerance_km",
    "recovered",
    "parent_collapsed_residual_ids",
    "altitude_sensitivity_recovered",
}
TRACK_COLUMNS = {
    "flight",
    "track_point_index",
    "time_utc",
    "latitude_deg",
    "longitude_deg_e",
    "altitude_ft",
    "heading_true_deg",
    "position_source",
    "position_method",
    "source_sheet",
    "source_excel_row",
}

SUMMARY_COLUMNS = (
    "epoch_id",
    "sequence",
    "flight",
    "arc_time_utc",
    "screen",
    "condition",
    "residual_cluster_count",
    "maximum_independent_links",
    "median_independent_links",
    "truth_id",
    "truth_position_time_utc",
    "truth_latitude_deg",
    "truth_longitude_deg_e",
    "truth_altitude_km",
    "truth_position_source",
    "truth_position_method",
    "truth_time_offset_seconds",
    "nearest_arc_epoch_reference_horizontal_km",
    "nearest_cluster_latitude_deg",
    "nearest_cluster_longitude_deg_e",
    "nearest_cluster_altitude_km",
    "nearest_cluster_altitude_minimum_km",
    "nearest_cluster_altitude_maximum_km",
    "nearest_cluster_feasible_altitude_count",
    "nearest_arc_epoch_reference_altitude_difference_km",
    "nearest_cluster_independent_links",
    "nearest_cluster_support_links",
    "nearest_cluster_physical_slot",
    "proximity_interpretation",
    "recovery_physical_slot",
    "recovery_truth_id",
    "recovery_truth_position_time_utc",
    "recovery_truth_latitude_deg",
    "recovery_truth_longitude_deg_e",
    "recovery_truth_altitude_km",
    "recovery_truth_position_source",
    "recovery_truth_position_method",
    "recovery_truth_time_offset_seconds",
    "recovery_slot_residual_cluster_count",
    "recovery_surviving_source_cluster_count",
    "nearest_time_aligned_truth_horizontal_km",
    "nearest_recovery_source_cluster_id",
    "nearest_recovery_source_altitude_km",
    "nearest_time_aligned_truth_altitude_difference_km",
    "minimum_time_aligned_truth_altitude_difference_km",
    "joint_clusters_within_tolerance",
    "recovery_parent_collapsed_residual_ids",
    "recovery_horizontal_tolerance_km",
    "recovery_altitude_tolerance_km",
    "recovery_horizontal_within_tolerance",
    "recovery_altitude_within_tolerance",
    "recovery_altitude_sensitivity_results",
    "recovered_within_tolerance",
    "recovery_interpretation",
    "figure_png",
    "figure_pdf",
    "figure_svg",
)

CLUSTER_PLOT_AUDIT_COLUMNS = (
    "input_row_number",
    "epoch_id",
    "flight",
    "arc_time_utc",
    "screen",
    "condition",
    "physical_slot",
    "cluster_rank",
    "center_candidate_id",
    "latitude_deg",
    "longitude_deg_e",
    "altitude_km",
    "altitude_minimum_km",
    "altitude_maximum_km",
    "feasible_altitude_count",
    "feasible_altitudes_km",
    "source_altitude_clusters",
    "source_altitude_cluster_ids",
    "support_spot_ids",
    "pair_intersections",
    "support_links",
    "independent_links",
    "nearest_other_condition_km",
    "is_residual",
    "plotted",
    "figure_png",
    "figure_pdf",
    "figure_svg",
)

RAW_CLUSTER_PLOT_AUDIT_COLUMNS = tuple(
    value for value in CLUSTER_PLOT_AUDIT_COLUMNS
    if value not in {"nearest_other_condition_km", "is_residual"}
)

RAW_SUMMARY_COLUMNS = (
    "epoch_id",
    "sequence",
    "flight",
    "arc_time_utc",
    "screen",
    "condition",
    "raw_cluster_count",
    "maximum_independent_links",
    "median_independent_links",
    "truth_id",
    "truth_position_time_utc",
    "truth_latitude_deg",
    "truth_longitude_deg_e",
    "truth_altitude_km",
    "truth_position_source",
    "truth_position_method",
    "nearest_arc_epoch_reference_horizontal_km",
    "nearest_cluster_latitude_deg",
    "nearest_cluster_longitude_deg_e",
    "nearest_cluster_altitude_minimum_km",
    "nearest_cluster_altitude_maximum_km",
    "nearest_cluster_independent_links",
    "nearest_cluster_support_links",
    "nearest_cluster_physical_slot",
    "proximity_interpretation",
    "figure_png",
    "figure_pdf",
    "figure_svg",
)


@dataclass(frozen=True)
class ClusterRow:
    input_row_number: int
    epoch_id: str
    flight: str
    arc_time_utc: str
    condition: str
    screen: str
    physical_slot: str
    cluster_rank: int
    center_candidate_id: str
    latitude_deg: float
    longitude_deg_e: float
    pair_intersections: int
    support_links: int
    independent_links: int
    altitude_km: float | None
    altitude_minimum_km: float | None
    altitude_maximum_km: float | None
    feasible_altitude_count: int
    feasible_altitudes_km: tuple[float, ...]
    source_altitude_clusters: int
    source_altitude_cluster_ids: tuple[str, ...]
    support_spot_ids: tuple[int, ...]
    nearest_other_condition_km: float
    is_residual: bool


@dataclass(frozen=True)
class ArcPoint:
    epoch_id: str
    sequence: int
    flight: str
    arc_time_utc: str
    arc_point_index: int
    latitude_deg: float
    longitude_deg_e: float


@dataclass(frozen=True)
class TruthRow:
    epoch_id: str
    truth_id: str
    reference_role: str
    physical_slot: str | None
    is_nearest_arc_slot: bool
    position_time_utc: str
    latitude_deg: float
    longitude_deg_e: float
    altitude_km: float | None
    position_source: str
    position_method: str
    time_offset_seconds: float


@dataclass(frozen=True)
class TruthReferences:
    arc_epoch: Mapping[str, TruthRow]
    nearest_physical_slot: Mapping[str, TruthRow]
    all_physical_slots: Mapping[tuple[str, str], TruthRow]


@dataclass(frozen=True)
class TruthScoreRow:
    epoch_id: str
    condition: str
    screen: str
    nearest_physical_slot: str
    truth_id: str
    truth_position_time_utc: str
    truth_latitude_deg: float
    truth_longitude_deg_e: float
    truth_altitude_km: float | None
    truth_position_source: str
    truth_position_method: str
    truth_time_offset_seconds: float
    eligible_residual_parent_clusters: int
    eligible_surviving_source_clusters: int
    nearest_horizontal_km: float | None
    nearest_source_cluster_id: str | None
    nearest_source_altitude_km: float | None
    nearest_horizontal_source_altitude_gap_km: float | None
    minimum_altitude_gap_km: float | None
    joint_clusters_within_tolerance: int
    horizontal_tolerance_km: float
    altitude_tolerance_km: float | None
    recovered: bool
    parent_collapsed_residual_ids: tuple[str, ...]
    altitude_sensitivity_recovered: Mapping[str, bool]


@dataclass(frozen=True)
class TrackPoint:
    flight: str
    track_point_index: int
    time_utc: str
    latitude_deg: float
    longitude_deg_e: float
    altitude_ft: float
    heading_true_deg: float
    position_source: str
    position_method: str
    source_sheet: str
    source_excel_row: int




def _read_csv(path: Path, required: set[str]) -> list[dict[str, str]]:
    with path.open("r", newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        missing = required.difference(reader.fieldnames or ())
        if missing:
            raise ValueError(f"{path}: missing columns {sorted(missing)}")
        return [dict(row) for row in reader]


def _finite_float(value: str, name: str) -> float:
    parsed = float(value)
    if not math.isfinite(parsed):
        raise ValueError(f"{name} must be finite")
    return parsed


def _optional_float(value: str, name: str) -> float | None:
    return None if value.strip() == "" else _finite_float(value, name)


def _nonnegative_distance(value: str, name: str) -> float:
    parsed = float(value)
    if math.isnan(parsed) or parsed < 0.0:
        raise ValueError(f"{name} must be non-negative")
    return parsed


def _optional_distance(value: str, name: str) -> float | None:
    return None if not value.strip() else _nonnegative_distance(value, name)


def _optional_int(value: str) -> int | None:
    return None if not value.strip() else int(value)


def _altitude_values(value: str) -> tuple[float, ...]:
    if not value.strip():
        return ()
    parsed = tuple(_finite_float(item, "feasible_altitudes_km") for item in value.split(";"))
    if parsed != tuple(sorted(set(parsed))):
        raise ValueError("feasible_altitudes_km must be sorted and unique")
    return parsed


def _string_values(value: str) -> tuple[str, ...]:
    if not value.strip():
        return ()
    parsed = tuple(item for item in value.split(";") if item)
    if len(parsed) != len(set(parsed)):
        raise ValueError("semicolon-delimited identifiers must be unique")
    return parsed


def _integer_values(value: str, name: str) -> tuple[int, ...]:
    if not value.strip():
        return ()
    parsed = tuple(int(item) for item in value.split(";"))
    if len(parsed) != len(set(parsed)):
        raise ValueError(f"{name} must contain unique values")
    return parsed


def _bool(value: str, name: str) -> bool:
    normalized = value.strip().lower()
    if normalized in {"true", "1", "yes"}:
        return True
    if normalized in {"false", "0", "no"}:
        return False
    raise ValueError(f"{name} must be true or false")


def _validate_coordinate(latitude: float, longitude: float, context: str) -> None:
    if not -90.0 <= latitude <= 90.0:
        raise ValueError(f"{context}: latitude outside [-90, 90]")
    if not -180.0 <= longitude <= 180.0:
        raise ValueError(f"{context}: longitude outside [-180, 180]")


def _utc_datetime(value: str, context: str) -> datetime:
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as error:
        raise ValueError(f"{context}: invalid UTC timestamp") from error
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError(f"{context}: timestamp must include a UTC offset")
    if parsed.utcoffset().total_seconds() != 0.0:
        raise ValueError(f"{context}: timestamp must be UTC")
    return parsed.astimezone(timezone.utc)


def read_clusters(
    path: Path, *, raw_input: bool = False
) -> tuple[ClusterRow, ...]:
    rows: list[ClusterRow] = []
    required = RAW_CLUSTER_COLUMNS if raw_input else CLUSTER_COLUMNS
    for index, raw in enumerate(_read_csv(path, required), 2):
        condition = raw["condition"]
        screen = raw["screen"]
        if condition not in CONDITIONS:
            raise ValueError(f"{path}:{index}: unknown condition {condition}")
        if screen not in KNOWN_SCREENS:
            raise ValueError(f"{path}:{index}: unknown screen {screen}")
        latitude = _finite_float(raw["latitude_deg"], "latitude_deg")
        longitude = _finite_float(raw["longitude_deg_e"], "longitude_deg_e")
        _validate_coordinate(latitude, longitude, f"{path}:{index}")
        altitude = _optional_float(raw["altitude_km"], "altitude_km")
        altitude_minimum = _optional_float(
            raw["altitude_minimum_km"], "altitude_minimum_km"
        )
        altitude_maximum = _optional_float(
            raw["altitude_maximum_km"], "altitude_maximum_km"
        )
        altitude_values = _altitude_values(raw["feasible_altitudes_km"])
        altitude_count = int(raw["feasible_altitude_count"])
        source_altitude_clusters = int(raw["source_altitude_clusters"])
        source_altitude_cluster_ids = _string_values(
            raw["source_altitude_cluster_ids"]
        )
        support_spot_ids = _integer_values(raw["support_spot_ids"], "support_spot_ids")
        if screen == "surface_endpoint":
            if any(value is not None for value in (altitude, altitude_minimum, altitude_maximum)):
                raise ValueError(f"{path}:{index}: surface cluster has altitude metadata")
            if (
                altitude_count != 0 or altitude_values
                or source_altitude_clusters != 0 or source_altitude_cluster_ids
            ):
                raise ValueError(f"{path}:{index}: surface cluster has altitude metadata")
        elif screen == "common_aircraft_altitude":
            if altitude is not None:
                raise ValueError(
                    f"{path}:{index}: primary altitude cluster must be spatially collapsed"
                )
            if altitude_minimum is None or altitude_maximum is None:
                raise ValueError(f"{path}:{index}: collapsed altitude range is required")
            if altitude_count != len(altitude_values) or not altitude_values:
                raise ValueError(f"{path}:{index}: inconsistent feasible altitude set")
            if not (
                math.isclose(altitude_minimum, altitude_values[0], abs_tol=1e-9)
                and math.isclose(altitude_maximum, altitude_values[-1], abs_tol=1e-9)
            ):
                raise ValueError(f"{path}:{index}: altitude range does not match set")
            if source_altitude_clusters < 1:
                raise ValueError(f"{path}:{index}: source altitude clusters are required")
            if source_altitude_clusters != len(source_altitude_cluster_ids):
                raise ValueError(f"{path}:{index}: source altitude cluster IDs disagree")
        else:
            if altitude is None:
                raise ValueError(f"{path}:{index}: exact-altitude sensitivity lacks altitude")
        independent = int(raw["independent_links"])
        support = int(raw["support_links"])
        if independent < 1 or support < independent:
            raise ValueError(f"{path}:{index}: invalid link counts")
        if len(support_spot_ids) != support:
            raise ValueError(f"{path}:{index}: support spot IDs disagree with count")
        rows.append(ClusterRow(
            input_row_number=index,
            epoch_id=raw["epoch_id"],
            flight=raw["flight"],
            arc_time_utc=raw["arc_time_utc"],
            condition=condition,
            screen=screen,
            physical_slot=raw["physical_slot"],
            cluster_rank=int(raw["cluster_rank"]),
            center_candidate_id=raw["center_candidate_id"],
            latitude_deg=latitude,
            longitude_deg_e=longitude,
            pair_intersections=int(raw["pair_intersections"]),
            support_links=support,
            independent_links=independent,
            altitude_km=altitude,
            altitude_minimum_km=altitude_minimum,
            altitude_maximum_km=altitude_maximum,
            feasible_altitude_count=altitude_count,
            feasible_altitudes_km=altitude_values,
            source_altitude_clusters=source_altitude_clusters,
            source_altitude_cluster_ids=source_altitude_cluster_ids,
            support_spot_ids=support_spot_ids,
            nearest_other_condition_km=(
                math.inf if raw_input else _nonnegative_distance(
                    raw["nearest_other_condition_km"],
                    "nearest_other_condition_km",
                )
            ),
            is_residual=(
                False if raw_input else _bool(raw["is_residual"], "is_residual")
            ),
        ))
    return tuple(rows)


def read_arcs(path: Path) -> tuple[ArcPoint, ...]:
    rows: list[ArcPoint] = []
    seen_indices: set[tuple[str, int]] = set()
    epoch_metadata: dict[str, tuple[int, str, str]] = {}
    for index, raw in enumerate(_read_csv(path, ARC_COLUMNS), 2):
        latitude = _finite_float(raw["latitude_deg"], "latitude_deg")
        longitude = _finite_float(raw["longitude_deg_e"], "longitude_deg_e")
        _validate_coordinate(latitude, longitude, f"{path}:{index}")
        point_index = int(raw["arc_point_index"])
        if point_index < 0:
            raise ValueError(f"{path}:{index}: negative arc point index")
        key = raw["epoch_id"], point_index
        if key in seen_indices:
            raise ValueError(f"{path}:{index}: duplicate arc point {key}")
        seen_indices.add(key)
        metadata = int(raw["sequence"]), raw["flight"], raw["arc_time_utc"]
        prior = epoch_metadata.setdefault(raw["epoch_id"], metadata)
        if prior != metadata:
            raise ValueError(f"{path}:{index}: inconsistent epoch metadata")
        rows.append(ArcPoint(
            epoch_id=raw["epoch_id"],
            sequence=metadata[0],
            flight=metadata[1],
            arc_time_utc=metadata[2],
            arc_point_index=point_index,
            latitude_deg=latitude,
            longitude_deg_e=longitude,
        ))
    if not rows:
        raise ValueError(f"{path}: no arc points")
    return tuple(sorted(rows, key=lambda row: (row.sequence, row.epoch_id, row.arc_point_index)))


def read_truth(path: Path) -> TruthReferences:
    arc_epoch: dict[str, TruthRow] = {}
    nearest_slot: dict[str, TruthRow] = {}
    all_slots: dict[tuple[str, str], TruthRow] = {}
    for index, raw in enumerate(_read_csv(path, TRUTH_COLUMNS), 2):
        epoch_id = raw["epoch_id"]
        role = raw["reference_role"]
        if role not in {"arc_epoch", "physical_slot"}:
            raise ValueError(f"{path}:{index}: invalid truth reference role")
        physical_slot = raw["physical_slot"] or None
        nearest = _bool(raw["is_nearest_arc_slot"], "is_nearest_arc_slot")
        if role == "arc_epoch" and (physical_slot is not None or nearest):
            raise ValueError(f"{path}:{index}: arc-epoch truth cannot name a slot")
        if role == "physical_slot" and physical_slot is None:
            raise ValueError(f"{path}:{index}: slot truth requires physical_slot")
        latitude = _finite_float(raw["latitude_deg"], "latitude_deg")
        longitude = _finite_float(raw["longitude_deg_e"], "longitude_deg_e")
        _validate_coordinate(latitude, longitude, f"{path}:{index}")
        if not raw["position_source"] or not raw["position_method"]:
            raise ValueError(f"{path}:{index}: truth provenance is required")
        row = TruthRow(
            epoch_id=epoch_id,
            truth_id=raw["truth_id"],
            reference_role=role,
            physical_slot=physical_slot,
            is_nearest_arc_slot=nearest,
            position_time_utc=raw["position_time_utc"],
            latitude_deg=latitude,
            longitude_deg_e=longitude,
            altitude_km=_optional_float(raw["altitude_km"], "altitude_km"),
            position_source=raw["position_source"],
            position_method=raw["position_method"],
            time_offset_seconds=_finite_float(
                raw["time_offset_seconds"], "time_offset_seconds"
            ),
        )
        if role == "arc_epoch":
            if epoch_id in arc_epoch:
                raise ValueError(f"{path}:{index}: duplicate arc-epoch truth")
            arc_epoch[epoch_id] = row
        else:
            assert physical_slot is not None
            key = epoch_id, physical_slot
            if key in all_slots:
                raise ValueError(f"{path}:{index}: duplicate physical-slot truth")
            all_slots[key] = row
            if nearest:
                if epoch_id in nearest_slot:
                    raise ValueError(f"{path}:{index}: multiple nearest-slot truths")
                nearest_slot[epoch_id] = row
    return TruthReferences(arc_epoch, nearest_slot, all_slots)


def read_tracks(path: Path) -> Mapping[str, tuple[TrackPoint, ...]]:
    grouped: dict[str, list[TrackPoint]] = {}
    for row_number, raw in enumerate(_read_csv(path, TRACK_COLUMNS), 2):
        context = f"{path}:{row_number}"
        flight = raw["flight"].strip()
        if not flight:
            raise ValueError(f"{context}: flight is required")
        point_index = int(raw["track_point_index"])
        source_row = int(raw["source_excel_row"])
        if point_index < 0 or source_row < 1:
            raise ValueError(f"{context}: invalid track/source row index")
        timestamp = raw["time_utc"].strip()
        _utc_datetime(timestamp, context)
        latitude = _finite_float(raw["latitude_deg"], "latitude_deg")
        longitude = _finite_float(raw["longitude_deg_e"], "longitude_deg_e")
        _validate_coordinate(latitude, longitude, context)
        heading = _finite_float(raw["heading_true_deg"], "heading_true_deg")
        if not 0.0 <= heading < 360.0:
            raise ValueError(f"{context}: heading outside [0, 360)")
        if not all(
            raw[name].strip()
            for name in ("position_source", "position_method", "source_sheet")
        ):
            raise ValueError(f"{context}: track provenance is required")
        grouped.setdefault(flight, []).append(TrackPoint(
            flight=flight,
            track_point_index=point_index,
            time_utc=timestamp,
            latitude_deg=latitude,
            longitude_deg_e=longitude,
            altitude_ft=_finite_float(raw["altitude_ft"], "altitude_ft"),
            heading_true_deg=heading,
            position_source=raw["position_source"],
            position_method=raw["position_method"],
            source_sheet=raw["source_sheet"],
            source_excel_row=source_row,
        ))
    if not grouped:
        raise ValueError(f"{path}: no track points")
    result: dict[str, tuple[TrackPoint, ...]] = {}
    for flight, rows in grouped.items():
        rows.sort(key=lambda row: row.track_point_index)
        if [row.track_point_index for row in rows] != list(range(len(rows))):
            raise ValueError(f"{path}: {flight} track indices must be contiguous from zero")
        timestamps = [_utc_datetime(row.time_utc, path.as_posix()) for row in rows]
        if timestamps != sorted(set(timestamps)):
            raise ValueError(f"{path}: {flight} track times must be unique and increasing")
        result[flight] = tuple(rows)
    return result


def read_track_provenance(
    path: Path,
    track_path: Path,
    tracks: Mapping[str, Sequence[TrackPoint]],
) -> Mapping[str, object]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if value.get("schema") != TRACK_PROVENANCE_SCHEMA:
        raise ValueError(f"{path}: unexpected track provenance schema")
    if value.get("track_schema") != TRACK_SCHEMA:
        raise ValueError(f"{path}: unexpected track table schema")
    role = value.get("role")
    if not isinstance(role, str) or not all(
        phrase in role
        for phrase in ("Post-selection", "never supplied", "not continuously observed")
    ):
        raise ValueError(f"{path}: track overlay role is not sufficiently explicit")
    output = value.get("output")
    if not isinstance(output, dict):
        raise ValueError(f"{path}: track output identity is required")
    rows_by_flight = {name: len(rows) for name, rows in sorted(tracks.items())}
    if (
        output.get("file") != track_path.name
        or output.get("sha256") != _sha256(track_path)
        or output.get("rows") != sum(rows_by_flight.values())
        or output.get("rows_by_flight") != rows_by_flight
    ):
        raise ValueError(f"{path}: track output identity does not match table")
    source = value.get("source")
    if not isinstance(source, dict) or not all(
        source.get(name) for name in ("dataset_url", "file", "license", "sha256")
    ):
        raise ValueError(f"{path}: track source provenance is incomplete")
    return value


def read_truth_scores(path: Path) -> dict[tuple[str, str, str], TruthScoreRow]:
    result: dict[tuple[str, str, str], TruthScoreRow] = {}
    for index, raw in enumerate(_read_csv(path, TRUTH_SCORE_COLUMNS), 2):
        condition, screen = raw["condition"], raw["screen"]
        if condition not in CONDITIONS or screen not in SCREENS:
            raise ValueError(f"{path}:{index}: invalid truth-score panel")
        try:
            sensitivity_value = json.loads(raw["altitude_sensitivity_recovered"] or "{}")
        except json.JSONDecodeError as error:
            raise ValueError(f"{path}:{index}: invalid altitude sensitivity JSON") from error
        if not isinstance(sensitivity_value, dict) or any(
            not isinstance(value, bool) for value in sensitivity_value.values()
        ):
            raise ValueError(f"{path}:{index}: altitude sensitivities must be booleans")
        latitude = _finite_float(raw["truth_latitude_deg"], "truth_latitude_deg")
        longitude = _finite_float(
            raw["truth_longitude_deg_e"], "truth_longitude_deg_e"
        )
        _validate_coordinate(latitude, longitude, f"{path}:{index}")
        row = TruthScoreRow(
            epoch_id=raw["epoch_id"],
            condition=condition,
            screen=screen,
            nearest_physical_slot=raw["nearest_physical_slot"],
            truth_id=raw["truth_id"],
            truth_position_time_utc=raw["truth_position_time_utc"],
            truth_latitude_deg=latitude,
            truth_longitude_deg_e=longitude,
            truth_altitude_km=_optional_float(
                raw["truth_altitude_km"], "truth_altitude_km"
            ),
            truth_position_source=raw["truth_position_source"],
            truth_position_method=raw["truth_position_method"],
            truth_time_offset_seconds=_finite_float(
                raw["truth_time_offset_seconds"], "truth_time_offset_seconds"
            ),
            eligible_residual_parent_clusters=int(
                raw["eligible_residual_parent_clusters"]
            ),
            eligible_surviving_source_clusters=int(
                raw["eligible_surviving_source_clusters"]
            ),
            nearest_horizontal_km=_optional_distance(
                raw["nearest_horizontal_km"], "nearest_horizontal_km"
            ),
            nearest_source_cluster_id=raw["nearest_source_cluster_id"] or None,
            nearest_source_altitude_km=_optional_float(
                raw["nearest_source_altitude_km"], "nearest_source_altitude_km"
            ),
            nearest_horizontal_source_altitude_gap_km=_optional_distance(
                raw["nearest_horizontal_source_altitude_gap_km"],
                "nearest_horizontal_source_altitude_gap_km",
            ),
            minimum_altitude_gap_km=_optional_distance(
                raw["minimum_altitude_gap_km"], "minimum_altitude_gap_km"
            ),
            joint_clusters_within_tolerance=int(
                raw["joint_clusters_within_tolerance"]
            ),
            horizontal_tolerance_km=_nonnegative_distance(
                raw["horizontal_tolerance_km"], "horizontal_tolerance_km"
            ),
            altitude_tolerance_km=_optional_distance(
                raw["altitude_tolerance_km"], "altitude_tolerance_km"
            ),
            recovered=_bool(raw["recovered"], "recovered"),
            parent_collapsed_residual_ids=_string_values(
                raw["parent_collapsed_residual_ids"]
            ),
            altitude_sensitivity_recovered={
                str(key): value for key, value in sensitivity_value.items()
            },
        )
        key = row.epoch_id, screen, condition
        if row.nearest_horizontal_km is None and (
            row.recovered or row.joint_clusters_within_tolerance != 0
        ):
            raise ValueError(
                f"{path}:{index}: empty truth-score panel cannot be recovered"
            )
        if key in result:
            raise ValueError(f"{path}:{index}: duplicate truth-score panel")
        result[key] = row
    return result


def read_metadata(path: Path) -> dict[str, object]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("run metadata must be a JSON object")
    required = {
        "schema",
        "run_id",
        "known_aircraft_truth_used_in_candidate_selection",
        "control_offsets_minutes",
        "cluster_radius_km",
        "residual_tolerance_km",
        "minimum_independent_links",
        "surface_endpoint_tolerance_km",
        "aircraft_altitude_tolerance_km",
        "truth_recovery_tolerance_km",
        "truth_recovery_altitude_tolerance_km",
        "truth_recovery_altitude_sensitivity_km",
        "route_geometry",
        "ionosphere_model",
        "map_extent_lon_lat",
        "aircraft_altitude_grid_km",
        "altitude_collapse_spatial_tolerance_km",
        "common_altitude_residual_model",
        "epoch_partition_applied_before_clustering",
    }
    missing = required.difference(value)
    if missing:
        raise ValueError(f"run metadata missing fields {sorted(missing)}")
    if value["schema"] != METADATA_SCHEMA:
        raise ValueError(f"unexpected run metadata schema: {value['schema']}")
    if value["known_aircraft_truth_used_in_candidate_selection"] is not False:
        raise ValueError("publication controls require blind candidate selection")
    if value["epoch_partition_applied_before_clustering"] is not True:
        raise ValueError("candidate pairs must be partitioned by epoch before clustering")
    if value["common_altitude_residual_model"] != (
        "source_clusters_matched_across_any_altitude_before_survivors_are_"
        "collapsed_for_event_display_and_count;truth_recovery_uses_surviving_"
        "source_centres_and_heights"
    ):
        raise ValueError(
            "primary common-altitude result must residualize source clusters "
            "before event collapse"
        )
    offsets = value["control_offsets_minutes"]
    expected = {"minus_60_min": -60, "actual_time": 0, "plus_60_min": 60}
    if offsets != expected:
        raise ValueError(f"control offsets must be {expected}")
    for name in (
        "cluster_radius_km",
        "residual_tolerance_km",
        "surface_endpoint_tolerance_km",
        "aircraft_altitude_tolerance_km",
        "truth_recovery_tolerance_km",
        "truth_recovery_altitude_tolerance_km",
    ):
        if not math.isfinite(float(value[name])) or float(value[name]) <= 0.0:
            raise ValueError(f"{name} must be positive and finite")
    if int(value["minimum_independent_links"]) < 1:
        raise ValueError("minimum_independent_links must be positive")
    sensitivity = value["truth_recovery_altitude_sensitivity_km"]
    if not (
        isinstance(sensitivity, list)
        and sensitivity
        and all(math.isfinite(float(item)) and float(item) > 0.0 for item in sensitivity)
        and [float(item) for item in sensitivity]
        == sorted(set(float(item) for item in sensitivity))
        and float(value["truth_recovery_altitude_tolerance_km"])
        in [float(item) for item in sensitivity]
    ):
        raise ValueError(
            "truth_recovery_altitude_sensitivity_km must be sorted, unique and "
            "include the primary tolerance"
        )
    altitude_grid = value["aircraft_altitude_grid_km"]
    if not (
        isinstance(altitude_grid, list)
        and altitude_grid
        and all(math.isfinite(float(item)) and float(item) >= 0.0 for item in altitude_grid)
        and [float(item) for item in altitude_grid]
        == sorted(set(float(item) for item in altitude_grid))
    ):
        raise ValueError("aircraft_altitude_grid_km must be sorted and unique")
    collapse_tolerance = float(value["altitude_collapse_spatial_tolerance_km"])
    if not math.isfinite(collapse_tolerance) or collapse_tolerance <= 0.0:
        raise ValueError(
            "altitude_collapse_spatial_tolerance_km must be positive and finite"
        )
    extent = value["map_extent_lon_lat"]
    if not (
        isinstance(extent, list)
        and len(extent) == 4
        and all(math.isfinite(float(item)) for item in extent)
        and float(extent[0]) < float(extent[1])
        and float(extent[2]) < float(extent[3])
    ):
        raise ValueError("map_extent_lon_lat must be [west, east, south, north]")
    return value


def great_circle_distance_km(
    latitude_1: float,
    longitude_1: float,
    latitude_2: float,
    longitude_2: float,
) -> float:
    first, second = math.radians(latitude_1), math.radians(latitude_2)
    delta_latitude = second - first
    delta_longitude = math.radians(longitude_2 - longitude_1)
    value = (
        math.sin(delta_latitude / 2.0) ** 2
        + math.cos(first) * math.cos(second)
        * math.sin(delta_longitude / 2.0) ** 2
    )
    return 2.0 * EARTH_MEAN_RADIUS_KM * math.asin(
        math.sqrt(max(0.0, min(1.0, value)))
    )


def _slug(value: str) -> str:
    cleaned = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    if not cleaned:
        raise ValueError("cannot form an output name from an empty identifier")
    return cleaned


def _display_time(value: str) -> str:
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return value
    return parsed.strftime("%Y-%m-%d %H:%M:%S UTC")


def _figure_stem(
    flight: str,
    screen: str,
    page_index: int,
    page_count: int,
) -> str:
    suffix = "" if page_count == 1 else f"-page-{page_index + 1}-of-{page_count}"
    return (
        f"known-flight-pharlap-{_slug(flight)}-{_slug(screen)}"
        f"-residual-controls{suffix}"
    )


def _raw_figure_stem(
    flight: str,
    screen: str,
    page_index: int,
    page_count: int,
) -> str:
    suffix = "" if page_count == 1 else f"-page-{page_index + 1}-of-{page_count}"
    return (
        f"known-flight-pharlap-{_slug(flight)}-{_slug(screen)}"
        f"-raw-arc-time{suffix}"
    )


def _truth_centered_latitude_limits(
    arc: Sequence[ArcPoint],
    clusters: Sequence[ClusterRow],
    truth: TruthRow | None,
    configured_extent: Sequence[float],
) -> tuple[float, float]:
    """Return symmetric y limits without hiding any frozen-domain geometry.

    The configured search latitude limits are included even when no surviving
    cluster lies at an edge.  This avoids making an unsearched region look
    empty when a low-latitude truth point requires the displayed range to
    extend outside the frozen search domain.
    """
    if len(configured_extent) != 4:
        raise ValueError("configured extent must be [west, east, south, north]")
    south, north = float(configured_extent[2]), float(configured_extent[3])
    center = (south + north) / 2.0 if truth is None else truth.latitude_deg
    values = [south, north]
    values.extend(point.latitude_deg for point in arc)
    values.extend(row.latitude_deg for row in clusters)
    half_span = max(abs(value - center) for value in values)
    padding = max(0.25, 0.02 * half_span)
    half_span += padding
    lower, upper = center - half_span, center + half_span
    if lower < -90.0 or upper > 90.0:
        raise ValueError("truth-centred latitude range would cross a pole")
    return lower, upper


def _draw_latitude_scale_bar(axis, latitude_limits: tuple[float, float]) -> float:
    """Draw a north/south great-circle ruler in a panel's right margin."""
    south, north = latitude_limits
    distance_km = 500.0
    height_deg = math.degrees(distance_km / EARTH_MEAN_RADIUS_KM)
    center = (south + north) / 2.0
    y_start = center - height_deg / 2.0
    y_end = center + height_deg / 2.0
    transform = axis.get_yaxis_transform()
    x = 0.965
    axis.plot(
        [x, x], [y_start, y_end], transform=transform,
        color="#111111", linewidth=2.0, solid_capstyle="butt", zorder=12,
        clip_on=False,
    )
    for y in (y_start, y_end):
        axis.plot(
            [x - 0.014, x + 0.014], [y, y], transform=transform,
            color="#111111", linewidth=2.0, zorder=12, clip_on=False,
        )
    axis.text(
        x - 0.020,
        (y_start + y_end) / 2.0,
        f"{distance_km:g} km",
        transform=transform,
        rotation=90,
        va="center",
        ha="right",
        fontsize=7.8,
        weight="bold",
        color="#111111",
        bbox={"facecolor": "white", "edgecolor": "none", "alpha": 0.78, "pad": 1.0},
        zorder=12,
    )
    return distance_km


def _format_latitude_axis(axis) -> None:
    from matplotlib.ticker import FuncFormatter

    def label(value: float, _position: float) -> str:
        if math.isclose(value, 0.0, abs_tol=1e-10):
            return "0°"
        suffix = "N" if value > 0.0 else "S"
        magnitude = abs(value)
        formatted = f"{magnitude:.1f}".rstrip("0").rstrip(".")
        return f"{formatted}°{suffix}"

    axis.yaxis.set_major_formatter(FuncFormatter(label))


def _shade_outside_search_latitude(
    axis,
    latitude_limits: tuple[float, float],
    configured_extent: Sequence[float],
    *,
    label: bool,
) -> None:
    lower, upper = latitude_limits
    search_south, search_north = map(float, configured_extent[2:4])
    bands: list[tuple[float, float]] = []
    if lower < search_south:
        bands.append((lower, search_south))
    if upper > search_north:
        bands.append((search_north, upper))
    for start, end in bands:
        axis.axhspan(start, end, color="#f2f2f2", zorder=-3)
        if label and end - start >= 1.0:
            axis.text(
                0.50,
                (start + end) / 2.0,
                (
                    f"Outside frozen {search_south:g}–{search_north:g}°N "
                    "candidate-search latitude"
                ),
                transform=axis.get_yaxis_transform(),
                ha="center",
                va="center",
                fontsize=6.8,
                style="italic",
                color="#777777",
                zorder=1,
            )


def epoch_pages(
    arcs: Sequence[ArcPoint],
    rows_per_page: int = 3,
) -> list[tuple[str, int, int, tuple[ArcPoint, ...]]]:
    """Group ordered epochs by flight into publication-sized pages."""
    if rows_per_page < 1:
        raise ValueError("rows_per_page must be positive")
    first_points: dict[str, ArcPoint] = {}
    for point in arcs:
        first_points.setdefault(point.epoch_id, point)
    by_flight: dict[str, list[ArcPoint]] = {}
    for epoch in sorted(
        first_points.values(), key=lambda row: (row.flight, row.sequence, row.epoch_id)
    ):
        by_flight.setdefault(epoch.flight, []).append(epoch)
    pages: list[tuple[str, int, int, tuple[ArcPoint, ...]]] = []
    for flight, epochs in sorted(by_flight.items()):
        page_count = math.ceil(len(epochs) / rows_per_page)
        for page_index in range(page_count):
            start = page_index * rows_per_page
            pages.append((
                flight,
                page_index,
                page_count,
                tuple(epochs[start:start + rows_per_page]),
            ))
    return pages


def summarize_panel(
    epoch: ArcPoint,
    screen: str,
    condition: str,
    residuals: Sequence[ClusterRow],
    arc_truth: TruthRow | None,
    truth_score: TruthScoreRow | None,
    figure_stem: str,
) -> dict[str, object]:
    rows = [
        row for row in residuals
        if row.epoch_id == epoch.epoch_id
        and row.screen == screen
        and row.condition == condition
        and row.is_residual
    ]
    summary: dict[str, object] = {
        "epoch_id": epoch.epoch_id,
        "sequence": epoch.sequence,
        "flight": epoch.flight,
        "arc_time_utc": epoch.arc_time_utc,
        "screen": screen,
        "condition": condition,
        "residual_cluster_count": len(rows),
        "maximum_independent_links": max(
            (row.independent_links for row in rows), default=""
        ),
        "median_independent_links": median(
            [row.independent_links for row in rows]
        ) if rows else "",
        "truth_id": "" if arc_truth is None else arc_truth.truth_id,
        "truth_position_time_utc": "" if arc_truth is None else arc_truth.position_time_utc,
        "truth_latitude_deg": "" if arc_truth is None else arc_truth.latitude_deg,
        "truth_longitude_deg_e": "" if arc_truth is None else arc_truth.longitude_deg_e,
        "truth_altitude_km": "" if arc_truth is None or arc_truth.altitude_km is None else arc_truth.altitude_km,
        "truth_position_source": "" if arc_truth is None else arc_truth.position_source,
        "truth_position_method": "" if arc_truth is None else arc_truth.position_method,
        "truth_time_offset_seconds": "" if arc_truth is None else arc_truth.time_offset_seconds,
        "nearest_arc_epoch_reference_horizontal_km": "",
        "nearest_cluster_latitude_deg": "",
        "nearest_cluster_longitude_deg_e": "",
        "nearest_cluster_altitude_km": "",
        "nearest_cluster_altitude_minimum_km": "",
        "nearest_cluster_altitude_maximum_km": "",
        "nearest_cluster_feasible_altitude_count": "",
        "nearest_arc_epoch_reference_altitude_difference_km": "",
        "nearest_cluster_independent_links": "",
        "nearest_cluster_support_links": "",
        "nearest_cluster_physical_slot": "",
        "proximity_interpretation": (
            "Distance to the static aircraft position at the BTO arc epoch; "
            "not a time-aligned detection or recovery score for clusters from "
            "other physical slots in the analysis window."
        ),
        "recovery_physical_slot": (
            "" if truth_score is None else truth_score.nearest_physical_slot
        ),
        "recovery_truth_id": "" if truth_score is None else truth_score.truth_id,
        "recovery_truth_position_time_utc": (
            "" if truth_score is None else truth_score.truth_position_time_utc
        ),
        "recovery_truth_latitude_deg": (
            "" if truth_score is None else truth_score.truth_latitude_deg
        ),
        "recovery_truth_longitude_deg_e": (
            "" if truth_score is None else truth_score.truth_longitude_deg_e
        ),
        "recovery_truth_altitude_km": (
            "" if truth_score is None or truth_score.truth_altitude_km is None
            else truth_score.truth_altitude_km
        ),
        "recovery_truth_position_source": (
            "" if truth_score is None else truth_score.truth_position_source
        ),
        "recovery_truth_position_method": (
            "" if truth_score is None else truth_score.truth_position_method
        ),
        "recovery_truth_time_offset_seconds": (
            "" if truth_score is None else truth_score.truth_time_offset_seconds
        ),
        "recovery_slot_residual_cluster_count": (
            "" if truth_score is None
            else truth_score.eligible_residual_parent_clusters
        ),
        "recovery_surviving_source_cluster_count": (
            "" if truth_score is None
            else truth_score.eligible_surviving_source_clusters
        ),
        "nearest_time_aligned_truth_horizontal_km": (
            "" if truth_score is None or truth_score.nearest_horizontal_km is None
            else truth_score.nearest_horizontal_km
        ),
        "nearest_recovery_source_cluster_id": (
            "" if truth_score is None or truth_score.nearest_source_cluster_id is None
            else truth_score.nearest_source_cluster_id
        ),
        "nearest_recovery_source_altitude_km": (
            "" if truth_score is None or truth_score.nearest_source_altitude_km is None
            else truth_score.nearest_source_altitude_km
        ),
        "nearest_time_aligned_truth_altitude_difference_km": (
            "" if truth_score is None
            or truth_score.nearest_horizontal_source_altitude_gap_km is None
            else truth_score.nearest_horizontal_source_altitude_gap_km
        ),
        "minimum_time_aligned_truth_altitude_difference_km": (
            "" if truth_score is None or truth_score.minimum_altitude_gap_km is None
            else truth_score.minimum_altitude_gap_km
        ),
        "joint_clusters_within_tolerance": (
            "" if truth_score is None else truth_score.joint_clusters_within_tolerance
        ),
        "recovery_parent_collapsed_residual_ids": (
            "" if truth_score is None
            else ";".join(truth_score.parent_collapsed_residual_ids)
        ),
        "recovery_horizontal_tolerance_km": (
            "" if truth_score is None else truth_score.horizontal_tolerance_km
        ),
        "recovery_altitude_tolerance_km": (
            "" if truth_score is None or truth_score.altitude_tolerance_km is None
            else truth_score.altitude_tolerance_km
        ),
        "recovery_horizontal_within_tolerance": (
            "" if truth_score is None or truth_score.nearest_horizontal_km is None
            else truth_score.nearest_horizontal_km <= truth_score.horizontal_tolerance_km
        ),
        "recovery_altitude_within_tolerance": (
            "" if truth_score is None
            or truth_score.altitude_tolerance_km is None
            or truth_score.nearest_horizontal_source_altitude_gap_km is None
            else truth_score.nearest_horizontal_source_altitude_gap_km
            <= truth_score.altitude_tolerance_km
        ),
        "recovery_altitude_sensitivity_results": (
            "" if truth_score is None
            else ";".join(
                f"{key}:{str(value).lower()}"
                for key, value in sorted(
                    truth_score.altitude_sensitivity_recovered.items(),
                    key=lambda item: float(item[0]),
                )
            )
        ),
        "recovered_within_tolerance": (
            "" if truth_score is None else truth_score.recovered
        ),
        "recovery_interpretation": (
            "Authoritative recovery uses surviving pre-collapse source centers "
            "and exact altitude slices in the WSPR physical slot nearest the BTO "
            "epoch, against aircraft truth interpolated to that slot midpoint."
        ),
        "figure_png": f"{figure_stem}.png",
        "figure_pdf": f"{figure_stem}.pdf",
        "figure_svg": f"{figure_stem}.svg",
    }
    def altitude_difference(reference: TruthRow, cluster: ClusterRow) -> float | str:
        if reference.altitude_km is None:
            return ""
        if cluster.altitude_km is not None:
            return abs(cluster.altitude_km - reference.altitude_km)
        if not cluster.feasible_altitudes_km:
            return ""
        return min(
            abs(value - reference.altitude_km)
            for value in cluster.feasible_altitudes_km
        )

    if arc_truth is not None and rows:
        distances = [
            great_circle_distance_km(
                arc_truth.latitude_deg,
                arc_truth.longitude_deg_e,
                row.latitude_deg,
                row.longitude_deg_e,
            )
            for row in rows
        ]
        nearest_index = min(range(len(rows)), key=distances.__getitem__)
        nearest = rows[nearest_index]
        summary.update({
            "nearest_arc_epoch_reference_horizontal_km": distances[nearest_index],
            "nearest_cluster_latitude_deg": nearest.latitude_deg,
            "nearest_cluster_longitude_deg_e": nearest.longitude_deg_e,
            "nearest_cluster_altitude_km": (
                "" if nearest.altitude_km is None else nearest.altitude_km
            ),
            "nearest_cluster_altitude_minimum_km": (
                "" if nearest.altitude_minimum_km is None
                else nearest.altitude_minimum_km
            ),
            "nearest_cluster_altitude_maximum_km": (
                "" if nearest.altitude_maximum_km is None
                else nearest.altitude_maximum_km
            ),
            "nearest_cluster_feasible_altitude_count": nearest.feasible_altitude_count,
            "nearest_arc_epoch_reference_altitude_difference_km": (
                altitude_difference(arc_truth, nearest)
            ),
            "nearest_cluster_independent_links": nearest.independent_links,
            "nearest_cluster_support_links": nearest.support_links,
            "nearest_cluster_physical_slot": nearest.physical_slot,
        })

    return summary


def build_summary(
    arcs: Sequence[ArcPoint],
    residuals: Sequence[ClusterRow],
    truths: TruthReferences,
    truth_scores: Mapping[tuple[str, str, str], TruthScoreRow],
    screens: Sequence[str],
) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for flight, page_index, page_count, epochs in epoch_pages(arcs):
        for screen in screens:
            stem = _figure_stem(flight, screen, page_index, page_count)
            for epoch in epochs:
                for condition in CONDITIONS:
                    slot_truth = truths.nearest_physical_slot.get(epoch.epoch_id)
                    truth_score = truth_scores.get((epoch.epoch_id, screen, condition))
                    if truth_score is not None and slot_truth is not None:
                        if (
                            truth_score.truth_id != slot_truth.truth_id
                            or truth_score.nearest_physical_slot != slot_truth.physical_slot
                            or truth_score.truth_position_time_utc
                            != slot_truth.position_time_utc
                            or not math.isclose(
                                truth_score.truth_latitude_deg,
                                slot_truth.latitude_deg,
                                abs_tol=1e-10,
                            )
                            or not math.isclose(
                                truth_score.truth_longitude_deg_e,
                                slot_truth.longitude_deg_e,
                                abs_tol=1e-10,
                            )
                        ):
                            raise ValueError(
                                f"truth score disagrees with slot truth for {epoch.epoch_id}"
                            )
                    rows.append(summarize_panel(
                        epoch,
                        screen,
                        condition,
                        residuals,
                        truths.arc_epoch.get(epoch.epoch_id),
                        truth_score,
                        stem,
                    ))
    return rows


def build_raw_actual_summary(
    arcs: Sequence[ArcPoint],
    clusters: Sequence[ClusterRow],
    truths: TruthReferences,
    screens: Sequence[str],
) -> list[dict[str, object]]:
    """Summarize central-window clusters before symmetric subtraction.

    Proximity is deliberately measured to the static aircraft reference at the
    BTO epoch.  It is descriptive, because the raw panel pools physical WSPR
    slots across the complete central analysis window.
    """
    rows: list[dict[str, object]] = []
    for flight, page_index, page_count, epochs in epoch_pages(arcs):
        for screen in screens:
            stem = _raw_figure_stem(flight, screen, page_index, page_count)
            for epoch in epochs:
                panel = [
                    row for row in clusters
                    if row.epoch_id == epoch.epoch_id
                    and row.screen == screen
                    and row.condition == "actual_time"
                ]
                truth = truths.arc_epoch.get(epoch.epoch_id)
                result: dict[str, object] = {
                    "epoch_id": epoch.epoch_id,
                    "sequence": epoch.sequence,
                    "flight": epoch.flight,
                    "arc_time_utc": epoch.arc_time_utc,
                    "screen": screen,
                    "condition": "actual_time",
                    "raw_cluster_count": len(panel),
                    "maximum_independent_links": max(
                        (row.independent_links for row in panel), default=""
                    ),
                    "median_independent_links": (
                        median([row.independent_links for row in panel])
                        if panel else ""
                    ),
                    "truth_id": "" if truth is None else truth.truth_id,
                    "truth_position_time_utc": (
                        "" if truth is None else truth.position_time_utc
                    ),
                    "truth_latitude_deg": "" if truth is None else truth.latitude_deg,
                    "truth_longitude_deg_e": (
                        "" if truth is None else truth.longitude_deg_e
                    ),
                    "truth_altitude_km": (
                        "" if truth is None or truth.altitude_km is None
                        else truth.altitude_km
                    ),
                    "truth_position_source": (
                        "" if truth is None else truth.position_source
                    ),
                    "truth_position_method": (
                        "" if truth is None else truth.position_method
                    ),
                    "nearest_arc_epoch_reference_horizontal_km": "",
                    "nearest_cluster_latitude_deg": "",
                    "nearest_cluster_longitude_deg_e": "",
                    "nearest_cluster_altitude_minimum_km": "",
                    "nearest_cluster_altitude_maximum_km": "",
                    "nearest_cluster_independent_links": "",
                    "nearest_cluster_support_links": "",
                    "nearest_cluster_physical_slot": "",
                    "proximity_interpretation": (
                        "Distance from a raw cluster pooled across the central "
                        "analysis window to the static aircraft position at the "
                        "BTO arc epoch; descriptive only, not a time-aligned "
                        "recovery score."
                    ),
                    "figure_png": f"{stem}.png",
                    "figure_pdf": f"{stem}.pdf",
                    "figure_svg": f"{stem}.svg",
                }
                if truth is not None and panel:
                    distances = [
                        great_circle_distance_km(
                            truth.latitude_deg,
                            truth.longitude_deg_e,
                            cluster.latitude_deg,
                            cluster.longitude_deg_e,
                        )
                        for cluster in panel
                    ]
                    nearest_index = min(
                        range(len(panel)), key=distances.__getitem__
                    )
                    nearest = panel[nearest_index]
                    result.update({
                        "nearest_arc_epoch_reference_horizontal_km": (
                            distances[nearest_index]
                        ),
                        "nearest_cluster_latitude_deg": nearest.latitude_deg,
                        "nearest_cluster_longitude_deg_e": nearest.longitude_deg_e,
                        "nearest_cluster_altitude_minimum_km": (
                            "" if nearest.altitude_minimum_km is None
                            else nearest.altitude_minimum_km
                        ),
                        "nearest_cluster_altitude_maximum_km": (
                            "" if nearest.altitude_maximum_km is None
                            else nearest.altitude_maximum_km
                        ),
                        "nearest_cluster_independent_links": nearest.independent_links,
                        "nearest_cluster_support_links": nearest.support_links,
                        "nearest_cluster_physical_slot": nearest.physical_slot,
                    })
                rows.append(result)
    return rows


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _write_summary(path: Path, rows: Sequence[Mapping[str, object]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=SUMMARY_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)


def _write_raw_summary(path: Path, rows: Sequence[Mapping[str, object]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=RAW_SUMMARY_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)


def _support_limits(
    clusters: Sequence[ClusterRow],
    screens: Sequence[str],
    minimum: int,
    *,
    residual_only: bool = True,
    condition: str | None = None,
) -> tuple[int, int]:
    values = [
        row.independent_links for row in clusters
        if (row.is_residual or not residual_only)
        and row.screen in screens
        and (condition is None or row.condition == condition)
    ]
    return minimum, max(values, default=minimum)


def _altitude_sizes(
    values: Sequence[float | None],
    domain: tuple[float, float] | None = None,
) -> list[float]:
    numeric = [value for value in values if value is not None]
    if not numeric:
        return [42.0] * len(values)
    minimum, maximum = domain if domain is not None else (min(numeric), max(numeric))
    span = maximum - minimum
    return [
        42.0 if value is None
        else 30.0 + (0.5 if span == 0.0 else (value - minimum) / span) * 62.0
        for value in values
    ]


def _draw_flight_page(
    flight: str,
    page_index: int,
    page_count: int,
    epochs: Sequence[ArcPoint],
    arcs_by_epoch: Mapping[str, Sequence[ArcPoint]],
    residuals: Sequence[ClusterRow],
    truths: TruthReferences,
    tracks_by_flight: Mapping[str, Sequence[TrackPoint]],
    screen: str,
    metadata: Mapping[str, object],
    summary_lookup: Mapping[tuple[str, str, str], Mapping[str, object]],
    support_limits: tuple[int, int],
    output_directory: Path,
) -> tuple[Path, Path, Path]:
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        from matplotlib.colors import BoundaryNorm
        from matplotlib.lines import Line2D
        from matplotlib.cm import ScalarMappable
    except ImportError as error:
        raise RuntimeError(
            "matplotlib is required to generate publication figures"
        ) from error

    minimum_support, maximum_support = support_limits
    boundaries = [
        value - 0.5 for value in range(minimum_support, maximum_support + 2)
    ]
    cmap = plt.get_cmap("viridis", maximum_support - minimum_support + 1)
    norm = BoundaryNorm(boundaries, cmap.N)
    extent = [float(value) for value in metadata["map_extent_lon_lat"]]
    altitude_grid = [float(value) for value in metadata["aircraft_altitude_grid_km"]]
    altitude_domain = min(altitude_grid), max(altitude_grid)
    track = tracks_by_flight[flight]

    row_count = len(epochs)
    fig, axes = plt.subplots(
        row_count,
        3,
        figsize=(21.0, 4.75 * row_count + 2.0),
        sharex=True,
        sharey=False,
        squeeze=False,
    )
    for row_index, epoch in enumerate(epochs):
        arc = arcs_by_epoch[epoch.epoch_id]
        arc_truth = truths.arc_epoch.get(epoch.epoch_id)
        row_clusters = [
            row for row in residuals
            if row.epoch_id == epoch.epoch_id and row.screen == screen
        ]
        latitude_limits = _truth_centered_latitude_limits(
            arc, row_clusters, arc_truth, extent
        )
        midpoint_latitude = sum(latitude_limits) / 2.0
        for column_index, condition in enumerate(CONDITIONS):
            axis = axes[row_index, column_index]
            _shade_outside_search_latitude(
                axis,
                latitude_limits,
                extent,
                label=column_index == len(CONDITIONS) - 1,
            )
            panel = [
                row for row in residuals
                if row.epoch_id == epoch.epoch_id
                and row.screen == screen
                and row.condition == condition
                and row.is_residual
            ]
            axis.plot(
                [point.longitude_deg_e for point in arc],
                [point.latitude_deg for point in arc],
                color="#151515",
                linewidth=2.2,
                zorder=3,
            )
            if condition == "actual_time":
                axis.plot(
                    [point.longitude_deg_e for point in track],
                    [point.latitude_deg for point in track],
                    color="#cc4c02",
                    linewidth=1.65,
                    linestyle="--",
                    marker="o",
                    markersize=3.2,
                    markerfacecolor="white",
                    markeredgecolor="#cc4c02",
                    markeredgewidth=0.8,
                    alpha=0.88,
                    zorder=4,
                )
            altitude_midpoints = [
                None if row.altitude_minimum_km is None
                else (row.altitude_minimum_km + row.altitude_maximum_km) / 2.0
                for row in panel
            ]
            if panel:
                axis.scatter(
                    [row.longitude_deg_e for row in panel],
                    [row.latitude_deg for row in panel],
                    c=[row.independent_links for row in panel],
                    s=_altitude_sizes(altitude_midpoints, altitude_domain),
                    cmap=cmap,
                    norm=norm,
                    alpha=0.90,
                    edgecolors="#101010",
                    linewidths=0.55,
                    zorder=5,
                    rasterized=True,
                )
            if arc_truth is not None and condition == "actual_time":
                nearest_report = "nearest retained ACARS" in arc_truth.position_method
                axis.scatter(
                    [arc_truth.longitude_deg_e],
                    [arc_truth.latitude_deg],
                    marker="D" if nearest_report else "*",
                    s=105 if nearest_report else 235,
                    facecolor="#d73027",
                    edgecolor="white",
                    linewidth=1.2,
                    zorder=10,
                )
                if panel:
                    nearest_cluster = min(
                        panel,
                        key=lambda cluster: great_circle_distance_km(
                            arc_truth.latitude_deg,
                            arc_truth.longitude_deg_e,
                            cluster.latitude_deg,
                            cluster.longitude_deg_e,
                        ),
                    )
                    axis.plot(
                        [arc_truth.longitude_deg_e, nearest_cluster.longitude_deg_e],
                        [arc_truth.latitude_deg, nearest_cluster.latitude_deg],
                        color="#d73027",
                        linewidth=1.15,
                        linestyle=(0, (3, 2)),
                        alpha=0.90,
                        zorder=8,
                    )
            summary = summary_lookup[(epoch.epoch_id, screen, condition)]
            nearest = summary["nearest_arc_epoch_reference_horizontal_km"]
            nearest_text = "—" if nearest == "" else f"{float(nearest):.1f} km"
            if condition == "actual_time":
                recovered = summary["recovered_within_tolerance"]
                recovery_text = (
                    "not scored" if recovered == ""
                    else "yes" if bool(recovered) else "no"
                )
                annotation = (
                    f"Residual clusters: {summary['residual_cluster_count']}\n"
                    f"Nearest plotted residual to arc-time reference: {nearest_text}\n"
                    f"Time-aligned 25-km recovery: {recovery_text}"
                )
            else:
                annotation = (
                    f"Residual clusters: {summary['residual_cluster_count']}\n"
                    "Shifted-time control; aircraft distance not scored"
                )
            axis.text(
                0.025,
                0.975,
                annotation,
                transform=axis.transAxes,
                va="top",
                ha="left",
                fontsize=8.4,
                linespacing=1.25,
                bbox={
                    "boxstyle": "round,pad=0.35",
                    "facecolor": "white",
                    "edgecolor": "#9a9a9a",
                    "alpha": 0.95,
                },
                zorder=9,
            )
            if arc_truth is not None and condition == "actual_time":
                lag = abs(arc_truth.time_offset_seconds)
                lag_note = (
                    "time-aligned" if lag < 0.05
                    else f"offset {arc_truth.time_offset_seconds:+.1f} s"
                )
                altitude_note = (
                    "altitude unavailable" if arc_truth.altitude_km is None
                    else f"altitude {arc_truth.altitude_km:.1f} km"
                )
                axis.text(
                    0.025,
                    0.025,
                    (
                        f"Withheld reference: {altitude_note}; {lag_note}\n"
                        f"{arc_truth.position_source}; {arc_truth.position_method}"
                    ),
                    transform=axis.transAxes,
                    va="bottom",
                    ha="left",
                    fontsize=7.2,
                    color="#333333",
                    bbox={
                        "boxstyle": "round,pad=0.30",
                        "facecolor": "white",
                        "edgecolor": "#c0c0c0",
                        "alpha": 0.92,
                    },
                    zorder=9,
                )
            if row_index == 0:
                axis.set_title(
                    CONDITION_LABELS[condition], fontsize=12.0, weight="bold"
                )
            axis.set_xlim(extent[0], extent[1])
            axis.set_ylim(*latitude_limits)
            _format_latitude_axis(axis)
            axis.set_aspect(
                1.0 / max(0.15, math.cos(math.radians(midpoint_latitude)))
            )
            axis.grid(color="#b8b8b8", alpha=0.30, linewidth=0.6, zorder=-1)
            if column_index == len(CONDITIONS) - 1:
                _draw_latitude_scale_bar(axis, latitude_limits)
            if row_index == row_count - 1:
                axis.set_xlabel("Longitude (°E)")
        axes[row_index, 0].set_ylabel(
            f"{_display_time(epoch.arc_time_utc)}\nLatitude",
            fontsize=9.2,
        )

    mappable = ScalarMappable(norm=norm, cmap=cmap)
    mappable.set_array([])
    colorbar_axis = fig.add_axes([0.925, 0.24, 0.012, 0.52])
    colorbar = fig.colorbar(
        mappable,
        cax=colorbar_axis,
        ticks=list(range(minimum_support, maximum_support + 1)),
    )
    colorbar.set_label("Independent contributing links")

    legend_handles = [
        Line2D([], [], color="#151515", linewidth=2.2, label="BTO arc"),
        Line2D(
            [], [], color="#cc4c02", linewidth=1.65, linestyle="--",
            marker="o", markersize=3.2, markerfacecolor="white",
            markeredgecolor="#cc4c02",
            label=(
                "ACARS report positions joined in time order "
                "(post-selection context)"
            ),
        ),
        Line2D(
            [], [], marker="*", linestyle="none", markersize=13,
            markerfacecolor="#d73027", markeredgecolor="white",
            label="Interpolated withheld aircraft reference",
        ),
    ]
    if any(
        "nearest retained ACARS" in truth.position_method
        for epoch in epochs
        if (truth := truths.arc_epoch.get(epoch.epoch_id)) is not None
    ):
        legend_handles.append(
            Line2D(
                [], [], marker="D", linestyle="none", markersize=8,
                markerfacecolor="#d73027", markeredgecolor="white",
                label="Nearest retained report reference (not propagated)",
            )
        )
    if screen == "common_aircraft_altitude":
        selections = sorted({
            altitude_grid[0],
            altitude_grid[len(altitude_grid) // 2],
            altitude_grid[-1],
        })
        sizes = _altitude_sizes(selections, altitude_domain)
        legend_handles.extend(
            Line2D(
                [], [], marker="o", linestyle="none",
                markersize=math.sqrt(size) * 0.72,
                markerfacecolor="#b8b8b8", markeredgecolor="#101010",
                label=f"Feasible-altitude midpoint {altitude:g} km",
            )
            for altitude, size in zip(selections, sizes)
        )
    fig.legend(
        handles=legend_handles,
        loc="lower center",
        ncol=min(5, len(legend_handles)),
        fontsize=8.6,
        frameon=True,
        bbox_to_anchor=(0.48, 0.014),
    )

    page_label = "" if page_count == 1 else f" — page {page_index + 1} of {page_count}"
    fig.suptitle(
        f"{flight} known-flight WSPR controls{page_label}\n"
        f"PHaRLAP-filtered residuals: {SCREEN_LABELS[screen]}",
        fontsize=15.0,
        y=0.985,
    )
    fig.text(
        0.48,
        0.090,
        (
            f"Blind, epoch-partitioned selection; "
            f"{float(metadata['cluster_radius_km']):g} km clustering, "
            f"{float(metadata['residual_tolerance_km']):g} km symmetric "
            f"residualization, ≥{metadata['minimum_independent_links']} independent "
            "links. Withheld aircraft references appear only in arc-time panels and "
            "were added after selection. Whole-window proximity uses the static arc-"
            "epoch reference; "
            "recovery uses the physical WSPR slot nearest the arc epoch and central-"
            "window truth evaluated at its midpoint. The same central-slot truth is "
            "reused as a reference in both controls; it is not aircraft truth at the "
            "shifted radio times."
            " The orange line joins reported ACARS positions in time order in the "
            "arc-time panels only as post-selection context; positions between "
            "reports are not observed and the line does not enter selection or "
            "scoring. Latitude limits are symmetric about the withheld arc-time "
            "position for each row and identical across its three panels; pale-"
            "grey latitude bands lie outside the frozen candidate-search domain. "
            "The ruler at right is a north/south great-circle distance."
        ),
        ha="center",
        va="bottom",
        fontsize=8.2,
        color="#333333",
        wrap=True,
    )
    if screen == "common_aircraft_altitude":
        fig.text(
            0.48,
            0.066,
            (
                "Control persistence is tested on source altitude-slice clusters "
                "across any height; only surviving sources are then collapsed into "
                "one event marker for display and counting. Marker size uses the "
                "feasible-set midrange as a geometry encoding, not evidential "
                "strength, and the audit CSV retains every source ID. "
                "Confirmatory recovery uses the surviving pre-collapse source "
                "centres and exact heights, not the displayed representative. "
                f"Time-aligned recovery uses a "
                f"{float(metadata['truth_recovery_altitude_tolerance_km']):g} km "
                "primary altitude allowance because ACARS pressure altitude and "
                "modeled geometric ray height are not identical; "
                f"sensitivities are {', '.join(f'{float(value):g}' for value in metadata['truth_recovery_altitude_sensitivity_km'])} km."
            ),
            ha="center",
            va="bottom",
            fontsize=7.8,
            color="#444444",
            wrap=True,
        )
    fig.subplots_adjust(
        left=0.06,
        right=0.91,
        bottom=0.170 if screen == "surface_endpoint" else 0.185,
        top=0.90,
        wspace=0.10,
        hspace=0.13,
    )

    stem = _figure_stem(flight, screen, page_index, page_count)
    png, pdf, svg = (
        output_directory / f"{stem}.png",
        output_directory / f"{stem}.pdf",
        output_directory / f"{stem}.svg",
    )
    fig.savefig(png, dpi=300, facecolor="white")
    fig.savefig(pdf, facecolor="white")
    fig.savefig(svg, facecolor="white")
    plt.close(fig)
    return png, pdf, svg


def _draw_raw_flight_page(
    flight: str,
    page_index: int,
    page_count: int,
    epochs: Sequence[ArcPoint],
    arcs_by_epoch: Mapping[str, Sequence[ArcPoint]],
    clusters: Sequence[ClusterRow],
    truths: TruthReferences,
    tracks_by_flight: Mapping[str, Sequence[TrackPoint]],
    screen: str,
    metadata: Mapping[str, object],
    summary_lookup: Mapping[tuple[str, str], Mapping[str, object]],
    support_limits: tuple[int, int],
    output_directory: Path,
) -> tuple[Path, Path, Path]:
    """Draw central-window clusters before cross-condition subtraction."""
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        from matplotlib.colors import BoundaryNorm
        from matplotlib.lines import Line2D
        from matplotlib.cm import ScalarMappable
    except ImportError as error:
        raise RuntimeError(
            "matplotlib is required to generate publication figures"
        ) from error

    minimum_support, maximum_support = support_limits
    boundaries = [
        value - 0.5 for value in range(minimum_support, maximum_support + 2)
    ]
    cmap = plt.get_cmap("viridis", maximum_support - minimum_support + 1)
    norm = BoundaryNorm(boundaries, cmap.N)
    extent = [float(value) for value in metadata["map_extent_lon_lat"]]
    altitude_grid = [float(value) for value in metadata["aircraft_altitude_grid_km"]]
    altitude_domain = min(altitude_grid), max(altitude_grid)
    track = tracks_by_flight[flight]
    page_epoch_ids = {epoch.epoch_id for epoch in epochs}
    has_panel_clusters = any(
        row.epoch_id in page_epoch_ids
        and row.screen == screen
        and row.condition == "actual_time"
        for row in clusters
    )

    row_count = len(epochs)
    fig, axes = plt.subplots(
        row_count,
        1,
        figsize=(11.0, 4.75 * row_count + 2.0),
        sharex=True,
        sharey=False,
        squeeze=False,
    )
    for row_index, epoch in enumerate(epochs):
        axis = axes[row_index, 0]
        arc = arcs_by_epoch[epoch.epoch_id]
        truth = truths.arc_epoch.get(epoch.epoch_id)
        panel = [
            row for row in clusters
            if row.epoch_id == epoch.epoch_id
            and row.screen == screen
            and row.condition == "actual_time"
        ]
        latitude_limits = _truth_centered_latitude_limits(
            arc, panel, truth, extent
        )
        midpoint_latitude = sum(latitude_limits) / 2.0
        _shade_outside_search_latitude(
            axis, latitude_limits, extent, label=True
        )
        axis.plot(
            [point.longitude_deg_e for point in arc],
            [point.latitude_deg for point in arc],
            color="#151515",
            linewidth=2.2,
            zorder=3,
        )
        axis.plot(
            [point.longitude_deg_e for point in track],
            [point.latitude_deg for point in track],
            color="#cc4c02",
            linewidth=1.65,
            linestyle="--",
            marker="o",
            markersize=3.2,
            markerfacecolor="white",
            markeredgecolor="#cc4c02",
            markeredgewidth=0.8,
            alpha=0.88,
            zorder=4,
        )
        altitude_midpoints = [
            None if row.altitude_minimum_km is None
            else (row.altitude_minimum_km + row.altitude_maximum_km) / 2.0
            for row in panel
        ]
        if panel:
            axis.scatter(
                [row.longitude_deg_e for row in panel],
                [row.latitude_deg for row in panel],
                c=[row.independent_links for row in panel],
                s=_altitude_sizes(altitude_midpoints, altitude_domain),
                cmap=cmap,
                norm=norm,
                alpha=0.90,
                edgecolors="#101010",
                linewidths=0.55,
                zorder=5,
                rasterized=True,
            )
        if truth is not None:
            nearest_report = "nearest retained ACARS" in truth.position_method
            axis.scatter(
                [truth.longitude_deg_e],
                [truth.latitude_deg],
                marker="D" if nearest_report else "*",
                s=105 if nearest_report else 235,
                facecolor="#d73027",
                edgecolor="white",
                linewidth=1.2,
                zorder=10,
            )
            if panel:
                nearest_cluster = min(
                    panel,
                    key=lambda cluster: great_circle_distance_km(
                        truth.latitude_deg,
                        truth.longitude_deg_e,
                        cluster.latitude_deg,
                        cluster.longitude_deg_e,
                    ),
                )
                axis.plot(
                    [truth.longitude_deg_e, nearest_cluster.longitude_deg_e],
                    [truth.latitude_deg, nearest_cluster.latitude_deg],
                    color="#d73027",
                    linewidth=1.15,
                    linestyle=(0, (3, 2)),
                    alpha=0.90,
                    zorder=8,
                )
        summary = summary_lookup[(epoch.epoch_id, screen)]
        nearest = summary["nearest_arc_epoch_reference_horizontal_km"]
        nearest_text = "—" if nearest == "" else f"{float(nearest):.1f} km"
        axis.text(
            0.025,
            0.975,
            (
                f"Raw central-window clusters: {summary['raw_cluster_count']}\n"
                f"Nearest to withheld arc-time reference: {nearest_text}"
            ),
            transform=axis.transAxes,
            va="top",
            ha="left",
            fontsize=8.8,
            linespacing=1.25,
            bbox={
                "boxstyle": "round,pad=0.35",
                "facecolor": "white",
                "edgecolor": "#9a9a9a",
                "alpha": 0.95,
            },
            zorder=9,
        )
        if truth is not None:
            altitude_note = (
                "altitude unavailable" if truth.altitude_km is None
                else f"altitude {truth.altitude_km:.1f} km"
            )
            axis.text(
                0.025,
                0.025,
                (
                    f"Withheld arc-time reference: {altitude_note}\n"
                    f"Source: {truth.position_source}\n"
                    f"Method: {truth.position_method}"
                ),
                transform=axis.transAxes,
                va="bottom",
                ha="left",
                fontsize=7.4,
                color="#333333",
                bbox={
                    "boxstyle": "round,pad=0.30",
                    "facecolor": "white",
                    "edgecolor": "#c0c0c0",
                    "alpha": 0.92,
                },
                zorder=9,
            )
        axis.set_xlim(extent[0], extent[1])
        axis.set_ylim(*latitude_limits)
        _format_latitude_axis(axis)
        axis.set_aspect(
            1.0 / max(0.15, math.cos(math.radians(midpoint_latitude)))
        )
        axis.grid(color="#b8b8b8", alpha=0.30, linewidth=0.6, zorder=-1)
        _draw_latitude_scale_bar(axis, latitude_limits)
        axis.set_ylabel(
            f"{_display_time(epoch.arc_time_utc)}\nLatitude", fontsize=9.2
        )
        if row_index == row_count - 1:
            axis.set_xlabel("Longitude (°E)")

    mappable = ScalarMappable(norm=norm, cmap=cmap)
    mappable.set_array([])
    if has_panel_clusters and minimum_support != maximum_support:
        colorbar_axis = fig.add_axes([0.905, 0.24, 0.018, 0.52])
        colorbar = fig.colorbar(
            mappable,
            cax=colorbar_axis,
            ticks=list(range(minimum_support, maximum_support + 1)),
        )
        colorbar.set_label("Independent contributing links")

    legend_handles = [
        Line2D([], [], color="#151515", linewidth=2.2, label="BTO arc"),
        Line2D(
            [], [], color="#cc4c02", linewidth=1.65, linestyle="--",
            marker="o", markersize=3.2, markerfacecolor="white",
            markeredgecolor="#cc4c02",
            label=(
                "ACARS report positions joined in time order "
                "(post-selection context)"
            ),
        ),
        Line2D(
            [], [], marker="*", linestyle="none", markersize=13,
            markerfacecolor="#d73027", markeredgecolor="white",
            label="Interpolated withheld aircraft reference",
        ),
    ]
    if has_panel_clusters and minimum_support == maximum_support:
        legend_handles.append(
            Line2D(
                [], [], marker="o", linestyle="none", markersize=6.5,
                markerfacecolor=cmap(norm(minimum_support)),
                markeredgecolor="#101010",
                label=(
                    "PHaRLAP-filtered cluster "
                    f"({minimum_support} independent links)"
                ),
            )
        )
    if any(
        "nearest retained ACARS" in reference.position_method
        for epoch in epochs
        if (reference := truths.arc_epoch.get(epoch.epoch_id)) is not None
    ):
        legend_handles.append(
            Line2D(
                [], [], marker="D", linestyle="none", markersize=8,
                markerfacecolor="#d73027", markeredgecolor="white",
                label="Nearest retained report reference (not propagated)",
            )
        )
    if screen == "common_aircraft_altitude" and has_panel_clusters:
        selections = sorted({
            altitude_grid[0],
            altitude_grid[len(altitude_grid) // 2],
            altitude_grid[-1],
        })
        sizes = _altitude_sizes(selections, altitude_domain)
        legend_handles.extend(
            Line2D(
                [], [], marker="o", linestyle="none",
                markersize=math.sqrt(size) * 0.72,
                markerfacecolor="#b8b8b8", markeredgecolor="#101010",
                label=f"Feasible-altitude midpoint {altitude:g} km",
            )
            for altitude, size in zip(selections, sizes)
        )
    fig.legend(
        handles=legend_handles,
        loc="lower center",
        ncol=min(3, len(legend_handles)),
        fontsize=8.4,
        frameon=True,
        bbox_to_anchor=(0.47, 0.014),
    )

    page_label = "" if page_count == 1 else f" — page {page_index + 1} of {page_count}"
    fig.suptitle(
        f"{flight} known-flight WSPR arc-time windows{page_label}\n"
        f"PHaRLAP-filtered raw clusters before control subtraction: "
        f"{SCREEN_LABELS[screen]}",
        fontsize=14.0,
        y=0.985,
    )
    fig.text(
        0.47,
        0.090,
        (
            f"Blind, epoch-partitioned selection; "
            f"{float(metadata['cluster_radius_km']):g} km clustering, "
            f"≥{metadata['minimum_independent_links']} independent links. "
            "These are all PHaRLAP-screened clusters in the central arc-time "
            "window before the ±60-minute controls are subtracted. Distance is "
            "to the static aircraft position at the BTO epoch and is descriptive, "
            "not a time-aligned recovery score for clusters from other WSPR slots. "
            "Truth and the joined report track were added only after selection. "
            "Latitude limits are symmetric about truth; pale-grey bands are outside "
            "the frozen candidate-search latitude. The ruler is a north/south "
            "great-circle distance."
            + (
                f" All retained raw clusters have {minimum_support} independent links."
                if has_panel_clusters and minimum_support == maximum_support else ""
            )
        ),
        ha="center",
        va="bottom",
        fontsize=8.0,
        color="#333333",
        wrap=True,
    )
    if screen == "common_aircraft_altitude" and has_panel_clusters:
        fig.text(
            0.47,
            0.066,
            (
                "Each marker is a spatially collapsed event with retained source "
                "altitude slices. Marker size encodes feasible-set midrange, not "
                "evidential strength; the audit CSV retains the source IDs."
            ),
            ha="center",
            va="bottom",
            fontsize=7.7,
            color="#444444",
            wrap=True,
        )
    fig.subplots_adjust(
        left=0.11,
        right=0.88,
        bottom=0.175,
        top=0.90,
        hspace=0.14,
    )

    stem = _raw_figure_stem(flight, screen, page_index, page_count)
    png, pdf, svg = (
        output_directory / f"{stem}.png",
        output_directory / f"{stem}.pdf",
        output_directory / f"{stem}.svg",
    )
    fig.savefig(png, dpi=300, facecolor="white")
    fig.savefig(pdf, facecolor="white")
    fig.savefig(svg, facecolor="white")
    plt.close(fig)
    return png, pdf, svg


def generate(
    cluster_path: Path,
    raw_cluster_path: Path,
    arc_path: Path,
    truth_path: Path,
    track_path: Path,
    track_metadata_path: Path,
    truth_score_path: Path,
    metadata_path: Path,
    output_directory: Path,
    screens: Sequence[str] = SCREENS,
) -> tuple[Path, Path]:
    invalid = set(screens).difference(SCREENS)
    if invalid:
        raise ValueError(f"unknown screens: {sorted(invalid)}")
    metadata = read_metadata(metadata_path)
    clusters = read_clusters(cluster_path)
    raw_clusters = read_clusters(raw_cluster_path, raw_input=True)
    arcs = read_arcs(arc_path)
    truths = read_truth(truth_path)
    tracks = read_tracks(track_path)
    track_provenance = read_track_provenance(
        track_metadata_path, track_path, tracks
    )
    truth_scores = read_truth_scores(truth_score_path)
    output_directory.mkdir(parents=True, exist_ok=True)

    epoch_groups: dict[str, list[ArcPoint]] = {}
    for point in arcs:
        epoch_groups.setdefault(point.epoch_id, []).append(point)
    arc_flights = {points[0].flight for points in epoch_groups.values()}
    if set(tracks) != arc_flights:
        raise ValueError(
            "track flights do not exactly match arc flights: "
            f"tracks={sorted(tracks)}, arcs={sorted(arc_flights)}"
        )
    for cluster in (*clusters, *raw_clusters):
        if cluster.epoch_id not in epoch_groups:
            raise ValueError(f"cluster epoch absent from arcs: {cluster.epoch_id}")
        epoch = epoch_groups[cluster.epoch_id][0]
        if (cluster.flight, cluster.arc_time_utc) != (epoch.flight, epoch.arc_time_utc):
            raise ValueError(f"cluster metadata does not match arc: {cluster.epoch_id}")
    truth_epochs = set(truths.arc_epoch) | {
        epoch_id for epoch_id, _ in truths.all_physical_slots
    }
    unknown_truth = truth_epochs.difference(epoch_groups)
    if unknown_truth:
        raise ValueError(f"truth epoch absent from arcs: {sorted(unknown_truth)}")
    unknown_scores = {
        epoch_id for epoch_id, _, _ in truth_scores
    }.difference(epoch_groups)
    if unknown_scores:
        raise ValueError(f"truth-score epoch absent from arcs: {sorted(unknown_scores)}")
    expected_scores = {
        (epoch_id, screen, condition)
        for epoch_id in truths.nearest_physical_slot
        for screen in screens
        for condition in CONDITIONS
    }
    missing_scores = expected_scores.difference(truth_scores)
    if missing_scores:
        raise ValueError(f"missing authoritative truth-score panels: {sorted(missing_scores)}")
    expected_sensitivities = {
        f"{float(value):g}"
        for value in metadata["truth_recovery_altitude_sensitivity_km"]
    }
    for key, score in truth_scores.items():
        if not math.isclose(
            score.horizontal_tolerance_km,
            float(metadata["truth_recovery_tolerance_km"]),
            abs_tol=1e-12,
        ):
            raise ValueError(f"truth-score horizontal tolerance mismatch: {key}")
        if score.screen == "common_aircraft_altitude":
            if score.altitude_tolerance_km is None or not math.isclose(
                score.altitude_tolerance_km,
                float(metadata["truth_recovery_altitude_tolerance_km"]),
                abs_tol=1e-12,
            ):
                raise ValueError(f"truth-score altitude tolerance mismatch: {key}")
            if set(score.altitude_sensitivity_recovered) != expected_sensitivities:
                raise ValueError(f"truth-score altitude sensitivities mismatch: {key}")

    summary = build_summary(
        arcs,
        clusters,
        truths,
        truth_scores,
        screens,
    )
    raw_summary = build_raw_actual_summary(
        arcs,
        raw_clusters,
        truths,
        screens,
    )
    summary_lookup = {
        (str(row["epoch_id"]), str(row["screen"]), str(row["condition"])): row
        for row in summary
    }
    support_limits = _support_limits(
        clusters, screens, int(metadata["minimum_independent_links"])
    )
    raw_support_limits = _support_limits(
        raw_clusters,
        screens,
        int(metadata["minimum_independent_links"]),
        residual_only=False,
        condition="actual_time",
    )
    output_paths: list[Path] = []
    pages = epoch_pages(arcs)
    arcs_by_epoch = {
        epoch_id: tuple(sorted(points, key=lambda point: point.arc_point_index))
        for epoch_id, points in epoch_groups.items()
    }
    for flight, page_index, page_count, epochs in pages:
        for screen in screens:
            output_paths.extend(_draw_flight_page(
                flight,
                page_index,
                page_count,
                epochs,
                arcs_by_epoch,
                clusters,
                truths,
                tracks,
                screen,
                metadata,
                summary_lookup,
                support_limits,
                output_directory,
            ))
            raw_lookup = {
                (str(row["epoch_id"]), str(row["screen"])): row
                for row in raw_summary
            }
            output_paths.extend(_draw_raw_flight_page(
                flight,
                page_index,
                page_count,
                epochs,
                arcs_by_epoch,
                raw_clusters,
                truths,
                tracks,
                screen,
                metadata,
                raw_lookup,
                raw_support_limits,
                output_directory,
            ))

    summary_path = output_directory / "known-flight-pharlap-residual-control-summary.csv"
    _write_summary(summary_path, summary)
    output_paths.append(summary_path)
    raw_summary_path = output_directory / "known-flight-pharlap-raw-actual-summary.csv"
    _write_raw_summary(raw_summary_path, raw_summary)
    output_paths.append(raw_summary_path)
    audit_path = output_directory / "known-flight-pharlap-residual-cluster-plot-audit.csv"
    audit_rows: list[dict[str, object]] = []
    for row in clusters:
        summary_row = summary_lookup.get((row.epoch_id, row.screen, row.condition))
        plotted = row.is_residual and row.screen in screens
        audit_rows.append({
            "input_row_number": row.input_row_number,
            "epoch_id": row.epoch_id,
            "flight": row.flight,
            "arc_time_utc": row.arc_time_utc,
            "screen": row.screen,
            "condition": row.condition,
            "physical_slot": row.physical_slot,
            "cluster_rank": row.cluster_rank,
            "center_candidate_id": row.center_candidate_id,
            "latitude_deg": row.latitude_deg,
            "longitude_deg_e": row.longitude_deg_e,
            "altitude_km": "" if row.altitude_km is None else row.altitude_km,
            "altitude_minimum_km": (
                "" if row.altitude_minimum_km is None else row.altitude_minimum_km
            ),
            "altitude_maximum_km": (
                "" if row.altitude_maximum_km is None else row.altitude_maximum_km
            ),
            "feasible_altitude_count": row.feasible_altitude_count,
            "feasible_altitudes_km": ";".join(
                f"{value:g}" for value in row.feasible_altitudes_km
            ),
            "source_altitude_clusters": row.source_altitude_clusters,
            "source_altitude_cluster_ids": ";".join(
                row.source_altitude_cluster_ids
            ),
            "support_spot_ids": ";".join(
                str(value) for value in row.support_spot_ids
            ),
            "pair_intersections": row.pair_intersections,
            "support_links": row.support_links,
            "independent_links": row.independent_links,
            "nearest_other_condition_km": row.nearest_other_condition_km,
            "is_residual": str(row.is_residual).lower(),
            "plotted": str(plotted).lower(),
            "figure_png": "" if summary_row is None else summary_row["figure_png"],
            "figure_pdf": "" if summary_row is None else summary_row["figure_pdf"],
            "figure_svg": "" if summary_row is None else summary_row["figure_svg"],
        })
    with audit_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=CLUSTER_PLOT_AUDIT_COLUMNS)
        writer.writeheader()
        writer.writerows(audit_rows)
    output_paths.append(audit_path)
    raw_audit_path = (
        output_directory / "known-flight-pharlap-raw-cluster-plot-audit.csv"
    )
    raw_summary_lookup = {
        (str(row["epoch_id"]), str(row["screen"])): row
        for row in raw_summary
    }
    raw_audit_rows: list[dict[str, object]] = []
    for row in raw_clusters:
        summary_row = raw_summary_lookup.get((row.epoch_id, row.screen))
        plotted = row.condition == "actual_time" and row.screen in screens
        raw_audit_rows.append({
            "input_row_number": row.input_row_number,
            "epoch_id": row.epoch_id,
            "flight": row.flight,
            "arc_time_utc": row.arc_time_utc,
            "screen": row.screen,
            "condition": row.condition,
            "physical_slot": row.physical_slot,
            "cluster_rank": row.cluster_rank,
            "center_candidate_id": row.center_candidate_id,
            "latitude_deg": row.latitude_deg,
            "longitude_deg_e": row.longitude_deg_e,
            "altitude_km": "" if row.altitude_km is None else row.altitude_km,
            "altitude_minimum_km": (
                "" if row.altitude_minimum_km is None else row.altitude_minimum_km
            ),
            "altitude_maximum_km": (
                "" if row.altitude_maximum_km is None else row.altitude_maximum_km
            ),
            "feasible_altitude_count": row.feasible_altitude_count,
            "feasible_altitudes_km": ";".join(
                f"{value:g}" for value in row.feasible_altitudes_km
            ),
            "source_altitude_clusters": row.source_altitude_clusters,
            "source_altitude_cluster_ids": ";".join(
                row.source_altitude_cluster_ids
            ),
            "support_spot_ids": ";".join(
                str(value) for value in row.support_spot_ids
            ),
            "pair_intersections": row.pair_intersections,
            "support_links": row.support_links,
            "independent_links": row.independent_links,
            "plotted": str(plotted).lower(),
            "figure_png": (
                "" if not plotted or summary_row is None
                else summary_row["figure_png"]
            ),
            "figure_pdf": (
                "" if not plotted or summary_row is None
                else summary_row["figure_pdf"]
            ),
            "figure_svg": (
                "" if not plotted or summary_row is None
                else summary_row["figure_svg"]
            ),
        })
    with raw_audit_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle, fieldnames=RAW_CLUSTER_PLOT_AUDIT_COLUMNS
        )
        writer.writeheader()
        writer.writerows(raw_audit_rows)
    output_paths.append(raw_audit_path)
    latitude_limits_by_epoch: dict[str, dict[str, float | None]] = {}
    for epoch_id, points in sorted(arcs_by_epoch.items()):
        reference = truths.arc_epoch.get(epoch_id)
        limits = _truth_centered_latitude_limits(
            points,
            [
                row for row in (*clusters, *raw_clusters)
                if row.epoch_id == epoch_id
            ],
            reference,
            metadata["map_extent_lon_lat"],
        )
        latitude_limits_by_epoch[epoch_id] = {
            "truth_center_latitude_deg": (
                None if reference is None else reference.latitude_deg
            ),
            "south_deg": limits[0],
            "north_deg": limits[1],
        }
    manifest_path = output_directory / "known-flight-pharlap-residual-plot-manifest.json"
    manifest = {
        "schema": "mh370.wspr.pharlap.known-flight-publication-plots.v1",
        "plotter_source_sha256": _sha256(Path(__file__)),
        "run_metadata": metadata,
        "inputs": {
            str(path): _sha256(path)
            for path in (
                cluster_path,
                raw_cluster_path,
                arc_path,
                truth_path,
                track_path,
                track_metadata_path,
                truth_score_path,
                metadata_path,
            )
        },
        "outputs": {
            path.name: _sha256(path) for path in output_paths
        },
        "figures": {
            "epochs": [epoch.epoch_id for _, _, _, values in pages for epoch in values],
            "pages": [
                {
                    "flight": flight,
                    "page_index": page_index + 1,
                    "page_count": page_count,
                    "epochs": [epoch.epoch_id for epoch in epochs],
                }
                for flight, page_index, page_count, epochs in pages
            ],
            "screens": list(screens),
            "conditions": list(CONDITIONS),
            "raw_figure_condition": "actual_time",
            "png_dpi": 300,
            "support_scale": list(support_limits),
            "raw_support_scale": list(raw_support_limits),
            "raw_support_encoding": (
                f"categorical legend; every raw actual cluster has "
                f"{raw_support_limits[0]} independent links"
                if raw_support_limits[0] == raw_support_limits[1]
                else "discrete colorbar"
            ),
            "latitude_axis": {
                "centering": "withheld arc-time truth",
                "same_limits_across_conditions_within_epoch": True,
                "no_frozen_domain_clipping": True,
                "outside_search_domain_shading": "pale grey with explicit label",
                "tick_labels": "degrees north/south",
                "limits_by_epoch": latitude_limits_by_epoch,
            },
            "scale_bar": {
                "distance_km": 500.0,
                "orientation": "north-south meridional great-circle",
                "placement": "right side, centred on withheld arc-time latitude",
            },
            "truth_overlay": (
                "actual_time panel only; added after blind selection; interpolated "
                "arc-epoch positions use stars and nearest-report positions use "
                "diamonds; no sparse truth positions are joined as a trajectory"
            ),
            "track_overlay": {
                "panels": "actual_time only",
                "label": (
                    "ACARS report positions joined in time order "
                    "(post-selection context)"
                ),
                "role": track_provenance["role"],
                "rows_by_flight": track_provenance["output"]["rows_by_flight"],
                "source": track_provenance["source"],
            },
            "common_altitude_display": (
                "source altitude-slice clusters residualized across any height; "
                "survivors collapsed to one event marker; no plot-time merge"
            ),
            "raw_actual_display": (
                "all primary PHaRLAP-screened actual-time clusters before "
                "cross-condition residual subtraction; separately exported by "
                "the assembler"
            ),
            "truth_recovery_source": (
                "authoritative truth-score CSV from surviving pre-collapse source "
                "centres and exact heights"
            ),
        },
        "runtime": {
            "python": platform.python_version(),
            "matplotlib": __import__("matplotlib").__version__,
        },
    }
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return summary_path, manifest_path


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--clusters", required=True, type=Path)
    parser.add_argument("--raw-clusters", required=True, type=Path)
    parser.add_argument("--arcs", required=True, type=Path)
    parser.add_argument("--truth", required=True, type=Path)
    parser.add_argument("--tracks", required=True, type=Path)
    parser.add_argument("--track-metadata", required=True, type=Path)
    parser.add_argument("--truth-scores", required=True, type=Path)
    parser.add_argument("--run-metadata", required=True, type=Path)
    parser.add_argument("--output-directory", required=True, type=Path)
    parser.add_argument(
        "--screens",
        nargs="+",
        choices=SCREENS,
        default=list(SCREENS),
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    arguments = _parser().parse_args(argv)
    summary, manifest = generate(
        arguments.clusters,
        arguments.raw_clusters,
        arguments.arcs,
        arguments.truth,
        arguments.tracks,
        arguments.track_metadata,
        arguments.truth_scores,
        arguments.run_metadata,
        arguments.output_directory,
        arguments.screens,
    )
    print(summary)
    print(manifest)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
