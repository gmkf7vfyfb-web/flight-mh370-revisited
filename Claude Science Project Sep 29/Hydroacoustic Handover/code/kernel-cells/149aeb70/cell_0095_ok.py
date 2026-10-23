import numpy as np, pandas as pd, re
ev = kw[["event","bearing","t_H01W"]].drop_duplicates().sort_values("t_H01W")
H01W = RX["H01W Cape Leeuwin"]
R=6371.0
def fwd(lat0, lon0, brg_deg, d_km):
    p1,l1,b,d = np.radians(lat0), np.radians(lon0), np.radians(brg_deg), d_km/R
    p2 = np.arcsin(np.sin(p1)*np.cos(d)+np.cos(p1)*np.sin(d)*np.cos(b))
    l2 = l1+np.arctan2(np.sin(b)*np.sin(d)*np.cos(p1), np.cos(d)-np.sin(p1)*np.sin(p2))
    return np.degrees(p2), np.degrees(l2)
rng = np.arange(50, 5000, 2.0)
rows=[]
for _,r in ev.iterrows():
    la_,lo_ = fwd(*H01W, r["bearing"], rng)
    resid = lo_ - np.polyval(cf, la_)
    sgn = np.sign(resid); idx = np.where(np.diff(sgn)!=0)[0]
    if len(idx)==0: rows.append((r["event"], r["bearing"], r["t_H01W"], None,None,None,None)); continue
    i=idx[0]; d=rng[i]; lat_x, lon_x = la_[i], lo_[i]
    t = pd.to_datetime("2014-03-08 "+r["t_H01W"]+"+00:00")
    tsrc = t - pd.Timedelta(seconds=d/1.48)
    rows.append((r["event"], r["bearing"], r["t_H01W"], round(lat_x,2), round(lon_x,2), round(d,0), tsrc.strftime("%H:%M:%S")))
out = pd.DataFrame(rows, columns=["event","bearing_deg","t_H01W","arc_lat","arc_lon","range_km","implied_source_time"])
print(out.to_string(index=False))
