"""CMST 2014-30 detections against island/coastal seismometers (exploratory).
For each CMST detection (receiver, time, bearing) the source is placed every 10 km along the bearing (50-6000 km,
WGS84 geodesic), origin = arrival - range/1.48 km/s. For each source point and seismometer with an open path
(clear or large attenuation), predicted T = origin + water/1.48 + seismic leg/6; a match is an unassigned or assigned
detection with onset within +/-150 s (or spanning the prediction). Reported: per station the best match along the
bearing (unassigned detections only); multi-station coincidences (>= 2 stations matched at the same range,
p_chance < 0.05 each), counted for all detections and for unassigned detections only; and the same counts for control times (arrival shifted by +/-1500 s, +/-3000 s) to show the chance level."""
import sys, numpy as np, pandas as pd, json
sys.path.insert(0,'scripts'); import geom
from obspy import UTCDateTime as U
D=pd.read_pickle('data/det_resolved.pkl'); st=pd.read_csv('data/stations.csv').set_index('station')
D['on_s']=pd.to_datetime(D.onset_utc,format='ISO8601').values.astype('datetime64[ms]').astype(np.int64)/1000.
D['off_s']=pd.to_datetime(D.end_utc,format='ISO8601').values.astype('datetime64[ms]').astype(np.int64)/1000.
SPAN=5*86400; W=150.
seis=[s for s in st.index if st.loc[s,'kind']=='seismometer' and s in set(D.station)]
rate={(s,b):np.sort(g.peak_snr.values) for (s,b),g in D.groupby(['station','band'])}
def pch(s,b,snr): a=rate[(s,b)]; return 1-np.exp(-(len(a)-np.searchsorted(a,snr))/SPAN*2*W)
CM=[('H01W',U('2014-03-08T01:34:50'),301.6,'detection of interest'),('H08S',U('2014-03-08T00:11:24'),168.05,'discrete detection (00:11-00:12)'),
    ('H08S',U('2014-03-08T01:58:55'),93.0,'discrete detection'),('H01W',U('2014-03-08T04:59:21'),210.2,'clock cross-check (high SNR)'),('H01W',U('2014-03-08T05:14:28'),208.5,'clock cross-check')]
rngs=np.arange(50,6001,10.)
on={k:(g.on_s.values,g.off_s.values,g.peak_snr.values,g.band.values,g.onset_utc.values,g.assigned.values) for k,g in D.groupby('station')}
def geometry(rcv,brg):
    la0,lo0=st.loc[rcv,'lat'],st.loc[rcv,'lon']
    lo,la,_=geom.geod.fwd(np.full(len(rngs),lo0),np.full(len(rngs),la0),np.full(len(rngs),brg),rngs*1000)
    G=[]
    for r,a,o in zip(rngs,la,lo):
        zz=geom.z(np.array([a]),np.array([o]))[0]
        if not np.isfinite(zz) or zz>-200: continue   # source must be in water deeper than 200 m
        for s_ in seis:
            p=geom.path(a,o,st.loc[s_,'lat'],st.loc[s_,'lon'],step_km=2.0)
            if p['cls'] in ('clear','large attenuation'): G.append((r,a,o,s_,geom.t_travel(p),p['cls']))
    return pd.DataFrame(G,columns=['range_km','src_lat','src_lon','station','tt_s','path_class'])
def match(G,t_arr):
    out=[]
    for _,g in G.iterrows():
        o,f,snr,b,ou,asg=on[g.station]; ts=t_arr.timestamp-g.range_km/geom.C_T+g.tt_s
        m=((o>=ts-W)&(o<=ts+W))|((o<=ts)&(f>=ts)&(o>=ts-W-600))
        if not m.any(): continue
        idx=np.where(m)[0]; pcs=np.array([pch(g.station,b[i],snr[i]) for i in idx]); i=idx[np.argmin(pcs)]
        out.append(dict(range_km=g.range_km,src_lat=g.src_lat,src_lon=g.src_lon,station=g.station,path_class=g.path_class,
            origin_utc=str(t_arr-g.range_km/geom.C_T)[:19],
            pred_T_utc=str(U(ts))[:19],det_onset_utc=ou[i],resid_s=o[i]-ts,snr=snr[i],band=b[i],p_chance=pcs.min(),assigned=asg[i]))
    return pd.DataFrame(out)
def coinc(X,unassigned_only):
    if not len(X): return pd.Series(dtype=int)
    Y=X[(X.p_chance<0.05)&((X.assigned=='') if unassigned_only else True)]
    c=Y.groupby('range_km').station.nunique(); return c[c>=2]
rows=[]; summ=[]
for rcv,t,brg,lab in CM:
    G=geometry(rcv,brg); res={sh:match(G,t+sh) for sh in [0,-3000,-1500,1500,3000]}
    for sh,X in res.items():
        if len(X): X['shift_s']=sh; X['cmst']=f'{rcv} {str(t)[11:19]} {brg} deg ({lab})'; rows.append(X)
    X=res[0]; cu=coinc(X,True); ca=coinc(X,False)
    ctl_u=[len(coinc(res[s],True)) for s in [-3000,-1500,1500,3000]]; ctl_a=[len(coinc(res[s],False)) for s in [-3000,-1500,1500,3000]]
    un=X[(X.p_chance<0.05)&(X.assigned=='')] if len(X) else X
    best=un.sort_values('p_chance').groupby('station').head(1).sort_values('p_chance') if len(un) else un
    summ.append(dict(cmst=f'{rcv} {str(t)[11:19]} {brg} deg ({lab})',n_source_points_in_water=int(G.range_km.nunique()),
        n_ranges_2plus_stations_any=len(ca),control_mean_any=float(np.mean(ctl_a)),
        n_ranges_2plus_stations_unassigned=len(cu),control_mean_unassigned=float(np.mean(ctl_u)),control_counts_unassigned=';'.join(map(str,ctl_u)),
        ranges_2plus_unassigned_km=';'.join(f'{int(r)}({n})' for r,n in cu.items())[:300],
        best_unassigned_per_station='; '.join(f"{r.station} r={r.range_km:.0f}km {r.det_onset_utc[11:19]} SNR{r.snr:.1f} p_chance{r.p_chance:.3f} res{r.resid_s:+.0f}s" for _,r in best.head(8).iterrows())))
R=pd.concat(rows,ignore_index=True); R.to_csv('out/island-seismic-cmst-bearing-scan.csv',index=False,float_format='%.5g')
S=pd.DataFrame(summ); S.to_csv('out/island-seismic-cmst-summary.csv',index=False)
for _,r in S.iterrows(): print(r.to_dict(),'\n')
# H08S 01:58:55 against Royer event 16
P=pd.read_csv('data/pred_arrivals.csv')
for e in ['ROY16','ROY16S']:
    q=P[(P.event_id==e)&(P.station=='H08S')].iloc[0]; print(e,'pred H08S',q.pred_T_utc,'obs-pred',round(U('2014-03-08T01:58:55')-U(q.pred_T_utc),1),'baz at H08S',round(q.baz_deg,1),'path',q.path_class)
