#!/usr/bin/env python3
"""Reduce score_supplement.py output to the B3 tables (work order overnight-2026-10-20).

    python reduce_supplement.py <exchange out> <results dir> <out.json> <tables.md>

Totals at the impact point, two normalisations: end of flight's convention (reduced-table rows outside the A1 strata x s_d from
settling's eof-convention-weights.json, plus the strata rows; A1 share = end of flight's) - the HEADLINE - and settling's single
measure (rest + strata, self-normalised). A1 = the strata. A2, B = the reduced table's rule-B rows. Run J alone = (i) this module's
a8e819f results (results/searched-areas-run-j-a1branch, all 153.6 M rows, A1 stratified) and (ii) production alone on the same
reduced table (lnw:alone; A1 unstratified). Northern masses: 95 % seed bootstrap (2,000 replicates; production replicates 1-24 and
supplement replicates 1001-1016 resampled independently; row weights held fixed; the A1 strata held fixed).
Settled: Z settled = Z point (all rows, same measure) + paired delta on settling's outcomes (outcomes of a1-stratified totals
weighted by end of flight's convention).
"""
import json, math, pathlib, sys
import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from score_supplement import CELLS, EVALS, BANDS, SETT, X, lookup, evaluate  # noqa: E402

SPLIT = ["searched", "north_of_25S", "beyond_25NM", "near_arc_unsearched"]
RNG = np.random.default_rng(20261020)


def add(a, b, k=1.0):
    out = {}
    for key, v in a.items():
        if key == "groups": continue
        if isinstance(v, dict): out[key] = add(v, b[key], k)
        else: out[key] = v + (k * k if key in ("m2", "mP2", "s2") else k) * b[key]
    return out


def scale(a, k):
    z = {kk: (scale(v, 0) if isinstance(v, dict) else 0.0) for kk, v in a.items() if kk != "groups"}
    return add(z, a, k)


def Q(t, e="base_rho0.05"):
    s = t[e]; m, mp = t["m"], s["mP"]
    if m <= 0: return None
    r = {"Z": mp / m, "mass": m, "on_searched_before": s["split_before"]["searched"] / m, "on_searched_after": s["split_after"]["searched"] / mp,
         "split_before": {c: s["split_before"][c] / m for c in SPLIT}, "split_after": {c: s["split_after"][c] / mp for c in SPLIT},
         "row_ess_before": m * m / t["m2"], "row_ess_after": mp * mp / s["mP2"], "state_ess_before": m * m / t["s2"], "state_ess_after": mp * mp / s["s2"],
         "bands": {}}
    for b in BANDS:
        tb, sb = t["bands"][b], s["bands"][b]
        r["bands"][b] = {"before": tb["m"] / m, "after": sb["mP"] / mp,
                         "row_ess_before": tb["m"] ** 2 / tb["m2"] if tb["m2"] > 0 else 0.0, "row_ess_after": sb["mP"] ** 2 / sb["mP2"] if sb["mP2"] > 0 else 0.0,
                         "state_ess_before": tb["m"] ** 2 / tb["s2"] if tb["s2"] > 0 else 0.0, "state_ess_after": sb["mP"] ** 2 / sb["s2"] if sb["s2"] > 0 else 0.0}
    return r


def boot(rest_g, k, strata, groups, B=2000):
    """rest_g: groups dict of the reduced-table part (lists over replicate ids); k: its scale; strata: fixed (m, mP, band dicts)."""
    g = np.array(groups); prod = np.where(g < 10000)[0]; sup = np.where(g >= 10000)[0]
    out = {}
    for which in ("m", "mP"):
        tot = np.array(rest_g[which]); bands = {b: np.array(v) for b, v in rest_g[f"bands_{which}"].items()}
        T = np.zeros(B); BB = {b: np.zeros(B) for b in bands}
        for i in range(B):
            c = np.zeros(len(g))
            np.add.at(c, RNG.choice(prod, len(prod)), 1.0)
            if len(sup) and tot[sup].sum() > 0: np.add.at(c, RNG.choice(sup, len(sup)), 1.0)
            T[i] = k * (c * tot).sum() + strata[which]
            for b in bands: BB[b][i] = k * (c * bands[b]).sum() + strata["bands"][b][which]
        out["after" if which == "mP" else "before"] = {b: [float(np.quantile(BB[b] / T, 0.025)), float(np.quantile(BB[b] / T, 0.975))] for b in bands}
    return out


