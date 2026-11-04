"""Screening core for the reverse-sensing run of 4 Nov 2026.
Every statistic calls, or mirrors line for line, reverse_detectors.py v1.0.0
(frozen with the methods specification).  Mirrored 'local' versions evaluate
only the windows that overlap an injection; test_core() checks that they equal
the module output exactly."""
import math, numpy as np
from scipy import signal as sps, stats
import reverse_detectors as rd

FS_ENV = 10.0
S1_L = (2.0, 5.0, 10.0, 30.0)
S2_L = (10.0, 30.0)
S4_L = (10.0, 30.0)
RAW_BANDS = {'8-20 Hz': (8.0, 20.0), '20-40 Hz': (20.0, 40.0), '40-100 Hz': (40.0, 100.0), '8-40 Hz': (8.0, 40.0)}
FS_RAW = 500.0

def ring_geom(L):
    """S1 ring (spec 5): max(120 s, 6L) each side, guard max(10 s, L).
    The same geometry is used for the S2 median reference."""
    return max(120.0, 6.0 * L), max(10.0, L)

def y_db(env):
    return 20.0 * np.log10(np.maximum(np.asarray(env, float), 1e-30))

# ---------------------------------------------------------------- S1, S2, S4 full segment
def s1(env, fs, L):
    ring, guard = ring_geom(L)
    return rd.energy_excess(env, fs, win_s=L, step_s=L / 4, ring_s=ring, guard_s=guard)

def s2(env, fs, L, lag):
    ring, guard = ring_geom(L)
    return rd.persistence(env, fs, win_s=L, step_s=L / 4, ring_s=ring, guard_s=guard, lag=lag)

def s4_window(y, fs, s0, w, ref_s=300.0, min_ref_s=60.0):
    """Page CUSUM inside one window, causal reference of the 300 s before the
    window in the same segment.  If fewer than 60 s precede the window (segment
    start), the reference is the 300 s after the window (flag 'forward')."""
    a = max(0, s0 - int(ref_s * fs))
    flag = 'causal'
    ref = y[a:s0]
    if ref.size < int(min_ref_s * fs):
        ref = y[s0 + w:s0 + w + int(ref_s * fs)]
        flag = 'forward'
        if ref.size < int(min_ref_s * fs):
            ref = np.r_[y[a:s0], y[s0 + w:]]
            flag = 'segment'
    m, sd = rd.robust_loc_scale(ref)
    g, last0 = rd.page_cusum(10 ** (y[s0:s0 + w] / 20.0), fs, m, sd, 1.0)
    k = int(np.argmax(g))
    return float(g[k]), s0 + int(last0[k]), flag

def s4(env, fs, L):
    y = y_db(env)
    w = max(1, int(round(L * fs))); step = max(1, int(round(L / 4 * fs)))
    st = rd.window_starts(y.size, w, step)
    G = np.full(st.size, np.nan); on = np.full(st.size, np.nan); fl = np.empty(st.size, object)
    for k, s0 in enumerate(st):
        G[k], o, fl[k] = s4_window(y, fs, s0, w)
        on[k] = o / fs
    return {'t': st / fs, 'G': G, 'onset': on, 'flag': fl}

def envelope_stats(env, fs, lag, flagged=None):
    """All envelope detectors on one segment.  Windows with >20 % flagged
    (interpolated) bins are set to NaN (spec 2.1)."""
    out = {}
    def bad(t, L):
        if flagged is None: return np.zeros(len(t), bool)
        w = int(round(L * fs)); st = np.round(np.asarray(t) * fs).astype(int)
        c = np.r_[0, np.cumsum(flagged.astype(float))]
        return (c[st + w] - c[st]) / w > 0.20
    for L in S1_L:
        r = s1(env, fs, L); b = bad(r['t'], L); r['z'][b] = np.nan
        out[('S1', L)] = {'t': r['t'], 'stat': r['z'], 'level_db': r['level_db']}
    for L in S2_L:
        r = s2(env, fs, L, lag); b = bad(r['t'], L)
        for k in ('T2', 'z_run', 'r1'): r[k][b] = np.nan
        out[('S2', L)] = {'t': r['t'], 'stat': r['T2'], 'z_run': r['z_run'], 'r1': r['r1']}
    for L in S4_L:
        r = s4(env, fs, L); b = bad(r['t'], L); r['G'][b] = np.nan
        out[('S4', L)] = {'t': r['t'], 'stat': r['G'], 'onset': r['onset']}
    return out

