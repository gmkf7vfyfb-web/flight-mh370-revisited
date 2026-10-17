"""Thinned-grid check (D0' = 'D0 total q=0.333 (C2 silent)'): rescore every run J waypoints impact on the run A surfaces thinned to
every other node in latitude and longitude (spacing 60 NM), with the scorer's own lookup, and compare the drift update with the
full-grid one. Writes compose-thin.npz with per-seed logc, p0, lat0 and, per surface, q1, lat1, nc."""
import sys, numpy as np, pandas as pd
sys.argv = [sys.argv[0], 'unused']
exec(open('compose_drift_runj.py').read().split("seeds = [int(x)")[0])          # imports, seed_cells, paths, G, NC
src = open('score_impacts.py').read(); ns = {}
exec("import numpy as np\nimport tomllib\nimport pandas as pd\n" + src[src.index("def lookup"):src.index("def wmedian")], ns); lookup = ns['lookup']
g2 = dict(lat0=G['lat0'], lon0=G['lon0'], dlat=2 * G['dlat'], dlon=2 * G['dlon'], nlat=21, nlon=19)
def thin_surface(model):
    df = pd.read_csv(REB / f'debris-drift-production-{model}/merged/nodes.csv'); i, j = df.node // G['nlon'], df.node % G['nlon']
    keep = (i % 2 == 0) & (j % 2 == 0); st = np.zeros(21 * 19, np.int8); v = np.full(21 * 19, np.nan)
    k2 = (i[keep] // 2) * 19 + (j[keep] // 2); ok = np.isfinite(df.ln_l[keep].values)
    st[k2.values] = np.where(ok, 1, 3); v[k2.values] = df.ln_l[keep].values; return st, v
TH = {m: thin_surface(m) for m in ('glorys12', 'globcurrent')}
seeds = sorted(int(p.name.split('-')[1]) for p in EOF.glob('seed-*') if p.is_dir()); K = len(seeds); key = 'D0 total q=0.333 (C2 silent)'
acc = {k: [] for k in ('logc', 'p0', 'lat0', 'g_q1', 'g_lat1', 'g_nc', 'c_q1', 'c_lat1', 'c_nc', 'm_q1', 'm_lat1', 'm_nc')}
for k_ in seeds:
    cells, f4, g = seed_cells(EOF / f'seed-{k_}', CORE / 'bto-bfo' / f'seed-{k_}' / 'handoff-m0011' / 'handoff.npy')
    lat, lon = g('latitude_deg'), g('longitude_deg'); a = cells[key]; fin = np.isfinite(a); s = float(a[fin].max()); m = np.where(fin, np.exp(a - s), 0.0)
    acc['logc'].append(np.log(1 / K) + s); acc['p0'].append(m.sum()); acc['lat0'].append((m * lat).sum())
    Ls = {}
    for tag, mod in (('g', 'glorys12'), ('c', 'globcurrent')):
        fl, ln = lookup(g2, 21, 19, *TH[mod], lat, lon); Ls[tag] = (fl == 1, np.where(fl == 1, np.exp(np.where(fl == 1, ln, LREF) - LREF), 0.0))
    Ls['m'] = (Ls['g'][0] & Ls['c'][0], 0.5 * (Ls['g'][1] + Ls['c'][1]))
    for tag, (sc, L) in Ls.items():
        Lbar = (m * L)[sc].sum() / m[sc].sum(); w = m * np.where(sc, L, Lbar)
        acc[f'{tag}_q1'].append(w.sum()); acc[f'{tag}_lat1'].append((w * lat).sum()); acc[f'{tag}_nc'].append(m[~sc].sum())
    print(f'seed-{k_}', flush=True)
np.savez('compose-thin.npz', **{k: np.array(v) for k, v in acc.items()}); print('WROTE')
