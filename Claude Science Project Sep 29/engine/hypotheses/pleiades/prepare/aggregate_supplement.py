"""Pool score_supplement.py parts: the run J northern supplement under H (order B2, 20 Oct 2026). Waypoints stratum only.

Per treatment d (D0'-D5 q = 1/3 totals; D3s-D5s 'other cause only') and setting (none, headline gcrel-0.25, GLORYS12-only g12-0.25),
for rule B ('comb', production + all supplement rows) and production alone ('alone'): ln Z, ESS (rows; per 5-deg impact band rows /
paths / distinct 00:11 states), family shares and band ESS, mean position, latitude PDF (0.1 deg), band masses, and the module's
tension (rerun_reference.tension) on the flight-only 0.05 deg map. Pooling = sums of end of flight's part accumulators (as its
supplement_summary / supplement_a1_outside).
A1 by end of flight's two conditional strata (supplement_a1_outside.py), with the H factor on every row:
    Z_H(d, A1) = Z(D0') [ P_D0'(b1) E_D0'[L_d L_H | b1] + P_D0'(b2) E_D0'[L_d L_H 1_A1 | b2] ]
P from the main rule-B set (flight only), E from the passes (b1 rule B, b2 production alone). Share: end of flight's form
Z_H(d, A1) / Z_H(d) (main set total) and, primary as on 19 Oct, the replacement form (main set with its own b1 and b2-A1 rows replaced).
Conditional on H; no identity likelihood; no Bayes factor or P(H | data).

    python aggregate_supplement.py WORKDIR OUT_JSON
"""
import json
import math
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import branch_eof289 as b  # noqa: E402
from rerun_reference import tension  # noqa: E402
from headline_splithalf import rho_L  # noqa: E402

SURF = Path("/Users/pete/Downloads/mh370-exchange/pleiades/run-j/surfaces")
CELLS = ("D0", "D1", "D2", "D3", "D4", "D5", "D3s", "D4s", "D5s")
SETTINGS = ("none", "gcrel-0.25", "g12-0.25")
GRIDL = {"gcrel-0.25": (0.25, "mean", "-gcrel"), "g12-0.25": (0.25, 0, "")}
FINE = np.round(np.arange(-45.0, -14.95, 0.1), 2); BANDS = np.arange(-45.0, -14.0, 5.0); NB = len(BANDS) - 1
B_OF_FINE = np.digitize(FINE[:-1] + 0.05, BANDS) - 1
NAMES = [f"{-BANDS[i]:.0f}-{-BANDS[i+1]:.0f} S" for i in range(NB)]
FAM = ("A1", "A2", "B", "other")
NLAT, NLON = 800, 740


def ess(a, b2):
    return float(a * a / b2) if b2 > 0 else 0.0


class Parts:
    def __init__(self, files, v):
        self.z = [np.load(f) for f in files]; self.v = v

    def s(self, key, s, d):
        return sum(z[f"{s}|{self.v}/{d}/{key}"].astype(np.float64) for z in self.z)


