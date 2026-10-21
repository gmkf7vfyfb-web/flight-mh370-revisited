"""Pete's 17 Oct Australian scheme (ABS tiers city+inner 1 / outer 0.3 / remote 0, times level rho = 0.3, 0.5, 0.65,
constant in time) at the 84 arc-latitude points, OFFLINE from stored node tables (no transport). Ocean drift, 21 Oct 2026.

The stored tables cannot give the module's exact value: the node likelihood (lib.rs node_ln_likelihood_zeros) is
  ln L = ln mean_{env, level draw} sum_c sum_{j in c} [ ln(a_cj . nu) - ln(A_c . nu) ],
with A_c the delay-weighted arrival coefficients per (segment x period) block for each (environment, class), a_cj the find
kernels, nu ~ log-normal(mu_block, 1) with 256 common draws. The tables hold only p_<class>_<segment> (arrivals before the
window end, averaged over environments, no period split, no delay weighting, no split halves) and the ln L columns.
So this is an EMULATOR of the module's form, calibrated per node on the measured columns:
  Delta(lambda) = ln mean_d prod_c (1 + sum_{s in AU} p_cs lambda_s eps_ds / (kappa G_c))^(-n_c),  G_c = sum_{s in find coasts} p_cs,
  eps ~ LN(0,1) one draw per Australian segment (1,024 draws), n = 1 / 6 / 2 finds (flaperon / low-exposure / high-windage),
  k1: kappa per node fitted to (B, C, populated) minus off; k2: also a factor on outer+remote levels.
Validation gate: reproduce the measured B, C and populated columns (in-sample and leave-one-out).
Usage: python ruled_australia_offline.py <old_node_dir> <ext_node_dir> <accumulators.npz> <out_dir>
"""
import sys, os, glob
import numpy as np, pandas as pd
from scipy.optimize import minimize_scalar, minimize

CLS = {'flaperon': 1, 'low_exposure_exterior': 6, 'high_windage_interior': 2}
NC = np.array(list(CLS.values()), float)
CITY, OUTER, REMOTE = [6, 7, 8], [9, 10, 11], [12, 13, 14, 15]
AU, FIND = CITY + OUTER + REMOTE, [0, 1, 2, 3, 4, 5]
def tiers(c, o, r):
    lam = np.zeros(16); lam[CITY] = c; lam[OUTER] = o; lam[REMOTE] = r; return lam
SCH = {'populated': tiers(1, 0, 0), 'B': tiers(1, 0.3, 0.05), 'C': tiers(0.3, 0.1, 0.02)}
RUL = {r: tiers(r, 0.3 * r, 0) for r in (0.3, 0.5, 0.65)}
COL = {'off': 'ln_l_lev_off', 'populated': 'ln_l_lev_populated', 'B': 'ln_l', 'C': 'ln_l_lev_C'}
half = lambda col, h: (col + '_half_' + h) if col != 'ln_l' else 'ln_l_half_' + h
HCOL = {h: {k: half(c, h) for k, c in COL.items()} for h in 'ab'}
EPS = np.exp(np.random.default_rng(11).standard_normal((1024, 16)))
P_COLS = [[f'p_{c}_{s}' for s in range(16)] for c in CLS]


def delta(Pn, lam, lk):
    G = Pn[:, FIND].sum(1)
    U = (Pn[None] * lam[None, None] * EPS[:, None])[:, :, AU].sum(2)
    x = -(NC[None] * np.log1p(U / (np.exp(lk) * G[None]))).sum(1)
    mx = x.max(); return mx + np.log(np.mean(np.exp(x - mx)))
def delta2(Pn, lam, th):
    l2 = lam.copy(); l2[OUTER + REMOTE] *= np.exp(th[1]); return delta(Pn, l2, th[0])
def fit1(Pn, tg):
    return minimize_scalar(lambda lk: sum((delta(Pn, SCH[k], lk) - v) ** 2 for k, v in tg.items()), bounds=(-12, 6), method='bounded').x
def fit2(Pn, tg, x0=(-2.0, 0.0)):
    f = lambda th: sum((delta2(Pn, SCH[k], th) - v) ** 2 for k, v in tg.items()) + 1e-4 * th[1] ** 2
    return minimize(f, x0, method='Nelder-Mead', options=dict(xatol=1e-4, fatol=1e-8, maxiter=400)).x


def load(old_dir, ext_dir):
    T, MG = {}, {}
    for m in ('globcurrent', 'glorys12'):
        fs = sorted(glob.glob(f'{old_dir}/arclat-{m}-*-nodes.csv')) + sorted(glob.glob(f'{ext_dir}/arclat-ext-{m}-*-nodes.csv'))
        T[m] = {os.path.basename(f).replace('-nodes.csv', ''): pd.read_csv(f) for f in fs}
        old = pd.concat([v for k, v in T[m].items() if not k.startswith('arclat-ext')], ignore_index=True)
        new = pd.concat([T[m][f'arclat-ext-{m}-a'], T[m][f'arclat-ext-{m}-b']], ignore_index=True)
        new = new[new.lat_deg > -25.45]                       # the 26 S repeat rows are not merged (as on 20 Oct)
        MG[m] = pd.concat([old, new], ignore_index=True).sort_values(['lat_deg', 'lon_deg']).reset_index(drop=True)
    assert len(MG['globcurrent']) == 84 and np.allclose(MG['globcurrent'].lat_deg, MG['glorys12'].lat_deg)
    return T, MG


