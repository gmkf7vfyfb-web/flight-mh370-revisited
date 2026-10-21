"""Composer views v3 on run J, step 2: compose on SETTLED seabed outcomes (numpy). Usage: python compose_v3.py OUTDIR

Base sample per 00:19 treatment D and flight-end family f: settling run J's resampled outcomes of product 'total' x f in each stratum
folder (each outcome 1/N), strata weighted by settling's stratum-mixture-weights.json (core share x Z_s(D), normalised) x the
family's share_of_option in that stratum. D3 / D4 waypoints: the both-burst folder (as views v2, searched areas and settling);
'prodonly' D3 / D4 with the production waypoints folder is a check. A composed product multiplies each outcome by its factors and
renormalises over all strata (so stratum weights become core share x Z_s x mean_s(factor), as required).
Factors: drift (finds only; dedicated arc-latitude run, joint ocean model), searched areas per-cell model V1 central on the settled
field (variants as labelled sensitivities), Pleiades (conditional on H), Australian non-recovery (labelled sensitivity: option B
pre-registered primary, C and populated coast as settings), hydroacoustics zero weight by ruling (no column).
Ocean model shared by drift, Australian term and Pleiades: Lambda = 0.5 (D_G P_G + D_C P_C).
Not computed (NaN) factor values: carried at the base-weighted mean of the computed outcomes of that (stratum, D, f) product, per
ocean model (ruling 15 Oct 2026, as v2); shares reported.
View (a): prior uniform per NM along the 7th arc (v2 span and u), r = u / q_hat per 10 NM bin of the 00:19:29 crossing, q_hat = core
base mass of the OUTCOME sample in that bin; bins of the span with no outcome are unreachable (share reported).
Seed bootstrap: seeds resampled with replacement within each stratum folder, NB draws.
"""
import sys, json, pathlib, time
import numpy as np
HERE = pathlib.Path(__file__).resolve().parent; sys.path.insert(0, str(HERE))
import views3_common as C
V = C.V
import views_lib as VL
X = C.X; W = X / 'composer/run-j-views-v3/work'
OUT = pathlib.Path(sys.argv[1]); OUT.mkdir(parents=True, exist_ok=True)
NB = int(sys.argv[2]) if len(sys.argv) > 2 else 200
rng = np.random.default_rng(19102026)
STRATA = ['run-j-waypoints', 'run-j-free', 'run-j-descent-climb', 'run-j-repro-radar']
DK = [f'D{d}' for d in range(6)]
FAMS = ['all', 'A1', 'A2', 'B']
MIXW = json.load(open(X / 'settling/run-j/stratum-mixture-weights.json'))['weights_per_cell']
ARCR = np.load(X / 'composer/run-j-views/work/arc-r.npz'); U_ARC = ARCR['u']; SPAN = ARCR['span']

import os
V31 = os.environ.get('V31') == '1'   # views v3.1 (19 Oct 2026): A1-branch stratified samples for waypoints totals and A1 under D3-D5
A1D = ('D3', 'D4', 'D5')
P0 = json.load(open(X / 'settling/run-j-a1branch/run-j-waypoints/rja1_pass0.json'))['cells'] if V31 else None
V32 = os.environ.get('V32') == '1'   # views v3.2 (20 Oct 2026): run J northern supplement for waypoint routes, D0'-D5
DEXT = os.environ.get('DEXT') == '1'  # drift arc-latitude profile extended to 20-40 S (181a5fa)
if V32:
    V31 = True
EWC = json.load(open(X / 'settling/run-j-supplement/a1-stratified/eof-convention-weights.json')) if V32 else None
T = {}
for s in STRATA + ['run-j-both-burst-waypoints'] + (['run-j-a1branch-waypoints'] if V31 else []) + (['supp-ruleB', 'supp-a1strat'] if V32 else []):
    z = np.load(W / f'{s}.npz'); T[s] = {k: z[k] for k in z.files}; T[s]['products'] = json.loads(str(T[s]['products'])); T[s]['chk'] = json.loads(str(T[s]['chk']))
    print('loaded', s, flush=True)
OPTION = {p['D']: p['option'] for p in T['run-j-waypoints']['products']}
if DEXT:   # recompute the drift columns of every table on the 20-40 S profile (impact point, as before)
    _DX = C.DriftExt(ruled=os.environ.get('RULED') == '1'); C.OPTS_USED = _DX.opts
    for s_, t_ in T.items():
        dl_ = _DX.lnL(t_['ilat'], t_['ilon'])
        for (o_, m_), arr in ((k, v) for k, v in dl_.items() if k != 'inside_dedicated_span'):
            t_[f'drift|{o_}|{m_}'] = arr
        t_['drift_inside'] = dl_['inside_dedicated_span']
    print('drift recomputed on the 20-40 S profile', flush=True)
