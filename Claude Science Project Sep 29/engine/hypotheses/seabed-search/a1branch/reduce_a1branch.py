#!/usr/bin/env python3
"""Reduce score_a1branch.py output to the B3 tables (work order overnight-2026-10-19).

    python reduce_a1branch.py <out dir> <results dir 'Claude Science Project Sep 29/results'> <out.json>

Impact point (all rows): stratified measure (settling's single measure) = production rows outside the branch + pass rows x SCALE.
End of flight's normalisation (a1_branch_combine.py) is computed beside it: A1 share = SCALE S_pass(d) / M_prod(d) + production A1
outside the branch / M_prod(d), with A2 / B / other rescaled by (1 - A1_new) / (1 - A1_prod); Z_total = sum of share x Z(family).
Z(A1) is identical under both (the A1 composition does not depend on the denominator). Production alone is reduced too, and must
reproduce the published run J waypoints values (results/searched-areas-run-j/run-j-reduced.json) for D0, D1, D2, D5 exactly.
Settled: Z_settled = Z_point(all rows, same measure and subset) + paired delta on settling's outcomes (run J settled recipe);
per-cell variants Z_V = Z_settled(V0) + paired (V - V0) (run J spatial recipe).
"""
import json, math, pathlib, sys
import numpy as np

DS = ["D0", "D1", "D2", "D3", "D4", "D5"]
SCEN = ["base_rho0.05", "base_rho0", "base_rho0.25", "base_rho0.5", "without_oi_rho0.05"]
VAR = ["V0_scalar", "V0_scalar_500m", "V1_central", "V1_rho0", "V1_rho0.25", "V1_rho0.5", "V1_rho_flat", "V1_lpd_terrain", "V1_oi_uniform",
       "V1_without_oi", "V2_pessimistic", "V3_optimistic"]


def add(a, b, k=1.0):
    """a + k*b for term dicts; squared terms scale with k**2."""
    out = {}
    for key in a:
        if isinstance(a[key], dict): out[key] = add(a[key], b[key], k)
        else: out[key] = a[key] + (k * k if key.endswith("2") else k) * b[key]
    return out


def zero_like(a):
    return {k: (zero_like(v) if isinstance(v, dict) else 0.0) for k, v in a.items()}


def q(t, scen):
    m = t["m"]; s = t[scen]; mp = s["mP"]
    r = {"Z": mp / m, "mass": m, "on_searched_before": t["on_union"] / m, "on_searched_after": s["on_union"] / mp,
         "on_atsb_before": t["on_atsb"] / m, "on_atsb_after": s["on_atsb"] / mp, "north33_before": t["north33"] / m, "north33_after": s["north33"] / mp,
         "row_ess_before": m * m / t["m2"], "row_ess_after": mp * mp / s["mP2"], "parent_ess_before": m * m / t["m_par2"]}
    if "mP_par2" in s: r["parent_ess_after"] = mp * mp / s["mP_par2"]
    return r


