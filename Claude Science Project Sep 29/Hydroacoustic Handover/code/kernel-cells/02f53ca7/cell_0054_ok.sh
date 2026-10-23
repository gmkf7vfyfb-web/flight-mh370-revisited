cd "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare"; cat > tl_recal_block9_charts.py <<'EOF'
"""Charts for block 9 (TL recalibration): (1) predicted vs measured received level per station with the EW0112 source,
(2) residual vs frequency with and without common-mode removal, (3) air7 -> H01W corridor sensitivity.
Usage: python tl_recal_block9_charts.py <results-data/tl_recal_block9> <results_out_dir>
Chart rule (10 Oct 2026): no project jargon in titles, axes or legends; two footnotes (plain, technical)."""
import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

BLUE, ORANGE, GREY, GREEN, RED = "#1f4e9c", "#c8761d", "#7f7f7f", "#2a8a5c", "#b03a2e"


def footnotes(fig, plain, tech, y0=0.005):
    fig.text(0.01, y0 + 0.075, plain, fontsize=6.3, color="#444", ha="left", va="bottom", wrap=True)
    fig.text(0.01, y0, tech, fontsize=6.3, color="#444", ha="left", va="bottom", wrap=True)


def wrapt(s, n=190):
    import textwrap
    return "\n".join(textwrap.wrap(s, n))


def chart1(D, out):
    R = pd.read_csv(D / "route1_residuals.csv"); G = pd.read_csv(D / "route1_grades.csv"); V = json.load(open(D / "route1_verdict.json"))
    base = R[(R.zs == 10.0) & (R.weights == "V^(1/3)") & (R.sign == 1) & (R.xh == 30) & (R.zh == 15) & (R.ball == "both")]
    fig, axes = plt.subplots(1, 2, figsize=(10.5, 5.6), sharey=True)
    for ax, st, name in zip(axes, ("H01W", "H08S"), ("Cape Leeuwin (H01W), 1,663 km", "Diego Garcia South (H08S), 3,549 km")):
        n = base[(base.station == st) & (base.SL_B == 235.0)].sort_values("fc_hz")
        lo = base[(base.station == st) & (base.SL_B == 230.0)].sort_values("fc_hz").rl_obs_db.values
        hi = base[(base.station == st) & (base.SL_B == 240.0)].sort_values("fc_hz").rl_obs_db.values
        ax.fill_between(n.fc_hz, lo, hi, color=GREY, alpha=0.25, lw=0, label="measured, range for a 230–240 dB source peak level")
        ax.plot(n.fc_hz, n.rl_obs_db, "o-", color=GREY, mec="k", label="measured (chart-read, 235 dB source peak level)")
        ax.plot(n.fc_hz, n.rl_pred_db, "s-", color=BLUE, label="predicted: near-source spectrum + array pattern − modelled loss")
        g = G[(G.station == st) & G.nominal].iloc[0]
        ax.set_title(f"{name}\nslope of the difference {g.slope:+.1f} ± {g.slope_se:.1f} dB/oct ({g.g_slope.lower()}), level {g.level:+.0f} dB ({g.g_level.lower()})", fontsize=9, loc="left")
        ax.set_xscale("log"); ax.set_xticks([6.3, 10, 16, 25, 40, 63]); ax.set_xticklabels(["6.3", "10", "16", "25", "40", "63"]); ax.minorticks_off()
        ax.set_xlabel("Frequency (Hz)"); ax.grid(alpha=0.25); ax.margins(0.06)
    axes[0].set_ylabel("Received level (dB; measured = source peak level − chart-read loss)")
    axes[0].legend(fontsize=7, frameon=False, loc="lower left")
    fig.suptitle("Airgun shots of October 2001 (site air9): predicted against measured received level at the two IMS stations, with the\nsource spectrum taken from the ship's own near-source recording", fontsize=10.5, x=0.01, ha="left")
    fig.subplots_adjust(top=0.84, bottom=0.30, left=0.08, right=0.98, wspace=0.08)
    plain = wrapt("What the chart shows: for one set of airgun shots fired in 2001, the sound level we predict at two listening stations (blue) against the level "
                  "that was measured (grey). The source level now comes from a recording made next to the airguns on the ship. The slope of the two curves "
                  "now agrees (within 3 dB per octave); the vertical offset does not, but the measured level is a peak level and the predicted level is a "
                  "spectrum level, so the offset cannot be read as an error. Verdict under the rule fixed before the calculation: NOT EXPLAINED (the level test fails). "
                  f"Caveats C1 and C2 apply to every number.")
    tech = wrapt("Technical: RL_pred = S0 + AF − TL; S0 = EW0112 Fig. 2 Ball spectrum (DIGITISED, two shots, dB mean) + 20 log10(25.75 m) − near-field reference factor "
                 "(OFR 95-228 20-gun layout, V^(1/3) weights, Ball 30 m ahead, 15 m deep, source 10 m); AF = horizontal array factor toward the station; TL = KRAKEN "
                 "adiabatic incoherent modes, hard bottom, Francois-Garrison, shared GEBCO_2026/WOA23 (Oct) sections, receiver at triad depth. RL_obs = SL_B − TL_obs(Fig. 23, "
                 "DIGITISED ±2 dB), SL_B = 235 (230–240 band). Bands: Fig. 23 span ∩ Fig. 2 readable (40 Hz excluded). Grades: audit criteria.md 940f1a3. Pre-registration "
                 f"e949144 (tl_recal_block9.py). Verdict {V['verdict']}; slope grid fraction {V['grid_fraction_slope_both_ok']:.2f} of 45. No MH370 impact posterior enters this chart "
                 "(calibration event only; run J is the impact set the module predicts for). C1: propagation slope misfit (+10.4/+7.4 dB/oct uncorrected); C2: coupling η not calibrated.")
    footnotes(fig, plain, tech)
    fig.savefig(out / "hydroacoustics-air9-ew0112-predicted-vs-measured.png", dpi=200); fig.savefig(out / "hydroacoustics-air9-ew0112-predicted-vs-measured.pdf")
    return fig


