"""Successive-sample correlation detectors (time domain), level-invariant.

1. Whiten the raw waveform with an AR(p) prediction-error filter fitted on noise (Yule-Walker).
   In whitened noise the sample autocorrelation at lags k>=1 has mean 0 and sd 1/sqrt(N).
2. For each 30 s window (5 s hop) compute rho(k), k = 1..K (normalised by rho(0): level-invariant).
3. Statistics
   - 'corr_any'  : template-free portmanteau Q = N sum_k rho(k)^2 (Ljung-Box form), as a z-score
                   (Wilson-Hilferty). Responds to ANY persistent structure.
   - 'corr_imp'  : matched: sqrt(N) sum_k w_k rho(k) / ||w||, w_k = autocorrelation of the whitened impact
                   spectrum (inverse transform of the template power shape). Max over the impact bank.
By Wiener-Khinchin, rho(k) is the Fourier transform of the whitened power spectrum, so 'corr_imp' is the
time-domain twin of the spectral-shape test; it ignores the lag-0 (level) term.
"""
import numpy as np
from scipy import signal, linalg
import sigdet as SD

FS = SD.FS
WIN = int(30 * FS)
HOP = int(5 * FS)
K = 125           # lags 1..125 (4 ms .. 0.5 s)
P_AR = 30


def ar_whitener(x_ref, p=P_AR):
    x = x_ref - x_ref.mean()
    nf = 1 << int(np.ceil(np.log2(2 * len(x))))
    r = np.fft.irfft(np.abs(np.fft.rfft(x, nf)) ** 2, nf)[: p + 1] / len(x)
    a = linalg.solve_toeplitz(r[:p], r[1:p + 1])
    return np.concatenate([[1.0], -a])


def whiten(x, A):
    return signal.lfilter(A, [1.0], x)


def band(x, lo=3.0, hi=60.0):
    b, a = signal.butter(4, [lo, hi], btype='band', fs=FS)
    return signal.filtfilt(b, a, x)


def lag_matrix(e):
    """rho(k) for k=1..K for each window; returns centres (s) and (nw, K)."""
    n = len(e)
    starts = np.arange(0, n - WIN + 1, HOP)
    idx = starts[:, None] + np.arange(WIN)[None, :]
    W = e[idx]
    W = W - W.mean(1, keepdims=True)
    nf = 1 << int(np.ceil(np.log2(2 * WIN)))
    F = np.fft.rfft(W, nf, axis=1)
    ac = np.fft.irfft(np.abs(F) ** 2, nf, axis=1)[:, : K + 1]
    rho = ac[:, 1:] / ac[:, :1]
    return (starts + WIN / 2) / FS, rho


def impact_lag_bank(A, R_km=3000.0):
    """Expected rho(k) pattern of each impact template after the same pipeline (band-pass + AR whitening)."""
    nf = 1 << 15
    f = np.fft.rfftfreq(nf, 1 / FS)
    Hw = np.abs(np.fft.rfft(A, nf)) ** 2                      # whitening filter power response
    b, a = signal.butter(4, [3.0, 60.0], btype='band', fs=FS)
    _, hb = signal.freqz(b, a, worN=f, fs=FS); Hb = np.abs(hb) ** 4   # filtfilt -> squared twice
    out = []
    for fc in (0.7, 2, 5, 10, 20):
        for al in (0.0, 2.0, 3.0, 4.5):
            S = SD.src_shape(f, fc, al) * SD.channel(f, R_km=R_km) * Hw * Hb
            ac = np.fft.irfft(S, nf)[: K + 1]
            w = ac[1:] / ac[0]
            out.append(w / np.linalg.norm(w))
    return np.array(out)


def corr_scores(e, Wbank):
    tc, rho = lag_matrix(e)
    N = WIN
    Q = N * (rho ** 2).sum(1)
    # Wilson-Hilferty chi2(K) -> z
    z_any = ((Q / K) ** (1 / 3) - (1 - 2 / (9 * K))) / np.sqrt(2 / (9 * K))
    z_imp = (np.sqrt(N) * rho @ Wbank.T).max(1)
    return tc, z_any, z_imp


def record_corr(x, A=None):
    xb = band(x)
    if A is None:
        A = ar_whitener(xb)
    e = whiten(xb, A)
    Wb = impact_lag_bank(A)
    return corr_scores(e, Wb), A


# ---------------------------------------------------------------- local-whitening version (used)
P_LOC = 200
REF_HALF = 300.0     # s each side
EXCL = 60.0          # s excluded each side of the window centre


