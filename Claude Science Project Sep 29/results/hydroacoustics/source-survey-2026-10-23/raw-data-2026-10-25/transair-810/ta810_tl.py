"""Transmission loss Oahu (NTSB ditching point) -> H11N / H11S with the module KRAKEN chain (tl_grid_run_j.build_path,
air9_tl_validation.build_profiles, kraken_tl.tl_path; adiabatic modes, hard bottom cp 1650 m/s, Francois-Garrison
absorption, spherical correction). Only the two loaders are substituted, as step2_tl.py did: bathymetry from the global
GEBCO_2026 netCDF (the extracted int16 grids stop at 180 E), 3 x 3 median + +/-2 km corridor max as bathy_along; sound
speed from WOA23 B5C2 (2015-2022) July t_an/s_an 1 deg (monthly to 1500 m, Jul-Sep seasonal below), TEOS-10 (gsw).
Source depths 0.5, 1, 2, 5, 10, 30 m; bands 5-63 Hz third octaves. FIELD abort (ReadModes) retried with one interior
profile removed (module practice, effect <= 0.01 dB). Usage: python ta810_tl.py <out_dir> <at_bin>"""
import sys, os, json, time, shutil, pathlib
from concurrent.futures import ThreadPoolExecutor
import numpy as np, pandas as pd, netCDF4, gsw
WS = pathlib.Path(__file__).resolve().parent.parent
MODP = WS / "repo/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare"
sys.path.insert(0, str(MODP))
import tl_grid_run_j as TG, air9_tl_validation as A, kraken_tl as K
OC = pathlib.Path(os.environ.get("MH370_OCEAN_DATA", "mh370-ocean-data"))
NC = netCDF4.Dataset(OC / "gebco/GEBCO_2026.nc"); GLAT = NC.variables["lat"][:]; GLON = NC.variables["lon"][:]; EL = NC.variables["elevation"]
STEP = float(GLAT[1] - GLAT[0]); _T = {}
def _tile(ti, tj):
    if (ti, tj) not in _T:
        i0 = int(np.searchsorted(GLAT, ti)) - 2; j0 = int(np.searchsorted(GLON, tj)) - 2; n = int(round(1 / STEP)) + 6
        i0 = max(i0, 0); j0 = max(j0, 0)
        _T[(ti, tj)] = (i0, j0, np.asarray(EL[i0:i0 + n, j0:j0 + n]).astype(float))
    return _T[(ti, tj)]
def el_at(lat, lon, di=0, dj=0):
    lon = ((np.asarray(lon) + 180) % 360) - 180; lat = np.asarray(lat); out = np.empty(len(lat))
    for k, (a, b) in enumerate(zip(lat, lon)):
        i0, j0, Tt = _tile(np.floor(a), np.floor(b))
        ii = int(np.rint((a - GLAT[i0]) / STEP)) + di; jj = int(np.rint((b - GLON[j0]) / STEP)) + dj
        out[k] = Tt[min(max(ii, 0), Tt.shape[0] - 1), min(max(jj, 0), Tt.shape[1] - 1)]
    return out
def bathy_along_nc(lat, lon, az):
    nb = np.stack([el_at(lat, lon, di, dj) for di in (-1, 0, 1) for dj in (-1, 0, 1)], 0)
    depth_med = np.median(nb, axis=0); t = np.zeros(len(lat), int)        # TID not used by the chain
    cmax = np.full(len(lat), -np.inf)
    for off in np.arange(-2000.0, 2000.1, 250.0):
        if off == 0:
            cmax = np.maximum(cmax, el_at(lat, lon)); continue
        plon, plat, _ = TG.G.fwd(lon, lat, az + 90.0, np.full(len(lat), off)); cmax = np.maximum(cmax, el_at(plat, plon))
    return depth_med, t, cmax
W = {}
def _woa():
    if not W:
        d = OC / "woa23"
        tm = netCDF4.Dataset(d / "woa23_B5C2_t07_01.nc"); sm = netCDF4.Dataset(d / "woa23_B5C2_s07_01.nc")
        ts = netCDF4.Dataset(d / "woa23_B5C2_t15_01.nc"); ss = netCDF4.Dataset(d / "woa23_B5C2_s15_01.nc")
        zm = tm.variables["depth"][:].astype(float); zs = ts.variables["depth"][:].astype(float); deep = zs > zm[-1]
        W["z"] = np.concatenate([zm, zs[deep]]); W["lat"] = tm.variables["lat"][:]; W["lon"] = tm.variables["lon"][:]
        W["t"] = (tm.variables["t_an"][0], ts.variables["t_an"][0], deep); W["s"] = (sm.variables["s_an"][0], ss.variables["s_an"][0], deep)
    return W
def _col(key, i, j):
    a, b, deep = _woa()[key]
    v = np.concatenate([np.ma.filled(a[:, i, j].astype(float), np.nan), np.ma.filled(b[deep, i, j].astype(float), np.nan)]); return v
