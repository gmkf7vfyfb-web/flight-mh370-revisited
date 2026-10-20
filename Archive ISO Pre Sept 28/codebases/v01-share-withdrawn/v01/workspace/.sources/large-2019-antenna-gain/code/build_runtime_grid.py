#!/usr/bin/env python3
"""Compile the audited first-pass antenna CSV into the lean runtime grid."""

import argparse
import csv
import gzip
import hashlib
import struct
from pathlib import Path

EXPECTED_SOURCE_SHA256 = "d60d14c6c137a1898c8e77336d7bdec5039b87b50269b1f723e676c0f92a3c15"
MAGIC = b"MH370AG1"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("source_csv", type=Path)
    parser.add_argument("output_grid", type=Path)
    arguments = parser.parse_args()

    payload = arguments.source_csv.read_bytes()
    source = gzip.decompress(payload) if arguments.source_csv.suffix == ".gz" else payload
    digest = hashlib.sha256(source).hexdigest()
    if digest != EXPECTED_SOURCE_SHA256:
        raise SystemExit(f"source SHA-256 differs: {digest}")

    rows = list(csv.DictReader(source.decode("utf-8").splitlines()))
    azimuths = sorted({float(row["aircraft_azimuth_deg"]) for row in rows})
    elevations = sorted({float(row["elevation_deg"]) for row in rows})
    if azimuths != [float(value) for value in range(-180, 181)]:
        raise SystemExit("azimuth axis is not -180..180 degrees at 1-degree spacing")
    if elevations != [0.5 * value for value in range(181)]:
        raise SystemExit("elevation axis is not 0..90 degrees at 0.5-degree spacing")

    gains = {
        (float(row["aircraft_azimuth_deg"]), float(row["elevation_deg"])): float(
            row["gain_dBic"]
        )
        for row in rows
    }
    if len(gains) != len(azimuths) * len(elevations):
        raise SystemExit("gain grid is incomplete or contains duplicate coordinates")

    output = bytearray(MAGIC)
    output.extend(struct.pack("<II", len(azimuths), len(elevations)))
    output.extend(struct.pack("<dddd", -180.0, 1.0, 0.0, 0.5))
    for elevation in elevations:
        for azimuth in azimuths:
            output.extend(struct.pack("<f", gains[(azimuth, elevation)]))

    arguments.output_grid.parent.mkdir(parents=True, exist_ok=True)
    arguments.output_grid.write_bytes(output)
    print(
        f"rows={len(gains)} bytes={len(output)} "
        f"sha256={hashlib.sha256(output).hexdigest()}"
    )


if __name__ == "__main__":
    main()
