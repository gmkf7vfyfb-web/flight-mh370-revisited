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

# Amendment 2, A2.7. Nothing below this line changes the S10 statistic.
RAW_FEATURES = ["slope_db_oct", "centroid_oct", "bandwidth_oct", "flatness", "tonality_db", "sweep_hz_s",
                "harmonicity", "low_frac", "log_dur", "log_rise", "decay_db_s", "repeat_strength",
                "log_repeat_lag", "env_kurtosis", "rec_level_db", "n_lines"]
ENV_FEATURES = ["log_dur", "log_rise", "decay_db_s", "repeat_strength", "log_repeat_lag", "env_kurtosis"]
CLASSES = ["whale call", "ship", "earthquake sound arrival", "ice event", "airgun shot", "impact-like",
           "background noise only"]
KNOWN = ["whale call", "ship", "earthquake sound arrival", "ice event", "airgun shot"]


def broadband_excess(W: Whitened):
    """Per-frame broadband excess ratio sum_f (P - N) / sum_f N."""
    return ((W.P - W.N[None, :]).sum(1)) / W.N.sum()


def time_features(E, dt, k0, k1, ctx=None):
    """Time-shape features of excess series E (ratio to noise; frame step dt) in frames [k0, k1].
    ctx: the whole-record series for the repeat features (default E)."""
    E = np.asarray(E, float)
    ctx = E if ctx is None else np.asarray(ctx, float)
    k0, k1 = max(0, int(k0)), min(len(E) - 1, int(k1))
    seg = E[k0:k1 + 1]
    kp = k0 + int(np.argmax(seg))
    pk = max(E[kp], 1e-6)
    j0 = kp
    while j0 > k0 and E[j0 - 1] >= 0.5 * pk:
        j0 -= 1
    j1 = kp
    while j1 < k1 and E[j1 + 1] >= 0.5 * pk:
        j1 += 1
    dur = (j1 - j0 + 1) * dt
    a = kp
    lo = max(0, k0 - int(10 / dt))
    while a > lo and E[a - 1] >= 0.1 * pk:
        a -= 1
    b = a
    while b < kp and E[b] < 0.9 * pk:
        b += 1
    rise = max((b - a) * dt, dt)
    tot = 10 * np.log10(np.maximum(1 + E[kp:k1 + 1], 1e-3))
    decay = float(np.polyfit(np.arange(len(tot)) * dt, tot, 1)[0]) if len(tot) >= 3 else 0.0
    w = E[max(0, k0 - int(10 / dt)):min(len(E), k1 + int(10 / dt) + 1)]
    kurt = float(stats.kurtosis(w)) if len(w) > 4 and np.std(w) > 0 else 0.0
    # repeat structure over the record
    y = np.log1p(np.maximum(ctx, 0))
    y = y - y.mean()
    rs, rl = 0.0, np.nan
    if np.std(y) > 0 and len(y) > int(8 / dt):
        ac = signal.fftconvolve(y, y[::-1], mode="full")[len(y) - 1:]
        ac = ac / ac[0]
        L0, L1 = int(4 / dt), min(int(120 / dt), len(y) // 2)
        if L1 > L0:
            # normalise by overlap length
            ac_n = ac[L0:L1] * len(y) / (len(y) - np.arange(L0, L1))
            i = int(np.argmax(ac_n))
            rs, rl = float(ac_n[i]), (L0 + i) * dt
    return dict(log_dur=np.log10(dur), log_rise=np.log10(rise), decay_db_s=decay, repeat_strength=rs,
                log_repeat_lag=np.log10(rl) if np.isfinite(rl) else np.nan, env_kurtosis=kurt,
                t_peak_frame=kp, dur_s=dur, rise_s=rise)


def _fine_psd(x, fs=FS, nper=1000):
    f, p = signal.welch(x, fs=fs, window="hann", nperseg=nper, noverlap=3 * nper // 4, detrend="constant")
    return f, p


def features_raw(x, t_on, t_off, gain_f_hz, gain_db, W: Whitened | None = None, station_ref_db=np.nan,
                 fs=FS):
    """All A2.7.2 features for window [t_on, t_off] (s from the start of the record x, 250 Hz volts)."""
    if W is None:
        f, t, P = spectrogram(x, fs)
        W = whiten(f, t, P)
    f = W.f
    tt = W.t - NPERSEG / fs / 2                                   # frame start times
    E = broadband_excess(W)
    k0 = int(np.searchsorted(tt, t_on)); k1 = max(k0, int(np.searchsorted(tt, t_off)) - 1)
    k1 = min(k1, len(tt) - 1); k0 = min(k0, k1)
    tf = time_features(E, DT, k0, k1)
    kp = tf["t_peak_frame"]
    j0, j1 = kp, kp
    while j0 > k0 and E[j0 - 1] >= 0.5 * E[kp]:
        j0 -= 1
    while j1 < k1 and E[j1 + 1] >= 0.5 * E[kp]:
        j1 += 1
    exc = np.maximum((W.P[j0:j1 + 1] - W.N[None, :]).mean(0), 0)
    r = exc / W.N
    G = gain_lin(f, gain_f_hz, gain_db)
    ep = exc / G
    good = r > 0.25
    if good.sum() >= 5:
        slope = float(np.polyfit(np.log2(f[good]), 10 * np.log10(ep[good]), 1, w=np.sqrt(np.minimum(r[good], 10)))[0])
    else:
        slope = np.nan
    e = np.where(good, ep, 0.0)
    if e.sum() > 0:
        cen = float(np.log2((f * e).sum() / e.sum() / 8.0))
        low = float(e[f < 20].sum() / e.sum())
        f1432 = float(e[(f >= 14) & (f <= 32)].sum() / e.sum())
    else:
        cen, low, f1432 = np.nan, np.nan, np.nan
    rw = np.maximum(r, 0)
    if rw.sum() > 0:
        lf = np.log2(f)
        mu = (rw * lf).sum() / rw.sum()
        bw = float(np.sqrt((rw * (lf - mu) ** 2).sum() / rw.sum()))
    else:
        bw = 0.0
    rp = np.maximum(r, 1e-3)
    flat = float(np.exp(np.mean(np.log(rp))) / np.mean(rp))
    # fine-resolution (0.25 Hz) spectrum over max(window, 16 s), against the record's trimmed noise
    c = 0.5 * (tt[j0] + tt[j1] + 1.0)
    span = max(16.0, (tt[k1] - tt[k0]) + 1.0)
    a = int(max(0, (c - span / 2) * fs)); b = int(min(len(x), (c + span / 2) * fs))
    ff, ps = _fine_psd(np.asarray(x[a:b], float))
    # noise fine PSD from the kept (quiet) 16 s blocks of the record
    nb = int(16 * fs)
    blocks = [np.asarray(x[i:i + nb], float) for i in range(0, len(x) - nb + 1, nb)]
    bp = np.array([np.mean(bk ** 2) for bk in blocks]) if blocks else np.array([1.0])
    keep = [bk for bk, p_ in zip(blocks, bp) if p_ <= np.quantile(bp, 0.8)] or blocks
    pn = np.mean([_fine_psd(bk)[1] for bk in keep], axis=0)
    m = (ff >= 10) & (ff <= 100)
    ratio = ps[m] / pn[m]
    sm = signal.medfilt(ratio, 21)
    ton = float(10 * np.log10(np.max(ratio / np.maximum(sm, 1e-12))))
    ld = 10 * np.log10(np.maximum(ratio, 1e-6)); ld = ld - ld.mean()
    ac = np.correlate(ld, ld, "full")[len(ld) - 1:]
    ac = ac / max(ac[0], 1e-12)
    df = ff[1] - ff[0]
    L0, L1 = int(4 / df), int(40 / df)
    harm = float(np.max(ac[L0:L1])) if L1 > L0 else 0.0
    # sweep: peak frequency per signal frame
    fr = np.arange(j0, j1 + 1)
    if len(fr) >= 3:
        pkf = f[np.argmax(W.Z[fr], axis=1)]
        wts = np.maximum(E[fr], 1e-6)
        sw = float(np.polyfit(fr * DT, pkf, 1, w=np.sqrt(wts))[0])
    else:
        sw = 0.0
    # context: record level and persistent tonal lines
    lev = float(10 * np.log10(np.median((W.P / G[None, :]).sum(1))))
    fr_, prec = _fine_psd(np.asarray(x, float))
    mm = (fr_ >= 10) & (fr_ <= 100)
    rr = prec[mm] / signal.medfilt(prec[mm], 21)
    pk_idx, _ = signal.find_peaks(10 * np.log10(rr), height=6.0, distance=4)
    out = dict(slope_db_oct=slope, centroid_oct=cen, bandwidth_oct=bw, flatness=flat, tonality_db=ton,
               sweep_hz_s=sw, harmonicity=harm, low_frac=low, frac_14_32=f1432, rec_level_db=lev - station_ref_db,
               n_lines=float(len(pk_idx)), rec_level_abs_db=lev, peak_excess_db=float(10 * np.log10(1 + max(E[kp], 0))),
               t_peak_s=float(tt[kp]), j0=int(j0), j1=int(j1))
    out.update(tf)
    return out


def envelope_from_raw(x, fs=FS, band=(8.0, 40.0), fs_out=10.0):
    """Kadri-form envelope: band-pass then max |x| per 0.1 s bin (as reverse_detectors.raw_to_envelope)."""
    sos = signal.butter(4, [band[0], band[1]], btype="bandpass", fs=fs, output="sos")
    y = np.abs(signal.sosfiltfilt(sos, np.asarray(x, float)))
    k = int(round(fs / fs_out))
    n = len(y) // k
    return y[:n * k].reshape(n, k).max(1)


def envelope_excess(env, keep=0.8):
    p = np.asarray(env, float) ** 2
    N = np.mean(p[p <= np.quantile(p, keep)])
    return p / N - 1.0


def features_envelope(env, fs_env, t_on, t_off):
    """Envelope-only (time-shape) features of window [t_on, t_off] (s from the envelope start)."""
    E = envelope_excess(env)
    # 0.5 s smoothing to match the raw frame scale
    k = max(1, int(round(0.5 * fs_env)))
    Es = np.convolve(E, np.ones(k) / k, "same")
    dt = 1.0 / fs_env
    return time_features(Es, dt, int(t_on * fs_env), int(t_off * fs_env))


def l0_transients(W: Whitened, z_thr=6.0, min_sep_s=20.0):
    """Labelling transient finder: 5 s smoothed broadband excess; robust z >= z_thr; >= min_sep_s apart.
    Returns list of (t_on, t_off, t_peak, z) in record seconds (half-peak extent +/- 2 s, max 60 s)."""
    E = broadband_excess(W)
    Es = np.convolve(E, np.ones(10) / 10, "same")
    med = np.median(Es); mad = 1.4826 * np.median(np.abs(Es - med)) + 1e-12
    z = (Es - med) / mad
    tt = W.t - NPERSEG / FS / 2
    pk, _ = signal.find_peaks(z, height=z_thr, distance=int(min_sep_s / DT))
    out = []
    for k in pk:
        j0, j1 = k, k
        while j0 > 0 and Es[j0 - 1] >= 0.5 * Es[k]:
            j0 -= 1
        while j1 < len(Es) - 1 and Es[j1 + 1] >= 0.5 * Es[k]:
            j1 += 1
        t_on = max(0.0, tt[j0] - 2.0); t_off = min(tt[-1] + 1.0, tt[j1] + 3.0, t_on + 60.0)
        out.append((float(t_on), float(t_off), float(tt[k]), float(z[k])))
    return out


# ------------------------------------------------------------------ classifier
class SourceClassifier:
    """Robust-standardised multinomial logistic regression (L2, C = 1, balanced) with an open-set
    Gaussian gate (shared Ledoit-Wolf covariance). Optional temperature (A2.7.4 item 3)."""

    def __init__(self, features, C=1.0):
        self.features = list(features)
        self.C = C
        self.T = 1.0

    def _prep(self, X, fit=False):
        X = np.asarray(X, float)
        miss = ~np.isfinite(X)
        if fit:
            self.med = np.nanmedian(X, 0)
            q75, q25 = np.nanpercentile(X, 75, 0), np.nanpercentile(X, 25, 0)
            self.iqr = np.where((q75 - q25) > 1e-9, q75 - q25, 1.0)
            self.miss_cols = np.where(miss.any(0))[0]
        Xf = np.where(miss, self.med[None, :], X)
        Xs = np.clip((Xf - self.med) / self.iqr, -8, 8)
        return np.hstack([Xs, miss[:, self.miss_cols].astype(float)])

    def fit(self, X, y):
        from sklearn.linear_model import LogisticRegression
        from sklearn.covariance import LedoitWolf
        Xp = self._prep(X, fit=True)
        self.classes_ = np.array(sorted(set(y), key=lambda c: CLASSES.index(c) if c in CLASSES else 99))
        self.lr = LogisticRegression(C=self.C, class_weight="balanced", max_iter=5000)
        self.lr.fit(Xp, y)
        k = len(self.features)
        Xs = Xp[:, :k]
        self.means = {c: Xs[np.asarray(y) == c].mean(0) for c in self.classes_}
        resid = np.vstack([Xs[np.asarray(y) == c] - self.means[c] for c in self.classes_])
        self.cov_inv = np.linalg.pinv(LedoitWolf().fit(resid).covariance_)
        self.k = k
        return self

    def predict_proba(self, X):
        Xp = self._prep(X)
        logit = self.lr.decision_function(Xp) / self.T
        logit -= logit.max(1, keepdims=True)
        p = np.exp(logit)
        p /= p.sum(1, keepdims=True)
        order = list(self.lr.classes_)
        return p[:, [order.index(c) for c in self.classes_]]

    def open_set_p(self, X):
        Xs = self._prep(X)[:, :self.k]
        d2 = np.min([np.einsum("ij,jk,ik->i", Xs - m, self.cov_inv, Xs - m) for m in self.means.values()], axis=0)
        return stats.chi2.sf(d2, self.k), d2


def decide(feat, probs, classes, open_p, timing_match=None):
    """Asymmetry decision rule (Amendment 2, A2.7.5). timing_match: dict class -> association prob
    from the catalogue (earthquake / ice), or None."""
    p = dict(zip(classes, probs))
    tm = timing_match or {}
    g = lambda k, d=np.nan: feat.get(k, d)
    ev = {
        "earthquake sound arrival": tm.get("earthquake sound arrival", 0.0) >= 0.5,
        "ice event": tm.get("ice event", 0.0) >= 0.5,
        "whale call": (g("tonality_db", 0) >= 8) or (g("harmonicity", 0) >= 0.5)
                      or (abs(g("sweep_hz_s", 0)) >= 0.2 and g("frac_14_32", 0) >= 0.6),
        "ship": (g("rec_level_db", -99) >= 6) and (g("n_lines", 0) >= 3),
        "airgun shot": (g("repeat_strength", 0) >= 0.5 and 5 <= 10 ** g("log_repeat_lag", 0) <= 30)
                       or bool(g("shot_train", False)),
    }
    known = [c for c in KNOWN if c in p and p[c] >= 0.5 and ev[c]]
    if open_p < 1e-3:
        return "unclassified", ev
    if known:
        return max(known, key=lambda c: p[c]), ev
    # A2.11 deviation 1 (clarification fixed before any arrival window was opened):
    # a window that is most probably background noise is labelled so before the impact-like test.
    if p.get("background noise only", 0) >= 0.5:
        return "background noise only", ev
    # A2.11 deviation 2 (4 Nov 2026, after the windows were opened): on envelope-only data the
    # spectrum is unknown, so "broadband" cannot be shown and impact-like is not assigned.
    if not np.isfinite(g("bandwidth_oct", np.nan)):
        return "unclassified", ev
    broadband = (g("bandwidth_oct", 0) >= 0.25) and (g("tonality_db", 99) < 8)
    fast = 10 ** g("log_rise", 9) <= 3.0
    norep = g("repeat_strength", 0) < 0.5
    if broadband and fast and norep and not any(ev[c] for c in KNOWN):
        return "impact-like", ev
    if p.get("background noise only", 0) >= 0.5:
        return "background noise only", ev
    return "unclassified", ev


# ------------------------------------------------------------------ classify() entry point
_MODELS = None


def load_models(path=None):
    import pickle
    global _MODELS
    p = Path(path) if path else Path(__file__).with_name("classifier_models.pkl")
    _MODELS = pickle.load(open(p, "rb"))
    return _MODELS


def classify(candidate_window, model_path=None):
    """Classify one candidate window (Amendment 2, A2.7).

    candidate_window: dict with
      form       'raw' (IMOS waveform) or 'envelope' (Kadri-form envelope)
      x          raw: record waveform, 250 Hz volts (whole 307 s record preferred, for context)
      env        envelope: linear envelope samples; fs_env (default 10 Hz)
      t_on, t_off  window, s from the start of x / env
      station    e.g. 'IMOS3275' (raw; sets the gain reference and record-level reference)
      gain       (gain_f_hz, gain_db) for raw
      timing_match  optional dict {'earthquake sound arrival': P, 'ice event': P} from section 8
    Returns dict: label (asymmetry rule A2.7.5), probabilities per class, open_set_p, features,
    evidence flags. The label never removes a candidate on its own.
    """
    M = _MODELS or load_models(model_path)
    cw = candidate_window
    if cw.get("form", "raw") == "raw":
        ref = M["station_ref_db"].get(cw.get("station"), np.nan)
        ft = features_raw(np.asarray(cw["x"], float), cw["t_on"], cw["t_off"], *cw["gain"], station_ref_db=ref)
        model, names = M["raw"], RAW_FEATURES
        X = np.array([[ft.get(k, np.nan) for k in names]], float)
    else:
        ft = features_envelope(np.asarray(cw["env"], float), cw.get("fs_env", 10.0), cw["t_on"], cw["t_off"])
        ft = {"env_" + k: v for k, v in ft.items()}
        model, names = M["env"], ["env_" + k for k in ENV_FEATURES]
        X = np.array([[ft.get(k, np.nan) for k in names]], float)
    pr = model.predict_proba(X)[0]
    op, d2 = model.open_set_p(X)
    feats_for_rule = dict(ft)
    if cw.get("form", "raw") != "raw":
        feats_for_rule = {k[4:]: v for k, v in ft.items()}
        feats_for_rule["shot_train"] = bool(cw.get("shot_train", False))
    label, ev = decide(feats_for_rule, pr, list(model.classes_), float(op[0]), cw.get("timing_match"))
    return dict(label=label, probs=dict(zip(model.classes_, map(float, pr))), open_set_p=float(op[0]),
                mahalanobis2=float(d2[0]), evidence=ev, features=ft, form=cw.get("form", "raw"))
