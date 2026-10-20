"""Reduced impact table for downstream modules: run J waypoints production + northern supplement, rule B (overnight order A).

    python supplement_reduced.py SUMMARY_JSON OUT_DIR TARGET_C PROD_ROOT CORE_HANDOFF_ROOT SUPP_ROOT[,XD_ROOT] [SUPP_ROOT2[,XD_ROOT2] ...]

(20 Oct: several supplement row sets, e.g. the two halves north-k2 and north-k2b, each with its extra-descents root.)

One unbiased Poisson (Horvitz-Thompson) thinning of every impact row of both techniques (and of the extra-descents pass, if
given), with inclusion probability pi_i = min(1, C x max_d a_id), a_id = m_id / Z_{d,b} the row's rule-B mass under 00:19 treatment d
normalised by the treatment's mass in the row's 5 deg impact-latitude band b (so every band keeps up to about C effective rows,
not only the southern bands that hold most of the mass) and under treatment d (D0'..D5, q = 1/3, C2 silent, survival factor; supplement_combine.py) and, for production rows, also the
production-alone mass. Every kept row stores ln(a_id / pi_i) per treatment, so for any treatment and any function f,
sum_kept exp(lnw_d) f estimates the rule-B posterior mean of f without bias (sum of exp(lnw_d) = 1 in expectation).
A row with a_id >= 1/C under any treatment is kept with probability 1. The stored ln weights are normalised by Z_d (not Z_{d,b}).
Output: OUT_DIR/impacts-ruleB.npz (columns listed in "columns") and OUT_DIR/impacts-ruleB.json (provenance, C, counts, and the
per-treatment sums of the stored weights, which are within Monte Carlo noise of 1).
"""
import json, os, pathlib, sys, zlib
import numpy as np
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from compact_impacts import load
from supplement_combine import row_terms, r_hat, CELLS, XD_CELLS

KEEP = ["latitude_deg", "longitude_deg", "t_impact_s", "velocity_east_mps", "velocity_north_mps", "velocity_up_mps",
        "flight_path_angle_deg", "mass_kg", "latent:impact_heading_deg", "latent:impact_bank_deg", "latent:impact_energy_transferred_j",
        "latent:breakup_p_intact", "latent:breakup_p_broken", "latent:breakup_p_fragmented", "latent:debris_class",
        "latent:spiral_bank_cap_deg", "latent:pushover_drawn", "latent:onset_mechanism", "latent:control_realised", "latent:recovery_attempted"]


