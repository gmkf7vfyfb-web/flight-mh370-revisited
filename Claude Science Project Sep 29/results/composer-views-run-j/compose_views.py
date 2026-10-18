"""Composer views on run J, step 2: pool the per-seed reductions and compute the composer brief section 0 products.

Pooling: seeds pooled by evidence within a stratum (ln(P_s / K_s) + seed scale, as option_table_0019 / combine_strata_0019);
strata mixed by core run J's P(family) at equal prior (core summary.json log_evidence). 00:19 options D0-D5 under the headline
cause model (competing causes, q = 1/3, other cause silent). D3 and D4: waypoints stratum from end of flight's both-burst
supplementary pass (8 seeds; EoF note section 3b), other strata production; the production-only version is a check.
Views (brief 0.1): (a) E alone on a prior uniform along the 7th arc: (ii) run J rows reweighted by r = u / q per 10 NM bin of
the arc position of their 00:19:29 crossing (u uniform per NM over the span the run J crossings reach, q the pooled core proposal
mass; arc_r.py), with not-computed rows carried at the mean under that base; and (i) the module's own surface evaluated at every
arc bin with one fixed end-of-flight displacement distribution (impact minus crossing, core D0, pooled); (b) core + E;
(c) all except E, and all. Disagreement (0.2), influence (0.3), whole-arc outputs (0.7).
Usage: python compose_views.py OUTDIR
"""
import sys, json, glob, pathlib, re, importlib.util
import numpy as np
from scipy.special import logsumexp
HERE = pathlib.Path(__file__).resolve().parent; PROJ = HERE.parents[1]
sys.path.insert(0, str(HERE))
import views_common as V, views_lib as VL
X = pathlib.Path('/Users/pete/Downloads/mh370-exchange'); WORK = X / 'composer/run-j-views/work'
OUT = pathlib.Path(sys.argv[1]); OUT.mkdir(parents=True, exist_ok=True)
STRATA = ['run-j-waypoints', 'run-j-free', 'run-j-repro-radar', 'run-j-descent-climb']
DK = [f'D{d}' for d in range(6)]
DNAME = {'D0': '00:19 data held out', 'D1': '00:19:29 BTO', 'D2': '00:19:29 BTO + BFO', 'D3': 'both 00:19 BFOs as recorded',
         'D4': 'both 00:19 BFOs, shared start-up offset', 'D5': '00:19:37 BFO with start-up offset'}
PRODS = ['core', 'D', 'S', 'P', 'DS', 'DP', 'SP', 'DSP', 'A', 'AS', 'AP', 'ASP', 'D100', 'D100S', 'DG', 'DC', 'DGS', 'DCS',
         'S00', 'S25', 'S50', 'DS00', 'DS25', 'DS50', 'SX', 'DSX', 'SPX', 'DSPX', 'ASX',
         'U', 'UD', 'US', 'UP', 'UA', 'UD100', 'US00', 'US25', 'US50', 'USX']
UMAP = {'D': 'UD', 'S': 'US', 'P': 'UP', 'A': 'UA', 'D100': 'UD100', 'S00': 'US00', 'S25': 'US25', 'S50': 'US50', 'SX': 'USX'}
AE = ('D', 'S', 'P', 'A', 'D100', 'S00', 'S25', 'S50', 'SX')
ARCR = np.load(WORK / 'arc-r.npz'); ARCINFO = json.loads(str(ARCR['info']))
FAMN = ['A1', 'A2', 'B']
lnZc = {s: json.load(open(X / f'core/run-j/{s}/summary.json'))['cases'][0]['log_evidence'] for s in STRATA}
lse = logsumexp(list(lnZc.values())); PFAM = {s: float(np.exp(v - lse)) for s, v in lnZc.items()}
rng = np.random.default_rng(17102026); NBOOT = 400

WV = WORK / 'v6'
files = {('prod', s): sorted(glob.glob(str(WV / f'prod_{s}_*.npz')), key=lambda f: int(re.findall(r'_(\d+)\.npz$', f)[0])) for s in STRATA}
files[('both', 'run-j-waypoints')] = sorted(glob.glob(str(WV / 'both_run-j-waypoints_*.npz')))
EXPECT = {'run-j-waypoints': 24, 'run-j-free': 18, 'run-j-repro-radar': 16, 'run-j-descent-climb': 16}
import os
PARTIAL = os.environ.get('PARTIAL') == '1'
if PARTIAL:   # development only: whatever seeds exist; strata without files dropped
    STRATA = [s for s in STRATA if files[('prod', s)]]
    if not files[('both', 'run-j-waypoints')]:
        files[('both', 'run-j-waypoints')] = files[('prod', 'run-j-waypoints')]
    NBOOT = 20
