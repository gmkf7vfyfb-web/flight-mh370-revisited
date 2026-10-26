"""Build the deliverable tables from data/det/*.csv, data/assoc_all.csv, data/assoc_control_shifted.csv.
Conflict rule (event 16 is represented by its seismic relocation ROY16S; an assignment is carried to the
overlapping detection in the other band): a detection claimed by several (event, phase) pairs is assigned to the claim with the lowest
p_chance; ties go to P/S over T and then to the smaller |residual - offset|. Other claims are listed as competing.
A claim counts as an association when p_chance < 0.05 (P, S) or < 0.05 (T)."""
import sys, glob, json, numpy as np, pandas as pd
sys.path.insert(0,'scripts'); import geom
A=pd.read_csv('data/assoc_all.csv'); Ctl=pd.read_csv('data/assoc_control_shifted.csv')
D=pd.concat([pd.read_csv(f) for f in sorted(glob.glob('data/det/*.csv'))],ignore_index=True)
D['det_id']=D.station+'|'+D.band+'|'+D.onset_utc
PC=0.05
claims=[]
for ph in ['T','P','S']:
    m=A[A[f'{ph}_det_id'].notna()]
    for _,r in m.iterrows():
        claims.append(dict(det_id=r[f'{ph}_det_id'],event_id=r.event_id,phase=ph,p_chance=r[f'{ph}_p_chance'],
            resid=r[f'{ph}_resid_s']-(r.T_offset_s if ph=='T' else 0),source=r.source,source_class=r.source_class))
CL=pd.DataFrame(claims); CL=CL[(CL.p_chance<PC)&(CL.event_id!='ROY16')]   # event 16 is represented by its seismic relocation ROY16S
CL['prio']=CL.phase.map({'P':0,'S':0,'T':1}); CL['ar']=CL.resid.abs()
CL=CL.sort_values(['det_id','p_chance','prio','ar'])
win=CL.groupby('det_id').head(1).set_index('det_id')
comp=CL.groupby('det_id').apply(lambda g: '; '.join(f"{r.phase}:{r.event_id}(p={r.p_chance:.3f},res={r.resid:+.0f}s)" for _,r in g.iloc[1:].iterrows()) if len(g)>1 else '')
# carry an assignment to the overlapping detection of the other band at the same station
D['on']=pd.to_datetime(D.onset_utc,format='ISO8601'); D['off']=pd.to_datetime(D.end_utc,format='ISO8601')
extra={}
for k in win.index:
    st,b,on=k.split('|'); r=D[(D.det_id==k)].iloc[0]
    o=D[(D.station==st)&(D.band!=b)&(D.on<=r.off)&(D.off>=r.on)]
    for kk in o.det_id:
        if kk not in win.index and kk not in extra: extra[kk]=win.loc[k]
if extra: win=pd.concat([win,pd.DataFrame(extra).T])
D['assigned']=D.det_id.map(lambda k: f"{win.loc[k,'phase']}:{win.loc[k,'event_id']}" if k in win.index else '')
D['assigned_source']=D.det_id.map(lambda k: win.loc[k,'source'] if k in win.index else '')
D['assigned_p_chance']=D.det_id.map(lambda k: win.loc[k,'p_chance'] if k in win.index else np.nan)
D['competing_claims']=D.det_id.map(lambda k: comp.get(k,''))
cols=['station','channel','fs_hz','band','onset_utc','end_utc','duration_s','peak_utc','peak_snr','peak_freq_hz','rms_band_nm_s','hf_lf_rel','assigned','assigned_source','assigned_p_chance','competing_claims','det_id']
D[cols].sort_values(['station','band','onset_utc']).to_csv('out/island-seismic-detections.csv',index=False,float_format='%.4g')
print('detections',len(D),'assigned',(D.assigned!='').sum(), D.assign(ph=D.assigned.str[:1]).ph.value_counts().to_dict())
# associations table: keep the winner flag per phase
for ph in ['T','P','S']:
    A[f'{ph}_assigned_here']=[(isinstance(d,str) and d in win.index and win.loc[d,'event_id']==e and win.loc[d,'phase']==ph) for d,e in zip(A[f'{ph}_det_id'],A.event_id)]
def verdict(r):
    if r.path_class in ('blocked','no deep water','no bathymetry'): base='T path '+r.path_class
    else: base='T path '+r.path_class
    if r.T_p_chance<PC and r.T_assigned_here: return base+'; T seen'
    if r.T_p_chance<PC: return base+'; T window holds a detection explained better by another source'
    return base+'; T not seen'
A['T_verdict']=A.apply(verdict,axis=1)
keep=['event_id','source','source_class','origin_utc','mag','magtype','depth_km','place','station','dist_km','baz_deg','path_class','seis_leg_km','water_leg_km','shallow_km',
      'pred_T_utc','T_offset_s','T_spread_s','T_win_s','T_onset_utc','T_resid_s','T_snr','T_dur_s','T_fpk_hz','T_p_chance','T_assigned_here','T_verdict',
      'pred_P_utc','P_onset_utc','P_resid_s','P_snr','P_p_chance','P_assigned_here','pred_S_utc','S_onset_utc','S_resid_s','S_snr','S_p_chance','S_assigned_here']
A[keep].to_csv('out/island-seismic-associations.csv',index=False,float_format='%.4g')
A.to_pickle('data/assoc_resolved.pkl'); D.to_pickle('data/det_resolved.pkl')
# detection levels: pooled and per station, D > 600 km, path clear/large attenuation, catalogued earthquakes only
def sel(X): return X[(X.source!='Royer 2016 Table 4')&X.path_class.isin(['clear','large attenuation'])&(X.dist_km>600)&X.mag.notna()&X.pred_T_utc.notna()].copy()
a=sel(A); c=sel(Ctl)
Mb=[(0,3.5,'M<3.5'),(3.5,4.0,'M3.5-4.0'),(4.0,4.5,'M4.0-4.5'),(4.5,9,'M>=4.5')]; Db=[(600,1500,'600-1500 km'),(1500,3000,'1500-3000 km'),(3000,20000,'>3000 km')]
rows=[]
for scope,g,gc in [('all stations',a,c)]+[(s,a[a.station==s],c[c.station==s]) for s in sorted(a.station.unique())]:
    for m0,m1,ml in Mb:
        for d0,d1,dl in Db:
            x=g[(g.mag>=m0)&(g.mag<m1)&(g.dist_km>=d0)&(g.dist_km<d1)]; y=gc[(gc.mag>=m0)&(gc.mag<m1)&(gc.dist_km>=d0)&(gc.dist_km<d1)]
            for thr in [0.05,0.01]:
                k=(x.T_p_chance<thr).sum(); kc=(y.T_p_chance<thr).sum()
                rows.append(dict(scope=scope,mag_bin=ml,dist_bin=dl,p_chance_threshold=thr,n_pairs=len(x),n_seen=k,frac_seen=k/len(x) if len(x) else np.nan,
                                 n_control=len(y),frac_control=kc/len(y) if len(y) else np.nan,excess=(k/len(x)-kc/len(y)) if len(x) and len(y) else np.nan,
                                 seen_events='; '.join(f"{r.event_id} {r.station} M{r.mag:g} {r.dist_km:.0f}km SNR{r.T_snr:.1f}" for _,r in x[x.T_p_chance<thr].iterrows()) if scope=='all stations' else ''))
L=pd.DataFrame(rows); L=L[L.n_pairs>0]; L.to_csv('out/island-seismic-detection-levels.csv',index=False,float_format='%.4g')
print(L[(L.scope=='all stations')].drop(columns='seen_events').to_string())
