"""Template bank from the KRAKEN broadband synthesis (template.py output). The 'h2' convention is used: it is the
one whose energy builds up to an abrupt end (the deep-sound-channel crescendo: fast high modes first, the slow loud
axial modes last); the other convention is its time reverse. Each range's 64 s circular series is rolled so that
its energy peak sits at 35 s and a 50 s window [0, 50] s is cut; the one-pole source spectrum for tau (flat ESD to
1/tau, f^-2 above) is applied, then the 5-40 Hz band-pass, resampling to FS, unit energy. Envelope templates are
the 0.5 s-smoothed squared series at 10 Hz, mean removed, unit energy. The cepstral band Q holds 80 % of the
2,200 km template's cepstral energy above 0.05 s (tau = 1 s)."""
from __future__ import annotations
import sys
from pathlib import Path
import numpy as np
from scipy import signal
sys.path.insert(0, str(Path(__file__).parent))
import preregistration as R
import methods as M

TLEN = 50.0
PEAK_AT = 35.0


def source_filter(x, fs, tau):
    """One-pole low-pass with corner 1/tau Hz (ESD flat to 1/tau, f^-2 above), zero-phase not used: causal minimum phase."""
    b, a = signal.butter(1, 1.0 / tau, btype="low", fs=fs)
    return signal.lfilter(b, a, x)


def pulse(T, r_key, tau, fs=R.FS):
    """Synthetic received pulse at FS for template range key (e.g. 'h2_2200.0') and tau; unit energy."""
    h = T[r_key]; fs0 = float(T["fs"])
    e = np.convolve(h ** 2, np.ones(int(fs0)) / fs0, "same")
    pk = int(np.argmax(e))
    h = np.roll(h, int(PEAK_AT * fs0) - pk)[: int(TLEN * fs0)]
    x = source_filter(h, fs0, tau)
    sos = signal.butter(4, list(R.BAND), btype="bandpass", fs=fs0, output="sos")
    x = signal.sosfiltfilt(sos, x)
    x = signal.resample_poly(x, int(fs), int(fs0))
    return (x / np.sqrt(np.sum(x ** 2))).astype(float)


def build(T, fs=R.FS):
    bank_wave, bank_env, keys = [], [], []
    for r in R.BANK_RANGES_KM:
        for tau in R.TAUS:
            p = pulse(T, f"h2_{r:.1f}", tau, fs)
            bank_wave.append(p); keys.append((r, tau))
            e = M.envelope(p, fs); e = e - e.mean(); bank_env.append(e / np.sqrt(np.sum(e ** 2)))
    pk = int(PEAK_AT * fs); pk_env = int(PEAK_AT * 10)
    # cepstral band from the 2,200 km tau = 1 template
    ref = pulse(T, "h2_2200.0", 1.0, fs)
    X = np.abs(np.fft.rfft(ref * np.hanning(len(ref)))); c = np.fft.irfft(np.log(X + 1e-12)); q = np.arange(len(c)) / fs
    m = (q >= 0.05) & (q <= len(c) / fs / 2); cc = c ** 2 * m; cs = np.cumsum(cc) / cc.sum()
    q_lo, q_hi = float(q[np.searchsorted(cs, 0.10)]), float(q[np.searchsorted(cs, 0.90)])
    return dict(bank_wave=bank_wave, bank_env=bank_env, bank_keys=keys, bank_peak_idx=pk, bank_env_peak_idx=pk_env, q_band=(q_lo, q_hi))
