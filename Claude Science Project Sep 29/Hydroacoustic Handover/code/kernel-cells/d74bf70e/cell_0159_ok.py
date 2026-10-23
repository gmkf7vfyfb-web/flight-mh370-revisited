import numpy as np, pandas as pd
S="repo/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/data/stub/"
for p in ["H01W","H08S"]:
    b=pd.read_csv(S+f"bathy_air9_{p}.csv"); c=pd.read_csv(S+f"ssp_air9_{p}.csv")
    d=-b.elevation_m.values; r=b.range_km.values
    # local minima shallower than 3000 m and their widths
    sh = d<3000; 
    runs=[]; i=0
    while i<len(d):
        if sh[i]:
            j=i
            while j<len(d) and sh[j]: j+=1
            runs.append((r[i], r[j-1], d[i:j].min())); i=j
        else: i+=1
    print(p, "segments shallower than 3000 m (start,end,min):", [(round(a),round(b_),int(m)) for a,b_,m in runs][:15])
    wmax = c.dropna().groupby("node").depth_m.max(); nodes=c.groupby("node").range_km.first()
    gd = np.interp(nodes.values, r, d)
    print("  WOA deepest valid vs GEBCO at node: median gap", np.median(gd-wmax.reindex(nodes.index).values).round(), "max gap", np.max(gd-wmax.reindex(nodes.index).values).round(), "WOA deeper than GEBCO at", int((wmax.reindex(nodes.index).values>gd).sum()), "nodes")
    print("  depth at source", d[0], "at receiver", d[-1])