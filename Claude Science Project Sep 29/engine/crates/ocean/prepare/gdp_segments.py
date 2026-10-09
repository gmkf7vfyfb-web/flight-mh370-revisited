"""Cut GDP 6-hourly quality-controlled drifter tracks (NOAA AOML, drifter_6hour_qc, as fetched by drift
into /Users/pete/Downloads/mh370-ocean-data/gdp) into replay segments for `examples/drifter_replay.rs`.

A segment is 61 consecutive fixes 6 h apart (15 days) of one drifter, all inside the domain, with one
drogue state throughout: drogued if the drogue-loss date is after the last fix, undrogued if it is at or
before the first; segments that straddle the loss are dropped. Starts are every `stride` fixes (default
20, i.e. 5 days) along each continuous run, so segments of one drifter overlap by 10 days and are not
independent; the replay reports drifter counts beside segment counts.

python gdp_segments.py <gdp_dir> <out.json> [t_start_iso t_end_iso [stride]]
"""
import json, sys
from datetime import datetime, timezone
import numpy as np
from scipy.io import netcdf_file

gdp, out = sys.argv[1], sys.argv[2]
t0 = datetime.fromisoformat(sys.argv[3] if len(sys.argv) > 3 else "2014-03-08T00:00:00").replace(tzinfo=timezone.utc).timestamp()
t1 = datetime.fromisoformat(sys.argv[4] if len(sys.argv) > 4 else "2017-01-30T00:00:00").replace(tzinfo=timezone.utc).timestamp()
stride = int(sys.argv[5]) if len(sys.argv) > 5 else 20
LON, LAT, N, DT = (15.0, 120.0), (-50.0, 0.0), 61, 21600.0
rows = []
y0, y1 = datetime.fromtimestamp(t0, timezone.utc).year, datetime.fromtimestamp(t1, timezone.utc).year
for y in range(y0, y1 + 1):
    f = netcdf_file(f"{gdp}/gdp6h_io_{y}.nc", "r", mmap=False)
    v = f.variables
    ids = np.array([b"".join(r).decode() for r in v["ID"][:]])
    rows.append((ids, v["time"][:].copy(), v["longitude"][:].copy(), v["latitude"][:].copy(), v["drogue_lost_date"][:].copy()))
ids, t, lon, lat, lost = (np.concatenate([r[k] for r in rows]) for k in range(5))
lon = np.where(lon > 180, lon - 360, lon)
segs, drifters = [], {True: set(), False: set()}
for d in np.unique(ids):
    k = np.where(ids == d)[0]
    k = k[np.argsort(t[k])]
    tt, xx, yy, ll = t[k], lon[k], lat[k], lost[k]
    inside = (xx >= LON[0]) & (xx <= LON[1]) & (yy >= LAT[0]) & (yy <= LAT[1]) & np.isfinite(xx) & np.isfinite(yy)
    ok_step = np.r_[np.diff(tt) == DT, False]
    i = 0
    while i + N <= len(tt):
        w = slice(i, i + N)
        if tt[i] >= t0 and tt[i + N - 1] <= t1 and inside[w].all() and ok_step[i:i + N - 1].all():
            drogued = bool(ll[i] > tt[i + N - 1])
            undrogued = bool(ll[i] <= tt[i])
            if drogued or undrogued:
                segs.append(dict(id=d, drogued=drogued, t0=float(tt[i]), lon=[round(float(a), 5) for a in xx[w]], lat=[round(float(a), 5) for a in yy[w]]))
                drifters[drogued].add(d)
            i += stride
        else:
            i += 1
json.dump(dict(source="NOAA AOML GDP drifter_6hour_qc (ERDDAP), files in " + gdp, step_s=DT, fixes=N, stride=stride,
               t_start=t0, t_end=t1, segments=segs), open(out, "w"))
print(json.dumps(dict(segments=len(segs), drogued=sum(s["drogued"] for s in segs), undrogued=sum(not s["drogued"] for s in segs),
                      drifters_drogued=len(drifters[True]), drifters_undrogued=len(drifters[False]))))
