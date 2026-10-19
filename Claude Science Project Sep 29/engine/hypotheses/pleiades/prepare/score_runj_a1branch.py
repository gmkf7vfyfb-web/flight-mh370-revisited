"""Pléiades module, overnight order B2 (19 Oct 2026): columns under H for end of flight's A1-branch conditional pass, and the
per-seed sums for the stratified estimator under H.

Run J recipe unchanged (score_runj.py): row mass per D x C cell is end of flight's option_table_0019.seed_terms (as score_runj's
seed_cells, the same skips), H factor by exact cell lookup on the wide surfaces, settings as score_runj.SETTINGS. Columns: the run J
builder (build_columns.build_seed), written for the A1-branch set only (production columns already exist).

Branch (end of flight, results/eof-a1-branch-oct18): onset flame-out-associated and control realised "no intervention"
    (latent:onset_mechanism == 2) & (latent:control_realised == 2).
Per seed and set (a1 = the A1-branch pass; prod = run J waypoints production; both = run J both-burst set), for every D x C cell and
setting: sums S, S2 of the row mass m over the masks below, the parent-aggregated sum of squares (distinct-parent ESS), mean position,
latitude histograms (0.05 deg, wide grid) and, flight only, the 2-D grid maps of all rows and branch rows for the total q = 1/3 cell.
Conditional on H; no identity likelihood; no Bayes factor or P(H | data).

    python score_runj_a1branch.py drive WORKDIR EXCHANGE_OUT NPROC
"""
import json
import os
import shutil
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import score_runj as SR  # noqa: E402
import build_columns as BC  # noqa: E402
import branch_eof289 as b  # noqa: E402

X = SR.X
ROOT = {"a1": X / "end-of-flight/run-j-a1branch", "prod": SR.EOF["prod"], "both": SR.EOF["both"]}
ST = "run-j-waypoints"
SR.SURF = X / "pleiades/run-j/surfaces"   # copy of run-i/surfaces (16 files re-verified against pleiades/run-j/SHA256SUMS, 19 Oct)
FLOOR_GIB = 25.0         # stricter original shared-rule floor kept (work order 7e081d4b allows 5 GB; this order does not need it)
CAP_BYTES = 2.0e9        # order B2 disk cap
HIST_SETTINGS = ("none (without H)", "gcrel-0.25", "g12-0.25")
MAP_D = ("D0", "D3", "D4", "D5")
MAP_C = "total q=1/3 (C2 silent)"


def masks(g, f4):
    br = (np.asarray(g("latent:onset_mechanism")) == 2) & (np.asarray(g("latent:control_realised")) == 2)
    return {"all": np.ones(len(f4), bool), "branch": br, "A1": f4 == 1, "A1_out": (f4 == 1) & ~br, "A2": f4 == 2, "B": f4 == 3,
            "code 6": f4 == 6}


