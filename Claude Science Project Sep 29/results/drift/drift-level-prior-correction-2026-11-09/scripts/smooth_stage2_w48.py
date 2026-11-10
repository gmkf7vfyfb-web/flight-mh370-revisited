"""Stage 2: Gaussian-process smoothing of the drift log-likelihood along the arc, with uncertainty from a joint bootstrap over ocean samples.
Input: res-smooth-w48/lm-<config>-s<seed>.npz (stage 1). Level draws of all seeds are pooled (lm = ln mean_seeds exp(lm_seed)).
Point estimate y_i (84 release points) = ln of the two-model average likelihood (or one model). Noise variance v_i = bootstrap variance of y_i.
GP: constant mean (profiled), Matern 3/2 kernel, amplitude and length scale fitted by restricted marginal likelihood, plus a nugget tau^2 for point-to-point
differences between the on-arc and +/-50 NM release points. The same smoother is applied to every bootstrap replicate (hyperparameters fixed).
Bootstrap: ocean samples 1-16 exist at every point and are shared by all points, 17-32 and 33-48 only south of 33.25 S; the three blocks are resampled separately,
the same indices at every point and in both ocean models (the ocean-error realisation is common to all points, so errors are correlated between points).
Prior along the arc: ledger bins (uniform per arc length). Core: final end of flight, Davey model + fuel, D0, on the same bins. Tension as in the evidence ledger;
p and sigma undefined (NaN) where the effective dimension d <= 0."""
import glob, os, sys, json, numpy as np, pandas as pd
from scipy import stats
from scipy.optimize import minimize
rng = np.random.default_rng(12345); B = 400; SUF = os.environ.get('SUF', ''); FIXELL = float(os.environ['FIXELL']) if os.environ.get('FIXELL') else None
# Uniform 0.1-degree latitude bins over the ledger arc span (40.25-19.9 S). Prior: uniform per unit arc length; its density per degree of latitude is the derivative of a cubic fit of
# the ledger's own equal-mass (10 NM) bin count against bin latitude (the ledger bin latitudes are noisy where the core has few samples, a smooth fit removes that).
Zl = np.load('arcm.npz'); l0 = Zl['D0|lat']; ok0 = np.isfinite(l0); l0 = l0[ok0]; pi0 = np.nan_to_num(Zl['D0|(uniform along the arc)'])[ok0]; ls_ = np.sort(l0[pi0 > 0])
cf = np.polyfit(ls_, np.arange(len(ls_)) + 0.5, 3); edges_l = np.arange(-40.25, -19.85, 0.1); la = 0.5 * (edges_l[1:] + edges_l[:-1]); pi = np.polyval(np.polyder(cf), la); assert (pi > 0).all(); pi = pi / pi.sum()
Zc = np.load('/Users/pete/Downloads/mh370-exchange/end-of-flight/final-2026-11-07/results/eof-final-handoff-df.npz'); lw = Zc['log_weight_D0'].astype(float)
hw = np.exp(lw - np.nanmax(lw)); hw = np.where(np.isfinite(hw), hw, 0); cl = Zc['latitude_deg'].astype(float)
pc, _ = np.histogram(cl, edges_l, weights=hw); pc = pc / pc.sum(); o = np.arange(len(la))
def tension(LB):
    LA = np.where(pi > 0, pc / np.maximum(pi, 1e-300), 0)
    post = lambda L: (lambda p: p / p.sum())(pi * L); pA, pB, pAB = post(LA), post(LB), post(LA * LB)
    KL = lambda p: float(np.sum(np.where(p > 0, p * np.log(np.maximum(p, 1e-300) / np.maximum(pi, 1e-300)), 0)))
    def dim(p, L): lL = np.log(np.maximum(L, 1e-300)); m = (p * lL).sum(); return 2 * float((p * (lL - m) ** 2).sum())
    lnR = float(np.log((pi * LA * LB).sum()) - np.log((pi * LA).sum()) - np.log((pi * LB).sum())); lnI = KL(pA) + KL(pB) - KL(pAB); lnS = lnR - lnI
    d = dim(pA, LA) + dim(pB, LB) - dim(pAB, LA * LB)
    if d <= 0: return dict(lnR=lnR, lnS=lnS, d=d, p=np.nan, sigma=np.nan)
    x = d - 2 * lnS; p = float(stats.chi2.sf(x, d)) if x > 0 else 1.0
    return dict(lnR=lnR, lnS=lnS, d=d, p=p, sigma=float(stats.norm.isf(p / 2)) if p < 1 else 0.0)
def summ(p):
    c = np.cumsum(p[o]); q = lambda f: la[o][np.searchsorted(c, f)]
    return dict(mean=float((p * la).sum()), median=float(q(0.5)), p05=float(q(0.05)), p95=float(q(0.95)), N33=100 * float(p[la >= -33].sum()))
