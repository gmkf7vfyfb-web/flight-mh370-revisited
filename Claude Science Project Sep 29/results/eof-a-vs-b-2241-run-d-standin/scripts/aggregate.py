"""Stand-in aggregation of the 22:41 A-vs-B on run D: per-stratum seed means, seed s.e., estimability gate, strata mixture."""
import json, glob, pathlib, re, math, sys
import numpy as np
from scipy.special import logsumexp
W = pathlib.Path(__file__).resolve().parents[1]; D = W / "abd"
EOFRUNS = pathlib.Path("/Users/pete/.claude-science/orgs/9db41e8b-db54-4736-82b9-d77e2a9ad222/workspaces/83c5d472-a2a6-4ff0-9602-ceefbdadb1ad/repo/Claude Science Project Sep 29/engine/runs")
STRATA = [("next-d-free", "Free"), ("next-d-repro-radar", "Davey dynamics + radar"), ("next-d-routes", "Routes"), ("next-d-descent-climb", "Descent-climb")]
P_README = {"next-d-repro-radar": 0.235, "next-d-free": 0.594, "next-d-routes": 0.019, "next-d-descent-climb": 0.153}  # run D README, equal priors
OPTS = [("m0011", "00:19 Held Out (23:15 BFO, 00:11 BTO+BFO)"), ("m0011+r600-bto", "00:19 R600 BTO Only"),
        ("m0011+r600/no-offset", "00:19 R600 BTO + Raw BFO"), ("m0011+r600/inflated", "R600 BTO + BFO, inflated noise (34 Hz)"),
        ("m0011+r600/startup-offset", "R600 BTO + BFO, Holland start-up offset"),
        ("m0011+both/no-offset", "both 00:19 bursts, raw BFO"), ("m0011+both/inflated", "both 00:19 bursts, inflated"),
        ("m0011+both/startup-offset", "both 00:19 bursts, start-up offset"),
        ("m2315-bfo", "23:15 BFO only"), ("m0011-bto", "00:11 BTO only"), ("m0011-bfo", "23:15 + 00:11 BFO only")]
GATE_PAR, GATE_SE = 30.0, 0.25

def stop_ev(f):
    t = pathlib.Path(f).read_text(); m = re.search(r"^log_evidence = ([-0-9.eE+]+)", t, re.M); return float(m.group(1)) if m else None

rows = {}; ev = {}
for st, _ in STRATA:
    for f in sorted(D.glob(f"ab-{st}-s*-standin.json")):
        k = int(re.search(r"-s(\d+)-standin", f.name).group(1)); rows[(st, k)] = json.loads(f.read_text())
        ev[(st, k)] = stop_ev(D / f"stop-{st}-s{k}.toml")
seeds = sorted({k for _, k in rows})
out = {"seeds_done": {st: sorted(k for s, k in rows if s == st) for st, _ in STRATA}, "per_stratum": {}, "mixed": {}, "stop_log_evidence": {f"{s}:{k}": v for (s, k), v in ev.items()}}

def summ(vals, parA, parB, impA, impB):
    v = np.array(vals); n = len(v)
    se = float(v.std(ddof=1) / math.sqrt(n)) if n > 1 else float("nan")
    est = bool(n >= 2 and min(parA) >= GATE_PAR and min(parB) >= GATE_PAR and se <= GATE_SE)
    return {"n_seeds": n, "ln_BF_mean": float(v.mean()), "seed_se": se, "per_seed": [float(x) for x in v],
            "min_eff_parents_A": float(min(parA)), "min_eff_parents_B": float(min(parB)),
            "min_eff_impacts_A": float(min(impA)), "min_eff_impacts_B": float(min(impB)), "estimable": est}

