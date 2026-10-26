"""Predicted arrivals at island/coastal seismometers and hydroacoustic receivers.
Events: (1) earthquakes in known-events-6-10mar2014.csv; (2) USGS global M>=4.5, 5 Mar 12:00 - 11 Mar,
not already in (1) (60 s / 150 km rule); (3) Royer 2016 Table 4 (20 events, hydro_data.sqlite).
T phase: water leg / 1.48 km/s + seismic leg / 6 km/s (geom.py, GEBCO_2026 path class).
P and S: first P-type and S-type arrivals, TauP iasp91, interpolated from a distance x depth table."""
import sys, glob, numpy as np, pandas as pd, sqlite3
sys.path.insert(0,'scripts'); import geom
from obspy import read_inventory, UTCDateTime as U
from obspy.taup import TauPyModel
from scipy.interpolate import RegularGridInterpolator
KE=sys.argv[1]; DB=sys.argv[2]
# stations
rows=[]
for x in sorted(glob.glob('data/resp/*.xml')):
    inv=read_inventory(x); n=inv[0]; s=n[0]; c=s[0]
    rows.append(dict(station=f'{n.code}.{s.code}',lat=c.latitude,lon=c.longitude,elev_m=c.elevation,kind='seismometer'))
st=pd.DataFrame(rows)
site=pd.read_sql('select site_id,lat,lon,sensor_depth_m from site',sqlite3.connect(DB))
hyd=site[site.site_id.isin(['H01W','H08S','H08N','IMOS3315','IMOS3376','IMOS3250','IMOS3274','IMOS3275'])].rename(columns={'site_id':'station'})
hyd['kind']='hydrophone'; hyd['elev_m']=-hyd.sensor_depth_m
st=pd.concat([st,hyd[['station','lat','lon','elev_m','kind']]],ignore_index=True)
st.to_csv('data/stations.csv',index=False)
# events
ke=pd.read_csv(KE); eq=ke[ke.source_class=='earthquake'].copy()
m=eq['size'].str.extract(r'^(\S+)\s+([-\d.]+)'); eq['magtype']=m[0]; eq['mag']=pd.to_numeric(m[1],errors='coerce')
E=pd.DataFrame(dict(event_id=eq.event_id,origin_utc=eq.time_utc,lat=eq.lat,lon=eq.lon,depth_km=eq.depth_km.fillna(10),mag=eq.mag,magtype=eq.magtype,
                    place=eq.place,source='known-events table',source_class='earthquake'))
g=pd.read_csv('data/cat/usgs_global_M4.5_20140305T12_20140311.csv')
tE=pd.to_datetime(E.origin_utc,format='ISO8601').values.astype('datetime64[s]').astype(float)
keep=[]
for i,r in g.iterrows():
    tt=pd.Timestamp(r.time_utc).to_datetime64().astype('datetime64[s]').astype(float)
    close=np.abs(tE-tt)<60
    dup=any(geom.dist_az(r.lat,r.lon,E.lat.values[j],E.lon.values[j])[0]<150 for j in np.where(close)[0])
    if not dup: keep.append(i)
g=g.loc[keep]
E=pd.concat([E,pd.DataFrame(dict(event_id=['USG%03d'%i for i in range(len(g))],origin_utc=g.time_utc.values,lat=g.lat.values,lon=g.lon.values,depth_km=g.depth_km.values,
          mag=g.mag.values,magtype=g.magtype.values,place=g.place.values,source='USGS global M>=4.5',source_class='earthquake'))],ignore_index=True)
rv=pd.read_sql('select * from dg_royer_2016_royer_events',sqlite3.connect(DB))
R=pd.DataFrame(dict(event_id=['ROY%02d'%i for i in rv['index']],origin_utc=(rv.origin_date+'T'+rv.origin_time_utc).values,lat=rv.lat_deg,lon=rv.lon_deg,depth_km=0.0,
   mag=np.nan,magtype='',place='Royer 2016 Table 4 event '+rv['index'].astype(str)+(' ('+rv.label.fillna('')+')').str.replace(r' \(\)','',regex=True),
   source='Royer 2016 Table 4',source_class=rv.event_class))
E=pd.concat([E,R],ignore_index=True); E.to_csv('data/events_all.csv',index=False)
print('stations',len(st),'events',len(E),E.source.value_counts().to_dict())
# TauP table
mod=TauPyModel('iasp91'); deps=np.array([0,10,20,35,50,70,100,150,200,300,450,600,700.]); dists=np.arange(0,180.01,0.5)
TP=np.full((len(dists),len(deps)),np.nan); TS=TP.copy()
for j,d in enumerate(deps):
    for i,x in enumerate(dists):
        a=mod.get_travel_times(d,x,phase_list=['ttbasic'])
        p=[q.time for q in a if q.name[0] in 'Pp' or q.name.startswith('PK')]; s=[q.time for q in a if q.name[0] in 'Ss']
        TP[i,j]=min(p) if p else np.nan; TS[i,j]=min(s) if s else np.nan
fP=RegularGridInterpolator((dists,deps),TP,bounds_error=False); fS=RegularGridInterpolator((dists,deps),TS,bounds_error=False)
out=[]
for _,e in E.iterrows():
    t0=U(e.origin_utc)
    for _,s in st.iterrows():
        p=geom.path(e.lat,e.lon,s.lat,s.lon)
        if s.kind=='hydrophone':  # receiver in the water: no seismic leg
            p['water_km']=p['D']; p['seis_km']=0.0
        tt=geom.t_travel(p) if p['cls'] not in ('no deep water','no bathymetry') else np.nan
        ddeg=p['D']/111.195; dep=min(max(e.depth_km,0),700)
        out.append(dict(event_id=e.event_id,station=s.station,dist_km=p['D'],baz_deg=p['baz'],path_class=p['cls'],seis_leg_km=p['seis_km'],water_leg_km=p['water_km'],
            shallow_km=p['shallow_km'],obst_lat=p['obst_lat'],obst_lon=p['obst_lon'],src_water_depth_m=p['src_depth_m'],
            pred_T_utc=str(t0+tt)[:22] if np.isfinite(tt) else '',pred_P_utc=str(t0+float(fP((ddeg,dep))))[:22],pred_S_utc=str(t0+float(fS((ddeg,dep))))[:22] if np.isfinite(fS((ddeg,dep))) else ''))
P=pd.DataFrame(out); P.to_csv('data/pred_arrivals.csv',index=False)
print(len(P), P.path_class.value_counts().to_dict())
