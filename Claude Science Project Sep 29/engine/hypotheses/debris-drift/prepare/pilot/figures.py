"""Pilot figure (PROVISIONAL; not evidence). Four panels from a merged pilot run directory.

a. Per-find kernel effective sample size at the primary bandwidth, across released nodes.
b. Fraction of nodes whose nine-find likelihood is Monte Carlo resolved, by latitude and bandwidth.
c. Resolved ln L relative to its maximum, by latitude, at the bandwidths that resolve.
d. Arrival probability by detection segment and motion class (median and 5-95% over nodes),
   against the ranges predicted before the run (results/debris-drift-pilot-prediction.md).

Usage (inside a kernel that may define apply_figure_style): RUN, OUT = ..., exec(open(...).read())
or: python figures.py <merged-run-dir> <out-prefix>
"""
import sys

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

try:
    RUN, OUT
except NameError:
    RUN, OUT = sys.argv[1], sys.argv[2]
if "apply_figure_style" in globals():
    apply_figure_style(sizes=(8, 7, 6))

d = pd.read_csv(f"{RUN}/nodes.csv")
finds = [c[len("n_eff_debris_"):] for c in d.columns if c.startswith("n_eff_debris_")]
short = {f: f.split("-")[0].capitalize() for f in finds}
classes = ["flaperon", "low_exposure_exterior", "high_windage_interior"]
cls_label = {"flaperon": "flaperon", "low_exposure_exterior": "low-exposure exterior", "high_windage_interior": "high-windage interior"}
cls_col = {"flaperon": "#1b6ca8", "low_exposure_exterior": "#e08214", "high_windage_interior": "#7b3294"}
segs = ["S1 Réunion", "S2 Mauritius-Rodrigues", "S3 S. Mozambique", "S4 S. Africa", "S5 NE Madagascar", "S6 Pemba"]
predicted = {0: (1e-4, 1e-3), 1: (1e-4, 1e-3), 2: (1e-3, 1e-2), 3: (1e-3, 1e-2), 4: (1e-4, 1e-3), 5: (1e-4, 1e-3)}
n = len(d)
try:
    NOISE_TITLE
except NameError:
    NOISE_TITLE = "Resolved ln L: spread is mostly Monte Carlo noise"

fig, axs = plt.subplots(2, 2, figsize=(7.2, 6.2), constrained_layout=True)

ax = axs[0, 0]
order = sorted(finds, key=lambda f: d[f"n_eff_debris_{f}"].median())
for i, f in enumerate(order):
    v = d[f"n_eff_debris_{f}"].values
    zero = np.mean(v < 1)
    lo, med, hi = np.percentile(v, [5, 50, 95])
    ax.plot([max(lo, 0.1), max(hi, 0.1)], [i, i], color="0.55", lw=1.2, zorder=1)
    ax.scatter([max(med, 0.1)], [i], color="k", s=14, zorder=2)
    ax.text(30, i, f"{zero:.0%} < 1", va="center", fontsize=6, color="0.3")
ax.set_xscale("log")
ax.set_xlim(0.08, 80)
ax.set_xticks([0.1, 1, 10])
ax.set_xticklabels(["0", "1", "10"])
ax.set_yticks(range(len(order)))
ax.set_yticklabels([short[f] for f in order])
ax.set_xlabel("kernel effective sample size per node (50 km)")
ax.set_title("Rodrigues and Mossel Bay are not resolved at 50 km", loc="left")

ax = axs[0, 1]
bins = np.arange(np.floor(d.lat_deg.min()), np.ceil(d.lat_deg.max()) + 1, 1.0)
mid = 0.5 * (bins[1:] + bins[:-1])
cut = pd.cut(d.lat_deg, bins)
for col, lab, c in [("ln_l", "25 and 50 km (primary): none", "#6baed6"), ("ln_l_h100", "100 km", "#2171b5"), ("ln_l_h200", "200 km", "#08306b")]:
    fr = d.groupby(cut, observed=False)[col].apply(lambda x: x.notna().mean()).values
    ax.plot(mid, fr, marker="o", ms=3, color=c, label=lab)
ax.set_xlabel("node latitude (°)")
ax.set_ylabel("fraction of nodes resolved")
ax.set_ylim(-0.04, 1.04)
ax.legend(frameon=False, loc="upper left", fontsize=6)
ax.set_title("Only wide kernels resolve, and fewer nodes in the south", loc="left")

ax = axs[1, 0]
for col, lab, c in [("ln_l_h100", "100 km", "#2171b5"), ("ln_l_h200", "200 km", "#08306b")]:
    v = d[col]
    ok = v.notna()
    if ok.sum():
        ax.scatter(d.lat_deg[ok], v[ok] - v[ok].max(), s=5, alpha=0.6, color=c, label=f"{lab} (n = {ok.sum()})", linewidths=0)
ax.set_xlabel("node latitude (°)")
ax.set_ylabel("ln L − max (resolved nodes)")
ax.legend(frameon=True, framealpha=0.92, edgecolor="none", loc="lower left", fontsize=6, markerscale=2)
ax.set_title(NOISE_TITLE, loc="left")

ax = axs[1, 1]
w = 0.25
for k in range(6):
    lo_p, hi_p = predicted[k]
    ax.add_patch(mpl.patches.Rectangle((k - 0.45, lo_p), 0.9, hi_p - lo_p, color="0.9", zorder=0, lw=0))
    for j, cl in enumerate(classes):
        v = d[f"p_{cl}_{k}"].values
        lo, med, hi = np.percentile(v, [5, 50, 95])
        x = k + (j - 1) * w
        ax.plot([x, x], [max(lo, 1e-6), max(hi, 1e-6)], color=cls_col[cl], lw=1.2)
        ax.scatter([x], [max(med, 1e-6)], color=cls_col[cl], s=12, label=cls_label[cl] if k == 0 else None, zorder=3)
ax.set_yscale("log")
ax.set_ylim(5e-6, 0.2)
ax.set_xticks(range(6))
ax.set_xticklabels([s.split(" ", 1)[0] for s in segs])
ax.set_ylabel("arrival probability by window end")
ax.legend(frameon=False, loc="lower left", fontsize=6, bbox_to_anchor=(0.0, 0.0))
ax.text(5.45, 6e-5, "grey: predicted range", ha="right", fontsize=6, color="0.4")
ax.set_title("Islands and Madagascar arrive far above prediction", loc="left")

for a, l in zip(axs.flat, "abcd"):
    if "panel_letter" in globals():
        panel_letter(a, l)
fig.suptitle(f"Drift pilot, PROVISIONAL (land-mask beaching, one product, K = 248 m²/s; {n} nodes). Not evidence.", fontsize=7, x=0.01, ha="left")
try:
    FOOTNOTE
except NameError:
    FOOTNOTE = ""
if FOOTNOTE:
    # Standing rule (Pete, 9 Oct ~20:20 UTC): run information beneath the chart, never in the axes.
    fig.text(0.01, -0.005, FOOTNOTE, ha="left", va="top", fontsize=5.5, color="0.25", wrap=True)
fig.savefig(f"{OUT}.png", dpi=300, bbox_inches="tight")
fig.savefig(f"{OUT}.pdf", bbox_inches="tight")
