#!/usr/bin/env python3
"""Extract the immutable MH371 cruise weather cube from public ARCO ERA5.

The product consumes a compact, documented binary grid rather than importing
Python, xarray, or a remote-data client at runtime.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import struct
import tempfile
import time
from pathlib import Path

import modal


SOURCE = "gs://gcp-public-data-arco-era5/ar/full_37-1h-0p25deg-chunk-1.zarr-v3"
SOURCE_ACCESS_REVISION = "google-research/arco-era5@8fb5e9b982f489ba91af3ced9ce0b0a8ade8dd7d"
TIMES = tuple(f"2014-03-07T{hour:02d}:00:00" for hour in range(1, 9))
SOURCE_PRESSURE_HPA = (150, 175, 200, 225, 250, 300, 350, 400, 450, 500, 550, 600, 650, 700)
FLIGHT_LEVELS_FT = (10_000, 15_000, 20_000, 25_000, 30_000, 35_000, 40_000, 43_000)
LATITUDE_NORTH_DEG = 60.0
LATITUDE_SOUTH_DEG = -15.0
LONGITUDE_WEST_DEG = 75.0
LONGITUDE_EAST_DEG = 140.0
GRID_STEP_DEG = 0.5
VARIABLES = ("temperature", "u_component_of_wind", "v_component_of_wind")
VOLUME_NAME = "mh370-environment-v1"
VOLUME_MOUNT = Path("/mnt/environment")
REMOTE_DIRECTORY = Path("mh371/2014-03-07")
REMOTE_BINARY = REMOTE_DIRECTORY / "mh371-era5-grid.bin"
REMOTE_MANIFEST = REMOTE_DIRECTORY / "mh371-era5-grid.manifest.json"
MAGIC = b"MHERA5V1"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def isa_pressure_hpa(altitude_ft: float) -> float:
    altitude_m = altitude_ft * 0.3048
    gravity = 9.80665
    gas_constant = 287.05287
    if altitude_m <= 11_000.0:
        return 1013.25 * (1.0 - 0.0065 * altitude_m / 288.15) ** (
            gravity / (gas_constant * 0.0065)
        )
    pressure_11_hpa = 1013.25 * (216.65 / 288.15) ** (
        gravity / (gas_constant * 0.0065)
    )
    return pressure_11_hpa * math.exp(
        -gravity * (altitude_m - 11_000.0) / (gas_constant * 216.65)
    )


def interpolate_pressure_levels(raw, source_levels, target_pressures):
    import numpy as np

    source_levels = np.asarray(source_levels, dtype=float)
    outputs = []
    records = []
    for target in target_pressures:
        right = int(np.searchsorted(source_levels, target, side="right"))
        if right <= 0 or right >= len(source_levels):
            raise ValueError(f"target pressure {target} hPa is not bracketed")
        left = right - 1
        weight = (
            (math.log(target) - math.log(source_levels[left]))
            / (math.log(source_levels[right]) - math.log(source_levels[left]))
        )
        outputs.append((1.0 - weight) * raw[:, left] + weight * raw[:, right])
        records.append(
            {
                "target_pressure_hpa": target,
                "lower_source_hpa": float(source_levels[left]),
                "upper_source_hpa": float(source_levels[right]),
                "log_pressure_weight_to_upper": weight,
            }
        )
    return np.stack(outputs, axis=1).astype("float32"), records


def write_binary(path: Path, times, levels, latitudes, longitudes, fields) -> None:
    import numpy as np

    axes = (times, levels, latitudes, longitudes)
    counts = tuple(len(axis) for axis in axes)
    expected_shape = counts
    if any(tuple(field.shape) != expected_shape for field in fields):
        raise RuntimeError("ERA5 field shape does not match binary axes")
    with path.open("wb") as stream:
        stream.write(MAGIC)
        stream.write(struct.pack("<IIII", *counts))
        stream.write(np.asarray(times, dtype="<i8").tobytes(order="C"))
        for axis in (levels, latitudes, longitudes):
            stream.write(np.asarray(axis, dtype="<f4").tobytes(order="C"))
        for field in fields:
            stream.write(np.asarray(field, dtype="<f4").tobytes(order="C"))


image = modal.Image.debian_slim(python_version="3.12").uv_pip_install(
    "numpy==2.2.6",
    "xarray==2025.6.1",
    "zarr==3.1.2",
    "gcsfs==2025.5.1",
    "dask[array]==2025.5.1",
)
app = modal.App("mh370-mh371-era5-extract", image=image)
volume = modal.Volume.from_name(VOLUME_NAME, create_if_missing=True, version=2)


@app.function(
    cpu=4.0,
    memory=(16_384, 24_576),
    timeout=3_600,
    startup_timeout=600,
    retries=modal.Retries(max_retries=2, initial_delay=2.0),
    volumes={str(VOLUME_MOUNT): volume},
)
def extract() -> dict:
    import numpy as np
    import xarray as xr

    started = time.monotonic()
    dataset = xr.open_zarr(
        SOURCE,
        chunks=None,
        storage_options={"token": "anon"},
        consolidated=True,
    )
    subset = dataset[list(VARIABLES)].sel(
        time=list(TIMES),
        level=list(SOURCE_PRESSURE_HPA),
        latitude=slice(LATITUDE_NORTH_DEG, LATITUDE_SOUTH_DEG),
        longitude=slice(LONGITUDE_WEST_DEG, LONGITUDE_EAST_DEG),
    )
    subset = subset.isel(latitude=slice(None, None, 2), longitude=slice(None, None, 2))
    expected_shape = (
        len(TIMES),
        len(SOURCE_PRESSURE_HPA),
        int((LATITUDE_NORTH_DEG - LATITUDE_SOUTH_DEG) / GRID_STEP_DEG) + 1,
        int((LONGITUDE_EAST_DEG - LONGITUDE_WEST_DEG) / GRID_STEP_DEG) + 1,
    )
    if tuple(subset[VARIABLES[0]].shape) != expected_shape:
        raise RuntimeError(
            f"unexpected ERA5 subset shape {subset[VARIABLES[0]].shape}; expected {expected_shape}"
        )

    target_pressures = [isa_pressure_hpa(value) for value in FLIGHT_LEVELS_FT]
    fields = {}
    pressure_records = None
    for variable in VARIABLES:
        raw = np.asarray(subset[variable].values, dtype="float32")
        field, records = interpolate_pressure_levels(
            raw,
            np.asarray(subset.level.values, dtype=float),
            target_pressures,
        )
        fields[variable] = field
        pressure_records = pressure_records or records

    output_directory = VOLUME_MOUNT / REMOTE_DIRECTORY
    output_directory.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="mh371-era5-") as scratch:
        scratch_path = Path(scratch) / REMOTE_BINARY.name
        write_binary(
            scratch_path,
            np.asarray(subset.time.values).astype("datetime64[s]").astype("int64"),
            FLIGHT_LEVELS_FT,
            np.asarray(subset.latitude.values, dtype="float32"),
            np.asarray(subset.longitude.values, dtype="float32"),
            (
                fields["temperature"],
                fields["u_component_of_wind"],
                fields["v_component_of_wind"],
            ),
        )
        destination = VOLUME_MOUNT / REMOTE_BINARY
        temporary = destination.with_suffix(".bin.tmp")
        temporary.write_bytes(scratch_path.read_bytes())
        temporary.replace(destination)
        record = {
            "schema_version": "mh371-era5-grid-manifest-v1",
            "status": "extracted_from_arco_era5",
            "source": SOURCE,
            "source_access_revision": SOURCE_ACCESS_REVISION,
            "source_attributes": {
                key: dataset.attrs.get(key)
                for key in ("valid_time_start", "valid_time_stop", "last_updated")
            },
            "times_utc": list(TIMES),
            "source_pressure_levels_hpa": list(SOURCE_PRESSURE_HPA),
            "flight_levels_ft": list(FLIGHT_LEVELS_FT),
            "flight_level_pressure_interpolation": pressure_records,
            "latitude_bounds_deg": [LATITUDE_SOUTH_DEG, LATITUDE_NORTH_DEG],
            "longitude_bounds_deg": [LONGITUDE_WEST_DEG, LONGITUDE_EAST_DEG],
            "grid_step_deg": GRID_STEP_DEG,
            "variables_in_binary_order": [
                "temperature_k",
                "wind_east_m_s",
                "wind_north_m_s",
            ],
            "binary_format": {
                "magic": MAGIC.decode("ascii"),
                "byte_order": "little_endian",
                "axis_order": ["time", "flight_level", "latitude", "longitude"],
                "axis_types": ["int64_unix_seconds", "float32", "float32", "float32"],
                "field_type": "float32",
            },
            "array_shape_time_flight_level_lat_lon": list(fields[VARIABLES[0]].shape),
            "output_path": str(REMOTE_BINARY),
            "output_sha256": sha256(scratch_path),
            "output_bytes": scratch_path.stat().st_size,
            "elapsed_seconds": time.monotonic() - started,
        }
    (VOLUME_MOUNT / REMOTE_MANIFEST).write_text(
        json.dumps(record, indent=2) + "\n", encoding="utf-8"
    )
    volume.commit()
    os.sync()
    return record


@app.local_entrypoint()
def main() -> None:
    print(json.dumps(extract.remote(), indent=2))
