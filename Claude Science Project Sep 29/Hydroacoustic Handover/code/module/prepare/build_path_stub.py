"""PROVISIONAL ocean-environment stub for the Blackman engine validation: two paths only.

Approved 2026-10-09 (coordination/HYDROACOUSTICS.md, morning rulings, item 5; extended to air8 by ruling
H3): WOA23 + GEBCO on the air9 and air8 -> H01W and -> H08S paths, tens of MB, in this module's own directory, sound speed via gsw,
DELETED when the shared ocean-transport API serves profiles and bathymetry. Its assumptions are stated
in coordination/OCEAN_TRANSPORT.md so the shared owner can reject rather than inherit them.

SOURCES: line midpoints from data/blackman/blackman_shot_lines.csv (both segments of each line):
air9 (19 Oct 2001, 02:10-02:46 UTC) -27.5612, 98.8821; air8 (16 Oct 2001, 12:28-13:04 UTC) -23.4246, 88.2167. RECEIVERS: FDSN triad centroids (data/stations.csv). H08S uses the
2002 FDSN position for a 2001 event, PROVISIONAL (ruling item 4).

PATH: WGS84 geodesic, sampled every 0.5 km for bathymetry and every 25 km for sound speed.

BATHYMETRY: GEBCO_2026 ice-surface-elevation grid (15 arc-second) and its Type Identifier grid, via
OPeNDAP at NERC CEDA (dap.ceda.ac.uk). Read in small boxes around each 100-km piece of path at full
resolution; each path point takes its NEAREST grid cell (no interpolation, so the TID stays exact).
The ensonified corridor is wider than one cell; the corridor maximum elevation within +/-2 km across
track is recorded beside the on-track value, as the blockage diagnostic.

SOUND SPEED: WOA23, decade 1995-2004 ('95A4'), season 16 (Oct-Dec), 1.00 deg, objectively analysed
t_an and s_an, via OPeNDAP at NOAA NCEI. Season 16 is the closest full-depth field to October 2001; the
monthly fields stop at 1,500 m. Bilinear in latitude and longitude at each node, levels kept native.
TEOS-10 (gsw 3.6): SA from SP, CT from in-situ t, then gsw.sound_speed at in-situ pressure. A level is
NaN where WOA has no data (below the local seafloor); never filled.

Run: python prepare/build_path_stub.py <out_dir> [air9|air8]   (default air9)
"""

import json
import pathlib
import sys

import gsw
import numpy as np
import pandas as pd
import xarray as xr
from pyproj import Geod

GEOD = Geod(ellps="WGS84")
SOURCES = {"air9": (-27.5612, 98.8821), "air8": (-23.4246, 88.2167)}
STATIONS = {"H01W": (-34.890303, 114.142637), "H08S": (-7.639380, 72.483828)}
GEBCO = "https://dap.ceda.ac.uk/thredds/dodsC/bodc/gebco/global/gebco_2026/ice_surface_elevation/netcdf/GEBCO_2026.nc"
TID = "https://dap.ceda.ac.uk/thredds/dodsC/bodc/gebco/global/gebco_2026/type_identifier_grid/netcdf/gebco_2026_tid.nc"
WOA_T = "https://www.ncei.noaa.gov/thredds-ocean/dodsC/woa23/DATA/temperature/netcdf/95A4/1.00/woa23_95A4_t16_01.nc"
WOA_S = "https://www.ncei.noaa.gov/thredds-ocean/dodsC/woa23/DATA/salinity/netcdf/95A4/1.00/woa23_95A4_s16_01.nc"
DS_BATHY_KM, DS_SSP_KM, CROSS_KM, PIECE = 0.5, 25.0, 2.0, 200


def path_points(lat0, lon0, lat1, lon1, step_km):
    az, _, dist = GEOD.inv(lon0, lat0, lon1, lat1)
    s = np.arange(0.0, dist / 1000.0 + 1e-9, step_km)
    lon, lat, _ = GEOD.fwd(np.full(len(s), lon0), np.full(len(s), lat0), np.full(len(s), az), s * 1000.0)
    _, back, _ = GEOD.inv(lon, lat, np.full(len(s), lon1), np.full(len(s), lat1))
    return s, lat, lon, np.asarray(back)


