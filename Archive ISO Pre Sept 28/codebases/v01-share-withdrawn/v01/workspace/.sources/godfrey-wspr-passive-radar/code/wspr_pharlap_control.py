#!/usr/bin/env python3
"""Blind WSPR propagation controls around BTO-arc candidate intersections.

This module is deliberately independent of PHaRLAP itself.  It turns frozen,
trajectory-blind great-circle pair locations into grouped ray-tracing jobs,
then applies returned propagation results before spatial clustering.  Route
geometry is delegated to the PHaRLAP worker because its 6378.137-km sphere and
geocentric projection must not be silently replaced by a mean-radius
haversine calculation.

Two tests of a candidate are kept distinct:

* ``surface_endpoint`` reproduces the published role of PropLab: a completed
  mode must land close to the candidate when traced from each of the four
  contributing link endpoints.
* ``common_aircraft_altitude`` asks the stronger physical question: all four
  rays must pass close to the candidate at the same declared altitude.

Neither test uses a known aircraft position to select candidates.  Truth is
accepted only by the separate scoring functions at the end of this file.
"""

from __future__ import annotations

import csv
import datetime as dt
import gzip
import itertools
import math
from collections import defaultdict
from dataclasses import dataclass, field, replace
from pathlib import Path
from typing import Callable, Iterable, Mapping, Protocol, Sequence


CONTROL_CONDITIONS = ("minus_60_min", "actual_time", "plus_60_min")
ENDPOINTS = ("transmitter", "receiver")
SURFACE_SCREEN = "surface_endpoint"
ALTITUDE_SCREEN = "common_aircraft_altitude"
EARTH_MEAN_RADIUS_KM = 6371.0088
ROUTE_RESULT_SCHEMA = "mh370.wspr.pharlap.route-result.v2"
WORKER_JOB_SCHEMA = "pharlap-spherical-route-job-v1"
WORKER_RESULT_SCHEMA = "pharlap-spherical-route-result-v1"
PHARLAP_EARTH_RADIUS_KM = 6378.137
WSPR_TRANSMISSION_START_OFFSET_SECONDS = 1.0
WSPR_TRANSMISSION_DURATION_SECONDS = 110.484
WSPR_TRANSMISSION_MIDPOINT_OFFSET_SECONDS = (
    WSPR_TRANSMISSION_START_OFFSET_SECONDS
    + WSPR_TRANSMISSION_DURATION_SECONDS / 2.0
)


@dataclass(frozen=True, order=True)
class RouteJobKey:
    """One fixed PHaRLAP origin, initial direction and WSPR report."""

    spot_id: int
    endpoint: str
    branch: str

    def __post_init__(self) -> None:
        if self.endpoint not in ENDPOINTS:
            raise ValueError(f"unknown endpoint: {self.endpoint}")
        if not self.branch:
            raise ValueError("route branch must be non-empty")


@dataclass(frozen=True)
class SpotRecord:
    spot_id: int
    time_utc: str
    frequency_hz: float
    transmitter: str
    receiver: str
    transmitter_locator: str
    receiver_locator: str
    archive_transmitter_lat_deg: float
    archive_transmitter_lon_deg_e: float
    archive_receiver_lat_deg: float
    archive_receiver_lon_deg_e: float


@dataclass(frozen=True)
class CandidatePair:
    """A frozen same-slot intersection, formed without aircraft truth."""

    candidate_id: str
    epoch_id: str
    condition: str
    physical_slot: str
    radio_time: str
    spot_id_1: int
    spot_id_2: int
    transmitter_1: str
    receiver_1: str
    transmitter_2: str
    receiver_2: str
    latitude_deg: float
    longitude_deg_e: float
    crossing_angle_deg: float | None = None
    distance_to_arc_km: float | None = None
    arc_side: str | None = None
    source_fields: Mapping[str, str] = field(default_factory=dict, compare=False)

    @property
    def spot_ids(self) -> tuple[int, int]:
        return self.spot_id_1, self.spot_id_2

    def link_metadata(self) -> dict[int, tuple[str, str]]:
        return {
            self.spot_id_1: (self.transmitter_1, self.receiver_1),
            self.spot_id_2: (self.transmitter_2, self.receiver_2),
        }


@dataclass(frozen=True)
class ResolvedRoute:
    """Declared 2-D route plus diagnostics against an alternative geometry."""

    branch: str
    origin_latitude_deg: float
    origin_longitude_deg_e: float
    initial_bearing_deg: float
    target_range_km: float
    geometry_model: str
    primary_cross_track_mismatch_km: float = 0.0
    auxiliary_cross_track_mismatch_km: float | None = None
    auxiliary_direct_range_km: float | None = None
    auxiliary_direct_bearing_deg: float | None = None


class RouteResolver(Protocol):
    def resolve(
        self,
        spot: SpotRecord,
        endpoint: str,
        candidate_latitude_deg: float,
        candidate_longitude_deg_e: float,
    ) -> ResolvedRoute:
        """Resolve a candidate onto one fixed PHaRLAP great-circle branch."""


def maidenhead_six_character_center(locator: str) -> tuple[float, float]:
    value = locator.strip().upper()
    if len(value) != 6:
        raise ValueError("six-character Maidenhead locator required")
    if not (
        "A" <= value[0] <= "R" and "A" <= value[1] <= "R"
        and value[2:4].isdigit()
        and "A" <= value[4] <= "X" and "A" <= value[5] <= "X"
    ):
        raise ValueError(f"invalid six-character Maidenhead locator: {locator}")
    longitude = (
        -180.0 + (ord(value[0]) - ord("A")) * 20.0 + int(value[2]) * 2.0
        + (ord(value[4]) - ord("A")) / 12.0 + 1.0 / 24.0
    )
    latitude = (
        -90.0 + (ord(value[1]) - ord("A")) * 10.0 + int(value[3])
        + (ord(value[5]) - ord("A")) / 24.0 + 1.0 / 48.0
    )
    return latitude, longitude


def published_spherical_inverse(
    origin_latitude_deg: float,
    origin_longitude_deg_e: float,
    target_latitude_deg: float,
    target_longitude_deg_e: float,
    radius_km: float = PHARLAP_EARTH_RADIUS_KM,
) -> tuple[float, float]:
    """Minor-arc range/bearing on the paper's geodetic-latitude sphere."""
    first = math.radians(origin_latitude_deg)
    second = math.radians(target_latitude_deg)
    delta_longitude = math.radians(target_longitude_deg_e - origin_longitude_deg_e)
    y = math.sin(delta_longitude) * math.cos(second)
    x = (
        math.cos(first) * math.sin(second)
        - math.sin(first) * math.cos(second) * math.cos(delta_longitude)
    )
    central_angle = math.atan2(
        math.hypot(y, x),
        math.sin(first) * math.sin(second)
        + math.cos(first) * math.cos(second) * math.cos(delta_longitude),
    )
    return radius_km * central_angle, math.degrees(math.atan2(y, x)) % 360.0


def _bearing_difference(first: float, second: float) -> float:
    return (first - second + 180.0) % 360.0 - 180.0


def _cross_track_km(
    direct_range_km: float,
    direct_bearing_deg: float,
    slice_bearing_deg: float,
    radius_km: float = PHARLAP_EARTH_RADIUS_KM,
) -> float:
    angle = direct_range_km / radius_km
    difference = math.radians(_bearing_difference(direct_bearing_deg, slice_bearing_deg))
    return abs(radius_km * math.asin(
        max(-1.0, min(1.0, math.sin(angle) * math.sin(difference)))
    ))


