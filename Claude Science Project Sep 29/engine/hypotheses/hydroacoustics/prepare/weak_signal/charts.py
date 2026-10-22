"""Charts for results/hydroacoustics-weak-signal-methods.md (chart rule of 10 Oct: no project jargon in titles, axes or
legends; two footnotes, plain and technical). Usage: python charts.py <out_root> <results_dir>"""
from __future__ import annotations
import json, sys
from pathlib import Path
import numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
sys.path.insert(0, str(Path(__file__).parent))
import preregistration as R

NAMES = {"M0a_stalta": "Short-term / long-term energy ratio (baseline)", "M0b_bandenergy": "Band energy excess (baseline)",
         "M1a_mf_waveform": "Matched filter, dispersed waveform", "M1b_mf_envelope": "Matched filter, dispersed envelope",
         "M3_cepstral": "Cepstral dispersion fingerprint", "M4a_spectral_kurtosis": "Spectral kurtosis", "M4b_kurtosis": "Time-domain kurtosis",
         "M5_synchrosqueezed": "Synchrosqueezed energy concentration", "M6_changepoint": "Bayesian change-point on band level",
         "M7_stochastic_resonance": "Stochastic resonance (exploratory)", "M2_pairs": "Two-station envelope stacking"}
COL = {"M0a_stalta": "#444444", "M0b_bandenergy": "#999999", "M1a_mf_waveform": "#b2182b", "M1b_mf_envelope": "#ef8a62",
       "M3_cepstral": "#80cdc1", "M4a_spectral_kurtosis": "#2166ac", "M4b_kurtosis": "#67a9cf", "M5_synchrosqueezed": "#8c6bb1",
       "M6_changepoint": "#41ab5d", "M7_stochastic_resonance": "#c2a5cf"}
STYLE = dict(font_size=8)


def foot(fig, plain, tech, y0=0.005):
    fig.text(0.01, y0 + 0.055, plain, fontsize=6.5, va="bottom", ha="left", wrap=True, color="#333333")
    fig.text(0.01, y0, tech, fontsize=6, va="bottom", ha="left", wrap=True, color="#555555")


def fig_pd(root, res):
    PD = pd.read_csv(root / "injection_ext" / "pd_vs_snr_union.csv"); S = json.load(open(root / "injection" / "summary.json"))
    P = PD[PD.logger == 3376]
    fig, axes = plt.subplots(2, 3, figsize=(11, 7.6), sharex=True, sharey=True)
    for i, a in enumerate(R.ALPHAS):
        for j, tau in enumerate(R.TAUS):
            ax = axes[i, j]
            for name in ["M0b_bandenergy", "M0a_stalta", "M3_cepstral", "M4b_kurtosis", "M5_synchrosqueezed", "M6_changepoint", "M7_stochastic_resonance", "M4a_spectral_kurtosis", "M1b_mf_envelope", "M1a_mf_waveform"]:
                g = P[(P.alpha == a) & (P.tau == tau) & (P.method == name)].sort_values("snr_db")
                lw = 2.0 if name.startswith("M1") or name.startswith("M0") else 1.0
                ax.plot(g.snr_db, g.pd, color=COL[name], lw=lw, label=NAMES[name] if (i, j) == (0, 0) else None)
                pre = g[g.grid == "prereg"]; ext = g[g.grid == "extension"]
                ax.plot(pre.snr_db, pre.pd, "o", color=COL[name], ms=3); ax.plot(ext.snr_db, ext.pd, "o", mfc="white", color=COL[name], ms=3)
                if name.startswith("M1") or name.startswith("M0"):
                    ax.fill_between(g.snr_db, g.ci_lo, g.ci_hi, color=COL[name], alpha=0.12, lw=0)
            ax.axhline(0.5, color="#bbbbbb", lw=0.6, ls=":"); ax.axvspan(10.5, 31, color="#f2f2f2", zorder=0)
            ax.set_title(f"source time constant {tau:g} s, false-alarm rate {a:g} per minute", fontsize=8, loc="left")
            ax.set_ylim(-0.02, 1.02); ax.set_xlim(-16, 31); ax.grid(alpha=0.2)
            if j == 0: ax.set_ylabel("Probability of detection")
    h, l = axes[0, 0].get_legend_handles_labels()
    fig.legend(h[::-1], l[::-1], loc="upper center", ncol=4, fontsize=7, frameon=False, bbox_to_anchor=(0.5, 0.935))
    fig.supxlabel("Signal-to-noise ratio of the injected pulse (dB: peak 1 s band level over the background median, 5-40 Hz)", fontsize=8, y=0.2)
    fig.suptitle("Matched filters built on the dispersed arrival shape detect injected impact pulses 6-9 dB fainter than the energy detectors\nat the same false-alarm rate (Perth Canyon logger 3376; the test pulses share the filters' propagation model, so this is their best case)", fontsize=9.5, x=0.01, ha="left", y=0.995, va="top")
    n = S["n_null_windows"]["3376"]
    foot(fig,
         "(i) Synthetic impact sounds were added to 14 days of real recordings from the Perth Canyon sea-noise logger, at six to ten loudness levels, 120 trials each. Each line is a detection method; "
         "the shaded grey area shows loudness levels added after the first run (an amendment). Filled circles: pre-registered levels; open circles: added levels. Shaded bands: 95 % Wilson intervals (matched filters and baselines only). Dotted line: 50 % detection. "
         "The two matched filters use the expected shape of a long-range deep-ocean arrival; the test pulses were made with the same propagation model, so this is a best case for them.",
         f"(ii) Prereg 78c7e88 (test set a), amendment 1 (15-30 dB). Background: IMOS 3376, 1-7 and 9-15 Mar 2014, {n} non-overlapping 60 s null windows; thresholds = null quantiles at alpha 0.01 / 0.001 per window (0.001 rests on the top ~5 values). "
         "Pulse = one-pole source (ESD flat to 1/tau, f^-2 above) x KRAKEN coherent broadband channel (WOA23 March midpoint profile, flat 4,610 m hard bottom, 2-48 Hz, ranges 1,800-3,000 km), 5-40 Hz, 100 Hz. "
         "Source posterior: run J seed-1 weighted-median impact for the path geometry only; no 00:19 option, p or eta enters (SNR is the control variable). Caveats C1 (TL slope misfit) and C2 (coupling uncalibrated) apply to any mapping of SNR to impact energy; none is made here.",
         y0=0.01)
    fig.subplots_adjust(top=0.82, bottom=0.25, left=0.06, right=0.99, hspace=0.3, wspace=0.08)
    for ext in ("png", "pdf"):
        fig.savefig(res / f"hydroacoustics-weak-signal-pd-vs-snr.{ext}", dpi=200)
    plt.close(fig)


