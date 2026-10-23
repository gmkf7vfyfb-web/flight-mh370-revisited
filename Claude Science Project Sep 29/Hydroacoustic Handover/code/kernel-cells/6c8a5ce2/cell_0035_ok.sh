cd .tmp/standin; python - <<'EOF'
import pandas as pd, numpy as np
D="/Users/pete/Downloads/mh370-exchange/ocean-transport/paths-calibration"
for n in ["af447-H10S","sanjuan-charge-H10N"]:
    b=pd.read_csv(f"{D}/bathy_{n}.csv"); s=pd.read_csv(f"{D}/ssp_{n}.csv")
    out=[]
    for node,g in s.groupby("node"):
        g=g.dropna(subset=["c_m_s"]).sort_values("depth_m"); c0=g.c_m_s.iloc[0]; z=g.depth_m.values; c=g.c_m_s.values
        ax=z[np.argmin(c)]; below=(z>ax)&(c>=c0); crit=z[below][0] if below.any() else np.nan
        r=g.range_km.iloc[0]; wd=-np.median(b[(b.range_km>r-12.5)&(b.range_km<r+12.5)].elevation_m)
        out.append((r,c0,ax,crit,z.max(),wd))
    o=pd.DataFrame(out,columns=["r","c_surf","axis_m","critical_m","woa_floor","water_m"])
    o["crit_below_bottom"]=(o.critical_m.isna())|(o.critical_m>o.water_m)
    print(n, "share of path where critical depth is absent or below seabed:", round(o.crit_below_bottom.mean(),2))
    print(o.iloc[::max(1,len(o)//10)].round(0).to_string(index=False))
EOF