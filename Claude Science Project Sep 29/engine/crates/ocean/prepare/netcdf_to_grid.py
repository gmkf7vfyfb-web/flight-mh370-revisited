"""Convert surface-vector netCDF4/HDF5 files (one per period) into the raw grids `GridField::load`
reads: little-endian float32 `[time][lat][lon][east, north]`, NaN at land, one part per input file,
plus a series manifest listing the parts in time order for `GridField::load_series`. h5py and numpy
only.

    python netcdf_to_grid.py --product glorys12v1 --component Current --u uo --v vo \
        --shift-hours 12 --out /path/series-stem in1.nc in2.nc ...

Time placement (`--shift-hours`): values are placed at label + shift. GLORYS12V1 daily means are
labelled 00:00 UTC of the averaged day, so +12 h puts them at the interval centre (PROVISIONAL until the
producer confirms the label convention). BRAN2016 labels its daily means at 12:00 (from average_T1/T2),
and WAVERYS and ERA5 are instantaneous: shift 0.

Unpacking: scale_factor/add_offset applied; _FillValue and missing_value become NaN. Latitude is
flipped to ascending if stored descending. Longitudes must be ascending in -180..180 (OSCAR's 0-360 grid
would need converting first).
"""
import argparse
import hashlib
import json
import os
from datetime import datetime, timedelta, timezone

import h5py
import numpy as np

UNITS = {"hours": 3600.0, "days": 86400.0, "seconds": 1.0, "minutes": 60.0}


def attr(var, name, default=None):
    v = var.attrs.get(name, default)
    if isinstance(v, bytes):
        return v.decode()
    if isinstance(v, np.ndarray) and v.size == 1:
        return v.item()
    return v


def decoded(var, sl):
    raw = var[sl]
    out = raw.astype(np.float32)
    for k in ("_FillValue", "missing_value"):
        f = attr(var, k)
        if f is not None:
            out[raw == f] = np.nan
    if raw.dtype.kind == "f":
        out[np.abs(out) > 1e10] = np.nan
    return out * np.float32(attr(var, "scale_factor", 1.0)) + np.float32(attr(var, "add_offset", 0.0))


def find(f, names):
    for n in names:
        if n in f:
            return f[n]
    raise KeyError(names)


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for b in iter(lambda: fh.read(1 << 22), b""):
            h.update(b)
    return h.hexdigest()


def convert(src, stem, a):
    with h5py.File(src, "r") as f:
        tv = find(f, ["time", "Time"])
        units = attr(tv, "units")
        step, _, origin = units.split(" ", 2)
        t0 = datetime.fromisoformat(origin.strip().replace(" 00:00:00", "")).replace(tzinfo=timezone.utc)
        labels = [t0 + timedelta(seconds=float(v) * UNITS[step]) for v in tv[:]]
        times = [d.timestamp() + 3600.0 * a.shift_hours for d in labels]
        lon = find(f, ["longitude", "lon", "xu_ocean"])[:].astype(np.float64)
        lat = find(f, ["latitude", "lat", "yu_ocean"])[:].astype(np.float64)
        flip = lat[0] > lat[-1]
        nt, land, vmax = len(times), None, 0.0
        with open(stem + ".f32", "wb") as out:
            for t0i in range(0, nt, 100):
                sl = slice(t0i, min(nt, t0i + 100))
                u = decoded(f[a.u], sl).reshape(-1, len(lat), len(lon))
                v = decoded(f[a.v], sl).reshape(-1, len(lat), len(lon))
                if flip:
                    u, v = u[:, ::-1], v[:, ::-1]
                d = np.stack([u, v], axis=-1).astype("<f4")
                if land is None:
                    land = float(np.isnan(d[0, :, :, 0]).mean())
                vmax = max(vmax, float(np.nanmax(np.hypot(u, v))))
                d.tofile(out)
    if flip:
        lat = lat[::-1]
    manifest = dict(product=a.product, component=a.component,
                    description=f"{a.product} {a.u}/{a.v} from {os.path.basename(src)} (sha256 {sha256(src)})",
                    lon=[round(x, 6) for x in lon.tolist()], lat=[round(x, 6) for x in lat.tolist()],
                    time_unix_s=times, time_placement=f"label + {a.shift_hours} h",
                    data_file=os.path.basename(stem) + ".f32",
                    layout="[time][lat][lon][east, north] little-endian float32, NaN = land")
    json.dump(manifest, open(stem + ".json", "w"))
    return dict(part=os.path.basename(stem) + ".json", first=labels[0].isoformat(), last=labels[-1].isoformat(),
                n=len(times), land_fraction=round(land, 4), max_speed=round(vmax, 3))


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--product", required=True)
    p.add_argument("--component", required=True, choices=["Current", "StokesDrift", "Wind10m"])
    p.add_argument("--u", required=True)
    p.add_argument("--v", required=True)
    p.add_argument("--shift-hours", type=float, default=0.0)
    p.add_argument("--out", required=True, help="series stem; parts are <stem>-NN")
    p.add_argument("inputs", nargs="+")
    a = p.parse_args()
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    parts = []
    for k, src in enumerate(a.inputs):
        info = convert(src, f"{a.out}-{k:02d}", a)
        parts.append(info["part"])
        print(json.dumps(info), flush=True)
    json.dump(dict(parts=parts), open(a.out + ".series.json", "w"))


if __name__ == "__main__":
    main()
