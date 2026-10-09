"""Convert a Copernicus Marine surface-current subset (netCDF4/HDF5) into the raw grid that
`GridField::load` reads: little-endian float32 `[time][lat][lon][east, north]`, NaN at land, plus a
JSON manifest. Uses h5py and numpy only.

Time placement: the Toolbox labels each GLORYS12V1 daily mean at 00:00 UTC of the day it averages
(the 2017 product manual describes the same means as midnight to midnight, centred at noon). Each
value is therefore placed at label + 12 h, the centre of its interval. This is PROVISIONAL until the
convention is confirmed with the producer; the alternative reading would shift the field by 12 h.

Usage: python netcdf_to_grid.py <in.nc> <out-stem> <product-id> [--label-is-centre]
"""
import hashlib
import json
import sys
from datetime import datetime, timedelta, timezone

import h5py
import numpy as np

UNITS = {"hours": 3600.0, "days": 86400.0, "seconds": 1.0, "minutes": 60.0}


def decoded(var):
    raw = var[...]
    fill = var.attrs.get("_FillValue")
    out = raw.astype(np.float64) * float(var.attrs.get("scale_factor", [1.0])[0]) + float(var.attrs.get("add_offset", [0.0])[0])
    if fill is not None:
        out[raw == fill[0]] = np.nan
    return out


def main():
    src, stem, product = sys.argv[1], sys.argv[2], sys.argv[3]
    label_is_centre = "--label-is-centre" in sys.argv
    with h5py.File(src, "r") as f:
        units = f["time"].attrs["units"]
        units = units.decode() if isinstance(units, bytes) else units
        step, _, origin = units.split(" ", 2)
        t0 = datetime.fromisoformat(origin.strip()).replace(tzinfo=timezone.utc)
        labels = [t0 + timedelta(seconds=float(v) * UNITS[step]) for v in f["time"][:]]
        shift = 0.0 if label_is_centre else 43200.0
        times = [d.timestamp() + shift for d in labels]
        lon = f["longitude"][:].astype(np.float64)
        lat = f["latitude"][:].astype(np.float64)
        u = decoded(f["uo"])[:, 0]
        v = decoded(f["vo"])[:, 0]
    data = np.stack([u, v], axis=-1).astype("<f4")  # [time][lat][lon][2]
    data.tofile(stem + ".f32")
    sha = hashlib.sha256(open(src, "rb").read()).hexdigest()
    manifest = {
        "product": product,
        "component": "Current",
        "description": f"{product} uo/vo at the top level, from {src.rsplit('/', 1)[-1]} (sha256 {sha})",
        "lon": [round(x, 6) for x in lon.tolist()],
        "lat": [round(x, 6) for x in lat.tolist()],
        "time_unix_s": times,
        "time_placement": "label is interval centre" if label_is_centre else "label + 12 h (label is the start of the daily mean)",
        "data_file": stem.rsplit("/", 1)[-1] + ".f32",
        "layout": "[time][lat][lon][east, north] little-endian float32, NaN = land",
    }
    json.dump(manifest, open(stem + ".json", "w"))
    land = float(np.isnan(data[0, :, :, 0]).mean())
    print(json.dumps({"shape": list(data.shape), "first": labels[0].isoformat(), "last": labels[-1].isoformat(),
                      "land_fraction": round(land, 4), "max_speed": float(np.nanmax(np.hypot(u, v)))}))


if __name__ == "__main__":
    main()