if V32:    # arc position from the IMPACT point for every table (the reduced supplement table has no 00:19:29 crossing)
    for s_, t_ in T.items():
        t_['sarc'] = V.arc_s(t_['ilat'], t_['ilon'])
    RED = np.load(X / 'end-of-flight/run-j-supplement/reduced/impacts-ruleB.npz')
    _rl, _rf = RED['latitude_deg'], RED['family4_code']
    FRESTN = {}
    for d_ in ('D3', 'D4', 'D5'):
        lw = RED[f'lnw:comb/{d_}'].astype(np.float64); w_ = np.exp(lw - np.nanmax(lw)); w_ = np.where(np.isfinite(w_), w_, 0.0); nA = _rf != 1
        FRESTN[d_] = float(w_[nA & (_rl > -33)].sum() / w_[nA].sum())
    del RED, _rl, _rf
    print('rest-north shares (non-A1, impact north of 33 S, reduced table):', FRESTN, flush=True)

# ---------------- products: name -> (drift option or None, ocean 'J'|'G'|'C', Pleiades?, searched variant or None)
SV = {'S': 'V1_central', 'S_V0': 'V0_scalar', 'S_V2': 'V2_pessimistic', 'S_V3': 'V3_optimistic', 'S_r0': 'V1_rho0',
      'S_r5': 'V1_rho0.25', 'S_r10': 'V1_rho0.5', 'S_rflat': 'V1_rho_flat', 'S_lpdter': 'V1_lpd_terrain', 'S_oiu': 'V1_oi_uniform',
      'S_nooi': 'V1_without_oi'}
SFV = {'V1_central': 'V1_central', 'V0_scalar': 'V0_scalar', 'V2_pessimistic': 'V2_pessimistic', 'V3_optimistic': 'V1_central',
       'V1_rho0': 'V1_central', 'V1_rho0.25': 'V1_central', 'V1_rho0.5': 'V1_central', 'V1_rho_flat': 'V1_central',
       'V1_lpd_terrain': 'V1_central', 'V1_oi_uniform': 'V1_oi_uniform', 'V1_without_oi': 'V1_without_oi'}
PR = {'core': (None, 'J', False, None), 'D': ('off', 'J', False, None), 'P': (None, 'J', True, None),
      'DP': ('off', 'J', True, None), 'D100': ('h100', 'J', False, None), 'DG': ('off', 'G', False, None), 'DC': ('off', 'C', False, None)}
for nm, v in SV.items():
    PR[nm] = (None, 'J', False, v); PR['D' + nm] = ('off', 'J', False, v)
PR['SP'] = (None, 'J', True, 'V1_central'); PR['DSP'] = ('off', 'J', True, 'V1_central')
PR['D100S'] = ('h100', 'J', False, 'V1_central'); PR['DGS'] = ('off', 'G', False, 'V1_central'); PR['DCS'] = ('off', 'C', False, 'V1_central')
for a in ('B', 'C', 'pop'):
    PR['A' + a] = (a, 'J', False, None); PR['A' + a + 'S'] = (a, 'J', False, 'V1_central')
PR['ABSP'] = ('B', 'J', True, 'V1_central'); PR['ABP'] = ('B', 'J', True, None)
if os.environ.get('RULED') == '1':   # Pete's 17 Oct Australian scheme, RECONSTRUCTED (gate failed), levels 0.3 / 0.5 / 0.65
    for a in ('r03', 'r05', 'r065'):
        PR['A' + a] = (a, 'J', False, None); PR['A' + a + 'S'] = (a, 'J', False, 'V1_central')
UPR = {'U': (None, None, None), 'UD': ('off', False, None), 'US': (None, False, 'V1_central'), 'UP': (None, True, None),
       'UAB': ('B', False, None), 'US_V0': (None, False, 'V0_scalar'), 'US_r0': (None, False, 'V1_rho0'), 'US_r10': (None, False, 'V1_rho0.5'),
       'US_V2': (None, False, 'V2_pessimistic'), 'US_V3': (None, False, 'V3_optimistic')}
AE = {'D': 'UD', 'S': 'US', 'P': 'UP', 'AB': 'UAB', 'S_V0': 'US_V0', 'S_r0': 'US_r0', 'S_r10': 'US_r10', 'S_V2': 'US_V2', 'S_V3': 'US_V3'}
KLP = [('D', 'core'), ('S', 'core'), ('P', 'core'), ('AB', 'core'), ('DS', 'core'), ('DS', 'S'), ('DS', 'D'), ('DSP', 'core'), ('DSP', 'DS'),
       ('DSP', 'SP'), ('DSP', 'DP'), ('ABS', 'core'), ('ABS', 'S'), ('ABS', 'AB'), ('ABSP', 'core'), ('ABSP', 'ABS'), ('ABSP', 'SP'), ('ABSP', 'ABP')] + \
      [('D' + nm, 'core') for nm in SV] + [('D' + nm, nm) for nm in SV] + [('D' + nm, 'D') for nm in SV] + [(nm, 'core') for nm in SV]
