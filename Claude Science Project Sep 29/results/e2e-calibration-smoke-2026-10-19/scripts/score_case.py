"""Calibration statistics for one smoke case (protocol 5): per data option D0-D5 x factor stack, pooled over replicates by
evidence (as option_table_0019.py) and per replicate (Monte Carlo noise). Usage: score_case.py CASE_DIR NODE_DIR FIELDS AUDIT"""
import sys, json, glob, pathlib, math
import numpy as np
from scipy.special import logsumexp
from e2e_terms import terms, Search, Drift
R_AUTH = 6371.0072; DZ = 769.3 / (R_AUTH ** 2 * math.radians(0.25))
VALID = {"D0": None, "D1": None, "D2": "no-offset", "D3": "no-offset", "D4": "startup-offset", "D5": "startup-offset"}


def cell(lat, lon):
    return (np.floor(np.sin(np.radians(lat)) / DZ).astype(np.int64) * 10_000_000 + np.floor(np.asarray(lon) / 0.25).astype(np.int64))


def hpd_level(key, w, key_truth):
    """Mass of cells strictly denser than the truth's cell (truth inside the alpha-HPD region iff level < alpha)."""
    u, inv = np.unique(key, return_inverse=True); m = np.bincount(inv, weights=w)
    j = np.searchsorted(u, key_truth); mt = m[j] if (j < len(u) and u[j] == key_truth) else 0.0
    return float(m[m > mt].sum()) if mt > 0 else 1.0


def rank(x, w, xt):
    return float(w[x < xt].sum() + 0.5 * w[x == xt].sum())


def stats(X, a, T, par):
    ok = np.isfinite(a)
    if not ok.any(): return None
    w = np.exp(a - a[ok].max()); w[~ok] = 0; w /= w.sum()
    im = T["impact"]; tf = T["family"]
    fam = np.where(np.isin(X["fam"], (3.0, 6.0)), "B", np.where(X["fam"] == 1.0, "A1", np.where(X["fam"] == 2.0, "A2", "?")))
    r1 = np.exp(X["c1"] - np.logaddexp(X["c1"], X["c2"])); r1 = np.where(np.isfinite(r1), r1, 0.0)
    Wp = np.bincount(par, weights=w)
    return dict(u_lat=rank(X["lat"], w, im["lat"]), u_time=rank(X["t"], w, im["unix_s"]), u_xarc=rank(X["xarc"], w, im["cross_arc_nm"]),
                hpd2d=hpd_level(cell(X["lat"], X["lon"]), w, cell(np.array([im["lat"]]), np.array([im["lon"]]))[0]),
                hpd_lat=hpd_level(np.floor(X["lat"] / 0.05).astype(np.int64), w, int(math.floor(im["lat"] / 0.05))),
                p_true_family=float(w[fam == tf].sum()), p_true_cause=float((w * r1).sum() if T["cause"] == "C1" else (w * (1 - r1)).sum()),
                p_family={f: float(w[fam == f].sum()) for f in ("A1", "A2", "B")},
                median_lat=float(X["lat"][np.argsort(X["lat"])][np.searchsorted(np.cumsum(w[np.argsort(X["lat"])]), 0.5)]),
                ess_rows=float(1 / np.sum(w ** 2)), ess_parents=float(1 / np.sum(Wp ** 2)))


