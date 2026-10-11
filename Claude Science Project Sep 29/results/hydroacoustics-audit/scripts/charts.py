"""Audit task 3: corrected background-noise vs expected-impact charts for Cape Leeuwin and Diego Garcia South.

Noise: the module's traced Blackman (2004) Appendix B noise panels (results-data/blackman_noise/, QC-passed, unique),
median and 10-90 % over panels, exactly as the module's chart. Markers: markers.py output (module arithmetic
reproduced to 0.0 dB, plus scenario (c) and the calibration error).

Usage: python charts.py <module_dir> <markers_audit.json> <out_dir>
"""
import csv
import json
import sys
import textwrap

import matplotlib as mpl
mpl.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402
from matplotlib.patches import Patch  # noqa: E402

mdir, mk_json, out = sys.argv[1:4]
J = json.load(open(mk_json))
z = np.load(f"{mdir}/results-data/blackman_noise/blackman_noise_curves.npz"); f = z["f"]
ok = {(r["station"], r["page"], r["image"], r["row"]) for r in csv.DictReader(open(f"{mdir}/results-data/blackman_noise/blackman_noise_panels.csv")) if r["status"] == "ok"}
S = {st: np.array([z[k] for k in z.files if k.startswith(st) and (st,) + tuple(x[1:] for x in k.split("_")[1:]) in ok]) for st in ("H01W", "H08S")}

plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 8, "axes.spines.top": False, "axes.spines.right": False})
COL = {"H01W": "#1f4e9c", "H08S": "#1f4e9c"}
SCEN = [("a", "o", "full", "Steep fast entry, 270–360 m/s, all energy"),
        ("c_eof_prior", "D", "full", "All modelled end-of-flight impacts"),
        ("b_total", "s", "none", "Slow ditching, 60–150 m/s, all energy"),
        ("b_vertical", "^", "none", "Slow ditching, vertical motion only")]
NAME = {"H01W": "Cape Leeuwin", "H08S": "Diego Garcia South"}
LONG = {"H01W": "Cape Leeuwin hydrophone station (off south-west Australia)",
        "H08S": "Diego Garcia South hydrophone station (central Indian Ocean)"}
GREY = "0.35"


