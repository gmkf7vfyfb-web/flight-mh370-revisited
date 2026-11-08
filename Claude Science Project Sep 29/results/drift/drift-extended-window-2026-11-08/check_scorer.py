import sys, os, glob, json, numpy as np, pandas as pd
sys.argv = ['x', 'rescore/x', '/Users/pete/Downloads/mh370-exchange/end-of-flight/run-j/summary/run-j-maps-accumulators.npz', 'arcm.npz', 'audit.csv', '/tmp/rs-check']
src = open('offline/rescore_analysis.py').read().split('rows = []; nodevals = {}')[0]
exec(src)
import drift_coef as dc
meta = dc.Meta('ext/extpack/ext-globcurrent-1-coefficients-meta.json'); recs = {m: {} for m in MODELS}
for m in MODELS:
    for f in sorted(glob.glob(f'ext/extpack/ext-{m}-?-coefficients.jsonl')):
        for nd in dc.read_nodes(f): recs[m][nd['node']] = nd
    for f in sorted(glob.glob(f'ext/extpack/ext2-{m}-?-coefficients.jsonl')):
        for nd in dc.read_nodes(f):
            for si, st in enumerate(nd['sets']):
                for part in ('full', 'half_a', 'half_b'): recs[m][nd['node']]['sets'][si][part] = recs[m][nd['node']]['sets'][si][part] + st[part]
common = sorted(set(recs['globcurrent']) & set(recs['glorys12'])); lat = np.array([recs['globcurrent'][k]['lat'] for k in common]); lon = np.array([recs['globcurrent'][k]['lon'] for k in common])
base, post, wnode = core('H_D0_all', lat, lon)
NINE = [f['id'] for f in meta.finds]; off = meta.mu({s: [-30.0] * meta.np for s in AU})
L = score(meta, recs, None, common, off, NINE, {}, wnode=wnode); print('module z, nine finds', round(post(L['globcurrent'], L['glorys12'])['shift'], 3))
for seed in (3, 4, 5):
    meta.z = np.random.default_rng(seed).standard_normal(meta.z.shape)
    L = score(meta, recs, None, common, off, NINE, {}, wnode=wnode); print('new z seed', seed, round(post(L['globcurrent'], L['glorys12'])['shift'], 3))
