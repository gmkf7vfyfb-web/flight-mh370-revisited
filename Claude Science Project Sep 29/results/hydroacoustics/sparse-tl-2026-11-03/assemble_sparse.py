import sys, json, numpy as np, pandas as pd
from collections import defaultdict
sys.path.insert(0, "tlchain/tl-chain-2026-10-27")
from tlchain import chain as C
OUT = [2.0, 5.0, 10.0, 30.0, 100.0, 300.0, 1000.0]
g = defaultdict(list)
for ln in open("sparse/runs/out.jsonl"):
    r = json.loads(ln)
    if r.get("status") != "ok": continue
    _, path, fc, f = r["id"].split("|"); g[(path, float(fc))].append((float(f), r))
rows, sub = [], []
for (path, fc), v in g.items():
    v.sort(key=lambda x: x[0]); fs = np.array([x[0] for x in v]); I = np.array([x[1]["I"] for x in v], float); L = v[0][1]["L_km"]
    tl, sd = C.band_tl_sd(I, fs, L)
    for j, z in enumerate(OUT):
        rows.append(dict(path=path, fc_hz=fc, src_depth_m=z, tl_db=float(tl[j]), band_sd_db=float(sd[j]), nf=len(fs), range_km=L))
    for k in (5, 7):
        idx = np.round(np.linspace(0, len(fs)-1, k)).astype(int)
        tk, _ = C.band_tl_sd(I[idx], fs[idx], L)
        for j, z in enumerate(OUT): sub.append(dict(path=path, fc_hz=fc, src_depth_m=z, k=k, err_db=float(tk[j]-tl[j])))
df = pd.DataFrame(rows); df.to_csv("sparse/tl_sparse_bands.csv", index=False)
s = pd.DataFrame(sub); s.to_csv("sparse/subsample_error.csv", index=False)
print(df.shape, df.path.nunique(), df.tl_db.describe().round(1).to_dict())
print(s.groupby('k').err_db.agg(['mean','std', lambda x: np.percentile(np.abs(x),95), lambda x: np.abs(x).max()]).round(2))
