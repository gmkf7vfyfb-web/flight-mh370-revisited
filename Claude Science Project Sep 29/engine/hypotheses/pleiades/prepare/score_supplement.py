"""Pléiades module, overnight order B2 (20 Oct 2026): the run J northern supplement (all rows, rule B) under H.

End of flight's combination is used UNCHANGED: rows, treatments and weights come from its own `smoke/supplement_combine.py`
(`pooled`, `row_terms`, `r_hat`, the rule-B betas, the 64:256 extra-descent pooling, the two halves of a supplement seed as one
replicate). This script only multiplies each row's mass by the Pléiades factor L_H (exact cell lookup on the module's wide surfaces,
as `score_runj.py`) and keeps the same accumulators per setting, plus the mean position and, flight only, a 0.05 deg grid map
per treatment (for the tension). The longitude of each row is read from the same compact file in the same row order (checked).

Parts (one per replicate, as end of flight's):  main  prod-<k> (run J waypoints 1-24) and supp-<s> (supplement 1001-1016: north-k2 +
north-k2b with their xd256 groups); b1 (A1 branch 1, rule B: run-j-a1branch 1-8 + north-k2-a1branch 1001-1016); b2 (A1 outside
the branch, run-j-a1outside 1-8, production alone). Constants per set as end of flight's notes (oct19 section 7 item 4, oct20 section 1).
Conditional on H; no identity likelihood; no Bayes factor or P(H | data).

    python score_supplement.py drive WORKDIR NPROC
"""
import json
import math
import os
import shutil
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "end-of-flight" / "smoke"))
import supplement_combine as SC  # noqa: E402
from compact_impacts import load  # noqa: E402

X = Path("/Users/pete/Downloads/mh370-exchange")
SUP = X / "end-of-flight/run-j-supplement"
CORE = X / "core/run-j/run-j-waypoints/bto-bfo"
SURF = X / "pleiades/run-j/surfaces"          # copy of run-i/surfaces (hashes in pleiades/run-j/SHA256SUMS)
SETTINGS = {"none": None, "gcrel-0.25": ("0.25", "-gcrel", "mean"), "g12-0.25": ("0.25", "", 0)}
NLAT, NLON = 800, 740; NCELL = NLAT * NLON
FLOOR_GIB = 5.0                                   # work order 20 Oct header
CONST = {"main": dict(SUP_S1=24, SUP_S2=16, SUP_N1=2399999, SUP_N2=1600003, SUP_K=1),
         "b1": dict(SUP_S1=8, SUP_S2=16, SUP_N1=799999, SUP_N2=800004, SUP_K=2),
         "b2": dict(SUP_S1=8, SUP_S2=16, SUP_N1=799999, SUP_N2=1600003, SUP_K=1)}   # b2: production alone only

LON_LOG = []
_orig_row_terms = SC.row_terms


def _row_terms(sd, handoff):
    R = _orig_row_terms(sd, handoff)
    meta, g = load(sd); lat = np.asarray(g("latitude_deg")); lon = np.asarray(g("longitude_deg"))
    assert len(lat) == len(R["lat"]) and np.array_equal(lat, np.asarray(R["lat"])), sd
    LON_LOG.append(lon)
    return R


SC.row_terms = _row_terms


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
        out[k] = ((np.logaddexp(J[0], J[1]) - math.log(2.0)) if model == "mean" else J[model]).ravel()
        geo = (float(m["lat0"]), float(m["lon0"]), float(m["step_deg"]))
    return out, geo


def cells_of(lat, lon, geo):
    lat0, lon0, step = geo
    i = np.floor((lat - (lat0 - step / 2)) / step).astype(np.int64); j = np.floor((lon - (lon0 - step / 2)) / step).astype(np.int64)
    ok = (i >= 0) & (i < NLAT) & (j >= 0) & (j < NLON)
    return np.where(ok, i * NLON + j, 0), ok