class PublishedSphericalRouteResolver:
    """Primary paper-compatible sphere with exact frozen link-branch caching."""

    def __init__(self, include_auxiliary_diagnostics: bool = True) -> None:
        self._auxiliary_inverse: Callable[..., tuple[float, float]] | None = None
        if include_auxiliary_diagnostics:
            try:
                from pharlap_raytrace_worker import pharlap_spherical_inverse
            except ImportError:
                pass
            else:
                self._auxiliary_inverse = pharlap_spherical_inverse

    def resolve(
        self,
        spot: SpotRecord,
        endpoint: str,
        candidate_latitude_deg: float,
        candidate_longitude_deg_e: float,
    ) -> ResolvedRoute:
        transmitter = maidenhead_six_character_center(spot.transmitter_locator)
        receiver = maidenhead_six_character_center(spot.receiver_locator)
        if endpoint == "transmitter":
            origin, other = transmitter, receiver
        elif endpoint == "receiver":
            origin, other = receiver, transmitter
        else:
            raise ValueError(f"unknown endpoint: {endpoint}")
        _other_range, toward_bearing = published_spherical_inverse(*origin, *other)
        target_range, target_bearing = published_spherical_inverse(
            *origin, candidate_latitude_deg, candidate_longitude_deg_e
        )
        antipodal = math.isclose(
            target_range, math.pi * PHARLAP_EARTH_RADIUS_KM, abs_tol=1e-6
        )
        toward = antipodal or abs(_bearing_difference(
            target_bearing, toward_bearing
        )) <= 90.0
        slice_bearing = toward_bearing if toward else (toward_bearing + 180.0) % 360.0
        auxiliary_range = auxiliary_bearing = auxiliary_cross_track = None
        if self._auxiliary_inverse is not None:
            auxiliary_range, auxiliary_bearing = self._auxiliary_inverse(
                *origin, candidate_latitude_deg, candidate_longitude_deg_e
            )
            auxiliary_cross_track = _cross_track_km(
                auxiliary_range, auxiliary_bearing, slice_bearing
            )
        return ResolvedRoute(
            branch=("toward_other_endpoint" if toward else "away_from_other_endpoint"),
            origin_latitude_deg=origin[0],
            origin_longitude_deg_e=origin[1],
            initial_bearing_deg=slice_bearing,
            target_range_km=target_range,
            geometry_model=(
                "published geodetic-latitude great-circle sphere, R=6378.137 km; "
                "PHaRLAP projects IRI grid coordinates along the declared slice"
            ),
            primary_cross_track_mismatch_km=_cross_track_km(
                target_range, target_bearing, slice_bearing
            ),
            auxiliary_cross_track_mismatch_km=auxiliary_cross_track,
            auxiliary_direct_range_km=auxiliary_range,
            auxiliary_direct_bearing_deg=auxiliary_bearing,
        )


class AuxiliarySphereDirectRouteResolver:
    """Sensitivity: a separate direct-candidate PHaRLAP auxiliary-sphere slice."""

    def __init__(self) -> None:
        try:
            from pharlap_raytrace_worker import (
                EARTH_EQUATORIAL_RADIUS_KM,
                pharlap_spherical_inverse,
            )
        except (ImportError, AttributeError) as error:
            raise RuntimeError(
                "the PHaRLAP worker and its numerical environment are required"
            ) from error
        self._radius_km = float(EARTH_EQUATORIAL_RADIUS_KM)
        self._inverse: Callable[..., tuple[float, float]] = pharlap_spherical_inverse

    def resolve(
        self,
        spot: SpotRecord,
        endpoint: str,
        candidate_latitude_deg: float,
        candidate_longitude_deg_e: float,
    ) -> ResolvedRoute:
        transmitter = maidenhead_six_character_center(spot.transmitter_locator)
        receiver = maidenhead_six_character_center(spot.receiver_locator)
        if endpoint == "transmitter":
            origin, other = transmitter, receiver
        elif endpoint == "receiver":
            origin, other = receiver, transmitter
        else:
            raise ValueError(f"unknown endpoint: {endpoint}")
        _other_range, toward_bearing = self._inverse(*origin, *other)
        target_range, target_bearing = self._inverse(
            *origin, candidate_latitude_deg, candidate_longitude_deg_e
        )
        antipodal = math.isclose(
            target_range, math.pi * self._radius_km, abs_tol=1e-6
        )
        bearing = toward_bearing if antipodal else round(target_bearing, 9) % 360.0
        branch = (
            "direct_candidate_antipodal"
            if antipodal else f"direct_candidate_bearing_{bearing:.9f}_deg"
        )
        return ResolvedRoute(
            branch=branch,
            origin_latitude_deg=origin[0],
            origin_longitude_deg_e=origin[1],
            initial_bearing_deg=bearing,
            target_range_km=target_range,
            geometry_model=(
                "sensitivity only: direct-candidate PHaRLAP 6378.137-km auxiliary "
                "sphere with WGS84-geodetic coordinates projected to geocentric latitude"
            ),
        )


@dataclass(frozen=True)
class RouteTarget:
    candidate_id: str
    epoch_id: str
    latitude_deg: float
    longitude_deg_e: float
    target_range_km: float
    primary_cross_track_mismatch_km: float = 0.0
    auxiliary_cross_track_mismatch_km: float | None = None
    auxiliary_direct_range_km: float | None = None
    auxiliary_direct_bearing_deg: float | None = None


@dataclass(frozen=True)
class RouteJob:
    key: RouteJobKey
    time_utc: str
    frequency_mhz: float
    origin_latitude_deg: float
    origin_longitude_deg_e: float
    initial_bearing_deg: float
    geometry_model: str
    targets: tuple[RouteTarget, ...]


@dataclass(frozen=True)
class RoutePlan:
    jobs: tuple[RouteJob, ...]
    pairs: tuple[CandidatePair, ...]
    leg_jobs: Mapping[tuple[str, int, str], RouteJobKey]


@dataclass(frozen=True)
class ModeMatch:
    minimum_error_km: float
    mode: Mapping[str, object]


@dataclass(frozen=True)
class TargetPropagationResult:
    job_key: RouteJobKey
    candidate_id: str
    epoch_id: str
    surface_endpoint: ModeMatch | None
    aircraft_altitudes: Mapping[float, ModeMatch]


@dataclass(frozen=True)
class ScreenedPair:
    pair: CandidatePair
    screen: str
    altitude_km: float | None
    leg_matches: Mapping[tuple[int, str], ModeMatch]


@dataclass(frozen=True)
class SpatialCluster:
    screen: str
    epoch_id: str
    condition: str
    physical_slot: str
    altitude_km: float | None
    feasible_altitudes_km: tuple[float, ...]
    cluster_rank: int
    latitude_deg: float
    longitude_deg_e: float
    pair_intersections: int
    support_links: int
    independent_links: int
    support_spot_ids: tuple[int, ...]
    center_candidate_id: str
    source_altitude_clusters: int = 0
    source_altitude_cluster_ids: tuple[str, ...] = ()

    @property
    def altitude_minimum_km(self) -> float | None:
        return min(self.feasible_altitudes_km) if self.feasible_altitudes_km else None

    @property
    def altitude_maximum_km(self) -> float | None:
        return max(self.feasible_altitudes_km) if self.feasible_altitudes_km else None


@dataclass(frozen=True)
class ResidualCluster:
    cluster: SpatialCluster
    nearest_other_condition_km: float
    is_residual: bool


