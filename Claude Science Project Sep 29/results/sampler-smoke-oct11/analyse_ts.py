"""Sampler-change smoke (job 8) analysis: per arm and stratum, split-half over all balanced partitions
(mh370-run-reporting), mode-weight vs shape decomposition, m0011 evidence-increment spread, stage counts,
worst stage ESS, distinct origins, runtime. Usage: python analyse_ts.py <runs-ts dir> <out csv>"""
import sys, json, glob, os, itertools
import numpy as np
root, out = sys.argv[1], sys.argv[2]
FLOOR8 = 0.924
def overlap(a, b, step):
    return float(np.minimum(a, b).sum() * step)
def split_half(dens, step):
    n = len(dens); v = []
    for half in itertools.combinations(range(n), n // 2):
        if 0 not in half: continue
        o = [i for i in range(n) if i not in half]
        v.append(overlap(np.mean([dens[i] for i in half], 0), np.mean([dens[i] for i in o], 0), step))
    return float(np.mean(v)), float(np.min(v)), float(np.max(v)), len(v)
rows = []
for rd in sorted(glob.glob(f"{root}/ts-*")):
    if not os.path.isdir(rd) or not os.path.exists(f"{rd}/summary.json"): continue
    name = os.path.basename(rd); arm, stratum = name.split("-")[1], name.split("-")[2]
    s = json.load(open(f"{rd}/summary.json")); j = json.load(open(f"{rd}/run.json"))
    case = [c for c in s["cases"] if c["case"] == "bto-bfo"][0]; step = s["grid"]["step"]
    dens = [np.asarray(r["density"], float) for r in case["replicates"]]
    m, lo, hi, k = split_half(dens, step)
    P = np.array([[md["posterior_probability"] for md in r["modes"]] for r in j["replicates"]])
    inc = {}; stages = []; worst = []; orig_end = []; orig_1941 = []
    for r in j["replicates"]:
        for md, n in zip(r["modes"], r["particles_per_mode"]):
            ee = {e["epoch"]: e for e in md["epochs"]}
            inc.setdefault(md["mode"], []).append(ee["m0011"]["log_evidence_increment"])
            for ep in ("m1839", "m1941", "m2041", "m2141", "m2241", "m0011"):
                st = ee[ep].get("temper_stage_ess", [])
                stages.append(len(st)); worst.append(min(st) / n if st else np.nan)
            orig_end.append(ee["m0019b"].get("distinct_origins", np.nan)); orig_1941.append(ee["m1941"].get("distinct_origins", np.nan))
    inc_sd = float(np.mean([np.std(v, ddof=1) for v in inc.values()]))
    rows.append(dict(arm=arm, stratum=stratum, seeds=len(dens), split_half_mean=round(m, 4), split_half_min=round(lo, 4), split_half_max=round(hi, 4),
                     partitions=k, floor_8=FLOOR8, mode_prob_sd_mean=round(float(P.std(0, ddof=1).mean()), 4), m0011_increment_sd_mean=round(inc_sd, 4),
                     tempered_stages_per_epoch=round(float(np.mean(stages)), 2), worst_stage_ess_fraction_median=round(float(np.nanmedian(worst)), 4),
                     origins_m1941_median=float(np.nanmedian(orig_1941)), origins_end_median=float(np.nanmedian(orig_end)),
                     runtime_s_per_seed=round(float(np.mean([r["runtime_s"] for r in j["replicates"]])), 1),
                     median_lat_0019=round(float(case["stats"]["median"]) if "median" in case["stats"] else np.nan, 3)))
import csv
with open(out, "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
for r in rows: print(r)