def fig_panels(root, res):
    import common as C
    S = np.load(root / "kadri" / "panel_statistics.npz"); null = np.load(root / "kadri" / "null_panel_maxima.npz")
    methods = ["M0a_stalta", "M0b_bandenergy", "M1b_mf_envelope", "M3_cepstral", "M4a_spectral_kurtosis", "M4b_kurtosis", "M5_synchrosqueezed", "M6_changepoint", "M7_stochastic_resonance"]
    fig, axes = plt.subplots(len(methods) + 1, 2, figsize=(12, 11), sharex="col", gridspec_kw=dict(height_ratios=[2] + [1] * len(methods)))
    for col, pnl in enumerate(["c", "a"]):
        tg, x, utc0, nv = C.load_panel(pnl)
        ax = axes[0, col]; ax.plot(tg, x, color="#333333", lw=0.4)
        ax.set_title(f"Kadri (2024) Fig. 9 panel ({pnl}), H01W, from {utc0.strftime('%H:%M')} UTC - digitised plot ({nv} vertices)", fontsize=8, loc="left")
        if col == 0: ax.set_ylabel("plotted\npressure (Pa)", fontsize=7)
        for name, (a, b) in R.BOXES.items():
            ta = (pd.Timestamp(f"2014-03-08T{a}Z") - utc0).total_seconds(); tb = (pd.Timestamp(f"2014-03-08T{b}Z") - utc0).total_seconds()
            if tb < 0 or ta > 600: continue
            for r in range(len(methods) + 1):
                axes[r, col].axvspan(ta, tb, color="#fde0a8", alpha=0.5, lw=0, zorder=0)
            ax.text((ta + tb) / 2, 0.97, name.replace("poster (a) ", "").replace(" time ", "\n"), fontsize=6, ha="center", va="top", transform=ax.get_xaxis_transform())
        for r, name in enumerate(methods, start=1):
            ax = axes[r, col]
            t, v = S[f"{pnl}/{name}/t"], S[f"{pnl}/{name}/v"]
            nv_ = null[name]; nv_ = np.sort(nv_[np.isfinite(nv_)])
            p = 1 - np.searchsorted(nv_, np.nan_to_num(v, nan=-np.inf), side="left") / len(nv_)
            p = np.maximum(p, 0.5 / len(nv_))
            ax.plot(t, -np.log10(p), color=COL[name], lw=0.8)
            for thr, ls in ((0.3, ":"), (0.1, "--"), (0.05, "-")):
                ax.axhline(-np.log10(thr), color="#888888", lw=0.5, ls=ls)
            ax.set_ylim(0, 3.5); ax.set_yticks([0, 1, 2, 3]); ax.set_yticklabels(["1", "0.1", "0.01", "0.001"], fontsize=6)
            if col == 0: ax.set_ylabel("p", fontsize=7, rotation=0, labelpad=8)
            ax.text(0.005, 0.95, NAMES[name], transform=ax.transAxes, fontsize=6.5, va="top", ha="left", color=COL[name])
        axes[-1, col].set_xlabel(f"seconds after {utc0.strftime('%H:%M:%S')} UTC, 8 March 2014")
        axes[-1, col].set_xlim(0, 600)
    fig.suptitle("On the digitised H01W traces only the envelope matched filter reaches p = 0.05 inside an author's box (text time 00:52:03);\nthe four panel (a) boxes stay above p = 0.08 for every method", fontsize=9, x=0.01, ha="left", y=0.995)
    foot(fig,
         "(i) Top row: Kadri's published pressure traces, redrawn from the figure's vector data (a decimated plot, not the recording). Lower rows: for each method, how unusual the statistic is against 14 days of real sea noise, as a "
         "probability (lower = more unusual; lines at 0.3, 0.1, 0.05). Orange bands: the author's boxes - text time 00:52:03, caption time 00:54:30, and the four 'weak' boxes of the 2025 poster panel (a). Chance alone gives about one value below 0.05 per 20 minutes of trace per method.",
         "(ii) Prereg 78c7e88 (test set b). Traces: PDF vector polylines ~14.5 vertices/s resampled to 20 Hz, band 1-9 Hz. Null: IMOS 3376 background through a plot-decimation emulator (per 69 ms bin min and max vertices, 20 Hz), 1,344 files x 4 windows of 60 s. p = fraction of null window maxima >= statistic (floor 1/(2 n)). "
         "Matched filter uses the KRAKEN 2,200 km template envelope only. Digitised data; caveats C1, C2; H08S panels d, e in the results note (shot-dominated).", y0=0.01)
    fig.subplots_adjust(top=0.93, bottom=0.14, left=0.06, right=0.99, hspace=0.35, wspace=0.08)
    for ext in ("png", "pdf"):
        fig.savefig(res / f"hydroacoustics-weak-signal-kadri-panels.{ext}", dpi=200)
    plt.close(fig)