def main(out, res, outp, tabp):
    out, res = pathlib.Path(out), pathlib.Path(res)
    RT = json.loads((out / "reduced_terms.json").read_text()); ST = json.loads((out / "strata_terms.json").read_text())["seeds"]
    SS = json.loads((out / "settled_summary.json").read_text())
    conv = json.loads((SETT / "a1-stratified/eof-convention-weights.json").read_text())
    A8 = json.loads((res / "searched-areas-run-j-a1branch/a1branch-reduced.json").read_text())
    RJS = json.loads((res / "searched-areas-run-j-settled/run-j-settled-reduced.json").read_text())["per_stratum"]["run-j-waypoints"]
    SPJ = json.loads((res / "searched-areas-spatial-detection/run-j-spatial-reduced.json").read_text())["mixture"]
    groups = RT["groups"]
    # check: this code against the published run J impact-point column on production seed 1 (all rows)
    I = np.load(X / "end-of-flight/run-j/run-j-waypoints/seed-1/impacts32.npy", mmap_mode="r")
    P, _ = evaluate(lookup(np.asarray(I[:, 7], float), np.asarray(I[:, 8], float)))
    pub = np.load(X / "searched-areas/run-j/run-j-waypoints/seed-1/seabed-lnL.npy")
    chk = {"label": RT["label"], "reduced_rows": RT["rows"], "technique_rows": RT["technique_rows"],
           "max_abs_dlnL_vs_published_run_j_seed1_all_rows": float(np.abs(np.log(P["base_rho0.05"]) - pub).max()),
           "strata_rows": {s: sum(x["check"]["rows"] for x in ST if x["check"]["src"] == s) for s in ("b1p", "b1s", "b2")},
           "b1p_max_abs_dlnL_vs_a8e819f": max(x["check"].get("max_abs_dlnL_vs_a8e819f_pass_column", 0) for x in ST),
           "arc_grid": json.loads((out / "arc-grid-check.json").read_text()), "settled": {k: v["checks"] for k, v in SS["sets"].items()}}
    R = {"checks": chk, "point": {}, "settled": {}}
    for d in CELLS:
        strata = None
        for x in ST:
            strata = x["terms"][d] if strata is None else add(strata, x["terms"][d])
        rest = RT["comb"][d]["rest"]; sd = conv[d]["outcome_weight_for_rest_rows_nonA1"]
        tot_conv = add(scale(rest, sd), strata); tot_single = add(rest, strata)
        chk.setdefault("conv_mass_sum", {})[d] = tot_conv["m"]
        e = {"s_d": sd, "A1_share_eof_convention": strata["m"] / tot_conv["m"], "A1_share_single": strata["m"] / tot_single["m"], "scen": {}}
        for ev in EVALS:
            q = {"all_eof_convention": Q(tot_conv, ev), "all_single_measure": Q(tot_single, ev), "all_unstratified": Q(RT["comb"][d]["all"], ev),
                 "A1": Q(strata, ev), "A1_unstratified": Q(RT["comb"][d]["A1"], ev), "A2": Q(RT["comb"][d]["A2"], ev), "B": Q(RT["comb"][d]["B"], ev),
                 "alone_all": Q(RT["alone"][d]["all"], ev), "alone_A1_unstratified": Q(RT["alone"][d]["A1"], ev),
                 "alone_A2": Q(RT["alone"][d]["A2"], ev), "alone_B": Q(RT["alone"][d]["B"], ev)}
            q["A1_share_after_eof_convention"] = strata[ev]["mP"] / tot_conv[ev]["mP"]
            if ev in ("base_rho0.05", "V1_central"):
                sfix = {"m": strata["m"], "mP": strata[ev]["mP"], "bands": {b: {"m": strata["bands"][b]["m"], "mP": strata[ev]["bands"][b]["mP"]} for b in BANDS}}
                q["boot_all_eof_convention"] = boot(RT["comb"][d]["rest"][ev]["groups"], sd, sfix, groups)
                zf = {"m": 0.0, "mP": 0.0, "bands": {b: {"m": 0.0, "mP": 0.0} for b in BANDS}}
                q["boot_alone_all"] = boot(RT["alone"][d]["all"][ev]["groups"], 1.0, zf, groups)
            e["scen"][ev] = q
        dd = d if d in A8["point"] else None
        if dd:
            a = A8["point"][d]["base_rho0.05"]["stratified"]
            e["run_j_alone_a8e819f"] = {f: {k: a[f][k] for k in ("Z", "on_searched_before", "on_searched_after", "row_ess_after")} for f in ("all", "A1", "A2", "B")}
        R["point"][d] = e
    # settled
    for set_, v in SS["sets"].items():
        for p in v["products"]:
            d, sub = p["D"], p["subset"]
            pt = R["point"][d]["scen"]
            for ev in EVALS:
                if set_ == "a1-stratified": zpt = pt[ev]["A1"]["Z"] if sub == "A1" else pt[ev]["all_eof_convention"]["Z"]
                elif sub == "north33": zpt = None
                elif sub == "all": zpt = pt[ev]["all_unstratified"]["Z"]
                else: zpt = pt[ev][sub]["Z"]
                s = p[ev]
                rec = {"Z_settled": (zpt + s["delta"]) if zpt is not None else s["Z_settled_resample"], "estimator": "point all rows + paired delta" if zpt is not None else "resample (conditional product)",
                       "delta": s["delta"], "delta_se": s["delta_se"], "on_searched_after": s["split_after"]["searched"], "split_after": s["split_after"],
                       "bands_after": s["bands_after"], "bands_before": s["bands_before"], "distinct_row_ess_after": s["distinct_row_ess_after"], "row_ess_before": p["row_ess_kish"]}
                R["settled"].setdefault(d, {}).setdefault(f"{set_}:{sub}", {})[ev] = rec
        # run J alone settled comparators
    for d in ("D0", "D1", "D2", "D3", "D4", "D5"):
        a = A8["settled"][d]
        R["settled"][d]["run_j_alone_a8e819f"] = {f: {"Z_settled": a[f]["scalar"]["base_rho0.05"]["Z_settled"], "on_searched_after": a[f]["scalar"]["base_rho0.05"]["on_searched_after_settled"],
                                                     "V1": a[f]["variants"]["V1_central"]["Z"], "V2": a[f]["variants"]["V2_pessimistic"]["Z"], "V3": a[f]["variants"]["V3_optimistic"]["Z"]} for f in ("all", "A1")}
        R["settled"][d]["run_j_settled_A2_B"] = {f: {"Z_settled": RJS[d]["total"][f]["base_rho0.05"]["Z_settled"], "on_searched_after": RJS[d]["total"][f]["base_rho0.05"]["on_searched_after_settled"]} for f in ("A2", "B")}
        R["settled"][d]["run_j_spatial_mixture"] = {v: {"Z": SPJ[d]["total"]["all"][v]["Z"], "after": SPJ[d]["total"]["all"][v]["after"]} for v in ("V0_scalar", "V1_central", "V2_pessimistic", "V3_optimistic")}
    pathlib.Path(outp).write_text(json.dumps(R, indent=1))
    tables(R, tabp)
    print(json.dumps({k: v for k, v in chk.items() if k not in ("arc_grid", "settled")}))


