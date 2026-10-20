"""Composer views on run J, step 0: drift node likelihoods and the Australian populated-coast node adjustment.

Drift: run A rebuilt node surfaces (debris-drift/runA-rebuilt/*/merged/nodes.csv), columns ln_l (50 km kernel) and ln_l_h100.
Australian non-recovery, populated coasts only (Pete 15 Oct; RECONSTRUCTED, labelled sensitivity): the functions deltas() and
spread() below are copied VERBATIM in substance from results/drift-runj-2026-10-17/apply_australia.py (drift stand-in, 17 Oct):
saturating law Delta = -k ln(1 + W/(c F)) fitted per model to the measured options B and C of the 15-160 E pilot node tables,
W restricted to city + inner-regional segments, carried to every run A node by inverse-distance-squared over the 8 nearest
pilot nodes. Output: nodes.npz with per-node arrays (NaN = node not evaluated).
Usage: python prep_nodes.py OUT.npz
"""
import sys, tomllib, json, pathlib, numpy as np, pandas as pd
from scipy.optimize import least_squares
HERE = pathlib.Path(__file__).resolve().parent
DR = HERE.parent / 'drift-runj-2026-10-17'
REB = pathlib.Path('/Users/pete/Downloads/mh370-exchange/debris-drift/runA-rebuilt')
G = dict(lat0=-41.166666666666664, lon0=83.96226004720266, dlat=0.5, dlon=0.5856322967993869, nlat=41, nlon=38)
NC = G['nlat'] * G['nlon']; NL = G['nlon']

def nodes(model, col):
    df = pd.read_csv(REB / f'debris-drift-production-{model}/merged/nodes.csv'); v = np.full(NC, np.nan)
    ok = np.isfinite(df[col].values); v[df.node.values[ok]] = df[col].values[ok]; return v

cfg = tomllib.load(open(DR / 'australia-160E/aus160-globcurrent.toml', 'rb'))['hypotheses']['debris-drift']
SEGS = [s['name'] for s in cfg['segments']]; CLS = ['flaperon', 'low_exposure_exterior', 'high_windage_interior']
lvl = {'B': {d['segment']: d['ln_mean_by_period'][0] for d in cfg['levels']['segment_ln_mean_by_period']}}
lvl['C'] = {d['segment']: d['ln_mean_by_period'][0] for d in next(a for a in cfg['levels']['alternatives'] if a['name'] == 'C')['segment_ln_mean_by_period']}
POP = [s for s in SEGS if s.endswith('city-inner')]

def deltas(path):
    df = pd.read_csv(path); p = {s: np.mean([df[f'p_{c}_{i}'] for c in CLS], 0) for i, s in enumerate(SEGS)}
    F = sum(p[s] for s in SEGS[:6]); W = {o: sum(np.exp(lvl[o][s]) * p[s] for s in SEGS[6:]) for o in lvl}
    Dm = {'B': df.ln_l - df.ln_l_lev_off, 'C': df.ln_l_lev_C - df.ln_l_lev_off}
    ok = np.isfinite(F) & (F > 0) & np.isfinite(Dm['B']) & np.isfinite(Dm['C'])
    fit = least_squares(lambda x: np.concatenate([(-x[0] * np.log1p(W[o] / (x[1] * F)) - Dm[o])[ok] for o in ('B', 'C')]), [3.5, 0.2], bounds=([0.01, 1e-4], [50, 50]))
    k, c = fit.x; Dpop = -k * np.log1p(sum(p[s] for s in POP) / (c * F))
    return df.node.values.astype(int), np.asarray(Dpop, float), {'k': float(k), 'c': float(c)}

def spread(pn, d):
    plat = G['lat0'] + (pn // NL) * G['dlat']; plon = G['lon0'] + (pn % NL) * G['dlon']
    alat = G['lat0'] + (np.arange(NC) // NL) * G['dlat']; alon = G['lon0'] + (np.arange(NC) % NL) * G['dlon']
    dx = (alon[:, None] - plon[None]) * 111.2 * np.cos(np.radians(alat[:, None])); dy = (alat[:, None] - plat[None]) * 111.2
    dist = np.hypot(dx, dy); ok = np.isfinite(d); dist[:, ~ok] = np.inf
    nn = np.argsort(dist, 1)[:, :8]; dd = np.take_along_axis(dist, nn, 1); w = 1 / np.maximum(dd, 1.0) ** 2
    out = (w * d[nn]).sum(1) / w.sum(1); exact = dd[:, 0] < 1e-6; out[exact] = d[nn[exact, 0]]; return out

out, meta = {}, {}
for mod in ('glorys12', 'globcurrent'):
    out[f'{mod}_h50'] = nodes(mod, 'ln_l'); out[f'{mod}_h100'] = nodes(mod, 'ln_l_h100')
    pn, Dp, km = deltas(DR / f'australia-160E/aus160-{mod}/nodes.csv'); out[f'{mod}_dpop'] = spread(pn, Dp); meta[mod] = km
np.savez(sys.argv[1], G=json.dumps(G), meta=json.dumps(meta), **out)
print('fit constants', meta, {k: int(np.isfinite(v).sum()) for k, v in out.items()})
