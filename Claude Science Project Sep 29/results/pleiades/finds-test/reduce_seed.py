"""Per-seed reduction of run J waypoints for the Pleiades x found-debris tests.
Weights: end of flight's option_table_0019.seed_terms UNCHANGED (only final reduction replaced, as compose_drift_runj.py).
Pleiades: joint-surface-rho0.25-gcrel (P + COSMO F1-F4, rho 0.25; [0]=GLORYS12, [1]=GlobCurrent product-relative), exact cell lookup,
cell convention of build_columns.py; not computed (non-finite) = zero likelihood (module convention).
Drift: bilinear-in-L lookup on run A rebuilt node surfaces, corners normalised over scored nodes (compose_drift_runj.corners).
Outputs per D key, per Pleiades weight p in {none, P_g12, P_gc}, per drift base model: node-contribution vector M, unscored sum U, total S,
and latitude-weighted versions. Usage: python reduce_seed.py SEED OUT.npz"""
import sys, os, json, math, pathlib, inspect, numpy as np, pandas as pd
sys.path.insert(0, 'scorer')
import displacement_hist as DH
DH.SATCOM_CSV = pathlib.Path('scorer/satcom-observations.csv').resolve()
import option_table_0019 as OT
OT.SATCOM_CSV = DH.SATCOM_CSV
src = inspect.getsource(OT.seed_terms); src = src[:src.index('    out = {}')] + '    return cells, f4, g\n'
ns = dict(OT.__dict__); exec(src, ns); seed_cells = ns['seed_terms']
X = pathlib.Path('/Users/pete/Downloads/mh370-exchange')
EOF_ = X / 'end-of-flight/run-j/run-j-waypoints'; CORE = X / 'core/run-j/run-j-waypoints'; DRIFT = X / 'debris-drift/run-j/run-j-waypoints'
REB = X / 'debris-drift/runA-rebuilt'; SURF = X / 'pleiades/run-i/surfaces'
KEYS = [f'D{d} total q=0.333 (C2 silent)' for d in range(6)]
G = dict(lat0=-41.166666666666664, lon0=83.96226004720266, dlat=0.5, dlon=0.5856322967993869, nlat=41, nlon=38); NC = G['nlat'] * G['nlon']
def state(model):
    df = pd.read_csv(REB / f'debris-drift-production-{model}/merged/nodes.csv'); st = np.zeros(NC, np.int8)
    st[df.node.values[np.isfinite(df.ln_l.values)]] = 1; return st
ST = {m: state(m) for m in ('glorys12', 'globcurrent')}
def corners(lat, lon):
    fi = (lat - G['lat0']) / G['dlat']; fj = (lon - G['lon0']) / G['dlon']
    inside = (fi >= 0) & (fj >= 0) & (fi <= G['nlat'] - 1) & (fj <= G['nlon'] - 1)
    i = np.minimum(np.floor(np.where(inside, fi, 0)).astype(int), G['nlat'] - 2); j = np.minimum(np.floor(np.where(inside, fj, 0)).astype(int), G['nlon'] - 2)
    ti, tj = fi - i, fj - j
    W = np.stack([(1 - ti) * (1 - tj), ti * (1 - tj), (1 - ti) * tj, ti * tj], 1)
    cid = i * G['nlon'] + j; nid = np.stack([cid, cid + G['nlon'], cid + 1, cid + G['nlon'] + 1], 1)
    return inside, nid, W
meta = {}
for line in (SURF / 'joint-surface-rho0.25-gcrel.toml').read_text().splitlines():
    k, v = line.split(' = ', 1); meta[k] = v