def gate(T):
    rows = []
    for m in T:
        for leg, d in T[m].items():
            P = np.stack([d[c].values for c in P_COLS], 1)
            for i in range(len(d)):
                meas = {k: d[COL[k]].iat[i] - d[COL['off']].iat[i] for k in SCH}
                r = dict(model=m, leg=leg, node=d.node.iat[i], lat=d.lat_deg.iat[i], lon=d.lon_deg.iat[i])
                lk, th = fit1(P[i], meas), fit2(P[i], meas)
                for k in SCH:
                    oth = {kk: v for kk, v in meas.items() if kk != k}
                    r.update({f'meas_{k}': meas[k], f'k1_fit_{k}': delta(P[i], SCH[k], lk), f'k1_loo_{k}': delta(P[i], SCH[k], fit1(P[i], oth)),
                              f'k2_fit_{k}': delta2(P[i], SCH[k], th), f'k2_loo_{k}': delta2(P[i], SCH[k], fit2(P[i], oth, th)),
                              f'sd_scheme_minus_off_{k}': abs((d[half(COL[k], 'a')].iat[i] - d[half(COL['off'], 'a')].iat[i]) - (d[half(COL[k], 'b')].iat[i] - d[half(COL['off'], 'b')].iat[i])) / 2,
                              f'sd_column_{k}': abs(d[half(COL[k], 'a')].iat[i] - d[half(COL[k], 'b')].iat[i]) / 2})
                rows.append(r)
    V = pd.DataFrame(rows); g = []
    name = {'B': 'option B', 'C': 'option C', 'populated': 'populated coast only'}
    for e_ in ('k1', 'k2'):
        for how in ('fit', 'loo'):
            for k in SCH:
                e = V[f'{e_}_{how}_{k}'] - V[f'meas_{k}']
                g.append(dict(emulator=e_, test={'fit': 'in-sample', 'loo': 'leave-one-out'}[how], column=name[k], nodes=len(e), max_abs_diff=e.abs().max(),
                              rms_diff=np.sqrt((e ** 2).mean()), median_sd_scheme_minus_off=V[f'sd_scheme_minus_off_{k}'].median(),
                              median_sd_column=V[f'sd_column_{k}'].median(), share_within_2sd_scheme_minus_off=(e.abs() <= 2 * V[f'sd_scheme_minus_off_{k}']).mean(),
                              share_within_2sd_column=(e.abs() <= 2 * V[f'sd_column_{k}']).mean()))
    return V, pd.DataFrame(g)


def core(acc):
    A = np.load(acc); H = A['H_D0_all'].astype(float); hl0, hn0, hg = float(A['lat0']), float(A['lon0']), float(A['grid'])
    hlat = hl0 + (np.arange(H.shape[0]) + 0.5) * hg; hlon = hn0 + (np.arange(H.shape[1]) + 0.5) * hg
    ii, jj = np.nonzero(H > 0); return hlat[ii], hlon[jj], H[ii, jj]


def make_shift(MG, cl, cn, hw):
    plat, plon = MG['globcurrent'].lat_deg.values, MG['globcurrent'].lon_deg.values
    dist = np.hypot((cn[:, None] - plon[None]) * 111.2 * np.cos(np.radians(cl[:, None])), (cl[:, None] - plat[None]) * 111.2)
    nn = np.argsort(dist, 1)[:, :6]; W = 1 / np.maximum(np.take_along_axis(dist, nn, 1), 1.0) ** 2; W /= W.sum(1, keepdims=True)
    cm = (hw * cl).sum() / hw.sum()
    def shift(lnG, lnY):
        a = (W * lnG[nn]).sum(1); b = (W * lnY[nn]).sum(1); mx = max(a.max(), b.max())
        p = hw * 0.5 * (np.exp(a - mx) + np.exp(b - mx)); p /= p.sum()
        o = np.argsort(cl); med = cl[o][np.searchsorted(np.cumsum(p[o]), 0.5)]
        return dict(shift=(p * cl).sum() - cm, median=med, share_N33=100 * p[cl >= -33].sum(), share_N26=100 * p[cl >= -26].sum())
    return shift


