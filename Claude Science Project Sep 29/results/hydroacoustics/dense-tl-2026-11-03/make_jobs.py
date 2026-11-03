import sys, os, json, pickle, pathlib, time
import numpy as np, pandas as pd
from multiprocessing import Pool
os.environ["TLCHAIN_GLOBSED"] = "/Users/pete/Downloads/mh370-ocean-data/globsed/GlobSed-v3.nc"
W = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(W/"tlchain/tl-chain-2026-10-27")); sys.path.insert(0, str(W))
MOD = W/"hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics"
os.environ["TLCHAIN_MODULE_DIR"] = str(MOD)
from tlchain import paths as P, chain as C
from tlchain.bottom import LAYERED
_sed = P.sediment
import build_sections_now as B
P.sediment = _sed   # build_sections_now blanks sediment; restore the GlobSed lookup
OUT = [2.0, 5.0, 10.0, 30.0, 100.0, 300.0, 1000.0]
BANDS = [5.0, 6.3, 8.0, 10.0, 12.5, 16.0, 20.0, 25.0, 31.5, 40.0]
NF = 7
LATS = [-41.0 + 0.5*i for i in range(43)]

def build(p):
    pk = W/f"dense/runs/sec/{p['name']}.pkl"
    try:
        old = W/f"sparse/runs/sec/{p['name']}.pkl"
        if old.exists(): sec = pickle.load(open(old, "rb"))
        else: sec = P.build(tuple(p["src"]), tuple(p["rcv"]), "A5B4", 3)
        pickle.dump(sec, open(pk, "wb"))
        d = sec["depth_native"]; rd = p["rd"]
        if rd is None or not np.isfinite(rd): rd = float(d[-1]) - 2.0
        return dict(name=p["name"], station=p["station"], src_lat=p["src"][0], src_lon=p["src"][1], L_km=float(sec["L_km"]),
                    rcv_depth_m=float(rd), land=bool((d[1:-1] <= 0).any()), shallowest_m=float(np.min(d[1:-1])))
    except Exception as e:
        return dict(name=p["name"], station=p["station"], error=repr(e))

if __name__ == "__main__":
    R = B.receivers(); J = []
    for lat, lon in B.arc_points(LATS):
        for k, r in R.items():
            J.append(dict(name=f"arc{abs(lat):04.1f}S-{k}", station=k, src=(lat, lon), rcv=(r["lat"], r["lon"]), rd=r["depth"]))
    t0 = time.time()
    with Pool(12) as pool: rows = pool.map(build, J, chunksize=1)
    m = pd.DataFrame(rows); m.to_csv(W/"dense/runs/paths.csv", index=False)
    print(len(J), "paths; errors", m.get("error", pd.Series(dtype=str)).notna().sum(), "land", int(m.land.sum()), f"{time.time()-t0:.0f}s")
    jobs = []
    for _, r in m[~m.land.astype(bool)].iterrows():
        pk = W/f"dense/runs/sec/{r['name']}.pkl"
        for fc in BANDS:
            for f in C.band_freqs(fc, NF):
                jobs.append(dict(id=f"S|{r['name']}|{fc:g}|{f:.4f}", model="ram", sec=str(pk), reverse=True, f=float(f), zsrc=float(r.rcv_depth_m),
                                 out_depths=OUT, bottom=LAYERED.as_dict(), mode="native", dr_lam=5.0, dz_lam=0.05, dr_max_m=250.0, window_m=1000.0,
                                 cost=float(r.L_km*f*max(f, 30.0))))
    json.dump(jobs, open(W/"dense/runs/jobs.json", "w"))
    ids = {j["id"] for j in jobs}; n = 0
    with open(W/"dense/runs/out.jsonl", "w") as fo:
        for ln in open(W/"sparse/runs/out.jsonl"):
            r = json.loads(ln)
            if r.get("status") == "ok" and r["id"] in ids: fo.write(ln if ln.endswith("\n") else ln+"\n"); n += 1
    sj = json.load(open(W/"sparse/runs/jobs.json"))
    cs = sum(j["cost"] for j in sj); cd = sum(j["cost"] for j in jobs if j["id"] not in {json.loads(l)["id"] for l in open(W/"dense/runs/out.jsonl")})
    print(len(jobs), "jobs;", n, "reused from sparse; cost ratio new/sparse", round(cd/cs, 3), "-> est h at sparse rate", round(cd/cs*8544/3600, 2))
