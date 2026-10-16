"""Run J (Pete 16 Oct ~16:40Z): the bank limit is drawn uniformly on [52, 90] deg and recorded (latent:spiral_bank_cap_deg), so other
priors on the limit are exact re-weightings of the same rows: Boeing-weighted (0.8 on [52, 63], 0.2 on [63, 90]) and the high end
(limit >= 80 deg only). Per raw 00:19 column (not the two-factor D totals), per seed: family shares, impact-latitude median, share
of impacts steeper than 45 deg, ln evidence increment and ESS; then seed means and standard errors.
Usage: python bank_prior_variants.py STRATUM_DIR OUT_JSON"""
import sys, json, glob, os
import numpy as np
from compact_impacts import load
CELLS = ["none", "r600/no-offset", "both/no-offset", "both/startup-offset"]
PRIORS = {"uniform 52-90 (headline)": None, "Boeing-weighted 0.8/0.2": (0.8 / (11 / 38), 0.2 / (27 / 38)), "limit 80-90 only": "hi"}
def main(base, outp):
    seeds = sorted(int(p.split("-")[-1]) for p in glob.glob(base + "/seed-*") if os.path.isdir(p) and os.path.exists(p + "/SHA256SUMS"))
    res = {}
    for k in seeds:
        m, g = load(f"{base}/seed-{k}"); w = g("weight"); fam = g("family4_code"); lat = g("latitude_deg")
        cap = g("latent:spiral_bank_cap_deg"); fpa = np.abs(g("flight_path_angle_deg"))
        for c in CELLS:
            ll = np.zeros(len(w)) if c == "none" else g("loglik:" + c); ll = np.where(np.isfinite(ll), ll, -np.inf)
            s = ll[np.isfinite(ll)].max(); L0 = w * np.exp(ll - s)
            for pn, pv in PRIORS.items():
                f = np.ones(len(w)) if pv is None else (np.where(cap >= 80, 1.0, 0.0) if pv == "hi" else np.where(cap < 63, pv[0], pv[1]))
                L = L0 * f; Z = L.sum(); o = np.argsort(lat); cc = np.cumsum(L[o]) / Z
                res.setdefault(f"{c} | {pn}", []).append(dict(ln_Z=float(np.log(Z) + s - np.log((w * f).sum())), A1=float(L[fam == 1].sum() / Z),
                    A2=float(L[fam == 2].sum() / Z), B=float(L[(fam == 3) | (fam == 6)].sum() / Z), lat_median=float(lat[o][np.searchsorted(cc, 0.5)]),
                    steep_gt45=float(L[fpa > 45].sum() / Z), ess=float(Z ** 2 / (L ** 2).sum())))
    out = {"seeds": seeds, "note": "raw 00:19 columns, not the two-factor D0'-D5 totals; seed mean and standard error", "cells": {}}
    for key, r in res.items():
        a = {q: np.array([x[q] for x in r]) for q in r[0]}
        out["cells"][key] = {q: {"mean": float(v.mean()), "se": float(v.std(ddof=1) / np.sqrt(len(v))), "min": float(v.min())} for q, v in a.items()}
    json.dump(out, open(outp, "w"), indent=1)
    for key, v in out["cells"].items():
        print(f"{key:48s} A1 {v['A1']['mean']:.3f}±{v['A1']['se']:.3f} A2 {v['A2']['mean']:.3f} B {v['B']['mean']:.3f} lat {v['lat_median']['mean']:.2f} steep {v['steep_gt45']['mean']:.3f} lnZ {v['ln_Z']['mean']:.2f}±{v['ln_Z']['se']:.2f} ESS {v['ess']['mean']:,.0f} (min {v['ess']['min']:,.0f})")
if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
