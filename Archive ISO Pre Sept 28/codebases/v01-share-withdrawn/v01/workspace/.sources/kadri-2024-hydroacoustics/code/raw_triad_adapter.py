#!/usr/bin/env python3
"""Validate and standardise raw three-channel hydrophone CSV input.

The adapter does not detect events. It converts calibrated pascals (or counts
with an explicit scalar calibration for every channel) into deterministic NPY
arrays plus a hash receipt. Instrument response deconvolution and clock
correction must be completed before this adapter, and their identities must be
recorded in the metadata.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np


SCHEMA_ID = "mh370-raw-hydrophone-triad"
SCHEMA_VERSION = 1


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def parse_utc(value: str) -> float:
    if not value.endswith("Z"):
        raise ValueError("start_time_utc must use an explicit Z suffix")
    return datetime.fromisoformat(value.replace("Z", "+00:00")).timestamp()


def validate_metadata(metadata: dict) -> None:
    required = {
        "schema_id",
        "schema_version",
        "station_id",
        "station_position_wgs84",
        "start_time_utc",
        "sample_rate_hz",
        "pressure_unit",
        "sample_file",
        "time_offset_column",
        "channels",
        "instrument_response_id",
        "timing_correction_id",
    }
    if set(metadata) != required:
        raise ValueError(f"metadata fields differ from schema: {set(metadata) ^ required}")
    if metadata["schema_id"] != SCHEMA_ID or metadata["schema_version"] != SCHEMA_VERSION:
        raise ValueError("unsupported raw-triad schema")
    if len(metadata["channels"]) != 3:
        raise ValueError("exactly three hydrophone channels are required")
    if metadata["pressure_unit"] not in {"pascal", "instrument_counts"}:
        raise ValueError("pressure_unit must be pascal or instrument_counts")
    if float(metadata["sample_rate_hz"]) <= 0.0:
        raise ValueError("sample_rate_hz must be positive")
    parse_utc(metadata["start_time_utc"])
    latitude = float(metadata["station_position_wgs84"]["latitude_deg"])
    longitude = float(metadata["station_position_wgs84"]["longitude_deg_e"])
    if not (-90.0 <= latitude <= 90.0 and -180.0 <= longitude < 180.0):
        raise ValueError("station coordinate is not canonical WGS84 longitude/latitude")

    ids = [str(row["id"]) for row in metadata["channels"]]
    columns = [str(row["input_column"]) for row in metadata["channels"]]
    if len(set(ids)) != 3 or len(set(columns)) != 3:
        raise ValueError("channel ids and input columns must be unique")
    for channel in metadata["channels"]:
        for field in ("local_east_m", "local_north_m", "local_up_m"):
            if not np.isfinite(float(channel[field])):
                raise ValueError(f"non-finite {field}")
        calibration = channel["pascal_per_count"]
        if metadata["pressure_unit"] == "pascal" and calibration is not None:
            raise ValueError("pascal_per_count must be null for pascal input")
        if metadata["pressure_unit"] == "instrument_counts" and (
            calibration is None or not np.isfinite(float(calibration)) or float(calibration) <= 0.0
        ):
            raise ValueError("positive pascal_per_count is required for count input")


def load_csv(metadata: dict, metadata_path: Path) -> tuple[np.ndarray, np.ndarray]:
    sample_path = Path(metadata["sample_file"])
    if not sample_path.is_absolute():
        sample_path = (metadata_path.parent / sample_path).resolve()
    with sample_path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        required = {metadata["time_offset_column"]} | {
            row["input_column"] for row in metadata["channels"]
        }
        if reader.fieldnames is None or not required.issubset(reader.fieldnames):
            raise ValueError(f"sample CSV lacks required columns: {sorted(required)}")
        rows = list(reader)
    if len(rows) < 4:
        raise ValueError("sample CSV must contain at least four rows")
    time_offset = np.asarray(
        [float(row[metadata["time_offset_column"]]) for row in rows], dtype="<f8"
    )
    pressure = np.asarray(
        [
            [float(row[channel["input_column"]]) for row in rows]
            for channel in metadata["channels"]
        ],
        dtype="<f8",
    )
    if metadata["pressure_unit"] == "instrument_counts":
        pressure *= np.asarray(
            [float(channel["pascal_per_count"]) for channel in metadata["channels"]],
            dtype="<f8",
        )[:, None]
    if not np.all(np.isfinite(time_offset)) or not np.all(np.isfinite(pressure)):
        raise ValueError("raw triad contains non-finite samples")
    expected_dt = 1.0 / float(metadata["sample_rate_hz"])
    differences = np.diff(time_offset)
    tolerance = max(1.0e-9, expected_dt * 1.0e-6)
    if np.max(np.abs(differences - expected_dt)) > tolerance:
        raise ValueError("time offsets are not a complete uniform sample grid")
    if abs(time_offset[0]) > tolerance:
        raise ValueError("the first time offset must be zero")
    return time_offset, pressure


def prepare(metadata_path: Path, output: Path) -> dict:
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    validate_metadata(metadata)
    time_offset, pressure = load_csv(metadata, metadata_path)
    output.mkdir(parents=True, exist_ok=True)
    time_path = output / "time-offset-s.npy"
    pressure_path = output / "pressure-pa.npy"
    np.save(time_path, time_offset, allow_pickle=False)
    np.save(pressure_path, pressure, allow_pickle=False)
    prepared_metadata = {
        "schema_id": "mh370-prepared-hydrophone-triad",
        "schema_version": 1,
        "station_id": metadata["station_id"],
        "station_position_wgs84": metadata["station_position_wgs84"],
        "start_time_utc": metadata["start_time_utc"],
        "start_time_utc_unix_s": parse_utc(metadata["start_time_utc"]),
        "sample_rate_hz": float(metadata["sample_rate_hz"]),
        "sample_count": int(time_offset.size),
        "channel_ids": [row["id"] for row in metadata["channels"]],
        "channel_local_enu_m": [
            [row["local_east_m"], row["local_north_m"], row["local_up_m"]]
            for row in metadata["channels"]
        ],
        "instrument_response_id": metadata["instrument_response_id"],
        "timing_correction_id": metadata["timing_correction_id"],
        "pressure_unit": "pascal",
        "analysis_status": "CALIBRATED_INPUT_ADAPTER_ONLY_NO_EVENT_DETECTION_OR_LIKELIHOOD",
    }
    prepared_path = output / "metadata.json"
    prepared_path.write_text(json.dumps(prepared_metadata, indent=2) + "\n", encoding="utf-8")
    receipt = {
        "schema_id": "mh370-prepared-hydrophone-triad-receipt",
        "schema_version": 1,
        "input_metadata_sha256": sha256(metadata_path),
        "input_sample_sha256": sha256(
            (metadata_path.parent / metadata["sample_file"]).resolve()
            if not Path(metadata["sample_file"]).is_absolute()
            else Path(metadata["sample_file"])
        ),
        "outputs": {
            time_path.name: sha256(time_path),
            pressure_path.name: sha256(pressure_path),
            prepared_path.name: sha256(prepared_path),
        },
    }
    receipt_path = output / "receipt.json"
    receipt_path.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    return receipt


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("metadata", type=Path)
    parser.add_argument("output", type=Path)
    arguments = parser.parse_args()
    print(json.dumps(prepare(arguments.metadata.resolve(), arguments.output.resolve()), indent=2))


if __name__ == "__main__":
    main()
