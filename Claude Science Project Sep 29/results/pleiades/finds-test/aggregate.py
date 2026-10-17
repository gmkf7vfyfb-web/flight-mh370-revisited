"""Aggregate the per-seed reductions (reduce_seed.py) into the Pléiades x found-debris tests on run J waypoints.

Test 1 (field): ln R = ln L_drift(field) - ln E_flight[L_drift]; field = mean over the six rating-5 clusters (equal weights; count weights
as a sensitivity) of the drift likelihood, bilinear in L on the run A rebuilt node surfaces.
Test 2 (shared impact point): ln R = ln E[L_P L_D] + ln E[1] - ln E[L_P] - ln E[L_D], ocean model shared between P and D, marginalised once
(equal prior). Australian non-recovery: option B, A, C measured on the 15-160 E pilot tables; populated coasts only RECONSTRUCTED with the
drift module's law Delta = -k ln(1 + W/(c F)) refitted per model (as apply_australia.py); carried to all nodes by inverse-distance-squared
over the 8 nearest pilot nodes; applied as L' = L exp(Delta). Everything is linear in the node likelihoods, so no impact is rescored.
Uncertainty: seed bootstrap (500) and transport-noise replicates (200; node ln L ~ N(-s^2/2, s) per 1-degree band from the committed
split halves; pilot Delta ~ N(0, split-half SD)); numerator and denominator perturbed together.
Usage (from the folder holding seed-*.npz):  python aggregate.py REPO_DIR EXCHANGE_DIR OUT.csv OUT-summary.json
"""
import sys, io, json, subprocess, tomllib, numpy as np, pandas as pd
from scipy.optimize import least_squares
from scipy.special import logsumexp
REPO, X, OUTCSV, OUTJ = sys.argv[1:5]
RES = 'Claude Science Project Sep 29/results/'
show = lambda p: subprocess.run(['git', '-C', REPO, 'show', 'HEAD:' + RES + p], capture_output=True, text=True, check=True).stdout
G = dict(lat0=-41.166666666666664, lon0=83.96226004720266, dlat=0.5, dlon=0.5856322967993869, nlat=41, nlon=38)
NC = G['nlat'] * G['nlon']; NL = G['nlon']; LREF = -125.0; MODS = ['glorys12', 'globcurrent']; PM = {'glorys12': 'P_g12', 'globcurrent': 'P_gc'}
CL = pd.DataFrame({'c': ['PHR_1 1', 'PHR_3 10', 'PHR_3 7', 'PHR_4 26,27', 'PHR_4 18,19', 'PHR_4 2-6'],
                   'lat': [-35.2053, -34.5938, -34.5571, -34.5467, -34.5014, -34.4539], 'lon': [90.4580, 90.4934, 90.4563, 91.2982, 91.3061, 91.3568], 'n': [1, 1, 1, 2, 2, 5]})
WEQ = np.ones(6) / 6; WCT = CL.n.values / CL.n.sum()
def nodes_vec(model):
    df = pd.read_csv(f'{X}/debris-drift/runA-rebuilt/debris-drift-production-{model}/merged/nodes.csv'); v = np.full(NC, np.nan)
    ok = np.isfinite(df.ln_l.values); v[df.node.values[ok]] = df.ln_l.values[ok]; return v
LN = {m: nodes_vec(m) for m in MODS}; STn = {m: np.isfinite(LN[m]).astype(int) for m in MODS}
AUS = {m: pd.read_csv(io.StringIO(show(f'drift-runj-2026-10-17/australia-160E/aus160-{m}/nodes.csv'))) for m in MODS}
cfg = tomllib.loads(show('drift-runj-2026-10-17/australia-160E/aus160-globcurrent.toml'))['hypotheses']['debris-drift']
SEGS = [s['name'] for s in cfg['segments']]; CLS = ['flaperon', 'low_exposure_exterior', 'high_windage_interior']
lvl = {'B': {d['segment']: d['ln_mean_by_period'][0] for d in cfg['levels']['segment_ln_mean_by_period']}}
lvl['C'] = {d['segment']: d['ln_mean_by_period'][0] for d in next(a for a in cfg['levels']['alternatives'] if a['name'] == 'C')['segment_ln_mean_by_period']}
POP = [s for s in SEGS if s.endswith('city-inner')]
def deltas(df):
    p = {s: np.mean([df[f'p_{c}_{i}'] for c in CLS], 0) for i, s in enumerate(SEGS)}
    F = sum(p[s] for s in SEGS[:6]); W = {o: sum(np.exp(lvl[o][s]) * p[s] for s in SEGS[6:]) for o in lvl}
    Dm = {'B': df.ln_l - df.ln_l_lev_off, 'C': df.ln_l_lev_C - df.ln_l_lev_off, 'A': df.ln_l_lev_A - df.ln_l_lev_off}
    ok = np.isfinite(F) & (F > 0) & np.isfinite(Dm['B']) & np.isfinite(Dm['C'])
    fit = least_squares(lambda x: np.concatenate([(-x[0] * np.log1p(W[o] / (x[1] * F)) - Dm[o])[ok] for o in ('B', 'C')]), [3.5, 0.2], bounds=([0.01, 1e-4], [50, 50]))
    k, c = fit.x; Dpop = -k * np.log1p(sum(p[s] for s in POP) / (c * F))
    halfB = (df.ln_l_half_a - df.ln_l_lev_off_half_a) - (df.ln_l_half_b - df.ln_l_lev_off_half_b)
    return df.node.values.astype(int), {'B': np.asarray(Dm['B'], float), 'populated': np.asarray(Dpop, float), 'A': np.asarray(Dm['A'], float), 'C': np.asarray(Dm['C'], float)}, dict(k=float(k), c=float(c), sdB=float(np.nanstd(halfB) / 2))
