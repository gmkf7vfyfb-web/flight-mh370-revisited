"""Storage for the both-burst SUPPLEMENTARY pass (Pete, 16 Oct 2026 ~03:40Z; results/eof-both-burst-oct16 section 4b).

The supplementary pass (children 64 = 256 descents per parent) writes about 11 GB per waypoints seed in the compact format. Only the
both-burst cells are scored from it (the production 32-descent pass carries every other cell). This script keeps an unbiased
subset: Poisson (Horvitz-Thompson) thinning with inclusion probability

    pi_i = min(1, c * max_k  w_i L_ik / sum_j w_j L_jk),     k in CELLS,

and the kept rows carry weight w_i / pi_i. For any cell k and any function f, sum_kept (w_i/pi_i) L_ik f_i is an unbiased estimate
of sum_all w_i L_ik f_i, so ln Z, shares and distributions stay exact in expectation. Rows that matter to any listed cell are kept
with probability 1. c is set by bisection so that the expected kept rows equal TARGET. Every column is kept, so cells that are
computed later from the stored innovations (D5, closed form) can be scored; r600/no-offset is in CELLS because D5 is that cell times
an R1200 offset factor, so its rows are covered.

Output: the same compact layout (impacts32.npy, parents32.npy, run.json, SHA256SUMS), readable by compact_impacts.load. run.json gets
a "thinning" block: cells, c, target, kept rows, the inclusion-probability random seed, and per-cell ln Z and ESS before and after.

Usage: python both_burst_thin.py IN_SEED_DIR OUT_SEED_DIR [TARGET_ROWS=1000000] [SEED=1]
"""
import sys, json, pathlib, hashlib, shutil
import numpy as np
from compact_impacts import load

CELLS = ["r600/no-offset", "both/no-offset", "both/startup-offset", "both/inflated"]


def cell_weights(g, w):
    out = {}
    for k in CELLS:
        ll = g("loglik:" + k); ll = np.where(np.isfinite(ll), ll, -np.inf); s = np.max(ll[np.isfinite(ll)])
        L = w * np.exp(ll - s); out[k] = (L, s)
    return out


def stats(wsum, cw):
    return {k: {"ln_Z_rel": float(np.log(L.sum()) + s - np.log(wsum)), "eff_impacts": float(L.sum() ** 2 / np.square(L).sum())}
            for k, (L, s) in cw.items()}


def thin(sd, out, target=1_000_000, seed=1):
    sd = pathlib.Path(sd); out = pathlib.Path(out)
    m, g = load(sd); w = g("weight"); n = len(w)
    cw = cell_weights(g, w)
    q = np.zeros(n)
    for L, _ in cw.values(): q = np.maximum(q, L / L.sum())
    lo, hi = 0.0, 1e12
    for _ in range(200):
        c = np.sqrt(lo * hi) if lo > 0 else hi / 1e6
        e = np.minimum(1.0, c * q).sum()
        if e > target: hi = c
        else: lo = c
        if abs(e - target) < 0.5 or hi / max(lo, 1e-300) < 1 + 1e-12: break
    c = lo if lo > 0 else c
    pi = np.minimum(1.0, c * q)
    rng = np.random.default_rng(seed)
    keep = (pi > 0) & (rng.random(n) < pi)
    idx = np.flatnonzero(keep)
    Y = np.load(sd / "impacts32.npy", mmap_mode="r")
    meta = json.loads((sd / "run.json").read_text())
    wcol = meta["impact_columns"].index("weight")
    Z = np.array(Y[idx], copy=True)
    w_new = w[idx] / pi[idx]
    Z[:, wcol] = w_new.astype(Z.dtype)
    # after-thinning statistics from the stored (rounded) weight column, as downstream will read it
    wk = Z[:, wcol].astype(np.float64)
    cw_after = {}
    for k, (L, s) in cw.items():
        cw_after[k] = (wk * (L[idx] / w[idx]), s)
    out.mkdir(parents=True, exist_ok=True)
    np.save(out / "impacts32.npy", Z)
    if (sd / "parents32.npy").exists(): shutil.copy(sd / "parents32.npy", out / "parents32.npy")
    for f in ("COLUMNS.txt",):
        if (sd / f).exists(): shutil.copy(sd / f, out / f)
    meta["thinning"] = {"method": "Poisson (Horvitz-Thompson) thinning, pi = min(1, c max_k w L_k / Z_k)", "cells": CELLS,
                        "c": float(c), "target_rows": int(target), "expected_rows": float(pi.sum()), "kept_rows": int(len(idx)),
                        "rows_in": int(n), "rows_with_pi_1": int(np.sum(pi >= 1.0)), "rng_seed": int(seed),
                        "source_sha256": {l.split()[1]: l.split()[0] for l in (sd / "SHA256SUMS").read_text().splitlines()},
                        "weight_sum_in": float(w.sum()), "before": stats(w.sum(), cw), "after": stats(w.sum(), cw_after),
                        "note": ("Weights are w/pi; the held-out cell is NOT represented (production pass carries it). ln Z must be normalised by "
                                 "weight_sum_in (the unthinned total), not by the sum of the stored weights, which excludes rows with pi = 0.")}
    (out / "run.json").write_text(json.dumps(meta))
    lines = []
    for f in sorted(p.name for p in out.iterdir() if p.name != "SHA256SUMS"):
        h = hashlib.sha256((out / f).read_bytes()).hexdigest(); lines.append(f"{h}  {f}")
    (out / "SHA256SUMS").write_text("\n".join(lines) + "\n")
    return meta["thinning"]


if __name__ == "__main__":
    a = sys.argv
    t = thin(a[1], a[2], int(a[3]) if len(a) > 3 else 1_000_000, int(a[4]) if len(a) > 4 else 1)
    print(json.dumps({k: t[k] for k in ("kept_rows", "rows_in", "rows_with_pi_1", "before", "after")}, indent=1))