M32 = lambda d, ell: (lambda r: (1 + r) * np.exp(-r))(np.sqrt(3) * np.abs(d) / ell)
def fit_gp(x, y, v):
    n = len(x); one = np.ones(n); D = x[:, None] - x[None]
    def parts(th):
        s2, ell, t2 = np.exp(2 * th[0]), np.exp(th[1]), np.exp(2 * th[2]); K = s2 * M32(D, ell) + np.diag(v + t2); return np.linalg.cholesky(K), K
    def nll(th):
        try: L, K = parts(th)
        except np.linalg.LinAlgError: return 1e10
        Ki1 = np.linalg.solve(K, one); mu = (Ki1 @ y) / (Ki1 @ one); r = y - mu; a = np.linalg.solve(K, r)
        return 0.5 * r @ a + np.log(np.diag(L)).sum() + 0.5 * np.log(Ki1 @ one)
    best = None
    for l0 in (0.0, 1.0, 2.0):
        for s0 in (0.0, 1.0):
            r = minimize(nll, [s0, l0, -1.0], method='L-BFGS-B', bounds=[(-2, 3), ((np.log(FIXELL) if FIXELL else np.log(0.5)), (np.log(FIXELL) if FIXELL else np.log(15))), (-6, 1.5)])
            if best is None or r.fun < best.fun: best = r
    th = best.x; L, K = parts(th); Ki1 = np.linalg.solve(K, one); mu = float((Ki1 @ y) / (Ki1 @ one))
    return dict(th=th, amp=float(np.exp(th[0])), ell=float(np.exp(th[1])), tau=float(np.exp(th[2])), mu=mu, K=K, nll=float(best.fun))
def smoother(g, x, xs):
    Ks = np.exp(2 * g['th'][0]) * M32(xs[:, None] - x[None], np.exp(g['th'][1])); return Ks @ np.linalg.inv(g['K'])      # f = mu + A (y - mu)
def comb(lG, lY, which):
    if which == 'gc': return lG
    if which == 'gl': return lY
    mx = np.maximum(lG, lY); return mx + np.log(0.5 * (np.exp(lG - mx) + np.exp(lY - mx)))
def lnl(lm, idx):      # ln mean over the selected ocean samples at each point
    out = np.empty(lm.shape[0])
    for i in range(lm.shape[0]):
        r = lm[i, idx[i]] if isinstance(idx, list) else lm[i, idx]; r = r[np.isfinite(r)]; mx = r.max(); out[i] = mx + np.log(np.mean(np.exp(r - mx)))
    return out
def load_lm(cfg):
    fs = sorted(glob.glob(f'res-smooth-w48/lm-{cfg}-s*.npz')); Z = [np.load(f) for f in fs]; out = {}
    for m in ('globcurrent', 'glorys12'):
        S = np.stack([z[f'lm_{m}'] for z in Z]); mx = np.nanmax(S, 0); out[m] = mx + np.log(np.nanmean(np.exp(S - mx), 0))
    return out['globcurrent'], out['glorys12'], Z[0]['lat'], len(fs)
def curve_stats(f, inside):
    LB = np.where(inside, np.exp(f - f[inside].max()), 0.0); p = pi * LB; p = p / p.sum(); return LB, p
CASES = [('Two ocean models', 'head', 'both'), ('GlobCurrent only', 'head', 'gc'), ('GLORYS12 only', 'head', 'gl'), ('No finds on Australian coasts (0.25)', 'au025', 'both'), ('Without Mossel Bay', 'butmb', 'both'), ('No finds on Australian coasts (0.25), without Mossel Bay', 'au025nomb', 'both'),
         ('Mossel Bay at the ATSB find date (21-23 Mar 2016)', 'mar', 'both'), ('Mossel Bay arrival within 10 days of 23 Dec 2015', 'fresh10', 'both'),
         ('Identity weights all 1', 'pw1', 'both'), ('Identity weights 1 / 0.9 / 0.7', 'pwlow', 'both')]
