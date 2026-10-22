"""Detector statistics for the run J searches, exactly as pre-registered in preregistration.py section 3-4.
IMOS path: 500 Hz decimated volts (imos_noise.read_volts/decimate) -> BE per band (1 s Hann periodogram), and the
5-40 Hz band-passed 100 Hz series -> D1 (STA 2 / LTA 30) and M1b (envelope matched filter, 18-template bank).
Panel path: 20 Hz series -> BE (2-5, 5-9 Hz), D1 on 1-9 Hz, M1b with the station's range templates.
Every statistic returns (t_s, s); a window's score is max(s) in the window, timed at the maximum."""
from __future__ import annotations
import sys
from pathlib import Path
import numpy as np, pandas as pd
from scipy import signal
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import preregistration as R
# weak_signal/bank.py and weak_signal/common.py are NOT imported (their `import preregistration` would resolve to this
# folder's module); the two helpers needed are copied verbatim below with their pre-registered constants.

SOS_540 = signal.butter(4, list(R.BAND_MAIN), btype="bandpass", fs=R.FS_D, output="sos")
SOS_P = signal.butter(4, list(R.PANEL_BAND), btype="bandpass", fs=R.PANEL_FS, output="sos")
EPS = 1e-30


# ---- template bank ----------------------------------------------------------------------------------------------
TLEN, PEAK_AT = 50.0, 35.0          # weak_signal/bank.py conventions


def _source_filter(x, fs, tau):
    b, a = signal.butter(1, 1.0 / tau, btype="low", fs=fs)
    return signal.lfilter(b, a, x)


def _pulse(T, key, tau, fs):
    """weak_signal/bank.pulse, copied: 'h2' series rolled to peak at 35 s, 50 s cut, one-pole source for tau,
    5-40 Hz band-pass, resampled to fs, unit energy."""
    h = T[key]; fs0 = float(T["fs"])
    e = np.convolve(h ** 2, np.ones(int(fs0)) / fs0, "same")
    pk = int(np.argmax(e))
    h = np.roll(h, int(PEAK_AT * fs0) - pk)[: int(TLEN * fs0)]
    x = _source_filter(h, fs0, tau)
    sos = signal.butter(4, list(R.BAND_MAIN), btype="bandpass", fs=fs0, output="sos")
    x = signal.sosfiltfilt(sos, x)
    x = signal.resample_poly(x, int(fs), int(fs0))
    return (x / np.sqrt(np.sum(x ** 2))).astype(float)


def emulate_plot(x500, fs_out=R.PANEL_FS, bin_s=0.069):
    """weak_signal/common.emulate_plot, copied: 5-40 Hz series at 500 Hz -> per-bin min and max as vertices -> interp."""
    y = signal.sosfiltfilt(SOS_540, x500)
    nb = int(bin_s * R.FS_D)
    n = len(y) // nb
    Y = y[: n * nb].reshape(n, nb)
    imin, imax = Y.argmin(1), Y.argmax(1)
    base = np.arange(n) * nb
    tv = np.concatenate([base + imin, base + imax]) / R.FS_D
    pv = np.concatenate([Y[np.arange(n), imin], Y[np.arange(n), imax]])
    o = np.argsort(tv)
    tg = np.arange(0, len(y) / R.FS_D, 1 / fs_out)
    return np.interp(tg, tv[o], pv[o]).astype(np.float32)


