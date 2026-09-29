#!/usr/bin/env python3
"""Retrieve resumable monthly WAVERYS surface-Stokes subsets with provenance."""

from __future__ import annotations

import argparse
import calendar
import hashlib
import json
import os
import subprocess
from datetime import date, datetime, time, timedelta, timezone
from pathlib import Path

import netCDF4
import numpy as np


PRODUCT_ID = "GLOBAL_MULTIYEAR_WAV_001_032"
DATASET_ID = "cmems_mod_glo_wav_my_0.2deg_PT3H-i"
DATASET_VERSION = "202411"
DATASET_PART = "default"
VARIABLES = ("VSDX", "VSDY")
STANDARD_NAMES = {
    "VSDX": "sea_surface_wave_stokes_drift_x_velocity",
    "VSDY": "sea_surface_wave_stokes_drift_y_velocity",
}
USERNAME_ENV = "COPERNICUSMARINE_SERVICE_USERNAME"
PASSWORD_ENV = "COPERNICUSMARINE_SERVICE_PASSWORD"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def atomic_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    temporary.replace(path)


def month_ranges(first: date, last: date):
    year, month = first.year, first.month
    while (year, month) <= (last.year, last.month):
        month_first = date(year, month, 1)
        month_last = date(year, month, calendar.monthrange(year, month)[1])
        yield max(first, month_first), min(last, month_last)
        if month == 12:
            year, month = year + 1, 1
        else:
            month += 1


def numeric(variable) -> np.ndarray:
    values = variable[:]
    if np.ma.isMaskedArray(values):
        values = values.filled(np.nan)
    return np.asarray(values)


def utc_iso(value) -> str:
    if hasattr(value, "to_pydatetime"):
        value = value.to_pydatetime()
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def expected_times(first: date, last: date) -> list[datetime]:
    start = datetime.combine(first, time(0), tzinfo=timezone.utc)
    end = datetime.combine(last, time(21), tzinfo=timezone.utc)
    count = int((end - start) / timedelta(hours=3)) + 1
    return [start + timedelta(hours=3 * index) for index in range(count)]


def inspect_subset(path: Path, first: date, last: date) -> dict:
    expected = expected_times(first, last)
    with netCDF4.Dataset(path) as dataset:
        for name in ("time", "latitude", "longitude", *VARIABLES):
            if name not in dataset.variables:
                raise ValueError(f"{path} lacks expected variable {name}")
        time_variable = dataset["time"]
        time_units = str(time_variable.units)
        time_calendar = str(getattr(time_variable, "calendar", "standard"))
        timestamps = netCDF4.num2date(
            time_variable[:],
            time_variable.units,
            only_use_cftime_datetimes=False,
        )
        observed = [
            value.replace(tzinfo=timezone.utc) if value.tzinfo is None else value
            for value in timestamps
        ]
        if len(observed) != len(expected) or any(
            actual != wanted for actual, wanted in zip(observed, expected, strict=True)
        ):
            raise ValueError(f"{path} does not contain the expected three-hour times")

        latitudes = numeric(dataset["latitude"]).astype(np.float64)
        longitudes = numeric(dataset["longitude"]).astype(np.float64)
        if np.any(np.diff(latitudes) <= 0.0) or np.any(np.diff(longitudes) <= 0.0):
            raise ValueError(f"{path} has unordered spatial coordinates")

        finite = {}
        component_metadata = {}
        for component in VARIABLES:
            variable = dataset[component]
            if variable.dimensions != ("time", "latitude", "longitude"):
                raise ValueError(
                    f"{path} {component} dimensions are {variable.dimensions}"
                )
            if variable.units not in {"m s-1", "m/s", "m s**-1"}:
                raise ValueError(
                    f"{path} {component} has unexpected units {variable.units!r}"
                )
            if getattr(variable, "standard_name", None) != STANDARD_NAMES[component]:
                raise ValueError(f"{path} {component} has an unexpected standard name")
            finite_count = 0
            value_count = 0
            for index in range(len(timestamps)):
                values = numeric(variable[index, :, :])
                finite_count += int(np.count_nonzero(np.isfinite(values)))
                value_count += values.size
            finite[component] = finite_count / value_count
            component_metadata[component] = {
                "units": str(variable.units),
                "standard_name": str(variable.standard_name),
                "long_name": str(getattr(variable, "long_name", "")),
                "cell_methods": str(getattr(variable, "cell_methods", "")),
            }

        attributes = {
            name: str(dataset.getncattr(name))
            for name in (
                "title",
                "institution",
                "product",
                "dataset",
                "version",
                "Conventions",
                "copernicusmarine_version",
            )
            if name in dataset.ncattrs()
        }

    return {
        "path": str(path.resolve()),
        "sha256": sha256(path),
        "bytes": path.stat().st_size,
        "time_count": len(timestamps),
        "first_time_utc": utc_iso(timestamps[0]),
        "last_time_utc": utc_iso(timestamps[-1]),
        "time_units": time_units,
        "time_calendar": time_calendar,
        "latitude_count": len(latitudes),
        "longitude_count": len(longitudes),
        "actual_bounds_degrees": {
            "south": float(latitudes[0]),
            "north": float(latitudes[-1]),
            "west": float(longitudes[0]),
            "east": float(longitudes[-1]),
        },
        "spacing_degrees": {
            "latitude_median": float(np.median(np.diff(latitudes))),
            "longitude_median": float(np.median(np.diff(longitudes))),
        },
        "finite_fraction_including_land": finite,
        "components": component_metadata,
        "global_attributes": attributes,
    }


