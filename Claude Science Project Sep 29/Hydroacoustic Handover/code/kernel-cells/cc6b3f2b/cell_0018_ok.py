
import numpy as np, json, os
from pyproj import Geod
g = Geod(ellps="WGS84")
# run J weighted median impact from one seed (geometry for the template path only)
d = "/Users/pete/Downloads/mh370-exchange/end-of-flight/run-j/run-j-waypoints/seed-1"
cols = open(f"{d}/COLUMNS.txt").read().split()
X = np.load(f"{d}/impacts32.npy", mmap_mode="r")
print(X.shape, X.dtype)
ci = {c:i for i,c in enumerate(cols)}
w = np.asarray(X[:, ci["weight"]], float); lat = np.asarray(X[:, ci["latitude_deg"]], float); lon = np.asarray(X[:, ci["longitude_deg"]], float)
ok = np.isfinite(w)&np.isfinite(lat)&np.isfinite(lon)&(w>0)
def wmed(v,w):
    o=np.argsort(v); c=np.cumsum(w[o]); return v[o][np.searchsorted(c, c[-1]/2)]
mlat, mlon = wmed(lat[ok], w[ok]), wmed(lon[ok], w[ok])
print("median impact", mlat, mlon)
H01W = (-34.8903, 114.1426); H08S = (-7.6394, 72.4838); PC3376 = (-31.8417, 115.0133)
for nm,(la,lo) in dict(H01W=H01W,H08S=H08S,PerthCanyon=PC3376).items():
    az,_,dist = g.inv(mlon, mlat, lo, la); print(nm, round(dist/1e3,1),"km", round(dist/1482), "s")
# GEBCO depth along path to H01W
gj = json.load(open("/Users/pete/Downloads/mh370-ocean-data/gebco/grid/gebco_2026.json")); print({k:gj[k] for k in gj if k!='notes'})