def chart2(D, out, audit_resid):
    R = pd.read_csv(D / "route1_residuals.csv"); CM = pd.read_csv(D / "route1_common_mode_residuals.csv"); CG = pd.read_csv(D / "route1_common_mode_grades.csv")
    G = pd.read_csv(D / "route1_grades.csv")
    sel = dict(zs=10.0, weights="V^(1/3)", sign=1, xh=30, zh=15, ball="both", SL_B=235.0)
    def pick(df):
        m = np.ones(len(df), bool)
        for k, v in sel.items():
            m &= (df[k] == v).values
        return df[m]
    Rn, CMn, CGn = pick(R), pick(CM), pick(CG)
    A = pd.read_csv(audit_resid); A = A[(A.model == "M1") & (A.src_depth_m == 10.0)]
    fig, axes = plt.subplots(1, 3, figsize=(12.5, 5.4), sharey=True)
    cols = {"H01W": BLUE, "H08S": ORANGE}
    ax = axes[0]
    for st in ("H01W", "H08S"):
        a = A[A.station == st].sort_values("fc_hz"); ax.plot(a.fc_hz, -a.residual_db, "o--", color=cols[st], alpha=0.55, mfc="none", label=f"{st}, flat source (before)")
        n = Rn[Rn.station == st].sort_values("fc_hz"); ax.plot(n.fc_hz, n.r_db - n.r_db.median(), "o-", color=cols[st], label=f"{st}, near-source spectrum (now)")
        g = G[(G.station == st) & G.nominal].iloc[0]
        x = np.log2(n.fc_hz); c = np.polyfit(x, n.r_db - n.r_db.median(), 1); ax.plot(n.fc_hz, np.polyval(c, x), "-", color=cols[st], lw=0.8, alpha=0.6)
        ax.text(n.fc_hz.iloc[-1] * 1.05, np.polyval(c, x.iloc[-1]), f"{g.slope:+.1f} ± {g.slope_se:.1f} dB/oct", fontsize=7, color=cols[st], va="center")
    ax.set_title("a  Measured − predicted, level removed:\n   the tilt is gone once the source spectrum is used", fontsize=9, loc="left")
    ax.set_ylabel("Measured minus predicted received level, median removed (dB)")
    ax.legend(fontsize=7, frameon=False, loc="upper left")
    ax = axes[1]
    for st in ("H01W", "H08S"):
        c = CMn[CMn.station == st].sort_values("fc_hz"); ax.plot(c.fc_hz, c.r_tilde_db, "o-", color=cols[st], label=f"{st}")
        g = CGn[(CGn.station == st)].iloc[0]
        ax.text(c.fc_hz.iloc[-1] * 1.05, c.r_tilde_db.iloc[-1], f"{g.slope:+.1f} ± {g.slope_se:.1f} dB/oct", fontsize=7, color=cols[st], va="center")
    ax.set_title("b  After removing the part common to both stations\n   (the path-only view): within 2 dB", fontsize=9, loc="left"); ax.legend(fontsize=7, frameon=False)
    ax = axes[2]
    c = CMn[CMn.station == "H01W"].sort_values("fc_hz"); cm = c.common_mode_db - c.common_mode_db.median()
    ax.plot(c.fc_hz, cm, "D-", color=GREEN, label="common part, near-source spectrum (now)")
    sh = A.pivot(index="fc_hz", columns="station", values="residual_db").dropna(); shm = -sh.mean(axis=1); shm = shm.loc[[f for f in shm.index if f in set(c.fc_hz)]]
    ax.plot(shm.index, shm - shm.median(), "D--", color=GREEN, alpha=0.5, mfc="none", label="common part, flat source (before)")
    g = CGn[CGn.station == "both"].iloc[0]
    ax.text(c.fc_hz.iloc[-1] * 1.05, cm.iloc[-1], f"{g.slope:+.1f} ± {g.slope_se:.1f} dB/oct", fontsize=7, color=GREEN, va="center")
    ax.set_title("c  The part common to both stations\n   (source-side term), median removed", fontsize=9, loc="left"); ax.legend(fontsize=7, frameon=False, loc="upper left")
    for ax in axes:
        ax.set_xscale("log"); ax.set_xticks([6.3, 10, 16, 25, 40, 63]); ax.set_xticklabels(["6.3", "10", "16", "25", "40", "63"]); ax.minorticks_off()
        ax.set_xlabel("Frequency (Hz)"); ax.grid(alpha=0.25); ax.axhline(0, color="k", lw=0.6); ax.margins(x=0.12, y=0.08)
    fig.suptitle("Airgun shots of October 2001 (site air9): the frequency tilt of the misfit, before and after the source spectrum from the ship's near-source recording", fontsize=10.5, x=0.01, ha="left")
    fig.subplots_adjust(top=0.85, bottom=0.30, left=0.07, right=0.99, wspace=0.08)
    plain = wrapt("What the chart shows: how far the predicted sound level is from the measured one at each frequency, at two listening stations. (a) With a flat source the "
                  "misfit tilted strongly with frequency (dashed); with the measured near-source spectrum the tilt is within 3 dB per octave (solid). (b) The part of the misfit "
                  "that differs between the two stations is within 2 dB. (c) The part shared by both stations, which is the source-side term, is now flat to about 1 dB per octave. "
                  "The vertical offset is not shown (it mixes a peak level with a spectrum level). Caveats C1 and C2 apply.")
    tech = wrapt("Technical: r_b = RL_obs − RL_pred (dB; audit sign reversed: here r > 0 means the model under-predicts the signal), nominal geometry (z_s 10 m, Ball 30 m ahead, "
                 "15 m deep, OFR 95-228 layout, V^(1/3) weights, SL_B 235). 'Before' = −(TL_obs − TL_model) of audit M1 (flat source). Common mode c_b = mean of r_b over the two "
                 "stations on the 7 shared bands (12.5–63 Hz, 40 Hz excluded); r~_b = r_b − c_b. OLS slopes on log2 f with standard errors; grades per criteria.md 940f1a3. "
                 "Sources DIGITISED: Blackman 2004 Fig. 23, EW0112 Fig. 2. Pre-registration e949144; verdict NOT EXPLAINED (level test). No MH370 posterior enters; "
                 "C1 (slope misfit) and C2 (η not calibrated) stay on every MH370 number.")
    footnotes(fig, plain, tech)
    fig.savefig(out / "hydroacoustics-air9-ew0112-residual-vs-frequency.png", dpi=200); fig.savefig(out / "hydroacoustics-air9-ew0112-residual-vs-frequency.pdf")
    return fig