else:
    for s in STRATA:
        assert len(files[('prod', s)]) == EXPECT[s], (s, len(files[('prod', s)]))
    assert len(files[('both', 'run-j-waypoints')]) == 8

def setfor(variant, d, s):
    return 'both' if (variant == 'head' and d in ('D3', 'D4') and s == 'run-j-waypoints') else 'prod'

# ---------- load and pool (each per-seed file decompressed once)
raw_cnt = np.zeros(V.NSUB + 1); raw_lon = np.zeros(V.NSUB + 1)
pool, perseed, ncs, meta = {}, {}, {}, {'checks': {'outside_grid_rows': 0, 'files': 0}}

VARS = [('head', d) for d in DK] + [('prodonly', 'D3'), ('prodonly', 'D4')]
# pass 1: seed constants c = ln(P_s / K_s) + seed scale, per (variant, option); reference = max
use = {}   # file -> list of (variant, d, stratum, c)
for variant, d in VARS:
    cs = []
    for s in STRATA:
        fl = files[(setfor(variant, d, s), s)]; K = len(fl)
        for f in fl:
            z = np.load(f)
            if int(z[f'{d}|valid']):
                cs.append((f, s, np.log(PFAM[s] / K) + float(z[f'{d}|s'])))
    cref = max(c for _, _, c in cs)
    for f, s, c in cs:
        use.setdefault(f, []).append((variant, d, s, float(np.exp(c - cref))))
    meta['checks'][f'n_seeds|{variant}|{d}'] = len(cs)
# pass 2: accumulate
order = [f for s in STRATA for key in (('prod', s), ('both', s)) if key in files for f in files[key] if f in use]
for f in order:
    z = dict(np.load(f)); meta['checks']['files'] += 1
    assert int(z['NSUB']) == V.NSUB and int(z['NY']) == V.NY and int(z['NX']) == V.NX, f
    meta['checks']['outside_grid_rows'] += int(z['n_outside_grid'])
    if f.split('/')[-1].startswith('prod'):
        raw_cnt += z['raw_count_sub']; raw_lon += z['raw_lon_sub']
    for variant, d, s, e in use[f]:
        for p in PRODS:
            key = (variant, d, p)
            S1 = e * z[f'{d}|{p}|S1'][:V.NSUB]; FAM = e * z[f'{d}|{p}|FAM'][:, :V.NSUB]
            MP = e * z[f'{d}|{p}|MAP'].astype(float)
            klk = [kk.split('|')[3] for kk in z if kk.startswith(f'{d}|KL|{p}|')]
            for ctx, s1, s2, mp, kl in [('mix', S1, e * e * z[f'{d}|{p}|S2'][:V.NSUB], MP[0], 'KL')] + \
                    [(FAMN[i], FAM[i], e * e * z[f'{d}|{p}|FAM2'][i, :V.NSUB], MP[i + 1], i) for i in range(3)] + [(s, S1, e * e * z[f'{d}|{p}|S2'][:V.NSUB], MP[0], 'KL')]:
                A = pool.setdefault((variant, d, p, ctx), {'S1': 0.0, 'S2': 0.0, 'IN': 0.0, 'INX': 0.0, 'NX': 0.0, 'MAP': 0.0, 'KL': {}, 'strat': {}, 'SB': 0.0})
                A['S1'] = A['S1'] + s1; A['S2'] = A['S2'] + s2; A['MAP'] = A['MAP'] + mp
                if ctx in ('mix',) + tuple(STRATA):
                    A['SB'] = A['SB'] + e * z[f'{d}|{p}|SB'][:V.NSB]
                if ctx in ('mix',) + tuple(STRATA):
                    A['IN'] = A['IN'] + e * z[f'{d}|{p}|IN'][:V.NSUB]; A['INX'] = A['INX'] + e * z[f'{d}|{p}|INX'][:V.NSUB]
                    A['NX'] = A['NX'] + e * float(z[f'{d}|{p}|NX'])
                if ctx == 'mix':
                    A['strat'][s] = A['strat'].get(s, 0.0) + float(S1.sum())
                for b in klk:
                    v = e * float(z[f'{d}|KL|{p}|{b}']) if kl == 'KL' else e * float(z[f'{d}|KLfam|{p}|{b}'][kl])
                    A['KL'][b] = A['KL'].get(b, 0.0) + v
            perseed.setdefault(key, []).append((s, S1.astype(np.float64)))
        for kk in list(z):
            if kk.startswith(f'{d}|nc|'):
                nm = kk.split('|')[2]; T = ncs.setdefault((variant, d, nm), [0.0, 0.0])
                if False: pass
                T[0] += e * float(z[f'{d}|M']) * float(z[kk]); T[1] += e * float(z[f'{d}|M'])
        T = ncs.setdefault((variant, d, 'no 00:19:29 crossing (weight 0 in arc-uniform views)'), [0.0, 0.0])
        T[0] += e * float(z[f'{d}|M']) * float(z[f'{d}|noburst_share']); T[1] += e * float(z[f'{d}|M'])
    print('pooled', f.split('/')[-1], flush=True)

