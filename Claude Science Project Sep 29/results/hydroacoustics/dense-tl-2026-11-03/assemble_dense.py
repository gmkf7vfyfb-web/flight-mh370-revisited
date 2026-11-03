import sys, json, numpy as np, pandas as pd
from collections import defaultdict
sys.path.insert(0, "tlchain/tl-chain-2026-10-27")
from tlchain import chain as C
OUT = [2.0, 5.0, 10.0, 30.0, 100.0, 300.0, 1000.0]
jobs = json.load(open("dense/runs/jobs.json")); need = defaultdict(set)
for j in jobs:
    _, p, fc, f = j["id"].split("|"); need[(p, float(fc))].add(j["id"])
g = defaultdict(dict); nerr = 0
for ln in open("dense/runs/out.jsonl"):
    r = json.loads(ln)
    if r.get("status") != "ok": nerr += 1; continue
    _, p, fc, f = r["id"].split("|"); g[(p, float(fc))][r["id"]] = (float(f), r)
rows = []; incomplete = 0
for key, ids in need.items():
    have = g.get(key, {})
    if set(have) != ids: incomplete += 1; continue
    v = sorted(have.values(), key=lambda x: x[0]); fs = np.array([x[0] for x in v])
    I = np.array([x[1]["I"] for x in v], float); L = v[0][1]["L_km"]
    tl, sd = C.band_tl_sd(I, fs, L)
    for k, z in enumerate(OUT):
        rows.append(dict(path=key[0], fc_hz=key[1], src_depth_m=z, tl_db=float(tl[k]), band_sd_db=float(sd[k]), nf=len(fs), range_km=L))
df = pd.DataFrame(rows)
m = pd.read_csv("dense/runs/paths.csv")
df = df.merge(m[["name", "station", "src_lat", "src_lon", "rcv_depth_m"]], left_on="path", right_on="name").drop(columns="name")
df.to_csv("dense/tl_dense_bands.csv", index=False)
print("band rows", len(df), "paths complete", df.path.nunique(), "band groups incomplete", incomplete, "error rows", nerr)
