"""Drift alone (flat prior), nine finds, old window: effect of the number of ocean samples and of level draws.
7 Nov run (seeds 101-132) and this run rescored to the old window (seeds 201-232)."""
import sys, glob, numpy as np, pandas as pd
sys.argv = ['x', 'rescore/x', '/Users/pete/Downloads/mh370-exchange/end-of-flight/run-j/summary/run-j-maps-accumulators.npz', 'arcm.npz', 'audit.csv', 'res-alone-ramp/diag']
exec(open('offline/pool_compare.py').read().split("base, post, wnode = core('H_D0_all', lat, lon)")[0].replace("ZDRAWS, ZSEED = 16384, 31\n", "ZDRAWS, ZSEED = 16384, 31\n"))
import drift_coef as dc
z16 = metaN.z.copy()
Mold = dc.Meta(sorted(glob.glob('oldrun/conv-globcurrent-1-coefficients-meta.json'))[0]); z256 = Mold.z
NINE = [f['id'] for f in metaN.finds][:9]; mu0 = mu_tiers(metaN)
def alone(lnG, lnY):
    mx = max(lnG.max(), lnY.max()); L = 0.5 * (np.exp(lnG - mx) + np.exp(lnY - mx)); o = np.argsort(lat); x = lat[o]; p = L[o] / L[o].sum()   # nodes ~ equally spaced in latitude
    c = np.cumsum(p); return dict(mean=float((p * x).sum()), median=float(x[np.searchsorted(c, 0.5)]), N33=100 * float(p[x >= -33].sum()))
def sub(R, n):
    return {m: {k: {'sets': [{p: R[m][k]['sets'][si][p][:n] for p in ('full', 'half_a', 'half_b')} for si in range(4)]} for k in common} for m in MODELS}
rows = []
for lab, R in (('7 Nov run (seeds 101-132)', recO), ('this run, old window (seeds 201-232)', recN)):
    for n, nl in ((4, 'first 4 ocean samples'), (99, 'all ocean samples (16, 32 south)')):
        for zname, z in (('256 level draws', z256), ('16384 level draws', z16)):
            metaN.z = z; L = score(metaN, sub(R, n), None, common, mu0, NINE, {})
            rows.append(dict(run=lab, ocean_samples=nl, level_draws=zname, **alone(L['globcurrent'], L['glorys12']))); print(rows[-1], flush=True)
pd.DataFrame(rows).to_csv('res-alone-ramp/diag/drift-alone-sample-count-effect.csv', index=False)
