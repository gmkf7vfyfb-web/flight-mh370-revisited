"""Markdown tables for README.md from run-j-reduced.json (same folder).  python make_tables.py > tables.md"""
import json, math, pathlib
r = json.load(open(pathlib.Path(__file__).with_name('run-j-reduced.json')))
F = ["run-j-waypoints", "run-j-free", "run-j-descent-climb", "run-j-repro-radar"]
f = lambda x, n=3: f"{x:.{n}f}"
print("**Table 1. D0' (00:19 values held out, transmission imposed) per family folder, base, rho 0.05.**\n")
print("| family | P(family), core | seeds | rows | Z | Z split-half | Z without OI (sens.) | on searched ground before → after | ATSB ground before → after | in next OI area before → after (layer) | ESS before / after |")
print("|---|---|---|---|---|---|---|---|---|---|---|")
for st in F:
    b = r['per_stratum'][st]['D0']['base_rho0.05']['all']; x = r['per_stratum'][st]['D0']['without_oi_rho0.05']['all']
    print(f"| {st} | {r['P_family_core'][st]:.4f} | {r['seeds'][st]} | {r['rows'][st]:,} | {f(b['Z'],4)} | {f(b['Z_split_half'][0],4)} / {f(b['Z_split_half'][1],4)} | {f(x['Z'],4)} | {f(b['on_searched_before'])} → {f(b['on_searched_after'])} | {f(b['on_atsb_before'])} → {f(b['on_atsb_after'])} | {f(b['next_area_before'])} → {f(b['next_area_after'])} | {b['ess_before']:,.0f} / {b['ess_after']:,.0f} |")
m = r['mixture']['D0']
print("\n**Table 2. D0', four-family mixture (core P(family)): the rho sweep and the sensitivity without Ocean Infinity.**\n")
print("| case | Z | ln Z | on searched ground before → after | ATSB ground before → after | in next OI area before → after (layer) | north of 33 S before → after | ESS after |")
print("|---|---|---|---|---|---|---|---|")
lab = {"base_rho0.05": "base, rho 0.05 (reference)", "base_rho0": "base, rho 0", "base_rho0.25": "base, rho 0.25", "base_rho0.5": "base, rho 0.5", "without_oi_rho0.05": "sensitivity: without Ocean Infinity, rho 0.05"}
for s in lab:
    b = m[s]['all']
    print(f"| {lab[s]} | {f(b['Z'],4)} | {f(math.log(b['Z']),3)} | {f(b['on_searched_before'])} → {f(b['on_searched_after'])} | {f(b['on_atsb_before'])} → {f(b['on_atsb_after'])} | {f(b['next_area_before'])} → {f(b['next_area_after'])} | {f(b['north33_before'])} → {f(b['north33_after'])} | {b['ess_after']:,.0f} |")
print("\n**Table 3. D0', mixture, by hypothesis family (A1 / A2 / B), base, rho 0.05.**\n")
print("| family | share before | share after | Z | on searched ground before → after | in next OI area after (layer) | ESS before / after |")
print("|---|---|---|---|---|---|---|")
for hf in ["A1", "A2", "B"]:
    b = m['base_rho0.05'][hf]
    print(f"| {hf} | {f(b['share_before'])} | {f(b['share_after'])} | {f(b['Z'],4)} | {f(b['on_searched_before'])} → {f(b['on_searched_after'])} | {f(b['next_area_after'])} | {b['ess_before']:,.0f} / {b['ess_after']:,.0f} |")
names = {"D0": "D0' held out", "D1": "D1 R600 BTO", "D2": "D2 R600 BTO + BFO", "D3": "D3 both BFOs (H2 data)†", "D4": "D4 shared offset (H1 data)†", "D5": "D5 R1200 BFO with offset"}
print("\n**Table 4. All six 00:19 options, mixture, base, rho 0.05** († D3/D4: waypoints from the both-burst supplementary set).\n")
print("| option | Z | Z without OI (sens.) | on searched ground before → after | in next OI area after (layer) | ESS before / after | ESS after A1 / A2 / B |")
print("|---|---|---|---|---|---|---|")
for D in names:
    b = r['mixture'][D]['base_rho0.05']['all']; x = r['mixture'][D]['without_oi_rho0.05']['all']; fa = r['mixture'][D]['base_rho0.05']
    print(f"| {names[D]} | {f(b['Z'],4)} | {f(x['Z'],4)} | {f(b['on_searched_before'])} → {f(b['on_searched_after'])} | {f(b['next_area_after'])} | {b['ess_before']:,.0f} / {b['ess_after']:,.0f} | {fa['A1']['ess_after']:,.0f} / {fa['A2']['ess_after']:,.0f} / {fa['B']['ess_after']:,.0f} |")
print("\n**Table 5. D0' per family folder, Z over the rho sweep (base).**\n")
print("| family | rho 0 | rho 0.05 | rho 0.25 | rho 0.5 | between-seed SD of Z (rho 0.05) |")
print("|---|---|---|---|---|---|")
for st in F:
    p = r['per_stratum'][st]['D0']
    print(f"| {st} | " + " | ".join(f(p[s]['all']['Z'], 4) for s in ["base_rho0", "base_rho0.05", "base_rho0.25", "base_rho0.5"]) + f" | {f(p['base_rho0.05']['all']['Z_seed_sd'],4)} |")
print("\n**Table 6. D0' per family folder and hypothesis family, base, rho 0.05: Z (ESS after).**\n")
print("| family | A1 | A2 | B |")
print("|---|---|---|---|")
for st in F:
    p = r['per_stratum'][st]['D0']['base_rho0.05']
    print(f"| {st} | " + " | ".join(f"{p[h]['Z']:.4f} ({p[h]['ess_after']:,.0f})" for h in ["A1", "A2", "B"]) + " |")
