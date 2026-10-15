"""Combine the per-stratum 00:19 tables of a run into the stratum mixture, when the per-seed files are gone.
Exact: total ln Z is the logsumexp of the per-stratum ln Z (each already carries its ln P - ln K), the second
moment of each stratum is recovered as 2 lnZ_s - ln(effective impacts)_s, and the latitude histogram is the
per-stratum normalised histogram weighted by exp(lnZ_s).
The per-stratum tables are CONDITIONAL (produced with stratum=1.0), so the stratum prior is applied here.
Usage: python combine_strata_0019.py SUMMARY_DIR OUT_JSON stratum=P [...]"""
import sys, json, pathlib, glob
import numpy as np
from scipy.special import logsumexp


def main(sdir, outp, W):
    files = sorted(glob.glob(str(pathlib.Path(sdir) / "table-0019-next-i-*.json")))
    tabs = {pathlib.Path(f).stem.replace("table-0019-", ""): json.load(open(f)) for f in files}
    tabs = {st: t for st, t in tabs.items() if st in W}
    assert set(tabs) == set(W), (sorted(tabs), sorted(W))
    lnP = {st: float(np.log(W[st])) for st in W}
    hists = {}
    for st in tabs:
        p = pathlib.Path(sdir) / f"table-0019-{st}-latitude.npz"
        if p.exists():
            hists[st] = np.load(p)
    cells = sorted(set().union(*[set(t["cells"]) for t in tabs.values()]))
    res = {"W_s": next(iter(tabs.values()))["W_s"], "D": next(iter(tabs.values()))["D"],
           "strata": list(tabs), "cells": {}}
    lat = None
    for c in cells:
        lz = [lnP[st] + t["cells"][c]["ln_Z"] for st, t in tabs.items() if c in t["cells"]]
        l2 = [2 * (lnP[st] + t["cells"][c]["ln_Z"]) - np.log(t["cells"][c]["eff_impacts"]) for st, t in tabs.items()
              if c in t["cells"] and t["cells"][c]["eff_impacts"] > 0]
        Z = float(logsumexp(lz)); S2 = float(logsumexp(l2))
        fam = {}
        for n in ("A1", "A2", "B"):
            f1 = [lnP[st] + t["cells"][c]["ln_Z"] + np.log(max(t["cells"][c]["families"][n]["share"], 1e-300)) for st, t in tabs.items() if c in t["cells"]]
            f2 = [2 * (lnP[st] + t["cells"][c]["ln_Z"] + np.log(max(t["cells"][c]["families"][n]["share"], 1e-300)))
                  - np.log(t["cells"][c]["families"][n]["eff_impacts"]) for st, t in tabs.items()
                  if c in t["cells"] and t["cells"][c]["families"][n]["eff_impacts"] > 0]
            F1 = float(logsumexp(f1))
            fam[n] = {"share": float(np.exp(F1 - Z)),
                      "eff_impacts": float(np.exp(2 * F1 - logsumexp(f2))) if f2 else 0.0}
        q = None
        key = c.replace(" ", "_").replace("=", "").replace("(", "").replace(")", "").replace("/", "_")
        if hists:
            h = None
            for st, z in hists.items():
                if key in z.files and c in tabs[st]["cells"]:
                    v = z[key] * np.exp(lnP[st] + tabs[st]["cells"][c]["ln_Z"] - Z)
                    h = v if h is None else h + v
                    lat = z["lat"]
            if h is not None and h.sum() > 0:
                hc = np.cumsum(h); hc /= hc[-1]
                q = [float(lat[np.searchsorted(hc, x)]) for x in (0.05, 0.5, 0.95)]
        res["cells"][c] = {"ln_Z": Z, "eff_impacts": float(np.exp(2 * Z - S2)), "families": fam,
                           "latitude_q05_q50_q95": q,
                           "per_stratum_ln_Z": {st: t["cells"][c]["ln_Z"] for st, t in tabs.items() if c in t["cells"]},
                           "stratum_prior": W}
    Z = lambda k: res["cells"][k]["ln_Z"]
    try:
        res["bayes_factors"] = {"C1:C2 within D (C2 silent)": {d: Z(f"{d}xC1") - Z(f"{d}xC2 silent") for d in res["D"]}}
    except KeyError:
        pass
    json.dump(res, open(outp, "w"), indent=1)
    for c, v in res["cells"].items():
        print(f"{c:34s} lnZ {v['ln_Z']:9.3f} ESS {v['eff_impacts']:11.0f} lat {v['latitude_q05_q50_q95']}")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], {a.split("=")[0]: float(a.split("=")[1]) for a in sys.argv[3:]})