LOO = {('D', 'DS'): 'S', ('S', 'DS'): 'D', ('D', 'DSP'): 'SP', ('S', 'DSP'): 'DP', ('P', 'DSP'): 'DS',
       ('AB', 'ABS'): 'S', ('S', 'ABS'): 'AB', ('AB', 'ABSP'): 'SP', ('S', 'ABSP'): 'ABP', ('P', 'ABSP'): 'ABS'}
for nm in SV:
    if nm != 'S':
        LOO[(nm, 'D' + nm)] = 'D'; LOO[('D', 'D' + nm)] = nm
BOOTP = ['core', 'D', 'S', 'P', 'AB', 'DS', 'DSP', 'ABS', 'ABSP', 'DP', 'SP'] + ['D' + nm for nm in SV if nm != 'S'] + [nm for nm in SV if nm != 'S'] + \
        ['D100S', 'DGS', 'DCS', 'ACS', 'ApopS'] + (['Ar03S', 'Ar05S', 'Ar065S'] if os.environ.get('RULED') == '1' else [])


def next_area_mask(lat, lon):
    from matplotlib.path import Path as MPath
    g = C.PROJ.parent / 'Sept 27 2026 backup PL ChatGPT instance/2026-09-28_codex_drift_and_search_update/combined_panel_versions/search_footprints.geojson'
    doc = json.loads(g.read_text()); f = next(f for f in doc['features'] if f['properties'].get('id') == 'oi2024_proposed_inboard_northwest')
    rings = f['geometry']['coordinates']; inside = np.zeros(len(lat), bool)
    box = (lat > -40) & (lat < -30) & (lon > 88) & (lon < 100); pts = np.column_stack([lon[box], lat[box]])
    ib = MPath(np.asarray(rings[0])).contains_points(pts)
    for hole in rings[1:]:
        ib &= ~MPath(np.asarray(hole)).contains_points(pts)
    inside[np.where(box)[0]] = ib
    return inside
for s in T:
    T[s]['nxt'] = next_area_mask(T[s]['slat'], T[s]['slon']).astype(float)


def folder(s, d, variant, f='all'):
    if V31 and variant == 'head' and s == 'run-j-waypoints' and d in A1D:
        return 'run-j-a1branch-waypoints' if f in ('all', 'A1') else 'run-j-waypoints'
    if s == 'run-j-waypoints' and d in ('D3', 'D4') and variant == 'head':
        return 'run-j-both-burst-waypoints'
    return s


def _prod(fs, d, f):
    q = [p for p in T[fs]['products'] if p['D'] == d and p['subset'] == f and p['N'] > 0]
    return q[0] if q else None


def _blk(fs, o, wsum, pi, p, extra=''):
    u, cnt = np.unique(o, return_counts=True)
    return {'s': 'run-j-waypoints', 'fs': fs, 'idx': u, 'w0': pi * wsum * cnt / cnt.sum(), 'N': p['N'], 'row_ess': p['row_ess_kish'], 'share': p['share_of_option'], 'part': extra}


