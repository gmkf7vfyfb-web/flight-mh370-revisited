import os
"""San Juan real-arrival test of the module's M1b (dispersion-aware envelope matched filter, prepare/weak_signal, unchanged)
(prereg J). Element records: response removed (Pa), 5-40 Hz 4-pole zero-phase, resampled 250 -> 100 Hz (module FS).
Event score = max M1b statistic in [t_pk-30, t_pk+30] s (60 s = module WINDOW_S). Null = maxima over non-overlapping
60 s windows of the same element's pre-event record on the same day (module window_maxima, warm-up 32 s).
p = (k+1)/(n+1), k = null windows with score >= event score."""
import sys, json, numpy as np, pandas as pd
from scipy import signal
sys.path.insert(0, "scripts"); import meas as MS
W = "repo/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare/weak_signal"; sys.path.insert(0, W); sys.path.insert(0, W + "/..")
import preregistration as R, methods as M, bank as B
from obspy import UTCDateTime as U
T = np.load(os.path.join(os.environ.get("MH370_EXCHANGE", "mh370-exchange"), "hydroacoustics", "run-j-weak-signal", "templates", "templates_raw.npz")); ctx = B.build(T)
SOS = signal.butter(4, list(R.BAND), btype="bandpass", fs=250.0, output="sos")
def prep(path, resp):
    tr, c = MS.load(path, resp); y = signal.sosfiltfilt(SOS, tr.data); return tr.stats.starttime, signal.resample_poly(y, 2, 5)
el = pd.read_csv("out/meas_elements.csv"); rows = []
for ev in ("sj_event", "sj_charge"):
    for s in ("H10N1", "H10N2", "H10N3", "H10S2", "H10S3"):
        t0n, xn = prep(f"raw/{ev}_null_{s}.mseed", f"raw/{ev}_resp.xml")
        tn, sn = M.m1b_matched_envelope(xn, R.FS, ctx); null = M.window_maxima(tn, sn, R.WARMUP_S, R.WINDOW_S, len(xn) / R.FS); null = null[np.isfinite(null)]
        t0e, xe = prep(f"raw/{ev}_{s}.mseed", f"raw/{ev}_resp.xml")
        te, se = M.m1b_matched_envelope(xe, R.FS, ctx)
        r = el[(el.event == ev) & (el.station == s)].iloc[0]; tpk = U(r.t_peak_utc) - t0e
        sc = M.window_max(te, se, tpk - 30, tpk + 30); m = (te >= tpk - 30) & (te <= tpk + 30); tbest = te[m][np.nanargmax(se[m])] - tpk
        # pre-arrival windows in the event file too (same-hour null, a second null)
        null2 = M.window_maxima(te, se, R.WARMUP_S, R.WINDOW_S, tpk - 90); null2 = null2[np.isfinite(null2)]
        k = int(np.sum(null >= sc)); n = len(null); rank = int(np.sum(null > sc)) + 1
        rows.append(dict(event=ev, station=s, m1b_score=sc, m1b_peak_minus_envelope_peak_s=float(tbest), n_null=n, k_null_ge=k, p_value=(k + 1) / (n + 1), p_floor=1 / (n + 1),
                         rank_among_null_plus_event=rank, null_median=float(np.median(null)), null_p95=float(np.quantile(null, .95)), null_max=float(null.max()),
                         n_null2=len(null2), k_null2_ge=int(np.sum(null2 >= sc)), snr_rms1_4_40_dB=r.snr_rms1_4_40_dB, rms1_peak_4_40_Pa=r.rms1_peak_4_40_Pa,
                         label="report" if (k + 1) / (n + 1) <= 0.05 else ("mark" if (k + 1) / (n + 1) <= 0.1 else ("screen" if (k + 1) / (n + 1) <= 0.3 else "none"))))
        print({a: (round(b, 4) if isinstance(b, float) else b) for a, b in rows[-1].items()}, flush=True)
pd.DataFrame(rows).to_csv("out/m1b_real_arrival.csv", index=False)
