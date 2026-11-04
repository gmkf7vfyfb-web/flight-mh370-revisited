"""Build sections and the job list for the Cape Leeuwin / Wake loss-gap diagnostics (4 Nov 2026).
Paths: F-35A point W (40.64 N, 142.96 E; frozen cases.py) to the H11N and H11S triad centroids (WOA23 B5C2, April),
and 7th-arc points 39.0, 35.5, 30.0 S to Cape Leeuwin H01W (dense-run sections, WOA23 A5B4, March, receiver 1,055 m).
Usage: python make_jobs_gap.py <workdir> <dense_sec_dir>"""
import json, os, pickle, shutil, sys
import numpy as np
W, DSEC = sys.argv[1], sys.argv[2]
sys.path.insert(0, os.environ["TLCHAIN_DIR"])
from tlchain import paths as P, chain as C, cases          # noqa: E402
from tlchain.bottom import LAYERED, HARD                   # noqa: E402
BANDS = [5.0, 6.3, 8.0, 10.0, 12.5, 16.0, 20.0, 25.0, 31.5, 40.0]
NF, NFK = 7, 3
sd = os.path.join(W, "sec"); os.makedirs(sd, exist_ok=True)
S = cases.stations()
paths = {}
for st in ("H11N", "H11S"):
    nm = f"f35a-{st}"; pk = os.path.join(sd, nm + ".pkl")
    if not os.path.exists(pk):
        pickle.dump(P.build((40.64, 142.96), (S[st]["lat"], S[st]["lon"]), "B5C2", 4), open(pk, "wb"))
    paths[nm] = dict(pk=pk, rd=S[st]["depth"])
for lat in ("39.0", "35.5", "30.0"):
    nm = f"arc{lat}S-H01W"; pk = os.path.join(sd, nm + ".pkl")
    shutil.copy(os.path.join(DSEC, nm + ".pkl"), pk)
    paths[nm] = dict(pk=pk, rd=1055.0)
J = []
for nm, p in paths.items():
    L = pickle.load(open(p["pk"], "rb"))["L_km"]
    p["L_km"] = L
    for fc in BANDS:
        for f in C.band_freqs(fc, NF):
            cost = float(L * f * max(f, 30.0))
            J.append(dict(id=f"rev|L1|{nm}|{fc:g}|{f:.4f}", kind="rev", model="ram", sec=p["pk"], reverse=True, f=float(f),
                          zsrc=float(p["rd"]), out_depths=[10.0, 2.0, 5.0, 30.0, 100.0], bottom=LAYERED.as_dict(), mode="native",
                          dr_lam=5.0, dz_lam=0.05, dr_max_m=250.0, window_m=1000.0, rec_every_m=1000.0, cost=cost))
            for bn, b in (("L1", LAYERED), ("H0", HARD)):
                J.append(dict(id=f"fwd|{bn}|{nm}|{fc:g}|{f:.4f}", kind="fwd", sec=p["pk"], f=float(f), zsrc=10.0, rd=float(p["rd"]),
                              bottom=b.as_dict(), rec_every_m=1000.0, cost=cost))
        for f in C.band_freqs(fc, NFK):
            for bn, b in (("L1", LAYERED), ("H0", HARD)):
                J.append(dict(id=f"krk|{bn}|{nm}|{fc:g}|{f:.4f}", kind="krk", sec=p["pk"], f=float(f), src_depths=[2.0, 10.0, 30.0],
                              rd=float(p["rd"]), bottom=b.as_dict(), work=os.path.join(W, "kwork"), cost=L * 30.0))
json.dump(J, open(os.path.join(W, "jobs.json"), "w"))
json.dump({k: dict(rd=v["rd"], L_km=v["L_km"]) for k, v in paths.items()}, open(os.path.join(W, "paths.json"), "w"), indent=1)
print(len(J), "jobs", {k: round(v["L_km"], 1) for k, v in paths.items()})