# ---------- arc geometry (views_common: small circle fitted by arc_line.py; span from arc_r.py)
SPAN_NM = ARCINFO['span_nm']; span_ends = ARCINFO['span_ends_latlon']
SB_MID = (np.arange(V.NSB) + 0.5) * V.SBIN_NM
def s_median(SB):
    c = np.concatenate([[0], np.cumsum(SB)]) / np.sum(SB); return float(np.interp(0.5, c, np.arange(V.NSB + 1) * V.SBIN_NM))
meta['arc'] = {'centre': V.ARC_C, 'radius_deg': V.ARC_RAD, 'span_nm_from_southern_tip': SPAN_NM, 'span_nm': SPAN_NM[1] - SPAN_NM[0],
               'span_ends_latlon': span_ends, 'arc_bins_10nm_in_span_with_lt10_crossings': ARCINFO['bins_in_span_with_lt10'],
               'uniform_share_unreachable': {k.split('|')[1] + ('' if k.startswith('head') else ' (production only)'): v for k, v in ARCINFO.items() if k.endswith('unreachable')},
               'raw_samples_by_5deg': {f'{lo}': float(raw_cnt[:V.NSUB][(V.SUB_EDGES[:-1] >= lo) & (V.SUB_EDGES[:-1] < lo + 5)].sum()) for lo in range(-50, -5, 5)}}

# ---------- helpers on pooled arrays
def l01(S1):
    return np.bincount(V.SUB_L01, S1, len(V.L01_MID))
BAND_EDGES = np.arange(-50, -5, 1.0)
def bands(h01):
    return np.array([h01[(V.L01_MID >= a) & (V.L01_MID < a + 1)].sum() for a in BAND_EDGES[:-1]]) / h01.sum()
def rowsum(S):
    return np.bincount(V.SUB_ROW, S, V.NY)
def summarise(S1, S2, MAP, IN=None):
    h = l01(S1); q = VL.quantiles(h, V.L01_EDGES); tot = S1.sum()
    out = {'q05': q[0], 'median': q[1], 'q95': q[2], 'mean': float((h * V.L01_MID).sum() / h.sum()),
           'ESS': float(tot ** 2 / S2.sum()) if np.sum(S2) > 0 else 0.0,
           'north_of_33S': float(h[V.L01_MID > -33].sum() / h.sum()), 'north_of_30S': float(h[V.L01_MID > -30].sum() / h.sum()),
           'bands': bands(h).tolist(), 'modes': VL.modes_1d(h, V.L01_MID)}
    for lv in (0.5, 0.9, 0.95):
        out[f'hpd{int(lv * 100)}_km2'] = float(VL.hpd_mask(MAP, lv).sum() * V.CELL_KM2)
    if IN is not None and np.ndim(IN):
        out['p_on_searched_ground'] = float(np.sum(IN) / tot)
        inb = np.array([IN[(V.SUB_EDGES[:-1] >= a) & (V.SUB_EDGES[:-1] < a + 1)].sum() for a in BAND_EDGES[:-1]]) / tot
        out['searched_by_band'] = inb.tolist()
    # Kish ESS per 5-degree band (within the band)
    ek = {}
    for lo in range(-50, -5, 5):
        sel = (V.SUB_EDGES[:-1] >= lo) & (V.SUB_EDGES[:-1] < lo + 5); a, b = S1[sel].sum(), S2[sel].sum()
        ek[f'{lo}'] = float(a * a / b) if b > 0 else 0.0
    out['kish_ess_by_5deg'] = ek
    sel = V.SUB_EDGES[:-1] >= -33.0; a, b = S1[sel].sum(), S2[sel].sum(); out['kish_ess_north_of_33S'] = float(a * a / b) if b > 0 else 0.0
    return out