def emulate(MG, method, colmap, targets):
    out = {}
    for m, d in MG.items():
        P = np.stack([d[c].values for c in P_COLS], 1); out[m] = {k: np.zeros(len(d)) for k in targets}
        for i in range(len(d)):
            meas = {k: d[colmap[k]].iat[i] - d[colmap['off']].iat[i] for k in SCH}
            if method == 'k1':
                lk = fit1(P[i], meas); f = lambda lam: delta(P[i], lam, lk)
            else:
                th = fit2(P[i], meas); f = lambda lam: delta2(P[i], lam, th)
            for k, lam in targets.items():
                out[m][k][i] = d[colmap['off']].iat[i] + f(lam)
    return out


if __name__ == '__main__':
    old_dir, ext_dir, acc, out = sys.argv[1:5]; os.makedirs(out, exist_ok=True)
    T, MG = load(old_dir, ext_dir)
    V, G = gate(T); V.to_csv(f'{out}/gate-per-node.csv', index=False); G.to_csv(f'{out}/gate-summary.csv', index=False)
    cl, cn, hw = core(acc); shift = make_shift(MG, cl, cn, hw)
    # posterior-level leave-one-out: emulate each measured column from the other two and compare the run J D0' shift
    lo = []
    for method in ('k1', 'k2'):
        for tgt in SCH:
            cm = {k: COL[k] for k in COL}
            E = {}
            for m, d in MG.items():
                P = np.stack([d[c].values for c in P_COLS], 1); v = np.zeros(len(d))
                for i in range(len(d)):
                    oth = {k: d[COL[k]].iat[i] - d[COL['off']].iat[i] for k in SCH if k != tgt}
                    v[i] = d[COL['off']].iat[i] + (delta(P[i], SCH[tgt], fit1(P[i], oth)) if method == 'k1' else delta2(P[i], SCH[tgt], fit2(P[i], oth)))
                E[m] = v
            se, sm = shift(E['globcurrent'], E['glorys12']), shift(MG['globcurrent'][COL[tgt]].values, MG['glorys12'][COL[tgt]].values)
            lo.append(dict(emulator=method, held_out=tgt, shift_emulated=se['shift'], shift_measured=sm['shift'], shift_error=se['shift'] - sm['shift'],
                           share_N33_error=se['share_N33'] - sm['share_N33']))
    pd.DataFrame(lo).to_csv(f'{out}/gate-posterior-leave-one-out.csv', index=False)
    # provisional ruled-scheme columns (NOT validated): k1 full and split halves, k2 full
    k1 = emulate(MG, 'k1', COL, RUL); k1a = emulate(MG, 'k1', HCOL['a'], RUL); k1b = emulate(MG, 'k1', HCOL['b'], RUL); k2 = emulate(MG, 'k2', COL, RUL)
    g = MG['globcurrent']; prof = pd.DataFrame(dict(node_lat=g.lat_deg, node_lon=g.lon_deg))
    mix = lambda a, b: np.maximum(a, b) + np.log(0.5 * (np.exp(a - np.maximum(a, b)) + np.exp(b - np.maximum(a, b))))
    post = []
    for r in RUL:
        lab = f'ruled level {r}'
        v = mix(k1['globcurrent'][r], k1['glorys12'][r]); prof[lab] = v - v.max()
        prof[lab + '_sd'] = np.sqrt(((k1a['globcurrent'][r] - k1b['globcurrent'][r]) / 2) ** 2 + ((k1a['glorys12'][r] - k1b['glorys12'][r]) / 2) ** 2) / 2
        for m in MG:
            prof[f'{lab} [{m}, ln L, k1]'] = k1[m][r]; prof[f'{lab} [{m}, ln L, k2]'] = k2[m][r]
        s, sa, sb, s2 = shift(k1['globcurrent'][r], k1['glorys12'][r]), shift(k1a['globcurrent'][r], k1a['glorys12'][r]), shift(k1b['globcurrent'][r], k1b['glorys12'][r]), shift(k2['globcurrent'][r], k2['glorys12'][r])
        post.append(dict(level=r, model='mean', shift_k1=s['shift'], shift_halfdiff=abs(sa['shift'] - sb['shift']), median=s['median'], share_N33=s['share_N33'],
                         share_N26=s['share_N26'], shift_k2=s2['shift'],
                         shift_k1_globcurrent=shift(k1['globcurrent'][r], k1['globcurrent'][r])['shift'], shift_k1_glorys12=shift(k1['glorys12'][r], k1['glorys12'][r])['shift']))
    for k in ('off', 'C', 'B', 'populated'):
        s = shift(MG['globcurrent'][COL[k]].values, MG['glorys12'][COL[k]].values)
        post.append(dict(level=f'measured {k}', model='mean', shift_k1=s['shift'], median=s['median'], share_N33=s['share_N33'], share_N26=s['share_N26']))
    prof.to_csv(f'{out}/arclat-ruled-australia-RECONSTRUCTED-gate-failed.csv', index=False)
    pd.DataFrame(post).to_csv(f'{out}/arclat-ruled-australia-posterior-RECONSTRUCTED.csv', index=False)
    print(G.round(3).to_string(index=False)); print(pd.DataFrame(lo).round(3).to_string(index=False)); print(pd.DataFrame(post).round(3).to_string(index=False))