def toolbox_version(toolbox: Path) -> str:
    result = subprocess.run(
        [str(toolbox), "--version"],
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip() or result.stderr.strip()


def command_for(
    toolbox: Path,
    output: Path,
    filename: str,
    first: date,
    last: date,
    bounds: dict,
) -> list[str]:
    start = datetime.combine(first, time(0), tzinfo=timezone.utc).isoformat()
    end = datetime.combine(last, time(21), tzinfo=timezone.utc).isoformat()
    return [
        str(toolbox),
        "subset",
        "--dataset-id",
        DATASET_ID,
        "--dataset-version",
        DATASET_VERSION,
        "--dataset-part",
        DATASET_PART,
        "--variable",
        "VSDX",
        "--variable",
        "VSDY",
        "--start-datetime",
        start,
        "--end-datetime",
        end,
        "--minimum-longitude",
        str(bounds["west"]),
        "--maximum-longitude",
        str(bounds["east"]),
        "--minimum-latitude",
        str(bounds["south"]),
        "--maximum-latitude",
        str(bounds["north"]),
        "--coordinates-selection-method",
        "outside",
        "--output-directory",
        str(output.resolve()),
        "--output-filename",
        filename,
        "--file-format",
        "netcdf",
        "--netcdf-compression-level",
        "4",
        "--disable-progress-bar",
        "--log-level",
        "ERROR",
        "--raise-if-updating",
    ]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--manifest", type=Path)
    parser.add_argument(
        "--toolbox", type=Path, default=Path(".venv/bin/copernicusmarine")
    )
    parser.add_argument("--start", type=date.fromisoformat, default=date(2014, 3, 7))
    parser.add_argument("--end", type=date.fromisoformat, default=date(2015, 7, 30))
    parser.add_argument("--west", type=float, default=10.0)
    parser.add_argument("--east", type=float, default=150.0)
    parser.add_argument("--south", type=float, default=-50.0)
    parser.add_argument("--north", type=float, default=30.0)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if args.start > args.end:
        parser.error("start date must not follow end date")
    if not (args.west < args.east and args.south < args.north):
        parser.error("spatial bounds are unordered")
    toolbox = args.toolbox.resolve()
    if not toolbox.is_file():
        parser.error(f"Copernicus Marine Toolbox is absent: {toolbox}")
    if not args.dry_run and not (
        os.environ.get(USERNAME_ENV) and os.environ.get(PASSWORD_ENV)
    ):
        parser.error(
            f"set {USERNAME_ENV} and {PASSWORD_ENV} through a secure environment file"
        )

    args.output.mkdir(parents=True, exist_ok=True)
    manifest_path = args.manifest or args.output / "retrieval-manifest.json"
    bounds = {
        "west": args.west,
        "east": args.east,
        "south": args.south,
        "north": args.north,
    }
    payload = {
        "schema": "mh370-cmems-waverys-retrieval-v1",
        "product_id": PRODUCT_ID,
        "dataset_id": DATASET_ID,
        "dataset_version": DATASET_VERSION,
        "dataset_part": DATASET_PART,
        "toolbox_version": toolbox_version(toolbox),
        "credential_environment_variables": [USERNAME_ENV, PASSWORD_ENV],
        "requested_variables": list(VARIABLES),
        "component_units": {
            "VSDX": "m s-1 east surface Stokes",
            "VSDY": "m s-1 north surface Stokes",
        },
        "time_basis": "three-hourly instantaneous analyses on a Gregorian UTC axis",
        "requested_period": {
            "start": args.start.isoformat(),
            "end": args.end.isoformat(),
        },
        "requested_bounds_degrees": bounds,
        "selection_method": "outside",
        "service_selection": "Copernicus Marine Toolbox automatic ARCO selection",
        "file_format": "NetCDF4 with compression level 4",
        "official_product": "https://data.marine.copernicus.eu/product/GLOBAL_MULTIYEAR_WAV_001_032/description",
        "official_user_manual": "https://documentation.marine.copernicus.eu/PUM/CMEMS-GLO-PUM-001-032.pdf",
        "official_subset_method": "https://help.marine.copernicus.eu/en/articles/7972861-copernicus-marine-toolbox-cli-subset",
        "files": [],
        "limitations": [
            "WAVERYS is assimilative through significant-wave-height observations and uses GLORYS12 currents in the wave model.",
            "VSDX/VSDY are surface Stokes velocities; their application to a partially submerged flaperon requires an explicit response sensitivity.",
            "Direct aerodynamic windage and object-specific residual leeway remain distinct from this field.",
        ],
    }
    existing_records = {}
    if manifest_path.is_file():
        existing = json.loads(manifest_path.read_text(encoding="utf-8"))
        if existing.get("schema") != payload["schema"]:
            raise ValueError(f"unsupported existing manifest: {manifest_path}")
        for field in (
            "product_id",
            "dataset_id",
            "dataset_version",
            "dataset_part",
            "requested_variables",
            "requested_period",
            "requested_bounds_degrees",
        ):
            if existing.get(field) != payload[field]:
                raise ValueError(
                    f"existing manifest {field} differs from the current request"
                )
        existing_records = {
            record["month"]: record for record in existing.get("files", [])
        }

    for first, last in month_ranges(args.start, args.end):
        month = first.strftime("%Y-%m")
        filename = f"cmems-waverys-stokes-{month}.nc"
        path = args.output / filename
        temporary_name = f"{filename}.partial.nc"
        temporary_path = args.output / temporary_name
        command = command_for(
            toolbox, args.output, temporary_name, first, last, bounds
        )
        if args.dry_run:
            result = subprocess.run(
                [*command, "--dry-run"],
                check=True,
                capture_output=True,
                text=True,
            )
            print(result.stdout.strip())
            break
        if path.is_file():
            inspection = inspect_subset(path, first, last)
            prior = existing_records.get(month)
            if prior is not None and prior["sha256"] != inspection["sha256"]:
                raise ValueError(f"existing {month} file differs from its manifest")
            response = prior.get("toolbox_response") if prior else None
        else:
            temporary_path.unlink(missing_ok=True)
            try:
                result = subprocess.run(
                    command, check=True, capture_output=True, text=True
                )
            except subprocess.CalledProcessError as error:
                detail = (error.stderr or error.stdout or "no diagnostic").strip()
                raise RuntimeError(
                    f"toolbox retrieval failed for {month}: {detail}"
                ) from None
            if not temporary_path.is_file():
                raise RuntimeError(
                    f"toolbox succeeded but did not create {temporary_path}"
                )
            inspect_subset(temporary_path, first, last)
            temporary_path.replace(path)
            inspection = inspect_subset(path, first, last)
            response = json.loads(result.stdout) if result.stdout.strip() else None
        payload["files"].append(
            {
                "month": month,
                "requested_start": first.isoformat(),
                "requested_end": last.isoformat(),
                "command": command,
                "toolbox_response": response,
                **inspection,
            }
        )
        atomic_json(manifest_path, payload)
        print(
            f"month={month} times={inspection['time_count']} bytes={inspection['bytes']} "
            f"sha256={inspection['sha256']}"
        )

    if not args.dry_run:
        payload["summary"] = {
            "file_count": len(payload["files"]),
            "time_count": sum(record["time_count"] for record in payload["files"]),
            "bytes": sum(record["bytes"] for record in payload["files"]),
            "all_file_sha256": hashlib.sha256(
                "".join(record["sha256"] for record in payload["files"]).encode(
                    "ascii"
                )
            ).hexdigest(),
        }
        atomic_json(manifest_path, payload)


if __name__ == "__main__":
    main()