def view_a(variant, d, E, ctx):
    PU, PE = pool[(variant, d, 'U', ctx)], pool[(variant, d, UMAP[E], ctx)]
    return PE['S1'], PE['S2'], np.asarray(PE['MAP']), PE['IN'], float(np.log(PE['S1'].sum() / PU['S1'].sum())), \
        ARCINFO.get(f'{variant}|{d}|uniform_share_unreachable', ARCINFO.get(f'head|{d}|uniform_share_unreachable'))

# ---------- view (a)(i): module surfaces at every 10 NM arc bin of the span, one fixed end-of-flight displacement distribution
spec = importlib.util.spec_from_file_location('seabed_loglik', str(PROJ / 'results/composer-pass1-run-c/seabed_loglik.py'))
SL = importlib.util.module_from_spec(spec); spec.loader.exec_module(SL); SL.COV = PROJ / 'engine/hypotheses/seabed-search/coverage'
DISP = ARCR['disp']; de_c = np.arange(-500, 500, 5) + 2.5
keep = DISP > 1e-6 * DISP.max(); ie, jn = np.where(keep); dw = DISP[keep] / DISP[keep].sum(); dE, dN = de_c[ie], de_c[jn]
kb = np.where(ARCR['span'])[0]; sk = SB_MID[kb]; alat, alon = V.arc_point(sk)
PL = (alat[:, None] + dN[None] / 111.32).ravel(); PO = (alon[:, None] + dE[None] / (111.32 * np.cos(np.radians(alat[:, None] + dN[None] / 222.64)))).ravel()
Nn = np.load(WORK / 'nodes.npz'); ins, nid, Wc = V.drift_corners(PL, PO)
surf = {}
for tag, mod in (('G', 'glorys12'), ('C', 'globcurrent')):
    surf['D' + tag] = V.drift_lookup(ins, nid, Wc, np.exp(Nn[f'{mod}_h50'] + 125.0))
    surf['A' + tag] = V.drift_lookup(ins, nid, Wc, np.exp(Nn[f'{mod}_h50'] + Nn[f'{mod}_dpop'] + 125.0))
del ins, nid, Wc
pm = {}
for line in (X / 'pleiades/run-i/surfaces/joint-surface-rho0.25-gcrel.toml').read_text().splitlines():
    k_, v_ = line.split(' = ', 1); pm[k_] = v_
nl_, nn_ = int(pm['nlat']), int(pm['nlon']); J = np.fromfile(X / 'pleiades/run-i/surfaces/joint-surface-rho0.25-gcrel.f32', '<f4').reshape(2, nl_, nn_).astype(float)
PREF = float(np.nanmax(np.where(np.isfinite(J), J, np.nan)))
pi_ = np.floor((PL - (float(pm['lat0']) - float(pm['step_deg']) / 2)) / float(pm['step_deg'])).astype(int); pj_ = np.floor((PO - (float(pm['lon0']) - float(pm['step_deg']) / 2)) / float(pm['step_deg'])).astype(int)
okp = (pi_ >= 0) & (pi_ < nl_) & (pj_ >= 0) & (pj_ < nn_)
for mi, tag in ((0, 'G'), (1, 'C')):
    v = np.full(len(PL), np.nan); v[okp] = J[mi, pi_[okp], pj_[okp]]; surf['P' + tag] = np.where(np.isfinite(v), np.exp(v - PREF), np.nan)
del J
surf['SX'] = np.exp(SL.loglik(PL, PO))
_mB = (1 - 0.945 * SL.coverage(SL.decode(SL.COV / 'phase2.cov'), PL, PO)) * (1 - 0.9 * SL.coverage(SL.decode(SL.COV / 'bluefin-2014.cov'), PL, PO))
for _n, _qf in (('ocean-infinity-2018', 0.9 * 0.889), ('ocean-infinity-2025', 0.9 * 0.7808)):
    _mB = _mB * (1 - _qf * SL.coverage(SL.decode(SL.COV / f'{_n}.cov'), PL, PO))
