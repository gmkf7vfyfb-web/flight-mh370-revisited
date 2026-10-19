"""A1-branch conditional pass on the run J northern supplement: A1 ESS and A1 band masses by impact band (overnight order A add-on).

    python supplement_a1_branch.py PARTS_DIR MAIN_SUMMARY_JSON OUT_JSON [P_BRANCH=0.0935]

PARTS_DIR holds prod-<k>.npz (the 18 Oct A1-branch pass, run J seeds 1-8, supplement_combine.py with SUP_S1=8 and SUP_N1 = their
hand-off rows) and supp-<s>.npz (tonight's A1-branch pass on the k = 2 supplement paths), combined by rule B. Stratified estimator
(results/eof-a1-branch-oct18): Z(d, branch, band) = Z(D0') P_D0'(branch) E_D0'[L_d 1_band | branch]; the A1 band share of
treatment d is that over Z(d) (main rule-B set, MAIN_SUMMARY_JSON), plus the A1 rows outside the branch, which this pass does not
sample (undemonstrated recoveries; not added here). ESS = Kish over the branch rows, by rows, paths and distinct 00:11 states.
"""
import json, pathlib, sys
import numpy as np

FINE = np.round(np.arange(-45.0, -14.95, 0.1), 2); BANDS = np.arange(-45.0, -14.0, 5.0); NB = len(BANDS) - 1
B_OF_FINE = np.digitize(FINE[:-1] + 0.05, BANDS) - 1
NAMES = [f"{-BANDS[i]:.0f}-{-BANDS[i+1]:.0f} S" for i in range(NB)]


def main(pdir, main_json, outp, p_branch=0.0935):
    p_branch = float(p_branch); M = json.load(open(main_json)); pdir = pathlib.Path(pdir)
    sets = {"production branch pass alone (8 seeds)": [(np.load(p), "alone") for p in sorted(pdir.glob("prod-*.npz"))]}
    sets["+ supplement branch pass (rule B)"] = [(np.load(p), "comb") for p in sorted(pdir.glob("prod-*.npz"))] + [(np.load(p), "comb") for p in sorted(pdir.glob("supp-*.npz"))]
    res = {"p_branch_D0prime": p_branch, "sets": {}}
    for name, P in sets.items():
        Z0 = sum(z[f"{v}/D0/imp/m"].sum() for z, v in P); out = {}
        for d in ("D0", "D2", "D3", "D4", "D5"):
            m = sum(z[f"{v}/{d}/imp/m"].sum(0) for z, v in P); m2 = sum(z[f"{v}/{d}/imp/m2"].sum(0) for z, v in P)
            bm = np.bincount(B_OF_FINE, m, NB); bm2 = np.bincount(B_OF_FINE, m2, NB)
            p2 = sum(z[f"{v}/{d}/imp/par2/all"] for z, v in P); s2 = sum(z[f"{v}/{d}/imp/st2/all"] for z, v in P)
            lnE = np.log(m.sum() / Z0); lnZd = M["cells"][d]["comb"]["imp"]["lnZ"]; lnZ0 = M["cells"]["D0"]["comb"]["imp"]["lnZ"]
            share = float(np.exp(lnZ0 + np.log(p_branch) + lnE - lnZd))
            out[d] = {"ln_E_L_given_branch": float(lnE), "branch_share_of_Z_d": share,
                      "bands": [{"band": NAMES[i], "branch_mass_share_of_Z_d": float(share * bm[i] / m.sum()),
                                 "ess_rows": float(bm[i] ** 2 / bm2[i]) if bm2[i] > 0 else 0.0,
                                 "ess_paths": float(bm[i] ** 2 / p2[i]) if p2[i] > 0 else 0.0,
                                 "ess_states": float(bm[i] ** 2 / s2[i]) if s2[i] > 0 else 0.0} for i in range(NB)]}
        res["sets"][name] = out
    json.dump(res, open(outp, "w"), indent=1)
    for name, out in res["sets"].items():
        print(f"\n{name}")
        for d, o in out.items():
            print(f"  {d} ln E[L|branch] {o['ln_E_L_given_branch']:.3f} share {o['branch_share_of_Z_d']:.4f} | " + " | ".join(
                f"{b['band']} {b['branch_mass_share_of_Z_d']:.4f} {b['ess_rows']:.0f}/{b['ess_paths']:.0f}/{b['ess_states']:.0f}" for b in o["bands"][1:5]))


if __name__ == "__main__":
    main(*sys.argv[1:])
