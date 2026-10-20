#!/usr/bin/env python3
"""Append hours to the ERA5 grid locally, with extract.py's own selection and interpolation.

Usage: .venv/bin/python .sources/era5-weather/extend.py GRID.bin OUT.bin HOUR_UTC [HOUR_UTC ...]
         e.g. extend.py data/era5-wind-temperature.bin /tmp/era5.bin 2014-03-08T02:00:00
       .venv/bin/python .sources/era5-weather/extend.py region OUT.bin LAT_S LAT_N LON_W LON_E HOUR_UTC ...
         a regional grid in the same format, e.g. for the MH371 control:
         extend.py region data/mh371/era5-wind-temperature.bin -20 60 60 150 2014-03-07T01:00:00 ... T08:00:00

extract.py runs on Modal with two independent reads; this reads the same public ARCO ERA5
store directly (xarray + gcsfs, anonymous) and reuses extract.py's constants,
interpolation_plan, interpolate_pressure_levels and write_binary, so an appended hour is
built exactly as the canonical ones were. Before appending, it re-extracts the grid's last
hour and requires it to be byte-identical to the stored one; otherwise it stops.
Requires xarray, zarr and gcsfs in the venv.
"""

import os
import struct
import sys
import types
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

# extract.py builds its Modal app at import; a stub lets its pure functions be reused here.
modal = types.ModuleType("modal")


class _Stub:
    def __getattr__(self, _):
        return self

    def __call__(self, *args, **kwargs):
        return args[0] if len(args) == 1 and callable(args[0]) and not kwargs else self


for name in ("Image", "App", "Volume", "Secret"):
    setattr(modal, name, _Stub())
sys.modules["modal"] = modal
sys.path.insert(0, str(Path(__file__).resolve().parent))
import extract as E  # noqa: E402


def read_grid(path):
    b = Path(path).read_bytes()
    nt, na, ny, nx = struct.unpack("<4I", b[8:24])
    o = 24
    times = np.frombuffer(b, "<i8", nt, o); o += 8 * nt
    alts = np.frombuffer(b, "<f4", na, o); o += 4 * na
    lats = np.frombuffer(b, "<f4", ny, o); o += 4 * ny
    lons = np.frombuffer(b, "<f4", nx, o); o += 4 * nx
    n = nt * na * ny * nx
    fields = [np.frombuffer(b, "<f4", n, o + 4 * n * k).reshape(nt, na, ny, nx) for k in range(3)]
    return times, alts, lats, lons, fields


BUCKET_HOST = "gcp-public-data-arco-era5.storage.googleapis.com"
# "gcs" is extract.py's own transport (gcsfs, whose JSON endpoint is the path-style host
# storage.googleapis.com); "https" reads the same objects from the bucket-qualified host, for
# networks where the path-style host is unreachable. Override with MH370_ERA5_TRANSPORT.
TRANSPORT = os.environ.get("MH370_ERA5_TRANSPORT", "https")


def open_source(transport=None):
    """The ARCO ERA5 store. Same objects either way; only the transport differs."""
    import xarray as xr

    transport = transport or TRANSPORT
    # aiohttp, under both transports, ignores HTTP(S)_PROXY unless told to trust the environment.
    # Without this, a proxied network with no direct DNS fails in a way that looks like an
    # unreachable store rather than an unconfigured client.
    client_kwargs = {"trust_env": True}
    if transport == "gcs":
        return xr.open_zarr(E.SOURCE, chunks=None, consolidated=True,
                            storage_options={"token": "anon", "cache_timeout": 0,
                                             "skip_instance_cache": True,
                                             "session_kwargs": client_kwargs})
    import fsspec

    # Consolidated metadata means no directory listing is needed, which is what makes a plain
    # HTTP read of a Zarr store workable.
    prefix = E.SOURCE.removeprefix("gs://").split("/", 1)[1]
    fs = fsspec.filesystem("https", client_kwargs=client_kwargs)
    return xr.open_zarr(fs.get_mapper(f"https://{BUCKET_HOST}/{prefix}"), chunks=None, consolidated=True)


