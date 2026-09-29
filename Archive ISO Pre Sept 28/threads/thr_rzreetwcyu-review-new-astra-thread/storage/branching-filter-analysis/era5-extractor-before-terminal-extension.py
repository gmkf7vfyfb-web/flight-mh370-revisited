#!/usr/bin/env python3
"""Extract and independently regenerate the canonical MH370 ERA5 grid.

The remote functions read only the public ARCO ERA5 pressure-level Zarr store.
Two independent reads must produce byte-identical binaries before ``finalize``
publishes a candidate to the Modal volume.  Local installation is deliberately
separate so the existing runtime grid is preserved until validation succeeds.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import shutil
import struct
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path

import modal


SOURCE = "gs://gcp-public-data-arco-era5/ar/full_37-1h-0p25deg-chunk-1.zarr-v3"
SOURCE_OBJECT_PREFIX = SOURCE.removeprefix("gs://")
SOURCE_ACCESS_REVISION = (
    "google-research/arco-era5@8fb5e9b982f489ba91af3ced9ce0b0a8ade8dd7d"
)
SOURCE_METADATA_GENERATION = "1788578126795769"
SOURCE_METADATA_SHA256 = "409449e1c7c4ec56159d7031d8756c76cb25619c6b5da005d15eaaf85eaaaf78"
SOURCE_METADATA_MD5_BASE64 = "kjsuNuyb3Ssu8Lo6N7nelQ=="

EXPECTED_SOURCE_CHUNK_IDENTITY_SHA256 = (
    "eed7079e6bbd5260d95f965071ed656d9667d43864f720207021fc1fb5bfb887"
)

TIMES = (
    "2014-03-07T17:00:00",
    "2014-03-07T18:00:00",
    "2014-03-07T19:00:00",
    "2014-03-07T20:00:00",
    "2014-03-07T21:00:00",
    "2014-03-07T22:00:00",
    "2014-03-07T23:00:00",
    "2014-03-08T00:00:00",
    "2014-03-08T01:00:00",
)
SOURCE_PRESSURE_HPA = (
    150,
    175,
    200,
    225,
    250,
    300,
    350,
    400,
    450,
    500,
    550,
    600,
    650,
    700,
    825,
    850,
    975,
    1000,
)
PRESSURE_ALTITUDES_FT = (
    500,
    5_000,
    10_000,
    15_000,
    20_000,
    25_000,
    28_000,
    31_000,
    34_000,
    37_000,
    40_000,
    43_000,
)
LATITUDE_NORTH_DEG = 90.0
LATITUDE_SOUTH_DEG = -90.0
LONGITUDE_WEST_DEG = -180.0
# +180 duplicates the -180 physical meridian. The extra axis endpoint closes
# the non-periodic runtime interpolator for valid queries in (179.5, 180).
LONGITUDE_EAST_DEG = 180.0
GRID_STEP_DEG = 0.5
VARIABLES = (
    "temperature",
    "u_component_of_wind",
    "v_component_of_wind",
)
VARIABLE_OUTPUT_NAMES = (
    "temperature_k",
    "wind_east_m_s",
    "wind_north_m_s",
)
VARIABLE_UNITS = {
    "temperature": "K",
    "u_component_of_wind": "m s**-1",
    "v_component_of_wind": "m s**-1",
}

SPOT_TARGETS = (
    {
        "time_utc": "2014-03-07T17:00:00",
        "pressure_altitude_ft": 500,
        "latitude_deg": 90.0,
        "longitude_deg": -180.0,
    },
    {
        "time_utc": "2014-03-07T21:00:00",
        "pressure_altitude_ft": 20_000,
        "latitude_deg": 0.0,
        "longitude_deg": 0.0,
    },
    {
        "time_utc": "2014-03-08T01:00:00",
        "pressure_altitude_ft": 43_000,
        "latitude_deg": -90.0,
        "longitude_deg": 180.0,
    },
)

ISA = {
    "sea_level_pressure_hpa": 1013.25,
    "sea_level_temperature_k": 288.15,
    "tropospheric_lapse_rate_k_m": 0.0065,
    "tropopause_geopotential_height_m": 11_000.0,
    "tropopause_temperature_k": 216.65,
    "standard_gravity_m_s2": 9.80665,
    "dry_air_gas_constant_j_kg_k": 287.05287,
    "metres_per_foot": 0.3048,
}

SOURCE_MEAN_LATITUDE_DEG = 5.624829
SOURCE_MEAN_LONGITUDE_DEG = 99.048157
SOURCE_POSITION_SD_NM = 0.5
CONTROL_DURATION_S = 22_150.0
COVERAGE_MACH_CAP = 0.87
METRES_PER_NAUTICAL_MILE = 1_852.0
DRY_AIR_HEAT_CAPACITY_RATIO = 1.4
# This is the minimum WGS-84 meridional radius of curvature and therefore
# gives a conservative conversion from path distance to latitude change.
WGS84_MINIMUM_MERIDIONAL_RADIUS_M = 6_335_439.3272928195

VOLUME_NAME = "mh370-environment-v1"
VOLUME_MOUNT = Path("/mnt/environment")
REMOTE_DIRECTORY = Path("mh370/2014-03-07_2014-03-08")
REMOTE_BINARY = REMOTE_DIRECTORY / "mh370-era5-grid.bin"
REMOTE_MANIFEST = REMOTE_DIRECTORY / "mh370-era5-grid.manifest.json"
REMOTE_RUN_DIRECTORY = REMOTE_DIRECTORY / "independent-runs"
MAGIC = b"MHERA5V1"


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def isa_pressure_hpa(altitude_ft: float) -> float:
    altitude_m = altitude_ft * ISA["metres_per_foot"]
    gravity = ISA["standard_gravity_m_s2"]
    gas_constant = ISA["dry_air_gas_constant_j_kg_k"]
    lapse_rate = ISA["tropospheric_lapse_rate_k_m"]
    sea_level_temperature = ISA["sea_level_temperature_k"]
    if altitude_m <= ISA["tropopause_geopotential_height_m"]:
        return ISA["sea_level_pressure_hpa"] * (
            1.0 - lapse_rate * altitude_m / sea_level_temperature
        ) ** (gravity / (gas_constant * lapse_rate))
    pressure_11_hpa = ISA["sea_level_pressure_hpa"] * (
        ISA["tropopause_temperature_k"] / sea_level_temperature
    ) ** (gravity / (gas_constant * lapse_rate))
    return pressure_11_hpa * math.exp(
        -gravity
        * (altitude_m - ISA["tropopause_geopotential_height_m"])
        / (gas_constant * ISA["tropopause_temperature_k"])
    )


def interpolation_plan(source_levels, target_altitudes):
    import numpy as np

    source_levels = np.asarray(source_levels, dtype="float64")
    records = []
    for altitude_ft in target_altitudes:
        target = isa_pressure_hpa(float(altitude_ft))
        right = int(np.searchsorted(source_levels, target, side="right"))
        if right <= 0 or right >= len(source_levels):
            raise ValueError(
                f"pressure altitude {altitude_ft} ft maps to {target} hPa, "
                "which is not bracketed"
            )
        left = right - 1
        lower = float(source_levels[left])
        upper = float(source_levels[right])
        weight = (math.log(target) - math.log(lower)) / (
            math.log(upper) - math.log(lower)
        )
        if not 0.0 <= weight <= 1.0:
            raise ValueError(f"invalid pressure interpolation weight {weight}")
        records.append(
            {
                "pressure_altitude_ft": int(altitude_ft),
                "target_pressure_hpa": target,
                "lower_source_hpa": lower,
                "upper_source_hpa": upper,
                "lower_source_index": left,
                "upper_source_index": right,
                "log_pressure_weight_to_upper": weight,
            }
        )
    return records


def interpolate_pressure_levels(raw, plan):
    import numpy as np

    outputs = []
    for record in plan:
        lower = raw[:, record["lower_source_index"]].astype("float64")
        upper = raw[:, record["upper_source_index"]].astype("float64")
        weight = record["log_pressure_weight_to_upper"]
        outputs.append(((1.0 - weight) * lower + weight * upper).astype("float32"))
    return np.stack(outputs, axis=1).astype("<f4", copy=False)


def write_binary(path: Path, times, levels, latitudes, longitudes, fields) -> None:
    import numpy as np

    axes = (times, levels, latitudes, longitudes)
    counts = tuple(len(axis) for axis in axes)
    if any(tuple(field.shape) != counts for field in fields):
        raise RuntimeError("ERA5 field shape does not match binary axes")
    if any(not np.all(np.isfinite(axis)) for axis in axes):
        raise RuntimeError("ERA5 binary axis contains a non-finite value")
    if any(
        len(axis) > 1
        and not (np.all(np.diff(axis) > 0.0) or np.all(np.diff(axis) < 0.0))
        for axis in axes
    ):
        raise RuntimeError("ERA5 binary axis is not strictly monotonic")
    if any(not np.all(np.isfinite(field)) for field in fields):
        raise RuntimeError("ERA5 field contains a non-finite value")
    with path.open("wb") as stream:
        stream.write(MAGIC)
        stream.write(struct.pack("<IIII", *counts))
        stream.write(np.asarray(times, dtype="<i8").tobytes(order="C"))
        for axis in (levels, latitudes, longitudes):
            stream.write(np.asarray(axis, dtype="<f4").tobytes(order="C"))
        for field in fields:
            stream.write(np.asarray(field, dtype="<f4").tobytes(order="C"))
        stream.flush()
        os.fsync(stream.fileno())


def normalized_gcs_identity(info: dict) -> dict:
    return {
        "generation": str(info.get("generation")),
        "metageneration": str(info.get("metageneration")),
        "size_bytes": int(info["size"]),
        "md5_base64": info.get("md5Hash") or info.get("md5"),
        "crc32c_base64": info.get("crc32c"),
        "etag": info.get("etag"),
        "updated": str(info.get("updated")),
    }


def source_identity(filesystem) -> tuple[dict, bytes]:
    metadata_path = f"{SOURCE_OBJECT_PREFIX}/.zmetadata"
    info = normalized_gcs_identity(filesystem.info(metadata_path))
    with filesystem.open(metadata_path, "rb") as stream:
        payload = stream.read()
    info.update(
        {
            "object": f"gs://{metadata_path}",
            "sha256": sha256_bytes(payload),
        }
    )
    if info["generation"] != SOURCE_METADATA_GENERATION:
        raise RuntimeError(
            "ARCO consolidated metadata generation changed: "
            f"{info['generation']} != {SOURCE_METADATA_GENERATION}"
        )
    if info["sha256"] != SOURCE_METADATA_SHA256:
        raise RuntimeError(
            f"ARCO consolidated metadata SHA-256 changed: {info['sha256']}"
        )
    if info["md5_base64"] != SOURCE_METADATA_MD5_BASE64:
        raise RuntimeError(
            f"ARCO consolidated metadata MD5 changed: {info['md5_base64']}"
        )
    return info, payload


def source_chunk_identities(filesystem, dataset) -> tuple[list[dict], str]:
    import numpy as np

    requested_times = np.asarray(TIMES, dtype="datetime64[ns]")
    time_indices = dataset.indexes["time"].get_indexer(requested_times)
    if (time_indices < 0).any():
        raise RuntimeError("one or more requested ERA5 times are absent")

    records = []
    for variable in VARIABLES:
        zarray = dataset[variable].encoding
        if tuple(dataset[variable].dims) != (
            "time",
            "level",
            "latitude",
            "longitude",
        ):
            raise RuntimeError(f"unexpected source dimensions for {variable}")
        for time_utc, time_index in zip(TIMES, time_indices, strict=True):
            relative_path = f"{variable}/{int(time_index)}.0.0.0"
            object_path = f"{SOURCE_OBJECT_PREFIX}/{relative_path}"
            identity = normalized_gcs_identity(filesystem.info(object_path))
            identity.update(
                {
                    "variable": variable,
                    "time_utc": time_utc,
                    "zarr_chunk_indices": [int(time_index), 0, 0, 0],
                    "object": f"gs://{object_path}",
                    "source_dtype": str(dataset[variable].dtype),
                    "source_chunks": list(zarray.get("chunks", (1, 37, 721, 1440))),
                }
            )
            records.append(identity)

    canonical = json.dumps(
        records, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("utf-8")
    identity_hash = sha256_bytes(canonical)
    if (
        EXPECTED_SOURCE_CHUNK_IDENTITY_SHA256 is not None
        and identity_hash != EXPECTED_SOURCE_CHUNK_IDENTITY_SHA256
    ):
        raise RuntimeError(
            "ARCO source chunk identity changed: "
            f"{identity_hash} != {EXPECTED_SOURCE_CHUNK_IDENTITY_SHA256}"
        )
    return records, identity_hash


def exact_index(values, target: float) -> int:
    import numpy as np

    indices = np.flatnonzero(np.asarray(values) == target)
    if len(indices) != 1:
        raise RuntimeError(f"coordinate {target} does not occur exactly once")
    return int(indices[0])


def raw_spot_checks(raw_fields, output_fields, plan, times, latitudes, longitudes):
    import numpy as np

    records = []
    for target in SPOT_TARGETS:
        time_index = exact_index(times, np.datetime64(target["time_utc"], "s"))
        altitude_index = exact_index(
            PRESSURE_ALTITUDES_FT, target["pressure_altitude_ft"]
        )
        latitude_index = exact_index(latitudes, target["latitude_deg"])
        longitude_index = exact_index(longitudes, target["longitude_deg"])
        bracket = plan[altitude_index]
        fields = {}
        for source_name, output_name in zip(
            VARIABLES, VARIABLE_OUTPUT_NAMES, strict=True
        ):
            raw = raw_fields[source_name]
            output = output_fields[source_name]
            fields[output_name] = {
                "raw_lower_source_value": float(
                    raw[
                        time_index,
                        bracket["lower_source_index"],
                        latitude_index,
                        longitude_index,
                    ]
                ),
                "raw_upper_source_value": float(
                    raw[
                        time_index,
                        bracket["upper_source_index"],
                        latitude_index,
                        longitude_index,
                    ]
                ),
                "output_value": float(
                    output[
                        time_index,
                        altitude_index,
                        latitude_index,
                        longitude_index,
                    ]
                ),
            }
        pressure_pa = bracket["target_pressure_hpa"] * 100.0
        temperature = fields["temperature_k"]["output_value"]
        records.append(
            {
                **target,
                "target_pressure_hpa": bracket["target_pressure_hpa"],
                "lower_source_hpa": bracket["lower_source_hpa"],
                "upper_source_hpa": bracket["upper_source_hpa"],
                "fields": fields,
                "derived_dry_air_density_kg_m3": pressure_pa
                / (ISA["dry_air_gas_constant_j_kg_k"] * temperature),
            }
        )
    return records


def peak_process_rss_bytes() -> int:
    import resource

    # Linux reports ru_maxrss in KiB.
    return int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss) * 1024


image = modal.Image.debian_slim(python_version="3.12").uv_pip_install(
    "numpy==2.2.6",
    "xarray==2025.6.1",
    "zarr==3.1.2",
    "gcsfs==2025.5.1",
    "dask[array]==2025.5.1",
)
app = modal.App("mh370-era5-expanded-extract", image=image)
volume = modal.Volume.from_name(VOLUME_NAME, create_if_missing=False, version=2)


@app.function(
    cpu=4.0,
    memory=(16_384, 24_576),
    timeout=3_600,
    startup_timeout=600,
    retries=modal.Retries(max_retries=2, initial_delay=2.0),
    volumes={str(VOLUME_MOUNT): volume},
)
def extract(run_id: str) -> dict:
    import gcsfs
    import numpy as np
    import xarray as xr

    if run_id not in {"independent-a", "independent-b", "source-pin-probe"}:
        raise ValueError(f"invalid run id {run_id!r}")

    started = time.perf_counter()
    filesystem = gcsfs.GCSFileSystem(
        token="anon", cache_timeout=0, skip_instance_cache=True
    )
    metadata_identity, metadata_payload = source_identity(filesystem)
    metadata_seconds = time.perf_counter() - started

    dataset = xr.open_zarr(
        SOURCE,
        chunks=None,
        storage_options={
            "token": "anon",
            "cache_timeout": 0,
            "skip_instance_cache": True,
        },
        consolidated=True,
    )
    chunk_records, chunk_identity_hash = source_chunk_identities(
        filesystem, dataset
    )
    source_attributes = {
        key: dataset.attrs.get(key)
        for key in (
            "valid_time_start",
            "valid_time_stop",
            "valid_time_stop_era5t",
            "last_updated",
        )
    }
    metadata_json = json.loads(metadata_payload)
    if metadata_json["metadata"][".zattrs"] != source_attributes:
        raise RuntimeError("xarray and consolidated root attributes disagree")

    source_variable_metadata = {}
    for variable in VARIABLES:
        attrs = dataset[variable].attrs
        actual_units = attrs.get("units")
        if actual_units != VARIABLE_UNITS[variable]:
            raise RuntimeError(
                f"unexpected {variable} units {actual_units!r}; "
                f"expected {VARIABLE_UNITS[variable]!r}"
            )
        source_variable_metadata[variable] = {
            key: attrs.get(key)
            for key in ("long_name", "short_name", "standard_name", "units")
        }

    open_subset = (
        dataset[list(VARIABLES)]
        .sel(
            time=list(TIMES),
            level=list(SOURCE_PRESSURE_HPA),
            latitude=slice(LATITUDE_NORTH_DEG, LATITUDE_SOUTH_DEG),
            longitude=slice(0.0, 359.75),
        )
        .isel(latitude=slice(None, None, 2), longitude=slice(None, None, 2))
        .transpose("time", "level", "latitude", "longitude")
    )
    expected_open_source_shape = (
        len(TIMES),
        len(SOURCE_PRESSURE_HPA),
        int((LATITUDE_NORTH_DEG - LATITUDE_SOUTH_DEG) / GRID_STEP_DEG) + 1,
        int(360.0 / GRID_STEP_DEG),
    )
    if tuple(open_subset[VARIABLES[0]].shape) != expected_open_source_shape:
        raise RuntimeError(
            f"unexpected ERA5 open subset shape {open_subset[VARIABLES[0]].shape}; "
            f"expected {expected_open_source_shape}"
        )
    if not np.array_equal(
        np.asarray(open_subset.level.values, dtype="float64"),
        np.asarray(SOURCE_PRESSURE_HPA, dtype="float64"),
    ):
        raise RuntimeError("unexpected ERA5 pressure-level axis")
    expected_latitudes = np.arange(
        LATITUDE_NORTH_DEG,
        LATITUDE_SOUTH_DEG - 0.5 * GRID_STEP_DEG,
        -GRID_STEP_DEG,
    )
    if not np.array_equal(
        np.asarray(open_subset.latitude.values, dtype="float64"), expected_latitudes
    ):
        raise RuntimeError("unexpected ERA5 latitude axis")

    source_longitudes = np.asarray(open_subset.longitude.values, dtype="float64")
    wrapped_longitudes = (source_longitudes + 180.0) % 360.0 - 180.0
    longitude_order = np.argsort(wrapped_longitudes)
    subset = open_subset.isel(longitude=longitude_order).assign_coords(
        longitude=wrapped_longitudes[longitude_order]
    )
    expected_open_longitudes = np.arange(-180.0, 180.0, GRID_STEP_DEG)
    if not np.array_equal(
        np.asarray(subset.longitude.values, dtype="float64"), expected_open_longitudes
    ):
        raise RuntimeError("unexpected wrapped ERA5 longitude axis")
    seam = subset.isel(longitude=slice(0, 1)).assign_coords(
        longitude=np.asarray([LONGITUDE_EAST_DEG], dtype="float64")
    )
    subset = xr.concat((subset, seam), dim="longitude")
    expected_source_shape = (
        len(TIMES),
        len(SOURCE_PRESSURE_HPA),
        int((LATITUDE_NORTH_DEG - LATITUDE_SOUTH_DEG) / GRID_STEP_DEG) + 1,
        int((LONGITUDE_EAST_DEG - LONGITUDE_WEST_DEG) / GRID_STEP_DEG) + 1,
    )
    if tuple(subset[VARIABLES[0]].shape) != expected_source_shape:
        raise RuntimeError(
            f"unexpected seam-closed ERA5 subset shape {subset[VARIABLES[0]].shape}; "
            f"expected {expected_source_shape}"
        )

    raw_fields = {
        variable: np.asarray(subset[variable].values, dtype="float32")
        for variable in VARIABLES
    }
    metadata_identity_after, _ = source_identity(filesystem)
    chunk_records_after, chunk_identity_hash_after = source_chunk_identities(
        filesystem, dataset
    )
    if metadata_identity_after != metadata_identity:
        raise RuntimeError("ARCO consolidated metadata changed during extraction")
    if (
        chunk_identity_hash_after != chunk_identity_hash
        or chunk_records_after != chunk_records
    ):
        raise RuntimeError("ARCO source chunks changed during extraction")
    data_load_seconds = time.perf_counter() - started - metadata_seconds
    if any(not np.isfinite(field).all() for field in raw_fields.values()):
        raise RuntimeError("ERA5 source subset contains non-finite values")
    if any(
        not np.array_equal(field[..., 0], field[..., -1])
        for field in raw_fields.values()
    ):
        raise RuntimeError("ERA5 source subset does not close the longitude seam")

    plan = interpolation_plan(subset.level.values, PRESSURE_ALTITUDES_FT)
    output_fields = {
        variable: interpolate_pressure_levels(raw_fields[variable], plan)
        for variable in VARIABLES
    }
    if any(not np.isfinite(field).all() for field in output_fields.values()):
        raise RuntimeError("interpolated ERA5 output contains non-finite values")
    if any(
        not np.array_equal(field[..., 0], field[..., -1])
        for field in output_fields.values()
    ):
        raise RuntimeError("interpolated ERA5 output does not close the longitude seam")

    output_times = np.asarray(subset.time.values).astype("datetime64[s]")
    output_unix_seconds = output_times.astype("int64")
    latitudes = np.asarray(subset.latitude.values, dtype="float32")
    longitudes = np.asarray(subset.longitude.values, dtype="float32")
    if output_times.tolist() != np.asarray(TIMES, dtype="datetime64[s]").tolist():
        raise RuntimeError("output times differ from the requested UTC hours")
    if not np.array_equal(
        latitudes,
        np.arange(
            LATITUDE_NORTH_DEG,
            LATITUDE_SOUTH_DEG - GRID_STEP_DEG / 2.0,
            -GRID_STEP_DEG,
            dtype="float32",
        ),
    ):
        raise RuntimeError("latitude coordinates differ from the pinned grid")
    if not np.array_equal(
        longitudes,
        np.arange(
            LONGITUDE_WEST_DEG,
            LONGITUDE_EAST_DEG + GRID_STEP_DEG / 2.0,
            GRID_STEP_DEG,
            dtype="float32",
        ),
    ):
        raise RuntimeError("longitude coordinates differ from the pinned grid")

    run_directory = VOLUME_MOUNT / REMOTE_RUN_DIRECTORY
    run_directory.mkdir(parents=True, exist_ok=True)
    destination = run_directory / f"{run_id}.bin"
    run_manifest_path = run_directory / f"{run_id}.json"
    with tempfile.TemporaryDirectory(prefix=f"mh370-era5-{run_id}-") as scratch:
        scratch_path = Path(scratch) / destination.name
        write_binary(
            scratch_path,
            output_unix_seconds,
            PRESSURE_ALTITUDES_FT,
            latitudes,
            longitudes,
            tuple(output_fields[variable] for variable in VARIABLES),
        )
        temporary = destination.with_suffix(".bin.tmp")
        shutil.copyfile(scratch_path, temporary)
        os.replace(temporary, destination)

    field_statistics = {}
    for source_name, output_name in zip(VARIABLES, VARIABLE_OUTPUT_NAMES, strict=True):
        field = output_fields[source_name]
        field_statistics[output_name] = {
            "minimum": float(field.min()),
            "maximum": float(field.max()),
            "mean": float(field.mean(dtype="float64")),
        }

    maximum_temperature_k = float(np.max(output_fields["temperature"]))
    maximum_wind_m_s = float(
        np.max(
            np.hypot(
                output_fields["u_component_of_wind"].astype("float64"),
                output_fields["v_component_of_wind"].astype("float64"),
            )
        )
    )
    maximum_tas_m_s = COVERAGE_MACH_CAP * math.sqrt(
        DRY_AIR_HEAT_CAPACITY_RATIO
        * ISA["dry_air_gas_constant_j_kg_k"]
        * maximum_temperature_k
    )
    maximum_ground_speed_m_s = maximum_tas_m_s + maximum_wind_m_s
    maximum_reach_nm = (
        maximum_ground_speed_m_s * CONTROL_DURATION_S / METRES_PER_NAUTICAL_MILE
    )
    maximum_latitude_change_deg = math.degrees(
        maximum_reach_nm
        * METRES_PER_NAUTICAL_MILE
        / WGS84_MINIMUM_MERIDIONAL_RADIUS_M
    )

    processing_seconds = time.perf_counter() - started - metadata_seconds - data_load_seconds
    record = {
        "schema_version": "mh370-era5-independent-run-v1",
        "status": "candidate_not_installed",
        "run_id": run_id,
        "retrieved_utc": utc_now(),
        "source": SOURCE,
        "source_access_revision": SOURCE_ACCESS_REVISION,
        "source_consolidated_metadata": metadata_identity,
        "source_attributes": source_attributes,
        "source_variable_metadata": source_variable_metadata,
        "source_chunk_objects": chunk_records,
        "source_chunk_identity_sha256": chunk_identity_hash,
        "source_chunk_compressed_bytes": sum(
            item["size_bytes"] for item in chunk_records
        ),
        "times_utc": list(TIMES),
        "times_unix_s": output_unix_seconds.tolist(),
        "time_basis": "UTC hourly analysis validity time; ERA5 analysis step is zero",
        "source_pressure_levels_hpa": list(SOURCE_PRESSURE_HPA),
        "pressure_altitudes_ft": list(PRESSURE_ALTITUDES_FT),
        "pressure_altitude_interpolation": plan,
        "pressure_altitude_model": {
            "name": "ICAO ISA pressure altitude through the 11 km tropopause",
            "constants": ISA,
            "vertical_interpolation": "linear in natural-log pressure for each field",
            "altitude_interpretation": (
                "pressure altitude, not observed geopotential or geometric height"
            ),
            "lowest_target_note": (
                "500 ft is the lowest near-sea-level target whose ISA pressure "
                "is strictly bracketed by the public 975 and 1000 hPa levels; "
                "0 ft would require extrapolation above 1000 hPa"
            ),
        },
        "latitude_axis": {
            "first_deg": float(latitudes[0]),
            "last_deg": float(latitudes[-1]),
            "count": len(latitudes),
            "step_deg": -GRID_STEP_DEG,
            "orientation": "north_to_south_descending",
        },
        "longitude_axis": {
            "first_deg": float(longitudes[0]),
            "last_deg": float(longitudes[-1]),
            "count": len(longitudes),
            "step_deg": GRID_STEP_DEG,
            "orientation": "west_to_east_ascending; degrees_east; +180 duplicates -180",
        },
        "domain_coverage_contract": {
            "purpose": "broad repeated-manoeuvre MH370 inference from M1822 through M0011",
            "latitude": "complete WGS-84 [-90, 90] support at 0.5 degree spacing",
            "longitude": "complete WGS-84 [-180, 180) query support; the +180 axis endpoint exactly duplicates the -180 physical meridian for non-periodic runtime interpolation",
            "altitude_ft": [float(PRESSURE_ALTITUDES_FT[0]), float(PRESSURE_ALTITUDES_FT[-1])],
            "time_utc": [TIMES[0], TIMES[-1]],
            "boundary_semantics": "a state outside the time or altitude axes is a data-coverage failure, not evidence against its control history",
            "deterministic_reach_bound": {
                "source_mean_latitude_deg": SOURCE_MEAN_LATITUDE_DEG,
                "source_mean_longitude_deg": SOURCE_MEAN_LONGITUDE_DEG,
                "source_position_sd_nm": SOURCE_POSITION_SD_NM,
                "duration_s": CONTROL_DURATION_S,
                "mach_cap": COVERAGE_MACH_CAP,
                "maximum_grid_temperature_k": maximum_temperature_k,
                "maximum_grid_wind_m_s": maximum_wind_m_s,
                "maximum_true_airspeed_m_s": maximum_tas_m_s,
                "maximum_ground_speed_m_s": maximum_ground_speed_m_s,
                "maximum_reach_nm": maximum_reach_nm,
                "maximum_latitude_change_deg_using_minimum_wgs84_meridional_radius": maximum_latitude_change_deg,
                "proof": "ground speed is no greater than Mach times the maximum grid speed of sound plus the maximum grid wind-vector magnitude; the installed spatial grid is global and therefore cannot truncate a valid WGS-84 trajectory regardless of this finite reach bound",
                "source_uncertainty_note": "the Gaussian tangent-plane source draw has mathematically unbounded tails, but the environment spans every valid runtime LatLon; invalid latitude draws are handled by the estimator's declared source-state logic rather than by this grid",
            },
            "coordinate_singularity_caveat": "east/north components and headings are coordinate-singular at the exact geographic poles even though ERA5 values there are finite",
        },
        "variables_in_binary_order": list(VARIABLE_OUTPUT_NAMES),
        "units": {
            "time": "integer Unix seconds in UTC",
            "pressure_altitude": "ft",
            "latitude": "degrees_north",
            "longitude": "degrees_east",
            "temperature_k": "K",
            "wind_east_m_s": "m s^-1; positive eastward",
            "wind_north_m_s": "m s^-1; positive northward",
        },
        "vertical_wind": "not retrieved, inferred, stored, or implied",
        "density_derivation_contract": {
            "stored_in_binary": False,
            "formula": "rho_kg_m3 = target_pressure_hpa * 100 / (R_d * temperature_k)",
            "dry_air_gas_constant_j_kg_k": ISA[
                "dry_air_gas_constant_j_kg_k"
            ],
            "pressure_source": (
                "ISA target pressure recorded for the pressure-altitude axis"
            ),
            "temperature_source": (
                "four-dimensionally interpolated ERA5 temperature from this binary"
            ),
            "humidity": "not applied; dry-air approximation",
        },
        "binary_format": {
            "magic": MAGIC.decode("ascii"),
            "byte_order": "little_endian",
            "axis_order": ["time", "pressure_altitude", "latitude", "longitude"],
            "axis_types": ["int64_unix_seconds", "float32", "float32", "float32"],
            "field_type": "float32",
            "array_memory_order": "C; longitude varies fastest",
            "longitude_seam": "+180 degree column exactly duplicates -180 degrees",
        },
        "source_open_array_shape_time_pressure_lat_lon": list(
            expected_open_source_shape
        ),
        "source_array_shape_time_pressure_lat_lon": list(expected_source_shape),
        "array_shape_time_pressure_altitude_lat_lon": list(
            output_fields[VARIABLES[0]].shape
        ),
        "raw_source_spot_checks": raw_spot_checks(
            raw_fields,
            output_fields,
            plan,
            output_times,
            latitudes,
            longitudes,
        ),
        "field_statistics": field_statistics,
        "output_path": str(REMOTE_RUN_DIRECTORY / f"{run_id}.bin"),
        "output_sha256": sha256(destination),
        "output_bytes": destination.stat().st_size,
        "extractor_sha256": sha256(Path(__file__)),
        "runtime": {
            "modal_cpu_request": 4.0,
            "modal_memory_request_mib": [16_384, 24_576],
            "metadata_and_identity_seconds": metadata_seconds,
            "source_data_load_seconds": data_load_seconds,
            "processing_and_write_seconds": processing_seconds,
            "elapsed_seconds": time.perf_counter() - started,
            "peak_process_rss_bytes": peak_process_rss_bytes(),
            "peak_process_rss_basis": "Linux getrusage(RUSAGE_SELF).ru_maxrss",
        },
    }
    run_manifest_path.write_text(
        json.dumps(record, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    volume.commit()
    os.sync()
    return record


def files_equal(first: Path, second: Path) -> bool:
    if first.stat().st_size != second.stat().st_size:
        return False
    with first.open("rb") as a, second.open("rb") as b:
        while True:
            block_a = a.read(1024 * 1024)
            block_b = b.read(1024 * 1024)
            if block_a != block_b:
                return False
            if not block_a:
                return True


@app.function(
    cpu=1.0,
    memory=1_024,
    timeout=600,
    volumes={str(VOLUME_MOUNT): volume},
)
def finalize(first: dict, second: dict) -> dict:
    volume.reload()
    if first["run_id"] != "independent-a" or second["run_id"] != "independent-b":
        raise RuntimeError("determinism runs have unexpected identifiers")

    equal_keys = (
        "source",
        "source_access_revision",
        "source_consolidated_metadata",
        "source_attributes",
        "source_variable_metadata",
        "source_chunk_objects",
        "source_chunk_identity_sha256",
        "times_utc",
        "times_unix_s",
        "source_pressure_levels_hpa",
        "pressure_altitudes_ft",
        "pressure_altitude_interpolation",
        "latitude_axis",
        "longitude_axis",
        "domain_coverage_contract",
        "variables_in_binary_order",
        "units",
        "raw_source_spot_checks",
        "field_statistics",
        "output_sha256",
        "output_bytes",
        "extractor_sha256",
    )
    for key in equal_keys:
        if first[key] != second[key]:
            raise RuntimeError(f"independent extraction runs disagree on {key}")

    first_binary = VOLUME_MOUNT / first["output_path"]
    second_binary = VOLUME_MOUNT / second["output_path"]
    if not files_equal(first_binary, second_binary):
        raise RuntimeError("independent extraction binaries are not byte-identical")

    destination = VOLUME_MOUNT / REMOTE_BINARY
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination.with_suffix(".bin.tmp")
    shutil.copyfile(first_binary, temporary)
    os.replace(temporary, destination)

    record = {
        key: value
        for key, value in first.items()
        if key
        not in {
            "schema_version",
            "status",
            "run_id",
            "retrieved_utc",
            "output_path",
            "runtime",
        }
    }
    record.update(
        {
            "schema_version": "mh370-era5-runtime-grid-manifest-v3",
            "status": "validated_global_grid",
            "retrieved_utc": first["retrieved_utc"],
            "independently_regenerated_utc": second["retrieved_utc"],
            "retrieval_command": (
                "modal run .sources/ecmwf-era5-weather/code/extract_mh370.py"
            ),
            "remote_download_commands": [
                (
                    "modal volume get --force mh370-environment-v1 "
                    f"{REMOTE_BINARY} .sources/ecmwf-era5-weather/outputs/"
                    "mh370-era5-grid.candidate.bin"
                ),
                (
                    "modal volume get --force mh370-environment-v1 "
                    f"{REMOTE_MANIFEST} .sources/ecmwf-era5-weather/outputs/"
                    "mh370-era5-grid.candidate.manifest.json"
                ),
            ],
            "local_validation_and_install_command": (
                "python3 .sources/ecmwf-era5-weather/code/validate_mh370.py "
                ".sources/ecmwf-era5-weather/outputs/mh370-era5-grid.candidate.bin "
                ".sources/ecmwf-era5-weather/outputs/"
                "mh370-era5-grid.candidate.manifest.json --record "
                ".sources/ecmwf-era5-weather/outputs/mh370-era5-validation.json "
                "--report .sources/ecmwf-era5-weather/outputs/"
                "mh370-era5-validation.html --install-directory inputs/environment"
            ),
            "output_path": str(REMOTE_BINARY),
            "intended_local_path": "inputs/environment/mh370-era5-grid.bin",
            "deterministic_regeneration": {
                "scope": (
                    "binary bytes; run timestamps and runtime measurements in the "
                    "manifest are intentionally run-specific"
                ),
                "independent_remote_runs": 2,
                "byte_for_byte_equal": True,
                "runs": [
                    {
                        "run_id": item["run_id"],
                        "retrieved_utc": item["retrieved_utc"],
                        "output_sha256": item["output_sha256"],
                        "output_bytes": item["output_bytes"],
                        "runtime": item["runtime"],
                    }
                    for item in (first, second)
                ],
            },
        }
    )
    if sha256(destination) != record["output_sha256"]:
        raise RuntimeError("finalized output hash differs from extraction hash")

    manifest_path = VOLUME_MOUNT / REMOTE_MANIFEST
    manifest_path.write_text(
        json.dumps(record, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    for candidate in (
        first_binary,
        second_binary,
        VOLUME_MOUNT / REMOTE_RUN_DIRECTORY / "independent-a.json",
        VOLUME_MOUNT / REMOTE_RUN_DIRECTORY / "independent-b.json",
        VOLUME_MOUNT / REMOTE_RUN_DIRECTORY / "source-pin-probe.bin",
        VOLUME_MOUNT / REMOTE_RUN_DIRECTORY / "source-pin-probe.json",
    ):
        candidate.unlink(missing_ok=True)
    volume.commit()
    os.sync()
    return record


@app.local_entrypoint()
def main() -> None:
    if EXPECTED_SOURCE_CHUNK_IDENTITY_SHA256 is None:
        raise SystemExit(
            "source chunk identity is not pinned; run the extract function once "
            "with run_id='source-pin-probe', record the returned identity hash, "
            "then set EXPECTED_SOURCE_CHUNK_IDENTITY_SHA256"
        )
    first = extract.remote("independent-a")
    second = extract.remote("independent-b")
    print(json.dumps(finalize.remote(first, second), indent=2, sort_keys=True))
