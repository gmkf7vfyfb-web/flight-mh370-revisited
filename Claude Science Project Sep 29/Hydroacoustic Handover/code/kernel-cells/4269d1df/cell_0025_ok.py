
import subprocess, sys
try:
    from geographiclib.geodesic import Geodesic
except ImportError:
    subprocess.run([sys.executable,"-m","pip","install","-q","geographiclib"]); from geographiclib.geodesic import Geodesic
import json, datetime as dt, numpy as np
G=Geodesic.WGS84
H01=(-34.8903,114.1426); AZ=306.18; R7=1591.3
line=G.Line(H01[0],H01[1],AZ)
T0=dt.datetime(2014,3,8,tzinfo=dt.timezone.utc)
tobs={'T':dt.datetime(2014,3,8,0,52,3,tzinfo=dt.timezone.utc),'C':dt.datetime(2014,3,8,0,54,30,tzinfo=dt.timezone.utc)}
c=1.48
pts=[]
for name,d in [('crossing',0),('strip50',50),('strip100',100),('strip150',150),('strip200',200)]:
    p=line.Position((R7+d)*1e3); pts.append((name,p['lat2'],p['lon2'],R7+d))
hx=(-25.975,101.461); gh=G.Inverse(H01[0],H01[1],*hx); pts.append(('haixun',hx[0],hx[1],gh['s12']/1e3))
rel=[]
for br in 'TC':
    for name,la,lo,rng in pts:
        t=tobs[br]-dt.timedelta(seconds=rng/c)
        rel.append(dict(point=name,branch=br,lat=round(la,5),lon=round(lo,5),range_km=round(rng,1),t_impact=t.strftime('%H:%M:%S'),unix=round(t.timestamp(),1)))
for r in rel: print(r)
xc=pts[0]; print('haixun-crossing km', G.Inverse(xc[1],xc[2],*hx)['s12']/1e3)
json.dump(rel,open('L_releases.json','w'),indent=1)
