"""Stratified estimate for the A1 no-intervention branch under the 00:19 treatments (smoke/a1-branch.toml; 18 Oct 2026).

    python a1_branch_estimate.py PROD_STRATUM_DIR BRANCH_STRATUM_DIR CORE_STRATUM_DIR OUT_JSON [SEEDS...]

Branch = onset flame-out-associated and control_realised = no intervention (the whole of D3's A1 mass on run J). For each treatment d:
    E_D0'[L_d | branch] = sum_rows m_d / sum_rows m_D0'     (rows in the branch; m from run_i_maps.cell_logmass, seeds pooled equally)
estimated twice: from production (rows restricted to the branch) and from the branch pass (all rows). The branch pass is valid if
its D0'-conditional latitude quantiles and E[L_D4 | branch] agree with production's (production ESS is large for both). Then
    Z(d, branch) = Z(D0') P_D0'(branch) E_D0'[L_d | branch]
and the A1 share of treatment d is Z(d, branch) / Z(d) plus the (negligible under D3) undemonstrated-recovery part from production.
Reports Kish ESS of the d-weighted branch rows in each pass, and their distinct-parent ESS.
"""
import json, sys, pathlib
import numpy as np
from scipy.special import logsumexp
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from compact_impacts import load
from run_i_maps import cell_logmass

CELLS = ("D0", "D2", "D3", "D4", "D5")


def wq(x, w, qs):
    o = np.argsort(x); c = np.cumsum(w[o]); c /= c[-1]
    return [float(x[o][min(np.searchsorted(c, q), len(x) - 1)]) for q in qs]


def side(stratum_dir, core_dir, seeds, restrict):
    acc = {d: {"l1": [], "l2": [], "p2": [], "lat": [], "m": []} for d in CELLS}; frac = []
    for k in seeds:
        sd = pathlib.Path(stratum_dir) / f"seed-{k}"
        if not sd.is_dir(): continue
        meta, g = load(sd); lm = cell_logmass(g, meta, pathlib.Path(core_dir) / "bto-bfo" / f"seed-{k}" / "handoff-m0011" / "handoff.npy")
        br = (g("latent:onset_mechanism") == 2) & (g("latent:control_realised") == 2)
        frac.append(float(br.mean()))
        sel = br if restrict else np.ones(len(br), bool)
        lat = g("latitude_deg"); par = g("parent").astype(np.int64)
        for d in CELLS:
            a = np.where(sel, lm[d], -np.inf); fin = np.isfinite(a)
            if not fin.any(): continue
            s = a[fin].max(); m = np.zeros(len(a)); m[fin] = np.exp(a[fin] - s)
            acc[d]["l1"].append(s + np.log(m.sum())); acc[d]["l2"].append(2 * s + np.log((m * m).sum()))
            ps = np.bincount(par[fin], m[fin]); acc[d]["p2"].append(2 * s + np.log((ps * ps).sum()))
            # keep a mass-preserving 20,000-row resample per seed for quantiles
            cs = np.cumsum(m); idx = np.minimum(np.searchsorted(cs, (np.arange(20000) + 0.5) / 20000 * cs[-1]), len(m) - 1)
            acc[d]["lat"].append(lat[idx]); acc[d]["m"].append(np.full(20000, np.exp(s) * cs[-1] / 20000))
    out = {"branch_row_fraction_mean": float(np.mean(frac)) if frac else None, "n_seeds": len(frac)}
    L = {d: logsumexp(acc[d]["l1"]) for d in CELLS if acc[d]["l1"]}
    for d in L:
        A = acc[d]; lat = np.concatenate(A["lat"]); m = np.concatenate(A["m"])
        out[d] = {"ln_E_L_given_branch": float(L[d] - L["D0"]), "ess_rows": float(np.exp(2 * L[d] - logsumexp(A["l2"]))),
                  "ess_parents": float(np.exp(2 * L[d] - logsumexp(A["p2"]))), "lat_q05_q50_q95": wq(lat, m, (0.05, 0.5, 0.95))}
    return out


def main(prod, branch, core, outp, seeds):
    seeds = [int(s) for s in seeds] or list(range(1, 25))
    res = {"production_branch_rows": side(prod, core, seeds, True), "branch_pass": side(branch, core, seeds, False)}
    json.dump(res, open(outp, "w"), indent=1)
    for k, v in res.items():
        print(k, "branch row fraction", v["branch_row_fraction_mean"], "seeds", v["n_seeds"])
        for d in CELLS:
            if d in v: print(f"  {d}: ln E[L|branch] {v[d]['ln_E_L_given_branch']:+.3f}  ESS rows {v[d]['ess_rows']:.0f} parents {v[d]['ess_parents']:.0f}  lat {[round(x, 2) for x in v[d]['lat_q05_q50_q95']]}")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5:])
