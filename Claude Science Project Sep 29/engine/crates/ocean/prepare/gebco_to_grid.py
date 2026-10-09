"""GEBCO_2026 (15 arc-second, global) -> a regional raw layer for `bathy::Bathymetry`:
int16 elevation (m, positive up) and uint8 Type Identifier, rows south to north, plus a manifest.
Values are copied unchanged (no resampling). Region 40-180 E, 60 S-30 N: the impact region, the
hydroacoustic paths to H01, H08 and H11, and the searched areas.

    python gebco_to_grid.py <GEBCO_2026.nc> <gebco_2026_tid.nc> <out-dir>
"""
import hashlib
import json
import os
import sys

import h5py
import numpy as np

LON, LAT = (40.0, 180.0), (-60.0, 30.0)


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 24), b""):
            h.update(b)
    return h.hexdigest()


def main():
    elev, tid, out = sys.argv[1], sys.argv[2], sys.argv[3]
    os.makedirs(out, exist_ok=True)
    with h5py.File(elev, "r") as f, h5py.File(tid, "r") as g:
        lon, lat = f["lon"][:], f["lat"][:]
        assert np.array_equal(lon, g["lon"][:]) and np.array_equal(lat, g["lat"][:])
        i = np.where((lon >= LON[0]) & (lon <= LON[1]))[0]
        j = np.where((lat >= LAT[0]) & (lat <= LAT[1]))[0]
        i0, i1, j0, j1 = i[0], i[-1] + 1, j[0], j[-1] + 1
        assert lat[1] > lat[0], "expected ascending latitude"
        with open(os.path.join(out, "gebco_2026_elevation.i16"), "wb") as fe, open(os.path.join(out, "gebco_2026_tid.u8"), "wb") as ft:
            for a in range(j0, j1, 1200):
                b = min(j1, a + 1200)
                f["elevation"][a:b, i0:i1].astype("<i2").tofile(fe)
                g["tid"][a:b, i0:i1].astype("u1").tofile(ft)
        step = float(lon[1] - lon[0])
        manifest = dict(source="gebco_2026", lon0=float(lon[i0]), lat0=float(lat[j0]), step_deg=step,
                        nlon=int(i1 - i0), nlat=int(j1 - j0), elevation_file="gebco_2026_elevation.i16",
                        elevation_dtype="i16", tid_file="gebco_2026_tid.u8",
                        description="GEBCO_2026 ice-surface elevation and TID, 15 arc-second, copied unchanged",
                        doi="10.5285/4f68d5c7-45eb-f999-e063-7086abc036fa",
                        source_sha256={os.path.basename(elev): sha256(elev), os.path.basename(tid): sha256(tid)})
    json.dump(manifest, open(os.path.join(out, "gebco_2026.json"), "w"), indent=1)
    print(json.dumps({k: manifest[k] for k in ("lon0", "lat0", "step_deg", "nlon", "nlat")}))


if __name__ == "__main__":
    main()