# ---------------------------------------------------------------- local (injection) versions
def s1_local(env, fs, L, targets):
    """S1 z at window indices `targets` (identical formula to rd.energy_excess)."""
    w = max(1, int(round(L * fs))); step = max(1, int(round(L / 4 * fs)))
    ring, guard = ring_geom(L)
    st, Lv = rd.window_levels_db(env, w, step)
    g = int(round(guard * fs)); r = int(round(ring * fs))
    z = np.full(len(targets), np.nan)
    for i, k in enumerate(targets):
        s0 = st[k]
        sel = ((st + w <= s0 - g) & (st >= s0 - g - r)) | ((st >= s0 + w + g) & (st + w <= s0 + w + g + r))
        if sel.sum() < 4: continue
        m, sd = rd.robust_loc_scale(Lv[sel]); z[i] = (Lv[k] - m) / sd
    return z

def s2_local(env, fs, L, lag, targets):
    y = y_db(env)
    w = max(2, int(round(L * fs))); step = max(1, int(round(L / 4 * fs)))
    ring, guard = ring_geom(L)
    g, r = int(round(guard * fs)), int(round(ring * fs))
    st = rd.window_starts(y.size, w, step)
    T2 = np.full(len(targets), np.nan)
    for i, k in enumerate(targets):
        s0 = st[k]; ri = rd.ring_indices(y.size, s0, w, r, g)
        if ri.size < 10: continue
        d = y[s0:s0 + w] - np.median(y[ri]); dt = d[::lag]
        pb = stats.binom.sf(int(np.sum(dt > 0)) - 1, dt.size, 0.5)
        T2[i] = -np.log10(max(pb, 1e-300))
    return T2

def s4_local(env, fs, L, targets):
    y = y_db(env)
    w = max(1, int(round(L * fs))); step = max(1, int(round(L / 4 * fs)))
    st = rd.window_starts(y.size, w, step)
    return np.array([s4_window(y, fs, st[k], w)[0] for k in targets])

def target_windows(n, fs, L, t_on, span_s=10.0):
    """Indices of the windows of length L (step L/4) that overlap [t_on, t_on+span_s]."""
    w = max(1, int(round(L * fs))); step = max(1, int(round(L / 4 * fs)))
    st = rd.window_starts(n, w, step) / fs
    return np.where((st <= t_on + span_s) & (st + L >= t_on))[0]

# ---------------------------------------------------------------- raw detectors
def bandpass(x, fs, band):
    return sps.sosfiltfilt(rd.bandpass_sos(fs, *band), np.asarray(x, float))

def raw_envelopes(x, fs=FS_RAW):
    return {b: rd.raw_to_envelope(x, fs, band=bd, fs_out=FS_ENV, mode='max')[1] for b, bd in RAW_BANDS.items()}

def s5(x, fs=FS_RAW, L=10.0, step=2.5, starts=None):
    """S5 spectral kurtosis z (500 Hz, 128-point frames, 8-100 Hz) per window,
    plus the Teager-Kaiser ratio label (window mean / ring median)."""
    w = int(round(L * fs)); stp = int(round(step * fs))
    st = rd.window_starts(len(x), w, stp) if starts is None else np.asarray(starts, int)
    z = np.full(st.size, np.nan); fpk = np.full(st.size, np.nan)
    for k, s0 in enumerate(st):
        z[k], fpk[k] = rd.sk_statistic(x[s0:s0 + w], fs, nperseg=128, fmin=8.0, fmax=100.0)
    return {'t': st / fs, 'stat': z, 'f_peak': fpk}

def tk_ratio(x, fs, t, L=10.0):
    xb = bandpass(x, fs, (8.0, 100.0)); psi = rd.teager_kaiser(xb)
    w = int(round(L * fs)); c = np.r_[0, np.cumsum(psi)]
    st = np.round(np.asarray(t) * fs).astype(int)
    m = (c[st + w] - c[st]) / w
    out = np.full(st.size, np.nan)
    ring, guard = int(120 * fs), int(10 * fs)
    for k, s0 in enumerate(st):
        sel = ((st + w <= s0 - guard) & (st >= s0 - guard - ring)) | ((st >= s0 + w + guard) & (st + w <= s0 + w + guard + ring))
        if sel.sum() >= 4: out[k] = m[k] / np.median(m[sel])
    return out

