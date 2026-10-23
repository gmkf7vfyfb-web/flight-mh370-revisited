"""Step 2 (and U2) transmission loss on the F-35A -> H11 paths, exactly as pre-registered in prereg.py (commit 7dc315f).
The TL-grid builder and run_path of tl_grid_run_j.py are used unchanged; only the two loaders are substituted:
bathymetry = GEBCO_2026 NW Pacific layer where lat >= 30 N, global layer elsewhere; sound speed = WOA23 B5C2 April
(soundspeed_nwpac). Jobs: H11N and H11S from the working point (primary); the same with the source moved -8 / +8 km
along the H11S azimuth (sensitivity); U2 = H11S with the first 500 km of sound-speed nodes replaced by the run J
median-region profile (37.5 S 89.5 E, WOA23 A5B4 March). Also writes the along-track path sections and the
cross-check against the 9 Oct ocean-transport exports.
Usage: python step2_tl.py <out_dir> <at_bin> [nproc]
"""
from __future__ import annotations
import json, os, pathlib, shutil, sys, time
from multiprocessing import Pool
import numpy as np, pandas as pd

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(HERE.parent))
import prereg as R  # noqa: E402
import tl_grid_run_j as TG  # noqa: E402
import air9_tl_validation as A  # noqa: E402
import kraken_tl as K  # noqa: E402

OCEAN = pathlib.Path("/Users/pete/Downloads/mh370-ocean-data")
EXPORT = OCEAN / "products/hydro-paths-f35a-2019-04"
_L = {}


def _grid(name):
    if name not in _L:
        m = json.loads((OCEAN / f"gebco/grid/{name}.json").read_text())
        el = np.memmap(OCEAN / "gebco/grid" / m["elevation_file"], dtype="<i2", mode="r", shape=(m["nlat"], m["nlon"]))
        tid = np.memmap(OCEAN / "gebco/grid" / m["tid_file"], dtype="u1", mode="r", shape=(m["nlat"], m["nlon"]))
        _L[name] = (m, el, tid)
    return _L[name]


def _sample(lat, lon, which):
    """elevation at the nearest cell, per point, from the layer chosen by latitude; which = 'el' or 'tid'."""
    out = np.empty(len(lat))
    for name, sel in (("gebco_2026_nwpac", lat >= 30.0), ("gebco_2026", lat < 30.0)):
        if sel.any():
            m, el, tid = _grid(name); i, j = TG._ij(m, lat[sel], lon[sel])
            out[sel] = (el if which == "el" else tid)[i, j]
    return out


def bathy_along_composite(lat, lon, az):
    """tl_grid_run_j.bathy_along with the layer chosen per point (3 x 3 median, centre tid, +/-2 km corridor)."""
    nb = []
    for di in (-1, 0, 1):
        for dj in (-1, 0, 1):
            v = np.empty(len(lat))
            for name, sel in (("gebco_2026_nwpac", lat >= 30.0), ("gebco_2026", lat < 30.0)):
                if sel.any():
                    m, el, tid = _grid(name); i, j = TG._ij(m, lat[sel], lon[sel]); v[sel] = el[i + di, j + dj]
            nb.append(v)
    depth_med = np.median(np.stack(nb, 0), axis=0)
    t = _sample(lat, lon, "tid").astype(int)
    cmax = np.full(len(lat), -np.inf)
    for off in np.arange(-2000.0, 2000.1, 250.0):
        if off == 0:
            cmax = np.maximum(cmax, _sample(lat, lon, "el")); continue
        plon, plat, _ = TG.G.fwd(lon, lat, az + 90.0, np.full(len(lat), off))
        cmax = np.maximum(cmax, _sample(plat, plon, "el"))
    return depth_med, t, cmax


def woa_loader(subdir, decade, month):
    d = OCEAN / "woa23" / subdir
    m = json.loads((d / f"woa23_{decade}_m{month:02d}.json").read_text())
    shp = (m["nlat"], m["nlon"], len(m["depth_m"]))
    g = {k: np.fromfile(d / m[f"{k}_file"], dtype="<f4").reshape(shp) for k in ("c_mean", "c_sd", "sa", "ct")}
    return m, g


