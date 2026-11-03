import sys, os, json, pickle, pathlib, time
import numpy as np, pandas as pd
os.environ["TLCHAIN_GLOBSED"] = "/Users/pete/Downloads/mh370-ocean-data/globsed/GlobSed-v3.nc"
W = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(W/"tlchain/tl-chain-2026-10-27")); sys.path.insert(0, str(W))
from tlchain import paths as P, chain as C
from tlchain.bottom import LAYERED
ix = pd.read_csv(W/"path-sections-index.csv")
sp = ix[(ix.group=="arc_sparse") & (~ix.land)]
OUT = [2.0, 5.0, 10.0, 30.0, 100.0, 300.0, 1000.0]
BANDS = [5.0, 6.3, 8.0, 10.0, 12.5, 16.0, 20.0, 25.0, 31.5, 40.0]
J = []; meta = []
for _, r in sp.iterrows():
    pk = W/f"sparse/runs/sec/{r['name']}.pkl"
    if not pk.exists():
        sec = P.build((r.src_lat, r.src_lon), (r.rcv_lat, r.rcv_lon), "A5B4", 3); pickle.dump(sec, open(pk, "wb"))
    meta.append(dict(name=r["name"], station=r.station, src_lat=r.src_lat, L_km=r.L_km, rcv_depth_m=r.rcv_depth_m, path_class=r.path_class))
    for fc in BANDS:
        for f in C.band_freqs(fc, C.nf_for(fc)):
            J.append(dict(id=f"S|{r['name']}|{fc:g}|{f:.4f}", model="ram", sec=str(pk), reverse=True, f=float(f), zsrc=float(r.rcv_depth_m),
                          out_depths=OUT, bottom=LAYERED.as_dict(), mode="native", dr_lam=5.0, dz_lam=0.05, dr_max_m=250.0, window_m=1000.0,
                          cost=float(r.L_km*f*max(f, 30.0))))
json.dump(J, open(W/"sparse/runs/jobs.json","w")); pd.DataFrame(meta).to_csv(W/"sparse/runs/paths.csv", index=False)
print(len(sp), "paths", len(J), "jobs")
