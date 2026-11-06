import sys, glob, os, numpy as np, pandas as pd
sys.path.insert(0,'.')
from obspy import UTCDateTime
import sigdet as SD
STATS={'L_d0':'d0','L_d1':'d1','L_d2':'d2','S_d1':'s_d1','S_d2':'s_d2','L_quake':'cls_quake','S_quake':'scls_quake','L_dive':'dive','L_ditch':'ditch'}
LOOK=int(round(120/SD.DT))
ev={}
for st in ('H01W','H08S'):
    d=pd.read_csv(f'bc/out/eq_{st}_events.csv'); d=d[d.status=='ok']
    for _,r in d.iterrows(): ev[f'{st}1_{r.evid}']=r
bg=[]; kn=[]
for fn in sorted(glob.glob('scores/*.npz')):
    k=os.path.basename(fn)[:-4]; z=np.load(fn); st=k[:4]; r=ev[k]
    t=z['t']; t0=UTCDateTime(str(z['start'])); tev=UTCDateTime(r.t_pred)-t0
    A={s:np.asarray(z[v],float) for s,v in STATS.items()}
    bad=z['gap'].astype(bool)
    for s in A: bad|=~np.isfinite(A[s])
    excl=(t>=tev-120)&(t<=tev+420)
    # background looks: non-overlapping 120 s blocks, clear of the event zone and of gaps
    for i in range(0,len(t)-LOOK,LOOK):
        sl=slice(i,i+LOOK)
        if excl[sl].any() or bad[sl].any(): continue
        bg.append(dict(st=st,rec=k,i=i,**{s:A[s][sl].max() for s in A}))
    look=(t>=tev-40)&(t<=tev+80)
    if look.sum()>200 and not bad[look].any():
        kn.append(dict(st=st,rec=k,snr_db=r.snr_db,mag=r.mag,dist_km=r.dist_km,dt_pk=r.dt_pk_s,**{s:A[s][look].max() for s in A}))
bg=pd.DataFrame(bg); kn=pd.DataFrame(kn)
bg.to_csv('background_looks.csv',index=False); kn.to_csv('known_events_raw.csv',index=False)
print(bg.groupby('st').size(), kn.groupby('st').size())
# thresholds
Q={'known_time_0.05':0.95,'window30min_0.05':1-0.05/15,'blind_1_per_day':1-1/720}
rows=[]
for st,g in bg.groupby('st'):
    for s in STATS:
        for qn,q in Q.items():
            rows.append(dict(st=st,stat=s,level=qn,thr=np.quantile(g[s],q),n_looks=len(g)))
th=pd.DataFrame(rows); th.to_csv('thresholds.csv',index=False)
print(th.pivot_table(index=['st','stat'],columns='level',values='thr').round(2))
