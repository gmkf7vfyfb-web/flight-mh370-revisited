
"""Row-level drift conditional for the Kadri hypothesis (Q7): run J impact rows weighted by end-of-flight's two-factor cells
'D{d} total q=0.333 (C2 silent)' (option_table_0019.seed_terms logic, lean copy restricted to those six cells) and by the
pre-registered acoustic likelihood (Q2: N(t_obs - t_i - d_i/c; 0, s_t) x N(b_obs - b_i; 0, s_b), c = 1.48 km/s,
s_t^2 = (d_i/c * 0.015/c)^2 + 5^2 s^2, s_b = 0.5 / 1.0 deg), branches T 00:52:03 and C 00:54:30 at H01W.
Times from run.json T0_unix_s via compact_impacts.load. Accumulates, per seed, the linear node-contribution vectors on the
run A drift node grid (bilinear corners), so any node surface (model, option, perturbation) can be applied afterwards.
Usage: python rowcond.py OUT.npz stratum=P [...]   (env KSEEDS=n limits seeds per stratum for a smoke)
"""
import sys, os, json, csv, pathlib, numpy as np
sys.path.insert(0, 'scorer')
import displacement_hist as DH
DH.SATCOM_CSV = pathlib.Path('scorer/satcom-observations.csv').resolve()
from compact_impacts import load, family_labels
from displacement_hist import derived_logliks, constraint_log_factor
from scipy.special import gammaln
from scipy.stats import norm
import option_table_0019 as OT
from pyproj import Geod
GEO = Geod(ellps='WGS84')
X = pathlib.Path('/Users/pete/Downloads/mh370-exchange'); EOF = X/'end-of-flight/run-j'; CORE = X/'core/run-j'
W_S = OT.W_S
G = dict(lat0=-41.166666666666664, lon0=83.96226004720266, dlat=0.5, dlon=0.5856322967993869, nlat=41, nlon=38)
NC = G['nlat']*G['nlon']; NL = G['nlon']
H01 = (-34.8903, 114.1426); BOBS = 306.18; C_KMS = 1.48
TOBS = {'T': 1394236800.0 + 52*60 + 3, 'C': 1394236800.0 + 54*60 + 30}
VARS = ['none', 'T_core', 'T_wide', 'C_core', 'C_wide']
TBIN = np.arange(1394236800.0 - 3600, 1394236800.0 + 5400 + 1, 30.0)   # 23:00-01:30, 30 s
import pandas as pd
REB = X/'debris-drift/runA-rebuilt'
def node_ok(model):
    df = pd.read_csv(REB/f'debris-drift-production-{model}/merged/nodes.csv'); v = np.zeros(NC, bool)
    v[df.node.values[np.isfinite(df.ln_l.values)]] = True; return v
NOK = {m: node_ok(m) for m in ('glorys12', 'globcurrent')}

def cells6(sd, handoff):
    meta, g = load(sd); logon = meta['config']['hypotheses']['end-of-flight']['logon']
    obs = {r['epoch_id']: r for r in csv.DictReader(open(DH.SATCOM_CSV))}
    w = g('weight'); lw = np.log(w) - np.log(w.sum())
    present = [c[len('loglik:'):] for c in meta['impact_columns'] if c.startswith('loglik:')]; der = derived_logliks(meta, g, present)
    V = np.asarray(np.load(handoff, mmap_mode='r')[:, 9])[g('parent').astype(np.int64)]
    col = lambda k: np.where(np.isfinite(g('loglik:'+k)), g('loglik:'+k), -np.inf)
    D = {'D0': np.zeros(len(w)), 'D1': der['r600-bto'], 'D2': col('r600/no-offset'), 'D3': col('both/no-offset'), 'D4': col('both/startup-offset'), 'D5': OT.d5_loglik(g, V, obs)}
    lag = logon['logon_unix_s'] - g('latent:realised_flameout_unix_s')
    with np.errstate(divide='ignore', invalid='ignore'):
        lfe = (logon['lag_shape']-1)*np.log(lag) - lag/logon['lag_scale_s'] - logon['lag_shape']*np.log(logon['lag_scale_s']) - gammaln(logon['lag_shape'])
        surv = np.log1p(-np.clip(g('latent:inflight_p_breakup_to_m0019b'), 0, 1))
    lfe = np.where(np.isfinite(lag) & (lag > 0), lfe, -np.inf)
    C1 = lfe + constraint_log_factor(g, logon, 'fuel-exhaustion', 'unpowered'); C2 = -np.log(W_S) + constraint_log_factor(g, logon, 'other', 'silent')
    p = 1/(1+1/3); lc = np.logaddexp(np.log(p)+C1, np.log(1-p)+C2)
    return {d: lw + surv + ld + lc for d, ld in D.items()}, g

