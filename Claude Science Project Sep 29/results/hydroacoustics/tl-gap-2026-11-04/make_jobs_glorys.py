"""Addendum (5 Nov 2026): real ocean conditions instead of WOA23 climatology.
Only the sound-speed nodes of the frozen sections change. Source: Copernicus Marine GLORYS12V1 reanalysis
(cmems_mod_glo_phy_my_0.083deg_P1D-m, daily mean thetao/so), bilinear at each 25-km node (NaN cells dropped, weights
renormalised), TEOS-10 (SA from SP, CT from potential temperature), below the deepest valid level SA/CT held and pressure
increased to 11,000 m (the chain's WOA23 convention, tlchain.paths.sound_speed_profile).
Variants (reciprocal RAM, frozen physics, layered seabed, 7 frequencies per band, outputs 10/2/30 m):
  G400_<date> : GLORYS on <date> for nodes r <= 400 km from the impact end, linear blend to WOA23 at 400-500 km
  GALL_<date> : GLORYS on <date> at every node (arc paths only; the Misawa box covers only the first 690-710 km of the 3,250-3,340 km Wake paths)
Usage: python make_jobs_glorys.py <workdir>"""
import json, os, pickle, sys
import numpy as np, netCDF4 as nc, gsw
W = sys.argv[1]
sys.path.insert(0, os.environ["TLCHAIN_DIR"])
from tlchain import chain as C                     # noqa: E402
from tlchain.bottom import LAYERED                 # noqa: E402
from tlchain.paths import EXT_LEVELS               # noqa: E402
GD = os.path.expanduser("~/Downloads/mh370-ocean-data/glorys12/profile")
FILES = {"arc": f"{GD}/glorys12v1_uo_vo_thetao_so_75-115E_45-10S_20140307-20140314.nc",
         "wake": f"{GD}/glorys12v1_thetao_so_141-149E_36-42N_20190330-20190419.nc"}
_cache = {}


def day(region, date):
    k = (region, date)
    if k not in _cache:
        d = nc.Dataset(FILES[region]); t = nc.num2date(d.variables["time"][:], d.variables["time"].units)
        i = [j for j, x in enumerate(t) if x.strftime("%Y-%m-%d") == date][0]
        th = np.ma.filled(d.variables["thetao"][i].astype(float), np.nan); so = np.ma.filled(d.variables["so"][i].astype(float), np.nan)
        _cache[k] = (th, so, d.variables["depth"][:].data.astype(float), d.variables["latitude"][:].data.astype(float),
                     d.variables["longitude"][:].data.astype(float))
    return _cache[k]


def bilin(a, la, lo, lat, lon):
    y = (lat - la[0]) / (la[1] - la[0]); x = (lon - lo[0]) / (lo[1] - lo[0]); i0, j0 = int(np.floor(y)), int(np.floor(x)); fy, fx = y - i0, x - j0
    num = np.zeros(a.shape[0]); den = np.zeros(a.shape[0])
    for di, dj, w in ((0, 0, (1 - fy) * (1 - fx)), (0, 1, (1 - fy) * fx), (1, 0, fy * (1 - fx)), (1, 1, fy * fx)):
        ii = min(max(i0 + di, 0), len(la) - 1); jj = min(max(j0 + dj, 0), len(lo) - 1)
        col = a[:, ii, jj]; ok = np.isfinite(col); num[ok] += w * col[ok]; den[ok] += w
    return np.where(den > 0, num / np.where(den > 0, den, 1.0), np.nan)


