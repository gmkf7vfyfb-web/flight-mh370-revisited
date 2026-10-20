"""Reduce score_settled_run_j.py summaries to the run J settled-position tables, beside the impact-point results.

    python hypotheses/seabed-search/reduce_settled_run_j.py <exchange run-j-settled dir> <settling run-j dir>
        <impact-point run-j-reduced.json> <out.json>

Mixing strata: settling's stratum-mixture-weights.json weights_per_cell["<option> | <cell>"][stratum] (= core share x Z_s(cell),
normalised), as settling instructs. Families within a stratum: the family product with weight share_of_option. D3/D4: the
waypoints stratum is taken from the both-burst supplement (run-j-both-burst-waypoints), beside, not pooled, as the impact-point
run J tables did; its mixture weight is the production waypoints weight of the cell (0.998; settling publishes none for it).

Estimators for each product (equal-weight outcomes of settling's systematic resample):
  Z_point_resample   mean over outcomes of P(no find | impact)
  Z_settled_resample mean over outcomes of P(no find | settled field, 'mean' treatment)
  delta              paired mean of (settled - point) on the same outcomes, with its Monte Carlo SE
  Z_settled          = Z_point_exact (impact-point run J, all rows) + delta   (control variate; headline)
"""
import json
import pathlib
import sys

import numpy as np

STRATA = ["run-j-waypoints", "run-j-free", "run-j-descent-climb", "run-j-repro-radar"]
BB = "run-j-both-burst-waypoints"
SCEN = ["base_rho0.05", "base_rho0", "base_rho0.25", "base_rho0.5", "without_oi_rho0.05"]