def main():
    cd, nodes, npz, audit = sys.argv[1:5]; T = json.load(open(f"{cd}/truth.json"))
    S = Search(npz); Dr = Drift({"glorys12": sorted(glob.glob(f"{nodes}/arclat-glorys12-*-nodes.csv")), "globcurrent": sorted(glob.glob(f"{nodes}/arclat-globcurrent-*-nodes.csv"))}, audit)
    seeds = sorted(glob.glob(f"{cd}/infer-eof-*/bto-bfo/seed-*"))
    per_seed, pooled_parts = [], []
    for sd in seeds:
        k = pathlib.Path(sd).name; run = str(pathlib.Path(sd).parents[1])
        X = terms(run, sd, f"{cd}/infer-core/bto-bfo/{k}/handoff-m0011/handoff.npy", f"{cd}/obs-synthetic.csv")
        pnf = S.p_no_find(X["lat"], X["lon"]); ls = np.log(1 - pnf + 1e-300) if T["search_detected"] else np.log(pnf)
        ld, _ = Dr.loglik(T["finds"], X["lat"]); nan_d = ~np.isfinite(ld)
        base = X["lw"] + X["surv"] + np.logaddexp(X["c1"], X["c2"])
        out = {"seed": k, "rows": int(len(base)), "drift_nan_rows": int(nan_d.sum()), "cells": {}}
        for d, ldd in X["D"].items():
            a0 = base + ldd
            ok = np.isfinite(a0); wv = np.exp(a0 - a0[ok].max()) if ok.any() else np.zeros_like(a0); wv[~ok] = 0
            out.setdefault("drift_nan_mass", {})[d] = float(wv[nan_d].sum() / max(wv.sum(), 1e-300))
            if (~nan_d & ok).any():   # NaN rows carried at the replicate's weighted mean likelihood ratio (composer ruling 1, 9 Oct)
                fill = logsumexp(ld[~nan_d & ok], b=wv[~nan_d & ok]) - np.log(wv[~nan_d & ok].sum())
            else: fill = 0.0
            ldf = np.where(nan_d, fill, ld)
            for st, a in (("core", a0), ("core+drift", a0 + ldf), ("core+searches", a0 + ls), ("all", a0 + ldf + ls)):
                s = stats(X, a, T, X["parent"]); out["cells"][f"{d}|{st}"] = s
                pooled_parts.append((f"{d}|{st}", k, a))
        out["lnZ"] = {d: float(logsumexp(base + v)) for d, v in X["D"].items()}
        per_seed.append(out)
        keep_X = X
        if len(seeds) > 0:
            pass
        np.savez_compressed(f"{cd}/rows-{k}.npz", lat=X["lat"].astype(np.float32), lon=X["lon"].astype(np.float32), t=X["t"], xarc=X["xarc"].astype(np.float32),
                            fam=X["fam"].astype(np.float32), parent=X["parent"].astype(np.int32), c1=X["c1"], c2=X["c2"], base=base, ls=ls, ld=ld,
                            **{f"D_{d}": v for d, v in X["D"].items()})
    # pooled over replicates by evidence (each replicate's unnormalised weights / K)
    pooled = {}
    rows = [np.load(f"{cd}/rows-{pathlib.Path(sd).name}.npz") for sd in seeds]
    cat = {k_: np.concatenate([r[k_] for r in rows]) for k_ in rows[0].files}
    offs = np.cumsum([0] + [len(r["lat"]) for r in rows])
    par = np.concatenate([r["parent"].astype(np.int64) + 10_000_000 * i for i, r in enumerate(rows)])
    Xc = dict(lat=cat["lat"].astype(float), lon=cat["lon"].astype(float), t=cat["t"], xarc=cat["xarc"].astype(float), fam=cat["fam"].astype(float), c1=cat["c1"], c2=cat["c2"])
    nan_d = ~np.isfinite(cat["ld"])
    for d in ("D0", "D1", "D2", "D3", "D4", "D5"):
        a0 = cat["base"] + cat[f"D_{d}"] - np.log(len(rows))
        ok = np.isfinite(a0); wv = np.exp(a0 - a0[ok].max()); wv[~ok] = 0
        fill = logsumexp(cat["ld"][~nan_d & ok], b=wv[~nan_d & ok]) - np.log(wv[~nan_d & ok].sum()) if (~nan_d & ok).any() else 0.0
        ldf = np.where(nan_d, fill, cat["ld"])
        for st, a in (("core", a0), ("core+drift", a0 + ldf), ("core+searches", a0 + cat["ls"]), ("all", a0 + ldf + cat["ls"])):
            pooled[f"{d}|{st}"] = stats(Xc, a, T, par)
    # Monte Carlo noise: SD over replicates of each statistic
    mc = {}
    for key in pooled:
        vals = [p["cells"].get(key) for p in per_seed]
        vals = [v for v in vals if v]
        if len(vals) > 1:
            mc[key] = {q: float(np.std([v[q] for v in vals], ddof=1)) for q in ("u_lat", "u_time", "u_xarc", "hpd2d", "hpd_lat", "p_true_family", "p_true_cause", "median_lat")}
    res = dict(case=T["case_seed"], truth={k_: T[k_] for k_ in ("impact", "family", "cause", "bfo_model_0019", "ocean_model", "search_detected", "p_no_find", "truth_inside_drift_nodes", "route_stratum")},
               valid_options=[d for d, m in VALID.items() if m is None or m == T["bfo_model_0019"]], pooled=pooled, mc_sd_between_replicates=mc, per_seed=per_seed)
    json.dump(res, open(f"{cd}/case-stats.json", "w"), indent=1, default=float)
    for key in ("D0|core", "D0|all", "D1|core", "D3|core", "D4|core"):
        p = pooled.get(key)
        if p: print(key, {q: round(p[q], 3) for q in ("u_lat", "u_time", "u_xarc", "hpd2d", "hpd_lat", "p_true_family", "p_true_cause", "median_lat", "ess_rows", "ess_parents")}, "MC", {q: round(v, 3) for q, v in mc.get(key, {}).items()})


if __name__ == "__main__":
    main()
