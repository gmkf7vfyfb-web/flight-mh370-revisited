#!/usr/bin/env python3
"""Build the global, seam-closed MH370 IGRF-14 runtime grid."""

from __future__ import annotations

import hashlib
import importlib
import json
import os
import struct
import sys
import tempfile
import zipfile
from datetime import datetime, timezone
from pathlib import Path

import numpy as np


REPOSITORY = Path(__file__).resolve().parents[3]
SOURCE = Path(__file__).resolve().parents[1] / "data/pyIGRF14.zip"
OUTPUT = REPOSITORY / "inputs/environment/mh370-igrf14-grid.bin"
MANIFEST = OUTPUT.with_suffix(".manifest.json")
REFERENCE_TIME = datetime(2014, 3, 8, 0, 0, tzinfo=timezone.utc)
PRESSURE_ALTITUDES_FT = np.asarray(
    [500, 5_000, 10_000, 15_000, 20_000, 25_000, 28_000, 31_000,
     34_000, 37_000, 40_000, 43_000],
    dtype="float32",
)
LATITUDE_DEG = np.arange(-90.0, 90.0 + 0.25, 0.5, dtype="float32")
OPEN_LONGITUDE_DEG = np.arange(-180.0, 179.5 + 0.25, 0.5, dtype="float32")
POLE_LIMIT_FOR_SYNTHESIS_DEG = 89.999999
MAGIC = b"MHIGRFV1"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def decimal_year(value: datetime) -> float:
    start = datetime(value.year, 1, 1, tzinfo=timezone.utc)
    end = datetime(value.year + 1, 1, 1, tzinfo=timezone.utc)
    return value.year + (value - start).total_seconds() / (end - start).total_seconds()


def load_official_package(extract_root: Path):
    with zipfile.ZipFile(SOURCE) as archive:
        archive.extractall(extract_root)
    package = extract_root / "pyIGRF14"
    sys.path.insert(0, str(package))
    try:
        utilities = importlib.import_module("igrf_utils")
    finally:
        sys.path.pop(0)
    coefficient_path = package / "SHC_files/IGRF14.SHC"
    return (
        utilities,
        utilities.load_shcfile(str(coefficient_path), None),
        coefficient_path,
    )


def coefficients_at(model, date: float) -> tuple[np.ndarray, tuple[float, float]]:
    right = int(np.searchsorted(model.time, date, side="right"))
    if right <= 0 or right >= len(model.time):
        raise ValueError(f"date {date} outside IGRF-14 coefficient epochs")
    left = right - 1
    fraction = (date - model.time[left]) / (model.time[right] - model.time[left])
    coefficients = (1.0 - fraction) * model.coeffs[:, left] + fraction * model.coeffs[:, right]
    return coefficients, (float(model.time[left]), float(model.time[right]))


def declination(utilities, model, coefficients, latitude, longitude, altitude_km):
    radius, colatitude, sd, cd = utilities.gg_to_geo(altitude_km, 90.0 - latitude)
    radial, theta, east = utilities.synth_values(
        coefficients.T, radius, colatitude, longitude, model.parameters["nmax"]
    )
    north = -theta
    down = -radial
    north_geodetic = north * cd + down * sd
    return np.degrees(np.arctan2(east, north_geodetic))


