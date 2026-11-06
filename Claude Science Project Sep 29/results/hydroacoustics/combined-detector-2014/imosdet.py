"""Combined weak-signal detector adapted to IMOS 307 s duty-cycled records (pre-registration v1.0, A4/B2).

Per record (250 Hz, 306.8 s): all statistics on a 5 s grid of centres (15..290 s).
  d0   band energy 8-40 Hz, 30 s window over the record median (dB)
  d1   impact spectral templates (loose bank), whitened by the record-median noise spectrum, 8-60 Hz
  s1   spectral shape change only (frame level removed)
  cimp successive-sample correlation matched to the impact lag pattern (AR(60) whitening fitted on the
       record outside +-30 s of the window; lags 4 ms-0.5 s; standardised per logger on background)
  pers envelope persistence (8-40 Hz envelope, 10/s; sign count against the rest of the record; fixed thin lag)
"""
import numpy as np
from scipy import signal, linalg, ndimage
from scipy.stats import binom
import sigdet as SD

FS = 250.0
NREC = 76700
F = SD.F
FBI = (F >= 8.0) & (F <= 60.0)
FB0I = (F >= 8.0) & (F <= 40.0)
CENT = np.arange(15.0, 291.0, 5.0)          # 56 centres
WIN = int(30 * FS); K = 125; P_AR = 60


def gain_shape(fg, G):
    """Relative instrument power response on F (normalised to its 20-40 Hz median)."""
    g = 10 ** (np.interp(F, fg, G) / 10)
    return g / np.median(g[(F >= 20) & (F <= 40)])


# ---------------------------------------------------------------- spectral part
def spectral(x, wt):
    t, P = SD.spec(x)
    N = np.maximum(np.median(P, axis=1, keepdims=True) / np.log(2), 1e-30)
    f = F[FBI]; Y = P[FBI] / N[FBI]; Nf = N[FBI, 0]
    banks = SD.bank_spectral(Nf, f=f); envs = SD.bank_envelopes()
    out = {}
    for shape, key in ((False, 'd1'), (True, 's1')):
        S = SD.d1_scores(Y, banks, envs, SD.PAIRS, shape=shape)
        S['whale'] = SD.d1_whale(Y, wt, shape=shape)
        L = {k: SD.lag_max(v, 40) for k, v in S.items()}
        imp = np.maximum(L['dive'], L['ditch'])
        out[key] = imp
        out[key + '_clut'] = np.max(np.vstack([L[c] for c in SD.CLUTTER]), axis=0)
        if key == 'd1':
            out['winner'] = np.argmax(np.vstack([L[c] for c in SD.IMPACT + SD.CLUTTER]), axis=0)
    e = P[FB0I].sum(0); n = int(round(30 / SD.DT))
    E = np.convolve(e, np.ones(n), 'same'); ref = np.median(e) * n
    out['d0'] = SD.lag_max(10 * np.log10(np.maximum(E, 1e-30) / ref), 40)
    # to the 5 s grid: max within +-2.5 s
    g = {}
    for k in ('d0', 'd1', 's1', 'd1_clut', 's1_clut'):
        v = out[k]; g[k] = np.array([np.nanmax(v[(t >= c - 2.5) & (t < c + 2.5)]) for c in CENT])
    w = out['winner']; g['winner'] = np.array([w[np.argmin(abs(t - c))] for c in CENT])
    return g


# ---------------------------------------------------------------- correlation part
def ar_whitener(xr, p=P_AR):
    x = xr - xr.mean(); nf = 1 << int(np.ceil(np.log2(2 * len(x))))
    r = np.fft.irfft(np.abs(np.fft.rfft(x, nf)) ** 2, nf)[: p + 1] / len(x)
    if not np.isfinite(r).all() or r[0] <= 0:
        return np.array([1.0])
    c = r[:p].copy(); c[0] *= 1 + 1e-6
    try:
        return np.concatenate([[1.0], -linalg.solve_toeplitz(c, r[1:p + 1])])
    except Exception:
        return np.array([1.0])


