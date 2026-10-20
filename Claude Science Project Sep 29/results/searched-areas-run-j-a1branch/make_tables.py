"""Tables for results/searched-areas-run-j-a1branch/README.md (work order overnight-2026-10-19 B3).

    python make_tables.py <exchange searched-areas/run-j-a1branch> > tables.md
Reads a1branch-reduced.json (this folder) and point_terms.json (exchange) for the seed-level standard errors.
"""
import json, pathlib, sys
import numpy as np

H = pathlib.Path(__file__).resolve().parent
R = json.loads((H / "a1branch-reduced.json").read_text())
PT = json.loads((pathlib.Path(sys.argv[1]) / "point_terms.json").read_text())["seeds"]
DS = ["D0", "D1", "D2", "D3", "D4", "D5"]
NAME = {"D0": "D0' 00:19 held out", "D1": "D1 R600 BTO only", "D2": "D2 R600 BTO + BFO as recorded", "D3": "D3 both BFOs as recorded",
        "D4": "D4 both BFOs, Holland transient bias added", "D5": "D5 R600 BFO + R1200 BFO, Holland transient bias added"}
f0 = lambda x: f"{x:,.0f}"
f3 = lambda x: f"{x:.3f}"
f4 = lambda x: f"{x:.4f}"
ok = lambda x: ("yes" if x >= 1000 else ("500 only" if x >= 500 else "NO"))


def seed_z(d, src, sub, scen="base_rho0.05"):
    z, w = [], []
    for s in PT:
        if s["check"]["src"] != src: continue
        t = s["terms"][d][sub]
        if t["m"] > 0: z.append(t[scen]["mP"] / t["m"]); w.append(t["m"])
    z, w = np.array(z), np.array(w); Z = (z * w).sum() / w.sum(); n = len(z)
    return Z, float(np.sqrt(np.sum((w / w.sum()) ** 2 * (z - Z) ** 2) * n / (n - 1))), n


def seed_se_A1(d):
    """Seed-level SE of Z(A1, stratified): the pass part (8 seeds) and the production part outside the branch (24 seeds), combined."""
    p = R["point"][d]["base_rho0.05"]["stratified"]["A1"]
    zb, sb, _ = seed_z(d, "pass", "pass_all")
    tot = lambda src, sub, key: sum(s["terms"][d][sub][key] if key == "m" else s["terms"][d][sub]["base_rho0.05"]["mP"] for s in PT if s["check"]["src"] == src)
    k = R["checks"]["SCALE"]; mb = k * tot("pass", "pass_all", "m"); mo = tot("prod", "strat_A1", "m")
    so = seed_z(d, "prod", "strat_A1")[1] if mo > 0 else 0.0
    fb = mb / (mb + mo)
    return float(np.sqrt((fb * sb) ** 2 + ((1 - fb) * so) ** 2)), fb


out = []
P = lambda *a: out.append(" ".join(str(x) for x in a))
c = R["checks"]
P("Checks: production rows", f0(c["rows_prod"]), "(24 seeds), pass rows", f0(c["rows_pass"]), "(8 seeds); impact-point ln L against the published run J",
  f"column: max |Δ| {c['max_abs_dlnL_vs_published_base']:.1e} (float64), {c['max_abs_dlnL_vs_published_f32_columns']:.1e} (float32 columns);",
  f"per-seed ln Z against option_table_0019 max |Δ| {c['lnZ_check_worst']:.1e}; SCALE {c['SCALE']:.6f} (settling {c['SCALE_settling']:.6f});",
  f"P_D0'(branch) {c['P_D0_branch']:.6f}. Settled point arm against the impact-point columns max |Δ ln L|",
  f"{c['settled']['point_arm_max_abs_dlnL_vs_impact_point_columns']:.1e}; {f0(c['settled']['settled_elements_scored'])} settled elements, {f0(c['settled']['outcomes'])} outcomes, 0 carried.")
