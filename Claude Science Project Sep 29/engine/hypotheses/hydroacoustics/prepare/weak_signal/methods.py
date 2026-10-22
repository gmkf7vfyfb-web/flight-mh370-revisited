"""Detector statistics for the weak-signal trials, exactly as pre-registered in preregistration.py (METHODS).
Every function takes a band-passed series x (float), its sample rate fs, and a context dict (templates, SR
constants) and returns (t, s): statistic sample times (s) and values. A window's score is max(s) inside it."""
from __future__ import annotations
import numpy as np, warnings
warnings.filterwarnings("ignore", category=RuntimeWarning)
from scipy import signal, stats
import preregistration as R

EPS = 1e-30


def _roll_med_mad(v, n):
    """Median and MAD of the PRECEDING n samples (exclusive), min 10 samples; NaN before that."""
    import pandas as pd
    s = pd.Series(v)
    med = s.shift(1).rolling(n, min_periods=10).median().values
    mad = (s.shift(1) - pd.Series(med)).abs().rolling(n, min_periods=10).median().values * 1.4826
    return med, np.maximum(mad, 1e-9)


def _zprev(v, n=60):
    med, mad = _roll_med_mad(v, n)
    return (v - med) / mad


def m0a_stalta(x, fs, ctx=None, sta_s=2.0, lta_s=30.0, hop_s=0.1):
    y = np.asarray(x, float) ** 2
    cs = np.concatenate([[0.0], np.cumsum(y)])
    sta, lta, hop = int(sta_s * fs), int(lta_s * fs), max(int(hop_s * fs), 1)
    i = np.arange(lta, len(y) - sta + 1, hop)
    s = ((cs[i + sta] - cs[i]) / sta) / np.maximum((cs[i] - cs[i - lta]) / lta, EPS)
    return (i + sta / 2) / fs, s


def band_levels(x, fs, bands):
    ns = len(x) // fs
    f, p = signal.periodogram(np.asarray(x[: ns * fs], float).reshape(ns, fs), fs=fs, window="hann", detrend="constant", axis=-1)
    out = []
    for a, b in bands:
        m = (f >= a) & (f < b)
        out.append(10 * np.log10(np.maximum(p[:, m].sum(1) * (f[1] - f[0]), EPS)))
    return np.arange(ns) + 0.5, out


def m0b_bandenergy(x, fs, ctx=None, bands=((5, 20), (10, 40))):
    t, levs = band_levels(x, fs, bands)
    k = np.ones(3) / 3
    out = []
    for lev in levs:
        import pandas as pd
        med = pd.Series(lev).shift(1).rolling(60, min_periods=10).median().values
        out.append(np.convolve(lev - med, k, "same"))
    return t, np.nanmax(np.vstack(out), axis=0)


def _norm_xcorr(x, h, step):
    """Normalised cross-correlation of x with unit-energy template h; returns |rho| sampled every `step` samples,
    at the time of the template START."""
    L = len(h)
    c = signal.fftconvolve(x, h[::-1], mode="valid")                      # c[i] = sum x[i+j] h[j]
    cs = np.concatenate([[0.0], np.cumsum(np.asarray(x, float) ** 2)])
    ex = cs[L:] - cs[:-L]
    rho = np.abs(c) / np.sqrt(np.maximum(ex, EPS) * np.sum(h ** 2))
    i = np.arange(0, len(rho), step)
    return i, rho[i]


def m1a_matched_waveform(x, fs, ctx, hop_s=0.1):
    bank = ctx["bank_wave"]                # list of unit-energy templates at fs
    step = max(int(hop_s * fs), 1)
    best = None
    for h in bank:
        i, r = _norm_xcorr(np.asarray(x, float), h, step)
        best = r if best is None else np.maximum(best[: len(r)], r[: len(best)])
    i = i[: len(best)]
    # time of the template's energy peak, so that the window test is onset-relative
    return (i + ctx["bank_peak_idx"]) / fs, best


def envelope(x, fs, smooth_s=0.5, out_fs=10):
    e = np.asarray(x, float) ** 2
    k = int(smooth_s * fs)
    e = np.convolve(e, np.ones(k) / k, "same")
    d = fs // out_fs
    n = len(e) // d
    return e[: n * d].reshape(n, d).mean(1)


