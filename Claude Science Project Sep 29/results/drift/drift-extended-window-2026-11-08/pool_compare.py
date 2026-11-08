"""Old-window (to 30 Jun 2016) nine-find likelihood from two independent runs: 7 Nov (environment seeds 101-132) and
the extended-window run rescored to the old window (seeds 201-232). Separately and pooled; 2048 level draws."""
import sys, os, glob, json, numpy as np, pandas as pd
sys.argv = ['x', 'rescore/x', '/Users/pete/Downloads/mh370-exchange/end-of-flight/run-j/summary/run-j-maps-accumulators.npz', 'arcm.npz', 'audit.csv', 'res-pool']
exec(open('offline/rescore_analysis.py').read().split('rows = []; nodevals = {}')[0])
ZDRAWS, ZSEED = 16384, 31
metaN, recN, _ = load('R1-oldwindow')
recO = {m: {} for m in MODELS}
for m in MODELS:
    for f in sorted(glob.glob(f'oldrun/conv-{m}-?-coefficients.jsonl')):
        for nd in dc.read_nodes(f): recO[m][nd['node']] = nd
    for f in sorted(glob.glob(f'oldrun/conv2-{m}-?-coefficients.jsonl')):
        for nd in dc.read_nodes(f):
            if nd['node'] not in recO[m]: continue
            for si, st in enumerate(nd['sets']):
                for part in ('full', 'half_a', 'half_b'): recO[m][nd['node']]['sets'][si][part] = recO[m][nd['node']]['sets'][si][part] + st[part]
common = sorted(set(recN['globcurrent']) & set(recO['globcurrent']) & set(recN['glorys12']) & set(recO['glorys12']))
print('common nodes', len(common))
lat = np.array([recN['globcurrent'][k]['lat'] for k in common]); lon = np.array([recN['globcurrent'][k]['lon'] for k in common])
assert np.allclose(lat, [recO['globcurrent'][k]['lat'] for k in common]) and np.allclose(lon, [recO['globcurrent'][k]['lon'] for k in common])
base, post, wnode = core('H_D0_all', lat, lon)
NINE = [f['id'] for f in metaN.finds][:9]; mu0 = mu_tiers(metaN)
pooled = {m: {k: {'sets': [{p: recO[m][k]['sets'][si][p] + recN[m][k]['sets'][si][p] for p in ('full', 'half_a', 'half_b')} for si in range(4)]} for k in common} for m in MODELS}
rows = []; V = {}
for lab, R in (('7 Nov run (seeds 101-132)', recO), ('extended run rescored to the old window (seeds 201-232)', recN), ('both runs pooled', pooled)):
    L = score(metaN, R, None, common, mu0, NINE, {}, wnode=wnode); V[lab] = L
    rows.append(dict(case=lab, **post(L['globcurrent'], L['glorys12'])))
    for m in MODELS: rows.append(dict(case=f'{lab} [{m} only]', **post(L[m], L[m])))
PS = pd.DataFrame(rows); os.makedirs('res-pool', exist_ok=True); PS.to_csv('res-pool/old-window-two-runs.csv', index=False)
pd.set_option('display.width', 200); print(PS[['case', 'mean', 'median', 'p95', 'shift', 'N33']].round(3).to_string(index=False))
d = {m: V['7 Nov run (seeds 101-132)'][m] - V['extended run rescored to the old window (seeds 201-232)'][m] for m in MODELS}
for m in MODELS:
    for band, sel in (('south of 33.25 S', lat < -33.25), ('33.25 S and north', lat >= -33.25)):
        x = d[m][sel]; print(m, band, 'run-to-run ln L difference: rms', round(float(np.sqrt(np.nanmean(x ** 2))), 2), 'mean', round(float(np.nanmean(x)), 2), 'undefined', int(np.isnan(x).sum()))
pd.DataFrame(dict(lat=lat, lon=lon, **{f'{m}|run1-run2': d[m] for m in MODELS})).to_csv('res-pool/run-to-run-node-differences.csv', index=False)