surf['S'] = 0.05 + 0.95 * _mB
W2 = np.broadcast_to(dw[None], (len(sk), len(dw))).ravel() / len(sk)     # uniform over arc bins x displacement distribution
li01 = np.clip(np.searchsorted(V.L01_EDGES, PL, side='right') - 1, 0, len(V.L01_MID) - 1)
VI = {}
for E in ('D', 'S', 'P', 'A', 'SX'):
    if E in ('S', 'SX'):
        Ls = [surf[E]]
    else:
        Ls = [surf[E + 'G'], surf[E + 'C']]
    lam = 0.0; ncw = 0.0
    for Lm in Ls:                      # per ocean model: not computed carried at the mean of the computed points under this base
        ok = np.isfinite(Lm); bar = np.sum(W2[ok] * Lm[ok]) / np.sum(W2[ok]); lam = lam + np.where(ok, Lm, bar) / len(Ls); ncw += np.sum(W2[~ok]) / len(Ls)
    w = W2 * lam; h01 = np.bincount(li01, w, len(V.L01_MID)); sbm = (w.reshape(len(sk), -1)).sum(1)
    SBf = np.zeros(V.NSB); SBf[kb] = sbm
    VI[E] = {'h01': h01, 'SB': SBf, 'lnE_uniform_i': float(np.log(w.sum())), 'not_computed_share': float(ncw),
             'median_lat': VL.quantiles(h01, V.L01_EDGES, (0.5,))[0], 'median_arc_nm': s_median(SBf),
             'north_of_33S': float(h01[V.L01_MID > -33].sum() / h01.sum())}
meta['view_a_i'] = {'arc_bins': int(len(sk)), 'displacement_points': int(len(dw)), 'displacement_sd_km': [float(np.sqrt(np.sum(dw * dE ** 2) - np.sum(dw * dE) ** 2)), float(np.sqrt(np.sum(dw * dN ** 2) - np.sum(dw * dN) ** 2))],
                    'displacement_mean_km_east_north': [float(np.sum(dw * dE)), float(np.sum(dw * dN))], 'PREF': PREF,
                    'not_computed_share': {E: VI[E]['not_computed_share'] for E in VI}}

# ---------- assemble per (variant, option, context, product)
EVID = {'D': 'debris drift (finds)', 'S': 'searched areas', 'P': 'Pleiades objects (conditional on H)', 'A': 'debris drift with Australian non-recovery (sensitivity)'}
ALL_U = 'DS'; ALL_H = 'DSP'
LOO = {('D', ALL_U): 'S', ('S', ALL_U): 'D', ('D', ALL_H): 'SP', ('S', ALL_H): 'DP', ('P', ALL_H): 'DS',
       ('A', 'AS'): 'S', ('S', 'AS'): 'A', ('A', 'ASP'): 'SP', ('S', 'ASP'): 'AP', ('P', 'ASP'): 'AS',
       ('D', 'DSX'): 'SX', ('SX', 'DSX'): 'D', ('P', 'DSPX'): 'DSX', ('SX', 'DSPX'): 'DP', ('A', 'ASX'): 'SX', ('SX', 'ASX'): 'A'}
RES = {'meta': meta, 'pfam': PFAM, 'cells': {}}
def sm(P):
    out = summarise(P['S1'], P['S2'], np.asarray(P['MAP']), P.get('IN'))
    if np.ndim(P.get('INX', 0)):
        out['p_on_atsb_ground'] = float(np.sum(P['INX']) / np.sum(P['S1'])); out['p_in_next_oi_area'] = float(P['NX'] / np.sum(P['S1']))
    return out