def main():
    ex, sett, ipj, outp = map(pathlib.Path, sys.argv[1:5])
    W = json.loads((sett / "stratum-mixture-weights.json").read_text())["weights_per_cell"]
    IP = json.loads(ipj.read_text())
    S = {st: json.loads((ex / st / "summary.json").read_text()) for st in STRATA + [BB]}
    idx = {st: {(p["D"], p["cell"], p["subset"]): p for p in S[st]["products"]} for st in S}
    res = {"checks": {st: S[st]["checks"] for st in S}, "per_stratum": {}, "mixture": {}}
    Ds = sorted({p["D"] for p in S[STRATA[0]]["products"]})
    for D in Ds:
        src = {st: (BB if (st == "run-j-waypoints" and D in ("D3", "D4")) else st) for st in STRATA}
        opt = idx[STRATA[0]][(D, "total", "all")]["option"]
        for cell in ("total", "C1", "C2 silent"):
            subsets = ("all", "A1", "A2", "B") if cell == "total" else ("all",)
            w = W[f"{opt} | {cell}"]
            for sub in subsets:
                for scen in SCEN:
                    num = {}
                    for st in STRATA:
                        p = idx[src[st]][(D, cell, sub)]
                        sh = p["share_of_option"] if sub != "all" else 1.0
                        ws = w[st] * sh
                        ip = None
                        if cell == "total":
                            ipd = IP["per_stratum"][st][D][scen].get("all" if sub == "all" else sub)
                            ip = ipd["Z"] if ipd and "Z" in ipd else None
                        r = {"source": src[st], "N": p["N"], "row_ess_before": p["row_ess_kish"], "share_of_option": p["share_of_option"],
                             "carried": p["carried"],
                             "Z_point_resample": p["point"][scen]["Z"], "Z_point_resample_se": p["point"][scen]["Z_se"],
                             "Z_settled_resample": p["mean"][scen]["Z"], "Z_settled_resample_se": p["mean"][scen]["Z_se"],
                             "Z_any_resample": p["any"][scen]["Z"],
                             "delta": p["paired"][scen]["mean_minus_point"], "delta_se": p["paired"][scen]["se"],
                             "delta_any": p["paired"][scen]["any_minus_point"],
                             "Z_point_exact": ip, "Z_settled": (ip + p["paired"][scen]["mean_minus_point"]) if ip is not None else None,
                             "on_searched_before_point": p["point"]["on_searched_before"],
                             "on_searched_before_settled": p["mean"]["on_searched_before"],
                             "on_searched_after_point": p["point"][scen]["on_searched_after"],
                             "on_searched_after_settled": p["mean"][scen]["on_searched_after"],
                             "on_atsb_before_settled": p["mean"]["on_atsb_before"], "on_atsb_after_settled": p["mean"][scen]["on_atsb_after"],
                             "next_area_after_settled": p["mean"][scen]["next_area_after"],
                             "north33_after_settled": p["mean"][scen]["north33_after"],
                             "outcome_ess_after_settled": p["mean"][scen]["outcome_ess_after"],
                             "diagnostics": p["diagnostics"], "weight": ws}
                        res["per_stratum"].setdefault(st, {}).setdefault(D, {}).setdefault(cell, {}).setdefault(sub, {})[scen] = r
                        num[st] = r
                    # mixture over strata (weights core share x Z_s, times family share)
                    tw = sum(r["weight"] for r in num.values())
                    m = lambda k: sum(r["weight"] * r[k] for r in num.values()) / tw
                    zP, zS = m("Z_point_resample"), m("Z_settled_resample")
                    after = lambda k, z: sum(r["weight"] * r[z] * r[k] for r in num.values()) / sum(r["weight"] * r[z] for r in num.values())
                    mix = {"weight_total": tw, "Z_point_resample": zP, "Z_settled_resample": zS, "Z_any_resample": m("Z_any_resample"),
                           "delta": m("delta"), "delta_se": float(np.sqrt(sum((r["weight"] / tw * r["delta_se"]) ** 2 for r in num.values()))),
                           "delta_any": m("delta_any"),
                           "on_searched_before_point": m("on_searched_before_point"), "on_searched_before_settled": m("on_searched_before_settled"),
                           "on_searched_after_point": after("on_searched_after_point", "Z_point_resample"),
                           "on_searched_after_settled": after("on_searched_after_settled", "Z_settled_resample"),
                           "on_atsb_before_settled": m("on_atsb_before_settled"),
                           "on_atsb_after_settled": after("on_atsb_after_settled", "Z_settled_resample"),
                           "next_area_after_settled": after("next_area_after_settled", "Z_settled_resample"),
                           "north33_after_settled": after("north33_after_settled", "Z_settled_resample"),
                           "share_point_off_field_on": sum(r["weight"] * r["diagnostics"]["share_point_off_field_on"] for r in num.values()) / tw,
                           "carried": sum(r["carried"] for r in num.values()), "N": sum(r["N"] for r in num.values())}
                    if cell == "total":
                        ipm = IP["mixture"][D][scen].get(sub)
                        if ipm and "Z" in ipm:
                            mix["Z_point_exact"] = ipm["Z"]
                            mix["Z_settled"] = ipm["Z"] + mix["delta"]
                            mix["on_searched_before_point_exact"] = ipm["on_searched_before"]
                            mix["on_searched_after_point_exact"] = ipm["on_searched_after"]
                            if sub != "all":
                                mix["share_before_exact"] = ipm.get("share_before")
                                mix["share_after_point_exact"] = ipm.get("share_after")
                    res["mixture"].setdefault(D, {}).setdefault(cell, {}).setdefault(sub, {})[scen] = mix
                # family shares after, settled, within the mixture
            if cell == "total":
                for scen in SCEN:
                    tot = res["mixture"][D]["total"]["all"][scen]
                    for sub in ("A1", "A2", "B"):
                        f = res["mixture"][D]["total"][sub][scen]
                        f["share_before_resample"] = f["weight_total"] / tot["weight_total"]
                        f["share_after_settled_resample"] = f["share_before_resample"] * f["Z_settled_resample"] / tot["Z_settled_resample"]
                        f["share_after_point_resample"] = f["share_before_resample"] * f["Z_point_resample"] / tot["Z_point_resample"]
    outp.write_text(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