def supp_blocks(d, f):
    """Waypoint routes from the run J northern supplement (rule B). Totals stratified by impact latitude: the 'north of 33 S' product
    (N 10,000) replaces the total product's northern outcomes, at its exact share. D3-D5: A1 by the two conditional strata at end of
    flight's share (eof-convention-weights.json); the rest (non-A1) split at 33 S with the exact reduced-table share."""
    pi = MIXW[f"{OPTION[d]} | total"]['run-j-waypoints']; R_, A_ = T['supp-ruleB'], T['supp-a1strat']
    if f == 'all':
        pn = _prod('supp-ruleB', d, 'north33'); on = R_[f"prod_{pn['j']}"]; sN = pn['share_of_option']
        assert (R_['ilat'][on] > -33).all()
        if d in ('D0', 'D1', 'D2'):
            pt = _prod('supp-ruleB', d, 'all'); ot = R_[f"prod_{pt['j']}"]; ot = ot[R_['ilat'][ot] <= -33]
            return [_blk('supp-ruleB', ot, 1 - sN, pi, pt, 'south'), _blk('supp-ruleB', on, sN, pi, pn, 'north33')]
        a1 = EWC[d]['A1_share_eof_convention']; fr = FRESTN[d]
        pt = _prod('supp-a1strat', d, 'all'); ot = A_[f"prod_{pt['j']}"]; st_ = A_['src'][ot]
        os_ = ot[st_ != 0]; orr = ot[(st_ == 0) & (A_['ilat'][ot] <= -33)]; onn = on[R_['fam'][on] != 0]
        return [_blk('supp-a1strat', os_, a1, pi, pt, 'A1 strata'), _blk('supp-a1strat', orr, (1 - a1) * (1 - fr), pi, pt, 'rest south'),
                _blk('supp-ruleB', onn, (1 - a1) * fr, pi, pn, 'rest north33')]
    if f == 'A1' and d in ('D3', 'D4', 'D5'):
        p = _prod('supp-a1strat', d, 'A1'); return [_blk('supp-a1strat', A_[f"prod_{p['j']}"], EWC[d]['A1_share_eof_convention'], pi, p, 'A1')]
    p = _prod('supp-ruleB', d, f); sh = p['share_of_option']
    if d in ('D3', 'D4', 'D5'):
        a1r = _prod('supp-ruleB', d, 'A1')['share_of_option']; sh = sh * (1 - EWC[d]['A1_share_eof_convention']) / (1 - a1r)
    b = _blk('supp-ruleB', R_[f"prod_{p['j']}"], sh, pi, p, f); b['share'] = sh
    return [b]


def base_sample(d, f, ctx, variant='head'):
    """Concatenated outcome sample: list of per-folder blocks with aggregated base weight per used outcome."""
    blocks = []
    strata = STRATA if ctx == 'mix' else [ctx]
    for s in strata:
        if V32 and variant == 'head' and s == 'run-j-waypoints':
            blocks += supp_blocks(d, f)
            continue
        fs = folder(s, d, variant, f); t = T[fs]
        pj = [p for p in t['products'] if p['D'] == d and p['subset'] == f]
        if not pj:
            continue
        p = pj[0]; o = t[f"prod_{p['j']}"]
        sh = p['share_of_option']
        if V31 and variant == 'head' and s == 'run-j-waypoints' and d in A1D and f in ('A2', 'B'):
            sh = P0[d][f'{f}_share_stratified']   # single measure: A2 / B shares of the stratified total (settling rja1_pass0.json)
        pi = MIXW[f"{p['option']} | total"][s] * (sh if f != 'all' else 1.0)
        u, cnt = np.unique(o, return_counts=True)
        blocks.append({'s': s, 'fs': fs, 'idx': u, 'w0': pi * cnt / p['N'], 'N': p['N'], 'row_ess': p['row_ess_kish'], 'share': sh})
    tot = sum(b['w0'].sum() for b in blocks)
    for b in blocks:
        b['w0'] = b['w0'] / tot
    return blocks


def factors(b, carry):
    """Per-outcome factor arrays for one block (relative scale), NaN carried at the base mean (per ocean model)."""
    t = T[b['fs']]; i = b['idx']; w0 = b['w0']; F = {}
    def car(a):
        ok = np.isfinite(a); bar = (w0[ok] * a[ok]).sum() / w0[ok].sum() if ok.any() else 1.0
        carry.setdefault('_', []).append(float(w0[~ok].sum())); return np.where(ok, a, bar), float(w0[~ok].sum())
    for o in getattr(C, 'OPTS_USED', C.OPTS):
        for m in 'GC':
            F[f'd|{o}|{m}'], carry[f'drift|{o}|{m}|{b["s"]}'] = car(np.exp(t[f'drift|{o}|{m}'][i] - C.LREF))
    for m in 'GC':
        F[f'p|{m}'], carry[f'pleiades|{m}|{b["s"]}'] = car(np.exp(t[f'ple|{m}'][i] - float(t['PREF'])))
    return F


def lam(F, b, spec):
    dv, oc, usep, sv = spec
    t = T[b['fs']]; i = b['idx']; n = len(i)
    if dv is None and not usep:
        L = np.ones(n)
    elif oc in ('G', 'C'):
        L = (F[f'd|{dv}|{oc}'] if dv else 1.0) * (F[f'p|{oc}'] if usep else 1.0) * np.ones(n)
    else:
        dG = F[f'd|{dv}|G'] if dv else 1.0; dC = F[f'd|{dv}|C'] if dv else 1.0
        pG = F['p|G'] if usep else 1.0; pC = F['p|C'] if usep else 1.0
        L = 0.5 * (dG * pG + dC * pC) * np.ones(n)
    if sv is not None:
        L = L * t[f'P|{sv}'][i]
    return L


