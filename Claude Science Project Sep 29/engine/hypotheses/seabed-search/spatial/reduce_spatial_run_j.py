#!/usr/bin/env python3
"""Reduce score_spatial_run_j.py summaries to mixture tables (same mixing as reduce_settled_run_j.py).

    python hypotheses/seabed-search/spatial/reduce_spatial_run_j.py <run-j-spatial dir> <settling run-j dir>
        <run-j-settled-reduced.json> <out.json>

Headline Z of a variant = published settled Z for the base (Z_point_exact + settled delta) + the paired mixture difference
(variant - V0) on the same settled outcomes, with its Monte Carlo SE. Shares before / after are resample estimates.
"""
import json, pathlib, sys
import numpy as np
STRATA = ["run-j-waypoints", "run-j-free", "run-j-descent-climb", "run-j-repro-radar"]
BB = "run-j-both-burst-waypoints"


def main():
    ex, sett, setred, outp = map(pathlib.Path, sys.argv[1:5])
    W = json.loads((sett / "stratum-mixture-weights.json").read_text())["weights_per_cell"]
    R = json.loads(setred.read_text())
    S = {st: json.loads((ex / st / "summary.json").read_text()) for st in STRATA + [BB]}
    V = list(S[STRATA[0]]["variants"])
    idx = {st: {(p["D"], p["cell"], p["subset"]): p for p in S[st]["products"]} for st in S}
    res = {"variants": S[STRATA[0]]["variants"], "checks": {st: S[st]["checks"] for st in S}, "mixture": {}}
    Ds = sorted({p["D"] for p in S[STRATA[0]]["products"]})
    for D in Ds:
        src = {st: (BB if (st == "run-j-waypoints" and D in ("D3", "D4")) else st) for st in STRATA}
        opt = idx[STRATA[0]][(D, "total", "all")]["option"]
        for cell in ("total", "C1", "C2 silent"):
            for sub in (("all", "A1", "A2", "B") if cell == "total" else ("all",)):
                w = W[f"{opt} | {cell}"]
                ps = {st: idx[src[st]][(D, cell, sub)] for st in STRATA}
                ws = {st: w[st] * (ps[st]["share_of_option"] if sub != "all" else 1.0) for st in STRATA}
                tw = sum(ws.values())
                base_pub = R["mixture"][D][cell][sub]["base_rho0.05"]
                zs = base_pub.get("Z_settled", base_pub["Z_settled_resample"])
                out = {"option": opt, "weight_total": tw, "Z_settled_published_base": zs}
                for v in V:
                    m = lambda f: sum(ws[st] * f(ps[st][v]) for st in STRATA) / tw
                    zr = m(lambda r: r["Z"]); dz = m(lambda r: r["dZ_vs_V0"])
                    se = float(np.sqrt(sum((ws[st] / tw * ps[st][v]["dZ_vs_V0_se"]) ** 2 for st in STRATA)))
                    cats = list(ps[STRATA[0]][v]["before"])
                    before = {c: m(lambda r, c=c: r["before"][c]) for c in cats}
                    den = sum(ws[st] * ps[st][v]["Z"] for st in STRATA)
                    after = {c: sum(ws[st] * ps[st][v]["Z"] * ps[st][v]["after"][c] for st in STRATA) / den for c in cats}
                    out[v] = {"Z": zs + dz, "dZ_vs_base": dz, "dZ_se": se, "Z_resample": zr, "before": before, "after": after}
                res["mixture"].setdefault(D, {}).setdefault(cell, {})[sub] = out
            if cell == "total":
                for v in V:
                    tot = res["mixture"][D]["total"]["all"]
                    for sub in ("A1", "A2", "B"):
                        f = res["mixture"][D]["total"][sub]
                        sb = f["weight_total"] / tot["weight_total"]
                        f[v]["share_before"] = sb
                        f[v]["share_after"] = sb * f[v]["Z_resample"] / tot[v]["Z_resample"]
    outp.write_text(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
