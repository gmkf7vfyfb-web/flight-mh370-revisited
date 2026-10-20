"""Audit figure: model-minus-measurement checks of the module's propagation. (a) air9 airgun, observed - model TL per
band at both stations, flat source (as Blackman) and with the array-directivity source model M3; (b) SUS 2003, the
station difference H01W - H08S of the implied source level (source cancels), per shot.

Usage: python fig_residuals.py <air9_residuals.csv> <sus_bands.csv> <out_png_stem>
"""
import sys
import textwrap

import matplotlib as mpl
mpl.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

R = pd.read_csv(sys.argv[1]); B = pd.read_csv(sys.argv[2]); out = sys.argv[3]
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 8, "axes.spines.top": False, "axes.spines.right": False})
C = {"H01W": "#1f4e9c", "H08S": "#b35806"}
fig = plt.figure(figsize=(9.0, 5.6))
a1 = fig.add_axes([0.07, 0.36, 0.40, 0.55]); a2 = fig.add_axes([0.57, 0.36, 0.40, 0.55])
for st in ("H01W", "H08S"):
    for mdl, ls, mk, lab in (("M1", "-", "o", "flat source (as Blackman)"), ("M3_e0", "--", "s", "source with array directivity")):
        g = R[(R.station == st) & (R.model == mdl) & (R.src_depth_m == 10.0)]
        a1.plot(g.fc_hz, g.residual_db, ls=ls, marker=mk, ms=3.5, color=C[st], mfc=C[st] if mdl == "M1" else "white", lw=1.1,
                label=f"{'Cape Leeuwin' if st == 'H01W' else 'Diego Garcia South'}, {lab}")
a1.axhline(0, color="0.5", lw=0.7); a1.axhspan(-3, 3, color="0.9", lw=0, zorder=0)
a1.set_xscale("log"); a1.set_xticks([6.3, 10, 16, 25, 40, 63]); a1.set_xticklabels(["6.3", "10", "16", "25", "40", "63"]); a1.minorticks_off()
a1.set_xlabel("Frequency (Hz)"); a1.set_ylabel("Measured minus modelled transmission loss (dB)")
a1.set_title("Airgun shots, 2001: the misfit grows with frequency at both stations", loc="left", fontsize=8)
a1.legend(frameon=False, fontsize=6.3, loc="upper left")
a1.text(-0.12, 1.06, "a", transform=a1.transAxes, fontweight="bold", fontsize=10)
shots = [s for s in B.shot.unique()]
k = 0
for s in shots:
    a = B[(B.shot == s) & (B.station == "H01W")].set_index("fc_hz").implied_sl_db
    b = B[(B.shot == s) & (B.station == "H08S")].set_index("fc_hz").implied_sl_db
    fb = [f for f in a.index if f in b.index and np.isfinite(a[f]) and np.isfinite(b[f])]
    if len(fb) >= 3:
        a2.plot(fb, [a[f] - b[f] for f in fb], marker="o", ms=3.5, lw=1.0, label=s.replace("sus", " SUS ").replace(" SUS 2b", " SUS 2, second").replace(" SUS 2", " SUS 610 m").replace(" SUS 3", " SUS 915 m"))
        k += 1
a2.axhline(0, color="0.5", lw=0.7); a2.axhspan(-3, 3, color="0.9", lw=0, zorder=0)
a2.set_xscale("log"); a2.set_xticks([25, 31.5, 40, 50, 63]); a2.set_xticklabels(["25", "31.5", "40", "50", "63"]); a2.minorticks_off()
a2.set_xlim(22, 70); a2.set_ylim(-10, 10)
a2.set_xlabel("Frequency (Hz)"); a2.set_ylabel("Cape Leeuwin minus Diego Garcia South (dB)")
a2.set_title(f"Deep charges, 2003: station difference within 5 dB ({k} shots)", loc="left", fontsize=8)
a2.legend(frameon=False, fontsize=6.3, loc="upper left")
a2.text(-0.12, 1.06, "b", transform=a2.transAxes, fontweight="bold", fontsize=10)
ste = ("What the chart shows. (a) Airgun shots in 2001 were recorded at two stations. The model gives too much loss at low frequency and "
       "too little at high frequency, at both stations. A source that sends less sound sideways at high frequency (open markers) removes "
       "about two thirds of the change with frequency, but leaves the model 2 to 5 dB too lossy. (b) Small charges at 610 m and 915 m in 2003 were recorded at both stations. The difference between "
       "the stations agrees with the model within 5 dB above 30 Hz, and its median is within 3 dB. Below 30 Hz the charges were too weak to see at both stations at once. The grey band is ±3 dB.")
tech = ("Technical. (a) r_b = TL_obs − TL_model, Blackman et al. 2004 Fig. 23 (p. 21) as digitised by the module (±2 dB), KRAKEN "
        "adiabatic incoherent modes, hard half-space, 10 m source; M3 = 4 × 5 planar array, 24 × 16 m, azimuth mean, horizontal (geometry "
        "proxy, not Ewing's). Slopes (dB/octave): flat 10.4 (H01W), 7.4 (H08S); M3 3.7, 3.0. (b) d_b = [S_b + TL_b](H01W) − [S_b + TL_b](H08S), "
        "S_b = noise-subtracted signal PSD from Blackman App. B (pp. 28–31) traced by the audit, bands with SNR ≥ 3 dB at both stations; "
        "module propagation on audit-built paths (GEBCO_2026, WOA23 95A4 May/June).")
fig.text(0.01, 0.22, textwrap.fill(ste, 200), fontsize=6.0, va="top", color="0.35")
fig.text(0.01, 0.12, textwrap.fill(tech, 235), fontsize=5.2, va="top", color="0.35")
fig.savefig(out + ".png", dpi=300); fig.savefig(out + ".pdf")