def woa_profile_nc(lat, lon):
    w = _woa(); lon = ((lon + 180) % 360) - 180
    x = (lon - w["lon"][0]); y = (lat - w["lat"][0]); j0, i0 = int(np.floor(x)), int(np.floor(y)); fx, fy = x - j0, y - i0
    z = w["z"]; num = {k: np.zeros(len(z)) for k in ("t", "s")}; den = {k: np.zeros(len(z)) for k in ("t", "s")}
    for i, j, wt in ((i0, j0, (1 - fy) * (1 - fx)), (i0, (j0 + 1) % 360, (1 - fy) * fx), (i0 + 1, j0, fy * (1 - fx)), (i0 + 1, (j0 + 1) % 360, fy * fx)):
        for k in ("t", "s"):
            v = _col(k, i, j); ok = np.isfinite(v); num[k][ok] += wt * v[ok]; den[k][ok] += wt
    t = np.where(den["t"] > 0, num["t"] / np.where(den["t"] > 0, den["t"], 1), np.nan); s = np.where(den["s"] > 0, num["s"] / np.where(den["s"] > 0, den["s"], 1), np.nan)
    p = gsw.p_from_z(-z, lat); sa = gsw.SA_from_SP(s, p, lon, lat); ct = gsw.CT_from_t(sa, t, p)
    return z, dict(c_mean=gsw.sound_speed(sa, ct, p), c_sd=np.full(len(z), np.nan), sa=sa, ct=ct)
TG.bathy_along = bathy_along_nc; TG.woa_profile = woa_profile_nc
SRC_DEPTHS = [0.5, 1.0, 2.0, 5.0, 10.0, 30.0]
BANDS = [5.0, 6.3, 8.0, 10.0, 12.5, 16.0, 20.0, 25.0, 31.5, 40.0, 50.0, 63.0]
def run(name, src, rcv, at_bin, work, pathdir):
    bathy, ssp, info = TG.build_path(src, rcv)
    bathy.to_csv(pathdir / f"bathy_{name}.csv", index=False); ssp.to_csv(pathdir / f"ssp_{name}.csv", index=False)
    rprof, profiles = A.build_profiles(bathy, ssp)
    rd = float(min(rcv["rcv_depth_m"], profiles[-1][0] - 1.0)); L = rprof[-1]; wd = pathlib.Path(work) / name; rows = []
    for fc in BANDS:
        tag = f"f{fc:g}".replace(".", "p"); rp, pr, drop = rprof, profiles, None
        for attempt in range(4):
            try:
                r, tl, nm, dt = K.tl_path(wd, tag, fc, pr, rp, np.array([L]), SRC_DEPTHS, [rd], A.BOTTOMS["hard"], at_bin, fg=A.FG)
                s = K.read_shd(wd / f"{tag}.shd"); x = s["rr_m"] / 1000.0 / 6371.0; sph = 10 * np.log10(x / np.sin(x))
                for js, zs in enumerate(s["sz"]):
                    rows.append(dict(path=name, fc_hz=fc, src_depth_m=float(zs), rcv_depth_m=rd, range_km=float(L), tl_db=float((-20 * np.log10(np.abs(s["p"][0, js, 0])) + sph)[-1]),
                                     status="ok", n_modes_first=nm[0] if nm else -1, n_modes_min=min(nm) if nm else -1, profile_dropped_km=drop,
                                     first_profile_depth_m=float(profiles[0][0])))
                break
            except RuntimeError as e:
                if "no modes" in str(e).lower():
                    for zs in SRC_DEPTHS:
                        rows.append(dict(path=name, fc_hz=fc, src_depth_m=zs, rcv_depth_m=rd, range_km=float(L), tl_db=np.nan, status="no_modes", first_profile_depth_m=float(profiles[0][0])))
                    break
                k = len(rprof) // 2 + attempt; rp = np.delete(rprof, k); pr = profiles[:k] + profiles[k + 1:]; drop = float(rprof[k])
        else:
            for zs in SRC_DEPTHS:
                rows.append(dict(path=name, fc_hz=fc, src_depth_m=zs, tl_db=np.nan, status="error"))
    shutil.rmtree(wd, ignore_errors=True)
    return rows, info
def main(out_dir, at_bin):
    out = pathlib.Path(out_dir); out.mkdir(parents=True, exist_ok=True); pathdir = out / "paths"; pathdir.mkdir(exist_ok=True)
    st = pd.read_csv(WS / "repo/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/data/stations.csv", comment="#")
    src = dict(id="ta810", lat=21.27616, lon=-158.02565)
    jobs = []
    for n in ("H11N", "H11S"):
        g = st[st.triad == n]; rcv = dict(name=n, lat=float(g.latitude_deg.mean()), lon=float(g.longitude_deg.mean()), kind="ims", rcv_depth_m=float(g.hydrophone_depth_m.mean()))
        jobs.append((f"ta810-{n}", src, rcv))
    # declared source-end alternative: source moved seaward along 180 deg (downslope escape), 3 / 6 / 10 km
    for dkm in (3.0, 6.0, 10.0):
        lon2, lat2, _ = TG.G.fwd(src["lon"], src["lat"], 180.0, dkm * 1000.0)
        for n in ("H11N", "H11S"):
            g = st[st.triad == n]; rcv = dict(name=n, lat=float(g.latitude_deg.mean()), lon=float(g.longitude_deg.mean()), kind="ims", rcv_depth_m=float(g.hydrophone_depth_m.mean()))
            jobs.append((f"ta810s{dkm:g}km-{n}", dict(id=f"ta810s{dkm:g}km", lat=float(lat2), lon=float(lon2)), rcv))
    t0 = time.time(); rows = []; infos = {}
    with ThreadPoolExecutor(3) as ex:
        for (r, info), j in zip(ex.map(lambda j: run(j[0], j[1], j[2], at_bin, str(out / "work"), pathdir), jobs), jobs):
            rows += r; infos[j[0]] = info; print(j[0], round(time.time() - t0), flush=True)
    pd.DataFrame(rows).to_csv(out / "ta810_tl.csv", index=False); json.dump(infos, open(out / "ta810_tl_meta.json", "w"), indent=1, default=float)
if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
