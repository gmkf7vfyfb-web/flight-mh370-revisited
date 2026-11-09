"""Drift headline (R3, twelve identity-weighted items, ramp prior) against three cores, eight level-draw seeds of 16384:
 (a) the evidence-combined Run J accumulator used so far (H_D0_all, 99.87 % waypoint family),
 (b) final 7 Nov end-of-flight Davey model + fuel, D0 (log-on only, no 00:19 measurement)  <- ruled main configuration,
 (c) same, waypoint/airway family, D0.
Drift-alone 1-D curve: node likelihoods averaged over the on-arc and +/-50 NM points at each latitude (no tie-order dependence), then interpolated to ledger bins.
Core on ledger bins: impact latitudes binned to the nearest ledger bin. Combined shift: inverse-distance weighting of the six nearest release points (as before).
Usage: python df_core_seeds.py SEED"""
import sys, os, json, numpy as np, pandas as pd
from scipy import stats
SEED = int(sys.argv[1])
sys.argv = ['x', 'rescore/x', '/Users/pete/Downloads/mh370-exchange/end-of-flight/run-j/summary/run-j-maps-accumulators.npz', 'arcm.npz', 'audit.csv', 'res-dfcore']
exec(open('offline/rescore_analysis.py').read().split('rows = []; nodevals = {}')[0])
exec(open('offline/drift_alone_ramp.py').read().split('rows, curves = ')[0].split("exec(open('offline/rescore_analysis.py')")[1].split('\n', 1)[1])   # tension(), summ(), la, pi, pc
ZDRAWS, ZSEED = 16384, SEED
meta, recs, nenv = load('R3-allcoasts-4periods')
common = sorted(set(recs['globcurrent']) & set(recs['glorys12'])); lat = np.array([recs['globcurrent'][k]['lat'] for k in common]); lon = np.array([recs['globcurrent'][k]['lon'] for k in common])
ids = [f['id'] for f in meta.finds]
NINE = [f for f in ids if f.startswith('item:') and aud.loc[f.split(':')[1], 'stringent_nine'] == 'yes']
HI = NINE + [f'item:{o}' for o in ('linga-linga-vertical-stabilizer', 'nautilus-bay-right-aileron', 'mpame-right-flap-fairing') if f'item:{o}' in ids]
PW = {f: GRADE_P[aud.loc[f.split(':')[1], 'official_classification']] for f in HI}
base_ = '/Users/pete/Downloads/mh370-exchange/end-of-flight/final-2026-11-07/results'
def points(fam):
    Z = np.load(f'{base_}/eof-final-handoff-{fam}.npz'); lw = Z['log_weight_D0'].astype(float); w = np.exp(lw - np.nanmax(lw)); w = np.where(np.isfinite(w), w, 0)
    return Z['latitude_deg'].astype(float), Z['longitude_deg'].astype(float), w
RS = A['RS_D0']; CORES = {'evidence-combined Run J (used so far)': (RS[:, 1].astype(float), RS[:, 2].astype(float), RS[:, 0].astype(float)),
                          'Davey model + fuel (final end of flight, D0)': points('df'), 'waypoint/airway (final end of flight, D0)': points('wp')}
def idw(cl, cn, hw):
    m = hw > 0; cl, cn, hw = cl[m], cn[m], hw[m]; nn = np.empty((len(cl), 6), int); W = np.empty((len(cl), 6))
    for i in range(0, len(cl), 50000):
        a, b = cl[i:i + 50000], cn[i:i + 50000]
        dist = np.hypot((b[:, None] - lon[None]) * 111.2 * np.cos(np.radians(a[:, None])), (a[:, None] - lat[None]) * 111.2)
        k = np.argsort(dist, 1)[:, :6]; ww = 1 / np.maximum(np.take_along_axis(dist, k, 1), 1.0) ** 2; nn[i:i + 50000] = k; W[i:i + 50000] = ww / ww.sum(1, keepdims=True)
    p0 = hw / hw.sum(); wn = np.zeros(len(lat)); np.add.at(wn, nn.ravel(), (p0[:, None] * W).ravel()); return cl, p0, nn, W, wn / wn.sum()
o = np.argsort(la); edges = np.r_[-np.inf, 0.5 * (la[o][1:] + la[o][:-1]), np.inf]
ulat = np.unique(lat)
rows = []
for cname, (cl, cn, hw) in CORES.items():
    clx, p0, nn, W, wnode = idw(cl, cn, hw)
    L = score(meta, recs, nenv, common, mu_tiers(meta), HI, PW, wnode=wnode)
    mx = max(L['globcurrent'].max(), L['glorys12'].max()); Ln = 0.5 * (np.exp(L['globcurrent'] - mx) + np.exp(L['glorys12'] - mx))
    Lu = np.array([Ln[lat == u].mean() for u in ulat]); LB = np.interp(la, ulat, Lu, left=np.nan, right=np.nan); inside = np.isfinite(LB); LB = np.where(inside, LB, 0.0)
    h = np.zeros(len(la)); idx = np.searchsorted(edges, cl, side='right') - 1; np.add.at(h, o[np.clip(idx, 0, len(la) - 1)], hw / hw.sum())
    global pc; pc = h / h.sum()
    pd_ = pi * LB; pd_ /= pd_.sum(); t = tension(np.where(inside, LB, 1e-300))
    a = (W * L['globcurrent'][nn]).sum(1); b = (W * L['glorys12'][nn]).sum(1); m2 = max(a.max(), b.max()); pp = p0 * 0.5 * (np.exp(a - m2) + np.exp(b - m2)); pp /= pp.sum()
    corem = float((p0 * clx).sum()); postm = float((pp * clx).sum()); oo = np.argsort(clx); cc = np.cumsum(pp[oo]); med = float(clx[oo][np.searchsorted(cc, 0.5)])
    sd = summ(pd_)
    rows.append(dict(seed=SEED, core=cname, core_mean=corem, combined_mean=postm, combined_median=med, shift=postm - corem, combined_N33=100 * float(pp[clx >= -33].sum()),
                     drift_alone_median=sd['median'], drift_alone_mean=sd['mean'], drift_alone_N33=sd['N33'], **{k: t[k] for k in ('lnR', 'lnI', 'lnS', 'd', 'p', 'sigma')}))
    print(rows[-1], flush=True)
os.makedirs('res-dfcore', exist_ok=True); pd.DataFrame(rows).to_csv(f'res-dfcore/seed-{SEED}.csv', index=False)
