"""Load the yearly GDP 6-hourly netCDF files written by fetch_gdp.py into one daily, undrogued
track table, cached as a compressed .npz beside the data.

Steps, each a declared choice:
  1. Read every gdp6h_io_YYYY.nc (scipy.io.netcdf_file; ERDDAP writes netCDF-3).
  2. Keep fixes with time strictly after drogue_lost_date ("undrogued"). A missing or
     non-finite drogue_lost_date means the drogue was never reported lost, and the value 0
     means "drogue status uncertain from beginning" (dataset long_name); both are dropped. (GDP drogue-loss dates are those distributed by AOML
     at retrieval, i.e. the re-evaluated drogue-presence record; Davey et al. 2016 used
     whatever version was current in 2015-16 - an unavoidable difference.)
  3. Keep only fixes at 00:00 UTC, giving one fix per drifter per day. The 1 deg (and down to
     0.25 deg) kernels and the 508 +/- 30 day window do not resolve sub-daily motion.
  4. Sort by (drifter, time) and assign integer drifter indices.

Output arrays (npz): drifter (int32), day (int32, days since 1970-01-01), lat, lon (float32,
lon in 0..360), sst (float32, NaN if missing), ids (str, drifter ID per index).
"""
import glob
import os
import sys

import numpy as np
from scipy.io import netcdf_file


def read_year(path):
    f = netcdf_file(path, "r", mmap=False)
    v = f.variables
    ids = np.array([b"".join(r).decode() for r in v["ID"][:]])
    t = np.asarray(v["time"][:], float)
    lat = np.asarray(v["latitude"][:], float)
    lon = np.asarray(v["longitude"][:], float) % 360.0
    sst = np.asarray(v["sst"][:], float)
    dld = np.asarray(v["drogue_lost_date"][:], float)
    for name, arr in (("sst", sst), ("drogue_lost_date", dld)):
        fv = getattr(v[name], "_FillValue", None)
        if fv is not None:
            arr[arr == fv] = np.nan
    f.close()
    return ids, t, lat, lon, sst, dld


def build(datadir, out=None):
    out = out or os.path.join(datadir, "derived", "gdp_daily_undrogued.npz")
    files = sorted(glob.glob(os.path.join(datadir, "gdp6h_io_*.nc")))
    parts = []
    n_all = n_undrogued = 0
    for p in files:
        ids, t, lat, lon, sst, dld = read_year(p)
        n_all += len(t)
        # dataset convention: missing = drogue still attached; 0 = status uncertain from the
        # beginning. Both are excluded; only a dated loss with time after it counts as undrogued.
        und = np.isfinite(dld) & (dld > 0) & (t > dld)
        n_undrogued += int(und.sum())
        daily = (np.mod(t, 86400.0) == 0.0)
        k = und & daily
        parts.append((ids[k], (t[k] // 86400).astype(np.int32), lat[k], lon[k], sst[k]))
    ids = np.concatenate([p[0] for p in parts])
    day = np.concatenate([p[1] for p in parts])
    lat = np.concatenate([p[2] for p in parts]).astype(np.float32)
    lon = np.concatenate([p[3] for p in parts]).astype(np.float32)
    sst = np.concatenate([p[4] for p in parts]).astype(np.float32)
    uid, drifter = np.unique(ids, return_inverse=True)
    order = np.lexsort((day, drifter))
    drifter, day, lat, lon, sst = (a[order] for a in (drifter.astype(np.int32), day, lat, lon, sst))
    # drop exact duplicates (a fix on 1 Jan can appear in two yearly files only if boundaries overlap)
    keep = np.ones(len(day), bool)
    keep[1:] = (drifter[1:] != drifter[:-1]) | (day[1:] != day[:-1])
    os.makedirs(os.path.dirname(out), exist_ok=True)
    np.savez_compressed(out, drifter=drifter[keep], day=day[keep], lat=lat[keep], lon=lon[keep],
                        sst=sst[keep], ids=uid, n_rows_6h=n_all, n_undrogued_6h=n_undrogued)
    return out


def load(path):
    z = np.load(path, allow_pickle=False)
    return {k: z[k] for k in z.files}


if __name__ == "__main__":
    print(build(sys.argv[1] if len(sys.argv) > 1 else "/Users/pete/Downloads/mh370-ocean-data/gdp"))
