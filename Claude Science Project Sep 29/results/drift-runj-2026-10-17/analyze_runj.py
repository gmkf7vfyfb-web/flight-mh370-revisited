"""Tension statistics for the drift-only composition of run J waypoints (reads compose-runj-waypoints.npz).

Per 00:19 treatment (q = 1/3, C2 silent; end of flight's two-factor cells) and per drift surface:
  core impact PDF (P1, no drift) vs the same with drift (Dr), and the drift-only density (display prior: uniform per unit area over
  drift-grid cells whose four corner nodes are all evaluated).
Statistics: shift of mean latitude; 5/50/95 % latitude; d lnZ (drift); ln BF of the core impact distribution against the uniform
reference, ln[E_core L / E_ref L]; ln[E_core L / max L]; two-way overlap of 90 % regions on the drift grid; mode displacement (NM);
ESS ratio; family shares; drift not-computed share.
Uncertainty: (a) seed bootstrap over the 24 seeds (1000 draws); (b) transport-noise replicates (200): each node's ln L perturbed by
N(-s_band^2/2, s_band) (mean-preserving in L), s_band = RMS(half_a - half_b)/2 per 1-deg latitude band from the committed split-half columns, exploiting linearity in L.
Usage: python analyze_runj.py compose-runj-waypoints.npz OUT.json
"""
import sys, json, numpy as np, pandas as pd
Z = np.load(sys.argv[1]); LAT = Z['LAT']; LREF = float(-125.0)
G = dict(lat0=-41.166666666666664, lon0=83.96226004720266, dlat=0.5, dlon=0.5856322967993869, nlat=41, nlon=38)
NC = G['nlat'] * G['nlon']; NL = G['nlon']
ci = np.arange(NC) // NL; cj = np.arange(NC) % NL
clat = G['lat0'] + (ci + 0.5) * G['dlat']; clon = G['lon0'] + (cj + 0.5) * G['dlon']
area = np.cos(np.radians(clat))
CORN = np.stack([np.arange(NC), np.arange(NC) + NL, np.arange(NC) + 1, np.arange(NC) + NL + 1], 1)
valid_cell = (ci < G['nlat'] - 1) & (cj < G['nlon'] - 1)
CORN = np.where(valid_cell[:, None], CORN, 0)
REB = '/Users/pete/Downloads/mh370-exchange/debris-drift/runA-rebuilt'
RES = 'repo/Claude Science Project Sep 29/results'

def nodes(model, col='ln_l'):
    df = pd.read_csv(f'{REB}/debris-drift-production-{model}/merged/nodes.csv'); v = np.full(NC, np.nan)
    ok = np.isfinite(df[col].values); v[df.node.values[ok]] = df[col].values[ok]; return v
NODES = {('glorys12', b): nodes('glorys12', c) for b, c in (('h50', 'ln_l'), ('h25', 'ln_l_h25'), ('h100', 'ln_l_h100'), ('h200', 'ln_l_h200'))}
NODES.update({('globcurrent', b): nodes('globcurrent', c) for b, c in (('h50', 'ln_l'), ('h25', 'ln_l_h25'), ('h100', 'ln_l_h100'), ('h200', 'ln_l_h200'))})
def node_L(mod, bw, delta=None):
    if mod == 'mean':
        a = node_L('glorys12', bw, None if delta is None else delta[0]); b = node_L('globcurrent', bw, None if delta is None else delta[1])
        return np.where(np.isfinite(a) & np.isfinite(b), 0.5 * (a + b), np.nan)
    v = NODES[(mod, bw)] + (0 if delta is None else delta)
    return np.exp(v - LREF)

def drift_only(Ln):
    Lc = Ln[CORN].mean(1); ok = valid_cell & np.all(np.isfinite(Ln[CORN]), 1)
    Lc = np.where(ok, Lc, np.nan); mass = np.where(ok, Lc * area, 0.0)
    lnEref = np.log(np.nansum(Lc * area) / area[ok].sum()) + LREF; lnLmax = np.log(np.nanmax(Lc)) + LREF
    return mass, ok, lnEref, lnLmax, Lc

def hdr(mass, dens, level=0.9):
    o = np.argsort(-dens); cm = np.cumsum(mass[o]) / mass.sum(); sel = np.zeros(len(mass), bool); sel[o[:np.searchsorted(cm, level) + 1]] = True; return sel

