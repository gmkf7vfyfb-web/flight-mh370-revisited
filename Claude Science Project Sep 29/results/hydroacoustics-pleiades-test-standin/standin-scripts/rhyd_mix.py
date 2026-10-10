"""Mixture, split-half error and both stratum weightings for R_hyd (pre-registration section 4). Stand-in.
Usage: python rhyd_mix.py <per_seed.json> <eof mixture.json> <out.json>"""
import json, sys, itertools
import numpy as np
from scipy.special import logsumexp

rows = json.load(open(sys.argv[1])); PF = json.load(open(sys.argv[2]))["p_family"]
STRATA = list(PF); SEEDS = [1, 2, 3, 4]
VARS = ["A", "A-IMOS", "A-VKE", "H01W-only"]
PARTS = [((1, 2), (3, 4)), ((1, 3), (2, 4)), ((1, 4), (2, 3))]
BANDS = [(0.5, "within noise"), (1.0, "weak"), (2.3, "moderate"), (np.inf, "strong")]


def band(x):
    a = abs(x)
    for lim, name in BANDS:
        if a < lim:
            return name if name == "within noise" else name + (" for H" if x > 0 else " for no H")


def lnR(R, pi, seeds, v, nc_both=False):
    """ln R from per-seed log sums; strata weighted by pi (dict), seeds equal within stratum."""
    num, den, e0 = [], [], []
    for s in STRATA:
        rs = [R[(s, k)] for k in seeds]; lw = np.log(pi[s]) - np.log(len(rs))
        num.append(lw + logsumexp([r[f"lnSHL|{v}"] - r["lnS0"] for r in rs]))
        den.append(lw + logsumexp([r["lnSH"] - r["lnS0"] for r in rs]))
        key, nrm = (f"lnS0L_comp|{v}", "lnS0_comp") if nc_both else (f"lnS0L|{v}", "lnS0")
        e0.append(lw + logsumexp([r[key] - r[nrm] for r in rs]))
    return float(logsumexp(num) - logsumexp(den) - (logsumexp(e0) - logsumexp([np.log(pi[s]) for s in STRATA])))


out = {}
for opt in dict.fromkeys(r["option"] for r in rows):
    R = {(r["stratum"], r["seed"]): r for r in rows if r["option"] == opt}
    lz = {s: float(logsumexp([R[(s, k)]["ln_Z0019"] for k in SEEDS]) - np.log(4)) for s in STRATA}
    rw = {s: np.log(PF[s]) + lz[s] for s in STRATA}; t = logsumexp(list(rw.values())); rw = {s: float(np.exp(v - t)) for s, v in rw.items()}
    o = {"p_family_fixed": PF, "p_family_reweighted": rw, "ln_Z0019_per_family": lz,
         "ln_Z0019_seed_sd": {s: float(np.std([R[(s, k)]["ln_Z0019"] for k in SEEDS], ddof=1)) for s in STRATA},
         "ess_flight": {s: sum(R[(s, k)]["ess_flight"] for k in SEEDS) for s in STRATA},
         "ess_H": {s: sum(R[(s, k)]["ess_H"] for k in SEEDS) for s in STRATA},
         "not_computed_weight": {s: float(np.mean([R[(s, k)]["not_computed_weight"] for k in SEEDS])) for s in STRATA},
         "check_p_maxabs": max(r["check_p_maxabs"] for r in R.values())}
    for lab, pi in (("reweighted", rw), ("fixed", PF)):
        for v in VARS:
            for ncb in (False, True):
                full = lnR(R, pi, SEEDS, v, ncb)
                d = [abs(lnR(R, pi, a, v, ncb) - lnR(R, pi, b, v, ncb)) / 2 for a, b in PARTS]
                se = float(np.sqrt(np.mean(np.square(d))))
                o[f"{lab}|{v}" + ("|nc_both" if ncb else "")] = dict(lnR=full, split_half_se=se, split_half_max=float(max(d)),
                    reading=band(full), reading_lo=band(full - 2 * se), reading_hi=band(full + 2 * se))
        o[f"{lab}|per_stratum_A"] = {s: lnR(R, {x: (1.0 if x == s else 1e-300) for x in STRATA}, SEEDS, "A") for s in STRATA}
    out[opt] = o
json.dump(out, open(sys.argv[3], "w"), indent=1)
for opt, o in out.items():
    print(opt, {k: (round(o[k]["lnR"], 3), round(o[k]["split_half_se"], 3), o[k]["reading"]) for k in o if k.endswith("|A") or k.endswith("|A-IMOS")})