def bathymetry(lat, lon, fwd_az):
    g = xr.open_dataset(GEBCO); t = xr.open_dataset(TID)
    glat, glon = g["lat"].values, g["lon"].values
    out = np.full((len(lat), 3), np.nan)
    # cross-track offsets for the corridor diagnostic
    offs = np.linspace(-CROSS_KM, CROSS_KM, 9) * 1000.0
    for a in range(0, len(lat), PIECE):
        sl = slice(a, min(a + PIECE, len(lat)))
        cl, cn, _ = GEOD.fwd(np.repeat(lon[sl], len(offs)), np.repeat(lat[sl], len(offs)),
                             np.repeat(fwd_az[sl] + 90.0, len(offs)), np.tile(offs, sl.stop - sl.start))
        la0, la1 = min(lat[sl].min(), cn.min()) - 0.01, max(lat[sl].max(), cn.max()) + 0.01
        lo0, lo1 = min(lon[sl].min(), cl.min()) - 0.01, max(lon[sl].max(), cl.max()) + 0.01
        i0, i1 = np.searchsorted(glat, [la0, la1]); j0, j1 = np.searchsorted(glon, [lo0, lo1])
        z = g["elevation"][i0:i1 + 1, j0:j1 + 1].values.astype(float)
        tid = t["tid"][i0:i1 + 1, j0:j1 + 1].values
        sub_lat, sub_lon = glat[i0:i1 + 1], glon[j0:j1 + 1]
        ii = np.abs(sub_lat[None, :] - lat[sl][:, None]).argmin(1)
        jj = np.abs(sub_lon[None, :] - lon[sl][:, None]).argmin(1)
        out[sl, 0] = z[ii, jj]; out[sl, 1] = tid[ii, jj]
        ci = np.abs(sub_lat[None, :] - cn[:, None]).argmin(1); cj = np.abs(sub_lon[None, :] - cl[:, None]).argmin(1)
        out[sl, 2] = z[ci, cj].reshape(-1, len(offs)).max(1)
        print(f"  bathymetry {sl.stop}/{len(lat)}", flush=True)
    return out


def sound_speed(lat, lon, woa):
    t, s = woa
    depth = t["depth"].values
    rows = []
    for k in range(len(lat)):
        tk = t["t_an"].isel(time=0).interp(lat=lat[k], lon=lon[k]).values
        sk = s["s_an"].isel(time=0).interp(lat=lat[k], lon=lon[k]).values
        p = gsw.p_from_z(-depth, lat[k])
        sa = gsw.SA_from_SP(sk, p, lon[k], lat[k]); ct = gsw.CT_from_t(sa, tk, p)
        c = gsw.sound_speed(sa, ct, p)
        for d, a, b, cc in zip(depth, tk, sk, c):
            rows.append((k, lat[k], lon[k], d, a, b, cc))
    return rows


def main(out_dir, source="air9"):
    SRC = (source,) + SOURCES[source]
    out = pathlib.Path(out_dir); out.mkdir(parents=True, exist_ok=True)
    woa = None
    meta = {"source": SRC, "stations": STATIONS, "gebco": GEBCO, "tid": TID, "woa_t": WOA_T, "woa_s": WOA_S,
            "gsw": gsw.__version__, "provisional": True, "paths": {}}
    for name, (sla, slo) in STATIONS.items():
        s, la, lo, _ = path_points(SRC[1], SRC[2], sla, slo, DS_BATHY_KM)
        az = np.array(GEOD.inv(lo[:-1], la[:-1], lo[1:], la[1:])[0]); az = np.append(az, az[-1])
        b = bathymetry(la, lo, az)
        pd.DataFrame({"range_km": s, "lat": la, "lon": lo, "elevation_m": b[:, 0], "tid": b[:, 1],
                      "corridor_max_elevation_m": b[:, 2]}).to_csv(out / f"bathy_{source}_{name}.csv", index=False,
                                                                     float_format="%.5f")
        if woa is None:
            box = dict(lat=slice(-37, -4), lon=slice(68, 117))
            woa = (xr.open_dataset(WOA_T, decode_times=False)[["t_an"]].sel(**box).load(),
                   xr.open_dataset(WOA_S, decode_times=False)[["s_an"]].sel(**box).load())
            xr.merge([woa[0], woa[1]]).to_netcdf(out / f"woa23_95A4_season16_box_{source}.nc")
        ss, sla_, slo_, _ = path_points(SRC[1], SRC[2], sla, slo, DS_SSP_KM)
        rows = sound_speed(sla_, slo_, woa)
        df = pd.DataFrame(rows, columns=["node", "lat", "lon", "depth_m", "t_insitu_c", "sp_psu", "c_m_s"])
        df.insert(1, "range_km", ss[df["node"].values])
        df.to_csv(out / f"ssp_{source}_{name}.csv", index=False, float_format="%.4f")
        meta["paths"][name] = {"length_km": float(s[-1]), "n_bathy": int(len(s)), "n_ssp_nodes": int(len(ss)),
                               "min_depth_on_track_m": float(-np.nanmax(b[:, 0])),
                               "min_depth_corridor_m": float(-np.nanmax(b[:, 2]))}
        print(name, json.dumps(meta["paths"][name]), flush=True)
    json.dump(meta, open(out / f"stub-manifest_{source}.json", "w"), indent=1)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else "air9")
