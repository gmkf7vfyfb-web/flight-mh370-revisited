"""Bayes factors for the five core 00:19 options on the SAME data (architecture ruling ~15:45 -0600 10 Oct, item 3).
D_00:19 = {R600 BTO, R600 BFO, R1200 BTO, R1200 BFO, log-on time}. An option scores an observation with its nominal
likelihood or treats it as anomalous: a declared proper uniform density over the observation's feasible range (central
widths BFO 700 Hz, BTO 20,000 us, log-on time 3,896 s; sensitivities in W). Input: family_evidence.py output (per-family
ln Zhat, which carries the nominal likelihoods' normalising constants); families mixed by its p_core.
First used for results/eof-same-data-bf-oct10 (constraint `alive`); scripted 10 Oct ~23:00 UTC for run C.

Usage: python same_data_bf.py FAMILY_EVIDENCE_JSON OUT_JSON [constraint: alive|unpowered|silent|none; default unpowered]
"""
import json, math, itertools, sys

NOMINAL = {  # R600 BTO, R600 BFO, R1200 BTO, R1200 BFO, log-on time
    "00:19 Held Out": (0, 0, 0, 0, 0), "00:19 R600 BTO Only": (1, 0, 0, 0, 0), "00:19 R600 BTO + Raw BFO": (1, 1, 0, 0, 0),
    "00:19 Holland H1": (1, 1, 0, 1, 1), "00:19 Holland H2": (1, 1, 0, 1, 0)}
W = {"bfo": (350.0, 700.0, 1400.0), "bto": (2000.0, 20000.0, 60000.0), "t": (1800.0, 3896.0, 7200.0)}
CENTRAL = "W_bfo=700Hz,W_bto=20000us,W_logon=3896s"


def main(inp, outp, con="unpowered"):
    d = json.load(open(inp)); P = d["p_core"]; S = list(P); suf = "" if con == "none" else f" +{con}"
    lz = lambda o, s: d["strata"][s][o + suf]["ln_Zhat"]
    res = {"constraint": con, "p_core": P, "settings": {}}
    for wb, wt, wl in itertools.product(W["bfo"], W["bto"], W["t"]):
        tab = {}
        for o, n in NOMINAL.items():
            add = -((not n[0]) + (not n[2])) * math.log(wt) - ((not n[1]) + (not n[3])) * math.log(wb) - (not n[4]) * math.log(wl)
            per = {s: lz(o, s) + add for s in S}
            tab[o] = (per, math.log(sum(P[s] * math.exp(per[s]) for s in S)))
        ref = tab["00:19 Held Out"]
        res["settings"][f"W_bfo={wb:.0f}Hz,W_bto={wt:.0f}us,W_logon={wl:.0f}s"] = {
            o: {"lnZ_mixture": m, "lnBF_vs_held_out": m - ref[1],
                "per_family_lnBF_vs_held_out": {s: per[s] - ref[0][s] for s in S},
                "per_family_seed_se": {s: d["strata"][s][o + suf]["ln_Zhat_se"] for s in S}} for o, (per, m) in tab.items()}
    res["summary"] = {o: {"central": res["settings"][CENTRAL][o]["lnBF_vs_held_out"],
                          "min": min(v[o]["lnBF_vs_held_out"] for v in res["settings"].values()),
                          "max": max(v[o]["lnBF_vs_held_out"] for v in res["settings"].values())} for o in NOMINAL}
    json.dump(res, open(outp, "w"), indent=1)
    for o, v in res["summary"].items():
        print(f"{o:28s} ln BF vs Held Out {v['central']:+.2f} (range {v['min']:+.2f} to {v['max']:+.2f})")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else "unpowered")
