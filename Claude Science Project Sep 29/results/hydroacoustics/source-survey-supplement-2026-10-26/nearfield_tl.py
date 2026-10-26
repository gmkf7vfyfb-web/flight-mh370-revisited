"""Module TL chain (tl_grid_run_j.run_path, unchanged; loaders of metz_f35a/step2_tl.install_loaders: GEBCO 2026 NW Pacific
layer, WOA23 B5C2 April) on the F-35A near-field paths to the four Off Kushiro-Tokachi hydrophones.
Receivers: positions read from Metz Fig. 1A (graticule 317.5 px/deg, marker bounding-box centre, +/-~2 km), receiver
2 m above the seabed (module IMOS rule). Sources: (P) 40.4496 N 142.9237 E = the point 180 km from DSOH, 255 km from KSP3
and 134.7 km from Misawa (Metz's stated ranges); (W) module working point 40.64 N 142.96 E (sensitivity).
Bottom: module 'hard' (cp 1650, rho 1.9, 0.5 dB/lambda) and 'soft' (cp 1560, rho 1.5, 1.0 dB/lambda) as sensitivity.
Usage: python nearfield_tl.py <hydro_module_dir> <at_bin> <out_dir>
"""
import sys, os, pathlib, json, time, shutil
from concurrent.futures import ThreadPoolExecutor
import numpy as np, pandas as pd
mod, at_bin, out = pathlib.Path(sys.argv[1]), os.path.abspath(sys.argv[2]), pathlib.Path(sys.argv[3]); out.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(mod / "prepare" / "metz_f35a")); sys.path.insert(0, str(mod / "prepare"))
import prereg as R, step2_tl as S2, tl_grid_run_j as TG, air9_tl_validation as A, kraken_tl as K
S2.install_loaders()
STA = {"DSOH": (41.6630, 144.3433), "KSP1": (41.6835, 144.3953), "KSP2": (41.9370, 145.0598), "KSP3": (42.2504, 144.8142)}
SRCS = {"P": (40.4496, 142.9237), "W": (40.64, 142.96)}
FORCE_DROP = len(sys.argv) > 4 and sys.argv[4] == "force_drop"
pathdir = out / "paths"; pathdir.mkdir(exist_ok=True); work = out / "work"
def one(args):
    sid, st, bname = args
    src = dict(id=sid, lat=SRCS[sid][0], lon=SRCS[sid][1]); rcv = dict(name=st, lat=STA[st][0], lon=STA[st][1], kind="imos")
    name = f"f35a{sid}-{st}-{bname}"; t0 = time.time()
    bathy, ssp, info = TG.build_path(src, rcv)
    bathy.to_csv(pathdir / f"bathy_{name}.csv", index=False); ssp.to_csv(pathdir / f"ssp_{name}.csv", index=False)
    rprof, profiles = A.build_profiles(bathy, ssp)
    rd = float(min(info["end_depth_m"], profiles[-1][0]) - 2.0); rd = float(min(rd, profiles[-1][0] - 1.0)); L = rprof[-1]
    rows = []; wd = work / name
    for fc in R.BANDS:
        tag = f"f{fc:g}".replace(".", "p")
        # FIELD (at_2026_8_29 build) aborts deterministically in ReadModes for some profile counts (rc -6, 'fort.30');
        # dropping any one interior profile clears it. Fallback: drop the mid-path profile, then its neighbour.
        # FORCE_DROP (validation): run every band with the mid profile dropped, to measure the effect on TL.
        status = None
        for drop in ((None,) if not FORCE_DROP else ()) + (len(profiles) // 2, len(profiles) // 2 + 1):
            pr_ = profiles if drop is None else [p for i, p in enumerate(profiles) if i != drop]
            rp_ = rprof if drop is None else np.delete(rprof, drop)
            try:
                r, tl, nm, dt = K.tl_path(wd, tag, fc, pr_, rp_, np.array([L]), R.SRC_DEPTHS, [rd], A.BOTTOMS[bname], at_bin, fg=A.FG)
                status = "ok" if drop is None else f"ok_dropped_profile_{drop}_of_{len(profiles)}"; break
            except RuntimeError as e:
                err = str(e)[:80]
        if status is None:
            rows += [dict(path=name, source=sid, station=st, bottom=bname, fc_hz=fc, src_depth_m=z, tl_db=np.nan, status=err) for z in R.SRC_DEPTHS]; continue
        s = K.read_shd(wd / f"{tag}.shd"); x = s["rr_m"] / 1000.0 / 6371.0; sph = 10 * np.log10(x / np.sin(x))
        for js, zs in enumerate(s["sz"]):
            rows.append(dict(path=name, source=sid, station=st, bottom=bname, fc_hz=fc, src_depth_m=float(zs), rcv_depth_m=rd, range_km=float(L),
                             src_water_depth_m=float(profiles[0][0]), end_depth_m=info["end_depth_m"], min_track_depth_m=info["min_track_depth_m"],
                             tl_db=float((-20 * np.log10(np.abs(s["p"][0, js, 0])) + sph)[-1]), status=status, n_modes_first=nm[0] if nm else -1))
    shutil.rmtree(wd, ignore_errors=True)
    return rows, name, time.time() - t0
jobs = [(s, st, b) for s in SRCS for st in STA for b in ("hard", "soft")]
rows = []; t0 = time.time()
with ThreadPoolExecutor(1) as ex:
    for r, name, dt in ex.map(one, jobs):
        rows += r; print(name, round(dt), flush=True)
D = pd.DataFrame(rows); D.to_csv(out / "nearfield_tl.csv", index=False)
print(D[(D.status.str.startswith("ok")) & (D.bottom == "hard") & (D.source == "P")].pivot_table(index=["station", "src_depth_m"], columns="fc_hz", values="tl_db").round(1).to_string())
print(D.groupby(["source", "station"])[["range_km", "src_water_depth_m", "end_depth_m", "rcv_depth_m"]].first().round(1).to_string()); print("done", round(time.time() - t0))
