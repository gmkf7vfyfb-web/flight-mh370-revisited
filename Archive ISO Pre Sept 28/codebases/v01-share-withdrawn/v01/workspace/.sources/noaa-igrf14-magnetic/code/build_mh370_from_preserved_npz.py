#!/usr/bin/env python3
"""Compile the hash-pinned MH370 IGRF-14 NPZ into the lean runtime grid."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import struct
from pathlib import Path

import numpy as np


EXPECTED_SOURCE_SHA256 = "642d6d57c121aeaefeb45c5539a5da0613d5b91bd118228354c689b4f43e3107"
MAGIC = b"MHIGRFV1"
DOWNSAMPLE = 2


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("source_npz", type=Path)
    parser.add_argument("output_binary", type=Path)
    parser.add_argument("output_manifest", type=Path)
    args = parser.parse_args()

    source_hash = sha256(args.source_npz)
    if source_hash != EXPECTED_SOURCE_SHA256:
        raise SystemExit(f"unexpected IGRF source SHA-256: {source_hash}")

    with np.load(args.source_npz, allow_pickle=False) as source:
        reference_time = int(source["reference_time_unix_s"])
        decimal_year = float(source["decimal_year"])
        levels = np.asarray(source["flight_level_ft"], dtype="<f4")
        latitudes = np.asarray(source["latitude_deg"][::DOWNSAMPLE], dtype="<f4")
        longitudes = np.asarray(source["longitude_deg"][::DOWNSAMPLE], dtype="<f4")
        declination = np.asarray(
            source["declination_deg"][:, ::DOWNSAMPLE, ::DOWNSAMPLE], dtype="<f4"
        )

    expected_shape = (len(levels), len(latitudes), len(longitudes))
    if declination.shape != expected_shape:
        raise SystemExit("IGRF field does not match the declared axes")

    args.output_binary.parent.mkdir(parents=True, exist_ok=True)
    temporary = args.output_binary.with_suffix(args.output_binary.suffix + ".tmp")
    with temporary.open("wb") as stream:
        stream.write(MAGIC)
        stream.write(
            struct.pack(
                "<IIIqd",
                len(levels),
                len(latitudes),
                len(longitudes),
                reference_time,
                decimal_year,
            )
        )
        for axis in (levels, latitudes, longitudes):
            stream.write(axis.tobytes(order="C"))
        stream.write(declination.tobytes(order="C"))
    os.replace(temporary, args.output_binary)

    record = {
        "schema_version": "mh370-igrf14-runtime-grid-v1",
        "status": "compiled_from_hash_pinned_official_igrf14_recreation",
        "source_npz_sha256": source_hash,
        "model": "IGRF-14",
        "reference_time_unix_s": reference_time,
        "decimal_year": decimal_year,
        "flight_levels_ft": levels.tolist(),
        "latitude_bounds_deg": [float(latitudes[0]), float(latitudes[-1])],
        "longitude_bounds_deg": [float(longitudes[0]), float(longitudes[-1])],
        "grid_step_deg": 0.5,
        "east_positive_declination": True,
        "array_shape_flight_level_lat_lon": list(expected_shape),
        "output_sha256": sha256(args.output_binary),
        "output_bytes": args.output_binary.stat().st_size,
    }
    args.output_manifest.write_text(
        json.dumps(record, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
