#!/usr/bin/env python3
"""Retrieve resumable monthly GLORYS12 surface-current subsets with provenance."""

from __future__ import annotations

import argparse
import calendar
import hashlib
import json
import os
import subprocess
from datetime import date, datetime, time, timezone
from pathlib import Path

import netCDF4
import numpy as np


PRODUCT_ID = "GLOBAL_MULTIYEAR_PHY_001_030"
DATASET_ID = "cmems_mod_glo_phy_my_0.083deg_P1D-m"
VARIABLES = ("uo", "vo")
SURFACE_DEPTH_METRES = 0.49402499198913574
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


def inspect_subset(path: Path, expected_first: date, expected_last: date) -> dict:
    with netCDF4.Dataset(path) as dataset:
        for name in ("time", "depth", "latitude", "longitude", *VARIABLES):
            if name not in dataset.variables:
                raise ValueError(f"{path} lacks expected variable {name}")
        time_variable = dataset["time"]
        time_units = str(time_variable.units)
        timestamps = netCDF4.num2date(
            time_variable[:],
            time_variable.units,
            only_use_cftime_datetimes=False,
        )
        expected_count = (expected_last - expected_first).days + 1
        if len(timestamps) != expected_count:
            raise ValueError(
                f"{path} has {len(timestamps)} times, expected {expected_count}"
            )
        observed_dates = [value.date() for value in timestamps]
        expected_dates = [
            date.fromordinal(expected_first.toordinal() + offset)
            for offset in range(expected_count)
        ]
        if observed_dates != expected_dates:
            raise ValueError(f"{path} does not contain the expected daily dates")

        latitudes = numeric(dataset["latitude"]).astype(np.float64)
        longitudes = numeric(dataset["longitude"]).astype(np.float64)
        depths = numeric(dataset["depth"]).astype(np.float64)
        if (
            len(depths) != 1
            or depths[0] < 0.0
            or depths[0] > 1.0
            or np.any(np.diff(latitudes) <= 0.0)
            or np.any(np.diff(longitudes) <= 0.0)
        ):
            raise ValueError(f"{path} has unexpected surface or spatial coordinates")

        expected_dimensions = ("time", "depth", "latitude", "longitude")
        finite = {}
        component_metadata = {}
        for component in VARIABLES:
            variable = dataset[component]
            if variable.dimensions != expected_dimensions:
                raise ValueError(
                    f"{path} {component} dimensions are {variable.dimensions}"
                )
            units = getattr(variable, "units", "")
            if units not in {"m s-1", "m/s", "m s**-1"}:
                raise ValueError(f"{path} {component} has unexpected units {units!r}")
            finite_count = 0
            value_count = 0
            for index in range(len(timestamps)):
                values = numeric(variable[index, 0, :, :])
                finite_count += int(np.count_nonzero(np.isfinite(values)))
                value_count += values.size
            finite[component] = finite_count / value_count
            component_metadata[component] = {
                "units": units,
                "standard_name": getattr(variable, "standard_name", None),
                "long_name": getattr(variable, "long_name", None),
            }

        attributes = {}
        for name in ("title", "institution", "source", "product", "Conventions"):
            if name in dataset.ncattrs():
                attributes[name] = str(dataset.getncattr(name))

    return {
        "path": str(path.resolve()),
        "sha256": sha256(path),
        "bytes": path.stat().st_size,
        "time_count": len(timestamps),
        "first_time_utc": utc_iso(timestamps[0]),
        "last_time_utc": utc_iso(timestamps[-1]),
        "time_units": time_units,
        "surface_depth_m": float(depths[0]),
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
    end = datetime.combine(last, time(0), tzinfo=timezone.utc).isoformat()
    return [
        str(toolbox),
        "subset",
        "--dataset-id",
        DATASET_ID,
        "--variable",
        "uo",
        "--variable",
        "vo",
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
        "--minimum-depth",
        str(SURFACE_DEPTH_METRES),
        "--maximum-depth",
        str(SURFACE_DEPTH_METRES),
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
        "schema": "mh370-cmems-glorys12-retrieval-v1",
        "product_id": PRODUCT_ID,
        "dataset_id": DATASET_ID,
        "toolbox_version": toolbox_version(toolbox),
        "credential_environment_variables": [USERNAME_ENV, PASSWORD_ENV],
        "requested_variables": list(VARIABLES),
        "component_units": {"uo": "m s-1 east", "vo": "m s-1 north"},
        "time_basis": "upstream daily field labelled at 00:00 UTC; averaging semantics preserved from source metadata",
        "requested_period": {
            "start": args.start.isoformat(),
            "end": args.end.isoformat(),
        },
        "requested_bounds_degrees": bounds,
        "requested_depth_metres": [
            SURFACE_DEPTH_METRES,
            SURFACE_DEPTH_METRES,
        ],
        "selection_method": "outside",
        "file_format": "NetCDF4 with compression level 4",
        "official_product": "https://data.marine.copernicus.eu/product/GLOBAL_MULTIYEAR_PHY_001_030/description",
        "official_user_manual": "https://documentation.marine.copernicus.eu/PUM/CMEMS-GLO-PUM-001-030.pdf",
        "official_subset_method": "https://help.marine.copernicus.eu/en/articles/7972861-copernicus-marine-toolbox-cli-subset",
        "files": [],
        "limitations": [
            "GLORYS12V1 is assimilative; drifter validation is not guaranteed held out.",
            "Only ocean current uo/vo are retrieved here. Stokes drift and direct windage remain distinct inputs.",
            "Acceptance as the primary family requires the same all-path predictive and source-stability diagnostics as native HYCOM.",
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
            "requested_variables",
            "requested_period",
            "requested_bounds_degrees",
            "requested_depth_metres",
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
        filename = f"cmems-glorys12-surface-{month}.nc"
        path = args.output / filename
        command = command_for(toolbox, args.output, filename, first, last, bounds)
        if args.dry_run:
            try:
                result = subprocess.run(
                    [*command, "--dry-run"],
                    check=True,
                    capture_output=True,
                    text=True,
                )
            except subprocess.CalledProcessError as error:
                detail = (error.stderr or error.stdout or "no diagnostic").strip()
                raise RuntimeError(f"toolbox dry-run failed for {month}: {detail}") from None
            print(result.stdout.strip())
            break
        if path.is_file():
            inspection = inspect_subset(path, first, last)
            prior = existing_records.get(month)
            if prior is not None and prior["sha256"] != inspection["sha256"]:
                raise ValueError(f"existing {month} file differs from its manifest")
        else:
            try:
                result = subprocess.run(
                    command, check=True, capture_output=True, text=True
                )
            except subprocess.CalledProcessError as error:
                detail = (error.stderr or error.stdout or "no diagnostic").strip()
                raise RuntimeError(f"toolbox retrieval failed for {month}: {detail}") from None
            if not path.is_file():
                raise RuntimeError(
                    f"toolbox succeeded but did not create {path}: {result.stdout.strip()}"
                )
            inspection = inspect_subset(path, first, last)
        payload["files"].append(
            {
                "month": month,
                "requested_start": first.isoformat(),
                "requested_end": last.isoformat(),
                "command": command,
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
                "".join(record["sha256"] for record in payload["files"]).encode("ascii")
            ).hexdigest(),
        }
        atomic_json(manifest_path, payload)


if __name__ == "__main__":
    main()
