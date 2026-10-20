#!/usr/bin/env python3
"""Independently spot-check packed MHGRID values against retrieved NetCDF."""

from __future__ import annotations

import argparse
import hashlib
import json
import struct
from datetime import timezone
from pathlib import Path

import netCDF4
import numpy as np


MAGIC = b"MHGRID1\0"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def read_header(path: Path) -> dict:
    with path.open("rb") as stream:
        if stream.read(8) != MAGIC:
            raise ValueError("invalid MHGRID magic")
        schema, time_axis, nt, ny, nx, nc = struct.unpack("<6I", stream.read(24))
        if schema not in {2, 3} or time_axis != 0 or nc != 2:
            raise ValueError("expected packed two-component Unix-time MHGRID")
        times = np.fromfile(stream, dtype="<f8", count=nt)
        latitudes = np.fromfile(stream, dtype="<f8", count=ny)
        longitudes = np.fromfile(stream, dtype="<f8", count=nx)
        count = nt * ny * nx
        components = {}
        for _ in range(nc):
            name = stream.read(16).split(b"\0", 1)[0].decode("ascii")
            encoding = struct.unpack("<I", stream.read(4))[0]
            scale, offset, missing = struct.unpack("<ddh", stream.read(18))
            persistent_land_mask = (
                struct.unpack("<h", stream.read(2))[0] if schema == 3 else None
            )
            if encoding != 1:
                raise ValueError("unexpected packed component encoding")
            data_offset = stream.tell()
            components[name] = {
                "scale": scale,
                "offset": offset,
                "missing": missing,
                "persistent_land_mask": persistent_land_mask,
                "data": np.memmap(
                    path,
                    mode="r",
                    dtype="<i2",
                    offset=data_offset,
                    shape=(nt, ny, nx),
                ),
            }
            stream.seek(count * 2, 1)
        if stream.read(1):
            raise ValueError("packed MHGRID has trailing bytes")
    return {
        "times": times,
        "latitudes": latitudes,
        "longitudes": longitudes,
        "components": components,
        "shape": [nt, ny, nx],
        "field_schema": schema,
    }


def unix_seconds(variable) -> np.ndarray:
    dates = netCDF4.num2date(
        variable[:], variable.units, only_use_cftime_datetimes=False
    )
    return np.asarray(
        [date.replace(tzinfo=timezone.utc).timestamp() for date in dates],
        dtype=np.float64,
    )


def exact_index(axis: np.ndarray, value: float, label: str) -> int:
    index = int(np.searchsorted(axis, value))
    if index >= len(axis) or not np.isclose(axis[index], value, rtol=0.0, atol=1e-7):
        raise ValueError(f"{label} coordinate absent from packed field: {value}")
    return index


