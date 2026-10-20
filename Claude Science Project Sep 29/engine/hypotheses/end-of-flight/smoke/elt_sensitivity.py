"""Emergency beacon (ELT) non-detection as a labelled sensitivity (evidence register B2; END_OF_FLIGHT.md 17 Oct 2026 22:50Z).

    python elt_sensitivity.py ACC_NPZ TABLE_JSON OUT_DIR

Observation: no 406 MHz alert from 9M-MRO (SIR p. 54, p. 365, finding 10 p. 433). Only the fixed ELTA 406 unit (g-switch, STA 1880,
blade antenna on the fuselage top) can raise an automatic satellite alert: the portable unit is normally OFF and the two raft units are
121.5/243 MHz only and need raft deployment (SIR pp. 53-54). Per impact row:
    P(no alert | row) = delta_f + (1 - delta_f) * (1 - p_class(row))
with the impact class from the contact state:
    ditching-like : |flight-path angle| <= 10 deg and contact speed <= 100 m/s
    high-energy   : contact speed > 212 m/s (1.25 VMO, G13) or |flight-path angle| >= 30 deg
    intermediate  : the rest
and p_class = probability the fixed ELT activates, survives and transmits a 406 MHz burst, in three declared settings:
    low     (0.40, 0.15, 0.00)   central (0.50, 0.25, 0.05)   high (0.60, 0.34, 0.15)   for (ditching-like, intermediate, high-energy)
Sources: ATSB AR-2012-128 (ELTs worked in about 40-60 % of accidents where activation was expected: ditching-like row); SIR ADREP figures
15-34 % over all accidents (intermediate row); BEA post-AF447 work (fixed ELTs destroyed in high-energy accidents; upper value 15 % = SIR
App. 1.6D overall rate). delta_f = probability the fixed unit was silenced before impact (needs cabin-ceiling access; no official document
discusses it). Scenarios: none; deliberate descent (B) 0.5; B 1.0; B and A2 1.0.
Input: the mass-preserving resample from run_j_maps_pass.py (columns mass lat lon fam stratum peak energy fpa speed).
Writes elt-sensitivity.json and elt-sensitivity.{png,pdf}.
"""
import json, sys, pathlib, textwrap
import numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt

P = {"low": (0.40, 0.15, 0.00), "central": (0.50, 0.25, 0.05), "high": (0.60, 0.34, 0.15)}
SCEN = {"not silenced": {}, "deliberate descent silenced p = 0.5": {"B": 0.5}, "deliberate descent silenced": {"B": 1.0},
        "deliberate descent and controlled-to-surface silenced": {"B": 1.0, "A2": 1.0}}
FAMS = {"A1": (1,), "A2": (2,), "B": (3, 6)}
CELLS = {"D0": "00:19 data not used", "D2": "00:19:29 range and frequency", "D4": "Both 00:19 frequencies, shared start-up offset"}


def wq(x, w, q):
    o = np.argsort(x); c = np.cumsum(w[o]); c /= c[-1]
    return float(x[o][min(np.searchsorted(c, q), len(x) - 1)])