def extract_hours(hours):
    """[field][time, alt, lat, lon] for the given UTC hours, as in extract.extract (cruise domain)."""
    import xarray as xr

    ds = open_source()
    sub = (ds[list(E.VARIABLES)]
           .sel(time=list(hours), level=list(E.SOURCE_PRESSURE_HPA),
                latitude=slice(E.LATITUDE_NORTH_DEG, E.LATITUDE_SOUTH_DEG), longitude=slice(0.0, 359.75))
           .isel(latitude=slice(None, None, 2), longitude=slice(None, None, 2))
           .transpose("time", "level", "latitude", "longitude"))
    lon = np.asarray(sub.longitude.values, dtype="float64")
    wrapped = (lon + 180.0) % 360.0 - 180.0
    order = np.argsort(wrapped)
    sub = sub.isel(longitude=order).assign_coords(longitude=wrapped[order])
    seam = sub.isel(longitude=slice(0, 1)).assign_coords(longitude=np.asarray([E.LONGITUDE_EAST_DEG]))
    sub = xr.concat((sub, seam), dim="longitude")
    plan = E.interpolation_plan(E.SOURCE_PRESSURE_HPA, E.PRESSURE_ALTITUDES_FT)
    return [E.interpolate_pressure_levels(np.asarray(sub[v].values, dtype="float32"), plan) for v in E.VARIABLES]


def unix(hour):
    return int(datetime.fromisoformat(hour).replace(tzinfo=timezone.utc).timestamp())


def region(out, lat_s, lat_n, lon_w, lon_e, hours):
    """Same selection and interpolation as the global grid, cut to a latitude/longitude box."""
    import extract as ex

    lats = np.arange(ex.LATITUDE_NORTH_DEG, ex.LATITUDE_SOUTH_DEG - 0.25, -ex.GRID_STEP_DEG)
    lons = np.arange(ex.LONGITUDE_WEST_DEG, ex.LONGITUDE_EAST_DEG + 0.25, ex.GRID_STEP_DEG)
    iy = np.nonzero((lats >= lat_s) & (lats <= lat_n))[0]
    ix = np.nonzero((lons >= lon_w) & (lons <= lon_e))[0]
    fields = [f[:, :, iy][:, :, :, ix] for f in extract_hours(hours)]
    E.write_binary(out, np.array([unix(h) for h in hours]), np.asarray(E.PRESSURE_ALTITUDES_FT, float),
                   lats[iy], lons[ix], fields)
    print(f"wrote {out}: {len(hours)} times x {len(iy)} x {len(ix)}")


def main():
    if sys.argv[1] == "region":
        out, box, hours = Path(sys.argv[2]), [float(v) for v in sys.argv[3:7]], sys.argv[7:]
        return region(out, *box, hours)
    grid, out, hours = sys.argv[1], Path(sys.argv[2]), sys.argv[3:]
    times, alts, lats, lons, fields = read_grid(grid)
    last = datetime.fromtimestamp(int(times[-1]), timezone.utc).strftime("%Y-%m-%dT%H:%M:%S")
    check = extract_hours([last])
    for k, name in enumerate(E.VARIABLES):
        if check[k][0].tobytes() != np.ascontiguousarray(fields[k][-1]).tobytes():
            sys.exit(f"re-extracted {last} {name} differs from the stored grid; not appending")
    print(f"re-extracted {last}: byte-identical to the stored grid")
    if any(unix(h) <= int(times[-1]) for h in hours):
        sys.exit("hours must come after the grid's last time")
    new = extract_hours(hours)
    all_times = np.concatenate([times, [unix(h) for h in hours]])
    joined = [np.concatenate([fields[k], new[k]]) for k in range(3)]
    E.write_binary(out, all_times, alts, lats, lons, joined)
    print(f"wrote {out}: {len(all_times)} times, {all_times[0]}..{all_times[-1]}")


if __name__ == "__main__":
    main()
