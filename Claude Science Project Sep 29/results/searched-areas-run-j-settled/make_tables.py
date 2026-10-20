"""Tables for results/searched-areas-run-j-settled/README.md from run-j-settled-reduced.json.  python make_tables.py"""
import json
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
R = json.loads((HERE / "run-j-settled-reduced.json").read_text())
OPT = {"D0": "D0' held out", "D1": "D1 R600 BTO", "D2": "D2 R600 BTO + BFO", "D3": "D3 both BFOs (H2 data)†",
       "D4": "D4 shared offset (H1 data)†", "D5": "D5 R1200 BFO with offset"}
SC = {"base_rho0.05": "base, rho 0.05 (reference)", "base_rho0": "base, rho 0", "base_rho0.25": "base, rho 0.25",
      "base_rho0.5": "base, rho 0.5", "without_oi_rho0.05": "sensitivity: without Ocean Infinity, rho 0.05"}
f4 = lambda x: "–" if x is None else f"{x:.4f}"
f3 = lambda x: "–" if x is None else f"{x:.3f}"
L, checks = [], {"resample_vs_exact_point_z": []}


def row_mix(D, cell, sub, scen):
    return R["mixture"][D][cell][sub][scen]


L.append("**Table 1. Impact point against settled seabed position, all six 00:19 options, four-family mixture, base, rho 0.05.**\n")
L.append("| option | Z impact point (all rows) | Z settled position | Δ settled − point (± MC SE) | Z any settled piece (optimistic bound) | "
         "on searched ground before: point → settled | after: point → settled (same outcomes) | after, impact point all rows | "
         "impact off searched ground, field on | outcomes |")
L.append("|---|---|---|---|---|---|---|---|---|---|")
for D in OPT:
    m = row_mix(D, "total", "all", "base_rho0.05")
    L.append(f"| {OPT[D]} | {f4(m['Z_point_exact'])} | **{f4(m['Z_settled'])}** | {m['delta']:+.4f} ± {m['delta_se']:.4f} | "
             f"{f4(m['Z_point_exact'] + m['delta_any'])} | {f3(m['on_searched_before_point'])} → {f3(m['on_searched_before_settled'])} | "
             f"{f3(m['on_searched_after_point'])} → {f3(m['on_searched_after_settled'])} | {f3(m['on_searched_after_point_exact'])} | "
             f"{m['share_point_off_field_on']:.4f} | {m['N']:,} |")
L.append("")
L.append("**Table 2. D0', mixture: the rho sweep and the sensitivity without Ocean Infinity.**\n")
L.append("| case | Z impact point | Z settled | Δ (± SE) | Z any piece | on searched ground after: point → settled (same outcomes) | ATSB ground after, settled | north of 33 S after, settled | in next OI area after, settled (layer) |")
L.append("|---|---|---|---|---|---|---|---|---|")
for s, nm in SC.items():
    m = row_mix("D0", "total", "all", s)
    L.append(f"| {nm} | {f4(m['Z_point_exact'])} | **{f4(m['Z_settled'])}** | {m['delta']:+.4f} ± {m['delta_se']:.4f} | "
             f"{f4(m['Z_point_exact'] + m['delta_any'])} | {f3(m['on_searched_after_point'])} → {f3(m['on_searched_after_settled'])} | "
             f"{f3(m['on_atsb_after_settled'])} | {f3(m['north33_after_settled'])} | {f3(m['next_area_after_settled'])} |")
L.append("")
L.append("**Table 3. By hypothesis family (A1 / A2 / B), mixture, base, rho 0.05: impact point → settled.**\n")
L.append("| option | family | Z impact point | Z settled | Δ (± SE) | share before | share after, point | share after, settled | on searched ground after: point → settled | row ESS before: waypoints source / lowest other stratum |")
L.append("|---|---|---|---|---|---|---|---|---|---|")
for D in OPT:
    for sub in ("A1", "A2", "B"):
        m = row_mix(D, "total", sub, "base_rho0.05")
        wp = R["per_stratum"]["run-j-waypoints"][D]["total"][sub]["base_rho0.05"]["row_ess_before"]
        oth = min(R["per_stratum"][st][D]["total"][sub]["base_rho0.05"]["row_ess_before"] for st in R["per_stratum"] if st != "run-j-waypoints")
        L.append(f"| {OPT[D]} | {sub} | {f4(m.get('Z_point_exact'))} | **{f4(m.get('Z_settled'))}** | {m['delta']:+.4f} ± {m['delta_se']:.4f} | "
                 f"{f3(m['share_before_resample'])} | {f3(m['share_after_point_resample'])} | {f3(m['share_after_settled_resample'])} | "
                 f"{f3(m['on_searched_after_point'])} → {f3(m['on_searched_after_settled'])} | {wp:,.0f} / {oth:,.0f} |")
L.append("")
L.append("**Table 4. By log-on cause (C1 / C2 silent), mixture, base, rho 0.05 (settling's resample only; no impact-point all-rows value exists for cause cells).**\n")
L.append("| option | cause | Z point (same outcomes) | Z settled (resample) | Δ (± SE) | on searched ground after: point → settled |")
L.append("|---|---|---|---|---|---|")
for D in OPT:
    for cell in ("C1", "C2 silent"):
        m = row_mix(D, cell, "all", "base_rho0.05")
        L.append(f"| {OPT[D]} | {cell} | {f4(m['Z_point_resample'])} | {f4(m['Z_settled_resample'])} | {m['delta']:+.4f} ± {m['delta_se']:.4f} | "
                 f"{f3(m['on_searched_after_point'])} → {f3(m['on_searched_after_settled'])} |")
L.append("")
L.append("**Table 5. Per stratum (family folder), all six options, base, rho 0.05: Z impact point → Z settled (Δ ± SE).**\n")
L.append("| option | " + " | ".join(R["per_stratum"]) + " |")
L.append("|---|" + "---|" * len(R["per_stratum"]))
for D in OPT:
    cells = []
    for st in R["per_stratum"]:
        r = R["per_stratum"][st][D]["total"]["all"]["base_rho0.05"]
        cells.append(f"{f4(r['Z_point_exact'])} → {f4(r['Z_settled'])} ({r['delta']:+.4f} ± {r['delta_se']:.4f})")
    L.append(f"| {OPT[D]} | " + " | ".join(cells) + " |")
L.append("")
# check: settling's resample reproduces the impact-point Z of all rows within Monte Carlo noise
for st in R["per_stratum"]:
    for D in OPT:
        for sub in ("all", "A1", "A2", "B"):
            r = R["per_stratum"][st][D]["total"][sub]["base_rho0.05"]
            if r["Z_point_exact"] is not None:
                checks["resample_vs_exact_point_z"].append(
                    {"stratum": st, "D": D, "family": sub, "source": r["source"],
                     "z_score": (r["Z_point_resample"] - r["Z_point_exact"]) / r["Z_point_resample_se"]})
zs = [abs(c["z_score"]) for c in checks["resample_vs_exact_point_z"]]
checks["summary"] = {"cells": len(zs), "max_abs_z": max(zs), "share_abs_z_gt_2": sum(z > 2 for z in zs) / len(zs),
                     "share_abs_z_gt_3": sum(z > 3 for z in zs) / len(zs)}
(HERE / "tables.md").write_text("\n".join(L) + "\n")
(HERE / "resample-check.json").write_text(json.dumps(checks, indent=1))
print(json.dumps(checks["summary"]))
