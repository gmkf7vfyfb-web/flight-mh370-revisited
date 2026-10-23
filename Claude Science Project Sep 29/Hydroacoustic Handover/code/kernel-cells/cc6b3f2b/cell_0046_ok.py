
import json, pandas as pd, numpy as np
th = json.load(open("out/injection/thresholds.json"))
print(pd.read_csv("out/injection/sr_calibration.csv").pivot(index="k", columns="sigma", values="rate").round(2))
nm = np.load("out/injection/null_maxima_3376.npz")
rows=[]
for k in nm.files:
    v=nm[k]; v=v[np.isfinite(v)]
    rows.append(dict(method=k, n=len(v), p50=np.median(v), p99=np.quantile(v,.99), p999=np.quantile(v,.999), max=v.max()))
print(pd.DataFrame(rows).round(3).to_string(index=False))
