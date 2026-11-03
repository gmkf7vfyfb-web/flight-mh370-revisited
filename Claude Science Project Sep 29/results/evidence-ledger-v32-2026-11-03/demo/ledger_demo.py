"""Teaching example for the evidence ledger (3 Nov 2026). ALL NUMBERS ARE INVENTED; this is not an MH370 result.
Usage: python ledger_demo.py OUTDIR. Six stylised types of evidence on a 2,200 x 300 km strip along an arc (flat prior); posteriors for all
64 subsets; bits = log2(cells) - entropy; 90 % area; Shapley values; pairwise synergy I(A,B) - I(A) - I(B); one-vs-rest suspiciousness
ln S = ln R - ln I with p from chi2(2) (Gaussian calibration, approximate); a second scenario with the hydrophone direction wrong by 6 deg."""
import sys, math, itertools, pathlib
import numpy as np, pandas as pd
from scipy.stats import chi2
OUT = pathlib.Path(sys.argv[1]); OUT.mkdir(parents=True, exist_ok=True)
s = np.arange(0, 2202, 2.0); d = np.arange(-150, 151.5, 1.5); S, D = np.meshgrid(s, d, indexing='ij'); CELL = 2.0 * 1.5
TRUTH = (600.0, 30.0); TI = (np.abs(s - TRUTH[0]).argmin(), np.abs(d - TRUTH[1]).argmin())
KEYS = ['arc', 'perf', 'drift', 'coast', 'search', 'hydro']
NAMES = {'arc': 'Satellite arc and end of flight', 'perf': 'Aircraft performance and fuel', 'drift': 'Debris drift',
         'coast': 'No debris on populated coasts', 'search': 'Searched areas (no find)', 'hydro': 'Hydrophone direction'}
gauss = lambda x, m, sg: np.exp(-0.5 * ((x - m) / sg) ** 2)
def build(biased=False):
    L = {'arc': gauss(D, 0.0, 20.0), 'perf': gauss(S, 700, 550) / (1 + np.exp((S - 1700) / 80)),
         'drift': 0.06 + gauss(S, 620, 110) + gauss(S, 1300, 120), 'coast': 1 - 0.85 / (1 + np.exp(-(S - 1050) / 80))}
    sw = np.ones_like(S)
    sw[(S >= 150) & (S <= 560) & (np.abs(D) <= 45)] *= 0.10; sw[(S > 560) & (S <= 850) & (np.abs(D) <= 20)] *= 0.15
    sw[(S > 1150) & (S <= 1450) & (np.abs(D) <= 25)] *= 0.20; L['search'] = sw
    th = np.deg2rad(55.0); sp = 1500.0 * np.deg2rad(0.66); err = np.deg2rad(6.0) * 1500.0 if biased else 4.0
    L['hydro'] = gauss((S - TRUTH[0]) * -np.sin(th) + (D - TRUTH[1]) * np.cos(th) - err, 0.0, sp)
    return L
def ledger(L):
    H0 = np.log2(S.size); rows = []; P = {}
    for r in range(7):
        for sub in itertools.combinations(KEYS, r):
            lw = sum((np.log(L[k] + 1e-300) for k in sub), np.zeros_like(S)); w = np.exp(lw - lw.max()); p = w / w.sum()
            q = p[p > 0]; H = -(q * np.log2(q)).sum(); srt = np.sort(p.ravel())[::-1]; n90 = np.searchsorted(np.cumsum(srt), 0.9) + 1
            P[frozenset(sub)] = p
            rows.append(dict(subset=' + '.join(sub) or '(prior only)', n_types=r, bits=H0 - H, A_eff_km2=2 ** H * CELL, A90_km2=n90 * CELL,
                             truth_in_90=bool(p[TI] >= srt[n90 - 1]), P_best5000km2=srt[:int(round(5000 / CELL))].sum(),
                             lnZ=np.log(w.mean()) + lw.max(), key=frozenset(sub)))
    return pd.DataFrame(rows), P
def KLp(p): q = p[p > 0]; return (q * np.log(q * S.size)).sum()
def lnS(df, P, A, B):
    z = dict(zip(df.key, df.lnZ)); A, B = frozenset(A), frozenset(B)
    return (z[A | B] - z[A] - z[B]) - (KLp(P[A]) + KLp(P[B]) - KLp(P[A | B]))
def shapley(df):
    v = dict(zip(df.key, df.bits)); K = 6; out = {}
    for k in KEYS:
        o = [x for x in KEYS if x != k]
        out[k] = sum(math.factorial(r) * math.factorial(K - r - 1) / math.factorial(K) * (v[frozenset(sub) | {k}] - v[frozenset(sub)])
                     for r in range(K) for sub in itertools.combinations(o, r))
    return out
subs, att = [], []
for nm, b in (('all evidence correct', False), ('hydrophone direction wrong by 6 deg', True)):
    df, P = ledger(build(b)); phi = shapley(df); df.insert(0, 'scenario', nm); subs.append(df.drop(columns='key'))
    bits1 = dict(zip(df.key, df.bits))
    for k in KEYS:
        ls = lnS(df, P, [k], [x for x in KEYS if x != k])
        att.append(dict(scenario=nm, evidence=NAMES[k], shapley_bits=phi[k], alone_bits=bits1[frozenset([k])], lnS_vs_rest=ls, p_vs_rest=chi2.sf(max(2 - 2 * ls, 0), 2)))
pd.concat(subs).round(4).to_csv(OUT / 'evidence-ledger-demo-subsets.csv', index=False)
pd.DataFrame(att).round(4).to_csv(OUT / 'evidence-ledger-demo-attribution.csv', index=False)
print(pd.DataFrame(att).round(3).to_string())