def chart(st):
    fig = plt.figure(figsize=(9.0, 6.6))
    ax = fig.add_axes([0.075, 0.34, 0.60, 0.56])
    v = S[st]; med = np.nanmedian(v, 0); lo, hi = np.nanquantile(v, [0.1, 0.9], 0)
    span_lo = J["stations"][st]["span_lo_hz"]
    ax.axvspan(4.2, span_lo * 2 ** (-1 / 6), color="0.92", lw=0, zorder=0)
    ax.text(4.35, 123, "no recorded data checks\nthe model in this range", fontsize=6.5, color=GREY, va="top")
    ax.fill_between(f, lo, hi, color=COL[st], alpha=0.16, lw=0, zorder=1)
    ax.plot(f, med, color=COL[st], lw=1.5, zorder=2)
    bands = np.array(J["bands"])
    for i, (key, mk, fill, _) in enumerate(SCEN):
        rows = J["stations"][st]["scen"][key]
        x = bands * 2 ** ((i - 1.5) * 0.045)
        for xx, r in zip(x, rows):
            ax.vlines(xx, r["ext_lo"], r["ext_hi"], color="0.65", lw=1.0, ls="-" if r["inside_span"] else (0, (2, 1.5)), zorder=3)
            ax.vlines(xx, r["q10"], r["q90"], color="0.1", lw=1.4, zorder=4)
        ax.plot(x, [r["q50"] for r in rows], ls="none", marker=mk, ms=4, mec="0.1", mfc="0.1" if fill == "full" else "white", mew=0.9, zorder=5)
    ax.set_xscale("log"); ax.set_xlim(4.2, 48); ax.set_ylim(10, 126)
    ax.set_xticks([5, 6.3, 8, 10, 12.5, 16, 20, 25, 31.5, 40]); ax.set_xticklabels(["5", "6.3", "8", "10", "12.5", "16", "20", "25", "31.5", "40"])
    ax.minorticks_off()
    ax.set_xlabel("Frequency, centre of third-octave band (Hz)")
    ax.set_ylabel("Power spectral density over a 6 s window (dB re 1 µPa²/Hz)")
    ax.set_title(f"{LONG[st]}: background noise and the sound level an impact would make,\nwith the calibration error added",
                 loc="left", fontsize=8)
    hh = [Line2D([], [], color=COL[st], lw=1.5, label=f"Background noise, 2003: median of {len(v)} records"),
          Patch(color=COL[st], alpha=0.16, lw=0, label="Background noise, 2003: 10–90 % range")]
    hh += [Line2D([], [], ls="none", marker=mk, mec="0.1", mfc="0.1" if fill == "full" else "white", label=lab) for _, mk, fill, lab in SCEN]
    hh += [Line2D([], [], color="0.1", lw=1.4, label="Dark bar: model range, 10–90 %"),
           Line2D([], [], color="0.65", lw=1.0, label="Light bar: range with calibration error added"),
           Line2D([], [], color="0.65", lw=1.0, ls=(0, (2, 1.5)), label="Dashed light bar: allowance only, no check data")]
    fig.legend(handles=hh, loc="upper left", bbox_to_anchor=(0.682, 0.90), labelspacing=0.6, handlelength=2.2, frameon=False, fontsize=6.5)
    rk = J["stations"][st]["range_km"]; r = J["stations"][st]["air9_residual_db"]; um = J["stations"][st]["unknown_bound_db"]
    rtxt = ", ".join(f"{float(k):g} Hz {v_:+.0f}" for k, v_ in r.items())
    ste = (f"What the chart shows. The curve is the background noise at {NAME[st]}. The markers are the sound level that an impact "
           f"near 37.2°S 89.6°E ({rk:,.0f} km away) would make at the station, one set for each frequency band. The dark bars are the "
           "range from the model. The light bars add the error that we found when we compared the model with airgun shots recorded "
           f"in 2001. Below {span_lo:g} Hz, no recorded data checks the model, so the dashed bars there are an allowance of ±{um:.0f} dB, "
           "not a measurement. If a marker is above the curve, the impact can be heard in that band. These are estimates. They are not "
           "a probability of detection.")
    tech = ("Technical. Received ESD = η_cal(τ, z_s)·E·ρc/2π·S_b(τ)·10^(−TL_b/10)·10^(C/10), shown as PSD over 6 s per third-octave "
            "band; η_cal from the F-35A (H11, 0.7 Pa, 900 MJ, RAM-corrected), τ ~ log-U(0.05, 10) s, z_s ∈ {2, 10, 30} m, ESD ∝ f⁻² "
            "above 1/τ, C ~ N(0, 10) + N(0, 3) dB; KRAKEN adiabatic incoherent modes, hard half-space, median impact path minus RAM Δ; "
            "m = 175 t; n = 40,000 draws per scenario (module arithmetic reproduced to 0.0 dB). Scenario 'all modelled' = core run (b) "
            "end-of-flight impacts, 00:19 option R600 BTO only, prior weights; 'steep fast entry' tops out above the sea-level speed "
            "of sound. Calibration error: RL_true = RL_model − r_b, r_b = observed − model TL for air9 at this station (Blackman et al. "
            f"2004, Fig. 23, p. 21; 10 m source; dB: {rtxt}); outside that span ±max|r_b|. Audit verdict for air9: level PASS, "
            "slope FAIL at both stations (not calibrated in slope). Noise: Blackman et al. 2004, App. B, pp. 25–31, 6 s pre-event "
            "windows, counts → Pa by the FDSN response with SAC scaling inferred, not stated (route R); May–June 2003, not March 2014.")
    fig.text(0.01, 0.232, textwrap.fill(ste, 200), fontsize=6.0, va="top", color=GREY)
    fig.text(0.01, 0.145, textwrap.fill(tech, 232), fontsize=5.2, va="top", color=GREY)
    fn = f"{out}/hydroacoustics-audit-noise-vs-impact-{st}"
    fig.savefig(fn + ".png", dpi=300); fig.savefig(fn + ".pdf")
    # render-then-verify: text overlaps and figure bounds
    rdr = fig.canvas.get_renderer()
    texts = [(t, t.get_window_extent(rdr)) for t in fig.findobj(mpl.text.Text) if t.get_text().strip() and t.get_visible()]
    bad = [(a.get_text()[:30], b.get_text()[:30]) for i, (a, ba) in enumerate(texts) for b, bb in texts[i + 1:] if ba.overlaps(bb)]
    outside = [t.get_text()[:30] for t, bt in texts if bt.x0 < 0 or bt.x1 > fig.bbox.x1 or bt.y0 < 0 or bt.y1 > fig.bbox.y1]
    print(st, "overlaps", bad[:5], "outside", outside[:5])
    plt.close(fig)


for st in ("H01W", "H08S"):
    chart(st)
