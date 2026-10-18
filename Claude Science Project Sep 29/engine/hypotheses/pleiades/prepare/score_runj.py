"""Pléiades module on core run J (end of flight's run-j, both-burst supplementary set): per-impact columns and the H-conditional
00:19 two-factor table, in one read of each seed's impacts.

Per seed (SET, STRATUM, K):
  1. columns: build_columns.build_seed (exchange format v2, row-aligned with impacts32.npy), written under the exchange root;
  2. row mass per D x C cell: end of flight's option_table_0019.seed_terms UNCHANGED (its source is executed up to its final
     reduction, as composer-views-run-j/reduce_seed_views.py does): D0-D5 x {C1, C2 silent, competing-causes total q = 1/3 (C2
     silent)}, survival factor throughout, thinned files normalised by thinning.weight_sum_in (seed_terms does this itself).
     D0 of that table is D0' (00:19 values held out, transmission imposed: the log-on cause factor and the survival factor apply);
  3. under H: exact cell lookup on the module's wide surfaces (rho 0.25 two models GlobCurrent product-relative = headline;
     GLORYS12 only rho 0.25 beside; rho 0 / 0.5 two models as sensitivity). A row outside the computed support has zero
     likelihood under H (module convention); its share of the flight-only mass is recorded;
  4. sums per cell x setting: evidence scale, S, S2, mean position, families A1 / A2 / B / code 6, mass at >= 30 and >= 50 NM
     inside the arc (arc_distance_nm <= -30 / -50; the column is positive beyond the arc, away from the satellite);
     flight-only grid histograms (0.05 deg wide grid) per cell, for the tension and the close-ups.
Conditional on H; no identity likelihood; no Bayes factor or P(H | data).

    python score_runj.py seed  SET STRATUM K WORKDIR EXCHANGE_OUT        (SET = prod | both)
    python score_runj.py drive WORKDIR EXCHANGE_OUT NPROC                 (every task, skips finished ones; disk floor 15 GiB)
"""
import inspect
import json
import math
import os
import shutil
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ENGINE = HERE.parents[2]
sys.path.insert(0, str(HERE.parents[1] / "end-of-flight" / "smoke"))
sys.path.append(str(HERE))
import displacement_hist as DH  # noqa: E402
DH.SATCOM_CSV = (ENGINE / "data" / "satcom-observations.csv").resolve()
import option_table_0019 as OT  # noqa: E402
OT.SATCOM_CSV = DH.SATCOM_CSV
import build_columns as BC  # noqa: E402
import branch_eof289 as b  # noqa: E402

_src = inspect.getsource(OT.seed_terms); _src = _src[:_src.index("    out = {}")] + "    return cells, f4, g\n"
# Memory (18 Oct): build only the cells used here. The two loops below are seed_terms' own; only the q = 1 and C2-unpowered totals,
# which this module does not report, are skipped. Every arithmetic term of the cells kept is unchanged.
for a, bb in (("for q in (1 / 3, 1.0):", "for q in (1 / 3,):"), ('for other in ("C2 silent", "C2 unpowered"):', 'for other in ("C2 silent",):')):
    assert _src.count(a) == 1, a
    _src = _src.replace(a, bb)
_ns = dict(OT.__dict__); exec(_src, _ns); seed_cells = _ns["seed_terms"]

X = Path("/Users/pete/Downloads/mh370-exchange")
EOF = {"prod": X / "end-of-flight/run-j", "both": X / "end-of-flight/run-j-both-burst"}
CORE = X / "core/run-j"
SURF = X / "pleiades/run-i/surfaces"
STRATA = ["run-j-waypoints", "run-j-free", "run-j-descent-climb", "run-j-repro-radar"]
DS = [f"D{d}" for d in range(6)]
CAUSES = {"C1": "{d}xC1", "C2 silent": "{d}xC2 silent", "total q=1/3 (C2 silent)": "{d} total q=0.333 (C2 silent)"}
SETTINGS = {"none (without H)": None, "gcrel-0.25": ("0.25", "-gcrel", "mean"), "g12-0.25": ("0.25", "", 0),
            "gcrel-0": ("0", "-gcrel", "mean"), "gcrel-0.5": ("0.5", "-gcrel", "mean")}
