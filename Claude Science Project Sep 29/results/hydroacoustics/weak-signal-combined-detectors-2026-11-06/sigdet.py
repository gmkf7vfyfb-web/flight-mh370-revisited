"""Spectral-signature detection below the noise: library.

Spectrogram -> whitening by a running-median noise spectrum -> three detectors
  D0  band energy 5-40 Hz, 30 s window over local median (T1-like reference)
  D1  locally optimal weak-signal detector: whitened, clipped spectrogram projected
      onto an impact template bank (spectral shape g(f) x envelope e(t)), max over bank
  D2  D1 with discrimination: impact bank score against the best clutter-class score
Synthetic source generators for injection (received-signal level; propagation folded in).
"""
from __future__ import annotations
import numpy as np
from scipy import signal, ndimage

FS = 250.0
NPS = 256            # 1.024 s
HOP = 128            # 0.512 s
DT = HOP / FS
F = np.fft.rfftfreq(NPS, 1 / FS)
BAND = (5.0, 40.0)
FB = (F >= 3.0) & (F <= 60.0)          # detector band for D1/D2 (H01W flat 1-100 Hz)
FB0 = (F >= BAND[0]) & (F <= BAND[1])   # band of D0 and of the SNR definition
CLIP = 4.0
MU_CLIP = 1 - np.exp(-CLIP)             # E[min(y,c)] for y ~ Exp(1)
VAR_CLIP = (2 - 2 * np.exp(-CLIP) * (CLIP + 1)) - MU_CLIP ** 2 + 0.0  # E[min(y,c)^2]-mu^2
# E[min(y,c)^2] = 2 - e^{-c}(c^2+2c+2) + c^2 e^{-c} = 2 - 2e^{-c}(c+1)


def spec(x):
    f, t, P = signal.spectrogram(x, fs=FS, window='hann', nperseg=NPS, noverlap=NPS - HOP,
                                 detrend='constant', scaling='density', mode='psd')
    return t, P            # P: (nf, nt) Pa^2/Hz


def noise_psd(P, win_s=600.0):
    n = int(win_s / DT) | 1
    return ndimage.median_filter(P, size=(1, n), mode='reflect') / np.log(2)   # median of Exp -> mean


def whiten(P, N):
    return P / N


# ---------------------------------------------------------------- spectral shapes
def src_shape(f, fc, a):
    """Received-source power spectrum shape: flat below corner fc, f^-a above."""
    f = np.maximum(f, 1e-3)
    return 1.0 / (1.0 + (f / fc) ** a)


def channel(f, f0=3.0, R_km=3000.0):
    """Deep-channel transfer (power): low-frequency mode cut-off and Thorp absorption."""
    f = np.maximum(f, 1e-3)
    fk = f / 1000.0
    thorp = 0.11 * fk**2 / (1 + fk**2) + 44 * fk**2 / (4100 + fk**2) + 2.75e-4 * fk**2 + 0.003  # dB/km
    return (1.0 / (1.0 + (f0 / f) ** 4)) * 10 ** (-(thorp - 0.003) * R_km / 10)


# ---------------------------------------------------------------- envelopes (power vs time)
def env_gamma(t, rise, decay):
    t = np.asarray(t, float)
    tp = np.clip(t, 0, None)
    e = np.where(t > 0, (1 - np.exp(-tp / max(rise, 1e-3))) ** 2 * np.exp(-tp / decay), 0.0)
    return e / e.max()


def env_train(t, period, n, width=1.0, decay=3.0):
    e = np.zeros_like(t, float)
    for k in range(n):
        e += env_gamma(t - k * period, width * 0.3, decay)
    return e / e.max()


# ---------------------------------------------------------------- template banks (whitened domain)
def norm(v):
    v = np.asarray(v, float); s = np.sqrt((v**2).sum()); return v / s if s > 0 else v