@dataclass(frozen=True)
class TruthReference:
    """Known position used only after blind selection and clustering."""

    truth_id: str
    epoch_id: str
    condition: str
    latitude_deg: float
    longitude_deg_e: float
    physical_slot: str | None = None
    screen: str | None = None
    altitude_km: float | None = None


@dataclass(frozen=True)
class TruthScore:
    truth_id: str
    epoch_id: str
    eligible_clusters: int
    nearest_distance_km: float
    nearest_altitude_gap_km: float | None
    minimum_altitude_gap_km: float | None
    clusters_within_tolerance: int
    recovered: bool
    nearest_independent_links: int | None
    nearest_support_rank: int | None
    nearest_cluster: SpatialCluster | None


def _open_csv(path: Path):
    return gzip.open(path, "rt", newline="") if path.suffix == ".gz" else path.open("r", newline="")


def _optional_float(value: str | None) -> float | None:
    return None if value is None or value == "" else float(value)


def read_candidate_pairs(path: Path, dataset_name: str) -> tuple[CandidatePair, ...]:
    """Read a frozen candidate table without modifying or regenerating it."""
    rows: list[CandidatePair] = []
    with _open_csv(path) as handle:
        reader = csv.DictReader(handle)
        required = {
            "condition", "physical_slot", "radio_time", "spot_id_1", "spot_id_2",
            "tx_1", "rx_1", "tx_2", "rx_2", "lat_deg", "lon_deg_E",
        }
        missing = required.difference(reader.fieldnames or ())
        if missing:
            raise ValueError(f"candidate table missing columns: {sorted(missing)}")
        for row_number, row in enumerate(reader, 1):
            condition = row["condition"]
            if condition not in CONTROL_CONDITIONS:
                raise ValueError(f"unknown control condition: {condition}")
            epoch_id = (row.get("epoch") or dataset_name).strip()
            if not epoch_id:
                raise ValueError("candidate epoch identifier cannot be empty")
            first, second = int(row["spot_id_1"]), int(row["spot_id_2"])
            if first == second:
                raise ValueError("a candidate pair must contain two different reports")
            rows.append(CandidatePair(
                candidate_id=f"{dataset_name}:{epoch_id}:{row_number:08d}",
                epoch_id=epoch_id,
                condition=condition,
                physical_slot=row["physical_slot"],
                radio_time=row["radio_time"],
                spot_id_1=first,
                spot_id_2=second,
                transmitter_1=row["tx_1"], receiver_1=row["rx_1"],
                transmitter_2=row["tx_2"], receiver_2=row["rx_2"],
                latitude_deg=float(row["lat_deg"]),
                longitude_deg_e=float(row["lon_deg_E"]),
                crossing_angle_deg=_optional_float(row.get("crossing_angle_deg")),
                distance_to_arc_km=_optional_float(row.get("distance_to_arc_km")),
                arc_side=row.get("arc_side") or None,
                source_fields=dict(row),
            ))
    return tuple(rows)


def read_spot_records(path: Path) -> dict[int, SpotRecord]:
    """Read the frozen WSPR archive extract needed by the route worker."""
    records: dict[int, SpotRecord] = {}
    with _open_csv(path) as handle:
        reader = csv.DictReader(handle)
        required = {
            "id", "time", "frequency", "tx_sign", "rx_sign", "tx_loc", "rx_loc",
            "tx_lat", "tx_lon", "rx_lat", "rx_lon",
        }
        missing = required.difference(reader.fieldnames or ())
        if missing:
            raise ValueError(f"spot table missing columns: {sorted(missing)}")
        for row in reader:
            record = SpotRecord(
                spot_id=int(row["id"]), time_utc=row["time"],
                frequency_hz=float(row["frequency"]),
                transmitter=row["tx_sign"], receiver=row["rx_sign"],
                transmitter_locator=row["tx_loc"].strip().upper(),
                receiver_locator=row["rx_loc"].strip().upper(),
                archive_transmitter_lat_deg=float(row["tx_lat"]),
                archive_transmitter_lon_deg_e=float(row["tx_lon"]),
                archive_receiver_lat_deg=float(row["rx_lat"]),
                archive_receiver_lon_deg_e=float(row["rx_lon"]),
            )
            if record.spot_id in records:
                raise ValueError(f"duplicate WSPR spot id: {record.spot_id}")
            records[record.spot_id] = record
    return records


def default_route_resolver() -> RouteResolver:
    """Use the paper-compatible sphere; auxiliary geometry is sensitivity only."""
    return PublishedSphericalRouteResolver()


def build_route_plan(
    pairs: Sequence[CandidatePair],
    spots: Mapping[int, SpotRecord],
    resolver: RouteResolver | None = None,
) -> RoutePlan:
    """Group candidate ranges by fixed report/endpoint/direction ray profile."""
    resolver = resolver or default_route_resolver()
    grouped: dict[RouteJobKey, dict[str, object]] = {}
    leg_jobs: dict[tuple[str, int, str], RouteJobKey] = {}
    for pair in pairs:
        for spot_id in pair.spot_ids:
            try:
                spot = spots[spot_id]
            except KeyError as error:
                raise ValueError(f"candidate references absent spot {spot_id}") from error
            if spot.time_utc != pair.radio_time:
                raise ValueError(
                    f"spot {spot_id} time {spot.time_utc} != pair radio time {pair.radio_time}"
                )
            for endpoint in ENDPOINTS:
                route = resolver.resolve(
                    spot, endpoint, pair.latitude_deg, pair.longitude_deg_e
                )
                if not (0.0 <= route.initial_bearing_deg < 360.0):
                    raise ValueError("initial bearing must be in [0, 360)")
                if route.target_range_km < 0.0:
                    raise ValueError("target range must be non-negative")
                key = RouteJobKey(spot_id, endpoint, route.branch)
                leg_key = (pair.candidate_id, spot_id, endpoint)
                if leg_key in leg_jobs:
                    raise ValueError(f"duplicate candidate leg: {leg_key}")
                leg_jobs[leg_key] = key
                target = RouteTarget(
                    pair.candidate_id, pair.epoch_id,
                    pair.latitude_deg, pair.longitude_deg_e,
                    route.target_range_km,
                    route.primary_cross_track_mismatch_km,
                    route.auxiliary_cross_track_mismatch_km,
                    route.auxiliary_direct_range_km,
                    route.auxiliary_direct_bearing_deg,
                )
                if key not in grouped:
                    grouped[key] = {
                        "spot": spot, "route": route, "targets": [target],
                    }
                else:
                    previous = grouped[key]["route"]
                    assert isinstance(previous, ResolvedRoute)
                    fixed = (
                        previous.origin_latitude_deg, previous.origin_longitude_deg_e,
                        previous.initial_bearing_deg, previous.geometry_model,
                    )
                    current = (
                        route.origin_latitude_deg, route.origin_longitude_deg_e,
                        route.initial_bearing_deg, route.geometry_model,
                    )
                    if any(
                        not math.isclose(a, b, abs_tol=1e-10) if isinstance(a, float)
                        else a != b
                        for a, b in zip(fixed, current)
                    ):
                        raise ValueError(f"resolver changed fixed geometry for job {key}")
                    targets = grouped[key]["targets"]
                    assert isinstance(targets, list)
                    targets.append(target)

    jobs: list[RouteJob] = []
    for key in sorted(grouped):
        item = grouped[key]
        spot = item["spot"]
        route = item["route"]
        targets = item["targets"]
        assert isinstance(spot, SpotRecord)
        assert isinstance(route, ResolvedRoute)
        assert isinstance(targets, list)
        jobs.append(RouteJob(
            key=key, time_utc=spot.time_utc,
            frequency_mhz=spot.frequency_hz / 1_000_000.0,
            origin_latitude_deg=route.origin_latitude_deg,
            origin_longitude_deg_e=route.origin_longitude_deg_e,
            initial_bearing_deg=route.initial_bearing_deg,
            geometry_model=route.geometry_model,
            targets=tuple(sorted(targets, key=lambda target: target.candidate_id)),
        ))
    return RoutePlan(tuple(jobs), tuple(pairs), leg_jobs)


