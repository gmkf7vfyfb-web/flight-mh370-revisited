"""Run J driver for per_impact_lnl.py (amendment 8): one task per seed, adaptive concurrency.
Starts at 4 workers (Pete, 17 Oct: start at 4 threads, expand as cores free). Before each launch the target is
  override file <out>/WORKERS (an integer) if present, else clamp(18 - (loadavg1 - own_workers) - 2, 4, 12),
and a launch also needs >= 8 GiB free+inactive memory. Each worker is single-threaded (BLAS threads = 1).
Writes to <out>.staging; the finaliser checks every seed (rows equal end of flight's, row = 0..n-1, lnL_gated == 0)
and only then renames to <out>, writes README.txt and, last, READY.
Usage: python run_j_driver.py <module_dir> <eof_run> <out> <kadri_csv> <compact_reader> <tau: eof|scenario>
"""
import json, os, pathlib, re, subprocess, sys, time, hashlib
import numpy as np
mod, eof, out, kcsv, creader, tau = sys.argv[1:7]
eof = pathlib.Path(eof); out = pathlib.Path(out); stg = pathlib.Path(str(out) + ".staging"); stg.mkdir(parents=True, exist_ok=True)
HERE = pathlib.Path(__file__).resolve().parent
STRATA = ["run-j-waypoints", "run-j-free", "run-j-repro-radar", "run-j-descent-climb"]
tasks = []
for s in STRATA:
    for sd in sorted((eof / s).glob("seed-*")):
        if sd.is_dir() and (sd / "impacts32.npy").exists():
            k = int(sd.name.split("-")[1])
            if not (stg / s / sd.name / "hydro-lnL.npy").exists() or not (stg / "_parts" / f"{s}_{k}.json").exists():
                tasks.append((s, k))
log = open(stg / "driver.log", "a")
def say(m):
    log.write(time.strftime("%Y-%m-%dT%H:%M:%SZ ", time.gmtime()) + m + "\n"); log.flush()
def memfree_gib():
    t = subprocess.run(["vm_stat"], capture_output=True, text=True).stdout
    pg = int(re.search(r"page size of (\d+)", t).group(1))
    v = lambda k: int(re.search(k + r":\s+(\d+)", t).group(1))
    return (v("Pages free") + v("Pages inactive")) * pg / 2**30
def target(nown):
    f = stg / "WORKERS"
    if f.exists():
        try: return max(1, int(f.read_text().strip()))
        except ValueError: pass
    return int(min(12, max(4, round(18 - (os.getloadavg()[0] - nown) - 2))))
env = dict(os.environ, OMP_NUM_THREADS="1", OPENBLAS_NUM_THREADS="1", MKL_NUM_THREADS="1", VECLIB_MAXIMUM_THREADS="1",
           PYTHONPATH=f"{HERE}:{HERE}/exploratory/pleiades_test")
say(f"start tau={tau} tasks={len(tasks)}")
running = {}; failed = []; t0 = time.time(); peak = 0
while tasks or running:
    for k_, (p, tk, ts) in list(running.items()):
        if p.poll() is not None:
            del running[k_]
            if p.returncode != 0: failed.append(tk); say(f"FAILED {tk} rc={p.returncode}")
            else: say(f"done {tk[0]}/seed-{tk[1]} {time.time()-ts:.0f}s")
    tgt = target(len(running))
    while tasks and len(running) < tgt and memfree_gib() > 8:
        s, k = tasks.pop(0)
        cmd = [sys.executable, str(HERE / "per_impact_lnl.py"), mod, str(eof), str(stg), kcsv, "--compact-reader", creader,
               "--strata", s, "--seeds", str(k), "--tau", tau, "--part", f"{s}_{k}"]
        p = subprocess.Popen(cmd, env=env, cwd=HERE, stdout=open(stg / f"_w_{s}_{k}.log", "w"), stderr=subprocess.STDOUT)
        running[(s, k)] = (p, (s, k), time.time()); peak = max(peak, len(running))
        say(f"launch {s}/seed-{k} workers={len(running)} target={tgt} load1={os.getloadavg()[0]:.1f}")
        time.sleep(2)
    time.sleep(5)
say(f"all tasks ended in {time.time()-t0:.0f}s, peak workers {peak}, failed {failed}")
if failed: sys.exit(1)
# finaliser: checks, then README and READY
sys.path.insert(0, str(pathlib.Path(creader).parent)); import compact_impacts as C
summ = {}; bad = []
for pj in sorted((stg / "_parts").glob("*.json")):
    d = json.loads(pj.read_text()); summ.setdefault("options", d.pop("options")); summ.update(d)
for s in STRATA:
    for sd in sorted((eof / s).glob("seed-*")):
        if not sd.is_dir(): continue
        n = np.load(sd / "impacts32.npy", mmap_mode="r").shape[0]
        r = np.load(stg / s / sd.name / "hydro-lnL.npy", mmap_mode="r")
        ok = len(r) == n and bool(np.all(r["row"] == np.arange(n))) and bool(np.all(r["lnL_gated"] == 0.0))
        if not ok: bad.append(f"{s}/{sd.name}")
say(f"checks: {len(bad)} seeds failing {bad}")
if bad: sys.exit(2)
rows = sum(v["rows"] for k, v in summ.items() if k != "options"); nc = sum(v["not_computed"] for k, v in summ.items() if k != "options")
cl = {s: float(np.average([v["tl_lat_clamped_share"] for k, v in summ.items() if k.startswith(s + "/")],
       weights=[v["rows"] for k, v in summ.items() if k.startswith(s + "/")])) for s in STRATA}
hdr = (f"Hydroacoustics on end of flight run J, all four strata (74 seeds), tau = {tau} "
       f"({'PRIMARY' if tau == 'eof' else 'SENSITIVITY: scenario tau, log-uniform 0.05-10 s'}). Written {time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}.\n"
       f"Writer prepare/per_impact_lnl.py amendment 8 (prereg 9662384), driver prepare/run_j_driver.py; peak {peak} single-thread workers.\n"
       f"Rows {rows:,}; not_computed {nc}; per-seed checks (rows equal end of flight's, row = 0..n-1, lnL_gated = 0.0): all pass.\n"
       "COMPOSER USE: lnL_gated = 0.0 is the module likelihood (P_D gate not passed). lnL_soft is a labelled SENSITIVITY only.\n"
       "LABELS: TL NOT CALIBRATED; IMS P_D borrowed (IMOS 3274 + 4.8 dB); run J convergence accepted as a pass by project ruling, 16 Oct 2026;\n"
       "  TL clamped at the table edge (reach gap) for rows outside the TL latitude span - share by stratum: "
       + ", ".join(f"{s} {v:.3f}" for s, v in cl.items()) + "\n\n")
stg.joinpath("README.txt").write_text(hdr + "Per-seed summary:\n" + json.dumps(summ, indent=1) + "\n")
if out.exists(): out.rename(str(out) + f".old-{int(time.time())}")
stg.rename(out)
(out / "READY").write_text(f"hydroacoustics run J per-impact columns, tau={tau}, written {time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}; lnL_gated = 0.0; see README.txt\n")
say("READY")
