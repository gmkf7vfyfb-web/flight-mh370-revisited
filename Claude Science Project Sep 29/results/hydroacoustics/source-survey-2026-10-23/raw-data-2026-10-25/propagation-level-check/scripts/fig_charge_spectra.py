
"""Figure: San Juan calibration charge, measured vs predicted band ESD at H10N and H10S (raw IMS)."""
import numpy as np, pandas as pd, matplotlib.pyplot as plt, textwrap, matplotlib.ticker as mt
B = [5.0, 6.3, 8.0, 10.0, 12.5, 16.0, 20.0, 25.0, 31.5, 40.0]
tb = pd.read_csv("out/triad_bands.csv"); tb = tb[(tb.window == "W60") & (tb.event == "sj_charge")]
res = pd.read_csv("out/residuals.csv"); res = res[(res.event == "sj_charge") & (res.src_depth_m == 33.0) & res.path.str.contains("V-")]
ni = pd.read_csv("out/nielsen_fig5c_vs_raw.csv")
fig, axs = plt.subplots(1, 2, figsize=(7.2, 4.2), sharey=True)
C = {"RAM": "#1f5fa8", "KRAKEN": "#7aa6d6"}
for ax, tri, name in zip(axs, ("H10N", "H10S"), ("Ascension North (5,989 km)", "Ascension South (5,881 km)")):
    m = tb[tb.triad == tri].set_index("fc_hz"); f = np.array([x for x in m.index if 4 <= x <= 50])
    bw = f * (2 ** (1 / 6) - 2 ** (-1 / 6)); noise = 10 * np.log10(m.E_noise[f] / bw) + 120
    ax.plot(f, noise, color="0.6", lw=1, ls=":", label="background (median of 10 windows)")
    ax.errorbar(f, m.esd_dB[f], yerr=[m.esd_dB[f] - m.esd_dB_lo[f], m.esd_dB_hi[f] - m.esd_dB[f]], fmt="o", color="k", ms=4, capsize=2, label="measured, raw records", zorder=5)
    for model in ("RAM", "KRAKEN"):
        for smod, ref, ls, lab in (("SA_GS_construction", np.nan, "-", "Gaspin-Shuler construction"), ("SB_GS_table3_similitude", "e_3lb_60ft", "--", "Gaspin-Shuler table, scaled")):
            r = res[(res.triad == tri) & (res.model == model) & (res.source_model == smod) & ((res.source_ref == ref) if isinstance(ref, str) else res.source_ref.isna())].sort_values("fc_hz")
            ax.plot(r.fc_hz, r.pred_esd_dB, color=C[model], ls=ls, lw=1.4 if model == "RAM" else 0.9, label=f"predicted: {lab}, {'normal modes + parabolic equation' if model=='RAM' else 'normal modes only'}")
    if tri == "H10N":
        ax.plot(ni.fc_hz, ni.nielsen_sig_minus_noise_psd_dB + 10, color="#c0392b", marker="x", lw=0.8, ls="-.", label="published spectrum (digitised), +10 log10(10 s)")
    ax.set_xscale("log"); ax.set_xticks([5, 10, 20, 40]); ax.set_xticklabels(["5", "10", "20", "40"]); ax.xaxis.set_minor_formatter(mt.NullFormatter()); ax.set_xlabel("Third-octave band centre (Hz)")
    ax.set_title(name, loc="left")
axs[0].set_ylabel("Energy spectral density\n(dB re 1 µPa² s/Hz)")
h, l = axs[0].get_legend_handles_labels(); fig.legend(h, l, loc="lower center", ncol=2, fontsize=6, frameon=False, bbox_to_anchor=(0.5, 0.215))
for a, L in zip(axs, "ab"): panel_letter(a, L)
fig.tight_layout(rect=(0, 0.38, 1, 1))
ste = ("(i) A 108 kg charge exploded at 33 m in the South Atlantic on 1 December 2017. The black dots are the sound energy that the Ascension Island "
       "hydrophones recorded. The blue lines are what the model calculates. The two blue line types use two source models. Their levels differ by 3.7 to 5.3 dB. "
       "The red line is the older value from a digitised chart. It is too low by about 7 dB because it assumed a 10 s signal. The true average time was about 50 s.")
tech = ("(ii) Raw IM.H10N1-3 / H10S2-3 (H10S1 excluded, ~30 dB low), response removed; 60 s window on the 2-40 Hz envelope peak; FFT ESD in base-2 third octaves, "
        "noise (10 x 60 s median) subtracted, bars = noise 16-84 %. Source 108 kg TNT at 33 m, 45.666 S 59.240 W (Vergoz 2021); G&S 1971 construction (kappa 4, sin^2) "
        "or Table 3 3 lb/60 ft by similitude, +191.1 dB; both outside G&S validity (<= few lb). TL: KRAKEN adiabatic incoherent / RAM, hard half-space "
        "(1650 m/s, 1.9, 0.5 dB/lambda), GEBCO_2026, WOA23 B5C2 December, Francois-Garrison, spherical correction, 2-D geodesic (no N x 2D at the Rio Grande Rise). "
        "Red: Nielsen 2021 Fig 5c digitised, noise removed, PSD + 10 log10(10 s) as in stage 1b.")
exec(open("scripts/footnotes.py").read()); footnotes(fig, ste, tech, top=0.17)
fig.savefig("out/fig_charge_spectra.png", dpi=200)
