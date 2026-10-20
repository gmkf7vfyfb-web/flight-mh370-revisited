"""Australian non-recovery term on run J waypoints (drift-only composition), from an Australian-pilot node table per ocean model.

For each model's pilot table (178 run A nodes): Delta_X = ln L(option X) - ln L(off), measured for the pre-registered options B, A, C,
searcher; the populated-coast-only variant (Pete, 15 Oct: only coasts where people live carry the evidence) is RECONSTRUCTED with the
drift module's saturating law Delta = -k ln(1 + W/(c F)), fitted to that table's measured B and C (W = level-weighted Australian arrival,
F = arrival on the six find coasts), with W restricted to the city and inner-regional segments (ABS RA 2021).
Delta is carried from the pilot nodes to every run A node by inverse-distance-squared weighting over the 8 nearest pilot nodes and
applied to the run A surface as L' = L exp(Delta); the composition is linear in L, so no impact is rescored.
Usage: python apply_australia.py OUT.json glorys12=<nodes.csv> [globcurrent=<nodes.csv>]
"""
import sys, json, tomllib, numpy as np, pandas as pd
from scipy.optimize import least_squares
args = dict(a.split('=', 1) for a in sys.argv[2:]); outp = sys.argv[1]
sys.argv = [sys.argv[0], 'compose-runj-waypoints.npz', 'unused.json']
exec(open('analyze_runj.py').read().split("for D in KEYS:")[0])
cfg = tomllib.load(open('aus160/aus160-globcurrent.toml', 'rb'))['hypotheses']['debris-drift']
SEGS = [s['name'] for s in cfg['segments']]; CLS = ['flaperon', 'low_exposure_exterior', 'high_windage_interior']
lvl = {'B': {d['segment']: d['ln_mean_by_period'][0] for d in cfg['levels']['segment_ln_mean_by_period']}}
lvl['C'] = {d['segment']: d['ln_mean_by_period'][0] for d in next(a for a in cfg['levels']['alternatives'] if a['name'] == 'C')['segment_ln_mean_by_period']}
POP = [s for s in SEGS if s.endswith('city-inner')]

def deltas(path):
    df = pd.read_csv(path); p = {s: np.mean([df[f'p_{c}_{i}'] for c in CLS], 0) for i, s in enumerate(SEGS)}
    F = sum(p[s] for s in SEGS[:6]); W = {o: sum(np.exp(lvl[o][s]) * p[s] for s in SEGS[6:]) for o in lvl}
    Dm = {'B': df.ln_l - df.ln_l_lev_off, 'C': df.ln_l_lev_C - df.ln_l_lev_off, 'A': df.ln_l_lev_A - df.ln_l_lev_off, 'searcher': df.ln_l_lev_searcher - df.ln_l_lev_off}
    ok = np.isfinite(F) & (F > 0) & np.isfinite(Dm['B']) & np.isfinite(Dm['C'])
    fit = least_squares(lambda x: np.concatenate([(-x[0] * np.log1p(W[o] / (x[1] * F)) - Dm[o])[ok] for o in ('B', 'C')]), [3.5, 0.2], bounds=([0.01, 1e-4], [50, 50]))
    k, c = fit.x; Dpop = -k * np.log1p(sum(p[s] for s in POP) / (c * F))
    Dwa = -k * np.log1p(p['AU-wa-city-inner'] / (c * F)); Dse = -k * np.log1p((p['AU-south-city-inner'] + p['AU-north-east-city-inner']) / (c * F))
    hold = -k * np.log1p(W['C'] / (c * F)) - Dm['C']
    halfB = (df.ln_l_half_a - df.ln_l_lev_off_half_a) - (df.ln_l_half_b - df.ln_l_lev_off_half_b)
    band = lambda x: {f'{lo}-{lo + 3}S': float(np.nanmean(x[(df.lat_deg >= -(lo + 3)) & (df.lat_deg < -lo)])) for lo in (37, 34, 31, 28, 25)}
    arr = {f'{lo}-{lo + 3}S': {'populated (city and inner regional)': float(np.mean(sum(p[s] for s in POP)[(df.lat_deg >= -(lo + 3)) & (df.lat_deg < -lo)])),
                               'all Australian coasts': float(np.mean(sum(p[s] for s in SEGS[6:])[(df.lat_deg >= -(lo + 3)) & (df.lat_deg < -lo)])),
                               'six find coasts': float(np.mean(F[(df.lat_deg >= -(lo + 3)) & (df.lat_deg < -lo)])),
                               'left domain': float(np.mean(df.left_domain_fraction[(df.lat_deg >= -(lo + 3)) & (df.lat_deg < -lo)]))} for lo in (37, 34, 31, 28, 25)}
    meta = {'k': float(k), 'c': float(c), 'n_nodes': int(len(df)), 'fit_rms': float(np.sqrt(np.mean(fit.fun ** 2))),
            'C_residual_mean_sd': [float(np.nanmean(hold[ok])), float(np.nanstd(hold[ok]))],
            'split_half_sd_of_Delta_B': float(np.nanstd(halfB) / 2), 'Delta_mean_by_band': {o: band(v) for o, v in {**Dm, 'populated-only (reconstructed)': Dpop, 'populated WA only': Dwa, 'populated south and east only': Dse}.items()},
            'arrival_by_band': arr}
    meta['segment_arrival_by_band'] = {f'{lo}-{lo + 3}S': {sg: float(np.mean(p[sg][(df.lat_deg >= -(lo + 3)) & (df.lat_deg < -lo)])) for sg in SEGS} for lo in (37, 34, 31, 28, 25)}
    return df.node.values.astype(int), {**Dm, 'populated-only (reconstructed)': np.asarray(Dpop), 'populated WA only': np.asarray(Dwa), 'populated south and east only': np.asarray(Dse)}, meta

