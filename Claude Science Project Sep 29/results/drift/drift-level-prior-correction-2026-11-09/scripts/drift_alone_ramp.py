"""Drift evidence alone along the 7th arc (flat prior in arc latitude) and its tension with the core: ledger-style R, I, S, d, p.
16384 level draws. Also the earlier drift-only curve from ledger v32 (October four-sample surfaces, 256 draws)."""
import sys, os, numpy as np, pandas as pd
from scipy import stats
sys.argv = ['x', 'rescore/x', '/Users/pete/Downloads/mh370-exchange/end-of-flight/run-j/summary/run-j-maps-accumulators.npz', 'arcm.npz', 'audit.csv', 'res-alone-ramp']
exec(open('offline/rescore_analysis.py').read().split('rows = []; nodevals = {}')[0])
ZDRAWS, ZSEED = 16384, 31
Zl = np.load(LED); la = Zl['D0|lat']; ok = np.isfinite(la); la = la[ok]
pi = np.nan_to_num(Zl['D0|(uniform along the arc)'])[ok]; pi /= pi.sum()
pc = np.nan_to_num(Zl['D0|core'])[ok]; pc /= pc.sum(); reach = np.nan_to_num(Zl['D0|reach'])[ok]
old_drift = np.nan_to_num(Zl['D0|drift'])[ok]; old_drift = old_drift / old_drift.sum()
def tension(LB):   # LB on ledger bins (likelihood, any scale); A = core with prior pi
    LA = np.where(pi > 0, pc / np.maximum(pi, 1e-300), 0)
    def post(L): p = pi * L; return p / p.sum()
    pA, pB, pAB = post(LA), post(LB), post(LA * LB)
    KL = lambda p: float(np.sum(np.where(p > 0, p * np.log(np.maximum(p, 1e-300) / np.maximum(pi, 1e-300)), 0)))
    def dim(p, L):
        lL = np.log(np.maximum(L, 1e-300)); m = (p * lL).sum(); return 2 * float((p * (lL - m) ** 2).sum())
    lnR = float(np.log((pi * LA * LB).sum()) - np.log((pi * LA).sum()) - np.log((pi * LB).sum()))
    lnI = KL(pA) + KL(pB) - KL(pAB); lnS = lnR - lnI
    d = dim(pA, LA) + dim(pB, LB) - dim(pAB, LA * LB); d = max(d, 1e-6)
    p = float(stats.chi2.sf(d - 2 * lnS, d)) if d - 2 * lnS > 0 else 1.0
    return dict(lnR=lnR, lnI=lnI, lnS=lnS, d=d, p=p, sigma=float(stats.norm.isf(p / 2)))
def summ(p):
    o = np.argsort(la); c = np.cumsum(p[o]); q = lambda f: la[o][np.searchsorted(c, f)]
    return dict(mean=float((p * la).sum()), median=q(0.5), p05=q(0.05), p95=q(0.95), mode=float(la[np.argmax(p / np.maximum(pi, 1e-300))]) if False else float(la[np.argmax(p)]), N33=100 * float(p[la >= -33].sum()), S36=100 * float(p[la < -36].sum()))
rows, curves = [], {'lat': la, 'flat prior': pi, 'core': pc, 'earlier drift alone (ledger v32, October surfaces)': old_drift}
s = summ(pc); rows.append(dict(case='core (satellite and flight data)', **s))
s = summ(old_drift); rows.append(dict(case='earlier drift alone (ledger v32, October surfaces, 256 draws)', **s, **tension(old_drift / np.maximum(pi, 1e-300))))
for v, cases in (('R0-module-run', ['nine']), ('R1-oldwindow', ['nine']), ('R3-allcoasts-4periods', ['head', 'nine', 'au025', 'au1', 'mbonly', 'butmb'])):
    meta, recs, nenv = load(v)
    common = sorted(set(recs['globcurrent']) & set(recs['glorys12'])); lat = np.array([recs['globcurrent'][k]['lat'] for k in common]); lon = np.array([recs['globcurrent'][k]['lon'] for k in common])
    wnode = core('H_D0_all', lat, lon)[2]; ids = [f['id'] for f in meta.finds]
    NINE = [f for f in ids if f.startswith('item:') and aud.loc[f.split(':')[1], 'stringent_nine'] == 'yes']
    H = NINE + [f'item:{o}' for o in ('linga-linga-vertical-stabilizer', 'nautilus-bay-right-aileron', 'mpame-right-flap-fairing') if f'item:{o}' in ids]
    PW = {f: GRADE_P[aud.loc[f.split(':')[1], 'official_classification']] for f in H}; MB = 'item:mossel-bay-engine-cowling-roy'
    C = {'nine': ('nine finds', NINE, {}, mu_tiers(meta)), 'head': ('HEADLINE twelve items', H, PW, mu_tiers(meta)), 'au025': ('headline + Australia ratio 0.25', H, PW, mu_tiers(meta, au=ruled_au(0.25))),
         'au1': ('headline + Australia ratio 1', H, PW, mu_tiers(meta, au=ruled_au(1.0))), 'mbonly': ('Mossel Bay only', [MB], PW, mu_tiers(meta)), 'butmb': ('headline without Mossel Bay', [x for x in H if x != MB], PW, mu_tiers(meta))}
    for key in cases:
        name, sel, pw, mu = C[key]; L = score(meta, recs, nenv, common, mu, sel, pw, wnode=wnode)
        for mlab, lnL in (('both models', None), ('GlobCurrent', L['globcurrent']), ('GLORYS12', L['glorys12'])):
            if lnL is None:
                mx = max(L['globcurrent'].max(), L['glorys12'].max()); Ln = 0.5 * (np.exp(L['globcurrent'] - mx) + np.exp(L['glorys12'] - mx))
            else: Ln = np.exp(lnL - lnL.max())
            o = np.argsort(lat); LB = np.interp(la, lat[o], Ln[o], left=np.nan, right=np.nan)
            inside = np.isfinite(LB); LB = np.where(inside, LB, 0.0)   # outside the 84 release points: no drift information computed -> excluded
            p = pi * LB; p = p / p.sum(); lab = f'{v} | {name} | {mlab}'
            rows.append(dict(case=lab, **summ(p), **tension(np.where(inside, LB, 1e-300)), lat_range=f'{lat.min():.2f} to {lat.max():.2f}')); curves[lab] = p
        print(v, name, flush=True)
os.makedirs('res-alone-ramp', exist_ok=True)
T = pd.DataFrame(rows); T.to_csv('res-alone-ramp/drift-alone-and-tension.csv', index=False); pd.DataFrame(curves).to_csv('res-alone-ramp/drift-alone-curves.csv', index=False)
pd.set_option('display.width', 250); pd.set_option('display.max_colwidth', 80)
print(T.drop(columns=['lat_range'], errors='ignore').round(3).to_string(index=False))
print('release points latitude range', rows[-1].get('lat_range'), 'ledger range', la.min(), la.max())
print('reach vs core (5 bins)', np.c_[la[::40], reach[::40], pc[::40] * 1e3][:12])