def corners(lat, lon):
    fi = (lat-G['lat0'])/G['dlat']; fj = (lon-G['lon0'])/G['dlon']
    inside = (fi >= 0) & (fj >= 0) & (fi <= G['nlat']-1) & (fj <= G['nlon']-1)
    i = np.minimum(np.floor(np.where(inside, fi, 0)).astype(int), G['nlat']-2); j = np.minimum(np.floor(np.where(inside, fj, 0)).astype(int), G['nlon']-2)
    ti, tj = fi-i, fj-j
    W = np.stack([(1-ti)*(1-tj), ti*(1-tj), (1-ti)*tj, ti*tj], 1); cid = i*NL+j
    return inside, np.stack([cid, cid+NL, cid+1, cid+NL+1], 1), W

def seed(sd, handoff):
    cells, g = cells6(sd, handoff)
    lat, lon, t = g('latitude_deg'), g('longitude_deg'), g('unix_s')
    az, _, dm = GEO.inv(np.full(len(lat), H01[1]), np.full(len(lat), H01[0]), lon, lat); d = dm/1e3; az = np.mod(az, 360)
    st = np.sqrt((d/C_KMS*0.015/C_KMS)**2 + 25.0); db = (az - BOBS + 180) % 360 - 180
    lLa = {}
    for br in 'TC':
        lt = norm.logpdf(TOBS[br] - (t + d/C_KMS), 0, st)
        lLa[f'{br}_core'] = lt + norm.logpdf(db, 0, 0.5); lLa[f'{br}_wide'] = lt + norm.logpdf(db, 0, 1.0)
    inside, nid, W = corners(lat, lon)
    val = {'glorys12': inside & NOK['glorys12'][nid].all(1), 'globcurrent': inside & NOK['globcurrent'][nid].all(1)}
    val['mean'] = val['glorys12'] & val['globcurrent']
    f4 = family_labels(g('latent:onset_mechanism'), g('latent:control_realised'), g('latent:recovery_attempted'))['family4_code']
    par = g('parent').astype(np.int64)
    out = {}
    for D, a in cells.items():
        for v in VARS:
            b = a if v == 'none' else a + lLa[v]
            fin = np.isfinite(b); s = float(b[fin].max())
            sel = np.where(fin & (b > s - 45))[0] if v != 'none' else np.where(fin)[0]
            m = np.exp(b[sel] - s); r = {'s': s, 'sum': m.sum(), 'sum2': (m*m).sum()}
            for vk, vm in val.items():
                ok = vm[sel]; r['vec_'+vk] = np.bincount(nid[sel][ok].ravel(), weights=(m[ok, None]*W[sel][ok]).ravel(), minlength=NC); r['den_'+vk] = m[ok].sum()
                for fc, fn in ((1, 'A1'), (2, 'A2'), (3, 'B')):
                    okf = ok & (f4[sel] == fc)
                    r[f'vec_{vk}_{fn}'] = np.bincount(nid[sel][okf].ravel(), weights=(m[okf, None]*W[sel][okf]).ravel(), minlength=NC); r[f'den_{vk}_{fn}'] = m[okf].sum()
                    r[f'sum_{fn}'] = m[f4[sel] == fc].sum()
            r['fam'] = np.bincount(np.nan_to_num(f4[sel], nan=0).astype(int), weights=m, minlength=8)
            r['thist'] = np.histogram(t[sel], TBIN, weights=m)[0]
            if v != 'none':
                o = np.argsort(-m); cm = np.cumsum(m[o])/m.sum(); top = o[:np.searchsorted(cm, 0.99)+1]
                r['parents99'] = len(np.unique(par[sel][top])); r['rows99'] = len(top)
                r['lat_mean'] = float((m*lat[sel]).sum()/m.sum()); r['lon_mean'] = float((m*lon[sel]).sum()/m.sum())
                r['d_inside_km'] = np.histogram(d[sel]-1591.3, np.arange(-300, 601, 10), weights=m)[0]
            out[(D, v)] = r
    return out

if __name__ == '__main__':
    outp = sys.argv[1]; strata = {a.split('=')[0]: float(a.split('=')[1]) for a in sys.argv[2:]}
    kmax = int(os.environ.get('KSEEDS', '999')); res = {}
    for stn, P in strata.items():
        seeds = sorted((p for p in (EOF/stn).glob('seed-*') if p.is_dir()), key=lambda p: int(p.name.split('-')[1])); K = len(seeds); lo, hi = (int(x) for x in os.environ.get('SEEDSEL', '0:999').split(':')); seeds = seeds[lo:hi]
        for sd in seeds:
            o = seed(sd, CORE/stn/'bto-bfo'/sd.name/'handoff-m0011'/'handoff.npy')
            res[(stn, sd.name)] = (np.log(P/K), o); print(stn, sd.name, flush=True)
    flat = {}
    for (stn, sn), (c, o) in res.items():
        for (D, v), r in o.items():
            for k, x in r.items(): flat[f'{stn}|{sn}|{D}|{v}|{k}'] = np.asarray(x)
        flat[f'{stn}|{sn}|c'] = np.asarray(c)
    np.savez_compressed(outp, **flat); print('WROTE', outp, len(flat))
