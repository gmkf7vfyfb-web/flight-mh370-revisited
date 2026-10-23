pip install -q geographiclib 2>/dev/null; python - <<'EOF'
import urllib.request
from geographiclib.geodesic import Geodesic
G=Geodesic.WGS84
try:
    t=urllib.request.urlopen("https://service.earthscope.org/fdsnws/station/1/query?net=IM&sta=H01W1,H01W2,H01W3&level=station&format=text&starttime=2014-03-08&endtime=2014-03-09",timeout=20).read().decode()
    rows=[l.split('|') for l in t.splitlines() if l and not l.startswith('#')]
    lat=sum(float(r[2]) for r in rows)/len(rows); lon=sum(float(r[3]) for r in rows)/len(rows)
    print("H01W triad centroid",round(lat,4),round(lon,4),len(rows))
except Exception as e:
    print("fetch fail",e); lat,lon=-34.89,114.14
pts={"Haixun 4 Apr":(-25.975,101.461),"Earlier arc crossing":(-26.2,101.9),"Chart star approx":(-25.8,101.38)}
for k,(a,b) in pts.items():
    g=G.Inverse(lat,lon,a,b); print(k,"az %.2f deg  range %.0f km"%(g['azi1']%360,g['s12']/1e3))
g=G.Inverse(-25.975,101.461,-26.2,101.9); print("Haixun to arc crossing %.1f km"%(g['s12']/1e3))
# perpendicular offset of Haixun from the 306.18 bearing line
line=G.Line(lat,lon,306.18); import math
best=min((G.Inverse(*[line.Position(s*1e3)[k] for k in('lat2','lon2')],-25.975,101.461)['s12'],s) for s in range(1300,1700))
print("Haixun offset from 306.18 deg line %.1f km at range %d km"%(best[0]/1e3,best[1]))
EOF