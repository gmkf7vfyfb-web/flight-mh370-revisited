"""Batch 2: candidate fixes on the arc, Wake and held-out calibration paths (4 Nov 2026).
Variants (all reciprocal RAM runs with the frozen chain; only the input section or the Bottom dataclass changes):
  L1  frozen primary (baseline at the same frequencies, calibration paths only; arc and Wake baselines are in batch 1)
  BR  bare rock where depth <= 2,500 m over >= 10 km, > 50 km from both ends (Phase 3 pre-registered rule 3b, copied)
  NS  no sediment anywhere (GlobSed thickness x 0: fluid basement 3,500 m/s at the seafloor)
  M3  3 x 3 median GEBCO depth (chain mode 'med3') instead of the nearest cell
Calibration paths: Blackman 2001 airguns air7, air8, air9 -> H01W_2001 (depths 7.5, 10 m; bands 5-63 Hz) and 2003 SUS
sites A7, A8, A10 -> H01W1_2003 and -> H08S (site depths; bands 16-63 Hz); frequencies NF_CAL per band.
Usage: python make_jobs_fixes.py <workdir>"""
import json, os, pickle, sys
import numpy as np
W = sys.argv[1]
sys.path.insert(0, os.environ["TLCHAIN_DIR"])
from tlchain import paths as P, chain as C, cases            # noqa: E402
from tlchain.bottom import LAYERED, Bottom                   # noqa: E402
NS = Bottom(name="no_sediment", h_scale=0.0)
NF_ARC, NF_CAL = 7, 3
LF = [5.0, 6.3, 8.0, 10.0, 12.5, 16.0, 20.0, 25.0, 31.5, 40.0]


def bare_rock(sec, zmax=2500.0, run_km=10.0, end_km=50.0):    # copy of Phase 3 p3_jobs.bare_rock
    d = sec["depth_native"]; r = sec["range_km"]; L = sec["L_km"]
    m = d <= zmax; out = np.zeros(len(d), bool); i = 0
    while i < len(d):
        if m[i]:
            j = i
            while j + 1 < len(d) and m[j + 1]:
                j += 1
            if r[j] - r[i] >= run_km:
                out[i:j + 1] = True
            i = j + 1
        else:
            i += 1
    out &= (r > end_km) & (r < L - end_km)
    s = dict(sec); s["sed_m"] = np.where(out, 0.0, sec["sed_m"]); s["bare_rock_mask"] = out
    return s, out


sd = os.path.join(W, "sec"); os.makedirs(sd, exist_ok=True)
allp = {p["name"]: p for p in cases.all_paths()}
cal = ["air7-H01W_2001", "air8-H01W_2001", "air9-H01W_2001", "A7-H01W1_2003", "A8-H01W1_2003", "A10-H01W1_2003", "A7-H08S", "A8-H08S", "A10-H08S"]
meta = {}
for nm in cal:
    p = allp[nm]; pk = os.path.join(sd, nm + ".pkl")
    if not os.path.exists(pk):
        pickle.dump(P.build(p["src"], p["rcv"], p["decade"], p["month"]), open(pk, "wb"))
    deps = [7.5, 10.0] if nm.startswith("air") else [float(z) for z in p["src_depths"]]
    meta[nm] = dict(pk=pk, rd=p["rd"], bands=[b for b in p["bands"] if b <= 40.0], depths=deps, nf=NF_CAL, variants=["L1", "BR", "NS", "M3"] if nm.startswith("air") else ["L1", "BR", "NS"])
for nm in ["arc39.0S-H01W", "arc35.5S-H01W", "arc30.0S-H01W"]:
    meta[nm] = dict(pk=os.path.join(sd, nm + ".pkl"), rd=1055.0, bands=LF, depths=[10.0, 2.0, 30.0], nf=NF_ARC, variants=["BR", "NS", "M3"])
for st, rd in (("H11N", cases.stations()["H11N"]["depth"]), ("H11S", cases.stations()["H11S"]["depth"])):
    nm = f"f35a-{st}"
    meta[nm] = dict(pk=os.path.join(sd, nm + ".pkl"), rd=rd, bands=LF, depths=[10.0, 2.0, 30.0], nf=NF_ARC, variants=["NS", "M3"])
J, info = [], []
for nm, m in meta.items():
    sec = pickle.load(open(m["pk"], "rb")); L = sec["L_km"]
    bpk = m["pk"].replace(".pkl", "__bare.pkl")
    s2, mask = bare_rock(sec); pickle.dump(s2, open(bpk, "wb"))
    info.append(dict(name=nm, L_km=L, bare_km=float(mask.sum() * 0.25), rd=m["rd"]))
    for v in m["variants"]:
        sec_path = bpk if v == "BR" else m["pk"]; bot = NS if v == "NS" else LAYERED; mode = "med3" if v == "M3" else "native"
        for fc in m["bands"]:
            for f in C.band_freqs(fc, m["nf"]):
                J.append(dict(id=f"rev|{v}|{nm}|{fc:g}|{f:.4f}", kind="rev", model="ram", sec=sec_path, reverse=True, f=float(f),
                              zsrc=float(m["rd"]), out_depths=m["depths"], bottom=bot.as_dict(), mode=mode, dr_lam=5.0, dz_lam=0.05,
                              dr_max_m=250.0, window_m=1000.0, cost=float(L * f * max(f, 30.0))))
json.dump(J, open(os.path.join(W, "jobs_fixes.json"), "w"))
json.dump({k: dict(rd=v["rd"], depths=v["depths"], bands=v["bands"], nf=v["nf"], variants=v["variants"]) for k, v in meta.items()},
          open(os.path.join(W, "paths_fixes.json"), "w"), indent=1)
import pandas as pd
pd.DataFrame(info).to_csv(os.path.join(W, "bare_rock_masks_fixes.csv"), index=False)
print(len(J), "jobs; est relative cost", round(sum(j["cost"] for j in J) / 1e9, 2))
print(pd.DataFrame(info).round(1).to_string())
