"""Effective sample per 5 deg latitude band on a production pass (composer request, END_OF_FLIGHT.md 17 Oct 2026 19:50Z).

    python band_ess.py EOF_ROOT CORE_ROOT TABLE_JSON OUT_JSON PART NPARTS      (then --combine OUT_PREFIX NPARTS)

Per band of impact latitude [-45,-40), ..., [-20,-15) and per treatment D0, D2, D3, D4 (competing-causes total, q = 1/3, C2 silent,
as option_table_0019): band mass share; Kish ESS over impact rows; and Kish ESS over distinct 00:11 parents (row masses summed per
parent before squaring), which is the number of independent satellite-fitted paths behind the band.
"""
import json, sys, pathlib
import numpy as np
from scipy.special import logsumexp
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from compact_impacts import load
from run_i_maps import cell_logmass
from run_j_maps_pass import STRATA, seed_list

BANDS = np.arange(-45.0, -14.0, 5.0); CELLS = ("D0", "D2", "D3", "D4")


def part(eof_root, core_root, table, outp, k, n):
    tab = json.load(open(table))["cells"]; lnz = {d: tab[f"{d} total q=0.333 (C2 silent)"]["ln_Z"] for d in CELLS}
    acc = {d: {"m": np.zeros(len(BANDS) - 1), "m2": np.zeros(len(BANDS) - 1), "p2": np.zeros(len(BANDS) - 1)} for d in CELLS}
    for st, P, K, sd in seed_list(eof_root)[k::n]:
        meta, g = load(sd)
        lm = cell_logmass(g, meta, pathlib.Path(core_root) / st / "bto-bfo" / sd.name / "handoff-m0011" / "handoff.npy")
        lat = g("latitude_deg"); par = g("parent").astype(np.int64); b = np.digitize(lat, BANDS) - 1
        ok = (b >= 0) & (b < len(BANDS) - 1); c = np.log(P / K)
        for d in CELLS:
            a = lm[d]; m = np.zeros(len(a)); fin = np.isfinite(a); m[fin] = np.exp(c + a[fin] - lnz[d]); m[~ok] = 0
            acc[d]["m"] += np.bincount(b[ok], m[ok], len(BANDS) - 1); acc[d]["m2"] += np.bincount(b[ok], m[ok] ** 2, len(BANDS) - 1)
            key = b[ok] * (par.max() + 1) + par[ok]; u, inv = np.unique(key, return_inverse=True); s = np.bincount(inv, m[ok])
            acc[d]["p2"] += np.bincount(u // (par.max() + 1), s ** 2, len(BANDS) - 1)
        print(f"part {k}: {st} {sd.name}", flush=True)
    json.dump({d: {x: v.tolist() for x, v in A.items()} for d, A in acc.items()}, open(outp, "w"))


def combine(prefix, n):
    Z = [json.load(open(f"{prefix}.part{k}.json")) for k in range(n)]; res = {"bands_lat": BANDS.tolist(), "cells": {}}
    for d in CELLS:
        m, m2, p2 = (np.sum([z[d][x] for z in Z], axis=0) for x in ("m", "m2", "p2"))
        res["cells"][d] = [{"band": f"{-BANDS[i]:.0f}-{-BANDS[i+1]:.0f} S", "mass": float(m[i]), "ess_rows": float(m[i] ** 2 / m2[i]) if m2[i] > 0 else 0.0,
                            "ess_parents": float(m[i] ** 2 / p2[i]) if p2[i] > 0 else 0.0} for i in range(len(BANDS) - 1)]
    json.dump(res, open(f"{prefix}.json", "w"), indent=1)
    for d in CELLS:
        print(d, " | ".join(f"{r['band']}: {r['mass']:.4f} {r['ess_rows']:.0f}/{r['ess_parents']:.0f}" for r in res["cells"][d]))


if __name__ == "__main__":
    if sys.argv[1] == "--combine": combine(sys.argv[2], int(sys.argv[3]))
    else: part(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], int(sys.argv[5]), int(sys.argv[6]))