def m1b_matched_envelope(x, fs, ctx):
    e = envelope(x, fs)                         # 10 Hz
    best = None
    for h in ctx["bank_env"]:                   # 10 Hz, zero-mean, unit energy
        L = len(h)
        c = signal.fftconvolve(e, h[::-1], mode="valid")
        cs1 = np.concatenate([[0.0], np.cumsum(e)]); cs2 = np.concatenate([[0.0], np.cumsum(e ** 2)])
        s1 = cs1[L:] - cs1[:-L]; s2 = cs2[L:] - cs2[:-L]
        var = np.maximum(s2 - s1 ** 2 / L, EPS)
        r = c / np.sqrt(var * np.sum(h ** 2))   # correlation coefficient with the local mean removed
        best = r if best is None else np.maximum(best[: len(r)], r[: len(best)])
    i = np.arange(len(best))
    return (i + ctx["bank_env_peak_idx"]) / 10.0, best


def cepstrum_fraction(seg, fs, q_lo, q_hi, qmin=0.05):
    X = np.abs(np.fft.rfft(seg * np.hanning(len(seg))))
    c = np.fft.irfft(np.log(X + 1e-12))
    q = np.arange(len(c)) / fs
    tot = np.sum(c[(q >= qmin) & (q <= len(c) / fs / 2)] ** 2)
    inq = np.sum(c[(q >= q_lo) & (q <= q_hi)] ** 2)
    return inq / max(tot, EPS)


def m3_cepstral(x, fs, ctx, seg_s=8.0, hop_s=1.0):
    L, hop = int(seg_s * fs), int(hop_s * fs)
    starts = np.arange(0, len(x) - L + 1, hop)
    v = np.array([cepstrum_fraction(np.asarray(x[i: i + L], float), fs, *ctx["q_band"]) for i in starts])
    return (starts + L / 2) / fs, _zprev(v, 60)


