"""Royer 2016 Table 4 labelled set: one row per event x receiver.
Receivers: IMS H01W, H08S, H08N; IMOS loggers 3315, 3376 (Perth Canyon), 3250 (Scott Reef), 3274, 3275 (Portland);
OHASISBIO sites used by Royer; all island/coastal seismometers processed here.
Hydroacoustic receivers: predicted T = geodesic distance / 1.48 km/s from Royer's location and origin (no seismic leg).
Royer's observed arrivals (royer_arrivals table) are attached where Royer lists them, with residual obs - pred.
Event 16: island rows use the seismic relocation (ROY16S, 06_roy16_relocate.py) for prediction and matching.
Seismometers: predicted T = water leg/1.48 + seismic leg/6.0 + pooled station offset; detection, SNR, p_chance and
the max SNR in the T window (upper bound when not seen), from out/island-seismic-associations.csv and the SNR series."""
import sys, json, sqlite3, numpy as np, pandas as pd
sys.path.insert(0,'scripts'); import geom
from obspy import UTCDateTime as U
DB=sys.argv[1]; con=sqlite3.connect(DB)
ev=pd.read_sql('select * from dg_royer_2016_royer_events',con); arr=pd.read_sql('select * from dg_royer_2016_royer_arrivals',con)
rst=pd.read_sql('select * from dg_royer_2016_royer_stations',con).set_index('station')
site=pd.read_sql('select site_id,lat,lon,sensor_depth_m from site',con).set_index('site_id')
A=pd.read_pickle('data/assoc_resolved.pkl'); A=A[A.source.isin(['Royer 2016 Table 4','seismic relocation of Royer event 16'])]
Ao=A[A.path_class.isin(['clear','large attenuation'])&A.pred_T_utc.notna()&(A.event_id!='ROY16S')&(A.event_id!='ROY16')]
NPAIR=len(Ao); NOBS={t:int(((Ao.T_p_chance<t)&Ao.T_assigned_here).sum()) for t in (0.05,0.01)}
reloc=json.load(open('data/roy16_relocation.json')); reun=json.load(open('data/reunion_array.json'))
def snr_series(st):
    z=np.load(f'data/det/{st}_snr.npz'); return U(str(z['t0'])),{k:z[k] for k in z.files if k.startswith('b')}
cache={}
def maxsnr(st,t,w):
    if st not in cache: cache[st]=snr_series(st)
    t0,S=cache[st]; i=int(round(t-t0)); best=(np.nan,'',np.nan)
    for b,s in S.items():
        if i-w<0 or i+w>=len(s): continue
        seg=s[i-w:i+w+1]; k=int(np.argmax(seg))
        if not np.isfinite(best[0]) or seg[k]>best[0]: best=(float(seg[k]),b[1:].replace('_','-'),k-w)
    return best
rows=[]
HYD=['H01W','H08S','H08N','IMOS3315','IMOS3376','IMOS3250','IMOS3274','IMOS3275']
OH=['MAD','NCRO','WKER','SSEIR','SWAMS1','SWAMS2','SWAMS3','H01W1','H01W2','H01W3']
for _,e in ev.iterrows():
    eid='ROY%02d'%e['index']; t0=U(e.origin_date+'T'+e.origin_time_utc)
    base=dict(royer_event=int(e['index']),label=e.label if isinstance(e.label,str) else '',source_class=e.event_class,origin_utc=str(t0)[:21],
              lat=e.lat_deg,lon=e.lon_deg,err_lat_deg=e.err_lat_deg,err_lon_deg=e.err_lon_deg,err_time_s=e.err_time_s,n_royer_hydrophones=e.n_hydrophones)
    for r in HYD+OH:
        if r in site.index and r in HYD: la,lo=site.loc[r,'lat'],site.loc[r,'lon']; kind='IMS hydrophone' if r.startswith('H') else 'IMOS seabed logger'
        else: la,lo=rst.loc[r,'lat_deg'],rst.loc[r,'lon_deg']; kind='IMS hydrophone element' if r.startswith('H01W') else 'OHASISBIO hydrophone'
        p=geom.path(e.lat_deg,e.lon_deg,la,lo); tt=p['D']/geom.C_T
        o=arr[(arr['index']==e['index'])&(arr.station==r)]
        obs=o.arrival_utc.values[0] if len(o) and isinstance(o.arrival_utc.values[0],str) else ''
        if obs:
            tobs=U(e.origin_date+'T'+obs);
            if tobs<t0-3600: tobs+=86400
            if tobs-t0>43200: tobs-=86400
        rows.append(dict(**base,receiver=r,receiver_kind=kind,dist_km=p['D'],baz_at_receiver_deg=p['baz'],path_class=p['cls'],shallow_km=p['shallow_km'],
             pred_arrival_utc=str(t0+tt)[:21],royer_observed_utc=str(tobs)[:22] if obs else '',resid_obs_minus_pred_s=(tobs-(t0+tt)) if obs else np.nan,
             island_seen='',island_snr=np.nan,island_p_chance=np.nan,island_max_snr_in_window=np.nan,island_note=''))
    for _,a in A[A.event_id==(eid if eid!='ROY16' else 'ROY16S')].iterrows():
        if not isinstance(a.pred_T_utc,str): continue
        w=int(max(60,2.5*a.T_spread_s)); tp=U(a.pred_T_utc)+a.T_offset_s; m=maxsnr(a.station,tp,w)
        seen='yes' if (a.T_p_chance<0.05 and a.T_assigned_here) else ('shared: better explained by another source' if a.T_p_chance<0.05 else 'no')
        rows.append(dict(**base,receiver=a.station,receiver_kind='island/coastal seismometer',dist_km=a.dist_km,baz_at_receiver_deg=a.baz_deg,path_class=a.path_class,shallow_km=a.shallow_km,
             pred_arrival_utc=str(tp)[:21],royer_observed_utc='',resid_obs_minus_pred_s=(a.T_resid_s-a.T_offset_s) if a.T_p_chance<0.05 else np.nan,
             island_seen=seen,island_snr=a.T_snr if a.T_p_chance<0.05 else np.nan,island_p_chance=a.T_p_chance,island_max_snr_in_window=m[0],
             island_note=f'T window +/-{w} s; max SNR band {m[1]} at {m[2]:+d} s' if np.isfinite(m[0]) else 'no data'))
