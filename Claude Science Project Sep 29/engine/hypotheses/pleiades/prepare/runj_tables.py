"""Markdown tables for the run J results note, read from aggregate_runj.py / aggregate_runj_joined.py outputs (no hand-typed numbers).
    python runj_tables.py TABLE_JSON JOINED_JSON OUT_MD"""
import json, sys
T = json.load(open(sys.argv[1])); J = json.load(open(sys.argv[2])); o = []
DN = {"D0": "D0′ held out, transmission imposed", "D1": "D1 R600 BTO", "D2": "D2 R600 BTO + R600 BFO", "D3": "D3 R600 BTO + both BFOs (H2 data)",
      "D4": "D4 R600 BTO + both BFOs, Holland transient bias (H1 data)", "D5": "D5 R600 BTO + R600 BFO + R1200 BFO with offset"}
def table(var, stg, causes, title):
    V = T["variants"][var]; ref = V["D0 x total q=1/3 (C2 silent)"][stg]["ln_mean_LH"]
    o.append(f"\n### {title}\n\n| D | cause | ESS under H (without H) | A1 / A2 / B ESS under H | mean under H | shift NM | ln S (p) | 90 % km² under H (without H) | PDF without H inside H 90 % | ln E[L_H] − D0′ (seed SD) |\n|---|---|---|---|---|---|---|---|---|---|")
    for ck, e in V.items():
        d, c = ck.split(" x ", 1)
        if c not in causes or (var == "prodonly" and d not in ("D3", "D4")): continue
        x = e[stg]; x0 = e["none (without H)"]; t = x["tension"]; f = x["families"]
        gap = " **GAP**" if x["eff_impacts"] < 1000 else ""
        o.append(f"| {DN[d]} | {c} | {x['eff_impacts']:,.0f} ({x0['eff_impacts']:,.0f}){gap} | {f['A1']['eff_impacts']:,.0f} / {f['A2']['eff_impacts']:,.0f} / {f['B']['eff_impacts']:,.0f} | "
                 f"{abs(x['mean_lat']):.2f} S {x['mean_lon']:.2f} E | {t['mean_shift_nm']:.0f} | {t['ln_S']:+.2f} ({t['tension_p']:.2f}) | {t['cond_hdr90_km2']:,.0f} ({t['uncond_hdr90_km2']:,.0f}) | "
                 f"{100 * t['uncond_in_cond_hdr90']:.0f} % | {x['ln_mean_LH'] - ref:+.2f} ({x.get('ln_mean_LH_waypoints_seed_sd', float('nan')):.2f}) |")
TOT = ("total q=1/3 (C2 silent)",); ALL = ("C1", "C2 silent", "total q=1/3 (C2 silent)")
table("head", "gcrel-0.25", TOT, "Primary: competing-causes total q = 1/3 (C2 silent), headline setting (ρ 0.25, two ocean models, GlobCurrent product-relative)")
table("head", "g12-0.25", TOT, "Beside it: GLORYS12 only, ρ 0.25, total q = 1/3 (C2 silent)")
table("head", "gcrel-0.25", ("C1", "C2 silent"), "Each cause separately, headline setting")
table("prodonly", "gcrel-0.25", ALL, "Check: D3 and D4 with the production waypoints seeds only (no both-burst set), headline setting")
# rho sensitivity
o.append("\n### Transport-error correlation ρ, total q = 1/3 (C2 silent), two ocean models\n\n| D | ρ 0: mean, ESS, ln S | ρ 0.25: mean, ESS, ln S | ρ 0.5: mean, ESS, ln S |\n|---|---|---|---|")
for d in DN:
    e = T["variants"]["head"][f"{d} x total q=1/3 (C2 silent)"]
    o.append(f"| {DN[d]} | " + " | ".join(f"{abs(e[s]['mean_lat']):.2f} S {e[s]['mean_lon']:.2f} E, {e[s]['eff_impacts']:,.0f}, {e[s]['tension']['ln_S']:+.2f}" for s in ("gcrel-0", "gcrel-0.25", "gcrel-0.5")) + " |")
# families
o.append("\n### Family shares, total q = 1/3 (C2 silent): without H → under H (headline setting)\n\n| D | A1 | A2 | B | code 6 (deliberate onset, ditching attempt) |\n|---|---|---|---|---|")
for d in DN:
    e = T["variants"]["head"][f"{d} x total q=1/3 (C2 silent)"]
    o.append(f"| {DN[d]} | " + " | ".join(f"{e['none (without H)']['families'][n]['share']:.3f} → {e['gcrel-0.25']['families'][n]['share']:.3f}" for n in ("A1", "A2", "B", "code 6")) + " |")
