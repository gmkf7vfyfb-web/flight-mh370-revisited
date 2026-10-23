def hms(s):
    if pd.isna(s) or s=='' : return np.nan
    h,m,x=str(s).split(':'); return int(h)*3600+int(m)*60+float(x)
def fmt(t):
    if pd.isna(t): return ''
    t=t%86400; h=int(t//3600); m=int((t%3600)//60); s=t%60
    return f"{h:02d}:{m:02d}:{s:04.1f}"
from math import radians
def geod_km(lat1,lon1,lat2,lon2):
    # Vincenty-free: use pyproj if available else haversine on WGS84 mean radius
    try:
        from pyproj import Geod
        g=Geod(ellps='WGS84'); return g.inv(lon1,lat1,lon2,lat2)[2]/1000
    except ImportError:
        R=6371.0088; p1,p2=np.radians(lat1),np.radians(lat2); dl=np.radians(lon2-lon1)
        a=np.sin((p2-p1)/2)**2+np.cos(p1)*np.cos(p2)*np.sin(dl/2)**2; return 2*R*np.arcsin(np.sqrt(a))
try:
    import pyproj; print('pyproj', pyproj.__version__)
except ImportError: print('no pyproj')
rx=json.load(open(H+'searches_run_j/geometry/run.json'))['receivers']
# origin seconds after 00:00 8 Mar (event 1 is 7 Mar 23:47 -> negative)
ev['t0']=ev.origin_s_after_T0  # T0?
print(ev[['index','label','origin_time_utc','origin_s_after_T0']].head(3))