def route_jobs_as_dicts(plan: RoutePlan) -> list[dict[str, object]]:
    """Serialize jobs using the stable worker input schema."""
    return [{
        "job_key": {
            "spot_id": job.key.spot_id,
            "endpoint": job.key.endpoint,
            "branch": job.key.branch,
        },
        "time_utc": job.time_utc,
        "frequency_mhz": job.frequency_mhz,
        "origin_latitude_deg": job.origin_latitude_deg,
        "origin_longitude_deg_e": job.origin_longitude_deg_e,
        "initial_bearing_deg": job.initial_bearing_deg,
        "geometry_model": job.geometry_model,
        "targets": [{
            "candidate_id": target.candidate_id,
            "epoch_id": target.epoch_id,
            "latitude_deg": target.latitude_deg,
            "longitude_deg_e": target.longitude_deg_e,
            "target_range_km": target.target_range_km,
            "primary_cross_track_mismatch_km": target.primary_cross_track_mismatch_km,
            "auxiliary_cross_track_mismatch_km": target.auxiliary_cross_track_mismatch_km,
            "auxiliary_direct_range_km": target.auxiliary_direct_range_km,
            "auxiliary_direct_bearing_deg": target.auxiliary_direct_bearing_deg,
        } for target in job.targets],
    } for job in plan.jobs]


def worker_job_inputs(
    plan: RoutePlan,
    aircraft_altitudes_km: Iterable[float] = tuple(value / 2.0 for value in range(1, 27)),
    range_step_km: float = 25.0,
    height_step_km: float = 3.0,
    elevation_minimum_deg: float = 0.5,
    elevation_maximum_deg: float = 89.5,
    elevation_step_deg: float = 0.5,
    elevations_deg: Iterable[float] | None = None,
    elevation_fan_provenance: str | None = None,
    maximum_hops: int = 10,
) -> list[dict[str, object]]:
    """Translate grouped plans to the worker's native JSON input schema."""
    altitudes = sorted(set(map(float, aircraft_altitudes_km)))
    if not altitudes:
        raise ValueError("at least one aircraft altitude is required")
    explicit_elevations = (
        None if elevations_deg is None else list(map(float, elevations_deg))
    )
    if explicit_elevations is not None:
        if not explicit_elevations:
            raise ValueError("an explicit elevation fan cannot be empty")
        if any(
            second <= first
            for first, second in zip(explicit_elevations, explicit_elevations[1:])
        ):
            raise ValueError("explicit elevations must be strictly increasing")
        if not elevation_fan_provenance or not elevation_fan_provenance.strip():
            raise ValueError("an explicit elevation fan requires provenance")

    if explicit_elevations is None:
        worker_elevation_fan: dict[str, object] = {
            "minimum_deg": elevation_minimum_deg,
            "maximum_deg": elevation_maximum_deg,
            "step_deg": elevation_step_deg,
        }
        reference_elevation_fan: dict[str, object] = {
            **worker_elevation_fan,
            "ray_count": int(
                math.floor(
                    (elevation_maximum_deg - elevation_minimum_deg)
                    / elevation_step_deg
                    + 1e-10
                )
            ) + 1,
            "status": (
                "assessment choice: broad deterministic uniform fan; not an "
                "inferred or aircraft-conditioned elevation"
            ),
        }
    else:
        worker_elevation_fan = {
            "elevations_deg": explicit_elevations,
            "provenance": elevation_fan_provenance,
        }
        reference_elevation_fan = {
            "definition": "explicit",
            "elevations_deg": explicit_elevations,
            "ray_count": len(explicit_elevations),
            "provenance": elevation_fan_provenance,
            "status": (
                "predeclared deterministic fan; not an inferred or "
                "aircraft-conditioned elevation"
            ),
        }

    def slot_midpoint(text: str) -> str:
        value = text.strip().replace("Z", "+00:00")
        epoch = dt.datetime.fromisoformat(value)
        if epoch.tzinfo is None:
            epoch = epoch.replace(tzinfo=dt.timezone.utc)
        else:
            epoch = epoch.astimezone(dt.timezone.utc)
        epoch += dt.timedelta(seconds=WSPR_TRANSMISSION_MIDPOINT_OFFSET_SECONDS)
        return epoch.isoformat(timespec="milliseconds").replace("+00:00", "Z")

    jobs: list[dict[str, object]] = []
    for route in plan.jobs:
        maximum_target = max(target.target_range_km for target in route.targets)
        maximum_range = min(
            math.pi * PHARLAP_EARTH_RADIUS_KM,
            math.ceil((maximum_target + 750.0) / range_step_km) * range_step_km,
        )
        jobs.append({
            "schema": WORKER_JOB_SCHEMA,
            "job_id": (
                f"spot-{route.key.spot_id}-{route.key.endpoint}-{route.key.branch}"
            ),
            "origin": {
                "latitude_deg": route.origin_latitude_deg,
                "longitude_deg": route.origin_longitude_deg_e,
            },
            "bearing_deg": route.initial_bearing_deg,
            "earth_radius_km": PHARLAP_EARTH_RADIUS_KM,
            "target_ground_ranges_km": sorted(set(
                target.target_range_km for target in route.targets
            )),
            "utc": slot_midpoint(route.time_utc),
            "frequency_mhz": route.frequency_mhz,
            "aircraft_altitudes_km": altitudes,
            "ionosphere_grid": {
                "range_step_km": range_step_km,
                "maximum_range_km": maximum_range,
                "height_start_km": 0.0,
                "height_step_km": height_step_km,
                "height_count": int(math.ceil(600.0 / height_step_km)) + 1,
                "r12": -1.0,
            },
            "elevation_fan": dict(worker_elevation_fan),
            "maximum_hops": maximum_hops,
            "solver": {
                "tolerance": 1e-7,
                "minimum_step_km": 0.01,
                "maximum_step_km": 10.0,
            },
            "runtime": {"ray_batch_size": 24, "nrt_num_threads": 1},
            "reference": {
                "route_job_key": {
                    "spot_id": route.key.spot_id,
                    "endpoint": route.key.endpoint,
                    "branch": route.key.branch,
                },
                "wspr_slot_start_utc": route.time_utc,
                "wspr_transmission_start_offset_seconds": (
                    WSPR_TRANSMISSION_START_OFFSET_SECONDS
                ),
                "wspr_transmission_duration_seconds": (
                    WSPR_TRANSMISSION_DURATION_SECONDS
                ),
                "wspr_slot_midpoint_offset_seconds": (
                    WSPR_TRANSMISSION_MIDPOINT_OFFSET_SECONDS
                ),
                "candidate_targets": [{
                    "candidate_id": target.candidate_id,
                    "epoch_id": target.epoch_id,
                    "target_ground_range_km": target.target_range_km,
                    "latitude_deg": target.latitude_deg,
                    "longitude_deg_e": target.longitude_deg_e,
                    "primary_cross_track_mismatch_km": (
                        target.primary_cross_track_mismatch_km
                    ),
                    "auxiliary_cross_track_mismatch_km": (
                        target.auxiliary_cross_track_mismatch_km
                    ),
                    "auxiliary_direct_range_km": target.auxiliary_direct_range_km,
                    "auxiliary_direct_bearing_deg": target.auxiliary_direct_bearing_deg,
                } for target in route.targets],
                "geometry_provenance": {
                    "primary": route.geometry_model,
                    "candidate_coordinates": (
                        "frozen geodetic latitude/longitude from trajectory-blind "
                        "same-slot WSPR great-circle intersections"
                    ),
                    "station_coordinates": "exact six-character Maidenhead cell centres",
                    "auxiliary_sphere_role": "explicit coordinate sensitivity only",
                },
                "elevation_fan_provenance": dict(reference_elevation_fan),
            },
        })
    return jobs