FAMS = {"A1": (1,), "A2": (2,), "B": (3,), "code 6": (6,)}
NLAT, NLON = 800, 740; NCELL = NLAT * NLON
FLOOR_GIB = 15.0
COLUMNS_MIN_GIB = 18.0
COLUMNS_FOR = {("prod", "run-j-waypoints")}   # coordination DISK ALERT 01:13Z: other families' columns deferred for disk   # write a seed's columns (0.2-0.35 GB) only above this free space


def surfaces():
    out = {}
    for k, v in SETTINGS.items():
        if v is None:
            continue
        rho, tag, model = v
        m = dict(l.split(" = ", 1) for l in (SURF / f"joint-surface-rho{rho}{tag}.toml").read_text().splitlines() if " = " in l)
        assert int(m["nlat"]) == NLAT and int(m["nlon"]) == NLON
        J = np.fromfile(SURF / f"joint-surface-rho{rho}{tag}.f32", "<f4").reshape(2, NLAT, NLON).astype(float)
        J = np.where(np.isfinite(J), J, -np.inf)
        out[k] = (np.logaddexp(J[0], J[1]) - math.log(2.0)) if model == "mean" else J[model]
        out[k] = out[k].ravel()
        geo = (float(m["lat0"]), float(m["lon0"]), float(m["step_deg"]))
    return out, geo


def task_list():
    t = [("prod", s, int(p.name.split("-")[1])) for s in STRATA for p in sorted((EOF["prod"] / s).glob("seed-*")) if p.is_dir()]
    t += [("both", "run-j-waypoints", int(p.name.split("-")[1])) for p in sorted((EOF["both"] / "run-j-waypoints").glob("seed-*")) if p.is_dir()]
    big = {"run-j-waypoints": 0}
    return sorted(t, key=lambda x: (big.get(x[1], 1), x[0], x[2]))


