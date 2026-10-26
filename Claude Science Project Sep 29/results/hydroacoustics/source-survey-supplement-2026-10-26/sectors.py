"""Bearing sectors at each IMS triplet (FDSN centroid = plain mean of the three EDH elements):
(a) the 7th arc at FL400 (official reference line, geojson) for 20-40 S, restricted to 88-110 E as in the brief;
(b) a rough Antarctic ice sector: azimuths to points 55-66 S, 30-150 E.  Geodesics: WGS84 (pyproj.Geod)."""
import json, numpy as np, pandas as pd
from pyproj import Geod
G = Geod(ellps="WGS84")
ch = pd.read_csv("meta/IM_hydro_channels.txt", sep="|")
ch.columns = [c.strip().lstrip("#").strip() for c in ch.columns]
ch = ch[ch.EndTime.isna()]
EL = {r.Station: (r.Latitude, r.Longitude, -r.Elevation) for r in ch.itertuples()}
CEN = {t: tuple(np.mean([EL[f"{t}{i}"][:2] for i in (1, 2, 3)], axis=0)) for t in ("H01W", "H08S", "H08N")}
arc = np.array(json.load(open("meta/seventh_arc_fl400.geojson"))["features"][0]["geometry"]["coordinates"])
def densify(c, n=50):
    out = []
    for a, b in zip(c[:-1], c[1:]):
        lons, lats = zip(*[(a[0] + (b[0]-a[0])*k/n, a[1] + (b[1]-a[1])*k/n) for k in range(n)])
        out += list(zip(lons, lats))
    return np.array(out)
arcd = densify(arc)
def sector(t, pts):
    la, lo = CEN[t]
    az, _, dist = G.inv(np.full(len(pts), lo), np.full(len(pts), la), pts[:, 0], pts[:, 1])
    az = np.mod(az, 360)
    return az, dist / 1e3
rows = []
for t in CEN:
    for name, m in [("arc_20_40S", (arcd[:, 1] <= -20) & (arcd[:, 1] >= -40)),
                    ("arc_20_35S", (arcd[:, 1] <= -20) & (arcd[:, 1] >= -35)),
                    ("arc_35_40S", (arcd[:, 1] <= -35) & (arcd[:, 1] >= -40)),
                    ("arc_20_40S_88_110E", (arcd[:, 1] <= -20) & (arcd[:, 1] >= -40) & (arcd[:, 0] >= 88) & (arcd[:, 0] <= 110))]:
        az, d = sector(t, arcd[m])
        rows.append(dict(triad=t, sector=name, lat_c=CEN[t][0], lon_c=CEN[t][1], az_min=az.min(), az_max=az.max(), dist_min_km=d.min(), dist_max_km=d.max(),
                         arc_lat_range=f"{arcd[m][:,1].min():.2f}..{arcd[m][:,1].max():.2f}", arc_lon_range=f"{arcd[m][:,0].min():.2f}..{arcd[m][:,0].max():.2f}"))
    LA, LO = np.meshgrid(np.arange(-66, -54.9, 1.0), np.arange(30, 150.1, 1.0))
    az, d = sector(t, np.c_[LO.ravel(), LA.ravel()])
    rows.append(dict(triad=t, sector="antarctic_55_66S_30_150E", lat_c=CEN[t][0], lon_c=CEN[t][1], az_min=az.min(), az_max=az.max(), dist_min_km=d.min(), dist_max_km=d.max(), arc_lat_range="-66..-55", arc_lon_range="30..150"))
df = pd.DataFrame(rows); df.to_csv("out/bearing-sectors.csv", index=False); print(df.round(2).to_string())
json.dump({k: list(v) for k, v in EL.items()}, open("meta/elements.json", "w"))
