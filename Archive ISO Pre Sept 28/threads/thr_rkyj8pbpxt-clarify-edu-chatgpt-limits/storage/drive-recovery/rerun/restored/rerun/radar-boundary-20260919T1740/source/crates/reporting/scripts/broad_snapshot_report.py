#!/usr/bin/env python3
"""Render structural/numerical uncertainty from broad-flight snapshots.

This reporter is deliberately diagnostic.  It never labels a conditional
posterior as the aircraft's "true" probability distribution.  Top-level
scientific families are rendered separately; only deterministic numerical
seeds within the same declared family are pooled, with equal seed weight.

When ``--truth`` is supplied, held-back positions are loaded only by this
reporting process and accuracy is calculated for matching SATCOM epochs.  With
no truth input the same path produces an accident-flight, all-physical-epoch
diagnostic without accuracy language or markers.
"""

from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
import math
import os
from pathlib import Path
import sys
import textwrap
from typing import Any, Iterable

os.environ.setdefault("MPLBACKEND", "Agg")
os.environ.setdefault("SOURCE_DATE_EPOCH", "1394237459")

import matplotlib as mpl

mpl.use("Agg")
mpl.rcParams.update(
    {
        "axes.facecolor": "#fbfcfd",
        "axes.grid": True,
        "font.family": "DejaVu Sans",
        "font.size": 8.5,
        "grid.color": "#dfe4e9",
        "grid.linewidth": 0.55,
        "pdf.fonttype": 42,
        "savefig.dpi": 220,
    }
)
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import numpy as np
from scipy.ndimage import gaussian_filter


SPEC_SCHEMA = "mh370-broad-snapshot-report-spec"
SPEC_VERSION = 1
INDEX_SCHEMA = "mh370-broad-observation-snapshot-index"
AUDIT_SCHEMA = "mh370-broad-snapshot-diagnostic"
AUDIT_VERSION = 1
EARTH_RADIUS_NM = 3440.0695
WEIGHT_TOLERANCE = 2.0e-6
DEFAULT_THRESHOLDS = {
    "minimum_particle_ess": 1000.0,
    "minimum_particle_ess_fraction": 0.005,
    "minimum_root_ess": 50.0,
    "maximum_root_mass": 0.05,
    "minimum_map_captured_mass": 0.99,
    "minimum_material_stratum_mass": 0.01,
    "minimum_material_stratum_particle_ess": 100.0,
    "minimum_material_stratum_root_ess": 20.0,
    "maximum_seed_total_variation": 0.20,
    "maximum_seed_mean_shift_nm": 25.0,
}


class ReportInputError(ValueError):
    """An input does not satisfy the report's provenance contract."""


@dataclass(frozen=True)
class Bounds:
    latitude_min: float
    latitude_max: float
    longitude_min: float
    longitude_max: float
    cell_size: float
    smoothing_sigma_cells: float

    @property
    def rows(self) -> int:
        return round((self.latitude_max - self.latitude_min) / self.cell_size)

    @property
    def columns(self) -> int:
        return round((self.longitude_max - self.longitude_min) / self.cell_size)


@dataclass(frozen=True)
class Truth:
    epoch_id: str
    time_utc: str
    seconds_from_t0: float
    latitude_deg: float
    longitude_deg: float
    heading_true_deg: float | None


@dataclass(frozen=True)
class Snapshot:
    epoch_id: str
    observation_kind: str
    enabled_evidence_components: tuple[str, ...]
    time_s: float
    time_utc: str | None
    latitude: np.ndarray
    longitude: np.ndarray
    weights: np.ndarray
    roots: np.ndarray
    strata: np.ndarray
    lateral_modes: np.ndarray
    lateral_events: np.ndarray
    speed_events: np.ndarray
    altitude_events: np.ndarray
    path: Path
    sha256: str


@dataclass(frozen=True)
class Source:
    family_id: str
    seed: int
    configured_particles: int
    index_path: Path
    index_sha256: str
    summary_path: Path
    summary_sha256: str
    log_evidence: float | None
    stratum_metadata: dict[str, dict[str, Any]]
    snapshots: dict[str, Snapshot]
    ordered_epochs: tuple[str, ...]


@dataclass(frozen=True)
class Family:
    family_id: str
    label: str
    color: str
    sources: tuple[Source, ...]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def finite(value: Any, description: str) -> float:
    try:
        result = float(value)
    except (TypeError, ValueError) as error:
        raise ReportInputError(f"{description} is not numeric") from error
    if not math.isfinite(result):
        raise ReportInputError(f"{description} is not finite")
    return result


def integer(value: Any, description: str) -> int:
    number = finite(value, description)
    if number != round(number):
        raise ReportInputError(f"{description} is not an integer")
    return int(number)


def resolve(base: Path, raw: Any, description: str) -> Path:
    if not isinstance(raw, str) or not raw:
        raise ReportInputError(f"{description} path is missing")
    path = Path(raw)
    return path if path.is_absolute() else (base.parent / path).resolve()


