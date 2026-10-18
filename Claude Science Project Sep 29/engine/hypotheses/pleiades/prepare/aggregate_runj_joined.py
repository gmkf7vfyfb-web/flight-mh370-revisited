"""Joined V2 (planned descents before 00:11) under H: per-seed reductions of score_runj_joined.py, combined as end of flight's
joined_v2_summary.py does (medians of seed values; shares pooled with weights Z_k; ESS per seed, min and sum, never pooled).
    python aggregate_runj_joined.py WORKDIR OUT_JSON
"""
import json, sys
from pathlib import Path
import numpy as np
from scipy.special import logsumexp

W = Path(sys.argv[1]); R = {}
for f in sorted(W.glob("joined_*.npz")):
    if "partial" not in f.name:
        r = json.loads(str(np.load(f)["res"])); R[r["k"]] = r
seeds = sorted(R); out = {"seeds": seeds, "check_lnZ_vs_eof_max_abs": max(abs(v) for k in seeds if R[k]["check_lnZ_vs_eof"] for v in R[k]["check_lnZ_vs_eof"].values()),
                          "checked_seeds": [k for k in seeds if R[k]["check_lnZ_vs_eof"]], "cells": {}}
for d in R[seeds[0]]["cells"]:
    out["cells"][d] = {}
    for s in ("none (without H)", "gcrel-0.25", "g12-0.25"):
        x = [R[k]["cells"][d][s] for k in seeds]; lz = np.array([e["lnZ"] for e in x]); wz = np.exp(lz - logsumexp(lz))
        e = dict(lnZ_combined=float(logsumexp(lz) - np.log(len(lz))), ess_min=min(v["ess"] for v in x), ess_sum=sum(v["ess"] for v in x),
                 mean_lat_pooled=float(np.sum(wz * [v["mean_lat"] for v in x])), mean_lon_pooled=float(np.sum(wz * [v["mean_lon"] for v in x])),
                 in30_pooled=float(np.sum(wz * [v["in30"] for v in x])), in50_pooled=float(np.sum(wz * [v["in50"] for v in x])))
        for f in ("A1", "A2", "B", "code 6"):
            sh = np.array([v["fam"][f]["share"] for v in x]); pre = np.array([v["fam"][f]["pre0011_share"] for v in x])
            es = np.array([v["fam"][f]["ess"] for v in x])
            e[f] = dict(share_median=float(np.median(sh)), share_range=[float(sh.min()), float(sh.max())], share_pooled=float(np.sum(wz * sh)),
                        pre0011_share_median=float(np.median(pre)), pre0011_share_pooled=float(np.sum(wz * pre)),
                        ess_min=float(es.min()), ess_sum=float(es.sum()))
        out["cells"][d][s] = e
    for s in ("gcrel-0.25", "g12-0.25"):
        a = np.array([R[k]["cells"][d][s]["lnZ"] - R[k]["cells"][d]["none (without H)"]["lnZ"] for k in seeds])
        out["cells"][d][s]["ln_mean_LH_seed_median"] = float(np.median(a)); out["cells"][d][s]["ln_mean_LH_seed_sd"] = float(a.std(ddof=1))
Path(sys.argv[2]).write_text(json.dumps(out, indent=1))
for d, e in out["cells"].items():
    for s in ("none (without H)", "gcrel-0.25"):
        x = e[s]; print(d, s, "B median %.3f (range %.3f-%.3f) pooled %.3f pre-00:11 B %.3f | B ESS sum %.0f min %.0f | all ESS sum %.0f | A1 %.3f A2 %.3f | mean %.2f %.2f" % (
            x["B"]["share_median"], *x["B"]["share_range"], x["B"]["share_pooled"], x["B"]["pre0011_share_median"], x["B"]["ess_sum"], x["B"]["ess_min"], x["ess_sum"],
            x["A1"]["share_median"], x["A2"]["share_median"], x["mean_lat_pooled"], x["mean_lon_pooled"]))
print("check", out["check_lnZ_vs_eof_max_abs"], len(out["checked_seeds"]))
