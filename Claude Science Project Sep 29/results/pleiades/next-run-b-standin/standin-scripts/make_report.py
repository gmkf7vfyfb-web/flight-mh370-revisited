"""Stand-in report builder (not module code): mixture figures via the module's own branch_figure.make()
(only the source line is replaced by a mixture-aware one built from the module's own run_provenance()),
the reference-289 comparison table, and one summary chart. Run after combine_mixture.py."""
import json, sys, textwrap
from pathlib import Path
import numpy as np, pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

WS = Path(__file__).resolve().parent
CSP = WS / "pl/Claude Science Project Sep 29"
PREP = CSP / "engine/hypotheses/pleiades/prepare"
sys.path.insert(0, str(PREP))
import branch_figure as BF  # noqa: E402

RUNS = CSP / "engine/runs/pleiades/next-run-b-standin"
RES = CSP / "results/pleiades/next-run-b-standin"
REF = WS / "repo/Claude Science Project Sep 29/results/pleiades"
NR = Path("/Users/pete/Downloads/mh370-exchange/end-of-flight/next-run")
LAB = ("core (b) split-half NOT converged; two-tank bookkeeping only; PROVISIONAL-OVERNIGHT; EoF sweep run by a stand-in; "
       "run by an architecture stand-in on the Pleiades module's behalf, module to review")
PFAM = {"next-free": 0.6948, "next-repro-radar": 0.1527, "next-descent-climb": 0.1376, "next-routes": 0.0149}

orig = BF.run_provenance
free_src = orig(NR / "next-free")
MIX_SRC = ("Source: end of flight's next-run impacts on core (b) m0011 hand-offs (EoF 3c6319f, idle floor ON), 4 strata mixed with core's P(family) "
           "held fixed and not updated by terminal-stage evidence (free 0.6948, Davey dynamics + radar 0.1527, descent-climb 0.1376, routes 0.0149; "
           "core split-half 0.71-0.88 vs floor 0.896, unconverged); within each stratum 4 seeds pooled with equal weight, 3.2 M impacts per seed. "
           "Free stratum detail: " + free_src[len("Source: "):])
BF.run_provenance = lambda root: MIX_SRC

plt.rcParams.update({"font.size": 6, "axes.titlesize": 6.5, "axes.labelsize": 6, "xtick.labelsize": 5.5, "ytick.labelsize": 5.5})
opts = json.loads((RES / "next-free" / "provenance.json").read_text())["options"]
for o in opts:
    d = RUNS / "mixture" / f"branch-{o.replace('/', '-')}-base"
    info = json.loads((d / "branch.json").read_text())
    if "impacts_root" not in info:
        info["impacts_root"] = str(NR); (d / "branch.json").write_text(json.dumps(info, indent=1))
    fig, _ = BF.make(d, CSP / "engine/hypotheses/pleiades", RES / "mixture" / f"branch-{o.replace('/', '-')}", plt=plt, labels=LAB + "; strata MIXED by P(family)")
    plt.close(fig)

# ---- comparison with reference-289 (module's committed tables) ----
S = pd.read_csv(RES / "mixture" / "by-0019-option-by-stratum-and-mixture.csv")
pa = pd.read_csv(REF / "branch-289-alive/plain-vs-alive.csv")
bo = pd.read_csv(REF / "branch-289/branch-by-0019-option.csv")
srch = {"base": "Phase 2 + Bluefin-21", "oi2018-2025": "+ OI 2018 + OI 2025-26 SE band", "none": "none"}
ref = []
for _, r in pa.iterrows():
    ref.append(dict(option="none" + ("+alive" if r.constraint == "+alive" else ""), field=r.field, stage=r.stage, search=srch[r.search],
                    ref_median_lat=round(r.cond_median_lat, 2), ref_hdr90_km2=round(r.cond_hdr90_km2), ref_ln_S=round(r.ln_S, 2),
                    ref_retained_under_H=round(r.search_retained_under_H, 3), ref_uncond_hdr90_km2=round(r.uncond_hdr90_km2)))
for _, r in bo.iterrows():
    o = r.option.split(" ")[0]
    if o == "none":
        continue
    ref.append(dict(option=o, field=r.field, stage=r.stage, search=srch["base"] if r.stage == "after search" else "none",
                    ref_median_lat=r.median_lat, ref_hdr90_km2=r.hdr90, ref_ln_S=r.lnS, ref_retained_under_H=r.retained, ref_uncond_hdr90_km2=r.uncond_hdr))