def main(summary, outd, C, prod_root, core_root, *supp_specs):
    S = json.load(open(summary)); C = float(C); outd = pathlib.Path(outd); outd.mkdir(parents=True, exist_ok=True)
    S1, S2, N1, N2, K = (float(os.environ[v]) for v in ("SUP_S1", "SUP_S2", "SUP_N1", "SUP_N2", "SUP_K"))
    lnZc = {d: S["cells"][d]["comb"]["imp"]["lnZ"] for d in CELLS}; lnZa = {d: S["cells"][d]["alone"]["imp"]["lnZ"] for d in CELLS}
    BND = np.arange(-45.0, -14.0, 5.0)
    lbm = {f"{v}/{d}": np.log(np.maximum([r["mass"] for r in S["cells"][d][v]["imp"]["bands"]], 1e-12)) for v in ("comb", "alone") for d in CELLS}
    jobs = [("prod", int(p.name.split("-")[1]), p, pathlib.Path(core_root) / p.name / "handoff-m0011" / "handoff.npy", None)
            for p in sorted(pathlib.Path(prod_root).glob("seed-*")) if p.is_dir()]
    for h, spec in enumerate(supp_specs):
        supp_root, xd_root = (spec.split(",") + [None])[:2]
        for p in sorted(pathlib.Path(supp_root).glob("seed-*")):
            if not p.is_dir(): continue
            s = int(p.name.split("-")[1]); jobs.append(("supp", (h, s), p, p / "handoff-subset.npy", None))
            if xd_root and xd_root != "-":
                for gd in sorted((pathlib.Path(xd_root) / p.name).glob("g[0-9]*")):
                    if (gd / "SHA256SUMS").exists(): jobs.append(("xd", (h, s), gd, gd / "handoff.npy", p))
    xd_sel = {}
    for tech, s, sd, hf, base in jobs:
        if tech == "xd":
            idx = np.asarray(json.load(open(sd / "select.json"))["subset_index"]); xd_sel.setdefault(s, []).append(idx)
    cols, kept, tot = None, [], {f"comb/{d}": 0.0 for d in CELLS} | {f"alone/{d}": 0.0 for d in CELLS}
    rng = np.random.default_rng(20261019)
    for tech, s, sd, hf, base in jobs:
        R = row_terms(sd, hf); meta, g = load(sd); n = len(R["lat"])
        r = r_hat(R["lat0011"]); b1 = N1 / (N1 + N2 * r); b2 = N2 * r / (N1 + N2 * r)
        lnc = np.log(b1 / S1) if tech == "prod" else np.log(b2 * K / S2)
        a = {}
        if tech == "xd":
            nx = float(meta["config"]["terminal"]["children"] * 4); idx = np.asarray(json.load(open(sd / "select.json"))["subset_index"])
            par_sub = idx[R["par"]]
            for d in CELLS: a[f"comb/{d}"] = R["t"][d] + lnc + np.log(nx / (64 + nx)) - lnZc[d] if d in XD_CELLS else np.full(n, -np.inf)
        else:
            adj = np.zeros(n)
            if tech == "supp" and s in xd_sel:
                sel = np.zeros(R["n_handoff"], bool); sel[np.concatenate(xd_sel[s])] = True
                nx = 256.0; adj = np.where(sel[R["par"]], np.log(64 / (64 + nx)), 0.0)
            for d in CELLS: a[f"comb/{d}"] = R["t"][d] + lnc + (adj if d in XD_CELLS else 0.0) - lnZc[d]
            if tech == "prod":
                for d in CELLS: a[f"alone/{d}"] = R["t"][d] + np.log(1 / S1) - lnZa[d]
            par_sub = R["par"]
        for k in tot:
            if k not in a: a[k] = np.full(n, -np.inf)
        A = np.stack([np.where(np.isfinite(a[k]), a[k], -np.inf) for k in tot])
        bi = np.clip(np.digitize(R["lat"], BND) - 1, 0, len(BND) - 2)
        Ab = np.stack([A[i] - lbm[k][bi] for i, k in enumerate(tot)])
        amax = np.exp(np.max(Ab, axis=0)); pi = np.minimum(1.0, C * amax)
        keep = rng.random(n) < pi; lnpi = np.log(pi[keep])
        for i, k in enumerate(tot): tot[k] += float(np.exp(A[i, keep] - lnpi).sum())
        if tech == "supp" or tech == "xd":
            orig = np.asarray(json.load(open((base or sd) / "stride.json"))["kept_original_rows"])[par_sub]
        else:
            orig = par_sub
        half, seed = s if isinstance(s, tuple) else (-1, s)
        blk = {"technique": np.full(keep.sum(), {"prod": 0, "supp": 1, "xd": 2}[tech], np.float32), "seed": np.full(keep.sum(), seed, np.float32),
               "supplement_half": np.full(keep.sum(), half, np.float32),
               "handoff_row": orig[keep].astype(np.float32), "family4_code": R["f4"][keep].astype(np.float32),
               "lat_0011_deg": R["lat0011"][keep].astype(np.float32)}
        for c in KEEP: blk[c] = g(c)[keep].astype(np.float64 if c == "t_impact_s" else np.float32)
        for i, k in enumerate(tot): blk["lnw:" + k] = (A[i, keep] - lnpi).astype(np.float32)
        kept.append(blk); cols = list(blk)
        print(f"{tech} {s} {sd.name}: kept {keep.sum()} of {n}", flush=True)
    T = {c: np.concatenate([b[c] for b in kept]) for c in cols}
    np.savez(outd / "impacts-ruleB.npz", **T)
    json.dump({"rule": "core results/run-j-supplement README section 5 rule B; supplement K-strided (u2 x K); extra descents pooled 64:256 per selected parent (D2-D5)",
               "C": C, "inclusion": "pi = min(1, C max_d m_d / Z_{d, 5-deg impact band})", "rows": int(len(T["technique"])), "columns": cols, "technique_codes": {"0": "run J production", "1": "supplement first pass (64 descents per parent)", "2": "supplement extra descents (256 per parent, thinned; D2-D5 only)"},
               "lnw_sum_check": tot, "S1": S1, "S2": S2, "N1": N1, "N2": N2, "K": K, "treatments": {"D0": "00:19 data not used (D0')", "D1": "R600 BTO", "D2": "R600 BTO + BFO", "D3": "both BFOs as recorded", "D4": "both BFOs, Holland transient bias added", "D5": "R600 BTO + BFO + R1200 BFO with start-up offset", "D3s": "D3, log-on from another cause only (C2 silent, no q mixture)", "D4s": "D4, log-on from another cause only", "D5s": "D5, log-on from another cause only"},
               "weights": "D0-D5: q = 1/3 total, C2 silent, survival factor; D3s-D5s: the C2-silent arm alone (cause-specific cell); lnw:alone/* are production-alone weights (supplement rows -inf)"},
              open(outd / "impacts-ruleB.json", "w"), indent=1)
    print("rows", len(T["technique"]), json.dumps(tot))


if __name__ == "__main__":
    main(*sys.argv[1:])
