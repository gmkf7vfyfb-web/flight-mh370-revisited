#!/usr/bin/env python3
"""Retrieve resumable native-grid GOFS 3.1 reanalysis surface-current tiles.

The canonical request covers the complete preparation domain at the server's
native horizontal spacing. `timeStride=8` is explicitly an approximately daily
subsample of available 3-hour analyses, not a daily mean. Missing upstream
analyses therefore remain time gaps and are summarized in the manifest.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import hashlib
import json
import os
import threading
import time
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

import netCDF4
import numpy as np


DATASET = "GOFS 3.1-like HYCOM+NCODA GLBv0.08 experiment 53.X reanalysis"
BASE = "https://ncss.hycom.org/thredds/ncss/grid/GLBv0.08/expt_53.X/data"
CANONICAL_PERIODS = {
    2014: ("2014-03-07T00:00:00Z", "2014-12-31T00:00:00Z"),
    2015: ("2015-01-01T00:00:00Z", "2015-07-30T00:00:00Z"),
}
# Exact native analyses inserted after auditing the complete three-hour time
# axis. They repair gaps created by the stride-8 sampling (not by absent
# upstream analyses), keeping every retained interval at or below 30 hours.
SUPPLEMENTAL_TIMES = {
    2014: (
        "2014-06-29T12:00:00Z",
        "2014-12-31T06:00:00Z",
    ),
}
NETCDF_LOCK = threading.Lock()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def boundaries(start: float, end: float, width: float) -> list[tuple[float, float]]:
    result = []
    current = start
    while current < end:
        next_value = min(current + width, end)
        result.append((current, next_value))
        current = next_value
    return result


def coordinate_label(value: float, positive: str, negative: str) -> str:
    direction = positive if value >= 0 else negative
    return f"{direction}{abs(value):05.1f}".replace(".", "p")


def request(
    year: int,
    west: float,
    east: float,
    south: float,
    north: float,
    exact_time: str | None = None,
) -> tuple[str, str]:
    start, end = CANONICAL_PERIODS[year]
    parameters = [
        ("var", "water_u"),
        ("var", "water_v"),
        ("north", str(north)),
        ("south", str(south)),
        ("east", str(east)),
        ("west", str(west)),
        ("disableProjSubset", "on"),
        ("horizStride", "1"),
        ("vertCoord", "0"),
        ("accept", "netcdf4"),
    ]
    if exact_time is None:
        parameters.extend(
            [
                ("time_start", start),
                ("time_end", end),
                ("timeStride", "8"),
            ]
        )
        prefix = str(year)
    else:
        parameters.append(("time", exact_time))
        prefix = "supplement_" + exact_time.replace("-", "").replace(":", "")
    url = f"{BASE}/{year}?{urllib.parse.urlencode(parameters)}"
    label = "_".join(
        [
            prefix,
            coordinate_label(west, "E", "W"),
            coordinate_label(east, "E", "W"),
            coordinate_label(south, "N", "S"),
            coordinate_label(north, "N", "S"),
        ]
    )
    return label + ".nc", url


def inspect_unlocked(path: Path, url: str) -> dict[str, object]:
    with netCDF4.Dataset(path) as dataset:
        if not {"water_u", "water_v", "time", "depth", "lat", "lon"}.issubset(
            dataset.variables
        ):
            raise ValueError(f"{path} lacks required native-HYCOM variables")
        east = dataset["water_u"]
        north = dataset["water_v"]
        if (
            east.dimensions != ("time", "depth", "lat", "lon")
            or north.dimensions != east.dimensions
            or len(dataset["depth"]) != 1
            or float(dataset["depth"][0]) != 0.0
            or east.units != "m/s"
            or north.units != "m/s"
        ):
            raise ValueError(f"{path} has unexpected dimensions, depth, or units")
        time_variable = dataset["time"]
        times = np.asarray(time_variable[:], dtype=np.float64)
        dates = netCDF4.num2date(
            times,
            time_variable.units,
            only_use_cftime_datetimes=False,
        )
        gaps = np.diff(times)
        gap_counts = {
            f"{gap:g}_hours": int(np.count_nonzero(np.isclose(gaps, gap)))
            for gap in sorted(set(gaps.tolist()))
        }
        latitudes = np.asarray(dataset["lat"][:], dtype=np.float64)
        longitudes = np.asarray(dataset["lon"][:], dtype=np.float64)
        return {
            "path": str(path),
            "request_url": url,
            "size_bytes": path.stat().st_size,
            "sha256": sha256(path),
            "shape": list(east.shape),
            "time_units": time_variable.units,
            "time_count": len(times),
            "first_time_utc": dates[0].isoformat() + "Z",
            "last_time_utc": dates[-1].isoformat() + "Z",
            "time_gap_counts": gap_counts,
            "latitude_bounds_deg": [float(latitudes[0]), float(latitudes[-1])],
            "longitude_bounds_deg": [float(longitudes[0]), float(longitudes[-1])],
            "median_latitude_spacing_deg": float(np.median(np.diff(latitudes))),
            "median_longitude_spacing_deg": float(np.median(np.diff(longitudes))),
            "component_units": {"water_u": east.units, "water_v": north.units},
        }


def inspect(path: Path, url: str) -> dict[str, object]:
    # The linked HDF5/netCDF library is not thread-safe on every supported
    # host. Network transfers remain concurrent; local structural inspection
    # is serialized to avoid nondeterministic native-library crashes.
    with NETCDF_LOCK:
        return inspect_unlocked(path, url)


def retrieve(target: Path, url: str, retries: int) -> dict[str, object]:
    if target.exists():
        try:
            return inspect(target, url)
        except Exception:
            target.unlink()
    temporary = target.with_suffix(target.suffix + ".part")
    for attempt in range(1, retries + 1):
        try:
            request_object = urllib.request.Request(
                url,
                headers={"User-Agent": "MH370-ocean-drift-input-preparation/1"},
            )
            with urllib.request.urlopen(request_object, timeout=900) as response:
                if response.status != 200:
                    raise RuntimeError(f"HTTP status {response.status}")
                with temporary.open("wb") as stream:
                    while block := response.read(1024 * 1024):
                        stream.write(block)
            os.replace(temporary, target)
            return inspect(target, url)
        except Exception:
            temporary.unlink(missing_ok=True)
            if attempt == retries:
                raise
            time.sleep(5 * attempt)
    raise AssertionError("unreachable")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--retries", type=int, default=3)
    parser.add_argument("--west", type=float, default=10.0)
    parser.add_argument("--east", type=float, default=150.0)
    parser.add_argument("--south", type=float, default=-50.0)
    parser.add_argument("--north", type=float, default=30.0)
    parser.add_argument("--tile-degrees", type=float, default=20.0)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    if (
        args.workers <= 0
        or args.retries <= 0
        or args.west >= args.east
        or args.south >= args.north
        or args.tile_degrees <= 0
    ):
        parser.error("invalid worker, retry, domain, or tile arguments")

    args.output.mkdir(parents=True, exist_ok=True)
    requests = []
    for year in CANONICAL_PERIODS:
        for west, east in boundaries(args.west, args.east, args.tile_degrees):
            for south, north in boundaries(args.south, args.north, args.tile_degrees):
                filename, url = request(year, west, east, south, north)
                requests.append(("primary", args.output / filename, url))
    for year, times in SUPPLEMENTAL_TIMES.items():
        for exact_time in times:
            for west, east in boundaries(args.west, args.east, args.tile_degrees):
                for south, north in boundaries(args.south, args.north, args.tile_degrees):
                    filename, url = request(
                        year, west, east, south, north, exact_time=exact_time
                    )
                    requests.append(("supplemental", args.output / filename, url))
    if args.dry_run:
        print("\n".join(url for _, _, url in requests))
        return

    started = datetime.now(timezone.utc)
    records = {"primary": [], "supplemental": []}
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as executor:
        futures = {
            executor.submit(retrieve, path, url, args.retries): (kind, path)
            for kind, path, url in requests
        }
        for future in concurrent.futures.as_completed(futures):
            kind, _ = futures[future]
            record = future.result()
            records[kind].append(record)
            print(
                f"kind={kind} retrieved={Path(record['path']).name} bytes={record['size_bytes']} "
                f"sha256={record['sha256']}",
                flush=True,
            )
    for values in records.values():
        values.sort(key=lambda item: str(item["path"]))
    manifest = {
        "schema": "mh370-native-hycom-retrieval-v2",
        "dataset": DATASET,
        "dataset_documentation": "https://www.hycom.org/dataserver/gofs-3pt1/reanalysis",
        "catalogs": {
            "2014": "https://tds.hycom.org/thredds/catalogs/GLBv0.08/expt_53.X.html?dataset=GLBv0.08-expt_53.X-2014",
            "2015": "https://tds.hycom.org/thredds/catalogs/GLBv0.08/expt_53.X.html?dataset=GLBv0.08-expt_53.X-2015",
        },
        "retrieval_started_utc": started.isoformat(),
        "retrieval_completed_utc": datetime.now(timezone.utc).isoformat(),
        "requested_domain_degrees": {
            "west": args.west,
            "east": args.east,
            "south": args.south,
            "north": args.north,
        },
        "requested_periods": CANONICAL_PERIODS,
        "variables": ["water_u", "water_v"],
        "surface_depth_m": 0.0,
        "horizontal_stride": 1,
        "time_stride_available_three_hour_analyses": 8,
        "time_sampling_limitation": "Approximately daily subsample, not a daily mean; upstream missing analyses cause variable phase changes.",
        "full_time_axis_audit": {
            "opendap_2014": "https://tds.hycom.org/thredds/dodsC/GLBv0.08/expt_53.X/data/2014.ascii?time",
            "opendap_2015": "https://tds.hycom.org/thredds/dodsC/GLBv0.08/expt_53.X/data/2015.ascii?time",
            "retrieved_ascii_sha256": {
                "2014": "41e08872079fcb5f3feb9984d99d1fe44ddbf0ebdb63d6375310274124b7f1de",
                "2015": "ce11abd49a261719da1a143d0a14117f87a1f34a1e0c0a87211cd0f5be708838",
            },
            "available_time_counts": {"2014": 2857, "2015": 2861},
            "available_gap_counts_hours": {
                "2014": {"3": 2805, "6": 49, "9": 1, "27": 1},
                "2015": {"3": 2810, "6": 49, "9": 1},
            },
            "finding": "The stride-8 sequence's 48 h and 54 h gaps contained available three-hour analyses; one exact analysis was inserted into each gap so the retained maximum gap is 30 h.",
        },
        "supplemental_times": SUPPLEMENTAL_TIMES,
        "primary_tile_count": len(records["primary"]),
        "supplemental_tile_count": len(records["supplemental"]),
        "tile_count": len(records["primary"]) + len(records["supplemental"]),
        "tiles": records["primary"],
        "supplemental_tiles": records["supplemental"],
    }
    manifest_path = args.output / "retrieval-manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(
        f"manifest={manifest_path} primary_tiles={len(records['primary'])} "
        f"supplemental_tiles={len(records['supplemental'])}",
        flush=True,
    )


if __name__ == "__main__":
    main()
