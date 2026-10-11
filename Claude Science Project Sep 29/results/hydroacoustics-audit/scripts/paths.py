"""Audit path builder (independent of the shared ocean-transport crate): WGS84 geodesic, GEBCO_2026 depth and
WOA23 sound speed along a source-receiver path, written in the schema that the hydroacoustics module's
air9_tl_validation.build_profiles reads (bathy_*.csv, ssp_*.csv).

Differences from the shared crate, declared: 0.5 km along-path spacing (shared: 0.25 km), depth = median of the
3 x 3 GEBCO cells (about +/-0.6 km) around each point (shared: +/-2 km corridor median), WOA23 bilinear in
lon/lat at 25 km nodes, NaN levels below the local WOA floor left for the module's gsw extension.

Usage (library): build(name, (lat0, lon0), (lat1, lon1), decade, month, out_dir)
"""
import json
import pathlib

import gsw
import numpy as np
import pandas as pd
from pyproj import Geod

OCEAN = pathlib.Path("/Users/pete/Downloads/mh370-ocean-data")
G = Geod(ellps="WGS84")
_gebco = None


def gebco():
    global _gebco
    if _gebco is None:
        m = json.loads((OCEAN / "gebco/grid/gebco_2026.json").read_text())
        z = np.memmap(OCEAN / "gebco/grid" / m["elevation_file"], dtype="<i2", mode="r", shape=(m["nlat"], m["nlon"]))
        _gebco = (m, z)
    return _gebco


def depth_at(lat, lon):
    m, z = gebco()
    i = np.rint((np.asarray(lat) - m["lat0"]) / m["step_deg"]).astype(int)
    j = np.rint((np.asarray(lon) - m["lon0"]) / m["step_deg"]).astype(int)
    out = np.empty(len(i))
    for k, (a, b) in enumerate(zip(i, j)):
        out[k] = np.median(z[a - 1:a + 2, b - 1:b + 2])
    return out


def woa(decade, month):
    d = OCEAN / "woa23/soundspeed"
    m = json.loads((d / f"woa23_{decade}_m{month:02d}.json").read_text())
    nz = len(m["depth_m"])
    shp = (m["nlat"], m["nlon"], nz)   # file layout [lat][lon][depth] (checked against the shared export)
    g = {k: np.fromfile(d / m[f"{k}_file"], dtype="<f4").reshape(shp) for k in ("c_mean", "sa", "ct")}
    return m, g


def woa_profile(m, g, lat, lon):
    x = (lon - m["lon0"]) / m["step_deg"]; y = (lat - m["lat0"]) / m["step_deg"]
    j0, i0 = int(np.floor(x)), int(np.floor(y)); fx, fy = x - j0, y - i0
    out = {}
    for k, a in g.items():
        cells = [(i0, j0, (1 - fy) * (1 - fx)), (i0, j0 + 1, (1 - fy) * fx), (i0 + 1, j0, fy * (1 - fx)), (i0 + 1, j0 + 1, fy * fx)]
        num = np.zeros(a.shape[2]); den = np.zeros(a.shape[2])
        for i, j, w in cells:
            v = a[i, j, :].astype(float); ok = np.isfinite(v)
            num[ok] += w * v[ok]; den[ok] += w
        out[k] = np.where(den > 0, num / np.where(den > 0, den, 1), np.nan)
    return np.array(m["depth_m"], float), out


def build(name, a, b, decade, month, out_dir, ds_km=0.5, node_km=25.0):
    out = pathlib.Path(out_dir); out.mkdir(parents=True, exist_ok=True)
    (lat0, lon0), (lat1, lon1) = a, b
    _, _, L = G.inv(lon0, lat0, lon1, lat1); L /= 1000.0
    n = int(np.ceil(L / ds_km))
    pts = [(lon0, lat0)] + G.npts(lon0, lat0, lon1, lat1, n - 1) + [(lon1, lat1)]
    lon = np.array([p[0] for p in pts]); lat = np.array([p[1] for p in pts]); r = np.linspace(0, L, len(pts))
    el = depth_at(lat, lon)
    pd.DataFrame(dict(range_km=r, lat=lat, lon=lon, elevation_m=el, tid=np.nan, corridor_max_elevation_m=np.nan)).to_csv(
        out / f"bathy_{name}.csv", index=False)
    m, g = woa(decade, month)
    rn = np.append(np.arange(0, L, node_km), L); rows = []
    for k, rr in enumerate(rn):
        ii = int(np.argmin(np.abs(r - rr)))
        z, p = woa_profile(m, g, lat[ii], lon[ii])
        pr = gsw.p_from_z(-z, lat[ii])
        sp = gsw.SP_from_SA(p["sa"], pr, lon[ii], lat[ii]); t = gsw.t_from_CT(p["sa"], p["ct"], pr)
        for zz, tt, ss, cc in zip(z, t, sp, p["c_mean"]):
            rows.append((k, rr, lat[ii], lon[ii], zz, tt, ss, cc))
    pd.DataFrame(rows, columns=["node", "range_km", "lat", "lon", "depth_m", "t_insitu_c", "sp_psu", "c_m_s"]).to_csv(
        out / f"ssp_{name}.csv", index=False)
    shallow = float(np.nanmax(el[: max(1, len(el) - int(100 / ds_km))]))
    return L, shallow
