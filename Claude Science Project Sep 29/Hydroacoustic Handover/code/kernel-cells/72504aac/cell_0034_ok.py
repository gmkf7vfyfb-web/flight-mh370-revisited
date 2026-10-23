
import numpy as np, pandas as pd, json, pyproj, os
G84 = pyproj.Geod(ellps='WGS84')
X='/Users/pete/Downloads/mh370-exchange'; S=X+'/hydroacoustics/run-j-searches'
arc=np.load(X+'/composer/run-j-views/arc-line.npz'); ALAT, ALON = arc['lat'], arc['lon']
print(arc['lat'][[0,-1]], arc['lat_range_measured'], float(arc['fit_rms_km']), arc['centre'], float(arc['radius_deg']))
# dense arc by small-circle interpolation
c=tuple(arc['centre']); rad=float(arc['radius_deg'])
def arc_pts(az):
    lon, lat, _ = G84.fwd(np.full_like(az, c[1]), np.full_like(az, c[0]), az, np.full_like(az, np.radians(rad)*6371008.8))
    return lat, lon
# use spherical small circle (as views_common)
def arc_point_az(az):
    az=np.radians(az); d=np.radians(rad); p1,l1=np.radians(c[0]),np.radians(c[1])
    p2=np.arcsin(np.sin(p1)*np.cos(d)+np.cos(p1)*np.sin(d)*np.cos(az))
    l2=l1+np.arctan2(np.sin(az)*np.sin(d)*np.cos(p1), np.cos(d)-np.sin(p1)*np.sin(p2))
    return np.degrees(p2), np.degrees(l2)
az=np.linspace(100,190,90001); arcLat, arcLon = arc_point_az(az)
m=(arcLat<-15)&(arcLat>-45); arcLat, arcLon = arcLat[m], arcLon[m]
rx=json.load(open(S+'/geometry/run.json'))['receivers']
def gdist(lat,lon,r):  # km
    la,lo=rx[r]; _,_,d=G84.inv(np.full_like(lat,lo), np.full_like(lat,la), lon, lat); return d/1000
dH01=gdist(arcLat,arcLon,'H01W'); dH08=gdist(arcLat,arcLon,'H08S')
lagA=(dH08-dH01)/1.482
def locus_from_lag(lag, ra='H01W', rb='H08S', latwin=(-41,-20)):
    da=gdist(arcLat,arcLon,ra); db=gdist(arcLat,arcLon,rb); L=(db-da)/1.482
    ok=(arcLat>latwin[0])&(arcLat<latwin[1]); s=np.sign(L-lag); idx=np.nonzero(ok[:-1]&ok[1:]&(s[:-1]!=s[1:]))[0]
    return [(arcLat[i],arcLon[i],da[i]) for i in idx]
print('G', locus_from_lag(1245))
lagE=(pd.Timestamp('2014-03-08 01:10:01')-pd.Timestamp('2014-03-08 00:52:04')).total_seconds()
lagF=(pd.Timestamp('2014-03-08 01:12:49')-pd.Timestamp('2014-03-08 00:54:27')).total_seconds()
print('E',lagE, locus_from_lag(lagE)); print('F',lagF, locus_from_lag(lagF))
G=dict(lat=-33.564949768575076, lon=94.50869477928312)
for r in ['H01W','H08S']:
    la,lo=rx[r]; faz,baz,d=G84.inv(lo,la,G['lon'],G['lat']); print(r, round(faz%360,2), round(d/1000,1))
