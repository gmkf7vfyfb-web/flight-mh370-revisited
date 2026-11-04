"""Reverse-sensing spectral search (S10) and source classifier.

Amendment 2 to the reverse-sensing methods specification (4 Nov 2026).
Propagation is used for TRAVEL TIME ONLY. Nothing here predicts a received level.

Contents
  I/O        read_dat_250, gain_lin
  spectra    spectrogram, whiten
  S10        template_bank, time_shapes, s10_scan, s10_peaks, synth_signal, inject
  features   features_raw, features_envelope, envelope_from_raw
  classifier SourceClassifier, classify

Units. Waveforms are volts at the logger input at 250 Hz (6 kHz decimated with
scipy.signal.resample_poly(1, 24)). Spectra are V^2/Hz. The system gain G(f) (dB)
converts a pressure-shape S_P(f) to a volts-shape: S_V = S_P * 10^(G/10).
The hydrophone sensitivity is a constant and cancels, because every statistic is
relative to the local noise.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
from scipy import signal, stats

__version__ = "1.0.0"

FS = 250.0            # Hz, analysis rate
NPERSEG = 250         # 1 s Hann frames, 1 Hz bins
HOP = 125             # 0.5 s hop
FMIN, FMAX = 8.0, 100.0
DT = HOP / FS         # 0.5 s
P_SUB = 4             # sub-bands of the shape-consistency (chi-square) test
MAX_SUPPORT_S = 90.0  # longest template support
MIN_INSIDE = 0.6      # fraction of template energy that must lie inside the record

# ------------------------------------------------------------------ I/O
def read_volts_6k(path) -> np.ndarray:
    """Port of Curtin load_loggerdatanew.m (as ns_readers.read_volts): 5 header lines,
    big-endian uint16, footer from 'Record'; volts, mean removed."""
    raw = Path(path).read_bytes()
    pos = 0
    for _ in range(5):
        pos = raw.index(b"\n", pos) + 1
    tail = raw[-1000:]
    footer_bytes = 1000 - tail.index(b"Record")
    end = len(raw) - footer_bytes - 2
    n = (end - pos) // 2
    x = np.frombuffer(raw, dtype=">u2", count=n, offset=pos).astype(np.float64) * (5.0 / 65536)
    return x - x.mean()


def read_dat_250(path) -> np.ndarray:
    """6 kHz DAT -> 250 Hz volts, the same decimation as the station data package."""
    return signal.resample_poly(read_volts_6k(path), 1, 24).astype(np.float32)


def gain_lin(f, gain_f_hz, gain_db):
    return 10 ** (np.interp(f, gain_f_hz, gain_db) / 10.0)


# ------------------------------------------------------------------ spectra
def spectrogram(x, fs=FS, nperseg=NPERSEG, hop=HOP, fmin=FMIN, fmax=FMAX):
    """One-sided PSD (V^2/Hz) on 1 s Hann frames, 0.5 s hop. Returns f, t (frame centre, s), P[t, f]."""
    f, t, Z = signal.stft(np.asarray(x, float), fs=fs, window="hann", nperseg=nperseg,
                          noverlap=nperseg - hop, detrend=False, boundary=None, padded=False,
                          scaling="psd")
    P = np.abs(Z) ** 2
    P[1:-1] *= 2.0
    m = (f >= fmin) & (f <= fmax)
    return f[m], t, P[m].T.copy()


@dataclass
class Whitened:
    f: np.ndarray
    t: np.ndarray
    P: np.ndarray          # [t, f] V^2/Hz
    N: np.ndarray          # [f] noise PSD (median over frames)
    sig: np.ndarray        # [f] robust sd of X = P/N - 1
    Z: np.ndarray          # [t, f] whitened excess


def whiten(f, t, P, noise_P=None, keep=0.8):
    """Local-noise whitening. The noise reference (the record itself, or noise_P) is
    trimmed to the fraction `keep` of frames with the lowest broadband power, so that
    transients do not bias it. N(f) = mean of the kept frames; X = P/N - 1;
    sigma(f) = sd of X over the kept frames; Z = X / sigma (zero mean, unit sd under noise)."""
    ref = P if noise_P is None else noise_P
    tot = ref.sum(axis=1)
    kept = ref[tot <= np.quantile(tot, keep)]
    N = kept.mean(axis=0)
    sig = np.maximum((kept / N - 1.0).std(axis=0), 1e-6)
    return Whitened(f, t, P, N, sig, (P / N - 1.0) / sig)


# ------------------------------------------------------------------ S10 template family
# Pre-registered ranges (Amendment 2, section A2.3, as revised by Pete's steer of 4 Nov 2026).
# LOOSE impact-like family: broadband, slope flat to steeply falling, corner below 1 Hz to 20 Hz,
# fast onset, duration < 1 s to about 60 s, level free. The Metz et al. (2022) F-35A shape is
# one labelled member (rows 0-2 of the bank), not the centre.
BANK_RANGES = dict(
    a=(0.0, 5.0),             # spectral slope exponent above the corner (0 = flat; 5 = -15 dB/octave); includes path tilt
    fc=(0.5, 20.0),           # corner frequency, Hz; log-uniform
    f_lo=(8.0, 20.0),         # receiver-side low-frequency cut-off (2nd-order high-pass), Hz
    f_hi=(15.0, 120.0),       # path high-frequency cut-off (2nd-order low-pass), Hz; log-uniform
    ripple_r=(0.0, 0.6),      # two-path amplitude ratio (0 in one draw in four)
    ripple_dt=(0.02, 0.5),    # two-path delay, s (ripple spacing 2-50 Hz); log-uniform
)
METZ_MEMBERS = [  # labelled members: F-35A at H11 (Metz, Obana and Fukao 2022), nominal and limits
    dict(a=3.1, fc=5.1, f_lo=8.0, f_hi=120.0, ripple_r=0.0, ripple_dt=0.1, ripple_ph=0.0),
    dict(a=2.65, fc=4.5, f_lo=8.0, f_hi=120.0, ripple_r=0.0, ripple_dt=0.1, ripple_ph=0.0),
    dict(a=3.5, fc=5.75, f_lo=8.0, f_hi=120.0, ripple_r=0.0, ripple_dt=0.1, ripple_ph=0.0),
]
TIME_RISE = (0.25, 1.0, 3.0)                    # s  (impulsive or fairly fast onset)
TIME_DECAY = (0.5, 1.0, 2.0, 4.0, 8.0, 16.0, 30.0)  # s  (durations < 1 s to about 60 s after spreading)
BANK_SEED = 20261104
BANK_N = 240


def draw_path_params(n=BANK_N, seed=BANK_SEED):
    """Fixed random draw of the path-distortion family (pre-registered seed).
    Constraint: f_hi >= 2 f_lo (at least one octave of bandwidth; the family stays broadband).
    One draw in four has no multipath ripple. Rows 0-2 are the labelled Metz et al. members."""
    rng = np.random.default_rng(seed)
    out = {k: [] for k in ("a", "fc", "f_lo", "f_hi", "ripple_r", "ripple_dt", "ripple_ph")}
    for m in METZ_MEMBERS:
        for k in out:
            out[k].append(m[k])
    while len(out["a"]) < n:
        p, _, _ = random_impact_draw(rng)
        for k in out:
            out[k].append(p[k])
    return {k: np.array(v) for k, v in out.items()}


def pressure_shape(f, a, fc, f_lo, f_hi, ripple_r, ripple_dt, ripple_ph=0.0):
    """Received pressure PSD shape (arbitrary level) of the loose impact-like family.
    Source-plus-path slope: flat below fc, f^-a above (a includes any path tilt).
    Receiver/path band: 2nd-order Butterworth high-pass at f_lo and low-pass at f_hi
    (power response). Multipath: two-path ripple |1 + r exp(-i(2 pi f dt + ph))|^2."""
    f = np.asarray(f, float)
    src = 1.0 / (1.0 + (f / fc) ** a) if a > 0 else np.ones_like(f)
    hp = (f / f_lo) ** 4 / (1.0 + (f / f_lo) ** 4)
    lp = 1.0 / (1.0 + (f / f_hi) ** 4)
    rip = np.abs(1.0 + ripple_r * np.exp(-1j * (2 * np.pi * f * ripple_dt + ripple_ph))) ** 2
    return src * hp * lp * rip


def template_bank(f, params=None):
    """Matrix [n_shapes, n_f] of pressure shapes, each normalised to unit sum."""
    params = draw_path_params() if params is None else params
    n = len(params["a"])
    S = np.empty((n, len(f)))
    for i in range(n):
        S[i] = pressure_shape(f, **{k: params[k][i] for k in params})
    return S / S.sum(axis=1, keepdims=True)


def time_shape(rise, decay, dt=DT, max_support=MAX_SUPPORT_S):
    """g(t) = (1 - exp(-t/rise)) exp(-t/decay), sampled at the frame hop, support <= max_support."""
    L = min(max_support, 3 * rise + 4 * decay)
    t = np.arange(0, L + dt / 2, dt)
    g = (1 - np.exp(-(t + dt / 2) / rise)) * np.exp(-t / decay)
    return g / g.max()


def time_shapes():
    out, meta = [], []
    for r in TIME_RISE:
        for d in TIME_DECAY:
            out.append(time_shape(r, d))
            meta.append((r, d))
    return out, meta


# ------------------------------------------------------------------ S10 scan
@dataclass
class ScanResult:
    t: np.ndarray            # frame-centre times (s, record time) = template onset times
    R: np.ndarray            # re-weighted statistic, max over bank (decision statistic)
    rho: np.ndarray          # plain matched-filter SNR of the best-R template
    chi2r: np.ndarray        # reduced shape chi-square of the best-R template
    i_spec: np.ndarray       # index of the best spectral shape
    i_time: np.ndarray       # index of the best time shape
    amp: np.ndarray          # fitted level (whitened units)
    meta: dict = field(default_factory=dict)


def _subbands(w2, p=P_SUB):
    """Split contiguous frequency bins into p groups of equal sum(w^2)."""
    c = np.cumsum(w2) / w2.sum()
    edges = np.searchsorted(c, np.arange(1, p) / p)
    return np.split(np.arange(len(w2)), edges)


def s10_scan(W: Whitened, gain_f_hz, gain_db, S_bank=None, tshapes=None):
    """S10 statistic at every frame (template onset) of one record.

    For spectral shape s (volts units) the whitened spectral weight is
    w = s G / (N sigma), normalised to ||w|| = 1; the template is h(t,f) = g(t) w(f).
    Matched-filter SNR at onset t0 (level free, positive part):
        rho = <Z, h(.-t0)> / ||g||.
    Shape consistency (Allen 2005, adapted to an incoherent power spectrogram): the
    frequency bins of w are split into P_SUB contiguous sub-bands of equal sum w^2;
    rho_i is the projection on sub-band i. With fitted level A = rho/||g||, the
    whitened-signal mean in a cell is A g w and the signal-to-noise power ratio is
    s_cell = A g w sigma, so a noise-like signal inflates the cell variance to
    (1 + s_cell)^2. Hence
        V_i = [Sg^2 Sw_i^2 + 2A Sg^3 S(w_i^3 sigma) + A^2 Sg^4 S(w_i^4 sigma^2)] / Sg^2
        chi2 = sum_i (rho_i - rho e_i)^2 / V_i,  e_i = S w_i^2,  chi2r = chi2/(P_SUB-1).
    Re-weighted SNR (Babak et al. 2013): R = rho if chi2r <= 1, otherwise
        R = rho / [(1 + chi2r^3)/2]^(1/6).
    Decision statistic: max of R over the whole bank (all spectral x time shapes).
    Sums over g use only the part of the template inside the record; onsets with less
    than MIN_INSIDE of the template energy inside are not scored.
    """
    f, Z = W.f, W.Z
    nT = Z.shape[0]
    if S_bank is None:
        S_bank = template_bank(f)
    if tshapes is None:
        tshapes, _ = time_shapes()
    G = gain_lin(f, gain_f_hz, gain_db)
    Wf = (S_bank * G[None, :]) / (W.N * W.sig)[None, :]
    Wf /= np.linalg.norm(Wf, axis=1, keepdims=True)
    ns, nf = Wf.shape
    # sub-band masks per shape -> [ns, P_SUB, nf]
    M = np.zeros((ns, P_SUB, nf))
    for s in range(ns):
        for i, idx in enumerate(_subbands(Wf[s] ** 2)):
            M[s, i, idx] = 1.0
    Wsub = Wf[:, None, :] * M                                     # [ns, P, nf]
    e = (Wsub ** 2).sum(-1)                                       # [ns, P]
    m3 = (Wsub ** 3 * W.sig[None, None, :]).sum(-1)
    m4 = (Wsub ** 4 * W.sig[None, None, :] ** 2).sum(-1)
    Ysub = Z @ Wsub.reshape(ns * P_SUB, nf).T                     # [nT, ns*P]
    bestR = np.full(nT, -np.inf); best_rho = np.zeros(nT); best_chi = np.zeros(nT)
    best_s = np.zeros(nT, int); best_j = np.zeros(nT, int); best_A = np.zeros(nT)
    for j, g in enumerate(tshapes):
        L = len(g)
        num = signal.fftconvolve(np.vstack([Ysub, np.zeros((L, ns * P_SUB))]), g[::-1, None], axes=0)[L - 1:L - 1 + nT]
        num = num.reshape(nT, ns, P_SUB)
        n_in = np.clip(nT - np.arange(nT), 0, L)
        cg = lambda m: np.concatenate([[0.0], np.cumsum(g ** m)])[n_in]
        G2, G3, G4 = cg(2), cg(3), cg(4)
        ok = G2 >= MIN_INSIDE * np.sum(g ** 2)
        sq = np.sqrt(np.maximum(G2, 1e-12))
        rho_i = num / sq[:, None, None]
        rho = rho_i.sum(-1)                                       # [nT, ns]
        A = np.maximum(rho, 0) / sq[:, None]
        V = (e[None] + 2 * A[..., None] * (G3 / np.maximum(G2, 1e-12))[:, None, None] * m3[None]
             + (A ** 2)[..., None] * (G4 / np.maximum(G2, 1e-12))[:, None, None] * m4[None])
        chi = ((rho_i - rho[..., None] * e[None]) ** 2 / np.maximum(V, 1e-12)).sum(-1) / (P_SUB - 1)
        R = np.where(chi <= 1, rho, rho / ((1 + chi ** 3) / 2) ** (1 / 6))
        R[~ok] = -np.inf
        R[rho <= 0] = np.where(ok[:, None], rho, -np.inf)[rho <= 0]
        s_arg = R.argmax(1); Rm = R[np.arange(nT), s_arg]
        upd = Rm > bestR
        bestR[upd] = Rm[upd]; best_s[upd] = s_arg[upd]; best_j[upd] = j
        best_rho[upd] = rho[np.arange(nT), s_arg][upd]; best_chi[upd] = chi[np.arange(nT), s_arg][upd]
        best_A[upd] = A[np.arange(nT), s_arg][upd]
    bestR[~np.isfinite(bestR)] = np.nan
    return ScanResult(W.t - NPERSEG / FS / 2, bestR, best_rho, best_chi, best_s, best_j, best_A)


def s10_peaks(sr: ScanResult, thr, min_sep_s=10.0, t_lo=-np.inf, t_hi=np.inf):
    """Local maxima of R at least min_sep_s apart with R >= thr inside [t_lo, t_hi]."""
    R = np.where(np.isfinite(sr.R), sr.R, -np.inf)
    m = (sr.t >= t_lo) & (sr.t <= t_hi) & (R >= thr)
    idx = np.where(m)[0]
    idx = idx[np.argsort(-R[idx])]
    keep = []
    for i in idx:
        if all(abs(sr.t[i] - sr.t[j]) >= min_sep_s for j in keep):
            keep.append(i)
    return sorted(keep)


# ------------------------------------------------------------------ synthetic signals
def synth_signal(n, onset_s, p_shape, rise, decay, gain_f_hz, gain_db, rng, fs=FS):
    """Noise-like transient: Gaussian noise with volts-PSD shape S_P(f) G(f), multiplied by
    sqrt(g(t)). Returns the signal (unit arbitrary) of length n."""
    nfft = int(2 ** np.ceil(np.log2(n)))
    fr = np.fft.rfftfreq(nfft, 1 / fs)
    S = pressure_shape(np.maximum(fr, 0.1), **p_shape) * gain_lin(fr, gain_f_hz, gain_db)
    S[(fr < 1.0)] = 0.0
    w = rng.normal(size=nfft)
    y = np.fft.irfft(np.fft.rfft(w) * np.sqrt(S), nfft)[:n]
    t = np.arange(n) / fs - onset_s
    g = np.where(t >= 0, (1 - np.exp(-np.maximum(t, 0) / rise)) * np.exp(-np.maximum(t, 0) / decay), 0.0)
    g[t > MAX_SUPPORT_S] = 0.0
    return y * np.sqrt(g)


def band_power(x, fs=FS, band=(FMIN, FMAX)):
    f, t, P = spectrogram(x, fs, fmin=band[0], fmax=band[1])
    return t, P.sum(axis=1) * (f[1] - f[0])


def inject(x, sig, onset_s, snr_db, fs=FS):
    """Scale sig so that (mean signal band power over the first 10 s after onset) /
    (median band power of x, 8-100 Hz, 1 s frames) = snr_db (spec section 11.4)."""
    _, pn = band_power(x, fs)
    i0, i1 = int(onset_s * fs), int((onset_s + 10) * fs)
    _, ps = band_power(sig[i0:i1], fs)
    k = math.sqrt(np.median(pn) * 10 ** (snr_db / 10) / max(np.mean(ps), 1e-30))
    return x + k * sig, k


def random_impact_draw(rng):
    """One draw from the loose S10 family (spectral and time parameters), f_hi >= 2 f_lo."""
    R = BANK_RANGES
    lu = lambda lo, hi: float(np.exp(rng.uniform(np.log(lo), np.log(hi))))
    while True:
        f_lo = rng.uniform(*R["f_lo"])
        f_hi = lu(*R["f_hi"])
        if f_hi >= 2 * f_lo:
            break
    p = dict(a=rng.uniform(*R["a"]), fc=lu(*R["fc"]), f_lo=f_lo, f_hi=f_hi,
             ripple_r=0.0 if rng.uniform() < 0.25 else rng.uniform(*R["ripple_r"]),
             ripple_dt=lu(*R["ripple_dt"]), ripple_ph=rng.uniform(0, 2 * np.pi))
    rise = lu(TIME_RISE[0], TIME_RISE[-1])
    decay = lu(TIME_DECAY[0], TIME_DECAY[-1])
    return p, rise, decay


# ------------------------------------------------------------------ features