def install_loaders():
    TG.bathy_along = bathy_along_composite
    TG._G["w"] = woa_loader("soundspeed_nwpac", R.WOA_DECADE, R.WOA_MONTH)


def receivers():
    st = pd.read_csv(HERE.parent.parent / "data/stations.csv", comment="#")
    out = {}
    for n in ("H11N", "H11S"):
        g = st[st.triad == n]
        out[n] = dict(name=n, lat=float(g.latitude_deg.mean()), lon=float(g.longitude_deg.mean()), kind="ims", rcv_depth_m=float(g.hydrophone_depth_m.mean()))
    return out


def reference_profile():
    """run J median-region profile (U2): WOA23 A5B4 March at 37.5 S 89.5 E, columns as build_path's ssp."""
    import gsw
    keep = TG._G.get("w"); TG._G["w"] = woa_loader("soundspeed", R.U_REF["decade"], R.U_REF["month"])
    z, p = TG.woa_profile(R.U_REF["lat"], R.U_REF["lon"])
    TG._G["w"] = keep
    pr = gsw.p_from_z(-z, R.U_REF["lat"])
    return pd.DataFrame(dict(depth_m=z, t_insitu_c=gsw.t_from_CT(p["sa"], p["ct"], pr), sp_psu=gsw.SP_from_SA(p["sa"], pr, R.U_REF["lon"], R.U_REF["lat"]),
                             c_m_s=p["c_mean"], c_sd_m_s=p["c_sd"]))


def run_on_sections(name, bathy, ssp, rcv, bands, at_bin, work):
    """run_path's KRAKEN part on given sections (used for U2, where the ssp is modified)."""
    rprof, profiles = A.build_profiles(bathy, ssp)
    rd = float(min(rcv["rcv_depth_m"], profiles[-1][0] - 1.0)); L = rprof[-1]; wd = pathlib.Path(work) / name; rows = []
    for fc in bands:
        tag = f"f{fc:g}".replace(".", "p")
        try:
            r, tl, nm, dt = K.tl_path(wd, tag, fc, profiles, rprof, np.array([L]), R.SRC_DEPTHS, [rd], A.BOTTOMS["hard"], at_bin, fg=A.FG)
        except RuntimeError as e:
            for zs in R.SRC_DEPTHS:
                rows.append(dict(path=name, fc_hz=fc, src_depth_m=zs, tl_db=np.nan, status="no_modes" if "no modes" in str(e).lower() else "error"))
            continue
        s = K.read_shd(wd / f"{tag}.shd"); x = s["rr_m"] / 1000.0 / 6371.0; sph = 10 * np.log10(x / np.sin(x))
        for js, zs in enumerate(s["sz"]):
            rows.append(dict(path=name, fc_hz=fc, src_depth_m=float(zs), rcv_depth_m=rd, range_km=float(L), tl_db=float((-20 * np.log10(np.abs(s["p"][0, js, 0])) + sph)[-1]),
                             status="ok", n_modes_first=nm[0] if nm else -1, n_modes_min=min(nm) if nm else -1))
    shutil.rmtree(wd, ignore_errors=True)
    return rows


def job(args):
    kind, name, src, rcv, at_bin, work, pathdir = args
    os.environ["OMP_NUM_THREADS"] = "1"; install_loaders(); t0 = time.time()
    if kind == "std":
        rows, dt, tk = TG.run_path((name, src, rcv, R.BANDS, at_bin, work, True, pathdir, False))
        return [dict(r, path=name) for r in rows], time.time() - t0
    bathy, ssp, info = TG.build_path(src, rcv)
    ref = reference_profile(); ssp = ssp.copy()
    for k, g in ssp.groupby("node"):
        if float(g.range_km.iloc[0]) <= R.U_REPLACE_KM:
            idx = g.index
            for col in ("t_insitu_c", "sp_psu", "c_m_s", "c_sd_m_s"):
                ssp.loc[idx, col] = np.interp(g.depth_m.values, ref.depth_m.values, ref[col].values, left=np.nan, right=np.nan)
    ssp.to_csv(pathlib.Path(pathdir) / f"ssp_{name}.csv", index=False)
    return [dict(r, **{k: v for k, v in info.items() if k in ("range_km", "back_azimuth_deg")}) for r in run_on_sections(name, bathy, ssp, rcv, R.BANDS, at_bin, work)], time.time() - t0


