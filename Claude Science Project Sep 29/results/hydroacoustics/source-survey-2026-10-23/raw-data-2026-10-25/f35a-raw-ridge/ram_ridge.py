"""RAM (pyram) minus KRAKEN TL delta on the F-35A W->H11N and W->H11S paths, using prepare/ram_tl_check.py's
env / ram_band / kraken_band functions UNCHANGED (no water absorption in either model, hard bottom, profiles every 5 km,
9 frequencies per third octave, intensity mean over the last 500 m, dr 2 lambda, dz lambda/20). The module's existing
delta (results-data/ram_check) covers only H11S; this run adds H11N (gap G-F3) and repeats H11S as a reproduction check.
Usage: python ram_ridge.py <paths_dir> <out_csv> <bands csv> <depths csv> [nthreads]"""
import sys, os, pathlib, time
from concurrent.futures import ThreadPoolExecutor
import numpy as np, pandas as pd
MOD = pathlib.Path(__file__).resolve().parents[1] / "H"
sys.path.insert(0, str(MOD / "prepare"))
import ram_tl_check as RC   # noqa: E402
AT = os.path.expanduser("~/Downloads/mh370-exchange/hydroacoustics/run-j-metz-f35a/at")
RD = {"H11N": 730.6666666666666, "H11S": 739.3333333333334}   # triad mean hydrophone depths (stations.csv), as step2_tl

def main(pdir, out, bands, depths, nth=4):
    pdir = pathlib.Path(pdir)
    RC.PATHS.update({"W-H11N": "H11N", "W-H11S": "H11S"})
    RC.F.receiver_depth = lambda st: RD[st]
    RC.SRC = depths
    envs = {n: RC.env(pdir, n) for n in ("W-H11N", "W-H11S")}
    jobs = [(n, fc, zs) for n in envs for fc in bands for zs in depths]
    done = []
    if os.path.exists(out + ".resume"):          # resume: keep finished (path, band, depth) rows
        done = pd.read_csv(out + ".resume").to_dict("records")
        have = {(r["path"], float(r["fc_hz"]), float(r["src_depth_m"])) for r in done}
        jobs = [j for j in jobs if (j[0], float(j[1]), float(j[2])) not in have]
    def run(j):
        n, fc, zs = j; t0 = time.time()
        return dict(path=n, fc_hz=fc, src_depth_m=zs, tl_ram_db=RC.ram_band(envs[n], fc, zs), s=time.time() - t0)
    rows = list(done)
    with ThreadPoolExecutor(nth) as ex:
        for r in ex.map(run, jobs):
            rows.append(r); print(r, flush=True); pd.DataFrame(rows).to_csv(out + ".partial", index=False)
    wk = pathlib.Path(out).parent / "ram_kraken_work"; K = []
    for n, e in envs.items():
        for fc in bands:
            w = wk / n; w.mkdir(parents=True, exist_ok=True)
            kt = RC.kraken_band(e, fc, w, AT)
            for zs in depths:
                K.append(dict(path=n, fc_hz=fc, src_depth_m=zs, tl_kraken_db=kt[float(zs)]))
    d = pd.DataFrame(rows).merge(pd.DataFrame(K), on=["path", "fc_hz", "src_depth_m"])
    d["delta_ram_minus_kraken_db"] = d.tl_ram_db - d.tl_kraken_db
    d.to_csv(out, index=False); print(d.to_string())

if __name__ == "__main__":
    a = sys.argv
    main(a[1], a[2], [float(x) for x in a[3].split(",")], [float(x) for x in a[4].split(",")], int(a[5]) if len(a) > 5 else 4)