def spread(pn, d):
    plat = G['lat0'] + (pn // NL) * G['dlat']; plon = G['lon0'] + (pn % NL) * G['dlon']
    alat = G['lat0'] + (np.arange(NC) // NL) * G['dlat']; alon = G['lon0'] + (np.arange(NC) % NL) * G['dlon']
    dx = (alon[:, None] - plon[None]) * 111.2 * np.cos(np.radians(alat[:, None])); dy = (alat[:, None] - plat[None]) * 111.2
    dist = np.hypot(dx, dy); ok = np.isfinite(d); dist[:, ~ok] = np.inf
    nn = np.argsort(dist, 1)[:, :8]; dd = np.take_along_axis(dist, nn, 1); w = 1 / np.maximum(dd, 1.0) ** 2
    out = (w * d[nn]).sum(1) / w.sum(1); exact = dd[:, 0] < 1e-6; out[exact] = d[nn[exact, 0]]; return out

res = {'models': {}, 'cells': {}}; DEL = {}
for mod, path in args.items():
    pn, Ds, meta = deltas(path); res['models'][mod] = {'table': path, **meta}
    DEL[mod] = {o: spread(pn, np.asarray(v, float)) for o, v in Ds.items()}
OPTS = list(next(iter(DEL.values())).keys())
for D in [f'D{d}' for d in range(6)]:
    cell = {}
    for o in ['none'] + OPTS:
        for mod in list(args) + (['mean'] if len(args) == 2 else []):
            if mod == 'mean':
                lg = node_L('glorys12', 'h50') * (1 if o == 'none' else np.exp(DEL['glorys12'][o])); lc = node_L('globcurrent', 'h50') * (1 if o == 'none' else np.exp(DEL['globcurrent'][o]))
                qg, lag, cg = lin_terms(D, 'glorys12', lg); qc, lac, cc = lin_terms(D, 'globcurrent', lc)
                Ln = np.where(np.isfinite(lg) & np.isfinite(lc), 0.5 * (lg + lc), np.nan); q1, l1, c1 = 0.5 * (qg + qc), 0.5 * (lag + lac), 0.5 * (cg + cc)
            else:
                Ln = node_L(mod, 'h50') * (1 if o == 'none' else np.exp(DEL[mod][o])); q1, l1, c1 = lin_terms(D, mod, Ln)
            s = stats(D, f'{mod}_h50', allidx, Ln=Ln, q1=q1, lat1=l1, c1=c1)
            e = np.exp(Z[f'{D}|logc'] - Z[f'{D}|logc'].max())
            cell[f'{o}|{mod}'] = {k: s[k] for k in ('mean_lat_core', 'mean_lat_with_drift', 'mean_lat_shift', 'dlnZ_drift', 'lnBF_core_vs_uniform', 'drift_mass_in_core90', 'core_mass_in_drift90', 'mode_displacement_nm')}
    res['cells'][D] = cell
json.dump(res, open(outp, 'w'), indent=1); print('WROTE', outp)
for mod, m in res['models'].items(): print(mod, {k: (round(v, 3) if isinstance(v, float) else v) for k, v in m.items() if k in ('k', 'c', 'fit_rms', 'C_residual_mean_sd', 'split_half_sd_of_Delta_B')})
for o in ['none'] + OPTS:
    print(o, {mod: (round(res['cells']['D0'][f'{o}|{mod}']['mean_lat_shift'], 3), round(res['cells']['D0'][f'{o}|{mod}']['lnBF_core_vs_uniform'], 3)) for mod in list(args) + (['mean'] if len(args) == 2 else [])})
