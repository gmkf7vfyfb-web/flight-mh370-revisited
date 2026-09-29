#!/usr/bin/env python3
"""Rebuild the canonical global ERA5 grid from the public ARCO store, and verify it.

`extract.py` retrieves the grid on Modal; `extend.py` reuses its pure functions to append an
hour locally. This does the same thing for the whole canonical grid, so a clone with no copy of
`data/era5-wind-temperature.bin` can regenerate it: the selection, the pressure-altitude
interpolation and the binary writer are `extract.py`'s own (`SOURCE`, `SOURCE_PRESSURE_HPA`,
`TIMES`, `PRESSURE_ALTITUDES_FT`, `interpolation_plan`, `interpolate_pressure_levels`,
`write_binary`), imported through `extend.py`'s Modal stub. No new numerical code is introduced
here, so the result is checkable rather than merely plausible: pass `--manifest` and the SHA-256
of the written file is compared with the value recorded when the grid was first validated.

The canonical grid is the 9 hours in `extract.py`'s `TIMES` (2014-03-07T17:00 to
2014-03-08T01:00), 12 pressure altitudes from 500 to 43,000 ft, global at 0.5 degrees:
337,328,648 bytes. The grid the filter actually loads has 2014-03-08T02:00 appended for
end-of-flight paths after 01:00; add it afterwards with
`extend.py OUT.bin FINAL.bin 2014-03-08T02:00:00`, which re-extracts 01:00 and refuses to append
unless it comes back byte-identical.

Transport. `extract.py` and `extend.py` reach the store with gcsfs, whose JSON endpoint is the
path-style host `storage.googleapis.com`. Where that host is unreachable, `--transport https`
reads the same objects from the bucket-qualified host over plain HTTPS instead. Only the
transport differs; the objects, and therefore the bytes, are the same ones, which is what the
SHA-256 comparison establishes.

Usage:
  python .sources/era5-weather/rebuild.py OUT.bin [--transport https|gcs] [--manifest M.json]
"""

import argparse
import hashlib
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import extend as X  # noqa: E402  (stubs modal, then imports extract)
import extract as E  # noqa: E402

def extract_global(transport: str):
    """[field][time, altitude, latitude, longitude] for extract.py's canonical TIMES."""
    import xarray as xr

    ds = X.open_source(transport)
    sub = (ds[list(E.VARIABLES)]
           .sel(time=list(E.TIMES), level=list(E.SOURCE_PRESSURE_HPA),
                latitude=slice(E.LATITUDE_NORTH_DEG, E.LATITUDE_SOUTH_DEG),
                longitude=slice(0.0, 359.75))
           .isel(latitude=slice(None, None, 2), longitude=slice(None, None, 2))
           .transpose("time", "level", "latitude", "longitude"))
    lon = np.asarray(sub.longitude.values, dtype="float64")
    wrapped = (lon + 180.0) % 360.0 - 180.0
    order = np.argsort(wrapped)
    sub = sub.isel(longitude=order).assign_coords(longitude=wrapped[order])
    seam = sub.isel(longitude=slice(0, 1)).assign_coords(longitude=np.asarray([E.LONGITUDE_EAST_DEG]))
    sub = xr.concat((sub, seam), dim="longitude")
    plan = E.interpolation_plan(E.SOURCE_PRESSURE_HPA, E.PRESSURE_ALTITUDES_FT)
    return [E.interpolate_pressure_levels(np.asarray(sub[v].values, dtype="float32"), plan)
            for v in E.VARIABLES]


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("out", type=Path, help="binary to write, e.g. data/era5-wind-temperature.bin")
    parser.add_argument("--transport", choices=("https", "gcs"), default="https",
                        help="https: bucket-qualified host (default); gcs: gcsfs, as extract.py uses")
    parser.add_argument("--manifest", type=Path,
                        help="grid manifest whose output_sha256 the written file must match")
    args = parser.parse_args()

    fields = extract_global(args.transport)
    latitudes = np.arange(E.LATITUDE_NORTH_DEG, E.LATITUDE_SOUTH_DEG - 0.25, -E.GRID_STEP_DEG)
    longitudes = np.arange(E.LONGITUDE_WEST_DEG, E.LONGITUDE_EAST_DEG + 0.25, E.GRID_STEP_DEG)
    times = np.array([X.unix(h) for h in E.TIMES])
    E.write_binary(args.out, times, np.asarray(E.PRESSURE_ALTITUDES_FT, dtype=float),
                   latitudes, longitudes, fields)

    digest = hashlib.sha256(args.out.read_bytes()).hexdigest()
    size = args.out.stat().st_size
    print(f"wrote {args.out}: {size:,} bytes, {len(times)} times x {len(E.PRESSURE_ALTITUDES_FT)} "
          f"altitudes x {len(latitudes)} x {len(longitudes)}")
    print(f"sha256 {digest}")
    for name, field in zip(E.VARIABLE_OUTPUT_NAMES, fields):
        print(f"{name}: min {field.min():.6f} mean {float(field.mean()):.6f} max {field.max():.6f}")

    if args.manifest:
        import json

        recorded = json.loads(args.manifest.read_text())
        expected_digest = recorded["output_sha256"]
        expected_bytes = recorded["output_bytes"]
        if digest == expected_digest and size == expected_bytes:
            print(f"matches {args.manifest}: byte-identical to the validated grid")
            return
        raise SystemExit(
            f"REBUILD DOES NOT MATCH {args.manifest}\n"
            f"  sha256 {digest} (recorded {expected_digest})\n"
            f"  bytes  {size:,} (recorded {expected_bytes:,})\n"
            "The grid is not interchangeable with the one the recorded results used; do not "
            "install it over data/era5-wind-temperature.bin without deciding why it differs.")


if __name__ == "__main__":
    main()
