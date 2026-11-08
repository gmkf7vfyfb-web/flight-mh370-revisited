"""Convergence of the level marginalisation in the number of level draws (two cases, two seeds per count)."""
import sys, os, numpy as np, pandas as pd
sys.argv = ['x', 'rescore/x', '/Users/pete/Downloads/mh370-exchange/end-of-flight/run-j/summary/run-j-maps-accumulators.npz', 'arcm.npz', 'audit.csv', 'res-draws']
exec(open('offline/rescore_analysis.py').read().split('rows = []; nodevals = {}')[0])
rows = []
for v in ('R0-module-run', 'R3-allcoasts-4periods'):
    for nd in (256, 1024, 4096, 16384):
        for zs in (21, 22):
            ZDRAWS, ZSEED = nd, zs; meta, recs, nenv = load(v)
            common = sorted(set(recs['globcurrent']) & set(recs['glorys12'])); lat = np.array([recs['globcurrent'][k]['lat'] for k in common]); lon = np.array([recs['globcurrent'][k]['lon'] for k in common])
            base, post, wnode = core('H_D0_all', lat, lon); ids = [f['id'] for f in meta.finds]
            NINE = [f for f in ids if f.startswith('item:') and aud.loc[f.split(':')[1], 'stringent_nine'] == 'yes']
            if v == 'R0-module-run': sel, pw = NINE, {}
            else:
                sel = NINE + ['item:linga-linga-vertical-stabilizer', 'item:nautilus-bay-right-aileron', 'item:mpame-right-flap-fairing']
                pw = {f: GRADE_P[aud.loc[f.split(':')[1], 'official_classification']] for f in sel}
            L = score(meta, recs, nenv, common, mu_tiers(meta), sel, pw, wnode=wnode)
            s = post(L['globcurrent'], L['glorys12']); rows.append(dict(variant=v, draws=nd, seed=zs, shift=s['shift'], median=s['median'], N33=s['N33']))
            print(rows[-1], flush=True)
os.makedirs('res-draws', exist_ok=True); pd.DataFrame(rows).to_csv('res-draws/level-draw-convergence.csv', index=False)
