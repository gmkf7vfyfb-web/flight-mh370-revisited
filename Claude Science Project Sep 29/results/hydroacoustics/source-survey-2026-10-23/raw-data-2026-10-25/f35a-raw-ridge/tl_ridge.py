"""KRAKEN TL for the raw F-35A coupling ridge: the module chain of prepare/metz_f35a/step2_tl.py UNCHANGED
(tl_grid_run_j.run_path with the step2_tl loaders: GEBCO_2026 NW Pacific layer, WOA23 B5C2 April, KRAKEN adiabatic
incoherent modes, hard bottom, Francois-Garrison, spherical correction). Only the source depth list and the band list
are extended: depths 1, 2, 5, 10, 20, 30, 50 m; third-octave bands 2-100 Hz. Paths from the module working point W
and from the Metz-consistent point P to the H11N and H11S centroids. Threads (KRAKEN runs as a subprocess).
Usage: python tl_ridge.py <out_dir> [nthreads] [bands csv]"""
import sys, os, time, json, pathlib
from concurrent.futures import ThreadPoolExecutor
import numpy as np, pandas as pd
MOD = pathlib.Path(__file__).resolve().parents[1] / "H"
sys.path.insert(0, str(MOD / "prepare" / "metz_f35a")); sys.path.insert(0, str(MOD / "prepare"))
import step2_tl as S2          # noqa: E402  (loaders; imports prereg, tl_grid_run_j, air9_tl_validation, kraken_tl)
TG = S2.TG
AT = os.path.expanduser("~/Downloads/mh370-exchange/hydroacoustics/run-j-metz-f35a/at")
DEPTHS = [1.0, 2.0, 5.0, 10.0, 20.0, 30.0, 50.0]
BANDS = [2.0, 2.5, 3.15, 4.0, 5.0, 6.3, 8.0, 10.0, 12.5, 16.0, 20.0, 25.0, 31.5, 40.0, 50.0, 63.0, 80.0, 100.0]
SRCS = {"W": dict(id="W", lat=40.64, lon=142.96), "P": dict(id="P", lat=40.4496, lon=142.9237)}

def main(out, nth=4, bands=None):
    out = pathlib.Path(out); out.mkdir(parents=True, exist_ok=True); pdir = out / "paths"; pdir.mkdir(exist_ok=True)
    bands = bands or BANDS
    S2.install_loaders(); TG.SRC = DEPTHS
    rc = S2.receivers()
    jobs = []
    for sk, s in SRCS.items():
        for st in ("H11N", "H11S"):
            for fc in bands:   # one job per (path, band): parallel over bands
                jobs.append((f"{sk}-{st}", s, rc[st], fc))
    def run(j):
        name, s, r, fc = j; t0 = time.time()
        rows, dt, tk = TG.run_path((name, s, r, [fc], AT, str(out / "work" / f"{name}_{fc:g}"), True, pdir, False))
        return [dict(rr, path=name) for rr in rows], time.time() - t0
    t0 = time.time(); R = []
    with ThreadPoolExecutor(nth) as ex:
        for rows, dt in ex.map(run, jobs):
            R.extend(rows); print(rows[0]["path"], rows[0]["fc_hz"], round(dt), round(time.time() - t0), flush=True)
            pd.DataFrame(R).to_csv(out / "tl_ridge_partial.csv", index=False)
    pd.DataFrame(R).to_csv(out / "tl_ridge.csv", index=False)
    json.dump(dict(receivers=rc, depths=DEPTHS, bands=bands, sources=SRCS, seconds=time.time() - t0), open(out / "tl_ridge_meta.json", "w"), indent=1)
    print("done", round(time.time() - t0))

if __name__ == "__main__":
    main(sys.argv[1], int(sys.argv[2]) if len(sys.argv) > 2 else 4, [float(x) for x in sys.argv[3].split(",")] if len(sys.argv) > 3 else None)