def local_lags(x, centres, x_ref=None):
    """z(k)=sqrt(N) rho(k), k=1..K, for 30 s windows centred at `centres` (s). Whitening: AR(200) fitted on
    x_ref (default x) over centre +-300 s excluding +-60 s. Returns (nw, K)."""
    xr = x if x_ref is None else x_ref
    out = np.full((len(centres), K), np.nan)
    n = len(x); nf = 1 << 16
    for j, c in enumerate(centres):
        i = int(c * FS); a0 = i - WIN // 2
        if a0 - 2000 < 0 or a0 + WIN > n:
            continue
        lo = max(0, i - int(REF_HALF * FS)); hi = min(n, i + int(REF_HALF * FS))
        ref = np.concatenate([xr[lo: i - int(EXCL * FS)], xr[i + int(EXCL * FS): hi]])
        if len(ref) < 60 * FS or np.mean(ref == 0) > 0.01:
            continue
        A = ar_whitener(ref, P_LOC)
        e = whiten(x[a0 - 2000: a0 + WIN], A)[2000:]
        e = e - e.mean()
        ac = np.fft.irfft(np.abs(np.fft.rfft(e, nf)) ** 2, nf)[: K + 1]
        out[j] = np.sqrt(WIN) * ac[1:] / ac[0]
    return out


def record_bank(x):
    return impact_lag_bank(ar_whitener(x[np.isfinite(x)], P_LOC))


def corr_stats(z, mu, sd, Wb):
    s = (z - mu) / sd
    q = np.nansum(s ** 2, 1)
    z_any = ((q / K) ** (1 / 3) - (1 - 2 / (9 * K))) / np.sqrt(2 / (9 * K))
    z_imp = np.max(s @ Wb.T, 1)
    return z_any, z_imp


def local_whiteners(x_ref, centres):
    n = len(x_ref); As = []
    for c in centres:
        i = int(c * FS)
        lo = max(0, i - int(REF_HALF * FS)); hi = min(n, i + int(REF_HALF * FS))
        ref = np.concatenate([x_ref[lo: i - int(EXCL * FS)], x_ref[i + int(EXCL * FS): hi]])
        As.append(ar_whitener(ref, P_LOC))
    return As


def lags_with(x, centres, As):
    out = np.full((len(centres), K), np.nan); nf = 1 << 16
    for j, (c, A) in enumerate(zip(centres, As)):
        a0 = int(c * FS) - WIN // 2
        e = whiten(x[a0 - 2000: a0 + WIN], A)[2000:]; e = e - e.mean()
        ac = np.fft.irfft(np.abs(np.fft.rfft(e, nf)) ** 2, nf)[: K + 1]
        out[j] = np.sqrt(WIN) * ac[1:] / ac[0]
    return out


# ---------------------------------------------------------------- envelope persistence (pre-registered S2 form)
from scipy.stats import binom


def envelope_db(x, lo=5.0, hi=40.0):
    b, a = signal.butter(4, [lo, hi], btype='band', fs=FS)
    xb = np.abs(signal.filtfilt(b, a, x))
    m = int(0.1 * FS); n = len(xb) // m
    return 20 * np.log10(np.maximum(xb[: n * m].reshape(n, m).max(1), 1e-12))   # 10 samples/s


def thin_lag(y):
    d = y - np.median(y)
    nf = 1 << int(np.ceil(np.log2(2 * len(d))))
    ac = np.fft.irfft(np.abs(np.fft.rfft(d, nf)) ** 2, nf)[:200]; ac /= ac[0]
    i = np.where(ac < 0.1)[0]
    return int(i[0]) if len(i) else 200


def persistence(y, centres, tau, L=30.0, guard=30.0, ring=180.0):
    """-log10 binomial tail of the count of thinned samples above the ring median, per window."""
    out = np.full(len(centres), np.nan); fe = 10.0
    for j, c in enumerate(centres):
        a, b = int((c - L / 2) * fe), int((c + L / 2) * fe)
        r1 = y[max(0, int((c - L / 2 - guard - ring) * fe)): max(0, int((c - L / 2 - guard) * fe))]
        r2 = y[int((c + L / 2 + guard) * fe): int((c + L / 2 + guard + ring) * fe)]
        r = np.concatenate([r1, r2])
        if a < 0 or b > len(y) or len(r) < 600:
            continue
        w = y[a:b][::tau]; k = int((w > np.median(r)).sum()); n = len(w)
        out[j] = -np.log10(max(binom.sf(k - 1, n, 0.5), 1e-300))
    return out


TAU = {'H01W': 3, 'H08S': 10}      # fixed thinning lags (0.1 s samples): median local-detrended null lag


def instrument(x):
    """Instrument-like response for synthetic signals: 1 Hz high-pass, steep 95 Hz low-pass (anti-alias)."""
    s1 = signal.butter(2, 1.0, btype='high', fs=FS, output='sos')
    s2 = signal.butter(8, 95.0, btype='low', fs=FS, output='sos')
    return signal.sosfiltfilt(s2, signal.sosfiltfilt(s1, x))
