import pandas as pd
sl = pd.read_csv("repo/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/data/blackman/blackman_shot_lines.csv", comment="#")
for s in ["air9","air8"]:
    r=sl[sl.site==s]; la=r[["start_lat_dd","end_lat_dd"]].values.mean(); lo=r[["start_lon_dd","end_lon_dd"]].values.mean()
    print(s, round(la,4), round(lo,4), {k:round(G.inv(lo,la,v[1],v[0])[2]/1000,1) for k,v in st.items()})