def glorys_profile(region, date, lat, lon):
    th, so, z, la, lo = day(region, date)
    if not (la[0] <= lat <= la[-1] and lo[0] <= lon <= lo[-1]):
        return None
    t = bilin(th, la, lo, lat, lon); s = bilin(so, la, lo, lat, lon)
    ok = np.isfinite(t) & np.isfinite(s)
    if not ok[0]:
        return None
    last = np.argmin(ok) if not ok.all() else len(ok)
    z, t, s = z[:last], t[:last], s[:last]
    p = gsw.p_from_z(-z, lat); sa = gsw.SA_from_SP(s, p, lon, lat); ct = gsw.CT_from_pt(sa, t); c = gsw.sound_speed(sa, ct, p)
    zx = np.concatenate([np.arange(z[-1] + 100.0, 5600.0, 100.0), EXT_LEVELS]); zx = np.unique(zx[zx > z[-1]])
    cx = gsw.sound_speed(np.full(len(zx), sa[-1]), np.full(len(zx), ct[-1]), gsw.p_from_z(-zx, lat))
    return np.concatenate([z, zx]), np.concatenate([c, cx])


def replace(sec, region, date, r_full, r_blend):
    rk = sec["range_km"]; out = dict(sec); nodes = []; log = []
    for r, z, c in sec["nodes"]:
        if r <= r_blend:
            k = int(np.argmin(np.abs(rk - r))); lat, lon = float(sec["lat"][k]), float(sec["lon"][k])
            g = glorys_profile(region, date, lat, lon)
            if g is not None:
                cg = np.interp(z, g[0], g[1]); w = 1.0 if r <= r_full else (r_blend - r) / (r_blend - r_full)
                log.append(dict(r_km=r, lat=lat, lon=lon, w=w, c_surf_woa=float(c[0]), c_surf_glorys=float(cg[0]),
                                dc_rms_0_1500=float(np.sqrt(np.mean((cg - c)[z <= 1500] ** 2)))))
                c = w * cg + (1 - w) * c
        nodes.append((r, z, c))
    out["nodes"] = nodes
    return out, log


if __name__ == "__main__":
    sd = os.path.join(W, "sec"); pf = json.load(open(os.path.join(W, "paths.json")))
    VAR = []
    for nm in ("arc39.0S-H01W", "arc35.5S-H01W", "arc30.0S-H01W"):
        for date in ("2014-03-08", "2014-03-07", "2014-03-14"):
            VAR.append((nm, "arc", date, "G400", 400.0, 500.0))
        VAR.append((nm, "arc", "2014-03-08", "GALL", 1e9, 1e9))
    for nm in ("f35a-H11N", "f35a-H11S"):
        for date in ("2019-04-09", "2019-03-30", "2019-04-19"):
            VAR.append((nm, "wake", date, "G400", 400.0, 500.0))
    J, LOG = [], []
    for nm, region, date, tag, rf, rb in VAR:
        sec = pickle.load(open(os.path.join(sd, nm + ".pkl"), "rb"))
        s2, log = replace(sec, region, date, rf, rb)
        v = f"{tag}_{date}"; pk = os.path.join(sd, f"{nm}__{v}.pkl"); pickle.dump(s2, open(pk, "wb"))
        LOG += [dict(path=nm, variant=v, source="GLORYS12V1 daily mean (cmems_mod_glo_phy_my_0.083deg_P1D-m)", date=date, **x) for x in log]
        rd = pf[nm]["rd"]
        for fc in [5.0, 6.3, 8.0, 10.0, 12.5, 16.0, 20.0, 25.0, 31.5, 40.0]:
            for f in C.band_freqs(fc, 7):
                J.append(dict(id=f"rev|{v}|{nm}|{fc:g}|{f:.4f}", kind="rev", model="ram", sec=pk, reverse=True, f=float(f), zsrc=float(rd),
                              out_depths=[10.0, 2.0, 30.0], bottom=LAYERED.as_dict(), mode="native", dr_lam=5.0, dz_lam=0.05,
                              dr_max_m=250.0, window_m=1000.0, cost=float(sec["L_km"] * f * max(f, 30.0))))
    json.dump(J, open(os.path.join(W, "jobs_glorys.json"), "w"))
    import pandas as pd
    pd.DataFrame(LOG).to_csv(os.path.join(W, "glorys_profiles_used.csv"), index=False)
    print(len(J), "jobs;", len(LOG), "node profiles replaced")