NAME = {"D0": "D0' 00:19 data held out", "D1": "D1 R600 BTO only", "D2": "D2 R600 BTO + BFO", "D3": "D3 both BFOs as recorded",
        "D4": "D4 both BFOs, Holland transient bias added", "D5": "D5 R600 + R1200 BFO, Holland transient bias added",
        "D3s": "D3, other log-on cause only", "D4s": "D4, other log-on cause only", "D5s": "D5, other log-on cause only"}
f0 = lambda x: f"{x:,.0f}"; f3 = lambda x: f"{x:.3f}"; f4 = lambda x: f"{x:.4f}"


def settled_get(R, d, key, ev="base_rho0.05"):
    return R["settled"].get(d, {}).get(key, {}).get(ev)


def tables(R, tabp):
    L = []; P = L.append
    c = R["checks"]
    P(f"Checks: reduced rule-B rows {c['reduced_rows']:,} (technique 0/1/2: {', '.join(f'{x:,}' for x in c['technique_rows'])}); strata rows " +
      ", ".join(f"{k} {v:,}" for k, v in c["strata_rows"].items()) + f"; this code against the published run J column on production seed 1 "
      f"(all 6.4 M rows) max |Δ ln L| {c['max_abs_dlnL_vs_published_run_j_seed1_all_rows']:.1e}; branch-1 production pass against the a8e819f columns "
      f"{c['b1p_max_abs_dlnL_vs_a8e819f']:.1e}; end-of-flight-convention mass sums " + ", ".join(f"{d} {v:.4f}" for d, v in c["conv_mass_sum"].items()) + ".")
    P("")
    P("**Table 1. Search factor Z and the share on searched ground, impact point, base (rho 0.05): rule B (all supplement rows) against run J alone.**")
    P("")
    P("| 00:19 treatment | Z rule B (EoF convention) | Z single measure | Z run J alone (a8e819f, all rows) | Z production alone (reduced table) | on searched ground before → after, rule B | run J alone | A1 share before → after (rule B) |")
    P("|---|---|---|---|---|---|---|---|")
    for d in CELLS:
        q = R["point"][d]["scen"]["base_rho0.05"]; a = R["point"][d].get("run_j_alone_a8e819f")
        t = q["all_eof_convention"]
        P(f"| {NAME[d]} | **{f4(t['Z'])}** | {f4(q['all_single_measure']['Z'])} | {f4(a['all']['Z']) if a else '—'} | {f4(q['alone_all']['Z'])} | "
          f"{f3(t['on_searched_before'])} → {f3(t['on_searched_after'])} | {(f3(a['all']['on_searched_before']) + ' → ' + f3(a['all']['on_searched_after'])) if a else '—'} | "
          f"{R['point'][d]['A1_share_eof_convention']:.4f} → {q['A1_share_after_eof_convention']:.4f} |")
    P("")
    P("**Table 2. By family, impact point, base: Z (row ESS after the searches). A1 from the two conditional strata; A2 and B from the rule-B rows.**")
    P("")
    P("| 00:19 treatment | A1 rule B | A1 run J alone (a8e819f) | A2 rule B | A2 production alone | B rule B | B production alone |")
    P("|---|---|---|---|---|---|---|")
    for d in CELLS:
        q = R["point"][d]["scen"]["base_rho0.05"]; a = R["point"][d].get("run_j_alone_a8e819f")
        g = lambda x: f"{f4(x['Z'])} ({f0(x['row_ess_after'])})" if x else "—"
        P(f"| {NAME[d]} | {g(q['A1'])} | {g(a['A1']) if a else '—'} | {g(q['A2'])} | {g(q['alone_A2'])} | {g(q['B'])} | {g(q['alone_B'])} |")
    P("")
    P("**Table 3. Where the remaining probability is after the searches (four-way split, impact point, all families): rule B (EoF convention) against production alone.**")
    P("")
    P("| 00:19 treatment | detection model | on searched ground | north of 25 S, unsearched | beyond 25 NM of the arc, unsearched | near the arc south of 25 S, unsearched |")
    P("|---|---|---|---|---|---|")
    for d in CELLS:
        for ev, lab in (("base_rho0.05", "base"), ("V1_central", "per-cell central"), ("V2_pessimistic", "per-cell pessimistic"), ("V3_optimistic", "per-cell optimistic")):
            q = R["point"][d]["scen"][ev]; t, a = q["all_eof_convention"]["split_after"], q["alone_all"]["split_after"]
            P(f"| {NAME[d] if ev == 'base_rho0.05' else ''} | {lab} | " + " | ".join(f"{t[s]:.4f} ({a[s]:.4f})" for s in SPLIT) + " |")
    P("")
    P("(In brackets: production alone on the same reduced table.)")
    P("")
    P("**Table 4. Northern masses after the searches (impact latitude, all families, base), with 95 % seed-bootstrap intervals: production alone → rule B.**")
    P("")
    P("| 00:19 treatment | 35-30 S | 30-25 S | 25-20 S | north of 33 S | north of 30 S |")
    P("|---|---|---|---|---|---|")
    for d in CELLS:
        q = R["point"][d]["scen"]["base_rho0.05"]; t, a = q["all_eof_convention"]["bands"], q["alone_all"]["bands"]
        bt, ba = q["boot_all_eof_convention"]["after"], q["boot_alone_all"]["after"]
        P(f"| {NAME[d]} | " + " | ".join(f"{a[b]['after']:.4f} [{ba[b][0]:.4f}, {ba[b][1]:.4f}] → **{t[b]['after']:.4f}** [{bt[b][0]:.4f}, {bt[b][1]:.4f}]" for b in BANDS) + " |")
    P("")
    P("**Table 5. Northern masses before the searches (check against end of flight's band masses), rule B.**")
    P("")
    P("| 00:19 treatment | 35-30 S | 30-25 S | 25-20 S | north of 33 S | north of 30 S |")
    P("|---|---|---|---|---|---|")
    for d in CELLS:
        t = R["point"][d]["scen"]["base_rho0.05"]["all_eof_convention"]["bands"]
        P(f"| {NAME[d]} | " + " | ".join(f"{t[b]['before']:.4f}" for b in BANDS) + " |")
    P("")
    P("**Table 6. Band ESS after the searches (impact latitude, all families, base): rows / paths (distinct hand-off rows per replicate). Production alone → rule B. Target 1,000.**")
    P("")
    P("| 00:19 treatment | 35-30 S | 30-25 S | 25-20 S | north of 33 S |")
    P("|---|---|---|---|---|")
    for d in CELLS:
        q = R["point"][d]["scen"]["base_rho0.05"]; t, a = q["all_unstratified"]["bands"], q["alone_all"]["bands"]
        cell = lambda b: f"{f0(a[b]['row_ess_after'])} / {f0(a[b]['state_ess_after'])} → **{f0(t[b]['row_ess_after'])} / {f0(t[b]['state_ess_after'])}**" + (" (below 1,000)" if t[b]["state_ess_after"] < 1000 else "")
        P(f"| {NAME[d]} | " + " | ".join(cell(b) for b in ("35-30S", "30-25S", "25-20S", "north33S")) + " |")
    P("")
    P("(Before the searches, rule B paths, for comparison with end of flight's full-set paths (rows / PATHS / states): " + "; ".join(
        f"{d} " + " / ".join(f0(R['point'][d]['scen']['base_rho0.05']['all_unstratified']['bands'][b]['state_ess_before']) for b in ("35-30S", "30-25S", "25-20S")) for d in CELLS[:6]) + ".)")
    P("")
    P("**Table 7. A1 strata, impact point, base: band ESS after the searches (rows / distinct parents) and Z.**")
    P("")
    P("| 00:19 treatment | Z(A1) | all rows / parents | 35-30 S | 30-25 S | 25-20 S |")
    P("|---|---|---|---|---|---|")
    for d in CELLS:
        a = R["point"][d]["scen"]["base_rho0.05"]["A1"]
        P(f"| {NAME[d]} | {f4(a['Z'])} | {f0(a['row_ess_after'])} / {f0(a['state_ess_after'])} | " + " | ".join(f"{f0(a['bands'][b]['row_ess_after'])} / {f0(a['bands'][b]['state_ess_after'])}" for b in ("35-30S", "30-25S", "25-20S")) + " |")
    P("")
    P("**Table 8. Settled seabed positions, base: Z settled (Δ settled − point ± SE), share on searched ground after, north of 33 S after.**")
    P("")
    P("| 00:19 treatment | all families: Z settled | on searched after | north of 33 S after | run J alone (a8e819f) Z / on searched | A1: Z settled | A1 run J alone | A2 Z settled | B Z settled |")
    P("|---|---|---|---|---|---|---|---|---|")
    for d in CELLS:
        tk = "a1-stratified:all" if d in ("D3", "D4", "D5", "D3s", "D4s", "D5s") else "ruleB-waypoints:all"
        t = settled_get(R, d, tk); a1 = settled_get(R, d, "a1-stratified:A1"); a2 = settled_get(R, d, "ruleB-waypoints:A2"); b = settled_get(R, d, "ruleB-waypoints:B")
        rj = R["settled"][d].get("run_j_alone_a8e819f")
        P(f"| {NAME[d]} | **{f4(t['Z_settled'])}** ({t['delta']:+.4f} ± {t['delta_se']:.4f}) | {f3(t['on_searched_after'])} | {t['bands_after']['north33S']:.4f} | "
          f"{(f4(rj['all']['Z_settled']) + ' / ' + f3(rj['all']['on_searched_after'])) if rj else '—'} | {f4(a1['Z_settled'])} | {f4(rj['A1']['Z_settled']) if rj else '—'} | "
          f"{f4(a2['Z_settled']) if a2 else '—'} | {f4(b['Z_settled']) if b else '—'} |")
    P("")
    P("(All families under D0'-D2: the rule-B total with A1 unstratified (A1 well sampled there); under D3-D5 and D3s-D5s: settling's totals with A1 stratified, outcomes weighted by end of flight's convention.)")
    P("")
    P("**Table 9. Per-cell detection field at the settled positions, all families: Z (on searched ground after; four-way split after under V1 central).**")
    P("")
    P("| 00:19 treatment | V0 base | V1 central | V2 pessimistic | V3 optimistic | V1 split: searched / north of 25 S / beyond 25 NM / near arc | run J spatial (mixture) V1 Z |")
    P("|---|---|---|---|---|---|---|")
    for d in CELLS:
        tk = "a1-stratified:all" if d in ("D3", "D4", "D5", "D3s", "D4s", "D5s") else "ruleB-waypoints:all"
        g = lambda ev: settled_get(R, d, tk, ev)
        z0 = g("base_rho0.05")["Z_settled"]
        zz = {ev: z0 + (g(ev)["Z_settled"] - z0) for ev in ("V1_central", "V2_pessimistic", "V3_optimistic")}
        sp = R["settled"][d].get("run_j_spatial_mixture")
        s1 = g("V1_central")["split_after"]
        P(f"| {NAME[d]} | {f4(z0)} ({f3(g('base_rho0.05')['on_searched_after'])}) | " + " | ".join(f"{f4(zz[ev])} ({f3(g(ev)['on_searched_after'])})" for ev in zz) +
          f" | {' / '.join(f'{s1[s]:.3f}' for s in SPLIT)} | {f4(sp['V1_central']['Z']) if sp else '—'} |")
    P("")
    P("**Table 10. Rho sweep and the sensitivity without Ocean Infinity, all families, impact point (EoF convention): Z and on searched ground after.**")
    P("")
    P("| 00:19 treatment | rho 0 | rho 0.05 | rho 0.25 | rho 0.5 | without Ocean Infinity (sensitivity) |")
    P("|---|---|---|---|---|---|")
    for d in CELLS:
        q = R["point"][d]["scen"]
        P(f"| {NAME[d]} | " + " | ".join(f"{f4(q[ev]['all_eof_convention']['Z'])} ({f3(q[ev]['all_eof_convention']['on_searched_after'])})" for ev in ("base_rho0", "base_rho0.05", "base_rho0.25", "base_rho0.5", "without_oi_rho0.05")) + " |")
    pathlib.Path(tabp).write_text("\n".join(L) + "\n")


if __name__ == "__main__":
    main(*sys.argv[1:5])
