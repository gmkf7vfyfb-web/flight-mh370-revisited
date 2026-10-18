"""Combine the A1-branch pass with production (stratified estimator; 18 Oct 2026).

    python a1_branch_combine.py PROD_STRATUM_DIR CORE_STRATUM_DIR BRANCH_ESTIMATE_JSON OUT_JSON [NPROC=6]

From production (all seeds of the stratum, pooled with equal seed weight as option_table_0019): P_D0'(branch), E_D0'[L_d] over all
rows, and the production family masses. From the branch pass (a1_branch_estimate.py output): E_D0'[L_d | branch]. Then for each
treatment d:
    share_branch(d)  = P_D0'(branch) * E_D0'[L_d | branch]_pass / E_D0'[L_d]_prod
    A1(d)            = share_branch(d) + share of A1 rows outside the branch (undemonstrated recoveries; from production)
and the other families are rescaled so the shares sum to 1: (A2, B, other) * (1 - A1_new) / (1 - A1_prod).
Waypoints stratum only (core P(family) 0.9982); the other strata change the mixture shares by < 0.002.
"""
import json, sys, pathlib
import numpy as np
from multiprocessing import Pool
from scipy.special import logsumexp
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from compact_impacts import load
from run_i_maps import cell_logmass

CELLS = ("D0", "D2", "D3", "D4", "D5")


def seed_terms(args):
    sd, core = args; meta, g = load(sd); k = sd.name
    lm = cell_logmass(g, meta, pathlib.Path(core) / "bto-bfo" / k / "handoff-m0011" / "handoff.npy")
    f4 = g("family4_code"); br = (g("latent:onset_mechanism") == 2) & (g("latent:control_realised") == 2)
    masks = {"all": np.ones(len(f4), bool), "branch": br, "A1": f4 == 1, "A1_out": (f4 == 1) & ~br, "A2": f4 == 2, "B": np.isin(f4, (3, 6))}
    out = {}
    for d in CELLS:
        a = lm[d]
        out[d] = {n: float(logsumexp(a[m & np.isfinite(a)])) if (m & np.isfinite(a)).any() else -np.inf for n, m in masks.items()}
    return out


def main(prod, core, est, outp, nproc=6):
    seeds = sorted((p for p in pathlib.Path(prod).glob("seed-*") if p.is_dir()), key=lambda p: int(p.name[5:]))
    with Pool(int(nproc)) as pool: T = pool.map(seed_terms, [(sd, core) for sd in seeds])
    pooled = {d: {n: float(logsumexp([t[d][n] for t in T])) for n in T[0][d]} for d in CELLS}
    E = json.load(open(est))["branch_pass"]
    lp_branch = pooled["D0"]["branch"] - pooled["D0"]["all"]
    res = {"n_production_seeds": len(seeds), "P_D0_branch": float(np.exp(lp_branch)), "cells": {}}
    for d in CELLS:
        p = pooled[d]; lE_all = p["all"] - pooled["D0"]["all"]
        sh_prod = {n: float(np.exp(p[n] - p["all"])) for n in ("A1", "A2", "B", "branch", "A1_out")}
        sh_branch = float(np.exp(lp_branch + E[d]["ln_E_L_given_branch"] - lE_all))
        a1 = sh_branch + sh_prod["A1_out"]; scale = (1 - a1) / (1 - sh_prod["A1"])
        res["cells"][d] = {"production": sh_prod, "stratified": {"A1": a1, "A1_branch": sh_branch, "A1_outside_branch": sh_prod["A1_out"],
                                                                "A2": sh_prod["A2"] * scale, "B": sh_prod["B"] * scale},
                           "branch_pass_ess_rows": E[d]["ess_rows"], "branch_pass_ess_parents": E[d]["ess_parents"],
                           "branch_pass_lat_q05_q50_q95": E[d]["lat_q05_q50_q95"]}
    json.dump(res, open(outp, "w"), indent=1)
    print("P_D0'(branch)", round(res["P_D0_branch"], 4), "production seeds", len(seeds))
    for d, r in res["cells"].items():
        print(d, "production A1/A2/B", [round(r["production"][k], 3) for k in ("A1", "A2", "B")], "| stratified A1/A2/B",
              [round(r["stratified"][k], 3) for k in ("A1", "A2", "B")], "(branch", round(r["stratified"]["A1_branch"], 3), "+ outside", round(r["stratified"]["A1_outside_branch"], 3), ")",
              "ESS", round(r["branch_pass_ess_rows"]), "lat", [round(x, 2) for x in r["branch_pass_lat_q05_q50_q95"]])


if __name__ == "__main__":
    main(*sys.argv[1:6])
