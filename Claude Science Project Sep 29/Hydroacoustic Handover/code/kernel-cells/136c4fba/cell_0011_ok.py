import pandas as pd, numpy as np, os
D="repo/Archive ISO Pre Sept 28/codebases/v01-share-withdrawn/v01/workspace/.sources/kadri-2024-hydroacoustics/data/kadri-figure-extraction/figure9-vector-traces"
for p,st in [("kadri-2024-figure9-panel-d-H08S.csv","d 01:00"),("kadri-2024-figure9-panel-e-H08S.csv","e 01:10")]:
    df=pd.read_csv(os.path.join(D,p))
    t=df.plotted_time_s.values
    dt=np.diff(t)
    print(st, "n=",len(df), "t range %.3f..%.3f"%(t.min(),t.max()),
          "utc %s..%s"%(df.utc.iloc[0][11:], df.utc.iloc[-1][11:]),
          "dt median %.4f p05 %.4f p95 %.4f max %.3f"%(np.median(dt),np.percentile(dt,5),np.percentile(dt,95),dt.max()),
          "monotonic", bool(np.all(dt>=0)), "|p| max %.3f"%np.abs(df.pressure_pa).max())