F0 = {}; rows, curves, nodetab, halves = [], {'lat': la, 'core': pc, 'prior': pi}, [], []
for name, cfg, which in CASES:
    lG, lY, lat, ns = load_lm(cfg); x = lat; inside = (la >= lat.min()) & (la <= lat.max())
    blocks = [np.arange(0, 16), np.arange(16, 32), np.arange(32, 48)]; valid = np.isfinite(lG)
    y0 = comb(lnl(lG, np.arange(48)), lnl(lY, np.arange(48)), which)
    Yb = np.empty((B, len(x)))
    for b in range(B):
        idx = np.concatenate([rng.choice(bl, len(bl), replace=True) for bl in blocks]); Yb[b] = comb(lnl(lG, idx), lnl(lY, idx), which)
    v = Yb.var(0) + 1e-6; g = fit_gp(x, y0, v); A = smoother(g, x, la); Ai = A     # smoother onto ledger bins
    f0 = g['mu'] + A @ (y0 - g['mu']); fb = g['mu'] + (Yb - g['mu']) @ A.T            # (B, bins)
    # raw (unsmoothed) curve: average points at equal latitude, interpolate to the ledger bins
    ul = np.unique(x); yr = np.array([np.log(np.mean(np.exp(y0[x == u] - y0.max()))) + y0.max() for u in ul]); fr = np.interp(la, ul, yr)
    def stat(f):
        LB, p = curve_stats(f, inside); return dict(**summ(p), **tension(np.where(inside, LB, 1e-300))), p
    F0[name] = f0
    s0, p0 = stat(f0); sr, pr = stat(fr); sb = [stat(fb[b])[0] for b in range(B)]; pbs = np.array([curve_stats(fb[b], inside)[1] for b in range(B)])
    SB = pd.DataFrame(sb); pct = lambda c: np.nanpercentile(SB[c], [5, 50, 95])
    r = dict(case=name, config=cfg, models=which, seeds=ns, draws=16384 * ns, gp_amp=g['amp'], gp_length_deg=g['ell'], gp_nugget=g['tau'])
    for c in ('median', 'mean', 'N33', 'lnS', 'p', 'sigma', 'd'): r[c] = s0[c]; r[c + '_b05'], r[c + '_b50'], r[c + '_b95'] = pct(c) if np.isfinite(SB[c]).any() else (np.nan,) * 3
    r['frac_d_undefined'] = float(SB.p.isna().mean()); r.update({'raw_' + c: sr[c] for c in ('median', 'mean', 'N33', 'lnS', 'p', 'sigma')}); rows.append(r)
    curves[name] = p0; curves[name + ' | raw'] = pr; curves[name + ' | b05'] = np.percentile(pbs, 5, 0); curves[name + ' | b95'] = np.percentile(pbs, 95, 0)
    nodetab.append(pd.DataFrame(dict(case=name, lat=x, y_raw=y0, boot_sd=np.sqrt(v), y_smooth=g['mu'] + (smoother(g, x, x) @ (y0 - g['mu'])))))
    # split halves: even / odd ocean samples within each block
    for hn, hs in (('A', [bl[0::2] for bl in blocks]), ('B', [bl[1::2] for bl in blocks])):
        idx = np.concatenate(hs); yh = comb(lnl(lG, idx), lnl(lY, idx), which); gh = fit_gp(x, yh, v * 2); fh = gh['mu'] + smoother(gh, x, la) @ (yh - gh['mu']); sh, ph = stat(fh)
        halves.append(dict(case=name, half=hn, gp_length_deg=gh['ell'], **{c: sh[c] for c in ('median', 'mean', 'N33', 'lnS', 'p', 'sigma')}, max_abs_density_diff_vs_full=float(np.abs(ph - p0).max() / p0.max())))
    print(name, {k: (round(v_, 3) if isinstance(v_, float) else v_) for k, v_ in r.items() if k in ('median', 'median_b05', 'median_b95', 'N33', 'lnS', 'p', 'p_b05', 'p_b95', 'gp_length_deg', 'gp_nugget', 'raw_median')}, flush=True)
# date-uncertainty mixture for the Mossel Bay item: L = w L(23 Dec 2015) + (1 - w) L(ATSB find date, 21-23 Mar 2016), other items unchanged (point estimates, no bootstrap)
mixrows = []
for w in (0.0, 0.1, 0.25, 0.5, 0.75, 0.9, 1.0):
    fD, fM = F0['Two ocean models'], F0['Mossel Bay at the ATSB find date (21-23 Mar 2016)']
    f = fM if w == 0 else (fD if w == 1 else np.logaddexp(np.log(w) + fD, np.log(1 - w) + fM)); s_, p_ = stat(f)
    mixrows.append(dict(w_photograph_date_correct=w, **{c: s_[c] for c in ('median', 'mean', 'N33', 'lnS', 'p', 'sigma', 'd')}, posterior_weight_on_dec=float(w * np.exp(np.logaddexp.reduce(np.log(pi[inside]) + fD[inside])) / (w * np.exp(np.logaddexp.reduce(np.log(pi[inside]) + fD[inside])) + (1 - w) * np.exp(np.logaddexp.reduce(np.log(pi[inside]) + fM[inside])))) if 0 < w < 1 else float(w)))
pd.DataFrame(mixrows).to_csv(f'res-smooth-w48/smoothed{SUF}-date-mixture.csv', index=False); print(pd.DataFrame(mixrows).round(3).to_string(index=False))
T = pd.DataFrame(rows); T.to_csv(f'res-smooth-w48/smoothed{SUF}-drift-alone-summary.csv', index=False); pd.DataFrame(halves).to_csv(f'res-smooth-w48/smoothed{SUF}-split-halves.csv', index=False)
pd.DataFrame(curves).to_csv(f'res-smooth-w48/smoothed{SUF}-drift-alone-curves.csv', index=False); pd.concat(nodetab).to_csv(f'res-smooth-w48/smoothed{SUF}-node-table.csv', index=False)
print(pd.DataFrame(halves).round(3).to_string(index=False))
