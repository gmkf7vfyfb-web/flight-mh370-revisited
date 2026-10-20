
import json, tomllib, numpy as np, pandas as pd
from scipy.optimize import least_squares
R = "repo/Claude Science Project Sep 29/results/drift-runj-2026-10-17/"
REB = '/Users/pete/Downloads/mh370-exchange/debris-drift/runA-rebuilt'
G = dict(lat0=-41.166666666666664, lon0=83.96226004720266, dlat=0.5, dlon=0.5856322967993869, nlat=41, nlon=38)
NC = G['nlat']*G['nlon']; NL = G['nlon']; LREF = -125.0
def nodes(model, col='ln_l'):
    df = pd.read_csv(f'{REB}/debris-drift-production-{model}/merged/nodes.csv'); v = np.full(NC, np.nan)
    ok = np.isfinite(df[col].values); v[df.node.values[ok]] = df[col].values[ok]; return v
BW = {'h50':'ln_l','h25':'ln_l_h25','h100':'ln_l_h100','h200':'ln_l_h200'}
NODES = {(m,b): nodes(m,c) for m in ('glorys12','globcurrent') for b,c in BW.items()}
cfg = tomllib.load(open(R+'australia-160E/aus160-globcurrent.toml','rb'))['hypotheses']['debris-drift']
SEGS = [s['name'] for s in cfg['segments']]; CLS = ['flaperon','low_exposure_exterior','high_windage_interior']
lvl = {'B': {d['segment']: d['ln_mean_by_period'][0] for d in cfg['levels']['segment_ln_mean_by_period']}}
lvl['C'] = {d['segment']: d['ln_mean_by_period'][0] for d in next(a for a in cfg['levels']['alternatives'] if a['name']=='C')['segment_ln_mean_by_period']}
POP = [s for s in SEGS if s.endswith('city-inner')]
def deltas(path):
    df = pd.read_csv(path); p = {s: np.mean([df[f'p_{c}_{i}'] for c in CLS],0) for i,s in enumerate(SEGS)}
    F = sum(p[s] for s in SEGS[:6]); W = {o: sum(np.exp(lvl[o][s])*p[s] for s in SEGS[6:]) for o in lvl}
    Dm = {'B': df.ln_l-df.ln_l_lev_off, 'C': df.ln_l_lev_C-df.ln_l_lev_off, 'A': df.ln_l_lev_A-df.ln_l_lev_off}
    ok = np.isfinite(F)&(F>0)&np.isfinite(Dm['B'])&np.isfinite(Dm['C'])
    fit = least_squares(lambda x: np.concatenate([(-x[0]*np.log1p(W[o]/(x[1]*F))-Dm[o])[ok] for o in ('B','C')]),[3.5,0.2],bounds=([0.01,1e-4],[50,50]))
    k,c = fit.x; Dpop = -k*np.log1p(sum(p[s] for s in POP)/(c*F))
    return df.node.values.astype(int), {**{o: np.asarray(v,float) for o,v in Dm.items()}, 'populated-only (reconstructed)': np.asarray(Dpop)}, (k,c)
def spread_to(plat, plon, d, alat, alon):
    dx = (alon[:,None]-plon[None])*111.2*np.cos(np.radians(alat[:,None])); dy = (alat[:,None]-plat[None])*111.2
    dist = np.hypot(dx,dy); ok = np.isfinite(d); dist[:,~ok] = np.inf
    nn = np.argsort(dist,1)[:,:8]; dd = np.take_along_axis(dist,nn,1); w = 1/np.maximum(dd,1.0)**2
    out = (w*d[nn]).sum(1)/w.sum(1); ex = dd[:,0]<1e-6; out[ex] = d[nn[ex,0]]; return out
alat_n = G['lat0']+(np.arange(NC)//NL)*G['dlat']; alon_n = G['lon0']+(np.arange(NC)%NL)*G['dlon']
DEL = {}; KC = {}
for m in ('glorys12','globcurrent'):
    pn, Ds, KC[m] = deltas(R+f'australia-160E/aus160-{m}/nodes.csv')
    plat = G['lat0']+(pn//NL)*G['dlat']; plon = G['lon0']+(pn%NL)*G['dlon']
    DEL[m] = {o: spread_to(plat,plon,v,alat_n,alon_n) for o,v in Ds.items()}
def node_L(m, bw='h50', opt='none'):
    if m == 'mean':
        a, b = node_L('glorys12',bw,opt), node_L('globcurrent',bw,opt)
        return np.where(np.isfinite(a)&np.isfinite(b), 0.5*(a+b), np.nan)
    v = NODES[(m,bw)] + (0 if opt in ('none','off') else DEL[m][opt]); return np.exp(v-LREF)
def corners(lat, lon):
    lat = np.atleast_1d(lat); lon = np.atleast_1d(lon)
    fi = (lat-G['lat0'])/G['dlat']; fj = (lon-G['lon0'])/G['dlon']
    i = np.minimum(np.floor(fi).astype(int), G['nlat']-2); j = np.minimum(np.floor(fj).astype(int), G['nlon']-2)
    ti, tj = fi-i, fj-j
    W = np.stack([(1-ti)*(1-tj), ti*(1-tj), (1-ti)*tj, ti*tj],1); cid = i*NL+j
    nid = np.stack([cid, cid+NL, cid+1, cid+NL+1],1); return nid, W
def lnL_at(lat, lon, m, bw='h50', opt='none'):
    Ln = node_L(m,bw,opt); nid, W = corners(lat,lon); v = Ln[nid]
    return np.log((W*v).sum(1)) + LREF   # NaN if any corner missing