def finite_values(variable) -> np.ndarray:
    values = variable[:]
    if np.ma.isMaskedArray(values):
        values = values.filled(np.nan)
    return np.asarray(values, dtype=np.float64)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--field", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--tiles", type=int, default=8)
    args = parser.parse_args()
    if args.tiles <= 0:
        parser.error("--tiles must be positive")

    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    manifest_schema = manifest.get("schema")
    if manifest_schema in {
        "mh370-native-hycom-retrieval-v1",
        "mh370-native-hycom-retrieval-v2",
    }:
        source_kind = "native_hycom_packed_i16"
        records = sorted(
            manifest["tiles"] + manifest.get("supplemental_tiles", []),
            key=lambda item: item["path"],
        )
    elif manifest_schema == "mh370-cmems-glorys12-retrieval-v1":
        source_kind = "cmems_glorys12_float"
        records = sorted(manifest["files"], key=lambda item: item["path"])
    elif manifest_schema == "mh370-cmems-waverys-retrieval-v1":
        source_kind = "cmems_waverys_float"
        records = sorted(manifest["files"], key=lambda item: item["path"])
    else:
        raise ValueError(f"unsupported retrieval manifest schema: {manifest_schema}")
    if not records:
        raise ValueError("retrieval manifest has no tiles")
    selected_count = min(args.tiles, len(records))
    selected_indices = (
        [0]
        if selected_count == 1
        else [
            round(index * (len(records) - 1) / (selected_count - 1))
            for index in range(selected_count)
        ]
    )
    selected = [records[index] for index in selected_indices]
    packed = read_header(args.field)
    checks = []
    for record in selected:
        tile_path = Path(record["path"])
        if sha256(tile_path) != record["sha256"]:
            raise ValueError(f"tile hash mismatch: {tile_path}")
        with netCDF4.Dataset(tile_path) as dataset:
            if source_kind == "native_hycom_packed_i16":
                for variable in (dataset["water_u"], dataset["water_v"]):
                    variable.set_auto_maskandscale(False)
                latitude_name = "lat"
                longitude_name = "lon"
                source_components = ("water_u", "water_v")
            elif source_kind == "cmems_glorys12_float":
                latitude_name = "latitude"
                longitude_name = "longitude"
                source_components = ("uo", "vo")
            else:
                latitude_name = "latitude"
                longitude_name = "longitude"
                source_components = ("VSDX", "VSDY")
            tile_times = unix_seconds(dataset["time"])
            latitudes = np.asarray(dataset[latitude_name][:], dtype=np.float64)
            longitudes = np.asarray(dataset[longitude_name][:], dtype=np.float64)
            for tile_time_index in sorted({0, len(tile_times) // 2, len(tile_times) - 1}):
                if source_kind == "native_hycom_packed_i16":
                    raw_u = np.asarray(
                        dataset["water_u"][tile_time_index, 0, :, :],
                        dtype=np.int16,
                    )
                    raw_v = np.asarray(
                        dataset["water_v"][tile_time_index, 0, :, :],
                        dtype=np.int16,
                    )
                    valid = np.argwhere((raw_u != -30000) & (raw_v != -30000))
                elif source_kind == "cmems_glorys12_float":
                    raw_u = finite_values(
                        dataset["uo"][tile_time_index, 0, :, :]
                    )
                    raw_v = finite_values(
                        dataset["vo"][tile_time_index, 0, :, :]
                    )
                    valid = np.argwhere(np.isfinite(raw_u) & np.isfinite(raw_v))
                else:
                    raw_u = finite_values(
                        dataset["VSDX"][tile_time_index, :, :]
                    )
                    raw_v = finite_values(
                        dataset["VSDY"][tile_time_index, :, :]
                    )
                    valid = np.argwhere(np.isfinite(raw_u) & np.isfinite(raw_v))
                if len(valid) == 0:
                    continue
                center = np.asarray(raw_u.shape, dtype=np.float64) / 2.0
                local_y, local_x = valid[
                    np.argmin(np.sum((valid - center) ** 2, axis=1))
                ]
                global_t = exact_index(
                    packed["times"], tile_times[tile_time_index], "time"
                )
                global_y = exact_index(
                    packed["latitudes"], latitudes[local_y], "latitude"
                )
                global_x = exact_index(
                    packed["longitudes"], longitudes[local_x], "longitude"
                )
                values = {}
                for raw_name, packed_name, raw in (
                    (source_components[0], "u", raw_u),
                    (source_components[1], "v", raw_v),
                ):
                    source_value = raw[local_y, local_x]
                    if source_kind == "native_hycom_packed_i16":
                        expected_packed = int(source_value)
                        source_metres_per_second = expected_packed * 0.001
                    else:
                        source_metres_per_second = float(source_value)
                        expected_packed = int(
                            np.rint(source_metres_per_second / 0.001)
                        )
                    packed_value = int(
                        packed["components"][packed_name]["data"][
                            global_t, global_y, global_x
                        ]
                    )
                    if packed_value != expected_packed:
                        raise ValueError(
                            f"{raw_name} mismatch at {tile_path.name}: "
                            f"expected={expected_packed}, packed={packed_value}"
                        )
                    values[packed_name] = {
                        "source_metres_per_second": source_metres_per_second,
                        "expected_packed_i16": expected_packed,
                        "packed_i16": packed_value,
                        "packed_metres_per_second": packed_value * 0.001,
                        "absolute_quantization_error_metres_per_second": abs(
                            source_metres_per_second - packed_value * 0.001
                        ),
                    }
                checks.append(
                    {
                        "source_file": tile_path.name,
                        "source_file_sha256": record["sha256"],
                        "unix_seconds": float(tile_times[tile_time_index]),
                        "latitude_deg": float(latitudes[local_y]),
                        "longitude_deg": float(longitudes[local_x]),
                        "values": values,
                    }
                )
    if len(checks) < len(selected):
        raise ValueError("too few finite native-field spot checks")
    payload = {
        "schema": (
            "mh370-packed-stokes-field-spot-check-v1"
            if source_kind == "cmems_waverys_float"
            else "mh370-packed-current-field-spot-check-v1"
        ),
        "source_kind": source_kind,
        "manifest": str(args.manifest),
        "manifest_sha256": sha256(args.manifest),
        "field": str(args.field),
        "field_sha256": sha256(args.field),
        "field_schema": packed["field_schema"],
        "field_shape": packed["shape"],
        "checked_values": 2 * len(checks),
        "mismatch_count": 0,
        "checks": checks,
        "method": "Standalone parser compared raw NetCDF velocity components with exact packed-field grid nodes. Native HYCOM int16 must match exactly; CMEMS current and WAVERYS float values must match independent nearest-0.001 m/s quantization. Schema 3 distinguishes persistent-land masking from intermittent missing data with separate sentinels; finite values are unchanged. Rust unit tests independently check scale and both missing semantics.",
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