def seed(set_, st, k, work, exch):
    t0 = time.time()
    work, exch = Path(work), Path(exch)
    work.mkdir(parents=True, exist_ok=True); outp = work / f"{set_}_{st}_{k}.npz"
    if outp.exists():
        return str(outp)
    sd = EOF[set_] / st / f"seed-{k}"
    cells, f4, g = seed_cells(sd, CORE / st / "bto-bfo" / f"seed-{k}" / "handoff-m0011" / "handoff.npy")
    keep = {(d, c): cells[key.format(d=d)] for d in DS for c, key in CAUSES.items()}; del cells
    # 1. columns (same reader g, so impacts32 is read once)
    mp, models, P, Cm = b.load_fields(SURF)
    croot = exch if set_ == "prod" else exch / "both-burst"
    free = shutil.disk_usage("/Users/pete").free / 2 ** 30
    if free >= COLUMNS_MIN_GIB and (set_, st) in COLUMNS_FOR:
        stat, sumline = BC.build_seed(sd, st, croot, (mp, P, Cm), g=g)
    else:   # columns deferred: scoring writes only a few MB; the columns can be rebuilt later by build_columns.py
        stat, sumline = {"stratum": st, "seed": k, "columns": "DEFERRED for disk (coordination 01:13Z)" if (set_, st) not in COLUMNS_FOR else f"DEFERRED (disk {free:.1f} GiB < {COLUMNS_MIN_GIB} GiB)"}, None
    del P, Cm
    # 2-4. sums
    L, (lat0, lon0, step) = surfaces()
    lat = np.asarray(g("latitude_deg"), float); lon = np.asarray(g("longitude_deg"), float); n = len(lat)
    arcd = np.asarray(g("arc_distance_nm"), float)
    i = np.floor((lat - (lat0 - step / 2)) / step).astype(np.int64); j = np.floor((lon - (lon0 - step / 2)) / step).astype(np.int64)
    inside = (i >= 0) & (i < NLAT) & (j >= 0) & (j < NLON)
    cell = np.where(inside, i * NLON + j, 0)
    LH = {"none (without H)": np.zeros(n)}
    for kk, Lg in L.items():
        LH[kk] = np.where(inside, Lg[cell], -np.inf)
    fam = {nm: np.isin(f4, codes) for nm, codes in FAMS.items()}
    in30, in50 = arcd <= -30.0, arcd <= -50.0
    res = {"set": set_, "stratum": st, "seed": k, "rows": n, "outside_grid_rows": int((~inside).sum()), "arc_nan_rows": int((~np.isfinite(arcd)).sum()),
           "fam_unlabelled_rows": int((~np.isin(f4, sum(FAMS.values(), ()))).sum()), "columns_stat": stat, "sha256": sumline, "cells": {}}
    H = {}
    for (d, c), a0 in keep.items():
        fin0 = np.isfinite(a0)
        if not fin0.any():
            res["cells"][f"{d} x {c}"] = None; continue
        s0 = float(a0[fin0].max()); m0 = np.where(fin0, np.exp(a0 - s0), 0.0)
        ent = {}
        for kk, lh in LH.items():
            with np.errstate(invalid="ignore"):
                a = a0 + lh
            fin = np.isfinite(a)
            if not fin.any():
                ent[kk] = None; continue
            s = float(a[fin].max()); m = np.where(fin, np.exp(a - s), 0.0)
            ent[kk] = dict(s=s, S=float(m.sum()), S2=float((m * m).sum()), lat=float((m * lat).sum()), lon=float((m * lon).sum()),
                           in30=float(m[in30].sum()), in50=float(m[in50].sum()),
                           fam={nm: [float(m[fk].sum()), float((m[fk] ** 2).sum()), float(m[fk & in30].sum()), float(m[fk & in50].sum())] for nm, fk in fam.items()},
                           not_computed_core_share=float(m0[~np.isfinite(lh)].sum() / m0.sum()))
        res["cells"][f"{d} x {c}"] = ent
        H[f"{d} x {c}|s"] = s0
        H[f"{d} x {c}|map"] = np.bincount(cell[inside & fin0], weights=m0[inside & fin0], minlength=NCELL).astype(np.float32)
        if c == "total q=1/3 (C2 silent)":
            for tag, msk in (("in30", in30), ("in50", in50)):
                sel = inside & fin0 & msk
                H[f"{d} x {c}|map_{tag}"] = np.bincount(cell[sel], weights=m0[sel], minlength=NCELL).astype(np.float32)
    res["wall_s"] = time.time() - t0
    tmp = work / f"{set_}_{st}_{k}.partial.npz"
    np.savez_compressed(tmp, res=json.dumps(res), **{kk: np.asarray(v) for kk, v in H.items()})
    os.replace(tmp, outp)
    print(f"{set_} {st} seed-{k} rows {n} {res['wall_s']:.0f} s", flush=True)
    return str(outp)


def _run(args):
    set_, st, k, work, exch = args
    free = shutil.disk_usage("/Users/pete").free / 2 ** 30
    if free < FLOOR_GIB + 0.5:
        return f"SKIPPED (disk {free:.1f} GiB) {set_} {st} {k}"
    try:
        return seed(set_, st, k, work, exch)
    except Exception as e:  # noqa: BLE001
        return f"FAILED {set_} {st} {k}: {e!r}"


def drive(work, exch, nproc, only=None):
    import multiprocessing as mpc
    Path(work).mkdir(parents=True, exist_ok=True)
    tasks = [(s, st, k, work, exch) for s, st, k in task_list() if only is None or (st == only) == (not only.startswith("not:")) and st != only[4:]]
    tasks = [t for t in tasks if not (Path(work) / f"{t[0]}_{t[1]}_{t[2]}.npz").exists()]
    print(len(tasks), "tasks", flush=True)
    with mpc.get_context("spawn").Pool(int(nproc), maxtasksperchild=1) as pool:
        for r in pool.imap_unordered(_run, tasks):
            print(time.strftime("%H:%M:%S"), r, f"disk {shutil.disk_usage('/Users/pete').free / 2 ** 30:.1f} GiB", flush=True)


if __name__ == "__main__":
    for v in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
        os.environ.setdefault(v, "1")
    if sys.argv[1] == "seed":
        seed(sys.argv[2], sys.argv[3], int(sys.argv[4]), sys.argv[5], sys.argv[6])
    else:
        drive(*sys.argv[2:6])
