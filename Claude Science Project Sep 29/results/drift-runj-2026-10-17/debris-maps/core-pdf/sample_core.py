"""Draw release points from the run J waypoints core impact PDF (no drift): end of flight's cell 'D0 total q=1/3 (C2 silent)',
seeds pooled by evidence. Uses 8 of the 24 seeds (1-8) to save time; declared."""
import sys, pathlib, inspect, json, numpy as np
sys.path.insert(0, 'scorer')
import displacement_hist as DH; DH.SATCOM_CSV = pathlib.Path('scorer/satcom-observations.csv').resolve()
import option_table_0019 as OT; OT.SATCOM_CSV = DH.SATCOM_CSV
src = inspect.getsource(OT.seed_terms); src = src[:src.index('    out = {}')] + '    return cells, f4, g\n'
ns = dict(OT.__dict__); exec(src, ns); seed_cells = ns['seed_terms']
X = pathlib.Path('/Users/pete/Downloads/mh370-exchange'); EOF_ = X / 'end-of-flight/run-j/run-j-waypoints'; CORE = X / 'core/run-j/run-j-waypoints'
key = 'D0 total q=0.333 (C2 silent)'; L, LO, W = [], [], []
for k in range(1, 9):
    cells, f4, g = seed_cells(EOF_ / f'seed-{k}', CORE / 'bto-bfo' / f'seed-{k}' / 'handoff-m0011' / 'handoff.npy')
    a = cells[key]; fin = np.isfinite(a); s = a[fin].max(); w = np.where(fin, np.exp(a - s), 0.0)
    z = np.log(w.sum()) + s                       # seed evidence
    lat, lon = g('latitude_deg'), g('longitude_deg')
    idx = np.random.default_rng(k).choice(len(w), 4000, p=w / w.sum())   # within-seed weighted draws
    L.append(lat[idx]); LO.append(lon[idx]); W.append(np.full(4000, z))
L, LO, W = np.concatenate(L), np.concatenate(LO), np.concatenate(W)
pz = np.exp(W - W.max()); pz /= pz.sum()          # pool seeds by evidence
pick = np.random.default_rng(20261017).choice(len(L), 200, p=pz)
lat_s, lon_s = L[pick], LO[pick]
h, e = np.histogram(L, bins=np.arange(-41, -30, 0.1), weights=pz); i = np.argmax(h); mlat = 0.5 * (e[i] + e[i + 1])
near = np.abs(L - mlat) < 0.05; mlon = float(np.average(LO[near], weights=pz[near]))
json.dump({'mode': [mlon, mlat], 'samples': [[float(a), float(b)] for a, b in zip(lon_s, lat_s)],
           'sample_lat_q05_q50_q95': np.quantile(lat_s, [0.05, 0.5, 0.95]).tolist()}, open('core-release-points.json', 'w'))
print('mode', round(mlon, 3), round(mlat, 3), '| samples lat 5/50/95', np.round(np.quantile(lat_s, [0.05, 0.5, 0.95]), 2), 'lon range', np.round([lon_s.min(), lon_s.max()], 2))
