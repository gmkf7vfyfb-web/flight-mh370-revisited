import os
"""Path sections outside the module's 40-180 E grid (prereg P1). Same convention as the audit builder
(results/hydroacoustics-audit/scripts/paths.py): WGS84 geodesic, 0.5 km spacing, depth = median of 3x3 GEBCO_2026
15-arc-second cells; WOA23 bilinear at 25 km nodes, TEOS-10. Differences, declared: GEBCO read from the global
GEBCO_2026.nc (same sha as the module layers); WOA23 objectively analysed t_an/s_an from the global 1-degree netCDF,
decade B5C2 (2015-2022), event month for 0-1500 m and the WOA season (13 JFM, 14 AMJ, 15 JAS, 16 OND) below 1500 m;
in-situ t and practical S bilinear-interpolated, then c = gsw.sound_speed. Output schema = module stub schema."""
import json, sys, pathlib, numpy as np, pandas as pd, gsw, netCDF4 as N
from pyproj import Geod
G = Geod(ellps="WGS84"); OC = pathlib.Path(os.environ.get("MH370_OCEAN_DATA", "mh370-ocean-data"))
GEB = N.Dataset(OC / "gebco/GEBCO_2026.nc"); EL = GEB.variables["elevation"]; LAT0, LON0, STEP = -90 + 1 / 480, -180 + 1 / 480, 1 / 240
def depth_at(lat, lon):
    i = np.rint((lat - LAT0) / STEP).astype(int); j = np.rint((lon - LON0) / STEP).astype(int); out = np.empty(len(i))
    for a in range(0, len(i), 200):
        ii, jj = i[a:a + 200], j[a:a + 200]
        blk = EL[ii.min() - 1:ii.max() + 2, jj.min() - 1:jj.max() + 2].astype(float); i0, j0 = ii.min() - 1, jj.min() - 1
        for k, (p, q) in enumerate(zip(ii, jj)):
            out[a + k] = np.median(blk[p - i0 - 1:p - i0 + 2, q - j0 - 1:q - j0 + 2])
    return out
_W = {}
def woa(month):
    if month in _W: return _W[month]
    season = 13 + (month - 1) // 3
    def rd(v, m):
        d = N.Dataset(OC / f"woa23/woa23_B5C2_{v}{m:02d}_01.nc"); a = d.variables[f"{v}_an"][0].filled(np.nan); z = d.variables["depth"][:].data; return z, a
    zm, tm = rd("t", month); _, sm = rd("s", month); zs, ts = rd("t", season); _, ss = rd("s", season)
    deep = zs > zm.max(); z = np.concatenate([zm, zs[deep]])
    t = np.concatenate([tm, ts[deep]], 0); s = np.concatenate([sm, ss[deep]], 0)
    _W[month] = (z, t, s); return _W[month]
def woa_profile(month, lat, lon):
    z, T, S = woa(month); x = lon + 179.5; y = lat + 89.5; j0, i0 = int(np.floor(x)), int(np.floor(y)); fx, fy = x - j0, y - i0
    out = {}
    for k, A in (("t", T), ("s", S)):
        num = np.zeros(len(z)); den = np.zeros(len(z))
        for i, j, w in ((i0, j0, (1 - fy) * (1 - fx)), (i0, j0 + 1, (1 - fy) * fx), (i0 + 1, j0, fy * (1 - fx)), (i0 + 1, j0 + 1, fy * fx)):
            v = A[:, i, j % 360]; ok = np.isfinite(v); num[ok] += w * v[ok]; den[ok] += w
        out[k] = np.where(den > 0, num / np.where(den > 0, den, 1), np.nan)
    p = gsw.p_from_z(-z, lat); SA = gsw.SA_from_SP(out["s"], p, lon, lat); CT = gsw.CT_from_t(SA, out["t"], p)
    return z, out["t"], out["s"], gsw.sound_speed(SA, CT, p)
def build(name, a, b, month, out, ds_km=0.5, node_km=25.0):
    out = pathlib.Path(out); out.mkdir(parents=True, exist_ok=True); (lat0, lon0), (lat1, lon1) = a, b
    az, baz, L = G.inv(lon0, lat0, lon1, lat1); L /= 1000.0; n = int(np.ceil(L / ds_km))
    pts = [(lon0, lat0)] + G.npts(lon0, lat0, lon1, lat1, n - 1) + [(lon1, lat1)]
    lon = np.array([p[0] for p in pts]); lat = np.array([p[1] for p in pts]); r = np.linspace(0, L, len(pts)); el = depth_at(lat, lon)
    pd.DataFrame(dict(range_km=r, lat=lat, lon=lon, elevation_m=el)).to_csv(out / f"bathy_{name}.csv", index=False)
    rn = np.append(np.arange(0, L, node_km), L); rows = []
    for k, rr in enumerate(rn):
        ii = int(np.argmin(np.abs(r - rr))); z, t, s, c = woa_profile(month, lat[ii], lon[ii])
        for zz, tt, sv, cc in zip(z, t, s, c): rows.append((k, rr, lat[ii], lon[ii], zz, tt, sv, cc))
    ssp = pd.DataFrame(rows, columns=["node", "range_km", "lat", "lon", "depth_m", "t_insitu_c", "sp_psu", "c_m_s"]); ssp.to_csv(out / f"ssp_{name}.csv", index=False)
    # channel axis per node
    ax = ssp.dropna().loc[lambda d: d.groupby("node").c_m_s.idxmin()]
    meta = dict(name=name, source=a, receiver=b, month=month, decade="B5C2", length_km=L, az_src_to_rcv=az % 360, n_samples=len(r), n_nodes=len(rn),
                src_water_depth_m=float(-el[0]), rcv_water_depth_m=float(-el[-1]), min_depth_excl_ends_m=float(-np.max(el[20:-200])),
                at_km=float(r[20:-200][np.argmax(el[20:-200])]), axis_depth_median_m=float(ax.depth_m.median()), axis_depth_range_m=[float(ax.depth_m.min()), float(ax.depth_m.max())])
    json.dump(meta, open(out / f"{name}_meta.json", "w"), indent=1); return meta
REC = {"H10N": (-7.83813, -14.48980), "H10S": (-8.95101, -14.65221)}
SRC = {"sjcV": ((-45.666, -59.240), 12), "sjcN": ((-45.6667, -59.415), 12), "sje": ((-45.950, -59.773), 11),
       "fsst16_1": ((30.0335, -79.6406), 6), "fsst16_2": ((29.9948, -79.449), 6), "fsst16_3": ((29.7651, -79.4341), 7), "fsst16_4": ((30.0952, -79.5416), 9),
       "fsst16_5": ((30.0745, -79.5044), 9), "fsst21_1": ((29.7433, -79.3493), 6), "fsst21_2": ((30.0852, -79.3251), 7), "fsst21_3": ((30.1465, -79.6066), 8)}
if __name__ == "__main__":
    which = sys.argv[1:] or list(SRC)
    for s in which:
        (p, m) = SRC[s]
        for r, q in REC.items():
            if s == "fsst16_4" and r == "H10S": continue
            mt = build(f"{s}-{r}", p, q, m, "paths"); print({k: (round(v, 1) if isinstance(v, float) else v) for k, v in mt.items() if k not in ("source", "receiver")}, flush=True)
