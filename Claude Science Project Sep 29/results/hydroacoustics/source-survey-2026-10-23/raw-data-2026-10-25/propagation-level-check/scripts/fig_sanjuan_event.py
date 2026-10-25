
"""Figure: San Juan loss event, explosion-equivalent yield and radiated energy inverted through the module chain, as a function of source depth."""
import numpy as np, pandas as pd, matplotlib.pyplot as plt
exec(open("scripts/footnotes.py").read())
w = pd.read_csv("out/sanjuan_event_tnt_equivalent.csv"); e = pd.read_csv("out/sanjuan_event_energy_vs_depth.csv"); ch = pd.read_csv("out/source_inversion.csv")
fig, axs = plt.subplots(1, 2, figsize=(7.2, 4.4))
C = {"H10N": "#1f5fa8", "H10S": "#c46a1b"}; NM = {"H10N": "Ascension North", "H10S": "Ascension South"}
ax = axs[0]
for tri in ("H10N", "H10S"):
    for smod, ls, lab in (("GS_construction", "-", "construction"), ("GS_table3_1p8lb_800ft", "--", "table, 1.8 lb at 800 ft")):
        g = w[(w.triad == tri) & (w.source == smod) & (w.chain == "KRAKEN")].sort_values("z_m"); ax.plot(g.z_m, g.W_eq_kg, color=C[tri], ls=ls, lw=1.3, label=f"{NM[tri]}, {lab}")
        r = w[(w.triad == tri) & (w.source == smod) & (w.chain == "RAM")]; ax.plot(r.z_m, r.W_eq_kg, "o", color=C[tri], ms=4, mfc="white" if ls == "--" else C[tri])
    # charge-relative route
    Ec = ch[(ch.event == "sj_charge") & (ch.triad == tri) & (ch.model == "KRAKEN")].E_rad_5_40_J.iloc[0]
    g = e[(e.triad == tri) & (e.chain == "KRAKEN")].sort_values("z_m"); ax.plot(g.z_m, 108 * g.E_rad_5_40_J / Ec, color=C[tri], ls=":", lw=1.2, label=f"{NM[tri]}, charge-relative energy")
ax.axhline(428, color="0.3", lw=1); ax.text(205, 480, "Heyburn et al. 2020: 428 kg", fontsize=6, color="0.3")
ax.axvline(920, color="0.6", lw=0.8, ls="-."); ax.text(905, 6, "wreck depth", rotation=90, fontsize=6, color="0.5", ha="right", va="bottom")
ax.set_yscale("log"); ax.set_xlabel("Assumed source depth (m)"); ax.set_ylabel("Explosion-equivalent yield (kg TNT)")
ax.set_title("Yield depends mostly on the assumed depth", loc="left"); ax.set_xlim(180, 960); ax.set_ylim(3, 3000); LA = ax.get_legend_handles_labels()
ax = axs[1]
for tri in ("H10N", "H10S"):
    g = e[(e.triad == tri) & (e.chain == "KRAKEN")].sort_values("z_m"); ax.plot(g.z_m, g.E_rad_5_40_J, color=C[tri], lw=1.3, label=f"{NM[tri]}, normal modes")
    r = e[(e.triad == tri) & (e.chain == "RAM")]; ax.plot(r.z_m, r.E_rad_5_40_J, "o", color=C[tri], ms=4, label=f"{NM[tri]}, with parabolic equation")
zz = np.linspace(200, 900, 50)
for V, ls in ((10, ":"), (100, "--")):
    ax.plot(zz, 0.01 * 1025 * 9.81 * zz * V, color="0.55", ls=ls, lw=0.9); ax.text(905, 0.01 * 1025 * 9.81 * 900 * V, f" 1 % of pV,\n V = {V} m³", fontsize=5.5, color="0.4", va="center")
ax.set_yscale("log"); ax.set_xlabel("Assumed source depth (m)"); ax.set_ylabel("Radiated acoustic energy, 5-40 Hz (J)")
ax.set_title("Radiated energy against implosion energy", loc="left"); ax.set_xlim(180, 1080); LB_ = ax.get_legend_handles_labels()
for a, L in zip(axs, "ab"): panel_letter(a, L)
fig.tight_layout(rect=(0, 0.36, 1, 1)); fig.legend(*LA, loc="upper left", bbox_to_anchor=(0.06, 0.37), ncol=2, fontsize=5.5, frameon=False); fig.legend(*LB_, loc="upper left", bbox_to_anchor=(0.56, 0.37), ncol=2, fontsize=5.5, frameon=False)
ste = ("(i) The submarine ARA San Juan was lost on 15 November 2017. We put the recorded sound back through the model to the source. The answer changes most "
       "with the depth of the source, which is not known. Near the wreck depth some model choices give the published 428 kg and others give 80 to 170 kg. At 500 m all results are lower. "
       "Panel b compares the sound energy with the energy of a collapsing air space of 10 or 100 cubic metres.")
tech = ("(ii) Raw IM.H10N1-3 / H10S2-3, 60 s window at the 14:58-14:59 UTC arrival, bands 5-40 Hz with SNR >= 3 dB; SL_b = ESD_b + TL_b, wreck 45.950 S 59.773 W "
        "(Vergoz 2021), WOA23 B5C2 November, KRAKEN 200-900 m, RAM 500/900 m. Yield = W for which a G&S 1971 charge at that depth radiates the same 5-40 Hz energy "
        "(construction; Table 3 1.8 lb/800 ft by similitude); dotted = event/charge energy ratio x 108 kg (path error cancels); panel a lines = normal modes, points = with parabolic equation (filled construction, open table). Explosion-equivalent label only: "
        "mechanism not known. E = 4 pi/(rho c) sum SL_b BW_b, rho c 1.54e6; pV with rho g z. Station difference ~4x (same as for the charge).")
footnotes(fig, ste, tech, top=0.2)
fig.savefig("out/fig_sanjuan_event_source.png", dpi=200)
