"""Chart for hydroacoustics-audit-sus-absolute.md. Usage: python sus_absolute_chart.py <out_dir>"""
import json
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

OUT = sys.argv[1]
df = pd.read_csv(f"{OUT}/sus_absolute_bands.csv"); df = df[df.variant == "base"]
S = json.load(open(f"{OUT}/sus_absolute_summary.json"))
C610, C915, GREY = "#1f5fa8", "#c2571a", "#777777"
plt.rcParams.update({"font.size": 8, "axes.titlesize": 8, "axes.labelsize": 8, "xtick.labelsize": 7,
                     "ytick.labelsize": 7, "legend.fontsize": 7, "axes.spines.top": False, "axes.spines.right": False})
fig = plt.figure(figsize=(7.4, 8.2))
gs = fig.add_gridspec(2, 2, left=0.09, right=0.98, top=0.965, bottom=0.31, hspace=0.42, wspace=0.08,
                      height_ratios=[1.15, 1])
axs = [fig.add_subplot(gs[0, 0])]; axs.append(fig.add_subplot(gs[0, 1], sharey=axs[0])); axc = fig.add_subplot(gs[1, :])
fb = np.array(sorted(df.fc_hz.unique()))
for ax, st, name in ((axs[0], "H01W", "Cape Leeuwin hydrophone"), (axs[1], "H08S", "Diego Garcia South hydrophone")):
    d = df[df.station == st]
    for z, col in ((610.0, C610), (915.0, C915)):
        one = d[d.src_depth_m == z].groupby("fc_hz").first()
        ax.plot(one.index, one.sl_pred_a_db, "-", color=col, lw=1.4)
        ax.plot(one.index, one.sl_pred_b_db, "--", color=col, lw=1.1)
        ex = one[one.route_a_flag == "extrap"]
        ax.plot(ex.index, ex.sl_pred_a_db, ":", color="white", lw=1.0)
        pts = d[(d.src_depth_m == z)].dropna(subset=["implied_sl_db"])
        ax.plot(pts.fc_hz * (1.03 if z == 915 else 0.97), pts.implied_sl_db, "o", ms=3.6, mfc=col, mec="white",
                mew=0.4, alpha=0.9, ls="none")
    ax.set_xscale("log"); ax.set_xticks([5, 10, 20, 40, 63]); ax.set_xticklabels(["5", "10", "20", "40", "63"])
    ax.xaxis.set_minor_formatter(matplotlib.ticker.NullFormatter())
    ax.set_xlim(4.5, 70); ax.set_title(name, loc="left"); ax.set_xlabel("Frequency (Hz, one-third-octave band centre)")
    ax.grid(alpha=0.25, lw=0.5)
axs[0].set_ylabel("Source energy level at 1 m\n(dB re 1 µPa²·s/Hz)")
plt.setp(axs[1].get_yticklabels(), visible=False)
axs[0].set_ylim(155, 215)
h = [plt.Line2D([], [], color=C610, lw=1.4), plt.Line2D([], [], color=C915, lw=1.4),
     plt.Line2D([], [], color="k", lw=1.4), plt.Line2D([], [], color="k", lw=1.1, ls="--"),
     plt.Line2D([], [], marker="o", color="k", ls="none", ms=3.6)]
axs[0].legend(h, ["charge at 610 m", "charge at 915 m", "model, scaled from 244 m", "model, rebuilt at depth",
                  "measured signal + model loss"], loc="upper left", frameon=False, handlelength=2.2)
for ax, L in zip(axs + [axc], "abc"):
    ax.text(-0.02 if L != "c" else -0.01, 1.04, L, transform=ax.transAxes, fontweight="bold", fontsize=10, ha="right")


def fe(col, sel):
    d = df[sel].dropna(subset=[col]).copy(); d["x"] = np.log2(d.fc_hz)
    g = d.groupby(["shot", "station"])
    xd = d.x - g.x.transform("mean"); yd = d[col] - g[col].transform("mean")
    b = (xd * yd).sum() / (xd ** 2).sum(); res = yd - b * xd; k = g.ngroups
    return b, np.sqrt((res ** 2).sum() / (len(d) - k - 1) / (xd ** 2).sum())


rows = []
for lab, col in (("deep charges,\nmodel scaled from 244 m", "resid_a_db"), ("deep charges,\nmodel rebuilt at depth", "resid_b_db")):
    for st, nm in (("H01W", "CL"), ("H08S", "DGS")):
        b, se = fe(col, df.station == st); rows.append((lab, nm, b, se, C610 if "scaled" in lab else C915))
