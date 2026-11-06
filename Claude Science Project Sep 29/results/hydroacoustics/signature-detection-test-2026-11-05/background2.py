import sys, glob, os, numpy as np, pandas as pd
sys.path.insert(0,'.')
import sigdet as SD
D=sys.argv[1]; tag=sys.argv[2]
STATS={'L_d0':'d0','L_d1':'d1','L_d2':'d2','L_dive':'dive','L_ditch':'ditch','S_d1':'s_d1','S_d2':'s_d2','S_dive':'s_dive','S_ditch':'s_ditch'}
for c in ('quake','whale','airgun','ship','ice'):
    STATS[f'L_c_{c}']=f'cls_{c}'; STATS[f'S_c_{c}']=f'scls_{c}'
LOOK=int(round(120/SD.DT))
bg=[]
for fn in sorted(glob.glob(f'{D}/*.npz')):
    k=os.path.basename(fn)[:-4]; z=np.load(fn); st=k[:4]
    A={s:np.asarray(z[v],float) for s,v in STATS.items()}
    bad=z['gap'].astype(bool)
    for s in A: bad|=~np.isfinite(A[s])
    for i in range(0,len(z['t'])-LOOK,LOOK):
        sl=slice(i,i+LOOK)
        if bad[sl].any(): continue
        bg.append(dict(st=st,rec=k,i=i,**{s:A[s][sl].max() for s in A}))
bg=pd.DataFrame(bg); bg.to_csv(f'background_looks_{tag}.csv',index=False)
print(bg.groupby('st').size(), bg.groupby('st').rec.nunique())
Q={'known_time_0.05':0.95,'window30min_0.05':1-0.05/15,'blind_1_per_day':1-1/720}
rows=[dict(st=st,stat=s,level=qn,thr=np.quantile(g[s],q),n_looks=len(g)) for st,g in bg.groupby('st') for s in STATS for qn,q in Q.items()]
th=pd.DataFrame(rows); th.to_csv(f'thresholds_{tag}.csv',index=False)
print(th[th.stat.isin(['L_d0','L_d1','S_d1'])].pivot_table(index=['st','stat'],columns='level',values='thr').round(2))
