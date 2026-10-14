"""8-seed aggregate of the joined V2 production run (core run I, stratum next-i-waypoints, binary o13d). Inputs: R/joined-sK.json
(smoke/joined_v2.py) and R/gate4-sK.json (pilot_oct13.py gate4 on the 22:41 arm). Writes R/joined-v2-summary.json and .csv.
Combination across seeds (independent replicates of the whole pipeline, core included): ln Z by log-mean-exp of the seed values,
with the seed standard deviation and the standard error of the mean of ln Z; family shares by pooling the seeds' posteriors with
weights Z_k (the mixture of the seed posteriors); ESS reported per seed (minimum and sum), never pooled into one number.
LABEL every quoted figure: "V2 joined at 00:11: onsets before 00:11 scored in-stage, after 00:11 in the filter; conditional on
symmetric single-engine flight (item 1 not landed); uncontrolled-arm dynamics not yet calibrated (item 2 gate open)"."""
import json, sys, pathlib, csv
import numpy as np
from scipy.special import logsumexp

R = pathlib.Path(sys.argv[1]); seeds = [int(s) for s in sys.argv[2:]]
J = {k: json.load(open(R / f"joined-s{k}.json")) for k in seeds}
G = {k: json.load(open(R / f"gate4-s{k}.json")) for k in seeds if (R / f"gate4-s{k}.json").exists()}
FAMS = ("A1", "A2", "B", "outside B (6)")
out = {"label": __doc__.split("LABEL every quoted figure: ")[1].split('"')[1], "seeds": seeds, "cells": {}}
rows = []
for cell in J[seeds[0]]["cells"]:
    lz = np.array([J[k]["cells"][cell]["lnZ"] for k in seeds])
    wz = np.exp(lz - logsumexp(lz))
    d = {"lnZ_combined": float(logsumexp(lz) - np.log(len(lz))), "lnZ_seed_sd": float(lz.std(ddof=1)), "lnZ_mean_se": float(lz.std(ddof=1) / np.sqrt(len(lz))),
         "lnZ_by_seed": lz.tolist(), "ess_min": float(min(J[k]["cells"][cell]["ess"] for k in seeds)), "ess_sum": float(sum(J[k]["cells"][cell]["ess"] for k in seeds)),
         "S1_share": float(np.sum(wz * [J[k]["cells"][cell]["S1_share"] for k in seeds])),
         "lat_q50_by_seed": [J[k]["cells"][cell]["lat_q05_q50_q95"][1] for k in seeds]}
    for f in FAMS:
        sh = np.array([J[k]["cells"][cell][f]["share"] for k in seeds]); es = [J[k]["cells"][cell][f]["ess"] for k in seeds]
        d[f] = {"share": float(np.sum(wz * sh)), "share_seed_sd": float(sh.std(ddof=1)), "ess_min": float(min(es)), "ess_sum": float(sum(es))}
    out["cells"][cell] = d
    rows.append(dict(cell=cell, lnZ=d["lnZ_combined"], lnZ_seed_sd=d["lnZ_seed_sd"], ess_min=d["ess_min"], S1_share=d["S1_share"],
                     **{f"{f}_share": d[f]["share"] for f in FAMS}, **{f"{f}_ess_min": d[f]["ess_min"] for f in FAMS}))
# 22:41-arm onset statistics (deliberate onsets before 00:11 live here), per seed: max over seeds of the boundary fraction
gs = {}
for k, g in G.items():
    for cell, v in g["cells"].items():
        for fam, x in v.items():
            gs.setdefault(cell, {}).setdefault(fam, []).append(x.get("onset_boundary_fraction"))
out["onset_boundary_fraction_max_over_seeds"] = {c: {f: (max(x for x in v if x is not None) if any(x is not None for x in v) else None) for f, v in fv.items()} for c, fv in gs.items()}
out["truncation_finite_fraction"] = {k: G[k]["truncation_finite_fraction"] for k in G}
out["s1_pi_factor_quantiles"] = {k: J[k].get("s1_pi_factor_quantiles") for k in seeds}
out["dlnZ_filter_by_seed"] = {k: J[k]["dlnZ_filter"] for k in seeds}
json.dump(out, open(R / "joined-v2-summary.json", "w"), indent=1)
with open(R / "joined-v2-summary.csv", "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
for r in rows:
    print(f"{r['cell']}: lnZ {r['lnZ']:.3f} (seed sd {r['lnZ_seed_sd']:.3f}) ESS min {r['ess_min']:.0f} | " +
          " ".join(f"{f} {r[f + '_share']:.3f} (ESS min {r[f + '_ess_min']:.0f})" for f in FAMS))
