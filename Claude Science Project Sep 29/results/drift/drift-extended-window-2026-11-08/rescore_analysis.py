"""Analysis of the offline rescoring of the extended-window drift run (arrivals.bin -> lib.rs rescore).
Variants: R1 old window (to 30 Jun 2016), R4 four detection periods, R2 all western Indian Ocean coasts, R3 all coasts and four periods.
Identity-weighted mixture: term_j = p_j q_j/Q_c + (1 - p_j) b_j(d), b_j(d) = core-prior average of q_j/Q_c (unrelated debris with
the prior-predictive place-time distribution). p_j = 1 reduces exactly to drift_coef.ln_l.
Usage: python rescore_analysis.py <rescore_dir with out/<variant>/<leg>.jsonl and cfg/<variant>-meta.json> <accumulators.npz> <ledger.npz> <audit.csv> <out_dir>"""
import sys, os, glob, json, numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import drift_coef as dc
RD, ACC, LED, AUD, OUT = sys.argv[1:6]; os.makedirs(OUT, exist_ok=True)
ZSEED = int(sys.argv[6]) if len(sys.argv) > 6 else 11; ZDRAWS = 2048; PACK = 'ext/extpack'
MODELS = ('globcurrent', 'glorys12')
AU = ['AU-north-east-city-inner', 'AU-south-city-inner', 'AU-wa-city-inner', 'AU-north-east-outer', 'AU-south-outer', 'AU-wa-outer',
      'AU-indian-ocean-territories-remote', 'AU-north-east-remote', 'AU-south-remote', 'AU-wa-remote']
POPULATED_WIO = ['WIO-mozambique-south-and-kzn-north', 'WIO-eastern-cape', 'WIO-western-cape']
GRADE_P = {'confirmed': 1.0, 'almost certain': 0.98, 'highly likely': 0.9, 'likely': 0.7}
aud = pd.read_csv(AUD).set_index('object_id')
def load(v):
    if v == 'R0-module-run':
        meta = dc.Meta(f'{PACK}/ext-globcurrent-1-coefficients-meta.json'); pat = f'{PACK}/' + '{}-{}-?-coefficients.jsonl'
        meta.finds = [dict(f, id='item:' + f['id'].split(':')[1]) for f in meta.finds]
    else:
        meta = dc.Meta(f'{RD}/cfg/{v}-meta.json'); pat = f'{RD}/out/{v}/' + '{}-{}-?.jsonl'
    meta.z = np.random.default_rng(ZSEED).standard_normal((ZDRAWS, meta.z.shape[1]))
    recs = {m: {} for m in MODELS}; nenv = {m: {} for m in MODELS}
    for m in MODELS:
        for f in sorted(glob.glob(pat.format('ext', m))):
            for nd in dc.read_nodes(f): recs[m][nd['node']] = nd
        for f in sorted(glob.glob(pat.format('ext2', m))):
            for nd in dc.read_nodes(f):
                for si, st in enumerate(nd['sets']):
                    for part in ('full', 'half_a', 'half_b'): recs[m][nd['node']]['sets'][si][part] = recs[m][nd['node']]['sets'][si][part] + st[part]
        for k in recs[m]: nenv[m][k] = len(recs[m][k]['sets'][0]['full'])
    return meta, recs, nenv
def mu_tiers(meta, moderate=np.log(0.3), au=None, populated=0.0):
    ov = {}
    for s in meta.seg:
        if s in AU: continue
        if s.startswith('WIO-'): ov[s] = [populated if s in POPULATED_WIO else moderate] * meta.np
    mu = meta.mu(ov)
    au = au or {s: -30.0 for s in AU}
    return meta.mu({**ov, **{s: [v] * meta.np for s, v in au.items()}})
def ruled_au(rho, outer=0.3):
    return {s: (np.log(rho) if 'city-inner' in s else (np.log(outer * rho) if 'outer' in s else -30.0)) for s in AU}
def terms(setd, part, meta, mu, sel):
    """log term array [env, draw, find] (NaN-free; -inf where q = 0)."""
    nu = np.exp(mu[None, :] + meta.sigma * meta.z); idx = {f['id']: (f['class'], f['segment'], jj) for c in range(meta.ncls) for jj, j in enumerate(meta.by_class[c]) for f in [meta.finds[j]]}
    T = np.full((len(setd[part]), nu.shape[0], len(sel)), -np.inf)
    for e, env in enumerate(setd[part]):
        for i, fid in enumerate(sel):
            c, sg, jj = idx[fid]; k = env[c]
            if k is None: continue
            q = nu[:, sg * meta.np:(sg + 1) * meta.np] @ np.asarray(k['a'][jj]); Q = nu @ np.asarray(k['A'])
            with np.errstate(divide='ignore'): T[e, :, i] = np.where((q > 0) & (Q > 0), np.log(np.maximum(q, 1e-300)) - np.log(np.maximum(Q, 1e-300)), -np.inf)
    return T
