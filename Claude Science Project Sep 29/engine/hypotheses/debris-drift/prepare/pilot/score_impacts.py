"""Score end of flight's impact samples against a drift node surface (architecture, 9 Oct ~14:45 UTC).

Reads a merged drift run (`nodes.csv` + `summary.toml`) and one end-of-flight seed directory, and
for every data option x log-on cause (end of flight's own recipe, imported read-only from
`hypotheses/end-of-flight/smoke/displacement_hist.py::option_posteriors`) reports, per drift
bandwidth column, the impact-posterior mass that is
  scored (flag 1), outside the drift surface's support (flag 0), Monte Carlo unresolved (flag 2),
exactly as `interpolate.rs::Surface::ln_likelihood` classifies a point (bilinear in LIKELIHOOD over
the four corners; land corners renormalised out; any positive-weight corner that is unresolved
makes the point unresolved, not computed or off-grid makes it outside support; never
extrapolate). On the scored mass only, it also reports the impact median latitude before and after
multiplying by the drift likelihood. That is a DIAGNOSTIC of the interface, not a posterior: the
unscored mass is excluded, and a pilot surface is never evidence.

Usage: python score_impacts.py <drift-run-dir> <eof-run-dir> <seed-dir> <out.json>
           [--recipe <end-of-flight smoke dir>] [--constraints alive,silent] [--support-only]

--recipe: where end of flight's `displacement_hist.py` lives (default <eof-run>/../../hypotheses/end-of-flight/smoke;
  the exchange layout, mh370-exchange/end-of-flight/next-run/<stratum>/seed-k with run.json in the seed dir,
  needs it given explicitly, and <eof-run-dir> may then be the seed dir itself).
--constraints: end of flight's declared variants passed to option_posteriors (keys gain "+<name>").
--support-only: treat every node in <drift-run-dir>/nodes.csv as scored with ln L = 0 (e.g. the count run's
  planned node list), so "scored" reads "inside the planned support" before the surface is complete.
"""
import json
import pathlib
import sys
import tomllib

import numpy as np
import pandas as pd


def surface_arrays(run, col):
    df = pd.read_csv(f"{run}/nodes.csv")
    with open(f"{run}/summary.toml", "rb") as f:
        g = tomllib.load(f)["grid"]
    nlat, nlon = int(g["nlat"]), int(g["nlon"])
    # state codes: 0 not computed, 1 value, 2 land, 3 unresolved (per bandwidth column)
    state = np.zeros(nlat * nlon, np.int8)
    val = np.full(nlat * nlon, np.nan)
    k = df.node.values.astype(int)
    land = (df.state == "land").values
    v = df[col].values
    state[k] = np.where(land, 2, np.where(np.isfinite(v), 1, 3))
    val[k] = v
    return g, nlat, nlon, state, val


def support_arrays(run):
    g, nlat, nlon, state, val = surface_arrays(run, "ln_l")
    df = pd.read_csv(f"{run}/nodes.csv")
    k = df.node.values.astype(int)
    land = (df.state == "land").values
    state[k] = np.where(land, 2, 1)
    val[k] = np.where(land, np.nan, 0.0)
    return g, nlat, nlon, state, val


