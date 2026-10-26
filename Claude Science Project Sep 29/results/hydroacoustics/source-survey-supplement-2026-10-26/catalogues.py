"""Merge USGS ComCat (FDSN event; box 75S-30N, 15-180E, M>=2.5; global M>=5.0) and ISC Bulletin (FDSN event, same
box, all magnitudes) for 28 Feb-31 Mar 2015-2019. Duplicates: within 60 s and 150 km (USGS kept). For association,
events with magnitude >= 3.0 (any type) are kept. Predicted T-phase arrival at each triplet centroid = origin +
WGS84 geodesic distance / 1.48 km/s (rule checked against 24 IDC T arrivals in 2014: median +10 s, SD 46 s).
Path blockage by land is NOT checked."""
import glob, numpy as np, pandas as pd
from pyproj import Geod
G = Geod(ellps="WGS84")
CEN = {"H01W": (-34.890303, 114.142637), "H08S": (-7.639380, 72.483828)}
u = pd.concat([pd.read_csv(f) for f in sorted(glob.glob("cat/usgs_*.csv"))]).drop_duplicates("id")
u = pd.DataFrame(dict(src="USGS", evid=u.id, time=pd.to_datetime(u.time, format="ISO8601", utc=True), lat=u.latitude, lon=u.longitude, depth_km=u.depth, mag=u.mag, magtype=u.magType, place=u.place))
rows = []
for f in sorted(glob.glob("cat/isc_box_*.txt")):
    d = pd.read_csv(f, sep="|", comment=None)
    d.columns = [c.strip().lstrip("#") for c in d.columns]
    rows.append(d)
i = pd.concat(rows).drop_duplicates("EventID")
i = i[pd.to_datetime(i.Time, format="ISO8601", errors="coerce").notna()]
i = pd.DataFrame(dict(src="ISC", evid=i.EventID.astype(str), time=pd.to_datetime(i.Time, format="ISO8601", utc=True, errors="coerce"), lat=i.Latitude, lon=i.Longitude, depth_km=i["Depth/km"], mag=pd.to_numeric(i.Magnitude, errors="coerce"), magtype=i.MagType, place=i.EventLocationName))
u = u.sort_values("time").reset_index(drop=True)
keep = np.ones(len(i), bool)
ut = u.time.values.astype("datetime64[s]").astype(np.int64)
for k, r in enumerate(i.itertuples()):
    t = np.int64(r.time.timestamp())
    j0, j1 = np.searchsorted(ut, t - 60), np.searchsorted(ut, t + 60)
    if j1 > j0:
        _, _, d = G.inv(np.full(j1 - j0, r.lon), np.full(j1 - j0, r.lat), u.lon.values[j0:j1], u.lat.values[j0:j1])
        if (d < 150e3).any(): keep[k] = False
E = pd.concat([u, i[keep]]).sort_values("time").reset_index(drop=True)
E = E[E.mag >= 3.0].reset_index(drop=True)
for st, (la, lo) in CEN.items():
    az, _, d = G.inv(np.full(len(E), lo), np.full(len(E), la), E.lon.values, E.lat.values)
    E[f"{st}_dist_km"] = d / 1e3; E[f"{st}_baz"] = np.mod(az, 360)
    E[f"{st}_t_pred"] = E.time + pd.to_timedelta(d / 1480.0, unit="s")
E.to_csv("cat/events_merged_m3.csv", index=False)
print(len(u), len(i), keep.sum(), len(E)); print(E.groupby([E.time.dt.year, "src"]).size().unstack())