def lmean(x, axis=None):
    mx = np.max(x, axis=axis, keepdims=True); mx = np.where(np.isfinite(mx), mx, 0.0)
    with np.errstate(divide='ignore'): return np.squeeze(mx, axis=axis) + np.log(np.mean(np.exp(x - mx), axis=axis))
# ---- core posterior (run J), node weights for the background
A = np.load(ACC)
def core(key, lat, lon):
    H = A[key].astype(float); hl0, hn0, hg = float(A['lat0']), float(A['lon0']), float(A['grid'])
    hlat = hl0 + (np.arange(H.shape[0]) + 0.5) * hg; hlon = hn0 + (np.arange(H.shape[1]) + 0.5) * hg
    ii, jj = np.nonzero(H > 0); cl, cn, hw = hlat[ii], hlon[jj], H[ii, jj]
    dist = np.hypot((cn[:, None] - lon[None]) * 111.2 * np.cos(np.radians(cl[:, None])), (cl[:, None] - lat[None]) * 111.2)
    nn = np.argsort(dist, 1)[:, :6]; W = 1 / np.maximum(np.take_along_axis(dist, nn, 1), 1.0) ** 2; W /= W.sum(1, keepdims=True)
    p0 = hw / hw.sum(); wnode = np.zeros(len(lat)); np.add.at(wnode, nn.ravel(), (p0[:, None] * W).ravel())
    o = np.argsort(cl)
    def summ(p):
        q = lambda f: cl[o][np.searchsorted(np.cumsum(p[o]), f)]
        return dict(mean=(p * cl).sum(), median=q(0.5), p05=q(0.05), p95=q(0.95), N33=100 * p[cl >= -33].sum(), S38=100 * p[cl < -38].sum())
    base = summ(p0)
    def post(lnG, lnY):
        a = (W * lnG[nn]).sum(1); b = (W * lnY[nn]).sum(1); mx = max(np.nanmax(a), np.nanmax(b))
        p = p0 * 0.5 * (np.exp(a - mx) + np.exp(b - mx)); Z = p.sum(); p = p / Z; s = summ(p); s['shift'] = s['mean'] - base['mean']; return s
    return base, post, wnode / wnode.sum()
def score(meta, recs, nenv, common, mu, sel, pw, part='full', si=0, wnode=None):
    """ln L per node and model with identity weights pw (dict id -> p; missing = 1)."""
    p = np.array([pw.get(f, 1.0) for f in sel]); out = {}
    for m in MODELS:
        Ts = [terms(recs[m][k]['sets'][si], part, meta, mu, sel) for k in common]
        if np.all(p == 1.0):
            out[m] = np.array([lmean(T.sum(2).ravel()) for T in Ts]); continue
        # background b_j(d): core-prior average over nodes and environments of the term
        bj = np.zeros((meta.z.shape[0], len(sel)))
        for w, T in zip(wnode, Ts):
            with np.errstate(over='ignore'): bj += w * np.exp(T).mean(0)
        lb = np.log(np.maximum(bj, 1e-300))
        vals = []
        for T in Ts:
            mix = np.logaddexp(np.log(np.where(p > 0, p, 1e-300))[None, None, :] + T, np.log(np.maximum(1 - p, 1e-300))[None, None, :] + lb[None, :, :])
            mix = np.where(p[None, None, :] >= 1.0, T, mix)
            vals.append(lmean(mix.sum(2).ravel()))
        out[m] = np.array(vals)
    return out