def part(set_, tech, specs, outp):
    """As supplement_combine.part (same weights and accumulators), for every setting; plus mean position and flight-only maps."""
    t0 = time.time(); c = CONST[set_]
    S1, S2, N1, N2, K = (float(c[v]) for v in ("SUP_S1", "SUP_S2", "SUP_N1", "SUP_N2", "SUP_K"))
    L, geo = surfaces(); T = None; nh = 0
    for j, (sd_j, hf_j, xd_j) in enumerate(specs):
        LON_LOG.clear()
        Tj, nhj, ij = SC.pooled(sd_j, hf_j, xd_j); nh += nhj
        base_lon = LON_LOG[0]; xd_lon = np.concatenate(LON_LOG) if len(LON_LOG) > 1 else base_lon
        Tj = {d: (v[0], v[1], v[2], v[3] + j * 10_000_000, v[4], v[5], v[6],
                  xd_lon if (d in SC.XD_CELLS and len(LON_LOG) > 1) else base_lon) for d, v in Tj.items()}
        for d, v in Tj.items():
            assert len(v[7]) == len(v[0]), (d, len(v[7]), len(v[0]))
        T = Tj if T is None else {d: tuple(np.concatenate([T[d][i], Tj[d][i]]) for i in range(8)) for d in T}
    nb = len(SC.BANDS) - 1; nf = len(SC.FINE) - 1
    out = {"n_rows": len(T["D0"][1]), "n_handoff": nh}
    nc = {}
    for d, (t, lat, lat0, par, fam, state, br, lon) in T.items():
        r = SC.r_hat(lat0); beta1 = N1 / (N1 + N2 * r); beta2 = N2 * r / (N1 + N2 * r)
        cw = {"alone": np.full(len(lat), 1.0 / S1), "comb": beta1 / S1} if tech == "prod" else {"comb": beta2 * K / S2}
        if set_ == "b2":
            cw = {"alone": cw["alone"]}
        cell, ok = cells_of(lat, lon, geo)
        fi = np.clip(np.floor((lat - SC.FINE[0]) / 0.1 + 1e-9).astype(int), 0, nf - 1)
        bi = np.digitize(lat, SC.BANDS) - 1; inb = (bi >= 0) & (bi < nb)
        for s in SETTINGS:
            lh = np.zeros(len(t)) if s == "none" else np.where(ok, L[s][cell], -np.inf)
            for v, cv in cw.items():
                k0 = f"{s}|{v}/{d}"
                with np.errstate(invalid="ignore"):
                    a = t + lh
                m = np.zeros(len(t)); fin = np.isfinite(a); m[fin] = np.exp(a[fin]) * cv[fin]
                out[f"{k0}/imp/m"] = np.stack([np.bincount(fi[fam == q], m[fam == q], nf) for q in range(4)])
                out[f"{k0}/imp/m2"] = np.stack([np.bincount(fi[fam == q], m[fam == q] ** 2, nf) for q in range(4)])
                for kb in (1, 2):
                    sel = (br == kb) & inb
                    out[f"{k0}/imp/br{kb}"] = np.bincount(bi[sel], m[sel], nb)
                    out[f"{k0}/imp/br{kb}m2"] = np.bincount(bi[sel], m[sel] ** 2, nb)
                    sel = sel & (fam == 0)
                    out[f"{k0}/imp/br{kb}A1"] = np.bincount(bi[sel], m[sel], nb)
                    out[f"{k0}/imp/br{kb}A1m2"] = np.bincount(bi[sel], m[sel] ** 2, nb)
                for q, fsel in (("all", None), ("A1", 0), ("A2", 1), ("B", 2)):
                    mm = m if fsel is None else np.where(fam == fsel, m, 0.0)
                    out[f"{k0}/imp/par2/{q}"] = SC.group_sq(par, bi, mm, nb)
                    out[f"{k0}/imp/st2/{q}"] = SC.group_sq(state, bi, mm, nb)
                out[f"{k0}/pos"] = np.array([m.sum(), (m * lat).sum(), (m * lon).sum()])
                if s == "none":
                    out[f"{k0}/map"] = np.bincount(cell[ok & fin], m[ok & fin], NCELL).astype(np.float32)
                    nc[f"{v}/{d}"] = float(m[~ok].sum() / m.sum()) if m.sum() > 0 else 0.0
    out["outside_grid_mass_share"] = json.dumps(nc); out["wall_s"] = time.time() - t0
    tmp = str(outp) + ".partial.npz"
    np.savez_compressed(tmp, **out); os.replace(tmp, outp)
    print(f"{set_} {tech} {Path(outp).name}: {out['n_rows']} rows {out['wall_s']:.0f} s", flush=True)
    return str(outp)