P("")
P("**Table 1. The gate: A1 (cruise to fuel exhaustion, then no control) after the searches, run J against the A1-branch stratified estimate.**")
P("")
P("| 00:19 treatment | run J impact point: row ESS after (source) | stratified impact point: row ESS before / after | parents after | settled: row ESS before (settling) | settled: distinct-row ESS after | gate 500 / 1,000 |")
P("|---|---|---|---|---|---|---|")
for d in DS:
    e = R["point"][d]["base_rho0.05"]; s = e["stratified"]["A1"]; rj = e["run_j_published_waypoints"]["A1"]; st = R["settled"][d]["A1"]
    lo = min(s["row_ess_after"], s["parent_ess_after"], st["row_ess_before_settling"], st["scalar"]["base_rho0.05"]["distinct_row_ess_after"])
    src = "both-burst" if d in ("D3", "D4") else "production"
    P(f"| {NAME[d]} | {f0(rj['ess_after'])} ({src}) | {f0(s['row_ess_before'])} / **{f0(s['row_ess_after'])}** | {f0(s['parent_ess_after'])} | {f0(st['row_ess_before_settling'])} | {f0(st['scalar']['base_rho0.05']['distinct_row_ess_after'])} | {'met / met' if lo >= 1000 else ('met / NOT met' if lo >= 500 else 'NOT met')} |")
P("")
P("**Table 2. Impact point, waypoints stratum, base, rho 0.05: Z and the share on searched ground, run J against the stratified estimate.**")
P("")
P("| 00:19 treatment | family | Z run J | Z stratified (seed SE) | Z, EoF normalisation | on searched ground before → after, run J | before → after, stratified | share before → after, stratified |")
P("|---|---|---|---|---|---|---|---|")
for d in DS:
    e = R["point"][d]["base_rho0.05"]; en = e["eof_normalisation"]
    for f in ("all", "A1", "A2", "B"):
        s = e["stratified"][f]; rj = e["run_j_published_waypoints"].get(f)
        se = f" ({seed_se_A1(d)[0]:.4f})" if f == "A1" else ""
        ze = f4(en["Z_all"]) if f == "all" else "same"
        sh = "1 → 1" if f == "all" else f"{s['share_before']:.4f} → {s['share_after']:.4f} (EoF {en['shares_before'][f]:.4f} → {en['shares_after'][f]:.4f})"
        P(f"| {NAME[d] if f == 'all' else ''} | {f} | {f4(rj['Z'])} | {f4(s['Z'])}{se} | {ze} | {f3(rj['on_searched_before'])} → {f3(rj['on_searched_after'])} | {f3(s['on_searched_before'])} → {f3(s['on_searched_after'])} | {sh} |")
P("")
P("**Table 3. The two normalisations: end of flight's (production Z(d) in the denominator, A2/B rescaled) minus settling's single measure.**")
P("")
P("| 00:19 treatment | A1 share before: single measure / EoF | Δ Z (all families) | Δ on searched ground after |")
P("|---|---|---|---|")
for d in DS:
    e = R["point"][d]["base_rho0.05"]; en = e["eof_normalisation"]
    P(f"| {NAME[d]} | {e['stratified']['A1']['share_before']:.4f} / {en['shares_before']['A1']:.4f} | {en['dZ_all_vs_stratified']:+.5f} | {en['d_on_searched_after_vs_stratified']:+.4f} |")
P("")
P("**Table 4. Validation: the search factor on the branch rows, production (24 seeds, branch rows only) against the pass (8 seeds).**")
P("")
P("| 00:19 treatment | Z(branch) production (seed SE) | Z(branch) pass (seed SE) | difference / combined SE |")
P("|---|---|---|---|")
for d in DS:
    a, sa, _ = seed_z(d, "prod", "prod_branch"); b, sb, _ = seed_z(d, "pass", "pass_all")
    P(f"| {NAME[d]} | {f4(a)} ({sa:.4f}) | {f4(b)} ({sb:.4f}) | {(b - a) / np.hypot(sa, sb):+.2f} |")