R=pd.DataFrame(rows)
# event-level assessment of the island check
summ=[]
for k,g in R.groupby('royer_event'):
    isl=g[g.receiver_kind=='island/coastal seismometer']; op=isl[isl.path_class.isin(['clear','large attenuation'])]
    seen=op[op.island_seen=='yes']; hy=g[g.receiver.str.startswith('H01W')&g.resid_obs_minus_pred_s.notna()]
    if k==16:
        b=reloc['best']; txt=(f"Supports: recorded as a local earthquake by GE.CISI, GE.UGM, AU.XMIS, AU.XMI (P and S). Seismic location {abs(b['lat']):.2f} S {b['lon']:.2f} E, "
              f"depth {b['depth_km']} km, origin {reloc['origin_minus_royer_s']:+.1f} s from Royer; {reloc['dist_best_to_royer_km']:.0f} km from Royer's location")
    elif len(seen):
        txt=f'Isolated match, not significant given {NPAIR} open-path pairs tested for events 1-15 and 17-20 ({NOBS[0.05]} assigned matches at p_chance < 0.05; {0.05*NPAIR:.0f} expected by chance): T seen at '+', '.join(f"{r.receiver} (SNR {r.island_snr:.1f}, p_chance {r.island_p_chance:.3f}, resid {r.resid_obs_minus_pred_s:+.0f} s)" for _,r in seen.iterrows())
        if k in (11,12): txt+=f"; Reunion array fit not resolved (back-azimuth bootstrap 95% range {reun['baz_boot_2p5']:.0f}-{reun['baz_boot_97p5']:.0f} deg); one detection serves C2 and C3"
    else:
        txt=f"Not tested with useful power: no island T at p_chance < 0.05 on {len(op)} open paths (no significant detection with limited power)"
    summ.append(dict(royer_event=k,label=g.label.iloc[0],source_class=g.source_class.iloc[0],origin_utc=g.origin_utc.iloc[0],lat=g.lat.iloc[0],lon=g.lon.iloc[0],
        n_island_open_paths=len(op),n_island_seen=len(seen),island_seen_at='; '.join(seen.receiver),
        median_resid_royer_H01W_obs_minus_rule_s=hy.resid_obs_minus_pred_s.median() if len(hy) else np.nan,
        pred_H01W_utc=g[g.receiver=='H01W'].pred_arrival_utc.iloc[0],pred_H08S_utc=g[g.receiver=='H08S'].pred_arrival_utc.iloc[0],
        H01W_path=g[g.receiver=='H01W'].path_class.iloc[0],H08S_path=g[g.receiver=='H08S'].path_class.iloc[0],island_check=txt))
S=pd.DataFrame(summ)
R.to_csv('out/royer-events-labelled-set.csv',index=False,float_format='%.5g'); S.to_csv('out/royer-events-island-check-summary.csv',index=False,float_format='%.5g')
oh=R[R.resid_obs_minus_pred_s.notna()&(R.receiver_kind!='island/coastal seismometer')]
print('Royer observed vs 1.48 rule: n',len(oh),'median',round(oh.resid_obs_minus_pred_s.median(),2),'sd',round(oh.resid_obs_minus_pred_s.std(),2),'min/max',round(oh.resid_obs_minus_pred_s.min(),1),round(oh.resid_obs_minus_pred_s.max(),1))
pd.set_option('display.width',250); pd.set_option('display.max_colwidth',200)
print(S[['royer_event','label','source_class','n_island_open_paths','n_island_seen','island_seen_at','median_resid_royer_H01W_obs_minus_rule_s','pred_H01W_utc','pred_H08S_utc','H08S_path']].to_string())
for _,r in S.iterrows(): print(r.royer_event,'|',r.island_check)
