W=/Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-tlrecal; tail -2 $W/nx2d.log
cd "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare"
python - <<'EOF'
import pandas as pd, numpy as np
W='/Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-tlrecal/sections/builder/'
for n in ['bathy_air7off+0_H01W.csv','bathy_air7off+50_H01W.csv','bathy_air9_H01W.csv']:
    b=pd.read_csv(W+n); d=-b.elevation_m.values; r=b.range_km.values
    # sills: local minima of depth below 2000 m, coarse 50 km windows
    out=[]
    for k in range(0,len(r),100):
        w=d[k:k+100]; 
        if w.min()<2000: out.append((int(r[k]), int(w.min())))
    print(n, 'range', int(r[-1]), 'sills(<2000 m) by 50 km window:', out[:30])
EOF