nl, nn = int(meta['nlat']), int(meta['nlon']); lat0, lon0, step = float(meta['lat0']), float(meta['lon0']), float(meta['step_deg'])
J = np.fromfile(SURF / 'joint-surface-rho0.25-gcrel.f32', '<f4').reshape(2, nl, nn).astype(float)
PREF = float(np.nanmax(np.where(np.isfinite(J), J, np.nan)))
k_ = int(sys.argv[1]); sd = EOF_ / f'seed-{k_}'
cells, f4, g = seed_cells(sd, CORE / 'bto-bfo' / f'seed-{k_}' / 'handoff-m0011' / 'handoff.npy')
lat, lon = g('latitude_deg'), g('longitude_deg'); n = len(lat)
A = np.load(DRIFT / f'seed-{k_}' / 'drift-lnL.npy', mmap_mode='r'); assert len(A) == n
inside, nid, W = corners(lat, lon)
WN, SC = {}, {}
for mod in ST:
    good = inside[:, None] & (ST[mod][nid] == 1) & (W > 0); Wg = np.where(good, W, 0.0); sw = Wg.sum(1)
    SC[mod] = sw > 0; WN[mod] = np.where(SC[mod][:, None], Wg / np.where(sw > 0, sw, 1)[:, None], 0.0)
    SC[mod + '_vs_export'] = int((SC[mod] != (np.asarray(A[f'state_{mod}_h50']) == 1)).sum())
pi = np.floor((lat - (lat0 - step / 2)) / step).astype(np.int64); pj = np.floor((lon - (lon0 - step / 2)) / step).astype(np.int64)
pin = (pi >= 0) & (pi < nl) & (pj >= 0) & (pj < nn)
LP = {}
for mi, name in ((0, 'P_g12'), (1, 'P_gc')):
    v = np.full(n, -np.inf); v[pin] = J[mi, pi[pin], pj[pin]]; v = np.where(np.isfinite(v), v, -np.inf); LP[name] = np.exp(v - PREF)
out = {'PREF': PREF, 'n_rows': n, 'p_outside': int((~pin).sum()), 'fam': f4.astype(np.int8)[:0]}
nidf = nid.ravel()
for key in KEYS:
    kk = key.split(' ')[0]; a = cells[key]; fin = np.isfinite(a); s = float(a[fin].max()); m = np.where(fin, np.exp(a - s), 0.0)
    out[f'{kk}|s'] = s
    for pname in ('none', 'P_g12', 'P_gc'):
        w = m if pname == 'none' else m * LP[pname]
        out[f'{kk}|{pname}|S'] = w.sum(); out[f'{kk}|{pname}|Slat'] = (w * lat).sum(); out[f'{kk}|{pname}|S2'] = (w * w).sum()
        out[f'{kk}|{pname}|fam'] = np.array([w[f4 == c].sum() for c in (1, 2, 3)])
        for mod in ST:
            mw = w[:, None] * WN[mod]
            out[f'{kk}|{pname}|{mod}|M'] = np.bincount(nidf, mw.ravel(), NC + G['nlon'] + 1)[:NC]
            out[f'{kk}|{pname}|{mod}|Mlat'] = np.bincount(nidf, (mw * lat[:, None]).ravel(), NC + G['nlon'] + 1)[:NC]
            out[f'{kk}|{pname}|{mod}|U'] = w[~SC[mod]].sum(); out[f'{kk}|{pname}|{mod}|Ulat'] = (w[~SC[mod]] * lat[~SC[mod]]).sum()
    # direct check against the drift export (finds only, core weights): ln sum m L_export with carry
    for mod in ST:
        lnL = np.asarray(A[f'lnL_{mod}_h50'], float); sc = np.asarray(A[f'state_{mod}_h50']) == 1
        L = np.where(sc, np.exp(np.where(sc, lnL, -125.0) + 125.0), 0.0); Lbar = (m * L).sum() / m[sc].sum()
        out[f'{kk}|check|{mod}'] = float((m * np.where(sc, L, Lbar)).sum())
out.update({f'sc_mismatch_{m}': SC[m + '_vs_export'] for m in ST})
np.savez(sys.argv[2], **out); print('seed', k_, 'rows', n, 'p_outside', out['p_outside'], 'sc mismatch', [SC[m + '_vs_export'] for m in ST], flush=True)
