import sys, os, json, pickle, pathlib, sqlite3, time
import numpy as np, pandas as pd
from multiprocessing import Pool
os.environ["TLCHAIN_GLOBSED"] = "/Users/pete/Downloads/mh370-ocean-data/globsed/GlobSed-v3.nc"
W = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(W/"tlchain/tl-chain-2026-10-27"))
MOD = W/"hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics"; os.environ["TLCHAIN_MODULE_DIR"] = str(MOD)
from tlchain import paths as P, chain as C
from tlchain.bottom import LAYERED
OUT = [2.0, 5.0, 10.0, 30.0, 100.0, 300.0, 1000.0]
BANDS = [5.0, 6.3, 8.0, 10.0, 12.5, 16.0, 20.0, 25.0, 31.5, 40.0]; NF = 7
con = sqlite3.connect(MOD/"registry/data_db/hydro_data.sqlite")
ev = pd.read_sql("select * from dg_royer_2016_royer_events", con)
st = pd.read_sql("select * from dg_royer_2016_royer_stations", con).set_index("station")
ar = pd.read_sql("select * from dg_royer_2016_royer_arrivals", con)

def build(p):
    pk = W/f"royer/runs/sec/{p['name']}.pkl"
    try:
        sec = pickle.load(open(pk, "rb")) if pk.exists() else P.build(tuple(p["src"]), tuple(p["rcv"]), "A5B4", 3)
        pickle.dump(sec, open(pk, "wb")); d = sec["depth_native"]
        return dict(p, L_km=float(sec["L_km"]), land=bool((d[1:-1] <= 0).any()), sed_ok=float(np.isfinite(sec["sed_m"]).mean()))
    except Exception as e:
        return dict(p, error=repr(e))

if __name__ == "__main__":
    J = []
    for _, a in ar.iterrows():
        e = ev[ev["index"] == a["index"]].iloc[0]
        if a.station in ("H01W1", "H01W3"): continue   # three Cape Leeuwin elements ~2 km apart; keep H01W2 (Royer spectrograms)
        if a.station not in st.index or not np.isfinite(st.loc[a.station, "lat_deg"]): continue
        s = st.loc[a.station]
        J.append(dict(name=f"royer{int(a['index']):02d}-{a.station}", event=int(a["index"]), event_class=e.event_class, label=e.label,
                      station=a.station, arrival=bool(pd.notna(a.arrival_utc)), src=(float(e.lat_deg), float(e.lon_deg)),
                      rcv=(float(s.lat_deg), float(s.lon_deg)), rcv_depth_m=float(s.hydrophone_depth_m)))
    t0 = time.time()
    with Pool(12) as pool: rows = pool.map(build, J, chunksize=1)
    m = pd.DataFrame(rows); m.to_csv(W/"royer/runs/paths.csv", index=False)
    print(len(m), "paths; errors", m.get("error", pd.Series(dtype=object)).notna().sum(), "land", int(m.land.sum()), "min sed coverage (water)", m[~m.land].sed_ok.min(), f"{time.time()-t0:.0f}s")
    print(m.groupby("station").agg(n=("name","size"), arrivals=("arrival","sum"), land=("land","sum"), L=("L_km","median")).round(0).to_string())
    jobs = []
    for _, r in m[~m.land].iterrows():
        for fc in BANDS:
            for f in C.band_freqs(fc, NF):
                jobs.append(dict(id=f"S|{r['name']}|{fc:g}|{f:.4f}", model="ram", sec=str(W/f"royer/runs/sec/{r['name']}.pkl"), reverse=True, f=float(f),
                                 zsrc=float(r.rcv_depth_m), out_depths=OUT, bottom=LAYERED.as_dict(), mode="native", dr_lam=5.0, dz_lam=0.05,
                                 dr_max_m=250.0, window_m=1000.0, cost=float(r.L_km*f*max(f, 30.0))))
    json.dump(jobs, open(W/"royer/runs/jobs.json", "w"))
    dj = json.load(open(W/"dense/runs/jobs.json")); cd = sum(j["cost"] for j in dj)*(34812/38780)
    print(len(jobs), "jobs; est h at last night's rate", round(sum(j["cost"] for j in jobs)/cd*5.75, 2))