def gc_nm(a, b):
    la1, lo1, la2, lo2 = map(np.radians, (clat[a], clon[a], clat[b], clon[b]))
    return float(3440.065 * 2 * np.arcsin(np.sqrt(np.sin((la2 - la1) / 2) ** 2 + np.cos(la1) * np.cos(la2) * np.sin((lo2 - lo1) / 2) ** 2)))

def quant(h):
    c = np.cumsum(h); c /= c[-1]; return [float(LAT[np.searchsorted(c, q)]) for q in (0.05, 0.5, 0.95)]

def stats(D, t, idx, Ln=None, q1=None, lat1=None, c1=None):
    e = np.exp(Z[f'{D}|logc'][idx] - Z[f'{D}|logc'][idx].max()); P0 = (e * Z[f'{D}|p0'][idx]).sum()
    Q1 = (e * Z[f'{D}|{t}|q1'][idx]).sum() if q1 is None else (e * q1[idx]).sum()
    L1 = (e * Z[f'{D}|{t}|lat1'][idx]).sum() if lat1 is None else (e * lat1[idx]).sum()
    C1 = (e[:, None] * (Z[f'{D}|{t}|c1'][idx] if c1 is None else c1[idx])).sum(0)[:NC]
    C0 = (e[:, None] * Z[f'{D}|c0'][idx]).sum(0)[:NC]
    mod, bw = t.split('_'); Ln = node_L(mod, bw) if Ln is None else Ln
    dm, ok, lnEref, lnLmax, Lc = drift_only(Ln)
    dlnZ = float(np.log(Q1 / P0) + LREF)
    core90 = hdr(C0, C0 / area); drift90 = hdr(dm, np.where(ok, Lc, -1))
    out = {'mean_lat_core': float((e * Z[f'{D}|lat0'][idx]).sum() / P0), 'mean_lat_with_drift': float(L1 / Q1),
           'dlnZ_drift': dlnZ, 'lnBF_core_vs_uniform': dlnZ - lnEref, 'ln_core_over_max': dlnZ - lnLmax,
           'drift_mass_in_core90': float(dm[core90].sum() / dm.sum()), 'core_mass_in_drift90': float(C0[drift90].sum() / C0.sum()),
           'mode_displacement_nm': gc_nm(int(np.argmax(C0 / area)), int(np.argmax(np.where(ok, Lc, -1)))),
           'core_mass_outside_drift_cells': float(C0[~ok].sum() / C0.sum())}
    out['mean_lat_shift'] = out['mean_lat_with_drift'] - out['mean_lat_core']
    return out

KEYS = [f'D{d}' for d in range(6)]; SURF = ['glorys12_h50', 'globcurrent_h50', 'mean_h50', 'mean_h25', 'mean_h100', 'mean_h200']
K = len(Z['seeds']); allidx = np.arange(K); res = {'seeds': int(K), 'cells': {}}
# transport noise sd per node from committed split halves, pooled per 1-deg band
rel = pd.read_csv(f'{RES}/debris-drift-two-model-nodes-relwind.csv')
sc = pd.concat([pd.read_csv(f'/Users/pete/Downloads/mh370-exchange/debris-drift/runA-standin/chunk-{k}/nodes.csv') for k in (2, 3)])
def band_sd(lat, a, b):
    d = pd.DataFrame({'band': np.floor(lat), 'd2': (a - b) ** 2}).dropna(); s = d.groupby('band').d2.mean() ** 0.5 / 2; return s