def chart3(D, out):
    C = pd.read_csv(D / "air7_corridor.csv"); V = json.load(open(D / "air7_verdict.json"))
    E = pd.read_csv(D / "tl_runs_ext.csv") if (D / "tl_runs_ext.csv").exists() else None
    ram = pd.read_csv(D / "air7_ram.csv") if (D / "air7_ram.csv").exists() else None
    sec = json.load(open(Path(str(D).replace("results-data/tl_recal_block9", "")) / "x")) if False else None
    fig, axes = plt.subplots(1, 2, figsize=(11.5, 5.6), gridspec_kw=dict(width_ratios=[1.5, 1]))
    ax = axes[0]
    offs = [-20, -10, -5, 0, 5, 10, 20]; cmap = plt.get_cmap("viridis")
    for i, d in enumerate(offs):
        ax.plot(C.fc_hz, C[f"tl_off{d:+.0f}_db"] - C.tl_air9_H01W_db, "-", color=cmap(i / (len(offs) - 1)), lw=1.6 if d == 0 else 1.0, label=f"path moved {d:+d} km" if d else "straight path (0 km)")
    ax.plot(C.fc_hz, C.tl_nx2d_db - C.tl_air9_H01W_db, "k--", lw=1.2, label="Fresnel corridor average (17 paths)")
    if E is not None:
        for d, ls in ((30, ":"), (40, ":"), (50, ":")):
            e = E[E.tag == f"air7off{d:+.0f}_H01W"].set_index("fc_hz").tl_db.reindex(C.fc_hz).values
            ax.plot(C.fc_hz, e - C.tl_air9_H01W_db, ls, color=RED, lw=1.0, label=f"path moved {d:+d} km (exploratory extension)" if d == 30 else None)
    if ram is not None:
        for tag, mk in (("air7off+0_H01W", "^"), ("air7off+20_H01W", "v")):
            r = ram[ram.tag == tag].merge(ram[ram.tag == "builder_air9_H01W"][["fc_hz", "tl_ram_db"]], on="fc_hz", suffixes=("", "_a9"))
            ax.plot(r.fc_hz, r.tl_ram_db - r.tl_ram_db_a9, mk, color=GREEN, ms=8, mec="k", label=f"coupled-mode (parabolic equation) check, {'straight' if '+0' in tag else '+20 km'} path")
    m = C.dtl_obs_db.notna(); ax.plot(C.fc_hz[m], C.dtl_obs_db[m], "o", color=GREY, mec="k", ms=8, label="measured (chart-read): air7 ≈ air9")
    ax.axhspan(-10, 10, color=GREY, alpha=0.15, lw=0, label="±10 dB acceptance band")
    ax.set_xscale("log"); ax.set_xticks([16, 20, 25, 31.5, 40, 50, 63]); ax.set_xticklabels(["16", "20", "25", "31.5", "40", "50", "63"]); ax.minorticks_off()
    ax.set_xlabel("Frequency (Hz)"); ax.set_ylabel("Extra loss of the air7 path relative to the air9 path at Cape Leeuwin (dB)")
    ax.set_title("a  Even the least-lossy path within ±20 km stays 33–41 dB above the measurement", fontsize=9, loc="left")
    ax.legend(fontsize=6.5, frameon=False, loc="upper left", ncol=2); ax.grid(alpha=0.25); ax.margins(x=0.05, y=0.05)
    ax = axes[1]
    crest = {-20: 1114.5, -10: 1128.5, -5: 1161.0, 0: 1199.0, 5: 1250.5, 10: 1323.5, 20: 1420.5}
    if E is not None:
        for d in (30, 40, 50):
            crest[d] = float(E[E.tag == f"air7off{d:+.0f}_H01W"].min_profile_depth_m.iloc[0])
    xs = sorted(crest); ax.plot(xs, [crest[x] for x in xs], "o-", color=BLUE)
    ex = C[C.fc_hz == 31.5].iloc[0]
    y31 = [float(ex[f"tl_off{d:+.0f}_db"] - ex.tl_air9_H01W_db) for d in offs]
    ax2 = ax.twinx(); ax2.plot(offs, y31, "s--", color=ORANGE)
    if E is not None:
        ax2.plot([30, 40, 50], [float(E[(E.tag == f"air7off{d:+.0f}_H01W") & (E.fc_hz == 31.5)].tl_db.iloc[0] - ex.tl_air9_H01W_db) for d in (30, 40, 50)], "s:", color=ORANGE)
    ax.set_xlabel("Lateral shift of the whole path at the ridge crossing (km; + = right of the forward direction)")
    ax.set_ylabel("Shallowest water on the path (m)", color=BLUE); ax2.set_ylabel("Extra loss at 31.5 Hz relative to air9 (dB)", color=ORANGE)
    ax.invert_yaxis(); ax.set_title("b  Shifting the path to the right deepens the sill and lowers the loss,\n   but 24 dB of excess remains even when the ridge is cleared", fontsize=9, loc="left"); ax.grid(alpha=0.25)
    fig.suptitle("Airgun site air7 (October 2001) to Cape Leeuwin: can a path beside the ridge explain that air7 was heard as well as air9?", fontsize=10.5, x=0.01, ha="left")
    fig.subplots_adjust(top=0.88, bottom=0.30, left=0.07, right=0.93, wspace=0.35)
    plain = wrapt("What the chart shows: the shots at site air7 were heard at Cape Leeuwin about as well as the shots at site air9, yet our model says the air7 path "
                  "loses 43–74 dB more because it crosses a ridge 1,190 m deep. (a) Moving the path sideways by up to 20 km, or averaging over a corridor of paths, does not "
                  f"close the gap; the best path is still 33–41 dB too lossy. (b) Moving 40–50 km to the right clears the ridge, but about 24 dB of extra loss remains. "
                  f"Verdict under the rule fixed in advance: {V['verdict']}. The measurement itself may be biased: only shots heard above the noise were plotted. Caveats C1 and C2 apply.")
    tech = wrapt("Technical: KRAKEN adiabatic incoherent modes, hard bottom, Francois-Garrison, z_s 10 m, receiver 1,055 m; source = shot-weighted mean of the air7 segments "
                 "(22.913 S 87.018 E); sections GEBCO_2026 3×3 median at 0.5 km, WOA23 95A4 October (audit path builder). Offsets d(s) = d_max sin(πs/R). N×2D = nx2d.py Fresnel "
                 "corridor (17 members, exp(−u²) weights, all members open). Reference: air9 → H01W on the same builder. Measured: Fig. 23 CL panel air7 and air9 band means "
                 f"(DIGITISED, airgun_sites_confirm). Medians over 31.5–63 Hz of (model − observed) difference: straight {V['median_excess_db_31p5_to_63']['tl_geo_db']:.1f}, corridor "
                 f"{V['median_excess_db_31p5_to_63']['tl_nx2d_db']:.1f}, least-loss ±20 km {V['median_excess_db_31p5_to_63']['tl_least_loss_db']:.1f} dB. Pre-registration e949144 "
                 "(amendment 2 adds +30/+40/+50 km, exploratory). Gap G22. No MH370 posterior enters; C1/C2 stay on every MH370 number.")
    footnotes(fig, plain, tech)
    fig.savefig(out / "hydroacoustics-air7-corridor-sensitivity.png", dpi=200); fig.savefig(out / "hydroacoustics-air7-corridor-sensitivity.pdf")
    return fig


if __name__ == "__main__":
    D, out = Path(sys.argv[1]), Path(sys.argv[2]); out.mkdir(parents=True, exist_ok=True)
    chart1(D, out); chart2(D, out, sys.argv[3]); chart3(D, out)
    print("charts written")
EOF
RES="$PWD/../../../../../../repo/Claude Science Project Sep 29/results"
python tl_recal_block9_charts.py ../results-data/tl_recal_block9 "$RES" "$RES/hydroacoustics-audit/data/air9_residuals.csv" 2>&1 | tail -5