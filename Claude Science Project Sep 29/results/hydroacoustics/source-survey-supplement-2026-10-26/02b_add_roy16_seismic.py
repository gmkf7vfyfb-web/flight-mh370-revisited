"""Append Royer event 16 at its seismic relocation (06_roy16_relocate.py) as a known source, so that its P, S and T
arrivals at island stations are predicted from the seismic hypocentre and origin time."""
import sys, json, numpy as np, pandas as pd
sys.path.insert(0,'scripts'); import geom
from obspy import UTCDateTime as U
from obspy.taup import TauPyModel
r=json.load(open('data/roy16_relocation.json'))['best']
t0=U('2014-03-08T01:15:00')+r['origin_s_after_0115']
E=pd.read_csv('data/events_all.csv'); E=E[E.event_id!='ROY16S']
E=pd.concat([E,pd.DataFrame([dict(event_id='ROY16S',origin_utc=str(t0)[:22],lat=r['lat'],lon=r['lon'],depth_km=r['depth_km'],mag=np.nan,magtype='',
     place='Royer 2016 event 16 at seismic relocation (this note)',source='seismic relocation of Royer event 16',source_class='earthquake')])],ignore_index=True)
E.to_csv('data/events_all.csv',index=False)
st=pd.read_csv('data/stations.csv'); P=pd.read_csv('data/pred_arrivals.csv'); P=P[P.event_id!='ROY16S']
mod=TauPyModel('iasp91'); out=[]
for _,s in st.iterrows():
    p=geom.path(r['lat'],r['lon'],s.lat,s.lon)
    if s.kind=='hydrophone': p['water_km']=p['D']; p['seis_km']=0.0
    tt=geom.t_travel(p) if p['cls'] not in ('no deep water','no bathymetry') else np.nan
    a=mod.get_travel_times(r['depth_km'],p['D']/111.195,phase_list=['ttbasic'])
    tp=min(q.time for q in a if q.name[0] in 'Pp' or q.name.startswith('PK')); ts=[q.time for q in a if q.name[0] in 'Ss']
    out.append(dict(event_id='ROY16S',station=s.station,dist_km=p['D'],baz_deg=p['baz'],path_class=p['cls'],seis_leg_km=p['seis_km'],water_leg_km=p['water_km'],
        shallow_km=p['shallow_km'],obst_lat=p['obst_lat'],obst_lon=p['obst_lon'],src_water_depth_m=p['src_depth_m'],
        pred_T_utc=str(t0+tt)[:22] if np.isfinite(tt) else '',pred_P_utc=str(t0+tp)[:22],pred_S_utc=str(t0+min(ts))[:22] if ts else ''))
pd.concat([P,pd.DataFrame(out)],ignore_index=True).to_csv('data/pred_arrivals.csv',index=False)
print('added ROY16S', str(t0), 'H08S pred T', [o['pred_T_utc'] for o in out if o['station']=='H08S'], 'H01W', [o['pred_T_utc'] for o in out if o['station']=='H01W'])