def load_json(path: Path, description: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ReportInputError(f"cannot read {description}: {path}") from error
    if not isinstance(value, dict):
        raise ReportInputError(f"{description} is not an object: {path}")
    return value


def parse_bounds(spec: dict[str, Any]) -> Bounds:
    raw = spec.get("map_bounds")
    if not isinstance(raw, dict):
        raise ReportInputError("specification requires fixed map_bounds")
    bounds = Bounds(
        finite(raw.get("latitude_min_deg"), "minimum map latitude"),
        finite(raw.get("latitude_max_deg"), "maximum map latitude"),
        finite(raw.get("longitude_min_deg"), "minimum map longitude"),
        finite(raw.get("longitude_max_deg"), "maximum map longitude"),
        finite(raw.get("cell_size_deg"), "map cell size"),
        finite(raw.get("smoothing_sigma_cells", 1.0), "display smoothing"),
    )
    if (
        not -90.0 <= bounds.latitude_min < bounds.latitude_max <= 90.0
        or not -180.0 <= bounds.longitude_min < bounds.longitude_max <= 180.0
        or bounds.cell_size <= 0.0
        or bounds.smoothing_sigma_cells < 0.0
    ):
        raise ReportInputError("fixed map bounds are invalid")
    rows = (bounds.latitude_max - bounds.latitude_min) / bounds.cell_size
    columns = (bounds.longitude_max - bounds.longitude_min) / bounds.cell_size
    if (
        abs(rows - round(rows)) > 1.0e-8
        or abs(columns - round(columns)) > 1.0e-8
        or round(rows) * round(columns) > 500_000
    ):
        raise ReportInputError("map grid is non-integral or exceeds 500,000 cells")
    return bounds


def load_truth(path: Path) -> tuple[dict[str, Truth], str]:
    rows: dict[str, Truth] = {}
    try:
        with path.open("r", encoding="utf-8", newline="") as stream:
            reader = csv.DictReader(stream)
            required = {
                "epoch_id",
                "time_utc",
                "seconds_from_t0",
                "lat_deg",
                "lon_deg",
            }
            if reader.fieldnames is None or not required.issubset(reader.fieldnames):
                raise ReportInputError("truth CSV lacks required fields")
            for row in reader:
                epoch = str(row["epoch_id"])
                if not epoch or epoch in rows:
                    raise ReportInputError("truth epoch identities must be unique")
                heading_raw = row.get("heading_true_deg")
                item = Truth(
                    epoch,
                    str(row["time_utc"]),
                    finite(row["seconds_from_t0"], f"truth time {epoch}"),
                    finite(row["lat_deg"], f"truth latitude {epoch}"),
                    finite(row["lon_deg"], f"truth longitude {epoch}"),
                    None
                    if heading_raw in (None, "")
                    else finite(heading_raw, f"truth heading {epoch}"),
                )
                if not -90.0 <= item.latitude_deg <= 90.0 or not -180.0 <= item.longitude_deg <= 180.0:
                    raise ReportInputError(f"truth coordinate is invalid for {epoch}")
                rows[epoch] = item
    except OSError as error:
        raise ReportInputError(f"cannot read truth CSV: {path}") from error
    if not rows:
        raise ReportInputError("truth CSV is empty")
    return rows, sha256(path)


def required_columns(fieldnames: Iterable[str] | None, path: Path) -> None:
    required = {
        "root",
        "stratum",
        "weight",
        "time_s",
        "latitude_deg",
        "longitude_deg",
        "lateral_mode",
        "lateral_events",
        "speed_events",
        "altitude_events",
    }
    if fieldnames is None or not required.issubset(fieldnames):
        raise ReportInputError(f"snapshot CSV lacks required broad-flight columns: {path}")


def load_snapshot(
    path: Path,
    digest: str,
    epoch: str,
    observation_kind: str,
    enabled_evidence_components: tuple[str, ...],
    time_s: float,
) -> Snapshot:
    if sha256(path) != digest:
        raise ReportInputError(f"snapshot SHA-256 mismatch: {path}")
    latitude: list[float] = []
    longitude: list[float] = []
    weights: list[float] = []
    roots: list[str] = []
    strata: list[str] = []
    modes: list[str] = []
    lateral: list[int] = []
    speed: list[int] = []
    altitude: list[int] = []
    total_weight = 0.0
    with path.open("r", encoding="utf-8", newline="") as stream:
        reader = csv.DictReader(stream)
        required_columns(reader.fieldnames, path)
        for number, row in enumerate(reader, start=2):
            weight = finite(row["weight"], f"snapshot weight at {path}:{number}")
            if weight < 0.0:
                raise ReportInputError(f"negative snapshot weight at {path}:{number}")
            total_weight += weight
            if weight == 0.0:
                continue
            row_time = finite(row["time_s"], f"snapshot time at {path}:{number}")
            if abs(row_time - time_s) > 1.0e-6:
                raise ReportInputError(f"particle time differs from snapshot index: {path}")
            lat = finite(row["latitude_deg"], f"latitude at {path}:{number}")
            lon = finite(row["longitude_deg"], f"longitude at {path}:{number}")
            if not -90.0 <= lat <= 90.0 or not -180.0 <= lon <= 180.0:
                raise ReportInputError(f"invalid particle coordinate at {path}:{number}")
            latitude.append(lat)
            longitude.append(lon)
            weights.append(weight)
            roots.append(str(row["root"]))
            strata.append(str(row["stratum"]))
            modes.append(str(row["lateral_mode"]))
            lateral.append(integer(row["lateral_events"], "lateral event count"))
            speed.append(integer(row["speed_events"], "speed event count"))
            altitude.append(integer(row["altitude_events"], "altitude event count"))
    if not weights or not math.isclose(total_weight, 1.0, abs_tol=WEIGHT_TOLERANCE, rel_tol=0.0):
        raise ReportInputError(f"snapshot weights do not sum to one: {path} ({total_weight:.9g})")
    normalized = np.asarray(weights, dtype=float)
    normalized /= np.sum(normalized)
    return Snapshot(
        epoch,
        observation_kind,
        enabled_evidence_components,
        time_s,
        None,
        np.asarray(latitude),
        np.asarray(longitude),
        normalized,
        np.asarray(roots, dtype=object),
        np.asarray(strata, dtype=object),
        np.asarray(modes, dtype=object),
        np.asarray(lateral, dtype=int),
        np.asarray(speed, dtype=int),
        np.asarray(altitude, dtype=int),
        path,
        digest,
    )


def load_source(spec_path: Path, family_id: str, raw: dict[str, Any]) -> Source:
    seed = integer(raw.get("seed"), f"seed in family {family_id}")
    index_path = resolve(spec_path, raw.get("snapshot_index"), "snapshot index")
    summary_path = resolve(spec_path, raw.get("summary"), "seed summary")
    index = load_json(index_path, "snapshot index")
    summary = load_json(summary_path, "seed summary")
    if (
        index.get("schema") != INDEX_SCHEMA
        or integer(index.get("schema_version"), "snapshot index schema version") != 1
        or index.get("family") != family_id
        or integer(index.get("seed"), "snapshot index seed") != seed
    ):
        raise ReportInputError(f"snapshot index identity mismatch: {index_path}")
    if summary.get("family") != family_id or integer(summary.get("seed"), "summary seed") != seed:
        raise ReportInputError(f"seed summary identity mismatch: {summary_path}")
    configured = integer(summary.get("configured_particles"), "configured particle count")
    raw_strata = index.get("scientific_strata")
    if not isinstance(raw_strata, list) or not raw_strata:
        raise ReportInputError(f"snapshot index lacks scientific-stratum metadata: {index_path}")
    stratum_metadata: dict[str, dict[str, Any]] = {}
    for item in raw_strata:
        if not isinstance(item, dict):
            raise ReportInputError(f"invalid scientific-stratum metadata: {index_path}")
        identifier = str(integer(item.get("id"), "scientific stratum id"))
        if identifier in stratum_metadata:
            raise ReportInputError(f"repeated scientific stratum id: {index_path}")
        if not isinstance(item.get("name"), str) or not isinstance(item.get("maneuver_process"), dict):
            raise ReportInputError(f"incomplete scientific stratum {identifier}: {index_path}")
        finite(item.get("scientific_prior_probability"), "scientific stratum probability")
        stratum_metadata[identifier] = item
    entries = index.get("snapshots")
    if not isinstance(entries, list) or not entries:
        raise ReportInputError(f"snapshot index is empty: {index_path}")
    snapshots: dict[str, Snapshot] = {}
    ordered: list[str] = []
    for entry in entries:
        if not isinstance(entry, dict):
            raise ReportInputError(f"snapshot index entry is not an object: {index_path}")
        observation_kind = entry.get("observation_kind")
        if observation_kind not in {"satcom", "checkpoint", "fuel_anchor"}:
            continue
        raw_epoch = entry.get("observation_id")
        epoch = (
            raw_epoch.removeprefix("held-out-")
            if observation_kind == "checkpoint" and isinstance(raw_epoch, str)
            else raw_epoch
        )
        if not isinstance(epoch, str) or not epoch or epoch in snapshots:
            raise ReportInputError(f"invalid/repeated physical epoch in {index_path}")
        raw_components = entry.get("enabled_evidence_components", [])
        if (
            not isinstance(raw_components, list)
            or any(component not in {"bto", "bfo"} for component in raw_components)
            or (observation_kind == "satcom" and not raw_components)
            or (observation_kind != "satcom" and raw_components)
        ):
            raise ReportInputError(f"invalid evidence-component ledger for {epoch}")
        time_s = finite(entry.get("observation_time_s"), f"snapshot time {epoch}")
        snapshot_path = resolve(index_path, entry.get("path"), f"snapshot {epoch}")
        digest = entry.get("sha256")
        if not isinstance(digest, str) or len(digest) != 64:
            raise ReportInputError(f"snapshot digest is invalid for {epoch}")
        snapshots[epoch] = load_snapshot(
            snapshot_path,
            digest,
            epoch,
            observation_kind,
            tuple(raw_components),
            time_s,
        )
        ordered.append(epoch)
    if not snapshots:
        raise ReportInputError(f"snapshot index contains no SATCOM/checkpoint populations: {index_path}")
    log_evidence_raw = summary.get("log_evidence")
    return Source(
        family_id,
        seed,
        configured,
        index_path,
        sha256(index_path),
        summary_path,
        sha256(summary_path),
        None if log_evidence_raw is None else finite(log_evidence_raw, "log evidence"),
        stratum_metadata,
        snapshots,
        tuple(ordered),
    )


def load_families(spec_path: Path, spec: dict[str, Any]) -> tuple[Family, ...]:
    raw_families = spec.get("families")
    if not isinstance(raw_families, list) or not raw_families:
        raise ReportInputError("specification contains no scientific families")
    families: list[Family] = []
    seen: set[str] = set()
    for raw_family in raw_families:
        if not isinstance(raw_family, dict):
            raise ReportInputError("family entry is not an object")
        family_id = raw_family.get("id")
        label = raw_family.get("label")
        color = raw_family.get("color", "#0072B2")
        if (
            not isinstance(family_id, str)
            or not family_id
            or family_id in seen
            or not isinstance(label, str)
            or not label
            or not isinstance(color, str)
        ):
            raise ReportInputError("family identity, label, or color is invalid")
        seen.add(family_id)
        raw_sources = raw_family.get("sources")
        if not isinstance(raw_sources, list) or not raw_sources:
            raise ReportInputError(f"family {family_id} contains no numerical seeds")
        sources = tuple(load_source(spec_path, family_id, item) for item in raw_sources)
        seeds = [source.seed for source in sources]
        if len(seeds) != len(set(seeds)):
            raise ReportInputError(f"family {family_id} repeats a seed")
        expected_epochs = sources[0].ordered_epochs
        if any(source.ordered_epochs != expected_epochs for source in sources[1:]):
            raise ReportInputError(f"family {family_id} seed snapshots do not align")
        reference_strata = json.dumps(sources[0].stratum_metadata, sort_keys=True)
        if any(json.dumps(source.stratum_metadata, sort_keys=True) != reference_strata for source in sources[1:]):
            raise ReportInputError(f"family {family_id} seed stratum metadata do not align")
        families.append(Family(family_id, label, color, tuple(sorted(sources, key=lambda item: item.seed))))
    epoch_order = families[0].sources[0].ordered_epochs
    if any(family.sources[0].ordered_epochs != epoch_order for family in families[1:]):
        raise ReportInputError("scientific families do not expose the same physical SATCOM-row epochs")
    for epoch in epoch_order:
        reference_time = families[0].sources[0].snapshots[epoch].time_s
        if any(
            abs(source.snapshots[epoch].time_s - reference_time) > 1.0e-6
            for family in families
            for source in family.sources
        ):
            raise ReportInputError(
                f"scientific families disagree on physical epoch time for {epoch}"
            )
    return tuple(families)


def aggregate(values: np.ndarray, weights: np.ndarray) -> dict[str, float]:
    text = values.astype(str)
    names, inverse = np.unique(text, return_inverse=True)
    masses = np.bincount(inverse, weights=weights, minlength=len(names))
    return {
        str(name): float(mass)
        for name, mass in zip(names.tolist(), masses.tolist())
    }


def aggregate_root_metrics(roots: np.ndarray, weights: np.ndarray) -> tuple[float, float, int]:
    masses = aggregate(roots, weights)
    values = np.asarray(list(masses.values()))
    return 1.0 / float(np.sum(values * values)), float(np.max(values)), len(values)


def spherical_mean(latitude: np.ndarray, longitude: np.ndarray, weights: np.ndarray) -> tuple[float, float]:
    lat = np.radians(latitude)
    lon = np.radians(longitude)
    x = float(np.sum(weights * np.cos(lat) * np.cos(lon)))
    y = float(np.sum(weights * np.cos(lat) * np.sin(lon)))
    z = float(np.sum(weights * np.sin(lat)))
    return math.degrees(math.atan2(z, math.hypot(x, y))), math.degrees(math.atan2(y, x))


def distances_nm(latitude: np.ndarray, longitude: np.ndarray, truth: Truth) -> np.ndarray:
    lat1 = np.radians(latitude)
    lat2 = math.radians(truth.latitude_deg)
    dlat = lat1 - lat2
    dlon = np.radians(longitude - truth.longitude_deg)
    a = np.sin(dlat / 2.0) ** 2 + np.cos(lat1) * math.cos(lat2) * np.sin(dlon / 2.0) ** 2
    return 2.0 * EARTH_RADIUS_NM * np.arcsin(np.sqrt(np.clip(a, 0.0, 1.0)))


def histogram(snapshot: Snapshot, bounds: Bounds) -> tuple[np.ndarray, float]:
    mass, _, _ = np.histogram2d(
        snapshot.latitude,
        snapshot.longitude,
        bins=(bounds.rows, bounds.columns),
        range=(
            (bounds.latitude_min, bounds.latitude_max),
            (bounds.longitude_min, bounds.longitude_max),
        ),
        weights=snapshot.weights,
    )
    captured = float(np.sum(mass))
    if captured > 0.0:
        mass /= captured
    return mass, captured


def smooth_display_surface(surface: np.ndarray, bounds: Bounds) -> np.ndarray:
    longitude_is_global = math.isclose(
        bounds.longitude_max - bounds.longitude_min,
        360.0,
        rel_tol=0.0,
        abs_tol=1.0e-9,
    )
    mode = ("constant", "wrap" if longitude_is_global else "constant")
    display = gaussian_filter(surface, bounds.smoothing_sigma_cells, mode=mode)
    total = float(np.sum(display))
    if total > 0.0:
        display /= total
    return display


def maneuver_rate_label(metadata: dict[str, Any]) -> str:
    process = metadata["maneuver_process"]
    labels = []
    for short, field in (("L", "lateral_clock"), ("S", "speed_clock"), ("A", "altitude_clock")):
        clock = process.get(field)
        if clock is None:
            labels.append(f"{short}=off")
        elif isinstance(clock, dict):
            mean = finite(clock.get("mean_interval_s"), f"{field} mean interval")
            labels.append(f"{short}={mean:g}s")
        else:
            raise ReportInputError(f"invalid {field} in scientific-stratum metadata")
    return "/".join(labels)


def stratum_group_mass(
    snapshot: Snapshot,
    metadata: dict[str, dict[str, Any]],
    field: str,
) -> dict[str, float]:
    labels: list[str] = []
    for identifier in snapshot.strata.astype(str):
        item = metadata.get(identifier)
        if item is None:
            raise ReportInputError(f"particle references unknown scientific stratum {identifier}")
        if field == "initial_lateral_mode":
            label = str(item.get("initial_lateral_mode"))
        elif field == "maneuver_rate_family":
            label = maneuver_rate_label(item)
        else:
            raise AssertionError("unknown stratum grouping")
        labels.append(label)
    return aggregate(np.asarray(labels, dtype=object), snapshot.weights)


def stratum_group_labels(
    snapshot: Snapshot,
    metadata: dict[str, dict[str, Any]],
    field: str,
) -> np.ndarray:
    labels: list[str] = []
    for identifier in snapshot.strata.astype(str):
        item = metadata.get(identifier)
        if item is None:
            raise ReportInputError(
                f"particle references unknown scientific stratum {identifier}"
            )
        if field == "initial_lateral_mode":
            label = str(item.get("initial_lateral_mode"))
        elif field == "maneuver_rate_family":
            label = maneuver_rate_label(item)
        else:
            raise AssertionError("unknown stratum grouping")
        labels.append(label)
    return np.asarray(labels, dtype=object)


def conditional_group_spatial_summaries(
    snapshot: Snapshot,
    labels: np.ndarray,
    truth: Truth | None,
) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    text = labels.astype(str)
    for label in sorted(set(text)):
        mask = text == label
        mass = float(np.sum(snapshot.weights[mask]))
        if mass <= 0.0:
            continue
        weights = snapshot.weights[mask] / mass
        mean_lat, mean_lon = spherical_mean(
            snapshot.latitude[mask], snapshot.longitude[mask], weights
        )
        root_ess, maximum_root_mass, root_count = aggregate_root_metrics(
            snapshot.roots[mask], weights
        )
        item: dict[str, Any] = {
            "posterior_mass": mass,
            "conditional_particle_ess": 1.0 / float(np.sum(weights * weights)),
            "conditional_root_ess": root_ess,
            "conditional_maximum_root_mass": maximum_root_mass,
            "conditional_contributing_roots": root_count,
            "conditional_posterior_mean_latitude_deg": mean_lat,
            "conditional_posterior_mean_longitude_deg": mean_lon,
            "conditional_mean_lateral_events": float(
                np.sum(weights * snapshot.lateral_events[mask])
            ),
            "conditional_mean_speed_events": float(
                np.sum(weights * snapshot.speed_events[mask])
            ),
            "conditional_mean_altitude_events": float(
                np.sum(weights * snapshot.altitude_events[mask])
            ),
        }
        if truth is not None:
            item["conditional_posterior_mean_error_nm"] = float(
                distances_nm(
                    np.asarray([mean_lat]), np.asarray([mean_lon]), truth
                )[0]
            )
        result[label] = item
    return result


def declared_structural_support(metadata: dict[str, dict[str, Any]]) -> dict[str, Any]:
    initial: dict[str, float] = {}
    rates: dict[str, float] = {}
    repeated_streams = True
    for item in metadata.values():
        probability = finite(
            item.get("scientific_prior_probability"),
            "scientific stratum prior probability",
        )
        mode = str(item.get("initial_lateral_mode"))
        rate = maneuver_rate_label(item)
        initial[mode] = initial.get(mode, 0.0) + probability
        rates[rate] = rates.get(rate, 0.0) + probability
        process = item["maneuver_process"]
        repeated_streams = repeated_streams and all(
            process.get(name) is not None
            for name in ("lateral_clock", "speed_clock", "altitude_clock")
        )
    return {
        "initial_lateral_mode_prior_mass": dict(sorted(initial.items())),
        "maneuver_rate_family_prior_mass": dict(sorted(rates.items())),
        "lateral_speed_altitude_renewal_streams_enabled": repeated_streams,
        "probability_status": "declared_not_empirically_calibrated",
    }


def snapshot_metrics(
    snapshot: Snapshot,
    bounds: Bounds,
    truth: Truth | None,
    stratum_metadata: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    particle_ess = 1.0 / float(np.sum(snapshot.weights * snapshot.weights))
    root_ess, maximum_root_mass, root_count = aggregate_root_metrics(snapshot.roots, snapshot.weights)
    mean_lat, mean_lon = spherical_mean(snapshot.latitude, snapshot.longitude, snapshot.weights)
    surface, captured = histogram(snapshot, bounds)
    strata = aggregate(snapshot.strata, snapshot.weights)
    initial_mode_labels = stratum_group_labels(
        snapshot, stratum_metadata, "initial_lateral_mode"
    )
    maneuver_rate_labels = stratum_group_labels(
        snapshot, stratum_metadata, "maneuver_rate_family"
    )
    material_strata = []
    for name, mass in strata.items():
        if mass < DEFAULT_THRESHOLDS["minimum_material_stratum_mass"]:
            continue
        mask = snapshot.strata.astype(str) == name
        conditional = snapshot.weights[mask] / mass
        conditional_root_ess, conditional_maximum_root, roots = aggregate_root_metrics(
            snapshot.roots[mask], conditional
        )
        material_strata.append(
            {
                "stratum": name,
                "posterior_mass": mass,
                "particle_ess": 1.0 / float(np.sum(conditional * conditional)),
                "root_ess": conditional_root_ess,
                "maximum_root_mass": conditional_maximum_root,
                "root_count": roots,
            }
        )
    result: dict[str, Any] = {
        "positive_particles": len(snapshot.weights),
        "particle_ess": particle_ess,
        "root_ess": root_ess,
        "maximum_root_mass": maximum_root_mass,
        "contributing_roots": root_count,
        "map_captured_mass": captured,
        "posterior_mean_latitude_deg": mean_lat,
        "posterior_mean_longitude_deg": mean_lon,
        "current_lateral_mode_mass": aggregate(snapshot.lateral_modes, snapshot.weights),
        "initial_lateral_mode_mass": stratum_group_mass(
            snapshot, stratum_metadata, "initial_lateral_mode"
        ),
        "maneuver_rate_family_mass": stratum_group_mass(
            snapshot, stratum_metadata, "maneuver_rate_family"
        ),
        "initial_lateral_mode_spatial_summaries": conditional_group_spatial_summaries(
            snapshot, initial_mode_labels, truth
        ),
        "maneuver_rate_family_spatial_summaries": conditional_group_spatial_summaries(
            snapshot, maneuver_rate_labels, truth
        ),
        "stratum_mass": strata,
        "material_strata": material_strata,
        "mean_lateral_events": float(np.sum(snapshot.weights * snapshot.lateral_events)),
        "mean_speed_events": float(np.sum(snapshot.weights * snapshot.speed_events)),
        "mean_altitude_events": float(np.sum(snapshot.weights * snapshot.altitude_events)),
        "mass_with_two_or_more_lateral_events": float(
            np.sum(snapshot.weights[snapshot.lateral_events >= 2])
        ),
    }
    if truth is not None:
        distance = distances_nm(snapshot.latitude, snapshot.longitude, truth)
        mean_position = Truth("mean", "", 0.0, mean_lat, mean_lon, None)
        result["accuracy"] = {
            "posterior_mean_error_nm": float(
                distances_nm(np.asarray([mean_lat]), np.asarray([mean_lon]), truth)[0]
            ),
            "posterior_expected_distance_nm": float(np.sum(snapshot.weights * distance)),
            "mass_within_25_nm": float(np.sum(snapshot.weights[distance <= 25.0])),
            "mass_within_50_nm": float(np.sum(snapshot.weights[distance <= 50.0])),
            "mass_within_100_nm": float(np.sum(snapshot.weights[distance <= 100.0])),
            "mass_within_200_nm": float(np.sum(snapshot.weights[distance <= 200.0])),
        }
        del mean_position
    result["_surface"] = surface
    return result


def pooled_snapshot(family: Family, epoch: str) -> Snapshot:
    count = len(family.sources)
    snapshots = [source.snapshots[epoch] for source in family.sources]
    if any(
        item.observation_kind != snapshots[0].observation_kind
        or item.enabled_evidence_components != snapshots[0].enabled_evidence_components
        for item in snapshots[1:]
    ):
        raise ReportInputError(
            f"family {family.family_id} seed evidence ledgers differ at {epoch}"
        )
    return Snapshot(
        epoch,
        snapshots[0].observation_kind,
        snapshots[0].enabled_evidence_components,
        snapshots[0].time_s,
        snapshots[0].time_utc,
        np.concatenate([item.latitude for item in snapshots]),
        np.concatenate([item.longitude for item in snapshots]),
        np.concatenate([item.weights / count for item in snapshots]),
        np.concatenate(
            [np.asarray([f"{source.seed}:{root}" for root in item.roots], dtype=object)
             for source, item in zip(family.sources, snapshots)]
        ),
        np.concatenate([item.strata for item in snapshots]),
        np.concatenate([item.lateral_modes for item in snapshots]),
        np.concatenate([item.lateral_events for item in snapshots]),
        np.concatenate([item.speed_events for item in snapshots]),
        np.concatenate([item.altitude_events for item in snapshots]),
        Path("<equal-seed pool>"),
        "",
    )


def total_variation(left: np.ndarray, right: np.ndarray) -> float:
    return 0.5 * float(np.sum(np.abs(left - right)))


def great_circle_nm(first: tuple[float, float], second: tuple[float, float]) -> float:
    proxy = Truth("point", "", 0.0, second[0], second[1], None)
    return float(distances_nm(np.asarray([first[0]]), np.asarray([first[1]]), proxy)[0])


def criterion(
    criteria: list[dict[str, Any]],
    scope: str,
    name: str,
    observed: Any,
    threshold: Any,
    passed: bool | None,
) -> None:
    criteria.append(
        {
            "scope": scope,
            "criterion": name,
            "observed": observed,
            "threshold": threshold,
            "status": "unassessed" if passed is None else ("passed" if passed else "failed"),
        }
    )


def analyze(
    spec_path: Path,
    spec: dict[str, Any],
    families: tuple[Family, ...],
    bounds: Bounds,
    truths: dict[str, Truth] | None,
    truth_path: Path | None,
    truth_sha256: str | None,
) -> tuple[dict[str, Any], dict[tuple[str, str], Snapshot]]:
    thresholds = dict(DEFAULT_THRESHOLDS)
    raw_thresholds = spec.get("numerical_thresholds", {})
    if not isinstance(raw_thresholds, dict):
        raise ReportInputError("numerical_thresholds must be an object")
    for name in thresholds:
        if name in raw_thresholds:
            thresholds[name] = finite(raw_thresholds[name], f"threshold {name}")
    model = spec.get("declared_control_history_model")
    model_ok = (
        isinstance(model, dict)
        and model.get("repeated_events") is True
        and isinstance(model.get("initial_lateral_modes"), list)
        and len(set(model["initial_lateral_modes"])) == 5
        and isinstance(model.get("maneuver_rate_families"), list)
        and len(set(model["maneuver_rate_families"])) == 4
        and model.get("probability_status") == "declared_not_empirically_calibrated"
    )
    criteria: list[dict[str, Any]] = []
    criterion(
        criteria,
        "declared-model",
        "multiple lateral modes and repeated events are in support",
        model if isinstance(model, dict) else None,
        "repeated_events=true; five initial modes; four rate families; probabilities explicitly uncalibrated",
        model_ok,
    )

    epoch_order = families[0].sources[0].ordered_epochs
    if truths is not None:
        missing = [
            epoch
            for epoch in epoch_order
            if families[0].sources[0].snapshots[epoch].observation_kind
            != "fuel_anchor"
            and epoch not in truths
        ]
        if missing:
            raise ReportInputError(f"truth CSV lacks SATCOM epochs: {', '.join(missing)}")
        for family in families:
            for source in family.sources:
                for epoch in epoch_order:
                    if source.snapshots[epoch].observation_kind == "fuel_anchor":
                        continue
                    if abs(source.snapshots[epoch].time_s - truths[epoch].seconds_from_t0) > 1.0e-6:
                        raise ReportInputError(f"truth time does not align at {epoch}")

    family_records: list[dict[str, Any]] = []
    pooled: dict[tuple[str, str], Snapshot] = {}
    for family in families:
        structural_support = declared_structural_support(
            family.sources[0].stratum_metadata
        )
        initial_priors = list(
            structural_support["initial_lateral_mode_prior_mass"].values()
        )
        rate_priors = list(
            structural_support["maneuver_rate_family_prior_mass"].values()
        )
        structural_ok = (
            len(initial_priors) == 5
            and len(rate_priors) == 4
            and all(abs(value - 0.2) <= 1.0e-10 for value in initial_priors)
            and all(abs(value - 0.25) <= 1.0e-10 for value in rate_priors)
            and structural_support[
                "lateral_speed_altitude_renewal_streams_enabled"
            ]
        )
        criterion(
            criteria,
            family.family_id,
            "declared support is five equal initial modes by four equal recurring-event rate families",
            structural_support,
            "5 × 0.2 initial modes; 4 × 0.25 rate families; all renewal streams enabled",
            structural_ok,
        )
        family_record: dict[str, Any] = {
            "id": family.family_id,
            "label": family.label,
            "color": family.color,
            "seed_pooling": "equal numerical-replicate weight within this family",
            "scientific_family_pooling": "none",
            "declared_structural_support": structural_support,
            "sources": [],
            "epochs": [],
        }
        for source in family.sources:
            family_record["sources"].append(
                {
                    "seed": source.seed,
                    "configured_particles": source.configured_particles,
                    "log_evidence": source.log_evidence,
                    "snapshot_index": {"path": str(source.index_path), "sha256": source.index_sha256},
                    "summary": {"path": str(source.summary_path), "sha256": source.summary_sha256},
                    "snapshots": [
                        {
                            "epoch_id": epoch,
                            "observation_kind": source.snapshots[epoch].observation_kind,
                            "enabled_evidence_components": list(
                                source.snapshots[epoch].enabled_evidence_components
                            ),
                            "path": str(source.snapshots[epoch].path),
                            "sha256": source.snapshots[epoch].sha256,
                        }
                        for epoch in epoch_order
                    ],
                }
            )
        for epoch in epoch_order:
            truth = (
                truths.get(epoch)
                if truths is not None
                and family.sources[0].snapshots[epoch].observation_kind
                != "fuel_anchor"
                else None
            )
            seed_metrics: list[dict[str, Any]] = []
            surfaces: list[np.ndarray] = []
            means: list[tuple[float, float]] = []
            for source in family.sources:
                metrics = snapshot_metrics(
                    source.snapshots[epoch], bounds, truth, source.stratum_metadata
                )
                surface = metrics.pop("_surface")
                surfaces.append(surface)
                means.append(
                    (
                        metrics["posterior_mean_latitude_deg"],
                        metrics["posterior_mean_longitude_deg"],
                    )
                )
                seed_metrics.append({"seed": source.seed, **metrics})
                scope = f"{family.family_id}/{epoch}/seed-{source.seed}"
                required_particle_ess = max(
                    thresholds["minimum_particle_ess"],
                    thresholds["minimum_particle_ess_fraction"] * source.configured_particles,
                )
                criterion(criteria, scope, "particle ESS", metrics["particle_ess"], required_particle_ess, metrics["particle_ess"] >= required_particle_ess)
                criterion(criteria, scope, "prior-root ESS", metrics["root_ess"], thresholds["minimum_root_ess"], metrics["root_ess"] >= thresholds["minimum_root_ess"])
                criterion(criteria, scope, "maximum prior-root mass", metrics["maximum_root_mass"], thresholds["maximum_root_mass"], metrics["maximum_root_mass"] <= thresholds["maximum_root_mass"])
                criterion(criteria, scope, "fixed map captured mass", metrics["map_captured_mass"], thresholds["minimum_map_captured_mass"], metrics["map_captured_mass"] >= thresholds["minimum_map_captured_mass"])
                for item in metrics["material_strata"]:
                    stratum_scope = f"{scope}/stratum-{item['stratum']}"
                    criterion(criteria, stratum_scope, "material-stratum particle ESS", item["particle_ess"], thresholds["minimum_material_stratum_particle_ess"], item["particle_ess"] >= thresholds["minimum_material_stratum_particle_ess"])
                    criterion(criteria, stratum_scope, "material-stratum root ESS", item["root_ess"], thresholds["minimum_material_stratum_root_ess"], item["root_ess"] >= thresholds["minimum_material_stratum_root_ess"])
            seed_tv: list[float] = []
            seed_shift: list[float] = []
            for left in range(len(family.sources)):
                for right in range(left + 1, len(family.sources)):
                    seed_tv.append(total_variation(surfaces[left], surfaces[right]))
                    seed_shift.append(great_circle_nm(means[left], means[right]))
            scope = f"{family.family_id}/{epoch}/across-seeds"
            if seed_tv:
                maximum_tv = max(seed_tv)
                maximum_shift = max(seed_shift)
                criterion(criteria, scope, "maximum seed total variation", maximum_tv, thresholds["maximum_seed_total_variation"], maximum_tv <= thresholds["maximum_seed_total_variation"])
                criterion(criteria, scope, "maximum seed mean shift (NM)", maximum_shift, thresholds["maximum_seed_mean_shift_nm"], maximum_shift <= thresholds["maximum_seed_mean_shift_nm"])
            else:
                maximum_tv = None
                maximum_shift = None
                criterion(criteria, scope, "maximum seed total variation", None, thresholds["maximum_seed_total_variation"], None)
                criterion(criteria, scope, "maximum seed mean shift (NM)", None, thresholds["maximum_seed_mean_shift_nm"], None)
            pooled_snapshot_value = pooled_snapshot(family, epoch)
            pooled[(family.family_id, epoch)] = pooled_snapshot_value
            pooled_metrics = snapshot_metrics(
                pooled_snapshot_value,
                bounds,
                truth,
                family.sources[0].stratum_metadata,
            )
            pooled_metrics.pop("_surface")
            family_record["epochs"].append(
                {
                    "epoch_id": epoch,
                    "observation_kind": pooled_snapshot_value.observation_kind,
                    "enabled_evidence_components": list(
                        pooled_snapshot_value.enabled_evidence_components
                    ),
                    "time_s": pooled_snapshot_value.time_s,
                    "truth": None
                    if truth is None
                    else {
                        "latitude_deg": truth.latitude_deg,
                        "longitude_deg": truth.longitude_deg,
                        "heading_true_deg": truth.heading_true_deg,
                        "time_utc": truth.time_utc,
                    },
                    "seed_metrics": seed_metrics,
                    "seed_spread": {
                        "maximum_total_variation": maximum_tv,
                        "maximum_posterior_mean_shift_nm": maximum_shift,
                    },
                    "equal_seed_pooled_metrics": pooled_metrics,
                }
            )
        family_records.append(family_record)

    statuses = {item["status"] for item in criteria}
    support_status = "failed" if "failed" in statuses else ("unassessed" if "unassessed" in statuses else "passed")
    watermark = (
        "FAILED NUMERICAL SUPPORT — DIAGNOSTIC ONLY"
        if support_status == "failed"
        else (
            "UNASSESSED NUMERICAL SUPPORT — DIAGNOSTIC ONLY"
            if support_status == "unassessed"
            else "CONDITIONAL MODEL DIAGNOSTIC — NOT CALIBRATED"
        )
    )
    generator = Path(__file__).resolve()
    audit = {
        "schema_id": AUDIT_SCHEMA,
        "schema_version": AUDIT_VERSION,
        "title": spec["title"],
        "flight_label": spec["flight_label"],
        "artifact_class": "diagnostic",
        "posterior_semantics": "filtering",
        "probability_interpretation": "conditional_on_declared_model_not_calibrated_true_probability",
        "truth_role": (
            "absent; no accuracy claims"
            if truths is None
            else "held back from inference and loaded only by reporter/scorer"
        ),
        "truth_input": None if truth_path is None else {"path": str(truth_path), "sha256": truth_sha256},
        "family_pooling": "none",
        "declared_control_history_model": model,
        "map_bounds": spec["map_bounds"],
        "families": family_records,
        "numerical_support": {
            "status": support_status,
            "publication_eligible": False,
            "watermark": watermark,
            "thresholds": thresholds,
            "criteria": criteria,
        },
        "limitations": [
            "No assumption-free or empirically calibrated true flight-path probability is claimed.",
            "Control modes, event-rate families, event marks, performance bounds, and their prior probabilities are declared model choices.",
            "Top-level scientific families are not pooled; seed pooling is numerical only and equal within a family.",
            "One known-flight trajectory cannot calibrate general coverage of the accident-flight technique.",
            "Map density is display-smoothed; all metrics use unsmoothed particle weights.",
        ]
        + (
            [
                "A configured fuel-state anchor is shown as a state reset with no positional likelihood; it is not a SATCOM measurement or a truth-scored epoch."
            ]
            if any(
                snapshot.observation_kind == "fuel_anchor"
                for snapshot in families[0].sources[0].snapshots.values()
            )
            else []
        ),
        "specification": {"path": str(spec_path), "sha256": sha256(spec_path)},
        "generator": {"path": str(generator), "sha256": sha256(generator)},
        "software": {
            "python": sys.version.split()[0],
            "numpy": np.__version__,
            "scipy": __import__("scipy").__version__,
            "matplotlib": mpl.__version__,
        },
    }
    return audit, pooled


def hpd_levels(surface: np.ndarray, masses: tuple[float, ...] = (0.50, 0.90, 0.95, 0.99)) -> list[float]:
    values = surface[surface > 0.0]
    if len(values) == 0:
        return []
    ordered = np.sort(values)[::-1]
    cumulative = np.cumsum(ordered)
    result = []
    for mass in masses:
        index = min(int(np.searchsorted(cumulative, mass)), len(ordered) - 1)
        result.append(float(ordered[index]))
    return sorted(set(result))


def plot_snapshot(
    axis: Any,
    snapshot: Snapshot,
    bounds: Bounds,
    color: str,
    truth: Truth | None,
) -> None:
    surface, _ = histogram(snapshot, bounds)
    display = smooth_display_surface(surface, bounds)
    extent = [bounds.longitude_min, bounds.longitude_max, bounds.latitude_min, bounds.latitude_max]
    axis.imshow(display, origin="lower", extent=extent, cmap="Blues", aspect="auto", alpha=0.88)
    levels = hpd_levels(display)
    if levels:
        lon = np.linspace(bounds.longitude_min + bounds.cell_size / 2.0, bounds.longitude_max - bounds.cell_size / 2.0, bounds.columns)
        lat = np.linspace(bounds.latitude_min + bounds.cell_size / 2.0, bounds.latitude_max - bounds.cell_size / 2.0, bounds.rows)
        axis.contour(lon, lat, display, levels=levels, colors=color, linewidths=np.linspace(0.7, 1.6, len(levels)))
    if truth is not None:
        axis.scatter([truth.longitude_deg], [truth.latitude_deg], marker="*", s=75, color="#D55E00", edgecolor="white", linewidth=0.6, zorder=9, label="held-back truth")
        if truth.heading_true_deg is not None:
            length = 0.06 * (bounds.latitude_max - bounds.latitude_min)
            heading = math.radians(truth.heading_true_deg)
            axis.arrow(truth.longitude_deg, truth.latitude_deg, length * math.sin(heading), length * math.cos(heading), color="#D55E00", width=0.0, head_width=0.18 * length, length_includes_head=True, zorder=8)
    axis.set_xlim(bounds.longitude_min, bounds.longitude_max)
    axis.set_ylim(bounds.latitude_min, bounds.latitude_max)
    axis.set_xlabel("Longitude (°E)")
    axis.set_ylabel("Latitude (°)")


def watermark(figure: Any, text: str) -> None:
    figure.text(0.5, 0.5, text, ha="center", va="center", rotation=28, fontsize=25, color="#A00000", alpha=0.12, fontweight="bold", zorder=20)


def portable_audit_path(path: str, audit_directory: Path) -> str:
    """Express a hashed audit dependency relative to the emitted audit.

    Report inputs are resolved before analysis so their hashes bind exact
    bytes.  Serializing the resolved absolute names, however, would make a
    copied release capsule point back to the producer's workstation.  POSIX
    relative names preserve the hash contract while remaining relocatable.
    """

    return Path(os.path.relpath(Path(path), audit_directory)).as_posix()


def make_audit_paths_portable(audit: dict[str, Any], audit_path: Path) -> None:
    directory = audit_path.parent
    for key in ("specification", "generator", "truth_input"):
        record = audit.get(key)
        if isinstance(record, dict) and isinstance(record.get("path"), str):
            record["path"] = portable_audit_path(record["path"], directory)
    for family in audit.get("families", []):
        if not isinstance(family, dict):
            continue
        for source in family.get("sources", []):
            if not isinstance(source, dict):
                continue
            for key in ("snapshot_index", "summary"):
                record = source.get(key)
                if isinstance(record, dict) and isinstance(record.get("path"), str):
                    record["path"] = portable_audit_path(record["path"], directory)
            for record in source.get("snapshots", []):
                if isinstance(record, dict) and isinstance(record.get("path"), str):
                    record["path"] = portable_audit_path(record["path"], directory)
    for record in audit.get("outputs", {}).values():
        if isinstance(record, dict) and isinstance(record.get("path"), str):
            record["path"] = portable_audit_path(record["path"], directory)


def metric_for(audit: dict[str, Any], family_id: str, epoch: str) -> dict[str, Any]:
    for family in audit["families"]:
        if family["id"] == family_id:
            for item in family["epochs"]:
                if item["epoch_id"] == epoch:
                    return item
    raise AssertionError("analyzed family/epoch disappeared")


def compact_mass(values: dict[str, float]) -> str:
    aliases = {
        "constant_true_heading": "CTH",
        "constant_magnetic_heading": "CMH",
        "constant_true_track": "CTT",
        "constant_magnetic_track": "CMT",
        "great_circle_track_continuation": "GC",
        "ConstantTrueHeading": "CTH",
        "ConstantMagneticHeading": "CMH",
        "ConstantTrueTrack": "CTT",
        "ConstantMagneticTrack": "CMT",
        "GreatCircleTrackContinuation": "GC",
    }
    mode_order = {
        "constant_true_heading": 0,
        "constant_magnetic_heading": 1,
        "constant_true_track": 2,
        "constant_magnetic_track": 3,
        "great_circle_track_continuation": 4,
        "ConstantTrueHeading": 0,
        "ConstantMagneticHeading": 1,
        "ConstantTrueTrack": 2,
        "ConstantMagneticTrack": 3,
        "GreatCircleTrackContinuation": 4,
    }

    def ordering(item: tuple[str, float]) -> tuple[int, float | str]:
        name = item[0]
        if name in mode_order:
            return (0, float(mode_order[name]))
        if name.startswith("L="):
            try:
                return (1, float(name.split("/", 1)[0][2:-1]))
            except ValueError:
                pass
        return (2, name)

    tokens = []
    for name, mass in sorted(values.items(), key=ordering):
        label = aliases.get(name, name)
        rates = name.split("/")
        if (
            len(rates) == 3
            and rates[0].startswith("L=")
            and rates[1].startswith("S=")
            and rates[2].startswith("A=")
            and rates[0][2:] == rates[1][2:] == rates[2][2:]
        ):
            label = f"tau={rates[0][2:]}"
        tokens.append(f"{label} {100.0 * mass:.1f}%")
    return "  ".join(tokens)


def compact_mass_lines(values: dict[str, float], groups_per_line: int) -> str:
    tokens = compact_mass(values).split("  ")
    return "\n".join(
        "  ".join(tokens[index : index + groups_per_line])
        for index in range(0, len(tokens), groups_per_line)
    )


def observation_condition_label(snapshot: Snapshot) -> str:
    if snapshot.observation_kind == "checkpoint":
        return "propagation-only checkpoint; likelihood disabled"
    if snapshot.observation_kind == "fuel_anchor":
        return "fuel-state anchor/reset; no positional likelihood"
    components = " + ".join(
        component.upper() for component in snapshot.enabled_evidence_components
    )
    return f"SATCOM likelihood update: {components}"


def structural_rows(values: dict[str, dict[str, Any]]) -> list[list[str]]:
    aliases = {
        "constant_true_heading": "constant true heading",
        "constant_magnetic_heading": "constant magnetic heading",
        "constant_true_track": "constant true track",
        "constant_magnetic_track": "constant magnetic track",
        "great_circle_track_continuation": "great-circle continuation",
    }
    rows: list[list[str]] = []
    for name, item in values.items():
        error = item.get("conditional_posterior_mean_error_nm")
        rows.append(
            [
                aliases.get(name, name),
                f"{100.0 * item['posterior_mass']:.2f}%",
                f"{item['conditional_posterior_mean_latitude_deg']:.3f}, "
                f"{item['conditional_posterior_mean_longitude_deg']:.3f}",
                f"{item['conditional_particle_ess']:.0f} / "
                f"{item['conditional_root_ess']:.1f}",
                f"{item['conditional_mean_lateral_events']:.2f} / "
                f"{item['conditional_mean_speed_events']:.2f} / "
                f"{item['conditional_mean_altitude_events']:.2f}",
                "—" if error is None else f"{error:.1f}",
            ]
        )
    return rows


def add_structural_table(
    axis: Any,
    title: str,
    values: dict[str, dict[str, Any]],
    truth_present: bool,
) -> None:
    axis.axis("off")
    axis.set_title(title, loc="left", fontsize=11, fontweight="bold", color="#0e1f35")
    table = axis.table(
        cellText=structural_rows(values),
        colLabels=[
            "Declared group",
            "Posterior mass",
            "Conditional mean lat, lon",
            "Particle / root ESS",
            "Mean events L / S / A",
            "Truth error NM" if truth_present else "Truth error",
        ],
        cellLoc="left",
        colLoc="left",
        loc="center",
        colWidths=[0.22, 0.12, 0.20, 0.15, 0.18, 0.11],
    )
    table.auto_set_font_size(False)
    table.set_fontsize(7.2)
    table.scale(1.0, 1.4)
    for (row, _column), cell in table.get_celld().items():
        if row == 0:
            cell.set_facecolor("#e9eef3")
            cell.set_text_props(weight="bold", color="#0e1f35")
        else:
            cell.set_facecolor("#fbfcfd" if row % 2 else "#f3f6f8")
        cell.set_edgecolor("#cbd3da")


def render(
    output: Path,
    spec: dict[str, Any],
    audit: dict[str, Any],
    families: tuple[Family, ...],
    bounds: Bounds,
    truths: dict[str, Truth] | None,
    pooled: dict[tuple[str, str], Snapshot],
) -> None:
    output.mkdir(parents=True, exist_ok=True)
    pdf_path = output / "broad_snapshot_diagnostic.pdf"
    png_path = output / "broad_snapshot_diagnostic.png"
    json_path = output / "broad_snapshot_diagnostic.json"
    watermark_text = audit["numerical_support"]["watermark"]
    metadata = {
        "Title": spec["title"],
        "Author": "MH370 broad-flight snapshot reporter",
        "Subject": "Conditional structural and numerical uncertainty diagnostic",
        "CreationDate": datetime.fromtimestamp(int(os.environ["SOURCE_DATE_EPOCH"]), tz=timezone.utc),
        "ModDate": datetime.fromtimestamp(int(os.environ["SOURCE_DATE_EPOCH"]), tz=timezone.utc),
    }
    with PdfPages(pdf_path, metadata=metadata) as pdf:
        cover = plt.figure(figsize=(8.27, 11.69), facecolor="white")
        cover.text(
            0.07,
            0.95,
            textwrap.fill(spec["title"], width=51, break_long_words=False),
            fontsize=18,
            color="#0e1f35",
            fontweight="bold",
            va="top",
            linespacing=1.12,
        )
        cover.text(0.07, 0.875, "Broad multi-mode, repeated-event filtering diagnostic", fontsize=11, color="#536273")
        status = audit["numerical_support"]["status"].upper()
        cover.text(0.07, 0.825, f"Numerical support: {status}", fontsize=13, fontweight="bold", color="#A00000" if status != "PASSED" else "#006B54")
        truth_text = "Held-back truth loaded for accuracy scoring" if truths is not None else "No truth loaded; no accuracy claims"
        cover.text(0.07, 0.79, truth_text, fontsize=10)
        y = 0.735
        cover.text(0.07, y, "Scientific families (never pooled)", fontsize=11, fontweight="bold")
        y -= 0.03
        for family in families:
            cover.text(0.085, y, f"• {family.label}: {len(family.sources)} deterministic seed(s)", fontsize=9.2, color=family.color)
            y -= 0.026
        y -= 0.015
        cover.text(0.07, y, "Declared control-history support", fontsize=11, fontweight="bold")
        y -= 0.03
        support = audit["families"][0]["declared_structural_support"]
        cover.text(
            0.085,
            y,
            "Five initial modes (declared prior):\n"
            + compact_mass_lines(
                support["initial_lateral_mode_prior_mass"], 3
            ),
            fontsize=8.5,
            va="top",
            linespacing=1.25,
        )
        y -= 0.058
        cover.text(
            0.085,
            y,
            "Four recurring-event rates (declared prior):\n"
            + compact_mass_lines(
                support["maneuver_rate_family_prior_mass"], 2
            ),
            fontsize=8.5,
            va="top",
            linespacing=1.25,
        )
        y -= 0.058
        recurring_text = textwrap.fill(
            "Every rate family enables recurring lateral, speed, and altitude renewal streams. "
            "Each lateral renewal can reselect any of the five modes and draw across the declared "
            "±180-degree course-change support; speed and altitude commands renew independently. "
            "All displayed prior weights are declared and uncalibrated.",
            width=96,
            break_long_words=False,
        )
        cover.text(0.085, y, recurring_text, fontsize=8.5, va="top")
        y -= 0.018 * len(recurring_text.splitlines()) + 0.016
        cover.text(0.07, y, "Interpretation limits", fontsize=11, fontweight="bold")
        y -= 0.03
        for item in audit["limitations"]:
            wrapped = textwrap.fill(
                f"• {item}",
                width=96,
                subsequent_indent="  ",
                break_long_words=False,
            )
            cover.text(0.085, y, wrapped, fontsize=8.4, va="top", linespacing=1.2)
            y -= 0.018 * len(wrapped.splitlines()) + 0.016
        failed = [item for item in audit["numerical_support"]["criteria"] if item["status"] != "passed"]
        failure_y = max(0.115, min(y - 0.006, 0.28))
        cover.text(
            0.07,
            failure_y,
            f"Failed/unassessed criteria: {len(failed)} of {len(audit['numerical_support']['criteria'])}",
            fontsize=10,
            fontweight="bold",
        )
        failure_detail = "Complete per-epoch criterion ledger: companion JSON audit."
        cover.text(
            0.085,
            failure_y - 0.028,
            failure_detail,
            fontsize=7.8,
            color="#536273",
            va="top",
            linespacing=1.15,
        )
        footer = textwrap.fill(
            "Every spatial probability shown is conditional on the declared model and evidence family. "
            "It is not a calibrated 'true uncertainty'.",
            width=85,
            break_long_words=False,
        )
        cover.text(0.07, 0.035, footer, fontsize=8.2, color="#A00000", fontweight="bold", va="bottom")
        watermark(cover, watermark_text)
        pdf.savefig(cover)
        plt.close(cover)

        epoch_order = families[0].sources[0].ordered_epochs
        for epoch in epoch_order:
            figure, axes = plt.subplots(1, len(families), figsize=(11.69, 8.27), squeeze=False)
            figure.suptitle(f"{spec['flight_label']} — {epoch} filtering posterior", fontsize=16, fontweight="bold", color="#0e1f35")
            truth = (
                truths.get(epoch)
                if truths is not None
                and pooled[(families[0].family_id, epoch)].observation_kind
                != "fuel_anchor"
                else None
            )
            for column, family in enumerate(families):
                axis = axes[0, column]
                plot_snapshot(axis, pooled[(family.family_id, epoch)], bounds, family.color, truth)
                record = metric_for(audit, family.family_id, epoch)
                metrics = record["equal_seed_pooled_metrics"]
                lines = [
                    f"{family.label} (kept separate)",
                    observation_condition_label(
                        pooled[(family.family_id, epoch)]
                    ),
                    f"particle/root ESS {metrics['particle_ess']:.0f} / {metrics['root_ess']:.1f}",
                    f"mean lateral/speed/altitude events {metrics['mean_lateral_events']:.2f} / {metrics['mean_speed_events']:.2f} / {metrics['mean_altitude_events']:.2f}",
                    f"mass with ≥2 lateral events {100 * metrics['mass_with_two_or_more_lateral_events']:.1f}%",
                    f"seed TV max {record['seed_spread']['maximum_total_variation'] if record['seed_spread']['maximum_total_variation'] is not None else float('nan'):.3f}",
                ]
                if "accuracy" in metrics:
                    lines.extend(
                        [
                            f"held-back mean error {metrics['accuracy']['posterior_mean_error_nm']:.1f} NM",
                            f"mass within 100 NM {100 * metrics['accuracy']['mass_within_100_nm']:.1f}%",
                        ]
                    )
                axis.set_title("\n".join(lines), fontsize=8.6, color=family.color)
                axis.text(
                    0.01,
                    0.01,
                    "Initial-mode posterior mass\n"
                    + compact_mass_lines(metrics["initial_lateral_mode_mass"], 3)
                    + "\nRate-family posterior mass\n"
                    + compact_mass_lines(metrics["maneuver_rate_family_mass"], 2),
                    transform=axis.transAxes,
                    fontsize=6.7,
                    va="bottom",
                    ha="left",
                    bbox={"facecolor": "white", "edgecolor": "#c6ced6", "alpha": 0.88},
                    zorder=12,
                )
            figure.text(0.5, 0.02, "Display-smoothed HPD geometry; metrics use unsmoothed weights. Families are not averaged.", ha="center", fontsize=8, color="#536273")
            watermark(figure, watermark_text)
            figure.tight_layout(rect=(0.02, 0.05, 0.98, 0.93))
            pdf.savefig(figure)
            plt.close(figure)

        final_epoch = epoch_order[-1]
        for family in families:
            metrics = metric_for(audit, family.family_id, final_epoch)[
                "equal_seed_pooled_metrics"
            ]
            figure, axes = plt.subplots(2, 1, figsize=(11.69, 8.27))
            figure.suptitle(
                f"{spec['flight_label']} — structural sensitivity at {final_epoch}",
                fontsize=15,
                fontweight="bold",
                color="#0e1f35",
            )
            figure.text(
                0.06,
                0.925,
                f"{family.label}; groups remain explicit conditionals inside this declared family. "
                "Differences in conditional mean location are structural spread, not Monte Carlo error.",
                fontsize=8.4,
                color="#536273",
            )
            add_structural_table(
                axes[0],
                "Five declared initial lateral modes",
                metrics["initial_lateral_mode_spatial_summaries"],
                truths is not None,
            )
            add_structural_table(
                axes[1],
                "Four declared recurring-event rate families",
                metrics["maneuver_rate_family_spatial_summaries"],
                truths is not None,
            )
            figure.text(
                0.06,
                0.035,
                "Masses are posterior within the named evidence family. Declared prior weights are equal and empirically uncalibrated; no cross-family mixture is formed.",
                fontsize=8,
                color="#A00000",
                fontweight="bold",
            )
            watermark(figure, watermark_text)
            figure.tight_layout(rect=(0.03, 0.06, 0.97, 0.90))
            pdf.savefig(figure)
            plt.close(figure)

    epoch_order = families[0].sources[0].ordered_epochs
    overview, axes = plt.subplots(
        len(epoch_order),
        len(families),
        figsize=(4.4 * len(families), 3.6 * len(epoch_order)),
        squeeze=False,
    )
    overview.suptitle(
        textwrap.fill(spec["title"], width=72, break_long_words=False),
        fontsize=14,
        fontweight="bold",
        color="#0e1f35",
    )
    for row, epoch in enumerate(epoch_order):
        truth = (
            truths.get(epoch)
            if truths is not None
            and pooled[(families[0].family_id, epoch)].observation_kind
            != "fuel_anchor"
            else None
        )
        for column, family in enumerate(families):
            axis = axes[row, column]
            plot_snapshot(axis, pooled[(family.family_id, epoch)], bounds, family.color, truth)
            metrics = metric_for(audit, family.family_id, epoch)["equal_seed_pooled_metrics"]
            suffix = ""
            if "accuracy" in metrics:
                suffix = f" | ≤100 NM {100 * metrics['accuracy']['mass_within_100_nm']:.1f}%"
            condition = observation_condition_label(
                pooled[(family.family_id, epoch)]
            )
            axis.set_title(
                f"{epoch} — {family.label}{suffix}\n{condition}",
                fontsize=8.2,
                color=family.color,
            )
            axis.text(
                0.01,
                0.01,
                "Initial mode mass\n"
                + compact_mass_lines(metrics["initial_lateral_mode_mass"], 3)
                + "\nRate-family mass\n"
                + compact_mass_lines(metrics["maneuver_rate_family_mass"], 2)
                + f"\nEvents L/S/A: {metrics['mean_lateral_events']:.2f}/{metrics['mean_speed_events']:.2f}/{metrics['mean_altitude_events']:.2f}",
                transform=axis.transAxes,
                fontsize=5.5,
                va="bottom",
                bbox={"facecolor": "white", "edgecolor": "#d5dbe1", "alpha": 0.84},
                zorder=12,
            )
    watermark(overview, watermark_text)
    overview.tight_layout(rect=(0.01, 0.01, 0.99, 0.97))
    overview.savefig(png_path, dpi=220, metadata={"Software": "MH370 broad-flight snapshot reporter"})
    plt.close(overview)

    audit["outputs"] = {
        "pdf": {"path": str(pdf_path), "sha256": sha256(pdf_path)},
        "png": {"path": str(png_path), "sha256": sha256(png_path)},
    }
    make_audit_paths_portable(audit, json_path)
    json_path.write_text(json.dumps(audit, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def parse_spec(path: Path) -> dict[str, Any]:
    spec = load_json(path, "report specification")
    if spec.get("schema_id") != SPEC_SCHEMA or integer(spec.get("schema_version"), "specification schema version") != SPEC_VERSION:
        raise ReportInputError("unsupported report specification")
    if not isinstance(spec.get("title"), str) or not spec["title"].strip() or not isinstance(spec.get("flight_label"), str) or not spec["flight_label"].strip():
        raise ReportInputError("report title and flight label are required")
    if spec.get("posterior_semantics") != "filtering":
        raise ReportInputError("snapshot report requires filtering posterior semantics")
    if spec.get("probability_interpretation") != "conditional_on_declared_model_not_calibrated_true_probability":
        raise ReportInputError("report must explicitly reject a calibrated 'true probability' interpretation")
    return spec


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--spec", required=True, type=Path)
    parser.add_argument("--truth", type=Path, help="held-back known-flight truth CSV; omit for accident-flight reporting")
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        spec_path = args.spec.resolve()
        spec = parse_spec(spec_path)
        bounds = parse_bounds(spec)
        families = load_families(spec_path, spec)
        truths = None
        truth_digest = None
        if args.truth is not None:
            truth_path = args.truth.resolve()
            truths, truth_digest = load_truth(truth_path)
            expected = spec.get("expected_truth_sha256")
            if expected is not None and expected != truth_digest:
                raise ReportInputError("truth SHA-256 differs from report specification")
        else:
            truth_path = None
        audit, pooled = analyze(
            spec_path,
            spec,
            families,
            bounds,
            truths,
            truth_path,
            truth_digest,
        )
        render(args.output.resolve(), spec, audit, families, bounds, truths, pooled)
    except ReportInputError as error:
        parser.error(str(error))
    print(
        f"generated diagnostic broad snapshot report in {args.output.resolve()} "
        f"(truth={'yes' if args.truth is not None else 'no'})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
