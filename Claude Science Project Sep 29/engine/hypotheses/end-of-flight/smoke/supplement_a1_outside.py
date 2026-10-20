"""A1 by the two conditional passes, stratified (overnight order A, 20 Oct 2026).

    python supplement_a1_outside.py MAIN_PARTS_DIR BRANCH_PARTS_DIR OUTSIDE_PARTS_DIR MAIN_SUMMARY_JSON OUT_JSON

Family A1 (cruise to fuel exhaustion then no control) is the union of two strata of the flame-out-associated onset:
  branch 1 = control realised "no intervention"                (18 Oct branch pass + 19 Oct supplement branch pass, rule B);
  branch 2 = recovery attempted (requested "upset then recovery"); A1 is its undemonstrated part (20 Oct outside pass).
For treatment d:  Z(d, A1) = Z(D0') [ P_D0'(b1) E_D0'[L_d | b1] + P_D0'(b2) E_D0'[L_d 1_A1 | b2] ],
with P_D0'(b) from the main rule-B set (MAIN_PARTS_DIR: production + both supplement halves; parts carry the per-band D0 mass in
each branch) and E from the conditional passes (PARTS: supplement_combine.py parts of the passes; the outside pass is run J seeds
1-8 only, weighted as production alone). A1 share = Z(d, A1) / Z(d). Band split and ESS (rows / paths / distinct 00:11 states)
per impact band for each stratum; the main set's own A1 cells are given beside for comparison.
"""
import json, pathlib, sys
import numpy as np

FINE = np.round(np.arange(-45.0, -14.95, 0.1), 2); BANDS = np.arange(-45.0, -14.0, 5.0); NB = len(BANDS) - 1
B_OF_FINE = np.digitize(FINE[:-1] + 0.05, BANDS) - 1
NAMES = [f"{-BANDS[i]:.0f}-{-BANDS[i+1]:.0f} S" for i in range(NB)]
CELLS = ("D0", "D2", "D3", "D4", "D5", "D3s", "D4s", "D5s")   # Ds: log-on from another cause only (C2 silent)


def parts(d, want):
    d = pathlib.Path(d); out = []
    for p in sorted(d.glob("prod-*.npz")): out.append((np.load(p), "alone" if want == "alone" else "comb"))
    if want == "comb":
        for p in sorted(d.glob("supp-*.npz")): out.append((np.load(p), "comb"))
    return out


def stratum(P, d, a1_only):
    """E_D0'[L_d (1_A1) | stratum] and its band split / ESS from a conditional pass's parts."""
    Z0 = sum(z[f"{v}/D0/imp/m"].sum() for z, v in P)
    if a1_only:
        m = sum(z[f"{v}/{d}/imp/m"][0] for z, v in P); m2 = sum(z[f"{v}/{d}/imp/m2"][0] for z, v in P); key = "A1"
    else:
        m = sum(z[f"{v}/{d}/imp/m"].sum(0) for z, v in P); m2 = sum(z[f"{v}/{d}/imp/m2"].sum(0) for z, v in P); key = "all"
    bm = np.bincount(B_OF_FINE, m, NB); bm2 = np.bincount(B_OF_FINE, m2, NB)
    p2 = sum(z[f"{v}/{d}/imp/par2/{key}"] for z, v in P); s2 = sum(z[f"{v}/{d}/imp/st2/{key}"] for z, v in P)
    ess = lambda a, b: float(a * a / b) if b > 0 else 0.0
    return float(m.sum() / Z0), [{"band": NAMES[i], "frac": float(bm[i] / m.sum()) if m.sum() > 0 else 0.0, "ess_rows": ess(bm[i], bm2[i]),
                                  "ess_paths": ess(bm[i], p2[i]), "ess_states": ess(bm[i], s2[i])} for i in range(NB)], ess(m.sum(), m2.sum())


def main(main_dir, br_dir, out_dir, main_json, outp):
    M = json.load(open(main_json)); MP = parts(main_dir, "comb")
    Ztot = sum(z[f"{v}/D0/imp/m"].sum() for z, v in MP)
    P1 = float(sum(z[f"{v}/D0/imp/br1"].sum() for z, v in MP) / Ztot); P2 = float(sum(z[f"{v}/D0/imp/br2"].sum() for z, v in MP) / Ztot)
    MPa = parts(main_dir, "alone"); Za = sum(z[f"{v}/D0/imp/m"].sum() for z, v in MPa)
    P1a = float(sum(z[f"{v}/D0/imp/br1"].sum() for z, v in MPa) / Za); P2a = float(sum(z[f"{v}/D0/imp/br2"].sum() for z, v in MPa) / Za)
    B1 = parts(br_dir, "comb"); B2 = parts(out_dir, "alone")
    frac_b2 = float(sum(z["alone/D0/imp/br2"].sum() for z, v in B2) / sum(z["alone/D0/imp/m"].sum() for z, v in B2))
    res = {"P_D0prime": {"branch1_ruleB": P1, "branch2_ruleB": P2, "branch1_production": P1a, "branch2_production": P2a},
           "outside_pass_rows_in_branch2_D0_mass_fraction": frac_b2, "cells": {}}
    lnZ0 = M["cells"]["D0"]["comb"]["imp"]["lnZ"]
    for d in CELLS:
        lnZd = M["cells"][d]["comb"]["imp"]["lnZ"]
        E1, b1, e1 = stratum(B1, d, False); E2, b2, e2 = stratum(B2, d, True)
        z1 = np.exp(lnZ0 - lnZd) * P1 * E1; z2 = np.exp(lnZ0 - lnZd) * P2 * E2
        # the main set's own A1 cells: total and outside-branch (br2 & A1) masses per band
        mA1 = sum(z[f"{v}/{d}/imp/m"][0] for z, v in MP); Zd = sum(z[f"{v}/{d}/imp/m"].sum() for z, v in MP)
        o2 = sum(z[f"{v}/{d}/imp/br2A1"] for z, v in MP)
        res["cells"][d] = {"A1_share_stratified": float(z1 + z2), "branch1_share": float(z1), "outside_share": float(z2),
                           "outside_fraction_of_A1": float(z2 / (z1 + z2)) if z1 + z2 > 0 else 0.0,
                           "A1_share_main_set": float(mA1.sum() / Zd), "outside_fraction_of_A1_main_set": float(o2.sum() / mA1.sum()) if mA1.sum() > 0 else 0.0,
                           "branch1_bands": b1, "outside_bands": b2, "outside_ess_rows_all": e2,
                           "A1_bands_stratified": [{"band": NAMES[i], "mass_share_of_Z_d": float(z1 * b1[i]["frac"] + z2 * b2[i]["frac"])} for i in range(NB)]}
    json.dump(res, open(outp, "w"), indent=1)
    print(json.dumps(res["P_D0prime"]), "outside-pass D0 mass in branch 2:", round(frac_b2, 4))
    for d, c in res["cells"].items():
        print(f"{d}: A1 stratified {c['A1_share_stratified']:.4f} (branch {c['branch1_share']:.4f} + outside {c['outside_share']:.4f}; outside {c['outside_fraction_of_A1']:.2f} of A1) "
              f"| main set A1 {c['A1_share_main_set']:.4f}, outside {c['outside_fraction_of_A1_main_set']:.2f} | outside ESS rows {c['outside_ess_rows_all']:.0f} | "
              + " | ".join(f"{b['band']} {b['ess_rows']:.0f}/{b['ess_paths']:.0f}/{b['ess_states']:.0f}" for b in c["outside_bands"][1:5]))


if __name__ == "__main__":
    main(*sys.argv[1:])
