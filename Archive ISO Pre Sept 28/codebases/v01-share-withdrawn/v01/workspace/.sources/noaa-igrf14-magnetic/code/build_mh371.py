#!/usr/bin/env python3
"""Build the MH371 IGRF-14 declination grid from NOAA's frozen package."""

from __future__ import annotations

import hashlib
import importlib
import json
import struct
import sys
import tempfile
import zipfile
from datetime import datetime, timezone
from pathlib import Path

import numpy as np


SOURCE = Path(__file__).resolve().parents[1] / "data/pyIGRF14.zip"
OUTPUT = Path(__file__).resolve().parents[3] / "inputs/environment/mh371-igrf14-grid.bin"
MANIFEST = OUTPUT.with_suffix(".manifest.json")
REFERENCE_TIME = datetime(2014, 3, 7, 4, 0, tzinfo=timezone.utc)
FLIGHT_LEVELS_FT = np.asarray(
    [10_000, 15_000, 20_000, 25_000, 30_000, 35_000, 40_000, 43_000],
    dtype="float32",
)
LATITUDE_DEG = np.arange(-15.0, 60.0 + 0.25, 0.5, dtype="float32")
LONGITUDE_DEG = np.arange(75.0, 140.0 + 0.25, 0.5, dtype="float32")
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
    coefficients = package / "SHC_files/IGRF14.SHC"
    return utilities, utilities.load_shcfile(str(coefficients), None), coefficients


def coefficients_at(model, date: float) -> np.ndarray:
    right = int(np.searchsorted(model.time, date, side="right"))
    if right <= 0 or right >= len(model.time):
        raise ValueError(f"date {date} outside IGRF-14 coefficient epochs")
    left = right - 1
    fraction = (date - model.time[left]) / (model.time[right] - model.time[left])
    return (1.0 - fraction) * model.coeffs[:, left] + fraction * model.coeffs[:, right]


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
    latitudes, longitudes = np.meshgrid(LATITUDE_DEG, LONGITUDE_DEG, indexing="ij")
    with tempfile.TemporaryDirectory(prefix="igrf14-") as temporary:
        utilities, model, coefficient_path = load_official_package(Path(temporary))
        coefficients = coefficients_at(model, date)
        fields = np.stack(
            [
                declination(
                    utilities,
                    model,
                    coefficients,
                    latitudes,
                    longitudes,
                    float(altitude_ft) * 0.0003048,
                ).astype("float32")
                for altitude_ft in FLIGHT_LEVELS_FT
            ]
        )
        coefficient_sha256 = sha256(coefficient_path)

    with OUTPUT.open("wb") as stream:
        stream.write(MAGIC)
        stream.write(
            struct.pack(
                "<IIIqd",
                len(FLIGHT_LEVELS_FT),
                len(LATITUDE_DEG),
                len(LONGITUDE_DEG),
                int(REFERENCE_TIME.timestamp()),
                date,
            )
        )
        for axis in (FLIGHT_LEVELS_FT, LATITUDE_DEG, LONGITUDE_DEG):
            stream.write(np.asarray(axis, dtype="<f4").tobytes(order="C"))
        stream.write(np.asarray(fields, dtype="<f4").tobytes(order="C"))

    fixture = declination(
        utilities,
        model,
        coefficients,
        5.624829,
        99.048157,
        35_000.0 * 0.0003048,
    )
    record = {
        "schema_version": "mh371-igrf14-grid-manifest-v1",
        "status": "derived_from_official_igrf14",
        "model": "IGRF-14",
        "reference_time_utc": REFERENCE_TIME.isoformat(),
        "decimal_year": date,
        "coefficient_interpolation_epochs": [2010.0, 2015.0],
        "noaa_package_sha256": sha256(SOURCE),
        "igrf14_shc_sha256": coefficient_sha256,
        "flight_levels_ft": FLIGHT_LEVELS_FT.tolist(),
        "latitude_bounds_deg": [float(LATITUDE_DEG[0]), float(LATITUDE_DEG[-1])],
        "longitude_bounds_deg": [float(LONGITUDE_DEG[0]), float(LONGITUDE_DEG[-1])],
        "grid_step_deg": 0.5,
        "east_positive_declination": True,
        "binary_format": {
            "magic": MAGIC.decode("ascii"),
            "byte_order": "little_endian",
            "axis_order": ["flight_level", "latitude", "longitude"],
            "axis_type": "float32",
            "field_type": "float32_declination_degrees",
        },
        "radar_fixture_35000ft": {
            "latitude_deg": 5.624829,
            "longitude_deg": 99.048157,
            "declination_deg": float(fixture),
        },
        "output_path": str(OUTPUT),
        "output_sha256": sha256(OUTPUT),
        "output_bytes": OUTPUT.stat().st_size,
        "limitations": [
            "IGRF represents the large-scale core field, not local crustal anomalies.",
            "The six-hour control uses one reference epoch; secular variation is negligible.",
        ],
    }
    MANIFEST.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(record, indent=2))


if __name__ == "__main__":
    main()