def bank_spectral(Nf, f=F[FB], R_km=3000.0):
    """Spectral templates per class in the whitened domain: g(f) = S(f) H(f) / N(f), unit norm.
    Nf: noise PSD on f (median over the record) -> per-record banks."""
    H = channel(f, R_km=R_km)
    B = {}
    # impact-like (loose class): corner 0.5-20 Hz, slope 0-5
    B['impact'] = [norm(src_shape(f, fc, a) * H / Nf) for fc in (0.7, 2, 5, 10, 20) for a in (0.0, 2.0, 3.0, 4.5)]
    # earthquake T-phase: corner 1-8 Hz, slope 2-4 (sits inside the loose impact family; separated by envelope)
    B['quake'] = [norm(src_shape(f, fc, a) * H / Nf) for fc in (1.5, 4, 8) for a in (2.0, 3.0, 4.0)]
    # airgun: broadband with bubble-pulse ripple (period Tb)
    B['airgun'] = [norm(src_shape(f, 30, 2) * (1 + 0.9 * np.cos(2 * np.pi * f * Tb)) * H / Nf)
                   for Tb in (0.08, 0.1, 0.125, 0.16, 0.2)]
    # ship and ice tremor: harmonic combs (narrow lines)
    def comb(f0, nh, bw=0.6):
        g = np.zeros_like(f)
        for k in range(1, nh + 1):
            g += np.exp(-0.5 * ((f - k * f0) / bw) ** 2)
        return g
    B['ship'] = [norm(comb(f0, 6) * src_shape(f, 30, 1) * H / Nf) for f0 in np.arange(5.0, 12.1, 0.5)]
    B['ice'] = [norm(comb(f0, 8, 0.8) * H / Nf) for f0 in np.arange(3.0, 8.1, 0.5)]
    return B


def bank_envelopes():
    t = np.arange(0, 240, DT)
    E = {}
    E['dive'] = [norm(env_gamma(t, r, d)[: int(min(240, 6 * d) / DT)]) for r in (0.7, 2.5) for d in (4, 10, 25)]
    def emergent(T):
        tt = t[: int(1.4 * T / DT)]
        e = np.sin(np.pi * np.clip(tt / T, 0, 1)) ** 2
        return norm(e)
    E['ditch'] = [emergent(T) for T in (20, 40, 70)]
    E['quake'] = [norm(env_gamma(t, r, d)[: int(min(240, 4 * d) / DT)]) for r in (8, 20) for d in (30, 70)]
    E['airgun'] = [norm(env_train(t[: int((8 * P + 6) / DT)], P, 8, 1.0, 2.0)) for P in range(8, 21, 2)]
    E['long'] = [norm(np.ones(int(T / DT))) for T in (60, 180)]
    return E


def whale_templates(f=F[FB]):
    """Non-separable whale call templates on (time, f) grid, unit norm, zero-mean free."""
    out = []
    # Antarctic blue whale Z-call: 27 Hz 8 s, sweep to 19 Hz over 2 s, 19 Hz 9 s
    for (fa, fb) in ((27.5, 19.0), (26.0, 18.5)):
        tt = np.arange(0, 19, DT)
        fi = np.where(tt < 8, fa, np.where(tt < 10, fa + (fb - fa) * (tt - 8) / 2, fb))
        T = np.exp(-0.5 * ((f[None, :] - fi[:, None]) / 0.7) ** 2)
        out.append(('zcall', T / np.sqrt((T**2).sum())))
    # fin whale 20 Hz pulse train: 1 s downsweep 24->17 Hz every IPI s, 8 pulses
    for ipi in (10, 13, 16, 20):
        tt = np.arange(0, 8 * ipi, DT)
        T = np.zeros((len(tt), len(f)))
        for k in range(8):
            m = (tt >= k * ipi) & (tt < k * ipi + 1.0)
            fi = 24 - 7 * (tt[m] - k * ipi)
            T[m] = np.exp(-0.5 * ((f[None, :] - fi[:, None]) / 1.0) ** 2)
        out.append(('fin', T / np.sqrt((T**2).sum())))
    # pygmy-blue-type long tonal with harmonics (20 Hz fundamental, 20-30 s units)
    for f0 in (18.0, 20.0, 22.0):
        tt = np.arange(0, 25, DT)
        g = sum(np.exp(-0.5 * ((f - k * f0) / 0.7) ** 2) for k in (1, 2, 3))
        T = np.tile(g, (len(tt), 1))
        out.append(('pygmy', T / np.sqrt((T**2).sum())))
    return out


# ---------------------------------------------------------------- detectors
def psi(y):
    return (np.minimum(y, CLIP) - MU_CLIP) / np.sqrt(VAR_CLIP)


def d0_band_energy(P, N, win_s=30.0):
    """T1-like: band energy 5-40 Hz in a 30 s sliding window over the 10-min running median, dB."""
    e = P[FB0].sum(0)
    n = int(round(win_s / DT))
    E = np.convolve(e, np.ones(n), 'same')
    ref = N[FB0].sum(0) * np.log(2) * n          # median-based reference
    return 10 * np.log10(E / ref)


def corr_same(z, e):
    """Correlate rows of z (K,T) with envelope e (L,), result aligned to template START, length T."""
    L = len(e)
    out = signal.fftconvolve(z, e[None, ::-1], mode='full', axes=1)[:, L - 1: L - 1 + z.shape[1]]
    return out