ctxs = ['mix'] + FAMN + STRATA
for variant in ('head', 'prodonly'):
    for d in DK:
        if variant == 'prodonly' and d not in ('D3', 'D4'):
            continue
        for ctx in ctxs:
            C = {}; Pc = pool[(variant, d, 'core', ctx)]; Zc = Pc['S1'].sum()
            for p in PRODS:
                P = pool[(variant, d, p, ctx)]; s_ = sm(P); s_['lnE_given_core'] = float(np.log(P['S1'].sum() / Zc))
                if np.ndim(P['SB']):
                    s_['median_arc_nm'] = s_median(P['SB'])
                if ctx == 'mix':
                    tot = sum(P['strat'].values()); s_['stratum_share'] = {k: v / tot for k, v in P['strat'].items()}
                    s_['family_share'] = {FAMN[i]: float(pool[(variant, d, p, FAMN[i])]['S1'].sum() / P['S1'].sum()) for i in range(3)}
                s_['KL'] = {b: VL.kl_from_sums(v, P['S1'].sum(), pool[(variant, d, b, ctx)]['S1'].sum()) for b, v in P['KL'].items()}
                C[p] = s_
            # view (a)(ii) for each evidence type, disagreement against the core
            for E in (AE if variant == 'head' else ()):
                S1, S2, MAP, IN, lnEU, lost = view_a(variant, d, E, ctx)
                va = summarise(S1, S2, MAP, IN); va['lnE_uniform'] = lnEU; va['uniform_share_unreachable'] = lost
                PEu = pool[(variant, d, UMAP[E], ctx)]
                if np.ndim(PEu.get('INX', 0)):
                    va['p_on_atsb_ground'] = float(np.sum(PEu['INX']) / np.sum(PEu['S1'])); va['p_in_next_oi_area'] = float(PEu['NX'] / np.sum(PEu['S1']))
                if np.ndim(PEu['SB']):
                    va['median_arc_nm'] = s_median(PEu['SB'])
                va['lnER_core_vs_uniform'] = C[E]['lnE_given_core'] - lnEU
                ov = VL.overlap(np.asarray(Pc['MAP']), MAP, 0.9)
                va['vs_core'] = {**ov, 'bhattacharyya': VL.bhattacharyya(np.asarray(Pc['MAP']), MAP), 'median_shift_deg': va['median'] - C['core']['median'],
                                 'median_shift_nm': (va.get('median_arc_nm', np.nan) - C['core'].get('median_arc_nm', np.nan))}
                if E in VI and ctx == 'mix':
                    va['view_i'] = {k: v for k, v in VI[E].items() if k not in ('h01', 'SB')}
                    va['lnER_core_vs_uniform_i'] = C[E]['lnE_given_core'] - VI[E]['lnE_uniform_i']
                C['a_' + E] = va
            # (c) leave-one-out against all, influence
            for (E, allp), loo in LOO.items():
                Pa, Pl = pool[(variant, d, allp, ctx)], pool[(variant, d, loo, ctx)]
                lnEc = float(np.log(Pa['S1'].sum() / Pl['S1'].sum()))
                ov = VL.overlap(np.asarray(Pa['MAP']), np.asarray(Pl['MAP']), 0.9)
                C.setdefault('loo', {})[f'{E}|{allp}'] = {
                    'leave_out_product': loo, 'lnE_E_given_others': lnEc,
                    'lnER_vs_uniform': lnEc - C['a_' + E]['lnE_uniform'] if ('a_' + E) in C else np.nan,
                    **ov, 'bhattacharyya': VL.bhattacharyya(np.asarray(Pa['MAP']), np.asarray(Pl['MAP'])),
                    'median_shift_on_removal_deg': C[loo]['median'] - C[allp]['median'],
                    'median_shift_on_removal_nm': C[loo].get('median_arc_nm', np.nan) - C[allp].get('median_arc_nm', np.nan),
                    'hpd90_change_on_removal_km2': C[loo]['hpd90_km2'] - C[allp]['hpd90_km2'],
                    'KL_all_vs_loo': C[allp]['KL'].get(loo, np.nan), 'KL_all_vs_core': C[allp]['KL'].get('core', np.nan)}
                x = C['loo'][f'{E}|{allp}']; x['KL_share_of_total'] = x['KL_all_vs_loo'] / x['KL_all_vs_core'] if x['KL_all_vs_core'] > 0 else np.nan
                x['flag_KL_gt_half'] = bool(x['KL_share_of_total'] > 0.5)
            RES['cells'][f'{variant}|{d}|{ctx}'] = C
        print('assembled', variant, d, flush=True)

# ---------- not-computed shares
RES['not_computed'] = {f'{v}|{d}|{nm}': T[0] / T[1] for (v, d, nm), T in ncs.items()}