R = pd.DataFrame(ref)
M = S[S.stratum == "mixture"]
rng = S[S.stratum != "mixture"].groupby(["option", "field", "stage", "search"]).agg(
    strata_median_lo=("median_lat", "min"), strata_median_hi=("median_lat", "max"),
    strata_ret_lo=("retained_under_H", "min"), strata_ret_hi=("retained_under_H", "max"),
    strata_lnS_lo=("ln_S", "min"), strata_lnS_hi=("ln_S", "max")).reset_index()
C = M.merge(rng, on=["option", "field", "stage", "search"]).merge(R, on=["option", "field", "stage", "search"], how="left")
C["d_median_deg"] = (C.median_lat - C.ref_median_lat).round(2)
C.to_csv(RES / "mixture" / "comparison-vs-reference-289.csv", index=False)

# ---- summary chart: P+C3 after the base search, per option ----
order = [o for o in opts]
sub = C[(C.field == "P+C3") & (C.stage == "after search") & (C.search == srch["base"])].set_index("option").loc[order]
fig, axs = plt.subplots(1, 3, figsize=(7.1, 2.9), sharey=True, gridspec_kw=dict(wspace=0.08))
y = np.arange(len(order))[::-1]
for ax, (k, lo, hi, rk, xl) in zip(axs, [("median_lat", "strata_median_lo", "strata_median_hi", "ref_median_lat", "Conditional median latitude (°)"),
                                          ("retained_under_H", "strata_ret_lo", "strata_ret_hi", "ref_retained_under_H", "Search retained under H"),
                                          ("ln_S", "strata_lnS_lo", "strata_lnS_hi", "ref_ln_S", "ln S (tension; < 0 = tension)")]):
    ax.hlines(y, sub[lo], sub[hi], color="#9ab", lw=2.2, label="range over the 4 strata")
    ax.plot(sub[k], y, "o", color="#1f5fa8", ms=3.5, label="P(family) mixture")
    m = sub[rk].notna()
    ax.plot(sub[rk][m], y[m.values], "x", color="#b03030", ms=4, mew=1, label="reference-289 (module, 9-10 Oct)")
    ax.set_xlabel(xl)
    ax.grid(axis="x", lw=0.3, color="#ddd")
    if k == "ln_S":
        ax.axvline(0, color="#666", lw=0.6, ls=":")
axs[0].set_yticks(y); axs[0].set_yticklabels(order)
h, l = axs[0].get_legend_handles_labels()
fig.legend(h, l, loc="upper center", bbox_to_anchor=(0.5, 0.965), ncol=3, fontsize=5.5, frameon=False)
fig.suptitle("P+C3 conditional under H after the base search (Phase 2 + Bluefin-21), by 00:19 option — next-run (core (b)) vs reference-289",
             x=0.01, ha="left", y=1.0, fontsize=7)
notes = [MIX_SRC,
         "Labels: " + LAB + ".",
         "Recipe: Pleiades module's prepare/rerun_next.py at ed85311, unchanged, run per stratum (branch_eof289.py: weight = impact weight x exp(loglik:<option>), "
         "'+alive' adds end of flight's own constraint_log_factor, log-on cause 'other'); strata combined afterwards by the stand-in's combine_mixture.py "
         "with the module's own summarise(). Headline arm: rho4 = 0, equal cluster weights, GLORYS12 + GlobCurrent daily (+ ERA5) equal weight, P+C per model, measured spread.",
         "Search: the searched-areas module's own per-impact seabed-search column (Phase 2 2014-17 + Bluefin-21, point target, rho = 0.05), from mh370 evaluate at ed85311 on these impacts.",
         "Reference-289 markers: results/pleiades/branch-289/branch-by-0019-option.csv (plain options) and branch-289-alive/plain-vs-alive.csv (none, none+alive); eof-289-full, idle floor OFF. "
         "Options absent there have no marker. both/no-offset and both/startup-offset are parent-limited (52-265 effective parents per stratum): not estimates.",
         "Every value is conditional on H (the objects are debris from 9M-MRO); no Bayes factor or P(H | data). PROVISIONAL-OVERNIGHT; unconverged upstream."]
BF.footnote(fig, notes, width=175, size=5, y=-0.02)
fig.savefig(RES / "mixture" / "summary-pc3-by-option.png", dpi=300, bbox_inches="tight")
fig.savefig(RES / "mixture" / "summary-pc3-by-option.pdf", bbox_inches="tight")
print("done")
