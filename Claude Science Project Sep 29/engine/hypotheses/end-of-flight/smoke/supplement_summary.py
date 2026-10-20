"""Run J northern supplement, end of flight: tables from the per-seed parts of supplement_combine.py (overnight order A).

    python supplement_summary.py PARTS_DIR OUT_JSON [EXTRA_PARTS_DIR]

PARTS_DIR holds prod-<k>.npz (run J production, 24 seeds) and supp-<s>.npz (supplement seeds). Per 00:19 treatment
(two-factor total, q = 1/3, C2 silent): ln Z; band masses (impact latitude and 00:11 latitude, 5 deg bands); family shares;
Kish ESS per band over rows, parents and distinct 00:11 states, production alone and combined by rule B; weighted latitude
quantiles; northern masses with a seed bootstrap (2,000 draws; production seeds and supplement seeds resampled separately,
with replacement). EXTRA_PARTS_DIR (optional) holds xd-<s>.npz from an extra-descents pass on the same supplement parents,
which replace the supp parts for D2-D5 by the descent-count-weighted pool (see the results note).
"""
import json, pathlib, sys
import numpy as np

CELLS = ("D0", "D1", "D2", "D3", "D4", "D5", "D3s", "D4s", "D5s")
FINE = np.round(np.arange(-45.0, -14.95, 0.1), 2); BANDS = np.arange(-45.0, -14.0, 5.0); NB = len(BANDS) - 1
FAMS = ("A1", "A2", "B", "other")
BAND_NAMES = [f"{-BANDS[i]:.0f}-{-BANDS[i+1]:.0f} S" for i in range(NB)]
B_OF_FINE = np.digitize(FINE[:-1] + 0.05, BANDS) - 1


def loadp(p):
    z = np.load(p); return {k: z[k] for k in z.files}


def tot(parts, key):
    return sum(p[key] for p in parts)


def quant(h, qs):
    c = np.cumsum(h); c = c / c[-1]; return [float(FINE[min(np.searchsorted(c, q), len(FINE) - 2)] + 0.05) for q in qs]


def summarise(groups, d):
    """groups: list of (parts, weighting). Returns per-treatment dict."""
    P = [(p, v) for parts, v in groups for p in parts]
    out = {}
    for name in ("imp", "h11"):
        m = sum(p[f"{v}/{d}/{name}/m"] for p, v in P); m2 = sum(p[f"{v}/{d}/{name}/m2"] for p, v in P)
        Z = m.sum(); bm = np.stack([np.bincount(B_OF_FINE, m[j], NB) for j in range(4)]); bm2 = np.stack([np.bincount(B_OF_FINE, m2[j], NB) for j in range(4)])
        rows = []
        for i in range(NB):
            r = {"band": BAND_NAMES[i], "mass": float(bm[:, i].sum() / Z)}
            for j, f in (("all", None), ("A1", 0), ("A2", 1), ("B", 2)):
                s = bm[:, i].sum() if f is None else bm[f, i]; s2 = bm2[:, i].sum() if f is None else bm2[f, i]
                par2 = sum(p[f"{v}/{d}/{name}/par2/{j}"][i] for p, v in P); st2 = sum(p[f"{v}/{d}/{name}/st2/{j}"][i] for p, v in P)
                r[j] = {"rows": float(s * s / s2) if s2 > 0 else 0.0, "parents": float(s * s / par2) if par2 > 0 else 0.0,
                        "states": float(s * s / st2) if st2 > 0 else 0.0, "share_in_band": float(s / bm[:, i].sum()) if bm[:, i].sum() > 0 else 0.0}
            rows.append(r)
        out[name] = {"bands": rows, "lnZ": float(np.log(Z)), "families": {f: float(m[j].sum() / Z) for j, f in enumerate(FAMS)},
                     "q05_q50_q95": quant(m.sum(0), (0.05, 0.5, 0.95)), "ess_rows_all": float(Z * Z / m2.sum()),
                     "pdf_per_deg": (m.sum(0) / Z / 0.1).tolist()}
    return out


def boot(prod, supp, d, comb, nboot=2000, seed=19):
    """seed bootstrap of impact-band masses, north of 33 S and north of 30 S (impact latitude)."""
    rng = np.random.default_rng(seed)
    v = "comb" if comb else "alone"
    hp = np.stack([p[f"{v}/{d}/imp/m"].sum(0) for p in prod]); hs = np.stack([p[f"comb/{d}/imp/m"].sum(0) for p in supp]) if comb else None
    n33 = FINE[:-1] >= -33.0 - 1e-9; n30 = FINE[:-1] >= -30.0 - 1e-9
    res = []
    for _ in range(nboot):
        h = hp[rng.integers(0, len(hp), len(hp))].sum(0)
        if comb: h = h + hs[rng.integers(0, len(hs), len(hs))].sum(0)
        Z = h.sum(); bm = np.bincount(B_OF_FINE, h, NB) / Z
        res.append(np.concatenate([bm, [h[n33].sum() / Z, h[n30].sum() / Z]]))
    res = np.array(res); names = BAND_NAMES + ["north of 33 S", "north of 30 S"]
    return {n: {"q025": float(np.quantile(res[:, i], 0.025)), "q975": float(np.quantile(res[:, i], 0.975)), "sd": float(res[:, i].std(ddof=1))} for i, n in enumerate(names)}


def point_north(groups, d):
    h = sum(p[f"{v}/{d}/imp/m"].sum(0) for parts, v in groups for p in parts); Z = h.sum()
    return {"north of 33 S": float(h[FINE[:-1] >= -33.0 - 1e-9].sum() / Z), "north of 30 S": float(h[FINE[:-1] >= -30.0 - 1e-9].sum() / Z)}


def main(pdir, outp, xdir=None):
    pdir = pathlib.Path(pdir)
    prod = [loadp(p) for p in sorted(pdir.glob("prod-*.npz"))]; supp = [loadp(p) for p in sorted(pdir.glob("supp-*.npz"))]
    res = {"n_prod_seeds": len(prod), "n_supp_seeds": len(supp), "bands": BAND_NAMES, "fine_lat": FINE.tolist(), "cells": {}}
    for d in CELLS:
        A = summarise([(prod, "alone")], d); C = summarise([(prod, "comb"), (supp, "comb")], d); S = summarise([(supp, "comb")], d)
        res["cells"][d] = {"alone": A, "comb": C, "supp_part_only": S,
                           "north_alone": point_north([(prod, "alone")], d), "north_comb": point_north([(prod, "comb"), (supp, "comb")], d),
                           "boot_alone": boot(prod, None, d, False), "boot_comb": boot(prod, supp, d, True)}
        print(d, "lnZ alone/comb %.3f %.3f" % (A["imp"]["lnZ"], C["imp"]["lnZ"]), "q50 %.2f %.2f" % (A["imp"]["q05_q50_q95"][1], C["imp"]["q05_q50_q95"][1]), flush=True)
    json.dump(res, open(outp, "w"), indent=1)


if __name__ == "__main__":
    main(*sys.argv[1:])