def _worker_summary_index(
    rows: object,
    include_altitude: bool,
) -> dict[tuple[float, float | None], Mapping[str, object]]:
    if not isinstance(rows, Sequence) or isinstance(rows, (str, bytes)):
        raise ValueError("worker screen must be an array")
    result: dict[tuple[float, float | None], Mapping[str, object]] = {}
    for row in rows:
        if not isinstance(row, Mapping):
            raise ValueError("worker screen row must be an object")
        target = float(row["target_ground_range_km"])
        altitude = float(row["aircraft_altitude_km"]) if include_altitude else None
        result[(target, altitude)] = row
    return result


def _find_worker_summary(
    index: Mapping[tuple[float, float | None], Mapping[str, object]],
    target_range_km: float,
    altitude_km: float | None,
) -> Mapping[str, object]:
    candidates = [
        (abs(target - target_range_km), row)
        for (target, altitude), row in index.items()
        if altitude == altitude_km
    ]
    if not candidates:
        raise ValueError("worker omitted a requested target/altitude summary")
    distance, row = min(candidates, key=lambda item: item[0])
    if distance > 1e-7:
        raise ValueError("worker target range does not match route plan")
    return row


def adapt_worker_result(
    route: RouteJob,
    worker_result: Mapping[str, object],
) -> dict[str, object]:
    """Restore candidate IDs after the range-indexed PHaRLAP worker run."""
    if worker_result.get("schema") != WORKER_RESULT_SCHEMA:
        raise ValueError("unexpected PHaRLAP worker result schema")
    worker_job = worker_result.get("job")
    if not isinstance(worker_job, Mapping):
        raise ValueError("worker result has no normalized job")
    expected_id = f"spot-{route.key.spot_id}-{route.key.endpoint}-{route.key.branch}"
    if worker_job.get("job_id") != expected_id:
        raise ValueError("worker result does not belong to route job")
    surface_index = _worker_summary_index(
        worker_result.get("surface_endpoint_screen"), False
    )
    altitude_index = _worker_summary_index(
        worker_result.get("aircraft_altitude_screen"), True
    )
    altitudes = sorted({altitude for _, altitude in altitude_index if altitude is not None})

    def match(row: Mapping[str, object]) -> dict[str, object] | None:
        error = row.get("minimum_absolute_error_km")
        topology = row.get("best_topology")
        if error is None or not isinstance(topology, Mapping):
            return None
        return {
            "minimum_error_km": float(error),
            "mode": {
                **dict(topology),
                "worker_job_id": expected_id,
                "target_ground_range_km": float(row["target_ground_range_km"]),
            },
        }

    targets = []
    for target in route.targets:
        targets.append({
            "candidate_id": target.candidate_id,
            "epoch_id": target.epoch_id,
            "surface_endpoint": match(_find_worker_summary(
                surface_index, target.target_range_km, None
            )),
            "aircraft_altitudes": [{
                "altitude_km": altitude,
                "match": match(_find_worker_summary(
                    altitude_index, target.target_range_km, altitude
                )),
            } for altitude in altitudes],
        })
    return {
        "schema": ROUTE_RESULT_SCHEMA,
        "job_key": {
            "spot_id": route.key.spot_id,
            "endpoint": route.key.endpoint,
            "branch": route.key.branch,
        },
        "targets": targets,
    }


def _mode_match(value: object) -> ModeMatch | None:
    if value is None:
        return None
    if not isinstance(value, Mapping):
        raise ValueError("mode match must be an object or null")
    error = float(value["minimum_error_km"])
    mode = value.get("mode")
    if error < 0.0 or not math.isfinite(error):
        raise ValueError("minimum error must be finite and non-negative")
    if not isinstance(mode, Mapping) or not mode:
        raise ValueError("a passing result must retain its completed-mode provenance")
    return ModeMatch(error, dict(mode))


def parse_route_results(documents: Iterable[Mapping[str, object]]) -> dict[
    tuple[RouteJobKey, str], TargetPropagationResult
]:
    """Validate worker output and index it by fixed job and candidate."""
    indexed: dict[tuple[RouteJobKey, str], TargetPropagationResult] = {}
    for document in documents:
        if document.get("schema") != ROUTE_RESULT_SCHEMA:
            raise ValueError(f"unexpected route-result schema: {document.get('schema')}")
        raw_key = document.get("job_key")
        if not isinstance(raw_key, Mapping):
            raise ValueError("route result has no job key")
        key = RouteJobKey(
            int(raw_key["spot_id"]), str(raw_key["endpoint"]), str(raw_key["branch"])
        )
        targets = document.get("targets")
        if not isinstance(targets, Sequence) or isinstance(targets, (str, bytes)):
            raise ValueError("route result targets must be an array")
        for raw_target in targets:
            if not isinstance(raw_target, Mapping):
                raise ValueError("route target result must be an object")
            candidate_id = str(raw_target["candidate_id"])
            epoch_id = str(raw_target.get("epoch_id", "")).strip()
            if not epoch_id:
                raise ValueError("route target result has no epoch identifier")
            altitude_matches: dict[float, ModeMatch] = {}
            raw_altitudes = raw_target.get("aircraft_altitudes", [])
            if not isinstance(raw_altitudes, Sequence) or isinstance(raw_altitudes, (str, bytes)):
                raise ValueError("aircraft_altitudes must be an array")
            for raw_altitude in raw_altitudes:
                if not isinstance(raw_altitude, Mapping):
                    raise ValueError("altitude match must be an object")
                altitude = float(raw_altitude["altitude_km"])
                match = _mode_match(raw_altitude.get("match"))
                if altitude in altitude_matches:
                    raise ValueError("duplicate altitude in target result")
                if match is not None:
                    altitude_matches[altitude] = match
            result = TargetPropagationResult(
                job_key=key, candidate_id=candidate_id, epoch_id=epoch_id,
                surface_endpoint=_mode_match(raw_target.get("surface_endpoint")),
                aircraft_altitudes=altitude_matches,
            )
            index_key = key, candidate_id
            if index_key in indexed:
                raise ValueError(f"duplicate route target result: {index_key}")
            indexed[index_key] = result
    return indexed


