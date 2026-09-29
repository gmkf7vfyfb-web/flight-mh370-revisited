#!/usr/bin/env python3
"""Run one controlled PHaRLAP spherical WSPR route-feasibility job.

The worker binds the independently written native IRI2020 and spherical 2-D
raytrace boundaries in this directory.  PHaRLAP itself remains an external,
controlled dependency.  One job describes one oriented great-circle branch;
several candidate ranges can therefore be scored against the same ray fan.

Two screens are returned separately:

* completed-hop surface landing distance to each target range; and
* ray crossings of each requested aircraft altitude near each target range.

Neither screen establishes that a modeled propagation mode actually occurred.
"""

from __future__ import annotations

import argparse
import bisect
import ctypes
import datetime as dt
import hashlib
import json
import math
import os
from pathlib import Path
import sys
import time
from typing import Any, Iterable, Sequence

import numpy as np


SCHEMA = "pharlap-spherical-route-job-v1"
RESULT_SCHEMA = "pharlap-spherical-route-result-v1"
EARTH_EQUATORIAL_RADIUS_KM = 6378.137
WGS84_SEMIMAJOR_KM = 6378.137
WGS84_FLATTENING = 1.0 / 298.257223563
WGS84_SEMIMINOR_KM = WGS84_SEMIMAJOR_KM * (1.0 - WGS84_FLATTENING)
IRI_PROFILE_ROWS = 15
IRI_EXTRA_VALUES = 100
MAX_GRID = 3001
MAX_POINTS = 20_000
HOP_FIELDS = 22
PATH_FIELDS = 9

HOP_FIELD_NAMES = {
    2: "ground_range_km",
    3: "group_range_km",
    4: "apogee_km",
    5: "ground_range_to_apogee_km",
    6: "hop_initial_elevation_deg",
    7: "hop_final_elevation_deg",
    8: "doppler_spread_hz",
    9: "doppler_shift_hz",
    10: "geometric_path_km",
    11: "effective_range_m",
    12: "deviative_absorption_db",
    13: "plasma_frequency_at_apogee_mhz",
    14: "fai_backscatter_coefficient_db",
    15: "virtual_height_km",
    16: "phase_path_km",
    17: "tec_electrons_m2",
    18: "total_absorption_db",
    19: "fai_altitude_km",
    20: "fai_ground_range_km",
    21: "fai_group_range_km",
}

PATH_FIELD_NAMES = {
    0: "ground_range_km",
    1: "height_km",
    2: "group_range_km",
    3: "phase_path_km",
    4: "geometric_distance_km",
    5: "electron_density_cm3",
    6: "refractive_index",
    7: "collision_frequency_hz",
    8: "cumulative_absorption_db",
}

RAY_LABELS = {
    1: "ground_return",
    0: "evanescent",
    -2: "ionosphere_penetration",
    -3: "range_grid_exhaustion",
    -4: "negative_angular_coordinate",
    -5: "path_point_limit",
    -6: "antipodal_guard",
    -100: "catastrophic_error",
}


class WorkerError(RuntimeError):
    """Input, external dependency, or native execution error."""


class IriRequest(ctypes.Structure):
    _fields_ = [
        ("latitude_deg", ctypes.c_double),
        ("longitude_deg", ctypes.c_double),
        ("year", ctypes.c_int32),
        ("month", ctypes.c_int32),
        ("day", ctypes.c_int32),
        ("hour", ctypes.c_int32),
        ("minute", ctypes.c_int32),
        ("second", ctypes.c_double),
        ("height_start_km", ctypes.c_double),
        ("height_step_km", ctypes.c_double),
        ("height_count", ctypes.c_int32),
        ("r12", ctypes.c_double),
    ]


class RaySettings(ctypes.Structure):
    _fields_ = [
        ("bearing_deg", ctypes.c_double),
        ("earth_radius_km", ctypes.c_double),
        ("hop_count", ctypes.c_int32),
        ("tolerance", ctypes.c_double),
        ("minimum_step_km", ctypes.c_double),
        ("maximum_step_km", ctypes.c_double),
    ]


def finite_or_none(value: float) -> float | None:
    value = float(value)
    return value if math.isfinite(value) else None