# western residual
o.append("\n### Western residual (brief 8.2) on run J impacts, total q = 1/3 (C2 silent): share of mass at ≥ 30 / ≥ 50 NM inside the 00:19 arc (arc_distance_nm)\n\n"
         "| D | without H: ≥ 30 / ≥ 50 NM | under H, whole grid: ≥ 30 / ≥ 50 NM | under H, inside H's 90 % region: ≥ 30 / ≥ 50 NM | same, west of 91.5 E | GLORYS12 only, inside H 90 %: ≥ 30 / ≥ 50 | A1 / A2 / B under H, share of family ≥ 30 NM | ESS under H |\n|---|---|---|---|---|---|---|---|")
for d in DN:
    e = T["variants"]["head"][f"{d} x total q=1/3 (C2 silent)"]; x = e["gcrel-0.25"]; x0 = e["none (without H)"]; g = e["g12-0.25"]; f = x["families"]
    o.append(f"| {DN[d]} | {100*x0['in30_share']:.1f} / {100*x0['in50_share']:.1f} % | {100*x['in30_share']:.1f} / {100*x['in50_share']:.1f} % | {100*x['in30_share_in_H_hdr90']:.1f} / {100*x['in50_share_in_H_hdr90']:.1f} % | "
             f"{100*x['in30_share_in_H_hdr90_west_91p5E']:.1f} / {100*x['in50_share_in_H_hdr90_west_91p5E']:.1f} % | {100*g['in30_share_in_H_hdr90']:.1f} / {100*g['in50_share_in_H_hdr90']:.1f} % | "
             f"{100*f['A1']['in30_share_of_family']:.1f} / {100*f['A2']['in30_share_of_family']:.1f} / {100*f['B']['in30_share_of_family']:.1f} % | {x['eff_impacts']:,.0f}{' **GAP**' if x['eff_impacts'] < 1000 else ''} |")
# joined
o.append(f"\n### Planned descents before 00:11 (end of flight's joined V2, run J waypoints, seed pairs {J['seeds'][0]}-{J['seeds'][-1]}), total q = 1/3 (C2 silent), headline setting\n\n"
         "| D | B share, median of seeds (range): without H → under H | B share pooled (Z-weighted): without H → under H | pre-00:11 B, median: without H → under H | B ESS under H, sum (min per seed) | all-family ESS under H, sum | mean under H | ln E[L_H] − its D0′, seed median (SD) |\n|---|---|---|---|---|---|---|---|")
r0 = J["cells"]["D0"]["gcrel-0.25"]["ln_mean_LH_seed_median"]
for d, e in J["cells"].items():
    a, b = e["none (without H)"], e["gcrel-0.25"]
    o.append(f"| {DN[d]} | {a['B']['share_median']:.3f} ({a['B']['share_range'][0]:.3f}-{a['B']['share_range'][1]:.3f}) → {b['B']['share_median']:.3f} ({b['B']['share_range'][0]:.3f}-{b['B']['share_range'][1]:.3f}) | "
             f"{a['B']['share_pooled']:.3f} → {b['B']['share_pooled']:.3f} | {a['B']['pre0011_share_median']:.3f} → {b['B']['pre0011_share_median']:.3f} | {b['B']['ess_sum']:,.0f} ({b['B']['ess_min']:,.0f}){' **GAP**' if b['B']['ess_sum'] < 1000 else ''} | "
             f"{b['ess_sum']:,.0f} | {abs(b['mean_lat_pooled']):.2f} S {b['mean_lon_pooled']:.2f} E | {b['ln_mean_LH_seed_median'] - r0:+.2f} ({b['ln_mean_LH_seed_sd']:.2f}) |")
# gate list
g = [x for x in T["gate_fail"] if x["setting"] == "gcrel-0.25"]
o.append("\n### Cells and families below the 1,000 gate under H (headline setting)\n\n" + "; ".join(f"{x['cell']}{'' if x['family'] == 'all' else ', ' + x['family']} ({x['ess']:,.0f})" for x in g) + ".")
open(sys.argv[3], "w").write("\n".join(o) + "\n")