def summarise(P, s, d, Lg, area, glat, glon, mapP=None):
    m = P.s("imp/m", s, d); m2 = P.s("imp/m2", s, d); Z = m.sum()
    bm = np.stack([np.bincount(B_OF_FINE, m[q], NB) for q in range(4)]); bm2 = np.stack([np.bincount(B_OF_FINE, m2[q], NB) for q in range(4)])
    out = {"lnZ": math.log(Z), "ess_rows": ess(Z, m2.sum()), "families": {}, "bands": []}
    for q, nm in enumerate(FAM):
        out["families"][nm] = {"share": float(m[q].sum() / Z), "ess_rows": ess(m[q].sum(), m2[q].sum())}
    p2 = {q: P.s(f"imp/par2/{q}", s, d) for q in ("all", "A1", "A2", "B")}; s2 = {q: P.s(f"imp/st2/{q}", s, d) for q in ("all", "A1", "A2", "B")}
    for i in range(NB):
        tot = bm[:, i].sum(); tot2 = bm2[:, i].sum()
        e = {"band": NAMES[i], "mass": float(tot / Z), "ess_rows": ess(tot, tot2), "ess_paths": ess(tot, p2["all"][i]), "ess_states": ess(tot, s2["all"][i])}
        for q, nm in enumerate(FAM[:3]):
            e[nm] = {"mass": float(bm[q, i] / Z), "ess_rows": ess(bm[q, i], bm2[q, i]), "ess_paths": ess(bm[q, i], p2[nm][i]), "ess_states": ess(bm[q, i], s2[nm][i])}
        out["bands"].append(e)
    pdf = m.sum(0) / Z; c = np.cumsum(pdf)
    out["q05_q50_q95"] = [float(FINE[np.searchsorted(c, q)]) for q in (0.05, 0.5, 0.95)]
    out["pdf_per_deg"] = (pdf / 0.1).tolist()
    for lim in (-35.0, -33.0, -30.0):
        out[f"mass_north_of_{-lim:.0f}S"] = float(pdf[FINE[:-1] >= lim].sum())
    pos = P.s("pos", s, d); out["mean_lat"], out["mean_lon"] = float(pos[1] / pos[0]), float(pos[2] / pos[0])
    if mapP is not None and s == "none":
        mp = mapP.s("map", "none", d).reshape(NLAT, NLON); pc = mp / mp.sum(); out["tension"] = {}
        for stg, Lk in Lg.items():
            t = tension(pc, Lk, area, glat, glon, *(np.zeros_like(area, bool),) * 3)
            out["tension"][stg] = {k: float(t[k]) for k in ("ln_S", "tension_p", "d_shared", "mean_shift_nm", "uncond_in_cond_hdr90",
                                                             "cond_in_uncond_hdr90", "cond_hdr90_km2", "uncond_hdr90_km2")}
    return out


