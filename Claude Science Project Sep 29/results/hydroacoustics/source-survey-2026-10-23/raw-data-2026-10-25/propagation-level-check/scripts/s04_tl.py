"""Module TL chain on the new paths (prereg P2), unchanged module code: kraken_tl.tl_path + air9_tl_validation.build_profiles
(KRAKEN adiabatic incoherent, hard bottom, Francois-Garrison, spherical) and tl_recal_block9.ram_job (RAM) + imos_ram_grid.fg_db_per_km.
Threads only (4); RAM runs in separate python subprocesses because pyram (numba, no nogil) holds the GIL.
Usage: python s04_tl.py kraken <paths...> | ram <jobfile>"""
import os, sys, json, time, pathlib, subprocess, numpy as np, pandas as pd
from concurrent.futures import ThreadPoolExecutor
MOD = pathlib.Path("repo/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare").resolve()
sys.path.insert(0, str(MOD)); import kraken_tl as K, air9_tl_validation as A
AT = str(pathlib.Path("at").resolve()); BANDS = [5.0, 6.3, 8.0, 10.0, 12.5, 16.0, 20.0, 25.0, 31.5, 40.0]
RD = {"H10N": 847.3, "H10S": 860.0}
ZS = {"sjc": [30.0, 33.0, 38.0], "sje": [200.0, 300.0, 400.0, 500.0, 600.0, 700.0, 800.0, 900.0], "fss": [30.0, 61.0, 100.0]}
os.environ.setdefault("DYLD_LIBRARY_PATH", os.environ.get("MH370_HYDRO_ENV_LIB", ""))  # conda env lib for KRAKEN/pyram
def kjob(name, fc):
    b = pd.read_csv(f"paths/bathy_{name}.csv"); s = pd.read_csv(f"paths/ssp_{name}.csv"); rprof, prof = A.build_profiles(b, s)
    rd = RD[name.split("-")[1]]; zs = ZS[name[:3]]; zs = [z for z in zs if z < prof[0][0] - 5]
    rd = min(rd, prof[-1][0] - 1.0); tag = f"f{fc:g}".replace(".", "p"); wd = pathlib.Path("work/k") / name; t0 = time.time()
    try:
        r, tl, nm, dt = K.tl_path(wd, tag, fc, prof, rprof, np.array([rprof[-1]]), zs, [rd], A.BOTTOMS["hard"], AT, fg=A.FG)
    except RuntimeError as e:
        return [dict(path=name, fc_hz=fc, src_depth_m=z, tl_db=np.nan, status=str(e)[:80]) for z in zs]
    sh = K.read_shd(wd / f"{tag}.shd"); x = sh["rr_m"] / 1000.0 / 6371.0; sph = 10 * np.log10(x / np.sin(x))
    out = [dict(path=name, model="KRAKEN", fc_hz=fc, src_depth_m=float(z), rcv_depth_m=rd, range_km=float(rprof[-1]), tl_db=float(-20 * np.log10(np.abs(sh["p"][0, j, 0, -1])) + sph[-1]),
                n_modes_first=nm[0] if nm else -1, n_modes_min=min(nm) if nm else -1, wall_s=time.time() - t0, status="ok") for j, z in enumerate(sh["sz"])]
    for f in wd.glob(f"{tag}.*"): f.unlink()
    return out
def rjob(name, fc, zs):
    rd = RD[name.split("-")[1]]; o = f"work/r/{name}_{fc:g}_{zs:g}.json"
    if os.path.exists(o): return json.load(open(o))
    code = f"""import sys,json; sys.path.insert(0,{str(MOD)!r}); import tl_recal_block9 as T, imos_ram_grid as I, pandas as pd
r=T.ram_job(({name!r},'paths/bathy_{name}.csv','paths/ssp_{name}.csv',{fc},{zs},{rd})); L=float(pd.read_csv('paths/bathy_{name}.csv').range_km.iloc[-1])
r.update(path={name!r},model='RAM',rcv_depth_m={rd},range_km=L,fg_db=float(I.fg_db_per_km({fc})*L)); r['tl_db']=r['tl_ram_db']+r['fg_db']
json.dump(r,open({o!r},'w'))"""
    env = dict(os.environ, OMP_NUM_THREADS="1", NUMBA_NUM_THREADS="1", OPENBLAS_NUM_THREADS="1")
    p = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, env=env)
    if p.returncode: return dict(path=name, fc_hz=fc, src_depth_m=zs, model="RAM", tl_db=float("nan"), status=p.stderr[-300:])
    return json.load(open(o))
if __name__ == "__main__":
    pathlib.Path("work/r").mkdir(parents=True, exist_ok=True); pathlib.Path("work/k").mkdir(parents=True, exist_ok=True)
    if sys.argv[1] == "kraken":
        jobs = [(n, fc) for n in sys.argv[3:] for fc in BANDS]; rows = []
        with ThreadPoolExecutor(4) as ex:
            for r in ex.map(lambda a: kjob(*a), jobs):
                rows += r; print(r[0]["path"], r[0]["fc_hz"], round(r[0].get("wall_s", -1)), r[0]["status"][:40], flush=True)
        pd.DataFrame(rows).to_csv(sys.argv[2], index=False)
    else:
        jobs = [tuple(x) for x in json.load(open(sys.argv[3]))]; rows = []
        with ThreadPoolExecutor(4) as ex:
            for r in ex.map(lambda a: rjob(*a), jobs):
                rows.append(r); print(r.get("path"), r.get("fc_hz"), r.get("src_depth_m"), round(r.get("wall_s", -1)), round(r.get("tl_db", float("nan")), 2), flush=True)
        pd.DataFrame(rows).to_csv(sys.argv[2], index=False)