air = json.load(open(sys.argv[2])) if len(sys.argv) > 2 else None
rows += [("airgun near the surface\n(audit, same propagation)", "CL", 10.38, 0.93, GREY),
         ("airgun near the surface\n(audit, same propagation)", "DGS", 7.42, 0.71, GREY)]
axc.axhspan(-1.5, 1.5, color="#d9ead3", zorder=0); axc.axhspan(1.5, 3, color="#fff2cc", zorder=0)
axc.axhspan(-3, -1.5, color="#fff2cc", zorder=0); axc.axhline(0, color="k", lw=0.6)
labs = []
for i, (lab, nm, b, se, col) in enumerate(rows):
    x = (i // 2) * 1.0 + (i % 2) * 0.3
    axc.errorbar(x, b, yerr=1.96 * se, fmt="o" if nm == "CL" else "s", color=col, ms=5, capsize=3, lw=1)
    axc.text(x + 0.05, b + (0.7 if abs(b) < 0.6 else 0), f"{nm} {b:+.1f}", va="center", fontsize=7)
    if i % 2 == 0:
        labs.append((x + 0.15, lab))
axc.set_xticks([p for p, _ in labs]); axc.set_xticklabels([l for _, l in labs])
axc.set_xlim(-0.3, 2.75); axc.set_ylim(-7.5, 13)
axc.set_ylabel("Residual slope (dB per octave)\nmeasured − model")
axc.set_title("Deep charges do not show the airgun's rise of residual with frequency (95 % intervals)", loc="left")
axc.text(2.72, -0.75, "pass ±1.5", fontsize=7, ha="right", va="center", color="#38761d")
axc.text(2.72, 2.25, "partial ±3", fontsize=7, ha="right", va="center", color="#7f6000")
axc.text(0.0, 11.8, "CL = Cape Leeuwin, DGS = Diego Garcia South", fontsize=7)
ste = ("STE100: UNCONVERGED (the core filter is not converged; this test does not use it). Panels a and b: the dots are the "
       "level that the charge had to make at 1 m, from the measured signal and the model loss. The lines are two "
       "estimates of that level from Gaspin and Shuler (1971). The solid line scales their 244 m result to the true "
       "depth. The broken line builds the pulse again at the true depth. The white dots on a line show where the scaled "
       "estimate goes below their lowest band. The two estimates are different by 4 to 17 dB in the bands that we "
       "use, so the absolute level is not known well. Panel c: the frequency slope of measured minus model. The deep "
       "charges have a slope near zero or negative. The airgun near the surface had a large positive slope.")
tech = ("Technical: core (b) split-half NOT CONVERGED (not used). Source: G&S NOLTR 71-160 Table 3 (p. 12), 1.8 lb TNT, "
        "free field, ideal 1/3-oct bands, dB re 1 erg/cm²/Hz at 100 yd, converted with ρc = 1.539e5 cgs and 20 log 91.44 m. "
        "Solid: time similitude from 800 ft, s = (833/(z+33))^(5/6) ft (G&S §7.5); dotted = extrapolated at the 12.5–16 Hz "
        "slope. Dashed: Table 2 construction re-implemented at depth (κ = 4, sin² negative phases; reproduces Table 3 at "
        "800 ft to RMS 1.3 dB). Both outside G&S's stated validity (≤ ~1000 ft, §8.1). Points: audit implied SL = S_b + TL_b "
        "+ 10 log 6 s, bands with (S+N)/N ≥ 3 dB only; TL = module KRAKEN wrapper on audit paths (WOA23, GEBCO), "
        "band centre. 8 shots of 1.8 lb (A6–A10), 12 shot-station pairs, 45 bands, 16–63 Hz; A11 excluded (charge "
        "not 1.8 lb). Panel c: within-pair OLS slope of r_b on log2 f, pooled per station, ±1.96 SE; air9 from audit "
        "C1 (12.5–63 / 6.3–63 Hz). Shading = C4 slope thresholds (criteria.md, 940f1a3).")
import textwrap
fig.text(0.01, 0.235, "\n".join(textwrap.wrap(ste, 150)), fontsize=6.3, va="top", ha="left")
fig.text(0.01, 0.118, "\n".join(textwrap.wrap(tech, 150)), fontsize=6.3, va="top", ha="left", color="#333333")
fig.savefig(f"{OUT}/hydroacoustics-audit-sus-absolute.png", dpi=200)
fig.savefig(f"{OUT}/hydroacoustics-audit-sus-absolute.pdf")
print("saved")
