import sys, os, json, pathlib, time
import numpy as np, pandas as pd, sqlite3
from multiprocessing import Pool
W = pathlib.Path.cwd()
sys.path.insert(0, str(W/"tlchain/tl-chain-2026-10-27"))
MOD = W/"hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics"
os.environ["TLCHAIN_MODULE_DIR"] = str(MOD)
from tlchain import paths as P, classify as C, cases
P.sediment = lambda lat, lon: np.full(np.atleast_1d(lat).shape, np.nan)   # GlobSed not held yet; sections need depth and sound speed only

def arc_points(lats):
    z = np.load("/Users/pete/Downloads/mh370-exchange/searched-areas/run-j-supplement/arc-grid.npz")
    arc = z["arc"].astype(float); n = z["n"]; s0, w0, st = float(z["south"]), float(z["west"]), float(z["step"])
    lons = w0 + st*np.arange(arc.shape[1]); out = []
    for lat in lats:
        i = int(round((lat - s0)/st)); ok = n[i] > 0
        near = ok & (np.abs(arc[i]) <= 150.0); use = near if near.sum() >= 20 else ok
        A = np.vstack([np.ones(use.sum()), arc[i][use]]).T
        c = np.linalg.lstsq(A, lons[use], rcond=None)[0]; out.append((lat, float(c[0])))
    return out

def receivers():
    con = sqlite3.connect(MOD/"registry/data_db/hydro_data.sqlite")
    s = pd.read_sql("select * from site", con).set_index("site_id")
    R = {}
    for k in ["H01W", "H08S"]:
        R[k] = dict(lat=s.loc[k,"lat"], lon=s.loc[k,"lon"], depth=s.loc[k,"sensor_depth_m"])
    for k in ["IMOS3315","IMOS3376","IMOS3250","IMOS3274","IMOS3275"]:
        R[k] = dict(lat=s.loc[k,"lat"], lon=s.loc[k,"lon"], depth=None)
    for k in ["SWAMS1","SWAMS2","SWAMS3","SSEIR","MAD","NCRO","WKER"]:
        R[k] = dict(lat=s.loc[k,"lat"], lon=s.loc[k,"lon"], depth=s.loc[k,"sensor_depth_m"])
    return R

def job(p):
    out = W/"sections"/f"{p['name']}.npz"
    try:
        t0 = time.time()
        sec = P.build(tuple(p["src"]), tuple(p["rcv"]), p["decade"], p["month"])
        cl = C.classify(sec, "native")
        zs, rr, Cm = P.node_matrix(sec, zmax=3000.0)
        ax = zs[np.argmin(Cm, axis=0)]
        rd = p.get("rd")
        if rd is None or not np.isfinite(rd): rd = float(sec["depth_native"][-1]) - 2.0
        np.savez_compressed(out, range_km=sec["range_km"], lat=sec["lat"], lon=sec["lon"], depth=sec["depth_native"],
                            depth_med3=sec["depth_med3"], node_r=rr, axis_z=ax, axis_c=Cm.min(0), L_km=sec["L_km"], az=sec["az_deg"])
        return dict(name=p["name"], group=p["group"], source=p["source"], station=p["station"], src_lat=p["src"][0], src_lon=p["src"][1],
                    rcv_lat=p["rcv"][0], rcv_lon=p["rcv"][1], rcv_depth_m=rd, L_km=sec["L_km"], cls=cl["cls"], B_path=cl["B_path"],
                    shallowest_m=cl["shallowest_depth"], shallowest_range_km=cl["shallowest_range_km"], src_water_m=cl["src_water_depth"],
                    land=bool((sec["depth_native"][1:-1] <= 0).any()), wall_s=time.time()-t0)
    except Exception as e:
        return dict(name=p["name"], group=p["group"], error=repr(e))

if __name__ == "__main__":
    J = []
    for p in cases.all_paths():
        J.append(dict(name=p["name"], group=p["case"], source=p["source"], station=p["station"], src=p["src"], rcv=p["rcv"],
                      rd=p["rd"], decade=p["decade"], month=p["month"]))
    R = receivers()
    for lat, lon in arc_points([-20.0, -25.0, -30.0, -35.0, -40.0]):
        for k, r in R.items():
            J.append(dict(name=f"arc{abs(lat):04.1f}S-{k}", group="arc_sparse", source=f"arc {abs(lat):.0f} S", station=k,
                          src=(lat, lon), rcv=(r["lat"], r["lon"]), rd=r["depth"], decade="A5B4", month=3))
    print(len(J), flush=True)
    with Pool(10) as pool:
        rows = pool.map(job, J, chunksize=1)
    pd.DataFrame(rows).to_csv(W/"sections/index.csv", index=False)
    print("done", sum("error" in r and isinstance(r.get("error"), str) for r in rows), flush=True)
