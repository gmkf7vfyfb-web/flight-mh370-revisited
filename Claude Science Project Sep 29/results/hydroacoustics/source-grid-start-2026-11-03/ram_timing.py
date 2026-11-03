import sys, os, time, json, numpy as np
os.environ["TLCHAIN_GLOBSED"] = "/Users/pete/Downloads/mh370-ocean-data/globsed/GlobSed-v3.nc"
sys.path.insert(0, "tlchain/tl-chain-2026-10-27"); sys.path.insert(0, ".")
from tlchain import paths as P, chain as C
from tlchain.bottom import LAYERED
from build_sections_now import arc_points
src = arc_points([-35.0])[0]; rcv = (-34.890303, 114.142637)
t0 = time.time(); sec = P.build(src, rcv, "A5B4", 3); tb = time.time()-t0
rs = C.reverse(sec); out = dict(build_s=tb, L_km=sec["L_km"])
for f in [5.0, 10.0, 20.0, 40.0]:
    o = C.ram_freq(rs, f, 1055.0, [2.0, 10.0, 30.0], bottom=LAYERED)
    I = np.asarray(o["I"]); TL = -10*np.log10(I) + C.fg_db_per_km(f)*sec["L_km"] + C.sph_db(sec["L_km"])
    out[str(f)] = dict(wall_s=o["wall_s"], nz=int(o["nz"]), nr=int(o["nr"]), TL=TL.tolist())
    print(f, round(o["wall_s"],1), np.round(TL,1), flush=True)
    json.dump(out, open("ram_timing.json","w"))
