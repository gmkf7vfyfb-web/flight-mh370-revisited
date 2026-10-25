import os

"""Figure: module M1b matched filter on the real San Juan arrivals at Ascension (raw IMS H10). Run inside the kernel after apply_figure_style()."""
import sys, numpy as np, pandas as pd, matplotlib.pyplot as plt
from scipy import signal
sys.path.insert(0, "scripts"); import meas as MS
W = "repo/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare/weak_signal"; sys.path.insert(0, W); sys.path.insert(0, W + "/..")
import preregistration as R, methods as M, bank as B
from obspy import UTCDateTime as U
T = np.load(os.path.join(os.environ.get("MH370_EXCHANGE", "mh370-exchange"), "hydroacoustics", "run-j-weak-signal", "templates", "templates_raw.npz")); ctx = B.build(T)
SOS = signal.butter(4, list(R.BAND), btype="bandpass", fs=250.0, output="sos")
el = pd.read_csv("out/meas_elements.csv"); res = pd.read_csv("out/m1b_real_arrival.csv")
fig, axs = plt.subplots(2, 2, figsize=(7.2, 5.0), gridspec_kw=dict(width_ratios=[1.5, 1]))
for row, (ev, lab) in enumerate((("sj_event", "ARA San Juan event, 15 Nov 2017"), ("sj_charge", "Calibration charge, 1 Dec 2017"))):
    s = "H10N1"; tr, c = MS.load(f"raw/{ev}_{s}.mseed", f"raw/{ev}_resp.xml"); fs = 250.0
    tpk = U(el[(el.event == ev) & (el.station == s)].t_peak_utc.iloc[0]) - tr.stats.starttime
    x = MS.bp(tr.data, fs, 5, 40); t = np.arange(len(x)) / fs - tpk; m = (t > -60) & (t < 60)
    ax = axs[row, 0]; ax.plot(t[m], x[m], lw=0.4, color="0.35", label="pressure, 5-40 Hz")
    y = signal.resample_poly(signal.sosfiltfilt(SOS, tr.data), 2, 5); ts, ss = M.m1b_matched_envelope(y, R.FS, ctx); ts = ts - tpk
    ax2 = ax.twinx(); mm = (ts > -60) & (ts < 60); ax2.plot(ts[mm], ss[mm], color="#1f5fa8", lw=1.0, label="matched-filter statistic"); ax2.set_ylim(-0.6, 1.05)
    ax2.axvspan(-30, 30, color="#1f5fa8", alpha=0.07, lw=0); ax2.set_ylabel("Matched-filter statistic", color="#1f5fa8")
    ax.set_ylabel("Pressure (Pa)"); ax.set_title(f"{lab}, Ascension North element 1", loc="left")
    if row == 1: ax.set_xlabel("Time from envelope peak (s)")
    r = res[(res.event == ev) & (res.station == s)].iloc[0]
    # null histogram
    tn, xn = None, None
    trn, _ = MS.load(f"raw/{ev}_null_{s}.mseed", f"raw/{ev}_resp.xml"); yn = signal.resample_poly(signal.sosfiltfilt(SOS, trn.data), 2, 5)
    a, b = M.m1b_matched_envelope(yn, R.FS, ctx); null = M.window_maxima(a, b, R.WARMUP_S, R.WINDOW_S, len(yn) / R.FS); null = null[np.isfinite(null)]
    ax = axs[row, 1]; ax.hist(null, bins=np.linspace(0, 1, 41), color="0.6", label=f"background, {len(null)} windows of 60 s")
    ax.axvline(r.m1b_score, color="#1f5fa8", lw=1.5); ax.text(r.m1b_score - 0.02, ax.get_ylim()[1] * 0.92, f"arrival\np = {r.p_value:.4f}", ha="right", va="top", fontsize=7, color="#1f5fa8")
    ax.set_xlabel("Window maximum of the statistic" if row == 1 else ""); ax.set_ylabel("Count"); ax.set_title("Same element, same day, before the event", loc="left")
for a, L in zip(axs.flat, "abcd"): panel_letter(a, L)
fig.tight_layout(rect=(0, 0.17, 1, 1))
ste = ("(i) The chart shows two real sounds from the South Atlantic at the Ascension Island hydrophones. The blue line is the module's matched filter. "
       "Each grey bar counts quiet 60 s windows from the same hydrophone before the event. Both arrivals are above all, or almost all, quiet windows. "
       "Some quiet windows have values near 1, so the filter alone does not separate a strong arrival well.")
tech = ("(ii) Raw IM.H10N1 EDH, StationXML response removed (Pa); module M1b (prepare/weak_signal, unchanged; template bank 1,800-3,000 km, Indian Ocean "
        "profile, tau 0.1/1/10 s, 5-40 Hz, 100 Hz); event score = max in [t_pk-30, t_pk+30] s; null = non-overlapping 60 s window maxima, 07:30-13:50 UTC "
        "(event) and 14:00-20:04 UTC (charge); p = (k+1)/(n+1), floor 1/(n+1) = 0.0026/0.0027. Exploratory test, written before computing. "
        "P_D is still a proxy until it is measured on real data; the frequency-slope caveat of the propagation model does not apply to this amplitude-blind statistic.")
import textwrap
fig.text(0.01, 0.105, "\n".join(textwrap.wrap(ste, 160)), fontsize=6, va="top"); fig.text(0.01, 0.045, "\n".join(textwrap.wrap(tech, 170)), fontsize=5.5, va="top", color="0.25")
fig.savefig("out/fig_m1b_real_arrival.png", dpi=200)