def crosscheck(pathdir):
    out = {}
    for st in ("H11N", "H11S"):
        b = pd.read_csv(pathdir / f"bathy_f35a-{st}.csv"); e = pd.read_csv(EXPORT / f"f35a-{st}_bathymetry.csv")
        d_new = -np.interp(e.s_m.values / 1000.0, b.range_km.values, b.elevation_m.values); dd = d_new - e.depth_m.values
        s = pd.read_csv(pathdir / f"ssp_f35a-{st}.csv"); se = pd.read_csv(EXPORT / f"f35a-{st}_soundspeed.csv")
        m = se.merge(s, on=["node", "depth_m"], how="inner")
        dc = (m.c_m_s - m.c_mean_m_s).dropna()
        out[st] = dict(depth_abs_diff_median_m=float(np.median(np.abs(dd))), depth_abs_diff_p95_m=float(np.quantile(np.abs(dd), 0.95)),
                       c_abs_diff_median_m_s=float(np.median(np.abs(dc))) if len(dc) else None, c_abs_diff_p95_m_s=float(np.quantile(np.abs(dc), 0.95)) if len(dc) else None,
                       n_c_pairs=int(len(dc)), new_range_km=float(b.range_km.iloc[-1]), export_range_km=float(e.s_m.iloc[-1] / 1000.0))
    return out


def main(out_dir, at_bin, nproc=4):
    at_bin = os.path.abspath(at_bin); out = pathlib.Path(out_dir); out.mkdir(parents=True, exist_ok=True); pathdir = out / "paths"; pathdir.mkdir(exist_ok=True); work = out / "work"
    rc = receivers(); src0 = dict(id="f35a", lat=R.SRC["lat"], lon=R.SRC["lon"])
    az = TG.G.inv(src0["lon"], src0["lat"], rc["H11S"]["lon"], rc["H11S"]["lat"])[0]
    jobs = [("std", f"f35a-{st}", src0, rc[st], at_bin, str(work), pathdir) for st in ("H11S", "H11N")]
    jobs.append(("u2", "f35a-H11S-U2", src0, rc["H11S"], at_bin, str(work), pathdir))
    for dkm in (-8.0, 8.0):
        lon, lat, _ = TG.G.fwd(src0["lon"], src0["lat"], az, -dkm * 1000.0)     # +8 = 8 km farther from H11S
        s = dict(id=f"f35a{dkm:+.0f}km", lat=float(lat), lon=float(lon))
        for st in ("H11S", "H11N"):
            jobs.append(("std", f"f35a{dkm:+.0f}km-{st}", s, rc[st], at_bin, str(work), pathdir))
    t0 = time.time(); rows = []; secs = {}
    with Pool(nproc) as pool:
        for r, dt in pool.imap_unordered(job, jobs):
            rows.extend(r); secs[r[0]["path"]] = round(dt); print(r[0]["path"], round(dt), round(time.time() - t0), flush=True)
    df = pd.DataFrame(rows); df.to_csv(out / "step2_tl.csv", index=False)
    install_loaders(); cc = crosscheck(pathdir)
    json.dump(dict(prereg="prepare/metz_f35a/prereg.py @7dc315f", receivers=rc, seconds=secs, crosscheck_vs_9oct_export=cc, h11s_azimuth_deg=float(az)),
              open(out / "step2_tl_meta.json", "w"), indent=1)
    shutil.rmtree(work, ignore_errors=True); print("done", round(time.time() - t0))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else 4)