def main(out, res, outp):
    out, res = pathlib.Path(out), pathlib.Path(res)
    PT = json.loads((out / "point_terms.json").read_text())
    seeds = PT["seeds"]
    chk = {"label": PT["label"], "n_prod_seeds": sum(s["check"]["src"] == "prod" for s in seeds), "n_pass_seeds": sum(s["check"]["src"] == "pass" for s in seeds),
           "rows_prod": sum(s["check"]["rows"] for s in seeds if s["check"]["src"] == "prod"),
           "rows_pass": sum(s["check"]["rows"] for s in seeds if s["check"]["src"] == "pass"),
           "lnZ_check_worst": max(s["check"]["lnZ_check_worst"] for s in seeds),
           "max_abs_dlnL_vs_published_base": max(s["check"].get("max_abs_dlnL_vs_published_base_rho0.05", 0) for s in seeds),
           "max_abs_dlnL_vs_published_f32_columns": max(max(v for k, v in s["check"].items() if k.startswith("max_abs_dlnL_vs_published_") and "base_rho0.05" not in k)
                                                       for s in seeds if s["check"]["src"] == "prod")}
    def tot(src, d, sub, which=None):
        S = [s for s in seeds if s["check"]["src"] == src and (which is None or s["check"]["seed"] in which)]
        acc = zero_like(S[0]["terms"][d][sub])
        for s in S: acc = add(acc, s["terms"][d][sub])
        return acc
    k = tot("prod", "D0", "prod_branch")["m"] / tot("pass", "D0", "pass_all")["m"]
    p0 = json.loads((pathlib.Path("/Users/pete/Downloads/mh370-exchange/settling/run-j-a1branch/run-j-waypoints") / "rja1_pass0.json").read_text())
    chk["SCALE"] = k; chk["SCALE_settling"] = p0["SCALE"]; chk["SCALE_rel_diff"] = k / p0["SCALE"] - 1
    chk["P_D0_branch"] = tot("prod", "D0", "prod_branch")["m"] / tot("prod", "D0", "prod_all")["m"]
    halves = ([f"seed-{i}" for i in range(1, 5)], [f"seed-{i}" for i in range(5, 9)])
    R = {"checks": chk, "point": {}, "settled": {}}
    runj = json.loads((res / "searched-areas-run-j/run-j-reduced.json").read_text())["per_stratum"]["run-j-waypoints"]
    for d in DS:
        P = {}
        strat = {sub: add(tot("prod", d, f"strat_{sub}"), tot("pass", d, "pass_all"), k) for sub in ("all", "A1")}
        fam = {"A1": strat["A1"], "A2": tot("prod", d, "A2"), "B": tot("prod", d, "B"), "other": tot("prod", d, "other")}
        prod = {"all": tot("prod", d, "prod_all"), "A1": tot("prod", d, "prod_A1")}
        for scen in SCEN:
            e = {"stratified": {}, "production": {}, "eof_normalisation": {}}
            for sub in ("all",): e["stratified"][sub] = q(strat[sub], scen)
            for f, t in fam.items():
                if t["m"] > 0: e["stratified"][f] = q(t, scen)
            for sub, t in prod.items(): e["production"][sub] = q(t, scen)
            for f in ("A2", "B"): e["production"][f] = dict(e["stratified"][f])
            mall = strat["all"]["m"]
            for f in ("A1", "A2", "B"):
                e["stratified"][f]["share_before"] = fam[f]["m"] / mall
                e["stratified"][f]["share_after"] = fam[f][scen]["mP"] / strat["all"][scen]["mP"]
                e["production"][f]["share_before_production"] = (prod["A1"]["m"] if f == "A1" else fam[f]["m"]) / prod["all"]["m"]
                e["production"][f]["share_after_production"] = (prod["A1"] if f == "A1" else fam[f])[scen]["mP"] / prod["all"][scen]["mP"]
            # end of flight's normalisation
            Mp = prod["all"]["m"]; a1p = prod["A1"]["m"] / Mp; a1n = strat["A1"]["m"] / Mp; sc = (1 - a1n) / (1 - a1p)
            sh = {"A1": a1n, "A2": fam["A2"]["m"] / Mp * sc, "B": fam["B"]["m"] / Mp * sc, "other": fam["other"]["m"] / Mp * sc}
            Zf = {f: (fam[f][scen]["mP"] / fam[f]["m"] if fam[f]["m"] > 0 else 0.0) for f in sh}
            Zt = sum(sh[f] * Zf[f] for f in sh)
            onb = sum(sh[f] * fam[f]["on_union"] / fam[f]["m"] for f in sh if fam[f]["m"] > 0)
            ona = sum(sh[f] * fam[f][scen]["on_union"] / fam[f]["m"] for f in sh if fam[f]["m"] > 0) / Zt
            e["eof_normalisation"] = {"shares_before": sh, "Z_all": Zt, "on_searched_before": onb, "on_searched_after": ona,
                                      "shares_after": {f: sh[f] * Zf[f] / Zt for f in sh},
                                      "dZ_all_vs_stratified": Zt - e["stratified"]["all"]["Z"],
                                      "d_on_searched_after_vs_stratified": ona - e["stratified"]["all"]["on_searched_after"]}
            if scen == "base_rho0.05":
                hz = []
                for h in halves:
                    kh = tot("prod", "D0", "prod_branch")["m"] / tot("pass", "D0", "pass_all", h)["m"]
                    sa1 = add(tot("prod", d, "strat_A1"), tot("pass", d, "pass_all", h), kh)
                    sal = add(tot("prod", d, "strat_all"), tot("pass", d, "pass_all", h), kh)
                    hz.append({"Z_A1": sa1[scen]["mP"] / sa1["m"], "Z_all": sal[scen]["mP"] / sal["m"], "A1_share_before": sa1["m"] / sal["m"],
                               "A1_row_ess_after": sa1[scen]["mP"] ** 2 / sa1[scen]["mP2"]})
                e["pass_seed_halves"] = hz
            # run J published, waypoints stratum (D3/D4 there: both-burst supplement)
            rj = runj[d][scen]
            e["run_j_published_waypoints"] = {f: {x: rj[f].get(x) for x in ("Z", "on_searched_before", "on_searched_after", "ess_before", "ess_after")}
                                              for f in ("all", "A1", "A2", "B") if rj.get(f)}
            e["run_j_source"] = "run-j-both-burst/run-j-waypoints (8 thinned seeds)" if d in ("D3", "D4") else "run-j/run-j-waypoints (24 seeds)"
            if d not in ("D3", "D4"):
                e["production_reproduces_run_j"] = {f: abs(e["production"][f]["Z"] - rj[f]["Z"]) for f in ("all", "A1")}
            P[scen] = e
        R["point"][d] = P
    # ---------- settled
    SS = json.loads((out / "settled_summary.json").read_text())
    R["checks"]["settled"] = SS["checks"]
    rs = json.loads((res / "searched-areas-run-j-settled/run-j-settled-reduced.json").read_text())["per_stratum"]["run-j-waypoints"]
    sp = json.loads((res / "searched-areas-spatial-detection/run-j-spatial-reduced.json").read_text())["mixture"]
    for p in SS["products"]:
        d, sub = p["D"], p["subset"]; sub_pt = "all" if sub == "all" else "A1"
        e = {"N": p["N"], "row_ess_before_settling": p["row_ess_kish"], "share_of_option": p["share_of_option"], "distinct_rows": p["distinct_rows"],
             "pass_share_of_outcomes": p["pass_share_of_outcomes"], "scalar": {}, "variants": {}}
        for scen in SCEN:
            zpt = R["point"][d][scen]["stratified"][sub_pt]["Z"]; s = p["scalar_vs_point"][scen]
            e["scalar"][scen] = {"Z_point_all_rows": zpt, "Z_settled": zpt + s["d"], "delta": s["d"], "delta_se": s["d_se"], "Z_settled_resample": s["Z"],
                                 "Z_point_resample": p["point"][scen]["Z"], "on_searched_before_point": p["point"]["on_searched_before"],
                                 "on_searched_before_settled": s["on_searched_before"], "on_searched_after_point": p["point"][scen]["on_searched_after"],
                                 "on_searched_after_settled": s["on_searched_after"], "north33_after_settled": s["north33_after"],
                                 "outcome_ess_after": s["outcome_ess_after"], "distinct_row_ess_after": s["distinct_row_ess_after"]}
        z0 = e["scalar"]["base_rho0.05"]["Z_settled"]
        for v in VAR:
            s = p["variants_vs_V0"][v]
            e["variants"][v] = {"Z": z0 + s["d"], "dZ_vs_V0": s["d"], "dZ_se": s["d_se"], "on_searched_before": s["on_searched_before"],
                                "on_searched_after": s["on_searched_after"], "distinct_row_ess_after": s["distinct_row_ess_after"]}
        rj = rs[d]["total"][sub_pt]["base_rho0.05"]
        e["run_j_settled_published"] = {"source": rj.get("source"), "Z_settled": rj["Z_settled"], "on_searched_after_settled": rj["on_searched_after_settled"],
                                        "row_ess_before": rj.get("row_ess_before"), "outcome_ess_after": rj.get("outcome_ess_after_settled")}
        e["run_j_spatial_published_mixture"] = {v: {"Z": sp[d]["total"][sub_pt][v]["Z"], "on_searched_after": sp[d]["total"][sub_pt][v]["after"]["searched"]}
                                                for v in ("V0_scalar", "V1_central", "V2_pessimistic", "V3_optimistic")}
        R["settled"].setdefault(d, {})[sub] = e
    pathlib.Path(outp).write_text(json.dumps(R, indent=1))
    print(json.dumps(R["checks"], indent=1)[:3000])


if __name__ == "__main__":
    main(*sys.argv[1:4])