def seed(set_, k, work, exch):
    t0 = time.time(); work = Path(work); outp = work / f"{set_}_{k}.npz"
    if outp.exists():
        return str(outp)
    sd = ROOT[set_] / ST / f"seed-{k}"
    cells, f4, g = SR.seed_cells(sd, SR.CORE / ST / "bto-bfo" / f"seed-{k}" / "handoff-m0011" / "handoff.npy")
    keep = {(d, c): cells[key.format(d=d)] for d in SR.DS for c, key in SR.CAUSES.items()}; del cells
    stat = sumline = None
    if set_ == "a1":
        used = sum(f.stat().st_size for f in (exch / ST).rglob("*") if f.is_file()) if (exch / ST).exists() else 0
        free = shutil.disk_usage("/Users/pete").free / 2 ** 30
        if free < FLOOR_GIB + 1 or used > CAP_BYTES - 0.4e9:
            stat = {"seed": k, "columns": f"PAUSED (free {free:.1f} GiB, used {used / 1e9:.2f} GB)"}
        else:
            mp, models, P, Cm = b.load_fields(SR.SURF)
            stat, sumline = BC.build_seed(sd, ST, exch, (mp, P, Cm), g=g)
            del P, Cm
    L, (lat0, lon0, step) = SR.surfaces()
    lat = np.asarray(g("latitude_deg"), float); lon = np.asarray(g("longitude_deg"), float); n = len(lat)
    par = np.asarray(g("parent")).astype(np.int64)
    i = np.floor((lat - (lat0 - step / 2)) / step).astype(np.int64); j = np.floor((lon - (lon0 - step / 2)) / step).astype(np.int64)
    inside = (i >= 0) & (i < SR.NLAT) & (j >= 0) & (j < SR.NLON)
    cell = np.where(inside, i * SR.NLON + j, 0); ib = np.clip(i, 0, SR.NLAT - 1)
    LH = {"none (without H)": np.zeros(n)}
    for kk, Lg in L.items():
        LH[kk] = np.where(inside, Lg[cell], -np.inf)
    M = masks(g, f4)
    res = {"set": set_, "stratum": ST, "seed": k, "rows": n, "branch_rows": int(M["branch"].sum()),
           "branch_row_fraction": float(M["branch"].mean()), "distinct_parents": int(len(np.unique(par))),
           "outside_grid_rows": int((~inside).sum()), "columns_stat": stat, "sha256": sumline, "cells": {}}
    H = {}
    for (d, c), a0 in keep.items():
        ck = f"{d} x {c}"; ent = {}
        for kk, lh in LH.items():
            with np.errstate(invalid="ignore"):
                a = a0 + lh
            fin = np.isfinite(a)
            if not fin.any():
                ent[kk] = None; continue
            s = float(a[fin].max()); m = np.where(fin, np.exp(a - s), 0.0)
            e = {"s": s}
            for nm, mk in M.items():
                mm = m[mk]
                e[nm] = [float(mm.sum()), float((mm * mm).sum()), float((mm * lat[mk]).sum()), float((mm * lon[mk]).sum())]
                if nm in ("all", "branch", "A1", "A1_out"):
                    ps = np.bincount(par[mk], mm); e[nm].append(float((ps * ps).sum()))
                if kk in HIST_SETTINGS and nm in ("all", "branch", "A1", "A1_out"):
                    H[f"{ck}|{kk}|{nm}|hist"] = np.bincount(ib[mk & inside], weights=m[mk & inside], minlength=SR.NLAT)
            ent[kk] = e
            if kk == "none (without H)" and c == MAP_C and d in MAP_D:
                for nm in ("all", "branch"):
                    sel = M[nm] & inside & fin
                    H[f"{ck}|{nm}|map"] = np.bincount(cell[sel], weights=m[sel], minlength=SR.NCELL).astype(np.float32)
        res["cells"][ck] = ent
    res["wall_s"] = time.time() - t0
    tmp = work / f"{set_}_{k}.partial.npz"
    np.savez_compressed(tmp, res=json.dumps(res), **H)
    os.replace(tmp, outp)
    print(f"{set_} seed-{k} rows {n} branch {res['branch_row_fraction']:.4f} {res['wall_s']:.0f} s", flush=True)
    return str(outp)


def _run(args):
    set_, k, work, exch = args
    free = shutil.disk_usage("/Users/pete").free / 2 ** 30
    if free < FLOOR_GIB + 0.5:
        return f"PAUSED (disk {free:.1f} GiB) {set_} {k}"
    try:
        return seed(set_, k, work, exch)
    except Exception as e:  # noqa: BLE001
        import traceback
        return f"FAILED {set_} {k}: {e!r}\n{traceback.format_exc()}"


def drive(work, exch, nproc):
    import multiprocessing as mpc
    work, exch = Path(work), Path(exch); work.mkdir(parents=True, exist_ok=True)
    tasks = [(s, int(p.name.split("-")[1]), work, exch) for s in ("a1", "both", "prod")
             for p in sorted((q for q in (ROOT[s] / ST).glob("seed-*") if q.is_dir()), key=lambda p: int(p.name.split("-")[1]))]
    tasks = [t for t in tasks if not (work / f"{t[0]}_{t[1]}.npz").exists()]
    print(len(tasks), "tasks", flush=True)
    with mpc.get_context("spawn").Pool(int(nproc), maxtasksperchild=1) as pool:
        for r in pool.imap_unordered(_run, tasks):
            print(time.strftime("%H:%M:%S"), r, f"disk {shutil.disk_usage('/Users/pete').free / 2 ** 30:.1f} GiB", flush=True)


if __name__ == "__main__":
    for v in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
        os.environ.setdefault(v, "1")
    if sys.argv[1] == "seed":
        seed(sys.argv[2], int(sys.argv[3]), Path(sys.argv[4]), Path(sys.argv[5]))
    else:
        drive(sys.argv[2], sys.argv[3], sys.argv[4])
