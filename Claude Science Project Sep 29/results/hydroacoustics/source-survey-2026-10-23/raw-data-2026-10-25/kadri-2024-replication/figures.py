"""Figures for the Kadri replication note. Run in the python kernel after apply_figure_style() (figure-style skill).
Inputs: kadri/out/panels/*.npz, window_statistics.csv, reproduction_match.csv, digitise_panels.py."""
import json, textwrap
import numpy as np, pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from scipy import signal
from obspy import UTCDateTime
import digitise_panels as dpn

ORANGE = "#d9541a"; GREY = "#8c8c8c"; WATER = "#3b75af"; HYB = "#c9a227"
NAMES = {"F35A": "F-35A crash off Misawa, 9 Apr 2019", "TA810": "Transair 810 ditching off Oahu, 2 Jul 2021",
         "SJ182": "Sriwijaya Air 182, Java Sea, 9 Jan 2021", "AB1103": "AB Aviation 1103 off Moheli, 26 Feb 2022",
         "QZ8501": "AirAsia 8501, Karimata Strait, 27 Dec 2014", "JT610": "Lion Air 610, Java Sea, 28 Oct 2018 (not in Kadri 2024)"}
STA = {"H11N": "Wake Island north (H11N)", "H11S": "Wake Island south (H11S)", "H08S": "Diego Garcia south (H08S)", "H01W": "Cape Leeuwin (H01W)"}

def foot(fig, plain, tech, y=0.005, width=190):
    t = "Plain note. " + plain + "\nTechnical note. " + tech
    fig.text(0.01, y, "\n".join(textwrap.fill(p, width) for p in t.split("\n")), fontsize=6, va="bottom", ha="left")

def load(k, tri):
    z = np.load(f"kadri/out/panels/{k}_{tri}.npz", allow_pickle=True)
    W = {nm: (UTCDateTime(a), UTCDateTime(b)) for nm, (a, b) in json.loads(str(z["windows"])).items()}
    return z, W

def panel_rows(keys, rp, ws, fname, plain, tech, title):
    dig = {k: dpn.digitise(k) for k in keys}
    fig, axs = plt.subplots(len(keys), 2, figsize=(11, 2.25 * len(keys) + 1.3), gridspec_kw=dict(width_ratios=[1, 1.35]))
    axs = np.atleast_2d(axs)
    for r, key in enumerate(keys):
        k, tri = key.split("_"); z, W = load(k, tri); d = dig[key]
        T0 = UTCDateTime(str(z["T0"])); t_panel = UTCDateTime(d["t0"])
        sub = rp[(rp.panel == key) & (rp["filter"] == "zero-phase")]
        el = sub.sort_values("r_zero_lag", ascending=False).iloc[0]
        x = z[f"x_{el.element}"]; xs0 = T0 + float(z["span_t0"])
        a = int((t_panel - xs0) * 250); seg = x[a:a + 150000]
        # spectrogram (ours)
        f, t, Sxx = signal.spectrogram(seg, fs=250, nperseg=500, noverlap=250)
        ax = axs[r, 0]
        im = ax.pcolormesh(t / 60, f, 10 * np.log10(Sxx + 1e-30) + 120, shading="auto", cmap="inferno", vmin=50, vmax=100, rasterized=True)
        ax.set_ylim(2, 40); ax.set_xlim(0, 10); ax.set_ylabel("Frequency (Hz)")
        kb = W["KB"]; ax.add_patch(Rectangle(((kb[0] - t_panel) / 60, 3), (kb[1] - kb[0]) / 60, 36, fill=False, ec="white", lw=1))
        ax.set_title(f"{NAMES[k].split(',')[0]}: {STA[tri]}, element {el.element[-1]}", loc="left")
        if r == len(keys) - 1: ax.set_xlabel(f"Time (min) after the panel start (UTC)")
        cb = fig.colorbar(im, ax=ax, pad=0.01, fraction=0.04); cb.set_label("dB re 1 µPa²/Hz")
        ax.text(0.01, 0.95, f"start {t_panel.strftime('%H:%M')} UTC", transform=ax.transAxes, color="white", fontsize=6, va="top")
        # time series overlay
        ax = axs[r, 1]
        ncol = len(d["t_min"]); nb = len(seg) // ncol; Y = seg[: nb * ncol].reshape(ncol, nb)
        ax.fill_between(d["t_min"], d["lower_pa"], d["upper_pa"], color=GREY, alpha=0.55, lw=0, label="Kadri 2024, printed trace (digitised)")
        ax.plot(d["t_min"], Y.max(1), color=ORANGE, lw=0.5, label="raw IMS data, Kadri's stated filter (ours)")
        ax.plot(d["t_min"], Y.min(1), color=ORANGE, lw=0.5)
        ax.add_patch(Rectangle(((kb[0] - t_panel) / 60, -1.2), (kb[1] - kb[0]) / 60, 2.4, fill=False, ec="k", lw=1, label="Kadri's box"))
        for nm, col in [("water", WATER), ("hybrid", HYB)]:
            if nm in W:
                a0 = (W[nm][0] - t_panel) / 60; a1 = (W[nm][1] - t_panel) / 60
                if a1 > 0 and a0 < 10:
                    ax.axvspan(max(a0, 0), min(a1, 10), color=col, alpha=0.18, lw=0,
                               label="our predicted window, water path" if nm == "water" else "our predicted window, crustal and water path")
        ax.set_xlim(0, 10); ax.set_ylim(-1.25, 1.25); ax.set_ylabel("Pressure (Pa)")
        rr = sub[sub.element == el.element].iloc[0]
        w = ws[(ws.case == k) & (ws.station == tri) & (ws.window == "KB")].iloc[0]
        ax.text(0.01, 0.97, f"envelope r = {rr.r_zero_lag:.2f} at 0 s, {rr.r_best:.2f} at {rr.lag_best_s:+.1f} s; median level {rr.median_upper_ratio_dB:+.1f} dB vs printed",
                transform=ax.transAxes, fontsize=6, va="top")
        ax.text(0.01, 0.03, f"box: peak {w.S_triad_rms1s_Pa:.3f} Pa (1-s RMS), p = {w.p_value:.3f}, SNR {w.SNR_day_dB:.1f} dB, back-azimuth {w.baz_deg:.0f}° (expected {w.expected_baz_deg:.0f}°)",
                transform=ax.transAxes, fontsize=6, va="bottom")
        if r == 0: ax.legend(loc="upper right", fontsize=6, frameon=False, bbox_to_anchor=(1.0, 0.86))
        if r == len(keys) - 1: ax.set_xlabel("Time (min) after the panel start (UTC)")
    fig.suptitle(title, x=0.01, ha="left", fontsize=9)
    fig.tight_layout(rect=(0, 0.11, 1, 0.97))
    foot(fig, plain, tech)
    fig.savefig(fname, dpi=200)
    return fig

