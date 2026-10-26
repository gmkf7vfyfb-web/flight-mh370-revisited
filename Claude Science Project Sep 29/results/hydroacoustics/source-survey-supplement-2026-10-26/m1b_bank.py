"""Registered M1b envelope matched filter and its 18-template bank, copied from
prepare/searches_run_j/detectors.py (hypothesis/hydroacoustics, commit d88d48e) with the pre-registered constants
(BAND_MAIN 5-40 Hz, ENV_SMOOTH_S 0.5, ENV_FS 10, IMOS_BANK_RANGES, TAUS, TLEN 50 s, PEAK_AT 35 s)."""
import numpy as np
from scipy import signal
BAND_MAIN = (5.0, 40.0); ENV_SMOOTH_S, ENV_FS = 0.5, 10
IMOS_BANK_RANGES = (1800.0, 2200.0, 2376.1, 2600.0, 3000.0, 3703.5); TAUS = (0.1, 1.0, 10.0)
TLEN, PEAK_AT = 50.0, 35.0; PEAK_IDX_10HZ = 350; EPS = 1e-30

def _source_filter(x, fs, tau):
    b, a = signal.butter(1, 1.0 / tau, btype="low", fs=fs)
    return signal.lfilter(b, a, x)

def _pulse(T, key, tau, fs):
    h = T[key]; fs0 = float(T["fs"])
    e = np.convolve(h ** 2, np.ones(int(fs0)) / fs0, "same")
    pk = int(np.argmax(e))
    h = np.roll(h, int(PEAK_AT * fs0) - pk)[: int(TLEN * fs0)]
    x = _source_filter(h, fs0, tau)
    sos = signal.butter(4, list(BAND_MAIN), btype="bandpass", fs=fs0, output="sos")
    x = signal.sosfiltfilt(sos, x)
    x = signal.resample_poly(x, int(fs), int(fs0))
    return (x / np.sqrt(np.sum(x ** 2))).astype(float)

def envelope(x, fs, smooth_s=ENV_SMOOTH_S, out_fs=ENV_FS):
    e = np.asarray(x, float) ** 2
    k = max(int(smooth_s * fs), 1)
    e = np.convolve(e, np.ones(k) / k, "same")
    d = int(fs // out_fs); n = len(e) // d
    return e[: n * d].reshape(n, d).mean(1)

def bank_env(T, ranges, fs):
    out, keys = [], []
    for r in ranges:
        for tau in TAUS:
            p = _pulse(T, f"h2_{r:.1f}", tau, 100)
            if fs != 100:
                p = signal.resample_poly(p, fs, 100)
            e = envelope(p, fs); e = e - e.mean(); out.append(e / np.sqrt(np.sum(e ** 2))); keys.append((r, tau))
    return out, keys

def m1b_env(e10, bank):
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
    return (i + PEAK_IDX_10HZ) / float(ENV_FS), best
