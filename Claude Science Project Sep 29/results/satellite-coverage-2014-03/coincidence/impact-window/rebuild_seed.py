"""Rebuild run J flight-posterior weights for one end-of-flight seed (recipe: option_table_0019.seed_terms exec'd unchanged
except its final reduction -> 'return cells, f4, g'), then draw M within-seed posterior samples per headline cell.
Usage: python rebuild_seed.py FAMILY SEED OUTDIR M"""
import sys, pathlib, inspect, json, numpy as np
HERE = pathlib.Path(__file__).resolve().parent; sys.path.insert(0, str(HERE))
import displacement_hist as DH
DH.SATCOM_CSV = (HERE / 'satcom-observations.csv').resolve()
import option_table_0019 as OT
OT.SATCOM_CSV = DH.SATCOM_CSV
src = inspect.getsource(OT.seed_terms); src = src[:src.index('    out = {}')] + '    return cells, f4, g\n'
ns = dict(OT.__dict__); exec(src, ns); seed_cells = ns['seed_terms']
fam, k, outd, M = sys.argv[1], int(sys.argv[2]), pathlib.Path(sys.argv[3]), int(sys.argv[4])
X = pathlib.Path('/Users/pete/Downloads/mh370-exchange')
sd = X / f'end-of-flight/run-j/{fam}/seed-{k}'
cells, f4, g = seed_cells(sd, X / f'core/run-j/{fam}/bto-bfo/seed-{k}/handoff-m0011/handoff.npy')
lat = g('latitude_deg'); lon = g('longitude_deg'); t = g('unix_s') - 1394236800.0; adn = g('arc_distance_nm')
tfo = g('latent:realised_flameout_unix_s') - 1394236800.0
KEYS = [f'D{d} total q=0.333 (C2 silent)' for d in (0, 1, 2, 3, 4, 5)]
rng = np.random.default_rng(1000 + k); res = {}; info = {'family': fam, 'seed': k, 'n_rows': int(len(lat))}
for key in KEYS:
    a = cells[key]; fin = np.isfinite(a); s = float(a[fin].max()); m = np.where(fin, np.exp(a - s), 0.0)
    S = m.sum(); lnZ = float(np.log(S) + s); ess = float(S ** 2 / (m * m).sum())
    idx = rng.choice(len(m), size=M, replace=True, p=m / S) if key.split()[0] in ('D0', 'D2', 'D4') else None
    kk = key.split()[0]; info[kk] = {'lnZ': lnZ, 'ess_rows': ess}
    if idx is not None:
        idx.sort(); res[f'{kk}_idx'] = idx.astype(np.int32)
# store only sampled rows (union) to keep disk small
U = np.unique(np.concatenate([res[f'{kk}_idx'] for kk in ('D0', 'D2', 'D4')]))
out = {'rows': U.astype(np.int32), 'lat': lat[U].astype(np.float64), 'lon': lon[U].astype(np.float64), 't': t[U].astype(np.float64),
       'adn': adn[U].astype(np.float32), 'tfo': tfo[U].astype(np.float32), 'f4': f4[U].astype(np.int8)}
for kk in ('D0', 'D2', 'D4'): out[f'{kk}_pos'] = np.searchsorted(U, res[f'{kk}_idx']).astype(np.int32)
np.savez(outd / f'{fam}-seed-{k}.npz', **out)
json.dump(info, open(outd / f'{fam}-seed-{k}.json', 'w'))
print(fam, k, {kk: round(info[kk]['lnZ'], 3) for kk in ('D0', 'D2', 'D4')}, flush=True)