def lag_bank(A, gshape, R_km=3000.0):
    nf = 1 << 15; f = np.fft.rfftfreq(nf, 1 / FS)
    Hw = np.abs(np.fft.rfft(A, nf)) ** 2; G = np.interp(f, F, gshape)
    out = []
    for fc in (0.7, 2, 5, 10, 20):
        for al in (0.0, 2.0, 3.0, 4.5):
            S = SD.src_shape(f, fc, al) * SD.channel(f, R_km=R_km) * Hw * G
            ac = np.fft.irfft(S, nf)[: K + 1]; w = ac[1:] / ac[0]; out.append(w / np.linalg.norm(w))
    return np.array(out)


def whiteners(xref):
    """One AR whitener per centre, fitted on the record outside +-30 s of the centre (xref = noise reference)."""
    As = []
    for c in CENT:
        i0, i1 = int((c - 30) * FS), int((c + 30) * FS)
        ref = np.concatenate([xref[: max(i0, 0)], xref[min(i1, len(xref)):]])
        As.append(ar_whitener(ref))
    return As


def lags(x, As):
    z = np.full((len(CENT), K), np.nan); nf = 1 << 16
    for j, (c, A) in enumerate(zip(CENT, As)):
        a0 = int(c * FS) - WIN // 2; a0c = max(a0, 0)
        pre = max(0, a0c - 400)
        e = signal.lfilter(A, [1.0], x[pre: a0c + WIN])[a0c - pre:]
        e = e - e.mean(); ac = np.fft.irfft(np.abs(np.fft.rfft(e, nf)) ** 2, nf)[: K + 1]
        z[j] = np.sqrt(len(e)) * ac[1:] / ac[0]
    return z


def corr_imp(z, mu, sd, Wb):
    s = (z - mu) / sd
    return np.max(s @ Wb.T, 1)


# ---------------------------------------------------------------- persistence part
def envelope_db(x):
    b, a = signal.butter(4, [8.0, 40.0], btype='band', fs=FS)
    xb = np.abs(signal.filtfilt(b, a, x)); m = 25; n = len(xb) // m
    return 20 * np.log10(np.maximum(xb[: n * m].reshape(n, m).max(1), 1e-12))


def thin_lag(y):
    d = y - ndimage.median_filter(y, size=601, mode='reflect')
    nf = 1 << int(np.ceil(np.log2(2 * len(d))))
    ac = np.fft.irfft(np.abs(np.fft.rfft(d - d.mean(), nf)) ** 2, nf)[:200]; ac /= ac[0]
    i = np.where(ac < 0.1)[0]; return int(i[0]) if len(i) else 200


def persistence(y, tau, guard=15.0):
    out = np.full(len(CENT), np.nan)
    for j, c in enumerate(CENT):
        a, b = int((c - 15) * 10), int((c + 15) * 10)
        r = np.concatenate([y[: max(0, int((c - 15 - guard) * 10))], y[int((c + 15 + guard) * 10):]])
        if a < 0 or b > len(y) or len(r) < 600:
            continue
        w = y[a:b][::tau]; k = int((w > np.median(r)).sum())
        out[j] = -np.log10(max(binom.sf(k - 1, len(w), 0.5), 1e-300))
    return out


# ---------------------------------------------------------------- one record, all statistics
def record_stats(x, wt, gshape, mu, sd, tau, xref=None):
    """x: record (volts, 250 Hz). xref: noise reference for whitening (default x). Returns dict of 56-point traces."""
    xr = x if xref is None else xref
    g = spectral(x, wt)
    As = whiteners(xr); Wb = lag_bank(ar_whitener(xr), gshape)
    z = lags(x, As)
    g['z'] = z
    g['cimp'] = corr_imp(z, mu, sd, Wb) if mu is not None else np.full(len(CENT), np.nan)
    g['pers'] = persistence(envelope_db(x), tau)
    return g