def main() -> None:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    date = decimal_year(REFERENCE_TIME)
    latitudes, longitudes = np.meshgrid(
        LATITUDE_DEG, OPEN_LONGITUDE_DEG, indexing="ij"
    )
    # The official helper can round its geodetic-to-geocentric cosine a few
    # ulps outside [-1, 1] at exactly +/-90 degrees for particular altitudes.
    # Declination is coordinate-singular there in any case. Store the finite
    # one-sided meridional limit at the two pole rows.
    synthesis_latitudes = np.clip(
        latitudes.astype("float64"),
        -POLE_LIMIT_FOR_SYNTHESIS_DEG,
        POLE_LIMIT_FOR_SYNTHESIS_DEG,
    )
    with tempfile.TemporaryDirectory(prefix="mh370-igrf14-") as temporary:
        utilities, model, coefficient_path = load_official_package(Path(temporary))
        coefficients, epochs = coefficients_at(model, date)
        open_fields = np.stack(
            [
                declination(
                    utilities,
                    model,
                    coefficients,
                    synthesis_latitudes,
                    longitudes,
                    float(altitude_ft) * 0.0003048,
                ).astype("float32")
                for altitude_ft in PRESSURE_ALTITUDES_FT
            ]
        )
        if not np.all(np.isfinite(open_fields)):
            raise RuntimeError("IGRF-14 grid contains a non-finite declination")
        coefficient_sha256 = sha256(coefficient_path)

    output_longitudes = np.concatenate(
        (OPEN_LONGITUDE_DEG, np.asarray([180.0], dtype="float32"))
    )
    fields = np.concatenate((open_fields, open_fields[:, :, :1]), axis=2)
    expected_shape = (
        len(PRESSURE_ALTITUDES_FT),
        len(LATITUDE_DEG),
        len(output_longitudes),
    )
    if fields.shape != expected_shape or not np.array_equal(fields[:, :, 0], fields[:, :, -1]):
        raise RuntimeError("IGRF-14 field shape or longitude seam is invalid")

    temporary_output = OUTPUT.with_suffix(".bin.tmp")
    with temporary_output.open("wb") as stream:
        stream.write(MAGIC)
        stream.write(
            struct.pack(
                "<IIIqd",
                *expected_shape,
                int(REFERENCE_TIME.timestamp()),
                date,
            )
        )
        for axis in (PRESSURE_ALTITUDES_FT, LATITUDE_DEG, output_longitudes):
            stream.write(np.asarray(axis, dtype="<f4").tobytes(order="C"))
        stream.write(np.asarray(fields, dtype="<f4").tobytes(order="C"))
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(temporary_output, OUTPUT)

    fixture = declination(
        utilities,
        model,
        coefficients,
        5.624829,
        99.048157,
        35_000.0 * 0.0003048,
    )
    record = {
        "schema_version": "mh370-igrf14-runtime-grid-v2",
        "status": "derived_from_official_igrf14_global_grid",
        "model": "IGRF-14",
        "reference_time_utc": REFERENCE_TIME.isoformat(),
        "reference_time_unix_s": int(REFERENCE_TIME.timestamp()),
        "decimal_year": date,
        "coefficient_interpolation_epochs": list(epochs),
        "noaa_package_sha256": sha256(SOURCE),
        "igrf14_shc_sha256": coefficient_sha256,
        "builder_sha256": sha256(Path(__file__)),
        "pressure_altitudes_ft": PRESSURE_ALTITUDES_FT.tolist(),
        "latitude_bounds_deg": [float(LATITUDE_DEG[0]), float(LATITUDE_DEG[-1])],
        "longitude_bounds_deg": [
            float(output_longitudes[0]),
            float(output_longitudes[-1]),
        ],
        "grid_step_deg": 0.5,
        "east_positive_declination": True,
        "pole_row_synthesis_latitude_deg": POLE_LIMIT_FOR_SYNTHESIS_DEG,
        "domain_coverage_contract": {
            "purpose": "broad repeated-manoeuvre MH370 inference from M1822 through M0011",
            "latitude": "complete WGS-84 [-90, 90] support at 0.5 degree spacing",
            "longitude": "complete WGS-84 [-180, 180) query support; +180 exactly duplicates the -180 physical meridian",
            "altitude_ft": [
                float(PRESSURE_ALTITUDES_FT[0]),
                float(PRESSURE_ALTITUDES_FT[-1]),
            ],
            "boundary_semantics": "an out-of-domain state is a data-coverage failure, not evidence against its control history",
            "quantitative_reach_proof": "recorded in the matching canonical MH370 ERA5 manifest",
        },
        "binary_format": {
            "magic": MAGIC.decode("ascii"),
            "byte_order": "little_endian",
            "axis_order": ["pressure_altitude", "latitude", "longitude"],
            "axis_direction": ["ascending", "ascending", "ascending"],
            "axis_type": "float32",
            "field_type": "float32_declination_degrees",
            "array_memory_order": "C; longitude varies fastest",
            "longitude_seam": "+180 degree column exactly duplicates -180 degrees",
        },
        "array_shape_pressure_altitude_lat_lon": list(expected_shape),
        "source_fixture_35000ft": {
            "latitude_deg": 5.624829,
            "longitude_deg": 99.048157,
            "declination_deg": float(fixture),
        },
        "output_path": str(OUTPUT.relative_to(REPOSITORY)),
        "output_sha256": sha256(OUTPUT),
        "output_bytes": OUTPUT.stat().st_size,
        "limitations": [
            "IGRF represents the large-scale core field, not local crustal anomalies.",
            "One reference epoch is used for the 6.15-hour inference; secular variation over that interval is negligible.",
            "Magnetic declination is direction-valued and undefined exactly at magnetic-field singularities; the runtime interpolates it circularly to avoid false jumps at +/-180 degrees.",
            "At the exact geographic poles, east and north are coordinate-singular even though the stored IGRF values are finite.",
            "The two exact geographic-pole rows store the finite one-sided declination limit synthesized at +/-89.999999 degrees to avoid roundoff NaNs in the official geodetic conversion helper.",
        ],
    }
    MANIFEST.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(record, indent=2))


if __name__ == "__main__":
    main()