def a1_strata(M, B1, B2, s, d):
    """End of flight's stratified A1 with the H factor (setting s); both share forms; ESS (rows overall and per band)."""
    Z0 = M.s("imp/m", "none", "D0").sum()
    P1 = M.s("imp/br1", "none", "D0").sum() / Z0; P2 = M.s("imp/br2", "none", "D0").sum() / Z0
    b10 = B1.s("imp/m", "none", "D0").sum(); b20 = B2.s("imp/m", "none", "D0").sum()
    a1 = Z0 * P1 / b10; a2 = Z0 * P2 / b20
    m1 = B1.s("imp/m", s, d).sum(0); m1q = B1.s("imp/m2", s, d).sum(0)            # branch 1: all rows of the pass
    m2 = B2.s("imp/m", s, d)[0]; m2q = B2.s("imp/m2", s, d)[0]                      # branch 2: A1 rows of the pass
    z1, z2 = a1 * m1.sum(), a2 * m2.sum()
    Mm = M.s("imp/m", s, d); Mm2 = M.s("imp/m2", s, d); Zd = Mm.sum(); A1m = Mm[0].sum(); A1m2 = Mm2[0].sum()
    br1, br2A1 = M.s("imp/br1", s, d).sum(), M.s("imp/br2A1", s, d).sum()
    br1A1, br1m2, br2A1m2 = M.s("imp/br1A1", s, d).sum(), M.s("imp/br1m2", s, d).sum(), M.s("imp/br2A1m2", s, d).sum()
    resid = A1m - br1A1 - br2A1; resid2 = max(A1m2 - M.s("imp/br1A1m2", s, d).sum() - br2A1m2, 0.0)
    Zrep = Zd - br1 - br2A1 + z1 + z2
    out = {"P_b1": P1, "P_b2": P2, "A1_share_eof_form": float((z1 + z2) / Zd), "A1_share": float((z1 + z2 + resid) / Zrep),
           "branch1_share": float(z1 / Zrep), "outside_share": float(z2 / Zrep), "residual_A1_share": float(resid / Zrep),
           "outside_fraction_of_A1": float(z2 / (z1 + z2 + resid)) if (z1 + z2 + resid) > 0 else 0.0,
           "br1_rows_not_A1_share_of_br1": float((br1 - br1A1) / br1) if br1 > 0 else 0.0,
           "A1_share_main_set": float(A1m / Zd), "A1_ess_main_set": ess(A1m, A1m2),
           "lnZ_rep": float(math.log(Zrep)), "lnZ_main": float(math.log(Zd)),
           "A1_ess_rows": ess(z1 + z2 + resid, a1 * a1 * m1q.sum() + a2 * a2 * m2q.sum() + resid2),
           "branch1_ess_rows": ess(m1.sum(), m1q.sum()), "outside_ess_rows": ess(m2.sum(), m2q.sum())}
    # per band: rows ESS of the stratified A1 (resid per band from fine bins), paths / states for each pass stratum
    bm1 = np.bincount(B_OF_FINE, m1, NB); bq1 = np.bincount(B_OF_FINE, m1q, NB); bm2 = np.bincount(B_OF_FINE, m2, NB); bq2 = np.bincount(B_OF_FINE, m2q, NB)
    p1, s1 = B1.s("imp/par2/all", s, d), B1.s("imp/st2/all", s, d); p2, s2 = B2.s("imp/par2/A1", s, d), B2.s("imp/st2/A1", s, d)
    bA1 = np.bincount(B_OF_FINE, Mm[0], NB); bA12 = np.bincount(B_OF_FINE, Mm2[0], NB)
    rb = bA1 - M.s("imp/br1A1", s, d) - M.s("imp/br2A1", s, d); rb2 = np.maximum(bA12 - M.s("imp/br1A1m2", s, d) - M.s("imp/br2A1m2", s, d), 0)
    out["bands"] = []
    for i in range(NB):
        zz = a1 * bm1[i] + a2 * bm2[i] + rb[i]
        out["bands"].append({"band": NAMES[i], "A1_mass_share": float(zz / Zrep),
                             "A1_ess_rows": ess(zz, a1 * a1 * bq1[i] + a2 * a2 * bq2[i] + rb2[i]),
                             "branch1_rows_paths_states": [ess(bm1[i], bq1[i]), ess(bm1[i], p1[i]), ess(bm1[i], s1[i])],
                             "outside_rows_paths_states": [ess(bm2[i], bq2[i]), ess(bm2[i], p2[i]), ess(bm2[i], s2[i])]})
    return out


def main(work, outp):
    work = Path(work); f = lambda pat: sorted(work.glob(pat))
    sets = {"comb": Parts(f("main-prod-*.npz") + f("main-supp-*.npz"), "comb"), "alone": Parts(f("main-prod-*.npz"), "alone")}
    B1 = Parts(f("b1-prod-*.npz") + f("b1-supp-*.npz"), "comb"); B2 = Parts(f("b2-prod-*.npz"), "alone")
    glat = -44.975 + 0.05 * np.arange(NLAT); glon = 78.025 + 0.05 * np.arange(NLON)
    area = b.area_km2(np.meshgrid(glat, glon, indexing="ij")[0])
    Lg = {k: rho_L(SURF, *v) for k, v in GRIDL.items()}
    res = {"parts": {k: len(v.z) for k, v in {**sets, "b1": B1, "b2": B2}.items()},
           "rows": {k: int(sum(int(z["n_rows"]) for z in v.z)) for k, v in {**sets, "b1": B1, "b2": B2}.items()}, "cells": {}}
    for d in CELLS:
        e = {}
        for v, P in sets.items():
            e[v] = {s: summarise(P, s, d, Lg, area, glat, glon, mapP=P) for s in SETTINGS}
            for s in SETTINGS[1:]:
                e[v][s]["ln_mean_LH"] = e[v][s]["lnZ"] - e[v]["none"]["lnZ"]
        e["A1_strata"] = {s: a1_strata(sets["comb"], B1, B2, s, d) for s in SETTINGS}
        res["cells"][d] = e
        print(d, "done", flush=True)
    Path(outp).write_text(json.dumps(res, indent=1))


if __name__ == "__main__":
    main(*sys.argv[1:3])