def fig_h08s(root, res):
    Z = np.load(root / "h08s" / "series.npz"); sup = pd.read_csv(root / "h08s" / "suppression.csv"); I = pd.read_csv(root / "h08s" / "injection_pd.csv")
    fig = plt.figure(figsize=(12, 9)); gs = fig.add_gridspec(3, 2, height_ratios=[1.2, 1.2, 1.1], hspace=0.6, wspace=0.25)
    for col, pnl in enumerate("de"):
        tg, e, resid, gm, ts = Z[f"{pnl}/tg"], Z[f"{pnl}/e"], Z[f"{pnl}/res"], Z[f"{pnl}/gm"], Z[f"{pnl}/ts"]
        ax = fig.add_subplot(gs[0, col]); ax.plot(tg - tg[0], 10 * np.log10(np.maximum(e, 1e-6)), color="#333333", lw=0.5, label="as plotted")
        ax.plot(tg - tg[0], 10 * np.log10(np.maximum(np.maximum(resid, 0), 1e-6)), color="#b2182b", lw=0.5, label="after shot-template subtraction")
        ax.fill_between(tg - tg[0], -60, 10, where=~gm, color="#d9e8f5", lw=0, zorder=0, label="gated out (shot cadence)")
        ax.set_ylim(-40, 8); ax.set_xlim(0, 600)
        row = sup[sup.panel == pnl].iloc[0]
        ax.set_title(f"H08S panel ({pnl}), {'01:00' if pnl == 'd' else '01:10'} UTC: {int(row.n_shots)} shots every {row.cadence_s:.2f} s;\nresidual energy {row.c1_reduction_db_whole:+.1f} dB after subtraction, {row.c1c2_reduction_db:+.1f} dB with gating", fontsize=8, loc="left")
        ax.set_ylabel("energy envelope (dB re 1 Pa$^2$)", fontsize=7)
        if col == 0: ax.legend(fontsize=6.5, frameon=False, loc="upper center", ncol=3, bbox_to_anchor=(1.05, -0.12))
        ax2 = fig.add_subplot(gs[1, col]); sel = (tg - tg[0] >= 200) & (tg - tg[0] <= 320)
        ax2.plot(tg[sel] - tg[0], e[sel], color="#333333", lw=0.7); ax2.plot(tg[sel] - tg[0], np.maximum(resid[sel], 0), color="#b2182b", lw=0.7)
        ax2.fill_between(tg[sel] - tg[0], 0, e[sel].max() * 1.05, where=~gm[sel], color="#d9e8f5", lw=0, zorder=0)
        ax2.set_xlim(200, 320); ax2.set_ylim(0, e[sel].max() * 1.05); ax2.set_title("detail, 200-320 s", fontsize=8, loc="left"); ax2.set_ylabel("energy envelope (Pa$^2$)", fontsize=7)
        ax2.set_xlabel(f"seconds after {'01:00:00' if pnl == 'd' else '01:10:00'} UTC")
        ax3 = fig.add_subplot(gs[2, col]); g = I[I.panel == pnl]
        for k, (hc, cc, lab, c) in enumerate((("hit_raw", "ctl_raw", "no suppression", "#333333"), ("hit_c1", "ctl_c1", "template subtraction", "#ef8a62"), ("hit_c1c2", "ctl_c1c2", "subtraction + cadence gating", "#b2182b"))):
            ax3.plot(g.level_db, g[hc], "-o", color=c, ms=4, lw=1.5, label=f"{lab}: with injected pulse")
            ax3.plot(g.level_db, g[cc], "--", color=c, lw=1, label=f"{lab}: chance (no pulse)")
        ax3.set_ylim(-0.02, 1.02); ax3.set_xlabel("injected pulse peak relative to the median shot peak (dB)"); ax3.set_ylabel("fraction of trials with a peak\nwithin 2 s (z >= 3)", fontsize=7)
        ax3.set_title("recovery of an injected deep-channel arrival (40 trials per level)", fontsize=8, loc="left")
        if col == 0: ax3.legend(fontsize=6, frameon=False, ncol=2, loc="upper left")
    fig.suptitle("Airgun shot suppression on the digitised H08S traces lowers the residual energy by 5-8 dB and cuts chance coincidences\nfrom about 0.5 to 0.1-0.2 per trial; an added long-range arrival 4 dB below the shots is still recovered", fontsize=9, x=0.01, ha="left", y=0.995)
    foot(fig,
         "(i) The Diego Garcia (H08S) traces are dominated by a seismic survey's airgun shots every 10 s. Top: the energy envelope as plotted (black) and after subtracting each shot's local average shape (red); blue bands mark times gated out on the shot rhythm. "
         "Middle: a two-minute detail. Bottom: how often an added long-range arrival is found (solid) against how often the same rule fires by chance at that time with nothing added (dashed).",
         "(ii) Prereg 78c7e88 (test set c). Panels d, e: PDF vector polylines resampled to 40 Hz (as h08s_shot_outliers.load); envelope p^2 boxcar 0.25 s; shots = h08s_pulse_energy rule; local median template of 12 neighbours over [-3, +6] s scaled to the shot peak; cadence = median 9-11 s interval, gate +-1.5 s (30 % of time). "
         "z against the median/MAD of the raw envelope in shot-free gaps. Injected arrival: KRAKEN 3,703.5 km template (tau 1 s) envelope, 6 levels x 40 onsets. Digitised data; caveats C1, C2.", y0=0.01)
    fig.subplots_adjust(top=0.92, bottom=0.13, left=0.07, right=0.99)
    for ext in ("png", "pdf"):
        fig.savefig(res / f"hydroacoustics-weak-signal-h08s-suppression.{ext}", dpi=200)
    plt.close(fig)


if __name__ == "__main__":
    root, res = Path(sys.argv[1]), Path(sys.argv[2]); res.mkdir(parents=True, exist_ok=True)
    plt.rcParams.update({"font.size": 8, "axes.titlesize": 8, "axes.labelsize": 7.5, "xtick.labelsize": 7, "ytick.labelsize": 7})
    fig_pd(root, res); fig_panels(root, res); fig_h08s(root, res)
    print("charts done")
