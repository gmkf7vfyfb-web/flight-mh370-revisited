import pandas as pd, numpy as np, json
S="hydro/stub/"
for p in ["H01W","H08S"]:
    b=pd.read_csv(S+f"bathy_air9_{p}.csv"); c=pd.read_csv(S+f"ssp_air9_{p}.csv")
    i=b.elevation_m.idxmax(); j=b.corridor_max_elevation_m.idxmax()
    ax = c.dropna().loc[c.dropna().groupby("node").c_m_s.idxmin()]
    print(p, "len", b.range_km.iloc[-1], "| on-track shallowest", -b.elevation_m[i], "m at", b.range_km[i], "km | corridor", -b.corridor_max_elevation_m[j], "at", b.range_km[j],
          "| median depth", -b.elevation_m.median(), "| TIDs", dict(b.tid.value_counts().head(4)))
    print("   axis depth m: min/med/max", ax.depth_m.min(), ax.depth_m.median(), ax.depth_m.max(), "| c_min", round(ax.c_m_s.min(),1), round(ax.c_m_s.max(),1),
          "| surface c", round(c[c.depth_m==0].c_m_s.median(),1), "| NaN frac", round(c.c_m_s.isna().mean(),3))
    # where is the seafloor within 300 m of the local axis
    ax_i = np.interp(b.range_km, ax.range_km, ax.depth_m)
    close = b[(-b.corridor_max_elevation_m) < ax_i + 300]
    print("   corridor seafloor within 300 m of axis:", len(close), "samples", (close.range_km.min(), close.range_km.max()) if len(close) else "")