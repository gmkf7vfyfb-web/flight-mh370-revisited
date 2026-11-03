import sys, os, time, json, numpy as np
from multiprocessing import Pool
os.environ["TLCHAIN_GLOBSED"] = "/Users/pete/Downloads/mh370-ocean-data/globsed/GlobSed-v3.nc"
sys.path.insert(0, "tlchain/tl-chain-2026-10-27"); sys.path.insert(0, ".")
from tlchain import paths as P, chain as C
from tlchain.bottom import LAYERED
from build_sections_now import arc_points
SRC = arc_points([-35.0])[0]; RCV = (-34.890303, 114.142637)
_rs = None
def init():
    global _rs
    _rs = C.reverse(P.build(SRC, RCV, "A5B4", 3))
def one(f):
    o = C.ram_freq(_rs, f, 1055.0, [2.0, 10.0, 30.0], bottom=LAYERED)
    return f, np.asarray(o["I"]).tolist(), o["wall_s"]
if __name__ == "__main__":
    jobs = []
    for fc, nf in [(10.0, 25), (31.5, 15)]:
        jobs += list(C.band_freqs(fc, nf))
    t0 = time.time()
    with Pool(12, initializer=init) as p: res = p.map(one, jobs)
    out = dict(res=[(f, I, w) for f, I, w in res], wall=time.time()-t0, L_km=None)
    json.dump(out, open("ram_band_test.json", "w")); print("done", round(time.time()-t0,1), sum(w for _,_,w in res))
