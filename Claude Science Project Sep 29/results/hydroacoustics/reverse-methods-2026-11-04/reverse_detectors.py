"""reverse_detectors -- pre-registered reverse-sensing detectors for the
MH370 hydroacoustic re-analysis (methods specification of 4 Nov 2026).

Propagation is used for TRAVEL TIME ONLY. No amplitude is predicted.
Every statistic here is calibrated against an empirical null taken from
data outside the arrival windows (or from form-matched open data), never
against a transmission-loss model.

Data forms
----------
raw       IMOS loggers, 6 kHz counts, 8 Hz hardware high-pass, 307 s / 900 s.
vertices  Kadri 2024 Fig. 9 digitised plot vertices (signed Pa, 5-40 Hz,
          irregular ~14.5-15 vertices/s).  Must be converted with
          `vertices_to_envelope` before any detector is applied: signed
          vertices alternate between the top and bottom of the plotted
          trace, so they are anti-correlated by construction.
envelope  uniform-rate envelope (from raw or vertices).
picks     published arrival times (Royer, CMST, Kadri Table 1).

Detector codes are used only inside the code.  Reports use the plain
names given in the methods specification.

S1 energy excess            (envelope, raw)
S2 sample persistence       (envelope, raw)
S3 energy + persistence     (envelope, raw)
S4 Page CUSUM onset         (envelope, raw)
S5 spectral kurtosis + TKEO (raw only)
S6 excess-power tiles       (raw only)
S7 shot-population anomaly  (H08S envelope)
S8 pick-cluster scan        (picks)
B1 cross-station coincidence with time slides
C1 travel-time stacking (source scanning / non-coherent integration)
C2 nearest-neighbour discord and repeat count (matrix profile / FAST)
C3 analog-template correlation with energy gate
C4 PELT change-point onsets
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field

import numpy as np
from scipy import signal as sps
from scipy import stats

__version__ = "1.0.0"  # frozen with the methods specification, 4 Nov 2026

MAD_TO_SD = 1.4826
EARTH_R_KM = 6371.0088

# ----------------------------------------------------------------------------
# Generic helpers
# ----------------------------------------------------------------------------

def robust_loc_scale(x):
    """Median and MAD-based scale (NaN ignored).  Scale floor avoids 0."""
    x = np.asarray(x, float)
    x = x[np.isfinite(x)]
    if x.size == 0:
        return np.nan, np.nan
    m = np.median(x)
    s = MAD_TO_SD * np.median(np.abs(x - m))
    if not np.isfinite(s) or s <= 0:
        s = np.std(x) if np.std(x) > 0 else 1e-12
    return float(m), float(s)


def to_db(power, floor=1e-30):
    return 10.0 * np.log10(np.maximum(np.asarray(power, float), floor))


def window_starts(n, w, step):
    if n < w:
        return np.array([], int)
    return np.arange(0, n - w + 1, step, dtype=int)


def ring_indices(n, start, w, ring, guard):
    """Sample indices of the two-sided reference ring around [start, start+w),
    excluding a guard band on each side (CA-CFAR geometry)."""
    lo1, hi1 = max(0, start - guard - ring), max(0, start - guard)
    lo2, hi2 = min(n, start + w + guard), min(n, start + w + guard + ring)
    return np.r_[np.arange(lo1, hi1), np.arange(lo2, hi2)]


def decorrelation_lag(y, max_lag=None, thr=0.1):
    """First lag (samples) at which the sample ACF of y drops below thr
    (default 0.1).  Used to thin samples so that the binomial null of S2 is
    valid; a 1/e threshold leaves rho ~ 0.37 and doubles the false-alarm
    rate (unit test)."""
    y = np.asarray(y, float)
    y = y[np.isfinite(y)] - np.nanmean(y)
    n = y.size
    if n < 4:
        return 1
    max_lag = max_lag or n // 4
    f = np.fft.rfft(y, 2 * n)
    acf = np.fft.irfft(f * np.conj(f))[:n]
    acf = acf / acf[0]
    below = np.where(acf[1:max_lag + 1] < thr)[0]
    return int(below[0] + 1) if below.size else int(max_lag)


# ----------------------------------------------------------------------------
# Data-form conversion
# ----------------------------------------------------------------------------

def vertices_to_envelope(t, x, fs_out=10.0, t0=None, t1=None):
    """Signed plot vertices -> envelope on a uniform grid.

    Envelope value in each output bin of 1/fs_out s = max |x| of the vertices
    in the bin (the plotted trace extreme).  Empty bins are filled by linear
    interpolation and flagged.  Returns (t_grid, env, filled_mask).
    """
    t = np.asarray(t, float)
    x = np.abs(np.asarray(x, float))
    t0 = t.min() if t0 is None else t0
    t1 = t.max() if t1 is None else t1
    nb = int(np.floor((t1 - t0) * fs_out)) + 1
    idx = np.floor((t - t0) * fs_out).astype(int)
    ok = (idx >= 0) & (idx < nb)
    env = np.full(nb, np.nan)
    np.fmax.at(env, idx[ok], x[ok])
    filled = ~np.isfinite(env)
    tg = t0 + np.arange(nb) / fs_out
    if filled.any() and (~filled).sum() >= 2:
        env[filled] = np.interp(tg[filled], tg[~filled], env[~filled])
    return tg, env, filled


def bandpass_sos(fs, lo, hi, order=4):
    nyq = fs / 2.0
    hi = min(hi, 0.99 * nyq)
    return sps.butter(order, [lo / nyq, hi / nyq], btype="band", output="sos")


def raw_to_envelope(x, fs, band=(8.0, 40.0), fs_out=10.0, mode="max"):
    """Raw pressure -> band envelope at fs_out.  mode='max' emulates the plot
    extremes of a digitised trace; mode='rms' gives block RMS."""
    y = sps.sosfiltfilt(bandpass_sos(fs, *band), np.asarray(x, float))
    a = np.abs(sps.hilbert(y)) if mode == "max" else y ** 2
    blk = int(round(fs / fs_out))
    nb = a.size // blk
    a = a[: nb * blk].reshape(nb, blk)
    env = a.max(axis=1) if mode == "max" else np.sqrt(a.mean(axis=1))
    return np.arange(nb) / fs_out, env


# ----------------------------------------------------------------------------
# p-values, tails, look-elsewhere
# ----------------------------------------------------------------------------

def empirical_p(obs, null, tail="upper"):
    """(1 + #null at least as extreme) / (1 + N)  -- never zero
    (Phipson & Smyth 2010)."""
    null = np.asarray(null, float)
    null = null[np.isfinite(null)]
    obs = np.atleast_1d(np.asarray(obs, float))
    s = np.sort(null)
    if tail == "upper":
        k = s.size - np.searchsorted(s, obs, side="left")
    else:
        k = np.searchsorted(s, obs, side="right")
    p = (1.0 + k) / (1.0 + s.size)
    return p if p.size > 1 else float(p[0])


def gpd_tail_p(obs, null, q=0.90, min_exceed=30):
    """Generalised-Pareto tail p for obs beyond the empirical range
    (Knijnenburg et al. 2009).  Returns (p, flag) with flag='extrapolated'."""
    null = np.asarray(null, float)
    null = null[np.isfinite(null)]
    u = np.quantile(null, q)
    exc = null[null > u] - u
    if exc.size < min_exceed or obs <= u:
        return empirical_p(obs, null), "empirical"
    c, loc, scale = stats.genpareto.fit(exc, floc=0.0)
    p = (1 - q) * stats.genpareto.sf(obs - u, c, loc=0.0, scale=scale)
    return float(max(p, 1e-300)), "extrapolated"


def pseudo_window_global_p(local_p_series_null, n_win_true, obs_min_p, n_draws=5000, rng=None):
    """Look-elsewhere by construction: place pseudo arrival windows of the
    same number of tests (n_win_true consecutive steps) at random in the null
    series of local p values; global p = fraction whose minimum is <= the
    observed minimum."""
    rng = np.random.default_rng(rng)
    s = np.asarray(local_p_series_null, float)
    n = s.size - n_win_true + 1
    if n <= 0:
        raise ValueError("null series shorter than the arrival window")
    starts = rng.integers(0, n, n_draws)
    mins = np.array([np.nanmin(s[a:a + n_win_true]) for a in starts])
    return float((1 + np.sum(mins <= obs_min_p)) / (1 + n_draws))


def bh_fdr(p, q=0.10):
    """Benjamini-Hochberg: returns boolean discoveries and adjusted q-values."""
    p = np.asarray(p, float)
    n = p.size
    o = np.argsort(p)
    ranked = p[o] * n / (np.arange(n) + 1)
    qv = np.minimum.accumulate(ranked[::-1])[::-1]
    out = np.empty(n)
    out[o] = np.minimum(qv, 1.0)
    return out <= q, out


def fisher_combine(p1, p2):
    """Fisher statistic -2(ln p1 + ln p2).  Its null is taken empirically
    (S3), because p1 and p2 are dependent."""
    return -2.0 * (np.log(np.asarray(p1)) + np.log(np.asarray(p2)))


# ----------------------------------------------------------------------------
# S1 energy excess (CA-CFAR energy detector on window levels)
# ----------------------------------------------------------------------------

def window_levels_db(env, w, step):
    """10 log10 of mean power in each window (env is an amplitude envelope)."""
    p = np.asarray(env, float) ** 2
    st = window_starts(p.size, w, step)
    c = np.r_[0.0, np.nancumsum(p)]
    lev = (c[st + w] - c[st]) / w
    return st, to_db(lev)


def energy_excess(env, fs, win_s=10.0, step_s=None, ring_s=120.0, guard_s=10.0):
    """S1.  z = (L - median(L_ring)) / (1.4826 MAD(L_ring)) where L are window
    power levels in dB and the ring holds the non-overlapping windows inside
    +/- ring_s outside a guard.  Candidate rule (pre-registered): z >= 2."""
    w = max(1, int(round(win_s * fs)))
    step = max(1, int(round((step_s or win_s / 4) * fs)))
    st, L = window_levels_db(env, w, step)
    g = int(round(guard_s * fs))
    r = int(round(ring_s * fs))
    z = np.full(st.size, np.nan)
    ref = np.full(st.size, np.nan)
    for k, s0 in enumerate(st):
        sel = ((st + w <= s0 - g) & (st >= s0 - g - r)) | ((st >= s0 + w + g) & (st + w <= s0 + w + g + r))
        if sel.sum() < 4:
            continue
        m, sd = robust_loc_scale(L[sel])
        z[k] = (L[k] - m) / sd
        ref[k] = m
    return {"t": st / fs, "z": z, "level_db": L, "ref_db": ref}


# ----------------------------------------------------------------------------
# S2 sample persistence (binomial count, Wald-Wolfowitz runs, lag-1 corr.)
# ----------------------------------------------------------------------------

def runs_test_z(b):
    """Wald-Wolfowitz runs test on a boolean sequence.  Negative z = fewer
    runs than chance = clustering (persistence)."""
    b = np.asarray(b, bool)
    n1, n2 = int(b.sum()), int((~b).sum())
    n = n1 + n2
    if n1 == 0 or n2 == 0:
        return -np.inf if n > 1 else np.nan
    R = 1 + int(np.sum(b[1:] != b[:-1]))
    mu = 2.0 * n1 * n2 / n + 1
    var = 2.0 * n1 * n2 * (2.0 * n1 * n2 - n) / (n * n * (n - 1))
    return (R - mu) / math.sqrt(var) if var > 0 else np.nan


def persistence(env, fs, win_s=10.0, step_s=None, ring_s=120.0, guard_s=10.0, lag=None):
    """S2 (Pete's successive-sample statistic).  Work on y = 20 log10 env.
    d_i = y_i - median(y_ring).  Under noise, signs of d sum to ~0 quickly;
    a signal holds them positive.
      K     = number of positive d among n thinned samples (every `lag`-th),
      p_bin = P(Binomial(n, 0.5) >= K)  [valid because thinning removes the
              envelope correlation: lag = decorrelation_lag of the null],
      z_run = Wald-Wolfowitz z on the unthinned signs,
      r1    = lag-1 autocorrelation of d inside the window.
    Decision value T2 = -log10 p_bin, calibrated empirically."""
    y = 20.0 * np.log10(np.maximum(np.asarray(env, float), 1e-30))
    w = max(2, int(round(win_s * fs)))
    step = max(1, int(round((step_s or win_s / 4) * fs)))
    lag = lag or decorrelation_lag(y)
    g, r = int(round(guard_s * fs)), int(round(ring_s * fs))
    st = window_starts(y.size, w, step)
    out = {k: np.full(st.size, np.nan) for k in ("K", "n", "p_bin", "T2", "z_run", "r1")}
    for k, s0 in enumerate(st):
        ri = ring_indices(y.size, s0, w, r, g)
        if ri.size < 10:
            continue
        m = np.median(y[ri])
        d = y[s0:s0 + w] - m
        dt = d[::lag]
        K, n = int(np.sum(dt > 0)), dt.size
        pb = stats.binom.sf(K - 1, n, 0.5)
        out["K"][k], out["n"][k], out["p_bin"][k] = K, n, pb
        out["T2"][k] = -np.log10(max(pb, 1e-300))
        out["z_run"][k] = runs_test_z(d > 0)
        dd = d - d.mean()
        den = np.sum(dd * dd)
        out["r1"][k] = np.sum(dd[1:] * dd[:-1]) / den if den > 0 else np.nan
    out["t"] = st / fs
    out["lag"] = lag
    return out


# ----------------------------------------------------------------------------
# S4 Page CUSUM
# ----------------------------------------------------------------------------

def page_cusum(env, fs, ref_median_db, ref_scale_db, delta_sigma=1.0):
    """S4.  Standardise y = 20 log10 env by an off-window reference, then the
    one-sided Page (1954) recursion g_i = max(0, g_{i-1} + u_i - delta/2).
    Returns g and the onset index of every excursion (last zero before)."""
    y = 20.0 * np.log10(np.maximum(np.asarray(env, float), 1e-30))
    u = (y - ref_median_db) / ref_scale_db
    g = np.zeros_like(u)
    last0 = np.zeros(u.size, int)
    z0 = 0
    for i in range(u.size):
        prev = g[i - 1] if i else 0.0
        g[i] = max(0.0, prev + u[i] - delta_sigma / 2.0)
        if g[i] == 0.0:
            z0 = i
        last0[i] = z0
    return g, last0


def window_max(series, fs, win_s, step_s=None):
    w = max(1, int(round(win_s * fs)))
    step = max(1, int(round((step_s or win_s / 4) * fs)))
    st = window_starts(len(series), w, step)
    return st / fs, np.array([np.nanmax(series[s:s + w]) for s in st])


# ----------------------------------------------------------------------------
# S5 spectral kurtosis and Teager-Kaiser (raw only)
# ----------------------------------------------------------------------------

def teager_kaiser(x):
    """Discrete TKEO psi[n] = x[n]^2 - x[n-1] x[n+1] (Kaiser 1990)."""
    x = np.asarray(x, float)
    psi = np.empty_like(x)
    psi[1:-1] = x[1:-1] ** 2 - x[:-2] * x[2:]
    psi[0], psi[-1] = psi[1], psi[-2]
    return psi


def spectral_kurtosis(x, fs, nperseg=256, fmin=8.0, fmax=100.0):
    """SK(f) = <|X|^4>/<|X|^2>^2 - 2 over STFT frames (Antoni 2006).
    Gaussian noise: SK ~ 0 with s.d. ~ 2/sqrt(M).  Returns f, SK, M."""
    f, _, Z = sps.stft(np.asarray(x, float), fs=fs, nperseg=nperseg, noverlap=nperseg // 2, boundary=None)
    sel = (f >= fmin) & (f <= fmax)
    P = np.abs(Z[sel]) ** 2
    sk = np.mean(P ** 2, axis=1) / np.mean(P, axis=1) ** 2 - 2.0
    return f[sel], sk, P.shape[1]


def sk_statistic(x, fs, nperseg=256, fmin=8.0, fmax=100.0):
    """S5 decision value: max over f of SK(f) * sqrt(M)/2 (Gaussian z)."""
    f, sk, M = spectral_kurtosis(x, fs, nperseg, fmin, fmax)
    zz = sk * math.sqrt(M) / 2.0
    k = int(np.argmax(zz))
    return float(zz[k]), float(f[k])


# ----------------------------------------------------------------------------
# S6 excess-power tiles (raw only)
# ----------------------------------------------------------------------------

def excess_power(x, fs, noise_psd_f, noise_psd, fmin=8.0, fmax=100.0,
                 durations=(0.5, 1.0, 2.0, 4.0, 8.0), bandwidths=(2.0, 4.0, 8.0, 16.0, 32.0), nperseg=None):
    """S6 (Anderson et al. 2001).  Whiten the STFT power by an off-window
    noise PSD; sum whitened power over time-frequency tiles; each tile sum is
    nominally Gamma(N_bins, 1).  Returns max over tiles of -log10 p_nominal and
    the tile (t, f, dt, df).  Decision p is empirical."""
    nperseg = nperseg or int(fs * 0.25)
    f, t, Z = sps.stft(np.asarray(x, float), fs=fs, nperseg=nperseg, noverlap=nperseg // 2, boundary=None)
    sel = (f >= fmin) & (f <= fmax)
    f, P = f[sel], np.abs(Z[sel]) ** 2
    ref = np.interp(f, noise_psd_f, noise_psd)
    W = P / ref[:, None]
    W = W / np.median(W) * math.log(2.0)  # exponential(1) median = ln 2
    dtb, dfb = t[1] - t[0], f[1] - f[0]
    best = (-np.inf, None)
    C = np.cumsum(np.cumsum(np.pad(W, ((1, 0), (1, 0))), axis=0), axis=1)
    for D in durations:
        nt = max(1, int(round(D / dtb)))
        for B in bandwidths:
            nf = max(1, int(round(B / dfb)))
            if nt > W.shape[1] or nf > W.shape[0]:
                continue
            S = C[nf:, nt:] - C[:-nf, nt:] - C[nf:, :-nt] + C[:-nf, :-nt]
            N = nt * nf
            lp = -stats.gamma.logsf(S, N) / math.log(10.0)
            i, j = np.unravel_index(np.argmax(lp), lp.shape)
            if lp[i, j] > best[0]:
                best = (float(lp[i, j]), (float(t[j]), float(f[i]), D, B))
    return best


# ----------------------------------------------------------------------------
# S7 shot-population anomaly test (Diego Garcia South airgun bursts)
# ----------------------------------------------------------------------------

@dataclass
class Shots:
    onsets: np.ndarray
    ends: np.ndarray
    interval_s_median: float
    interval_s_acf: float
    duration_s_median: float
    floor_db: np.ndarray = field(repr=False)


def running_quantile(y, n, q=0.10):
    """Running q-quantile over a centred window of n samples (floor estimate)."""
    y = np.asarray(y, float)
    h = n // 2
    out = np.empty_like(y)
    for i in range(y.size):
        out[i] = np.nanquantile(y[max(0, i - h):i + h + 1], q)
    return out


def segment_shots(env, fs, floor_win_s=30.0, thr_db=6.0, merge_s=0.3, min_dur_s=0.2):
    """Measure bursts from the record (nothing assumed):
    floor = running 10th percentile of y over floor_win_s; a burst is a run of
    samples with y - floor > max(thr_db, 3 robust sd of y - floor); runs closer
    than merge_s are merged.  Interval = median onset difference, checked by
    the first ACF peak of y between 2 and 60 s."""
    y = 20.0 * np.log10(np.maximum(np.asarray(env, float), 1e-30))
    fl = running_quantile(y, int(floor_win_s * fs), 0.10)
    e = y - fl
    _, sd = robust_loc_scale(e)
    thr = max(thr_db, 3.0 * sd)
    m = e > thr
    d = np.diff(np.r_[0, m.astype(int), 0])
    on, off = np.where(d == 1)[0], np.where(d == -1)[0]
    gap = int(round(merge_s * fs))
    keep_on, keep_off = [], []
    for a, b in zip(on, off):
        if keep_on and a - keep_off[-1] <= gap:
            keep_off[-1] = b
        else:
            keep_on.append(a)
            keep_off.append(b)
    on, off = np.array(keep_on, int), np.array(keep_off, int)
    ok = (off - on) >= int(round(min_dur_s * fs))
    on, off = on[ok], off[ok]
    iv = float(np.median(np.diff(on)) / fs) if on.size > 2 else np.nan
    yy = y - np.mean(y)
    acf = np.correlate(yy, yy, "full")[yy.size - 1:]
    lo, hi = int(2 * fs), min(int(60 * fs), acf.size - 1)
    pk = sps.find_peaks(acf[lo:hi])[0]
    iv_acf = float((pk[np.argmax(acf[lo:hi][pk])] + lo) / fs) if pk.size else np.nan
    return Shots(on, off, iv, iv_acf, float(np.median(off - on) / fs) if on.size else np.nan, fl)


def shot_cycles(shots: Shots, n_samples, fs, pre_s=0.5, max_dev_frac=0.2):
    """Fit a periodic comb to the measured onsets and partition the record into
    whole shot cycles [phase + kP - pre, phase + (k+1)P - pre).  Every sample
    then belongs to exactly one cycle, so a second signal anywhere (in the
    burst or in the gap) lands in some cycle.  Bursts off the comb by more than
    max_dev_frac * P are returned separately as off-comb bursts."""
    P = shots.interval_s_median * fs
    on = shots.onsets.astype(float)
    k = np.round((on - on[0]) / P)
    good = np.abs(on - on[0] - k * P) <= max_dev_frac * P
    # least-squares comb on the on-comb onsets
    A = np.c_[np.ones(good.sum()), k[good]]
    ph, P = np.linalg.lstsq(A, on[good], rcond=None)[0]
    pre = int(round(pre_s * fs))
    kmin = int(np.ceil((pre - ph) / P))
    kmax = int(np.floor((n_samples - ph + pre) / P)) - 1
    # only cycles between the first and last measured on-comb onset
    kmin = max(kmin, int(round((on[good].min() - ph) / P)))
    kmax = min(kmax, int(round((on[good].max() - ph) / P)))
    starts = np.array([int(round(ph + j * P)) - pre for j in range(kmin, kmax + 1)])
    starts = starts[(starts >= 0) & (starts + int(round(P)) <= n_samples)]
    resid = on - (ph + np.round((on - ph) / P) * P)
    off = shots.onsets[np.abs(resid) > max_dev_frac * P]
    return starts, float(P / fs), off


def cycle_matrix(env, fs, shots: Shots, pre_s=0.5, length_s=None):
    """Aligned cycle matrix in dB above the floor (the floor reference removes
    level steps such as the +8.8 dB Kadri panel-e join)."""
    y = 20.0 * np.log10(np.maximum(np.asarray(env, float), 1e-30))
    e = y - shots.floor_db
    starts, P_s, off = shot_cycles(shots, e.size, fs, pre_s)
    L = int(round((length_s or P_s) * fs))
    starts = starts[starts + L <= e.size]
    M = np.array([e[a0:a0 + L] for a0 in starts])
    return M, starts / fs, P_s, off / fs


def features_from_matrix(M, fs, thr_db=6.0, lag=None, half=5):
    """Per-cycle features.  Template of cycle i = median of the cycles within
    +/- half cycles, excluding i (leave-one-out, local: follows slow path
    change as the survey ship moves)."""
    n = M.shape[0]
    names = ("energy_db", "peak_db", "rise_s", "decay_db_s", "duration_s",
             "persist_T2", "resid_rms_db", "ncc", "subspace_resid")
    feats = {k: np.full(n, np.nan) for k in names}

    def tmpl_of(i):
        j = [k for k in range(max(0, i - half), min(n, i + half + 1)) if k != i]
        return np.median(M[j], axis=0)

    if lag is None:
        lag = max(1, int(np.median([decorrelation_lag(M[i] - tmpl_of(i)) for i in range(n)])))
    U, S, Vt = np.linalg.svd(M - M.mean(0), full_matrices=False)
    r = int(np.searchsorted(np.cumsum(S ** 2) / np.sum(S ** 2), 0.90) + 1)
    for i in range(n):
        x = M[i]
        tmpl = tmpl_of(i)
        res = x - tmpl  # levels are floor-referenced: no free offset
        p = 10 ** (x / 10.0)
        feats["energy_db"][i] = to_db(np.sum(np.maximum(p - 1.0, 0)) / fs + 1e-12)
        feats["peak_db"][i] = x.max()
        pk = int(np.argmax(x))
        a10 = np.where(p[:pk + 1] >= 0.1 * p[pk])[0]
        a90 = np.where(p[:pk + 1] >= 0.9 * p[pk])[0]
        feats["rise_s"][i] = (a90[0] - a10[0]) / fs if a10.size and a90.size else np.nan
        above = np.where(x > thr_db)[0]
        end = above[-1] if above.size else pk
        tail = np.arange(pk, min(x.size, max(end, pk + 4) + 1))
        if tail.size > 3:
            feats["decay_db_s"][i] = np.polyfit(tail / fs, x[tail], 1)[0]
        feats["duration_s"][i] = (above[-1] - above[0] + 1) / fs if above.size else 0.0
        rt = res[::lag]
        K = int(np.sum(rt > 0))
        feats["persist_T2"][i] = (K - rt.size / 2.0) / math.sqrt(rt.size / 4.0)  # sign-count z
        feats["resid_rms_db"][i] = np.sqrt(np.mean(res ** 2))
        feats["ncc"][i] = np.corrcoef(x, tmpl)[0, 1]
        xc = x - M.mean(0)
        proj = Vt[:r].T @ (Vt[:r] @ xc)
        feats["subspace_resid"][i] = np.sum((xc - proj) ** 2) / max(np.sum(xc ** 2), 1e-12)
    feats["subspace_rank"] = r
    feats["persist_lag"] = lag
    return feats


def shot_features(env, fs, shots: Shots, pre_s=0.5, length_s=None, lag=None, half=5):
    """S7 features for every shot cycle of a record.  Returns (feats, M)."""
    M, cstart, P_s, off = cycle_matrix(env, fs, shots, pre_s, length_s)
    _, sd = robust_loc_scale(M)
    feats = features_from_matrix(M, fs, max(6.0, 3.0 * sd), lag, half)
    feats["cycle_start_s"] = cstart
    feats["period_s_fit"] = P_s
    feats["off_comb_bursts_s"] = off
    feats["thr_db"] = max(6.0, 3.0 * sd)
    return feats, M


S7_FEATURES = ("energy_db", "rise_s", "decay_db_s", "duration_s", "persist_T2", "resid_rms_db", "ncc", "subspace_resid")
_S7_FLOORS = {"rise_s": 0.1, "duration_s": 0.1, "decay_db_s": 0.1, "energy_db": 0.1,
              "resid_rms_db": 0.05, "ncc": 1e-3, "subspace_resid": 1e-3, "persist_T2": 0.5}


def shot_Q(feats, names=S7_FEATURES, fs=10.0):
    """Leave-one-out robust z per feature and Q = sum z^2 per cycle.
    Scale floors: time features 1/fs (sample quantisation)."""
    fl = dict(_S7_FLOORS, rise_s=1.0 / fs, duration_s=1.0 / fs)
    Z = []
    for nm in names:
        v = np.asarray(feats[nm], float)
        z = np.full(v.size, np.nan)
        for i in range(v.size):
            m, sc = robust_loc_scale(np.delete(v, i))
            z[i] = (v[i] - m) / max(sc, fl.get(nm, 1e-3))
        Z.append(z)
    Z = np.array(Z)
    return np.nansum(Z ** 2, axis=0), dict(zip(names, Z))


def simulate_population(M, fs, thr_db, rng, half=5, quiet_frac=0.3):
    """One null pseudo-population with the measured structure of the record:
    running template (signal power above the noise), measured amplitude
    jitter (robust s.d. of cycle energy), measured onset jitter (ignored at
    envelope resolution if below one sample) and REAL noise taken from the
    quiet end (last quiet_frac) of randomly chosen cycles, in random order.
    No second signal is present by construction, except whatever the real
    quiet blocks hold (this makes the null conservative)."""
    n, L = M.shape
    P = 10 ** (M / 10.0)
    q0 = int(L * (1 - quiet_frac))
    quiet = P[:, q0:]
    noise_med = np.median(quiet)
    tm = np.array([np.median(P[[k for k in range(max(0, i - half), min(n, i + half + 1)) if k != i]], axis=0) for i in range(n)])
    S = np.maximum(tm - noise_med, 0.0)
    e_db = to_db(np.sum(np.maximum(P - noise_med, 0), axis=1))
    _, a_sd = robust_loc_scale(e_db)
    out = np.empty_like(P)
    nq = quiet.shape[1]
    for i in range(n):
        blocks = []
        while sum(b.size for b in blocks) < L:
            blocks.append(quiet[rng.integers(n)][rng.integers(0, max(1, nq // 2)):])
        N_ = np.concatenate(blocks)[:L]
        out[i] = S[i] * 10 ** (rng.normal(0, a_sd) / 10.0) + N_
    return to_db(out)


def shot_population_test(feats, M, fs, n_mc=200, rng=None, names=S7_FEATURES, half=5):
    """S7 decision.  Local p = exact rank among cycles (minimum 1/N).
    Global p = P(max Q over a null pseudo-population >= Q_i), from n_mc
    pseudo-populations built by simulate_population (look-elsewhere over all
    cycles is inside the max)."""
    rng = np.random.default_rng(rng)
    Q, Z = shot_Q(feats, names, fs)
    N = Q.size
    p_rank = np.array([(1 + np.sum(np.delete(Q, i) >= Q[i])) / N for i in range(N)])
    lag = feats.get("persist_lag")
    thr = feats.get("thr_db", 6.0)
    mx = np.empty(n_mc)
    for k in range(n_mc):
        Ms = simulate_population(M, fs, thr, rng, half)
        fs_ = features_from_matrix(Ms, fs, thr, lag, half)
        mx[k] = np.max(shot_Q(fs_, names, fs)[0])
    p_glob = np.array([(1 + np.sum(mx >= q)) / (1 + n_mc) for q in Q])
    return {"Q": Q, "z": Z, "p_rank": p_rank, "p_global": p_glob, "null_maxQ": mx}


# kept for backwards use in notebooks: parametric version (NOT the decision rule;
# unit tests show it is anti-conservative for heavy-tailed shot features)
def shot_outlier_scores(feats, names=S7_FEATURES, fs=10.0):
    Q, Z = shot_Q(feats, names, fs)
    N = Q.size
    p_rank = np.array([(1 + np.sum(np.delete(Q, i) >= Q[i])) / N for i in range(N)])
    return {"z": Z, "Q": Q, "p_rank": p_rank}


# ----------------------------------------------------------------------------
# S8 pick-cluster scan (point picks)
# ----------------------------------------------------------------------------

def scan_count(times, t0, t1, width):
    """Maximum number of points inside any interval of length `width`
    that lies within [t0, t1]."""
    t = np.sort(np.asarray(times, float))
    t = t[(t >= t0) & (t <= t1)]
    if t.size == 0:
        return 0
    j = np.searchsorted(t, t + width, side="right")
    return int(np.max(j - np.arange(t.size)))


def scan_p_poisson(k_obs, rate, T, width, n_mc=20000, rng=None):
    """Monte Carlo p of the scan statistic under a homogeneous Poisson
    process of off-window rate (Naus 1965)."""
    rng = np.random.default_rng(rng)
    ks = np.empty(n_mc, int)
    for i in range(n_mc):
        n = rng.poisson(rate * T)
        ks[i] = scan_count(rng.uniform(0, T, n), 0, T, width)
    return float((1 + np.sum(ks >= k_obs)) / (1 + n_mc))


# ----------------------------------------------------------------------------
# Geometry: 7th-arc hypothesis grid and travel-time intervals
# ----------------------------------------------------------------------------

ARC_CENTRE = (0.570, 64.252)   # deg (lat, lon) -- hydro_data README
ARC_RADIUS_DEG = 44.501


def _xyz(lat, lon):
    la, lo = np.radians(lat), np.radians(lon)
    return np.array([np.cos(la) * np.cos(lo), np.cos(la) * np.sin(lo), np.sin(la)])


def _latlon(v):
    v = v / np.linalg.norm(v)
    return float(np.degrees(np.arcsin(v[2]))), float(np.degrees(np.arctan2(v[1], v[0])))


def arc_point(lat, offset_nm=0.0, centre=ARC_CENTRE, radius_deg=ARC_RADIUS_DEG, east=True):
    """Point on the 7th arc (spherical small circle) at latitude `lat`, moved
    `offset_nm` radially (positive = away from the centre = outside the arc)."""
    c = _xyz(*centre)
    best = None
    for lon in np.linspace(centre[1], centre[1] + (90 if east else -90), 9001):
        dd = np.degrees(np.arccos(np.clip(c @ _xyz(lat, lon), -1, 1))) - radius_deg
        if best is None or abs(dd) < abs(best[1]):
            best = (lon, dd)
    lo = best[0]
    for _ in range(50):  # Newton refine in longitude
        h = 1e-6
        f0 = np.degrees(np.arccos(np.clip(c @ _xyz(lat, lo), -1, 1))) - radius_deg
        f1 = np.degrees(np.arccos(np.clip(c @ _xyz(lat, lo + h), -1, 1))) - radius_deg
        if f1 == f0:
            break
        lo -= f0 * h / (f1 - f0)
    p = _xyz(lat, lo)
    if offset_nm:
        ang = offset_nm * 1.852 / EARTH_R_KM  # radians
        axis = np.cross(c, p)
        axis /= np.linalg.norm(axis)
        p = p * np.cos(ang) + np.cross(axis, p) * np.sin(ang) + axis * (axis @ p) * (1 - np.cos(ang))
    return _latlon(p)


def geodesic_km(lat1, lon1, lat2, lon2):
    """WGS84 geodesic (pyproj) with spherical fallback."""
    try:
        from pyproj import Geod
        _, _, d = Geod(ellps="WGS84").inv(lon1, lat1, lon2, lat2)
        return np.asarray(d) / 1000.0
    except Exception:
        p1, p2 = np.radians([lat1, lon1]), np.radians([lat2, lon2])
        a = np.sin((p2[0] - p1[0]) / 2) ** 2 + np.cos(p1[0]) * np.cos(p2[0]) * np.sin((p2[1] - p1[1]) / 2) ** 2
        return 2 * EARTH_R_KM * np.arcsin(np.sqrt(a))


def arrival_interval(t0_lo, t0_hi, dist_km, v_lo_kms, v_hi_kms, extra_s=0.0):
    """Earliest and latest arrival for a source-time interval and speed range."""
    return t0_lo + dist_km / v_hi_kms, t0_hi + dist_km / v_lo_kms + extra_s


# ----------------------------------------------------------------------------
# B1 cross-station coincidence with time slides;  C1 travel-time stacking
# ----------------------------------------------------------------------------

def coincidences(trig_a, trig_b, lag_lo, lag_hi):
    """Pairs (i, j) with lag_lo <= t_b - t_a <= lag_hi.  Triggers are dicts
    {'t': array, 'z': array}.  Statistic of a pair = z_a + z_b."""
    ta, tb = np.asarray(trig_a["t"]), np.asarray(trig_b["t"])
    out = []
    for i, t in enumerate(ta):
        j = np.where((tb - t >= lag_lo) & (tb - t <= lag_hi))[0]
        for jj in j:
            out.append((i, int(jj), float(trig_a["z"][i] + trig_b["z"][jj])))
    return out


def grid_coincidence_max(trig, cells, shift=None):
    """Max over hypothesis cells of the summed trigger z of the best trigger
    per station inside that station's arrival interval.  `cells` is a list of
    dicts {station: (t_lo, t_hi)}.  At least two stations must contribute.
    `shift` maps station -> seconds added to its trigger times (time slide).
    Returns (best_score, best_cell_index, n_stations)."""
    best = (-np.inf, -1, 0)
    for ci, cell in enumerate(cells):
        tot, ns = 0.0, 0
        for st, (lo, hi) in cell.items():
            if st not in trig:
                continue
            t = np.asarray(trig[st]["t"]) + (shift or {}).get(st, 0.0)
            m = (t >= lo) & (t <= hi)
            if m.any():
                tot += float(np.max(np.asarray(trig[st]["z"])[m]))
                ns += 1
        if ns >= 2 and tot > best[0]:
            best = (tot, ci, ns)
    return best


def time_slide_null(trig, cells, record_span, min_shift, n_slides=1000, rng=None, circular=True):
    """Distribution of grid_coincidence_max under random time slides of every
    station except the first (shifts |s| >= min_shift, wrapped inside each
    station's record span (t_start, t_end) when circular).  The max over the
    whole grid is taken in each slide, so the global p handles look-elsewhere."""
    rng = np.random.default_rng(rng)
    sts = list(trig)
    vals = np.empty(n_slides)
    for k in range(n_slides):
        tr = {}
        for si, st in enumerate(sts):
            t = np.asarray(trig[st]["t"], float)
            if si > 0:
                a, b = record_span[st]
                L = b - a
                s = rng.uniform(min_shift, max(min_shift + 1e-9, L - min_shift)) if circular else rng.uniform(min_shift, 3 * min_shift)
                t = a + np.mod(t - a + s, L) if circular else t + s * rng.choice([-1, 1])
            tr[st] = {"t": t, "z": trig[st]["z"]}
        vals[k] = grid_coincidence_max(tr, cells)[0]
    return vals


def triggers_from_series(t, z, thr=2.0, min_sep_s=5.0):
    """Local maxima of a score series above thr, at least min_sep_s apart."""
    t, z = np.asarray(t), np.asarray(z)
    dt = np.median(np.diff(t)) if t.size > 1 else 1.0
    pk, _ = sps.find_peaks(np.nan_to_num(z, nan=-np.inf), height=thr, distance=max(1, int(min_sep_s / dt)))
    return {"t": t[pk], "z": z[pk]}


def stack_brightness(series, cells, stat="max"):
    """C1 source scanning (Kao & Shan 2004) / non-coherent integration:
    B(cell) = sum over stations of max score inside the station's arrival
    interval.  `series` maps station -> (t, z).  Returns array per cell and
    the number of contributing stations."""
    B = np.zeros(len(cells))
    N = np.zeros(len(cells), int)
    for ci, cell in enumerate(cells):
        for st, (lo, hi) in cell.items():
            if st not in series:
                continue
            t, z = series[st]
            m = (t >= lo) & (t <= hi) & np.isfinite(z)
            if m.any():
                B[ci] += np.max(z[m])
                N[ci] += 1
    return B, N


# ----------------------------------------------------------------------------
# C2 nearest-neighbour discord / repeat count (matrix profile, FAST idea)
# ----------------------------------------------------------------------------

def mass_distance(query, series):
    """z-normalised Euclidean distance profile of `query` against all
    subsequences of `series` (MASS, FFT based)."""
    q = np.asarray(query, float)
    x = np.asarray(series, float)
    m, n = q.size, x.size
    qz = (q - q.mean()) / (q.std() + 1e-12)
    c = np.r_[0.0, np.cumsum(x)]
    c2 = np.r_[0.0, np.cumsum(x * x)]
    mu = (c[m:] - c[:-m]) / m
    sig = np.sqrt(np.maximum((c2[m:] - c2[:-m]) / m - mu * mu, 1e-24))
    N = 1 << int(np.ceil(np.log2(n + m)))
    dot = np.fft.irfft(np.fft.rfft(x, N) * np.fft.rfft(qz[::-1], N), N)[m - 1:n]
    d2 = 2 * m * (1 - dot / (m * sig))
    return np.sqrt(np.maximum(d2, 0))


def discord_and_repeats(series, start, m, exclusion=None, repeat_radius=None):
    """C2 for the subsequence at `start`: nearest-neighbour distance (outside an
    exclusion zone of +/- m) -- large = unique transient (discord) -- and the
    number of near repeats within `repeat_radius` -- large = repeating source
    (airgun, call, ice).  Calibrated empirically on off-window queries."""
    d = mass_distance(series[start:start + m], series)
    ex = exclusion or m
    lo, hi = max(0, start - ex), min(d.size, start + ex + 1)
    d[lo:hi] = np.inf
    nn = float(np.min(d))
    rr = repeat_radius if repeat_radius is not None else 0.5 * math.sqrt(2 * m)
    return nn, int(np.sum(d <= rr))


# ----------------------------------------------------------------------------
# C3 analog-template correlation with energy gate
# ----------------------------------------------------------------------------

def template_ncc(y, template):
    """Sliding Pearson correlation of y (dB envelope) with a template."""
    m = len(template)
    return 1.0 - mass_distance(template, y) ** 2 / (2.0 * m)


# ----------------------------------------------------------------------------
# C4 PELT change points (Gaussian mean change)
# ----------------------------------------------------------------------------

def pelt_mean(y, penalty, sigma=None, min_size=2):
    """PELT (Killick et al. 2012) for changes in mean with known sigma.
    Cost of a segment = sum of squared deviations from its mean / sigma^2.
    Returns change-point indices (segment starts, excluding 0)."""
    y = np.asarray(y, float)
    n = y.size
    sigma = sigma or robust_loc_scale(np.diff(y))[1] / math.sqrt(2)
    c1 = np.r_[0.0, np.cumsum(y)]
    c2 = np.r_[0.0, np.cumsum(y * y)]

    def cost(a, b):
        s, ss, L = c1[b] - c1[a], c2[b] - c2[a], b - a
        return (ss - s * s / L) / (sigma * sigma)

    F = np.full(n + 1, np.inf)
    F[0] = -penalty
    last = np.zeros(n + 1, int)
    R = [0]
    for t in range(min_size, n + 1):
        cand = [s for s in R if t - s >= min_size]
        vals = np.array([F[s] + cost(s, t) + penalty for s in cand])
        k = int(np.argmin(vals))
        F[t], last[t] = vals[k], cand[k]
        keep = [s for s, v in zip(cand, vals) if v - penalty <= F[t]]
        young = [s for s in R if t - s < min_size]
        R = keep + young + [t - min_size + 1] if t - min_size + 1 > 0 else keep + young
        R = sorted(set(R))
    cps, t = [], n
    while t > 0:
        s = int(last[t])
        if s > 0:
            cps.append(s)
        t = s
    return sorted(cps)


# ----------------------------------------------------------------------------
# Known events and injection
# ----------------------------------------------------------------------------

def association_probability(t_cand, t_pred, sigma_t, bg_rate_per_s):
    """P(candidate is known event k | times) for a two-hypothesis timing model:
    known-event arrival ~ N(t_pred, sigma_t) against background candidates at
    the off-window rate.  Removal rule: P >= 0.95 (airguns at H08S: label only)."""
    lam_k = stats.norm.pdf(t_cand, t_pred, sigma_t)
    return float(lam_k / (lam_k + bg_rate_per_s))


def impulsive_shape(fs, rise_s=1.0, decay_s=5.0, dur_s=None):
    """Amplitude envelope: linear rise then exponential decay (power decays
    with time constant decay_s/2)."""
    dur_s = dur_s or rise_s + 5 * decay_s
    t = np.arange(int(round(dur_s * fs))) / fs
    a = np.where(t < rise_s, t / max(rise_s, 1e-9), np.exp(-(t - rise_s) / decay_s))
    return a


def inject_envelope(env, fs, t0_s, shape, snr_db, noise_ref=None, win_s=10.0):
    """Incoherent (power) addition of a scaled shape to an amplitude envelope.
    SNR definition (pre-registered): mean signal power over the first win_s
    after onset / median noise power of the reference (default: whole env)."""
    env = np.asarray(env, float).copy()
    i0 = int(round(t0_s * fs))
    sh = np.asarray(shape, float)
    n = min(sh.size, env.size - i0)
    pn = np.median((noise_ref if noise_ref is not None else env) ** 2)
    w = max(1, min(n, int(round(win_s * fs))))
    ps = np.mean(sh[:w] ** 2)
    g = math.sqrt(pn * 10 ** (snr_db / 10.0) / ps)
    env[i0:i0 + n] = np.sqrt(env[i0:i0 + n] ** 2 + (g * sh[:n]) ** 2)
    return env


def inject_raw(x, fs, t0_s, shape_env, snr_db, band=(8.0, 40.0), rng=None, win_s=10.0):
    """Add band-limited Gaussian noise modulated by shape_env (a stochastic
    transient), scaled to SNR = signal power / noise power in band over the
    first win_s after onset."""
    rng = np.random.default_rng(rng)
    x = np.asarray(x, float).copy()
    sos = bandpass_sos(fs, *band)
    nb = sps.sosfiltfilt(sos, x)
    pn = np.mean(nb ** 2)
    i0 = int(round(t0_s * fs))
    env = np.interp(np.arange(int(len(shape_env) * fs / 10.0)) / fs, np.arange(len(shape_env)) / 10.0, shape_env)
    s = sps.sosfiltfilt(sos, rng.standard_normal(env.size)) * env
    n = min(s.size, x.size - i0)
    w = max(1, min(n, int(win_s * fs)))
    g = math.sqrt(pn * 10 ** (snr_db / 10.0) / np.mean(s[:w] ** 2))
    x[i0:i0 + n] += g * s[:n]
    return x