def _maps(b):
    if 'ks' not in b:
        t = T[b['fs']]; pos = np.full(len(t['seed']), -1, np.int64); pos[b['idx']] = np.arange(len(b['idx']))
        k = pos[t['sub_o']]; ok = k >= 0; b['ks'] = (k[ok], t['sub_b'][ok], t['sub_w'][ok])
        k = pos[t['cell_o']]; ok = k >= 0; b['kc'] = (k[ok], t['cell_b'][ok], t['cell_w'][ok])
        sd = t['seed'][b['idx']]; us = np.unique(sd); b['us'] = us; b['si'] = np.searchsorted(us, sd)
    return b


def hist_sub(b, w):
    k, bb, ww = _maps(b)['ks']
    return np.bincount(bb, w[k] * ww, V.NSUB + 1)[:V.NSUB]


def hist_cell(b, w):
    k, bb, ww = _maps(b)['kc']
    return np.bincount(bb, w[k] * ww, V.NY * V.NX + 1)[:V.NY * V.NX]


def hist_sub_seed(b, w):
    k, bb, ww = _maps(b)['ks']; ns = len(b['us']); nb = V.NSUB + 1
    return np.bincount(b['si'][k] * nb + bb, w[k] * ww, ns * nb).reshape(ns, nb)[:, :V.NSUB]


def hist_cell_seed(b, w):
    k, bb, ww = _maps(b)['kc']; ns = len(b['us']); nb = V.NY * V.NX + 1
    return np.bincount(b['si'][k] * nb + bb, w[k] * ww, ns * nb).reshape(ns, nb)[:, :V.NY * V.NX]


def l01(S1):
    return np.bincount(V.SUB_L01, S1, len(V.L01_MID))
BAND_EDGES = np.arange(-50, -5, 1.0)
def bands(h01):
    return np.array([h01[(V.L01_MID >= a) & (V.L01_MID < a + 1)].sum() for a in BAND_EDGES[:-1]]) / h01.sum()


def prepare(d, f, ctx, variant='head', with_u=False):
    """All per-outcome weights for one (D, f, ctx): returns dict product -> list of per-block weight arrays."""
    blocks = base_sample(d, f, ctx, variant); carry = {}; Wt = {p: [] for p in PR}
    if with_u:
        for p in UPR:
            Wt[p] = []
    for b in blocks:
        F = factors(b, carry); b['F'] = F
        for p, spec in PR.items():
            Wt[p].append(b['w0'] * lam(F, b, spec))
    if with_u:   # arc-uniform base: r = u / q_hat per 10 NM bin of the crossing
        SB = np.zeros(V.NSB + 1)
        for b in blocks:
            b['sb'] = V.sbin_index(T[b['fs']]['sarc'][b['idx']]); SB += np.bincount(b['sb'], b['w0'], V.NSB + 1)
        q = SB[:V.NSB]; reach = SPAN & (q > 0); u = np.where(SPAN, U_ARC, 0.0); u = u / u.sum()
        r = np.r_[np.where(reach, u / np.where(reach, q, 1.0), 0.0), 0.0]; lost = float(u[SPAN & ~reach].sum())
        for b in blocks:
            mu = b['w0'] * r[b['sb']]; b['mu'] = mu
            for p, (dv, usep, sv) in UPR.items():
                if dv is None and not usep:
                    L = np.ones(len(mu))
                elif usep:
                    L = 0.5 * (b['F']['p|G'] + b['F']['p|C'])
                else:
                    L = 0.5 * (b['F'][f'd|{dv}|G'] + b['F'][f'd|{dv}|C'])
                if sv is not None:
                    L = L * T[b['fs']][f'P|{sv}'][b['idx']]
                Wt[p].append(mu * L)
        carry['arc_uniform_unreachable_share'] = lost
    return blocks, Wt, carry