def timeline(cases, ws, fname, plain, tech, title, CASES):
    fig, axs = plt.subplots(len(cases), 1, figsize=(11, 1.45 * len(cases) + 1.5), sharex=False)
    for ax, (k, tri) in zip(axs, cases):
        z, W = load(k, tri); T0 = UTCDateTime(str(z["T0"])); ti = UTCDateTime(CASES[k]["off_t"].isoformat())
        tt = z["tt"]; R = z["R"]; tmin = ((T0 - ti) + tt) / 60.0
        m = (tmin > -5) & (tmin < 75)
        ax.semilogy(tmin[m], R[m], color="k", lw=0.4)
        ax.axhline(float(z["bg_day"]), color=GREY, lw=0.6, ls="--")
        for nm, col, lab in [("water", WATER, "predicted, water path"), ("hybrid", HYB, "predicted, crustal and water path"), ("hybrid_wide", HYB, None)]:
            if nm in W:
                a0, a1 = (W[nm][0] - ti) / 60, (W[nm][1] - ti) / 60
                ax.axvspan(a0, a1, color=col, alpha=0.25 if nm != "hybrid_wide" else 0.1, lw=0)
        if "KB" in W:
            a0, a1 = (W["KB"][0] - ti) / 60, (W["KB"][1] - ti) / 60
            ax.axvspan(a0, a1, fill=False, ec="k", lw=1.0, hatch="////", alpha=0.6)
        rows = ws[(ws.case == k) & (ws.station == tri)]
        txt = []
        for _, w in rows.iterrows():
            if not isinstance(w.peak_utc, str):
                txt.append(f"{w.window}: no open data"); continue
            tp = (UTCDateTime(w.peak_utc) - ti) / 60
            if w.window in ("KB", "water", "hybrid"):
                ax.plot(tp, w.S_triad_rms1s_Pa, "v", ms=4, color={"KB": "k", "water": WATER, "hybrid": HYB}[w.window])
            lab = {"KB": "Kadri box", "water": "water", "hybrid": "crustal", "hybrid_wide": "crustal (wide)"}[w.window]
            txt.append(f"{lab}: p={w.p_value:.2f}, {w.baz_deg:.0f}°")
        ax.set_xlim(-5, 75); ax.set_ylim(0.02, 2)
        ax.set_title(f"{NAMES[k]}: {STA[tri]}; expected back-azimuth {rows.expected_baz_deg.dropna().iloc[0]:.0f}°" if rows.expected_baz_deg.notna().any() else f"{NAMES[k]}: {STA[tri]}", loc="left", fontsize=7)
        ax.text(1.005, 0.5, "\n".join(txt), transform=ax.transAxes, fontsize=5.5, va="center")
        ax.set_ylabel("1-s RMS (Pa)", fontsize=6)
    axs[-1].set_xlabel("Time after the official impact time (min)")
    fig.suptitle(title, x=0.01, ha="left", fontsize=9)
    fig.tight_layout(rect=(0, 0.075, 0.86, 0.975))
    foot(fig, plain, tech, width=200)
    fig.savefig(fname, dpi=200)
    return fig
