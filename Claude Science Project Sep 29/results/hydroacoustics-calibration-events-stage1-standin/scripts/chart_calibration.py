import json, numpy as np, pandas as pd, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt, matplotlib.ticker
M = "../hy/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/results-data"
tl = pd.read_csv("tl/event_tl.csv"); f = pd.read_csv(f"{M}/f35a_cal/f35a_tl.csv")
g = pd.read_csv("q1/af447_q1_grid.csv"); sj = pd.read_csv("sanjuan_h10n_implied_source.csv")
plt.rcParams.update({"font.size": 9, "axes.titlesize": 9.5, "axes.labelsize": 9, "legend.fontsize": 7.5})
fig = plt.figure(figsize=(13, 7.4))
ax = [fig.add_axes([0.055 + i * 0.33, 0.33, 0.27, 0.56]) for i in range(3)]
cA = {2.0: "#9ecae1", 10.0: "#3182bd", 30.0: "#08519c"}
for z, c in cA.items():
    h = tl[(tl.path == "af447-H10S") & np.isclose(tl.src_depth_m, z)]
    ax[0].plot(h.fc_hz, h.tl_db, "-o", ms=3, color=c, label=f"Air France 447 to Ascension south, source {z:g} m")
h = tl[(tl.path == "sanjuan-charge-H10N") & np.isclose(tl.src_depth_m, 33.0)]
ax[0].plot(h.fc_hz, h.tl_db, "--s", ms=3, color="#d95f02", label="Navy charge to Ascension north, 33 m (provisional)")
for st, ls in (("H11N", ":"), ("H11S", "-.")):
    h = f[(f.station == st) & np.isclose(f.src_depth_m, 10.0)]
    ax[0].plot(h.fc_hz, h.tl_db, ls, color="0.35", label=f"F-35A to Wake Island {st[-1]}, 10 m (reference)")
ax[0].set_xscale("log"); ax[0].set_xticks([5, 10, 20, 40]); ax[0].set_xticklabels(["5", "10", "20", "40"]); ax[0].xaxis.set_minor_formatter(matplotlib.ticker.NullFormatter())
ax[0].set_xlabel("Frequency (Hz)"); ax[0].set_ylabel("Transmission loss (dB)"); ax[0].set_ylim(166, 104)
ax[0].set_title("A. Sound loss along each path (more loss is lower)"); ax[0].legend(loc="lower left", frameon=False)
for conv, ls in (("total KE", "-"), ("vertical KE", "--")):
    for z, c in cA.items():
        h = g[(g.convention == conv) & np.isclose(g.src_depth_m, z)]
        ax[1].plot(h.tau_s, h.delta_ratio_mean_db, ls, color=c, label=f"{'total' if conv == 'total KE' else 'vertical'} energy, source {z:g} m")
ax[1].axhspan(-6, 6, color="#c7e9c0", alpha=0.6, lw=0); ax[1].axhspan(6, 10, color="#fee391", alpha=0.6, lw=0); ax[1].axhspan(-10, -6, color="#fee391", alpha=0.6, lw=0)
ax[1].axhline(0, color="0.4", lw=0.6)
ax[1].text(0.06, 1.0, "within ±6 dB", fontsize=7.5, color="#238b45"); ax[1].text(0.06, 7.2, "6–10 dB", fontsize=7.5, color="#b8860b")
ax[1].set_xscale("log"); ax[1].set_ylim(-12, 26)
ax[1].set_xlabel("Assumed source duration τ (s)"); ax[1].set_ylabel("Upper bound on coupling difference Δ (dB)")
ax[1].set_title("B. Air France 447: upper bound on coupling\nrelative to the F-35A (signal not detected)"); ax[1].legend(loc="lower right", frameon=False, ncol=1)
h = sj[np.isclose(sj.src_depth_m, 33.0)]
x = np.log2(h.fc_hz / 25.0); cfit = np.polyfit(x, h.implied_sl_db, 1)
ax[2].plot(h.fc_hz, h.implied_sl_db, "s", color="#d95f02", label="Received level + modelled loss, source 33 m")
ax[2].plot(h.fc_hz, np.polyval(cfit, x), "-", color="#d95f02", lw=0.8, label=f"Least-squares line, slope {cfit[0]:+.1f} dB per octave")
for _, r in h.iterrows():
    ax[2].annotate(f"{int(r.n_modes_min)}", (r.fc_hz, r.implied_sl_db), textcoords="offset points", xytext=(0, 6), ha="center", fontsize=7, color="0.3")
ax[2].set_xscale("log"); ax[2].set_xticks([5, 10, 20, 40]); ax[2].set_xticklabels(["5", "10", "20", "40"]); ax[2].xaxis.set_minor_formatter(matplotlib.ticker.NullFormatter())
ax[2].set_xlabel("Frequency (Hz)"); ax[2].set_ylabel("Implied source spectral level (dB re 1 µPa² m²/Hz)")
ax[2].set_title("C. Navy charge (provisional, plain 2-D): source level\nthe model needs (numbers: fewest modes on the path)")
ax[2].legend(loc="lower left", frameon=False); ax[2].set_ylim(205, 219)
fig.text(0.5, 0.965, "Calibration events, stage 1 (stand-in run of the module's recipe). Not a likelihood. Run C sensitivity in the same note is UNCONVERGED.",
         ha="center", fontsize=10, weight="bold")
ste = ("STE100: Panel A shows how much sound the model loses between each event and the hydrophone. Panel B: the Air France 447 signal was not seen above the noise in the "
       "published figure, so the panels give only a maximum. If the crash put the same part of its energy into sound as the F-35A, the model "
       "predicts a peak of about 0.13 Pa, which is below the noise. To see a peak, the crash must put about 20 dB (100 times) more of its energy into sound than the F-35A. "
       "So this event does not test the ±6 dB or ±10 dB limits. Panel C: a ridge (Rio Grande Rise) is on the path; the result is not final.")
tech = ("Technical: KRAKEN adiabatic normal modes, incoherent sum, hard fluid half-space (cp 1650 m/s, ρ 1.9, 0.5 dB/λ), Francois–Garrison, spherical correction, third-octave 5–40 Hz; "
        "GEBCO_2026 3×3 median + WOA23 (A5B4 June; B5C2 Dec), ocean-transport sections dafb0d1. B: Δ_ratio = 10log10[(p_e/p_F)²(E_F/E_e)G_F/G_e] (prereg 23add102 am. 1), "
        "p_e = 0.914 Pa (Kadri 2024 Fig. 5a, SNR 1.32, upper limit), p_F = 1.15/1.22 Pa (Fig. 4a, mean of H11N/H11S Δ), E_F = 900 MJ, E_e = 625 MJ total / 315 MJ vertical (BEA), band fraction slope 2, "
        "τ grid 0.05–10 s. On 86% of the AF447 path the critical depth is absent or below the seabed, so the TL depends on the bottom model. "
        "C: Nielsen et al. 2021 Fig. 5c (module digitisation), noise subtracted in power; PSD ordinate, so the source unit needs Nielsen's window before an absolute check. "
        "Rise at 2,590–2,672 km (track 674 m, channel axis ~850 m): needs N×2D; H04S path not yet built, so the pre-registered station difference is not computable.")
import textwrap
fig.text(0.015, 0.225, textwrap.fill(ste, 228), fontsize=7.3, va="top")
fig.text(0.015, 0.135, textwrap.fill(tech, 240), fontsize=7.0, va="top", color="0.2")
fig.savefig("hydroacoustics-calibration-events-stage1-standin.png", dpi=160); fig.savefig("hydroacoustics-calibration-events-stage1-standin.pdf")
