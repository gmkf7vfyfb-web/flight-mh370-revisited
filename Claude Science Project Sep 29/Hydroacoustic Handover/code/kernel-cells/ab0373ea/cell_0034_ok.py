import subprocess, os, pathlib, pandas as pd, time
OUT = pathlib.Path("/Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-imos-ram-grid")
WS = pathlib.Path.cwd()
P = WS / "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare"
os.rename(OUT / "paths_hold", OUT / "paths")
import shutil; shutil.rmtree(OUT / "work", ignore_errors=True)
d = pd.read_csv(OUT / "ram_grid_rows.csv")
n0 = len(d); d = d.drop_duplicates(["tag", "fc_hz"]); d.to_csv(OUT / "ram_grid_rows.csv", index=False)
print("rows", n0, "->", len(d))
env = dict(os.environ, DYLD_LIBRARY_PATH="/Users/pete/.claude-science/conda/envs/mh370-hydro/lib", OMP_NUM_THREADS="1", OPENBLAS_NUM_THREADS="1", PYTHONPATH=str(P))
logf = open(OUT / "run2.log", "w")
proc = subprocess.Popen(["python", "imos_ram_grid.py", "run", str(OUT), "--at-bin", str(WS / "tools"), "--procs", "6", "--deadline", "2026-10-22T03:50"],
                        cwd=str(P), env=env, stdout=logf, stderr=subprocess.STDOUT)
time.sleep(60)
print(proc.pid, proc.poll())
print(open(OUT / "run2.log").read().strip().splitlines()[-3:])