def validate_complete_route_results(
    plan: RoutePlan,
    results: Mapping[tuple[RouteJobKey, str], TargetPropagationResult],
) -> None:
    """Reject missing, extra or cross-epoch route targets before screening."""
    expected = {
        (route.key, target.candidate_id): target.epoch_id
        for route in plan.jobs
        for target in route.targets
    }
    if set(results) != set(expected):
        missing = len(set(expected).difference(results))
        extra = len(set(results).difference(expected))
        raise ValueError(
            f"route-result set is incomplete or foreign: {missing} missing, {extra} extra"
        )
    for key, epoch_id in expected.items():
        if results[key].epoch_id != epoch_id:
            raise ValueError(f"route result {key} has the wrong epoch")


def _four_leg_results(
    plan: RoutePlan,
    pair: CandidatePair,
    results: Mapping[tuple[RouteJobKey, str], TargetPropagationResult],
) -> dict[tuple[int, str], TargetPropagationResult]:
    legs: dict[tuple[int, str], TargetPropagationResult] = {}
    for spot_id in pair.spot_ids:
        for endpoint in ENDPOINTS:
            key = plan.leg_jobs[(pair.candidate_id, spot_id, endpoint)]
            result = results.get((key, pair.candidate_id))
            if result is None:
                raise ValueError(
                    f"incomplete propagation results for candidate leg "
                    f"{pair.candidate_id}/{spot_id}/{endpoint}"
                )
            if result.epoch_id != pair.epoch_id:
                raise ValueError("route result epoch does not match candidate epoch")
            legs[(spot_id, endpoint)] = result
    return legs


def apply_surface_endpoint_screen(
    plan: RoutePlan,
    results: Mapping[tuple[RouteJobKey, str], TargetPropagationResult],
    tolerance_km: float,
) -> tuple[ScreenedPair, ...]:
    """Apply the published-role landing test, independently of altitude hits."""
    if tolerance_km < 0.0:
        raise ValueError("tolerance must be non-negative")
    accepted: list[ScreenedPair] = []
    for pair in plan.pairs:
        legs = _four_leg_results(plan, pair, results)
        matches = {
            leg: result.surface_endpoint
            for leg, result in legs.items()
            if result.surface_endpoint is not None
            and result.surface_endpoint.minimum_error_km <= tolerance_km
        }
        if len(matches) == 4:
            accepted.append(ScreenedPair(
                pair, SURFACE_SCREEN, None,
                {leg: match for leg, match in matches.items() if match is not None},
            ))
    return tuple(accepted)


def apply_common_altitude_screen(
    plan: RoutePlan,
    results: Mapping[tuple[RouteJobKey, str], TargetPropagationResult],
    tolerance_km: float,
    altitudes_km: Iterable[float] | None = None,
) -> tuple[ScreenedPair, ...]:
    """Require four ray-path hits at one common aircraft altitude."""
    if tolerance_km < 0.0:
        raise ValueError("tolerance must be non-negative")
    declared = None if altitudes_km is None else tuple(sorted(set(map(float, altitudes_km))))
    accepted: list[ScreenedPair] = []
    for pair in plan.pairs:
        legs = _four_leg_results(plan, pair, results)
        common = set.intersection(*(
            set(result.aircraft_altitudes) for result in legs.values()
        ))
        if declared is not None:
            common.intersection_update(declared)
        for altitude in sorted(common):
            matches = {
                leg: result.aircraft_altitudes[altitude]
                for leg, result in legs.items()
                if result.aircraft_altitudes[altitude].minimum_error_km <= tolerance_km
            }
            if len(matches) == 4:
                accepted.append(ScreenedPair(
                    pair, ALTITUDE_SCREEN, altitude, matches
                ))
    return tuple(accepted)


def maximum_independent_links(
    spot_ids: Iterable[int], metadata: Mapping[int, tuple[str, str]]
) -> int:
    """Maximum links sharing neither a transmitter nor a receiver."""
    adjacency: dict[str, set[str]] = defaultdict(set)
    for spot_id in set(spot_ids):
        transmitter, receiver = metadata[spot_id]
        adjacency[transmitter].add(receiver)
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