# ---------- seed bootstrap (within strata) for the mixture: band masses, north mass, median; and for the arc-uniform views
def boot(variant, d, prods, arcE=()):
    out = {}
    prods = list(prods) + [UMAP[E] for E in arcE]
    lists = {p: perseed[(variant, d, p)] for p in set(prods) | {'core'}}
    strata_idx = {s: [i for i, (ss, _) in enumerate(lists['core']) if ss == s] for s in STRATA}
    draws = [np.concatenate([rng.choice(ix, len(ix)) for ix in strata_idx.values() if ix]) for _ in range(NBOOT)]
    arr = {p: np.stack([a for _, a in lists[p]]) for p in lists}
    for p in prods:
        bm, nm, md = [], [], []
        for dr in draws:
            S = arr[p][dr].sum(0); h = l01(S); bm.append(bands(h)); nm.append(h[V.L01_MID > -33].sum() / h.sum()); md.append(VL.quantiles(h, V.L01_EDGES, (0.5,))[0])
        bm = np.array(bm); out[p] = {'band_se': bm.std(0).tolist(), 'north33_se': float(np.std(nm)), 'median_se': float(np.std(md))}
        pb = bands(l01(arr[p].sum(0)))
        out[p]['implied_n_by_5deg'] = {f'{lo}': implied(arr[p], draws, lo) for lo in range(-50, -5, 5)}
    for E in arcE:
        out['a_' + E] = out[UMAP[E]]
    return out
def implied(A_, draws, lo):
    vals = []
    for dr in draws:
        h = l01(A_[dr].sum(0)); vals.append(h[(V.L01_MID >= lo) & (V.L01_MID < lo + 5)].sum() / h.sum())
    h = l01(A_.sum(0)); p_ = h[(V.L01_MID >= lo) & (V.L01_MID < lo + 5)].sum() / h.sum(); se = np.std(vals)
    return float(p_ * (1 - p_) / se ** 2) if se > 0 else np.nan
RES['boot'] = {}
for d in DK:
    BP = ['core', 'D', 'S', 'P', 'A', 'DS', 'DSP', 'AS', 'ASP', 'DP', 'SP', 'SX', 'DSX', 'DSPX', 'ASX', 'DS00', 'DS25', 'DS50']
    RES['boot'][d] = boot('head', d, BP, arcE=('D', 'S', 'P', 'A', 'SX'))
    pn = {p: RES['cells'][f'head|{d}|mix'][p]['north_of_33S'] for p in BP}
    pn.update({'a_' + E: RES['cells'][f'head|{d}|mix']['a_' + E]['north_of_33S'] for E in ('D', 'S', 'P', 'A', 'SX')})
    for p in pn:
        se = RES['boot'][d][p]['north33_se']; RES['boot'][d][p]['implied_n_north_of_33S'] = float(pn[p] * (1 - pn[p]) / se ** 2) if se > 0 else np.nan
    print('boot', d, flush=True)

# ---------- maps needed for figures (head, D0, mix)
np.savez_compressed(OUT / 'maps-D0-mix.npz', **{p: np.asarray(pool[('head', 'D0', p, 'mix')]['MAP'], np.float32) for p in ('core', 'DS', 'DSP', 'AS', 'D', 'S', 'P', 'DSX', 'DSPX', 'SX')},
                    **{'a_' + E: view_a('head', 'D0', E, 'mix')[2].astype(np.float32) for E in ('D', 'S', 'P', 'A', 'SX')}, NY=V.NY, NX=V.NX)
np.savez_compressed(OUT / 'view-a-i.npz', **{E: VI[E]['h01'] for E in VI}, **{E + '_SB': VI[E]['SB'] for E in VI}, mids=V.L01_MID)
# 0.01 deg PDFs for figures
np.savez_compressed(OUT / 'pdf01-mix.npz', mids=V.L01_MID, **{f'{d}|{p}': l01(pool[('head', d, p, 'mix')]['S1']) for d in DK for p in PRODS},
                    **{f'{d}|a_{E}': l01(view_a('head', d, E, 'mix')[0]) for d in DK for E in ('D', 'S', 'P', 'A', 'SX')})

def clean(o):
    if isinstance(o, dict):
        return {str(k): clean(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [clean(v) for v in o]
    if isinstance(o, (np.floating, float)):
        return None if not np.isfinite(o) else float(o)
    if isinstance(o, (np.integer,)):
        return int(o)
    if isinstance(o, np.ndarray):
        return clean(o.tolist())
    return o
json.dump(clean(RES), open(OUT / 'views-run-j.json', 'w'))
print('WROTE', OUT / 'views-run-j.json')
