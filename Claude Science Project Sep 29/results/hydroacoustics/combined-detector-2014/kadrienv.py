"""Kadri Fig. 9 envelope stations (Cape Leeuwin, Diego Garcia South): band energy and envelope persistence only.

Envelope: max |pressure| of the digitised vertices in 0.1 s bins; gaps shorter than 0.3 s are filled from the
previous bin; longer gaps are missing. Statistics on a 5 s grid (absolute s after 2014-03-08 00:00 UTC):
  E    10 log10( mean env^2 in the 30 s window / median env^2 in the ring )
  pers -log10 binomial tail of the count of thinned envelope samples (dB) above the ring median
Ring: 180 s on each side outside a 30 s guard (the available part at the trace ends; >= 60 s required).
Null: the trace's own distribution (point ranks; window maxima from random windows in the trace).
"""
import numpy as np, pandas as pd
from scipy import ndimage
from scipy.stats import binom

STEP = 5.0


def envelope(kv, station):
    d = kv[kv.station == station].sort_values('t_s')
    t0, t1 = np.floor(d.t_s.min()), np.ceil(d.t_s.max())
    edges = np.arange(t0, t1 + 0.1, 0.1); idx = np.digitize(d.t_s.values, edges) - 1
    env = np.full(len(edges) - 1, np.nan)
    a = np.abs(d.pressure_pa.values)
    for i, v in zip(idx, a):
        if 0 <= i < len(env) and (np.isnan(env[i]) or v > env[i]):
            env[i] = v
    # fill gaps shorter than 0.3 s (<= 2 empty bins)
    isn = np.isnan(env); lab, n = ndimage.label(isn)
    for k in range(1, n + 1):
        w = np.where(lab == k)[0]
        if len(w) <= 2 and w[0] > 0:
            env[w] = env[w[0] - 1]
    return edges[:-1], env


def thin_lag(y):
    yy = np.where(np.isfinite(y), y, np.nanmedian(y))
    d = yy - ndimage.median_filter(yy, size=601, mode='reflect')
    nf = 1 << int(np.ceil(np.log2(2 * len(d))))
    ac = np.fft.irfft(np.abs(np.fft.rfft(d - d.mean(), nf)) ** 2, nf)[:200]; ac /= ac[0]
    i = np.where(ac < 0.1)[0]; return int(i[0]) if len(i) else 200


def traces(kv, station):
    t, env = envelope(kv, station)
    y = 20 * np.log10(np.maximum(env, 1e-12)); y[~np.isfinite(env)] = np.nan
    p2 = env ** 2; tau = thin_lag(y)
    cent = np.arange(t[0] + 15, t[-1] - 15 + 1e-6, STEP)
    E = np.full(len(cent), np.nan); P = np.full(len(cent), np.nan)
    for j, c in enumerate(cent):
        w = (t >= c - 15) & (t < c + 15)
        r = ((t >= c - 225) & (t < c - 45)) | ((t >= c + 45) & (t < c + 225))
        wv, rv = p2[w], p2[r]
        if np.isfinite(wv).mean() < 0.8 or np.isfinite(rv).sum() < 600:
            continue
        E[j] = 10 * np.log10(np.nanmean(wv) / np.nanmedian(rv))
        yw = y[w][::tau]; yw = yw[np.isfinite(yw)]; k = int((yw > np.nanmedian(y[r])).sum())
        P[j] = -np.log10(max(binom.sf(k - 1, len(yw), 0.5), 1e-300))
    return pd.DataFrame(dict(station=station, t_s=cent, E=E, pers=P, tau=tau))


def rank_p(v):
    """Upper-tail rank probability within the trace itself."""
    v = np.asarray(v, float); s = np.sort(v[np.isfinite(v)]); n = len(s)
    return np.where(np.isfinite(v), (n - np.searchsorted(s, v, side='left')) / n, np.nan)