def summarise(blocks, ws, sv='V1_central'):
    S1 = sum(hist_sub(b, w) for b, w in zip(blocks, ws)); MAP = sum(hist_cell(b, w) for b, w in zip(blocks, ws))
    h = l01(S1); tot = h.sum(); q = VL.quantiles(h, V.L01_EDGES)
    wall = np.concatenate(ws); ess = float(wall.sum() ** 2 / (wall ** 2).sum())
    north = np.concatenate([T[b['fs']]['slat'][b['idx']] > -33 for b in blocks]); wn = wall[north]
    sfk = SFV.get(sv, 'V1_central')
    sf = sum(float((w * T[b['fs']][f'SF|{sfk}'][b['idx']]).sum()) for b, w in zip(blocks, ws)) / wall.sum()
    nx = sum(float((w * T[b['fs']]['nxt'][b['idx']]).sum()) for b, w in zip(blocks, ws)) / wall.sum()
    sb = sum(np.bincount(V.sbin_index(T[b['fs']]['sarc'][b['idx']]), w, V.NSB + 1)[:V.NSB] for b, w in zip(blocks, ws))
    c = np.concatenate([[0], np.cumsum(sb)]) / sb.sum(); med_nm = float(np.interp(0.5, c, np.arange(V.NSB + 1) * V.SBIN_NM))
    out = {'q05': q[0], 'median': q[1], 'q95': q[2], 'mean': float((h * V.L01_MID).sum() / tot), 'median_arc_nm': med_nm,
           'kish_ess': ess, 'n_outcomes_distinct': int(len(wall)), 'north_of_33S': float(h[V.L01_MID > -33].sum() / tot),
           'kish_ess_north_of_33S': float(wn.sum() ** 2 / (wn ** 2).sum()) if wn.sum() > 0 else 0.0,
           'p_on_searched_ground': sf, 'p_in_next_oi_area_not_evidence': nx, 'bands_1deg': bands(h).tolist(), 'modes': VL.modes_1d(h, V.L01_MID)}
    for lv in (0.5, 0.9, 0.95, 0.99):
        out[f'hpd{int(lv * 100)}_km2'] = float(VL.hpd_mask(MAP, lv).sum() * V.CELL_KM2)
    ek = {}
    for lo in range(-50, -5, 5):
        selb = np.concatenate([(T[b['fs']]['slat'][b['idx']] >= lo) & (T[b['fs']]['slat'][b['idx']] < lo + 5) for b in blocks]); a = wall[selb]
        ek[str(lo)] = float(a.sum() ** 2 / (a ** 2).sum()) if a.sum() > 0 else 0.0
    out['kish_ess_by_5deg'] = ek
    out['stratum_share'] = {}
    for b, w in zip(blocks, ws):
        out['stratum_share'][b['s']] = out['stratum_share'].get(b['s'], 0.0) + float(w.sum() / wall.sum())
    fam = np.concatenate([T[b['fs']]['fam'][b['idx']] for b in blocks])
    out['family_share'] = {fn: float(wall[fam == k].sum() / wall.sum()) for k, fn in enumerate(['A1', 'A2', 'B'])}
    return out, S1, MAP


def kl(blocks, wp, wq):
    a = np.concatenate(wp); c = np.concatenate(wq); Zp, Zq = a.sum(), c.sum(); ok = a > 0
    return float(np.sum(a[ok] * np.log((a[ok] / Zp) / (c[ok] / Zq))) / Zp)


