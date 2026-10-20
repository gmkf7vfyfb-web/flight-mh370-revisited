#!/usr/bin/env python3
"""Convert attributed NetCDF inputs to the runner's compact MHGRID1 format.

This is input preparation, not product inference. Product crates never import it.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import struct
from datetime import datetime, timezone
from pathlib import Path

import netCDF4
import numpy as np


MAGIC = b"MHGRID1\0"

CONVERTER_VERSION = "ocean-input-preparation-v5"
PACKED_CURRENT_SCALE = 0.001
PACKED_CURRENT_MISSING = np.int16(-30000)
PACKED_PERSISTENT_LAND_MASK = np.int16(-29999)

def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def numeric(variable) -> np.ndarray:
    values = variable[:]
    if np.ma.isMaskedArray(values):
        values = values.filled(np.nan)
    return np.asarray(values)


def write_grid(
    output: Path,
    time_axis: int,
    times: np.ndarray,
    latitudes: np.ndarray,
    longitudes: np.ndarray,
    components: list[tuple[str, np.ndarray]],
    metadata: dict,
) -> None:
    times = np.asarray(times, dtype="<f8")
    latitudes = np.asarray(latitudes, dtype="<f8")
    longitudes = np.asarray(longitudes, dtype="<f8")
    shape = (len(times), len(latitudes), len(longitudes))
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("wb") as stream:
        stream.write(MAGIC)
        stream.write(struct.pack("<6I", 1, time_axis, *shape, len(components)))
        stream.write(times.tobytes(order="C"))
        stream.write(latitudes.tobytes(order="C"))
        stream.write(longitudes.tobytes(order="C"))
        for name, values in components:
            encoded = name.encode("ascii")
            if len(encoded) > 15:
                raise ValueError(f"component name too long: {name}")
            values = np.asarray(values, dtype="<f4")
            if values.shape != shape:
                raise ValueError(f"{name} has {values.shape}, expected {shape}")
            stream.write(encoded.ljust(16, b"\0"))
            stream.write(values.tobytes(order="C"))
    metadata = {
        "schema": "mh370-gridded-field-input-v1",
        "converter_version": CONVERTER_VERSION,
        "binary_format": "MHGRID1 little-endian",
        "binary_sha256": sha256(output),
        "axis_order": ["time", "latitude", "longitude"],
        "latitude_units": "degrees_north WGS84",
        "longitude_units": "degrees_east WGS84",
        **metadata,
    }
    output.with_suffix(output.suffix + ".json").write_text(
        json.dumps(metadata, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


def read_static_land_fraction(path: Path) -> dict:
    with path.open("rb") as stream:
        if stream.read(8) != MAGIC:
            raise ValueError(f"invalid MHGRID magic in {path}")
        schema, time_axis, nt, ny, nx, nc = struct.unpack("<6I", stream.read(24))
        if schema != 1 or time_axis != 0 or nt != 2 or nc != 1:
            raise ValueError(f"{path} is not a static float coastal-support field")
        times = np.fromfile(stream, dtype="<f8", count=nt)
        latitudes = np.fromfile(stream, dtype="<f8", count=ny)
        longitudes = np.fromfile(stream, dtype="<f8", count=nx)
        name = stream.read(16).split(b"\0", 1)[0].decode("ascii")
        values = np.fromfile(stream, dtype="<f4", count=nt * ny * nx).reshape(
            nt, ny, nx
        )
        if stream.read(1):
            raise ValueError(f"{path} has trailing bytes")
    if (
        name != "land_fraction"
        or not np.array_equal(values[0], values[1])
        or not np.all(np.isin(values, (0.0, 1.0)))
    ):
        raise ValueError(f"{path} is not an invariant binary land-fraction mask")
    return {
        "times": times,
        "latitudes": latitudes,
        "longitudes": longitudes,
        "land": values[0].astype(bool),
    }


def nearest_axis_indices(source: np.ndarray, targets: np.ndarray) -> np.ndarray:
    upper = np.searchsorted(source, targets).clip(0, len(source) - 1)
    lower = np.maximum(upper - 1, 0)
    choose_lower = np.abs(targets - source[lower]) <= np.abs(source[upper] - targets)
    return np.where(choose_lower, lower, upper)


def combine_cmems_coastal_support(output_directory: Path) -> None:
    glorys_path = output_directory / "cmems-glorys12-coast.mhgrid"
    waverys_path = output_directory / "cmems-waverys-coast.mhgrid"
    for path in (glorys_path, waverys_path):
        if not path.is_file() or not path.with_suffix(path.suffix + ".json").is_file():
            raise ValueError(f"combined CMEMS coastal support requires {path} and metadata")
    glorys = read_static_land_fraction(glorys_path)
    waverys = read_static_land_fraction(waverys_path)
    wave_y = nearest_axis_indices(waverys["latitudes"], glorys["latitudes"])
    wave_x = nearest_axis_indices(waverys["longitudes"], glorys["longitudes"])
    wave_land_on_glorys = waverys["land"][wave_y[:, None], wave_x[None, :]]
    union_land = glorys["land"] | wave_land_on_glorys
    first_time = max(glorys["times"][0], waverys["times"][0])
    last_time = min(glorys["times"][-1], waverys["times"][-1])
    if first_time >= last_time:
        raise ValueError("CMEMS coastal-support fields have no common time support")
    output = output_directory / "cmems-glorys12-waverys-coast.mhgrid"
    write_grid(
        output,
        0,
        np.asarray([first_time, last_time], dtype=np.float64),
        glorys["latitudes"],
        glorys["longitudes"],
        [
            (
                "land_fraction",
                np.stack([union_land, union_land], axis=0).astype(np.float32),
            )
        ],
        {
            "name": "CMEMS GLORYS12 and WAVERYS union coastal-support field",
            "family": "cmems_glorys12_reanalysis",
            "field_role": "coastal_support",
            "time_axis": "constant over the common GLORYS12/WAVERYS retrieval interval",
            "component_units": {"land_fraction": "binary fraction 0 water 1 persistent model mask"},
            "source_support_fields": [
                {
                    "path": str(glorys_path),
                    "sha256": sha256(glorys_path),
                    "metadata_sha256": sha256(
                        glorys_path.with_suffix(glorys_path.suffix + ".json")
                    ),
                },
                {
                    "path": str(waverys_path),
                    "sha256": sha256(waverys_path),
                    "metadata_sha256": sha256(
                        waverys_path.with_suffix(waverys_path.suffix + ".json")
                    ),
                },
            ],
            "definition": "union of the GLORYS12 persistent current mask and nearest-node WAVERYS persistent Stokes mask on the native GLORYS12 grid",
            "mask_counts": {
                "grid_cells": int(union_land.size),
                "glorys12_land_cells": int(np.count_nonzero(glorys["land"])),
                "waverys_land_cells_mapped_to_glorys12": int(
                    np.count_nonzero(wave_land_on_glorys)
                ),
                "union_land_cells": int(np.count_nonzero(union_land)),
                "added_by_waverys": int(
                    np.count_nonzero(wave_land_on_glorys & ~glorys["land"])
                ),
                "added_by_glorys12": int(
                    np.count_nonzero(glorys["land"] & ~wave_land_on_glorys)
                ),
            },
            "limitations": [
                "This is a conservative union of two invariant model support masks, not a measured shoreline-distance, beaching-probability, retention, or refloating model.",
                "The 0.2-degree WAVERYS mask is nearest-mapped onto the 1/12-degree GLORYS12 grid and can terminate a path before the geometric shoreline.",
                "No beaching_rate component is present, so the transport code cannot invent coastal retention.",
            ],
        },
    )


def convert_hycom(paths: list[Path], output: Path) -> None:
    times, east, north, source_files = [], [], [], []
    latitudes = longitudes = None
    for path in paths:
        with netCDF4.Dataset(path) as dataset:
            if dataset["time"].units != "seconds since 1970-01-01T00:00:00Z":
                raise ValueError(f"unexpected HYCOM time units in {path}: {dataset['time'].units}")
            expected_dimensions = ("time", "depth", "latitude", "longitude")
            if dataset["water_u"].dimensions != expected_dimensions or dataset["water_v"].dimensions != expected_dimensions:
                raise ValueError(f"unexpected HYCOM velocity dimensions in {path}")
            current_latitudes = numeric(dataset["latitude"])
            current_longitudes = numeric(dataset["longitude"])
            if latitudes is None:
                latitudes, longitudes = current_latitudes, current_longitudes
            elif not (
                np.array_equal(latitudes, current_latitudes)
                and np.array_equal(longitudes, current_longitudes)
            ):
                raise ValueError("HYCOM segment grids differ")
            times.append(numeric(dataset["time"]))
            east.append(numeric(dataset["water_u"])[:, 0, :, :])
            north.append(numeric(dataset["water_v"])[:, 0, :, :])
        source_files.append({"path": str(path), "sha256": sha256(path)})
    times = np.concatenate(times)
    east = np.concatenate(east)
    north = np.concatenate(north)
    order = np.argsort(times)
    times, east, north = times[order], east[order], north[order]
    if np.any(np.diff(times) <= 0):
        raise ValueError("HYCOM segment times overlap or repeat")
    gaps = np.diff(times) / 86400.0
    write_grid(
        output,
        0,
        times,
        latitudes,
        longitudes,
        [("u", east), ("v", north)],
        {
            "name": "HYCOM GLBu0.08 surface-current analysis, preserved regional subset",
            "family": "hycom",
            "time_axis": "UTC Unix seconds",
            "component_units": {"u": "m s-1 east", "v": "m s-1 north"},
            "source_files": source_files,
            "native_product_resolution_degrees": 0.08,
            "preserved_grid_resolution_degrees": float(np.median(np.diff(latitudes))),
            "time_count": int(len(times)),
            "gaps_over_1p5_days": int(np.count_nonzero(gaps > 1.5)),
            "maximum_gap_days": float(gaps.max()),
            "limitations": [
                "The preserved field is approximately 0.96 degree, not native 1/12 degree.",
                "Field interpolation rejects any cell with missing corners and records trajectory termination.",
                "No Stokes field is included unless selected separately by runner configuration.",
            ],
        },
    )


def unix_seconds(variable) -> np.ndarray:
    dates = netCDF4.num2date(
        numeric(variable),
        variable.units,
        only_use_cftime_datetimes=False,
    )
    return np.asarray(
        [date.replace(tzinfo=timezone.utc).timestamp() for date in dates],
        dtype=np.float64,
    )


def convert_native_hycom_tiles(
    manifest_path: Path, output: Path, coast_output: Path
) -> None:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("schema") not in {
        "mh370-native-hycom-retrieval-v1",
        "mh370-native-hycom-retrieval-v2",
    }:
        raise ValueError("unsupported native-HYCOM retrieval manifest")
    primary_records = manifest.get("tiles", [])
    supplemental_records = manifest.get("supplemental_tiles", [])
    tile_records = primary_records + supplemental_records
    if not tile_records:
        raise ValueError("native-HYCOM retrieval manifest has no tiles")

    tiles_by_time_signature: dict[tuple[float, ...], list[dict]] = {}
    all_latitudes, all_longitudes = [], []
    source_bytes = 0
    for record in tile_records:
        path = Path(record["path"])
        if not path.is_absolute():
            path = manifest_path.parent / path
        actual_hash = sha256(path)
        if actual_hash != record["sha256"]:
            raise ValueError(f"native-HYCOM tile hash mismatch: {path}")
        source_bytes += path.stat().st_size
        with netCDF4.Dataset(path) as dataset:
            current_times = unix_seconds(dataset["time"])
            all_latitudes.append(numeric(dataset["lat"]).astype(np.float64))
            all_longitudes.append(numeric(dataset["lon"]).astype(np.float64))
            for component in ("water_u", "water_v"):
                variable = dataset[component]
                if (
                    variable.dimensions != ("time", "depth", "lat", "lon")
                    or variable.dtype != np.dtype("int16")
                    or variable.units != "m/s"
                    or float(variable.scale_factor) != np.float32(0.001)
                    or float(variable.add_offset) != 0.0
                    or int(variable._FillValue) != -30000
                ):
                    raise ValueError(f"unexpected native-HYCOM packing in {path}")
        signature = tuple(current_times.tolist())
        tiles_by_time_signature.setdefault(signature, []).append(
            {"path": path, "record": record}
        )

    latitudes = np.unique(np.concatenate(all_latitudes))
    longitudes = np.unique(np.concatenate(all_longitudes))
    if (
        np.any(np.diff(latitudes) <= 0)
        or np.any(np.diff(longitudes) <= 0)
        or float(np.max(np.diff(latitudes))) > 0.081
        or float(np.max(np.diff(longitudes))) > 0.081
    ):
        raise ValueError("native-HYCOM tile mosaic has a spatial gap")

    time_sources = []
    for signature, tiles in tiles_by_time_signature.items():
        group_latitudes, group_longitudes = [], []
        for tile in tiles:
            with netCDF4.Dataset(tile["path"]) as dataset:
                group_latitudes.append(numeric(dataset["lat"]).astype(np.float64))
                group_longitudes.append(numeric(dataset["lon"]).astype(np.float64))
        if not (
            np.array_equal(np.unique(np.concatenate(group_latitudes)), latitudes)
            and np.array_equal(np.unique(np.concatenate(group_longitudes)), longitudes)
        ):
            raise ValueError(
                "a native-HYCOM time group does not cover the full requested mosaic"
            )
        for local_index, unix_time in enumerate(signature):
            time_sources.append((unix_time, signature, local_index))
    time_sources.sort(key=lambda item: item[0])
    times = np.asarray([item[0] for item in time_sources], dtype=np.float64)
    if np.any(np.diff(times) <= 0):
        raise ValueError("native-HYCOM time groups overlap or are unordered")

    shape = (len(times), len(latitudes), len(longitudes))
    output.parent.mkdir(parents=True, exist_ok=True)
    missing = np.int16(-30000)
    valid_east = 0
    ever_valid_east = np.zeros((len(latitudes), len(longitudes)), dtype=bool)
    with output.open("wb") as stream:
        stream.write(MAGIC)
        stream.write(struct.pack("<6I", 2, 0, *shape, 2))
        stream.write(np.asarray(times, dtype="<f8").tobytes(order="C"))
        stream.write(np.asarray(latitudes, dtype="<f8").tobytes(order="C"))
        stream.write(np.asarray(longitudes, dtype="<f8").tobytes(order="C"))
        for source_name, target_name in (("water_u", "u"), ("water_v", "v")):
            stream.write(target_name.encode("ascii").ljust(16, b"\0"))
            stream.write(struct.pack("<I", 1))  # packed signed i16
            stream.write(struct.pack("<ddh", 0.001, 0.0, int(missing)))
            opened = []
            try:
                for tiles in tiles_by_time_signature.values():
                    for tile in tiles:
                        dataset = netCDF4.Dataset(tile["path"])
                        variable = dataset[source_name]
                        variable.set_auto_maskandscale(False)
                        variable.set_var_chunk_cache(
                            size=1024 * 1024, nelems=1009, preemption=0.75
                        )
                        tile["dataset"] = dataset
                        tile["variable"] = variable
                        tile["latitude_indices"] = np.searchsorted(
                            latitudes, numeric(dataset["lat"])
                        )
                        tile["longitude_indices"] = np.searchsorted(
                            longitudes, numeric(dataset["lon"])
                        )
                        opened.append(dataset)
                for _, signature, local_time_index in time_sources:
                    mosaic = np.full(
                        (len(latitudes), len(longitudes)),
                        missing,
                        dtype="<i2",
                    )
                    for tile in tiles_by_time_signature[signature]:
                        values = np.asarray(
                            tile["variable"][local_time_index, 0, :, :],
                            dtype="<i2",
                        )
                        target = np.ix_(
                            tile["latitude_indices"], tile["longitude_indices"]
                        )
                        prior = mosaic[target]
                        overlap = (prior != missing) & (values != missing)
                        if np.any(prior[overlap] != values[overlap]):
                            raise ValueError(
                                f"native-HYCOM overlap differs in {tile['path']}"
                            )
                        replace = values != missing
                        prior[replace] = values[replace]
                        mosaic[target] = prior
                    if source_name == "water_u":
                        valid_east += int(np.count_nonzero(mosaic != missing))
                        ever_valid_east |= mosaic != missing
                    stream.write(mosaic.tobytes(order="C"))
            finally:
                for dataset in opened:
                    dataset.close()

    gaps_hours = np.diff(times) / 3600.0
    metadata = {
        "schema": "mh370-gridded-field-input-v2",
        "converter_version": CONVERTER_VERSION,
        "binary_format": "MHGRID schema 2 little-endian packed i16",
        "binary_sha256": sha256(output),
        "axis_order": ["time", "latitude", "longitude"],
        "latitude_units": "degrees_north WGS84",
        "longitude_units": "degrees_east WGS84",
        "name": "GOFS 3.1-like HYCOM+NCODA GLBv0.08 experiment 53.X native-grid surface currents",
        "family": "hycom_gofs31_reanalysis",
        "field_role": "currents",
        "time_axis": "UTC Unix seconds",
        "component_units": {"u": "m s-1 east", "v": "m s-1 north"},
        "packing": {
            "encoding": "signed i16",
            "scale_factor": 0.001,
            "add_offset": 0.0,
            "missing_value": -30000,
        },
        "retrieval_manifest": {
            "path": str(manifest_path),
            "sha256": sha256(manifest_path),
        },
        "source_tile_count": len(tile_records),
        "primary_tile_count": len(primary_records),
        "supplemental_tile_count": len(supplemental_records),
        "source_tile_bytes": source_bytes,
        "spatial_bounds_degrees": {
            "south": float(latitudes[0]),
            "north": float(latitudes[-1]),
            "west": float(longitudes[0]),
            "east": float(longitudes[-1]),
        },
        "latitude_spacing_degrees": sorted(
            set(np.round(np.diff(latitudes), 6).tolist())
        ),
        "longitude_spacing_degrees": sorted(
            set(np.round(np.diff(longitudes), 6).tolist())
        ),
        "time_count": len(times),
        "first_time_unix_seconds": float(times[0]),
        "last_time_unix_seconds": float(times[-1]),
        "time_gap_counts_hours": {
            f"{gap:g}": int(np.count_nonzero(np.isclose(gaps_hours, gap)))
            for gap in sorted(set(gaps_hours.tolist()))
        },
        "maximum_time_gap_hours": float(gaps_hours.max()),
        "full_time_axis_audit": manifest.get("full_time_axis_audit"),
        "finite_eastward_fraction_including_land": valid_east / np.prod(shape),
        "limitations": [
            "This is every eighth available 3-hour analysis, not a daily mean; exact supplemental analyses repair two stride-created gaps, leaving variable 24-30 hour spacing and phase changes.",
            "The GOFS 3.1-like reanalysis documents known deep-water and Philippine Sea issues; predictive drifter validation is required before primary use.",
            "Land remains the packed missing sentinel. No missing ocean value is converted to zero current.",
            "Stokes drift, direct windage, and coastal beaching are not included in this current field and require distinct explicit inputs.",
        ],
    }
    output.with_suffix(output.suffix + ".json").write_text(
        json.dumps(metadata, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )

    # Use the source model's persistent wet mask only to distinguish a true
    # land encounter from missing current coverage. This does not invent a
    # beaching process: `beaching_rate` is deliberately absent.
    land_fraction = (~ever_valid_east).astype(np.float32)
    write_grid(
        coast_output,
        0,
        np.asarray([times[0], times[-1]], dtype=np.float64),
        latitudes,
        longitudes,
        [
            (
                "land_fraction",
                np.stack([land_fraction, land_fraction], axis=0),
            )
        ],
        {
            "name": "Native HYCOM persistent wet-mask coastal support field",
            "family": "hycom_gofs31_reanalysis",
            "field_role": "coastal_support",
            "time_axis": "constant over the native-current retrieval interval",
            "component_units": {"land_fraction": "binary fraction 0 ocean 1 land"},
            "retrieval_manifest": {
                "path": str(manifest_path),
                "sha256": sha256(manifest_path),
            },
            "definition": "land_fraction=1 only where eastward surface current is missing at every retrieved analysis; intermittently missing ocean cells remain ocean and terminate as missing field coverage when encountered",
            "limitations": [
                "This model wet mask distinguishes land from data gaps; it is not a shoreline-distance or beaching-probability model.",
                "No beaching_rate component is present, so the transport code cannot invent coastal retention.",
            ],
        },
    )


def packed_velocity_slice(
    values: np.ndarray, source: str, persistent_land_mask: np.ndarray | None = None
) -> tuple[np.ndarray, np.ndarray]:
    values = np.asarray(values, dtype=np.float64)
    finite = np.isfinite(values)
    encoded = np.full(values.shape, PACKED_CURRENT_MISSING, dtype="<i2")
    if persistent_land_mask is not None:
        if persistent_land_mask.shape != values.shape:
            raise ValueError(f"{source} persistent-land mask has the wrong shape")
        encoded[persistent_land_mask & ~finite] = PACKED_PERSISTENT_LAND_MASK
    scaled = np.rint(values[finite] / PACKED_CURRENT_SCALE)
    if (
        np.any(scaled < np.iinfo(np.int16).min)
        or np.any(scaled > np.iinfo(np.int16).max)
        or np.any(scaled == int(PACKED_CURRENT_MISSING))
        or np.any(scaled == int(PACKED_PERSISTENT_LAND_MASK))
    ):
        raise ValueError(f"{source} contains a value outside packed-velocity range")
    encoded[finite] = scaled.astype("<i2")
    return encoded, finite


def audit_persistent_finite_mask(
    paths: list[Path], variables: tuple[str, ...], has_depth_axis: bool
) -> tuple[np.ndarray, dict]:
    reference = None
    always_finite = None
    ever_finite = None
    changed_cells = None
    comparisons = 0
    for source_name in variables:
        for path in paths:
            with netCDF4.Dataset(path) as dataset:
                variable = dataset[source_name]
                variable.set_var_chunk_cache(
                    size=8 * 1024 * 1024, nelems=10_007, preemption=0.75
                )
                for time_index in range(len(dataset["time"])):
                    selection = (
                        variable[time_index, 0, :, :]
                        if has_depth_axis
                        else variable[time_index, :, :]
                    )
                    finite = np.isfinite(numeric(selection))
                    if reference is None:
                        reference = finite.copy()
                        always_finite = finite.copy()
                        ever_finite = finite.copy()
                        changed_cells = np.zeros(finite.shape, dtype=bool)
                    else:
                        comparisons += 1
                        always_finite &= finite
                        ever_finite |= finite
                        changed_cells |= finite != reference
    if reference is None:
        raise ValueError("cannot audit an empty field")
    persistent_missing = ~ever_finite
    return persistent_missing, {
        "time_component_comparisons": comparisons,
        "changed_cells": int(np.count_nonzero(changed_cells)),
        "persistent_missing_cells": int(np.count_nonzero(persistent_missing)),
        "intermittently_missing_cells": int(
            np.count_nonzero(ever_finite & ~always_finite)
        ),
    }


def convert_cmems_glorys12(
    manifest_path: Path, output: Path, coast_output: Path
) -> None:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if (
        manifest.get("schema") != "mh370-cmems-glorys12-retrieval-v1"
        or manifest.get("product_id") != "GLOBAL_MULTIYEAR_PHY_001_030"
        or manifest.get("dataset_id") != "cmems_mod_glo_phy_my_0.083deg_P1D-m"
    ):
        raise ValueError("unsupported CMEMS GLORYS12 retrieval manifest")
    records = manifest.get("files", [])
    if not records:
        raise ValueError("CMEMS GLORYS12 retrieval manifest has no files")

    paths = []
    time_segments = []
    latitudes = longitudes = None
    source_bytes = 0
    for record in records:
        path = Path(record["path"])
        if not path.is_absolute():
            path = manifest_path.parent / path
        if sha256(path) != record["sha256"]:
            raise ValueError(f"CMEMS GLORYS12 file hash mismatch: {path}")
        source_bytes += path.stat().st_size
        with netCDF4.Dataset(path) as dataset:
            current_latitudes = numeric(dataset["latitude"]).astype(np.float64)
            current_longitudes = numeric(dataset["longitude"]).astype(np.float64)
            depths = numeric(dataset["depth"]).astype(np.float64)
            current_times = unix_seconds(dataset["time"])
            if (
                len(depths) != 1
                or not np.isclose(depths[0], 0.49402499198913574)
                or dataset["uo"].dimensions
                != ("time", "depth", "latitude", "longitude")
                or dataset["vo"].dimensions != dataset["uo"].dimensions
                or dataset["uo"].units != "m s-1"
                or dataset["vo"].units != "m s-1"
            ):
                raise ValueError(f"unexpected CMEMS GLORYS12 schema in {path}")
            if latitudes is None:
                latitudes = current_latitudes
                longitudes = current_longitudes
            elif not (
                np.array_equal(latitudes, current_latitudes)
                and np.array_equal(longitudes, current_longitudes)
            ):
                raise ValueError("CMEMS GLORYS12 monthly grids differ")
        paths.append(path)
        time_segments.append(current_times)

    times = np.concatenate(time_segments)
    if (
        np.any(np.diff(times) <= 0.0)
        or len(times) != manifest.get("summary", {}).get("time_count")
    ):
        raise ValueError("CMEMS GLORYS12 times overlap, repeat, or differ from manifest")
    gaps_hours = np.diff(times) / 3600.0
    if not np.allclose(gaps_hours, 24.0, rtol=0.0, atol=1e-6):
        raise ValueError("CMEMS GLORYS12 field is not a gap-free daily sequence")
    if (
        np.any(np.diff(latitudes) <= 0.0)
        or np.any(np.diff(longitudes) <= 0.0)
        or float(np.max(np.diff(latitudes))) > 0.084
        or float(np.max(np.diff(longitudes))) > 0.084
    ):
        raise ValueError("CMEMS GLORYS12 grid is unordered or has a spatial gap")

    shape = (len(times), len(latitudes), len(longitudes))
    output.parent.mkdir(parents=True, exist_ok=True)
    valid_counts = {}
    persistent_land_mask, mask_audit = audit_persistent_finite_mask(
        paths, ("uo", "vo"), has_depth_axis=True
    )
    with output.open("wb") as stream:
        stream.write(MAGIC)
        stream.write(struct.pack("<6I", 3, 0, *shape, 2))
        stream.write(np.asarray(times, dtype="<f8").tobytes(order="C"))
        stream.write(np.asarray(latitudes, dtype="<f8").tobytes(order="C"))
        stream.write(np.asarray(longitudes, dtype="<f8").tobytes(order="C"))
        for source_name, target_name in (("uo", "u"), ("vo", "v")):
            stream.write(target_name.encode("ascii").ljust(16, b"\0"))
            stream.write(struct.pack("<I", 1))
            stream.write(
                struct.pack(
                    "<ddhh",
                    PACKED_CURRENT_SCALE,
                    0.0,
                    int(PACKED_CURRENT_MISSING),
                    int(PACKED_PERSISTENT_LAND_MASK),
                )
            )
            valid_count = 0
            for path in paths:
                with netCDF4.Dataset(path) as dataset:
                    variable = dataset[source_name]
                    variable.set_var_chunk_cache(
                        size=8 * 1024 * 1024, nelems=10_007, preemption=0.75
                    )
                    for time_index in range(len(dataset["time"])):
                        encoded, finite = packed_velocity_slice(
                            numeric(variable[time_index, 0, :, :]),
                            f"{path.name}:{source_name}:{time_index}",
                            persistent_land_mask,
                        )
                        valid_count += int(np.count_nonzero(finite))
                        stream.write(encoded.tobytes(order="C"))
            valid_counts[target_name] = valid_count

    metadata = {
        "schema": "mh370-gridded-field-input-v2",
        "converter_version": CONVERTER_VERSION,
        "binary_format": "MHGRID schema 3 little-endian packed i16 with distinct persistent-land sentinel",
        "binary_sha256": sha256(output),
        "axis_order": ["time", "latitude", "longitude"],
        "latitude_units": "degrees_north WGS84",
        "longitude_units": "degrees_east WGS84",
        "name": "CMEMS GLORYS12V1 daily-mean native-grid surface currents",
        "family": "cmems_glorys12_reanalysis",
        "field_role": "currents",
        "product_id": manifest["product_id"],
        "dataset_id": manifest["dataset_id"],
        "time_axis": "UTC Unix seconds; upstream daily field labelled at 00:00 UTC",
        "component_units": {"u": "m s-1 east", "v": "m s-1 north"},
        "surface_depth_metres": 0.49402499198913574,
        "packing": {
            "encoding": "signed i16",
            "scale_factor": PACKED_CURRENT_SCALE,
            "add_offset": 0.0,
            "missing_value": int(PACKED_CURRENT_MISSING),
            "persistent_land_mask_value": int(PACKED_PERSISTENT_LAND_MASK),
        },
        "retrieval_manifest": {
            "path": str(manifest_path),
            "sha256": sha256(manifest_path),
        },
        "source_file_count": len(paths),
        "source_file_bytes": source_bytes,
        "spatial_bounds_degrees": {
            "south": float(latitudes[0]),
            "north": float(latitudes[-1]),
            "west": float(longitudes[0]),
            "east": float(longitudes[-1]),
        },
        "latitude_spacing_degrees": sorted(
            set(np.round(np.diff(latitudes), 8).tolist())
        ),
        "longitude_spacing_degrees": sorted(
            set(np.round(np.diff(longitudes), 8).tolist())
        ),
        "time_count": len(times),
        "first_time_unix_seconds": float(times[0]),
        "last_time_unix_seconds": float(times[-1]),
        "time_gap_counts_hours": {"24": len(times) - 1},
        "maximum_time_gap_hours": float(gaps_hours.max()),
        "finite_component_fractions_including_land": {
            name: count / np.prod(shape) for name, count in valid_counts.items()
        },
        "persistent_missing_mask_audit": {
            **mask_audit,
            "interpretation": "Persistent missing cells define coastal support. Any intermittent missing cell remains missing in the packed current field and is never converted to zero.",
        },
        "limitations": [
            "GLORYS12V1 is assimilative; the available drifter replay is not guaranteed held out.",
            "Daily means omit subdaily current variability represented by the native-HYCOM three-hour analyses.",
            "Land and any missing ocean value remain the packed missing sentinel; no missing value is converted to zero current.",
            "Stokes drift, direct windage, and coastal beaching are not included in this current field and require distinct explicit inputs.",
        ],
    }
    output.with_suffix(output.suffix + ".json").write_text(
        json.dumps(metadata, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )

    land_fraction = persistent_land_mask.astype(np.float32)
    write_grid(
        coast_output,
        0,
        np.asarray([times[0], times[-1]], dtype=np.float64),
        latitudes,
        longitudes,
        [
            (
                "land_fraction",
                np.stack([land_fraction, land_fraction], axis=0),
            )
        ],
        {
            "name": "CMEMS GLORYS12V1 persistent wet-mask coastal support field",
            "family": "cmems_glorys12_reanalysis",
            "field_role": "coastal_support",
            "time_axis": "constant over the CMEMS retrieval interval",
            "component_units": {"land_fraction": "binary fraction 0 ocean 1 land"},
            "retrieval_manifest": {
                "path": str(manifest_path),
                "sha256": sha256(manifest_path),
            },
            "definition": "land_fraction=1 only where eastward surface current is missing at every retrieved daily analysis; intermittently missing ocean cells remain ocean and terminate as missing field coverage when encountered",
            "limitations": [
                "This model wet mask distinguishes persistent land from data gaps; it is not a shoreline-distance or beaching-probability model.",
                "No beaching_rate component is present, so the transport code cannot invent coastal retention.",
            ],
        },
    )


def convert_cmems_waverys(
    manifest_path: Path, output: Path, coast_output: Path
) -> None:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if (
        manifest.get("schema") != "mh370-cmems-waverys-retrieval-v1"
        or manifest.get("product_id") != "GLOBAL_MULTIYEAR_WAV_001_032"
        or manifest.get("dataset_id") != "cmems_mod_glo_wav_my_0.2deg_PT3H-i"
        or manifest.get("dataset_version") != "202411"
    ):
        raise ValueError("unsupported CMEMS WAVERYS retrieval manifest")
    records = manifest.get("files", [])
    if not records:
        raise ValueError("CMEMS WAVERYS retrieval manifest has no files")

    paths = []
    time_segments = []
    latitudes = longitudes = None
    source_bytes = 0
    expected_standard_names = {
        "VSDX": "sea_surface_wave_stokes_drift_x_velocity",
        "VSDY": "sea_surface_wave_stokes_drift_y_velocity",
    }
    for record in records:
        path = Path(record["path"])
        if not path.is_absolute():
            path = manifest_path.parent / path
        if sha256(path) != record["sha256"]:
            raise ValueError(f"CMEMS WAVERYS file hash mismatch: {path}")
        source_bytes += path.stat().st_size
        with netCDF4.Dataset(path) as dataset:
            current_latitudes = numeric(dataset["latitude"]).astype(np.float64)
            current_longitudes = numeric(dataset["longitude"]).astype(np.float64)
            current_times = unix_seconds(dataset["time"])
            for component, standard_name in expected_standard_names.items():
                variable = dataset[component]
                if (
                    variable.dimensions != ("time", "latitude", "longitude")
                    or variable.units != "m s-1"
                    or variable.standard_name != standard_name
                ):
                    raise ValueError(f"unexpected CMEMS WAVERYS schema in {path}")
            if latitudes is None:
                latitudes = current_latitudes
                longitudes = current_longitudes
            elif not (
                np.array_equal(latitudes, current_latitudes)
                and np.array_equal(longitudes, current_longitudes)
            ):
                raise ValueError("CMEMS WAVERYS monthly grids differ")
        paths.append(path)
        time_segments.append(current_times)

    times = np.concatenate(time_segments)
    if (
        np.any(np.diff(times) <= 0.0)
        or len(times) != manifest.get("summary", {}).get("time_count")
    ):
        raise ValueError("CMEMS WAVERYS times overlap, repeat, or differ from manifest")
    gaps_hours = np.diff(times) / 3600.0
    if not np.allclose(gaps_hours, 3.0, rtol=0.0, atol=1e-6):
        raise ValueError("CMEMS WAVERYS field is not a gap-free three-hour sequence")
    if (
        np.any(np.diff(latitudes) <= 0.0)
        or np.any(np.diff(longitudes) <= 0.0)
        or float(np.max(np.diff(latitudes))) > 0.201
        or float(np.max(np.diff(longitudes))) > 0.201
    ):
        raise ValueError("CMEMS WAVERYS grid is unordered or has a spatial gap")

    shape = (len(times), len(latitudes), len(longitudes))
    output.parent.mkdir(parents=True, exist_ok=True)
    valid_counts = {}
    persistent_land_mask, mask_audit = audit_persistent_finite_mask(
        paths, ("VSDX", "VSDY"), has_depth_axis=False
    )
    with output.open("wb") as stream:
        stream.write(MAGIC)
        stream.write(struct.pack("<6I", 3, 0, *shape, 2))
        stream.write(np.asarray(times, dtype="<f8").tobytes(order="C"))
        stream.write(np.asarray(latitudes, dtype="<f8").tobytes(order="C"))
        stream.write(np.asarray(longitudes, dtype="<f8").tobytes(order="C"))
        for source_name, target_name in (("VSDX", "u"), ("VSDY", "v")):
            stream.write(target_name.encode("ascii").ljust(16, b"\0"))
            stream.write(struct.pack("<I", 1))
            stream.write(
                struct.pack(
                    "<ddhh",
                    PACKED_CURRENT_SCALE,
                    0.0,
                    int(PACKED_CURRENT_MISSING),
                    int(PACKED_PERSISTENT_LAND_MASK),
                )
            )
            valid_count = 0
            for path in paths:
                with netCDF4.Dataset(path) as dataset:
                    variable = dataset[source_name]
                    variable.set_var_chunk_cache(
                        size=8 * 1024 * 1024, nelems=10_007, preemption=0.75
                    )
                    for time_index in range(len(dataset["time"])):
                        encoded, finite = packed_velocity_slice(
                            numeric(variable[time_index, :, :]),
                            f"{path.name}:{source_name}:{time_index}",
                            persistent_land_mask,
                        )
                        valid_count += int(np.count_nonzero(finite))
                        stream.write(encoded.tobytes(order="C"))
            valid_counts[target_name] = valid_count

    metadata = {
        "schema": "mh370-gridded-field-input-v2",
        "converter_version": CONVERTER_VERSION,
        "binary_format": "MHGRID schema 3 little-endian packed i16 with distinct persistent-land sentinel",
        "binary_sha256": sha256(output),
        "axis_order": ["time", "latitude", "longitude"],
        "latitude_units": "degrees_north WGS84",
        "longitude_units": "degrees_east WGS84",
        "name": "CMEMS WAVERYS MFWAM three-hourly native-grid surface Stokes velocity",
        "family": "cmems_waverys_reanalysis",
        "field_role": "stokes",
        "product_id": manifest["product_id"],
        "dataset_id": manifest["dataset_id"],
        "dataset_version": manifest["dataset_version"],
        "dataset_part": manifest["dataset_part"],
        "time_axis": "UTC Unix seconds; upstream three-hourly instantaneous analyses",
        "component_units": {
            "u": "m s-1 east surface Stokes",
            "v": "m s-1 north surface Stokes",
        },
        "packing": {
            "encoding": "signed i16",
            "scale_factor": PACKED_CURRENT_SCALE,
            "add_offset": 0.0,
            "missing_value": int(PACKED_CURRENT_MISSING),
            "persistent_land_mask_value": int(PACKED_PERSISTENT_LAND_MASK),
        },
        "retrieval_manifest": {
            "path": str(manifest_path),
            "sha256": sha256(manifest_path),
        },
        "source_file_count": len(paths),
        "source_file_bytes": source_bytes,
        "spatial_bounds_degrees": {
            "south": float(latitudes[0]),
            "north": float(latitudes[-1]),
            "west": float(longitudes[0]),
            "east": float(longitudes[-1]),
        },
        "latitude_spacing_degrees": sorted(
            set(np.round(np.diff(latitudes), 8).tolist())
        ),
        "longitude_spacing_degrees": sorted(
            set(np.round(np.diff(longitudes), 8).tolist())
        ),
        "time_count": len(times),
        "first_time_unix_seconds": float(times[0]),
        "last_time_unix_seconds": float(times[-1]),
        "time_gap_counts_hours": {"3": len(times) - 1},
        "maximum_time_gap_hours": float(gaps_hours.max()),
        "finite_component_fractions_including_land": {
            name: count / np.prod(shape) for name, count in valid_counts.items()
        },
        "persistent_missing_mask_audit": {
            **mask_audit,
            "missing_fraction": float(np.mean(persistent_land_mask)),
            "interpretation": "Only cells missing in both components at every time are persistent coastal support. Intermittent or component-specific gaps retain the ordinary missing sentinel, terminate as missing field coverage when sampled, and are never converted to land or zero velocity.",
        },
        "limitations": [
            "WAVERYS is assimilative through significant-wave-height observations and uses GLORYS12 currents in the wave calculation.",
            "The field is surface Stokes velocity; a partially submerged flaperon response is represented only through an explicit scale sensitivity in transport configuration.",
            "Land and any missing ocean value remain the packed missing sentinel; no missing value is converted to zero velocity.",
            "The full evidence-domain missing mask varies with time or component. Those gaps remain typed missing coverage and are not included in the persistent coastal-support mask.",
            "Direct aerodynamic windage and object-specific residual leeway remain separate model terms.",
        ],
    }
    output.with_suffix(output.suffix + ".json").write_text(
        json.dumps(metadata, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )

    land_fraction = persistent_land_mask.astype(np.float32)
    write_grid(
        coast_output,
        0,
        np.asarray([times[0], times[-1]], dtype=np.float64),
        latitudes,
        longitudes,
        [
            (
                "land_fraction",
                np.stack([land_fraction, land_fraction], axis=0),
            )
        ],
        {
            "name": "CMEMS WAVERYS persistent-mask coastal support field",
            "family": "cmems_waverys_reanalysis",
            "field_role": "coastal_support",
            "time_axis": "constant over the WAVERYS retrieval interval",
            "component_units": {"land_fraction": "binary fraction 0 water 1 persistent wave-model mask"},
            "retrieval_manifest": {
                "path": str(manifest_path),
                "sha256": sha256(manifest_path),
            },
            "definition": "land_fraction=1 exactly where both WAVERYS Stokes components are missing at every retrieved three-hour analysis; intermittent and component-specific missing values remain typed field gaps rather than coast",
            "persistent_mask_counts": {
                "masked_cells": int(np.count_nonzero(land_fraction)),
                "water_cells": int(np.count_nonzero(1.0 - land_fraction)),
                "intermittently_missing_cells": mask_audit[
                    "intermittently_missing_cells"
                ],
                "changed_cells": mask_audit["changed_cells"],
            },
            "limitations": [
                "This is the native wave model persistent support mask, not a measured shoreline-distance, beaching-probability, retention, or refloating model.",
                "Its 0.2-degree coastal support is coarser than GLORYS12 currents and can terminate a path before the geometric shoreline.",
                "No beaching_rate component is present, so the transport code cannot invent coastal retention.",
            ],
        },
    )


def convert_gdp(path: Path, output: Path) -> None:
    with netCDF4.Dataset(path) as dataset:
        times = numeric(dataset["ClimatologicalMonth"])
        latitudes = numeric(dataset["latitude"])
        longitudes = numeric(dataset["longitude"])
        components = []
        for source, target in [("U", "u"), ("V", "v"), ("eU", "u_error"), ("eV", "v_error")]:
            values = numeric(dataset[source]).transpose(0, 2, 1)
            components.append((target, values))
    finite_fraction = float(np.isfinite(components[0][1]).mean())
    write_grid(
        output,
        1,
        times,
        latitudes,
        longitudes,
        components,
        {
            "family": "gdp",
            "name": "NOAA GDP drifter-derived monthly mean surface currents",
            "time_axis": "climatological month 0=January through 11=December; piecewise monthly",
            "component_units": {
                "u": "m s-1 east",
                "v": "m s-1 north",
                "u_error": "m s-1 standard error",
                "v_error": "m s-1 standard error",
            },
            "source_files": [{"path": str(path), "sha256": sha256(path)}],
            "preserved_grid_resolution_degrees": float(np.median(np.diff(latitudes))),
            "finite_ocean_fraction": finite_fraction,
            "limitations": [
                "This preserved subset is 0.5 degree; the current official product is 0.25 degree.",
                "Land and sparsely observed missing cells are not nearest-filled.",
                "Formal mean-current standard errors are not eddy diffusivity.",
            ],
        },
    )


def convert_oisst(paths: list[Path], output: Path) -> None:
    times, temperatures, source_files = [], [], []
    latitudes = longitudes = None
    epoch = datetime(1800, 1, 1, tzinfo=timezone.utc).timestamp()
    for path in paths:
        with netCDF4.Dataset(path) as dataset:
            current_latitudes = numeric(dataset["lat"])
            current_longitudes = numeric(dataset["lon"])
            if latitudes is None:
                latitudes, longitudes = current_latitudes, current_longitudes
            elif not (
                np.array_equal(latitudes, current_latitudes)
                and np.array_equal(longitudes, current_longitudes)
            ):
                raise ValueError("OISST segment grids differ")
            units = dataset["time"].units
            if units != "days since 1800-01-01 00:00:00":
                raise ValueError(f"unexpected OISST time units: {units}")
            times.append(epoch + numeric(dataset["time"]) * 86400.0)
            temperatures.append(numeric(dataset["sst"]))
        source_files.append({"path": str(path), "sha256": sha256(path)})
    times = np.concatenate(times)
    temperatures = np.concatenate(temperatures)
    order = np.argsort(times)
    times, temperatures = times[order], temperatures[order]
    if np.any(np.diff(times) <= 0):
        raise ValueError("OISST segment times overlap or repeat")
    write_grid(
        output,
        0,
        times,
        latitudes,
        longitudes,
        [("sst", temperatures)],
        {
            "name": "NOAA 1/4 degree daily OISST v2.1 regional subset",
            "field_role": "sst",
            "time_axis": "UTC Unix seconds",
            "component_units": {"sst": "degree C"},
            "source_files": source_files,
            "preserved_grid_resolution_degrees": float(np.median(np.diff(latitudes))),
            "limitations": [
                "SST is an analyzed gridded product, not an in-situ observation along the flaperon path."
            ],
        },
    )


def convert_isotope(path: Path, output: Path) -> None:
    records = []
    with path.open(newline="", encoding="utf-8-sig") as stream:
        for row in csv.DictReader(stream):
            if not row.get("temp", "").strip():
                continue
            day = float(row["days2-25"])
            temperature = float(row["temp"])
            # Algebraic inverse of Al-Qattan et al. equation 2 with d18Ow=0.4.
            delta18o = (19.0 - temperature) / 4.63 + (0.4 - 0.27)
            records.append(
                {
                    "sample_id": f"A2-G1-{len(records) + 1:02d}",
                    "delta18o_calcite_per_mil": delta18o,
                    "growth_fraction": day / 154.0,
                }
            )
    if len(records) != 49:
        raise ValueError(f"expected 49 nonblank A2-G1 target samples, found {len(records)}")
    # The sparse table ends on day 153; the paper anchors its terminal value on day 154.
    records[-1]["growth_fraction"] = 1.0
    payload = {
        "schema": "mh370-a2-g1-isotope-v1",
        "source_file": str(path),
        "converter_version": CONVERTER_VERSION,
        "source_sha256": sha256(path),
        "record_count": 49,
        "terminal_anchor": "2015-07-29",
        "note": "Sparse final nonblank row is 2015-07-28; the published daily interpolation carries the endpoint to the 2015-07-29 anchor.",
        "records": records,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def convert_stokes(path: Path, output: Path) -> None:
    with np.load(path) as dataset:
        required = {
            "date_days_since_1970",
            "latitude_deg",
            "longitude_deg",
            "stokes_east_m_s",
            "stokes_north_m_s",
        }
        if set(dataset.files) != required:
            raise ValueError(f"unexpected Stokes fields: {sorted(dataset.files)}")
        times = np.asarray(dataset["date_days_since_1970"], dtype=np.float64) * 86400.0
        latitudes = np.asarray(dataset["latitude_deg"], dtype=np.float64)
        longitudes = np.asarray(dataset["longitude_deg"], dtype=np.float64)
        east = np.asarray(dataset["stokes_east_m_s"], dtype=np.float32)
        north = np.asarray(dataset["stokes_north_m_s"], dtype=np.float32)
    if east.shape != (len(times), len(latitudes), len(longitudes)) or north.shape != east.shape:
        raise ValueError("Stokes component dimensions do not match their coordinates")
    latitude_order = np.argsort(latitudes)
    latitudes = latitudes[latitude_order]
    east = east[:, latitude_order, :]
    north = north[:, latitude_order, :]
    if np.any(np.diff(times) <= 0) or np.any(np.diff(longitudes) <= 0):
        raise ValueError("Stokes time/longitude coordinates are not strictly increasing")
    write_grid(
        output,
        0,
        times,
        latitudes,
        longitudes,
        [("u", east), ("v", north)],
        {
            "name": "ERA5 daily Stokes surface drift, preserved 1 degree regional field",
            "field_role": "stokes",
            "time_axis": "UTC Unix seconds",
            "component_units": {"u": "m s-1 east Stokes", "v": "m s-1 north Stokes"},
            "source_files": [{"path": str(path), "sha256": sha256(path)}],
            "preserved_grid_resolution_degrees": float(np.median(np.diff(latitudes))),
            "limitations": [
                "Daily 1 degree Stokes field omits subdaily and subgrid wave variability."
            ],
        },
    )


def convert_wind(u_paths: list[Path], v_paths: list[Path], output: Path) -> None:
    if not u_paths or len(u_paths) != len(v_paths):
        raise ValueError("wind conversion requires paired u/v files")
    epoch = datetime(1800, 1, 1, tzinfo=timezone.utc).timestamp()
    times, east, north, source_files = [], [], [], []
    latitudes = source_latitudes = longitudes = None
    for u_path, v_path in zip(u_paths, v_paths, strict=True):
        with netCDF4.Dataset(u_path) as u_dataset, netCDF4.Dataset(v_path) as v_dataset:
            expected = ("time", "level", "lat", "lon")
            if (
                u_dataset["uwnd"].dimensions != expected
                or v_dataset["vwnd"].dimensions != expected
                or u_dataset["time"].units != "hours since 1800-1-1 00:00:0.0"
                or v_dataset["time"].units != u_dataset["time"].units
                or u_dataset["uwnd"].units != "m/s"
                or v_dataset["vwnd"].units != "m/s"
            ):
                raise ValueError("unexpected NCEP R2 wind units or dimensions")
            u_time = numeric(u_dataset["time"])
            v_time = numeric(v_dataset["time"])
            u_lat = numeric(u_dataset["lat"])
            v_lat = numeric(v_dataset["lat"])
            u_lon = numeric(u_dataset["lon"])
            v_lon = numeric(v_dataset["lon"])
            if not (
                np.array_equal(u_time, v_time)
                and np.array_equal(u_lat, v_lat)
                and np.array_equal(u_lon, v_lon)
            ):
                raise ValueError("paired NCEP R2 wind coordinates differ")
            latitude_order = np.argsort(u_lat)
            current_latitudes = u_lat[latitude_order]
            current_longitudes = u_lon
            if latitudes is None:
                source_latitudes = current_latitudes
                # NCEP R2 T62 winds use a non-uniform Gaussian latitude axis.
                # MHGRID has a regular axis, so interpolate explicitly rather
                # than mislabelling the Gaussian rows as uniformly spaced.
                latitudes = np.linspace(
                    current_latitudes[0],
                    current_latitudes[-1],
                    len(current_latitudes),
                    dtype=np.float64,
                )
                longitudes = current_longitudes
            elif not (
                np.array_equal(source_latitudes, current_latitudes)
                and np.array_equal(longitudes, current_longitudes)
            ):
                raise ValueError("NCEP R2 yearly wind grids differ")
            times.append(epoch + u_time * 3600.0)
            east.append(
                interpolate_regular_latitude(
                    numeric(u_dataset["uwnd"])[:, 0, latitude_order, :],
                    source_latitudes,
                    latitudes,
                )
            )
            north.append(
                interpolate_regular_latitude(
                    numeric(v_dataset["vwnd"])[:, 0, latitude_order, :],
                    source_latitudes,
                    latitudes,
                )
            )
        source_files.extend(
            [
                {"path": str(u_path), "sha256": sha256(u_path)},
                {"path": str(v_path), "sha256": sha256(v_path)},
            ]
        )
    times = np.concatenate(times)
    east = np.concatenate(east)
    north = np.concatenate(north)
    order = np.argsort(times)
    times, east, north = times[order], east[order], north[order]
    if np.any(np.diff(times) <= 0):
        raise ValueError("NCEP R2 wind times overlap or repeat")
    write_grid(
        output,
        0,
        times,
        latitudes,
        longitudes,
        [("u", east), ("v", north)],
        {
            "name": "NCEP-DOE Reanalysis 2 daily 10 m winds, regular-latitude diagnostic field",
            "field_role": "wind_10m",
            "time_axis": "UTC Unix seconds",
            "component_units": {"u": "m s-1 east", "v": "m s-1 north"},
            "source_files": source_files,
            "source_latitude_axis": "T62 Gaussian, ascending after source-row reversal",
            "latitude_regridding": "linear interpolation onto equal spacing with the source endpoint latitudes and row count",
            "target_spacing_degrees": {
                "latitude": float(latitudes[1] - latitudes[0]),
                "longitude": float(longitudes[1] - longitudes[0]),
            },
            "coverage": {
                "first_time_utc": datetime.fromtimestamp(
                    float(times[0]), timezone.utc
                ).isoformat(),
                "last_time_utc": datetime.fromtimestamp(
                    float(times[-1]), timezone.utc
                ).isoformat(),
                "south_degrees": float(latitudes[0]),
                "north_degrees": float(latitudes[-1]),
                "west_degrees": float(longitudes[0]),
                "east_degrees": float(longitudes[-1]),
            },
            "limitations": [
                "Daily winds omit subdaily variability and are used only when direct windage is explicitly nonzero.",
                "The native Gaussian latitude grid is linearly regridded; this field is a direct-windage sensitivity, not a primary atmospheric product."
            ],
        },
    )


def interpolate_regular_latitude(
    values: np.ndarray, source_latitudes: np.ndarray, target_latitudes: np.ndarray
) -> np.ndarray:
    upper = np.searchsorted(source_latitudes, target_latitudes, side="left")
    upper = np.clip(upper, 1, len(source_latitudes) - 1)
    lower = upper - 1
    span = source_latitudes[upper] - source_latitudes[lower]
    fraction = (target_latitudes - source_latitudes[lower]) / span
    return (
        values[:, lower, :] * (1.0 - fraction)[None, :, None]
        + values[:, upper, :] * fraction[None, :, None]
    )


def convert_source_cells(path: Path, output: Path) -> None:
    document = json.loads(path.read_text(encoding="utf-8"))
    if document.get("type") != "FeatureCollection" or len(document.get("features", [])) != 1:
        raise ValueError("seventh-arc input must be a one-feature GeoJSON collection")
    geometry = document["features"][0].get("geometry", {})
    coordinates = geometry.get("coordinates")
    if geometry.get("type") != "LineString" or not isinstance(coordinates, list) or len(coordinates) != 200:
        raise ValueError("expected the official 200-point FL400 seventh-arc LineString")
    selected = coordinates[116:193]
    prior = 1.0 / len(selected)
    cells = []
    for index, coordinate in enumerate(selected, start=116):
        if not isinstance(coordinate, list) or len(coordinate) < 2:
            raise ValueError("invalid seventh-arc coordinate")
        longitude, latitude = map(float, coordinate[:2])
        cells.append(
            {
                "id": f"arc-{index}",
                "position": {"latitude": latitude, "longitude": longitude},
                "prior_weight": prior,
            }
        )
    payload = {
        "schema": "mh370-ocean-source-cells-v1",
        "source": "Official seventh-arc FL400 geometric reference",
        "source_path": str(path),
        "source_sha256": sha256(path),
        "selection": "geometry indices 116 through 192 inclusive; southern arc diagnostic domain",
        "cell_count": len(cells),
        "cells": cells,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--hycom", type=Path, nargs=3)
    parser.add_argument("--native-hycom-manifest", type=Path)
    parser.add_argument("--cmems-glorys12-manifest", type=Path)
    parser.add_argument("--cmems-waverys-manifest", type=Path)
    parser.add_argument("--combine-cmems-coast-support", action="store_true")
    parser.add_argument("--gdp", type=Path)
    parser.add_argument("--oisst", type=Path, nargs=2)
    parser.add_argument("--isotope", type=Path)
    parser.add_argument("--stokes", type=Path)
    parser.add_argument("--wind-u", type=Path, nargs="+")
    parser.add_argument("--wind-v", type=Path, nargs="+")
    parser.add_argument("--source-arc", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    legacy_inputs = [args.hycom, args.gdp, args.oisst, args.isotope, args.stokes, args.source_arc]
    if any(value is not None for value in legacy_inputs) and not all(
        value is not None for value in legacy_inputs
    ):
        parser.error(
            "--hycom, --gdp, --oisst, --isotope, --stokes, and --source-arc must be supplied together"
        )
    if (
        args.native_hycom_manifest is None
        and args.cmems_glorys12_manifest is None
        and args.cmems_waverys_manifest is None
        and not args.combine_cmems_coast_support
        and not all(value is not None for value in legacy_inputs)
        and args.wind_u is None
        and args.wind_v is None
    ):
        parser.error("no input family was selected")
    if args.native_hycom_manifest is not None:
        convert_native_hycom_tiles(
            args.native_hycom_manifest,
            args.output / "hycom-native.mhgrid",
            args.output / "hycom-native-coast.mhgrid",
        )
    if args.cmems_glorys12_manifest is not None:
        convert_cmems_glorys12(
            args.cmems_glorys12_manifest,
            args.output / "cmems-glorys12.mhgrid",
            args.output / "cmems-glorys12-coast.mhgrid",
        )
    if args.cmems_waverys_manifest is not None:
        convert_cmems_waverys(
            args.cmems_waverys_manifest,
            args.output / "cmems-waverys-stokes.mhgrid",
            args.output / "cmems-waverys-coast.mhgrid",
        )
    if args.combine_cmems_coast_support:
        combine_cmems_coastal_support(args.output)
    if all(value is not None for value in legacy_inputs):
        convert_hycom(args.hycom, args.output / "hycom.mhgrid")
        convert_gdp(args.gdp, args.output / "gdp.mhgrid")
        convert_oisst(args.oisst, args.output / "oisst.mhgrid")
        convert_isotope(args.isotope, args.output / "a2-g1-isotope.json")
        convert_stokes(args.stokes, args.output / "stokes.mhgrid")
    if (args.wind_u is None) != (args.wind_v is None):
        parser.error("--wind-u and --wind-v must be supplied together")
    if args.wind_u is not None:
        convert_wind(args.wind_u, args.wind_v, args.output / "wind.mhgrid")
    if args.source_arc is not None:
        convert_source_cells(args.source_arc, args.output / "source-cells.json")


if __name__ == "__main__":
    main()
