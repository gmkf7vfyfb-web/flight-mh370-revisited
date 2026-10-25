
"""Figure: measured minus predicted band level for all known-energy explosions and the fitted frequency slopes, against the airgun slope misfit."""
import numpy as np, pandas as pd, matplotlib.pyplot as plt, matplotlib.ticker as mt
exec(open("scripts/footnotes.py").read())
st = pd.read_csv("out/sigma_model_table.csv"); S = pd.read_csv("out/scores_primary.csv")
fig, axs = plt.subplots(1, 2, figsize=(7.2, 4.4), gridspec_kw=dict(width_ratios=[1.25, 1]))
COL = {"San Juan charge": "#1f5fa8", "FSST 2016": "#d08c2b", "FSST 2021": "#6b4c9a"}
def grp(e): return "San Juan charge" if e == "sj_charge" else ("FSST 2016" if e.startswith("fsst16") else "FSST 2021")
ax = axs[0]; d = st[(st.chain == "MODULE_KRAKEN_ONLY") & (st.source == "GS_construction")]
for (ev, tri), g in d.groupby(["event", "triad"]):
    g = g.sort_values("fc_hz"); G = grp(ev)
    ax.plot(g.fc_hz, g.resid_dB, color=COL[G], ls="-" if tri == "H10N" else "--", lw=1.6 if ev == "sj_charge" else 0.8, alpha=1 if ev == "sj_charge" else 0.75, marker="o" if ev == "sj_charge" else None, ms=3)
f = np.array([5, 40.0])
for s, lab in ((10.4, "airgun misfit, Cape Leeuwin"), (7.4, "airgun misfit, Diego Garcia South")):
    ax.plot(f, s * np.log2(f / 14.1), color="0.55", ls=":", lw=1); ax.text(40, s * np.log2(40 / 14.1), f" +{s} dB/oct", fontsize=6, color="0.4", va="center")
ax.axhline(0, color="k", lw=0.6); ax.set_xscale("log"); ax.set_xticks([5, 10, 20, 40]); ax.set_xticklabels(["5", "10", "20", "40"]); ax.xaxis.set_minor_formatter(mt.NullFormatter())
ax.set_xlabel("Third-octave band centre (Hz)"); ax.set_ylabel("Measured minus predicted (dB)"); ax.set_xlim(4.5, 60); ax.set_ylim(-19, 17)
ax.set_title("Explosions: offsets and curvature, no steady rise", loc="left")
from matplotlib.lines import Line2D
h = [Line2D([], [], color=c, lw=1.4, label=k) for k, c in COL.items()] + [Line2D([], [], color="k", ls="-", label="Ascension North"), Line2D([], [], color="k", ls="--", label="Ascension South"), Line2D([], [], color="0.55", ls=":", label="airgun slope misfit (2001)")]
ax.legend(handles=h, fontsize=6, frameon=False, loc="lower right", ncol=2, bbox_to_anchor=(1.0, 0.0))
ax = axs[1]; S = S.copy(); S["G"] = S.event.map(grp)
lab = {("MODULE_KRAKEN_ONLY", "GS_construction"): "normal modes, construction", ("MODULE_KRAKEN_ONLY", "GS_table3_1p8lb_300ft"): "normal modes, table scaled",
       ("MODULE_KRAKEN_RAM", "GS_construction"): "with parabolic eq., construction", ("MODULE_KRAKEN_RAM", "GS_table3_1p8lb_300ft"): "with parabolic eq., table scaled"}
for i, (k, name) in enumerate(lab.items()):
    g = S[(S.chain == k[0]) & (S.source == k[1])]
    for j, (_, r) in enumerate(g.iterrows()):
        y = i + (j - len(g) / 2) * 0.035
        ax.errorbar(r.slope_dB_per_oct, y, xerr=1.96 * r.slope_se, fmt="o" if r.triad == "H10N" else "s", ms=3, color=COL[r.G], elinewidth=0.6, mfc=COL[r.G] if r.triad == "H10N" else "white")
ax.axvspan(-1.5, 1.5, color="#5a9e5a", alpha=0.12, lw=0); ax.axvspan(-3, -1.5, color="#e0c050", alpha=0.12, lw=0); ax.axvspan(1.5, 3, color="#e0c050", alpha=0.12, lw=0)
for s in (10.4, 7.4): ax.axvline(s, color="0.55", ls=":", lw=1)
ax.text(8.9, 3.55, "airgun\nmisfit", fontsize=6, color="0.4", ha="center")
ax.set_yticks(range(4)); ax.set_yticklabels(list(lab.values()), fontsize=6); ax.set_xlabel("Residual frequency slope (dB per octave), 95 % interval")
ax.set_title("No explosion shows the airgun slope", loc="left"); ax.set_xlim(-6, 12); ax.set_ylim(-0.6, 4.0)
for a, L in zip(axs, "ab"): panel_letter(a, L)
fig.tight_layout(rect=(0, 0.25, 1, 1))
ste = ("(i) Each line is one explosion seen at one Ascension Island station: measured sound minus model sound in each band. "
       "They are offset up or down by a level that changes from event to event, and the Florida lines bend down at 5 Hz and 40 Hz. They do not rise steadily with frequency. The dotted lines show how steep the error was for the 2001 airguns. "
       "Panel b gives the slope of each line. All slopes are between -4 and +3 dB per octave. The airgun slopes were +7 and +10.")
tech = ("(ii) 17 event-station pairs (charge 1 x 2 stations; FSST 2016 5 shots H10N, 4 H10S; FSST 2021 3 x 2), raw IM.H10 EDH, H10S1 excluded; 60 s window; "
        "bands with SNR >= 3 dB. Panel a: KRAKEN adiabatic, G&S 1971 construction. Panel b: OLS slope of r_b on log2 f, +/-1.96 SE; filled = H10N, open = H10S; RAM run for "
        "charge and FSST shots 2016-1, 2021-1 only. Charge 108 kg/33 m; FSST 6,759/18,000 kg at 61 m (depth not published for 2016/2021; 2008 FSST value). "
        "Shading: slope PASS 1.5, PARTIAL 3 dB/oct (criteria.md C1). Airgun values: audit C1 (flat source). Exploratory, written in advance.")
footnotes(fig, ste, tech, top=0.205)
fig.savefig("out/fig_residuals_slopes.png", dpi=200)