for st, lab in STRATA:
    ks = sorted(k for s, k in rows if s == st)
    if not ks: continue
    o = {}
    for key, _ in OPTS:
        for ver in ("", "~v212"):
            kk = key + ver; R = [rows[(st, k)] for k in ks if rows[(st, k)]["A"]["options"].get(kk) and rows[(st, k)]["B"]["options"].get(kk)]
            if not R: continue
            s = summ([r["ln_BF_A_to_B"][kk] for r in R], [r["A"]["options"][kk]["eff_parents"] for r in R], [r["B"]["options"][kk]["eff_parents"] for r in R],
                     [r["A"]["options"][kk]["eff_impacts"] for r in R], [r["B"]["options"][kk]["eff_impacts"] for r in R])
            s["median_lat_A"] = float(np.mean([r["A"]["options"][kk]["median_lat"] for r in R])); s["median_lat_B"] = float(np.mean([r["B"]["options"][kk]["median_lat"] for r in R]))
            s["family_share_A"] = {f: float(np.mean([r["A"]["options"][kk]["family_share"][f] for r in R])) for f in R[0]["A"]["options"][kk]["family_share"]}
            s["family_share_B"] = {f: float(np.mean([r["B"]["options"][kk]["family_share"][f] for r in R])) for f in R[0]["B"]["options"][kk]["family_share"]}
            if ver: s["removed_share_A"] = float(np.mean([r["A"]["options"][kk]["removed_share_v212"] for r in R])); s["removed_share_B"] = float(np.mean([r["B"]["options"][kk]["removed_share_v212"] for r in R]))
            o[kk] = s
    out["per_stratum"][st] = o

# mixture over strata per seed index: (i) equal stratum priors x evidence to the hand-off ([stop].log_evidence); (ii) fixed run D README P(family)
full = [k for k in seeds if all((st, k) in rows for st, _ in STRATA)]
for mode in ("stop_evidence", "readme_P"):
    o = {}
    for key, _ in OPTS:
        for ver in ("", "~v212"):
            kk = key + ver; vals = []; parA = []; parB = []
            for k in full:
                R = [rows[(st, k)] for st, _ in STRATA]
                if not all(r["A"]["options"].get(kk) and r["B"]["options"].get(kk) for r in R): break
                lw = np.array([ev[(st, k)] for st, _ in STRATA]) if mode == "stop_evidence" else np.log([P_README[st] for st, _ in STRATA])
                lw = lw - logsumexp(lw)
                zA = logsumexp(lw + np.array([r["A"]["options"][kk]["ln_Z"] for r in R])); zB = logsumexp(lw + np.array([r["B"]["options"][kk]["ln_Z"] for r in R]))
                vals.append(float(zA - zB)); parA.append(min(r["A"]["options"][kk]["eff_parents"] for r in R)); parB.append(min(r["B"]["options"][kk]["eff_parents"] for r in R))
            else:
                if vals: o[kk] = summ(vals, parA, parB, [1e9], [1e9]); o[kk]["note"] = "eff-parent minima are the smallest over strata"
    out["mixed"][mode] = {"seeds": full, "options": o}
    if mode == "stop_evidence" and full:
        out["mixed"]["stratum_weight_at_handoff"] = {k: {st: float(np.exp(np.array([ev[(s, k)] for s, _ in STRATA]) - logsumexp([ev[(s, k)] for s, _ in STRATA]))[i]) for i, (st, _) in enumerate(STRATA)} for k in full}

# run C comparison (end of flight's own JSONs, descent-climb seeds 1-4)
rc = {}
for f in sorted(EOFRUNS.glob("C2241-next-c-descent-climb-s*-ab.json")):
    j = json.loads(f.read_text()); rc[j["seed"]] = {k: v["ln_BF_A_to_B"] for k, v in j["options"].items()} | {k + ":effpar": (v["A"]["eff_parents"], v["B"]["eff_parents"]) for k, v in j["options"].items()}
out["run_c_descent_climb_eof"] = rc
json.dump(out, open(D / "aggregate.json", "w"), indent=1)
for st, lab in STRATA:
    for kk in ("m0011", "m0011+r600-bto", "m0011+r600/no-offset", "m0011~v212"):
        s = out["per_stratum"].get(st, {}).get(kk)
        if s: print(f"{lab:24s} {kk:24s} n={s['n_seeds']} lnBF {s['ln_BF_mean']:+.2f} ± {s['seed_se']:.2f}  minpar {s['min_eff_parents_A']:.0f}/{s['min_eff_parents_B']:.0f} {'EST' if s['estimable'] else 'not-est'}")
for kk in ("m0011", "m0011+r600-bto", "m0011+r600/no-offset"):
    s = out["mixed"]["stop_evidence"]["options"].get(kk)
    if s: print(f"MIXED(stop) {kk:24s} lnBF {s['ln_BF_mean']:+.2f} ± {s['seed_se']:.2f}")