from scipy.special import gammaln
def gamma_neglog10_sf(S, N):
    """-log10 P(Gamma(N,1) >= S).  scipy's logsf underflows to -inf far in the
    tail; there the asymptotic series of the upper incomplete gamma function
    log Q = -S + (N-1) ln S - lnGamma(N) + ln(1 + (N-1)/S + (N-1)(N-2)/S^2) is used."""
    S = np.asarray(S, float)
    ls = stats.gamma.logsf(S, N)
    bad = ~np.isfinite(ls)
    if bad.any():
        Sb = np.maximum(S[bad], 1e-9)
        ls[bad] = -Sb + (N - 1) * np.log(Sb) - gammaln(N) + np.log1p((N - 1) / Sb + (N - 1) * (N - 2) / Sb ** 2)
    return -ls / math.log(10.0)

S6_D = (0.5, 1.0, 2.0, 4.0, 8.0); S6_B = (2.0, 4.0, 8.0, 16.0, 32.0)

def s6_tiles(x, fs=FS_RAW, noise=None):
    """Whitened STFT power (rd.excess_power formula) on the whole record; the
    noise spectrum is the median over the record's frames unless given.
    Returns per-tile-start time series of max -log10 p over (D, B), with the tile."""
    nperseg = int(fs * 0.25)
    f, t, Z = sps.stft(np.asarray(x, float), fs=fs, nperseg=nperseg, noverlap=nperseg // 2, boundary=None)
    sel = (f >= 8.0) & (f <= 100.0); f, P = f[sel], np.abs(Z[sel]) ** 2
    ref = np.median(P, axis=1) if noise is None else noise
    W = P / ref[:, None]; W = W / np.median(W) * math.log(2.0)
    dtb, dfb = t[1] - t[0], f[1] - f[0]
    C = np.cumsum(np.cumsum(np.pad(W, ((1, 0), (1, 0))), axis=0), axis=1)
    best = np.full(W.shape[1], -np.inf); tile = [None] * W.shape[1]
    bestD = np.full(W.shape[1], np.nan); bestF = np.full(W.shape[1], np.nan)
    for D in S6_D:
        nt = max(1, int(round(D / dtb)))
        for B in S6_B:
            nf = max(1, int(round(B / dfb)))
            if nt > W.shape[1] or nf > W.shape[0]: continue
            S = C[nf:, nt:] - C[:-nf, nt:] - C[nf:, :-nt] + C[:-nf, :-nt]
            lp = gamma_neglog10_sf(S, nf * nt)
            i = np.argmax(lp, axis=0); v = lp[i, np.arange(lp.shape[1])]
            # tile j starts at frame j and ends at frame j+nt-1
            upd = v > best[:v.size]
            best[:v.size][upd] = v[upd]; bestD[:v.size][upd] = D; bestF[:v.size][upd] = f[i][upd]
    return t, best, bestD, bestF, ref

def s6(x, fs=FS_RAW, L=10.0, step=2.5, noise=None):
    t, best, bD, bF, ref = s6_tiles(x, fs, noise)
    tstart = t - 0.125  # frame centre -> frame start (nperseg/2/fs)
    n = len(x); w = L; st = rd.window_starts(n, int(L * fs), int(step * fs)) / fs
    out = np.full(st.size, np.nan); tt = np.full(st.size, np.nan); ff = np.full(st.size, np.nan)
    for k, s0 in enumerate(st):
        m = (tstart >= s0) & (tstart + np.nan_to_num(bD, nan=99) <= s0 + w)
        if m.any():
            j = np.where(m)[0][np.argmax(best[m])]
            out[k], tt[k], ff[k] = best[j], tstart[j], bF[j]
    return {'t': st, 'stat': out, 'tile_t': tt, 'tile_f': ff, 'noise_psd': ref}

def test_core(seed=0):
    rng = np.random.default_rng(seed)
    env = np.exp(rng.normal(0, 0.5, 3000)); env[1500:1550] *= 4
    for L in S1_L:
        full = s1(env, 10.0, L)['z']; tg = target_windows(env.size, 10.0, L, 150.0)
        assert np.allclose(full[tg], s1_local(env, 10.0, L, tg), equal_nan=True)
    for L in S2_L:
        full = s2(env, 10.0, L, 3)['T2']; tg = target_windows(env.size, 10.0, L, 150.0)
        assert np.allclose(full[tg], s2_local(env, 10.0, L, 3, tg), equal_nan=True)
    for L in S4_L:
        full = s4(env, 10.0, L)['G']; tg = target_windows(env.size, 10.0, L, 150.0)
        assert np.allclose(full[tg], s4_local(env, 10.0, L, tg), equal_nan=True)
    return True