def lookup(g, nlat, nlon, state, val, lat, lon):
    fi = (lat - g["lat0"]) / g["dlat"]
    fj = (lon - g["lon0"]) / g["dlon"]
    flag = np.zeros(lat.size, np.int8)  # 0 outside, 1 scored, 2 unresolved
    out = np.full(lat.size, np.nan)
    ok = (fi >= 0) & (fj >= 0) & (fi <= nlat - 1) & (fj <= nlon - 1) & np.isfinite(fi) & np.isfinite(fj)
    i = np.minimum(np.floor(np.where(ok, fi, 0)).astype(int), nlat - 2)
    j = np.minimum(np.floor(np.where(ok, fj, 0)).astype(int), nlon - 2)
    ti, tj = np.where(ok, fi - i, 0.0), np.where(ok, fj - j, 0.0)
    corners = [(i, j, (1 - ti) * (1 - tj)), (i + 1, j, ti * (1 - tj)), (i, j + 1, (1 - ti) * tj), (i + 1, j + 1, ti * tj)]
    # Same order as the Rust loop: off-grid -> outside; then corners in order, where the first
    # positive-weight corner that is unresolved (-> 2) or not computed (-> 0) decides.
    decided = ~ok
    flag[decided] = 0
    ws = np.zeros(lat.size)
    lref = np.full(lat.size, -np.inf)
    S, V, W = [], [], []
    for ci, cj, w in corners:
        idx = ci * nlon + cj
        s, v = state[idx], val[idx]
        pos = w > 0
        hit2 = ~decided & pos & (s == 3)
        hit0 = ~decided & pos & (s == 0)
        flag[hit2], flag[hit0] = 2, 0
        decided |= hit2 | hit0
        good = pos & (s == 1)
        S.append(good), V.append(np.where(good, v, -np.inf)), W.append(np.where(good, w, 0.0))
        ws += np.where(good, w, 0.0)
        lref = np.maximum(lref, np.where(good, v, -np.inf))
    acc = np.zeros(lat.size)
    for good, v, w in zip(S, V, W):
        acc += np.where(good, w / np.where(ws > 0, ws, 1) * np.exp(v - np.where(np.isfinite(lref), lref, 0)), 0.0)
    flag[~decided & (ws == 0)] = 0
    flag[~decided & (ws > 0)] = 1
    sc = flag == 1
    out[sc] = lref[sc] + np.log(acc[sc])
    return flag, out


def wmedian(x, w):
    o = np.argsort(x)
    c = np.cumsum(w[o])
    return float(x[o][np.searchsorted(c, 0.5 * c[-1])])


def main(drift_run, eof_run, seed_dir, out, recipe=None, constraints=(), support_only=False):
    sys.path.insert(0, recipe or str(pathlib.Path(eof_run).parents[1] / "hypotheses" / "end-of-flight" / "smoke"))
    from displacement_hist import option_posteriors  # end of flight's recipe, read-only

    cols = [c for c in ("ln_l", "ln_l_h25", "ln_l_h100", "ln_l_h200") if c in pd.read_csv(f"{drift_run}/nodes.csv", nrows=1).columns]
    if support_only:
        cols = ["ln_l"]
        surfs = {"ln_l": support_arrays(drift_run)}
    else:
        surfs = {c: surface_arrays(drift_run, c) for c in cols}
    res = {"label": ("SUPPORT CHECK: planned drift nodes (ln L = 0) on end-of-flight impacts; 'scored' = inside planned support."
                     if support_only else "INTERFACE DIAGNOSTIC: drift node surface scored on end-of-flight impacts. Never evidence."),
           "drift_run": str(drift_run), "eof_seed": str(seed_dir), "constraints": list(constraints), "options": {}}
    cache = {}
    kw = {"constraints": tuple(constraints)} if constraints else {}
    for key, p, c in option_posteriors(pathlib.Path(eof_run), pathlib.Path(seed_dir), **kw):
        lat, lon = c["lat"], c["lon"]
        r = {"impact_median_lat": wmedian(lat[p > 0], p[p > 0]), "by_bandwidth": {}}
        for col in cols:
            if col not in cache:
                cache[col] = lookup(*surfs[col], lat, lon)
            flag, ll = cache[col]
            m = {name: float(p[flag == f].sum()) for name, f in (("scored", 1), ("outside_support", 0), ("mc_unresolved", 2))}
            if m["scored"] > 0:
                s = flag == 1
                q = p[s] * np.exp(ll[s] - ll[s].max())
                m["scored_median_lat_before"] = wmedian(lat[s], p[s])
                m["scored_median_lat_after_diagnostic"] = wmedian(lat[s], q)
                m["scored_ess_fraction"] = float(q.sum() ** 2 / (q ** 2).sum() / (p[s].sum() ** 2 / (p[s] ** 2).sum()))
            r["by_bandwidth"][col] = m
        res["options"][key] = r
    pathlib.Path(out).write_text(json.dumps(res, indent=1))


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    for a in ("drift_run", "eof_run", "seed_dir", "out"):
        ap.add_argument(a)
    ap.add_argument("--recipe"); ap.add_argument("--constraints", default=""); ap.add_argument("--support-only", action="store_true")
    a = ap.parse_args()
    main(a.drift_run, a.eof_run, a.seed_dir, a.out, a.recipe, [c for c in a.constraints.split(",") if c], a.support_only)
