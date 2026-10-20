"""Run-J northern supplement: checks on the staged outputs (Mac).
    python analyse_supplement.py STAGE_DIR RUNJ_REF_JSON OUT_JSON
STAGE_DIR holds validate/seed-1/... and north/seed-<s>/... (each with handoff-m0011/, handoff-m0011-supplement/,
diagnostics.json, final-stats.json). Reports: (1) prior recovery on run J seed 1 (same population): corrected
supplement means against the normal hand-off, z with Kish-ESS standard errors over distinct states; (2) prior recovery
on the new seeds against run J's 24 seeds (seed-level z); (3) re-allocation check (normal hand-off, final.npy, ln Z);
(4) supplement composition; (5) per-mode ln Z seed sd against run J; (6) pooled r_hat(lat) table for MIS."""
import sys, json, pathlib, numpy as np
STAGE, REF, OUT = pathlib.Path(sys.argv[1]), json.load(open(sys.argv[2])), sys.argv[3]
F = {"lat": lambda H: H[:, 1], "lon": lambda H: H[:, 2], "alt_ft": lambda H: H[:, 3], "mach": lambda H: H[:, 4], "bfo_bias_hz": lambda H: H[:, 8],
     "north_33": lambda H: (H[:, 1] > -33) * 1.0, "north_30": lambda H: (H[:, 1] > -30) * 1.0, "north_25": lambda H: (H[:, 1] > -25) * 1.0}
for m in range(5): F[f"mode{m}"] = (lambda m: lambda H: (H[:, 6] == m) * 1.0)(m)
def wstats(H):
    w = H[:, 0] * np.exp(H[:, 13]); W = w.sum()
    _, sid = np.unique(H[:, [1, 2, 3, 8]], axis=0, return_inverse=True); sid = sid.ravel()
    ws = np.bincount(sid, w); ess = W ** 2 / (ws ** 2).sum()   # Kish ESS over distinct states (conservative)
    out = {}
    for k, f in F.items():
        v = f(H); mu = (w * v).sum() / W; var = (w * (v - mu) ** 2).sum() / W
        out[k] = (float(mu), float(np.sqrt(var / ess)))
    return out, float(ess), float(W)
res = {}
# (1) same population
v = STAGE / "validate" / "seed-1"
if v.exists():
    P = np.load(v / "handoff-m0011" / "handoff.npy"); S = np.load(v / "handoff-m0011-supplement" / "handoff.npy")
    sp, ep, Wp = wstats(P); ss, es, Ws = wstats(S)
    res["validate_seed1"] = {"ess_states_normal": ep, "ess_states_supplement": es, "weight_sum_normal": Wp, "weight_sum_supplement": Ws,
        "z": {k: (ss[k][0] - sp[k][0]) / np.hypot(ss[k][1], sp[k][1]) if np.hypot(ss[k][1], sp[k][1]) > 0 else 0.0 for k in F},
        "means": {k: [sp[k][0], ss[k][0]] for k in F}}
# (2)-(5) new seeds
seeds = sorted((STAGE / "north").glob("seed-*"), key=lambda p: int(p.name[5:])) if (STAGE / "north").exists() else []
ref = list(REF.values())
if seeds:
    sup = {k: [] for k in F}; nor = {k: [] for k in F}; fin = {}; lnz = []; comp = []; pb = []; info0 = None; wsum = []
    for sd in seeds:
        S = np.load(sd / "handoff-m0011-supplement" / "handoff.npy"); P = np.load(sd / "handoff-m0011" / "handoff.npy")
        a, _, Ws = wstats(S); b, _, _ = wstats(P); wsum.append(Ws)
        for k in F: sup[k].append(a[k][0]); nor[k].append(b[k][0])
        fs = json.load(open(sd / "final-stats.json"))
        for k in ("lat_median", "north_of_33S", "north_of_30S", "shoulder_34p5_36p5", "mean_lat"): fin.setdefault(k, []).append(fs[k])
        d = json.load(open(sd / "diagnostics.json")); lnz.append([m["log_evidence"] for m in d["modes"]] + [d["log_evidence"]])
        info = json.load(open(sd / "handoff-m0011-supplement" / "supplement.json")); info0 = info0 or info; pb.append(info["posterior_bin_probability"])
        lat = S[:, 1]; comp.append([float((lat > -34.5).mean()), float(((lat <= -29.5) & (lat > -34.5)).mean()), float(((lat <= -25.5) & (lat > -29.5)).mean()),
                                    float(((lat <= -21.0) & (lat > -25.5)).mean())])
    def z(a, b):
        a, b = np.asarray(a), np.asarray(b); se = np.sqrt(a.var(ddof=1) / len(a) + b.var(ddof=1) / len(b)); return float((a.mean() - b.mean()) / se) if se > 0 else 0.0
    rh = {k: [r["handoff_m0011"][{"alt_ft": "alt_ft"}.get(k, k)] if k in r["handoff_m0011"] else None for r in ref] for k in F}
    keymap = {"north_33": "north_33", "north_30": "north_30", "north_25": "north_25"}
    res["new_seeds"] = {"n": len(seeds), "supplement_weight_sum_mean": float(np.mean(wsum)),
        "prior_recovery_supplement_vs_runj": {k: z(sup[k], rh[k]) for k in F if rh[k][0] is not None},
        "reallocation_normal_vs_runj": {k: z(nor[k], rh[k]) for k in F if rh[k][0] is not None},
        "reallocation_final_vs_runj": {k: z(fin[k], [r["final"][k] for r in ref]) for k in fin},
        "means": {k: [float(np.mean(sup[k])), float(np.mean(nor[k])), float(np.mean(rh[k]))] for k in F if rh[k][0] is not None},
        "composition_rows_00_11": {"north_of_34.5": float(np.mean([c[0] for c in comp])), "34.5-29.5": float(np.mean([c[1] for c in comp])),
                                   "29.5-25.5": float(np.mean([c[2] for c in comp])), "25.5-21.0": float(np.mean([c[3] for c in comp]))},
        "lnZ_seed_sd_by_mode_new": np.std(np.array(lnz), axis=0, ddof=1).tolist(),
        "lnZ_seed_sd_by_mode_runj": np.std(np.array([r["lnZ_by_mode"] + [r["log_evidence"]] for r in ref]), axis=0, ddof=1).tolist(),
        "lnZ_mean_new": np.mean(np.array(lnz), axis=0).tolist(), "lnZ_mean_runj": np.mean(np.array([r["lnZ_by_mode"] + [r["log_evidence"]] for r in ref]), axis=0).tolist()}
    p = np.mean(np.array(pb), axis=0); t = np.array(info0["target"]); e = np.array(info0["edges_deg"])
    h = np.where(p > 0, t / np.where(p > 0, p, 1), 0.0); H = t[p > 0].sum(); r = info0["defensive"] + (1 - info0["defensive"]) * h / H
    res["r_hat"] = {"edges_deg": e.tolist(), "r_hat": r.tolist(), "outside": info0["defensive"], "pooled_posterior_bin_probability": p.tolist()}
json.dump(res, open(OUT, "w"), indent=1)
print(json.dumps({k: (v if k != "r_hat" else "...") for k, v in res.items()}, indent=1)[:6000])