def d1_scores(Y, banks, envs, pairs, shape=False):
    """Locally optimal score: sum_t,f g(f) e(t) psi(y) / ||g e|| for each (spec class, env class) pair.
    Y: whitened spectrogram on FB (nf, nt). Returns dict class -> max-over-templates time series (nt,)
    aligned to template start time."""
    Z = psi(Y)
    if shape:   # remove the broadband level of each frame: level-invariant (shape-only) test
        Z = (Z - Z.mean(0, keepdims=True)) * np.sqrt(Z.shape[0] / (Z.shape[0] - 1))
    out = {}
    for name, (sc, ec) in pairs.items():
        G = np.array(banks[sc])                 # (K, nf), unit norm
        if shape:
            G = G - G.mean(1, keepdims=True); G = G / np.sqrt((G**2).sum(1, keepdims=True))
        zk = G @ Z                              # (K, nt)
        best = np.full(Z.shape[1], -np.inf)
        for e in envs[ec]:
            c = corr_same(zk, e).max(0)
            best = np.maximum(best, c)
        out[name] = best
    return out


def d1_whale(Y, wt, shape=False):
    Z = psi(Y)
    if shape:
        Z = (Z - Z.mean(0, keepdims=True)) * np.sqrt(Z.shape[0] / (Z.shape[0] - 1))
    best = np.full(Z.shape[1], -np.inf)
    for _, T in wt:
        L = T.shape[0]
        if shape:
            T = T - T.mean(1, keepdims=True); T = T / np.sqrt((T**2).sum())
        # sum over frequency of correlation of Z[f] with T[:, f]
        c = signal.fftconvolve(Z, T[::-1, :].T, mode='full', axes=1).sum(0)
        best = np.maximum(best, c[L - 1: L - 1 + Z.shape[1]])
    return best


PAIRS = {
    'dive':   ('impact', 'dive'),
    'ditch':  ('impact', 'ditch'),
    'quake':  ('quake', 'quake'),
    'airgun': ('airgun', 'airgun'),
    'ship':   ('ship', 'long'),
    'ice':    ('ice', 'long'),
}
IMPACT = ('dive', 'ditch')
CLUTTER = ('quake', 'airgun', 'ship', 'ice', 'whale')


def lag_max(s, half_frames):
    """Max of s over [t - half, t + half] (aligns start-aligned scores with centred windows)."""
    return ndimage.maximum_filter1d(s, size=2 * half_frames + 1, mode='nearest')


def all_scores(x, N=None, R_km=3000.0, wt=None):
    t, P = spec(x)
    if N is None:
        N = noise_psd(P)
    Y = P[FB] / N[FB]
    Nf = np.median(N[FB], axis=1)
    banks = bank_spectral(Nf, R_km=R_km)
    envs = bank_envelopes()
    wt = wt if wt is not None else whale_templates()
    S = d1_scores(Y, banks, envs, PAIRS)
    S['whale'] = d1_whale(Y, wt)
    S['d0'] = d0_band_energy(P, N)
    Ss = d1_scores(Y, banks, envs, PAIRS, shape=True)
    Ss['whale'] = d1_whale(Y, wt, shape=True)
    Ss['d0'] = S['d0']
    return t, P, N, S, Ss


def combine(S, smooth_frames=40):
    """Per-time combined statistics. Class scores are start-aligned; take local maxima over +-20 s
    so that classes compete for the same event."""
    L = {k: lag_max(v, smooth_frames) for k, v in S.items() if k != 'd0'}
    imp = np.maximum(L['dive'], L['ditch'])
    clut = np.max(np.vstack([L[c] for c in CLUTTER]), axis=0)
    d1 = imp
    d2 = 2 * imp - np.maximum(imp, clut)
    winner = np.argmax(np.vstack([L[c] for c in IMPACT + CLUTTER]), axis=0)
    out = dict(d0=lag_max(S['d0'], smooth_frames), d1=d1, d2=d2,
               dive=L['dive'], ditch=L['ditch'], clut=clut, winner=winner)
    for c in CLUTTER:
        out['c_' + c] = L[c]
    return out


CLASS_ORDER = IMPACT + CLUTTER


# ---------------------------------------------------------------- synthetic received signals
def shaped_noise(n, shape_fn, rng):
    w = rng.standard_normal(n)
    W = np.fft.rfft(w)
    f = np.fft.rfftfreq(n, 1 / FS)
    W *= np.sqrt(np.maximum(shape_fn(f), 0))
    return np.fft.irfft(W, n)