def main(acc, table, out):
    out = pathlib.Path(out); out.mkdir(parents=True, exist_ok=True); A = np.load(acc); R = {"settings": P, "scenarios": SCEN, "cells": {}}
    for d in CELLS:
        x = A[f"RS_{d}"].astype(np.float64); m = x[:, 0] / x[:, 0].sum(); lat = x[:, 1]; f = x[:, 3]; fpa = np.abs(x[:, 7]); v = x[:, 8]
        cls = np.where((fpa <= 10) & (v <= 100), 0, np.where((v > 212) | (fpa >= 30), 2, 1))
        fam = {k: np.isin(f, c) for k, c in FAMS.items()}
        base = {k: float(m[s].sum()) for k, s in fam.items()}
        r = {"prior_family_share": base, "class_share_by_family": {k: [float(m[s & (cls == c)].sum() / m[s].sum()) for c in (0, 1, 2)] for k, s in fam.items()},
             "lat_median_prior": wq(lat, m, 0.5), "results": {}}
        for pn, pc in P.items():
            pal = np.array(pc)[cls]
            for sn, dl in SCEN.items():
                delta = np.zeros(len(m))
                for k, val in dl.items(): delta[fam[k]] = val
                L = delta + (1 - delta) * (1 - pal); mL = m * L; Z = mL.sum()
                EL = {k: float(mL[s].sum() / m[s].sum()) for k, s in fam.items()}
                r["results"][f"{pn} | {sn}"] = {"lnL": float(np.log(Z)), "E_L_given_family": EL,
                                               "ln_ratio_vs_A1": {k: float(np.log(EL[k] / EL["A1"])) for k in FAMS},
                                               "posterior_family_share": {k: float(mL[s].sum() / Z) for k, s in fam.items()},
                                               "lat_median_shift_deg": wq(lat, mL, 0.5) - r["lat_median_prior"]}
        R["cells"][d] = r
    json.dump(R, open(out / "elt-sensitivity.json", "w"), indent=1)
    # figure: family shares, prior and after the non-detection, central setting, per scenario, per treatment
    matplotlib.rcParams.update({"font.size": 7, "axes.spines.top": False, "axes.spines.right": False, "legend.frameon": False, "pdf.fonttype": 42})
    fc = {"A1": "#3b3b3b", "A2": "#8c8c8c", "B": "#c9c9c9"}
    names = {"A1": "Fuel exhaustion, then no control", "A2": "Fuel exhaustion, then controlled to the surface", "B": "Deliberate descent before fuel exhaustion"}
    fig, axs = plt.subplots(1, 3, figsize=(7.4, 3.6), sharey=True, gridspec_kw={"wspace": 0.04})
    rows = ["before"] + list(SCEN)
    lab = {"before": "before the beacon evidence", "not silenced": "beacon not silenced", "deliberate descent silenced p = 0.5": "silenced with p = 0.5\nin a deliberate descent",
           "deliberate descent silenced": "always silenced in a\ndeliberate descent", "deliberate descent and controlled-to-surface silenced": "always silenced in a deliberate\nor controlled descent"}
    for ax, d in zip(axs, CELLS):
        r = R["cells"][d]
        for i, rn in enumerate(rows):
            sh = r["prior_family_share"] if rn == "before" else r["results"][f"central | {rn}"]["posterior_family_share"]
            left = 0.0
            for k in FAMS:
                ax.barh(len(rows) - 1 - i, sh[k], left=left, color=fc[k], edgecolor="white", lw=0.4, label=names[k] if (i == 0 and d == "D0") else None)
                if sh[k] > 0.07: ax.text(left + sh[k] / 2, len(rows) - 1 - i, f"{sh[k]:.2f}", ha="center", va="center", fontsize=5.8, color="white" if k != "B" else "black")
                left += sh[k]
            if rn != "before":
                lo = r["results"][f"low | {rn}"]["posterior_family_share"]["B"]; hi = r["results"][f"high | {rn}"]["posterior_family_share"]["B"]
                ax.text(1.01, len(rows) - 1 - i, f"{min(lo, hi):.2f}-{max(lo, hi):.2f}", va="center", fontsize=5.4, color="#555555")
        ax.set_xlim(0, 1.27); ax.set_xticks([0, 0.5, 1]); ax.set_title(textwrap.fill(CELLS[d], 30), fontsize=6.8, loc="left"); ax.set_xlabel("share of probability")
    axs[0].set_yticks(range(len(rows))); axs[0].set_yticklabels([lab[r] for r in rows[::-1]], fontsize=6)
    fig.legend(loc="upper center", ncol=3, fontsize=6, bbox_to_anchor=(0.55, 1.0))
    fig.suptitle("No beacon alert moves probability away from survivable ditchings; it changes the family shares only a little unless the beacon was silenced",
                 x=0.01, ha="left", fontsize=7, y=0.90)
    n1 = ("Note 1: The aircraft's fixed emergency beacon sends a satellite alert after a hard deceleration. No alert came. A beacon works more often in a "
          "survivable ditching than in a fast, steep impact, which usually destroys it. The bars show the share of each type of flight end before and after "
          "this evidence, with the middle values of the beacon rates. The grey numbers at the right show the range of the deliberate-descent share for the low "
          "and high rates. A person can silence the beacon only from the cabin ceiling; no official report discusses this. This is a sensitivity, not a result.")
    n2 = ("Note 2: P(no alert | row) = delta + (1 - delta)(1 - p_class); classes ditching-like (|FPA| <= 10 deg, v <= 100 m/s), high-energy (v > 212 m/s or "
          "|FPA| >= 30 deg), intermediate; p_class low/central/high = (0.40, 0.15, 0.00)/(0.50, 0.25, 0.05)/(0.60, 0.34, 0.15) (ATSB AR-2012-128; SIR pp. 53-56, "
          "365-366, App. 1.6D; BEA post-AF447). Run J impact resample (10,000 rows per seed per treatment, all strata), q = 1/3, C2 silent; families A1 = code 1, "
          "A2 = 2, B = 3+6. Uncontrolled-arm dynamics NOT CALIBRATED (Boeing leave-one-out gate failed in all three rounds): impact class is a labelled sensitivity.")
    fig.text(0.01, 0.01, textwrap.fill(n1, 200) + "\n" + textwrap.fill(n2, 200), fontsize=4.7, va="bottom")
    fig.subplots_adjust(left=0.2, right=0.99, top=0.78, bottom=0.33)
    for ext in ("png", "pdf"): fig.savefig(out / f"elt-sensitivity.{ext}", dpi=300)
    for d in CELLS:
        r = R["cells"][d]; print(d, "prior", {k: round(v, 3) for k, v in r["prior_family_share"].items()}, "classes", {k: [round(a, 2) for a in v] for k, v in r["class_share_by_family"].items()})
        for key, v in r["results"].items():
            print("  ", key, "lnL %.3f" % v["lnL"], "lnratio", {k: round(a, 3) for k, a in v["ln_ratio_vs_A1"].items()}, "post", {k: round(a, 3) for k, a in v["posterior_family_share"].items()}, "dlat %.3f" % v["lat_median_shift_deg"])


if __name__ == "__main__":
    main(*sys.argv[1:4])