P("")
P("**Table 5. Settled seabed positions (settling run-j-a1branch products), base, rho 0.05.**")
P("")
P("| 00:19 treatment | family | Z settled (Δ settled − point ± SE) | Z settled, run J | on searched ground after: point → settled | run J settled | settled outcomes N / distinct rows |")
P("|---|---|---|---|---|---|---|")
for d in DS:
    for f in ("all", "A1"):
        e = R["settled"][d][f]; s = e["scalar"]["base_rho0.05"]; rj = e["run_j_settled_published"]
        P(f"| {NAME[d] if f == 'all' else ''} | {f} | **{f4(s['Z_settled'])}** ({s['delta']:+.4f} ± {s['delta_se']:.4f}) | {f4(rj['Z_settled'])} | {f3(s['on_searched_after_point'])} → {f3(s['on_searched_after_settled'])} | {f3(rj['on_searched_after_settled'])} | {f0(e['N'])} / {f0(e['distinct_rows'])} |")
P("")
P("**Table 6. Per-cell detection field at the settled positions (V0 base, V1 central, V2 pessimistic, V3 optimistic): Z and on searched ground after.**")
P("")
P("| 00:19 treatment | family | V0 | V1 central (Δ vs V0 ± SE) | V2 | V3 | on searched after V0 / V1 / V2 / V3 | run J spatial (mixture) V1 Z / on searched after |")
P("|---|---|---|---|---|---|---|---|")
for d in DS:
    for f in ("all", "A1"):
        v = R["settled"][d][f]["variants"]; sp = R["settled"][d][f]["run_j_spatial_published_mixture"]
        P(f"| {NAME[d] if f == 'all' else ''} | {f} | {f4(v['V0_scalar']['Z'])} | {f4(v['V1_central']['Z'])} ({v['V1_central']['dZ_vs_V0']:+.4f} ± {v['V1_central']['dZ_se']:.4f}) | {f4(v['V2_pessimistic']['Z'])} | {f4(v['V3_optimistic']['Z'])} | "
          f"{' / '.join(f3(v[x]['on_searched_after']) for x in ('V0_scalar', 'V1_central', 'V2_pessimistic', 'V3_optimistic'))} | {f4(sp['V1_central']['Z'])} / {f3(sp['V1_central']['on_searched_after'])} |")
P("")
P("**Table 7. A1 under the both-frequency treatments: rho sweep and the sensitivity without Ocean Infinity (stratified).**")
P("")
P("| 00:19 treatment | case | Z impact point | row ESS after | Z settled | on searched ground after, settled |")
P("|---|---|---|---|---|---|")
for d in ("D3", "D4", "D5"):
    for scen, lab in (("base_rho0.05", "base, rho 0.05"), ("base_rho0", "base, rho 0"), ("base_rho0.25", "base, rho 0.25"), ("base_rho0.5", "base, rho 0.5"),
                      ("without_oi_rho0.05", "sensitivity: without Ocean Infinity")):
        s = R["point"][d][scen]["stratified"]["A1"]; t = R["settled"][d]["A1"]["scalar"][scen]
        P(f"| {NAME[d] if scen == 'base_rho0.05' else ''} | {lab} | {f4(s['Z'])} | {f0(s['row_ess_after'])} | {f4(t['Z_settled'])} | {f3(t['on_searched_after_settled'])} |")
P("")
P("**Table 8. The other families under the both-frequency treatments (impact point, stratified measure; unchanged rows from production).**")
P("")
P("| 00:19 treatment | A2 row ESS after | B row ESS after | all families row ESS after | run J (both-burst for D3/D4) A2 / B / all |")
P("|---|---|---|---|---|")
for d in ("D3", "D4", "D5"):
    e = R["point"][d]["base_rho0.05"]; s = e["stratified"]; rj = e["run_j_published_waypoints"]
    P(f"| {NAME[d]} | {f0(s['A2']['row_ess_after'])} | {f0(s['B']['row_ess_after'])} | {f0(s['all']['row_ess_after'])} | {f0(rj['A2']['ess_after'])} / {f0(rj['B']['ess_after'])} / {f0(rj['all']['ess_after'])} |")
print("\n".join(out))
