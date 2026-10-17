"""Drift-only composition of core run J / end-of-flight run J (stratum from env STRATUM, default waypoints; drift columns computed in memory by drift_columns_inmem when no stored drift-lnL.npy) with the run A drift surfaces (rebuilt).

Weights per impact are end of flight's own two-factor cells, built by option_table_0019.seed_terms UNCHANGED (its source is
exec'd with only the final reduction replaced by `return cells, f4, g`). Seeds pooled by evidence exactly as that script.
Drift factor: per-impact drift-lnL.npy (export_per_impact.py on the rebuilt surfaces). Rows the drift term did not compute
are carried at the seed's (cell, surface) weighted mean likelihood ratio and never excluded (ruling 15 Oct, composition-nan).
Accumulates per seed: prior/posterior sums, 0.01 deg latitude histograms, drift-grid cell masses, family shares, and the
linear node-contribution matrices used for transport-noise replicates (likelihood is linear in node values).
Usage: python compose_drift_runj.py OUT.npz
"""
import sys, json, pathlib, inspect, textwrap, numpy as np
sys.path.insert(0, 'scorer')
import displacement_hist as DH
DH.SATCOM_CSV = pathlib.Path('scorer/satcom-observations.csv').resolve()
import option_table_0019 as OT
OT.SATCOM_CSV = DH.SATCOM_CSV
from compact_impacts import load

src = inspect.getsource(OT.seed_terms)
src = src[:src.index('    out = {}')] + '    return cells, f4, g\n'
ns = dict(OT.__dict__); exec(src, ns); seed_cells = ns['seed_terms']

X = pathlib.Path('/Users/pete/Downloads/mh370-exchange')
import os; ST = os.environ.get('STRATUM', 'run-j-waypoints')
EOF = X / 'end-of-flight/run-j' / ST; CORE = X / 'core/run-j' / ST; DRIFT = X / 'debris-drift/run-j' / ST
sys.path.append(os.getcwd()); import drift_columns_inmem as DC
REB = X / 'debris-drift/runA-rebuilt'
KEYS = [f'D{d} total q=0.333 (C2 silent)' for d in range(6)]
SURF = [('glorys12', 'h50'), ('globcurrent', 'h50'), ('mean', 'h50'), ('mean', 'h25'), ('mean', 'h100'), ('mean', 'h200')]
LREF = -125.0
LAT = OT.LAT
G = dict(lat0=-41.166666666666664, lon0=83.96226004720266, dlat=0.5, dlon=0.5856322967993869, nlat=41, nlon=38)
NC = G['nlat'] * G['nlon']

import pandas as pd
def node_state(model):
    df = pd.read_csv(REB / f'debris-drift-production-{model}/merged/nodes.csv')
    st = np.zeros(NC, np.int8); v = np.full(NC, np.nan)
    ok = np.isfinite(df.ln_l.values); st[df.node.values[ok]] = 1; v[df.node.values[ok]] = df.ln_l.values[ok]
    return st, v
NODE = {m: node_state(m) for m in ('glorys12', 'globcurrent')}

def corners(lat, lon):
    fi = (lat - G['lat0']) / G['dlat']; fj = (lon - G['lon0']) / G['dlon']
    inside = (fi >= 0) & (fj >= 0) & (fi <= G['nlat'] - 1) & (fj <= G['nlon'] - 1)
    i = np.minimum(np.floor(np.where(inside, fi, 0)).astype(int), G['nlat'] - 2); j = np.minimum(np.floor(np.where(inside, fj, 0)).astype(int), G['nlon'] - 2)
    ti, tj = fi - i, fj - j
    W = np.stack([(1 - ti) * (1 - tj), ti * (1 - tj), (1 - ti) * tj, ti * tj], 1)
    cid = i * G['nlon'] + j; nid = np.stack([cid, cid + G['nlon'], cid + 1, cid + G['nlon'] + 1], 1)
    return inside, cid, nid, W

