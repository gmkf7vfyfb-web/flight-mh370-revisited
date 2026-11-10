"""Posterior of the exterior-class windage hyperparameters (median m, log-sd sigma) from the drift data and the ruled core, 10 Nov 2026.

Each grid target is a truncated log-normal prior for the windage of every exterior object (truncated to 0.3-5 % of U10 on the wide-run grid, 0.8-5 % on the higher-run grid).
The stored particles of the wide run (sampling median 1.2 %, 0.3-5 %) and of the higher-windage run (median 2.4 %, 0.8-6 %) were reweighted by windage (reweight_rescore.py),
rescored offline and scored with the headline configuration (smooth_stage1 head, seeds 1-4). Wide-run targets use 48 ocean samples in the south, higher-run targets 32.
Z(theta) = core-weighted mean likelihood at the 84 release points, two ocean models at equal weight (same definition as the earlier ln Z of the three priors).
Posterior on the grid: p(theta | data) proportional to pi(theta) Z(theta); pi is uniform on the cells used (log-uniform in m, uniform in sigma).
Hierarchical likelihood for the latitude: lm_mix = ln sum_theta pi(theta) exp(lm_theta) at every release point and ocean sample (prior weights; the data enter through the likelihood).
Outputs: windage-hyperparameter-grid.csv, windage-hyperparameter-posterior.csv, res-grid/mixA (wide grid, 48 samples), res-grid/mixB (all cells with sigma <= 0.5, 32 samples).
"""
import numpy as np, pandas as pd, json, glob, os, sys
from scipy.special import logsumexp
wn = np.load('res-smooth/wnode_df.npy'); wn = wn / wn.sum(); SEEDS = (1, 2, 3, 4)
T = json.load(open('rw-in/targets-grid.json')) + json.load(open('rw-in/targets-high.json'))
tags = [t['tag'] for t in T if t['tag'][0] in 'mh']
def get(tag, mm, ncols=None):
    out = []
    for s in SEEDS:
        lm = np.load(f'res-grid/{tag}/lm-head-s{s}.npz')['lm_' + mm]
        if ncols: lm = lm.copy(); lm[:, ncols:] = np.nan
        out.append(lm)
    return np.array(out)                                    # (seeds, 84, 48)
def lnz(arr):
    li = np.array([[logsumexp(r[~np.isnan(r)]) - np.log((~np.isnan(r)).sum()) for r in a] for a in arr])
    return float(logsumexp(logsumexp(li, axis=0) - np.log(len(arr)) + np.log(wn)))
rows = []
for t in tags:
    fam = 'higher-run particles' if t.startswith('h_') else 'wide-run particles'
    m_, s_ = t.replace('h_', '')[1:].split('_s'); r = dict(tag=t, particles=fam, median_pct=float(m_), sigma_log=float(s_))
    for nc, nm in ((None, 'all'), (32, '32')):
        zz = [lnz(get(t, mm, nc)) for mm in ('globcurrent', 'glorys12')]; r[f'lnZ_{nm}_samples'] = float(np.logaddexp(*zz) - np.log(2))
    rows.append(r)
G = pd.DataFrame(rows); G.to_csv('windage-hyperparameter-grid.csv', index=False)
print(G.round(2).to_string(index=False))