def tasks(work):
    T = []
    for k in range(1, 25):
        T.append(("main", "prod", [(str(X / f"end-of-flight/run-j/run-j-waypoints/seed-{k}"), str(CORE / f"seed-{k}/handoff-m0011/handoff.npy"), None)], work / f"main-prod-{k}.npz"))
    for s in range(1001, 1017):
        sp = []
        for h, xd in (("north-k2", "north-k2-xd256"), ("north-k2b", "north-k2b-xd256")):
            sd = SUP / h / f"seed-{s}"; xdd = SUP / xd / f"seed-{s}"
            sp.append((str(sd), str(sd / "handoff-subset.npy"), str(xdd) if xdd.is_dir() else None))
        T.append(("main", "supp", sp, work / f"main-supp-{s}.npz"))
    for k in range(1, 9):
        T.append(("b1", "prod", [(str(X / f"end-of-flight/run-j-a1branch/run-j-waypoints/seed-{k}"), str(CORE / f"seed-{k}/handoff-m0011/handoff.npy"), None)], work / f"b1-prod-{k}.npz"))
        T.append(("b2", "prod", [(str(SUP / f"run-j-a1outside/seed-{k}"), str(CORE / f"seed-{k}/handoff-m0011/handoff.npy"), None)], work / f"b2-prod-{k}.npz"))
    for s in range(1001, 1017):
        sd = SUP / "north-k2-a1branch" / f"seed-{s}"
        T.append(("b1", "supp", [(str(sd), str(sd / "handoff-subset.npy"), None)], work / f"b1-supp-{s}.npz"))
    return [t for t in T if not Path(t[3]).exists()]


def _run(a):
    free = shutil.disk_usage("/Users/pete").free / 2 ** 30
    if free < FLOOR_GIB + 1:
        return f"PAUSED (disk {free:.1f} GiB) {a[3]}"
    try:
        return part(*a)
    except Exception as e:  # noqa: BLE001
        import traceback
        return f"FAILED {a[3]}: {e!r}\n{traceback.format_exc()}"


def drive(work, nproc):
    import multiprocessing as mpc
    work = Path(work); work.mkdir(parents=True, exist_ok=True); T = tasks(work)
    T.sort(key=lambda t: (t[0] != "main" or t[1] != "supp"))     # the big supplement parts first
    print(len(T), "tasks", flush=True)
    with mpc.get_context("spawn").Pool(int(nproc), maxtasksperchild=1) as pool:
        for r in pool.imap_unordered(_run, T):
            print(time.strftime("%H:%M:%S"), r, f"disk {shutil.disk_usage('/Users/pete').free / 2 ** 30:.1f} GiB", flush=True)


if __name__ == "__main__":
    for v in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
        os.environ.setdefault(v, "1")
    if sys.argv[1] == "one":
        work = Path(sys.argv[2]); T = [t for t in tasks(work) if Path(t[3]).name == sys.argv[3]]; part(*T[0])
    else:
        drive(sys.argv[2], sys.argv[3])