seeds = [int(x) for x in __import__("os").environ["SEEDS"].split(",")] if "SEEDS" in __import__("os").environ else sorted(int(p.name.split('-')[1]) for p in EOF.glob('seed-*') if p.is_dir())
K = len(seeds); out = {'seeds': np.array(seeds), 'LREF': LREF}
acc = {}
for k_ in seeds:
    sd = EOF / f'seed-{k_}'
    cells, f4, g = seed_cells(sd, CORE / 'bto-bfo' / f'seed-{k_}' / 'handoff-m0011' / 'handoff.npy')
    lat, lon = g('latitude_deg'), g('longitude_deg')
    A = np.load(DRIFT / f'seed-{k_}' / 'drift-lnL.npy') if (DRIFT / f'seed-{k_}' / 'drift-lnL.npy').exists() else DC.columns(lat, lon, g('parent'))[0]
    assert len(A) == len(lat)
    li = np.clip(np.searchsorted(LAT, lat), 0, len(LAT) - 1)
    inside, cid, nid, W = corners(lat, lon); cidx = np.where(inside, cid, NC)
    for key in KEYS:
        a = cells[key]; fin = np.isfinite(a); s = float(a[fin].max()); m = np.where(fin, np.exp(a - s), 0.0)
        r = {'logc': np.log(1.0 / K) + s, 'p0': m.sum(), 'p2': (m * m).sum(), 'hp': np.bincount(li, m, len(LAT)),
             'lat0': (m * lat).sum(), 'c0': np.bincount(cidx, m, NC + 1), 'fam0': np.array([m[f4 == c].sum() for c in (1, 2, 3)])}
        for (mod, bw) in SURF:
            col = f'lnL_{mod}_{bw}'; lnL = A[col].astype(float)
            sc = np.isfinite(lnL) if mod == 'mean' else (A[f'state_{mod}_{bw}'] == 1)
            L = np.where(sc, np.exp(np.where(sc, lnL, LREF) - LREF), 0.0)
            ssc = m[sc].sum(); Lbar = (m * L).sum() / ssc
            Lf = np.where(sc, L, Lbar); w = m * Lf
            t = f'{mod}_{bw}'
            r[t] = {'q1': w.sum(), 'q2': (w * w).sum(), 'nc': m[~sc].sum(), 'hq': np.bincount(li, w, len(LAT)), 'lat1': (w * lat).sum(),
                    'c1': np.bincount(cidx, w, NC + 1), 'fam1': np.array([w[f4 == c].sum() for c in (1, 2, 3)])}
            if mod != 'mean' and bw == 'h50':
                st = NODE[mod][0]; good = (st[nid] == 1) & (W > 0); Wg = np.where(good, W, 0.0); sw = Wg.sum(1)
                Wn = np.where(sc[:, None] & (sw[:, None] > 0), Wg / np.where(sw > 0, sw, 1)[:, None], 0.0)
                mw = m[:, None] * Wn
                r[t]['M'] = np.bincount(nid.ravel(), mw.ravel(), NC + G['nlon'] + 1)[:NC]
                r[t]['Mlat'] = np.bincount(nid.ravel(), (mw * lat[:, None]).ravel(), NC + G['nlon'] + 1)[:NC]
                r[t]['MC'] = np.bincount((cidx[:, None] * 4 + np.arange(4)).ravel(), mw.ravel(), (NC + 1) * 4)  # cell x corner
                r[t]['Ssc'] = ssc; r[t]['U'] = m[~sc].sum(); r[t]['Ulat'] = (m[~sc] * lat[~sc]).sum(); r[t]['Uc'] = np.bincount(cidx[~sc], m[~sc], NC + 1)
        acc.setdefault(key, []).append(r)
    print(f'seed-{k_} done', flush=True)

# flatten into npz
flat = {}
for key, rs in acc.items():
    kk = key.split(' ')[0]
    for f in ('logc', 'p0', 'p2', 'lat0'): flat[f'{kk}|{f}'] = np.array([r[f] for r in rs])
    for f in ('hp', 'c0', 'fam0'): flat[f'{kk}|{f}'] = np.stack([r[f] for r in rs])
    for (mod, bw) in SURF:
        t = f'{mod}_{bw}'
        for f in rs[0][t]:
            v = [r[t][f] for r in rs]
            flat[f'{kk}|{t}|{f}'] = np.stack(v) if np.ndim(v[0]) else np.array(v)
flat['seeds'] = np.array(seeds); flat['LAT'] = LAT
np.savez_compressed(sys.argv[1], **flat)
print('WROTE', sys.argv[1], len(flat), 'arrays')
