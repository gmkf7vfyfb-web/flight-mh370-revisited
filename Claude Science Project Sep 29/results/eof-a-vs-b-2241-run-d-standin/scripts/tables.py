"""Markdown tables for the stand-in results note, generated from abd/aggregate.json and abd/distinct_particles.json (no retyping)."""
import json, pathlib, numpy as np
W = pathlib.Path(__file__).resolve().parents[1]; A = json.load(open(W / "abd/aggregate.json"))
DP = json.load(open(W / "abd/distinct_particles.json")) if (W / "abd/distinct_particles.json").exists() else {}
STR = [("next-d-free", "Free"), ("next-d-repro-radar", "Davey dynamics + radar"), ("next-d-routes", "Routes"), ("next-d-descent-climb", "Descent-climb")]
OPT = [("m0011", "Held Out"), ("m0011+r600-bto", "R600 BTO Only"), ("m0011+r600/no-offset", "R600 BTO + Raw BFO"),
       ("m0011+r600/inflated", "R600 BTO + BFO, inflated noise"), ("m0011+r600/startup-offset", "R600 BTO + BFO, start-up offset"),
       ("m0011+both/no-offset", "both bursts, raw BFO (H1/H2 data)"), ("m0011+both/inflated", "both bursts, inflated"), ("m0011+both/startup-offset", "both bursts, start-up offset"),
       ("m2315-bfo", "(part) 23:15 BFO only"), ("m0011-bto", "(part) 00:11 BTO only"), ("m0011-bfo", "(part) 23:15 + 00:11 BFO")]
f = lambda d: f"{d['ln_BF_mean']:+.2f} ± {d['seed_se']:.2f}"
out = []
out.append("| 00:19 option (with 23:15 + 00:11) | " + " | ".join(l for _, l in STR) + " | mixture ([stop] evidence) | mixture (README P) |")
out.append("|---|" + "---|" * (len(STR) + 2))
for key, lab in OPT:
    for ver in ("", "~v212"):
        k = key + ver; cells = []
        for st, _ in STR:
            d = A["per_stratum"].get(st, {}).get(k)
            cells.append("—" if not d else (f"**{f(d)}**" if d["estimable"] else f"{f(d)} (n.e.; par {d['min_eff_parents_A']:.0f}/{d['min_eff_parents_B']:.0f})"))
        for mode in ("stop_evidence", "readme_P"):
            d = A["mixed"][mode]["options"].get(k)
            cells.append("—" if not d else (f"**{f(d)}**" if d["estimable"] else f"{f(d)} (n.e.)"))
        out.append(f"| {lab}{' ~v212' if ver else ''} | " + " | ".join(cells) + " |")
T1 = "\n".join(out)
out = ["| stratum | option | eff. parents A (min / mean over seeds) | eff. parents B | eff. impacts A (min) | eff. impacts B (min) | median impact lat A / B | v212 weight removed A / B |", "|---|---|---|---|---|---|---|---|"]
for st, lab in STR:
    for key, ol in OPT[:5]:
        d = A["per_stratum"].get(st, {}).get(key); v = A["per_stratum"].get(st, {}).get(key + "~v212")
        if not d: continue
        out.append(f"| {lab} | {ol} | {d['min_eff_parents_A']:.0f} | {d['min_eff_parents_B']:.0f} | {d['min_eff_impacts_A']:.0f} | {d['min_eff_impacts_B']:.0f} | {d['median_lat_A']:.2f} / {d['median_lat_B']:.2f} | "
                   + (f"{100*v['removed_share_A']:.1f} % / {100*v['removed_share_B']:.1f} %" if v else "—") + " |")
T2 = "\n".join(out)
FN = {"1": "A1", "2": "A2", "4": "A, controlled then lost", "3": "B, ditching approach", "5": "B, control lost en route", "6": "outside B"}
out = ["| stratum | arm | family | prior share | posterior share, Held Out | posterior share, R600 BTO Only |", "|---|---|---|---|---|---|"]
for st, lab in STR:
    ks = A["seeds_done"][st]
    for arm in ("A", "B"):
        for code in (("1", "2", "4") if arm == "A" else ("3", "5", "6")):
            pr = np.mean([json.load(open(W / f"abd/ab-{st}-s{k}-standin.json"))[arm]["prior_family_share"][code] for k in ks])
            h = A["per_stratum"][st]["m0011"][f"family_share_{arm}"][code]; b = A["per_stratum"][st]["m0011+r600-bto"][f"family_share_{arm}"][code]
            out.append(f"| {lab} | {arm} | {FN[code]} | {pr:.3f} | {h:.3f} | {b:.3f} |")
T3 = "\n".join(out)
rc = A["run_c_descent_climb_eof"]; out = ["| option | run C descent-climb, module's runs, per seed (1-4) | mean ± s.e. | run D descent-climb, stand-in (mean ± s.e.) |", "|---|---|---|---|"]
for key, lab in OPT[:5] + OPT[8:]:
    v = [rc[s].get(key) for s in sorted(rc)]
    if any(x is None for x in v): continue
    d = A["per_stratum"]["next-d-descent-climb"].get(key)
    out.append(f"| {lab} | " + ", ".join(f"{x:+.2f}" for x in v) + f" | {np.mean(v):+.2f} ± {np.std(v, ddof=1)/np.sqrt(len(v)):.2f} | " + (f(d) if d else "—") + " |")
T4 = "\n".join(out)
out = ["| stratum | seed | stratum weight at 22:41 (equal priors × [stop] evidence) | hand-off rows: ESS of corrected weights / distinct filter particles |", "|---|---|---|---|"]
for k, wts in A["mixed"].get("stratum_weight_at_handoff", {}).items():
    for st, lab in STR:
        dp = DP.get(f"{st}-A-s{k}", {})
        out.append(f"| {lab} | {k} | {wts[st]:.3f} | " + (f"{dp['handoff_ess_rows']:.0f} / {dp['distinct_rows_in_handoff']}" if dp else "—") + " |")
T5 = "\n".join(out)
json.dump({"T1": T1, "T2": T2, "T3": T3, "T4": T4, "T5": T5}, open(W / "abd/tables.json", "w"))
print(T1); print(); print(T4)
