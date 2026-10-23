
import numpy as np, json, pathlib, time
EX = pathlib.Path('/Users/pete/Downloads/mh370-exchange')
z = np.load(EX/'searched-areas/run-j-supplement/arc-grid.npz')
arc = z['arc']; south, west, step = float(z['south']), float(z['west']), float(z['step'])
lats_g = south + step*np.arange(arc.shape[0]); lons_g = west + step*np.arange(arc.shape[1])
# arc value at a point west of the arc at 35S: find zero crossing along row
def arc_lon(lat, off=0.0):
    i = int(round((lat-south)/step)); row = arc[i]-off
    s = np.where(np.diff(np.sign(row))!=0)[0]
    out=[]
    for k in s:
        x0,x1=lons_g[k],lons_g[k+1]; y0,y1=row[k],row[k+1]
        out.append(x0 - y0*(x1-x0)/(y1-y0))
    return out
for lat in (-40,-35,-30,-25,-20,-15):
    print(lat, arc_lon(lat), 'arc west-of-arc sign:', np.sign(arc[int(round((lat-south)/step)), int(round((arc_lon(lat)[0]-2-west)/step))]))

# prior contour from one seed per stratum
strata = ['run-j-waypoints','run-j-free','run-j-descent-climb','run-j-repro-radar']
def wq(x,w,qs):
    o=np.argsort(x); c=np.cumsum(w[o]); c/=c[-1]; return x[o][np.searchsorted(c,qs)]
res={}
for st in strata:
    sd = EX/'end-of-flight/run-j'/st/'seed-1'
    cols = open(sd/'COLUMNS.txt').read().split()
    X = np.load(sd/'impacts32.npy', mmap_mode='r')
    lat = np.asarray(X[:,cols.index('latitude_deg')],float); w = np.asarray(X[:,cols.index('weight')],float)
    ad = np.asarray(X[:,cols.index('arc_distance_nm')],float)
    ok = np.isfinite(lat)&np.isfinite(w)&np.isfinite(ad)
    lat,w,ad = lat[ok],w[ok],ad[ok]
    r = {'n':int(ok.sum()), 'lat_q': wq(lat,w,[0.005,0.01,0.05,0.5,0.95,0.99,0.995]).round(2).tolist(),
         'arc_q': wq(ad,w,[0.005,0.01,0.05,0.25,0.5,0.75,0.95,0.99,0.995]).round(1).tolist(),
         'mass_|ad|>45': float(w[np.abs(ad)>45].sum()/w.sum()), 'mass_ad<-45': float(w[ad<-45].sum()/w.sum()), 'mass_ad>45': float(w[ad>45].sum()/w.sum()),
         'mass_|ad|>15': float(w[np.abs(ad)>15].sum()/w.sum())}
    # per option posterior
    for opt in ['loglik:r600/no-offset','loglik:both/no-offset','loglik:r600/inflated']:
        ll = np.asarray(X[:,cols.index(opt)],float)[ok]; ww = w*np.exp(ll-np.nanmax(ll)); ww=np.nan_to_num(ww)
        r[opt]= wq(lat,ww,[0.005,0.01,0.5,0.99,0.995]).round(2).tolist()
    res[st]=r; print(st, json.dumps(r))
# supplement
s = np.load(EX/'end-of-flight/run-j-supplement/reduced/impacts-ruleB.npz'); print(s.files[:5])
