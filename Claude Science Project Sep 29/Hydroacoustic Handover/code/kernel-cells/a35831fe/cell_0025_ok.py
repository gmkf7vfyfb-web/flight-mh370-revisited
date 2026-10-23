from pyproj import Geod
G=Geod(ellps='WGS84')
arr['t_arr']=arr.arrival_s_after_T0
sp=arr.dropna(subset=['implied_speed_km_s'])
print(sp.groupby('station').implied_speed_km_s.describe()[['count','mean','min','max']])
# per-event speed: median over picks
evsp=sp.groupby('index').implied_speed_km_s.agg(['median','std','count'])
# coverage spans
pw['t']=pw.window_start_utc.map(hms)
cov={}
for r,g in pw.groupby('receiver'):
    for p,gg in g.groupby('panel'): cov.setdefault(r,[]).append((gg.t.min(), gg.t.max()+55))
iw['t']=iw.window_start_utc.map(hms)
for (r,f),g in iw.groupby(['receiver','file']): cov.setdefault(str(r),[]).append((g.t.min(), g.t.max()+55))
for r in cov: 
    cov[r]=sorted(cov[r]); print(r, [(fmt(a),fmt(b)) for a,b in cov[r]][:12], len(cov[r]))