sd_g = band_sd(pd.concat([rel.lat_deg, sc.lat_deg]), pd.concat([rel.ln_l_half_a, sc.ln_l_half_a]), pd.concat([rel.ln_l_half_b, sc.ln_l_half_b]))
sd_c = band_sd(rel.lat_deg, rel.ln_l_half_a_gc, rel.ln_l_half_b_gc)
nlat_node = G['lat0'] + (np.arange(NC) // NL) * G['dlat']
def sd_nodes(s):
    b = np.floor(nlat_node); keys = np.array(s.index); return np.array([s.loc[keys[np.argmin(np.abs(keys - x))]] for x in b])
SDN = {'glorys12': sd_nodes(sd_g), 'globcurrent': sd_nodes(sd_c)}
res['noise_sd_by_band'] = {'glorys12': {str(int(k)): round(float(v), 3) for k, v in sd_g.items()}, 'globcurrent': {str(int(k)): round(float(v), 3) for k, v in sd_c.items()}}
rng = np.random.default_rng(20261017)

def lin_terms(D, mod, ell):
    """Per-seed q1, lat1, c1 for model surface given node likelihood vector ell (NaN -> 0)."""
    ell = np.nan_to_num(ell); t = f'{mod}_h50'
    S = Z[f'{D}|{t}|M'] @ ell; Lbar = S / Z[f'{D}|{t}|Ssc']
    q1 = S + Z[f'{D}|{t}|U'] * Lbar; lat1 = Z[f'{D}|{t}|Mlat'] @ ell + Z[f'{D}|{t}|Ulat'] * Lbar
    MC = Z[f'{D}|{t}|MC'].reshape(K, NC + 1, 4)[:, :NC, :]
    c1 = np.einsum('skc,kc->sk', MC, ell[CORN]) + Z[f'{D}|{t}|Uc'][:, :NC] * Lbar[:, None]
    return q1, lat1, np.concatenate([c1, np.zeros((K, 1))], 1)

for D in KEYS:
    e = np.exp(Z[f'{D}|logc'] - Z[f'{D}|logc'].max()); P0 = (e * Z[f'{D}|p0']).sum()
    hp = (e[:, None] * Z[f'{D}|hp']).sum(0)
    cell = {'core': {'latitude_q05_q50_q95': quant(hp), 'ESS': float(P0 ** 2 / (e ** 2 * Z[f'{D}|p2']).sum()),
                     'families_A1_A2_B': list(map(float, (e[:, None] * Z[f'{D}|fam0']).sum(0) / P0))}}
    for t in SURF:
        s = stats(D, t, allidx); Q1 = (e * Z[f'{D}|{t}|q1']).sum()
        s['latitude_q05_q50_q95_with_drift'] = quant((e[:, None] * Z[f'{D}|{t}|hq']).sum(0))
        s['ESS_with_drift'] = float(Q1 ** 2 / (e ** 2 * Z[f'{D}|{t}|q2']).sum()); s['ESS_ratio'] = s['ESS_with_drift'] / cell['core']['ESS']
        s['families_with_drift'] = list(map(float, (e[:, None] * Z[f'{D}|{t}|fam1']).sum(0) / Q1))
        s['not_computed_share'] = float((e * Z[f'{D}|{t}|nc']).sum() / P0)
        if t in ('glorys12_h50', 'globcurrent_h50', 'mean_h50'):
            boot = [stats(D, t, rng.integers(0, K, K)) for _ in range(1000)]
            s['seed_bootstrap'] = {k: [float(np.std([b[k] for b in boot])), float(np.quantile([b[k] for b in boot], 0.025)), float(np.quantile([b[k] for b in boot], 0.975))]
                                   for k in ('mean_lat_shift', 'dlnZ_drift', 'lnBF_core_vs_uniform', 'drift_mass_in_core90', 'core_mass_in_drift90', 'mode_displacement_nm')}
            reps = []
            for r_ in range(201):
                dg = 0 if r_ == 0 else rng.normal(-0.5 * SDN['glorys12'] ** 2, SDN['glorys12']); dc = 0 if r_ == 0 else rng.normal(-0.5 * SDN['globcurrent'] ** 2, SDN['globcurrent'])
                if t == 'mean_h50':
                    qg, lg, cg = lin_terms(D, 'glorys12', node_L('glorys12', 'h50', dg)); qc, lc_, cc = lin_terms(D, 'globcurrent', node_L('globcurrent', 'h50', dc))
                    q1, lat1, c1 = 0.5 * (qg + qc), 0.5 * (lg + lc_), 0.5 * (cg + cc); Ln = node_L('mean', 'h50', (dg, dc))
                else:
                    mod = t.split('_')[0]; d_ = dg if mod == 'glorys12' else dc; Ln = node_L(mod, 'h50', d_); q1, lat1, c1 = lin_terms(D, mod, Ln)
                reps.append(stats(D, t, allidx, Ln=Ln, q1=q1, lat1=lat1, c1=c1))
            s['linear_check_vs_direct'] = {k: reps[0][k] - s[k] for k in ('mean_lat_shift', 'dlnZ_drift', 'drift_mass_in_core90')}
            s['transport_noise'] = {k: [float(np.std([b[k] for b in reps[1:]])), float(np.quantile([b[k] for b in reps[1:]], 0.025)), float(np.quantile([b[k] for b in reps[1:]], 0.975))]
                                    for k in ('mean_lat_shift', 'dlnZ_drift', 'lnBF_core_vs_uniform', 'drift_mass_in_core90', 'core_mass_in_drift90', 'mode_displacement_nm')}
        cell[t] = s
    res['cells'][D] = cell
    print(D, 'done', flush=True)
json.dump(res, open(sys.argv[2], 'w'), indent=1)
print('WROTE', sys.argv[2])