def envelope(x, fs, smooth_s=R.ENV_SMOOTH_S, out_fs=R.ENV_FS):
    e = np.asarray(x, float) ** 2
    k = max(int(smooth_s * fs), 1)
    e = np.convolve(e, np.ones(k) / k, "same")
    d = int(fs // out_fs); n = len(e) // d
    return e[: n * d].reshape(n, d).mean(1)


def bank_env(T, ranges, fs):
    """Zero-mean unit-energy envelope templates at 10 Hz for the given ranges x TAUS."""
    out, keys = [], []
    for r in ranges:
        for tau in R.TAUS:
            p = _pulse(T, f"h2_{r:.1f}", tau, 100)
            if fs != 100:
                p = signal.resample_poly(p, fs, 100)
            e = envelope(p, fs); e = e - e.mean(); out.append(e / np.sqrt(np.sum(e ** 2))); keys.append((r, tau))
    return out, keys


PEAK_IDX_10HZ = 350   # bank.PEAK_AT (35 s) at 10 Hz


# ---- statistics -------------------------------------------------------------------------------------------------
def d1_stalta(x, fs, sta_s=R.STA_S, lta_s=R.LTA_S, hop_s=R.HOP_S):
    y = np.asarray(x, float) ** 2
    cs = np.concatenate([[0.0], np.cumsum(y)])
    sta, lta, hop = int(sta_s * fs), int(lta_s * fs), max(int(hop_s * fs), 1)
    i = np.arange(lta, len(y) - sta + 1, hop)
    s = ((cs[i + sta] - cs[i]) / sta) / np.maximum((cs[i] - cs[i - lta]) / lta, EPS)
    return (i + sta / 2) / fs, s


def m1b_env(e10, bank):
    """Envelope matched filter on a 10 Hz envelope e10; returns (t_s at the template energy peak, max rho over bank)."""
    best = None
    for h in bank:
        L = len(h)
        if len(e10) < L + 2:
            return np.array([]), np.array([])
        c = signal.fftconvolve(e10, h[::-1], mode="valid")
        cs1 = np.concatenate([[0.0], np.cumsum(e10)]); cs2 = np.concatenate([[0.0], np.cumsum(e10 ** 2)])
        s1 = cs1[L:] - cs1[:-L]; s2 = cs2[L:] - cs2[:-L]
        var = np.maximum(s2 - s1 ** 2 / L, EPS)
        r = c / np.sqrt(var * np.sum(h ** 2))
        best = r if best is None else np.maximum(best[: len(r)], r[: len(best)])
    i = np.arange(len(best))
    return (i + PEAK_IDX_10HZ) / float(R.ENV_FS), best


def band_levels_1s(x, fs, bands):
    ns = len(x) // fs
    f, p = signal.periodogram(np.asarray(x[: ns * fs], float).reshape(ns, fs), fs=fs, window="hann", detrend="constant", axis=-1)
    df = f[1] - f[0]
    out = {}
    for a, b in bands:
        m = (f >= a) & (f < b)
        out[(a, b)] = 10 * np.log10(np.maximum(p[:, m].sum(1) * df, EPS))
    return np.arange(ns) + 0.5, out


def be_stats(x, fs, bands):
    """Band energy per band: 1 s level minus the median of the preceding 60 s, 3 s running mean (dB)."""
    t, lev = band_levels_1s(x, fs, bands)
    k = np.ones(R.BE_MEAN_S) / R.BE_MEAN_S
    out = {}
    for b, v in lev.items():
        med = pd.Series(v).shift(1).rolling(R.BE_MED_S, min_periods=10).median().values
        out[b] = (t, np.convolve(v - med, k, "same"))
    return out, lev


def window_scores(t, s, t_end, start=R.WARMUP_S, L=R.WINDOW_S):
    """Max of s in each non-overlapping L s window from `start` to t_end; returns (w_start, score, t_of_max)."""
    ws, sc, tm = [], [], []
    a = start
    while a + L <= t_end + 1e-6:
        m = (t >= a) & (t < a + L) & np.isfinite(s)
        if m.any():
            j = np.argmax(np.where(m, s, -np.inf)); ws.append(a); sc.append(float(s[j])); tm.append(float(t[j]))
        a += L
    return np.array(ws), np.array(sc), np.array(tm)


# ---- full pipelines ---------------------------------------------------------------------------------------------
def imos_series(x500):
    """From the 500 Hz series: (x100 band-passed 5-40 Hz, e10 envelope)."""
    y = signal.sosfiltfilt(SOS_540, x500)
    x100 = signal.decimate(y, R.FS_D // R.FS, ftype="fir", zero_phase=True)
    return x100, envelope(x100, R.FS)


def imos_stats(x500, bank):
    x100, e10 = imos_series(x500)
    out = {}
    t, s = d1_stalta(x100, R.FS); out["D1"] = (t, s)
    t, s = m1b_env(e10, bank); out["M1b"] = (t, s)
    be, lev = be_stats(x500, R.FS_D, R.BANDS)
    for b, (t, s) in be.items():
        out[f"BE_{R.BAND_LABEL(b)}"] = (t, s)
    return out, lev


def panel_stats(x20, bank):
    xb = signal.sosfiltfilt(SOS_P, np.asarray(x20, float))
    out = {}
    t, s = d1_stalta(xb, R.PANEL_FS); out["D1"] = (t, s)
    t, s = m1b_env(envelope(xb, R.PANEL_FS), bank); out["M1b"] = (t, s)
    be, lev = be_stats(xb, R.PANEL_FS, R.PANEL_BANDS)
    for b, (t, s) in be.items():
        out[f"BE_{R.BAND_LABEL(b)}"] = (t, s)
    return out, lev


def scores_all(stats, t_end):
    return {k: window_scores(t, s, t_end) for k, (t, s) in stats.items()}