def require_number(value: Any, name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise WorkerError(f"{name} must be a number")
    result = float(value)
    if not math.isfinite(result):
        raise WorkerError(f"{name} must be finite")
    return result


def require_int(value: Any, name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise WorkerError(f"{name} must be an integer")
    return value


def normalize_longitude(longitude_deg: float) -> float:
    value = (longitude_deg + 180.0) % 360.0 - 180.0
    return 180.0 if value == -180.0 and longitude_deg > 0.0 else value


def parse_utc(text: str) -> dt.datetime:
    if not isinstance(text, str):
        raise WorkerError("utc must be an ISO-8601 string")
    try:
        parsed = dt.datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError as error:
        raise WorkerError(f"invalid utc timestamp: {text}") from error
    if parsed.tzinfo is None or parsed.utcoffset() != dt.timedelta(0):
        raise WorkerError("utc must include Z or an explicit +00:00 offset")
    return parsed.astimezone(dt.timezone.utc)


def wgs84_surface_radius_km(latitude_deg: float) -> float:
    """Distance from Earth's centre to the WGS84 surface at geodetic latitude."""
    latitude = math.radians(latitude_deg)
    a2 = WGS84_SEMIMAJOR_KM**2
    b2 = WGS84_SEMIMINOR_KM**2
    a2cos2 = a2 * math.cos(latitude) ** 2
    b2sin2 = b2 * math.sin(latitude) ** 2
    return math.sqrt((a2 * a2cos2 + b2 * b2sin2) / (a2cos2 + b2sin2))


def wgs84_to_geocentric_latitude_deg(
    geodetic_latitude_deg: float, height_km: float
) -> float:
    """Port of PHaRLAP's ``wgs842gc_lat`` scalar calculation."""
    latitude = math.radians(geodetic_latitude_deg)
    eccentricity_squared = 1.0 - (
        WGS84_SEMIMINOR_KM / WGS84_SEMIMAJOR_KM
    ) ** 2
    chi = math.sqrt(1.0 - eccentricity_squared * math.sin(latitude) ** 2)
    c1 = WGS84_SEMIMAJOR_KM + chi * height_km
    tangent = math.tan(latitude) * (
        c1 - WGS84_SEMIMAJOR_KM * eccentricity_squared
    ) / c1
    return math.degrees(math.atan(tangent))


def geocentric_to_wgs84_geodetic_deg(
    geocentric_latitude_deg: float, longitude_deg: float, radius_km: float
) -> tuple[float, float, float]:
    """Convert a geocentric point to WGS84 geodetic latitude/lon/height.

    Bowring's closed-form initialization is more than adequate for a point on
    the PHaRLAP auxiliary sphere and agrees with the standard iterative ECEF
    conversion to sub-millimetre height over the route fixtures.
    """
    gc_lat = math.radians(geocentric_latitude_deg)
    longitude = math.radians(longitude_deg)
    x = radius_km * math.cos(gc_lat) * math.cos(longitude)
    y = radius_km * math.cos(gc_lat) * math.sin(longitude)
    z = radius_km * math.sin(gc_lat)
    p = math.hypot(x, y)
    if p < 1e-12:
        latitude = math.copysign(math.pi / 2.0, z)
        height = abs(z) - WGS84_SEMIMINOR_KM
        return math.degrees(latitude), normalize_longitude(longitude_deg), height
    a = WGS84_SEMIMAJOR_KM
    b = WGS84_SEMIMINOR_KM
    e2 = 1.0 - (b / a) ** 2
    ep2 = (a / b) ** 2 - 1.0
    theta = math.atan2(z * a, p * b)
    latitude = math.atan2(
        z + ep2 * b * math.sin(theta) ** 3,
        p - e2 * a * math.cos(theta) ** 3,
    )
    normal = a / math.sqrt(1.0 - e2 * math.sin(latitude) ** 2)
    height = p / math.cos(latitude) - normal
    return (
        math.degrees(latitude),
        normalize_longitude(math.degrees(math.atan2(y, x))),
        height,
    )


def spherical_destination(
    latitude_deg: float,
    longitude_deg: float,
    bearing_deg: float,
    range_km: float,
    radius_km: float,
) -> tuple[float, float]:
    """Direct geodesic on a sphere, returning geocentric coordinates."""
    latitude = math.radians(latitude_deg)
    longitude = math.radians(longitude_deg)
    bearing = math.radians(bearing_deg)
    angle = range_km / radius_km
    destination_latitude = math.asin(
        math.sin(latitude) * math.cos(angle)
        + math.cos(latitude) * math.sin(angle) * math.cos(bearing)
    )
    destination_longitude = longitude + math.atan2(
        math.sin(bearing) * math.sin(angle) * math.cos(latitude),
        math.cos(angle) - math.sin(latitude) * math.sin(destination_latitude),
    )
    return (
        math.degrees(destination_latitude),
        normalize_longitude(math.degrees(destination_longitude)),
    )


def pharlap_slice_coordinate(
    origin_geodetic_latitude_deg: float,
    origin_longitude_deg: float,
    bearing_deg: float,
    range_km: float,
    radius_km: float = EARTH_EQUATORIAL_RADIUS_KM,
) -> tuple[float, float]:
    """Port the coordinate convention used by PHaRLAP ``gen_iono_grid_2d``.

    The geodetic origin is lifted to the equatorial-radius auxiliary sphere,
    converted to geocentric latitude, advanced along a spherical great circle,
    then converted from ECEF back to WGS84 geodetic coordinates for IRI.
    """
    origin_height = radius_km - wgs84_surface_radius_km(
        origin_geodetic_latitude_deg
    )
    origin_gc_latitude = wgs84_to_geocentric_latitude_deg(
        origin_geodetic_latitude_deg, origin_height
    )
    gc_latitude, gc_longitude = spherical_destination(
        origin_gc_latitude,
        origin_longitude_deg,
        bearing_deg,
        range_km,
        radius_km,
    )
    latitude, longitude, _height = geocentric_to_wgs84_geodetic_deg(
        gc_latitude, gc_longitude, radius_km
    )
    return latitude, longitude


def pharlap_spherical_inverse(
    origin_geodetic_latitude_deg: float,
    origin_longitude_deg: float,
    target_geodetic_latitude_deg: float,
    target_longitude_deg: float,
    radius_km: float = EARTH_EQUATORIAL_RADIUS_KM,
) -> tuple[float, float]:
    """Shortest auxiliary-sphere range and initial bearing between two points."""
    origin_height = radius_km - wgs84_surface_radius_km(
        origin_geodetic_latitude_deg
    )
    target_height = radius_km - wgs84_surface_radius_km(
        target_geodetic_latitude_deg
    )
    lat1 = math.radians(
        wgs84_to_geocentric_latitude_deg(
            origin_geodetic_latitude_deg, origin_height
        )
    )
    lat2 = math.radians(
        wgs84_to_geocentric_latitude_deg(
            target_geodetic_latitude_deg, target_height
        )
    )
    delta_lon = math.radians(
        normalize_longitude(target_longitude_deg - origin_longitude_deg)
    )
    y = math.sin(delta_lon) * math.cos(lat2)
    x = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(
        lat2
    ) * math.cos(delta_lon)
    central_angle = math.atan2(
        math.hypot(y, x),
        math.sin(lat1) * math.sin(lat2)
        + math.cos(lat1) * math.cos(lat2) * math.cos(delta_lon),
    )
    return radius_km * central_angle, math.degrees(math.atan2(y, x)) % 360.0


def geodetic_sphere_inverse(
    origin_latitude_deg: float,
    origin_longitude_deg: float,
    target_latitude_deg: float,
    target_longitude_deg: float,
    radius_km: float = EARTH_EQUATORIAL_RADIUS_KM,
) -> tuple[float, float]:
    """Shortest simple-sphere range/bearing using geodetic latitudes directly.

    This is distinct from :func:`pharlap_spherical_inverse`.  The published
    WSPR screenshot's 99.3427-degree bearing follows this convention, whereas
    PHaRLAP's IRI slice still uses ``pharlap_slice_coordinate`` internally.
    """
    lat1 = math.radians(origin_latitude_deg)
    lat2 = math.radians(target_latitude_deg)
    delta_lon = math.radians(
        normalize_longitude(target_longitude_deg - origin_longitude_deg)
    )
    y = math.sin(delta_lon) * math.cos(lat2)
    x = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(
        lat2
    ) * math.cos(delta_lon)
    central_angle = math.atan2(
        math.hypot(y, x),
        math.sin(lat1) * math.sin(lat2)
        + math.cos(lat1) * math.cos(lat2) * math.cos(delta_lon),
    )
    return radius_km * central_angle, math.degrees(math.atan2(y, x)) % 360.0


def inclusive_values(minimum: float, maximum: float, step: float) -> list[float]:
    if step <= 0.0 or maximum < minimum:
        raise WorkerError("fan/list step must be positive and maximum >= minimum")
    count = int(math.floor((maximum - minimum) / step + 1e-10)) + 1
    return [minimum + index * step for index in range(count)]


def production_elevations_deg(
    *, half_step: bool = False, include_worked_example: bool = False
) -> list[float]:
    """Return the predeclared broad production/sensitivity elevation fan.

    The primary grid is 0.5--15 degrees by 0.1 degree followed by
    15.5--89.5 degrees by 0.5 degree.  ``half_step`` is the separately named
    convergence sensitivity (0.05 and 0.25 degree increments).  The exact
    1.981-degree worked-example ray is opt-in, so adding it never silently
    changes a frozen primary fan.
    """
    if half_step:
        values = inclusive_values(0.5, 15.0, 0.05)
        values.extend(inclusive_values(15.25, 89.75, 0.25))
    else:
        values = inclusive_values(0.5, 15.0, 0.1)
        values.extend(inclusive_values(15.5, 89.5, 0.5))
    values = [round(value, 12) for value in values]
    if include_worked_example:
        values.append(1.981)
    return sorted(set(values))


def validate_and_normalize_job(job: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(job, dict):
        raise WorkerError("input must be a JSON object")
    if job.get("schema") != SCHEMA:
        raise WorkerError(f"schema must be {SCHEMA!r}")
    reference = job.get("reference", {})
    if not isinstance(reference, dict):
        raise WorkerError("reference must be an object when supplied")
    origin = job.get("origin")
    if not isinstance(origin, dict):
        raise WorkerError("origin must be an object")
    latitude = require_number(origin.get("latitude_deg"), "origin.latitude_deg")
    longitude = require_number(
        origin.get("longitude_deg"), "origin.longitude_deg"
    )
    if not -90.0 <= latitude <= 90.0 or not -180.0 <= longitude <= 180.0:
        raise WorkerError("origin latitude/longitude are out of range")
    radius = require_number(
        job.get("earth_radius_km", EARTH_EQUATORIAL_RADIUS_KM),
        "earth_radius_km",
    )
    if radius <= 0.0:
        raise WorkerError("earth_radius_km must be positive")
    bearing = require_number(job.get("bearing_deg"), "bearing_deg") % 360.0
    targets_value = job.get("target_ground_ranges_km")
    if not isinstance(targets_value, list) or not targets_value:
        raise WorkerError("target_ground_ranges_km must be a non-empty list")
    targets = sorted(
        {require_number(value, "target_ground_ranges_km[]") for value in targets_value}
    )
    if targets[0] < 0.0 or targets[-1] > math.pi * radius + 1e-9:
        raise WorkerError("target ranges must lie on the shortest branch [0, pi*R]")
    altitudes_value = job.get("aircraft_altitudes_km")
    if not isinstance(altitudes_value, list) or not altitudes_value:
        raise WorkerError("aircraft_altitudes_km must be a non-empty list")
    altitudes = sorted(
        {require_number(value, "aircraft_altitudes_km[]") for value in altitudes_value}
    )
    if altitudes[0] < 0.0:
        raise WorkerError("aircraft altitudes must be non-negative")
    epoch = parse_utc(job.get("utc"))
    frequency = require_number(job.get("frequency_mhz"), "frequency_mhz")
    if frequency <= 0.0:
        raise WorkerError("frequency_mhz must be positive")

    grid_input = job.get("ionosphere_grid", {})
    if not isinstance(grid_input, dict):
        raise WorkerError("ionosphere_grid must be an object")
    range_step = require_number(
        grid_input.get("range_step_km", 25.0), "ionosphere_grid.range_step_km"
    )
    maximum_range = require_number(
        grid_input.get("maximum_range_km"), "ionosphere_grid.maximum_range_km"
    )
    height_start = require_number(
        grid_input.get("height_start_km", 0.0),
        "ionosphere_grid.height_start_km",
    )
    height_step = require_number(
        grid_input.get("height_step_km", 5.0),
        "ionosphere_grid.height_step_km",
    )
    height_count = require_int(
        grid_input.get("height_count", 121), "ionosphere_grid.height_count"
    )
    r12 = require_number(grid_input.get("r12", -1.0), "ionosphere_grid.r12")
    if range_step <= 0.0 or maximum_range < targets[-1]:
        raise WorkerError("range grid must have positive step and cover every target")
    if maximum_range > math.pi * radius + 1e-9:
        raise WorkerError("maximum_range_km cannot exceed pi*earth_radius_km")
    if height_start < 0.0 or height_step <= 0.0 or not 2 <= height_count <= 1000:
        raise WorkerError("invalid height grid")
    if altitudes[-1] > height_start + height_step * (height_count - 1):
        raise WorkerError("height grid does not cover every aircraft altitude")
    if r12 != -1.0 and not 0.0 < r12 <= 200.0:
        raise WorkerError("r12 must be -1 or in (0, 200]")
    range_count = int(math.ceil(maximum_range / range_step - 1e-12)) + 1
    if range_count > MAX_GRID:
        raise WorkerError(f"range grid exceeds native limit of {MAX_GRID}")
    effective_maximum_range = (range_count - 1) * range_step

    fan_input = job.get("elevation_fan", {})
    if not isinstance(fan_input, dict):
        raise WorkerError("elevation_fan must be an object")
    explicit_elevations = fan_input.get("elevations_deg")
    if explicit_elevations is not None:
        if any(key in fan_input for key in ("minimum_deg", "maximum_deg", "step_deg")):
            raise WorkerError(
                "explicit elevation_fan.elevations_deg cannot be combined with a uniform fan"
            )
        if not isinstance(explicit_elevations, list) or not explicit_elevations:
            raise WorkerError("elevation_fan.elevations_deg must be a non-empty list")
        elevations = [
            require_number(value, "elevation_fan.elevations_deg[]")
            for value in explicit_elevations
        ]
        if any(second <= first for first, second in zip(elevations, elevations[1:])):
            raise WorkerError("explicit elevations must be strictly increasing and unique")
        provenance = fan_input.get("provenance")
        if not isinstance(provenance, str) or not provenance.strip():
            raise WorkerError("an explicit elevation fan requires non-empty provenance")
        fan_min = elevations[0]
        fan_max = elevations[-1]
        fan_step = None
        fan_definition = "explicit"
    else:
        fan_min = require_number(fan_input.get("minimum_deg", 0.5), "fan minimum")
        fan_max = require_number(fan_input.get("maximum_deg", 89.5), "fan maximum")
        fan_step = require_number(fan_input.get("step_deg", 0.5), "fan step")
        elevations = inclusive_values(fan_min, fan_max, fan_step)
        provenance = str(fan_input.get("provenance", "uniform fan declared in job"))
        fan_definition = "uniform"
    if fan_min <= 0.0 or fan_max >= 90.0:
        raise WorkerError("elevations must lie strictly between 0 and 90 degrees")

    hop_count = require_int(job.get("maximum_hops", 10), "maximum_hops")
    if not 1 <= hop_count <= 50:
        raise WorkerError("maximum_hops must lie in [1, 50]")
    solver_input = job.get("solver", {})
    if not isinstance(solver_input, dict):
        raise WorkerError("solver must be an object")
    tolerance = require_number(solver_input.get("tolerance", 1e-7), "tolerance")
    minimum_step = require_number(
        solver_input.get("minimum_step_km", 0.01), "minimum_step_km"
    )
    maximum_step = require_number(
        solver_input.get("maximum_step_km", 10.0), "maximum_step_km"
    )
    if tolerance <= 0.0 or minimum_step <= 0.0 or maximum_step < minimum_step:
        raise WorkerError("invalid solver settings")
    runtime_input = job.get("runtime", {})
    if not isinstance(runtime_input, dict):
        raise WorkerError("runtime must be an object")
    batch_size = require_int(runtime_input.get("ray_batch_size", 24), "ray_batch_size")
    threads = require_int(runtime_input.get("nrt_num_threads", 1), "nrt_num_threads")
    if not 1 <= batch_size <= 32:
        raise WorkerError("ray_batch_size must lie in [1, 32]")
    if threads < 1:
        raise WorkerError("nrt_num_threads must be positive")
    output_detail = job.get("output_detail", "minima")
    if output_detail not in ("minima", "hop_landings", "all_candidates"):
        raise WorkerError(
            "output_detail must be 'minima', 'hop_landings', or 'all_candidates'"
        )

    return {
        "schema": SCHEMA,
        "job_id": str(job.get("job_id", "")),
        "reference": reference,
        "origin": {"latitude_deg": latitude, "longitude_deg": longitude},
        "bearing_deg": bearing,
        "earth_radius_km": radius,
        "target_ground_ranges_km": targets,
        "utc": epoch,
        "frequency_mhz": frequency,
        "aircraft_altitudes_km": altitudes,
        "ionosphere_grid": {
            "range_step_km": range_step,
            "requested_maximum_range_km": maximum_range,
            "effective_maximum_range_km": effective_maximum_range,
            "range_count": range_count,
            "height_start_km": height_start,
            "height_step_km": height_step,
            "height_count": height_count,
            "r12": r12,
        },
        "elevation_fan": {
            "definition": fan_definition,
            "minimum_deg": fan_min,
            "maximum_deg": fan_max,
            "step_deg": fan_step,
            "provenance": provenance,
            "ray_count": len(elevations),
            "elevations_deg": elevations,
        },
        "maximum_hops": hop_count,
        "solver": {
            "tolerance": tolerance,
            "minimum_step_km": minimum_step,
            "maximum_step_km": maximum_step,
        },
        "runtime": {"ray_batch_size": batch_size, "nrt_num_threads": threads},
        "output_detail": output_detail,
    }


def load_iri_library(path: Path, data_root: Path) -> ctypes.CDLL:
    if not path.is_file():
        raise WorkerError(f"IRI shared library does not exist: {path}")
    library = ctypes.CDLL(str(path))
    library.pharlap_iri2020_set_data_root.argtypes = [
        ctypes.c_char_p,
        ctypes.c_char_p,
        ctypes.c_size_t,
    ]
    library.pharlap_iri2020_set_data_root.restype = ctypes.c_int
    library.pharlap_iri2020_profiles.argtypes = [
        ctypes.POINTER(IriRequest),
        ctypes.c_size_t,
        ctypes.POINTER(ctypes.c_float),
        ctypes.c_size_t,
        ctypes.c_size_t,
        ctypes.POINTER(ctypes.c_float),
        ctypes.c_size_t,
        ctypes.c_size_t,
        ctypes.POINTER(ctypes.c_size_t),
        ctypes.c_char_p,
        ctypes.c_size_t,
    ]
    library.pharlap_iri2020_profiles.restype = ctypes.c_int
    for name in (
        "pharlap_iri2020_release",
        "pharlap_iri2020_archive_sha256",
        "pharlap_iri2020_data_manifest_sha256",
    ):
        getattr(library, name).restype = ctypes.c_char_p
    error = ctypes.create_string_buffer(1024)
    status = library.pharlap_iri2020_set_data_root(
        os.fsencode(data_root), error, len(error)
    )
    if status != 0:
        raise WorkerError(f"IRI data initialization failed: {error.value.decode()}")
    return library


def load_ray_library(path: Path) -> ctypes.CDLL:
    if not path.is_file():
        raise WorkerError(f"ray shared library does not exist: {path}")
    library = ctypes.CDLL(str(path))
    library.pharlap_raytrace_2d_sp_set_ionosphere.argtypes = [
        ctypes.c_size_t,
        ctypes.c_size_t,
        ctypes.c_double,
        ctypes.c_double,
        ctypes.c_double,
        ctypes.POINTER(ctypes.c_double),
        ctypes.c_size_t,
        ctypes.POINTER(ctypes.c_double),
        ctypes.c_size_t,
        ctypes.POINTER(ctypes.c_double),
        ctypes.c_size_t,
        ctypes.c_char_p,
        ctypes.c_size_t,
    ]
    library.pharlap_raytrace_2d_sp_set_ionosphere.restype = ctypes.c_int
    library.pharlap_raytrace_2d_sp_trace.argtypes = [
        ctypes.POINTER(RaySettings),
        ctypes.c_size_t,
        ctypes.POINTER(ctypes.c_double),
        ctypes.c_size_t,
        ctypes.POINTER(ctypes.c_double),
        ctypes.c_size_t,
        ctypes.POINTER(ctypes.c_double),
        ctypes.c_size_t,
        ctypes.POINTER(ctypes.c_int32),
        ctypes.c_size_t,
        ctypes.POINTER(ctypes.c_int32),
        ctypes.c_size_t,
        ctypes.POINTER(ctypes.c_double),
        ctypes.c_size_t,
        ctypes.POINTER(ctypes.c_int32),
        ctypes.c_size_t,
        ctypes.POINTER(ctypes.c_double),
        ctypes.c_char_p,
        ctypes.c_size_t,
    ]
    library.pharlap_raytrace_2d_sp_trace.restype = ctypes.c_int
    library.pharlap_raytrace_2d_sp_clear_ionosphere.argtypes = []
    for name in (
        "pharlap_raytrace_2d_sp_propagation_archive_sha256",
        "pharlap_raytrace_2d_sp_maths_archive_sha256",
    ):
        getattr(library, name).restype = ctypes.c_char_p
    return library


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def generate_ionosphere(
    job: dict[str, Any], iri_library: ctypes.CDLL
) -> tuple[np.ndarray, dict[str, Any]]:
    grid = job["ionosphere_grid"]
    ranges = np.arange(grid["range_count"], dtype=np.float64) * grid["range_step_km"]
    coordinates = [
        pharlap_slice_coordinate(
            job["origin"]["latitude_deg"],
            job["origin"]["longitude_deg"],
            job["bearing_deg"],
            float(range_km),
            job["earth_radius_km"],
        )
        for range_km in ranges
    ]
    epoch = job["utc"]
    request_array = (IriRequest * grid["range_count"])(
        *[
            IriRequest(
                latitude,
                longitude,
                epoch.year,
                epoch.month,
                epoch.day,
                epoch.hour,
                epoch.minute,
                epoch.second + epoch.microsecond / 1_000_000.0,
                grid["height_start_km"],
                grid["height_step_km"],
                grid["height_count"],
                grid["r12"],
            )
            for latitude, longitude in coordinates
        ]
    )
    profile_stride = IRI_PROFILE_ROWS * grid["height_count"]
    profiles = np.empty(
        (grid["range_count"], IRI_PROFILE_ROWS, grid["height_count"]),
        dtype=np.float32,
    )
    extras = np.empty((grid["range_count"], IRI_EXTRA_VALUES), dtype=np.float32)
    failed = ctypes.c_size_t(0)
    error = ctypes.create_string_buffer(1024)
    status = iri_library.pharlap_iri2020_profiles(
        request_array,
        grid["range_count"],
        profiles.ctypes.data_as(ctypes.POINTER(ctypes.c_float)),
        profile_stride,
        profiles.size,
        extras.ctypes.data_as(ctypes.POINTER(ctypes.c_float)),
        IRI_EXTRA_VALUES,
        extras.size,
        ctypes.byref(failed),
        error,
        len(error),
    )
    if status != 0:
        raise WorkerError(
            f"IRI batch failed at profile {failed.value}: {error.value.decode()}"
        )
    raw_density = profiles[:, 0, :]
    unavailable = (~np.isfinite(raw_density)) | (raw_density < 0.0)
    density_cm3 = np.where(unavailable, 0.0, raw_density).astype(np.float64) * 1e-6
    coordinate_array = np.asarray(coordinates, dtype="<f8")
    sample_indices = sorted({0, len(coordinates) // 2, len(coordinates) - 1})
    metadata = {
        "coordinate_model": (
            "PHaRLAP gen_iono_grid_2d convention: WGS84 geodetic origin to "
            "equatorial-radius auxiliary sphere, spherical direct geodesic, "
            "then auxiliary-sphere ECEF to WGS84 geodetic IRI coordinates"
        ),
        "coordinate_sha256": hashlib.sha256(coordinate_array.tobytes()).hexdigest(),
        "density_cm3_sha256": hashlib.sha256(
            np.ascontiguousarray(density_cm3.astype("<f8")).tobytes()
        ).hexdigest(),
        "iri_unavailable_values_replaced_with_zero": int(unavailable.sum()),
        "coordinate_samples": [
            {
                "range_km": float(ranges[index]),
                "latitude_deg": coordinates[index][0],
                "longitude_deg": coordinates[index][1],
            }
            for index in sample_indices
        ],
        "nmf2_m3_range": [
            finite_or_none(np.nanmin(extras[:, 0])),
            finite_or_none(np.nanmax(extras[:, 0])),
        ],
        "hmf2_km_range": [
            finite_or_none(np.nanmin(extras[:, 1])),
            finite_or_none(np.nanmax(extras[:, 1])),
        ],
    }
    return np.ascontiguousarray(density_cm3), metadata


def interpolate_path_value(values: np.ndarray, index: int, fraction: float) -> float | None:
    first = float(values[index])
    second = float(values[index + 1])
    if not math.isfinite(first) or not math.isfinite(second):
        return None
    return first + fraction * (second - first)


def altitude_crossing_segments(
    ground_ranges_km: Sequence[float],
    heights_km: Sequence[float],
    altitude_km: float,
    epsilon: float = 1e-9,
) -> list[tuple[int, float, float, str]]:
    """Return every unique crossing as (segment, fraction, range, direction)."""
    if len(ground_ranges_km) != len(heights_km):
        raise ValueError("range and height arrays must have equal length")
    if len(heights_km) < 2:
        return []
    crossings: list[tuple[int, float, float, str]] = []
    for index in range(len(heights_km) - 1):
        h0 = float(heights_km[index])
        h1 = float(heights_km[index + 1])
        r0 = float(ground_ranges_km[index])
        r1 = float(ground_ranges_km[index + 1])
        if not all(math.isfinite(value) for value in (h0, h1, r0, r1)):
            continue
        d0 = h0 - altitude_km
        d1 = h1 - altitude_km
        if abs(d0) <= epsilon:
            fraction = 0.0
        elif d0 * d1 < 0.0:
            fraction = (altitude_km - h0) / (h1 - h0)
        else:
            continue
        crossing_range = r0 + fraction * (r1 - r0)
        direction = "ascending" if h1 > h0 else "descending" if h1 < h0 else "tangent"
        if crossings and abs(crossing_range - crossings[-1][2]) <= 1e-7:
            continue
        crossings.append((index, fraction, crossing_range, direction))
    last_height = float(heights_km[-1])
    last_range = float(ground_ranges_km[-1])
    if math.isfinite(last_height) and math.isfinite(last_range) and abs(
        last_height - altitude_km
    ) <= epsilon:
        if not crossings or abs(last_range - crossings[-1][2]) > 1e-7:
            direction = (
                "ascending"
                if last_height > float(heights_km[-2])
                else "descending"
                if last_height < float(heights_km[-2])
                else "tangent"
            )
            crossings.append((len(heights_km) - 2, 1.0, last_range, direction))
    return crossings


def hop_index_for_range(crossing_range_km: float, landing_ranges_km: Sequence[float]) -> int:
    """One-based hop containing a path point; landing itself closes that hop."""
    return bisect.bisect_left(list(landing_ranges_km), crossing_range_km - 1e-8) + 1


def summarize_hop(
    values: np.ndarray, label: int, ray_index: int, elevation_deg: float, hop_index: int
) -> dict[str, Any]:
    record: dict[str, Any] = {
        "ray_index": ray_index,
        "initial_elevation_deg": elevation_deg,
        "hop_index": hop_index,
        "ray_label": label,
        "ray_label_meaning": RAY_LABELS.get(label, "unknown"),
    }
    for field, name in HOP_FIELD_NAMES.items():
        record[name] = finite_or_none(values[field])
    return record


def extract_crossing_records(
    path: np.ndarray,
    altitudes_km: Sequence[float],
    landing_ranges_km: Sequence[float],
    hop_outcomes: Sequence[dict[str, Any]],
    ray_index: int,
    elevation_deg: float,
    origin: dict[str, float],
    bearing_deg: float,
    radius_km: float,
) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    ground_ranges = path[:, 0]
    heights = path[:, 1]
    hop_altitude_ordinals: dict[tuple[float, int], int] = {}
    for altitude in altitudes_km:
        segments = altitude_crossing_segments(ground_ranges, heights, altitude)
        for crossing_ordinal, (segment, fraction, crossing_range, direction) in enumerate(
            segments, start=1
        ):
            hop_index = hop_index_for_range(crossing_range, landing_ranges_km)
            key = (altitude, hop_index)
            hop_altitude_ordinals[key] = hop_altitude_ordinals.get(key, 0) + 1
            latitude, longitude = pharlap_slice_coordinate(
                origin["latitude_deg"],
                origin["longitude_deg"],
                bearing_deg,
                crossing_range,
                radius_km,
            )
            outcome = hop_outcomes[hop_index - 1] if hop_index <= len(hop_outcomes) else None
            record: dict[str, Any] = {
                "ray_index": ray_index,
                "initial_elevation_deg": elevation_deg,
                "aircraft_altitude_km": altitude,
                "crossing_ordinal": crossing_ordinal,
                "hop_crossing_ordinal": hop_altitude_ordinals[key],
                "hop_index": hop_index,
                "direction": direction,
                "path_segment_start_index": segment,
                "path_segment_fraction": fraction,
                "ground_range_km": crossing_range,
                "latitude_deg": latitude,
                "longitude_deg": longitude,
                "hop_terminal_label": outcome["ray_label"] if outcome else None,
                "hop_terminal_label_meaning": (
                    outcome["ray_label_meaning"] if outcome else None
                ),
            }
            for field, name in PATH_FIELD_NAMES.items():
                if field in (0, 1):
                    continue
                record[name] = interpolate_path_value(path[:, field], segment, fraction)
            records.append(record)
    return records


def minimum_error_summaries(
    targets_km: Sequence[float],
    records: Sequence[dict[str, Any]],
    altitudes_km: Sequence[float] | None = None,
) -> list[dict[str, Any]]:
    summaries: list[dict[str, Any]] = []
    altitude_groups: Iterable[float | None] = altitudes_km if altitudes_km is not None else [None]
    for target in targets_km:
        for altitude in altitude_groups:
            candidates = [
                record
                for record in records
                if altitude is None or record.get("aircraft_altitude_km") == altitude
            ]
            summary: dict[str, Any] = {"target_ground_range_km": target}
            if altitude is not None:
                summary["aircraft_altitude_km"] = altitude
            if not candidates:
                summary.update(
                    {
                        "candidate_count": 0,
                        "minimum_absolute_error_km": None,
                        "signed_error_km": None,
                        "best_topology": None,
                    }
                )
            else:
                best = min(
                    candidates,
                    key=lambda record: (
                        abs(record["ground_range_km"] - target),
                        record["ray_index"],
                        record["hop_index"],
                        record.get("crossing_ordinal", 0),
                    ),
                )
                signed_error = best["ground_range_km"] - target
                topology_keys = (
                    "ray_index",
                    "initial_elevation_deg",
                    "hop_index",
                    "crossing_ordinal",
                    "hop_crossing_ordinal",
                    "direction",
                    "ray_label",
                    "ray_label_meaning",
                    "hop_terminal_label",
                    "hop_terminal_label_meaning",
                    "ground_range_km",
                    "latitude_deg",
                    "longitude_deg",
                    "apogee_km",
                    "plasma_frequency_at_apogee_mhz",
                )
                summary.update(
                    {
                        "candidate_count": len(candidates),
                        "minimum_absolute_error_km": abs(signed_error),
                        "signed_error_km": signed_error,
                        "best_topology": {
                            key: best[key] for key in topology_keys if key in best
                        },
                    }
                )
            summaries.append(summary)
    return summaries


def set_ionosphere(
    library: ctypes.CDLL, job: dict[str, Any], density_cm3: np.ndarray
) -> None:
    grid = job["ionosphere_grid"]
    error = ctypes.create_string_buffer(1024)
    status = library.pharlap_raytrace_2d_sp_set_ionosphere(
        grid["range_count"],
        grid["height_count"],
        grid["height_start_km"],
        grid["height_step_km"],
        grid["range_step_km"],
        density_cm3.ctypes.data_as(ctypes.POINTER(ctypes.c_double)),
        density_cm3.size,
        None,
        0,
        None,
        0,
        error,
        len(error),
    )
    if status != 0:
        raise WorkerError(f"ray ionosphere initialization failed: {error.value.decode()}")


def trace_job(
    job: dict[str, Any], ray_library: ctypes.CDLL, density_cm3: np.ndarray
) -> dict[str, Any]:
    set_ionosphere(ray_library, job, density_cm3)
    settings = RaySettings(
        job["bearing_deg"],
        job["earth_radius_km"],
        job["maximum_hops"],
        job["solver"]["tolerance"],
        job["solver"]["minimum_step_km"],
        job["solver"]["maximum_step_km"],
    )
    elevations = job["elevation_fan"]["elevations_deg"]
    batch_size = job["runtime"]["ray_batch_size"]
    hop_outcomes: list[dict[str, Any]] = []
    landings: list[dict[str, Any]] = []
    crossings: list[dict[str, Any]] = []
    ray_diagnostics: list[dict[str, Any]] = []
    native_elapsed = 0.0
    try:
        for batch_start in range(0, len(elevations), batch_size):
            batch_elevations = np.ascontiguousarray(
                elevations[batch_start : batch_start + batch_size], dtype=np.float64
            )
            ray_count = len(batch_elevations)
            frequencies = np.full(ray_count, job["frequency_mhz"], dtype=np.float64)
            hop_data = np.empty(
                (job["maximum_hops"], HOP_FIELDS, ray_count), dtype=np.float64
            )
            labels = np.empty((job["maximum_hops"], ray_count), dtype=np.int32)
            attempted = np.empty(ray_count, dtype=np.int32)
            path_data = np.empty((MAX_POINTS, PATH_FIELDS, ray_count), dtype=np.float64)
            point_counts = np.empty(ray_count, dtype=np.int32)
            elapsed = ctypes.c_double()
            error = ctypes.create_string_buffer(1024)
            status = ray_library.pharlap_raytrace_2d_sp_trace(
                ctypes.byref(settings),
                ray_count,
                batch_elevations.ctypes.data_as(ctypes.POINTER(ctypes.c_double)),
                ray_count,
                frequencies.ctypes.data_as(ctypes.POINTER(ctypes.c_double)),
                ray_count,
                hop_data.ctypes.data_as(ctypes.POINTER(ctypes.c_double)),
                hop_data.size,
                labels.ctypes.data_as(ctypes.POINTER(ctypes.c_int32)),
                labels.size,
                attempted.ctypes.data_as(ctypes.POINTER(ctypes.c_int32)),
                attempted.size,
                path_data.ctypes.data_as(ctypes.POINTER(ctypes.c_double)),
                path_data.size,
                point_counts.ctypes.data_as(ctypes.POINTER(ctypes.c_int32)),
                point_counts.size,
                ctypes.byref(elapsed),
                error,
                len(error),
            )
            if status != 0:
                raise WorkerError(
                    f"ray batch beginning at {batch_start} failed: {error.value.decode()}"
                )
            native_elapsed += elapsed.value
            for local_ray in range(ray_count):
                global_ray = batch_start + local_ray
                elevation = float(batch_elevations[local_ray])
                number_hops = int(attempted[local_ray])
                number_points = int(point_counts[local_ray])
                if not 0 <= number_hops <= job["maximum_hops"]:
                    raise WorkerError("native ray returned invalid hop count")
                if not 0 <= number_points <= MAX_POINTS:
                    raise WorkerError("native ray returned invalid path-point count")
                ray_hops: list[dict[str, Any]] = []
                landing_ranges: list[float] = []
                for hop_offset in range(number_hops):
                    label = int(labels[hop_offset, local_ray])
                    record = summarize_hop(
                        hop_data[hop_offset, :, local_ray],
                        label,
                        global_ray,
                        elevation,
                        hop_offset + 1,
                    )
                    ray_hops.append(record)
                    hop_outcomes.append(record)
                    if label == 1 and record["ground_range_km"] is not None:
                        landing_ranges.append(record["ground_range_km"])
                        latitude, longitude = pharlap_slice_coordinate(
                            job["origin"]["latitude_deg"],
                            job["origin"]["longitude_deg"],
                            job["bearing_deg"],
                            record["ground_range_km"],
                            job["earth_radius_km"],
                        )
                        landing = dict(record)
                        landing.update(
                            {"latitude_deg": latitude, "longitude_deg": longitude}
                        )
                        landings.append(landing)
                ray_path = path_data[:number_points, :, local_ray]
                ray_crossings = extract_crossing_records(
                    ray_path,
                    job["aircraft_altitudes_km"],
                    landing_ranges,
                    ray_hops,
                    global_ray,
                    elevation,
                    job["origin"],
                    job["bearing_deg"],
                    job["earth_radius_km"],
                )
                crossings.extend(ray_crossings)
                ray_diagnostics.append(
                    {
                        "ray_index": global_ray,
                        "initial_elevation_deg": elevation,
                        "hops_attempted": number_hops,
                        "path_point_count": number_points,
                        "completed_ground_returns": len(landing_ranges),
                        "altitude_crossing_count": len(ray_crossings),
                        "maximum_path_height_km": (
                            finite_or_none(np.nanmax(ray_path[:, 1]))
                            if number_points
                            else None
                        ),
                        "terminal_label": ray_hops[-1]["ray_label"] if ray_hops else None,
                        "terminal_label_meaning": (
                            ray_hops[-1]["ray_label_meaning"] if ray_hops else None
                        ),
                    }
                )
    finally:
        ray_library.pharlap_raytrace_2d_sp_clear_ionosphere()
    result = {
        "native_elapsed_seconds": native_elapsed,
        "ray_diagnostics": ray_diagnostics,
        "hop_outcome_count": len(hop_outcomes),
        "surface_landing_count": len(landings),
        "altitude_crossing_count": len(crossings),
        "surface_endpoint_screen": minimum_error_summaries(
            job["target_ground_ranges_km"], landings
        ),
        "aircraft_altitude_screen": minimum_error_summaries(
            job["target_ground_ranges_km"], crossings, job["aircraft_altitudes_km"]
        ),
    }
    if job["output_detail"] in ("hop_landings", "all_candidates"):
        result["hop_outcomes"] = hop_outcomes
        result["surface_landings"] = landings
    if job["output_detail"] == "all_candidates":
        result["altitude_crossings"] = crossings
    return result


def public_job(job: dict[str, Any]) -> dict[str, Any]:
    result = dict(job)
    result["utc"] = job["utc"].isoformat().replace("+00:00", "Z")
    return result


def run_job(
    raw_job: dict[str, Any], pharlap_home: Path, iri_path: Path, ray_path: Path
) -> dict[str, Any]:
    job = validate_and_normalize_job(raw_job)
    pharlap_home = pharlap_home.resolve()
    data_root = pharlap_home / "dat"
    if not (data_root / "iri2020").is_dir():
        raise WorkerError(f"PHARLAP_HOME lacks dat/iri2020: {pharlap_home}")
    os.environ["PHARLAP_HOME"] = str(pharlap_home)
    os.environ["NRT_NUM_THREADS"] = str(job["runtime"]["nrt_num_threads"])
    iri_library = load_iri_library(iri_path.resolve(), data_root)
    ray_library = load_ray_library(ray_path.resolve())
    started = time.monotonic()
    ionosphere_started = time.monotonic()
    density_cm3, ionosphere_metadata = generate_ionosphere(job, iri_library)
    ionosphere_elapsed = time.monotonic() - ionosphere_started
    trace_result = trace_job(job, ray_library, density_cm3)
    result = {
        "schema": RESULT_SCHEMA,
        "job": public_job(job),
        "model": {
            "interpretation": (
                "deterministic propagation-feasibility screens; not evidence that a "
                "specific WSPR observation used any returned mode"
            ),
            "geometry": "PHaRLAP spherical 2-D, no geomagnetic O/X splitting",
            "earth_radius_primary_km": EARTH_EQUATORIAL_RADIUS_KM,
            "irregularities_enabled": False,
            "collision_frequency_model": "zero (geometry/MUF feasibility only)",
            "electron_density_5min_model": "same as observation epoch (Doppler disabled)",
            "surface_and_altitude_screens_are_parallel_not_conjunctive": True,
        },
        "units": {
            "angle": "degree",
            "distance_and_altitude": "kilometre",
            "frequency": "megahertz",
            "electron_density_iri": "electron per cubic metre",
            "electron_density_raytrace": "electron per cubic centimetre",
            "collision_frequency": "hertz",
            "time": "UTC",
        },
        "external_identity": {
            "pharlap_home": str(pharlap_home),
            "iri_library_path": str(iri_path.resolve()),
            "iri_library_sha256": sha256_file(iri_path.resolve()),
            "ray_library_path": str(ray_path.resolve()),
            "ray_library_sha256": sha256_file(ray_path.resolve()),
            "pharlap_release": iri_library.pharlap_iri2020_release().decode(),
            "iri_archive_sha256": iri_library.pharlap_iri2020_archive_sha256().decode(),
            "iri_data_manifest_sha256": (
                iri_library.pharlap_iri2020_data_manifest_sha256().decode()
            ),
            "propagation_archive_sha256": (
                ray_library.pharlap_raytrace_2d_sp_propagation_archive_sha256().decode()
            ),
            "maths_archive_sha256": (
                ray_library.pharlap_raytrace_2d_sp_maths_archive_sha256().decode()
            ),
        },
        "ionosphere": ionosphere_metadata,
        "execution": {
            "ionosphere_elapsed_seconds": ionosphere_elapsed,
            "raytrace_native_elapsed_seconds": trace_result.pop(
                "native_elapsed_seconds"
            ),
            "wall_elapsed_seconds": time.monotonic() - started,
            "ray_batches": math.ceil(
                job["elevation_fan"]["ray_count"]
                / job["runtime"]["ray_batch_size"]
            ),
        },
        **trace_result,
    }
    return result


def maidenhead_six_character_center(locator: str) -> tuple[float, float]:
    locator = locator.strip()
    if len(locator) != 6:
        raise ValueError("six-character Maidenhead locator required")
    first_lon = ord(locator[0].upper()) - ord("A")
    first_lat = ord(locator[1].upper()) - ord("A")
    square_lon = int(locator[2])
    square_lat = int(locator[3])
    sub_lon = ord(locator[4].lower()) - ord("a")
    sub_lat = ord(locator[5].lower()) - ord("a")
    longitude = -180.0 + first_lon * 20.0 + square_lon * 2.0 + sub_lon / 12.0 + 1.0 / 24.0
    latitude = -90.0 + first_lat * 10.0 + square_lat + sub_lat / 24.0 + 1.0 / 48.0
    return latitude, longitude


def published_fixture_job() -> dict[str, Any]:
    """Published G6RRL route inputs for spot 186192616.

    The screenshot declares a 12,273.9-km path and its 99.3427-degree bearing
    is the simple-geodetic-sphere bearing.  Those two numbers are *not* one
    internally consistent R=6378.137 spherical inverse: the exact locator
    centre and candidate calculate to 12,289.639 km on that sphere.  This
    fixture therefore treats the screenshot distance as an independently
    declared input and records the discrepancy.  The ray Earth radius remains
    6378.137 km; IRI sampling separately retains PHaRLAP's auxiliary transform.
    """
    origin_latitude, origin_longitude = maidenhead_six_character_center("IO90iw")
    target_latitude = -21.502
    target_longitude = 94.972
    computed_simple_sphere_range, bearing = geodetic_sphere_inverse(
        origin_latitude,
        origin_longitude,
        target_latitude,
        target_longitude,
    )
    target_range = 12_273.9
    maximum_range = min(
        math.pi * EARTH_EQUATORIAL_RADIUS_KM,
        math.ceil((target_range + 750.0) / 25.0) * 25.0,
    )
    return {
        "schema": SCHEMA,
        "job_id": "published-spot-186192616-g6rrl-to-candidate",
        "origin": {
            "latitude_deg": origin_latitude,
            "longitude_deg": origin_longitude,
        },
        "bearing_deg": bearing,
        "earth_radius_km": EARTH_EQUATORIAL_RADIUS_KM,
        "target_ground_ranges_km": [target_range],
        "reference": {
            "wspr_spot_id": 186192616,
            "transmitter": "G6RRL",
            "transmitter_maidenhead_locator": "IO90iw",
            "candidate_aircraft_latitude_deg": target_latitude,
            "candidate_aircraft_longitude_deg": target_longitude,
            "published_launch_elevation_deg": 1.981,
            "published_hop_count": 5,
            "published_approximate_apogee_km": 235.0,
            "published_declared_path_km": target_range,
            "simple_sphere_path_from_locator_center_km": (
                computed_simple_sphere_range
            ),
            "declared_minus_simple_sphere_path_km": (
                target_range - computed_simple_sphere_range
            ),
            "route_geometry": (
                "bearing calculated on the R=6378.137 geodetic-latitude sphere "
                "from IO90iw centre to the stated candidate; range independently "
                "fixed to the screenshot's 12273.9-km declaration; PHaRLAP "
                "auxiliary transform retained only for IRI slice sampling"
            ),
        },
        "utc": "2014-03-07T22:52:55Z",
        "frequency_mhz": 3.594078,
        "aircraft_altitudes_km": [value / 2.0 for value in range(1, 27)],
        "ionosphere_grid": {
            "range_step_km": 25.0,
            "maximum_range_km": maximum_range,
            "height_start_km": 0.0,
            "height_step_km": 5.0,
            "height_count": 121,
            "r12": -1.0,
        },
        "elevation_fan": {
            "minimum_deg": 0.5,
            "maximum_deg": 89.5,
            "step_deg": 0.5,
        },
        "maximum_hops": 10,
        "solver": {
            "tolerance": 1e-7,
            "minimum_step_km": 0.01,
            "maximum_step_km": 10.0,
        },
        "runtime": {"ray_batch_size": 24, "nrt_num_threads": 1},
        "output_detail": "hop_landings",
    }


def published_auxiliary_direct_fixture_job() -> dict[str, Any]:
    """Sensitivity using a direct inverse on PHaRLAP's auxiliary sphere."""
    job = published_fixture_job()
    origin = job["origin"]
    reference = dict(job["reference"])
    target_range, bearing = pharlap_spherical_inverse(
        origin["latitude_deg"],
        origin["longitude_deg"],
        reference["candidate_aircraft_latitude_deg"],
        reference["candidate_aircraft_longitude_deg"],
    )
    job["job_id"] = "published-spot-186192616-auxiliary-direct-sensitivity"
    job["bearing_deg"] = bearing
    job["target_ground_ranges_km"] = [target_range]
    maximum_range = min(
        math.pi * EARTH_EQUATORIAL_RADIUS_KM,
        math.ceil((target_range + 750.0) / 25.0) * 25.0,
    )
    job["ionosphere_grid"] = dict(job["ionosphere_grid"])
    job["ionosphere_grid"]["maximum_range_km"] = maximum_range
    reference["route_geometry"] = (
        "sensitivity: target range and bearing both use PHaRLAP auxiliary-sphere inverse"
    )
    reference["auxiliary_direct_path_km"] = target_range
    job["reference"] = reference
    return job


def read_json(path: str) -> dict[str, Any]:
    if path == "-":
        return json.load(sys.stdin)
    with Path(path).open(encoding="utf-8") as handle:
        return json.load(handle)


def write_json(path: str, value: dict[str, Any]) -> None:
    text = json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n"
    if path == "-":
        sys.stdout.write(text)
    else:
        Path(path).write_text(text, encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", default="-", help="job JSON path, or - for stdin")
    parser.add_argument("--output", default="-", help="result JSON path, or - for stdout")
    parser.add_argument(
        "--pharlap-home", required=True, type=Path, help="external PHaRLAP 4.7.4 root"
    )
    parser.add_argument(
        "--iri-library",
        required=True,
        type=Path,
        help="out-of-tree libpharlap_iri2020.so",
    )
    parser.add_argument(
        "--ray-library",
        required=True,
        type=Path,
        help="out-of-tree libpharlap_raytrace_2d_sp.so",
    )
    parser.add_argument(
        "--published-fixture",
        action="store_true",
        help="run the published spot 186192616 G6RRL-to-candidate leg",
    )
    parser.add_argument(
        "--published-auxiliary-direct-fixture",
        action="store_true",
        help="run the explicitly named auxiliary-sphere direct-route sensitivity",
    )
    parser.add_argument(
        "--emit-published-fixture",
        action="store_true",
        help="emit that fixture job JSON without loading PHaRLAP",
    )
    parser.add_argument(
        "--emit-published-auxiliary-direct-fixture",
        action="store_true",
        help="emit that auxiliary-direct sensitivity job without loading PHaRLAP",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.emit_published_fixture:
            write_json(args.output, published_fixture_job())
            return 0
        if args.emit_published_auxiliary_direct_fixture:
            write_json(args.output, published_auxiliary_direct_fixture_job())
            return 0
        if args.published_fixture and args.published_auxiliary_direct_fixture:
            raise WorkerError("select only one published fixture geometry")
        if args.published_fixture:
            raw_job = published_fixture_job()
        elif args.published_auxiliary_direct_fixture:
            raw_job = published_auxiliary_direct_fixture_job()
        else:
            raw_job = read_json(args.input)
        result = run_job(
            raw_job,
            pharlap_home=args.pharlap_home,
            iri_path=args.iri_library,
            ray_path=args.ray_library,
        )
        write_json(args.output, result)
        return 0
    except (WorkerError, OSError, json.JSONDecodeError) as error:
        print(f"pharlap_raytrace_worker: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
