"""Reduce the per-seed summaries written by score_run_j.py to the run J tables of the results note.

    python hypotheses/seabed-search/reduce_run_j.py <summaries dir> <core run-j dir> <out.json> [<both-burst summaries dir>]

With the fourth argument, D3 and D4 take the waypoints stratum from end of flight's supplementary both-burst set
(run-j-both-burst/run-j-waypoints, thinned; seed_terms normalises by thinning.weight_sum_in), as end of flight instructs
(architecture.md 2026-10-17 09:56Z) and as the composer does. The other strata and options use the production set.

Row mass per 00:19 option: end of flight's `option_table_0019.seed_terms` cell 'D<d> total q=0.333 (C2 silent)' (headline
cause model), unchanged. Seeds pooled by evidence within a family folder (stratum); strata mixed by core's P(family) from
core/run-j/<stratum>/summary.json (log_evidence of case 0), as option_table_0019 and the composer do. Quantities:
  Z            = E[P(no find)] under the option's end-of-flight posterior (the searches' evidence factor)
  on searched  = posterior mass x searched fraction 1 - prod_k (1 - f_k c_k), before and after the searches
  next area    = mass inside the planned next Ocean Infinity area (map layer, not evidence), before and after
  ESS          = pooled Kish effective sample, before and after
Monte Carlo noise: split-half by seed position within each stratum, and the between-seed spread.
"""
import json
import pathlib
import sys

import numpy as np
from scipy.special import logsumexp

FAMILIES = ["run-j-waypoints", "run-j-free", "run-j-descent-climb", "run-j-repro-radar"]
SCEN = ["base_rho0.05", "base_rho0", "base_rho0.25", "base_rho0.5", "without_oi_rho0.05"]
DKEYS = [f"D{d}" for d in range(6)]
HF = ["all", "A1", "A2", "B"]


def pooled(recs, scen, fam):
    """recs: list of (log seed weight incl. scale s, record for (option, fam)). Returns dict of pooled quantities."""
    lw = np.array([l for l, _ in recs])
    if not len(lw):
        return None
    sh = lw.max()
    W = np.exp(lw - sh)
    g = lambda f: float(sum(w * f(r) for w, (_, r) in zip(W, recs)))
    g2 = lambda f: float(sum(w * w * f(r) for w, (_, r) in zip(W, recs)))
    m = g(lambda r: r["m"])
    if m <= 0:
        return {"mass": 0.0}
    mp = g(lambda r: r[scen]["mP"])
    out = {"Z": mp / m,
           "on_searched_before": g(lambda r: r["on_union"]) / m, "on_searched_after": g(lambda r: r[scen]["on_union"]) / mp,
           "on_atsb_before": g(lambda r: r["on_atsb"]) / m, "on_atsb_after": g(lambda r: r[scen]["on_atsb"]) / mp,
           "next_area_before": g(lambda r: r["next"]) / m, "next_area_after": g(lambda r: r[scen]["next"]) / mp,
           "north33_before": g(lambda r: r["north33"]) / m, "north33_after": g(lambda r: r[scen]["north33"]) / mp,
           "ess_before": m * m / g2(lambda r: r["m2"]), "ess_after": mp * mp / g2(lambda r: r[scen]["mP2"]),
           "log_mass": float(np.log(m) + sh)}
    return out


def main():
    sdir, core, outp = map(pathlib.Path, sys.argv[1:4])
    bb = pathlib.Path(sys.argv[4]) if len(sys.argv) > 4 else None
    lnZc = {s: json.load(open(core / s / "summary.json"))["cases"][0]["log_evidence"] for s in FAMILIES}
    lse = logsumexp(list(lnZc.values()))
    PF = {s: float(np.exp(v - lse)) for s, v in lnZc.items()}
    S = {}
    for f in sorted(sdir.glob("*.json")):
        d = json.loads(f.read_text())
        S.setdefault(d["stratum"], []).append(d)
    for st in S:
        S[st].sort(key=lambda d: int(d["seed"].split("-")[1]))
    SB = sorted((json.loads(f.read_text()) for f in bb.glob("*.json")), key=lambda d: int(d["seed"].split("-")[1])) if bb else None
    use = lambda D: {st: (SB if (SB and D in ("D3", "D4") and st == "run-j-waypoints") else v) for st, v in S.items()}
    res = {"P_family_core": PF, "seeds": {st: len(v) for st, v in S.items()},
           "d3_d4_waypoints_from_both_burst": {"seeds": len(SB), "rows": sum(d["rows"] for d in SB)} if SB else None,
           "rows": {st: sum(d["rows"] for d in v) for st, v in S.items()},
           "checks": {"max_abs_dP_algebra_vs_rust": max(d["checks"]["max_abs_dP_algebra_vs_rust"] for v in S.values() for d in v),
                      "max_abs_dlnL_algebra_vs_rust": max(d["checks"]["max_abs_dlnL_algebra_vs_rust"] for v in S.values() for d in v),
                      "all_finite": all(d["checks"]["finite_all_rows"] for v in S.values() for d in v),
                      "rows_match": all(d["checks"]["rows_impacts32"] == d["checks"]["rows_evaluate"] == d["rows"]
                                        for v in S.values() for d in v)},
           "per_stratum": {}, "mixture": {}}
    for D in DKEYS:
        SD = use(D)
        for scen in SCEN:
            for hf in HF:
                # per stratum
                for st, v in SD.items():
                    K = len(v)
                    recs = [(d["options"][D]["s"] + np.log(1.0 / K), d["options"][D][hf]) for d in v]
                    r = pooled(recs, scen, hf)
                    if r and "Z" in r and hf == "all":
                        half = [pooled(recs[:K // 2], scen, hf), pooled(recs[K // 2:], scen, hf)]
                        r["Z_split_half"] = [h["Z"] for h in half]
                        zs = [x[1][scen]["mP"] / x[1]["m"] for x in recs if x[1]["m"] > 0]
                        r["Z_seed_sd"] = float(np.std(zs, ddof=1))
                    res["per_stratum"].setdefault(st, {}).setdefault(D, {}).setdefault(scen, {})[hf] = r
                recs = [(d["options"][D]["s"] + np.log(PF[st] / len(v)), d["options"][D][hf]) for st, v in SD.items() for d in v]
                res["mixture"].setdefault(D, {}).setdefault(scen, {})[hf] = pooled(recs, scen, hf)
            # family shares in the mixture, before and after
            mix = res["mixture"][D][scen]
            tot = mix["all"]["log_mass"]
            for hf in HF[1:]:
                if mix[hf] and "Z" in mix[hf]:
                    mix[hf]["share_before"] = float(np.exp(mix[hf]["log_mass"] - tot))
                    mix[hf]["share_after"] = mix[hf]["share_before"] * mix[hf]["Z"] / mix["all"]["Z"]
    outp.write_text(json.dumps(res, indent=1))
    print(json.dumps({"P_family_core": PF, "seeds": res["seeds"], "checks": res["checks"]}, indent=1))


if __name__ == "__main__":
    main()