def boot(blocks, Wt, prods, d, f):
    """Seed bootstrap within each stratum folder: per-seed sums, then NB draws of seed multiplicities."""
    keys = []
    for bi, b in enumerate(blocks):
        _maps(b); keys.append((bi, b['us'], b['si']))
    nseed = sum(len(us) for _, us, _ in keys); off = np.cumsum([0] + [len(us) for _, us, _ in keys])
    # bootstrap units = (stratum, seed key); the same unit gets the same multiplicity in every block; resampled within its group
    units = sorted({(blocks[bi]['s'], int(k)) for bi, us, _ in keys for k in us})
    gdiv = 10000 if V32 else 100
    groups = {}
    for i, (s_, k) in enumerate(units):
        groups.setdefault((s_, k // gdiv), []).append(i)
    MU = np.zeros((NB, len(units)))
    for k in range(NB):
        for g, ix in groups.items():
            MU[k, ix] = np.bincount(rng.integers(0, len(ix), len(ix)), minlength=len(ix))
    uidx = {u: i for i, u in enumerate(units)}
    M = np.zeros((NB, nseed))
    for (bi, us, _), o0 in zip(keys, off[:-1]):
        M[:, o0:o0 + len(us)] = MU[:, [uidx[(blocks[bi]['s'], int(k))] for k in us]]
    per = {}
    for p in set(prods) | {'core', 'S', 'D', 'DS', 'DSP', 'SP', 'DP', 'ABS', 'AB'}:
        H = np.zeros((nseed, len(V.L01_MID))); MP = np.zeros((nseed, V.NY * V.NX)); SFs = np.zeros(nseed); Z = np.zeros(nseed)
        sv = PR[p][3] or 'V1_central'
        for (bi, us, si), o0 in zip(keys, off[:-1]):
            b = blocks[bi]; w = Wt[p][bi]; ns = len(us)
            Hs = hist_sub_seed(b, w); H[o0:o0 + ns] = np.stack([l01(h) for h in Hs]); MP[o0:o0 + ns] = hist_cell_seed(b, w)
            SFs[o0:o0 + ns] = np.bincount(si, w * T[b['fs']][f'SF|{SFV[sv]}'][b['idx']], ns); Z[o0:o0 + ns] = np.bincount(si, w, ns)
        per[p] = (H, MP, SFs, Z)
    # per-seed sums for KL: sum w_p ln(Lp/Lq) by seed
    klp = [(a, c) for a, c in KLP if a in per and c in per] + [(a, c) for (_, a), c in LOO.items() if a in per and c in per]
    KS = {}
    for a, c in set(klp):
        v = np.zeros(nseed)
        for (bi, us, si), o0 in zip(keys, off[:-1]):
            wa, wc = Wt[a][bi], Wt[c][bi]; ok = wa > 0; t_ = np.zeros(len(wa)); t_[ok] = wa[ok] * np.log(wa[ok] / wc[ok])
            v[o0:o0 + len(us)] = np.bincount(si, t_, len(us))
        KS[(a, c)] = v
    res = {}
    for p in prods:
        H, MP, SFs, Z = per[p]; Hb = M @ H; MPb = M @ MP; Zb = M @ Z
        med = [VL.quantiles(h, V.L01_EDGES, (0.5,))[0] for h in Hb]; n33 = Hb[:, V.L01_MID > -33].sum(1) / Hb.sum(1)
        a90 = [VL.hpd_mask(m, 0.9).sum() * V.CELL_KM2 for m in MPb]; a50 = [VL.hpd_mask(m, 0.5).sum() * V.CELL_KM2 for m in MPb]
        a95 = [VL.hpd_mask(m, 0.95).sum() * V.CELL_KM2 for m in MPb]
        sg = (M @ SFs) / Zb; bd = np.array([bands(h) for h in Hb])
        res[p] = {'median_se': float(np.std(med)), 'north33_se': float(np.std(n33)), 'hpd50_se': float(np.std(a50)), 'hpd90_se': float(np.std(a90)),
                  'hpd95_se': float(np.std(a95)), 'searched_se': float(np.std(sg)), 'band_se': bd.std(0).tolist(),
                  'median_q': np.percentile(med, [2.5, 97.5]).tolist(), 'north33_q': np.percentile(n33, [2.5, 97.5]).tolist(),
                  'hpd90_q': np.percentile(a90, [2.5, 97.5]).tolist(), 'searched_q': np.percentile(sg, [2.5, 97.5]).tolist()}
        p_ = float(H.sum(0)[V.L01_MID > -33].sum() / H.sum()); se = res[p]['north33_se']
        res[p]['implied_n_north_of_33S'] = float(p_ * (1 - p_) / se ** 2) if se > 0 else None
    kres = {}
    for (a, c), v in KS.items():
        Za, Zc = per[a][3], per[c][3]
        vals = (M @ v) / (M @ Za) - np.log((M @ Za) / (M @ Zc))
        kres[f'{a}|{c}'] = {'se': float(np.std(vals)), 'q': np.percentile(vals, [2.5, 97.5]).tolist()}
    return res, kres


RES = {'meta': {'checks': {s: T[s]['chk'] for s in T}, 'NB': NB, 'products': {k: list(v) for k, v in PR.items()}, 'uproducts': {k: list(v) for k, v in UPR.items()}}, 'cells': {}}
PDF = {}; MAPS = {}
t0 = time.time()
jobs = [('head', d, f, ctx) for d in DK for f in FAMS for ctx in (['mix'] + STRATA if f == 'all' else ['mix'])] + \
       [('prodonly', d, 'all', 'mix') for d in ('D3', 'D4')] + [('prodonly', 'D3', 'A1', 'mix')]
import os
if os.environ.get('ONLY'):
    jobs = [j for j in jobs if j[1] == os.environ['ONLY']]
for variant, d, f, ctx in jobs:
    with_u = (ctx == 'mix' and f == 'all' and variant == 'head')
    blocks, Wt, carry = prepare(d, f, ctx, variant, with_u)
    if not blocks:
        continue
    Cc = {'blocks': [{k: b[k] for k in ('s', 'fs', 'N', 'row_ess', 'share')} for b in blocks],
          'not_computed_share': {k: v for k, v in carry.items() if k != '_'}}
    Zc = sum(w.sum() for w in Wt['core'])
    for p in PR:
        s_, S1, MAP = summarise(blocks, Wt[p], PR[p][3] or 'V1_central'); s_['lnE_given_core'] = float(np.log(sum(w.sum() for w in Wt[p]) / Zc))
        Cc[p] = s_
        if ctx == 'mix' and variant == 'head':
            PDF[f'{d}|{f}|{p}'] = l01(S1)
            if f == 'all' and p in ('core', 'D', 'S', 'P', 'DS', 'DSP', 'ABS', 'AB', 'DS_r0', 'DS_r10', 'DS_V2', 'DS_V3', 'DS_V0', 'ApopS', 'ACS', 'Ar03S', 'Ar05S', 'Ar065S'):
                MAPS[f'{d}|{p}'] = MAP.astype(np.float32)
        if ctx in ('run-j-waypoints', 'run-j-free') and p in ('core', 'DS', 'DSP', 'S', 'D'):
            PDF[f'{d}|{ctx}|{p}'] = l01(S1); MAPS[f'{d}|{ctx}|{p}'] = MAP.astype(np.float32)
        Cc[p]['_MAP'] = MAP
    Cc['KL'] = {f'{a}|{c}': kl(blocks, Wt[a], Wt[c]) for a, c in KLP}
    for (E, allp), loo in LOO.items():
        x = {'leave_out_product': loo, 'lnE_E_given_others': float(np.log(sum(w.sum() for w in Wt[allp]) / sum(w.sum() for w in Wt[loo]))),
             'KL_all_vs_loo': kl(blocks, Wt[allp], Wt[loo]), 'KL_all_vs_core': kl(blocks, Wt[allp], Wt['core']),
             'median_shift_on_removal_deg': Cc[loo]['median'] - Cc[allp]['median'], 'median_shift_on_removal_nm': Cc[loo]['median_arc_nm'] - Cc[allp]['median_arc_nm'],
             'hpd90_change_on_removal_km2': Cc[loo]['hpd90_km2'] - Cc[allp]['hpd90_km2'],
             'bhattacharyya': VL.bhattacharyya(Cc[allp]['_MAP'], Cc[loo]['_MAP']), **VL.overlap(Cc[allp]['_MAP'], Cc[loo]['_MAP'], 0.9)}
        x['KL_share_of_total'] = x['KL_all_vs_loo'] / x['KL_all_vs_core'] if x['KL_all_vs_core'] > 0 else None
        x['flag_KL_gt_half'] = bool(x['KL_share_of_total'] is not None and x['KL_share_of_total'] > 0.5)
        Cc.setdefault('loo', {})[f'{E}|{allp}'] = x
    if with_u:
        ZU = sum(w.sum() for w in Wt['U'])
        for E, up in AE.items():
            s_, S1, MAP = summarise(blocks, Wt[up], UPR[up][2] or 'V1_central'); s_['lnE_uniform'] = float(np.log(sum(w.sum() for w in Wt[up]) / ZU))
            s_['lnER_core_vs_uniform'] = Cc[E]['lnE_given_core'] - s_['lnE_uniform']
            s_['vs_core'] = {**VL.overlap(Cc['core']['_MAP'], MAP, 0.9), 'bhattacharyya': VL.bhattacharyya(Cc['core']['_MAP'], MAP),
                             'median_shift_deg': s_['median'] - Cc['core']['median'], 'median_shift_nm': s_['median_arc_nm'] - Cc['core']['median_arc_nm']}
            s_['arc_uniform_unreachable_share'] = carry['arc_uniform_unreachable_share']
            Cc['a_' + E] = s_; PDF[f'{d}|a_{E}'] = l01(S1)
            if E in ('D', 'S', 'P', 'AB'):
                MAPS[f'{d}|a_{E}'] = MAP.astype(np.float32)
        su, S1, _ = summarise(blocks, Wt['U']); Cc['a_uniform_base'] = su; PDF[f'{d}|a_uniform'] = l01(S1)
    if variant == 'head' and ctx == 'mix':
        bp = BOOTP if f == 'all' else ['core', 'DS', 'DSP', 'S', 'D', 'ABS']
        Cc['boot'], Cc['boot_KL'] = boot(blocks, Wt, bp, d, f)
    for p in PR:
        Cc[p].pop('_MAP', None)
    RES['cells'][f'{variant}|{d}|{f}|{ctx}'] = Cc
    print(f'{variant} {d} {f} {ctx} done {time.time() - t0:.0f}s', flush=True)

np.savez_compressed(OUT / 'pdf01-v3.npz', mids=V.L01_MID, **PDF)
np.savez_compressed(OUT / 'maps-v3.npz', NY=V.NY, NX=V.NX, **MAPS)
def clean(o):
    if isinstance(o, dict):
        return {str(k): clean(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [clean(v) for v in o]
    if isinstance(o, (np.floating, float)):
        return None if not np.isfinite(o) else float(o)
    if isinstance(o, (np.integer,)):
        return int(o)
    if isinstance(o, np.bool_):
        return bool(o)
    if isinstance(o, np.ndarray):
        return clean(o.tolist())
    return o
json.dump(clean(RES), open(OUT / 'views-v3-run-j.json', 'w'))
print('WROTE', OUT, time.time() - t0)