rows = []; nodevals = {}
for v in ('R0-module-run', 'R1-oldwindow', 'R4-4periods', 'R2-allcoasts', 'R3-allcoasts-4periods'):
    meta, recs, nenv = load(v)
    common = sorted(set(recs['globcurrent']) & set(recs['glorys12'])); lat = np.array([recs['globcurrent'][k]['lat'] for k in common]); lon = np.array([recs['globcurrent'][k]['lon'] for k in common])
    base, post, wnode = core('H_D0_all', lat, lon)
    if not rows: rows.append(dict(variant='-', case='core only', **base, shift=0.0))
    ids = [f['id'] for f in meta.finds]; obj = {f: f.split(':')[1] if f.startswith('item:') else None for f in ids}
    NINE = [f for f in ids if f.startswith('item:') and aud.loc[obj[f], 'stringent_nine'] == 'yes']
    has = lambda o: f'item:{o}' in ids
    LL = ['item:linga-linga-vertical-stabilizer'] if has('linga-linga-vertical-stabilizer') else []
    NB = ['item:nautilus-bay-right-aileron'] if has('nautilus-bay-right-aileron') else []
    MP = ['item:mpame-right-flap-fairing'] if has('mpame-right-flap-fairing') else []
    CIRC = [f for f in ids if f.startswith('shadow:identity-from-drift')] + [f'item:{o}' for o in ('kosi-bay-right-wing-body-fairing', 'anvil-bay-wing-body-fairing', 'macaneta-left-trailing-edge-panel') if has(o)]
    grade = lambda f: aud.loc[obj[f] if obj[f] else f.split('identity-from-drift-')[-1], 'official_classification']
    PW = {f: GRADE_P[grade(f)] for f in NINE + LL + NB + MP + CIRC}
    swap = lambda sel, a, b: [b if x == a else x for x in sel]
    MB, FL, PA = 'item:mossel-bay-engine-cowling-roy', 'item:reunion-right-flaperon', 'item:paindane-right-flap-fairing'
    mu0 = mu_tiers(meta)
    cases = {'nine finds': (NINE, {}, mu0), 'nine finds and Linga Linga': (NINE + LL, {}, mu0) if LL else None,
             'nine finds and Linga Linga, Nautilus Bay, Mpame (all p = 1)': (NINE + LL + NB + MP, {}, mu0) if MP else None,
             'non-circular items, identity-weighted (headline candidate)': (NINE + LL + NB + MP, PW, mu0) if MP else None,
             'non-circular and drift-identified items, identity-weighted': (NINE + LL + NB + MP + CIRC, PW, mu0) if MP else None,
             'nine finds, Mossel Bay second beaching': (swap(NINE, MB, 'shadow:mossel-bay-refound-2016-03-21'), {}, mu0),
             'nine finds, three fresh marks (10 d, 10 d, 14 d)': (swap(swap(swap(NINE, FL, 'shadow:flaperon-fresh-10d'), MB, 'shadow:mossel-bay-fresh-10d'), PA, 'shadow:paindane-fresh-14d'), {}, mu0),
             'nine finds and Linga Linga, Australia ratio 0.25': (NINE + LL, {}, mu_tiers(meta, au=ruled_au(0.25))) if LL else None}
    if MP:
        H = NINE + LL + NB + MP
        cases['headline candidate, three fresh marks (10 d, 10 d, 14 d)'] = (swap(swap(swap(H, FL, 'shadow:flaperon-fresh-10d'), MB, 'shadow:mossel-bay-fresh-10d'), PA, 'shadow:paindane-fresh-14d'), PW, mu0)
        cases['headline candidate, other coasts at the find-coast level'] = (H, PW, mu_tiers(meta, moderate=0.0))
        cases['headline candidate, other coasts at 0.1'] = (H, PW, mu_tiers(meta, moderate=np.log(0.1)))
        cases['headline candidate, new coast segments switched off'] = (H, PW, mu_tiers(meta, moderate=-30.0, populated=-30.0)) if False else None
        cases['headline candidate, Australia ratio 0.25'] = (H, PW, mu_tiers(meta, au=ruled_au(0.25)))
        cases['headline candidate, all but Mossel Bay'] = ([x for x in H if x != MB], PW, mu0)
    for name, cdef in cases.items():
        if cdef is None: continue
        sel, pw, mu = cdef
        if not set(sel) <= set(ids): continue
        L = score(meta, recs, nenv, common, mu, sel, pw, wnode=wnode)
        s = post(L['globcurrent'], L['glorys12']); rows.append(dict(variant=v, case=name, n_items=len(sel), **s))
        for m in MODELS: rows.append(dict(variant=v, case=f'{name} [{m} only]', n_items=len(sel), **post(L[m], L[m])))
        nodevals[(v, name)] = L
    print(v, 'done', len(common), 'nodes')
PS = pd.DataFrame(rows); PS['level_draw_seed'] = ZSEED; PS.to_csv(f'{OUT}/rescore-posterior-summaries.csv', index=False)
pd.set_option('display.width', 250); print(PS[~PS.case.str.contains(r'\[')][['variant', 'case', 'n_items', 'mean', 'median', 'p95', 'shift', 'N33']].round(3).to_string(index=False))
pd.DataFrame({f'{v}|{n}|{m}': L[m] for (v, n), L in nodevals.items() for m in MODELS}).to_csv(f'{OUT}/rescore-node-values.csv', index=False)