def m4a_spectral_kurtosis(x, fs, ctx=None, block_s=8.0, hop_s=1.0):
    f, t, Z = signal.stft(np.asarray(x, float), fs=fs, window="hann", nperseg=fs, noverlap=fs - fs // 4, boundary=None, padded=False)
    m = (f >= R.BAND[0]) & (f <= R.BAND[1]) if fs > 2 * R.BAND[1] else (f >= R.PANEL_BAND[0]) & (f <= R.PANEL_BAND[1])
    P = np.abs(Z[m]) ** 2                       # [nf, nt], frames every 0.25 s
    nb, nh = int(block_s * 4), int(hop_s * 4)
    starts = np.arange(0, P.shape[1] - nb + 1, nh)
    out = np.empty(len(starts))
    for n, i in enumerate(starts):
        B = P[:, i: i + nb]
        sk = (B ** 2).mean(1) / np.maximum(B.mean(1) ** 2, EPS) - 2.0
        out[n] = sk.mean()
    return t[starts] + block_s / 2, out


def m4b_kurtosis(x, fs, ctx=None, frame_s=2.0, hop_s=1.0):
    L, hop = int(frame_s * fs), int(hop_s * fs)
    starts = np.arange(0, len(x) - L + 1, hop)
    v = np.array([stats.kurtosis(np.asarray(x[i: i + L], float)) for i in starts])
    return (starts + L / 2) / fs, v


def m5_synchrosqueezed(x, fs, ctx, block_s=8.0, hop_s=1.0, top=0.05):
    from ssqueezepy import ssq_stft
    xx = np.asarray(x, float)
    Tx, Sx, ssq_freqs, Sfs = ssq_stft(xx, fs=fs, n_fft=fs, hop_len=fs // 10)   # frames every 0.1 s
    band = R.BAND if fs > 2 * R.BAND[1] else R.PANEL_BAND
    m = (ssq_freqs >= band[0]) & (ssq_freqs <= band[1])
    P = np.abs(Tx[m]) ** 2
    nb, nh = int(block_s * 10), int(hop_s * 10)
    starts = np.arange(0, P.shape[1] - nb + 1, nh)
    v = np.empty(len(starts))
    for n, i in enumerate(starts):
        B = P[:, i: i + nb].ravel()
        k = max(int(top * B.size), 1)
        part = np.partition(B, B.size - k)[B.size - k:]
        v[n] = part.sum() / max(B.sum(), EPS)
    return (starts + nb / 2) / 10.0, _zprev(v, 60)


def bocpd(y, hazard=R.BOCPD_HAZARD, rmax=300, mu0=None, kappa0=1.0, alpha0=1.0, beta0=None):
    """Adams & MacKay (2007) with Normal-Gamma conjugate prior; returns P(r_t <= 2) per sample."""
    y = np.asarray(y, float)
    n = len(y)
    mu0 = np.nanmedian(y[:60]) if mu0 is None else mu0
    beta0 = (np.nanstd(y[:60]) ** 2 + 1e-6) if beta0 is None else beta0
    mu = np.array([mu0]); kap = np.array([kappa0]); al = np.array([alpha0]); be = np.array([beta0])
    logR = np.array([0.0])
    out = np.zeros(n)
    for t in range(n):
        yt = y[t]
        if not np.isfinite(yt):
            out[t] = 0.0
            continue
        # predictive Student-t
        df = 2 * al; scale = np.sqrt(be * (kap + 1) / (al * kap))
        lp = stats.t.logpdf(yt, df, loc=mu, scale=scale)
        lgrow = logR + lp + np.log(1 - hazard)
        lcp = np.logaddexp.reduce(logR + lp) + np.log(hazard)
        logR = np.concatenate([[lcp], lgrow])
        logR -= np.logaddexp.reduce(logR)
        # update sufficient statistics
        mu_n = (kap * mu + yt) / (kap + 1); kap_n = kap + 1; al_n = al + 0.5
        be_n = be + kap * (yt - mu) ** 2 / (2 * (kap + 1))
        mu = np.concatenate([[mu0], mu_n]); kap = np.concatenate([[kappa0], kap_n]); al = np.concatenate([[alpha0], al_n]); be = np.concatenate([[beta0], be_n])
        if len(logR) > rmax:
            logR, mu, kap, al, be = logR[:rmax], mu[:rmax], kap[:rmax], al[:rmax], be[:rmax]
            logR -= np.logaddexp.reduce(logR)
        out[t] = np.exp(np.logaddexp.reduce(logR[:3]))
    return out


def m6_changepoint(x, fs, ctx=None):
    band = R.BAND if fs > 2 * R.BAND[1] else R.PANEL_BAND
    t, (lev,) = band_levels(x, fs, [band])
    p = bocpd(lev)
    import pandas as pd
    s = pd.Series(lev)
    rising = (s.rolling(3, min_periods=1).mean() > s.shift(3).rolling(10, min_periods=3).mean()).values
    return t, np.where(rising, p, 0.0)


def m7_stochastic_resonance(x, fs, ctx, seed=1):
    k, sig = ctx["sr_k"], ctx["sr_sigma"]
    xx = np.asarray(x, float)
    import pandas as pd
    rms = pd.Series(xx ** 2).rolling(60 * fs, min_periods=5 * fs).mean().shift(1).bfill().values ** 0.5
    s = xx / np.maximum(rms, 1e-12)
    rng = np.random.default_rng(seed)
    dt = 1.0 / fs
    u = 1.0; sw = np.zeros(len(s) // fs)
    xi = rng.standard_normal(len(s)) * np.sqrt(dt) * sig
    prev = 1.0
    cnt = np.zeros(len(s), bool)
    for n in range(len(s)):
        u = u + dt * (u - u ** 3 + k * s[n]) + xi[n]
        sgn = 1.0 if u >= 0 else -1.0
        cnt[n] = sgn != prev
        prev = sgn
    ns = len(s) // fs
    rate = cnt[: ns * fs].reshape(ns, fs).sum(1).astype(float)
    med = pd.Series(rate).shift(1).rolling(60, min_periods=10).median().values
    return np.arange(ns) + 0.5, rate - med


METHODS = {
    "M0a_stalta": m0a_stalta, "M0b_bandenergy": m0b_bandenergy, "M1a_mf_waveform": m1a_matched_waveform,
    "M1b_mf_envelope": m1b_matched_envelope, "M3_cepstral": m3_cepstral, "M4a_spectral_kurtosis": m4a_spectral_kurtosis,
    "M4b_kurtosis": m4b_kurtosis, "M5_synchrosqueezed": m5_synchrosqueezed, "M6_changepoint": m6_changepoint,
    "M7_stochastic_resonance": m7_stochastic_resonance,
}


def window_max(t, s, a, b):
    m = (t >= a) & (t <= b) & np.isfinite(s)
    return float(s[m].max()) if m.any() else np.nan


def window_maxima(t, s, start, L, end):
    """Maxima over consecutive non-overlapping windows [start + kL, start + (k+1)L) up to end."""
    edges = np.arange(start, end - L + 1e-9, L)
    return np.array([window_max(t, s, a, a + L) for a in edges])