def synth(cls, rng, dur=240.0, R_km=None):
    """Received waveform (arbitrary scale) for class cls; returns x (n,), centre time of energy (s)."""
    n = int(dur * FS)
    t = np.arange(n) / FS
    R = R_km if R_km is not None else rng.uniform(1500, 4500)
    H = lambda f: channel(f, f0=rng.uniform(2, 4), R_km=R)
    t0 = 60.0
    if cls == 'dive':
        fc = np.exp(rng.uniform(np.log(1), np.log(20))); a = rng.uniform(2.0, 4.0)
        dec = rng.uniform(3, 20); rise = rng.uniform(0.3, 2.0)
        x = shaped_noise(n, lambda f: src_shape(f, fc, a) * H(f), rng) * np.sqrt(env_gamma(t - t0, rise, dec))
    elif cls == 'ditch':
        fc = np.exp(rng.uniform(np.log(0.5), np.log(10))); a = rng.uniform(2.0, 4.0)
        T = rng.uniform(15, 60); k = rng.integers(3, 9)
        e = np.zeros(n)
        for tk in np.sort(rng.uniform(0, T, k)):
            e += rng.lognormal(0, 0.7) ** 2 * env_gamma(t - t0 - tk, rng.uniform(0.5, 3), rng.uniform(3, 12))
        x = shaped_noise(n, lambda f: src_shape(f, fc, a) * H(f), rng) * np.sqrt(e / e.max())
    elif cls == 'quake':
        fc = rng.uniform(1.5, 8); a = rng.uniform(2, 4)
        x = shaped_noise(n, lambda f: src_shape(f, fc, a) * H(f), rng) * np.sqrt(env_gamma(t - t0, rng.uniform(5, 20), rng.uniform(15, 60)))
    elif cls == 'implosion':
        x = shaped_noise(n, lambda f: src_shape(f, 200, 2) * H(f), rng) * np.sqrt(env_gamma(t - t0, rng.uniform(0.2, 1), rng.uniform(3, 15)))
    elif cls == 'airgun':
        P = rng.uniform(8, 20); Tb = rng.uniform(0.08, 0.2); nsh = int((dur - t0) // P)
        e = env_train(t - t0, P, nsh, 1.0, rng.uniform(1, 4))
        x = shaped_noise(n, lambda f: src_shape(f, 30, 2) * (1 + 0.9 * np.cos(2 * np.pi * f * Tb)) * H(f), rng) * np.sqrt(e)
    elif cls == 'ship':
        f0 = rng.uniform(5, 12)
        x = shaped_noise(n, lambda f: src_shape(f, 30, 1) * H(f), rng) * 0.3
        for k in range(1, 7):
            x += np.sqrt(2) * rng.uniform(0.3, 1) * np.sin(2 * np.pi * (k * f0 + 0.02 * rng.standard_normal()) * t + rng.uniform(0, 6.3))
        x *= np.exp(-0.5 * ((t - dur / 2) / rng.uniform(300, 900)) ** 2)
    elif cls == 'ice':
        f0 = rng.uniform(3, 8); x = np.zeros(n); glide = rng.uniform(-0.01, 0.01)
        for k in range(1, 9):
            ph = 2 * np.pi * np.cumsum(k * f0 * (1 + glide * (t - t0) / 60)) / FS
            x += rng.uniform(0.3, 1) * np.sin(ph) / k ** 0.5
        x *= np.sqrt(env_gamma(t - t0, rng.uniform(10, 30), rng.uniform(60, 200)))
    elif cls == 'zcall':
        fa, fb = rng.uniform(26, 28), rng.uniform(18.5, 19.5)
        tt = t - t0
        fi = np.where(tt < 8, fa, np.where(tt < 10, fa + (fb - fa) * (tt - 8) / 2, fb))
        x = np.sin(2 * np.pi * np.cumsum(fi) / FS) * ((tt > 0) & (tt < 19))
    elif cls == 'fin':
        ipi = rng.uniform(10, 20); x = np.zeros(n)
        for k in range(int((dur - t0) // ipi)):
            tt = t - t0 - k * ipi; m = (tt >= 0) & (tt < 1.0)
            fi = 24 - 7 * tt
            ph = 2 * np.pi * np.cumsum(np.where(m, fi, 0)) / FS
            x += np.where(m, np.sin(ph) * np.sin(np.pi * np.clip(tt, 0, 1)), 0)
    else:
        raise ValueError(cls)
    return x, t0


def band_snr_scale(x, noise_band_power, target_db, win_s=30.0):
    """Scale x so that its max 30 s band (5-40 Hz) energy = target SNR x noise band energy in 30 s.
    noise_band_power: noise power in 5-40 Hz, Pa^2 (mean square)."""
    b, a = signal.butter(4, [BAND[0], BAND[1]], btype='band', fs=FS)
    xb = signal.filtfilt(b, a, x)
    n = int(win_s * FS)
    e = np.convolve(xb**2, np.ones(n), 'valid')
    emax = e.max()
    target = 10 ** (target_db / 10) * noise_band_power * n
    return x * np.sqrt(target / emax)