def spread(pn, d):
    plat = G['lat0'] + (pn // NL) * G['dlat']; plon = G['lon0'] + (pn % NL) * G['dlon']
    alat = G['lat0'] + (np.arange(NC) // NL) * G['dlat']; alon = G['lon0'] + (np.arange(NC) % NL) * G['dlon']
    dx = (alon[:, None] - plon[None]) * 111.2 * np.cos(np.radians(alat[:, None])); dy = (alat[:, None] - plat[None]) * 111.2
    dist = np.hypot(dx, dy); ok = np.isfinite(d); dist[:, ~ok] = np.inf
    nn = np.argsort(dist, 1)[:, :8]; dd = np.take_along_axis(dist, nn, 1); w = 1 / np.maximum(dd, 1.0) ** 2
    out = (w * d[nn]).sum(1) / w.sum(1); ex = dd[:, 0] < 1e-6; out[ex] = d[nn[ex, 0]]; return out
PIL = {m: deltas(AUS[m]) for m in MODS}; DEL = {m: {o: spread(PIL[m][0], v) for o, v in PIL[m][1].items()} for m in MODS}
S = [dict(np.load(f'seed-{k}.npz')) for k in range(1, 25)]; K = len(S); Dk = [f'D{d}' for d in range(6)]
def Lnode(mod, opt='none', dln=None, ddel=None):
    v = LN[mod] + (0 if opt == 'none' else (DEL[mod][opt] if ddel is None else ddel)) + (0 if dln is None else dln)
    return np.where(np.isfinite(v), np.exp(v - LREF), 0.0)
def pooled(vals, D, idx=None):
    idx = range(K) if idx is None else idx
    return logsumexp([S[k][f'{D}|s'] + np.log(max(vals[k], 1e-300)) for k in idx])
def seed_sums(D, mod, L, p):
    out = []
    for z in S:
        Lbar = (z[f'{D}|none|{mod}|M'] @ L) / (z[f'{D}|none|S'] - z[f'{D}|none|{mod}|U'])
        out.append(z[f'{D}|{p}|{mod}|M'] @ L + z[f'{D}|{p}|{mod}|U'] * Lbar)
    return np.array(out)
tot = lambda D, p: np.array([z[f'{D}|{p}|S'] for z in S])
def field_L(mod, L, wts):
    fi = (CL.lat.values - G['lat0']) / G['dlat']; fj = (CL.lon.values - G['lon0']) / G['dlon']; i = np.floor(fi).astype(int); j = np.floor(fj).astype(int); ti, tj = fi - i, fj - j
    W = np.stack([(1 - ti) * (1 - tj), ti * (1 - tj), (1 - ti) * tj, ti * tj], 1); cid = i * NL + j; nid = np.stack([cid, cid + NL, cid + 1, cid + NL + 1], 1)
    Wg = np.where((STn[mod][nid] == 1) & (W > 0), W, 0); Wn = Wg / Wg.sum(1, keepdims=True)
    return float(np.sum(wts * (Wn * L[nid]).sum(1)))
def compute(D, opt, idx=None, dln=None, ddel=None, wts=WEQ):
    L = {m: Lnode(m, opt, None if dln is None else dln[m], None if ddel is None else ddel[m]) for m in MODS}
    l0 = pooled(tot(D, 'none'), D, idx)
    lnED = {m: pooled(seed_sums(D, m, L[m], 'none'), D, idx) - l0 for m in MODS}
    lnEP = {m: pooled(tot(D, PM[m]), D, idx) - l0 for m in MODS}
    lnEPD = {m: pooled(seed_sums(D, m, L[m], PM[m]), D, idx) - l0 for m in MODS}
    o = {f'lnR_B|{m}': lnEPD[m] - lnEP[m] - lnED[m] for m in MODS}
    jPD, jP, jD = (np.logaddexp(d['glorys12'], d['globcurrent']) for d in (lnEPD, lnEP, lnED))
    o['lnR_B|joint'] = jPD - jP - jD + np.log(2)
    fL = {m: field_L(m, L[m], wts) for m in MODS}
    o.update({f'lnR_A|{m}': np.log(fL[m]) - lnED[m] for m in MODS}); o['lnR_A|joint'] = np.log(0.5 * (fL['glorys12'] + fL['globcurrent'])) - (jD - np.log(2))
    o['lnE_core_LD|joint'] = jD - np.log(2) + LREF; o['lnE_H_LD|joint'] = jPD - jP + LREF; o['lnL_field|joint'] = np.log(0.5 * sum(fL.values())) + LREF
    return o
rel = pd.read_csv(io.StringIO(show('debris-drift-two-model-nodes-relwind.csv')))
sc_ = pd.concat([pd.read_csv(f'{X}/debris-drift/runA-standin/chunk-{k}/nodes.csv') for k in (2, 3)])
def band_sd(lat, a, b):
    d = pd.DataFrame({'band': np.floor(lat), 'd2': (a - b) ** 2}).dropna(); return d.groupby('band').d2.mean() ** 0.5 / 2
sd_g = band_sd(pd.concat([rel.lat_deg, sc_.lat_deg]), pd.concat([rel.ln_l_half_a, sc_.ln_l_half_a]), pd.concat([rel.ln_l_half_b, sc_.ln_l_half_b]))
sd_c = band_sd(rel.lat_deg, rel.ln_l_half_a_gc, rel.ln_l_half_b_gc)
nlat_node = G['lat0'] + (np.arange(NC) // NL) * G['dlat']; nlon_node = G['lon0'] + (np.arange(NC) % NL) * G['dlon']
def sd_nodes(s):
    keys = np.array(s.index); return np.array([s.loc[keys[np.argmin(np.abs(keys - x))]] for x in np.floor(nlat_node)])
SDN = {'glorys12': sd_nodes(sd_g), 'globcurrent': sd_nodes(sd_c)}
rng = np.random.default_rng(20261017)
KEYQ = ['lnR_A|joint', 'lnR_A|glorys12', 'lnR_A|globcurrent', 'lnR_B|joint', 'lnR_B|glorys12', 'lnR_B|globcurrent']
res = {}
for D in Dk:
    for o in ['none', 'B', 'populated']:
        b0 = compute(D, o); boot = [compute(D, o, idx=rng.integers(0, K, K)) for _ in range(500)]; reps = []
        for _ in range(200):
            dln = {m: rng.normal(-0.5 * SDN[m] ** 2, SDN[m]) for m in MODS}
            ddel = None if o == 'none' else {m: spread(PIL[m][0], PIL[m][1][o] + rng.normal(0, PIL[m][2]['sdB'], len(PIL[m][0]))) for m in MODS}
            reps.append(compute(D, o, dln=dln, ddel=ddel))
        for q in KEYQ:
            res[(D, o, q)] = dict(value=b0[q], seed_sd=np.std([b[q] for b in boot]), noise_sd=np.std([r[q] for r in reps]),
                                  noise_q025=np.quantile([r[q] for r in reps], 0.025), noise_q975=np.quantile([r[q] for r in reps], 0.975))
R = pd.DataFrame(res).T; R.index.names = ['D', 'australia', 'quantity']; R = R.reset_index(); R['total_sd'] = np.sqrt(R.seed_sd ** 2 + R.noise_sd ** 2)
R.to_csv(OUTCSV, index=False)
# summary: absolute terms, cluster-weight sensitivity, ocean weights, latitude-band percentile, law constants
summ = {'law_constants': {m: PIL[m][2] for m in MODS}, 'absolute_D0': {o: {k: v for k, v in compute('D0', o).items() if k.startswith('ln') and '|joint' in k and 'lnR' not in k} for o in ['none', 'B', 'populated', 'A', 'C']},
        'count_weight_lnR_A_joint_D0': {o: compute('D0', o, wts=WCT)['lnR_A|joint'] for o in ['none', 'B', 'populated']},
        'P_globcurrent_given_pleiades': {D: float(1 / (1 + np.exp((pooled(tot(D, 'P_g12'), D) - pooled(tot(D, 'P_gc'), D))))) for D in Dk}}
band = (nlat_node >= -36.0) & (nlat_node <= -34.0) & (nlon_node >= 87) & (nlon_node <= 97); summ['field_percentile_34_36S'] = {}
for o in ['none', 'populated']:
    Lm = 0.5 * (Lnode('glorys12', o) + Lnode('globcurrent', o)); ok = band & (Lm > 0); v = np.log(Lm[ok]) + LREF
    f = np.log(0.5 * sum(field_L(m, Lnode(m, o), WEQ) for m in MODS)) + LREF
    summ['field_percentile_34_36S'][o] = dict(n_nodes=int(ok.sum()), field=float(f), median=float(np.median(v)), percentile=float((v < f).mean() * 100))
json.dump(summ, open(OUTJ, 'w'), indent=1, default=float); print('WROTE', OUTCSV, OUTJ)