def great_circle_distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Mean-sphere distance used only for cluster and truth proximity."""
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = phi2 - phi1
    dlon = math.radians(lon2 - lon1)
    value = (
        math.sin(dphi / 2.0) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(dlon / 2.0) ** 2
    )
    return 2.0 * EARTH_MEAN_RADIUS_KM * math.asin(math.sqrt(min(1.0, max(0.0, value))))


def cluster_screened_pairs(
    screened_pairs: Sequence[ScreenedPair],
    radius_km: float = 25.0,
    minimum_independent_links: int = 3,
) -> tuple[SpatialCluster, ...]:
    """Cluster within slot and, for physical hits, within altitude slice."""
    if radius_km <= 0.0 or minimum_independent_links < 1:
        raise ValueError("invalid clustering thresholds")
    groups: dict[
        tuple[str, str, str, str, float | None], list[ScreenedPair]
    ] = defaultdict(list)
    for item in screened_pairs:
        if item.screen == ALTITUDE_SCREEN and item.altitude_km is None:
            raise ValueError("aircraft-altitude pair lost its altitude")
        groups[
            (
                item.screen,
                item.pair.epoch_id,
                item.pair.condition,
                item.pair.physical_slot,
                item.altitude_km,
            )
        ].append(item)

    all_clusters: list[SpatialCluster] = []
    for group_key in sorted(
        groups,
        key=lambda key: (
            key[0], key[1], key[2], key[3],
            -1 if key[4] is None else key[4],
        ),
    ):
        items = groups[group_key]
        if len({item.pair.epoch_id for item in items}) != 1:
            raise ValueError("a spatial cluster cannot mix candidate epochs")
        metadata: dict[int, tuple[str, str]] = {}
        for item in items:
            for spot_id, calls in item.pair.link_metadata().items():
                if spot_id in metadata and metadata[spot_id] != calls:
                    raise ValueError(f"inconsistent station metadata for spot {spot_id}")
                metadata[spot_id] = calls
        distances = [[0.0] * len(items) for _ in items]
        for first in range(len(items)):
            a = items[first].pair
            for second in range(first + 1, len(items)):
                b = items[second].pair
                distance = great_circle_distance_km(
                    a.latitude_deg, a.longitude_deg_e,
                    b.latitude_deg, b.longitude_deg_e,
                )
                distances[first][second] = distances[second][first] = distance
        proposals: list[dict[str, object]] = []
        for center in range(len(items)):
            neighbors = [index for index, distance in enumerate(distances[center]) if distance <= radius_km]
            spot_ids = sorted({
                spot_id for index in neighbors for spot_id in items[index].pair.spot_ids
            })
            proposals.append({
                "center": center,
                "neighbors": len(neighbors),
                "spot_ids": spot_ids,
                "independent": maximum_independent_links(spot_ids, metadata),
            })
        proposals.sort(key=lambda proposal: (
            -int(proposal["independent"]),
            -len(proposal["spot_ids"]),
            -int(proposal["neighbors"]),
            items[int(proposal["center"])].pair.candidate_id,
        ))
        selected: list[dict[str, object]] = []
        for proposal in proposals:
            center = int(proposal["center"])
            if any(distances[center][int(prior["center"])] <= radius_km for prior in selected):
                continue
            selected.append(proposal)
        strict = [proposal for proposal in selected if int(proposal["independent"]) >= minimum_independent_links]
        screen, epoch_id, condition, physical_slot, altitude = group_key
        for rank, proposal in enumerate(strict, 1):
            center_pair = items[int(proposal["center"])].pair
            spot_ids = tuple(int(value) for value in proposal["spot_ids"])
            all_clusters.append(SpatialCluster(
                screen=screen, epoch_id=epoch_id, condition=condition,
                physical_slot=physical_slot, altitude_km=altitude,
                feasible_altitudes_km=(
                    () if altitude is None else (float(altitude),)
                ),
                cluster_rank=rank,
                latitude_deg=center_pair.latitude_deg,
                longitude_deg_e=center_pair.longitude_deg_e,
                pair_intersections=int(proposal["neighbors"]),
                support_links=len(spot_ids),
                independent_links=int(proposal["independent"]),
                support_spot_ids=spot_ids,
                center_candidate_id=center_pair.candidate_id,
                source_altitude_clusters=(1 if altitude is not None else 0),
                source_altitude_cluster_ids=(
                    ()
                    if altitude is None
                    else (
                        f"{epoch_id}|{condition}|{physical_slot}|"
                        f"{float(altitude):.3f}|{rank}|{center_pair.candidate_id}",
                    )
                ),
            ))
    return tuple(all_clusters)


def collapse_altitude_clusters(
    clusters: Sequence[SpatialCluster],
    radius_km: float = 25.0,
) -> tuple[SpatialCluster, ...]:
    """Collapse co-located altitude slices into display/count events.

    Altitude is a modeled feasible-mode label, not a WSPR observation.  The
    per-altitude clustering stage remains useful because all four ray legs
    must be feasible at a common altitude, but adjacent feasible slices are
    not independent spatial detections.  Primary residualization is performed
    on those source slices first; this function is then applied separately to
    all sources for raw event counts and to surviving sources for residual
    event counts and display.  Within each epoch, panel and physical slot it
    selects the strongest remaining slice as a spatial representative and
    absorbs every remaining slice centre within ``radius`` of it.  Every
    absorbed centre is therefore directly close to the retained centre; no
    transitive single-linkage chain is used.
    """
    if radius_km <= 0.0:
        raise ValueError("altitude-collapse radius must be positive")
    surface: list[SpatialCluster] = []
    groups: dict[tuple[str, str, str], list[SpatialCluster]] = defaultdict(list)
    for cluster in clusters:
        if cluster.screen == SURFACE_SCREEN:
            if cluster.altitude_km is not None or cluster.feasible_altitudes_km:
                raise ValueError("surface cluster cannot carry aircraft altitude")
            surface.append(cluster)
            continue
        if cluster.screen != ALTITUDE_SCREEN:
            raise ValueError(f"unknown screen: {cluster.screen}")
        if cluster.altitude_km is None and not cluster.feasible_altitudes_km:
            raise ValueError("altitude cluster has no feasible altitude")
        groups[
            (cluster.epoch_id, cluster.condition, cluster.physical_slot)
        ].append(cluster)

    collapsed: list[SpatialCluster] = []
    for group_key in sorted(groups):
        remaining = list(groups[group_key])
        if len({cluster.epoch_id for cluster in remaining}) != 1:
            raise ValueError("altitude collapse cannot mix epochs")
        rank = 0
        while remaining:
            remaining.sort(key=lambda cluster: (
                -cluster.independent_links,
                -cluster.support_links,
                -cluster.pair_intersections,
                cluster.cluster_rank,
                cluster.center_candidate_id,
            ))
            representative = remaining[0]
            absorbed = [
                cluster for cluster in remaining
                if great_circle_distance_km(
                    representative.latitude_deg,
                    representative.longitude_deg_e,
                    cluster.latitude_deg,
                    cluster.longitude_deg_e,
                ) <= radius_km
            ]
            absorbed_ids = {id(cluster) for cluster in absorbed}
            remaining = [
                cluster for cluster in remaining if id(cluster) not in absorbed_ids
            ]
            feasible = sorted({
                altitude
                for cluster in absorbed
                for altitude in (
                    cluster.feasible_altitudes_km
                    if cluster.feasible_altitudes_km
                    else (() if cluster.altitude_km is None else (cluster.altitude_km,))
                )
            })
            source_ids = sorted({
                source_id
                for cluster in absorbed
                for source_id in (
                    cluster.source_altitude_cluster_ids
                    or (
                        f"{cluster.epoch_id}|{cluster.condition}|"
                        f"{cluster.physical_slot}|{cluster.altitude_km}|"
                        f"{cluster.cluster_rank}|{cluster.center_candidate_id}",
                    )
                )
            })
            rank += 1
            collapsed.append(replace(
                representative,
                altitude_km=None,
                feasible_altitudes_km=tuple(feasible),
                cluster_rank=rank,
                source_altitude_clusters=sum(
                    max(1, cluster.source_altitude_clusters)
                    for cluster in absorbed
                ),
                source_altitude_cluster_ids=tuple(source_ids),
            ))
    return tuple(sorted(
        (*surface, *collapsed),
        key=lambda cluster: (
            cluster.screen,
            cluster.epoch_id,
            cluster.condition,
            cluster.physical_slot,
            cluster.cluster_rank,
        ),
    ))


def symmetric_residuals(
    clusters: Sequence[SpatialCluster],
    tolerance_km: float = 25.0,
    match_physical_slot: bool = False,
    altitude_matching: str = "source_spatial_any_altitude",
) -> tuple[ResidualCluster, ...]:
    """Subtract persistent clusters symmetrically within each flight epoch.

    The primary altitude-screen option compares every pre-collapse source
    cluster against every source cluster in another panel while ignoring the
    modeled altitude label.  Only surviving source clusters are subsequently
    collapsed for display and event-level counts.  This order prevents a
    representative centre from hiding persistence near one of its absorbed
    members.  ``exact_altitude_sensitivity`` quantifies the old per-slice rule.
    """
    if tolerance_km < 0.0:
        raise ValueError("tolerance must be non-negative")
    if altitude_matching not in (
        "source_spatial_any_altitude", "exact_altitude_sensitivity"
    ):
        raise ValueError("unknown altitude residual-matching model")
    results: list[ResidualCluster] = []
    for source in clusters:
        if source.screen == ALTITUDE_SCREEN and source.altitude_km is None:
            raise ValueError(
                "altitude residualization requires pre-collapse source clusters"
            )
        nearest = math.inf
        for target in clusters:
            if target.condition == source.condition:
                continue
            if target.epoch_id != source.epoch_id or target.screen != source.screen:
                continue
            if (
                source.screen == ALTITUDE_SCREEN
                and altitude_matching == "exact_altitude_sensitivity"
                and target.altitude_km != source.altitude_km
            ):
                continue
            if match_physical_slot and target.physical_slot != source.physical_slot:
                continue
            nearest = min(nearest, great_circle_distance_km(
                source.latitude_deg, source.longitude_deg_e,
                target.latitude_deg, target.longitude_deg_e,
            ))
        results.append(ResidualCluster(source, nearest, nearest > tolerance_km))
    return tuple(results)


def condition_counts(items: Iterable[object]) -> dict[str, int]:
    counts = {condition: 0 for condition in CONTROL_CONDITIONS}
    for item in items:
        if isinstance(item, ResidualCluster):
            if not item.is_residual:
                continue
            condition = item.cluster.condition
        elif isinstance(item, SpatialCluster):
            condition = item.condition
        elif isinstance(item, ScreenedPair):
            condition = item.pair.condition
        elif isinstance(item, CandidatePair):
            condition = item.condition
        else:
            raise TypeError(f"unsupported count item: {type(item).__name__}")
        counts[condition] = counts.get(condition, 0) + 1
    return counts


def count_clusters_by_block(
    clusters: Iterable[SpatialCluster | ResidualCluster],
    block_unit: str = "epoch",
) -> dict[str, dict[str, int]]:
    """Count panels using independent flight epochs as the primary blocks.

    Adjacent two-minute slots share paths, stations and ionospheric state and
    are not independent replicates.  Slot blocks are therefore exposed only as
    an explicitly named sensitivity.
    """
    if block_unit not in ("epoch", "physical_slot_sensitivity"):
        raise ValueError("unknown statistical block unit")
    counts: dict[str, dict[str, int]] = defaultdict(lambda: {condition: 0 for condition in CONTROL_CONDITIONS})
    for item in clusters:
        if isinstance(item, ResidualCluster):
            if not item.is_residual:
                continue
            cluster = item.cluster
        else:
            cluster = item
        if block_unit == "epoch":
            block = f"{cluster.epoch_id}|{cluster.screen}"
        else:
            altitude_block = (
                str(cluster.altitude_km)
                if cluster.altitude_km is not None
                else "collapsed" if cluster.screen == ALTITUDE_SCREEN else "surface"
            )
            block = (
                f"{cluster.epoch_id}|{cluster.screen}|{altitude_block}|"
                f"{cluster.physical_slot}"
            )
        counts[block][cluster.condition] += 1
    return dict(counts)


def spatial_cluster_record(
    cluster: SpatialCluster,
    residual: ResidualCluster | None = None,
) -> dict[str, object]:
    """Stable publication/CSV representation shared by plots and tables."""
    if residual is not None and residual.cluster != cluster:
        raise ValueError("residual metadata belongs to another cluster")
    return {
        "screen": cluster.screen,
        "epoch_id": cluster.epoch_id,
        "condition": cluster.condition,
        "physical_slot": cluster.physical_slot,
        "altitude_km": cluster.altitude_km,
        "altitude_minimum_km": cluster.altitude_minimum_km,
        "altitude_maximum_km": cluster.altitude_maximum_km,
        "feasible_altitude_count": len(cluster.feasible_altitudes_km),
        "feasible_altitudes_km": ";".join(
            f"{value:.3f}" for value in cluster.feasible_altitudes_km
        ),
        "cluster_rank": cluster.cluster_rank,
        "latitude_deg": cluster.latitude_deg,
        "longitude_deg_e": cluster.longitude_deg_e,
        "pair_intersections": cluster.pair_intersections,
        "support_links": cluster.support_links,
        "independent_links": cluster.independent_links,
        "support_spot_ids": ";".join(map(str, cluster.support_spot_ids)),
        "center_candidate_id": cluster.center_candidate_id,
        "source_altitude_clusters": cluster.source_altitude_clusters,
        "source_altitude_cluster_ids": ";".join(
            cluster.source_altitude_cluster_ids
        ),
        "nearest_other_condition_km": (
            None if residual is None else residual.nearest_other_condition_km
        ),
        "is_residual": None if residual is None else residual.is_residual,
    }


def exact_blocked_sign_flip(
    block_counts: Mapping[str, Mapping[str, int]],
) -> dict[str, object]:
    """Exact actual-minus-control-mean sign-flip test over declared blocks."""
    differences = [
        values.get("actual_time", 0)
        - (values.get("minus_60_min", 0) + values.get("plus_60_min", 0)) / 2.0
        for _, values in sorted(block_counts.items())
    ]
    nonzero = [value for value in differences if value != 0.0]
    if len(nonzero) > 20:
        raise ValueError("exact sign-flip enumeration is limited to 20 nonzero blocks")
    observed = sum(nonzero)
    permutations = [
        sum(sign * value for sign, value in zip(signs, nonzero))
        for signs in itertools.product((-1.0, 1.0), repeat=len(nonzero))
    ] or [0.0]
    epsilon = 1e-12
    return {
        "blocks": len(differences),
        "nonzero_blocks": len(nonzero),
        "differences_actual_minus_control_mean": differences,
        "observed_sum_difference": observed,
        "one_sided_actual_excess_p": sum(value >= observed - epsilon for value in permutations) / len(permutations),
        "two_sided_p": sum(abs(value) >= abs(observed) - epsilon for value in permutations) / len(permutations),
    }


def score_truth_references(
    clusters: Sequence[SpatialCluster],
    truths: Sequence[TruthReference],
    tolerance_km: float = 25.0,
    altitude_allowance_km: float = 0.5,
    require_time_matched_truth: bool = True,
) -> tuple[TruthScore, ...]:
    """Score already-selected clusters against withheld time-matched truth.

    Surface-screen recovery is horizontal only.  Aircraft-altitude recovery
    additionally requires the known altitude to lie within
    ``altitude_allowance_km`` of at least one feasible grid altitude.  The
    nearest horizontal distance and its altitude gap remain descriptive even
    when the joint recovery rule fails.
    """
    if tolerance_km < 0.0 or altitude_allowance_km < 0.0:
        raise ValueError("truth tolerances must be non-negative")
    scores: list[TruthScore] = []
    for truth in truths:
        if require_time_matched_truth and truth.physical_slot is None:
            raise ValueError(
                "primary truth scoring requires the nearest physical WSPR slot"
            )
        eligible = [cluster for cluster in clusters
            if cluster.epoch_id == truth.epoch_id
            and cluster.condition == truth.condition
            and (truth.physical_slot is None or cluster.physical_slot == truth.physical_slot)
            and (truth.screen is None or cluster.screen == truth.screen)]
        ranked_support = sorted(
            eligible,
            key=lambda cluster: (-cluster.independent_links, -cluster.support_links, cluster.cluster_rank),
        )
        if not eligible:
            scores.append(TruthScore(
                truth.truth_id, truth.epoch_id, 0, math.inf, None, None,
                0, False, None, None, None
            ))
            continue
        distances = [great_circle_distance_km(
            truth.latitude_deg, truth.longitude_deg_e,
            cluster.latitude_deg, cluster.longitude_deg_e,
        ) for cluster in eligible]

        def altitude_gap(cluster: SpatialCluster) -> float | None:
            if cluster.screen == SURFACE_SCREEN:
                return None
            if truth.altitude_km is None:
                return math.inf
            feasible = (
                cluster.feasible_altitudes_km
                if cluster.feasible_altitudes_km
                else (() if cluster.altitude_km is None else (cluster.altitude_km,))
            )
            return (
                min(abs(value - truth.altitude_km) for value in feasible)
                if feasible else math.inf
            )

        altitude_gaps = [altitude_gap(cluster) for cluster in eligible]
        joint_passes = [
            distance <= tolerance_km
            and (gap is None or gap <= altitude_allowance_km)
            for distance, gap in zip(distances, altitude_gaps)
        ]
        nearest_index = min(range(len(eligible)), key=distances.__getitem__)
        nearest = eligible[nearest_index]
        finite_gaps = [
            gap for gap in altitude_gaps
            if gap is not None and math.isfinite(gap)
        ]
        scores.append(TruthScore(
            truth_id=truth.truth_id,
            epoch_id=truth.epoch_id,
            eligible_clusters=len(eligible),
            nearest_distance_km=distances[nearest_index],
            nearest_altitude_gap_km=altitude_gaps[nearest_index],
            minimum_altitude_gap_km=min(finite_gaps) if finite_gaps else None,
            clusters_within_tolerance=sum(joint_passes),
            recovered=any(joint_passes),
            nearest_independent_links=nearest.independent_links,
            nearest_support_rank=ranked_support.index(nearest) + 1,
            nearest_cluster=nearest,
        ))
    return tuple(scores)
