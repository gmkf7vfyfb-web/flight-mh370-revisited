import pandas as pd, numpy as np
b=pd.read_csv("hydro/stub8/bathy_air8_H01W.csv"); c=pd.read_csv("hydro/stub8/ssp_air8_H01W.csv")
d=-b.elevation_m; dc=-b.corridor_max_elevation_m
i=d.idxmin(); print("shallowest on track", d[i], "m at", b.range_km[i], "km", round(b.lat[i],3), round(b.lon[i],3), "TID", b.tid[i])
ax=c.dropna().loc[c.dropna().groupby("node").c_m_s.idxmin()][["range_km","depth_m","c_m_s"]]
axd=np.interp(b.range_km, ax.range_km, ax.depth_m)
for thr in [0, 300, 600]:
    m=dc < axd+thr; print(f"corridor seafloor within {thr} m of axis:", int(m.sum()), "samples; ranges", np.round(b.range_km[m].values[[0,-1]],1) if m.any() else "")
w=b[(b.range_km>b.range_km[i]-60)&(b.range_km<b.range_km[i]+60)]
print("segment <2000 m:", np.round(w[-w.elevation_m<2000].range_km.values[[0,-1]],1), "width km", round(((-w.elevation_m)<2000).sum()*0.5,1))
print("TID in segment:", dict(w.tid.value_counts()))
print("axis depth there:", round(float(np.interp(b.range_km[i], ax.range_km, ax.depth_m))), "m")